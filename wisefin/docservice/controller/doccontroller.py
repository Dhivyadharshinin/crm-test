import json
import boto3
from django.http import HttpResponse, StreamingHttpResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from docservice.data.response.documentresponse import DocumentsResponse
from docservice.models.docmodels import MemoDocuments, VendorDocuments, InwardDocuments
from docservice.service.documentservice import DocumentsService, VowDocumentsService
from docservice.util.docutil import DocModule, DocPrefix, getDocModuleType, get_docmodule_type_list, getDocModuleType_ta
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def upload_documents(request):
    if request.method == 'POST':
        scope = request.scope
        doc_service=DocumentsService(scope)
        #params=json.loads(request.body)
        params = json.loads(request.data.dict().get('params'))
        resp_obj = doc_service.upload(request,params)
        response= HttpResponse(resp_obj.get(), content_type="application/json")
        return HttpResponse(response, content_type='application/json')


@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_documents(request, file_id):
    if request.method == 'GET':
        user_id = request.user.id
        scope = request.scope
        module = request.GET.get('module')
        module=int(module)
        #print(module,'TESTINH@889900')
        document_service = DocumentsService(scope)
        resp_obj = document_service.fetch_documents(file_id, user_id,module)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_document(request,file_id)

# @api_view(['GET', 'DELETE'])
# @authentication_classes([VysfinAuthentication])
# @permission_classes([IsAuthenticated, VysfinPermission])
def delete_document(request,file_id):
    user_id = request.user.id
    scope = request.scope
    module = request.GET.get('module')
    module = int(module)
    document_service = DocumentsService(scope)
    resp_obj = document_service.delete_document( file_id, user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response



#@api_view(['GET', 'POST'])
#@authentication_classes([VysfinAuthentication])
#@permission_classes([IsAuthenticated, VysfinPermission])
def download_attachment(request, file_id):
    #user_id = request.user.id
    user_id = None
    scope = request.scope
    module=request.GET.get('module')
    #module=int(module)
    document_service = DocumentsService(scope)
    resp_obj = document_service.doc_download(file_id, user_id)
    return resp_obj



@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_info(request):
    user_id = request.user.id
    scope = request.scope
    fileid = request.GET.get('file_id')
    module_sep = fileid.split(',')[0]
    module_prefix = module_sep.split('_')[0]
    module_prefix=module_prefix + '_'
    doc_module=DocModule()
    module = doc_module.get_prefix_modulenum_(module_prefix)
    fileids=list(fileid.split(','))
    array_data=[]
    for file_data in fileids:
        file_ids=file_data.split('_')[-1]
        array_data.append(file_ids)
    document_service = DocumentsService(scope)
    resp_obj = document_service.get_fileinfo(array_data, module)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def upload_single_document(request):
    if request.method == 'POST':
        scope = request.scope
        doc_service=DocumentsService(scope)
        params = json.loads(request.data.dict().get('params'))
        files=request.FILES.get('file')
        resp_obj = doc_service.upload_single_doc(files,params)
        response= HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def doc_module(request):
    module = request.GET.get('query')
    module = int(module)
    response = getDocModuleType(module)
    print(response)
    response = json.dumps(response, indent=4)
    response = HttpResponse(response, content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def doc_module_ta(request):
    # module = request.GET.get('query')
    # module = int(module)
    response = getDocModuleType_ta(request)
    print(response)
    response = json.dumps(response, indent=4)
    response = HttpResponse(response, content_type="application/json")
    return response

@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def doc_upload_ta(request):
    scope = request.scope
    params = json.loads(request.body)
    params = params['params']
    doc_service=DocumentsService(scope)
    print("doc_upload api ")
    print("doc_upload", params)
    resp_obj = doc_service.doc_upload_ta(request,params)
    response= HttpResponse(resp_obj.get(), content_type="application/json")
    return HttpResponse(response, content_type='application/json')
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def doc_upload(request):
    scope = request.scope
    params = json.loads(request.body)
    params = params['params']
    doc_service=DocumentsService(scope)
    print("doc_upload api ")
    print("doc_upload", params)
    resp_obj = doc_service.doc_upload(request,params)
    response= HttpResponse(resp_obj.get(), content_type="application/json")
    return HttpResponse(response, content_type='application/json')

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def doc_moduletype(request):
    response = get_docmodule_type_list()
    print(response)
    response = HttpResponse(response.get(), content_type="application/json")
    return response


@api_view(['GET'])
def doc_download(request, file_id):
    document_service = VowDocumentsService(request)
    resp_obj = document_service.vow_doc_download(file_id)
    return resp_obj


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def docdownload(request, file_id):
    document_service = DocumentsService(request)
    resp_obj = document_service.doc_download(file_id, None)
    return resp_obj