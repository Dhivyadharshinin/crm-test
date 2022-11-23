import array
import io
import json
import base64
from datetime import datetime

import pandas as pd
from django.core.files.base import ContentFile

from faservice.util.fautil import dictdefault
from userservice.data.errordata import ErrorData
import requests
from django.core import signing
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from rest_framework import status
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from userservice.controller.authcontroller import get_authtoken
from userservice.data.request.departmentrequest import DepartmentRequest
from userservice.data.request.employeerequest import EmployeeRequest, EmployeemobileRequest
from userservice.models import Employee, Department, EmployeeBranch, EmployeeAddress      #   Authrequest
from userservice.service.departmentservice import DepartmentService
from userservice.service.employeeservice import EmployeeService, TA_employee_service
from nwisefin import settings
# from vysfinutility.data.error import Error
# from vysfinutility.data.error_const import ErrorMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.data.response.nwisefinuser import NWisefinUser
from utilityservice.data.response.nwisefinsearch import NwisefinSearch
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from userservice.data.request.addresscontactrequest import ContactRequest, AddressRequest
from userservice.service.addresscontactservice import AddressService, ContactService
import time
from utilityservice.permissions.filter.urlpermission import UrlPermission
from userservice.service.employeedepartmentservice import EmployeeDepartmentService
from nwisefin.settings import logger
# from validationservice.service.tpservice import TPService
from validationservice.service.tpservice import TPService
# from validationservice.controller.vendorvalidation import VendorValidation
val_url = settings.VYSFIN_URL


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_employee(request):

    if request.method == 'POST':
        user_id = request.employee_id
        scope = request.scope
        emp_json = json.loads(request.body)
        emp_obj = EmployeeRequest(emp_json)
        employee_service = EmployeeService(scope)
        contact_service = ContactService(scope)
        address_service = AddressService(scope)
        contact = emp_json.get("contact")
        contact_obj = ContactRequest(contact)
        address = emp_json.get("address")
        address_obj = AddressRequest(address)
        emp_id = emp_obj.get_id()
        if emp_id != None:
            cont_add_id = employee_service.get_contact_address_id(emp_id)
            contact_obj.id = cont_add_id.contact_id
            address_obj.id = cont_add_id.address_id

        contact_id = contact_service.create_employeecontact(contact_obj, user_id)
        address_id = address_service.create_employeeaddress(address_obj, user_id)

        resp_obj = employee_service.create_employee(emp_obj, user_id, address_id, contact_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    else:
        resp_obj = get_employee_list(request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
@csrf_exempt
# @api_view(['GET'])
# @authentication_classes([VysfinAuthentication])
# @permission_classes([IsAuthenticated, VysfinPermission, UrlPermission])
def fetch_emp_dropdown(request):
    if request.method == 'GET':
        # user_id = request.user.id
        scope=request.scope
        employee_service = EmployeeService(scope)
        data = request.GET.get('data')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = employee_service.get_emp_dropdn(vys_page,data)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_employee_department(request):
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        scope=request.scope
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        employee_department_service = TA_employee_service(scope)
        resp_obj = employee_department_service.create_department_get(request,vys_page)
        return HttpResponse(resp_obj.get(), content_type='application/json')
def get_employee_list(request):
    user_id = request.employee_id
    scope = request.scope
    search_key = request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    employee_service = EmployeeService(scope)
    resp_obj = employee_service.get_employee_list(request,vys_page,user_id,search_key)
    return resp_obj


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_user_emp_list(request):
    user_id = request.employee_id
    scope = request.scope
    search = request.GET.get('search', False)
    employee_service = EmployeeService(scope)
    resp_obj = employee_service.get_user_emp_list(user_id, search)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_list_by_filter(request):
    user_id = request.employee_id
    scope = request.scope
    search = request.GET.get('search', 'memo')
    employee_service = EmployeeService(scope)
    resp_obj = employee_service.get_memo_filter(user_id, search)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_employee(request, employee_id):
    t1 = time.time()
    user_id = request.employee_id
    scope = request.scope
    employee_service = EmployeeService(scope)
    resp_obj = employee_service.get_full_employee_info(employee_id, user_id)
    contact_service = ContactService(scope)
    address_service = AddressService(scope)
    if resp_obj.contact_id is not None:
        cont_id = resp_obj.contact_id
        contact = contact_service.fetch_employeecontact(cont_id)
        resp_obj.contact_id = contact
    if resp_obj.address_id is not None:
        address_id = resp_obj.address_id
        address = address_service.fetch_employeeaddress(address_id)
        resp_obj.address_id = address
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    t2 = time.time()
    return response


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission, UrlPermission])
def department(request):
    if request.method == 'POST':
        user_id = request.employee_id
        dept_json = json.loads(request.body)
        scope = request.scope
        dept_obj = DepartmentRequest(dept_json)
        dept_service = DepartmentService(scope)
        resp_obj = dept_service.create_department(dept_obj, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    else:
        resp_obj = get_department_list(request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission, UrlPermission])
