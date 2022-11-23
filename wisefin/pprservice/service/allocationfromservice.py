
from django.db import IntegrityError


from pprservice.models import FAS_Main
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from datetime import datetime

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

now = datetime.now()
from pprservice.data.response.allocationfromresponse import AllocationFromResponse
class AllocationService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.PPR_SERVICE)

    def create_allocation(self, allocationlevel_obj, user_id):
        if not allocationlevel_obj.get_id() is None:
            try:
                allocation_update = FAS_Main.objects.using(self._current_app_schema()).filter(id=allocationlevel_obj.get_id(),entity_id=self._entity_id()).update(
                                source=allocationlevel_obj.get_source(),
                                entry_id=allocationlevel_obj.get_entry_id(),
                                entity_code=allocationlevel_obj.get_entity_code(),
                                module=allocationlevel_obj.get_module(),
                                sync_date=allocationlevel_obj.get_sync_date(),
                                wiseFin_date=allocationlevel_obj.get_wiseFin_date(),
                                update_date=allocationlevel_obj.get_update_date(),
                                CBS_date=allocationlevel_obj.get_CBS_date(),
                                entry_status=allocationlevel_obj.get_entry_status(),
                                branch_id=allocationlevel_obj.get_branch_id(),
                                cr_no=allocationlevel_obj.get_cr_no(),
                                supplier_id=allocationlevel_obj.get_supplier_id(),
                                product_id=allocationlevel_obj.get_product_id(),
                                commodity_id=allocationlevel_obj.get_commodity_id(),
                                apcat_id=allocationlevel_obj.get_apcat_id(),
                                apsubcat_id=allocationlevel_obj.get_apsubcat_id(),
                                bs_id=allocationlevel_obj.get_bs_id(),
                                bscc_id=allocationlevel_obj.get_bscc_id(),
                                CBS_GL=allocationlevel_obj.get_CBS_GL(),
                                sort_oder=allocationlevel_obj.get_sort_oder(),
                                ALEI=allocationlevel_obj.get_ALEI(),
                                input=allocationlevel_obj.get_input(),
                                sorce_bscc_id=allocationlevel_obj.get_sorce_bscc_id(),
                                amount=allocationlevel_obj.get_amount(),
                                updated_date=now,
                                updated_by=user_id)

                allocation_update = FAS_Main.objects.get(id=allocationlevel_obj.get_id())

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except FAS_Main.DoesNotExist:
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
            # try:
                allocation_update = FAS_Main.objects.using(self._current_app_schema()).create(
                    source=allocationlevel_obj.get_source(),
                    entry_id=allocationlevel_obj.get_entry_id(),
                    entity_code=allocationlevel_obj.get_entity_code(),
                    module=allocationlevel_obj.get_module(),
                    sync_date=allocationlevel_obj.get_sync_date(),
                    wiseFin_date=allocationlevel_obj.get_wiseFin_date(),
                    update_date=allocationlevel_obj.get_update_date(),
                    CBS_date=allocationlevel_obj.get_CBS_date(),
                    entry_status=allocationlevel_obj.get_entry_status(),
                    branch_id=allocationlevel_obj.get_branch_id(),
                    cr_no=allocationlevel_obj.get_cr_no(),
                    supplier_id=allocationlevel_obj.get_supplier_id(),
                    product_id=allocationlevel_obj.get_product_id(),
                    commodity_id=allocationlevel_obj.get_commodity_id(),
                    apcat_id=allocationlevel_obj.get_apcat_id(),
                    apsubcat_id=allocationlevel_obj.get_apsubcat_id(),
                    bs_id=allocationlevel_obj.get_bs_id(),
                    bscc_id=allocationlevel_obj.get_bscc_id(),
                    CBS_GL=allocationlevel_obj.get_CBS_GL(),
                    sort_oder=allocationlevel_obj.get_sort_oder(),
                    ALEI=allocationlevel_obj.get_ALEI(),
                    input=allocationlevel_obj.get_input(),
                    sorce_bscc_id=allocationlevel_obj.get_sorce_bscc_id(),
                    amount=allocationlevel_obj.get_amount(),entity_id=self._entity_id(),created_by=user_id)

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

        allocation_data = AllocationFromResponse()
        allocation_data.set_id(allocation_update.id)

        return allocation_data

