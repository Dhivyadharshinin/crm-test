from django.http import HttpResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from userservice.service.employeeservice import EmployeeService
from vendorservice.service.vendorhistoryservice import VendorHistoryService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from userservice.models import Employee


@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_vendor_history(request, vendor_id):
    # emp = Employee.objects.get(user_id=user_id)
    # employee_id = emp.id
    employee_id = request.employee_id
    scope = request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    vendor_service = VendorHistoryService(scope)
    resp_obj = vendor_service.get_vendor_history(request, vendor_id, employee_id, vys_page)
    return HttpResponse(resp_obj.get(), content_type='application/json')
