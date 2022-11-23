import pandas as pd
import json
from vendorservice.service.mainvendorservice import MainVendorService
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, serializers
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from docservice.service.documentservice import DocumentsService
from docservice.util.docutil import DocModule
from nwisefin import settings
from nwisefin.settings import logger
from masterservice.service.bankservice import BankService
from masterservice.service.bankbranchservice import BankBranchService
from masterservice.service.paymodeservice import PaymodeService
from validationservice.controller.vendorvalidation import VendorValidation
from vendorservice.data.response.errordata import ErrorData
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.exceptions.authexception import AuthException
from vendorservice.service.vendorservice import VendorService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from vendorservice.data.request.supplierrequest import ProfileRequest,ContactRequest,AddressRequest
from vendorservice.service.vendoraddressservice import VendorAddressService
from vendorservice.service.branchservice import branchservice
from vendorservice.service.paymentservice import paymentservice
from vendorservice.service.suppliertaxservice import TaxService
from vendorservice.data.request.vendoraddressrequest import AddressRequest
from vendorservice.service.venodrcontactservice import VendorContactService
from vendorservice.data.request.vendorcontactrequest import ContactRequest
from vendorservice.data.request.supplierrequest import ProfileRequest
from vendorservice.service.profileservice import ProfileService
from vendorservice.data.request.directorrequest import DirectorRequest
from vendorservice.service.directorservice import DirectorService
from vendorservice.data.request.vendorrequest import VendorRequest, VowVendorRequest
from vendorservice.service.vowservice import VOWService
from masterservice.service.cityservice import CityService
from masterservice.service.stateservice import StateService
from masterservice.service.districtservice import DistrictService
from masterservice.service.pincodeservice import PincodeService
# from masterservice.service.designationservice import DesignationService
from masterservice.service.contacttypeservice import ContactTypeService
from masterservice.service.customercategoryservice import CustomerCategoryService
from vendorservice.util.vendorutil import getType, getGroup, getOrgType, getClassification, getComposite
from userservice.service.employeeservice import EmployeeService
from vendorservice.util.vendorutil import getVendorStatus, getVendorMainStatus, \
    getVendorRequestStatus, getroleStatus, get_risk_type
from userservice.models import Employee
from vendorservice.service.vendoraccessorservice import VendorAccessorService
from django.db import transaction
from vendorservice.models import VendorDirector, VendorImage, SupplierBranch, SupplierTax
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from userservice.service.userservice import Vendor_user_service
val_url = settings.VYSFIN_URL


def getip(request):
    d = request.META.get('HTTP_X_FORWARDED_FOR')
    real_ip = request.META.get('HTTP_X_REAL_IP')
    a = request.META.get('REMOTE_ADDR')
    logger.info("HTTP_X_FORWARDED_FOR")
    logger.info(str(d))
    logger.info("HTTP_X_REAL_IP")
    logger.info(str(real_ip))
    logger.info("REMOTE_ADDR")
    logger.info(str(a))
    datas={}
    data={'HTTP_X_FORWARDED_FOR':d,'HTTP_X_REAL_IP':real_ip,'REMOTE_ADDR':a}
    datas['data']=data
    return HttpResponse(json.dumps(datas), content_type="application/json")


def getoldatmadata(request,vendor_id):
    scope = request.scope
    vendor_service = VendorService(scope)
    resp_data = vendor_service.fetch_data(vendor_id)
    return HttpResponse(json.dumps(resp_data), content_type="application/json")


