import json
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from hrmsservice.service.hrmspdfservice import HrmsPdfService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinpermission import NWisefinPermission
from django.http import HttpResponse
from docservice.util.docutil import DocModule
from masterservice.util.masterutil import MasterDocUtil
from docservice.service.documentservice import DocumentsService
from userservice.data.request.departmentrequest import DepartmentuploadRequest
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def commontemplate_pdf(request,employee_id):
    if request.method == 'GET':
        scope = request.scope
        type=request.GET.get('type', None)
        user_id = request.employee_id
        response = HrmsPdfService(scope).get_temp_data(type,employee_id,user_id)
        return response

# @csrf_exempt
# @api_view(['GET', 'POST'])
# def create_hrmsfile(request):
#     if request.method == 'POST':
#         project_data = json.loads(request.data.dict().get('data'))
#         scope = request.scope
#         resp_obj = DepartmentuploadRequest(project_data)
#         hrm_service = HrmsPdfService(scope)
#         doc_service = DocumentsService(scope)
#         module_obj = MasterDocUtil()
#         docmodule = DocModule()
#         response = hrm_service.hrmsfileupload(resp_obj)
#         params = dict()
#         params['module'] = docmodule.MASTER
#         params['ref_id'] = response
#         params['ref_type'] = module_obj.ORGANITATION
#         file_len = len(request.FILES.getlist('file'))
#         if file_len > 0:
#             resp_obj = doc_service.upload(request, params)
#             success_obj = NWisefinSuccess()
#             success_obj.set_status("Success")
#             success_obj.set_message("Created Successfully")
#             response = HttpResponse(success_obj.get(), content_type='application/json')
#             return response