from cmsservice.util.cmsutil import ActiveStatus
from masterservice.data.response.questionresponse import QuestionResponse
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from masterservice.models.mastermodels import QuestionGroupMapping, Questions, Question_Type, Question_Header


class Questioner_mapping(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def question_mapping_add(self,type_id,data,is_remove,employee_id):
        group_id = data["group_id"]
        if is_remove=="1":
            tab = QuestionGroupMapping.objects.filter(type_id=type_id, group_id__in=group_id).update(status=ActiveStatus.Delete)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.message = SuccessMessage.DELETE_MESSAGE
            return success_obj
        else:
            arr=[]
            for i in group_id:
                tab=QuestionGroupMapping.objects.filter(type_id=type_id,group_id=i,status=ActiveStatus.Active)
                if len(tab)==0:
                    obj=QuestionGroupMapping(type_id=type_id,group_id=i,created_by=employee_id)
                    arr.append(obj)
            QuestionGroupMapping.objects.bulk_create(arr)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.message = SuccessMessage.CREATE_MESSAGE
            return success_obj

    def question_group_get(self,type_id):
        data=QuestionGroupMapping.objects.filter(type_id=type_id)
        pr_list_data = NWisefinList()
        for i in data:
            data_resp = QuestionResponse()
            data_resp.set_id(i.id)
            data_resp.set_type_id(i.type.id)
            data_resp.set_group_id(i.group_id)
            pr_list_data.append(data_resp)
        return pr_list_data

    def projectquestion(self, pro_id):
        from utilityservice.service import cms_api_service
        from cmsservice.models.cmsmodels import QuestionAnswers
        ans_resp = QuestionAnswers.objects.filter(question_id=1, classify__classify_type=2,
                                                  classify__classify_id=pro_id)

        api_serv = cms_api_service.ApiService(self._scope())
        questype = api_serv.get_proquesmap_id(pro_id)
        q_type = Question_Type.objects.filter(id__in=questype)
        qheader_type = Question_Header.objects.filter(type_id__in=questype)
        data = Questions.objects.filter(type_id__in=questype)
        resp_list = NWisefinList()
        for j in q_type:
            type = {"id": j.id, "name": j.name}
            header_obj = self.get_questionheader_info(j.id, qheader_type)
            q_arr = []
            for i in data:
                if i.type_id == j.id:
                    data_resp = QuestionResponse()
                    data_resp.set_id(i.id)
                    data_resp.set_text(i.text)
                    data_resp.set_input_type(i.input_type)
                    data_resp.set_order(i.order)
                    data_resp.anser = self.get_answer(i.id, ans_resp)
                    q_arr.append(data_resp)
            d = {"type": type, "questions": q_arr, "header": header_obj}
            resp_list.append(d)
        return resp_list

    def get_questionheader_info(self, type_id, header_arr):
        arr = []
        for i in header_arr:
            if i.type_id == type_id:
                d = {"name": i.name, "order": i.order}
                arr.append(d)
        return arr

    def get_answer(self, q_id, ans_obj):
        ans_arr = []
        for i in ans_obj:
            if i.question_id == q_id:
                d = {"id": i.id, "answer": i.answer, "option_type": i.option_type}
                ans_arr.append(d)
        return ans_arr

from userservice.controller.vowusercontroller import VowUser
class VowQuesansprojService:
    def __init__(self,request):
        vowuser_info = VowUser().get_user(request)
        print(vowuser_info)
        self.emp_id = vowuser_info['user_id']
        self.entity_id = vowuser_info['entity_id']
        self.is_user = vowuser_info['is_user']
        self.schema = vowuser_info['schema']

    def vow_projectquestion(self,request,pro_id):
        from utilityservice.service import cms_api_service
        api_serv = cms_api_service.CmsCommonService(request)
        questype = api_serv.get_proquesmap(pro_id)
        q_type = Question_Type.objects.filter(id__in=questype)
        qheader_type = Question_Header.objects.filter(type_id__in=questype)
        data = Questions.objects.filter(type_id__in=questype)
        resp_list = NWisefinList()
        for j in q_type:
            type = {"id": j.id, "name": j.name}
            header_obj = self.vow_questionheader_info(j.id, qheader_type)
            q_arr = []
            for i in data:
                if i.type_id == j.id:
                    data_resp = QuestionResponse()
                    data_resp.set_id(i.id)
                    data_resp.set_text(i.text)
                    data_resp.set_input_type(i.input_type)
                    q_arr.append(data_resp)
            d = {"type": type, "questions": q_arr, "header": header_obj}
            resp_list.append(d)
        return resp_list

    def vow_questionheader_info(self, type_id, header_arr):
        arr = []
        for i in header_arr:
            if i.type_id == type_id:
                d = {"name": i.name, "order": i.order}
                arr.append(d)
        return arr