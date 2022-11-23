from django.db import transaction
from django.http import HttpResponse
from rest_framework.decorators import authentication_classes, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from cmsservice.service.vowservice import VowEmployeeService


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def vendor_get(request):
    pr_service = VowEmployeeService(request.scope)
    response_obj = pr_service.vendor_get(request)
    response = HttpResponse(response_obj, content_type="application/json")
    return response


# vendor create
@transaction.atomic()
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def proposal_vendorcreate(request, proposal_id):
    pr_service = VowEmployeeService(request.scope)

    response_obj = pr_service.proposal_vendorcreate(request, proposal_id)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response