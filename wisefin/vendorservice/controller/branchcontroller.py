import json
from django.db.models import Q
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from userservice.service.employeeservice import EmployeeService
from vendorservice.data.request.supplierrequest import Gstrequest
from vendorservice.data.request.supplierrequest import BranchRequest
from vendorservice.service.branchservice import branchservice
from vendorservice.service.profileservice import ProfileService
from vendorservice.service.supplierservice import AddressService , ContactService
from vendorservice.data.request.supplierrequest import ContactRequest,AddressRequest
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from nwisefin.settings import logger
from masterservice.service.cityservice import CityService
from masterservice.service.stateservice import StateService
from masterservice.service.districtservice import DistrictService
from masterservice.service.pincodeservice import PincodeService
from masterservice.service.designationservice import DesignationService
from masterservice.service.contacttypeservice import ContactTypeService
from vendorservice.controller.vendorcontroller import VendorService
from vendorservice.util.vendormandatory import VendorMandatory
from vendorservice.models import Vendor, SupplierBranch
from django.db import transaction
# supplier branch - create , insert , update , delete


@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def branch(request,vendor_id):
    if request.method == 'POST':
        scope = request.scope
        branch_service = branchservice(scope)
        contact_service = ContactService(scope)
        address_service = AddressService(scope)
        branch_data = json.loads(request.body)
        branch_obj = BranchRequest(branch_data)
        vendor_mand = VendorMandatory()
        branch_validate = vendor_mand.branch(branch_obj)
        gst_flag = branch_service.check_state_gst(branch_data)
        if gst_flag == False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.GST_STATE)
            error_obj.set_description(ErrorDescription.GST_STATE)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return HttpResponse(response, content_type='application/json')
        if branch_validate['checker'] == False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(branch_validate['response'])
            return HttpResponse(error_obj.get(), content_type="application/json")
        vendor_id=int(vendor_id)
        employee_id = request.employee_id
        regcom = branch_service.get_barnch_composite(vendor_id)
        # branchcom=Vendor.objects.get(id=vendor_id)
        # regcom=branchcom.composite
        if (regcom==2 and (branch_obj.get_gstno()=='' or branch_obj.get_gstno()==None)):
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.GET_DATA)
            error_obj.set_description(ErrorDescription.GET_DATA)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return HttpResponse(response, content_type='application/json')
        #logger.info(branch_check_final)

        contact = branch_data.get("contact")
        contact_obj = ContactRequest(contact)
        address = branch_data.get("address")
        address_obj = AddressRequest(address)
        address_validate = vendor_mand.address(address_obj)
        contact_validate = vendor_mand.contact(contact_obj)
        if address_validate['checker'] == False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(address_validate['response'])
            return HttpResponse(error_obj.get(), content_type="application/json")
        elif contact_validate['checker'] == False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(contact_validate['response'])
            return HttpResponse(error_obj.get(), content_type="application/json")
        if branch_obj.id != None :
            cont_add_id = branch_service.get_contact_address_id(branch_obj.id)
            contact_obj.id = cont_add_id.contact_id
            address_obj.id = cont_add_id.address_id
        vendor_service = VendorService(scope)
        mod_status = vendor_service.get_modification_status(vendor_id)
        if mod_status is True:
            branch_check_id = branch_data.get('id')
            if not branch_check_id is None:
                branch_check_final = True
            else:
                branch_check = branch_service.branch_count_flag(vendor_id)
                if branch_check:
                    branch_check_final = True
                else:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_BRANCH_ERROR)
                    error_obj.set_description(ErrorDescription.UNEXPECTED_BRANCH_ERROR)
                    response = HttpResponse(error_obj.get(), content_type="application/json")
                    return response
            logger.info(str(branch_check_final))
            if branch_check_final:
                cont_id = contact_service.modification_create_contact(contact_obj, employee_id,vendor_id)
                add_id = address_service.modification_create_address(address_obj, employee_id,vendor_id)
                resp_obj = branch_service.modification_create_branch(branch_obj, employee_id, vendor_id,add_id,cont_id)
                response = HttpResponse(resp_obj.get(), content_type="application/json")
                return response
        else:

            branch_check_id = branch_data.get('id')
            if not branch_check_id is None:
                branch_check_final = True
            else:
                branch_check = branch_service.branch_count_check(vendor_id)
                if branch_check:
                    branch_check_final = True
                else:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_BRANCH_ERROR)
                    error_obj.set_description(ErrorDescription.UNEXPECTED_BRANCH_ERROR)
                    response = HttpResponse(error_obj.get(), content_type="application/json")
                    return response
            if  branch_check_final:
                cont_id=contact_service.create_contact(contact_obj, employee_id,vendor_id)
                add_id=address_service.create_address(address_obj, employee_id,vendor_id)
                resp_obj = branch_service.create_branch(branch_obj,employee_id,vendor_id,add_id,cont_id,address_obj)
                if resp_obj == 'NOTVALID_GST':
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.NOTVALID_GST)
                    error_obj.set_description(ErrorDescription.NOTVALID_GST)
                    response = HttpResponse(error_obj.get(), content_type="application/json")
                    return response
                if resp_obj == "GSTEXSIST":
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.GSTEXSIST)
                    error_obj.set_description(ErrorDescription.GSTEXSIST)
                    response = HttpResponse(error_obj.get(), content_type="application/json")
                    return response
                response = HttpResponse(resp_obj.get(), content_type="application/json")
                return response
    elif request.method == 'GET':
        return fetch_branch_list(request,vendor_id)


