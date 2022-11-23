# from django.views.decorators.csrf import csrf_exempt
# from rest_framework.decorators import api_view, authentication_classes, permission_classes
# from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
# from utilityservice.service.nwisefinpermission import NWisefinPermission
# from rest_framework.permissions import IsAuthenticated
# from utilityservice.data.response.nwisefinpage import NWisefinPage
# from productservice.data.request.productrequest import PRequest
# from productservice.util.product_util import AttendanceDocumentUtil
# from utilityservice.data.response.nwisefinsuccess import SuccessMessage
# from productservice.service.productservice import ProductService
# from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription
# from django.http import HttpResponse
# import json
#
#
# # leave request
# @csrf_exempt
# @api_view(['GET', 'POST'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def leave_request(request):
#     scope = request.scope
#     employee_id = request.employee_id
#
#     if request.method == 'POST':
#         leave_service = LeaveRequestService(scope)
#
#         leave_data = json.loads(request.data.dict().get('data'))
#         req_data = LeaveDataRequest(leave_data)
#         response = leave_service.new_leave_req(req_data, employee_id)
#         try:
#             if not request.FILES['file'] is None:
#                 doc_serv = AttendanceDocumentService(scope)
#                 doc_serv.create_attendance_document(response, AttendanceDocumentUtil.LEAVE_REQUEST, request)
#         except KeyError:
#             print('error while uploading documents for the below data')
#             print('select * from attendanceservice_leaverequest where id='+str(response.id))
#         resp = MessageResponse()
#         resp.set_status(StatusType.SUCCESS)
#         resp.set_message(SuccessMessage.CREATE_MESSAGE)
#         response = HttpResponse(resp.get(), content_type="application/json")
#         return response
#
#     elif request.method == 'GET':
#         scope = request.scope
#         emp_id = request.employee_id
#         leave_serv = LeaveRequestService(scope)
#         page = request.GET.get('page', 1)
#         page = int(page)
#         vys_page = NWisefinPage(page, 10)
#         resp = leave_serv.new_leave_summary(vys_page, request, emp_id)
#         response = HttpResponse(resp.get(), content_type="application/json")
#         return response
