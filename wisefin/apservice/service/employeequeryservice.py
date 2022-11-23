import json
from django.db.models import Q
from apservice.data.response.apcreditresponse import APCreditResponse
from apservice.data.response.apheaderresponse import APHeaderResponse
from apservice.data.response.apinvoicedetailresponse import APInvoiceDetailsResponse, APDebitResponse, \
    APccbsDetailsResponse
from apservice.data.response.apinvoiceheaderresponse import APInvoiceheaderresponse
from apservice.data.response.paymentresponse import paymentdetailsresponse
from apservice.models import APHeader, APInvoiceHeader, APCCBSDetails, APCredit, APDebit, APInvoicedetail, \
    PaymentDetails
from apservice.service.paymentheaderservice import PreparePapmentService
from apservice.util.aputil import get_apstatus, get_APType
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.permissions.filter.commonpermission import ModulePermission
from utilityservice.permissions.util.dbutil import RoleList, ModuleList
from utilityservice.service.api_service import ApiService
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


import json
import pandas as pd

class employeequeryservice(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.AP_SERVICE)
    def empq_list(self, request,vys_page):
        obj = APHeader.objects.using(self._current_app_schema()).all().order_by('created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        list_len = len(obj)
        pro_list = NWisefinList()
        if list_len > 0:
            for emqu in obj:
                emqu_data = APHeaderResponse()
                emqu_data.set_id(emqu.id)
                emqu_data.set_crno(emqu.crno)
                emqu_data.set_supplier_type(emqu.supplier_type)
                emqu_data.set_commodity(emqu.commodity_id)
                emqu_data.set_aptype(get_APType(emqu.aptype))
                emqu_data.set_apdate(emqu.apdate)
                emqu_data.set_apamount(emqu.apamount)
                emqu_data.set_apstatus(get_apstatus(emqu.apstatus))
                emqu_data.set_ppx(emqu.ppx)
                emqu_data.set_notename(emqu.notename)
                emqu_data.set_remark(emqu.remark)
                emqu_data.set_payto(emqu.payto)
                emqu_data.set_raisedby(emqu.raisedby)
                emqu_data.set_raiserbranch(emqu.raiserbranch)
                emqu_data.set_raisername(emqu.raisername)
                emqu_data.set_approvername(emqu.approvername)
                emqu_data.set_Apinvoiceheader(None)
                aph = APInvoiceHeader.objects.using(self._current_app_schema()).filter(apheader_id=emqu.id,entity_id=self._entity_id()).all()
                invheader_list = []
                for inv_list in aph:
                    api_serv = ApiService(self._scope())
                    supp_data = api_serv.get_supliersingle_id(request, inv_list.supplier_id)
                    supp_name = supp_data['name']
                    invh_data = APInvoiceheaderresponse()
                    invh_data.set_id(inv_list.id)
                    invh_data.set_apheader(inv_list.apheader_id)
                    invh_data.set_invoiceno(inv_list.invoiceno)
                    invh_data.set_dedupinvoiceno(inv_list.dedupinvoiceno)
                    invh_data.set_invoicedate(inv_list.invoicedate)
                    invh_data.set_suppliergst(inv_list.suppliergst)
                    invh_data.set_raisorbranchgst(inv_list.raisorbranchgst)
                    invh_data.set_invoiceamount(inv_list.invoiceamount)
                    invh_data.set_taxamount(inv_list.taxamount)
                    invh_data.set_totalamount(inv_list.totalamount)
                    invh_data.set_otheramount(inv_list.otheramount)
                    invh_data.set_roundoffamt(inv_list.roundoffamt)
                    invh_data.set_invoicegst(inv_list.invoicegst)
                    invh_data.set_supplier(supp_name)
                    invh_data.set_supplierstate(inv_list.supplierstate_id)
                    invheader_list.append(json.loads(invh_data.get()))
                emqu_data.set_Apinvoiceheader(invheader_list)
                pro_list.append(emqu_data)
            vpage = NWisefinPaginator(obj, vys_page.get_index(), 10)
            pro_list.set_pagination(vpage)
        return pro_list

    def fetch_crno(self,request, crno, emp_id):
        # try:
            aphdr = APHeader.objects.using(self._current_app_schema()).get(crno=crno,entity_id=self._entity_id())
            aphdr_id  = aphdr.id
            apinvheader = APInvoiceHeader.objects.using(self._current_app_schema()).filter(apheader_id=aphdr_id,entity_id=self._entity_id()).all()
            emqu_data = APHeaderResponse()
            emqu_data.set_id(aphdr.id)
            emqu_data.set_crno(aphdr.crno)
            emqu_data.set_supplier_type(aphdr.supplier_type)
            emqu_data.set_commodity(aphdr.commodity_id)
            emqu_data.set_aptype(get_APType(aphdr.aptype))
            emqu_data.set_apdate(aphdr.apdate)
            emqu_data.set_apamount(aphdr.apamount)
            emqu_data.set_apstatus(get_apstatus(aphdr.apstatus))
            emqu_data.set_ppx(aphdr.ppx)
            emqu_data.set_notename(aphdr.notename)
            emqu_data.set_remark(aphdr.remark)
            emqu_data.set_payto(aphdr.payto)
            emqu_data.set_raisedby(aphdr.raisedby)
            emqu_data.set_raiserbranch(aphdr.raiserbranch)
            emqu_data.set_raisername(aphdr.raisername)
            emqu_data.set_approvername(aphdr.approvername)
            ecfhdr_list = []
            invhdr_list = []
            if len(apinvheader)!=0:
                for inhdr in apinvheader:
                    api_serv = ApiService(self._scope())
                    invdtl_list = APInvoicedetail.objects.using(self._current_app_schema()).filter(apinvoiceheader_id=inhdr.id, status = 1,entity_id=self._entity_id()).all()
                    deb_list = APDebit.objects.using(self._current_app_schema()).filter(apinvoiceheader_id=inhdr.id, status = 1,entity_id=self._entity_id()).all()
                    credit_list = APCredit.objects.using(self._current_app_schema()).filter(apinvoiceheader_id=inhdr.id, status = 1,entity_id=self._entity_id()).all()
                    supp_data = api_serv.get_supliersingle_id(request, inhdr.supplier_id)
                    supp_name = supp_data['name']
                    invh_data = APInvoiceheaderresponse()
                    invh_data.set_id(inhdr.id)
                    invh_data.set_apheader(inhdr.apheader_id)
                    invh_data.set_invoiceno(inhdr.invoiceno)
                    invh_data.set_dedupinvoiceno(inhdr.dedupinvoiceno)
                    invh_data.set_invoicedate(inhdr.invoicedate)
                    invh_data.set_suppliergst(inhdr.suppliergst)
                    invh_data.set_raisorbranchgst(inhdr.raisorbranchgst)
                    invh_data.set_invoiceamount(inhdr.invoiceamount)
                    invh_data.set_taxamount(inhdr.taxamount)
                    invh_data.set_totalamount(inhdr.totalamount)
                    invh_data.set_otheramount(inhdr.otheramount)
                    invh_data.set_roundoffamt(inhdr.roundoffamt)
                    invh_data.set_invoicegst(inhdr.invoicegst)
                    invh_data.set_supplier(supp_name)
                    invh_data.set_supplierstate(inhdr.supplierstate_id)
                    invhdr_list.append(json.loads(invh_data.get()))
                    invh_data.set_invoiceheader(invhdr_list)
                    inv_list = []
                    for invdtl in invdtl_list:
                        api_serv = ApiService(self._scope())
                        hsn = api_serv.get_hsn_code(request, invdtl.hsn)
                        apindtl_data = APInvoiceDetailsResponse()
                        apindtl_data.set_id(invdtl.id)
                        apindtl_data.set_apinvoiceheader(invdtl.apinvoiceheader_id)
                        apindtl_data.set_apinvoice_po(invdtl.apinvoice_po)
                        apindtl_data.set_mepno(invdtl.mepno)
                        apindtl_data.set_productcode(invdtl.productcode)
                        apindtl_data.set_productname(invdtl.productname)
                        apindtl_data.set_description(invdtl.description)
                        apindtl_data.set_hsn(hsn)
                        apindtl_data.set_hsn_percentage(invdtl.hsn_percentage)
                        apindtl_data.set_uom(invdtl.uom)
                        apindtl_data.set_unitprice(invdtl.unitprice)
                        apindtl_data.set_quantity(invdtl.quantity)
                        apindtl_data.set_amount(invdtl.amount)
                        apindtl_data.set_discount(invdtl.discount)
                        apindtl_data.set_sgst(invdtl.sgst)
                        apindtl_data.set_cgst(invdtl.cgst)
                        apindtl_data.set_igst(invdtl.igst)
                        apindtl_data.set_taxamount(invdtl.taxamount)
                        apindtl_data.set_totalamount(invdtl.totalamount)
                        inv_list.append(json.loads(apindtl_data.get()))
                        invh_data.set_invoicedtl(inv_list)

                        invdeb_list = []
                        for apdebit in deb_list:
                            api_serv = ApiService(self._scope())
                            cat = api_serv.get_cat_code(request,apdebit.category_code)
                            sub = api_serv.get_subcat_code(request,apdebit.subcategory_code)
                            apdbt_data = APDebitResponse()
                            apdbt_data.set_id(apdebit.id)
                            apdbt_data.set_apinvoiceheader(apdebit.apinvoiceheader_id)
                            apdbt_data.set_apinvoicedetail(apdebit.apinvoicedetail_id)
                            apdbt_data.set_category_code(cat)
                            apdbt_data.set_subcategory_code(sub)
                            apdbt_data.set_debitglno(apdebit.debitglno)
                            apdbt_data.set_amount(apdebit.amount)
                            apdbt_data.set_deductionamount(apdebit.deductionamount)
                            ccbs_list=[]
                            ccb_list = APCCBSDetails.objects.using(self._current_app_schema()).filter(apdebit_id=apdebit.id,entity_id=self._entity_id()).all()
                            for apccbs in ccb_list:
                                api_serv = ApiService(self._scope())
                                cc = api_serv.get_cc_code(request,apccbs.cc_code)
                                bs = api_serv.get_bs_code(request,apccbs.bs_code)
                                apccbs_data = APccbsDetailsResponse()
                                apccbs_data.set_id(apccbs.id)
                                apccbs_data.set_debit(apccbs.apdebit_id)
                                apccbs_data.set_cc_code(cc)
                                apccbs_data.set_bs_code(bs)
                                apccbs_data.set_code(apccbs.code)
                                apccbs_data.set_ccbspercentage(apccbs.ccbspercentage)
                                apccbs_data.set_glno(apccbs.glno)
                                apccbs_data.set_amount(apccbs.amount)
                                apccbs_data.set_remarks(apccbs.remarks)
                                ccbs_list.append(json.loads(apccbs_data.get()))
                                apdbt_data.set_ccbs(apccbs_data)
                                invdeb_list.append(json.loads(apdbt_data.get()))
                                invh_data.set_debit(invdeb_list)

                    crd_list = []
                    for apcredit in credit_list:
                        api_serv = ApiService(self._scope())
                        cat = api_serv.get_cat_code(request, apcredit.category_code)
                        sub = api_serv.get_subcat_code(request, apcredit.subcategory_code)
                        apcredit_data = APCreditResponse()
                        apcredit_data.set_id(apcredit.id)
                        apcredit_data.set_apinvoiceheader(apcredit.apinvoiceheader_id)
                        apcredit_data.set_paymode(apcredit.paymode_id)
                        apcredit_data.set_category_code(cat)
                        apcredit_data.set_subcategory_code(sub)
                        # apcredit_data.set_creditbank_id(apcredit.creditbank_id)
                        apcredit_data.set_suppliertax(apcredit.suppliertax_id)
                        apcredit_data.set_amount(apcredit.amount)
                        apcredit_data.set_creditglno(apcredit.creditglno)
                        apcredit_data.set_creditrefno(apcredit.creditrefno)
                        apcredit_data.set_suppliertaxtype(apcredit.suppliertaxtype)
                        apcredit_data.set_taxexcempted(apcredit.taxexcempted)
                        apcredit_data.set_taxableamount(apcredit.taxableamount)
                        apcredit_data.set_ddtranbranch(apcredit.ddtranbranch)
                        apcredit_data.set_ddpaybranch(apcredit.ddpaybranch)
                        crd_list.append(json.loads(apcredit_data.get()))
                    invh_data.set_credit(crd_list)
                    ecfhdr_list.append(json.loads(invh_data.get()))
            emqu_data.set_apinvheader(ecfhdr_list)
            return emqu_data
        # except:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.INVALID_INVOICE_ID)
        #     error_obj.set_description(ErrorDescription.INVALID_INVOICE_ID)
        #     return error_obj

    def empqlist(self, No):
        emqu = APHeader.objects.using(self._current_app_schema()).get(id=No,entity_id=self._entity_id())
        emqu_data = APHeaderResponse()
        emqu_data.set_id(emqu.id)
        emqu_data.set_crno(emqu.crno)
        emqu_data.set_supplier_type(emqu.supplier_type)
        emqu_data.set_commodity(emqu.commodity_id)
        emqu_data.set_aptype(get_APType(emqu.aptype))
        emqu_data.set_apdate(emqu.apdate)
        emqu_data.set_apamount(emqu.apamount)
        emqu_data.set_apstatus(get_apstatus(emqu.apstatus))
        emqu_data.set_ppx(emqu.ppx)
        emqu_data.set_notename(emqu.notename)
        emqu_data.set_remark(emqu.remark)
        emqu_data.set_payto(emqu.payto)
        emqu_data.set_raisedby(emqu.raisedby)
        emqu_data.set_raiserbranch(emqu.raiserbranch)
        emqu_data.set_raisername(emqu.raisername)
        emqu_data.set_approvername(emqu.approvername)
        return emqu_data

    def empq_search(self, request,vys_page,grn_obj,emp_id):
        print(grn_obj)
        condition = Q(status=1,entity_id=self._entity_id())
        if 'crno' in grn_obj:
            condition = Q(apheader_id__crno__icontains=grn_obj['crno'])
        if 'aptype' in grn_obj:
            condition &= Q(apheader_id__aptype__icontains=grn_obj['aptype'])
        if 'invoiceno' in grn_obj:
            condition &= Q(invoiceno__icontains=grn_obj['invoiceno'])
        if 'invoiceamount' in grn_obj:
            condition &= Q(invoiceamount__icontains=grn_obj['invoiceamount'])
        if 'suppliername' in grn_obj:
            condition &= Q(supplier_id__icontains=grn_obj['suppliername'])
        if 'branch' in grn_obj:
            condition &= Q(supplier_id__icontains=grn_obj['branch'])
        if 'fromdate' in grn_obj:
            condition &= Q(invoicedate__range=(grn_obj['fromdate'], grn_obj['todate']))
        obj = APInvoiceHeader.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        print(obj)
        list_len = len(obj)
        pro_list = NWisefinList()
        if list_len > 0:
            for inv_list in obj:
                api_serv = ApiService(self._scope())
                supp_data = api_serv.get_supliersingle_id(request, inv_list.supplier_id)
                supp_name = supp_data['name']
                invh_data = APInvoiceheaderresponse()
                invh_data.set_id(inv_list.id)
                invh_data.set_apheader(self.empqlist(inv_list.apheader_id))
                invh_data.set_invoiceno(inv_list.invoiceno)
                invh_data.set_dedupinvoiceno(inv_list.dedupinvoiceno)
                invh_data.set_invoicedate(inv_list.invoicedate)
                invh_data.set_suppliergst(inv_list.suppliergst)
                invh_data.set_raisorbranchgst(inv_list.raisorbranchgst)
                invh_data.set_invoiceamount(inv_list.invoiceamount)
                invh_data.set_taxamount(inv_list.taxamount)
                invh_data.set_totalamount(inv_list.totalamount)
                invh_data.set_otheramount(inv_list.otheramount)
                invh_data.set_roundoffamt(inv_list.roundoffamt)
                invh_data.set_invoicegst(inv_list.invoicegst)
                invh_data.set_supplier(supp_name)
                invh_data.set_supplierstate(inv_list.supplierstate_id)
                pro_list.append(json.loads(invh_data.get()))
            vpage = NWisefinPaginator(obj, vys_page.get_index(), 10)
            pro_list.set_pagination(vpage)
        return pro_list


    def fetch_paymentdetails(self,request, crno, emp_id):
            aphdr = APHeader.objects.using(self._current_app_schema()).filter(crno=crno,entity_id=self._entity_id())
            list_len = len(aphdr)
            pro_list = NWisefinList()
            if list_len > 0:
                pay = PreparePapmentService(self._scope())
                aphdr_id = aphdr[0].id
                apinvheader = APInvoiceHeader.objects.using(self._current_app_schema()).get(apheader_id=aphdr_id,entity_id=self._entity_id())
                apinvhdr = apinvheader.id
                print(apinvhdr)
                paydet = PaymentDetails.objects.using(self._current_app_schema()).get(apinvoiceheader_id=apinvhdr,entity_id=self._entity_id())
                print(paydet)
                paydetres = paymentdetailsresponse()
                paydetres.set_id(paydet.id)
                paydetres.set_paymentheader_id(pay.fetch_paylist(paydet.paymentheader_id))
                paydetres.set_apinvoiceheader_id(paydet.apinvoiceheader_id)
                paydetres.set_apcredit_id(paydet.apcredit_id)
                paydetres.set_paymentdetails_amount(paydet.paymentdetails_amount)
                pro_list.append(json.loads(paydetres.get()))
            return pro_list