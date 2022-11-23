from wisefinapi.internal.queryhandler import QueryHandler
from wisefinapi.internal.tokenhandler import TokenHandler
from wisefinapi.internal.apicalling import APICall
import json


class MasterAPI:
    def get_bsdetails(self, request, bs_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        bs_ids = {"bs_id": bs_id}
        bs_data = json.dumps(bs_ids, indent=4)
        url = query_handler.get_bs(bs_data)
        headers = token_handler.get_token(request)
        resp = api_calling.call_post(url, headers, bs_data)
        return resp

    def get_commodity_data_apexpense(self, request, commodity_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.post_commoditydata_apexpense(commodity_id)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        return resp

    def get_ccdetails(self, request, cc_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        cc_ids = {"cc_id": cc_id}
        cc_data = json.dumps(cc_ids, indent=4)
        url = query_handler.get_cc(cc_data)
        headers = token_handler.get_token(request)
        resp = api_calling.call_post(url, headers, cc_data)
        return resp
    def get_bs_list(self, request):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.get_bs_list()
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        return resp
    def fetch_pincode_state(self, request, code):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.fetch_pincodestateid(code)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get_params(url, headers,code)
        resp = json.loads(resp.content)
        return resp
    def create_codegen_detail(self,subcat_id,request):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.create_codegen_det()
        headers = token_handler.get_token(request)
        resp = api_calling.call_post(url,headers,subcat_id)
        resp = json.loads(resp.content)
        return resp
    def get_apcatdetails(self, request, category_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        category_ids = {"category_id": category_id}
        cat_data = json.dumps(category_ids, indent=4)
        url = query_handler.get_category(cat_data)
        headers = token_handler.get_token(request)
        resp = api_calling.call_post(url, headers, cat_data)
        return resp

    def get_apsubcatdetails(self, request, subcategory_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        subcategory_ids = {"subcategory_id": subcategory_id}
        subcat_data = json.dumps(subcategory_ids, indent=4)
        url = query_handler.get_subcategory(subcat_data)
        headers = token_handler.get_token(request)
        resp = api_calling.call_post(url, headers, subcat_data)
        return resp
    def get_apsubcatdetails_data(self, request, subcategory_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        subcategory_ids = {"subcategory_id": subcategory_id}
        subcat_data = json.dumps(subcategory_ids, indent=4)
        url = query_handler.get_subcategory_data(subcat_data)
        headers = token_handler.get_token(request)
        resp = api_calling.call_post(url, headers, subcat_data)
        return resp

    # SG MASTER
    def get_employeecat(self, request, arr):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        data = {"arr": arr}
        arr_data = json.dumps(data, indent=4)
        url = query_handler.get_employeecat()
        headers = token_handler.get_token(request)
        resp = api_calling.call_post(url, headers, arr_data)
        return resp

    def get_employeetype(self, request, arr):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        data = {"arr": arr}
        arr_data = json.dumps(data, indent=4)
        url = query_handler.get_employeetype()
        headers = token_handler.get_token(request)
        resp = api_calling.call_post(url, headers, arr_data)
        return resp

    def get_employeetype_name(self, request, type):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        # data = {"arr": arr}
        # arr_data = json.dumps(data, indent=4)
        url = query_handler.get_employeetype_name(type)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        return resp

    def get_statezone(self, request, arr):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        data = {"arr": arr}
        arr_data = json.dumps(data, indent=4)
        url = query_handler.get_statezone()
        headers = token_handler.get_token(request)
        resp = api_calling.call_post(url, headers, arr_data)
        return resp

    def get_statezone_mapping(self, request, arr):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        data = {"arr": arr}
        arr_data = json.dumps(data, indent=4)
        url = query_handler.get_statezone_mapping()
        headers = token_handler.get_token(request)
        resp = api_calling.call_post(url, headers, arr_data)
        return resp

    # ecf
    def get_commodity(self, request, comm_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        commodity_ids = {"commo_id1": comm_id}
        commodity_data = json.dumps(commodity_ids, indent=2)
        print('codata', commodity_data)
        url = query_handler.get_commo(commodity_data)
        headers = token_handler.get_token(request)
        resp = api_calling.call_post(url, headers, commodity_data)
        return resp

    def get_state(self, request, state_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        state_ids = {"state_id": state_id}
        state_data = json.dumps(state_ids, indent=2)
        print('statedata', state_data)
        url = query_handler.get_state(state_data)
        headers = token_handler.get_token(request)
        resp = api_calling.call_post(url, headers, state_data)
        return resp

    def get_commodityid(self, request, commodity_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.get_commodity_one(commodity_id)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        resp = json.loads(resp.text)
        return resp

    def get_stateid(self, request, state_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.get_state_one(state_id)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        resp = json.loads(resp.text)
        return resp

    def get_bank(self, request, bank_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        bank_ids = {"bank_id": bank_id}
        bank_data = json.dumps(bank_ids, indent=2)
        print('bankdata', bank_data)
        url = query_handler.get_bank(bank_data)
        headers = token_handler.get_token(request)
        resp = api_calling.call_post(url, headers, bank_data)
        return resp

    def get_paymodeid(self, request, paymode_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.get_paymode_one(paymode_id)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        resp = json.loads(resp.text)
        return resp

    def get_catcode(self, request, cat_code):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.get_cat_one(cat_code)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        resp = json.loads(resp.text)
        return resp

    def get_subcatcode(self, request, subcat_code):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.get_subcat_one(subcat_code)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        resp = json.loads(resp.text)
        return resp

    # ecf end

    # prpo
    def fetch_apcategorydata(self, request, category_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.fetch_apcategorydata(category_id)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        resp = json.loads(resp.text)
        return resp

    # prpo
    def get_commodity_data(self, request, commodity_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        commodity_ids = {"commodity_id": commodity_id}
        commodity_data = json.dumps(commodity_ids, indent=4)
        url = query_handler.post_commoditydata(commodity_data)
        headers = token_handler.get_token(request)
        resp = api_calling.call_post(url, headers, commodity_data)
        return resp

    def get_product_data(self, request, product_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        product_ids = {"product_id": product_id}
        product_data = json.dumps(product_ids, indent=4)
        url = query_handler.post_productdata(product_data)
        headers = token_handler.get_token(request)
        resp = api_calling.call_post(url, headers, product_data)
        return resp

    def get_product_using_id(self, request, product_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.get_productdata(product_id)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        return json.loads(resp.text)
    def get_product_using_code(self, request, product_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.get_productdata_code(product_id)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        return json.loads(resp.text)

    def fetch_commoditydata(self, request, commodity_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.fetch_commoditydata(commodity_id)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        resp = json.loads(resp.text)
        return resp

    def fetch_productdata(self, request, product_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.fetch_productdata(product_id)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        resp = json.loads(resp.text)
        return resp

    def search_productname(self, request, query):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.search_productname(query)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        resp = json.loads(resp.text)
        return resp

    def paymode_name(self, request, query):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.paymode_name(query)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        resp = json.loads(resp.text)
        return resp

    def search_commodityname(self, request, query):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.search_commodityname(query)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        resp = json.loads(resp.text)
        return resp

    def fetch_city(self, request, city_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.fetch_city(city_id)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        resp = json.loads(resp.text)
        return resp

    def fetch_pincode(self, request, pincode_id, city_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.fetch_pincode(pincode_id, city_id)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        resp = json.loads(resp.text)
        return resp

    def fetch_state(self, request, state_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.fetch_state(state_id)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        resp = json.loads(resp.text)
        return resp

    def commodity_name(self, request, commodity_name):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.commodity_name(commodity_name)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        resp = json.loads(resp.text)
        return resp

    def producttype_list(self, request, product_id, cat):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        product_ids = {"product_id": product_id}
        product_data = json.dumps(product_ids, indent=4)
        url = query_handler.producttype_list(product_data, cat)
        headers = token_handler.get_token(request)
        resp = api_calling.call_post(url, headers, product_data)
        return resp

    def productcat_list(self, request, product_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        product_ids = {"product_id": product_id}
        product_data = json.dumps(product_ids, indent=4)
        url = query_handler.productcat_list(product_data)
        headers = token_handler.get_token(request)
        resp = api_calling.call_post(url, headers, product_data)
        return resp

    def product_cat_type(self, request, product_category_id, product_type_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.product_cat_type(product_category_id, product_type_id)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        resp = json.loads(resp.text)
        return resp

    def product_name(self, request, query):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.product_name(query)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        resp = json.loads(resp.text)
        return resp

    def fetch_uomdata(self, request, uom_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.fetch_uomdata(uom_id)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        resp = json.loads(resp.text)
        return resp

    def fetch_pdtcat(self, request, pdtcat_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.fetch_pdtcat(pdtcat_id)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        resp = json.loads(resp.text)
        return resp

    def pdtcat_name(self, request, product_id, query):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        product_ids = {"product_id": product_id}
        product_data = json.dumps(product_ids, indent=4)
        url = query_handler.pdtcat_name(product_data, query)
        headers = token_handler.get_token(request)
        resp = api_calling.call_post(url, headers, product_data)
        return resp

    def producttype_name(self, request, product_id, category, query):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        product_ids = {"product_id": product_id}
        product_data = json.dumps(product_ids, indent=4)
        url = query_handler.producttype_name(product_data, category, query)
        headers = token_handler.get_token(request)
        resp = api_calling.call_post(url, headers, product_data)
        return resp

    def fetch_pdttype(self, request, pdttype_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.fetch_pdttype(pdttype_id)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        resp = json.loads(resp.text)
        return resp
    #ecf
    def get_hsncode(self, request, hsn_code):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.get_subcat_one(hsn_code)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        resp = json.loads(resp.text)
        return resp
    #ecf end
    #ecf
    def get_subtax(self, request, subtax_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        subtax_ids = {"subtax_id": subtax_id}
        subtax_data = json.dumps(subtax_ids, indent=2)
        print('subtax_data', subtax_data)
        url = query_handler.get_subtaxlist(subtax_data)
        headers = token_handler.get_token(request)
        resp = api_calling.call_post(url, headers, subtax_data)
        return resp
    def get_taxrate(self, request, subtax_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        subtax_ids = {"subtax_id": subtax_id}
        subtax_data = json.dumps(subtax_ids, indent=2)
        print('subtax_data', subtax_data)
        url = query_handler.get_subtaxlist(subtax_data)
        headers = token_handler.get_token(request)
        resp = api_calling.call_post(url, headers, subtax_data)
        return resp
    def fetch_codegen_list(self, params,request):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()

        url = query_handler.get_codegen(params['product_id'],params['QTY'])
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url,headers)
        return resp
    #get_courier_single_data_api_call
    def get_courier_single(self, request, courier_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.get_courier_sinle_url(courier_id)
        headers = token_handler.get_token(request)
        api_resp = api_calling.call_get(url, headers)
        courierdata_resp=json.loads(api_resp.content)
        return courierdata_resp

    # TA
    def city_name(self, request, city_name):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.get_state_id(city_name)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        return resp

    def ecf_category_code(self, request, id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.ecf_category_code(id)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        return resp

    def ecf_subcategory_code(self, request, id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.ecf_subcategory_code(id)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        return resp

    def cat_no_get(self, request, no):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.cat_no_get(no)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        return resp

    def sub_cat_no_get(self, request, no, cat_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.sub_cat_no_get(no, cat_id)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        return resp

    # def get_courier(self, request, courier_id):
    #     query_handler = QueryHandler()
    #     token_handler = TokenHandler()
    #     api_calling = APICall()
    #     courier_ids = {"courier_id": courier_id}
    #     courier_data = json.dumps(courier_ids, indent=4)
    #     url = query_handler.get_courier(courier_data)
    #     headers = token_handler.get_token(request)
    #     resp = api_calling.call_post(url, headers, courier_data)
    #     return resp
    #
    # def fetch_courierdata(self, request, courier_id):
    #     query_handler = QueryHandler()
    #     token_handler = TokenHandler()
    #     api_calling = APICall()
    #     url = query_handler.fetch_courierdata(courier_id)
    #     print("url ", url)
    #     headers = token_handler.get_token(request)
    #     resp = api_calling.call_get(url, headers)
    #     print(resp.text)
    #     print("status_code ", resp.status_code)
    #     resp = json.loads(resp.text)
    #     return resp
    #
    # def get_channel(self, request, channel_id):
    #     query_handler = QueryHandler()
    #     token_handler = TokenHandler()
    #     api_calling = APICall()
    #     channel_ids = {"channel_id": channel_id}
    #     doc_data = json.dumps(channel_ids, indent=4)
    #     url = query_handler.get_channel(doc_data)
    #     headers = token_handler.get_token(request)
    #     resp = api_calling.call_post(url, headers, doc_data)
    #     return resp
    #
    # def fetch_channeldata(self, request, channel_id):
    #     query_handler = QueryHandler()
    #     token_handler = TokenHandler()
    #     api_calling = APICall()
    #     url = query_handler.fetch_channeldata(channel_id)
    #     print("url ", url)
    #     headers = token_handler.get_token(request)
    #     resp = api_calling.call_get(url, headers)
    #     resp = json.loads(resp.text)
    #     return resp

    def get_doctype(self, request, doctype_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        doctype_ids = {"doctype_id": doctype_id}
        doc_data = json.dumps(doctype_ids, indent=4)
        url = query_handler.get_doctype(doc_data)
        headers = token_handler.get_token(request)
        resp = api_calling.call_post(url, headers, doc_data)
        return resp

    # def fetch_doctypedata(self, request, doctype_id):
    #     query_handler = QueryHandler()
    #     token_handler = TokenHandler()
    #     api_calling = APICall()
    #     url = query_handler.fetch_doctypedata(doctype_id)
    #     headers = token_handler.get_token(request)
    #     resp = api_calling.call_get(url, headers)
    #     resp = json.loads(resp.text)
    #     return resp

    def bankbranch_api(self, request, bank_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.bankbranch_url(bank_id)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        return resp

    def get_paymodeList(self,request):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.paymode_list_url()
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        return resp
    def get_state_id_new(self, request, state_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.fetch_state_id_url(state_id)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        return resp

    def fetch_department_id(self, request, dept_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.fetch_department_id_url(dept_id)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        return resp

    def fetch_designation_id(self, request, designation_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.fetch_designation_id_url(designation_id)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        return resp
    def asset_approve_api(self,id,module,emp_id,request):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        doctype_ids = {"id": id,"module_name":module}
        doc_data = json.dumps(doctype_ids, indent=4)
        url = query_handler.get_asset_approve()
        headers = token_handler.get_token(request)
        resp = api_calling.call_post(url, headers, doc_data)
        return resp
    def create_entrydetails(self,request,emp_id,entry_obj):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        doctype_ids = entry_obj
        doc_data = json.dumps(doctype_ids, indent=4)
        url = query_handler.set_asset_entry()
        headers = token_handler.get_token(request)
        resp = api_calling.call_post(url, headers, doc_data)
        return resp

    def fetch_district(self,request,district_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.fetch_district_id_url(district_id)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        return resp

    def fetch_pincode_id(self,request,pincode_id):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.fetch_pincode_id_url(pincode_id)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        return resp
    def upload_single_file(self,request,file,params):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        doc_data = {"params": params,"file":file}
        resp_data = json.dumps(doc_data, indent=4)
        url = query_handler.fetch_upload_single_file_url()
        headers = token_handler.get_headers(request)
        resp = api_calling.call_post(url, headers, resp_data)
        return resp

    def fetch_rm_name(self, request, query):
        query_handler = QueryHandler()
        token_handler = TokenHandler()
        api_calling = APICall()
        url = query_handler.fetch_rm_name_url(query)
        headers = token_handler.get_token(request)
        resp = api_calling.call_get(url, headers)
        return resp

