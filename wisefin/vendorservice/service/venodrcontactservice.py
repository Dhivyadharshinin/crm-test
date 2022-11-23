from userservice.models import Employee
from vendorservice.data.response.directorresponse import DirectorResponse
from vendorservice.data.response.vendorauditresponse import VendorAuditResponse
from vendorservice.service.vendorauditservice import VendorAuditService
from vendorservice.service.vendorservice import VendorService
from vendorservice.models import VendorContact,VendorModificationRel
from vendorservice.data.response.vendorcontactresponse import ContactResponse
from django.db import IntegrityError
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from vendorservice.util.vendorutil import VendorRefType, ModifyStatus, RequestStatusUtil
from django.db.models import Q
from django.db.models import Max


class VendorContactService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def create_vendorcontact(self,vendor_id, contact_obj,user_id):
        req_status = RequestStatusUtil.ONBOARD
        if not contact_obj.get_id() is None:
            # try:
                contact_update = VendorContact.objects.using(self._current_app_schema()).filter(id=contact_obj.get_id(), entity_id=self._entity_id()).update(
                                                                                       vendor_id=vendor_id,
                                                                                          name=contact_obj.get_name(),
                                                                                          designation=contact_obj.get_designation(),
                                                                                          landline=contact_obj.get_landline(),
                                                                                          landline2=contact_obj.get_landline2(),
                                                                                          mobile=contact_obj.get_mobile(),
                                                                                          mobile2=contact_obj.get_mobile2(),
                                                                                          email=contact_obj.get_email(),
                                                                                          dob=contact_obj.get_dob(),
                                                                                          wedding_date=contact_obj.get_wedding_date(),
                                                                                          updated_by=user_id,
                                                                                          updated_date=timezone.now(),
                                                                                          portal_flag=contact_obj.get_portal_flag())
                contact_auditdata={'id':contact_obj.get_id(),
                                                                                       'vendor_id':vendor_id,
                                                                                          'name':contact_obj.get_name(),
                                                                                          'designation':contact_obj.get_designation(),
                                                                                          'landline':contact_obj.get_landline(),
                                                                                          'landline2':contact_obj.get_landline2(),
                                                                                          'mobile':contact_obj.get_mobile(),
                                                                                          'mobile2':contact_obj.get_mobile2(),
                                                                                          'email':contact_obj.get_email(),
                                                                                          'dob':contact_obj.get_dob(),
                                                                                          'wedding_date':contact_obj.get_wedding_date(),
                                                                                          'updated_by':user_id,
                                                                                          'updated_date':timezone.now()}

                contact = VendorContact.objects.using(self._current_app_schema()).get(id=contact_obj.get_id(), entity_id=self._entity_id())
                self.audit_function(contact_auditdata, vendor_id, user_id, req_status, contact.id, ModifyStatus.update)



            # except IntegrityError as error:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except VendorContact.DoesNotExist:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_VendorRelContact_ID)
            #     error_obj.set_description(ErrorDescription.INVALID_VendorRelContact_ID)
            #     return error_obj
            # except:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj
        else:
            # try:
                contact = VendorContact.objects.using(self._current_app_schema()).create(
                                                          name=contact_obj.get_name(),
                                                          designation=contact_obj.get_designation(),
                                                          landline=contact_obj.get_landline(),
                                                          landline2=contact_obj.get_landline2(),
                                                          mobile=contact_obj.get_mobile(),
                                                          mobile2=contact_obj.get_mobile2(),
                                                          email=contact_obj.get_email(),
                                                          dob=contact_obj.get_dob(),
                                                          wedding_date=contact_obj.get_wedding_date(),
                                                          created_by=user_id,
                                                          vendor_id=vendor_id,entity_id=self._entity_id(),
                                                          portal_flag=contact_obj.get_portal_flag()
                                                          )
                self.audit_function(contact, vendor_id, user_id, req_status, contact.id, ModifyStatus.create)
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

        contact_data = ContactResponse()
        contact_data.set_id(contact.id)

        contact_data.set_name(contact.name)
        contact_data.set_designation(contact.designation)
        contact_data.set_landline(contact.landline)
        contact_data.set_landline2(contact.landline2)
        contact_data.set_mobile(contact.mobile)
        contact_data.set_mobile2(contact.mobile2)
        contact_data.set_email(contact.email)
        contact_data.set_dob(contact.dob)
        contact_data.set_wedding_date(contact.wedding_date)
        contact_data.set_portal_flag(contact.portal_flag)

        return contact_data

    def fetch_vendorcontact_list(self,vendor_id,user_id):
        contactlist = VendorContact.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())
        list_length = len(contactlist)
        logger.info(str(list_length))
        if list_length <= 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_VendorRelContact_ID)
            error_obj.set_description(ErrorDescription.INVALID_VendorRelContact_ID)
            return error_obj
        else:
            contact_list_data = NWisefinList()
            for contact in contactlist:
                contact_data = ContactResponse()
                contact_data.set_id(contact.id)

                contact_data.set_name(contact.name)
                contact_data.set_designation(contact.designation)
                contact_data.set_landline(contact.landline)
                contact_data.set_landline2(contact.landline2)
                contact_data.set_mobile(contact.mobile)
                contact_data.set_mobile2(contact.mobile2)
                contact_data.set_email(contact.email)
                contact_data.set_dob(contact.dob)
                contact_data.set_wedding_date(contact.wedding_date)
                contact_data.set_portal_flag(contact.portal_flag)
                contact_list_data.append(contact_data)
            return contact_list_data

    def fetch_vendorcontact(self,vendor_id,user_id):
        try:
            contact = VendorContact.objects.using(self._current_app_schema()).get(vendor_id=vendor_id, entity_id=self._entity_id())
            contact_data = ContactResponse()
            contact_data.set_id(contact.id)
            contact_data.set_name(contact.name)
            contact_data.set_designation(contact.designation)
            contact_data.set_landline(contact.landline)
            contact_data.set_landline2(contact.landline2)
            contact_data.set_mobile(contact.mobile)
            contact_data.set_mobile2(contact.mobile2)
            contact_data.set_email(contact.email)
            contact_data.set_dob(contact.dob)
            contact_data.set_wedding_date(contact.wedding_date)
            contact_data.set_portal_flag(contact.portal_flag)

            return contact_data
        except VendorContact.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_VendorRelContact_ID)
            error_obj.set_description(ErrorDescription.INVALID_VendorRelContact_ID)
            return error_obj

    def vow_fetch_vendorcontact(self,vendor_id,user_id):
        try:
            contact = VendorContact.objects.using(self._current_app_schema()).get(vendor_id=vendor_id, entity_id=self._entity_id(),
                                                                                  modify_status=-1)
            contact_data = ContactResponse()
            contact_data.set_id(contact.id)
            contact_data.set_name(contact.name)
            contact_data.set_designation(contact.designation)
            contact_data.set_landline(contact.landline)
            contact_data.set_landline2(contact.landline2)
            contact_data.set_mobile(contact.mobile)
            contact_data.set_mobile2(contact.mobile2)
            contact_data.set_email(contact.email)
            contact_data.set_dob(contact.dob)
            contact_data.set_wedding_date(contact.wedding_date)
            contact_data.set_portal_flag(contact.portal_flag)

            return contact_data
        except VendorContact.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_VendorRelContact_ID)
            error_obj.set_description(ErrorDescription.INVALID_VendorRelContact_ID)
            return error_obj

    def delete_vendorcontact(self,vendor_id, contact_id,user_id):
        contact = VendorContact.objects.using(self._current_app_schema()).filter(id=contact_id, entity_id=self._entity_id()).delete()
        req_status = RequestStatusUtil.ONBOARD
        self.audit_function(contact, vendor_id, user_id, req_status, contact_id, ModifyStatus.delete)
        if contact[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_VendorRelContact_ID)
            error_obj.set_description(ErrorDescription.INVALID_VendorRelContact_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def create_vendorcontact_modification(self,vendor_id, contact_obj,user_id):
        if not contact_obj.get_id() is None:
            vendor_service = VendorService(self._scope())
            # try:
            ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_CONTACT, contact_obj.get_id())
            if ref_flag == True:
                    contact = VendorContact.objects.using(self._current_app_schema()).filter(id=contact_obj.get_id(), entity_id=self._entity_id()).update(
                                                           name=contact_obj.get_name(),
                                                           designation=contact_obj.get_designation(),
                                                           landline=contact_obj.get_landline(),
                                                           landline2=contact_obj.get_landline2(),
                                                           mobile=contact_obj.get_mobile(),
                                                           mobile2=contact_obj.get_mobile2(),
                                                           email=contact_obj.get_email(),
                                                           dob=contact_obj.get_dob(),
                                                           wedding_date=contact_obj.get_wedding_date(),
                                                           vendor_id=vendor_id,
                                                           portal_flag=contact_obj.get_portal_flag()

                                                           )
                    contact=VendorContact.objects.using(self._current_app_schema()).get(id=contact_obj.get_id(), entity_id=self._entity_id())
            else:
                    contact = VendorContact.objects.using(self._current_app_schema()).create(
                                                              name=contact_obj.get_name(),
                                                              designation=contact_obj.get_designation(),
                                                              landline=contact_obj.get_landline(),
                                                              landline2=contact_obj.get_landline2(),
                                                              mobile=contact_obj.get_mobile(),
                                                              mobile2=contact_obj.get_mobile2(),
                                                              email=contact_obj.get_email(),
                                                              dob=contact_obj.get_dob(),
                                                              wedding_date=contact_obj.get_wedding_date(),
                                                              created_by=user_id,
                                                                modify_status=1,
                                                              vendor_id=vendor_id, entity_id=self._entity_id(),
                                                              portal_flag=contact_obj.get_portal_flag()

                                                              )
                    contact_update = VendorContact.objects.using(self._current_app_schema()).filter(id=contact_obj.get_id(), entity_id=self._entity_id()).update(modify_ref_id=contact.id,modified_by=user_id)
                    req_status = RequestStatusUtil.MODIFICATION
                    VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=contact_obj.get_id(),
                                                         ref_type=VendorRefType.VENDOR_CONTACT, mod_status=2,
                                                         modify_ref_id=contact.id, entity_id=self._entity_id())

        else:
            contact = VendorContact.objects.using(self._current_app_schema()).create(
                name=contact_obj.get_name(),
                designation=contact_obj.get_designation(),
                landline=contact_obj.get_landline(),
                landline2=contact_obj.get_landline2(),
                mobile=contact_obj.get_mobile(),
                mobile2=contact_obj.get_mobile2(),
                email=contact_obj.get_email(),
                dob=contact_obj.get_dob(),
                wedding_date=contact_obj.get_wedding_date(),
                created_by=user_id,
                modify_status=1,
                vendor_id=vendor_id, entity_id=self._entity_id(),
                portal_flag=contact_obj.get_portal_flag()

            )
            contact_update = VendorContact.objects.using(self._current_app_schema()).filter(id=contact.id, entity_id=self._entity_id()).update(modify_ref_id=contact.id,
                                                                                          modified_by=user_id)
            req_status = RequestStatusUtil.MODIFICATION
            # self.audit_function(contact, vendor_id, user_id, req_status, contact.id, ModifyStatus.create)
            # self.audit_function(contact_update, vendor_id, user_id, req_status, contact.id, ModifyStatus.update)

            VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=contact.id,
                                                 ref_type=VendorRefType.VENDOR_CONTACT, mod_status=1,
                                                 modify_ref_id=contact.id, entity_id=self._entity_id())

        contact_data = ContactResponse()
        contact_data.set_id(contact.id)

        contact_data.set_name(contact.name)
        contact_data.set_designation(contact.designation)
        contact_data.set_landline(contact.landline)
        contact_data.set_landline2(contact.landline2)
        contact_data.set_mobile(contact.mobile)
        contact_data.set_mobile2(contact.mobile2)
        contact_data.set_email(contact.email)
        contact_data.set_dob(contact.dob)
        contact_data.set_wedding_date(contact.wedding_date)
        contact_data.set_portal_flag(contact.portal_flag)

        return contact_data

    def modification_action_vendorcontact(self, mod_status, old_id, new_id,vendor_id,user_id):
        # emp = Employee.objects.get(user_id=user_id)
        # employee_id = emp.id
        if mod_status == 2:
            contact_obj = self.approve_vendorcontact_modification(new_id,user_id)
            if contact_obj.get_dob()==str(None):
                dob_date=None
            else:
                dob_date= contact_obj.get_dob()

            if contact_obj.get_wedding_date() == str(None):
                wed_date = None
            else:
                wed_date = contact_obj.get_wedding_date()
            contact = VendorContact.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(
                                                                                   vendor_id=vendor_id,
                                                                                   name=contact_obj.get_name(),
                                                                                   designation=contact_obj.get_designation(),
                                                                                   landline=contact_obj.get_landline(),
                                                                                   landline2=contact_obj.get_landline2(),
                                                                                   mobile=contact_obj.get_mobile(),
                                                                                   mobile2=contact_obj.get_mobile2(),
                                                                                   email=contact_obj.get_email(),
                                                                                   dob=dob_date,
                                                                                   wedding_date=wed_date,
                                                                                   modify_status=-1,modified_by =-1,
                                                                                   modify_ref_id=-1,
                                                                                   portal_flag=contact_obj.get_portal_flag()
                                                                                   )


            req_status = RequestStatusUtil.MODIFICATION
            self.audit_function(contact, vendor_id, user_id, req_status, old_id, ModifyStatus.update)
            # self.audit_function(contact_del, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)
        if mod_status==1:
            con_obj=VendorContact.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).update(modify_status=-1,modified_by =-1,modify_ref_id=-1)

        if mod_status==0:
            con_obj = VendorContact.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).delete()
        return
    def fetch_vendorcontact_modification(self,vendor_id,user_id):
        try:
            contact = VendorContact.objects.using(self._current_app_schema()).get(Q(vendor_id=vendor_id) & Q(modify_status=1)&Q(entity_id=self._entity_id()))
            contact_data = ContactResponse()
            contact_data.set_id(contact.id)

            contact_data.set_name(contact.name)
            contact_data.set_designation(contact.designation)
            contact_data.set_landline(contact.landline)
            contact_data.set_landline2(contact.landline2)
            contact_data.set_mobile(contact.mobile)
            contact_data.set_mobile2(contact.mobile2)
            contact_data.set_email(contact.email)
            contact_data.set_dob(contact.dob)
            contact_data.set_wedding_date(contact.wedding_date)
            contact_data.set_portal_flag(contact.portal_flag)

            return contact_data
        except VendorContact.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_VendorRelContact_ID)
            error_obj.set_description(ErrorDescription.INVALID_VendorRelContact_ID)
            return error_obj

    def approve_vendorcontact_modification(self,contact_id,user_id):
        try:
            contact = VendorContact.objects.using(self._current_app_schema()).get(Q(id=contact_id) & Q(modify_status=1)&Q(entity_id=self._entity_id()))
            contact_data = ContactResponse()
            contact_data.set_id(contact.id)

            contact_data.set_name(contact.name)
            contact_data.set_designation(contact.designation)
            contact_data.set_landline(contact.landline)
            contact_data.set_landline2(contact.landline2)
            contact_data.set_mobile(contact.mobile)
            contact_data.set_mobile2(contact.mobile2)
            contact_data.set_email(contact.email)
            contact_data.set_dob(contact.dob)
            contact_data.set_wedding_date(contact.wedding_date)
            contact_data.set_portal_flag(contact.portal_flag)

            return contact_data
        except VendorContact.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_VendorRelContact_ID)
            error_obj.set_description(ErrorDescription.INVALID_VendorRelContact_ID)
            return error_obj


    def modification_reject_vendorcontact(self, mod_status, old_id, new_id, user_id,vendor_id):
        if mod_status == ModifyStatus.update:

            contact_del=VendorContact.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()
            vendor_contact =VendorContact.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(modify_ref_id=-1)

            req_status = RequestStatusUtil.MODIFICATION
            self.audit_function(contact_del, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)
            self.audit_function(vendor_contact, vendor_id, user_id, req_status, old_id, ModifyStatus.update)

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj

    def audit_function(self, vendor_contact, vendor_id, user_id, req_status, id, action):
        if action == ModifyStatus.delete:
            data = None
        elif action == ModifyStatus.update:
            data = vendor_contact
        else:
            data = vendor_contact.__dict__
            del data['_state']
        audit_service = VendorAuditService(self._scope())
        audit_obj = VendorAuditResponse()
        audit_obj.set_refid(vendor_id)
        audit_obj.set_reftype(VendorRefType.VENDOR)
        audit_obj.set_userid(user_id)
        audit_obj.set_reqstatus(req_status)
        audit_obj.set_relrefid(id)
        audit_obj.set_relreftype(VendorRefType.VENDOR_CONTACT)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_vendoraudit(audit_obj)
        return
