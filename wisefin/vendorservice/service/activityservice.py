import django

from django.db import IntegrityError
from nwisefin.settings import logger
from userservice.models import Employee
from vendorservice.data.response.activityresponse import ActivityResponse
from vendorservice.data.response.vendorauditresponse import VendorAuditResponse
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from vendorservice.models.vendormodels import SupplierActivity,SupplierBranch,Vendor,\
    ActivityDetail,VendorModificationRel
from datetime import datetime
now = datetime.now()
from vendorservice.data.request.vendorauditrequest import VendorAuditRequest
from vendorservice.service.vendorauditservice import VendorAuditService
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.utilityservice import NWisefinUtilityService
from django.db.models import Q
from django.utils import timezone
from vendorservice.util.vendorutil import ModifyStatus, VendorRefType, RequestStatusUtil
from vendorservice.service.supplierservice import ContactService
from vendorservice.service.vendorservice import VendorService
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from userservice.service.employeeservice import EmployeeService
from masterservice.service.activityservice import Activityservice


class ActivityService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def create_activity(self, activity_obj,contact_id,user_id,branch_id,vendor_id):

        req_status = RequestStatusUtil.ONBOARD
        if not activity_obj.get_id() is None:
            # try:
                activity_update = SupplierActivity.objects.using(self._current_app_schema()).filter(id=activity_obj.get_id(), entity_id=self._entity_id()).update(
                                type=activity_obj.get_type(),
                                name=activity_obj.get_name(),
                                description=activity_obj.get_description(),
                                branch_id=branch_id,
                                start_date=activity_obj.get_startdate(),
                                end_date=activity_obj.get_enddate(),
                                contract_spend=activity_obj.get_contractspend(),
                                rm=activity_obj.get_rm(),
                                fidelity=activity_obj.get_fidelity(),
                                bidding=activity_obj.get_bidding(),
                                contact_id=contact_id,
                                activity_status=activity_obj.get_activity_status(),
                                updated_date=timezone.now(),
                                updated_by=user_id,portal_flag=activity_obj.get_portal_flag(),rel_type=activity_obj.get_rel_type(),activity_id=activity_obj.get_activity_id())

                activity_auditdata={'id':activity_obj.get_id(),
                                'type':activity_obj.get_type(),
                                'name':activity_obj.get_name(),
                                'description':activity_obj.get_description(),
                                'branch_id':branch_id,
                                'start_date':activity_obj.get_startdate(),
                                'end_date':activity_obj.get_enddate(),
                                'contract_spend':activity_obj.get_contractspend(),
                                'rm':activity_obj.get_rm(),
                                'fidelity':activity_obj.get_fidelity(),
                                'bidding':activity_obj.get_bidding(),
                                'contact_id':contact_id,
                                'activity_status':activity_obj.get_activity_status(),
                                'updated_date':timezone.now(),
                                'updated_by':user_id}

                activity_var = SupplierActivity.objects.using(self._current_app_schema()).get(id=activity_obj.get_id(), entity_id=self._entity_id())
                self.audit_function(activity_auditdata, vendor_id, user_id, req_status, activity_var.id, ModifyStatus.update)

            # except IntegrityError as error:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except SupplierActivity.DoesNotExist:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_CATEGORY_ID)
            #     error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
            #     return error_obj
            # except:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj
        else:
            # try:
                activity_var = SupplierActivity.objects.using(self._current_app_schema()).create(
                                                               type=activity_obj.get_type(),
                                                               name=activity_obj.get_name(),
                                                               description=activity_obj.get_description(),
                                                               branch_id=branch_id,
                                                               start_date=activity_obj.get_startdate(),
                                                               end_date=activity_obj.get_enddate(),
                                                               contract_spend=activity_obj.get_contractspend(),
                                                               rm=activity_obj.get_rm(),
                                                               fidelity=activity_obj.get_fidelity(),
                                                               bidding=activity_obj.get_bidding(),
                                                               activity_status=activity_obj.get_activity_status(),
                                                               contact_id=contact_id,
                                                     created_by=user_id, entity_id=self._entity_id(), portal_flag=activity_obj.get_portal_flag(),rel_type=activity_obj.get_rel_type(),activity_id=activity_obj.get_activity_id())

                vendor_service=VendorService(self._scope())
                vendor_check = vendor_service.branchvalidate(branch_id)
                if vendor_check == True:
                    vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).update(is_validate=True)
                else:
                    vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).update(is_validate=False)

                self.audit_function(activity_var, vendor_id, user_id, req_status, activity_var.id, ModifyStatus.create)
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


        activity_data = ActivityResponse()
        activity_data.set_id(activity_var.id)
        activity_data.set_type(activity_var.type)
        activity_data.set_name(activity_var.name)
        activity_data.set_description(activity_var.description)
        activity_data.set_branch(activity_var.branch_id)
        activity_data.set_startdate(activity_var.start_date)
        activity_data.set_enddate(activity_var.end_date)
        activity_data.set_contractspend(activity_var.contract_spend)
        activity_data.set_rm(activity_var.rm)
        activity_data.set_fidelity(activity_var.fidelity)
        activity_data.set_bidding(activity_var.bidding)
        activity_data.set_portal_flag(activity_var.portal_flag)
        activity_data.set_rel_type(activity_var.rel_type)
        activity_data.set_activity_id(activity_var.activity_id)
        return activity_data

    # def fetch_activity_list(self,user_id):
    #     activitylist = SupplierActivity.objects.all()
    #     list_length = len(activitylist)
    #     logger.info(list_length)
    #     if list_length <= 0:
    #         error_obj = Error()
    #         error_obj.set_code(ErrorMessage.INVALID_ACTIVITY_ID)
    #         error_obj.set_description(ErrorDescription.INVALID_ACTIVITY_ID)
    #         return error_obj
    #     else:
    #         activity_list_data = VysfinList()
    #         for activity_var in activitylist:
    #             activity_data = ActivityResponse()
    #             activity_data.set_id(activity_var.id)
    #             activity_data.set_type(activity_var.type)
    #             activity_data.set_name(activity_var.name)
    #             activity_data.set_description(activity_var.description)
    #             activity_data.set_branch(activity_var.branch)
    #             activity_data.set_startdate(activity_var.start_date)
    #             activity_data.set_enddate(activity_var.end_date)
    #             activity_data.set_contractspend(activity_var.contract_spend)
    #             activity_data.set_rm(activity_var.rm)
    #             activity_data.set_fidelity(activity_var.fidelity)
    #             activity_data.set_bidding(activity_var.bidding)
    #             activity_list_data.append(activity_data)
    #         return activity_list_data

    def fetch_activity_list(self,request, vys_page,user_id,branch_id):
        query = request.GET.get('query', None)
        queue_arr= SupplierActivity.objects.using(self._current_app_schema()).filter(branch_id=branch_id, entity_id=self._entity_id()).values('id')
        condition = None
        for vendor in queue_arr:
            logger.info(str(vendor))
            if condition is None:
                condition = (Q(id__exact=vendor['id'])& (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1)) &Q(entity_id=self._entity_id())
            else:
                condition |= (Q(id__exact=vendor['id'])& (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1)) &Q(entity_id=self._entity_id())
        if condition is not None:
            if query != None:
                condition &= Q(name__icontains =query)
            activitylist = SupplierActivity.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        else:
            activitylist = []

        vlist = NWisefinList()
        user_list = []
        activity_arr = []
        for vendor in activitylist:
            user_list.append(vendor.created_by)
        user_list = set(user_list)
        user_list = list(user_list)
        utility_service = NWisefinUtilityService()
        user_list_obj = utility_service.get_user_info(request,user_list)





        for activity_var in activitylist:
            activity_data = ActivityResponse()
            activity_id = vendor.activity_id
            activity_arr.append(activity_id)
            activity_serv = Activityservice(self._scope())
            activity_val = activity_serv.activity(activity_arr)
            activity_data.set_id(activity_var.id)
            activity_data.set_type(activity_var.type)
            activity_data.set_name(activity_var.name)
            activity_data.set_description(activity_var.description)
            activity_data.set_branch(activity_var.branch_id)
            activity_data.set_contact(activity_var.contact_id)
            activity_data.set_startdate(activity_var.start_date)
            activity_data.set_enddate(activity_var.end_date)
            activity_data.set_contractspend(activity_var.contract_spend)
            activity_data.set_rm(activity_var.rm)
            activity_data.set_fidelity(activity_var.fidelity)
            activity_data.set_bidding(activity_var.bidding)
            activity_data.set_activity_status(activity_var.activity_status)
            activity_data.set_created_by(activity_var.created_by)
            activity_data.set_modify_ref_id(activity_var.modify_ref_id)
            activity_data.set_modify_status(activity_var.modify_status)
            activity_data.set_portal_flag(activity_var.portal_flag)
            activity_data.set_rel_type(activity_var.rel_type)
            activity_data.set_activity(activity_var.activity_id, activity_val)

            for ul in user_list_obj['data']:
                if ul['id'] == SupplierActivity.created_by:
                    activity_data.set_created_by(ul)
            vlist.append(activity_data)
        vpage = NWisefinPaginator(activitylist, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist



    def fetch_activity(self, activity_id):
        try:
            activity_var = SupplierActivity.objects.using(self._current_app_schema()).get(id=activity_id, entity_id=self._entity_id())
            activity_data = ActivityResponse()
            activity_data.set_id(activity_var.id)
            activity_data.set_type(activity_var.type)
            activity_data.set_name(activity_var.name)
            activity_data.set_description(activity_var.description)
            activity_data.set_branch(activity_var.branch_id)
            activity_data.set_contact(activity_var.contact_id)
            activity_data.set_startdate(activity_var.start_date)
            activity_data.set_enddate(activity_var.end_date)
            activity_data.set_contractspend(activity_var.contract_spend)
            activity_data.set_rm(activity_var.rm)
            activity_data.set_fidelity(activity_var.fidelity)
            activity_data.set_bidding(activity_var.bidding)
            activity_data.set_activity_status(activity_var.activity_status)
            activity_data.set_created_by(activity_var.created_by)
            activity_data.set_modify_ref_id(activity_var.modify_ref_id)
            activity_data.set_modify_status(activity_var.modify_status)
            activity_data.set_portal_flag(activity_var.portal_flag)
            activity_data.set_rel_type(activity_var.rel_type)
            activity_data.set_activity_id(activity_var.activity_id)

            return activity_data
        except SupplierActivity.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_ACTIVITY_ID)
            error_obj.set_description(ErrorDescription.INVALID_ACTIVITY_ID)
            return error_obj

    def delete_activity(self, activity_id, vendor_id, user_id,branch_id):

        activity_obj = SupplierActivity.objects.using(self._current_app_schema()).get(id=activity_id, entity_id=self._entity_id())
        contact_id = activity_obj.contact_id
        activity = SupplierActivity.objects.using(self._current_app_schema()).filter(id=activity_id, entity_id=self._entity_id()).delete()
        self.audit_function(activity, vendor_id, user_id, RequestStatusUtil.ONBOARD, activity_id, ModifyStatus.delete)
        vendor_service=VendorService(self._scope())
        vendor_check = vendor_service.branchvalidate(branch_id)
        if vendor_check == True:
            vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).update(is_validate=True)
        else:
            vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).update(is_validate=False)
        contact_service = ContactService(self._scope())
        contact_service.delete_contact(contact_id, vendor_id, user_id)
        if activity[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_ACTIVITY_ID)
            error_obj.set_description(ErrorDescription.INVALID_ACTIVITY_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    # vendor status

    def get_vendorstatus_activity(self,activity_id):
        activity = SupplierActivity.objects.using(self._current_app_schema()).get(id=activity_id, entity_id=self._entity_id())
        branch_id = activity.branch_id

        branch = SupplierBranch.objects.using(self._current_app_schema()).get(id=branch_id, entity_id=self._entity_id())
        vendor_id = branch.vendor_id

        vendor = Vendor.objects.using(self._current_app_schema()).get(id=vendor_id, entity_id=self._entity_id())
        vobj = vendor.vendor_status

        return vobj

    def get_vendorstatus_catalog(self, activitydtl_id):
        activity = ActivityDetail.objects.using(self._current_app_schema()).get(id=activitydtl_id, entity_id=self._entity_id())
        activity_id = activity.activity_id

        activity = SupplierActivity.objects.using(self._current_app_schema()).get(id=activity_id, entity_id=self._entity_id())
        branch_id = activity.branch_id

        branch = SupplierBranch.objects.using(self._current_app_schema()).get(id=branch_id, entity_id=self._entity_id())
        vendor_id = branch.vendor_id

        vendor = Vendor.objects.using(self._current_app_schema()).get(id=vendor_id, entity_id=self._entity_id())
        vobj = vendor.vendor_status

        return vobj

    # modificaton

    def modification_create_activity(self, activity_obj,contact_id,user_id,branch_id,vendor_id):

        req_status = RequestStatusUtil.MODIFICATION
        vendor_service = VendorService(self._scope())
        if not activity_obj.get_id() is None:
            # try:
                ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_ACTIVITY, activity_obj.get_id())
                if ref_flag==True:
                    activity_var = SupplierActivity.objects.using(self._current_app_schema()).filter(id=activity_obj.get_id(), entity_id=self._entity_id()).update(type=activity_obj.get_type(),
                                                                   name=activity_obj.get_name(),
                                                                   description=activity_obj.get_description(),
                                                                   branch_id=branch_id,
                                                                   start_date=activity_obj.get_startdate(),
                                                                   end_date=activity_obj.get_enddate(),
                                                                   contract_spend=activity_obj.get_contractspend(),
                                                                   rm=activity_obj.get_rm(),
                                                                   fidelity=activity_obj.get_fidelity(),
                                                                   bidding=activity_obj.get_bidding(),
                                                                   contact_id=contact_id,
                                                                   activity_status=activity_obj.get_activity_status(),
                                                                   portal_flag=activity_obj.get_portal_flag(),
                                                                   rel_type=activity_obj.get_rel_type(),
                                                                   activity_id=activity_obj.get_activity_id()
                                                                   )
                    activity_var=SupplierActivity.objects.using(self._current_app_schema()).get(id=activity_obj.get_id(), entity_id=self._entity_id())
                else:
                    activity_var = SupplierActivity.objects.using(self._current_app_schema()).create(type=activity_obj.get_type(),
                                name=activity_obj.get_name(),description=activity_obj.get_description(),
                                branch_id=branch_id,start_date=activity_obj.get_startdate(),
                                end_date=activity_obj.get_enddate(),contract_spend=activity_obj.get_contractspend(),
                                rm=activity_obj.get_rm(),fidelity=activity_obj.get_fidelity(),
                                bidding=activity_obj.get_bidding(),contact_id=contact_id,
                                activity_status=activity_obj.get_activity_status(),created_by=user_id,
                                modify_status = ModifyStatus.update, modified_by = user_id,
                                modify_ref_id = activity_obj.get_id(), entity_id=self._entity_id(),portal_flag=activity_obj.get_portal_flag(),rel_type=activity_obj.get_rel_type(),activity_id=activity_obj.get_activity_id())

                    activity_update = SupplierActivity.objects.using(self._current_app_schema()).filter(id=activity_obj.get_id(), entity_id=self._entity_id()).update(modify_ref_id=activity_var.id)

                    activityupdate_auditdata={'id':activity_obj.get_id(),'modify_ref_id':activity_var.id}

                    VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=activity_obj.get_id(),
                                                     ref_type=VendorRefType.VENDOR_ACTIVITY,
                                                     mod_status=ModifyStatus.update,
                                                     modify_ref_id=activity_var.id, entity_id=self._entity_id())

                    vendor_check = vendor_service.branchvalidate(branch_id)
                    if vendor_check == True:
                        vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).update(is_validate=True)

                # activity_var1 = SupplierActivity.objects.get(id=activity_obj.get_id())
                self.audit_function(activity_var, vendor_id, user_id, req_status, activity_var.id, ModifyStatus.create)
                # self.audit_function(activityupdate_auditdata, vendor_id, user_id, req_status, activity_update, ModifyStatus.update)

            # except IntegrityError as error:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except SupplierActivity.DoesNotExist:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_CATEGORY_ID)
            #     error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
            #     return error_obj
            # except:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj
        else:
            # try:
                activity_var = SupplierActivity.objects.using(self._current_app_schema()).create(type=activity_obj.get_type(),
                            name=activity_obj.get_name(),description=activity_obj.get_description(),
                            branch_id=branch_id,start_date=activity_obj.get_startdate(),
                            end_date=activity_obj.get_enddate(),contract_spend=activity_obj.get_contractspend(),
                            rm=activity_obj.get_rm(),fidelity=activity_obj.get_fidelity(),
                            bidding=activity_obj.get_bidding(),activity_status=activity_obj.get_activity_status(),
                            contact_id=contact_id,created_by=user_id,modify_status=ModifyStatus.create,
                             modified_by=user_id, entity_id=self._entity_id(), portal_flag=activity_obj.get_portal_flag(),rel_type=activity_obj.get_rel_type(),activity_id=activity_obj.get_activity_id())

                activity_var.modify_ref_id = activity_var.id
                activity_var.save()

                VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=activity_var.id,
                                                     ref_type=VendorRefType.VENDOR_ACTIVITY,
                                                     mod_status=ModifyStatus.create,
                                                     modify_ref_id=activity_var.id, entity_id=self._entity_id())

                vendor_check = vendor_service.branchvalidate(branch_id)
                if vendor_check == True:
                    vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).update(is_validate=True)
                else:
                    vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).update(is_validate=False)

                self.audit_function(activity_var, vendor_id, user_id, req_status, activity_var.id, ModifyStatus.create)

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


        activity_data = ActivityResponse()
        activity_data.set_id(activity_var.id)
        activity_data.set_type(activity_var.type)
        activity_data.set_name(activity_var.name)
        activity_data.set_description(activity_var.description)
        activity_data.set_branch(activity_var.branch_id)
        activity_data.set_startdate(activity_var.start_date)
        activity_data.set_enddate(activity_var.end_date)
        activity_data.set_contractspend(activity_var.contract_spend)
        activity_data.set_rm(activity_var.rm)
        activity_data.set_fidelity(activity_var.fidelity)
        activity_data.set_bidding(activity_var.bidding)
        activity_data.set_portal_flag(activity_var.portal_flag)
        activity_data.set_rel_type(activity_var.rel_type)
        activity_data.set_activity_id(activity_var.activity_id)

        return activity_data

    def modification_delete_activity(self, activity_id, vendor_id,user_id,branch_id):

        req_status = RequestStatusUtil.MODIFICATION
        vendor_service = VendorService(self._scope())
        try:
            activity = SupplierActivity.objects.using(self._current_app_schema()).get(id=activity_id, entity_id=self._entity_id())
            ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_ACTIVITY, activity_id)
            activity_update = SupplierActivity.objects.using(self._current_app_schema()).filter(id=activity_id, entity_id=self._entity_id()).update(
                modify_ref_id=activity_id,modify_status=ModifyStatus.delete)

            contact_id = activity.contact_id
            if ref_flag == True:
                flag_obj = VendorModificationRel.objects.using(self._current_app_schema()).filter(Q(modify_ref_id=activity_id)&Q(ref_type=VendorRefType.VENDOR_ACTIVITY)&Q(entity_id=self._entity_id())).update(mod_status=ModifyStatus.delete)
            else:
                VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=activity_id,
                                                     ref_type=VendorRefType.VENDOR_ACTIVITY,
                                                     mod_status=ModifyStatus.delete, entity_id=self._entity_id())

            vendor_check = vendor_service.branchvalidate(branch_id)
            if vendor_check == True:
                vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).update(is_validate=True)
            else:
                vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id, entity_id=self._entity_id()).update(is_validate=False)

            # self.audit_function(activity_update, vendor_id, user_id, req_status, activity_id,  ModifyStatus.update)

            contact_service = ContactService(self._scope())
            contact_service.modification_delete_contact(contact_id, vendor_id,user_id)

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)

            return success_obj
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj

    def modification_action_activity(self,mod_status,old_id,new_id, vendor_id, user_id):

        req_status = RequestStatusUtil.MODIFICATION
        contact_service = ContactService(self._scope())
        vendor_old_id = self.get_contact_id(old_id)
        vendor_new_id = self.get_contact_id(new_id)
        contact_service.modification_action_contact(mod_status, vendor_old_id,
                                                    vendor_new_id, vendor_id, user_id)
        if mod_status == ModifyStatus.update:
            activity_obj = self.fetch_activity(new_id)
            if activity_obj.get_startdate()==str(None):
                from_date=None
            else:
                from_date= activity_obj.get_startdate()

            if activity_obj.get_enddate() == str(None):
                to_date = None
            else:
                to_date = activity_obj.get_enddate()

            activity_update = SupplierActivity.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(type=activity_obj.get_type(),
                            name=activity_obj.get_name(),description=activity_obj.get_description(),
                            start_date=from_date,
                            end_date=to_date,contract_spend=activity_obj.get_contractspend(),
                            rm=activity_obj.get_rm(),fidelity=activity_obj.get_fidelity(),
                            bidding=activity_obj.get_bidding(),activity_status=activity_obj.get_activity_status(),modified_by =-1,
                            modify_status=-1,modify_ref_id = -1,portal_flag=activity_obj.get_portal_flag(),rel_type=activity_obj.get_rel_type(),activity_id=activity_obj.get_activity_id()
                )


            self.audit_function(activity_update, vendor_id, user_id, req_status, old_id, ModifyStatus.update)
            # self.audit_function(activity, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)

        elif mod_status == ModifyStatus.create:

            activity_update =SupplierActivity.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).update(modify_status=-1,
                modify_ref_id=-1,modified_by =-1)
            self.audit_function(activity_update, vendor_id, user_id, req_status, new_id, ModifyStatus.update)

        else:
            activity = SupplierActivity.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).delete()
            self.audit_function(activity, vendor_id, user_id, req_status, old_id, ModifyStatus.delete)





        return

    def get_vendor_id(self, branch_id):
        branch = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id,entity_id=self._entity_id()).get()
        vendor_id = branch.vendor_id
        return vendor_id

    def modification_reject_activity(self, mod_status, old_id, new_id, vendor_id, user_id):


        req_status = RequestStatusUtil.MODIFICATION
        contact_service = ContactService(self._scope())
        vendor_old_id = self.get_contact_id(old_id)
        vendor_new_id = self.get_contact_id(new_id)
        contact_service.modification_reject_contact(mod_status, vendor_old_id,
                                                    vendor_new_id, vendor_id, user_id)
        if mod_status == ModifyStatus.update:
            activity_update=SupplierActivity.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()

            activity=SupplierActivity.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(modify_ref_id=-1)

            self.audit_function(activity_update, vendor_id, user_id, req_status, new_id, ModifyStatus.update)
            self.audit_function(activity, vendor_id, user_id, req_status, old_id, ModifyStatus.delete)

        elif mod_status == ModifyStatus.create:

            activity=SupplierActivity.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()
            self.audit_function(activity, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)

        else:
            activity=SupplierActivity.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(modify_ref_id=-1)
            self.audit_function(activity, vendor_id, user_id, req_status, old_id, ModifyStatus.update)



        return

    def audit_function(self, activity, vendor_id, user_id, req_status, id, action):
        if action == ModifyStatus.delete:
            data = None
        elif action == ModifyStatus.update:
            data = activity
        else:
            data = activity.__dict__
            del data['_state']
        audit_service = VendorAuditService(self._scope())
        audit_obj = VendorAuditResponse()
        audit_obj.set_refid(vendor_id)
        audit_obj.set_reftype(VendorRefType.VENDOR)
        audit_obj.set_userid(user_id)
        audit_obj.set_reqstatus(req_status)
        audit_obj.set_relrefid(id)
        audit_obj.set_relreftype(VendorRefType.VENDOR_ACTIVITY)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_vendoraudit(audit_obj)
        return

    def get_contact_id(self,activity_id):
        activity = SupplierActivity.objects.using(self._current_app_schema()).get(id=activity_id, entity_id=self._entity_id())
        contact_id = activity.contact_id
        return contact_id

    def delete_activity_using_id(self, activity_id, branch_id, user_id):
        activity_detail = ActivityDetail.objects.using(self._current_app_schema()).filter(activity_id=activity_id, entity_id=self._entity_id())
        activity_detail_len = len(activity_detail)
        logger.info(str(activity_detail_len))
        if activity_detail_len == 0:
            # scope = request.scope
            # activity_service = ActivityService(scope)
            vendor_service = VendorService(self._scope())
            vendor_id = self.get_vendor_id(branch_id)
            mod_status = vendor_service.get_modification_status(vendor_id)
            # user_id = request.user.id

            if mod_status is True:
                resp_obj = self.modification_delete_activity(activity_id, vendor_id, user_id, branch_id)
            else:
                resp_obj = self.delete_activity(activity_id, vendor_id, user_id, branch_id)
            return resp_obj
            # response = HttpResponse(resp_obj.get(), content_type="application/json")
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ACTIVITYID_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ACTIVITYID_ERROR)
            # response = HttpResponse(error_obj.get(), content_type="application/json")
            return error_obj

    def activity_list(self, request, vys_page, user_id, branch_id):
        query = request.GET.get('query', None)
        branch = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id)
        vendor_id = branch[0].vendor_id
        vendor_service = VendorService(self._scope())
        mod_status = vendor_service.get_modification_status(vendor_id)
        if mod_status is True:
            condition = Q(branch_id=branch_id) & (Q(modify_status=1) | Q(modify_status=-1)) & Q(
                entity_id=self._entity_id())
        else:
            queue_arr = SupplierActivity.objects.using(self._current_app_schema()).filter(branch_id=branch_id,
                                                                                          entity_id=self._entity_id()).values(
                'id')
            condition = None
            for activity in queue_arr:
                logger.info(str(activity))
                if condition is None:
                    condition = (Q(id__exact=activity['id']) & (
                                Q(modify_status__exact=-1) | Q(modify_status__exact=0)) & Q(modified_by=-1)) & Q(
                        entity_id=self._entity_id())
                else:
                    condition |= (Q(id__exact=activity['id']) & (
                                Q(modify_status__exact=-1) | Q(modify_status__exact=0)) & Q(modified_by=-1)) & Q(
                        entity_id=self._entity_id())
        if condition is not None:
            if query != None:
                condition &= Q(name__icontains=query)
            activitylist = SupplierActivity.objects.using(self._current_app_schema()).filter(condition).order_by(
                'created_date')[
                           vys_page.get_offset():vys_page.get_query_limit()]
        else:
            activitylist = []

        vlist = NWisefinList()
        user_list = []
        for vendor in activitylist:
            user_list.append(vendor.created_by)
        user_list = set(user_list)
        user_list = list(user_list)
        utility_service = NWisefinUtilityService()
        user_list_obj = utility_service.get_user_info(request, user_list)

        for activity_var in activitylist:
            activity_data = ActivityResponse()
            activity_data.set_id(activity_var.id)
            activity_data.set_type(activity_var.type)
            activity_data.set_name(activity_var.name)
            activity_data.set_description(activity_var.description)
            activity_data.set_branch(activity_var.branch_id)
            activity_data.set_contact(activity_var.contact_id)
            activity_data.set_startdate(activity_var.start_date)
            activity_data.set_enddate(activity_var.end_date)
            activity_data.set_contractspend(activity_var.contract_spend)
            activity_data.set_rm(activity_var.rm)
            activity_data.set_fidelity(activity_var.fidelity)
            activity_data.set_bidding(activity_var.bidding)
            activity_data.set_activity_status(activity_var.activity_status)
            activity_data.set_created_by(activity_var.created_by)
            activity_data.set_modify_ref_id(activity_var.modify_ref_id)
            activity_data.set_modify_status(activity_var.modify_status)
            activity_data.set_portal_flag(activity_var.portal_flag)
            activity_data.set_rel_type(activity_var.rel_type)
            activity_data.set_activity_id(activity_var.activity_id)

            for ul in user_list_obj['data']:
                if ul['id'] == SupplierActivity.created_by:
                    activity_data.set_created_by(ul)
            vlist.append(activity_data)
        vpage = NWisefinPaginator(activitylist, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist

    def activity_mapping(self,vendor_id):
        activity_var = SupplierActivity.objects.using(self._current_app_schema()).filter(branch__vendor_id = vendor_id).values('activity_id','id','rel_type','name','branch__vendor_id')
        data=[ y for y in activity_var if activity_var.count()>0]
        return data

