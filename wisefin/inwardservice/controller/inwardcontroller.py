import json
from django.http import HttpResponse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from docservice.service.documentservice import DocumentsService
from docservice.util.docutil import DocModule
from inwardservice.data.request.commentdocrequest import CommentDocRequest
from inwardservice.models import InwardFiles
from inwardservice.service.commentservice import CommentDocService
from inwardservice.util.inwardutil import get_inward_status_list, get_inward_docstatus, get_inwardstatus, \
    get_inwardaction, get_fileextension_val, get_inwarddocaction
from masterservice.data.request.courierrequest import CourierRequest
from masterservice.service.courierservice import CourierService
from nwisefin.settings import logger
from userservice.models import Employee

from inwardservice.data.request.inwardheaderrequest import HeaderRequest
from inwardservice.data.request.inwarddetailsrequest import DetailsRequest
from inwardservice.service.inwardservice import InwardService
from django.db import transaction

from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.inward_api_service import ApiService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_inward(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        inward_service = InwardService(scope)
        courier_service = CourierService(scope)
        inward_data = json.loads(request.body)
        # user_id = request.user.id
        # api_serv = ApiService(self._scope())
        # emp = api_serv.get_emp_id(request, user_id)
        # emp_id = emp['id']
        if ('courier_id' in inward_data) & (inward_data['courier_id'] != ''):
            iscourier = str(inward_data['courier_id']).isnumeric()
            if iscourier == False:
                courier_data=dict()
                courier_data['name']=inward_data['courier_id']
                courier_data['all_branch'] = False
                courier_obj = CourierRequest(courier_data)
                add_id = None
                cont_id = None
                resp_obj = courier_service.create_courier(courier_obj, add_id, cont_id, emp_id)
                try:
                    courier_id=json.loads(resp_obj.get())['id']
                    branch_id=None
                    courier_br=inward_service.courier_branch(branch_id, courier_id)
                except KeyError:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.DUPLICATE_COURIER_NAME)
                    response = HttpResponse(error_obj.get(), content_type="application/json")
                    return response
                inward_data['courier_id']=courier_id

        headerrequest_obj = HeaderRequest(inward_data)
        resp_obj = inward_service.create_inward(request, headerrequest_obj, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_inward_list(request)


def fetch_inward_list(request):
    scope = request.scope
    inward_service = InwardService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = inward_service.fetch_inward_list(vys_page, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_inward(request,inward_id):
    if request.method == 'GET':
        scope = request.scope
        inward_service = InwardService(scope)
        resp_obj = inward_service.fetch_inward(request,inward_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_inward(request, inward_id)

@csrf_exempt
def delete_inward(request, inward_id):
    scope = request.scope
    emp_id = request.employee_id
    # user_id = request.user.id
    # api_serv = ApiService(self._scope())
    # emp = api_serv.get_emp_id(request, user_id)
    # emp_id = emp['id']
    inward_service = InwardService(scope)
    resp_obj = inward_service.delete_inward(inward_id, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_inward_detail_list(request, inward_id):
    scope = request.scope
    inward_service = InwardService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = inward_service.fetch_inwarddetails_list(request,inward_id,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_detail(request, inward_id, details_id):
    if request.method == 'GET':
        scope = request.scope
        inward_service = InwardService(scope)
        resp_obj = inward_service.fetch_inwddetails(request,inward_id,details_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        inward_service = InwardService(scope)
        inward_detail_data = json.loads(request.body)
        print("inward_detail_data input" , inward_detail_data)
        inward_detail_data1 = inward_service.inward_details_assign_validation(inward_detail_data, details_id)
        # user_id = request.user.id
        # api_serv = ApiService(self._scope())
        # emp = api_serv.get_emp_id(request, user_id)
        # emp_id = emp['id']
        # inward_detail_obj = DetailsRequest(inward_detail_data1)

        count_var = request.GET.get('count', False)
        print("count_var",count_var)
        print("inward_detail_data1",inward_detail_data1)
        if count_var:
            resp_obj = inward_service.update_inwarddtlscount(inward_detail_data1,details_id, emp_id)
        else:
            resp_obj = inward_service.update_inwarddetails(inward_detail_data1,details_id, emp_id, request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        scope = request.scope
        emp_id = request.employee_id
        inward_service = InwardService(scope)
        # user_id = request.user.id
        # api_serv = ApiService(self._scope())
        # emp = api_serv.get_emp_id(request, user_id)
        # emp_id = emp['id']
        resp_obj = inward_service.delete_inwarddetail(details_id,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def clone_detail(request, inward_id, details_id, tcount):
    scope = request.scope
    emp_id = request.employee_id
    inward_service = InwardService(scope)
    # user_id = request.user.id
    # api_serv = ApiService(self._scope())
    # emp = api_serv.get_emp_id(request, user_id)
    # emp_id = emp['id']
    resp_obj = inward_service.inwarddetail_clone(request, details_id, emp_id)

    inwarddetail_id = details_id
    print("inwarddetail_id", inwarddetail_id)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = inward_service.fetch_inward_headerdetails(request, inward_id, inwarddetail_id, vys_page, tcount)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_inward(request):
    scope = request.scope
    search_obj = json.loads(request.body)
    inward_service = InwardService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = inward_service.search_inward(request, search_obj, vys_page)
    return HttpResponse(resp_obj.get(), content_type='application/json')



# @csrf_exempt
# @api_view(['POST'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def emp_branchassign(request,branch_id,user_id):
#     if request.method == 'POST':
#         Employee.objects.filter(user_id=user_id).update(branch=branch_id)
#         success_obj = Success()
#         success_obj.set_status(SuccessStatus.SUCCESS)
#         response = HttpResponse(success_obj.get(), content_type="application/json")
#         return response

# @api_view(['GET'])
# @authentication_classes([VysfinAuthentication])
# @permission_classes([IsAuthenticated, VysfinPermission])
# def fetch_branchcourier(request):
#     if request.method == 'GET':
#         inward_service = InwardService()
#         user_id = request.user.id
#         api_serv = ApiService(self._scope())
#         emp = api_serv.get_emp_id(request, user_id)
#         emp_id = emp['id']
#         page = request.GET.get('page', 1)
#         page = int(page)
#         vys_page = NWisefinPage(page, 10)
#         resp_obj = inward_service.fetch_branchcourier(vys_page,emp_id)
#         response = HttpResponse(resp_obj.get(), content_type="application/json")
#         return response


@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_ap_inward(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        inward_service = InwardService(scope)
        search_obj = json.loads(request.body)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        # user_id = request.user.id
        # api_serv = ApiService(self._scope())
        # emp = api_serv.get_emp_id(request, user_id)
        # emp_id = emp['id']
        resp_obj = inward_service.fetch_ap_inward_list(request,search_obj,vys_page,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def inwardstatus_update(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        inward_service = InwardService(scope)
        print('request ',request)
        print('request ',request.body)
        print('request ',json.loads(request.body))
        search_obj = json.loads(request.body)
        # user_id = request.user.id
        # api_serv = ApiService(self._scope())
        # emp = api_serv.get_emp_id(request, user_id)
        # emp_id = emp['id']
        resp_obj = inward_service.inwardstatus_change(search_obj,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_inward_status(request):
    if request.method == 'GET':
        resp_obj = get_inward_status_list()
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def inward_summarysearch(request):
    scope = request.scope
    inward_service = InwardService(scope)
    inwd_obj = json.loads(request.body)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = inward_service.inward_summarysearch(vys_page,inwd_obj, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def view_file(request, file_id):
    scope = request.scope
    logger.info("view file Id" + str(file_id))
    doc_service = DocumentsService(scope)
    response = doc_service.file_download(file_id, request)
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def inward_file_download(request, file_id):
    scope = request.scope
    emp_id = request.employee_id
    # user_id = request.user.id
    api_serv = ApiService(scope)
    # emp = api_serv.get_emp_id(request, user_id)
    # emp_id = emp['id']
    resp_obj = api_serv.download_m2m(request, file_id, emp_id)
    return resp_obj

@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def inward_details_summarysearch(request):
    scope = request.scope
    inward_service = InwardService(scope)
    inwd_obj = json.loads(request.body)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = inward_service.inward_details_summarysearch(vys_page, inwd_obj, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_inward_docstatus(request):
    resp_obj = get_inward_docstatus()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_inwardstatus(request):
    resp_obj = get_inwardstatus()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_inwardaction(request):
    resp_obj = get_inwardaction()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def documentsummarysearch(request):
    scope = request.scope
    inward_service = InwardService(scope)
    inwd_obj = json.loads(request.body)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = inward_service.documentsummarysearch(vys_page, inwd_obj, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


# @transaction.atomic
# @csrf_exempt
# @api_view(['GET', 'POST'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def documentresponseupdate(request):
#     scope = request.scope
#     emp_id = request.employee_id
#     inward_service = InwardService(scope)
#     # response_data = json.loads(request.body)
#     response_data = json.loads(request.data.dict().get('data'))
#     # user_id = request.user.id
#     # api_serv = ApiService(self._scope())
#     # emp = api_serv.fetch_employeedata(request, user_id)
#     # emp_id = emp['id']
#     commentservice = CommentDocService(scope)
#     headerrequest_obj = DetailsRequest(response_data)
#     resp_obj = inward_service.documentresponseupdate(request, headerrequest_obj, emp_id)
#    # par_obj = ParRequest(response_data)
#     details_id = response_data["id"]
#     a = response_data.get("comments")  # []
#     doc_module = DocModule.INWARD  ###
#     for resp in a:
#         arr_obj = CommentDocRequest(resp)
#         resp_obj1 = commentservice.create_commentdoc(request,arr_obj,details_id, emp_id)
#         #arr.append(resp_obj1.id)
#         cmnt_id = resp_obj1.id
#         print("cmnt_id  :", cmnt_id)
#         h_file_key = resp.get("filekey")
#         print("comment_file_key", h_file_key)
#         if not h_file_key is None:
#             for h in h_file_key:
#                 if h not in request.FILES:
#                     logger.info("grn file key not in fileList" + str(h))
#                     print("grn file not in fileList", h)
#                     continue
#                 logger.info("grn file- key :" + str(h))
#                 logger.info("grn fileName :" + str(request.FILES.getlist(h)))
#                 for i in request.FILES.getlist(h):
#                     file_name = i.name
#                     extension = file_name.split('.')[-1]
#                     filetype_check = get_fileextension_val(extension)
#                     if filetype_check is False:
#                         error_obj = NWisefinError()
#                         error_obj.set_code(ErrorMessage.INVALID_HEADER_FILETYPE)
#                         error_obj.set_description(ErrorDescription.INVALID_HEADER_FILETYPE)
#                         response = HttpResponse(error_obj.get(), content_type="application/json")
#                         return HttpResponse(response, content_type='application/json')
#                 doc_resp_obj = api_serv.doc_upload_key(request, doc_module, h)
#                 print("doc_resp_obj", doc_resp_obj)
#                 logger.info("doc_upload_key" + str(doc_resp_obj))
#                 document_json = doc_resp_obj['data']
#                 for doc_json in document_json:
#                     inwardfiles = InwardFiles.objects.using(self._current_app_schema()).create(inwarddetails_id=details_id,
#                                                             commentdoc_id=cmnt_id,
#                                                             file_id=doc_json['file_name'],
#                                                             created_by=emp_id,
#                                                             created_date=now())
#
#                     # file_id = doc_json['id']
#                     # response_obj = par_service.updateFileidParDetails(file_id, pardetails_id, emp_id)
#                 logger.info('CommentDoc file Uploaded')
#     logger.info('Documnet Responsed' + str(details_id) + ',' + 'CommentDoc created' )
#     response = HttpResponse(resp_obj.get(), content_type="application/json")
#     return response

#
# @transaction.atomic
# @csrf_exempt
# @api_view(['GET', 'POST'])
# @authentication_classes([VysfinAuthentication])
# @permission_classes([IsAuthenticated, VysfinPermission])
# def documentassignupdate(request):
#     inward_service = InwardService()
#     inward_data = json.loads(request.data.dict().get('data'))
#     #inward_data = json.loads(request.body)
#     id_arr = inward_data.get('id')
#     user_id = request.user.id
#     api_serv = ApiService(self._scope())
#     emp = api_serv.fetch_employeedata(request, user_id)
#     emp_id = emp['id']
#     headerrequest_obj = DetailsRequest(inward_data)
#     resp_obj = inward_service.documentassignupdate(request, headerrequest_obj, emp_id, id_arr)
#     if "filekey" in inward_data:
#         print("iiiiiiiiiii")
#         a = inward_data.get("filekey")  # []
#         inwaeddetails_id = resp_obj.id
#         doc_module = DocModule.INWARD  ###
#         for ironman in a:
#             d_file_key = ironman
#             print("detail_file_key", d_file_key)
#             if (not d_file_key is None):
#                 logger.info("INWARD detail file- key :" + str(d_file_key))
#                 logger.info("INWARD detail fileName :" + str(request.FILES.getlist(d_file_key)))
#                 if d_file_key not in request.FILES:
#                     print("not in fileList", d_file_key)
#                     logger.info("file key not in fileList" + str(d_file_key))
#                     continue
#                 for i in request.FILES.getlist(d_file_key):
#                     print("In fileList", d_file_key)
#                     print("detailsLoop", i)
#                     file_name = i.name
#                     extension = file_name.split('.')[-1]
#                     filetype_check = get_fileextension_val(extension)
#                     if filetype_check is False:
#                         error_obj = NWisefinError()
#                         error_obj.set_code(ErrorMessage.INVALID_DETAIL_FILETYPE)
#                         error_obj.set_description(ErrorDescription.INVALID_DETAIL_FILETYPE)
#                         response = HttpResponse(error_obj.get(), content_type="application/json")
#                         return HttpResponse(response, content_type='application/json')
#                     doc_resp_obj = api_serv.doc_upload_key(request, doc_module, d_file_key)
#                     print("doc_resp_obj", doc_resp_obj)
#                     logger.info("doc_upload_key" + str(doc_resp_obj))
#                     document_json = doc_resp_obj['data']
#                     for doc_json in document_json:
#                         inwardfiles = InwardFiles.objects.using(self._current_app_schema()).create(inwarddetails_id=inwaeddetails_id,
#                                                                                      file_id=doc_json['id'],
#                                                                                      #file_name=doc_json['file_name'],
#                                                                                      created_by=emp_id,
#                                                                                      created_date=now())
#
#                     logger.info('Inwarddetail file Uploaded')
#         logger.info('Inwarddetail' + str(inwaeddetails_id) + ',' + 'Inwarddetail created')
#
#     else:
#         print("need to check")
#     response = HttpResponse(resp_obj.get(), content_type="application/json")
#     return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_inward_docaction(request):
    resp_obj = get_inwarddocaction()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_inwarddetails(request, inward_id):
    scope = request.scope
    inward_service = InwardService(scope)
    resp_obj = inward_service.fetch_inwarddetails(inward_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def inwarddetails(request):
    scope = request.scope
    inward_service = InwardService(scope)
    inward_id = request.GET.get('inward_id')
    packet_no = request.GET.get('packet_no')
    resp_obj = inward_service.inwarddetails(inward_id, packet_no, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response



@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def clone_detail(request, inward_id, details_id):
    scope = request.scope
    emp_id = request.employee_id
    inward_service = InwardService(scope)
    # user_id = request.user.id
    # api_serv = ApiService(self._scope())
    # emp = api_serv.get_emp_id(request, user_id)
    # emp_id = emp['id']
    resp_obj = inward_service.inwarddetail_clone(request, inward_id, details_id, emp_id)
    # inwarddetail_id = resp_obj.id
    # page = request.GET.get('page', 1)
    # page = int(page)
    # vys_page = NWisefinPage(page, 10)
    # resp_obj = inward_service.inward_details_clone(request, inward_id, inwarddetail_id, vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def clone_packet_count(request, inward_id, packet_no, count):
    scope = request.scope
    emp_id = request.employee_id
    inward_service = InwardService(scope)
    count = int(count)
    # user_id = request.user.id
    # api_serv = ApiService(self._scope())
    # emp = api_serv.get_emp_id(request, user_id)
    # emp_id = emp['id']
    resp_obj = inward_service.clone_packet_count(request, emp_id, inward_id, packet_no, count)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

# @transaction.atomic
# @csrf_exempt
# @api_view(['GET', 'POST'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def inwarddetailupdate(request):
#     scope = request.scope
#     emp_id = request.employee_id
#     inward_service = InwardService(scope)
#    # response_data = json.loads(request.body)
#    #  user_id = request.user.id
#    #  api_serv = ApiService(self._scope())
#    #  emp = api_serv.fetch_employeedata(request, user_id)
#    #  emp_id = emp['id']
#
#     inward_data = json.loads(request.data.dict().get('data'))
#     inward_obj = DetailsRequest(inward_data)
#     respnse_obj = inward_service.inwarddetailupdate(request, inward_obj, emp_id)
#     a = inward_data.get("filekey")  # []
#     inwaeddetails_id = respnse_obj.id
#     doc_module = DocModule.INWARD ###
#     for ironman in a:
#         d_file_key = ironman
#         print("detail_file_key", d_file_key)
#         if (not d_file_key is None):
#             # logger.info("INWARD detail file- key :" + str(d_file_key))
#             # logger.info("INWARD detail fileName :" + str(request.FILES.getlist(d_file_key)))
#             if d_file_key not in request.FILES:
#                 print("not in fileList", d_file_key)
#                 # logger.info("file key not in fileList" + str(d_file_key))
#                 continue
#             for i in request.FILES.getlist(d_file_key):
#                 print("In fileList", d_file_key)
#                 print("detailsLoop", i)
#                 file_name = i.name
#                 extension = file_name.split('.')[-1]
#                 filetype_check = get_fileextension_val(extension)
#                 if filetype_check is False:
#                     error_obj = NWisefinError()
#                     error_obj.set_code(ErrorMessage.INVALID_DETAIL_FILETYPE)
#                     error_obj.set_description(ErrorDescription.INVALID_DETAIL_FILETYPE)
#                     response = HttpResponse(error_obj.get(), content_type="application/json")
#                     return HttpResponse(response, content_type='application/json')
#                 doc_resp_obj = api_serv.doc_upload_key(request, doc_module, d_file_key)
#                 print("doc_resp_obj", doc_resp_obj)
#                 logger.info("doc_upload_key" + str(doc_resp_obj))
#                 document_json = doc_resp_obj['data']
#                 for doc_json in document_json:
#                     inwardfiles = InwardFiles.objects.using(self._current_app_schema()).create(inwarddetails_id=inwaeddetails_id,
#                                                                                  file_id=doc_json['id'],
#                                                                                  #file_name=doc_json['file_name'],
#                                                                                  created_by=emp_id,
#                                                                                  created_date=now())
#
#     #             logger.info('Inwarddetail file Uploaded')
#     # logger.info('Inwarddetail' + str(inwaeddetails_id) + ',' + 'Inwarddetail created')
#     response = HttpResponse(respnse_obj.get(), content_type="application/json")
#     return response

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def inwarddetailupdate(request):
    scope = request.scope
    emp_id = request.employee_id
    inward_service = InwardService(scope)
    # user_id = request.user.id
    api_serv = ApiService(scope)
    # emp = api_serv.get_emp_id(request, user_id)
    # emp_id = emp['id']
    inward_data = json.loads(request.data.dict().get('data'))
    logger.info("inward create data:" + str(inward_data))
    # catalog_flag = inward_data['type']
    inward_obj = DetailsRequest(inward_data)
    arr = []
    # with transaction.atomic(using=DataBase.INWARD_DB):
    respnse_obj = inward_service.inwarddetailupdate(request, inward_obj, emp_id)
    detail_id = respnse_obj.id

    h_file_key = inward_data.get('filekey')
    print("header_filekey", h_file_key)
    doc_module = DocModule.INWARD  ###
    if not h_file_key is None:
        for h in h_file_key:
            if h not in request.FILES:
                logger.info("Inwarddetail file key not in fileList" + str(h))
                print("Inwarddetail file not in fileList", h)
                continue
            logger.info("Inwarddetail file- key :" + str(h))
            logger.info("Inwarddetail fileName :" + str(request.FILES.getlist(h)))
            for i in request.FILES.getlist(h):
                file_name = i.name
                extension = file_name.split('.')[-1]
                filetype_check = get_fileextension_val(extension)
                if filetype_check is False:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_FILETYPE)
                    error_obj.set_description(ErrorDescription.INVALID_FILETYPE)
                    response = HttpResponse(error_obj.get(), content_type="application/json")
                    return HttpResponse(response, content_type='application/json')
            doc_resp_obj = api_serv.doc_upload_key(request, doc_module, h)
            document_json = doc_resp_obj['data']
            r_obj = inward_service.inwardfile(detail_id, document_json, emp_id)
            print(r_obj)
            # for doc_json in document_json:
            #     inwardfiles = InwardFiles.objects.using(ApplicationNamespace.INWARD_SERVICE).create(
            #         inwarddetails_id=detail_id,
            #         file_id=doc_json['id'],
            #         # file_name=doc_json['file_name'],
            #         created_by=emp_id,
            #         created_date=now())
            #     logger.info('PO Header file Uploaded')
            logger.info('Inwarddetail file Uploaded')
    logger.info('Inwarddetail' + str(detail_id) + ',' + 'Inwarddetail created')
    response = HttpResponse(respnse_obj.get(), content_type="application/json")
    return response



# @api_view(['POST'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def doc_responsesummarysearch(request):
#     scope = request.scope
#     emp_id = request.employee_id
#     inward_service = InwardService(scope)
#     inwd_obj = json.loads(request.body)
#     # user_id = request.user.id
#     # api_serv = ApiService(self._scope())
#     # emp = api_serv.fetch_employeedata(request, user_id)
#     # emp_id = emp['id']
#     page = request.GET.get('page', 1)
#     page = int(page)
#     vys_page = NWisefinPage(page, 10)
#     resp_obj = inward_service.doc_responsesummarysearch(emp_id, vys_page, inwd_obj, request)
#     response = HttpResponse(resp_obj.get(), content_type="application/json")
#     return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def inwardtran(request, inward_id):
    scope = request.scope
    emp_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    # user_id = request.user.id
    # api_serv = ApiService(self._scope())
    # emp = api_serv.get_emp_id(request, user_id)
    # emp_id = emp['id']
    inward_service = InwardService(scope)
    response_obj = inward_service.inwardtran(inward_id, emp_id, vys_page, request)
    response = HttpResponse(response_obj.get(), content_type='application/json')
    return response

@api_view(['DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def inward_delete(request, inward_id, detail_id,packet_no):
    scope = request.scope
    emp_id = request.employee_id
    inward_service = InwardService(scope)
    # user_id = request.user.id
    # api_serv = ApiService(self._scope())
    # emp = api_serv.get_emp_id(request, user_id)
    # emp_id = emp['id']
    resp_obj = inward_service.inward_delete(inward_id, detail_id , packet_no, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def inwarddetails_file(request, file_id):
    scope = request.scope
    emp_id = request.employee_id
    inward_service = InwardService(scope)
    doc_module = DocModule.INWARD  ###
    # detail_id = request.GET.get('detail_id')
    # comment_id = int(request.GET.get('comment_id'))
    # if comment_id == 0:
    #     print("comm", comment_id)
    resp_obj = inward_service.inwarddetails_file(request, doc_module, file_id, emp_id)
    # else:
    #     resp_obj = inward_service.inwarddetails_doc_file(request, doc_module, detail_id, comment_id, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response