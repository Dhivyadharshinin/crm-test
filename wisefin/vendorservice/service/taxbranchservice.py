from vendorservice.data.response.taxresponse import TaxResponse
from vendorservice.service.vendorservice import VendorService
from vendorservice.models import SupplierTax
from django.db import IntegrityError
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList


class TaxBranchService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def create_taxbranch(self, branch_id, tax_obj, user_id):
        vendor_service = VendorService(self._scope())
        vendor_status = vendor_service.is_active(tax_obj.get_vendor_id)
        logger.info(str(vendor_status))
        if vendor_status != 1:
            if not tax_obj.get_id() is None:
                try:
                    tax = SupplierTax.objects.using(self._current_app_schema()).filter(id=tax_obj.get_id(), entity_id=self._entity_id()).update(
                        branch_id_id=branch_id, branch=tax_obj.get_branch(),
                        msme=tax_obj.get_msme(), type=tax_obj.get_type(),msme_reg_no=tax_obj.get_msme_reg_no,
                        panno=tax_obj.get_panno(),updated_by=user_id

                    )
                    tax = SupplierTax.objects.using(self._current_app_schema()).get(id=tax_obj.get_id(), entity_id=self._entity_id())
                except IntegrityError as error:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
                except SupplierTax.DoesNotExist:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_VENDORTAX_ID)
                    error_obj.set_description(ErrorDescription.INVALID_VENDORTAX_ID)
                    return error_obj
                except:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                    return error_obj
            else:
                try:

                    tax = SupplierTax.objects.using(self._current_app_schema()).create(
                        branch_id_id=branch_id, branch=tax_obj.get_branch(),
                        msme=tax_obj.get_msme(), type=tax_obj.get_type(),msme_reg_no=tax_obj.get_msme_reg_no,
                        panno=tax_obj.get_panno(),created_by=user_id, entity_id=self._entity_id()
                    )
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
            tax_data.set_branch_id(tax.branch_id)
            tax_data.set_branch(tax.branch)
            tax_data.set_msme(tax.msme)
            tax_data.set_type(tax.type)
            tax_data.set_panno(tax.panno)
            return tax_data

    def fetch_taxbranch_list(self,branch_id, user_id):
            taxList = SupplierTax.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())
            list_length = len(taxList)
            logger.info(str(list_length))
            taxa_list_data = NWisefinList()
            if list_length <= 0:
                pass
            else:
                for tax in taxList:
                    tax_data = TaxResponse()
                    tax_data.set_id(tax.id)
                    tax_data.set_branch_id(tax.branch_id)
                    tax_data.set_branch(tax.branch)
                    tax_data.set_msme(tax.msme)
                    tax_data.set_type(tax.type)
                    tax_data.set_panno(tax.panno)
                    taxa_list_data.append(tax_data)
            return taxa_list_data


    def fetch_taxbranch(self,branch_id, tax_id, user_id):
            try:
                tax = SupplierTax.objects.using(self._current_app_schema()).get(id=tax_id, entity_id=self._entity_id())
                tax_data = TaxResponse()
                tax_data.set_id(tax.id)
                tax_data.set_branch_id(tax.branch_id)
                tax_data.set_branch(tax.branch)
                tax_data.set_msme(tax.msme)
                tax_data.set_type(tax.type)
                tax_data.set_panno(tax.panno)
                return tax_data
            except SupplierTax.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_VENDORTAX_ID)
                error_obj.set_description(ErrorDescription.INVALID_VENDORTAX_ID)
                return error_obj


    def delete_taxbranch(self,branch_id, tax_id, user_id):
            tax = SupplierTax.objects.using(self._current_app_schema()).filter(id=tax_id, entity_id=self._entity_id()).delete()
            if tax[0] == 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_VENDORTAX_ID)
                error_obj.set_description(ErrorDescription.INVALID_VENDORTAX_ID)
                return error_obj
            else:
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
                return success_obj
