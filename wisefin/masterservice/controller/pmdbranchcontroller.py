import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import authentication_classes, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from masterservice.data.request.pmdbranchrequest import PmdBranchRequest
from masterservice.service.pmdbranchservice import PmdBranchService
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def pmd_branch_create(request):
    if request.method == 'POST':
        scope=request.scope
        pmd_serv = PmdBranchService(scope)
        pmd_data = json.loads(request.body)
        data_obj = PmdBranchRequest(pmd_data)
        user_id = request.employee_id
        resp_obj = pmd_serv.create_pmd_branch(data_obj, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_pmd_branch_list(request)


def fetch_pmd_branch_list(request):
    user_id = request.employee_id
    scope=request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    # query = request.GET.get('query')
    pmd_serv = PmdBranchService(scope)
    resp_obj = pmd_serv.fetch_pmd_branch_list(user_id,vys_page,request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@csrf_exempt
@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def pmd_activate_inactivate(request):
    scope = request.scope
    data = json.loads(request.body)
    data_request = PmdBranchRequest(data)
    gl_service = PmdBranchService(scope)
    resp_obj = gl_service.pmd_activate_inactivate(request, data_request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


