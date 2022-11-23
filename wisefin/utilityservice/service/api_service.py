from apservice.service.ppxdetailsservice import APppxDetailsService
from docservice.service.documentservice import DocumentsService
from entryservice.service.entryoracleservice import EntryOracleService
from entryservice.service.entryservice import EntryService
from masterservice.service import ccbsservice
from masterservice.service.bankbranchservice import BankBranchService
from masterservice.service.bsproductservice import BsproductService
from masterservice.service.cityservice import CityService
from masterservice.service.clientcodeservice import ClientcodeService
from masterservice.service.counrtyservice import CountryService
from masterservice.service.districtservice import DistrictService
from masterservice.service.pincodeservice import PincodeService
from masterservice.service.productservice import ProductService
from masterservice.service.questionheaderservice import QuestionheaderService
from masterservice.service.questionservice import QuestionService
from masterservice.service.questionsubservice import QuestionsubService
from masterservice.service.questiontypeservice import QuestiontypeService
from masterservice.service.taxservice import TaxMasterService
from masterservice.service.uomservice import UomService
from nwisefin.settings import logger
from userservice.service import employeeservice
from masterservice.service.commodityservice import CommodityService
from masterservice.service.stateservice import StateService
from masterservice.service.bankservice import BankService
from masterservice.service.paymodeservice import PaymodeService
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
# from vendorservice.service.paymentservice import paymentservice
#test
from vendorservice.service.supplierservice import ContactService
from masterservice.service.apcategoryservice import CategoryService
from masterservice.service.apsubcategoryservice import SubcategoryService
from masterservice.service.Hsnservice import Hsnservice
from wisefinapi.vendorapi import VendorAPI
from wisefinapi.employeeapi import EmployeeAPI
from wisefinapi.masterapi import MasterAPI
import json
from vendorservice.service.vendoraddressservice import VendorAddressService
from vendorservice.service.suppliertaxservice import TaxService
from masterservice.service.subtaxservice import SubTaxService
from masterservice.service.taxrateservice import TaxRateService
from taservice.util.ta_util import DictObj
from userservice.service.employeeservice import TA_employee_service
from userservice.service.departmentservice import DepartmentService
from masterservice.service.designationservice import DesignationService
from userservice.service.branchservice import EmployeeBranchService
class ApiService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ECF_SERVICE)

    MICRO_SERVICE = True

    def get_emp_id(self,request,emp_id):
        if self.MICRO_SERVICE:
            emp_ser = employeeservice.EmployeeService(self._scope())
            emp = emp_ser.get_employee_from_userid(emp_id)
            emp=emp.__dict__
            emp['name']=emp['full_name']
            print('data',emp)
            return emp
        else:
            emp_api=EmployeeAPI()
            emp = emp_api.get_emp_by_userid(request, emp_id)
            print('data2',emp)
            return emp
            # employeeservice.get employedetail Micro-Micro

    def get_empsingle_id(self, request, emp_id):
        if self.MICRO_SERVICE:
            emp_ser = employeeservice.EmployeeService(self._scope())
            emp = emp_ser.fetch_employee_by_empid(emp_id)
            return emp
        else:
            emp_api = EmployeeAPI()
            emp = emp_api.get_emp_by_empid(request, emp_id)
            print('empsingle', emp)
            return emp
    def get_emp_grade(self, request, emp_id):
        if self.MICRO_SERVICE:
            emp_ser = employeeservice.EmployeeService(self._scope())
            emp = emp_ser.fetch_employee_grade(emp_id)
            return emp
        else:
            emp_api = EmployeeAPI()
            emp = emp_api.get_emp_by_empid(request, emp_id)
            print('empsingle', emp)
            return emp
    def get_empbranch_id(self, request, emp_id):
        if self.MICRO_SERVICE:
            emp_ser = employeeservice.EmployeeService(self._scope())
            emp = emp_ser.fetch_empbranch(emp_id)
            return emp
        else:
            emp_api = EmployeeAPI()
            emp = emp_api.get_empbranchid(request, emp_id)
            print('empbranhc', emp)
            return emp
    def get_empbranch_empid(self, request, emp_id):
        if self.MICRO_SERVICE:
            emp_ser = employeeservice.EmployeeService(self._scope())
            emp = emp_ser.fetch_empbranch_empid(emp_id)
            return emp
        else:
            emp_api = EmployeeAPI()
            emp = emp_api.get_empbranchid_empid(request, emp_id)
            print('empbranhc', emp)
            return emp
    def get_commodity_list(self, request, comm_id):
        if self.MICRO_SERVICE:
            commodity_ids = {"commo_id1": comm_id}
            commodity_data = json.dumps(commodity_ids, indent=2)
            com_ser = CommodityService(self._scope())
            com = com_ser.fetch_commoditylist(commodity_ids)
            com = json.loads(com)
            return com
        else:
            mst_api = MasterAPI()
            com = MasterAPI.get_commodity(self, request , comm_id)
            print('datacom3', com)
            return com
    def get_cc_code(self, request, cc_code):
        if self.MICRO_SERVICE:
            cc_ser = ccbsservice.BusinessSegmentService(self._scope())
            cc = cc_ser.fetch_cc(cc_code)
            return cc
        else:
            emp_api = EmployeeAPI()
            cc = emp_api.get_cccode(request, cc_code)
            print('cc', cc)
            return cc
    def get_bs_code(self, request, bs_code):
        if self.MICRO_SERVICE:
            cc_ser = ccbsservice.BusinessSegmentService(self._scope())
            bs = cc_ser.fetch_bs(bs_code)
            return bs
        else:
            emp_api = EmployeeAPI()
            bs = emp_api.get_bscode(request, bs_code)
            print('bs', bs)
            return bs

    def get_commosingle_id(self, request, com_id):
        if self.MICRO_SERVICE:
            com_ser = CommodityService(self._scope())
            com = com_ser.fetch_commoditys(com_id)
            return com
        else:
            master_service = MasterAPI()
            com = master_service.get_commodityid(request, com_id)
            print('commosingle', com)
            return com
    def get_statesingle_id(self, request, state_id):
        if self.MICRO_SERVICE:
            state_ser = StateService(self._scope())
            state = state_ser.fetch_stateone(state_id)
            return state
        else:
            master_service = MasterAPI()
            state = master_service.get_stateid(request, state_id)
            print('statesingle', state)
            return state
    def get_cat_code(self, request, cat_code):
        if self.MICRO_SERVICE:
            cat_ser = CategoryService(self._scope())
            cat = cat_ser.fetch_apcategory1(cat_code)
            return cat
        else:
            mst_api = MasterAPI()
            cat = mst_api.get_catcode(request, cat_code)
            print('cat', cat)
            return cat
    def get_subcat_code(self, request, subcat_code):
        if self.MICRO_SERVICE:
            subcat_ser = SubcategoryService(self._scope())
            subcat = subcat_ser.fetch_apsubcategory(subcat_code)
            return subcat
        else:
            mst_api = MasterAPI()
            subcat = mst_api.get_subcatcode(request, subcat_code)
            print('subcat', subcat)
            return subcat
    def get_bank_list(self, request, bank_id):
        if self.MICRO_SERVICE:
            bank_ids = {"bank_id": bank_id}
            bank_ser = BankService(self._scope())
            bank = bank_ser.fetch_banklist(bank_ids)
            bank = json.loads(bank)
            return bank
        else:
            mst_api = MasterAPI()
            bank = MasterAPI.get_bank(self, request , bank_id)
            print('bankdata', bank)
            return bank
    def get_paymodesingle_id(self, request, pay_id):
        if self.MICRO_SERVICE:
            paymode_ser = PaymodeService(self._scope())
            paymode = paymode_ser.fetch_paymodeone(pay_id)
            return paymode
        else:
            master_service = MasterAPI()
            paymode = master_service.get_paymodeid(request, pay_id)
            print('paymodesingle', paymode)
            return paymode
    def get_paymodeList(self,request,vys_page):
        if self.MICRO_SERVICE:
            paymode_ser = PaymodeService(self._scope())
            paymode = paymode_ser.fetch_paymode_list(vys_page)
            return paymode
        else:
            master_service = MasterAPI()
            paymode = master_service.get_paymodeList(request)
            print('paymodelist', paymode)
            return paymode


    def get_supliersingle_id(self, request, sup_id):
        if self.MICRO_SERVICE:
            sup_ser = ContactService(self._scope())
            supplier = sup_ser.fetch_supplier(sup_id)
            return supplier
        else:
            vendor_service = VendorAPI()
            supplier = vendor_service.get_supplierid(request, sup_id)
            print('suppliersingle', supplier)
            return supplier
    def get_supplier_list(self, request, supp_id):
        if self.MICRO_SERVICE:
            supp_ids = {"supplier_id": supp_id}
            supp_ser = ContactService(self._scope())
            supp = supp_ser.fetch_supplierlist(supp_ids)
            supp = json.loads(supp)
            return supp
        else:
            ven_api = VendorAPI()
            supp = ven_api.get_supplier(request , supp_id)
            print('suppdata', supp)
            return supp

    def get_hsn_code(self, request, hsn_code):
        if self.MICRO_SERVICE:
            hsn_ser = Hsnservice(self._scope())
            hsn = hsn_ser.fetch_hsnone(hsn_code)
            return hsn
        else:
            mst_api = MasterAPI()
            hsn = mst_api.get_hsncode(request, hsn_code)
            print('hsn', hsn)
            return hsn
    def get_empaddress_id(self, request, emp_id):
        if self.MICRO_SERVICE:
            emp_ser = employeeservice.EmployeeService(self._scope())
            emp = emp_ser.fetch_employee_address(emp_id)
            return emp
        else:
            emp_api = EmployeeAPI()
            emp = emp_api.get_emp_by_empid(request, emp_id)
            print('empsingle', emp)
            return emp
    def get_venaddress(self, request, add_id):
        if self.MICRO_SERVICE:
            ven_ser = VendorAddressService(self._scope())
            vendor = ven_ser.fetch_vendoraddress1(add_id)
            return vendor
        else:
            vendor_service = VendorAPI()
            supplier = vendor_service.get_supplierid(request, add_id)
            print('suppliersingle', supplier)
            return supplier

    def get_vendorsubtax_list(self, request, vendor_id):
        if self.MICRO_SERVICE:
            vendor_ids = {"vendor_id": vendor_id}
            subtax_ser = TaxService(self._scope())
            subtax = subtax_ser.fetch_subtaxlist(vendor_ids)
            subtax = json.loads(subtax)
            return subtax
        else:
            vendor_service = VendorAPI()
            subtax = vendor_service.get_subtax(request,vendor_id)
            print('subtaxdata', subtax)
            return subtax

    def get_subtax_list(self, request, subtax_id):
        if self.MICRO_SERVICE:
            subtax_ids = {"subtax_id": subtax_id}
            subtax_ser = SubTaxService(self._scope())
            subtax = subtax_ser.fetch_subtaxlist(subtax_ids)
            subtax = json.loads(subtax)
            return subtax
        else:
            mst_api = MasterAPI()
            subtax = mst_api.get_subtax(request , subtax_id)
            print('subtaxlistdata', subtax)
            return subtax
    def get_taxrate_list(self, request, subtax_id):
        if self.MICRO_SERVICE:
            subtax_ids = {"subtax_id": subtax_id}
            taxrate_ser = TaxRateService(self._scope())
            taxrate = taxrate_ser.fetch_taxratelist(subtax_ids)
            taxrate = json.loads(taxrate)
            return taxrate
        else:
            mst_api = MasterAPI()
            taxrate = mst_api.get_taxrate(request , subtax_id)
            print('taxratelistdata', taxrate)
            return taxrate

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

    def doc_upload_ecf(self, request,params,filekey):
        if self.MICRO_SERVICE:
            p_ser = DocumentsService(self._scope())
            p = p_ser.document_upload_ecf(request,params, filekey)
            logger.info("doc_upload_key - serv" + str(p))
            print("doc_upload_key - serv", p)
            p = json.loads(p.get())
            return p
        else:
           pass

    def get_hsn(self,code):
        if self.MICRO_SERVICE:
            emp_ser = Hsnservice(self._scope())
            emp = emp_ser.fetch_hsnone(code)
            return emp
        else:
            pass

    def get_uom(self,vys_page,code):
        if self.MICRO_SERVICE:
            emp_ser = UomService(self._scope())
            emp = emp_ser.fetch_uom_search(vys_page,code)
            return emp
        else:
            pass

    def get_supplierpayment(self,branch,paymode,account,emp_id):
        from vendorservice.service.paymentservice import paymentservice
        if self.MICRO_SERVICE:
            emp_ser = paymentservice(self._scope())
            emp = emp_ser.supplierpaymentacc(branch,paymode,account,emp_id)
            return emp
        else:
            pass
    def get_vendor(self,request,vys_page,emp_id,vendorId):
        if self.MICRO_SERVICE:
            emp_ser = TaxService(self._scope())
            emp = emp_ser.fetch_suppliertax_list(request,vys_page,emp_id,vendorId)
            return emp
        else:
            pass

    def get_tax(self,tax,emp_id):
        if self.MICRO_SERVICE:
            emp_ser = TaxMasterService(self._scope())
            emp = emp_ser.fetch_tax(tax,emp_id)
            return emp
        else:
            pass

    def get_bank(self,bank_id,emp_id):
        if self.MICRO_SERVICE:
            emp_ser = BankService(self._scope())
            emp = emp_ser.fetch_bank(bank_id,emp_id)
            return emp
        else:
            pass

    def get_bankList(self,data,vys_page):
        if self.MICRO_SERVICE:
            emp_ser = BankService(self._scope())
            emp = emp_ser.fetch_bank_list(vys_page,data)
            return emp
        else:
            pass

    def get_bankbranch(self, branch_id, emp_id):
        if self.MICRO_SERVICE:
            emp_ser = BankBranchService(self._scope())
            emp = emp_ser.fetch_bankbranch(branch_id, emp_id)
            return emp
        else:
            pass

    def get_bankbranch_search(self,query,branch_id,vys_page):
        if self.MICRO_SERVICE:
            emp_ser = BankBranchService(self._scope())
            emp = emp_ser.fetch_bankbranch_search(query,branch_id,vys_page)
            return emp
        else:
            mst_api = MasterAPI()
            comm = mst_api.bankbranch_api(query, branch_id)
            logger.info("get_product - api" + str(comm))
            print("get_product - api", comm)
            return comm

    def get_bankbranch_single(self,request,branch_id,vys_page):
        if self.MICRO_SERVICE:
            emp_ser = BankBranchService(self._scope())
            emp = emp_ser.bank_branch_summary(request,branch_id,vys_page)
            return emp
        else:
            pass

    def get_clicode(self,clientid):
        if self.MICRO_SERVICE:
            emp_ser = ClientcodeService(self._scope())
            emp = emp_ser.fetch_clientcode(clientid)
            return emp
        else:
            pass

    def get_bscode(self,clientid):
        if self.MICRO_SERVICE:
            emp_ser = BsproductService(self._scope())
            emp = emp_ser.fetch_bsproductcode(clientid)
            return emp
        else:
            pass
          
    def get_product(self, request, product_id):
        if self.MICRO_SERVICE:
            product_ids = {"product_id": product_id}
            comm_ser = ProductService(self._scope())
            comm = comm_ser.fetch_productlistget(product_ids)
            logger.info("get_product - serv" + str(comm))
            print("get_product - serv", comm)
            print('PRODUCT ID ARRAY SERV', comm)
            # comm = json.loads(comm.get())
            comm = json.loads(comm)
            return comm
        else:
            mst_api = MasterAPI()
            comm = mst_api.get_product_data(request, product_id)
            logger.info("get_product - api" + str(comm))
            print("get_product - api", comm)
            return comm

    def fetch_productdata(self, request, product_id):
        if self.MICRO_SERVICE:
            comm_ser = ProductService(self._scope())
            comm = comm_ser.fetch_productdata(product_id)
            logger.info("fetch_productdata - serv" + str(comm))
            print("fetch_productdata - serv", comm)
            return comm
        else:
            mst_api = MasterAPI()
            comm = mst_api.fetch_productdata(request, product_id)
            logger.info("fetch_productdata - api" + str(comm))
            print("fetch_productdata - api", comm)
            return comm
    def fetch_commoditydata(self, request, commodity_id):
        if self.MICRO_SERVICE:
            pos_ser = CommodityService()
            pos = pos_ser.fetch_commoditys(commodity_id)
            logger.info("fetch_commoditydata - serv" + str(pos))
            print("fetch_commoditydata - serv", pos)
            return pos
        else:
            master_apicall = MasterAPI()
            master_commodity = master_apicall.fetch_commoditydata(request,commodity_id)
            logger.info("fetch_commoditydata - api" + str(master_commodity))
            print("fetch_commoditydata - api", master_commodity)
            return master_commodity

    def get_creditpayment(self,branch,emp_id):
        from vendorservice.service.paymentservice import paymentservice
        if self.MICRO_SERVICE:
            emp_ser = paymentservice(self._scope())
            emp = emp_ser.fetch_creditpayment(branch,emp_id)
            return emp
        else:
            pass
    def get_state(self, request, state_id):
        if self.MICRO_SERVICE:
            state_ser = StateService(self._scope())
            state = state_ser.fetchstate(state_id)
            return state
        else:
            master_service = MasterAPI()
            state = master_service.get_state_id_new(request, state_id)
            print('statesingle', state)
            return state

    def get_single_bank_branch(self,bankbranch_id,emp_id):
        if self.MICRO_SERVICE:
            emp_ser = BankBranchService(self._scope())
            bank_branch = emp_ser.fetch_bankbranch(bankbranch_id,emp_id)
            return bank_branch
        else:
            pass



    def ppxdetails_ecfcrno_update(self,ecfheader_id,crno,emp_id):
        if self.MICRO_SERVICE:
            ap_ppx_dtls_serv = APppxDetailsService(self._scope())
            ap_ppx_dtls = ap_ppx_dtls_serv.ppxdetails_crno_update(ecfheader_id,crno,emp_id)
            return ap_ppx_dtls
        else:
            pass



    def get_department_id(self, request, dept_id):
        if self.MICRO_SERVICE:
            department_ser = DepartmentService(self._scope())
            department = department_ser.fetch_internal_department(dept_id)
            return department
        else:
            emp_api = EmployeeAPI()
            emp = emp_api.fetch_department_id(request, dept_id)
            print('empsingle', emp)
            return emp

    def get_designation_id(self, request, designation_id):
        if self.MICRO_SERVICE:
            designation_serv = DesignationService(self._scope())
            designation = designation_serv.fetch_designation(designation_id)
            return designation
        else:
            designation_serv = MasterAPI()
            designation = designation_serv.fetch_designation_id(request, designation_id)
            print('designation', designation)
            return designation


    def get_designation_name(self,name,Entity):
        if self.MICRO_SERVICE:
            designation_serv = DesignationService(self._scope())
            designation = designation_serv.fetch_by_designation_code(name,Entity)
            return designation
        else:
            pass

    def get_department_name(self,name,Entity):
        if self.MICRO_SERVICE:
            department_ser = DepartmentService(self._scope())
            dept =department_ser.fetch_department_name(name,Entity)
            return dept
        else:
            pass

    def get_emp_branch_name(self, code,name,gstin,Entity):
        if self.MICRO_SERVICE:
            emp_ser = employeeservice.EmployeeService(self._scope())
            data=emp_ser.fetch_emp_branch_name(code,name,gstin,Entity)
            return data
        else:
            pass


    def get_entryapi(self,request,emp_id,entry_id):
        if self.MICRO_SERVICE:
            entry = EntryService(self._scope())
            emp = entry.create_entrydetails(request,emp_id,entry_id)
            return emp
        else:
            pass

    def get_entryoracleapi(self,entry_id,emp_id):
        if self.MICRO_SERVICE:
            entry = EntryOracleService(self._scope())
            emp = entry.journal_entry_api(entry_id,emp_id)
            return emp
        else:
            pass

    def get_empbrnchdata(self,branchcode):
        if self.MICRO_SERVICE:
            emp_ser = employeeservice.EmployeeService(self._scope())
            emp = emp_ser.fetch_empbranchcode(branchcode)
            return emp
        else:
            pass

    def create_country_sync(self,country_name,Entity):
        if self.MICRO_SERVICE:
            ctry_ser = CountryService(self._scope())
            data=ctry_ser.country_sync_create(country_name,Entity)
            return data
        else:
            pass

    def create_state_sync(self,state_name,country_id,Entity):
        if self.MICRO_SERVICE:
            state_ser = StateService(self._scope())
            data=state_ser.create_sync_state(state_name,country_id,Entity)
            return data
        else:
            pass

    def create_district_sync(self,district_name,state_id,Entity):
        if self.MICRO_SERVICE:
            dt_ser = DistrictService(self._scope())
            data=dt_ser.create_sync_district(district_name,state_id,Entity)
            return data
        else:
            pass

    def create_city_sync(self,city_name,state_id,Entity):
        if self.MICRO_SERVICE:
            city_ser = CityService(self._scope())
            data=city_ser.create_sync_city(city_name,state_id,Entity)
            return data
        else:
            pass

    def create_pincode_sync(self,pincde_no,city_id,district_id,Entity):
        if self.MICRO_SERVICE:
            pcde_ser = PincodeService(self._scope())
            data=pcde_ser.create_sync_pincode(pincde_no,city_id,district_id,Entity)
            return data
        else:
            pass

    def fetch_rm_code(self,rm_code):
        if self.MICRO_SERVICE:
            emp_ser = employeeservice.EmployeeService(self._scope())
            data = emp_ser.fetch_emp_rm_id(rm_code)
            return data
        else:
            pass

    def fetch_bank_sync(self,bank_name):
        if self.MICRO_SERVICE:
            bank_ser = BankService(self._scope())
            data = bank_ser.get_bank_sync_id(bank_name)
            return data
        else:
            pass

    def fetch_bank_branch_sync(self,branch_name,ifsccode):
        if self.MICRO_SERVICE:
            bank_ser = BankBranchService(self._scope())
            data = bank_ser.get_bank_branch_sync(branch_name,ifsccode)
            return data
        else:
            pass
    def fetch_pincode(self,pincode_id, user_id,request):
        if self.MICRO_SERVICE:
            pincode_ser = PincodeService(self._scope())
            data = pincode_ser.fetch_pincode(pincode_id, user_id)
            return data
        else:
            master_service = MasterAPI()
            state = master_service.fetch_pincode_id(request, pincode_id)
            print('state', state)
            return state
    def fetch_city(self,city_id, user_id,request):
        if self.MICRO_SERVICE:
            city_ser = CityService(self._scope())
            data = city_ser.fetch_city(city_id, user_id)
            return data
        else:
            master_service = MasterAPI()
            state = master_service.fetch_city(request, city_id)
            print('state', state)
            return state

    def fetch_district(self,district_id,request):
        if self.MICRO_SERVICE:
            district_ser = DistrictService(self._scope())
            data = district_ser.fetchdistrict(district_id)
            return data
        else:
            master_service = MasterAPI()
            district = master_service.fetch_district(request, district_id)
            print('district', district)
            return district
    def fetch_state(self,state_id,request):
        if self.MICRO_SERVICE:
            state_ser = StateService(self._scope())
            data = state_ser.fetchstate(state_id)
            return data
        else:
            master_service = MasterAPI()
            state = master_service.fetch_state(request, state_id)
            print('state', state)
            return state
    def fetch_designation(self,designation_id,request):
        if self.MICRO_SERVICE:
            designation_ser = DesignationService(self._scope())
            data = designation_ser.fetch_designation(designation_id)
            return data
        else:
            master_service = MasterAPI()
            designation = master_service.fetch_designation_id(request, designation_id)
            print('designation', designation)
            return designation

    def upload_single_file(self,file, doc_param, request):
        if self.MICRO_SERVICE:
            doc_ser = DocumentsService(self._scope())
            data = doc_ser.upload_single_doc(file, doc_param)
            return data
        else:
            master_service = MasterAPI()
            file = master_service.upload_single_file(request,file,doc_param)
            # print('file', file)
            return file
    def fetch_rm_name(self,request, query,vys_page):
        if self.MICRO_SERVICE:
            emp_ser = employeeservice.EmployeeService(self._scope())
            data = emp_ser.search_employee_list(request, query,vys_page)
            return data
        else:
            master_service = MasterAPI()
            employee = master_service.fetch_rm_name(request, query)
            print('employee', employee)
            return employee

    def download_file(self, request, file_id, emp_id):
        if self.MICRO_SERVICE:
            doc_ser = DocumentsService(self._scope())
            file_id = file_id
            doc = doc_ser.file_download(file_id, emp_id)
            print("download_m2m serv ", doc)
            return doc
        else:
            doc_apicall = MasterAPI()
            download_m2m = doc_apicall.download_m2m(request, file_id)
            print("download_m2m  api", download_m2m)
            doc_download = doc_apicall.doc_download(download_m2m)
            print("doc_download", doc_download)
            return doc_download
    def fetch_branch_list(self, branch_id):
        if self.MICRO_SERVICE:
            emp_branch_ser = employeeservice.EmployeeBranchService(self._scope())
            data = emp_branch_ser.fetch_branch(branch_id)
            return data
        else:
            pass

    def fetch_emp_id(self,  emp_id):
        if self.MICRO_SERVICE:
            emp_ser = employeeservice.EmployeeService(self._scope())
            data = emp_ser.search_employee(emp_id,user_id=None)
            return data
        else:
            pass
            # master_service = MasterAPI()
            # employee = master_service.fetch_rm_name(request)
            # print('employee', employee)
            # return employee

    def doc_upload_atma(self, request,params):
        if self.MICRO_SERVICE:
            p_ser = DocumentsService(self._scope())
            p = p_ser.upload(request,params)
            logger.info("doc_upload_key - serv" + str(p))
            print("doc_upload_key - serv", p)
            p = json.loads(p.get())
            return p
        else:
           pass

    def get_questions(self,data):
        if self.MICRO_SERVICE:
            vendor_master = QuestionService(self._scope())
            resp = vendor_master.get_question(data)
            return resp
        else:
            pass

    def get_subquestions(self,data):
        if self.MICRO_SERVICE:
            vendor_master = QuestionService(self._scope())
            resp = vendor_master.get_sub_question_arr1(data)
            return resp
        else:
            pass

    def get_quesheader(self,data):
        if self.MICRO_SERVICE:
            vendor_master = QuestionheaderService(self._scope())
            resp = vendor_master.question_header_single_get_info(data)
            return resp
        else:
            pass

    def get_question_type(self,data):
        if self.MICRO_SERVICE:
            vendor_master = QuestiontypeService(self._scope())
            resp = vendor_master.question_single_get(data)
            return resp
        else:
            pass

