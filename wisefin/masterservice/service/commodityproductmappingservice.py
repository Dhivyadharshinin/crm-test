import json
import traceback

from django.db import IntegrityError
from django.db.models import Q
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.service.Codegenerator import CodeGen
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.util.masterutil import ModifyStatus, MasterRefType, RequestStatusUtil, Code_Gen_Type, Code_Gen_Value
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessMessage, SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from datetime import datetime
import json
from masterservice.data.response.commodityproductmappingresponse import CommodityProductMapResponse
from masterservice.models.mastermodels import CommodityProductMaping
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.api_service import ApiService
# from django.db.models import Q
# from prservice.data.response.commodityproductmappingresponse import CommodityProductMapResponse
# from prservice.data.response.mepresponse import MepResponse
# from prservice.data.response.prauditresponse import PrAuditResponse
# from prservice.models import CommodityProductMaping
# from prservice.service.prauditservice import PrAuditService
# from prservice.util.prutil import PrModifyStatus, PrRefType
# from vysfinutility.data.error import Error
# from vysfinutility.data.error_const import ErrorDescription, ErrorMessage
# from vysfinutility.data.success import Success, SuccessMessage, SuccessStatus
# from vysfin.settings import logger
from django.utils.timezone import now
# from vysfinutility.data.vysfinlist import VysfinList
# from vysfinutility.data.vysfinpaginator import VysfinPaginator
# from vysfinutility.service.dbutil import DataBase
# from vysfinutility.service.prpo_api_service import ApiService

