import traceback
from datetime import datetime, date, timedelta
from django.db import IntegrityError, Error, transaction
from django.db.models import Q
from faservice.data.response.assetidresponse import AssetidResponse
from faservice.data.response.assetvaluechangeresponse import AssetValueResponse
from faservice.data.response.categorychangeresponse import CategoryChangeResponse
from faservice.models.famodels import AssetId, AssetValue, AssetDetails, AssetHeader, AssetTFR, AssetCatChange, AssetCat
from faservice.service.assetcatservice import AssetCatService
from faservice.service.assetlocationservice import AssetLocationService
from faservice.service.faauditservice import FaAuditService
from faservice.util.FaApiService import ApiCall, ServiceCall, FaApiService
from faservice.util.fautil import FaModifyStatus, FaRefType, FaRequestStatusUtil, AssetRequestfor, AssetRequestStatus, \
    AssetStatus, AssetSource, assetvaluedtl_status, asset_requestfor_status, asset_requeststatus, assetrequst_status, \
    FaConst
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


class AssetCategoryChange(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
    #@transaction.atomic(using='fa_service')
    def make_categorychange(self, catchange_json,emp_id):
        try:
            with transaction.atomic(using=self._current_app_schema()):
                catchange_date=catchange_json['catchange_date']
                catchange_reason=None
                if 'reason' in catchange_json:
                    catchange_reason=catchange_json['reason']

                for cat_dict in catchange_json['assetdetails']:
                    asset_dtls=AssetDetails.objects.filter(assetdetails_id=cat_dict['assetdetails_id'])
                    asset_details=asset_dtls[0]
                    asset_dtls.update(requestfor=AssetRequestfor.ASSETCAT)
                    catchage= AssetCatChange.objects.create(
                        assetdetails_id = asset_details.id,
                        date = catchange_date,
                        reason = catchange_reason,
                        category = cat_dict['category_id'],
                        oldcat = asset_details.assetcat_id,
                        created_by = emp_id,
                        status=AssetRequestStatus.PENDING)

                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.CREATE_MESSAGE)

        except Exception  as excep:
            logger.info('FAL_ASSETCATCHANGE_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

        return success_obj


    def fetch_categorychange_list(self, vys_page,filter_json,emp_id,request=None):
        scope=request.scope
        try:
            assetid_list = NWisefinList()

            module_permission = ModulePermission(scope)
            role_arr = module_permission.employee_modulerole(emp_id, ModuleList.FA)
            print(role_arr,' role_arr')
            maker = RoleList.maker
            checker = RoleList.checker

            if maker in role_arr :
                condition = Q(assetdetails_status=AssetStatus.ACTIVE,
                            status=AssetRequestStatus.APPROVED, requestfor__in=[AssetRequestfor.DEFAULT,
                                                                      AssetRequestfor.NEW]) \
                            & Q(assetheader_id__isnull=False)
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

            # assetdtl_data = AssetDetails.objects.filter(condition).order_by('-id','-assetdetails_id')[
            #                   vys_page.get_offset():vys_page.get_query_limit()]

            print('condition',condition)

            bulk_tuple = tuple(AssetDetails.objects.filter(condition).values('id', 'barcode').order_by('-id', '-assetdetails_id'))

            data_count = 0
            barcode_list = list()
            id_list = list()
            stop_point = int(vys_page.get_query_limit())

            for asset_data in bulk_tuple:
                if data_count == int(stop_point):
                    break
                if asset_data['barcode'] not in barcode_list:
                    barcode_list.append(asset_data['barcode'])
                    id_list.append(asset_data['id'])
                    data_count = data_count + 1

            get_list = id_list[int(vys_page.get_offset()):int(vys_page.get_query_limit())]
            assetdtl_data = AssetDetails.objects.filter(id__in=get_list).order_by('-id')

            #print('condition',condition)

            if len(assetdtl_data) > 0 :
                for assecat in assetdtl_data:
                    print('assecat  ', assecat.id)
                    assetdetls_data = AssetDetails.objects.filter(barcode=assecat.barcode)[0]


                    assetvalue_resp = CategoryChangeResponse()

                    assetvalue_resp.set_capdate(assetdetls_data.capdate)
                    assetvalue_resp.set_assetdetails_id(assecat.id)
                    assetvalue_resp.set_assetdtls_id(assecat.assetdetails_id)
                    assetvalue_resp.set_status(assetvaluedtl_status(assecat.status))
                    assetvalue_resp.set_assetdetails_value(assecat.assetheader.valuetot)
                    assetvalue_resp.set_barcode(assecat.barcode)
                    #product
                    fa_service_call=FaApiService(scope)
                    product_data=fa_service_call.fetch_product(assecat.product_id,emp_id,request=None)
                    assetvalue_resp.set_product_name(product_data.name)
                    #print('product_data ',product_data.name)
                    # asset Location
                    location_serv = AssetLocationService(scope)
                    assetvalue_resp.set_location(location_serv.fetch_assetlocation(assecat.assetlocation_id))
                    # employee_branch
                    emp_branch = FaApiService(scope)
                    assetvalue_resp.branch = (emp_branch.fetch_branch(assecat.branch_id))
                    #assetcat
                    assetcat=assecat.assetcat # assetcat FK details get
                    assetvalue_resp.set_assetcat_id(assetcat.id)
                    assetvalue_resp.set_assetcat_subcatname(assetcat.subcatname)
                    assetid_list.append(assetvalue_resp)
                vpage = NWisefinPaginator(assetdtl_data, vys_page.get_index(), 10)
                assetid_list.set_pagination(vpage)

        except Exception  as excep:
            logger.info('FAL_ASSETCATCHANGE_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

        return assetid_list


    def get_categorychange_list(self, vys_page,filter_json,emp_id,request):
        try:
            assetid_list = NWisefinList()
            scope=request.scope
            module_permission = ModulePermission(scope)
            role_arr = module_permission.employee_modulerole(emp_id, ModuleList.FA)
            print(role_arr,' role_arr')
            maker = RoleList.maker
            checker = RoleList.checker

            if maker in role_arr :
                condition = Q(status__in=[AssetRequestStatus.PENDING,AssetRequestStatus.APPROVED,
                              AssetRequestStatus.REJECTED])&Q(assetdetails__requestfor__in=[AssetRequestfor.ASSETCAT,
                                                              AssetRequestfor.NEW])\
                             &Q(assetdetails__status=AssetStatus.ACTIVE)
            else:
                return assetid_list


            if 'assetdetails_value' in filter_json:
                condition&= Q(assetdetails__assetdetails_value=filter_json['assetdetails_value'])
            if 'branch_id' in filter_json:
                condition&= Q(assetdetails__branch_id=filter_json['branch_id'])
            if 'assetcat_id' in filter_json:
                condition&= Q(category=filter_json['assetcat_id'])
            if 'barcode' in filter_json:
                condition&= Q(assetdetails__barcode__icontains=filter_json['barcode'])
            if 'capdate' in filter_json:
                condition&= Q(assetdetails__capdate=filter_json['capdate'])

            assetdtl_data = AssetCatChange.objects.filter(condition).order_by('-id')[
                              vys_page.get_offset():vys_page.get_query_limit()]

            print('condition',condition,len(assetdtl_data))

            if len(assetdtl_data) > 0 :
                for assetfr in assetdtl_data:
                    print(assetfr.id,' assetfr')
                    assetvalue_resp = CategoryChangeResponse()
                    assetcat_serv=AssetCatService(scope)
                    #AssetCatChange

                    catchage= assetfr
                    assetfr = assetfr.assetdetails
                    assetvalue_resp.category_status =(assetrequst_status(catchage.status))

                    old_assetcat=assetcat_serv.fetch_assetcat(catchage.oldcat,request)
                    new_assetcat=assetcat_serv.fetch_assetcat(catchage.category,request)
                    print('old_assetcat',old_assetcat)
                    print('new_assetcat',new_assetcat)
                    assetvalue_resp.set_old_categtory(old_assetcat.subcatname)
                    assetvalue_resp.set_new_categtory(new_assetcat.subcatname)

                    #asstdetails
                    assetvalue_resp.set_reason(catchage.reason)
                    assetvalue_resp.set_capdate(assetfr.capdate)
                    assetvalue_resp.set_assetdetails_id(assetfr.id)
                    assetvalue_resp.set_assetdtls_id(assetfr.assetdetails_id)
                    assetvalue_resp.set_assetdetails_status(assetvaluedtl_status(assetfr.assetdetails_status))
                    assetvalue_resp.set_assetdetails_value(assetfr.assetheader.valuetot)
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
                    # assetcat=assetfr.assetcat # assetcat FK details get
                    # assetvalue_resp.set_assetcat_id(assetcat.id)
                    # assetvalue_resp.set_assetcat_subcatname(assetcat.subcatname)

                    assetid_list.append(assetvalue_resp)
                vpage = NWisefinPaginator(assetdtl_data, vys_page.get_index(), 10)
                assetid_list.set_pagination(vpage)

        except Exception  as excep:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

        return assetid_list


    def fetch_catchangechecker_list(self, vys_page,filter_json,emp_id,request):
        try:
            assetid_list = NWisefinList()
            scope=request.scope
            module_permission = ModulePermission(scope)
            role_arr = module_permission.employee_modulerole(emp_id, ModuleList.FA)
            print(role_arr,' role_arr')
            maker = RoleList.maker
            checker = RoleList.checker

            if checker in role_arr :
                condition = Q(status=AssetRequestStatus.PENDING) & Q(assetdetails__requestfor=AssetRequestfor.ASSETCAT) \
                            & Q(assetdetails__status=AssetStatus.ACTIVE)
            else:
                return assetid_list

            if 'assetdetails_value' in filter_json:
                condition &= Q(assetdetails__assetdetails_value=filter_json['assetdetails_value'])
            if 'branch_id' in filter_json:
                condition &= Q(assetdetails__branch_id=filter_json['branch_id'])
            if 'assetcat_id' in filter_json:
                condition &= Q(category=filter_json['assetcat_id'])
            if 'barcode' in filter_json:
                condition &= Q(assetdetails__barcode__icontains=filter_json['barcode'])
            if 'capdate' in filter_json:
                condition &= Q(assetdetails__capdate=filter_json['capdate'])

            assetdtl_data = AssetCatChange.objects.filter(condition).order_by('-id')[
                            vys_page.get_offset():vys_page.get_query_limit()]

            print('condition',condition)

            if len(assetdtl_data) > 0 :
                for assetfr in assetdtl_data:
                    assetvalue_resp = CategoryChangeResponse()
                    assetcat_serv=AssetCatService(scope)
                    #AssetCatChange
                    catchage = assetfr
                    assetfr = assetfr.assetdetails
                    assetvalue_resp.category_status =(assetrequst_status(catchage.status))

                    old_assetcat=assetcat_serv.fetch_assetcat(catchage.oldcat,request)
                    new_assetcat=assetcat_serv.fetch_assetcat(catchage.category,request)
                    print('old_assetcat',old_assetcat)
                    print('new_assetcat',new_assetcat)
                    assetvalue_resp.set_old_categtory(old_assetcat.subcatname)
                    assetvalue_resp.set_new_categtory(new_assetcat.subcatname)
                    #asstdetails
                    assetvalue_resp.set_capdate(assetfr.capdate)
                    assetvalue_resp.set_assetdetails_id(assetfr.id)
                    assetvalue_resp.set_assetdtls_id(assetfr.assetdetails_id)
                    assetvalue_resp.set_assetdetails_status(assetvaluedtl_status(assetfr.assetdetails_status))
                    assetvalue_resp.set_assetdetails_value(assetfr.assetheader.valuetot)
                    assetvalue_resp.set_barcode(assetfr.barcode)
                    assetvalue_resp.set_reason(catchage.reason)
                    #product
                    fa_service_call=FaApiService(scope)
                    product_data=fa_service_call.fetch_product(assetfr.product_id,emp_id,request=None)
                    assetvalue_resp.set_product_name(product_data.name)
                    #print('product_data ',product_data.name)
                    # asset Location
                    location_serv = AssetLocationService(scope)
                    assetvalue_resp.set_location(
                        location_serv.fetch_assetlocation(assetfr.assetlocation_id))
                    # employee_branch
                    emp_branch = FaApiService(scope)
                    assetvalue_resp.branch = (emp_branch.fetch_branch(assetfr.branch_id))
                    #assetcat
                    # assetcat=assetfr.assetcat # assetcat FK details get
                    # assetvalue_resp.set_assetcat_id(assetcat.id)
                    # assetvalue_resp.set_assetcat_subcatname(assetcat.subcatname)

                    if int(catchage.created_by) == int(emp_id):
                        approval_flage=False
                    else:
                        approval_flage=True
                    assetvalue_resp.set_approval_flage(approval_flage)

                    assetid_list.append(assetvalue_resp)
                vpage = NWisefinPaginator(assetdtl_data, vys_page.get_index(), 10)
                assetid_list.set_pagination(vpage)

        except Exception  as excep:
            logger.info('FAL_ASSETCATCHANGE_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

        return assetid_list

    def catchange_approver_validation(self,assetcat_json,approver_emp_id):
        for catchange in assetcat_json['assetdetails']:
            condition=Q(assetdetails__assetdetails_id=catchange['assetdetails_id'],
                                                             status=AssetRequestStatus.PENDING)
            assetvalue_data = AssetCatChange.objects.filter(condition)[0]
            created_by=int(assetvalue_data.created_by)
            print('created_by  ',int(approver_emp_id) , created_by)
            if int(approver_emp_id) == created_by:
                return True

        return False

    #@transaction.atomic(using='fa_service')
    def catchangechecker_approve(self,assetcat_json,emp_id):
        try:
            with transaction.atomic(using=self._current_app_schema()):
                reason=None
                if 'reason' in assetcat_json:
                    reason=assetcat_json['reason']

                for catchange in assetcat_json['assetdetails']:
                    catchange_data = AssetCatChange.objects.filter(assetdetails__assetdetails_id=catchange['assetdetails_id'],
                                                             status=AssetRequestStatus.PENDING)
                    catagory_change_update=catchange_data
                    if int(catchange['status']) == int(AssetRequestStatus.APPROVED):
                        assetdetails_data = AssetDetails.objects.filter(assetdetails_id=catchange['assetdetails_id'])[0]
                        cat_data = AssetCat.objects.filter(id=catchange_data[0].category)[0]
                        if cat_data.deptype=='WDV':
                            sal_val = FaConst()
                            asst_dep_rate = round(1 - ((sal_val.SALVAGE_VALUE / assetdetails_data.assetdetails_value) ** (
                                        1 / (cat_data.lifetime / 12))), 2)
                            asst_dep_rate = asst_dep_rate * 100
                        else:
                            asst_dep_rate=cat_data.deprate
                        life_time=int(cat_data.lifetime)
                        apsubcategoryid=cat_data.subcategory_id
                        cap_date=assetdetails_data.capdate
                        from dateutil.relativedelta import relativedelta
                        End_date = cap_date + relativedelta(months=life_time)-relativedelta(days=1)
                        #End_date = cap_date + timedelta(days=life_time)
                        print('Enddate ',End_date," , ",cat_data.deprate)

                        assetdtl_data = AssetDetails.objects.filter(assetdetails_id=catchange['assetdetails_id']).update(
                            enddate=End_date,
                            assetcat_id=catchange_data[0].category,
                            subcat=apsubcategoryid,
                            deprate=asst_dep_rate,
                            requestfor=AssetRequestfor.NEW,
                            status=catchange['status'],
                            updated_by=emp_id,
                            updated_date=now())
                    else:
                        assetdtl_data = AssetDetails.objects.filter(assetdetails_id=catchange['assetdetails_id']).update(
                            requestfor=AssetRequestfor.NEW,
                            updated_by=emp_id,
                            updated_date=now())

                    catagory_change_update.update(status=catchange['status'],
                                     catchange_status=catchange['status'],
                                     reason=reason,
                                     updated_by=emp_id,
                                     updated_date=now() )

                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)

        except Exception  as excep:
            logger.info('FAL_ASSETCATCHANGE_EXCEPT:{}'.format(traceback.print_exc()))
            traceback.print_exc()
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

        return success_obj


