import json
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from nwisefin.settings import logger
from userservice.service.employeeservice import EmployeeService
from vendorservice.models import SupplierActivity, ActivityDetail
from django.http import HttpResponse
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from django.views.decorators.csrf import csrf_exempt
from vendorservice.service.activityservice import  ActivityService
from vendorservice.service.supplierservice import ContactService
from vendorservice.data.request.activityrequest import ActivityRequest
from vendorservice.data.request.supplierrequest import ContactRequest
from masterservice.service.designationservice import DesignationService
from masterservice.service.contacttypeservice import ContactTypeService
from vendorservice.service.branchservice import branchservice
from vendorservice.service.vendorservice import VendorService
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from vendorservice.util.vendormandatory import VendorMandatory


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def activity(request,branch_id):
    if request.method == 'POST':
        scope = request.scope
        activity_service = ActivityService(scope)
        contact_service = ContactService(scope)
        activity_data = json.loads(request.body)
        emp_id = request.employee_id

        contact = activity_data.get("contact")
        contact_obj = ContactRequest(contact)
        activity_obj = ActivityRequest(activity_data)
        vendor_mand = VendorMandatory()
        activity_validate = vendor_mand.activity(activity_obj)
        contact_validate = vendor_mand.contact(contact_obj)
        if activity_validate['checker'] == False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(activity_validate['response'])
            return HttpResponse(error_obj.get(), content_type="application/json")
        elif contact_validate['checker'] == False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(contact_validate['response'])
            return HttpResponse(error_obj.get(), content_type="application/json")

        if activity_obj.id != None :
            contact_id = activity_service.get_contact_id(activity_obj.id)
            contact_obj.id = contact_id

        vendor_service = VendorService(scope)
        vendor_id = activity_service.get_vendor_id(branch_id)
        mod_status = vendor_service.get_modification_status(vendor_id)
        if mod_status is True:
            contact_id = contact_service.modification_create_contact(contact_obj, emp_id,vendor_id)
            resp_obj = activity_service.modification_create_activity(activity_obj,contact_id, emp_id,branch_id,vendor_id)
        else:
            contact_id = contact_service.create_contact(contact_obj, emp_id,vendor_id)
            resp_obj = activity_service.create_activity(activity_obj,contact_id, emp_id,branch_id,vendor_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_activity_list(request,branch_id)


def fetch_activity_list(request,branch_id):
    scope = request.scope
    activity_service = ActivityService(scope)
    emp_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = activity_service.fetch_activity_list(request, vys_page,emp_id,branch_id)

    contact_service = ContactService(scope)
    branch_service = branchservice(scope)
    x = resp_obj.data
    for i in x:
        cont_id = i.contact_id
        contact = contact_service.fetch_contact(cont_id, emp_id)
        i.contact_id = contact

        supplierbranch_id = i.branch
        vendor_status = branch_service.get_vendorstatus_branch(supplierbranch_id)
        i.q_modify = False
        if (i.created_by == emp_id):
            if (vendor_status == 0 or vendor_status == 1):
                i.q_modify = True

    #modification
        # i.q_modify = True

    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_activity(request,activity_id,branch_id):
    if request.method == 'GET':
        scope = request.scope
        activity_service = ActivityService(scope)
        employee_id = request.employee_id
        contact_service = ContactService(scope)
        contacttype_service = ContactTypeService(scope)
        # designation_service = DesignationService(scope)

        resp_obj = activity_service.fetch_activity(activity_id)
        cont_id = resp_obj.contact_id
        contact = contact_service.fetch_contact(cont_id, employee_id)
        resp_obj.contact_id = contact


        # designation_id = resp_obj.contact_id.designation_id
        # designation = designation_service.fetch_designation(designation_id)
        # resp_obj.contact_id.designation_id = designation

        branch_service = branchservice(scope)
        supplierbranch_id = resp_obj.branch
        vendor_status = branch_service.get_vendorstatus_branch(supplierbranch_id)
        resp_obj.q_modify = False
        if (resp_obj.created_by == employee_id):
            if (vendor_status == 0 or vendor_status == 1):
                resp_obj.q_modify = True

        # modification
        resp_obj.q_modify = True

        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_activity(request,activity_id,branch_id)



def delete_activity(request,activity_id,branch_id):
    scope = request.scope
    activity_service = ActivityService(scope)
    user_id = request.employee_id
    del_activity = activity_service.delete_activity_using_id(activity_id, branch_id, user_id)

    # activity_detail = ActivityDetail.objects.filter(activity_id=activity_id)
    # activity_detail_len = len(activity_detail)
    # logger.info(activity_detail_len)
    # if activity_detail_len ==0:
    #     scope = request.scope
    #     activity_service = ActivityService(scope)
    #     vendor_service = VendorService(scope)
    #     vendor_id = activity_service.get_vendor_id(branch_id)
    #     mod_status = vendor_service.get_modification_status(vendor_id)
    #     user_id = request.user.id
    #     emp_service = EmployeeService()
    #     employee_id = emp_service.get_empid_from_userid(user_id)
    #
    #     if mod_status is True:
    #         resp_obj = activity_service.modification_delete_activity(activity_id,vendor_id,employee_id,branch_id)
    #     else:
    #         resp_obj = activity_service.delete_activity(activity_id, vendor_id, employee_id,branch_id)
    #     response = HttpResponse(resp_obj.get(), content_type="application/json")
    # else:
    #     error_obj = NWisefinError()
    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ACTIVITYID_ERROR)
    #     error_obj.set_description(ErrorDescription.UNEXPECTED_ACTIVITYID_ERROR)
    #     response = HttpResponse(error_obj.get(), content_type="application/json")
    return HttpResponse(del_activity.get(), content_type="application/json")


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def activity_list(request,branch_id):
    scope = request.scope
    activity_service = ActivityService(scope)
    emp_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = activity_service.activity_list(request, vys_page,emp_id,branch_id)

    contact_service = ContactService(scope)
    branch_service = branchservice(scope)
    x = resp_obj.data
    for i in x:
        cont_id = i.contact_id
        contact = contact_service.fetch_contact(cont_id, emp_id)
        i.contact_id = contact

        supplierbranch_id = i.branch
        vendor_status = branch_service.get_vendorstatus_branch(supplierbranch_id)
        i.q_modify = False
        if (i.created_by == emp_id):
            if (vendor_status == 0 or vendor_status == 1):
                i.q_modify = True

    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
