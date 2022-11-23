import io
import json

import pandas as pd
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from masterservice.util.masterutil import dictdefault
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.data.request.branchrequest import EmployeeBranchRequest,EmployeeBranchSyncRequest ,BranchLogRequest
from userservice.data.request.addresscontactrequest import ContactRequest,AddressRequest ,BranchAddressSyncRequest,BranchContactSyncRequest
from userservice.service.branchservice import EmployeeBranchService
from userservice.service.addresscontactservice import AddressService,ContactService
from django.db import transaction
from django.conf import settings
from userservice.models import EmployeeBranch, Department, EmployeeAddress
from userservice.controller.authcontroller import UserLogin_scheduler
from userservice.service.employeeservice import EmployeeService
from userservice.data.userutil import employeelog_status
from ast import literal_eval
from django.utils import timezone
from nwisefin.settings import logger


@transaction.atomic
@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employeebranch(request):
    if request.method == 'POST':
        scope = request.scope
        branch_service = EmployeeBranchService(scope)
        contact_service = ContactService(scope)
        address_service = AddressService(scope)
        branch_data = json.loads(request.body)
        user_id = request.employee_id
        branch_obj = EmployeeBranchRequest(branch_data)
        contact = branch_data.get("contact")
        contact_obj = ContactRequest(contact)
        address = branch_data.get("address")
        address_obj = AddressRequest(address)
        branch_id = branch_obj.get_id()
        if  branch_id != None:
            cont_add_id = branch_service.get_contact_address_id(branch_id)
            contact_obj.id = cont_add_id.contact_id
            address_obj.id = cont_add_id.address_id

        contact_id = contact_service.create_employeecontact(contact_obj, user_id)
        if not isinstance(contact_id,int):
            contact_id =None
        address_id = address_service.create_employeeaddress(address_obj, user_id)
        if not isinstance(address_id,int):
            address_id =None
        resp_obj = branch_service.create_branch(branch_obj, user_id,address_id,contact_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_employeebranch_list(request)


def fetch_employeebranch_list(request):
    scope = request.scope
    branch_service = EmployeeBranchService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    user_id = request.user.id
    resp_obj = branch_service.fetch_branch_list(request,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_employeebranch(request,employeebranch_id):
    if request.method == 'GET':
        scope = request.scope
        branch_service = EmployeeBranchService(scope)
        contact_service = ContactService(scope)
        address_service = AddressService(scope)
        user_id = request.user.id
        resp_obj = branch_service.fetch_branch(employeebranch_id)
        if resp_obj.contact_id is not None:
            cont_id = resp_obj.contact_id
            contact = contact_service.fetch_employeecontact(cont_id)
            resp_obj.contact = contact
        else:
            resp_obj.contact = None
        if resp_obj.address_id is not None:
            address_id = resp_obj.address_id
            address = address_service.fetch_employeeaddress(address_id)
            resp_obj.address = address
        else:
            resp_obj.address = None
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_employeebranch(request,employeebranch_id)


@csrf_exempt
def delete_employeebranch(request,employeebranch_id):
    scope = request.scope
    branch_service = EmployeeBranchService(scope)
    resp_obj = branch_service.delete_branch(employeebranch_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def userbranch(request):
    if request.method == 'GET':
        scope = request.scope
        branch_service = EmployeeBranchService(scope)
        user_id = request.employee_id
        resp_obj = branch_service.current_user_branch(user_id)
        if resp_obj is None :
            response = HttpResponse(None, content_type="application/json")
        else:
            response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def searchbranch(request):
    if request.method == 'GET':
        scope = request.scope
        branch_service = EmployeeBranchService(scope)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        query = request.GET.get('query')
        resp_obj = branch_service.search_branch(vys_page,query)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

#  employee branch sync

from userservice.controller.employeedepartmentmapping import EmpSync
import requests
import json

def branch_sync_data():
    empdept_map = EmpSync()
    token = empdept_map.get_token()
    client_url = settings.CLIENT_URL
    branch_url = client_url+str("next/v1/mw/master/sync")
    # branch_url =  settings.EMPLOYEESYNC_URL

    body_data = { "master" : "branch"}
    data = json.dumps(body_data)
    branch_headers = {'Authorization': 'Bearer ' + token}

    try:
        req_obj = requests.get(branch_url, data=data, headers=branch_headers,verify=False)
        logger.info(str(req_obj.status_code))
        if req_obj.status_code == 200:
            resp_json = json.loads(req_obj.text)
            out_msg = resp_json.get('out_msg')
            branch_data = out_msg.get('ESM_BRANCH_Master')
            logger.info("branch_data: "+str(branch_data))
    except:
        logger.info("invalid branch code")
        branch_data=[]

    return branch_data

# from userservice.models import ApiRelationalMapping
# from vysfinutility.permissions.util.apisyncutil import RelType
# from django.db.models import Q
from datetime import datetime
now = datetime.now()
#
# def branch_sync():
#     branch_data_arr= branch_sync_data()
#
#     for branch_data in branch_data_arr:
#         create_branch(branch_data)
#     return

@csrf_exempt
@api_view(['POST'])
def branch_sync_create(request):
    logger.info("k")
    scope = request.scope
    # branch_data = request.data
    # d = request.FILES.getlist('file')
    if not request.FILES['file'] is None:
        file = request.FILES['file']
        file_io = file.file
        file_str = file.read()
        branch_data = json.loads(file_str)
    for i in branch_data:
        create_branch(i, scope)
    response = HttpResponse("TEST CASE DONE", content_type="application/json")
    return response

def create_branch(branch_data, scope):
    branch_code = branch_data.get('CODE')
    branch_service = EmployeeBranchService(scope)
    contact_service = ContactService(scope)
    address_service = AddressService(scope)
    address1 = branch_data.get('ADDRESS1')
    contact_name = branch_data.get('CONTACT_PERSON')
    user_id = None
    try:
        branch = EmployeeBranch.objects.get(code=branch_code)
        branch_check = True
    except:
        branch_check = False

    if branch_check is False:
        # create
        branch_obj = EmployeeBranchRequest(branch_data)
        if address1 == ''  or address1 == None:
            address_id = None
        else:
            address_obj = AddressRequest(branch_data)
            address_id = address_service.create_employeeaddress(address_obj, user_id)

        if contact_name == ''or contact_name == None:
            contact_id = None
        else:
            contact_obj = ContactRequest(branch_data)
            contact_id = contact_service.create_employeecontact(contact_obj, user_id)

        branch_data = branch_service.create_branch(branch_obj, user_id, address_id, contact_id)

        branch_id = branch_data.id

    else:
        # update
        branch_id = branch.id
        branch_obj = branch_service.fetch_branch(branch_id)
        address_id = branch_obj.address_id
        contact_id = branch_obj.contact_id

        branch_obj = EmployeeBranchRequest(branch_data)
        branch_obj.id = branch_id

        if contact_name == '' or contact_name == None:
            contact_id = None
        else:
            contact_obj = EmployeeBranchRequest(branch_data)
            contact_obj.id = contact_id
            contact_id = contact_service.create_employeecontact(contact_obj, user_id)
        if address1 == ''  or address1 == None:
            address_id = None
        else:
            address_obj = EmployeeBranchRequest(branch_data)
            address_obj.id = address_id
            address_id = address_service.create_employeeaddress(address_obj, user_id)

        branch = branch_service.create_branch(branch_obj, user_id, address_id, contact_id)
        logger.info("update")
    return

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def missing_branch(request):
    arr=[]
    logger.info('missed branch')
    if not request.FILES['file'] is None:
        file = request.FILES['file']
        # file_io = file.file
        file_str = file.read()
        branch_data = json.loads(file_str)
    for i in branch_data:
        c = branch_data.get(i)
        branch_code = c.get('BRANCH_CODE')
        try:
            branch = EmployeeBranch.objects.get(code=branch_code)
            logger.info(branch)

        except:
            arr.append(branch_code)
    return_data={"missing data":arr}
    response = HttpResponse(return_data.values(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def branchmapping(request):
    scope = request.scope
    if not request.FILES['file'] is None:
        file = request.FILES['file']
        # file_io = file.file
        file_str = file.read()
        branch_data = json.loads(file_str)

    for i in branch_data:
        branch = branch_data.get(i)
        branch_code = branch.get('BRANCH_CODE')
        branch_service = EmployeeBranchService(scope)
        branch = branch_service.branchtype(branch_code)

    response = HttpResponse('BRANCH CODE mapped', content_type="application/json")
    return response

# admin api for adding missing branch in department
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def branch_dept_mapping(request):
    if request.method == 'GET':
        scope = request.scope
        branch_service = EmployeeBranchService(scope)
        resp_obj = branch_service.add_dept_branch()
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


def employeebranchdata_sync():
    employee_service = EmployeeService()
    for y in range(1, 1200, 300):
        # access code
        accesscode = UserLogin_scheduler()
        logger.info(str(accesscode))
        # branch sync parameters
        headers = {'Content-Type': 'application/javascript', 'Authorization': 'Bearer ' + accesscode}
        client_url = settings.CLIENT_URL
        branch_sync_url = client_url + str("next/v1/mw/master/sync")

        user_data = {"master": 'branch',"records":{ "from": y, "to": y + 300}}
        json_data = json.dumps(user_data)
        # branch sync
        req_obj = requests.get(branch_sync_url, data=json_data, headers=headers, verify=False)
        logger.info(str(req_obj))
        logger.info('Employee Branch Sync API called sucessfully')
        resp_json = json.loads(req_obj.text)
        outmsg = resp_json.get("out_msg")
        logger.info(str(outmsg))
        if (outmsg.get("ErrorCode")== '0' and outmsg.get("ErrorMessage") == 'Success'):
            emp_obj = BranchLogRequest(outmsg)
            if len(emp_obj.maindata)>0:
                resp_obj = employee_service.create_employeelog(emp_obj,employeelog_status.branch)

    datefilter = datetime.now().strftime('%Y-%m-%d')
    resp_obj = employee_service.get_employee_log_list(datefilter, employeelog_status.branch)
    logger.info("branch sync started")
    for x in resp_obj.data:
        main_data = x.maindata
        m_data = literal_eval(main_data)
        if len(m_data) > 0:
            employee_branch_sync(m_data)
    logger.info("branch sync finished")
    response = HttpResponse("BRANCH SYNC DONE", content_type="application/json")
    return response


def employee_branch_sync(emp_branch_data):
    # logger.info('branch_sync')
    for branch_data in emp_branch_data:
        branch_code = branch_data['CODE']
        branch_service = EmployeeBranchService()
        contact_service = ContactService()
        address_service = AddressService()
        user_id = None
        try:
            branch = EmployeeBranch.objects.get(code=branch_code)
            branch_check = True
        except:
            branch_check = False
        if branch_check is False:
            # create
            branch_obj = EmployeeBranchSyncRequest(branch_data)
            address_obj = BranchAddressSyncRequest(branch_data)
            contact_obj = BranchContactSyncRequest(branch_data)

            if address_obj.line1 is None:
                address_id = None
            else:
                address_id = address_service.create_employeeaddress(address_obj, user_id)

            if (contact_obj.name is not None) or  (contact_obj.landline is not None) or (contact_obj.mobile is not None )or  (contact_obj.email is not None) :
                contact_id = contact_service.create_employeecontact(contact_obj, user_id)
            else:
                contact_id = None

            branch_data = branch_service.create_branch(branch_obj, user_id, address_id, contact_id)
            # adding dept
            dept_obj = Department.objects.create(name=None, branch_id=branch_data.id, is_sys=True)
            code = "DGRP" + str(dept_obj.id)
            dept_obj.code = code
            dept_obj.save()

        else:
            # update

            branch_obj = EmployeeBranchSyncRequest(branch_data)
            address_obj = BranchAddressSyncRequest(branch_data)
            contact_obj = BranchContactSyncRequest(branch_data)

            # checking address
            if branch.address_id != None:
                address_check_cond = (address_obj.line1 == branch.address.line1)&(address_obj.line1 == branch.address.line1)&(address_obj.line2 == branch.address.line2)&(address_obj.line3 == branch.address.line3)&(address_obj.state_id == branch.address.state_id)&(address_obj.district_id == branch.address.district_id)&(address_obj.city_id == branch.address.city_id)&(address_obj.pincode_id == branch.address.pincode_id)
            else:
                address_check_cond = address_obj.line1 is None

            address_id = branch.address_id
            if address_check_cond is False:
                address_obj.id = address_id
                if address_id is None and address_obj.line1 is not None:
                        address_obj.id = None

                address_id = address_service.create_employeeaddress(address_obj, user_id)
                EmployeeBranch.objects.filter(id=branch.id).update(lastsync_date=timezone.now())

            #  checking contact
            if branch.contact_id != None:
                contact_check_cond = (contact_obj.name == branch.contact.name)&(contact_obj.designation_id == branch.contact.designation_id)&(contact_obj.landline == branch.contact.landline)&(contact_obj.landline2 == branch.contact.landline2)&(contact_obj.mobile == branch.contact.mobile)&(contact_obj.mobile2 == branch.contact.mobile2)&(contact_obj.email == branch.contact.email)
            else:
                contact_check_cond=((contact_obj.name is None) or  (contact_obj.landline is None) or (contact_obj.mobile is None )or  (contact_obj.email is None) )

            contact_id = branch.contact_id
            if contact_check_cond == False:
                contact_obj.id = contact_id
                if contact_id is None and ((contact_obj.name is not None) or  (contact_obj.landline is not None) or (contact_obj.mobile is not None )or  (contact_obj.email is not None) ):
                    contact_obj.id = None

                contact_id = contact_service.create_employeecontact(contact_obj, user_id)
                EmployeeBranch.objects.filter(id=branch.id).update(lastsync_date=timezone.now())

            #  checking branch
            branch_check_cond = (branch_obj.name == branch.name)&(branch_obj.tanno == branch.tanno)&(branch_obj.glno == branch.glno)&(branch_obj.stdno == branch.stdno)&(branch_obj.incharge == branch.incharge)&(branch_obj.entity == branch.entity)&(branch_obj.entity_detail == branch.entity_detail)&(branch_obj.gstin == branch.gstin)&(branch_obj.control_office_branch == branch.control_office_branch)&(address_id == branch.address_id)&(contact_id == branch.contact_id)

            if branch_check_cond == False:
                branch_obj.id = branch.id
                logger.info('branch update - '+str(branch.id))
                branch_service.create_branch(branch_obj, user_id, address_id, contact_id)

    return

@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ctr_office_branch(request):
    if request.method == 'POST':
        scope = request.scope
        branch_service = EmployeeBranchService(scope)
        branch_arr = json.loads(request.body)

        resp_obj =branch_service. ctr_office_info(branch_arr)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

# prpo-micro to micro
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employeebranch_get(request):
    employeebranch_data = json.loads(request.body)
    employeebranchId_arr = employeebranch_data['employeebranch_id']
    employeebranch = EmployeeBranch.objects.filter(id__in = employeebranchId_arr).values('id',
                                                                                         'code',
                                                                                         'name','gstin',
                                                                                         'address_id', 'contact_id')
    employeebranch_list_data = NWisefinList()
    for i in employeebranch:
        data = {"id": i['id'], "code":i['code'], "name": i['name'],"gstin": i["gstin"],"address_id": i["address_id"],
                "contact_id": i["contact_id"],
                "fullname":i['code'] + "--" + i['name']}
        employeebranch_list_data.append(data)
    return HttpResponse(employeebranch_list_data.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_branch_data(request):
    if request.method == 'POST':
        scope = request.scope
        branch_service = EmployeeBranchService(scope)
        branch_arr = json.loads(request.body)
        resp_obj =branch_service.fetch_branch_data(branch_arr)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_employeebranchdata(request, employeebranch_id):
    employeebranch = EmployeeBranch.objects.get(id=employeebranch_id)
    emp_data = {"id": employeebranch.id, "code": employeebranch.code, "name": employeebranch.name,
                "fullname":employeebranch.code + "--" + employeebranch.name,
                "address_id": employeebranch.address_id,
                "contact_id": employeebranch.contact_id,
                "gstin": employeebranch.gstin}
    employee_dic = json.dumps(emp_data, indent=4)
    return HttpResponse(employee_dic, content_type='application/json')
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_employeebranchdata_code(request, employeebranch_id):
    scope = request.scope
    emp_obj=EmployeeBranchService(scope)
    data=emp_obj.fetch_branch_using_code(employeebranch_id)
    return HttpResponse(data, content_type='application/json')

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_branch(request):
    scope = request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query')
    branch_service = EmployeeBranchService(scope)
    resp_obj = branch_service.search_empbranch(vys_page,query)
    return HttpResponse(resp_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_ebranchaddressdata(request, employeebranch_id):
    employeebranch1 = EmployeeBranch.objects.get(id=employeebranch_id)
    employeebranch = EmployeeAddress.objects.get(id=employeebranch1.address_id)
    emp_data = {"id": employeebranch1.id, "name": employeebranch1.name,
                "line1": employeebranch.line1, "line2": employeebranch.line2, "line3": employeebranch.line3,
                "pincode_id": employeebranch.pincode_id,
                "city_id": employeebranch.city_id,
                "district_id": employeebranch.district_id,
                "state_id": employeebranch.state_id}
    employee_dic = json.dumps(emp_data, indent=4)
    return HttpResponse(employee_dic, content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_ebranchaddress(request, employeebranch_id):
    employeebranch1 = EmployeeBranch.objects.get(id=employeebranch_id)
    employeebranch = EmployeeAddress.objects.get(id=employeebranch1.address_id)
    emp_data = {"id": employeebranch1.id, "name": employeebranch1.name,"gstin":employeebranch1.gstin,
                "line1": employeebranch.line1, "line2": employeebranch.line2, "line3": employeebranch.line3,
                "pincode_id": employeebranch.pincode_id,
                "city_id": employeebranch.city_id,
                "district_id": employeebranch.district_id,
                "state_id": employeebranch.state_id}
    employee_dic = json.dumps(emp_data, indent=4)
    return HttpResponse(employee_dic, content_type='application/json')


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def empbranch(request):
    scope = request.scope
    branch_service = EmployeeBranchService(scope)
    user_id = request.employee_id
    resp_obj = branch_service.empbranch(user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_user_branch_ctrl(request):
    if request.method == 'GET':
        scope = request.scope
        branch_service = EmployeeService(scope)
        user_id = request.employee_id
        resp_obj = branch_service.employeectrlbranch_get()
        if resp_obj is None :
            response = HttpResponse(None, content_type="application/json")
        else:
            response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ctrl_office_branch(request):
    if request.method == 'GET':
        scope = request.scope
        branch_service = EmployeeService(scope)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        # query = None
        # if request.GET.get('query') != '' or None:
        query = request.GET.get('query')
        resp_obj = branch_service.ctrl_office_info(query,vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employeebranch_activate_inactivate(request):
    if request.method == 'POST':
        scope = request.scope
        branch_service = EmployeeBranchService(scope)
        branch_data = json.loads(request.body)
        user_id = request.employee_id
        branch_obj = EmployeeBranchRequest(branch_data)
        resp_obj = branch_service.employeebranch_activate_inactivate(request, branch_obj)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employeebranch_download(request):
    scope = request.scope
    branch_service = EmployeeBranchService(scope)
    user_id = request.user.id
    resp_obj = branch_service.fetch_employeebranch_download(request)
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
    worksheet.write_string(2, 2, 'EmployeeBranch Master Excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="EmployeeBranch Master.xlsx"'
    logger.info("Test_Download Data:")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_employeebranch_get(request,employeebranch_id):
    if request.method == 'GET':
        scope = request.scope
        branch_service = EmployeeBranchService(scope)
        user_id = request.user.id
        resp_obj = branch_service.fetch_employeebranch_get(employeebranch_id,user_id,request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response



