import django
from django.db import IntegrityError

from vendorservice.data.response.paymentresponse import PaymentResponse
from vendorservice.models import SupplierPayment ,VendorQueue ,SupplierBranch,VendorModificationRel
from vendorservice.util.vendorutil import VendorRefType,ModifyStatus ,RequestStatusUtil
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from django.utils import timezone
from vendorservice.data.request.vendorauditrequest import VendorAuditRequest
from vendorservice.service.vendorauditservice import VendorAuditService,VendorAuditResponse
from vendorservice.service.vendorservice import VendorService
from utilityservice.service.utilityservice import NWisefinUtilityService
from django.db.models import Q
from masterservice.models import PayMode
from nwisefin.settings import logger
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace


class paymentservice(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_payment(self, payment_obj,user_id,branch_id,vendor_id):
        req_status = RequestStatusUtil.ONBOARD
        paymode = PayMode.objects.using(self._current_app_schema()).filter(id=payment_obj.get_paymode_id()).values('name')
        # paymode = PayMode.objects.get(id=payment_obj.get_id())
        if not payment_obj.get_id() is None:
            checkupdate = True
            # condition = Q(status=1)
                       # & Q(paymode_id__exact=payment_obj.get_paymode_id()) & Q(supplier__exact=payment_obj.get_supplier()) & Q(account_type__exact=payment_obj.get_account_type())\
                        #& Q(beneficiary__exact=payment_obj.get_beneficiary()) & Q(remarks__exact=payment_obj.get_remarks())
            # payment = SupplierPayment.objects.filter(condition)
            # paymentlist = []

            if  paymode[0]['name']=='DD':
                # checkupdate = False
                payment_update = SupplierPayment.objects.using(self._current_app_schema()).filter(id=payment_obj.get_id()).update(
                        supplier=payment_obj.get_supplier(),
                        paymode_id=payment_obj.get_paymode_id(), bank_id=0,
                        branch_id=0,
                        account_type=payment_obj.get_account_type(), account_no=payment_obj.get_account_no(),
                        beneficiary=payment_obj.get_beneficiary(), remarks=payment_obj.get_remarks(),
                        supplierbranch_id=branch_id, updated_by=user_id, updated_date=timezone.now(),portal_flag=payment_obj.get_portal_flag())

                payment_auditdata = {'id': payment_obj.get_id(), 'supplier': payment_obj.get_supplier(),
                                         'paymode_id': payment_obj.get_paymode_id(),
                                         'bank_id': payment_obj.get_bank_id(),
                                         'branch_id': payment_obj.get_branch_id(),
                                         'account_type': payment_obj.get_account_type(),
                                         'account_no': payment_obj.get_account_no(),
                                         'beneficiary': payment_obj.get_beneficiary(),
                                         'remarks': payment_obj.get_remarks(),
                                         'supplierbranch_id': branch_id, 'updated_by': user_id,
                                         'updated_date': timezone.now()}

                payment = SupplierPayment.objects.using(self._current_app_schema()).get(id=payment_obj.get_id())
                self.audit_function(payment_auditdata, vendor_id, user_id, req_status, payment.id,
                                        ModifyStatus.update)

                # if checkupdate == False :
                #     error_obj = Error()
                #     error_obj.set_code(ErrorMessage.DUPLICATE_ENTRY)
                #     error_obj.set_description(ErrorDescription.ACCOUNT_ALREADY_EXIST)
                #     return error_obj

            else:
                # error_obj = Error()
                # error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                # error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                # return error_obj
                try:
                    payment_update = SupplierPayment.objects.using(self._current_app_schema()).filter(id=payment_obj.get_id()).update(supplier=payment_obj.get_supplier(),
                        paymode_id=payment_obj.get_paymode_id(),bank_id=payment_obj.get_bank_id(),branch_id=payment_obj.get_branch_id(),
                        account_type=payment_obj.get_account_type(),account_no=payment_obj.get_account_no(),
                        beneficiary=payment_obj.get_beneficiary(),remarks=payment_obj.get_remarks(),
                        supplierbranch_id=branch_id,updated_by=user_id,updated_date=timezone.now(), portal_flag=payment_obj.get_portal_flag())
                    payment_auditdata={'id':payment_obj.get_id(),'supplier':payment_obj.get_supplier(),
                        'paymode_id':payment_obj.get_paymode_id(),'bank_id':payment_obj.get_bank_id(),'branch_id':payment_obj.get_branch_id(),
                        'account_type':payment_obj.get_account_type(),'account_no':payment_obj.get_account_no(),
                        'beneficiary':payment_obj.get_beneficiary(),'remarks':payment_obj.get_remarks(),
                        'supplierbranch_id':branch_id,'updated_by':user_id,'updated_date':timezone.now()}

                    payment = SupplierPayment.objects.using(self._current_app_schema()).get(id=payment_obj.get_id())
                    self.audit_function(payment_auditdata, vendor_id, user_id, req_status, payment.id, ModifyStatus.update)

                except IntegrityError as error:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
                except SupplierPayment.DoesNotExist:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_VENDORPAYMENT_ID)
                    error_obj.set_description(ErrorDescription.INVALID_VENDORPAYMENT_ID)
                    return error_obj
                except:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                    return error_obj
        else:
            # if payment_obj.get_branch_id() is not None:
            #     condition =  Q(status=1)
            #     payment = SupplierPayment.objects.filter(condition)
            # else:
            #     payment=[]


            # if len(payment) > 0 :
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.DUPLICATE_ENTRY)
            #     error_obj.set_description(ErrorDescription.ACCOUNT_ALREADY_EXIST)
            #     return error_obj

            try:

                payment = SupplierPayment.objects.using(self._current_app_schema()).create(supplier=payment_obj.get_supplier(),
                    paymode_id=payment_obj.get_paymode_id(),
                    bank_id=payment_obj.get_bank_id(),branch_id=payment_obj.get_branch_id(),
                    account_type=payment_obj.get_account_type(),account_no=payment_obj.get_account_no(),
                    beneficiary=payment_obj.get_beneficiary(),remarks=payment_obj.get_remarks(),
                    supplierbranch_id=branch_id,created_by=user_id , entity_id=self._entity_id(),portal_flag=payment_obj.get_portal_flag())
                vendor_service=VendorService()
                vendor_check = vendor_service.branchvalidate(branch_id)
                if vendor_check == True:
                    vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id).update(is_validate=True)
                else:
                    vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id).update(is_validate=False)

                self.audit_function(payment, vendor_id, user_id, req_status, payment.id, ModifyStatus.create)
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

        payment_data = PaymentResponse()
        payment_data.set_id(payment.id)
        payment_data.set_supplier(payment.supplier)
        payment_data.set_paymode_id(payment.paymode_id)
        payment_data.set_bank_id(payment.bank_id)
        payment_data.set_branch_id(payment.branch_id)
        payment_data.set_account_type(payment.account_type)
        payment_data.set_account_no(payment.account_no)
        payment_data.set_beneficiary(payment.beneficiary)
        payment_data.set_remarks(payment.remarks)
        payment_data.set_supplierbranch_id(payment.supplierbranch_id)
        payment_data.set_status(payment.status)
        payment_data.set_is_active(payment.is_active)
        payment_data.set_created_by(payment.created_by)
        payment_data.set_portal_flag(payment.portal_flag)

        return payment_data

    def fetch_payment_list(self,request, vys_page,user_id,branch_id):
        queue_arr= SupplierPayment.objects.using(self._current_app_schema()).filter(supplierbranch_id=branch_id).values('id')
        condition = None
        for vendor in queue_arr:
            logger.error(str(vendor))
            if condition is None:
                condition = Q(id__exact=vendor['id']) & Q(status__exact=1) & (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1)
            else:
                condition |= Q(id__exact=vendor['id']) & Q(status__exact=1) & (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1)
        if condition is not None:
            paymentlist = SupplierPayment.objects.using(self._current_app_schema()).filter(condition).order_by('-id')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        else:
            paymentlist = []

        vlist = NWisefinList()
        user_list = []
        for vendor in paymentlist:
            user_list.append(vendor.created_by)
        user_list = set(user_list)
        user_list = list(user_list)
        utility_service = NWisefinUtilityService()
        user_list_obj = utility_service.get_user_info(request,user_list)

        for payment in paymentlist:
            payment_data = PaymentResponse()
            payment_data.set_id(payment.id)
            payment_data.set_supplier(payment.supplier)
            payment_data.set_paymode_id(payment.paymode_id)
            payment_data.set_bank_id(payment.bank_id)
            payment_data.set_branch_id(payment.branch_id)
            payment_data.set_account_type(payment.account_type)
            payment_data.set_account_no(payment.account_no)
            payment_data.set_beneficiary(payment.beneficiary)
            payment_data.set_remarks(payment.remarks)
            payment_data.set_supplierbranch_id(payment.supplierbranch_id)
            payment_data.set_created_by(payment.created_by)
            payment_data.set_modify_ref_id(payment.modify_ref_id)
            payment_data.set_modify_status(payment.modify_status)
            payment_data.set_is_active(payment.is_active)
            payment_data.set_portal_flag(payment.portal_flag)

            for ul in user_list_obj['data']:
                if ul['id'] == SupplierPayment.created_by:
                    payment_data.set_created_by(ul)
            vlist.append(payment_data)
        vpage = NWisefinPaginator(paymentlist, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist


    def fetch_payment(self, payment_id):
        try:
            payment = SupplierPayment.objects.using(self._current_app_schema()).get(id=payment_id)
            payment_data = PaymentResponse()
            payment_data.set_id(payment.id)
            payment_data.set_supplier(payment.supplier)
            payment_data.set_paymode_id(payment.paymode_id)
            payment_data.set_bank_id(payment.bank_id)
            payment_data.set_branch_id(payment.branch_id)
            payment_data.set_account_type(payment.account_type)
            payment_data.set_account_no(payment.account_no)
            payment_data.set_beneficiary(payment.beneficiary)
            payment_data.set_remarks(payment.remarks)
            payment_data.set_supplierbranch_id(payment.supplierbranch_id)
            payment_data.set_status(payment.status)
            payment_data.set_created_by(payment.created_by)
            payment_data.set_modify_ref_id(payment.modify_ref_id)
            payment_data.set_modify_status(payment.modify_status)
            payment_data.set_is_active(payment.is_active)
            payment_data.set_portal_flag(payment.portal_flag)
            return payment_data

        except SupplierPayment.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_VENDORPAYMENT_ID)
            error_obj.set_description(ErrorDescription.INVALID_VENDORPAYMENT_ID)
            return error_obj

    def inactive_payment(self, payment_id,vendor_id,user_id,branch_id):
        payment = SupplierPayment.objects.using(self._current_app_schema()).filter(id=payment_id).update(status=0)
        vendor_service=VendorService()
        vendor_check = vendor_service.branchvalidate(branch_id)
        if vendor_check == True:
            vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id).update(is_validate=True)
        else:
            vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id).update(is_validate=False)

        req_status = RequestStatusUtil.ONBOARD
        self.audit_function(payment, vendor_id, user_id, req_status, payment_id, ModifyStatus.update)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj

    def get_vendor_id(self,branch_id):
       branch = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id).get()
       vendor_id = branch.vendor_id
       return vendor_id

    # modification payment
    def payment_modification(self, payment_obj, user_id, branch_id,vendor_id):
        req_status = RequestStatusUtil.MODIFICATION
        vendor_service = VendorService()
        if not payment_obj.get_id() is None:
               # try:
                   ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_PAYMENT, payment_obj.get_id())
                   if ref_flag==True:
                       payment = SupplierPayment.objects.using(self._current_app_schema()).filter(id=payment_obj.get_id()).update(supplier=payment_obj.get_supplier(),
                                                                paymode_id=payment_obj.get_paymode_id(),
                                                                bank_id=payment_obj.get_bank_id(),
                                                                branch_id=payment_obj.get_branch_id(),
                                                                account_type=payment_obj.get_account_type(),
                                                                account_no=payment_obj.get_account_no(),
                                                                beneficiary=payment_obj.get_beneficiary(),
                                                                remarks=payment_obj.get_remarks(),
                                                                supplierbranch_id=branch_id,
                                                                portal_flag=payment_obj.get_portal_flag()
                                                                )
                       payment = SupplierPayment.objects.using(self._current_app_schema()).get(id=payment_obj.get_id())

                   else:
                       payment = SupplierPayment.objects.using(self._current_app_schema()).create(supplier=payment_obj.get_supplier(),
                                                                paymode_id=payment_obj.get_paymode_id(),
                                                                bank_id=payment_obj.get_bank_id(),
                                                                branch_id=payment_obj.get_branch_id(),
                                                                account_type=payment_obj.get_account_type(),
                                                                account_no=payment_obj.get_account_no(),
                                                                beneficiary=payment_obj.get_beneficiary(),
                                                                remarks=payment_obj.get_remarks(),
                                                                supplierbranch_id=branch_id, created_by=user_id,
                                                                modify_status=ModifyStatus.update,modify_ref_id=payment_obj.get_id(),
                                                                modified_by=user_id, entity_id=self._entity_id(), portal_flag=payment_obj.get_portal_flag())

                       payment_update=SupplierPayment.objects.using(self._current_app_schema()).filter(id=payment_obj.get_id()).update(modify_ref_id=payment.id)

                       paymentupdate_auditdata={'id':payment_obj.get_id(),'modify_ref_id':payment.id}
                       VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=payment_obj.get_id(),
                                                            ref_type=VendorRefType.VENDOR_PAYMENT, mod_status=ModifyStatus.update,
                                                            modify_ref_id=payment.id, entity_id=self._entity_id())


                   # audit
                   payment_update_id =payment_obj.get_id()
                   self.audit_function(payment, vendor_id, user_id, req_status, payment.id, ModifyStatus.create)
                   # self.audit_function(paymentupdate_auditdata, vendor_id, user_id, req_status, payment_update_id, ModifyStatus.update)

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
        else:
               # try:
                   payment = SupplierPayment.objects.using(self._current_app_schema()).create(supplier=payment_obj.get_supplier(),
                                                            paymode_id=payment_obj.get_paymode_id(),
                                                            bank_id=payment_obj.get_bank_id(),
                                                            branch_id=payment_obj.get_branch_id(),
                                                            account_type=payment_obj.get_account_type(),
                                                            account_no=payment_obj.get_account_no(),
                                                            beneficiary=payment_obj.get_beneficiary(),
                                                            remarks=payment_obj.get_remarks(),
                                                            supplierbranch_id=branch_id, created_by=user_id,
                                                            modify_status=ModifyStatus.create,modified_by=user_id, entity_id=self._entity_id(),portal_flag=payment_obj.get_portal_flag())
                   payment.modify_ref_id = payment.id
                   payment.save()

                   VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id,
                                                        ref_id=payment.id,
                                                        ref_type=VendorRefType.VENDOR_PAYMENT,
                                                        mod_status=ModifyStatus.create,
                                                        modify_ref_id=payment.id, entity_id=self._entity_id())

                   vendor_check = vendor_service.branchvalidate(branch_id)
                   if vendor_check == True:
                       vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id).update(is_validate=True)
                   else:
                       vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id).update(is_validate=False)

                   self.audit_function(payment, vendor_id, user_id, req_status, payment.id, ModifyStatus.create)


        payment_data = PaymentResponse()
        payment_data.set_id(payment.id)
        payment_data.set_paymode_id(payment.paymode_id)
        payment_data.set_bank_id(payment.bank_id)
        payment_data.set_branch_id(payment.branch_id)
        payment_data.set_account_type(payment.account_type)
        payment_data.set_account_no(payment.account_no)
        payment_data.set_beneficiary(payment.beneficiary)
        payment_data.set_remarks(payment.remarks)
        payment_data.set_supplierbranch_id(payment.supplierbranch_id)
        payment_data.set_status(payment.status)
        payment_data.set_created_by(payment.created_by)
        payment_data.set_is_active(payment.is_active)
        payment_data.set_portal_flag(payment.portal_flag)
        return payment_data


    def modification_delete_payment(self, payment_id, vendor_id,user_id,branch_id):
           try:
               vendor_service = VendorService()
               payment=SupplierPayment.objects.using(self._current_app_schema()).filter(id=payment_id).update(modify_ref_id=payment_id,modify_status=ModifyStatus.delete)
               ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_PAYMENT, payment_id)
               if ref_flag == True:
                   flag_obj = VendorModificationRel.objects.using(self._current_app_schema()).filter(
                       Q(modify_ref_id=payment_id) & Q(ref_type=VendorRefType.VENDOR_PAYMENT)).update(
                       mod_status=ModifyStatus.delete)
               else:
                   VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=payment_id,
                                                        ref_type=VendorRefType.VENDOR_PAYMENT,
                                                        mod_status=ModifyStatus.delete,
                                                        modify_ref_id=payment_id, entity_id=self._entity_id())

               vendor_check = vendor_service.branchvalidate(branch_id)
               if vendor_check == True:
                   vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id).update(is_validate=True)
               else:
                   vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id).update(is_validate=False)

               req_status = RequestStatusUtil.MODIFICATION
               # self.audit_function(payment, vendor_id, user_id, req_status, payment_id, ModifyStatus.update)

               success_obj = NWisefinSuccess()
               success_obj.set_status(SuccessStatus.SUCCESS)
               success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
               return success_obj
           except:
               error_obj = NWisefinError()
               error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
               error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
               return error_obj

    def modification_paymentactive(self, payment_obj,branch_id, vendor_id, user_id):
        req_status = RequestStatusUtil.MODIFICATION
        vendor_service = VendorService()
        if not payment_obj.get_id() is None:
            ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_PAYMENT, payment_obj.get_id())
            if ref_flag == True:
                payment = SupplierPayment.objects.filter(id=payment_obj.get_id()).update(
                    supplier=payment_obj.get_supplier(),
                    paymode_id=payment_obj.get_paymode_id(),
                    bank_id=payment_obj.get_bank_id(),
                    branch_id=payment_obj.get_branch_id(),
                    account_type=payment_obj.get_account_type(),
                    account_no=payment_obj.get_account_no(),
                    beneficiary=payment_obj.get_beneficiary(),
                    remarks=payment_obj.get_remarks(),
                    supplierbranch_id=branch_id,
                    is_active=payment_obj.get_is_active(),
                    portal_flag=payment_obj.get_portal_flag()
                    )
                payment = SupplierPayment.objects.using(self._current_app_schema()).get(id=payment_obj.get_id())
            else:
                payment = SupplierPayment.objects.using(self._current_app_schema()).create(supplier=payment_obj.get_supplier(),
                                                         paymode_id=payment_obj.get_paymode_id(),
                                                         bank_id=payment_obj.get_bank_id(),
                                                         branch_id=payment_obj.get_branch_id(),
                                                         account_type=payment_obj.get_account_type(),
                                                         account_no=payment_obj.get_account_no(),
                                                         beneficiary=payment_obj.get_beneficiary(),
                                                         remarks=payment_obj.get_remarks(),
                                                         supplierbranch_id=branch_id, created_by=user_id,
                                                         modify_status=ModifyStatus.active_in,
                                                         modify_ref_id=payment_obj.get_id(),
                                                         is_active=payment_obj.get_is_active(),
                                                         modified_by=user_id, entity_id=self._entity_id(),portal_flag=payment_obj.get_portal_flag())

                payment_update = SupplierPayment.objects.using(self._current_app_schema()).filter(id=payment_obj.get_id()).update(
                    modify_ref_id=payment.id)

                paymentupdate_auditdata = {'id': payment_obj.get_id(), 'modify_ref_id': payment.id}
                VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=payment_obj.get_id(),
                                                     ref_type=VendorRefType.VENDOR_PAYMENT,
                                                     mod_status=ModifyStatus.active_in,
                                                     modify_ref_id=payment.id, entity_id=self._entity_id())

            # audit
            payment_update_id = payment_obj.get_id()
            self.audit_function(payment, vendor_id, user_id, req_status, payment.id, ModifyStatus.active_in)

        else:
            payment = SupplierPayment.objects.using(self._current_app_schema()).create(supplier=payment_obj.get_supplier(),
                                                     paymode_id=payment_obj.get_paymode_id(),
                                                     bank_id=payment_obj.get_bank_id(),
                                                     branch_id=payment_obj.get_branch_id(),
                                                     account_type=payment_obj.get_account_type(),
                                                     account_no=payment_obj.get_account_no(),
                                                     beneficiary=payment_obj.get_beneficiary(),
                                                     remarks=payment_obj.get_remarks(),
                                                     is_active=payment_obj.get_is_active(),
                                                     supplierbranch_id=branch_id, created_by=user_id,
                                                     modify_status=ModifyStatus.create, modified_by=user_id, entity_id=self._entity_id(),portal_flag=payment_obj.get_portal_flag())
            payment.modify_ref_id = payment.id
            payment.save()

            VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id,
                                                 ref_id=payment.id,
                                                 ref_type=VendorRefType.VENDOR_PAYMENT,
                                                 mod_status=ModifyStatus.create,
                                                 modify_ref_id=payment.id, entity_id=self._entity_id())

            vendor_check = vendor_service.branchvalidate(branch_id)
            if vendor_check == True:
                vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id).update(is_validate=True)
            else:
                vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id).update(is_validate=False)

            self.audit_function(payment, vendor_id, user_id, req_status, payment.id, ModifyStatus.create)

        payment_data = PaymentResponse()
        payment_data.set_id(payment.id)
        payment_data.set_paymode_id(payment.paymode_id)
        payment_data.set_bank_id(payment.bank_id)
        payment_data.set_branch_id(payment.branch_id)
        payment_data.set_account_type(payment.account_type)
        payment_data.set_account_no(payment.account_no)
        payment_data.set_beneficiary(payment.beneficiary)
        payment_data.set_remarks(payment.remarks)
        payment_data.set_supplierbranch_id(payment.supplierbranch_id)
        payment_data.set_status(payment.status)
        payment_data.set_created_by(payment.created_by)
        payment_data.set_is_active(payment.is_active)
        payment_data.set_portal_flag(payment.portal_flag)
        return payment_data



    def modification_action_payment(self, mod_status, old_id, new_id,vendor_id,user_id):
        req_status = RequestStatusUtil.MODIFICATION
        if mod_status == ModifyStatus.update:
               payment_obj = self.fetch_payment(new_id)

               payment_update=SupplierPayment.objects.using(self._current_app_schema()).filter(id=old_id).update(supplier=payment_obj.get_supplier(),
                                                                paymode_id=payment_obj.get_paymode(),
                                                                bank_id=payment_obj.get_bank_id(),
                                                                branch_id=payment_obj.get_branch_id(),
                                                                account_type=payment_obj.get_account_type(),
                                                                account_no=payment_obj.get_account_no(),
                                                                beneficiary=payment_obj.get_beneficiary(),
                                                                remarks=payment_obj.get_remarks(),
                                                                modify_status=-1,modified_by=-1, modify_ref_id=-1,portal_flag=payment_obj.get_portal_flag())



               #audit
               self.audit_function(payment_update, vendor_id, user_id, req_status, old_id, ModifyStatus.update)
               # self.audit_function(payment, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)

        elif mod_status == ModifyStatus.create:

               payment_update=SupplierPayment.objects.using(self._current_app_schema()).filter(id=new_id).update(modify_status=-1,modified_by=-1,
                                                                modify_ref_id=-1)
               # audit
               self.audit_function(payment_update, vendor_id, user_id, req_status, new_id, ModifyStatus.update)
        elif mod_status==ModifyStatus.active_in:
            payment_obj = SupplierPayment.objects.using(self._current_app_schema()).get(id=new_id)
            payment_update = SupplierPayment.objects.using(self._current_app_schema()).filter ( id=old_id ).update ( modify_status=-1 , modified_by=-1 ,
                                                                                   modify_ref_id=-1 ,
                                                                                   is_active=payment_obj.is_active)
            # audit
            self.audit_function ( payment_update , vendor_id , user_id , req_status , new_id , ModifyStatus.active_in )

        else:
               payment=SupplierPayment.objects.using(self._current_app_schema()).filter(id=old_id).delete()
               # audit
               self.audit_function(payment, vendor_id, user_id, req_status, old_id, ModifyStatus.delete)
        return

    def modification_reject_payment(self, mod_status, old_id, new_id,vendor_id,user_id):
        req_status = RequestStatusUtil.MODIFICATION
        if mod_status == ModifyStatus.update:
            payment=SupplierPayment.objects.using(self._current_app_schema()).filter(id=new_id).delete()
            payment_update=SupplierPayment.objects.using(self._current_app_schema()).filter(id=old_id).update(modify_ref_id=-1)
            # audit
            self.audit_function(payment, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)
            self.audit_function(payment_update, vendor_id, user_id, req_status, old_id, ModifyStatus.update)
        elif mod_status == ModifyStatus.create:
            payment=SupplierPayment.objects.using(self._current_app_schema()).filter(id=new_id).delete()
            # audit
            self.audit_function(payment, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)
        else:
            payment=SupplierPayment.objects.using(self._current_app_schema()).filter(id=old_id).update(modify_ref_id=-1)
            # audit
            self.audit_function(payment, vendor_id, user_id, req_status, old_id, ModifyStatus.update)
        return

    def audit_function(self,payment,vendor_id,user_id,req_status,id,action):

        if action == ModifyStatus.delete:
            data = None
        elif action == ModifyStatus.update:
            data = payment
        elif action == ModifyStatus.active_in:
            data = payment
        else:
            data = payment.__dict__
            del data['_state']
        audit_service = VendorAuditService()
        audit_obj = VendorAuditResponse()
        audit_obj.set_refid(vendor_id)
        audit_obj.set_reftype(VendorRefType.VENDOR)
        audit_obj.set_userid(user_id)
        audit_obj.set_reqstatus(req_status)
        audit_obj.set_relrefid(id)
        audit_obj.set_relreftype(VendorRefType.VENDOR_PAYMENT)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_vendoraudit(audit_obj)
        return
    def paymentactiveflagservice(self,data):
        paymentupdate = SupplierPayment.objects.using(self._current_app_schema()).filter(id=data.id).update(is_active=data.is_active)
        if paymentupdate:
            payment=SupplierPayment.objects.using(self._current_app_schema()).get(id=data.id)

        payment_data = PaymentResponse()
        payment_data.set_id(payment.id)
        payment_data.set_supplier(payment.supplier)
        payment_data.set_paymode_id(payment.paymode_id)
        payment_data.set_bank_id(payment.bank_id)
        payment_data.set_branch_id(payment.branch_id)
        payment_data.set_account_type(payment.account_type)
        payment_data.set_account_no(payment.account_no)
        payment_data.set_beneficiary(payment.beneficiary)
        payment_data.set_remarks(payment.remarks)
        payment_data.set_supplierbranch_id(payment.supplierbranch_id)
        payment_data.set_status(payment.status)
        payment_data.set_created_by(payment.created_by)
        payment_data.set_is_active(payment.is_active)
        payment_data.set_portal_flag(payment.portal_flag)
        return payment_data

    def fetch_paymentvendor(self,request, vys_page,user_id,vendor_id):
        queue_arr= SupplierPayment.objects.using(self._current_app_schema()).filter(supplierbranch__vendor_id=vendor_id).values('id')
        condition = None
        for vendor in queue_arr:
            logger.error(str(vendor))
            if condition is None:
                condition = Q(id__exact=vendor['id']) & Q(status__exact=1) & (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1)
            else:
                condition |= Q(id__exact=vendor['id']) & Q(status__exact=1) & (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1)
        if condition is not None:
            paymentlist = SupplierPayment.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        else:
            paymentlist = []

        vlist = NWisefinList()
        user_list = []
        for vendor in paymentlist:
            user_list.append(vendor.created_by)
        user_list = set(user_list)
        user_list = list(user_list)
        utility_service = NWisefinUtilityService()
        user_list_obj = utility_service.get_user_info(request,user_list)

        for payment in paymentlist:
            payment_data = PaymentResponse()
            payment_data.set_id(payment.id)
            payment_data.set_supplier(payment.supplier)
            payment_data.set_paymode_id(payment.paymode_id)
            payment_data.set_bank_id(payment.bank_id)
            payment_data.set_branch_id(payment.branch_id)
            payment_data.set_account_type(payment.account_type)
            payment_data.set_account_no(payment.account_no)
            payment_data.set_beneficiary(payment.beneficiary)
            payment_data.set_remarks(payment.remarks)
            payment_data.set_supplierbranch_id(payment.supplierbranch_id)
            payment_data.set_created_by(payment.created_by)
            payment_data.set_modify_ref_id(payment.modify_ref_id)
            payment_data.set_modify_status(payment.modify_status)
            payment_data.set_is_active(payment.is_active)
            payment_data.set_portal_flag(payment.portal_flag)

            for ul in user_list_obj['data']:
                if ul['id'] == SupplierPayment.created_by:
                    payment_data.set_created_by(ul)
            vlist.append(payment_data)
        vpage = NWisefinPaginator(paymentlist, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist

    def supplierpayment(self,branch_id,paymode_id):
        condition = Q(supplierbranch_id=branch_id) & Q(paymode_id=paymode_id)
        payment = SupplierPayment.objects.using(self._current_app_schema()).filter(condition)
        list_length = len(payment)
        paymentdata = NWisefinList()
        if list_length > 0:
            for payment in payment:
                payment_data = PaymentResponse()
                payment_data.set_id(payment.id)
                payment_data.set_supplier(payment.supplier)
                payment_data.set_paymode_id(payment.paymode_id)
                payment_data.set_account_no(payment.account_no)
                paymentdata.append(payment_data)
        return paymentdata

    # def fetch_paymentvendor(self,request, vys_page,user_id,vendor_id):
    #     queue_arr= SupplierPayment.objects.filter(supplierbranch__vendor_id=vendor_id).values('id')
    #     condition = None
    #     for vendor in queue_arr:
    #         logger.error(str(vendor))
    #         if condition is None:
    #             condition = Q(id__exact=vendor['id']) & Q(status__exact=1) & (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1)
    #         else:
    #             condition |= Q(id__exact=vendor['id']) & Q(status__exact=1) & (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1)
    #     if condition is not None:
    #         paymentlist = SupplierPayment.objects.filter(condition).order_by('created_date')[
    #                      vys_page.get_offset():vys_page.get_query_limit()]
    #     else:
    #         paymentlist = []
    #
    #     vlist = NWisefinList()
    #     user_list = []
    #     for vendor in paymentlist:
    #         user_list.append(vendor.created_by)
    #     user_list = set(user_list)
    #     user_list = list(user_list)
    #     utility_service = NWisefinUtilityService()
    #     user_list_obj = utility_service.get_user_info(request,user_list)
    #
    #     for payment in paymentlist:
    #         payment_data = PaymentResponse()
    #         payment_data.set_id(payment.id)
    #         payment_data.set_supplier(payment.supplier)
    #         payment_data.set_paymode_id(payment.paymode_id)
    #         payment_data.set_bank_id(payment.bank_id)
    #         payment_data.set_branch_id(payment.branch_id)
    #         payment_data.set_account_type(payment.account_type)
    #         payment_data.set_account_no(payment.account_no)
    #         payment_data.set_beneficiary(payment.beneficiary)
    #         payment_data.set_remarks(payment.remarks)
    #         payment_data.set_supplierbranch_id(payment.supplierbranch_id)
    #         payment_data.set_created_by(payment.created_by)
    #         payment_data.set_modify_ref_id(payment.modify_ref_id)
    #         payment_data.set_modify_status(payment.modify_status)
    #         payment_data.set_is_active(payment.is_active)
    #
    #         for ul in user_list_obj['data']:
    #             if ul['id'] == SupplierPayment.created_by:
    #                 payment_data.set_created_by(ul)
    #         vlist.append(payment_data)
    #     vpage = NWisefinPaginator(paymentlist, vys_page.get_index(), 10)
    #     vlist.set_pagination(vpage)
    #     return vlist

    def supplierpayment(self,branch_id,paymode_id):
        condition = Q(supplierbranch_id=branch_id) & Q(paymode_id=paymode_id)
        payment = SupplierPayment.objects.filter(condition)
        list_length = len(payment)
        paymentdata = NWisefinList()
        if list_length > 0:
            for payment in payment:
                payment_data = PaymentResponse()
                payment_data.set_id(payment.id)
                payment_data.set_supplier(payment.supplier)
                payment_data.set_paymode_id(payment.paymode_id)
                payment_data.set_account_no(payment.account_no)
                paymentdata.append(payment_data)
        return paymentdata


    def fetch_supplierbranch_payment(self,request, emp_id,supplierbranch_id,supplierbranch_accountno):

        print('supplierbranch_id ',supplierbranch_id)
        print('supplierbranch_accountno ',supplierbranch_accountno)
        supplier_payment= SupplierPayment.objects.filter(supplierbranch_id=supplierbranch_id,
                                                  account_no=supplierbranch_accountno)

        list_length = len(supplier_payment)
        vysfin_list = NWisefinList()
        if list_length > 0:
            for payment in supplier_payment:
                return_json={"supplierbranch_id":payment.supplierbranch_id,
                             "supplier_accountno":payment.account_no,
                             "validation_flag":True}
                vysfin_list.append(return_json)
        return vysfin_list