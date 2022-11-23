import traceback
from datetime import datetime, date

import pandas as pd
from dateutil.relativedelta import relativedelta
from dateutil.parser import parser
import tzlocal
from django.db import IntegrityError, Error, transaction
from django.db.models import Q
from faservice.data.response.assetidresponse import AssetidResponse
from faservice.data.response.assetvaluechangeresponse import AssetValueResponse
from faservice.models.famodels import AssetId, AssetValue, AssetDetails, AssetHeader, AssetTFR, AssetCat
from faservice.service.assetlocationservice import AssetLocationService
from faservice.service.faauditservice import FaAuditService
from faservice.util.FaApiService import  FaApiService, DictObj
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
from utilityservice.service.api_service import ApiService

class AssetTransfer(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
    def fetch_assettransfer_list(self, vys_page,filter_json,emp_id,request=None):
        scope=request.scope
        try:
            assetid_list = NWisefinList()

            module_permission = ModulePermission(scope)
            role_arr = module_permission.employee_modulerole(emp_id, ModuleList.FA)
            print(role_arr,' role_arr')
            maker = RoleList.maker
            checker = RoleList.checker

            if maker in role_arr :
                condition =  Q(assetdetails_status=AssetStatus.ACTIVE,
                                  status=AssetStatus.ACTIVE,requestfor__in=[AssetRequestfor.DEFAULT,
                                                                                      AssetRequestfor.NEW])
            else:
                return assetid_list


            if 'assetdetails_value' in filter_json:
                condition&= Q(assetheader__valuetot=filter_json['assetdetails_value'])
            if 'branch_id' in filter_json:
                condition&= Q(branch_id=filter_json['branch_id'])
            if 'assetcat_id' in filter_json:
                condition&= Q(assetcat_id=filter_json['assetcat_id'])
            if 'barcode' in filter_json:
                condition&= Q(barcode__icontains=filter_json['barcode'])
            if 'capdate' in filter_json:
                condition&= Q(capdate=filter_json['capdate'])

            # assetdtl_data = AssetDetails.objects.filter(condition).order_by('-id','-assetdetails_id')

            bulk_tuple = AssetDetails.objects.filter(condition).values().order_by('-id','-assetdetails_id')
            df=pd.DataFrame.from_records(bulk_tuple)
            if len(bulk_tuple)>0:
                agg=dict.fromkeys(bulk_tuple[0].keys(),'first')
                df=df.groupby('barcode').agg(agg)
                df=df[vys_page.get_offset():vys_page.get_query_limit()]
                df=df.to_dict('records')
            else:
                return assetid_list
            assetdtl_data=None
            dict_obj=DictObj()
            for assetfr in df:
                assetfr=dict_obj.get_obj(assetfr)
                assetvalue_resp = AssetValueResponse()


                #assetvalue
                # assetvalue_resp.set_id(assetval.id)
                # assetvalue_resp.set_oldvalue(assetval.asset_oldvalue)
                # assetvalue_resp.set_assetvalue(assetval.asset_value)
                # assetvalue_resp.set_reason(assetval.reason)
                # assetvalue_resp.set_assetvalue_date(assetval.date)
                #assetdetails

                assetvalue_resp.set_capdate(assetfr.capdate)
                assetvalue_resp.set_assetdetails_id(assetfr.id)
                assetvalue_resp.set_assetdtls_id(assetfr.assetdetails_id)
                assetvalue_resp.set_assetdetails_status(assetvaluedtl_status(assetfr.status))
                #assetvalue_resp.set_status(assetrequst_status(assetfr.status))
                try:
                    asst_header=AssetHeader.objects.get(id=assetfr.assetheader_id)
                    assetvalue_resp.set_assetdetails_value(asst_header.valuetot)
                except:
                    logger.info('FAL_ASSETTFR_EXCEPT:{}'.format(traceback.print_exc()))
                    continue
                assetvalue_resp.set_barcode(assetfr.barcode)
                #product
                fa_service_call=FaApiService(scope)
                product_data=fa_service_call.fetch_product(assetfr.product_id,emp_id,request=None)
                assetvalue_resp.set_product_name(product_data.name)
                #print('product_data ',product_data.name)
                # asset Location
                location_serv = AssetLocationService(scope)
                assetvalue_resp.set_location(location_serv.fetch_assetlocation(assetfr.assetlocation_id))
                # employee_branch
                emp_branch = FaApiService(scope)
                assetvalue_resp.branch = (emp_branch.fetch_branch(assetfr.branch_id))
                #assetcat
                assetcat=AssetCat.objects.filter(id=assetfr.assetcat_id).values()[0] # assetcat FK details get
                assetvalue_resp.set_assetcat_id(assetcat)
                assetvalue_resp.created_date=assetfr.created_date
                assetvalue_resp.set_assetcat_subcatname(assetcat['subcatname'])
                assetid_list.append(assetvalue_resp)
            vpage = NWisefinPaginator(df, vys_page.get_index(), 10)
            assetid_list.set_pagination(vpage)

        except Exception  as excep:
            logger.info('FAL_ASSETTFR_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

        return assetid_list

    def get_assettransfer_list(self, vys_page,filter_json,emp_id,request):
        scope=request.scope
        try:
            assetid_list = NWisefinList()

            module_permission = ModulePermission(scope)
            role_arr = module_permission.employee_modulerole(emp_id, ModuleList.FA)
            print(role_arr,' role_arr')
            maker = RoleList.maker
            checker = RoleList.checker

            if maker in role_arr :
                condition = Q()
            else:
                return assetid_list

    #        condition = Q(status=AssetStatus.ACTIVE)



            if 'assetdetails_value' in filter_json:
                condition&= Q(assetdetails__assetdetails_value=filter_json['assetdetails_value'])
            if 'branch_id' in filter_json:
                condition&= Q(assetdetails__branch_id=filter_json['branch_id'])
            if 'assetcat_id' in filter_json:
                condition&= Q(assetdetails__assetcat_id=filter_json['assetcat_id'])
            if 'barcode' in filter_json:
                condition&= Q(assetdetails__barcode__icontains=filter_json['barcode'])
            if 'capdate' in filter_json:
                condition&= Q(assetdetails__capdate=filter_json['capdate'])

            assetdtl_data = AssetTFR.objects.filter(condition).exclude(status=0).order_by('-id')[
                              vys_page.get_offset():vys_page.get_query_limit()]



            if len(assetdtl_data) > 0 :
                for assetfr in assetdtl_data:
                    print(assetfr.assetdetails_id,'  assetfr.assetdetails_id')
                    assetvalue_resp = AssetValueResponse()
                    #transfer
                    assetdetail=AssetDetails.objects.filter(assetdetails_id=assetfr.newassetdetailsid)
                    if len(assetdetail) > 0:
                        assetdetail=assetdetail[0]
                    else:
                        continue

                    emp_branch = FaApiService(scope)
                    from_branch = emp_branch.fetch_branch(assetfr.assetdetails.branch_id, request)
                    newassetdetails_data = AssetDetails.objects.filter(assetdetails_id=assetfr.newassetdetailsid)[0]
                    to_branch = emp_branch.fetch_branch(newassetdetails_data.branch_id, request)
                    assetvalue_resp.assettfr_status =(assetrequst_status(assetfr.assettfr_status))
                    assetvalue_resp.status =(assetrequst_status(assetfr.status))
                    assetvalue_resp.set_assetbranch_from(from_branch.name)
                    assetvalue_resp.set_assetbranch_to(to_branch.name)
                    assetvalue_resp.set_reason(assetfr.reason)
                    # emp_code=assetfr.emp_code
                    common_serv=ApiService(self._scope())
                    employee=common_serv.fetch_rm_name(request,assetfr.emp_code,vys_page)
                    assetvalue_resp.empname=employee.data[0].full_name
                    # emp_code=assetfr.reason

                    #assetvalue
                    # assetvalue_resp.set_id(assetval.id)
                    # assetvalue_resp.set_oldvalue(assetval.asset_oldvalue)
                    # assetvalue_resp.set_assetvalue(assetval.asset_value)
                    # assetvalue_resp.set_reason(assetval.reason)
                    # assetvalue_resp.set_assetvalue_date(assetval.date)
                    #assetdetails
                    asststatus=AssetStatus()
                    assetvalue_resp.set_capdate(assetdetail.capdate)
                    assetvalue_resp.set_assetdetails_id(assetdetail.id)
                    assetvalue_resp.set_assetdtls_id(assetdetail.assetdetails_id)
                    assetvalue_resp.set_assetdetails_status(asststatus.get_val(assetdetail.assetdetails_status))
                    assetvalue_resp.set_assetdetails_value(assetdetail.assetheader.valuetot)
                    assetvalue_resp.set_barcode(assetdetail.barcode)
                    #product
                    fa_service_call=FaApiService(scope)
                    try:
                        product_data=fa_service_call.fetch_product(assetdetail.product_id,emp_id,request=None)
                        assetvalue_resp.set_product_name(product_data.name)
                    except:
                        assetvalue_resp.set_product_name(assetdetail.name)
                    # print('product_data ',product_data.name)
                    # asset Location
                    location_serv = AssetLocationService(scope)
                    assetvalue_resp.set_location(location_serv.fetch_assetlocation(assetdetail.assetlocation_id))
                    # employee_branch
                    fa_obj=FaApiService(scope)
                    try:
                        assetvalue_resp.branch = (fa_obj.fetch_branch(assetdetail.branch_id))
                    except:
                        continue
                    assetcat=assetdetail.assetcat
                    assetvalue_resp.set_assetcat_id(assetcat.id)
                    assetvalue_resp.set_assetcat_subcatname(assetcat.subcatname)
                    assetid_list.append(assetvalue_resp)
                vpage = NWisefinPaginator(assetdtl_data, vys_page.get_index(), 10)
                assetid_list.set_pagination(vpage)


        except Exception  as excep:
            logger.info('FAL_ASSETTRF_LIST_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

        return assetid_list


    def get_assettransfer_checker_list(self, vys_page, filter_json, emp_id,request):
        scope=request.scope
        try:
            assetid_list = NWisefinList()

            module_permission = ModulePermission(scope)
            role_arr = module_permission.employee_modulerole(emp_id, ModuleList.FA)
            print(role_arr, ' role_arr')
            maker = RoleList.maker
            checker = RoleList.checker

            if checker in role_arr:
                condition = Q(assettfr_status=AssetRequestStatus.PENDING,status=AssetRequestStatus.PENDING)
            else:
                return assetid_list

        #    condition = Q(status=AssetStatus.IN_PROCESS,requestfor=AssetRequestfor.TRANSFER)

            if 'assetdetails_value' in filter_json:
                condition &= Q(assetdetails__assetdetails_value=filter_json['assetdetails_value'])
            if 'branch_id' in filter_json:
                condition &= Q(assetdetails__branch_id=filter_json['branch_id'])
            if 'assetcat_id' in filter_json:
                condition &= Q(assetdetails__assetcat_id=filter_json['assetcat_id'])
            if 'barcode' in filter_json:
                condition &= Q(assetdetails__barcode__icontains=filter_json['barcode'])
            if 'capdate' in filter_json:
                condition &= Q(assetdetails__capdate=filter_json['capdate'])

            assetdtl_data = AssetTFR.objects.filter(condition).order_by('-id')[
                            vys_page.get_offset():vys_page.get_query_limit()]

            if len(assetdtl_data) > 0:
                for assetfr in assetdtl_data:
                    assetvalue_resp = AssetValueResponse()
                    # transfer
                    assettransfer_data = AssetDetails.objects.filter(assetdetails_id=assetfr.newassetdetailsid)
                    if len(assettransfer_data) > 0:
                            assettransfer_data = assettransfer_data[0]
                    else:
                        continue
                    emp_branch = FaApiService(scope)
                    from_branch = emp_branch.fetch_branch(assetfr.assetdetails.branch_id,request)
                    newassetdetails_data=AssetDetails.objects.filter(assetdetails_id=assetfr.newassetdetailsid)[0]
                    to_branch = emp_branch.fetch_branch(newassetdetails_data.branch_id,request)
                    asst_loc=AssetLocationService(scope)
                    # from_branch=asst_loc.fetch_assetlocation(assetfr.assettfr_from)
                    # to_branch=asst_loc.fetch_assetlocation(assetfr.assettfr_to)
                    assetvalue_resp.assettfr_status = (assetvaluedtl_status(assetfr.assettfr_status))
                    assetvalue_resp.status = (assetrequst_status(assetfr.status))
                    assetvalue_resp.set_assetbranch_from(from_branch.name)
                    assetvalue_resp.set_assetbranch_to(to_branch.name)
                    assetvalue_resp.tfr_id=(assetfr.id)
                    assetvalue_resp.set_reason(assetfr.reason)

                    # assetvalue
                    # assetvalue_resp.set_id(assetval.id)
                    # assetvalue_resp.set_oldvalue(assetval.asset_oldvalue)
                    # assetvalue_resp.set_oldvalue(assetval.asset_oldvalue)
                    # assetvalue_resp.set_assetvalue(assetval.asset_value)
                    # assetvalue_resp.set_reason(assetval.reason)
                    # assetvalue_resp.set_assetvalue_date(assetval.date)
                    # assetdetails

                    assetvalue_resp.set_capdate(assettransfer_data.capdate)
                    assetvalue_resp.set_assetdetails_id(assettransfer_data.id)
                    assetvalue_resp.set_assetdtls_id(assettransfer_data.assetdetails_id)
                    assetvalue_resp.set_assetdetails_status(assetvaluedtl_status(assettransfer_data.status))
                    assetvalue_resp.set_assetdetails_value(assettransfer_data.assetheader.valuetot)
                    assetvalue_resp.set_barcode(assettransfer_data.barcode)
                    assetvalue_resp.set_request_for(asset_requestfor_status(assettransfer_data.requestfor))
                    # product
                    fa_service_call = FaApiService(scope)
                    product_data = fa_service_call.fetch_product(assettransfer_data.product_id, emp_id, request=None)
                    assetvalue_resp.set_product_name(product_data.name)
                    # print('product_data ',product_data.name)
                    # asset Location
                    location_serv = AssetLocationService(scope)
                    assetvalue_resp.set_location(location_serv.fetch_assetlocation(assetfr.assetdetails.assetlocation_id))
                    # employee_branch
                    emp_branch = FaApiService(scope)
                    assetvalue_resp.branch = (emp_branch.fetch_branch(assetfr.assetdetails.branch_id))
                    # assetcat
                    assetcat = assetfr.assetdetails.assetcat  # assetcat FK details get
                    assetvalue_resp.set_assetcat_id(assetcat.id)
                    assetvalue_resp.set_assetcat_subcatname(assetcat.subcatname)
                    if int(assetfr.created_by) == int(emp_id):
                        approval_flage=False
                    else:
                        approval_flage=True
                    assetvalue_resp.set_approval_flage(approval_flage)
                    assetid_list.append(assetvalue_resp)
                vpage = NWisefinPaginator(assetdtl_data, vys_page.get_index(), 10)
                assetid_list.set_pagination(vpage)
        except Exception  as excep:
            logger.info('FAL_ASSETTFR_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

        return assetid_list

    #@transaction.atomic(using='fa_service')
    def make_assettransfer(self, assetdtls_json, emp_id):
        try:
            with transaction.atomic(using=self._current_app_schema()):
                assettransfer_date = assetdtls_json['assettransfer_date']

                for assetdetails_obj in assetdtls_json['assetdetails']:
                    assetdetails = AssetDetails.objects.filter(assetdetails_id=assetdetails_obj['assetdetails_id'],).order_by('-assetdetails_id')
                    ###NAENTR
                    # assetdtls = assetdetails[0]
                    assetdetails.update(
                        requestfor=AssetRequestfor.TRANSFER,
                        requeststatus=AssetRequestStatus.PENDING
                    )
                    common_api = ApiService(self._scope())
                    employee_code = common_api.fetch_emp_id(int(assetdtls_json['empid'])).code
                    asset_Header=AssetHeader.objects.get(barcode=assetdetails[0].barcode)
                    asset_Header.emp_code=employee_code
                    asset_Header.save()
                    for i in range(2):
                        if i == 1:
                            source_val = AssetSource.FATRANP
                            brn_id=assetdetails_obj['branch_id']
                            assetdtls = assetdetails[0]
                            assetdtls_code=AssetDetails.objects.filter(barcode=assetdtls.barcode).order_by('-assetdetails_id')[0]
                            split_barcode = str(assetdtls_code.assetdetails_id.split('/')[0])
                            split_writeoffnumb = str(assetdtls_code.assetdetails_id.split('/')[-2])
                            split_valuechangenum = int(assetdtls_code.assetdetails_id.split('/')[-1]) + 1
                            split_valuechangenum = str(split_valuechangenum)
                            assetdetails_id = split_valuechangenum.zfill(len(split_valuechangenum) + 1)
                            assetdetails_id = split_barcode + '/' + split_writeoffnumb + '/' + assetdetails_id
                            bs =assetdetails_obj['bs_id']
                            cc =assetdetails_obj['cc_id']
                            loc=assetdetails_obj['location_id']
                        if i == 0:
                            source_val = AssetSource.FATRANN

                            assetdtls = assetdetails[0]
                            brn_id=assetdtls.branch_id
                            split_barcode = str(assetdtls.assetdetails_id.split('/')[0])
                            split_writeoffnumb = str(assetdtls.assetdetails_id.split('/')[-2])
                            split_valuechangenum = int(assetdtls.assetdetails_id.split('/')[-1]) + 1
                            split_valuechangenum = str(split_valuechangenum)
                            assetdetails_id = split_valuechangenum.zfill(len(split_valuechangenum) + 1)
                            assetdetails_id = split_barcode + '/' + split_writeoffnumb + '/' + assetdetails_id
                            bs=assetdtls.assetdetails_bs
                            cc=assetdtls.assetdetails_cc
                            loc=assetdtls.assetlocation_id

                        diff = assetdtls.enddate -datetime.strptime(assettransfer_date, "%Y-%m-%d").astimezone(tzlocal.get_localzone())
                        dep_rate_cal = (365 / (diff.days)) * 100
                        asst_dep_rate = dep_rate_cal
                        assettransfer_condate = datetime.strptime(assettransfer_date, "%Y-%m-%d").date()
                        enddate = assetdtls.enddate.date()
                        assetdtls_data = AssetDetails.objects.create(assetdetails_id=assetdetails_id,
                                                                     qty=assetdtls.qty,
                                                                     assetheader=assetdtls.assetheader,
                                                                     barcode=assetdtls.barcode,
                                                                     date=assetdtls.date,
                                                                     assetcat_id=assetdtls.assetcat_id,
                                                                     assetgroup_id=assetdtls.assetgroup_id,
                                                                     product_id=assetdtls.product_id,
                                                                     cat=assetdtls.cat,
                                                                     subcat=assetdtls.subcat,
                                                                     assetdetails_value=assetdtls.assetheader.valuetot,
                                                                     assetdetails_cost=assetdtls.assetheader.costtot,
                                                                     description=assetdtls.description,
                                                                     capdate=assettransfer_date,
                                                                     source=source_val,
                                                                     assetdetails_status=assetdtls.assetdetails_status,
                                                                     requestfor=AssetRequestfor.TRANSFER,
                                                                     requeststatus=AssetRequestStatus.PENDING,
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
                                                                     branch_id=brn_id,
                                                                     assetlocation_id=loc,
                                                                     assetdetails_bs=bs,
                                                                     assetdetails_cc=cc,
                                                                     deponhold=assetdtls.deponhold,
                                                                     # deprate=asst_dep_rate,
                                                                     deprate=assetdtls.deprate,
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
                                                                     reason=assetdtls_json['reason'],
                                                                     # imagepath = assetdetails_obj.get_imagepath(),
                                                                     vendorname=assetdtls.vendorname,
                                                                     status=AssetStatus.ACTIVE,
                                                                     created_by=emp_id)

                    self.create_assettransfer(assetdtls, assetdetails_obj,assetdtls_json,assetdetails_id, emp_id)

                    assetdetails.update(status=AssetStatus.IN_ACTIVE)

                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.CREATE_MESSAGE)

        except Exception  as excep:
            logger.info('FAL_ASSETTFR_EXCEPT:{}'.format(traceback.print_exc()))
            traceback.print_exc()
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj
        return success_obj

    def assettransfer_capdate_validation(self, assetdtls_json):
        assettransfer_date = datetime.strptime(assetdtls_json['assettransfer_date'], '%Y-%m-%d')
        print(assettransfer_date, 'valuechange_date')
        for assetdetails_obj in assetdtls_json['assetdetails']:
            print(assetdetails_obj, 'assetdetails_obj')

            assetdetails = AssetDetails.objects.filter(assetdetails_id=assetdetails_obj['assetdetails_id'],
                                                       status=AssetStatus.ACTIVE)[0]

            capdate = assetdetails.capdate
            # capdate= datetime.strptime(capdate, '%Y-%m-%d')
            print(capdate, '  capdate')

            if datetime(assettransfer_date.year, assettransfer_date.month, assettransfer_date.day) \
                    < datetime(capdate.year, capdate.month, capdate.day):
                return True

        return False

    def assettransfer_date_validation(self, assetdtls_json):
        assettransfer_date = datetime.strptime(assetdtls_json['assettransfer_date'], '%Y-%m-%d')
        print(assettransfer_date, 'valuechange_date')

        today_date=date.today()
        if datetime(assettransfer_date.year, assettransfer_date.month, assettransfer_date.day) \
                > datetime(today_date.year, today_date.month, today_date.day):
            return True

        return False

    def create_assettransfer(self,assetdetails, assetdetails_obj,assetdtls_json,newassetdetailsid, emp_id):
        reason=None
        if 'reason' in assetdtls_json:
            reason=assetdtls_json['reason']
        chk_assttfr=AssetTFR.objects.filter(assetdetails_id = assetdetails.id).exclude(assettfr_status__in=[1,3],status=0)
        # if len(chk_assttfr)>0:
        #     chk_assttfr.update(status=0)
        common_api = ApiService(self._scope())
        employee_code=common_api.fetch_emp_id(int(assetdtls_json['empid'])).code
        assettransfer_data = AssetTFR.objects.create(assetdetails_id = assetdetails.id,
                                                    date = assetdtls_json['assettransfer_date'],
                                                    assettfr_from=assetdetails.assetlocation_id,
                                                    assettfr_to=assetdetails_obj['location_id'],
                                                    reason = reason,
                                                    newassetdetailsid = newassetdetailsid,
                                                    assettfr_value=assetdetails.assetdetails_value,
                                                    created_by = emp_id,
                                                    assettfr_status = AssetRequestStatus.PENDING,
                                                    emp_code=employee_code,
                                                    status = AssetRequestStatus.PENDING)


    def transfer_approver_validation(self,assetdtls_json,approver_emp_id):
        for trnfr in assetdtls_json['assetdetails']:
            condition=Q(newassetdetailsid=trnfr['assetdetails_id'])
            assetvalue_data = AssetTFR.objects.filter(condition).exclude(status=0)[0]
            created_by=int(assetvalue_data.created_by)
            print('created_by  ',int(approver_emp_id) , created_by)
            if int(approver_emp_id) == created_by:
                return True

        return False

    #@transaction.atomic(using='fa_service')
    def transfer_approve(self, assetdtls_json, emp_id):
        try:
            with transaction.atomic(using=self._current_app_schema()):
                reason=None
                if 'reason' in assetdtls_json:
                    reason=assetdtls_json['reason']
                for trnfr in assetdtls_json['assetdetails']:
                    assettransfer_data = AssetTFR.objects.filter(newassetdetailsid=trnfr['assetdetails_id'])
                    old_assetdetails_id=assettransfer_data[0].assetdetails_id

                    assettransfer_data.update(assettfr_status = trnfr['status'],
                                              reason=reason,
                                              status = trnfr['status'])

                    # old_assettransfer_data = AssetTFR.objects.filter(assetdetails_id=old_assetdetails_id).update(
                    #                           assettfr_status = trnfr['status'],
                    #                           status = trnfr['status'])
                    if int(trnfr['status']) == 1:
                        new_assetdtls_data = AssetDetails.objects.filter(barcode=trnfr['assetdetails_id'][:-6],requestfor=AssetRequestfor.TRANSFER).update(
                                                    requestfor=AssetRequestfor.DEFAULT,
                                                    requeststatus=AssetRequestStatus.APPROVED,
                                                    updated_by=emp_id,
                                                    updated_date=now())
                        asset_data=AssetDetails.objects.filter(barcode=trnfr['assetdetails_id'][:-6],requestfor=AssetRequestfor.TRANSFER).update(
                            requestfor=AssetRequestfor.DEFAULT,
                            requeststatus=AssetRequestStatus.APPROVED
                        )

                    if int(trnfr['status']) == 3:
                        asset_data = AssetDetails.objects.filter(barcode=trnfr['assetdetails_id'][:-6],source__in=[AssetSource.FATRANP,AssetSource.FATRANN],
                                                                 requestfor=AssetRequestfor.TRANSFER).update(
                            requestfor=AssetRequestfor.DEFAULT,
                            requeststatus=AssetRequestStatus.REJECTED,
                            assetdetails_status=AssetStatus.IN_ACTIVE,
                            status=AssetStatus.IN_ACTIVE
                        )
                        asset_data=AssetDetails.objects.filter(barcode=trnfr['assetdetails_id'][:-6])
                        old_assetdtls_data = AssetDetails.objects.filter(id=old_assetdetails_id).update(
                                                    status=AssetStatus.ACTIVE,
                                                    requeststatus=AssetRequestStatus.REJECTED,
                                                    requestfor=AssetRequestfor.DEFAULT,
                                                    updated_by=emp_id,
                                                    updated_date=now())


                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)

        except Exception  as excep:
            logger.info('FAL_ASSETTFR_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

        return success_obj



    def transfer_currentdate_validation(self,assetdtls_json):
        for assetdetails_obj in assetdtls_json['assetdetails']:
            print(assetdetails_obj,'assetdetails_obj')

            assetdetails = AssetDetails.objects.filter(assetdetails_id=assetdetails_obj['assetdetails_id'],
                                                       status=AssetStatus.ACTIVE).order_by('-id', '-assetdetails_id')[0]

            cap_date= assetdetails.capdate
            today_date=now()
            print(cap_date,'  cap_date ',type(cap_date))
            print(today_date.date(),'  today_date',type(today_date.date()))

            if cap_date == today_date.date():
                return True

        return False