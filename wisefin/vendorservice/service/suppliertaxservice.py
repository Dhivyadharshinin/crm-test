from django.db import IntegrityError

from userservice.models import Employee
from vendorservice.data.response.suppliertaxresponse import TaxResponse
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from vendorservice.models import SupplierTax, VendorModificationRel, SupplierBranch, VendorFileAttachment, Vendor
from vendorservice.models import SupplierSubTax
from django.utils import timezone
from nwisefin.settings import logger
from vendorservice.util.vendorutil import VendorRefType ,ModifyStatus ,RequestStatusUtil
from vendorservice.service.vendorservice import VendorService
from vendorservice.data.request.vendorauditrequest import VendorAuditRequest
from vendorservice.service.vendorauditservice import VendorAuditService
from vendorservice.data.response.vendorauditresponse import VendorAuditResponse
from utilityservice.service.utilityservice import NWisefinUtilityService
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from django.db.models import Q


class TaxService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def create_suppliertax(self, tax_obj,branch_id,user_id,ref_id,vendor_id):
        req_status = RequestStatusUtil.ONBOARD
        if not tax_obj.get_id() is None:
            # try:
                if tax_obj.isexcempted=="Y":
                    if tax_obj.excemfrom==None:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.INVALID_DATA)
                        error_obj.set_description(ErrorDescription.INVALID_DATA)
                        return error_obj
                    if tax_obj.excemto==None:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.INVALID_DATA)
                        error_obj.set_description(ErrorDescription.INVALID_DATA)
                        return error_obj
                    if tax_obj.excemthrosold==None:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.INVALID_DATA)
                        error_obj.set_description(ErrorDescription.INVALID_DATA)
                        return error_obj
                if tax_obj.isexcempted == "N":
                    if tax_obj.excemfrom != None:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.INVALID_DATA)
                        error_obj.set_description(ErrorDescription.INVALID_DATA)
                        return error_obj
                    if tax_obj.excemto != None:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.INVALID_DATA)
                        error_obj.set_description(ErrorDescription.INVALID_DATA)
                        return error_obj
                    if tax_obj.excemthrosold != 0:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.INVALID_DATA)
                        error_obj.set_description(ErrorDescription.INVALID_DATA)
                        return error_obj

                tax_update = SupplierTax.objects.using(self._current_app_schema()).filter(id=tax_obj.get_id(), entity_id=self._entity_id()).update(
                tax_id =tax_obj.get_tax(),subtax_id =tax_obj.get_subtax(),
                msme =tax_obj.get_msme(),type =tax_obj.get_type(),panno=tax_obj.get_panno(),msme_reg_no=tax_obj.get_msme_reg_no(),
                updated_by=user_id,updated_date=timezone.now(),portal_flag=tax_obj.get_portal_flag())

                tax_auditdata={'id':tax_obj.get_id(),'branch_id':branch_id,
                'tax_id' :tax_obj.get_tax(),'subtax_id' :tax_obj.get_subtax(),
                'msme' :tax_obj.get_msme(),'type' :tax_obj.get_type(),'panno':tax_obj.get_panno(),'msme_reg_no':tax_obj.get_msme_reg_no(),
                'updated_by':user_id,'updated_date':timezone.now()}

                taxsubdetails_update = SupplierSubTax.objects.using(self._current_app_schema()).filter(suppliertax_id=tax_obj.get_id(), entity_id=self._entity_id()).update(
                                                              isexcempted=tax_obj.get_isexcempted(),
                                                              excemfrom=tax_obj.get_excemfrom(),
                                                              excemto=tax_obj.get_excemto(),
                                                              excemthrosold=tax_obj.get_excemthrosold(),
                                                              excemrate=tax_obj.get_excemrate(),
                                                              rate_id=tax_obj.get_taxrate(),
                                                              attachment=ref_id,
                                                              updated_by=user_id,updated_date=timezone.now(),
                                                              portal_flag=tax_obj.get_portal_flag()
                                                              )

                taxdetails_auditdata={'suppliertax_id':tax_obj.get_id(),
                                                              'isexcempted':tax_obj.get_isexcempted(),
                                                              'excemfrom':tax_obj.get_excemfrom(),
                                                              'excemto':tax_obj.get_excemto(),
                                                              'excemthrosold':tax_obj.get_excemthrosold(),
                                                              'excemrate':tax_obj.get_excemrate(),
                                                              'rate_id':tax_obj.get_taxrate(),
                                                              'attachment':ref_id,
                                                              'updated_by':user_id,'updated_date':timezone.now()}

                tax = SupplierTax.objects.using(self._current_app_schema()).get(id=tax_obj.get_id(), entity_id=self._entity_id())
                taxsubdetails = SupplierSubTax.objects.using(self._current_app_schema()).get(suppliertax_id=tax_obj.get_id(), entity_id=self._entity_id())
                # audit
                Audit_Action = ModifyStatus.update
                self.audit_function(tax_auditdata, vendor_id, user_id, req_status, tax.id, VendorRefType.VENDOR_SUPPLIERTAX, Audit_Action)
                self.audit_function(taxdetails_auditdata, vendor_id, user_id, req_status, taxsubdetails.id, VendorRefType.VENDOR_SUPPLIERSUBTAX,
                                    Audit_Action)
            # except IntegrityError as error:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except SupplierTax.DoesNotExist:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_tax_ID)
            #     error_obj.set_description(ErrorDescription.INVALID_tax_ID)
            #     return error_obj
            # except:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj
        else:
            # try:
                if tax_obj.isexcempted=="Y":
                    if tax_obj.excemfrom==None:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.INVALID_DATA)
                        error_obj.set_description(ErrorDescription.INVALID_DATA)
                        return error_obj
                    if tax_obj.excemto==None:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.INVALID_DATA)
                        error_obj.set_description(ErrorDescription.INVALID_DATA)
                        return error_obj
                    if tax_obj.excemthrosold==None:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.INVALID_DATA)
                        error_obj.set_description(ErrorDescription.INVALID_DATA)
                        return error_obj
                if tax_obj.isexcempted == "N":
                    if tax_obj.excemfrom != None:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.INVALID_DATA)
                        error_obj.set_description(ErrorDescription.INVALID_DATA)
                        return error_obj
                    if tax_obj.excemto != None:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.INVALID_DATA)
                        error_obj.set_description(ErrorDescription.INVALID_DATA)
                        return error_obj
                    if tax_obj.excemthrosold != 0:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.INVALID_DATA)
                        error_obj.set_description(ErrorDescription.INVALID_DATA)
                        return error_obj
                # branch_obj=SupplierBranch.objects.get(id=branch_id)
                # vendor_id=branch_obj.vendor.id
                # vendor_code=branch_obj.vendor.code
                tax = SupplierTax.objects.using(self._current_app_schema()).create(branch_id='',vendor_id=tax_obj.get_vendor(),vendor_code=tax_obj.get_vendorcode(),
                                                 tax_id=tax_obj.get_tax(), subtax_id=tax_obj.get_subtax(),
                                                 msme=tax_obj.get_msme(), type=tax_obj.get_type(),
                                                 panno=tax_obj.get_panno(),msme_reg_no=tax_obj.get_msme_reg_no(),
                                                 created_by=user_id, entity_id=self._entity_id(),portal_flag=tax_obj.get_portal_flag())

                taxdetails_id = tax.id
                taxsubdetails = SupplierSubTax.objects.using(self._current_app_schema()).create(suppliertax_id=taxdetails_id,
                                                              isexcempted=tax_obj.get_isexcempted(),
                                                              excemfrom=tax_obj.get_excemfrom(),
                                                              excemto=tax_obj.get_excemto(),
                                                              excemthrosold=tax_obj.get_excemthrosold(),
                                                              rate_id=tax_obj.get_taxrate(),
                                                              excemrate=tax_obj.get_excemrate(),
                                                              attachment=ref_id,
                                                              created_by=user_id, entity_id=self._entity_id(),
                                                              portal_flag=tax_obj.get_portal_flag())
                vendor_service=VendorService(self._scope())
                # vendor_check = vendor_service.branchvalidate(branch_id)
                # if vendor_check == True:
                #     vendor_branchupdate = SupplierBranch.objects.filter(id=branch_id).update(is_validate=True)
                # else:
                #     vendor_branchupdate = SupplierBranch.objects.filter(id=branch_id).update(is_validate=False)

                # audit
                Audit_Action = ModifyStatus.create
                self.audit_function(tax, vendor_id, user_id, req_status, tax.id, VendorRefType.VENDOR_SUPPLIERTAX, Audit_Action)
                self.audit_function(taxsubdetails, vendor_id, user_id, req_status, taxsubdetails.id, VendorRefType.VENDOR_SUPPLIERSUBTAX,
                                    Audit_Action)
            # except IntegrityError as error:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except SupplierTax.DoesNotExist:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_tax_ID)
            #     error_obj.set_description(ErrorDescription.INVALID_tax_ID)
            #     return error_obj
            # except:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj


        tax_data = TaxResponse()
        tax_data.set_id(tax.id)
        tax_data.set_msme(tax.msme)
        tax_data.set_msme_reg_no(tax.msme_reg_no)
        tax_data.set_panno(tax.panno)
        tax_data.set_isexcempted(taxsubdetails.isexcempted)
        tax_data.set_excemfrom(taxsubdetails.excemfrom)
        tax_data.set_excemto(taxsubdetails.excemto)
        tax_data.set_excemthrosold(taxsubdetails.excemthrosold)
        tax_data.set_excemrate(taxsubdetails.excemrate)
        tax_data.set_portal_flag(taxsubdetails.portal_flag)
        ## tax_data.set_attachment(taxsubdetails.attachment)

        return tax_data


    def fetch_suppliertax_list(self,request, vys_page,user_id,vendor_id):
        queue_arr = SupplierTax.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id, entity_id=self._entity_id()).values('id')
        condition = None
        for vendor in queue_arr:
            logger.info(str(vendor))
            if condition is None:
                condition = (Q(id__exact=vendor['id']) & (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1))&Q(entity_id=self._entity_id())
            else:
                condition |= (Q(id__exact=vendor['id'])& (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1))&Q(entity_id=self._entity_id())
        if condition is not None:
            taxlist = SupplierTax.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        else:
            taxlist = []

        vlist = NWisefinList()
        user_list = []
        for vendor in taxlist:
            user_list.append(vendor.created_by)
        user_list = set(user_list)
        user_list = list(user_list)
        utility_service = NWisefinUtilityService()
        user_list_obj = utility_service.get_user_info(request, user_list)

        for tax in taxlist:
            taxsubdetails = SupplierSubTax.objects.using(self._current_app_schema()).get(suppliertax_id=tax.id, entity_id=self._entity_id())
            taxsubdetails = taxsubdetails
            tax_data = TaxResponse()
            tax_data.set_id(tax.id)
            tax_data.set_msme(tax.msme)
            tax_data.set_msme_reg_no(tax.msme_reg_no)
            # tax_data.set_type(tax.type)
            tax_data.set_panno(tax.panno)
            tax_data.set_vendor(tax.vendor_id)
            tax_data.set_modify_ref_id(tax.modify_ref_id)
            tax_data.set_modify_status(tax.modify_status)
            tax_data.set_isexcempted(taxsubdetails.isexcempted)
            tax_data.set_excemfrom(taxsubdetails.excemfrom)
            tax_data.set_excemto(taxsubdetails.excemto)
            tax_data.set_excemthrosold(taxsubdetails.excemthrosold)
            tax_data.set_tax(tax.tax_id)
            tax_data.set_subtax(tax.subtax_id)
            tax_data.set_taxrate(taxsubdetails.rate_id)
            tax_data.set_excemrate(taxsubdetails.excemrate)
            tax_data.set_created_by(taxsubdetails.created_by)
            tax_data.set_portal_flag(taxsubdetails.portal_flag)


            for ul in user_list_obj['data']:
                if ul['id'] == SupplierTax.created_by:
                    tax_data.set_created_by(ul)
            vlist.append(tax_data)
        vpage = NWisefinPaginator(taxlist, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist



    def get_suppliertax_list_using_subtax_id(self,vendor_id,subtax_id):

        condition = (Q(id=vendor_id,subtax_id=subtax_id) & (Q(modify_status=-1) |Q(modify_status=0))&
                     Q(modified_by=-1))&Q(entity_id=self._entity_id())
        taxlist = SupplierTax.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')

        vlist = []
        if len(taxlist) > 0:
            for tax in taxlist:
                taxsubdetails = SupplierSubTax.objects.using(self._current_app_schema()).get(suppliertax_id=tax.id, entity_id=self._entity_id())
                taxsubdetails = taxsubdetails
                tax_data = TaxResponse()
                tax_data.set_id(tax.id)
                tax_data.set_msme(tax.msme)
                tax_data.set_msme_reg_no(tax.msme_reg_no)
                tax_data.set_panno(tax.panno)
                tax_data.set_vendor(tax.vendor_id)
                tax_data.set_modify_ref_id(tax.modify_ref_id)
                tax_data.set_modify_status(tax.modify_status)
                tax_data.set_isexcempted(taxsubdetails.isexcempted)
                tax_data.set_excemfrom(taxsubdetails.excemfrom)
                tax_data.set_excemto(taxsubdetails.excemto)
                tax_data.set_excemthrosold(taxsubdetails.excemthrosold)
                tax_data.set_tax(tax.tax_id)
                tax_data.set_subtax(tax.subtax_id)
                tax_data.set_taxrate(taxsubdetails.rate_id)
                tax_data.set_excemrate(taxsubdetails.excemrate)
                tax_data.set_created_by(taxsubdetails.created_by)
                tax_data.set_portal_flag(taxsubdetails.portal_flag)
                vlist.append(tax_data)
        return vlist

    def get_suppliertax_list_using_vendor_id(self, vendor_id, subtax_id):

        condition = (Q(vendor_id=vendor_id, subtax_id=subtax_id) & (Q(modify_status=-1) | Q(modify_status=-1)) &
                     Q(modified_by=-1)) & Q(entity_id=self._entity_id())
        taxlist = SupplierTax.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')

        vlist = NWisefinList ()
        if len(taxlist) > 0:
            for tax in taxlist:
                taxsubdetails = SupplierSubTax.objects.using(self._current_app_schema()).get(suppliertax_id=tax.id,
                                                                                             entity_id=self._entity_id())
                taxsubdetails = taxsubdetails
                tax_data = TaxResponse()
                tax_data.set_id(tax.id)
                tax_data.set_msme(tax.msme)
                tax_data.set_msme_reg_no(tax.msme_reg_no)
                tax_data.set_panno(tax.panno)
                tax_data.set_vendor(tax.vendor_id)
                tax_data.set_modify_ref_id(tax.modify_ref_id)
                tax_data.set_modify_status(tax.modify_status)
                tax_data.set_isexcempted(taxsubdetails.isexcempted)
                tax_data.set_excemfrom(taxsubdetails.excemfrom)
                tax_data.set_excemto(taxsubdetails.excemto)
                tax_data.set_excemthrosold(taxsubdetails.excemthrosold)
                tax_data.set_tax(tax.tax_id)
                tax_data.set_subtax(tax.subtax_id)
                tax_data.set_taxrate(taxsubdetails.rate_id)
                tax_data.set_excemrate(taxsubdetails.excemrate)
                tax_data.set_created_by(taxsubdetails.created_by)
                tax_data.set_portal_flag(taxsubdetails.portal_flag)
                vlist.append(tax_data)
        return vlist

    def fetch_suppliertax(self,tax_id):
        try:
            tax = SupplierTax.objects.using(self._current_app_schema()).get(id=tax_id, entity_id=self._entity_id())
            taxsubdetails = SupplierSubTax.objects.using(self._current_app_schema()).get(suppliertax_id=tax.id, entity_id=self._entity_id())
            tax_data = TaxResponse()
            tax_data.set_id(tax.id)
            tax_data.set_msme(tax.msme)
            tax_data.set_msme_reg_no(tax.msme_reg_no)
            # tax_data.set_type(tax.type)
            tax_data.set_panno(tax.panno)
            tax_data.set_tax(tax.tax_id)
            tax_data.set_subtax(tax.subtax_id)
            tax_data.set_vendor(tax.vendor_id)
            tax_data.set_isexcempted(taxsubdetails.isexcempted)
            tax_data.set_excemfrom(taxsubdetails.excemfrom)
            tax_data.set_excemto(taxsubdetails.excemto)
            tax_data.set_excemrate(taxsubdetails.excemrate)
            tax_data.set_taxrate(taxsubdetails.rate_id)
            tax_data.set_excemthrosold(taxsubdetails.excemthrosold)
            # tax_data.set_attachment(taxsubdetails.attachment)
            tax_data.set_created_by(taxsubdetails.created_by)
            tax_data.set_modify_ref_id(tax.modify_ref_id)
            tax_data.set_modify_status(tax.modify_status)
            tax_data.set_portal_flag(tax.portal_flag)

            return tax_data

        except SupplierTax.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_tax_ID)
            error_obj.set_description(ErrorDescription.INVALID_tax_ID)
            return error_obj

    def delete_suppliertax(self,tax_id,user_id,vendor_id,branch_id):

        subtax_id = SupplierSubTax.objects.using(self._current_app_schema()).get(suppliertax_id=tax_id, entity_id=self._entity_id())
        subtax_id = subtax_id.id
        tax = SupplierTax.objects.using(self._current_app_schema()).filter(id=tax_id, entity_id=self._entity_id()).delete()
        subtax = SupplierSubTax.objects.using(self._current_app_schema()).filter(suppliertax_id=tax_id, entity_id=self._entity_id()).delete()
        vendor_service = VendorService(self._scope())
        # vendor_check = vendor_service.branchvalidate(branch_id)
        # if vendor_check == True:
        #     vendor_branchupdate = SupplierBranch.objects.filter(id=branch_id).update(is_validate=True)
        # else:
        #     vendor_branchupdate = SupplierBranch.objects.filter(id=branch_id).update(is_validate=False)

        req_status = RequestStatusUtil.ONBOARD
        Audit_Action = ModifyStatus.delete
        self.audit_function(tax, vendor_id, user_id, req_status, tax_id, VendorRefType.VENDOR_SUPPLIERTAX,
                            Audit_Action)
        self.audit_function(subtax, vendor_id, user_id, req_status, subtax_id,
                            VendorRefType.VENDOR_SUPPLIERTAX, Audit_Action)

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

    # modification
    def modification_create_suppliertax(self, tax_obj,branch_id, user_id, ref_id,vendor_id):

        req_status = RequestStatusUtil.MODIFICATION
        vendor_service = VendorService(self._scope())
        if not tax_obj.get_id() is None:
            # try:
                ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_SUPPLIERTAX, tax_obj.get_id())
                if ref_flag==True:
                    if tax_obj.isexcempted == "Y":
                        if tax_obj.excemfrom == None:
                            error_obj = NWisefinError()
                            error_obj.set_code(ErrorMessage.INVALID_DATA)
                            error_obj.set_description(ErrorDescription.INVALID_DATA)
                            return error_obj
                        if tax_obj.excemto == None:
                            error_obj = NWisefinError()
                            error_obj.set_code(ErrorMessage.INVALID_DATA)
                            error_obj.set_description(ErrorDescription.INVALID_DATA)
                            return error_obj
                        if tax_obj.excemthrosold == None:
                            error_obj = NWisefinError()
                            error_obj.set_code(ErrorMessage.INVALID_DATA)
                            error_obj.set_description(ErrorDescription.INVALID_DATA)
                            return error_obj
                    if tax_obj.isexcempted == "N":
                        if tax_obj.excemfrom != None:
                            error_obj = NWisefinError()
                            error_obj.set_code(ErrorMessage.INVALID_DATA)
                            error_obj.set_description(ErrorDescription.INVALID_DATA)
                            return error_obj
                        if tax_obj.excemto != None:
                            error_obj = NWisefinError()
                            error_obj.set_code(ErrorMessage.INVALID_DATA)
                            error_obj.set_description(ErrorDescription.INVALID_DATA)
                            return error_obj
                        if tax_obj.excemthrosold != 0:
                            error_obj = NWisefinError()
                            error_obj.set_code(ErrorMessage.INVALID_DATA)
                            error_obj.set_description(ErrorDescription.INVALID_DATA)
                            return error_obj

                    tax = SupplierTax.objects.using(self._current_app_schema()).filter(id=tax_obj.get_id(), entity_id=self._entity_id()).update(tax_id=tax_obj.get_tax(),
                         subtax_id=tax_obj.get_subtax(),msme=tax_obj.get_msme(),type=tax_obj.get_type(),msme_reg_no=tax_obj.get_msme_reg_no(),
                         panno=tax_obj.get_panno(),portal_flag=tax_obj.get_portal_flag())
                    tax=SupplierTax.objects.using(self._current_app_schema()).get(id=tax_obj.get_id(), entity_id=self._entity_id())

                    taxsubdetails = SupplierSubTax.objects.using(self._current_app_schema()).filter(suppliertax_id=tax_obj.get_id(), entity_id=self._entity_id()).update(isexcempted=tax_obj.get_isexcempted(),
                        excemfrom=tax_obj.get_excemfrom(),excemto=tax_obj.get_excemto(),
                        excemthrosold=tax_obj.get_excemthrosold(),excemrate=tax_obj.get_excemrate(),
                        rate_id=tax_obj.get_taxrate(),attachment=ref_id,portal_flag=tax_obj.get_portal_flag())
                    taxsubdetails=SupplierSubTax.objects.using(self._current_app_schema()).get(suppliertax_id=tax_obj.get_id(), entity_id=self._entity_id())
                else:
                    if tax_obj.isexcempted == "Y":
                        if tax_obj.excemfrom == None:
                            error_obj = NWisefinError()
                            error_obj.set_code(ErrorMessage.INVALID_DATA)
                            error_obj.set_description(ErrorDescription.INVALID_DATA)
                            return error_obj
                        if tax_obj.excemto == None:
                            error_obj = NWisefinError()
                            error_obj.set_code(ErrorMessage.INVALID_DATA)
                            error_obj.set_description(ErrorDescription.INVALID_DATA)
                            return error_obj
                        if tax_obj.excemthrosold == None:
                            error_obj = NWisefinError()
                            error_obj.set_code(ErrorMessage.INVALID_DATA)
                            error_obj.set_description(ErrorDescription.INVALID_DATA)
                            return error_obj
                    if tax_obj.isexcempted == "N":
                        if tax_obj.excemfrom != None:
                            error_obj = NWisefinError()
                            error_obj.set_code(ErrorMessage.INVALID_DATA)
                            error_obj.set_description(ErrorDescription.INVALID_DATA)
                            return error_obj
                        if tax_obj.excemto != None:
                            error_obj = NWisefinError()
                            error_obj.set_code(ErrorMessage.INVALID_DATA)
                            error_obj.set_description(ErrorDescription.INVALID_DATA)
                            return error_obj
                        if tax_obj.excemthrosold != 0:
                            error_obj = NWisefinError()
                            error_obj.set_code(ErrorMessage.INVALID_DATA)
                            error_obj.set_description(ErrorDescription.INVALID_DATA)
                            return error_obj
                    # branch_obj = SupplierBranch.objects.get(id=branch_id)
                    # vendor_id = branch_obj.vendor.id
                    # vendor_code = branch_obj.vendor.code

                    tax = SupplierTax.objects.using(self._current_app_schema()).create(branch_id='', tax_id=tax_obj.get_tax(),vendor_id=tax_obj.get_vendor(),vendor_code=tax_obj.get_vendorcode(),
                                                     subtax_id=tax_obj.get_subtax(), msme=tax_obj.get_msme(),
                                                     type=tax_obj.get_type(),msme_reg_no=tax_obj.get_msme_reg_no(),
                                                     panno=tax_obj.get_panno(), created_by=user_id,
                                                     modify_status=ModifyStatus.update,
                                                     modified_by=user_id, modify_ref_id=tax_obj.get_id(), entity_id=self._entity_id(),portal_flag=tax_obj.get_portal_flag())

                    taxsubdetails = SupplierSubTax.objects.using(self._current_app_schema()).create(suppliertax_id=tax.id,
                                                                  isexcempted=tax_obj.get_isexcempted(),
                                                                  excemfrom=tax_obj.get_excemfrom(),
                                                                  excemto=tax_obj.get_excemto(),
                                                                  excemthrosold=tax_obj.get_excemthrosold(),
                                                                  excemrate=tax_obj.get_excemrate(),
                                                                  rate_id=tax_obj.get_taxrate(), attachment=ref_id,
                                                                  created_by=user_id, modified_by=user_id, entity_id=self._entity_id(),portal_flag=tax_obj.get_portal_flag())

                    tax_update = SupplierTax.objects.using(self._current_app_schema()).filter(id=tax_obj.get_id(), entity_id=self._entity_id()).update(modify_ref_id=tax.id)
                    taxupdate_auditdata={'id':tax_obj.get_id(),'modify_ref_id':tax.id}

                    VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=tax_obj.get_id(),
                                                         ref_type=VendorRefType.VENDOR_SUPPLIERTAX,
                                                         mod_status=ModifyStatus.update,
                                                         modify_ref_id=tax.id, entity_id=self._entity_id())


                # audit
                # ref_type_tax = VendorRefType.VENDOR_SUPPLIERTAX
                # self.audit_function(tax, vendor_id, user_id, req_status, tax.id, ref_type_tax, ModifyStatus.create)
                # ref_type_subtax = VendorRefType.VENDOR_SUPPLIERSUBTAX
                # self.audit_function(taxsubdetails, vendor_id, user_id, req_status, taxsubdetails.id, ref_type_subtax,
                #                     ModifyStatus.create)
                # tax_id = tax_obj.get_id()
                # self.audit_function(taxupdate_auditdata, vendor_id, user_id, req_status, tax_id, ref_type_tax, ModifyStatus.update)

                # tax = SupplierTax.objects.get(id=tax.id)
                # taxsubdetails = SupplierSubTax.objects.get(suppliertax_id=tax_obj.get_id())

            # except IntegrityError as error:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except SupplierTax.DoesNotExist:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_tax_ID)
            #     error_obj.set_description(ErrorDescription.INVALID_tax_ID)
            #     return error_obj
            # except:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj
        else:
            if tax_obj.isexcempted == "Y":
                if tax_obj.excemfrom == None:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
                if tax_obj.excemto == None:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
                if tax_obj.excemthrosold == None:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
            if tax_obj.isexcempted == "N":
                if tax_obj.excemfrom != None:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
                if tax_obj.excemto != None:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
                if tax_obj.excemthrosold != 0:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
            # branch_obj = SupplierBranch.objects.get(id=branch_id)
            # vendor_id = branch_obj.vendor.id
            # vendor_code = branch_obj.vendor.code
            tax = SupplierTax.objects.using(self._current_app_schema()).create(branch_id='',tax_id=tax_obj.get_tax(), subtax_id=tax_obj.get_subtax(),
                                             vendor_id=tax_obj.get_vendor(),vendor_code=tax_obj.get_vendorcode(),
                  msme=tax_obj.get_msme(), type=tax_obj.get_type(),panno=tax_obj.get_panno(),created_by=user_id,msme_reg_no=tax_obj.get_msme_reg_no(),
                  modify_status=ModifyStatus.create,modified_by=user_id, entity_id=self._entity_id(),portal_flag=tax_obj.get_portal_flag())

            taxsubdetails = SupplierSubTax.objects.using(self._current_app_schema()).create(suppliertax_id=tax.id,isexcempted=tax_obj.get_isexcempted(),
                            excemfrom=tax_obj.get_excemfrom(),excemto=tax_obj.get_excemto(),
                            excemthrosold=tax_obj.get_excemthrosold(),rate_id=tax_obj.get_taxrate(),
                            excemrate=tax_obj.get_excemrate(),attachment=ref_id,created_by=user_id,
                            modify_status=ModifyStatus.create,modified_by=user_id, entity_id=self._entity_id(), portal_flag=tax_obj.get_portal_flag())
            VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=tax.id,
                                                 ref_type=VendorRefType.VENDOR_SUPPLIERTAX, mod_status=ModifyStatus.create,
                                                 modify_ref_id=tax.id, entity_id=self._entity_id())

            tax.modify_ref_id = tax.id
            tax.save()
            # vendor_check = vendor_service.branchvalidate(branch_id)
            # if vendor_check == True:
            #     vendor_branchupdate = SupplierBranch.objects.filter(id=branch_id).update(is_validate=True)
            # else:
            #     vendor_branchupdate = SupplierBranch.objects.filter(id=branch_id).update(is_validate=False)

            # audit
            Audit_Action = ModifyStatus.create
            self.audit_function(tax, vendor_id, user_id, req_status, tax.id, VendorRefType.VENDOR_SUPPLIERTAX, Audit_Action)
            self.audit_function(taxsubdetails, vendor_id, user_id, req_status, taxsubdetails.id, VendorRefType.VENDOR_SUPPLIERSUBTAX,
                                Audit_Action)


        tax_data = TaxResponse()
        tax_data.set_id(tax.id)
        tax_data.set_msme(tax.msme)
        tax_data.set_msme_reg_no(tax.msme_reg_no)
        tax_data.set_panno(tax.panno)
        tax_data.set_isexcempted(taxsubdetails.isexcempted)
        tax_data.set_excemfrom(taxsubdetails.excemfrom)
        tax_data.set_excemto(taxsubdetails.excemto)
        tax_data.set_excemthrosold(taxsubdetails.excemthrosold)
        tax_data.set_excemrate(taxsubdetails.excemrate)
        tax_data.set_portal_flag(taxsubdetails.portal_flag)

        return tax_data

    def modification_delete_suppliertax(self, tax_id,user_id, vendor_id,branch_id):
        try :
            vendor_service = VendorService(self._scope())
            tax_update = SupplierTax.objects.using(self._current_app_schema()).filter(id=tax_id, entity_id=self._entity_id()).update(
                modify_ref_id=tax_id,modify_status=ModifyStatus.delete)
            ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_SUPPLIERTAX, tax_id)
            if ref_flag == True:
                flag_obj = VendorModificationRel.objects.using(self._current_app_schema()).filter(
                    Q(modify_ref_id=tax_id) & Q(ref_type=VendorRefType.VENDOR_SUPPLIERTAX)&Q(entity_id=self._entity_id())).update(
                    mod_status=ModifyStatus.delete)
            else:
                VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=tax_id,
                                                     ref_type=VendorRefType.VENDOR_SUPPLIERTAX,
                                                     mod_status=ModifyStatus.delete,
                                                     modify_ref_id=tax_id, entity_id=self._entity_id())

            # vendor_check = vendor_service.branchvalidate(branch_id)
            # if vendor_check == True:
            #     vendor_branchupdate = SupplierBranch.objects.filter(id=branch_id).update(is_validate=True)
            # else:
            #     vendor_branchupdate = SupplierBranch.objects.filter(id=branch_id).update(is_validate=False)

            # audit
            req_status = RequestStatusUtil.MODIFICATION
            ref_type = VendorRefType.VENDOR_SUPPLIERTAX
            # self.audit_function(tax_update, vendor_id, user_id, req_status, tax_id, ref_type, ModifyStatus.update)

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
        except :
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj

    def modification_action_suppliertax(self,mod_status,old_id,new_id,vendor_id,user_id):

        req_status = RequestStatusUtil.MODIFICATION
        if mod_status == ModifyStatus.update:
            tax_obj = self.fetch_suppliertax(new_id)

            tax_update = SupplierTax.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(
                tax_id =tax_obj.get_tax(),subtax_id =tax_obj.get_subtax(),msme =tax_obj.get_msme(),msme_reg_no=tax_obj.get_msme_reg_no(),
                type =tax_obj.get_type(),panno=tax_obj.get_panno(),modify_status=-1,modify_ref_id = -1,modified_by=-1,portal_flag=tax_obj.get_portal_flag())

            doc_file = VendorFileAttachment.objects.using(self._current_app_schema()).filter(
                Q(representtabel_id=new_id) & Q(tab_type=VendorRefType.VENDOR_SUPPLIERTAX)&Q(entity_id=self._entity_id())).update(
                representtabel_id=old_id)

            if tax_obj.get_excemfrom()==str(None):
                from_date=None
            else:
                from_date= tax_obj.get_excemfrom()

            if tax_obj.get_excemto() == str(None):
                to_date = None
            else:
                to_date = tax_obj.get_excemto()

            subtax_update = SupplierSubTax.objects.using(self._current_app_schema()).filter(suppliertax_id=old_id, entity_id=self._entity_id()).update(
                isexcempted=tax_obj.get_isexcempted(),
                excemfrom=from_date,
                excemto=to_date,
                excemthrosold=tax_obj.get_excemthrosold(),
                excemrate=tax_obj.get_excemrate(),
                rate_id=tax_obj.get_taxrate(),
                attachment=tax_obj.get_attachment(),modify_status=-1,modify_ref_id = -1,modified_by=-1,
                portal_flag=tax_obj.get_portal_flag()
            )

            # audit
            action_update = ModifyStatus.update
            subt_id = SupplierSubTax.objects.using(self._current_app_schema()).get(suppliertax_id=old_id, entity_id=self._entity_id())
            subt_id = subt_id.id
            self.audit_function(tax_update, vendor_id, user_id, req_status, old_id,VendorRefType.VENDOR_SUPPLIERTAX, action_update)
            self.audit_function(subtax_update, vendor_id, user_id, req_status, subt_id,VendorRefType.VENDOR_SUPPLIERSUBTAX, action_update)
            # self.audit_function(tax, vendor_id, user_id, req_status, old_id, VendorRefType.VENDOR_SUPPLIERTAX, ModifyStatus.delete)
            # self.audit_function(subtax, vendor_id, user_id, req_status, subt_new_id, VendorRefType.VENDOR_SUPPLIERSUBTAX, ModifyStatus.delete)

        elif mod_status == ModifyStatus.create:
            tax=SupplierTax.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).update(modify_status=-1,modify_ref_id=-1,modified_by=-1)

            subtax=SupplierSubTax.objects.using(self._current_app_schema()).filter(suppliertax_id=new_id, entity_id=self._entity_id()).update(modify_status=-1,
                                                         modify_ref_id=-1,modified_by=-1)
            # audit
            self.audit_function(tax, vendor_id, user_id, req_status, old_id, VendorRefType.VENDOR_SUPPLIERTAX,
                                ModifyStatus.delete)
            subtax_id = SupplierSubTax.objects.using(self._current_app_schema()).get(suppliertax_id=new_id, entity_id=self._entity_id())
            subtax_id = subtax_id.id
            self.audit_function(subtax, vendor_id, user_id, req_status, subtax_id, VendorRefType.VENDOR_SUPPLIERSUBTAX,
                                ModifyStatus.delete)
        else:
            tax=SupplierTax.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).delete()
            # subt_new_id = SupplierSubTax.objects.get(suppliertax_id=old_id)
            # subt_new_id = subt_new_id.id
            # subtax=SupplierSubTax.objects.filter(suppliertax_id=old_id).delete()
            # audit
            self.audit_function(tax, vendor_id, user_id, req_status, old_id, VendorRefType.VENDOR_SUPPLIERTAX,
                                ModifyStatus.delete)

            # self.audit_function(subtax, vendor_id, user_id, req_status, subt_new_id, VendorRefType.VENDOR_SUPPLIERSUBTAX,
            #                     ModifyStatus.delete)

        return


    def get_vendor_id(self,branch_id):
        branch = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).get()
        vendor_id = branch.vendor_id
        return vendor_id

    def modification_reject_suppliertax(self, mod_status, old_id, new_id, vendor_id, user_id):

        req_status = RequestStatusUtil.MODIFICATION
        if mod_status == ModifyStatus.update:
            subtax_id = SupplierSubTax.objects.using(self._current_app_schema()).get(suppliertax_id=new_id, entity_id=self._entity_id())
            subtax_id = subtax_id.id
            tax = SupplierTax.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()
            subtax = SupplierSubTax.objects.using(self._current_app_schema()).filter(suppliertax_id=new_id, entity_id=self._entity_id()).delete()
            tax_update = SupplierTax.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(modify_ref_id=-1)
            # audit
            self.audit_function(tax, vendor_id, user_id, req_status, new_id, VendorRefType.VENDOR_SUPPLIERTAX,
                                ModifyStatus.delete)
            self.audit_function(subtax, vendor_id, user_id, req_status, subtax_id,
                                VendorRefType.VENDOR_SUPPLIERSUBTAX, ModifyStatus.delete)
            self.audit_function(tax_update, vendor_id, user_id, req_status, old_id, VendorRefType.VENDOR_SUPPLIERTAX,
                                ModifyStatus.update)
        elif mod_status == ModifyStatus.create:
            subtax_id = SupplierSubTax.objects.using(self._current_app_schema()).get(suppliertax_id=new_id, entity_id=self._entity_id())
            subtax_id = subtax_id.id
            tax = SupplierTax.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()
            subtax = SupplierSubTax.objects.using(self._current_app_schema()).filter(suppliertax_id=new_id, entity_id=self._entity_id()).delete()
            # audit
            self.audit_function(tax, vendor_id, user_id, req_status, new_id, VendorRefType.VENDOR_SUPPLIERTAX,
                                ModifyStatus.delete)
            self.audit_function(subtax, vendor_id, user_id, req_status, subtax_id,
                                VendorRefType.VENDOR_SUPPLIERSUBTAX, ModifyStatus.delete)
        else:
            tax = SupplierTax.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(modify_ref_id=-1)
            # audit
            self.audit_function(tax, vendor_id, user_id, req_status, old_id, VendorRefType.VENDOR_SUPPLIERTAX,
                                ModifyStatus.delete)
        return

    def audit_function(self,tax_data,vendor_id,user_id,req_status,id,ref_type,action):

        if action == ModifyStatus.delete:
            data = None
        elif action == ModifyStatus.update:
            data = tax_data
        else:
            data = tax_data.__dict__
            del data['_state']
        audit_service = VendorAuditService(self._scope())
        audit_obj = VendorAuditResponse()
        audit_obj.set_refid(vendor_id)
        audit_obj.set_reftype(VendorRefType.VENDOR)
        audit_obj.set_userid(user_id)
        audit_obj.set_reqstatus(req_status)
        audit_obj.set_relrefid(id)
        audit_obj.set_relreftype(ref_type)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_vendoraudit(audit_obj)
        return

    def get_vendorstatus_tax(self,vendor_id):
        vendor = Vendor.objects.using(self._current_app_schema()).get(id=vendor_id, entity_id=self._entity_id())
        vobj = vendor.vendor_status

        return vobj

    def fetch_subtaxlist(self,subtax_ids):
        # subtax_ids = json.loads(request.body)
        subtax_id2 = subtax_ids['vendor_id']
        obj = SupplierTax.objects.using(self._current_app_schema()).filter(vendor_id = subtax_id2, entity_id=self._entity_id()).values('id', 'branch_id','vendor_id','subtax_id')
        subtax_list_data = NWisefinList()
        for i in obj:
            data = {"id": i['id'], "branch_id": i['branch_id'], "vendor_id": i['vendor_id'],
                    "subtax_id": i['subtax_id']}
            subtax_list_data.append(data)
        return subtax_list_data.get()

    def update_tax(self, tax, subtax, employee_id, vendor_id, new_pan):
        ref_id = 0
        vendor_service = VendorService(self._scope())
        ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_SUPPLIERTAX, tax.id)
        if ref_flag==True:
            tax = SupplierTax.objects.using(self._current_app_schema()).filter(id=tax.id, entity_id=self._entity_id()).update(
                 panno=new_pan)

        else:
            tax_data = SupplierTax.objects.using(self._current_app_schema()).create(branch_id='', tax_id=tax.tax_id,vendor_id=tax.vendor_id,vendor_code=tax.vendor_code,
                                             subtax_id=tax.subtax_id, msme=tax.msme,
                                             type=tax.type,msme_reg_no=tax.msme_reg_no,
                                             panno=new_pan, created_by=employee_id,
                                             modify_status=ModifyStatus.update,
                                             modified_by=employee_id, modify_ref_id=tax.id, entity_id=self._entity_id(),portal_flag=tax.portal_flag)

            taxsubdetails = SupplierSubTax.objects.using(self._current_app_schema()).create(suppliertax_id=tax_data.id,
                                                          isexcempted=subtax.isexcempted,
                                                          excemfrom=subtax.excemfrom,
                                                          excemto=subtax.excemto,
                                                          excemthrosold=subtax.excemthrosold,
                                                          excemrate=subtax.excemrate,
                                                          rate_id=subtax.rate_id, attachment=ref_id,
                                                          created_by=employee_id, modified_by=employee_id, entity_id=self._entity_id(),portal_flag=subtax.portal_flag)

            tax_update = SupplierTax.objects.using(self._current_app_schema()).filter(id=tax.id, entity_id=self._entity_id()).update(modify_ref_id=tax_data.id)

            VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=tax.id,
                                                 ref_type=VendorRefType.VENDOR_SUPPLIERTAX,
                                                 mod_status=ModifyStatus.update,
                                                 modify_ref_id=tax_data.id, entity_id=self._entity_id())

    def update_tax_pan(self, employee_id, vendor_id, new_pan):
        tax_list = SupplierTax.objects.using(self._current_app_schema()).filter(vendor_id = vendor_id,entity_id=self._entity_id(),modify_status=-1)
        for tax in tax_list:
            sub_tax = SupplierSubTax.objects.using(self._current_app_schema()).filter(suppliertax_id=tax.id, entity_id=self._entity_id())
            mod_tax = SupplierTax.objects.using(self._current_app_schema()).filter(id=tax.modify_ref_id,entity_id=self._entity_id())
            if len(mod_tax) == 0:
                pan = self.update_tax(tax, sub_tax[0], employee_id, vendor_id, new_pan)
            else:
                pan = SupplierTax.objects.using(self._current_app_schema()).filter(id=mod_tax[0].id).update(panno=new_pan)

