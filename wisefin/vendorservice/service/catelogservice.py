import pandas as pd

from userservice.models import Employee
from vendorservice.data.response.catelogresponse import CatelogResponse
from vendorservice.data.response.vendorauditresponse import VendorAuditResponse
from vendorservice.models import Catelog, VendorModificationRel, ActivityDetail, SupplierActivity, SupplierBranch
from vendorservice.service.vendorauditservice import VendorAuditService
from vendorservice.service.vendorservice import VendorService
from django.db import IntegrityError
from vendorservice.util.vendorutil import VendorRefType, ModifyStatus, RequestStatusUtil
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.utilityservice import NWisefinUtilityService
from django.db.models import Q
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace


class CatelogService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def create_catelog(self, activitydetail_id,catelog_obj, user_id,vendor_id):

            req_status = RequestStatusUtil.ONBOARD
            if not catelog_obj.get_id() is None:
                # try:
                    catelog_update = Catelog.objects.using(self._current_app_schema()).filter(id=catelog_obj.get_id(), entity_id=self._entity_id()).update(
                        activitydetail_id=activitydetail_id, detailname=catelog_obj.get_detail_name(),
                        productname=catelog_obj.get_product_name(), category=catelog_obj.get_category(),
                        subcategory=catelog_obj.get_subcategory(), name=catelog_obj.get_name(),
                        specification=catelog_obj.get_specification(), size=catelog_obj.get_size(),
                        remarks=catelog_obj.get_remarks(),
                        uom=catelog_obj.get_uom(), unitprice=catelog_obj.get_unitprice(), fromdate=catelog_obj.get_from_date(),
                        todate=catelog_obj.get_to_date(), packing_price=catelog_obj.get_packing_price(),
                        deliverydate=catelog_obj.get_delivery_date(), capacity=catelog_obj.get_capacity(),
                        direct_to=catelog_obj.get_direct_to(),updated_by=user_id, portal_flag=catelog_obj.get_portal_flag())

                    catelog_auditdata={'id':catelog_obj.get_id(),
                        'activitydetail_id':activitydetail_id, 'detailname':catelog_obj.get_detail_name(),
                        'productname':catelog_obj.get_product_name(), 'category':catelog_obj.get_category(),
                        'subcategory':catelog_obj.get_subcategory(), 'name':catelog_obj.get_name(),
                        'specification':catelog_obj.get_specification(), 'size':catelog_obj.get_size(),
                        'remarks':catelog_obj.get_remarks(),
                        'uom':catelog_obj.get_uom(), 'unitprice':catelog_obj.get_unitprice(), 'fromdate':catelog_obj.get_from_date(),
                        'todate':catelog_obj.get_to_date(), 'packing_price':catelog_obj.get_packing_price(),
                        'deliverydate':catelog_obj.get_delivery_date(), 'capacity':catelog_obj.get_capacity(),
                        'direct_to':catelog_obj.get_direct_to(),'updated_by':user_id}

                    catelog = Catelog.objects.using(self._current_app_schema()).get(id=catelog_obj.get_id(), entity_id=self._entity_id())

                    self.audit_function(catelog_auditdata, vendor_id, user_id, req_status, catelog.id, ModifyStatus.update)


                # except IntegrityError as error:
                #     error_obj = Error()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj
                # except Catelog.DoesNotExist:
                #     error_obj = Error()
                #     error_obj.set_code(ErrorMessage.INVALID_VENDORCARELOG_ID)
                #     error_obj.set_description(ErrorDescription.INVALID_VENDORCARELOG_ID)
                #     return error_obj
                # except:
                #     error_obj = Error()
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                #     return error_obj
            else:
                # try:
                    catelog = Catelog.objects.using(self._current_app_schema()).create(
                        activitydetail_id=activitydetail_id, detailname=catelog_obj.get_detail_name(),
                        productname=catelog_obj.get_product_name(), category=catelog_obj.get_category(),
                        subcategory=catelog_obj.get_subcategory(), name=catelog_obj.get_name(),
                        specification=catelog_obj.get_specification(), size=catelog_obj.get_size(),
                        remarks=catelog_obj.get_remarks(),
                        uom=catelog_obj.get_uom(), unitprice=catelog_obj.get_unitprice(), fromdate=catelog_obj.get_from_date(),
                        todate=catelog_obj.get_to_date(), packing_price=catelog_obj.get_packing_price(),
                        deliverydate=catelog_obj.get_delivery_date(), capacity=catelog_obj.get_capacity(),
                        direct_to=catelog_obj.get_direct_to(),created_by=user_id, entity_id=self._entity_id(),portal_flag=catelog_obj.get_portal_flag())

                    vendor_service=VendorService(self._scope())
                    activitydtl_obj = ActivityDetail.objects.using(self._current_app_schema()).get(id=activitydetail_id)
                    activity_id = activitydtl_obj.activity.id
                    activity_obj = SupplierActivity.objects.using(self._current_app_schema()).get(id=activity_id)
                    branch_id = activity_obj.branch.id
                    vendor_check2 = vendor_service.activitydtlcatalog_validate(activitydetail_id)
                    if vendor_check2 == True:
                        vendor_branchupdate = ActivityDetail.objects.using(self._current_app_schema()).filter(id=activitydetail_id, entity_id=self._entity_id()).update(
                            is_validate=True)
                    else:
                        vendor_branchupdate = ActivityDetail.objects.using(self._current_app_schema()).filter(id=activitydetail_id, entity_id=self._entity_id()).update(
                            is_validate=False)

                    vendor_check1 = vendor_service.activtydtl_validate(activity_id)
                    if vendor_check1 == True:
                        vendor_branchupdate = SupplierActivity.objects.using(self._current_app_schema()).filter(id=activity_id, entity_id=self._entity_id()).update(is_validate=True)
                    else:
                        vendor_branchupdate = SupplierActivity.objects.using(self._current_app_schema()).filter(id=activity_id, entity_id=self._entity_id()).update(is_validate=False)
                    vendor_check = vendor_service.branchvalidate(branch_id)
                    if vendor_check == True:
                        vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).update(is_validate=True)
                    else:
                        vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).update(is_validate=False)

                    self.audit_function(catelog, vendor_id, user_id, req_status, catelog.id, ModifyStatus.create)
                # except IntegrityError as error:
                #     error_obj = Error()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj
                # except:
                #     error_obj = Error()
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                #     return error_obj

            catelog_data = CatelogResponse()
            catelog_data.set_id(catelog.id)
            catelog_data.set_activitydetail_id(catelog.activitydetail_id)
            catelog_data.set_detailname(catelog.detailname)
            catelog_data.set_productname(catelog.productname)
            catelog_data.set_category(catelog.category)
            catelog_data.set_subcategory(catelog.subcategory)
            catelog_data.set_name(catelog.name)
            catelog_data.set_specification(catelog.specification)
            catelog_data.set_size(catelog.size)
            catelog_data.set_remarks(catelog.remarks)
            catelog_data.set_uom(catelog.uom)
            catelog_data.set_unitprice(catelog.unitprice)
            catelog_data.set_fromdate(catelog.fromdate)
            catelog_data.set_todate(catelog.todate)
            catelog_data.set_packing_price(catelog.packing_price)
            catelog_data.set_delivery_date(catelog.deliverydate)
            catelog_data.set_capacity(catelog.capacity)
            catelog_data.set_direct_to(catelog.direct_to)
            catelog_data.set_portal_flag(catelog.portal_flag)

            return catelog_data

    # def fetch_catelog_list(self,catelog_id, user_id):
    #         catelogList = Catelog.objects.all()
    #         list_length = len(catelogList)
    #         logger.info(list_length)
    #         catelog_list_data = VysfinList()
    #         if list_length <= 0:
    #             pass
    #         else:
    #             for catelog in catelogList:
    #                 catelog_data = CatelogResponse()
    #                 catelog_data.set_id(catelog.id)
    #                 catelog_data.set_activitydetail_id(catelog.activitydetail_id)
    #                 catelog_data.set_detailname(catelog.detailname)
    #                 catelog_data.set_productname(catelog.productname)
    #                 catelog_data.set_category(catelog.category)
    #                 catelog_data.set_subcategory(catelog.subcategory)
    #                 catelog_data.set_name(catelog.name)
    #                 catelog_data.set_specification(catelog.specification)
    #                 catelog_data.set_size(catelog.size)
    #                 catelog_data.set_remarks(catelog.remarks)
    #                 catelog_data.set_uom(catelog.uom)
    #                 catelog_data.set_unitprice(catelog.unitprice)
    #                 catelog_data.set_fromdate(catelog.fromdate)
    #                 catelog_data.set_todate(catelog.todate)
    #                 catelog_data.set_packing_price(catelog.packing_price)
    #                 catelog_data.set_delivery_date(catelog.deliverydate)
    #                 catelog_data.set_capacity(catelog.capacity)
    #                 catelog_data.set_direct_to(catelog.direct_to)
    #                 catelog_list_data.append(catelog_data)
    #         return catelog_list_data

    def fetch_catelog_list(self,request, vys_page,user_id,activitydetail_id):
        queue_arr = Catelog.objects.using(self._current_app_schema()).filter(activitydetail_id=activitydetail_id, entity_id=self._entity_id()).values('id')
        condition = None
        for vendor in queue_arr:
            logger.info(str(vendor))
            if condition is None:
                condition = (Q(id__exact=vendor['id'])& (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1)) &Q(entity_id=self._entity_id())
            else:
                condition |= (Q(id__exact=vendor['id'])& (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1)) &Q(entity_id=self._entity_id())
        if condition is not None:
            catelogList = Catelog.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                              vys_page.get_offset():vys_page.get_query_limit()]
        else:
            catelogList = []

        vlist = NWisefinList()
        user_list = []
        for vendor in catelogList:
            user_list.append(vendor.created_by)
        user_list = set(user_list)
        user_list = list(user_list)
        utility_service = NWisefinUtilityService()
        user_list_obj = utility_service.get_user_info(request, user_list)

        for catelog in catelogList:
            catelog_data = CatelogResponse()
            catelog_data.set_id(catelog.id)
            catelog_data.set_activitydetail_id(catelog.activitydetail_id)
            catelog_data.set_detailname(catelog.detailname)
            catelog_data.set_productname(catelog.productname)
            catelog_data.set_category(catelog.category)
            catelog_data.set_subcategory(catelog.subcategory)
            catelog_data.set_name(catelog.name)
            catelog_data.set_specification(catelog.specification)
            catelog_data.set_size(catelog.size)
            catelog_data.set_remarks(catelog.remarks)
            catelog_data.set_uom(catelog.uom)
            catelog_data.set_unitprice(catelog.unitprice)
            catelog_data.set_fromdate(catelog.fromdate)
            catelog_data.set_todate(catelog.todate)
            catelog_data.set_packing_price(catelog.packing_price)
            catelog_data.set_delivery_date(catelog.deliverydate)
            catelog_data.set_capacity(catelog.capacity)
            catelog_data.set_direct_to(catelog.direct_to)
            catelog_data.set_created_by(catelog.created_by)
            catelog_data.set_modify_ref_id(catelog.modify_ref_id)
            catelog_data.set_modify_status(catelog.modify_status)
            catelog_data.set_portal_flag(catelog.portal_flag)

            for ul in user_list_obj['data']:
                if ul['id'] == Catelog.created_by:
                    catelog_data.set_created_by(ul)
            vlist.append(catelog_data)
        vpage = NWisefinPaginator(catelogList, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist


    def fetch_catelog(self,  catelog_id):
        catelog = Catelog.objects.using(self._current_app_schema()).get(id=catelog_id, entity_id=self._entity_id())
        catelog_data = CatelogResponse()
        catelog_data.set_id(catelog.id)
        catelog_data.set_activitydetail_id(catelog.activitydetail_id)
        catelog_data.set_detailname(catelog.detailname)
        catelog_data.set_productname(catelog.productname)
        catelog_data.set_category(catelog.category)
        catelog_data.set_subcategory(catelog.subcategory)
        catelog_data.set_name(catelog.name)
        catelog_data.set_specification(catelog.specification)
        catelog_data.set_size(catelog.size)
        catelog_data.set_remarks(catelog.remarks)
        catelog_data.set_uom(catelog.uom)
        catelog_data.set_unitprice(catelog.unitprice)
        catelog_data.set_fromdate(catelog.fromdate)
        catelog_data.set_todate(catelog.todate)
        catelog_data.set_packing_price(catelog.packing_price)
        catelog_data.set_delivery_date(catelog.deliverydate)
        catelog_data.set_capacity(catelog.capacity)
        catelog_data.set_direct_to(catelog.direct_to)
        catelog_data.set_created_by(catelog.created_by)
        catelog_data.set_modify_ref_id(catelog.modify_ref_id)
        catelog_data.set_modify_status(catelog.modify_status)
        catelog_data.set_portal_flag(catelog.portal_flag)
        return catelog_data



    def delete_catelog(self, branch_id, catelog_id, user_id, vendor_id,activitydetail_id):

            catelog = Catelog.objects.using(self._current_app_schema()).filter(id=catelog_id, entity_id=self._entity_id()).delete()

            vendor_service = VendorService(self._scope())
            activitydtl_obj = ActivityDetail.objects.using(self._current_app_schema()).get(id=activitydetail_id, entity_id=self._entity_id())
            activity_id = activitydtl_obj.activity.id
            activity_obj = SupplierActivity.objects.using(self._current_app_schema()).get(id=activity_id, entity_id=self._entity_id())
            branch_id = activity_obj.branch.id
            vendor_check2 = vendor_service.activitydtlcatalog_validate(activitydetail_id)
            if vendor_check2 == True:
                vendor_branchupdate = ActivityDetail.objects.using(self._current_app_schema()).filter(id=activitydetail_id, entity_id=self._entity_id()).update(
                    is_validate=True)
            else:
                vendor_branchupdate = ActivityDetail.objects.using(self._current_app_schema()).filter(id=activitydetail_id, entity_id=self._entity_id()).update(
                    is_validate=False)

            vendor_check1 = vendor_service.activtydtl_validate(activity_id)
            if vendor_check1 == True:
                vendor_branchupdate = SupplierActivity.objects.using(self._current_app_schema()).filter(id=activity_id, entity_id=self._entity_id()).update(is_validate=True)
            else:
                vendor_branchupdate = SupplierActivity.objects.using(self._current_app_schema()).filter(id=activity_id, entity_id=self._entity_id()).update(is_validate=False)
            vendor_check = vendor_service.branchvalidate(branch_id)
            if vendor_check == True:
                vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).update(is_validate=True)
            else:
                vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).update(is_validate=False)

            if catelog[0] == 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_VENDORCARELOG_ID)
                error_obj.set_description(ErrorDescription.INVALID_VENDORCARELOG_ID)
                return error_obj
            else:
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.DELETE_MESSAGE)

                req_status = RequestStatusUtil.MODIFICATION
                self.audit_function(catelog, vendor_id, user_id, req_status, catelog_id, ModifyStatus.delete)
                return success_obj


    def catelog_modification(self, activitydetail_id,catelog_obj, user_id,vendor_id):

        req_status = RequestStatusUtil.MODIFICATION
        vendor_service = VendorService(self._scope())
        if catelog_obj.get_id():
            # try:
                ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_CATELOG, catelog_obj.get_id())
                if ref_flag==True:
                    catelog = Catelog.objects.using(self._current_app_schema()).filter(id=catelog_obj.get_id(), entity_id=self._entity_id()).update(activitydetail_id=activitydetail_id,
                                                     detailname=catelog_obj.get_detail_name(),
                                                     productname=catelog_obj.get_product_name(),
                                                     category=catelog_obj.get_category(),
                                                     subcategory=catelog_obj.get_subcategory(),
                                                     name=catelog_obj.get_name(),
                                                     specification=catelog_obj.get_specification(),
                                                     size=catelog_obj.get_size(),
                                                     remarks=catelog_obj.get_remarks(),
                                                     uom=catelog_obj.get_uom(), unitprice=catelog_obj.get_unitprice(),
                                                     fromdate=catelog_obj.get_from_date(),
                                                     todate=catelog_obj.get_to_date(),
                                                     packing_price=catelog_obj.get_packing_price(),
                                                     deliverydate=catelog_obj.get_delivery_date(),
                                                     capacity=catelog_obj.get_capacity(),
                                                     direct_to=catelog_obj.get_direct_to(),
                                                     portal_flag=catelog_obj.get_portal_flag()
                                                    )
                    catelog=Catelog.objects.using(self._current_app_schema()).get(id=catelog_obj.get_id(), entity_id=self._entity_id())
                else:
                    catelog = Catelog.objects.using(self._current_app_schema()).create(activitydetail_id=activitydetail_id, detailname=catelog_obj.get_detail_name(),
                            productname=catelog_obj.get_product_name(), category=catelog_obj.get_category(),
                            subcategory=catelog_obj.get_subcategory(), name=catelog_obj.get_name(),
                            specification=catelog_obj.get_specification(), size=catelog_obj.get_size(),
                            remarks=catelog_obj.get_remarks(),
                            uom=catelog_obj.get_uom(), unitprice=catelog_obj.get_unitprice(), fromdate=catelog_obj.get_from_date(),
                            todate=catelog_obj.get_to_date(), packing_price=catelog_obj.get_packing_price(),
                            deliverydate=catelog_obj.get_delivery_date(), capacity=catelog_obj.get_capacity(),
                            direct_to=catelog_obj.get_direct_to(),created_by=user_id,
                             modify_status=ModifyStatus.update,modify_ref_id=catelog_obj.get_id(),
                             modified_by=user_id, entity_id=self._entity_id(),portal_flag=catelog_obj.get_portal_flag())
                    catelog_update=Catelog.objects.using(self._current_app_schema()).filter(id=catelog_obj.get_id()).update(
                        modify_ref_id=catelog.id)

                    catelogupdate_auditdata={'id':catelog_obj.get_id(),'modify_ref_id':catelog.id}

                    VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=catelog_obj.get_id(),
                                                         ref_type=VendorRefType.VENDOR_CATELOG,
                                                         mod_status=ModifyStatus.update,
                                                         modify_ref_id=catelog.id, entity_id=self._entity_id())


                # self.audit_function(catelog, vendor_id, user_id, req_status, catelog.id, ModifyStatus.create)
                # self.audit_function(catelogupdate_auditdata, vendor_id, user_id, req_status, catelog.id, ModifyStatus.update)

            # except IntegrityError as error:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj
        else:
            # try:
                catelog = Catelog.objects.using(self._current_app_schema()).create(activitydetail_id=activitydetail_id, detailname=catelog_obj.get_detail_name(),
                        productname=catelog_obj.get_product_name(), category=catelog_obj.get_category(),
                        subcategory=catelog_obj.get_subcategory(), name=catelog_obj.get_name(),
                        specification=catelog_obj.get_specification(), size=catelog_obj.get_size(),
                        remarks=catelog_obj.get_remarks(),
                        uom=catelog_obj.get_uom(), unitprice=catelog_obj.get_unitprice(), fromdate=catelog_obj.get_from_date(),
                        todate=catelog_obj.get_to_date(), packing_price=catelog_obj.get_packing_price(),
                        deliverydate=catelog_obj.get_delivery_date(), capacity=catelog_obj.get_capacity(),
                        direct_to=catelog_obj.get_direct_to(),created_by=user_id, modify_status=ModifyStatus.create,
                                                                modified_by=user_id, entity_id=self._entity_id(),portal_flag=catelog_obj.get_portal_flag())
                catelog_update=Catelog.objects.using(self._current_app_schema()).filter(id=catelog.id, entity_id=self._entity_id()).update(modify_ref_id=catelog.id)

                VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=catelog.id,
                                                     ref_type=VendorRefType.VENDOR_CATELOG, mod_status=ModifyStatus.create,
                                                     modify_ref_id=catelog.id, entity_id=self._entity_id())

                activitydtl_obj=ActivityDetail.objects.using(self._current_app_schema()).get(id=activitydetail_id, entity_id=self._entity_id())
                activity_id=activitydtl_obj.activity.id
                activity_obj=SupplierActivity.objects.using(self._current_app_schema()).get(id=activity_id, entity_id=self._entity_id())
                branch_id=activity_obj.branch.id
                vendor_check2 = vendor_service.activitydtlcatalog_validate(activitydetail_id)
                if vendor_check2 == True:
                    vendor_branchupdate = ActivityDetail.objects.using(self._current_app_schema()).filter(id=activitydetail_id, entity_id=self._entity_id()).update(is_validate=True)
                else:
                    vendor_branchupdate = ActivityDetail.objects.using(self._current_app_schema()).filter(id=activitydetail_id, entity_id=self._entity_id()).update(is_validate=False)

                vendor_check1 = vendor_service.activtydtl_validate(activity_id)
                if vendor_check1 == True:
                    vendor_branchupdate = SupplierActivity.objects.using(self._current_app_schema()).filter(id=activity_id, entity_id=self._entity_id()).update(is_validate=True)
                else:
                    vendor_branchupdate = SupplierActivity.objects.using(self._current_app_schema()).filter(id=activity_id, entity_id=self._entity_id()).update(is_validate=False)
                vendor_check = vendor_service.branchvalidate(branch_id)
                if vendor_check == True:
                    vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).update(is_validate=True)
                else:
                    vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).update(is_validate=False)

                # self.audit_function(catelog, vendor_id, user_id, req_status, catelog.id, ModifyStatus.create)
                # self.audit_function(catelog_update, vendor_id, user_id, req_status, catelog_update.id, ModifyStatus.update)


            # except IntegrityError as error:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj

        catelog_data = CatelogResponse()
        catelog_data.set_id(catelog.id)
        catelog_data.set_activitydetail_id(catelog.activitydetail_id)
        catelog_data.set_detailname(catelog.detailname)
        catelog_data.set_productname(catelog.productname)
        catelog_data.set_category(catelog.category)
        catelog_data.set_subcategory(catelog.subcategory)
        catelog_data.set_name(catelog.name)
        catelog_data.set_specification(catelog.specification)
        catelog_data.set_size(catelog.size)
        catelog_data.set_remarks(catelog.remarks)
        catelog_data.set_uom(catelog.uom)
        catelog_data.set_unitprice(catelog.unitprice)
        catelog_data.set_fromdate(catelog.fromdate)
        catelog_data.set_todate(catelog.todate)
        catelog_data.set_packing_price(catelog.packing_price)
        catelog_data.set_delivery_date(catelog.deliverydate)
        catelog_data.set_capacity(catelog.capacity)
        catelog_data.set_direct_to(catelog.direct_to)
        catelog_data.set_modify_ref_id(catelog.modify_ref_id)
        catelog_data.set_modify_status(catelog.modify_status)
        catelog_data.set_portal_flag(catelog.portal_flag)

        return catelog_data

    def modification_delete_catelog(self, catelog_id,vendor_id, user_id,activitydetail_id):
        try:
            vendor_service = VendorService(self._scope())
            catelog_update=Catelog.objects.using(self._current_app_schema()).filter(id=catelog_id, entity_id=self._entity_id()).update(modify_ref_id=catelog_id,modify_status=ModifyStatus.delete)
            ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_CATELOG, catelog_id)
            if ref_flag == True:
                flag_obj = VendorModificationRel.objects.using(self._current_app_schema()).filter(
                    Q(modify_ref_id=catelog_id) & Q(ref_type=VendorRefType.VENDOR_CATELOG) &Q(entity_id=self._entity_id())).update(
                    mod_status=ModifyStatus.delete)
            else:
                VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=catelog_id,
                                                     ref_type=VendorRefType.VENDOR_CATELOG,
                                                     mod_status=ModifyStatus.delete,
                                                     modify_ref_id=catelog_id, entity_id=self._entity_id())

            vendor_service = VendorService(self._scope())
            activitydtl_obj = ActivityDetail.objects.using(self._current_app_schema()).get(id=activitydetail_id, entity_id=self._entity_id())
            activity_id = activitydtl_obj.activity.id
            activity_obj = SupplierActivity.objects.using(self._current_app_schema()).get(id=activity_id, entity_id=self._entity_id())
            branch_id = activity_obj.branch.id
            vendor_check2 = vendor_service.activitydtlcatalog_validate(activitydetail_id)
            if vendor_check2 == True:
                vendor_branchupdate = ActivityDetail.objects.using(self._current_app_schema()).filter(id=activitydetail_id, entity_id=self._entity_id()).update(
                    is_validate=True)
            else:
                vendor_branchupdate = ActivityDetail.objects.using(self._current_app_schema()).filter(id=activitydetail_id, entity_id=self._entity_id()).update(
                    is_validate=False)

            vendor_check1 = vendor_service.activtydtl_validate(activity_id)
            if vendor_check1 == True:
                vendor_branchupdate = SupplierActivity.objects.using(self._current_app_schema()).filter(id=activity_id, entity_id=self._entity_id()).update(is_validate=True)
            else:
                vendor_branchupdate = SupplierActivity.objects.using(self._current_app_schema()).filter(id=activity_id, entity_id=self._entity_id()).update(is_validate=False)
            vendor_check = vendor_service.branchvalidate(branch_id)
            if vendor_check == True:
                vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).update(is_validate=True)
            else:
                vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).update(is_validate=False)

            req_status = RequestStatusUtil.MODIFICATION
            # self.audit_function(catelog_update, vendor_id, user_id, req_status, catelog_update.id, ModifyStatus.update)

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj

    def get_vendorid_catalog(self, activitydtl_id):
        activity = ActivityDetail.objects.using(self._current_app_schema()).get(id=activitydtl_id, entity_id=self._entity_id())
        activity_id = activity.activity_id

        activity = SupplierActivity.objects.using(self._current_app_schema()).get(id=activity_id, entity_id=self._entity_id())
        branch_id = activity.branch_id

        branch = SupplierBranch.objects.using(self._current_app_schema()).get(id=branch_id, entity_id=self._entity_id())
        vobj = branch.vendor_id
        return vobj

    def modification_reject_catelog(self, mod_status, old_id, new_id, vendor_id, user_id):

        req_status = RequestStatusUtil.MODIFICATION
        if mod_status == ModifyStatus.update:
            catelog = Catelog.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()
            catelog_update=Catelog.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(modify_ref_id=-1,modified_by=-1)


            self.audit_function(catelog, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)
            self.audit_function(catelog_update, vendor_id, user_id, req_status, old_id, ModifyStatus.update)
        elif mod_status == ModifyStatus.create:
            catelog = Catelog.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()
            self.audit_function(catelog, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)
        else:
            catelog_update=Catelog.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(modify_ref_id=-1,modified_by=-1)
            self.audit_function(catelog_update, vendor_id, user_id, req_status, old_id, ModifyStatus.update)

    def modification_action_catelog(self, mod_status, old_id, new_id, vendor_id, user_id):

        req_status = RequestStatusUtil.MODIFICATION
        if mod_status == ModifyStatus.update:
            catelog_obj = self.fetch_catelog(new_id)
            if catelog_obj.get_fromdate()==str(None):
                from_date=None
            else:
                from_date= catelog_obj.get_fromdate()

            if catelog_obj.get_todate() == str(None):
                to_date = None
            else:
                to_date = catelog_obj.get_todate()
            catelog_update = Catelog.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(
                activitydetail_id=catelog_obj.get_activitydetail_id(),detailname=catelog_obj.get_detailname(),
                productname=catelog_obj.get_productname(), category=catelog_obj.get_category(),
                subcategory=catelog_obj.get_subcategory(), name=catelog_obj.get_name(),
                specification=catelog_obj.get_specification(), size=catelog_obj.get_size(),
                remarks=catelog_obj.get_remarks(),
                uom=catelog_obj.get_uom(), unitprice=catelog_obj.get_unitprice(), fromdate=from_date,
                todate=to_date, packing_price=catelog_obj.get_packing_price(),
                deliverydate=catelog_obj.get_delivery_date(), capacity=catelog_obj.get_capacity(),
                direct_to=catelog_obj.get_direct_to(),
                modify_status=-1,
                modify_ref_id=-1,modified_by=-1,portal_flag=catelog_obj.get_portal_flag())

            self.audit_function(catelog_update, vendor_id, user_id, req_status, old_id, ModifyStatus.update)
            # self.audit_function(catelog_del, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)
        elif mod_status == ModifyStatus.create:


            catelog_update=Catelog.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).update(modify_status=-1,
                                                     modify_ref_id=-1,modified_by=-1)
            self.audit_function(catelog_update, vendor_id, user_id, req_status, new_id, ModifyStatus.update)
        else:
            catelog = Catelog.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).delete()

            Audit_Action = ModifyStatus.delete
            self.audit_function(catelog, vendor_id, user_id, req_status, old_id, Audit_Action)
        return

    def audit_function(self, catelog, vendor_id, user_id, req_status, id, action):
        if action == ModifyStatus.delete:
            data = None
        elif action == ModifyStatus.update:
            data = catelog
        else:
            data = catelog.__dict__
            del data['_state']
        audit_service = VendorAuditService(self._scope())
        audit_obj = VendorAuditResponse()
        audit_obj.set_refid(vendor_id)
        audit_obj.set_reftype(VendorRefType.VENDOR)
        audit_obj.set_userid(user_id)
        audit_obj.set_reqstatus(req_status)
        audit_obj.set_relrefid(id)
        audit_obj.set_relreftype(VendorRefType.VENDOR_CATELOG)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_vendoraudit(audit_obj)

        return

    def get_cat_forrcn(self, product_id, query,catname_supplier,dts,vys_page):
        condition = Q(status=1) &Q(entity_id=self._entity_id())
        if product_id:
            condition &=Q(productname=product_id)
        if dts:
            condition &=Q(dts__icontains=dts)
        if query:
            condition &= Q(name__icontains=query)
        if catname_supplier:
            condition &= Q(name__icontains=catname_supplier)

        queue_arr = Catelog.objects.using(self._current_app_schema()).filter(condition).values('productname','id','name','activitydetail_id','fromdate','todate','unitprice','uom')
        # queue_arr = Catelog.objects.filter(activitydetail_id__activity_id__branch_id__name='t')
        logger.info(str(queue_arr.query))
        if queue_arr:
            df = pd.DataFrame.from_records(queue_arr)
            df['fromdate'] = pd.to_datetime(df["fromdate"]).dt.strftime('%Y-%m-%d')
            df['todate'] = pd.to_datetime(df["todate"]).dt.strftime('%Y-%m-%d')

            logger.info(str(df['activitydetail_id']))
            for index, j in df.iterrows():
                supp=list(ActivityDetail.objects.using(self._current_app_schema()).filter(id=j['activitydetail_id'], entity_id=self._entity_id()).values_list('activity_id',flat=True))
                branch_ids=list(SupplierActivity.objects.using(self._current_app_schema()).filter(id__in=supp, entity_id=self._entity_id()).values_list('branch_id',flat=True))
                branch_data=SupplierBranch.objects.using(self._current_app_schema()).filter(id__in=branch_ids, entity_id=self._entity_id()).values('name','code','id')
                # logger.info(branch_data)
                # if (j['product_gid'] != 0):
                df.loc[index, 'branch_data'] = branch_data

            queue_arr = df.to_dict('records')
        else:
            queue_arr =[]
        vlist = NWisefinList()
        vlist.append(queue_arr)
        vpage = NWisefinPaginator(queue_arr, vys_page, 10)
        vlist.set_pagination(vpage)
        return vlist

    def fetch_supplier_catalog(self,supplier_id,product_id,dts,vys_page,employee_id,query):
        ActivityList = SupplierActivity.objects.using(self._current_app_schema()).filter(branch_id=supplier_id, entity_id=self._entity_id()).values_list('id', flat=True)
        ActivityDtlList = ActivityDetail.objects.using(self._current_app_schema()).filter(activity_id__in=ActivityList, entity_id=self._entity_id()).values_list('id', flat=True)
        condition=Q(activitydetail_id__in=ActivityDtlList) & Q(productname=product_id) & Q(direct_to=dts) &Q(entity_id=self._entity_id())
        if query is not None:
            condition &=Q(name__icontains=query)
        CateloglList = Catelog.objects.using(self._current_app_schema()).filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
        vlist=NWisefinList()
        for catelog in CateloglList:
            catelog_data = CatelogResponse()
            catelog_data.set_id(catelog.id)
            catelog_data.set_activitydetail_id(catelog.activitydetail_id)
            catelog_data.set_detailname(catelog.detailname)
            catelog_data.set_productname(catelog.productname)
            catelog_data.set_category(catelog.category)
            catelog_data.set_subcategory(catelog.subcategory)
            catelog_data.set_name(catelog.name)
            catelog_data.set_specification(catelog.specification)
            catelog_data.set_size(catelog.size)
            catelog_data.set_remarks(catelog.remarks)
            catelog_data.set_uom(catelog.uom)
            catelog_data.set_unitprice(catelog.unitprice)
            catelog_data.set_fromdate(catelog.fromdate)
            catelog_data.set_todate(catelog.todate)
            catelog_data.set_packing_price(catelog.packing_price)
            catelog_data.set_delivery_date(catelog.deliverydate)
            catelog_data.set_capacity(catelog.capacity)
            catelog_data.set_direct_to(catelog.direct_to)
            catelog_data.set_created_by(catelog.created_by)
            catelog_data.set_modify_ref_id(catelog.modify_ref_id)
            catelog_data.set_modify_status(catelog.modify_status)
            catelog_data.set_portal_flag(catelog.portal_flag)
            vlist.append(catelog_data)
        vpage = NWisefinPaginator(CateloglList, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist

    def fetch_product_catalog(self,product_id,dts,vys_page,employee_id,query):
        condition = Q(productname=product_id) & Q(direct_to=dts) &Q(entity_id=self._entity_id())
        if query is not None:
            condition &= Q(name__icontains=query)
        CateloglList = Catelog.objects.using(self._current_app_schema()).filter(condition)
        list_ary=[]
        list_id=[]
        for catelog in CateloglList:
            if catelog.name not in list_ary:
                list_id.append(catelog.id)
                list_ary.append(catelog.name)
        CateloglList1 = Catelog.objects.using(self._current_app_schema()).filter(id__in=list_id, entity_id=self._entity_id())[vys_page.get_offset():vys_page.get_query_limit()]
        vlist = NWisefinList()
        if len(CateloglList1) >0:
            for catelog in CateloglList1:
                catelog_data = CatelogResponse()
                catelog_data.set_id(catelog.id)
                catelog_data.set_activitydetail_id(catelog.activitydetail_id)
                catelog_data.set_detailname(catelog.detailname)
                catelog_data.set_productname(catelog.productname)
                catelog_data.set_category(catelog.category)
                catelog_data.set_subcategory(catelog.subcategory)
                catelog_data.set_name(catelog.name)
                catelog_data.set_specification(catelog.specification)
                catelog_data.set_size(catelog.size)
                catelog_data.set_remarks(catelog.remarks)
                catelog_data.set_uom(catelog.uom)
                catelog_data.set_unitprice(catelog.unitprice)
                catelog_data.set_fromdate(catelog.fromdate)
                catelog_data.set_todate(catelog.todate)
                catelog_data.set_packing_price(catelog.packing_price)
                catelog_data.set_delivery_date(catelog.deliverydate)
                catelog_data.set_capacity(catelog.capacity)
                catelog_data.set_direct_to(catelog.direct_to)
                catelog_data.set_created_by(catelog.created_by)
                catelog_data.set_modify_ref_id(catelog.modify_ref_id)
                catelog_data.set_modify_status(catelog.modify_status)
                catelog_data.set_portal_flag(catelog.portal_flag)
                vlist.append(catelog_data)
            vpage = NWisefinPaginator(CateloglList1, vys_page.get_index(), 10)
            vlist.set_pagination(vpage)
        return vlist

    def fetch_catalog_unitprice(self,catalog_name,supplier_id, product_id, vys_page,employee_id,query):
        ActivityList = SupplierActivity.objects.using(self._current_app_schema()).filter(branch_id=supplier_id, entity_id=self._entity_id()).values_list('id', flat=True)
        ActivityDtlList = ActivityDetail.objects.using(self._current_app_schema()).filter(activity_id__in=ActivityList, entity_id=self._entity_id()).values_list('id', flat=True)
        condition = Q(activitydetail_id__in=ActivityDtlList) & Q(name=catalog_name) & Q(productname=product_id) &Q(entity_id=self._entity_id())
        if query is not None:
            condition &= Q(name__icontains=query)
        CateloglList = Catelog.objects.using(self._current_app_schema()).filter(condition)
        vlist = NWisefinList()
        from masterservice.service.uomservice import UomService
        for catelog in CateloglList:
                catelog_data = CatelogResponse()
                catelog_data.set_id(catelog.id)
                catelog_data.set_name(catelog.name)
                uom_service = UomService(self._scope())
                uom_id = catelog.uom
                if uom_id is not None:
                    uom = uom_service.fetch_uom(uom_id, employee_id)
                    catelog_data.uom = uom
                catelog_data.set_unitprice(catelog.unitprice)
                vlist.append(catelog_data)

        return vlist

    def fetch_unitprice(self, supplier_id, product_id, emp_id):
        ActivityList = SupplierActivity.objects.using(self._current_app_schema()).filter(branch_id=supplier_id, entity_id=self._entity_id()).values_list('id', flat=True)
        ActivityDtlList = ActivityDetail.objects.using(self._current_app_schema()).filter(activity_id__in=ActivityList, entity_id=self._entity_id()).values_list('id', flat=True)
        condition = Q(activitydetail_id__in=ActivityDtlList) & Q(productname=product_id) & Q(direct_to=0) &Q(entity_id=self._entity_id())
        # catelog = Catelog.objects.filter(condition).order_by('-created_date')
        # catelog = catelog[0]
        catelog = Catelog.objects.using(self._current_app_schema()).get(condition)
        from masterservice.service.uomservice import UomService
        catelog_data = CatelogResponse()
        catelog_data.set_id(catelog.id)
        catelog_data.set_name(catelog.name)
        uom_service = UomService(self._scope())
        uom_id = catelog.uom
        if uom_id is not None:
            uom = uom_service.fetch_uom(uom_id, emp_id)
            catelog_data.uom = uom
        catelog_data.set_unitprice(catelog.unitprice)
        return catelog_data

    def product_get(self, catalogId_arr):
        catalog = Catelog.objects.using(self._current_app_schema()).filter(id__in=catalogId_arr, entity_id = self._entity_id()).values('id', 'code', 'name', 'productname')
        product_list_data = NWisefinList()
        for i in catalog:
            data = {"id": i['id'], "code": i['code'], "name": i['name']}
            product_list_data.append(data)
        return product_list_data

    def fetch_catelogdata(self, catelog_id):
        catelog = Catelog.objects.using(self._current_app_schema()).get(id=catelog_id,entity_id = self._entity_id())
        catelog_data = {"id": catelog.id, "name": catelog.name}
        return catelog_data

    def catelog_productdts(self, product_data, dts):
        productId_arr = product_data['product_id']
        catalog_obj1 = Catelog.objects.using(self._current_app_schema()).filter(productname__in=productId_arr, direct_to=dts, entity_id = self._entity_id())
        list_id = []
        list_ary = []
        if len(catalog_obj1) > 0:
            for c in catalog_obj1:
                if c.productname not in list_ary:
                    list_id.append(c.id)
                    list_ary.append(c.productname)
        product_data = {"id": list_ary}
        print(list_id)
        print("p", list_ary)
        return product_data
