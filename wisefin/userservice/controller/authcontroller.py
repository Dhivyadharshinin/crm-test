import json
import datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
import requests
from knox.auth import TokenAuthentication
from datetime import timedelta
from userservice.models import Employee, User, LogoutInfo
from django.contrib.auth import logout
from userservice.service.authservice import AuthService
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.data.response.nwisefinpage import NWisefinPage
from django.conf import settings
from nwisefin.settings import TOKEN_URL, CLIENT_ID, REDIRECT_URI, logger
from django.utils import timezone
val_url = settings.VYSFIN_URL
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage
ADFS_LOGIN = False

@csrf_exempt
def signup(request):
    signup_json = json.loads(request.body)
    entity_id = signup_json['entity_id']
    code = signup_json['code']
    full_name = signup_json['full_name']
    email_id = signup_json['email_id']
    password = signup_json['password']
    user = User.objects.create_user(username=code, password=password, is_staff=True)
    user.set_password(password)
    user.save()
    user_id = user.id
    Employee.objects.create(code=code, full_name=full_name, email_id=email_id, user_id=user_id)
    resp_obj = NWisefinSuccess()
    resp_obj.set_status(200)
    resp_obj.set_message(code + ' ' + full_name + ' User Created Successfully')
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
def auth_token(request):
    if ADFS_LOGIN == True :
        resp_data = json.loads(request.body)
        url = resp_data['url']
        url_info = url.split('?')
        url_code = url_info[1].split('&')
        code_data = url_code[0].split('=')
        code = code_data[1]
        logger.info('Received ADFS code :-' + str(code))
        if code is None:
            resp_obj = NWisefinError()
            resp_obj.set_code(ErrorMessage.INVALID_USER_ID)
            resp_obj.set_description(ErrorDescription.INVALID_USER_ID)
        else:
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = 'grant_type=authorization_code&scope=openid&client_id=' + CLIENT_ID + '&code=' + code + '&resource=nimbus_api&redirect_uri=' + REDIRECT_URI
            result = requests.post(TOKEN_URL, headers=headers, data=data, verify=False)
            logger.info('Response from the Token URL ' + str(result.status_code))
            service = AuthService()
            resp_obj = service.auth_welcome(result)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
    else:
        auth_json = json.loads(request.body)
        user_name = auth_json['username']
        password = auth_json['password']
        service = AuthService()
        if 'entity_id' in auth_json:
            entity_id = auth_json['entity_id']
            resp_obj = service.nwisefin_authenticate(user_name, password, entity_id)
        else:
            resp_obj = service.nwisefin_authenticate_default(user_name, password)
        logger.info('Auth Token generated')
        response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def test(request):
    resp_obj = NWisefinSuccess()
    resp_obj.set_status(200)
    resp_obj.set_message('Success')
    print(request.scope)
    tlocal = NWisefinThread(request.scope)
    print(tlocal._schema())
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

def converttoascii(password):
    l = len(password)
    newuser = ''
    for i in range(0, l):
        tmp = ord(password[i])
        temp = tmp - l
        g = len(str(temp))
        newuser = newuser + ("0" if g < 3 else "") + str(temp)
    return newuser

def get_authtoken():
    username = 'apuser'
    password = 'vsolv123'
    datenow = str(datetime.datetime.now().strftime("%Y-%m-%d"))
    password = datenow + username[::-1]
    password = converttoascii(password)
    logger.info("while using following url: " +str(val_url))
    headers = {"content-type": "application/json"}
    params = ''
    datas = json.dumps({"username": username, "password": "abcd", "auth_pwd": password, "apitype": "Direct"})
    print(datas)
    print("" +val_url+ "token")
    url = ""+val_url+"token"
    logger.info("while using following token url: " +str(url))

    resp = requests.post(url, params=params, data=datas, headers=headers,
                         verify=False)
    print(resp)
    logger.info("while after hitting url: " +str(url))
    logger.info("after hitting url response" + str(resp))
    token_data = json.loads(resp.content.decode("utf-8"))
    logger.info("mono_token_data" + str(token_data))
    print("token_data:-",token_data)
    ### Validations
    if token_data != '' and resp.status_code == 200:
        access_token = token_data.get("access")
        refresh_token = token_data.get("refresh")
        print("access_token:--",access_token)
    return access_token


def UserLogin_scheduler():
    client_url = settings.CLIENT_URL
    url = client_url + str("next//v1/oauth/cc/accesstoken")
