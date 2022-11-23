from docservice.service.documentservice import DocumentsService
from masterservice.service.clientcodeservice import ClientcodeService
from taservice.util.ta_util import DictObj
from masterservice.service.ccbsservice import CostCentreService, BusinessSegmentService
from utilityservice.permissions.filter.commonpermission import ModulePermission
from wisefinapi.docservapi import DocAPI
from wisefinapi.employeeapi import EmployeeAPI
import json
from userservice.service.employeeservice import EmployeeService, TA_employee_service
from masterservice.service.customerservice import CustomerService
from userservice.controller.authcontroller import get_authtoken
from wisefinapi.masterapi import MasterAPI
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace


class ApiService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)

    MICRO_SERVICE = True

    def get_emp_id(self,request,emp_id):
        if self.MICRO_SERVICE:
            emp_ser = EmployeeService(self._scope())
            emp = emp_ser.get_employee_from_userid(emp_id)
            emp=emp.__dict__
            return emp
        else:
            emp_api=EmployeeAPI()
            emp = emp_api.get_emp_by_userid(request, emp_id)
            return emp

    def get_RM_ID(self,request,emp_id):
        if self.MICRO_SERVICE:
            emp_ser = EmployeeService(self._scope())
            emp = emp_ser.get_employee_RMID(emp_id)
            # emp=emp.__dict__
            return emp
        # else:
        #     emp_api=EmployeeAPI()
        #     emp = emp_api.get_emp_by_userid(request, emp_id)
        #     return emp
    def get_rm_emp(self,request,emp_id):
        if self.MICRO_SERVICE:
            emp_ser = EmployeeService(self._scope())
            emp = emp_ser.get_rm_employee(emp_id)
            # emp=emp.__dict__
            return emp
        # else:
        #     emp_api=EmployeeAPI()
        #     emp = emp_api.get_emp_by_userid(request, emp_id)
        #     return emp
    def get_functional_head(self,request,emp_id):
        if self.MICRO_SERVICE:
            emp_ser = EmployeeService(self._scope())
            emp = emp_ser.get_employee_functionalhead(emp_id)
            # emp=emp.__dict__
            return emp
        # else:
        #     emp_api=EmployeeAPI()
        #     emp = emp_api.get_emp_by_userid(request, emp_id)
        #     return emp
    def employee_modulerole_get(self,emp_id,module,request):
        if self.MICRO_SERVICE:
            module_permission = ModulePermission(self._scope())
            role_arr = module_permission.employee_modulerole(emp_id,module)
            # emp=emp.__dict__
            return role_arr
        # else:
        #     emp_api=EmployeeAPI()
        #     emp = emp_api.get_emp_by_userid(request, emp_id)
        #     return emp


    def employee_details_get(self,emp_id,request):
        if self.MICRO_SERVICE:
            emp_ser = TA_employee_service(self._scope())
            emp = emp_ser.employee_details_get(emp_id)
            # emp=emp.__dict__
            return emp
        else:
            emp_api=EmployeeAPI()
            emp = emp_api.employee_details_get(request, emp_id)
            d_obj=DictObj()
            emp=d_obj.get_obj(emp)
            return emp

    def emp_teamid_get(self,emp_id,request):
        if self.MICRO_SERVICE:
            emp_ser = TA_employee_service(self._scope())
            emp = emp_ser.employee_teamdetails_get(emp_id)
            return emp

    def employee_details_arr(self,emp_id,request):
        if self.MICRO_SERVICE:
            emp_ser = TA_employee_service(self._scope())
            emp = emp_ser.employee_details_arr(emp_id)
            # emp=emp.__dict__
            return emp
        # else:
        #     emp_api=EmployeeAPI()
        #     emp = emp_api.employee_details_get(request, emp_id)
        #     d_obj=DictObj()
        #     emp=d_obj.get_obj(emp)
        #     return emp


    def get_branch_data(self,branch,request):
        if self.MICRO_SERVICE:
            emp_ser = TA_employee_service(self._scope())
            emp = emp_ser.get_branch_data(branch)
            return emp
        else:
            emp_api=EmployeeAPI()
            emp = emp_api.get_branch_data(request,branch)
            d_obj = DictObj()
            emp = d_obj.get_obj(emp)
            return emp
    def get_address_data(self,addressid,request):
        if self.MICRO_SERVICE:
            emp_ser = TA_employee_service(self._scope())
            emp = emp_ser.get_address_data(addressid)
            return emp
        # else:
        #     emp_api=EmployeeAPI()
        #     emp = emp_api.get_branch_data(request,branch)
        #     d_obj = DictObj()
        #     emp = d_obj.get_obj(emp)
        #     return emp

    def get_branch_data_empid(self,empid,request):
        if self.MICRO_SERVICE:
            emp_ser = EmployeeService(self._scope())
            branch_data = emp_ser.get_employee_detail(empid)
            if len(branch_data)==0:
                branch_data={'branch_code': None, 'branch_id': None, 'branch_name': None, 'code': None,
                 'employe_name': None, 'full_name':None, 'id': None}
                return branch_data
            else:
                branch_data=json.loads(branch_data[0])
                return branch_data
        else:
            emp_api=EmployeeAPI()
            emp = emp_api.fetch_employee_branch(request,empid[0])
            return emp


    def role_bh_emp_get(self,branch,approver,approver_except,request):
        if self.MICRO_SERVICE:
            emp_ser = TA_employee_service(self._scope())
            emp = emp_ser.role_bh_emp_get(branch,approver,approver_except)
            return emp
        else:
            emp_api=EmployeeAPI()
            emp = emp_api.role_bh_emp_get(branch,approver,approver_except,request)
            return emp

    def get_cc_details(self,id,request):
        if self.MICRO_SERVICE:
            emp_ser = CostCentreService(self._scope())
            emp = emp_ser.fetch_costcentre(id)
            # emp=emp.__dict__
            return emp
        else:
            emp_api=EmployeeAPI()
            emp = emp_api.cc_get(request, [id])
            emp=emp[0]
            d_obj = DictObj()
            emp = d_obj.get_obj(emp)
            return emp

    def get_bs_details(self,id,request):
        if self.MICRO_SERVICE:
            emp_ser = BusinessSegmentService(self._scope())
            emp = emp_ser.fetch_businesssegment(id)
            # emp=emp.__dict__
            return emp
        else:
            emp_api=EmployeeAPI()
            emp = emp_api.bs_get(request, [id])
            emp=emp[0]
            d_obj = DictObj()
            emp = d_obj.get_obj(emp)
            return emp


    def state_id(self,cityname,request):
        if self.MICRO_SERVICE:
            city_ser = CustomerService(self._scope())
            state = city_ser.city_name(cityname)
            return state
        else:
            mst_api=MasterAPI()
            emp = mst_api.city_name( request,cityname)
            return emp.text
    def city_name(self,cityid,request):
        if self.MICRO_SERVICE:
            city_ser = CustomerService(self._scope())
            state = city_ser.ta_city_id(cityid)
            return state
        # else:
        #     mst_api=MasterAPI()
        #     emp = mst_api.city_name( request,cityname)
        #     return emp.text
    def city_dropdown(self,request,city_name,vys_page):
        if self.MICRO_SERVICE:
            city_ser = CustomerService(self._scope())
            state = city_ser.ta_city_dropdown(request,city_name,vys_page)
            return state
        # else:
        #     mst_api=MasterAPI()
        #     emp = mst_api.city_name( request,cityname)
        #     return emp.text

    def emp_branch(self,request,city_name,vys_page):
        if self.MICRO_SERVICE:
            city_ser = TA_employee_service(self._scope())
            state = city_ser.branch_dropdown(city_name,vys_page)
            return state
        # else:
        #     mst_api=MasterAPI()
        #     emp = mst_api.city_name( request,cityname)
        #     return emp.text


    # def ecf_category_code(self,tour_reason,request):
    #     if self.MICRO_SERVICE:
    #         emp_ser = CustomerService(self._scope())
    #         emp = emp_ser.ecf_category_code_nac(tour_reason)
    #         return emp
    #     else:
    #         mst_api=MasterAPI()
    #         emp = mst_api.ecf_category_code( request,id)
    #         return emp.text

    def ecf_subcategory_code(self,id,request):
        if self.MICRO_SERVICE:
            emp_ser = CustomerService(self._scope())
            emp = emp_ser.ecf_subcategory_code(id)
            return emp
        else:
            mst_api=MasterAPI()
            emp = mst_api.ecf_subcategory_code( request,id)
            return emp.text

    def cat_no_get(self,no,request):
        if self.MICRO_SERVICE:
            cat_service = CustomerService(self._scope())
            cat_data = cat_service.ap_cat_no_get(no)
            return cat_data
        else:
            mst_api=MasterAPI()
            emp = mst_api.cat_no_get( request,no)
            return emp.text

    def sub_cat_no_get (self,no,cat_id,request):
        if self.MICRO_SERVICE:
            cat_service = CustomerService(self._scope())
            cat_data = cat_service.ap_subcat_no_get(no,cat_id)
            return cat_data
        else:
            mst_api=MasterAPI()
            emp = mst_api.sub_cat_no_get( request,no,cat_id)
            return emp.text

    def emp_all_details(self,empid,request):
        if self.MICRO_SERVICE:
            emp_ser = TA_employee_service(self._scope())
            emp = emp_ser.employee_all_details_get(empid)
            return emp
        else:
            emp_api=EmployeeAPI()
            emp = emp_api.employee_all_details_get(request,empid)
            d_obj = DictObj()
            emp = d_obj.get_obj(emp)
            return emp

    def get_authtoken(self, request):
        if self.MICRO_SERVICE:
            token = get_authtoken()
            print('get_authtoken serv', token)
            return token
        else:
            emp_api=EmployeeAPI()
            token = emp_api.get_authtoken(request)
            token = token["access_token"]
            print('get_authtoken api',token)
            return token

    def branch_employee_get(self,branchid,vys_page,request,maker):
        if self.MICRO_SERVICE:
            emp_ser = TA_employee_service(self._scope())
            emp = emp_ser.branch_employee_get(branchid,None,vys_page,int(maker))
            emp=emp.__dict__
            return emp
        else:
            emp_api=EmployeeAPI()
            emp = emp_api.branch_employee(branchid,request,maker)
            return emp

    # file uplosd typr-s Ste
    def doc_upload(self, request, module_id,ta_id):
        if self.MICRO_SERVICE:
            p_ser = DocumentsService(self._scope())
            p = p_ser.document_upload_ta(request, module_id,ta_id)
            p = json.loads(p.get())
            return p
        else:
            ta_apicall = DocAPI()
            #module, prefix
            doc_module = ta_apicall.doc_module_ta(request, module_id,ta_id)
            print("doc_module", doc_module)
            params = doc_module
            #s3 bucket
            document_uploadbucket = ta_apicall.document_uploadbucket_ta(request, params)
            print("document_uploadbucket", document_uploadbucket)
            document_uploadbucket=json.loads(document_uploadbucket.get())
            #doc
            doc_upload = ta_apicall.doc_upload_ta(request, document_uploadbucket)
            print("doc_upload", doc_upload)
            return doc_upload
    def ta_doc_upload(self,request,params):
        if self.MICRO_SERVICE:
            p_ser = DocumentsService(self._scope())
            p = p_ser.upload(request,params)
            return p
        else:
            emp_api=EmployeeAPI()
            emp = emp_api.branch_employee(request,params)
            return emp

    def ta_reason_catagory(self,tour_reason):
        if self.MICRO_SERVICE:
            emp_ser = CustomerService(self._scope())
            category = emp_ser.ta_reason_category(tour_reason)
            return category


    def sub_category(self,category_no,expense):
        if self.MICRO_SERVICE:
            emp_ser = CustomerService(self._scope())
            sub_category = emp_ser.ta_sub_category(category_no,expense)
            return sub_category


    def ta_commodity(self,commodity_name):
        if self.MICRO_SERVICE:
            emp_ser = CustomerService(self._scope())
            commodity = emp_ser.ta_commodity(commodity_name)
            return commodity


    def emp_accountno_ta(self,empid,request):
        if self.MICRO_SERVICE:
            emp_ser = TA_employee_service(self._scope())
            emp = emp_ser.employee_acc_no_get_ta(empid)
            return emp





    def get_client(self, request, client_id):
        if self.MICRO_SERVICE:
            client_serv = ClientcodeService(self._scope())
            resp_obj = client_serv.fetch_clientcode(client_id)
            return resp_obj
        # else:
        #     mst_api = MasterAPI()
        #     resp_obj = mst_api.client_obj(request, client_id)
        #     return resp_obj.text

    def get_client_arr(self, request, client_id):
        if self.MICRO_SERVICE:
            client_serv = ClientcodeService(self._scope())
            resp_obj = client_serv.fetch_clientcode_arr(client_id)
            return resp_obj
        # else:
        #     mst_api = MasterAPI()
        #     resp_obj = mst_api.client_obj(request, client_id)
        #     return resp_obj.text

    def onb_permission(self, request, empid):
        if self.MICRO_SERVICE:
            onb_serv = TA_employee_service(self._scope())
            resp_obj = onb_serv.check_permission_ta(empid)
            return resp_obj
        # else:
        #     mst_api = MasterAPI()
        #     resp_obj = mst_api.client_obj(request, client_id)
        #     return resp_obj.text

    def all_emp_list(self, request, query, vys_page,maker):
        if self.MICRO_SERVICE:
            onb_serv = EmployeeService(self._scope())
            resp_obj = onb_serv.search_employee_exclude_maker( request, query, vys_page,maker)
            return resp_obj
        # else:
        #     mst_api = MasterAPI()
        #     resp_obj = mst_api.client_obj(request, client_id)
        #     return resp_obj.text

    def emp_team_get(self,emp_id, request):
        if self.MICRO_SERVICE:
            onb_serv = TA_employee_service(self._scope())
            resp_obj = onb_serv.emp_team_get( emp_id)
            return resp_obj
        # else:
        #     mst_api = MasterAPI()
        #     resp_obj = mst_api.client_obj(request, client_id)
        #     return resp_obj.text
    def emp_team_arr(self,emp_id, request):
        if self.MICRO_SERVICE:
            onb_serv = TA_employee_service(self._scope())
            resp_obj = onb_serv.emp_team_arr( emp_id)
            return resp_obj
        # else:
        #     mst_api = MasterAPI()
        #     resp_obj = mst_api.client_obj(request, client_id)
        #     return resp_obj.text

    def get_team_name(self, request,team,sub_team):
        if self.MICRO_SERVICE:
            serv = TA_employee_service(self._scope())
            resp_obj = serv.team_name(team,sub_team)
            return resp_obj
        # else:
        #     mst_api = MasterAPI()
        #     resp_obj = mst_api.client_obj(request, client_id)
        #     return resp_obj.text

    def cc_data(self):
        if self.MICRO_SERVICE:
            serv = CostCentreService(self._scope())
            resp_obj = serv.cc_data_frame()
            return resp_obj
        # else:
        #     mst_api = MasterAPI()
        #     resp_obj = mst_api.client_obj(request, client_id)
        #     return resp_obj.text

    def bs_data(self):
        if self.MICRO_SERVICE:
            serv = BusinessSegmentService(self._scope())
            resp_obj = serv.bs_data_frame()
            return resp_obj
        # else:
        #     mst_api = MasterAPI()
        #     resp_obj = mst_api.client_obj(request, client_id)
        #     return resp_obj.text
    def get_emp_name(self,request,emp_name):
        if self.MICRO_SERVICE:
            emp_ser = TA_employee_service(self._scope())
            emp = emp_ser.emp_id_get(emp_name)
            # emp=emp.__dict__
            return emp
        # else:
        #     emp_api=EmployeeAPI()
        #     emp = emp_api.employee_details_get(request, emp_id)
        #     d_obj=DictObj()
        #     emp=d_obj.get_obj(emp)
        #     return emp
    def get_emp_branchid(self,request,emp_name):
        if self.MICRO_SERVICE:
            emp_ser = TA_employee_service(self._scope())
            emp = emp_ser.emp_branchid(emp_name)
            # emp=emp.__dict__
            return emp
        # else:
        #     emp_api=EmployeeAPI()
        #     emp = emp_api.employee_details_get(request, emp_id)
        #     d_obj=DictObj()
        #     emp=d_obj.get_obj(emp)
        #     return emp


    def frequent_clientlist_ta(self,vys_page,query,frequent_client_data):
        if self.MICRO_SERVICE:
            emp_ser = ClientcodeService(self._scope())
            emp = emp_ser.frequent_clientlist_ta(vys_page,query,frequent_client_data)
            # emp=emp.__dict__
            return emp
        # else:
        #     emp_api=EmployeeAPI()
        #     emp = emp_api.employee_details_get(request, emp_id)
        #     d_obj=DictObj()
        #     emp=d_obj.get_obj(emp)
        #     return emp
