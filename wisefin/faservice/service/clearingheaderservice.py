import traceback

from dateutil.parser import parser
from django.db import IntegrityError, transaction
from django.db.models import Q

from faservice.data.response.assetlocationresponse import AssetLocationResponse
from faservice.data.response.clearingheaderresponse import ClearingHeaderResponse,SearchBucketResponce
from faservice.data.response.faauditresponse import FaAuditResponse
from faservice.models.famodels import AssetLocation, ClearingHeader, ClearingDetails, CwipGroup
from faservice.service.faauditservice import FaAuditService
from faservice.util.FaApiService import FaApiService
from faservice.util.fautil import FaModifyStatus, FaRefType, FaRequestStatusUtil, Fa_Doctype
#from inwardservice.models import EscalationType
from inwardservice.models import EscalationType
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from django.utils.timezone import now
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from faservice.service.clearingdetailsservice import ClearingDetailsService
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class ClearingHeaderService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
    def create_clearingheader(self, clearingheader_obj,doc_type, emp_id,request):
        reqstatus = FaRequestStatusUtil.ONBORD
        scope=request.scope
        try:
            if clearingheader_obj.get_id() is not None:
                if doc_type != Fa_Doctype.BUC:
                    bal_amt =clearingheader_obj.get_totamount()-(clearingheader_obj.get_tottaxamount()/2)
                else:
                    bal_amt = clearingheader_obj.get_totamount()
                clearingheader_var = ClearingHeader.objects.filter(id=clearingheader_obj.get_id()).update(
                    assettype=clearingheader_obj.get_assettype(),
                    invoicecount=clearingheader_obj.get_invoicecount(),
                    totinvoiceamount=clearingheader_obj.get_totinvoiceamount(),
                    tottaxamount=clearingheader_obj.get_tottaxamount(),
                    totamount=clearingheader_obj.get_totamount(),
                    captalizedamount=clearingheader_obj.get_captalizedamount(),
                    balanceamount=self.cal_balanceamount(bal_amt),
                    groupno=clearingheader_obj.get_groupno(),
                    remarks=clearingheader_obj.get_remarks(),
                    updated_date=now(),
                    updated_by=emp_id)

                clearingheader = ClearingHeader.objects.get(id=clearingheader_obj.get_id())

                refid = ref_type = -1
                relrefid = clearingheader.id
                self.audit_function(clearingheader, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.UPDATE, reqstatus,request)


            else:
                try:
                    if doc_type != Fa_Doctype.BUC:
                        bal_amt =clearingheader_obj.get_totamount()-(clearingheader_obj.get_tottaxamount()/2)
                    else:
                        bal_amt = clearingheader_obj.get_totamount()
                    clearingheader = ClearingHeader.objects.create(
                        assettype=clearingheader_obj.get_assettype(),
                        invoicecount=clearingheader_obj.get_invoicecount(),
                        totinvoiceamount=clearingheader_obj.get_totinvoiceamount(),
                        tottaxamount=clearingheader_obj.get_tottaxamount(),
                        totamount=clearingheader_obj.get_totamount(),
                        capitalizedamount=clearingheader_obj.get_capitalizedamount(),
                        balanceamount=bal_amt,
                        groupno=clearingheader_obj.get_groupno(),
                        remarks=clearingheader_obj.get_remarks(),
                        created_by=emp_id)
                except:
                    err=Error()
                    return err
                refid = ref_type = -1
                relrefid = clearingheader.id
                self.audit_function(clearingheader, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.CREATE, reqstatus,request)
        except:
            err=Error()
            err.set_code(ErrorMessage.INVALID_DATA)
            err.set_description(ErrorDescription.INVALID_DATA)
            return err

        clearingheader_resp = ClearingHeaderResponse()
        clearingheader_resp.set_id(clearingheader.id)
        clearingheader_resp.set_assettype(clearingheader.assettype)
        clearingheader_resp.set_invoicecount(clearingheader.invoicecount)
        clearingheader_resp.set_totinvoiceamount(clearingheader.totinvoiceamount)
        clearingheader_resp.set_tottaxamount(clearingheader.tottaxamount)
        clearingheader_resp.set_totamount(clearingheader.totamount)
        clearingheader_resp.set_capitalizedamount(clearingheader.capitalizedamount)
        clearingheader_resp.set_balanceamount(clearingheader.balanceamount)
        clearingheader_resp.set_groupno(clearingheader.groupno)
        clearingheader_resp.set_remarks(clearingheader.remarks)

        return clearingheader_resp

    def fetch_clearingheader(self, vys_page,is_grp,doc_type=None,request=None):
        scope=request.scope
        clearingheader_list = []
        condition = Q(status=1)
        if doc_type == None:
            condition &= Q(doctype=1)
        else:
            condition&=Q(doctype=doc_type)
        if 'invno' in request.GET:
            condition &= Q(invoiceno__icontains=request.GET.get('invno'))
        if 'crno' in request.GET:
            condition &= Q(ecfnum__icontains=request.GET.get('crno'))
        if 'invdate' in request.GET:
            date=request.GET.get('invdate')
            condition &= Q(invoicedate=date)
        if 'supname' in request.GET:
            fa_obj = FaApiService(scope)
            supp_id = fa_obj.fetch_data(request.GET.get('supname'), request)
            condition &= Q(supplier_id=supp_id['id'])
        clringdetail_filter_dtype = ClearingDetails.objects.filter(condition)
        for record in clringdetail_filter_dtype:
            if (record.clearingheader_id not in clearingheader_list):
                clearingheader_list.append(record.clearingheader_id)
        print(clearingheader_list)
        if is_grp=='N':
            clearingheader_data = ClearingHeader.objects.filter(id__in=clearingheader_list,status=1,groupno=0).order_by('created_by')[
                              vys_page.get_offset():vys_page.get_query_limit()]
        else:
            clearingheader_data = ClearingHeader.objects.filter(id__in=clearingheader_list,status=1).exclude(groupno=0).order_by('created_by')[
                                  vys_page.get_offset():vys_page.get_query_limit()]
        clearinghead_data = clearingheader_data.values()
        print(clearinghead_data)
        clearingheader_list = NWisefinList()
        clearingdetail_serv = ClearingDetailsService(scope)

        for clearingheader in clearingheader_data:
            clearingheader_resp = ClearingHeaderResponse()
            clearingheader_resp.set_id(clearingheader.id)
            clearingheader_resp.set_assettype(clearingheader.assettype)
            clearingheader_resp.set_invoicecount(clearingheader.invoicecount)
            clearingheader_resp.set_totinvoiceamount(clearingheader.totinvoiceamount)
            clearingheader_resp.set_tottaxamount(clearingheader.tottaxamount)
            clearingheader_resp.set_totamount(clearingheader.totamount)
            clearingheader_resp.set_capitalizedamount(clearingheader.capitalizedamount)
            clearingheader_resp.set_balanceamount(clearingheader.balanceamount)
            clearingheader_resp.set_groupno(clearingheader.groupno)
            clearingheader_resp.set_remarks(clearingheader.remarks)
            # fetch clearingdetails
            clearingheader_resp.details = clearingdetail_serv.fetch_clearingdetails_list(doc_type,clearingheader.id,request)
            clearingheader_list.append(clearingheader_resp)
        vpage = NWisefinPaginator(clearingheader_data, vys_page.get_index(), 10)
        clearingheader_list.set_pagination(vpage)
        return clearingheader_list

    def fetch_assetlocation_list(self,query, vys_page):
        assetlocation_data = AssetLocation.objects.filter(status=1).order_by('created_by')[vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(assetlocation_data)
        #print(list_length)
        assetlocation_list = NWisefinList()
        if list_length > 0:
            for assetlocation in assetlocation_data:
                assetlocation_resp = AssetLocationResponse()
                assetlocation_resp.set_id(assetlocation.id)
                assetlocation_resp.set_refgid(assetlocation.refgid)
                assetlocation_resp.set_reftablegid(assetlocation.reftablegid)
                assetlocation_resp.set_name(assetlocation.name)
                assetlocation_resp.set_floor(assetlocation.floor)
                assetlocation_resp.set_remarks(assetlocation.remarks)
                assetlocation_list.append(assetlocation_resp)
            vpage = NWisefinPaginator(assetlocation_data, vys_page.get_index(), 10)
            assetlocation_list.set_pagination(vpage)
        return assetlocation_list

    # def fetch_assetlocation(self,assetlocation_id):
    #     try:
    #         assetlocation = AssetLocation.objects.get(id=assetlocation_id)
    #
    #         assetlocation_resp = AssetLocationResponse()
    #         assetlocation_resp.set_id(assetlocation.id)
    #         assetlocation_resp.set_refgid(assetlocation.refgid)
    #         assetlocation_resp.set_reftablegid(assetlocation.reftablegid)
    #         assetlocation_resp.set_name(assetlocation.name)
    #         assetlocation_resp.set_floor(assetlocation.floor)
    #         assetlocation_resp.set_remarks(assetlocation.remarks)
    #         return assetlocation_resp
    #     except AssetLocation.DoesNotExist:
    #         error_obj = Error()
    #         error_obj.set_code(ErrorMessage.INVALID_ASSETLOCATION_ID)
    #         error_obj.set_description(ErrorDescription.INVALID_ASSETLOCATION_ID)
    #         return error_obj
    #
    # def delete_assetlocation(self,assetlocation_id,emp_id):
    #     assetlocation = AssetLocation.objects.filter(id=assetlocation_id).delete()
    #     reqstatus = FaRequestStatusUtil.ONBORD
    #
    #     refid = ref_type = -1
    #     relrefid = assetlocation_id
    #     self.audit_function(assetlocation, refid, ref_type, relrefid,
    #                         emp_id, FaModifyStatus.DELETE, reqstatus)
    #     if assetlocation[0] == 0:
    #         error_obj = Error()
    #         error_obj.set_code(ErrorMessage.INVALID_ASSETLOCATION_ID)
    #         error_obj.set_description(ErrorDescription.INVALID_ASSETLOCATION_ID)
    #         return error_obj
    #     else:
    #         success_obj = Success()
    #         success_obj.set_status(SuccessStatus.SUCCESS)
    #         success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
    #         return success_obj
    #

    def clearance_bucket(self, details_data, emp_id):
        clearingheaders_list=[]
        print(details_data)
        for clearingheader in details_data['clearing_header']:
            clearingheaders_data=ClearingHeader.objects.get(id=clearingheader['id'])
            clearingheaders_list.append(clearingheaders_data)
        bucket_data=CwipGroup.objects.get(code=details_data['bucket_code'])
        check_bucket=ClearingHeader.objects.filter(groupno=bucket_data.name,status=1)
        if (len(check_bucket)>0):
            bucket_clearinghead=check_bucket[0]
        else:
            if len(details_data['clearing_header'])==1:
                err_obj=Error()
                err_obj.set_code(ErrorMessage.INVALID_DATA_COUNT_FOR_BUCKET)
                err_obj.set_description(ErrorDescription.INVALID_BUCKET_DATA_COUNT)
                return err_obj.get()
            bucket_clearinghead=clearingheaders_list[0]
        for data in clearingheaders_list:
            if(data.id!=bucket_clearinghead.id):
                data.status=0
                bucket_clearinghead.totinvoiceamount += data.totinvoiceamount
                bucket_clearinghead.tottaxamount+=data.tottaxamount
                bucket_clearinghead.invoicecount += data.invoicecount
                bucket_clearinghead.totamount += data.totamount
                bucket_clearinghead.capitalizedamount += data.capitalizedamount
                bucket_clearinghead.expenseamount += data.expenseamount
                bucket_clearinghead.balanceamount += data.balanceamount
                clearingdetails_data=ClearingDetails.objects.filter(clearingheader_id=data.id)
                inv_dbt_tax=clearingdetails_data[0].inv_debit_tax
                for clearingdetails in clearingdetails_data:
                    clearingdetails.clearingheader_id=bucket_clearinghead.id
                    clearingdetails.save()
            data.groupno=bucket_data.name
            data.save()
        bucket_clearinghead.groupno=bucket_data.name
        bucket_clearinghead.save()
        success_resp=NWisefinSuccess()
        success_resp.set_status(SuccessStatus.SUCCESS)
        success_resp.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_resp.get()





    def audit_function(self, audit_data, refid,reftype, relrefid, emp_id, action,reqstatus,request=None):
        if action == FaModifyStatus.DELETE:
            data = None
        else:
            data = audit_data.__dict__
            del data['_state']
        scope=request.scope
        audit_service = FaAuditService(scope)
        audit_obj = FaAuditResponse()
        audit_obj.set_refid(refid)
        audit_obj.set_reqstatus(reqstatus)
        audit_obj.set_reftype(reftype)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(FaRefType.CLEARINGHEADER)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)


    def cal_balanceamount(self,total_amount):
        return total_amount

    def fetch_bucket(self,query=None):
        from faservice.data.response.clearingheaderresponse import BucketResponse
        bucket_resp=BucketResponse()
        if query!=None:
            buckets=CwipGroup.objects.filter(name__icontains=query)
        else:
            buckets=CwipGroup.objects.filter()
        for bucket in buckets:
            bucket_resp.add_bucket(bucket.name,bucket.id,bucket.code)
        return bucket_resp.get()

    def createnewbucket(self, buck_res, emp_id):
        existing_data=CwipGroup.objects.all()
        bucket_obj=CwipGroup()
        if len(existing_data)==0:
            bucket_obj.code='CWG001'
        else:
            data=existing_data.latest('id')
            new_code=data.code.replace(data.code[-3:],str(int(data.code[-3:])+1).zfill(3))
            print(new_code)
            bucket_obj.code=new_code
        bucket_obj.name=buck_res.name
        bucket_obj.doctype=buck_res.doctype
        bucket_obj.created_by=emp_id
        bucket_obj.save()
        bucket_obj.__dict__.pop('_state')
        return bucket_obj.__dict__
    def bucketsummary(self,vys_page,request):
        clearingheader_data = ClearingHeader.objects.filter(status=1,invoicecount__gt=1).exclude(groupno=0).order_by('created_by')[
                              vys_page.get_offset():vys_page.get_query_limit()]
        clearinghead_data = clearingheader_data.values()
        print(clearinghead_data)
        clearingheader_list = NWisefinList()
        scope=request.scope
        clearingdetail_serv = ClearingDetailsService(scope)

        for clearingheader in clearingheader_data:
            clearingheader_resp = ClearingHeaderResponse()
            clearingheader_resp.set_id(clearingheader.id)
            data=CwipGroup.objects.filter(name=clearingheader.assettype).values('id','code','name')[0]
            clearingheader_resp.set_assettype(data)
            clearingheader_resp.set_invoicecount(clearingheader.invoicecount)
            clearingheader_resp.set_totinvoiceamount(clearingheader.totinvoiceamount)
            clearingheader_resp.set_tottaxamount(clearingheader.tottaxamount)
            clearingheader_resp.set_totamount(clearingheader.totamount)
            clearingheader_resp.set_capitalizedamount(clearingheader.capitalizedamount)
            clearingheader_resp.set_balanceamount(clearingheader.balanceamount)
            clearingheader_resp.set_groupno(clearingheader.groupno)
            clearingheader_resp.set_remarks(clearingheader.remarks)
            # fetch clearingdetails
            # clearingheader_resp.details = clearingdetail_serv.fetch_clearingdetails_list(doc_type, clearingheader.id,
            #                                                                              request)
            clearingheader_list.append(clearingheader_resp)
        vpage = NWisefinPaginator(clearingheader_data, vys_page.get_index(), 10)
        clearingheader_list.set_pagination(vpage)
        return clearingheader_list
    def bucketnamesearch(self,vys_page,data):
        buc_datas=CwipGroup.objects.filter(name__contains=data)[vys_page.get_offset():vys_page.get_query_limit()]
        buc_data=buc_datas.values()
        searchdata=NWisefinList()
        for d in buc_datas:
            obj_data = SearchBucketResponce()
            obj_data.set_id(d.id)
            obj_data.set_name(d.name)
            obj_data.set_code(d.code)
            searchdata.append(obj_data)
        vpage=NWisefinPaginator(buc_datas,vys_page.get_index(),10)
        searchdata.set_pagination(vpage)
        return searchdata

    def clearingheader_capitalize_unlock(self,json_data):
        try:
            clearingheader_list=ClearingHeader.objects.filter(id__in=json_data['id'])

            for clearingheader_data in clearingheader_list:
                if clearingheader_data.updated_date==None:
                    clearingheader_data.updated_date=now()
                print((now() - clearingheader_data.updated_date).total_seconds())
                if json_data['status'] == 'LOCK':
                    clearingheader_data.islock=0

                elif json_data['status'] == 'UNLOCK' and ((now()-clearingheader_data.updated_date).total_seconds())/60>1:
                    clearingheader_data.islock=1
                    clearingheader_data.updated_date=now()
                    resp=NWisefinSuccess()
                    resp.set_message(SuccessMessage.UPDATE_MESSAGE)
                    resp.set_status(SuccessStatus.SUCCESS)
                    return resp
                else:
                    err=Error()
                    err.set_code("Wait 30 Mins")
                    err.set_description(ErrorDescription.CLEARINGHEADER_ID_LOCK_TIMEWAIT)
                    return err
                clearingheader_data.save()
        except Exception as e:
            traceback.print_exc()
            err=Error()
            err.set_code(ErrorMessage.INVALID_DATA)
            err.set_description(str(e))
            return  err
        resp_obj=NWisefinSuccess()
        resp_obj.set_status(SuccessStatus.SUCCESS)
        resp_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
    def get_clearing_lock_status(self,crno):
        try:
            clearingheader_data=ClearingDetails.objects.filter(crnum=crno)[0].clearingheader
            lock_data=clearingheader_data.islock
            resp=ClearingHeaderResponse()
            resp.crno = crno
            resp.clearingheader_id = clearingheader_data.id
            if lock_data==1:
                resp.status='UNLOCKED'
            else:
                resp.status='LOCK'
        except Exception as e:
            err=Error()
            err.set_code(ErrorMessage.INVALID_DATA)
            err.set_description(str(e))
            return  err
        return resp