# http://127.0.0.1:8000/prsnserv/internalprovision  -post
#
# prov_data =[{"category_id":data['category_id'],
# "subcategory_id":data['subcategory_id'],
# "gl_id":data['gl_id'],
#                 "branch_id":data['branch_id'],
#                 "narration":"SG",
#                 "vendor_id":data['vendor_id'],
#              "expense_date":data['expense_date'],
#             "amount":data['amount'],
#             "gst_amount":data['gst_amount'],
#             "cc_id":data['cc_id'],
#             "bs_id":data['bs_id'],
#              "reference_number":3,
#              "reference_code":inv_crno,
#              "reference_text":"SG",
#              "module":3}]
#
#
# module no will change
#
#
# ****************************************
#
# status update
#
# http://127.0.0.1:8000/prsnserv/internalprovision?action=ignore&MODULE_NO=3&REF_NO=212244  - get
import json
from datetime import datetime

import requests

# from sgservice.controller.sgecfcontroller import ecf_pdf_generate
from nwisefin.settings import SERVER_IP
from taservice.data.response.payment_resp import Payment_resp
from taservice.models import Glmapping, TourRequest, Ccbs, TourAdvance as TourAdvanceModel
from taservice.service.touradvance import TourAdvance
# from userservice.controller.authcontroller import get_authtoken
# from nwisefin.settings import SERVER_IP
# from utilityservice.service.dbutil import DataBase

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.ta_api_service import ApiService
from nwisefin import settings
vysfin_url = settings.VYSFIN_URL
from utilityservice.service.threadlocal import NWisefinThread
class Payment(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)
    def provision(self,request,list):
        data_array=[]

        for data in list:
            if data['type']=="ADVANCE":

                gl_map=Glmapping.objects.using(self._current_app_schema()).get(category_description__icontains=data ['category_description'],entity_id=self._entity_id())
                emp_data=TourRequest.objects.using(self._current_app_schema()).get(id=data ['tour_id'],entity_id=self._entity_id())
                ccbs_list = Ccbs.objects.using(self._current_app_schema()).filter(tour_id=data ['tour_id'], ccbs_type=1,requestid=data ['adv_id'],entity_id=self._entity_id())

                ref_code=data['ref_code']
                for ccbs_data in ccbs_list:
                    resp = Payment_resp()
                    resp.set_category_id(gl_map.categorycode)
                    resp.set_subcategory_id(gl_map.subcategorycode)
                    resp.set_gl_id(gl_map.glno)
                    resp.set_branch_id(emp_data.empbranchgid)
                    resp.set_narration(gl_map.gl_description)
                    resp.set_vendor_id(0)
                    resp.set_expense_date(datetime.today())
                    resp.set_amount(ccbs_data.amount)
                    resp.set_gst_amount(0)
                    resp.set_cc_id(ccbs_data.ccid)
                    resp.set_bs_id(ccbs_data.bsid)
                    resp.set_reference_code(ref_code)
                    resp.set_reference_text('reference_text')
                    resp.set_module(6)
                    dict_data=json.loads(resp.get())
                    data_array.append(dict_data)

            elif type =="CLAIM":
                ref_code = data['ref_code']
                gl_map = Glmapping.objects.using(self._current_app_schema()).get(category_description__icontains=data['category_description'],sub_category_description__icontains=data['sub_category_description']
                                               ,gender=data['gender'],entity_id=self._entity_id())
                emp_data = TourRequest.objects.using(self._current_app_schema()).get(id=data['tour_id'],entity_id=self._entity_id())
                ccbs_list = Ccbs.objects.using(self._current_app_schema()).filter(tour_id=data['tour_id'], ccbs_type=2, requestid=0,entity_id=self._entity_id())

                for ccbs_data in ccbs_list:
                    resp = Payment_resp()
                    resp.set_category_id(gl_map.categorycode)
                    resp.set_subcategory_id(gl_map.subcategorycode)
                    resp.set_gl_id(gl_map.glno)
                    resp.set_branch_id(emp_data.empbranchgid)
                    resp.set_narration(gl_map.gl_description)
                    resp.set_vendor_id(0)
                    resp.set_expense_date(datetime.today)
                    resp.set_amount(ccbs_data.amount)
                    resp.set_gst_amount(0)
                    resp.set_cc_id(ccbs_data.ccid)
                    resp.set_bs_id(ccbs_data.bsid)
                    resp.set_reference_code(ref_code)
                    resp.set_reference_text('reference_text')
                    resp.set_module(6)
                    dict=json.loads(resp.get())
                    data_array.append(dict)

        params=''
        token=request.headers['Authorization']
        headers = {"content-type": "application/json", "Authorization": "" + token + ""}
        # resp_data=json.dumps(data_array)
        resp_data=json.dumps(data_array)
        provision_url = SERVER_IP+'/prsnserv/internalprovision'
        resp = requests.post(provision_url, params=params, data=resp_data, headers=headers, verify=False)
        results = resp.content.decode("utf-8")
        # results = json.loads(results)
        return results

    # def advance_payment_process(self,adv_id,ecf_no,emp_id):
    #     service=Payment()
    #     crn_no=service.get_crnno(ecf_no,emp_id)
    #     adv_service=TourAdvance()
    #     adv_update=adv_service.advance_invoice(adv_id,ecf_no,crn_no)
    #     return adv_update

    # def advance_paid(self,crn_no,adjust_amount):
    #     TourAdvanceModel.objects.using(self._current_app_schema()).filter(crnno=crn_no).update(adjustamount=adjust_amount)




    # def get_crnno(self,ecf_no,emp_id):
    #     crn_no=ecf_pdf_generate(ecf_no,emp_id)
    #     return crn_no

    def recovery_summary(self,request,data,empid):

        empdtl = ApiService(self._scope())
        employee = empdtl.employee_details_get(empid,request)
        if data['Employee_gid'] !='':
            emp_code = employee.code
        else:
            emp_code=''
        branch = empdtl.get_branch_data(employee.employee_branch_id, request)

        if data['Branch_code'] is None:
            if branch.code=="1903":
                branch_code=''
            else:
                branch_code = branch.code
        else:
            branch_code=data['Branch_code']

        data={ "Employee_code": emp_code,
               "Employee_gid": "",
               "Branch_code":branch_code,
               "Branch_gid": "",
               "Invoice_No": data['Invoice_No'] }

        ecf_service = ApiService(self._scope())
        token = "Bearer  " + ecf_service.get_authtoken(request)
        # token = "Bearer  " + get_authtoken()
        mono_url = vysfin_url+'AP_TA_Recovery_Get'
        params=''
        headers = {"content-type": "application/json", "Authorization": "" + token + ""}
        resp = requests.post(mono_url, params=params, data=json.dumps(data), headers=headers, verify=False)
        results = resp.content.decode("utf-8")
        # results = json.loads(results)
        # print(results)
        return results

    def recovery_get_jv(self,request,data,empid):
        data={"Invoice_crnno": data['Invoice_crnno'],
              "Balanceamt": data['Balanceamt']}

        mono_url=vysfin_url+'JV_eClaim_Recovery_Get_API'
        ecf_service = ApiService(self._scope())
        token = "Bearer  " + ecf_service.get_authtoken(request)
        params = ''
        headers = {"content-type": "application/json", "Authorization": "" + token + ""}
        resp = requests.post(mono_url, params=params, data=data, headers=headers, verify=False)
        results = resp.content.decode("utf-8")
        # results = json.loads(results)
        return results