class CommodityProductMapService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)
    def cpmapping(self, data, emp_id):
        method = data.get('method')
        commodity_id = data.get('commodity_id')
        product_id_arr = data.get('product_id')
        logger.error(str(method))
        logger.error(str(commodity_id))
        logger.error(str(product_id_arr))
        try:
            if method == 'add':
                logger.error('COMMODITYPRODUCTMAPPING: CommodityProductMaping Update or added Started')
                for product_id in product_id_arr:
                    condition = Q(commodity_id=commodity_id) & Q(product_id=product_id)
                    cmp = CommodityProductMaping.objects.using(self._current_app_schema()).filter(condition)
                    logger.error(str(cmp))
                    if len(cmp) <= 0:
                        com_prod_mapping=CommodityProductMaping.objects.using(self._current_app_schema()).create(commodity_id=commodity_id,
                                                               product_id=product_id,
                                                              created_by=emp_id)
                    logger.error('COMMODITYPRODUCTMAPPING: CommodityProductMaping Update or added Success' + str(com_prod_mapping))
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                return success_obj
            elif method == 'remove':
                logger.error('COMMODITYPRODUCTMAPPING: CommodityProductMaping Remove Started')
                for product_id in product_id_arr:
                    condition = Q(commodity_id=commodity_id) & Q(product_id=product_id)
                    com_prod_mapping=CommodityProductMaping.objects.using(self._current_app_schema()).filter(condition).delete()
                    logger.error('COMMODITYPRODUCTMAPPING: CommodityProductMaping Remove Success' + str(com_prod_mapping))
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
                return success_obj
        except:

            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_COMMODITYPRODUCTMAPING_ID)
            error_obj.set_description(ErrorDescription.INVALID_COMMODITYPRODUCTMAPING_ID)
            return error_obj

    def audit_function(self, audit_data, refid, relrefid, emp_id, action, reqstatus):
        if action == PrModifyStatus.DELETE:
            data = None
        else:
            data = audit_data.__dict__
            del data['_state']
        audit_service = PrAuditService()
        audit_obj = PrAuditResponse()
        audit_obj.set_refid(refid)
        audit_obj.set_reqstatus(reqstatus)
        audit_obj.set_reftype(PrRefType.COMMODITYPRODUCTMAPING)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(PrRefType.COMMODITYPRODUCTMAPING)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)

    def fetch_CommodityProductMap(self, commodity_id, emp_id, request):
        condition = Q(status=1) & Q(commodity_id=commodity_id)
        cpMap_list = CommodityProductMaping.objects.using(self._current_app_schema()).filter(condition)
        list_length = len(cpMap_list)
        cpMap_list_data = NWisefinList()
        p_arr = []
        if list_length > 0:
            for i in cpMap_list:
                p_arr.append(i.product_id)
        master_apicall = ApiService(self._scope())
        print(p_arr)
        product_data = master_apicall.get_product(request, p_arr)
        if list_length <= 0:
            pass
        else:
            for cpMap in cpMap_list:
                cpMap_data = CommodityProductMapResponse()
                cpMap_data.set_id(cpMap.id)
                cpMap_data.set_product(cpMap.product_id, product_data['data'])
                cpMap_data.set_commodity(cpMap.commodity_id)
                cpMap_list_data.append(cpMap_data)
        return cpMap_list_data

    def commodity_productsearch(self, product_id, query, request):
        product_id = int(product_id)
        if query is None:
            cpMap_list = CommodityProductMaping.objects.using(self._current_app_schema()).filter(product_id=product_id)
        else:
            condition = Q(status=1) & Q(commodity_id=query) & Q(product_id=product_id)
            cpMap_list = CommodityProductMaping.objects.using(self._current_app_schema()).filter(condition)
            c_arr = []
            list_length = len(cpMap_list)
            if list_length > 0:
                for i in cpMap_list:
                    c_arr.append(i.commodity_id)
            master_apicall = ApiService(self._scope())
            commodity_data = master_apicall.get_commodity(request, c_arr)
            print(commodity_data['data'])
        return commodity_data['data']

    def cpmapping_code(self, data, emp_id, request):
        commodity_code = data.get('commodity_code')
        product_code_arr = data.get('product_code')
        logger.error('Product_code_data_type: ' + str(type(product_code_arr)))
        if isinstance(product_code_arr, str):
            product_code_arr = json.loads(product_code_arr)
        logger.error(str(commodity_code))
        logger.error(str(product_code_arr))
        try:
            product_arr = []
            p_arr = []
            cp_arr = []
            p_id_arr = []
            cp_id_arr = []

            for product_code in product_code_arr:
                master_apicall = ApiService()
                master_product = master_apicall.fetch_productcode(request, product_code)
                product_id = master_product["id"]
                product_arr.append(product_id)

            master_apicall = ApiService()
            master_commodity = master_apicall.fetch_commoditycode(request, commodity_code)
            commodity_id = master_commodity["id"]
            # print("p", product_arr)
            # print("c", commodity_id)
            condition1 = Q(commodity_id=commodity_id) & Q(status=1)
            cmp = CommodityProductMaping.objects.using(self._current_app_schema()).filter(condition1)
            for i in cmp:
                p_arr.append(i.product_id)
                p_id_arr.append(i.id)

            # print("b_p", p_arr)
            # print("b_p_id_arr", p_id_arr)
            for productid in product_arr:
                condition2 = Q(commodity_id=commodity_id) & Q(product_id=productid) & Q(status=1)
                cmp = CommodityProductMaping.objects.using(self._current_app_schema()).filter(condition2)
                if len(cmp) > 0:
                    for i in cmp:
                        cp_arr.append(i.product_id)
                        cp_id_arr.append(i.id)
                continue
            # print("cp", cp_arr)
            # print("cp_id_arr", cp_id_arr)
            for a in p_id_arr:
                if a not in cp_id_arr:
                    print("Inactive CommodityProductMaping id", a)
                    cmp1 = CommodityProductMaping.objects.using(self._current_app_schema()).get(id=a)
                    cmp1.status = 0
                    cmp1.updated_date = now()
                    cmp1.updated_by = emp_id
                    cmp1.save()

            for p in product_arr:
                if p not in cp_arr:
                    # comm = commodity_service.search_commoditycode(commodity_code)
                    # if (isinstance(comm, Error)):
                    #     logger.error(comm.get())
                    #     return comm
                    # commodity_id = comm.id
                    CommodityProductMaping.objects.using(self._current_app_schema()).create(commodity_id=commodity_id,
                                                          product_id=p,
                                                          created_by=emp_id)
            logger.error("success")
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj

        except Exception as e:
            logger.error(e)
            import traceback
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_COMMODITYPRODUCTMAPING_ID)
            error_obj.set_description(ErrorDescription.INVALID_COMMODITYPRODUCTMAPING_ID)
            return error_obj

    def delete_cpmap(self, cpmap_id, emp_id):
        cpmap = CommodityProductMaping.objects.using(self._current_app_schema()).filter(id=cpmap_id).delete()
        self.audit_function(cpmap, cpmap_id, cpmap_id, emp_id, PrModifyStatus.DELETE, PrRefType.COMMODITYPRODUCTMAPING)
        if cpmap[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_COMMODITYPRODUCTMAPING_ID)
            error_obj.set_description(ErrorDescription.INVALID_COMMODITYPRODUCTMAPING_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def fetch_cpmap_list(self, vys_page, emp_id, request):
        cpmap_list = CommodityProductMaping.objects.using(self._current_app_schema()).all().order_by('-created_date')[
                     vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(cpmap_list)
        cpmap_list_data = NWisefinList()
        p_arr = []
        c_arr = []
        if list_length > 0:
            for i in cpmap_list:
                p_arr.append(i.product_id)
                c_arr.append(i.commodity_id)
        master_apicall = ApiService()
        product_data = master_apicall.get_product(request, p_arr)
        commodity_data = master_apicall.get_commodity(request, c_arr)
        if list_length <= 0:
            pass
        else:
            for cpMap in cpmap_list:
                cpMap_data = CommodityProductMapResponse()
                cpMap_data.set_id(cpMap.id)
                cpMap_data.set_product(cpMap.product_id, product_data['data'])
                cpMap_data.set_commodity(commodity_data['data'])
                cpmap_list_data.append(cpMap_data)
            vpage = NWisefinPaginator(cpmap_list, vys_page.get_index(), 10)
            cpmap_list_data.set_pagination(vpage)
        return cpmap_list_data

    def fetch_cpmap(self, cpmap_id, request):
        try:
            cpMap = CommodityProductMaping.objects.using(self._current_app_schema()).get(id=cpmap_id)
            cpMap_data = CommodityProductMapResponse()
            cpMap_data.set_id(cpMap.id)
            master_apicall = ApiService(self._scope())
            master_product = master_apicall.fetch_productdata(request, cpMap.product_id)
            cpMap_data.product=master_product
            master_commodity = master_apicall.fetch_commoditydata(request, cpMap.commodity_id)
            cpMap_data.set_commodity(master_commodity)
            return cpMap_data
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_COMMODITYPRODUCTMAPING_ID)
            error_obj.set_description(ErrorDescription.INVALID_COMMODITYPRODUCTMAPING_ID)
            return error_obj

    def commodity_product(self, commodity_id, name, category, vys_page, request):
        cpMap_list = CommodityProductMaping.objects.using(self._current_app_schema()).filter(commodity_id=commodity_id)
        cp_len = len(cpMap_list)
        c_id = []
        p_id = []
        mep_list_data = NWisefinList()
        master_apicall = ApiService()
        if cp_len > 0:
            for cpMap in cpMap_list:
                if cpMap.id not in c_id:
                    c_id.append(cpMap.id)
                    p_id.append(cpMap.product_id)
            if (category is None) | (category == ''):
                if (name is None) | (name == ''):
                    print("commodity cat_resp --name is none ")

                    productcat_data = master_apicall.productcat_list(request, p_id)
                    print("cat_resp --name is none : ",productcat_data)
                    print("pp: ", productcat_data['data'])
                    resp1 = productcat_data['data'][0]
                    # print(resp1, "r1")
                    resp2=resp1['id']
                    # print("r2", resp2)
                    for pdtcat in resp2:
                        pdtcat_data = master_apicall.fetch_productcatdata(request, pdtcat)
                        # print("cat_resp: ", pdtcat_data)
                        mep_data = MepResponse()
                        mep_data.set_id(pdtcat_data['id'])
                        mep_data.set_name(pdtcat_data['name'])
                        mep_list_data.append(mep_data)
                    return mep_list_data
                else:
                    print("commodity cat_resp ---name is given ")
                    producttype_data = master_apicall.get_productcat(request, p_id, name)
                    print("producttype_data", producttype_data)
                    # print("commodity type_resp ---name : ", producttype_data)
                    resp1 = producttype_data['data'][0]
                    resp2 = resp1['id']
                    for pdtcat in resp2:
                        pdtcat_data = master_apicall.fetch_productcatdata(request, pdtcat)
                        # print("cat_resp: ", pdtcat_data)
                        mep_data = MepResponse()
                        mep_data.set_id(pdtcat_data['id'])
                        mep_data.set_name(pdtcat_data['name'])
                        mep_list_data.append(mep_data)
                    return mep_list_data
            else:
                if (name is None) | (name == ''):
                    print("commodity type_resp name is none")
                    producttype_data = master_apicall.get_producttype(request, p_id, category)
                    print(producttype_data)
                    print("commodity type_resp --- : ", producttype_data)
                    resp1 = producttype_data['data'][0]
                    resp2 = resp1['id']
                    for pdttype in resp2:
                        pdtcat_data = master_apicall.fetch_producttypedata(request, pdttype)
                        # print("cat_resp: ", pdtcat_data)
                        mep_data = MepResponse()
                        mep_data.set_id(pdtcat_data['id'])
                        mep_data.set_name(pdtcat_data['name'])
                        mep_list_data.append(mep_data)
                    # print("product_pdttype: ", mep_list_data.get())
                    return mep_list_data
                else:
                    print("commodity type_resp ---name is given")
                    master_apicall = ApiService()
                    producttype_data = master_apicall.get_producttype_name(request, p_id, category, name)
                    print(producttype_data)
                    # print("commodity type_resp ---name : ", producttype_data)
                    resp1 = producttype_data['data'][0]
                    resp2 = resp1['id']
                    for pdttype in resp2:
                        pdtcat_data = master_apicall.fetch_producttypedata(request, pdttype)
                        # print("cat_resp: ", pdtcat_data)
                        mep_data = MepResponse()
                        mep_data.set_id(pdtcat_data['id'])
                        mep_data.set_name(pdtcat_data['name'])
                        mep_list_data.append(mep_data)
                    return mep_list_data
        return mep_list_data
