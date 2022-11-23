import json
from datetime import timedelta

import numpy as np
import pandas as pd
from django.db.models import Count, F, Q, Sum
from django.http import HttpResponse

from pprservice.data.request.nac_income_request import ppr_clientrequest

from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessMessage, SuccessStatus
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from pprservice.models.pprmodel import DSS_Format_Date,DSS_Format_Month,Ppr_Sources,Head_Groups,Sub_Groups,GL_Subgroup
from pprservice.util.pprutility import Fees_type, Client_flag, Activestatus, Asset_class, USER_SERVICE
from pprservice.data.response.nac_income_respone import ppr_clientresponse,Income_details_response as Income_details_response
from datetime import datetime
from pprservice.data.response.nac_income_respone import ppr_clientresponse, \
    Income_details_response as Income_details_response, ppr_source_response

class DSS_Service(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.PPR_SERVICE)

    def dss_upload_date(self, dssfile_obj, emp_id):
        gl_data = GL_Subgroup.objects.using(self._current_app_schema()).filter(status=1)
        gl_df = pd.DataFrame(gl_data.values('id', 'gl_no'))
        data_type = {"id": int, "gl_no": int}
        gl_df = gl_df.astype(data_type)
        # dssfile_obj['gl_no'].astype(str)
        merge_data = pd.merge(gl_df, dssfile_obj,
                              on="gl_no", how="right",
                              )
        dss_obj = merge_data.fillna(np.nan).replace([np.nan], [0]).to_dict(orient='records')
        # month_tab=self.dss_upload_month(dss_obj,emp_id)
        # dssfile_obj.gl_no.update(dssfile_obj.gl_no.map(gl_df.set_index('gl_no').id), ignore_index=True)
        # file_obj = dssfile_obj
        for file_data in dss_obj:
            month_tab = self.dss_upload_month(file_data, emp_id)
            if file_data["id"] != 0:
                obj = DSS_Format_Date.objects.using(self._current_app_schema()).filter(gl_subgroup=file_data["id"],
                                                                                       entity_id=self._entity_id(),
                                                                                       flag=1, date=file_data["date"])
                if len(obj) != 0:
                    dss_obj = DSS_Format_Date.objects.using(self._current_app_schema()).filter(
                        gl_subgroup_id=file_data["id"], entity_id=self._entity_id()).update(
                        credit=F('credit') + file_data["Credits"], debit=F('debit') + file_data["Debits"],
                        opening_balance=F('opening_balance') + file_data["Beginning Balance"],
                        closing_balance=F('closing_balance') + file_data["Ending Balance"], month=1, status=1,
                        updated_by=emp_id, updated_date=datetime.now(), date=file_data["date"],
                        entity_id=self._entity_id(), flag=1)
                else:
                    dss_obj = DSS_Format_Date.objects.using(self._current_app_schema()).create(
                        credit=file_data["Credits"],
                        debit=file_data["Debits"], opening_balance=file_data["Beginning Balance"],
                        date=file_data["date"], closing_balance=file_data["Ending Balance"], status=1,
                        created_by=emp_id, created_date=datetime.now(), gl_subgroup_id=file_data["id"],
                        entity_id=self._entity_id(), flag=1)
            else:
                dss_obj = DSS_Format_Date.objects.using(self._current_app_schema()).create(credit=file_data["Credits"],
                                                                                           debit=file_data["Debits"],
                                                                                           opening_balance=file_data[
                                                                                               "Beginning Balance"],
                                                                                           date=file_data["date"],
                                                                                           closing_balance=file_data[
                                                                                               "Ending Balance"],
                                                                                           status=1, created_by=emp_id,
                                                                                           created_date=datetime.now(),
                                                                                           gl_subgroup_id=None,
                                                                                           entity_id=self._entity_id(),
                                                                                           flag=2)

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def dss_upload_month(self, file_data, emp_id):
        # date=file_data["date"]
        # datem = file_data["date"].month
        month = file_data["date"].month
        if file_data["id"] != 0:
            obj = DSS_Format_Month.objects.using(self._current_app_schema()).filter(gl_subgroup=file_data["id"],
                                                                                    entity_id=self._entity_id(),
                                                                                    flag=1, month=month)
            if len(obj) != 0:
                dss_obj = DSS_Format_Month.objects.using(self._current_app_schema()).filter(
                    gl_subgroup_id=file_data["id"], entity_id=self._entity_id()).update(
                    credit=F('credit') + file_data["Credits"], debit=F('debit') + file_data["Debits"],
                    opening_balance=F('opening_balance') + file_data["Beginning Balance"],
                    closing_balance=F('closing_balance') + file_data["Ending Balance"], month=month, status=1,
                    updated_by=emp_id, updated_date=datetime.now(),
                    entity_id=self._entity_id(), flag=1)
            else:
                dss_obj = DSS_Format_Month.objects.using(self._current_app_schema()).create(
                    credit=file_data["Credits"],
                    debit=file_data["Debits"], opening_balance=file_data["Beginning Balance"], month=month,
                    closing_balance=file_data["Ending Balance"], status=1, created_by=emp_id,
                    created_date=datetime.now(), gl_subgroup_id=file_data["id"], entity_id=self._entity_id(),
                    flag=1)
        else:
            dss_obj = DSS_Format_Month.objects.using(self._current_app_schema()).create(credit=file_data["Credits"],
                                                                                        debit=file_data["Debits"],
                                                                                        opening_balance=file_data[
                                                                                            "Beginning Balance"],
                                                                                        month=month,
                                                                                        closing_balance=file_data[
                                                                                            "Ending Balance"],
                                                                                        status=1, created_by=emp_id,
                                                                                        created_date=datetime.now(),
                                                                                        gl_subgroup_id=None,
                                                                                        entity_id=self._entity_id(),
                                                                                        flag=2)

    def fetch_dssdate_level_list(self, filterobj):
        prolist = NWisefinList()
        prolist1 = NWisefinList()
        prolist2 = NWisefinList()
        befo_date = filterobj.get_date()
        input_date = datetime.strptime(befo_date, "%Y-%m-%d")
        input_date = input_date.date()
        day = timedelta(days=1)
        prev_date = input_date - day
        month = input_date.replace(day=1)
        prev_month = month - day
        condition = Q(status=1, date__date=input_date)
        condition2 = Q(status=1, date__date=input_date,
                       gl_subgroup__head_group__head_group__source_id=filterobj.get_id())
        condition3 = Q(status=1, date__date=input_date, gl_subgroup__head_group__head_group_id=filterobj.get_id())
        condition4 = Q(status=1, date__date=input_date, gl_subgroup__head_group_id=filterobj.get_id())
        if filterobj.get_type() != None and filterobj.get_type() != "":
            if filterobj.get_type() == 1:
                filter_var = DSS_Format_Date.objects.using(self._current_app_schema()).filter(condition).values(
                    'date__date', "gl_subgroup__head_group__head_group__source__id",
                    "gl_subgroup__head_group__head_group__source__name",).annotate(credit=Sum('credit'),
                                                                                                 debit=Sum('debit'),
                                                                                                 opening_balance=Sum(
                                                                                                     'opening_balance'),
                                                                                                 closing_balance=Sum(
                                                                                                     'closing_balance'))
            if filterobj.get_type() == 2:
                filter_var = DSS_Format_Date.objects.using(self._current_app_schema()).filter(condition2).values(
                    'date__date', "gl_subgroup__head_group__head_group__id",
                    "gl_subgroup__head_group__head_group__name").annotate(credit=Sum('credit'),
                                                                                         debit=Sum('debit'),
                                                                                         opening_balance=Sum(
                                                                                             'opening_balance'),
                                                                                         closing_balance=Sum(
                                                                                             'closing_balance'))
            if filterobj.get_type() == 3:
                filter_var = DSS_Format_Date.objects.using(self._current_app_schema()).filter(condition3).values(
                    'date__date', "gl_subgroup__head_group__id", "gl_subgroup__head_group__name").annotate(
                    credit=Sum('credit'), debit=Sum('debit'), opening_balance=Sum('opening_balance'),
                    closing_balance=Sum('closing_balance'))
            if filterobj.get_type() == 4:
                filter_var = DSS_Format_Date.objects.using(self._current_app_schema()).filter(condition4).values(
                'date__date', "gl_subgroup__id", "gl_subgroup__description", "gl_subgroup__gl_no").annotate(
                credit=Sum('credit'), debit=Sum('debit'), opening_balance=Sum('opening_balance'),
                closing_balance=Sum('closing_balance'))
        arr1 = []
        arr2 = []
        data1 = []
        data2 = []
        value = []
        if len(filter_var) != 0:
            for i in filter_var:
                ppr_response = ppr_source_response()
                if filterobj.get_type() == 1:
                    ppr_response.set_name(i["gl_subgroup__head_group__head_group__source__name"])
                    name = i["gl_subgroup__head_group__head_group__source__name"]
                    id_grp = i["gl_subgroup__head_group__head_group__source__id"]
                    ppr_response.set_opening_balance(abs(i["opening_balance"]))
                    ppr_response.set_closing_balance(abs(i["closing_balance"]))
                    ppr_response.set_credit(abs(i["credit"]))
                    ppr_response.set_debit(abs(i["debit"]))
                    ppr_response.set_date(str(i["date__date"]))
                    value.append(ppr_response)
                    data1 = {"name": name, "value": value, "id": id_grp}
                    value = []
                    prolist.append(data1)
                elif filterobj.get_type() == 2:
                    ppr_response.set_name(i["gl_subgroup__head_group__head_group__name"])
                    ppr_response.set_id(i["gl_subgroup__head_group__head_group__id"])
                    name = i["gl_subgroup__head_group__head_group__name"]
                    id_grp = i["gl_subgroup__head_group__head_group__id"]
                    ppr_response.set_opening_balance(abs(i["opening_balance"]))
                    ppr_response.set_closing_balance(abs(i["closing_balance"]))
                    ppr_response.set_credit(abs(i["credit"]))
                    ppr_response.set_debit(abs(i["debit"]))
                    ppr_response.set_date(str(i["date__date"]))
                    value.append(ppr_response)
                    data1 = {"name": name, "value": value, "id": id_grp}
                    value = []
                    prolist.append(data1)
                elif filterobj.get_type() == 3:
                    ppr_response.set_name(i["gl_subgroup__head_group__name"])
                    ppr_response.set_id(i["gl_subgroup__head_group__id"])
                    name = i["gl_subgroup__head_group__name"]
                    id_grp = i["gl_subgroup__head_group__id"]
                    ppr_response.set_opening_balance(abs(i["opening_balance"]))
                    ppr_response.set_closing_balance(abs(i["closing_balance"]))
                    ppr_response.set_credit(abs(i["credit"]))
                    ppr_response.set_debit(abs(i["debit"]))
                    ppr_response.set_date(str(i["date__date"]))
                    value.append(ppr_response)
                    data1 = {"name": name, "value": value, "id": id_grp}
                    value = []
                    prolist.append(data1)
                elif filterobj.get_type() == 4:
                    ppr_response.set_name(i["gl_subgroup__gl_no"]+" -("+str(i['gl_subgroup__description'])+")")
                    name = i["gl_subgroup__gl_no"]+" -("+str(i['gl_subgroup__description'])+")"
                    id_grp = i["gl_subgroup__id"]
                    ppr_response.set_description(i["gl_subgroup__description"])
                    ppr_response.set_opening_balance(abs(i["opening_balance"]))
                    ppr_response.set_closing_balance(abs(i["closing_balance"]))
                    ppr_response.set_credit(abs(i["credit"]))
                    ppr_response.set_debit(abs(i["debit"]))
                    ppr_response.set_date(str(i["date__date"]))
                    value.append(ppr_response)
                    data1 = {"name": name, "value": value, "id": id_grp}
                    value = []
                    prolist.append(data1)
        # return prolist
        condition = Q(status=1, date__date=prev_date)
        condition2 = Q(status=1, date__date=prev_date,
                       gl_subgroup__head_group__head_group__source_id=filterobj.get_id())
        condition3 = Q(status=1, date__date=prev_date, gl_subgroup__head_group__head_group_id=filterobj.get_id())
        condition4 = Q(status=1, date__date=prev_date, gl_subgroup__head_group_id=filterobj.get_id())
        if filterobj.get_type() != None and filterobj.get_type() != "":
            if filterobj.get_type() == 1:
                filter_var = DSS_Format_Date.objects.using(self._current_app_schema()).filter(condition).values(
                    'date__date', "gl_subgroup__head_group__head_group__source__id",
                    "gl_subgroup__head_group__head_group__source__name").annotate(credit=Sum('credit'),
                                                                                                 debit=Sum('debit'),
                                                                                                 opening_balance=Sum(
                                                                                                     'opening_balance'),
                                                                                                 closing_balance=Sum(
                                                                                                     'closing_balance'))
            if filterobj.get_type() == 2:
                filter_var = DSS_Format_Date.objects.using(self._current_app_schema()).filter(condition2).values(
                    'date__date', "gl_subgroup__head_group__head_group__id",
                    "gl_subgroup__head_group__head_group__name").annotate(credit=Sum('credit'),
                                                                                         debit=Sum('debit'),
                                                                                         opening_balance=Sum(
                                                                                             'opening_balance'),
                                                                                         closing_balance=Sum(
                                                                                             'closing_balance'))
            if filterobj.get_type() == 3:
                filter_var = DSS_Format_Date.objects.using(self._current_app_schema()).filter(condition3).values(
                    'date__date', "gl_subgroup__head_group__id", "gl_subgroup__head_group__name").annotate(
                    credit=Sum('credit'), debit=Sum('debit'), opening_balance=Sum('opening_balance'),
                    closing_balance=Sum('closing_balance'))
            if filterobj.get_type() == 4:
                filter_var = DSS_Format_Date.objects.using(self._current_app_schema()).filter(condition4).values(
                        'date__date', "gl_subgroup__id", "gl_subgroup__description", "gl_subgroup__gl_no").annotate(
                        credit=Sum('credit'), debit=Sum('debit'), opening_balance=Sum('opening_balance'),
                        closing_balance=Sum('closing_balance'))
        arr1 = []
        arr2 = []
        data1 = []
        data2 = []
        value = []
        if len(filter_var) != 0:
            for i in filter_var:
                ppr_response = ppr_source_response()
                if filterobj.get_type() == 1:
                    ppr_response.set_name(i["gl_subgroup__head_group__head_group__source__name"])
                    name = i["gl_subgroup__head_group__head_group__source__name"]
                    id_grp = i["gl_subgroup__head_group__head_group__source__id"]
                    ppr_response.set_opening_balance(abs(i["opening_balance"]))
                    ppr_response.set_closing_balance(abs(i["closing_balance"]))
                    ppr_response.set_credit(abs(i["credit"]))
                    ppr_response.set_debit(abs(i["debit"]))
                    ppr_response.set_date(str(i["date__date"]))
                    value.append(ppr_response)
                    data1 = {"name": name, "value": value, "id": id_grp}
                    value = []
                    prolist1.append(data1)
                elif filterobj.get_type() == 2:
                    ppr_response.set_name(i["gl_subgroup__head_group__head_group__name"])
                    ppr_response.set_id(i["gl_subgroup__head_group__head_group__id"])
                    name = i["gl_subgroup__head_group__head_group__name"]
                    id_grp = i["gl_subgroup__head_group__head_group__id"]
                    ppr_response.set_opening_balance(abs(i["opening_balance"]))
                    ppr_response.set_closing_balance(abs(i["closing_balance"]))
                    ppr_response.set_credit(abs(i["credit"]))
                    ppr_response.set_debit(abs(i["debit"]))
                    ppr_response.set_date(str(i["date__date"]))
                    value.append(ppr_response)
                    data1 = {"name": name, "value": value, "id": id_grp}
                    value = []
                    prolist1.append(data1)
                elif filterobj.get_type() == 3:
                    ppr_response.set_name(i["gl_subgroup__head_group__name"])
                    ppr_response.set_id(i["gl_subgroup__head_group__id"])
                    name = i["gl_subgroup__head_group__name"]
                    id_grp = i["gl_subgroup__head_group__id"]
                    ppr_response.set_opening_balance(abs(i["opening_balance"]))
                    ppr_response.set_closing_balance(abs(i["closing_balance"]))
                    ppr_response.set_credit(abs(i["credit"]))
                    ppr_response.set_debit(abs(i["debit"]))
                    ppr_response.set_date(str(i["date__date"]))
                    value.append(ppr_response)
                    data1 = {"name": name, "value": value, "id": id_grp}
                    value = []
                    prolist1.append(data1)
                elif filterobj.get_type() == 4:
                    ppr_response.set_name(i["gl_subgroup__gl_no"])
                    name = i["gl_subgroup__gl_no"]
                    id_grp = i["gl_subgroup__id"]
                    ppr_response.set_description(i["gl_subgroup__description"])
                    ppr_response.set_opening_balance(abs(i["opening_balance"]))
                    ppr_response.set_closing_balance(abs(i["closing_balance"]))
                    ppr_response.set_credit(abs(i["credit"]))
                    ppr_response.set_debit(abs(i["debit"]))
                    ppr_response.set_date(str(i["date__date"]))
                    value.append(ppr_response)
                    data1 = {"name": name, "value": value, "id": id_grp}
                    value = []
                    prolist1.append(data1)
        a=prolist.data
        b=prolist1.data
        resp_list=NWisefinList()
        arr=[]
        for i in a:
            # a=False
            for j in b:
                if i["id"]==j["id"]:
                    i["value"].append(j["value"][0])
                    resp_list.append(i)
                    arr.append(i["id"])
                #     resp_list.append(i)
                #     a=True
                # else:
                #     i["value"].append({"closing_balance": "", "credit": "", "date": "", "debit": "", "opening_balance": "",
                #              "id": "", "name": ""})

                #     resp_list.append(i)
        for i in a:
            if i["id"] not in arr:
                i["value"].append({"closing_balance": 0.00, "credit": 0.00, "date": str(prev_date), "debit": 0.00, "opening_balance": 0.00,
                             "id": "", "name": ""})
                resp_list.append(i)
        for j in b:
            if j["id"] not in arr:
                j["value"].insert(0,{"closing_balance": 0.00, "credit": 0.00, "date": str(input_date), "debit": 0.00, "opening_balance": 0.00,
                             "id": "", "name": ""})
                resp_list.append(j)
        # return resp_list
        condition = Q(status=1, date__date=prev_month)
        condition2 = Q(status=1, date__date=prev_month,
                       gl_subgroup__head_group__head_group__source_id=filterobj.get_id())
        condition3 = Q(status=1, date__date=prev_month, gl_subgroup__head_group__head_group_id=filterobj.get_id())
        condition4 = Q(status=1, date__date=prev_month, gl_subgroup__head_group_id=filterobj.get_id())
        if filterobj.get_type() != None and filterobj.get_type() != "":
            if filterobj.get_type() == 1:
                filter_var = DSS_Format_Date.objects.using(self._current_app_schema()).filter(condition).values(
                    'date__date', "gl_subgroup__head_group__head_group__source__id",
                    "gl_subgroup__head_group__head_group__source__name").annotate(credit=Sum('credit'),
                                                                                                 debit=Sum('debit'),
                                                                                                 opening_balance=Sum(
                                                                                                     'opening_balance'),
                                                                                                 closing_balance=Sum(
                                                                                                     'closing_balance'))
            if filterobj.get_type() == 2:
                filter_var = DSS_Format_Date.objects.using(self._current_app_schema()).filter(condition2).values(
                    'date__date', "gl_subgroup__head_group__head_group__id",
                    "gl_subgroup__head_group__head_group__name").annotate(credit=Sum('credit'),
                                                                                         debit=Sum('debit'),
                                                                                         opening_balance=Sum(
                                                                                             'opening_balance'),
                                                                                         closing_balance=Sum(
                                                                                             'closing_balance'))
            if filterobj.get_type() == 3:
                filter_var = DSS_Format_Date.objects.using(self._current_app_schema()).filter(condition3).values(
                    'date__date', "gl_subgroup__head_group__id", "gl_subgroup__head_group__name").annotate(
                    credit=Sum('credit'), debit=Sum('debit'), opening_balance=Sum('opening_balance'),
                    closing_balance=Sum('closing_balance'))
            if filterobj.get_type() == 4:
                filter_var = DSS_Format_Date.objects.using(self._current_app_schema()).filter(condition4).values(
                    'date__date', "gl_subgroup__id", "gl_subgroup__gl_no","gl_subgroup__description").annotate(
                    credit=Sum('credit'), debit=Sum('debit'), opening_balance=Sum('opening_balance'),
                    closing_balance=Sum('closing_balance'))
        arr1 = []
        arr2 = []
        data1 = []
        data2 = []
        value = []
        if len(filter_var) != 0:
            for i in filter_var:
                ppr_response = ppr_source_response()
                if filterobj.get_type() == 1:
                    ppr_response.set_id(i["gl_subgroup__head_group__head_group__source__id"])
                    ppr_response.set_name(i["gl_subgroup__head_group__head_group__source__name"])
                    name = i["gl_subgroup__head_group__head_group__source__name"]
                    id_grp = i["gl_subgroup__head_group__head_group__source__id"]
                    # ppr_response.set_opening_balance(i["opening_balance"])
                    ppr_response.set_month_balance(abs(i["closing_balance"]))
                    # ppr_response.set_credit(i["credit"])
                    # ppr_response.set_debit(i["debit"])
                    ppr_response.set_date(str(i["date__date"]))
                    value.append(ppr_response)
                    data1 = {"name": name, "value": value, "id": id_grp}
                    value = []
                    prolist2.append(data1)
                elif filterobj.get_type() == 2:
                    ppr_response.set_id(i["gl_subgroup__head_group__head_group__id"])
                    ppr_response.set_name(i["gl_subgroup__head_group__head_group__name"])
                    name = i["gl_subgroup__head_group__head_group__name"]
                    id_grp = i["gl_subgroup__head_group__head_group__id"]
                    # ppr_response.set_opening_balance(i["opening_balance"])
                    ppr_response.set_month_balance(abs(i["closing_balance"]))
                    # ppr_response.set_credit(i["credit"])
                    # ppr_response.set_debit(i["debit"])
                    ppr_response.set_date(str(i["date__date"]))
                    value.append(ppr_response)
                    data1 = {"name": name, "value": value, "id": id_grp}
                    value = []
                    prolist2.append(data1)
                elif filterobj.get_type() == 3:
                    ppr_response.set_id(i["gl_subgroup__head_group__id"])
                    ppr_response.set_name(i["gl_subgroup__head_group__name"])
                    name = i["gl_subgroup__head_group__name"]
                    id_grp = i["gl_subgroup__head_group__id"]
                    # ppr_response.set_opening_balance(i["opening_balance"])
                    ppr_response.set_month_balance(abs(i["closing_balance"]))
                    # ppr_response.set_credit(i["credit"])
                    # ppr_response.set_debit(i["debit"])
                    ppr_response.set_date(str(i["date__date"]))
                    value.append(ppr_response)
                    data1 = {"name": name, "value": value, "id": id_grp}
                    value = []
                    prolist2.append(data1)
                elif filterobj.get_type() == 4:
                    ppr_response.set_id(i["gl_subgroup__id"])
                    ppr_response.set_name(i["gl_subgroup__gl_no"])
                    name = i["gl_subgroup__gl_no"]
                    id_grp = i["gl_subgroup__id"]
                    ppr_response.set_description(i["gl_subgroup__description"])
                    # ppr_response.set_opening_balance(i["opening_balance"])
                    ppr_response.set_month_balance(abs(i["closing_balance"]))
                    # ppr_response.set_credit(i["credit"])
                    # ppr_response.set_debit(i["debit"])
                    ppr_response.set_date(str(i["date__date"]))
                    value.append(ppr_response)
                    data1 = {"name": name, "value": value, "id": id_grp}
                    value = []
                    prolist2.append(data1)
        c = resp_list.data
        d = prolist2.data
        resp_list1 = NWisefinList()
        arr3 = []
        for k in c:
            # a=False
            for l in d:
                if k["id"] ==l["id"]:
                    k["value"].append(l["value"][0])
                    resp_list1.append(k)
                    arr3.append(k["id"])
                #     resp_list.append(i)
                #     a=True
                # else:
                #     i["value"].append({"closing_balance": "", "credit": "", "date": "", "debit": "", "opening_balance": "",
                #              "id": "", "name": ""})

                #     resp_list.append(i)
        for i in c:
            if i["id"] not in arr3:
                i["value"].append(
                    {"month_balance": 0.00,"date": "",
                     "id": "", "name": ""})
                resp_list1.append(i)
        # for j in d:
        #     if j["id"] not in arr3:
        #         j["value"].append({"month_balance": "","date": str(input_date),
        #                               "id": "", "name": ""})
        #         resp_list1.append(j)
        return resp_list1