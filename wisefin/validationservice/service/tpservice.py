import base64
import json
from urllib import request

import requests
from django.contrib.auth import authenticate
from django.core import signing
from django.http import HttpResponse

from knox.models import AuthToken
from rest_framework import status
from nwisefin.settings import logger
# from userservice.controller.authcontroller import get_authtoken
from django.conf import settings
from django.contrib.auth.models import User
# from userservice.controller.employeecontroller import get_user_id
from userservice.data.authdata import AuthData
from userservice.data.errordata import ErrorData


class TPResponse:
    validation_status = None

    def __init__(self):
        validation_status = False

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_status(self, status):
        self.validation_status = status

    def get_status(self):
        return self.validation_status

class TPService:

    val_url = settings.CLIENT_URL
    val_tokenid=settings.ADURL_KEY
    val_tokenvalue=settings.CLIENT_SECRET
    def get_token(self):
        adurl = self.val_url + str("next/v1/oauth/cc/accesstoken")
        logger.info("token",adurl)
        ad_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        ad_request = {'grant_type': 'client_credentials'}
        req_obj = requests.post(adurl, data=ad_request, headers=ad_headers,
                                auth=(self.val_tokenid, self.val_tokenvalue), verify=False)
        resp_json = json.loads(req_obj.text)
        logger.info("tokenresponse")
        logger.info(req_obj)
        return resp_json['access_token']

    def get_pan_response(self, pan_number):
        pan_url = self.val_url + str("next/v1/mw/pan/") + pan_number
        logger.info(pan_url)
        token = self.get_token()
        authorization = 'Bearer ' + token
        headers = {'Authorization': authorization}
        req_obj = requests.get(pan_url, headers=headers,verify=False)
        resp_json = json.loads(req_obj.text)
        logger.info("pan",req_obj)
        return req_obj

    def get_gst_response(self, gst_number):
        # gst_url = 'https://kvb-test.apigee.net/next/v1/gst/searchtaxpayer?gstin=' + gst_number + '&action=TP'
        gst_url = self.val_url + str("next/v1/gst/searchtaxpayer?gstin=") + gst_number + '&action=TP'
        logger.info(gst_url)
        token = self.get_token()
        authorization = 'Bearer ' + token
        headers = {'Authorization': authorization}
        req_obj = requests.get(gst_url, headers=headers, verify=False)
        logger.info(req_obj)
        resp_json = json.loads(req_obj.text)
        return resp_json

    def perform_pan_validation(self, pan_number):
        # resp_json = self.get_pan_response(pan_number)
        # pan_resp = json.loads(resp_json.text)
        # logger.info(pan_resp)
        resp = TPResponse()
        resp.set_status("Success")
        # if 'errorCode' in pan_resp:
        #     logger.info('Error')
        #     resp.set_status(False)
        # else:
        #     logger.info('Success')
        #     resp.set_status(pan_resp)

        return resp


    def get_genotp_response(self, mobilenumber):
        # gst_url = 'https://kvb-test.apigee.net/next/v1/gst/searchtaxpayer?gstin=' + gst_number + '&action=TP'
        gst_url = self.val_url + str("next/v1/mw/generateotp")
        logger.info(gst_url)
        print(gst_url)
        token = self.get_token()
        authorization = 'Bearer ' + token
        # headers = {'Authorization': authorization}
        headers = {"content-type": "application/json", "Authorization": "" + authorization + ""}
        datas=json.dumps({"mobileNumber":mobilenumber},indent=4)
        req_obj = requests.post(gst_url, data=datas, headers=headers, verify=False)
        logger.info(req_obj)

        if req_obj.status_code in (500,502):
            resp_json = {'Status': 'Failure',
                        'ErrorMessage': 'KVB OTP-GEN API FAILED TRY AGAIN', 'ErrorCode': '12'}
        else:
            resp_json = json.loads(req_obj.content)
        return resp_json

    def get_otpvaliation_response(self, mobilenumber,otp):

        gst_url = self.val_url + str("next/v1/mw/validateotp")
        logger.info(gst_url)
        token = self.get_token()
        authorization = 'Bearer ' + token
        # headers = {'Authorization': authorization}
        headers = {"content-type": "application/json", "Authorization": "" + authorization + ""}
        data=json.dumps({"mobileNumber":mobilenumber,"otp":otp})
        req_obj = requests.post(gst_url, headers=headers,data=data, verify=False)
        logger.info(req_obj)
        resp_json = json.loads(req_obj.content)
        return resp_json

    def perform_gst_validation(self, gst_number):
        # gst_resp = self.get_gst_response(gst_number)
        # logger.info(gst_resp)
        resp = TPResponse()
        resp.set_status('Success')
        # if 'errorCode' in gst_resp:
        #     logger.info('Error')
        #     resp.set_status(False)
        # else:
        #     logger.info('Success')
        #     resp.set_status(gst_resp)

        return resp.get()

    def get_ifsc_response(self, ifsc_code):
        # gst_url = 'https://kvb-test.apigee.net/next/v1/gst/searchtaxpayer?gstin=' + gst_number + '&action=TP'
        ifsc_url = self.val_url + str("next/v1/mw/ifsc-check")
        logger.info("ifsc",ifsc_url)
        datas = json.dumps({"IFSC_Code": ifsc_code})
        logger.info(datas)
        token = self.get_token()
        logger.info(token)
        authorization = 'Bearer ' + token
        headers = {"content-type": "application/json", 'Authorization': authorization}
        req_obj = requests.post(ifsc_url, data=datas, headers=headers, verify=False)
        a = json.loads(req_obj.text)
        # result=req_obj.content.decode("utf-8")
        # return req_obj.text
        # resp_json = json.loads(req_obj.text)
        return a
    def perform_ifsc_validation(self, ifsc_code):
        # gst_resp = self.get_ifsc_response(ifsc_code)
        # logger.info(gst_resp)
        resp = TPResponse()
        resp.set_status('Success')
        # if 'errorCode' in gst_resp:
        #     logger.info('Error')
        #     resp.set_status(False)
        # else:
        #     logger.info('Success')
        #     resp.set_status(gst_resp)
        return resp.get()