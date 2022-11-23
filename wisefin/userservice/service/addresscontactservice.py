import traceback

from django.db import IntegrityError
from nwisefin.settings import logger
from userservice.data.response.addresscontactresponse import AddressResponse,ContactResponse
from userservice.models import EmployeeAddress ,EmployeeContact
from django.utils import timezone
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
import json


class AddressService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.USER_SERVICE)

    def create_employeeaddress(self, address_obj,user_id):
        if not address_obj.get_id() is None:
            try:
                logger.error('EMPLOYEEADDRESS: EmployeeAddress Update Started')
                address = EmployeeAddress.objects.using(self._current_app_schema()).filter(id=address_obj.get_id()).update(
                                                                                        line1=address_obj.get_line1(),
                                                                                          line2=address_obj.get_line2(),
                                                                                          line3=address_obj.get_line3(),
                                                                                          pincode_id=address_obj.get_pincode_id(),
                                                                                          city_id=address_obj.get_city_id(),
                                                                                          district_id=address_obj.get_district_id(),
                                                                                          state_id=address_obj.get_state_id(),
                                                                                          updated_by=user_id,
                                                                                          updated_date=timezone.now())

                address = EmployeeAddress.objects.using(self._current_app_schema()).get(id=address_obj.get_id())
                logger.error('EMPLOYEEADDRESS: EmployeeAddress Update Success' + str(address))
            except IntegrityError as error:
                logger.info('ERROR_EmployeeAddress_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except EmployeeAddress.DoesNotExist:
                logger.info('ERROR_EmployeeAddress_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_Address_ID)
                error_obj.set_description(ErrorDescription.INVALID_Address_ID)
                return error_obj
            except:
                logger.info('ERROR_EmployeeAddress_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('EMPLOYEEADDRESS: EmployeeAddress Creation Started')
                address = EmployeeAddress.objects.using(self._current_app_schema()).create(line1=address_obj.get_line1(),
                                                          line2=address_obj.get_line2(), line3=address_obj.get_line3(),
                                                          pincode_id=address_obj.get_pincode_id(),
                                                          city_id=address_obj.get_city_id(),
                                                          district_id=address_obj.get_district_id(),
                                                          state_id=address_obj.get_state_id(),
                                                          created_by=user_id
                                                          )
                logger.error('EMPLOYEEADDRESS: EmployeeAddress Creation Success' + str(address))
            except IntegrityError as error:
                logger.error('ERROR_EmployeeAddress_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_EmployeeAddress_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        return address.id

    def fetch_employeeaddress_list(self):
        addresslist = EmployeeAddress.objects.using(self._current_app_schema()).all()
        list_length = len(addresslist)
        print(list_length)
        if list_length <= 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_Address_ID)
            error_obj.set_description(ErrorDescription.INVALID_Address_ID)
            return error_obj
        else:
            add_list_data = NWisefinList()
            for address in addresslist:
                add_data = AddressResponse()
                add_data.set_id(address.id)
                add_data.set_line1(address.line1)
                add_data.set_line2(address.line2)
                add_data.set_line3(address.line3)
                add_data.set_pincode_id(address.pincode_id)
                add_data.set_city_id(address.city_id)
                add_data.set_district_id(address.district_id)
                add_data.set_state_id(address.state_id)

                add_list_data.append(add_data)
            return add_list_data

    def fetch_employeeaddress(self,address_id):
        try:
            address = EmployeeAddress.objects.using(self._current_app_schema()).get(id=address_id)
            add_data = AddressResponse()
            add_data.set_id(address.id)
            add_data.set_line1(address.line1)
            add_data.set_line2(address.line2)
            add_data.set_line3(address.line3)
            add_data.set_pincode_id(address.pincode_id)
            add_data.set_city_id(address.city_id)
            add_data.set_district_id(address.district_id)
            add_data.set_state_id(address.state_id)

            return add_data
        except EmployeeAddress.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_Address_ID)
            error_obj.set_description(ErrorDescription.INVALID_Address_ID)
            return error_obj

    def delete_employeeaddress(self,address_id):
        address = EmployeeAddress.objects.using(self._current_app_schema()).filter(id=address_id).delete()
        if address[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_Address_ID)
            error_obj.set_description(ErrorDescription.INVALID_Address_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

class ContactService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.USER_SERVICE)

    def create_employeecontact(self,contact_obj,user_id):
        if not contact_obj.get_id() is None:
            try:
                logger.error('EMPLOYEECONTACT: EmployeeContact Update Started')
                contact = EmployeeContact.objects.using(self._current_app_schema()).filter(id=contact_obj.get_id()).update(type_id=contact_obj.get_type_id(),
                                                                                          name=contact_obj.get_name(),
                                                                                          designation_id=contact_obj.get_designation_id(),
                                                                                          landline=contact_obj.get_landline(),
                                                                                          landline2=contact_obj.get_landline2(),
                                                                                          mobile=contact_obj.get_mobile(),
                                                                                          mobile2=contact_obj.get_mobile2(),
                                                                                          email=contact_obj.get_email(),
                                                                                          dob=contact_obj.get_dob(),
                                                                                          wedding_date=contact_obj.get_wedding_date(),
                                                                                          updated_by=user_id,
                                                                                          updated_date=timezone.now())

                contact = EmployeeContact.objects.using(self._current_app_schema()).get(id=contact_obj.get_id())
                logger.error('EMPLOYEECONTACT: EmployeeContact Update Success' + str(contact))
            except IntegrityError as error:
                logger.info('ERROR_EmployeeContact_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except EmployeeContact.DoesNotExist:
                logger.info('ERROR_EmployeeContact_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_Contact_ID)
                error_obj.set_description(ErrorDescription.INVALID_Contact_ID)
                return error_obj
            except:
                logger.info('ERROR_EmployeeContact_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('EMPLOYEECONTACT: EmployeeContact Creation Started')
                contact = EmployeeContact.objects.using(self._current_app_schema()).create(type_id=contact_obj.get_type_id(),
                                                          name=contact_obj.get_name(),
                                                          designation_id=contact_obj.get_designation_id(),
                                                          landline=contact_obj.get_landline(),
                                                          landline2=contact_obj.get_landline2(),
                                                          mobile=contact_obj.get_mobile(),
                                                          mobile2=contact_obj.get_mobile2(),
                                                          email=contact_obj.get_email(),
                                                          dob=contact_obj.get_dob(),
                                                          wedding_date=contact_obj.get_wedding_date(),
                                                          created_by=user_id,
                                                          )
                logger.error('EMPLOYEECONTACT: EmployeeContact Creation Success' + str(contact))
            except IntegrityError as error:
                logger.error('ERROR_EmployeeContact_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_EmployeeContact_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        return contact.id

    def fetch_employeecontact_list(self):
        contactlist = EmployeeContact.objects.using(self._current_app_schema()).all()
        list_length = len(contactlist)
        print(list_length)
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
                contact_data.set_dob(contact.dob)
                contact_data.set_wedding_date(contact.wedding_date)
                contact_list_data.append(contact_data)
            return contact_list_data

    def fetch_employeecontact(self,contact_id):
        try:
            contact = EmployeeContact.objects.using(self._current_app_schema()).get(id=contact_id)
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
            contact_data.set_dob(contact.dob)
            contact_data.set_wedding_date(contact.wedding_date)

            return contact_data
        except EmployeeContact.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_Contact_ID)
            error_obj.set_description(ErrorDescription.INVALID_Contact_ID)
            return error_obj

    def delete_employeecontact(self,contact_id):
        contact = EmployeeContact.objects.using(self._current_app_schema()).filter(id=contact_id).delete()
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
