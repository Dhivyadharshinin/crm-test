import traceback
from django.db.models import Q
from django.utils.timezone import now
from cmsservice.data.response.projectcmtresponse import Commentsresponse, CommentsReplyresponse
from cmsservice.models import TransactionComments, CMSDocuments
from cmsservice.util.cmsutil import ActiveStatus, DocUtil, CovernoteUtil
from cmsservice.util.cmsutil import CommentsUtil
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.cms_api_service import ApiService, CmsCommonService


class Commentservice(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.CMS_SERVICE)

    def createcmts(self, request, cmts_obj, ref_id, emp_id):
        ref_type = request.GET.get('ref_type')
        q_type = request.GET.get('q_type')
        cmts = TransactionComments.objects.using(self._current_app_schema()).create(
                                            ref_id=ref_id,
                                            ref_type=ref_type,
                                            comment=cmts_obj.get_comment(),
                                            type=cmts_obj.get_type(),
                                            q_type=q_type,
                                            created_by=emp_id,
                                            created_date=now())
        return cmts

    def fetch_cmts_list(self, request, vys_page, ref_id):
        q_type = request.GET.get('q_type')
        ref_type = int(request.GET.get('ref_type'))
        scope = request.scope
        if ref_type == CovernoteUtil.proposal_finalize:
            condition = Q(status=ActiveStatus.Active) & Q(ref_id=ref_id) & Q(ref_type=ref_type) & Q(q_type=q_type)
        else:
            condition = Q(status=ActiveStatus.Active) & Q(ref_id=ref_id) & Q(ref_type=ref_type)

        comment_obj = TransactionComments.objects.using(self._current_app_schema()).filter(condition).order_by(
            '-created_date')[vys_page.get_offset():vys_page.get_query_limit()]

        cmt_obj, reply_obj, trancmt_id, tranreply_id, user_id, vow_user = [], [], [], [], [], []
        for j in comment_obj:
            if j.reply_id == None:
                cmt_obj.append(j)
                trancmt_id.append(j.id)
            else:
                reply_obj.append(j)
                tranreply_id.append(j.id)
            if j.is_user == True:
                user_id.append(j.created_by)
            else:
                vow_user.append(j.created_by)

        total_trancmt_id = [*trancmt_id, *tranreply_id]

        api_serv = ApiService(scope)
        emp_data = api_serv.get_multi_emp(request, user_id)
        vow_emp_data = api_serv.fetch_vow_multi_employee(vow_user)
        docu_data = self.get_comments_document(total_trancmt_id)

        ecf_list_data = NWisefinList()
        for cmts in cmt_obj:
            cmts_data = Commentsresponse()
            cmts_data.set_id(cmts.id)
            cmts_data.set_ref_id(cmts.ref_id)
            cmts_data.set_ref_type(cmts.ref_type)
            cmts_data.set_comment(cmts.comment)
            cmts_data.set_reply(self.get_reply_cmt(reply_obj, emp_data, vow_emp_data, docu_data, cmts.id))
            cmts_data.set_type(cmts.type)
            cmts_data.set_is_user(cmts.is_user)
            cmts_data.set_created_by(emp_data, vow_emp_data, cmts.created_by, cmts.is_user)
            cmts_data.set_created_date(cmts.created_date)
            cmts_data.set_file_data(cmts.id, docu_data)
            cmts_data.set_q_type(cmts.q_type)
            ecf_list_data.append(cmts_data)
            vpage = NWisefinPaginator(comment_obj, vys_page.get_index(), 10)
            ecf_list_data.set_pagination(vpage)
        return ecf_list_data

    def get_comments_document(self, arr):
        cmtsdoc = CMSDocuments.objects.using(self._current_app_schema()).filter(rel_id__in=arr,
                                                                                rel_type=DocUtil.comments)
        return cmtsdoc

    def get_reply_cmt(self, reply_obj, emp_data, vow_emp_data, docu_data, cmt_id):
        arr = []
        for i in reply_obj:
            cmts_data = CommentsReplyresponse()
            if i.reply_id == cmt_id:
                cmts_data.set_id(i.id)
                cmts_data.set_comment(i.comment)
                cmts_data.set_created_date(i.created_date)
                cmts_data.set_created_by(emp_data, vow_emp_data, i.created_by, i.is_user)
                cmts_data.set_file_data(i.id, docu_data)
                cmts_data.set_is_user(i.is_user)
                arr.append(cmts_data)
        return arr

    def createreply(self, request, cmts_obj, ref_id, emp_id):
        ref_type = request.GET.get('ref_type')
        reply_id = request.GET.get('reply_id')
        q_type = request.GET.get('q_type')
        cmts = TransactionComments.objects.using(self._current_app_schema()).create(
            ref_id=ref_id,
            ref_type=ref_type,
            comment=cmts_obj.get_comment(),
            type=CommentsUtil.reply,
            q_type=q_type,
            reply_id=reply_id,
            created_by=emp_id,
            created_date=now())

        cmts_data = Commentsresponse()
        cmts_data.set_id(cmts.id)
        cmts_data.set_ref_id(cmts.ref_id)
        cmts_data.set_ref_type(cmts.ref_type)
        cmts_data.set_comment(cmts.comment)
        cmts_data.set_type(cmts.type)
        cmts_data.set_is_user(cmts.is_user)
        cmts_data.set_reply_id(cmts.reply_id)
        return cmts_data


    def file_func(self, request, obj, reply):
        arr = []
        for i in obj:
            from utilityservice.service import cms_api_service
            api_serv = cms_api_service.ApiService(self._scope())
            if i.reply_id == reply or None:
                cmtsdoc = CMSDocuments.objects.using(self._current_app_schema()).filter(rel_id=i.id)
                file_arry = []
                arr1 = {"comment": i.comment,
                        "id": i.id, "created_by": api_serv.get_empsingle_id(request, i.created_by),
                        "file_data": file_arry}
                arr.append(arr1)
                for k in cmtsdoc:
                    file_arry.append({"file_name": k.file_name, "gen_file_name": k.gen_file_name, "id": k.id})
        return arr


