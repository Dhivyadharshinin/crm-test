
from django.db import IntegrityError
from django.db.models import Q

from pprservice.models import CostDriver
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from vendorservice.data.response.bankresponse import BankResponse
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from datetime import datetime
now = datetime.now()
from pprservice.data.response.costdriverresponse import CostDriverResponse

class CostDriverService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.PPR_SERVICE)

    def create_costdriver(self, cost_obj, user_id):
        if not cost_obj.get_id() is None:
            try:
                costdriver_update = CostDriver.objects.using(self._current_app_schema()).filter(id=cost_obj.get_id()).update(
                                name=cost_obj.get_name(),
                                parameter_name=cost_obj.get_parameter_name(),
                                updated_date=now,
                                updated_by=user_id)

                costdriver_update = CostDriver.objects.get(id=cost_obj.get_id())

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except CostDriver.DoesNotExist:
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
                costdriver_update = CostDriver.objects.create(
                                                    name=cost_obj.get_name(),
                                                    parameter_name=cost_obj.get_parameter_name(),
                                                    created_by=user_id)
                code = "C" + str(costdriver_update.id)
                costdriver_update.code = code
                costdriver_update.save()

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

        cost_data = CostDriverResponse()
        cost_data.set_id(costdriver_update.id)
        cost_data.set_code(costdriver_update.code)
        cost_data.set_name(costdriver_update.name)
        cost_data.set_parameter_name(costdriver_update.parameter_name)
        return cost_data

    def fetch_costdriver_list(self,vys_page,query):
        conditions = Q(status=1,entity_id=self._entity_id())
        if query is not None:
            conditions &= Q(name__icontains=query)
        cost_obj = CostDriver.objects.using(self._current_app_schema()).filter(conditions).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(cost_obj)
        cost_list_data = NWisefinList()
        if list_length >= 0:
            for catobj in cost_obj:
                cost_data = CostDriverResponse()
                cost_data.set_id(catobj.id)
                cost_data.set_code(catobj.code)
                cost_data.set_name(catobj.name)
                cost_data.set_parameter_name(catobj.parameter_name)
                cost_list_data.append(cost_data)
                vpage = NWisefinPaginator(cost_obj, vys_page.get_index(), 10)
                cost_list_data.set_pagination(vpage)
        return cost_list_data

    def fetch_costdriver(self, category_id,user_id):
        try:
            cost_var = CostDriver.objects.using(self._current_app_schema()).get(id=category_id)
            cost_data = CostDriverResponse()
            cost_data.set_id(cost_var.id)
            cost_data.set_code(cost_var.code)
            cost_data.set_name(cost_var.name)
            cost_data.set_parameter_name(cost_var.parameter_name)
            return cost_data
        except CostDriver.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_BANK_ID)
            error_obj.set_description(ErrorDescription.INVALID_BANK_ID)
            return error_obj

    def delete_costdriver(self, costdriver_id,user_id):
        cost_obj = CostDriver.objects.using(self._current_app_schema()).filter(id=costdriver_id).delete()

        if cost_obj[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_BANK_ID)
            error_obj.set_description(ErrorDescription.INVALID_BANK_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def fetch_costdriver_search(self,query,vys_page):
        condition=Q(status=1,entity_id=self._entity_id())
        if query is not None:
            condition &=Q(name__icontains=query)
        cost_obj = CostDriver.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        cost_list_data = NWisefinList()
        for catobj in cost_obj:
            cost_data = CostDriverResponse()
            cost_data.set_id(catobj.id)
            cost_data.set_code(catobj.code)
            cost_data.set_name(catobj.name)
            cost_data.set_parameter_name(catobj.parameter_name)
            cost_list_data.append(cost_data)
            vpage = NWisefinPaginator(cost_obj, vys_page.get_index(), 10)
            cost_list_data.set_pagination(vpage)
        return cost_list_data