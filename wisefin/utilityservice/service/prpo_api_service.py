from masterservice.service.bankservice import BankService
# from masterservice.service.paymentservice import paymentservice
from masterservice.service.paymodeservice import PaymodeService
from masterservice.service.subtaxservice import SubTaxService
from masterservice.service.taxrateservice import TaxRateService
from masterservice.service.taxservice import TaxMasterService
from masterservice.service.Hsnservice import Hsnservice
from masterservice.service.cityservice import CityService
from masterservice.service.pincodeservice import PincodeService
from masterservice.service.productcategoryservice import Productcategoryservice
from masterservice.service.productservice import ProductService
from masterservice.service.producttypeservice import ProducttypeService
from masterservice.service.stateservice import StateService
from masterservice.service.uomservice import UomService
from masterservice.service.commodityservice import CommodityService
from docservice.service.documentservice import DocumentsService
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from vendorservice.service.suppliertaxservice import TaxService
from vendorservice.service.branchservice import branchservice
from vendorservice.service.vendoraddressservice import VendorAddressService
from userservice.service import employeeservice
# from userservice.service.ccbsservice import CostCentreService, BusinessSegmentService
from userservice.service.employeeservice import EmployeeService
from userservice.controller.authcontroller import get_authtoken

from nwisefin.settings import logger
# from vysfinutility.data.vysfinpage import VysfinPage
from wisefinapi.docservapi import DocAPI
from wisefinapi.vendorapi import VendorAPI
from wisefinapi.employeeapi import EmployeeAPI
from wisefinapi.masterapi import MasterAPI

import json

class ApiService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ECF_SERVICE)

    MICRO_SERVICE = False

