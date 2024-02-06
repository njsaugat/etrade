from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from decouple import config
from dj_rest_auth.registration.views import RegisterView, SocialLoginView
from dj_rest_auth.views import LoginView
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.utils.translation import gettext as _
from rest_framework import permissions, status
from rest_framework.generics import (GenericAPIView, RetrieveAPIView,
                                     RetrieveUpdateAPIView)
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from users.models import Address, PhoneNumber, Profile
from users.permissions import IsUserAddressOwner, IsUserProfileOwner
from users.serializers import (AddressReadOnlySerializer,
                               PhoneNumberSerializer, ProfileSerializer,
                               UserLoginSerializer, UserRegistrationSerializer,
                               UserSerializer, VerifyPhoneNumberSerializer)

User=get_user_model()


class UserRegistrationAPIView(RegisterView):
    """
    Register new users using phone number or email and password
    """

    serializer_class=UserRegistrationSerializer

    @staticmethod
    def send_email(data):
        email=EmailMessage(
            subject=data['subject'],
            body=data['body'],
            from_email=config('EMAIL_FROM'),
            to=[data['to_email']]
        )
        email.send()
    
    def send_message(self,request,message,*args,**kwargs):
        res=SendOrResendSMSAPIView.as_view()(request._request,*args,**kwargs)

        if res.status_code==200:
            return {"detail":message}
        

    # inherit from genericAPIview -->so overwrite create method
    def create(self,request,*args,**kwargs):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers=self.get_success_headers(serializer.data)

        response_data=""

        email=request.data.get("email",None)
        phone_number=request.data.get("phone_number",None)

        if email and phone_number:
            response_data=self.send_message(request,message=_("Verification e-mail and SMS sent."),*args,**kwargs)
            
        elif email and not phone_number:
            response_data={"detail":_("verification email sent.")}

        else:
            response_data=self.send_message(request,message=_("Verification SMS sent."),*args,**kwargs)
        
        return Response(response_data,status=status.HTTP_201_CREATED,headers=headers)



class UserLoginAPIView(LoginView):
    """
    Authenticate existing users using (phone number or email) and password
    """
    serializer_class=UserLoginSerializer
    

class SendOrResendSMSAPIView(GenericAPIView):
    
    """
    Check if submitted phone number is valid phone number and send OTP
    """
    # this is where we call the twilio
    
    serializer_class=PhoneNumberSerializer
    
    def post(self,request,*args,**kwargs):
        serializer=self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
                    
        phone_number=str(serializer.validated_data["phone_number"])

        user=User.objects.filter(phone__phone_number=phone_number).first()
        
        sms_verification=PhoneNumber.objects.filter(
            user=user,is_verified=False
        ).first()

        sms_verification.send_confirmation()
    
        return Response(status=status.HTTP_200_OK)
        

class VerifyPhoneNumberAPIView(GenericAPIView):
    """
    Check if submitted phone number and OTP matches and verify the user
    """

    serializer_class=VerifyPhoneNumberSerializer
    
    def post(self,request,*args,**kwargs):
        serializer=self.get_serializer(data=request.data)

        if not serializer.is_valid:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

        message={"detail":_("Phone number successfully verified.")}
        return Response(message,status=status.HTTP_200_OK)


class GoogleLogin(SocialLoginView):
    """
    Social authentication with Google
    """
    
    adapter_class=GoogleOAuth2Adapter
    callback_url="call_back_url"
    client_class=OAuth2Client

class ProfileAPIView(RetrieveUpdateAPIView):
    """
    Get, update user profile
    """
    
    queryset=Profile.objects.all()
    serializer_class=ProfileSerializer
    permission_classes=(IsUserProfileOwner,)

    def get_object(self):
        return self.request.user.profile
    

class UserAPIView(RetrieveAPIView):
    """
    Get user details
    """
    
    queryset=User.objects.all()
    serializer_class=UserSerializer
    permission_classes=(permissions.IsAuthenticated,)

    
    def get_object(self):
        return self.request.user

class AddressViewSet(ReadOnlyModelViewSet):
    """
    List and retrieve user addresses
    """
    
    queryset=Address.objects.all()
    serializer_class=AddressReadOnlySerializer
    permission_classes=(IsUserAddressOwner,)

    def get_queryset(self):
        res=super().get_queryset()
        user=self.request.user
        return res.filter(user=user)

        