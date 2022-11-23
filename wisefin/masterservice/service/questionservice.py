import json
from django.db.models import Q
from django.http import HttpResponse
from masterservice.data.response.questionheaderresponse import QuestionheaderResponse
from masterservice.data.response.questionresponse import QuestionResponse
from masterservice.data.response.questionsubresponse import QuestionsubResponse
from masterservice.service.questionheaderservice import QuestionheaderService
from masterservice.service.questionsubservice import QuestionsubService
from masterservice.service.questiontypeservice import QuestiontypeService
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessMessage, SuccessStatus
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from masterservice.models.mastermodels import Questions, Question_Header, Questions_suboptions, Questions_Typemapping, \
    Questions_flagmaster
from masterservice.util.masterutil import ModifyStatus, VendorMapping


class QuestionService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)


    def create_question(self,question_req, emp_id,input_type):
        resp = NWisefinSuccess()
        create_arr = []
        print(question_req)
        if not question_req.get_id() is None:
                obj = Questions.objects.using(self._current_app_schema()).filter(id=question_req.get_id(), entity_id=self._entity_id()).update(text=question_req.get_text(),
                                                                                                              header_id=question_req.get_header_id(),
                                                                                                              type_id=question_req.get_type_id(),
                                                                                                              order=question_req.get_order(),
                                                                                                              input_type=input_type, updated_by=emp_id,
                                                                                                               ref_id=question_req.get_ref_id(),
                                                                                                               is_score=question_req.get_is_score(),
                                                                                                               min=question_req.get_min(),
                                                                                                               max=question_req.get_max()
                                                                                                              )

                obj = Questions.objects.using(self._current_app_schema()).get(id=question_req.get_id(),
                                                                             entity_id=self._entity_id())
                resp.set_message(SuccessMessage.UPDATE_MESSAGE)
                resp.set_status(SuccessStatus.SUCCESS)

        else:
            # for question in question_req:
            obj = Questions.objects.using(self._current_app_schema()).create(text=question_req.get_text(),
                          header_id=question_req.get_header_id(),
                          type_id=question_req.get_type_id(),
                          order=question_req.get_order(),
                          input_type=input_type, created_by=emp_id, entity_id=self._entity_id(), ref_id=question_req.get_ref_id(),is_score=question_req.get_is_score(),
                                                                                                               min=question_req.get_min(),
                                                                                                               max=question_req.get_max())

            resp.set_status(SuccessStatus.SUCCESS)
            resp.set_message(SuccessMessage.CREATE_MESSAGE)

        return obj.id

