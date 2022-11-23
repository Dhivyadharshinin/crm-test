import json
from django.http import HttpResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from entryservice.service.entryoracleservice import EntryOracleService
from userservice.service.sftpservice import SFTPCommonService


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def sftp_common_file_upload(request):
    try:
        if request.method == 'POST':
            #module = request.POST.get("module")
            #excel_file = request.FILES['file']
            scope = request.scope
            data = json.loads(request.body)
            module=data.get("module")
            file_path=data.get("file_path")
            sftp_service=SFTPCommonService(scope)
            emp_id = request.employee_id
            response_obj = sftp_service.sftp_common_upload_api(module,file_path,emp_id)
            return JsonResponse(response_obj)
    except Exception as e:
        return JsonResponse({"Message": "ERROR_OCCURED_ON_SFTP_COMMON_API_", "DATA": str(e)})