import django

from django.db import IntegrityError
from nwisefin.settings import logger
from masterservice.models import BankBranch
from userservice.models import Employee
from vendorservice.data.response.bankbranchresponse import BankBranchResponse
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from datetime import datetime
now = datetime.now()


class BankBranchService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_bankbranch(self, bankbranch_obj, user_id):

        if not bankbranch_obj.get_id() is None:
            try:
                bankbranch_var = BankBranch.objects.using(self._current_app_schema()).filter(id=bankbranch_obj.get_id(), entity_id=self._entity_id()).update(
                                code=bankbranch_obj.get_code(),
                                ifsccode=bankbranch_obj.get_ifsccode(),
                                microcode=bankbranch_obj.get_microcode(),
                                name=bankbranch_obj.get_name(),
                                bank_id=bankbranch_obj.get_bankid(),
                                address_id=bankbranch_obj.get_addrid(),
                                updated_time=now,
                                updated_by=user_id)

                bankbranch_var = BankBranch.objects.using(self._current_app_schema()).get(id=bankbranch_obj.get_id(), entity_id=self._entity_id())

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except BankBranch.DoesNotExist:
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
                bankbranch_var = BankBranch.objects.using(self._current_app_schema()).create(code=bankbranch_obj.get_code(),
                                                     ifsccode=bankbranch_obj.get_ifsccode(),
                                                     microcode=bankbranch_obj.get_microcode(),
                                                     name=bankbranch_obj.get_name(),
                                                     bank_id=bankbranch_obj.get_bankid(),
                                                     address_id=bankbranch_obj.get_addrid(),
                                                     created_by=user_id, entity_id=self._entity_id())
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

        bankbranch_data = BankBranchResponse()
        bankbranch_data.set_id(bankbranch_var.id)
        bankbranch_data.set_code(bankbranch_var.code)
        bankbranch_data.set_name(bankbranch_var.name)
        bankbranch_data.set_ifsccode(bankbranch_var.ifsccode)
        bankbranch_data.set_microcode(bankbranch_var.microcode)
        return bankbranch_data

    def fetch_bankbranch_list(self,user_id):
        bankbranchlist = BankBranch.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())
        list_length = len(bankbranchlist)
        logger.info(str(list_length))
        if list_length <= 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_BANKBRANCH_ID)
            error_obj.set_description(ErrorDescription.INVALID_BANKBRANCH_ID)
            return error_obj
        else:
            bankbranch_list_data = NWisefinList()
            for bankobj in bankbranchlist:
                bankbranch_data = BankBranchResponse()
                bankbranch_data.set_id(bankobj.id)
                bankbranch_data.set_code(bankobj.code)
                bankbranch_data.set_name(bankobj.name)
                bankbranch_data.set_ifsccode(bankobj.ifsccode)
                bankbranch_data.set_microcode(bankobj.microcode)
                bankbranch_list_data.append(bankbranch_data)
            return bankbranch_list_data

    def fetch_bankbranch(self, bankbranch_id,user_id):
        try:
            bankbranch_var = BankBranch.objects.using(self._current_app_schema()).get(id=bankbranch_id, entity_id=self._entity_id())
            bankbranch_data = BankBranchResponse()
            bankbranch_data.set_id(bankbranch_var.id)
            bankbranch_data.set_code(bankbranch_var.code)
            bankbranch_data.set_name(bankbranch_var.name)
            bankbranch_data.set_ifsccode(bankbranch_var.ifsccode)
            bankbranch_data.set_microcode(bankbranch_var.microcode)
            return bankbranch_data
        except BankBranch.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_BANKBRANCH_ID)
            error_obj.set_description(ErrorDescription.INVALID_BANKBRANCH_ID)
            return error_obj

    def delete_bankbranch(self, bankbranch_id):
        bankbranch = BankBranch.objects.using(self._current_app_schema()).filter(id=bankbranch_id, entity_id=self._entity_id()).delete()
        if bankbranch[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_BANKBRANCH_ID)
            error_obj.set_description(ErrorDescription.INVALID_BANKBRANCH_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
