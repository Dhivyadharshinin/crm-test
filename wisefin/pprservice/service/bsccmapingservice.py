import django
from django.db import IntegrityError
from django.db.models import Q

from pprservice.models import bscc_maping
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
from pprservice.data.response.bsccmapingresponse import BSCCmapingResponse

class BSCCmapingService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.PPR_SERVICE)

    def create_bsccmaping(self, bscc_obj, user_id):
        if not bscc_obj.get_id() is None:
            try:
                bscc_update = bscc_maping.objects.using(self._current_app_schema()).filter(id=bscc_obj.get_id(),entity_id=self._entity_id()).update(
                                name=bscc_obj.get_name(),
                                bsname=bscc_obj.get_bsname(),
                                subcat_id=bscc_obj.get_subcat_id(),
                                allocationlevel_id=bscc_obj.get_allocationlevel(),
                                costdriver_id=bscc_obj.get_costdriver(),
                                updated_date=now,
                                updated_by=user_id)

                bscc_update = bscc_maping.objects.using(self._current_app_schema()).get(id=bscc_obj.get_id())

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except bscc_maping.DoesNotExist:
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
                bscc_update = bscc_maping.objects.using(self._current_app_schema()).create(
                                                    name=bscc_obj.get_name(),
                                                    bsname=bscc_obj.get_bsname(),
                                                    subcat_id=bscc_obj.get_subcat_id(),
                                                    allocationlevel_id=bscc_obj.get_allocationlevel(),
                                                    costdriver_id=bscc_obj.get_costdriver(),
                                                    created_by=user_id,entity_id=self._entity_id())
                code = "BSCC" + str(bscc_update.id)
                bscc_update.code = code
                bscc_update.save()

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

        bscc_data = BSCCmapingResponse()
        bscc_data.set_id(bscc_update.id)
        bscc_data.set_code(bscc_update.code)
        bscc_data.set_name(bscc_update.name)
        bscc_data.set_subcat_id(bscc_update.subcat_id)
        bscc_data.set_allocationlevel(bscc_update.allocationlevel_id)
        bscc_data.set_costdriver(bscc_update.costdriver_id)
        return bscc_data

    def fetch_bsccmaping_list(self,vys_page,query):
        conditions = Q(status=1,entity_id=self._entity_id())
        if query is not None:
            conditions &= Q(name__icontains=query)
        cost_obj = bscc_maping.objects.using(self._current_app_schema()).filter(conditions).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(cost_obj)
        cost_list_data = NWisefinList()
        if list_length >= 0:
            for bsccobj in cost_obj:
                cost_data = BSCCmapingResponse()
                cost_data.set_id(bsccobj.id)
                cost_data.set_code(bsccobj.code)
                cost_data.set_name(bsccobj.name)
                cost_data.set_subcat_id(bsccobj.subcat_id)
                cost_data.set_allocationlevel(bsccobj.allocationlevel_id)
                cost_data.set_costdriver(bsccobj.costdriver_id)
                cost_list_data.append(cost_data)
                vpage = NWisefinPaginator(cost_obj, vys_page.get_index(), 10)
                cost_list_data.set_pagination(vpage)
        return cost_list_data

    def fetch_bsccmaping(self, bsccmaping_id,user_id):
        try:
            cost_var = bscc_maping.objects.using(self._current_app_schema()).get(id=bsccmaping_id,entity_id=self._entity_id())
            cost_data = BSCCmapingResponse()
            cost_data.set_id(cost_var.id)
            cost_data.set_code(cost_var.code)
            cost_data.set_name(cost_var.name)
            cost_data.set_subcat_id(cost_var.subcat_id)
            cost_data.set_allocationlevel(cost_var.allocationlevel_id)
            cost_data.set_costdriver(cost_var.costdriver_id)
            return cost_data
        except bscc_maping.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_BANK_ID)
            error_obj.set_description(ErrorDescription.INVALID_BANK_ID)
            return error_obj

    def delete_bsccmaping(self, bsccmaping_id,user_id):
        cost_obj = bscc_maping.objects.using(self._current_app_schema()).filter(id=bsccmaping_id,entity_id=self._entity_id()).delete()

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

    def fetch_bsccmaping_search(self,query,vys_page):
        condition=Q(status=1,entity_id=self._entity_id())
        if query is not None:
            condition &=Q(name__icontains=query)
        cost_obj = bscc_maping.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        cost_list_data = NWisefinList()
        for bsccobj in cost_obj:
            cost_data = BSCCmapingResponse()
            cost_data.set_id(bsccobj.id)
            cost_data.set_code(bsccobj.code)
            cost_data.set_name(bsccobj.name)
            cost_data.set_subcat_id(bsccobj.subcat_id)
            cost_data.set_allocationlevel(bsccobj.allocationlevel_id)
            cost_data.set_costdriver(bsccobj.costdriver_id)
            cost_list_data.append(cost_data)
            vpage = NWisefinPaginator(cost_obj, vys_page.get_index(), 10)
            cost_list_data.set_pagination(vpage)
        return cost_list_data
