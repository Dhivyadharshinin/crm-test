from validationservice.service.tpservice import TPService
from validationservice.service.tpservice import TPResponse
import json
from nwisefin.settings import logger
from django.db.models import Q

import requests

from vendorservice.service.vendorservice import VendorService


class VendorValidation:
    def pan_validation(self,pan_number):
        tpserv = TPService()
        val=tpserv.perform_pan_validation(pan_number)
        print(val.get())
        return val.get()

    def gst_validation(self,gst_number):
        tpserv = TPService()
        return tpserv.perform_gst_validation(gst_number)

    # commented for purpose

    # def gen_validation(self,mobilenumber,employee_id):
    #     tpserv = TPService()
    #     rep=tpserv.perform_otp_gen(mobilenumber,employee_id)
    #     return rep.get()
    # def otp_validation(self,mobilenumber,otp,employee_id,request):
    #     tpserv = TPService()
    #     rep = tpserv.perform_otp_validation(mobilenumber,otp,employee_id,request)
    #     return rep.get()

    def ifsc_validation(self,ifsc_code):
        tpserv = TPService()
        return tpserv.perform_ifsc_validation(ifsc_code)


    def vendorcontract_validation(self,contratobj):
        # try:
            resp=TPResponse()
            a=contratobj.get_name()
            b=contratobj.get_service()
            if a!='' and b!='':
                resp.set_status(True)
                return resp.get()
            else:
                resp.set_status(False)
                return resp.get()

        # except:
        #     resp.set_status(False)
        #     return resp.get()

    def vendor_name_validation(self, value, request):
        scope = request.scope
        vendor_service = VendorService(scope)
        return vendor_service.vendor_name_validation(value)
