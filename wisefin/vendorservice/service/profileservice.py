import django
from django.db import IntegrityError
from django.db.models import Q
from nwisefin.settings import logger
from userservice.models import Employee
from vendorservice.data.response.supplierresponse import ProfileResponse
from vendorservice.data.response.vendorauditresponse import VendorAuditResponse
from vendorservice.models import VendorProfile,VendorModificationRel
from vendorservice.service.vendorauditservice import VendorAuditService
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from vendorservice.util.vendorutil import VendorRefType, ModifyStatus, RequestStatusUtil
from django.db.models import Max
from vendorservice.service.vendorservice import VendorService
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace


class ProfileService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def create_profile(self, profile_obj,vendor_id,user_id):
        req_status = RequestStatusUtil.ONBOARD
        if not profile_obj.get_id() is None:
            # try:
                profile_update = VendorProfile.objects.using(self._current_app_schema()).filter(id=profile_obj.get_id(), entity_id=self._entity_id()).update(year=profile_obj.get_year(),
                associate_year=profile_obj.get_associate_year(),award_details=profile_obj.get_award_details(),
                permanent_employee=profile_obj.get_permanent_employee(),temporary_employee=profile_obj.get_temporary_employee(),
                total_employee=profile_obj.get_total_employee(),
                branch=profile_obj.get_branch(),factory=profile_obj.get_factory(),remarks=profile_obj.get_remarks(),
                updated_by=user_id,updated_date=timezone.now(), portal_flag=profile_obj.get_portal_flag())

                profile_auditdata={'id':profile_obj.get_id(),'year':profile_obj.get_year(),
                'associate_year':profile_obj.get_associate_year(),'award_details':profile_obj.get_award_details(),
                'permanent_employee':profile_obj.get_permanent_employee(),'temporary_employee':profile_obj.get_temporary_employee(),
                'total_employee':profile_obj.get_total_employee(),
                'branch':profile_obj.get_branch(),'factory':profile_obj.get_factory(),'remarks':profile_obj.get_remarks(),
                'updated_by':user_id,'updated_date':timezone.now()}

                profile = VendorProfile.objects.using(self._current_app_schema()).get(id=profile_obj.get_id(), entity_id=self._entity_id())

                self.audit_function(profile_auditdata, user_id, user_id, req_status, profile.id, ModifyStatus.update)

            # except IntegrityError as error:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except VendorProfile.DoesNotExist:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_PROFILE_ID)
            #     error_obj.set_description(ErrorDescription.INVALID_PROFILE_ID)
            #     return error_obj
            # except:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj
        else:
            # try:
                profile = VendorProfile.objects.using(self._current_app_schema()).create(year=profile_obj.get_year(),
                associate_year=profile_obj.get_associate_year(),award_details=profile_obj.get_award_details(),
                permanent_employee=profile_obj.get_permanent_employee(),temporary_employee=profile_obj.get_temporary_employee(),
                total_employee=profile_obj.get_total_employee(),
                branch=profile_obj.get_branch(),factory=profile_obj.get_factory(),remarks=profile_obj.get_remarks(),
                created_by=user_id,vendor_id=vendor_id, entity_id=self._entity_id(),portal_flag=profile_obj.get_portal_flag())
                self.audit_function(profile, vendor_id, user_id, req_status, profile.id, ModifyStatus.create)
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

        profile_data = ProfileResponse()
        profile_data.set_id(profile.id)
        profile_data.set_year(profile.year)
        profile_data.set_associate_year(profile.associate_year)
        profile_data.set_award_details(profile.award_details)
        profile_data.set_permanent_employee(profile.permanent_employee)
        profile_data.set_temporary_employee(profile.temporary_employee)
        profile_data.set_total_employee(profile.total_employee)
        profile_data.set_branch(profile.branch)
        profile_data.set_factory(profile.factory)
        profile_data.set_remarks(profile.remarks)
        profile_data.set_portal_flag(profile.portal_flag)
        return profile_data

    def fetch_profile_list(self,vendor_id,user_id):
        profilelist = VendorProfile.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())
        list_length = len(profilelist)
        logger.info(str(list_length))
        if list_length <= 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PROFILE_ID)
            error_obj.set_description(ErrorDescription.INVALID_PROFILE_ID)
            return error_obj
        else:
            profile_list_data = NWisefinList()
            for profile in profilelist:
                profile_data = ProfileResponse()
                profile_data.set_id(profile.id)
                profile_data.set_year(profile.year)
                profile_data.set_associate_year(profile.associate_year)
                profile_data.set_award_details(profile.award_details)
                profile_data.set_permanent_employee(profile.permanent_employee)
                profile_data.set_temporary_employee(profile.temporary_employee)
                profile_data.set_total_employee(profile.total_employee)
                profile_data.set_branch(profile.branch)
                profile_data.set_factory(profile.factory)
                profile_data.set_remarks(profile.remarks)
                profile_data.set_portal_flag(profile.portal_flag)
                profile_list_data.append(profile_data)
            return profile_list_data

    def fetch_profile(self,vendor_id,user_id):
        try:
            profile = VendorProfile.objects.using(self._current_app_schema()).get(vendor_id=vendor_id, entity_id=self._entity_id())
            profile_data = ProfileResponse()
            profile_data.set_id(profile.id)
            profile_data.set_year(profile.year)
            profile_data.set_associate_year(profile.associate_year)
            profile_data.set_award_details(profile.award_details)
            profile_data.set_permanent_employee(profile.permanent_employee)
            profile_data.set_temporary_employee(profile.temporary_employee)
            profile_data.set_total_employee(profile.total_employee)
            profile_data.set_branch(profile.branch)
            profile_data.set_factory(profile.factory)
            profile_data.set_remarks(profile.remarks)
            profile_data.set_portal_flag(profile.portal_flag)
            return profile_data

        except VendorProfile.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PROFILE_ID)
            error_obj.set_description(ErrorDescription.INVALID_PROFILE_ID)
            return error_obj

    def delete_profile(self, profile_id,vendor_id,user_id):

        profile = VendorProfile.objects.using(self._current_app_schema()).filter(id=profile_id, entity_id=self._entity_id()).delete()
        req_status = RequestStatusUtil.ONBOARD
        self.audit_function(profile, vendor_id, user_id, req_status, profile.id, ModifyStatus.delete)
        if profile[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PROFILE_ID)
            error_obj.set_description(ErrorDescription.INVALID_PROFILE_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def create_profile_modification(self, profile_obj,vendor_id,user_id):
        if not profile_obj.get_id() is None:
            vendor_service = VendorService(self._scope())
            # try:
            ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_PROFILE, profile_obj.get_id())
            if ref_flag == True:
                    profile = VendorProfile.objects.using(self._current_app_schema()).filter(id=profile_obj.get_id(), entity_id=self._entity_id()).update(year=profile_obj.get_year(),
                                                           associate_year=profile_obj.get_associate_year(),
                                                           award_details=profile_obj.get_award_details(),
                                                           permanent_employee=profile_obj.get_permanent_employee(),
                                                           temporary_employee=profile_obj.get_temporary_employee(),
                                                           total_employee=profile_obj.get_total_employee(),
                                                           branch=profile_obj.get_branch(),
                                                           factory=profile_obj.get_factory(),
                                                           remarks=profile_obj.get_remarks(), modify_status=1,
                                                            vendor_id=vendor_id,portal_flag=profile_obj.get_portal_flag()
                                                           )
                    profile=VendorProfile.objects.using(self._current_app_schema()).get(id=profile_obj.get_id(), entity_id=self._entity_id())

            else:
                    profile = VendorProfile.objects.using(self._current_app_schema()).create(year=profile_obj.get_year(),
                    associate_year=profile_obj.get_associate_year(),award_details=profile_obj.get_award_details(),
                    permanent_employee=profile_obj.get_permanent_employee(),temporary_employee=profile_obj.get_temporary_employee(),
                    total_employee=profile_obj.get_total_employee(),
                    branch=profile_obj.get_branch(),factory=profile_obj.get_factory(),remarks=profile_obj.get_remarks(),modify_status=1,
                    created_by=user_id,vendor_id=vendor_id, entity_id=self._entity_id(),
                    portal_flag=profile_obj.get_portal_flag()
                                                   )

                    profile_update = VendorProfile.objects.using(self._current_app_schema()).filter(id=profile_obj.get_id(), entity_id=self._entity_id()).update(modify_ref_id=profile.id,modified_by=user_id)
                    VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=profile_obj.get_id(),
                                                         ref_type=VendorRefType.VENDOR_PROFILE, mod_status=2,
                                                         modify_ref_id=profile.id, entity_id=self._entity_id())
                    req_status = RequestStatusUtil.MODIFICATION
                # self.audit_function(profile, vendor_id, user_id, req_status, profile.id, ModifyStatus.create)
                # self.audit_function(profile_update, vendor_id, user_id, req_status, profile_update.id, ModifyStatus.update)
        else:
            profile = VendorProfile.objects.using(self._current_app_schema()).create(year=profile_obj.get_year(),
                                                   associate_year=profile_obj.get_associate_year(),
                                                   award_details=profile_obj.get_award_details(),
                                                   permanent_employee=profile_obj.get_permanent_employee(),
                                                   temporary_employee=profile_obj.get_temporary_employee(),
                                                   total_employee=profile_obj.get_total_employee(),
                                                   branch=profile_obj.get_branch(), factory=profile_obj.get_factory(),
                                                   remarks=profile_obj.get_remarks(), modify_status=1,
                                                   created_by=user_id, vendor_id=vendor_id, entity_id=self._entity_id(),
                                                   portal_flag=profile_obj.get_portal_flag()
                                                   )

            profile_update = VendorProfile.objects.using(self._current_app_schema()).filter(id=profile.id, entity_id=self._entity_id()).update(modify_ref_id=profile.id,
                                                                                          modified_by=user_id)

            VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=profile.id,
                                                 ref_type=VendorRefType.VENDOR_PROFILE, mod_status=1,
                                                 modify_ref_id=profile.id, entity_id=self._entity_id())

        profile_data = ProfileResponse()
        profile_data.set_id(profile.id)
        profile_data.set_year(profile.year)
        profile_data.set_associate_year(profile.associate_year)
        profile_data.set_award_details(profile.award_details)
        profile_data.set_permanent_employee(profile.permanent_employee)
        profile_data.set_temporary_employee(profile.temporary_employee)
        profile_data.set_total_employee(profile.total_employee)
        profile_data.set_branch(profile.branch)
        profile_data.set_factory(profile.factory)
        profile_data.set_remarks(profile.remarks)
        profile_data.set_portal_flag(profile.portal_flag)
        return profile_data

    def modification_action_vendorprofile(self, mod_status, old_id, new_id,vendor_id,user_id):
        # emp = Employee.objects.get(user_id=user_id)
        # employee_id = emp.id
        if mod_status == 2:
            profile_obj = self.approve_profile_modification(new_id,user_id)
            profile = VendorProfile.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(year=profile_obj.get_year(),
                                                                     vendor_id=vendor_id,
                                                                                   associate_year=profile_obj.get_associate_year(),
                                                                                   award_details=profile_obj.get_award_details(),
                                                                                   permanent_employee=profile_obj.get_permanent_employee(),
                                                                                   temporary_employee=profile_obj.get_temporary_employee(),
                                                                                   total_employee=profile_obj.get_total_employee(),
                                                                                   branch=profile_obj.get_branch(),
                                                                                   factory=profile_obj.get_factory(),
                                                                                   remarks=profile_obj.get_remarks(),
                                                                     modify_status=-1,
                                                                     modify_ref_id=-1,modified_by=-1,
                                                                     portal_flag=profile_obj.get_portal_flag()
                                                                     )


            req_status = RequestStatusUtil.MODIFICATION
            self.audit_function(profile, vendor_id, user_id, req_status, old_id, ModifyStatus.update)
            # self.audit_function(profile_del, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)
        if mod_status==1:
            profile_obj = VendorProfile.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).update(modify_status=-1, modified_by=-1, modify_ref_id=-1)
        if mod_status==0:
            profile_obj = VendorProfile.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).delete()
        return
    def fetch_profile_modification(self,vendor_id,user_id):
        try:
            profile = VendorProfile.objects.using(self._current_app_schema()).get(Q(vendor_id=vendor_id) & Q(modify_status=1)&Q(entity_id=self._entity_id()))
            profile_data = ProfileResponse()
            profile_data.set_id(profile.id)
            profile_data.set_year(profile.year)
            profile_data.set_associate_year(profile.associate_year)
            profile_data.set_award_details(profile.award_details)
            profile_data.set_permanent_employee(profile.permanent_employee)
            profile_data.set_temporary_employee(profile.temporary_employee)
            profile_data.set_total_employee(profile.total_employee)
            profile_data.set_branch(profile.branch)
            profile_data.set_factory(profile.factory)
            profile_data.set_remarks(profile.remarks)
            profile_data.set_portal_flag(profile.portal_flag)
            return profile_data

        except VendorProfile.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PROFILE_ID)
            error_obj.set_description(ErrorDescription.INVALID_PROFILE_ID)
            return error_obj

    def approve_profile_modification(self,profile_id,user_id):
        try:
            profile = VendorProfile.objects.using(self._current_app_schema()).get(Q(id=profile_id) & Q(modify_status=1)&Q(entity_id=self._entity_id()))
            profile_data = ProfileResponse()
            profile_data.set_id(profile.id)
            profile_data.set_year(profile.year)
            profile_data.set_associate_year(profile.associate_year)
            profile_data.set_award_details(profile.award_details)
            profile_data.set_permanent_employee(profile.permanent_employee)
            profile_data.set_temporary_employee(profile.temporary_employee)
            profile_data.set_total_employee(profile.total_employee)
            profile_data.set_branch(profile.branch)
            profile_data.set_factory(profile.factory)
            profile_data.set_remarks(profile.remarks)
            profile_data.set_portal_flag(profile.portal_flag)
            return profile_data

        except VendorProfile.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PROFILE_ID)
            error_obj.set_description(ErrorDescription.INVALID_PROFILE_ID)
            return error_obj

    def modification_reject_vendorprofile(self, mod_status, old_id, new_id, user_id, vendor_id):
        # emp = Employee.objects.get(user_id=user_id)
        # employee_id = emp.id
        if mod_status == ModifyStatus.update:
            profile_del=VendorProfile.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()
            vendor_profile =VendorProfile.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(modify_ref_id=-1,modified_by=-1)

            req_status = RequestStatusUtil.MODIFICATION
            self.audit_function(profile_del, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)
            self.audit_function(vendor_profile, vendor_id, user_id, req_status, old_id, ModifyStatus.update)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj

    def audit_function(self, profile, vendor_id, user_id, req_status, id, action):
        if action == ModifyStatus.delete:
            data = None
        elif action == ModifyStatus.update:
            data = profile
        else:
            data = profile.__dict__
            del data['_state']
        audit_service = VendorAuditService(self._scope())
        audit_obj = VendorAuditResponse()
        audit_obj.set_refid(vendor_id)
        audit_obj.set_reftype(VendorRefType.VENDOR)
        audit_obj.set_userid(user_id)
        audit_obj.set_reqstatus(req_status)
        audit_obj.set_relrefid(id)
        audit_obj.set_relreftype(VendorRefType.VENDOR_PROFILE)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_vendoraudit(audit_obj)
        return

    def vow_fetch_profile(self,vendor_id,user_id):
        try:
            profile = VendorProfile.objects.using(self._current_app_schema()).get(vendor_id=vendor_id, entity_id=self._entity_id(),
                                                                                  modify_status=-1)
            profile_data = ProfileResponse()
            profile_data.set_id(profile.id)
            profile_data.set_year(profile.year)
            profile_data.set_associate_year(profile.associate_year)
            profile_data.set_award_details(profile.award_details)
            profile_data.set_permanent_employee(profile.permanent_employee)
            profile_data.set_temporary_employee(profile.temporary_employee)
            profile_data.set_total_employee(profile.total_employee)
            profile_data.set_branch(profile.branch)
            profile_data.set_factory(profile.factory)
            profile_data.set_remarks(profile.remarks)
            profile_data.set_portal_flag(profile.portal_flag)
            return profile_data

        except VendorProfile.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PROFILE_ID)
            error_obj.set_description(ErrorDescription.INVALID_PROFILE_ID)
            return error_obj

