from userservice.models import Employee
from vendorservice.data.response.directorresponse import DirectorResponse
from vendorservice.data.response.vendorauditresponse import VendorAuditResponse
from vendorservice.service.vendorauditservice import VendorAuditService
from vendorservice.service.vendorservice import VendorService
from vendorservice.models import Vendor, VendorDirector, VendorAddress, VendorModificationRel, VendorRelAddress
from vendorservice.data.response.vendoraddressresponse import AddressResponse
from django.db import IntegrityError
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from vendorservice.util.vendorutil import VendorRefType, ModifyStatus, RequestStatusUtil
from django.db.models import Q
from django.db.models import Max
from nwisefin.settings import logger
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace


class VendorAddressService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def create_vendoraddress(self, address_obj,vendor_id,user_id):
        req_status = RequestStatusUtil.ONBOARD
        if not address_obj.get_id() is None:
            # try:
                address_updsate = VendorAddress.objects.using(self._current_app_schema()).filter(id=address_obj.get_id(), entity_id=self._entity_id()).update(vendor_id=vendor_id,
                                                                                        line1=address_obj.get_line1(),
                                                                                          line2=address_obj.get_line2(),
                                                                                          line3=address_obj.get_line3(),
                                                                                          pincode_id=address_obj.get_pincode_id(),
                                                                                          city_id=address_obj.get_city_id(),
                                                                                          district_id=address_obj.get_district_id(),
                                                                                          state_id=address_obj.get_state_id(),
                                                                                          updated_by=user_id,
                                                                                          updated_date=timezone.now(),
                                                                                        portal_flag=address_obj.get_portal_flag())

                address_auditdata={'id':address_obj.get_id(),'vendor_id':vendor_id,
                                                                                        'line1':address_obj.get_line1(),
                                                                                          'line2':address_obj.get_line2(),
                                                                                          'line3':address_obj.get_line3(),
                                                                                          'pincode_id':address_obj.get_pincode_id(),
                                                                                          'city_id':address_obj.get_city_id(),
                                                                                          'district_id':address_obj.get_district_id(),
                                                                                          'state_id':address_obj.get_state_id(),
                                                                                          'updated_by':user_id,
                                                                                          'updated_date':timezone.now()}

                address = VendorAddress.objects.using(self._current_app_schema()).get(id=address_obj.get_id(), entity_id=self._entity_id())
                self.audit_function(address_auditdata, vendor_id, user_id, req_status, address.id, ModifyStatus.update)

            # except IntegrityError as error:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except VendorAddress.DoesNotExist:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_VendorRelAddress_ID)
            #     error_obj.set_description(ErrorDescription.INVALID_VendorRelAddress_ID)
            #     return error_obj
            # except:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj
        else:
            # try:
                address = VendorAddress.objects.using(self._current_app_schema()).create(line1=address_obj.get_line1(),
                                                          line2=address_obj.get_line2(), line3=address_obj.get_line3(),
                                                          pincode_id=address_obj.get_pincode_id(),
                                                          city_id=address_obj.get_city_id(),
                                                          district_id=address_obj.get_district_id(),
                                                          vendor_id=vendor_id,
                                                          state_id=address_obj.get_state_id(),
                                                          created_by=user_id, entity_id=self._entity_id(),
                                                          portal_flag=address_obj.get_portal_flag()
                                                          )
                self.audit_function(address, vendor_id, user_id, req_status, address.id, ModifyStatus.create)
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

        add_data = AddressResponse()
        add_data.set_id(address.id)
        add_data.set_line1(address.line1)
        add_data.set_line2(address.line2)
        add_data.set_line3(address.line3)
        add_data.set_pincode_id(address.pincode_id)
        add_data.set_city_id(address.city_id)
        add_data.set_district_id(address.district_id)
        add_data.set_state_id(address.state_id)
        add_data.set_portal_flag(address.portal_flag)
        return add_data

    def fetch_vendoraddress_list(self,vendor_id,address_id):
        addresslist = VendorAddress.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())
        list_length = len(addresslist)
        logger.info(str(list_length))
        if list_length <= 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_VendorRelAddress_ID)
            error_obj.set_description(ErrorDescription.INVALID_VendorRelAddress_ID)
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
                add_data.set_portal_flag(address.portal_flag)

                add_list_data.append(add_data)
            return add_list_data

    def fetch_vendoraddress(self,vendor_id,user_id):
        try:
            address = VendorAddress.objects.using(self._current_app_schema()).get(vendor_id=vendor_id, entity_id=self._entity_id())
            add_data = AddressResponse()
            add_data.set_id(address.id)
            add_data.set_line1(address.line1)
            add_data.set_line2(address.line2)
            add_data.set_line3(address.line3)
            add_data.set_pincode_id(address.pincode_id)
            add_data.set_city_id(address.city_id)
            add_data.set_district_id(address.district_id)
            add_data.set_state_id(address.state_id)
            add_data.set_portal_flag(address.portal_flag)

            return add_data
        except VendorAddress.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_VendorRelAddress_ID)
            error_obj.set_description(ErrorDescription.INVALID_VendorRelAddress_ID)
            return error_obj

    def delete_vendoraddress(self,vendor_id, address_id,user_id):

        address = VendorAddress.objects.using(self._current_app_schema()).filter(id=address_id, entity_id=self._entity_id()).delete()
        req_status = RequestStatusUtil.ONBOARD
        self.audit_function(address, vendor_id, user_id, req_status, address_id, ModifyStatus.delete)
        if address[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_VendorRelAddress_ID)
            error_obj.set_description(ErrorDescription.INVALID_VendorRelAddress_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def create_vendoraddress_modification(self, address_obj,vendor_id,user_id):
        if not address_obj.get_id() is None:
            vendor_service=VendorService(self._scope())

            # try:
            ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_ADDRESS, address_obj.get_id())
            if ref_flag == True:
                address = VendorAddress.objects.using(self._current_app_schema()).filter(id=address_obj.get_id(), entity_id=self._entity_id()).update(line1=address_obj.get_line1(),
                                                           line2=address_obj.get_line2(), line3=address_obj.get_line3(),
                                                           pincode_id=address_obj.get_pincode_id(),
                                                           city_id=address_obj.get_city_id(),
                                                           district_id=address_obj.get_district_id(),
                                                           vendor_id=vendor_id,
                                                           state_id=address_obj.get_state_id(),
                                                           portal_flag=address_obj.get_portal_flag())

                address=VendorAddress.objects.using(self._current_app_schema()).get(id=address_obj.get_id(), entity_id=self._entity_id())

            else:

                address = VendorAddress.objects.using(self._current_app_schema()).create(line1=address_obj.get_line1(),
                                                              line2=address_obj.get_line2(), line3=address_obj.get_line3(),
                                                              pincode_id=address_obj.get_pincode_id(),
                                                              city_id=address_obj.get_city_id(),
                                                              district_id=address_obj.get_district_id(),
                                                              vendor_id=vendor_id,
                                                              state_id=address_obj.get_state_id(),
                                                           modify_status=1,
                                                              created_by=user_id, entity_id=self._entity_id(),
                                                              portal_flag=address_obj.get_portal_flag()

                                                              )
                address_update = VendorAddress.objects.using(self._current_app_schema()).filter(id=address_obj.get_id(), entity_id=self._entity_id()).update(modify_ref_id=address.id,modified_by=user_id)

                VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=address_obj.get_id(),
                                                         ref_type=VendorRefType.VENDOR_ADDRESS, mod_status=2,
                                                         modify_ref_id=address.id, entity_id=self._entity_id())
        else:
            address = VendorAddress.objects.using(self._current_app_schema()).create(line1=address_obj.get_line1(),
                                                   line2=address_obj.get_line2(), line3=address_obj.get_line3(),
                                                   pincode_id=address_obj.get_pincode_id(),
                                                   city_id=address_obj.get_city_id(),
                                                   district_id=address_obj.get_district_id(),
                                                   vendor_id=vendor_id,
                                                   state_id=address_obj.get_state_id(),
                                                   modify_status=1,
                                                   created_by=user_id, entity_id=self._entity_id(),
                                                   portal_flag=address_obj.get_portal_flag()

                                                   )
            address_update = VendorAddress.objects.using(self._current_app_schema()).filter(id=address.id, entity_id=self._entity_id()).update(modify_ref_id=address.id,
                                                                                          modified_by=user_id)

            VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=address.id,
                                                 ref_type=VendorRefType.VENDOR_ADDRESS, mod_status=1,
                                                 modify_ref_id=address.id, entity_id=self._entity_id())
        req_status = RequestStatusUtil.MODIFICATION

                # self.audit_function(address, vendor_id, user_id, req_status, address.id, ModifyStatus.create)
                # self.audit_function(address_update, vendor_id, user_id, req_status, address_update.id, ModifyStatus.update)

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

        add_data = AddressResponse()
        add_data.set_id(address.id)
        add_data.set_line1(address.line1)
        add_data.set_line2(address.line2)
        add_data.set_line3(address.line3)
        add_data.set_pincode_id(address.pincode_id)
        add_data.set_city_id(address.city_id)
        add_data.set_district_id(address.district_id)
        add_data.set_state_id(address.state_id)
        add_data.set_portal_flag(address.portal_flag)
        return add_data

    def modification_action_vendoraddress(self, mod_status, old_id, new_id,vendor_id,user_id):

        if mod_status == 2:
            address_obj = self.approve_vendoraddress_modification(new_id,user_id)
            address = VendorAddress.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(vendor_id=vendor_id,
                                                                                   line1=address_obj.get_line1(),
                                                                                   line2=address_obj.get_line2(),
                                                                                   line3=address_obj.get_line3(),
                                                                                   pincode_id=address_obj.get_pincode_id(),
                                                                                   city_id=address_obj.get_city_id(),
                                                                                   district_id=address_obj.get_district_id(),
                                                                                   state_id=address_obj.get_state_id(),
                                                                     modify_status=-1,modified_by =-1,
                                                                     modify_ref_id=-1,
                                                                     portal_flag=address_obj.get_portal_flag()
                                                                     )


            req_status = RequestStatusUtil.MODIFICATION
            self.audit_function(address, vendor_id, user_id, req_status, old_id, ModifyStatus.update)
            # self.audit_function(address_delete, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)

        if mod_status==1:
            add_obj=VendorAddress.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).update( modify_status=-1,modified_by =-1,
                                                                     modify_ref_id=-1)

        if mod_status==0:
            vendor_obj = VendorAddress.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).delete()
        return

    def fetch_vendoraddress_modification(self,vendor_id,user_id):
        try:

            # address_max=VendorAddress.objects.filter(vendor_id=vendor_id).aggregate(Max('id'))
            # b=address_max['max_id']
            # a=address_max.id__max
            # address = VendorAddress.objects.get(id=b)
            address = VendorAddress.objects.using(self._current_app_schema()).get(Q(vendor_id=vendor_id) & Q(modify_status=1)&Q(entity_id=self._entity_id()))
            add_data = AddressResponse()
            add_data.set_id(address.id)
            add_data.set_line1(address.line1)
            add_data.set_line2(address.line2)
            add_data.set_line3(address.line3)
            add_data.set_pincode_id(address.pincode_id)
            add_data.set_city_id(address.city_id)
            add_data.set_district_id(address.district_id)
            add_data.set_state_id(address.state_id)
            add_data.set_portal_flag(address.portal_flag)

            return add_data
        except VendorAddress.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_VendorRelAddress_ID)
            error_obj.set_description(ErrorDescription.INVALID_VendorRelAddress_ID)
            return error_obj

    def approve_vendoraddress_modification(self,add_id,user_id):
        try:

            # address_max=VendorAddress.objects.filter(vendor_id=vendor_id).aggregate(Max('id'))
            # b=address_max['max_id']
            # a=address_max.id__max
            # address = VendorAddress.objects.get(id=b)
            address = VendorAddress.objects.using(self._current_app_schema()).get(Q(id=add_id) & Q(modify_status=1)&Q(entity_id=self._entity_id()))
            add_data = AddressResponse()
            add_data.set_id(address.id)
            add_data.set_line1(address.line1)
            add_data.set_line2(address.line2)
            add_data.set_line3(address.line3)
            add_data.set_pincode_id(address.pincode_id)
            add_data.set_city_id(address.city_id)
            add_data.set_district_id(address.district_id)
            add_data.set_state_id(address.state_id)
            add_data.set_portal_flag(address.portal_flag)

            return add_data
        except VendorAddress.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_VendorRelAddress_ID)
            error_obj.set_description(ErrorDescription.INVALID_VendorRelAddress_ID)
            return error_obj


    def modification_reject_vendoraddress(self, mod_status, old_id, new_id, user_id, vendor_id):

        if mod_status == ModifyStatus.update:
            vendor_delete =VendorAddress.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()
            vendor_address =VendorAddress.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(modify_ref_id=-1)

            req_status = RequestStatusUtil.MODIFICATION
            self.audit_function(vendor_delete, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)
            self.audit_function(vendor_address, vendor_id, user_id, req_status, old_id, ModifyStatus.update)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj

    # microtomicro
    def fetch_vendoraddress1(request, address_id):
        vendoraddresss = VendorRelAddress.objects.using(request._current_app_schema()).get(id=address_id, entity_id=request._entity_id())
        vendoraddress_data = {"id": vendoraddresss.id,
                              "line1": vendoraddresss.line1,
                              "line2": vendoraddresss.line2,
                              "line3": vendoraddresss.line3,
                              "pincode_id": vendoraddresss.pincode_id,
                              "city_id": vendoraddresss.city_id,
                              "state_id": vendoraddresss.state_id}
        # venaddress_dic = json.dumps(vendoraddress_data, indent=4)
        return vendoraddress_data

    def audit_function(self, vendor_addr, vendor_id, user_id, req_status, id, action):
        if action == ModifyStatus.delete:
            data = None
        elif action == ModifyStatus.update:
            data = vendor_addr
        else:
            data = vendor_addr.__dict__
            del data['_state']
        audit_service = VendorAuditService(self._scope())
        audit_obj = VendorAuditResponse()
        audit_obj.set_refid(vendor_id)
        audit_obj.set_reftype(VendorRefType.VENDOR)
        audit_obj.set_userid(user_id)
        audit_obj.set_reqstatus(req_status)
        audit_obj.set_relrefid(id)
        audit_obj.set_relreftype(VendorRefType.VENDOR_ADDRESS)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_vendoraudit(audit_obj)
        return

    def vow_fetch_vendoraddress(self,vendor_id,user_id):
        try:
            address = VendorAddress.objects.using(self._current_app_schema()).get(vendor_id=vendor_id, entity_id=self._entity_id(),
                                                                                  modify_status=-1)
            add_data = AddressResponse()
            add_data.set_id(address.id)
            add_data.set_line1(address.line1)
            add_data.set_line2(address.line2)
            add_data.set_line3(address.line3)
            add_data.set_pincode_id(address.pincode_id)
            add_data.set_city_id(address.city_id)
            add_data.set_district_id(address.district_id)
            add_data.set_state_id(address.state_id)
            add_data.set_portal_flag(address.portal_flag)

            return add_data
        except VendorAddress.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_VendorRelAddress_ID)
            error_obj.set_description(ErrorDescription.INVALID_VendorRelAddress_ID)
            return error_obj
