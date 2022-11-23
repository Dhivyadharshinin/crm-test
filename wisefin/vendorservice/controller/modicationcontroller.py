from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from nwisefin import settings
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from django.db import transaction
from vendorservice.service.modicationservice import ModicationService
val_url = settings.VYSFIN_URL


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def modication_view(request, vendor_id):
    scope = request.scope
    employee_id = request.employee_id
    modication_serv = ModicationService(scope)
    response = modication_serv.modication_view(employee_id,vendor_id)
    return response


@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def modication_approve(request, vendor_id):
    scope = request.scope
    employee_id = request.employee_id
    modication_serv = ModicationService(scope)
    response = modication_serv.modication_approve(request, vendor_id, employee_id)
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def modication_view_type(request, vendor_id):
    scope = request.scope
    modication_serv = ModicationService(scope)
    response = modication_serv.modication_view_type(vendor_id)
    return response

# @csrf_exempt
# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def modication_approve(request, vendor_id):
#     vendor_service = VendorService()
#     mod_status_rel='delete'
#     resp_obj = vendor_service.modification_serviceview(vendor_id)
#     x = resp_obj.data
#     user_id = request.user.id
#     for i in x:
#         mod_status = i.mod_status
#         old_id = i.ref_id
#         new_id = i.modify_ref_id
#         mod_type = i.ref_type
#         if mod_status ==ModifyStatus.delete:
#             resp_obj = vendor_service.modify_delrecursion(vendor_id, old_id,user_id)
#         if mod_type == VendorRefType.VENDOR:
#             resp_obj = vendor_service.modification_action_vendor(mod_status, old_id, new_id, user_id)
#         if mod_type == VendorRefType.VENDOR_ADDRESS:
#             address_service = VendorAddressService()
#             resp_obj = address_service.modification_action_vendoraddress(mod_status, old_id, new_id, vendor_id, user_id)
#         if mod_type == VendorRefType.VENDOR_CONTACT:
#             contact_service = VendorContactService()
#             resp_obj = contact_service.modification_action_vendorcontact(mod_status, old_id, new_id, vendor_id, user_id)
#         if mod_type == VendorRefType.VENDOR_PROFILE:
#             profile_service = ProfileService()
#             resp_obj = profile_service.modification_action_vendorprofile(mod_status, old_id, new_id, vendor_id, user_id)
#         if mod_type == VendorRefType.VENDOR_DIRECTOR:
#             director_service = DirectorService()
#             resp_obj = director_service.modification_action_vendordirector(mod_status, old_id, new_id, vendor_id,
#                                                                            user_id)
#         if mod_type == VendorRefType.VENDOR_BRANCH:
#             branch_service = branchservice()
#             resp_obj = branch_service.modification_action_branch(mod_status, old_id, new_id, vendor_id, user_id)
#         if mod_type == VendorRefType.VENDOR_CONTRACT:
#             contract_service = ContractorService()
#             resp_obj = contract_service.modification_action_contractor(mod_status, old_id, new_id, vendor_id, user_id)
#         if mod_type == VendorRefType.VENDOR_CLIENT:
#             client_service = ClientService()
#             resp_obj = client_service.modification_action_client(mod_status, old_id, new_id, vendor_id, user_id)
#         if mod_type == VendorRefType.VENDOR_PRODUCT:
#             product_service = productservice()
#             resp_obj = product_service.modification_action_product(mod_status, old_id, new_id, vendor_id, user_id)
#         if mod_type == VendorRefType.VENDOR_DOCUMENT:
#             document_service = DocumentService()
#             resp_obj = document_service.modification_action_document(mod_status, old_id, new_id, vendor_id, user_id)
#         if mod_type == VendorRefType.VENDOR_SUPPLIERTAX:
#             suppliertax_service = TaxService()
#             resp_obj = suppliertax_service.modification_action_suppliertax(mod_status, old_id, new_id, vendor_id,
#                                                                            user_id)
#         if mod_type == VendorRefType.VENDOR_PAYMENT:
#             payment_service = paymentservice()
#             resp_obj = payment_service.modification_action_payment(mod_status, old_id, new_id, vendor_id, user_id)
#         if mod_type == VendorRefType.VENDOR_ACTIVITY:
#             activity_service = ActivityService()
#             resp_obj = activity_service.modification_action_activity(mod_status, old_id, new_id, vendor_id, user_id)
#         if mod_type == VendorRefType.VENDOR_ACTIVITYDETAIL:
#             activitydtl_service = ActivityDetailsService()
#             resp_obj = activitydtl_service.modification_action_activitydetail(mod_status, old_id, new_id, vendor_id,
#                                                                               user_id)
#         if mod_type == VendorRefType.VENDOR_CATELOG:
#             catelog_service = CatelogService()
#             resp_obj = catelog_service.modification_action_catelog(mod_status, old_id, new_id, vendor_id, user_id)
#     resp_obj = vendor_service.modification_approve_status(vendor_id, user_id)
#     return HttpResponse(resp_obj.get(), content_type='application/json')
