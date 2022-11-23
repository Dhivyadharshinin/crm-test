import json
import sys
import traceback


from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from apservice.service.apservice import APService
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

# @csrf_exempt
# @api_view(['GET', 'POST'])
# @authentication_classes([VysfinAuthentication])
# @permission_classes([IsAuthenticated, VysfinPermission])
# def create_ap(request):
#     if request.method == 'POST':
#         from utilityservice.service import api_service
#         ap_data = json.loads(request.body)
#         ap_service=APService()
#         user_id = request.user.id
#         api_serv = api_service.ApiService()
#         emp = api_serv.get_emp_id(request, user_id)
#         emp_id  = emp['id']
#         response_obj = ap_service.apfinal_submit(request,ap_data, emp_id)
#         response = HttpResponse(response_obj.get(), content_type='application/json')
#         return response



@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_apauditchecklist_mapping(request):
    if request.method == 'POST':
        from utilityservice.service import api_service
        ap_data = json.loads(request.body)
        scope = request.scope
        ap_service=APService(scope)
        emp_id = request.employee_id
        response_obj = ap_service.map_apaudit_checklist(ap_data, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_apauditchecklist(request):
    if request.method == 'POST':
        from utilityservice.service import api_service
        ap_data = json.loads(request.body)
        scope = request.scope
        ap_service=APService(scope)
        emp_id = request.employee_id
        response_obj = ap_service.make_apauditchecklist(ap_data, emp_id)
        response = HttpResponse(response_obj, content_type='application/json')
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_apauditchecklist(request,aptype_id):
    if request.method == 'GET':
        from utilityservice.service import api_service
        scope = request.scope
        ap_service=APService(scope)
        emp_id = request.employee_id
        response_obj = ap_service.get_apaudit_checklist(aptype_id, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_bounce_apauditchecklist(request,apinvoiceheader_id):
    if request.method == 'GET':
        from utilityservice.service import api_service
        scope = request.scope
        ap_service=APService(scope)
        emp_id = request.employee_id
        response_obj = ap_service.get_bounce_apauditchecklist(apinvoiceheader_id, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response



@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ap_finalsubmit(request):
    if request.method == 'POST':
        scope = request.scope
        ap_service=APService(scope)
        emp_id = request.employee_id
        ap_data = json.loads(request.body)
        status_validation=ap_service.apfinal_submit_status_validation(ap_data['apheader_id'])
        if status_validation != False:
            return HttpResponse(status_validation.get(), content_type='application/json')
        response_obj = ap_service.apfinal_submit(request,ap_data, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def apstatus_history(request,apinvoicehdr_id):
    if request.method == 'GET':
        from utilityservice.service import api_service
        scope = request.scope
        ap_service=APService(scope)
        emp_id = request.employee_id
        #ap_data = json.loads(request.body)
        response_obj = ap_service.apstatus_tracker(request,apinvoicehdr_id, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response



@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_apraiser_accntdtls(request,raiseremp_id):
    if request.method == 'GET':
        from utilityservice.service.ap_api_service import APApiService
        scope = request.scope
        ap_api_service=APApiService(scope)
        emp_id = request.employee_id
        response_obj = ap_api_service.fetch_apraiser_emp_accntdtls_using_emp_id(request, raiseremp_id)
        response = HttpResponse(json.dumps(response_obj), content_type='application/json')
        return response



@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def apfile_download_and_view(request,file_id):
    if request.method == 'GET':
        try:
            from utilityservice.service.ap_api_service import APApiService
            scope = request.scope
            ap_api_service=APApiService(scope)
            emp_id = request.employee_id
            download = request.GET.get('download',None)
            if download:
                response_obj = ap_api_service.apfile_download(file_id, emp_id)
            else:
                response_obj = ap_api_service.apfile_view(file_id, emp_id)

            return response_obj
        except Exception as excep:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            traceback.print_exc()
            success_obj = NWisefinSuccess()
            success_obj.set_status("Failed")
            success_obj.set_message(str(excep) + " - " + str(filename) + ", line_no: " + str(line_number) + str(', exception_type : {c} '.format(c=type(excep).__name__)))
            return HttpResponse(success_obj.get(), content_type='application/json')
    elif request.method == 'DELETE':
        return apfile_delete(request, file_id)



def apfile_delete(request,file_id):
    if request.method == 'DELETE':
        try:
            from apservice.service.apdocumentservice import APDocumentService
            scope = request.scope
            ap_doc_service=APDocumentService(scope)
            emp_id = request.employee_id
            response_obj = ap_doc_service.delete_apfile(file_id, emp_id)
            response = HttpResponse(response_obj.get(), content_type='application/json')
            return response
        except Exception as excep:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            traceback.print_exc()
            success_obj = NWisefinSuccess()
            success_obj.set_status("Failed")
            success_obj.set_message(str(excep) + " - " + str(filename) + ", line_no: " + str(line_number) + str(', exception_type : {c} '.format(c=type(excep).__name__)))
            return HttpResponse(success_obj.get(), content_type='application/json')


