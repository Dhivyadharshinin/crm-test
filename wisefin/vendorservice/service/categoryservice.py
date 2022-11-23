from django.db import IntegrityError
from vendorservice.data.response.paymoderesponse import PaymodeResponse
from vendorservice.data.response.mapcategoryresponse import ApcategoryResponse
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from masterservice.models import District
from masterservice.models import Apcategory
from django.utils import timezone
from nwisefin.settings import logger
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace


class CategoryService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_category(self, Category_obj, user_id):
        if not Category_obj.get_id() is None:
            try:
                category = Apcategory.objects.using(self._current_app_schema()).filter(id=Category_obj.get_id(), entity_id=self._entity_id()).update(code=Category_obj.get_code(),
                                                                                 no=Category_obj.get_no(),
                                                                                 name=Category_obj.get_name(),
                                                                                 glno=Category_obj.get_glno(),
                                                                                 isasset=Category_obj.get_isasset(),
                                                                                 updated_by=user_id,
                                                                                 updated_date=timezone.now())
                category = Apcategory.objects.using(self._current_app_schema()).get(id=Category_obj.get_id(), entity_id=self._entity_id())
            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Apcategory.DoesNotExist:
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
                category = Apcategory.objects.using(self._current_app_schema()).create(code=Category_obj.get_code(),
                                                                                 no=Category_obj.get_no(),
                                                                                 name=Category_obj.get_name(),
                                                                                 glno=Category_obj.get_glno(),
                                                                                 isasset=Category_obj.get_isasset(),
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
        cat_data = ApcategoryResponse()
        cat_data.set_id(category.id)
        cat_data.set_code(category.code)
        cat_data.set_no(category.no)
        cat_data.set_name(category.name)
        cat_data.set_status(category.status)
        cat_data.set_glno(category.glno)
        cat_data.set_isasset(category.isasset)
        cat_data.set_created_by(category.created_by)
        cat_data.set_updated_by(category.updated_by)
        return cat_data
    def fetchcategory(self, category_id):
        try:
            category = Apcategory.objects.using(self._current_app_schema()).get(id=category_id, entity_id=self._entity_id())
            cat_data = ApcategoryResponse()
            cat_data.set_id(category.id)
            cat_data.set_code(category.code)
            cat_data.set_no(category.no)
            cat_data.set_name(category.name)
            cat_data.set_status(category.status)
            cat_data.set_glno(category.glno)
            cat_data.set_isasset(category.isasset)
            cat_data.set_created_by(category.created_by)
            cat_data.set_updated_by(category.updated_by)
            return cat_data
        except Apcategory.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_STATE_ID)
            error_obj.set_description(ErrorDescription.INVALID_STATE_ID)
            return error_obj
    def fetch_category_list(self):
        categoryList = Apcategory.objects.using(self._current_app_schema()).all()
        list_length = len(categoryList)
        logger.info(str(list_length))
        category_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for category in categoryList:
                cat_data = ApcategoryResponse()
                cat_data.set_id(category.id)
                cat_data.set_code(category.code)
                cat_data.set_no(category.no)
                cat_data.set_name(category.name)
                cat_data.set_status(category.status)
                cat_data.set_glno(category.glno)
                cat_data.set_isasset(category.isasset)
                cat_data.set_created_by(category.created_by)
                cat_data.set_updated_by(category.updated_by)
                category_list_data.append(cat_data)
        return category_list_data

    def delete_category(self, category_id):
        category = Apcategory.objects.using(self._current_app_schema()).filter(id=category_id, entity_id=self._entity_id()).delete()
        if category[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_CATEGORY_ID)
            error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
