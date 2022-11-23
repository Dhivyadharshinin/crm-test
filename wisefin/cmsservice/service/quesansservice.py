import traceback

from django.db.models import Q

from cmsservice.data.response.quesansresponse import Quesansresponse, Quesansmapresponse, Answermapresponse, \
    Quesclassifyresponse, Questionansmapresponse,AnswerEvaluatorresponse
from cmsservice.models import QuestionAnswers, CMSQuestionAnswer, AnswerMapping, QuestionClassification, \
    QuestionProjectMapping,ProposedContract, CMSDocuments, QuestionaireTranComments
from django.utils.timezone import now
from cmsservice.service.cmscommonservice import VowCommonService,CommonService
from cmsservice.util.cmsutil import ActiveStatus, get_commentsreftype, DocUtil, ApprovalStatus, AnswerRefType,\
    get_question_input_type, HistoryStatus,CommentsRefTypeUtil
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.service.utilityservice import NWisefinUtilityService
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess
from utilityservice.service import cms_api_service
from docservice.service.documentservice import VowDocumentsService
from docservice.util.docutil import DocModule
import pandas as pd
import numpy as np
import json

utilityservice=NWisefinUtilityService()
class Quesansservice(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.CMS_SERVICE)

    def createquesans(self,request,ans_data,emp_id):
        proposal_id = request.GET.get('proposal_id', None)
        q_type= request.GET.get('q_type',None)
        if (proposal_id == None) or (q_type == None):
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(ErrorMessage.INVALID_REQUEST_ID)
            return error_obj

        # QuestionClassification
        classify_obj = QuestionClassification.objects.using(self._current_app_schema()).filter(classify_id=proposal_id,classify_type=DocUtil.proposer,status=ActiveStatus.Active,question_type=q_type)

        if len(classify_obj) == 0:
            q_classification = QuestionClassification.objects.using(self._current_app_schema()).create(classify_id=proposal_id,classify_type=DocUtil.proposer,   question_type=q_type)
            classify_id = q_classification.id
            approval_status = q_classification.approval_status
        else:
            classify_id = classify_obj[0].id
            approval_status = classify_obj[0].approval_status

        if approval_status == HistoryStatus.APPROVED:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.PERMISSION_DENIED)
            error_obj.set_description(ErrorDescription.PERMISSION_DENIED)
            return error_obj
        arr = []
        for ans_obj in ans_data:
            if (approval_status == HistoryStatus.DRAFT) or (approval_status is None):
                if ans_obj.get_id() is not None:
                    update = QuestionAnswers.objects.using(self._current_app_schema()).filter(id=ans_obj.get_id()).update(
                                          answer=ans_obj.get_answer(),
                                          option_type=ans_obj.get_option_type(),
                                          option_id=ans_obj.get_option_id())
                else:
                    ans = QuestionAnswers(question_id=ans_obj.get_question_id(),
                                          question_type=q_type,
                                          answer=ans_obj.get_answer(),
                                          option_type=ans_obj.get_option_type(),
                                          option_id=ans_obj.get_option_id(),
                                          ref_type=AnswerRefType.supplier,
                                          ref_id=ans_obj.get_ref_id(),
                                          classify_id=classify_id,
                                          created_by=emp_id)
                    arr.append(ans)
            elif approval_status == HistoryStatus.REVIEW:
                if ans_obj.get_id() is not None:
                    previous_data = QuestionAnswers.objects.using(self._current_app_schema()).get(id=ans_obj.get_id())
                    # data = {'classify': previous_data.classify_id, 'question_id': previous_data.question_id,
                    #         'question_type': previous_data.question_type, 'answer': previous_data.answer,
                    #         'option_type': previous_data.option_type, 'option_id': previous_data.option_id}
                    com_serv = CommonService(self._scope())
                    data = com_serv.obj_to_dict_conversion(previous_data)
                    history_id = com_serv.insert_update_ref_data(data,previous_data.id, DocUtil.Questionnaire, emp_id)
                    update = QuestionAnswers.objects.using(self._current_app_schema()).filter(id=ans_obj.get_id()
                                                                                              ).update(
                        is_ref=True, update_refid=history_id, answer=ans_obj.get_answer())
                else:
                    ans = QuestionAnswers(question_id=ans_obj.get_question_id(),
                                          question_type=q_type,
                                          answer=ans_obj.get_answer(),
                                          option_type=ans_obj.get_option_type(),
                                          option_id=ans_obj.get_option_id(),
                                          ref_type=AnswerRefType.supplier,
                                          ref_id=ans_obj.get_ref_id(),
                                          classify_id=classify_id,
                                          created_by=emp_id,
                                          is_ref=True,
                                          update_refid=-1)
                    arr.append(ans)
        QuestionAnswers.objects.using(self._current_app_schema()).bulk_create(arr)
        success_obj = NWisefinSuccess()
        success_obj.set_status("Success")
        success_obj.set_message("Created Successfully")
        return success_obj

    def fetch_classify(self,request,classify_id):
        quesclass = QuestionClassification.objects.using(self._current_app_schema()).get(id=classify_id)
        api_serv = cms_api_service.ApiService(self._scope())
        class_data = Quesclassifyresponse()
        class_data.set_classify_id(quesclass.classify_id)
        class_data.set_classify_type(get_commentsreftype(quesclass.classify_type))
        class_data.set_question_type(api_serv.get_ques_id(quesclass.question_type))
        return class_data

    def fetch_ans_list(self,request,question_id,question_type,vys_page,emp_id):
        try:
            condition = Q(status=ActiveStatus.Active) & Q(question_type=question_type)
            ans = QuestionAnswers.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')
            list_len = len(ans)
            question_arr = []
            ans_list_data = NWisefinList()
            if list_len > 0:
                for i in ans:
                    api_serv = cms_api_service.ApiService(self._scope())
                    ans_data = Quesansresponse()
                    ans_data.set_id(i.id)
                    if i.question_id != None:
                        ans_data.set_question_id(api_serv.get_ques_id(i.question_id))
                    ans_data.set_answer(i.answer)
                    ans_data.set_option_type(i.option_type)
                    ans_data.set_option_id(i.option_id)
                    ans_data.set_ref_type(i.ref_type)
                    ans_data.set_ref_id(i.ref_id)
                    ans_data.set_classify_id(api_serv.get_classify_id(request, i.classify_id))
                    question_arr.append(ans_data)
                    if i.question_type != None:
                        quey_type = api_serv.get_questype_id(i.question_type)
                        ans_list_data.append({"type_id": quey_type, "question": question_arr})
                return ans_list_data
        except Exception as ex:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(ex))
            return error_obj

    def createquesansmap(self,ans_obj,emp_id):
        try:
            ans = CMSQuestionAnswer.objects.using(self._current_app_schema()).create(
                                                answer_id=ans_obj.get_answer_id(),
                                                type_id = ans_obj.get_type_id(),
                                                subtype_id = ans_obj.get_subtype_id(),
                                                reftype_id = ans_obj.get_reftype_id(),
                                                ref_id =ans_obj.get_ref_id(),
                                                created_by=emp_id,
                                                created_date=now())


            ans_data = Quesansmapresponse()
            ans_data.set_id(ans.id)
            ans_data.set_answer_id(ans.answer_id)
            ans_data.set_type_id(ans.type_id)
            ans_data.set_subtype_id(ans.subtype_id)
            ans_data.set_reftype_id(ans.reftype_id)
            ans_data.set_ref_id(ans.ref_id)
            return ans_data

        except Exception as ex:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(ex))
            return error_obj

    def createansmap(self,ans_obj,emp_id):
        arr = []
        for ans_data in ans_obj:
            if not ans_data.get_id() is None:
                AnswerMapping.objects.using(self._current_app_schema()).filter(id=ans_data.get_id()).update(answer_id=ans_data.get_answer_id(),
                                                    ref_type = DocUtil.proposer,
                                                    ref_id = ans_data.get_ref_id(),
                                                    comments = ans_data.get_comments(),
                                                    score = ans_data.get_score(),
                                                    red_flag = ans_data.get_red_flag(),
                                                    updated_by=emp_id,
                                                    updated_date=now())

            else:
                ans = AnswerMapping(
                    answer_id=ans_data.get_answer_id(),
                    ref_type=DocUtil.proposer,
                    ref_id=ans_data.get_ref_id(),
                    comments=ans_data.get_comments(),
                    score=ans_data.get_score(),
                    red_flag=ans_data.get_red_flag(),
                    created_by=emp_id)

                arr.append(ans)

        if len(arr)>0:
            AnswerMapping.objects.using(self._current_app_schema()).bulk_create(arr)

        success_obj = NWisefinSuccess()
        success_obj.set_status("Success")
        success_obj.set_message("Created Successfully")
        return success_obj

    def fetch_evaluation(self,request,ref_id,type_id):
        condition = Q(ref_id=ref_id,question_type=type_id)
        quesclass1 = QuestionAnswers.objects.using(self._current_app_schema()).filter(condition).values_list("id",flat=True)

        quesclass2 = AnswerMapping.objects.using(self._current_app_schema()).filter(answer_id__in=quesclass1,status=ActiveStatus.Active)
        arr=NWisefinList()
        for i in quesclass2:
            eval = Answermapresponse()
            eval.set_id(i.id)
            eval.set_comments(i.comments)
            eval.set_answer_id(i.answer_id)
            eval.set_red_flag(i.red_flag)
            arr.append(eval)
        return arr

    def createquesclassify(self,ans_obj,emp_id):
        try:
            ans = QuestionClassification.objects.using(self._current_app_schema()).create(
                                                classify_id=ans_obj.get_classify_id(),
                                                question_type = ans_obj.get_question_type(),
                                                classify_type = ans_obj.get_classify_type(),
                                                created_by=emp_id,
                                                created_date=now())


            ans_data = Quesclassifyresponse()
            ans_data.set_id(ans.id)
            ans_data.set_classify_id(ans.classify_id)
            ans_data.set_classify_type(ans.classify_type)
            ans_data.set_question_type(ans.question_type)
            return ans_data

        except Exception as ex:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(ex))
            return error_obj

    def createquesprojmap(self,ans_data,project_id,emp_id):
        arr=[]
        for typeid in ans_data:
            ans = QuestionProjectMapping(project_id = project_id,
                                                type_id = typeid,
                                                created_by=emp_id)
            arr.append(ans)

        QuestionProjectMapping.objects.using(self._current_app_schema()).bulk_create(arr)

        success_obj = NWisefinSuccess()
        success_obj.set_status("Success")
        success_obj.set_message("Created Successfully")
        return success_obj

    def fetch_projquesmap(self,pro_id):
        quesclass = QuestionProjectMapping.objects.using(self._current_app_schema()).filter(project_id=pro_id).values_list('type_id',flat=True)
        print(quesclass)
        return quesclass

    def projectquestion(self,request, pro_id):
        proposal_id = request.GET.get('proposal_id')
        q_type_id= request.GET.get('q_type',None)

        if proposal_id != None:
            proposal_id=int(proposal_id)
        else:
            proposal_id=-1

        api_serv = cms_api_service.ApiService(self._scope())
        # project - question type
        questype = api_serv.get_proquesmap_id(pro_id)
        if q_type_id == None:
            q_type = api_serv.get_questype(questype)
        else:
            q_type=api_serv.get_questype([q_type_id])

        qheader_type = api_serv.get_quesheader_id(questype)
        data = api_serv.get_ques(questype)

        # classification id
        classification_obj=QuestionClassification.objects.using(self._current_app_schema()).filter(classify_id=proposal_id,classify_type=DocUtil.proposer,question_type__in=q_type)

        q_data, qid_arr, subq_data, subq_id_arr, subq_refid, ques_ids = [], [], [], [], [], []
        for q in data:
            # all question for sub_option
            ques_ids.append(q.id)
            # QUESTION
            if q.ref_id == None:
                q_data.append(q)
                qid_arr.append(q.id)
            # SUB QUESTION
            else:
                subq_data.append(q)
                subq_id_arr.append(q.id)
                subq_refid.append(q.ref_id)

        # sub_options
        cms_serv = cms_api_service.ApiService(self._scope())
        sub_option_data = cms_serv.get_ques_suboption(ques_ids)
        # QUESTIONS
        ans_resp = QuestionAnswers.objects.filter(question_id__in=qid_arr, classify__classify_type=DocUtil.proposer,classify__classify_id=proposal_id,status=ActiveStatus.Active)
        ansid_arr = [a.id for a in ans_resp]
        ans_comments=[]
        if len(ansid_arr)>0:
            ans_comments=AnswerMapping.objects.filter(answer_id__in=ansid_arr,status=ActiveStatus.Active)

        # SUBQUESTIONS
        subq_ans_resp = QuestionAnswers.objects.filter(question_id__in=subq_id_arr, classify__classify_type=DocUtil.proposer,classify__classify_id=proposal_id, status=ActiveStatus.Active)
        subq_ansid_arr = [a.id for a in subq_ans_resp]
        subq_ans_comments = []
        if len(ansid_arr) > 0:
            subq_ans_comments = AnswerMapping.objects.filter(answer_id__in=subq_ansid_arr, status=ActiveStatus.Active)

        answerid_arr=ansid_arr+subq_ansid_arr
        file_data=CommonService(request.scope).cms_multi_file(answerid_arr,DocUtil.Questionnaire)

        resp_list = NWisefinList()
        for j in q_type:
            approval_status=self.approval_status_key(classification_obj,j.id)
            can_comment=True
            # status=ApprovalStatus.DRAFT
            type = {"id": j.id, "name": j.name,"is_approver":approval_status,"status":approval_status,"can_comment":can_comment}
            header_obj = self.get_questionheader_info(j.id, qheader_type)
            q_arr=[]
            for i in q_data:
                if i.type_id == j.id:
                    data_resp = Questionansmapresponse()
                    data_resp.set_id(i.id)
                    data_resp.set_text(i.text)
                    data_resp.set_input_type(i.input_type)
                    data_resp.set_order(i.order)
                    data_resp.ans = self.get_answer(i.id, ans_resp,ans_comments,file_data,i.input_type, sub_option_data)
                    data_resp.sub_question=[]
                    if  i.id in subq_refid:
                        data_resp.sub_question=self.sub_question_opt(i.id,subq_data,subq_ans_resp,subq_ans_comments,file_data, sub_option_data)
                    q_arr.append(data_resp)
            d = {"type": type, "questions": q_arr, "header": header_obj}
            resp_list.append(d)
        return resp_list

    def approval_status_key(self,obj,type_id):
        approval_status=True
        for m in obj :
            if (m.question_type == type_id):
                approval_status=m.approval_status
        return approval_status

    def sub_question_opt(self,q_id,subq_data,ans_resp,ans_comments,input_data, sub_option_data):

        resp_list =[]
        for i in subq_data:
            if i.ref_id == q_id:
                data_resp = Questionansmapresponse()
                data_resp.set_id(i.id)
                data_resp.set_text(i.text)
                data_resp.set_input_type(i.input_type)
                data_resp.set_order(i.order)
                data_resp.ans = self.get_answer(i.id, ans_resp, ans_comments,input_data,i.input_type, sub_option_data)
                resp_list.append(data_resp)
        return resp_list

    def projectquestion2(self,request, pro_id):
        proposal_id = request.GET.get('proposal_id')
        if proposal_id != None:
            proposal_id=int(proposal_id)
        else:
            proposal_id=-1

        api_serv = cms_api_service.ApiService(self._scope())
        # project - question type
        questype = api_serv.get_proquesmap_id(pro_id)
        q_type = api_serv.get_questype(questype)
        qheader_type = api_serv.get_quesheader_id(questype)
        data = api_serv.get_ques(questype)
        qid_arr = [q.id for q in data]
        qid_arr = list(set(qid_arr))

        # question dataframe
        q_df=pd.DataFrame(data.values('text','type_id','id','input_type','ref_id'))
        q_df=q_df.rename({"id":"question_id"},axis=1)

        q_type_df=pd.DataFrame(q_type.values('id','name'))
        q_type_df=q_type_df.rename({"id":"questiontype_id"},axis=1)

        question_df =pd.merge(q_df,q_type_df,how='left',left_on=['type_id'],right_on=['questiontype_id'])
        print(question_df)

        # suboption dataframe
        suboption = api_serv.get_ques_suboption(qid_arr)

        suboption_df=pd.DataFrame(suboption.values('id','options','order'))
        suboption_df = suboption_df.rename({"id":"suboption_id"},axis=1)

        #  answer dataframe
        ans_resp = QuestionAnswers.objects.filter(question_id__in=qid_arr, classify__classify_type=DocUtil.proposer,classify__classify_id=proposal_id,status=ActiveStatus.Active)
        # ans_resp =ans_resp.values()
        ans_df = pd.DataFrame(ans_resp.values('id','question_id','question_type','answer','option_id','option_type'))
        ans_df = ans_df.rename({"id":"answer_id"},axis=1)

        ansid_arr = [a.id for a in ans_resp]
        ans_comments=[]
        if len(ansid_arr)>0:
            ans_comments=AnswerMapping.objects.filter(answer_id__in=ansid_arr,status=ActiveStatus.Active)

        if len(ans_comments)>0:
            ans_comments_df = pd.DataFrame(ans_comments.values('answer_id','comments','score','red_flag'))
        else:
            ans_comments_df = pd.DataFrame(columns=['answer_id','comments','score','red_flag'])
        print(ans_comments_df)
        answer_df = pd.merge(ans_df,ans_comments_df,how='left',left_on=['answer_id'],right_on=['answer_id'])

        answer_df = pd.merge(answer_df,suboption_df,how='left',left_on=['option_id'],right_on=['suboption_id'])
        print(answer_df)

        final_df =pd.merge(question_df,answer_df,how='left',left_on=['question_id'],right_on=['question_id'])
        print(final_df)
        # a=final_df.groupby(['question_id']).agg({'suboption_id': {"a":"suboption_id"}})

        # parent_question_df= final_df[final_df.ref_id.isnull()]
        # sub_question_df= final_df[~final_df.ref_id.isnull()]

       #  j = (final_df
       #       .apply(lambda x: x.to_dict('records')
       #       .reset_index()
       #       .rename(columns={0: 'sub_question'})
       #       .to_json(orient='records')))
       #
       #
       #  k=(final_df.groupby(['question_id'], as_index=False)
       # .apply(lambda x: dict(zip(x.type_id,x.order)))
       # .reset_index()
       # .rename(columns={"":'sub_question'})
       # .to_json(orient='records'))

        # final_df.loc[final_df['ref_id']==141, 'sub_question'] = final_df.to_dict('records')
        # final_df = final_df.assign(asd=lambda x: x.to_dict('records') if x['ref_id'] == 141 else None)
        final_df = final_df.assign(sub_question=np.where(final_df['ref_id'] != None ,final_df.to_dict('records') ))

        # j = (final_df.groupby(['question_id'])
        #      .apply(lambda x: x[['question_id', 'answer_id', 'ref_id', 'option_id', 'comments'] ] if(x.ref_id.isnull())else None).to_dict('records')
        #      .reset_index()
        #      .rename(columns={0: 'sub_question'})
        #      .to_json(orient='records'))
        return

    def get_questionheader_info(self, type_id, header_arr):
        arr = []
        for i in header_arr:
            if i.type_id == type_id:
                d = {"name": i.name, "order": i.order}
                arr.append(d)
        return arr

    def get_answer(self, q_id, ans_obj,ans_comments,file_data,input_type, sub_option_data):
        # ans_arr = []
        d=None
        for i in ans_obj:
            if i.question_id == q_id:
                comments, red_flag, comment_id = None, None, None

                for j in ans_comments:
                    if i.id == j.answer_id:
                        comments=j.comments
                        red_flag=j.red_flag
                        comment_id=j.id
                        break
                answer = i.answer
                if (i.option_type in [3, 4]) and (i.answer is not None):
                    answer = self.get_sub_option_by_id(i.answer, sub_option_data)
                d = {"id": i.id, "answer": answer, "option_type": i.option_type,"comments":comments,"red_flag":red_flag,"comment_id":comment_id}
                if input_type == get_question_input_type().FILE:
                    file_arr = [{"id": f.id, "file_name": f.file_name, "file_id": f.file_id} for f in file_data if
                                (f.rel_type == DocUtil.Questionnaire and f.rel_id == i.id)]
                    d['file']= file_arr
                break
                # ans_arr.append(d)
        return d

    def get_sub_option_by_id(self, sub_id, arr):
        for i in arr:
            if int(sub_id) == int(i.id):
                return i.options
        return ''

    def get_finalized_proposal(self,project_id):
        proposal_id=ProposedContract.objects.filter(project_id=project_id,status=ActiveStatus.Active,is_finalized=True,project__status=ActiveStatus.Active).values_list('id',flat=True)
        return proposal_id

    def get_finalized_proposal_info(self,project_id):
        proposal_obj=ProposedContract.objects.filter(project_id=project_id,status=ActiveStatus.Active,is_finalized=True,project__status=ActiveStatus.Active).values('id','name')
        return proposal_obj


    def fetch_final_evaluation(self,request,project_id):
        type_id =request.GET.get('type_id')
        api_serv = cms_api_service.ApiService(self._scope())
        # project type
        if type_id == None:
            questype = api_serv.get_proquesmap_id(project_id)
        else:
            questype =[int(type_id)]

        q_type = api_serv.get_questype(questype)
        qheader_type = api_serv.get_quesheader_id(questype)
        data = api_serv.get_ques(questype)
        qid_arr = [q.id for q in data]
        qid_arr = list(set(qid_arr))
        proposalid_arr=self.get_finalized_proposal(project_id)
        ans_resp = QuestionAnswers.objects.filter(question_id__in=qid_arr, classify__classify_type=DocUtil.proposer,classify__classify_id__in=proposalid_arr,status=ActiveStatus.Active)
        ansid_arr=[ans.id for ans in ans_resp]

        evaluator_cmt = AnswerMapping.objects.filter(id__in=ansid_arr,status=ActiveStatus.Active)

        resp_list = NWisefinList()
        for j in q_type:
            type = {"id": j.id, "name": j.name}
            header_obj = self.get_questionheader_info(j.id, qheader_type)
            q_arr = []
            for i in data:
                if i.type_id == j.id:
                    data_resp = Questionansmapresponse()
                    data_resp.set_id(i.id)
                    data_resp.set_text(i.text)
                    data_resp.set_input_type(i.input_type)
                    data_resp.set_order(i.order)
                    q_arr.append(data_resp)
            ans_arr=[]
            for a in ans_resp:
                if a.question_type == j.id:
                    data_resp = AnswerEvaluatorresponse()
                    data_resp.set_id(a.id)
                    data_resp.set_question_id(a.question_id)
                    data_resp.set_answer(a.answer)
                    data_resp.set_option_type(a.option_type)
                    cmt_obj=self.get_evalautor_comments(a.id,evaluator_cmt)
                    data_resp.comments=cmt_obj
                    ans_arr.append(data_resp)
            d = {"type": type, "questions": q_arr, "header": header_obj,"answer":ans_arr}
            resp_list.append(d)
        return resp_list

    def get_evalautor_comments(self,answer_id,arr):
        # ans_arr=[]
        for i in arr:
            if i.answer_id == answer_id:
                d={"comments":i.comments,"red_flag":i.red_flag,"comments_id":i.id}
                # ans_arr.append(d)
                return d
        d = {"comments": None, "red_flag": None, "comments_id": None}
        return d


    def get_final_evla(self,request,project_id):
        type_id = request.GET.get('type_id')
        api_serv = cms_api_service.ApiService(self._scope())
        # question
        question_obj=api_serv.get_question_id_by_type(type_id)
        question_df= pd.DataFrame(question_obj)

        proposal_id_arr=self.get_finalized_proposal(project_id)
        #answer
        ans_obj = QuestionAnswers.objects.filter( classify__classify_type=DocUtil.proposer,classify__classify_id__in=proposal_id_arr, status=ActiveStatus.Active,question_type=type_id).values()
        answer_df=pd.DataFrame(ans_obj)

        df1 = pd.merge(question_df, answer_df, how='left',left_on=['id'], right_on=['question_id'])
        print(df1)
        #comments

        return

    def approval_status_check(self,proposal_id):
        q_obj = QuestionClassification.objects.filter(classify_id=proposal_id,classify_type=CommentsRefTypeUtil.proposal,approval_status=ApprovalStatus.REVIEW)

        qtype_arr=[i.question_type for i in q_obj]
        # question type
        api_serv = cms_api_service.ApiService(self._scope())
        qtype =api_serv.get_questype(qtype_arr)
        # cmt
        QuestionaireTranComments.objects.filter()
        q_obj_arr=[{"text":i.name,"id":i.id,"remarks":None} for i in qtype]

        data = json.dumps(q_obj_arr,indent=4)
        return data

    # def test(self,vendor_id,proposal_id):
    #     proposal_obj = ProposedContract.objects.get(id=proposal_id)
    #     a=self.questionarier_to_vendor(proposal_obj,vendor_id)
    #     return a

    def questionarier_to_vendor(self,proposal_obj,vendor_id):
        proposal_id=proposal_obj.id
        q_obj = QuestionClassification.objects.filter(classify_id=proposal_id,
                                                      classify_type=CommentsRefTypeUtil.proposal,
                                                      approval_status=ApprovalStatus.APPROVED)

        qtype_arr = list(q_obj.values_list('question_type'))
        clf_arr = list(q_obj.values_list('id'))
        final_arr=[]

        rel_cat=proposal_obj.project.rel_cat
        criticality=proposal_obj.project.criticality
        vendor_type=proposal_obj.project.vendor_type
        api_serv = cms_api_service.ApiService(self._scope())
        vendor_clf_obj =api_serv.get_vendor_classification(rel_cat,criticality,vendor_type,qtype_arr)

        q_classify_df=pd.DataFrame(q_obj.values())
        q_classify_df=q_classify_df.rename({"id":"q_classify_id"},axis=1)
        vendor_classify_df=pd.DataFrame(vendor_clf_obj.values())

        if len(q_classify_df)==0 or len(vendor_classify_df)==0:
            # data1 = json.dumps(final_arr, indent=4)
            # return data1
            return final_arr

        final_df = pd.merge(q_classify_df,vendor_classify_df,how='left',left_on='question_type',right_on='type_id')
        final_dict=final_df.to_dict('records')
        # print(final_dict)
        ans_obj=QuestionAnswers.objects.filter(classify_id__in=clf_arr)
        for i in final_dict:

            final_data={"activity_flag": 0,
            "question_type": i['question_type'],
            "period": i['period'],
            # "period_start": i['period_start'],
            # "period_end": i['period_end'],
            "remarks": "",
            "type_status": 1,
            "vendor_id":vendor_id,
            "Activity": None}

            ans_data=[j  for j in ans_obj if j.classify_id == i['q_classify_id'] ]
            arr=[]
            for a in ans_data:
                d={
                    "question_id": a.question_id,
                    "type_id": a.question_type,
                    "answer": a.answer,
                    "sub_question": [],
                    "header_id": 2,
                    "activity_id": "0",
                    "input_type": a.option_type,
                    "input_value": []
                }
                arr.append(d)
            final_data['answer']=arr
            final_arr.append(final_data)
        print(final_arr)

        # data1 = json.dumps(final_arr,indent=4)
        # return data1
        return final_arr

