import datetime
import boto3
from datetime import datetime
from nwisefin import settings
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinlist import NWisefinList
from wisefinapi.internal.queryhandler import QueryHandler
from wisefinapi.internal.tokenhandler import TokenHandler
from wisefinapi.internal.apicalling import APICall
import json
class DocAPI:
	def doc_upload(self,request,params):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		doc_data = {"params": params}
		resp_data = json.dumps(doc_data, indent=4)
		url=query_handler.doc_upload()
		headers=token_handler.get_headers(request)
		resp=api_calling.call_post(url,headers,resp_data)
		return resp

	def get_doc_filename(self,request,file_name):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		doc_data = {"params": file_name}
		resp_data = json.dumps(doc_data, indent=4)
		url = query_handler.doc_get_filename()
		headers = token_handler.get_headers(request)
		resp = api_calling.call_post(url, headers, resp_data)
		return resp

	def doc_module_ta(self, request, module,ta_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.doc_module_ta()
		headers = token_handler.get_token(request)
		params={"module":module,"ta_id":ta_id}
		resp = api_calling.call_get_params(url, headers,params)
		resp = json.loads(resp.text)
		return resp

	def document_uploadbucket_ta(self, request, params):
		if not request.FILES['file'] is None:
			try:
				file_count = len(request.FILES.getlist('file'))
				print(params)
				ref_id = params['id']
				prefix = params['prefix']
				rel_type = params['module']
				resp_list = NWisefinList()
				for i in range(0, file_count):
					file = request.FILES.getlist('file')[i]
					file_name = file.name
					file_size = file.size
					file_name_new = prefix + str(datetime.now().strftime("%y%m%d_%H%M%S")) + file_name
					contents = file
					s3 = boto3.resource('s3')
					s3_obj = s3.Object(bucket_name=settings.BUCKET_NAME_FOR_ASSETS, key=file_name_new)
					s3_obj.put(Body=contents)
					data ={"file_name": file.name,
						  "gen_file_name": file_name_new,
						  "rel_id": ref_id,
						  "rel_type": rel_type,
						  "prefix": prefix,
						  "size": file_size}
					resp_list.append(data)
					logger.info('uploaded file :' + str(file_name))
					print("uploaded file :", file_name)
				return resp_list
			except KeyError:
				logger.info('Kindly pass file information')



	def doc_upload_ta(self, request, params):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		subtax_ids = {"params": params}
		params = json.dumps(subtax_ids, indent=2)
		print('params', params)
		url = query_handler.doc_upload_ta()
		headers = token_handler.get_token(request)
		resp = api_calling.call_post(url, headers, params)
		return resp


	def upload_single_doc(self,request_file,params,request):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		url = query_handler.doc_upload_singlefilename()
		headers = token_handler.get_headers(request)
		resp = api_calling.call_post_multi_part(url, headers, params,request_file)
		return resp

	def doc_module(self, request, query):
		try:
			query_handler = QueryHandler()
			token_handler = TokenHandler()
			api_calling = APICall()
			url = query_handler.doc_module(query)
			headers = token_handler.get_token(request)
			resp = api_calling.call_get(url, headers)
			resp = json.loads(resp.text)
			print("resp", resp)
			return resp
		except:
			return False

	def doc_upload_ecf(self, request, params):
		try:
			query_handler = QueryHandler()
			token_handler = TokenHandler()
			api_calling = APICall()
			subtax_ids = {"params": params}
			params = json.dumps(subtax_ids, indent=2)
			print('params', params)
			url = query_handler.doc_upload_ecf()
			headers = token_handler.get_token(request)
			resp = api_calling.call_post(url, headers, params)
			return resp

		except:
			return False

	def document_uploadbucket_key(self, request, params, x):
		if not request.FILES[x] is None:
			try:
				file_count = len(request.FILES.getlist(x))
				print(params)
				ref_id = params['id']
				prefix = params['prefix']
				resp_list = NWisefinList()
				for i in range(0, file_count):
					file = request.FILES.getlist(x)[i]
					file_name = file.name
					file_size = file.size
					file_name_new = prefix + str(datetime.now().strftime("%y%m%d_%H%M%S")) + file_name
					contents = file
					s3 = boto3.resource('s3')
					s3_obj = s3.Object(bucket_name=settings.BUCKET_NAME_FOR_ASSETS, key=file_name_new)
					s3_obj.put(Body=contents)
					data ={"file_name": file.name,
						  "gen_file_name": file_name_new,
						  "rel_id": ref_id,
						  "prefix": prefix,
						  "size": file_size}
					resp_list.append(data)
					logger.info('uploaded file :' + str(file_name))
					print("uploaded file :", file_name)
				return resp_list
			except KeyError:
				resp_list = NWisefinList()
				data = {"file_name": False}
				resp_list.append(data)
				logger.info('Kindly pass file information')
