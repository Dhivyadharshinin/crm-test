import traceback

from django.db import IntegrityError
from masterservice.data.response.contactresponse import ContactResponse
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from masterservice.models import Contact
from django.utils import timezone
import json

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class ContactService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_contact(self, contact_obj, user_id):
        if not contact_obj.get_id() is None:
            try:
                logger.error('CONTACT: Contact Update Started')
                contact = Contact.objects.using(self._current_app_schema()).filter(id=contact_obj.get_id(),
                                                                                   entity_id=self._entity_id()).update(
                    type_id=contact_obj.get_type_id(),
                    name=contact_obj.get_name(),
                    designation_id=contact_obj.get_designation_id(),
                    landline=contact_obj.get_landline(),
                    landline2=contact_obj.get_landline2(),
                    mobile=contact_obj.get_mobile(),
                    mobile2=contact_obj.get_mobile2(),
                    email=contact_obj.get_email(),
                    # dob=contact_obj.get_dob(),
                    # wedding_date=contact_obj.get_wedding_date(),
                    updated_by=user_id,
                    updated_date=timezone.now())

                contact = Contact.objects.using(self._current_app_schema()).get(id=contact_obj.get_id(),
                                                                                entity_id=self._entity_id())
                logger.error('CONTACT: Contact Update Success' + str(contact))
            except IntegrityError as error:
                logger.error('ERROR_Contact_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Contact.DoesNotExist:
                logger.error('ERROR_Contact_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_Contact_ID)
                error_obj.set_description(ErrorDescription.INVALID_Contact_ID)
                return error_obj
            except:
                logger.error('ERROR_Contact_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('CONTACT: Contact Creation Started')
                contact = Contact.objects.using(self._current_app_schema()).create(type_id=contact_obj.get_type_id(),
                                                                                   name=contact_obj.get_name(),
                                                                                   designation_id=contact_obj.get_designation_id(),
                                                                                   landline=contact_obj.get_landline(),
                                                                                   landline2=contact_obj.get_landline2(),
                                                                                   mobile=contact_obj.get_mobile(),
                                                                                   mobile2=contact_obj.get_mobile2(),
                                                                                   email=contact_obj.get_email(),
                                                                                   # dob=contact_obj.get_dob(),
                                                                                   # wedding_date=contact_obj.get_wedding_date(),
                                                                                   created_by=user_id,
                                                                                   entity_id=self._entity_id()
                                                                                   )
                logger.error('CONTACT: Contact Creation Success' + str(contact))
            except IntegrityError as error:
                logger.error('ERROR_Contact_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_Contact_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        return contact.id

    def fetchcontact_list(self):
        contactlist = Contact.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())
        list_length = len(contactlist)
        if list_length <= 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_Contact_ID)
            error_obj.set_description(ErrorDescription.INVALID_Contact_ID)
            return error_obj
        else:
            contact_list_data = NWisefinList()
            for contact in contactlist:
                contact_data = ContactResponse()
                contact_data.set_id(contact.id)
                contact_data.set_type_id(contact.type_id)
                contact_data.set_name(contact.name)
                contact_data.set_designation_id(contact.designation_id)
                contact_data.set_landline(contact.landline)
                contact_data.set_landline2(contact.landline2)
                contact_data.set_mobile(contact.mobile)
                contact_data.set_mobile2(contact.mobile2)
                contact_data.set_email(contact.email)
                # contact_data.set_dob(contact.dob)
                # contact_data.set_wedding_date(contact.wedding_date)
                contact_list_data.append(contact_data)
            return contact_list_data

    def fetchcontact(self, contact_id):
        try:
            contact = Contact.objects.using(self._current_app_schema()).get(id=contact_id, entity_id=self._entity_id())
            contact_data = ContactResponse()
            contact_data.set_id(contact.id)
            contact_data.set_type_id(contact.type_id)
            contact_data.set_name(contact.name)
            contact_data.set_designation_id(contact.designation_id)
            contact_data.set_landline(contact.landline)
            contact_data.set_landline2(contact.landline2)
            contact_data.set_mobile(contact.mobile)
            contact_data.set_mobile2(contact.mobile2)
            contact_data.set_email(contact.email)
            # contact_data.set_dob(contact.dob)
            # contact_data.set_wedding_date(contact.wedding_date)

            return contact_data
        except Contact.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_Contact_ID)
            error_obj.set_description(ErrorDescription.INVALID_Contact_ID)
            return error_obj

    def deletecontact(self, contact_id):
        contact = Contact.objects.using(self._current_app_schema()).filter(id=contact_id,
                                                                           entity_id=self._entity_id()).delete()
        if contact[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_Contact_ID)
            error_obj.set_description(ErrorDescription.INVALID_Contact_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
