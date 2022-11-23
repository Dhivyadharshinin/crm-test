import json

from django.db.models import Q

from masterservice.data.response.questiontypemappresponse import QuestiontypemappResponse, QuestionflagResponse, \
    QuestionflagResponse
from masterservice.service.questionheaderservice import QuestionheaderService
from masterservice.service.questiontypeservice import QuestiontypeService
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessMessage, SuccessStatus
from masterservice.util.masterutil import ModifyStatus
from masterservice.models.mastermodels import Questions_Typemapping, Questions_flagmaster
from masterservice.service.questionservice import QuestionService


class QuestiontypemappService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_questiontype_mapping(self,question_obj,question_id,emp_id):
        resp = NWisefinSuccess()
        if not question_obj.get_id() is None:
            obj = Questions_Typemapping.objects.using(self._current_app_schema()).filter(id=question_obj.get_id(),entity_id=self._entity_id()).update(is_checked=question_obj.get_is_checked())

            obj = Questions_Typemapping.objects.using(self._current_app_schema()).get(id=question_obj.get_id(),
                                                                                         entity_id=self._entity_id())
            resp.set_message(SuccessMessage.UPDATE_MESSAGE)
            resp.set_status(SuccessStatus.SUCCESS)

        else:
            obj = Questions_Typemapping.objects.using(self._current_app_schema()).create(type_id=question_obj.get_type_id(),header=question_obj.get_header(), question_id=question_id, created_by=emp_id,entity_id=self._entity_id(),is_checked=question_obj.get_is_checked())

            resp.set_status(SuccessStatus.SUCCESS)
            resp.set_message(SuccessMessage.CREATE_MESSAGE)

        return resp

    def fetch_questiontype_mapping(self, vys_page, request):
        query = request.GET.get('query')
        header = request.GET.get('header')
        condtion=Q(entity_id=self._entity_id(), status=ModifyStatus.create)
        if query is not None and query !='':
            condtion &=Q(type_id=query)
        elif header is not None and header!='':
            condtion &=Q(header=header)
        questiontype_obj = Questions_Typemapping.objects.using(self._current_app_schema()).filter(condtion).order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        header_list = []
        type_list = []
        question_list = []
        for i in questiontype_obj:
            header_id = i.header
            type_id = i.type.id
            question_id = i.question.id
            header_list.append(header_id)
            type_list.append(type_id)
            question_list.append(question_id)
        header_serv = QuestionheaderService(self._scope())
        type_serv = QuestiontypeService(self._scope())
        question_serv = QuestionService(self._scope())
        header_data = header_serv.question_header_info(header_list)
        type_data = type_serv.questiontype_info(type_list)
        question_data = question_serv.question_info(question_list)
        list_data = NWisefinList()
        for obj in questiontype_obj:
            data_resp = QuestiontypemappResponse()
            data_resp.set_id(obj.id)
            data_resp.set_type_id(obj.type.id, type_data)
            data_resp.set_header(obj.header, header_data)
            data_resp.set_question_id(obj.question.id, question_data)
            data_resp.set_is_checked(obj.is_checked)
            list_data.append(data_resp)
        vpage = NWisefinPaginator(questiontype_obj, vys_page.get_index(), 10)
        list_data.set_pagination(vpage)
        return list_data

    def get_questiontype_mapping(self,id):
        obj = Questions_Typemapping.objects.using(self._current_app_schema()).get(id=id)
        data_resp = QuestiontypemappResponse()
        data_resp.set_id(obj.id)
        header_serv = QuestionheaderService(self._scope())
        header = header_serv.question_header_single_get_info(obj.header)
        data_resp.set_header_info(header)
        type_serv = QuestiontypeService(self._scope())
        type_id = type_serv.question_single_get(obj.type_id)
        data_resp.set_type(type_id)
        question_serv = QuestionService(self._scope())
        question_id = question_serv.question_singleget_info(obj.question_id)
        data_resp.set_question_info(question_id)
        data_resp.set_is_checked(obj.is_checked)
        return data_resp

    def create_questionflag(self,type_id,header_id):
        question_serv = QuestionService(self._scope())
        question_list = question_serv.get_type_basedquestions(type_id,header_id)
        if len(question_list)>0:
             for i in range(len(question_list)):
                is_question_exist=self.__exist_not(question_list[i],type_id,header_id)
                if is_question_exist:
                    continue
                else:
                    create_obj=Questions_Typemapping.objects.using(self._current_app_schema()).create(
                        type_id=type_id,header=header_id,question_id=question_list[i],entity_id=self._entity_id()
                    )

        return  True





    def __exist_not(self,question_id,type_id,header_id):
        query_obj=Questions_Typemapping.objects.using(self._current_app_schema()).filter(type_id=type_id,question_id=question_id,header=header_id)
        if len(query_obj)>0:
            return  True
        else:
            return  False

