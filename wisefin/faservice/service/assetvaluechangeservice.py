import traceback
from datetime import datetime

from django.db import transaction
from django.db.models import Q, Count,QuerySet

from faservice.data.request.assetheaderrequest import AssetHeaderRequest
from faservice.data.response.assetidresponse import AssetidResponse
from faservice.data.response.assetvaluechangeresponse import AssetValueResponse
from faservice.models.famodels import AssetId, AssetValue, AssetDetails, AssetHeader, AssetCat
from faservice.service.assetheaderservice import AssetheaderService
from faservice.service.assetlocationservice import AssetLocationService
from faservice.service.faauditservice import FaAuditService
from faservice.util.FaApiService import  FaApiService
from faservice.util.fautil import FaModifyStatus, FaRefType, FaRequestStatusUtil, AssetRequestfor, AssetRequestStatus, \
    AssetStatus, AssetSource, assetvaluedtl_status, asset_requestfor_status, asset_requeststatus, assetrequst_status
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from django.utils.timezone import now
from utilityservice.data.response.nwisefinsuccess import SuccessMessage,NWisefinSuccess,SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from faservice.data.response.faauditresponse import FaAuditResponse
from utilityservice.permissions.filter.commonpermission import ModulePermission
from utilityservice.permissions.util.dbutil import RoleList,ModuleList
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class AssetValueChange(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
    def fetch_assetvaluechange_list(self, vys_page,filter_json,emp_id,request=None):
        scope=request.scope
        try:
            assetid_list = NWisefinList()

            module_permission = ModulePermission(scope)
            role_arr = module_permission.employee_modulerole(emp_id, ModuleList.FA)
            maker = RoleList.maker
            checker = RoleList.checker


            if maker in role_arr :
                condition = Q(assetdetails__assetdetails_status__in=[AssetStatus.ACTIVE,AssetStatus.IN_ACTIVE]) #&\
                            # Q(assetdetails__requestfor__in=[AssetRequestfor.VALUEREDUCTION],)
            else:
                return assetid_list


            if 'assetdetails_value' in filter_json:
                condition&= Q(asset_value=filter_json['assetdetails_value'])
            if 'branch_id' in filter_json:
                condition&= Q(assetdetails__branch_id=filter_json['branch_id'])
            if 'assetcat_id' in filter_json:
                condition&= Q(assetdetails__assetcat_id=filter_json['assetcat_id'])
            if 'barcode' in filter_json:
                condition&= Q(assetdetails__barcode__icontains=filter_json['barcode'])
            if 'capdate' in filter_json:
                condition&= Q(assetdetails__capdate=filter_json['capdate'])

            assetval_data = AssetValue.objects.filter(condition).order_by('-id','-assetdetails__assetdetails_id')[vys_page.get_offset():vys_page.get_query_limit()]

            # print(assetval_data.query)
            assetvalid_list=list()
            assetvalbar_list=list()


            if len(assetval_data) > 0 :
                for assetval in assetval_data:
                    assetvalue_resp = AssetValueResponse()
                    #assetvalue
                    assetvalue_resp.set_id(assetval.id)
                    assetvalue_resp.set_oldvalue(assetval.asset_oldvalue)
                    assetvalue_resp.set_assetvalue(assetval.asset_value)
                    assetvalue_resp.set_reason(assetval.reason)
                    assetvalue_resp.set_assetvalue_date(assetval.date)
                    assetvalue_resp.set_newvalue(str(assetval.asset_value))
                    asst_req=AssetRequestStatus()
                    assetvalue_resp.set_valuechange_status(asst_req.get_val(assetval.assetvalue_status))
                    #assetdetails
                    assetdetails = assetval.assetdetails # assetdetails FK details get
                    assetvalue_resp.set_capdate(assetdetails.capdate)
                    assetvalue_resp.set_assetdetails_id(assetdetails.id)
                    assetvalue_resp.set_assetdtls_id(assetdetails.assetdetails_id)
                    assetvalue_resp.set_assetdetails_status(assetvaluedtl_status(assetdetails.assetdetails_status))
                    asst_header=AssetHeader.objects.filter(id=assetdetails.assetheader_id)
                    if len(asst_header)>0:
                        asst_header=asst_header[0]
                    assetvalue_resp.set_assetdetails_value(asst_header.valuetot)
                    assetvalue_resp.set_barcode(assetdetails.barcode)
                    #asset Location
                    location_serv = AssetLocationService(scope)
                    assetvalue_resp.set_location(location_serv.fetch_assetlocation(assetdetails.assetlocation_id))
                    #employee_branch
                    emp_branch=FaApiService(scope)
                    assetvalue_resp.branch= (emp_branch.fetch_branch(assetval.assetdetails.branch_id))
                    #assetcat
                    assetcat=assetval.assetdetails.assetcat # assetcat FK details get
                    assetvalue_resp.set_assetcat_subcatname(assetcat.subcatname)
                    assetid_list.append(assetvalue_resp)
                vpage = NWisefinPaginator(assetval_data, vys_page.get_index(), 10)
                assetid_list.set_pagination(vpage)
        except Exception  as excep:
            logger.info('FAL_ASSETVALCHANGE_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

        return assetid_list

    #@transaction.atomic(using='fa_service')
    def create_valuechange_assetdetails(self, assetdtlsobj, emp_id,request):
        # print(assetdtlsobj)
        try:
            with transaction.atomic(using=self._current_app_schema()):
                valuechange_date=assetdtlsobj['valuechange_date']
                reqstatus = FaRequestStatusUtil.ONBORD

                for assetdetails_obj in assetdtlsobj['assetdetails']:
                    assetdetails=AssetDetails.objects.filter(barcode=assetdetails_obj['barcode'],
                                                          status=AssetStatus.ACTIVE).order_by('-id','-assetdetails_id')
                    if len(assetdetails)>0:
                        assetdetails=assetdetails[0]
                    else:
                        continue
                    #

                    assetdetails.requestfor=AssetRequestfor.VALUEREDUCTION
                    assetdetails.requeststatus=AssetRequestStatus.PENDING
                    assetdetails.save()
                    self.create_assetvalue(assetdetails,assetdtlsobj,assetdetails_obj,emp_id)
                    # print('assetdtls_data.status1')
                    #self.update_assetheader(assetdtls.barcode, assetdetails_obj['new_value'],emp_id)

                    # update the status





                    refid = ref_type = -1
                    relrefid = assetdetails.id
                    self.audit_function(assetdetails, refid, ref_type, relrefid,
                                        emp_id, FaModifyStatus.CREATE, reqstatus,request)

                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.CREATE_MESSAGE)

        except Exception  as excep:
            logger.info('FAL_ASSETVALCHANGE_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

        return success_obj


    def create_assetvalue(self,asset_dtls,assetdtls_obj,assetdtls_dict,emp_id):
        reason=None
        if 'reason' in  assetdtls_obj:
            reason=assetdtls_obj['reason']

        assetdetails = AssetDetails.objects.filter(barcode=assetdtls_dict['barcode'],
                                                   status=AssetStatus.ACTIVE).order_by('-id', '-assetdetails_id')[0]
        asset_val=AssetValue.objects.create(
                        assetdetails_id =asset_dtls.id,
                        asset_barcode=assetdtls_dict['barcode'],
                        date = assetdtls_obj['valuechange_date'],
                        assetvalue_status = AssetRequestStatus.PENDING,
                        reason =reason,
                        asset_value = assetdtls_dict['new_value'],
                        #asset_oldvalue = old_assetdtls.assetdetails_value,
                        asset_oldvalue = asset_dtls.assetheader.valuetot,
                        status=AssetStatus.ACTIVE,
                        created_by=emp_id)







    def valuechange_checkersummary(self, vys_page,filter_json,emp_id,request=None):
        try:
            scope=request.scope
            assetid_list = NWisefinList()
            module_permission = ModulePermission(scope)
            role_arr = module_permission.employee_modulerole(emp_id, ModuleList.FA)
            maker = RoleList.maker
            checker = RoleList.checker

            # print('role_arr',role_arr)

            if checker in role_arr:
                condition = Q(assetvalue_status=AssetRequestStatus.PENDING) & \
                            Q(assetdetails__status=AssetStatus.ACTIVE) & \
                            Q(assetdetails__requestfor=AssetRequestfor.VALUEREDUCTION,assetdetails__requeststatus=AssetRequestStatus.PENDING)
            else:
                return assetid_list


            if 'assetdetails_value' in filter_json:
                condition&= Q(asset_value=filter_json['assetdetails_value'])
            if 'branch_id' in filter_json:
                condition&= Q(assetdetails__branch_id=filter_json['branch_id'])
            if 'assetcat_id' in filter_json:
                condition&= Q(assetdetails__assetcat_id=filter_json['assetcat_id'])
            if 'barcode' in filter_json:
                condition&= Q(assetdetails__barcode__icontains=filter_json['barcode'])
            if 'capdate' in filter_json:
                condition&= Q(assetdetails__capdate=filter_json['capdate'])
            assetvalue_data = AssetValue.objects.filter(condition).order_by('-assetdetails_id'
                                                                      )[vys_page.get_offset():vys_page.get_query_limit()]

            if len(assetvalue_data) > 0 :
                for assetval in assetvalue_data:
                    assetvalue_resp = AssetValueResponse()
                    #assetvalue
                    assetvalue_resp.set_id(assetval.id)
                    assetvalue_resp.set_oldvalue(assetval.asset_oldvalue)
                    assetvalue_resp.set_assetvalue(assetval.asset_value)
                    assetvalue_resp.set_reason(assetval.reason)
                    assetvalue_resp.set_assetvalue_date(assetval.date)
                    asst_req_stat=AssetRequestStatus()
                    assetvalue_resp.set_valuechange_status(asst_req_stat.get_val(assetval.assetvalue_status))
                    #assetdetails
                    assetdetails = assetval.assetdetails # assetdetails FK details get
                    assetvalue_resp.set_capdate(assetdetails.capdate)
                    assetvalue_resp.set_assetdetails_id(assetdetails.id)
                    assetvalue_resp.set_assetdtls_id(assetdetails.assetdetails_id)
                    assetvalue_resp.set_assetdetails_status(assetdetails.assetdetails_status)
                    assetvalue_resp.set_assetdetails_value(assetdetails.assetdetails_value)
                    assetvalue_resp.set_request_for(asset_requestfor_status(assetdetails.requestfor))
                    # print('requeststatus',assetdetails.requeststatus)
                    #assetvalue_resp.set_request_status(asset_requeststatus(assetdetails.requeststatus))

                    assetvalue_resp.set_barcode(assetdetails.barcode)
                    #assetheader
                    # assetheader_data = AssetHeader.objects.filter(barcode=assetdetails.barcode)[0]
                    assetvalue_resp.set_cost_total(assetdetails.assetheader.costtot)
                    assetvalue_resp.set_value_total(assetdetails.assetheader.valuetot)
                    # asset Location
                    location_serv = AssetLocationService(scope)
                    assetvalue_resp.set_location(location_serv.fetch_assetlocation(assetdetails.assetlocation_id))
                    # employee_branch
                    emp_branch = FaApiService(scope)
                    assetvalue_resp.branch = (emp_branch.fetch_branch(assetval.assetdetails.branch_id))
                    #assetcat
                    assetcat=assetval.assetdetails.assetcat # assetcat FK details get
                    assetvalue_resp.set_assetcat_subcatname(assetcat.subcatname)
                    #approval flag
                    #print(int(assetcat.created_by) , int(emp_id),'  created_by')
                    if int(assetval.created_by) == int(emp_id):
                        approval_flage=False
                    else:
                        approval_flage=True
                    assetvalue_resp.set_approval_flage(approval_flage)

                    assetid_list.append(assetvalue_resp)
                vpage = NWisefinPaginator(assetvalue_data, vys_page.get_index(), 10)
                assetid_list.set_pagination(vpage)
        except Exception  as excep:
            logger.info('FAL_ASSETVALCHANGE_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

        return assetid_list


    def valuechange_summary(self, vys_page,filter_json,emp_id,request=None):
        try:
            scope=request.scope
            assetid_list = NWisefinList()

            module_permission = ModulePermission(scope)
            role_arr = module_permission.employee_modulerole(emp_id, ModuleList.FA)
            # print(role_arr, ' role_arr')
            maker = RoleList.maker
            checker = RoleList.checker
            if maker in role_arr:
                condition =  Q(assetdetails_status=AssetStatus.ACTIVE,
                                 requestfor__in=[AssetRequestfor.DEFAULT,
                                            AssetRequestfor.NEW],status=AssetStatus.ACTIVE)
                asst_val_ids=AssetValue.objects.filter(status=1,assetvalue_status=AssetRequestStatus.PENDING)
                asst_val_id_list=[]
                for asst in asst_val_ids:
                    if asst.asset_barcode not in asst_val_id_list:
                        asst_val_id_list.append(asst.asset_barcode)
            else:
                return assetid_list
            if 'assetdetails_value' in filter_json:
                condition &= Q(assetheader__valuetot=filter_json['assetdetails_value'])
            if 'branch_id' in filter_json:
                condition &= Q(branch_id=filter_json['branch_id'])
            if 'assetcat_id' in filter_json:
                condition &= Q(assetcat_id=filter_json['assetcat_id'])
            if 'barcode' in filter_json:
                condition &= Q(barcode__icontains=filter_json['barcode'])
            if 'capdate' in filter_json:
                condition &= Q(capdate=filter_json['capdate'])

            # assetdtl_data = AssetDetails.objects.filter(condition).order_by('id')[
            #                 vys_page.get_offset():vys_page.get_query_limit()]
            # print('condition ',condition)

            bulk_tuple=tuple(AssetDetails.objects.filter(condition).exclude(barcode__in=asst_val_id_list).order_by('-id','-assetdetails_id').values('id','barcode'))
            asset_dtl_datas = AssetDetails.objects.filter(condition)


            data_count=0
            barcode_list=list()
            id_list=list()
            stop_point=int(vys_page.get_query_limit())


            for asset_data in bulk_tuple:
                if data_count == int(stop_point):
                    break
                if asset_data['barcode'] not in barcode_list:
                    asset_data=AssetDetails.objects.filter(barcode=asset_data['barcode']).last()
                    id_list.append(asset_data.id)
                    data_count=data_count+1


            #if len(id_list) <= int(vys_page.get_query_limit()):
            get_list=id_list[int(vys_page.get_offset()):int(vys_page.get_query_limit())]
            # else:
            #     get_list = id_list[0:int(vys_page.get_query_limit())]


            assetdtl_data = AssetDetails.objects.filter(id__in=get_list,requestfor__in=[AssetRequestfor.DEFAULT,AssetRequestfor.NEW]).order_by('-id','-assetdetails_id')
            assetdtl_data.exclude()
            if len(assetdtl_data) > 0:
                for assecat in assetdtl_data:
                    assetdetls_data = AssetDetails.objects.filter(condition,barcode=assecat.barcode).order_by('-id','-assetdetails_id')[0]


                    assetvalue_resp = AssetValueResponse()
                    #assetdetails
                    assetvalue_resp.set_capdate(assetdetls_data.capdate)
                    assetvalue_resp.set_assetdetails_id(assecat.id)
                    assetvalue_resp.set_assetdtls_id(assecat.assetdetails_id)
                    assetvalue_resp.set_assetdetails_status(assetvaluedtl_status(assecat.status))
                    # assetvalue_resp.set_assetvalue(str(assecat.assetdetails_value))
                    asst_hdr = AssetHeader.objects.filter(id=assecat.assetheader_id)
                    if len(asst_hdr) > 0:
                        assetvalue_resp.set_assetvalue(str(asst_hdr[0].valuetot))
                    else:
                        continue
                    #assetvalue_resp.set_newvalue(str(assecat.assetdetails_value))
                    assetvalue_resp.set_barcode(assecat.barcode)
                    # product
                    fa_service_call = FaApiService(scope)
                    product_data = fa_service_call.fetch_product(assecat.product_id, emp_id, request=None)
                    assetvalue_resp.set_product_name(product_data.name)
                    # print('product_data ',product_data.name)
                    # asset Location
                    location_serv = AssetLocationService(scope)
                    assetvalue_resp.set_location(location_serv.fetch_assetlocation(assecat.assetlocation_id))
                    # employee_branch
                    emp_branch = FaApiService(scope)
                    assetvalue_resp.branch = (emp_branch.fetch_branch(assecat.branch_id))
                    # assetcat
                    assetcat = assecat.assetcat  # assetcat FK details get
                    assetvalue_resp.set_assetcat_id(assetcat.id)
                    assetvalue_resp.set_assetcat_subcatname(assetcat.subcatname)
                    assetid_list.append(assetvalue_resp)
                vpage = NWisefinPaginator(assetdtl_data, vys_page.get_index(), 10)
                assetid_list.set_pagination(vpage)
        except Exception  as excep:
            logger.info('FAL_ASSETVALCHANGE_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

        return assetid_list

    #@transaction.atomic(using='fa_service')
    def valuechange_approve(self,assetvalue_json,emp_id):
        try:
            with transaction.atomic(using=self._current_app_schema()):
                reason=None
                if 'reason' in assetvalue_json :
                    reason=assetvalue_json['reason']
                else:
                    err=Error()
                    err.set_code(ErrorMessage.REASON_CANT_BE_NONE)
                    err.set_description(ErrorDescription.REASON_CANT_BE_NONE)

                for i in assetvalue_json['assetdetails'] :
                    assetval = AssetValue.objects.filter(id=i['id'])[0]#assetdetails[0]
                    assetdtls=assetval.assetdetails
                    assetdtls_code=AssetDetails.objects.filter(barcode=assetdtls.barcode).order_by('-assetdetails_id')[0]
                    split_barcode = str(assetdtls_code.assetdetails_id.split('/')[0])
                    # print('split_barcode', split_barcode)
                    split_writeoffnumb = str(assetdtls_code.assetdetails_id.split('/')[-2])
                    split_valuechangenum = int(assetdtls_code.assetdetails_id.split('/')[-1]) + 1
                    split_valuechangenum = str(split_valuechangenum)
                    assetdetails_id = split_valuechangenum.zfill(len(split_valuechangenum) + 1)
                    # print('assetdetails_id', assetdetails_id)
                    assetdetails_id = split_barcode + '/' + split_writeoffnumb + '/' + assetdetails_id
                    # print(assetdetails_id)
                    # asset_old_value=float(assetdetails[0].assetdetails_value)
                    asset_old_value = float(assetdtls.assetheader.valuetot)
                    asset_new_value = float(i['new_value'])
                    if asset_old_value < asset_new_value:
                        source = AssetSource.FAValP
                        assetdetails_cost = asset_new_value - asset_old_value
                    elif asset_old_value > asset_new_value:
                        source = AssetSource.FAValN
                        assetdetails_cost = asset_old_value - asset_new_value

                    valuechange_convertdate = assetval.date.date()
                    cap_date = assetdtls.capdate
                    # d2 = datetime.strptime(d2, "%Y-%m-%d")
                    # print('valuechange_convertdate - cap_date   ', assetdtls.enddate.date()-valuechange_convertdate )

                    dep_date_cal = (365 /((assetdtls.enddate.date()-valuechange_convertdate).days + 1))* 100
                    depreciation_rate = round(dep_date_cal, 2)
                    assetcat=AssetCat.objects.get(id=assetdtls.assetcat_id)
                    if assetcat.deptype =='WDV':
                        dep=assetdtls.deprate
                    else:
                        dep=depreciation_rate
                    # print(depreciation_rate, ' depreciation_rate')
                    # print(assetdtls.deprate, ' current deprate')
                    header_data = AssetHeader.objects.filter(barcode=assetdtls.barcode)[0]
                    assetdtls_data = AssetDetails.objects.create(assetdetails_id=assetdetails_id,
                                                                 qty=assetdtls.qty,
                                                                 assetheader=header_data,
                                                                 barcode=assetdtls.barcode,
                                                                 date=assetdtls.date,
                                                                 assetcat_id=assetdtls.assetcat_id,
                                                                 assetgroup_id=assetdtls.assetgroup_id,
                                                                 product_id=assetdtls.product_id,
                                                                 cat=assetdtls.cat,
                                                                 subcat=assetdtls.subcat,
                                                                 assetdetails_value=assetdetails_cost,
                                                                 assetdetails_cost=assetdetails_cost,
                                                                 description=assetdtls.description,
                                                                 capdate=assetval.date,
                                                                 source=source,
                                                                 assetdetails_status=assetdtls.assetdetails_status,
                                                                 requestfor=AssetRequestfor.DEFAULT,
                                                                 requeststatus=AssetRequestStatus.APPROVED,
                                                                 assettfr_id=assetdtls.assettfr_id,
                                                                 assetsale_id=assetdtls.assetsale_id,
                                                                 not5k=assetdtls.not5k,
                                                                 assetowner=assetdtls.assetowner,
                                                                 lease_startdate=assetdtls.lease_startdate,
                                                                 lease_enddate=assetdtls.lease_enddate,
                                                                 impairasset_id=assetdtls.impairasset_id,
                                                                 impairasset=assetdtls.impairasset,
                                                                 writeoff_id=assetdtls.writeoff_id,
                                                                 assetcatchange_id=assetdtls.assetcatchange_id,
                                                                 assetvalue_id=assetdtls.assetvalue_id,
                                                                 assetcapdate_id=assetdtls.assetcapdate_id,
                                                                 assetsplit_id=assetdtls.assetsplit_id,
                                                                 assetmerge_id=assetdtls.assetmerge_id,
                                                                 assetcatchangedate=assetdtls.assetcatchangedate,
                                                                 reducedvalue=assetdtls.reducedvalue,
                                                                 branch_id=assetdtls.branch_id,
                                                                 assetlocation_id=assetdtls.assetlocation_id,
                                                                 assetdetails_bs=assetdtls.assetdetails_bs,
                                                                 assetdetails_cc=assetdtls.assetdetails_cc,
                                                                 deponhold=assetdtls.deponhold,
                                                                 deprate=dep,
                                                                 enddate=assetdtls.enddate,
                                                                 parent_id=assetdtls.parent_id,
                                                                 assetserialno=assetdtls.assetserialno,
                                                                 invoice_id=assetdtls.invoice_id,
                                                                 faclringdetails_id=assetdtls.faclringdetails_id,
                                                                 inwheader_id=assetdtls.inwheader_id,
                                                                 inwdetail_id=assetdtls.inwdetail_id,
                                                                 inwarddate=assetdtls.inwarddate,
                                                                 mepno=assetdtls.mepno,
                                                                 ponum=assetdtls.ponum,
                                                                 crnum=assetdtls.crnum,
                                                                 debit_id=assetdtls.debit_id,
                                                                 # imagepath = assetdetails_obj.get_imagepath(),
                                                                 vendorname=assetdtls.vendorname,
                                                                 status=AssetStatus.ACTIVE,
                                                                 created_by=emp_id,
                                                                 assetheader_id=assetdtls.assetheader_id)

                    assetdtl_data = AssetDetails.objects.filter(barcode=i['barcode'],
                                                                status=AssetStatus.ACTIVE,
                                                                requestfor=AssetRequestfor.VALUEREDUCTION)

                    if AssetRequestStatus.APPROVED == int(i['status']):
                        # assetvalue_update = AssetValue.objects.filter(assetdetails_id=assetdtl_data[0].id,
                        #                                             status=AssetRequestStatus.PENDING
                        #                                             )[0]
                        #cost=float(assetvalue_update.asset_value)-float(assetvalue_update.asset_value)
                        assethdr_data = AssetHeader.objects.filter(barcode=i['barcode']).update(
                            #costtot=cost,
                            astvalbeforedeptot=i['new_value'],
                            revisedcbtot=i['new_value'],
                            valuetot=i['new_value'],
                            costtot=i['new_value'],
                            updated_by=emp_id,
                            updated_date=now())

                        assetdtl_data = AssetDetails.objects.filter(barcode=i['barcode'],
                                                                    status=AssetStatus.ACTIVE,
                                                                    requestfor=AssetRequestfor.VALUEREDUCTION)
                        #here update the asset value id in asset details *** START
                        assetvalue_id_update = AssetValue.objects.filter(assetdetails_id=assetdtl_data[0].id,
                                                                    assetvalue_status=AssetRequestStatus.PENDING)[0]
                        assetdtl_update = AssetDetails.objects.filter(barcode=i['barcode']).update(
                                                assetvalue_id=assetvalue_id_update.id,
                                                updated_by=emp_id,
                                                updated_date=now())
                        # here update the asset value id in asset details *** END

                    assetvalue_data = AssetValue.objects.filter(assetdetails_id=assetdtl_data[0].id,
                                                                assetvalue_status=AssetRequestStatus.PENDING
                                                                )
                    assetvalue_data.update(
                        assetvalue_status=AssetRequestStatus.APPROVED,
                        reason=reason,
                        updated_by=emp_id,
                        updated_date=now())
                    if AssetRequestStatus.APPROVED == int(i['status']):
                        assetdtl_data.update(
                            requestfor=AssetRequestfor.DEFAULT,
                            requeststatus=AssetRequestStatus.APPROVED,
                            updated_by=emp_id,
                            updated_date=now())
                    else:
                        assetdtl_data.update(
                            assetvalue=assetvalue_data[0].asset_oldvalue,
                            requestfor=AssetRequestfor.DEFAULT,
                            requeststatus=AssetRequestStatus.REJECTED,
                            updated_by=emp_id,
                            updated_date=now())

                    #reverce the status
                    # assetdtl_olddata = AssetDetails.objects.filter(barcode=i['barcode'],
                    #                                             status=AssetStatus.PROCESSED)
                    #
                    #
                    # assetdtl_lis=list(assetdtl_olddata.values_list('id', flat=True))
                    #
                    # assetvalue_olddata = AssetValue.objects.filter(assetdetails_id__in=assetdtl_lis,
                    #                                                status=AssetStatus.PROCESSED
                    #                                                ).update(
                    #     status=AssetStatus.ACTIVE,
                    #     updated_by=emp_id,
                    #     updated_date=now())
                    #
                    # assetdtl_olddata.update(
                    #     status=AssetStatus.ACTIVE,
                    #     updated_by=emp_id,
                    #     updated_date=now())

                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)

        except Exception  as excep:
            logger.info('FAL_ASSETVALCHANGE_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

        return success_obj
    def valuechange_reject(self,assetvalue_json,emp_id):
        try:
            with transaction.atomic(using=self._current_app_schema()):
                reason=None
                if 'reason' in assetvalue_json :
                    reason=assetvalue_json['reason']
                else:
                    res=Error()
                    res.set_code(ErrorMessage)
                for i in assetvalue_json['assetdetails'] :
                    if AssetRequestStatus.REJECTED == int(i['status']):

                        # assetdtl_data = AssetDetails.objects.filter(barcode=i['barcode'],
                        #                                             requeststatus=AssetRequestStatus.PENDING,
                        #                                             requestfor=AssetRequestfor.VALUEREDUCTION
                        #                                             )
                        # assetdtl_data.update( status=AssetStatus.IN_ACTIVE,
                        #                         updated_by=emp_id,
                        #                         updated_date=now())
                        # # here update the asset value id in asset details *** END

                        assetvalue_data = AssetValue.objects.filter(id=i['id'],
                                                                assetvalue_status=AssetRequestStatus.PENDING
                                                                )[0]
                        assetvalue_data.status=i['status']
                        assetvalue_data.assetvalue_status=i['status']
                        assetvalue_data.reason=reason
                        assetvalue_data.updated_by=emp_id
                        assetvalue_data.updated_date=now()
                        assetvalue_data.save()
                        asst_data=AssetDetails.objects.get(id=assetvalue_data.assetdetails.id)
                        asst_data.requestfor=AssetRequestfor.DEFAULT
                        asst_data.requeststatus=AssetRequestStatus.REJECTED
                        asst_data.save()
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)

        except Exception  as excep:
            logger.info('FAL_ASSETVALCHANGE_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

        return success_obj


    def valuechange_currentdate_validation(self,assetdtls_json):
        for assetdetails_obj in assetdtls_json['assetdetails']:
            # print(assetdetails_obj,'assetdetails_obj')

            assetdetails = AssetDetails.objects.filter(barcode=assetdetails_obj['barcode'],
                                                       status=AssetStatus.ACTIVE).order_by('-id', '-assetdetails_id')[0]

            cap_date= assetdetails.capdate
            today_date=now()
            # print(cap_date,'  cap_date ',type(cap_date))
            # print(today_date.date(),'  today_date',type(today_date.date()))


            if cap_date == today_date.date():
                return True

        return False


    def valuechange_validation(self,assetdtls_json):
        for assetdetails_obj in assetdtls_json['assetdetails']:
            # print(assetdetails_obj,'assetdetails_obj')

            assetdetails = AssetDetails.objects.filter(barcode=assetdetails_obj['barcode'],
                                                       status=AssetStatus.ACTIVE).order_by('-id', '-assetdetails_id')[0]

            asset_currentvalue= assetdetails.assetdetails_value
            # print(assetdetails.id,'  assetdetails_id')
            # print(assetdetails.assetdetails_id,'  assetdetails_id1')
            # print(asset_currentvalue,'  asset_currentvalue')
            if float(asset_currentvalue) == float(assetdetails_obj['new_value']):
                return True

        return False

    def valuechange_capdate_validation(self,assetdtls_json):
        valuechange_date=datetime.strptime(assetdtls_json['valuechange_date'], '%Y-%m-%d')
        # print(valuechange_date,'valuechange_date')
        for assetdetails_obj in assetdtls_json['assetdetails']:
            # print(assetdetails_obj,'assetdetails_obj')

            assetdetails = AssetDetails.objects.filter(barcode=assetdetails_obj['barcode'],
                                                           status=AssetStatus.ACTIVE).order_by('-id','-assetdetails_id')[0]

            capdate= assetdetails.capdate
            #capdate= datetime.strptime(capdate, '%Y-%m-%d')
            # print(capdate,'  capdate')
            print(assetdetails_obj['new_value'],'  assetdetails_obj[new_value]')
            if datetime(valuechange_date.year,valuechange_date.month,valuechange_date.day) \
                    < datetime(capdate.year,capdate.month,capdate.day) :
                return True

        return False




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
        audit_obj.set_relreftype(FaRefType.ASSETDETAILS)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)


    def valuechange_approver_validation(self,valuechange_json,approver_emp_id):
        assetdetails_list=valuechange_json['assetdetails']
        for i in assetdetails_list:
            condition=Q(assetdetails__barcode = i['barcode'],
            assetdetails__status = AssetStatus.ACTIVE,
            assetdetails__requestfor = AssetRequestfor.VALUEREDUCTION)
            assetvalue_data = AssetValue.objects.filter(condition)[0]
            created_by=int(assetvalue_data.created_by)
            print('created_by  ',int(approver_emp_id) , created_by)
            if int(approver_emp_id) == created_by:
                return True
        return False