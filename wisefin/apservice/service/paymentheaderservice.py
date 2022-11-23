import json
import sys
import traceback
from django.db import transaction
from apservice.data.response.apauditresponse import APAuditResponse
from apservice.data.response.apinvoicedetailresponse import APDebitResponse
from apservice.data.response.paymentresponse import PaymentHeaderResponse
from apservice.models import PaymentHeader, PaymentDetails, APQueue, APInvoiceHeader
from apservice.service.apauditservice import APAuditService

from apservice.util.aputil import APModifyStatus, APRefType, APRequestStatusUtil, AP_Status, get_AP_status
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.permissions.filter.commonpermission import ModulePermission
from utilityservice.permissions.util.dbutil import RoleList, ModuleList
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from django.utils.timezone import now

class PreparePapmentService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.AP_SERVICE)
        
    def create_paymentheader_and_details(self,paymenthdr_obj,pymtdtls_list,emp_id):
        try:
            with transaction.atomic(using=self._current_app_schema()):
                Payment_hdr = PaymentHeader.objects.using(self._current_app_schema()).create(
                    paymentheader_date = paymenthdr_obj.get_paymentheader_date(),
                    paymentheader_amount = paymenthdr_obj.get_paymentheader_amount(),
                    pay_to = paymenthdr_obj.get_pay_to(),
                    beneficiary_code = paymenthdr_obj.get_beneficiary_code(),
                    paymode = paymenthdr_obj.get_paymode(),
                    bankdetails_id = paymenthdr_obj.get_bankdetails_id(),
                    beneficiaryname = paymenthdr_obj.get_beneficiaryname(),
                    bankname = paymenthdr_obj.get_bankname(),
                    IFSCcode = paymenthdr_obj.get_ifsccode(),
                    accno = paymenthdr_obj.get_accno(),
                    #debitbankacc=paymenthdr_obj.get_debitbankacc(),
                    remarks = paymenthdr_obj.get_remarks(),
                    created_by=emp_id,entity_id=self._entity_id()
                  # stalechq_id = apdebit_obj.get_debitbankacc(),
                  # refno = apdebit_obj.get_debitbankacc(),
                  # callbackrefno = apdebit_obj.get_callbackrefno(),
                  # dispatch_id = apdebit_obj.get_dispatch_id(),
                  # chqno = apdebit_obj.get_beneficiaryname(),
                  # chqdate = apdebit_obj.get_beneficiaryname()
                     )
                Payment_hdr.pvno = "PV" + str(Payment_hdr.id)
                Payment_hdr.save()

                paymt_dtls_list=list()
                for paymt_dtls in pymtdtls_list:
                    Payment_dtls = PaymentDetails.objects.using(self._current_app_schema()).create(
                                paymentheader_id = Payment_hdr.id,
                                apinvoiceheader_id = paymt_dtls['apinvhdr_id'],
                                apcredit_id = paymt_dtls['apcredit_id'],
                                paymentdetails_amount = paymt_dtls['paymntdtls_amt'],
                                created_by=emp_id,entity_id=self._entity_id())

                    # invoicehdr_get=APInvoiceHeader.objects.using(self._current_app_schema()).filter(
                    #     id=paymt_dtls['apinvhdr_id'],entity_id=self._entity_id()).update(status=AP_Status.PAYMENT_INITIATE,
                    #                                          updated_by=emp_id,
                    #                                          updated_date=now())

                    paymentdtls_json={"paymentheader_id" :Payment_dtls.paymentheader_id,"apinvoiceheader_id":Payment_dtls.apinvoiceheader_id,
                      "apcredit_id":Payment_dtls.apcredit_id,"paymentdetails_amount" :Payment_dtls.paymentdetails_amount}
                    paymt_dtls_list.append(paymentdtls_json)


                    self.audit_function(Payment_dtls, Payment_dtls.id, Payment_dtls.id, emp_id,
                                        APModifyStatus.CREATE, APRequestStatusUtil.ONBORD, APRefType.PAYMENTDETAILS)

                self.audit_function(Payment_hdr, Payment_hdr.id, Payment_hdr.id, emp_id,
                                     APModifyStatus.CREATE,APRequestStatusUtil.ONBORD, APRefType.PAYMENTHEADER)

                # apqueue = APQueue.objects.using(self._current_app_schema()).create(ref_id=Payment_dtls.apinvoiceheader_id,
                #                                                        ref_type=APRefType.APINVOICEHEADER,
                #                                                        from_user_id=emp_id,
                #                                                        to_user_id=emp_id,
                #                                                        created_date=now(),
                #                                                        comments='PREPARE PAYMENT',
                #                                                        status=AP_Status.PAYMENT_INITIATE,
                #                                                        remarks=paymenthdr_obj.get_remarks(),
                #                                                        is_sys=True,entity_id=self._entity_id())


                payment_data = PaymentHeaderResponse()
                payment_data.set_id(Payment_hdr.id)
                payment_data.set_paymentheader_date(str(Payment_hdr.paymentheader_date))
                payment_data.set_paymentheader_amount(str(Payment_hdr.paymentheader_amount))
                # payment_data.set_ref_id(Payment_hdr.ref_id)
                # payment_data.set_reftable_id(Payment_hdr.reftable_id)
                payment_data.set_paymode(Payment_hdr.paymode)
                payment_data.set_bankdetails_id(Payment_hdr.bankdetails_id)
                payment_data.set_beneficiaryname(Payment_hdr.beneficiaryname)
                payment_data.set_bankname(Payment_hdr.bankname)
                payment_data.set_ifsccode(Payment_hdr.IFSCcode)
                payment_data.set_accno(Payment_hdr.accno)
                #payment_data.set_debitbankacc(Payment_hdr.debitbankacc)
                payment_data.set_remarks(Payment_hdr.remarks)
                payment_data.Paymentdtls = (paymt_dtls_list)
                return payment_data
        except Exception as excep:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            traceback.print_exc()
            success_obj = NWisefinSuccess()
            success_obj.set_status(ErrorMessage.INVALID_DATA)
            success_obj.set_message(str(excep))
            success_obj.error_info=(str(filename)+", line_no: "+str(line_number)+str(', exception_type : {c} '.format(c=type(excep).__name__)))
            return success_obj


    def audit_function(self, audit_data, refid, relrefid, emp_id, action,reqstatus, req_type):
        if action == APModifyStatus.DELETE:
            data = None
        else:
            data = audit_data.__dict__
            del data['_state']
        audit_service = APAuditService(self._scope())
        audit_obj = APAuditResponse()
        audit_obj.set_refid(refid)
        audit_obj.set_reqstatus(reqstatus)
        audit_obj.set_reftype(req_type)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(req_type)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)

    def fetch_paylist(self, No):
        Payment_hdr = PaymentHeader.objects.using(self._current_app_schema()).get(id=No,entity_id=self._entity_id())
        payment_data = PaymentHeaderResponse()
        payment_data.set_id(Payment_hdr.id)
        payment_data.set_paymentheader_date(str(Payment_hdr.paymentheader_date))
        payment_data.set_paymentheader_amount(str(Payment_hdr.paymentheader_amount))
        payment_data.set_ref_id(Payment_hdr.ref_id)
        payment_data.set_reftable_id(Payment_hdr.reftable_id)
        payment_data.set_paymode(Payment_hdr.paymode)
        payment_data.set_bankdetails_id(Payment_hdr.bankdetails_id)
        payment_data.set_beneficiaryname(Payment_hdr.beneficiaryname)
        payment_data.set_bankname(Payment_hdr.bankname)
        payment_data.set_ifsccode(Payment_hdr.IFSCcode)
        payment_data.set_accno(Payment_hdr.accno)
        payment_data.set_debitbankacc(Payment_hdr.debitbankacc)
        payment_data.set_remarks(Payment_hdr.remarks)
        payment_data.set_pvno(Payment_hdr.pvno)
        return payment_data


    def preparepaymen_status_update(self,ap_data,emp_id):
        try:
            invoicehdr_get = APInvoiceHeader.objects.using(self._current_app_schema()).filter(
                id=ap_data['apinvoiceheader_id'], entity_id=self._entity_id()).update(status=AP_Status.PAYMENT_INITIATE,
                                                                                  updated_by=emp_id,
                                                                                  updated_date=now())

            apqueue = APQueue.objects.using(self._current_app_schema()).create(ref_id=ap_data['apinvoiceheader_id'],
                                                                               ref_type=APRefType.APINVOICEHEADER,
                                                                               from_user_id=emp_id,
                                                                               to_user_id=emp_id,
                                                                               created_date=now(),
                                                                               comments='MOVE TO PREPARE PAYMENT',
                                                                               status=AP_Status.PAYMENT_INITIATE,
                                                                               remarks=ap_data.get('remarks'),
                                                                               is_sys=True, entity_id=self._entity_id())

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj
        except Exception as excep:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            traceback.print_exc()
            success_obj = NWisefinSuccess()
            success_obj.set_status(ErrorMessage.INVALID_DATA)
            success_obj.set_message(str(excep))
            success_obj.error_info=(str(filename)+", line_no: "+str(line_number)+str(', exception_type : {c} '.format(c=type(excep).__name__)))
            return success_obj

    def validation_pvno_using_apinvoiceheader_id(self,apinvoiceheader_id):
        Payment_dtls_count = PaymentDetails.objects.using(self._current_app_schema()).filter(
            apinvoiceheader_id=apinvoiceheader_id,entity_id=self._entity_id(),is_delete=0).count()
        print('Payment_dtls_count ',Payment_dtls_count)

        if Payment_dtls_count > 0:
            return True
        else:
            return False



    def get_payment_and_inward_details(self,request, crno,emp_id):
        try:
            Payment_details = PaymentDetails.objects.using(self._current_app_schema()).filter(is_delete=0,status=1,
                apinvoiceheader__apheader__crno=crno,entity_id=self._entity_id())

            resp_list = NWisefinList()
            if len(Payment_details) >0:
                for Payment_dtl in Payment_details:
                    payment_data = PaymentHeaderResponse()
                    from utilityservice.service.ap_api_service import APApiService
                    from apservice.service.apcreditservice import APCreditService
                    ap_api = APApiService(self._scope())
                    apcrdt=APCreditService(self._scope())
                    inwarddtls_id = Payment_dtl.apinvoiceheader.apheader.inwarddetails_id
                    payment_data.set_id(Payment_dtl.id)
                    payment_data.apinvoiceheader_id = Payment_dtl.apinvoiceheader_id
                    payment_data.inwarddetails_id = inwarddtls_id
                    payment_data.inwarddetails = ap_api.fetch_inward_no_using_inwaddtls_id(request, inwarddtls_id)

                    payment_data.invoiceno = Payment_dtl.apinvoiceheader.invoiceno
                    payment_data.invoicedate = str(Payment_dtl.apinvoiceheader.invoicedate)
                    payment_data.invoiceamount = str(Payment_dtl.apinvoiceheader.invoiceamount)
                    payment_data.pvno = Payment_dtl.paymentheader.pvno
                    apcrdit_data=apcrdt.fetch_apcredit_account_dtls_using_single_credit(request,Payment_dtl.apinvoiceheader_id,emp_id)
                    paymode_id=apcrdit_data.paymode_id
                    payment_data.paymode_details = ap_api.paymode_single_get(paymode_id)

                    payment_data.header_date = str(Payment_dtl.paymentheader.paymentheader_date)
                    payment_data.cheque_no = Payment_dtl.paymentheader.chqno
                    cheque_date  = Payment_dtl.paymentheader.chqdate
                    if cheque_date != None:
                        cheque_date = str(cheque_date)
                    payment_data.cheque_date = cheque_date
                    payment_data.header_amount = str(Payment_dtl.paymentheader.paymentheader_amount)
                    payment_data.details_amount = str(Payment_dtl.paymentdetails_amount)
                    payment_data.refno = str(Payment_dtl.paymentheader.refno)
                    payment_data.utr_refno = str(Payment_dtl.paymentheader.callbackrefno)
                    payment_data.apstatus = get_AP_status(Payment_dtl.apinvoiceheader.status)
                    resp_list.append(payment_data)
            return resp_list
        except Exception as excep:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            traceback.print_exc()
            success_obj = NWisefinSuccess()
            success_obj.set_status("Failed")
            success_obj.set_message(str(excep) +" - "+str(filename)+", line_no: "+str(line_number)+str(', exception_type : {c} '.format(c=type(excep).__name__)))
            return success_obj

    def update_UTR_refno_using_pvno(self,pv_no,utr_refno,emp_id):
        Payment_hdr = PaymentHeader.objects.using(self._current_app_schema()).filter(pvno=pv_no,entity_id=self._entity_id(),
                                    is_delete=0).update(callbackrefno=utr_refno,
                                                        updated_by=emp_id,
                                                        updated_date=now())
