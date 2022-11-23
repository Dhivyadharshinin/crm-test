import json
import traceback

from apservice.data.response.apauditresponse import APAuditResponse
from apservice.data.response.apinvoicedetailresponse import APInvoiceDetailsResponse, APccbsDetailsResponse
from apservice.models import APInvoicedetail, APCCBSDetails
from apservice.service.apauditservice import APAuditService
from apservice.util.aputil import APRefType, APModifyStatus
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from django.utils.timezone import now


class APInvoiceDetailService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.AP_SERVICE)

    def apinvdtl_create(self,apinvdtl_obj,apinvhdr_id,emp_id):
        print('get_is_capitalized ',apinvdtl_obj.get_is_capitalized())
        if not apinvdtl_obj.get_id() is None:
            apinvdtl_update = APInvoicedetail.objects.using(self._current_app_schema()).filter(id=apinvdtl_obj.get_id(),
                                                                   entity_id=self._entity_id()).update(
                apinvoiceheader_id=apinvhdr_id,
                mepno=apinvdtl_obj.get_mepno(),
                productcode=apinvdtl_obj.get_productcode(),
                productname=apinvdtl_obj.get_productname(),
                description=apinvdtl_obj.get_description(),
                hsn=apinvdtl_obj.get_hsn(),
                hsn_percentage=apinvdtl_obj.get_hsn_percentage(),
                uom=apinvdtl_obj.get_uom(),
                unitprice=apinvdtl_obj.get_unitprice(),
                quantity=apinvdtl_obj.get_quantity(),
                amount=apinvdtl_obj.get_amount(),
                discount=apinvdtl_obj.get_discount(),
                sgst=apinvdtl_obj.get_sgst(),
                cgst=apinvdtl_obj.get_cgst(),
                igst=apinvdtl_obj.get_igst(),
                taxamount=apinvdtl_obj.get_taxamount(),
                totalamount=apinvdtl_obj.get_totalamount(),
                otheramount=apinvdtl_obj.get_otheramount(),
                roundoffamt=apinvdtl_obj.get_roundoffamt(),
                is_capitalized=apinvdtl_obj.get_is_capitalized(),
                updated_by=emp_id,
                updated_date=now())

            apinvdtl = APInvoicedetail.objects.using(self._current_app_schema()).get(id=apinvdtl_obj.get_id(),
                                                                                     entity_id=self._entity_id())

            from apservice.service.apinvoiceheaderservice import APInvoiceheaderService
            apinvhdr_serv=APInvoiceheaderService(self._scope())
            apinvhdr_serv.update_invoicehdr_adjsmt_amount(apinvhdr_id,apinvdtl_obj.get_otheramount(),apinvdtl_obj.get_roundoffamt(), emp_id)
            self.audit_function(apinvdtl, apinvdtl.id, apinvdtl.id, emp_id,
                                APModifyStatus.UPDATE, APRefType.APINVOICEDETAIL)

        else:
            apinvdtl = APInvoicedetail.objects.using(self._current_app_schema()).create(
                apinvoiceheader_id=apinvhdr_id,
                mepno=apinvdtl_obj.get_mepno(),
                productcode=apinvdtl_obj.get_productcode(),
                productname=apinvdtl_obj.get_productname(),
                description=apinvdtl_obj.get_description(),
                is_capitalized=apinvdtl_obj.get_is_capitalized(),
                hsn=apinvdtl_obj.get_hsn(),
                hsn_percentage=apinvdtl_obj.get_hsn_percentage(),
                uom=apinvdtl_obj.get_uom(),
                unitprice=apinvdtl_obj.get_unitprice(),
                quantity=apinvdtl_obj.get_quantity(),
                amount=apinvdtl_obj.get_amount(),
                discount=apinvdtl_obj.get_discount(),
                sgst=apinvdtl_obj.get_sgst(),
                cgst=apinvdtl_obj.get_cgst(),
                igst=apinvdtl_obj.get_igst(),
                taxamount=apinvdtl_obj.get_taxamount(),
                totalamount=apinvdtl_obj.get_totalamount(),
                otheramount=apinvdtl_obj.get_otheramount(),
                roundoffamt=apinvdtl_obj.get_roundoffamt(),
                created_by=emp_id,
                entity_id=self._entity_id())

            self.audit_function(apinvdtl, apinvdtl.id, apinvdtl.id, emp_id,
                                APModifyStatus.CREATE, APRefType.APINVOICEDETAIL)


        apindtl_data = APInvoiceDetailsResponse()
        apindtl_data.set_id(apinvdtl.id)
        apindtl_data.set_apinvoiceheader(apinvdtl.apinvoiceheader_id)
        apindtl_data.set_otheramount(apinvdtl.otheramount)
        apindtl_data.set_roundoffamt(apinvdtl.roundoffamt)
        apindtl_data.set_apinvoice_po(apinvdtl.apinvoice_po)
        apindtl_data.set_mepno(apinvdtl.mepno)
        apindtl_data.set_productcode(apinvdtl.productcode)
        apindtl_data.set_productname(apinvdtl.productname)
        apindtl_data.set_description(apinvdtl.description)
        apindtl_data.set_hsn(apinvdtl.hsn)
        apindtl_data.set_hsn_percentage(apinvdtl.hsn_percentage)
        apindtl_data.set_uom(apinvdtl.uom)
        apindtl_data.set_unitprice(apinvdtl.unitprice)
        apindtl_data.set_quantity(apinvdtl.quantity)
        apindtl_data.set_amount(apinvdtl.amount)
        apindtl_data.set_discount(apinvdtl.discount)
        apindtl_data.set_sgst(apinvdtl.sgst)
        apindtl_data.set_cgst(apinvdtl.cgst)
        apindtl_data.set_igst(apinvdtl.igst)
        apindtl_data.set_taxamount(apinvdtl.taxamount)
        apindtl_data.set_totalamount(apinvdtl.totalamount)
        apindtl_data.set_is_capitalized(self.boolean_conver_to_number(apinvdtl.is_capitalized))
        apindtl_data.set_entry_flag(self.boolean_conver_to_number(apinvdtl.entry_flag))
        return apindtl_data


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
        audit_obj.set_reftype(APRefType.APINVOICEDETAIL)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(APRefType.APINVOICEDETAIL)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)

    def apccbs_create(self, apccbs_obj, apdebit_id, emp_id):

        if not apccbs_obj.get_id() is None:
            apccbs_update = APCCBSDetails.objects.using(self._current_app_schema()).filter(id=apccbs_obj.get_id(),
                                                                                entity_id=self._entity_id()).update(
                apdebit_id=apdebit_id,
                cc_code=apccbs_obj.get_cc_code(),
                bs_code=apccbs_obj.get_bs_code(),
                code=apccbs_obj.get_code(),
                ccbspercentage=apccbs_obj.get_ccbspercentage(),
                glno=apccbs_obj.get_glno(),
                amount=apccbs_obj.get_amount(),
                remarks=apccbs_obj.get_remarks(),
                updated_by=emp_id,
                updated_date=now())
            apccbs = APCCBSDetails.objects.using(self._current_app_schema()).get(id=apccbs_obj.get_id(),
                                                                            entity_id=self._entity_id())
            self.audit_function_ccbs(apccbs, apccbs.id, apccbs.id, emp_id,
                                APModifyStatus.UPDATE, APRefType.APDEBITCCBS)

        else:
            apccbs = APCCBSDetails.objects.using(self._current_app_schema()).create(
                apdebit_id=apdebit_id,
                cc_code=apccbs_obj.get_cc_code(),
                bs_code=apccbs_obj.get_bs_code(),
                code=apccbs_obj.get_code(),
                ccbspercentage=apccbs_obj.get_ccbspercentage(),
                glno=apccbs_obj.get_glno(),
                amount=apccbs_obj.get_amount(),
                remarks=apccbs_obj.get_remarks(),
                created_by=emp_id,entity_id=self._entity_id())
            self.audit_function_ccbs(apccbs, apccbs.id, apccbs.id, emp_id,
                                     APModifyStatus.CREATE, APRefType.APDEBITCCBS)

        apccbs_data = APccbsDetailsResponse()
        apccbs_data.set_id(apccbs.id)
        apccbs_data.set_debit(apccbs.apdebit_id)
        apccbs_data.set_cc_code(apccbs.cc_code)
        apccbs_data.set_bs_code(apccbs.bs_code)
        apccbs_data.set_code(apccbs.code)
        apccbs_data.set_ccbspercentage(apccbs.ccbspercentage)
        apccbs_data.set_glno(apccbs.glno)
        apccbs_data.set_amount(apccbs.amount)
        apccbs_data.set_remarks(apccbs.remarks)
        return apccbs_data

    def direct_ccbs_create(self,ccbs_data,apdebit_new,emp_id):
        ap_ccbs = APCCBSDetails.objects.using(self._current_app_schema()).create(
            apdebit_id=apdebit_new.id,
            cc_code=ccbs_data.cc_code,
            bs_code=ccbs_data.bs_code,
            code=ccbs_data.code,
            ccbspercentage=ccbs_data.ccbspercentage,
            glno=ccbs_data.glno,
            amount=ccbs_data.amount,
            remarks=None,
            created_by=emp_id, entity_id=self._entity_id())
        self.audit_function_ccbs(ap_ccbs, ap_ccbs.id, ap_ccbs.id, emp_id,
                                 APModifyStatus.CREATE, APRefType.APDEBITCCBS)
        return ap_ccbs

    def audit_function_ccbs(self, audit_data, refid, relrefid, emp_id, action, reqstatus):
        if action == APModifyStatus.DELETE:
            data = None
        else:
            data = audit_data.__dict__
            del data['_state']
        audit_service = APAuditService(self._scope())
        audit_obj = APAuditResponse()
        audit_obj.set_refid(refid)
        audit_obj.set_reqstatus(reqstatus)
        audit_obj.set_reftype(APRefType.APDEBITCCBS)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(APRefType.APDEBITCCBS)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)

    def fetch_apdebit_ccbs(self,request,apdebit_id):

        ccbs_json = dict()
        ccbs_list=[]
        ccbs_data = APCCBSDetails.objects.using(self._current_app_schema()).filter(apdebit_id=apdebit_id,
                                                                is_delete=0,entity_id=self._entity_id())
        if len(ccbs_data) > 0:
            for ccbs in ccbs_data:
                from utilityservice.service import api_service
                api_serv = api_service.ApiService(self._scope())
                cc = api_serv.get_cc_code(request, ccbs.cc_code)
                bs = api_serv.get_bs_code(request, ccbs.bs_code)
                ccbs_data = APccbsDetailsResponse()
                ccbs_data.set_id(ccbs.id)
                # ccbs_data.set_debit(ccbs.apdebit_id)
                ccbs_data.set_cc_code(cc)
                ccbs_data.set_bs_code(bs)
                ccbs_data.set_code(ccbs.code)
                ccbs_data.set_ccbspercentage(ccbs.ccbspercentage)
                ccbs_data.set_glno(ccbs.glno)
                ccbs_data.set_amount(ccbs.amount)
                ccbs_data.set_remarks(ccbs.remarks)
                ccbs_list.append(json.loads(ccbs_data.get()))
        return ccbs_list

                #dbt_data.set_ccbs(ccbs_data)
                #invdeb_list.append(json.loads(dbt_data.get()))



    def fetch_apdebit_ccbs_list(self,request,apdebit_id):

        ccbs_list = NWisefinList()
        ccbs_data = APCCBSDetails.objects.using(self._current_app_schema()).filter(apdebit_id=apdebit_id,
                                                                    is_delete=0,entity_id=self._entity_id())
        if len(ccbs_data) > 0:
            for ccbs in ccbs_data:
                from utilityservice.service import api_service
                api_serv = api_service.ApiService(self._scope())
                cc = api_serv.get_cc_code(request, ccbs.cc_code)
                bs = api_serv.get_bs_code(request, ccbs.bs_code)
                ccbs_data = APccbsDetailsResponse()
                ccbs_data.set_id(ccbs.id)
                # ccbs_data.set_debit(ccbs.apdebit_id)
                ccbs_data.set_cc_code(cc)
                ccbs_data.set_bs_code(bs)
                ccbs_data.set_code(ccbs.code)
                ccbs_data.set_ccbspercentage(ccbs.ccbspercentage)
                ccbs_data.set_glno(ccbs.glno)
                ccbs_data.set_amount(ccbs.amount)
                ccbs_data.set_remarks(ccbs.remarks)
                ccbs_list.append(ccbs_data)
                #dbt_data.set_ccbs(ccbs_data)
                #invdeb_list.append(json.loads(dbt_data.get()))
        return ccbs_list

    def get_apdebit_ccbs_single(self,request,apccbs_id,emp_id):
        try:
            ccbs = APCCBSDetails.objects.using(self._current_app_schema()).get(id=apccbs_id,
                                                                    entity_id=self._entity_id(),is_delete=0)

            from utilityservice.service import api_service
            api_serv = api_service.ApiService(self._scope())
            cc = api_serv.get_cc_code(request, ccbs.cc_code)
            bs = api_serv.get_bs_code(request, ccbs.bs_code)
            ccbs_data = APccbsDetailsResponse()
            ccbs_data.set_id(ccbs.id)
            # ccbs_data.set_debit(ccbs.apdebit_id)
            ccbs_data.set_cc_code(cc)
            ccbs_data.set_bs_code(bs)
            ccbs_data.set_code(ccbs.code)
            ccbs_data.set_ccbspercentage(ccbs.ccbspercentage)
            ccbs_data.set_glno(ccbs.glno)
            ccbs_data.set_amount(ccbs.amount)
            ccbs_data.set_remarks(ccbs.remarks)
            return ccbs_data
        except Exception as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj


    def ccbs_delete_using_apdebit_id(self,emp_id,apdebit_id):
            ccbs_delete = APCCBSDetails.objects.using(self._current_app_schema()).filter(apdebit_id=apdebit_id,
                        entity_id=self._entity_id(),is_delete=0).update(
                        is_delete=1,updated_by=emp_id,updated_date=now())
            print('ccbsdetails_delete ',ccbs_delete)
            return ccbs_delete


    def ccbs_delete_using_apinvoicedetail_id(self,emp_id,apinvoicedetail_id):
            ccbs_delete = APCCBSDetails.objects.using(self._current_app_schema()).filter(apdebit__apinvoicedetail__id=apinvoicedetail_id,
                        entity_id=self._entity_id(),is_delete=0).update(
                        is_delete=1,updated_by=emp_id,updated_date=now())
            print('ccbsdetails_delete ',ccbs_delete)
            return ccbs_delete

    def apdebit_ccbs_single_delete(self,apccbs_id,emp_id):
        try:
            apcredit = APCCBSDetails.objects.using(self._current_app_schema()).filter(id=apccbs_id,
                                                                entity_id=self._entity_id(),is_delete=0).update(
                is_delete=1,updated_by=emp_id,updated_date=now())

            if apcredit == 0:
                error_obj = NWisefinError()
                error_obj.set_code('INVALID_APCCBS_ID')
                error_obj.set_description('INVALID APCCBS ID')
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


    def fetch_apinvdtl_using_apinvhdr(self,request,apinvhdr_id,emp_id):

        apinvdtl_data = APInvoicedetail.objects.using(self._current_app_schema()).filter(apinvoiceheader_id=apinvhdr_id,
                                                                    status=1,is_delete=0,entity_id=self._entity_id())

        apinvdtl_list = []
        if len(apinvdtl_data) >0 :
            for apinvdtl in apinvdtl_data:
                from apservice.service.apdebitservice import APDebitService
                from utilityservice.service import api_service
                api_serv = api_service.ApiService(self._scope())
                apdebt_serv = APDebitService(self._scope())
                print('apinvdtl_hsn',apinvdtl.hsn)
                try:
                    if apinvdtl.hsn not in ['',' ',None,0,"0"]:
                        hsn = api_serv.get_hsn_code(request, apinvdtl.hsn)
                        print('hsntype ',type(hsn))
                        if type(hsn) != type(dict()) and "description" in hsn.get():
                            hsn = {"Status": "Failed", "Message": "Invalid hsn code -" + str(apinvdtl.hsn)}
                    else:
                        hsn={ "Status":"Failed","Message":"Invalid hsn code- "  + str(apinvdtl.hsn) }
                except:
                     hsn={ "Status":"Failed","Message":"Invalid hsn code-" + str(apinvdtl.hsn) }

                apinvdtl_resp = APInvoiceDetailsResponse()
                apinvdtl_resp.set_id(apinvdtl.id)
                apinvdtl_resp.set_apinvoiceheader(apinvdtl.apinvoiceheader_id)
                apinvdtl_resp.set_apinvoice_po(apinvdtl.apinvoice_po)
                apinvdtl_resp.set_productcode(apinvdtl.productcode)
                apinvdtl_resp.set_productname(apinvdtl.productname)
                apinvdtl_resp.set_description(apinvdtl.description)
                apinvdtl_resp.set_hsn(hsn)
                apinvdtl_resp.set_hsn_percentage(apinvdtl.hsn_percentage)
                apinvdtl_resp.set_uom({"uom": apinvdtl.uom, "apinvdtl_id": apinvdtl.id})
                apinvdtl_resp.set_unitprice(apinvdtl.unitprice)
                apinvdtl_resp.set_quantity(apinvdtl.quantity)
                apinvdtl_resp.set_amount(apinvdtl.amount)
                apinvdtl_resp.set_discount(apinvdtl.discount)
                apinvdtl_resp.set_sgst(apinvdtl.sgst)
                apinvdtl_resp.set_cgst(apinvdtl.cgst)
                apinvdtl_resp.set_igst(apinvdtl.igst)
                apinvdtl_resp.set_taxamount(apinvdtl.taxamount)
                apinvdtl_resp.set_totalamount(apinvdtl.totalamount)
                apinvdtl_resp.set_otheramount(apinvdtl.otheramount)
                apinvdtl_resp.set_roundoffamt(apinvdtl.roundoffamt)

                apinvdtl_resp.set_is_capitalized(self.boolean_conver_to_number(apinvdtl.is_capitalized))
                apinvdtl_resp.set_entry_flag(self.boolean_conver_to_number(apinvdtl.entry_flag))
                apinvdtl_resp.apdebit=(apdebt_serv.get_apdebit_invoicedetails_list(request,apinvdtl.id,emp_id))
                apinvdtl_list.append(json.loads(apinvdtl_resp.get()))
        return apinvdtl_list

    def fetch_apinvoicedetails(self, request, apinvhdr_id):
        print('apinvhdr_id ',apinvhdr_id)

        apinvdtl_data = APInvoicedetail.objects.using(self._current_app_schema()).filter(apinvoiceheader_id=apinvhdr_id,
                                                                entity_id=self._entity_id(), status=1,is_delete=0)
        print('apinvdtl_data ',len(apinvdtl_data))

        apinvdtl_list = NWisefinList()
        if len(apinvdtl_data) > 0:
            for apinvdtl in apinvdtl_data:
                from utilityservice.service import api_service
                api_serv = api_service.ApiService(self._scope())

                try:
                    if apinvdtl.hsn not in ['',' ',None,0,"0"]:
                        hsn = api_serv.get_hsn_code(request, apinvdtl.hsn)
                        if type(hsn) != type(dict()) and  "description" in hsn.get():
                            hsn = {"Status": "Failed", "Message": "Invalid hsn code -" + str(apinvdtl.hsn)}
                    else:
                        hsn={ "Status":"Failed","Message":"Invalid hsn code- "  + str(apinvdtl.hsn) }
                except:
                    hsn={ "Status":"Failed","Message":"Invalid hsn code - " + str(apinvdtl.hsn) }


                apinvdtl_resp = APInvoiceDetailsResponse()
                apinvdtl_resp.set_id(apinvdtl.id)
                apinvdtl_resp.set_otheramount(apinvdtl.otheramount)
                apinvdtl_resp.set_roundoffamt(apinvdtl.roundoffamt)
                apinvdtl_resp.set_apinvoiceheader(apinvdtl.apinvoiceheader_id)
                apinvdtl_resp.set_apinvoice_po(apinvdtl.apinvoice_po)
                apinvdtl_resp.set_productcode(apinvdtl.productcode)
                apinvdtl_resp.set_productname(apinvdtl.productname)
                apinvdtl_resp.set_description(apinvdtl.description)
                apinvdtl_resp.set_hsn(hsn)
                apinvdtl_resp.set_hsn_percentage(apinvdtl.hsn_percentage)
                apinvdtl_resp.set_uom({"uom": apinvdtl.uom, "apinvdtl_id": apinvdtl.id})
                apinvdtl_resp.set_unitprice(apinvdtl.unitprice)
                apinvdtl_resp.set_quantity(apinvdtl.quantity)
                apinvdtl_resp.set_amount(apinvdtl.amount)
                apinvdtl_resp.set_discount(apinvdtl.discount)
                apinvdtl_resp.set_sgst(apinvdtl.sgst)
                apinvdtl_resp.set_cgst(apinvdtl.cgst)
                apinvdtl_resp.set_igst(apinvdtl.igst)
                apinvdtl_resp.set_taxamount(apinvdtl.taxamount)
                apinvdtl_resp.set_totalamount(apinvdtl.totalamount)

                apinvdtl_resp.set_is_capitalized(self.boolean_conver_to_number(apinvdtl.is_capitalized))
                apinvdtl_resp.set_entry_flag(self.boolean_conver_to_number(apinvdtl.entry_flag))
                apinvdtl_list.append(apinvdtl_resp)
        return apinvdtl_list

    def boolean_conver_to_number(self,boolean_value):
        if boolean_value == True :
            return 1
        else:
            return 0

    def fetch_apinvoicedetails_single(self,apinvoicedtls_id):
        apinvdtl = APInvoicedetail.objects.using(self._current_app_schema()).get(id=apinvoicedtls_id,
                                                                entity_id=self._entity_id(),status=1,is_delete=0)
        return apinvdtl

    def get_apinvoicedetails_single(self, request, apinvoicedtls_id):
        try:
            apinvdtl = APInvoicedetail.objects.using(self._current_app_schema()).get(id=apinvoicedtls_id,
                                                                entity_id=self._entity_id(),status=1,is_delete=0)
            from utilityservice.service import api_service
            from utilityservice.service.ap_api_service import APApiService
            api_serv = api_service.ApiService(self._scope())
            ap_api_serv=APApiService(self._scope())

            try:
                if apinvdtl.hsn not in ['', ' ', None, 0, "0"]:
                    hsn = api_serv.get_hsn_code(request, apinvdtl.hsn)
                    if type(hsn) != type(dict()) and "description" in hsn.get():
                        hsn = {"Status": "Failed", "Message": "Invalid hsn code -" + str(apinvdtl.hsn)}
                else:
                    hsn = {"Status": "Failed", "Message": "Invalid hsn code- " + str(apinvdtl.hsn)}
            except:
                hsn = {"Status": "Failed", "Message": "Invalid hsn code - " + str(apinvdtl.hsn)}

            apinvdtl_resp = APInvoiceDetailsResponse()
            apinvdtl_resp.set_id(apinvdtl.id)
            apinvdtl_resp.set_apinvoiceheader(apinvdtl.apinvoiceheader_id)
            apinvdtl_resp.set_apinvoice_po(apinvdtl.apinvoice_po)
            apinvdtl_resp.set_productcode(apinvdtl.productcode)
            apinvdtl_resp.set_productcode_details(ap_api_serv.fetch_product_using_productcode(apinvdtl.productcode))
            apinvdtl_resp.set_productname(apinvdtl.productname)
            apinvdtl_resp.set_description(apinvdtl.description)
            apinvdtl_resp.set_hsn(hsn)
            apinvdtl_resp.set_hsn_percentage(apinvdtl.hsn_percentage)
            apinvdtl_resp.set_uom({"uom": apinvdtl.uom, "apinvdtl_id": apinvdtl.id})
            apinvdtl_resp.set_unitprice(apinvdtl.unitprice)
            apinvdtl_resp.set_quantity(apinvdtl.quantity)
            apinvdtl_resp.set_amount(apinvdtl.amount)
            apinvdtl_resp.set_discount(apinvdtl.discount)
            apinvdtl_resp.set_sgst(apinvdtl.sgst)
            apinvdtl_resp.set_cgst(apinvdtl.cgst)
            apinvdtl_resp.set_igst(apinvdtl.igst)
            apinvdtl_resp.set_taxamount(apinvdtl.taxamount)
            apinvdtl_resp.set_totalamount(apinvdtl.totalamount)
            apinvdtl_resp.set_is_capitalized(self.boolean_conver_to_number(apinvdtl.is_capitalized))
            apinvdtl_resp.set_entry_flag(self.boolean_conver_to_number(apinvdtl.entry_flag))
            return apinvdtl_resp

        except Exception  as excep:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

    def apinvoicedetails_delete(self,apinvoicedetails_id,emp_id):
        try:
            apcredit = APInvoicedetail.objects.using(self._current_app_schema()).filter(id=apinvoicedetails_id,
                                                            entity_id=self._entity_id(),is_delete=0).update(
                                    is_delete=1,updated_by=emp_id,updated_date=now())

            from apservice.service.apdebitservice import APDebitService
            apdebt_serv = APDebitService(self._scope())
            apdebit_delete=apdebt_serv.apdebit_delete_using_apinvoicedetail_id(apinvoicedetails_id,emp_id)
            print('apdebit_delete ',apdebit_delete)

            if apcredit == 0:
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
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj



    def apinvoicedetails_entryflag_update(self,apinvoicedetails_id,entry_flag,emp_id):
        try:
            apcredit = APInvoicedetail.objects.using(self._current_app_schema()).filter(id=apinvoicedetails_id,
                                entity_id=self._entity_id()).update(entry_flag=entry_flag,
                                                            updated_by=emp_id,updated_date=now())

            if apcredit == 0:
                error_obj = NWisefinError()
                error_obj.set_code('INVALID_INVOICEDETAILS_ID')
                error_obj.set_description('INVALID INVOICEDETAILS ID')
                return error_obj
            else:
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                return success_obj

        except Exception as excep:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj




    # def apinwardinvdtl_create(self,apinvdtl_obj,apinwardinvhdr_id,emp_id):
    #     if not apinvdtl_obj.get_id() is None:
    #         apinvdtl_update = APInwardInvoicedetail.objects.using(self._current_app_schema()).filter(id=apinvdtl_obj.get_id()).update(
    #             apinwardinvoiceheader=apinwardinvhdr_id,
    #             mepno=apinvdtl_obj.get_mepno(),
    #             productcode=apinvdtl_obj.get_productcode(),
    #             productname=apinvdtl_obj.get_productname(),
    #             description=apinvdtl_obj.get_description(),
    #             hsn=apinvdtl_obj.get_hsn(),
    #             hsn_percentage=apinvdtl_obj.get_hsn_percentage(),
    #             uom=apinvdtl_obj.get_uom(),
    #             unitprice=apinvdtl_obj.get_unitprice(),
    #             quantity=apinvdtl_obj.get_quantity(),
    #             amount=apinvdtl_obj.get_amount(),
    #             discount=apinvdtl_obj.get_discount(),
    #             sgst=apinvdtl_obj.get_sgst(),
    #             cgst=apinvdtl_obj.get_cgst(),
    #             igst=apinvdtl_obj.get_igst(),
    #             taxamount=apinvdtl_obj.get_taxamount(),
    #             totalamount=apinvdtl_obj.get_totalamount(),
    #             updated_by=emp_id,
    #             updated_date=now())
    #         apinvdtl = APInvoicedetail.objects.using(self._current_app_schema()).get(id=apinvdtl_obj.get_id())
    #         self.audit_function(apinvdtl, apinvdtl.id, apinvdtl.id, emp_id,
    #                             APModifyStatus.UPDATE, APRefType.APINVOICEDETAIL)
    #
    #     else:
    #         apinvdtl = APInvoicedetail.objects.using(self._current_app_schema()).create(
    #             apinvoiceheader_id=apinwardinvhdr_id,
    #             mepno=apinvdtl_obj.get_mepno(),
    #             productcode=apinvdtl_obj.get_productcode(),
    #             productname=apinvdtl_obj.get_productname(),
    #             description=apinvdtl_obj.get_description(),
    #             hsn=apinvdtl_obj.get_hsn(),
    #             hsn_percentage=apinvdtl_obj.get_hsn_percentage(),
    #             uom=apinvdtl_obj.get_uom(),
    #             unitprice=apinvdtl_obj.get_unitprice(),
    #             quantity=apinvdtl_obj.get_quantity(),
    #             amount=apinvdtl_obj.get_amount(),
    #             discount=apinvdtl_obj.get_discount(),
    #             sgst=apinvdtl_obj.get_sgst(),
    #             cgst=apinvdtl_obj.get_cgst(),
    #             igst=apinvdtl_obj.get_igst(),
    #             taxamount=apinvdtl_obj.get_taxamount(),
    #             totalamount=apinvdtl_obj.get_totalamount(),
    #             created_by=emp_id)
    #
    #         self.audit_function(apinvdtl, apinvdtl.id, apinvdtl.id, emp_id,
    #                             APModifyStatus.CREATE, APRefType.APINVOICEDETAIL)
    #
    #
    #     apindtl_data = APInvoiceDetailsResponse()
    #     apindtl_data.set_id(apinvdtl.id)
    #     apindtl_data.set_apinvoiceheader(apinvdtl.apinvoiceheader_id)
    #     apindtl_data.set_apinvoice_po(apinvdtl.apinvoice_po)
    #     apindtl_data.set_mepno(apinvdtl.mepno)
    #     apindtl_data.set_productcode(apinvdtl.productcode)
    #     apindtl_data.set_productname(apinvdtl.productname)
    #     apindtl_data.set_description(apinvdtl.description)
    #     apindtl_data.set_hsn(apinvdtl.hsn)
    #     apindtl_data.set_hsn_percentage(apinvdtl.hsn_percentage)
    #     apindtl_data.set_uom(apinvdtl.uom)
    #     apindtl_data.set_unitprice(apinvdtl.unitprice)
    #     apindtl_data.set_quantity(apinvdtl.quantity)
    #     apindtl_data.set_amount(apinvdtl.amount)
    #     apindtl_data.set_discount(apinvdtl.discount)
    #     apindtl_data.set_sgst(apinvdtl.sgst)
    #     apindtl_data.set_cgst(apinvdtl.cgst)
    #     apindtl_data.set_igst(apinvdtl.igst)
    #     apindtl_data.set_taxamount(apinvdtl.taxamount)
    #     apindtl_data.set_totalamount(apinvdtl.totalamount)
    #     return apindtl_data
    #

    def fetch_apinvdtl_product_details(self,request,apinvdtl_id):

        apinvdtl_data = APInvoicedetail.objects.using(self._current_app_schema()).filter(id=apinvdtl_id,
                                                                    status=1,is_delete=0,entity_id=self._entity_id())

        productcode=apinvdtl_data.productcode