#user
    def get_emp_id(self, request, emp_id):
        if self.MICRO_SERVICE:
            emp_ser = employeeservice.EmployeeService()
            emp = emp_ser.get_employee_from_userid(emp_id)
            emp=emp.__dict__
            emp['name']=emp['full_name']
            print('data',emp)
            return emp
        else:
            emp_api=EmployeeAPI()
            emp = emp_api.get_emp_by_userid(request, emp_id)
            # print('data2',emp)
            return emp

    def get_emp_by_userid_queryparams(self, request, emp_id):
        if self.MICRO_SERVICE:
            emp_ser = employeeservice.EmployeeService()
            emp = emp_ser.get_employee_from_userid(emp_id)
            logger.info("get_emp_by_userid_queryparams - serv" + str(emp))
            print("get_emp_by_userid_queryparams - serv", emp)
            emp = emp.__dict__
            emp['name']=emp['full_name']
            print('get_emp_by_userid_queryparams data',emp)
            return emp
        else:
            emp_api=EmployeeAPI()
            emp = emp_api.get_emp_by_userid_queryparams(request, emp_id)
            logger.info("get_emp_by_userid_queryparams - api" + str(emp))
            print('get_emp_by_userid_queryparams - api', emp)
            return emp

    def get_authtoken(self, request):
        if self.MICRO_SERVICE:
            emp = get_authtoken()
            logger.info("get_authtoken - serv" + str(emp))
            print('get_authtoken - serv', emp)
            return emp
        else:
            emp_api=EmployeeAPI()
            emp = emp_api.get_authtoken(request)
            logger.info("get_authtoken - api" + str(emp))
            print('get_authtoken - api', emp)
            emp = emp["access_token"]
            print('get_authtoken api',emp)
            return emp

    def fetch_employeedata(self, request, employee_id):
        if self.MICRO_SERVICE:
            po_ser = EmployeeService()
            po = po_ser.fetch_employeedata(employee_id)
            logger.info("fetch_employeedata - serv" + str(po))
            print("fetch_employeedata serv", po)
            return po
        else:
            emp_api = EmployeeAPI()
            po = emp_api.fetch_employeedata(request, employee_id)
            logger.info("fetch_employeedata - api" + str(po))
            print("fetch_employeedata - api", po)
            return po

    def fetch_employeebranchdata(self, request, branch_id):
        if self.MICRO_SERVICE:
            pose_ser = EmployeeService()
            pose = pose_ser.fetch_empbranch(branch_id)
            logger.info("fetch_employeebranchdata - serv" + str(pose))
            print("fetch_employeebranchdata - serv", pose)
            return pose
        else:
            emp_api = EmployeeAPI()
            user_employeebranch = emp_api.fetch_employeebranchdata(request, branch_id)
            logger.info("fetch_employeebranchdata - api" + str(user_employeebranch))
            print("fetch_employeebranchdata - api", user_employeebranch)
            return user_employeebranch

    def get_commodity_apexpense(self, request, commodity_id):
        if self.MICRO_SERVICE:
            pos_ser = CommodityService()
            pos = pos_ser.commodity_get(commodity_id)
            logger.info("get_commodity - serv" + str(pos))
            print("get_commodity - serv", pos)
            pos = json.loads(pos)
            return pos
        else:
            master_apicall = MasterAPI()
            master_commodity = master_apicall.get_commodity_data_apexpense(request, commodity_id)
            logger.info("get_commodity - api" + str(master_commodity))
            print("get_commodity - api", master_commodity)
            return master_commodity
    def fetch_ebranchaddressdata(self, request, branch_id):
        if self.MICRO_SERVICE:
            emp_ser = employeeservice.EmployeeService()
            emp = emp_ser.fetch_ebranchaddressdata(branch_id)
            logger.info("fetch_ebranchaddressdata - serv" + str(emp))
            print("fetch_ebranchaddressdata - serv", emp)
            return emp
        else:
            emp_api = EmployeeAPI()
            emp = emp_api.fetch_ebranchaddressdata(request, branch_id)
            logger.info("fetch_ebranchaddressdata - api" + str(emp))
            print("fetch_ebranchaddressdata - api", emp)
            return emp

    def get_employeedata(self, request):
        if self.MICRO_SERVICE:
            po_ser = EmployeeService(self._scope())
            po = po_ser.get_employeedata()
            logger.info("get_employeedata - serv" + str(po))
            print("get_employeedata - serv", po)
            po = json.loads(po)
            return po
        else:
            emp_api = EmployeeAPI()
            po = emp_api.employee_list(request)
            logger.info("get_employeedata - api" + str(po))
            print("get_employeedata - api", po)
            po = json.loads(po.content)  #add
            return po

    def get_employee(self, request, employee_id):
        if self.MICRO_SERVICE:
            employee_ids = {"employee_id": employee_id}
            po_ser = EmployeeService(self._scope())
            po = po_ser.employee_get(employee_ids)
            logger.info("get_employee - serv" + str(po))
            print("get_employee - serv", po)
            po = json.loads(po)
            return po
        else:
            emp_api = EmployeeAPI()
            po = emp_api.get_employee_data(request, employee_id)
            logger.info("get_employee - api" + str(po))
            print("get_employee - api", po)
            return po

    def get_employee_details(self, request, employee_id):
        if self.MICRO_SERVICE:
            employee_ids = {"employee_id": employee_id}
            po_ser = EmployeeService(self._scope())
            po = po_ser.employee_get(employee_ids)
            logger.info("get_employee - serv" + str(po))
            print("get_employee - serv", po)
            po = json.loads(po)
            return po
        else:
            emp_api = EmployeeAPI()
            po = emp_api.get_employee_data_apexpense(request, employee_id)
            logger.info("get_employee - api" + str(po))
            print("get_employee - api", po)
            return po

    def get_employeebranch(self, request, branch_id):
        if self.MICRO_SERVICE:
            branch_ids = {"employeebranch_id": branch_id}
            pose_ser = EmployeeService()
            pose = pose_ser.employeebranch_get(branch_ids)
            logger.info("get_employeebranch - serv" + str(pose))
            print("get_employeebranch - serv", pose)
            pose = json.loads(pose)
            return pose
        else:
            emp_api = EmployeeAPI()
            user_employeebranch = emp_api.get_empolyeebranch_data(request, branch_id)
            logger.info("get_employeebranch - api" + str(user_employeebranch))
            print("user_employeebranch - api", user_employeebranch)
            return user_employeebranch

    def get_employeename(self, request, name):
        if self.MICRO_SERVICE:
            po_ser = EmployeeService(self._scope())
            po = po_ser.get_employeename(name)
            logger.info("get_employeename - serv" + str(po))
            print("get_employeename - serv", po)
            po = json.loads(po)
            return po
        else:
            emp_api = EmployeeAPI()
            po = emp_api.get_employeename(request, name)
            logger.info("get_employeename - api" + str(po))
            print("get_employeename - api", po)
            po = json.loads(po.content)  # add
            return po

    def get_employeebranchname(self, request, name):
        if self.MICRO_SERVICE:
            po_ser = EmployeeService()
            po = po_ser.get_employeebranchname(name)
            print("get_employeebranchname - serv", po)
            logger.info("get_employeebranchname - serv" + str(po))
            return po
        else:
            emp_api = EmployeeAPI()
            po = emp_api.get_employeebranchname(request, name)
            logger.info("get_employeebranchname - api" + str(po))
            print("get_employeebranchname - api", po)
            return po

    def get_ccname(self, request, name):
        if self.MICRO_SERVICE:
            po_ser = CostCentreService()
            po = po_ser.get_ccname(name)
            logger.info("get_ccname - serv" + str(po))
            print("get_ccname -serv", po)
            return po
        else:
            emp_api = EmployeeAPI()
            po = emp_api.get_ccname(request, name)
            logger.info("get_ccname - api" + str(po))
            print("get_ccname - api", po)
            return po

    def get_bsname(self, request, name):
        if self.MICRO_SERVICE:
            po_ser = BusinessSegmentService()
            po = po_ser.get_bsname(name)
            logger.info("get_bsname - serv" + str(po))
            print("get_bsname - serv", po)
            return po
        else:
            emp_api = EmployeeAPI()
            po = emp_api.get_bsname(request, name)
            logger.info("get_bsname - api" + str(po))
            print("get_bsname - api", po)
            return po

    def get_employeecode(self, request, query):
        if self.MICRO_SERVICE:
            po_ser = EmployeeService()
            po = po_ser.get_employeecode(query)
            logger.info("get_employeecode - serv" + str(po))
            print("get_employeecode - serv", po)
            return po
        else:
            emp_api = EmployeeAPI()
            po = emp_api.get_employeecode(request, query)
            logger.info("get_employeecode - api" + str(po))
            print("get_employeecode - api", po)
            return po

    def get_employeename_data(self, request, employee_id, query):
        if self.MICRO_SERVICE:
            employee_ids = {"employee_id": employee_id}
            po_ser = EmployeeService()
            po = po_ser.get_employeename_data(employee_ids, query)
            logger.info("get_employeename_data - serv" + str(po))
            print("get_employeename_data - serv", po)
            po = json.loads(po)
            return po
        else:
            emp_api = EmployeeAPI()
            po = emp_api.get_employeename_data(request, employee_id, query)
            logger.info("get_employeename_data - api" + str(po))
            print("get_employeename_data - api", po)
            return po

