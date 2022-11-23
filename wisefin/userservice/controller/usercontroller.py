import json
import urllib

from knox.models import AuthToken

from userservice.data.authdata import AuthData
from userservice.service.authservice import AuthService
from django.core import signing
from environs import Env
env = Env()
env.read_env()
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from nwisefin import settings
from rest_framework import status
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from userservice.data.errordata import ErrorData
from userservice.data.request.employeerequest import EmployeeRequest
from userservice.data.userdata import UserData
from userservice.models import Employee # Employeemobileno, Authrequest,
from userservice.service.employeeservice import EmployeeService, TA_employee_service
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinuser import NWisefinUser
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@csrf_exempt
def create_user(request):
    scope = request.scope
    if not request.method == 'POST':
        error_data = ErrorData()
        error_data.set_error('Invalid request')
        return HttpResponse(error_data.get(), content_type='application/json', status=status.HTTP_400_BAD_REQUEST)
    username = None
    password = None
    emp_json = None
    user = None
    try:
        user_json = json.loads(request.body)
        username = user_json['username']
        password = user_json['password']
        emp_json = user_json['employee']
        # user = User.objects.get(username=username)
    except KeyError:
        error_data = ErrorData()
        error_data.set_error('Invalid Parameters')
        # return HttpResponse(error_data.get(), content_type='application/json', status=status.HTTP_400_BAD_REQUEST)
        # except:
        #     error_data = ErrorData()
        #     error_data.set_error('Invalid Parameters')
        return HttpResponse(error_data.get(), content_type='application/json', status=status.HTTP_400_BAD_REQUEST)
    except:
        error_data = ErrorData()
        error_data.set_error('Invalid Parameters')

    #    return HttpResponse(error_data.get(), content_type='application/json', status=status.HTTP_400_BAD_REQUEST)
    if user is not None:
        error_data = ErrorData()
        error_data.set_error('User already exists')
        return HttpResponse(error_data.get(), content_type='application/json', status=status.HTTP_409_CONFLICT)
    else:
        user = User.objects.create_user(username=username, password=password, is_staff=True)
        user.set_password(password)
        user.save()
        emp_req = EmployeeRequest(emp_json)
        emp_req.set_user_id(user.id)
        employee_service = EmployeeService(scope)
        address_id = None
        contact_id = None
        employee_service.create_employee(emp_req, user.id, address_id, contact_id)
        user_data = UserData()
        user_data.set_id(user.id)
        user_data.set_username(user.username)
        return HttpResponse(user_data.get(), content_type='application/json', status=status.HTTP_200_OK)


def get_current_user(request):
    user_obj = User


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def user(request):
    user_arr = json.loads(request.body)
    condition = None
    user_list = None
    for user_id in user_arr:
        if condition is None:
            condition = Q(id__exact=user_id)
        else:
            condition |= Q(id__exact=user_id)
    if condition is not None:
        user_list = User.objects.filter(condition)
    resp_list = NWisefinList()
    if user_list is not None:
        for user in user_list:
            user_obj = NWisefinUser()
            user_obj.set_id(user.id)
            user_obj.set_username(user.username)
            user_obj.set_email(user.email)
            user_obj.set_first_name(user.first_name)
            user_obj.set_last_name(user.last_name)
            user_obj.set_is_active(user.is_active)
            resp_list.append(user_obj)
    return HttpResponse(resp_list.get(), content_type='application/json')


def emp_sync_user(emp_code):
    password = "vsolv123"
    try:
        user = User.objects.create_user(username=emp_code, password=password, is_staff=True)
        adlogin_check = True
        user.set_password(password)
        user.save()
        user_id = user.id

    except:
        user = User.objects.get(username=emp_code)
        user_id = user.id
        adlogin_check = False
    emp_sync_user_dict = dict([('adlogin_check', adlogin_check), ('user_id', user_id)])
    return emp_sync_user_dict


def health_check(request):
    var = "good response !!!"
    return HttpResponse(var)

