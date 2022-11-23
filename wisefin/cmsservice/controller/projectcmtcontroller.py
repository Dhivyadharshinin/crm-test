import json
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from cmsservice.data.request.projectcmtrequest import Commentsrequest
from cmsservice.service.cmscommonservice import CommonService, VowCommonService
from cmsservice.service.projectcmtservice import Commentservice, VowCommentService
from cmsservice.util.cmsutil import get_fileextension_val, DocUtil
from docservice.service.documentservice import DocumentsService, VowDocumentsService
from docservice.util.docutil import DocModule
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage


# comments - create and view
@transaction.atomic()
@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_comments(request, ref_id):
    if request.method == 'POST':
        scope = request.scope
        logger.info("start comment")
        doc_service = DocumentsService(scope)
        docmodule_obj = DocModule()
        print("File", request.FILES.getlist('file'))
        if request.FILES.getlist('file') != []:
            for i in request.FILES.getlist('file'):
                file_name = i.name
                print(file_name, ',file_name')
                extension = file_name.split('.')[-1]
                logger.info("fileextension " + str(file_name) + ' ' + str(extension))
                filetype_check = get_fileextension_val(extension)
                logger.info("filetypecheck " + str(filetype_check))
                if filetype_check is False:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_FILETYPE)
                    error_obj.set_description(ErrorDescription.INVALID_FILETYPE)
                    response = HttpResponse(error_obj.get(), content_type="application/json")
                    return HttpResponse(response, content_type='application/json')
        cmts_data = json.loads(request.data.dict().get('data'))
        cmts_obj = Commentsrequest(cmts_data)
        cmts_service = Commentservice(scope)
        com_service = CommonService(scope)
        emp_id = request.employee_id
        response_obj = cmts_service.createcmts(request, cmts_obj, ref_id, emp_id)
        content_type = DocUtil.comments
        cmts_id = response_obj.id
        type = response_obj.ref_type
        if request.FILES.getlist('file') != []:
            params = dict()
            params['module'] = docmodule_obj.CMS
            params['ref_id'] = docmodule_obj.CMS
            params['ref_type'] = docmodule_obj.CMS
            resp_obj3 = doc_service.upload(request, params)
            logger.info("docupload" + str(resp_obj3))
            document_json = json.loads(resp_obj3.get())['data']
            logger.info("docjson" + str(document_json))
            docfl_obj = com_service.updateprojectattachement(document_json, cmts_id, content_type, type, emp_id)

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        response = HttpResponse(success_obj.get(), content_type='application/json')
        return response

    elif request.method == 'GET':
        return fetch_cmts_list(request, ref_id)


def fetch_cmts_list(request, ref_id):
    scope = request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    cmts_service = Commentservice(scope)
    response_obj = cmts_service.fetch_cmts_list(request, vys_page, ref_id)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response


