import json
import datetime

from masterservice.service.questionheaderservice import QuestionheaderService
from masterservice.service.questiontypeservice import QuestiontypeService
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from vendorservice.data.response.questionanswerresponse import QuestionanswerResponse, QuestionsfilesResponse
from vendorservice.data.response.questionvendormappingresponse import Questionansmappingresponse
from vendorservice.models import Question_Answers, Questions_Queue, Question_vendor_mapping, Questions_files
from vendorservice.util.vendorutil import get_approving_level, Approving_level, Type_status, VendorOrActivityQueue
from masterservice.service.questionservice import QuestionService
from django.utils.timezone import now

class QuestionanswerService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)


    def question_answer_create(self,question_req,vendor_id,emp_id):
        resp = NWisefinSuccess()
        if not question_req.get_id() is None:
            obj = Question_Answers.objects.using(self._current_app_schema()).filter(id=question_req.get_id(), entity_id=self._entity_id()).update(question_id=question_req.get_question_id(),
                                                                                                                        type_id=question_req.get_type_id(),
                                                                                                                        vendor_id=vendor_id,
                                                                                                                        answer=question_req.get_answer(),updated_by=emp_id,
                                                                                                                        header_id=question_req.get_header_id(),
                                                                                                                        activity_id =question_req.get_activity_id())

            obj = Question_Answers.objects.using(self._current_app_schema()).get(id=question_req.get_id(),
                                                                                    entity_id=self._entity_id())

            Questions_Queue.objects.using(self._current_app_schema()).create(ref_id=vendor_id,ref_type=VendorOrActivityQueue.vendor,from_user_id=emp_id, to_user_id=emp_id,
                                                                             comments=Type_status.draft,
                                                                             remarks=question_req.get_remarks(),
                                                                             is_sys=True,
                                                                             entity_id=self._entity_id(),question_ans_id=obj.id)
        else:
            obj = Question_Answers.objects.using(self._current_app_schema()).create(question_id=question_req.get_question_id(),
                                                                                    type_id=question_req.get_type_id(),
                                                                                    vendor_id=vendor_id,
                                                                                    answer=question_req.get_answer(),
                                                                                    entity_id=self._entity_id(),
                                                                                    created_by=emp_id,
                                                                                    header_id=question_req.get_header_id(),
                                                                                    activity_id =question_req.get_activity_id())

            Questions_Queue.objects.using(self._current_app_schema()).create(ref_id=vendor_id,ref_type=VendorOrActivityQueue.vendor,from_user_id=emp_id, to_user_id=emp_id,
                                                                             comments=Type_status.draft,
                                                                             remarks=question_req.get_remarks(),
                                                                             is_sys=True,
                                                                             entity_id=self._entity_id(),question_ans_id=obj.id)
            resp = obj.id
        return obj

    def question_answer_create1(self, question_req, vendor_id, emp_id):
        resp = NWisefinSuccess()
        if not question_req.get_id() is None:
            obj = Question_Answers.objects.using(self._current_app_schema()).filter(id=question_req.get_id(),
                                                                                    entity_id=self._entity_id()).update(
                question_id=question_req.get_question_id(),
                type_id=question_req.get_type_id(),
                vendor_id=vendor_id,
                answer=question_req.get_answer(), updated_by=emp_id,
                header_id=question_req.get_header_id(),
                activity_id=question_req.get_activity_id())

            obj = Question_Answers.objects.using(self._current_app_schema()).get(id=question_req.get_id(),
                                                                                 entity_id=self._entity_id())

            Questions_Queue.objects.using(self._current_app_schema()).create(ref_id=vendor_id,
                                                                             ref_type=VendorOrActivityQueue.vendor,
                                                                             from_user_id=emp_id, to_user_id=emp_id,
                                                                             comments=Type_status.approve,
                                                                             remarks=question_req.get_remarks(),
                                                                             is_sys=True,
                                                                             entity_id=self._entity_id(),
                                                                             question_ans_id=obj.id)
        else:
            obj = Question_Answers.objects.using(self._current_app_schema()).create(
                question_id=question_req.get_question_id(),
                type_id=question_req.get_type_id(),
                vendor_id=vendor_id,
                answer=question_req.get_answer(),
                entity_id=self._entity_id(),
                created_by=emp_id,
                header_id=question_req.get_header_id(),
                activity_id=question_req.get_activity_id())

            Questions_Queue.objects.using(self._current_app_schema()).create(ref_id=vendor_id,
                                                                             ref_type=VendorOrActivityQueue.vendor,
                                                                             from_user_id=emp_id, to_user_id=emp_id,
                                                                             comments=Type_status.approve,
                                                                             remarks=question_req.get_remarks(),
                                                                             is_sys=True,
                                                                             entity_id=self._entity_id(),
                                                                             question_ans_id=obj.id)
            resp = obj.id
        return obj

    def upload(self,document_json,header_id,emp_id):
        arrdoc = []
        list_data = NWisefinList()
        if len(document_json) > 0:
            for doc_json in document_json:
                dtpcdocument = Questions_files.objects.using(self._current_app_schema()).create(
                    question_ans_id=header_id,
                    file_id=doc_json['id'],
                    file_name=doc_json['file_name'],
                    # gen_file_name=doc_json['gen_file_name'],
                    created_by=emp_id,entity_id=self._entity_id()
                )
            #
            # arrdoc.append(dtpcdocument)
                file_doc = QuestionsfilesResponse()
                file_doc.set_id(dtpcdocument.id)
                file_doc.set_question_ans_id(dtpcdocument.question_ans_id)
                file_doc.set_file_id(dtpcdocument.file_id)
                file_doc.set_file_name(dtpcdocument.file_name)
                list_data.append(file_doc)
            print("save")
            return list_data

    def fetch_question_answer(self,vys_page):
        question_obj = Question_Answers.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        list_data = NWisefinList()
        for obj in question_obj:
            data_resp = QuestionanswerResponse()
            data_resp.set_id(obj.id)
            data_resp.set_type_id(obj.type_id)
            data_resp.set_answer(obj.answer)
            data_resp.set_question_id(obj.question_id)
            data_resp.set_vendor_id(obj.vendor_id)
            data_resp.set_approving_level(obj.approving_level)
            # data_resp.set_header_id(QuestionService(self._scope()).header_function(obj.id))
            list_data.append(data_resp)
        vpage =NWisefinPaginator(question_obj, vys_page.get_index(), 10)
        list_data.set_pagination(vpage)
        return list_data

    def question_answer_get(self, id):
        question_obj = Question_Answers.objects.using(self._current_app_schema()).get(id=id)
        data_resp = QuestionanswerResponse()
        data_resp.set_id(question_obj.id)
        data_resp.set_answer(question_obj.answer)
        from utilityservice.service import api_service
        api_serv = api_service.ApiService(self._scope())
        data_resp.set_question_id(api_serv.get_questions(question_obj.question_id))
        data_resp.set_vendor_id(question_obj.vendor_id)
        data_resp.set_type_id(api_serv.get_question_type(question_obj.type_id))
        data_resp.set_approving_level(question_obj.approving_level)
        return data_resp


    def del_question_answer(self,id):
        question_obj = Question_Answers.objects.using(self._current_app_schema()).filter(id=id, entity_id=self._entity_id()).delete()
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj


    def get_answer_req(self,question_id):
        obj = Question_Answers.objects.using(self._current_app_schema()).filter(id=question_id)
        return obj


    def question_answer_get_val(self,vendor_id,question_id,type_id):
        obj = Question_Answers.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id, question_id=question_id,type_id=type_id,activity_id=False)
        list_data = []
        for x in obj:
            data_resp = QuestionanswerResponse()
            data_resp.set_id(x.id)
            data_resp.set_answer(x.answer)
            data_resp.set_question_id(x.question_id)
            data_resp.set_type_id(x.type_id)
            data_resp.set_vendor_id(x.vendor_id)
            data_resp.set_approving_level(x.approving_level)
            file_list = Questions_files.objects.using(self._current_app_schema()).filter(question_ans_id=x.id,status=1)
            filelist = []
            for fl in file_list:
                list_lent = len(file_list)
                if list_lent > 0:
                    dtpc_res = QuestionsfilesResponse()
                    dtpc_res.set_id(fl.id)
                    # dtpc_res.set_file_id(fl.file_id)
                    dtpc_res.set_file_name(fl.file_name)
                    filelist.append(dtpc_res)
                data_resp.set_file_data(filelist)
            # data_resp.set_header_id(QuestionService(self._scope()).header_function(x.id))
            list_data.append(data_resp)
        return list_data

    def question_answer_get_val1(self,vendor_id,question_id,type_id,activity_id):
        obj = Question_Answers.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id, question_id=question_id,type_id=type_id,activity_id=activity_id)
        list_data = []
        for x in obj:
            data_resp = QuestionanswerResponse()
            data_resp.set_id(x.id)
            data_resp.set_answer(x.answer)
            data_resp.set_question_id(x.question_id)
            data_resp.set_type_id(x.type_id)
            data_resp.set_vendor_id(x.vendor_id)
            data_resp.set_approving_level(x.approving_level)
            file_list = Questions_files.objects.using(self._current_app_schema()).filter(question_ans_id=x.id,status=1)
            filelist = []
            for fl in file_list:
                list_lent = len(file_list)
                if list_lent > 0:
                    dtpc_res = QuestionsfilesResponse()
                    dtpc_res.set_id(fl.id)
                    # dtpc_res.set_file_id(fl.file_id)
                    dtpc_res.set_file_name(fl.file_name)
                    filelist.append(dtpc_res)
                data_resp.set_file_data(filelist)
            # data_resp.set_header_id(QuestionService(self._scope()).header_function(x.id))
            list_data.append(data_resp)
        return list_data

    def answermapping(self, vendor_id,type_id):
        obj = Question_vendor_mapping.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id,question_type=type_id)
        list_data = []
        for x in obj:
            data_resp = Questionansmappingresponse()
            data_resp.set_id(x.id)
            data_resp.set_question_type(x.question_type)
            data_resp.set_period(x.period)
            # data_resp.set_periodicity(x.periodicity)
            data_resp.set_remarks(x.remarks)
            data_resp.set_type_status(x.type_status)
            data_resp.set_period_start(x.period_start)
            data_resp.set_period_end(x.period_end)
            # for reneval validation
            value = x.period_end
            month = int(value.month)
            year = int(value.year)
            today = datetime.datetime.now()
            if month == today.month and year == today.year:
                val = True
            else:
                val = False
            data_resp.set_expiry(val)
            data_resp.set_Activity(x.Activity)
            data_resp.set_vendor(x.vendor.id)
            list_data.append(data_resp)
        return list_data

    def answermapping1(self, vendor_id,type_id,activity_id):
        obj = Question_vendor_mapping.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id,question_type=type_id,Activity=activity_id)
        list_data = []
        for x in obj:
            data_resp = Questionansmappingresponse()
            data_resp.set_id(x.id)
            data_resp.set_question_type(x.question_type)
            data_resp.set_period(x.period)
            # data_resp.set_periodicity(x.periodicity)
            data_resp.set_remarks(x.remarks)
            data_resp.set_type_status(x.type_status)
            data_resp.set_period_start(x.period_start)
            data_resp.set_period_end(x.period_end)
            # for reneval validation
            value = x.period_end
            month = int(value.month)
            year = int(value.year)
            today = datetime.datetime.now()
            if month == today.month and year == today.year:
                val = True
            else:
                val = False
            data_resp.set_expiry(val)
            data_resp.set_Activity(x.Activity)
            data_resp.set_vendor(x.vendor.id)
            list_data.append(data_resp)
        return list_data


    def question_answer_activity_mapping(self,vendor_id,question_id,type_id,activity_id):
        obj = Question_Answers.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id, question_id=question_id,type_id=type_id,activity_id=activity_id)
        list_data = []
        for x in obj:
            data_resp = QuestionanswerResponse()
            data_resp.set_id(x.id)
            data_resp.set_answer(x.answer)
            data_resp.set_question_id(x.question_id)
            data_resp.set_type_id(x.type_id)
            data_resp.set_vendor_id(x.vendor_id)
            data_resp.set_approving_level(x.approving_level)
            data_resp.set_activity_id(x.activity_id)
            # data_resp.set_header_id(QuestionService(self._scope()).header_function(x.id))
            list_data.append(data_resp)
        return list_data

    def Delete_quesfiles(self,request, file_id, emp_id):
        try:
            Ecfhdr = Questions_files.objects.using(self._current_app_schema()).filter(file_id=file_id,entity_id=self._entity_id()).update(
                                                                      status=0,
                                                                      updated_by=emp_id,
                                                                      updated_date=now())
            ecf = Questions_files.objects.using(self._current_app_schema()).get(file_id=file_id)

            Questions_Queue.objects.using(self._current_app_schema()).create(ref_id=ecf.id,from_user_id=emp_id,
                                    to_user_id=emp_id,
                                    created_date=now(),
                                    comments="DELETE",
                                    is_sys=True,
                                    entity_id=self._entity_id()
                                    )
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            # success_obj.set_message(SuccessMessage.APPROVED_MESSAGE)
            return success_obj

        except Exception as ex:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(ex))
            return error_obj

    def ques_queuedetails(self,request,ecfhdr_id,type):
        ecf_que=Questions_Queue.objects.using(self._current_app_schema()).filter(ref_id=ecfhdr_id,entity_id=self._entity_id(),question_ans__type_id=type)
        print("queue",ecf_que)

        qudate=[]
        dupl_checklist=[]
        for i in ecf_que:
            date = i.created_date.date()
            if str(date) not in dupl_checklist:
                quedate = {
                    "created_date":str(date)
                }
                dupl_checklist.append(str(date))
                qudate.append(quedate)
        arr=[]
        for j in qudate:
            print("fldate",len(qudate))
            print("created_date ", j.get("created_date"))
            ecf_que1 = Questions_Queue.objects.using(self._current_app_schema()).filter(ref_id=ecfhdr_id,
                                                                                       entity_id=self._entity_id(),
                                                                                       question_ans__type_id=type,created_date__date=j.get("created_date"),comments=Type_status.approve)

            from utilityservice.service import api_service
            api_serv = api_service.ApiService(self._scope())
            headerservice = QuestionheaderService(self._scope())
            header = headerservice.fetch_questionheaderbased_type(type)
            type_serv = QuestiontypeService(self._scope())
            type_id = type_serv.question_single_get(type).__dict__
            queue = []
            for k in ecf_que1:
                print("header", k.question_ans.header_id)
                headers = api_serv.get_quesheader(k.question_ans.header_id).__dict__
                print("headers", headers)
                if len(ecf_que1) != 0:
                    ques = api_serv.get_questions(k.question_ans.question_id).__dict__
                    print("quesss", ques)
                else:
                    ques = {}
                ans = k.question_ans.id
                print("ans",ans)
                ansss = self.ques_queuefiles(ans)
                print("anssss",ansss)
                suboption = api_serv.get_subquestions(ques['id'])
                print("sub",suboption)
                answer_text = [{"answer":k.question_ans.answer,"file_data":ansss}]
                question = {"id": ques['id'], "text": ques['text'], "answer_text": answer_text,"header_id":headers,"input_type":ques['input_type'].__dict__,"sub_question":[],"Input_value":ques['sub_question'],"created_date":str(k.created_date.date())}
                queue.append(question)
            aa1={"type_id":type_id,"question_header":json.loads(header),"question":queue}
            arr.append(aa1)


        return {"date": qudate, "question_data": arr}


    def activity_queuedetails(self,request,activity_id,type):
        ecf_que=Questions_Queue.objects.using(self._current_app_schema()).filter(ref_id=activity_id,entity_id=self._entity_id(),question_ans__type_id=type, ref_type=VendorOrActivityQueue.activity)
        print("queue",ecf_que)

        qudate=[]
        dupl_checklist=[]
        for i in ecf_que:
            date = i.created_date.date()
            if str(date) not in dupl_checklist:
                quedate = {
                    "created_date":str(date)
                }
                dupl_checklist.append(str(date))
                qudate.append(quedate)
        arr=[]
        for j in qudate:
            print("fldate",len(qudate))
            print("created_date ", j.get("created_date"))
            ecf_que1 = Questions_Queue.objects.using(self._current_app_schema()).filter(ref_id=activity_id,
                                                                                       entity_id=self._entity_id(),
                                                                                       question_ans__type_id=type,created_date__date=j.get("created_date"),comments=Type_status.approve,ref_type=VendorOrActivityQueue.activity)

            from utilityservice.service import api_service
            api_serv = api_service.ApiService(self._scope())
            headerservice = QuestionheaderService(self._scope())
            header = headerservice.fetch_questionheaderbased_type(type)
            type_serv = QuestiontypeService(self._scope())
            type_id = type_serv.question_single_get(type).__dict__
            queue = []
            for k in ecf_que1:
                print("header", k.question_ans.header_id)
                headers = api_serv.get_quesheader(k.question_ans.header_id).__dict__
                print("headers", headers)
                if len(ecf_que1) != 0:
                    ques = api_serv.get_questions(k.question_ans.question_id).__dict__
                    print("quesss", ques)
                else:
                    ques = {}
                ans = k.question_ans.id
                print("ans",ans)
                ansss = self.ques_queuefiles(ans)
                print("anssss",ansss)
                suboption = api_serv.get_subquestions(ques['id'])
                print("sub",suboption)
                answer_text = [{"answer":k.question_ans.answer,"file_data":ansss}]
                question = {"id": ques['id'], "text": ques['text'], "answer_text": answer_text,"header_id":headers,"input_type":ques['input_type'].__dict__,"sub_question":[],"Input_value":ques['sub_question'],"created_date":str(k.created_date.date())}
                queue.append(question)
            aa1={"type_id":type_id,"question_header":json.loads(header),"question":queue}
            arr.append(aa1)


        return {"date": qudate, "question_data": arr}

    def ques_queuefiles(self,id):
        file_list = Questions_files.objects.using(self._current_app_schema()).filter(question_ans_id=id,status=1)
        filelist = []
        for fl in file_list:
            list_lent = len(file_list)
            if list_lent > 0:
                dtpc_res = QuestionsfilesResponse()
                dtpc_res.set_id(fl.id)
                # dtpc_res.set_file_id(fl.file_id)
                dtpc_res.set_file_name(fl.file_name)
                filelist.append(dtpc_res.__dict__)
        return filelist


    def activity_answer_create(self, question_req, activity_id, emp_id,vendor_id):
        resp = NWisefinSuccess()
        if not question_req.get_id() is None:
            obj = Question_Answers.objects.using(self._current_app_schema()).filter(id=question_req.get_id(),
                                                                                    entity_id=self._entity_id()).update(
                question_id=question_req.get_question_id(),
                type_id=question_req.get_type_id(),
                vendor_id=vendor_id,
                answer=question_req.get_answer(), updated_by=emp_id,
                header_id=question_req.get_header_id(),
                activity_id=activity_id)

            obj = Question_Answers.objects.using(self._current_app_schema()).get(id=question_req.get_id(),
                                                                                 entity_id=self._entity_id())

            Questions_Queue.objects.using(self._current_app_schema()).create(ref_id=activity_id,
                                                                             ref_type=VendorOrActivityQueue.activity,
                                                                             from_user_id=emp_id, to_user_id=emp_id,
                                                                             comments=Type_status.draft,
                                                                             remarks=question_req.get_remarks(),
                                                                             is_sys=True,
                                                                             entity_id=self._entity_id(),
                                                                             question_ans_id=obj.id)
        else:
            obj = Question_Answers.objects.using(self._current_app_schema()).create(
                question_id=question_req.get_question_id(),
                type_id=question_req.get_type_id(),
                vendor_id=vendor_id,
                answer=question_req.get_answer(),
                entity_id=self._entity_id(),
                created_by=emp_id,
                header_id=question_req.get_header_id(),
                activity_id=activity_id)

            Questions_Queue.objects.using(self._current_app_schema()).create(ref_id=activity_id,
                                                                             ref_type=VendorOrActivityQueue.activity,
                                                                             from_user_id=emp_id, to_user_id=emp_id,
                                                                             comments=Type_status.draft,
                                                                             remarks=question_req.get_remarks(),
                                                                             is_sys=True,
                                                                             entity_id=self._entity_id(),
                                                                             question_ans_id=obj.id)
            resp = obj.id
        return obj

    def activity_answer_create1(self, question_req, activity_id, emp_id, vendor_id):
        resp = NWisefinSuccess()
        if not question_req.get_id() is None:
            obj = Question_Answers.objects.using(self._current_app_schema()).filter(id=question_req.get_id(),
                                                                                    entity_id=self._entity_id()).update(
                question_id=question_req.get_question_id(),
                type_id=question_req.get_type_id(),
                vendor_id=vendor_id,
                answer=question_req.get_answer(), updated_by=emp_id,
                header_id=question_req.get_header_id(),
                activity_id=activity_id)

            obj = Question_Answers.objects.using(self._current_app_schema()).get(id=question_req.get_id(),
                                                                                 entity_id=self._entity_id())

            Questions_Queue.objects.using(self._current_app_schema()).create(ref_id=activity_id,
                                                                             ref_type=VendorOrActivityQueue.activity,
                                                                             from_user_id=emp_id, to_user_id=emp_id,
                                                                             comments=Type_status.approve,
                                                                             remarks=question_req.get_remarks(),
                                                                             is_sys=True,
                                                                             entity_id=self._entity_id(),
                                                                             question_ans_id=obj.id)
        else:
            obj = Question_Answers.objects.using(self._current_app_schema()).create(
                question_id=question_req.get_question_id(),
                type_id=question_req.get_type_id(),
                vendor_id=vendor_id,
                answer=question_req.get_answer(),
                entity_id=self._entity_id(),
                created_by=emp_id,
                header_id=question_req.get_header_id(),
                activity_id=activity_id)

            Questions_Queue.objects.using(self._current_app_schema()).create(ref_id=activity_id,
                                                                             ref_type=VendorOrActivityQueue.activity,
                                                                             from_user_id=emp_id, to_user_id=emp_id,
                                                                             comments=Type_status.approve,
                                                                             remarks=question_req.get_remarks(),
                                                                             is_sys=True,
                                                                             entity_id=self._entity_id(),
                                                                             question_ans_id=obj.id)
            resp = obj.id
        return obj