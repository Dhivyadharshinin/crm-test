from masterservice.data.response.apcategoryresponse import ApcategoryResponse
from masterservice.data.response.apsubcategoryresponse import ApsubcategoryResponse
from masterservice.models import Apcategory, APsubcategory
from userservice.controller.vowusercontroller import VowUser
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage


class MasterCommonService:
    def __init__(self, request):
        vowuser_info = VowUser().get_user(request)

        self.emp_id = vowuser_info['user_id']
        self.entity_id = vowuser_info['entity_id']
        self.is_user = vowuser_info['is_user']
        self.schema = vowuser_info['schema']

    def fetchcategory(self, category_id):
        try:
            category = Apcategory.objects.using(self.schema).get(id=category_id)
            cat_data = ApcategoryResponse()
            cat_data.set_id(category.id)
            cat_data.set_code(category.code)
            cat_data.set_no(category.no)
            cat_data.set_name(category.name)
            cat_data.set_glno(category.glno)
            cat_data.set_isasset(category.isasset)
            cat_data.set_expense(category.expense)
            return cat_data
        except Apcategory.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_category_ID)
            error_obj.set_description(ErrorDescription.INVALID_category_ID)
            return error_obj

    def fetchsubcategory(self, subcategory_id):
        try:
            subcategory = APsubcategory.objects.using(self.schema).get(id=subcategory_id)
            cat_data = ApsubcategoryResponse()
            cat_data.set_id(subcategory.id)
            cat_data.set_code(subcategory.code)
            cat_data.set_assetcode(subcategory.assetcode)
            cat_data.set_no(subcategory.no)
            cat_data.set_name(subcategory.name)
            cat_data.set_category(subcategory.category)
            cat_data.set_gstblocked(subcategory.gstblocked)
            cat_data.set_gstrcm(subcategory.gstrcm)
            cat_data.set_glno(subcategory.glno)
            cat_data.set_assetcode(subcategory.assetcode)
            return cat_data
        except APsubcategory.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_SUBCATEGORY_ID)
            error_obj.set_description(ErrorDescription.INVALID_SUBCATEGORY_ID)
            return error_obj