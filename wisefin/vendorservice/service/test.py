import json

import requests

from nwisefin.settings import logger


class TestV1:
    def get_info(self,user_list):
        json_data = json.dumps(user_list)
        user_resp = requests.post('http://127.0.0.1:8000/usrserv/employee', data=json_data)
        user_data = json.loads(user_resp.text)
        return user_data


user_li = [1,5,6,7,8,9]
v1 = TestV1()
ud = v1.get_info(user_li)
logger.info(str(ud))
