from django.http import HttpResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from faservice.data.request.assetdebitrequest import AssetDebitRequest
from faservice.data.request.assetdetailsrequest import AssetDetailsRequest
from faservice.service.assetdebitservice import AssetDebitService
from faservice.service.assetdetailsservice import AssetDetailsService
from faservice.service.assetlocationservice import AssetLocationService
# from userservice.service.employeeservice import EmployeeService
from nwisefin.settings import logger
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
import json
from utilityservice.data.response.nwisefinpage import NWisefinPage

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_assetdebit(request):

    if request.method == 'POST':
        assetcapit_data = json.loads(request.body)
        logger.info('FAL_ASSETDEBIT_DATA:{}'.format(assetcapit_data))
        assetcapit_array=assetcapit_data.get('Asset')
        #doc_type=assetcapit_data['Doc_Type']
        #qty=int(assetcapit_data.get('qty'))
        emp_service = ''
        user_id = request.user.id
        emp_id=request.employee_id




        # obj_array=list()
        # for i in assetdebit_json:
        #     assetdebit_obj = AssetDebitRequest(i)
        #     obj_array.append(assetdebit_obj)
        # resp_obj = assetdebit_serv.create_assetdebit(obj_array, emp_id,doc_type,assetdebit_data)
        #
        assetdetails_serv = AssetDetailsService(scope)
        assetdtlsobj_list = list()
        for i in assetcapit_array:
            assetdetails_obj = AssetDetailsRequest(i)
            assetdtlsobj_list.append(assetdetails_obj)
            #print('TESTING',assetdtlsobj_list)
            #assetdtlsobj_list.append(assetdetails_obj)
        assetdtlsresp_obj = assetdetails_serv.create_assetdetails(assetdtlsobj_list, emp_id, user_id)


        #if type(resp_obj) is type(tuple()):
        # assetdebit_resp=resp_obj[0]/
        # assetgroup_resp=resp_obj[1]/
        # asset_capresp=json.loads(assetdebit_resp.get())
        # assetdtls_resp=json.loads(assetdtlsresp_obj.get())
        # asset_capresp['AssetDtlsData'] = assetdtls_resp["data"]
        # if doc_type == 'BUC':
        #     asset_capresp['AssetGroup']=assetgroup_resp.__dict__
        # resp=json.dumps(asset_capresp)


        response = HttpResponse(assetdtlsresp_obj.get(), content_type="application/json")
        return response

#     elif request.method == 'GET':
#         return fetch_assetlocation_list(request)
#
#
# def fetch_assetlocation_list(request):
#     user_id = request.user.id
#     page = request.GET.get('page', 1)
#     page = int(page)
#     vys_page = NWisefinPage(page, 10)
#     query = request.GET.get('query', None)
#     resp_obj = assetlocation_serv.fetch_assetlocation_list(query, vys_page)
#     response = HttpResponse(resp_obj.get(), content_type="application/json")
#     return response
#
#
# @api_view(['GET', 'DELETE'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def fetch_assetlocation(request, assetlocation_id):
#     if request.method == 'GET':
#         user_id = request.user.id
#         resp_obj = assetlocation_serv.fetch_assetlocation(assetlocation_id)
#         response = HttpResponse(resp_obj.get(), content_type="application/json")
#         return response
#     elif request.method == 'DELETE':
#         return delete_assetlocation(request, assetlocation_id)
#
#
# def delete_assetlocation(request, assetlocation_id):
#     user_id = request.user.id
#     emp_id=request.employee_id
#     resp_obj = assetlocation_serv.delete_assetlocation(assetlocation_id,emp_id)
#     response = HttpResponse(resp_obj.get(), content_type="application/json")
#     return response
