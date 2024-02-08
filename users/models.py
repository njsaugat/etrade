import datetime
import re
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext as _
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework.exceptions import NotAcceptable
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
from django.core.mail import EmailMessage
from decouple import config
from django.core.mail import send_mail


def phone_number_validator(value):
    phone_regex = r'^\+?1?\d{9,15}$'
    if not re.match(phone_regex, value):
        raise ValidationError('Phone number must be entered in the format: \'+999999999\'. Up to 15 digits allowed.')


class User(AbstractUser):
    username=models.CharField(max_length=255,unique=True,)
    email=models.EmailField(unique=True,blank=True,null=True)
    phone_number=PhoneNumberField(unique=True,blank=True,null=True)

    @property
    def identifier(self):
        return self.email or self.phone_number.as_e164


    def __str__(self):
        return self.identifier

    
    
    USERNAME_FIELD='username'
    
    def save(self,*args,**kwargs):
        # self.username=self.identifier
        super().save(*args,**kwargs)
    
    
class CreatedModified(models.Model):
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        abstract=True

class OTP(CreatedModified):
    user=models.OneToOneField(User,related_name="phone",on_delete=models.CASCADE)
    security_code=models.CharField(max_length=120)
    is_verified=models.BooleanField(default=False)
    sent=models.DateTimeField(null=True)
    
    class Meta:
        ordering=("-created_at",)
    
    
    def __str__(self):
        return self.user.identifier
    
    def generate_security_code(self):
        """Return a unique random security_code for given TOKEN_LENGTH"""

        token_length=getattr(settings,"TOKEN_LENGTH",6)
        return get_random_string(token_length,allowed_chars="0123456789")
    
    def is_security_code_expired(self):
        expiration_date=self.sent+datetime.timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)

        return expiration_date<=timezone.now()
    
    
    def send_confirmation(self):#override twilio
        twilio_account_sid=settings.TWILIO_ACCOUNT_SID
        twilio_auth_token=settings.TWILIO_AUTH_TOKEN
        twilio_phone_number=settings.TWILIO_PHONE_NUMBER

        self.security_code=self.generate_security_code()

        if not all([twilio_account_sid,twilio_auth_token,twilio_phone_number]):
            raise ValueError("Twilio credentials are not set.")
        try:
            user_instance = User.objects.get(id=self.user_id)
            phone_number = user_instance.phone_number
        except User.DoesNotExist:
            raise  
        
        try:
            twilio_client=Client(twilio_account_sid,twilio_auth_token)
            twilio_client.messages.create(
                body=f"Your activation code is {self.security_code}",
                to=str(phone_number),
                from_=twilio_phone_number,
            )
            self.sent=timezone.now()
            self.save()
            return True
        except TwilioRestException as e:
            raise ValueError(e)

    def send_email_OTP(self,reciever_email):
        self.security_code=self.generate_security_code()
        self.sent=timezone.now()
        try:
            email=EmailMessage(
                subject='Email Verification',
                body=f"Your OTP code is : {self.security_code}",
                from_email=config("EMAIL_USER"),
                to=[reciever_email],
                
            )
            
            email.send()
        
        except Exception as e:
            raise 
        self.save()
        

    def check_verification(self,security_code,is_otp_for_password):
        if is_otp_for_password:
            if (self.is_security_code_expired() or security_code!=self.security_code ):
                raise NotAcceptable(
                    _(
                        "Your security code is wrong or expired."
                    )
                )
            return True
            
            
        if (self.is_security_code_expired() or security_code!=self.security_code or self.is_verified):
            raise NotAcceptable(
                _(
                    "Your security code is wrong,expired, or this account is already verified."
                )
            )
            
        self.is_verified=True
        self.save()
        return self.is_verified



class Profile(CreatedModified):
    user=models.OneToOneField(User,related_name="profile",on_delete=models.CASCADE)
    avatar=models.ImageField(upload_to="avatar",blank=True)
    bio=models.CharField(max_length=200,blank=True)

    
    class Meta:
        ordering=("-created_at",)
    
    def __str__(self):
        return self.user.get_full_name()
    
    

class Address(CreatedModified):
    BILLING="B"
    SHIPPING="S"
    
    ADDRESS_CHOICES=((BILLING,_("billing")),(SHIPPING,_("shipping")))

    user=models.ForeignKey(User,related_name="addresses",on_delete=models.CASCADE)
    address_type=models.CharField(max_length=1,choices=ADDRESS_CHOICES)
    default=models.BooleanField(default=False)
    country=CountryField()
    city=models.CharField(max_length=100)
    street_address=models.CharField(max_length=100)
    apartment_address=models.CharField(max_length=100)
    postal_code=models.CharField(max_length=20,blank=True)

    class Meta:
        ordering=("-created_at",)
    
    
    def __str__(self):
        return self.user.get_full_name()