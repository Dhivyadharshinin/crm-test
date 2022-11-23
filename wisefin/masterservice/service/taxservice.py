import json
import traceback

from django.db import IntegrityError
from django.db.models import Q

from masterservice.models import Tax,SubTax,TaxRate
from vendorservice.data.response.taxresponse import TaxResponse,TaxsummaryResponse,List
from vendorservice.data.response.subtaxresponse import SubTaxResponse
from vendorservice.data.response.taxrateresponse import TaxRateResponse
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from masterservice.data.request.masterauditrequest import MasterAuditRequest
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.util.masterutil import ModifyStatus,MasterRefType,RequestStatusUtil
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from masterservice.service.Codegenerator import CodeGen


class TaxMasterService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_tax(self, tax_obj, user_id):
        if not tax_obj.get_id() is None:
            try:
                logger.error('TAX: Tax Update Started')
                tax_update = Tax.objects.using(self._current_app_schema()).filter(id=tax_obj.get_id()).update(#code =tax_obj.get_code (),
                name  =tax_obj.get_name  (),receivable =tax_obj.get_receivable (),
                payable =tax_obj.get_payable (),glno =tax_obj.get_glno (),
                updated_by=user_id,updated_date=timezone.now())

                tax = Tax.objects.using(self._current_app_schema()).get(id=tax_obj.get_id())

                taxrate_auditdata = {'id': tax_obj.get_id(),
                                     #'code': tax_obj.get_code(),
                                     'name': tax_obj.get_name(),
                                     'receivable': tax_obj.get_receivable(),
                                     'payable': tax_obj.get_payable(), 'glno': tax_obj.get_glno(),
                                     'updated_date': timezone.now(),
                                     'updated_by': user_id}
                self.audit_function(taxrate_auditdata, user_id, tax.id, ModifyStatus.update)
                logger.error('TAX: Tax Update Success' + str(tax_update))
            except IntegrityError as error:
                logger.error('ERROR_Tax_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Tax.DoesNotExist:
                logger.error('ERROR_Tax_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_tax_ID)
                error_obj.set_description(ErrorDescription.INVALID_tax_ID)
                return error_obj
            except:
                logger.error('ERROR_Tax_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('TAX: Tax Creation Started')
                tax = Tax.objects.using(self._current_app_schema()).create(#code =tax_obj.get_code (),
                name  =tax_obj.get_name  (),receivable =tax_obj.get_receivable (),
                payable =tax_obj.get_payable (),glno =tax_obj.get_glno (),
                created_by =user_id, entity_id=self._entity_id()
                )
                # code = "ISCT" + str(tax.id)
                try:
                    max_cat_code = Tax.objects.using(self._current_app_schema()).filter(code__icontains='TAX').order_by('-code')[0].code
                    rnsl = int(max_cat_code[3:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "TAX" + str(new_rnsl).zfill(3)
                tax.code = code
                tax.save()
                self.audit_function(tax, user_id, tax.id, ModifyStatus.create)
                logger.error('TAX: Tax Creation Success' + str(tax))

            except IntegrityError as error:
                logger.error('ERROR_Tax_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_Tax_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        tax_data = TaxResponse()
        tax_data.set_id(tax.id)
        tax_data.set_code(tax.code)
        tax_data.set_name(tax.name)
        tax_data.set_receivable(tax.receivable)
        tax_data.set_payable(tax.payable)
        tax_data.set_glno(tax.glno)
        # return tax_data
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj
    def fetch_tax_list(self, vys_page):
        taxlist = Tax.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by(
            'created_date')[
                  vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(taxlist)
        if list_length < 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_tax_ID)
            error_obj.set_description(ErrorDescription.INVALID_tax_ID)
            return error_obj
        else:
            tax_list_data = NWisefinList()
            for tax in taxlist:
                tax_data = TaxResponse()
                tax_data.set_id(tax.id)
                tax_data.set_code(tax.code)
                tax_data.set_name(tax.name)
                tax_data.set_receivable(tax.receivable)
                tax_data.set_payable(tax.payable)
                tax_data.set_glno(tax.glno)
                tax_list_data.append(tax_data)
            vpage = NWisefinPaginator(taxlist, vys_page.get_index(), 10)
            tax_list_data.set_pagination(vpage)
            return tax_list_data

    def fetch_tax(self, tax_id, user_id):
        try:
            tax = Tax.objects.using(self._current_app_schema()).get(id=tax_id, entity_id=self._entity_id())
            tax_data = TaxResponse()
            tax_data.set_id(tax.id)
            tax_data.set_code(tax.code)
            tax_data.set_name(tax.name)
            tax_data.set_receivable(tax.receivable)
            tax_data.set_payable(tax.payable)
            tax_data.set_glno(tax.glno)
            return tax_data

        except Tax.DoesNotExist :
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_tax_ID)
            error_obj.set_description(ErrorDescription.INVALID_tax_ID)
            return error_obj

    def delete_tax(self, tax_id, user_id):
        tax = Tax.objects.using(self._current_app_schema()).filter(id=tax_id, entity_id=self._entity_id()).delete()
        self.audit_function(tax, user_id, tax_id, ModifyStatus.delete)

        if tax[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_tax_ID)
            error_obj.set_description(ErrorDescription.INVALID_tax_ID)
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
        audit_obj.set_relreftype(MasterRefType.TAX)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return

    def fetch_tax_search(self, query, vys_page):
        if query is None:
            taxlist = Tax.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by(
                'created_date')[
                      vys_page.get_offset():vys_page.get_query_limit()]
        else:
            taxlist = Tax.objects.using(self._current_app_schema()).filter(name__icontains=query,
                                                                           entity_id=self._entity_id()).order_by(
                'created_date')[
                      vys_page.get_offset():vys_page.get_query_limit()]

        tax_list_data = NWisefinList()
        for tax in taxlist:
            tax_data = TaxResponse()
            tax_data.set_id(tax.id)
            tax_data.set_code(tax.code)
            tax_data.set_name(tax.name)
            tax_list_data.append(tax_data)
            vpage = NWisefinPaginator(taxlist, vys_page.get_index(), 10)
            tax_list_data.set_pagination(vpage)
        return tax_list_data

    def create_tax_mtom(self, tax_obj,action,user_id):

        if action == 'active' or action == 'inactive':
            try:
                tax_update = Tax.objects.using(self._current_app_schema()).filter(code=tax_obj.get_code()).update(
                    status=tax_obj.get_status(),
                    updated_date=timezone.now(),
                    updated_by=user_id)
                tax = Tax.objects.using(self._current_app_schema()).get(code=tax_obj.get_code())
                product_update_auditdata = {'id': tax.id,
                                            'code': tax_obj.get_code(),
                                            'status': tax_obj.get_status(),
                                            'updated_date': timezone.now(),
                                            'updated_by': user_id}
                self.audit_function(product_update_auditdata, user_id, tax.id, ModifyStatus.update)
                logger.error("hsn mtom updated " +str(tax_obj.get_code()))
            except Exception as excep:
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(str(excep))
                return error_obj

        if action =='update':
            try:
                tax_update = Tax.objects.using(self._current_app_schema()).filter(code =tax_obj.get_code()).update(code =tax_obj.get_code(),
                name  =tax_obj.get_name (),
                status  =tax_obj.get_status(),
                receivable =tax_obj.get_receivable (),
                payable =tax_obj.get_payable (),glno =tax_obj.get_glno (),
                updated_by=user_id,updated_date=timezone.now())

                tax = Tax.objects.using(self._current_app_schema()).get(code =tax_obj.get_code())

                taxrate_auditdata = {'id': tax.id,
                                     'code': tax_obj.get_code(),
                                     'name': tax_obj.get_name(),
                                     'receivable': tax_obj.get_receivable(),
                                     'payable': tax_obj.get_payable(), 'glno': tax_obj.get_glno(),
                                     'updated_date': timezone.now(),
                                     'updated_by': user_id}
                self.audit_function(taxrate_auditdata, user_id, tax.id, ModifyStatus.update)

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Tax.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_tax_ID)
                error_obj.set_description(ErrorDescription.INVALID_tax_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        elif action =='create':
            try:
                tax = Tax.objects.using(self._current_app_schema()).create(code =tax_obj.get_code(),
                name  =tax_obj.get_name  (),receivable =tax_obj.get_receivable(),
                payable =tax_obj.get_payable (),glno =tax_obj.get_glno(),
                created_by =user_id, entity_id=self._entity_id())

                self.audit_function(tax, user_id, tax.id, ModifyStatus.create)

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

        tax_data = TaxResponse()
        tax_data.set_id(tax.id)
        tax_data.set_code(tax.code)
        tax_data.set_name(tax.name)
        tax_data.set_receivable(tax.receivable)
        tax_data.set_payable(tax.payable)
        tax_data.set_glno(tax.glno)
        return tax_data

    def new_tax_summmary(self,request,vys_page):
        try:
            condition = Q()
            if "data" in request.GET:
                condition &= Q(name__icontains=request.GET.get("data"))
            tax_details=Tax.objects.using(self._current_app_schema()).filter(condition).order_by('id')
            vyslist=List()
            if len(tax_details)>0:
                for tax_record in tax_details:
                    tax_resp=TaxsummaryResponse()
                    ##set tax details in responsee below this line
                    tax_resp.set_id(tax_record.id)
                    tax_resp.set_name(tax_record.name)
                    tax_resp.receivable=tax_record.receivable
                    tax_resp.glno=tax_record.glno
                    tax_resp.payable=tax_record.payable
                    # print("tax_id",tax_record.id)
                    subtax_details=SubTax.objects.using(self._current_app_schema()).filter(tax_id=tax_record.id)
                    if len(subtax_details)>0:
                        for subtax_record in subtax_details:
                            subtax_resp=SubTaxResponse()
                            subtax_resp.set_id(subtax_record.id)
                            subtax_resp.set_name(subtax_record.name)
                            subtax_resp.set_subtaxamount(subtax_record.subtaxamount)

                            # print("subtax_id",subtax_record.id)
                            taxrate_details=TaxRate.objects.using(self._current_app_schema()).filter(subtax_id=subtax_record.id)
                            # print(taxrate_details)
                            # print(len(taxrate_details))
                            if len(taxrate_details)>0:
                                for taxrate_record in taxrate_details:
                                    taxrate_resp=TaxRateResponse()
                                    taxrate_resp.set_id(taxrate_record.id)
                                    taxrate_resp.set_name(taxrate_record.name)
                                    taxrate_resp.set_rate(taxrate_record.rate)
                                    taxrate_resp.set_status(taxrate_record.status)
                                    tax_resp.tax_rate_id=json.loads(taxrate_resp.get())
                                    tax_resp.set_subtax_id(json.loads(subtax_resp.get()))
                                    vyslist.append(tax_resp.__dict__.copy())
                                    # tax_resp=TaxsummaryResponse()
                                    # print(tax_resp)
                            else:
                                tax_resp.set_subtax_id(json.loads(subtax_resp.get()))
                                vyslist.append(tax_resp.__dict__.copy())

                    #
                    else:
                        vyslist.append(tax_resp.__dict__.copy())
                        # vyslist.append(tax_resp)
                vyslist.data=vyslist.data[vys_page.get_offset():vys_page.get_query_limit()]
                vpage = NWisefinPaginator(vyslist.data, vys_page.get_index(), 10)
                vyslist.set_pagination(vpage)
                return vyslist
            else:
                return vyslist
        except:
            logger.error('ERROR_TAX_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj

    #





    def taxname_get(self,request,vys_page):
        condition = Q()
        if "data" in request.GET:
            condition &= Q(name__icontains=request.GET.get("data"))
        data=Tax.objects.using(self._current_app_schema()).filter(condition).values('id','name','code')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        # print(data)
        tax_list_data = List()
        list_data = len(data)
        if list_data <= 0:
            vpage = NWisefinPaginator(data, vys_page.get_index(), 10)
            tax_list_data.set_pagination(vpage)
            return tax_list_data
        else:
            for i in data:
                # print(i)
                response = TaxResponse()
                response.set_id(i['id'])
                response.set_code(i['code'])
                response.set_name(i['name'])
                tax_list_data.append(response)
            vpage = NWisefinPaginator(data, vys_page.get_index(), 10)
            tax_list_data.set_pagination(vpage)
            return tax_list_data

    def subtaxname(self,request,vys_page,tax_id):
        condition = Q(tax_id=tax_id)
        if "data" in request.GET:
            condition &= Q(name__icontains=request.GET.get("data"))
        data = SubTax.objects.using(self._current_app_schema()).filter(condition).values('id', 'name', 'code','tax_id')[
               vys_page.get_offset():vys_page.get_query_limit()]
        # print(data)
        tax_list_data = List()
        list_data = len(data)
        if list_data <= 0:
            vpage = NWisefinPaginator(data, vys_page.get_index(), 10)
            tax_list_data.set_pagination(vpage)
            return tax_list_data
        else:
            for i in data:
                # print(i)
                response = SubTaxResponse()
                response.set_id(i['id'])
                response.set_code(i['code'])
                response.set_name(i['name'])
                response.set_tax_id(i['tax_id'])
                tax_list_data.append(response)
            vpage = NWisefinPaginator(data, vys_page.get_index(), 10)
            tax_list_data.set_pagination(vpage)
            return tax_list_data


    def taxratename(self,request,vys_page,subtax_id):
        condition = Q(subtax_id=subtax_id)
        if "data" in request.GET:
            condition &= Q(name__icontains=request.GET.get("data"))
        data = TaxRate.objects.using(self._current_app_schema()).filter(condition).values('id', 'name', 'code','subtax_id')[
               vys_page.get_offset():vys_page.get_query_limit()]
        # print(data)
        tax_list_data = List()
        list_data = len(data)
        if list_data <= 0:
            vpage = NWisefinPaginator(data, vys_page.get_index(), 10)
            tax_list_data.set_pagination(vpage)
            return tax_list_data
        else:
            for i in data:
                # print(i)
                response = TaxRateResponse()
                response.set_id(i['id'])
                response.set_code(i['code'])
                response.set_name(i['name'])
                response.set_subtax_id(i['subtax_id'])
                tax_list_data.append(response)
            vpage = NWisefinPaginator(data, vys_page.get_index(), 10)
            tax_list_data.set_pagination(vpage)
            return tax_list_data

    def fetch_tax_list_download(self, vys_page):
        taxlist = Tax.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by('created_date')
        list_length = len(taxlist)
        if list_length < 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_tax_ID)
            error_obj.set_description(ErrorDescription.INVALID_tax_ID)
            return error_obj
        else:
            tax_list_data = NWisefinList()
            for tax in taxlist:
                tax_data = TaxResponse()
                tax_data.set_id(tax.id)
                tax_data.set_code(tax.code)
                tax_data.set_name(tax.name)
                tax_data.set_receivable(tax.receivable)
                tax_data.set_payable(tax.payable)
                tax_data.set_glno(tax.glno)
                tax_list_data.append(tax_data)
            return tax_list_data