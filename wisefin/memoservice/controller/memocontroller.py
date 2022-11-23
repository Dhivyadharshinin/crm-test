import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from memoservice.service.memoservice import MemoService
from memoservice.data.request.memorequest import MemoReq


@csrf_exempt
def memo(request):
    if request.method == 'POST':
        return create_memo(request)
    if request.method == 'GET':
        return fetch_memo(request)
    if request.method == 'DELETE':
        return delete_memo(request)


@csrf_exempt
def create_memo(request):
    memo_obj = json.loads(request.body)
    memo_data = MemoReq(memo_obj)
    scope = request.scope
    service = MemoService(scope)
    resp_obj = service.create_memo(memo_data)
    response = HttpResponse(resp_obj.get(), content_type='application/json')
    return response


@csrf_exempt
def fetch_memo(request):
    scope = request.scope
    service = MemoService(scope)
    resp_obj = service.fetch_memo()
    response = HttpResponse(resp_obj, content_type='application/json')
    return response


@csrf_exempt
def delete_memo(request):
    memo_id = request.GET.get('id')
    scope = request.scope
    service = MemoService(scope)
    resp_obj = service.delete_memo(memo_id)
    response = HttpResponse(resp_obj.get(), content_type='application/json')
    return response