#master
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

    def fetch_productdata(self, request, product_id):
        if self.MICRO_SERVICE:
            comm_ser = ProductService()
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

    def fetch_uomdata(self, request, uomid):
        if self.MICRO_SERVICE:
            comm_ser = UomService()
            comm = comm_ser.fetch_uomdata(uomid)
            logger.info("fetch_uomdata - serv" + str(comm))
            print("fetch_uomdata - serv", comm)
            return comm
        else:
            mst_api = MasterAPI()
            comm = mst_api.fetch_uomdata(request, uomid)
            logger.info("fetch_uomdata - api" + str(comm))
            print("fetch_uomdata - api", comm)
            return comm

    def fetch_productapcatdata(self, request, product_id):
        if self.MICRO_SERVICE:
            comm_ser = ProductService()
            comm = comm_ser.fetch_apcategorydata(product_id)
            logger.info("fetch_productapcatdata - serv" + str(comm))
            print("fetch_productapcatdata - serv", comm)
            return comm
        else:
            mst_api = MasterAPI()
            comm = mst_api.fetch_apcategorydata(request, product_id)
            logger.info("fetch_productapcatdata - api", str(comm))
            print("fetch_productapcatdata - api", comm)
            return comm

    def fetch_producttypedata(self, request, productcat_id):
        if self.MICRO_SERVICE:
            pr_ser = ProducttypeService()
            productcat = pr_ser.fetch_producttypedata(productcat_id)
            logger.info("fetch_producttypedata - serv" + str(productcat))
            print("fetch_producttypedata - serv", productcat)
            return productcat
        else:
            master_apicall = MasterAPI()
            productcat = master_apicall.fetch_pdttype(request, productcat_id)
            logger.info("fetch_producttypedata - api" + str(productcat))
            print("fetch_producttypedata - api", productcat)
            return productcat

    def fetch_productcatdata(self, request, productcat_id):
        if self.MICRO_SERVICE:
            pr_ser = Productcategoryservice()
            productcat = pr_ser.fetch_productcatdata(productcat_id)
            logger.info("fetch_productcatdata - serv" + str(productcat))
            print("fetch_productcatdata - serv", productcat)
            return productcat

        else:
            master_apicall = MasterAPI()
            productcat = master_apicall.fetch_pdtcat(request, productcat_id)
            logger.info("fetch_productcatdata - api" + str(productcat))
            print("fetch_productcatdata - api", productcat)
            return productcat


    def fetch_hsndata(self, request, hsn_id):
        if self.MICRO_SERVICE:
            comm_ser = Hsnservice()
            comm = comm_ser.fetch_hsn(hsn_id)
            logger.info("fetch_hsndata - serv" + str(comm))
            print("fetch_hsndata - serv", comm)
            return comm
        else:
            mst_api = MasterAPI()
            comm = mst_api.fetch_hsndata(request, hsn_id)
            logger.info("fetch_hsndata" + str(comm))
            print("fetch_hsndata - api", comm)
            print('fetch_hsndata - api', comm)
            return comm


    def fetch_state(self, request, commodity_id):
        if self.MICRO_SERVICE:
            pos_ser = StateService()
            pos = pos_ser.fetch_stateone(commodity_id)
            logger.info("fetch_state - serv" + str(pos))
            print("fetch_state - serv", pos)
            return pos
        else:
            master_apicall = MasterAPI()
            master_commodity = master_apicall.get_stateid(request, commodity_id)
            logger.info("fetch_state - api" + str(master_commodity))
            print("fetch_state - api", master_commodity)
            return master_commodity


    def fetch_city(self, request, product_id):
        if self.MICRO_SERVICE:
            comm_ser = CityService()
            comm = comm_ser.fetch_cityone(product_id)
            logger.info("fetch_city - serv" + str(comm))
            print("fetch_city - serv", comm)
            return comm
        else:
            mst_api = MasterAPI()
            comm = mst_api.fetch_city(request, product_id)
            logger.info("fetch_city - api" + str(comm))
            print("fetch_city - api", comm)
            return comm


    def fetch_pincode(self, request, pincode_id, city_id):
        if self.MICRO_SERVICE:
            comm_ser = PincodeService()
            comm = comm_ser.fetch_pincodeone(pincode_id, city_id)
            logger.info("fetch_pincode - serv" + str(comm))
            print("fetch_pincode - serv", comm)
            return comm
        else:
            mst_api = MasterAPI()
            comm = mst_api.fetch_pincode(request, pincode_id, city_id)
            logger.info("fetch_pincode - api" + str(comm))
            print("fetch_pincode - api", comm)
            return comm


    def get_productcode(self, request, product_code):
        if self.MICRO_SERVICE:
            pr_ser = ProductService()
            mst = pr_ser.get_productcode(product_code)
            logger.info("get_productcode - serv" + str(mst))
            print("get_productcode - serv", mst)
            print("product code serv", mst)
            return mst
        else:
            master_apicall = MasterAPI()
            master_product = master_apicall.get_productcode(request, product_code)
            logger.info("get_productcode - api" + str(master_product))
            print("get_productcode - api", master_product)
            return master_product


    def get_commoditycode(self, request, commodity_code):
        if self.MICRO_SERVICE:
            cd_ser = CommodityService()
            cd = cd_ser.get_commoditycode(commodity_code)
            logger.info("get_commoditycode - serv" + str(cd))
            print("get_commoditycode - serv", cd)
            print("get_commoditycode serv", cd)
            return cd
        else:
            master_apicall = MasterAPI()
            master_commodity = master_apicall.get_commoditycode(request, commodity_code)
            logger.info("get_commoditycode - api" + str(master_commodity))
            print("get_commoditycode - api", master_commodity)
            return master_commodity


    def get_commodityname(self, request, name):
        if self.MICRO_SERVICE:
            pr_ser = CommodityService()
            mst = pr_ser.commodity_name(name)
            logger.info("get_commodityname - serv" + str(mst))
            print("get_commodityname - serv", mst)
            mst = json.loads(mst)
            print("name ", mst)
            return mst
        else:
            master_apicall = MasterAPI()
            master_product = master_apicall.commodity_name(request, name)
            logger.info("get_commodityname - api" + str(master_product))
            print("get_commodityname - api", master_product)
            return master_product


    def get_productname(self, request, name):
        if self.MICRO_SERVICE:
            pr_ser = ProductService()
            mst = pr_ser.product_name(name)
            logger.info("get_productname - serv" + str(mst))
            print("get_productname - serv", mst)
            print("product code serv", mst)
            return mst
        else:
            master_apicall = MasterAPI()
            master_product = master_apicall.product_name(request, name)
            logger.info("get_productname - api" + str(master_product))
            print("get_productname - api", master_product)
            return master_product


    def get_paymodename(self, request, name):
        if self.MICRO_SERVICE:
            pr_ser = PaymodeService()
            mst = pr_ser.fetch_paymodename(name)
            logger.info("get_paymodename - serv" + str(mst))
            print("get_paymodename - serv", mst)
            mst = json.loads(mst)
            print("name ", mst)
            return mst
        else:
            master_apicall = MasterAPI()
            master_product = master_apicall.paymode_name(request, name)
            logger.info("get_paymodename - api" + str(master_product))
            print("get_paymodename - api", master_product)
            return master_product


    def get_commodity(self, request, commodity_id):
        if self.MICRO_SERVICE:
            commodity_ids = {"commodity_id": commodity_id}
            pos_ser = CommodityService()
            pos = pos_ser.commodity_get(commodity_ids)
            logger.info("get_commodity - serv" + str(pos))
            print("get_commodity - serv", pos)
            pos = json.loads(pos)
            return pos
        else:
            master_apicall = MasterAPI()
            master_commodity = master_apicall.get_commodity_data(request, commodity_id)
            logger.info("get_commodity - api" + str(master_commodity))
            print("get_commodity - api", master_commodity)
            return master_commodity


    def get_product(self, request, product_id):
        if self.MICRO_SERVICE:
            product_ids = {"product_id": product_id}
            comm_ser = ProductService()
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


    def productcat_list(self, request, product_id):
        if self.MICRO_SERVICE:
            product_ids = {"product_id": product_id}
            pr_ser = ProductService()
            pr = pr_ser.productcategory_list(product_ids)
            logger.info("productcat_list - serv" + str(pr))
            print("productcat_list - serv", pr)
            pr = json.loads(pr)
            return pr
        else:
            master_apicall = MasterAPI()
            pdtcat_data = master_apicall.productcat_list(request, product_id)
            logger.info("productcat_list - api" + str(pdtcat_data))
            print("productcat_list - api", pdtcat_data)
            return pdtcat_data

    def get_productcat(self, request, product_id, query):
        if self.MICRO_SERVICE:
            pr_ser = ProductService()
            product_ids = {"product_id": product_id}
            pr = pr_ser.productcat_name(product_ids, query)
            logger.info("get_productcat - serv" + str(pr))
            print("get_productcat - serv", pr)
            pr = json.loads(pr)
            return pr
        else:
            master_apicall = MasterAPI()
            productcat = master_apicall.pdtcat_name(request, product_id, query)
            logger.info("get_productcat - api" + str(productcat))
            print("get_productcat - api", productcat)
            return productcat

    def get_producttype(self, request, product_id, query):
        if self.MICRO_SERVICE:
            pr_ser = ProductService()
            product_ids = {"product_id": product_id}
            pr = pr_ser.get_producttype(product_ids, query)
            logger.info("get_producttype - serv" + str(pr))
            print("get_producttype - serv", pr)
            pr = json.loads(pr)
            return pr
        else:
            master_apicall = MasterAPI()
            productcat = master_apicall.producttype_list(request, product_id, query)
            logger.info("get_producttype - api" + str(productcat))
            print("get_producttype - api", productcat)
            return productcat

    def get_producttype_name(self, request, product_id, product_category_id, query):
        if self.MICRO_SERVICE:
            pr_ser = ProductService()
            product_ids = {"product_id": product_id}
            pr = pr_ser.get_producttype_name(product_ids, product_category_id, query)
            logger.info("get_producttype_name - serv" + str(pr))
            print("get_producttype_name - serv", pr)
            pr = json.loads(pr)
            return pr
        else:
            master_apicall = MasterAPI()
            productcat = master_apicall.producttype_name(request, product_id, product_category_id, query)
            logger.info("get_producttype_name - api" + str(productcat))
            print("get_producttype_name - api", productcat)
            return productcat

    def get_product_cat_type(self, request, product_category_id, product_type_id):
        if self.MICRO_SERVICE:
            pr_ser = ProductService()
            pr = pr_ser.product_cat_type(product_category_id, product_type_id)
            logger.info("get_product_cat_type - serv" + str(pr))
            print("get_product_cat_type - serv", pr)
            return pr
        else:
            master_apicall = MasterAPI()
            productcat = master_apicall.product_cat_type(request, product_category_id, product_type_id)
            logger.info("get_product_cat_type - api" + str(productcat))
            print("get_product_cat_type - api", productcat)
            return productcat

    # vendor
    def fetch_supplierbranchdata(self, request, supplierbranch_id):
        if self.MICRO_SERVICE:
            p_ser = branchservice()
            p = p_ser.fetch_supplierbranchdata(supplierbranch_id)
            logger.info("fetch_supplierbranchdata - serv" + str(p))
            print("fetch_supplierbranchdata - serv", p)
            return p
        else:
            vendor_apicall = VendorAPI()
            vendor_supplierbranch = vendor_apicall.fetch_supplierbranchdata(request, supplierbranch_id)
            logger.info("fetch_supplierbranchdata - api" + str(vendor_supplierbranch))
            print("fetch_supplierbranchdata - api", vendor_supplierbranch)
            return vendor_supplierbranch

    def fetch_catelogdata(self, request, id):
        if self.MICRO_SERVICE:
            p_ser = branchservice()
            p = p_ser.fetch_catelogdata(id)
            logger.info("fetch_catelogdata - serv" + str(p))
            print("fetch_catelogdata - serv", p)
            return p
        else:
            vendor_apicall = VendorAPI()
            vendor_supplierbranch = vendor_apicall.fetch_catelogdata(request, id)
            logger.info("fetch_catelogdata - api" + str(vendor_supplierbranch))
            print("fetch_catelogdata - api", vendor_supplierbranch)
            return vendor_supplierbranch

    def supplier_tax(self, request, id, employee_id):
        if self.MICRO_SERVICE:
            director_service = TaxService()
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page = VysfinPage(page, 10)
            resp_obj = director_service.fetch_suppliertax_list(request, vys_page, employee_id, id)
            logger.info("supplier_tax - serv" + str(resp_obj))
            print("supplier_tax - serv", resp_obj)
            taxmaster_service = TaxMasterService()
            subtax_service = SubTaxService()
            taxrate_service = TaxRateService()

            x = resp_obj.data
            for i in x:
                supplierbranch_id = i.vendor_id

                tax1_id = i.tax
                if tax1_id != -1:
                    tax = taxmaster_service.fetch_tax(tax1_id, employee_id)
                    logger.info("fetch_tax - serv" + str(tax))
                    print("fetch_tax - serv", tax)
                    i.tax = tax
                    taxname = i.tax.name

                subtax_id = i.subtax
                if subtax_id != -1:
                    subtax = subtax_service.fetch_subtax(subtax_id, employee_id)
                    logger.info("fetch_subtax - serv" + str(subtax))
                    print("fetch_subtax - serv", subtax)
                    i.subtax = subtax
                    subtax_name = subtax.name

                isTDSExempt = i.isexcempted  # TDS_Exempt

                if i.taxrate == 0:
                    i.taxrate = None
                    taxRate = None  # Tax_Rate
                else:
                    taxrate_id = i.taxrate
                    taxrate = taxrate_service.fetch_taxrate(taxrate_id, employee_id)
                    logger.info("fetch_taxrate - serv" + str(taxrate))
                    print("fetch_taxrate - serv", taxrate)
                    i.taxrate = taxrate
                    taxRate = i.taxrate.rate  # Tax_Rate

                vendor_status = director_service.get_vendorstatus_tax(supplierbranch_id)
                logger.info("get_vendorstatus_tax - serv" + str(vendor_status))
                print("get_vendorstatus_tax - serv", vendor_status)
                i.q_modify = False
                if (i.created_by == employee_id):
                    if (vendor_status == 0 or vendor_status == 1):
                        i.q_modify = True
                print(i)
            return resp_obj.get()
        else:
            vendor_apicall = VendorAPI()
            vendor_supplierbranch = vendor_apicall.supplier_tax(request, id)
            logger.info("supplier_tax - api" + str(vendor_supplierbranch))
            print("supplier_tax - api", vendor_supplierbranch)
            return vendor_supplierbranch

    def supplier_payment(self, request, id, employee_id):
        if self.MICRO_SERVICE:
            payment_service = paymentservice()
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page = VysfinPage(page, 10)
            resp_obj = payment_service.fetch_payment_list(request, vys_page, employee_id, id)
            logger.info("supplier_payment - serv" + str(resp_obj))
            print("supplier_payment - serv", resp_obj)
            bank_service = BankService()
            paymode_service = PaymodeService()
            branch_service = branchservice()
            x = resp_obj.data
            for i in x:
                bank_id = i.bank_id
                if (bank_id == 0) | (bank_id == None) | (bank_id == -1):
                    i.bank_id = ""
                else:
                    bank = bank_service.fetch_bank(bank_id, employee_id)
                    logger.info("supplier_payment - serv" + str(resp_obj))
                    print("supplier_payment - serv", resp_obj)
                    i.bank_id = bank
                paymode_id = i.paymode_id
                paymode = paymode_service.fetchpaymode(paymode_id)
                logger.info("fetchpaymode - serv" + str(paymode))
                print("fetchpaymode - serv", paymode)
                i.paymode_id = paymode
                supplierbranch_id = i.supplierbranch_id
                vendor_status = branch_service.get_vendorstatus_branch(supplierbranch_id)
                logger.info("vendor_status - serv" + str(vendor_status))
                print("vendor_status - serv", vendor_status)
                i.q_modify = False
                if (i.created_by == employee_id):
                    if (vendor_status == 0 or vendor_status == 1):
                        i.q_modify = True
            return resp_obj.get()
        else:
            vendor_apicall = VendorAPI()
            vendor_supplierbranch = vendor_apicall.supplier_payment(request, id)
            logger.info("supplier_payment - api" + str(vendor_supplierbranch))
            print("supplier_payment - api", vendor_supplierbranch)
            return vendor_supplierbranch

    def fetch_venaddress(self, request, add_id):
        if self.MICRO_SERVICE:
            ven_ser = VendorAddressService()
            vendor = ven_ser.fetch_vendoraddress1(add_id)
            logger.info("fetch_venaddress - serv" + str(vendor))
            print("fetch_venaddress - serv", vendor)
            return vendor
        else:
            vendor_service = VendorAPI()
            supplier = vendor_service.fetch_vendoraddress(request, add_id)
            logger.info("fetch_venaddress - api" + str(supplier))
            print("fetch_venaddress - api", supplier)
            return supplier

    def get_supplierbranch(self, request, supplierbranch_id):
        if self.MICRO_SERVICE:
            supplierbranch_ids = {"supplierbranch_id": supplierbranch_id}
            p_ser = branchservice()
            p = p_ser.get_supplierbranch(supplierbranch_ids)
            logger.info("get_supplierbranch - serv" + str(p))
            print("get_supplierbranch - serv", p)
            p = json.loads(p)
            return p
        else:
            vendor_apicall = VendorAPI()
            vendor_supplierbranch = vendor_apicall.get_supplier_data(request, supplierbranch_id)
            logger.info("get_supplierbranch - api" + str(vendor_supplierbranch))
            print("get_supplierbranch - api", vendor_supplierbranch)
            return vendor_supplierbranch

    def get_product_catelogdts(self, request, supplierbranch_id, dts):
        if self.MICRO_SERVICE:
            supplierbranch_ids = {"product_id": supplierbranch_id}
            p_ser = branchservice()
            p = p_ser.catelog_productdts(supplierbranch_ids, dts)
            logger.info("get_product_catelogdts - serv" + str(p))
            print("get_product_catelogdts - serv", p)
            return p
        else:
            vendor_apicall = VendorAPI()
            vendor_supplierbranch = vendor_apicall.catelog_productdts(request, supplierbranch_id, dts)
            logger.info("get_product_catelogdts - api" + str(vendor_supplierbranch))
            print("get_product_catelogdts - api", vendor_supplierbranch)
            return vendor_supplierbranch


    def doc_upload_key(self, request, module_id, filekey):
        if self.MICRO_SERVICE:
            p_ser = DocumentsService(self._scope())
            p = p_ser.document_upload_key(request, module_id, filekey)
            logger.info("doc_upload_key - serv" + str(p))
            print("doc_upload_key - serv", p)
            p = json.loads(p.get())
            return p
        else:
            vendor_apicall = DocAPI()
            #module, prefix
            doc_module = vendor_apicall.doc_upload_ecf(request, module_id)
            print("doc_module api ", doc_module)
            # logger.info("doc_module api "+ str(doc_module))
            params = doc_module
            #s3 bucket
            doc_upload_key = vendor_apicall.document_uploadbucket_key(request, params, filekey)
            print("document_uploadbucket_key api ", doc_upload_key)
            # logger.info("document_uploadbucket_key api " + str(doc_module))
            doc_upload_key=json.loads(doc_upload_key.get())
            # logger.info("document_uploadbucket_key" +str(doc_upload_key))
            #doc
            doc_tableupload = vendor_apicall.doc_upload(request, doc_upload_key)
            print("doc_tableupload api ", doc_tableupload)
            logger.info("doc_tableupload api " + str(doc_tableupload))
            return doc_tableupload

    def doc_upload(self, request, module_id):
        if self.MICRO_SERVICE:
            p_ser = DocumentsService()
            p = p_ser.document_upload(request, module_id)
            print("doc_upload serv ", p)
            logger.info("doc_upload serv " + str(p))
            p = json.loads(p.get())
            return p
        else:
            vendor_apicall = DocAPI()
            #module, prefix
            doc_module = vendor_apicall.doc_module(request, module_id)
            print("doc_module", doc_module)
            params = doc_module
            #s3 bucket
            document_uploadbucket = vendor_apicall.documentb_uploadbucket(request, params)
            print("document_uploadbucket", document_uploadbucket)
            document_uploadbucket=json.loads(document_uploadbucket.get())
            #doc
            doc_upload = vendor_apicall.doc_upload(request, document_uploadbucket)
            print("doc_upload", doc_upload)
            return doc_upload

    def doc_uploadkey(self, request, module_id):
        if self.MICRO_SERVICE:
            p_ser = DocumentsService()
            p = p_ser.document_upload(request, module_id)
            print("doc_uploadkey serv ", p)
            logger.info("doc_uploadkey serv " + str(p))
            p = json.loads(p.get())
            return p
        else:
            vendor_apicall = DocAPI()
            #module, prefix
            doc_module = vendor_apicall.doc_module(request, module_id)
            print("doc_module", doc_module)
            params = doc_module
            #s3 bucket
            document_uploadbucket = vendor_apicall.document_uploadbucket1(request, params)
            print("document_uploadbucket", document_uploadbucket)
            document_uploadbucket=json.loads(document_uploadbucket.get())
            #doc
            doc_upload = vendor_apicall.doc_upload(request, document_uploadbucket)
            print("doc_upload", doc_upload)
            return doc_upload


    def download_m2m(self, request, file_id, emp_id):
        if self.MICRO_SERVICE:
            doc_ser = DocumentsService()
            doc = doc_ser.download(file_id, emp_id)
            print("download_m2m serv ", doc)
            logger.info("download_m2m serv " + str(doc))
            return doc
        else:
            doc_apicall = DocAPI()
            download_m2m = doc_apicall.download_m2m(request, file_id)
            print("download_m2m  api", download_m2m)
            logger.info("download_m2m api " + str(download_m2m))
            #doc doc_download
            doc_download = doc_apicall.doc_download(download_m2m)
            print("doc_download", doc_download)
            logger.info("doc_download api " + str(doc_download))
            return doc_download

    def download_m2m_queryparams(self, request, file_id, emp_id):
        if self.MICRO_SERVICE:
            doc_ser = DocumentsService()
            doc = doc_ser.download(file_id, emp_id)
            print("download_m2m_queryparams serv ", doc)
            logger.info("download_m2m_queryparams serv " + str(doc))
            return doc
        else:
            doc_apicall = DocAPI()
            download_m2m = doc_apicall.download_m2m_queryparams(request, file_id)
            print("download_m2m_queryparams", download_m2m)
            logger.info("download_m2m_queryparams api " + str(download_m2m))
            #doc doc_download
            doc_download = doc_apicall.doc_download(download_m2m)
            print("download_m2m_queryparams", doc_download)
            logger.info("download_m2m_queryparams api " + str(doc_download))
            return doc_download

    def get_employee1(self, request, employee_id):
        if self.MICRO_SERVICE:
            employee_ids = {"employee_id": employee_id}
            po_ser = EmployeeService(self._scope())
            po = po_ser.employee_get(employee_ids)
            logger.info("get_employee - serv" + str(po))
            print("get_employee - serv", po)
            po = json.loads(po)
            return po
        else:
            emp_api = EmployeeAPI()
            po = emp_api.get_employee_data(request, employee_id)
            logger.info("get_employee - api" + str(po))
            print("get_employee - api", po)
            return po