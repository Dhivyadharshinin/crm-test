
from ecfservice.util.ecfutil import get_Type, get_tds
from inwardservice.service.inwardservice import InwardService
from masterservice.service import ccbsservice
from masterservice.service.bankbranchservice import BankBranchService
from masterservice.service.bankdetailsservice import BankDetailsService
from masterservice.service.bsproductservice import BsproductService
from masterservice.service.clientcodeservice import ClientcodeService
from masterservice.service.pincodeservice import PincodeService
from masterservice.service.productservice import ProductService
from masterservice.service.taxservice import TaxMasterService
from masterservice.service.uomservice import UomService
from nwisefin.settings import logger
from userservice.service import employeeservice
from masterservice.service.commodityservice import CommodityService
from masterservice.service.stateservice import StateService
from masterservice.service.bankservice import BankService
from masterservice.service.paymodeservice import PaymodeService

from userservice.service.branchservice import EmployeeBranchService


from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from vendorservice.service.branchservice import branchservice
from vendorservice.service.paymentservice import paymentservice

from masterservice.service.apcategoryservice import CategoryService
from masterservice.service.apsubcategoryservice import SubcategoryService
from masterservice.service.Hsnservice import Hsnservice
from vendorservice.service.vendorservice import VendorService
from wisefinapi.vendorapi import VendorAPI
from wisefinapi.employeeapi import EmployeeAPI
from wisefinapi.masterapi import MasterAPI
import json
from vendorservice.service.vendoraddressservice import VendorAddressService

from masterservice.service.subtaxservice import SubTaxService
from masterservice.service.taxrateservice import TaxRateService
from taservice.util.ta_util import DictObj
from userservice.service.employeeservice import TA_employee_service, EmployeeService