#FOR_QUESTIONSUB_OPTION_CREATE
    def create_question_info(self, question_req, emp_id, input_type, ref_id, header_id, type_id):
        resp = NWisefinSuccess()
        create_arr = []
        print(question_req)
        if not question_req.get_id() is None:
            obj = Questions.objects.using(self._current_app_schema()).filter(id=question_req.get_id(),
                                                                             entity_id=self._entity_id()).update(
                text=question_req.get_text(),
                header_id=header_id,
                type_id=type_id,
                order=question_req.get_order(),
                input_type=input_type, updated_by=emp_id,
                ref_id=ref_id,  is_score=question_req.get_is_score(),
                min=question_req.get_min(),
                max=question_req.get_max()
                )

            obj = Questions.objects.using(self._current_app_schema()).get(id=question_req.get_id(),
                                                                          entity_id=self._entity_id())
            resp.set_message(SuccessMessage.UPDATE_MESSAGE)
            resp.set_status(SuccessStatus.SUCCESS)

        else:
            # for question in question_req:
            obj = Questions.objects.using(self._current_app_schema()).create(text=question_req.get_text(),
                                                                             header_id=header_id,
                                                                             type_id=type_id,
                                                                             order=question_req.get_order(),
                                                                             input_type=input_type, created_by=emp_id,
                                                                             entity_id=self._entity_id(),
                                                                             ref_id=ref_id, is_score=question_req.get_is_score(),
                                                                             min=question_req.get_min(),
                                                                             max=question_req.get_max())

            resp.set_status(SuccessStatus.SUCCESS)
            resp.set_message(SuccessMessage.CREATE_MESSAGE)

        return obj.id

    def fetch_all_questions(self,is_type,is_header):
        condition=Q(status=ModifyStatus.create,entity_id=self._entity_id(), question__status=1, question__ref_id__isnull=True)
        if is_type:
            condition&=Q(type_id=is_type, question__header=is_header)
        question_obj = Questions_Typemapping.objects.using(self._current_app_schema()).filter(condition)
        list_data = NWisefinList()
        for obj in question_obj:
            relation_category, criticality, vendor_type = self.question_type_mapping(obj.id)
            sub_question = self.get_sub_question_arr(obj.question.id)
            data = {"id": obj.id, "header_id": obj.header, "text": obj.question.text, "question_id": obj.question.id, "is_check": obj.is_checked, "relation_category": relation_category, "criticality": criticality, "vendor_type": vendor_type,"sub_question":sub_question}

            list_data.append(data)
        return list_data


    def fetch_question(self,vys_page,request):
        query = request.GET.get('query')
        condtion = Q(entity_id=self._entity_id(), status=ModifyStatus.create, ref_id__isnull=True)
        if query is not None and query!='':
            condtion &= Q(type_id=query)
        question_obj = Questions.objects.using(self._current_app_schema()).filter(condtion).order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        header_list = []
        type_list = []
        for i in question_obj:
            header_id = i.header.id
            type_id = i.type_id
            header_list.append(header_id)
            type_list.append(type_id)
        header_serv = QuestionheaderService(self._scope())
        type_serv = QuestiontypeService(self._scope())
        header_data = header_serv.question_header_info(header_list)
        type_data = type_serv.questiontype_info(type_list)
        list_data = NWisefinList()
        for obj in question_obj:
            data_resp = QuestionResponse()
            data_resp.set_id(obj.id)
            data_resp.set_type_id(obj.type_id,type_data)
            data_resp.set_text(obj.text)
            data_resp.set_input_type(obj.input_type)
            data_resp.set_header_id(obj.header.id,header_data)
            data_resp.set_order(obj.order)
            data_resp.set_ref_id(obj.ref_id)
            # data_resp.set_sub_options(obj.sub_options)
            data_resp.set_sub_options(self.get_sub_question_arr(obj.id))
            data_resp.set_is_score(obj.is_score)
            data_resp.set_min(obj.min)
            data_resp.set_max(obj.max)
            list_data.append(data_resp)
        vpage = NWisefinPaginator(question_obj, vys_page.get_index(), 10)
        list_data.set_pagination(vpage)
        return list_data


    def get_question(self,id):
        obj = Questions.objects.using(self._current_app_schema()).get(id=id, entity_id=self._entity_id())
        data_resp = QuestionResponse()
        data_resp.set_id(obj.id)
        data_resp.set_text(obj.text)
        type_serv = QuestiontypeService(self._scope())
        type = type_serv.question_single_get(obj.type_id)
        data_resp.set_type(type)
        data_resp.set_input_type(obj.input_type)
        header_serv = QuestionheaderService(self._scope())
        header = header_serv.question_header_single_get_info(obj.header_id)
        data_resp.set_header(header)
        # data_resp.set_header_id(obj.header_id, self._scope())
        data_resp.set_order(obj.order)
        data_resp.set_ref_id(obj.ref_id)
        data_resp.set_sub_options(QuestionsubService.get_questionsuboptions(self, obj.id))
        data_resp.set_is_score(obj.is_score)
        data_resp.set_min(obj.min)
        data_resp.set_max(obj.max)
        return data_resp

    def get_cmsquestion(self,id):
        obj=Questions.objects.using(self._current_app_schema()).filter(type_id__in=id,status=ModifyStatus.create)
        # qid_arr=[q.question_id for q in qid_obj]
        #
        # obj = Questions.objects.using(self._current_app_schema()).filter(id__in=qid_arr, entity_id=self._entity_id())
        # for i in obj:
        #     for j in qid_obj:
        #         if j.question_id == i.id:
        #             i.type_id= j.type_id
        #             break
        # obj =[i.question for i in qid_obj]
        return obj

    def get_cms_subquestion(self,id):
        cond=Q(type_id__in=id,status=ModifyStatus.create)&~Q(ref_id=None)
        obj=Questions.objects.using(self._current_app_schema()).filter(cond)
        return obj

    def del_question_serv(self, id):
        obj = Questions.objects.using(self._current_app_schema()).filter(id=id, entity_id=self._entity_id()).update(status=ModifyStatus.delete)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj

    def get_question_req(self, question_id):
        obj = Questions.objects.using(self._current_app_schema()).filter(id=question_id)
        return obj

    def obj_dict(self,obj):
        return obj.__dict__


    def get_question_type(self, type_id,data):
        question_obj=Questions_Typemapping.objects.using(self._current_app_schema()).filter(type_id=type_id,entity_id=self._entity_id(),status=1,is_checked=1,question__ref_id__isnull=True)
        # question_obj = Questions.objects.using(self._current_app_schema()).filter(type_id=type_id,entity_id=self._entity_id(),status=1,ref_id__isnull=True)
        list_data = []
        for obj in question_obj:
            data_resp = QuestionResponse()

            # d=QuestiontypemappService(self._scope())
            relation_category,criticality,vendor_type=self.question_type_mapping(obj.id)
            # criticality = data['criticality'], vendor_type = data['vendor_type'], rel_cat = data['rel_cat']
            if data['criticality'] in criticality and data['vendor_type'] in vendor_type and data['rel_cat'] in relation_category:
                data_resp.set_id(obj.question.id)
                data_resp.set_question_mapping_id(obj.id)
                # type_serv = QuestiontypeService(self._scope())
                # type = type_serv.question_single_get(obj.type_id)
                # data_resp.set_type(type)
                # data_resp.set_type_id(obj.type_id, self._scope())
                data_resp.set_input_value(self.input_value(obj.question_id))
                data_resp.set_text(obj.question.text)
                data_resp.set_input_type(obj.question.input_type)
                header_serv = QuestionheaderService(self._scope())
                header = header_serv.question_header_single_get_info(obj.question.header_id)
                data_resp.set_header(header)
                # data_resp.set_header_id(obj.header_id, self._scope())
                data_resp.set_order(obj.question.order)
                # data_resp.set_sub_options(obj.sub_options)
                data_resp.set_sub_options(self.get_sub_question_arr(obj.question_id))
                data_resp.set_is_score(obj.question.is_score)
                data_resp.set_min(obj.question.min)
                data_resp.set_max(obj.question.max)
                list_data.append(data_resp)
            else:
                continue
            # response = HttpResponse(list_data.get(), content_type='application/json')
        json_string = json.dumps(list_data, default=self.obj_dict)
        return json_string

    def get_questions(self, id):
        obj = Questions.objects.using(self._current_app_schema()).get(id=id, entity_id=self._entity_id())
        # list_data = []
        # for i in obj:
        data_resp = QuestionResponse()
        data_resp.set_id(obj.id)
        data_resp.set_text(obj.text)
        type_serv = QuestiontypeService(self._scope())
        type = type_serv.question_single_get(obj.type_id)
        data_resp.set_type(type)
        # data_resp.set_type_id(obj.type_id, self._scope())
        data_resp.set_input_type(obj.input_type)
        # data_resp.set_header_id(obj.header_id, self._scope())
        header_serv = QuestionheaderService(self._scope())
        header = header_serv.question_header_single_get_info(obj.header_id)
        data_resp.set_header(header)
        data_resp.set_order(obj.order)
        data_resp.set_input_value(self.input_value(obj.id))
        data_resp.set_is_score(obj.is_score)
        data_resp.set_min(obj.min)
        data_resp.set_max(obj.max)
            # list_data.append(data_resp)

        return data_resp

    def get_question_info(self, type_id):
        question_obj = Questions.objects.using(self._current_app_schema()).filter(type_id=type_id,
                                                                                  entity_id=self._entity_id())
        list = []
        for obj in question_obj:
            data_resp = QuestionResponse()
            data_resp.set_id(obj.id)
            data_resp.set_order(obj.order)
            data_resp.set_text(obj.text)
            data_resp.set_input_type(obj.input_type)
            # data_resp.set_type_id(obj.type_id, self._scope())
            # type_serv = QuestiontypeService(self._scope())
            # type = type_serv.question_single_get(obj.type_id)
            # data_resp.set_type(type)
            # data_resp.set_header_id(obj.header_id, self._scope())
            # header_serv = QuestionheaderService(self._scope())
            # header = header_serv.question_header_single_get_info(obj.header_id)
            # data_resp.set_header(header)
            data_resp.set_sub_options(QuestionsubService.get_questionsuboptions(self, obj.id))
            data_resp.set_is_score(obj.is_score)
            data_resp.set_min(obj.min)
            data_resp.set_max(obj.max)
            list.append(data_resp)
        return list


    # def header_function(self,header_id):
    #     obj =Questions.objects.using(self._current_app_schema()).filter(header_id=header_id)
    #     list_data = []
    #     for x in obj:
    #         data_resp = QuestionResponse()
    #         data_resp.header_id(x.id)
    #         list_data.append(data_resp)
    #     return list_data

    def question_info(self,question_id):
        obj = Questions.objects.using(self._current_app_schema()).filter(id__in=question_id)
        list_data = []
        for x in obj:
            data_resp = QuestionResponse()
            data_resp.set_id(x.id)
            data_resp.set_text(x.text)
            # data_resp.set_group_id(x.group_id)
            data_resp.set_input_type(x.input_type)
            list_data.append(data_resp)
        return list_data

    def question_singleget_info(self, question_id):
        obj = Questions.objects.using(self._current_app_schema()).filter(id=question_id)
        if len(obj)!=0:
            data_resp = QuestionResponse()
            data_resp.set_id(obj[0].id)
            data_resp.set_text(obj[0].text)
            data_resp.set_input_type(obj[0].input_type)
            return data_resp

    def get_sub_question_arr(self, question_id):
        obj = Questions.objects.using(self._current_app_schema()).filter(ref_id=question_id)
        list_arr= []
        for x in obj:
            data_resp = QuestionResponse()
            data_resp.set_id(x.id)
            type_serv = QuestiontypeService(self._scope())
            type = type_serv.question_single_get(x.type_id)
            data_resp.set_type(type)
            header_serv = QuestionheaderService(self._scope())
            header = header_serv.question_header_single_get_info(x.header_id)
            data_resp.set_header(header)
            # data_resp.set_header(x.header.id)
            data_resp.set_text(x.text)
            data_resp.set_input_value(self.input_value(x.id))
            data_resp.set_input_type(x.input_type)
            data_resp.set_order(x.order)
            data_resp.set_is_score(x.is_score)
            data_resp.set_min(x.min)
            data_resp.set_max(x.max)
            list_arr.append(data_resp)
        return list_arr

    def input_value(self,id):
        arr = []
        obj = Questions_suboptions.objects.using(self._current_app_schema()).filter(question_id=id)
        for x in obj:
            data_resp = QuestionsubResponse()
            data_resp.set_id(x.id)
            data_resp.set_options(x.options)
            data_resp.set_order(x.order)
            arr.append(data_resp.__dict__)
        return arr
    def get_type_basedquestions(self, type_id,header_id):
        question_obj = list(Questions.objects.using(self._current_app_schema()).filter(type_id=type_id,header_id=header_id,
                                                              entity_id=self._entity_id(), status=1).values_list('id',flat=True))

        return question_obj

    def question_type_mapping(self,questionmapping_id):
        obj = Questions_flagmaster.objects.using(self._current_app_schema()).filter(questionmapping_id=questionmapping_id,status=ModifyStatus.create)
        relation_category=[]
        criticality=[]
        vendor_type =[]
        if len(obj)>0:
            for x in obj:
              if x.ref_type ==VendorMapping.relationship_category:
               relation_category.append(x.ref_id)
              elif x.ref_type == VendorMapping.criticality:
                  criticality.append(x.ref_id)
              elif x.ref_type == VendorMapping.vendor_type:
                  vendor_type.append(x.ref_id)
        return  relation_category,criticality,vendor_type



    def get_question_mapping(self, type_id,data):
            question_obj=Questions_Typemapping.objects.using(self._current_app_schema()).filter(type_id=type_id,entity_id=self._entity_id(),status=1,is_checked=1,question__ref_id__isnull=True)
            # question_obj = Questions.objects.using(self._current_app_schema()).filter(type_id=type_id,entity_id=self._entity_id(),status=1,ref_id__isnull=True)
            list_data = []
            for obj in question_obj:
                data_resp = QuestionResponse()
                # d=QuestiontypemappService(self._scope())
                relation_category,criticality,vendor_type=self.question_type_mapping(obj.id)
                # criticality = data['criticality'], vendor_type = data['vendor_type'], rel_cat = data['rel_cat']
                if data['rel_type'] in relation_category:
                    data_resp.set_id(obj.question_id)
                    data_resp.set_question_mapping_id(obj.id)
                    # type_serv = QuestiontypeService(self._scope())
                    # type = type_serv.question_single_get(obj.type_id)
                    # data_resp.set_type(type)
                    # data_resp.set_type_id(obj.type_id, self._scope())
                    data_resp.set_input_value(self.input_value(obj.question_id))
                    data_resp.set_text(obj.question.text)
                    data_resp.set_input_type(obj.question.input_type)
                    header_serv = QuestionheaderService(self._scope())
                    header = header_serv.question_header_single_get_info(obj.question.header_id)
                    data_resp.set_header(header)
                    # data_resp.set_header_id(obj.header_id, self._scope())
                    data_resp.set_order(obj.question.order)
                    # data_resp.set_sub_options(obj.sub_options)
                    # data_resp.set_sub_options(QuestionsubService.get_questionsuboptions2(self, obj.question.id))
                    data_resp.set_sub_options(QuestionService.get_sub_question_arr(self, obj.question_id))
                    data_resp.set_is_score(obj.question.is_score)
                    data_resp.set_min(obj.question.min)
                    data_resp.set_max(obj.question.max)
                    list_data.append(data_resp)

                # response = HttpResponse(list_data.get(), content_type='application/json')
            json_string = json.dumps(list_data, default=self.obj_dict)
            return json_string

    def get_sub_question_arr1(self, question_id):
        obj = Questions_suboptions.objects.using(self._current_app_schema()).filter(question_id=question_id)
        list_arr= []
        for x in obj:
            data_resp = QuestionResponse()
            data_resp.set_id(x.id)
            data_resp.set_input_value(self.input_value(x.id))
            list_arr.append(data_resp.__dict__)
        return list_arr
