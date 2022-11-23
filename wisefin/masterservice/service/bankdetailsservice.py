import traceback

import django
from django.db import IntegrityError
from django.db.models import Q
from masterservice.data.response.bankdetailsresponse import BankDetailsResponse
from masterservice.models import  BankDetails
from masterservice.service.bankbranchservice import BankBranchService
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from datetime import datetime

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

now = datetime.now()
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.util.masterutil import ModifyStatus,MasterRefType,RequestStatusUtil
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
import json

class BankDetailsService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_bankdetails(self, bank_obj, user_id):
        if not bank_obj.get_id() is None:
            try:
                logger.error('BANKDETAILS: BankDetails Update Started')
                bankdetails_update = BankDetails.objects.using(self._current_app_schema()).filter(id=bank_obj.get_id()).update(
                                bankbranch_id=bank_obj.get_bankbranch_id(),
                                account_no=bank_obj.get_account_no(),
                                accountholder=bank_obj.get_accountholder(),
                                updated_date=now,
                                updated_by=user_id)

                bankdetails_var = BankDetails.objects.using(self._current_app_schema()).get(id=bank_obj.get_id())
                logger.error('BANKDETAILS: BankDetails Update Success' + str(bankdetails_update))
                bankdetails_auditdata ={'id':bank_obj.get_id(),
                                'bankbranch_id':bank_obj.get_bankbranch_id(),
                                'account_no':bank_obj.get_account_no(),
                                'accountholder':bank_obj.get_accountholder(),
                                'updated_date':now,
                                'updated_by':user_id}

                self.audit_function(bankdetails_auditdata, user_id, bankdetails_var.id, ModifyStatus.update)
            except IntegrityError as error:
                logger.error('ERROR_BankDetails_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except BankDetails.DoesNotExist:
                logger.error('ERROR_BankDetails_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CATEGORY_ID)
                error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
                return error_obj
            except:
                logger.error('ERROR_BankDetails_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('BANKDETAILS: BankDetails Creation Started')
                bankdetails_var = BankDetails.objects.using(self._current_app_schema()).create(bankbranch_id=bank_obj.get_bankbranch_id(),
                                                        account_no=bank_obj.get_account_no(),
                                                        accountholder=bank_obj.get_accountholder(),
                                                         created_by=user_id, entity_id=self._entity_id())

                self.audit_function(bankdetails_var, user_id, bankdetails_var.id, ModifyStatus.create)
                logger.error('BANKDETAILS: BankDetails Creation Success' + str(bankdetails_var))

            except IntegrityError as error:
                logger.error('ERROR_BankDetails_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_BankDetails_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        bank_data = BankDetailsResponse()
        bank_data.set_id(bankdetails_var.id)
        bank_data.set_bankbranch_id(bankdetails_var.bankbranch_id)
        bank_data.set_account_no(bankdetails_var.account_no)
        bank_data.set_accountholder(bankdetails_var.accountholder)
        return bank_data


    def fetch_bankdetails_list(self,vys_page,account_no,emp_id):
        conditions = Q(entity_id=self._entity_id())
        if account_no is not None:
            conditions &= Q(account_no__icontains=account_no)
        bankdtls_list = BankDetails.objects.using(self._current_app_schema()).filter(conditions).order_by('-id')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(bankdtls_list)
        if list_length >= 0:
            bank_list_data = NWisefinList()
            for bankdtls in bankdtls_list:
                bank_data = BankDetailsResponse()
                bankbranch_serv=BankBranchService(self._scope())
                bank_data.set_id(bankdtls.id)
                bank_data.set_bankbranch_id(bankdtls.bankbranch_id)
                bank_data.set_bankbranch(bankbranch_serv.fetch_bankbranch(bankdtls.bankbranch_id,emp_id))
                bank_data.set_account_no(bankdtls.account_no)
                bank_data.set_accountholder(bankdtls.accountholder)
                bank_list_data.append(bank_data)
            vpage = NWisefinPaginator(bankdtls_list, vys_page.get_index(), 10)
            bank_list_data.set_pagination(vpage)
            return bank_list_data
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_BANK_ID)
            error_obj.set_description(ErrorDescription.INVALID_BANK_ID)
            return error_obj

    def fetch_bankdetails(self, bankdetails_id,emp_id):
        try:
            bank_var = BankDetails.objects.using(self._current_app_schema()).get(id=bankdetails_id,entity_id=self._entity_id())
            bankbranch_serv = BankBranchService(self._scope())
            bank_data = BankDetailsResponse()
            bank_data.set_id(bank_var.id)
            bank_data.set_bankbranch_id(bank_var.bankbranch_id)
            bank_data.set_bankbranch(bankbranch_serv.fetch_bankbranch(bank_var.bankbranch_id, emp_id))
            bank_data.set_account_no(bank_var.account_no)
            bank_data.set_accountholder(bank_var.accountholder)
            return bank_data
        except BankDetails.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_BANK_ID)
            error_obj.set_description(ErrorDescription.INVALID_BANK_ID)
            return error_obj

    def delete_bankdetails(self, bankdetails_id,emp_id):

        bankdetails = BankDetails.objects.using(self._current_app_schema()).filter(id=bankdetails_id,entity_id=self._entity_id()).update(
            status=ModifyStatus.delete,
            updated_by=emp_id,
            updated_date=now )

        if bankdetails == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_BANK_ID)
            error_obj.set_description(ErrorDescription.INVALID_BANK_ID)
            return error_obj
        else:
            self.audit_function(bankdetails, emp_id, bankdetails_id, ModifyStatus.delete)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def audit_function(self,data_obj,user_id,id,action):
        if action == ModifyStatus.delete:
            data = None
        elif action == ModifyStatus.update:
            data = data_obj
        else:
            data = data_obj.__dict__
            del data['_state']
        audit_service = MasterAuditService(self._scope())
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

    def fetch_bankdtails_search(self,account_no,accountholder,vys_page):
        coditions=Q(entity_id=self._entity_id())
        if account_no is None:
            coditions&=Q(account_no__icontains=account_no)
        if accountholder is None:
            coditions&=Q(accountholder__icontains=accountholder)

        bankdtails_list = BankDetails.objects.using(self._current_app_schema()).filter(coditions).order_by('-id')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        bank_list_data = NWisefinList()
        for bank_var in bankdtails_list:
            bank_data = BankDetailsResponse()
            bank_data.set_id(bank_var.id)
            bank_data.set_bankbranch_id(bank_var.bankbranch_id)
            bank_data.set_account_no(bank_var.account_no)
            bank_data.set_accountholder(bank_var.accountholder)
            bank_list_data.append(bank_data)
            vpage = NWisefinPaginator(bankdtails_list, vys_page.get_index(), 10)
            bank_list_data.set_pagination(vpage)
        return bank_list_data