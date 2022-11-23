import json

from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import permission_classes, authentication_classes, api_view
from rest_framework.permissions import IsAuthenticated

from docservice.util.docutil import DocModule
from cmsservice.service.cmscommonservice import CommonService
from cmsservice.service.projectidentification import Project_Identification_Service
from cmsservice.util.cmsutil import DocUtil, get_fileextension_val
from docservice.service.documentservice import DocumentsService
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@transaction.atomic
@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def projectidentification(request):
    if request.method == "POST":
        project_data = request.data.dict().get('data')
        project_data = json.loads(project_data)
        print("project_data", project_data)
        scope = request.scope
        project_service = Project_Identification_Service(scope)
        common_service = CommonService(scope)
        emp_id = request.employee_id

        # file removal on updating
        if ("id" in project_data) & ("file_remove" in project_data):
            project_id = project_data.get("id")
            file_remove = project_data.get("file_remove")
            file_remove_len = len(file_remove)
            if file_remove_len > 0:
                common_service.remove_prjattachement(project_id, file_remove, emp_id)

        #  IDENTIFICATION CREATE
        response_obj = project_service.project_identification(request, project_data, emp_id)
        ref_id = response_obj.id

        # APPROVAL TRAN INSERT
        if "id" not in project_data:
            approval = project_data.get("approval")
            app_resp_obj = project_service.pro_tran_approval(approval, ref_id, emp_id)

            if not app_resp_obj['app_resp']:
                print("app_resp_obj['app_resp'] : ", app_resp_obj['app_resp'])
                transaction.set_rollback(True)
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                response = HttpResponse(error_obj.get(), content_type="application/json")
                return response

        # content upload
        attach_type = DocUtil.project_identification
        doc_service = DocumentsService(scope)
        docmodule_obj = DocModule()
        params = dict()
        params['module'] = docmodule_obj.CMS
        params['ref_id'] = ref_id
        params['ref_type'] = docmodule_obj.CMS
        doc_type = project_data.get("type")
        project_content = project_data.get('content')

        # covernote
        common_service.covernote_create(ref_id, attach_type, project_content, emp_id)

        file_len = len(request.FILES.getlist('file'))
        if file_len > 0:
            for i in request.FILES.getlist('file'):
                file_name = i.name
                extension = file_name.split('.')[-1]
                filetype_check = get_fileextension_val(extension)
                if filetype_check is False:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_FILETYPE)
                    error_obj.set_description(ErrorDescription.INVALID_FILETYPE)
                    response = HttpResponse(error_obj.get(), content_type="application/json")
                    return HttpResponse(response, content_type='application/json')

            # upload project document
            resp_obj = doc_service.upload(request, params)
            document_json = json.loads(resp_obj.get())['data']
            common_service.updateprojectattachement(document_json, ref_id, attach_type, doc_type, emp_id)

        success_obj = NWisefinSuccess()
        success_obj.set_status("Success")
        success_obj.set_message("Created Successfully")
        response = HttpResponse(success_obj.get(), content_type='application/json')
        return response
    elif request.method == 'GET':
        return project_identification_fetch(request)


@transaction.atomic
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def projectidentification_get(request, project_iden_id):
    scope = request.scope
    employee_id = request.employee_id
    service = Project_Identification_Service(scope)
    func = service.project_identication_get(project_iden_id, employee_id, request)
    response = HttpResponse(func.get(), content_type="application/json")
    return response


@transaction.atomic
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def projectidentification_tran_get(request, id):
    scope = request.scope
    service = Project_Identification_Service(scope)
    func = service.project_identication_tran_get(id)
    response = HttpResponse(func.get(), content_type="application/json")
    return response


@transaction.atomic
@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def project_identification_approval(request, project_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        scope = request.scope
        emp_id = request.employee_id
        approval_service = Project_Identification_Service(scope)
        resp_obj = approval_service.project_identification_approval(request, data, project_id, emp_id)
        response = HttpResponse(resp_obj.get(), content_type='application/json')
        return response


def project_identification_fetch(request):
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    scope = request.scope
    project_service = Project_Identification_Service(scope)
    emp_id = request.employee_id
    response_obj = project_service.project_identification_list(scope, vys_page, emp_id, request)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response


@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def projectidentification_parallel_app(request, projectidentification_id):
    scope = request.scope
    employee_id = request.employee_id
    approval_service = Project_Identification_Service(scope)
    resp_obj = approval_service.projectidentification_parallel_app(projectidentification_id, employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def project_identification_resubmit(request, identification_id):
    if request.method == "POST":
        scope = request.scope
        employee_id = request.employee_id
        project_service = Project_Identification_Service(scope)
        resp_obj = project_service.project_ide_resubmit(identification_id, employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def project_identification_closure(request, project_id):
    if request.method == "POST":
        data1 = json.loads(request.body)
        arr = data1['arr']
        scope = request.scope
        project_service = Project_Identification_Service(scope)
        resp_obj = project_service.projectidentificationclosure(project_id,arr)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response