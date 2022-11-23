from django.db import IntegrityError
from django.db.models import Q
from nwisefin.settings import logger
from userservice.models import Employee
from vendorservice.data.response.directorresponse import DirectorResponse
from vendorservice.models import VendorDirector,VendorModificationRel
from vendorservice.service.vendorservice import VendorService
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from vendorservice.util.vendorutil import VendorRefType,ModifyStatus
from django.db.models import Max
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace


class DirectorService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def create_director(self, vendor_id, director_obj, user_id):
            # emp = Employee.objects.get(user_id=user_id)
            # employee_id = emp.id

            if not director_obj.get_id() is None:
                # try:
                    director = VendorDirector.objects.using(self._current_app_schema()).filter(id=director_obj.get_id(), entity_id=self._entity_id()).update(
                        vendor_id=vendor_id, name=director_obj.get_name(),d_sign=director_obj.get_d_sign(),
                        d_pan=director_obj.get_d_pan(), d_sanctions=director_obj.get_d_sanctions(), d_match=director_obj.get_d_match(),
                        updated_date=timezone.now(), updated_by=user_id,portal_flag=director_obj.get_portal_flag())
                    director = VendorDirector.objects.using(self._current_app_schema()).get(id=director_obj.get_id(), entity_id=self._entity_id())
                # except IntegrityError as error:
                #     error_obj = Error()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj
                # except VendorDirector.DoesNotExist:
                #     error_obj = Error()
                #     error_obj.set_code(ErrorMessage.INVALID_VENDORDIRECTOR_ID)
                #     error_obj.set_description(ErrorDescription.INVALID_VENDORDIRECTOR_ID)
                #     return error_obj
                # except:
                #     error_obj = Error()
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                #     return error_obj
            else:
                # try:

                    director = VendorDirector.objects.using(self._current_app_schema()).create(vendor_id=vendor_id,
                                                             name=director_obj.get_name(), d_sign=director_obj.get_d_sign(),
                        d_pan=director_obj.get_d_pan(), d_sanctions=director_obj.get_d_sanctions(), d_match=director_obj.get_d_match(),
                                                             created_by=user_id, entity_id=self._entity_id(),portal_flag=director_obj.get_portal_flag())

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
            director_data = DirectorResponse()
            director_data.set_id(director.id)
            director_data.set_name(director.name)
            # director_data.set_d_sign(director.d_sign)
            director_data.set_d_pan(director.d_pan)
            # director_data.set_d_sanctions(director.d_sanctions)
            # director_data.set_d_match(director.d_match)
            director_data.set_portal_flag(director.portal_flag)
            return director_data

    def create_bulk_director(self, director_obj, user_id):
        pass

    def fetch_director_list(self,vendor_id, user_id):
            directorList = VendorDirector.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())
            list_length = len(directorList)
            logger.info(str(list_length))
            dir_list_data = NWisefinList()
            if list_length <= 0:
                pass
            else:
                for director in directorList:
                    director_data = DirectorResponse()
                    director_data.set_id(director.id)
                    #director_data.set_vendor_id(director.vendor_id)
                    director_data.set_name(director.name)
                    # director_data.set_d_sign(director.d_sign)
                    director_data.set_d_pan(director.d_pan)
                    # director_data.set_d_sanctions(director.d_sanctions)
                    # director_data.set_d_match(director.d_match)
                    director_data.set_portal_flag(director.portal_flag)
                    dir_list_data.append(director_data)
            return dir_list_data


    def fetch_director_count(self, vendor_id, user_id):
        vendor_service = VendorService(self._scope())
        director_count = vendor_service.get_director_count(vendor_id)
        return director_count

    def fetch_director(self, vendor_id, user_id):
            try:
                director = VendorDirector.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id, entity_id=self._entity_id())
                dir_array=[]
                for i in director:
                    # x = director[i]
                    director_data = DirectorResponse()
                    director_data.set_id(i.id)
                    director_data.set_vendor_id(i.vendor_id)
                    director_data.set_name(i.name)
                    # director_data.set_d_sign(i.d_sign)
                    director_data.set_d_pan(i.d_pan)
                    # director_data.set_d_sanctions(i.d_sanctions)
                    # director_data.set_d_match(i.d_match)
                    director_data.set_portal_flag(i.portal_flag)
                    dir_array.append(director_data)

                return dir_array
            except VendorDirector.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_VENDORDIRECTOR_ID)
                error_obj.set_description(ErrorDescription.INVALID_VENDORDIRECTOR_ID)
                return error_obj

    def delete_director(self, vendor_id, director_id, user_id):

            director = VendorDirector.objects.using(self._current_app_schema()).filter(id=director_id, entity_id=self._entity_id()).delete()
            if director[0] == 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_VENDORDIRECTOR_ID)
                error_obj.set_description(ErrorDescription.INVALID_VENDORDIRECTOR_ID)
                return error_obj
            else:
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
                return success_obj

    def create_director_modification(self, vendor_id, director_obj, user_id):

            if not director_obj.get_id() is None:
                vendor_service = VendorService(self._scope())
                # try:
                ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_DIRECTOR, director_obj.get_id())
                if ref_flag == True:
                        director = VendorDirector.objects.using(self._current_app_schema()).filter(id=director_obj.get_id(), entity_id=self._entity_id()).update(vendor_id=vendor_id,
                                                                 name=director_obj.get_name(), d_sign=director_obj.get_d_sign(),
                        d_pan=director_obj.get_d_pan(), d_sanctions=director_obj.get_d_sanctions(), d_match=director_obj.get_d_match(),
                                                                                                                                                                 modify_status=1,
                        portal_flag=director_obj.get_portal_flag()
                                                                 )
                        director=VendorDirector.objects.using(self._current_app_schema()).get(id=director_obj.get_id(), entity_id=self._entity_id())
                else:
                        director = VendorDirector.objects.using(self._current_app_schema()).create(vendor_id=vendor_id,
                                                                 name=director_obj.get_name(), d_sign=director_obj.get_d_sign(),
                        d_pan=director_obj.get_d_pan(), d_sanctions=director_obj.get_d_sanctions(), d_match=director_obj.get_d_match(),
                                                                                                   modify_status=1,
                                                                 created_by=user_id, entity_id=self._entity_id(),portal_flag=director_obj.get_portal_flag())

                        director_update = VendorDirector.objects.using(self._current_app_schema()).filter(id=director_obj.get_id(), entity_id=self._entity_id()).update(modify_ref_id=director.id,modified_by=user_id)

                        VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=director_obj.get_id(),
                                                         ref_type=VendorRefType.VENDOR_DIRECTOR, mod_status=2,
                                                         modify_ref_id=director.id, entity_id=self._entity_id())

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

                    director = VendorDirector.objects.using(self._current_app_schema()).create(vendor_id=vendor_id,
                                                             name=director_obj.get_name(), d_sign=director_obj.get_d_sign(),
                        d_pan=director_obj.get_d_pan(), d_sanctions=director_obj.get_d_sanctions(), d_match=director_obj.get_d_match(),
                                                             modify_status=1,
                                                             created_by=user_id, entity_id=self._entity_id(),portal_flag=director_obj.get_portal_flag())
                    director_update=VendorDirector.objects.using(self._current_app_schema()).filter(id=director.id, entity_id=self._entity_id()).update(modify_ref_id=director.id)
                    VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=director.id,
                                                         ref_type=VendorRefType.VENDOR_DIRECTOR, mod_status=2,
                                                         modify_ref_id=director.id, entity_id=self._entity_id())

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
            director_data = DirectorResponse()
            director_data.set_id(director.id)
            director_data.set_name(director.name)
            # director_data.set_d_sign(director.d_sign)
            director_data.set_d_pan(director.d_pan)
            # director_data.set_d_sanctions(director.d_sanctions)
            # director_data.set_d_match(director.d_match)
            director_data.set_portal_flag(director.portal_flag)
            return director_data

    def modification_action_vendordirector(self, mod_status, old_id, new_id,vendor_id,user_id):
        if mod_status == 2:
            director_obj = self.approve_director_modification(new_id,user_id)

            director = VendorDirector.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(
            vendor_id=vendor_id, name=director_obj.name,d_sign=director_obj.get_d_sign(), d_pan=director_obj.get_d_pan(),
                d_sanctions=director_obj.get_d_sanctions(), d_match=director_obj.get_d_match(), modify_status=-1,
                modified_by =-1, modify_ref_id=-1, portal_flag=director_obj.get_portal_flag()
            )
            return

    def fetch_director_modification(self, vendor_id, user_id):
            try:
                director = VendorDirector.objects.using(self._current_app_schema()).all().filter(Q(vendor_id=vendor_id) & Q(modify_status=1)&Q(entity_id=self._entity_id()))
                dir_array=[]
                for i in director:
                    # x = director[i]
                    director_data = DirectorResponse()
                    director_data.set_id(i.id)
                    director_data.set_vendor_id(i.vendor_id)
                    director_data.set_name(i.name)
                    # director_data.set_d_sign(i.d_sign)
                    director_data.set_d_pan(i.d_pan)
                    # director_data.set_d_sanctions(i.d_sanctions)
                    # director_data.set_d_match(i.d_match)
                    director_data.set_portal_flag(i.portal_flag)
                    dir_array.append(director_data)

                return dir_array
            except VendorDirector.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_VENDORDIRECTOR_ID)
                error_obj.set_description(ErrorDescription.INVALID_VENDORDIRECTOR_ID)
                return error_obj

    def approve_director_modification(self, dic_id, user_id):
            try:
                director = VendorDirector.objects.using(self._current_app_schema()).get(Q(id=dic_id) & Q(modify_status=1)&Q(entity_id=self._entity_id()))
                director_data = DirectorResponse()
                director_data.set_id(director.id)
                director_data.set_vendor_id(director.vendor_id)
                director_data.set_name(director.name)
                # director_data.set_d_sign(director.d_sign)
                director_data.set_d_pan(director.d_pan)
                # director_data.set_d_sanctions(director.d_sanctions)
                # director_data.set_d_match(director.d_match)
                director_data.set_portal_flag(director.portal_flag)
                return director_data
            except VendorDirector.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_VENDORDIRECTOR_ID)
                error_obj.set_description(ErrorDescription.INVALID_VENDORDIRECTOR_ID)
                return error_obj

    def modification_reject_vendordirector(self, mod_status, old_id, new_id, user_id):
        if mod_status == ModifyStatus.update:
            VendorDirector.objects.using(self._current_app_schema()).filter(id=new_id).delete()
            vendor_director =VendorDirector.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(modify_ref_id=-1)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj

    def vow_fetch_director(self, vendor_id, user_id):
            try:
                director = VendorDirector.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id, entity_id=self._entity_id(),
                                                                                           modify_status=-1)
                dir_array=[]
                for i in director:
                    director_data = DirectorResponse()
                    director_data.set_id(i.id)
                    director_data.set_vendor_id(i.vendor_id)
                    director_data.set_name(i.name)
                    director_data.set_d_pan(i.d_pan)
                    director_data.set_portal_flag(i.portal_flag)
                    dir_array.append(director_data)

                return dir_array
            except VendorDirector.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_VENDORDIRECTOR_ID)
                error_obj.set_description(ErrorDescription.INVALID_VENDORDIRECTOR_ID)
                return error_obj
