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
from apservice.data.response.apinvoiceheaderresponse import APInvoiceheaderresponse, APppxHeaderResponse
from apservice.models import APppxHeader, APppxDetails
from apservice.service.apauditservice import APAuditService
from apservice.service.apcreditservice import APCreditService
from apservice.service.apdebitservice import APDebitService
from apservice.service.apinvoicedetailsservice import APInvoiceDetailService

from apservice.service.apservice import APService
from apservice.util.aputil import APModifyStatus, APRefType, ap_get_api_caller, get_APType, get_AP_status, AP_Status, \
    dropdown_status
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.permissions.filter.commonpermission import ModulePermission
from utilityservice.permissions.util.dbutil import RoleList, ModuleList
from utilityservice.service.ap_api_service import APApiService
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from django.utils.timezone import now

class APppxHeaderService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.AP_SERVICE)

    def create_ap_ppxheader(self,request,ppxheader_obj,emp_id):

        if not ppxheader_obj.get_id() is None:
            ap_ppx_header_update = APppxHeader.objects.using(self._current_app_schema()).filter(id=ppxheader_obj.get_id(),
                                                                                entity_id=self._entity_id()).update(
                                                                                #ppxheader_date = ppxheader_obj.get_ppxheader_date(),
                                                                                ppxheader_amount = ppxheader_obj.get_ppxheader_amount(),
                                                                                ppxheader_balance = ppxheader_obj.get_ppxheader_balance(),
                                                                                updated_by=emp_id,
                                                                                updated_date=now())
            ap_ppx_header = APppxHeader.objects.using(self._current_app_schema()).get(id=ppxheader_obj.get_id(),
                                                                                     entity_id=self._entity_id())
            self.audit_function(ap_ppx_header, ap_ppx_header.id, ap_ppx_header.id, emp_id,
                                APModifyStatus.UPDATE, APRefType.AP_PPXHeader)

        else:
            ap_ppx_header = APppxHeader.objects.using(self._current_app_schema()).create(
                                                apinvoiceheader_id=ppxheader_obj.get_apinvoiceheader_id(),
                                                crno = ppxheader_obj.get_crno(),
                                                #ppxheader_date = ppxheader_obj.get_ppxheader_date(),
                                                ppxheader_amount = ppxheader_obj.get_ppxheader_amount(),
                                                ppxheader_balance = ppxheader_obj.get_ppxheader_balance(),
                                                created_by=emp_id, entity_id=self._entity_id())

            apserv=APService(self._scope())
            queue_dict={"ref_id":ap_ppx_header.id,"ref_type":APRefType.AP_PPXHeader,"remarks":None,"from_user_id":emp_id,
                        "status":AP_Status.NEW,"to_user_id":-1,"comments":"PPX HEADER CREATE"}

            apserv.create_apqueue(queue_dict)
            self.audit_function(ap_ppx_header, ap_ppx_header.id, ap_ppx_header.id, emp_id,
                                APModifyStatus.CREATE, APRefType.AP_PPXHeader)

        apinhdr_data = APppxHeaderResponse()
        apinhdr_data.set_id(ap_ppx_header.id)
        apinhdr_data.set_apinvoiceheader_id(ap_ppx_header.apinvoiceheader_id)
        apinhdr_data.set_crno(ap_ppx_header.crno)
        apinhdr_data.set_ppxheader_date(ap_ppx_header.ppxheader_date)
        apinhdr_data.set_ppxheader_amount(ap_ppx_header.ppxheader_amount)
        apinhdr_data.set_ppxheader_balance(ap_ppx_header.ppxheader_balance)
        return apinhdr_data


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
        audit_obj.set_reftype(APRefType.AP_PPXHeader)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(APRefType.AP_PPXHeader)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)



    def ap_ppxheader_update(self,ppxheader_balance,ppxheader_id,emp_id):
        ap_ppx_header_update = APppxHeader.objects.using(self._current_app_schema()).filter(id=ppxheader_id,
                                                                            entity_id=self._entity_id()).update(
                                                                            ppxheader_balance = ppxheader_balance,
                                                                            updated_by=emp_id,
                                                                            updated_date=now())



    def ap_ppxheader_ecfamt_update(self,ecf_amount,ap_amount,ppxheader_id,emp_id):

        ap_ppx_header = APppxHeader.objects.using(self._current_app_schema()).filter(
                                                id=ppxheader_id,entity_id=self._entity_id())[0]

        print('ap_amount ', ap_amount)
        print('ecf_amount ', ecf_amount)
        ppxhdr_ap_amount = float(ap_ppx_header.ap_amount)
        ap_update_amount = ppxhdr_ap_amount + float(ap_amount)
        print('ppxhdr_ap_amount ',ppxhdr_ap_amount)
        print('ap_update_amount ',ap_update_amount)

        ppxhdr_ecfamt = float(ap_ppx_header.ecf_amount)
        ecf_update_amount=ppxhdr_ecfamt + float(ecf_amount)
        print('ppxhdr_ecfamt ', ppxhdr_ecfamt)

        print('ecf_update_amount ', ecf_update_amount)

        ap_ppx_header_update = APppxHeader.objects.using(self._current_app_schema()).filter(id=ppxheader_id,
                                                                            entity_id=self._entity_id()).update(
                                                                            ecf_amount = ecf_update_amount,
                                                                            ap_amount = ap_update_amount,
                                                                            updated_by=emp_id,
                                                                            updated_date=now())
        return ap_ppx_header_update




    def get_ppxheader_liquidation(self,apjson_data,vys_page,emp_id):
        try:
            contions=Q(is_delete=False,is_closed=False)

            if 'supplier_id' in  apjson_data:
                contions&=Q(apinvoiceheader__supplier_id  = apjson_data['supplier_id'],apinvoiceheader__apheader__payto="S")
            if 'raisedby' in apjson_data:
                contions &= Q(apinvoiceheader__apheader__raisedby=apjson_data['raisedby'],apinvoiceheader__apheader__payto="E")

            ap_ppxheader_data = APppxHeader.objects.using(self._current_app_schema()).filter(contions).order_by("-id")[
                                     vys_page.get_offset():vys_page.get_query_limit()]
            resp_list = NWisefinList()
            if len(ap_ppxheader_data) > 0:
                for ap_ppxheader in ap_ppxheader_data:
                    from apservice.service.ppxdetailsservice import APppxDetailsService
                    from apservice.service.apinvoiceheaderservice import APInvoiceheaderService
                    ap_api_serv=APApiService(self._scope())
                    debit_serv=APDebitService(self._scope())
                    debit_data=debit_serv.get_apdebit_using_apinvoicehdr_id(ap_ppxheader.apinvoiceheader_id)
                    apserv_crdit=APCreditService(self._scope())
                    ppxdtls_serv = APppxDetailsService(self._scope())
                    apinvhdr_serv = APInvoiceheaderService(self._scope())
                    apppxhdr_data = APppxHeaderResponse()

                    apppxhdr_data.set_id(ap_ppxheader.id)
                    apppxhdr_data.set_apinvoiceheader_id(ap_ppxheader.apinvoiceheader_id)

                    apppxhdr_data.credit_glno=(debit_data.debitglno)
                    apppxhdr_data.credit_category=(debit_data.category_code)
                    apppxhdr_data.credit_subcategory=(debit_data.subcategory_code)

                    apppxhdr_data.set_ppxheader_amount(ap_ppxheader.ppxheader_amount)
                    apppxhdr_data.set_ppxheader_balance(ap_ppxheader.ppxheader_balance)
                    apppxhdr_data.set_crno(ap_ppxheader.crno)
                    apppxhdr_data.Payto=(ap_ppxheader.apinvoiceheader.apheader.payto)
                    apppxhdr_data.invoice_no=(ap_ppxheader.apinvoiceheader.invoiceno)
                    apppxhdr_data.emp_branch_details=self.emp_branch_details(ap_ppxheader.apinvoiceheader.apheader.raisedby)
                    credit_data=apserv_crdit.fetch_apcredit_account_dtls(None,ap_ppxheader.apinvoiceheader_id,None)
                    credit_id=None
                    credit_refno=None
                    #credit_glno=None
                    if credit_data:
                        credit_id=credit_data.id
                        credit_refno=credit_data.creditrefno
                        #credit_glno=credit_data.creditglno

                    apppxhdr_data.credit_id = credit_id
                    apppxhdr_data.credit_refno = credit_refno
                    #apppxhdr_data.credit_glno = credit_glno

                    apppxhdr_data.payto_name = None
                    if str(ap_ppxheader.apinvoiceheader.apheader.payto) == "S":
                         supplierbranch_json=ap_api_serv.get_supplierbranch_details(ap_ppxheader.apinvoiceheader.supplier_id,emp_id)
                         apppxhdr_data.payto_name={"name":supplierbranch_json.get("name"),"code":supplierbranch_json.get("code"),
                                                   "full_name":supplierbranch_json.get("name")+" - "+supplierbranch_json.get("code")}
                    if str(ap_ppxheader.apinvoiceheader.apheader.payto) == "E":
                        emp_json =ap_api_serv.get_employee_single(ap_ppxheader.apinvoiceheader.apheader.raisedby)
                        apppxhdr_data.payto_name ={"name":emp_json.get("full_name"),"code":emp_json.get("code") ,
                                                   "full_name":emp_json.get("full_name")+" - "+emp_json.get("code")}

                    apppxhdr_data.ppxheader_date= str(ap_ppxheader.ppxheader_date.date())
                    apppxhdr_data.process_amount= str(ap_ppxheader.process_amount)
                    apppxhdr_data.ap_amount= str(ap_ppxheader.ap_amount)
                    apppxhdr_data.ecf_amount= str(ap_ppxheader.ecf_amount)
                    #liquedate_limit for ECF
                    apppxhdr_data.liquedate_limit = 0
                    if  float(ap_ppxheader.ppxheader_amount) > float(ap_ppxheader.ecf_amount):
                        apppxhdr_data.liquedate_limit = str(ap_ppxheader.ppxheader_amount - ap_ppxheader.ecf_amount)
                    #AP_liquedate_limit for AP
                    apppxhdr_data.AP_liquedate_limit = 0
                    if  float(ap_ppxheader.ppxheader_amount) > float(ap_ppxheader.ap_amount):
                        apppxhdr_data.AP_liquedate_limit = str(ap_ppxheader.ppxheader_amount - ap_ppxheader.ap_amount)
                    # liquedate_amount for ECF UI process , in BE Dummy Field
                    apppxhdr_data.liquedate_amount = 0
                    apppxhdr_data.invoiceheader_status = apinvhdr_serv.get_invoiceheader_status(ap_ppxheader.apinvoiceheader_id)
                    apppxhdr_data.ppxdetails = ppxdtls_serv.get_ppx_liquidation_using_ppxheader_id(ap_ppxheader.id,emp_id)
                    resp_list.append(apppxhdr_data)
                vpage = NWisefinPaginator(ap_ppxheader_data, vys_page.get_index(), 10)
                resp_list.set_pagination(vpage)
            return resp_list
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

    def emp_branch_details(self,raisedby_emp_id):
        from utilityservice.service.ap_api_service import APApiService
        return_data=[]
        ap_api_serv = APApiService(self._scope())
        raiser_emp = ap_api_serv.get_single_emp_id(raisedby_emp_id)
        empbranch_id=raiser_emp.get('employee_branch')
        if empbranch_id not  in ['',' ',None]:
            return_data=ap_api_serv.ap_employee_branch_single_get(empbranch_id)
        return return_data


    def ap_ppxheader_balance_update(self,ap_amount,ppxheader_id,emp_id):
            ap_ppxheader = APppxHeader.objects.using(self._current_app_schema()).get(id=ppxheader_id,
                                                                                is_delete=0, is_closed=0)
            print('ap_ppxheader ',ap_ppxheader)
            ppxheader_balance= float(ap_ppxheader.ppxheader_balance)-float(ap_amount)

            ap_ppx_header_update = APppxHeader.objects.using(self._current_app_schema()).filter(id=ppxheader_id,
                                                    is_delete=0, is_closed=0,entity_id=self._entity_id()).update(
                                                                        ppxheader_balance = ppxheader_balance,
                                                                        updated_by=emp_id,
                                                                        updated_date=now())
            print('ap_ppx_header_update ',ap_ppx_header_update)
            ap_ppx_header = APppxHeader.objects.using(self._current_app_schema()).get(id=ppxheader_id,
                                                                        is_delete=0,is_closed=0)
            print('ppxheader_balance ',ppxheader_balance)
            if int(ppxheader_balance) == 0:
                ap_ppx_header.is_closed=True
                ap_ppx_header.save()




