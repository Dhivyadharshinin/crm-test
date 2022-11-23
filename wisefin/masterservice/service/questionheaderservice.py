import json

from django.db.models import Q

from masterservice.data.response.questionheaderresponse import QuestionheaderResponse
from masterservice.models import Question_Header
from masterservice.service.questiontypeservice import QuestiontypeService
from masterservice.util.masterutil import QuestionHeader
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from masterservice.util.masterutil import ModifyStatus

class QuestionheaderService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_question_header(self, question_header, emp_id):
        resp = NWisefinSuccess()

        if not question_header.get_id() is None:
            question_header_obj = Question_Header.objects.using(self._current_app_schema()).filter(id=question_header.get_id(), entity_id=self._entity_id()).update(name=question_header.get_name(),
                                                                                                                        type_id=question_header.get_type_id(),
                                                                                                                        # slno=question_header.get_slno(),
                                                                                                                        order=question_header.get_order(),
                                                                                                                        is_input=question_header.get_is_input(),
                                                                                                                        input_type=question_header.get_input_type(),
                                                                                                                        updated_by=emp_id)

            question_header_obj = Question_Header.objects.using(self._current_app_schema()).get(id=question_header.get_id(), entity_id=self._entity_id())
            resp.set_message(SuccessMessage.UPDATE_MESSAGE)
            resp.set_status(SuccessStatus.SUCCESS)

        else:
            obj = Question_Header.objects.using(self._current_app_schema()).create(name=question_header.get_name(),
                                                                                                   type_id=question_header.get_type_id(),
                                                                                                   # slno=question_header.get_slno(),
                                                                                                   order=question_header.get_order(),
                                                                                                   is_input=question_header.get_is_input(),
                                                                                                   input_type=question_header.get_input_type(),
                                                                                                   created_by=emp_id, entity_id=self._entity_id())
            obj.slno = QuestionHeader.SLNO +str(obj.id)
            obj.save()
            resp.set_message(SuccessMessage.CREATE_MESSAGE)
            resp.set_status(SuccessStatus.SUCCESS)
            resp.id = obj.id
            resp.name = obj.name

        return resp

    def fetch_questionheader(self, vys_page, request, scope):
        query = request.GET.get('query')
        condtion=Q(entity_id=self._entity_id(),status=ModifyStatus.create)
        if query is not None and query!='':
            condtion &=Q(name__icontains=query)
        questionheader_obj = Question_Header.objects.using(self._current_app_schema()).filter(condtion).order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        list_length=len(questionheader_obj)
        print(list_length)
        type_arr = [i.type.id for i in questionheader_obj]
        type_serv = QuestiontypeService(scope)
        type_data = type_serv.questiontype_info(type_arr)
        list_data = NWisefinList()
        for obj in questionheader_obj:
            data_resp = QuestionheaderResponse()
            data_resp.set_id(obj.id)
            data_resp.set_name(obj.name)
            # data_resp.set_slno(obj.slno)
            data_resp.set_order(obj.order)
            data_resp.set_is_input(obj.is_input)
            data_resp.set_input_type(obj.input_type)
            data_resp.set_type_id(obj.type.id,type_data)
            list_data.append(data_resp)
        vpage = NWisefinPaginator(questionheader_obj, vys_page.get_index(), 10)
        list_data.set_pagination(vpage)
        return list_data

    def fetch_questionheaderbased_type(self,type_id):
        questionheader_obj = Question_Header.objects.using(self._current_app_schema()).filter(type_id=type_id,status=ModifyStatus.create)
        list_data = list()
        for obj in questionheader_obj:
            data_resp = QuestionheaderResponse()
            data_resp.set_id(obj.id)
            data_resp.set_name(obj.name)
            # data_resp.set_slno(obj.slno)
            data_resp.set_order(obj.order)
            data_resp.set_is_input(obj.is_input)
            data_resp.set_input_type(obj.input_type)
            # data_resp.set_type_id(obj.type_id, self._scope())
            list_data.append(data_resp)
        resp=json.dumps(list_data,default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

        return resp

    def get_question_header(self, id):
        question_header = Question_Header.objects.using(self._current_app_schema()).get(id=id, entity_id=self._entity_id())
        data_resp = QuestionheaderResponse()
        data_resp.set_id(question_header.id)
        data_resp.set_name(question_header.name)
        # data_resp.set_slno(question_header.slno)
        data_resp.set_order(question_header.order)
        data_resp.set_input_type(question_header.input_type)
        data_resp.set_is_input(question_header.is_input)
        type_serv = QuestiontypeService(self._scope())
        type = type_serv.question_single_get(question_header.type_id)
        data_resp.set_type(type)

        return data_resp

    def del_question_header(self, id):
        question_header = Question_Header.objects.using(self._current_app_schema()).filter(id=id, entity_id=self._entity_id()).update(status=ModifyStatus.delete)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj

    def type_base_headername(self, request):
        type_id = request.GET.get('type_id')
        query = request.GET.get('query')
        condtion = Q(entity_id=self._entity_id())
        if type_id is not None and type_id != '':
            condtion &= Q(type_id=type_id)
        if query is not None and query !='':
            condtion &=Q(name__icontains=query)
        questionheader_obj=Question_Header.objects.using(self._current_app_schema()).filter(condtion)
        list_data = NWisefinList()
        for y in questionheader_obj:
            data_resp = QuestionheaderResponse()
            data_resp.set_id(y.id)
            data_resp.set_name(y.name)
            list_data.append(data_resp)
        return list_data

    # HEADER_BASED_QUESTION
    def header_based_question(self, id):
        question_type_obj = Question_Header.objects.using(self._current_app_schema()).filter(id=id,
                                                                                             entity_id=self._entity_id())
        list_data = NWisefinList()
        for obj in question_type_obj:
            data_resp = QuestionheaderResponse()
            data_resp.set_id(obj.id)
            data_resp.set_name(obj.name)
            data_resp.set_order(obj.order)
            # data_resp.set_slno(obj.slno)
            data_resp.set_input_type(obj.input_type)
            data_resp.set_is_input(obj.is_input)
            from masterservice.service.questionservice import QuestionService
            data_resp.set_question(QuestionService.get_question_info(self, obj.id))
            list_data.append(data_resp)
        return list_data

        # question_req = Question_Header.objects.using(self._current_app_schema()).filter(condtion).values_list('header_id',
        #                                                                                                 flat=True)
        # header_id = list(question_req)
        # print(header_id)
        # header_list = Question_Header.objects.using(self._current_app_schema()).filter(id__in=header_id)
        # print(header_list)
        # list_data = NWisefinList()
        # for obj in header_list:
        #     data_resp = QuestionheaderResponse()
        #     data_resp.set_id(obj.id)
        #     data_resp.set_name(obj.name)
        #     list_data.append(data_resp)
        # return list_data

    def question_header_info(self,header_id):
        obj = Question_Header.objects.using(self._current_app_schema()).filter(id__in=header_id)
        arr = []
        for x in obj:
            data_resp = QuestionheaderResponse()
            data_resp.set_id(x.id)
            data_resp.set_name(x.name)
            data_resp.set_type(x.type_id)
            arr.append(data_resp)
        return arr

    def question_header_single_get_info(self,header_id):
        obj = Question_Header.objects.using(self._current_app_schema()).filter(id=header_id)
        if len(obj)!=0:
            data_resp = QuestionheaderResponse()
            data_resp.set_id(obj[0].id)
            data_resp.set_name(obj[0].name)
            data_resp.set_type(obj[0].type_id)
            return data_resp


    def fetch_cmsquestionheader_type(self,type_id):
        questionheader_obj = Question_Header.objects.using(self._current_app_schema()).filter(type_id__in=type_id,status=ModifyStatus.create)
        return questionheader_obj
