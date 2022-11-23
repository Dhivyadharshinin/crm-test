import django
from django.db import IntegrityError
from nwisefin.settings import logger
from userservice.models import Employee
from vendorservice.models import VendorRelAddress , VendorRelContact , VendorProfile , VendorModificationRel , \
    SupplierBranch
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from vendorservice.data.response.supplierresponse import AddressResponse , ContactResponse
from django.utils import timezone
from vendorservice.util.vendorutil import VendorRefType , ModifyStatus , RequestStatusUtil
from vendorservice.service.vendorauditservice import VendorAuditService , VendorAuditResponse
from vendorservice.service.vendorservice import VendorService
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
import json
from masterservice.service.cityservice import CityService
from masterservice.service.stateservice import StateService
from masterservice.service.districtservice import DistrictService
from masterservice.service.pincodeservice import PincodeService


class AddressService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def create_address ( self , address_obj , user_id , vendor_id ) :

        req_status = RequestStatusUtil.ONBOARD
        if not address_obj.get_id ( ) is None :
            # try:
            address_update = VendorRelAddress.objects.using(self._current_app_schema()).filter ( id=address_obj.get_id(), entity_id=self._entity_id()).update (
                line1=address_obj.get_line1 ( ) ,
                line2=address_obj.get_line2 ( ) , line3=address_obj.get_line3 ( ) ,
                pincode_id=address_obj.get_pincode_id ( ) ,
                city_id=address_obj.get_city_id () ,
                district_id=address_obj.get_district_id ( ), state_id=address_obj.get_state_id ( ) ,
                updated_by=user_id , updated_date=timezone.now ( ),portal_flag=address_obj.get_portal_flag())

            address = VendorRelAddress.objects.using(self._current_app_schema()).get ( id=address_obj.get_id ( ) )
            address_auditdata = {'id' : address_obj.get_id ( ) , 'line1' : address_obj.get_line1 ( ) ,
                                 'line2' : address_obj.get_line2 ( ) , 'line3' : address_obj.get_line3 ( ) ,
                                 'pincode_id' : address_obj.get_pincode_id ( ) ,
                                 'city_id' : address_obj.get_city_id ( ) ,
                                 'district_id' : address_obj.get_district_id ( ) ,
                                 'state_id' : address_obj.get_state_id ( ) ,
                                 'updated_by' : user_id , 'updated_date' : timezone.now ( )}
            self.audit_function ( address_auditdata , vendor_id , user_id , req_status , address.id ,
                                  ModifyStatus.update )
        # except IntegrityError as error:
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.INVALID_DATA)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
        #     return error_obj
        # except VendorRelAddress.DoesNotExist:
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.INVALID_VendorRelAddress_ID)
        #     error_obj.set_description(ErrorDescription.INVALID_VendorRelAddress_ID)
        #     return error_obj
        # except:
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
        #     return error_obj
        else :
            # try:
            address = VendorRelAddress.objects.using(self._current_app_schema()).create ( line1=address_obj.get_line1 ( ) ,
                                                        line2=address_obj.get_line2 ( ) ,
                                                        line3=address_obj.get_line3 ( ) ,
                                                        pincode_id=address_obj.get_pincode_id ( ) ,
                                                        city_id=address_obj.get_city_id ( ) ,
                                                        district_id=address_obj.get_district_id ( ) ,
                                                        state_id=address_obj.get_state_id ( ) ,
                                                        created_by=user_id, entity_id=self._entity_id(), portal_flag=address_obj.get_portal_flag())
            self.audit_function ( address , vendor_id , user_id , req_status , address.id , ModifyStatus.create )
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

        add_data = AddressResponse ( )
        add_data.set_id ( address.id )
        add_data.set_line1 ( address.line1 )
        add_data.set_line2 ( address.line2 )
        add_data.set_line3 ( address.line3 )
        add_data.set_pincode_id ( address.pincode_id )
        add_data.set_city_id ( address.city_id )
        add_data.set_district_id ( address.district_id )
        add_data.set_state_id ( address.state_id )
        add_data.set_portal_flag(address.portal_flag)

        return add_data.id

    def fetch_address_list ( self , user_id ) :
        addresslist = VendorRelAddress.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())
        list_length = len ( addresslist )
        logger.info (str(list_length))
        if list_length <= 0 :
            error_obj = NWisefinError ( )
            error_obj.set_code ( ErrorMessage.INVALID_VendorRelAddress_ID )
            error_obj.set_description ( ErrorDescription.INVALID_VendorRelAddress_ID )
            return error_obj
        else :
            add_list_data = NWisefinList ( )
            for address in addresslist :
                add_data = AddressResponse ( )
                add_data.set_id ( address.id )
                add_data.set_line1 ( address.line1 )
                add_data.set_line2 ( address.line2 )
                add_data.set_line3 ( address.line3 )
                add_data.set_pincode_id ( address.pincode_id )
                add_data.set_city_id ( address.city_id )
                add_data.set_district_id ( address.district_id )
                add_data.set_state_id ( address.state_id )
                add_data.set_portal_flag(address.portal_flag)

                add_list_data.append ( add_data )
            return add_list_data

    def fetch_address ( self , address_id , user_id ) :
        try :
            address = VendorRelAddress.objects.using(self._current_app_schema()).get ( id=address_id, entity_id=self._entity_id())
            add_data = AddressResponse ( )
            add_data.set_id ( address.id )
            add_data.set_line1 ( address.line1 )
            add_data.set_line2 ( address.line2 )
            add_data.set_line3 ( address.line3 )
            add_data.set_pincode_id ( address.pincode_id )
            add_data.set_city_id ( address.city_id )
            add_data.set_district_id ( address.district_id )
            add_data.set_state_id ( address.state_id )
            add_data.set_portal_flag(address.portal_flag)

            return add_data
        except VendorRelAddress.DoesNotExist :
            error_obj = NWisefinError ( )
            error_obj.set_code ( ErrorMessage.INVALID_VendorRelAddress_ID )
            error_obj.set_description ( ErrorDescription.INVALID_VendorRelAddress_ID )
            return error_obj

    def delete_address ( self , address_id , vendor_id , user_id ) :

        address = VendorRelAddress.objects.using(self._current_app_schema()).filter ( id=address_id, entity_id=self._entity_id()).delete ( )

        req_status = RequestStatusUtil.ONBOARD
        self.audit_function ( address , vendor_id , user_id , req_status , address_id , ModifyStatus.delete )
        if address [ 0 ] == 0 :
            error_obj = NWisefinError ( )
            error_obj.set_code ( ErrorMessage.INVALID_VendorRelAddress_ID )
            error_obj.set_description ( ErrorDescription.INVALID_VendorRelAddress_ID )
            return error_obj
        else :
            success_obj = NWisefinSuccess ( )
            success_obj.set_status ( SuccessStatus.SUCCESS )
            success_obj.set_message ( SuccessMessage.DELETE_MESSAGE )
            return success_obj

    def fetch_sup_address ( self , address_id ) :
        try :
            address = VendorRelAddress.objects.using(self._current_app_schema()).get ( id=address_id, entity_id=self._entity_id())
            add_data = AddressResponse ( )
            add_data.set_id ( address.id )
            add_data.set_line1 ( address.line1 )
            add_data.set_line2 ( address.line2 )
            add_data.set_line3 ( address.line3 )
            add_data.set_pincode_id ( address.pincode_id )
            add_data.set_city_id ( address.city_id )
            add_data.set_district_id ( address.district_id )
            add_data.set_state_id ( address.state_id )
            add_data.set_portal_flag(address.portal_flag)
            return add_data
        except VendorRelAddress.DoesNotExist :
            error_obj = NWisefinError ( )
            error_obj.set_code ( ErrorMessage.INVALID_VendorRelAddress_ID )
            error_obj.set_description ( ErrorDescription.INVALID_VendorRelAddress_ID )
            return error_obj

    # modification request address
    def modification_create_address ( self , address_obj , user_id , vendor_id ) :

        req_status = RequestStatusUtil.MODIFICATION
        vendor_service = VendorService (self._scope())
        if not address_obj.get_id ( ) is None :
            # try:
            ref_flag = vendor_service.checkmodify_rel ( VendorRefType.VENDOR_REL_ADDRESS , address_obj.get_id ( ) )
            if ref_flag == True :
                address = VendorRelAddress.objects.using(self._current_app_schema()).filter ( id=address_obj.get_id(), entity_id=self._entity_id()).update (
                    line1=address_obj.get_line1 ( ) , line2=address_obj.get_line2 ( ) ,
                    line3=address_obj.get_line3 ( ) ,
                    pincode_id=address_obj.get_pincode_id ( ) ,
                    city_id=address_obj.get_city_id ( ) ,
                    district_id=address_obj.get_district_id ( ) ,
                    state_id=address_obj.get_state_id ( ),
                    portal_flag=address_obj.get_portal_flag()
                    )
                address = VendorRelAddress.objects.using(self._current_app_schema()).get ( id=address_obj.get_id(), entity_id=self._entity_id())

            else :
                address = VendorRelAddress.objects.using(self._current_app_schema()).create ( line1=address_obj.get_line1 ( ) ,
                                                            line2=address_obj.get_line2 ( ) ,
                                                            line3=address_obj.get_line3 ( ) ,
                                                            pincode_id=address_obj.get_pincode_id ( ) ,
                                                            city_id=address_obj.get_city_id ( ) ,
                                                            district_id=address_obj.get_district_id ( ) ,
                                                            state_id=address_obj.get_state_id ( ) , created_by=user_id ,
                                                            modify_status=ModifyStatus.create , modified_by=user_id, entity_id=self._entity_id(),
                                                            portal_flag=address_obj.get_portal_flag())

                VendorModificationRel.objects.using(self._current_app_schema()).create ( vendor_id=vendor_id , ref_id=address_obj.get_id ( ) ,
                                                       ref_type=VendorRefType.VENDOR_REL_ADDRESS ,
                                                       mod_status=ModifyStatus.update ,
                                                       modify_ref_id=address.id, entity_id=self._entity_id())

            address_update_id = address_obj.get_id ( )

            # self.audit_function(address, vendor_id, user_id, req_status, address.id, ModifyStatus.create)
            # self.audit_function(addressupdate_auditdata, vendor_id, user_id, req_status, address_update_id,
            #                     ModifyStatus.update)

        # except IntegrityError as error:
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.INVALID_DATA)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
        #     return error_obj
        #
        # except VendorRelAddress.DoesNotExist:
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.INVALID_VendorRelAddress_ID)
        #     error_obj.set_description(ErrorDescription.INVALID_VendorRelAddress_ID)
        #     return error_obj
        #
        # except:
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
        #     return error_obj

        else :
            # try:
            address = VendorRelAddress.objects.using(self._current_app_schema()).create ( line1=address_obj.get_line1 ( ) ,
                                                        line2=address_obj.get_line2 ( ) ,
                                                        line3=address_obj.get_line3 ( ) ,
                                                        pincode_id=address_obj.get_pincode_id ( ) ,
                                                        city_id=address_obj.get_city_id ( ) ,
                                                        district_id=address_obj.get_district_id ( ) ,
                                                        state_id=address_obj.get_state_id ( ) , created_by=user_id ,
                                                        modify_status=ModifyStatus.create , modified_by=user_id, entity_id=self._entity_id(),
                                                        portal_flag=address_obj.get_portal_flag())

            address.modify_ref_id = address.id
            address.save ( )

            VendorModificationRel.objects.using(self._current_app_schema()).create ( vendor_id=vendor_id , ref_id=address.id ,
                                                   ref_type=VendorRefType.VENDOR_REL_ADDRESS ,
                                                   mod_status=ModifyStatus.create ,
                                                   modify_ref_id=address.id, entity_id=self._entity_id())

            self.audit_function ( address , vendor_id , user_id , req_status , address.id , ModifyStatus.create )
        # except IntegrityError as error:
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.INVALID_DATA)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
        #     return error_obj
        #
        # except VendorRelAddress.DoesNotExist:
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.INVALID_VendorRelAddress_ID)
        #     error_obj.set_description(ErrorDescription.INVALID_VendorRelAddress_ID)
        #     return error_obj
        #
        # except:
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
        #     return error_obj

        return address.id

    def modification_delete_address ( self , address_id , vendor_id , user_id ) :
        req_status = RequestStatusUtil.MODIFICATION
        try :
            address_update = VendorRelAddress.objects.using(self._current_app_schema()).filter ( id=address_id, entity_id=self._entity_id()).update (
                modify_ref_id=address_id , modify_status=ModifyStatus.delete )

            VendorModificationRel.objects.using(self._current_app_schema()).filter ( modify_ref_id=address_id ,
                                                   ref_type=VendorRefType.VENDOR_REL_ADDRESS, entity_id=self._entity_id()).update (
                mod_status=ModifyStatus.delete )

            # self.audit_function(address_update, vendor_id, user_id, req_status, address_id, ModifyStatus.update)

            success_obj = NWisefinSuccess ( )
            success_obj.set_status ( SuccessStatus.SUCCESS )
            success_obj.set_message ( SuccessMessage.DELETE_MESSAGE )
            return success_obj
        except :
            error_obj = NWisefinError ( )
            error_obj.set_code ( ErrorMessage.UNEXPECTED_ERROR )
            error_obj.set_description ( ErrorDescription.UNEXPECTED_ERROR )
            return error_obj

    def modification_action_address ( self , mod_status , old_id , new_id , vendor_id , user_id ) :

        req_status = RequestStatusUtil.MODIFICATION
        if mod_status == ModifyStatus.update or ModifyStatus.active_in :
            address_obj = self.fetch_address ( new_id , user_id )

            address_update = VendorRelAddress.objects.using(self._current_app_schema()).filter ( id=old_id, entity_id=self._entity_id()).update ( line1=address_obj.get_line1 ( ) ,
                                                                                    line2=address_obj.get_line2 ( ) ,
                                                                                    line3=address_obj.get_line3 ( ) ,
                                                                                    pincode_id=address_obj.get_pincode_id ( ) ,
                                                                                    city_id=address_obj.get_city_id ( ) ,
                                                                                    district_id=address_obj.get_district_id ( ) ,
                                                                                    state_id=address_obj.get_state_id ( ) ,
                                                                                    modify_status=-1 ,
                                                                                    modify_ref_id=-1 , modified_by=-1,
                                                                                    portal_flag=address_obj.get_portal_flag())

            self.audit_function ( address_update , vendor_id , user_id , req_status , old_id , ModifyStatus.update )
            # self.audit_function(address, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)

        elif mod_status == ModifyStatus.create :
            address_update = VendorRelAddress.objects.using(self._current_app_schema()).filter ( id=new_id, entity_id=self._entity_id()).update ( modify_status=-1 ,
                                                                                    modify_ref_id=-1 , modified_by=-1 )
            self.audit_function ( address_update , vendor_id , user_id , req_status , new_id , ModifyStatus.update )
        else :
            address = VendorRelAddress.objects.using(self._current_app_schema()).filter ( id=old_id, entity_id=self._entity_id()).delete ( )
            self.audit_function ( address , vendor_id , user_id , req_status , old_id , ModifyStatus.delete )
        return

    def modification_reject_address ( self , mod_status , old_id , new_id , vendor_id , user_id ) :
        req_status = RequestStatusUtil.MODIFICATION
        if mod_status == ModifyStatus.update :
            address = VendorRelAddress.objects.using(self._current_app_schema()).filter ( id=new_id, entity_id=self._entity_id()).delete ( )
            address_update = VendorRelAddress.objects.using(self._current_app_schema()).filter ( id=old_id ).update ( modify_ref_id=-1 )

            self.audit_function ( address , vendor_id , user_id , req_status , new_id , ModifyStatus.delete )
            self.audit_function ( address_update , vendor_id , user_id , req_status , old_id , ModifyStatus.update )

        elif mod_status == ModifyStatus.create :
            address = VendorRelAddress.objects.using(self._current_app_schema()).filter ( id=new_id, entity_id=self._entity_id()).delete ( )
            self.audit_function ( address , vendor_id , user_id , req_status , new_id , ModifyStatus.delete )

        else :
            address_update = VendorRelAddress.objects.using(self._current_app_schema()).filter ( id=old_id, entity_id=self._entity_id()).update ( modify_ref_id=-1 )
            self.audit_function ( address_update , vendor_id , user_id , req_status , old_id , ModifyStatus.update )
        return

    def audit_function ( self , address , vendor_id , user_id , req_status , id , action ) :

        if action == ModifyStatus.delete :
            data = None
        elif action == ModifyStatus.update :
            data = address
        else :
            data = address.__dict__
            del data [ '_state' ]
        audit_service = VendorAuditService (self._scope())
        audit_obj = VendorAuditResponse ( )
        audit_obj.set_refid ( vendor_id )
        audit_obj.set_reftype ( VendorRefType.VENDOR )
        audit_obj.set_userid ( user_id )
        audit_obj.set_reqstatus ( req_status )
        audit_obj.set_relrefid ( id )
        audit_obj.set_relreftype ( VendorRefType.VENDOR_REL_ADDRESS )
        audit_obj.set_action ( action )
        audit_obj.set_data ( data )
        audit_service.create_vendoraudit ( audit_obj )
        return

    def fetch_address_data ( self , address_id , user_id ) :
        state_service = StateService(self._scope())
        city_service = CityService(self._scope())
        district_service = DistrictService(self._scope())
        pincode_service = PincodeService(self._scope())
        try :
            address = VendorRelAddress.objects.using(self._current_app_schema()).get ( id=address_id, entity_id=self._entity_id())
            add_data = AddressResponse ( )
            add_data.set_id ( address.id )
            add_data.set_line1 ( address.line1 )
            add_data.set_line2 ( address.line2 )
            add_data.set_line3 ( address.line3 )
            pincode = pincode_service.fetch_pincode(address.pincode_id, user_id)
            add_data.set_pincode_id ( pincode )
            city = city_service.fetch_city(address.city_id, user_id)
            add_data.set_city_id ( city )
            district = district_service.fetchdistrict(address.district_id)
            add_data.set_district_id ( district )
            state = state_service.fetchstate(address.state_id)
            add_data.set_state_id ( state )
            add_data.set_portal_flag(address.portal_flag)
            return add_data
        except VendorRelAddress.DoesNotExist :
            error_obj = NWisefinError ( )
            error_obj.set_code ( ErrorMessage.INVALID_VendorRelAddress_ID )
            error_obj.set_description ( ErrorDescription.INVALID_VendorRelAddress_ID )
            return error_obj


