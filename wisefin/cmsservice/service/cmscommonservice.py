from datetime import datetime

from django.utils import timezone
from django.utils.timezone import now

from cmsservice.data.response.cmsdocumentsresponse import Cmsdocresponse, CmsCovernoteResponse
from cmsservice.models import CMSCovernote, CMSDocuments, ProposedContractApprovalTran, CMSNotepad, CMSCovernoteHistory, \
    CMSDocumentsHistory,CMSUpdateHistory,CMSProjectInvitation,CMSGroupMapping
# from utilityservice.service.cms_api_service import CmsCommonService
from cmsservice.util.cmsutil import DocUtil, TranStatus, ActiveStatus, TranApproverType
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from userservice.controller.vowusercontroller import VowUser
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess,SuccessStatus
from ast import literal_eval
import json
import time
import collections


class CommonService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.CMS_SERVICE)

    # Doc -- attachement
    def updateprojectattachement(self, document_json, ref_id, content_type, doc_type, emp_id):
        doc = []
        for d_j in document_json:
            project = CMSDocuments.objects.using(self._current_app_schema()).create(
                                                file_id=d_j['id'],
                                                rel_id=ref_id,
                                                rel_type=content_type,
                                                file_name=d_j['file_name'],
                                                gen_file_name=d_j['gen_file_name'],
                                                type=doc_type,
                                                created_by=emp_id)
            doc.append(project)
        return doc

    def updatedfile(self, ref_id, content_type):
        active_doc = CMSDocuments.objects.using(self._current_app_schema()).filter(rel_id=ref_id, rel_type=content_type, status=ActiveStatus.Active)
        return active_doc

    # prefix & filename -- attachement
    def content_prefix(self, ref_id, content_type):
        if content_type == DocUtil.project:
            prefix = "ProjectContent_"
        elif content_type == DocUtil.proposer:
            prefix = "ProposerContent_"
        txt = '.txt'
        file_name = prefix + str(datetime.now().strftime("%y%m%d_%H%M%S")) + "_" + str(ref_id) + str(txt)
        return file_name

    # covernote -- attachement
    def covernote_create(self, ref_id, content_type, content, emp_id):
        prop_obj = CMSCovernote.objects.using(self._current_app_schema()
                                              ).filter(rel_id=ref_id,rel_type=content_type,
                                                       status=ActiveStatus.Active)
        if len(prop_obj) > 0:
            prop_objg = CMSCovernote.objects.using(self._current_app_schema()
                                            ).filter(rel_id=ref_id,rel_type=content_type,
                                            status=ActiveStatus.Active).update(
                                            note=content,
                                            updated_by=emp_id,
                                            updated_date=timezone.now())
            prop_obj = prop_obj[0]
        else:
            prop_obj = CMSCovernote.objects.using(self._current_app_schema()).create(
                                    rel_id=ref_id,
                                    rel_type=content_type,
                                    note=content,
                                    created_by=emp_id)
        return prop_obj


    # bulk create
    def bulk_create_assign(self, ass_emp_id, ref_id, tran_type, to_type, emp_id,parallel_approver):
        arr = []
        q_order = 1
        for i in ass_emp_id:
            if parallel_approver==True:
                tran_status = TranStatus.awaiting
            else:
                if q_order == 1:
                    tran_status = TranStatus.pending
                else:
                    tran_status = TranStatus.awaiting
            obj = ProposedContractApprovalTran(proposed_id=ref_id, tran_type=tran_type, to_type=to_type,
                                               to=i,
                                               order=q_order, tran_status=tran_status, created_by=emp_id,
                                               created_date=timezone.now())
            arr.append(obj)
            q_order += q_order

        ProposedContractApprovalTran.objects.using(self._current_app_schema()).bulk_create(arr)
        print("inserted covernote for content_type- ok")
        return True

    def remove_prjattachement(self, ref_id, file_remove, emp_id):
        for file_id in file_remove:
            project = CMSDocuments.objects.using(self._current_app_schema()).filter(
                                                id=file_id,
                                                rel_id=ref_id
                                                ).update(
                                                status=ActiveStatus.Delete,
                                                updated_by=emp_id,
                                                updated_date=now())
        return True

    def covernote_project(self, rel_id, rel_type):
        cmt_resp = CmsCovernoteResponse()
        covern = CMSCovernote.objects.using(self._current_app_schema()).filter(rel_id=rel_id, rel_type=rel_type,
                                             status=ActiveStatus.Active)
        if len(covern) > 0:
            covern = covern[0]
            cmt_resp.set_id(covern.id)
            cmt_resp.set_rel_id(covern.rel_id)
            cmt_resp.set_rel_type(covern.rel_type)
            cmt_resp.set_note(covern.note)
        return cmt_resp

    def covernotehistory_project(self, rel_id, rel_type):
        cmt_resp = CmsCovernoteResponse()
        c = CMSCovernoteHistory.objects.using(self._current_app_schema()).filter(rel_id=rel_id, rel_type=rel_type, status=ActiveStatus.Active)
        if len(c) > 0:
            c = c[0]
            cmt_resp.set_id(c.id)
            cmt_resp.set_rel_id(c.rel_id)
            cmt_resp.set_rel_type(c.rel_type)
            cmt_resp.set_note(c.note)
        return cmt_resp

    def attachement_project(self, rel_id, type):
        file_arr = []
        file = CMSDocuments.objects.using(self._current_app_schema()).filter(rel_id=rel_id, rel_type=type, status=ActiveStatus.Active)
        for f in file:
            doc_resp = Cmsdocresponse()
            doc_resp.set_id(f.id)
            doc_resp.set_file_id(f.file_id)
            doc_resp.set_rel_id(f.rel_id)
            doc_resp.set_rel_type(f.rel_type)
            doc_resp.set_file_name(f.file_name)
            file_arr.append(doc_resp)
        return file_arr

    def attachementhistory_project(self, rel_id, type):
        file_arr = []
        file = CMSDocumentsHistory.objects.using(self._current_app_schema()).filter(rel_id=rel_id, rel_type=type, status=ActiveStatus.Active)
        for f in file:
            doc_resp = Cmsdocresponse()
            doc_resp.set_id(f.id)
            doc_resp.set_rel_id(f.rel_id)
            doc_resp.set_file_id(f.file_id)
            doc_resp.set_rel_type(f.rel_type)
            doc_resp.set_file_name(f.file_name)
            file_arr.append(doc_resp)
        return file_arr

    def create_notepad(self, pr_obj, rel_id, type, emp_id):
        if not pr_obj.get_id() is None:
            prop_obj = CMSNotepad.objects.using(self._current_app_schema()).filter(
                                    id=pr_obj.get_id()).update(
                                    rel_id=rel_id,
                                    rel_type=type,
                                    content=pr_obj.get_content(),
                                    updated_by=emp_id,
                                    updated_date=timezone.now())
            prop_obj = CMSNotepad.objects.using(self._current_app_schema()).get(id=pr_obj.get_id())
        else:
            prop_obj = CMSNotepad.objects.using(self._current_app_schema()).create(
                                    rel_id=rel_id,
                                    rel_type=type,
                                    content=pr_obj.get_content(),
                                    created_by=emp_id)
        return prop_obj
    def get_pending_grp(self,emp_grp,approver_grp):
        arr=[]
        for i in approver_grp:
            if (i.to_type['id'] == TranApproverType.group) & (i.approver['id'] in emp_grp) & (i.status['id']== TranStatus.pending):
                arr.append(i)
        return arr

    # for version insert needed
    def updated_covernote(self, rel_id, rel_type):
        active_doc = CMSCovernote.objects.using(self._current_app_schema()).filter(rel_id=rel_id, rel_type=rel_type,
                                             status=ActiveStatus.Active)

        return active_doc
    #  updated history get
    def get_update_ref_data(self,ref_id):
        obj=CMSUpdateHistory.objects.using(self._current_app_schema()).get(id=ref_id)
        updated_data=obj.data
        resp_data =literal_eval(updated_data)
        r=collections.namedtuple("obj",resp_data.keys())(*resp_data.values())
        return r

    def obj_to_dict_conversion(self,data):
        rework_data = data.__dict__
        del rework_data['_state']
        for k, v in rework_data.items():
            if (v.__class__.__name__ == 'datetime'):
                rework_data[k] =  int(rework_data[k].timestamp() * 1000)
            elif(v.__class__.__name__ == 'date'):
                rework_data[k] = int(time.mktime(rework_data[k].timetuple()) * 1000)
        return rework_data

    #  updated history insert
    def insert_update_ref_data(self,data,refid,reftype,emp_id):
        # cms update history
        obj=CMSUpdateHistory.objects.using(self._current_app_schema()).create(data=data,created_by=emp_id,ref_id=refid,ref_type=reftype)

        return obj.id

    def common_update_ref_data(self,m_models,refid,update_refid):
        #  update_refid update in parent table
        m_models.objects.using(self._current_app_schema()).filter(id=refid).update(update_refid=update_refid, is_ref=True)
        return





    def mailprojectinvitation(self,project_id):
        proinvitation = CMSProjectInvitation.objects.using(self._current_app_schema()).filter(project_id=project_id,status=ActiveStatus.Active)

    def cmsinsertmultiplegroup(self,arr,emp_id,ref_id,ref_type):
        data=[]
        for grpid in arr:
            cms_obj=CMSGroupMapping(ref_id=ref_id,ref_type=ref_type,created_by=emp_id,group_id=grpid)
            data.append(cms_obj)
        CMSGroupMapping.objects.using(self._current_app_schema()).bulk_create(data)



    # def cmsgetmultiplegroup(self,ref_id,ref_type):
    #     arr=[]
    #     getgrp = CMSGroupMapping.objects.using(self._current_app_schema()).filter(ref_id=ref_id,ref_type=ref_type,status=ActiveStatus.Active)
    #     for grp in getgrp:
    #         arr.append(grp.group_id)
    #     serv=CmsCommonService(self._scope())
    #     getmultigrp=serv.fetch_multi_group_by_id(arr)
    #     return getmultigrp
    def cms_multi_file(self, refid_arr, content_type):
        active_doc = CMSDocuments.objects.using(self._current_app_schema()).filter(rel_id__in=refid_arr, rel_type=content_type, status=ActiveStatus.Active)
        return active_doc



