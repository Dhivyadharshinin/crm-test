import json

from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from masterservice.util.masterutil import MasterDocUtil
from docservice.util.docutil import DocModule
from userservice.service.deptfileuploadservice import DepartmentService
from docservice.service.documentservice import DocumentsService
from userservice.data.request.departmentrequest import DepartmentuploadRequest
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess
@transaction.atomic()
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_deptfile(request,dept_id):
    if request.method == 'POST':
        project_data = json.loads(request.data.dict().get('data'))
        scope = request.scope
        emp_id = scope['employee_id']
        dept_obj = DepartmentuploadRequest(project_data)
        dept_service = DepartmentService(scope)
        doc_service = DocumentsService(scope)
        module_obj = MasterDocUtil()
        docmodule = DocModule()
        response_obj = dept_service.deptuploadfile(dept_obj, emp_id,dept_id)
        params = dict()
        params['module'] = docmodule.MASTER
        params['ref_id'] = response_obj
        params['ref_type'] = module_obj.DEPARTMENT
        file_len = len(request.FILES.getlist('file'))
        if file_len > 0:
            resp_obj = doc_service.upload(request, params)
            success_obj = NWisefinSuccess()
            success_obj.set_status("Success")
            success_obj.set_message("Created Successfully")
            response = HttpResponse(success_obj.get(), content_type='application/json')
            return response
    elif request.method == 'GET':
        scope = request.scope
        service = DepartmentService(scope)
        re_obj = service.getdeptuploadfile(dept_id,scope,request)
        response = HttpResponse(re_obj, content_type="application/json")
        return response