def fetch_department(request, dept_id):
    user_id = request.employee_id
    scope = request.scope
    department_service = DepartmentService(scope)
    resp_obj = department_service.fetch_department(dept_id, user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


def get_department_list(request):
    user_id = request.employee_id
    scope = request.scope
    search_key = request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    department_service = DepartmentService(scope)
    resp_obj = department_service.fetch_department_list(vys_page, user_id, search_key)
    return resp_obj

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def department_download(request):
    scope = request.scope
    department_service = DepartmentService(scope)
    user_id = request.user.id
    search_key = request.GET.get('query')
    resp_obj = department_service.fetch_department_download(user_id,search_key)
    data = json.loads(json.dumps(resp_obj.__dict__, default=dictdefault))['data']
    df = pd.DataFrame(data)
    BytesIO = io.BytesIO()
    BytesIO.name = 'EXCEL-DOWNLOAD-(' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ').xlsx'
    writer = pd.ExcelWriter(BytesIO, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False, startcol=0, startrow=5)
    worksheet = writer.sheets['Sheet1']
    workbook = writer.book
    header_format = workbook.add_format()
    header_format.set_align('center')
    header_format.set_bold()
    worksheet.write_string(2, 2, 'Department Master Excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="Department Master.xlsx"'
    logger.info("Test_Download Data:")
    return response


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employee_info(request):
    user_arr = json.loads(request.body)
    condition = None
    user_list = None
    for user_id in user_arr:
        if condition is None:
            condition = Q(id__exact=user_id)
        else:
            condition |= Q(id__exact=user_id)
    if condition is not None:
        user_list = Employee.objects.filter(condition)
    resp_list = NWisefinList()
    if user_list is not None:
        for user in user_list:
            user_obj = NWisefinUser()
            user_obj.set_id(user.user_id)
            # user_obj.set_username(user.username)
            # user_obj.set_email(user.email)
            disp_name = '(' + user.code + ') ' + user.full_name
            user_obj.set_full_name(disp_name)
            # user_obj.set_first_name(user.first_name)
            # user_obj.set_last_name(user.last_name)
            # user_obj.set_is_active(user.is_active)
            resp_list.append(user_obj)
    return HttpResponse(resp_list.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission, UrlPermission])
def employee_info_by_id(request):
    user_arr = json.loads(request.body)
    condition = None
    user_list = None
    for user_id in user_arr:
        if condition is None:
            condition = Q(id__exact=user_id)
        else:
            condition |= Q(id__exact=user_id)
    if condition is not None:
        user_list = Employee.objects.filter(condition)
    resp_list = NWisefinList()
    if user_list is not None:
        for user in user_list:
            user_obj = NWisefinUser()
            user_obj.set_id(user.id)
            # user_obj.set_username(user.username)
            # user_obj.set_email(user.email)
            disp_name = '(' + user.code + ') ' + user.full_name
            user_obj.set_full_name(disp_name)
            # user_obj.set_first_name(user.first_name)
            # user_obj.set_last_name(user.last_name)
            # user_obj.set_is_active(user.is_active)
            resp_list.append(user_obj)
    return HttpResponse(resp_list.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def department_info(request):
    user_arr = json.loads(request.body)
    condition = None
    user_list = None
    for user_id in user_arr:
        if condition is None:
            condition = Q(id__exact=user_id)
        else:
            condition |= Q(id__exact=user_id)
    if condition is not None:
        user_list = Department.objects.filter(condition)
    resp_list = NWisefinList()
    if user_list is not None:
        for user in user_list:
            user_obj = NwisefinSearch()
            user_obj.set_id(user.id)
            # user_obj.set_username(user.username)
            # user_obj.set_email(user.email)
            user_obj.set_name(user.name)
            # user_obj.set_first_name(user.first_name)
            # user_obj.set_last_name(user.last_name)
            # user_obj.set_is_active(user.is_active)
            resp_list.append(user_obj)
    return HttpResponse(resp_list.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_user_id(request):
    user_arr = json.loads(request.body)
    condition = None
    user_list = None
    for user_id in user_arr:
        if condition is None:
            condition = Q(id__exact=user_id)
        else:
            condition |= Q(id__exact=user_id)
    if condition is not None:
        user_list = Employee.objects.filter(condition)
    resp_list = []
    if user_list is not None:
        for user in user_list:
            resp_list.append(str(user.user_id))

    return HttpResponse(resp_list, content_type='application/json')


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission, UrlPermission])
def employee_department(request, employee_id):
    user_id = request.employee_id
    scope = request.scope
    if request.method == 'GET':
        type = request.GET.get('type')
        search_key = request.GET.get('query')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        employee_service = EmployeeService(scope)
        employee_id = int(employee_id)
        if user_id == employee_id:
            employee_id = employee_service.get_empid_from_userid(employee_id)
            logger.info(str(employee_id))

        resp_obj = employee_service.get_dept_from_emp(employee_id, type, search_key, vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'POST':
        employee_service = EmployeeService(scope)
        department_arr = json.loads(request.body)
        resp_obj = employee_service.add_remove_department_from_employee(employee_id, department_arr)
        # emp dep permission
        emp_dep_service = EmployeeDepartmentService(scope)
        resp_obj = emp_dep_service.emp_to_dep_permission(employee_id, department_arr, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission, UrlPermission])
def department_employee(request, department_id):
    user_id = request.employee_id
    scope = request.scope
    if request.method == 'GET':
        type = request.GET.get('type')
        search_key = request.GET.get('query')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        employee_service = EmployeeService(scope)
        resp_obj = employee_service.get_emp_from_dept(department_id, type, search_key, vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'POST':
        employee_service = EmployeeService(scope)
        employee_arr = json.loads(request.body)
        resp_obj = employee_service.add_remove_employee_from_department(department_id, employee_arr)
        # emp dep permission
        emp_dep_service = EmployeeDepartmentService(scope)
        emp_id = employee_service.get_empid_from_userid(user_id)
        resp_obj = emp_dep_service.dep_to_emp_permission(department_id, employee_arr, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


# search employee
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_employee_list(request):
    if request.method == 'GET':
        user_id = request.employee_id
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        query = None
        query = request.GET.get('query', None)
        employee_service = EmployeeService(scope)
        resp_obj = employee_service.search_employee_list(request, query, vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def searchrm(request):
    if request.method == 'GET':
        user_id = request.employee_id
        scope = request.scope
        emp = Employee.objects.get(id=user_id)
        employee_id = emp.id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        query = None
        query = request.GET.get('query', None)
        employee_service = EmployeeService(scope = request.scope)
        resp_obj = employee_service.search_employee_list(request, query, vys_page)
        empdata = json.loads(resp_obj.get())
        if empdata['data']:
            for k in empdata['data']:
                if k['id'] == employee_id:
                    empdata['data'].remove(k)

        response = HttpResponse(json.dumps(empdata), content_type="application/json")
        return response


# search department
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_department_list(request):
    if request.method == 'GET':
        user_id = request.employee_id
        scope = request.scope
        page = request.GET.get('page', 1)
        query = None
        query = request.GET.get('query', query)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        type = request.GET.get('type')
        is_master = request.GET.get('is_master')
        department_service = DepartmentService(scope)
        if type is None:
            resp_obj = department_service.search_department_list(request, query, vys_page, is_master)
        else:
            emp_service = EmployeeService(scope)
            resp_obj = department_service.search_department_type(user_id, type, query, vys_page)

        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def deldept(request, dept_id):
    scope = request.scope
    department_service = DepartmentService(scope)
    resp_obj = department_service.delete_department(dept_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission, UrlPermission])
def department_sys(request):
    if request.method == 'POST':
        user_id = request.employee_id
        scope = request.scope
        dept_json = json.loads(request.body)
        dept_obj = DepartmentRequest(dept_json)
        dept_service = DepartmentService(scope)
        resp_obj = dept_service.create_department_sys(dept_obj, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['get'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_employees(request):
    user_id = request.employee_id
    scope = request.scope
    search_key = request.GET.get('query')
    employee_service = EmployeeService(scope)
    resp_obj = employee_service.fetch_employee_list(search_key)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def searchemployee_designation(request):
    if request.method == 'GET':
        user_id = request.employee_id
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        query = None
        query = request.GET.get('query', None)
        employee_service = EmployeeService(scope)
        resp_obj = employee_service.search_employee_designation(request, query, vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET'])
# @authentication_classes([VysfinAuthentication])
# @permission_classes([IsAuthenticated, VysfinPermission])
def employee_get_sync(request):
    scope = request.scope
    getfull_data = request.GET.get('type')
    datefilter = request.GET.get('date')
    employee_service = EmployeeService(scope)
    resp_obj = employee_service.get_employee_list_sync(getfull_data, datefilter)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


from userservice.service.branchservice import EmployeeBranchService


@csrf_exempt
@api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, VysfinPermission])
def fetch_allbranch_list(request):
    scope = request.scope
    datefilter = request.GET.get('date')
    branch_service = EmployeeBranchService(scope)
    resp_obj = branch_service.Fetch_All_Branch_List(datefilter)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, VysfinPermission])
def fetch_emp_get(request):
    scope = request.scope
    codefilter = request.GET.get('code')
    emp_service = EmployeeService(scope)
    resp_obj = emp_service.Fetch_Emp_List(codefilter)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employee_info_update(request):
    scope = request.scope
    data = json.loads(request.body)
    logger.info(str(data))
    employee_service = EmployeeService(scope)
    resp_obj = employee_service.employee_info_update(data)
    response = HttpResponse('updated', content_type="application/json")
    return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def department_branch(request):
    if request.method == 'POST':
        user_id = request.employee_id
        scope = request.scope
        dept_json = json.loads(request.body)
        dept_name = dept_json.get('name')
        branch_id = dept_json.get('branch_id')
        department = Department.objects.create(name=dept_name, branch_id=branch_id, is_sys=False, created_by=user_id)
        code = "DGRP" + str(department.id)
        department.code = code
        department.save()

        permission_service = EmployeeDepartmentService(scope)
        permission_service.emp_dep_perm_from_department(user_id, department.id)
        response = HttpResponse('created', content_type="application/json")
        return response

# # given model not in the usermodel
# @transaction.atomic
# @csrf_exempt
# @api_view(['POST'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def employeemobilenomicro(request):
#     if request.method == 'POST':
#         code = request.GET.get('code')
#         otp=request.GET.get('otp')
#         value = signing.loads(code)
#         vendor_validation = TPService()
#         validation_resp = vendor_validation.perform_otp_validation('mobileupdation',otp,code, request)
#         resp = validation_resp.get()
#         resp = json.loads(resp)
#         # print(resp[])
#         if resp['validation_status']['Status']=='Success':
#             try:
#                 auth_obj = Authrequest.objects.get(employee=value['employee'], created_date=value['date'])
#                 employee_service = EmployeeService()
#                 user_id = request.user.id
#                 emp = Employee.objects.get(user_id=user_id)
#                 employee_id = emp.id
#                 apuserflag = emp.code
#
#                 empauth=Employee.objects.get(id=auth_obj.employee)
#                 data={
#                     "code": empauth.code,
#                     "mobile_number": auth_obj.mobile_number
#                 }
#                 if apuserflag == 'apuser' or emp.code == data['code']:
#                     emp_obj = EmployeemobileRequest(data)
#
#                     resp_obj = employee_service.empmobileupdate(emp_obj, employee_id)
#
#                 else:
#                     resp_obj = {"MESSAGE": 'Not a Valid user '}
#                 if apuserflag != 'apuser':
#                     token = "Bearer  " + get_authtoken()
#                     print(token)
#                     headers = {"content-type": "application/json", "Authorization": "" + token + ""}
#                     params = {"Params": {
#                         "Filter": {"code": empauth.code,
#                                    "mobile_number": auth_obj.mobile_number}
#                     }
#                     }
#
#                     datas = json.dumps(params, indent=4)
#                     logger.info(datas)
#                     resp = requests.post(
#                         "" + val_url + 'update_personal_infonum?GROUP=EMPLOYEE_MOBILENO&Action=EMPLOYEE_MOBILENO',
#                         data=datas,
#                         headers=headers,
#                         verify=False)
#                     results = resp.content.decode("utf-8")
#                     results = json.loads(results)
#
#                     logger.info(results)
#
#                     if results['MESSAGE'] == ['SUCCESS']:
#                         return HttpResponse(json.dumps(resp_obj, indent=4), content_type='application/json')
#
#                     else:
#                         transaction.set_rollback(True)
#                         emp_resp = {"MESSAGE": ' Wisefyn Sync Failed '}
#                         return HttpResponse(json.dumps(emp_resp, indent=4), content_type='application/json')
#
#                 return HttpResponse(json.dumps(resp_obj, indent=4), content_type="application/json")
#
#
#
#             except Exception as inst:
#
#                 print(type(inst))  # the exception instance
#
#                 print(inst.args)  # arguments stored in .args
#                 print(inst)
#
#                 error_data = ErrorData()
#                 error_data.set_error('error2222')
#                 return HttpResponse(error_data.get(), content_type='application/json',
#                                     status=status.HTTP_401_UNAUTHORIZED)
#
#         else:
#             error_data = ErrorData()
#             error_data.set_error(resp['validation_status']['Description'])
#             return HttpResponse(error_data.get(), content_type='application/json', status=status.HTTP_401_UNAUTHORIZED)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def mobileupdation(request):
    scope = request.scope
    employee_service = EmployeeService(scope)
    user_id = request.employee_id
    emp = Employee.objects.get(id=user_id)
    apuserflag = emp.code
    data = json.loads(request.body)
    authrequest_obj = employee_service.updateauthrequest(user_id,data)
    data = {'employee': authrequest_obj.employee, 'date': str(authrequest_obj.created_date)}
    value = signing.dumps(data)
    userinfo = {'id': value}
    flag='mobileupdation'
    resp_dict = {'validation_status': True}
    validation_resp = None
    vendor_validation = TPService()
    validation_resp = vendor_validation.perform_otp_gen(flag, value)
    resp=validation_resp.get()
    resp=json.loads(resp)
    # print(resp[])
    if resp['validation_status']['Status'] == 'Success':
        return HttpResponse(json.dumps(userinfo), content_type='application/json', status=status.HTTP_200_OK)
    else:
        error_data = ErrorData()
        error_data.set_error(resp['validation_status']['Description'])
        return HttpResponse(error_data.get(), content_type='application/json', status=status.HTTP_401_UNAUTHORIZED)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_empmobile(request):
    datas={}
    scope = request.scope
    employee_service = EmployeeService(scope)
    user_id = request.employee_id
    emp = Employee.objects.get(id=user_id)
    logincode = emp.code
    code=request.GET.get('code')
    if logincode==code:
        emp = Employee.objects.get(code=code)
        employee_id = emp.id
        resp_obj = employee_service.empmobileget(code)
        datas['data']=json.loads(resp_obj.get())
        response = HttpResponse(json.dumps(datas), content_type="application/json")
    else:
        datas['data'] = []
        response = HttpResponse(json.dumps(datas), content_type="application/json")

    return response
@csrf_exempt
@api_view(['GET'])
def bs_data_get(request):
    if request.method == 'GET':
        scope=request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        employee_service = TA_employee_service(scope)
        resp_obj = employee_service.bs_data(request,vys_page)
        return HttpResponse(resp_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['GET'])
def Branch_data(request):
    if request.method == 'GET':
        scope=request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        employee_service = TA_employee_service(scope)
        resp_obj = employee_service.branch_data(request,vys_page)
        return HttpResponse(resp_obj.get(), content_type='application/json')

@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employeemobileno(request):
    if request.method == 'POST':
        scope = request.scope
        employee_service = EmployeeService(scope)
        user_id = request.employee_id
        emp = Employee.objects.get(id=user_id)
        employee_id = emp.id
        apuserflag=emp.code
        data = json.loads(request.body)
        if apuserflag=='apuser' or emp.code==data['code']:
            emp_obj = EmployeemobileRequest(data)

            resp_obj = employee_service.empmobileupdate(emp_obj,employee_id)

        else:
            resp_obj = {"MESSAGE": 'Not a Valid user '}
        if apuserflag!='apuser':
            token = "Bearer  " + get_authtoken()
            headers = {"content-type": "application/json", "Authorization": "" + token + ""}
            params={"Params": {
                "Filter": {"code":data['code'],
                           "mobile_number": data['mobile_number']}
            }
            }

            datas = json.dumps(params, indent=4)
            logger.info(datas)
            resp = requests.post(
                "" + val_url + 'update_personal_infonum?GROUP=EMPLOYEE_MOBILENO&Action=EMPLOYEE_MOBILENO',
                data=datas,
                headers=headers,
                verify=False)
            results = resp.content.decode("utf-8")
            results = json.loads(results)
            logger.info(results)

            if results['MESSAGE'] == ['SUCCESS']:
                return HttpResponse(json.dumps(resp_obj, indent=4), content_type='application/json')

            else:
                transaction.set_rollback(True)
                emp_resp = {"MESSAGE": ' Wisefyn Sync Failed '}
                return HttpResponse(json.dumps(emp_resp, indent=4), content_type='application/json')

        return  HttpResponse(json.dumps(resp_obj, indent=4), content_type="application/json")
##COMMON NEW EMPLOYEE API
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_employee_by_userid(request,user_id):
    employee = Employee.objects.get(user_id=user_id)
    emp_data = {"id": employee.id, "code": employee.code, "name": employee.full_name}
    employee_dic = json.dumps(emp_data, indent=4)
    return HttpResponse(employee_dic, content_type='application/json')

@csrf_exempt
@api_view(['post'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_employee_id(request):
        id_obj = json.loads(request.body)
        obj = Employee.objects.filter(id__in=id_obj["employee_id"]).values('id','full_name','code','employee_branch_id')
        arr = []
        for i in obj:
            data = {"id": i['id'], "full_name": i['full_name'],"code":i['code'],"branch_id": i['employee_branch_id']}
            arr.append(data)
        employee_dic = json.dumps(arr, indent=4)
        return HttpResponse(employee_dic, content_type='application/json')

@csrf_exempt
@api_view(['post'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_employee_branch(request):
        scope = request.scope
        id_obj = json.loads(request.body)
        serv=EmployeeService(scope)
        data=id_obj['arr']
        resp = serv.get_employee_detail(data)
        return HttpResponse(resp, content_type='application/json')


# prpo-micro to micro
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employee_get(request):
    emp_data = json.loads(request.body)
    empId_arr = emp_data['employee_id']
    employee = Employee.objects.filter(id__in = empId_arr)
    emp_list_data = NWisefinList()
    for i in employee:
        i=i.__dict__
        data = {"id": i['id'], "code": i['code'],
                "name": i['full_name'],
                "designation": i['designation'],
                "full_name": i['code'] + "--" +i['full_name']}
        emp_list_data.append(data)
    return HttpResponse(emp_list_data.get(), content_type='application/json')

#particular_fetch
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_employee1(request, employee_id):
    employee = Employee.objects.get(id=employee_id)
    emp_data = {"id": employee.id, "code": employee.code,
                "name": employee.full_name,
                "employee_branch_id": employee.employee_branch_id,
                "full_name": employee.code + "--" + employee.full_name}
    employee_dic = json.dumps(emp_data, indent=4)
    return HttpResponse(employee_dic, content_type='application/json')
class GENDER:
    OTHERS = "-1"
    MALE = "1"
    FEMALE = "2"
    Other_value = 'Others'
    MALE_VALUE = 'Male'
    FEMALE_VALUE = 'Female'

    def getGenderType(request,id):
        data = [{"id": GENDER.OTHERS, "name": GENDER.Other_value},
                {"id": GENDER.MALE, "name": GENDER.MALE_VALUE},
                {"id": GENDER.FEMALE, "name": GENDER.FEMALE_VALUE}]
        for i in data:
            if(int(i['id'])==id):

                return i['name']


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_employee_id(request, employee_id):
    employee = Employee.objects.get(id=employee_id)
    emp_branchid=employee.employee_branch_id
    branch=EmployeeBranch.objects.get(id=emp_branchid)
    # print(branch.name)
    Gender_service=GENDER()
    genderdb = (employee.gender)
    print(genderdb)
    gender=Gender_service.getGenderType(int(genderdb))
    emp_data = {"id": employee.id, "code": employee.code,
                "name": employee.full_name,
                "employee_branch_id": employee.employee_branch_id,
                "employee_branch_name": branch.name,
                "full_name": employee.code + "--" + employee.full_name,
                # "designation": designation.name,
                # "employee_type": department.name,
                "date_of_Joining":str(employee.doj),
                # "cost_centre": costcentre.name,
                "business_segment": employee.businesssegment, "middle_name": employee.middle_name,
                "last_name": employee.last_name,
                # "supervisor": supervisor.full_name,
                "grade": employee.grade, "date_of_birth": str(employee.dob), "phone_number": employee.phone_no,
                "mail_id": employee.email_id, "gender": gender}
    costcentre_id=employee.costcentre
    from utilityservice.service.ta_api_service import ApiService
    scope=request.scope
    serv=ApiService(scope)
    costcentre=dict()
    if costcentre_id !='' and costcentre_id != None:
        try:
            costcentre=serv.get_cc_details(costcentre_id,request)
            emp_data["cost_centre"]=costcentre.name
        except:
            emp_data["cost_centre"]=None
    else:
        emp_data["cost_centre"]=None
    from utilityservice.service.api_service import ApiService
    common_serv=ApiService(scope)
    dept_id=employee.employee_type
    department={}
    if dept_id != '' and dept_id != None:
        try:
            department=common_serv.get_department_id(request,dept_id)
            emp_data["employee_type"]=department.name
        except:
            emp_data["employee_type"]=None
    else:
        emp_data["employee_type"]=None
    supervisor_id=employee.supervisor
    supervisor = dict()
    if supervisor_id != '' and supervisor_id != None:
        try:
            supervisor=Employee.objects.get(id=supervisor_id)
            emp_data["supervisor"]=supervisor.full_name
        except:
            emp_data["supervisor"]= None
    else:
        emp_data["supervisor"] = None
    designation_id=employee.designation
    designation = {}
    if designation_id != '' and designation_id != None:
        try:
            designation=common_serv.get_designation_id(request,designation_id)
            emp_data["designation"]=designation.name
        except:
            emp_data["designation"] = None
            # designation['name'] = None
    else:
        emp_data["designation"] = None

    employee_dic = json.dumps(emp_data, indent=4)
    return HttpResponse(employee_dic, content_type='application/json')
#employeelimit dropdown
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_employeename(request, employee_name):
    condition1 = (Q(full_name__icontains=employee_name) | Q(code__icontains=employee_name)) & Q(status=1)
    employee = Employee.objects.filter(condition1).values('id', 'code', 'full_name', 'employee_branch_id')
    emp_list_data = NWisefinList()
    for i in employee:
        data = {"id": i['id'],
                "code": i['code'],
                "name": i['full_name'],
                "full_name": i['code'] + "--" + i['full_name'],
                "employee_branch_id": i['employee_branch_id']}
        emp_list_data.append(data)
    return HttpResponse(emp_list_data.get(), content_type='application/json')

#empcode search
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_employeecode(request, employee_code):
    employee = Employee.objects.get(id=employee_code, status=1)
    emp_data = {"id": employee.id,
                "code": employee.code,
                "name": employee.full_name,
                "full_name": employee.code + "--" + employee.full_name,
                "employee_branch_id": employee.employee_branch_id}
    employee_dic = json.dumps(emp_data, indent=4)
    return HttpResponse(employee_dic, content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_employeedata(request):
    employee_id=request.GET.get('emp_id')
    employee = Employee.objects.get(id=employee_id)
    emp_data = {"id": employee.id,
                "code": employee.code,
                "name": employee.full_name,
                "fullname": employee.code + "--" + employee.full_name,
                "full_name": employee.code + "--" + employee.full_name,
                "employee_branch_id": employee.employee_branch_id}
    employee_dic = json.dumps(emp_data, indent=4)
    return HttpResponse(employee_dic, content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employee_list(request):
    scope = request.scope
    emp_service = EmployeeService(scope)
    resp_data = emp_service.fetch_employee_id()
    return HttpResponse(resp_data.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_employeename(request):
    employee_name = request.GET.get('query')
    condition1 = (Q(full_name__icontains=employee_name) | Q(code__icontains=employee_name)) & Q(status=1)
    employee = Employee.objects.filter(condition1).values('id')
    emp_list_data = NWisefinList()
    prod_arr = []
    for i in employee:
        prod_arr.append(i['id'])
    data = {"id": prod_arr}
    emp_list_data.append(data)
    return HttpResponse(emp_list_data.get(), content_type='application/json')


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_employeename_data(request):
    emp_data = json.loads(request.body)
    empId_arr = emp_data['employee_id']
    query = request.GET.get('query')
    if query != '':
        employee = Employee.objects.filter(id__in=empId_arr, full_name=query)
    else:
        employee = Employee.objects.filter(id__in=empId_arr)
    print(employee)
    emp_list_data = NWisefinList()
    for i in employee:
        data = {"id": i.id,
                "code": i.code,
                "name": i.full_name,
                "designation": i.designation,
                "full_name": i.code + "--" + i.full_name,
                "employee_branch_id": i.employee_branch_id}
        emp_list_data.append(data)
    return HttpResponse(emp_list_data.get(), content_type='application/json')

#Micro to micro ecf
#employee get
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_employee_by_empid(request,emp_id):
    employee = Employee.objects.get(id=emp_id)
    emp_data = {"id": employee.id, "code": employee.code, "name": employee.full_name,
                "employee_branch":employee.employee_branch_id,"address_id": employee.address_id}
    employee_dic = json.dumps(emp_data, indent=6)
    return HttpResponse(employee_dic, content_type='application/json')
#employeebranch get
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_empbranch(request,empbranch_id):
    empbranch = EmployeeBranch.objects.get(id=empbranch_id)
    empbranch_data = {"id": empbranch.id, "code": empbranch.code, "name": empbranch.name,"gstin":empbranch.gstin}
    empbranch_dic = json.dumps(empbranch_data, indent=5)
    return HttpResponse(empbranch_dic, content_type='application/json')
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_empbranch_empid(request,emp_id):
    empbranch = Employee.objects.get(id=emp_id)
    empbranch_data = {"id": empbranch.id, "code": empbranch.code,"branch":empbranch.branch}
    empbranch_dic = json.dumps(empbranch_data, indent=5)
    return HttpResponse(empbranch_dic, content_type='application/json')

@csrf_exempt
@api_view(['POST'])
# @authentication_classes([VysfinAuthentication])
# @permission_classes([IsAuthenticated, VysfinPermission])
def get_multi_employee(request):
    scope = request.scope
    emp_data = json.loads(request.body)
    empid_arr = emp_data['arr']
    employee_service = EmployeeService(scope)

    data=employee_service.get_multi_employee(empid_arr)
    print(data)
    return HttpResponse(data)
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_employee_address(request,add_id):
    employee = EmployeeAddress.objects.get(id=add_id)
    emp_data = {"id": employee.id, "line1": employee.line1, "line2": employee.line2,
                "line3":employee.line3,"pincode_id": employee.pincode_id,"city_id":employee.city_id,"state_id":employee.state_id}
    employee_dic = json.dumps(emp_data, indent=8)
    return HttpResponse(employee_dic, content_type='application/json')


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_employeename(request):
    employee_name = request.GET.get('query')
    condition1 = (Q(full_name__icontains=employee_name) | Q(code__icontains=employee_name)) & Q(status=1)
    employee = Employee.objects.filter(condition1).values('id')
    emp_list_data = NWisefinList()
    prod_arr = []
    for i in employee:
        prod_arr.append(i['id'])
    data = {"id": prod_arr}
    emp_list_data.append(data)
    return HttpResponse(emp_list_data.get(), content_type='application/json')


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_employeename_data(request):
    emp_data = json.loads(request.body)
    empId_arr = emp_data['employee_id']
    query = request.GET.get('query')
    if query != '':
        employee = Employee.objects.filter(id__in=empId_arr, full_name=query)
    else:
        employee = Employee.objects.filter(id__in=empId_arr)
    print(employee)
    emp_list_data = NWisefinList()
    for i in employee:
        data = {"id": i.id,
                "code": i.code,
                "name": i.full_name,
                "designation": i.designation,
                "full_name": i.code + "--" + i.full_name,
                "employee_branch_id": i.employee_branch_id}
        emp_list_data.append(data)
    return HttpResponse(emp_list_data.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_employeecode(request):
    employee_name = request.GET.get('query')
    condition1 = Q(code=employee_name) & Q(status=1)
    employee = Employee.objects.get(condition1)
    emp_data = {"id": employee.id, "code": employee.code, "name": employee.full_name,
                "employee_branch": employee.employee_branch_id, "address_id": employee.address_id}
    employee_dic = json.dumps(emp_data, indent=6)
    return HttpResponse(employee_dic, content_type='application/json')

@csrf_exempt
@api_view(['GET'])
# @authentication_classes([VysfinAuthentication])
# @permission_classes([IsAuthenticated, VysfinPermission])
def get_employee_designation_department(request,emp_id):
    #user_id = request.employee_id
    scope = request.scope
    emp_service = EmployeeService(scope)
    resp_obj = emp_service.get_employee_designation_department(emp_id)
    return HttpResponse(resp_obj.get(), content_type='application/json')

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def emp_empbranch(request, emp_id):
    scope = request.scope
    emp_serv = EmployeeService(scope)
    resp_obj = emp_serv.emp_branch(emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def check_permission_ta(request):
    if request.method=='POST':
        emp_id=request.employee_id
        scope = request.scope
        emp_service = TA_employee_service(scope)
        resp_obj = emp_service.check_permission_ta(emp_id)
        response = HttpResponse(resp_obj, content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ceo_team_get_ta(request):
    if request.method=='GET':
        emp_id=request.employee_id
        query = request.GET.get('query')
        scope = request.scope
        emp_service = TA_employee_service(scope)
        resp_obj = emp_service.ceo_team_get_ta(emp_id,query)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ceo_team_get_ta_check(request):
    if request.method=='GET':
        emp_id=request.employee_id
        query = request.GET.get('query')
        scope = request.scope
        emp_service = TA_employee_service(scope)
        resp_obj = emp_service.ceo_team_get_ta_check(emp_id,query)
        response = HttpResponse(resp_obj, content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employee_org_info(request):
    scope = request.scope
    if request.method == 'POST':
        body_data = json.loads(request.body)
        resp_obj = EmployeeService(scope).cemployee_org_info(body_data)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    else:
        emp_id = request.GET.get('emp_id')
        resp_obj = EmployeeService(scope).getemployee_org_info(emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response