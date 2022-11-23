import json

import numpy as np
import pandas as pd
import requests
from django.db.models import Count, F, Q, Sum
from django.http import HttpResponse
from masterservice.models import APsubcategory, APexpensegroup
from pprservice.data.request.nac_income_request import ppr_clientrequest
# from pprservice.data.response.nac_income_respone import Income_details_month
from pprservice.data.response.success import successMessage
from userservice.controller.authcontroller import get_authtoken
from nwisefin import settings
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessMessage, SuccessStatus
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from pprservice.models.pprmodel import active_clients, clients_details_months, Income_header, Income_details_month, \
    Income_details_date, clients_details_date, GL_Subgroup, Income_overalldata, \
    Sub_Groups, Head_Groups, Ppr_Sources
from pprservice.util.pprutility import Fees_type, Client_flag, Activestatus, Asset_class, MASTER_SERVICE,USER_SERVICE
from pprservice.data.response.nac_income_respone import ppr_clientresponse, \
    Income_details_response as Income_details_response, ppr_source_response
from datetime import datetime
class Income_Service(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.PPR_SERVICE)

    def fetch_asset_search_list(self):
        filter_val = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,13,14,15,16,17,18]
        pro_list = NWisefinList()
        for i in filter_val:
            filter_response = ppr_clientresponse()
            filter_response.set_asset_dtls(int(i))
            pro_list.append(filter_response)
        return pro_list

    def fileupload_acti_clients(self,transac_obj,employee_id):
        from datetime import datetime
        for data in transac_obj:
            # print(data)
            masterservice = MASTER_SERVICE(self._scope())
            asset_dtls = masterservice.get_BS([data["Asset class"]])
            asset_id = asset_dtls[0]["id"]
            mst_dtls = masterservice.get_mstsegment([data["Business Type"]])
            biz_id = mst_dtls[0]["id"]
            obj=active_clients.objects.using(self._current_app_schema()).filter(client_id=data["client name"],product_id=biz_id,asset_id=asset_id,entity_id=self._entity_id())
            if len(obj)==0:
                create_clients=active_clients.objects.using(self._current_app_schema()).create(client_id=data["client name"],product_id=biz_id,status=1,created_by=employee_id,created_date=datetime.now(),asset_id=asset_id,entity_id=self._entity_id())
                create_months=clients_details_months.objects.using(self._current_app_schema()).create(activeclient_id=create_clients.id,bop=data["BOP"],new_client=data["New"],attrition=data["Attrition"],closing=data["Closing"],created_by=employee_id,created_date=datetime.now(),month=1,entity_id=self._entity_id())
                len_gth=len(obj)
                act_cli=create_clients.id
                self.active_clients_date(len_gth,data,employee_id,act_cli)
            else:
                update_client=active_clients.objects.using(self._current_app_schema()).filter(id=obj[0].id).update(client_id=data["client name"],product_id=biz_id,status=1,updated_by=employee_id,updated_date=datetime.now(),asset_id=asset_id,entity_id=self._entity_id())
                cal=clients_details_months.objects.using(self._current_app_schema()).get(activeclient_id=obj[0].id,month=1)
                new_client=cal.new_client+data["New"]
                bop=cal.bop+data["BOP"]
                attrition=cal.attrition+data["Attrition"]
                closing_new=(new_client+bop)-attrition
                len_gth = len(obj)
                act_cli = obj[0].id
                self.active_clients_date(len_gth, data, employee_id, act_cli)

                update_mon=clients_details_months.objects.using(self._current_app_schema()).filter(activeclient_id=obj[0].id,month=1).update(bop=F('bop') + data["BOP"],new_client=new_client,attrition=attrition,closing=closing_new,updated_by=employee_id,updated_date=datetime.now(),entity_id=self._entity_id())
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def fileupload_cc_income(self,transac_obj,employee_id):
        try:
            arr=[]
            for data in transac_obj:
                masterservice = MASTER_SERVICE(self._scope())
                user_service = USER_SERVICE(self._scope())
                branch_dtls = user_service.get_branch_id([int(data["Branch code"])])
                if len(branch_dtls) == 0:
                    branch_id = int(data["Branch code"])
                else:
                    branch_id = branch_dtls[0]["id"]
                biz_dtls = masterservice.get_mstsegment([data["Business type"]])
                if len(biz_dtls) == 0:
                    biz_id = int(data["Business id"])
                else:
                    biz_id = biz_dtls[0]["id"]
                asset_dtls = masterservice.get_BS([data["Asset class"]])
                if len(asset_dtls) == 0:
                    asset_id = int(data["asset class"])
                else:
                    asset_id = asset_dtls[0]["id"]
                over_data = Income_overalldata(branch_id=branch_id, business_id=biz_id,
                                               assest_class=asset_id, client_id=data["Client id"],
                                               product_id=1, sanctioned_amount=100,
                                               sanctioned_date="2022-01-01",
                                               disbursed_amount=100,
                                               total_disbural=data["Total disbursal"], fee_type=data["Fee type"],
                                               beginning_fee_due=data["Total fee due beginning"],
                                               fee_due=data["fee due"], collected_fee=data["Total fee collected"],
                                               interest_amount=data["Int Amount"], eir_amount=data["EIR"],interest_gl=data["Interest"],
                                               opening_pos=data["Opening POS"], closing_pos=data["Closing POS"],status=1,created_by=employee_id,
                                                                                          created_date=datetime.now(),updated_date='2022-01-05')
                arr.append(over_data)
            Income_overalldata.objects.using(self._current_app_schema()).bulk_create(arr)

            for data in transac_obj:
                arr = []
                masterservice = MASTER_SERVICE(self._scope())
                user_service = USER_SERVICE(self._scope())
                branch_dtls = user_service.get_branch_id([int(data["Branch code"])])
                if len(branch_dtls) == 0:
                    branch_id = int(data["Branch code"])
                else:
                    branch_id = branch_dtls[0]["id"]
                biz_dtls = masterservice.get_mstsegment([data["Business type"]])
                if len(biz_dtls) == 0:
                    biz_id = int(data["Business id"])
                else:
                    biz_id = biz_dtls[0]["id"]
                asset_dtls = masterservice.get_BS([data["Asset class"]])
                if len(asset_dtls) == 0:
                    asset_id = int(data["asset class"])
                else:
                    asset_id = asset_dtls[0]["id"]
                condition = Q(branch_id=branch_id, business_id=None, assest_class=None, client_id=None,
                              product_id=None, flag=data["Flag"], fee_type=data["Fee type"]) | Q(
                    branch_id=branch_id, business_id=biz_id, assest_class=None, client_id=None,
                    product_id=None, flag=data["Flag"], fee_type=data["Fee type"]) | Q(branch_id=branch_id,
                                                                                       business_id=biz_id,
                                                                                       assest_class=asset_id,
                                                                                       client_id=None, product_id=None,
                                                                                       flag=data["Flag"],
                                                                                       fee_type=data["Fee type"]) | Q(
                    branch_id=branch_id, business_id=biz_id, assest_class=asset_id,
                    client_id=data["Client id"], product_id=None, flag=data["Flag"], fee_type=data["Fee type"]) | Q(
                    branch_id=branch_id, business_id=biz_id, assest_class=asset_id,
                    client_id=data["Client id"], product_id=1, flag=data["Flag"],
                    fee_type=data["Fee type"])
                income_header = Income_header.objects.using(self._current_app_schema()).filter(condition)
                len_gth=len(income_header)
                if len(income_header) == 0:

                    inc1 = Income_header.objects.using(self._current_app_schema()).create(branch_id=branch_id,
                                                                                          business_id=None,
                                                                                          assest_class=None,
                                                                                          client_id=None,
                                                                                          product_id=None,
                                                                                          created_by=employee_id,
                                                                                          created_date=datetime.now(),
                                                                                          entity_id=self._entity_id(),
                                                                                          flag=data["Flag"],
                                                                                          fee_type=data["Fee type"],
                                                                                          status=1)
                    income_header_id1=inc1.id
                    self.income_date_upload(0, data, employee_id,income_header_id1)
                    inc2 = Income_header.objects.using(self._current_app_schema()).create(branch_id=branch_id,
                                                                                          business_id=biz_id,
                                                                                          assest_class=None,
                                                                                          client_id=None,
                                                                                          product_id=None,
                                                                                          created_by=employee_id,
                                                                                          created_date=datetime.now(),
                                                                                          entity_id=self._entity_id(),
                                                                                          flag=data["Flag"],
                                                                                          fee_type=data["Fee type"],
                                                                                          status=1)
                    income_header_id2 = inc2.id
                    self.income_date_upload(0, data, employee_id, income_header_id2)
                    inc3 = Income_header.objects.using(self._current_app_schema()).create(branch_id=branch_id,
                                                                                          business_id=biz_id,
                                                                                          assest_class=asset_id,
                                                                                          client_id=None,
                                                                                          product_id=None,
                                                                                          created_by=employee_id,
                                                                                          created_date=datetime.now(),
                                                                                          entity_id=self._entity_id(),
                                                                                          flag=data["Flag"],
                                                                                          fee_type=data["Fee type"],
                                                                                          status=1)
                    income_header_id3 = inc3.id
                    self.income_date_upload(0, data, employee_id, income_header_id3)
                    inc4 = Income_header.objects.using(self._current_app_schema()).create(branch_id=branch_id,
                                                                                          business_id=biz_id,
                                                                                          assest_class=asset_id,
                                                                                          client_id=data["Client id"],
                                                                                          product_id=None,
                                                                                          created_by=employee_id,
                                                                                          created_date=datetime.now(),
                                                                                          entity_id=self._entity_id(),
                                                                                          flag=data["Flag"],
                                                                                          fee_type=data["Fee type"],
                                                                                          status=1)
                    income_header_id4 = inc4.id
                    self.income_date_upload(0, data, employee_id, income_header_id4)
                    inc5 = Income_header.objects.using(self._current_app_schema()).create(branch_id=branch_id,
                                                                                          business_id=biz_id,
                                                                                          assest_class=asset_id,
                                                                                          client_id=data["Client id"],
                                                                                          product_id=1,
                                                                                          created_by=employee_id,
                                                                                          created_date=datetime.now(),
                                                                                          entity_id=self._entity_id(),
                                                                                          flag=data["Flag"],
                                                                                          fee_type=data["Fee type"],
                                                                                          status=1)
                    income_header_id5 = inc5.id
                    self.income_date_upload(0, data, employee_id, income_header_id5)
                    inc_mon1 = Income_details_month.objects.using(self._current_app_schema()).create(
                        activeclient_id=inc1.id, month=1, disbursal_amount=data["Disbursed amount"],
                        total_disbursalamount=data["Total disbursal"],
                        beginning_fee_due=data["Total fee due beginning"],
                        interest_amount=data["Int Amount"], eir_amount=data["EIR"],
                        created_by=employee_id, created_date=datetime.now(), entity_id=self._entity_id(),
                        flag=data["Flag"], sanctioned_amount=0,
                        sanctioned_date=data["Sanctioned Date"], opening_pos=data["Opening POS"],
                        closing_pos=data["Closing POS"],fee_due=data["fee due"],collected_fee=data["Total fee collected"],interest_gl=data["Interest"])
                    inc_mon2 = Income_details_month.objects.using(self._current_app_schema()).create(
                        activeclient_id=inc2.id, month=1, disbursal_amount=data["Disbursed amount"],
                        total_disbursalamount=data["Total disbursal"],
                        beginning_fee_due=data["Total fee due beginning"],
                        interest_amount=data["Int Amount"], eir_amount=data["EIR"],
                        created_by=employee_id, created_date=datetime.now(), entity_id=self._entity_id(),
                        flag=data["Flag"], sanctioned_amount=0,
                        sanctioned_date=data["Sanctioned Date"], opening_pos=data["Opening POS"],
                        closing_pos=data["Closing POS"],fee_due=data["fee due"],collected_fee=data["Total fee collected"],interest_gl=data["Interest"])
                    inc_mon3 = Income_details_month.objects.using(self._current_app_schema()).create(
                        activeclient_id=inc3.id, month=1, disbursal_amount=data["Disbursed amount"],
                        total_disbursalamount=data["Total disbursal"],
                        beginning_fee_due=data["Total fee due beginning"],
                        interest_amount=data["Int Amount"], eir_amount=data["EIR"],
                        created_by=employee_id, created_date=datetime.now(), entity_id=self._entity_id(),
                        flag=data["Flag"], sanctioned_amount=0,
                        sanctioned_date=data["Sanctioned Date"], opening_pos=data["Opening POS"],
                        closing_pos=data["Closing POS"],fee_due=data["fee due"],collected_fee=data["Total fee collected"],interest_gl=data["Interest"])
                    inc_mon4 = Income_details_month.objects.using(self._current_app_schema()).create(
                        activeclient_id=inc4.id, month=1, disbursal_amount=data["Disbursed amount"],
                        total_disbursalamount=data["Total disbursal"],
                        beginning_fee_due=data["Total fee due beginning"],
                        interest_amount=data["Int Amount"], eir_amount=data["EIR"],
                        created_by=employee_id, created_date=datetime.now(), entity_id=self._entity_id(),
                        flag=data["Flag"], sanctioned_amount=0,
                        sanctioned_date=data["Sanctioned Date"], opening_pos=data["Opening POS"],
                        closing_pos=data["Closing POS"],fee_due=data["fee due"],collected_fee=data["Total fee collected"],interest_gl=data["Interest"])
                    inc_mon5 = Income_details_month.objects.using(self._current_app_schema()).create(
                        activeclient_id=inc5.id, month=1, disbursal_amount=data["Disbursed amount"],
                        total_disbursalamount=data["Total disbursal"],
                        beginning_fee_due=data["Total fee due beginning"],
                        interest_amount=data["Int Amount"], eir_amount=data["EIR"],
                        created_by=employee_id, created_date=datetime.now(), entity_id=self._entity_id(),
                        flag=data["Flag"], sanctioned_amount=0,
                        sanctioned_date=data["Sanctioned Date"], opening_pos=data["Opening POS"],
                        closing_pos=data["Closing POS"],fee_due=data["fee due"],collected_fee=data["Total fee collected"],interest_gl=data["Interest"])

                else:
                    if len(income_header) == 1:
                        arr = []
                        for i in income_header:
                            arr.append(i.id)
                        # income_header_id5 = inc5.id
                        self.income_date_upload(len_gth, data, employee_id, arr)
                        inc_mon1 = Income_details_month.objects.using(self._current_app_schema()).filter(
                            activeclient_id__in=arr).update(
                            month=1, disbursal_amount=F('disbursal_amount') + data["Disbursed amount"],
                            total_disbursalamount=F('total_disbursalamount') + data["Total disbursal"],
                            beginning_fee_due=F('beginning_fee_due') + data["Total fee due beginning"],

                            interest_amount=F('interest_amount') + data["Int Amount"],
                            eir_amount=F('eir_amount') + data["EIR"], created_by=employee_id,
                            created_date=datetime.now(), entity_id=self._entity_id(),
                            sanctioned_amount=F('sanctioned_amount') + 0,
                            opening_pos=F('opening_pos') + data["Opening POS"],
                            closing_pos=F('closing_pos') + data["Closing POS"],fee_due=F('fee_due') +data["fee due"],collected_fee=F('collected_fee') +data["Total fee collected"])

                        inc2 = Income_header.objects.using(self._current_app_schema()).create(
                            branch_id=branch_id,
                            business_id=biz_id,
                            assest_class=None,
                            client_id=None,
                            product_id=None,
                            created_by=employee_id,
                            created_date=datetime.now(),
                            entity_id=self._entity_id(),
                            flag=data["Flag"],
                            fee_type=data["Fee type"],
                            status=1)
                        income_header_id2 = inc2.id
                        # len_gth=0
                        self.income_date_upload(0, data, employee_id, income_header_id2)
                        inc3 = Income_header.objects.using(self._current_app_schema()).create(
                            branch_id=branch_id,
                            business_id=biz_id,
                            assest_class=asset_id,
                            client_id=None,
                            product_id=None,
                            created_by=employee_id,
                            created_date=datetime.now(),
                            entity_id=self._entity_id(),
                            flag=data["Flag"],
                            fee_type=data["Fee type"],
                            status=1)
                        income_header_id3 = inc3.id
                        # len_gth=0
                        self.income_date_upload(0, data, employee_id, income_header_id3)
                        inc4 = Income_header.objects.using(self._current_app_schema()).create(
                            branch_id=branch_id,
                            business_id=biz_id,
                            assest_class=asset_id,
                            client_id=data["Client id"],
                            product_id=None,
                            created_by=employee_id,
                            created_date=datetime.now(),
                            entity_id=self._entity_id(),
                            flag=data["Flag"],
                            fee_type=data["Fee type"],
                            status=1)
                        income_header_id4 = inc4.id
                        # len_gth = 0
                        self.income_date_upload(0, data, employee_id, income_header_id4)
                        inc5 = Income_header.objects.using(self._current_app_schema()).create(
                            branch_id=branch_id,
                            business_id=biz_id,
                            assest_class=asset_id,
                            client_id=data["Client id"],
                            product_id=1,
                            created_by=employee_id,
                            created_date=datetime.now(),
                            entity_id=self._entity_id(),
                            flag=data["Flag"],
                            fee_type=data["Fee type"],
                            status=1)
                        income_header_id5 = inc5.id
                        # len_gth = 0
                        self.income_date_upload(0, data, employee_id, income_header_id5)
                        inc_mon2 = Income_details_month.objects.using(self._current_app_schema()).create(
                            activeclient_id=inc2.id, month=1, disbursal_amount=data["Disbursed amount"],
                            total_disbursalamount=data["Total disbursal"],
                            beginning_fee_due=data["Total fee due beginning"],
                            interest_gl = data["Interest"],
                            interest_amount=data["Int Amount"],
                            eir_amount=data["EIR"], created_by=employee_id,
                            created_date=datetime.now(), entity_id=self._entity_id(),
                            sanctioned_amount=0, sanctioned_date=data["Sanctioned Date"],
                            opening_pos=data["Opening POS"], closing_pos=data["Closing POS"],fee_due=data["fee due"],collected_fee=data["Total fee collected"])
                        inc_mon3 = Income_details_month.objects.using(self._current_app_schema()).create(
                            activeclient_id=inc3.id, month=1, disbursal_amount=data["Disbursed amount"],
                            total_disbursalamount=data["Total disbursal"],
                            beginning_fee_due=data["Total fee due beginning"],
                            interest_gl = data["Interest"],
                            interest_amount=data["Int Amount"],
                            eir_amount=data["EIR"], created_by=employee_id,
                            created_date=datetime.now(), entity_id=self._entity_id(),
                            sanctioned_amount=0, sanctioned_date=data["Sanctioned Date"],
                            opening_pos=data["Opening POS"], closing_pos=data["Closing POS"],fee_due=data["fee due"],collected_fee=data["Total fee collected"])
                        inc_mon4 = Income_details_month.objects.using(self._current_app_schema()).create(
                            activeclient_id=inc4.id, month=1, disbursal_amount=data["Disbursed amount"],
                            total_disbursalamount=data["Total disbursal"],
                            beginning_fee_due=data["Total fee due beginning"],
                            interest_gl = data["Interest"],
                            interest_amount=data["Int Amount"],
                            eir_amount=data["EIR"], created_by=employee_id,
                            created_date=datetime.now(), entity_id=self._entity_id(),
                            sanctioned_amount=0, sanctioned_date=data["Sanctioned Date"],
                            opening_pos=data["Opening POS"], closing_pos=data["Closing POS"],fee_due=data["fee due"],collected_fee=data["Total fee collected"])
                        inc_mon5 = Income_details_month.objects.using(self._current_app_schema()).create(
                            activeclient_id=inc5.id, month=1, disbursal_amount=data["Disbursed amount"],
                            total_disbursalamount=data["Total disbursal"],
                            beginning_fee_due=data["Total fee due beginning"],
                            interest_gl = data["Interest"],
                            interest_amount=data["Int Amount"],
                            eir_amount=data["EIR"], created_by=employee_id,
                            created_date=datetime.now(), entity_id=self._entity_id(),
                            sanctioned_amount=0, sanctioned_date=data["Sanctioned Date"],
                            opening_pos=data["Opening POS"], closing_pos=data["Closing POS"],fee_due=data["fee due"],collected_fee=data["Total fee collected"])

                    elif len(income_header) == 2:
                        for i in income_header:
                            arr.append(i.id)
                        self.income_date_upload(len_gth, data, employee_id, arr)
                        inc_mon1 = Income_details_month.objects.using(self._current_app_schema()).filter(
                            activeclient_id__in=arr).update(
                            month=1, disbursal_amount=F('disbursal_amount') + data["Disbursed amount"],
                            total_disbursalamount=F('total_disbursalamount') + data["Total disbursal"],
                            beginning_fee_due=F('beginning_fee_due') + data["Total fee due beginning"],
                            interest_gl = data["Interest"],
                            interest_amount=F('interest_amount') + data["Int Amount"],
                            eir_amount=F('eir_amount') + data["EIR"], created_by=employee_id,
                            created_date=datetime.now(), entity_id=self._entity_id(),
                            sanctioned_amount=F('sanctioned_amount') + 0,
                            opening_pos=F('opening_pos') + data["Opening POS"],
                            closing_pos=F('closing_pos') + data["Closing POS"],fee_due=F('fee_due') +data["fee due"],collected_fee=F('collected_fee') +data["Total fee collected"])
                        inc3 = Income_header.objects.using(self._current_app_schema()).create(
                            branch_id=branch_id,
                            business_id=biz_id,
                            assest_class=asset_id,
                            client_id=None,
                            product_id=None,
                            created_by=employee_id,
                            created_date=datetime.now(),
                            entity_id=self._entity_id(),
                            flag=data["Flag"],
                            fee_type=data["Fee type"],
                            status=1)
                        income_header_id3 = inc3.id
                        # len_gth = 0
                        self.income_date_upload(0, data, employee_id, income_header_id3)
                        inc4 = Income_header.objects.using(self._current_app_schema()).create(
                            branch_id=branch_id,
                            business_id=biz_id,
                            assest_class=asset_id,
                            client_id=data["Client id"],
                            product_id=None,
                            created_by=employee_id,
                            created_date=datetime.now(),
                            entity_id=self._entity_id(),
                            flag=data["Flag"],
                            fee_type=data["Fee type"],
                            status=1)
                        income_header_id4 = inc4.id
                        # len_gth = 0
                        self.income_date_upload(0, data, employee_id, income_header_id4)
                        inc5 = Income_header.objects.using(self._current_app_schema()).create(
                            branch_id=branch_id,
                            business_id=biz_id,
                            assest_class=asset_id,
                            client_id=data["Client id"],
                            product_id=1,
                            created_by=employee_id,
                            created_date=datetime.now(),
                            entity_id=self._entity_id(),
                            flag=data["Flag"],
                            fee_type=data["Fee type"],
                            status=1)
                        income_header_id5 = inc5.id
                        # len_gth = 0
                        self.income_date_upload(0, data, employee_id, income_header_id5)
                        inc_mon3 = Income_details_month.objects.using(self._current_app_schema()).create(
                            activeclient_id=inc3.id, month=1, disbursal_amount=data["Disbursed amount"],
                            total_disbursalamount=data["Total disbursal"],
                            beginning_fee_due=data["Total fee due beginning"],
                            interest_gl = data["Interest"],
                            interest_amount=data["Int Amount"],
                            eir_amount=data["EIR"], created_by=employee_id,
                            created_date=datetime.now(), entity_id=self._entity_id(),
                            sanctioned_amount=0, sanctioned_date=data["Sanctioned Date"],
                            opening_pos=data["Opening POS"], closing_pos=data["Closing POS"],fee_due=data["fee due"],collected_fee=data["Total fee collected"])
                        inc_mon4 = Income_details_month.objects.using(self._current_app_schema()).create(
                            activeclient_id=inc4.id, month=1, disbursal_amount=data["Disbursed amount"],
                            total_disbursalamount=data["Total disbursal"],
                            beginning_fee_due=data["Total fee due beginning"],
                            interest_gl = data["Interest"],
                            interest_amount=data["Int Amount"],
                            eir_amount=data["EIR"], created_by=employee_id,
                            created_date=datetime.now(), entity_id=self._entity_id(),
                            sanctioned_amount=0, sanctioned_date=data["Sanctioned Date"],
                            opening_pos=data["Opening POS"], closing_pos=data["Closing POS"],fee_due=data["fee due"],collected_fee=data["Total fee collected"])
                        inc_mon5 = Income_details_month.objects.using(self._current_app_schema()).create(
                            activeclient_id=inc5.id, month=1, disbursal_amount=data["Disbursed amount"],
                            total_disbursalamount=data["Total disbursal"],
                            beginning_fee_due=data["Total fee due beginning"],
                            interest_gl = data["Interest"],
                            interest_amount=data["Int Amount"],
                            eir_amount=data["EIR"], created_by=employee_id,
                            created_date=datetime.now(), entity_id=self._entity_id(),
                            sanctioned_amount=0, sanctioned_date=data["Sanctioned Date"],
                            opening_pos=data["Opening POS"], closing_pos=data["Closing POS"],fee_due=data["fee due"],collected_fee=data["Total fee collected"])

                    elif len(income_header) == 3:
                        for i in income_header:
                            arr.append(i.id)
                        # income_header_id3 = inc3.id
                        # len_gth = 0
                        self.income_date_upload(len_gth, data, employee_id, arr)
                        inc_mon1 = Income_details_month.objects.using(self._current_app_schema()).filter(
                            activeclient_id__in=arr).update(
                            month=1, disbursal_amount=F('disbursal_amount') + data["Disbursed amount"],
                            total_disbursalamount=F('total_disbursalamount') + data["Total disbursal"],
                            beginning_fee_due=F('beginning_fee_due') + data["Total fee due beginning"],
                            interest_gl = data["Interest"],
                            interest_amount=F('interest_amount') + data["Int Amount"],
                            eir_amount=F('eir_amount') + data["EIR"], created_by=employee_id,
                            created_date=datetime.now(), entity_id=self._entity_id(),
                            sanctioned_amount=F('sanctioned_amount') + 0,
                            opening_pos=F('opening_pos') + data["Opening POS"],
                            closing_pos=F('closing_pos') + data["Closing POS"],fee_due=F('fee_due') +data["fee due"],collected_fee=F('collected_fee') +data["Total fee collected"])
                        inc4 = Income_header.objects.using(self._current_app_schema()).create(
                            branch_id=branch_id,
                            business_id=biz_id,
                            assest_class=asset_id,
                            client_id=data["Client id"],
                            product_id=None,
                            created_by=employee_id,
                            created_date=datetime.now(),
                            entity_id=self._entity_id(),
                            flag=data["Flag"],
                            fee_type=data["Fee type"],
                            status=1)
                        income_header_id4 = inc4.id
                        # len_gth = 0
                        self.income_date_upload(0, data, employee_id, income_header_id4)
                        inc5 = Income_header.objects.using(self._current_app_schema()).create(
                            branch_id=branch_id,
                            business_id=biz_id,
                            assest_class=asset_id,
                            client_id=data["Client id"],
                            product_id=1,
                            created_by=employee_id,
                            created_date=datetime.now(),
                            entity_id=self._entity_id(),
                            flag=data["Flag"],
                            fee_type=data["Fee type"],
                            status=1)
                        income_header_id5 = inc5.id
                        # len_gth = 0
                        self.income_date_upload(0, data, employee_id, income_header_id5)
                        inc_mon4 = Income_details_month.objects.using(self._current_app_schema()).create(
                            activeclient_id=inc4.id, month=1, disbursal_amount=data["Disbursed amount"],
                            total_disbursalamount=data["Total disbursal"],
                            beginning_fee_due=data["Total fee due beginning"],
                            interest_gl = data["Interest"],
                            interest_amount=data["Int Amount"],
                            eir_amount=data["EIR"], created_by=employee_id,
                            created_date=datetime.now(), entity_id=self._entity_id(),
                            sanctioned_amount=0, sanctioned_date=data["Sanctioned Date"],
                            opening_pos=data["Opening POS"], closing_pos=data["Closing POS"],fee_due=data["fee due"],collected_fee=data["Total fee collected"])
                        inc_mon5 = Income_details_month.objects.using(self._current_app_schema()).create(
                            activeclient_id=inc5.id, month=1, disbursal_amount=data["Disbursed amount"],
                            total_disbursalamount=data["Total disbursal"],
                            beginning_fee_due=data["Total fee due beginning"],
                            interest_gl = data["Interest"],
                            interest_amount=data["Int Amount"],
                            eir_amount=data["EIR"], created_by=employee_id,
                            created_date=datetime.now(), entity_id=self._entity_id(),
                            sanctioned_amount=0, sanctioned_date=data["Sanctioned Date"],
                            opening_pos=data["Opening POS"], closing_pos=data["Closing POS"],fee_due=data["fee due"],collected_fee=data["Total fee collected"])

                    elif len(income_header) == 4:
                        for i in income_header:
                            arr.append(i.id)
                        # income_header_id3 = inc3.id
                        # len_gth = 0
                        self.income_date_upload(len_gth, data, employee_id, arr)
                        inc_mon1 = Income_details_month.objects.using(self._current_app_schema()).filter(
                            activeclient_id__in=arr).update(
                            month=1, disbursal_amount=F('disbursal_amount') + data["Disbursed amount"],
                            total_disbursalamount=F('total_disbursalamount') + data["Total disbursal"],
                            beginning_fee_due=F('beginning_fee_due') + data["Total fee due beginning"],
                            interest_gl = data["Interest"],
                            interest_amount=F('interest_amount') + data["Int Amount"],
                            eir_amount=F('eir_amount') + data["EIR"], created_by=employee_id,
                            created_date=datetime.now(), entity_id=self._entity_id(),
                            sanctioned_amount=F('sanctioned_amount') + 0,
                            opening_pos=F('opening_pos') + data["Opening POS"],
                            closing_pos=F('closing_pos') + data["Closing POS"],fee_due=F('fee_due') +data["fee due"],collected_fee=F('collected_fee') +data["Total fee collected"])
                        inc5 = Income_header.objects.using(self._current_app_schema()).create(
                            branch_id=branch_id,
                            business_id=biz_id,
                            assest_class=asset_id,
                            client_id=data["Client id"],
                            product_id=1,
                            created_by=employee_id,
                            created_date=datetime.now(),
                            entity_id=self._entity_id(),
                            flag=data["Flag"],
                            fee_type=data["Fee type"],
                            status=1)
                        income_header_id5 = inc5.id
                        # len_gth = 0
                        self.income_date_upload(0, data, employee_id, income_header_id5)
                        inc_mon5 = Income_details_month.objects.using(self._current_app_schema()).create(
                            activeclient_id=inc5.id, month=1, disbursal_amount=data["Disbursed amount"],
                            total_disbursalamount=data["Total disbursal"],
                            beginning_fee_due=data["Total fee due beginning"],
                            interest_gl = data["Interest"],
                            interest_amount=data["Int Amount"],
                            eir_amount=data["EIR"], created_by=employee_id,
                            created_date=datetime.now(), entity_id=self._entity_id(),
                            sanctioned_amount=0, sanctioned_date=data["Sanctioned Date"],
                            opening_pos=data["Opening POS"], closing_pos=data["Closing POS"],fee_due=data["fee due"],collected_fee=data["Total fee collected"])

                    elif len(income_header) == 5:

                        arr = []
                        for i in income_header:
                            # inc1 = Income_header.objects.using(self._current_app_schema()).filter(id=i.id).update(
                            #     branch_id=data["Branch code"], business_id=None, assest_class=None, client_id=None,
                            #     product_id=None, created_by=employee_id, created_date=datetime.now(),
                            #     entity_id=self._entity_id(), flag=data["Flag"], fee_type=data["Fee type"], status=1)
                            # inc2 = Income_header.objects.using(self._current_app_schema()).filter(id=i.id).update(
                            #     branch_id=data["Branch code"], business_id=data["Business id"], assest_class=None,
                            #     client_id=None, product_id=None, created_by=employee_id, created_date=datetime.now(),
                            #     entity_id=self._entity_id(), flag=data["Flag"], fee_type=data["Fee type"], status=1)
                            # inc3 = Income_header.objects.using(self._current_app_schema()).filter(id=i.id).update(
                            #     branch_id=data["Branch code"], business_id=data["Business id"],
                            #     assest_class=data["asset class"], client_id=None, product_id=None, created_by=employee_id,
                            #     created_date=datetime.now(), entity_id=self._entity_id(), flag=data["Flag"],
                            #     fee_type=data["Fee type"], status=1)
                            # inc4 = Income_header.objects.using(self._current_app_schema()).filter(id=i.id).update(
                            #     branch_id=data["Branch code"], business_id=data["Business id"],
                            #     assest_class=data["asset class"], client_id=data["Client id"], product_id=None,
                            #     created_by=employee_id, created_date=datetime.now(), entity_id=self._entity_id(),
                            #     flag=data["Flag"], fee_type=data["Fee type"], status=1)
                            # inc5 = Income_header.objects.using(self._current_app_schema()).filter(id=i.id).update(
                            #     branch_id=data["Branch code"], business_id=data["Business id"],
                            #     assest_class=data["asset class"], client_id=data["Client id"],
                            #     product_id=data["product id"], created_by=employee_id, created_date=datetime.now(),
                            #     entity_id=self._entity_id(), flag=data["Flag"], fee_type=data["Fee type"], status=1)
                            arr.append(i.id)
                            # income_header_id3 = inc3.id
                            # len_gth = 0
                        self.income_date_upload(len_gth, data, employee_id, arr)
                        inc_mon1 = Income_details_month.objects.using(self._current_app_schema()).filter(
                            activeclient_id__in=arr).update(
                            month=1, disbursal_amount=F('disbursal_amount') + data["Disbursed amount"],
                            total_disbursalamount=F('total_disbursalamount') + data["Total disbursal"],
                            beginning_fee_due=F('beginning_fee_due') + data["Total fee due beginning"],
                            interest_gl = data["Interest"],
                            interest_amount=F('interest_amount') + data["Int Amount"],
                            eir_amount=F('eir_amount') + data["EIR"], created_by=employee_id,
                            created_date=datetime.now(), entity_id=self._entity_id(),
                            sanctioned_amount=F('sanctioned_amount') + 0,
                            opening_pos=F('opening_pos') + data["Opening POS"],
                            closing_pos=F('closing_pos') + data["Closing POS"],fee_due=F('fee_due') +data["fee due"],collected_fee=F('collected_fee') +data["Total fee collected"])

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return success_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj


    def income_header_fetch(self,data,employee_id,vys_page):
        try:
            income_details=Income_details_month.objects.using(self._current_app_schema()).filter(activeclient__assest_class__in=data["assest_class"],month=data["month"],activeclient__product_id=None,activeclient__client_id=None).values("activeclient__assest_class", "activeclient__fee_type").annotate(interest_amount1=Sum("interest_amount"),eir_amount1=Sum("eir_amount"),fee_due1=Sum("fee_due")).values("interest_amount","eir_amount","fee_due","activeclient__fee_type","activeclient__assest_class")[vys_page.get_offset():vys_page.get_query_limit()]

            Interest_income=[]
            Gurantee_fee=[]
            Syndication_fee=[]
            Professional_fee=[]
            resp_list = NWisefinList()
            data1=[]
            data2=[]
            data3=[]
            data4=[]
            for i in income_details:

                doc_data = Income_details_response()
                if i["activeclient__fee_type"]==Fees_type.Interest_income:
                    interest_amount=float(i["interest_amount"])+float(i["eir_amount"])
                    doc_data.set_amount(interest_amount)

                    # doc_data.set_fee_type(Fees_type.Interest_income_var)
                    # if i.activeclient.flag == Client_flag.OWN:
                    #     doc_data.set_flag(Client_flag.OWN_VAL)
                    # elif i.activeclient.flag == Client_flag.ENABLED:
                    #     doc_data.set_flag(Client_flag.ENABLED_VAL)

                    cls = Asset_class()
                    doc_data.set_assest_class(cls.getasset(i["activeclient__assest_class"]))
                    Interest_income.append(doc_data)
                    data1={"name":Fees_type.Interest_income_var,"value":Interest_income}
                    # resp_list.append(dict)
                    # resp_list.append(data)
                elif i["activeclient__fee_type"]==Fees_type.Gurantee_fee:
                    # doc_data.set_fee_type(Fees_type.Gurantee_fee_var)
                    doc_data.set_amount(i["fee_due"])

                    # if i.activeclient.flag == Client_flag.OWN:
                    #     doc_data.set_flag(Client_flag.OWN_VAL)
                    # elif i.activeclient.flag == Client_flag.ENABLED:
                    #     doc_data.set_flag(Client_flag.ENABLED_VAL)

                    cls = Asset_class()
                    doc_data.set_assest_class(cls.getasset(i["activeclient__assest_class"]))


                    data2 = {"name": Fees_type.Gurantee_fee_var, "value": Gurantee_fee}
                    # resp_list.append(dict)
                    # resp_list.append(data)
                elif i["activeclient__fee_type"]==Fees_type.Syndication_fee:
                    # doc_data.set_fee_type(Fees_type.Syndication_fee_var)
                    doc_data.set_amount(i["fee_due"])
                    # doc_data = Income_details_response()

                    # if i.activeclient.flag == Client_flag.OWN:
                    #     doc_data.set_flag(Client_flag.OWN_VAL)
                    # elif i.activeclient.flag == Client_flag.ENABLED:
                    #     doc_data.set_flag(Client_flag.ENABLED_VAL)

                    cls = Asset_class()
                    doc_data.set_assest_class(cls.getasset(i["activeclient__assest_class"]))


                    Syndication_fee.append(doc_data)

                    data3 = {"name": Fees_type.Syndication_fee_var, "value": Syndication_fee}

                elif i["activeclient__fee_type"]==Fees_type.Professional_fee:
                    # doc_data.set_fee_type(Fees_type.Professional_fee_var)

                    if i.activeclient.flag == Client_flag.OWN:
                        doc_data.set_flag(Client_flag.OWN_VAL)
                    elif i.activeclient.flag == Client_flag.ENABLED:
                        doc_data.set_flag(Client_flag.ENABLED_VAL)
                    doc_data.set_amount(i["fee_due"])

                    cls = Asset_class()
                    doc_data.set_assest_class(cls.getasset(i["activeclient__assest_class"]))



                    data4 = {"name": Fees_type.Professional_fee_var, "value": Professional_fee}
            if len(data1)!=0:
                resp_list.append(data1)
            if len(data2) != 0:
                resp_list.append(data2)
            if len(data3)!=0:
                resp_list.append(data3)
            if len(data4)!=0:
                resp_list.append(data4)
            vpage = NWisefinPaginator(income_details, vys_page.get_index(), 10)
            resp_list.set_pagination(vpage)
            return resp_list
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            # logger.info('ta_ change_approver- ' + str(e) + str(exc))
            return error_obj


    def income_amount_date(self,body,employee_id,vys_page):
        try:
            masterservice = MASTER_SERVICE(self._scope())
            condition = Q(date__date__range=(body["fromdate"], body["todate"]))
            # if int(body["business_id"]) !=4:
            condition&=Q(activeclient__business_id=body["business_id"])
            # if "product_id" not in body and "client_id" not in body:
            #     condition&=Q(activeclient__product_id=None,activeclient__client_id=None)
            if "product_id" not in body:
                if "Rm_id" in body and "client_id" in body and "assest_class" in body:
                    rm = self.client_get(body["Rm_id"])
                    rm.append(body["client_id"])
                    condition &= Q(activeclient__product_id=None, activeclient__client_id__in=rm,activeclient__assest_class__in=body["assest_class"])
                elif "Rm_id" in body and "client_id" in body and "assest_class" not in body:
                    rm = self.client_get(body["Rm_id"])
                    rm.append(body["client_id"])
                    condition &= Q(activeclient__product_id=None, activeclient__client_id__in=rm)
                elif "Rm_id" in body and "client_id" not in body and "assest_class" in body:
                    rm=self.client_get(body["Rm_id"])
                    condition &= Q(activeclient__product_id=None, activeclient__client_id__in=rm,activeclient__assest_class__in=body["assest_class"])
                elif "Rm_id" in body and "client_id" not in body and "assest_class" not in body:
                    rm=self.client_get(body["Rm_id"])
                    condition &= Q(activeclient__product_id=None, activeclient__client_id__in=rm)
                elif "Rm_id" not in body and "client_id" in body and "assest_class" in body:
                    condition &= Q(activeclient__product_id=None, activeclient__client_id=body["client_id"])
                elif "Rm_id" not in body and "client_id" in body and "assest_class" not  in body:
                    condition &= Q(activeclient__product_id=None, activeclient__client_id=body["client_id"],activeclient__assest_class__in=body["assest_class"])
                elif "Rm_id" not in body and "client_id" not in body and "assest_class" not  in body:
                    # condition &= Q(activeclient__product_id=None, activeclient__client_id=None)
                    condition &= Q(activeclient__product_id=None, activeclient__client_id=None)
                    condition&=~Q(activeclient__assest_class=None)

                elif "Rm_id" not in body and "client_id" not in body and "assest_class" in body:
                    condition &= Q(activeclient__product_id=None, activeclient__client_id=None,activeclient__assest_class__in=body["assest_class"])


            elif "product_id"  in body :
                # if "client_id" in body:
                if "Rm_id" in body and "client_id" in body and "assest_class" in body:
                    rm = self.client_get(body["Rm_id"])
                    rm.append(body["client_id"])
                    condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id__in=rm,
                                   activeclient__assest_class__in=body["assest_class"])
                elif "Rm_id" in body and "client_id" in body and "assest_class" not in body:
                    rm = self.client_get(body["Rm_id"])
                    rm.append(body["client_id"])
                    condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id__in=rm)
                elif "Rm_id" in body and "client_id" not in body and "assest_class" in body:
                    rm = self.client_get(body["Rm_id"])
                    condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id__in=rm,
                                   activeclient__assest_class__in=body["assest_class"])
                elif "Rm_id" in body and "client_id" not in body and "assest_class" not in body:
                    rm = self.client_get(body["Rm_id"])
                    condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id__in=rm)
                elif "Rm_id" not in body and "client_id" in body and "assest_class" in body:
                    condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id=body["client_id"])
                elif "Rm_id" not in body and "client_id" in body and "assest_class" not in body:
                    condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id=body["client_id"],
                                   activeclient__assest_class__in=body["assest_class"])
                elif "Rm_id" not in body and "client_id" not in body and "assest_class" not in body:
                    condition &= Q(activeclient__product_id=body["product_id"])
                    condition &= ~Q(activeclient__assest_class=None)
                elif "Rm_id" not in body and "client_id" not in body and "assest_class" in body:
                    condition &= Q(activeclient__product_id=body["product_id"],
                                   activeclient__assest_class__in=body["assest_class"])
            # else:
            #     condition&=~Q(activeclient__business_id=None)
            #     condition&=~Q(activeclient__assest_class=None)
            #     condition&=Q(activeclient__client_id=None)

            # if "product_id" in body:
            #         condition &= Q(activeclient__product_id=body["product_id"])

            income_details = Income_details_date.objects.using(self._current_app_schema()).filter(condition
                ).values(
                "activeclient__assest_class","activeclient__flag").annotate(opening_pos1=Sum("opening_pos"),
                                                                             closing_pos1=Sum("closing_pos"),
                                                                             disbursal_amount1=Sum("disbursal_amount"),
                                                                             total_disbursalamount1=Sum(
                                                                                 "total_disbursalamount"),sanctioned_amount1=Sum("sanctioned_amount")).values(
                "activeclient__assest_class", "activeclient__flag", "opening_pos1", "total_disbursalamount1",
                "disbursal_amount1", "closing_pos1","sanctioned_amount1")
            resp_list = NWisefinList()
            assest_class_owned=[]
            assest_class_enabled=[]
            disbursal_amount_owned=[]
            total_disbursalamount_enabled=[]
            disbursal_amount_enabled=[]
            total_disbursalamount_owned=[]
            opening_pos_own=[]
            closing_pos_enable=[]
            opening_pos_enable= []
            closing_pos_own = []
            volume_own = []
            volume_enable = []
            average_enable = []
            average_own = []
            growth_own = []
            growth_enable = []
            # volume=0
            # opening_pos=0
            # closing_pos=0
            # disbursal_amount=0
            # total_disbursalamount=0
            for data in income_details:

                doc_data = Income_details_response()

                # opening_pos =opening_pos+ data["opening_pos1"]
                # closing_pos =closing_pos+ data["closing_pos1"]
                # volume =volume+ data["sanctioned_amount1"]
                # average = (int(opening_pos) + int(closing_pos)) / 2
                # growth = (int(closing_pos) - int(opening_pos))
                #
                # disbursal_amount =disbursal_amount+ data["disbursal_amount1"]
                # total_disbursalamount =total_disbursalamount+ data["total_disbursalamount1"]
                # disbursal_amount_owned.append(disbursal_amount)
                # total_disbursalamount_arr.append(total_disbursalamount)
                # doc_data.set_average(average)
                # doc_data.set_growth(growth)
                # doc_data.set_disbursal_amount(disbursal_amount)
                # doc_data.set_total_disbursalamount(total_disbursalamount)
                # doc_data.set_volume(data["sanctioned_amount1"])
                if data["activeclient__flag"] == Client_flag.OWN:
                    doc_data.set_flag(Client_flag.OWN_VAL)
                    flag_name=Client_flag.OWN_VAL
                    user_dtls = masterservice.get_BS_id([data["activeclient__assest_class"]])
                    # ppr_response.set_assest_class(user_dtls[0]["name"])
                    # cls = Asset_class()
                    # assest = (cls.getasset((data["activeclient__assest_class"])))
                    # print(assest.name)
                    assest_class_owned.append(user_dtls[0]["name"])
                    disbursal_amount = data["disbursal_amount1"]
                    total_disbursalamount = data["total_disbursalamount1"]
                    opening_pos = data["opening_pos1"]
                    closing_pos = data["closing_pos1"]
                    volume = data["sanctioned_amount1"]
                    average = (float(opening_pos) + float(closing_pos)) / 2
                    if (opening_pos) != 0:
                        growth = ((float(closing_pos) - float(opening_pos)) / (float(opening_pos))) * 100
                    else:
                        growth = 0

                    disbursal_amount_owned.append(disbursal_amount)
                    total_disbursalamount_owned.append(total_disbursalamount)
                    opening_pos_own.append(opening_pos)
                    closing_pos_own.append(closing_pos)
                    volume_own.append(volume)
                    average_own.append(average)
                    growth_own.append(growth)


                elif data["activeclient__flag"] == Client_flag.ENABLED:
                    doc_data.set_flag(Client_flag.ENABLED_VAL)
                    flag_name=Client_flag.ENABLED_VAL
                    user_dtls = masterservice.get_BS_id([data["activeclient__assest_class"]])
                    # ppr_response.set_assest_class(user_dtls[0]["name"])
                    # cls = Asset_class()
                    # assest = (cls.getasset((data["activeclient__assest_class"])))
                    # print(assest.name)
                    assest_class_enabled.append(user_dtls[0]["name"])
                    # assest_class_owned.append(user_dtls[0]["name"])
                    disbursal_amount = data["disbursal_amount1"]
                    total_disbursalamount = data["total_disbursalamount1"]

                    opening_pos = data["opening_pos1"]
                    closing_pos =data["closing_pos1"]
                    volume = data["sanctioned_amount1"]
                    average = (float(opening_pos) + float(closing_pos)) / 2
                    if (opening_pos) !=0:
                        growth = ((float(closing_pos) - float(opening_pos)) / (float(opening_pos) ))*100
                    else:
                        growth=0

                    closing_pos_enable.append(closing_pos)
                    opening_pos_enable.append(opening_pos)
                    disbursal_amount_enabled.append(disbursal_amount)
                    total_disbursalamount_enabled.append(total_disbursalamount)
                    volume_enable.append(volume)
                    average_enable.append(average)
                    growth_enable.append(growth)


                cls = Asset_class()
                user_dtls = masterservice.get_BS_id([data["activeclient__assest_class"]])
                doc_data.set_activeclient(user_dtls[0]["id"])
                doc_data.set_opening_pos(opening_pos)
                doc_data.set_closing_pos(closing_pos)
                # resp_list.append(doc_data)
                # arr=["volume","disbursal_amount","Total_disbursal_amount","open","close","average","growth"]
                #
                # for i in range(len(arr)):
                #
                #     if arr[i]=="Total_disbursal_amount":
                #
                #         cls = Client_dtls()
                #         assest=(cls.getasset(data["activeclient__assest_class"]))
                #         data1 = {"name": "Total Disbursal amount -" + flag_name, "value": total_disbursalamount,"assest_class":assest}
                #         # resp_list.append(data1)
                #     if arr[i]=="disbursal_amount":
                #         cls = Client_dtls()
                #         assest = (cls.getasset(data["activeclient__assest_class"]))
                #         data2={"name":"Disbursal Amount -"+flag_name,"value":disbursal_amount,"assest_class":assest}
                #         cls = Client_dtls()
                #         # doc_data.set_activeclient(cls.getasset(data["activeclient__assest_class","assest_class":assest]))
                #         # resp_list.append(data2)
                #     if arr[i]=="volume":
                #         cls = Client_dtls()
                #         assest = (cls.getasset(data["activeclient__assest_class"]))
                #         data3={"name":"Volume -"+flag_name,"value":volume,"assest_class":assest}
                #         cls = Client_dtls()
                #         doc_data.set_activeclient(cls.getasset(data["activeclient__assest_class"]))
                #     if arr[i]=="open":
                #         cls = Client_dtls()
                #         assest = (cls.getasset(data["activeclient__assest_class"]))
                #         data4={"name":"Beginning of period POS  -"+flag_name,"value":opening_pos,"assest_class":assest}
                #         cls = Client_dtls()
                #         doc_data.set_activeclient(cls.getasset(data["activeclient__assest_class"]))
                #     if arr[i]=="close":
                #         cls = Client_dtls()
                #         assest = (cls.getasset(data["activeclient__assest_class"]))
                #         data5={"name":"End of period -"+flag_name,"value":closing_pos,"assest_class":assest}
                #         cls = Client_dtls()
                #         doc_data.set_activeclient(cls.getasset(data["activeclient__assest_class"]))
                #     if arr[i]=="average":
                #         cls = Client_dtls()
                #         assest = (cls.getasset(data["activeclient__assest_class"]))
                #         data6={"name":"Average -"+flag_name,"value":average,"assest_class":assest}
                #         cls = Client_dtls()
                #         doc_data.set_activeclient(cls.getasset(data["activeclient__assest_class"]))
                #     if arr[i]=="growth":
                #         cls = Client_dtls()
                #         assest = (cls.getasset(data["activeclient__assest_class"]))
                #         data7={"name":"Growth -"+flag_name,"value":growth,"assest_class":assest}
                #         cls = Client_dtls()
                #         doc_data.set_activeclient(cls.getasset(data["activeclient__assest_class"]))

                # if len(data1)!=0:
                #     resp_list.append(data1)
                # if len(data2) != 0:
                #     resp_list.append(data2)
                # if len(data3) != 0:
                #     resp_list.append(data3)
                # if len(data4) != 0:
                #     resp_list.append(data4)
                # if len(data5) != 0:
                #     resp_list.append(data5)
                # if len(data6) != 0:
                #     resp_list.append(data6)
                # if len(data7) != 0:
                #     resp_list.append(data7)


            # new_data=json.loads(resp_list.get())
            # print(new_data)
            # client_name=[]
            # client_name_enabled=[]
            # total_disbursalamount=[]
            # disbursal_amount=[]
            #
            # client_name_enabled=[]
            # total_disbursalamount_enabled=[]
            # disbursal_amount_enabled=[]
            # for new_data1 in new_data["data"]:
            #     print(new_data1)
            #     if new_data1["activeclient_id"]["name"]==Asset_class.CF_VAL and new_data1["flag"]==Client_flag.OWN_VAL:
            #         client_name.append(new_data1["activeclient_id"]["name"])
            #         total_disbursalamount.append(new_data1["total_disbursalamount"])
            #         disbursal_amount.append(new_data1["disbursal_amount"])
            #     elif new_data1["activeclient_id"]["name"]==Asset_class.CF_VAL and new_data1["flag"]==Client_flag.ENABLED_VAL:
            #         client_name_enabled.append(new_data1["activeclient_id"]["name"])
            #         total_disbursalamount_enabled.append(new_data1["total_disbursalamount"])
            #         disbursal_amount_enabled.append(new_data1["disbursal_amount"])
            #
            #
            #     elif new_data1["activeclient_id"]["name"]==Asset_class.MF_VAL and new_data1["flag"]==Client_flag.OWN_VAL:
            #         client_name.append(new_data1["activeclient_id"]["name"])
            #         total_disbursalamount.append(new_data1["total_disbursalamount"])
            #         disbursal_amount.append(new_data1["disbursal_amount"])
            #     elif new_data1["activeclient_id"]["name"]==Asset_class.MF_VAL and new_data1["flag"]==Client_flag.ENABLED_VAL:
            #         client_name_enabled.append(new_data1["activeclient_id"]["name"])
            #         total_disbursalamount_enabled.append(new_data1["total_disbursalamount"])
            #         disbursal_amount_enabled.append(new_data1["disbursal_amount"])
            #
            #     elif new_data1["activeclient_id"]["name"]==Asset_class.AGRI_VAL and new_data1["flag"]==Client_flag.OWN_VAL:
            #         client_name.append(new_data1["activeclient_id"]["name"])
            #         total_disbursalamount.append(new_data1["total_disbursalamount"])
            #         disbursal_amount.append(new_data1["disbursal_amount"])
            #     elif new_data1["activeclient_id"]["name"]==Asset_class.AGRI_VAL and new_data1["flag"]==Client_flag.ENABLED_VAL:
            #         client_name_enabled.append(new_data1["activeclient_id"]["name"])
            #         total_disbursalamount_enabled.append(new_data1["total_disbursalamount"])
            #         disbursal_amount_enabled.append(new_data1["disbursal_amount"])
            #
            #
            #     elif  new_data1["activeclient_id"]["name"]==Asset_class.SBL_VAL and new_data1["flag"]==Client_flag.OWN_VAL:
            #         client_name.append(new_data1["activeclient_id"]["name"])
            #         total_disbursalamount.append(new_data1["total_disbursalamount"])
            #         disbursal_amount.append(new_data1["disbursal_amount"])
            #     elif  new_data1["activeclient_id"]["name"]==Asset_class.SBL_VAL and new_data1["flag"]==Client_flag.ENABLED_VAL:
            #         client_name_enabled.append(new_data1["activeclient_id"]["name"])
            #         total_disbursalamount_enabled.append(new_data1["total_disbursalamount"])
            #         disbursal_amount_enabled.append(new_data1["disbursal_amount"])

            # print("client_name:",client_name)
            # print("client_name_enabled:",client_name_enabled)
            # print("total_disbursalamount:",total_disbursalamount)
            # print("disbursal_amount:",disbursal_amount)
            # print("total_disbursalamount_enabled:",total_disbursalamount_enabled)
            # print("disbursal_amount_enabled",disbursal_amount_enabled)
            # out=[]
            # total_disbursalamount1={}
            # # total_disbursalamount1_enabled={}
            # total_disbursalamount1["name"]="total_disbursalamount_own"
            # total_disbursalamount1["Asset_class_value"]=client_name
            # total_disbursalamount1["total_disbursalamount"]=total_disbursalamount
            # total_disbursalamount1_enabled={}
            # total_disbursalamount1_enabled["name"]="total_disbursalamount_enabled"
            # total_disbursalamount1_enabled["Asset_class_value"]=client_name
            # total_disbursalamount1_enabled["total_disbursalamount"]=total_disbursalamount
            # out.append(total_disbursalamount1_enabled)
            # out.append(total_disbursalamount1_enabled)
            # print(out)
            # return out
            # if len(data1)!=0:
            #     resp_list.append(data1)
            # if len(data2) != 0:
            #     resp_list.append(data2)
            # if len(data3) != 0:
            #     resp_list.append(data3)
            # print(data10, "ttowned")
            # print(data11, "ttenabled")
            # print(data12, "dis owned")
            # print(data13, "dis enabled")
            if len(assest_class_owned)!=len(assest_class_enabled):
                if len(assest_class_owned)>len(assest_class_enabled):
                    for i in range(len(assest_class_owned)):
                        # if assest_class_owned[i]!=assest_class_enabled[i]:
                        # if len(assest_class_enabled)==0:
                        #     assest_class_enabled.insert(i,assest_class_owned[i])
                        #     disbursal_amount_enabled.insert(i,0)
                        #     total_disbursalamount_enabled.insert(i,0)
                        #     volume_enable.insert(i,0)
                        #     average_enable.insert(i,0)
                        #     growth_enable.insert(i,0)
                        #     opening_pos_enable.insert(i,0)
                        #     closing_pos_enable.insert(i,0)
                        #
                        # else:
                        if assest_class_owned[i] not in assest_class_enabled:
                            assest_class_enabled.insert(i, assest_class_owned[i])
                            disbursal_amount_enabled.insert(i, 0)
                            total_disbursalamount_enabled.insert(i, 0)
                            volume_enable.insert(i, 0)
                            average_enable.insert(i, 0)
                            growth_enable.insert(i, 0)
                            opening_pos_enable.insert(i, 0)
                            closing_pos_enable.insert(i, 0)
                else:
                    for i in range(len(assest_class_enabled)):
                        # if assest_class_owned[i]!=assest_class_enabled[i]:
                        # if len(assest_class_owned)==0:
                        #     assest_class_owned.insert(i,assest_class_enabled[i])
                        #     disbursal_amount_owned.insert(i,0)
                        #     total_disbursalamount_owned.insert(i,0)
                        #     volume_own.insert(i, 0)
                        #     average_own.insert(i, 0)
                        #     growth_own.insert(i, 0)
                        #     opening_pos_own.insert(i, 0)
                        #     closing_pos_own.insert(i, 0)
                        # else:
                        if assest_class_owned[i] not in assest_class_enabled:
                            assest_class_owned.insert(i, assest_class_enabled[i])
                            disbursal_amount_owned.insert(i, 0)
                            total_disbursalamount_owned.insert(i, 0)
                            volume_own.insert(i, 0)
                            average_own.insert(i, 0)
                            growth_own.insert(i, 0)
                            opening_pos_own.insert(i, 0)
                            closing_pos_own.insert(i, 0)


            arr1=["OWN","ENABLED"]
            for i in range(len(arr1)):
                if arr1[i]==Client_flag.OWN_VAL:
                    dis_own = {"name": "Disbursal Amount OWN (For The Period)", "value": disbursal_amount_owned,
                              "assest_class": assest_class_owned}
                    tot_Dis_own = {"name": "Total Disbursal Amount OWN" , "value": total_disbursalamount_owned,
                              "assest_class": assest_class_owned}
                    Opening_own = {"name": "Opening POS OWN" , "value": opening_pos_own,
                              "assest_class": assest_class_owned}
                    Closing_own={"name": "Closing POS OWN" , "value": closing_pos_own,
                              "assest_class": assest_class_owned}
                    Average={"name": "Average OWN" , "value": average_own,
                              "assest_class": assest_class_owned}
                    Volume={"name": "Volume OWN" , "value": volume_own,
                              "assest_class": assest_class_owned}
                    Growth={"name": "Growth OWN" , "value": growth_own,
                              "assest_class": assest_class_owned}
                    resp_list.append(Volume)
                    resp_list.append(dis_own)
                    resp_list.append(tot_Dis_own)
                    resp_list.append(Opening_own)
                    resp_list.append(Closing_own)
                    resp_list.append(Average)
                    resp_list.append(Growth)

                elif arr1[i] == Client_flag.ENABLED_VAL:
                    dis_enable = {"name": "Disbursal Amount Enabled (For The Period)", "value": disbursal_amount_enabled,
                              "assest_class": assest_class_enabled}

                    tot_Dis_enable = {"name": "Total Disbursal Amount Enabled" , "value": total_disbursalamount_enabled,
                              "assest_class": assest_class_enabled}
                    Opening_enable = {"name": "Opening POS Enabled", "value": opening_pos_enable,
                                   "assest_class": assest_class_enabled}
                    Closing_enable = {"name": "Closing POS Enabled", "value": closing_pos_enable,
                                   "assest_class": assest_class_enabled}
                    Average_enable = {"name": "Average Enabled", "value": average_enable,
                               "assest_class": assest_class_enabled}
                    Volume_enable = {"name": "Volume Enabled", "value":volume_enable,
                              "assest_class": assest_class_enabled}
                    Growth_enable = {"name": "Growth Enabled", "value": growth_enable,
                              "assest_class": assest_class_enabled}
                    resp_list.append(Volume_enable)
                    resp_list.append(dis_enable)
                    resp_list.append(tot_Dis_enable)
                    resp_list.append(Opening_enable)
                    resp_list.append(Closing_enable)
                    resp_list.append(Average_enable)
                    resp_list.append(Growth_enable)







            return resp_list.get()
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            # logger.info('ta_ change_approver- ' + str(e) + str(exc))
            return error_obj.get()


    def fetch_ppr_activeclients(self, filter_obj):
        pro_list = NWisefinList()
        pprutility = Asset_class()
        condition = Q(status=Activestatus.Active,
                      activeclient__type=None,
                      entity_id=self._entity_id()
                      )
        if filter_obj.get_asset_id() != None and filter_obj.get_asset_id() != "" and len(filter_obj.get_asset_id()) > 0 :
            condition &= Q(activeclient__asset_id__in=filter_obj.get_asset_id())
        if filter_obj.get_month() != None and filter_obj.get_month() != "":
            condition &= Q(month=filter_obj.get_month())
        else:
            return pro_list
        get_clients = clients_details_months.objects.using(self._current_app_schema()).filter(condition).values(
            "status", "activeclient__asset_id", "month", "amount").annotate(bop1=Sum('bop'),
                                                                            new_client1=Sum('new_client'),
                                                                            attrition1=Sum('attrition'),
                                                                            closing1=Sum('closing'))
        for i in get_clients:
            fetch_data = ppr_clientresponse()
            asset_var = pprutility.getasset(int(i["activeclient__asset_id"]))
            fetch_data.set_asset_id(asset_var.id)
            fetch_data.set_asset_name(asset_var.name)
            fetch_data.set_month(i["month"])
            fetch_data.set_attrition(i["attrition1"])
            fetch_data.set_bop(i["bop1"])
            fetch_data.set_new_client(i["new_client1"])
            fetch_data.set_amount(i["amount"])
            fetch_data.set_closing(i["closing1"])
            fetch_data.set_status(i["status"])
            pro_list.append(fetch_data)
        return pro_list
    def ppractiveclients_date(self, body):
        masterservice = MASTER_SERVICE(self._scope())
        pro_list = NWisefinList()
        pprutility = Asset_class()
        if "assest_class" in body:
            condition = Q(activeclient__asset_id__in=body["assest_class"],
                          date__date__range=(body["fromdate"], body["todate"]),activeclient__product_id=body["business_id"])
            # if "product_id" not in body and "client_id" not in body:
            #     condition&=Q(activeclient__product_id=None,activeclient__client_id=None)
            if "product_id" not in body:
                if "Rm_id" in body and "client_id" in body:
                    rm = self.client_get(body["Rm_id"])
                    rm.append(body["client_id"])
                    condition &= Q(activeclient__product_id=None, activeclient__client_id__in=rm)
                elif "Rm_id" in body and "client_id" not in body:
                    rm = self.client_get(body["Rm_id"])
                    condition &= Q(activeclient__product_id=None, activeclient__client_id__in=rm)
                elif "Rm_id" not in body and "client_id" in body:
                    condition &= Q(activeclient__product_id=None, activeclient__client_id=body["client_id"])
                # else:
                    # condition &= Q(activeclient__product_id=None, activeclient__client_id=None)


            elif "product_id" in body:
                # if "client_id" in body:
                if "Rm_id" in body and "client_id" in body:
                    rm = self.client_get(body["Rm_id"])
                    rm.append(body["client_id"])
                    condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id__in=rm)
                elif "Rm_id" in body and "client_id" not in body:
                    rm = self.client_get(body["Rm_id"])
                    condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id__in=rm)
                elif "Rm_id" not in body and "client_id" in body:
                    condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id=body["client_id"])
                    # condition &= Q(activeclient__product_id=body["product_id"],activeclient__client_id=body["client_id"])
                else:
                    condition &= Q(activeclient__product_id=body["product_id"])
        else:
            condition = Q(date__date__range=(body["fromdate"], body["todate"]),activeclient__product_id=body["business_id"])

        get_clients = clients_details_date.objects.using(self._current_app_schema()).filter(condition).values(
            "status", "activeclient__asset_id", "amount").annotate(bop1=Sum('bop'),
                                                                            new_client1=Sum('new_client'),
                                                                            attrition1=Sum('attrition'),
                                                                            closing1=Sum('closing'))
        for i in get_clients:
            fetch_data = ppr_clientresponse()
            utils = masterservice.get_BS_id([i["activeclient__asset_id"]])
            # print(utils)
            asset_var = pprutility.getasset(int(i["activeclient__asset_id"]))
            fetch_data.set_asset_id(utils[0]["id"])
            fetch_data.set_asset_name(utils[0]["name"])
            # fetch_data.set_month(i["month"])
            fetch_data.set_attrition(i["attrition1"])
            fetch_data.set_bop(i["bop1"])
            fetch_data.set_new_client(i["new_client1"])
            fetch_data.set_amount(i["amount"])
            fetch_data.set_closing(i["closing1"])
            fetch_data.set_status(i["status"])
            pro_list.append(fetch_data)
        return pro_list

    def income_date_upload(self,len_gth,data,employee_id,income_header_id):
        if len_gth==0:
            inci_date1=Income_details_date.objects.using(self._current_app_schema()).create(activeclient_id=income_header_id, disbursal_amount=data["Disbursed amount"],
                        total_disbursalamount=data["Total disbursal"],
                        beginning_fee_due=data["Total fee due beginning"],
                        interest_amount=data["Int Amount"], eir_amount=data["EIR"],
                        created_by=employee_id, created_date=datetime.now(), entity_id=self._entity_id(),
                        flag=data["Flag"], sanctioned_amount=0,interest_gl=data["Interest"],
                        sanctioned_date=data["Sanctioned Date"], opening_pos=data["Opening POS"],
                        closing_pos=data["Closing POS"],date=data["date"],fee_due=data["fee due"],collected_fee=data["Total fee collected"])
        # elif len_gth!=0:
        #     inc_mon1 = Income_details_month.objects.using(self._current_app_schema()).filter(
        #         activeclient_id__in=income_header_id,date=data["date"]).update(
        #         month=1, disbursal_amount=F('disbursal_amount') + data["Disbursed amount"],
        #         total_disbursalamount=F('total_disbursalamount') + data["Total disbursal"],
        #         beginning_fee_due=F('beginning_fee_due') + data["Opening Balance - Disbursal"],
        #
        #         interest_amount=F('interest_amount') + data["Int Amount"],
        #         eir_amount=F('eir_amount') + data["EIR"], created_by=employee_id,
        #         created_date=datetime.now(), entity_id=self._entity_id(),
        #         sanctioned_amount=F('sanctioned_amount') + data["Facility Amount"],
        #         opening_pos=F('opening_pos') + data["Opening POS"],
        #         closing_pos=F('closing_pos') + data["Closing POS"])
        elif len_gth!=0:
            inc_date2 = Income_details_date.objects.using(self._current_app_schema()).filter(
                activeclient_id__in=income_header_id,date=data["date"])
            if len(inc_date2)!=0:
                inc_date2.update(
                disbursal_amount=F('disbursal_amount') + data["Disbursed amount"],
                total_disbursalamount=F('total_disbursalamount') + data["Total disbursal"],
                beginning_fee_due=F('beginning_fee_due') + data["Total fee due beginning"],

                interest_amount=F('interest_amount') + data["Int Amount"],
                eir_amount=F('eir_amount') + data["EIR"], created_by=employee_id,
                created_date=datetime.now(), entity_id=self._entity_id(),
                sanctioned_amount=F('sanctioned_amount') + 0,
                opening_pos=F('opening_pos') + data["Opening POS"],
                closing_pos=F('closing_pos') + data["Closing POS"],fee_due=F('fee_due') +data["fee due"],collected_fee=F('collected_fee') +data["Total fee collected"])
            else:
                for i in income_header_id:
                    inci_date1 = Income_details_date.objects.using(self._current_app_schema()).create(
                        activeclient_id=i, disbursal_amount=data["Disbursed amount"],
                        total_disbursalamount=data["Total disbursal"],
                        beginning_fee_due=data["Total fee due beginning"],
                        interest_amount=data["Int Amount"], eir_amount=data["EIR"],interest_gl=data["Interest"],
                        created_by=employee_id, created_date=datetime.now(), entity_id=self._entity_id(),
                        flag=data["Flag"], sanctioned_amount=0,
                        sanctioned_date=data["Sanctioned Date"], opening_pos=data["Opening POS"],
                        closing_pos=data["Closing POS"], date=data["date"],fee_due=data["fee due"],collected_fee=data["Total fee collected"])


    def income_header_amount(self,body,employee_id,vys_page):
        try:
            masterservice = MASTER_SERVICE(self._scope())
            income_details = Income_details_month.objects.using(self._current_app_schema()).filter(
                activeclient__assest_class__in=body["assest_class"], month=body["month"],activeclient__product_id=None,activeclient__client_id=None).values(
                "activeclient__assest_class", "activeclient__flag").annotate(opening_pos1=Sum("opening_pos"),
                                                                             closing_pos1=Sum("closing_pos"),
                                                                             disbursal_amount1=Sum("disbursal_amount"),
                                                                             total_disbursalamount1=Sum(
                                                                                 "total_disbursalamount"),sanctioned_amount1=Sum("sanctioned_amount")).values(
                "activeclient__assest_class", "activeclient__flag", "opening_pos", "total_disbursalamount",
                "disbursal_amount", "closing_pos","sanctioned_amount")
            resp_list = NWisefinList()
            assest_class_owned=[]
            assest_class_enabled=[]
            disbursal_amount_owned=[]
            total_disbursalamount_enabled=[]
            disbursal_amount_enabled=[]
            total_disbursalamount_owned=[]
            opening_pos_own=[]
            closing_pos_enable=[]
            opening_pos_enable= []
            closing_pos_own = []
            volume_own = []
            volume_enable = []
            average_enable = []
            average_own = []
            growth_own = []
            growth_enable = []

            for data in income_details:

                doc_data = Income_details_response()

                opening_pos = data["opening_pos"]
                closing_pos = data["closing_pos"]
                volume = data["sanctioned_amount"]
                average = (int(opening_pos) + int(closing_pos)) / 2
                growth = (int(closing_pos) - int(opening_pos))

                disbursal_amount = data["disbursal_amount"]
                total_disbursalamount = data["total_disbursalamount"]
                # disbursal_amount_owned.append(disbursal_amount)
                # total_disbursalamount_arr.append(total_disbursalamount)
                doc_data.set_average(average)
                doc_data.set_growth(growth)
                doc_data.set_disbursal_amount(disbursal_amount)
                doc_data.set_total_disbursalamount(total_disbursalamount)
                doc_data.set_volume(data["sanctioned_amount"])
                if data["activeclient__flag"] == Client_flag.OWN:
                    doc_data.set_flag(Client_flag.OWN_VAL)
                    flag_name=Client_flag.OWN_VAL
                    cls = Asset_class()
                    assest = (cls.getasset((data["activeclient__assest_class"])))
                    # print(assest.name)
                    ast_dtls = masterservice.get_BS_id(data["activeclient__assest_class"])
                    assest_class_owned.append(ast_dtls[0]["name"])
                    disbursal_amount = data["disbursal_amount"]
                    total_disbursalamount = data["total_disbursalamount"]
                    opening_pos = data["opening_pos"]
                    closing_pos = data["closing_pos"]
                    volume = data["sanctioned_amount"]
                    average = (int(opening_pos) + int(closing_pos)) / 2
                    growth = (int(closing_pos) - int(opening_pos))

                    disbursal_amount_owned.append(disbursal_amount)
                    total_disbursalamount_owned.append(total_disbursalamount)
                    opening_pos_own.append(opening_pos)
                    closing_pos_own.append(closing_pos)
                    volume_own.append(volume)
                    average_own.append(average)
                    growth_own.append(growth)


                elif data["activeclient__flag"] == Client_flag.ENABLED:
                    doc_data.set_flag(Client_flag.ENABLED_VAL)
                    flag_name=Client_flag.ENABLED_VAL
                    cls = Asset_class()
                    assest = cls.getasset(data["activeclient__assest_class"])
                    ast_dtls = masterservice.get_BS_id(data["activeclient__assest_class"])
                    assest_class_owned.append(ast_dtls[0]["name"])
                    disbursal_amount = data["disbursal_amount"]
                    total_disbursalamount = data["total_disbursalamount"]

                    opening_pos = data["opening_pos"]
                    closing_pos = data["closing_pos"]
                    volume = data["sanctioned_amount"]
                    average = (int(opening_pos) + int(closing_pos)) / 2
                    growth = (int(closing_pos) - int(opening_pos))

                    closing_pos_enable.append(closing_pos)
                    opening_pos_enable.append(opening_pos)
                    disbursal_amount_enabled.append(disbursal_amount)
                    total_disbursalamount_enabled.append(total_disbursalamount)
                    volume_enable.append(volume)
                    average_enable.append(average)
                    growth_enable.append(growth)


                cls = Asset_class()
                doc_data.set_activeclient(cls.getasset(data["activeclient__assest_class"]))
                doc_data.set_opening_pos(opening_pos)
                doc_data.set_closing_pos(closing_pos)
                # resp_list.append(doc_data)
                # arr=["volume","disbursal_amount","Total_disbursal_amount","open","close","average","growth"]
                #
                # for i in range(len(arr)):
                #
                #     if arr[i]=="Total_disbursal_amount":
                #
                #         cls = Client_dtls()
                #         assest=(cls.getasset(data["activeclient__assest_class"]))
                #         data1 = {"name": "Total Disbursal amount -" + flag_name, "value": total_disbursalamount,"assest_class":assest}
                #         # resp_list.append(data1)
                #     if arr[i]=="disbursal_amount":
                #         cls = Client_dtls()
                #         assest = (cls.getasset(data["activeclient__assest_class"]))
                #         data2={"name":"Disbursal Amount -"+flag_name,"value":disbursal_amount,"assest_class":assest}
                #         cls = Client_dtls()
                #         # doc_data.set_activeclient(cls.getasset(data["activeclient__assest_class","assest_class":assest]))
                #         # resp_list.append(data2)
                #     if arr[i]=="volume":
                #         cls = Client_dtls()
                #         assest = (cls.getasset(data["activeclient__assest_class"]))
                #         data3={"name":"Volume -"+flag_name,"value":volume,"assest_class":assest}
                #         cls = Client_dtls()
                #         doc_data.set_activeclient(cls.getasset(data["activeclient__assest_class"]))
                #     if arr[i]=="open":
                #         cls = Client_dtls()
                #         assest = (cls.getasset(data["activeclient__assest_class"]))
                #         data4={"name":"Beginning of period POS  -"+flag_name,"value":opening_pos,"assest_class":assest}
                #         cls = Client_dtls()
                #         doc_data.set_activeclient(cls.getasset(data["activeclient__assest_class"]))
                #     if arr[i]=="close":
                #         cls = Client_dtls()
                #         assest = (cls.getasset(data["activeclient__assest_class"]))
                #         data5={"name":"End of period -"+flag_name,"value":closing_pos,"assest_class":assest}
                #         cls = Client_dtls()
                #         doc_data.set_activeclient(cls.getasset(data["activeclient__assest_class"]))
                #     if arr[i]=="average":
                #         cls = Client_dtls()
                #         assest = (cls.getasset(data["activeclient__assest_class"]))
                #         data6={"name":"Average -"+flag_name,"value":average,"assest_class":assest}
                #         cls = Client_dtls()
                #         doc_data.set_activeclient(cls.getasset(data["activeclient__assest_class"]))
                #     if arr[i]=="growth":
                #         cls = Client_dtls()
                #         assest = (cls.getasset(data["activeclient__assest_class"]))
                #         data7={"name":"Growth -"+flag_name,"value":growth,"assest_class":assest}
                #         cls = Client_dtls()
                #         doc_data.set_activeclient(cls.getasset(data["activeclient__assest_class"]))

                # if len(data1)!=0:
                #     resp_list.append(data1)
                # if len(data2) != 0:
                #     resp_list.append(data2)
                # if len(data3) != 0:
                #     resp_list.append(data3)
                # if len(data4) != 0:
                #     resp_list.append(data4)
                # if len(data5) != 0:
                #     resp_list.append(data5)
                # if len(data6) != 0:
                #     resp_list.append(data6)
                # if len(data7) != 0:
                #     resp_list.append(data7)


            # new_data=json.loads(resp_list.get())
            # print(new_data)
            # client_name=[]
            # client_name_enabled=[]
            # total_disbursalamount=[]
            # disbursal_amount=[]
            #
            # client_name_enabled=[]
            # total_disbursalamount_enabled=[]
            # disbursal_amount_enabled=[]
            # for new_data1 in new_data["data"]:
            #     print(new_data1)
            #     if new_data1["activeclient_id"]["name"]==Asset_class.CF_VAL and new_data1["flag"]==Client_flag.OWN_VAL:
            #         client_name.append(new_data1["activeclient_id"]["name"])
            #         total_disbursalamount.append(new_data1["total_disbursalamount"])
            #         disbursal_amount.append(new_data1["disbursal_amount"])
            #     elif new_data1["activeclient_id"]["name"]==Asset_class.CF_VAL and new_data1["flag"]==Client_flag.ENABLED_VAL:
            #         client_name_enabled.append(new_data1["activeclient_id"]["name"])
            #         total_disbursalamount_enabled.append(new_data1["total_disbursalamount"])
            #         disbursal_amount_enabled.append(new_data1["disbursal_amount"])
            #
            #
            #     elif new_data1["activeclient_id"]["name"]==Asset_class.MF_VAL and new_data1["flag"]==Client_flag.OWN_VAL:
            #         client_name.append(new_data1["activeclient_id"]["name"])
            #         total_disbursalamount.append(new_data1["total_disbursalamount"])
            #         disbursal_amount.append(new_data1["disbursal_amount"])
            #     elif new_data1["activeclient_id"]["name"]==Asset_class.MF_VAL and new_data1["flag"]==Client_flag.ENABLED_VAL:
            #         client_name_enabled.append(new_data1["activeclient_id"]["name"])
            #         total_disbursalamount_enabled.append(new_data1["total_disbursalamount"])
            #         disbursal_amount_enabled.append(new_data1["disbursal_amount"])
            #
            #     elif new_data1["activeclient_id"]["name"]==Asset_class.AGRI_VAL and new_data1["flag"]==Client_flag.OWN_VAL:
            #         client_name.append(new_data1["activeclient_id"]["name"])
            #         total_disbursalamount.append(new_data1["total_disbursalamount"])
            #         disbursal_amount.append(new_data1["disbursal_amount"])
            #     elif new_data1["activeclient_id"]["name"]==Asset_class.AGRI_VAL and new_data1["flag"]==Client_flag.ENABLED_VAL:
            #         client_name_enabled.append(new_data1["activeclient_id"]["name"])
            #         total_disbursalamount_enabled.append(new_data1["total_disbursalamount"])
            #         disbursal_amount_enabled.append(new_data1["disbursal_amount"])
            #
            #
            #     elif  new_data1["activeclient_id"]["name"]==Asset_class.SBL_VAL and new_data1["flag"]==Client_flag.OWN_VAL:
            #         client_name.append(new_data1["activeclient_id"]["name"])
            #         total_disbursalamount.append(new_data1["total_disbursalamount"])
            #         disbursal_amount.append(new_data1["disbursal_amount"])
            #     elif  new_data1["activeclient_id"]["name"]==Asset_class.SBL_VAL and new_data1["flag"]==Client_flag.ENABLED_VAL:
            #         client_name_enabled.append(new_data1["activeclient_id"]["name"])
            #         total_disbursalamount_enabled.append(new_data1["total_disbursalamount"])
            #         disbursal_amount_enabled.append(new_data1["disbursal_amount"])

            # print("client_name:",client_name)
            # print("client_name_enabled:",client_name_enabled)
            # print("total_disbursalamount:",total_disbursalamount)
            # print("disbursal_amount:",disbursal_amount)
            # print("total_disbursalamount_enabled:",total_disbursalamount_enabled)
            # print("disbursal_amount_enabled",disbursal_amount_enabled)
            # out=[]
            # total_disbursalamount1={}
            # # total_disbursalamount1_enabled={}
            # total_disbursalamount1["name"]="total_disbursalamount_own"
            # total_disbursalamount1["Asset_class_value"]=client_name
            # total_disbursalamount1["total_disbursalamount"]=total_disbursalamount
            # total_disbursalamount1_enabled={}
            # total_disbursalamount1_enabled["name"]="total_disbursalamount_enabled"
            # total_disbursalamount1_enabled["Asset_class_value"]=client_name
            # total_disbursalamount1_enabled["total_disbursalamount"]=total_disbursalamount
            # out.append(total_disbursalamount1_enabled)
            # out.append(total_disbursalamount1_enabled)
            # print(out)
            # return out
            # if len(data1)!=0:
            #     resp_list.append(data1)
            # if len(data2) != 0:
            #     resp_list.append(data2)
            # if len(data3) != 0:
            #     resp_list.append(data3)
            # print(data10, "ttowned")
            # print(data11, "ttenabled")
            # print(data12, "dis owned")
            # print(data13, "dis enabled")
            if len(assest_class_owned)!=len(assest_class_enabled):
                if len(assest_class_owned)>len(assest_class_enabled):
                    for i in range(len(assest_class_owned)):
                        # if assest_class_owned[i]!=assest_class_enabled[i]:
                        # if len(assest_class_enabled)==0:
                        #     assest_class_enabled.insert(i,assest_class_owned[i])
                        #     disbursal_amount_enabled.insert(i,0)
                        #     total_disbursalamount_enabled.insert(i,0)
                        #     volume_enable.insert(i,0)
                        #     average_enable.insert(i,0)
                        #     growth_enable.insert(i,0)
                        #     opening_pos_enable.insert(i,0)
                        #     closing_pos_enable.insert(i,0)
                        #
                        # else:
                        if assest_class_owned[i] not in assest_class_enabled:
                            assest_class_enabled.insert(i, assest_class_owned[i])
                            disbursal_amount_enabled.insert(i, 0)
                            total_disbursalamount_enabled.insert(i, 0)
                            volume_enable.insert(i, 0)
                            average_enable.insert(i, 0)
                            growth_enable.insert(i, 0)
                            opening_pos_enable.insert(i, 0)
                            closing_pos_enable.insert(i, 0)
                else:
                    for i in range(len(assest_class_enabled)):
                        # if assest_class_owned[i]!=assest_class_enabled[i]:
                        # if len(assest_class_owned)==0:
                        #     assest_class_owned.insert(i,assest_class_enabled[i])
                        #     disbursal_amount_owned.insert(i,0)
                        #     total_disbursalamount_owned.insert(i,0)
                        #     volume_own.insert(i, 0)
                        #     average_own.insert(i, 0)
                        #     growth_own.insert(i, 0)
                        #     opening_pos_own.insert(i, 0)
                        #     closing_pos_own.insert(i, 0)
                        # else:
                        if assest_class_owned[i] not in assest_class_enabled:
                            assest_class_owned.insert(i, assest_class_enabled[i])
                            disbursal_amount_owned.insert(i, 0)
                            total_disbursalamount_owned.insert(i, 0)
                            volume_own.insert(i, 0)
                            average_own.insert(i, 0)
                            growth_own.insert(i, 0)
                            opening_pos_own.insert(i, 0)
                            closing_pos_own.insert(i, 0)
            # else:
            #     if len(assest_class_owned)==0:
            #         pass



            arr1=["OWN","ENABLED"]
            for i in range(len(arr1)):
                if arr1[i]==Client_flag.OWN_VAL:
                    dis_own = {"name": "Disbursal amount OWN", "value": disbursal_amount_owned,
                              "assest_class": assest_class_owned}
                    tot_Dis_own = {"name": "Total Disbursal amount OWN" , "value": total_disbursalamount_owned,
                              "assest_class": assest_class_owned}
                    Opening_own = {"name": "Opening OWN" , "value": opening_pos_own,
                              "assest_class": assest_class_owned}
                    Closing_own={"name": "Closing OWN" , "value": closing_pos_own,
                              "assest_class": assest_class_owned}
                    Average={"name": "Average OWN" , "value": average_own,
                              "assest_class": assest_class_owned}
                    Volume={"name": "Volume OWN" , "value": volume_own,
                              "assest_class": assest_class_owned}
                    Growth={"name": "Growth OWN" , "value": growth_own,
                              "assest_class": assest_class_owned}
                    resp_list.append(dis_own)
                    resp_list.append(tot_Dis_own)
                    resp_list.append(Opening_own)
                    resp_list.append(Closing_own)
                    resp_list.append(Average)
                    resp_list.append(Volume)
                    resp_list.append(Growth)

                elif arr1[i] == Client_flag.ENABLED_VAL:
                    dis_enable = {"name": "Disbursal amount ENABLE", "value": disbursal_amount_enabled,
                              "assest_class": assest_class_enabled}

                    tot_Dis_enable = {"name": "Total Disbursal amount ENABLE" , "value": total_disbursalamount_enabled,
                              "assest_class": assest_class_enabled}
                    Opening_enable = {"name": "Opening Enable", "value": opening_pos_enable,
                                   "assest_class": assest_class_enabled}
                    Closing_enable = {"name": "Closing Enable", "value": closing_pos_enable,
                                   "assest_class": assest_class_enabled}
                    Average_enable = {"name": "Average Enable", "value": average_enable,
                               "assest_class": assest_class_enabled}
                    Volume_enable = {"name": "Volume Enable", "value":volume_enable,
                              "assest_class": assest_class_enabled}
                    Growth_enable = {"name": "Growth Enable", "value": growth_enable,
                              "assest_class": assest_class_enabled}
                    resp_list.append(Opening_enable)
                    resp_list.append(Closing_enable)
                    resp_list.append(Average_enable)
                    resp_list.append(Volume_enable)
                    resp_list.append(Growth_enable)
                    resp_list.append(tot_Dis_enable)
                    resp_list.append(dis_enable)





            return resp_list.get()
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            # logger.info('ta_ change_approver- ' + str(e) + str(exc))
            return error_obj.get()

    def client_get(self,Rm_id):
        from masterservice.models.mastermodels import Nac_Client
        client_tab=Nac_Client.objects.using(self._current_app_schema()).filter(rm_name=Rm_id)
        arr=[]
        for data in client_tab:
            arr.append(data.id)
        return arr

    def active_clients_date(self,len_gth,data,employee_id,active_clie_id):
        if len_gth==0:
            act_date=clients_details_date.objects.using(self._current_app_schema()).create(activeclient_id=active_clie_id,bop=data["BOP"],new_client=data["New"],attrition=data["Attrition"],closing=data["Closing"],created_by=employee_id,created_date=datetime.now(),entity_id=self._entity_id(),date=data["date"])
        else:
            cal = clients_details_date.objects.using(self._current_app_schema()).get(activeclient_id=active_clie_id,
                                                                                       date=data["date"])
            new_client = cal.new_client + data["New"]
            bop = cal.bop + data["BOP"]
            attrition = cal.attrition + data["Attrition"]
            closing_new = (new_client + bop) - attrition
            update_mon = clients_details_date.objects.using(self._current_app_schema()).filter(
                activeclient_id=active_clie_id).update(bop=F('bop') + data["BOP"], new_client=new_client,
                                                           attrition=attrition, closing=closing_new,
                                                           updated_by=employee_id, updated_date=datetime.now(),
                                                           entity_id=self._entity_id())


    def income_header_date(self,body,employee_id):
        try:
            condition = Q(date__date__range=(body["fromdate"], body["todate"]))
            if body["business_id"]!=4:
                condition = Q(activeclient__business_id=body["business_id"])
                if "product_id" not in body:
                    if "Rm_id" in body and "client_id" in body and "assest_class" in body:
                        rm = self.client_get(body["Rm_id"])
                        rm.append(body["client_id"])
                        condition &= Q(activeclient__product_id=None, activeclient__client_id__in=rm,
                                       activeclient__assest_class__in=body["assest_class"])
                    elif "Rm_id" in body and "client_id" in body and "assest_class" not in body:
                        rm = self.client_get(body["Rm_id"])
                        rm.append(body["client_id"])
                        condition &= Q(activeclient__product_id=None, activeclient__client_id__in=rm)
                    elif "Rm_id" in body and "client_id" not in body and "assest_class" in body:
                        rm = self.client_get(body["Rm_id"])
                        condition &= Q(activeclient__product_id=None, activeclient__client_id__in=rm,
                                       activeclient__assest_class__in=body["assest_class"])
                    elif "Rm_id" in body and "client_id" not in body and "assest_class" not in body:
                        rm = self.client_get(body["Rm_id"])
                        condition &= Q(activeclient__product_id=None, activeclient__client_id__in=rm)
                    elif "Rm_id" not in body and "client_id" in body and "assest_class" in body:
                        condition &= Q(activeclient__product_id=None, activeclient__client_id=body["client_id"])
                    elif "Rm_id" not in body and "client_id" in body and "assest_class" not in body:
                        condition &= Q(activeclient__product_id=None, activeclient__client_id=body["client_id"],
                                       activeclient__assest_class__in=body["assest_class"])
                    elif "Rm_id" not in body and "client_id" not in body and "assest_class" not in body:
                        # condition &= Q(activeclient__product_id=None, activeclient__client_id=None)
                        condition &= Q(activeclient__product_id=None, activeclient__client_id=None)
                        condition &= ~Q(activeclient__assest_class=None)

                    elif "Rm_id" not in body and "client_id" not in body and "assest_class" in body:
                        condition &= Q(activeclient__product_id=None, activeclient__client_id=None,
                                       activeclient__assest_class__in=body["assest_class"])


                elif "product_id" in body:
                    # if "client_id" in body:
                    if "Rm_id" in body and "client_id" in body and "assest_class" in body:
                        rm = self.client_get(body["Rm_id"])
                        rm.append(body["client_id"])
                        condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id__in=rm,
                                       activeclient__assest_class__in=body["assest_class"])
                    elif "Rm_id" in body and "client_id" in body and "assest_class" not in body:
                        rm = self.client_get(body["Rm_id"])
                        rm.append(body["client_id"])
                        condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id__in=rm)
                    elif "Rm_id" in body and "client_id" not in body and "assest_class" in body:
                        rm = self.client_get(body["Rm_id"])
                        condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id__in=rm,
                                       activeclient__assest_class__in=body["assest_class"])
                    elif "Rm_id" in body and "client_id" not in body and "assest_class" not in body:
                        rm = self.client_get(body["Rm_id"])
                        condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id__in=rm)
                    elif "Rm_id" not in body and "client_id" in body and "assest_class" in body:
                        condition &= Q(activeclient__product_id=body["product_id"],
                                       activeclient__client_id=body["client_id"])
                    elif "Rm_id" not in body and "client_id" in body and "assest_class" not in body:
                        condition &= Q(activeclient__product_id=body["product_id"],
                                       activeclient__client_id=body["client_id"],
                                       activeclient__assest_class__in=body["assest_class"])
                    elif "Rm_id" not in body and "client_id" not in body and "assest_class" not in body:
                        condition &= Q(activeclient__product_id=body["product_id"])
                    elif "Rm_id" not in body and "client_id" not in body and "assest_class" in body:
                        condition &= Q(activeclient__product_id=body["product_id"],
                                       activeclient__assest_class__in=body["assest_class"])
            else:
                condition &= ~Q(activeclient__business_id=None)
                condition &= ~Q(activeclient__assest_class=None)
                condition &= Q(activeclient__client_id=None)


            income_details=Income_details_date.objects.using(self._current_app_schema()).filter(condition).values("activeclient__assest_class", "activeclient__fee_type").annotate(interest_amount1=Sum("interest_amount"),eir_amount1=Sum("eir_amount"),fee_due1=Sum("fee_due")).values("interest_amount1","eir_amount1","fee_due1","activeclient__fee_type","activeclient__assest_class")

            Interest_income=[]
            Gurantee_fee=[]
            Syndication_fee=[]
            Professional_fee=[]
            Processing_fee=[]
            Preclosure_fee=[]
            resp_list = NWisefinList()
            data1=[]
            data2=[]
            data3=[]
            data4=[]
            data5=[]
            data6=[]
            for i in income_details:

                doc_data = Income_details_response()
                if i["activeclient__fee_type"]==Fees_type.Interest_income:
                    interest_amount=float(i["interest_amount1"])+float(i["eir_amount1"])
                    doc_data.set_amount(interest_amount)

                    # doc_data.set_fee_type(Fees_type.Interest_income_var)
                    # if i.activeclient.flag == Client_flag.OWN:
                    #     doc_data.set_flag(Client_flag.OWN_VAL)
                    # elif i.activeclient.flag == Client_flag.ENABLED:
                    #     doc_data.set_flag(Client_flag.ENABLED_VAL)

                    cls = Asset_class()
                    doc_data.set_assest_class(cls.getasset(i["activeclient__assest_class"]))
                    Interest_income.append(doc_data)
                    data1={"name":Fees_type.Interest_income_var,"value":Interest_income}
                    # resp_list.append(dict)
                    # resp_list.append(data)
                if i["activeclient__fee_type"]==Fees_type.Gurantee_fee:
                    # doc_data.set_fee_type(Fees_type.Gurantee_fee_var)
                    doc_data.set_amount(i["fee_due1"])

                    # if i.activeclient.flag == Client_flag.OWN:
                    #     doc_data.set_flag(Client_flag.OWN_VAL)
                    # elif i.activeclient.flag == Client_flag.ENABLED:
                    #     doc_data.set_flag(Client_flag.ENABLED_VAL)

                    cls = Asset_class()
                    doc_data.set_assest_class(cls.getasset(i["activeclient__assest_class"]))
                    Gurantee_fee.append(doc_data)


                    data2 = {"name": Fees_type.Gurantee_fee_var, "value": Gurantee_fee}
                    # resp_list.append(dict)
                    # resp_list.append(data)
                if i["activeclient__fee_type"]==Fees_type.Syndication_fee:
                    # doc_data.set_fee_type(Fees_type.Syndication_fee_var)
                    doc_data.set_amount(i["fee_due1"])
                    # doc_data = Income_details_response()

                    # if i.activeclient.flag == Client_flag.OWN:
                    #     doc_data.set_flag(Client_flag.OWN_VAL)
                    # elif i.activeclient.flag == Client_flag.ENABLED:
                    #     doc_data.set_flag(Client_flag.ENABLED_VAL)

                    cls = Asset_class()
                    doc_data.set_assest_class(cls.getasset(i["activeclient__assest_class"]))


                    Syndication_fee.append(doc_data)

                    data3 = {"name": Fees_type.Syndication_fee_var, "value": Syndication_fee}

                if i["activeclient__fee_type"]==Fees_type.Professional_fee:
                    # doc_data.set_fee_type(Fees_type.Professional_fee_var)

                    # if i.activeclient.flag == Client_flag.OWN:
                    #     doc_data.set_flag(Client_flag.OWN_VAL)
                    # elif i.activeclient.flag == Client_flag.ENABLED:
                    #     doc_data.set_flag(Client_flag.ENABLED_VAL)
                    doc_data.set_amount(i["fee_due1"])

                    cls = Asset_class()
                    doc_data.set_assest_class(cls.getasset(i["activeclient__assest_class"]))
                    Professional_fee.append(doc_data)
                    data4 = {"name": Fees_type.Professional_fee_var, "value": Professional_fee}
                if i["activeclient__fee_type"] == Fees_type.Preclosure_fee:
                    # doc_data.set_fee_type(Fees_type.Professional_fee_var)

                    # if i.activeclient.flag == Client_flag.OWN:
                    #     doc_data.set_flag(Client_flag.OWN_VAL)
                    # elif i.activeclient.flag == Client_flag.ENABLED:
                    #     doc_data.set_flag(Client_flag.ENABLED_VAL)
                    doc_data.set_amount(i["fee_due1"])

                    cls = Asset_class()
                    doc_data.set_assest_class(cls.getasset(i["activeclient__assest_class"]))
                    Preclosure_fee.append(doc_data)
                    data5 = {"name": Fees_type.Preclosure_fee_var, "value": Preclosure_fee}

                if i["activeclient__fee_type"] == Fees_type.Processing_fee:
                    # doc_data.set_fee_type(Fees_type.Professional_fee_var)

                    # if i.activeclient.flag == Client_flag.OWN:
                    #     doc_data.set_flag(Client_flag.OWN_VAL)
                    # elif i.activeclient.flag == Client_flag.ENABLED:
                    #     doc_data.set_flag(Client_flag.ENABLED_VAL)
                    doc_data.set_amount(i["fee_due1"])

                    cls = Asset_class()
                    doc_data.set_assest_class(cls.getasset(i["activeclient__assest_class"]))
                    Processing_fee.append(doc_data)
                    data6 = {"name": Fees_type.Processing_fee_var, "value": Processing_fee}


            if len(data1)!=0:
                resp_list.append(data1)
            if len(data2) != 0:
                resp_list.append(data2)
            if len(data3)!=0:
                resp_list.append(data3)
            if len(data4)!=0:
                resp_list.append(data4)
            if len(data5)!=0:
                resp_list.append(data5)
            if len(data6)!=0:
                resp_list.append(data6)
            # vpage = NWisefinPaginator(income_details, vys_page.get_index(), 10)
            # resp_list.set_pagination(vpage)
            return resp_list
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            # logger.info('ta_ change_approver- ' + str(e) + str(exc))
            return error_obj

    def get_client(self, assettype_id, query, type, vys_page):
        pro_list = NWisefinList()
        from masterservice.models import Nac_Client
        if type == 'CLIENT':
            client_data = Nac_Client.objects.using(self._current_app_schema()).filter(assettype_id=assettype_id,
                                                                                      client_name__icontains=query,
                                                                                      entity_id=self._entity_id()).values(
                'id', 'client_code', 'client_name')[vys_page.get_offset():vys_page.get_query_limit()]
            for i in client_data:
                pro_list.append(
                    {"client_id": i['id'], "client_name": str(i['client_code']) + '-' + str(i['client_name'])})
            vpage = NWisefinPaginator(client_data, vys_page.get_index(), 10)
            pro_list.set_pagination(vpage)
            return pro_list

        elif type == 'RM':
            rm_arr = []
            # rmdata = USER_SERVICE(self._scope())
            Client_data = Nac_Client.objects.using(self._current_app_schema()).filter(assettype_id=assettype_id,
                                                                                      entity_id=self._entity_id())
            for i in Client_data:
                rm_arr.append(i.rm_name)
            rm = self.get_rm_data(rm_arr, query, vys_page)
            return rm

        else:
            return pro_list

    def get_rm_data(self, filter_obj, query, vys_page):
        arr = NWisefinList()
        from userservice.models import Employee
        emp_obj = Employee.objects.using(self._current_app_schema()).filter(
            (Q(id__in=filter_obj) & (Q(full_name__icontains=query) | Q(code__icontains=query)))).values('id', 'code',
                                                                                                        'full_name',
                                                                                                        'designation')[
                  vys_page.get_offset():vys_page.get_query_limit()]
        for i in emp_obj:
            arr.append({"rm_id": i['id'], "rm_name": str(i['code']) + '-' + str(i['full_name'])})
        vpage = NWisefinPaginator(emp_obj, vys_page.get_index(), 10)
        arr.set_pagination(vpage)
        return arr

    def getclient_id(self,client_name):
        from masterservice.models import Nac_Client
        nac_client=Nac_Client.objects.using(self._current_app_schema()).filter(client_name__icontains=client_name).last()
        client_id=nac_client.id
        return client_id
    def get_buisness_type(self,buisness_type):
        from masterservice.models import MasterBusinessSegment
        buisness_type=MasterBusinessSegment.objects.using(self._current_app_schema()).filter(code__icontains=buisness_type).last()
        buissness_id=buisness_type.id
        return buissness_id

    def get_masterbuisness(self,buisness_name):
        from masterservice.models import MasterBusinessSegment
        buisness_type = MasterBusinessSegment.objects.using(self._current_app_schema()).filter(
            name__icontains=buisness_name)
        arr = NWisefinList()
        for data in buisness_type:
            response=Income_details_response()
            response.set_id(data.id)
            response.set_name(data.name)
            arr.append(response)
        return arr

    def income_Filedownload(self, data, employee_id, scope, vys_page):
        serv = Income_Service(scope)
        client_data = serv.ppractiveclients_date(data)
        header_data = serv.income_amount_date(data, employee_id, 0)
        amount_data = serv.incomeheader_interest_excel(data, employee_id, 0)


        exldata1 = json.dumps(client_data, default=lambda o: o.__dict__)
        exldata2 = json.dumps(header_data, default=lambda o: o.__dict__)
        exldata3 = json.dumps(amount_data, default=lambda o: o.__dict__)
        response_data1 = pd.read_json(json.dumps(json.loads(exldata1)['data']))
        import numpy as np


             # response_data2 = pd.read_json(json.loads(json.loads(exldata2))['data'][0]["assest_class"][i])
        response_data3 = pd.read_json(json.dumps(json.loads(exldata3)['data']))
        XLSX_FORM = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response = HttpResponse(content_type=XLSX_FORM)
        response['Content-Disposition'] = 'attachment; filename="Income_Exception_File.xlsx"'
        writer = pd.ExcelWriter(response, engine='xlsxwriter')
        size=0
        if client_data.data != []:
            # final_df1 = response_data1[
            #     ['asset_name','bop','new_client','attrition','closing']]
            # final_df1.columns = ['Asset Name', 'BOP', 'New Client','Attrition',
            #                      'Closing']
            asset_class=[]
            attrion=[]
            bop=[]
            new_client=[]
            amount=[]
            closing=[]

            for j in range(len(json.loads(exldata1)["data"])):
                asset_class.append((json.loads(exldata1)["data"])[j]["asset_name"])
                attrion.append((json.loads(exldata1)["data"])[j]["attrition"])
                bop.append((json.loads(exldata1)["data"])[j]["bop"])
                new_client.append((json.loads(exldata1)["data"])[j]["new_client"])
                closing.append((json.loads(exldata1)["data"])[j]["closing"])
            response_data1 = np.array([bop,new_client,attrion,closing])
            # columns = json.loads(json.loads(exldata2))['data'][0]["assest_class"]
            df5 = pd.DataFrame(response_data1, columns=asset_class, index=["BOP","New client","Attrition","Closing"])
            df5.to_excel(writer, sheet_name='sheet1', startrow=size)


            # final_df1.to_excel(writer, sheet_name='sheet1',startcol=-1)
            # workbook = writer.book
            # worksheet = writer.sheets['sheet1']
            #
            # header_format = workbook.add_format({
            #     'bold': True,
            #     'fg_color': '21CBE5',
            #     'border': 1})
            # for col_num, value in enumerate(final_df1.columns.values):
            #     worksheet.write(0, col_num, value, header_format)
            #
            #     column_len = final_df1[value].astype(str).str.len().max()
            #     column_len = max(column_len, len(value)) + 3
            #     worksheet.set_column(col_num, col_num, column_len)
            # size = int(len(client_data.data)) + 2
        if len(json.loads(json.loads(exldata2))['data']) != 0:
            size=0
            if int(len(json.loads(json.dumps(json.loads(exldata1)['data']))))!=0:
                size=int(len(json.loads(json.dumps(json.loads(exldata1)['data'])))) + 3
            arr = []
            arr1 = []
            for i in range(len(json.loads(json.loads(exldata2))['data'])):
                value = json.loads(json.loads(exldata2))['data'][i]["value"]
                name = json.loads(json.loads(exldata2))['data'][i]["name"]
                # json.loads(json.loads(exldata2))['data'].insert(1, "Name")
                arr.append(value)
                arr1.append(name)
            response_data2 = np.array(arr)
            columns = json.loads(json.loads(exldata2))['data'][0]["assest_class"]

            df = pd.DataFrame(response_data2, columns=columns, index=arr1)
            # df.index.set_names('Courses_Duration', level=0)
            # print(df)
            # df.rename_axis('Name', inplace=True,axis=0,columns=0)
            # df.index.name = 'Index1'
            # first_idx = df.index[0]
            # last_idx = df.index[-1]

            # df.loc[first_idx, ''] = 'Name'
            # df.loc[last_idx, 'C'] = 'y'
            df.to_excel(writer, sheet_name='sheet1',startrow=size, columns=columns, index=arr1)
            # workbook = writer.book
            # worksheet = writer.sheets['sheet2']
            #
            # header_format = workbook.add_format({
            #     'bold': True,
            #     'fg_color': '21CBE5',
            #     'border': 1})
            # for col_num, value in enumerate(df.columns.values):
            #     worksheet.write(size, col_num, value, header_format)
            #
            #     column_len = df[value].astype(str).str.len().max()
            #     column_len = max(column_len, len(value)) + 3
            #     worksheet.set_column(col_num, col_num, column_len)
        if amount_data.data != []:
            size1=0
            if int(len(json.loads(json.loads(exldata2))["data"]))!=0:
                size1 = int(size)+int(len(json.loads(json.loads(exldata2))["data"]))+ 3
            else:
                size1 = int(len(json.loads(json.dumps(json.loads(exldata1)['data']))))+3

            final_df3 = response_data3[['assest_class', 'fee_type', 'amount']]
            final_df3.columns = ["Asset Name", "Income Type", "Amount"]
            final_df3.to_excel(writer, index=False, sheet_name='sheet1',startrow=size1, startcol=0)
            workbook = writer.book
            worksheet = writer.sheets['sheet1']

            header_format = workbook.add_format({
                'bold': True,
                'fg_color': '21CBE5',
                'border': 1})
            for col_num, value in enumerate(final_df3.columns.values):
                worksheet.write(size1, col_num, value, header_format)

                column_len = final_df3[value].astype(str).str.len().max()
                column_len = max(column_len, len(value)) + 3
                worksheet.set_column(col_num, col_num, column_len)





        writer.save()

        return HttpResponse(response)

    def incomeheader_amt_excel(self, body, employee_id, vys_page):
        condition = Q(date__date__range=(body["fromdate"], body["todate"]),
                      activeclient__business_id=body["business_id"])
        # if "product_id" not in body and "client_id" not in body:
        #     condition&=Q(activeclient__product_id=None,activeclient__client_id=None)
        if "product_id" not in body:
            if "Rm_id" in body and "client_id" in body and "assest_class" in body:
                rm = self.client_get(body["Rm_id"])
                rm.append(body["client_id"])
                condition &= Q(activeclient__product_id=None, activeclient__client_id__in=rm,
                               activeclient__assest_class__in=body["assest_class"])
            elif "Rm_id" in body and "client_id" in body and "assest_class" not in body:
                rm = self.client_get(body["Rm_id"])
                rm.append(body["client_id"])
                condition &= Q(activeclient__product_id=None, activeclient__client_id__in=rm)
            elif "Rm_id" in body and "client_id" not in body and "assest_class" in body:
                rm = self.client_get(body["Rm_id"])
                condition &= Q(activeclient__product_id=None, activeclient__client_id__in=rm,
                               activeclient__assest_class__in=body["assest_class"])
            elif "Rm_id" in body and "client_id" not in body and "assest_class" not in body:
                rm = self.client_get(body["Rm_id"])
                condition &= Q(activeclient__product_id=None, activeclient__client_id__in=rm)
            elif "Rm_id" not in body and "client_id" in body and "assest_class" in body:
                condition &= Q(activeclient__product_id=None, activeclient__client_id=body["client_id"])
            elif "Rm_id" not in body and "client_id" in body and "assest_class" not in body:
                condition &= Q(activeclient__product_id=None, activeclient__client_id=body["client_id"],
                               activeclient__assest_class__in=body["assest_class"])
            elif "Rm_id" not in body and "client_id" not in body and "assest_class" not in body:
                # condition &= Q(activeclient__product_id=None, activeclient__client_id=None)
                condition &= Q(activeclient__product_id=None, activeclient__client_id=None)
                condition &= ~Q(activeclient__assest_class=None)

            elif "Rm_id" not in body and "client_id" not in body and "assest_class" in body:
                condition &= Q(activeclient__product_id=None, activeclient__client_id=None,
                               activeclient__assest_class__in=body["assest_class"])


        elif "product_id" in body:
            # if "client_id" in body:
            if "Rm_id" in body and "client_id" in body and "assest_class" in body:
                rm = self.client_get(body["Rm_id"])
                rm.append(body["client_id"])
                condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id__in=rm,
                               activeclient__assest_class__in=body["assest_class"])
            elif "Rm_id" in body and "client_id" in body and "assest_class" not in body:
                rm = self.client_get(body["Rm_id"])
                rm.append(body["client_id"])
                condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id__in=rm)
            elif "Rm_id" in body and "client_id" not in body and "assest_class" in body:
                rm = self.client_get(body["Rm_id"])
                condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id__in=rm,
                               activeclient__assest_class__in=body["assest_class"])
            elif "Rm_id" in body and "client_id" not in body and "assest_class" not in body:
                rm = self.client_get(body["Rm_id"])
                condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id__in=rm)
            elif "Rm_id" not in body and "client_id" in body and "assest_class" in body:
                condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id=body["client_id"])
            elif "Rm_id" not in body and "client_id" in body and "assest_class" not in body:
                condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id=body["client_id"],
                               activeclient__assest_class__in=body["assest_class"])
            elif "Rm_id" not in body and "client_id" not in body and "assest_class" not in body:
                condition &= Q(activeclient__product_id=body["product_id"])
            elif "Rm_id" not in body and "client_id" not in body and "assest_class" in body:
                condition &= Q(activeclient__product_id=body["product_id"],
                               activeclient__assest_class__in=body["assest_class"])

        # if "product_id" in body:
        #         condition &= Q(activeclient__product_id=body["product_id"])

        income_details = Income_details_date.objects.using(self._current_app_schema()).filter(condition
                                                                                              ).values(
            "activeclient__assest_class", "activeclient__flag").annotate(opening_pos1=Sum("opening_pos"),
                                                                         closing_pos1=Sum("closing_pos"),
                                                                         disbursal_amount1=Sum("disbursal_amount"),
                                                                         total_disbursalamount1=Sum(
                                                                             "total_disbursalamount"),
                                                                         sanctioned_amount1=Sum(
                                                                             "sanctioned_amount")).values(
            "activeclient__assest_class", "activeclient__flag", "opening_pos1", "total_disbursalamount1",
            "disbursal_amount1", "closing_pos1", "sanctioned_amount1")
        arr = NWisefinList()
        for inc_det in income_details:
            doc_data = Income_details_response()
            cls = Asset_class()

            if inc_det["activeclient__flag"] == Client_flag.OWN:
                doc_data.set_flag(Client_flag.OWN_VAL)
                flag_name = Client_flag.OWN_VAL

                assest = (cls.getasset((inc_det["activeclient__assest_class"])))
                assest_class_name = str(assest.name) + "-" + Client_flag.OWN_VAL
                disbursal_amount=inc_det["disbursal_amount1"]/10000000
                disbursal_amount =round(disbursal_amount,2)
                total_disbursalamount=inc_det["total_disbursalamount1"]/10000000
                total_disbursalamount = round(total_disbursalamount,2)
                opening_pos=inc_det["opening_pos1"]/10000000
                opening_pos = round(opening_pos,2)

                closing_pos=inc_det["closing_pos1"]/10000000
                closing_pos = round(closing_pos,2)
                volume=inc_det["sanctioned_amount1"]/10000000
                volume = round(volume,2)
                average = (float(inc_det["opening_pos1"]) + float(inc_det["closing_pos1"])) / 2
                average=average/10000000
                average=round(average,2)
                if (opening_pos) != 0:
                    growth = ((float(inc_det["closing_pos1"]) - float(inc_det["opening_pos1"])) / (float(inc_det["opening_pos1"]))) * 100
                    # growth=growth/10000000

                else:
                    growth = 0.000
                growth=round(growth,2)
                doc_data.set_disbursal_amount(disbursal_amount)
                doc_data.set_total_disbursalamount(total_disbursalamount)
                doc_data.set_opening_pos(opening_pos)
                doc_data.set_closing_pos(closing_pos)
                doc_data.set_volume(volume)
                doc_data.set_average(average)
                doc_data.set_growth(growth)
                doc_data.set_assest_class(assest_class_name)
                doc_data.set_assest_id(assest.id)


            elif inc_det["activeclient__flag"] == Client_flag.ENABLED:
                doc_data.set_flag(Client_flag.ENABLED_VAL)
                flag_name = Client_flag.ENABLED_VAL
                assest = (cls.getasset((inc_det["activeclient__assest_class"])))
                assest_class_name = str(assest.name) + "-" + Client_flag.OWN_VAL
                disbursal_amount = inc_det["disbursal_amount1"] / 10000000
                disbursal_amount = round(disbursal_amount, 2)
                total_disbursalamount = inc_det["total_disbursalamount1"] / 10000000
                total_disbursalamount = round(total_disbursalamount, 2)
                opening_pos = inc_det["opening_pos1"] / 10000000
                opening_pos = round(opening_pos, 2)

                closing_pos = inc_det["closing_pos1"] / 10000000
                closing_pos = round(closing_pos, 2)
                volume = inc_det["sanctioned_amount1"] / 10000000
                volume = round(volume, 2)
                average = (float(inc_det["opening_pos1"]) + float(inc_det["closing_pos1"])) / 2
                average = average / 10000000
                average = round(average, 2)
                if (opening_pos) != 0:
                    growth = ((float(inc_det["closing_pos1"]) - float(inc_det["opening_pos1"])) / (
                        float(inc_det["opening_pos1"]))) * 100
                    # growth = growth / 10000000

                else:
                    growth = 0.000
                growth = round(growth, 2)
                doc_data.set_disbursal_amount(disbursal_amount)
                doc_data.set_total_disbursalamount(total_disbursalamount)
                doc_data.set_opening_pos(opening_pos)
                doc_data.set_closing_pos(closing_pos)
                doc_data.set_volume(volume)
                doc_data.set_average(average)
                doc_data.set_growth(growth)
                doc_data.set_assest_class(assest_class_name)
                doc_data.set_assest_id(assest.id)
            arr.append(doc_data)
        return arr

    def incomeheader_interest_excel(self, body, employee_id, vys_page):
        condition = Q(date__date__range=(body["fromdate"], body["todate"]))
        if int(body["business_id"]) != 4:
            condition&=Q(activeclient__business_id=body["business_id"])
            if "product_id" not in body:
                if "Rm_id" in body and "client_id" in body and "assest_class" in body:
                    rm = self.client_get(body["Rm_id"])
                    rm.append(body["client_id"])
                    condition &= Q(activeclient__product_id=None, activeclient__client_id__in=rm,
                                   activeclient__assest_class__in=body["assest_class"])
                elif "Rm_id" in body and "client_id" in body and "assest_class" not in body:
                    rm = self.client_get(body["Rm_id"])
                    rm.append(body["client_id"])
                    condition &= Q(activeclient__product_id=None, activeclient__client_id__in=rm)
                elif "Rm_id" in body and "client_id" not in body and "assest_class" in body:
                    rm = self.client_get(body["Rm_id"])
                    condition &= Q(activeclient__product_id=None, activeclient__client_id__in=rm,
                                   activeclient__assest_class__in=body["assest_class"])
                elif "Rm_id" in body and "client_id" not in body and "assest_class" not in body:
                    rm = self.client_get(body["Rm_id"])
                    condition &= Q(activeclient__product_id=None, activeclient__client_id__in=rm)
                elif "Rm_id" not in body and "client_id" in body and "assest_class" in body:
                    condition &= Q(activeclient__product_id=None, activeclient__client_id=body["client_id"])
                elif "Rm_id" not in body and "client_id" in body and "assest_class" not in body:
                    condition &= Q(activeclient__product_id=None, activeclient__client_id=body["client_id"],
                                   activeclient__assest_class__in=body["assest_class"])
                elif "Rm_id" not in body and "client_id" not in body and "assest_class" not in body:
                    # condition &= Q(activeclient__product_id=None, activeclient__client_id=None)
                    condition &= Q(activeclient__product_id=None, activeclient__client_id=None)
                    condition &= ~Q(activeclient__assest_class=None)

                elif "Rm_id" not in body and "client_id" not in body and "assest_class" in body:
                    condition &= Q(activeclient__product_id=None, activeclient__client_id=None,
                                   activeclient__assest_class__in=body["assest_class"])


            elif "product_id" in body:
                # if "client_id" in body:
                if "Rm_id" in body and "client_id" in body and "assest_class" in body:
                    rm = self.client_get(body["Rm_id"])
                    rm.append(body["client_id"])
                    condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id__in=rm,
                                   activeclient__assest_class__in=body["assest_class"])
                elif "Rm_id" in body and "client_id" in body and "assest_class" not in body:
                    rm = self.client_get(body["Rm_id"])
                    rm.append(body["client_id"])
                    condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id__in=rm)
                elif "Rm_id" in body and "client_id" not in body and "assest_class" in body:
                    rm = self.client_get(body["Rm_id"])
                    condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id__in=rm,
                                   activeclient__assest_class__in=body["assest_class"])
                elif "Rm_id" in body and "client_id" not in body and "assest_class" not in body:
                    rm = self.client_get(body["Rm_id"])
                    condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id__in=rm)
                elif "Rm_id" not in body and "client_id" in body and "assest_class" in body:
                    condition &= Q(activeclient__product_id=body["product_id"],
                                   activeclient__client_id=body["client_id"])
                elif "Rm_id" not in body and "client_id" in body and "assest_class" not in body:
                    condition &= Q(activeclient__product_id=body["product_id"],
                                   activeclient__client_id=body["client_id"],
                                   activeclient__assest_class__in=body["assest_class"])
                elif "Rm_id" not in body and "client_id" not in body and "assest_class" not in body:
                    condition &= Q(activeclient__product_id=body["product_id"])
                elif "Rm_id" not in body and "client_id" not in body and "assest_class" in body:
                    condition &= Q(activeclient__product_id=body["product_id"],
                                   activeclient__assest_class__in=body["assest_class"])


        else:
            condition &= ~Q(activeclient__business_id=None)
            condition &= ~Q(activeclient__assest_class=None)
            condition &= Q(activeclient__client_id=None)
        income_details = Income_details_date.objects.using(self._current_app_schema()).filter(condition).values(
            "activeclient__assest_class", "activeclient__fee_type").annotate(interest_amount1=Sum("interest_amount"),
                                                                             eir_amount1=Sum("eir_amount"),
                                                                             fee_due1=Sum("fee_due")).values(
            "interest_amount1", "eir_amount1", "fee_due1", "activeclient__fee_type", "activeclient__assest_class")

        arr = NWisefinList()
        for i in income_details:
            doc_data = Income_details_response()
            if i["activeclient__fee_type"] == Fees_type.Interest_income:
                interest_amount = float(i["interest_amount1"]) + float(i["eir_amount1"])
                interest_amount = interest_amount / 10000000
                interest_amount = round(interest_amount, 2)
                doc_data.set_amount(interest_amount)
                cls = Asset_class()
                asset_name = (cls.getasset(i["activeclient__assest_class"])).name
                doc_data.set_assest_class(asset_name)
                doc_data.set_fee_type(Fees_type.Interest_income_var)
            elif i["activeclient__fee_type"] == Fees_type.Gurantee_fee:
                interest_amount = float(i["interest_amount1"]) + float(i["eir_amount1"])
                interest_amount = interest_amount / 10000000
                interest_amount=round(interest_amount,2)
                doc_data.set_amount(interest_amount)
                cls = Asset_class()
                asset_name = (cls.getasset(i["activeclient__assest_class"])).name
                doc_data.set_assest_class(asset_name)
                doc_data.set_fee_type(Fees_type.Gurantee_fee_var)

            elif i["activeclient__fee_type"] == Fees_type.Professional_fee:
                interest_amount = float(i["interest_amount1"]) + float(i["eir_amount1"])
                interest_amount = interest_amount / 10000000
                interest_amount = round(interest_amount, 2)
                doc_data.set_amount(interest_amount)
                cls = Asset_class()
                asset_name = (cls.getasset(i["activeclient__assest_class"])).name
                doc_data.set_assest_class(asset_name)
                doc_data.set_fee_type(Fees_type.Professional_fee_var)
            elif i["activeclient__fee_type"] == Fees_type.Syndication_fee:
                interest_amount = float(i["interest_amount1"]) + float(i["eir_amount1"])
                interest_amount=interest_amount/10000000
                interest_amount = round(interest_amount, 2)
                doc_data.set_amount(interest_amount)
                cls = Asset_class()
                asset_name = (cls.getasset(i["activeclient__assest_class"])).name
                doc_data.set_assest_class(asset_name)
                doc_data.set_fee_type(Fees_type.Syndication_fee_var)
            elif i["activeclient__fee_type"] == Fees_type.Preclosure_fee:
                interest_amount = float(i["interest_amount1"]) + float(i["eir_amount1"])
                interest_amount=interest_amount/10000000
                interest_amount = round(interest_amount, 2)
                doc_data.set_amount(interest_amount)
                cls = Asset_class()
                asset_name = (cls.getasset(i["activeclient__assest_class"])).name
                doc_data.set_assest_class(asset_name)
                doc_data.set_fee_type(Fees_type.Preclosure_fee_var)
            elif i["activeclient__fee_type"] == Fees_type.Processing_fee:
                interest_amount = float(i["interest_amount1"]) + float(i["eir_amount1"])
                interest_amount=interest_amount/10000000
                interest_amount = round(interest_amount, 2)
                doc_data.set_amount(interest_amount)
                cls = Asset_class()
                asset_name = (cls.getasset(i["activeclient__assest_class"])).name
                doc_data.set_assest_class(asset_name)
                doc_data.set_fee_type(Fees_type.Processing_fee_var)

            arr.append(doc_data)
        return arr

    def ppractiveclients_date_excel(self, body):
        pro_list = NWisefinList()
        pprutility = Asset_class()
        if "assest_class" in body:
            condition = Q(activeclient__asset_id__in=body["assest_class"],
                          date__date__range=(body["fromdate"], body["todate"]))
            # if "product_id" not in body and "client_id" not in body:
            #     condition&=Q(activeclient__product_id=None,activeclient__client_id=None)
            if "product_id" not in body:
                if "Rm_id" in body and "client_id" in body:
                    rm = self.client_get(body["Rm_id"])
                    rm.append(body["client_id"])
                    condition &= Q(activeclient__product_id=None, activeclient__client_id__in=rm)
                elif "Rm_id" in body and "client_id" not in body:
                    rm = self.client_get(body["Rm_id"])
                    condition &= Q(activeclient__product_id=None, activeclient__client_id__in=rm)
                elif "Rm_id" not in body and "client_id" in body:
                    condition &= Q(activeclient__product_id=None, activeclient__client_id=body["client_id"])
                # else:
                    # condition &= Q(activeclient__product_id=None, activeclient__client_id=None)


            elif "product_id" in body:
                # if "client_id" in body:
                if "Rm_id" in body and "client_id" in body:
                    rm = self.client_get(body["Rm_id"])
                    rm.append(body["client_id"])
                    condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id__in=rm)
                elif "Rm_id" in body and "client_id" not in body:
                    rm = self.client_get(body["Rm_id"])
                    condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id__in=rm)
                elif "Rm_id" not in body and "client_id" in body:
                    condition &= Q(activeclient__product_id=body["product_id"], activeclient__client_id=body["client_id"])
                    # condition &= Q(activeclient__product_id=body["product_id"],activeclient__client_id=body["client_id"])
                else:
                    condition &= Q(activeclient__product_id=body["product_id"])
        else:
            condition = Q(date__date__range=(body["fromdate"], body["todate"]))

        get_clients = clients_details_date.objects.using(self._current_app_schema()).filter(condition).values(
            "status", "activeclient__asset_id", "amount").annotate(bop1=Sum('bop'),
                                                                            new_client1=Sum('new_client'),
                                                                            attrition1=Sum('attrition'),
                                                                            closing1=Sum('closing'))
        for i in get_clients:
            fetch_data = ppr_clientresponse()
            asset_var = pprutility.getasset(int(i["activeclient__asset_id"]))
            fetch_data.set_asset_id(asset_var.id)
            fetch_data.set_asset_name(asset_var.name)
            # fetch_data.set_month(i["month"])
            fetch_data.set_attrition(i["attrition1"])
            fetch_data.set_bop(i["bop1"])
            fetch_data.set_new_client(i["new_client1"])
            amount=i["amount"]/10000000
            amount=round(amount,2)
            fetch_data.set_amount(amount)
            fetch_data.set_closing(i["closing1"])
            fetch_data.set_status(i["status"])
            pro_list.append(fetch_data)
        return pro_list

    def insert_ppr_sources(self, ppr_obj, emp_id):
        ppr_response = ppr_source_response()
        if ppr_obj.get_id() is None:
            source_obj = Ppr_Sources.objects.using(self._current_app_schema()).create(
            code=ppr_obj.get_code(),
            name=ppr_obj.get_name(),
            created_by=emp_id,
            entity_id=self._entity_id())
            code_gen = "C00" + str(source_obj.id)
            var = Ppr_Sources.objects.filter(id=source_obj.id).update(code=code_gen)
        else:
            source_obj = Ppr_Sources.objects.filter(id=ppr_obj.get_id()).update(
                                                                            name=ppr_obj.get_name(),
                                                                            updated_by=emp_id,
                                                                            updated_date=datetime.now(),
                                                                            entity_id=self._entity_id())
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def insert_head_groups(self, ppr_obj, emp_id):
        ppr_response = ppr_source_response()
        if ppr_obj.get_id() is None:
            headgrp_obj = Head_Groups.objects.using(self._current_app_schema()).create(
            source_id=ppr_obj.get_source(),
            code=ppr_obj.get_code(),
            name=ppr_obj.get_name(),
            description=ppr_obj.get_description(),
            created_by=emp_id,
            entity_id=self._entity_id())
            code_gen = "C00" + str(headgrp_obj.id)
            var = Head_Groups.objects.filter(id=headgrp_obj.id).update(code=code_gen)
        else:
            headgrp_obj = Head_Groups.objects.filter(id=ppr_obj.get_id()).update(
                                                                                name=ppr_obj.get_name(),
                                                                                source_id=ppr_obj.get_source(),
                                                                                description=ppr_obj.get_description(),
                                                                                updated_by=emp_id,
                                                                                updated_date=datetime.now(),
                                                                                entity_id=self._entity_id())
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def insert_sub_groups(self, ppr_obj, emp_id):
        ppr_response = ppr_source_response()
        if ppr_obj.get_id() is None:
            subgrp_obj = Sub_Groups.objects.using(self._current_app_schema()).create(
                head_group_id=ppr_obj.get_head_group(),
                code=ppr_obj.get_code(),
                name=ppr_obj.get_name(),
                description=ppr_obj.get_description(),
                gl_no=ppr_obj.get_gl_no(),
                created_by=emp_id,
                entity_id=self._entity_id())
            code_gen = "C00" + str(subgrp_obj.id)
            var = Sub_Groups.objects.filter(id=subgrp_obj.id).update(code=code_gen)
        else:
            subgrp_obj = Sub_Groups.objects.filter(id=ppr_obj.get_id()).update(
                                                                                name=ppr_obj.get_name(),
                                                                                description=ppr_obj.get_description(),
                                                                                head_group_id=ppr_obj.get_head_group(),
                                                                                gl_no=ppr_obj.get_gl_no(),
                                                                                updated_by=emp_id,
                                                                                updated_date=datetime.now(),
                                                                                entity_id=self._entity_id())
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def fetch_pprsources_list(self, filter_obj,vys_page):
        condition = Q(status=1)
        if filter_obj.get_name() != None and filter_obj.get_name() != '':
            condition &= Q(name=filter_obj.get_name())
        if filter_obj.get_code() != None and filter_obj.get_code() != '':
            condition &= Q(code=filter_obj.get_code())
        source_obj = Ppr_Sources.objects.using(self._current_app_schema()).filter(condition).values(
                                                                        "id","code","name")[
                     vys_page.get_offset():vys_page.get_query_limit()]
        pro_list = NWisefinList()
        if len(source_obj) <= 0:
            return pro_list
        else:
            for i in source_obj:
                ppr_response = ppr_source_response()
                ppr_response.set_id(i["id"])
                ppr_response.set_name(i["code"])
                ppr_response.set_code(i["name"])
                pro_list.append(ppr_response)
                vpage = NWisefinPaginator(source_obj, vys_page.get_index(), 10)
                pro_list.set_pagination(vpage)
            return pro_list

    def fetch_headgrps_list(self, filter_obj,vys_page):
        condition = Q(status=1)
        if filter_obj.get_source() != None and filter_obj.get_source() != '':
            condition &= Q(source_id=filter_obj.get_source())
        if filter_obj.get_name() != None and filter_obj.get_name() != '':
            condition &= Q(name=filter_obj.get_name())
        if filter_obj.get_code() != None and filter_obj.get_code() != '':
            condition &= Q(code=filter_obj.get_code())
        headgrp_obj = Head_Groups.objects.using(self._current_app_schema()).filter(condition).values(
                                            "id","name","code","description","source__id","source__name")[
                     vys_page.get_offset():vys_page.get_query_limit()]
        pro_list = NWisefinList()
        if len(headgrp_obj) <= 0:
            return pro_list
        else:
            for i in headgrp_obj:
                ppr_response = ppr_source_response()
                ppr_response.set_id(i["id"])
                ppr_response.set_name(i["code"])
                ppr_response.set_code(i["name"])
                ppr_response.set_description(i["description"])
                ppr_response.set_source_id(i["source__id"])
                ppr_response.set_source_name(i["source__name"])
                pro_list.append(ppr_response)
                vpage = NWisefinPaginator(headgrp_obj, vys_page.get_index(), 10)
                pro_list.set_pagination(vpage)
            return pro_list

    def fetch_subgrps_list(self, filter_obj,vys_page):
        condition = Q(status=1)
        if filter_obj.get_head_group() != None and filter_obj.get_head_group() != '':
            condition &= Q(head_group_id=filter_obj.get_head_group())
        if filter_obj.get_name() != None and filter_obj.get_name() != '':
            condition &= Q(name=filter_obj.get_name())
        if filter_obj.get_code() != None and filter_obj.get_code() != '':
            condition &= Q(code=filter_obj.get_code())
        if filter_obj.get_gl_no() != None and filter_obj.get_gl_no() != '':
            condition &= Q(gl_no=filter_obj.get_gl_no())
        subgrp_obj = Sub_Groups.objects.using(self._current_app_schema()).filter(condition).values(
                    "id", "name", "code", "description", "head_group__id", "head_group__name","gl_no")[
                     vys_page.get_offset():vys_page.get_query_limit()]
        pro_list = NWisefinList()
        if len(subgrp_obj) <= 0:
            return pro_list
        else:
            for i in subgrp_obj:
                ppr_response = ppr_source_response()
                ppr_response.set_id(i["id"])
                ppr_response.set_name(i["name"])
                ppr_response.set_code(i["code"])
                ppr_response.set_description(i["description"])
                ppr_response.set_head_group_id(i["head_group__id"])
                ppr_response.set_head_group_name(i["head_group__name"])
                ppr_response.set_gl_no(i["gl_no"])
                pro_list.append(ppr_response)
                vpage = NWisefinPaginator(subgrp_obj, vys_page.get_index(), 10)
                pro_list.set_pagination(vpage)
            return pro_list

    def insert_GL_subgrp(self, ppr_obj, emp_id):
        ppr_response = ppr_source_response()
        if ppr_obj.get_id() is None:
            subgrp_obj = GL_Subgroup.objects.using(self._current_app_schema()).create(
                head_group_id=ppr_obj.get_head_group(),
                gl_no=ppr_obj.get_gl_no(),
                description=ppr_obj.get_description(),
                created_by=emp_id,
                entity_id=self._entity_id())
        else:
            subgrp_obj = GL_Subgroup.objects.filter(id=ppr_obj.get_id()).update(head_group_id=ppr_obj.get_head_group(),
                                                                                gl_no=ppr_obj.get_gl_no(),
                                                                                description=ppr_obj.get_description(),
                                                                                updated_by=emp_id,
                                                                                updated_date=datetime.now(),
                                                                                entity_id=self._entity_id())
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def fetch_GL_subgrp_list(self, filter_obj,vys_page):
        condition = Q(status=1)
        if filter_obj.get_head_group() != None and filter_obj.get_head_group() != '':
            condition &= Q(head_group_id=filter_obj.get_head_group())
        if filter_obj.get_gl_no() != None and filter_obj.get_gl_no() != '':
            condition &= Q(gl_no=filter_obj.get_gl_no())
        subgrp_obj = GL_Subgroup.objects.using(self._current_app_schema()).filter(condition).values(
            "id","description", "head_group__id", "head_group__name","gl_no")[
                     vys_page.get_offset():vys_page.get_query_limit()]
        pro_list = NWisefinList()
        if len(subgrp_obj) <= 0:
            return pro_list
        else:
            for i in subgrp_obj:
                ppr_response = ppr_source_response()
                ppr_response.set_id(i["id"])
                ppr_response.set_head_group_id(i["head_group__id"])
                ppr_response.set_head_group_name(i["head_group__name"])
                ppr_response.set_gl_no(i["gl_no"])
                ppr_response.set_description(i["description"])
                pro_list.append(ppr_response)
                vpage = NWisefinPaginator(subgrp_obj, vys_page.get_index(), 10)
                pro_list.set_pagination(vpage)
            return pro_list


    def get_source_list(self,vys_page,query):
        condition = Q(status=1)
        pro_list = NWisefinList()
        if query != None:
            condition &= Q(name__icontains=query)|Q(code__icontains=query)
        source_var = Ppr_Sources.objects.using(self._current_app_schema()).filter(condition).values(
                                                                                'id','name','code')[
                     vys_page.get_offset():vys_page.get_query_limit()]
        if len(source_var) <= 0:
            return pro_list
        else:
            for i in source_var:
                ppr_response = ppr_source_response()
                ppr_response.set_id(i['id'])
                ppr_response.set_name(i["name"])
                ppr_response.set_code(i['code'])
                pro_list.append(ppr_response)
                vpage = NWisefinPaginator(source_var, vys_page.get_index(), 10)
                pro_list.set_pagination(vpage)
            return pro_list

    def get_headgrp_list(self,vys_page,query):
        condition = Q(status=1)
        pro_list = NWisefinList()
        if query != None:
            condition &= Q(name__icontains=query)|Q(code__icontains=query)
        source_var = Head_Groups.objects.using(self._current_app_schema()).filter(condition).values(
                                                                                'id','name','code')[
                     vys_page.get_offset():vys_page.get_query_limit()]
        if len(source_var) <= 0:
            return pro_list
        else:
            for i in source_var:
                ppr_response = ppr_source_response()
                ppr_response.set_id(i['id'])
                ppr_response.set_name(i['name'])
                ppr_response.set_code(i['code'])
                pro_list.append(ppr_response)
                vpage = NWisefinPaginator(source_var, vys_page.get_index(), 10)
                pro_list.set_pagination(vpage)
            return pro_list

    def get_subgrp_list(self,vys_page,query):
        condition = Q(status=1)
        pro_list = NWisefinList()
        if query != None:
            condition &= Q(name__icontains=query)|Q(code__icontains=query)
        source_var = Sub_Groups.objects.using(self._current_app_schema()).filter(condition).values(
                                                                                'id','name','code')[
                     vys_page.get_offset():vys_page.get_query_limit()]
        if len(source_var) <= 0:
            return pro_list
        else:
            for i in source_var:
                ppr_response = ppr_source_response()
                ppr_response.set_id(i['id'])
                ppr_response.set_name(i['name'])
                ppr_response.set_code(i['code'])
                pro_list.append(ppr_response)
                vpage = NWisefinPaginator(source_var, vys_page.get_index(), 10)
                pro_list.set_pagination(vpage)
            return pro_list

    def get_glsubgrp_list(self,vys_page,query):
        condition = Q(status=1)
        pro_list = NWisefinList()
        if query != None:
            condition &= Q(gl_no__icontains=query)
        source_var = GL_Subgroup.objects.using(self._current_app_schema()).filter(condition).values(
                                                                                'id','gl_no')[
                     vys_page.get_offset():vys_page.get_query_limit()]
        if len(source_var) <= 0:
            return pro_list
        else:
            for i in source_var:
                ppr_response = ppr_source_response()
                ppr_response.set_id(i['id'])
                ppr_response.set_name(i['gl_no'])
                pro_list.append(ppr_response)
                vpage = NWisefinPaginator(source_var, vys_page.get_index(), 10)
                pro_list.set_pagination(vpage)
            return pro_list

    def ppr_incomegrp_logic(self,filter_obj):
        masterservice=MASTER_SERVICE(self._scope())
        user_service = USER_SERVICE(self._scope())
        condition = Q(status=1)
        if filter_obj.get_from_date() != None and filter_obj.get_from_date() != "" and filter_obj.get_to_date() != None and filter_obj.get_to_date() != "":
            condition &= Q(date__range=[filter_obj.get_from_date(),filter_obj.get_to_date()])
        if filter_obj.get_business_id() != 4:
            if filter_obj.get_asset_id() != None and filter_obj.get_asset_id() != "" and len(filter_obj.get_asset_id()) != 0:
                condition &= Q(activeclient__assest_class__in=filter_obj.get_asset_id())
            else:
                condition &= ~Q(activeclient__assest_class=None)
            if filter_obj.get_Rm_id() != None and filter_obj.get_Rm_id() != "":
                rm = self.client_get(filter_obj.get_Rm_id())
                rm.append(filter_obj.get_client_id())
            if filter_obj.get_client_id() != None and filter_obj.get_client_id() != "" :
                condition &= Q(activeclient__client_id=filter_obj.get_client_id())
            else:
                condition &= Q(activeclient__client_id=None)
            if filter_obj.get_product_id() != None and filter_obj.get_product_id() != "" :
                condition &= Q(activeclient__product_id=filter_obj.get_product_id())
            else:
                condition &= Q(activeclient__product_id=None)
            if filter_obj.get_business_id() != None and filter_obj.get_business_id() != "" :
                condition &= Q(activeclient__business_id=filter_obj.get_business_id())
            else:
                condition &= Q(activeclient__business_id=None)
        else:
            condition &= ~Q(activeclient__business_id=None)
            condition &= ~Q(activeclient__assest_class=None)
            condition &= ~Q(activeclient__client_id=None)
            condition &= ~Q(activeclient__product_id=None)
        filter_var  = Income_details_date.objects.using(self._current_app_schema()).filter(condition).values("interest_gl","activeclient__assest_class").annotate(interest_amount=Sum("fee_due"))\
                                                                        .values("activeclient__business_id","interest_gl",
                                                                                "activeclient__assest_class","interest_amount",
                                                                                "activeclient__client_id",
                                                                                "activeclient__product_id")
        prolist = NWisefinList()
        if len(filter_var) == 0:
            return prolist
        else:
            for data in filter_var:
                ppr_response = Income_details_response()
                ppr_response.set_interest_amount(data["interest_amount"])
                ppr_response.set_interest_gl(data["interest_gl"])
                exp_dtls = APsubcategory.objects.using(self._current_app_schema()).filter(glno=data["interest_gl"]).values("glno","category__expense__exp_grp_id")
                exp_dtls = masterservice.get_subcat_expgrp(data["interest_gl"])
                for j in exp_dtls:
                    expgrp_dtls = masterservice.get_expense_grp(j['category__expense__exp_grp_id'])
                    # expgrp_dtls = APexpensegroup.objects.using(self._current_app_schema()).filter(id=j["category__expense__exp_grp_id"]).values("id","name")
                    for i in expgrp_dtls:
                        ppr_response.set_id(i["id"])
                        ppr_response.set_name(i["name"])
                user_dtls = user_service.get_BS([data["activeclient__assest_class"]])
                ppr_response.set_assest_class(user_dtls[0]["name"])
                # if data["activeclient__assest_class"] == Asset_class.AGRI:
                #     ppr_response.set_assest_class(Asset_class.AGRI_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.BD:
                #     ppr_response.set_assest_class(Asset_class.BD_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.CC:
                #     ppr_response.set_assest_class(Asset_class.CC_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.CF:
                #     ppr_response.set_assest_class(Asset_class.CF_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.CL:
                #     ppr_response.set_assest_class(Asset_class.CL_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.AHF:
                #     ppr_response.set_assest_class(Asset_class.AHF_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.CONS:
                #     ppr_response.set_assest_class(Asset_class.CONS_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.CORP:
                #     ppr_response.set_assest_class(Asset_class.CORP_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.INTER_COMPANY:
                #     ppr_response.set_assest_class(Asset_class.INTER_COMPANY_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.MFI:
                #     ppr_response.set_assest_class(Asset_class.MFI_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.OTH:
                #     ppr_response.set_assest_class(Asset_class.OTH_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.SBL:
                #     ppr_response.set_assest_class(Asset_class.SBL_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.VF:
                #     ppr_response.set_assest_class(Asset_class.VF_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.Consumer_Finance:
                #     ppr_response.set_assest_class(Asset_class.Consumer_Finance_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.Gold_Loans:
                #     ppr_response.set_assest_class(Asset_class.Gold_Loans_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.CV:
                #     ppr_response.set_assest_class(Asset_class.CV_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.VL:
                #     ppr_response.set_assest_class(Asset_class.VL_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.SME:
                #     ppr_response.set_assest_class(Asset_class.SME_VAL)
                prolist.append(ppr_response)
        return prolist

    def ppr_incomehead_logic(self,filter_obj):
        masterservice=MASTER_SERVICE(self._scope())
        user_service = USER_SERVICE(self._scope())
        # exp = pprservice_expense.objects.values_list('expensegrp_id', flat=True).distinct
        where_gl = masterservice.get_subcatgl_exphead(filter_obj.get_id())
        gl_arr = []
        for x in where_gl:
            gl_arr.append(x)
        condition = Q(status=1)
        if filter_obj.get_from_date() != None and filter_obj.get_from_date() != "" and filter_obj.get_to_date() != None and filter_obj.get_to_date() != "":
            condition &= Q(date__range=[filter_obj.get_from_date(),filter_obj.get_to_date()])
        if filter_obj.get_business_id() != 4:
            if filter_obj.get_asset_id() != None and filter_obj.get_asset_id() != "" and len(filter_obj.get_asset_id()) != 0:
                condition &= Q(activeclient__assest_class__in=filter_obj.get_asset_id())
            else:
                condition &= ~Q(activeclient__assest_class=None)
            if filter_obj.get_Rm_id() != None and filter_obj.get_Rm_id() != "":
                rm = self.client_get(filter_obj.get_Rm_id())
                rm.append(filter_obj.get_client_id())
            if filter_obj.get_client_id() != None and filter_obj.get_client_id() != "":
                condition &= Q(activeclient__client_id=filter_obj.get_client_id())
            else:
                condition &= Q(activeclient__client_id=None)
            if filter_obj.get_product_id() != None and filter_obj.get_product_id() != "":
                condition &= Q(activeclient__product_id=filter_obj.get_product_id())
            else:
                condition &= Q(activeclient__product_id=None)
            if filter_obj.get_business_id() != None and filter_obj.get_business_id() != "":
                condition &= Q(activeclient__business_id=filter_obj.get_business_id())
            else:
                condition &= Q(activeclient__business_id=None)
        else:
            condition &= ~Q(activeclient__business_id=None)
            condition &= ~Q(activeclient__assest_class=None)
            condition &= ~Q(activeclient__client_id=None)
            condition &= ~Q(activeclient__product_id=None)
        condition &= Q(interest_gl__in = gl_arr)
        filter_var = Income_details_date.objects.using(self._current_app_schema()).filter(condition).values("interest_gl","activeclient__assest_class").annotate(interest_amount=Sum("fee_due"))\
                                                                                .values("activeclient__business_id","interest_gl",
                                                                                "activeclient__assest_class","interest_amount",
                                                                                "activeclient__client_id",
                                                                                "activeclient__product_id")
        prolist = NWisefinList()
        if len(filter_var) == 0:
            return prolist
        else:
            for data in filter_var:
                ppr_response = Income_details_response()
                ppr_response.set_interest_amount(data["interest_amount"])
                ppr_response.set_interest_gl(data["interest_gl"])
                if filter_obj.get_id() != None and filter_obj.get_id() != "":
                    # exp_dtls = APsubcategory.objects.using(self._current_app_schema()).filter(glno=data["interest_gl"],category__expense__exp_grp_id=filter_obj.get_id()).values("glno","category__expense__id","category__expense__head")
                    exp_dtls = masterservice.get_subcat_exp(data["interest_gl"],filter_obj.get_id())
                    # for j in exp_dtls:
                    #     expgrp_dtls = masterservice.get_expense_head(j["category__expense__id"])
                    for k in exp_dtls:
                        ppr_response.set_id(k["category__expense__id"])
                        ppr_response.set_name(k["category__expense__head"])
                        ppr_response.set_expensegrp_id(k["category__expense__exp_grp_id"])
                user_dtls = user_service.get_BS([data["activeclient__assest_class"]])
                ppr_response.set_assest_class(user_dtls[0]["name"])
                # if data["activeclient__assest_class"] == Asset_class.AGRI:
                #     ppr_response.set_assest_class(Asset_class.AGRI_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.BD:
                #     ppr_response.set_assest_class(Asset_class.BD_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.CC:
                #     ppr_response.set_assest_class(Asset_class.CC_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.CF:
                #     ppr_response.set_assest_class(Asset_class.CF_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.CL:
                #     ppr_response.set_assest_class(Asset_class.CL_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.AHF:
                #     ppr_response.set_assest_class(Asset_class.AHF_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.CONS:
                #     ppr_response.set_assest_class(Asset_class.CONS_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.CORP:
                #     ppr_response.set_assest_class(Asset_class.CORP_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.INTER_COMPANY:
                #     ppr_response.set_assest_class(Asset_class.INTER_COMPANY_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.MFI:
                #     ppr_response.set_assest_class(Asset_class.MFI_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.OTH:
                #     ppr_response.set_assest_class(Asset_class.OTH_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.SBL:
                #     ppr_response.set_assest_class(Asset_class.SBL_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.VF:
                #     ppr_response.set_assest_class(Asset_class.VF_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.Consumer_Finance:
                #     ppr_response.set_assest_class(Asset_class.Consumer_Finance_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.Gold_Loans:
                #     ppr_response.set_assest_class(Asset_class.Gold_Loans_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.CV:
                #     ppr_response.set_assest_class(Asset_class.CV_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.VL:
                #     ppr_response.set_assest_class(Asset_class.VL_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.SME:
                #     ppr_response.set_assest_class(Asset_class.SME_VAL)
                prolist.append(ppr_response)
        return prolist

    def ppr_incomecat_logic(self,filter_obj):
        masterservice=MASTER_SERVICE(self._scope())
        user_service = USER_SERVICE(self._scope())
        where_gl = masterservice.get_subcatgl_cat(filter_obj.get_expgrp_id(),filter_obj.get_id())
        gl_arr = []
        for x in where_gl:
            gl_arr.append(x)
        condition = Q(status=1)
        if filter_obj.get_from_date() != None and filter_obj.get_from_date() != "" and filter_obj.get_to_date() != None and filter_obj.get_to_date() != "":
            condition &= Q(date__range=[filter_obj.get_from_date(),filter_obj.get_to_date()])
        if filter_obj.get_business_id() != 4:
            if filter_obj.get_asset_id() != None and filter_obj.get_asset_id() != "" and len(filter_obj.get_asset_id()) != 0:
                condition &= Q(activeclient__assest_class__in=filter_obj.get_asset_id())
            else:
                condition &= ~Q(activeclient__assest_class=None)
            if filter_obj.get_Rm_id() != None and filter_obj.get_Rm_id() != "":
                rm = self.client_get(filter_obj.get_Rm_id())
                rm.append(filter_obj.get_client_id())
            if filter_obj.get_client_id() != None and filter_obj.get_client_id() != "" :
                condition &= Q(activeclient__client_id=filter_obj.get_client_id())
            else:
                condition &= Q(activeclient__client_id=None)
            if filter_obj.get_product_id() != None and filter_obj.get_product_id() != "" :
                condition &= Q(activeclient__product_id=filter_obj.get_product_id())
            else:
                condition &= Q(activeclient__product_id=None)
            if filter_obj.get_business_id() != None and filter_obj.get_business_id() != "" :
                condition &= Q(activeclient__business_id=filter_obj.get_business_id())
            else:
                condition &= Q(activeclient__business_id=None)
        else:
            condition &= ~Q(activeclient__business_id=None)
            condition &= ~Q(activeclient__assest_class=None)
            condition &= ~Q(activeclient__client_id=None)
            condition &= ~Q(activeclient__product_id=None)
        condition &= Q(interest_gl__in=gl_arr)
        filter_var  = Income_details_date.objects.using(self._current_app_schema()).filter(condition).values("interest_gl",'activeclient__assest_class').annotate(interest_amount=Sum("fee_due")) \
                                                        .values("activeclient__business_id", "interest_gl",
                                                                "activeclient__assest_class", "interest_amount",
                                                                "activeclient__client_id",
                                                                "activeclient__product_id")
        prolist = NWisefinList()
        if len(filter_var) == 0:
            return prolist
        else:
            for data in filter_var:
                ppr_response = Income_details_response()
                ppr_response.set_interest_amount(data["interest_amount"])
                ppr_response.set_interest_gl(data["interest_gl"])
                if filter_obj.get_id() != None and filter_obj.get_id() != "":
                    cat_dtls = APsubcategory.objects.using(self._current_app_schema()).filter(glno=data["interest_gl"],category__expense__id=filter_obj.get_id()).values("glno","category__id","category__name")
                    cat_dtls = masterservice.get_subcat_cat(data["interest_gl"],filter_obj.get_id())
                    for k in cat_dtls:
                        ppr_response.set_id(k["category__id"])
                        ppr_response.set_name(k["category__name"])
                        ppr_response.set_expensegrp_id(k['category__expense__exp_grp_id'])
                        ppr_response.set_apexpense_id(k['category__expense__id'])
                user_dtls = user_service.get_BS([data["activeclient__assest_class"]])
                ppr_response.set_assest_class(user_dtls[0]["name"])
                # if data["activeclient__assest_class"] == Asset_class.AGRI:
                #     ppr_response.set_assest_class(Asset_class.AGRI_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.BD:
                #     ppr_response.set_assest_class(Asset_class.BD_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.CC:
                #     ppr_response.set_assest_class(Asset_class.CC_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.CF:
                #     ppr_response.set_assest_class(Asset_class.CF_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.CL:
                #     ppr_response.set_assest_class(Asset_class.CL_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.AHF:
                #     ppr_response.set_assest_class(Asset_class.AHF_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.CONS:
                #     ppr_response.set_assest_class(Asset_class.CONS_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.CORP:
                #     ppr_response.set_assest_class(Asset_class.CORP_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.INTER_COMPANY:
                #     ppr_response.set_assest_class(Asset_class.INTER_COMPANY_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.MFI:
                #     ppr_response.set_assest_class(Asset_class.MFI_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.OTH:
                #     ppr_response.set_assest_class(Asset_class.OTH_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.SBL:
                #     ppr_response.set_assest_class(Asset_class.SBL_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.VF:
                #     ppr_response.set_assest_class(Asset_class.VF_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.Consumer_Finance:
                #     ppr_response.set_assest_class(Asset_class.Consumer_Finance_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.Gold_Loans:
                #     ppr_response.set_assest_class(Asset_class.Gold_Loans_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.CV:
                #     ppr_response.set_assest_class(Asset_class.CV_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.VL:
                #     ppr_response.set_assest_class(Asset_class.VL_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.SME:
                #     ppr_response.set_assest_class(Asset_class.SME_VAL)
                prolist.append(ppr_response)
        return prolist

    def ppr_income_subcat_logic(self, filter_obj):
        masterservice=MASTER_SERVICE(self._scope())
        user_service = USER_SERVICE(self._scope())
        where_gl = masterservice.get_subcatgl_subcat(filter_obj.get_expgrp_id(), filter_obj.get_exp_id(),filter_obj.get_cat_id())
        gl_arr = []
        for x in where_gl:
            gl_arr.append(x)
        condition = Q(status=1)
        if filter_obj.get_from_date() != None and filter_obj.get_from_date() != "" and filter_obj.get_to_date() != None and filter_obj.get_to_date() != "":
            condition &= Q(date__range=[filter_obj.get_from_date(), filter_obj.get_to_date()])
        if filter_obj.get_business_id() != 4:
            if filter_obj.get_asset_id() != None and filter_obj.get_asset_id() != "" and len(filter_obj.get_asset_id()) != 0:
                condition &= Q(activeclient__assest_class__in=filter_obj.get_asset_id())
            else:
                condition &= ~Q(activeclient__assest_class=None)
            if filter_obj.get_Rm_id() != None and filter_obj.get_Rm_id() != "":
                rm = self.client_get(filter_obj.get_Rm_id())
                rm.append(filter_obj.get_client_id())
            if filter_obj.get_client_id() != None and filter_obj.get_client_id() != "" :
                condition &= Q(activeclient__client_id=filter_obj.get_client_id())
            else:
                condition &= Q(activeclient__client_id=None)
            if filter_obj.get_product_id() != None and filter_obj.get_product_id() != "" :
                condition &= Q(activeclient__product_id=filter_obj.get_product_id())
            else:
                condition &= Q(activeclient__product_id=None)
            if filter_obj.get_business_id() != None and filter_obj.get_business_id() != "" :
                condition &= Q(activeclient__business_id=filter_obj.get_business_id())
            else:
                condition &= Q(activeclient__business_id=None)
        else:
            condition &= ~Q(activeclient__business_id=None)
            condition &= ~Q(activeclient__assest_class=None)
            condition &= ~Q(activeclient__client_id=None)
            condition &= ~Q(activeclient__product_id=None)
        condition &= Q(interest_gl__in=gl_arr)
        filter_var = Income_details_date.objects.using(self._current_app_schema()).filter(condition).values("interest_gl","activeclient__assest_class").annotate(interest_amount=Sum("fee_due")) \
                                                            .values("activeclient__business_id", "interest_gl",
                                                                    "activeclient__assest_class", "interest_amount",
                                                                    "activeclient__client_id",
                                                                    "activeclient__product_id")
        prolist = NWisefinList()
        if len(filter_var) == 0:
            return prolist
        else:
            for data in filter_var:
                ppr_response = Income_details_response()
                ppr_response.set_interest_amount(data["interest_amount"])
                ppr_response.set_interest_gl(data["interest_gl"])
                if filter_obj.get_cat_id() != None and filter_obj.get_cat_id() != "":
                    subcat_dtls = masterservice.get_subcat_glno(data['interest_gl'],filter_obj.get_cat_id())
                    for k in subcat_dtls:
                        ppr_response.set_id(k["id"])
                        ppr_response.set_name(k["name"])
                        ppr_response.set_expensegrp_id(k['category__expense__exp_grp_id'])
                        ppr_response.set_apexpense_id(k['category__expense__id'])
                        ppr_response.set_category_id(k['category__id'])
                user_dtls = user_service.get_BS([data["activeclient__assest_class"]])
                ppr_response.set_assest_class(user_dtls[0]["name"])
                # if data["activeclient__assest_class"] == Asset_class.AGRI:
                #     ppr_response.set_assest_class(Asset_class.AGRI_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.BD:
                #     ppr_response.set_assest_class(Asset_class.BD_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.CC:
                #     ppr_response.set_assest_class(Asset_class.CC_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.CF:
                #     ppr_response.set_assest_class(Asset_class.CF_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.CL:
                #     ppr_response.set_assest_class(Asset_class.CL_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.AHF:
                #     ppr_response.set_assest_class(Asset_class.AHF_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.CONS:
                #     ppr_response.set_assest_class(Asset_class.CONS_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.CORP:
                #     ppr_response.set_assest_class(Asset_class.CORP_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.INTER_COMPANY:
                #     ppr_response.set_assest_class(Asset_class.INTER_COMPANY_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.MFI:
                #     ppr_response.set_assest_class(Asset_class.MFI_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.OTH:
                #     ppr_response.set_assest_class(Asset_class.OTH_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.SBL:
                #     ppr_response.set_assest_class(Asset_class.SBL_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.VF:
                #     ppr_response.set_assest_class(Asset_class.VF_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.Consumer_Finance:
                #     ppr_response.set_assest_class(Asset_class.Consumer_Finance_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.Gold_Loans:
                #     ppr_response.set_assest_class(Asset_class.Gold_Loans_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.CV:
                #     ppr_response.set_assest_class(Asset_class.CV_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.VL:
                #     ppr_response.set_assest_class(Asset_class.VL_VAL)
                # elif data["activeclient__assest_class"] == Asset_class.SME:
                #     ppr_response.set_assest_class(Asset_class.SME_VAL)
                prolist.append(ppr_response)
        return prolist

    def ppr_income_logic(self,params_data,pprdata,asset_data):
        pprdata = json.loads(pprdata)
        expgrpname = []
        assetname = []
        value = []
        amount_ary = []
        expensegrp_id = ''
        expense_id = ''
        cat_id = ''
        prolist = NWisefinList()
        row = {}

        for x in pprdata["data"]:
            # ref_id = x["expensegroup_id"]
            if x["name"] not in expgrpname:
                expgrpname.append(x["name"])
            if x["assest_class"] not in assetname:
                assetname.append(x["assest_class"])
            if x["id"] not in value:
                value.append(x["id"])
        if params_data != 1:
            assetname = asset_data
        # assetname.append("Total")
        # value.append(0)
        append_flag = 0
        ast_name = ''
        for a1, a in zip(expgrpname, value):
            amount_ary = []
            ytd_val = 0
            for a2 in assetname:
                asst_amt = 0
                ast_name = a2
                flag = False
                for a3 in pprdata["data"]:
                    if a1 == a3['name']:
                        if a2 == a3['assest_class']:
                            flag = True
                            ytd_val = ytd_val + a3['interest_amount']
                            asst_amt = asst_amt + a3['interest_amount']
                            # amount_ary.append(a3['amount'])
                if flag == False:
                    if ast_name != 'Total':
                        amount_ary.append(0.00)
                else:
                    amount_ary.append(asst_amt)
            amount_ary.append(ytd_val)

            if int(params_data) == 1:
                if append_flag == 0:
                    assetname.append('Total')

                data = {"id": a, "name": a1, "asset_name": assetname, "amount": amount_ary,
                        "expensegrp_id": expensegrp_id}
                append_flag = append_flag + 1
                prolist.append(data)

            if int(params_data) == 2:
                if append_flag == 0:
                    assetname.append('Total')
                if len(pprdata["data"]) != 0:
                    expensegrp_id = pprdata["data"][0]['expensegroup_id']
                data = {"id": a, "name": a1, "asset_name": assetname, "amount": amount_ary,
                        "expensegrp_id": expensegrp_id}
                append_flag = append_flag + 1
                prolist.append(data)
            if int(params_data) == 3:
                if append_flag == 0:
                    assetname.append('Total')
                if len(pprdata["data"]) != 0:
                    expensegrp_id = pprdata["data"][0]['expensegroup_id']
                    expense_id = pprdata["data"][0]['apexpense_id']
                data = {"id": a, "name": a1, "asset_name": assetname, "amount": amount_ary,
                        "expensegrp_id": expensegrp_id, "expense_id": expense_id}
                append_flag = append_flag + 1
                prolist.append(data)
            if int(params_data) == 4:
                if append_flag == 0:
                    assetname.append('Total')
                if len(pprdata["data"]) != 0:
                    expensegrp_id = pprdata["data"][0]['expensegroup_id']
                    expense_id = pprdata["data"][0]['apexpense_id']
                    cat_id = pprdata["data"][0]['category_id']
                data = {"id": a, "name": a1, "asset_name": assetname, "amount": amount_ary,
                        "expensegrp_id": expensegrp_id, "expense_id": expense_id, "cat_id": cat_id}
                append_flag = append_flag + 1
                prolist.append(data)
        if int(params_data) == 1:
            total_ary = []
            aa11 = prolist.get()
            aa12 = json.loads(aa11)
            for index, assetname_obj, in enumerate(assetname):
                amount_val = 0
                for exp_obj in aa12['data']:
                    if assetname_obj == exp_obj['asset_name'][index]:
                        amount_val = amount_val + exp_obj['amount'][index]
                total_ary.append(amount_val)
            data = {"name": "Total", "asset_name": assetname, "amount": total_ary,
                    }
            prolist.append(data)
        return prolist

    def new_ppr_incomegrp_logic(self,filter_obj):
        masterservice=MASTER_SERVICE(self._scope())
        # user_service = USER_SERVICE(self._scope())
        condition = Q(status=1)
        if filter_obj.get_from_date() != None and filter_obj.get_from_date() != "" and filter_obj.get_to_date() != None and filter_obj.get_to_date() != "":
            condition &= Q(updated_date__range=[filter_obj.get_from_date(),filter_obj.get_to_date()])
        # if filter_obj.get_business_id() != 4:
        if filter_obj.get_asset_id() != None and filter_obj.get_asset_id() != "" and len(filter_obj.get_asset_id()) != 0:
            condition &= Q(assest_class__in=filter_obj.get_asset_id())
        # else:
        #     condition &= ~Q(assest_class=None)
        if filter_obj.get_Rm_id() != None and filter_obj.get_Rm_id() != "":
            rm = self.client_get(filter_obj.get_Rm_id())
            rm.append(filter_obj.get_client_id())
        if filter_obj.get_client_id() != None and filter_obj.get_client_id() != "" :
            condition &= Q(client_id=filter_obj.get_client_id())
        # else:
        #     condition &= Q(client_id=None)
        if filter_obj.get_product_id() != None and filter_obj.get_product_id() != "" :
            condition &= Q(product_id=filter_obj.get_product_id())
        # else:
        #     condition &= Q(product_id=None)
        if filter_obj.get_business_id() != None and filter_obj.get_business_id() != "" :
            condition &= Q(business_id=filter_obj.get_business_id())
        # else:
        #     condition &= Q(business_id=None)
        # else:
        #     condition &= ~Q(business_id=None)
        #     condition &= ~Q(assest_class=None)
        #     condition &= ~Q(client_id=None)
        #     condition &= ~Q(product_id=None)
        filter_var  = Income_overalldata.objects.using(self._current_app_schema()).filter(condition).values("interest_gl","assest_class").annotate(interest_amount=F("fee_due")+F("interest_amount")+F("eir_amount"))\
                                                                        .values("business_id","interest_gl",
                                                                                "assest_class","interest_amount",
                                                                                "client_id",
                                                                                "product_id")
        prolist = NWisefinList()
        if len(filter_var) == 0:
            return prolist
        else:
            for data in filter_var:
                ppr_response = Income_details_response()
                ppr_response.set_interest_amount(data["interest_amount"])
                ppr_response.set_interest_gl(data["interest_gl"])
                exp_dtls = APsubcategory.objects.using(self._current_app_schema()).filter(glno=data["interest_gl"]).values("glno","category__expense__exp_grp_id")
                exp_dtls = masterservice.get_subcat_expgrp(data["interest_gl"])
                for j in exp_dtls:
                    expgrp_dtls = masterservice.get_expense_grp(j['category__expense__exp_grp_id'])
                    # expgrp_dtls = APexpensegroup.objects.using(self._current_app_schema()).filter(id=j["category__expense__exp_grp_id"]).values("id","name")
                    for i in expgrp_dtls:
                        ppr_response.set_id(i["id"])
                        ppr_response.set_name(i["name"])
                user_dtls = masterservice.get_BS_id([data["assest_class"]])
                ppr_response.set_assest_class(user_dtls[0]["name"])
                prolist.append(ppr_response)
        return prolist

    def new_incomehead_logic(self,filter_obj):
        masterservice=MASTER_SERVICE(self._scope())
        # user_service = USER_SERVICE(self._scope())
        # exp = pprservice_expense.objects.values_list('expensegrp_id', flat=True).distinct
        where_gl = masterservice.get_subcatgl_exphead(filter_obj.get_id())
        # my_list = [foo for foo in where_gl]
        gl_arr = []
        for x in where_gl:
            gl_arr.append(x)
        condition = Q(status=1)
        if filter_obj.get_from_date() != None and filter_obj.get_from_date() != "" and filter_obj.get_to_date() != None and filter_obj.get_to_date() != "":
            condition &= Q(updated_date__range=[filter_obj.get_from_date(),filter_obj.get_to_date()])
        # if filter_obj.get_business_id() != 4:
        if filter_obj.get_asset_id() != None and filter_obj.get_asset_id() != "" and len(
                filter_obj.get_asset_id()) != 0:
            condition &= Q(assest_class__in=filter_obj.get_asset_id())
        # else:
        #     condition &= ~Q(assest_class=None)
        if filter_obj.get_Rm_id() != None and filter_obj.get_Rm_id() != "":
            rm = self.client_get(filter_obj.get_Rm_id())
            rm.append(filter_obj.get_client_id())
        if filter_obj.get_client_id() != None and filter_obj.get_client_id() != "":
            condition &= Q(client_id=filter_obj.get_client_id())
        # else:
        #     condition &= Q(client_id=None)
        if filter_obj.get_product_id() != None and filter_obj.get_product_id() != "":
            condition &= Q(product_id=filter_obj.get_product_id())
        # else:
        #     condition &= Q(product_id=None)
        if filter_obj.get_business_id() != None and filter_obj.get_business_id() != "":
            condition &= Q(business_id=filter_obj.get_business_id())
            # else:
            #     condition &= Q(business_id=None)
        # else:
        #     condition &= ~Q(business_id=None)
        #     condition &= ~Q(assest_class=None)
        #     condition &= ~Q(client_id=None)
        #     condition &= ~Q(product_id=None)
        condition &= Q(interest_gl__in = gl_arr)
        filter_var = Income_overalldata.objects.using(self._current_app_schema()).filter(condition).values("interest_gl","assest_class").annotate(interest_amount=F("fee_due")+F("interest_amount")+F("eir_amount"))\
                                                                                .values("business_id","interest_gl",
                                                                                "assest_class","interest_amount",
                                                                                "client_id",
                                                                                "product_id")
        prolist = NWisefinList()
        if len(filter_var) == 0:
            return prolist
        else:
            for data in filter_var:
                ppr_response = Income_details_response()
                ppr_response.set_interest_amount(data["interest_amount"])
                ppr_response.set_interest_gl(data["interest_gl"])
                if filter_obj.get_id() != None and filter_obj.get_id() != "":
                    exp_dtls = masterservice.get_subcat_exp(data["interest_gl"],filter_obj.get_id())
                    for k in exp_dtls:
                        ppr_response.set_id(k["category__expense__id"])
                        ppr_response.set_name(k["category__expense__head"])
                        ppr_response.set_expensegrp_id(k["category__expense__exp_grp_id"])
                user_dtls = masterservice.get_BS_id([data["assest_class"]])
                ppr_response.set_assest_class(user_dtls[0]["name"])
                prolist.append(ppr_response)
        return prolist

    def new_incomecat_logic(self,filter_obj):
        masterservice=MASTER_SERVICE(self._scope())
        # user_service = USER_SERVICE(self._scope())
        where_gl = masterservice.get_subcatgl_cat(filter_obj.get_expgrp_id(),filter_obj.get_id())
        gl_arr = []
        for x in where_gl:
            gl_arr.append(x)
        condition = Q(status=1)
        if filter_obj.get_from_date() != None and filter_obj.get_from_date() != "" and filter_obj.get_to_date() != None and filter_obj.get_to_date() != "":
            condition &= Q(updated_date__range=[filter_obj.get_from_date(),filter_obj.get_to_date()])
        # if filter_obj.get_business_id() != 4:
        if filter_obj.get_asset_id() != None and filter_obj.get_asset_id() != "" and len(filter_obj.get_asset_id()) != 0:
            condition &= Q(assest_class__in=filter_obj.get_asset_id())
        # else:
        #     condition &= ~Q(activeclient__assest_class=None)
        if filter_obj.get_Rm_id() != None and filter_obj.get_Rm_id() != "":
            rm = self.client_get(filter_obj.get_Rm_id())
            rm.append(filter_obj.get_client_id())
        if filter_obj.get_client_id() != None and filter_obj.get_client_id() != "" :
            condition &= Q(client_id=filter_obj.get_client_id())
        # else:
        #     condition &= Q(activeclient__client_id=None)
        if filter_obj.get_product_id() != None and filter_obj.get_product_id() != "" :
            condition &= Q(product_id=filter_obj.get_product_id())
        # else:
        #     condition &= Q(activeclient__product_id=None)
        if filter_obj.get_business_id() != None and filter_obj.get_business_id() != "" :
            condition &= Q(business_id=filter_obj.get_business_id())
            # else:
            #     condition &= Q(activeclient__business_id=None)
        # else:
        #     condition &= ~Q(business_id=None)
        #     condition &= ~Q(assest_class=None)
        #     condition &= ~Q(client_id=None)
        #     condition &= ~Q(product_id=None)
        condition &= Q(interest_gl__in=gl_arr)
        filter_var  = Income_overalldata.objects.using(self._current_app_schema()).filter(condition).values("interest_gl",'assest_class').annotate(interest_amount=F("fee_due")+F("interest_amount")+F("eir_amount")) \
                                                        .values("business_id", "interest_gl",
                                                                "assest_class", "interest_amount",
                                                                "client_id",
                                                                "product_id")
        prolist = NWisefinList()
        if len(filter_var) == 0:
            return prolist
        else:
            for data in filter_var:
                ppr_response = Income_details_response()
                ppr_response.set_interest_amount(data["interest_amount"])
                ppr_response.set_interest_gl(data["interest_gl"])
                if filter_obj.get_id() != None and filter_obj.get_id() != "":
                    # cat_dtls = APsubcategory.objects.using(self._current_app_schema()).filter(glno=data["interest_gl"],category__expense__id=filter_obj.get_id()).values("glno","category__id","category__name")
                    cat_dtls = masterservice.get_subcat_cat(data["interest_gl"],filter_obj.get_id())
                    for k in cat_dtls:
                        ppr_response.set_id(k["category__id"])
                        ppr_response.set_name(k["category__name"])
                        ppr_response.set_expensegrp_id(k['category__expense__exp_grp_id'])
                        ppr_response.set_apexpense_id(k['category__expense__id'])
                user_dtls = masterservice.get_BS_id([data["assest_class"]])
                ppr_response.set_assest_class(user_dtls[0]["name"])
                prolist.append(ppr_response)
        return prolist

    def new_incomesubcat_logic(self, filter_obj):
        masterservice=MASTER_SERVICE(self._scope())
        # user_service = USER_SERVICE(self._scope())
        where_gl = masterservice.get_subcatgl_subcat(filter_obj.get_expgrp_id(), filter_obj.get_exp_id(),filter_obj.get_cat_id())
        gl_arr = []
        for x in where_gl:
            gl_arr.append(x)
        condition = Q(status=1)
        if filter_obj.get_from_date() != None and filter_obj.get_from_date() != "" and filter_obj.get_to_date() != None and filter_obj.get_to_date() != "":
            condition &= Q(updated_date__range=[filter_obj.get_from_date(), filter_obj.get_to_date()])
        # if filter_obj.get_business_id() != 4:
        if filter_obj.get_asset_id() != None and filter_obj.get_asset_id() != "" and len(filter_obj.get_asset_id()) != 0:
            condition &= Q(assest_class__in=filter_obj.get_asset_id())
        # else:
        #     condition &= ~Q(activeclient__assest_class=None)
        if filter_obj.get_Rm_id() != None and filter_obj.get_Rm_id() != "":
            rm = self.client_get(filter_obj.get_Rm_id())
            rm.append(filter_obj.get_client_id())
        if filter_obj.get_client_id() != None and filter_obj.get_client_id() != "" :
            condition &= Q(client_id=filter_obj.get_client_id())
        # else:
        #     condition &= Q(activeclient__client_id=None)
        if filter_obj.get_product_id() != None and filter_obj.get_product_id() != "" :
            condition &= Q(product_id=filter_obj.get_product_id())
        # else:
        #     condition &= Q(activeclient__product_id=None)
        if filter_obj.get_business_id() != None and filter_obj.get_business_id() != "" :
            condition &= Q(business_id=filter_obj.get_business_id())
            # else:
            #     condition &= Q(activeclient__business_id=None)
        # else:
        #     condition &= ~Q(business_id=None)
        #     condition &= ~Q(assest_class=None)
        #     condition &= ~Q(client_id=None)
        #     condition &= ~Q(product_id=None)
        condition &= Q(interest_gl__in=gl_arr)
        filter_var = Income_overalldata.objects.using(self._current_app_schema()).filter(condition).values("interest_gl","assest_class").annotate(interest_amount=F("fee_due")+F("interest_amount")+F("eir_amount")) \
                                                            .values("business_id", "interest_gl",
                                                                    "assest_class", "interest_amount",
                                                                    "client_id",
                                                                    "product_id")
        prolist = NWisefinList()
        if len(filter_var) == 0:
            return prolist
        else:
            for data in filter_var:
                ppr_response = Income_details_response()
                ppr_response.set_interest_amount(data["interest_amount"])
                ppr_response.set_interest_gl(data["interest_gl"])
                if filter_obj.get_cat_id() != None and filter_obj.get_cat_id() != "":
                    subcat_dtls = masterservice.get_subcat_glno(data['interest_gl'],filter_obj.get_cat_id())
                    for k in subcat_dtls:
                        ppr_response.set_id(k["id"])
                        ppr_response.set_name(k["name"]+" -("+str(k['glno'])+")")
                        ppr_response.set_expensegrp_id(k['category__expense__exp_grp_id'])
                        ppr_response.set_apexpense_id(k['category__expense__id'])
                        ppr_response.set_category_id(k['category__id'])
                user_dtls = masterservice.get_BS_id([data["assest_class"]])
                ppr_response.set_assest_class(user_dtls[0]["name"])
                prolist.append(ppr_response)
        return prolist