class VowCommonService:
    def __init__(self, request):
        vowuser_info = VowUser().get_user(request)

        self.emp_id = vowuser_info['user_id']
        self.entity_id = vowuser_info['entity_id']
        self.is_user = vowuser_info['is_user']
        self.schema = vowuser_info['schema']

    def updateprojectattachement(self, document_json, ref_id,content_type,doc_type):
        doc_data = []
        for d_j in document_json:
            project = CMSDocuments.objects.using(self.schema).create(
                rel_id=ref_id,
                rel_type=content_type,
                file_id=d_j['id'],
                file_name=d_j['file_name'],
                gen_file_name=d_j['gen_file_name'],
                type=doc_type,
                is_user=self.is_user,
                created_by=self.emp_id)
            doc_data.append(project)
        return doc_data

    # prefix & filename -- attachement
    def content_prefix(self, ref_id, content_type):
        if content_type == DocUtil.project:
            prefix = "ProjectContent_"
        elif content_type == DocUtil.proposer:
            prefix = "ProposerContent_"
        txt = '.txt'
        file_name = prefix + str(datetime.now().strftime("%y%m%d_%H%M%S")) + "_" + str(ref_id) + str(txt)
        return file_name

    # covernote -- attachement
    def vow_covernote_create(self, ref_id, content_type, content):
        prop_obj = CMSCovernote.objects.using(self.schema).filter(rel_id=ref_id,
                                                                rel_type=content_type,
                                                                status=ActiveStatus.Active)
        if len(prop_obj) > 0:
            prop_objg = CMSCovernote.objects.using(self.schema).filter(rel_id=ref_id,
                                                                rel_type=content_type,
                                                                status=ActiveStatus.Active).update(
                                                                note=content,
                                                                updated_by=self.emp_id,
                                                                updated_date=timezone.now())
            prop_obj = prop_obj[0]
        else:
            prop_obj = CMSCovernote.objects.using(self.schema).create(
                rel_id=ref_id,
                rel_type=content_type,
                note=content,
                is_user=self.is_user,
                created_by=self.emp_id)
        return prop_obj

    def vow_remove_prjattachement(self, ref_id, file_remove):
        for file_id in file_remove:
            project = CMSDocuments.objects.using(self.schema).filter(
                                            id=file_id, rel_id=ref_id
                                            ).update(
                                            status=ActiveStatus.Delete,
                                            updated_by=self.emp_id,
                                            updated_date=now())
        return True

    def vow_covernote_project(self, rel_id, type):
        cmt_resp = CmsCovernoteResponse()
        covern = CMSCovernote.objects.using(self.schema).filter(rel_id=rel_id, rel_type=type, status=ActiveStatus.Active)
        if len(covern) > 0:
            covern = covern[0]
            cmt_resp.set_id(covern.id)
            cmt_resp.set_rel_id(covern.rel_id)
            cmt_resp.set_rel_type(covern.rel_type)
            cmt_resp.set_note(covern.note)
        return cmt_resp

    def vow_attachement_project(self, rel_id, type):
        file_arr = []
        file = CMSDocuments.objects.using(self.schema).filter(rel_id=rel_id, rel_type=type, status=ActiveStatus.Active)
        for f in file:
            doc_resp = Cmsdocresponse()
            doc_resp.set_id(f.id)
            doc_resp.set_rel_id(f.rel_id)
            doc_resp.set_file_id(f.file_id)
            doc_resp.set_rel_type(f.rel_type)
            doc_resp.set_file_name(f.file_name)
            file_arr.append(doc_resp)
        return file_arr

    def vow_create_notepad(self, pr_obj, rel_id, type):
        if not pr_obj.get_id() is None:
            prop_obj = CMSNotepad.objects.using(self.schema).filter(
                id=pr_obj.get_id()).update(
                rel_id=rel_id,
                rel_type=type,
                content=pr_obj.get_content(),
                is_user=self.is_user,
                updated_by=self.emp_id,
                updated_date=timezone.now())
            prop_obj = CMSNotepad.objects.using(self.schema).get(id=pr_obj.get_id())
        else:
            prop_obj = CMSNotepad.objects.using(self.schema).create(
                rel_id=rel_id,
                rel_type=type,
                content=pr_obj.get_content(),
                is_user=self.is_user,
                created_by=self.emp_id)
        return prop_obj


    def vow_updatedfile(self, ref_id, content_type):
        active_doc = CMSDocuments.objects.using(self.schema).filter(rel_id=ref_id, rel_type=content_type, status=ActiveStatus.Active)
        return active_doc

    def vow_multi_file(self, refid_arr, content_type):
        active_doc = CMSDocuments.objects.using(self.schema).filter(rel_id__in=refid_arr, rel_type=content_type, status=ActiveStatus.Active)
        return active_doc


    def vow_covernotehistory_project(self, rel_id, type):
        c = CMSCovernoteHistory.objects.using(self.schema).get(rel_id=rel_id, rel_type=type, status=ActiveStatus.Active)
        cmt_resp = CmsCovernoteResponse()
        cmt_resp.set_id(c.id)
        cmt_resp.set_rel_id(c.rel_id)
        cmt_resp.set_rel_type(c.rel_type)
        cmt_resp.set_note(c.note)
        return cmt_resp


    def vow_attachementhistory_project(self, rel_id, type):
        file_arr = []
        file = CMSDocumentsHistory.objects.using(self.schema).filter(rel_id=rel_id, rel_type=type, status=ActiveStatus.Active)
        for f in file:
            doc_resp = Cmsdocresponse()
            doc_resp.set_id(f.id)
            doc_resp.set_file_id(f.file_id)
            doc_resp.set_rel_id(f.rel_id)
            doc_resp.set_rel_type(f.rel_type)
            doc_resp.set_file_name(f.file_name)
            file_arr.append(doc_resp)
        return file_arr

    def vowinsertmultiplegroup(self, arr, emp_id, ref_id, ref_type):
        data=[]
        for grpid in arr:
            vow_obj = CMSGroupMapping(ref_id=ref_id,ref_type=ref_type,created_by=emp_id,group_id=grpid)
            data.append(vow_obj)
        CMSGroupMapping.objects.using(self.schema).bulk_create(data)


