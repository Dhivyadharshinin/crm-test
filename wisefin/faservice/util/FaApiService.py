import json
import logging

from django.db.models import QuerySet

from entryservice.service.entryservice import EntryService
from entryservice.service.faentrytemplateservice import FATemplateService
from masterservice.service.apcategoryservice import CategoryService
from masterservice.service.apsubcategoryservice import SubcategoryService
from masterservice.service.ccbsservice import BusinessSegmentService
from masterservice.service.codegenservice import CodegeneratorService
from masterservice.service.customerservice import CustomerService
from masterservice.service.pincodeservice import PincodeService
from masterservice.service.productservice import ProductService
from masterservice.service.stateservice import StateService
from userservice.controller.employeebranchcontroller import fetch_employeebranchdata_code
from userservice.service.branchservice import EmployeeBranchService
from userservice.service.employeeservice import EmployeeService
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from vendorservice.service.supplierservice import ContactService
from vendorservice.service.vendorservice import VendorService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from wisefinapi.docservapi import DocAPI
from wisefinapi.employeeapi import EmployeeAPI
from wisefinapi.masterapi import MasterAPI
from wisefinapi.vendorapi import VendorAPI
from docservice.service.documentservice import DocumentsService
MICRO_SERVICE = True
#Create method in both classes(ServiceCAll and ApiCall) With same name and same number of parameter.
#Give unused parameters with (=None) to avoid parameter Error
#Condition to Set create Service Object or API Object
class FaApiService:
    def __new__(self,scope=None):
        if MICRO_SERVICE:
            cls_obj=ServiceCall(scope)
        else:
            cls_obj=ApiCall(scope)
        return cls_obj



