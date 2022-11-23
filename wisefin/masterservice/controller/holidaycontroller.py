import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from docservice.service.documentservice import DocumentsService
from docservice.util.docutil import DocModule

from masterservice.data.request.holidayrequest import HolidayRequest
from masterservice.service.holidayservice import HolidayService
from masterservice.util.masterutil import SG_FileType, get_fileextension_val
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from userservice.service.employeeservice import EmployeeService
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from django.db import transaction

# @transaction.atomic
# @csrf_exempt
# @api_view(['GET', 'POST'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def create_holiday(request):
#     if request.method == 'POST':
#         scope=request.scope
#         doc_service = DocumentsService(scope)
#         docmodule_obj = DocModule()
#         par_data = json.loads(request.data.dict().get('data'))
#         state_id = par_data.get("state_id")
#         validfrom=par_data.get("validfrom")
#         validto=par_data.get("validto")
#
#         file_name = request.FILES.getlist('file')[0].name
#         extension = file_name.split('.')[-1]
#         filetype_check = get_fileextension_val(extension)
#
#         user_id = request.employee_id
#         emp_service = EmployeeService(scope)
#         emp_id = emp_service.get_empid_from_userid(user_id)
#
#         params = {}
#         params['module'] = docmodule_obj.SG
#         params['ref_id'] = docmodule_obj.SG
#         params['ref_type'] = docmodule_obj.SG
#
#         if filetype_check:
#             resp_obj = doc_service.upload(request, params)
#
#             excel_data = pd.read_excel(request.FILES['file'] ,engine='openpyxl')
#             df = pd.DataFrame(excel_data, columns= ['S.no','Holidayname','State','Date'])
#             df.dropna(subset = ["Holidayname"], inplace=True)
#
#             transation_obj = df.to_dict(orient='records')
#
#             holiday = HolidayService(scope)
#             arr_obj=[]
#             for i in transation_obj:
#                 obj = HolidayRequest(i)
#                 arr_obj.append(obj)
#             holiday.bulk_insert_holiday(arr_obj,emp_id,state_id,validfrom,validto)
#
#             resp_obj = NWisefinSuccess()
#             resp_obj.set_status(SuccessStatus.SUCCESS)
#             resp_obj.set_message(SuccessMessage.CREATE_MESSAGE)
#             response = HttpResponse(resp_obj.get(), content_type="application/json")
#             return response
#         else:
#             error_obj = NWisefinError()
#             error_obj.set_code("ERROR")
#             error_obj.set_description("INVAILD FILE FORMATE")
#             response = HttpResponse(error_obj.get(), content_type="application/json")
#             return response
#
#     elif request.method == 'GET':
#         return holiday_list(request)
#
#
# def holiday_list(request):
#     scope = request.scope
#     subject_service = HolidayService(scope)
#     page = request.GET.get('page', 1)
#     page = int(page)
#     vys_page = NWisefinPage(page, 10)
#     resp_obj = subject_service.holiday_list(vys_page)
#     response = HttpResponse(resp_obj.get(), content_type='application/json')
#     return response


# Holiday
@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_holiday(request):
    scope = request.scope
    employee_id = request.employee_id
    service = HolidayService(scope)
    if request.method == 'POST':
        leave_data = json.loads(request.body)
        is_update = request.GET.get('is_update', None)
        if is_update == '1':
            resp = service.update_holiday(leave_data, employee_id)
        else:
            resp = service.create_holiday(leave_data, employee_id)
    elif request.method == 'GET':
        action = request.GET.get('action')
        if action == None:
            state = request.GET.get('state', None)
            year = request.GET.get('year', None)
            resp = service.holiday_list(state, year)
        elif action =='leavesummary':
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page = NWisefinPage(page, 10)
            resp = service.holidaysummary(request, vys_page)

    response = HttpResponse(resp.get(), content_type="application/json")
    return response

























