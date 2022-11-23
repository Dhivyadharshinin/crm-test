from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
import json
from django.http import HttpResponse
from utilityservice.data.response.nwisefinpage import NWisefinPage
from masterservice.service.apexpensegroupservice import ExpenseGroupservice
from masterservice.data.request.apexpensegrprequest import ApExpenseGrouprequest
from userservice.service.employeeservice import EmployeeService


# expensegroup
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ApExpenseGroup(request):
    if request.method == 'POST':
        scope = request.scope
        expensegrpservice = ExpenseGroupservice(scope)
        expensegrp_obj = json.loads(request.body)
        expensegrp_obj = ApExpenseGrouprequest(expensegrp_obj)
        user_id = request.employee_id
        emp_service = EmployeeService(scope)
        empid = emp_service.get_empid_from_userid(user_id)
        resp_obj = expensegrpservice.create_expensegrp(expensegrp_obj, empid)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    else:
        resp=expensegrp_search(request)
        return resp
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def apexpense_activate_inactivate(request):
    if request.method == 'POST':
        scope=request.scope
        apexp_service = ExpenseGroupservice(scope)
        apsector_obj = json.loads(request.body)
        ap_obj = ApExpenseGrouprequest(apsector_obj)
        resp_obj = apexp_service.apexpense_activate_inactivate(request,ap_obj)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
def expensegrp_search(request):
    user_id = request.employee_id
    query = request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    scope = request.scope
    expensegrp_service = ExpenseGroupservice(scope)
    response_data = expensegrp_service.fetch_expensegrp_search_list(query, vys_page)
    response = HttpResponse(response_data.get(), content_type="application/json")
    return response