@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def vendor(request):
    scope = request.scope
    vendor_service = VendorService(scope)
    schema = vendor_service.get_schema()
    entity_id = vendor_service.get_entity_id()
    response = None
    logger.info(str(request.user))
    if request.method == 'POST':
        # logger.info('CHECK_VENDOR_ID')
        # logger.info('CHECK_MOD_STATUS')
        employee_id = request.employee_id
        emp = Employee.objects.get(id=employee_id)
        employee_id = emp.id

        vendor_maker = vendor_service.ismaker(employee_id,True)
        if vendor_maker == False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.EMPLOYEE_ADMIN)
            error_obj.set_description(ErrorDescription.EMPLOYEE_ADMIN)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return HttpResponse(response, content_type='application/json')

        vendor_obj = json.loads(request.data.dict().get('data'))
        vendor_data = VendorRequest(vendor_obj)
        vendor_json = vendor_obj


        vendor_id = vendor_data.id
        rmid=vendor_data.get_rm_id()
        # emp = Employee.objects.get(user_id=user_id)
        # employee_id = emp.id
        if rmid == employee_id:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_RM_ID)
            error_obj.set_description(ErrorDescription.INVALID_RM_ID)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return HttpResponse(response, content_type='application/json')
        comreg=vendor_data.get_composite()

        logger.info('CHECK_VENDOR_ID' + '=' + str(vendor_id))
        mod_status = vendor_service.get_modification_status(vendor_id)
        logger.info('CHECK_MOD_STATUS'+'='+str(mod_status))
        if mod_status is True:
            old_vendor = vendor_service.fetch_vendor(vendor_data.id,employee_id)
            resp_obj = vendor_service.create_vendor_modification(vendor_data, vendor_json, employee_id)
            if resp_obj == 'PANNO_EXISTS':
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.PANNO_EXISTS)
                error_obj.set_description(ErrorDescription.PANNO_EXISTS)
                response = HttpResponse(error_obj.get(), content_type="application/json")
                return response

            new_vendor=resp_obj.get_id()
            if new_vendor:
                update=vendor_service.get_rmdata(new_vendor)

            # address
            vendoraddress_service = VendorAddressService(scope)
            address = vendor_obj.get("address")
            vendoraddress_obj = AddressRequest(address)
            respaddress_obj = vendoraddress_service.create_vendoraddress_modification(vendoraddress_obj, new_vendor, employee_id)
            # contact
            vendorcontact_service = VendorContactService(scope)
            contact = vendor_obj.get("contact")
            contact_obj = ContactRequest(contact)
            respcontact_obj = vendorcontact_service.create_vendorcontact_modification(new_vendor, contact_obj, employee_id)
            # profile
            profile_service = ProfileService(scope)
            profile = vendor_obj.get("profile")
            profile_obj = ProfileRequest(profile)
            respprofile_obj = profile_service.create_profile_modification(profile_obj, new_vendor, employee_id)
            # director
            director_service = DirectorService(scope)
            director = vendor_obj.get("director")
            director_obj = DirectorRequest(director)
            vendor_dir_obj = VendorDirector.objects.using(schema).filter(vendor_id=vendor_id, entity_id= entity_id)
            for a in vendor_dir_obj:
                flag = False
                for b in director:
                    try:
                        dir_id=b['id']
                    except:
                        dir_id=None
                    if a.id==dir_id:
                        flag = True

                if flag==False:
                    VendorDirector.objects.using(schema).filter(id=a.id, entity_id=entity_id).delete()

            for i in director:
                director_obj = DirectorRequest(i)
                respdirector_obj = director_service.create_director_modification(new_vendor, director_obj, employee_id)

            # update branch and tax for pan
            tax_service = TaxService(scope)
            ven_id = vendor_service.get_old_vendor_id(vendor_id)
            if resp_obj.panno != old_vendor.panno:
                branch_pan = vendor_service.update_branch_pan(ven_id,employee_id,resp_obj.panno)
                tax_pan = tax_service.update_tax_pan(employee_id,vendor_id,resp_obj.panno)
        else:
            resp_obj = vendor_service.create_vendor(vendor_data, vendor_json, employee_id)
            if resp_obj == 'PANNO_EXISTS':
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.PANNO_EXISTS)
                error_obj.set_description(ErrorDescription.PANNO_EXISTS)
                response = HttpResponse(error_obj.get(), content_type="application/json")
                return response
            elif resp_obj == 'GSTNO_EXISTS':
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.GSTNO_EXISTS)
                error_obj.set_description(ErrorDescription.GSTNO_EXISTS)
                response = HttpResponse(error_obj.get(), content_type="application/json")
                return response
            vendor_id = resp_obj.id

            accessor_service = VendorAccessorService(scope)
            accessor_service.set_accessor(vendor_id, employee_id, resp_obj.get_vendor_status())

            vendoraddress_service = VendorAddressService(scope)
            address = vendor_obj.get("address")
            vendoraddress_obj = AddressRequest(address)
            respaddress_obj = vendoraddress_service.create_vendoraddress(vendoraddress_obj, vendor_id, employee_id)

            vendorcontact_service = VendorContactService(scope)
            contact = vendor_obj.get("contact")
            contact_obj = ContactRequest(contact)
            respcontact_obj = vendorcontact_service.create_vendorcontact(vendor_id, contact_obj, employee_id)

            profile_service = ProfileService(scope)
            profile = vendor_obj.get("profile")
            profile_obj = ProfileRequest(profile)
            respprofile_obj = profile_service.create_profile(profile_obj, vendor_id, employee_id)

            director_service = DirectorService(scope)
            director = vendor_obj.get("director")
            director_obj = DirectorRequest(director)
            vendor_dir_obj = VendorDirector.objects.using(schema).filter(vendor_id=vendor_id, entity_id=entity_id)

            for a in vendor_dir_obj:
                flag = False

                for b in director:
                    try:
                        dir_id = b['id']
                    except:
                        dir_id = None
                    if a.id==dir_id:
                        flag = True

                if flag==False:
                    VendorDirector.objects.using(schema).filter(id=a.id, entity_id=entity_id).delete()

            for i in director:
                director_obj = DirectorRequest(i)
                respdirector_obj = director_service.create_director(vendor_id, director_obj, employee_id)

        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    else:
        try:
            resp_obj = get_vendor_list(request)
            response = HttpResponse(resp_obj.get(), content_type="application/json")
            return response
        except AuthException:
            error_data = ErrorData()
            error_data.set_error('Invalid credentials')
            return HttpResponse(error_data.get(), content_type='application/json', status=status.HTTP_403_FORBIDDEN)


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def director(request, vendor_id):
    response = HttpResponse()
    if request.method == 'POST':
        scope = request.scope
        director_obj = json.loads(request.body)
        vendor_service = VendorService(scope)
        employee_id = request.employee_id
        resp_obj = vendor_service.create_director(director_obj, vendor_id, employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    else:
        response.write('POST Operation only allowed')
        return response


def get_vendor_list(request):
    query = None
    employee_id = request.employee_id
    scope = request.scope
    emp = Employee.objects.get(id=employee_id)
    employee_id = emp.id

    # employee_service = EmployeeService()
    # user_role = employee_service.get_employee_role(employee_id)
    status=0
    right_checker=False
    right_header=False
    vendor_service = VendorService(scope)
    # vendor_checker=vendor_service.ischecker(request)
    # if vendor_checker==True:
    #     right_checker=True
    #     status=getroleStatus('move to header')
    vendor_maker = vendor_service.ismaker(employee_id,True)
    if vendor_maker==True:
        status=getroleStatus('move to rm')
    # vendor_header = vendor_service.isheader(request)
    # if vendor_header == True:
    #     right_header = True
    #     status = getroleStatus('approved')
    # vendor=vendor_service.ismaker(request)
    right_check=False
    # if right_checker==True and right_header==True:
    #     right_check=True
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    # status = 3
    # resp_obj = vendor_service.(request,'query', vys_page, user_id)
    vendor_accessor_service = VendorAccessorService(scope)
    resp_obj = vendor_accessor_service.get_vendor_list(request, employee_id, status, vys_page, query,right_check)
    x = resp_obj.data
    for i in x:
        vendorstatus_get = getVendorStatus(i.vendor_status)
        # logger.info(i,i.code)
        i.vendor_status_name = vendorstatus_get
        vendorrequeststatus_get = getVendorRequestStatus(i.requeststatus)
        i.requeststatus_name = vendorrequeststatus_get
        vendormainstatus_get = getVendorMainStatus(i.mainstatus)
        i.mainstatus_name = vendormainstatus_get
        composite = getComposite(i.composite)
        logger.info(str(i.composite))
        i.composite = composite.text

        i.q_modify = False
        # if (i.created_by["id"] == user_id):
        if (i.vendor_status == 0 or i.vendor_status == 1):
             i.q_modify = True

    return resp_obj

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_vendor_code(request, vendor_code):
    if request.method == 'GET':
        response = HttpResponse()
        employee_id = request.employee_id
        scope = request.scope
        vendor_service = VendorService(scope)
        resp_obj = vendor_service.fetch_vendor_code(vendor_code, employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_vendor(request, vendor_id):
    if request.method == 'GET':
        response = HttpResponse()
        employee_id = request.employee_id
        scope = request.scope
        vendor_service = VendorService(scope)
        resp_obj = vendor_service.fetch_vendor(vendor_id, employee_id)

        # monesh
        address_service = VendorAddressService(scope)
        contact_service = VendorContactService(scope)
        director_service = DirectorService(scope)
        profile_service = ProfileService(scope)
        state_service = StateService(scope)
        city_service = CityService(scope)
        district_service = DistrictService(scope)
        pincode_service = PincodeService(scope)
        contacttype_service = ContactTypeService(scope)
        # designation_service = DesignationService(scope)
        customercategory_service = CustomerCategoryService(scope)

        vendor_id = resp_obj.id
        address = address_service.fetch_vendoraddress(vendor_id, employee_id)
        resp_obj.address = address
        contact = contact_service.fetch_vendorcontact(vendor_id, employee_id)
        resp_obj.contact = contact
        profile = profile_service.fetch_profile(vendor_id, employee_id)
        resp_obj.profile = profile
        director = director_service.fetch_director(vendor_id, employee_id)
        resp_obj.director = director
        # address
        city_id = resp_obj.address.city_id
        city = city_service.fetch_city(city_id, employee_id)
        resp_obj.address.city_id = city
        state_id = resp_obj.address.state_id
        state = state_service.fetchstate(state_id)
        resp_obj.address.state_id = state
        district_id = resp_obj.address.district_id
        district = district_service.fetchdistrict(district_id)
        resp_obj.address.district_id = district
        pincode_id = resp_obj.address.pincode_id
        pincode = pincode_service.fetch_pincode(pincode_id, employee_id)
        resp_obj.address.pincode_id = pincode
        # contact

        # designation_id = resp_obj.contact.designation_id
        # designation = designation_service.fetch_designation(designation_id)
        # resp_obj.contact.designation_id = designation

        # orgtype
        orgtype_id = resp_obj.orgtype
        orgtype = getOrgType(orgtype_id)
        resp_obj.orgtype = orgtype

        # classification
        classification_id = resp_obj.classification
        classification = getClassification(classification_id)
        resp_obj.classification = classification

        # group
        group_id = resp_obj.group
        group = getGroup(group_id)
        resp_obj.group = group

        # composite
        composite_id = resp_obj.composite
        composite = getComposite(composite_id)
        resp_obj.composite = composite

        # type
        type_id = resp_obj.type
        type = getType(type_id)
        resp_obj.type = type

        # rmname
        employee_service = EmployeeService(scope)
        rm_id = resp_obj.rm_id
        rmname = employee_service.get_employee(rm_id, employee_id)
        resp_obj.rm_id = rmname

        custcategory_id = resp_obj.custcategory_id
        custcategory = customercategory_service.fetch_customercategory(custcategory_id, employee_id)
        resp_obj.custcategory_id = custcategory

        # user_id
        resp_obj.user_id = employee_id
        vendor_status = resp_obj.vendor_status

        vendorstatus_get = getVendorStatus(vendor_status)
        resp_obj.vendor_status_name = vendorstatus_get

        vendormainstatus_get = getVendorMainStatus(resp_obj.mainstatus)
        resp_obj.mainstatus_name = vendormainstatus_get
        vendorrequeststatus_get = getVendorRequestStatus(resp_obj.requeststatus)
        resp_obj.requeststatus_name = vendorrequeststatus_get
        flag = vendor_service.check_vendor_category(vendor_id)
        resp_obj.compliance_flag = flag
        organization = vendor_service.get_org_type(vendor_id,employee_id)
        resp_obj.kyc_org = organization['org_name']
        resp_obj.is_rm = organization['vendor_rm']
        if flag == True:
            compilence_flag = vendor_service.iscompliance(request)
            resp_obj.is_header = compilence_flag
        else:
            header_flag = vendor_service.isheader(request)
            resp_obj.is_header = header_flag

        # vendorrisktype_get=get_risk_type(resp_obj.risktype)
        # resp_obj.risktype = vendorrisktype_get
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    else:
        response = HttpResponse()
        response.write('Post operation not allowed')
        return response



@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_modificationvendor(request, vendor_id):
    if request.method == 'GET':
        response = HttpResponse()
        employee_id = request.employee_id
        scope = request.scope
        vendor_service = VendorService(scope)
        resp_obj = vendor_service.fetch_vendor(vendor_id, employee_id)

        # monesh
        address_service = VendorAddressService(scope)
        contact_service = VendorContactService(scope)
        director_service = DirectorService(scope)
        profile_service = ProfileService(scope)
        state_service = StateService(scope)
        city_service = CityService(scope)
        district_service = DistrictService(scope)
        pincode_service = PincodeService(scope)
        contacttype_service = ContactTypeService(scope)
        # designation_service = DesignationService(scope)
        customercategory_service = CustomerCategoryService(scope)

        vendor_id1 = resp_obj.get_modify_ref_id()
        address = address_service.fetch_vendoraddress_modification(vendor_id1, employee_id)
        resp_obj.address = address
        contact = contact_service.fetch_vendorcontact_modification(vendor_id1, employee_id)
        resp_obj.contact = contact
        profile = profile_service.fetch_profile_modification(vendor_id1, employee_id)
        resp_obj.profile = profile
        director = director_service.fetch_director_modification(vendor_id1, employee_id)
        resp_obj.director = director
        # address
        city_id = resp_obj.address.city_id
        city = city_service.fetch_city(city_id, employee_id)
        resp_obj.address.city_id = city
        state_id = resp_obj.address.state_id
        state = state_service.fetchstate(state_id)
        resp_obj.address.state_id = state
        district_id = resp_obj.address.district_id
        district = district_service.fetchdistrict(district_id)
        resp_obj.address.district_id = district
        pincode_id = resp_obj.address.pincode_id
        pincode = pincode_service.fetch_pincode(pincode_id, employee_id)
        resp_obj.address.pincode_id = pincode
        # contact
        #
        # designation_id = resp_obj.contact.designation_id
        # designation = designation_service.fetch_designation(designation_id)
        # resp_obj.contact.designation_id = designation

        # orgtype
        orgtype_id = resp_obj.orgtype
        orgtype = getOrgType(orgtype_id)
        resp_obj.orgtype = orgtype

        # classification
        classification_id = resp_obj.classification
        classification = getClassification(classification_id)
        resp_obj.classification = classification

        # group
        group_id = resp_obj.group
        group = getGroup(group_id)
        resp_obj.group = group

        # composite
        composite_id = resp_obj.composite
        composite = getComposite(composite_id)
        resp_obj.composite = composite

        # type
        type_id = resp_obj.type
        type = getType(type_id)
        resp_obj.type = type

        # rmname
        employee_service = EmployeeService(scope)
        rm_id = resp_obj.rm_id
        rmname = employee_service.get_employee(rm_id, employee_id)
        resp_obj.rm_id = rmname

        custcategory_id = resp_obj.custcategory_id
        custcategory = customercategory_service.fetch_customercategory(custcategory_id, employee_id)
        resp_obj.custcategory_id = custcategory

        # user_id
        resp_obj.user_id = employee_id
        vendor_status = resp_obj.vendor_status

        vendorstatus_get = getVendorStatus(vendor_status)
        resp_obj.vendor_status_name = vendorstatus_get

        vendormainstatus_get = getVendorMainStatus(resp_obj.mainstatus)
        resp_obj.mainstatus_name = vendormainstatus_get
        vendorrequeststatus_get = getVendorRequestStatus(resp_obj.requeststatus)
        resp_obj.requeststatus_name = vendorrequeststatus_get
        # vendorrisktype_get=get_risk_type(resp_obj.risktype)
        # resp_obj.risktype = vendorrisktype_get

        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    else:
        response = HttpResponse()
        response.write('Post operation not allowed')
        return response
@csrf_exempt
@transaction.atomic
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def status_update(request, vendor_id):
    employee_id = request.employee_id
    scope = request.scope
    vendor_service = MainVendorService(scope)
    response = vendor_service.status_update(request, vendor_id, employee_id)
    return response


def do_validation(request):
    value = request.GET.get('value')

    employee_id = request.GET.get('employee_id')
    type = request.GET.get('type')
    otp = request.GET.get('otp')
    resp_dict = {'validation_status': True}
    validation_resp = None
    vendor_validation = VendorValidation()
    if type == 'pan':
        validation_resp = vendor_validation.pan_validation(value)

        # validation_resp = json.loads(validation_resp)
        logger.info(str(validation_resp))
    elif type == 'gst':
        validation_resp = vendor_validation.gst_validation(value)
        logger.info(str(validation_resp))
    elif type == 'ifsc':
        validation_resp = vendor_validation.ifsc_validation(value)
        logger.info(str(validation_resp))
    elif type == 'gen_OTP':
        validation_resp = vendor_validation.gen_validation(value,employee_id)
        logger.info(str(validation_resp))
    elif type == 'validate_OTP':
        validation_resp = vendor_validation.otp_validation(value,otp,employee_id,request)
        logger.info(str(validation_resp))
    elif type == 'vendor_name':
        validation_resp = vendor_validation.vendor_name_validation(value, request)
        logger.info(str(validation_resp))

    return HttpResponse(validation_resp, content_type='application/json')

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_vendor_searchlist(request):
    scope = request.scope
    panno = request.GET.get('panno',None)
    name = request.GET.get('name',None)
    gstno = request.GET.get('gstno',None)
    code = request.GET.get('code',None)
    type = request.GET.get('type',None)
    renewal_date = request.GET.get('renewal_date',None)
    rm_id = request.GET.get('rm_id',None)
    vendor_status = request.GET.get('vendor_status',None)
    query = {"name": name, "panno": panno, "gstno": gstno, "code": code, "type": type, "renewal_date": renewal_date,
             "rm_id": rm_id, "vendor_status": vendor_status}
    employee_id = request.employee_id
    emp = Employee.objects.get(id=employee_id)
    employee_id = emp.id

    vendor_service = VendorService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    status = None
    right_checker=False
    right_header=False
    vendor_service = VendorService(scope)
    vendor_checker = vendor_service.ischecker(request)
    if vendor_checker == True:
        right_checker=True
        status = getroleStatus('move to header')
    vendor_maker = vendor_service.ismaker(employee_id, True)
    if vendor_maker == True:
        status = getroleStatus('move to rm')
    vendor_header = vendor_service.isheader(request)
    if vendor_header == True:
        right_header=True
        status = getroleStatus('approved')
    right_check=False
    if right_checker==True  and right_header==True:
        right_check=True

    vendor_accessor_service = VendorAccessorService(scope)
    resp_obj = vendor_accessor_service.get_vendor_list(request, employee_id, status, vys_page, query,right_check)
    x = resp_obj.data

    for i in x:


        vendorstatus_get = getVendorStatus(i.vendor_status)
        logger.info(str(i.code))
        i.vendor_status_name = vendorstatus_get
        vendorrequeststatus_get = getVendorRequestStatus(i.requeststatus)
        i.requeststatus_name = vendorrequeststatus_get
        vendormainstatus_get = getVendorMainStatus(i.mainstatus)
        i.mainstatus_name = vendormainstatus_get
        composite = getComposite(i.composite)
        logger.info(str(i.composite))
        i.composite = composite.text

        i.q_modify = False
        # if (i.created_by["id"] == user_id):
        if (i.vendor_status == 0 or i.vendor_status == 1):
            i.q_modify = True

    address_service = VendorAddressService(scope)
    contact_service = VendorContactService(scope)
    director_service = DirectorService(scope)
    profile_service = ProfileService(scope)
    x = resp_obj.data
    for i in x:
        vendor_id = i.id
        address = address_service.fetch_vendoraddress(vendor_id, employee_id)
        i.address = address
        contact = contact_service.fetch_vendorcontact(vendor_id, employee_id)
        i.contact = contact
        profile = profile_service.fetch_profile(vendor_id, employee_id)
        i.profile = profile
        director = director_service.fetch_director(vendor_id, employee_id)
        i.director = director

    return HttpResponse(resp_obj.get(), content_type='application/json')

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def q_validation(request, vendor_id):
    user_id = request.user.id
    scope = request.scope
    vendor_service = VendorService(scope)
    resp_obj = vendor_service.q_validation(vendor_id)

    return HttpResponse(resp_obj, content_type='application/json')


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def modification_summary(request):
    query = None
    user_id = request.employee_id
    scope = request.scope
    # emp = Employee.objects.get(user_id=user_id)
    # employee_id = emp.id

    # employee_service = EmployeeService()
    # user_role = employee_service.get_employee_role(employee_id)

    vendor_service = VendorService(scope)
    page = request.GET.get('page', 1)
    supplierprocess = request.GET.get('supplierprocess')
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    # status = user_role

    if supplierprocess=='7':
        status=None
        right_checker=False
        right_header=False
        vendor_checker = vendor_service.ischecker(request)
        if vendor_checker == True:
            right_checker = True
            status = getroleStatus('move to header')
        vendor_header = vendor_service.isheader(request)
        if vendor_header == True:
            right_header = True
            status = getroleStatus('approved')

        right_check = False
        if right_checker == True and right_header == True:
            right_check = True
        vendor_accessor_service = VendorAccessorService(scope)
        resp_obj = vendor_accessor_service.get_checkerheader_list(request, user_id, status, vys_page, query, right_check)
    else:
        resp_obj = vendor_service.get_modification_data(request, 'query', vys_page, supplierprocess, user_id)

    x = resp_obj.data
    for i in x:
        vendorstatus_get = getVendorStatus(i.vendor_status)
        i.vendor_status_name = vendorstatus_get
        vendorrequeststatus_get = getVendorRequestStatus(i.requeststatus)
        i.requeststatus_name = vendorrequeststatus_get
        vendormainstatus_get = getVendorMainStatus(i.mainstatus)
        i.mainstatus_name = vendormainstatus_get
        composite = getComposite(i.composite)
        i.composite = composite.text

        i.q_modify = False
        if (i.created_by["id"] == user_id):
            if (i.vendor_status == 0 or i.vendor_status == 1):
                i.q_modify = True

    return HttpResponse(resp_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def modification_request(request, vendor_id):
    scope = request.scope
    vendor_service = VendorService(scope)
    user_id = request.employee_id
    supplierprocess = request.GET.get('supplierprocess')
    resp_obj = vendor_service.modificationstatus_update(vendor_id,supplierprocess, user_id)
    return HttpResponse(resp_obj.get(), content_type='application/json')

@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def modification_reject(request, vendor_id):
    scope = request.scope
    ven_service = MainVendorService(scope)
    response = ven_service.modification_reject(request,vendor_id)
    return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def upload(request, vendor_id):
    if request.method == 'POST':
        scope = request.scope
        doc_service = DocumentsService(scope)
        docmodule_obj = DocModule()
        user_id = request.user.id
        emp = Employee.objects.get(user_id=user_id)
        user_id = emp.id
        params = {}
        params['module'] = docmodule_obj.VENDOR
        params['ref_id'] = vendor_id
        params['ref_type'] = docmodule_obj.VENDOR
        resp_obj = doc_service.upload(request, params)
        # docmnts_json = json.loads(resp_obj.get())['data'][0]
        docmnts_json = resp_obj.get()
        docmnts_json = json.loads(docmnts_json)
        # logger.info(docmnts_json)
        for doc_json in docmnts_json['data']:
            vend_doc = VendorImage()
            vend_doc.vendor_id = vendor_id
            vend_doc.file_id = doc_json['id']
            vend_doc.file_name = doc_json['file_name']
            vend_doc.created_by = user_id
            vend_doc.save()

        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return HttpResponse(response, content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_file(request, vendor_id, file_id):
    if request.method == 'GET':
        scope = request.scope
        doc_service = DocumentsService(scope)
        user_id = request.user.id
        emp = Employee.objects.get(user_id=user_id)
        user_id = emp.id
        resp_obj = doc_service.download(file_id, user_id)
        return resp_obj

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def vendorrm_validation(request, vendor_id):
    if request.method == 'GET':
        scope = request.scope
        ven_service = VendorService(scope)
        resp_obj = ven_service.vendor_validate(vendor_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return HttpResponse(response, content_type='application/json')
# # commented for scheduler
# @transaction.atomic
# def renewal_approve(vendor_id):
#     # scheduler api
#     vendor_service = VendorService()
#     resp_obj = vendor_service.modificationapprove_serviceview(vendor_id)
#     x = resp_obj.data
#     data = []
#     user_id = -1
#     vendor_resp=Vendor.objects.get(id=vendor_id)
#     request_sts=vendor_resp.requeststatus
#     # if request_sts==5:
#     #     resp_obj = vendor_service.modification_approve_status(vendor_id, request_sts, user_id)
#     if request_sts == 5:
#         for i in x:
#             mod_status = i.mod_status
#             old_id = i.ref_id
#             new_id = i.modify_ref_id
#             mod_type = i.ref_type
#             if mod_status !=ModifyStatus.delete:
#             #     resp_obj = vendor_service.modify_delrecursion(vendor_id, old_id,user_id)
#                 if mod_type == VendorRefType.VENDOR:
#                     resp_obj = vendor_service.modification_action_vendor(mod_status, old_id, new_id, user_id)
#                 if mod_type == VendorRefType.VENDOR_ADDRESS:
#                     address_service = VendorAddressService()
#                     resp_obj = address_service.modification_action_vendoraddress(mod_status, old_id, new_id, vendor_id, user_id)
#                 if mod_type == VendorRefType.VENDOR_CONTACT:
#                     contact_service = VendorContactService()
#                     resp_obj = contact_service.modification_action_vendorcontact(mod_status, old_id, new_id, vendor_id, user_id)
#                 if mod_type == VendorRefType.VENDOR_PROFILE:
#                     profile_service = ProfileService()
#                     resp_obj = profile_service.modification_action_vendorprofile(mod_status, old_id, new_id, vendor_id, user_id)
#                 if mod_type == VendorRefType.VENDOR_DIRECTOR:
#                     director_service = DirectorService()
#                     resp_obj = director_service.modification_action_vendordirector(mod_status, old_id, new_id, vendor_id,
#                                                                                    user_id)
#                 if mod_type == VendorRefType.VENDOR_BRANCH:
#                     branch_service = branchservice()
#                     resp_obj = branch_service.modification_action_branch(mod_status, old_id, new_id, vendor_id, user_id)
#                 if mod_type == VendorRefType.VENDOR_CONTRACT:
#                     contract_service = ContractorService()
#                     resp_obj = contract_service.modification_action_contractor(mod_status, old_id, new_id, vendor_id, user_id)
#                 if mod_type == VendorRefType.VENDOR_CLIENT:
#                     client_service = ClientService()
#                     resp_obj = client_service.modification_action_client(mod_status, old_id, new_id, vendor_id, user_id)
#                 if mod_type == VendorRefType.VENDOR_PRODUCT:
#                     product_service = productservice()
#                     resp_obj = product_service.modification_action_product(mod_status, old_id, new_id, vendor_id, user_id)
#                 if mod_type == VendorRefType.VENDOR_DOCUMENT:
#                     document_service = DocumentService()
#                     resp_obj = document_service.modification_action_document(mod_status, old_id, new_id, vendor_id, user_id)
#                 if mod_type == VendorRefType.VENDOR_SUPPLIERTAX:
#                     suppliertax_service = TaxService()
#                     resp_obj = suppliertax_service.modification_action_suppliertax(mod_status, old_id, new_id, vendor_id,
#                                                                                    user_id)
#                 if mod_type == VendorRefType.VENDOR_PAYMENT:
#                     payment_service = paymentservice()
#                     resp_obj = payment_service.modification_action_payment(mod_status, old_id, new_id, vendor_id, user_id)
#                 if mod_type == VendorRefType.VENDOR_ACTIVITY:
#                     activity_service = ActivityService()
#                     resp_obj = activity_service.modification_action_activity(mod_status, old_id, new_id, vendor_id, user_id)
#                 if mod_type == VendorRefType.VENDOR_ACTIVITYDETAIL:
#                     activitydtl_service = ActivityDetailsService()
#                     resp_obj = activitydtl_service.modification_action_activitydetail(mod_status, old_id, new_id, vendor_id,
#                                                                                       user_id)
#                 if mod_type == VendorRefType.VENDOR_CATELOG:
#                     catelog_service = CatelogService()
#                     resp_obj = catelog_service.modification_action_catelog(mod_status, old_id, new_id, vendor_id, user_id)
#             if mod_status == ModifyStatus.delete:
#                 #     resp_obj = vendor_service.modify_delrecursion(vendor_id, old_id,user_id)
#                 if mod_type == VendorRefType.VENDOR:
#                     resp_obj = vendor_service.modification_action_vendor(mod_status, old_id, new_id, user_id)
#                 if mod_type == VendorRefType.VENDOR_ADDRESS:
#                     address_service = VendorAddressService()
#                     resp_obj = address_service.modification_action_vendoraddress(mod_status, old_id, new_id, vendor_id,
#                                                                                  user_id)
#                 if mod_type == VendorRefType.VENDOR_CONTACT:
#                     contact_service = VendorContactService()
#                     resp_obj = contact_service.modification_action_vendorcontact(mod_status, old_id, new_id, vendor_id,
#                                                                                  user_id)
#                 if mod_type == VendorRefType.VENDOR_PROFILE:
#                     profile_service = ProfileService()
#                     resp_obj = profile_service.modification_action_vendorprofile(mod_status, old_id, new_id, vendor_id,
#                                                                                  user_id)
#                 if mod_type == VendorRefType.VENDOR_DIRECTOR:
#                     director_service = DirectorService()
#                     resp_obj = director_service.modification_action_vendordirector(mod_status, old_id, new_id,
#                                                                                    vendor_id,
#                                                                                    user_id)
#                 if mod_type == VendorRefType.VENDOR_BRANCH:
#                     branch_service = branchservice()
#                     resp_obj = branch_service.modification_action_branch(mod_status, old_id, new_id, vendor_id, user_id)
#                 if mod_type == VendorRefType.VENDOR_CONTRACT:
#                     contract_service = ContractorService()
#                     resp_obj = contract_service.modification_action_contractor(mod_status, old_id, new_id, vendor_id,
#                                                                                user_id)
#                 if mod_type == VendorRefType.VENDOR_CLIENT:
#                     client_service = ClientService()
#                     resp_obj = client_service.modification_action_client(mod_status, old_id, new_id, vendor_id, user_id)
#                 if mod_type == VendorRefType.VENDOR_PRODUCT:
#                     product_service = productservice()
#                     resp_obj = product_service.modification_action_product(mod_status, old_id, new_id, vendor_id,
#                                                                            user_id)
#                 if mod_type == VendorRefType.VENDOR_DOCUMENT:
#                     document_service = DocumentService()
#                     resp_obj = document_service.modification_action_document(mod_status, old_id, new_id, vendor_id,
#                                                                              user_id)
#                 if mod_type == VendorRefType.VENDOR_SUPPLIERTAX:
#                     suppliertax_service = TaxService()
#                     resp_obj = suppliertax_service.modification_action_suppliertax(mod_status, old_id, new_id,
#                                                                                    vendor_id,
#                                                                                    user_id)
#                 if mod_type == VendorRefType.VENDOR_PAYMENT:
#                     payment_service = paymentservice()
#                     resp_obj = payment_service.modification_action_payment(mod_status, old_id, new_id, vendor_id,
#                                                                            user_id)
#                 if mod_type == VendorRefType.VENDOR_ACTIVITY:
#                     activity_service = ActivityService()
#                     resp_obj = activity_service.modification_action_activity(mod_status, old_id, new_id, vendor_id,
#                                                                              user_id)
#                 if mod_type == VendorRefType.VENDOR_ACTIVITYDETAIL:
#                     activitydtl_service = ActivityDetailsService()
#                     resp_obj = activitydtl_service.modification_action_activitydetail(mod_status, old_id, new_id,
#                                                                                       vendor_id,
#                                                                                       user_id)
#                 if mod_type == VendorRefType.VENDOR_CATELOG:
#                     catelog_service = CatelogService()
#                     resp_obj = catelog_service.modification_action_catelog(mod_status, old_id, new_id, vendor_id,
#                                                                            user_id)
#         for i in x:
#             mod_status = i.mod_status
#             old_id = i.ref_id
#             new_id = i.modify_ref_id
#             mod_type = i.ref_type
#             if mod_status == ModifyStatus.update:
#                 if mod_type == VendorRefType.VENDOR:
#                     vendor_del=Vendor.objects.filter(id=new_id).delete()
#                 if mod_type == VendorRefType.VENDOR_BRANCH:
#                     branch = SupplierBranch.objects.filter(id=new_id).delete()
#                 if mod_type == VendorRefType.VENDOR_CONTRACT:
#                     contractor_del = VendorSubContractor.objects.filter(id=new_id).delete()
#                 if mod_type == VendorRefType.VENDOR_CLIENT:
#                     client_del = VendorClient.objects.filter(id=new_id).delete()
#                 if mod_type == VendorRefType.VENDOR_PRODUCT:
#                     product_del = SupplierProduct.objects.filter(id=new_id).delete()
#                 if mod_type == VendorRefType.VENDOR_DOCUMENT:
#                     document = VendorDocument.objects.filter(id=new_id).delete()
#                 if mod_type == VendorRefType.VENDOR_SUPPLIERTAX:
#                     try:
#                         subt_new_id = SupplierSubTax.objects.get(suppliertax_id=new_id)
#                         subt_new_id = subt_new_id.id
#                         tax = SupplierTax.objects.filter(id=new_id).delete()
#                         subtax = SupplierSubTax.objects.filter(suppliertax_id=new_id).delete()
#                     except:
#                         pass
#                 if mod_type == VendorRefType.VENDOR_PAYMENT:
#                     payment = SupplierPayment.objects.filter(id=new_id).delete()
#                 if mod_type == VendorRefType.VENDOR_ACTIVITY:
#                     activity = SupplierActivity.objects.filter(id=new_id).delete()
#                 if mod_type == VendorRefType.VENDOR_ACTIVITYDETAIL:
#                     activitydtl_del = ActivityDetail.objects.filter(id=new_id).delete()
#                 if mod_type == VendorRefType.VENDOR_CATELOG:
#                     catelog_del = Catelog.objects.filter(id=new_id).delete()
#         resp_obj = vendor_service.modification_approve_status(vendor_id,request_sts, user_id,data)
#     return HttpResponse(resp_obj.get(), content_type='application/json')

@transaction.atomic
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def unitprice(request):
    scope = request.scope
    vendor_service = VendorService(scope)
    supplier_id=request.GET.get('suplier')
    product_id=request.GET.get('product')
    resp_obj=vendor_service.get_unitprice(supplier_id,product_id)
    data = json.dumps(resp_obj)
    response = HttpResponse(data, content_type="application/json")
    return response
@transaction.atomic
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def getvendor_name(request):
    scope = request.scope
    vendor_service = VendorService(scope)
    user_id = request.user.id
    page = request.GET.get('page', 1)
    query = request.GET.get('query', None)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj=vendor_service.getvendor_name(query,vys_page,user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@transaction.atomic
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def landlord_tax(request):
    scope = request.scope
    vendor_service = VendorService(scope)
    user_id = request.user.id
    page = request.GET.get('page', 1)
    query = request.GET.get('query', None)
    vendor_id = request.GET.get('vendor_id', None)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj=vendor_service.landlord_tax(vendor_id,query,vys_page,user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@transaction.atomic
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def vendor_payment(request):
    scope = request.scope
    payment_service = paymentservice(scope)
    user_id = request.user.id
    page = request.GET.get('page', 1)
    vendor_id = request.GET.get('vendor_id', None)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = payment_service.fetch_paymentvendor(request, vys_page, user_id, vendor_id)
    bank_service = BankService(scope)
    bankbranch_service = BankBranchService(scope)
    paymode_service = PaymodeService(scope)
    branch_service = branchservice(scope)
    x = resp_obj.data
    for i in x:
        bank_id = i.bank_id
        bank = bank_service.fetch_bank(bank_id, user_id)
        i.bank_id = bank
        branch_id = i.branch_id
        branch = bankbranch_service.fetch_bankbranch(branch_id, user_id)
        i.branch_id = branch
        paymode_id = i.paymode_id
        paymode = paymode_service.fetchpaymode(paymode_id)
        i.paymode_id = paymode
        supplierbranch_id = i.supplierbranch_id
        supplierbranch = branch_service.fetch_branch(supplierbranch_id)
        i.supplierbranch_id = supplierbranch
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def product_supplier(request):
    scope = request.scope
    vendor_service = VendorService(scope)
    user_id = request.user.id
    page = request.GET.get('page', 1)
    query = request.GET.get('query', None)
    vendor_data = json.loads(request.body)
    product_id=vendor_data.get("product_id")
    dts = vendor_data.get("dts")
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = vendor_service.product_supplier(product_id, query, vys_page, user_id,dts)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def vendor_supplier_address(request):
    scope = request.scope
    vendor_service = VendorService(scope)
    user_id = request.user.id
    data=json.loads(request.body)
    type =data['type']
    addressarray = data['code']
    resp_obj = vendor_service.for_monoaddress_report(type,addressarray)
    response = HttpResponse(json.dumps(resp_obj), content_type="application/json")
    return response
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def vendor_queuefilter(request):
    user_id = request.user.id
    scope = request.scope
    emp = Employee.objects.get(user_id=user_id)
    employee_id = emp.id
    vendor_service = VendorService(scope)
    page = request.GET.get('page', 1)
    type = request.GET.get('type', None)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    status=0
    if type==1:
        status = None
    elif type == 2:
        vendor_checker = vendor_service.ischecker(request)
        if vendor_checker:
            status=3
    elif type==3:
        vendor_header = vendor_service.isheader(request)
        if vendor_header:
            status=4
    vendor_accessor_service = VendorAccessorService(scope)
    resp_obj = vendor_accessor_service.get_vendor_queuefilter(employee_id, status, vys_page)
    x = resp_obj.data
    for i in x:
        vendorstatus_get = getVendorStatus(i.vendor_status)
        i.vendor_status_name = vendorstatus_get
        vendorrequeststatus_get = getVendorRequestStatus(i.requeststatus)
        i.requeststatus_name = vendorrequeststatus_get
        vendormainstatus_get = getVendorMainStatus(i.mainstatus)
        i.mainstatus_name = vendormainstatus_get
        composite = getComposite(i.composite)
        i.composite = composite.text

        i.q_modify = False
        # if (i.created_by["id"] == user_id):
        if (i.vendor_status == 0 or i.vendor_status == 1):
             i.q_modify = True

    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@transaction.atomic
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_product(request):
    scope = request.scope
    vendor_service = VendorService(scope)
    user_id = request.user.id
    product_type_id=request.GET.get('product_type_id', None)
    query = request.GET.get('query',None)
    dts=request.GET.get('dts', None)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = vendor_service.get_product(product_type_id, dts, vys_page, user_id,query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def report(request):
    query = None
    user_id = request.user.id
    scope = request.scope
    emp = Employee.objects.get(user_id=user_id)
    body_obj=json.loads(request.body)
    employee_id = emp.id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    vendor_accessor_service = VendorAccessorService(scope)
    resp_obj = vendor_accessor_service.get_report(body_obj, employee_id, vys_page)
    x = resp_obj.data
    for i in x:
        vendorstatus_get = getVendorStatus(i.vendor_status)
        print(i, i.code)
        i.vendor_status_name = vendorstatus_get
        vendorrequeststatus_get = getVendorRequestStatus(i.requeststatus)
        i.requeststatus_name = vendorrequeststatus_get
        vendormainstatus_get = getVendorMainStatus(i.mainstatus)
        i.mainstatus_name = vendormainstatus_get
        composite = getComposite(i.composite)
        print(i.composite)
        i.composite = composite.text
        i.q_modify = False
        if (i.vendor_status == 0 or i.vendor_status == 1):
            i.q_modify = True

    data = resp_obj.get()
    datatodf = json.loads(data)
    d1 = datatodf.get('data')
    response_data = pd.DataFrame(d1)
    if len(response_data.index)>0:
        finaldf=response_data[['code','name','requeststatus_name','vendor_status_name','mainstatus_name','created_date']]
        response_data=finaldf
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="vendorreport.xlsx"'
    writer = pd.ExcelWriter(response, engine='xlsxwriter')

    response_data.to_excel(writer, index=False)
    writer.save()
    return HttpResponse(response)
###new changes in commonvendor api
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_vendor(request):
    id_obj = json.loads(request.body)
    scope = request.scope
    vendor_service = VendorService(scope)
    resp_data = vendor_service.get_vendor(id_obj)
    # obj = Vendor.objects.filter(id__in=id_obj["vendor_id"]).values('id','name','code')
    # arr = []
    # for i in obj:
    #     data = {"id": i['id'], "name": i['name'],"code":i['code']}
    #     arr.append(data)
    vendor_dic = json.dumps(resp_data, indent=4)
    return HttpResponse(vendor_dic, content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def common_search_vendor(request):
    scope = request.scope
    subject_service = VendorService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query', None)
    resp_obj = subject_service.common_search_vendor(vys_page, query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

#microtomicro New
#get Vendor
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_supplier(request,supplier_id):
    scope = request.scope
    vendor_service = VendorService(scope)
    resp_data = vendor_service.fetch_supplier(supplier_id)
    # supplier = SupplierBranch.objects.get(id=supplier_id)
    # supplier_data = {"id": supplier.id, "code": supplier.code, "name": supplier.name,"gstno":supplier.gstno,"address_id":supplier.address_id,"vendor_id":supplier.vendor_id}
    supplier_dic = json.dumps(resp_data, indent=6)
    return HttpResponse(supplier_dic, content_type='application/json')
#supplier getlist
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_supplierlist(request):
    scope = request.scope
    supplier_ids = json.loads(request.body)
    vendor_service = VendorService(scope)
    resp_data = vendor_service.fetch_supplierlist(supplier_ids)
    # supplier_id2 = supplier_ids['supplier_id']
    # obj = SupplierBranch.objects.filter(id__in=supplier_id2).values('id', 'name')
    # supplier_list_data = NWisefinList()
    # for i in obj:
    #     data = {"id": i['id'], "name": i['name']}
    #     supplier_list_data.append(data)
    return HttpResponse(resp_data.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_dept_rm(request):
    user_service = Vendor_user_service(request.scope)
    employee_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query', None)
    response_data = user_service.get_employee_with_dept(employee_id, query, vys_page)
    response = HttpResponse(response_data.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_vendor_by_code(request):
    if request.method == 'GET':
        code = request.GET.get('code', None)
        employee_id = request.employee_id
        scope = request.scope
        vendor_service = VendorService(scope)
        resp_obj = vendor_service.fetch_vendor_code(code, employee_id)
        address_service = VendorAddressService(scope)
        contact_service = VendorContactService(scope)
        director_service = DirectorService(scope)
        profile_service = ProfileService(scope)
        state_service = StateService(scope)
        city_service = CityService(scope)
        district_service = DistrictService(scope)
        pincode_service = PincodeService(scope)
        customercategory_service = CustomerCategoryService(scope)
        vendor_id = resp_obj.id
        address = address_service.vow_fetch_vendoraddress(vendor_id, employee_id)
        resp_obj.address = address
        contact = contact_service.vow_fetch_vendorcontact(vendor_id, employee_id)
        resp_obj.contact = contact
        profile = profile_service.vow_fetch_profile(vendor_id, employee_id)
        resp_obj.profile = profile
        director = director_service.vow_fetch_director(vendor_id, employee_id)
        resp_obj.director = director
        city_id = resp_obj.address.city_id
        city = city_service.fetch_city(city_id, employee_id)
        resp_obj.address.city_id = city
        state_id = resp_obj.address.state_id
        state = state_service.fetchstate(state_id)
        resp_obj.address.state_id = state
        district_id = resp_obj.address.district_id
        district = district_service.fetchdistrict(district_id)
        resp_obj.address.district_id = district
        pincode_id = resp_obj.address.pincode_id
        pincode = pincode_service.fetch_pincode(pincode_id, employee_id)
        resp_obj.address.pincode_id = pincode
        orgtype_id = resp_obj.orgtype
        orgtype = getOrgType(orgtype_id)
        resp_obj.orgtype = orgtype
        classification_id = resp_obj.classification
        classification = getClassification(classification_id)
        resp_obj.classification = classification
        group_id = resp_obj.group
        group = getGroup(group_id)
        resp_obj.group = group
        composite_id = resp_obj.composite
        composite = getComposite(composite_id)
        resp_obj.composite = composite
        type_id = resp_obj.type
        type = getType(type_id)
        resp_obj.type = type
        employee_service = EmployeeService(scope)
        rm_id = resp_obj.rm_id
        rmname = employee_service.get_employee(rm_id, employee_id)
        resp_obj.rm_id = rmname
        custcategory_id = resp_obj.custcategory_id
        custcategory = customercategory_service.fetch_customercategory(custcategory_id, employee_id)
        resp_obj.custcategory_id = custcategory
        resp_obj.user_id = employee_id
        vendor_status = resp_obj.vendor_status
        vendorstatus_get = getVendorStatus(vendor_status)
        resp_obj.vendor_status_name = vendorstatus_get
        vendormainstatus_get = getVendorMainStatus(resp_obj.mainstatus)
        resp_obj.mainstatus_name = vendormainstatus_get
        vendorrequeststatus_get = getVendorRequestStatus(resp_obj.requeststatus)
        resp_obj.requeststatus_name = vendorrequeststatus_get
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_contact_details(request):
    scope = request.scope
    query = request.GET.get('query', None)
    type = request.GET.get('type', 2)
    type = int(type)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    ven_serv = VendorService(scope)
    resp_data = ven_serv.get_contact_details(query, type, vys_page)
    response = HttpResponse(resp_data.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def approve_vendor(request):
    scope = request.scope
    data = json.loads(request.body)
    vow_serv = VOWService(scope)
    resp_data = vow_serv.insert_approved_vendor(data)
    response = HttpResponse(resp_data.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def portal_flag_update(request,vendor_id):
    if request.method == 'POST':
        scope = request.scope
        vendor_data = json.loads(request.body)
        vendor_obj = VendorRequest(vendor_data)
        vendor_servi = VendorService(scope)
        resp_obj = vendor_servi.portal_flag_update(vendor_id, vendor_obj)
        # resp = {'code': 'worked', 'message': 'successfully completed'}
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response