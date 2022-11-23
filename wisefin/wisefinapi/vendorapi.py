from wisefinapi.internal.queryhandler import QueryHandler
from wisefinapi.internal.tokenhandler import TokenHandler
from wisefinapi.internal.apicalling import APICall

import json
class VendorAPI:
	def get_vendordetails(self,request,vendor_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		vendor_ids = {"vendor_id": vendor_id}
		vendor_data = json.dumps(vendor_ids, indent=4)
		url=query_handler.get_vendor(vendor_data)
		headers=token_handler.get_token(request)
		resp=api_calling.call_post(url,headers,vendor_data)
		return resp

	def common_vendor_search(self,request):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url=query_handler.common_vendor_search()
		headers=token_handler.get_token(request)
		resp=api_calling.call_get(url,headers)
		return resp

	# ecf
	def get_supplier(self, request, supplier_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		supplier_ids = {"supplier_id": supplier_id}
		supplier_data = json.dumps(supplier_ids, indent=2)
		print('codata', supplier_data)
		url = query_handler.get_supplier(supplier_data)
		headers = token_handler.get_token(request)
		resp = api_calling.call_post(url, headers, supplier_data)
		return resp

	def get_supplierid(self, request, supplier_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.get_supplier_one(supplier_id)
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		return json.loads(resp.text)
	#prpo
	def get_supplier_data(self,request,supplier_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		supplier_ids = {"supplierbranch_id": supplier_id}
		supplier_data = json.dumps(supplier_ids, indent=4)
		url=query_handler.post_supplierdata(supplier_data)
		headers=token_handler.get_token(request)
		resp=api_calling.call_post(url,headers,supplier_data)
		return resp

	def fetch_catelogdata(self, request, catelog_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.fetch_catelogdata(catelog_id)
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		resp = json.loads(resp.text)
		return resp

	def fetch_supplierbranchdata(self, request, supplierbranch_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.fetch_supplierbranchdata(supplierbranch_id)
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		resp = json.loads(resp.text)
		return resp

	def supplierbranch(self, request, supplierbranch_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.supplierbranch(supplierbranch_id)
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		resp = json.loads(resp.text)
		return resp

	def supplier_payment(self, request, supplierbranch_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.supplier_payment(supplierbranch_id)
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		resp = json.loads(resp.text)
		return resp

	def supplier_tax(self, request, vendor_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.supplier_tax(vendor_id)
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		resp = json.loads(resp.text)
		return resp

	def fetch_vendoraddress(self, request, vendoraddress_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.fetch_vendoraddress(vendoraddress_id)
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		resp = json.loads(resp.text)
		return resp

	def catelog_productdts(self, request, product_id, dts):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		product_ids = {"product_id": product_id}
		product_data = json.dumps(product_ids, indent=4)
		url = query_handler.catelog_productdts(product_data, dts)
		headers = token_handler.get_token(request)
		resp = api_calling.call_post(url, headers, product_data)
		return resp
	def get_vendor_data(self, request, vendor_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.get_vendor_data(vendor_id)
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		return json.loads(resp.text)
	def get_vendor_code(self, vendor_id,request):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.get_vendor_code(vendor_id)
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		return json.loads(resp.text)
	def fetch_vendor_data(self, request,vendor_id):
			query_handler = QueryHandler()
			token_handler = TokenHandler()
			api_calling = APICall()
			url = query_handler.fetch_vendor_data(vendor_id)
			headers = token_handler.get_token(request)
			resp = api_calling.call_get(url, headers)
			return json.loads(resp.text)
	def fetch_vendor_data_code(self,vendor_code,request):
			query_handler = QueryHandler()
			token_handler = TokenHandler()
			api_calling = APICall()
			url = query_handler.fetch_vendor_data_code(vendor_code)
			headers = token_handler.get_token(request)
			resp = api_calling.call_get(url, headers)
			return json.loads(resp.text)

	#ecf
	def get_subtax(self, request, vendor_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		vendor_ids = {"vendor_id": vendor_id}
		vendor_data = json.dumps(vendor_ids, indent=2)
		print('codata', vendor_data)
		url = query_handler.get_subtax(vendor_data)
		headers = token_handler.get_token(request)
		resp = api_calling.call_post(url, headers, vendor_data)
		return resp