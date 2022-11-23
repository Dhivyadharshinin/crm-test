import json
import traceback

from django.db.models import Q

from apservice.data.response.apauditresponse import APAuditResponse
from apservice.data.response.apcreditresponse import APCreditResponse
from apservice.models import APCredit
from apservice.service.apauditservice import APAuditService

from apservice.util.aputil import APRefType, APModifyStatus, ap_get_api_caller, ap_post_api_caller
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from django.utils.timezone import now
from django.db import IntegrityError, transaction


class APCreditService(NWisefinThread):
    def __init__(self, scope): 
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.AP_SERVICE)

    #@transaction(using=self._current_app_schema())
    def apcredit_create(self,apcrdt_obj,apinvoicehdr_id,emp_id):

        if not apcrdt_obj.get_id() is None:
            from apservice.service.apservice import APService
            apserv = APService(self._scope())
            vendor_type = apserv.get_vendor_type(apcrdt_obj.get_creditglno())
            apcrdt_update = APCredit.objects.using(self._current_app_schema()).filter(id=apcrdt_obj.get_id(),entity_id=self._entity_id()).update(
                                                                apinvoiceheader_id=apinvoicehdr_id,
                                                                paymode_id=apcrdt_obj.get_paymode_id(),
                                                                creditbank_id=apcrdt_obj.get_creditbank_id(),
                                                                suppliertax_id=apcrdt_obj.get_suppliertax_id(),
                                                                creditglno=apcrdt_obj.get_creditglno(),
                                                                creditrefno=apcrdt_obj.get_creditrefno(),
                                                                suppliertaxtype=apcrdt_obj.get_suppliertaxtype(),
                                                                suppliertaxrate=apcrdt_obj.get_suppliertaxrate(),
                                                                taxexcempted=apcrdt_obj.get_taxexcempted(),
                                                                amount=apcrdt_obj.get_amount(),
                                                                taxableamount=apcrdt_obj.get_taxableamount(),
                                                                ddtranbranch=apcrdt_obj.get_ddtranbranch(),
                                                                ddpaybranch=apcrdt_obj.get_ddpaybranch(),
                                                                category_code=apcrdt_obj.get_category_code(),
                                                                subcategory_code=apcrdt_obj.get_subcategory_code(),
                                                                #bankdetails_id=apcrdt_obj.get_bankdetails_id(),
                                                                vendor_type=vendor_type,
                                                                updated_by=emp_id,
                                                                updated_date=now())
            #TDS and LIQ Dedection
            from utilityservice.service.ap_api_service import APApiService
            ap_api_serv = APApiService(self._scope())
            paymode_liq_detail = ap_api_serv.paymode_single_get_with_name("LIQ")
            paymode_tds_detail = ap_api_serv.paymode_single_get_with_name("TDS")
            paymod_tds_id = paymode_tds_detail['data'][0]['id']
            paymod_liq_id = paymode_liq_detail['data'][0]['id']
            if int(apcrdt_obj.paymode_id) == int(paymod_tds_id) or int(apcrdt_obj.paymode_id) == int(paymod_liq_id) :
                print('tds_liq_detection_in_credit ', apcrdt_obj.paymode_id)
                print('apinvoicehdr_id ', apinvoicehdr_id)
                self.tds_liq_detection_in_credit(apinvoicehdr_id,emp_id)

            # bankdetails_update
            from apservice.service.apinvoiceheaderservice import APInvoiceheaderService
            apinvhdr_serv = APInvoiceheaderService(self._scope())
            apinvhdr_serv.apinvoicehdr_bankdetails_update(apinvoicehdr_id, apcrdt_obj.get_bankdetails_id(), emp_id)

            apcredit = APCredit.objects.using(self._current_app_schema()).get(id=apcrdt_obj.get_id(),
                                                                              entity_id=self._entity_id())

            self.audit_function(apcredit, apcredit.id, apcredit.id, emp_id,
                                APModifyStatus.UPDATE, APRefType.APCREDIT)

        else:
            from apservice.service.apservice import APService
            apserv = APService(self._scope())
            vendor_type=apserv.get_vendor_type(apcrdt_obj.get_creditglno())
            apcredit = APCredit.objects.using(self._current_app_schema()).create(
                                            apinvoiceheader_id=apinvoicehdr_id,
                                            paymode_id=apcrdt_obj.get_paymode_id(),
                                            creditbank_id = apcrdt_obj.get_creditbank_id(),
                                            suppliertax_id = apcrdt_obj.get_suppliertax_id(),
                                            creditglno = apcrdt_obj.get_creditglno(),
                                            creditrefno = apcrdt_obj.get_creditrefno(),
                                            suppliertaxtype = apcrdt_obj.get_suppliertaxtype(),
                                            suppliertaxrate = apcrdt_obj.get_suppliertaxrate(),
                                            taxexcempted = apcrdt_obj.get_taxexcempted(),
                                            amount = apcrdt_obj.get_amount(),
                                            taxableamount = apcrdt_obj.get_taxableamount(),
                                            ddtranbranch = apcrdt_obj.get_ddtranbranch(),
                                            ddpaybranch = apcrdt_obj.get_ddpaybranch(),
                                            category_code = apcrdt_obj.get_category_code(),
                                            subcategory_code = apcrdt_obj.get_subcategory_code(),
                                            #bankdetails_id = apcrdt_obj.get_bankdetails_id(),
                                            vendor_type=vendor_type,
                                            created_by=emp_id,
                                            entity_id=self._entity_id())

            # TDS and LIQ Dedection
            from utilityservice.service.ap_api_service import APApiService
            ap_api_serv = APApiService(self._scope())
            paymode_liq_detail = ap_api_serv.paymode_single_get_with_name("LIQ")
            paymode_tds_detail = ap_api_serv.paymode_single_get_with_name("TDS")
            paymod_tds_id = paymode_tds_detail['data'][0]['id']
            paymod_liq_id = paymode_liq_detail['data'][0]['id']
            if int(apcrdt_obj.paymode_id) == int(paymod_tds_id) or int(apcrdt_obj.paymode_id) == int(paymod_liq_id):
                print('tds_liq_detection_in_credit ', paymod_liq_id)
                print('apinvoicehdr_id ', apinvoicehdr_id)
                self.tds_liq_detection_in_credit(apinvoicehdr_id, emp_id)

            #bankdetails_update
            from apservice.service.apinvoiceheaderservice import APInvoiceheaderService
            apinvhdr_serv=APInvoiceheaderService(self._scope())
            apinvhdr_serv.apinvoicehdr_bankdetails_update(apinvoicehdr_id, apcrdt_obj.get_bankdetails_id(), emp_id)

            self.audit_function(apcredit, apcredit.id, apcredit.id, emp_id,
                                APModifyStatus.CREATE, APRefType.APCREDIT)


        apcredit_data = APCreditResponse()
        apcredit_data.set_id(apcredit.id)
        apcredit_data.set_apinvoiceheader(apcredit.apinvoiceheader_id)
        apcredit_data.set_paymode(apcredit.paymode_id)
        apcredit_data.set_category_code(apcredit.category_code)
        apcredit_data.set_subcategory_code(apcredit.subcategory_code)
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
        apcredit_data.set_vendor_type(apcredit.vendor_type)
        return apcredit_data

    # def tds_detection_in_credit(self,apinvoicehdr_id,emp_id):
    #     from utilityservice.service.ap_api_service import APApiService
    #     ap_api_serv = APApiService(self._scope())
    #     paymode_details = ap_api_serv.paymode_single_get_with_name("TDS")
    #     logger.info('apinvoicehdr_id ' + str(apinvoicehdr_id))
    #     logger.info('paymode_details ' + str(paymode_details))
    #     paymode_id = paymode_details['data'][0]['id']
    #     logger.info('paymode_id ' + str(paymode_id))
    #     apcredit_tds = APCredit.objects.using(self._current_app_schema()).filter(apinvoiceheader_id=apinvoicehdr_id,
    #                                             is_delete=0,paymode_id=paymode_id,entity_id=self._entity_id())[0]
    #     logger.info('apcredit_tds ' + str(apcredit_tds))
    #     apcredit_entry = APCredit.objects.using(self._current_app_schema()).filter(apinvoiceheader_id=apinvoicehdr_id,
    #                                 is_delete=0, category_code='SUSPENSE',entity_id=self._entity_id())[0]
    #     logger.info('apcredit_entry ' + str(apcredit_entry))
    #
    #     detect_amt=float(apcredit_tds.amount)
    #     dedection_amt=float(apcredit_entry.apinvoiceheader.totalamount)-float(detect_amt)
    #
    #     logger.info('detect_amt ' + str(detect_amt))
    #     logger.info('dedection_amt ' + str(apcredit_entry))
    #
    #     apcredit_suspense_minus = APCredit.objects.using(self._current_app_schema()).filter(id=apcredit_entry.id,
    #                                           is_delete=0 ,entity_id=self._entity_id()).update(
    #                                                             amount=dedection_amt,
    #                                                             updated_by=emp_id,
    #                                                             updated_date=now())

    def tds_liq_detection_in_credit(self,apinvoicehdr_id,emp_id):
        from utilityservice.service.ap_api_service import APApiService
        ap_api_serv = APApiService(self._scope())

        apcredit_tds_liq = APCredit.objects.using(self._current_app_schema()).filter(apinvoiceheader_id=apinvoicehdr_id,
                                                                                 is_delete=0,entity_id=self._entity_id())
        for tds_liq in apcredit_tds_liq:
            paymode_single=ap_api_serv.paymode_single_get(tds_liq.paymode_id)
            gl_flag=paymode_single['gl_flag']
            if str(gl_flag) == "Payable":
                #tds_liq_creditid=tds_liq.id
                dedection_amt=tds_liq.amount


        logger.info('detect_amt ' + str(dedection_amt))
        print('dedection_amt ' , str(dedection_amt))

        apcredit_suspense_minus = APCredit.objects.using(self._current_app_schema()).filter(apinvoiceheader_id=apinvoicehdr_id,
                           category_code='SUSPENSE',is_delete=0 ,entity_id=self._entity_id()).update(
                                                                amount=dedection_amt,
                                                                updated_by=emp_id,
                                                                updated_date=now())

    # def liq_detection_in_credit(self,credit,apinvoicehdr_id,emp_id):
    #
    #
    #     apcredit_liq = APCredit.objects.using(self._current_app_schema()).filter(apinvoiceheader_id=apinvoicehdr_id,
    #                            category_code= 'SUSPENSE' ,is_delete=0,entity_id=self._entity_id())[0]
    #
    #     dedection_amt=float(apcredit_liq.amount)-float(credit.amount)
    #     print('credit.amount ',credit.amount)
    #     print('apcredit_liq.amount ',apcredit_liq.amount)
    #     print('dedection_amt ',dedection_amt)
    #     print('apcredit_liq.id ',apcredit_liq.id)
    #     print('schema ', self._current_app_schema())
    #
    #     apcredit_suspense_minus = APCredit.objects.using(self._current_app_schema()).filter(id=apcredit_liq.id,
    #                                                             entity_id=self._entity_id()).update(
    #                                                             amount=dedection_amt,
    #                                                             updated_by=emp_id,
    #                                                             updated_date=now())
    #     print('apinvoicehdr_id ',apinvoicehdr_id)
    #     print('apcredit_suspense_minus ',apcredit_suspense_minus)



    def audit_function(self, audit_data, refid, relrefid, emp_id, action, reqstatus):
        if action == APModifyStatus.DELETE:
            data = None
        else:
            data = audit_data.__dict__
            del data['_state']
        audit_service = APAuditService(self._scope())
        audit_obj = APAuditResponse()
        audit_obj.set_refid(refid)
        audit_obj.set_reqstatus(reqstatus)
        audit_obj.set_reftype(APRefType.APCREDIT)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(APRefType.APCREDIT)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)


    def fetch_apcredit_using_invoiceheader(self,request,apinvhdr_id,emp_id):

        apcredit_data = APCredit.objects.using(self._current_app_schema()).filter(apinvoiceheader_id=apinvhdr_id,
                                                                                  is_delete=0,entity_id=self._entity_id())
        apcredit_list = []
        #bank_arr = []
        if len(apcredit_data) > 0 :
            # for i in apcredit_data:
            #     bank_arr.append(i.creditbank_id)
            for apcredit in apcredit_data:
                from utilityservice.service import api_service
                api_serv = api_service.ApiService(self._scope())
                from utilityservice.service.ap_api_service import APApiService
                ap_api_serv = APApiService(self._scope())
                cat = api_serv.get_cat_code(request, apcredit.category_code)
                #sub = api_serv.get_subcat_code(request, apcredit.subcategory_code)
                from utilityservice.service.ap_api_service import APApiService
                ap_api_serv = APApiService(self._scope())
                sub = ap_api_serv.get_apsubcategory_code(apcredit.category_code, apcredit.subcategory_code)
                apcredit_resp = APCreditResponse()
                supplierbranch_id=apcredit.apinvoiceheader.supplier_id
                supplierpayment_details =None
                if supplierbranch_id and  apcredit.paymode_id and apcredit.creditrefno:
                    supplierpayment_details=ap_api_serv.get_apcredit_supplierpayment(supplierbranch_id, apcredit.paymode_id, apcredit.creditrefno, emp_id)

                #bank_data = ap_get_api_caller(request,{"api_url":'/mstserv/bank/'+str(apcredit.creditbank_id)})
                bank_data = None
                if apcredit.creditbank_id:
                    bank_data = ap_api_serv.get_apcredit_singlebank_data(apcredit.creditbank_id,emp_id)

                apcredit_resp.set_id(apcredit.id)
                apcredit_resp.set_supplierpayment_details(supplierpayment_details)
                apcredit_resp.set_apinvoiceheader(apcredit.apinvoiceheader_id)
                apcredit_resp.set_vendor_type(apcredit.vendor_type)
                if apcredit.paymode_id is None:
                    pay = None
                else:
                    pay = ap_api_serv.paymode_single_get(apcredit.paymode_id)
                apcredit_resp.set_paymode(pay)
                # bankdtl = (credit_service.fetch_payment_listget(request, vys_page,supp,,emp_id))
                # crd_data.set_paydetails(bankdtl)
                apcredit_resp.set_category_code(cat)
                apcredit_resp.set_subcategory_code(sub)
                apcredit_resp.set_creditbank(bank_data)
                apcredit_resp.set_suppliertax(apcredit.suppliertax_id)
                apcredit_resp.set_suppliertaxrate(apcredit.suppliertaxrate)
                apcredit_resp.set_amount(apcredit.amount)
                apcredit_resp.set_creditglno(apcredit.creditglno)
                apcredit_resp.set_creditrefno(apcredit.creditrefno)
                apcredit_resp.set_suppliertaxtype(apcredit.suppliertaxtype)
                apcredit_resp.set_taxexcempted(apcredit.taxexcempted)
                apcredit_resp.set_taxableamount(apcredit.taxableamount)
                apcredit_resp.set_ddtranbranch(apcredit.ddtranbranch)
                apcredit_resp.set_ddpaybranch(apcredit.ddpaybranch)


                if int(apcredit.status) == 1:
                    is_display="YES"
                else:
                    is_display="NO"
                apcredit_resp.set_is_display(is_display)
                apcredit_list.append(json.loads(apcredit_resp.get()))
            return apcredit_list

    def single_get_apcredit(self,request,apinvoiceheader_id, emp_id):

            apcredit = APCredit.objects.using(self._current_app_schema()).filter(apinvoiceheader_id=apinvoiceheader_id,
                                                                                 is_delete=0,entity_id=self._entity_id())[0]

            from utilityservice.service import api_service
            api_serv = api_service.ApiService(self._scope())
            cat = api_serv.get_cat_code(request, apcredit.category_code)
            #sub = api_serv.get_subcat_code(request, apcredit.subcategory_code)
            from utilityservice.service.ap_api_service import APApiService
            ap_api_serv = APApiService(self._scope())
            sub = ap_api_serv.get_apsubcategory_code(apcredit.category_code, apcredit.subcategory_code)
            apcredit_resp = APCreditResponse()
            #bank_data = api_serv.get_bank_list(request, bank_arr)
            #bank_data = ap_get_api_caller(request, {"api_url":'/mstserv/bank/'+str(apcredit.creditbank_id)})

            bank_data = ap_api_serv.fetch_bank_single(apcredit.creditbank_id, emp_id)
            print('bank_data',bank_data)
            print('apcredit_creditbank_id',apcredit.creditbank_id)

            #bankbranch_data = ap_get_api_caller(request, {"api_url":'/mstserv/bankbranch_search?bank_id='+str(apcredit.creditbank_id)})
            #print('bankbranch_data', bankbranch_data)
            #apdebit_data = ap_get_api_caller(request, { "api_url": '/venserv/branch/' + str(apcredit.apinvoiceheader.supplier_id) + '/payment/'+ str(apcredit.creditbank_id)})
            # beneficiary = None
            # if type(dict()) == type(apdebit_data) :
            #     beneficiary=apdebit_data['beneficiary']
            #print('apdebit_data',apdebit_data)

            supplierbranch_id = apcredit.apinvoiceheader.supplier_id
            supplierpayment_details = None
            if supplierbranch_id and apcredit.paymode_id and apcredit.creditrefno:
                supplierpayment_details = ap_api_serv.get_apcredit_supplierpayment(supplierbranch_id,
                                                                                   apcredit.paymode_id,
                                                                                   apcredit.creditrefno, emp_id)

            apcredit_resp.set_id(apcredit.id)
            apcredit_resp.set_vendor_type(apcredit.vendor_type)
            apcredit_resp.set_apinvoiceheader(apcredit.apinvoiceheader_id)
            apcredit_resp.set_supplierpayment_details(supplierpayment_details)
            if apcredit.paymode_id is None:
                pay = None
            else:
                from utilityservice.service.ap_api_service import APApiService
                ap_api_serv = APApiService(self._scope())
                pay = ap_api_serv.paymode_single_get(apcredit.paymode_id)
            print("payment",pay)
            apcredit_resp.set_paymode(pay)
            apcredit_resp.paymode_id = (apcredit.paymode_id)
            # bankdtl = (credit_service.fetch_payment_listget(request, vys_page,supp,,emp_id))
            # crd_data.set_paydetails(bankdtl)
            apcredit_resp.set_category_code(cat)
            apcredit_resp.set_subcategory_code(sub)
            apcredit_resp.creditbank=(bank_data)
            # apcredit_resp.beneficiaryname=(beneficiary)
            # apcredit_resp.bankbranch=(bankbranch_data)
            apcredit_resp.set_suppliertax(apcredit.suppliertax_id)
            apcredit_resp.set_suppliertaxrate(apcredit.suppliertaxrate)
            apcredit_resp.set_amount(apcredit.amount)
            apcredit_resp.set_creditglno(apcredit.creditglno)
            apcredit_resp.set_creditrefno(apcredit.creditrefno)
            apcredit_resp.set_suppliertaxtype(apcredit.suppliertaxtype)
            apcredit_resp.set_taxexcempted(apcredit.taxexcempted)
            apcredit_resp.set_taxableamount(apcredit.taxableamount)
            apcredit_resp.set_ddtranbranch(apcredit.ddtranbranch)
            apcredit_resp.set_ddpaybranch(apcredit.ddpaybranch)
            return apcredit_resp




    def fetch_apcredit_list(self,request,apinvhdr_id, emp_id):

        apcredit_data = APCredit.objects.using(self._current_app_schema()).filter(apinvoiceheader_id=apinvhdr_id,entity_id=self._entity_id(),
                                                                                  is_delete=0)
        apcredit_list  = NWisefinList()
        if len(apcredit_data) > 0 :
            for apcredit in apcredit_data:
                from utilityservice.service import api_service
                api_serv = api_service.ApiService(self._scope())
                cat = api_serv.get_cat_code(request, apcredit.category_code)
                #sub = api_serv.get_subcat_code(request, apcredit.subcategory_code)
                from utilityservice.service.ap_api_service import APApiService
                ap_api_serv = APApiService(self._scope())
                sub = ap_api_serv.get_apsubcategory_code(apcredit.category_code, apcredit.subcategory_code)
                apcredit_resp = APCreditResponse()

                #bank_data = ap_get_api_caller(request,{"api_url":'/mstserv/bank/'+str(apcredit.creditbank_id)})
                apinwrdinvhdr=apcredit.apinvoiceheader
                #bankdetails = ap_get_api_caller(request, {"api_url": '/mstserv/bankdetails/' + str(apinwrdinvhdr.bankdetails_id)})

                bankdetails = ap_api_serv.get_ap_bankdetails_master(apinwrdinvhdr.bankdetails_id, emp_id)
                #bank_data = ap_api_serv.fetch_bank_single(apcredit.creditbank_id, emp_id)
                print(bankdetails,bankdetails)

                emp_accntno_dtls = self.fetch_apcredit_account_dtls_using_single_credit(request, apcredit.apinvoiceheader_id, emp_id)
                emp_accntno = None
                if emp_accntno_dtls:
                    emp_accntno = emp_accntno_dtls.creditrefno
                emp_accntdtls = NWisefinList()
                print('emp_accntno ', emp_accntno)
                if emp_accntno:
                    print('crno ', apcredit.apinvoiceheader.apheader.crno)
                    print('apinwrdinvhdr.apheader.raisedby ', apcredit.apinvoiceheader.apheader.raisedby)
                    emp_accntdtls = ap_api_serv.fetch_apraiser_emp_accntdtls_using_accntno(request, emp_accntno,
                                                                                           apcredit.apinvoiceheader.apheader.raisedby)

                supplierbranch_id = apcredit.apinvoiceheader.supplier_id
                supplierpayment_details = None
                if supplierbranch_id and apcredit.paymode_id and apcredit.creditrefno:
                    supplierpayment_details = ap_api_serv.get_apcredit_supplierpayment(supplierbranch_id,
                                                                                       apcredit.paymode_id,
                                                                                       apcredit.creditrefno, emp_id)

                apcredit_resp.set_id(apcredit.id)
                apcredit_resp.set_apinvoiceheader(apcredit.apinvoiceheader_id)
                if apcredit.paymode_id is None:
                    pay = None
                else:
                    from utilityservice.service.ap_api_service import APApiService
                    ap_api_serv = APApiService(self._scope())
                    pay = ap_api_serv.paymode_single_get(apcredit.paymode_id)
                apcredit_resp.set_paymode(pay)
                apcredit_resp.employee_account_dtls = (emp_accntdtls)
                apcredit_resp.set_category_code(cat)
                apcredit_resp.set_vendor_type(apcredit.vendor_type)
                apcredit_resp.set_subcategory_code(sub)
                apcredit_resp.set_supplierpayment_details(supplierpayment_details)
                apcredit_resp.set_creditbank(apcredit.creditbank_id)
                apcredit_resp.set_suppliertax(apcredit.suppliertax_id)
                apcredit_resp.set_suppliertaxrate(apcredit.suppliertaxrate)
                apcredit_resp.set_amount(apcredit.amount)
                apcredit_resp.set_creditglno(apcredit.creditglno)
                apcredit_resp.set_creditrefno(apcredit.creditrefno)
                apcredit_resp.set_suppliertaxtype(apcredit.suppliertaxtype)
                apcredit_resp.set_taxexcempted(apcredit.taxexcempted)
                apcredit_resp.set_taxableamount(apcredit.taxableamount)
                apcredit_resp.set_ddtranbranch(apcredit.ddtranbranch)
                apcredit_resp.set_ddpaybranch(apcredit.ddpaybranch)
                apcredit_resp.bankdetails=(bankdetails)
                if int(apcredit.status) == 1:
                    is_display="YES"
                else:
                    is_display="NO"
                apcredit_resp.set_is_display(is_display)
                apcredit_resp.pay_to = (apcredit.apinvoiceheader.apheader.payto)
                apcredit_list.append(apcredit_resp)
        return apcredit_list


    def fetch_apcredit_account_dtls(self,request,apinvhdr_id, emp_id):
        condition=Q(apinvoiceheader_id=apinvhdr_id,entity_id=self._entity_id(),
                    status=1,is_delete=0)&~Q(creditrefno=0)&~Q(creditrefno="")&~Q(creditrefno__isnull=True)
        apcredit_data = APCredit.objects.using(self._current_app_schema()).filter(condition)
        print(apcredit_data.query)
        apcredit=None
        if len(apcredit_data) > 0:
            apcredit=apcredit_data[0]
        return apcredit


    def fetch_apcredit_account_dtls_using_single_credit(self,request,apinvoiceheader_id, emp_id):
        from utilityservice.service.ap_api_service import APApiService
        ap_api_serv = APApiService(self._scope())
        era_paymode_detail = ap_api_serv.paymode_single_get_with_name("ERA")
        neft_paymode_detail = ap_api_serv.paymode_single_get_with_name("NEFT")
        era_paymod_id = int(era_paymode_detail['data'][0]['id'])
        neft_paymod_id = int(neft_paymode_detail['data'][0]['id'])

        condition=Q(apinvoiceheader_id=apinvoiceheader_id,entity_id=self._entity_id(),
                    status=1,is_delete=0,paymode_id__in=[era_paymod_id,neft_paymod_id])
        apcredit_data = APCredit.objects.using(self._current_app_schema()).filter(condition)
        print(apcredit_data.query)
        print('len apcredit_data',len(apcredit_data))
        apcredit=None
        if len(apcredit_data) > 0:
            apcredit=apcredit_data[0]
        return apcredit


    def fetch_apcredit_using_category_code(self,request,apinvhdr_id,category_code, emp_id):

        apcredit_data = APCredit.objects.using(self._current_app_schema()).filter(apinvoiceheader_id=apinvhdr_id,entity_id=self._entity_id(),
                                                            status=0,is_delete=0,category_code=category_code)

        print('apinvhdr_id,category_code ',apinvhdr_id,"  " ,category_code)
        print('len(apcredit_data)',len(apcredit_data))
        print('apcredit_data',apcredit_data)

        apcredit_list  = NWisefinList()
        #if len(apcredit_data) ==1  :
        if len(apcredit_data) > 0  :
            apcredit = apcredit_data[0]
            from utilityservice.service import api_service
            api_serv = api_service.ApiService(self._scope())
            cat = api_serv.get_cat_code(request, apcredit.category_code)
            #sub = api_serv.get_subcat_code(request, apcredit.subcategory_code)
            from utilityservice.service.ap_api_service import APApiService
            ap_api_serv = APApiService(self._scope())
            sub = ap_api_serv.get_apsubcategory_code(apcredit.category_code, apcredit.subcategory_code)
            apcredit_resp = APCreditResponse()
            #bank_data = ap_get_api_caller(request,{"api_url":'/mstserv/bank/'+str(apcredit.creditbank_id)})
            apinwrdinvhdr=apcredit.apinvoiceheader
            #bankdetails = ap_get_api_caller(request, {"api_url": '/mstserv/bankdetails/' + str(apinwrdinvhdr.bankdetails_id)})

            bankdetails = ap_api_serv.get_ap_bankdetails_master(apinwrdinvhdr.bankdetails_id, emp_id)
            bank_data = ap_api_serv.fetch_bank_single(apcredit.creditbank_id, emp_id)
            print(bankdetails,bankdetails)
            #supplierbranch_id = apcredit.apinvoiceheader.supplier_id
            # supplierpayment_details = None
            # if supplierbranch_id and apcredit.paymode_id and apcredit.creditrefno:
            #     supplierpayment_details = ap_api_serv.get_apcredit_supplierpayment(supplierbranch_id,
            #                                                                        apcredit.paymode_id,
            #                                                                        apcredit.creditrefno, emp_id)

            apcredit_resp.set_id(apcredit.id)
            apcredit_resp.set_apinvoiceheader(apcredit.apinvoiceheader_id)
            if apcredit.paymode_id is None:
                pay = None
            else:
                from utilityservice.service.ap_api_service import APApiService
                ap_api_serv = APApiService(self._scope())
                pay = ap_api_serv.paymode_single_get(apcredit.paymode_id)
            apcredit_resp.set_paymode(pay)
            apcredit_resp.set_category_code(cat)
            apcredit_resp.set_vendor_type(apcredit.vendor_type)
            apcredit_resp.set_subcategory_code(sub)
            #apcredit_resp.set_supplierpayment_details(supplierpayment_details)
            apcredit_resp.set_creditbank(bank_data)
            apcredit_resp.set_suppliertax(apcredit.suppliertax_id)
            apcredit_resp.set_suppliertaxrate(apcredit.suppliertaxrate)
            apcredit_resp.set_amount(apcredit.amount)
            apcredit_resp.set_creditglno(apcredit.creditglno)
            apcredit_resp.set_creditrefno(apcredit.creditrefno)
            apcredit_resp.set_suppliertaxtype(apcredit.suppliertaxtype)
            apcredit_resp.set_taxexcempted(apcredit.taxexcempted)
            apcredit_resp.set_taxableamount(apcredit.taxableamount)
            apcredit_resp.set_ddtranbranch(apcredit.ddtranbranch)
            apcredit_resp.set_ddpaybranch(apcredit.ddpaybranch)
            apcredit_resp.bankdetails=(bankdetails)
            if int(apcredit.status) == 1:
                is_display="YES"
            else:
                is_display="NO"
            apcredit_resp.set_is_display(is_display)
            apcredit_list.append(apcredit_resp)
        return apcredit_list






    def get_apcredit_single(self,request,apcreditr_id,emp_id):
        try:
            apcredit = APCredit.objects.using(self._current_app_schema()).get(id=apcreditr_id,is_delete=0,
                                                                              entity_id=self._entity_id())
            from utilityservice.service import api_service
            api_serv = api_service.ApiService(self._scope())
            cat = api_serv.get_cat_code(request, apcredit.category_code)
            #sub = api_serv.get_subcat_code(request, apcredit.subcategory_code)
            from utilityservice.service.ap_api_service import APApiService
            ap_api_serv = APApiService(self._scope())
            sub = ap_api_serv.get_apsubcategory_code(apcredit.category_code, apcredit.subcategory_code)
            apcredit_resp = APCreditResponse()
            #bank_data = ap_get_api_caller(request,{"api_url":'/mstserv/bankbranch_search?bank_id='+str(apcredit.creditbank_id)})
            from utilityservice.service.ap_api_service import APApiService
            ap_api_serv = APApiService(self._scope())

            supplierbranch_id = apcredit.apinvoiceheader.supplier_id
            supplierpayment_details = None
            if supplierbranch_id and apcredit.paymode_id and apcredit.creditrefno:
                supplierpayment_details = ap_api_serv.get_apcredit_supplierpayment(supplierbranch_id,
                                                                      apcredit.paymode_id,apcredit.creditrefno, emp_id)

            #apinvoicehdr_id = apcredit.apinvoiceheader.id
            emp_accntno_dtls = self.fetch_apcredit_account_dtls_using_single_credit(request, apcredit.id, emp_id)
            emp_accntno = None
            if emp_accntno_dtls:
                emp_accntno = emp_accntno_dtls.creditrefno
            emp_accntdtls = NWisefinList()
            print('emp_accntno ', emp_accntno)
            if emp_accntno:
                print('crno ',  apcredit.apinvoiceheader.apheader.crno)
                print('apinwrdinvhdr.apheader.raisedby ', apcredit.apinvoiceheader.apheader.raisedby)
                emp_accntdtls = ap_api_serv.fetch_apraiser_emp_accntdtls_using_accntno(request, emp_accntno,
                                                                                       apcredit.apinvoiceheader.apheader.raisedby)


            apcredit_resp.set_id(apcredit.id)
            apcredit_resp.set_apinvoiceheader(apcredit.apinvoiceheader_id)
            if apcredit.paymode_id is None:
                pay = None
            else:
                from utilityservice.service.ap_api_service import APApiService
                ap_api_serv = APApiService(self._scope())
                pay = ap_api_serv.paymode_single_get(apcredit.paymode_id)
            apcredit_resp.set_paymode(pay)
            apcredit_resp.employee_account_dtls=(emp_accntdtls)
            apcredit_resp.set_supplierpayment_details(supplierpayment_details)
            apcredit_resp.set_category_code(cat)
            apcredit_resp.set_vendor_type(apcredit.vendor_type)
            apcredit_resp.set_subcategory_code(sub)
            apcredit_resp.set_creditbank(apcredit.creditbank_id)
            apcredit_resp.set_suppliertax(apcredit.suppliertax_id)
            apcredit_resp.set_suppliertaxrate(apcredit.suppliertaxrate)
            apcredit_resp.set_amount(apcredit.amount)
            apcredit_resp.set_creditglno(apcredit.creditglno)
            apcredit_resp.set_creditrefno(apcredit.creditrefno)
            apcredit_resp.set_suppliertaxtype(apcredit.suppliertaxtype)
            apcredit_resp.set_taxexcempted(apcredit.taxexcempted)
            apcredit_resp.set_taxableamount(apcredit.taxableamount)
            apcredit_resp.set_ddtranbranch(apcredit.ddtranbranch)
            apcredit_resp.set_ddpaybranch(apcredit.ddpaybranch)
            apcredit_resp.pay_to=(apcredit.apinvoiceheader.apheader.payto)
            if int(apcredit.status) == 1:
                is_display = "YES"
            else:
                is_display = "NO"
            apcredit_resp.set_is_display(is_display)
            return apcredit_resp

        except Exception as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj


    def apcredit_delete(self,apcreditr_id,emp_id):
        try:
            apcredit = APCredit.objects.using(self._current_app_schema()).filter(id=apcreditr_id, is_delete=0,
                                                                                 entity_id=self._entity_id()).update(
                is_delete=1, updated_by=emp_id, updated_date=now())

            if apcredit == 0:
                error_obj = NWisefinError()
                error_obj.set_code('INVALID_CREDIT_ID')
                error_obj.set_description('INVALID CREDIT ID')
                return error_obj
            else:
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
                return success_obj

        except Exception as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

    def apcredit_delete_entry(self,invoiceheader_id,emp_id):
        try:
            apcredit_entrydata_delete = APCredit.objects.using(self._current_app_schema()).filter(
                apinvoiceheader_id=invoiceheader_id, is_delete=0, is_entry=True,
                entity_id=self._entity_id()).update(is_delete=1,
                                                    updated_by=emp_id,
                                                    updated_date=now())

            if apcredit_entrydata_delete == 0:
                error_obj = NWisefinError()
                error_obj.set_code('INVALID_INVOICEHEADER_ID')
                error_obj.set_description('INVALID INVOICE HEADER ID')
                return error_obj
            else:
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
                return success_obj

        except Exception as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

    def fetch_tdsrate_calculation(self,request,creditamount,tdsamt,emp_id):
        try:
            tds_rate=float(creditamount) * (float(tdsamt)/100)
            #print('tds_rate',tds_rate)
            #print('creditamount',creditamount)
            subtraction_rate=float(creditamount) - tds_rate
            #print('subtraction_rate', subtraction_rate)
            crd_data = APCreditResponse()
            crd_data.set_tdsrate(round(tds_rate,2))
            crd_data.set_tds_subtraction_rate(round(subtraction_rate,2))
            crd_data.set_creditamount(creditamount)
            crd_data.set_tds_percentage(tdsamt)
            return crd_data

        except Exception as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

    def credit_dtls_get(self,request,apinvoiceheader_id):
        # from utilityservice.service import api_service
        # api_serv = api_service.ApiService(self._scope())
        # pay = api_serv.paymode_single_get(request, apcredit.paymode_id)
        apcredit = APCredit.objects.using(self._current_app_schema()).filter(apinvoiceheader_id=apinvoiceheader_id,
                                                paymode_id=5,
                                                is_delete=0,
                                                entity_id=self._entity_id())[0]
        return apcredit

    def entry_module_name_return(self,credit_is_rcm_isblocked,aptype_id):
        from utilityservice.service.ap_api_service import APApiService
        ap_api_serv = APApiService(self._scope())
        aptype_data = ap_api_serv.get_ap_ecftypesingle(aptype_id)
        module_name = aptype_data['text']
        print(' aptype_data_module_name', module_name)
        credit_is_rcm = credit_is_rcm_isblocked[0]
        credit_isblocked = credit_is_rcm_isblocked[-1]
        if credit_is_rcm == "Y":
            module_name = "NON PO RCM"
        # if credit_isblocked == "Y":
        #     module_name = "NON PO BLOCKED"
        print('module_name', module_name)
        logger.info('module_name ' + str(module_name))
        return module_name

    def entry_apcredit(self,request,apdata,credit_is_rcm_isblocked,emp_id):
        apcredit_data = APCredit.objects.using(self._current_app_schema()).filter(apinvoiceheader_id=apdata['invoiceheader_id'], is_delete=0,
                                                                             entity_id=self._entity_id())
        aptype_id=apcredit_data[0].apinvoiceheader.apheader.aptype
        crno=apcredit_data[0].apinvoiceheader.apheader.crno
        print('crno', crno)
        module_name=self.entry_module_name_return(credit_is_rcm_isblocked, aptype_id)
        if int(aptype_id) == 4:
            module_name = str(apcredit_data[0].apinvoiceheader.apheader.crno)[0:3]
        print('module_name ---> ',module_name)

        entrydebit_data = ap_post_api_caller(request, {"api_url": '/entryserv/commonquerydata?type=CREDIT',
                                                       "crno": crno,
                                                       "invoiceheader_id":apdata['invoiceheader_id'],
                                                       "invoicedetails_id": "0",
                                                       "module_name": str(module_name)})
        print('entrydebit_data ',entrydebit_data)

        if 'apcredit' not in entrydebit_data:
            success_obj = NWisefinSuccess()
            success_obj.set_status("Failed")
            success_obj.set_message("Please check entry template")
            return success_obj

        print('entrydebit_data ', entrydebit_data)
        logger.info('entrydebit_data '  + str(entrydebit_data))
        print('entrydebit_data apcredit', entrydebit_data['apcredit'])
        logger.info('entrydebit_data apcredit'  + str(entrydebit_data['apcredit']))

        for obj_deb in entrydebit_data['apcredit']:

            if 'category_code' in obj_deb:
                if obj_deb['category_code'] is not None and obj_deb['category_code'] != '' and obj_deb['category_code'] != 'DYNAMIC':
                    if 'code' in obj_deb['category_code']:
                        if obj_deb['category_code']['code'] is not None and obj_deb['category_code']['code'] != '' and obj_deb['category_code']['code'] != 'DYNAMIC':
                            category_code = obj_deb['category_code']['code']
            if 'subcategory_code' in obj_deb:
                if obj_deb['subcategory_code'] is not None and obj_deb['subcategory_code'] != '' and obj_deb['subcategory_code'] != 'DYNAMIC':
                    if obj_deb['subcategory_code']['code'] is not None and obj_deb['subcategory_code']['code'] != '' and obj_deb['subcategory_code']['code'] != 'DYNAMIC':
                        subcategory_code = obj_deb['subcategory_code']['code']
            if 'debitglno' in obj_deb:
                if obj_deb['debitglno'] is not None and obj_deb['debitglno'] != '' and obj_deb['debitglno'] != 'DYNAMIC':
                    creditglno = obj_deb['debitglno']
                    duplicate_gl = False
                    # for obj_apcredit in apcredit_data:
                    #     creditglno_int=obj_apcredit.creditglno
                    #     if int(creditglno) == int(creditglno_int):
                    #         duplicate_gl=True
                    # if duplicate_gl is True:
                    #     continue
            if 'amount' in obj_deb:
                if obj_deb['amount'] is not None and obj_deb['amount'] != '' and obj_deb['amount'] != 'DYNAMIC':
                    amount = obj_deb['amount']

            is_display = obj_deb['display']
            if is_display == 'NO':
                status = 0
            else:
                status = 1

            from utilityservice.service.ap_api_service import APApiService
            ap_api_serv = APApiService(self._scope())
            paymode_details = ap_api_serv.paymode_single_get_with_name("CREDITGL")
            print('paymode_details', paymode_details)
            paymode_id = paymode_details['data'][0]['id']
            #apcredit_entrydata_delete
            # apcredit_entrydata_delete = APCredit.objects.using(self._current_app_schema()).filter(
            #     apinvoiceheader_id=apdata['invoiceheader_id'], is_delete=0,is_entry=True,
            #     entity_id=self._entity_id()).update(is_delete=1,
            #                                         updated_by=emp_id,
            #                                         updated_date=now())
            from apservice.service.apservice import APService
            apserv = APService(self._scope())
            vendor_type = apserv.get_vendor_type(creditglno)
            apcredit = APCredit.objects.using(self._current_app_schema()).create(
                apinvoiceheader_id=apdata['invoiceheader_id'],
                vendor_type=vendor_type,
                paymode_id=paymode_id,
                creditbank_id=None,
                suppliertax_id=None,
                creditglno=creditglno,
                creditrefno=0,
                suppliertaxtype=None,
                suppliertaxrate=0,
                taxexcempted="N",
                amount=amount,
                taxableamount=0,
                ddtranbranch=0,
                ddpaybranch=0,
                category_code=category_code,
                subcategory_code=subcategory_code,
                created_by=emp_id,
                status=status,
                is_entry=True,
                entity_id=self._entity_id())

            self.audit_function(apcredit, apcredit.id, apcredit.id, emp_id,
                                APModifyStatus.CREATE, APRefType.APCREDIT)

        return True