class APApiService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ECF_SERVICE)

    MICRO_SERVICE = True

    def common_json_converter(self,str_data):
        return  json.loads(str_data.get())

    def get_ap_bankdetails_master(self,bankdetails_id,emp_id):
        if self.MICRO_SERVICE:
            bankdtls=BankDetailsService(self._scope())
            bankdetails_data=bankdtls.fetch_bankdetails(bankdetails_id,emp_id)
            return_resp=self.common_json_converter(bankdetails_data)
            return return_resp
        else:
            pass

    def get_ap_clientcode(self,client_id):
        if self.MICRO_SERVICE:
            emp_ser = ClientcodeService(self._scope())
            emp = emp_ser.fetch_clientcode(client_id)
            return_resp = self.common_json_converter(emp)
            return return_resp
        else:
            pass

    def get_supplier_payment_details(self,request,employee_id,supplierbranch_id):
        if self.MICRO_SERVICE:
            payment_service = paymentservice(self._scope())
            page = 1
            page = int(page)
            vys_page = NWisefinPage(page, 10)
            resp_obj = payment_service.fetch_payment_list(request, vys_page,employee_id,supplierbranch_id)
            return_resp = self.common_json_converter(resp_obj)
            return return_resp
        else:
            pass


    def get_supplier_details(self,supplierbranch_id):
        if self.MICRO_SERVICE:
            branch_service = branchservice(self._scope())
            resp_obj = branch_service.fetch_branch(supplierbranch_id)
            return_resp = self.common_json_converter(resp_obj)
            return return_resp
        else:
            pass


    def get_vendor_address(self,vendor_id,emp_id):
        if self.MICRO_SERVICE:
            vendor_service = VendorAddressService(self._scope())
            resp_obj = vendor_service.fetch_vendoraddress(vendor_id,emp_id)
            return_resp = self.common_json_converter(resp_obj)
            return return_resp
        else:
            pass


    def get_supplierbranch_details(self,supplier_id,emp_id):
        if self.MICRO_SERVICE:
            branch_service = branchservice(self._scope())
            resp_obj = branch_service.fetch_branch(supplier_id)
            return_resp = self.common_json_converter(resp_obj)
            return return_resp
        else:
            pass


    def get_supplier_address(self,supplier_id,emp_id):
        if self.MICRO_SERVICE:
            from vendorservice.service.supplierservice import ContactService, AddressService
            supplieraddrs_service = AddressService(self._scope())
            supplierbranch_details = self.get_supplierbranch_details(supplier_id,emp_id)
            resp_obj = supplieraddrs_service.fetch_address (supplierbranch_details['address_id'] , emp_id )
            return_resp = self.common_json_converter(resp_obj)
            return return_resp
        else:
            pass


    def get_supplier_contact(self,supplier_id,emp_id):
        if self.MICRO_SERVICE:
            from vendorservice.service.supplierservice import ContactService, AddressService
            suppliercontct_service = ContactService(self._scope())
            supplierbranch_details = self.get_supplierbranch_details(supplier_id,emp_id)
            resp_obj = suppliercontct_service.fetch_contact (supplierbranch_details['contact_id'],emp_id )
            return_resp = self.common_json_converter(resp_obj)
            return return_resp
        else:
            pass


    def get_supplier_pincode(self,supplier_id,emp_id):
        if self.MICRO_SERVICE:
            from vendorservice.service.supplierservice import ContactService, AddressService
            supplieraddrs_service = AddressService(self._scope())
            supplierbranch_details = self.get_supplierbranch_details(supplier_id,emp_id)
            resp_obj = supplieraddrs_service.fetch_address(supplierbranch_details['address_id'] , emp_id )
            supplieraddrs_json = self.common_json_converter(resp_obj)
            pincode_id=supplieraddrs_json['pincode_id']
            pincode_service = PincodeService(self._scope())
            pincoderesp_obj = pincode_service.fetch_pincode(pincode_id, emp_id)
            pincode_json = self.common_json_converter(pincoderesp_obj)
            pincode_no=''
            if pincode_json['no']:
                pincode_no=pincode_json['no']
            #print('pincode_json',pincode_json)
            return pincode_no
        else:
            pass

    def get_emp_pincode(self,pincode_id,emp_id):
        if self.MICRO_SERVICE:
            pincode_service = PincodeService(self._scope())
            pincoderesp_obj = pincode_service.fetch_pincode(pincode_id, emp_id)
            pincode_json = self.common_json_converter(pincoderesp_obj)
            pincode_no=''
            if pincode_json['no']:
                pincode_no=pincode_json['no']
            return pincode_no
        else:
            pass



    def paymode_single_get(self,paymode_id):
        if self.MICRO_SERVICE:
            paymode_service = PaymodeService(self._scope())
            paymode_details = paymode_service.fetchpaymode(paymode_id)
            paymode_json = self.common_json_converter(paymode_details)
            return paymode_json
        else:
            pass



    def get_ap_ecftypesingle(self,ecftype_id):
        print('ecftype_id ',ecftype_id)
        if self.MICRO_SERVICE:
            resp_obj = get_Type(int(ecftype_id))
            return_json = self.common_json_converter(resp_obj)
            return return_json
        else:
            pass



    def paymode_single_get_with_name(self,query):
        if self.MICRO_SERVICE:
            paymode_service = PaymodeService(self._scope())
            vys_page = NWisefinPage(1, 10)
            paymode_details = paymode_service.fetch_paymode_search(query,vys_page)
            paymode_json = self.common_json_converter(paymode_details)
            return paymode_json
        else:
            pass


    def get_apcredit_supplierpayment(self,branch_id,paymode_id,account_no,emp_id):
        from vendorservice.service.paymentservice import paymentservice
        if self.MICRO_SERVICE:
            emp_ser = paymentservice(self._scope())
            supplierpaymentacc = emp_ser.supplierpaymentacc(branch_id,paymode_id,account_no,emp_id)
            return_json = self.common_json_converter(supplierpaymentacc)
            return return_json
        else:
            pass

    def get_apcredit_singlebank_data(self,bank_id,emp_id):
        if self.MICRO_SERVICE:
            bank_service = BankService(self._scope())
            resp_obj = bank_service.fetch_bank(bank_id, emp_id)
            return_json = self.common_json_converter(resp_obj)
            return return_json
        else:
            pass

    def get_single_emp_id(self,emp_id):
        if self.MICRO_SERVICE:
            emp_ser = employeeservice.EmployeeService(self._scope())
            emp = emp_ser.fetch_employee_by_empid(emp_id)
            return emp
        else:
            pass

    def fetch_product_using_productcode(self,product_code):
        if self.MICRO_SERVICE:
            product_service = ProductService(self._scope())
            resp_obj = product_service.search_productcode(product_code)
            return_json = self.common_json_converter(resp_obj)
            return return_json
        else:
            pass


    def fetch_bank_single(self, bank_id, emp_id):
        if self.MICRO_SERVICE:
            bank_service = BankService(self._scope())
            resp_obj = bank_service.fetch_bank(bank_id, emp_id)
            return_json = self.common_json_converter(resp_obj)
            return return_json
        else:
            pass

    def fetch_single_supplier_data(self,supplier_id):
        if self.MICRO_SERVICE:
            #vendor_service = VendorService(self._scope())
            branch_service = branchservice(self._scope())
            resp_obj = branch_service.fetch_branch(supplier_id)
            return_json = self.common_json_converter(resp_obj)
            return return_json
        else:
            pass

    def fetch_single_supplier_data_with_vendor(self,supplier_id):
        if self.MICRO_SERVICE:
            #vendor_service = VendorService(self._scope())
            branch_service = branchservice(self._scope())
            resp_obj = branch_service.fetch_single_supplierbranch(supplier_id)
            return_json = self.common_json_converter(resp_obj)
            return return_json
        else:
            pass

    def ap_employee_branch_single_get(self,employeebranch_id):
        if self.MICRO_SERVICE:
            branch_service = EmployeeBranchService(self._scope())
            resp_obj = branch_service.fetch_branch(employeebranch_id)
            return_json = self.common_json_converter(resp_obj)
            return return_json
        else:
            pass

    def ap_commodity_single_get(self,commodity_id, emp_id):
        if self.MICRO_SERVICE:
            commodity_serv = CommodityService(self._scope())
            resp_obj =  commodity_serv.fetch_Commodity(commodity_id, emp_id)
            return_json = self.common_json_converter(resp_obj)
            return return_json
        else:
            pass

    def ap_ef_tds_single_get(self,aptds_id):
        if self.MICRO_SERVICE:
            resp_obj =  get_tds(aptds_id)
            return_json = self.common_json_converter(resp_obj)
            return return_json
        else:
            pass

    def fetch_apraiser_emp_accntdtls_using_accntno(self, request, emp_accountno, emp_id):
        if self.MICRO_SERVICE:
            from userservice.service.employeeaccountdetailsservice import EmployeeAccountDetailsService
            empaccnt_serv = EmployeeAccountDetailsService(self._scope())
            resp_obj =  empaccnt_serv.fetch_emp_accntdtls_using_accntno(request,emp_accountno,emp_id)
            return_json = self.common_json_converter(resp_obj)
            return return_json
        else:
            pass

    def fetch_apraiser_emp_accntdtls_using_emp_id(self, request, emp_id):
        if self.MICRO_SERVICE:
            from userservice.service.employeeaccountdetailsservice import EmployeeAccountDetailsService
            empaccnt_serv = EmployeeAccountDetailsService(self._scope())
            resp_obj =  empaccnt_serv.fetch_emp_accntdtls_using_emp_id(request,emp_id)
            return_json = self.common_json_converter(resp_obj)
            return return_json
        else:
            pass

    def fetch_ecfraiser_emp_address(self,address_id):
        if self.MICRO_SERVICE:
            from userservice.service.addresscontactservice import AddressService
            empaddr_serv = AddressService(self._scope())
            resp_obj = empaddr_serv.fetch_employeeaddress(address_id)
            return_json = self.common_json_converter(resp_obj)
            return return_json
        else:
            pass

    def get_emp_address_contact_id(self,ecfraiser_empid):
        if self.MICRO_SERVICE:
            emp_serv = EmployeeService(self._scope())
            resp_obj = emp_serv.get_contact_address_id(ecfraiser_empid)
            return_json = self.common_json_converter(resp_obj)
            return return_json
        else:
            pass

    def get_employee_single(self,emp_id):
        if self.MICRO_SERVICE:
            emp_serv = EmployeeService(self._scope())
            resp_obj = emp_serv.get_employee(emp_id, None)
            return_json = self.common_json_converter(resp_obj)
            return return_json
        else:
            pass

    def get_apsubcategory_code(self,category_code,subcat_code):
        if self.MICRO_SERVICE:
            subcat_serv = SubcategoryService(self._scope())
            apsubcategory=subcat_serv.get_apsubcategory_code(category_code,subcat_code)
            #return_json = self.common_json_converter(apsubcategory)
            return apsubcategory
        else:
            pass

    def fetch_inward_no_using_inwaddtls_id(self,request,inwarddtdl_id):
        if self.MICRO_SERVICE:
            inwd_serv = InwardService(self._scope())
            inwd_hdr=inwd_serv.get_inward_no_using_inwaddtls_id(request,inwarddtdl_id)
            return_json = self.common_json_converter(inwd_hdr)
            return return_json
        else:
            pass

    def fetch_first_prodct(self):
        if self.MICRO_SERVICE:
            prdct_serv = ProductService(self._scope())
            inwd_hdr=prdct_serv.fetch_first_product()
            return_json = self.common_json_converter(inwd_hdr)
            return return_json
        else:
            pass

    def fetch_suppliertax_list_using_subtax_id(self,vendor_id,subtax_id):
        if self.MICRO_SERVICE:
            from vendorservice.service.suppliertaxservice import TaxService
            suppliertax_serv = TaxService(self._scope())
            return_list=suppliertax_serv.get_suppliertax_list_using_vendor_id(vendor_id,subtax_id)
            return_json = self.common_json_converter(return_list)
            return return_json
        else:
            pass

    def get_glno_description(self, glno):
        if self.MICRO_SERVICE:
            from userservice.service.generalledgerservice import General_LedgerService
            pose_ser = General_LedgerService(self._scope())
            return_json = pose_ser.fetch_gl_no_api(None,glno)
            return return_json
        else:
            pass


    def doc_upload_ap(self, request,params,filekey):
        if self.MICRO_SERVICE:
            from docservice.service.documentservice import DocumentsService
            doc_serv = DocumentsService(self._scope())
            return_list = doc_serv.document_upload_ap(request,params, filekey)
            return_json = self.common_json_converter(return_list)
            logger.info("doc_upload_key - serv " + str(return_json))
            print("doc_upload_key - serv ", return_json)
            return return_json
        else:
           pass


    def apfile_view(self, file_id, emp_id):
        if self.MICRO_SERVICE:
            from docservice.service.documentservice import DocumentsService
            doc_serv = DocumentsService(self._scope())
            return_data = doc_serv.file_download(file_id, emp_id)
            logger.info("return_data " + str(return_data))
            print("return_data ", return_data)
            return return_data
        else:
           pass


    def apfile_download(self, file_id, emp_id):
        if self.MICRO_SERVICE:
            from docservice.service.documentservice import DocumentsService
            doc_serv = DocumentsService(self._scope())
            return_data = doc_serv.doc_download(file_id, emp_id)
            logger.info("return_data " + str(return_data))
            print("return_data ", return_data)
            return return_data
        else:
           pass


    def apfile_delete(self, file_id, emp_id):
        if self.MICRO_SERVICE:
            from docservice.service.documentservice import DocumentsService
            doc_serv = DocumentsService(self._scope())
            return_data = doc_serv.delete_document(file_id, emp_id)
            logger.info("return_data " + str(return_data))
            print("return_data ", return_data)
            return return_data
        else:
           pass


    def fetch_employees_using_modulerole(self, module,module_role,emp_id):
        if self.MICRO_SERVICE:
            from userservice.service.roleemployeeservice import RoleEmployeeService
            emprole_serv = RoleEmployeeService(self._scope())
            return_data = emprole_serv.fetch_employees_by_role(module,module_role,emp_id)
            logger.info("return_data " + str(return_data))
            print("return_data ", return_data)
            return return_data
        else:
           pass