#DELETE_QUESTIONTYPEMAPPING
    def del_questiontype_mapping(self,id):
        obj = Questions_Typemapping.objects.using(self._current_app_schema()).filter(id=id, entity_id=self._entity_id()).update(status=ModifyStatus.delete)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj

    def question_mapping_is_checked(self, data):
        resp = NWisefinSuccess()
        question_type_obj = Questions_Typemapping.objects.using(self._current_app_schema()).filter(id=data.id).update(is_checked=data.is_checked)
        questiontype_mapping = Questions_Typemapping.objects.using(self._current_app_schema()).get(id=data.id)
        resp.set_message(SuccessMessage.UPDATE_MESSAGE)
        resp.set_status(SuccessStatus.SUCCESS)
        return resp


class Questionflagservices(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_flagmaster(self, data_obj,emp_id):
        resp = NWisefinSuccess()
        if not data_obj.get_id() is None:
            obj = Questions_flagmaster.objects.using(self._current_app_schema()).filter(id=data_obj.get_id()).update(questionmapping_id=data_obj.get_questionmapping_id(),
                                                                     ref_type=data_obj.get_ref_type(),
                                                                     ref_id=data_obj.get_ref_id(),
                                                                     entity_id=self._entity_id(),updated_by=emp_id)
            obj = Questions_flagmaster.objects.using(self._current_app_schema()).filter(id=data_obj.get_id(),entity_id=self._entity_id())

            resp.set_message(SuccessMessage.UPDATE_MESSAGE)
            resp.set_status(SuccessStatus.SUCCESS)

        else:
            obj = Questions_flagmaster.objects.using(self._current_app_schema()).create(
                 questionmapping_id=data_obj.get_questionmapping_id(),
                 ref_type=data_obj.get_ref_type(),
                 ref_id=data_obj.get_ref_id(),
                 entity_id=self._entity_id(),created_by=emp_id)

            resp.set_status(SuccessStatus.SUCCESS)
            resp.set_message(SuccessMessage.CREATE_MESSAGE)

        return resp
    def remove_flagmaster(self,data_obj,emp_id):

        obj = Questions_flagmaster.objects.using(self._current_app_schema()).filter(questionmapping_id=data_obj.get_questionmapping_id(),
            ref_type=data_obj.get_ref_type(),
            ref_id=data_obj.get_ref_id()).update(status=0)
        print(obj)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return  success_obj
    def fetch_flagmaster(self):
        flagmaster_obj = Questions_flagmaster.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())
        list_data = NWisefinList()
        for obj in flagmaster_obj:
            data_resp = QuestionflagResponse()
            data_resp.set_id(obj.id)
            data_resp.set_questionmapping_id(obj.questionmapping_id)
            data_resp.set_ref_id(obj.ref_id)
            data_resp.set_ref_type(obj.ref_type)
            list_data.append(data_resp)

        return list_data


    def get_flagmaster(self,id):
        obj = Questions_flagmaster.objects.using(self._current_app_schema()).get(id=id, entity_id=self._entity_id())
        data_resp = QuestionflagResponse()
        data_resp.set_id(obj.id)
        data_resp.set_ref_type(obj.ref_type)
        data_resp.set_ref_id(obj.ref_id)
        data_resp.set_questionmapping_id(obj.questionmapping_id)
        return data_resp

    def del_flagmaster(self,id):
        obj = Questions_flagmaster.objects.using(self._current_app_schema()).filter(id=id, entity_id=self._entity_id()).update(status=ModifyStatus.delete)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj


