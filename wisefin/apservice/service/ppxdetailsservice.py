import json
import sys
import traceback
from datetime import datetime
import numpy as np
import pandas as pd
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse

from apservice.data.request.apheaderrequest import APppxDetailsRequest
from apservice.data.response.apauditresponse import APAuditResponse
from apservice.data.response.apinvoiceheaderresponse import APInvoiceheaderresponse, APppxHeaderResponse, \
    APppxDetailsResponse
from apservice.models import APppxHeader, APppxDetails
from apservice.service.apauditservice import APAuditService
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


class APppxDetailsService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.AP_SERVICE)

    def create_ap_ppxdetails(self, request, ap_data, emp_id):
        try:
            with transaction.atomic(using=self._current_app_schema()):
                resp_list = NWisefinList()
                for ap_json in ap_data['ppxdetails']:
                    ppxdetails_obj = APppxDetailsRequest(ap_json)
                    if not ppxdetails_obj.get_id() is None:
                        ap_ppxdetails_update = APppxDetails.objects.using(self._current_app_schema()).filter(
                            id=ppxdetails_obj.get_id(),
                            entity_id=self._entity_id()).update(
                            #apppxheader_id=ppxdetails_obj.get_apppxheader_id(),
                            #apinvoiceheader_id = ppxdetails_obj.get_apinvoiceheader_id(),
                            #apcredit_id =ppxdetails_obj.get_apcredit_id(),
                            ppxdetails_amount = ppxdetails_obj.get_ppxdetails_amount(),
                            ppxdetails_adjusted = ppxdetails_obj.get_ppxdetails_adjusted(),
                            ppxdetails_balance = ppxdetails_obj.get_ppxdetails_balance(),
                            ap_amount=ppxdetails_obj.get_ap_amount(),
                            ecf_amount = ppxdetails_obj.get_ecf_amount(),
                            process_amount=ppxdetails_obj.get_process_amount(),
                            updated_by=emp_id,
                            updated_date=now())

                        # ap_ppxheader_ecfamt_update
                        from apservice.service.ppxheaderservice import APppxHeaderService
                        ppxheader_id = ppxdetails_obj.get_apppxheader_id()
                        ecf_amount = ppxdetails_obj.get_ecf_amount()
                        ap_amount = ppxdetails_obj.get_ap_amount()
                        ppxhdr_serv = APppxHeaderService(self._scope())
                        print('ecf_amount', ecf_amount, ppxheader_id, emp_id)
                        ecfamt_update = ppxhdr_serv.ap_ppxheader_ecfamt_update(ecf_amount, ap_amount, ppxheader_id,emp_id)
                        print('ecfamt_update', ecfamt_update)

                        ap_ppxdetails = APppxDetails.objects.using(self._current_app_schema()).get(id=ppxdetails_obj.get_id(),
                                                                                                  entity_id=self._entity_id())
                        self.audit_function(ap_ppxdetails, ap_ppxdetails.id, ap_ppxdetails.id, emp_id,
                                            APModifyStatus.UPDATE, APRefType.AP_PPXDetails)

                    else:
                        ap_ppxdetails = APppxDetails.objects.using(self._current_app_schema()).create(
                            apppxheader_id=ppxdetails_obj.get_apppxheader_id(),
                            apinvoiceheader_id=ppxdetails_obj.get_apinvoiceheader_id(),
                            apcredit_id=ppxdetails_obj.get_apcredit_id(),
                            ppxdetails_amount=ppxdetails_obj.get_ppxdetails_amount(),
                            ppxdetails_adjusted=ppxdetails_obj.get_ppxdetails_adjusted(),
                            ecf_amount=ppxdetails_obj.get_ecf_amount(),
                            ap_amount=ppxdetails_obj.get_ap_amount(),
                            process_amount=ppxdetails_obj.get_process_amount(),
                            ppxdetails_balance=ppxdetails_obj.get_ppxdetails_balance(),
                            ecfheader_id=ppxdetails_obj.get_ecfheader_id(),
                            ppxlique_crno=ppxdetails_obj.get_ppxlique_crno(),
                            created_by=emp_id, entity_id=self._entity_id())
                        #ap_ppxheader_ecfamt_update
                        from apservice.service.ppxheaderservice import APppxHeaderService
                        ppxheader_id=ppxdetails_obj.get_apppxheader_id()
                        ecf_amount = ppxdetails_obj.get_ecf_amount()
                        ap_amount = ppxdetails_obj.get_ap_amount()
                        ppxhdr_serv=APppxHeaderService(self._scope())
                        print('ecf_amount',ecf_amount,ppxheader_id,emp_id)
                        ecfamt_update=ppxhdr_serv.ap_ppxheader_ecfamt_update(ecf_amount,ap_amount,ppxheader_id,emp_id)
                        print('ecfamt_update',ecfamt_update)

                        apserv = APService(self._scope())
                        queue_dict = {"ref_id": ap_ppxdetails.id, "ref_type": APRefType.AP_PPXDetails, "remarks": None,
                                      "from_user_id": emp_id,
                                      "status": AP_Status.NEW, "to_user_id": -1, "comments": "PPX DETAILS CREATE"}

                        apserv.create_apqueue(queue_dict)
                        self.audit_function(ap_ppxdetails, ap_ppxdetails.id, ap_ppxdetails.id, emp_id,
                                            APModifyStatus.CREATE, APRefType.AP_PPXDetails)

                    apinvdtl_data = APppxDetailsResponse()
                    apinvdtl_data.set_id(ap_ppxdetails.id)
                    apinvdtl_data.set_apinvoiceheader_id(ap_ppxdetails.apinvoiceheader_id)
                    apinvdtl_data.set_apppxheader_id(ap_ppxdetails.apppxheader_id)
                    apinvdtl_data.set_apcredit_id(ap_ppxdetails.apcredit_id)
                    apinvdtl_data.set_ppxdetails_amount(ap_ppxdetails.ppxdetails_amount)
                    apinvdtl_data.set_ppxdetails_adjusted(ap_ppxdetails.ppxdetails_adjusted)
                    apinvdtl_data.set_ppxdetails_balance(ap_ppxdetails.ppxdetails_balance)
                    apinvdtl_data.set_process_amount(ap_ppxdetails.process_amount)
                    apinvdtl_data.set_ap_amount(ap_ppxdetails.ap_amount)
                    apinvdtl_data.set_ecf_amount(ap_ppxdetails.ecf_amount)
                    apinvdtl_data.set_ecfheader_id(ap_ppxdetails.ecfheader_id)
                    resp_list.append(apinvdtl_data)
            return resp_list

        except Exception as excep:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            traceback.print_exc()
            success_obj = NWisefinSuccess()
            success_obj.set_status("Failed")
            success_obj.set_message(str(excep))
            success_obj.error_info=(str(filename)+", line_no: "+str(line_number)+str(', exception_type : {c} '.format(c=type(excep).__name__)))
            return success_obj



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


    def get_ppx_liquidation(self,apjson_data,vys_page,emp_id):
        contions=Q(is_delete=False,is_closed=False)

        if 'supplier_id' in  apjson_data:
            contions&=Q(apinvoiceheader__supplier_id  = apjson_data['supplier_id'],apinvoiceheader__apheader__payto="S")
        if 'raisedby' in apjson_data:
            contions &= Q(apinvoiceheader__apheader__raisedby=apjson_data['raisedby'],apinvoiceheader__apheader__payto="E")

        ap_ppxdetails_data = APppxDetails.objects.using(self._current_app_schema()).filter(contions).order_by("-id")[
                                 vys_page.get_offset():vys_page.get_query_limit()]
        resp_list = NWisefinList()

        for ap_ppxdetails in ap_ppxdetails_data:
            ap_api_serv=APApiService(self._scope())
            apinvdtl_data = APppxDetailsResponse()
            apinvdtl_data.set_id(ap_ppxdetails.id)
            apinvdtl_data.set_apinvoiceheader_id(ap_ppxdetails.apinvoiceheader_id)
            apinvdtl_data.set_apppxheader_id(ap_ppxdetails.apppxheader_id)
            apinvdtl_data.set_apcredit_id(ap_ppxdetails.apcredit_id)
            apinvdtl_data.set_ppxdetails_amount(ap_ppxdetails.ppxdetails_amount)
            apinvdtl_data.set_ppxdetails_adjusted(ap_ppxdetails.ppxdetails_adjusted)
            apinvdtl_data.set_ppxdetails_balance(ap_ppxdetails.ppxdetails_balance)
            apinvdtl_data.crno=(ap_ppxdetails.apppxheader.crno)
            apinvdtl_data.Payto=(ap_ppxdetails.apinvoiceheader.apheader.payto)
            apinvdtl_data.payto_name = None
            if str(ap_ppxdetails.apinvoiceheader.apheader.payto) == "S":
                 supplierbranch_json=ap_api_serv.get_supplierbranch_details(ap_ppxdetails.apinvoiceheader.supplier_id,emp_id)
                 apinvdtl_data.payto_name={"name":supplierbranch_json.get("name"),"code":supplierbranch_json.get("code"),
                                           "full_name":supplierbranch_json.get("name")+" - "+supplierbranch_json.get("code")}
            if str(ap_ppxdetails.apinvoiceheader.apheader.payto) == "E":
                emp_json =ap_api_serv.get_employee_single(ap_ppxdetails.apinvoiceheader.apheader.raisedby)
                apinvdtl_data.payto_name ={"name":emp_json.get("full_name"),"code":emp_json.get("code") ,
                                           "full_name":emp_json.get("full_name")+" - "+emp_json.get("code")}

            apinvdtl_data.ppxheader_date= str(ap_ppxdetails.apppxheader.ppxheader_date.date())
            apinvdtl_data.process_amount= str(ap_ppxdetails.process_amount)
            apinvdtl_data.ap_amount= str(ap_ppxdetails.ap_amount)
            apinvdtl_data.ecf_amount= str(ap_ppxdetails.ecf_amount)
            resp_list.append(apinvdtl_data)
        return resp_list

    def get_ppx_liquidation_using_ppxheader_id(self,ppxheader_id,emp_id):
        contions=Q(is_delete=False,is_closed=False,apppxheader_id=ppxheader_id)

        ap_ppxdetails_data = APppxDetails.objects.using(self._current_app_schema()).filter(contions).order_by("-id")
        resp_list = NWisefinList()

        for ap_ppxdetails in ap_ppxdetails_data:
            from apservice.service.apinvoiceheaderservice import APInvoiceheaderService
            apinvhdr_serv = APInvoiceheaderService(self._scope())
            ap_api_serv=APApiService(self._scope())
            apinvdtl_data = APppxDetailsResponse()
            apinvdtl_data.set_id(ap_ppxdetails.id)
            apinvdtl_data.set_apinvoiceheader_id(ap_ppxdetails.apinvoiceheader_id)
            apinvdtl_data.set_apppxheader_id(ap_ppxdetails.apppxheader_id)
            apinvdtl_data.set_apcredit_id(ap_ppxdetails.apcredit_id)
            apinvdtl_data.set_ppxdetails_amount(ap_ppxdetails.ppxdetails_amount)
            apinvdtl_data.set_ppxdetails_adjusted(ap_ppxdetails.ppxdetails_adjusted)
            apinvdtl_data.set_ppxdetails_balance(ap_ppxdetails.ppxdetails_balance)
            apinvdtl_data.crno=(ap_ppxdetails.apppxheader.crno)
            apinvdtl_data.Payto=(ap_ppxdetails.apinvoiceheader.apheader.payto)
            apinvdtl_data.payto_name = None
            if str(ap_ppxdetails.apinvoiceheader.apheader.payto) == "S":
                 supplierbranch_json=ap_api_serv.get_supplierbranch_details(ap_ppxdetails.apinvoiceheader.supplier_id,emp_id)
                 apinvdtl_data.payto_name={"name":supplierbranch_json.get("name"),"code":supplierbranch_json.get("code"),
                                           "full_name":supplierbranch_json.get("name")+" - "+supplierbranch_json.get("code")}
            if str(ap_ppxdetails.apinvoiceheader.apheader.payto) == "E":
                emp_json =ap_api_serv.get_employee_single(ap_ppxdetails.apinvoiceheader.apheader.raisedby)
                apinvdtl_data.payto_name ={"name":emp_json.get("full_name"),"code":emp_json.get("code") ,
                                           "full_name":emp_json.get("full_name")+" - "+emp_json.get("code")}

            apinvdtl_data.ppxheader_date= str(ap_ppxdetails.apppxheader.ppxheader_date.date())
            apinvdtl_data.process_amount= str(ap_ppxdetails.process_amount)
            apinvdtl_data.ap_amount= str(ap_ppxdetails.ap_amount)
            apinvdtl_data.ecf_amount= str(ap_ppxdetails.ecf_amount)
            apinvdtl_data.current_crno= ap_ppxdetails.ppxlique_crno
            apinvdtl_data.ecfheader_id= ap_ppxdetails.ecfheader_id
            apinvdtl_data.invoiceheader_status = apinvhdr_serv.get_invoiceheader_status(ap_ppxdetails.apinvoiceheader_id)
            apinvdtl_data.invoicehdr_current_status = apinvhdr_serv.get_invoiceheader_status_using_crno(ap_ppxdetails.ppxlique_crno)

            resp_list.append(apinvdtl_data)
        return resp_list

    def ppxdetails_delete(self,ecfheader_id,emp_id):
        try:
            ppxdetails = APppxDetails.objects.using(self._current_app_schema()).filter(ecfheader_id=ecfheader_id, is_delete=0,
                                     entity_id=self._entity_id()).update(
                        is_delete=1, updated_by=emp_id, updated_date=now())

            if ppxdetails == 0:
                success_obj = NWisefinSuccess()
                success_obj.set_status("Failed")
                success_obj.set_message("INVALID ECFHEADER ID")
                return success_obj
            else:
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
                return success_obj

        except Exception as excep:
            traceback.print_exc()
            success_obj = NWisefinSuccess()
            success_obj.set_status("Failed")
            success_obj.set_message(str(excep))
            return success_obj


    def ppxdetails_crno_update(self,ecfheader_id,crno,emp_id):
        try:
            ppxdetails = APppxDetails.objects.using(self._current_app_schema()).filter(ecfheader_id=ecfheader_id, is_delete=0,
                                     entity_id=self._entity_id()).update(
                        ppxlique_crno=crno, updated_by=emp_id, updated_date=now())
            print('ppxdetails_crno_update in AP -- ',' ecfheader_id ', ecfheader_id ,' crno ',crno ,'ppxdetails ',ppxdetails )
            logger('ppxdetails_crno_update in AP -- '+' ecfheader_id '+ str(ecfheader_id) ,' crno ' +str(crno) +'ppxdetails '+str(ppxdetails))

            if ppxdetails == 0:
                success_obj = NWisefinSuccess()
                success_obj.set_status("Failed")
                success_obj.set_message("INVALID ECFHEADER ID")
                return success_obj
            else:
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
                return success_obj

        except Exception as excep:
            traceback.print_exc()
            success_obj = NWisefinSuccess()
            success_obj.set_status("Failed")
            success_obj.set_message(str(excep))
            return success_obj


    def ppxdetails_liquedation_update(self,ppxlique_crno,emp_id):
        ap_ppxdtls_update = APppxDetails.objects.using(self._current_app_schema()).filter(
            is_closed=False,is_delete=False,ppxlique_crno=ppxlique_crno,
            entity_id=self._entity_id())
        print('ap_ppxdetails_update ',ap_ppxdtls_update)
        print('ap_ppxdetails_update_query ',ap_ppxdtls_update.query)

        for ap_ppxdtls in ap_ppxdtls_update:
            ap_amount = ap_ppxdtls.ap_amount
            ap_ppxdetails_update = APppxDetails.objects.using(self._current_app_schema()).filter(
                is_closed=False, is_delete=False, id=ap_ppxdtls.id,
                entity_id=self._entity_id()).update(
                process_amount=ap_amount,
                is_closed = True,
                updated_by = emp_id,
                updated_date = now())
            print('ap_ppxdetails_update ',ap_ppxdetails_update)

            #header update
            from apservice.service.ppxheaderservice import APppxHeaderService
            ppxhdr_serv = APppxHeaderService(self._scope())
            ppxhdr_serv.ap_ppxheader_balance_update(ap_amount, ap_ppxdtls.apppxheader_id, emp_id)