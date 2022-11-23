import datetime
import boto3
# from memoservice.models import Documents
from docservice.service.documentservice import DocumentsService
from vendorservice.models import VendorFileAttachment
import json
from django.http import HttpResponse , StreamingHttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from vendorservice.service.attactmentservice import VendorAttactments

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def vendor_download_file(request,file_id):
    scope = request.scope
    if request.method == 'GET':
        try:
            atractment_serv = VendorAttactments(scope)
            doc_id = atractment_serv.get_fileid_using_id(file_id)
            doc_service=DocumentsService(scope)
            response=doc_service.doc_download(doc_id,request)
            return response
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DOCUMENT_ID)
            error_obj.set_description(ErrorDescription.INVALID_DOCUMENT_ID)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response
    elif request.method == 'DELETE':
            atractment_serv = VendorAttactments(scope)
            doc_id = atractment_serv.get_fileid_using_id(file_id)
            attactment_serv = VendorAttactments(scope)
            response = attactment_serv.vendor_delete(doc_id)
            return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def vendor_view_file(request,file_id):
    scope = request.scope
    if request.method == 'GET':
        try:
            atractment_serv = VendorAttactments(scope)
            doc_id = atractment_serv.get_fileid_using_id(file_id)
            doc_service = DocumentsService(scope)
            response = doc_service.file_download(doc_id, request)
            return response
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DOCUMENT_ID)
            error_obj.set_description(ErrorDescription.INVALID_DOCUMENT_ID)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response