from userservice.controller.vowusercontroller import VowUser


class VowCommentService:
    def __init__(self, request):
        vowuser_info = VowUser().get_user(request)
        print(vowuser_info)
        self.emp_id = vowuser_info['user_id']
        self.entity_id = vowuser_info['entity_id']
        self.is_user = vowuser_info['is_user']
        self.schema = vowuser_info['schema']

    def vow_createcmts(self, request, cmts_obj, ref_id, ref_type):
        try:
            cmts = TransactionComments.objects.using(self.schema).create(
                ref_id=ref_id,
                ref_type=ref_type,
                comment=cmts_obj.get_comment(),
                type=cmts_obj.get_type(),
                is_user=self.is_user,
                created_by=self.emp_id,
                created_date=now()
            )
            cmts_data = Commentsresponse()
            cmts_data.set_id(cmts.id)
            cmts_data.set_ref_id(cmts.ref_id)
            cmts_data.set_ref_type(cmts.ref_type)
            cmts_data.set_comment(cmts.comment)
            cmts_data.set_type(cmts.type)
            cmts_data.set_is_user(cmts.is_user)
            return cmts_data

        except Exception as ex:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(ex))
            return error_obj

    def vow_fetch_cmts_list(self, request, vys_page, ref_id, ref_type):
        try:
            condition = Q(status=ActiveStatus.Active) & Q(ref_id=ref_id) & Q(ref_type=ref_type)
            comment_obj = TransactionComments.objects.using(self.schema).filter(condition).order_by('-created_date')[
                          vys_page.get_offset():vys_page.get_query_limit()]

            cmt_obj, reply_obj, trancmt_id, tranreply_id, user_id, vow_user = [], [], [], [], [], []
            ecf_list_data = NWisefinList()
            for j in comment_obj:
                if j.reply_id == None:
                    cmt_obj.append(j)
                    trancmt_id.append(j.id)
                else:
                    reply_obj.append(j)
                    tranreply_id.append(j.id)
                if j.is_user == True:
                    user_id.append(j.created_by)
                else:
                    vow_user.append(j.created_by)
            total_trancmt_id = [*trancmt_id, *tranreply_id]

            api_serv = CmsCommonService(request)
            emp_data = api_serv.get_employee_info(user_id)
            vow_emp_data = api_serv.fetch_vow_multi_employee(vow_user)
            docu_data = self.get_vowcomments_document(total_trancmt_id)
            for cmts in cmt_obj:
                cmts_data = Commentsresponse()
                cmts_data.set_id(cmts.id)
                cmts_data.set_ref_id(cmts.ref_id)
                cmts_data.set_ref_type(cmts.ref_type)
                cmts_data.set_comment(cmts.comment)
                cmts_data.set_reply(self.get_reply_vowcmt(reply_obj, emp_data, vow_emp_data, docu_data, cmts.id))
                cmts_data.set_type(cmts.type)
                cmts_data.set_is_user(cmts.is_user)
                cmts_data.set_created_date(cmts.created_date)
                cmts_data.set_created_by(emp_data, vow_emp_data, cmts.created_by, cmts.is_user)
                cmts_data.set_file_data(cmts.id, docu_data)
                ecf_list_data.append(cmts_data)
                vpage = NWisefinPaginator(comment_obj, vys_page.get_index(), 10)
                ecf_list_data.set_pagination(vpage)
            return ecf_list_data
        except Exception as ex:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(ex))
            return error_obj

    def get_vowcomments_document(self, arr):
        cmtsdoc = CMSDocuments.objects.using(self.schema).filter(rel_id__in=arr,
                                                                 rel_type=DocUtil.comments)
        return cmtsdoc

    def get_reply_vowcmt(self, reply_obj, emp_data, vow_emp_data, docu_data, cmt_id):
        arr = []
        for i in reply_obj:
            cmts_data = CommentsReplyresponse()
            if i.reply_id == cmt_id:
                cmts_data.set_id(i.id)
                cmts_data.set_comment(i.comment)
                cmts_data.set_created_date(i.created_date)
                cmts_data.set_created_by(emp_data, vow_emp_data, i.created_by, i.is_user)
                cmts_data.set_file_data(i.id, docu_data)
                cmts_data.set_is_user(i.is_user)
                arr.append(cmts_data)
        return arr

    def vow_createreply(self, request, cmts_obj, ref_id, ref_type, reply):
        try:
            cmts = TransactionComments.objects.using(self.schema).create(
                ref_id=ref_id,
                ref_type=ref_type,
                comment=cmts_obj.get_comment(),
                type=CommentsUtil.reply,
                reply_id=reply,
                is_user=self.is_user,
                created_by=self.emp_id)

            cmts_data = Commentsresponse()
            cmts_data.set_id(cmts.id)
            cmts_data.set_ref_id(cmts.ref_id)
            cmts_data.set_ref_type(cmts.ref_type)
            cmts_data.set_comment(cmts.comment)
            cmts_data.set_type(cmts.type)
            cmts_data.set_is_user(cmts.is_user)
            cmts_data.set_reply_id(cmts.reply_id)
            return cmts_data

        except Exception as ex:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(ex))
            return error_obj

    def vow_file_func(self, request, obj, reply):
        arr = []
        for i in obj:
            from utilityservice.service import cms_api_service
            api_serv = cms_api_service.CmsCommonService(request)
            if i.reply_id == reply or None:
                cmtsdoc = CMSDocuments.objects.using(self.schema).filter(rel_id=i.id)
                file_arry = []
                arr1 = {"comment": i.comment,
                        "id": i.id, "created_by": api_serv.get_empsingle_id(i.created_by),
                        "file_data": file_arry}
                arr.append(arr1)
                for k in cmtsdoc:
                    file_arry.append({"file_name": k.file_name, "gen_file_name": k.gen_file_name, "id": k.id})
        return arr
