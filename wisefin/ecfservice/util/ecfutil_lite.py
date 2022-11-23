
import base64
import json
import requests
from nwisefin.settings import SERVER_IP
import json


#test
def get_authtoken_ecf():
    ip_address=SERVER_IP+'/usrserv/auth_token'
    username = 'EMP001'
    password = '1234'
    entity_id = 1
    # password = base64.b64encode(password)
    # password=password.decode("utf-8")
    datas = json.dumps({"username": username, "password": password,"entity_id":entity_id})
    resp = requests.post(ip_address,  data=datas,verify=False)
    token_data = json.loads(resp.content.decode("utf-8"))
    ### Validations
    if resp.status_code == 200:
        return token_data["token"]
        # response = HttpResponse(token_data["token"], content_type="application/json")
        # return response
    # else:
    #     response = HttpResponse('token_data["token"]', content_type="application/json")
    #     return response