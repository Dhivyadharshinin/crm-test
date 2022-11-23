from wisefinapi.internal.queryhandler import QueryHandler
from wisefinapi.internal.tokenhandler import TokenHandler
from wisefinapi.internal.apicalling import APICall

import json
class EmployeeAPI:
	def get_emp_by_userid(self,request,user_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url=query_handler.get_employee(user_id)
		headers=token_handler.get_token(request)
		resp=api_calling.call_get(url,headers)
		resp = json.loads(resp.text)
		return resp

	def post_empolyee_id(self,request,emp_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		emp_ids = {"employee_id": emp_id}
		emp_data = json.dumps(emp_ids, indent=4)
		url=query_handler.post_employee(emp_data)
		headers=token_handler.get_token(request)
		resp=api_calling.call_post(url,headers,emp_data)
		return resp

	def get_usertoken(self,request):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url=query_handler.get_userid(request)
		headers=token_handler.get_token(request)
		resp=api_calling.call_get(url,headers)
		resp = json.loads(resp.text)
		return resp

	def get_emp_details(self,request,emp_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		emp_data = {"id": emp_id}
		data = json.dumps(emp_data, indent=4)
		url=query_handler.emp_details_get()
		headers=token_handler.get_token(request)
		resp=api_calling.call_post(url,headers,data)
		return resp

	def employee_all_details_get(self,request,empid):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url=query_handler.employee_all_details_get(empid)
		headers=token_handler.get_token(request)
		resp=api_calling.call_get(url,headers)
		return json.loads(resp.text)

	def get_login_emp_details(self,request,emp_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url=query_handler.login_emp_details_get(emp_id)
		headers=token_handler.get_token(request)
		resp=api_calling.call_get(url,headers)
		resp = json.loads(resp.text)
		return resp

	# def get_emp_grade1(self,request,emp_id):
	# 	query_handler = QueryHandler()
	# 	token_handler = TokenHandler()
	# 	api_calling = APICall()
	# 	url=query_handler.get_emp_grade1(emp_id)
	# 	headers=token_handler.get_token(request)
	# 	resp=api_calling.call_get(url,headers)
	# 	resp = resp.text
	# 	return resp

	def get_branch_data(self,request,branch):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url=query_handler.get_branch_data(branch)
		headers=token_handler.get_token(request)
		resp=api_calling.call_get(url,headers)
		resp = json.loads(resp.text)
		return resp

	def fetch_employee_branch(self,request,branch):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url=query_handler.fetch_employee_branch()
		headers=token_handler.get_token(request)
		data=json.dumps({"arr":[branch]})
		resp=api_calling.call_post(url,headers,data)
		# resp = resp.text
		return resp

	def employee_details_get(self,request,empid):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url=query_handler.employee_details_get(empid)
		headers=token_handler.get_token(request)
		resp=api_calling.call_get(url,headers)
		resp = json.loads(resp.text)
		return resp

	# def search_hsncode(self,request,query, vys_page):
	# 	query_handler = QueryHandler()
	# 	token_handler = TokenHandler()
	# 	api_calling = APICall()
	# 	url=query_handler.search_hsncode()
	# 	headers=token_handler.get_token(request)
	# 	resp=api_calling.call_get(url,headers)
	# 	resp = resp.text
	# 	return resp

	# def get_emp_branch_details(self,request,branch_id):
	# 	query_handler = QueryHandler()
	# 	token_handler = TokenHandler()
	# 	api_calling = APICall()
	# 	branch_data = {"id": branch_id}
	# 	data = json.dumps(branch_data, indent=4)
	# 	url=query_handler.emp_branch_details_get()
	# 	headers=token_handler.get_token(request)
	# 	resp=api_calling.call_post(url,headers,data)
	# 	return resp

	def role_bh_emp_get(self,branch,approver,maker,request):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url=query_handler.get_role_bh_emp(branch)
		headers=token_handler.get_token(request)
		data={"approver":approver,"maker":json.dumps(maker)}
		resp=api_calling.call_get_params(url,headers,data)
		resp = json.loads(resp.text)
		return resp

	def cc_get(self,request,id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		cc_data = {"cc_id": id}
		data = json.dumps(cc_data, indent=4)
		url=query_handler.get_cc()
		headers=token_handler.get_token(request)
		resp=api_calling.call_post(url,headers,data)
		return resp

	def bs_get(self,request,id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		cc_data = {"bs_id": id}
		data = json.dumps(cc_data, indent=4)
		url=query_handler.get_bs()
		headers=token_handler.get_token(request)
		resp=api_calling.call_post(url,headers,data)
		return resp

	def branch_employee(self,branch,request,maker):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url=query_handler.branch_emp_get(branch)
		headers=token_handler.get_token(request)
		page=request.GET.get('page')
		data=({"page":page,"maker":maker})
		resp=api_calling.call_get_params(url,headers,data)
		resp = json.loads(resp.text)
		return resp

	# def search_employeebranch(self,request):
	# 	query_handler = QueryHandler()
	# 	token_handler = TokenHandler()
	# 	api_calling = APICall()
	# 	url=query_handler.search_employeebranch()
	# 	headers=token_handler.get_token(request)
	# 	name=request.GET.get('name')
	# 	data=({"name":name})
	# 	resp=api_calling.call_get_params(url,headers,data)
	# 	resp = json.loads(resp.text)
	# 	return resp

	# def search_employee_exclude_maker(self,branch,request):
	# 	query_handler = QueryHandler()
	# 	token_handler = TokenHandler()
	# 	api_calling = APICall()
	# 	url=query_handler.search_employee_exclude_maker(branch)
	# 	headers=token_handler.get_token(request)
	# 	name=request.GET.get('name')
	# 	data=({"name":name})
	# 	resp=api_calling.call_get_params(url,headers,data)
	# 	resp = json.loads(resp.text)
	# 	return resp

	def fetch_employee_branch_data(self,request,arr):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		branch_ids = {"arr": arr}
		emp_data = json.dumps(branch_ids, indent=4)
		url=query_handler.fetch_employee_branch_data()
		headers=token_handler.get_token(request)
		resp=api_calling.call_post(url,headers,emp_data)
		return resp

	def fetch_employee_rolemodule(self,request,arr,module):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		branch_ids = {"employee_arr": arr,"module":module}
		emp_data = json.dumps(branch_ids, indent=4)
		url=query_handler.fetch_employee_rolemodule()
		headers=token_handler.get_token(request)
		resp=api_calling.call_post(url,headers,emp_data)
		return resp

	# branch
	def fetch_branch_data(self,request,arr):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		branch_ids = {"arr": arr}
		emp_data = json.dumps(branch_ids, indent=4)
		url=query_handler.fetch_branch_data()
		headers=token_handler.get_token(request)
		resp=api_calling.call_post(url,headers,emp_data)
		return resp
	# ecf
	def get_emp_by_empid(self, request, emp_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.get_employeedtl(emp_id)
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		resp = json.loads(resp.text)
		return resp
	def get_empbranchid(self, request, empbranch_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.get_empbranch(empbranch_id)
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		resp = json.loads(resp.text)
		return resp
	def get_empbranchid_empid(self, request, emp_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.get_empbranch_empid(emp_id)
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		resp = json.loads(resp.text)
		return resp
	def get_cccode(self, request, cc_code):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.get_cc_one(cc_code)
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		resp = json.loads(resp.text)
		return resp
	def get_bscode(self, request, bs_code):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.get_bs_one(bs_code)
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		resp = json.loads(resp.text)
		return resp
	# ecf end

	# prpo
	def get_employee_data(self, request, employee_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		emp_ids = {"employee_id": employee_id}
		emp_data = json.dumps(emp_ids, indent=4)
		url = query_handler.post_employeedata1(emp_data)
		headers = token_handler.get_token(request)
		resp = api_calling.call_post(url, headers, emp_data)
		return resp
	def get_employee_data_apexpense(self, request, employee_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()

		url = query_handler.post_employeedata_accountdetails(employee_id)
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		return resp

	def get_empolyeebranch_data(self, request, employeebranch_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		empbranch_ids = {"employeebranch_id": employeebranch_id}
		empbranch_data = json.dumps(empbranch_ids, indent=4)
		url = query_handler.post_employeebranchdata(empbranch_data)
		headers = token_handler.get_token(request)
		resp = api_calling.call_post(url, headers, empbranch_data)
		return resp

	def search_employeename(self, request, emp_name):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.search_employeename(emp_name)
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		resp = json.loads(resp.text)
		return resp

	def fetch_employeedata(self, request, employee_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.fetch_employeedata(employee_id)
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		resp = json.loads(resp.text)
		return resp

	def fetch_employeebranchdata(self, request, employeebranch_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.fetch_employeebranchdata(employeebranch_id)
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		resp = json.loads(resp.text)
		return resp

	def fetch_ebranchaddressdata(self, request, employeebranch_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.fetch_ebranchaddressdata(employeebranch_id)
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		resp = json.loads(resp.text)
		return resp

	def employee_list(self, request):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.employee_list()
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		# resp = json.loads(resp.text)
		return resp

	def get_authtoken(self, request):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.get_authtoken()
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		resp = json.loads(resp.text)
		print(resp)
		return resp
	def empbranch_using_id(self,request,id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.empbranch_using_id(id)
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		resp = json.loads(resp.text)
		return resp
	def branch_using_user(self,request,id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.get_userbranch(id)
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		resp = json.loads(resp.text)
		return resp
	def empbranch_using_code(self,request,id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.empbranch_using_code(id)
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		resp = json.loads(resp.text)
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

	def fetch_multi_empolyee(self,request,empid_arr):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		emp_ids = {"arr": empid_arr}
		emp_data = json.dumps(emp_ids, indent=4)
		url=query_handler.get_multi_employee()
		headers=token_handler.get_token(request)
		resp=api_calling.call_post(url,headers,emp_data)
		return resp

	def get_employeename(self, request, name):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.get_employeename(name)
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		return resp

	def get_employeename_data(self, request, employee_id, query):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		emp_ids = {"employee_id": employee_id}
		emp_data = json.dumps(emp_ids, indent=4)
		url = query_handler.get_employeename_data(query)
		headers = token_handler.get_token(request)
		resp = api_calling.call_post(url, headers, emp_data)
		return resp

	def get_branch_ctrloffice(self,request):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.get_userbranchctrl()
		headers = token_handler.get_token(request)
		resp = api_calling.call_get(url, headers)
		resp = json.loads(resp.text)
		return resp