#
# def loginstatus(request):
#     FA =  settings._2FAMODE
#     code = request.GET.get('code')
#     value = signing.loads(code)
#     try:
#         auth_obj = Authrequest.objects.get(employee=value['employee'], created_date=value['date'])
#         if FA == True:
#             x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#             if x_forwarded_for:
#                 file = x_forwarded_for
#             else:
#                 file = request.META.get('REMOTE_ADDR')
#             ip_fr_validate = settings.KVB_IPS
#             print(file)
#             user_ip = file.split(",")
#             print(user_ip)
#             envIP_list = ip_fr_validate.split(",")
#             print(envIP_list)
#             for i in envIP_list:
#                 i = i.replace(" ", "")
#                 print(i)
#                 for j in user_ip:
#                     j = j.replace(" ", "")
#                     print(j)
#                     if i == j:
#                         cond_tion = True
#                         condition_ = '0'
#                         Login_notkvb = True
#                         print(condition_)
#                         break
#                     if i != j:
#                         cond_tion = False
#                         condition_ = '1'
#                         Login_notkvb = False
#                         print(condition_)
#                 if cond_tion:
#                     break
#         else:
#             Login_notkvb = True
#         if Login_notkvb == True:
#             emp = Employee.objects.get(id=value['employee'])
#             user = User.objects.get(id=emp.user_id)
#             request.user = user
#             # user = authenticate(username=user.username, password=user.password)
#             # logger.info(user.username, user.password)
#             if user is not None:
#                 request.user.auth_token_set.all().delete()
#                 token_obj = AuthToken.objects.create(user)
#                 auth_data = AuthData()
#                 logger.info(token_obj)
#                 auth_user = token_obj[0].user
#                 expiry = token_obj[0].expiry
#                 expiry_str = str(expiry)
#                 token = token_obj[1]
#                 auth_data.set_user_id(user.id)
#                 auth_data.set_token(token)
#                 employee = Employee.objects.get(user_id=user.id)
#                 auth_data.set_name(employee.full_name)
#                 auth_data.set_code(employee.code)
#                 auth_data.employee_id = employee.id
#                 request.session['token'] = token
#                 return HttpResponse(auth_data.get(), content_type='application/json', status=status.HTTP_200_OK)
#
#             else:
#                 error_data = ErrorData()
#                 error_data.set_error('Invalid credentials')
#                 return HttpResponse(error_data.get(), content_type='application/json',
#                                     status=status.HTTP_401_UNAUTHORIZED)
#
#         emp=Employee.objects.get(id=value['employee'])
#         mobile = list(Employeemobileno.objects.filter(code=emp.code).values('mobile_number'))
#         if mobile:
#             modbile_number = mobile[0]['mobile_number']
#             modbile_number = modbile_number[-3:]
#
#         else:
#             modbile_number = ''
#         return HttpResponse(json.dumps({'status': Login_notkvb, "mobile_number": modbile_number}),
#                         content_type='application/json')
#     except Authrequest.DoesNotExist:
#         # raise Http404("Tamparing blocked")
#         error_data = ErrorData()
#         error_data.set_error('Invalid credentials')
#         return HttpResponse(error_data.get(), content_type='application/json', status=status.HTTP_401_UNAUTHORIZED)
#
#
#



def envcheck(request):
    KVB_IPS = env.str('Two_Factor_Auth_KVB_Whitelisted_IPs')
    _2FAMODE = env.str('Two_Factor_Auth_Status')
    # otp bypass
    # _2FAMODE='Disabled'
    if _2FAMODE == 'Disabled':
        _2FAMODE = False
    else:
        _2FAMODE = True
    datas={}
    data = {'2FA_KVB_Whitelisted_IPs': KVB_IPS, '2FA_Status': env.str('Two_Factor_Auth_Status'), '_2FAMODE': _2FAMODE}
    datas['data'] = data
    return HttpResponse(json.dumps(datas), content_type="application/json")

# TA Dependents api call
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_emp_details(request):
    if request.method == 'POST':
        scope = request.scope
        service = TA_employee_service(scope)
        emp_arr = json.loads(request.body)
        resp_obj = service.employee_details_get(emp_arr)
        response = HttpResponse(resp_obj, content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_login_emp_details(request,userid):
    if request.method == 'GET':
        scope = request.scope
        service = TA_employee_service(scope)
        resp_obj = service.login_emp_details_get(userid)
        response = HttpResponse(resp_obj, content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_emp_grade1(request,emp_id):
    if request.method == 'GET':
        scope = request.scope
        service = TA_employee_service(scope)
        resp_obj = service.get_emp_grade1(emp_id)
        response = HttpResponse(resp_obj, content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_branch_details(request):
    if request.method == 'POST':
        scope = request.scope
        service = TA_employee_service(scope)
        branch_arr = json.loads(request.body)
        resp_obj = service.get_branch_details(branch_arr)
        response = HttpResponse(resp_obj, content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_branch_data(request,branch):
    if request.method == 'GET':
        scope = request.scope
        service = TA_employee_service(scope)
        resp_obj = service.get_branch_data(branch)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employee_details_get(request,empid):
    if request.method == 'GET':
        scope = request.scope
        service = TA_employee_service(scope)
        resp_obj = service.employee_details_get(empid)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employee_details_all_get_ta(request,empid):
    if request.method == 'GET':
        scope = request.scope
        service = TA_employee_service(scope)
        resp_obj = service.employee_all_details_get(empid)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def bank_gst_get(request):
    if request.method == 'GET':
        scope = request.scope
        gst = request.GET.get('gst', "")
        service = TA_employee_service(scope)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = service.bank_gst_get(gst, vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def role_bh_emp_get(request,branch_id):
    if request.method == 'GET':
        scope = request.scope
        user_id = request.employee_id
        emp = Employee.objects.get(id=user_id)
        employee_id = emp.id
        # maker = request.GET.get('maker', employee_id)
        maker = json.loads(request.GET.get('maker'))
        approver = request.GET.get('approver')
        service = TA_employee_service(scope)
        resp_obj = service.role_bh_emp_get(branch_id,approver,maker)
        resp = json.dumps(resp_obj, default=lambda o: o.__dict__)
        response = HttpResponse(resp, content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def branch_employee_get(request,branch):
    if request.method == 'GET':
        scope = request.scope
        tour_service = TA_employee_service(scope)
        search= request.GET.get('name')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        maker = request.GET.get('maker', None)
        resp_obj = tour_service.branch_employee_get(branch,search,vys_page,maker)
        return HttpResponse(resp_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def change_password(request):
    scope = request.scope
    resp_obj = json.loads(request.body)
    old_pass = resp_obj['old_password']
    new_pass = resp_obj['new_password']
    user_name = resp_obj['code']
    employee_service = EmployeeService(scope)
    portal_response = employee_service.change_password(old_pass, user_name, new_pass)
    response = HttpResponse(portal_response.get(), content_type="application/json")
    return response