#Calling Services Directly.Enable by Setting MICRO_SERVICE=True
#samplecommit
class ServiceCall(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
        self.bs_obj = BusinessSegmentService(scope)
        self.ven_obj = VendorService(scope)
        self.sup_obj = ContactService(scope)
        self.apsub_obj = SubcategoryService(scope)
        self.apcat_obj = CategoryService(scope)
        self.emp_obj = EmployeeService(scope)
        self.emp_branch = EmployeeBranchService(scope)
        self.state_obj = StateService(scope)
        self.prd_obj = ProductService(scope)
        self.pin_obj = PincodeService(scope)
        self.vys_page = NWisefinPage(1, 10)
        self.cust_obj = CustomerService(scope)
        self.code_gen_obj = CodegeneratorService(scope)
        self.doc_serv = DocumentsService(scope)
        self.entry_serv=FATemplateService(scope)
        self.entry_serv_create=EntryService(scope)
    scope=None
    def get_state_from_id(self,state_id,request=None):
        return self.state_obj.fetchstate(state_id)
    def get_emp_branch(self,userid,request=None):

        print(self.emp_branch.current_emp_branch(userid))
        return self.emp_branch.current_emp_branch(userid)
    def get_empid_from_userid(self,userid,request=None):
        return self.emp_obj.get_empid_from_userid(userid)
    def fetchsubcategory(self,subcatid,request=None):
        return self.apsub_obj.fetchsubcategory(subcatid)
    def fetch_code_subcategory(self,subcat_code,request=None):
        return self.apsub_obj.fetch_apsubcategory_code(subcat_code)
    def search_subcategory(self,vys_page,searchgl,user_id=0):
        return self.apsub_obj.search_subcategory(self,vys_page,searchgl)
    def fetchcategory(self, subcatid, request=None):
        return self.apcat_obj.fetchcategory(subcatid)
    def fetchcategory_dep(self, request=None):
        return self.apcat_obj.categorylistActive_dep()
    def fetchsubcategory_dep(self, request=None):
        return self.apsub_obj.fetch_subcategory_list_dep()
    def fetch_businesssegment_list(self,vysfin_page):
        return self.bs_obj.fetch_businesssegment_list(vysfin_page)
    def fetch_data(self,id,request=None):
        return self.sup_obj.fetch_supplier(id)
    def fetch_data_code(self,id,request=None):
        logging.error("FA_SUPPLIER_DATA_FETCH: "+str(id))
        return self.sup_obj.fetch_supplier_code(id)
    def fetch_product(self,product_id,user_id,request=None):
        return self.prd_obj.fetch_product(product_id,user_id)
    def fetch_product_code(self,product_id,user_id,request=None):
        logging.error("FA_CLEARING_PRODUCT_CODE:"+str(product_id))
        data=self.prd_obj.fetch_product_code(product_id,user_id).__dict__
        logging.error("FA_CLEARING_PRODUCT_DATA:" + str(data))
        return data
    def fetch_branch(self,branch_id,request=None):
        return self.emp_branch.fetch_branch(branch_id)

    def fetch_branch_code(self,branch_id,request=None):
        logging.error("FA_CLEARING_BRANCH_ID"+str(branch_id))
        dict_obj=DictObj()
        data=dict_obj.get(self.emp_branch.fetch_branch_using_code(branch_id))
        logging.error("FA_CLEARING_BRANCH_DATA:"+str(data))
        return data
    def fetch_codegenerator_list(self,params,request):
        return self.code_gen_obj.fetch_codegenerator_list(params,request)

    def fetch_codegenerator_list_new(self, params, request):
        return self.code_gen_obj.fetch_codegenerator_list_new(params, request)

    def fetch_branch_listid(self,branchlist):
        return self.emp_branch.fetch_branch_listid(branchlist)
    def fetch_product_listid(self,product_list):
        return self.prd_obj.fetch_product_listid(product_list)
    def upload_single_file(self,request_file,params,request=None):
        return self.doc_serv.upload_single_doc(request_file,params)
    def fetch_employee_address(self,branch,request=None):
        return self.emp_obj.fetch_employee_address(branch)
    def fetch_pincode_state_id(self,data,request=None):
        return self.pin_obj.fetch_pincode_state(request,data)
    def emp_branch_list(self,request=None):
        return self.emp_branch.fetch_branch_list_dep()
    def fetch_product_dep(self,request=None):
        return self.prd_obj.fetch_product_dep()
    def fetch_customer(self,cust_id,request):
        return self.cust_obj.fetch_customer_fa(cust_id,request)
    def create_codegen_detail(self,subcat_id,request):

        emp_id=request.employee_id
        return self.code_gen_obj.code_gen_details(subcat_id,emp_id)
    def asset_approve(self,id,module,request):
        return self.entry_serv.FAquerycondition_check(id,module,request.employee_id,request.scope)
    def asset_approve_cr(self,id,module,request):
        return self.entry_serv.FAqueryconditioncr_check(id,module,request.employee_id,request.scope)
    def asset_entry_create(self,request,emp_id,entry_obj):
            return self.entry_serv_create.create_entrydetails(request,emp_id,entry_obj)
#Call Services Through API. Enable by Setting MICRO_SERVICE=False

class ApiCall(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
    doc_serv=DocAPI()
    mst_api_obj=MasterAPI()
    emp_api_obj = EmployeeAPI()
    ven_api_obj = VendorAPI()
    def get_state_from_id(self,state_id,request=None):
        return self.mst_api_obj.fetch_state(request,state_id)
    def get_emp_branch(self,userid,request=None):
        emp_id=self.emp_api_obj.branch_using_user()
        return emp_id
    def get_empid_from_userid(self,userid,request):
        return self.emp_api_obj.get_emp_by_userid(request,userid)['id']
    def fetchsubcategory(self,subcategory_id,request=None,data=None):
        if data !=None:
            dict_obj=DictObj()
            return  dict_obj.get_obj(self.mst_api_obj.get_apsubcatdetails_data(request, [subcategory_id])[0])
        else:
            sub=self.mst_api_obj.get_apsubcatdetails_data(request,[subcategory_id])[0]
            return [sub['id'],sub]
    def fetchcategory(self,cat,request=None,data=None):
        if data !=None:
            dict_obj=DictObj()
            return  dict_obj.get_obj(self.mst_api_obj.fetch_apcategorydata(request, [cat])[0])
        else:
            data=self.mst_api_obj.fetch_apcategorydata(request,cat[1]['category_id'])
            return data['id']
    def fetchcategory_dep(self, request=None):
        return self.mst_api_obj.categorylistActive_dep()
    def fetchsubcategory_dep(self, request=None):
        return self.mst_api_obj.subcategorylistActive_dep(request)
    def fetch_businesssegment_list(self, vysfin_page):
        return self.mst_api_obj.get_bs_list()
    def fetch_data_code(self,id,request=None):
        return self.ven_api_obj.fetch_vendor_data_code(id,request)
    def fetch_data(self,id,request):
        return self.ven_api_obj.get_supplierid(request,id)
    def fetch_product(self,product_id,user_id,request=None):
        return self.mst_api_obj.get_product_using_id(request,product_id)
    def fetch_product_dep(self,request=None):
        return self.mst_api_obj.get_product_dep(request)
    def fetch_product_code(self,product_id,user_id,request=None):
        return self.mst_api_obj.get_product_using_code(request,product_id)
    def fetch_customer(self,product_id,request=None):
        return self.mst_api_obj.get_product_using_code(request,product_id)
    def fetch_branch(self,branch_id,request):
        dict_obj=DictObj()
        data=dict_obj.get(self.emp_api_obj.empbranch_using_id(request,branch_id))
        return data
    def fetch_branch_code(self,branch_id,request):
        dict_obj=DictObj()
        data=dict_obj.get(self.emp_api_obj.empbranch_using_code(request,branch_id))
        return data
    def fetch_code_subcategory(self,subcat_code,request=None):
        return self.mst_api_obj.get_subcatcode(request,subcat_code)
    def fetch_codegenerator_list(self, params, request):
        return self.mst_api_obj.fetch_codegen_list(params, request)
    def upload_single_file(self,request_file,params,request):
        return self.doc_serv.upload_single_doc(request_file,params,request)
    def fetch_employee_address(self,branch,request):
        return self.emp_api_obj.fetch_ebranchaddressdata(request,branch)
    def fetch_pincode_state_id(self,data,request=None):
        return self.mst_api_obj.fetch_pincode_state(request,data)
    def emp_branch_list(self,request=None):
        return self.emp_api_obj.fetch_branch_list_dep(request)
    def get_emp_branch_ctrl(self,request):
        emp_id=self.emp_api_obj.get_branch_ctrloffice(request)
        return emp_id

    def create_codegen_detail(self, subcat_id, request):
        emp_id=request.employee_id
        data={
            'subcat_id':subcat_id,
            'url':1
        }
        self.mst_api_obj.create_codegen_detail(data,request,emp_id)
    def asset_approve(self,id,module,request):
        return self.mst_api_obj.asset_approve_api(id,module,request.employee_id,request)
    def asset_entry_create(self,request,emp_id,entry_obj):
        return self.mst_api_obj.create_entrydetails(request,emp_id,entry_obj)
from django.db.models import QuerySet
class DictObj:
    queryset_data=[]
    result_set=[]
    def get(self,dict1):
        if isinstance(dict1,str):
            dict1=json.loads(dict1)
        self.__dict__.update(dict1)
        return self.__dict__
    def get_obj(self,dict1):
        if isinstance(dict1,QuerySet):

            for data in dict1:
                self.__dict__.update(data)
                self.queryset_data.append(self)
            return self.queryset_data
        else:
            self.__dict__.update(dict1)
            return self

    def values_list(self, field):
        for data in self.queryset_data:
            for key, value in data.items():
                if key == field:
                    self.result_set.append(value)
        return self.result_set
    # class DictObj:
    #     queryset_data = []
    #     result_set = []
    #
    #     def get(self, dict1):
    #         if isinstance(dict1, str):
    #             dict1 = json.loads(dict1)
    #         self.__dict__.update(dict1)
    #         return self.__dict__
    #
    #     def get_obj(self, dict1):
    #         if isinstance(dict1, QuerySet):
    #             for data in dict1:
    #                 self.__dict__.update(data)
    #                 self.queryset_data.append(self)
    #             return self.queryset_data
    #         else:
    #             self.__dict__.update(dict1)
    #             return self
    #
    #     def values_list(self, field):
    #         for data in self.queryset_data:
    #             for key, value in data.items():
    #                 if key == field:
    #                     self.result_set.append(value)
    #         return self.result_set
    #test