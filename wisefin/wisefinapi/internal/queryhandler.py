from nwisefin import settings
from nwisefin.settings import micro_masterservice


class QueryHandler:
    # employee
    def get_employee(self, id):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'employee_by_userid/' + str(id)
        return employee_url

    def post_employee(self, id):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'employee_id'
        return employee_url

    def fetch_employee_branch_data(self):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'fetch_employee_branch'
        return employee_url
    def fetch_pincodestateid(self, query):
        masterservice_url = micro_masterservice
        master_url = masterservice_url + 'pincode_stateid'
        return master_url
    def create_codegen_det(self):
        masterservice_url = micro_masterservice
        master_url = masterservice_url + 'create_subcat_code_gen'
        return master_url
    def fetch_employee_rolemodule(self):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'employee_modulerole'
        return employee_url

    # VENDOR
    def get_vendor(self, id):
        vendorservice_url = settings.micro_vendorservice
        vendor_url = vendorservice_url + 'commonvendor'
        return vendor_url

    def common_vendor_search(self):
        vendorservice_url = settings.micro_vendorservice
        vendor_url = vendorservice_url + 'common_vendor_search'
        return vendor_url

    # CCBS
    def get_bs(self):
        userservice_url = settings.micro_userservice
        bs_url = userservice_url + 'businesssegmentcommon'
        return bs_url
    def get_bs_list(self):
        userservice_url = settings.micro_userservice
        bs_url = userservice_url + 'businesssegment'
        return bs_url
    def get_cc(self):
        userservice_url = settings.micro_userservice
        cc_url = userservice_url + 'costcentrecommon'
        return cc_url

    # CATEDORY
    def get_category(self, id):
        masterservice_url = settings.micro_masterservice
        apcategory_url = masterservice_url + 'apcategorycommon'
        return apcategory_url

    def get_subcategory(self, id):
        masterservice_url = settings.micro_masterservice
        apcategory_url = masterservice_url + 'apsubcategorycommon'
        return apcategory_url
    def get_subcategory_data(self, id):
        masterservice_url = settings.micro_masterservice
        apcategory_url = masterservice_url + 'apsubcategorycommon_data'
        return apcategory_url

    # EMPLOYEE USERID
    def get_userid(self, token):
        userservice_url = settings.micro_userservice
        authe_url = userservice_url + 'msauthenticate'
        return authe_url

    def emp_details_get(self, ):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'get_emp_details'
        return employee_url

    def login_emp_details_get(self, id):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'get_login_emp_details/' + str(id)
        return employee_url

    def employee_all_details_get(self, empid):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'employee_details_all_get_ta/' + str(empid)
        return employee_url

    def post_commoditydata_apexpense(self, id):
        masterservice_url = settings.micro_masterservice
        vendor_url = masterservice_url + 'fetch_commoditydata_delmat/' + str(id)
        return vendor_url

    def get_branch_data(self, id):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'get_branch_data/' + str(id)
        return employee_url

    def fetch_employee_branch(self):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'fetch_employee_branch'
        return employee_url

    def employee_details_get(self, id):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'employee_details_get/' + str(id)
        return employee_url

    def get_role_bh_emp(self, branch):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'role_bh_emp_get/' + str(branch)
        return employee_url

    def branch_emp_get(self, branch):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'branchwise_employee_get/' + str(branch)
        return employee_url

    def get_multi_employee(self):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'fetch_multi_employee'
        return employee_url

    # sg master
    def get_employeecat(self):
        masterservice_url = settings.micro_masterservice
        authe_url = masterservice_url + 'get_employeecat'
        return authe_url

    def get_employeetype(self):
        masterservice_url = settings.micro_masterservice
        authe_url = masterservice_url + 'get_employeetype'
        return authe_url

    def get_employeetype_name(self, type):
        masterservice_url = settings.micro_masterservice
        authe_url = masterservice_url + 'get_employeetype_name' + '?type=' + type
        return authe_url

    def get_statezone(self):
        masterservice_url = settings.micro_masterservice
        authe_url = masterservice_url + 'get_statezone'
        return authe_url

    def get_statezone_mapping(self):
        masterservice_url = settings.micro_masterservice
        authe_url = masterservice_url + 'get_statezone_mapping'
        return authe_url

    #Courier
    def get_courier_sinle_url(self, courier_id):
        masterservice_url = settings.SERVER_IP
        mstserv_url = masterservice_url + '/mstserv/courier/'+str(courier_id)
        return mstserv_url

    #  branch
    def fetch_branch_data(self):
        userservice_url = settings.micro_userservice
        authe_url = userservice_url + 'fetch_branch_data'
        return authe_url

    # premise
    def fetch_premise_data(self):
        pdservice_url = settings.micro_pdservice
        authe_url = pdservice_url + 'common_premise'
        return authe_url

    # doc serv

    def doc_upload(self):
        doc_service_url = settings.micro_docservice
        authe_url = doc_service_url + 'document'
        return authe_url

    def doc_upload_ta(self):
        doc_service_url = settings.micro_docservice
        authe_url = doc_service_url + 'doc_upload_ta'
        return authe_url

    # ecf
    def get_employeedtl(self, id):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'employee_by_empid/' + str(id)
        return employee_url

    def get_empbranch(self, id):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'get_empbranch/' + str(id)
        return employee_url
    def get_empbranch_empid(self, id):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'get_emp_empid/' + str(id)
        return employee_url

    def get_cc_one(self, code):
        userservice_url = settings.micro_userservice
        cc_url = userservice_url + 'get_cc?query=' + str(code)
        return cc_url

    def get_bs_one(self, code):
        userservice_url = settings.micro_userservice
        bs_url = userservice_url + 'get_bs?query=' + str(code)
        return bs_url

    def get_commodity_one(self, id):
        masterservice_url = settings.micro_masterservice
        com_url = masterservice_url + 'get_commodity/' + str(id)
        return com_url

    def get_commo(self, id):
        masterservice_url = settings.micro_masterservice
        com_url = masterservice_url + 'get_commoditylist'
        return com_url

    def get_state(self, id):
        masterservice_url = settings.micro_masterservice
        com_url = masterservice_url + 'get_statelist'
        return com_url

    def get_state_one(self, id):
        masterservice_url = settings.micro_masterservice
        com_url = masterservice_url + 'get_state/' + str(id)
        return com_url

    def get_bank(self, id):
        masterservice_url = settings.micro_masterservice
        com_url = masterservice_url + 'get_banklist'
        return com_url

    def get_paymode_one(self, id):
        masterservice_url = settings.micro_masterservice
        pay_url = masterservice_url + 'get_paymode/' + str(id)
        return pay_url

    def get_cat_one(self, code):
        masterservice_url = settings.micro_masterservice
        cat_url = masterservice_url + 'get_apcategory?query=' + str(code)
        return cat_url

    def get_subcat_one(self, code):
        masterservice_url = settings.micro_masterservice
        sub_url = masterservice_url + 'get_apsubcategory?query=' + str(code)
        return sub_url

    def get_supplier(self, id):
        vendorservice_url = settings.micro_vendorservice
        vendor_url = vendorservice_url + 'get_supplierlist'
        return vendor_url

    def get_supplier_one(self, id):
        vendorservice_url = settings.micro_vendorservice
        vendor_url = vendorservice_url + 'get_supplier/' + str(id)
        return vendor_url

    # prpo
    def search_employeename(self, emp_name):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'search_employeename/' + str(emp_name)
        return employee_url

    def post_employeedata(self, id):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'employee_get'
        return employee_url

    def post_employeedata_accountdetails(self, id):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'employee_get_apexpense?emp_id='+str(id)
        return employee_url

    def post_employeedata1(self, id):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'employee_get'
        return employee_url

    def post_employeebranchdata(self, id):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'employeebranch_get'
        return employee_url

    def post_supplierdata(self, id):
        vendorservice_url = settings.micro_vendorservice
        vendor_url = vendorservice_url + 'supplierbranch_get'
        return vendor_url

    def post_productdata(self, id):
        masterservice_url = settings.micro_masterservice
        vendor_url = masterservice_url + 'product_get'
        return vendor_url
    def get_productdata(self, id):
        masterservice_url = settings.micro_masterservice
        vendor_url = masterservice_url + 'product/'+str(id)
        return vendor_url
    def get_productdata_code(self, id):
        masterservice_url = settings.micro_masterservice
        vendor_url = masterservice_url + 'product_code/'+str(id)
        return vendor_url
    def post_commoditydata(self, id):
        masterservice_url = settings.micro_masterservice
        vendor_url = masterservice_url + 'commodity_get'
        return vendor_url

    def fetch_commoditydata(self, id):
        masterservice_url = settings.micro_masterservice
        vendor_url = masterservice_url + 'fetch_commoditydata/' + str(id)
        return vendor_url

    def fetch_productdata(self, id):
        masterservice_url = settings.micro_masterservice
        vendor_url = masterservice_url + 'fetch_productdata/' + str(id)
        return vendor_url

    def fetch_employeedata(self, id):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'fetch_employeedata/' + str(id)
        return employee_url

    def fetch_employeebranchdata(self, id):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'fetch_employeebranchdata/' + str(id)
        return employee_url

    def fetch_supplierbranchdata(self, id):
        vendorservice_url = settings.micro_vendorservice
        vendor_url = vendorservice_url + 'fetch_supplierbranchdata/' + str(id)
        return vendor_url

    def fetch_catelogdata(self, id):
        vendorservice_url = settings.micro_vendorservice
        vendor_url = vendorservice_url + 'fetch_catelogdata/' + str(id)
        return vendor_url

    # prpo -- empbranch address
    def fetch_ebranchaddressdata(self, id):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'fetch_ebranchaddressdata/' + str(id)
        return employee_url

    def fetch_apcategorydata(self, id):
        masterservice_url = settings.micro_masterservice
        vendor_url = masterservice_url + 'fetch_apcategorydata/' + str(id)
        return vendor_url

    def employee_list(self):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'employee_list'
        return employee_url

    def supplierbranch(self, id):
        vendorservice_url = settings.micro_vendorservice
        vendor_url = vendorservice_url + 'supplierbranch/' + str(id)
        return vendor_url

    def search_productname(self, query):
        masterservice_url = settings.micro_masterservice
        vendor_url = masterservice_url + 'search_productname' + '?query=' + query
        return vendor_url

    def paymode_name(self, query):
        masterservice_url = settings.micro_masterservice
        vendor_url = masterservice_url + 'paymode_name' + '?query=' + query
        return vendor_url

    def supplier_payment(self, id):
        vendorservice_url = settings.micro_vendorservice
        vendor_url = vendorservice_url + 'supplier_payment/' + str(id)
        # supplier payment/ branch_id
        return vendor_url

    def supplier_tax(self, id):
        vendorservice_url = settings.micro_vendorservice
        vendor_url = vendorservice_url + 'supplier_tax/' + str(id)
        return vendor_url

    def get_authtoken(self):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'get_mono_authtoken'
        return employee_url

    def search_commodityname(self, query):
        masterservice_url = settings.micro_masterservice
        vendor_url = masterservice_url + 'search_commodityname' + '?query=' + query
        return vendor_url

    def fetch_vendoraddress(self, id):
        vendorservice_url = settings.micro_vendorservice
        vendor_url = vendorservice_url + 'fetch_vendoraddress/' + str(id)
        return vendor_url

    def fetch_city(self, id):
        masterservice_url = settings.micro_masterservice
        vendor_url = masterservice_url + 'get_city/' + str(id)
        return vendor_url

    def fetch_pincode(self, id1, id2):
        masterservice_url = settings.micro_masterservice
        vendor_url = masterservice_url + 'get_pincode/' + str(id1) + '/' + str(id2)
        return vendor_url

    def fetch_state(self, id):
        masterservice_url = settings.micro_masterservice
        vendor_url = masterservice_url + 'get_state/' + str(id)
        return vendor_url

    def commodity_name(self, commodity_name):
        masterservice_url = settings.micro_masterservice
        master_url = masterservice_url + 'commodity_name/' + str(commodity_name)
        return master_url

    def producttype_list(self, product_arr, id):
        masterservice_url = settings.micro_masterservice
        master_url = masterservice_url + 'producttype_list/' + str(id)
        return master_url

    def productcat_list(self, id):
        masterservice_url = settings.micro_masterservice
        master_url = masterservice_url + 'productcat_list'
        return master_url

    def product_cat_type(self, id1, id2):
        masterservice_url = settings.micro_masterservice
        master_url = masterservice_url + 'product_cat_type/' + str(id1) + '/' + str(id2)
        return master_url

    def product_name(self, query):
        masterservice_url = settings.micro_masterservice
        master_url = masterservice_url + 'product_name' + '?query=' + query
        return master_url

    def catelog_productdts(self, product_arr, id):
        masterservice_url = settings.micro_vendorservice
        master_url = masterservice_url + 'catelog_productdts/' + str(id)
        return master_url

    def fetch_uomdata(self, id):
        masterservice_url = settings.micro_masterservice
        vendor_url = masterservice_url + 'uom/' + str(id)
        return vendor_url

    def fetch_pdtcat(self, id):
        masterservice_url = settings.micro_masterservice
        vendor_url = masterservice_url + 'pdtcat/' + str(id)
        return vendor_url

    def fetch_pdttype(self, id):
        masterservice_url = settings.micro_masterservice
        vendor_url = masterservice_url + 'pdttype/' + str(id)
        return vendor_url

    def pdtcat_name(self, p_arr, query):
        masterservice_url = settings.micro_masterservice
        master_url = masterservice_url + 'pdtcat_name' + '?query=' + query
        return master_url

    def producttype_name(self, p_arr, category, query):
        masterservice_url = settings.micro_masterservice
        master_url = masterservice_url + 'producttype_name/' + str(category) + '?query=' + query
        return master_url

    # prpo- doc serv
    def doc_upload_post(self):
        doc_service_url = settings.micro_docservice
        authe_url = doc_service_url + 'document_upload'
        return authe_url
    #vendor data
    def get_vendor_data(self,id):
        vendor_url=settings.micro_vendorservice
        vendor_get_url=vendor_url+'getoldatmadata/'+str(id)
        return vendor_get_url
    def fetch_vendor_data(self,id):
        vendor_url=settings.micro_vendorservice
        vendor_get_url=vendor_url+'vendor/'+str(id)
        return vendor_get_url
    def fetch_vendor_data_code(self,code):
        vendor_url=settings.micro_vendorservice
        vendor_get_url=vendor_url+'fetch_supplier_code/'+str(code)
        return vendor_get_url
    def get_vendor_code(self,id):
        vendor_url=settings.micro_vendorservice
        vendor_get_url=vendor_url+'vendor_code/'+str(id)
        return vendor_get_url
    def empbranch_using_id(self,id):
        emp_url=settings.micro_userservice
        branch_url=emp_url+'fetch_employeebranchdata/'+str(id)
        return branch_url
    def empbranch_using_code(self,id):
        emp_url=settings.micro_userservice
        branch_url=emp_url+'fetch_employeebranchdata_code/'+str(id)
        return branch_url
    #ecf
    def get_hsn_one(self, code):
        masterservice_url = settings.micro_masterservice
        hsn_url = masterservice_url + 'get_hsn?query=' + str(code)
        return hsn_url
    def get_subtax(self, id):
        vendorservice_url = settings.micro_vendorservice
        vendor_url = vendorservice_url + 'supplier_tds'
        return vendor_url
    def get_subtaxlist(self, id):
        masterservice_url = settings.micro_masterservice
        com_url = masterservice_url + 'get_subtax'
        return com_url
    def get_taxratelist(self, id):
        masterservice_url = settings.micro_masterservice
        com_url = masterservice_url + 'get_taxrate'
        return com_url
    def get_codegen(self, qty,prod):
        masterservice_url = settings.micro_masterservice
        com_url = masterservice_url + 'codegenerator?product='+str(prod)+'&qty='+str(qty)
        return com_url
    def get_userbranch(self, id):
        masterservice_url = settings.micro_masterservice
        com_url = masterservice_url + 'user_branch'
        return com_url
    #ecf end

    #TA

    def ecf_category_code(self, id):
        masterservice_url = settings.micro_masterservice
        mstserv_url = masterservice_url + 'category_id/'+str(id)
        return mstserv_url

    def ecf_subcategory_code(self, id):
        masterservice_url = settings.micro_masterservice
        mstserv_url = masterservice_url + 'subcategory_id/'+str(id)
        return mstserv_url

    def cat_no_get(self, courier_id):
        masterservice_url = settings.micro_masterservice
        mstserv_url = masterservice_url + 'category_no_get/'+str(courier_id)
        return mstserv_url

    def sub_cat_no_get(self, no,cat_id):
        masterservice_url = settings.micro_masterservice
        mstserv_url = masterservice_url + 'subcategory_no_get/'+str(no)+"/no/"+str(cat_id)
        return mstserv_url

    def get_state_id(self, city_name):
        masterservice_url = settings.micro_masterservice
        mstserv_url = masterservice_url + 'state_id/'+str(city_name)
        return mstserv_url

    def doc_module_ta(self):
        doc_service_url = settings.micro_docservice
        authe_url = doc_service_url + 'doc_module_ta'
        return authe_url
    def doc_upload_singlefilename(self):
        docserv_url=settings.micro_docservice
        doc_url=docserv_url+'document_single'

    def doc_upload_ecf(self):
        doc_service_url = settings.micro_docservice
        authe_url = doc_service_url + 'doc_upload'
        return authe_url

    def get_employeename(self, query):
        userservice_url = settings.micro_userservice
        master_url = userservice_url + 'get_employeename' + '?query=' + query
        return master_url


    def get_employeename_data(self, query):
        userservice_url = settings.micro_userservice
        employee_url = userservice_url + 'get_employeename_data'
        return employee_url


    def get_doctype(self, doctype_id):
        masterservice_url = settings.micro_userservice
        vendor_url = masterservice_url + 'get_doctype'
        return vendor_url


    def bankbranch_url(self, id):
        masterservice_url = settings.micro_masterservice
        mstserv_url = masterservice_url + 'bankbranch_search/'+str(id)
        return mstserv_url
    def paymode_list_url(self):
        masterservice_url = settings.micro_masterservice
        mstserv_url = masterservice_url + 'paymode'
        return mstserv_url
    def fetch_state_id_url(self,id):
        masterservice_url = settings.micro_masterservice
        mstserv_state_url = masterservice_url + 'state_new/'+str(id)
        return mstserv_state_url

    def fetch_department_id_url(self, dept_id):
        masterservice_url = settings.micro_masterservice
        mstserv_department_url = masterservice_url + 'department/' + str(dept_id)
        return mstserv_department_url

    def fetch_designation_id_url(self, designation_id):
        masterservice_url = settings.micro_masterservice
        mstserv_designation_url = masterservice_url + 'designation/' + str(designation_id)
        return mstserv_designation_url

    def get_asset_approve(self):
        entryservice_url = settings.micro_entryservice
        ent_serv_fa_approve = entryservice_url +'facommonquerydata '
        return ent_serv_fa_approve
    def set_asset_entry(self):
        entryservice_url = settings.micro_entryservice
        ent_serv_fa_approve = entryservice_url +'entrydetails'
        return ent_serv_fa_approve

    def get_userbranchctrl(self):
        userservice_url = settings.micro_userservice
        com_url = userservice_url + 'user_branch_ctrl'
        return com_url

    def fetch_district_id_url(self, district_id):
        masterservice_url = settings.micro_masterservice
        mstserv_district_url = masterservice_url + 'district/' + str(district_id)
        return mstserv_district_url
    def fetch_pincode_id_url(self, pincode_id):
        masterservice_url = settings.micro_masterservice
        mstserv_pincode_url = masterservice_url + 'pincode/' + str(pincode_id)
        return mstserv_pincode_url

    def fetch_upload_single_file_url(self):
        docservice_url = settings.micro_docservice
        upload_single_file_url = docservice_url + 'document_single'
        return upload_single_file_url
    def fetch_rm_name_url(self,query):
        userservice_url = settings.micro_userservice
        fetch_rm_name_url = userservice_url + 'searchrm'+ '?query=' + query
        return fetch_rm_name_url
    #vendor
    def question_typeget(self, type_id):
        masterservice_url = settings.micro_masterservice
        mstserv_pincode_url = masterservice_url + 'question_typeget/' + str(type_id)
        return mstserv_pincode_url
    def get_vendorclassficationtype(self, type_id):
        masterservice_url = settings.micro_masterservice
        mstserv_pincode_url = masterservice_url + 'get_vendorclassficationtype'
        return mstserv_pincode_url
