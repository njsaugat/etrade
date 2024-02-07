from django.contrib import admin

from .models import Address,OTP,Profile

admin.site.register(OTP)
admin.site.register(Profile)
admin.site.register(Address)
