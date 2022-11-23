from wisefinapi.internal.queryhandler import QueryHandler
from wisefinapi.internal.tokenhandler import TokenHandler
from wisefinapi.internal.apicalling import APICall

import json
class PdAPI:
	def get_Premisedetails(self,request,premise_id):
		query_handler = QueryHandler()
		token_handler = TokenHandler()
		api_calling = APICall()
		premise_ids = {"arr": premise_id}
		data = json.dumps(premise_ids, indent=4)
		url=query_handler.fetch_premise_data()
		headers=token_handler.get_token(request)
		resp=api_calling.call_post(url,headers,data)
		return resp