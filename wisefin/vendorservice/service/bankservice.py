import django
from django.db import IntegrityError
from nwisefin.settings import logger
from masterservice.models import Bank
from userservice.models import Employee
from vendorservice.data.response.bankresponse import BankResponse
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from datetime import datetime
now = datetime.now()


class BankService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_bank(self, bank_obj, user_id):
        if not bank_obj.get_id() is None:
            # try:
                bank_var = Bank.objects.using(self._current_app_schema()).filter(id=bank_obj.get_id(), entity_id=self._entity_id()).update(
                                code=bank_obj.get_bankcode(),
                                name=bank_obj.get_bankname(),
                                updated_time=now,
                                updated_by=user_id)

                bank_var = Bank.objects.using(self._current_app_schema()).get(id=bank_obj.get_id(), entity_id=self._entity_id())
                #logger.info(category)
            # except IntegrityError as error:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except MemoCategory.DoesNotExist:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_CATEGORY_ID)
            #     error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
            #     return error_obj
            # except:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj
        else:
            #try:
                bank_var = Bank.objects.using(self._current_app_schema()).create(code=bank_obj.get_bankcode(),
                                                     name=bank_obj.get_bankname(),
                                                     created_by=user_id, entity_id=self._entity_id())
            # except IntegrityError as error:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj

        bank_data = BankResponse()
        bank_data.set_id(bank_var.id)
        bank_data.set_code(bank_var.code)
        bank_data.set_name(bank_var.name)
        return bank_data

    def fetch_bank_list(self,user_id):
        banklist = Bank.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())
        list_length = len(banklist)
        logger.info(str(list_length))
        if list_length <= 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_BANK_ID)
            error_obj.set_description(ErrorDescription.INVALID_BANK_ID)
            return error_obj
        else:
            bank_list_data = NWisefinList()
            for bankobj in banklist:
                bank_data = BankResponse()
                bank_data.set_id(bankobj.id)
                bank_data.set_code(bankobj.code)
                bank_data.set_name(bankobj.name)
                bank_list_data.append(bank_data)
            return bank_list_data

    def fetch_bank(self, bank_id,user_id):
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

    def delete_bank(self, category_id):
        bank = Bank.objects.using(self._current_app_schema()).filter(id=category_id, entity_id=self._entity_id()).delete()
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
