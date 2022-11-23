import traceback

from django.db import IntegrityError
from django.db.models import Q
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.service.Codegenerator import CodeGen
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.util.masterutil import ModifyStatus, MasterRefType, RequestStatusUtil, Code_Gen_Type, Code_Gen_Value, \
    MasterStatus
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessMessage, SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from datetime import datetime
import json

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

now = datetime.now()
now = str(now)
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from masterservice.models import Commodity, Product,CommodityProductMaping
from masterservice.data.response.commodityresponse import CommodityResponse, CommodityProductMapResponse


class CommodityService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_Commodity(self, commodity_obj, emp_id):
        if not commodity_obj.get_id() is None:
            try:
                logger.error('COMMODITY: Commodity Update Started')
                commodity_var = Commodity.objects.using(self._current_app_schema()).filter(id=commodity_obj.get_id(),
                                                                                           entity_id=self._entity_id()).update(
                    name=commodity_obj.get_name(), description=commodity_obj.get_description(),
                    updated_by=emp_id,
                    updated_date=now)
                commodity = Commodity.objects.using(self._current_app_schema()).get(id=commodity_obj.get_id(),
                                                                                    entity_id=self._entity_id())
                logger.error('COMMODITY: Commodity Update Success' + str(commodity_var))
                commodity_auditdata = {'id': commodity_obj.get_id(),
                                       'name': commodity_obj.get_name(),
                                       'updated_date': now,
                                       'updated_by': emp_id}
                self.audit_function(commodity_auditdata, emp_id, commodity.id, ModifyStatus.update)

            except IntegrityError as error:
                logger.error('ERROR_Commodity_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Commodity.DoesNotExist:
                logger.error('ERROR_Commodity_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_COMMODITY_ID)
                error_obj.set_description(ErrorDescription.INVALID_COMMODITY_ID)
                return error_obj
            except:
                logger.error('ERROR_Commodity_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        else:
            condition = Q(name__exact=commodity_obj.get_name()) & Q(entity_id=self._entity_id())
            commodity = Commodity.objects.using(self._current_app_schema()).filter(condition)
            if len(commodity) > 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                return error_obj
            try:
                logger.error('COMMODITY: Commodity Creation Started')
                commodity = Commodity.objects.using(self._current_app_schema()).create(name=commodity_obj.get_name(),
                                                                                       description=commodity_obj.get_description(),
                                                                                       created_by=emp_id,
                                                                                       entity_id=self._entity_id())
                try:
                    max_cat_code = \
                    Commodity.objects.using(self._current_app_schema()).filter(code__icontains='CUS').order_by(
                        '-code')[0].code
                    rnsl = int(max_cat_code[3:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "CUS" + str(new_rnsl).zfill(3)  # code = "COMD" + str(commdity_code)
                commodity.code = code
                commodity.save()
                self.audit_function(commodity, emp_id, commodity.id, ModifyStatus.create)
                logger.error('COMMODITY: Commodity Creation Success' + str(commodity))
            except IntegrityError as error:
                logger.error('ERROR_Commodity_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_Commodity_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        commodity_data = CommodityResponse()
        commodity_data.set_id(commodity.id)
        commodity_data.set_code(commodity.code)
        commodity_data.set_status(commodity.status)
        commodity_data.set_name(commodity.name)
        return commodity_data

    def delete_Commodity(self, commodity_id, emp_id):
        commodity = Commodity.objects.using(self._current_app_schema()).filter(id=commodity_id,
                                                                               entity_id=self._entity_id()).delete()
        self.audit_function(commodity, emp_id, commodity_id, ModifyStatus.delete)
        if commodity[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_COMMODITY_ID)
            error_obj.set_description(ErrorDescription.INVALID_COMMODITY_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def fetch_Commodity(self, commodity_id, emp_id):
        try:
            commodity = Commodity.objects.using(self._current_app_schema()).get(id=commodity_id,
                                                                                entity_id=self._entity_id())
            commodity_data = CommodityResponse()
            commodity_data.set_id(commodity.id)
            commodity_data.set_code(commodity.code)
            commodity_data.set_name(commodity.name)
            commodity_data.set_status(commodity.status)
            return commodity_data
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_COMMODITY_ID)
            error_obj.set_description(ErrorDescription.INVALID_COMMODITY_ID)
            return error_obj

    def fetch_Commodity_list(self, request, vys_page, emp_id):
        try:
            condition = Q(entity_id=self._entity_id())
            if "query" in request.GET:
                condition &= Q(name__icontains=request.GET.get("query"))
            commodity_list = Commodity.objects.using(self._current_app_schema()).filter(condition).order_by('id')[
                             vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(commodity_list)
            commodity_list_data = NWisefinList()
            if list_length > 0:
                for commodity in commodity_list:
                    commodity_data = CommodityResponse()
                    commodity_data.set_id(commodity.id)
                    commodity_data.set_code(commodity.code)
                    commodity_data.set_name(commodity.name)
                    commodity_data.set_status(commodity.status)
                    commodity_data.set_description(commodity.description)
                    commodity_list_data.append(commodity_data)
                vpage = NWisefinPaginator(commodity_list, vys_page.get_index(), 10)
                commodity_list_data.set_pagination(vpage)
            return commodity_list_data
        except:
            logger.error('ERROR_Commodity_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_COMMODITY_ID)
            error_obj.set_description(ErrorDescription.INVALID_COMMODITY_ID)
            return error_obj
    def fetch_commodity_download(self, request, emp_id):
        try:
            condition = Q(entity_id=self._entity_id())
            if "query" in request.GET:
                condition &= Q(name__icontains=request.GET.get("query"))
            commodity_list = Commodity.objects.using(self._current_app_schema()).filter(condition).order_by('id')
            list_length = len(commodity_list)
            commodity_list_data = NWisefinList()
            if list_length > 0:
                for commodity in commodity_list:
                    commodity_data = CommodityResponse()
                    commodity_data.Code = commodity.code
                    commodity_data.Name = commodity.name
                    status = MasterStatus()
                    if commodity.status == status.Active:
                        commodity_data.Status = status.Active_VALUE
                    if commodity.status == status.Inactive:
                        commodity_data.Status = status.Inactive_VALUE
                    commodity_data.Description = commodity.description
                    commodity_list_data.append(commodity_data)
            return commodity_list_data
        except:
            logger.error('ERROR_Commodity_Excel_Download_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_COMMODITY_ID)
            error_obj.set_description(ErrorDescription.INVALID_COMMODITY_ID)
            return error_obj


    def audit_function(self, data_obj, user_id, id, action):
        if action == ModifyStatus.delete:
            data = None
        elif action == ModifyStatus.update:
            data = data_obj
        else:
            data = data_obj.__dict__
            del data['_state']
        audit_service = MasterAuditService(self._scope())  # changed
        audit_obj = MasterAuditResponse()
        audit_obj.set_refid(-1)
        audit_obj.set_reftype(MasterRefType.MASTER)
        audit_obj.set_userid(user_id)
        audit_obj.set_reqstatus(RequestStatusUtil.ONBOARD)
        audit_obj.set_relrefid(id)
        audit_obj.set_relreftype(MasterRefType.COMMODITY)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return

    def search_CommodityAll(self, vys_page, query):
        name = query.get('name')
        code = query.get('code')
        condition = Q(name__icontains=name) & Q(code__icontains=code) & Q(entity_id=self._entity_id())

        commodity_list = Commodity.objects.using(self._current_app_schema()).filter(condition)[
                         vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(commodity_list)
        commodity_list_data = NWisefinList()
        if list_length > 0:
            for commodity in commodity_list:
                commodity_data = CommodityResponse()
                commodity_data.set_id(commodity.id)
                commodity_data.set_code(commodity.code)
                commodity_data.set_name(commodity.name)
                commodity_data.set_status(commodity.status)
                commodity_data.description = commodity.description
                commodity_list_data.append(commodity_data)
            vpage = NWisefinPaginator(commodity_list, vys_page.get_index(), 10)
            commodity_list_data.set_pagination(vpage)
        return commodity_list_data

    def UpdateStatus_Commodity(self, commodity_id, status, emp_id):
        commodity_update = Commodity.objects.using(self._current_app_schema()).filter(id=commodity_id,
                                                                                      entity_id=self._entity_id()).update(
            status=status,
            updated_by=emp_id,
            updated_date=timezone.now())
        self.audit_function(commodity_update, emp_id, commodity_id, ModifyStatus.update)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    def create_Commodity_mtom(self, commodity_obj, emp_id):
        if not commodity_obj.get_id() is None:
            try:
                commodity_var = Commodity.objects.using(self._current_app_schema()).filter(id=commodity_obj.get_id(),
                                                                                           entity_id=self._entity_id()).update(
                    name=commodity_obj.get_name(),
                    code=commodity_obj.get_code(),
                    updated_by=emp_id,
                    updated_date=now)
                commodity = Commodity.objects.using(self._current_app_schema()).get(id=commodity_obj.get_id(),
                                                                                    entity_id=self._entity_id())
                commodity_auditdata = {'id': commodity_obj.get_id(),
                                       'name': commodity_obj.get_name(),
                                       'updated_date': now,
                                       'updated_by': emp_id}
                self.audit_function(commodity_auditdata, emp_id, commodity.id, ModifyStatus.update)

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Commodity.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_COMMODITY_ID)
                error_obj.set_description(ErrorDescription.INVALID_COMMODITY_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        else:
            condition = Q(name__exact=commodity_obj.get_name()) & Q(entity_id=self._entity_id())
            commodity = Commodity.objects.using(self._current_app_schema()).filter(condition)
            if len(commodity) > 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                return error_obj
            try:
                commodity = Commodity.objects.using(self._current_app_schema()).create(name=commodity_obj.get_name(),
                                                                                       code=commodity_obj.get_code(),
                                                                                       created_by=emp_id,
                                                                                       entity_id=self._entity_id())

                self.audit_function(commodity, emp_id, commodity.id, ModifyStatus.create)
            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        commodity_data = CommodityResponse()
        commodity_data.set_id(commodity.id)
        commodity_data.set_code(commodity.code)
        commodity_data.set_status(commodity.status)
        commodity_data.set_name(commodity.name)
        return commodity_data

    def search_commoditycode(self, query):
        condition = Q(code__exact=query) & Q(status=1) & Q(entity_id=self._entity_id())
        try:
            commodity = Commodity.objects.using(self._current_app_schema()).get(condition)
            commodity_data = CommodityResponse()
            commodity_data.set_id(commodity.id)
            commodity_data.set_code(commodity.code)
            commodity_data.set_name(commodity.name)
            commodity_data.set_status(commodity.status)
            return commodity_data
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_COMMODITY_ID)
            error_obj.set_description(ErrorDescription.INVALID_COMMODITY_ID)
            return error_obj

    def search_CommodityName(self, query):
        condition = Q(name__icontains=query) & Q(entity_id=self._entity_id())
        commodity_list = Commodity.objects.using(self._current_app_schema()).filter(condition)
        list_length = len(commodity_list)
        commodity_list_data = NWisefinList()
        if list_length > 0:
            for commodity in commodity_list:
                commodity_data = CommodityResponse()
                commodity_data.set_id(commodity.id)
                commodity_data.set_code(commodity.code)
                commodity_data.set_name(commodity.name)
                commodity_data.set_status(commodity.status)
                commodity_list_data.append(commodity_data)
        return commodity_list_data

    def search_Commodity(self, vys_page, emp_id, query):
        if query is None:
            commodity_id = None
            commodity_list = Commodity.objects.using(self._current_app_schema()).filter(id=commodity_id,
                                                                                        entity_id=self._entity_id())[
                             vys_page.get_offset():vys_page.get_query_limit()]
        else:
            condition = Q(status=1) & Q(name__icontains=query) & Q(entity_id=self._entity_id())
            commodity_list = Commodity.objects.using(self._current_app_schema()).filter(condition)[
                             vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(commodity_list)
        delmat_list_data = NWisefinList()
        if list_length > 0:
            for commodity in commodity_list:
                commodity_data = CommodityResponse()
                commodity_data.set_id(commodity.id)
                commodity_data.set_name(commodity.name)
                delmat_list_data.append(commodity_data)
                vpage = NWisefinPaginator(commodity_list, vys_page.get_index(), 10)
                delmat_list_data.set_pagination(vpage)
            return delmat_list_data
        return delmat_list_data

    def search_commodityname(self, query):
        condition = Q(name__exact=query) & Q(entity_id=self._entity_id())
        try:
            commodity = Commodity.objects.using(self._current_app_schema()).get(condition)
            commodity_data = CommodityResponse()
            commodity_data.set_id(commodity.id)
            commodity_data.set_code(commodity.code)
            commodity_data.set_name(commodity.name)
            commodity_data.set_status(commodity.status)
            return commodity_data
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_COMMODITY_ID)
            error_obj.set_description(ErrorDescription.INVALID_COMMODITY_ID)
            return error_obj

    def fetch_commoditylist(request, commodity_data):
        # commo_id1 = json.loads(request.body)
        print('comodity', commodity_data)
        commo_id2 = commodity_data.get('commo_id1')
        obj = Commodity.objects.using(request._current_app_schema()).filter(id__in=commo_id2,
                                                                            entity_id=request._entity_id()).values('id',
                                                                                                                   'name')
        ecf_list_data = NWisefinList()
        for i in obj:
            data = {"id": i['id'], "name": i['name']}
            ecf_list_data.append(data)
        return ecf_list_data.get()

    def fetch_commoditys(self, commodity_id):
        commodity = Commodity.objects.using(self._current_app_schema()).get(id=commodity_id,
                                                                            entity_id=self._entity_id())
        comm_data = {"id": commodity.id, "code": commodity.code, "name": commodity.name}
        comodity_dic = json.dumps(comm_data, indent=4)
        return comm_data

    def get_commoditycode(self, code):
        try:
            commodity = Commodity.objects.get(code=code, status=1)
            comm_data = {"id": commodity.id, "code": commodity.code, "name": commodity.name}
            return comm_data
        except Commodity.DoesNotExist as e:
            print(e)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_COMMODITY_ID)
            error_obj.set_description(str(e) + ' : ' + str(code))
            return error_obj

    def commodity_get(self, commodity_data):
        commodityId_arr = commodity_data.get('commodity_id')
        commodity = Commodity.objects.using(self._current_app_schema()).filter(id__in=commodityId_arr,
                                                                               entity_id=self._entity_id()).values('id',
                                                                                                                   'code',
                                                                                                                   'name',
                                                                                                                   'status')
        commodity_list_data = NWisefinList()
        for i in commodity:
            data = {"id": i['id'],
                    "code": i['code'],
                    "status": i['status'],
                    "name": i['name']}
            commodity_list_data.append(data)
        return commodity_list_data.get()

    def commodity_name(self, query):
        commodity = Commodity.objects.using(self._current_app_schema()).filter(name__icontains=query,
                                                                               entity_id=self._entity_id())
        commodity_list_data = NWisefinList()
        for i in commodity:
            data = {"id": i.id,
                    "name": i.name}
            commodity_list_data.append(data)
        return commodity_list_data.get()

    def get_commodityname(self, query):
        try:
            commodity = Commodity.objects.using(self._current_app_schema()).get(name=query, entity_id=self._entity_id())
            comm_data = {"id": commodity.id, "code": commodity.code,
                         "name": commodity.name,
                         "status": commodity.status}
            return comm_data
        except Commodity.DoesNotExist as e:
            print(e)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(e) + ' : ' + str(query))
            return error_obj

    def fetch_commoditycode(self, code):
        try:
            commodity = Commodity.objects.get(code=code, status=1)
            commodity_data = CommodityResponse()
            commodity_data.set_id(commodity.id)
            commodity_data.set_code(commodity.code)
            commodity_data.set_name(commodity.name)
            return commodity_data
        except Commodity.DoesNotExist as e:
            print(e)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_COMMODITY_ID)
            error_obj.set_description(str(e) + ' : ' + str(code))
            return error_obj

    # def fetch_CommodityProductMap(self, commodity_id, request):
    #     condition = Q(status=1) & Q(id=commodity_id)
    #     # cpMap_list = CommodityProductMaping.objects.using(self._current_app_schema()).filter(condition)
    #     cpMap_list = Commodity.objects.using(self._current_app_schema()).filter(condition)
    #     list_length = len(cpMap_list)
    #     cpMap_list_data = NWisefinList()
    #     # prod_id=cpMap_list.product_id
    #     # product_data=Product.objects.using(self._current_app_schema()).get(status=1,id=prod_id)
    #
    #     # p_arr = []
    #     # if list_length > 0:
    #     #     for i in cpMap_list:
    #     #         p_arr.append(i.product_id)
    #     # master_apicall = ApiService()
    #     # print(p_arr)
    #     # product_data = master_apicall.get_product(request, p_arr)
    #     if list_length <= 0:
    #         pass
    #     else:
    #         for cpMap in cpMap_list:
    #             prod_id = cpMap.product_id
    #             product_data = Product.objects.using(self._current_app_schema()).get(status=1, id=prod_id)
    #             cpMap_data = CommodityProductMapResponse()
    #             cpMap_data.set_id(cpMap.id)
    #             cpMap_data.set_product(cpMap.product_id)
    #             cpMap_data.set_commodity(cpMap.commodity_id)
    #             cpMap_list_data.append(cpMap_data)
    #     return cpMap_list_data

