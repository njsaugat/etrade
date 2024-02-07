from django.utils.translation import gettext as _
from rest_framework.exceptions import APIException

class AccountNotRegisteredException(APIException):
    status_code=404
    default_detail=_("The account is not registered.")
    default_code="non-registered-account"


class AccountDisabledException(APIException):
    status_code=403
    default_detail=_("User account is disabled.")
    default_code="account-disabled"
class AccountNotVerifiedException(APIException):
    status_code=403
    default_detail=_("User account is not verified.")
    default_code="account-not-verified"
    
    
class InvalidCredentialsException(APIException):
    status_code=401
    default_detail=_("Wrong username or password.")
    default_code="invalid-credentials"
