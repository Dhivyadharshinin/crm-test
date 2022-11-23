import json
import sys
import traceback
from datetime import datetime

from django.db.models import Q
from django.utils.timezone import now


from apservice.data.response.apauditresponse import APAuditResponse
from apservice.data.response.apheaderresponse import APQueueResponse
from apservice.models import APAuditChecklistMapping, APAuditChecklist, APHeader, APInvoiceHeader, APInvoicedetail, \
    APDebit, APCredit, APQueue, APCCBSDetails, APSegment_Vendor_Identifier
from apservice.service.apauditservice import APAuditService

from apservice.util.aputil import get_APType, APModifyStatus, APRefType, APRequestStatusUtil, ap_post_api_caller, \
    get_audit_checklist_value, AP_Status, get_apstatus, ap_get_api_caller, get_AP_status, audit_checklist_value
from apservice.data.request.apcreditrequest import APCreditRequest
from apservice.data.request.apinvoicedetailrequest import APInvoiceDetailsRequest, APDebitRequest, APccbsDetailsRequest
from apservice.data.request.apinvoiceheaderrequest import APInvoiceheaderrequest
from apservice.service.apcreditservice import APCreditService
from apservice.service.apdebitservice import APDebitService
from apservice.service.apinvoicedetailsservice import APInvoiceDetailService
import requests
from django.db import transaction
from apservice.data.request.apheaderrequest import APHeaderRequest
from nwisefin.settings import logger, SERVER_IP
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.permissions.filter.commonpermission import ModulePermission
from utilityservice.permissions.util.dbutil import RoleList, ModuleList
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class APService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.AP_SERVICE)

    def ap_create(self, request, ap_data, emp_id):
        try:
            with transaction.atomic(using=self._current_app_schema()):
                direct_entry=False
                from apservice.service.apinvoiceheaderservice import APInvoiceheaderService
                from apservice.service.apheaderservice import APHeaderService
                ecf_json = self.call_ecfapi_for_data(request, ap_data['crno'])
                logger.info('ecf_json')
                logger.info(json.dumps(ecf_json))
                # Create AP Header ***
                ap_obj = APHeaderRequest(ecf_json,direct_entry)
                ap_service = APHeaderService(self._scope())
                response_obj = ap_service.apheader_create(request, ap_data, ap_obj, emp_id)
                # Create APInvoice Header ***
                ecftype_id=ecf_json['ecftype_id']

                for apinvhdr_json in ecf_json['Invheader']:
                    apfile_data = None
                    del apinvhdr_json['id']
                    apinvhdr_obj = APInvoiceheaderrequest(apinvhdr_json)
                    apinvhdr_serv = APInvoiceheaderService(self._scope())
                    if 'file_data' in apinvhdr_json:
                        if apinvhdr_json['file_data'] is not None and len(apinvhdr_json['file_data']) > 0:
                            apfile_data=apinvhdr_json['file_data']
                    apinvhdr_response = apinvhdr_serv.apinvhdrcreate(request,apfile_data,apinvhdr_json,apinvhdr_obj, response_obj.id, emp_id)
                    #Create APInvoice Details ***
                    apinvdtls_id=None
                    if 'invoicedtl' in apinvhdr_json:
                        for invdtl_json in apinvhdr_json['invoicedtl']:
                            invdtl_id = invdtl_json['id']
                            del invdtl_json['id']
                            if int(ecftype_id) == 4:
                                prdct_data = self.change_product_for_advance_case()
                                invdtl_json['productcode']=prdct_data[0]
                                invdtl_json['productname']=prdct_data[1]
                            apinvdtls_obj = APInvoiceDetailsRequest(invdtl_json)
                            apinvdtls_serv = APInvoiceDetailService(self._scope())
                            apinvdtls_resp = apinvdtls_serv.apinvdtl_create(apinvdtls_obj, apinvhdr_response.id, emp_id)
                            apinvdtls_id=apinvdtls_resp.id
                            print('apinvdtls_id ',apinvdtls_id)
                            #apinwardinvdtl_resp=apinvdtls_serv.apinwardinvdtl_create(apinvdtls_obj,apiwdinvhdr_resp.id,emp_id)
                            # Create AP Debit ***
                            if 'debit' in apinvhdr_json:
                                for debit_json in apinvhdr_json['debit']:
                                    if invdtl_id != debit_json['invoicedetail']:
                                        continue
                                    else:
                                        del debit_json['id']
                                        debit_obj = APDebitRequest(debit_json,direct_entry)
                                        apdebit_serv = APDebitService(self._scope())
                                        print('apinvdtls_id1',apinvdtls_id)
                                        apdebit_resp = apdebit_serv.apdebit_create(debit_obj, apinvhdr_response.id, apinvdtls_id,emp_id)
                                        # Create AP CCBS ***
                                        ccbs_json = debit_json['ccbs']
                                        del ccbs_json['id']
                                        apinvdtls_serv = APInvoiceDetailService(self._scope())
                                        apccbsdebit_obj = APccbsDetailsRequest(ccbs_json)
                                        apccbs_resp = apinvdtls_serv.apccbs_create(apccbsdebit_obj, apdebit_resp.id, emp_id)
                    # Create AP Credit ***
                    if 'credit' in apinvhdr_json:
                        for apcredit_json in apinvhdr_json['credit']:
                            del apcredit_json['id']
                            manual=False
                            apcredit_obj = APCreditRequest(apcredit_json,manual)
                            apcredit_serv = APCreditService(self._scope())
                            apcredit_resp = apcredit_serv.apcredit_create(apcredit_obj, apinvhdr_response.id, emp_id)

                aphdr_serv = APHeaderService(self._scope())
                invhdr_count = aphdr_serv.get_pocket_apinvoiceheader_count(ap_data['inwarddetails_id'])
                api_json = {"api_url": '/inwdserv/inwardstatus_update', "inwarddetails_id": ap_data['inwarddetails_id']}
                api_json['status_id'] = 4
                logger.info(int(invhdr_count) == int(ap_data['invoice_count']))
                logger.info(str(invhdr_count)+"  "+str(ap_data['invoice_count']))
                logger.info('ap_data 123#$%   ' +str(ap_data['inwarddetails_id']))
                if int(invhdr_count) == int(ap_data['invoice_count']):
                    api_json['status_id'] = 4

                inwardstatusupdate_resp = ap_post_api_caller(request, api_json)
                logger.info('inwardstatusupdate_resp '+str(inwardstatusupdate_resp))
                ecfstatus_update_json = {"api_url": '/ecfserv/apupdate',"crno": ap_data['crno'], "ap_status": "WIP"}
                ecfstatus_update_resp = ap_post_api_caller(request, ecfstatus_update_json)
                logger.info('ecfstatus_update_resp ' + str(ecfstatus_update_resp))
                print('ecfstatus_update_resp ' , str(ecfstatus_update_resp))

                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                success_obj.apheader_id=(response_obj.id)
                return success_obj
        except Exception  as excep:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep)+" - "+ str(filename)+", line_no : "+str(line_number)+str(', exception_type : {c} '.format(c=type(excep).__name__)))
            return error_obj

    def change_product_for_advance_case(self,):
        from utilityservice.service.ap_api_service import APApiService
        ap_api_serv = APApiService(self._scope())
        product_data = ap_api_serv.fetch_first_prodct()
        return product_data['code'],product_data['name']

    def map_apaudit_checklist(self, auditchcklist_data, emp_id):
        try:
            for auditchk in auditchcklist_data['auditchecklist']:
                if 'id' in auditchk:
                    apaudit_update = APAuditChecklistMapping.objects.using(self._current_app_schema()).filter(
                        id=auditchk['id'], entity_id=self._entity_id()).update(
                        value=auditchk['value'],
                        updated_date=now(),
                        updated_by=emp_id)
                    apaudit = APAuditChecklistMapping.objects.using(self._current_app_schema()).get(id=auditchk['id'],
                                                                                                    entity_id=self._entity_id())
                    self.audit_function(apaudit, apaudit.id, apaudit.id, emp_id, APModifyStatus.UPDATE,
                                        APRequestStatusUtil.ONBORD, APRefType.APAUDITCHECKLIST_MAP,
                                        APRefType.APAUDITCHECKLIST_MAP)
                else:

                    apaudit = APAuditChecklistMapping.objects.using(self._current_app_schema()).create(
                        apauditchecklist_id=auditchk['apauditchecklist_id'],
                        apinvoiceheader_id=auditchk['apinvoiceheader_id'],
                        value=auditchk['value'],
                        created_by=emp_id, entity_id=self._entity_id())
                    self.audit_function(apaudit, apaudit.id, apaudit.id, emp_id, APModifyStatus.CREATE,
                                        APRequestStatusUtil.ONBORD, APRefType.APAUDITCHECKLIST_MAP,
                                        APRefType.APAUDITCHECKLIST_MAP)

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return success_obj
        except Exception as excep:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

    def make_apauditchecklist(self, auditchcklist_json, emp_id):
        try:
            if 'id' in auditchcklist_json:
                apaudit_update = APAuditChecklist.objects.using(self._current_app_schema()).filter(
                    id=auditchcklist_json['id'], entity_id=self._entity_id()).update(
                    type=auditchcklist_json['type_id'],
                    group=auditchcklist_json['group'],
                    question=auditchcklist_json['question'],
                    solution=auditchcklist_json['solution'],
                    updated_by=emp_id,
                    updated_date=now())
                apaudit = APAuditChecklist.objects.using(self._current_app_schema()).get(id=auditchcklist_json['id'],
                                                                                         entity_id=self._entity_id())
                self.audit_function(apaudit, apaudit.id, apaudit.id, emp_id, APModifyStatus.CREATE,
                                    APRequestStatusUtil.ONBORD, APRefType.APAUDITCHECKLIST, APRefType.APAUDITCHECKLIST)
            else:
                apaudit = APAuditChecklist.objects.using(self._current_app_schema()).create(
                    type=auditchcklist_json['type_id'],
                    group=auditchcklist_json['group'],
                    question=auditchcklist_json['question'],
                    solution=auditchcklist_json['solution'],
                    created_by=emp_id, entity_id=self._entity_id())
                apaudit.code = 'CH' + str(apaudit.id)
                apaudit.save()
                self.audit_function(apaudit, apaudit.id, apaudit.id, emp_id, APModifyStatus.UPDATE,
                                    APRequestStatusUtil.ONBORD, APRefType.APAUDITCHECKLIST, APRefType.APAUDITCHECKLIST)

            apaudit = apaudit.__dict__
            del apaudit['created_date'], apaudit['updated_date'], apaudit['updated_by']

            return json.dumps(apaudit, default=lambda o: o.__dict__,
                              sort_keys=True, indent=4)
        except Exception as excep:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj.get()

    def get_apaudit_checklist(self, aptype_id, emp_id):
        try:
            apaudit_data = APAuditChecklist.objects.using(self._current_app_schema()).filter(type=aptype_id,
                                                                                             is_delete=0,
                                                                                             entity_id=self._entity_id())
            resp_list = NWisefinList()
            if len(apaudit_data) > 0:
                for apaudit in apaudit_data:
                    return_json = {"id": apaudit.id, "type": get_APType(apaudit.type), "group": apaudit.group,
                                   "question": apaudit.question, "solution": apaudit.solution,"value":audit_checklist_value.OK}
                    resp_list.append(return_json)

            return resp_list
        except Exception as excep:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

    def get_bounce_apauditchecklist(self, apinvoiceheader_id, emp_id):
        try:
            apaudit_data = APAuditChecklistMapping.objects.using(self._current_app_schema()).filter(
                apinvoiceheader_id=apinvoiceheader_id,
                apauditchecklist__is_delete=0, entity_id=self._entity_id())
            resp_list = NWisefinList()
            if len(apaudit_data) > 0:
                for bounce_audit in apaudit_data:
                    apaudit = bounce_audit.apauditchecklist
                    return_json = {"id": bounce_audit.id, "type": get_APType(apaudit.type), "group": apaudit.group,
                                   "apauditchecklist_id": apaudit.id,
                                   "question": apaudit.question, "solution": apaudit.solution,
                                   "value": get_audit_checklist_value(bounce_audit.value)}
                    resp_list.append(return_json)

            return resp_list
        except Exception as excep:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

    def audit_function(self, audit_data, refid, relrefid, emp_id, action, reqstatus, reftype, relreftype):
        if action == APModifyStatus.DELETE:
            data = None
        else:
            data = audit_data.__dict__
            del data['_state']
        audit_service = APAuditService(self._scope())
        audit_obj = APAuditResponse()
        audit_obj.set_refid(refid)
        audit_obj.set_reqstatus(reqstatus)
        audit_obj.set_reftype(reftype)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(relreftype)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)

    def call_ecfapi_for_data(self, request, crno):
        token_name = request.headers['Authorization']
        # url = SERVER_IP 'http://143.110.244.51:8000' + '/ecfserv/get_ecf/' + str(ecf_data['ecfhdr_id'])
        url = SERVER_IP + '/ecfserv/get_ecfno/' + str(crno)
        logger.info("ecfserv  url: " + str(url))
        logger.info("ecfserv  url: " + str(url))
        headers = {"content-type": "application/json", "Authorization": "" + token_name + ""}
        ecf_resp = requests.get(url, headers=headers, verify=False)
        logger.info('ecf_resp', ecf_resp)
        logger.info('ecf_resp', ecf_resp.text)
        logger.info('ecf_resp', ecf_resp.content)
        ecf_json = json.loads(ecf_resp.content)
        del ecf_json['id']
        return ecf_json

    def apfinal_submit_status_validation(self,apheader_id):
        apinvhdr = APInvoiceHeader.objects.using(self._current_app_schema()).filter(
            apheader_id=apheader_id, entity_id=self._entity_id())[0]
        if int(apinvhdr.status) not in [AP_Status.NEW, AP_Status.RE_AUDIT]:
            ap_status=get_AP_status(apinvhdr.status)
            apstatus_json = json.loads(ap_status.get())
            success_obj = NWisefinSuccess()
            success_obj.set_status("Failed")
            success_obj.set_message("This AP in '" + str(apstatus_json.get('text')) +  "' status")
            return success_obj
        else:
            return False

    def from_bank_validation(self,ap_dict):
        apinvhdrlist = APInvoiceHeader.objects.using(self._current_app_schema()).filter(
            apheader_id=ap_dict['apheader_id'],
            entity_id=self._entity_id(), status=AP_Status.NEW, is_delete=0)
        for apinvobj in apinvhdrlist:
            if (apinvobj.bankdetails_id is None):
                success_obj = NWisefinSuccess()
                success_obj.set_status("Failed")
                success_obj.set_message("Kindly provide from bank in credit page")
                return success_obj
        return False


    def apfinal_submit(self, request, ap_dict, emp_id):
        try:
            with transaction.atomic(using=self._current_app_schema()):
                aphdr_data = APHeader.objects.using(self._current_app_schema()).get(id=ap_dict['apheader_id'],
                                                                                    is_delete=0,
                                                                                    entity_id=self._entity_id())
                apytpe = int(aphdr_data.aptype)
                if apytpe == 1:
                    code = "ECF"
                elif apytpe == 2:
                    code = "NPO"
                elif apytpe == 3:
                    code = "BCF"
                elif apytpe == 4:
                    code = "PPX"
                elif apytpe == 5:
                    code = "DTP"
                elif apytpe == 8:
                    code = "TCF"

                frombank_val=self.from_bank_validation(ap_dict)
                if frombank_val:
                    return frombank_val

                apinvoice_detail = APInvoicedetail.objects.using(self._current_app_schema()).filter(
                    apinvoiceheader__apheader_id=ap_dict['apheader_id'],status=AP_Status.NEW, is_delete=0,
                    entity_id=self._entity_id())[0]


                from utilityservice.service.ap_api_service import APApiService
                ap_api_serv = APApiService(self._scope())
                product_details=ap_api_serv.fetch_product_using_productcode(apinvoice_detail.productcode)
                print('product_details ', product_details)
                print('product_details ', type(product_details))
                if 'product_isrcm' not in product_details:
                    success_obj = NWisefinSuccess()
                    success_obj.set_status("Failed")
                    success_obj.set_message("Please check Product Name in invoice details")
                    return success_obj

                print('product_isrcms ', product_details['product_isrcm'] )

                if aphdr_data.crno is None :
                    crno = code + str(datetime.now().strftime("%y%m%d")) + str(ap_dict['apheader_id']).zfill(4)
                if str(product_details['product_isrcm'])=='Y':
                    is_rcm_true=self.product_is_rcm_true(ap_dict, emp_id,request)
                    if is_rcm_true != True:
                        return is_rcm_true
                    print('is_rcm_true ',is_rcm_true)
                else:
                    is_rcm_false=self.product_is_rcm_false(request, aphdr_data, ap_dict, apytpe, emp_id)
                    print('is_rcm_false ', is_rcm_false)
                    if is_rcm_false != True:
                        return is_rcm_false



                if aphdr_data.crno is None :
                    aphdr = APHeader.objects.using(self._current_app_schema()).filter(id=ap_dict['apheader_id'],
                                                                                      entity_id=self._entity_id()).update(
                        # approvedby=ap_dict['approved_by'],
                        # approvername=appr_name,
                        # approver_branch=ap_dict['approver_branch'],
                        # tds=ap_dict['tds'],
                        # aptype=ap_dict['aptype'],
                        crno=crno,
                        remark=ap_dict.get('remarks'),
                        status=AP_Status.PENDING_FOR_APPROVAL,
                        updated_by=emp_id,
                        updated_date=now())

                apinvhdr = APInvoiceHeader.objects.using(self._current_app_schema()).filter(
                    apheader_id=ap_dict['apheader_id'], entity_id=self._entity_id()).update(
                    status=AP_Status.PENDING_FOR_APPROVAL,
                    updated_by=emp_id,
                    updated_date=now())

                apinvhdr_data = APInvoiceHeader.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(), apheader_id=ap_dict['apheader_id'])

                queue_dict = {"ref_id": aphdr_data.id, "ref_type": APRefType.APHEADER,
                              "remarks": ap_dict.get('remarks'),
                              "from_user_id": emp_id, "status": AP_Status.PENDING_FOR_APPROVAL,
                              "to_user_id": -1, "comments": "PENDING FOR APPROVAL"}
                self.create_apqueue(queue_dict)

                for apinv_hdr in apinvhdr_data:
                    queue_dict = {"ref_id": apinv_hdr.id, "ref_type": APRefType.APINVOICEHEADER,
                                  "remarks": ap_dict.get('remarks'),
                                  "from_user_id": emp_id, "status": AP_Status.PENDING_FOR_APPROVAL,
                                  "to_user_id": -1, "comments": "PENDING FOR APPROVAL"}
                    self.create_apqueue(queue_dict)

                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                #Mail_Trigger**
                #mails_status=self.mail_to_apapprover(request,emp_id,aphdr_data)
                #success_obj.set_message(SuccessMessage.UPDATE_MESSAGE + mails_status)
                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE )
                return success_obj

        except Exception as excep:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            traceback.print_exc()
            success_obj = NWisefinSuccess()
            success_obj.set_status("Failed")
            success_obj.set_message(str(excep) +" - " +str(filename)+",line_no : "+str(line_number)+str(', exception_type : {c} '.format(c=type(excep).__name__)))
            return success_obj

    def mail_to_apapprover(self,request,emp_id,aphdr_data):
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
            maker = api_serv.get_empsingle_id(request, aphdr_data)
            maker_name = maker['name']
            maker_email_id = maker['email']
            approver = api_serv.get_empsingle_id(request, aphdr_data.raisedby)
            approver_name = approver['name']
            approver_email_id = approver['email']
            print("approver_email_id", approver_email_id)
            template = loader.get_template("ecfraiser.html")
            name = approver_name
            subject = "Vendor payment request raised by Raiser"
            m_id = emp_id
            cc = [maker_email_id]
            to = [approver_email_id]#{'saravanarajselvam0@gmail.com','saravanarajselvam0@gmail.com'}

            from1 = From_url
            email = to
            msg = MIMEMultipart('alternative')
            maker_subject = subject
            cc = maker_email_id
            referenceno = aphdr_data.crno
            raiseddate = aphdr_data.created_date
            amount = aphdr_data.apamount
            ecftype = aphdr_data.aptype
            data = {"emp_name": name,
                    "id": m_id,
                    "server_ip": BASE_URL,
                    "subject": subject,
                    "cc": cc,
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
            # msd2 = ','.join(to)
            # msg1 = ','.join(cc)
            # toAddress =  msd2
            msg.attach(part1)
            msg['Subject'] = "Vendor payment request raised by Raiser"
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
            return ", Mail Not Sent"



    def product_is_rcm_false(self,request,aphdr_data,ap_dict,apytpe, emp_id):

        apamount = round(float(aphdr_data.apamount), 2)
        apinvhdr_list = APInvoiceHeader.objects.using(self._current_app_schema()).filter(
            apheader_id=ap_dict['apheader_id'],
            entity_id=self._entity_id(), status__in=[AP_Status.NEW,AP_Status.RE_AUDIT], is_delete=0)
        apinvheadertotal = float(0)
        for apinv_obj in apinvhdr_list:
            apinvheadertotal = round(apinvheadertotal + apinv_obj.totalamount, 2)

        if (apamount != apinvheadertotal):
            success_obj = NWisefinSuccess()
            success_obj.set_status("Failed")
            success_obj.set_message("APinvoice header amount mismatch. "+"APHeader_amt: " +str(apamount)+", ApInvoicehdr_amt "+str(apinvheadertotal))
            return success_obj
        for apinvhdr_obj in apinvhdr_list:
            apinvhdr_totalamt = float(apinvhdr_obj.totalamount)
            apinvhdr_id = apinvhdr_obj.id
            if apytpe != 4:
                apinvdtl_list = APInvoicedetail.objects.using(self._current_app_schema()).filter(
                    apinvoiceheader_id=apinvhdr_id,
                    status=AP_Status.NEW, is_delete=0, entity_id=self._entity_id())
                apinvdtl_total = float(0)
                for apinvdtl_obj in apinvdtl_list:
                    apinvdtl_total = round((apinvdtl_total + apinvdtl_obj.totalamount + float(apinvdtl_obj.roundoffamt)),2)
                if (apinvhdr_totalamt != apinvdtl_total):
                    success_obj = NWisefinSuccess()
                    success_obj.set_status("Failed")
                    success_obj.set_message("APinvoice details amount mismatch. " +"APInvoicehdr_amt: " +str(apinvhdr_totalamt)+", ApInvoicedtls_amt "+str(apinvdtl_total))
                    return success_obj
                for apinvdtl_obj in apinvdtl_list:
                    # entry_debit_validation
                    entry_debitvalid = self.is_entry_debit_validation(apinvhdr_id)
                    if entry_debitvalid != False:
                        return entry_debitvalid
                    #apinvdtl_id = apinvdtl_obj.id
                    print('apinvoiceheader_id for debit ' ,apinvhdr_id)
                    codition=Q(apinvoiceheader_id=apinvhdr_id,status=AP_Status.NEW, is_delete=0,
                               entity_id=self._entity_id())&~Q(amount=0)

                    apdebit_list = APDebit.objects.using(self._current_app_schema()).filter(codition)
                    apdebit_total = float(0)
                    for deb_obj in apdebit_list:
                        debit_val=self.debit_validation(deb_obj)
                        if debit_val != False:
                            return debit_val
                        # APCCBS Validation
                        print('Debit_id For CCBS ',deb_obj.id)
                        apccbsdtls_data = APCCBSDetails.objects.using(self._current_app_schema()).filter(
                            apdebit_id=deb_obj.id, status=AP_Status.NEW, is_delete=0)
                        if len(apccbsdtls_data) == 0:
                            success_obj = NWisefinSuccess()
                            success_obj.set_status("Failed")
                            success_obj.set_message("Kindly provide each apdebit's CCBS")
                            return success_obj

                        debt_amount = round(deb_obj.amount, 2)
                        apdebit_total = round((apdebit_total + debt_amount) ,2)
                    #apdebit_total= apdebit_total + apinv_obj.otheramount

                    #if apinv_obj.roundoffamt > 0:
                    apdebit_total= round(apdebit_total + apinv_obj.roundoffamt,2)


                    print('apinvdtl_total',apinvdtl_total ,'apdebit_total', apdebit_total)
                    if (apinvdtl_total != apdebit_total):
                        success_obj = NWisefinSuccess()
                        success_obj.set_status("Failed")
                        success_obj.set_message("APdebit amount mismatch.  apdebit_amt : " +str(apdebit_total)+", apinvdtl_total : "+str(apinvdtl_total)+ ", apinvoicehdr_amt : "+str(apinvheadertotal) + ", apheaderamt : " + str(apamount))
                        return success_obj

            else:
                # entry_debit_validation
                # entry_debitvalid = self.is_entry_debit_validation(apinvhdr_id)
                # if entry_debitvalid != False:
                #     return entry_debitvalid
                apdebit_data = APDebit.objects.using(self._current_app_schema()).filter(
                    apinvoiceheader_id=apinvhdr_id,
                    entity_id=self._entity_id(), status=AP_Status.NEW, is_delete=0)
                debit_total = float(0)
                for deb_obj in apdebit_data:
                    #Debit APCat and APSubCat Validation
                    debit_total = debit_total + deb_obj.amount
                    debit_val = self.debit_validation(deb_obj)
                    if debit_val != False:
                        return debit_val
                    #APCCBS Validation
                    apccbsdtls_data=APCCBSDetails.objects.using(self._current_app_schema()).filter(apdebit_id=deb_obj.id,
                                                                       status=AP_Status.NEW,is_delete=0)
                    if len(apccbsdtls_data) == 0:
                        success_obj = NWisefinSuccess()
                        success_obj.set_status("Failed")
                        success_obj.set_message("Kindly provide each apdebit's CCBS")
                        return success_obj

                if (apinvhdr_totalamt != debit_total):
                    success_obj = NWisefinSuccess()
                    success_obj.set_status("Failed")
                    success_obj.set_message("APdebit amount mismatch.")
                    return success_obj
            print("apinvhdr_id123", apinvhdr_id)
            #entry_credit_validation
            entry_credit_valid=self.is_entry_credit_validation(apinvhdr_id)
            if entry_credit_valid != False:
                return entry_credit_valid

            apcredit_list = APCredit.objects.using(self._current_app_schema()).filter(
                apinvoiceheader_id=apinvhdr_id,entity_id=self._entity_id(), status=AP_Status.NEW, is_delete=0)
            credit_total = float(0)
            is_payable_paymode = False
            for apcrdt_obj in apcredit_list:
                from utilityservice.service.ap_api_service import APApiService
                ap_api_serv = APApiService(self._scope())
                era_paymode_detail = ap_api_serv.paymode_single_get_with_name("ERA")
                neft_paymode_detail = ap_api_serv.paymode_single_get_with_name("NEFT")
                era_paymod_id = int(era_paymode_detail['data'][0]['id'])
                neft_paymod_id = int(neft_paymode_detail['data'][0]['id'])
                if int(apcrdt_obj.paymode_id) in [era_paymod_id,neft_paymod_id] :
                    is_payable_paymode=True
                    is_valid_account=self.is_valid_account_details(request, apcrdt_obj, emp_id)
                    if is_valid_account != False:
                        return is_valid_account
                credit_total = round((credit_total + apcrdt_obj.amount + apinv_obj.otheramount), 2)
            if is_payable_paymode != True:
                success_obj = NWisefinSuccess()
                success_obj.set_status("Failed")
                success_obj.set_message("Payable Paymode Not in Credit Screen")
                return success_obj


            print('credit_total ', apinvhdr_totalamt, credit_total)
            if (apinvhdr_totalamt != credit_total):
                success_obj = NWisefinSuccess()
                success_obj.set_status("Failed")
                success_obj.set_message("apcredit amount mismatch. apinvoicehdr_amt :" +str(apinvhdr_totalamt) +" APcredit_amt : " +str(credit_total))
                return success_obj


        return True


    def product_is_rcm_true(self,ap_dict, emp_id,request):

        apinvoice_header= APInvoiceHeader.objects.using(self._current_app_schema()).filter(
            apheader_id=ap_dict['apheader_id'],
            entity_id=self._entity_id(), status=AP_Status.NEW, is_delete=0)[0]
        apinvhdr_id=apinvoice_header.id
        #entry_debit_validation
        entry_debitvalid = self.is_entry_debit_validation(apinvhdr_id)
        if entry_debitvalid != False:
            return entry_debitvalid

        condition=Q(apinvoiceheader_id=apinvhdr_id,entity_id=self._entity_id(),
                    status=AP_Status.NEW, is_delete=0)&~Q(amount=0)
        apdebit_data = APDebit.objects.using(self._current_app_schema()).filter(condition)
        debit_total = float(0)
        for deb_obj in apdebit_data:
            debit_val = self.debit_validation(deb_obj)
            if debit_val != False:
                return debit_val
            #APCCBS Validation
            print('deb_obj_id ',deb_obj.id)
            apccbsdtls_data = APCCBSDetails.objects.using(self._current_app_schema()).filter(apdebit_id=deb_obj.id,
                                                                            status=AP_Status.NEW,is_delete=0)
            print('len_apccbsdtls_data ',len(apccbsdtls_data))
            print('len_apccbsdtls_data ',len(apccbsdtls_data))
            if len(apccbsdtls_data) == 0:
                success_obj = NWisefinSuccess()
                success_obj.set_status("Failed")
                success_obj.set_message("Kindly provide each apdebit's CCBS")
                return success_obj
            debit_total = round((debit_total + deb_obj.amount +apinvoice_header.otheramount),2)
            print('debit_total, roundoffamt ',debit_total,apinvoice_header.roundoffamt)
        #if apinvoice_header.roundoffamt > 0:
        debit_total = round(debit_total + apinvoice_header.roundoffamt, 2)

        print("apinvhdr_id123", apinvhdr_id)
        # entry_credit_validation
        entry_credit_valid = self.is_entry_credit_validation(apinvhdr_id)
        if entry_credit_valid != False:
            return entry_credit_valid
        apcredit_list = APCredit.objects.using(self._current_app_schema()).filter(
            apinvoiceheader_id=apinvhdr_id,
            entity_id=self._entity_id(), status=AP_Status.NEW, is_delete=0)
        credit_total = float(0)
        is_payable_paymode = False
        for apcrdt_obj in apcredit_list:
            from utilityservice.service.ap_api_service import APApiService
            ap_api_serv = APApiService(self._scope())
            era_paymode_detail = ap_api_serv.paymode_single_get_with_name("ERA")
            neft_paymode_detail = ap_api_serv.paymode_single_get_with_name("NEFT")
            era_paymod_id = int(era_paymode_detail['data'][0]['id'])
            neft_paymod_id = int(neft_paymode_detail['data'][0]['id'])
            if int(apcrdt_obj.paymode_id) in [era_paymod_id, neft_paymod_id]:
                is_payable_paymode = True
                is_valid_account = self.is_valid_account_details(request, apcrdt_obj, emp_id)
                if is_valid_account != False:
                    return is_valid_account
            credit_total = round((credit_total + apcrdt_obj.amount +apinvoice_header.otheramount),2)
        if is_payable_paymode != True:
            success_obj = NWisefinSuccess()
            success_obj.set_status("Failed")
            success_obj.set_message("Payable Paymode Not in Credit Screen")
            return success_obj
        print('debit_total credit_total 1', debit_total, credit_total)
        print('debit_total credit_total 2', (debit_total != credit_total))
        if (debit_total != credit_total):
            success_obj = NWisefinSuccess()
            success_obj.set_status("Failed")
            success_obj.set_message("Credit And Debit Amount Mismatch. debit_amt: " +str(debit_total)  + "credit_amt: " +str(credit_total))
            return success_obj

        return True




    def is_valid_account_details(self,request,apcrdt_obj,emp_id):
        from utilityservice.service.ap_api_service import APApiService
        ap_api_serv = APApiService(self._scope())

        account_no=apcrdt_obj.creditrefno
        print('account_no ',account_no)
        print('account_no ',type(account_no))
        print('apcredit_id ',apcrdt_obj.id)
        if account_no in ['',' ',0,'0',None]:
            success_obj = NWisefinSuccess()
            success_obj.set_status("Failed")
            success_obj.set_message("Invalid Account No In Credit , account_no: " + str(account_no))
            return success_obj
        pay_to = apcrdt_obj.apinvoiceheader.apheader.payto
        if pay_to == "S":
            supplierpayment_details = ap_api_serv.get_apcredit_supplierpayment(apcrdt_obj.apinvoiceheader.supplier_id,
                                                                               apcrdt_obj.paymode_id,
                                                                               apcrdt_obj.creditrefno,emp_id)

            if 'data' in supplierpayment_details:
                supplierpayment_data = supplierpayment_details.get('data')
                print('supplierpayment_data_length ', len(supplierpayment_data))
                if len(supplierpayment_data)==0:
                    success_obj = NWisefinSuccess()
                    success_obj.set_status("Failed")
                    success_obj.set_message("Invalid Supplier Account No In Credit , account no: " + str(account_no))
                    return success_obj
            else:
                success_obj = NWisefinSuccess()
                success_obj.set_status("Failed")
                success_obj.set_message("Invalid Supplier Account No In Credit , account_no: " + str(account_no))
                return success_obj

        if pay_to == "E":
            emp_accntdtls = ap_api_serv.fetch_apraiser_emp_accntdtls_using_accntno(request, account_no,
                                                    apcrdt_obj.apinvoiceheader.apheader.raisedby)

            print('emp_accntdtls ',emp_accntdtls)
            if 'data' in  emp_accntdtls:
                success_obj = NWisefinSuccess()
                success_obj.set_status("Failed")
                success_obj.set_message("Invalid Emp Raiser Account No In Credit , account_no: " + str(account_no))
                return success_obj
            if 'account_number' not in emp_accntdtls:
                success_obj = NWisefinSuccess()
                success_obj.set_status("Failed")
                success_obj.set_message("Invalid Raiser Account No In Credit , account_no: " + str(account_no))
                return success_obj
            if 'bankbranch' not in emp_accntdtls:
                success_obj = NWisefinSuccess()
                success_obj.set_status("Failed")
                success_obj.set_message("Invalid Bankbranch Details In Credit Screen." )
                return success_obj
            elif 'bankbranch'  in emp_accntdtls:
                if 'ifsccode' not in emp_accntdtls['bankbranch'] :
                    success_obj = NWisefinSuccess()
                    success_obj.set_status("Failed")
                    success_obj.set_message("Invalid Bankbranch IFSCcode In Credit Screen.")
                    return success_obj
            elif 'bankbranch'  in emp_accntdtls:
                if 'name' not in emp_accntdtls['bankbranch'] :
                    success_obj = NWisefinSuccess()
                    success_obj.set_status("Failed")
                    success_obj.set_message("Invalid Bankbranch Name In Credit Screen.")
                    return success_obj
            if 'beneficiary_name' not in emp_accntdtls:
                success_obj = NWisefinSuccess()
                success_obj.set_status("Failed")
                success_obj.set_message("Invalid Beneficiary Name In Credit Screen.")
                return success_obj


        return False





    def is_entry_debit_validation(self,apinvoiceheader_id):
        condition = Q(apinvoiceheader_id=apinvoiceheader_id, entity_id=self._entity_id(),
                      is_delete=0,is_entry=1)
        apdebit_data_count = APDebit.objects.using(self._current_app_schema()).filter(condition).count()
        if apdebit_data_count > 0:
            return False
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status("Failed")
            #success_obj.set_message("Debit Entry Template Not Picked so kindly rechoose")
            success_obj.set_message("Kindly re-choose the product in each InvoiceDetails for Debit Entry")
            return success_obj



    def is_entry_credit_validation(self,apinvoiceheader_id):
        apcredit_data_count = APCredit.objects.using(self._current_app_schema()).filter(apinvoiceheader_id=apinvoiceheader_id,
                                                        entity_id=self._entity_id(), is_delete=0,is_entry=1).count()
        if apcredit_data_count > 0:
            return False
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status("Failed")
            #success_obj.set_message("Credit Entry Template Not Picked")
            success_obj.set_message("Kindly re-choose the product in each InvoiceDetails for Credit Entry")
            return success_obj



    def debit_validation(self,debit_data):
        print('category_code ',debit_data.category_code)
        print('subcategory_code ',debit_data.subcategory_code)

        if debit_data.category_code in ["DYNAMIC","DUMMY","UNEXPECTED_ERROR","UNEXPECTED ERROR",""," ",None]:
            success_obj = NWisefinSuccess()
            success_obj.set_status("Failed")
            success_obj.set_message("Please enter valid category in Debit screen")
            return success_obj
        if debit_data.subcategory_code in ["DYNAMIC","DUMMY","UNEXPECTED_ERROR","UNEXPECTED ERROR",""," ",None]:
            success_obj = NWisefinSuccess()
            success_obj.set_status("Failed")
            success_obj.set_message("Please enter valid subcategory in Debit screen")
            return success_obj

        return False



    def apstatus_tracker(self, request, apinvoiceheader_id, emp_id):
        try:
            apqueue_data = APQueue.objects.using(self._current_app_schema()).filter(ref_id=apinvoiceheader_id,
                                                                                    entity_id=self._entity_id(),
                                                                                    ref_type=APRefType.APINVOICEHEADER)

            resp_list = NWisefinList()
            if len(apqueue_data) > 0:
                for apqueue in apqueue_data:
                    from_user_data = ap_get_api_caller(request,{"api_url": '/usrserv/employee/' + str(apqueue.from_user_id)})
                    from_user_branch_data = ap_get_api_caller(request,{"api_url": '/usrserv/emp_empbranch/' + str(apqueue.from_user_id)})
                    to_user_data = ap_get_api_caller(request,{"api_url": '/usrserv/employee/' + str(apqueue.to_user_id)})
                    to_user_branch_data = ap_get_api_caller(request,{"api_url": '/usrserv/emp_empbranch/' + str(apqueue.to_user_id)})
                    apqueue_resp = APQueueResponse()
                    apqueue_resp.set_id(apqueue.id)
                    apqueue_resp.set_created_date(str(apqueue.created_date.date()))
                    apqueue_resp.set_comments(apqueue.comments)
                    apqueue_resp.set_remarks(apqueue.remarks)
                    apqueue_resp.set_status(get_AP_status(apqueue.status))
                    apqueue_resp.set_from_user_id(apqueue.from_user_id)
                    apqueue_resp.set_from_user(from_user_data)
                    apqueue_resp.set_from_user_branch(from_user_branch_data)
                    apqueue_resp.set_to_user_id(apqueue.to_user_id)
                    apqueue_resp.set_to_user(to_user_data)
                    apqueue_resp.set_to_user_branch(to_user_branch_data)
                    apqueue_resp.type = ("AP")
                    resp_list.append(apqueue_resp)
            return resp_list
        except Exception as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

    def create_apqueue(self, queue_data):
        try:
            apqueue = APQueue.objects.using(self._current_app_schema()).create(ref_id=queue_data['ref_id'],
                                                                               ref_type=queue_data['ref_type'],
                                                                               from_user_id=queue_data['from_user_id'],
                                                                               status=queue_data['status'],
                                                                               to_user_id=queue_data['to_user_id'],
                                                                               comments=queue_data['comments'],
                                                                               remarks=queue_data['remarks'],
                                                                               is_sys=True,
                                                                               entity_id=self._entity_id())
        except Exception as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj


    def get_vendor_type(self, glno):
        try:
            # print('get_vendor_type invoiceheader_id ', str(apinvoicehdr_id))
            # logger.info('get_vendor_type invoiceheader_id ' + str(apinvoicehdr_id))
            # from apservice.service.apinvoiceheaderservice import APInvoiceheaderService
            # apinv_serv=APInvoiceheaderService(self._scope())
            # #APSegment_Vendor_Identifier
            # supplier_code=apinv_serv.get_supplierbranchcode_using_invoiceheader_id(apinvoicehdr_id)
            apsegment = APSegment_Vendor_Identifier.objects.using(self._current_app_schema()).filter(glno=glno,
                        is_delete=0,entity_id=self._entity_id())

            if len(apsegment) > 0:
                vendor_type = apsegment[0].vendor_type
                return vendor_type
            else:
                return 'default'

        except Exception as excep:
            return 'default'



    def apcredit_direct_entry(self,apcredit_json,apinvhdr_id,emp_id):
        manual=True
        apcredit_obj = APCreditRequest(apcredit_json,manual)
        apcredit_serv = APCreditService(self._scope())
        apcredit_resp = apcredit_serv.apcredit_create(apcredit_obj, apinvhdr_id, emp_id)
        return apcredit_resp

    def apdebit_direct_entry(self, debit_json, apinvhdr_id,apinvdtls_id, emp_id):
        debit_obj = APDebitRequest(debit_json, True)
        apdebit_serv = APDebitService(self._scope())
        apdebit_resp = apdebit_serv.apdebit_create(debit_obj, apinvhdr_id, apinvdtls_id, emp_id)
        return apdebit_resp
