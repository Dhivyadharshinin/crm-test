import sys
import traceback
from django.db import transaction
from django.db.models import Q
from apservice.data.response.apauditresponse import APAuditResponse
from apservice.data.response.apheaderresponse import APHeaderResponse
from apservice.data.response.apinvoiceheaderresponse import APInvoiceheaderresponse
from apservice.models import APHeader, APQueue, APBounce
from apservice.service.apauditservice import APAuditService
from apservice.service.apinvoicedetailsservice import APInvoiceDetailService
from apservice.service.apinvoiceheaderservice import APInvoiceheaderService
from apservice.util.aputil import APStatus, APModifyStatus, APRefType, get_APType, get_apstatus, get_pay_to, AP_Status, \
    ap_get_api_caller, get_AP_status
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from django.utils.timezone import now


class APHeaderService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.AP_SERVICE)

    def apheader_create(self,request,aphdr_json,ap_obj,emp_id):
        is_originalinvoice =True
        if 'is_originalinvoice' in aphdr_json:
            is_originalinvoice=aphdr_json['is_originalinvoice']
        inwarddetails_id=aphdr_json['inwarddetails_id']

        raised_by = ap_obj.get_raisedby()
        raiser_branch = ap_obj.get_raiserbranch()
        raiser_name = ap_obj.get_raisername()

        # if raised_by is None and raiser_branch is None and raiser_name is None:
        #     from utilityservice.service import api_service
        #     api_serv = api_service.ApiService(self._scope())
        #     emp = api_serv.get_empsingle_id(request, emp_id)
        #     raiser_branch = emp['employee_branch']
        #     raiser_name = emp['name']
        #     raised_by = emp['id']

        if not ap_obj.get_id() is None:
            aphdr_update = APHeader.objects.using(self._current_app_schema()).filter(id=ap_obj.get_id(),entity_id=self._entity_id()).update(
                                                                        inwarddetails_id=inwarddetails_id,
                                                                        supplier_type=ap_obj.get_supplier_type(),
                                                                        commodity_id=ap_obj.get_commodity_id(),
                                                                        #aptype=ap_obj.get_ecftype(),
                                                                        apdate=ap_obj.get_ecfdate(),
                                                                        apamount=ap_obj.get_ecfamount(),
                                                                        #apstatus=APStatus.DRAFT,
                                                                        apstatus=ap_obj.get_ecfstatus_id(),
                                                                        ppx=ap_obj.get_ppx_id(),
                                                                        notename=ap_obj.get_notename(),
                                                                        remark=ap_obj.get_remark(),
                                                                        #payto=ap_obj.get_payto(),
                                                                        is_originalinvoice=is_originalinvoice,
                                                                        #raisedby=ap_obj.get_raisedby(),
                                                                        #raiserbranch=ap_obj.get_raiserbranch(),
                                                                        #raisername=ap_obj.get_raisername(),
                                                                        #crno=ap_obj.get_crno()
                                                                        client_code=ap_obj.get_client_code(),
                                                                        rmcode=ap_obj.get_rmcode(),
                                                                        updated_by=emp_id,
                                                                        updated_date=now())

            Ecfhdr = APHeader.objects.using(self._current_app_schema()).get(id=ap_obj.get_id())
            self.audit_function(Ecfhdr, Ecfhdr.id, Ecfhdr.id, emp_id,
                                APModifyStatus.UPDATE, APRefType.APHEADER)
            # APQueue.objects.using(self._current_app_schema()).create(ref_id=Ecfhdr.id, ref_type=APRefType.APHEADER, from_user_id=emp_id,
            #                         to_user_id=emp_id,
            #                         created_date=now(),
            #                         comments="PENDING  FOR APPROVAL",
            #                         remarks=ap_obj.get_remark(),
            #                         is_sys=True)

        else:
                Ecfhdr = APHeader.objects.using(self._current_app_schema()).create(
                                                    inwarddetails_id=inwarddetails_id,
                                                    supplier_type=ap_obj.get_supplier_type(),
                                                    commodity_id=ap_obj.get_commodity_id(),
                                                    aptype=ap_obj.get_ecftype(),
                                                    apdate=ap_obj.get_ecfdate(),
                                                    apamount=ap_obj.get_ecfamount(),
                                                    apstatus=ap_obj.get_ecfstatus_id(),
                                                    ppx=ap_obj.get_ppx_id(),
                                                    notename=ap_obj.get_notename(),
                                                    remark=ap_obj.get_remark(),
                                                    approvedby=ap_obj.get_approvedby(),
                                                    approvername=ap_obj.get_approvername(),
                                                    payto=ap_obj.get_payto(),
                                                    raisedby=raised_by,
                                                    raiserbranch=raiser_branch,
                                                    raisername=raiser_name,
                                                    crno=ap_obj.get_crno(),
                                                    created_by=emp_id,
                                                    tds=ap_obj.get_tds_id(),
                                                    client_code=ap_obj.get_client_code(),
                                                    rmcode=ap_obj.get_rmcode(),
                                                    approver_branch = ap_obj.get_approver_branch_id(),
                                                    branch = ap_obj.get_choseapprover_branch_id(),
                                                    is_originalinvoice=is_originalinvoice,
                                                    entity_id=self._entity_id())

                y=now().strftime("%y")
                m=now().strftime("%m")
                d=now().strftime("%d")
                Ecfhdr.rmubarcode = 'RMU'+y+m+d+str(Ecfhdr.id).zfill(4)
                Ecfhdr.save()

                self.audit_function(Ecfhdr, Ecfhdr.id, Ecfhdr.id, emp_id,
                                    APModifyStatus.CREATE, APRefType.APHEADER)
                APQueue.objects.using(self._current_app_schema()).create(ref_id=Ecfhdr.id, ref_type=APRefType.APINVOICEHEADER,
                                                             from_user_id=emp_id, to_user_id=-1,
                                       comments="NEW" ,
                                       remarks=ap_obj.get_remark(),
                                       is_sys=True,entity_id=self._entity_id())


        ap_data = APHeaderResponse()
        ap_data.set_id(Ecfhdr.id)
        ap_data.set_crno(Ecfhdr.crno)
        ap_data.set_supplier_type(Ecfhdr.supplier_type)
        ap_data.set_commodity(Ecfhdr.commodity_id)
        ap_data.set_aptype(Ecfhdr.aptype)
        ap_data.set_apdate(Ecfhdr.apdate)
        ap_data.set_apamount(Ecfhdr.apamount)
        ap_data.set_apstatus(Ecfhdr.apstatus)
        ap_data.set_ppx(Ecfhdr.ppx)
        ap_data.set_notename(Ecfhdr.notename)
        ap_data.set_remark(Ecfhdr.remark)
        ap_data.set_payto(Ecfhdr.payto)
        ap_data.set_raisedby(Ecfhdr.raisedby)
        ap_data.set_raiserbranch(Ecfhdr.raiserbranch)
        ap_data.set_raisername(Ecfhdr.raisername)
        ap_data.set_approvername(Ecfhdr.approvername)
        ap_data.set_rmcode(Ecfhdr.rmcode)
        ap_data.set_rmubarcode(Ecfhdr.rmubarcode)
        ap_data.set_client_code(Ecfhdr.client_code)
        return ap_data


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

    def fetch_apheader_single(self,request,aphdr_id,emp_id):
        try:
            aphdr_data = APHeader.objects.using(self._current_app_schema()).get(id=aphdr_id, is_delete=0,
                                                                                entity_id=self._entity_id())
            apinvhdr_serv = APInvoiceheaderService(self._scope())
            aphdr_resp = APHeaderResponse()
            self.fetch_apheader_list_lite(request,aphdr_resp, aphdr_data, emp_id)
            #aphdr_resp.set_apinvheader(apinvhdr_serv.fetch_apinvhdr_using_aphdr(request,aphdr_id,emp_id))

            return aphdr_resp
        except Exception as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

    def apheader_delete(self,apheader_id,emp_id):
        try:
            apcredit = APHeader.objects.using(self._current_app_schema()).filter(id=apheader_id,
                                                                    entity_id=self._entity_id(),
                                                                                 is_delete=0).update(
                is_delete=1,updated_by=emp_id,updated_date=now())

            if apcredit == 0:
                error_obj = NWisefinError()
                error_obj.set_code('INVALID_APHEADER_ID')
                error_obj.set_description('INVALID APHEADER ID')
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

    def fetch_apheader_all_list(self,request,vys_page,emp_id):
        try:
            aphdr_data = APHeader.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                    is_delete=0).order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]
            #apinvhdr_serv = APInvoiceheaderService()
            resp_list = NWisefinList()
            if len(aphdr_data) > 0:
                for aphdr in aphdr_data:
                    aphdr_resp = APHeaderResponse()
                    self.fetch_apheader_list_lite(request,aphdr_resp, aphdr, emp_id)
                    resp_list.append(aphdr_resp)
                vpage = NWisefinPaginator(aphdr_data, vys_page.get_index(), 10)
                resp_list.set_pagination(vpage)
            #aphdr_resp.set_apinvheader(apinvhdr_serv.fetch_apinvhdr_using_aphdr(request,aphdr_id,emp_id))
            return resp_list
        except Exception as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj



    def fetch_apheader_list(self,request,aphdr_id,crno,emp_id):
        try:
            codition=Q(is_delete=0,entity_id=self._entity_id())
            print('crno ',crno)
            if crno:
                codition&=Q(crno=aphdr_id)
            else:
                codition&=Q(id=aphdr_id)

            aphdr_data = APHeader.objects.using(self._current_app_schema()).get(codition)
            aphdr_id=aphdr_data.id
            apinvhdr_serv = APInvoiceheaderService(self._scope())
            aphdr_resp = APHeaderResponse()
            self.fetch_apheader_list_lite(request,aphdr_resp, aphdr_data, emp_id)
            logger.info('aphdr_id '+str(aphdr_id))
            aphdr_resp.set_apinvheader(apinvhdr_serv.fetch_apinvhdr_using_aphdr(request,aphdr_id,emp_id))
            return aphdr_resp

        except Exception as excep:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            traceback.print_exc()
            success_obj = NWisefinError()
            success_obj.set_code(ErrorMessage.INVALID_DATA)
            success_obj.set_description(str(excep) + " - " + str(filename) + ", line_no: " + str(line_number) + str(', exception_type : {c} '.format(c=type(excep).__name__)))
            return success_obj

    def fetch_apheader_list_lite(self,request, aphdr_resp, aphdr_data, emp_id):
        from utilityservice.service import api_service
        api_serv = api_service.ApiService(self._scope())
        employee_data = ap_get_api_caller(request,{"api_url": '/usrserv/employee/' + str(aphdr_data.raisedby)})

        from utilityservice.service.ap_api_service import APApiService
        ap_api_serv = APApiService(self._scope())
        empbranch_data = ap_api_serv.ap_employee_branch_single_get(aphdr_data.raiserbranch)
        if aphdr_data.approver_branch is not None:
            approver_branch_data = ap_api_serv.ap_employee_branch_single_get(aphdr_data.approver_branch)
        else:
            approver_branch_data = None

        if aphdr_data.branch is not None:
            raiserchoose_branch_data = ap_api_serv.ap_employee_branch_single_get(aphdr_data.branch)
        else:
            raiserchoose_branch_data = None

        commodity_data=ap_api_serv.ap_commodity_single_get(aphdr_data.commodity_id, emp_id)
        aptype_data=ap_api_serv.get_ap_ecftypesingle(aphdr_data.aptype)
        ecftds_data=ap_api_serv.ap_ef_tds_single_get(aphdr_data.tds)
        logger.info('ecftds_data  '+str(ecftds_data))

        aphdr_resp.set_id(aphdr_data.id)
        aphdr_resp.set_crno(aphdr_data.crno) 
        aphdr_resp.set_is_originalinvoice(self.is_original_return(aphdr_data.is_originalinvoice))
        aphdr_resp.set_commodity(commodity_data)
        aphdr_resp.set_aptype(aptype_data)
        aphdr_resp.set_apdate(aphdr_data.apdate)
        aphdr_resp.set_apamount(aphdr_data.apamount)
        #aphdr_resp.set_apstatus(get_apstatus(aphdr_data.apstatus))
        aphdr_resp.set_ppx(aphdr_data.ppx)
        aphdr_resp.set_notename(aphdr_data.notename)
        aphdr_resp.set_remark(aphdr_data.remark)
        aphdr_resp.set_payto(get_pay_to(aphdr_data.payto))
        #aphdr_resp.set_payto_id(aphdr_data.payto)
        aphdr_resp.set_raisedby(employee_data)
        aphdr_resp.set_raiserbranch(empbranch_data)
        aphdr_resp.set_raisername(aphdr_data.raisername)
        aphdr_resp.set_approvedby(aphdr_data.approvedby)
        aphdr_resp.set_approvername(aphdr_data.approvername)
        aphdr_resp.set_rmubarcode(aphdr_data.rmubarcode)
        aphdr_resp.set_branch(aphdr_data.branch)
        aphdr_resp.raiserchoose_branch=(raiserchoose_branch_data)
        aphdr_resp.set_approver_branch(approver_branch_data)
        aphdr_resp.set_tds(ecftds_data)
        # if 'data' in ecftds_data :
        #     for tds_dict in ecftds_data['data']:
        #         if 'id' in tds_dict :
        #             if int(tds_dict['id'])==int(aphdr_data.tds):
        #                 aphdr_resp.set_tds(tds_dict)

        if aphdr_data.client_code:
            aphdr_resp.set_client_code(api_serv.get_clicode(aphdr_data.client_code))
        else:
            aphdr_resp.set_client_code(None)
        if aphdr_data.rmcode:
            aphdr_resp.set_rmcode(api_serv.get_empsingle_id(request, aphdr_data.rmcode))
        else:
            aphdr_resp.set_rmcode(None)


    def is_original_return(self,is_original):
        if is_original is True :
            return 1
        elif is_original is False :
            return 0
        else:
            return None


    def get_pocket_apinvoiceheader_count(self,inwarddtl_id):
            condition=Q(inwarddetails_id=inwarddtl_id,is_delete=0,entity_id=self._entity_id())
            apinwrdinvhdr_data = APHeader.objects.using(self._current_app_schema()).filter(condition)
            return len(apinwrdinvhdr_data)

    def apheader_status_change(self,aphdr_data,emp_id):
        try:
            with transaction.atomic(using=self._current_app_schema()):
                apinwrdinvhdr_data = APHeader.objects.using(self._current_app_schema()).filter(id=aphdr_data['apheader_id'],
                                                              entity_id=self._entity_id()).update(
                    status=aphdr_data['status_id'],
                    updated_date=now(),
                    updated_by=emp_id)
                if int(aphdr_data['status_id']) == AP_Status.BOUNCE:
                    bounce=APBounce.objects.using(self._current_app_schema()).create(
                        apinvoiceheader_id=aphdr_data['apinvoicehdr_id'],
                        invoicedate=aphdr_data['invoicedate'],
                        created_by=emp_id,
                        created_date=now(),entity_id=self._entity_id())

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj

        except Exception  as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj


    def apheader_status_approve(self,apheader_id,emp_id):
        apinwrdinvhdr_data = APHeader.objects.using(self._current_app_schema()).filter(id=apheader_id,
                                                      entity_id=self._entity_id()).update(
            status=AP_Status.APPROVED,
            updated_date=now(),
            updated_by=emp_id)

    def apheader_status_reject(self,apheader_id,emp_id):
        apinwrdinvhdr_data = APHeader.objects.using(self._current_app_schema()).filter(id=apheader_id,
                                                      entity_id=self._entity_id()).update(
            status=AP_Status.REJECTED,
            updated_date=now(),
            updated_by=emp_id)

    def aptables_delete(self,request,emp_id):
            aphdr_data = APHeader.objects.using(self._current_app_schema()).delete()

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def aptables_single_delete(self,request,apheader_id,emp_id):
            aphdr_data = APHeader.objects.using(self._current_app_schema()).filter(id=apheader_id,
                                                                    entity_id=self._entity_id()).delete()

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def apheader_duplicate_validation(self,crno):
        conditon=Q(entity_id=self._entity_id(),crno=crno,is_delete=0)&~Q(status=AP_Status.REJECTED)
        aphdr_data = APHeader.objects.using(self._current_app_schema()).filter(conditon)

        if len(aphdr_data) > 0:
            return True
        else:
            return False

    def ap_queuedetails(self,request,ecfhdr_id):
        from utilityservice.service import api_service
        ecf_que=APQueue.objects.using(self._current_app_schema()).filter(ref_id=ecfhdr_id,
                                                                entity_id=self._entity_id())
        vysfin_list = NWisefinList()
        stop_count=len(ecf_que)
        if len(ecf_que) > 0:
            for ecfque in ecf_que:
                # if  stop_count > 2:
                #     stop_count=stop_count-1
                #     continue
                api_serv = api_service.ApiService(self._scope())
                ecfque_json=dict()
                ecfque_json['from_user'] = api_serv.get_empsingle_id(request,ecfque.from_user_id)
                ecfque_json['to_user'] = api_serv.get_empsingle_id(request,ecfque.to_user_id)
                ecfque_json['status'] = ecfque.comments
                ecfque_json['remarks'] = ecfque.remarks
                ecfque_json['created_date'] = str(ecfque.created_date.date())
                vysfin_list.append(ecfque_json)
        return vysfin_list


    def get_pocket_apheader_new(self,request,emp_id,inwarddtl_id):
        try:
            condition=Q(status__in=[AP_Status.NEW,AP_Status.PENDING_FOR_APPROVAL,AP_Status.APPROVED],
                        inwarddetails_id=inwarddtl_id,is_delete=0,entity_id=self._entity_id())
            aphdr_data = APHeader.objects.using(self._current_app_schema()).filter(condition)

            resp_list = NWisefinList()
            print('len(apinvhdr_data)',len(aphdr_data))
            if len(aphdr_data) > 0:
                for aphdr in aphdr_data:
                    apinwardind_resp = APInvoiceheaderresponse()
                    aphdr_serv=APInvoiceheaderService(self._scope())
                    apinwardind_resp.set_id(aphdr.id)
                    apinwardind_resp.set_crno(aphdr.crno)
                    apinwardind_resp.set_is_originalinvoice(self.is_original_return(aphdr.is_originalinvoice))
                    apinwardind_resp.set_apdate(str(aphdr.apdate))
                    apinwardind_resp.set_apamount(aphdr.apamount)
                    apinwardind_resp.set_raiser_employeename(aphdr.raisername)
                    apinwardind_resp.set_approvername(aphdr.approvername)
                    apinwardind_resp.set_inwarddetails_id(aphdr.inwarddetails_id)
                    apinwardind_resp.set_remarks(aphdr.remark)
                    apinwardind_resp.apinvoicehdr=(aphdr_serv.fetch_apinvhdr_using_aphdr(request,aphdr.id,emp_id))
                    # apinwardind_resp.set_invoicetype_id(get_APType(apheader.aptype))
                    # apinwardind_resp.set_supplier(supplier_data
                    # apinwardind_resp.set_invoice_date(apinwrdinvhdr.invoicedate)
                    # apinwardind_resp.set_invoice_amount(apheader.apamount)
                    apinwardind_resp.set_status(get_AP_status(aphdr.status))
                    resp_list.append(apinwardind_resp)
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


