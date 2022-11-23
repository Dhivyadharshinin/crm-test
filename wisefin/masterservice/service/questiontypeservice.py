from django.db.models import Q
from django.utils import timezone

from masterservice.data.response.questiontyperesponse import QuestiontypeResponse
from masterservice.models import Question_Type, Question_Header
from userservice.service.moduleservice import ModuleService
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from masterservice.util.masterutil import ModifyStatus


class QuestiontypeService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)


    def create_question_type(self,questiontype, emp_id):
        resp = NWisefinSuccess()
        if not questiontype.get_id() is None:
            question_obj = Question_Type.objects.using(self._current_app_schema()).filter(id=questiontype.get_id(), entity_id=self._entity_id()
                                                                                          ).update(name=questiontype.get_name(),
                                                                                          remarks=questiontype.get_remarks(),
                                                                                          updated_by=emp_id,
                                                                                          updated_date=timezone.now(),
                                                                                          display_name=questiontype.get_display_name(),module_id=questiontype.get_module_id())


            question_obj = Question_Type.objects.using(self._current_app_schema()).get(id=questiontype.get_id(),entity_id=self._entity_id())
            resp.set_message(SuccessMessage.UPDATE_MESSAGE)
            resp.set_status(SuccessStatus.SUCCESS)


        else:
            question_obj = Question_Type.objects.using(self._current_app_schema()).create(name=questiontype.get_name(), created_by=emp_id,
                                                                                          updated_date=timezone.now(),remarks=questiontype.get_remarks(),
                                                                                          entity_id=self._entity_id(),display_name=questiontype.get_display_name(),module_id=questiontype.get_module_id())

            resp.set_status(SuccessStatus.SUCCESS)
            resp.set_message(SuccessMessage.CREATE_MESSAGE)
            resp.name = question_obj.name
            resp.id = question_obj.id
        return resp


    def fetch_question_type(self,vys_page,request,scope):
        query = request.GET.get('query')
        condtion = Q(entity_id=self._entity_id(),status=ModifyStatus.create)
        if query is not None and query !='':
            condtion &= Q(name__icontains=query)
        question_type = Question_Type.objects.using(self._current_app_schema()).filter(condtion).order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        module_arr = [i.module_id for i in question_type]
        module_serv = ModuleService(scope)
        module_data = module_serv.get_module_id(module_arr)
        list_data = NWisefinList()
        for obj in question_type:
            # print(obj)
            data_resp = QuestiontypeResponse()
            data_resp.set_id(obj.id)
            data_resp.set_name(obj.name)
            data_resp.set_remarks(obj.remarks)
            data_resp.set_display_name(obj.display_name)
            data_resp.set_module_id(obj.module_id, module_data)
            list_data.append(data_resp)
        vpage = NWisefinPaginator(question_type, vys_page.get_index(), 10)
        list_data.set_pagination(vpage)
        return list_data


    def get_question_type(self,id):
        questioin_type = Question_Type.objects.using(self._current_app_schema()).get(id=id)
        data_resp = QuestiontypeResponse()
        data_resp.set_id(questioin_type.id)
        data_resp.set_name(questioin_type.name)
        data_resp.set_remarks(questioin_type.remarks)
        data_resp.set_display_name(questioin_type.display_name)
        module_serv = ModuleService(self._scope())
        module = module_serv.get_single_module(questioin_type.module_id)
        data_resp.set_module(module)

        return data_resp

    def get_cmsquestion_type(self,id):
        questioin_type = Question_Type.objects.using(self._current_app_schema()).filter(id__in=id)
        return questioin_type

    def del_question_type(self, id):
        question_type = Question_Type.objects.using(self._current_app_schema()).filter(id=id, entity_id=self._entity_id()).update(status=ModifyStatus.delete)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj

    # def question_type_info(self,data_obj):
    #     question_type_id = data_obj['id']
    #     obj = Question_Type.objects.using(self._current_app_schema()).get(type_id=question_type_id)
    #
    def question_type_info(self, type_id):
        # type_id = data_obj['type_id']
        obj = Question_Type.objects.using(self._current_app_schema()).get(id=type_id)
        resp = QuestiontypeResponse()

        # question_type
        question_type_serv = QuestiontypeService(self._scope())
        c = question_type_serv.get_question_type(obj.id)

        # question_header
        from masterservice.service.questionheaderservice import QuestionheaderService
        question_header = QuestionheaderService(self._scope())
        v = question_header.header_based_question(obj.id)

        # question
        # question_serv = QuestionService(self._scope())
        # w = question_serv.get_question_info(obj.id)
        c.question_header = v
        # c.question = w
        resp.set_data(c)
        return resp


    def questiontype_info(self,type_id):
        obj = Question_Type.objects.using(self._current_app_schema()).filter(id__in=type_id)
        arr = []
        for x in obj:
            data_resp = QuestiontypeResponse()
            data_resp.set_id(x.id)
            data_resp.set_name(x.name)
            data_resp.set_module(x.module_id)
            # data_resp.set_remarks(x.remarks)
            # data_resp.set_display_name(x.display_name)
            arr.append(data_resp)
        return arr

    def question_single_get(self,type_id):
        obj = Question_Type.objects.using(self._current_app_schema()).filter(id=type_id)
        if len(obj)!=0:
            data_resp = QuestiontypeResponse()
            data_resp.set_id(obj[0].id)
            data_resp.set_name(obj[0].name)
            data_resp.set_module(obj[0].module_id)
            return data_resp