def fetch_branch_list(request,vendor_id):
    scope = request.scope
    branch_service = branchservice(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    employee_id = request.employee_id
    resp_obj = branch_service.fetch_branch_list(request, vys_page, employee_id,vendor_id)
    #monesh
    address_service = AddressService(scope)
    contact_service = ContactService(scope)
    vendor_service = VendorService(scope)
    x = resp_obj.data
    for i in x:
        add_id = i.address_id
        address=address_service.fetch_address(add_id, employee_id)
        i.address_id = address
        cont_id = i.contact_id
        contact = contact_service.fetch_contact(cont_id, employee_id)
        i.contact_id = contact
        vendor_id = i.vendor_id
        vendor_status =vendor_service.get_vendor_status(vendor_id)
        i.q_modify = False
        if (i.created_by == employee_id):
            if (vendor_status == 0 or vendor_status == 1):
                i.q_modify = True
    #modificaton
        # i.q_modify = True
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@csrf_exempt
def delete_branch(request,vendor_id,branch_id):
    scope = request.scope
    branch_service = branchservice(scope)
    employee_id = request.employee_id
    vendor_service = VendorService(scope)
    mod_status = vendor_service.get_modification_status(vendor_id)
    if mod_status is True:
        resp_obj = branch_service.modification_delete_branch(branch_id,vendor_id,employee_id)
    else:
        resp_obj = branch_service.delete_branch(branch_id,vendor_id,employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_branch(request,vendor_id, branch_id):
    if request.method == 'GET':
        scope = request.scope
        branch_service = branchservice(scope)
        contact_service = ContactService(scope)
        address_service = AddressService(scope)
        state_service = StateService(scope)
        city_service = CityService(scope)
        district_service = DistrictService(scope)
        pincode_service = PincodeService(scope)
        contacttype_service = ContactTypeService(scope)
        # designation_service = DesignationService(scope)
        employee_id = request.employee_id
        resp_obj = branch_service.fetch_branch(branch_id)
        cont_id = resp_obj.contact_id
        contact = contact_service.fetch_contact(cont_id, employee_id)
        resp_obj.contact_id = contact
        add_id = resp_obj.address_id
        address = address_service.fetch_address(add_id, employee_id)
        resp_obj.address_id = address
        city_id = resp_obj.address_id.city_id
        city = city_service.fetch_city(city_id, employee_id)
        resp_obj.address_id.city_id = city
        state_id = resp_obj.address_id.state_id
        state = state_service.fetchstate(state_id)
        resp_obj.address_id.state_id = state
        district_id = resp_obj.address_id.district_id
        district = district_service.fetchdistrict(district_id)
        resp_obj.address_id.district_id = district
        pincode_id = resp_obj.address_id.pincode_id
        pincode = pincode_service.fetch_pincode(pincode_id, employee_id)
        resp_obj.address_id.pincode_id = pincode
        # contact

        # designation_id = resp_obj.contact_id.designation_id
        # designation = designation_service.fetch_designation(designation_id)
        # resp_obj.contact_id.designation_id = designation
        vendor_service = VendorService(scope)
        vendor_id = resp_obj.vendor_id
        vendor_status = vendor_service.get_vendor_status(vendor_id)
        resp_obj.q_modify = False
        if (resp_obj.created_by == employee_id):
            if (vendor_status == 0 or vendor_status == 1):
                resp_obj.q_modify = True
        # for modification testing
        # resp_obj.q_modify = True
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_branch(request,vendor_id,branch_id)

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def pendingbranch(request,vendor_id):
    if request.method == 'GET':
        scope = request.scope
        branch_service = branchservice(scope)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        employee_id = request.employee_id
        resp_obj = branch_service.pendingbranch_list(request, vys_page, employee_id, vendor_id)

        address_service = AddressService(scope)
        contact_service = ContactService(scope)
        vendor_service = VendorService(scope)
        x = resp_obj.data
        for i in x:
            add_id = i.address_id
            address = address_service.fetch_address(add_id, employee_id)
            i.address_id = address
            cont_id = i.contact_id
            contact = contact_service.fetch_contact(cont_id, employee_id)
            i.contact_id = contact
            vendor_id = i.vendor_id
            vendor_status = vendor_service.get_vendor_status(vendor_id)
            i.q_modify = False
            if (i.created_by == employee_id):
                if (vendor_status == 0 or vendor_status == 1):
                    i.q_modify = True
        # modificaton
        # i.q_modify = True
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def landlordbranch_list(request):
    if request.method == 'GET':
        scope = request.scope
        branch_service = branchservice(scope)
        query = request.GET.get('query', None)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        employee_id = request.employee_id
        resp_obj = branch_service.landlordbranch_list(vys_page,employee_id,query)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])