#     url = settings.ADURL_ACCESS
    print('Token API started')
    client_id = settings.ADURL_KEY
    client_secret = settings.CLIENT_SECRET
    grant_type = 'client_credentials'
    response = requests.post(url, auth=(client_id, client_secret),
                             data={'grant_type': grant_type, 'client_id': client_id,
                                   'client_secret': client_secret})
    datas = json.loads(response.content.decode("utf-8"))
    access_token = datas.get("access_token")
    print('Token---->',access_token)
    return access_token

@csrf_exempt
def get_entity(request):
    auth_service = AuthService()
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = auth_service.get_entity(vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_emp_entity(request):
    employee_id = request.employee_id
    auth_service = AuthService()
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = auth_service.get_emp_entity(vys_page, employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def update_default_entity(request):
    query = request.GET.get('query')
    employee_id = request.employee_id
    auth_service = AuthService()
    resp_obj = auth_service.update_default_entity(query, employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated,NWisefinPermission])
def create_emp_entity(request):
    if request.method == 'POST':
        entity_serv = AuthService()
        ent_body = json.loads(request.body)
        entity_obj = entity_serv.create_emp_entity(ent_body)
        response = HttpResponse(entity_obj.get(),content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated,NWisefinPermission])
def delete_emp_entity(request):
    if request.method == 'POST':
        emp_ent = AuthService()
        resp = json.loads(request.body)
        entity_obj = emp_ent.delete_emp_entity(resp)
        response = HttpResponse(entity_obj.get(),content_type="application/json")
        return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def nwisefin_logout(request):
    user_id = request.user.id
    try:
        del request.session['token']
        request.user.auth_token_set.all().delete()
    except:
        request.user.auth_token_set.all().delete()
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    employee = Employee.objects.get(user_id=user_id)
    LogoutInfo.objects.create(employee=employee.id, ip_address=ip, logout_date=timezone.now())
    logout(request)
    success_obj = NWisefinSuccess()
    success_obj.set_status(SuccessStatus.SUCCESS)
    success_obj.set_message(SuccessMessage.SUCCESSFULLY_LOGOUT)
    return HttpResponse(success_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def nwisefin_RefreshToken(request):
    try:
        scope = request.scope
        token = scope['token']
        tok = TokenAuthentication()
        token.encode("utf-8")
        tstr = token.encode("utf-8")
        token_obj = tok.authenticate_credentials(tstr)
        token_key = token_obj[1].token_key
        user_id = request.user.id
        # expiry_date=request.user.auth_token_set.get(user_id=user_id)
        # expiry_date_add=expiry_date.expiry+timedelta(minutes=45)
        # resp_obj=request.user.auth_token_set.filter(user_id=user_id).update(expiry=expiry_date_add)
        response = NWisefinSuccess()
        response.set_status(SuccessStatus.SUCCESS)
        response.set_message(SuccessMessage.UPDATE_MESSAGE)
    except:
        response = NWisefinError()
        response.set_code(ErrorMessage.UNEXPECTED_ERROR)
        response.set_description(ErrorDescription.UNEXPECTED_ERROR)
    return HttpResponse(response.get(), content_type='application/json')


@csrf_exempt
def vow_signup(request):
    signup_json = json.loads(request.body)
    code = signup_json['code']
    password = "1234"
    user = User.objects.create_user(username=code, password=password)
    user.set_password(password)
    user.save()
    data = {"user_id": user.id}

    # Employee.objects.create(code=code, full_name=full_name, email_id=email_id, user_id=user_id)
    # resp_obj = NWisefinSuccess()
    # resp_obj.set_status(200)
    # resp_obj.set_message(code + ' ' + full_name + ' User Created Successfully')
    # response = HttpResponse(resp_obj.get(), content_type="application/json")
    return data


@csrf_exempt
def vow_auth_token(request):
    auth_json = json.loads(request.body)
    user_name = auth_json['username']
    password = auth_json['password']
    entity_id = auth_json['entity_id']
    service = AuthService()
    resp_obj = service.vow_welcome(user_name, password, entity_id)
    logger.info('Auth Token generated for vow')
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['POST'])
def vow_user_insert(request):
    try:
        data = json.loads(request.body)
        employee_id = request.employee_id
        # scope = request.scope
        sign_up = vow_signup(request)
        # user_id=data["user_id"]
        data.update(sign_up)
        service = AuthService()
        response = service.vow_user_insert(data, employee_id)
        # return HttpResponse(serv.get(), content_type="application/json")

    except:
        response = NWisefinError()
        response.set_code(ErrorMessage.UNEXPECTED_ERROR)
        response.set_description(ErrorDescription.UNEXPECTED_ERROR)
    return HttpResponse(response.get(), content_type='application/json')
