from rest_framework import authentication, exceptions
from middleware.nwisefinauth import NWisefinAuth


class NWisefinAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_service = NWisefinAuth()
        auth_service.authenticate(request)
        if request.user is None:
            raise exceptions.AuthenticationFailed('Invalid credentials/token.')
        else:
            return request.user, None
