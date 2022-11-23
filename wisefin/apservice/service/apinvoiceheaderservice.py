import json
import sys
import traceback
from datetime import datetime
import numpy as np
import pandas as pd
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse


from apservice.data.response.apauditresponse import APAuditResponse
from apservice.data.response.apinvoiceheaderresponse import APInvoiceheaderresponse
from apservice.models import APInvoiceHeader, APBounce, PaymentDetails, APQueue, APFiles, APHeader
from apservice.service.apauditservice import APAuditService
from apservice.service.apdebitservice import APDebitService
from apservice.service.apinvoicedetailsservice import APInvoiceDetailService
from apservice.service.apservice import APService


from apservice.util.aputil import APModifyStatus, APRefType, ap_get_api_caller, get_APType, get_AP_status, AP_Status, \
    dropdown_status, ap_post_api_caller
from nwisefin.settings import logger
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

class APInvoiceheaderService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.AP_SERVICE)

    def apinvhdrcreate(self,request,file_array,apinvhdr_json,apinvhdr_obj,aphdr_id,emp_id):

        if not apinvhdr_obj.get_id() is None:
            apinvhdr_update = APInvoiceHeader.objects.using(self._current_app_schema()).filter(id=apinvhdr_obj.get_id(),
                                                                                    entity_id=self._entity_id()).update(
                                                                                apheader_id=aphdr_id,
                                                                                invoiceno=apinvhdr_obj.get_invoiceno(),
                                                                                dedupinvoiceno=apinvhdr_obj.get_dedupinvoiceno(),
                                                                                invoicedate=apinvhdr_obj.get_invoicedate(),
                                                                                #suppliergst=apinvhdr_obj.get_suppliergst(),
                                                                                #raisorbranchgst=apinvhdr_obj.get_raisorbranchgst(),
                                                                                invoiceamount=apinvhdr_obj.get_invoiceamount(),
                                                                                taxamount=apinvhdr_obj.get_taxamount(),
                                                                                totalamount=apinvhdr_obj.get_totalamount(),
                                                                                otheramount=apinvhdr_obj.get_otheramount(),
                                                                                roundoffamt=apinvhdr_obj.get_roundoffamt(),
                                                                                invoicegst=apinvhdr_obj.get_invoicegst(),
                                                                                supplier_id=apinvhdr_obj.get_supplier_id(),
                                                                                supplierstate_id=apinvhdr_obj.get_supplierstate_id(),
                                                                                updated_by=emp_id,
                                                                                updated_date=now())
            apinvhdr = APInvoiceHeader.objects.using(self._current_app_schema()).get(id=apinvhdr_obj.get_id(),
                                                                                     entity_id=self._entity_id())
            file_resp=None
            #addtional_file_add_in_apinvoiceheader
            if 'file_key' in apinvhdr_json:
                if len(apinvhdr_json['file_key']) > 0:
                    file_resp=self.addtional_file_add_in_apinvoiceheader(request,apinvhdr_json, apinvhdr.id, emp_id)

            self.audit_function(apinvhdr, apinvhdr.id, apinvhdr.id, emp_id,
                                APModifyStatus.UPDATE, APRefType.APINVOICEHEADER)

        else:

            apinvhdr = APInvoiceHeader.objects.using(self._current_app_schema()).create(
                                                apheader_id=aphdr_id,
                                                invoiceno=apinvhdr_obj.get_invoiceno(),
                                                dedupinvoiceno=apinvhdr_obj.get_dedupinvoiceno(),
                                                invoicedate=apinvhdr_obj.get_invoicedate(),
                                                suppliergst=apinvhdr_obj.get_suppliergst(),
                                                raisorbranchgst=apinvhdr_obj.get_raisorbranchgst(),
                                                invoiceamount=apinvhdr_obj.get_invoiceamount(),
                                                taxamount=apinvhdr_obj.get_taxamount(),
                                                totalamount=apinvhdr_obj.get_totalamount(),
                                                otheramount=apinvhdr_obj.get_otheramount(),
                                                roundoffamt=apinvhdr_obj.get_roundoffamt(),
                                                invoicegst=apinvhdr_obj.get_invoicegst(),
                                                supplier_id=apinvhdr_obj.get_supplier_id(),
                                                supplierstate_id=apinvhdr_obj.get_supplierstate_id(),
                                                apinvoiceheader_crno=apinvhdr_obj.get_invoicehdr_crno(),
                                                created_by=emp_id, entity_id=self._entity_id())

            y = now().strftime("%y")
            m = now().strftime("%m")
            d = now().strftime("%d")
            apinvhdr.barcode = 'BAR' + y + m + d + str(apinvhdr.id).zfill(4)
            apinvhdr.save()
            #file data insert here
            file_resp=None
            if file_array is not None:
                for file_json in file_array:
                    from apservice.service.apdocumentservice import APDocumentService
                    apdoc_serv=APDocumentService(self._scope())
                    file_json['id']=file_json['file_id']
                    apdoc_serv.apdocumentcreate( request, file_json, apinvhdr.id, emp_id)

            apserv=APService(self._scope())
            queue_dict={"ref_id":apinvhdr.id,"ref_type":APRefType.APINVOICEHEADER,"remarks":None,"from_user_id":emp_id,
                        "status":AP_Status.NEW,"to_user_id":-1,"comments":"PENDING FOR APPROVAL"}

            apserv.create_apqueue(queue_dict)
            self.audit_function(apinvhdr, apinvhdr.id, apinvhdr.id, emp_id,
                                APModifyStatus.CREATE, APRefType.APINVOICEHEADER)

        apinhdr_data = APInvoiceheaderresponse()
        apinhdr_data.set_id(apinvhdr.id)
        apinhdr_data.set_apheader(apinvhdr.apheader_id)
        apinhdr_data.file_data=(file_resp)
        apinhdr_data.set_invoiceno(apinvhdr.invoiceno)
        apinhdr_data.set_dedupinvoiceno(apinvhdr.dedupinvoiceno)
        apinhdr_data.set_invoicedate(apinvhdr.invoicedate)
        apinhdr_data.set_suppliergst(apinvhdr.suppliergst)
        apinhdr_data.set_raisorbranchgst(apinvhdr.raisorbranchgst)
        apinhdr_data.set_invoiceamount(apinvhdr.invoiceamount)
        apinhdr_data.set_taxamount(apinvhdr.taxamount)
        apinhdr_data.set_totalamount(apinvhdr.totalamount)
        apinhdr_data.set_otheramount(apinvhdr.otheramount)
        apinhdr_data.set_roundoffamt(apinvhdr.roundoffamt)
        apinhdr_data.set_invoicegst(apinvhdr.invoicegst)
        apinhdr_data.set_supplier(apinvhdr.supplier_id)
        apinhdr_data.set_supplierstate(apinvhdr.supplierstate_id)
        apinhdr_data.set_barcode(apinvhdr.barcode)
        apinhdr_data.set_entry_flag(self.invhdr_boolean_conver_to_number(apinvhdr.entry_flag))

        # if apinvhdr_obj.get_supplier_id() != '':
        #     apinhdr_data.set_gsttype(gsttype)

        return apinhdr_data

    def addtional_file_add_in_apinvoiceheader(self,request,apinvhdr_json, apinvhdr_id, emp_id):
        file_resp=None
        file_list = list()
        if len(apinvhdr_json['file_key']) > 0:
            from utilityservice.service.ap_api_service import APApiService
            for file_key in apinvhdr_json['file_key']:
                file_data = 11
                doc_serv = APApiService(self._scope())
                file_resp = doc_serv.doc_upload_ap(request, file_data, file_key)
                print('file_resp ',file_resp)
                file_list = file_resp['data']
                print('file_list ',file_list)
                logger.info('file_list ', file_list)

        # file data insert here
        if file_list is not None and len(file_list) > 0:
            for file_json in file_list:
                from apservice.service.apdocumentservice import APDocumentService
                apdoc_serv = APDocumentService(self._scope())
                apdoc_serv.apdocumentcreate(request, file_json, apinvhdr_id, emp_id)
        return file_resp



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
        audit_obj.set_reftype(APRefType.APHEADER)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(APRefType.APHEADER)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)

    def fetch_apinvhdr_using_aphdr(self,request,aphdr_id,emp_id):
            apinvhdr_data = APInvoiceHeader.objects.using(self._current_app_schema()).filter(apheader_id=aphdr_id,
                                                                            entity_id=self._entity_id(),is_delete=0)
            apinvhdr_list = []
            if len(apinvhdr_data) > 0:
                for apinvhdr in apinvhdr_data:
                    from utilityservice.service import api_service
                    api_serv = api_service.ApiService(self._scope())
                    apinvdtl_serv = APInvoiceDetailService(self._scope())
                    from apservice.service.apcreditservice import APCreditService
                    apcredit_serv=APCreditService(self._scope())
                    inhdr_data = APInvoiceheaderresponse()
                    #supplier_data = ap_get_api_caller(request,{"api_url":'/venserv/get_supplier/'+str(apinvhdr.supplier_id)})
                    from utilityservice.service.ap_api_service import APApiService
                    ap_api_serv = APApiService(self._scope())
                    supplier_data = ap_api_serv.fetch_single_supplier_data(apinvhdr.supplier_id)
                    bankdetails = ap_api_serv.get_ap_bankdetails_master(apinvhdr.bankdetails_id, emp_id)
                    #print("bankdetails_response", bankdetails)
                    logger.info('supplier_data ' + str(supplier_data))
                    print("supplier_data ", supplier_data)


                    apinwrdinvhdr_data = APFiles.objects.using(self._current_app_schema()).filter(ref_id=apinvhdr.id,is_delete=0,
                                                                   entity_id=self._entity_id(), ref_type=APRefType.APINVOICEHEADER)
                    if len(apinwrdinvhdr_data) > 0:
                        inhdr_data.apfile = list(apinwrdinvhdr_data.values('id', 'file_id', 'filename'))
                    else:
                        inhdr_data.apfile = []

                    from apservice.service.apcreditservice import APCreditService
                    ap_credit = APCreditService(self._scope())
                    emp_accntno_dtls = ap_credit.fetch_apcredit_account_dtls(request, apinvhdr.id, emp_id)
                    emp_accntno = None
                    if emp_accntno_dtls:
                        emp_accntno = emp_accntno_dtls.creditrefno
                    emp_accntdtls = NWisefinList()
                    if emp_accntno :
                        print('crno ', apinvhdr.apheader.crno)
                        print('emp_accntno ', emp_accntno)
                        print('apinwrdinvhdr.apheader.raisedby ', apinvhdr.apheader.raisedby)
                        emp_accntdtls = ap_api_serv.fetch_apraiser_emp_accntdtls_using_accntno(request, emp_accntno,
                                                                                               apinvhdr.apheader.raisedby)
                    #

                    # from utilityservice.service import api_service
                    # api_serv = api_service.ApiService(self._scope())
                    # emp = api_serv.get_empsingle_id(request, emp_id)
                    # print('emp2', emp)
                    # emp_add = emp['address_id']
                    # empadd = api_serv.get_empaddress_id(request, emp_add)
                    #
                    # gst = empadd['state_id']
                    # if apinvhdr.supplier_id != '':
                    #     state = api_serv.get_statesingle_id(request, apinvhdr.supplierstate_id)
                    #     supp = api_serv.get_supliersingle_id(request, apinvhdr.supplier_id)
                    #     suppadd = supp['address_id']
                    #     ven = api_serv.get_venaddress(request, suppadd)
                    #     supgst = ven['state_id']
                    #     if supgst != gst:
                    #         gsttype = 'IGST'
                    #     else:
                    #         gsttype = 'SGST & CGST'
                    # inhdr_data.set_supplierstate(state)
                    # if apinvhdr.supplier_id != '':
                    #     inhdr_data.set_gsttype(gsttype)

                    inhdr_data.set_id(apinvhdr.id)
                    inhdr_data.set_apheader(apinvhdr.apheader_id)
                    inhdr_data.set_invoiceno(apinvhdr.invoiceno)
                    inhdr_data.set_dedupinvoiceno(apinvhdr.dedupinvoiceno)
                    inhdr_data.set_invoicedate(apinvhdr.invoicedate)
                    inhdr_data.set_suppliergst(apinvhdr.suppliergst)
                    inhdr_data.set_raisorbranchgst(apinvhdr.raisorbranchgst)
                    inhdr_data.set_invoiceamount(apinvhdr.invoiceamount)
                    inhdr_data.set_taxamount(apinvhdr.taxamount)
                    inhdr_data.set_totalamount(apinvhdr.totalamount)
                    inhdr_data.set_otheramount(apinvhdr.otheramount)
                    inhdr_data.set_roundoffamt(apinvhdr.roundoffamt)
                    inhdr_data.set_invoicegst(apinvhdr.invoicegst)
                    inhdr_data.debit_bankdetails = (bankdetails)
                    inhdr_data.supplier_id = (apinvhdr.supplier_id)
                    inhdr_data.set_employee_account_dtls(emp_accntdtls)
                    inhdr_data.set_entry_flag(self.invhdr_boolean_conver_to_number(apinvhdr.entry_flag))

                    if apinvhdr.supplier_id is not None :
                        inhdr_data.set_gsttype(self.get_gst_type(request,apinvhdr,emp_id))
                    else:
                        inhdr_data.set_gsttype(None)
                    inhdr_data.set_apinvoicedetails(apinvdtl_serv.fetch_apinvdtl_using_apinvhdr(request, apinvhdr.id,emp_id))
                    inhdr_data.set_apcredit(apcredit_serv.fetch_apcredit_using_invoiceheader(request, apinvhdr.id,emp_id))
                    inhdr_data.set_supplier(supplier_data)
                    #inhdr_data.supplier_data = api_serv.get_supliersingle_id(request, apinvhdr.supplier_id)
                    #print('supplierstate_id',apinvhdr.supplierstate_id)
                    if apinvhdr.supplierstate_id is not None:
                        inhdr_data.supplierstate_data = api_serv.get_statesingle_id(request, apinvhdr.supplierstate_id)
                    else:
                        inhdr_data.supplierstate_data = None
                    inhdr_data.set_barcode(apinvhdr.barcode)
                    inhdr_data.set_status(get_AP_status(apinvhdr.status))
                    inhdr_data.set_invoicehdr_crno(apinvhdr.apinvoiceheader_crno)
                    apinvhdr_list.append(json.loads(inhdr_data.get()))
            return apinvhdr_list

    def get_apinvhdr_using_apinvhdr(self,apinvhdr):
            apinvoicehdr_data = APInvoiceHeader.objects.using(self._current_app_schema()).filter(id=apinvhdr,
                                                              entity_id=self._entity_id(),is_delete=0)
            return_json = dict()
            if len(apinvoicehdr_data) > 0:
                apinvhdr_data=apinvoicehdr_data[0]
                from utilityservice.service.ap_api_service import APApiService
                ap_api_serv = APApiService(self._scope())
                empbranch_data = ap_api_serv.ap_employee_branch_single_get(apinvhdr_data.apheader.raiserbranch)
                return_json['empbranch_code']=empbranch_data.get('code')
                return_json['is_dovendor']=False
                return_json['invoice_no']=apinvhdr_data.invoiceno
                return_json['invoice_date']=str(apinvhdr_data.invoicedate.strftime("%d-%m-%Y"))
                payto=apinvhdr_data.apheader.payto
                if str(payto) == 'S':
                    #vendor_name
                    supplier_data=ap_api_serv.fetch_single_supplier_data_with_vendor(apinvhdr_data.supplier_id)
                    return_json['Payto']=str(supplier_data['vendor_name'])
                elif str(payto) == 'E':
                    return_json['Payto']=str(apinvhdr_data.apheader.raisername)


            return return_json

    def get_gst_type(self,request,apinvhdr,emp_id):
        from utilityservice.service import api_service
        api_serv = api_service.ApiService(self._scope())
        emp = api_serv.get_empsingle_id(request, emp_id)
        print('emp2', emp)
        emp_add = emp['address_id']
        empadd = api_serv.get_empaddress_id(request, emp_add)

        gst = empadd['state_id']
        gsttype=None
        if apinvhdr.supplier_id != '' and apinvhdr.supplier_id != None :
            supp = api_serv.get_supliersingle_id(request, apinvhdr.supplier_id)
            suppadd = supp['address_id']
            ven = api_serv.get_venaddress(request, suppadd)
            supgst = ven['state_id']
            if supgst != gst:
                gsttype = 'IGST'
            else:
                gsttype = 'SGST & CGST'

        return gsttype

    def get_pocket_apinvoiceheader(self,request,emp_id,inwarddtl_id):
        try:
            condition=Q(status__in=[AP_Status.NEW,AP_Status.BOUNCE,AP_Status.RE_AUDIT,
                                    AP_Status.PAYMENT_INITIATE,AP_Status.REJECTED,AP_Status.PAID],
                        apheader__inwarddetails_id=inwarddtl_id,is_delete=0,entity_id=self._entity_id())
            apinwrdinvhdr_data = APInvoiceHeader.objects.using(self._current_app_schema()).filter(condition)

            resp_list = NWisefinList()
            print('len(apinwrdinvhdr_data)',len(apinwrdinvhdr_data))
            if len(apinwrdinvhdr_data) > 0:
                for apinwrdinvhdr in apinwrdinvhdr_data:
                    apinwardind_resp = APInvoiceheaderresponse()
                    apinwrdinvhdr_data = APFiles.objects.using(self._current_app_schema()).filter(ref_id=apinwrdinvhdr.id,is_delete=0,
                                                            entity_id=self._entity_id(),ref_type=APRefType.APINVOICEHEADER)
                    if len(apinwrdinvhdr_data) > 0:
                        #print("apinwrdinvhdr_data ", list(apinwrdinvhdr_data.values('id', 'file_id', 'filename')))
                        apinwardind_resp.apfile = list(apinwrdinvhdr_data.values('id', 'file_id', 'filename'))
                    else:
                        apinwardind_resp.apfile = []


                    apheader=apinwrdinvhdr.apheader
                    #supplier_data=ap_get_api_caller(request, {"api_url":'/venserv/get_supplier/'+str(apinwrdinvhdr.supplier_id)})
                    apinwardind_resp.set_id(apinwrdinvhdr.id)
                    apinwardind_resp.set_crno(apheader.crno)
                    apinwardind_resp.set_apdate(str(apheader.apdate))
                    apinwardind_resp.set_apamount(apheader.apamount)
                    apinwardind_resp.set_raiser_employeename(apheader.raisername)
                    apinwardind_resp.set_approvername(apheader.approvername)
                    apinwardind_resp.set_apheader_id(apheader.id)
                    apinwardind_resp.set_inwarddetails_id(apheader.inwarddetails_id)
                    apinwardind_resp.set_invoice_no(apinwrdinvhdr.invoiceno)
                    apinwardind_resp.set_remarks(apheader.remark)
                    apinwardind_resp.set_status(get_AP_status(apinwrdinvhdr.status))
                    apinwardind_resp.invoicegst = (apinwrdinvhdr.invoicegst)
                    apinwardind_resp.set_barcode(apinwrdinvhdr.barcode)
                    apinwardind_resp.set_entry_flag(self.invhdr_boolean_conver_to_number(apinwrdinvhdr.entry_flag))
                    apinwardind_resp.set_gsttype(self.get_gst_type(request, apinwrdinvhdr, emp_id))
                    apinwardind_resp.set_invoicehdr_crno(apinwrdinvhdr.apinvoiceheader_crno)
                    # apinwardind_resp.set_invoicetype_id(get_APType(apheader.aptype))
                    # apinwardind_resp.set_supplier(supplier_data
                    # apinwardind_resp.set_invoice_date(apinwrdinvhdr.invoicedate)
                    # apinwardind_resp.set_invoice_amount(apheader.apamount)
                    # apinwardind_resp.set_status(get_AP_status(apinwrdinvhdr.status))
                    resp_list.append(apinwardind_resp)
            return resp_list

        except Exception  as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj



    def single_get_apinwardinvoiceheader(self,request,apinvhdr_id,emp_id):
        try:
            condition=Q(is_delete=0,id=apinvhdr_id,entity_id=self._entity_id())
            apinwrdinvhdr = APInvoiceHeader.objects.using(self._current_app_schema()).get(condition)
            apheader=apinwrdinvhdr.apheader
            supplier_data=ap_get_api_caller(request, {"api_url":'/venserv/get_supplier/'+str(apinwrdinvhdr.supplier_id)})
            branch_data=ap_get_api_caller(request, {"api_url":'/usrserv/employeebranch/'+str(apheader.raiserbranch)})
            aptype_data = ap_get_api_caller(request, {"api_url": '/ecfserv/get_ecftype_single/' + str(apheader.aptype)})

            apinwardind_resp = APInvoiceheaderresponse()
            apinwrdinvhdr_data = APFiles.objects.using(self._current_app_schema()).filter(ref_id=apinwrdinvhdr.id,is_delete=0,
                                             entity_id=self._entity_id(),ref_type=APRefType.APINVOICEHEADER)
            if len(apinwrdinvhdr_data) > 0:
                apinwardind_resp.apfile = list(apinwrdinvhdr_data.values('id', 'file_id', 'filename'))
            else:
                apinwardind_resp.apfile = []

            apinwardind_resp.set_id(apinwrdinvhdr.id)
            apinwardind_resp.set_crno(apheader.crno)
            apinwardind_resp.set_inwarddetails_id(apheader.inwarddetails_id)
            apinwardind_resp.set_invoicetype(aptype_data)
            apinwardind_resp.set_supplier(supplier_data)
            apinwardind_resp.set_invoice_no(apinwrdinvhdr.invoiceno)
            apinwardind_resp.set_invoice_date(apinwrdinvhdr.invoicedate)
            apinwardind_resp.set_branch(branch_data)
            apinwardind_resp.apheader_amount=(apheader.apamount)
            apinwardind_resp.set_barcode(apinwrdinvhdr.barcode)
            apinwardind_resp.set_remarks(apheader.remark)
            apinwardind_resp.set_raiser_employeename(apheader.raisername)
            apinwardind_resp.set_status(get_AP_status(apinwrdinvhdr.status))
            apinwardind_resp.set_gsttype(self.get_gst_type(request, apinwrdinvhdr, emp_id))
            apinwardind_resp.set_invoice_amount(apinwrdinvhdr.invoiceamount)
            apinwardind_resp.set_taxamount(apinwrdinvhdr.taxamount)
            apinwardind_resp.set_totalamount(apinwrdinvhdr.totalamount)
            apinwardind_resp.set_otheramount(apinwrdinvhdr.otheramount)
            apinwardind_resp.set_roundoffamt(apinwrdinvhdr.roundoffamt)
            apinwardind_resp.set_deductionamt(apinwrdinvhdr.deductionamt)
            apinwardind_resp.invoicegst=(apinwrdinvhdr.invoicegst)
            apinwardind_resp.set_invoicehdr_crno(apinwrdinvhdr.apinvoiceheader_crno)

            return apinwardind_resp

        except Exception  as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

    def apinvoiceheader_delete(self,apinvheader_id,emp_id):
        try:
            apcredit = APInvoiceHeader.objects.using(self._current_app_schema()).filter(id=apinvheader_id,
                                                            is_delete=0,entity_id=self._entity_id()).update(
                is_delete=1,updated_by=emp_id,updated_date=now())

            if apcredit == 0:
                error_obj = NWisefinError()
                error_obj.set_code('INVALID_INVOICEHEADER_ID')
                error_obj.set_description('INVALID INVOICEHEADER ID')
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



    def apinvoiceheader_update_entry_flag(self,apinvoicehdr_id,entry_flag,emp_id):
        try:
            apcredit = APInvoiceHeader.objects.using(self._current_app_schema()).filter(id=apinvoicehdr_id,
                                                            is_delete=0,entity_id=self._entity_id()).update(
                        entry_flag=entry_flag,updated_by=emp_id,updated_date=now())

            if apcredit == 0:
                error_obj = NWisefinError()
                error_obj.set_code('INVALID_INVOICEHEADER_ID')
                error_obj.set_description('INVALID INVOICEHEADER ID')
                return error_obj
            else:
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                return success_obj

        except Exception as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj


    def get_apinwardinvoiceheader(self, request, filter_json, vys_page, emp_id):
        try:
            # condition=Q (status__in=[AP_Status.NEW,AP_Status.BOUNCE,AP_Status.RE_AUDIT,AP_Status.REJECTED],is_delete=0)
            module_permission = ModulePermission(self._scope())
            resp_list = NWisefinList()
            role_arr = module_permission.employee_modulerole(emp_id, ModuleList.AP)
            print('role_arr',role_arr)
            maker = RoleList.maker
            checker = RoleList.checker
            if maker in role_arr or checker in role_arr:
                condition = Q(created_by = emp_id,is_delete=0,entity_id=self._entity_id())
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description('You dont have permission')
                return error_obj
            print('status',filter_json.get('status'))
            # print((filter_json.get('status') == dropdown_status.APPROVED_BY_ME))
            if (filter_json.get('status') == AP_Status.NEW):
                condition &= Q(status=AP_Status.NEW)
            elif (filter_json.get('status') == AP_Status.PENDING_FOR_APPROVAL):
                condition &= Q(status=AP_Status.PENDING_FOR_APPROVAL)
            elif (filter_json.get('status') == AP_Status.BOUNCE):
                condition &= Q(status=AP_Status.BOUNCE)
            elif (filter_json.get('status') == AP_Status.RE_AUDIT):
                condition &= Q(status=AP_Status.RE_AUDIT)
            elif (filter_json.get('status') == dropdown_status.REJECTED_BY_ME):
                condition &= Q(status=dropdown_status.REJECTED_BY_ME)
            elif (filter_json.get('status') == AP_Status.PAYMENT_INITIATE):
                condition &= Q(status=AP_Status.PAYMENT_INITIATE)
            elif (filter_json.get('status') == dropdown_status.APPROVED_BY_ME):
                condition &= Q(status__in=dropdown_status.APPROVED_BY_ME)
            if 'crno' in filter_json:
                condition &= Q(apheader__crno = filter_json.get('crno'))
            print('filter_jason',filter_json)
            if 'invoicetype_id' in filter_json:
                condition &= Q(apheader__aptype__in=filter_json.get('invoicetype_id'))
            if 'supplier_id' in filter_json:
                condition &= Q(supplier_id=filter_json.get('supplier_id'))
            if 'branch_id' in filter_json:
                condition &= Q(apheader__raiserbranch=filter_json.get('branch_id'))
            if 'raisername' in filter_json:
                condition &= Q(apheader__raisername__icontains=filter_json.get('raisername'))
            if 'invoice_no' in filter_json:
                condition &= Q(invoiceno__icontains=filter_json.get('invoice_no'))
            if 'invoice_amount' in filter_json:
                condition &= Q(apheader__apamount__icontains=filter_json.get('invoice_amount'))
            if 'invoice_from_date' in filter_json and 'invoice_to_date' in filter_json:
                inv_from_date = filter_json.get('invoice_from_date')
                inv_to_date = filter_json.get('invoice_to_date')
                condition &= Q(invoicedate__gte=inv_from_date, invoicedate__lte=inv_to_date)
            # if 'inward_from_date' in filter_json and 'inward_to_date' in filter_json:
            #     inward_from_date = datetime.strptime(filter_json.get('inward_from_date'), '%d-%m-%Y')
            #     inward_to_date = datetime.strptime(filter_json.get('inward_to_date'), '%d-%m-%Y')
            #     condition&=Q(invoice_date__gte=inward_from_date,invoice_date__lte=inward_to_date)
            print('condition',condition)

            apinwrdinvhdr_data = APInvoiceHeader.objects.using(self._current_app_schema()).filter(condition).order_by("-id")[
                                 vys_page.get_offset():vys_page.get_query_limit()]
            print('apinwrdinvhdr_data',apinwrdinvhdr_data)
            if len(apinwrdinvhdr_data) > 0:
                for apinwrdinvhdr in apinwrdinvhdr_data:
                    apheader = apinwrdinvhdr.apheader
                    supplier_data = ap_get_api_caller(request, {
                        "api_url": '/venserv/get_supplier/' + str(apinwrdinvhdr.supplier_id)})
                    branch_data = ap_get_api_caller(request, {"api_url": '/usrserv/employeebranch/' + str(apheader.raiserbranch)})
                    employee_data = ap_get_api_caller(request,{"api_url": '/usrserv/employee/' + str(apheader.created_by)})
                    aptype_data = ap_get_api_caller(request,{"api_url": '/ecfserv/get_ecftype_single/' + str(apheader.aptype)})

                    apinwardind_resp = APInvoiceheaderresponse()
                    apinwardind_resp.set_id(apinwrdinvhdr.id)
                    apinwardind_resp.set_invoicehdr_crno(apinwrdinvhdr.apinvoiceheader_crno)
                    apinwardind_resp.apheader_id=(apheader.id)
                    apinwardind_resp.set_crno(apheader.crno)
                    apinwardind_resp.set_inwarddetails_id(apheader.inwarddetails_id)
                    apinwardind_resp.set_invoicetype(aptype_data)
                    apinwardind_resp.set_supplier(supplier_data)
                    apinwardind_resp.set_invoice_no(apinwrdinvhdr.invoiceno)
                    apinwardind_resp.set_invoice_date(apinwrdinvhdr.invoicedate)
                    apinwardind_resp.set_branch(branch_data)
                    apinwardind_resp.set_invoice_amount(apheader.apamount)
                    #apinwardind_resp.set_rmubarcode(None)
                    apinwardind_resp.set_barcode(apinwrdinvhdr.barcode)
                    apinwardind_resp.set_remarks(apheader.remark)
                    apinwardind_resp.set_raiser_employeename(apheader.raisername)
                    apinwardind_resp.set_status(get_AP_status(apinwrdinvhdr.status))
                    apinwardind_resp.set_invoicehdr_crno(apinwrdinvhdr.apinvoiceheader_crno)
                    apinwardind_resp.set_createdby_data(employee_data)
                    resp_list.append(apinwardind_resp)
                vpage = NWisefinPaginator(apinwrdinvhdr_data, vys_page.get_index(), 10)
                resp_list.set_pagination(vpage)
            return resp_list

        except Exception  as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

    def apstatus_change(self,request,apinvoicehdr_data,emp_id):
        try:
            with transaction.atomic(using=self._current_app_schema()):
                from apservice.service.apheaderservice import APHeaderService
                aphdr_serv = APHeaderService(self._scope())
                remark=apinvoicehdr_data['remark']
                mail_response=""
                apinvoicehdr_update = APInvoiceHeader.objects.using(self._current_app_schema()).filter(id=apinvoicehdr_data['apinvoicehdr_id'],
                                                                                                      entity_id=self._entity_id())
                apinvoiceheader_data=apinvoicehdr_update[0]
                apinvoicehdr_update.update(status=apinvoicehdr_data['status_id'],
                    updated_date=now(),updated_by=emp_id)

                if int(apinvoicehdr_data['status_id']) == AP_Status.APPROVED:
                    #mail_response=self.mail_to_ecf_maker( request, emp_id, apinvoiceheader_data.apheader)
                    aphdr_serv.apheader_status_approve(apinvoiceheader_data.apheader_id, emp_id)
                    comment='MOVE TO APRROVED'
                #REJECTED
                if int(apinvoicehdr_data['status_id']) == AP_Status.REJECTED:
                    comment='MOVE TO REJECTED'
                    aphdr_serv.apheader_status_reject(apinvoiceheader_data.apheader_id, emp_id)
                    ecfstatus_update_json = {"api_url": '/ecfserv/apupdate', "crno": apinvoiceheader_data.apheader.crno,
                                             "ap_status": AP_Status.REJECTED_VAL}
                    ecfstatus_update_resp = ap_post_api_caller(request, ecfstatus_update_json)
                    logger.info('ecfstatus_update_resp ' + str(ecfstatus_update_resp))
                    print('ecfstatus_update_resp ', str(ecfstatus_update_resp))
                if int(apinvoicehdr_data['status_id']) == AP_Status.RE_AUDIT:
                    comment='MOVE TO RE-AUDIT'
                if int(apinvoicehdr_data['status_id']) == AP_Status.AP_INITIATE:
                    comment='MOVE TO AP-INITIATED'
                if int(apinvoicehdr_data['status_id']) == AP_Status.PAY_INITIATE:
                    comment='MOVE TO PAY-INITIATED'
                #BOUNCE
                if int(apinvoicehdr_data['status_id']) == AP_Status.BOUNCE:
                    bounce=APBounce.objects.using(self._current_app_schema()).create(
                        apinvoiceheader_id=apinvoicehdr_data['apinvoicehdr_id'],
                        invoicedate=apinvoicehdr_data['invoicedate'],
                        created_by=emp_id,
                        created_date=now(),entity_id=self._entity_id())
                    comment='MOVE TO BOUNCE'
                    ecfstatus_update_json = {"api_url": '/ecfserv/apupdate', "crno": apinvoiceheader_data.apheader.crno,
                                             "ap_status": AP_Status.BOUNCE_VAL}
                    ecfstatus_update_resp = ap_post_api_caller(request, ecfstatus_update_json)
                    logger.info('ecfstatus_update_resp ' + str(ecfstatus_update_resp))
                    print('ecfstatus_update_resp ', str(ecfstatus_update_resp))

                apqueue=APQueue.objects.using(self._current_app_schema()).create(ref_id=apinvoicehdr_data['apinvoicehdr_id'], ref_type=APRefType.APINVOICEHEADER,
                                                             from_user_id=emp_id,
                                                             to_user_id=emp_id,
                                                             comments=comment,
                                                             remarks=remark,
                                                             status=apinvoicehdr_data['status_id'],
                                                             is_sys=True,entity_id=self._entity_id())

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE + mail_response)
            return success_obj

        except Exception  as excep:
            traceback.print_exc()
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep)+" - "+ str(filename)+", line_no : "+str(line_number)+str(', exception_type : {c} '.format(c=type(excep).__name__)))
            return error_obj

    def maker_as_approver_validation(self,apinvoicehdr_id,emp_id):
        try:
            apqueue_data=self.apqueue_get(apinvoicehdr_id)
            if apqueue_data:
                user_id=int(apqueue_data.from_user_id)
                if int(user_id) == int(emp_id):
                    success_obj = NWisefinSuccess()
                    success_obj.set_status("Failed")
                    success_obj.set_message("You already play maker role in this AP")
                    return success_obj
            return False
        except Exception as excep:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            traceback.print_exc()
            success_obj = NWisefinSuccess()
            success_obj.set_status("Failed")
            success_obj.set_message(str(excep) + " - " + str(filename) + ", line_no: " + str(line_number) + str(', exception_type : {c} '.format(c=type(excep).__name__)))
            return success_obj


    def mail_to_ecf_maker(self,request,emp_id,aphdr_data):
        try:
            from environs import Env
            from utilityservice.service import api_service
            from django.template import loader
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            import smtplib
            env = Env()
            env.read_env()
            BASE_URL = env.str('WISEFIN_URL')
            From_url = env.str('SMTP_USER_NAME')
            PW_url = env.str('SMTP_KEY')
            api_serv = api_service.ApiService(self._scope())
            maker = api_serv.get_empsingle_id(request, aphdr_data.raisedby)
            maker_name = maker['name']
            maker_email_id = maker['email']
            approver = api_serv.get_empsingle_id(request, aphdr_data.raisedby)
            approver_name = approver['name']
            approver_email_id = approver['email']
            print("approver_email_id", approver_email_id)
            template = loader.get_template("ecfraiser.html")
            name = approver_name
            subject = "vendor payment request is approved by Checker"
            m_id = aphdr_data.id
            to = [approver_email_id]#{'saravanarajselvam0@gmail.com','saravanarajselvam0@gmail.com'}
            from1 = From_url
            msg = MIMEMultipart('alternative')
            referenceno = aphdr_data.crno
            raiseddate = aphdr_data.created_date
            amount = aphdr_data.apamount
            ecftype = aphdr_data.aptype
            data = {"emp_name": name,
                    "id": m_id,
                    "server_ip": BASE_URL,
                    "subject": subject,
                    "to": to,
                    "raisername": maker_name,
                    "approvername": approver_name,
                    "referenceno": referenceno,
                    "raiseddate": raiseddate,
                    "amount": amount,
                    "ecftype": ecftype
                    }

            body_html = template.render(data)
            part1 = MIMEText(body_html, "html")
            msg.attach(part1)
            msg['Subject'] = "vendor payment request is approved by Checker"
            TEXT = msg.as_string()
            server = smtplib.SMTP("smtp-mail.outlook.com", 587)
            server.starttls()
            server.ehlo()
            server.login(From_url, PW_url)
            server.sendmail(from1, to, TEXT)
            print("Successfully sent email " ,aphdr_data.crno)
            server.quit()
            logger.info("Successfully_sent_email  " + str(aphdr_data.crno))
            logger.info("ECF_mail_data:" + str(msg))
            return ", Mail Sent"
        except:
            print("sent_email_Failed ", aphdr_data.crno)
            logger.info("sent_email_Failed  " + str(aphdr_data.crno))
            traceback.print_exc()
            return ", Mail Not Sent"




    def apqueue_get(self,apinvoicehdr_id):
        apqueue = APQueue.objects.using(self._current_app_schema()).filter(ref_id=apinvoicehdr_id,
                             status=AP_Status.PENDING_FOR_APPROVAL,ref_type=APRefType.APINVOICEHEADER)
        ap_queue = None
        if len(apqueue) > 0:
            ap_queue=apqueue[0]
        return ap_queue


    def apdedupe_check(self,request,dedupe_type,apinvoicehdr_id,emp_id):
        try:
            #invoiceheader get query
            apinwrdinvhdr_data = APInvoiceHeader.objects.using(self._current_app_schema()).get(
                id=apinvoicehdr_id,is_delete=0,entity_id=self._entity_id())
            #exact match query
            if str(dedupe_type) == 'exact':
                apinwrdinvhdr = APInvoiceHeader.objects.using(self._current_app_schema()).filter(
                    invoiceno=apinwrdinvhdr_data.invoiceno,
                    invoicedate=apinwrdinvhdr_data.invoicedate,
                    invoiceamount=apinwrdinvhdr_data.invoiceamount,
                    supplier_id=apinwrdinvhdr_data.supplier_id,
                    #apheader__crno=apinwrdinvhdr_data.apheader.crno,
                    #apheader__raiserbranch=apinwrdinvhdr_data.apheader.raiserbranch,
                    #apheader__raisername=apinwrdinvhdr_data.apheader.raisername
                    is_delete=0,
                    entity_id=self._entity_id()).order_by('-id')
            #query without supplier ***
            if str(dedupe_type) == 'supplier':
                apinwrdinvhdr = APInvoiceHeader.objects.using(self._current_app_schema()).filter(
                    invoiceno=apinwrdinvhdr_data.invoiceno,
                    invoicedate=apinwrdinvhdr_data.invoicedate,
                    invoiceamount=apinwrdinvhdr_data.invoiceamount,
                    #apheader__crno=apinwrdinvhdr_data.apheader.crno,
                    #apheader__raiserbranch=apinwrdinvhdr_data.apheader.raiserbranch,
                    #apheader__raisername=apinwrdinvhdr_data.apheader.raisername,
                    is_delete=0,
                entity_id=self._entity_id()).order_by('-id')
            # query without invoice_amount ***
            if str(dedupe_type) == 'invoice_amount':
                apinwrdinvhdr = APInvoiceHeader.objects.using(self._current_app_schema()).filter(
                    invoiceno=apinwrdinvhdr_data.invoiceno,
                    invoicedate=apinwrdinvhdr_data.invoicedate,
                    supplier_id=apinwrdinvhdr_data.supplier_id,
                    #apheader__crno=apinwrdinvhdr_data.apheader.crno,
                    #apheader__raiserbranch=apinwrdinvhdr_data.apheader.raiserbranch,
                    #apheader__raisername=apinwrdinvhdr_data.apheader.raisername,
                    is_delete=0,
                entity_id=self._entity_id()).order_by('-id')
            # query without invoiceno ***
            if str(dedupe_type) == 'invoiceno':
                apinwrdinvhdr = APInvoiceHeader.objects.using(self._current_app_schema()).filter(
                    invoiceamount=apinwrdinvhdr_data.invoiceamount,
                    invoicedate=apinwrdinvhdr_data.invoicedate,
                    supplier_id=apinwrdinvhdr_data.supplier_id,
                    #apheader__crno=apinwrdinvhdr_data.apheader.crno,
                    #apheader__raiserbranch=apinwrdinvhdr_data.apheader.raiserbranch,
                    #apheader__raisername=apinwrdinvhdr_data.apheader.raisername,
                    is_delete=0,
                entity_id=self._entity_id()).order_by('-id')
            # query without invoice_date ***
            if str(dedupe_type) == 'invoice_date':
                apinwrdinvhdr = APInvoiceHeader.objects.using(self._current_app_schema()).filter(
                    invoiceno=apinwrdinvhdr_data.invoiceno,
                    invoiceamount=apinwrdinvhdr_data.invoiceamount,
                    supplier_id=apinwrdinvhdr_data.supplier_id,
                    #apheader__crno=apinwrdinvhdr_data.apheader.crno,
                    #apheader__raiserbranch=apinwrdinvhdr_data.apheader.raiserbranch,
                    #apheader__raisername=apinwrdinvhdr_data.apheader.raisername,
                    is_delete=0,
                entity_id=self._entity_id()).order_by('-id')

            resp_list = NWisefinList()
            if len(apinwrdinvhdr) > 1:
                i=0
                for data in apinwrdinvhdr:
                    if i==0:
                        i = i + 1
                        continue
                    supplier_data = ap_get_api_caller(request,{"api_url":'/venserv/get_supplier/' + str(data.supplier_id)})
                    branch_data = ap_get_api_caller(request,{"api_url": '/usrserv/employeebranch/' + str(data.apheader.raiserbranch)})
                    return_json={"id":data.id,"invoiceno":data.invoiceno,"invoiceamount":data.invoiceamount,
                                 "crno":data.apheader.crno,"raised_empname":data.apheader.raisername,
                                 "supplier":supplier_data,"branch":branch_data,"status":get_AP_status(data.status)}
                    resp_list.append(return_json)
            return resp_list

        except Exception  as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj


    def supplierpaymentacctno_val(self,request,filter_json,emp_id):
        try:
            supplierpayment=ap_get_api_caller(request, {"api_url":'/mstserv/supplierbranch_payment/'+
                                                              str(filter_json['supplier_id']) + '?supplier_accno=' + str(filter_json['supplier_accno'])})

            return json.dumps(supplierpayment)

        except Exception as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj.get()

    def fetch_preparepayment(self,request,filter_json,vys_page,emp_id):
        try:
            module_permission = ModulePermission(self._scope())
            role_arr = module_permission.employee_modulerole(emp_id, ModuleList.AP)
            print('role_arr', role_arr)
            AP_Payment_Maker = RoleList.AP_Payment_Maker
            if AP_Payment_Maker not in role_arr :
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description("You don't have 'AP Payment Maker' permission")
                return error_obj

            condition=Q(status__in=[AP_Status.APPROVED],is_delete=0,entity_id=self._entity_id())
            if 'crno' in filter_json:
                condition&=Q(apheader__crno__icontains=filter_json.get('crno'))
            if 'invoicetype_id' in filter_json:
                condition&=Q(apheader__aptype=filter_json.get('invoicetype_id'))
            if 'supplier_id' in filter_json:
                condition&=Q(supplier_id=filter_json.get('supplier_id'))
            if 'branch_id' in filter_json:
                condition&=Q(apheader__raiserbranch=filter_json.get('branch_id'))
            if 'raisername' in filter_json:
                condition&=Q(apheader__raisername__icontains=filter_json.get('raisername'))
            if 'invoice_no' in filter_json:
                condition&=Q(invoiceno__icontains=filter_json.get('invoice_no'))
            if 'invoice_amount' in filter_json:
                condition&=Q(apheader__apamount__icontains=filter_json.get('invoice_amount'))
            if 'invoice_from_date' in filter_json and 'invoice_to_date' in filter_json:
                inv_from_date = filter_json.get('invoice_from_date')
                inv_to_date =filter_json.get('invoice_to_date')
                condition&=Q(invoicedate__gte=inv_from_date,apinvoiceheader__invoicedate__lte=inv_to_date)


            apinwrdinvhdr_data = APInvoiceHeader.objects.using(self._current_app_schema()).filter(condition).order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]
            #paymentdetails_data = PaymentDetails.objects.using(self._current_app_schema()).filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
            resp_list = NWisefinList()
            if len(apinwrdinvhdr_data) > 0:
                for apinwrdinvhdr in apinwrdinvhdr_data:
                    apinvdtl_serv=APInvoiceDetailService(self._scope())
                    from apservice.service.apcreditservice import APCreditService
                    from utilityservice.service.ap_api_service import APApiService
                    ap_api_serv = APApiService(self._scope())
                    paymentdetails_data = PaymentDetails.objects.using(self._current_app_schema()).filter(apinvoiceheader_id=apinwrdinvhdr.id,
                                                                    is_delete=False,entity_id=self._entity_id())
                    ap_credit=APCreditService(self._scope())
                    emp_accntno_dtls=ap_credit.fetch_apcredit_account_dtls(request, apinwrdinvhdr.id, emp_id)
                    emp_accntno=None
                    apcredit_paymode_id=None
                    if emp_accntno_dtls:
                        emp_accntno=emp_accntno_dtls.creditrefno
                        apcredit_paymode_id=emp_accntno_dtls.paymode_id
                    emp_accntdtls=NWisefinList()
                    if emp_accntno:
                        print('crno ', apinwrdinvhdr.apheader.crno)
                        print('emp_accntno ', emp_accntno)
                        print('apinwrdinvhdr.apheader.raisedby ', apinwrdinvhdr.apheader.raisedby)
                        emp_accntdtls=ap_api_serv.fetch_apraiser_emp_accntdtls_using_accntno(request,emp_accntno, apinwrdinvhdr.apheader.raisedby)
                    #crdit_data=ap_credit.fetch_apcredit_list(request, apinwrdinvhdr.id, emp_id)
                    category_code="SUSPENSE"
                    crdit_data=ap_credit.fetch_apcredit_using_category_code(request,apinwrdinvhdr.id,category_code, emp_id)
                    print('paymode_id  apinwrdinvhdr.id   ' , apinwrdinvhdr.id)
                    print('json.loads(crdit_data.get())   ' , json.loads(crdit_data.get()))



                    supplierbranch_id = apinwrdinvhdr.supplier_id
                    supplierpayment_details = []
                    if supplierbranch_id and apcredit_paymode_id and emp_accntno:
                        supplierpayment_details = ap_api_serv.get_apcredit_supplierpayment(supplierbranch_id,
                                                                                           apcredit_paymode_id,
                                                                                           emp_accntno, emp_id)


                    # paymode=json.loads(crdit_data.get())
                    #
                    # if 'id' in paymode:
                    #     paymode_id=paymode['paymode_id']
                    #     paymode_data = ap_api_serv.paymode_single_get(paymode_id)
                    # else:
                    #     paymode_data=[]
                    apheader=apinwrdinvhdr.apheader
                    #supplier_data=ap_get_api_caller(request, {"api_url":'/venserv/get_supplier/'+str(apinwrdinvhdr.supplier_id)})
                    #branch_data=ap_get_api_caller(request, {"api_url":'/usrserv/get_empbranch/'+str(apheader.raiserbranch)})
                    #aptype_data = ap_get_api_caller(request, {"api_url": '/ecfserv/get_ecftype_single/' + str(apheader.aptype)})

                    apcredit_paymode = ap_api_serv.paymode_single_get(apcredit_paymode_id)
                    print('apcredit_paymode ', apcredit_paymode)
                    print('apcredit_paymode type', type(apcredit_paymode))


                    supplier_data = []
                    if apinwrdinvhdr.supplier_id != None and apinwrdinvhdr.supplier_id != "":
                        supplier_data = ap_api_serv.fetch_single_supplier_data(apinwrdinvhdr.supplier_id)
                    aptype_data = ap_api_serv.get_ap_ecftypesingle(apheader.aptype)

                    apinwardind_resp = APInvoiceheaderresponse()
                    apinwardind_resp.set_id(apinwrdinvhdr.id)
                    apinwardind_resp.credit_paymode=(apcredit_paymode)
                    apinwardind_resp.raiserbranch_id=(apinwrdinvhdr.apheader.raiserbranch)
                    apinwardind_resp.set_crno(apheader.crno)
                    apinwardind_resp.set_inwarddetails_id(apheader.inwarddetails_id)
                    apinwardind_resp.invoicedetails=(apinvdtl_serv.fetch_apinvoicedetails(request,apinwrdinvhdr.id))
                    apinwardind_resp.set_invoicetype(aptype_data)
                    apinwardind_resp.set_supplier(supplier_data)
                    apinwardind_resp.set_invoice_no(apinwrdinvhdr.invoiceno)
                    apinwardind_resp.set_invoice_date(apinwrdinvhdr.invoicedate)
                    apinwardind_resp.set_invoice_amount(apinwrdinvhdr.invoiceamount)
                    apinwardind_resp.set_apamount(apheader.apamount)
                    apinwardind_resp.set_remarks(apheader.remark)
                    apinwardind_resp.set_raiser_employeename(apheader.raisername)
                    apinwardind_resp.set_status(get_AP_status(apinwrdinvhdr.status))
                    apinwardind_resp.set_apcredit(crdit_data)
                    apinwardind_resp.set_invoicehdr_crno(apinwrdinvhdr.apinvoiceheader_crno)
                    apinwardind_resp.set_supplierpayment_details(supplierpayment_details)

                    from utilityservice.service.ap_api_service import APApiService
                    ap_api_serv = APApiService(self._scope())
                    empbranch_data = ap_api_serv.ap_employee_branch_single_get(apinwrdinvhdr.apheader.raiserbranch)
                    apinwardind_resp.raiserbranch = (empbranch_data)
                    #apinwardind_resp.set_apdebit(crdit_data)
                    #apinwardind_resp.paymode_data = (paymode_data)
                    print("len(paymentdetails_data) ",len(paymentdetails_data))
                    if len(paymentdetails_data) > 0:
                        paymentdetails_data=paymentdetails_data[0]
                        pvno=paymentdetails_data.paymentheader.pvno
                        paymentheader_date=str(paymentdetails_data.paymentheader.paymentheader_date)
                        paymentheader_amount=paymentdetails_data.paymentheader.paymentheader_amount
                        paymentdetails_amount=paymentdetails_data.paymentdetails_amount
                    else:
                        pvno = None
                        paymentheader_date = None
                        paymentheader_amount = None
                        paymentdetails_amount = None

                    apinwardind_resp.pvno = (pvno)
                    apinwardind_resp.paymentheader_date = (paymentheader_date)
                    apinwardind_resp.paymentheader_amount = (paymentheader_amount)
                    apinwardind_resp.paymendetails_amount = (paymentdetails_amount)

                    apinwardind_resp.set_employee_account_dtls(emp_accntdtls)
                    apinwardind_resp.set_pay_to(apheader.payto)

                    resp_list.append(apinwardind_resp)
                vpage = NWisefinPaginator(apinwrdinvhdr_data, vys_page.get_index(), 25)
                resp_list.set_pagination(vpage)
            return resp_list

        except Exception as excep:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep) +" - "+str(filename)+", line_no: "+str(line_number)+str(', exception_type : {c} '.format(c=type(excep).__name__)))
            return error_obj

    def fetch_paymentfile(self,request,filter_json,vys_page,emp_id):
        try:
            module_permission = ModulePermission(self._scope())
            role_arr = module_permission.employee_modulerole(emp_id, ModuleList.AP)
            print('role_arr', role_arr)
            AP_Payment_Maker = RoleList.AP_Payment_Maker
            if AP_Payment_Maker not in role_arr:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description("You don't have 'AP Payment Maker' permission")
                return error_obj

            condition=Q(is_delete=0, entity_id=self._entity_id())
            if 'pvno' in filter_json:
                condition&=Q(paymentheader__pvno__icontains=filter_json.get('pvno'))
            if 'bankdetails_id' in filter_json:
                condition&=Q(apinvoiceheader__bankdetails_id=filter_json.get('bankdetails_id'))
            if 'paymentheader_date' in filter_json :
                paymentheader_date =filter_json.get('paymentheader_date')
                condition&=Q(paymentheader__paymentheader_date=paymentheader_date)
            if 'status' in filter_json :
                            status =int(filter_json.get('status'))
                            condition&=Q(apinvoiceheader__status=status)
            else:
                condition&=Q(apinvoiceheader__status__in = [AP_Status.PAYMENT_INITIATE, AP_Status.FILE_INITIATE])


            #apinwrdinvhdr_data = APInvoiceHeader.objects.using(self._current_app_schema()).filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
            paymentdtls_data = PaymentDetails.objects.using(self._current_app_schema()).filter(condition).order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]
            #print('query',paymentdtls_data.query)
            resp_list = NWisefinList()
            if len(paymentdtls_data) > 0:
                for paymentdetails in paymentdtls_data:
                    apinwrdinvhdr=paymentdetails.apinvoiceheader
                    from apservice.service.apcreditservice import APCreditService
                    ap_credit=APCreditService(self._scope())
                    #crdit_data=ap_credit.single_get_apcredit(request, apinwrdinvhdr.id, emp_id)
                    credit_data=ap_credit.fetch_apcredit_list(request,apinwrdinvhdr.id, emp_id)
                    crdit_data = json.loads(credit_data.get())
                    print('paymode_id  apinwrdinvhdr.id    ' , apinwrdinvhdr.id)
                    print('crdit_data    ' ,crdit_data)
                    print('crdit_data    ' ,type(crdit_data))
                    print('bankdetails_id',apinwrdinvhdr.bankdetails_id)
                    #bankdetails = ap_get_api_caller(request,{"api_url": '/mstserv/bankdetails/' + str(apinwrdinvhdr.bankdetails_id)})
                    from utilityservice.service.ap_api_service import APApiService
                    ap_api_serv = APApiService(self._scope())
                    bankdetails = ap_api_serv.get_ap_bankdetails_master(apinwrdinvhdr.bankdetails_id, emp_id)
                    #print("bankdetails_response",bankdetails)

                    apheader=apinwrdinvhdr.apheader
                    #supplier_data=ap_get_api_caller(request, {"api_url":'/venserv/get_supplier/'+str(apinwrdinvhdr.supplier_id)})
                    supplier_data = ap_api_serv.fetch_single_supplier_data(apinwrdinvhdr.supplier_id)
                    apinwardind_resp = APInvoiceheaderresponse()
                    apinwardind_resp.set_id(apinwrdinvhdr.id)
                    apinwardind_resp.set_crno(apheader.crno)
                    apinwardind_resp.pvno = (paymentdetails.paymentheader.pvno)
                    apinwardind_resp.set_apcredit(crdit_data)
                    apinwardind_resp.set_supplier(supplier_data)
                    apinwardind_resp.debit_bankdetails=(bankdetails)
                    apinwardind_resp.utr_refno = (paymentdetails.paymentheader.callbackrefno)
                    apinwardind_resp.pv_date = str(paymentdetails.paymentheader.paymentheader_date)
                    apinwardind_resp.pv_amount = (paymentdetails.paymentheader.paymentheader_amount)
                    apinwardind_resp.set_raiser_employeename(apheader.raisername)
                    apinwardind_resp.set_status(get_AP_status(apinwrdinvhdr.status))
                    apinwardind_resp.set_invoicehdr_crno(apinwrdinvhdr.apinvoiceheader_crno)
                    apinwardind_resp.select_flag=False



                    resp_list.append(apinwardind_resp)
                vpage = NWisefinPaginator(paymentdtls_data, vys_page.get_index(), 25)
                resp_list.set_pagination(vpage)
            return resp_list
        except Exception  as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj



    def paymentdetails_download(self, request,ap_data, bankdetails_id, emp_id):
        try:
            with transaction.atomic(using=self._current_app_schema()):
                condition = Q(apinvoiceheader__status__in=[AP_Status.PAYMENT_INITIATE],is_delete=0,apinvoiceheader__is_delete=0,entity_id=self._entity_id(),
                              apinvoiceheader__bankdetails_id=bankdetails_id,paymentheader__pvno__in=ap_data.get('pvno_list'))

                paymentdtls_data = PaymentDetails.objects.using(self._current_app_schema()).filter(condition)
                print('paymentdtls_data_count ',len(paymentdtls_data))
                print('pvno_list' ,ap_data.get('pvno_list'))
                # serial_num_list=list()

                paymentdate_list=list()
                pvno_list=list()
                debit_accountno_list=list()
                ifsccode_list=list()
                pvamount_list=list()
                beneficiary_name_list=list()
                beneficiary_accountno_list=list()
                paymodetype_list=list()
                transaction_typecode_list=list()
                clientcode_list=list()
                # beneficary_accnt_type_list=list()
                # payable_location_list=list()
                # address_one_list=list()
                # address_two_list=list()
                # address_three_list=list()
                # address_four_list=list()
                #beneficary_id_list=list()
                transaction_currency_list = list()
                mode_of_delivery_list = list()
                beneficary_email_id_list = list()
                beneficary_mobile_no_list = list()
                purpose_code_list = list()
                #customer_refno_list = list()
                empty_data_list = list()
                return_json=dict()

                #serial_num=0
                if len(paymentdtls_data) > 0:
                    for paymentdetails in paymentdtls_data:
                        from apservice.service.apcreditservice import APCreditService
                        apinvoicehdr = paymentdetails.apinvoiceheader
                        apheader = paymentdetails.apinvoiceheader.apheader
                        paymentheader = paymentdetails.paymentheader
                        #FILE_INITIATE update and add Queue**
                        self.status_update_and_add_queue(apinvoicehdr.id,emp_id)
                        from utilityservice.service.ap_api_service import APApiService
                        ap_api_serv=APApiService(self._scope())
                        #clientcode_data=ap_api_serv.get_ap_clientcode(apinvoicehdr.apheader.client_code)
                        beneficary_email_id = ""
                        beneficary_mobile_no = ""
                        if str(apheader.payto) == "S":
                            supplierpayment_data=ap_api_serv.get_supplier_payment_details(request,emp_id,apinvoicehdr.supplier_id)
                            logger.info('supplierpayment_data - ' + str(supplierpayment_data))
                            supplieraddress_data = ap_api_serv.get_supplier_address(apinvoicehdr.supplier_id, emp_id)
                            #supplieraddr_tuple = self.get_ap_supplier_address(supplieraddress_data)
                            # address_one=supplieraddr_tuple[0]
                            # address_two=supplieraddr_tuple[1]
                            # address_three=supplieraddr_tuple[2]
                            # beneficary_pincode = ap_api_serv.get_supplier_pincode(apinvoicehdr.supplier_id, emp_id)
                            suppliercontact_data = ap_api_serv.get_supplier_contact(apinvoicehdr.supplier_id, emp_id)
                            supplier_mailid_and_mbl_no = self.get_supplier_mail_id_and_mobile_no(suppliercontact_data)
                            beneficary_email_id = supplier_mailid_and_mbl_no[0]
                            beneficary_mobile_no = supplier_mailid_and_mbl_no[1]
                            #supplierbranch_data = ap_api_serv.get_supplier_details(apinvoicehdr.supplier_id)
                            #beneficary_accnt_type=self.beneficiary_account_type(supplierpayment_data)
                            #beneficary_id=supplierbranch_data['code']
                            #logger.info('supplierbranch_data - ' + str(supplierbranch_data))

                        elif str(apheader.payto) == "E":
                            raisedby_emp_id = apheader.raisedby
                            #emp_accntdtls=ap_api_serv.fetch_apraiser_emp_accntdtls_using_accntno(request, emp_accountno, emp_id)
                            #beneficary_accnt_type ="saving"
                            # address_one = ""
                            # address_two = ""
                            # address_three = ""
                            # beneficary_pincode = ""
                            # beneficary_email_id = ""
                            # beneficary_mobile_no = ""
                            # beneficary_id = ""
                            #emp_address_contact_id=ap_api_serv.get_emp_address_contact_id(raisedby_emp_id)
                            #if 'address_id' in emp_address_contact_id:
                                #if emp_address_contact_id['address_id'] is not None and emp_address_contact_id['address_id'] !="":
                                   #emp_address=ap_api_serv.fetch_ecfraiser_emp_address(emp_address_contact_id['address_id'])
                                   # empaddr_tuple = self.get_ap_supplier_address(emp_address)
                                   # address_one = empaddr_tuple[0]
                                   # address_two = empaddr_tuple[1]
                                   # address_three = empaddr_tuple[2]
                                   # pincode_id=emp_address.get("pincode_id")
                                   # if pincode_id is not None and pincode_id !="":
                                   #     beneficary_pincode=ap_api_serv.get_emp_pincode(pincode_id,emp_id)


                            raiser_emp=ap_api_serv.get_single_emp_id(raisedby_emp_id)
                            if raiser_emp.get('email'):
                                beneficary_email_id=raiser_emp.get('email')
                            if raiser_emp.get('phone_no'):
                                beneficary_mobile_no = raiser_emp.get('phone_no')
                            # if raiser_emp.get('code'):
                            #     beneficary_id = raiser_emp.get('code')

                        bankdetails_data = ap_api_serv.get_ap_bankdetails_master(bankdetails_id, emp_id)
                        logger.info('bankdetails_data - ' + str(bankdetails_data))
                        #logger.info('beneficary_pincode - ' +  str(beneficary_pincode))
                        pvno_list.append(paymentdetails.paymentheader.pvno)
                        #beneficary_accnt_type_list.append("")
                        #beneficary_id_list.append(beneficary_id)
                        #pvno_list.append("")
                        paymentdate_list.append(str(paymentdetails.paymentheader.paymentheader_date.strftime("%d-%m-%Y")))
                        beneficiary_name_list.append(paymentheader.beneficiaryname)
                        ifsccode_list.append(paymentheader.IFSCcode)
                        beneficiary_accountno_list.append(paymentheader.accno)
                        debit_accountno_list.append(bankdetails_data['account_no'])

                        transaction_currency_list.append('INR')
                        pvamount_list.append(paymentdetails.paymentheader.paymentheader_amount)
                        clientcode_list.append("NACL")

                        mode_of_delivery_list.append(paymentheader.paymode)
                        transaction_typecode=self.get_transaction_typecode(bankdetails_data,paymentheader)
                        transaction_typecode_list.append(transaction_typecode)
                        paymode_type=self.get_paymodetype(paymentdetails,transaction_typecode)
                        purpose_code=self.get_purpose_code(paymode_type)
                        paymodetype_list.append(paymode_type)
                        purpose_code_list.append(purpose_code)
                        beneficary_email_id_list.append(beneficary_email_id)
                        beneficary_mobile_no_list.append(beneficary_mobile_no)
                        # payable_location_list.append('')
                        # address_one_list.append(address_one)
                        # address_two_list.append(address_two)
                        # address_three_list.append(address_three)
                        # address_four_list.append(beneficary_pincode)
                        #customer_refno_list.append("")
                        empty_data_list.append("")


                    #     serial_num=serial_num+1
                    #     serial_num_list.append(serial_num)
                    # return_json['S.NO']=serial_num_list
                    return_json['Client Code']=clientcode_list
                    return_json['Debit account no.'] = debit_accountno_list
                    return_json['Transaction type code']=transaction_typecode_list
                    return_json['Value Date'] = paymentdate_list
                    return_json['Amount'] = pvamount_list
                    return_json['Beneficiary Name']=beneficiary_name_list
                    return_json['Beneficary Accunt no.']=beneficiary_accountno_list
                    return_json['IFSC code']=ifsccode_list
                    return_json['Customer Ref no.']=pvno_list
                    return_json['Beneficary email id']=beneficary_email_id_list
                    return_json['Beneficiary mobile no.']=beneficary_mobile_no_list
                    return_json['Remarks']=empty_data_list
                    return_json['Payment Type']=paymodetype_list
                    return_json['Purpose code']=purpose_code_list
                    return_json['Bene a/c type']=empty_data_list
                    return_json['Payable Location'] = empty_data_list
                    return_json['Print branch name']=empty_data_list
                    return_json['Mode of delivery']=empty_data_list
                    return_json['Transaction currency']=transaction_currency_list
                    return_json['BENE_ADD1']=empty_data_list
                    return_json['BENE_ADD2']=empty_data_list
                    return_json['BENE_ADD3']=empty_data_list
                    return_json['BENE_ADD4']=empty_data_list
                    return_json['Beneficiary ID']=empty_data_list
                    return_json['Debit_Bank_Name']=bankdetails_data['bankbranch']['bank']['name']
            return return_json

        except Exception  as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj.get()


    def get_supplier_mail_id_and_mobile_no(self,suppliercontact_data):
        logger.info('suppliercontact_data')
        logger.info(suppliercontact_data)
        supplier_mail_id=''
        supplier_mobile_no=''
        if suppliercontact_data['email']:
            supplier_mail_id=suppliercontact_data['email']
        if suppliercontact_data['mobile']:
            supplier_mobile_no=suppliercontact_data['mobile']
        return supplier_mail_id,supplier_mobile_no


    def get_paymodetype(self,paymentdetails,transaction_typecode):
        paymodetype = "NEFT"
        if paymentdetails.paymentheader.paymentheader_amount > float(200000):
            paymodetype = "RTGS"
        if transaction_typecode == "BT":
            paymodetype = ""
        return paymodetype


    def get_purpose_code(self,paymodetype):
        purpose_code = ""
        if paymodetype == "NEFT":
            purpose_code="OTH"
        elif paymodetype == "RTGS":
            purpose_code = "CMS"
        return purpose_code



    def get_transaction_typecode(self,bankdetails_data,paymentheader):
        debit_bankname = bankdetails_data['bankbranch']['bank']['name']
        transaction_typecode = "LBT"
        if str(paymentheader.bankname) == str(debit_bankname):
            transaction_typecode = "BT"
        return transaction_typecode

    def status_update_and_add_queue(self,apinvoicehdr_id,emp_id):
        apinvhdr_update = APInvoiceHeader.objects.using(self._current_app_schema()).filter(
            id=apinvoicehdr_id).update(
            status=AP_Status.FILE_INITIATE, updated_by=emp_id, updated_date=now())
        queue_dict = {"ref_id": apinvoicehdr_id, "ref_type": APRefType.APINVOICEHEADER, "remarks": None,
                      "from_user_id": emp_id, "status": AP_Status.FILE_INITIATE,
                      "to_user_id": -1, "comments": "MOVE TO FILE INITIATED"}
        apserv = APService(self._scope())
        apserv.create_apqueue(queue_dict)

    def get_ap_supplier_address(self,supplieraddress_data):
        logger.info('supplieraddress_data')
        logger.info(supplieraddress_data)
        address_one = ''
        address_two = ''
        address_three = ''
        if supplieraddress_data['line1']:
            address_one = supplieraddress_data['line1']
        if supplieraddress_data['line2']:
            address_two = supplieraddress_data['line2']
        if supplieraddress_data['line3']:
            address_three = supplieraddress_data['line3']
        return address_one,address_two,address_three

    def beneficiary_account_type(self,supplierpayment_data):
        account_type = ''
        if 'data' in supplierpayment_data:
            if len(supplierpayment_data['data']) > 0:
                if supplierpayment_data['data'][0]['account_type']:
                    account_type = supplierpayment_data['data'][0]['account_type']
        return account_type

    def payment_excel_download(self, request,ap_data, bankdetails_id, emp_id):
        try:
                import pandas as pd
                from django.http import StreamingHttpResponse
                import io
                BytesIO = io.BytesIO()
                collection = self.paymentdetails_download(request,ap_data, bankdetails_id, emp_id)

                if type(collection) is type(str()):
                    error_obj = HttpResponse(collection, content_type='application/json')
                    return error_obj
                if type(collection) is type(dict()):
                    if len(collection) == 0:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.INVALID_DATA)
                        error_obj.set_description("Data Not Found")
                        error_obj = HttpResponse(error_obj.get(), content_type='application/json')
                        return error_obj
                Debit_Bank_Name = collection.get('Debit_Bank_Name')
                del collection['Debit_Bank_Name']
                print('collection ',collection)

                output = BytesIO
                df = pd.DataFrame(collection)
                writer = pd.ExcelWriter(output, engine='xlsxwriter')
                df.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.save()
                output.seek(0)
                print(datetime.now().strftime("%y%m%d_%H%M%S"))
                file_name = str(Debit_Bank_Name) + ' - (' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ').xlsx'
                response = StreamingHttpResponse(output, content_type='application/octet-stream')
                response['Content-Disposition'] = 'inline; filename="{}"'.format(file_name)
                return response

        except Exception as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return_error_obj = HttpResponse(error_obj.get(), content_type='application/json')
            return return_error_obj

    def paymentstatus_update(self,request,ap_data,emp_id):
        try:
            if ap_data is None:
                excel_data = pd.read_excel(request.FILES['file'])
                payment_list=excel_data.to_dict(orient='records')
                print('excel_data',type(excel_data.to_dict(orient='records')))
            else:
                payment_list=ap_data['paymentpvno_list']
            print('payment_list', payment_list)

            for pymt in payment_list:
                with transaction.atomic(using=self._current_app_schema()):
                    self.payment_update(request,pymt,emp_id)

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj

        except Exception as excep:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep)+ " - "+ str(filename)+", line_no: "+str(line_number)+str(', exception_type: {c} '.format(c=type(excep).__name__)))
            return error_obj

    #@transaction.atomic
    def payment_update(self,request,pymt,emp_id):
        from apservice.service.ppxdetailsservice import APppxDetailsService
        from apservice.service.paymentheaderservice import PreparePapmentService
        preparepaymnt_serv=PreparePapmentService(self._scope())
        ppxdtls_serv = APppxDetailsService(self._scope())

        paymentdtls_data = PaymentDetails.objects.using(self._current_app_schema()).filter(paymentheader__pvno=pymt['Customer Ref no.'],
                                                                        entity_id=self._entity_id())[0]
        aptype = paymentdtls_data.apinvoiceheader.apheader.aptype

        #Update UTR RefNo*
        utr_refno=None
        if 'UTR RefNo' in  pymt and int(aptype) == 2:
            utr_refno=pymt['UTR RefNo']

        preparepaymnt_serv.update_UTR_refno_using_pvno(pymt['Customer Ref no.'],utr_refno,emp_id)


        apinvhdr_update = APInvoiceHeader.objects.using(self._current_app_schema()).filter(
            id=paymentdtls_data.apinvoiceheader_id,entity_id=self._entity_id()).update(status=AP_Status.PAID,
                                                           updated_by=emp_id,
                                                           updated_date=now())
        print('apinvhdr_update ',apinvhdr_update)
        print('AP_Status.PAID , emp_id',AP_Status.PAID,emp_id)
        #ap status update in ECF
        ecfstatus_update_json = {"api_url": '/ecfserv/apupdate', "crno": paymentdtls_data.apinvoiceheader.apheader.crno,
                                 "ap_status": AP_Status.PAID_VAL}
        ecfstatus_update_resp = ap_post_api_caller(request, ecfstatus_update_json)
        logger.info('ecfstatus_update_resp ' + str(ecfstatus_update_resp))
        print('ecfstatus_update_resp ', str(ecfstatus_update_resp))

        apqueue = APQueue.objects.using(self._current_app_schema()).create(ref_id=paymentdtls_data.apinvoiceheader_id,
                                                               ref_type=APRefType.APINVOICEHEADER,
                                                               from_user_id=emp_id,
                                                               to_user_id=emp_id,
                                                               created_date=now(),
                                                               comments='MOVE TO PAID',
                                                               remarks=pymt['Customer Ref no.'],
                                                               status=AP_Status.PAID,
                                                               is_sys=True,entity_id=self._entity_id())

        aptype=paymentdtls_data.apinvoiceheader.apheader.aptype
        crno = paymentdtls_data.apinvoiceheader.apheader.crno
        print('aptype ',aptype)
        # Advance Entry Here
        if int(aptype) == 4: #ADVANCE Creation
            self.craete_ppxheader(request,paymentdtls_data,emp_id)
        if int(aptype) == 2 or int(aptype) == 3: #3-->ERA Liquedation : #2-->NON_PO Liquedation
            ppxdtls_serv.ppxdetails_liquedation_update(crno,emp_id)


        return None


    def craete_ppxheader(self,request,paymentdtls_data,emp_id):
        from apservice.service.ppxheaderservice import APppxHeaderService
        from apservice.data.request.apheaderrequest import APppxHeaderRequest
        paymentheader_amount = paymentdtls_data.paymentheader.paymentheader_amount
        crno = paymentdtls_data.apinvoiceheader.apheader.crno
        ap_data = {'apinvoiceheader_id': paymentdtls_data.apinvoiceheader_id, 'crno': crno,
                   'ppxheader_amount': paymentheader_amount, 'ppxheader_balance': paymentheader_amount}
        ap_ppxhdr_serv = APppxHeaderService(self._scope())
        ap_obj = APppxHeaderRequest(ap_data)
        response_obj = ap_ppxhdr_serv.create_ap_ppxheader(request, ap_obj, emp_id)





    def get_bounce(self, request,filter_obj,vys_page,type, emp_id):
        try:
            
            if type=='reject':
                condition = Q(status=AP_Status.REJECTED,is_delete=0,entity_id=self._entity_id())
            else:
                condition = Q(status=AP_Status.BOUNCE,is_delete=0,entity_id=self._entity_id())

            if 'crno' in filter_obj:
                condition = Q(apheader_id__crno__icontains=filter_obj['crno'])
            if 'invoicetype' in filter_obj:
                condition &= Q(apheader_id__aptype=filter_obj['invoicetype'])
            if 'branch_id' in filter_obj:
                condition &= Q(apheader__raiserbranch=filter_obj['branch_id'])
            if 'supplier_id' in filter_obj:
                condition &= Q(supplier_id=filter_obj['supplier_id'])
            if 'invoiceno' in filter_obj:
                condition &= Q(invoiceno__icontains=filter_obj['invoiceno'])
            if 'invoiceamount' in filter_obj:
                condition &= Q(invoiceamount__icontains=filter_obj['invoiceamount'])
            if 'update_fromdate' in filter_obj and 'update_todate' in filter_obj:
                condition &= Q(updated_date__range=[filter_obj['update_fromdate'],filter_obj['update_todate']])



            apinvhdr_data = APInvoiceHeader.objects.using(self._current_app_schema()).filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]

            resp_list = NWisefinList()
            if len(apinvhdr_data) > 0:
                for apinvhd in apinvhdr_data:
                    aphdr_data=apinvhd.apheader
                    from apservice.data.response.apheaderresponse import APHeaderResponse
                    from apservice.service.apheaderservice import APHeaderService
                    aphdr_resp = APHeaderResponse()
                    aphdr_serv=APHeaderService(self._scope())

                    aphdr_serv.fetch_apheader_list_lite(request, aphdr_resp, aphdr_data, emp_id)
                    aphdr_resp.set_apinvheader(self.fetch_apinvhdr_using_aphdr_lite(request, aphdr_data.id, emp_id))
                    resp_list.append(aphdr_resp)

                vpage = NWisefinPaginator(apinvhdr_data, vys_page.get_index(), 10)
                resp_list.set_pagination(vpage)

            return resp_list
        except Exception as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

    def single_get_bounce(self, request,apinvheader_id,   emp_id):
        try:
            condition = Q(id=apinvheader_id, is_delete=0, entity_id=self._entity_id())
            apinvhdr_data = APInvoiceHeader.objects.using(self._current_app_schema()).filter(condition)

            resp_list = NWisefinList()
            if len(apinvhdr_data) > 0:
                for apinvhd in apinvhdr_data:
                    aphdr_data = apinvhd.apheader
                    from apservice.data.response.apheaderresponse import APHeaderResponse
                    from apservice.service.apheaderservice import APHeaderService
                    aphdr_resp = APHeaderResponse()
                    aphdr_serv = APHeaderService(self._scope())

                    aphdr_serv.fetch_apheader_list_lite(request, aphdr_resp, aphdr_data, emp_id)
                    aphdr_resp.set_apinvheader(self.fetch_apinvhdr_using_aphdr_lite(request, aphdr_data.id, emp_id))
                    resp_list.append(aphdr_resp)

            return resp_list
        except Exception as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

    def fetch_apinvhdr_using_aphdr_lite(self,request,aphdr_id,emp_id):
            apinvhdr_data = APInvoiceHeader.objects.using(self._current_app_schema()).filter(apheader_id=aphdr_id,
                                                                                             is_delete=0,
                                                                                            entity_id=self._entity_id())
            apinvhdr_list = []
            if len(apinvhdr_data) > 0:
                for apinvhdr in apinvhdr_data:
                    # apinvdtl_serv = APInvoiceDetailService(self._scope())
                    # apdebt_serv=APDebitService(self._scope())
                    # apcredit_serv=APCreditService(self._scope())
                    inhdr_data = APInvoiceheaderresponse()
                    supplier_data = ap_get_api_caller(request,{"api_url":'/venserv/get_supplier/'+str(apinvhdr.supplier_id)})

                    inhdr_data.set_id(apinvhdr.id)
                    inhdr_data.set_apheader(apinvhdr.apheader_id)
                    inhdr_data.set_invoiceno(apinvhdr.invoiceno)
                    inhdr_data.set_dedupinvoiceno(apinvhdr.dedupinvoiceno)
                    inhdr_data.set_invoicedate(apinvhdr.invoicedate)
                    inhdr_data.set_suppliergst(apinvhdr.suppliergst)
                    inhdr_data.set_raisorbranchgst(apinvhdr.raisorbranchgst)
                    inhdr_data.set_invoiceamount(apinvhdr.invoiceamount)
                    inhdr_data.set_taxamount(apinvhdr.taxamount)
                    inhdr_data.set_totalamount(apinvhdr.totalamount)
                    inhdr_data.set_otheramount(apinvhdr.otheramount)
                    inhdr_data.set_roundoffamt(apinvhdr.roundoffamt)
                    inhdr_data.set_invoicegst(apinvhdr.invoicegst)
                    inhdr_data.set_entry_flag(self.invhdr_boolean_conver_to_number(apinvhdr.entry_flag))
                    inhdr_data.set_gsttype(self.get_gst_type(request,apinvhdr,emp_id))
                    inhdr_data.set_supplier(supplier_data)
                    inhdr_data.set_status(get_AP_status(apinvhdr.status))
                    inhdr_data.set_invoicehdr_crno(apinvhdr.apinvoiceheader_crno)
                    if apinvhdr.updated_date is None:
                        inhdr_data.set_updated_date(apinvhdr.updated_date)
                    else:
                        inhdr_data.set_updated_date(str(apinvhdr.updated_date.date()))
                    #inhdr_data.set_apinvoicedetails(apinvdtl_serv.fetch_apinvdtl_using_apinvhdr(request, apinvhdr.id))
                    # inhdr_data.set_apdebit(apdebt_serv.fetch_apdebit_using_apinvoicehdr(request,apinvhdr.id))
                    # inhdr_data.set_apcredit(apcredit_serv.fetch_apcredit_using_invoiceheader(request, apinvhdr.id))


                    apinvhdr_list.append(json.loads(inhdr_data.get()))
            return apinvhdr_list


    def fetch_supplier_report(self,request,supplier_id,apinvheader_id,subtax_id,emp_id):
        try:
            from django.db.models import Sum
            #from django.db.models.aggregates import Count
            condition=Q(status__in=[AP_Status.APPROVED,AP_Status.AP_INITIATE,AP_Status.PAY_INITIATE,AP_Status.FILE_INITIATE,AP_Status.PAID]
                        ,is_delete=0,supplier_id=supplier_id,entity_id=self._entity_id())
            apinwrdinvhdr_data = APInvoiceHeader.objects.using(self._current_app_schema()).filter(condition
                                ).values("supplier_id","updated_date__year").annotate(Sum("invoiceamount"),Sum("totalamount"))

            print('apinwrdinvhdr_data ')
            print('apinvheader_id ', apinvheader_id)
            print(apinwrdinvhdr_data)
            print(apinwrdinvhdr_data.query)
            resp_list = NWisefinList()
            #return resp_list
            print('len(apinwrdinvhdr_data)',len(apinwrdinvhdr_data))
            if len(apinwrdinvhdr_data) > 0:
                for apinwrdinvhdr in apinwrdinvhdr_data:
                    apinwardind_resp = APInvoiceheaderresponse()
                    invhdr_conditions = Q(id=apinvheader_id, is_delete=0,entity_id=self._entity_id(),)
                    apinvhdr_data = APInvoiceHeader.objects.using(self._current_app_schema()).filter(invhdr_conditions).order_by("-id")[0]
                    invoice_date=apinvhdr_data.invoicedate
                    invoiceamount=apinvhdr_data.invoiceamount
                    print('invoice_date ',invoice_date)
                    print('invoiceamount ',invoiceamount)

                    supplier_data=ap_get_api_caller(request, {"api_url":'/venserv/get_supplier/'+str(apinwrdinvhdr.get("supplier_id"))} )
                    print('supplier_data ', supplier_data)

                    if 'vendor_id' in supplier_data:
                        vendor_id=supplier_data['vendor_id']
                    #vendor_data = ap_get_api_caller(request, {"api_url": '/venserv/branch/'+str(vendor_id)+'/suppliertax' })
                    from utilityservice.service.ap_api_service import APApiService
                    print('vendor_id ',vendor_id)
                    ap_api_serv = APApiService(self._scope())
                    vendor_data = ap_api_serv.fetch_suppliertax_list_using_subtax_id(vendor_id,subtax_id)
                    print('vendor_data')
                    print(vendor_data)
                    excemthrosold = None
                    isexcempted = None
                    excemfrom = None
                    excemto = None
                    is_throsold = False
                    current_exide_amt = None
                    current_limit_amt = None

                    if len(vendor_data['data']) > 0:
                        is_throsold = False
                        for throsold_data in vendor_data['data']:
                            isexcempted=throsold_data['isexcempted']
                            if isexcempted in ['Y','y']:
                                print("excemthrosold",excemthrosold)
                                is_throsold = False
                                excemthrosold = throsold_data['excemthrosold']
                                excemfrom = pd.to_datetime(throsold_data['excemfrom']).date()
                                excemto = pd.to_datetime(throsold_data['excemto']).date()

                                current_total_invamt=float(apinwrdinvhdr.get("invoiceamount__sum")) #+ float(invoiceamount)
                                print("excemfrom , invoice_date , excemto",excemfrom , invoice_date , excemto)
                                print("excemfrom , invoice_date , excemto check", not excemfrom <= invoice_date <= excemto)
                                print("current_total_invamt ", current_total_invamt)
                                print("excemthrosold ", excemthrosold)
                                print("excemthrosold_amt_check ",  float(current_total_invamt) >= float(excemthrosold))

                                if not excemfrom <= invoice_date <= excemto or float(current_total_invamt) >= float(excemthrosold):
                                        is_throsold = True
                                        print('is_throsold', is_throsold)
                                        print('current_exide_amt', float(apinwrdinvhdr.get("invoiceamount__sum"))  > float(excemthrosold))

                                else:
                                    print( 'current_total_invamt ',float(current_total_invamt) ,' excemthrosold ', float(excemthrosold))
                                    current_tot_invamt = float(apinwrdinvhdr.get("invoiceamount__sum"))   + float(invoiceamount)
                                    print('current_tot_invamt ', float(current_tot_invamt))
                                    if float(current_tot_invamt) > float(excemthrosold):
                                        current_exide_amt =  float(current_tot_invamt) - float(excemthrosold)
                                        if float(invoiceamount) > float(current_exide_amt):
                                            current_limit_amt = float(invoiceamount) - float(current_exide_amt)
                                        else:
                                            current_limit_amt = float(current_exide_amt) - float(invoiceamount)

                                excemfrom = str(excemfrom)
                                excemto = str(excemto)

                    #apinwardind_resp.set_id(apinwrdinvhdr.id)
                    # apinwardind_resp.set_invoicehdr_crno(apinwrdinvhdr.apheader.crno)
                    apinwardind_resp.current_tds_applicable_amt=(current_limit_amt)
                    apinwardind_resp.current_exide_amt = (current_exide_amt)
                    apinwardind_resp.invoiceamount=str(invoiceamount)
                    apinwardind_resp.paid_invoiceamount=(apinwrdinvhdr.get("invoiceamount__sum"))
                    apinwardind_resp.to_be_paid_invoiceamount=(float(apinwrdinvhdr.get("invoiceamount__sum"))+ float(invoiceamount))
                    apinwardind_resp.paid_totalamount=(apinwrdinvhdr.get("totalamount__sum"))
                    apinwardind_resp.set_supplier(supplier_data)
                    apinwardind_resp.vendor_data=(vendor_data)

                    apinwardind_resp.year = (apinwrdinvhdr.get("updated_date__year"))
                    apinwardind_resp.is_throsold = (is_throsold)
                    apinwardind_resp.invoice_date = str(invoice_date)
                    apinwardind_resp.excemthrosold_amt = (excemthrosold)
                    apinwardind_resp.isexcempted = (isexcempted)
                    apinwardind_resp.excemfrom = (excemfrom)
                    apinwardind_resp.excemto = (excemto)
                    resp_list.append(apinwardind_resp)
            else:
                supplier_new_transaction=self.supplier_new_transaction(request,apinvheader_id,subtax_id,supplier_id)
                print('supplier_new_transaction ', supplier_new_transaction)
                resp_list.append(supplier_new_transaction)
            return resp_list

        except Exception as excep:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep)+" - "+str(filename)+", line_no: "+str(line_number)+str(', exception_type : {c} '.format(c=type(excep).__name__)))
            return error_obj

    def supplier_new_transaction(self,request,apinvheader_id,subtax_id,supplier_id):
        apinwardind_resp = APInvoiceheaderresponse()
        invhdr_conditions = Q(id=apinvheader_id, is_delete=0, entity_id=self._entity_id())
        apinvhdr_data = APInvoiceHeader.objects.using(self._current_app_schema()).filter(invhdr_conditions).order_by("-id")[0]
        invoice_date = apinvhdr_data.invoicedate
        invoiceamount = apinvhdr_data.invoiceamount
        print('invoice_date ', invoice_date)
        print('invoiceamount ', invoiceamount)

        supplier_data = ap_get_api_caller(request,{"api_url":'/venserv/get_supplier/' + str(supplier_id)})
        print('supplier_data ', supplier_data)

        if 'vendor_id' in supplier_data:
            vendor_id = supplier_data['vendor_id']
        # vendor_data = ap_get_api_caller(request, {"api_url": '/venserv/branch/'+str(vendor_id)+'/suppliertax' })
        from utilityservice.service.ap_api_service import APApiService
        print('vendor_id ', vendor_id)
        ap_api_serv = APApiService(self._scope())
        vendor_data = ap_api_serv.fetch_suppliertax_list_using_subtax_id(vendor_id, subtax_id)
        print('vendor_data')
        print(vendor_data)
        excemthrosold = None
        isexcempted = None
        excemfrom = None
        excemto = None
        is_throsold = False
        current_exide_amt = None
        current_limit_amt = None

        if len(vendor_data['data']) > 0:
            is_throsold = False
            for throsold_data in vendor_data['data']:
                isexcempted = throsold_data['isexcempted']
                if isexcempted in ['Y', 'y']:
                    print("excemthrosold", excemthrosold)
                    is_throsold = False
                    excemthrosold = throsold_data['excemthrosold']
                    excemfrom = pd.to_datetime(throsold_data['excemfrom']).date()
                    excemto = pd.to_datetime(throsold_data['excemto']).date()

                    print('excemfrom ', excemfrom, invoice_date, excemto)
                    print('main sub validation2 ', not excemfrom <= invoice_date <= excemto)

                    #current_total_invamt is current invoice amt
                    current_total_invamt = float(invoiceamount)
                    print('current_total_invamt ', float(current_total_invamt) , float(excemthrosold))
                    print('current_total_invamt_val ', float(current_total_invamt) >= float(excemthrosold))
                    if float(current_total_invamt) >= float(excemthrosold) or not excemfrom <= invoice_date <= excemto:
                    #if not excemfrom <= invoice_date <= excemto :
                        is_throsold = True
                        print('is_throsold ', is_throsold)


                    print('main validation ', float(current_total_invamt) >= float(excemthrosold))
                    print('current_total_invamt', current_total_invamt)
                    #current_exide_amt = float(excemthrosold)- current_total_invamt

                    current_limit_amt = None
                    current_exide_amt = None
                    if float(current_total_invamt) > float(excemthrosold) :
                        current_exide_amt = float(current_total_invamt) -  float(excemthrosold)
                        current_limit_amt = float(current_total_invamt) - float(current_exide_amt)
                    #else:
                        #current_exide_amt = float(current_total_invamt) - float(excemthrosold)


                    # if float(invoiceamount) > float(current_exide_amt):
                    #     current_limit_amt = float(invoiceamount) - float(current_exide_amt)
                    # else:
                    #     current_limit_amt = float(current_exide_amt) - float(invoiceamount)

                    excemfrom = str(excemfrom)
                    excemto = str(excemto)

        # apinwardind_resp.set_id(apinwrdinvhdr.id)
        # apinwardind_resp.set_invoicehdr_crno(apinwrdinvhdr.apheader.crno)
        apinwardind_resp.current_tds_applicable_amt = (current_limit_amt)
        apinwardind_resp.current_exide_amt = (current_exide_amt)
        apinwardind_resp.invoiceamount = str(invoiceamount)
        apinwardind_resp.paid_invoiceamount = 0
        apinwardind_resp.to_be_paid_invoiceamount =  float(invoiceamount)
        apinwardind_resp.paid_totalamount = 0
        apinwardind_resp.set_supplier(supplier_data)
        apinwardind_resp.vendor_data = (vendor_data)
        apinwardind_resp.year = (now().year)
        apinwardind_resp.is_throsold = (is_throsold)
        apinwardind_resp.invoice_date = str(invoice_date)
        apinwardind_resp.excemthrosold_amt = (excemthrosold)
        apinwardind_resp.isexcempted = (isexcempted)
        apinwardind_resp.excemfrom = (excemfrom)
        apinwardind_resp.excemto = (excemto)
        return  apinwardind_resp


    def apinvoicehdr_bankdetails_update(self,apinvhdr_id,bankdtls_id,emp_id):
        #try:
            condition=Q(is_delete=0,id=apinvhdr_id,entity_id=self._entity_id())
            apinvhdr = APInvoiceHeader.objects.using(self._current_app_schema()).get(condition)

            apinvhdr.bankdetails_id=bankdtls_id
            apinvhdr.updated_by=emp_id
            apinvhdr.updated_date=now()
            apinvhdr.save()


        # except Exception  as excep:
        #     traceback.print_exc()
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.INVALID_DATA)
        #     error_obj.set_description(str(excep))
        #     return error_obj

    def apinvhdr_crno_update(self,apinvhdr_id,apinvhdr_crno,emp_id):
        apinvhdr_update = APInvoiceHeader.objects.using(self._current_app_schema()).filter(
                                      id=apinvhdr_id,is_delete=False,entity_id=self._entity_id()).update(
                                                                      apinvoiceheader_crno=apinvhdr_crno)

    def fetch_ap_common_summary(self, request, filter_json, vys_page, emp_id):
        try:
            # condition=Q (status__in=[AP_Status.NEW,AP_Status.BOUNCE,AP_Status.RE_AUDIT,AP_Status.REJECTED],is_delete=0)
            scope = request.scope
            module_permission = ModulePermission(scope)
            resp_list = NWisefinList()
            role_arr = module_permission.employee_modulerole(emp_id, ModuleList.AP)
            print('role_arr', role_arr)
            AP_maker = RoleList.AP_Maker
            AP_approver = RoleList.AP_Approver
            AP_bounce_checker = RoleList.AP_Bounce_Checker
            if AP_maker in role_arr or AP_approver in role_arr or AP_bounce_checker in role_arr:
                pass
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description("You don't have any permission")
                return error_obj
            condition = Q(is_delete=0,entity_id=self._entity_id())

            print('status', filter_json.get('status'))
            print('status', type(filter_json.get('status')))

            if 'status' in  filter_json:
                if int(filter_json.get('status')) == dropdown_status.REVIEWED_BY_ME:
                    if AP_maker not in role_arr:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.INVALID_DATA)
                        error_obj.set_description("You don't have AP maker permission")
                        return error_obj
                    else:
                        condition &= Q(created_by=emp_id ,status__in=[AP_Status.NEW,AP_Status.PENDING_FOR_APPROVAL,AP_Status.BOUNCE,
                                                   AP_Status.RE_AUDIT,AP_Status.REJECTED,AP_Status.PAYMENT_INITIATE,
                                                   AP_Status.APPROVED,AP_Status.PAID,AP_Status.FILE_INITIATE,AP_Status.AP_INITIATE,AP_Status.PAY_INITIATE])
                        print('condition_review', condition)
                if int(filter_json.get('status')) == AP_Status.PENDING_FOR_APPROVAL:
                    if AP_approver not in role_arr:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.INVALID_DATA)
                        error_obj.set_description("You don't have AP approver permission")
                        return error_obj
                    else:
                        condition &= Q(status=AP_Status.PENDING_FOR_APPROVAL)

                elif int(filter_json.get('status')) == AP_Status.BOUNCE:
                    if AP_bounce_checker not in role_arr:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.INVALID_DATA)
                        error_obj.set_description("You don't have AP bounce checker permission")
                        return error_obj
                    else:
                        condition &= Q(status=AP_Status.BOUNCE)
                elif int(filter_json.get('status')) == dropdown_status.REJECTED_BY_ME:
                    if AP_maker not in role_arr:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.INVALID_DATA)
                        error_obj.set_description("You don't have AP maker permission")
                        return error_obj
                    else:
                        condition &= Q(status=dropdown_status.REJECTED_BY_ME)
                elif int(filter_json.get('status')) == dropdown_status.APPROVED_BY_ME:
                    if AP_approver not in role_arr:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.INVALID_DATA)
                        error_obj.set_description("You don't have AP approver permission")
                        return error_obj
                    else:
                        condition &= Q(status__in=[dropdown_status.APPROVED_BY_ME])
                elif int(filter_json.get('status')) == AP_Status.PAYMENT_INITIATE:
                        condition &= Q(status=AP_Status.PAYMENT_INITIATE)
                elif int(filter_json.get('status')) == AP_Status.FILE_INITIATE:
                        condition &= Q(status=AP_Status.FILE_INITIATE)
                elif int(filter_json.get('status')) == AP_Status.AP_INITIATE:
                        condition &= Q(status__in=[AP_Status.AP_INITIATE,AP_Status.PAY_INITIATE])

            else:
                condition &= Q(status__in=[AP_Status.NEW,AP_Status.PENDING_FOR_APPROVAL,AP_Status.BOUNCE,AP_Status.RE_AUDIT,
                                           AP_Status.REJECTED,AP_Status.PAYMENT_INITIATE,AP_Status.APPROVED,AP_Status.PAID,
                                           AP_Status.FILE_INITIATE,AP_Status.AP_INITIATE,AP_Status.PAY_INITIATE])



            if 'crno' in filter_json:
                condition &= Q(apheader__crno=filter_json.get('crno'))
            print('filter_jason', filter_json)
            if 'invoicetype_id' in filter_json:
                condition &= Q(apheader__aptype__in=filter_json.get('invoicetype_id'))
            if 'supplier_id' in filter_json:
                condition &= Q(supplier_id=filter_json.get('supplier_id'))
            if 'branch_id' in filter_json:
                condition &= Q(apheader__raiserbranch=filter_json.get('branch_id'))
            if 'raisername' in filter_json:
                condition &= Q(apheader__raisername__icontains=filter_json.get('raisername'))
            if 'invoice_no' in filter_json:
                condition &= Q(invoiceno__icontains=filter_json.get('invoice_no'))
            if 'invoice_amount' in filter_json:
                condition &= Q(apheader__apamount__icontains=filter_json.get('invoice_amount'))
            if 'invoice_from_date' in filter_json and 'invoice_to_date' in filter_json:
                inv_from_date = filter_json.get('invoice_from_date')
                inv_to_date = filter_json.get('invoice_to_date')
                condition &= Q(invoicedate__gte=inv_from_date, invoicedate__lte=inv_to_date)
            # if 'inward_from_date' in filter_json and 'inward_to_date' in filter_json:
            #     inward_from_date = datetime.strptime(filter_json.get('inward_from_date'), '%d-%m-%Y')
            #     inward_to_date = datetime.strptime(filter_json.get('inward_to_date'), '%d-%m-%Y')
            #     condition&=Q(invoice_date__gte=inward_from_date,invoice_date__lte=inward_to_date)
            print('condition', condition)

            apinwrdinvhdr_data = APInvoiceHeader.objects.using(self._current_app_schema()).filter(condition).order_by('-id')[
                                 vys_page.get_offset():vys_page.get_query_limit()]
            print('apinwrdinvhdr_data', apinwrdinvhdr_data)
            if len(apinwrdinvhdr_data) > 0:
                for apinwrdinvhdr in apinwrdinvhdr_data:
                    apheader = apinwrdinvhdr.apheader
                    from utilityservice.service.ap_api_service import APApiService
                    ap_api=APApiService(self._scope())
                    supplier_data =ap_api.get_supplierbranch_details(apinwrdinvhdr.supplier_id,emp_id)
                    branch_data = ap_api.ap_employee_branch_single_get(apheader.raiserbranch)
                    aptype_data = ap_api.get_ap_ecftypesingle(apheader.aptype)
                    print("aptypedata",aptype_data)
                    apinwardind_resp = APInvoiceheaderresponse()
                    apinwardind_resp.set_id(apinwrdinvhdr.id)
                    print("ap_invoice hdr id",apinwrdinvhdr.id)
                    apinwardind_resp.set_crno(apheader.crno)
                    print("ap_crno",apheader.crno)
                    print("aptype",apheader.aptype)
                    apinwardind_resp.apheader_id = (apheader.id)
                    apinwardind_resp.set_inwarddetails_id(apheader.inwarddetails_id)
                    apinwardind_resp.inwarddetails=(ap_api.fetch_inward_no_using_inwaddtls_id(request,apheader.inwarddetails_id))
                    apinwardind_resp.set_invoicetype(aptype_data)
                    apinwardind_resp.set_supplier(supplier_data)
                    apinwardind_resp.set_invoice_no(apinwrdinvhdr.invoiceno)
                    apinwardind_resp.set_invoice_date(apinwrdinvhdr.invoicedate)
                    apinwardind_resp.set_branch(branch_data)
                    apinwardind_resp.set_invoice_amount(apheader.apamount)
                    # apinwardind_resp.set_rmubarcode(None)
                    apinwardind_resp.set_barcode(apinwrdinvhdr.barcode)
                    apinwardind_resp.set_remarks(apheader.remark)
                    apinwardind_resp.set_raiser_employeename(apheader.raisername)
                    apinwardind_resp.set_status(get_AP_status(apinwrdinvhdr.status))
                    apinwardind_resp.set_invoicehdr_crno(apinwrdinvhdr.apinvoiceheader_crno)
                    resp_list.append(apinwardind_resp)
                vpage = NWisefinPaginator(apinwrdinvhdr_data, vys_page.get_index(), 10)
                resp_list.set_pagination(vpage)
            return resp_list

        except Exception as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

    def fetch_approved_crno(self, apcrno):
        apinvhdr_data = APInvoiceHeader.objects.using(self._current_app_schema()).filter(apheader__crno=apcrno,
                           status=AP_Status.APPROVED,is_delete=0,entity_id=self._entity_id())
        success_obj = NWisefinSuccess()
        if len(apinvhdr_data) > 0:
            success_obj.set_message("Found")
            return success_obj
        else:
            success_obj.set_message("Not Found")
            return success_obj

    def update_invoicehdr_adjsmt_amount(self,apinvoicehdr_id,otheramount,roundoffamt,emp_id):
        apinvhdr_update = APInvoiceHeader.objects.using(self._current_app_schema()).filter(id=apinvoicehdr_id,
                                                          entity_id=self._entity_id()).update(

            otheramount=otheramount,
            roundoffamt=roundoffamt,
            updated_by=emp_id,
            updated_date=now())


    def apstatus_update_validation(self,apinvoicehdr_id,Actual_apstatus):
        try:
            apinvhdr = APInvoiceHeader.objects.using(self._current_app_schema()).filter(
                id=apinvoicehdr_id,is_delete=False, entity_id=self._entity_id())[0]
            #if int(apinvhdr.status) != int(Actual_apstatus):
            print('apinvhdr ',apinvhdr.status)
            print('Actual_apstatus ',Actual_apstatus)
            if int(apinvhdr.status) not in Actual_apstatus:
                ap_status=get_AP_status(apinvhdr.status)
                apstatus_json = json.loads(ap_status.get())
                success_obj = NWisefinSuccess()
                success_obj.set_status("Failed")
                success_obj.set_message("This AP in '" + str(apstatus_json.get('text')) +  "' status")
                return success_obj
            else:
                return False

        except Exception as excep:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            traceback.print_exc()
            success_obj = NWisefinSuccess()
            success_obj.set_status("Failed")
            success_obj.set_message(str(excep) +" - "+str(filename)+", line_no: "+str(line_number)+str(', exception_type : {c} '.format(c=type(excep).__name__)))
            return success_obj

    def get_invoiceheader_status(self,apinvhdr_id):
            condition = Q(is_delete=0, id=apinvhdr_id, entity_id=self._entity_id())
            apinwrdinvhdr = APInvoiceHeader.objects.using(self._current_app_schema()).get(condition)
            apinvcestatus=get_AP_status(apinwrdinvhdr.status)
            return apinvcestatus

    def get_invoiceheader_status_using_crno(self,crno):
        try:
            print('crno ',crno)
            condition = Q(is_delete=0, apheader__crno=crno, entity_id=self._entity_id())
            apinwrdinvhdr = APInvoiceHeader.objects.using(self._current_app_schema()).get(condition)
            apinvcestatus=get_AP_status(apinwrdinvhdr.status)
            return apinvcestatus
        except Exception as excep:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            traceback.print_exc()
            success_obj = NWisefinSuccess()
            success_obj.set_status("Failed")
            success_obj.set_message(str(excep) + " - " + str(filename) + ", line_no: " + str(line_number) + str(
                ', exception_type : {c} '.format(c=type(excep).__name__)))
            return success_obj


    def invhdr_boolean_conver_to_number(self, boolean_value):
        if boolean_value == True:
            return 1
        else:
            return 0


    def get_supplierbranchcode_using_invoiceheader_id(self,invoiceheader_id):
            print('vendor type invoiceheader_id ', str(invoiceheader_id))
            logger.info('vendor type invoiceheader_id '+ str(invoiceheader_id))
            from utilityservice.service.ap_api_service import APApiService

            condition = Q(id=invoiceheader_id, entity_id=self._entity_id(),is_delete=0)
            apinwrdinvhdr = APInvoiceHeader.objects.using(self._current_app_schema()).get(condition)

            ap_serv=APApiService(self._scope())
            supplier_data=ap_serv.fetch_single_supplier_data(apinwrdinvhdr.supplier_id)
            supplier_code=supplier_data['code']

            return supplier_code