class ContactService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def create_contact ( self , contact_obj , user_id , vendor_id ) :
        req_status = RequestStatusUtil.ONBOARD
        if not contact_obj.get_id ( ) is None :
            # try:
            contact_update = VendorRelContact.objects.using(self._current_app_schema()).filter ( id=contact_obj.get_id(), entity_id=self._entity_id()).update (
                name=contact_obj.get_name ( ) , designation=contact_obj.get_designation( ) ,
                landline=contact_obj.get_landline ( ) , landline2=contact_obj.get_landline2 ( ) ,
                mobile=contact_obj.get_mobile ( ) ,
                mobile2=contact_obj.get_mobile2 ( ) , email=contact_obj.get_email ( ) ,
                dob=contact_obj.get_dob ( ) , wedding_date=contact_obj.get_wedding_date ( ) ,
                updated_by=user_id , updated_date=timezone.now ( ),portal_flag=contact_obj.get_portal_flag())

            contact_auditdata = {'id' : contact_obj.get_id ( ) ,
                                 'name' : contact_obj.get_name ( ) ,
                                 'designation' : contact_obj.get_designation( ) ,
                                 'landline' : contact_obj.get_landline ( ) ,
                                 'landline2' : contact_obj.get_landline2 ( ) , 'mobile' : contact_obj.get_mobile ( ) ,
                                 'mobile2' : contact_obj.get_mobile2 ( ) , 'email' : contact_obj.get_email ( ) ,
                                 'dob' : contact_obj.get_dob ( ) , 'wedding_date' : contact_obj.get_wedding_date ( ) ,
                                 'updated_by' : user_id , 'updated_date' : timezone.now ( )}
            contact = VendorRelContact.objects.using(self._current_app_schema()).get ( id=contact_obj.get_id(), entity_id=self._entity_id())
            self.audit_function ( contact_auditdata , vendor_id , user_id , req_status , contact.id ,
                                  ModifyStatus.update )
        # except IntegrityError as error:
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.INVALID_DATA)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
        #     return error_obj
        # except VendorRelContact.DoesNotExist:
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.INVALID_VendorRelContact_ID)
        #     error_obj.set_description(ErrorDescription.INVALID_VendorRelContact_ID)
        #     return error_obj
        # except:
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
        #     return error_obj
        else :
            # try:
            contact = VendorRelContact.objects.using(self._current_app_schema()).create (
                name=contact_obj.get_name ( ) , designation=contact_obj.get_designation( ) ,
                landline=contact_obj.get_landline ( ) , landline2=contact_obj.get_landline2 ( ) ,
                mobile=contact_obj.get_mobile ( ) ,
                mobile2=contact_obj.get_mobile2 ( ) , email=contact_obj.get_email ( ) ,
                dob=contact_obj.get_dob ( ) , wedding_date=contact_obj.get_wedding_date ( ) ,
                created_by=user_id, entity_id=self._entity_id(),portal_flag=contact_obj.get_portal_flag())
            self.audit_function ( contact , vendor_id , user_id , req_status , contact.id , ModifyStatus.create )

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

        contact_data = ContactResponse ( )
        contact_data.set_id ( contact.id )

        contact_data.set_name ( contact.name )
        contact_data.set_designation ( contact.designation)
        contact_data.set_landline ( contact.landline )
        contact_data.set_landline2 ( contact.landline2 )
        contact_data.set_mobile ( contact.mobile )
        contact_data.set_mobile2 ( contact.mobile2 )
        contact_data.set_email ( contact.email )
        contact_data.set_dob ( contact.dob )
        contact_data.set_wedding_date ( contact.wedding_date)
        contact_data.set_portal_flag(contact.portal_flag)

        return contact_data.id

    def fetch_contact_list ( self , user_id ) :
        contactlist = VendorRelContact.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())
        list_length = len ( contactlist )
        logger.info (str(list_length))
        if list_length <= 0 :
            error_obj = NWisefinError ( )
            error_obj.set_code ( ErrorMessage.INVALID_VendorRelContact_ID )
            error_obj.set_description ( ErrorDescription.INVALID_VendorRelContact_ID )
            return error_obj
        else :
            contact_list_data = NWisefinList ( )
            for contact in contactlist :
                contact_data = ContactResponse ( )
                contact_data.set_id ( contact.id )

                contact_data.set_name ( contact.name )
                contact_data.set_designation( contact.designation)
                contact_data.set_landline ( contact.landline )
                contact_data.set_landline2 ( contact.landline2 )
                contact_data.set_mobile ( contact.mobile )
                contact_data.set_mobile2 ( contact.mobile2 )
                contact_data.set_email ( contact.email )
                contact_data.set_dob ( contact.dob )
                contact_data.set_wedding_date ( contact.wedding_date )
                contact_data.set_portal_flag(contact.portal_flag)

                contact_list_data.append ( contact_data )
            return contact_list_data

    def fetch_contact ( self , contact_id , user_id ) :
        try :
            contact = VendorRelContact.objects.using(self._current_app_schema()).get ( id=contact_id, entity_id=self._entity_id())
            contact_data = ContactResponse ( )
            contact_data.set_id ( contact.id )

            contact_data.set_name ( contact.name )
            contact_data.set_designation( contact.designation)
            contact_data.set_landline ( contact.landline )
            contact_data.set_landline2 ( contact.landline2 )
            contact_data.set_mobile ( contact.mobile )
            contact_data.set_mobile2 ( contact.mobile2 )
            contact_data.set_email ( contact.email )
            contact_data.set_dob ( contact.dob )
            contact_data.set_wedding_date ( contact.wedding_date )
            contact_data.set_portal_flag(contact.portal_flag)

            return contact_data
        except VendorRelContact.DoesNotExist :
            error_obj = NWisefinError ( )
            error_obj.set_code ( ErrorMessage.INVALID_VendorRelContact_ID )
            error_obj.set_description ( ErrorDescription.INVALID_VendorRelContact_ID )
            return error_obj

    def delete_contact ( self , contact_id , user_id , vendor_id ) :
        req_status = RequestStatusUtil.ONBOARD
        contact = VendorRelContact.objects.using(self._current_app_schema()).filter ( id=contact_id, entity_id=self._entity_id()).delete ( )
        self.audit_function ( contact , vendor_id , user_id , req_status , contact_id , ModifyStatus.delete )

        if contact [ 0 ] == 0 :
            error_obj = NWisefinError ( )
            error_obj.set_code ( ErrorMessage.INVALID_VendorRelContact_ID )
            error_obj.set_description ( ErrorDescription.INVALID_VendorRelContact_ID )
            return error_obj
        else :
            success_obj = NWisefinSuccess ( )
            success_obj.set_status ( SuccessStatus.SUCCESS )
            success_obj.set_message ( SuccessMessage.DELETE_MESSAGE )
            return success_obj

    # modification contact

    def modification_create_contact ( self , contact_obj , user_id , vendor_id ) :
        req_status = RequestStatusUtil.MODIFICATION
        if not contact_obj.get_id ( ) is None :
            # try:
            contact = VendorRelContact.objects.using(self._current_app_schema()).create ( name=contact_obj.get_name ( ) ,
                                                        designation=contact_obj.get_designation( ) ,
                                                        landline=contact_obj.get_landline ( ) ,
                                                        landline2=contact_obj.get_landline2 ( ) ,
                                                        mobile=contact_obj.get_mobile ( ) ,
                                                        mobile2=contact_obj.get_mobile2 ( ) ,
                                                        email=contact_obj.get_email ( ) , dob=contact_obj.get_dob ( ) ,
                                                        wedding_date=contact_obj.get_wedding_date ( ) ,
                                                        created_by=user_id , modify_status=ModifyStatus.update ,
                                                        modified_by=user_id , modify_ref_id=contact_obj.get_id ( ), entity_id=self._entity_id(),
                                                        portal_flag=contact_obj.get_portal_flag())

            contact_update = VendorRelContact.objects.using(self._current_app_schema()).filter ( id=contact_obj.get_id(), entity_id=self._entity_id()).update (
                modify_ref_id=contact.id )
            contactupdate_auditdata = {'id' : contact_obj.get_id ( ) , 'modify_ref_id' : contact.id}
            VendorModificationRel.objects.using(self._current_app_schema()).create ( vendor_id=vendor_id , ref_id=contact_obj.get_id ( ) ,
                                                   ref_type=VendorRefType.VENDOR_REL_CONTACT ,
                                                   mod_status=ModifyStatus.update ,
                                                   modify_ref_id=contact.id, entity_id=self._entity_id())

            contact_update_id = contact_obj.get_id ( )
            self.audit_function ( contact , vendor_id , user_id , req_status , contact.id , ModifyStatus.create )
            self.audit_function ( contactupdate_auditdata , vendor_id , user_id , req_status , contact_update_id ,
                                  ModifyStatus.update )
        # except IntegrityError as error:
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.INVALID_DATA)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
        #     return error_obj
        #
        # except VendorRelContact.DoesNotExist:
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.INVALID_VendorRelContact_ID)
        #     error_obj.set_description(ErrorDescription.INVALID_VendorRelContact_ID)
        #     return error_obj
        #
        # except:
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
        #     return error_obj

        else :
            # try:
            contact = VendorRelContact.objects.using(self._current_app_schema()).create ( name=contact_obj.get_name ( ) ,
                                                        designation=contact_obj.get_designation( ) ,
                                                        landline=contact_obj.get_landline ( ) ,
                                                        landline2=contact_obj.get_landline2 ( ) ,
                                                        mobile=contact_obj.get_mobile ( ) ,
                                                        mobile2=contact_obj.get_mobile2 ( ) ,
                                                        email=contact_obj.get_email ( ) ,
                                                        dob=contact_obj.get_dob ( ) ,
                                                        wedding_date=contact_obj.get_wedding_date ( ) ,
                                                        created_by=user_id ,
                                                        modify_status=ModifyStatus.create , modified_by=user_id, entity_id=self._entity_id(),
                                                        portal_flag=contact_obj.get_portal_flag())

            contact.modify_ref_id = contact.id
            contact.save ( )

            VendorModificationRel.objects.using(self._current_app_schema()).create ( vendor_id=vendor_id , ref_id=contact.id ,
                                                   ref_type=VendorRefType.VENDOR_REL_CONTACT ,
                                                   mod_status=ModifyStatus.create ,
                                                   modify_ref_id=contact.id, entity_id=self._entity_id())

            self.audit_function ( contact , vendor_id , user_id , req_status , contact.id , ModifyStatus.create )
        # except IntegrityError as error:
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.INVALID_DATA)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
        #     return error_obj
        #
        # except VendorRelContact.DoesNotExist:
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.INVALID_VendorRelContact_ID)
        #     error_obj.set_description(ErrorDescription.INVALID_VendorRelContact_ID)
        #     return error_obj
        #
        # except:
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
        #     return error_obj

        contact_data = ContactResponse ( )
        contact_data.set_id ( contact.id )

        contact_data.set_name ( contact.name )
        return contact_data.id

    def modification_delete_contact ( self , contact_id , vendor_id , user_id ) :
        req_status = RequestStatusUtil.MODIFICATION
        try :
            contact_update = VendorRelContact.objects.using(self._current_app_schema()).filter ( id=contact_id, entity_id=self._entity_id()).update (
                modify_ref_id=contact_id )

            VendorModificationRel.objects.using(self._current_app_schema()).create ( vendor_id=vendor_id , ref_id=contact_id ,
                                                   ref_type=VendorRefType.VENDOR_REL_CONTACT ,
                                                   mod_status=ModifyStatus.delete ,
                                                   modify_ref_id=contact_id, entity_id=self._entity_id())
            self.audit_function ( contact_update , vendor_id , user_id , req_status , contact_id , ModifyStatus.update )

        except :
            error_obj = NWisefinError ( )
            error_obj.set_code ( ErrorMessage.UNEXPECTED_ERROR )
            error_obj.set_description ( ErrorDescription.UNEXPECTED_ERROR )
            return error_obj

    def modification_action_contact ( self , mod_status , old_id , new_id , vendor_id , user_id ) :

        req_status = RequestStatusUtil.MODIFICATION
        if mod_status == ModifyStatus.update or ModifyStatus.active_in :
            contact_obj = self.fetch_contact ( new_id , user_id )
            logger.info (str(contact_obj.get_dob ( ) ))
            if contact_obj.get_dob ( ) == str ( None ) :
                dob_date = None
            else :
                dob_date = contact_obj.get_dob ( )

            if contact_obj.get_wedding_date ( ) == str ( None ) :
                wed_date = None
            else :
                wed_date = contact_obj.get_wedding_date ( )
            contact_update = VendorRelContact.objects.using(self._current_app_schema()).filter ( id=old_id, entity_id=self._entity_id()).update (
                name=contact_obj.get_name ( ) , designation=contact_obj.get_designation( ) ,
                landline=contact_obj.get_landline ( ) , landline2=contact_obj.get_landline2 ( ) ,
                mobile=contact_obj.get_mobile ( ) , mobile2=contact_obj.get_mobile2 ( ) ,
                email=contact_obj.get_email ( ) , dob=dob_date ,
                wedding_date=wed_date ,
                modify_status=-1 , modify_ref_id=-1,portal_flag=contact_obj.get_portal_flag())

            # contact=VendorRelContact.objects.filter(id=new_id).delete()
            # audit
            self.audit_function ( contact_update , vendor_id , user_id , req_status , old_id , ModifyStatus.update )
            # self.audit_function(contact, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)

        elif mod_status == ModifyStatus.create :
            contact_update = VendorRelContact.objects.using(self._current_app_schema()).filter ( id=new_id, entity_id=self._entity_id()).update ( modify_status=-1 ,
                                                                                    modify_ref_id=-1 , modified_by=-1 )
            # audit
            self.audit_function ( contact_update , vendor_id , user_id , req_status , new_id , ModifyStatus.update )

        else :
            contact = VendorRelContact.objects.using(self._current_app_schema()).filter ( id=old_id, entity_id=self._entity_id()).delete ( )
            # audit
            self.audit_function ( contact , vendor_id , user_id , req_status , old_id , ModifyStatus.delete )
        return

    def modification_reject_contact ( self , mod_status , old_id , new_id , vendor_id , user_id ) :
        req_status = RequestStatusUtil.MODIFICATION
        if mod_status == ModifyStatus.update :
            contact = VendorRelContact.objects.using(self._current_app_schema()).filter ( id=new_id, entity_id=self._entity_id()).delete ( )
            contact_update = VendorRelContact.objects.using(self._current_app_schema()).filter ( id=old_id, entity_id=self._entity_id()).update ( modify_ref_id=-1 )
            # audit
            self.audit_function ( contact , vendor_id , user_id , req_status , new_id , ModifyStatus.delete )
            self.audit_function ( contact_update , vendor_id , user_id , req_status , old_id , ModifyStatus.update )
        elif mod_status == ModifyStatus.create :
            contact = VendorRelContact.objects.using(self._current_app_schema()).filter ( id=new_id, entity_id=self._entity_id()).delete ( )
            # audit
            self.audit_function ( contact , vendor_id , user_id , req_status , new_id , ModifyStatus.delete )
        else :
            contact_update = VendorRelContact.objects.using(self._current_app_schema()).filter ( id=old_id, entity_id=self._entity_id()).update ( modify_ref_id=-1 )
            # audit
            self.audit_function ( contact_update , vendor_id , user_id , req_status , old_id , ModifyStatus.update )
        return

    def audit_function ( self , contact , vendor_id , user_id , req_status , id , action ) :

        if action == ModifyStatus.delete :
            data = None
        elif action == ModifyStatus.update :
            data = contact
        else :
            data = contact.__dict__
            del data [ '_state' ]
        audit_service = VendorAuditService (self._scope())
        audit_obj = VendorAuditResponse ( )
        audit_obj.set_refid ( vendor_id )
        audit_obj.set_reftype ( VendorRefType.VENDOR )
        audit_obj.set_userid ( user_id )
        audit_obj.set_reqstatus ( req_status )
        audit_obj.set_relrefid ( id )
        audit_obj.set_relreftype ( VendorRefType.VENDOR_REL_CONTACT )
        audit_obj.set_action ( action )
        audit_obj.set_data ( data )
        audit_service.create_vendoraudit ( audit_obj )
        return

    def fetch_supplier ( self , supplier_id ) :
        supplier = SupplierBranch.objects.using(self._current_app_schema()).get ( id=supplier_id, entity_id=self._entity_id())
        supplier_data = {"id" : supplier.id , "code" : supplier.code , "name" : supplier.name , "gstno" : supplier.gstno
            , "address_id" : supplier.address_id , "vendor_id" : supplier.vendor_id}
        supplier_dic = json.dumps ( supplier_data , indent=7 )
        return supplier_data

    def fetch_supplier_code ( self , sup_code ) :
        supplier = SupplierBranch.objects.using(self._current_app_schema()).get ( code=sup_code, entity_id=self._entity_id())
        supplier_data = {"id" : supplier.id , "code" : supplier.code , "name" : supplier.name , "gstno" : supplier.gstno
            , "address_id" : supplier.address_id , "vendor_id" : supplier.vendor_id}
        supplier_dic = json.dumps ( supplier_data , indent=7 )
        return supplier_data

    def fetch_supplierlist ( request , supplier_ids ) :
        supplier_id2 = supplier_ids.get ( 'supplier_id' )
        obj = SupplierBranch.objects.using(request._current_app_schema()).filter ( id__in=supplier_id2, entity_id=request._entity_id()).values ( 'id' , 'name' )
        supplier_list_data = NWisefinList ( )
        for i in obj :
            data = {"id" : i [ 'id' ] , "name" : i [ 'name' ]}
            supplier_list_data.append ( data )
        return supplier_list_data.get ( )
