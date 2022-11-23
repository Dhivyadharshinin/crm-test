import json
import requests
from nwisefin.settings import logger
from vendorservice.service.vowservice import VOWService
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessMessage
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from cmsservice.service.projectquestionservice import Projectquesservice
from cmsservice.models.cmsmodels import ProposedContract,ProposerVendorMapping
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from cmsservice.util.cmsutil import ActiveStatus,ApprovalStatus
from django.db.models import Q
from cmsservice.service.quesansservice import Quesansservice
# from nwisefin.settings import vow_url
vow_url = 'http://143.110.244.51:8189/'

class VowEmployeeService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.CMS_SERVICE)

    def get_vow_employee_info(self, arr):
        datas = {"arr": arr}
        api_name = vow_url + 'usrserv/port_user'
        headers = {"content-type": "application/json"}
        resp = requests.post(api_name, data=datas, headers=headers, verify=False)
        datas = json.loads(resp.content.decode("utf-8"))
        vow_info = datas.get("data")

        return vow_info

    def vendor_get(self, request):
        vendor_code = request.GET.get('vendor_code')
        api_name = vow_url + 'venserv/branch_get?code=' + str(vendor_code)
        print("api_name", api_name)
        headers = {"content-type": "application/json"}
        resp = requests.get(api_name, headers=headers, verify=False)
        print("resp", resp)
        logger.info("venserv/branch_get?code -- resp : " + str(resp))
        if resp.status_code != 200:
            error_obj = "Error On Vendor Api Call"
            return error_obj
        ven_resp = resp.text
        return ven_resp

    def proposal_vendorcreate(self, request, proposal_id):
        emp_id = request.employee_id
        scope = request.scope
        # vendor_code = request.GET.get('vendor_code')

        proposal_obj=ProposedContract.objects.using(self._current_app_schema()).filter(id=proposal_id,status=ActiveStatus.Active)

        # to check ProposedContract is active
        if len(proposal_obj)==0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD Proposer id ")
            return error_obj

        proposal_obj = proposal_obj[0]
        approval_status =proposal_obj.approval_status
        proposer_code = proposal_obj.proposer_code
        is_vendor = proposal_obj.is_vendor

        if is_vendor == True:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("vendor / activity  already created")
            return error_obj

        cond =Q(vendor_code=proposer_code)
        ven_pro_map=ProposerVendorMapping.objects.using(self._current_app_schema()).filter(proposer_code=cond)

        is_vendor=False
        if len(ven_pro_map)!=0:
            is_vendor = True
        # check is vendor by  code
        elif 'PA' in proposer_code :
            is_vendor = True

        # to check ProposedContract is approved
        if approval_status != ApprovalStatus.APPROVED:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD DATA")
            return error_obj

        vow_serv = VOWService(scope)
        proj_que_serv = Projectquesservice(scope)
        vendor_code=None
        # Activity create
        if is_vendor == True:
            actv_resp = proj_que_serv.fetch_proposalvendor_proposal(request, proposal_id)
            activity_name = actv_resp.name
            activity_type = actv_resp.type
            productname = actv_resp.productname['id']
            category = actv_resp.category.id
            subcategory = actv_resp.subcategory.id

            activity = {"name": activity_name, "type": activity_type}
            catelog = {"product_name": productname, "catelog_category": category, "catelog_subcategory": subcategory}
            vendor_details = {"activity": activity,
                              "catelog": catelog, "created_by": emp_id}

            # call activity create function
            activity_data = vow_serv.insert_activity(vendor_details, vendor_code)
            print("activity create:", activity_data)

            proposal_obj = ProposedContract.objects.using(self._current_app_schema()).filter(id=proposal_id,status=ActiveStatus.Active).update(is_vendor=True)

            success_obj = NWisefinSuccess()
            success_obj.set_status("Activity Created Successfully")
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return success_obj

        # vendor creation
        else:
            # vendor details from vow
            vow_get = self.vendor_get(request)
            vendor_data = json.loads(vow_get)
            print(vendor_data)
            name = vendor_data['name']
            panno = vendor_data['pan_no']
            gstno = vendor_data['gst_no']
            created_by = emp_id

            address = {"line_1": vendor_data['address_id']['line1'], "line_2": vendor_data['address_id']['line2'],
                       "line_3": vendor_data['address_id']['line3'],
                       "pincode_id": vendor_data['address_id']['pincode_id']['id'],
                       "city_id": vendor_data['address_id']['city_id']['id'],
                       "district_id": vendor_data['address_id']['district_id']['id'],
                       "state_id": vendor_data['address_id']['state_id']['id']}
            print("address", address)
            contact = {"name": vendor_data['contact_id']['name'],
                       "designation": vendor_data['contact_id']['designation'],
                       "mobile_1": vendor_data['contact_id']['mobile_1'],
                       "mobile_2": vendor_data['contact_id']['mobile_2'],
                       "email": vendor_data['contact_id']['email']}
            print("contact", contact)
            actv_resp = proj_que_serv.fetch_proposalvendor_proposal(request, proposal_id)
            activity_name = actv_resp.name
            activity_type = actv_resp.type
            productname = actv_resp.productname['id']
            category = actv_resp.category.id
            subcategory = actv_resp.subcategory.id
            print("actv_resp.rm", actv_resp.rm)
            rm_id = actv_resp.rm['id']
            rm_name = actv_resp.rm['full_name']

            rm_id = {"id": rm_id, "name": rm_name}
            activity = {"name": activity_name, "type": activity_type}
            catelog = {"product_name": productname, "catelog_category": category, "catelog_subcategory": subcategory}
            vendor_details = {"rm_id": rm_id, "address": address, "contact": contact, "activity": activity,"catelog": catelog,"name": name, "panno": panno, "gstno": gstno, "created_by": created_by}

            resp_data = vow_serv.insert_approved_vendor(vendor_details)
            print("vendor create api resp:", resp_data)
            # vendor - proposer mapping
            ProposerVendorMapping.objects.using(self._current_app_schema()).create(proposer_code=proposer_code,vendor_code=resp_data.vendor_code,created_by=emp_id)
            # questionary
            vendor_id = resp_data.vendor_id
            Quesansservice(scope).questionarier_to_vendor(proposal_obj,vendor_id)
            # IS VENDOR update
            ProposedContract.objects.using(self._current_app_schema()).filter(id=proposal_id,status=ActiveStatus.Active).update(is_vendor=True)


            success_obj = NWisefinSuccess()
            success_obj.set_status("Vendor Created Successfully")
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return success_obj