from userservice.controller.vowusercontroller import VowUser
class VowQuesansService:
    def __init__(self,request):
        vowuser_info = VowUser().get_user(request)
        self.emp_id = vowuser_info['user_id']
        self.entity_id = vowuser_info['entity_id']
        self.is_user = vowuser_info['is_user']
        self.schema = vowuser_info['schema']

    def vow_createquesans(self,request,qans_obj,project_id):
        # classify_id
        proposal_code= request.GET.get('proposer_code',None)
        q_type= request.GET.get('q_type',None)
        if (proposal_code == None) or (q_type == None):
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(ErrorMessage.INVALID_REQUEST_ID)
            return error_obj

        proposal_id=self.get_proposal_id(project_id,proposal_code)
        # QuestionClassification
        classify_obj=QuestionClassification.objects.using(self.schema).filter(classify_id=proposal_id,classify_type=DocUtil.proposer,status=ActiveStatus.Active,question_type=q_type)

        if len(classify_obj)==0:
            q_classification=QuestionClassification.objects.using(self.schema).create(classify_id=proposal_id,classify_type=DocUtil.proposer,question_type=q_type)

            classify_id =q_classification.id
        else:
            classify_id=classify_obj[0].id

        input_type = get_question_input_type()
        arr ,file_key= [],[]
        for ans_obj in qans_obj:
            if ans_obj.get_answer() is not None:
                option_type=ans_obj.get_option_type()
                if option_type in [input_type.CHECK_BOX,input_type.DROPDOWN,input_type.RADIO_BUTTON]:
                    option_id = int(ans_obj.get_answer())
                else:
                    option_id=None

                # file
                if input_type.FILE ==option_type:
                    question_id=ans_obj.get_question_id()
                    qa_obj=QuestionAnswers.objects.using(self.schema).create(question_id=question_id,
                                                                             question_type=q_type,
                                                                             answer=ans_obj.get_answer(),
                                                                             option_type=option_type,
                                                                             option_id=option_id,
                                                                             ref_type=AnswerRefType.supplier,
                                                                             classify_id=classify_id,
                                                                             created_by=self.emp_id,
                                                                             is_user=self.is_user)
                    k="file_"+str(question_id)
                    file_key_data={"file_key":k,"answer_id":qa_obj.id}
                    file_key.append(file_key_data)
                    continue
                else:
                    ans = QuestionAnswers(question_id=ans_obj.get_question_id(),
                                          question_type=q_type,
                                          answer=ans_obj.get_answer(),
                                          option_type= option_type,
                                          option_id=option_id,
                                          ref_type=AnswerRefType.supplier,
                                          # ref_id=ans_obj.get_ref_id(),
                                          classify_id=classify_id,
                                          created_by=self.emp_id,is_user=self.is_user)
                    arr.append(ans)

        if len(file_key)>0:
            self.questionnaire_file_upload(file_key,request)

        QuestionAnswers.objects.using(self.schema).bulk_create(arr)

        success_obj = NWisefinSuccess()
        success_obj.set_status("Success")
        success_obj.set_message("Created Successfully")
        return success_obj

    def questionnaire_file_upload(self,arr,request):
        attach_type=DocUtil.Questionnaire
        doc_service = VowDocumentsService(request)
        common_service = VowCommonService(request)
        docmodule_obj = DocModule()
        for i in arr:
            file_key=i['file_key']
            answer_id=i['answer_id']
            params = {"module": docmodule_obj.CMS, "ref_id": answer_id, "ref_type": DocUtil.Questionnaire}

            try:
                if not request.FILES[file_key] is None:
                    resp_obj = doc_service.vow_document_upload_key(request, params, file_key)
                    document_json = json.loads(resp_obj.get())['data']
                    type = -1
                    common_service.updateprojectattachement(document_json, answer_id, attach_type, type)
            except:
                pass
        return




    def prop_createquesans(self, request, ans_obj, proposal_id, q_type):
        api_serv = cms_api_service.CmsCommonService(request)
        pro_id = api_serv.get_project(proposal_id)
        ab=pro_id[0].project_id
        if q_type == None:
            questype = api_serv.get_proquesmap(ab)
        else:
            questype = [q_type]
        data = api_serv.vow_get_ques(questype)
        arr = []
        for i in data:
            ques_id = i.id
            arr.append(ques_id)

        for t in questype :
            classify_obj = QuestionClassification.objects.using(self.schema).filter(classify_id=proposal_id,classify_type=DocUtil.proposer,status=ActiveStatus.Active,question_type=t)
            if len(classify_obj) == 0:
                q_classification = QuestionClassification.objects.using(self.schema).create(classify_id=proposal_id, classify_type=DocUtil.proposer, question_type=t)
                classify_id = q_classification.id
            else:
                classify_id = classify_obj[0].id

            q_arr = []
            answer = ans_obj['answer']
            # option_type = ans_obj[0].get_option_type(),
            # option_id = ans_obj[0].get_option_id(),
            ref_id = ans_obj['ref_id']
            for j in arr:
                ans = QuestionAnswers(question_id=j,
                                      question_type=q_type,
                                      answer=answer,
                                      option_type=None,
                                      option_id=None,
                                      ref_type=AnswerRefType.supplier,
                                      ref_id=ref_id,
                                      classify_id=classify_id,
                                      created_by=self.emp_id, is_user=self.is_user)
                q_arr.append(ans)

            QuestionAnswers.objects.using(self.schema).bulk_create(q_arr)

        success_obj = NWisefinSuccess()
        success_obj.set_status("Success")
        success_obj.set_message("Created Successfully")
        return success_obj

    def vow_fetch_ans_list(self,request,question_type):
        condition = Q(status=ActiveStatus.Active) & Q(question_type=question_type)
        ans = QuestionAnswers.objects.using(self.schema).filter(condition).order_by('-created_date')
        ans_ids = [an.question_id for an in ans]
        input_type = get_question_input_type()
        doc_list = CMSDocuments.objects.using(self.schema).filter(rel_id__in=ans_ids, rel_type=DocUtil.Questionnaire)
        question_arr = []
        ans_list_data = NWisefinList()
        api_serv = cms_api_service.CmsCommonService(request)
        for i in ans:
            ans_data = Quesansresponse()
            ans_data.set_id(i.id)
            if i.question_id != None:
                ans_data.set_question_id(api_serv.fetch_Question(i.question_id))
            ans_data.set_answer(i.answer)
            ans_data.set_option_type(i.option_type)
            if i.option_type == input_type.FILE:
                file = self.get_file_data_in_arr(i.id, doc_list)
                ans_data.set_file(file)
            ans_data.set_classify_id(i.classify_id)
            ans_data.set_option_id(i.option_id)
            ans_data.set_ref_type(i.ref_type)
            ans_data.set_ref_id(i.ref_id)
            # ans_data.set_is_user(i.is_user)
            question_arr.append(ans_data)
        if i.question_type != None:
            quey_type = api_serv.fetch_Questype(i.question_type)
            ans_list_data.append({"type_id": quey_type, "question": question_arr})

        return ans_list_data

    def get_file_data_in_arr(self, rel_id, arr):
        list_data = []
        for i in arr:
            if rel_id == i.rel_id:
                file = {"id":i.id, "name":i.file_name}
                list_data.append(file)
        return list_data

    def vow_createquesansmap(self,ans_obj):
        try:
            ans = CMSQuestionAnswer.objects.using(self.schema).create(
                                                answer_id=ans_obj.get_answer_id(),
                                                type_id = ans_obj.get_type_id(),
                                                subtype_id = ans_obj.get_subtype_id(),
                                                reftype_id = ans_obj.get_reftype_id(),
                                                ref_id =ans_obj.get_ref_id(),
                                                is_user=self.is_user,
                                                created_by=self.emp_id,
                                                created_date=now())


            ans_data = Quesansmapresponse()
            ans_data.set_id(ans.id)
            ans_data.set_answer_id(ans.answer_id)
            ans_data.set_type_id(ans.type_id)
            ans_data.set_subtype_id(ans.subtype_id)
            ans_data.set_reftype_id(ans.reftype_id)
            ans_data.set_ref_id(ans.ref_id)
            return ans_data

        except Exception as ex:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(ex))
            return error_obj

    def vow_createansmap(self,ans_obj,ref_id,ref_type):
        arr=[]
        for ans_pro in ans_obj:
            ans = AnswerMapping(
                         answer_id=ans_pro.get_answer_id(),
                                                ref_type = ref_type,
                                                ref_id = ref_id,
                                                comments = ans_pro.get_comments(),
                                                score = ans_pro.get_score(),
                                                # is_user=self.is_user,
                                                created_by=self.emp_id,
                                                created_date=now())
            arr.append(ans)
        AnswerMapping.objects.using(self.schema).bulk_create(arr)
        success_obj = NWisefinSuccess()
        success_obj.set_status("Success")
        success_obj.set_message("Created Successfully")
        return success_obj

    def vow_quesclassify(self,ans_obj):
        try:
            ans = QuestionClassification.objects.using(self.schema).create(
                                                classify_id=ans_obj.get_classify_id(),
                                                question_type = ans_obj.get_question_type(),
                                                classify_type = ans_obj.get_classify_type(),
                                                is_user=self.is_user,
                                                created_by=self.emp_id)

            ans_data = Quesclassifyresponse()
            ans_data.set_id(ans.id)
            ans_data.set_classify_id(ans.classify_id)
            ans_data.set_classify_type(ans.classify_type)
            ans_data.set_question_type(ans.question_type)
            return ans_data

        except Exception as ex:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(ex))
            return error_obj

    def get_proposal_id(self,project_id,proposal_code):
        proposal_id=None
        cond=Q(project_id=project_id)&Q(proposer_code=proposal_code) &~Q(project__approval_status=ApprovalStatus.DRAFT)&Q(status=ActiveStatus.Active,project__status=ActiveStatus.Active)

        obj=ProposedContract.objects.using(self.schema).filter(cond)
        if len(obj)>0:
            proposal_id = obj[0].id

        return proposal_id

    def vow_projectquestion(self, request,pro_id):
        proposal_code= request.GET.get('proposer_code',None)
        proposal_id = self.get_proposal_id(pro_id,proposal_code)

        qclf_obj = QuestionClassification.objects.filter(classify_id=proposal_id,
                                                      classify_type=CommentsRefTypeUtil.proposal)

        api_serv = cms_api_service.CmsCommonService(request)
        questype = api_serv.get_proquesmap(pro_id)
        q_type = api_serv.vow_get_questype(questype)
        qheader_type = api_serv.vow_get_quesheader_id(questype)
        data = api_serv.vow_get_ques(questype)
        q_data , qid_arr , subq_data,subq_id_arr,subq_refid=[],[],[],[],[]
        for q in data:
            if q.ref_id == None:
                q_data.append(q)
                qid_arr.append(q.id)
            else:
                subq_data.append(q)
                subq_id_arr.append(q.id)
                subq_refid.append(q.ref_id)

        qid_arr = list(set(qid_arr))
        subq_id_arr = list(set(subq_id_arr))

        # suboption
        arr = qid_arr+subq_id_arr
        sub_option_data=api_serv.vow_question_suboption(arr)

        ans_resp = QuestionAnswers.objects.using(self.schema).filter(question_id__in=qid_arr, classify__classify_type=DocUtil.proposer, classify__classify_id=proposal_id)

        subq_ans_resp =QuestionAnswers.objects.using(self.schema).filter(question_id__in=subq_id_arr, classify__classify_type=DocUtil.proposer, classify__classify_id=proposal_id)

        if len(ans_resp)==0:
            is_answer=False
            answerid_arr=[]
        else:
            is_answer=True
            answer_id=[i.id for i in ans_resp]
            sub_answer_id=[i.id for i in subq_ans_resp]
            answerid_arr=answer_id+sub_answer_id

        file_data=VowCommonService(request).vow_multi_file(answerid_arr,DocUtil.Questionnaire)

        resp_list = NWisefinList()
        for j in q_type:
            # QUESTIONARY STATUS
            c_status= [m.approval_status for m in qclf_obj if m.question_type == j.id]
            if len(c_status)>0:
                status=c_status[0]
            else:
                status=None

            type = {"id": j.id, "name": j.name,"status":status}
            header_obj = self.get_questionheader_info(j.id, qheader_type)
            q_arr=[]
            for i in q_data:
                if i.type_id == j.id:
                    data_resp = Questionansmapresponse()
                    data_resp.set_id(i.id)
                    data_resp.set_text(i.text)
                    data_resp.set_input_type(i.input_type)
                    data_resp.set_order(i.order)
                    data_resp.set_sub_option(i.id,sub_option_data)
                    data_resp.ans = self.get_answer(i.id, ans_resp,file_data,i.input_type)
                    data_resp.sub_question=[]
                    if i.id in subq_refid:
                        data_resp.sub_question = self.get_sub_question_resp(i.id,subq_data,subq_ans_resp,sub_option_data,file_data)
                    q_arr.append(data_resp)
            d = {"type": type, "questions": q_arr, "header": header_obj,"is_answer":is_answer}
            resp_list.append(d)
        return resp_list

    def get_sub_question_resp(self,q_id,subq_data,subq_ans_resp,sub_option_data,file_data):
        resp_list = []
        for i in subq_data:
            if i.ref_id == q_id:
                data_resp = Questionansmapresponse()
                data_resp.set_id(i.id)
                data_resp.set_text(i.text)
                data_resp.set_input_type(i.input_type)
                data_resp.set_order(i.order)
                data_resp.set_sub_option(i.id, sub_option_data)
                data_resp.ans = self.get_answer(i.id, subq_ans_resp,file_data,i.input_type)
                resp_list.append(data_resp)
        return resp_list

    def get_questionheader_info(self, type_id, header_arr):
        arr = []
        for i in header_arr:
            if i.type_id == type_id:
                d = {"name": i.name, "order": i.order}
                arr.append(d)
        return arr

    def get_answer(self, q_id, ans_obj,file_data,input_type):
        # ans_arr = []
        d=None
        for i in ans_obj:
            if i.question_id == q_id:
                answer = i.answer
                if i.option_type in [3, 4] and (i.answer is not None):
                    answer = int(i.answer)

                d = {"id": i.id, "answer": answer, "option_type": i.option_type}

                if input_type == get_question_input_type().FILE:
                    file_arr=[{"id":f.id,"file_name":f.file_name} for f in file_data if (f.rel_type==DocUtil.Questionnaire and f.rel_id ==i.id) ]
                    d['file'] = file_arr

        return d
