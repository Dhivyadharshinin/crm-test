import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from vendorservice.data.request.activitydetailsrequest import ActivityDetailsRequest
from vendorservice.models import Catelog
from vendorservice.service.activitydetailsservice import ActivityDetailsService
from vendorservice.service.activityservice import ActivityService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from userservice.service.employeeservice import EmployeeService
from vendorservice.service.vendorservice import VendorService
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from vendorservice.util.vendormandatory import VendorMandatory


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_activity_search(request):
    scope = request.scope
    activity_service = ActivityDetailsService(scope)
    query = request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = activity_service.fetch_activity_search(query,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
#vendor_id
def supplieractivitydtl(request,activity_id):
    user_id = request.employee_id
    scope = request.scope
    if request.method == 'POST':
        activitydtl_service = ActivityDetailsService(scope)
        activitydtl_obj = json.loads(request.body)
        activitydtl_obj=ActivityDetailsRequest(activitydtl_obj)
        vendor_service = VendorService(scope)
        vendor_mand = VendorMandatory()
        validate = vendor_mand.activity_detail(activitydtl_obj)
        if validate['checker'] == False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(validate['response'])
            return HttpResponse(error_obj.get(), content_type="application/json")
        vendor_id = activitydtl_service.get_vendor_id(activity_id)
        mod_status = vendor_service.get_modification_status(vendor_id)
        if mod_status is True:
            resp_obj = activitydtl_service.modification_create_activitydtl(activity_id, activitydtl_obj, user_id,vendor_id)
        else:
            resp_obj = activitydtl_service.create_activitydtl(activity_id, activitydtl_obj, user_id, vendor_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_activitydtl_list(request,activity_id)


def fetch_activitydtl_list(request, activity_id):
    user_id = request.employee_id
    scope = request.scope
    emp_service = EmployeeService(scope)
    scope = request.scope
    activitydtl_service = ActivityDetailsService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = activitydtl_service.fetch_activitydtl_list(request, vys_page,user_id,activity_id)

    activity_service = ActivityService(scope)
    x = resp_obj.data
    for i in x:
        activity_id = i.activity_id
        activity = activity_service.fetch_activity(activity_id)
        i.activity_id = activity

        raisor_id = i.raisor
        raisor = emp_service.get_employee(raisor_id, user_id)
        i.raisor = raisor
        approver_id = i.approver
        approver = emp_service.get_employee(approver_id, user_id)
        i.approver = approver

        vendor_status = activity_service.get_vendorstatus_activity(activity_id)
        i.q_modify = False
        if (i.created_by == user_id):
            if (vendor_status == 0 or vendor_status == 1):
                i.q_modify = True

    # modification
    #     i.q_modify = True

    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_activitydtl(request,activity_id,id):
    if request.method == 'GET':
        user_id = request.employee_id
        scope = request.scope
        emp_service = EmployeeService(scope)
        activitydtl_service = ActivityDetailsService(scope)
        resp_obj = activitydtl_service.fetch_activitydtl(id)

        activity_service = ActivityService(scope)
        activity_id = resp_obj.activity_id
        activity = activity_service.fetch_activity(activity_id)
        resp_obj.activity_id = activity
        raisor_id = resp_obj.raisor
        raisor = emp_service.get_employee(raisor_id, user_id)
        resp_obj.raisor = raisor

        approver_id = resp_obj.approver
        approver = emp_service.get_employee(approver_id, user_id)
        resp_obj.approver = approver

        vendor_status = activity_service.get_vendorstatus_activity(activity_id)
        resp_obj.q_modify = False
        if (resp_obj.created_by == user_id):
            if (vendor_status == 0 or vendor_status == 1):
                resp_obj.q_modify = True
        # modification
        # resp_obj.q_modify = True

        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_activitydtl(request,activity_id,id)


def delete_activitydtl(request,activity_id,id):
    scope = request.scope
    activity_detail_service = ActivityDetailsService(scope)
    user_id = request.employee_id
    del_activity = activity_detail_service.delete_condition(activity_id, id, user_id)
    # catlog_id = Catelog.objects.filter(activitydetail_id=id)
    # catlog_len = len(catlog_id)
    # if catlog_len == 0:
    #     user_id = request.user.id
    #     emp_service = EmployeeService()
    #     employee_id = emp_service.get_empid_from_userid(user_id)
    #     scope = request.scope
    #     activitydtl_service = ActivityDetailsService(scope)
    #     vendor_service = VendorService(scope)
    #     vendor_id = activitydtl_service.get_vendor_id(activity_id)
    #     mod_status = vendor_service.get_modification_status(vendor_id)
    #
    #     if mod_status is True:
    #         resp_obj = activitydtl_service.modification_delete_activitydtl(id,vendor_id,employee_id,activity_id)
    #     else:
    #         resp_obj = activitydtl_service.delete_activitydtl(employee_id,id,vendor_id,activity_id)
    #     response = HttpResponse(resp_obj.get(), content_type="application/json")
    #     return response
    #
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
def activitydtl_list(request, activity_id):
    user_id = request.employee_id
    scope = request.scope
    emp_service = EmployeeService(scope)
    scope = request.scope
    activitydtl_service = ActivityDetailsService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = activitydtl_service.activitydtl_list(request, vys_page,user_id,activity_id)

    activity_service = ActivityService(scope)
    x = resp_obj.data
    for i in x:
        activity_id = i.activity_id
        activity = activity_service.fetch_activity(activity_id)
        i.activity_id = activity

        raisor_id = i.raisor
        raisor = emp_service.get_employee(raisor_id, user_id)
        i.raisor = raisor
        approver_id = i.approver
        approver = emp_service.get_employee(approver_id, user_id)
        i.approver = approver

        vendor_status = activity_service.get_vendorstatus_activity(activity_id)
        i.q_modify = False
        if (i.created_by == user_id):
            if (vendor_status == 0 or vendor_status == 1):
                i.q_modify = True

    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

