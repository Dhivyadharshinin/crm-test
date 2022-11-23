import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from productservice.data.request.sourcerequest import SourceRequest
from productservice.service.sourceservice import SourceService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def source(request):
    scope=request.scope
    if request.method == 'POST':
        data_json=json.loads(request.body)
        emp_id=request.employee_id
        request_fn = SourceRequest()
        source_req=request_fn.source_request(data_json,emp_id)
        resp=SourceService(scope).create_source(source_req,emp_id)
        response = HttpResponse(resp.get(), content_type='application/json')
        return response
    elif request.method == 'GET':
        action = request.GET.get('action', None)
        if action == None or action == 'summary':
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page = NWisefinPage(page, 10)
            resp = SourceService(scope).fetch_source(request, vys_page)
            response = HttpResponse(resp.get(), content_type='application/json')
            return response

        elif  action == 'fetch':
            source_id = request.GET.get('id',None)
            resp = SourceService(scope).particular_get_source(source_id)
            response = HttpResponse(resp.get(), content_type='application/json')
            return response













