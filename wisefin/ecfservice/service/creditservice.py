import json
import traceback

from django.http import HttpResponse

from nwisefin.settings import logger
#test
from ecfservice.data.response.ecfauditresponse import ECFAuditResponse
from ecfservice.models.ecfmodels import Credit,Invoicedetail,InvoicePO,InvoiceHeader,ECFQueue,ECFHeader

from ecfservice.service.ecfauditservice import ECFAuditService
from ecfservice.util.ecfutil import ECFModifyStatus, ECFRefType, ECFQuery,Type
from ecfservice.data.response.creditresponse import Creditresponse
from django.db.models import Q
from datetime import datetime, timedelta, date
#other service
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from vendorservice.service.suppliertaxservice import TaxService
from vendorservice.service.branchservice import branchservice
from masterservice.service.subtaxservice import SubTaxService
from masterservice.service.taxrateservice import TaxRateService
from masterservice.service.taxservice import TaxMasterService
from masterservice.service.bankbranchservice import BankBranchService
from masterservice.service.bankservice import BankService
from vendorservice.data.response.paymentresponse import PaymentResponse
from vendorservice.models import SupplierPayment, SupplierBranch
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from django.utils.timezone import now
from django.db import IntegrityError
from utilityservice.service.utilityservice import NWisefinUtilityService

