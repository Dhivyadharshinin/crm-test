from django.db import IntegrityError
from vendorservice.data.response.paymoderesponse import PaymodeResponse
from vendorservice.data.response.mapsubcategoryresponse import ApsubcategoryResponse
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from masterservice.models import District
from masterservice.models import APsubcategory
from django.utils import timezone
from nwisefin.settings import logger
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace


class SubcategoryService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_subcategory(self, Subcategory_obj, user_id):
        if not Subcategory_obj.get_id() is None:
            try:
                subcategory = APsubcategory.objects.using(self._current_app_schema()).filter(id=Subcategory_obj.get_id(), entity_id=self._entity_id()).update(code=Subcategory_obj.get_code(),
                                                                                 no=Subcategory_obj.get_no(),
                                                                                 name=Subcategory_obj.get_name(),
                                                                                 category_id=Subcategory_obj.get_category_id(),
                                                                                 glno=Subcategory_obj.get_glno(),
                                                                                 expense=Subcategory_obj.get_expense(),
                                                                                 gstblocked=Subcategory_obj.get_gstblocked(),
                                                                                 gstrcm=Subcategory_obj.get_gstrcm(),
                                                                                 updated_by=user_id,
                                                                                 updated_date=timezone.now())
                subcategory = APsubcategory.objects.using(self._current_app_schema()).get(id=Subcategory_obj.get_id(), entity_id=self._entity_id())
            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except APsubcategory.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_District_ID)
                error_obj.set_description(ErrorDescription.INVALID_District_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                subcategory = APsubcategory.objects.using(self._current_app_schema()).create(code=Subcategory_obj.get_code(),
                                                                                 no=Subcategory_obj.get_no(),
                                                                                 name=Subcategory_obj.get_name(),
                                                                                 category_id=Subcategory_obj.get_category_id(),
                                                                                 glno=Subcategory_obj.get_glno(),
                                                                                 expense=Subcategory_obj.get_expense(),
                                                                                 gstblocked=Subcategory_obj.get_gstblocked(),
                                                                                 gstrcm=Subcategory_obj.get_gstrcm(),
                                                                                 created_by=user_id, entity_id=self._entity_id()
                                                                                 )
            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        cat_data = ApsubcategoryResponse()
        cat_data.set_id(subcategory.id)
        cat_data.set_code(subcategory.code)
        cat_data.set_no(subcategory.no)
        cat_data.set_name(subcategory.name)
        cat_data.set_status(subcategory.status)
        cat_data.set_category_id(subcategory.category_id)
        # cat_data.set_expense(subcategory.expense)
        cat_data.set_gstblocked(subcategory.gstblocked)
        cat_data.set_gstrcm(subcategory.gstrcm)
        cat_data.set_glno(subcategory.glno)
        cat_data.set_created_by(subcategory.created_by)
        cat_data.set_updated_by(subcategory.updated_by)
        return cat_data
    def fetchsubcategory(self,subcategory_id):
        try:
            subcategory = APsubcategory.objects.using(self._current_app_schema()).get(id=subcategory_id, entity_id=self._entity_id())
            cat_data = ApsubcategoryResponse()
            cat_data.set_id(subcategory.id)
            cat_data.set_code(subcategory.code)
            cat_data.set_no(subcategory.no)
            cat_data.set_name(subcategory.name)
            cat_data.set_status(subcategory.status)
            cat_data.set_category_id(subcategory.category_id)
            # cat_data.set_expense(subcategory.expense)
            cat_data.set_gstblocked(subcategory.gstblocked)
            cat_data.set_gstrcm(subcategory.gstrcm)
            cat_data.set_glno(subcategory.glno)
            cat_data.set_created_by(subcategory.created_by)
            cat_data.set_updated_by(subcategory.updated_by)
            return cat_data
        except APsubcategory.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_STATE_ID)
            error_obj.set_description(ErrorDescription.INVALID_STATE_ID)
            return error_obj
    def fetch_subcategory_list(self):
        subcategoryList = APsubcategory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())
        list_length = len(subcategoryList)
        logger.info(str(list_length))
        subcategory_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for subcategory in subcategoryList:
                cat_data = ApsubcategoryResponse()
                cat_data.set_id(subcategory.id)
                cat_data.set_code(subcategory.code)
                cat_data.set_no(subcategory.no)
                cat_data.set_name(subcategory.name)
                cat_data.set_status(subcategory.status)
                cat_data.set_category_id(subcategory.category_id)
                # cat_data.set_expense(subcategory.expense)
                cat_data.set_gstblocked(subcategory.gstblocked)
                cat_data.set_gstrcm(subcategory.gstrcm)
                cat_data.set_glno(subcategory.glno)
                cat_data.set_created_by(subcategory.created_by)
                cat_data.set_updated_by(subcategory.updated_by)
                subcategory_list_data.append(cat_data)
        return subcategory_list_data

    def delete_subcategory(self,subcategory_id):
        subcategory = APsubcategory.objects.using(self._current_app_schema()).filter(id=subcategory_id, entity_id=self._entity_id()).delete()
        if subcategory[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_CATEGORY_ID)
            error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
