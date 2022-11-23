# import io

import pdfkit
# from PyPDF2 import PdfFileReader, PdfFileWriter
from django.db.models import Q
import re

# from reportlab.lib.colors import HexColor
# from reportlab.lib.units import cm
# from reportlab.pdfgen import canvas

from cmsservice.service.projecttypeservice import ProjectTypeService
from cmsservice.util.cmsutil import ApprovalStatus, ActiveStatus, DocUtil, HistoryStatus, ClausesUtil,AgreementTemplateUtil,SuperScriptUtil
# from nwisefin.settings import BASE_DIR
from userservice.controller.vowusercontroller import VowUser
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.cms_api_service import ApiService
from utilityservice.service.threadlocal import NWisefinThread
from cmsservice.models.cmsmodels import LegalClauses, ProjectTranComments, ProposalLegalclausesMapping, \
    ProposalAgreement, ProposedContract, Project , ProposalAgreementVersion,Agreement_Superscript
from cmsservice.data.response.leaglclauseresponse import LegalResponse
from django.utils import timezone

# from io import BytesIO
from django.http import HttpResponse
# from xhtml2pdf import pisa


class LegalClauseService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.CMS_SERVICE)

    def legal_clause_insert(self,data,employee_id):
        if data.get_id()!=None:
            obj=LegalClauses.objects.using(self._current_app_schema()).filter(id=data.get_id()).update(name=data.get_name(),clauses=data.get_clauses(),type=data.get_type(),description=data.get_description(),updated_by=employee_id,updated_date=timezone.now())

        else:
            obj=LegalClauses.objects.using(self._current_app_schema()).create(name=data.get_name(),clauses=data.get_clauses(),description=data.get_description(),approval_status=ApprovalStatus.APPROVED,type=data.get_type(),created_by=employee_id)

            ProjectTranComments.objects.using(self._current_app_schema()).create(rel_id=obj.id,rel_type=DocUtil.LegalClauses,approver=employee_id, comments=None, created_by=employee_id,approval_status=HistoryStatus.APPROVED)

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    def legal_clause_fetch(self,request):
        approval_status = request.GET.get('approval_status')
        type = request.GET.get('type')

        condition=Q(status=ActiveStatus.Active) & Q(parent_id=None)
        name=request.GET.get('name')
        if (name is not None) & (name != ''):
            condition&=Q(name__icontains=name)
        if (approval_status is not None) & (approval_status != ''):
            approval_status=int(approval_status)
            condition &= Q(approval_status = approval_status)
        if approval_status==ApprovalStatus.DRAFT or approval_status==ApprovalStatus.REVIEW:
            condition &= Q(created_by=request.employee_id)
        elif approval_status==ApprovalStatus.PENDING  or approval_status==ApprovalStatus.REJECTED:
            condition &=Q(approval_by=request.employee_id)
        if type != None:
            condition &=Q(type=int(type))

        filter_legal=LegalClauses.objects.using(self._current_app_schema()).filter(condition).order_by("-id")
        # approver_list = [i.approval_by for i in filter_legal]
        # approver_data = ApiService(request.scope).get_multi_emp(request, approver_list)

        arr = NWisefinList()
        for data in filter_legal:
            resp=LegalResponse()
            resp.set_id(data.id)
            resp.set_type(data.type)
            resp.set_approval_status(data.approval_status)
            resp.set_description(data.description)
            resp.set_name(data.name)
            # resp.set_approval_by(data.approval_by,approver_data)
            arr.append(resp)
        return arr

    # def legal_clause_approval(self,legal_clause_id,data,employee_id):
    #
    #     status=data["status"]
    #     if int(status)==2:
    #
    #         data=self.legalclause_movetoapproover(legal_clause_id,data,employee_id)
    #         return data
    #
    #     else:
    #         remarks = data["remarks"]
    #         filter_legal = LegalClauses.objects.using(self._current_app_schema()).filter(id=legal_clause_id)
    #         if status in [ApprovalStatus.APPROVED, ApprovalStatus.REJECTED, ApprovalStatus.REVIEW]:
    #             pass
    #         else:
    #             error_obj = NWisefinError()
    #             error_obj.set_code(ErrorMessage.INVALID_DATA)
    #             error_obj.set_description("INVAILD STATUS")
    #             return error_obj
    #         if filter_legal[0].approval_status!=ApprovalStatus.PENDING:
    #             error_obj = NWisefinError()
    #             error_obj.set_code(ErrorMessage.INVALID_DATA)
    #             error_obj.set_description("INVAILD STATUS")
    #             return error_obj
    #         if filter_legal[0].approval_by!=employee_id:
    #             error_obj = NWisefinError()
    #             error_obj.set_code(ErrorMessage.INVALID_DATA)
    #             error_obj.set_description("INVAILD APPROVER")
    #             return error_obj
    #         filter_legal.update(approval_status=status,updated_by=employee_id,updated_date=timezone.now())
    #         ProjectTranComments.objects.using(self._current_app_schema()).create(rel_id=legal_clause_id,
    #                                                                              rel_type=DocUtil.LegalClauses,
    #                                                                              approver=employee_id,
    #                                                                              comments=remarks, created_by=employee_id,
    #                                                                              created_date=timezone.now(),
    #                                                                              approval_status=status)
    #         success_obj = NWisefinSuccess()
    #         success_obj.set_status(SuccessStatus.SUCCESS)
    #         success_obj.set_message("Successfully Approved")
    #         return success_obj

    # def legalclause_movetoapproover(self,legal_clause_id,data,employee_id):
    #     approved_by=data["approval_by"]
    #     filter_legal=LegalClauses.objects.using(self._current_app_schema()).filter(id=legal_clause_id)
    #     if filter_legal[0].approval_status!=ApprovalStatus.DRAFT and filter_legal[0].approval_status!=ApprovalStatus.REVIEW:
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.INVALID_DATA)
    #         error_obj.set_description("INVAILD STATUS")
    #         return error_obj
    #     if filter_legal[0].created_by != employee_id:
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.INVALID_DATA)
    #         error_obj.set_description("INVAILD APPROVER")
    #         return error_obj
    #     if approved_by==None or approved_by=="":
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.INVALID_DATA)
    #         error_obj.set_description("INVAILD APPROVER")
    #         return error_obj
    #     if approved_by==filter_legal[0].created_by:
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.INVALID_DATA)
    #         error_obj.set_description("INVAILD APPROVER")
    #         return error_obj
    #
    #     filter_legal.update(approval_status=ApprovalStatus.PENDING,approval_by=approved_by,updated_by=employee_id,updated_date=timezone.now())
    #     success_obj = NWisefinSuccess()
    #     success_obj.set_status(SuccessStatus.SUCCESS)
    #     success_obj.set_message("Submitted Successfully")
    #     return success_obj

    # def proposal_legal_Mapping(self,data,proposal_id,employee_id):
    #     clause_id=data["clause_id"]
    #     order=data["order"]
    #     obj=ProposalLegalclausesMapping.objects.using(self._current_app_schema()).filter(clauses_id=clause_id,
    #                                                                                  proposal_id=proposal_id)
    #     if len(obj)!=0:
    #         obj.update(order=order,updated_by=employee_id,updated_date=timezone.now())
    #     else:
    #         ProposalLegalclausesMapping.objects.using(self._current_app_schema()).create(clauses_id=clause_id,proposal_id=proposal_id,order=order)
    #     success_obj = NWisefinSuccess()
    #     success_obj.set_status(SuccessStatus.SUCCESS)
    #     success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
    #     return success_obj
    def legal_agreement(self,body_data,proposal_id,clauses_id,emp_id):
        obj=ProposalAgreement.objects.using(self._current_app_schema()).filter(proposal_id=proposal_id)
        if len(obj) != 0 and body_data.get_id()==None:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("Invalid Proposal id")
            return error_obj


        arr=[]
        for i in clauses_id:
            obj=ProposalLegalclausesMapping(clauses_id=i,proposal_id=proposal_id)
            arr.append(obj)
        ProposalLegalclausesMapping.objects.using(self._current_app_schema()).bulk_create(arr)
        if body_data.get_id()!=None:
            ProposalAgreement.objects.using(self._current_app_schema()).filter(proposal_id=proposal_id).update(agreement=body_data.get_agreement(),
                                                                               start_date=body_data.get_start_date(),
                                                                               end_date=body_data.get_end_date(),
                                                                               updated_by=emp_id,updated_date=timezone.now())
        else:
            ProposalAgreement.objects.using(self._current_app_schema()).create(agreement=body_data.get_agreement(),start_date=body_data.get_start_date(),end_date=body_data.get_end_date(),created_by=emp_id,proposal_id=proposal_id)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def legal_agreement_get(self,proposal_id):
        data=ProposalAgreement.objects.using(self._current_app_schema()).filter(proposal_id=proposal_id)
        type_arr = [i.type for i in data]
        project_identificationtype_service = ProjectTypeService(self._scope())
        type_data = project_identificationtype_service.get_projecttype_info(type_arr)


        resp = LegalResponse()
        is_created=False
        if len(data)!=0:
            is_created=True
        # for obj in data:
            obj = data[0]
            resp.set_id(obj.id)
            resp.set_type(obj.type)
            resp.set_proposal_id(obj.proposal_id)

            # resp.set_proposalclauses(obj.proposalclauses_id)
            resp.set_agreement(obj.agreement)
            resp.set_start_date(obj.start_date)
            resp.set_end_date(obj.end_date)
            resp.set_is_issued(obj.is_issued)
            resp.set_is_accepted(obj.is_accepted)
            resp.set_is_created(is_created)
        else:
            resp.set_is_created(is_created)
            resp.set_is_issued(False)
            resp.set_is_accepted(False)
        return resp.get()
        
    def legal_clause_delete(self,legal_clause_id, emp_id):
        LegalClauses.objects.using(self._current_app_schema()).filter(id=legal_clause_id).update(status=ActiveStatus.Delete,updated_by=emp_id,updated_date=timezone.now())
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj

    def legal_clause_get(self,legal_clause_id,request):

        data=LegalClauses.objects.using(self._current_app_schema()).get(id=legal_clause_id)
        approver_list = [data.approval_by]
        approver_data = ApiService(self._scope()).get_multi_emp(request, approver_list)
        is_approver=False
        is_created_by=False
        if data.created_by != request.employee_id and data.approval_by==request.employee_id and data.approval_status==ApprovalStatus.PENDING:
            is_approver=True
        if data.created_by==request.employee_id:
            if data.approval_status == ApprovalStatus.DRAFT or data.approval_status==ApprovalStatus.REVIEW:
                is_created_by=True
        resp = LegalResponse()
        resp.set_id(data.id)
        resp.set_approval_status(data.approval_status)
        resp.set_description(data.description)
        if data.type==AgreementTemplateUtil.template["id"]:
            resp.set_type(AgreementTemplateUtil.template["name"])
        elif data.type==AgreementTemplateUtil.clauses["id"]:
            resp.set_type(AgreementTemplateUtil.clauses["name"])
        else:
            resp.set_type(None)
        resp.set_clauses(data.clauses)
        resp.set_name(data.name)
        resp.set_is_approver(is_approver)
        resp.set_is_created_by(is_created_by)
        resp.set_approval_by(data.approval_by, approver_data)
        return resp

    def proposallegal_mapping_get(self,request,proposal_id):
        obj=ProposalLegalclausesMapping.objects.using(self._current_app_schema()).filter(proposal_id=proposal_id,status=ActiveStatus.Active)
        arr = NWisefinList()
        for data in obj:
            resp = LegalResponse()
            resp.set_proposalclauses(data.clauses_id)
            resp.set_proposalclauses(data.clauses_id)
            resp.set_proposal_id(data.proposal_id)
            resp.set_proposal_name(data.proposal.name)
            resp.set_clauses_name(data.clauses.name)
            resp.set_clauses(data.clauses.clauses)
            resp.set_order(data.order)
            arr.append(obj)
        return arr
    def proposal_agreement(self,proposal_id,request):

        clauses_id = request.GET.get('clauses_id')
        data=LegalClauses.objects.using(self._current_app_schema()).get(id=clauses_id).clauses
        dollar_values = list(set(re.findall(r'\$\w+', data)))
        cls = ProposalagreementService(self._scope())

        for i in dollar_values:
            values = (i[1:]).lower()
            if ClausesUtil.project_name["text"] == values:
                replace_value = cls.proposalagreement_projectclauses(proposal_id)
                data = data.replace(i, replace_value)
            elif ClausesUtil.proposer_name["text"] == values:
                replace_value = cls.proposalagreement_proposerclauses(proposal_id)
                data = data.replace(i, replace_value)
            elif ClausesUtil.company_name["text"] == values:
                replace_value = cls.proposalagreement_companyclauses()
                data = data.replace(i, replace_value)
        return {"text":data}

    def legal_agreement_download(self,legal_clause_id):
        obj=ProposalAgreement.objects.using(self._current_app_schema()).get(id=legal_clause_id)
        agreement=obj.agreement

        options = {
            'margin-top': '0.25in',
            'margin-right': '0.5in',
            'margin-bottom': '0.75in',
            'margin-left': '0.5in',
            'enable-local-file-access': None,
            'encoding': 'UTF-8',
        }
        # path_wkthmltopdf = "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"
        # config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
        # pdf = pdfkit.from_string(agreement, False, options, configuration=config)
        # result = BytesIO()
        # pdf = pisa.pisaDocument(BytesIO(agreement.encode("ISO-8859-1")), result)
        #
        pdf = pdfkit.from_string(agreement, False, options,configuration=None)
        #
        return HttpResponse(pdf, content_type='application/pdf')

    # def final_booklets(self,booklet, file_name):
    #     watermark_obj = PdfFileReader(file_name)
    #     # watermark_page = watermark_obj.getNumPages()
    #     pdf_reader = PdfFileReader(booklet)
    #     # pdf_reader_page = pdf_reader.getNumPages()
    #     pdf_writer = PdfFileWriter()
    #     # Watermark all the pages
    #     for pageno in range(pdf_reader.getNumPages()):
    #         page = pdf_reader.getPage(pageno)
    #         page.mergePage(watermark_obj.getPage(pageno))
    #         pdf_writer.addPage(page)
    #     output3 = io.BytesIO()
    #     pdf_writer.write(output3)
    #     return output3
    #
    # def watermark_pdf(self,target, booklet, refno, createby):
    #     output = io.BytesIO()
    #     c = canvas.Canvas(output)
    #     pdf_reader = PdfFileReader(booklet)
    #     for page in range(pdf_reader.getNumPages()):
    #         c.saveState()
    #         c.drawImage(BASE_DIR + 'wisefin-be\wisefin\cmsservice\logo', 500, 0, 50, 50)
    #         c.setFillColor(HexColor('#808080'), 0.80)
    #         c.setFont("Helvetica", 8)
    #         c.drawString(20 * cm, 1 * cm, str(int(page) + 1) + "/" + str(pdf_reader.getNumPages()))
    #         c.drawString(0.75 * cm, 1 * cm, str(createby))
    #         c.drawString(10 * cm, 1 * cm, str(refno))
    #         c.setFillColor(HexColor('#D3D3D3'), 0.38)
    #         c.setFont("Helvetica", 30)
    #         c.translate(8 * cm, 8 * cm)
    #         c.rotate(60)
    #         c.drawString(5 * cm, 0 * cm, target)
    #         c.drawString(0 * cm, 5 * cm, target)
    #         c.setFillAlpha(0.2)
    #         c.restoreState()
    #         c.showPage()
    #     c.save()
    #     output = target.final_booklets(booklet, output)
    #     return output

    def agreement_moveto_vendor(self,proposal_agreement_id,emp_id):
        obj=ProposalAgreement.objects.using(self._current_app_schema()).filter(id=proposal_agreement_id)
        if len(obj)==0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PROJECT_ID)
            error_obj.set_description("Invalid Proposal")
            return error_obj

        obj=obj[0]
        version = obj.version
        if version == None:
            version =1
        else:
            version +=1

        ProposalAgreement.objects.using(self._current_app_schema()).filter(id=proposal_agreement_id).update(is_issued=True,version=version, updated_by=emp_id, updated_date=timezone.now(),is_vow_submit=True)

        v_obj = ProposalAgreementVersion.objects.using(self._current_app_schema()).create(note=obj.agreement,version=version, agreement_id=obj.id,created_by=emp_id,type=SuperScriptUtil.original)

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message("Successfully Moved to Vendor")
        return success_obj

    def subclause(self, data, employee_id,parent_id):
        obj = LegalClauses.objects.using(self._current_app_schema()).filter(id=parent_id,status=ActiveStatus.Active)
        if len(obj) == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVALID ID")
            return error_obj
        obj1 = LegalClauses.objects.using(self._current_app_schema()).create(name=data.get_name(),
                                                                            clauses=data.get_clauses(),
                                                                            description=data.get_description(),
                                                                            approval_status=ApprovalStatus.APPROVED,
                                                                            type=AgreementTemplateUtil.clauses['id'],
                                                                            created_by=employee_id,
                                                                            parent_id=parent_id)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj


    def getsubclause(self,parent_id):
        obj2 = LegalClauses.objects.using(self._current_app_schema()).filter(parent_id=parent_id,status=ActiveStatus.Active)
        subclauses = NWisefinList()
        for i in obj2:
            data = LegalResponse()
            data.set_name(i.name)
            data.set_type(i.type)
            data.set_approval_status(i.approval_status)
            data.set_description(i.description)
            subclauses.append(data)
        return subclauses