class CreditService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ECF_SERVICE)

    def creditcreate(self,cdt_obj,emp_id):
        invhdr = InvoiceHeader.objects.using(self._current_app_schema()).get(id=cdt_obj.get_invoiceheader_id(),entity_id=self._entity_id())
        ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=invhdr.ecfheader_id,entity_id=self._entity_id())
        print("ecfhdr", ecfhdr)
        type = ecfhdr.ecftype
        amt = invhdr.totalamount
        if type == Type.NON_PO:
            if (amt != cdt_obj.get_credittotal()):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                return error_obj
            else:
                if not cdt_obj.get_id() is None:
                    crd = Credit.objects.using(self._current_app_schema()).filter(id=cdt_obj.get_id(),entity_id=self._entity_id()).update(
                                                                        invoiceheader_id=cdt_obj.get_invoiceheader_id(),
                                                                        paymode_id=cdt_obj.get_paymode_id(),
                                                                        creditbank_id=cdt_obj.get_creditbank_id(),
                                                                        suppliertax_id=cdt_obj.get_suppliertax_id(),
                                                                        creditglno=cdt_obj.get_creditglno(),
                                                                        creditrefno=cdt_obj.get_creditrefno(),
                                                                        suppliertaxtype=cdt_obj.get_suppliertaxtype(),
                                                                        suppliertaxrate=cdt_obj.get_suppliertaxrate(),
                                                                        taxexcempted=cdt_obj.get_taxexcempted(),
                                                                        amount=cdt_obj.get_amount(),
                                                                        taxableamount=cdt_obj.get_taxableamount(),
                                                                        ddtranbranch=cdt_obj.get_ddtranbranch(),
                                                                        ddpaybranch=cdt_obj.get_ddpaybranch(),
                                                                        category_code=cdt_obj.get_category_code(),
                                                                        subcategory_code=cdt_obj.get_subcategory_code(),
                                                                        updated_by=emp_id,
                                                                        updated_date=now())
                    crd = Credit.objects.using(self._current_app_schema()).get(id=cdt_obj.get_id(),entity_id=self._entity_id())

                    self.audit_function(crd, crd.id, crd.id, emp_id,
                                        ECFModifyStatus.UPDATE, ECFRefType.CREDIT)

                else:
                    crd = Credit.objects.using(self._current_app_schema()).create(

                                                    invoiceheader_id=cdt_obj.get_invoiceheader_id(),
                                                    paymode_id=cdt_obj.get_paymode_id(),
                                                    creditbank_id = cdt_obj.get_creditbank_id(),
                                                    suppliertax_id = cdt_obj.get_suppliertax_id(),
                                                    creditglno = cdt_obj.get_creditglno(),
                                                    creditrefno = cdt_obj.get_creditrefno(),
                                                    suppliertaxtype = cdt_obj.get_suppliertaxtype(),
                                                    suppliertaxrate = cdt_obj.get_suppliertaxrate(),
                                                    taxexcempted = cdt_obj.get_taxexcempted(),
                                                    amount = cdt_obj.get_amount(),
                                                    taxableamount = cdt_obj.get_taxableamount(),
                                                    ddtranbranch = cdt_obj.get_ddtranbranch(),
                                                    ddpaybranch = cdt_obj.get_ddpaybranch(),
                                                    category_code = cdt_obj.get_category_code(),
                                                    subcategory_code = cdt_obj.get_subcategory_code(),
                                                    created_by=emp_id,
                                                    entity_id=self._entity_id())

                    self.audit_function(crd, crd.id, crd.id, emp_id,
                                        ECFModifyStatus.CREATE, ECFRefType.CREDIT)


                crd_data = Creditresponse()
                crd_data.set_id(crd.id)
                crd_data.set_invoiceheader(crd.invoiceheader_id)
                crd_data.set_paymode(crd.paymode_id)
                crd_data.set_category_code(crd.category_code)
                crd_data.set_subcategory_code(crd.subcategory_code)
                # crd_data.set_creditbank_id(crd.creditbank_id)
                crd_data.set_suppliertax(crd.suppliertax_id)
                crd_data.set_amount(crd.amount)
                crd_data.set_creditglno(crd.creditglno)
                crd_data.set_creditrefno(crd.creditrefno)
                crd_data.set_suppliertaxtype(crd.suppliertaxtype)
                crd_data.set_taxexcempted(crd.taxexcempted)
                crd_data.set_taxableamount(crd.taxableamount)
                crd_data.set_ddtranbranch(crd.ddtranbranch)
                crd_data.set_ddpaybranch(crd.ddpaybranch)
                return crd_data
        elif type == Type.ERA:
            if (amt != cdt_obj.get_credittotal()):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                return error_obj
            else:
                if not cdt_obj.get_id() is None:
                    crd = Credit.objects.using(self._current_app_schema()).filter(id=cdt_obj.get_id(),entity_id=self._entity_id()).update(
                        invoiceheader_id=cdt_obj.get_invoiceheader_id(),
                        paymode_id=cdt_obj.get_paymode_id(),
                        creditbank_id=cdt_obj.get_creditbank_id(),
                        suppliertax_id=cdt_obj.get_suppliertax_id(),
                        creditglno=cdt_obj.get_creditglno(),
                        creditrefno=cdt_obj.get_creditrefno(),
                        suppliertaxtype=cdt_obj.get_suppliertaxtype(),
                        suppliertaxrate=cdt_obj.get_suppliertaxrate(),
                        taxexcempted=cdt_obj.get_taxexcempted(),
                        amount=cdt_obj.get_amount(),
                        taxableamount=cdt_obj.get_taxableamount(),
                        ddtranbranch=cdt_obj.get_ddtranbranch(),
                        ddpaybranch=cdt_obj.get_ddpaybranch(),
                        category_code=cdt_obj.get_category_code(),
                        subcategory_code=cdt_obj.get_subcategory_code(),
                        updated_by=emp_id,
                        updated_date=now())
                    crd = Credit.objects.using(self._current_app_schema()).get(id=cdt_obj.get_id(),entity_id=self._entity_id())

                    self.audit_function(crd, crd.id, crd.id, emp_id,
                                        ECFModifyStatus.UPDATE, ECFRefType.CREDIT)

                else:
                    crd = Credit.objects.using(self._current_app_schema()).create(

                        invoiceheader_id=cdt_obj.get_invoiceheader_id(),
                        paymode_id=cdt_obj.get_paymode_id(),
                        creditbank_id=cdt_obj.get_creditbank_id(),
                        suppliertax_id=cdt_obj.get_suppliertax_id(),
                        creditglno=cdt_obj.get_creditglno(),
                        creditrefno=cdt_obj.get_creditrefno(),
                        suppliertaxtype=cdt_obj.get_suppliertaxtype(),
                        suppliertaxrate=cdt_obj.get_suppliertaxrate(),
                        taxexcempted=cdt_obj.get_taxexcempted(),
                        amount=cdt_obj.get_amount(),
                        taxableamount=cdt_obj.get_taxableamount(),
                        ddtranbranch=cdt_obj.get_ddtranbranch(),
                        ddpaybranch=cdt_obj.get_ddpaybranch(),
                        category_code=cdt_obj.get_category_code(),
                        subcategory_code=cdt_obj.get_subcategory_code(),
                        created_by=emp_id,
                        entity_id=self._entity_id())

                    self.audit_function(crd, crd.id, crd.id, emp_id,
                                        ECFModifyStatus.CREATE, ECFRefType.CREDIT)

                crd_data = Creditresponse()
                crd_data.set_id(crd.id)
                crd_data.set_invoiceheader(crd.invoiceheader_id)
                crd_data.set_paymode(crd.paymode_id)
                crd_data.set_category_code(crd.category_code)
                crd_data.set_subcategory_code(crd.subcategory_code)
                # crd_data.set_creditbank_id(crd.creditbank_id)
                crd_data.set_suppliertax(crd.suppliertax_id)
                crd_data.set_amount(crd.amount)
                crd_data.set_creditglno(crd.creditglno)
                crd_data.set_creditrefno(crd.creditrefno)
                crd_data.set_suppliertaxtype(crd.suppliertaxtype)
                crd_data.set_taxexcempted(crd.taxexcempted)
                crd_data.set_taxableamount(crd.taxableamount)
                crd_data.set_ddtranbranch(crd.ddtranbranch)
                crd_data.set_ddpaybranch(crd.ddpaybranch)
                return crd_data
        elif type == Type.ADVANCE:
            if (amt != cdt_obj.get_credittotal()):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                return error_obj
            else:
                if not cdt_obj.get_id() is None:
                    crd = Credit.objects.using(self._current_app_schema()).filter(id=cdt_obj.get_id(),entity_id=self._entity_id()).update(
                        invoiceheader_id=cdt_obj.get_invoiceheader_id(),
                        paymode_id=cdt_obj.get_paymode_id(),
                        creditbank_id=cdt_obj.get_creditbank_id(),
                        suppliertax_id=cdt_obj.get_suppliertax_id(),
                        creditglno=cdt_obj.get_creditglno(),
                        creditrefno=cdt_obj.get_creditrefno(),
                        suppliertaxtype=cdt_obj.get_suppliertaxtype(),
                        suppliertaxrate=cdt_obj.get_suppliertaxrate(),
                        taxexcempted=cdt_obj.get_taxexcempted(),
                        amount=cdt_obj.get_amount(),
                        taxableamount=cdt_obj.get_taxableamount(),
                        ddtranbranch=cdt_obj.get_ddtranbranch(),
                        ddpaybranch=cdt_obj.get_ddpaybranch(),
                        category_code=cdt_obj.get_category_code(),
                        subcategory_code=cdt_obj.get_subcategory_code(),
                        updated_by=emp_id,
                        updated_date=now())
                    crd = Credit.objects.using(self._current_app_schema()).get(id=cdt_obj.get_id(),entity_id=self._entity_id())

                    self.audit_function(crd, crd.id, crd.id, emp_id,
                                        ECFModifyStatus.UPDATE, ECFRefType.CREDIT)

                else:
                    crd = Credit.objects.using(self._current_app_schema()).create(

                        invoiceheader_id=cdt_obj.get_invoiceheader_id(),
                        paymode_id=cdt_obj.get_paymode_id(),
                        creditbank_id=cdt_obj.get_creditbank_id(),
                        suppliertax_id=cdt_obj.get_suppliertax_id(),
                        creditglno=cdt_obj.get_creditglno(),
                        creditrefno=cdt_obj.get_creditrefno(),
                        suppliertaxtype=cdt_obj.get_suppliertaxtype(),
                        suppliertaxrate=cdt_obj.get_suppliertaxrate(),
                        taxexcempted=cdt_obj.get_taxexcempted(),
                        amount=cdt_obj.get_amount(),
                        taxableamount=cdt_obj.get_taxableamount(),
                        ddtranbranch=cdt_obj.get_ddtranbranch(),
                        ddpaybranch=cdt_obj.get_ddpaybranch(),
                        category_code=cdt_obj.get_category_code(),
                        subcategory_code=cdt_obj.get_subcategory_code(),
                        created_by=emp_id,entity_id=self._entity_id())

                    self.audit_function(crd, crd.id, crd.id, emp_id,
                                        ECFModifyStatus.CREATE, ECFRefType.CREDIT)

                crd_data = Creditresponse()
                crd_data.set_id(crd.id)
                crd_data.set_invoiceheader(crd.invoiceheader_id)
                crd_data.set_paymode(crd.paymode_id)
                crd_data.set_category_code(crd.category_code)
                crd_data.set_subcategory_code(crd.subcategory_code)
                # crd_data.set_creditbank_id(crd.creditbank_id)
                crd_data.set_suppliertax(crd.suppliertax_id)
                crd_data.set_amount(crd.amount)
                crd_data.set_creditglno(crd.creditglno)
                crd_data.set_creditrefno(crd.creditrefno)
                crd_data.set_suppliertaxtype(crd.suppliertaxtype)
                crd_data.set_taxexcempted(crd.taxexcempted)
                crd_data.set_taxableamount(crd.taxableamount)
                crd_data.set_ddtranbranch(crd.ddtranbranch)
                crd_data.set_ddpaybranch(crd.ddpaybranch)
                return crd_data
    def audit_function(self, audit_data, refid, relrefid, emp_id, action, reqstatus):
        if action == ECFModifyStatus.DELETE:
            data = None
        else:
            data = audit_data.__dict__
            del data['_state']
        audit_service = ECFAuditService(self._scope())
        audit_obj = ECFAuditResponse()
        audit_obj.set_refid(refid)
        audit_obj.set_reqstatus(reqstatus)
        audit_obj.set_reftype(ECFRefType.CREDIT)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(ECFRefType.CREDIT)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)


    def fetch_payment_list(self,request, vys_page,branch_id,paymode_id,account_no,emp_id):
        cond= Q(supplierbranch_id=branch_id) & Q(paymode_id=paymode_id)
        if account_no != '':
            cond &= Q(account_no=account_no)
        queue_arr= SupplierPayment.objects.filter(cond).values('id')
        from utilityservice.service import api_service
        api_serv = api_service.ApiService(self._scope())
        supp = api_serv.get_supliersingle_id(request, branch_id)
        vendorId = supp['vendor_id']
        condition = None
        for vendor in queue_arr:
            logger.info(str(vendor))
            if condition is None:
                condition = Q(id__exact=vendor['id']) & Q(status__exact=1) & (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1)
            else:
                condition |= Q(id__exact=vendor['id']) & Q(status__exact=1) & (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1)
        if condition is not None:
            paymentlist = SupplierPayment.objects.filter(condition).order_by('created_date')[
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
        director_service = TaxService(self._scope())
        supplierTax_resp_obj = director_service.fetch_suppliertax_list(request, vys_page, emp_id, vendorId)
        # print("suppliertax_response", supplierTax_resp_obj)
        branch_service = branchservice(self._scope())
        taxrate_service = TaxRateService(self._scope())
        subtax_service = SubTaxService(self._scope())
        taxmaster_service = TaxMasterService(self._scope())
        s_tax = supplierTax_resp_obj.data
        for payment,t  in zip(paymentlist, s_tax):
            tax1_id = t.tax
            excempted=t.isexcempted
            if tax1_id != -1:
                tax = taxmaster_service.fetch_tax(tax1_id, emp_id)
                t.tax = tax
                taxname = t.tax.name
            payment_data = PaymentResponse()
            payment_data.set_id(payment.id)
            payment_data.set_supplier(payment.supplier)
            payment_data.set_paymode_id(payment.paymode_id)
            bank_service = BankService(self._scope())
            bankbranch_service=BankBranchService(self._scope())
            payment_data.set_bank_id(bank_service.fetch_bank(payment.bank_id,emp_id))
            payment_data.set_branch_id(bankbranch_service.fetch_bankbranch(payment.branch_id,emp_id))
            payment_data.set_account_type(payment.account_type)
            payment_data.set_account_no(payment.account_no)
            payment_data.set_beneficiary(payment.beneficiary)
            if taxname == 'TDS':
                payment_data.set_remarks("Y")
            else:
                payment_data.set_remarks("N")
            payment_data.set_supplierbranch_id(payment.supplierbranch_id)
            payment_data.set_created_by(payment.created_by)
            payment_data.set_modify_ref_id(excempted)
            payment_data.set_modify_status(payment.modify_status)

            for ul in user_list_obj['data']:
                if ul['id'] == SupplierPayment.created_by:
                    payment_data.set_created_by(ul)
            vlist.append(payment_data)
        vpage = NWisefinPaginator(paymentlist, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist
    def Delete_credit(self,request, crd_id, emp_id):
        try:
            cdt = Credit.objects.using(self._current_app_schema()).filter(id=crd_id,entity_id=self._entity_id()).update(
                                                                      status=0,
                                                                      updated_by=emp_id,
                                                                      updated_date=now())
            cdt = Credit.objects.using(self._current_app_schema()).get(id=crd_id,entity_id=self._entity_id())
            self.audit_function(cdt, cdt.id, cdt.id, emp_id,
                                ECFModifyStatus.UPDATE, ECFRefType.CREDIT)
            ECFQueue.objects.using(self._current_app_schema()).create(ref_id=cdt.id, ref_type=ECFRefType.CREDIT, from_user_id=emp_id,
                                    to_user_id=emp_id,
                                    created_date=now(),
                                    comments="DELETE",
                                    is_sys=True,
                                    entity_id=self._entity_id()
                                    )
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            # success_obj.set_message(SuccessMessage.APPROVED_MESSAGE)
            return success_obj

        except Exception as ex:
            traceback.print_exc(True)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(ex))
            return error_obj
    def creditmodcreate(self,cdt_obj,emp_id):
        invhdr = InvoiceHeader.objects.using(self._current_app_schema()).get(id=cdt_obj.get_invoiceheader_id(),entity_id=self._entity_id())
        ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=invhdr.ecfheader_id,entity_id=self._entity_id())
        print("ecfhdr", ecfhdr)
        type = ecfhdr.ecftype
        amt = invhdr.totalamount
        if type == Type.NON_PO:
            if not cdt_obj.get_id() is None:
                crd = Credit.objects.using(self._current_app_schema()).filter(id=cdt_obj.get_id(),entity_id=self._entity_id()).update(
                                                                    invoiceheader_id=cdt_obj.get_invoiceheader_id(),
                                                                    paymode_id=cdt_obj.get_paymode_id(),
                                                                    creditbank_id=cdt_obj.get_creditbank_id(),
                                                                    suppliertax_id=cdt_obj.get_suppliertax_id(),
                                                                    creditglno=cdt_obj.get_creditglno(),
                                                                    creditrefno=cdt_obj.get_creditrefno(),
                                                                    suppliertaxtype=cdt_obj.get_suppliertaxtype(),
                                                                    suppliertaxrate=cdt_obj.get_suppliertaxrate(),
                                                                    taxexcempted=cdt_obj.get_taxexcempted(),
                                                                    amount=cdt_obj.get_amount(),
                                                                    taxableamount=cdt_obj.get_taxableamount(),
                                                                    ddtranbranch=cdt_obj.get_ddtranbranch(),
                                                                    ddpaybranch=cdt_obj.get_ddpaybranch(),
                                                                    category_code=cdt_obj.get_category_code(),
                                                                    subcategory_code=cdt_obj.get_subcategory_code(),
                                                                    updated_by=emp_id,
                                                                    updated_date=now())
                crd = Credit.objects.using(self._current_app_schema()).get(id=cdt_obj.get_id(),entity_id=self._entity_id())

                self.audit_function(crd, crd.id, crd.id, emp_id,
                                    ECFModifyStatus.UPDATE, ECFRefType.CREDIT)

            else:
                crd = Credit.objects.using(self._current_app_schema()).create(

                                                invoiceheader_id=cdt_obj.get_invoiceheader_id(),
                                                paymode_id=cdt_obj.get_paymode_id(),
                                                creditbank_id = cdt_obj.get_creditbank_id(),
                                                suppliertax_id = cdt_obj.get_suppliertax_id(),
                                                creditglno = cdt_obj.get_creditglno(),
                                                creditrefno = cdt_obj.get_creditrefno(),
                                                suppliertaxtype = cdt_obj.get_suppliertaxtype(),
                                                suppliertaxrate = cdt_obj.get_suppliertaxrate(),
                                                taxexcempted = cdt_obj.get_taxexcempted(),
                                                amount = cdt_obj.get_amount(),
                                                taxableamount = cdt_obj.get_taxableamount(),
                                                ddtranbranch = cdt_obj.get_ddtranbranch(),
                                                ddpaybranch = cdt_obj.get_ddpaybranch(),
                                                category_code = cdt_obj.get_category_code(),
                                                subcategory_code = cdt_obj.get_subcategory_code(),
                                                created_by=emp_id)

                self.audit_function(crd, crd.id, crd.id, emp_id,
                                    ECFModifyStatus.CREATE, ECFRefType.CREDIT)

            invhdr1 = InvoiceHeader.objects.using(self._current_app_schema()).filter(id=cdt_obj.get_invoiceheader_id(),entity_id=self._entity_id())
            invhdr = invhdr1[0]

            Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=invhdr.ecfheader_id,entity_id=self._entity_id())
            self.audit_function(Ecfhdr, Ecfhdr.id, Ecfhdr.id, emp_id,
                                ECFModifyStatus.UPDATE, ECFRefType.ECFHEADER)
            ECFQueue.objects.using(self._current_app_schema()).create(ref_id=Ecfhdr.id, ref_type=ECFRefType.ECFHEADER,
                                                           from_user_id=emp_id,
                                                           to_user_id=emp_id,
                                                           created_date=now(),
                                                           comments="PENDING  FOR APPROVAL MODIFICATION",
                                                           is_sys=True,
                                                           entity_id=self._entity_id()
                                                           )

            crd_data = Creditresponse()
            crd_data.set_id(crd.id)
            crd_data.set_invoiceheader(crd.invoiceheader_id)
            crd_data.set_paymode(crd.paymode_id)
            crd_data.set_category_code(crd.category_code)
            crd_data.set_subcategory_code(crd.subcategory_code)
            # crd_data.set_creditbank_id(crd.creditbank_id)
            crd_data.set_suppliertax(crd.suppliertax_id)
            crd_data.set_amount(crd.amount)
            crd_data.set_creditglno(crd.creditglno)
            crd_data.set_creditrefno(crd.creditrefno)
            crd_data.set_suppliertaxtype(crd.suppliertaxtype)
            crd_data.set_taxexcempted(crd.taxexcempted)
            crd_data.set_taxableamount(crd.taxableamount)
            crd_data.set_ddtranbranch(crd.ddtranbranch)
            crd_data.set_ddpaybranch(crd.ddpaybranch)
            return crd_data
        elif type == Type.ERA:
            if (amt != cdt_obj.get_credittotal()):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                return error_obj
            else:
                if not cdt_obj.get_id() is None:
                    crd = Credit.objects.using(self._current_app_schema()).filter(id=cdt_obj.get_id(),entity_id=self._entity_id()).update(
                        invoiceheader_id=cdt_obj.get_invoiceheader_id(),
                        paymode_id=cdt_obj.get_paymode_id(),
                        creditbank_id=cdt_obj.get_creditbank_id(),
                        suppliertax_id=cdt_obj.get_suppliertax_id(),
                        creditglno=cdt_obj.get_creditglno(),
                        creditrefno=cdt_obj.get_creditrefno(),
                        suppliertaxtype=cdt_obj.get_suppliertaxtype(),
                        suppliertaxrate=cdt_obj.get_suppliertaxrate(),
                        taxexcempted=cdt_obj.get_taxexcempted(),
                        amount=cdt_obj.get_amount(),
                        taxableamount=cdt_obj.get_taxableamount(),
                        ddtranbranch=cdt_obj.get_ddtranbranch(),
                        ddpaybranch=cdt_obj.get_ddpaybranch(),
                        category_code=cdt_obj.get_category_code(),
                        subcategory_code=cdt_obj.get_subcategory_code(),
                        updated_by=emp_id,
                        updated_date=now())
                    crd = Credit.objects.using(self._current_app_schema()).get(id=cdt_obj.get_id(),entity_id=self._entity_id())

                    self.audit_function(crd, crd.id, crd.id, emp_id,
                                        ECFModifyStatus.UPDATE, ECFRefType.CREDIT)

                else:
                    crd = Credit.objects.using(self._current_app_schema()).create(

                        invoiceheader_id=cdt_obj.get_invoiceheader_id(),
                        paymode_id=cdt_obj.get_paymode_id(),
                        creditbank_id=cdt_obj.get_creditbank_id(),
                        suppliertax_id=cdt_obj.get_suppliertax_id(),
                        creditglno=cdt_obj.get_creditglno(),
                        creditrefno=cdt_obj.get_creditrefno(),
                        suppliertaxtype=cdt_obj.get_suppliertaxtype(),
                        suppliertaxrate=cdt_obj.get_suppliertaxrate(),
                        taxexcempted=cdt_obj.get_taxexcempted(),
                        amount=cdt_obj.get_amount(),
                        taxableamount=cdt_obj.get_taxableamount(),
                        ddtranbranch=cdt_obj.get_ddtranbranch(),
                        ddpaybranch=cdt_obj.get_ddpaybranch(),
                        category_code=cdt_obj.get_category_code(),
                        subcategory_code=cdt_obj.get_subcategory_code(),
                        created_by=emp_id,entity_id=self._entity_id())

                    self.audit_function(crd, crd.id, crd.id, emp_id,
                                        ECFModifyStatus.CREATE, ECFRefType.CREDIT)

                invhdr1 = InvoiceHeader.objects.using(self._current_app_schema()).filter(id=cdt_obj.get_invoiceheader_id(),entity_id=self._entity_id())
                invhdr = invhdr1[0]

                Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=invhdr.ecfheader_id,entity_id=self._entity_id())
                self.audit_function(Ecfhdr, Ecfhdr.id, Ecfhdr.id, emp_id,
                                    ECFModifyStatus.UPDATE, ECFRefType.ECFHEADER)
                ECFQueue.objects.using(self._current_app_schema()).create(ref_id=Ecfhdr.id, ref_type=ECFRefType.ECFHEADER,
                                                               from_user_id=emp_id,
                                                               to_user_id=emp_id,
                                                               created_date=now(),
                                                               comments="PENDING  FOR APPROVAL MODIFICATION",
                                                               is_sys=True,
                                                               entity_id=self._entity_id()
                                                               )

                crd_data = Creditresponse()
                crd_data.set_id(crd.id)
                crd_data.set_invoiceheader(crd.invoiceheader_id)
                crd_data.set_paymode(crd.paymode_id)
                crd_data.set_category_code(crd.category_code)
                crd_data.set_subcategory_code(crd.subcategory_code)
                # crd_data.set_creditbank_id(crd.creditbank_id)
                crd_data.set_suppliertax(crd.suppliertax_id)
                crd_data.set_amount(crd.amount)
                crd_data.set_creditglno(crd.creditglno)
                crd_data.set_creditrefno(crd.creditrefno)
                crd_data.set_suppliertaxtype(crd.suppliertaxtype)
                crd_data.set_taxexcempted(crd.taxexcempted)
                crd_data.set_taxableamount(crd.taxableamount)
                crd_data.set_ddtranbranch(crd.ddtranbranch)
                crd_data.set_ddpaybranch(crd.ddpaybranch)
                return crd_data
        elif type == Type.ADVANCE:
            if (amt != cdt_obj.get_credittotal()):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                return error_obj
            else:
                if not cdt_obj.get_id() is None:
                    crd = Credit.objects.using(self._current_app_schema()).filter(id=cdt_obj.get_id(),entity_id=self._entity_id()).update(
                        invoiceheader_id=cdt_obj.get_invoiceheader_id(),
                        paymode_id=cdt_obj.get_paymode_id(),
                        creditbank_id=cdt_obj.get_creditbank_id(),
                        suppliertax_id=cdt_obj.get_suppliertax_id(),
                        creditglno=cdt_obj.get_creditglno(),
                        creditrefno=cdt_obj.get_creditrefno(),
                        suppliertaxtype=cdt_obj.get_suppliertaxtype(),
                        suppliertaxrate=cdt_obj.get_suppliertaxrate(),
                        taxexcempted=cdt_obj.get_taxexcempted(),
                        amount=cdt_obj.get_amount(),
                        taxableamount=cdt_obj.get_taxableamount(),
                        ddtranbranch=cdt_obj.get_ddtranbranch(),
                        ddpaybranch=cdt_obj.get_ddpaybranch(),
                        category_code=cdt_obj.get_category_code(),
                        subcategory_code=cdt_obj.get_subcategory_code(),
                        updated_by=emp_id,
                        updated_date=now())
                    crd = Credit.objects.using(self._current_app_schema()).get(id=cdt_obj.get_id(),entity_id=self._entity_id())

                    self.audit_function(crd, crd.id, crd.id, emp_id,
                                        ECFModifyStatus.UPDATE, ECFRefType.CREDIT)

                else:
                    crd = Credit.objects.using(self._current_app_schema()).create(

                        invoiceheader_id=cdt_obj.get_invoiceheader_id(),
                        paymode_id=cdt_obj.get_paymode_id(),
                        creditbank_id=cdt_obj.get_creditbank_id(),
                        suppliertax_id=cdt_obj.get_suppliertax_id(),
                        creditglno=cdt_obj.get_creditglno(),
                        creditrefno=cdt_obj.get_creditrefno(),
                        suppliertaxtype=cdt_obj.get_suppliertaxtype(),
                        suppliertaxrate=cdt_obj.get_suppliertaxrate(),
                        taxexcempted=cdt_obj.get_taxexcempted(),
                        amount=cdt_obj.get_amount(),
                        taxableamount=cdt_obj.get_taxableamount(),
                        ddtranbranch=cdt_obj.get_ddtranbranch(),
                        ddpaybranch=cdt_obj.get_ddpaybranch(),
                        category_code=cdt_obj.get_category_code(),
                        subcategory_code=cdt_obj.get_subcategory_code(),
                        created_by=emp_id,entity_id=self._entity_id())

                    self.audit_function(crd, crd.id, crd.id, emp_id,
                                        ECFModifyStatus.CREATE, ECFRefType.CREDIT)

                invhdr1 = InvoiceHeader.objects.using(self._current_app_schema()).filter(id=cdt_obj.get_invoiceheader_id(),entity_id=self._entity_id())
                invhdr = invhdr1[0]

                Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=invhdr.ecfheader_id,entity_id=self._entity_id())
                self.audit_function(Ecfhdr, Ecfhdr.id, Ecfhdr.id, emp_id,
                                    ECFModifyStatus.UPDATE, ECFRefType.ECFHEADER)
                ECFQueue.objects.using(self._current_app_schema()).create(ref_id=Ecfhdr.id, ref_type=ECFRefType.ECFHEADER,
                                                               from_user_id=emp_id,
                                                               to_user_id=emp_id,
                                                               created_date=now(),
                                                               comments="PENDING  FOR APPROVAL MODIFICATION",
                                                               is_sys=True,
                                                               entity_id=self._entity_id()
                                                               )

                crd_data = Creditresponse()
                crd_data.set_id(crd.id)
                crd_data.set_invoiceheader(crd.invoiceheader_id)
                crd_data.set_paymode(crd.paymode_id)
                crd_data.set_category_code(crd.category_code)
                crd_data.set_subcategory_code(crd.subcategory_code)
                # crd_data.set_creditbank_id(crd.creditbank_id)
                crd_data.set_suppliertax(crd.suppliertax_id)
                crd_data.set_amount(crd.amount)
                crd_data.set_creditglno(crd.creditglno)
                crd_data.set_creditrefno(crd.creditrefno)
                crd_data.set_suppliertaxtype(crd.suppliertaxtype)
                crd_data.set_taxexcempted(crd.taxexcempted)
                crd_data.set_taxableamount(crd.taxableamount)
                crd_data.set_ddtranbranch(crd.ddtranbranch)
                crd_data.set_ddpaybranch(crd.ddpaybranch)
                return crd_data
    # def fetch_payment_listget(self,request, vys_page,branch_id,paymode_id,emp_id):
    #     cond= Q(supplierbranch_id=branch_id) & Q(paymode_id=paymode_id)
    #     queue_arr= SupplierPayment.objects.filter(cond).values('id')
    #     supp = SupplierBranch.objects.get(id=branch_id)
    #     vendorId = supp.vendor_id
    #     condition = None
    #     for vendor in queue_arr:
    #         logger.info(str(vendor))
    #         if condition is None:
    #             condition = Q(id__exact=vendor['id']) & Q(status__exact=1) & (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1)
    #         else:
    #             condition |= Q(id__exact=vendor['id']) & Q(status__exact=1) & (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1)
    #     if condition is not None:
    #         paymentlist = SupplierPayment.objects.filter(condition).order_by('created_date')
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
    #     director_service = TaxService()
    #     supplierTax_resp_obj = director_service.fetch_suppliertax_list(request, vys_page, emp_id, vendorId)
    #     taxmaster_service = TaxMasterService()
    #     s_tax = supplierTax_resp_obj.data
    #     for payment,t  in zip(paymentlist, s_tax):
    #         tax1_id = t.tax
    #         excempted=t.isexcempted
    #         if tax1_id != -1:
    #             tax = taxmaster_service.fetch_tax(tax1_id, emp_id)
    #             t.tax = tax
    #             taxname = t.tax.name
    #         payment_data = PaymentResponse()
    #         payment_data.set_id(payment.id)
    #         payment_data.set_supplier(payment.supplier)
    #         bank_service = BankService()
    #         bankbranch_service=BankBranchService()
    #         payment_data.set_branch_id(bankbranch_service.fetch_bankbranch(payment.branch_id,emp_id))
    #         payment_data.set_account_type(payment.account_type)
    #         payment_data.set_account_no(payment.account_no)
    #         payment_data.set_beneficiary(payment.beneficiary)
    #         if taxname == 'TDS':
    #             payment_data.set_remarks("Y")
    #         else:
    #             payment_data.set_remarks("N")
    #         payment_data.set_supplierbranch_id(payment.supplierbranch_id)
    #         payment_data.set_created_by(payment.created_by)
    #         payment_data.set_modify_ref_id(excempted)
    #         vlist.append(payment_data)
    #     return vlist

    def fetch_suppliertds(self,request,supplier_id,emp_id):
        try:
            from utilityservice.service import api_service
            api_serv = api_service.ApiService(self._scope())
            supp = api_serv.get_supliersingle_id(request, supplier_id)
            vendor = supp['vendor_id']
            suptx_dtl = ECFQuery.supp_taxdtl(self,vendor)
            suptx_ty = [i['suppliertax__subtax_id'] for i in suptx_dtl]
            tx_typ_get = ECFQuery.tax_type_get(self,suptx_ty)
            tx_typ_get = json.loads(tx_typ_get)
            # print(tx_typ_get)
            tax_typ_lsit = {'vendor_id':vendor, 'subtax_list': tx_typ_get['data']}
            return tax_typ_lsit

            # supp = api_serv.get_vendorsubtax_list(request, vendor)
            # subtax_arr=[]
            # for i in supp['data']:
            #     subtax_arr.append(i['subtax_id'])
            # sub_data = api_serv.get_subtax_list(request, subtax_arr)
            # return sub_data

        except Exception as ex:
            traceback.print_exc(True)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_INVOICE_ID)
            error_obj.set_description(str(ex))
            return error_obj

    def fetch_taxrate(self,request,vendor_id,subtax_id,emp_id):
        suptx_ratedtl = ECFQuery.supp_taxratedtl(self, vendor_id, subtax_id)
        strate_arr = []
        if len(suptx_ratedtl) != 0:
            for i in suptx_ratedtl:
                subrate = ECFQuery.tax_mst_get(self, i['suppliertax__subtax_id'], i['rate_id'])
                subrate = json.loads(subrate)
        else:
            subrate = ECFQuery.tax_mst_get(self, subtax_id, 0)
            subrate = json.loads(subrate)
        return subrate

    def fetch_ratecal(self,request,creditamount,tdsamt,emp_id):
        try:
            rate=float(creditamount) * (float(tdsamt)/100)
            crd_data = Creditresponse()
            crd_data.set_tdsrate(rate)
            return crd_data
        except Exception as ex:
            traceback.print_exc(True)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(ex))
            return error_obj

    def creditccreate(self,cdt_obj,invhdr_id,emp_id):
        invhdr = InvoiceHeader.objects.using(self._current_app_schema()).get(id=invhdr_id,entity_id=self._entity_id())
        amt = invhdr.totalamount
        if (amt != cdt_obj.get_credittotal()):
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
            return error_obj
        else:
            if not cdt_obj.get_id() is None:
                crd = Credit.objects.using(self._current_app_schema()).filter(id=cdt_obj.get_id(),entity_id=self._entity_id()).update(
                                                                    invoiceheader_id=invhdr_id,
                                                                    paymode_id=cdt_obj.get_paymode_id(),
                                                                    creditbank_id=cdt_obj.get_creditbank_id(),
                                                                    suppliertax_id=cdt_obj.get_suppliertax_id(),
                                                                    creditglno=cdt_obj.get_creditglno(),
                                                                    creditrefno=cdt_obj.get_creditrefno(),
                                                                    suppliertaxtype=cdt_obj.get_suppliertaxtype(),
                                                                    suppliertaxrate=cdt_obj.get_suppliertaxrate(),
                                                                    taxexcempted=cdt_obj.get_taxexcempted(),
                                                                    amount=cdt_obj.get_amount(),
                                                                    taxableamount=cdt_obj.get_taxableamount(),
                                                                    ddtranbranch=cdt_obj.get_ddtranbranch(),
                                                                    ddpaybranch=cdt_obj.get_ddpaybranch(),
                                                                    category_code=cdt_obj.get_category_code(),
                                                                    subcategory_code=cdt_obj.get_subcategory_code(),
                                                                    updated_by=emp_id,
                                                                    updated_date=now())
                crd = Credit.objects.using(self._current_app_schema()).get(id=cdt_obj.get_id())

                self.audit_function(crd, crd.id, crd.id, emp_id,
                                    ECFModifyStatus.UPDATE, ECFRefType.CREDIT)

            else:
                crd = Credit.objects.using(self._current_app_schema()).create(

                                                invoiceheader_id=invhdr_id,
                                                paymode_id=cdt_obj.get_paymode_id(),
                                                creditbank_id = cdt_obj.get_creditbank_id(),
                                                suppliertax_id = cdt_obj.get_suppliertax_id(),
                                                creditglno = cdt_obj.get_creditglno(),
                                                creditrefno = cdt_obj.get_creditrefno(),
                                                suppliertaxtype = cdt_obj.get_suppliertaxtype(),
                                                suppliertaxrate = cdt_obj.get_suppliertaxrate(),
                                                taxexcempted = cdt_obj.get_taxexcempted(),
                                                amount = cdt_obj.get_amount(),
                                                taxableamount = cdt_obj.get_taxableamount(),
                                                ddtranbranch = cdt_obj.get_ddtranbranch(),
                                                ddpaybranch = cdt_obj.get_ddpaybranch(),
                                                category_code = cdt_obj.get_category_code(),
                                                subcategory_code = cdt_obj.get_subcategory_code(),
                                                created_by=emp_id,entity_id=self._entity_id())

                self.audit_function(crd, crd.id, crd.id, emp_id,
                                    ECFModifyStatus.CREATE, ECFRefType.CREDIT)


            crd_data = Creditresponse()
            crd_data.set_id(crd.id)
            crd_data.set_invoiceheader(crd.invoiceheader_id)
            crd_data.set_paymode(crd.paymode_id)
            crd_data.set_category_code(crd.category_code)
            crd_data.set_subcategory_code(crd.subcategory_code)
            # crd_data.set_creditbank_id(crd.creditbank_id)
            crd_data.set_suppliertax(crd.suppliertax_id)
            crd_data.set_amount(crd.amount)
            crd_data.set_creditglno(crd.creditglno)
            crd_data.set_creditrefno(crd.creditrefno)
            crd_data.set_suppliertaxtype(crd.suppliertaxtype)
            crd_data.set_taxexcempted(crd.taxexcempted)
            crd_data.set_taxableamount(crd.taxableamount)
            crd_data.set_ddtranbranch(crd.ddtranbranch)
            crd_data.set_ddpaybranch(crd.ddpaybranch)
            return crd_data

    def paymode(self,request,paymode_id,emp_id):
        try:
            if paymode_id == "4":
                from utilityservice.service import api_service
                api_serv = api_service.ApiService(self._scope())
                emp_bran = api_serv.get_empsingle_id(request, emp_id)
                emp_acc = emp_bran['accountnumber']
                from utilityservice.service.ap_api_service import APApiService
                appservice = APApiService(self._scope())
                app_service = appservice.fetch_apraiser_emp_accntdtls_using_accntno(request, emp_bran['accountnumber'],
                                                                                    emp_id)
                print("empappservice", app_service)
                print("emp",emp_bran)
                branch_dict = json.dumps(app_service, indent=4)
                return HttpResponse(branch_dict, content_type='application/json')
            elif paymode_id == "1":
                from utilityservice.service import api_service
                api_serv = api_service.ApiService(self._scope())
                emp_bran = api_serv.get_empsingle_id(request, emp_id)
                emp_branch_id = emp_bran['employee_branch']
                print("bran",emp_branch_id)
                emp_glno = api_serv.get_empbranch_id(request, emp_bran['employee_branch'])
                print("kj",emp_glno)
                glno = emp_glno['glno']
                print("glno",glno)
                return glno
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description("Invalid paymode or data")
                return error_obj
        except Exception as ex:
            traceback.print_exc(True)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(ex))
            return error_obj


    def fetch_payment_details(self, request, vys_page, branch_id, paymode_id, account_no, emp_id):
        from utilityservice.service import api_service
        api_serv = api_service.ApiService(self._scope())
        pymt = api_serv.get_supplierpayment(branch_id,paymode_id,account_no,emp_id)
        print("pymt",pymt)
        supp = api_serv.get_supliersingle_id(request, branch_id)
        vendorId = supp['vendor_id']
        print("print",vendorId)
        vndr = api_serv.get_vendor(request,vys_page,emp_id,vendorId)
        print("tax",vndr.__dict__)
        s_tax = vndr.data
        print("s_tx",s_tax)
        payment_list=[]
        for payment, t in zip(payment_list, s_tax):
            tax1_id = t.tax
            excempted = t.isexcempted
            if tax1_id != -1:
                tax = api_serv.get_tax(tax1_id, emp_id)
                t.tax = tax
                taxname = t.tax.name
                print("print",taxname)
        return pymt