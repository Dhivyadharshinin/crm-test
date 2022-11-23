import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view,authentication_classes, permission_classes
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinpermission import NWisefinPermission
from hrmsservice.service.employeedocumentservice import EmployeeDocService
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess
from hrmsservice.util.hrmsutil import EmployeeDocUtil
from docservice.util.docutil import DocModule
from docservice.service.documentservice import DocumentsService
from attendanceservice.util.responsemessage import MessageResponse, StatusType
from django.db import transaction

@transaction.atomic
@csrf_exempt
@api_view(['POST', 'GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employee_document(request, employee_id):
    scope = request.scope
    user_id = request.employee_id
    if request.method == 'POST':
        emp_doc_service = EmployeeDocService(request.scope)
        document_data = json.loads(request.data.dict().get('data'))
        doc_serv = DocumentsService(scope)
        # if not request.FILES['file'] is None:
        params = dict()
        params['module'] = DocModule.ATD
        params['ref_id'] = employee_id
        params['ref_type'] = EmployeeDocUtil.employee_document
        for m in document_data:
            d_type = m['type']
            doc_obj = doc_serv.document_upload_by_reftype(request, params, str(d_type))
            emp_doc_service.create_employee_document(doc_obj, d_type, employee_id, user_id)

        success_obj = NWisefinSuccess()
        success_obj.set_status("Success")
        success_obj.set_message("Created Successfully")
        response = HttpResponse(success_obj.get(), content_type="application/json")
        return response

        # else:
        #     error_obj = MessageResponse()
        #     error_obj.set_status(StatusType.FAILED)
        #     error_obj.set_message('Invaild id')
        #     response = HttpResponse(error_obj.get(), content_type="application/json")
        #     return response

    elif request.method == 'GET':
        doc_service = EmployeeDocService(scope)
        resp_obj = doc_service.employee_doc_summary(employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

    elif request.method == 'DELETE':
        doc_id = request.GET.get('doc_id')
        if doc_id == None:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message('Invaild id')
            return error_obj

        doc_service = EmployeeDocService(scope)
        doc_service.employee_doc_delete(doc_id)

        success_obj = NWisefinSuccess()
        success_obj.set_status("Success")
        success_obj.set_message("Delete Successfully")
        response = HttpResponse(success_obj.get(), content_type="application/json")
        return response
