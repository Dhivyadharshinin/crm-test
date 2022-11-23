import json
import requests
from datetime import datetime, date


def vendorscheduler():
    from nwisefin.settings import logger
    from nwisefin.settings import APPLICATION_BE_URL
    now = date.today()
    ip_address = APPLICATION_BE_URL + '/usrserv/auth_token'
    username = 'apuser'
    password = '1234'
    datas = json.dumps({"username": username, "password": password, "entity_id": 1})
    resp = requests.post(ip_address, data=datas, verify=False)
    token_data = json.loads(resp.content.decode("utf-8"))
    vendor_json = {
        "report_id": [
            {
                "operators": "DATE BETWEEN",
                "value1date": str(now),
                "value2date": str(now),
                "module": "Vendor Statement",
                "scheduler": 1
            }
        ]
    }
    logger.info('EntryEOD TrailBalance API CALL ' + str(datetime.now()))
    report_url = APPLICATION_BE_URL + '/reportserv/vendorstatement_eod'
    headers = {"content-type": "application/json", "Authorization": "Token " + token_data["token"] + ""}
    jsonData = json.dumps(vendor_json)
    logger.info('VendorEOD Inserted API SUCCESS ' + str(datetime.now()))
    resp = requests.post("" + report_url, params='', data=jsonData,
                         headers=headers,
                         verify=False)
    logger.info('VendorEOD TrailBalance Response MESSAGE ' + str(token_data))
    logger.info('VendorEOD TrailBalance Inserted Succesfully ' + str(datetime.now()))
    return True
