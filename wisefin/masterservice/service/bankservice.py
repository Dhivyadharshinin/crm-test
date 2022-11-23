import traceback

import django
from django.db import IntegrityError
from django.db.models import Q

from masterservice.models import Bank
from nwisefin.settings import logger
from vendorservice.data.response.bankresponse import BankResponse
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from datetime import datetime
now = datetime.now()
from masterservice.data.request.masterauditrequest import MasterAuditRequest
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.util.masterutil import ModifyStatus, MasterRefType, RequestStatusUtil, Code_Gen_Type, Code_Gen_Value
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
import json
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from masterservice.service.Codegenerator import CodeGen


class BankService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_bank(self, bank_obj, user_id):
        if not bank_obj.get_id() is None:
            try:
                logger.error('BANK: Bank Update Started')
                bank_update = Bank.objects.using(self._current_app_schema()).filter(id=bank_obj.get_id(),
                                                                                    entity_id=self._entity_id()).update(
                    # code=bank_obj.get_bankcode(),
                    name=bank_obj.get_bankname(),
                    updated_date=now,
                    updated_by=user_id)

                bank_var = Bank.objects.using(self._current_app_schema()).get(id=bank_obj.get_id(), entity_id=self._entity_id())
                logger.error('BANK: Bank Update Success' + str(bank_update))
                bank_auditdata = {'id': bank_obj.get_id(),
                                  # 'code':bank_obj.get_bankcode(),
                                  'name': bank_obj.get_bankname(),
                                  'updated_date': now,
                                  'updated_by': user_id}
                self.audit_function(bank_auditdata, user_id, bank_var.id, ModifyStatus.update)
            except IntegrityError as error:
                logger.error('ERROR_Bank_Update_EXCEPT:{}'.format(traceback.print_exc()))
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Bank.DoesNotExist:
                logger.error('ERROR_Bank_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CATEGORY_ID)
                error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
                return error_obj
            except:
                logger.error('ERROR_Bank_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('BANK: Bank Creation Started')
                bank_var = Bank.objects.using(self._current_app_schema()).create(  # code=bank_obj.get_bankcode(),
                    name=bank_obj.get_bankname(),
                    created_by=user_id, entity_id=self._entity_id())
                try:
                    max_cat_code = Bank.objects.using(self._current_app_schema()).filter(code__icontains='BK').order_by('-code')[0].code
                    rnsl = int(max_cat_code[2:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "BK" + str(new_rnsl).zfill(6) # code = "ISCT" + str(bank_serv)
                bank_var.code = code
                bank_var.save()
                self.audit_function(bank_var, user_id, bank_var.id, ModifyStatus.create)
                logger.error('BANK: Bank Creation Success' + str(bank_var))

            except IntegrityError as error:
                logger.error('ERROR_Bank_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_Bank_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        # bank_data = BankResponse()
        # bank_data.set_id(bank_var.id)
        # bank_data.set_code(bank_var.code)
        # bank_data.set_name(bank_var.name)
        resp=NWisefinSuccess()
        resp.set_status(SuccessStatus.SUCCESS)
        resp.set_message(SuccessMessage.CREATE_MESSAGE)
        resp.set_message(SuccessMessage.CREATE_MESSAGE)
        return resp

    def fetch_bank_list(self, vys_page, query):
        try:
            conditions = Q(status=1) & Q(entity_id=self._entity_id())
            if query is not None:
                conditions &= Q(name__icontains=query)
            banklist = Bank.objects.using(self._current_app_schema()).filter(conditions).order_by('created_date')[
                       vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(banklist)
            if list_length >= 0:
                bank_list_data = NWisefinList()
                for bankobj in banklist:
                    bank_data = BankResponse()
                    bank_data.set_id(bankobj.id)
                    bank_data.set_code(bankobj.code)
                    bank_data.set_name(bankobj.name)
                    bank_list_data.append(bank_data)
                vpage = NWisefinPaginator(banklist, vys_page.get_index(), 10)
                bank_list_data.set_pagination(vpage)
                return bank_list_data
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_BANK_ID)
                error_obj.set_description(ErrorDescription.INVALID_BANK_ID)
                return error_obj
        except:
            logger.error('ERROR_Bank_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_BANK_ID)
            error_obj.set_description(ErrorDescription.INVALID_BANK_ID)
            return error_obj

    def fetch_bank(self, bank_id, user_id):
        try:
            bank_var = Bank.objects.using(self._current_app_schema()).get(id=bank_id, entity_id=self._entity_id())
            bank_data = BankResponse()
            bank_data.set_id(bank_var.id)
            bank_data.set_code(bank_var.code)
            bank_data.set_name(bank_var.name)
            return bank_data
        except Bank.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_BANK_ID)
            error_obj.set_description(ErrorDescription.INVALID_BANK_ID)
            return error_obj

    def delete_bank(self, bank_id, user_id):
        bank = Bank.objects.using(self._current_app_schema()).filter(id=bank_id, entity_id=self._entity_id()).delete()
        self.audit_function(bank, user_id, bank_id, ModifyStatus.delete)

        if bank[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_BANK_ID)
            error_obj.set_description(ErrorDescription.INVALID_BANK_ID)
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
        audit_obj.set_relreftype(MasterRefType.BANK)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return

    def fetch_bank_search(self, query, vys_page):
        if query is None:
            banklist = Bank.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by(
                'created_date')[
                       vys_page.get_offset():vys_page.get_query_limit()]
        else:
            banklist = Bank.objects.using(self._current_app_schema()).filter(name__icontains=query,
                                                                             entity_id=self._entity_id()).order_by(
                'created_date')[
                       vys_page.get_offset():vys_page.get_query_limit()]
        bank_list_data = NWisefinList()
        for bankobj in banklist:
            bank_data = BankResponse()
            bank_data.set_id(bankobj.id)
            bank_data.set_code(bankobj.code)
            bank_data.set_name(bankobj.name)
            bank_list_data.append(bank_data)
            vpage = NWisefinPaginator(banklist, vys_page.get_index(), 10)
            bank_list_data.set_pagination(vpage)
        return bank_list_data

    def create_bank_mtom(self, bank_obj, user_id):
        if not bank_obj.get_id() is None:
            try:
                bank_update = Bank.objects.using(self._current_app_schema()).filter(id=bank_obj.get_id(),
                                                                                    entity_id=self._entity_id()).update(
                    code=bank_obj.get_bankcode(),
                    name=bank_obj.get_bankname(),
                    updated_date=now,
                    updated_by=user_id)

                bank_var = Bank.objects.using(self._current_app_schema()).get(id=bank_obj.get_id(),
                                                                              entity_id=self._entity_id())
                bank_auditdata = {'id': bank_obj.get_id(),
                                  'code': bank_obj.get_bankcode(),
                                  'name': bank_obj.get_bankname(),
                                  'updated_date': now,
                                  'updated_by': user_id}
                self.audit_function(bank_auditdata, user_id, bank_var.id, ModifyStatus.update)
            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Bank.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CATEGORY_ID)
                error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                bank_var = Bank.objects.using(self._current_app_schema()).create(code=bank_obj.get_bankcode(),
                                                                                 name=bank_obj.get_bankname(),
                                                                                 created_by=user_id,
                                                                                 entity_id=self._entity_id())

                self.audit_function(bank_var, user_id, bank_var.id, ModifyStatus.create)

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

        bank_data = BankResponse()
        bank_data.set_id(bank_var.id)
        bank_data.set_code(bank_var.code)
        bank_data.set_name(bank_var.name)
        return bank_data

    def fetch_bankone(self, bank_id):
        bank = Bank.objects.using(self._current_app_schema()).get(id=bank_id, entity_id=self._entity_id())
        bank_data = {"id": bank.id, "code": bank.code, "name": bank.name}
        bank_dic = json.dumps(bank_data, indent=4)
        return bank_data

    def fetch_banklist(request, bank_ids):
        # bank_ids = json.loads(request.body)
        bank_id2 = bank_ids.get('bank_id')
        obj = Bank.objects.using(request._current_app_schema()).filter(id__in=bank_id2,
                                                                       entity_id=request._entity_id()).values('id',
                                                                                                              'name',
                                                                                                              'code')
        bank_list_data = NWisefinList()
        for i in obj:
            data = {"id": i['id'], "name": i['name'], "code": i['code']}
            bank_list_data.append(data)
        return bank_list_data.get()

    def get_bank_sync_id(self, bank_name):
        bank_var = Bank.objects.using(self._current_app_schema()).filter(name__iexact=bank_name)
        if len(bank_var) > 0:
            bank_id = bank_var[0].id
            return bank_id
        else:
            return 0

    def fetch_bank_list_download(self, vys_page):
        try:
            banklist = Bank.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by('created_date')
            list_length = len(banklist)
            if list_length >= 0:
                bank_list_data = NWisefinList()
                for bankobj in banklist:
                    bank_data = BankResponse()
                    bank_data.set_id(bankobj.id)
                    bank_data.set_code(bankobj.code)
                    bank_data.set_name(bankobj.name)
                    bank_list_data.append(bank_data)
                return bank_list_data
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_BANK_ID)
                error_obj.set_description(ErrorDescription.INVALID_BANK_ID)
                return error_obj
        except:
            logger.error('ERROR_Bank_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_BANK_ID)
            error_obj.set_description(ErrorDescription.INVALID_BANK_ID)
            return error_obj