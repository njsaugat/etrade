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
    InvalidCredentialsException,
    AccountNotVerifiedException
)
from .models import Address,OTP, Profile,User

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
                            queryset=User.objects.all(),
                            message=_("A user is already registered with this phone number.")
                        )
                    ])
    email=serializers.EmailField(required=False,
                                 validators=[
                        UniqueValidator(
                            queryset=User.objects.all(),
                            message=_("A user is already registered with this email.")
                        )
                    ])

    
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
        user.phone_number=self.validated_data.get("phone_number")
        user.save()        

    def custom_signup(self,request,user):
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
        
        user_otp=OTP.objects.filter(user=user).first()
        
        if not user_otp.is_verified:
            raise AccountNotVerifiedException()
        
        if not user:
            raise InvalidCredentialsException()
            
        if not user.is_active:
            raise AccountDisabledException
        user_serializer=UserSerializer(data=user)
        validated_data["user"]=user_serializer.initial_data
        return validated_data
    
    

class PhoneNumberSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize phone number
    """
    
    phone_number=PhoneNumberField()

    class Meta:
        model=User
        fields=("phone_number",)
    
    def validate_phone_number(self,value):
        try:
            queryset=OTP.objects.get(user__phone_number=value).first()
            if queryset.is_verified:
                err_message=_("Phone number is already verified.") 
                raise serializers.ValidationError(err_message)
        except User.DoesNotExist:
            raise AccountNotRegisteredException()
            
        
        return value
class EmailSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize phone number
    """
    
    email=serializers.EmailField()
    is_otp_for_password = serializers.BooleanField(write_only=True, required=False,default=False)

    class Meta:
        model=User
        fields=("email","is_otp_for_password")
    
    def validate_email(self,value):
        try:
            email_exist=User.objects.get(email=value)
        except User.DoesNotExist:
            raise AccountNotRegisteredException()
        
        try:            
            email_qs=OTP.objects.get(user__email=value)        
        except OTP.DoesNotExist:
            return value
        
        if email_qs.is_verified:
            err_message=_("Email is already verified.") 
            raise serializers.ValidationError(err_message)
        
            
        
        return value
    

class VerifyEmailSerializer(serializers.Serializer):
    """
    Serializer class to verify OTP
    """

    email=serializers.EmailField()
    otp=serializers.CharField(max_length=settings.TOKEN_LENGTH)

    def validate_email(self,value):
        email_qs=User.objects.filter(email=value)
        if not email_qs.exists():
            raise AccountNotRegisteredException()
        
        return value
    
    def validate(self,validated_data):
            
        
        email=str(validated_data.get("email"))
        otp=validated_data.get("otp")
        is_otp_for_password=validated_data.get("is_otp_for_password",False)

        email_qs=OTP.objects.get(user__email=email)
        
        email_qs.check_verification(security_code=otp,is_otp_for_password=is_otp_for_password)        
        
        return validated_data  
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
        phone_number_qs=User.objects.filter(phone_number=value)
        if not phone_number_qs.exists():
            raise AccountNotRegisteredException()
        
        return value
    
    def validate(self,validated_data):
            
        
        phone_number=str(validated_data.get("phone_number"))
        otp=validated_data.get("otp")

    

        phone_number_qs=OTP.objects.get(user__phone_number=phone_number)
        
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
    addresses=AddressReadOnlySerializer(read_only=True,many=True)
    
    class Meta:
        model=User
        fields=(
            "id",
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "is_active",
            "last_login", 
            "is_superuser", 
            "username",
            "is_staff", 
            "date_joined",
            "profile",
            "addresses",
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

