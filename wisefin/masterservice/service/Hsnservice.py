import json
import traceback
from django.db.models import Q
import django

from django.db import IntegrityError
from django.db.models import Q

from masterservice.data.response.Hsnresponse import HsnResponse
from masterservice.data.response.taxrate_response import TaxRateResponse
from masterservice.service.Codegenerator import CodeGen
from utilityservice.data.response.nwisefinlist import NWisefinList
from masterservice.models import Hsn, TaxRate
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from django.utils import timezone
from django.utils.timezone import now
from masterservice.data.request.masterauditrequest import MasterAuditRequest
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.util.masterutil import ModifyStatus, MasterRefType, RequestStatusUtil, Code_Gen_Type, Code_Gen_Value
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from nwisefin.settings import logger
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from masterservice.data.response.taxrateresponse import TaxRateResponse

class Hsnservice(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_hsn(self, hsn_obj, emp_id):
        if not hsn_obj.get_id() is None:
            try:
                logger.error('HSN: Hsn Update Started')
                hsn_update = Hsn.objects.using(self._current_app_schema()).filter(id=hsn_obj.get_id(),
                                                                                  entity_id=self._entity_id()).update(
                    code=hsn_obj.get_code(),
                    description=hsn_obj.get_description(),
                    cgstrate=hsn_obj.get_cgstrate(),
                    sgstrate=hsn_obj.get_sgstrate(),
                    igstrate=hsn_obj.get_igstrate(),
                    cgstrate_id=hsn_obj.get_cgstrate_id(),
                    sgstrate_id=hsn_obj.get_sgstrate_id(),
                    igstrate_id=hsn_obj.get_igstrate_id(),
                    updated_by=emp_id,
                    updated_date=timezone.now()
                )

                hsn = Hsn.objects.using(self._current_app_schema()).get(id=hsn_obj.get_id(),
                                                                        entity_id=self._entity_id())
                logger.error('HSN: Hsn Update Success' + str(hsn_update))
                hsn_auditdata = {'id': hsn_obj.get_id(),
                                 # 'code': hsn_obj.get_code(),
                                 'description': hsn_obj.get_description(),
                                 'cgstrate': hsn_obj.get_cgstrate(),
                                 'sgstrate': hsn_obj.get_sgstrate(),
                                 'igstrate': hsn_obj.get_igstrate(),
                                 'cgstrate_id': hsn_obj.get_cgstrate_id(),
                                 'sgstrate_id': hsn_obj.get_sgstrate_id(),
                                 'igstrate_id': hsn_obj.get_igstrate_id(),
                                 'updated_date': timezone.now(),
                                 'updated_by': emp_id}
                self.audit_function(hsn_auditdata, emp_id, hsn.id, ModifyStatus.update)
                data = NWisefinSuccess()
                data.set_status(SuccessStatus.SUCCESS)
                data.set_message(SuccessMessage.UPDATE_MESSAGE)
                return data
            except IntegrityError as error:
                logger.error('ERROR_Hsn_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return
            except Hsn.DoesNotExist:
                logger.error('ERROR_Hsn_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_HSN_ID)
                error_obj.set_description(ErrorDescription.INVALID_HSN_ID)
                return error_obj
            except:
                logger.error('ERROR_Hsn_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('HSN: Hsn Creation Started')
                data_len = Hsn.objects.using(self._current_app_schema()).filter(
                    cgstrate=hsn_obj.get_cgstrate(),
                    sgstrate=hsn_obj.get_sgstrate(),
                    igstrate=hsn_obj.get_igstrate()).values()
                if (len(data_len) > 0):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                    return error_obj
                hsn = Hsn.objects.using(self._current_app_schema()).create(code=hsn_obj.get_code(),
                    description=hsn_obj.get_description(),
                    cgstrate=hsn_obj.get_cgstrate(),
                    sgstrate=hsn_obj.get_sgstrate(),
                    igstrate=hsn_obj.get_igstrate(),
                    cgstrate_id=hsn_obj.get_cgstrate_id(),
                    sgstrate_id=hsn_obj.get_sgstrate_id(),
                    igstrate_id=hsn_obj.get_igstrate_id(),
                    created_by=emp_id, entity_id=self._entity_id())

                logger.error('HSN: Hsn Creation Success' + str(hsn))
                self.audit_function(hsn, emp_id, hsn.id, ModifyStatus.create)
                data = NWisefinSuccess()
                data.set_status(SuccessStatus.SUCCESS)
                data.set_message(SuccessMessage.CREATE_MESSAGE)
                return data
            except IntegrityError as error:
                logger.error('ERROR_Hsn_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_Hsn_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        # hsn_res = HsnResponse()
        # hsn_res.set_id(hsn.id)
        # hsn_res.set_code(hsn.code)
        # hsn_res.set_description(hsn.description)
        # hsn_res.set_cgstrate(hsn.cgstrate)
        # hsn_res.set_sgstrate(hsn.sgstrate)
        # hsn_res.set_igstrate(hsn.igstrate)
        # hsn_res.set_cgstrate_id(hsn.cgstrate_id)
        # hsn_res.set_sgstrate_id(hsn.sgstrate_id)
        # hsn_res.set_igstrate_id(hsn.igstrate_id)
        # # return hsn_res
        # data = NWisefinSuccess()
        # data.set_status(SuccessStatus.SUCCESS)
        # data.set_message(SuccessMessage.CREATE_MESSAGE)
        # return data

    def hsn_taxrateget(self, request, vys_page):
        condition = Q()
        if "data" in request.GET:
            condition &= Q(name__icontains=request.GET.get("data"))|Q(rate__icontains=request.GET.get("data"))
        hsn_data = TaxRate.objects.using(self._current_app_schema()).filter(condition).values('id', 'name', 'code', 'rate')[
               vys_page.get_offset():vys_page.get_query_limit()]
        # print(data)
        tax_list_data = NWisefinList()
        list_data = len(hsn_data)
        if list_data <= 0:
            vpage = NWisefinPaginator(hsn_data, vys_page.get_index(), 10)
            tax_list_data.set_pagination(vpage)
            return tax_list_data
        else:
            for i in hsn_data:
                #print(i)
                response = TaxRateResponse()
                response.set_id(i['id'])
                response.set_code(i['code'])
                response.set_name(i['name']+"-"+str(i['rate']))
                response.set_rate(i['rate'])
                tax_list_data.append(response)
            vpage = NWisefinPaginator(hsn_data, vys_page.get_index(), 10)
            tax_list_data.set_pagination(vpage)
            return tax_list_data
    def fetch_hsn(self, hsn_id):
        try:
            hsn = Hsn.objects.using(self._current_app_schema()).get(id=hsn_id, entity_id=self._entity_id())
            hsn_res = HsnResponse()
            hsn_res.set_id(hsn.id)
            hsn_res.set_code(hsn.code)
            hsn_res.set_description(hsn.description)
            hsn_res.set_cgstrate(hsn.cgstrate)
            hsn_res.set_sgstrate(hsn.sgstrate)
            hsn_res.set_igstrate(hsn.igstrate)
            hsn_res.set_cgstrate_id(hsn.cgstrate_id)
            hsn_res.set_sgstrate_id(hsn.sgstrate_id)
            hsn_res.set_igstrate_id(hsn.igstrate_id)
            return hsn_res
        except Hsn.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_HSN_ID)
            error_obj.set_description(ErrorDescription.INVALID_HSN_ID)
            return error_obj

    # list all
    def fetch_hsn_list(self, vys_page):
        try:
            obj = Hsn.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())[
                  vys_page.get_offset():vys_page.get_query_limit()]
            list_len = len(obj)
            fetch_hsn_list = NWisefinList()
            if list_len <= 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_HSN_ID)
                error_obj.set_description(ErrorDescription.INVALID_HSN_ID)
                return error_obj
            else:
                for hsn in obj:
                    hsn_res = HsnResponse()
                    hsn_res.set_id(hsn.id)
                    hsn_res.set_code(hsn.code)
                    hsn_res.set_description(hsn.description)
                    hsn_res.set_cgstrate(hsn.cgstrate)
                    hsn_res.set_sgstrate(hsn.sgstrate)
                    hsn_res.set_igstrate(hsn.igstrate)
                    hsn_res.set_cgstrate_id(hsn.cgstrate_id)
                    hsn_res.set_sgstrate_id(hsn.sgstrate_id)
                    hsn_res.set_igstrate_id(hsn.igstrate_id)
                    hsn_res.set_status(hsn.status)
                    fetch_hsn_list.append(hsn_res)
                vpage = NWisefinPaginator(obj, vys_page.get_index(), 10)
                fetch_hsn_list.set_pagination(vpage)
                return fetch_hsn_list
        except:
            logger.error('ERROR_HSN_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_HSN_ID)
            error_obj.set_description(ErrorDescription.INVALID_HSN_ID)
            return error_obj


    def delete_hsn(self, hsn_id, emp_id):
        temp = Hsn.objects.using(self._current_app_schema()).filter(id=hsn_id, entity_id=self._entity_id()).delete()
        self.audit_function(temp, emp_id, hsn_id, ModifyStatus.delete)
        if temp[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_HSN_ID)
            error_obj.set_description(ErrorDescription.INVALID_HSN_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

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
        audit_obj.set_relreftype(MasterRefType.HSN)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return

    def search_hsn(self, query, vys_page):
        if query is None:
            hsnlist = Hsn.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by(
                'created_date')[
                      vys_page.get_offset():vys_page.get_query_limit()]
        else:
            hsnlist = Hsn.objects.using(self._current_app_schema()).filter(code__icontains=query,
                                                                           entity_id=self._entity_id()).order_by(
                'created_date')[
                      vys_page.get_offset():vys_page.get_query_limit()]
        hsn_list_data = NWisefinList()
        for hsn in hsnlist:
            hsn_res = HsnResponse()
            hsn_res.set_id(hsn.id)
            hsn_res.set_code(hsn.code)
            hsn_res.set_description(hsn.description)
            hsn_res.set_cgstrate(hsn.cgstrate)
            hsn_res.set_sgstrate(hsn.sgstrate)
            hsn_res.set_igstrate(hsn.igstrate)
            hsn_res.set_cgstrate_id(hsn.cgstrate_id)
            hsn_res.set_sgstrate_id(hsn.sgstrate_id)
            hsn_res.set_igstrate_id(hsn.igstrate_id)
            hsn_res.set_status(hsn.status)
            hsn_list_data.append(hsn_res)
            vpage = NWisefinPaginator(hsnlist, vys_page.get_index(), 10)
            hsn_list_data.set_pagination(vpage)
        return hsn_list_data


    def create_hsn_mtom(self, hsn_obj,action, emp_id):
        logger.error("hsn_obj."+str(hsn_obj.get_cgstrate_code())+str(hsn_obj.get_sgstrate_code())+str(hsn_obj.get_igstrate_code()))


        if action == 'active' or action == 'inactive':
            try:
                hsn_update = Hsn.objects.using(self._current_app_schema()).filter(code=hsn_obj.get_code()).update(
                    status=hsn_obj.get_status(),
                    updated_date=timezone.now(),
                    updated_by=emp_id)
                hsn = Hsn.objects.using(self._current_app_schema()).get(code=hsn_obj.get_code())
                product_update_auditdata = {'id': hsn.id,
                                            'code': hsn_obj.get_code(),
                                            'status': hsn_obj.get_status(),
                                            'updated_date': timezone.now(),
                                            'updated_by': emp_id}
                self.audit_function(product_update_auditdata, emp_id, hsn.id, ModifyStatus.update)
                logger.error("hsn mtom updated " +str(hsn_obj.get_code()))
            except Exception as excep:
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(str(excep))
                return error_obj


        if action=='update':
            try:
                cgstrate_id = TaxRate.objects.using(self._current_app_schema()).filter(code=hsn_obj.get_cgstrate_code())[0].id
                sgstrate_id = TaxRate.objects.using(self._current_app_schema()).filter(code=hsn_obj.get_sgstrate_code())[0].id
                igstrate_id = TaxRate.objects.using(self._current_app_schema()).filter(code=hsn_obj.get_igstrate_code())[0].id
                hsn_update=Hsn.objects.using(self._current_app_schema()).filter(code=hsn_obj.get_code()).update(code=hsn_obj.get_code(),
                                                                          #status=hsn_obj.get_status(),
                                                                          description=hsn_obj.get_description(),
                                                                          cgstrate=hsn_obj.get_cgstrate(),
                                                                          sgstrate=hsn_obj.get_sgstrate(),
                                                                          igstrate=hsn_obj.get_igstrate(),
                                                                          cgstrate_id=cgstrate_id,
                                                                          sgstrate_id=sgstrate_id,
                                                                          igstrate_id=igstrate_id,
                                                                          updated_by = emp_id,
                                                                          updated_date=timezone.now()
                                                                                        )

                hsn=Hsn.objects.using(self._current_app_schema()).get(code=hsn_obj.get_code())
                hsn_auditdata = {'id': hsn.id,
                                 'code': hsn_obj.get_code(),
                                 'description': hsn_obj.get_description(),
                                 'cgstrate': hsn_obj.get_cgstrate(),
                                 'sgstrate': hsn_obj.get_sgstrate(),
                                 'igstrate': hsn_obj.get_igstrate(),
                                 'cgstrate_id': cgstrate_id,
                                 'sgstrate_id': sgstrate_id,
                                 'igstrate_id': igstrate_id,
                                 'updated_date': timezone.now(),
                                 'updated_by': emp_id}
                self.audit_function(hsn_auditdata, emp_id, hsn.id, ModifyStatus.update)

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return

            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                cgstrate_id = TaxRate.objects.using(self._current_app_schema()).filter(code=hsn_obj.get_cgstrate_code())[0].id
                sgstrate_id = TaxRate.objects.using(self._current_app_schema()).filter(code=hsn_obj.get_sgstrate_code())[0].id
                igstrate_id = TaxRate.objects.using(self._current_app_schema()).filter(code=hsn_obj.get_igstrate_code())[0].id
                hsn=Hsn.objects.create(code=hsn_obj.get_code(),
                                        description=hsn_obj.get_description(),
                                        cgstrate=hsn_obj.get_cgstrate(),
                                        sgstrate=hsn_obj.get_sgstrate(),
                                        igstrate=hsn_obj.get_igstrate(),
                                        cgstrate_id=cgstrate_id,
                                        sgstrate_id=sgstrate_id,
                                        igstrate_id=igstrate_id,
                                        created_by=emp_id)

                self.audit_function(hsn, emp_id, hsn.id, ModifyStatus.create)
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

        hsn_res=HsnResponse()
        hsn_res.set_id(hsn.id)
        hsn_res.set_code(hsn.code)
        hsn_res.set_description(hsn.description)
        hsn_res.set_cgstrate(hsn.cgstrate)
        hsn_res.set_sgstrate(hsn.sgstrate)
        hsn_res.set_igstrate(hsn.igstrate)
        hsn_res.set_cgstrate_id(hsn.cgstrate_id)
        hsn_res.set_sgstrate_id(hsn.sgstrate_id)
        hsn_res.set_igstrate_id(hsn.igstrate_id)
        return hsn_res

    def search_hsncode(self, query, vys_page):
        if query is None:
            hsnlist = Hsn.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by(
                'created_date')[
                      vys_page.get_offset():vys_page.get_query_limit()]
        else:
            hsnlist = Hsn.objects.using(self._current_app_schema()).filter(code__icontains=query,
                                                                           entity_id=self._entity_id()).order_by(
                'created_date')[
                      vys_page.get_offset():vys_page.get_query_limit()]
        hsn_list_data = NWisefinList()
        for hsn in hsnlist:
            hsn_res = HsnResponse()
            hsn_res.set_id(hsn.id)
            hsnrate = str(hsn.igstrate)
            hsncode = hsn.code + '-' + hsnrate
            hsn_res.set_code(hsncode)
            hsn_res.set_description(hsn.description)
            hsn_res.set_cgstrate(hsn.cgstrate)
            hsn_res.set_sgstrate(hsn.sgstrate)
            hsn_res.set_igstrate(hsn.igstrate)
            hsn_res.set_cgstrate_id(hsn.cgstrate_id)
            hsn_res.set_sgstrate_id(hsn.sgstrate_id)
            hsn_res.set_igstrate_id(hsn.igstrate_id)
            hsn_list_data.append(hsn_res)
            vpage = NWisefinPaginator(hsnlist, vys_page.get_index(), 10)
            hsn_list_data.set_pagination(vpage)
        return hsn_list_data

    # Get hsn
    def fetch_hsnone(self, query):
        x = query
        y = x.split("-")
        code = y[0]
        hsn1 = Hsn.objects.using(self._current_app_schema()).filter(code=code, entity_id=self._entity_id())
        if len(hsn1) != 0:
            hsn = hsn1[0]
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj
        hsn_data = {"id": hsn.id, "code": hsn.code, "cgstrate": hsn.cgstrate, "sgstrate": hsn.sgstrate,
                    "igstrate": hsn.igstrate}
        hsn_dic = json.dumps(hsn_data, indent=4)
        return hsn_data


    # def hsn_taxrateget(self, request, vys_page):
    #     condition = Q()
    #     if "data" in request.GET:
    #         condition &= Q(name__icontains=request.GET.get("data"))|Q(rate__icontains=request.GET.get("data"))
    #     hsn_data = TaxRate.objects.using(self._current_app_schema()).filter(condition).values('id', 'name', 'code', 'rate')[
    #            vys_page.get_offset():vys_page.get_query_limit()]
    #     # print(data)
    #     tax_list_data = NWisefinList()
    #     list_data = len(hsn_data)
    #     if list_data <= 0:
    #         vpage = NWisefinPaginator(hsn_data, vys_page.get_index(), 10)
    #         tax_list_data.set_pagination(vpage)
    #         return tax_list_data
    #     else:
    #         for i in hsn_data:
    #             # print(i)
    #             response = TaxRateResponse()
    #             response.set_id(i['id'])
    #             response.set_code(i['code'])
    #             response.set_name(i['name'])
    #             response.set_rate(i['rate'])
    #             tax_list_data.append(response)
    #         vpage = NWisefinPaginator(hsn_data, vys_page.get_index(), 10)
    #         tax_list_data.set_pagination(vpage)
    #         return tax_list_data


    def hsn_activate_inactivate(self, request,hsn_obj):

        if (int(hsn_obj.status) == 0):

            hsn_data = Hsn.objects.using(self._current_app_schema()).filter(id=hsn_obj.id).update(
                status=1)
        else:
            hsn_data = Hsn.objects.using(self._current_app_schema()).filter(id=hsn_obj.id).update(
                status=0)
        hsn_var = Hsn.objects.using(self._current_app_schema()).get(id=hsn_obj.id)
        data = HsnResponse()
        data.set_status(hsn_var.status)
        status = hsn_var.status

        data.set_id(hsn_var.id)

        if status == 1:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.ACTIVATED)
            return data
        else:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.INACTIVATED)
            return data
    def hsn_iddata(self,request,id):
        obj = Hsn.objects.using(self._current_app_schema()).filter(id=int(id))
        list_len = len(obj)
        fetch_hsn_list = NWisefinList()
        if list_len <= 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_HSN_ID)
            error_obj.set_description(ErrorDescription.INVALID_HSN_ID)
            return error_obj
        else:
            for hsn in obj:
                hsn_res = HsnResponse()
                hsn_res.set_id(hsn.id)
                hsn_res.set_code(hsn.code)
                hsn_res.set_description(hsn.description)
                hsn_res.set_cgstrate(hsn.cgstrate)
                hsn_res.set_sgstrate(hsn.sgstrate)
                hsn_res.set_igstrate(hsn.igstrate)
                hsn_res.set_cgstrate_id(hsn.cgstrate_id)
                cgstid=hsn.cgstrate_id
                cgst_data=TaxRate.objects.using(self._current_app_schema()).get(id=cgstid)
                hsn_res.set_cgstname(cgst_data.name)

                hsn_res.set_sgstrate_id(hsn.sgstrate_id)
                sgstid=hsn.sgstrate_id
                sgst_data = TaxRate.objects.using(self._current_app_schema()).get(id=sgstid)
                hsn_res.set_sgstname(sgst_data.name)
                hsn_res.set_igstrate_id(hsn.igstrate_id)
                igst_data=hsn.igstrate_id
                igst_data = TaxRate.objects.using(self._current_app_schema()).get(id=igst_data)
                hsn_res.set_igstname(igst_data.name)
                hsn_res.set_status(hsn.status)
                fetch_hsn_list.append(hsn_res)

            return fetch_hsn_list


    def fetch_hsn_list_download(self, vys_page):
        try:
            obj = Hsn.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())
            list_len = len(obj)
            fetch_hsn_list = NWisefinList()
            if list_len <= 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_HSN_ID)
                error_obj.set_description(ErrorDescription.INVALID_HSN_ID)
                return error_obj
            else:
                for hsn in obj:
                    hsn_res = HsnResponse()
                    hsn_res.set_id(hsn.id)
                    hsn_res.set_code(hsn.code)
                    hsn_res.set_description(hsn.description)
                    hsn_res.set_cgstrate(hsn.cgstrate)
                    hsn_res.set_sgstrate(hsn.sgstrate)
                    hsn_res.set_igstrate(hsn.igstrate)
                    hsn_res.set_cgstrate_id(hsn.cgstrate_id)
                    hsn_res.set_sgstrate_id(hsn.sgstrate_id)
                    hsn_res.set_igstrate_id(hsn.igstrate_id)
                    hsn_res.set_status(hsn.status)
                    fetch_hsn_list.append(hsn_res)
                return fetch_hsn_list
        except:
            logger.error('ERROR_HSN_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_HSN_ID)
            error_obj.set_description(ErrorDescription.INVALID_HSN_ID)
            return error_obj