def gstnumbercontroller(request,vendor_id):
    if request.method == 'POST':
        scope = request.scope
        branch_service = branchservice(scope)
        branch_data = json.loads(request.body)
        branch_obj = Gstrequest(branch_data)
        vendor_id = int(vendor_id)
        resp=branch_service.get_check(branch_obj,vendor_id)


        if resp == 'VALID_GST':
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.VALID_GST)
            error_obj.set_description(ErrorDescription.VALID_GST)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response
        elif resp == 'NOTVALID_GST':
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.NOTVALID_GST)
            error_obj.set_description(ErrorDescription.NOTVALID_GST)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response
# @csrf_exempt
# @api_view(['POST'])
# @authentication_classes([VysfinAuthentication])
# @permission_classes([IsAuthenticated, VysfinPermission])
#
# def brachactive(request):
#     if request.method == 'POST':
#         vendor_service = VendorService()
#         branch_service = branchservice()
#         user_id = request.user.id
#         emp_service = EmployeeService()
#         employee_id = emp_service.get_empid_from_userid(user_id)
#         branch_data = json.loads(request.body)
#         vendor_id = int(branch_data['vendor_id'])
#         mod_status = vendor_service.get_modification_status(vendor_id)
#         resp=branch_service.updatebranch(branch_data,employee_id,mod_status)
#         return 1

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def product_dts(request):
    if request.method == 'GET':
        scope = request.scope
        branch_service = branchservice(scope)
        product_id = request.GET.get('product_id', None)
        dts = request.GET.get('dts', 0)
        query = request.GET.get('query', None)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        employee_id = request.employee_id
        resp_obj = branch_service.fetch_productdts(product_id,dts,vys_page,employee_id,query)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def catalog_supplier(request):
    if request.method == 'GET':
        scope = request.scope
        catalog_service = branchservice(scope)
        product_id = request.GET.get('product_id', None)
        dts = request.GET.get('dts', 0)
        catalog = request.GET.get('catalog', None)
        query = request.GET.get('query', None)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        employee_id = request.employee_id
        resp_obj = catalog_service.fetch_product_catalog(product_id, dts,catalog, vys_page, employee_id, query)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def catalogproduct_supplier(request):
    if request.method == 'POST':
        scope = request.scope
        catalog_service = branchservice(scope)
        body_data = json.loads(request.body)
        product_id = body_data['product']
        dts = body_data['dts']
        catalog = body_data['catalog']
        query = request.GET.get('query', None)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        employee_id = request.employee_id
        resp_obj = catalog_service.fetch_catalogproduct_supplier(product_id, dts,catalog, vys_page, employee_id, query)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_suppliername(request):
    scope = request.scope
    branch_service = branchservice(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    name = request.GET.get('name')
    sup_id = request.GET.get('sup_id')
    query = {"name": name, "sup_id": sup_id}
    resp_obj = branch_service.search_suppliername(vys_page,query)
    return HttpResponse(resp_obj.get(), content_type='application/json')

# prpo-micro to micro
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def supplierbranch_get(request):
    supplierbranch_data = json.loads(request.body)
    scope=request.scope
    branch_service = branchservice(scope)
    resp_data = branch_service.supplierbranch_get(supplierbranch_data)
    # supplierbranchId_arr = supplierbranch_data['supplierbranch_id']
    # supplierbranch = SupplierBranch.objects.filter(id__in = supplierbranchId_arr).values('id', 'code',
    #                                                                                      'name', 'gstno',
    #                                                                                      'address_id', 'vendor_id')
    # supplierbranch_list_data = NWisefinList()
    # for i in supplierbranch:
    #     data = {"id": i['id'],
    #             "code":i['code'],
    #             "name":i['name'],
    #             "gstno":i['gstno'],
    #             "address_id":i['address_id'],
    #             "vendor_id":i['vendor_id'],
    #             "fullname": i['code'] + "--" + i['name']}
    #     supplierbranch_list_data.append(data)
    return HttpResponse(resp_data.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_supplierbranchdata(request, supplierbranch_id):
    scope = request.scope
    branch_service = branchservice(scope)
    resp_data = branch_service.fetch_supplierbranchdata(supplierbranch_id)
    # supplierbranch = SupplierBranch.objects.get(id=supplierbranch_id)
    # supplierbranch_data = {"id": supplierbranch.id,
    #                        "code": supplierbranch.code,
    #                        "name": supplierbranch.name,
    #                        "gstno": supplierbranch.gstno,
    #                        "address_id": supplierbranch.address_id,
    #                        "vendor_id": supplierbranch.vendor_id,
    #                        "fullname": supplierbranch.code + "--" + supplierbranch.name}
    supplierbranch_dic = json.dumps(resp_data, indent=4)
    return HttpResponse(supplierbranch_dic, content_type='application/json')

#supplierbranch_name search
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_supplierbranch(request, supplierbranch_name):
    scope = request.scope()
    branch_service = branchservice(scope)
    supplier_branch = branch_service.search_supplier_branch(supplierbranch_name)
    # condition1 = (Q(name__icontains=supplierbranch_name) | Q(code__icontains=supplierbranch_name)) & Q(status=1)
    # supplierbranch = SupplierBranch.objects.filter(condition1).values('id', 'code', 'name')
    # emp_list_data = NWisefinList()
    # for i in supplierbranch:
    #     data = {"id": i['id'], "code": i['code'], "name": i['name'],
    #             "fullname": i['code'] + "--" + i['name']}
    #     emp_list_data.append(data)
    return HttpResponse(supplier_branch.get(), content_type='application/json')

#
# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def supplierbranch(request,sup_id):
#     page = request.GET.get('page', 1)
#     page = int(page)
#     vys_page = NWisefinPage(page, 10)
#     scope = request.scope
#     branch_service = branchservice(scope)
#     user_id = request.user.id
#     emp_service = EmployeeService()
#     emp_id = emp_service.get_empid_from_userid(user_id)
#     resp_obj = branch_service.supplierbranch(vys_page, sup_id, emp_id)
#     return HttpResponse(resp_obj.get(), content_type='application/json')

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def supplierbranch(request,sup_id):
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    scope = request.scope
    branch_service = branchservice(scope)
    emp_id = request.employee_id
    resp_obj = branch_service.supplierbranch(vys_page, sup_id, emp_id)
    return HttpResponse(resp_obj.get(), content_type='application/json')

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_supplier(request):
    panno = request.GET.get('panno')
    gstno = request.GET.get('gstno')
    code = request.GET.get('code')
    query = {"panno": panno, "gstno": gstno, "code": code}
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    emp_id = request.employee_id
    scope = request.scope
    branch_service = branchservice(scope)
    response_obj = branch_service.search_supplier_list(query, vys_page, emp_id)
    response = HttpResponse(response_obj.get(), content_type='application/json')
    return response
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_supplier_name(request):
    query = request.GET.get('name')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    emp_id = request.employee_id
    scope = request.scope
    branch_service = branchservice(scope)
    response_obj = branch_service.search_supplier_list_name(query, vys_page, emp_id)
    response = HttpResponse(response_obj.get(), content_type='application/json')
    return response

@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
@csrf_exempt
def supplieractive(request):
    if request.method == 'POST':
        scope = request.scope
        branch_service = branchservice (scope)
        contact_service = ContactService(scope)
        address_service = AddressService(scope)
        branch_data = json.loads(request.body)

        branch_obj = BranchRequest ( branch_data )

        employee_id = request.employee_id
        vendor_service = VendorService(scope)

        mod_status = vendor_service.get_modification_status(branch_data['vendor_id'])
        if mod_status:
            contact = branch_data.get ( "contact_id" )
            contact_obj = ContactRequest ( contact )
            address = branch_data.get ( "address_id" )
            address_obj = AddressRequest ( address )
            if branch_obj.id != None :
                cont_add_id = branch_service.get_contact_address_id ( branch_obj.id )
                contact_obj.id = cont_add_id.contact_id
                address_obj.id = cont_add_id.id
            branch_check_id = branch_data.get('id')
            if not branch_check_id is None:
                branch_check_final = True
            else:
                branch_check = branch_service.branch_count_flag(branch_data['vendor_id'])
                if branch_check:
                    branch_check_final = True
                else:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_BRANCH_ERROR)
                    error_obj.set_description(ErrorDescription.UNEXPECTED_BRANCH_ERROR)
                    response = HttpResponse(error_obj.get(), content_type="application/json")
                    return response
            logger.info(str(branch_check_final))
            if branch_check_final:
                cont_id = contact_service.modification_create_contact(contact_obj, employee_id,branch_data['vendor_id'])
                add_id = address_service.modification_create_address(address_obj, employee_id,branch_data['vendor_id'])
            resp_obj = branch_service.branchactivemodification(branch_obj,employee_id,branch_data['vendor_id'],cont_id,add_id)
        else:
            resp_obj = branch_service.branchactive(branch_obj,employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def branch_count(request, vendor_id):
    scope = request.scope
    print(vendor_id)
    branch_service = branchservice(scope)
    count_flag = branch_service.branch_count_flag(vendor_id)
    response = HttpResponse(count_flag.get(), content_type='application/json')
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_suppliername_dropdown(request):
    scope = request.scope
    branch_service = branchservice(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query')
    resp_obj = branch_service.search_suppliername_dropdown(vys_page,query)
    return HttpResponse(resp_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_branch_by_code(request):
    if request.method == 'GET':
        scope = request.scope
        code = request.GET.get('code', None)
        branch_service = branchservice(scope)
        contact_service = ContactService(scope)
        address_service = AddressService(scope)
        state_service = StateService(scope)
        city_service = CityService(scope)
        district_service = DistrictService(scope)
        pincode_service = PincodeService(scope)
        employee_id = request.employee_id
        resp_obj = branch_service.fetch_branch_by_code(code)
        cont_id = resp_obj.contact_id
        contact = contact_service.fetch_contact(cont_id, employee_id)
        resp_obj.contact_id = contact
        add_id = resp_obj.address_id
        address = address_service.fetch_address(add_id, employee_id)
        resp_obj.address_id = address
        city_id = resp_obj.address_id.city_id
        city = city_service.fetch_city(city_id, employee_id)
        resp_obj.address_id.city_id = city
        state_id = resp_obj.address_id.state_id
        state = state_service.fetchstate(state_id)
        resp_obj.address_id.state_id = state
        district_id = resp_obj.address_id.district_id
        district = district_service.fetchdistrict(district_id)
        resp_obj.address_id.district_id = district
        pincode_id = resp_obj.address_id.pincode_id
        pincode = pincode_service.fetch_pincode(pincode_id, employee_id)
        resp_obj.address_id.pincode_id = pincode
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
