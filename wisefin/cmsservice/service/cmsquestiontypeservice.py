import traceback
from cmsservice.data.response.cmsquestiontyperesponse import Cmsquestiontyperesponse, Cmsquestypemapresponse
from cmsservice.models import CMSQuestionType, CMSQuestionTypeMapping
from django.utils.timezone import now
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class Cmsquestypeservice(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.CMS_SERVICE)

    def createcmsquestype(self, ans_obj, emp_id):
        try:
            ans = CMSQuestionType.objects.using(self._current_app_schema()).create(
                                            question_type_id=ans_obj.get_question_type_id(),
                                            vendor_id=ans_obj.get_vendor_id(),
                                            cat_id=ans_obj.get_cat_id(),
                                            subcat_id=ans_obj.get_subcat_id(),
                                            group_id=ans_obj.get_group_id(),
                                            created_by=emp_id,
                                            created_date=now())

            ans_data = Cmsquestiontyperesponse()
            ans_data.set_id(ans.id)
            ans_data.set_question_type_id(ans.question_type_id)
            ans_data.set_vendor_id(ans.vendor_id)
            ans_data.set_cat_id(ans.cat_id)
            ans_data.set_subcat_id(ans.subcat_id)
            ans_data.set_group_id(ans.group_id)
            return ans_data

        except Exception as ex:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(ex))
            return error_obj

    def createcmsquestypemap(self, ans_obj, emp_id):
        try:
            ans = CMSQuestionTypeMapping.objects.using(self._current_app_schema()).create(
                question_id=ans_obj.get_question_id(),
                mapping_id=ans_obj.get_mapping_id(),
                created_by=emp_id,
                created_date=now())

            ans_data = Cmsquestypemapresponse()
            ans_data.set_id(ans.id)
            ans_data.set_question_id(ans.question_id)
            ans_data.set_mapping_id(ans.mapping_id)
            return ans_data

        except Exception as ex:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(ex))
            return error_obj


from userservice.controller.vowusercontroller import VowUser


class VowQuesansService:
    def __init__(self, request):
        vowuser_info = VowUser().get_user(request)
        print(vowuser_info)
        self.emp_id = vowuser_info['user_id']
        self.entity_id = vowuser_info['entity_id']
        self.is_user = vowuser_info['is_user']
        self.schema = vowuser_info['schema']

    def vow_createcmsquestype(self, ans_obj):
        try:
            ans = CMSQuestionType.objects.using(self.schema).create(
                question_type_id=ans_obj.get_question_type_id(),
                vendor_id=ans_obj.get_vendor_id(),
                cat_id=ans_obj.get_cat_id(),
                subcat_id=ans_obj.get_subcat_id(),
                group_id=ans_obj.get_group_id(),
                is_user=self.is_user,
                created_by=self.emp_id,
                created_date=now())

            ans_data = Cmsquestiontyperesponse()
            ans_data.set_id(ans.id)
            ans_data.set_question_type_id(ans.question_type_id)
            ans_data.set_vendor_id(ans.vendor_id)
            ans_data.set_cat_id(ans.cat_id)
            ans_data.set_subcat_id(ans.subcat_id)
            ans_data.set_group_id(ans.group_id)
            return ans_data

        except Exception as ex:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(ex))
            return error_obj

    def vow_createcmsquestypemap(self, ans_obj):
        try:
            ans = CMSQuestionTypeMapping.objects.using(self.schema).create(
                question_id=ans_obj.get_question_id(),
                mapping_id=ans_obj.get_mapping_id(),
                is_user=self.is_user,
                created_by=self.emp_id,
                created_date=now())

            ans_data = Cmsquestypemapresponse()
            ans_data.set_id(ans.id)
            ans_data.set_question_id(ans.question_id)
            ans_data.set_mapping_id(ans.mapping_id)
            return ans_data

        except Exception as ex:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(ex))
            return error_obj