class ProposalagreementService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.CMS_SERVICE)
    def proposalagreement_companyclauses(self):
        cmpany="company"
        return cmpany
    def proposalagreement_proposerclauses(self,proposal_id):
        name=ProposedContract.objects.using(self._current_app_schema()).get(id=proposal_id).name
        return name

    def proposalagreement_projectclauses(self,project_id):
        # proposals = Project.objects.using(self._current_app_schema()).get(id=project_id)
        data="Project"

        return data

class VowLegalAgreement:
    def __init__(self, request):
        vowuser_info = VowUser().get_user(request)

        self.emp_id = vowuser_info['user_id']
        self.entity_id = vowuser_info['entity_id']
        self.is_user = vowuser_info['is_user']
        self.schema = vowuser_info['schema']

    def vendor_accepted(self,proposal_agreement_id):
        obj=ProposalAgreement.objects.using(self.schema).filter(id=proposal_agreement_id,is_accepted=True)
        if len(obj)!=0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PROJECT_ID)
            error_obj.set_description("Invalid Proposal")
            return error_obj
        ProposalAgreement.objects.using(self.schema).filter(id=proposal_agreement_id).update(
            is_accepted=True, updated_by=self.emp_id, updated_date=timezone.now())
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message("Submitted Successfully")
        return success_obj


    def vendor_return(self,proposal_agreement_id,data):
        content = data['content']
        obj=ProposalAgreement.objects.using(self.schema).filter(id=proposal_agreement_id,status=ActiveStatus.Active)

        if len(obj)==0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("Invalid Proposal ID")
            return error_obj

        version = obj[0].version
        is_accepted =  obj[0].is_accepted
        is_vow_submit = obj[0].is_vow_submit
        if is_accepted == True or is_vow_submit == False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("Already Proposal accepted/return")
            return error_obj

        ProposalAgreementVersion.objects.using(self.schema).create(
            note=content, created_by=self.emp_id,type=SuperScriptUtil.span_tag,version=version)
        ProposalAgreement.objects.using(self.schema).filter(id=proposal_agreement_id).update(is_vow_submit=False)


        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message("Submitted Successfully")
        return success_obj

    def agreement_get(self,proposal_id):
        data = ProposalAgreement.objects.using(self.schema).filter(proposal_id=proposal_id,is_issued=True)

        resp = LegalResponse()
        if len(data) != 0:
            obj = data[0]
            resp.set_id(obj.id)

            resp.set_proposal_id(obj.proposal_id)

            resp.set_agreement(obj.agreement)
            resp.set_start_date(obj.start_date)
            resp.set_end_date(obj.end_date)
            resp.set_is_issued(obj.is_issued)
            resp.set_is_accepted(obj.is_accepted)
            resp.set_is_return(obj.is_vow_submit)
            resp.set_version(obj.version)
        return resp.get()

    def vow_legal_agreement_download(self,legal_clause_id):
        obj=ProposalAgreement.objects.using(self.schema).get(id=legal_clause_id)
        agreement=obj.agreement
        options = {
            'margin-top': '0.25in',
            'margin-right': '0.5in',
            'margin-bottom': '0.75in',
            'margin-left': '0.5in',
            'enable-local-file-access': None,
            'encoding': 'UTF-8',
        }
        # path_wkthmltopdf = "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"
        # config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
        # pdf = pdfkit.from_string(agreement, False, options, configuration=config)

        pdf = pdfkit.from_string(agreement, False, options,configuration=None)
        return HttpResponse(pdf, content_type='application/pdf')


    # def vow_agreement_superscript(self,agreement_id):
    #     a=get_vow_agreement_superscript(agreement_id)
