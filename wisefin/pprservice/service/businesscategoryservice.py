
from django.db import IntegrityError
from django.db.models import Q

from pprservice.models import Business_Category
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from datetime import datetime
now = datetime.now()
from pprservice.data.response.businesscategoryresponse import BusinessCategoryResponse

from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator

class BusinessCategoryService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.PPR_SERVICE)

    def create_businesscategory(self, category_obj, user_id):
        if not category_obj.get_id() is None:
            try:
                category_update = Business_Category.objects.using(self._current_app_schema()).filter(id=category_obj.get_id(),entity_id=self._entity_id()).update(
                                name=category_obj.get_name(),
                                sector_id=category_obj.get_sector_id(),
                                updated_date=now,
                                updated_by=user_id)

                category_update = Business_Category.objects.using(self._current_app_schema()).objects.get(id=category_obj.get_id(),entity_id=self._entity_id())

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Business_Category.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CATEGORY_ID)
                error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                category_update = Business_Category.objects.using(self._current_app_schema()).create(
                                                    name=category_obj.get_name(),
                                                    sector_id=category_obj.get_sector_id(),
                                                    created_by=user_id,entity_id=self._entity_id())
                code = "BCAT" + str(category_update.id)
                category_update.code = code
                category_update.save()

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

        category_data = BusinessCategoryResponse()
        category_data.set_id(category_update.id)
        category_data.set_code(category_update.code)
        category_data.set_name(category_update.name)
        category_data.set_sector(category_update.sector_id)
        return category_data

    def fetch_category_list(self,vys_page,query):
        conditions = Q(status=1,entity_id=self._entity_id())
        if query is not None:
            conditions &= Q(name__icontains=query)
        category_obj = Business_Category.objects.using(self._current_app_schema()).filter(conditions).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(category_obj)
        cate_list_data = NWisefinList()
        if list_length >= 0:

            for catobj in category_obj:
                cat_data = BusinessCategoryResponse()
                cat_data.set_id(catobj.id)
                cat_data.set_code(catobj.code)
                cat_data.set_name(catobj.name)
                cat_data.set_sector(catobj.sector_id)
                cate_list_data.append(cat_data)
                vpage = NWisefinPaginator(category_obj, vys_page.get_index(), 10)
                cate_list_data.set_pagination(vpage)
        return cate_list_data

    def fetch_businesscategory(self, category_id,user_id):
        try:
            cate_var = Business_Category.objects.using(self._current_app_schema()).get(id=category_id,entity_id=self._entity_id())
            cate_data = BusinessCategoryResponse()
            cate_data.set_id(cate_var.id)
            cate_data.set_code(cate_var.code)
            cate_data.set_name(cate_var.name)
            return cate_data
        except Business_Category.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_BANK_ID)
            error_obj.set_description(ErrorDescription.INVALID_BANK_ID)
            return error_obj

    def delete_category(self, category_id,user_id):
        category_obj = Business_Category.objects.using(self._current_app_schema()).filter(id=category_id,entity_id=self._entity_id()).delete()

        if category_obj[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_BANK_ID)
            error_obj.set_description(ErrorDescription.INVALID_BANK_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def fetch_businesscategory_search(self,query,vys_page):
        condition=Q(status=1,entity_id=self._entity_id())
        if query is not None:
            condition &=Q(name__icontains=query)
        category_obj = Business_Category.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        cate_list_data = NWisefinList()
        for catobj in category_obj:
            cat_data = BusinessCategoryResponse()
            cat_data.set_id(catobj.id)
            cat_data.set_code(catobj.code)
            cat_data.set_name(catobj.name)
            cat_data.set_sector(catobj.sector_id)
            cate_list_data.append(cat_data)
            vpage = NWisefinPaginator(category_obj, vys_page.get_index(), 10)
            cate_list_data.set_pagination(vpage)
        return cate_list_data