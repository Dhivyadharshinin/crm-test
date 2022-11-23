from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from utilityservice.service.hrms_api_service import HrmsAPIService
from hrmsservice.util.hrmsutil import TemplateUtil
from masterservice.service.leaveattendanceservice import OrgDetails



class HrmsPdfService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.HRMS_SERVICE)

    def hrms_commonpdf(self,template_path,data):
        response = HttpResponse(content_type='application/pdf')
        template = get_template(template_path)
        html = template.render(data)
        pisa.CreatePDF(html, dest=response)
        return response


    def get_temp_data(self,type,employee_id,user_id):
        if int(type) == TemplateUtil.CallLetter:
            template = 'call letter.html'
            data = HrmsAPIService(self._scope()).employee_address_info(employee_id,user_id)
            resp = self.hrms_commonpdf(template,data)
            return resp
        elif int(type) == TemplateUtil.RelievingLetter:
            template = 'relieving letter.html'
            data = HrmsAPIService(self._scope()).employee_address_info(employee_id, user_id)
            res = self.hrms_commonpdf(template, data)
            return res
        elif int(type) == TemplateUtil.AddressConfirmation:
            template = 'addressconfirmation.html'
            emp_data = HrmsAPIService(self._scope()).employee_address_info(employee_id, user_id)
            org_data = HrmsAPIService(self._scope()).get_org_info(employee_id)
            data = {"employee": emp_data, "org": org_data}
            resp = self.hrms_commonpdf(template, data)
            return resp

    # def hrmsfileupload(self, resp_obj):
    #     org_details = OrgDetails.objects.using(self._current_app_schema()).create(
    #         latitude=resp_obj.get_latitude(),
    #         longitude=resp_obj.get_longitude(),
    #         name=resp_obj.get_name(),
    #         radius=resp_obj.get_radius(),
    #         address_id=resp_obj.get_address(),
    #         entity_id=self._entity_id())
    #     # code_ger = CodeGen(self._scope())
    #     # code = code_ger.codegenerator(Code_Gen_Type.ORG_DETAILS, self._entity_id(), emp_id,
    #     #                               Code_Gen_Value.ORG_DETAILS)
    #     # org_details.code = code
    #     # org_details.save()
    #     org = org_details.id
    #     return org