from dj_rest_auth.registration.serializers import RegisterSerializer
from django.conf import settings
from django.contrib.auth import authenticate,get_user_model
from django.utils.translation import gettext as _
from django_countries.serializers import CountryFieldMixin
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .exceptions import (
    AccountDisabledException,
    AccountNotRegisteredException,
    InvalidCredentialsException
)
from .models import Address,PhoneNumber, Profile
# We are using this model
User=get_user_model()

class UserRegistrationSerializer(RegisterSerializer):
    """
    Serializer for registering new users using email or phone num
    """
    
    username=None
    first_name=serializers.CharField(required=False,write_only=True) #we're using default Auth model
    last_name=serializers.CharField(required=False,write_only=True) 
    phone_number=PhoneNumberField(required=False,
                    write_only=True,
                    validators=[
                        UniqueValidator(
                            queryset=PhoneNumber.objects.all(),
                            message=_("A user is already registered with this phone number.")
                        )
                    ])
    email=serializers.EmailField(required=False)

    
    def validate(self,validated_data):
        email=validated_data.get("email",None)
        phone_number=validated_data.get("phone_number",None)

        if not (email or phone_number):
            raise serializers.ValidationError(_("Enter an email or a phone number."))

        if validated_data["password1"] != validated_data["password2"]:
            raise serializers.ValidationError(_("The two passwords fields didn't match."))
        
        return validated_data
    
    def get_cleaned_data_extra(self):
        return {
            "phone_number":self.validated_data.get("phone_number",""),
            "first_name":self.validated_data.get("first_name",""),
            "last_name":self.validated_data.get("last_name","")
        }
        
    def create_extra(self,user,validated_data):
        user.first_name=self.validated_data.get("first_name")
        user.last_name=self.validated_data.get("last_name")
        user.save()

        phone_number=validated_data.get("phone_number")

        if phone_number:
            PhoneNumber.objects.create(user=user,phone_number=phone_number)
            user.phone.save()
        

    def custom_signup(self,request,user):
        # clean the data and save it in db
        self.create_extra(user,self.get_cleaned_data_extra())


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer to login users with email or phone number
    """
    phone_number=PhoneNumberField(required=False,allow_blank=True)
    email=serializers.EmailField(required=False,allow_blank=True)

    password=serializers.CharField(write_only=True,style={"input_type":"password"})
    
    
    def _validate_phone_email(self,phone_number,email,password):
        
        if email and password:
            return authenticate(username=email,password=password)
        elif str(phone_number) and password:
            return authenticate(username=str(phone_number),password=password)
            
        raise serializers.ValidationError(
                _("Enter a phone number or an email and password.")
            )
    
    def validate(self,validated_data):
        phone_number=validated_data.get("phone_number")
        email=validated_data.get("email")
        password=validated_data.get("password")

        user=None
        
        user=self._validate_phone_email(phone_number,email,password)
        
        if not user:
            # easily raise the exception here, if sth goes wrong
            raise InvalidCredentialsException()
            
        if not user.is_active:
            raise AccountDisabledException
        
        if email:
            email_address=user.emailaddress_set.filter(email=user.email,verified=True).exists()
            if not email_address:
                raise serializers.ValidationError(_("Email is not verified."))
            
        else:
            if not user.phone.is_verified:
                raise serializers.ValidationError(_("Phone number is not verified."))
            
            
        validated_data["user"]=user
        return validated_data
    
    

class PhoneNumberSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize phone number
    """
    
    phone_number=PhoneNumberField()

    class Meta:
        model=PhoneNumber
        fields=("phone_number",)
    
    # only validates one field
    def validate_phone_number(self,value):
        try:
            queryset=User.objects.get(phone__phone_number=value)
            if queryset.phone.is_verified:
                err_message=_("Phone number is already verified.") 
                raise serializers.ValidationError(err_message)
        except User.DoesNotExist:
            raise AccountNotRegisteredException()
            
        
        return value
    

class VerifyPhoneNumberSerializer(serializers.Serializer):
    
    """
    Serializer class to verify OTP
    """
    phone_number=PhoneNumberField()
    email=serializers.EmailField(validators=[
                        UniqueValidator(
                            queryset=User.objects.all(),
                            message=_("A user is already registered with this email.")
                        )
                    ])
    otp=serializers.CharField(max_length=settings.TOKEN_LENGTH)
    
    def validate_phone_number(self,value):
        phone_number_qs=User.objects.filter(phone__phone_number=value)
        if not phone_number_qs.exists():
            raise AccountNotRegisteredException()
        
        return value
    
    def validate(self,validated_data):
            
        
        phone_number=str(validated_data.get("phone_number"))
        # email=str(validated_data.get("email"))
        otp=validated_data.get("otp")

        # if not(email or phone_number):
        #     raise serializers.ValidationError(_("Enter an email or a phone number."))


        # if email:            
        #     email_qs=PhoneNumber.objects.get(user__email=email)
    

        phone_number_qs=PhoneNumber.objects.get(phone_number=phone_number)
        
        phone_number_qs.check_verification(security_code=otp)        
        
        return validated_data    


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize the user Profile Model
    """
    
    class Meta:
        model=Profile
        fields=(
            "avatar",
            "bio",
            "created_at",
            "updated_at"
        )
        
    
class AddressReadOnlySerializer(CountryFieldMixin,serializers.ModelSerializer):
    """
    Serializer class to serialize Address model
    """
    
    user=serializers.CharField(source="user.get_full_name",read_only=True)
    
    class Meta:
        model=Address
        fields="__all__"
    
    

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize User model
    """
    profile=ProfileSerializer(read_only=True)
    phone_number=PhoneNumberField(source="phone",read_only=True)
    addresses=AddressReadOnlySerializer(read_only=True,many=True)# return many addresses
    
    class Meta:
        model=User
        fields=(
            "id",
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "is_active",
            "profile",
            "addresses"
        )
        

class ShippingAddressSerializer(CountryFieldMixin,serializers.ModelSerializer):
    """
    Serializer class to serialize address of type shipping
    for shipping addreess auto set adress type to shipping
    """
    
    user=serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model=Address
        fields="__all__"
        read_only_fields=("address_type",)
    
    def to_representation(self,instance):
        representation=super().to_representation(instance)
        representation["address_type"]="S"

        return representation
        
        

class BillingAddressSerializer(CountryFieldMixin,serializers.ModelSerializer):
    """
    Serializer class to serialize address of type billing
    
    For billing address, automatically set address type to billing
    """
    
    user=serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model=Address
        fields="__all__"
        read_only_fields=("address_type",)
    
    def to_representation(self, instance):
        representation=super().to_representation(instance)
        representation["address_type"]="B"

        return representation

