from django.db.models import Q
import re
from cmsservice.service.projecttypeservice import ProjectTypeService
from cmsservice.util.cmsutil import ApprovalStatus, ActiveStatus, DocUtil, HistoryStatus, ClausesUtil, \
    AgreementTemplateUtil,CommentsRefTypeUtil,SuperScriptUtil
from userservice.controller.vowusercontroller import VowUser
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.cms_api_service import ApiService,CmsCommonService
from utilityservice.service.threadlocal import NWisefinThread
from cmsservice.models.cmsmodels import LegalClauses, ProjectTranComments, ProposalLegalclausesMapping,ProposalAgreement, ProposedContract, Project , TransactionComments,Agreement_Superscript,ProposalAgreementVersion
from cmsservice.data.response.leaglclauseresponse import SuperscriptResponse
from django.utils import timezone
from django.http import HttpResponse


class SuperScriptService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.CMS_SERVICE)

    # cms superscript comments
    def superscript_comments(self, agreement_id, data):
        pass

    # cms superscript comments get
    def get_superscript_comments(self, proposal_id, request):
        arr = NWisefinList()
        version = request.GET.get('version')
        if version !=None:
            version=int(version)
        # proposal agreement
        proposal_arg_obj = ProposalAgreement.objects.using(self._current_app_schema()).filter(proposal_id=proposal_id,status=ActiveStatus.Active)
        if len(proposal_arg_obj) == 0 :
            arr.superscript = None
            arr.content = None
            arr.version = None
            arr.is_created= False
            arr.is_issued=False
            arr.is_accepted=False
            return arr

        proposal_arg=proposal_arg_obj[0]
        agreement_id =proposal_arg.id
        agreement_version = proposal_arg.version
        content = proposal_arg.agreement
        super_script_content = None
        orginal_id, span_tag_id = None, None

        # ProposalAgreementVersion
        cond = Q(agreement_id=agreement_id) & Q(status=ActiveStatus.Active)
        if version != None:
            cond &= Q(version=version)
            v=version
        else:
            cond &= Q(version=agreement_version)
            v=agreement_version


        agreement_v_obj = ProposalAgreementVersion.objects.using(self._current_app_schema()).filter(cond).order_by('-version')

        for obj in agreement_v_obj:
            if (obj.type == SuperScriptUtil.original) and (obj.version == version) and (version != None):
                content = obj.note
            # if (obj.type == SuperScriptUtil.span_tag)and (obj.agreement.is_vow_submit==False):
            #     if (obj.version == agreement_version) and version == None:
            #         super_script_content = obj.note
            #         span_tag_id = obj.id
            #     elif obj.version == version and version != None:
            #         super_script_content = obj.note
            #         span_tag_id = obj.id

            if (obj.type == SuperScriptUtil.span_tag):
                if (obj.agreement.is_vow_submit==False)and (obj.version == v):
                    super_script_content = obj.note
                    span_tag_id = obj.id

                if (obj.version == version):
                    super_script_content = obj.note
                    span_tag_id = obj.id

        if span_tag_id != None:
            # agreement_vid.append(span_tag_id)
            s_obj = Agreement_Superscript.objects.using(self._current_app_schema()).filter(
            agreementversion_id=span_tag_id,status=ActiveStatus.Active)

            arr_id = [i.id for i in s_obj]
            cmt_obj = TransactionComments.objects.using(self._current_app_schema()).filter(ref_id__in=arr_id,ref_type=CommentsRefTypeUtil.superscript,status=ActiveStatus.Active)

            cms_emp_arr=[a.created_by for a in cmt_obj if a.is_user==True ]
            vow_emp_arr=[a.created_by for a in cmt_obj if a.is_user==False]
            api_serv = ApiService(request.scope)
            emp_data = api_serv.get_multi_emp(request, cms_emp_arr)
            vow_emp_data = api_serv.fetch_vow_multi_employee(vow_emp_arr)

            for obj in s_obj:
                resp = SuperscriptResponse()
                resp.set_id(obj.id)
                resp.set_start_index(obj.start_index)
                resp.set_end_index(obj.end_index)
                resp.set_comments(obj.id, cmt_obj,emp_data, vow_emp_data)
                resp.set_order(obj.order)
                arr.append(resp)

        arr.superscript = super_script_content
        arr.content = content
        arr.version = v
        arr.is_created = True
        arr.is_issued = proposal_arg.is_issued
        arr.is_accepted = proposal_arg.is_accepted
        arr.start_date = str(proposal_arg.start_date)
        arr.end_date = str(proposal_arg.end_date)
        arr.agreement_id=proposal_arg.id
        arr.is_vow_submited = proposal_arg.is_vow_submit
        return arr

    def cms_superscript_comments(self,data,superscript_id,emp_id):
        ss_obj = Agreement_Superscript.objects.using(self._current_app_schema()).get(id=superscript_id)
        is_submit = ss_obj.agreementversion.agreement.is_vow_submit
        if is_submit == True:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("Agreement Submitted  to VOW")
            return error_obj

        comments = data['comments']
        ss1_obj = TransactionComments.objects.using(self._current_app_schema()).create(
            ref_type=CommentsRefTypeUtil.superscript,
            ref_id=superscript_id, created_by=emp_id, comment=comments)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessStatus.SUCCESS)
        return success_obj