@transaction.atomic()
@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_reply(request, ref_id):
    if request.method == 'POST':
        scope = request.scope
        logger.info("start")
        doc_service = DocumentsService(scope)
        docmodule_obj = DocModule()
        if request.FILES.getlist('file') != []:
            for i in request.FILES.getlist('file'):
                file_name = i.name
                print(file_name, ',file_name')
                extension = file_name.split('.')[-1]
                logger.info("fileextension " + str(file_name) + ' ' + str(extension))
                filetype_check = get_fileextension_val(extension)
                logger.info("filetypecheck " + str(filetype_check))
                if filetype_check is False:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_FILETYPE)
                    error_obj.set_description(ErrorDescription.INVALID_FILETYPE)
                    response = HttpResponse(error_obj.get(), content_type="application/json")
                    return HttpResponse(response, content_type='application/json')
                logger.info("Fuction Entry")
        cmts_data = json.loads(request.data.dict().get('data'))
        cmts_obj = Commentsrequest(cmts_data)
        cmts_service = Commentservice(scope)
        com_service = CommonService(scope)
        emp_id = request.employee_id
        # ref_type = request.GET.get('ref_type')
        # reply_id = request.GET.get('reply_id')
        response_obj = cmts_service.createreply(request, cmts_obj, ref_id, emp_id)
        content_type = DocUtil.comments
        cmts_id = response_obj.id
        type = response_obj.type
        print("response", response_obj.__dict__)
        print("comments", cmts_id)
        if request.FILES.getlist('file') != []:
            params = dict()
            params['module'] = docmodule_obj.CMS
            params['ref_id'] = docmodule_obj.CMS
            params['ref_type'] = docmodule_obj.CMS
            resp_obj3 = doc_service.upload(request, params)
            logger.info("docupload" + str(resp_obj3))
            document_json = json.loads(resp_obj3.get())['data']
            logger.info("docjson" + str(document_json))
            docfl_obj = com_service.updateprojectattachement(document_json, cmts_id, content_type, type, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


#  vow comments api
@transaction.atomic()
@csrf_exempt
@api_view(['POST', 'GET'])
def vow_create_comments(request, ref_id):
    if request.method == 'POST':
        logger.info("start")
        doc_service = VowDocumentsService(request)
        docmodule_obj = DocModule()
        print("File", request.FILES.getlist('file'))
        print("File", request.FILES.getlist('file') != [])
        if request.FILES.getlist('file') != []:
            for i in request.FILES.getlist('file'):
                file_name = i.name
                print(file_name, ',file_name')
                extension = file_name.split('.')[-1]
                logger.info("fileextension " + str(file_name) + ' ' + str(extension))
                filetype_check = get_fileextension_val(extension)
                logger.info("filetypecheck " + str(filetype_check))
                if filetype_check is False:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_FILETYPE)
                    error_obj.set_description(ErrorDescription.INVALID_FILETYPE)
                    response = HttpResponse(error_obj.get(), content_type="application/json")
                    return HttpResponse(response, content_type='application/json')
                logger.info("Fuction Entry")
        cmts_data = json.loads(request.data.dict().get('data'))
        cmts_obj = Commentsrequest(cmts_data)
        comments_service = VowCommentService(request)
        ref_type = request.GET.get('ref_type')
        response_obj = comments_service.vow_createcmts(request, cmts_obj, ref_id, ref_type)
        cmts_id = response_obj.id
        content_type = DocUtil.comments
        type = response_obj.type["id"]
        if request.FILES.getlist('file') != []:
            params = dict()
            params['module'] = docmodule_obj.CMS
            params['ref_id'] = docmodule_obj.CMS
            params['ref_type'] = docmodule_obj.CMS
            resp_obj3 = doc_service.upload(request, params)
            logger.info("docupload" + str(resp_obj3))
            document_json = json.loads(resp_obj3.get())['data']
            logger.info("docjson" + str(document_json))
            comm_service = VowCommonService(request)
            docfl_obj = comm_service.updateprojectattachement(document_json, cmts_id, content_type, type)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response

    elif request.method == 'GET':
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        ref_type = request.GET.get('ref_type')
        comments_service = VowCommentService(request)
        response_obj = comments_service.vow_fetch_cmts_list(request, vys_page, ref_id, ref_type)
        response = HttpResponse(response_obj.get(), content_type="application/json")
        return response


@transaction.atomic()
@csrf_exempt
@api_view(['POST', 'GET'])
def vow_create_reply(request, ref_id):
    if request.method == 'POST':
        comments_service = VowCommentService(request)
        comm_service = VowCommonService(request)
        logger.info("start")
        doc_service = VowDocumentsService(request)
        docmodule_obj = DocModule()
        if request.FILES.getlist('file') != []:
            for i in request.FILES.getlist('file'):
                file_name = i.name
                print(file_name, ',file_name')
                extension = file_name.split('.')[-1]
                logger.info("fileextension " + str(file_name) + ' ' + str(extension))
                filetype_check = get_fileextension_val(extension)
                logger.info("filetypecheck " + str(filetype_check))
                if filetype_check is False:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_FILETYPE)
                    error_obj.set_description(ErrorDescription.INVALID_FILETYPE)
                    response = HttpResponse(error_obj.get(), content_type="application/json")
                    return HttpResponse(response, content_type='application/json')
                logger.info("Fuction Entry")
        cmts_data = json.loads(request.data.dict().get('data'))
        cmts_obj = Commentsrequest(cmts_data)
        ref_type = request.GET.get('ref_type')
        reply_id = request.GET.get('reply_id')
        response_obj = comments_service.vow_createreply(request, cmts_obj, ref_id, ref_type, reply_id)
        cmts_id = response_obj.id
        type = response_obj.type["id"]
        if request.FILES.getlist('file') != []:
            params = dict()
            params['module'] = docmodule_obj.CMS
            params['ref_id'] = docmodule_obj.CMS
            params['ref_type'] = docmodule_obj.CMS
            resp_obj3 = doc_service.upload(request, params)
            logger.info("docupload" + str(resp_obj3))
            document_json = json.loads(resp_obj3.get())['data']
            logger.info("docjson" + str(document_json))
            content_type = DocUtil.comments
            docfl_obj = comm_service.updateprojectattachement(document_json, cmts_id, content_type, type)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response
