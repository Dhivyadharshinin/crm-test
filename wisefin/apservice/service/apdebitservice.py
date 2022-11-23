import json
import sys
import traceback

from django.db import transaction

from apservice.data.response.apauditresponse import APAuditResponse
from apservice.data.response.apinvoicedetailresponse import APDebitResponse
from apservice.models import APDebit, APCCBSDetails
from apservice.service.apauditservice import APAuditService
from apservice.service.apinvoicedetailsservice import APInvoiceDetailService
from apservice.util.aputil import APModifyStatus, APRefType, ap_get_api_caller, ap_post_api_caller
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from django.utils.timezone import now

class APDebitService(NWisefinThread):
    def __init__(self, scope): 
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.AP_SERVICE)

        
    def apdebit_create(self,apdebit_obj,apinvhdr_id,apinvdtl_id,emp_id):

        if not apdebit_obj.get_id() is None:
            from apservice.service.apservice import APService
            apserv = APService(self._scope())
            vendor_type = apserv.get_vendor_type(apdebit_obj.get_debitglno())
            apdebit_update = APDebit.objects.using(self._current_app_schema()).filter(id=apdebit_obj.get_id(),entity_id=self._entity_id()).update(apinvoiceheader_id=apinvhdr_id,
                                                                   #apinvoicedetail_id=apinvdtl_id,
                                                                   vendor_type=vendor_type,
                                                                   category_code=apdebit_obj.get_category_code(),
                                                                   subcategory_code=apdebit_obj.get_subcategory_code(),
                                                                   debitglno=apdebit_obj.get_debitglno(),
                                                                   amount=apdebit_obj.get_amount(),
                                                                   deductionamount=apdebit_obj.get_deductionamount(),
                                                                   bsproduct=apdebit_obj.get_bsproduct_code(),
                                                                   updated_by=emp_id,
                                                                   updated_date=now())
            apdebit = APDebit.objects.using(self._current_app_schema()).get(id=apdebit_obj.get_id(),
                                                                            entity_id=self._entity_id())
            self.audit_function(apdebit, apdebit.id, apdebit.id, emp_id,
                                APModifyStatus.UPDATE,APRefType.APDEBIT)
        else:
            from apservice.service.apservice import APService
            apserv = APService(self._scope())
            vendor_type = apserv.get_vendor_type(apdebit_obj.get_debitglno())
            apdebit = APDebit.objects.using(self._current_app_schema()).create(apinvoiceheader_id=apinvhdr_id,
                                        apinvoicedetail_id = apinvdtl_id,
                                        vendor_type=vendor_type,
                                        category_code=apdebit_obj.get_category_code(),
                                        subcategory_code=apdebit_obj.get_subcategory_code(),
                                        debitglno = apdebit_obj.get_debitglno(),
                                        amount = apdebit_obj.get_amount(),
                                        deductionamount = apdebit_obj.get_deductionamount(),
                                        bsproduct = apdebit_obj.get_bsproduct_code(),
                                        created_by=emp_id,
                                        entity_id=self._entity_id())

            self.audit_function(apdebit, apdebit.id, apdebit.id, emp_id,
                                            APModifyStatus.CREATE, APRefType.APDEBIT)


        apdbt_data = APDebitResponse()
        apdbt_data.set_id(apdebit.id)
        apdbt_data.set_apinvoiceheader(apdebit.apinvoiceheader_id)
        apdbt_data.set_vendor_type(apdebit.vendor_type)
        apdbt_data.set_apinvoicedetail(apdebit.apinvoicedetail_id)
        apdbt_data.set_category_code(apdebit.category_code)
        apdbt_data.set_subcategory_code(apdebit.subcategory_code)
        apdbt_data.set_debitglno(apdebit.debitglno)
        apdbt_data.set_amount(apdebit.amount)
        apdbt_data.set_deductionamount(apdebit.deductionamount)
        apdbt_data.set_bsproduct_code(apdebit.bsproduct)
        return apdbt_data


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
        audit_obj.set_reftype(APRefType.APDEBIT)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(APRefType.APDEBIT)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)


    def fetch_apdebit_using_apinvoicehdr(self,request,apinvhdr_id):
        apdebit_data = APDebit.objects.using(self._current_app_schema()).filter(apinvoiceheader_id=apinvhdr_id,entity_id=self._entity_id()
                                                                                ,status=1,is_delete=0)
        apdebit_list = []
        if len(apdebit_data) > 0:
            for apdebit in apdebit_data:
                from utilityservice.service import api_service
                apinvdtl_serv = APInvoiceDetailService(self._scope())
                api_serv = api_service.ApiService(self._scope())
                cat = api_serv.get_cat_code(request, apdebit.category_code)
                #sub = api_serv.get_subcat_code(request, apdebit.subcategory_code)
                from utilityservice.service.ap_api_service import APApiService
                ap_api_serv = APApiService(self._scope())
                sub = ap_api_serv.get_apsubcategory_code(apdebit.category_code, apdebit.subcategory_code)
                apdebit_resp = APDebitResponse()
                apdebit_resp.set_id(apdebit.id)
                apdebit_resp.set_apinvoiceheader(apdebit.apinvoiceheader_id)
                apdebit_resp.set_vendor_type(apdebit.vendor_type)
                apdebit_resp.set_apinvoicedetail(apdebit.apinvoicedetail_id)
                apdebit_resp.set_category_code(cat)
                apdebit_resp.set_subcategory_code(sub)
                apdebit_resp.set_debitglno(apdebit.debitglno)
                apdebit_resp.set_amount(apdebit.amount)
                apdebit_resp.set_deductionamount(apdebit.deductionamount)
                apdebit_resp.set_ccbs(apinvdtl_serv.fetch_apdebit_ccbs(request,apdebit.id))
                apdebit_resp.set_bsproduct_code(api_serv.get_bscode(apdebit.bsproduct))
                apdebit_list.append(json.loads(apdebit_resp.get()))
        return apdebit_list

    def get_apdebit_using_apinvoicehdr_id(self,apinvoicehdr_id):
        apdebit_data = APDebit.objects.using(self._current_app_schema()).filter(apinvoiceheader_id=apinvoicehdr_id,
                                                                                entity_id=self._entity_id(),is_delete=0,status=1)[0]
        return apdebit_data


    def get_apdebit_list(self,request,apinvoicehdr_id,emp_id):
        apdebit_data = APDebit.objects.using(self._current_app_schema()).filter(apinvoiceheader_id=apinvoicehdr_id,
                                                                                entity_id=self._entity_id(),is_delete=0,status=1)
        apdebit_list = NWisefinList()
        if len(apdebit_data) > 0:
            for apdebit in apdebit_data:
                from utilityservice.service import api_service
                apinvdtl_serv = APInvoiceDetailService(self._scope())
                api_serv = api_service.ApiService(self._scope())
                cat = api_serv.get_cat_code(request, apdebit.category_code)
                #sub = api_serv.get_subcat_code(request, apdebit.subcategory_code)
                from utilityservice.service.ap_api_service import APApiService
                ap_api_serv = APApiService(self._scope())
                sub = ap_api_serv.get_apsubcategory_code(apdebit.category_code, apdebit.subcategory_code)
                apdebit_resp = APDebitResponse()
                apdebit_resp.set_id(apdebit.id)
                apdebit_resp.set_vendor_type(apdebit.vendor_type)
                apdebit_resp.set_apinvoiceheader(apdebit.apinvoiceheader_id)
                apdebit_resp.set_apinvoicedetail(apdebit.apinvoicedetail_id)
                apdebit_resp.set_category_code(cat)
                apdebit_resp.set_subcategory_code(sub)
                apdebit_resp.set_debitglno(apdebit.debitglno)
                apdebit_resp.set_amount(apdebit.amount)
                apdebit_resp.set_deductionamount(apdebit.deductionamount)
                apdebit_resp.set_ccbs(apinvdtl_serv.fetch_apdebit_ccbs(request,apdebit.id))
                apdebit_resp.set_bsproduct_code(api_serv.get_bscode(apdebit.bsproduct))
                apdebit_list.append(apdebit_resp)
        return apdebit_list


    def get_apdebit_invoicedetails_list(self,request,apinvdtls_id,emp_id):
        apdebit_data = APDebit.objects.using(self._current_app_schema()).filter(apinvoicedetail_id=apinvdtls_id,
                                                            entity_id=self._entity_id(),is_delete=0,status=1)
        apdebit_list = NWisefinList()
        if len(apdebit_data) > 0:
            for apdebit in apdebit_data:
                from utilityservice.service import api_service
                apinvdtl_serv = APInvoiceDetailService(self._scope())
                api_serv = api_service.ApiService(self._scope())
                from utilityservice.service.ap_api_service import APApiService
                ap_api_serv = APApiService(self._scope())
                cat = api_serv.get_cat_code(request, apdebit.category_code)
                #sub = api_serv.get_subcat_code(request, apdebit.subcategory_code)
                sub = ap_api_serv.get_apsubcategory_code(apdebit.category_code, apdebit.subcategory_code)
                apdebit_resp = APDebitResponse()
                apdebit_resp.set_id(apdebit.id)
                apdebit_resp.set_apinvoiceheader(apdebit.apinvoiceheader_id)
                apdebit_resp.set_vendor_type(apdebit.vendor_type)
                apdebit_resp.set_apinvoicedetail(apdebit.apinvoicedetail_id)
                apdebit_resp.set_category_code(cat)
                apdebit_resp.set_subcategory_code(sub)
                apdebit_resp.set_debitglno(apdebit.debitglno)
                if apdebit.debitglno in [0,"0",''," ",None]:
                    apdebit_resp.glno_description=(None)
                else:
                    apdebit_resp.glno_description=(ap_api_serv.get_glno_description(apdebit.debitglno))
                apdebit_resp.set_amount(apdebit.amount)
                apdebit_resp.set_deductionamount(apdebit.deductionamount)
                apdebit_resp.set_ccbs(apinvdtl_serv.fetch_apdebit_ccbs(request,apdebit.id))
                apdebit_resp.set_bsproduct_code(api_serv.get_bscode(apdebit.bsproduct))
                apdebit_list.append(apdebit_resp)
        return apdebit_list

    def get_apdebit_single(self,request,apdebit_id,emp_id):
        try:
            apdebit = APDebit.objects.using(self._current_app_schema()).get(id=apdebit_id,
                                                        entity_id=self._entity_id(),is_delete=0,status=1)
            from utilityservice.service import api_service
            apinvdtl_serv = APInvoiceDetailService(self._scope())
            api_serv = api_service.ApiService(self._scope())
            cat = api_serv.get_cat_code(request, apdebit.category_code)
            #sub = api_serv.get_subcat_code(request, apdebit.subcategory_code)
            from utilityservice.service.ap_api_service import APApiService
            ap_api_serv = APApiService(self._scope())
            sub = ap_api_serv.get_apsubcategory_code(apdebit.category_code, apdebit.subcategory_code)
            apdebit_resp = APDebitResponse()
            apdebit_resp.set_id(apdebit.id)
            apdebit_resp.set_apinvoiceheader(apdebit.apinvoiceheader_id)
            apdebit_resp.set_vendor_type(apdebit.vendor_type)
            apdebit_resp.set_apinvoicedetail(apdebit.apinvoicedetail_id)
            apdebit_resp.set_category_code(cat)
            apdebit_resp.set_subcategory_code(sub)
            apdebit_resp.set_debitglno(apdebit.debitglno)
            apdebit_resp.set_amount(apdebit.amount)
            apdebit_resp.set_deductionamount(apdebit.deductionamount)
            #print('apdebit.id  ',apdebit.id)
            apdebit_resp.set_ccbs(apinvdtl_serv.fetch_apdebit_ccbs(request,apdebit.id))
            apdebit_resp.set_bsproduct_code(api_serv.get_bscode(apdebit.bsproduct))

            return apdebit_resp
        except Exception as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

    def apdebit_delete_using_apinvoicedetail_id(self,apinvoicedetail_id,emp_id):
            apinvdtls_serv = APInvoiceDetailService(self._scope())
            apdebit_delete = APDebit.objects.using(self._current_app_schema()).filter(apinvoicedetail_id=apinvoicedetail_id,
                                                                        entity_id=self._entity_id(),is_delete=0).update(
                                                            is_delete=1,updated_by=emp_id,
                                                            updated_date=now())
            print('apdebit_delete ',apdebit_delete)
            ccbs_delete=apinvdtls_serv.ccbs_delete_using_apinvoicedetail_id(apinvoicedetail_id,emp_id)
            print('ccbs_delete ',ccbs_delete)
            return apdebit_delete

    def apdebit_delete(self,apdebit_id,emp_id):
        try:
            apinvdtls_serv = APInvoiceDetailService(self._scope())
            apdebit = APDebit.objects.using(self._current_app_schema()).filter(id=apdebit_id,
                                                                        entity_id=self._entity_id(),is_delete=0).update(
                                                            is_delete=1,updated_by=emp_id,
                                                            updated_date=now())

            ccbs_delete=apinvdtls_serv.ccbs_delete_using_apdebit_id(emp_id, apdebit_id)
            print('ccbs_delete_using_apdebit_id ',ccbs_delete)

            if apdebit == 0: 
                error_obj = NWisefinError()
                error_obj.set_code('INVALID_INVOICEDETAILS_ID')
                error_obj.set_description('INVALID INVOICEDETAILS ID')
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

    def get_product_isrcm_and_isblocked(self,request, apdebit_data,apinvdtls_serv):
        apinvoice_dtls=apinvdtls_serv.get_apinvoicedetails_single(request, apdebit_data['invoicedetails_id'])
        print('apinvoice_dtls   ',apinvoice_dtls)
        print('apinvoice_dtls 2  ',apinvoice_dtls.productcode_details)
        print('product_isrcm    ',apinvoice_dtls.productcode_details.get('product_isrcm'))
        print('product_isblocked    ',apinvoice_dtls.productcode_details.get('product_isblocked'))
        print('productcode_details -> '+str(apinvoice_dtls.productcode_details))
        if 'product_isrcm' not in apinvoice_dtls.productcode_details:
            success_obj = NWisefinSuccess()
            success_obj.set_status("Failed")
            success_obj.set_message("Please check Product Name in invoice details")
            return success_obj
        else:
            product_isrcm= apinvoice_dtls.productcode_details.get('product_isrcm')
            product_isblocked = apinvoice_dtls.productcode_details.get('product_isblocked')
            return product_isrcm,product_isblocked

    def ap_entry_debit(self,request,apdebit,entrytype,emp_id):
        try:
            with transaction.atomic(using=self._current_app_schema()):
                if entrytype == 'apcredit':
                    from apservice.service.apcreditservice import APCreditService
                    apcredit_serv=APCreditService(self._scope())
                    credit_is_rcm_isblocked=self.credit_is_rcm_and_isblocked_check(request,apdebit['invoiceheader_id'])
                    if type(credit_is_rcm_isblocked) != type(tuple()) :
                        return credit_is_rcm_isblocked
                    #*****----entry_apcredit-----****
                    entry_apcredit=apcredit_serv.entry_apcredit(request,apdebit,credit_is_rcm_isblocked,emp_id)
                    if entry_apcredit !=True:
                        return entry_apcredit
                else:
                    apdebit_data = APDebit.objects.using(self._current_app_schema()).filter(apinvoicedetail_id=apdebit['invoicedetails_id'],
                                                                                       entity_id=self._entity_id(),
                                                                                       is_delete=0)
                    apdebit_id=0
                    apinvoicedetail_id = apdebit['invoicedetails_id']
                    if len(apdebit_data) > 0:
                        apdebit_data=apdebit_data[0]
                        aptype_id = apdebit_data.apinvoiceheader.apheader.aptype
                        crno = apdebit_data.apinvoiceheader.apheader.crno
                        apinvoiceheader_id = apdebit_data.apinvoiceheader_id
                        apdebit_id=apdebit_data.id
                        #data prepare
                        category_code = apdebit_data.category_code
                        subcategory_code = apdebit_data.subcategory_code
                        debitglno = apdebit_data.debitglno
                        amount = apdebit_data.amount
                        deductionamount = apdebit_data.deductionamount
                        bsproduct_code_id = apdebit_data.bsproduct
                    else:
                        apinvdtls_serv=APInvoiceDetailService(self._scope())
                        fetch_apinvdtls_single=apinvdtls_serv.fetch_apinvoicedetails_single(apdebit['invoicedetails_id'])
                        aptype_id =fetch_apinvdtls_single.apinvoiceheader.apheader.aptype
                        crno =fetch_apinvdtls_single.apinvoiceheader.apheader.crno
                        apinvoiceheader_id =fetch_apinvdtls_single.apinvoiceheader_id
                        #data prepare
                        category_code = None
                        subcategory_code = None
                        debitglno = None
                        amount = 0
                        deductionamount = 0
                        bsproduct_code_id = None



                    apinvdtls_serv=APInvoiceDetailService(self._scope())
                    isrcm_and_isblocked=self.get_product_isrcm_and_isblocked(request, apdebit, apinvdtls_serv)
                    if type(isrcm_and_isblocked) == type(tuple()) :
                        product_isrcm = isrcm_and_isblocked[0]
                        product_isblocked = isrcm_and_isblocked[-1]
                    else:
                        return isrcm_and_isblocked

                    from utilityservice.service.ap_api_service import APApiService
                    ap_api_serv = APApiService(self._scope())
                    aptype_data = ap_api_serv.get_ap_ecftypesingle(aptype_id)
                    print('aptype_data -> ',aptype_data)
                    logger.info('aptype_data -> ',str(aptype_data))
                    module_name = aptype_data['text']

                    if str(module_name) != "ERA" and str(product_isrcm) == 'Y' :
                        module_name="NON PO RCM"
                    if int(aptype_data['id'])==4:
                        module_name = str(crno)[0:3]

                    # if str(product_isblocked) == 'Y':
                    #     module_name="NON PO BLOCKED"
                    logger.info('module_name ' + str(module_name))
                    print('module_name ',module_name)

                    entrydebit_data = ap_post_api_caller(request, {"api_url": '/entryserv/commonquerydata',
                                                   "crno":crno,
                                                    "invoiceheader_id":apinvoiceheader_id,
                                                    "invoicedetails_id":apinvoicedetail_id,"module_name":str(module_name) })
                    print('entrydebit_data', entrydebit_data)
                    print('entrydebit_data type', type(entrydebit_data))

                    if 'apdebit' not in entrydebit_data:
                        entrydebit_resp = json.loads(entrydebit_data)
                        logger.info('entrydebit_resp - '+str(entrydebit_resp))
                        success_obj = NWisefinSuccess()
                        success_obj.set_status("Failed")
                        success_obj.set_message("Please check entry template")
                        return success_obj


                    logger.info('entrydebit_data ' + str(entrydebit_data))
                    logger.info('apdebit'  + str(entrydebit_data['apdebit']))
                    print(entrydebit_data['apdebit'],entrydebit_data['apdebit'])
                    apdebit_del = APDebit.objects.using(self._current_app_schema()).filter(
                        apinvoicedetail_id=apinvoicedetail_id,
                        entity_id=self._entity_id(), is_delete=0).update(
                        is_delete=1, updated_by=emp_id,
                        updated_date=now())

                    for obj_deb in entrydebit_data['apdebit']:

                        if 'category_code' in obj_deb:
                            if obj_deb['category_code'] is not None and obj_deb['category_code']!='' and obj_deb['category_code']!='DYNAMIC':
                                if 'code' in obj_deb['category_code']:
                                    if obj_deb['category_code']['code'] is not None and obj_deb['category_code']['code']!='' and obj_deb['category_code']['code']!='DYNAMIC' :
                                        category_code=obj_deb['category_code']['code']
                        if 'subcategory_code' in obj_deb:
                            if obj_deb['subcategory_code'] is not None and obj_deb['subcategory_code'] != '' and obj_deb['subcategory_code'] != 'DYNAMIC':
                                if obj_deb['subcategory_code']['code'] is not None and obj_deb['subcategory_code']['code'] != ''and obj_deb['subcategory_code']['code'] != 'DYNAMIC':
                                    subcategory_code=obj_deb['subcategory_code']['code']
                        if 'debitglno' in obj_deb:
                            if obj_deb['debitglno'] is not None and obj_deb['debitglno'] != '' and obj_deb['debitglno'] != 'DYNAMIC':
                                debitglno=obj_deb['debitglno']
                        if 'amount' in obj_deb:
                            if obj_deb['amount'] is not None and obj_deb['amount'] != ''and obj_deb['amount'] != 'DYNAMIC':
                                amount=obj_deb['amount']
                        if 'deductionamount' in obj_deb:
                            if obj_deb['deductionamount'] is not None and obj_deb['deductionamount'] != '' and obj_deb['deductionamount'] != 'DYNAMIC':
                                deductionamount=obj_deb['deductionamount']

                        from apservice.service.apservice import APService
                        apserv = APService(self._scope())
                        vendor_type = apserv.get_vendor_type(debitglno)
                        apdebit_new = APDebit.objects.using(self._current_app_schema()).create(apinvoiceheader_id=apinvoiceheader_id,
                                                                                       apinvoicedetail_id=apinvoicedetail_id,
                                                                                       category_code=category_code,
                                                                                       vendor_type=vendor_type,
                                                                                       subcategory_code=subcategory_code,
                                                                                       debitglno=debitglno,
                                                                                       amount=amount,
                                                                                       deductionamount=deductionamount,
                                                                                       bsproduct=bsproduct_code_id,
                                                                                       created_by=emp_id,
                                                                                       is_entry=True,
                                                                                       entity_id=self._entity_id())
                        print('apdebit_id ',apdebit_id)
                        print('apdebit_new_id ',apdebit_new.id)
                        apinvdtl_serv = APInvoiceDetailService(self._scope())
                        # ap_ccbsdtls = APCCBSDetails.objects.using(self._current_app_schema()).filter(
                        #     apdebit_id=apdebit_id,entity_id=self._entity_id())

                        # if len(ap_ccbsdtls) > 0:
                        #     for apccbsdtls in ap_ccbsdtls:
                        #         apccbsdtls_update=apinvdtl_serv.direct_ccbs_create(apccbsdtls,apdebit_new,emp_id)
                        #         print('apccbsdtls_update ', apccbsdtls_update)
                        # apccbsdtls_update = APCCBSDetails.objects.using(self._current_app_schema()).filter(
                        #                                                            apdebit_id=apdebit.id,
                        #                                                            entity_id=self._entity_id()).update(
                        #                                                            apdebit_id=apdebit_new.id,
                        #                                                            updated_by=emp_id,
                        #                                                            updated_date=now())


                        self.audit_function(apdebit_new, apdebit_new.id, apdebit_new.id, emp_id,APModifyStatus.CREATE, APRefType.APDEBIT)
                    # apccbs = APCCBSDetails.objects.using(self._current_app_schema()).filter(apdebit_id=apdebit.id,
                    #                                                                           entity_id=self._entity_id())[0]



                    apccbs_update = APCCBSDetails.objects.using(self._current_app_schema()).filter(apdebit_id=apdebit_id,
                                                                                                 entity_id=self._entity_id()).update(
                                                                                                is_delete=1,
                                                                                            updated_by=emp_id,
                                                                                            updated_date=now())



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
            success_obj.set_status("Failed")
            success_obj.set_message(str(excep))
            success_obj.error_info=(str(filename)+",line_no : "+str(line_number)+str(', exception_type : {c} '.format(c=type(excep).__name__)))
            return success_obj

    def credit_is_rcm_and_isblocked_check(self,request,invoicehdr_id):
        apinvdtls_serv = APInvoiceDetailService(self._scope())
        apinvoicedtls=apinvdtls_serv.fetch_apinvoicedetails(request, invoicehdr_id)
        apinvoicedtls_json=json.loads(apinvoicedtls.get())

        product_isrcm='N'
        product_isblocked='N'
        if 'data' in apinvoicedtls_json :
            if len(apinvoicedtls_json['data']) > 0:
                for dtls in apinvoicedtls_json['data']:
                    apinvoice_dtls = apinvdtls_serv.get_apinvoicedetails_single(request, dtls['id'])
                    product_dict=  apinvoice_dtls.__dict__
                    print('product_dict ',product_dict)
                    print('product_dict ',product_dict['productcode_details'])
                    if 'productcode_details' not in  product_dict:
                        success_obj = NWisefinSuccess()
                        success_obj.set_status("Failed")
                        success_obj.set_message("Please check Product Name in invoice details")
                        return success_obj
                    else:
                        if 'product_isrcm' not in product_dict['productcode_details'] \
                        or 'product_isblocked' not in product_dict['productcode_details']:
                            success_obj = NWisefinSuccess()
                            success_obj.set_status("Failed")
                            success_obj.set_message("Please check Product Name in invoice details")
                            return success_obj

                    product_isrcm =product_dict['productcode_details']['product_isrcm']
                    product_isblocked = product_dict['productcode_details']['product_isblocked']
                    print('product_isrcm ', product_isrcm)
                    print('product_isblocked ', product_isblocked)

        return product_isrcm,product_isblocked