class VowSuperScriptService:
    def __init__(self, request):
        vowuser_info = VowUser().get_user(request)
        self.emp_id = vowuser_info['user_id']
        self.entity_id = vowuser_info['entity_id']
        self.is_user = vowuser_info['is_user']
        self.schema = vowuser_info['schema']

    def vow_agreement_superscript(self,agreement_id,data):
        start_index=data['start_index']
        end_index =data['end_index']
        comments = data['comments']
        superscript_content=data['superscript_content']
        proposal_agreement_obj = ProposalAgreement.objects.using(self.schema).get(id=agreement_id)
        version=proposal_agreement_obj.version
        is_submit=proposal_agreement_obj.is_vow_submit
        if is_submit ==False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("Agreement Submitted  to CMS")
            return error_obj

        #  agreement version
        agreement_v_obj = ProposalAgreementVersion.objects.using(self.schema).filter(agreement_id=agreement_id,status=ActiveStatus.Active,type=SuperScriptUtil.span_tag,version=version).order_by('-version')
        if len(agreement_v_obj)>0:
            agreement_vid=agreement_v_obj[0].id
            ProposalAgreementVersion.objects.using(self.schema).filter(id=agreement_vid).update(note=superscript_content,updated_by=self.emp_id,updated_date=timezone.now())
        else:
            p_obj=ProposalAgreementVersion.objects.using(self.schema).create(note=superscript_content,agreement_id=agreement_id,created_by=self.emp_id,is_user=False,type=SuperScriptUtil.span_tag,version=version)
            agreement_vid=p_obj.id
        ss_obj=Agreement_Superscript.objects.using(self.schema).filter(agreementversion_id=agreement_vid).order_by('-id')
        if len(ss_obj)==0:
            ss_order=1
        else:
            ss_order =(ss_obj[0].order)+1
        # superscript insert
        agr_ss_obj=Agreement_Superscript.objects.using(self.schema).create(agreementversion_id=agreement_vid,start_index=start_index,end_index=end_index,is_user=False,created_by=self.emp_id,order=ss_order)
        #  superscript comment
        TransactionComments.objects.using(self.schema).create(ref_id=agr_ss_obj.id,ref_type=CommentsRefTypeUtil.superscript,comment=comments,created_by=self.emp_id,is_user=False)

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessStatus.SUCCESS)
        return success_obj

    def get_vow_agreement_superscript(self,agreement_id,request):
        version = request.GET.get('version')
        cond=Q(agreement_id=agreement_id)&Q(status=ActiveStatus.Active)
        if version !=None:
            cond &=Q(version=version)
        agreement_v_obj = ProposalAgreementVersion.objects.using(self.schema).filter(cond).order_by('-version')
        super_script_content, content = None, None
        orginal_id, span_tag_id = None, None
        # agreement_vid=[]
        # agreement_vid=agreement_v_obj[0].id
        agreement_version=agreement_v_obj[0].version
        for obj in agreement_v_obj:
            if (obj.type == SuperScriptUtil.original) and (obj.version==agreement_version):
                content=obj.note
                # orginal_id=obj.id
            if (obj.type == SuperScriptUtil.span_tag) and (obj.version==agreement_version):
                super_script_content=obj.note
                span_tag_id=obj.id
        # if orginal_id != None:
        #     agreement_vid.append(orginal_id)
        # if span_tag_id != None:
        #     agreement_vid.append(span_tag_id)
        s_obj = Agreement_Superscript.objects.using(self.schema).filter(agreementversion_id=span_tag_id,status=ActiveStatus.Active)
        arr_id=[i.id for i in s_obj]
        cmt_obj=TransactionComments.objects.using(self.schema).filter(ref_id__in=arr_id,ref_type=CommentsRefTypeUtil.superscript,status=ActiveStatus.Active)

        cms_emp_arr = [a.created_by for a in cmt_obj if a.is_user == True]
        vow_emp_arr = [a.created_by for a in cmt_obj if a.is_user == False]
        api_serv = CmsCommonService(request)
        emp_data = api_serv.get_employee_info(cms_emp_arr)
        vow_emp_data = api_serv.fetch_vow_multi_employee(vow_emp_arr)
        arr=NWisefinList()
        for obj in s_obj:
            resp=SuperscriptResponse()
            resp.set_id(obj.id)
            resp.set_start_index(obj.start_index)
            resp.set_end_index(obj.end_index)
            resp.set_comments(obj.id,cmt_obj,emp_data,vow_emp_data)
            resp.set_order(obj.order)
            arr.append(resp)
        arr.superscript = super_script_content
        arr.content = content
        arr.version=agreement_version
        return arr

# vow superscript comments
    def vow_superscript_comments(self,superscript_id, data):
        ss_obj=Agreement_Superscript.objects.using(self.schema).get(id=superscript_id)
        is_submit = ss_obj.agreementversion.agreement.is_vow_submit
        print(is_submit)
        if is_submit ==False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("Agreement Submitted  to CMS")
            return error_obj

        comments = data['comments']
        ss2_obj = TransactionComments.objects.using(self.schema).create(
            ref_type=CommentsRefTypeUtil.superscript,
            ref_id=superscript_id, created_by=self.emp_id,is_user=False,comment=comments)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessStatus.SUCCESS)
        return success_obj