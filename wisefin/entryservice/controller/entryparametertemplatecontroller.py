import json
from django.http import HttpResponse

from entryservice.data.request.entryparamtemplaterequest import EntryTemplateRequest
from entryservice.data.request.entryrequest import EntryRequest
from entryservice.service.enrtryparametertemplateservice import ParmaTemplateService
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from entryservice.util.entryutil import Fetch_Data, list_conditionname, get_entry_list
from entryservice.util.entryutil import Fetch_Data
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
#from vysfinutility.data.vysfinpage import VysfinPage
from utilityservice.service.entry_api_service import ApiService

@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def createparametername(request):
    if request.method == 'POST':
        scope = request.scope
        paramtemp_service = ParmaTemplateService(scope)
        paramname_details = json.loads(request.body)
        paramname = paramname_details['paramname']
        columnnamecredit = paramname_details['columnnamecredit']
        # columnnamedebit = paramname_details['columnnamedebit']
        # code = paramname_details['code']
        # entry_template = paramname_details['entry_template']
        # # columnnames = paramname_details['columnname']
        # # code = paramname_details['code']
        # # columnnames_dumps = json.dumps(columnnames)
        # # columnnames_dumps = list(columnnames_dumps)
        # # columnnames_dumps[0] = ''
        # # columnnames_dumps[-1] = ''
        # # columnnames_dumps = ''.join(columnnames_dumps)
        columnnamecredit = json.dumps(columnnamecredit)
        columnnamecredit = list(columnnamecredit)
        columnnamecredit[0] = ''
        columnnamecredit[-1] = ''
        columnnamecredit = ''.join(columnnamecredit)

        columnnamedebit = paramname_details['columnnamedebit']
        columnnamedebit = json.dumps(columnnamedebit)
        columnnamedebit = list(columnnamedebit)
        columnnamedebit[0] = ''
        columnnamedebit[-1] = ''
        columnnamedebit = ''.join(columnnamedebit)
        code = paramname_details['code']
        entry_template = paramname_details['entry_template']
        # entry_template = json.dumps(entry_template)
        # entry_template = list(entry_template)
        # entry_template[0] = ''
        # entry_template[-1] = ''
        # entry_template = ''.join(entry_template)
        vysfinservice = ApiService(scope)
        emp_id = request.employee_id
        resp_obj = paramtemp_service.create_parametername(emp_id,paramname,code,entry_template,columnnamecredit,columnnamedebit,scope)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

    elif request.method == 'GET':
        return fetch_columnparameter(request)
def fetch_columnparameter(request):
    if request.method == 'GET':
        scope = request.scope
        paramtemp_service = ParmaTemplateService(scope)
        user_id = request.user.id
        trans_id = request.GET.get('trans_id')
        resp_obj = paramtemp_service.fetch_columnparameterservice(user_id,trans_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_displaynamedr(request):
    if request.method == 'GET':
        scope = request.scope
        paramtemp_service = ParmaTemplateService(scope)
        user_id = request.user.id
        trans_id = request.GET.get('trans_id')
        dynamic_query = Fetch_Data(scope)
        query = dynamic_query.dynamic_querydr(trans_id,scope)
        query = json.dumps(query, indent=6)
        return HttpResponse(query, content_type='application/json')

@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_displaynamecr(request):
    if request.method == 'GET':
        scope = request.scope
        paramtemp_service = ParmaTemplateService(scope)
        user_id = request.user.id
        trans_id = request.GET.get('trans_id')
        dynamic_query = Fetch_Data(scope)
        query = dynamic_query.dynamic_querycr(trans_id,scope)
        query = json.dumps(query, indent=6)
        return HttpResponse(query, content_type='application/json')


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_conditions(request):
    scope = request.scope
    resp_obj = list_conditionname()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_querycondition(request):
    if request.method == 'POST':
        scope = request.scope
        paramtemp_service = ParmaTemplateService(scope)
        query_data = json.loads(request.body)
        emp_id = request.employee_id
        crno = query_data['crno']
        invoiceheader_id = query_data['invoiceheader_id']
        invoicedetails_id = query_data['invoicedetails_id']
        module_name = query_data['module_name']
        #apdebitamount = query_data['apdebit_amount']
        type = request.GET.get('type')
        if type=='CREDIT':
            resp_obj = paramtemp_service.queryconditioncr_check(crno, invoiceheader_id, invoicedetails_id, module_name,emp_id,scope)
            response = HttpResponse(resp_obj.get(), content_type="application/json")
            return response
        else:
            resp_obj = paramtemp_service.querycondition_check(crno,invoiceheader_id,invoicedetails_id,module_name,emp_id,scope)
            response = HttpResponse(resp_obj.get(), content_type="application/json")
            return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_paramname_list(request):
    if request.method == 'GET':
        scope = request.scope
        paramtemp_service = ParmaTemplateService(scope)
        emp_id = request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        query = request.GET.get('query', None)
        resp_obj = paramtemp_service.fetch_all_paramname_list(query, vys_page, emp_id, request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    # elif request.method == 'POST':
    #     return inactive_parametername(request)
@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def inactive_parametername(request):
    if request.method == 'POST':
        scope = request.scope
        paramtemp_service = ParmaTemplateService(scope)
        query_data = json.loads(request.body)
        param_id=query_data['param_id']
        #param_id = request.GET.get('param_id')
        emp_id = request.employee_id
        resp_obj = paramtemp_service.inactiveparametername(param_id,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return parameternameget(request)

def parameternameget(request):
    if request.method == 'GET':
        scope = request.scope
        paramtemp_service = ParmaTemplateService(scope)
        emp_id = request.employee_id
        param_id = request.GET.get('param_id')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        query = request.GET.get('query', None)
        resp_obj = paramtemp_service.fetch_parametername(query, vys_page, param_id, request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def entrytemplateupdate(request):
    if request.method == 'POST':
        scope = request.scope
        paramtemp_service = ParmaTemplateService(scope)
        template_obj = json.loads(request.body)
        vysfinservice = ApiService(scope)
        emp_id = request.employee_id
        for i in template_obj:
            templateobj = EntryTemplateRequest(i)
            resp_obj = paramtemp_service.entrytemplate_update(emp_id,templateobj)
            response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


#entrymoduledropdown

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_entrytype(request):
    scope = request.scope
    resp_obj = get_entry_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
