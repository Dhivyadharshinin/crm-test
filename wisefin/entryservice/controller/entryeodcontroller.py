import json

import requests

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, date
from django import db


def scheduler():
    from nwisefin.settings import logger
    from nwisefin.settings import APPLICATION_BE_URL
    now = date.today()
    ip_address = APPLICATION_BE_URL + '/usrserv/auth_token'
    username = 'apuser'
    password = '1234'
    # password = base64.b64encode(password)
    # password = password.decode("utf-8")
    datas = json.dumps({"username": username, "password": password, "entity_id": 1})
    resp = requests.post(ip_address, data=datas, verify=False)
    token_data = json.loads(resp.content.decode("utf-8"))
    trail_balance_json = {
        "report_id": [
            {
                "operators": "DATE BETWEEN",
                "value1date": str(now),
                "value2date": str(now),
                "module": "TRIAL BALANCE",
                "scheduler":1
            }
        ]
    }
    logger.info('EntryEOD TrailBalance API CALL ' + str(datetime.now()))
    report_url = APPLICATION_BE_URL + '/reportserv/reportdownload'
    headers = {"content-type": "application/json", "Authorization": "Token " + token_data["token"] + ""}
    # ip = common.clientapi()
    jsonData = json.dumps(trail_balance_json)
    logger.info('EntryEOD TrailBalance Inserted API SUCCESS ' + str(datetime.now()))
    resp = requests.post("" + report_url, params='', data=jsonData,
                         headers=headers,
                         verify=False)
    # token_data = json.loads(resp.content.decode("utf-8"))
    logger.info('EntryEOD TrailBalance Response MESSAGE ' + str(token_data))
    logger.info('EntryEOD TrailBalance Inserted Succesfully ' + str(datetime.now()))
    return True

#
# def sched1(request):
#     # scope = json.loads(resp.request.scope)['entity_id']
#     scope = request.scope
#     from entryservice.service.entryeodservice import EntrySchedulerService
#     schedule = EntrySchedulerService(scope)
#     try:
#         print('scheduler starts')
#         d = schedule.entryeod()
#         print(d)
#     except:
#         print('scheduler fail')
#     finally:
#         print('scheduler success')
#         db.connections['scheduler'].close()
#     return

# @csrf_exempt
# @api_view(['GET', 'POST'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def entryeod(request):
#     if request.method == 'POST':
#         scope = request.scope
#         entry_service = EntryService(scope)
#         entrydetails_obj = json.loads(request.body)
#         vysfinservice = ApiService(scope)
#         emp_id = request.employee_id
#         resp_obj = entry_service.create_entrydetails(request,emp_id,entrydetails_obj)
#         response = HttpResponse(resp_obj.get(), content_type="application/json")
#         return response
#
#     elif request.method == 'GET':
#         return fetch_entry_list(request)