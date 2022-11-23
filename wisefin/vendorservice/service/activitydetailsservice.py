from userservice.models import Employee
from vendorservice.data.response.activitydetailsresponse import ActivityDetailsResponse
from vendorservice.data.response.vendorauditresponse import VendorAuditResponse
from vendorservice.service.vendorauditservice import VendorAuditService
from vendorservice.service.vendorservice import VendorService
from vendorservice.models import ActivityDetail ,VendorModificationRel ,SupplierActivity,SupplierBranch, Catelog
from django.db import IntegrityError
from userservice.service.employeeservice import EmployeeService
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.utilityservice import NWisefinUtilityService
from django.db.models import Q
from vendorservice.util.vendorutil import ModifyStatus, VendorRefType, RequestStatusUtil
from nwisefin.settings import logger
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace


class ActivityDetailsService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def create_activitydtl(self,activity_id, activitydtl_obj, user_id, vendor_id):
        # vendor_service = VendorService()
        # vendor_status = vendor_service.is_active(activitydtl_obj.get_vendor_id)
        # logger.info(vendor_status)
        # if vendor_status != 1:

            req_status = RequestStatusUtil.ONBOARD
            if not activitydtl_obj.get_id() is None:
                # try:
                    activitydtl_update = ActivityDetail.objects.using(self._current_app_schema()).filter(id=activitydtl_obj.get_id(), entity_id=self._entity_id()).update(
                                                                activity_id=activity_id,
                                                                # code=activitydtl_obj.get_code(),
                                                                detailname=activitydtl_obj.get_detailname(),
                                                                raisor=activitydtl_obj.get_raisor(),
                                                                approver=activitydtl_obj.get_approver(),
                                                                remarks=activitydtl_obj.get_remarks(),
                                                                updated_date=timezone.now(),
                                                                updated_by=user_id,portal_flag=activitydtl_obj.get_portal_flag())

                    activitydtl_auditdata={'id':activitydtl_obj.get_id(),
                                                                'activity_id':activity_id,
                                                                'code':activitydtl_obj.get_code(),
                                                                'detailname':activitydtl_obj.get_detailname(),
                                                                'raisor':activitydtl_obj.get_raisor(),
                                                                'approver':activitydtl_obj.get_approver(),
                                                                'remarks':activitydtl_obj.get_remarks(),
                                                                'updated_date':timezone.now(),
                                                                'updated_by':user_id}

                    activitydtl = ActivityDetail.objects.using(self._current_app_schema()).get(id=activitydtl_obj.get_id(),entity_id=self._entity_id())

                    Audit_Action = ModifyStatus.update
                    self.audit_function(activitydtl_auditdata, vendor_id, user_id, req_status, activitydtl.id, Audit_Action)


                # except IntegrityError as error:
                #     error_obj = Error()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj
                # except ActivityDetail.DoesNotExist:
                #     error_obj = Error()
                #     error_obj.set_code(ErrorMessage.INVALID_VENDORDACTIVITYDETAILS_ID)
                #     error_obj.set_description(ErrorDescription.INVALID_VENDORDACTIVITYDETAILS_ID)
                #     return error_obj
                # except:
                #     error_obj = Error()
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                #     return error_obj
            else:
                # try:

                    activitydtl = ActivityDetail.objects.using(self._current_app_schema()).create(activity_id=activity_id,
                                                                #code=activitydtl_obj.get_code(),
                                                                detailname=activitydtl_obj.get_detailname(),
                                                                raisor=activitydtl_obj.get_raisor(),
                                                                approver=activitydtl_obj.get_approver(),
                                                                remarks=activitydtl_obj.get_remarks(),
                                                                created_by=user_id, entity_id=self._entity_id(),portal_flag=activitydtl_obj.get_portal_flag())
                    code = "AD" + str(activitydtl.id)
                    activitydtl.code = code
                    activitydtl.save()
                    Audit_Action = ModifyStatus.create
                    vendor_service=VendorService(self._scope())
                    vendor_check1 = vendor_service.activtydtl_validate(activity_id)
                    branch_obj = SupplierActivity.objects.using(self._current_app_schema()).get(id=activity_id)
                    branch_id=branch_obj.branch.id
                    if vendor_check1 == True:
                        vendor_branchupdate = SupplierActivity.objects.using(self._current_app_schema()).filter(id=activity_id, entity_id=self._entity_id()).update(is_validate=True)
                    else:
                        vendor_branchupdate = SupplierActivity.objects.using(self._current_app_schema()).filter(id=activity_id, entity_id=self._entity_id()).update(is_validate=False)
                    vendor_check = vendor_service.branchvalidate(branch_id)
                    if vendor_check == True:
                        vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).update(is_validate=True)
                    else:
                        vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).update(is_validate=False)

                    self.audit_function(activitydtl, vendor_id, user_id, req_status, activitydtl.id, Audit_Action)
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
            activitydetails_data = ActivityDetailsResponse()
            activitydetails_data.set_id(activitydtl.id)
            activitydetails_data.set_activity_id(activitydtl.activity_id)
            activitydetails_data.set_code(activitydtl.code)
            activitydetails_data.set_detailname(activitydtl.detailname)
            activitydetails_data.set_raisor(activitydtl.raisor)
            activitydetails_data.set_approver(activitydtl.approver)
            activitydetails_data.set_remarks(activitydtl.remarks)
            activitydetails_data.set_portal_flag(activitydtl.portal_flag)

            return activitydetails_data

    # def fetch_activitydtl_list(self,activity_id,user_id):
    #         activitydtlList = ActivityDetail.objects.filter(activity_id=activity_id)
    #         list_length = len(activitydtlList)
    #         logger.info(list_length)
    #         Activitydtl_List_Data = VysfinList()
    #         if list_length <= 0:
    #             pass
    #         else:
    #             for activitydtl in activitydtlList:
    #                 activitydetails_data = ActivityDetailsResponse()
    #                 activitydetails_data.set_id(activitydtl.id)
    #                 activitydetails_data.set_activity_id(activitydtl.activity_id)
    #                 activitydetails_data.set_name(activitydtl.name)
    #                 activitydetails_data.set_detailname(activitydtl.detailname)
    #                 activitydetails_data.set_raisor(activitydtl.raisor)
    #                 activitydetails_data.set_approver(activitydtl.approver)
    #                 activitydetails_data.set_remarks(activitydtl.remarks)
    #                 Activitydtl_List_Data.append(activitydetails_data)
    #                 #activitydtl_list_data.append(activitydtl_list_data)
    #             return Activitydtl_List_Data
    #
    def fetch_activitydtl_list(self,request, vys_page,user_id,activity_id):
        if activity_id is None:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj
        query = request.GET.get('query', None)
        queue_arr= ActivityDetail.objects.using(self._current_app_schema()).filter(activity_id=activity_id, entity_id=self._entity_id()).values('id')
        condition = None
        for vendor in queue_arr:
            logger.info(str(vendor))
            if condition is None:
                condition = (Q(id__exact=vendor['id'])& (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1))&Q(entity_id=self._entity_id())
            else:
                condition |= (Q(id__exact=vendor['id'])& (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1))&Q(entity_id=self._entity_id())
        if condition is not None:
            if query != None:
                condition &= Q(detailname__icontains=query)|Q(code__icontains=query)
            activitydtlList = ActivityDetail.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        else:
            activitydtlList = []

        vlist = NWisefinList()
        user_list = []
        for vendor in activitydtlList:
            user_list.append(vendor.created_by)
        user_list = set(user_list)
        user_list = list(user_list)
        utility_service = NWisefinUtilityService()
        user_list_obj = utility_service.get_user_info(request,user_list)

        for activitydtl in activitydtlList:
            activitydetails_data = ActivityDetailsResponse()
            activitydetails_data.set_id(activitydtl.id)
            activitydetails_data.set_activity_id(activitydtl.activity_id)
            activitydetails_data.set_code(activitydtl.code)
            activitydetails_data.set_detailname(activitydtl.detailname)
            activitydetails_data.set_raisor(activitydtl.raisor)
            activitydetails_data.set_approver(activitydtl.approver)
            activitydetails_data.set_remarks(activitydtl.remarks)
            activitydetails_data.set_created_by(activitydtl.created_by)
            activitydetails_data.set_modify_ref_id(activitydtl.modify_ref_id)
            activitydetails_data.set_modify_status(activitydtl.modify_status)
            activitydetails_data.set_portal_flag(activitydtl.portal_flag)

            for ul in user_list_obj['data']:
                if ul['id'] == ActivityDetail.created_by:
                    activitydetails_data.set_created_by(ul)
            vlist.append(activitydetails_data)
        vpage = NWisefinPaginator(activitydtlList, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)

        return vlist





    def fetch_activitydtl(self,id):
            try:
                activitydtl = ActivityDetail.objects.using(self._current_app_schema()).get(id=id, entity_id=self._entity_id())
                activitydetails_data = ActivityDetailsResponse()
                activitydetails_data.set_id(activitydtl.id)
                activitydetails_data.set_activity_id(activitydtl.activity_id)
                activitydetails_data.set_code(activitydtl.code)
                activitydetails_data.set_detailname(activitydtl.detailname)
                activitydetails_data.set_raisor(activitydtl.raisor)
                activitydetails_data.set_approver(activitydtl.approver)
                activitydetails_data.set_remarks(activitydtl.remarks)
                activitydetails_data.set_created_by(activitydtl.created_by)
                activitydetails_data.set_modify_ref_id(activitydtl.modify_ref_id)
                activitydetails_data.set_modify_status(activitydtl.modify_status)
                activitydetails_data.set_portal_flag(activitydtl.portal_flag)
                return activitydetails_data
            except ActivityDetail.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_VENDORDACTIVITYDETAILS_ID)
                error_obj.set_description(ErrorDescription.INVALID_VENDORDACTIVITYDETAILS_ID)
                return error_obj

    def delete_activitydtl(self,user_id,id,vendor_id,activity_id):
            activitydtl = ActivityDetail.objects.using(self._current_app_schema()).filter(id=id, entity_id=self._entity_id()).delete()

            vendor_service = VendorService(self._scope())
            vendor_check1 = vendor_service.activtydtl_validate(activity_id)
            branch_obj = SupplierActivity.objects.using(self._current_app_schema()).get(id=activity_id, entity_id=self._entity_id())
            branch_id = branch_obj.branch.id
            if vendor_check1 == True:
                vendor_branchupdate = SupplierActivity.objects.using(self._current_app_schema()).filter(id=activity_id, entity_id=self._entity_id()).update(is_validate=True)
            else:
                vendor_branchupdate = SupplierActivity.objects.using(self._current_app_schema()).filter(id=activity_id, entity_id=self._entity_id()).update(is_validate=False)
            vendor_check = vendor_service.branchvalidate(branch_id)
            if vendor_check == True:
                vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).update(is_validate=True)
            else:
                vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).update(is_validate=False)

            if activitydtl[0] == 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_VENDORDACTIVITYDETAILS_ID)
                error_obj.set_description(ErrorDescription.INVALID_VENDORDACTIVITYDETAILS_ID)
                return error_obj
            else:
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.DELETE_MESSAGE)


                req_status = RequestStatusUtil.ONBOARD
                Audit_Action = ModifyStatus.delete
                self.audit_function(activitydtl, vendor_id, user_id, req_status, id, Audit_Action)
                return success_obj

    def modification_create_activitydtl(self,activity_id, activitydtl_obj, user_id,vendor_id):

            req_status = RequestStatusUtil.MODIFICATION
            vendor_service = VendorService(self._scope())
            if not activitydtl_obj.get_id() is None:
                # try:
                    ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_ACTIVITYDETAIL, activitydtl_obj.get_id())
                    if ref_flag==True:
                        activitydtl = ActivityDetail.objects.using(self._current_app_schema()).filter(id=activitydtl_obj.get_id(), entity_id=self._entity_id()).update(activity_id=activity_id,

                                                                       detailname=activitydtl_obj.get_detailname(),
                                                                       raisor=activitydtl_obj.get_raisor(),
                                                                       approver=activitydtl_obj.get_approver(),
                                                                       remarks=activitydtl_obj.get_remarks(),
                                                                       portal_flag=activitydtl_obj.get_portal_flag()
                                                                      )
                        activitydtl = ActivityDetail.objects.using(self._current_app_schema()).get(id=activitydtl_obj.get_id(), entity_id=self._entity_id())
                    else:

                        activitydtl = ActivityDetail.objects.using(self._current_app_schema()).create(activity_id=activity_id,
                        code=activitydtl_obj.get_code(),detailname=activitydtl_obj.get_detailname(),
                        raisor=activitydtl_obj.get_raisor(),approver=activitydtl_obj.get_approver(),
                        remarks=activitydtl_obj.get_remarks(),created_by=user_id,
                        modify_status=ModifyStatus.update,modified_by=user_id,
                        modify_ref_id=activitydtl_obj.get_id(), entity_id=self._entity_id(),portal_flag=activitydtl_obj.get_portal_flag())

                        activitydtl_update = ActivityDetail.objects.using(self._current_app_schema()).filter(id=activitydtl_obj.get_id(), entity_id=self._entity_id()).update(
                            modify_ref_id=activitydtl.id)

                        # activitydtlupdate_auditdata={'id':activitydtl_obj.get_id(),'modify_ref_id':activitydtl.id}

                        VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=activitydtl_obj.get_id(),
                                                             ref_type=VendorRefType.VENDOR_ACTIVITYDETAIL,
                                                             mod_status=ModifyStatus.update,
                                                             modify_ref_id=activitydtl.id, entity_id=self._entity_id())




                    # self.audit_function(activitydetail, vendor_id, user_id, req_status, activitydetail.id, ModifyStatus.create)
                    # self.audit_function(activitydtlupdate_auditdata, vendor_id, user_id, req_status, activitydtl_update, ModifyStatus.update)

                # except IntegrityError as error:
                #     error_obj = Error()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj
                # except ActivityDetail.DoesNotExist:
                #     error_obj = Error()
                #     error_obj.set_code(ErrorMessage.INVALID_VENDORDACTIVITYDETAILS_ID)
                #     error_obj.set_description(ErrorDescription.INVALID_VENDORDACTIVITYDETAILS_ID)
                #     return error_obj
                # except:
                #     error_obj = Error()
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                #     return error_obj
            else:
                # try:

                    activitydtl = ActivityDetail.objects.using(self._current_app_schema()).create(activity_id=activity_id,
                                detailname=activitydtl_obj.get_detailname(),
                                raisor=activitydtl_obj.get_raisor(),approver=activitydtl_obj.get_approver(),
                                remarks=activitydtl_obj.get_remarks(),created_by=user_id,
                                modify_status=ModifyStatus.create,modified_by=user_id, entity_id=self._entity_id(),portal_flag=activitydtl_obj.get_portal_flag())

                    activitydtl.modify_ref_id = activitydtl.id
                    code = "AD" + str(activitydtl.id)
                    activitydtl.code = code
                    activitydtl.save()

                    VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=activitydtl.id,
                                                         ref_type=VendorRefType.VENDOR_ACTIVITYDETAIL,
                                                         mod_status=ModifyStatus.create,
                                                         modify_ref_id=activitydtl.id, entity_id=self._entity_id())

                    vendor_check1 = vendor_service.activtydtl_validate(activity_id)
                    branch_obj=SupplierActivity.objects.using(self._current_app_schema()).get(id=activity_id, entity_id=self._entity_id())
                    branch_id=branch_obj.branch.id
                    if vendor_check1 == True:
                        vendor_branchupdate = SupplierActivity.objects.using(self._current_app_schema()).filter(id=activity_id, entity_id=self._entity_id()).update(is_validate=True)
                    else:
                        vendor_branchupdate = SupplierActivity.objects.using(self._current_app_schema()).filter(id=activity_id, entity_id=self._entity_id()).update(is_validate=False)
                    vendor_check = vendor_service.branchvalidate(branch_id)
                    if vendor_check == True:
                        vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).update(is_validate=True)
                    else:
                        vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).update(is_validate=False)

                    self.audit_function(activitydtl, vendor_id, user_id, req_status, activitydtl.id, ModifyStatus.create)
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
            activitydetails_data = ActivityDetailsResponse()
            activitydetails_data.set_id(activitydtl.id)
            activitydetails_data.set_activity_id(activitydtl.activity_id)
            activitydetails_data.set_code(activitydtl.code)
            activitydetails_data.set_detailname(activitydtl.detailname)
            activitydetails_data.set_raisor(activitydtl.raisor)
            activitydetails_data.set_approver(activitydtl.approver)
            activitydetails_data.set_remarks(activitydtl.remarks)
            activitydetails_data.set_portal_flag(activitydtl.portal_flag)


            return activitydetails_data

    def modification_delete_activitydtl(self, activitydtl_id, vendor_id, user_id,activity_id):
        # try :
            vendor_service = VendorService(self._scope())
            activitydetail_update = ActivityDetail.objects.using(self._current_app_schema()).filter(id=activitydtl_id, entity_id=self._entity_id()).update(
                modify_ref_id=activitydtl_id,modify_status=ModifyStatus.delete)
            ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_ACTIVITYDETAIL, activitydtl_id)
            if ref_flag == True:
                flag_obj = VendorModificationRel.objects.using(self._current_app_schema()).filter(
                    Q(modify_ref_id=activitydtl_id) & Q(ref_type=VendorRefType.VENDOR_ACTIVITYDETAIL)&Q(entity_id=self._entity_id())).update(
                    mod_status=ModifyStatus.delete)
            else:
                VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=activitydtl_id,
                                                     ref_type=VendorRefType.VENDOR_ACTIVITYDETAIL,
                                                     mod_status=ModifyStatus.delete,
                                                     modify_ref_id=activitydtl_id, entity_id=self._entity_id())

            vendor_service = VendorService(self._scope())
            vendor_check1 = vendor_service.activtydtl_validate(activity_id)
            branch_obj = SupplierActivity.objects.using(self._current_app_schema()).get(id=activity_id, entity_id=self._entity_id())
            branch_id = branch_obj.branch.id
            if vendor_check1 == True:
                vendor_branchupdate = SupplierActivity.objects.using(self._current_app_schema()).filter(id=activity_id, entity_id=self._entity_id()).update(is_validate=True)
            else:
                vendor_branchupdate = SupplierActivity.objects.using(self._current_app_schema()).filter(id=activity_id, entity_id=self._entity_id()).update(is_validate=False)
            vendor_check = vendor_service.branchvalidate(branch_id)
            if vendor_check == True:
                vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).update(is_validate=True)
            else:
                vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).update(is_validate=False)

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)

            req_status = RequestStatusUtil.MODIFICATION
            # self.audit_function(activitydetail_update, vendor_id, user_id, req_status, activitydtl_id, ModifyStatus.update)
            return success_obj
        # except :
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
        #     return error_obj

    def modification_action_activitydetail(self,mod_status,old_id,new_id, vendor_id, user_id):

        req_status = RequestStatusUtil.MODIFICATION
        if mod_status == ModifyStatus.update:
            activitydtl_obj = self.fetch_activitydtl(new_id)

            activitydetail_update = ActivityDetail.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(code=activitydtl_obj.get_code(),
                                detailname=activitydtl_obj.get_detailname(),raisor=activitydtl_obj.get_raisor(),
                                approver=activitydtl_obj.get_approver(),remarks=activitydtl_obj.get_remarks(),
                                modify_status=-1,modify_ref_id = -1,modified_by=-1,portal_flag=activitydtl_obj.get_portal_flag())



            self.audit_function(activitydetail_update, vendor_id, user_id, req_status, old_id, ModifyStatus.update)
            # self.audit_function(activitydtl_del, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)

        elif mod_status == ModifyStatus.create:
            activitydetail_update=ActivityDetail.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).update(modify_status=-1,
                modify_ref_id=-1,modified_by=-1)

            self.audit_function(activitydetail_update, vendor_id, user_id, req_status, new_id, ModifyStatus.update)

        else:
            activitydetail = ActivityDetail.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).delete()

            self.audit_function(activitydetail, vendor_id, user_id, req_status, old_id, ModifyStatus.delete)
        return

    def get_vendor_id(self, activity_id):
        activity = SupplierActivity.objects.using(self._current_app_schema()).filter(id=activity_id, entity_id=self._entity_id()).get()
        branch_id = activity.branch_id
        branch = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).get()
        vendor_id = branch.vendor_id
        return vendor_id

    def modification_reject_activitydetail(self, mod_status, old_id, new_id, vendor_id, user_id):

        req_status = RequestStatusUtil.MODIFICATION
        if mod_status == ModifyStatus.update:
            activitydetail=ActivityDetail.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()

            activitydetail_update=ActivityDetail.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(modify_ref_id=-1,modified_by=-1)

            self.audit_function(activitydetail, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)
            self.audit_function(activitydetail_update, vendor_id, user_id, req_status, old_id, ModifyStatus.update)

        elif mod_status == ModifyStatus.create:
            activitydetail=ActivityDetail.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()

            self.audit_function(activitydetail, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)

        else:
            activitydetail=ActivityDetail.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(modify_ref_id=-1,modified_by=-1)

            self.audit_function(activitydetail, vendor_id, user_id, req_status, old_id, ModifyStatus.update)

    def audit_function(self, activity_dtl, vendor_id, user_id, req_status, id, action):
        if action == ModifyStatus.delete:
            data = None
        elif action == ModifyStatus.update:
            data = activity_dtl
        else:
            data = activity_dtl.__dict__
            del data['_state']
        audit_service = VendorAuditService(self._scope())
        audit_obj = VendorAuditResponse()
        audit_obj.set_refid(vendor_id)
        audit_obj.set_reftype(VendorRefType.VENDOR)
        audit_obj.set_userid(user_id)
        audit_obj.set_reqstatus(req_status)
        audit_obj.set_relrefid(id)
        audit_obj.set_relreftype(VendorRefType.VENDOR_ACTIVITYDETAIL)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_vendoraudit(audit_obj)
        return

    def fetch_activity_search(self, query, vys_page):
        if query is None:
            activityList = ActivityDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by('created_date')[
                           vys_page.get_offset():vys_page.get_query_limit()]
        else:
            activityList = ActivityDetail.objects.using(self._current_app_schema()).filter(name__icontains=query, entity_id=self._entity_id()).order_by('created_date')[
                           vys_page.get_offset():vys_page.get_query_limit()]

        activity_list_data = NWisefinList()
        for activity in activityList:
            activity_data = ActivityDetailsResponse()
            activity_data.set_id(activity.id)
            activity_data.set_activity_id(activity.activity_id)
            activity_data.set_code(activity.code)
            activity_data.set_detailname(activity.detailname)
            activity_data.set_raisor(activity.raisor)
            activity_data.set_approver(activity.approver)
            activity_data.set_remarks(activity.remarks)
            activity_data.set_created_by(activity.created_by)
            activity_data.set_modify_ref_id(activity.modify_ref_id)
            activity_data.set_modify_status(activity.modify_status)
            activity_data.set_portal_flag(activity.portal_flag)
            activity_list_data.append(activity_data)
            vpage = NWisefinPaginator(activityList, vys_page.get_index(), 10)
            activity_list_data.set_pagination(vpage)
        return activity_list_data

    def delete_condition(self, activity_id, branch_id, user_id):
        catlog_id = Catelog.objects.using(self._current_app_schema()).filter(activitydetail_id=branch_id, entity_id=self._entity_id())
        catlog_len = len(catlog_id)
        if catlog_len == 0:
            # user_id = request.user.id
            # scope = request.scope
            activitydtl_service = ActivityDetailsService(self._scope())
            vendor_service = VendorService(self._scope())
            vendor_id = activitydtl_service.get_vendor_id(activity_id)
            mod_status = vendor_service.get_modification_status(vendor_id)

            if mod_status is True:
                resp_obj = activitydtl_service.modification_delete_activitydtl(branch_id, vendor_id, user_id, activity_id)
            else:
                resp_obj = activitydtl_service.delete_activitydtl(user_id, branch_id, vendor_id, activity_id)
            # response = HttpResponse(resp_obj.get(), content_type="application/json")
            return resp_obj

        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ACTIVITYID_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ACTIVITYID_ERROR)
            # response = HttpResponse(error_obj.get(), content_type="application/json")

            return error_obj

    def activitydtl_list(self,request, vys_page,user_id,activity_id):
        if activity_id is None:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj
        query = request.GET.get('query', None)
        vendor_id = self.get_vendor_id(activity_id)
        vendor_service = VendorService(self._scope())
        mod_status = vendor_service.get_modification_status(vendor_id)
        if mod_status is True:
            print('mod')
            condition = Q(activity_id=activity_id) & (Q(modify_status=1) | Q(modify_status=-1)) & Q(entity_id=self._entity_id())
        else:
            queue_arr= ActivityDetail.objects.using(self._current_app_schema()).filter(activity_id=activity_id, entity_id=self._entity_id()).values('id')
            condition = None
            for vendor in queue_arr:
                logger.info(str(vendor))
                if condition is None:
                    condition = (Q(id__exact=vendor['id'])& (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1))&Q(entity_id=self._entity_id())
                else:
                    condition |= (Q(id__exact=vendor['id'])& (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1))&Q(entity_id=self._entity_id())
        if condition is not None:
            if query != None:
                condition &= Q(detailname__icontains=query)|Q(code__icontains=query)
            activitydtlList = ActivityDetail.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        else:
            activitydtlList = []

        vlist = NWisefinList()
        user_list = []
        for vendor in activitydtlList:
            user_list.append(vendor.created_by)
        user_list = set(user_list)
        user_list = list(user_list)
        utility_service = NWisefinUtilityService()
        user_list_obj = utility_service.get_user_info(request,user_list)

        for activitydtl in activitydtlList:
            activitydetails_data = ActivityDetailsResponse()
            activitydetails_data.set_id(activitydtl.id)
            activitydetails_data.set_activity_id(activitydtl.activity_id)
            activitydetails_data.set_code(activitydtl.code)
            activitydetails_data.set_detailname(activitydtl.detailname)
            activitydetails_data.set_raisor(activitydtl.raisor)
            activitydetails_data.set_approver(activitydtl.approver)
            activitydetails_data.set_remarks(activitydtl.remarks)
            activitydetails_data.set_created_by(activitydtl.created_by)
            activitydetails_data.set_modify_ref_id(activitydtl.modify_ref_id)
            activitydetails_data.set_modify_status(activitydtl.modify_status)
            activitydetails_data.set_portal_flag(activitydtl.portal_flag)

            for ul in user_list_obj['data']:
                if ul['id'] == ActivityDetail.created_by:
                    activitydetails_data.set_created_by(ul)
            vlist.append(activitydetails_data)
        vpage = NWisefinPaginator(activitydtlList, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)

        return vlist
