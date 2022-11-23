import requests
import json
class APICall:

    def call_get(self,url,headers):
        resp = requests.get(url,headers=headers,verify=False)
        return resp

    def call_post(self,url,headers,data):
        resp = requests.post(url, headers=headers,data=data, verify=False)
        datalist=json.loads(resp.content)
        return datalist

    def call_post_multi_part(self,url,headers,data,files):
     return

    def call_get_params(self,url,headers,data):
     resp = requests.get(url,headers=headers,verify=False, params=data)
     return resp
