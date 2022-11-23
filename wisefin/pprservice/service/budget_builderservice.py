import json
import pandas as pd
from pprservice.data.response.pprreportresponse import pprresponse
from pprservice.data.response.warning import Pprdata_warning
from pprservice.util.pprutility import Ppr_utilityservice
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
import datetime
from utilityservice.data.response.nwisefinlist import NWisefinList
from decimal import Decimal
from pprservice.models.pprmodel import Pprdata, Budgetdetial,PPR_history,PPR_Documents
from django.db.models import Count
from django.db.models import Q, Sum
from pprservice.data.response.budgetbuilderresponse import BudgetBuilderresponse,EmployeeBranchresponse,BudgetRemarkResponse,budget_reject_response
from pprservice.util.pprutility import Pprutility_keys,CRUDstatus,ReftableType,VENDOR_SERVICE,USER_SERVICE,MASTER_SERVICE
from pprservice.service.ppr_reportservice import Pprservice
from pprservice.data.response.success import Success, successMessage
from django.utils.timezone import now

from pprservice.data.response.pprauditresponse import PprAuditResponse
from pprservice.service.ppr_auditservice import PPRAuditService
from userservice.models.usermodels import Employee,EmployeeBranch,EmployeeBusinessSegmentMapping
from nwisefin.settings import logger
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


from masterservice.models.mastermodels import APexpensegroup, Apsector, APexpense, Apcategory, APsubcategory
import boto3
from django.conf import settings


class BudgetBuilderservice(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.PPR_SERVICE)

    def budget_expensegrp_list(self, bgt_obj):
        bgtdata = []
        pro_list = NWisefinList()
        utilitys = Ppr_utilityservice(self._scope())
        masterservice = MASTER_SERVICE(self._scope())
        condition = Q(status=1,entity_id=self._entity_id())
        expensegrp_id = APexpensegroup.objects.using(self._current_app_schema()).filter(condition)
        for exgrp_id in expensegrp_id:
            expense_id = masterservice.get_new_expgrp_exp([exgrp_id.id])
            if len(expense_id) == 0:
                if bgt_obj.get_year_term() == 'Monthly':
                    tranmon1 = 4
                    for f in range(0, 12):
                        tranmon = tranmon1
                        if tranmon1 == 13:
                            tranmon = 1
                        if tranmon1 == 14:
                            tranmon = 2
                        if tranmon1 == 15:
                            tranmon = 3
                        pprresponser = pprresponse()
                        pprresponser.expensegrp_id = exgrp_id.id
                        pprresponser.expensegrpname = exgrp_id.name
                        pprresponser.set_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                        pprresponser.set_transactionmonth(tranmon)
                        pro_list.data.append(pprresponser)
                        tranmon1 = tranmon1 + 1
                if bgt_obj.get_year_term() == 'Quarterly':
                    tranmon1 = 1
                    for f in range(0, 4):
                        tranmon = tranmon1
                        pprresponser = pprresponse()
                        pprresponser.expensegrp_id = exgrp_id.id
                        pprresponser.expensegrpname = exgrp_id.name
                        pprresponser.set_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                        pprresponser.set_quarter(tranmon)
                        pro_list.data.append(pprresponser)
                        tranmon1 = tranmon1 + 1
            else:
                for expense in expense_id:
                    condition = Q(status=2,entity_id=self._entity_id())
                    if bgt_obj.get_finyear() != None and bgt_obj.get_finyear() != "":
                        condition &= Q(finyear=bgt_obj.get_finyear())
                    if bgt_obj.get_branch_id() != None and bgt_obj.get_branch_id() != "":
                        condition &= Q(apinvoicebranch_id=bgt_obj.get_branch_id())
                    if bgt_obj.get_sector_name() != None and bgt_obj.get_sector_name() != "":
                        condition &= Q(sectorname=bgt_obj.get_sector_name())
                    if bgt_obj.get_mstbusiness_segment_name() != None and bgt_obj.get_mstbusiness_segment_name() != "":
                        condition &= Q(bizname=bgt_obj.get_mstbusiness_segment_name())
                    if bgt_obj.get_bs_name() != None and bgt_obj.get_bs_name() != "":
                        condition &= Q(bsname=bgt_obj.get_bs_name())
                    if bgt_obj.get_cc_name() != None and bgt_obj.get_cc_name() != "":
                        condition &= Q(ccname=bgt_obj.get_cc_name())
                    condition &= Q(apexpense_id=expense)
                    if bgt_obj.get_year_term() == 'Monthly':
                        bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id', 'transactionmonth').annotate(
                            amount=Sum('amount'))
                    if bgt_obj.get_year_term() == 'Quarterly':
                        bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id', 'quarter').annotate(
                            amount=Sum('amount'))
                    if len(bgtdata) <= 0:
                        if bgt_obj.get_year_term() == 'Monthly':
                            tranmon1 = 4
                            for f in range(0, 12):
                                tranmon = tranmon1
                                if tranmon1 == 13:
                                    tranmon = 1
                                if tranmon1 == 14:
                                    tranmon = 2
                                if tranmon1 == 15:
                                    tranmon = 3
                                pprresponser = pprresponse()
                                pprresponser.expensegrp_id = exgrp_id.id
                                pprresponser.expensegrpname = exgrp_id.name
                                pprresponser.set_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                                pprresponser.set_transactionmonth(tranmon)
                                pro_list.data.append(pprresponser)
                                tranmon1 = tranmon1 + 1
                        if bgt_obj.get_year_term() == 'Quarterly':
                            tranmon1 = 1
                            for f in range(0, 4):
                                tranmon = tranmon1
                                pprresponser = pprresponse()
                                pprresponser.expensegrp_id = exgrp_id.id
                                pprresponser.expensegrpname = exgrp_id.name
                                pprresponser.set_quarter(tranmon)
                                pprresponser.set_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                                pro_list.data.append(pprresponser)
                                tranmon1 = tranmon1 + 1
                    else:
                        for i in bgtdata:
                            bgtresponser = BudgetBuilderresponse()
                            bgtresponser.expensegrp_id = exgrp_id.id
                            bgtresponser.expensegrpname = exgrp_id.name
                            bgtresponser.set_bgtamount(str(Decimal(i['amount']) / bgt_obj.get_divAmount()))
                            if bgt_obj.get_year_term() == 'Monthly':
                                bgtresponser.set_transactionmonth(i["transactionmonth"])
                            if bgt_obj.get_year_term() == 'Quarterly':
                                bgtresponser.set_quarter(i["quarter"])
                            pro_list.data.append(bgtresponser)
        return pro_list

    def compare_ppr_bgt_expensegrp(self, pprdata, bgtdata, bgt_obj):
        # try:
        #test
        logger.info('compare expensegrp start')
        pprdata = json.loads(pprdata)
        bgtdata = json.loads(bgtdata)
        keys = Pprutility_keys()
        yearterm = bgt_obj.get_year_term()
        condition = ""
        valu_mQ = ""
        if yearterm == "Monthly":
            condition = keys.transactionmonth
            valu_mQ = "0"
        if yearterm == "Quarterly":
            condition = keys.quarter
            valu_mQ = 0
        if len(pprdata["data"]) <= 0:
            pprdata["data"] = [{
                condition: valu_mQ,
                "amount": "",
                "expensegrp_id": 0,
                "expensegrpname": "",
            }]
        if len(bgtdata["data"]) <= 0:
            bgtdata["data"] = [{
                condition: valu_mQ,
                "amount": "",
                "expensegrp_id": 0,
                "expensegrpname": "",
            }]
        ppr_df = pd.DataFrame(pprdata["data"])
        bgt_df = pd.DataFrame(bgtdata["data"])
        merge_data = pd.merge(ppr_df, bgt_df, how="left",
                              left_on=[condition, "expensegrp_id", "expensegrpname"],
                              right_on=[condition, "expensegrp_id", "expensegrpname"])
        final_merge = merge_data[
            [condition, "expensegrp_id", "expensegrpname", "bgtamount",
             "amount"]].fillna(0)
        logger.info('compare expensegrp end')
        return final_merge.to_json(orient="records")
        # except:
        #     return json.dumps([])

    def future_budget_expensegrp_list(self, bgt_obj,pagequery):
        bgtdata = []
        pro_list = NWisefinList()
        pprutility = Ppr_utilityservice(self._scope())
        masterservice = MASTER_SERVICE(self._scope())
        condition = Q(entity_id=self._entity_id())
        expensegrp_id = APexpensegroup.objects.using(self._current_app_schema()).filter(condition)
        for exgrp_id in expensegrp_id:
            expense_id = masterservice.get_new_expgrp_exp([exgrp_id.id])
            if len(expense_id) == 0:
                if bgt_obj.get_year_term() == 'Monthly':
                    tranmon1 = 4
                    for f in range(0, 12):
                        tranmon = tranmon1
                        if tranmon1 == 13:
                            tranmon = 1
                        if tranmon1 == 14:
                            tranmon = 2
                        if tranmon1 == 15:
                            tranmon = 3
                        pprresponser = pprresponse()
                        pprresponser.expensegrp_id = exgrp_id.id
                        pprresponser.expensegrpname = exgrp_id.name
                        pprresponser.set_future_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                        pprresponser.set_transactionmonth(tranmon)
                        pro_list.data.append(pprresponser)
                        tranmon1 = tranmon1 + 1
                if bgt_obj.get_year_term() == 'Quarterly':
                    tranmon1 = 1
                    for f in range(0, 4):
                        tranmon = tranmon1
                        pprresponser = pprresponse()
                        pprresponser.expensegrp_id = exgrp_id.id
                        pprresponser.expensegrpname = exgrp_id.name
                        pprresponser.set_future_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                        pprresponser.set_quarter(tranmon)
                        pprresponser.set_status(str(Decimal(0.0)))
                        pprresponser.set_remark_key("")
                        pro_list.data.append(pprresponser)
                        tranmon1 = tranmon1 + 1
            else:
                for expense in expense_id:

                    if bgt_obj.get_status_id() != None and bgt_obj.get_status_id() != "":
                        condition = Q(status=bgt_obj.get_status_id(),entity_id=self._entity_id())
                    if pagequery !=None and pagequery != "":
                        if pagequery == "APPROVER":
                            condition = Q(status=3,entity_id=self._entity_id())
                        elif pagequery == "CHECKER":
                            condition = Q(status=2,entity_id=self._entity_id())
                        elif pagequery == "VIEWER":
                            condition = Q(status=4,entity_id=self._entity_id())
                    if bgt_obj.get_finyear() != None and bgt_obj.get_finyear() != "":
                        condition &= Q(finyear=f'FY{int(bgt_obj.get_finyear().split("-")[0][-2:]) + 1}-{int(bgt_obj.get_finyear().split("-")[1]) + 1}')
                    if bgt_obj.get_branch_id() != None and bgt_obj.get_branch_id() != "":
                        condition &= Q(apinvoicebranch_id=bgt_obj.get_branch_id())
                    if bgt_obj.get_sector_name() != None and bgt_obj.get_sector_name() != "":
                        condition &= Q(sectorname=bgt_obj.get_sector_name())
                    if bgt_obj.get_mstbusiness_segment_name() != None and bgt_obj.get_mstbusiness_segment_name() != "":
                        condition &= Q(bizname=bgt_obj.get_mstbusiness_segment_name())
                    if bgt_obj.get_bs_name() != None and bgt_obj.get_bs_name() != "":
                        condition &= Q(bsname=bgt_obj.get_bs_name())
                    if bgt_obj.get_cc_name() != None and bgt_obj.get_cc_name() != "":
                        condition &= Q(ccname=bgt_obj.get_cc_name())
                    condition &= Q(apexpense_id=expense)
                    if bgt_obj.get_year_term() == 'Monthly':
                        bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id', 'transactionmonth','status','remark_key').annotate(
                            fut_bgt_amount=Sum('amount'))
                    if bgt_obj.get_year_term() == 'Quarterly':
                        bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id', 'quarter','status','remark_key').annotate(
                            fut_bgt_amount=Sum('amount'))
                    if len(bgtdata) <= 0:
                        if bgt_obj.get_year_term() == 'Monthly':
                            tranmon1 = 4
                            for f in range(0, 12):
                                tranmon = tranmon1
                                if tranmon1 == 13:
                                    tranmon = 1
                                if tranmon1 == 14:
                                    tranmon = 2
                                if tranmon1 == 15:
                                    tranmon = 3
                                pprresponser = pprresponse()
                                pprresponser.expensegrp_id = exgrp_id.id
                                pprresponser.expensegrpname = exgrp_id.name
                                pprresponser.set_future_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                                pprresponser.set_transactionmonth(tranmon)
                                pprresponser.set_status(str(Decimal(0.0)))
                                pprresponser.set_remark_key("")
                                pro_list.data.append(pprresponser)
                                tranmon1 = tranmon1 + 1
                        if bgt_obj.get_year_term() == 'Quarterly':
                            tranmon1 = 1
                            for f in range(0, 4):
                                tranmon = tranmon1
                                pprresponser = pprresponse()
                                pprresponser.expensegrp_id = exgrp_id.id
                                pprresponser.expensegrpname = exgrp_id.name
                                pprresponser.set_future_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                                pprresponser.set_quarter(tranmon)
                                pprresponser.set_status(str(Decimal(0.0)))
                                pprresponser.set_remark_key("")
                                pro_list.data.append(pprresponser)
                                tranmon1 = tranmon1 + 1
                    else:
                        for i in bgtdata:
                            bgtresponser = BudgetBuilderresponse()
                            bgtresponser.expensegrp_id = exgrp_id.id
                            bgtresponser.expensegrpname = exgrp_id.name
                            bgtresponser.set_future_bgtamount(str(Decimal(i["fut_bgt_amount"]) / bgt_obj.get_divAmount()))
                            bgtresponser.set_status(i['status'])
                            bgtresponser.set_remark_key(i['remark_key'])
                            if bgt_obj.get_year_term() == 'Monthly':
                                bgtresponser.set_transactionmonth(i["transactionmonth"])
                            if bgt_obj.get_year_term() == 'Quarterly':
                                bgtresponser.set_quarter(i["quarter"])
                            bgtresponser.set_status(i['status'])
                            bgtresponser.set_remark_key(i['remark_key'])
                            pro_list.data.append(bgtresponser)
        return pro_list

    def compare_future_bgt_expensegrp(self,future_bgt,ppr_bgt,bgt_obj,pagequery):
        # try:
        logger.info('compare future expensegrp start')
        future_bgt = json.loads(future_bgt)
        ppr_bgt = json.loads(ppr_bgt)
        keys = Pprutility_keys()
        yearterm = bgt_obj.get_year_term()
        condition = ""
        valu_mQ = ""
        if yearterm == "Monthly":
            condition = keys.transactionmonth
            valu_mQ = "0"
        if yearterm == "Quarterly":
            condition = keys.quarter
            valu_mQ = 0
        if len(ppr_bgt) <= 0:
            ppr_bgt = [{
                condition: valu_mQ,
                "expensegrp_id": 0,
                "expensegrpname": "",
                "bgtamount": "",
                "amount": ""
            }]
        if len(future_bgt["data"]) <= 0:
            future_bgt["data"] = [{
                "expensegrp_id": 0,
                "expensegrpname": "",
                "future_bgtamount": "",
                "status":0,
                "remark_key":"",
                condition: valu_mQ
            }]
        ppr_bgtDF = pd.DataFrame(ppr_bgt)
        future_bgtDF = pd.DataFrame(future_bgt["data"])
        merge_data = pd.merge(future_bgtDF, ppr_bgtDF, how="outer",
                              left_on=["expensegrpname",
                                       condition,"expensegrp_id"],
                              right_on=["expensegrpname",
                                        condition,"expensegrp_id"])
        final_merge = merge_data[
            ["expensegrp_id","expensegrpname","bgtamount","amount","future_bgtamount",condition,"status","remark_key"]].fillna(0)
        logger.info('compare future expensegrp end')
        if pagequery !=None and pagequery != "":
            if pagequery == "APPROVER":
                return final_merge[final_merge['status'] == 3.0].to_json(orient="records")
            elif pagequery == "VIEWER":
                return final_merge[final_merge['status'] == 4.0].to_json(orient="records")
            elif pagequery == "CHECKER":
                return final_merge[final_merge['status'] == 2.0].to_json(orient="records")
        if bgt_obj.get_status_id() != None and bgt_obj.get_status_id() != "":
            return final_merge[final_merge['status'] == int(bgt_obj.get_status_id())].to_json(orient="records")
        return final_merge.to_json(orient="records")
        # except:
        #     return json.dumps([])

    def new_expensegrp_logic(self, expensegrp_data, ppr_obj):
        expensegrp_data = json.loads(expensegrp_data)
        pprservice = Pprservice(self._scope())
        keys = Pprutility_keys()
        output = []
        expensegrp_datauniq = []
        for i in expensegrp_data:
            if i["expensegrp_id"] != 0 and i["expensegrpname"] != "":
                if 'transactionmonth' in i:
                    if i["transactionmonth"] != "0":
                        expensegrp_datauniq.append(i)
                if 'quarter' in i:
                    if i["quarter"] != 0:
                        expensegrp_datauniq.append(i)
        try:
            if len(expensegrp_datauniq) <= 0:
                pass
            else:
                year_term = ppr_obj.get_year_term()
                if year_term == "Monthly":
                    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                elif year_term == "Quarterly":
                    month = ["Quarterly_1", "Quarterly_2", "Quarterly_3", "Quarterly_4"]
                else:
                    return {"message": Pprdata_warning.month_quaterneed}
                uniqexpensegrpname = pprservice.remove_duplicate_arrdict(expensegrp_datauniq, '', keys.expensegrpname,
                                                                         '')
                for expensegrp in uniqexpensegrpname:
                    row = {}
                    row[keys.name] = expensegrp
                    status = []
                    for imonth in month:
                        row[imonth] = [Decimal(round(Decimal('0.00'), 2)), Decimal(round(Decimal('0.00'), 2)),
                                       Decimal(round(Decimal('0.00'), 2))]
                    for uniq_month in expensegrp_datauniq:
                        if expensegrp == uniq_month[keys.expensegrpname]:
                            if int(uniq_month[keys.expensegrp_id]) > 0:
                                if int(uniq_month[keys.status]) not in status:
                                    status.append(int(uniq_month[keys.status]))
                            row[keys.remark_key] = uniq_month[keys.remark_key]
                            if year_term == "Monthly":
                                if row[month[int(uniq_month[keys.transactionmonth]) - 1]][1] != Decimal(
                                        round(Decimal('0.00'), 2)):
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][1] = row[month[
                                        int(uniq_month[keys.transactionmonth]) - 1]][1] + Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][0] = row[month[
                                        int(uniq_month[keys.transactionmonth]) - 1]][0] + Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                    if row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] != Decimal(
                                            round(Decimal('0.00'), 2)):
                                        row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] = row[month[
                                            int(uniq_month[keys.transactionmonth]) - 1]][2] + Decimal(
                                            round(Decimal(uniq_month["future_bgtamount"]), 2))
                                    else:
                                        row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] = Decimal(
                                            round(Decimal(uniq_month["future_bgtamount"]), 2))
                                else:
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][1] = Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][0] = Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                    if row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] != Decimal(
                                            round(Decimal('0.00'), 2)):
                                        row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] = row[month[
                                            int(uniq_month[keys.transactionmonth]) - 1]][2] + Decimal(
                                            round(Decimal(uniq_month["future_bgtamount"]), 2))
                                    else:
                                        row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] = Decimal(
                                            round(Decimal(uniq_month["future_bgtamount"]), 2))
                            if year_term == "Quarterly":
                                if row[f"Quarterly_{uniq_month[keys.quarter]}"][1] != Decimal(
                                        round(Decimal('0.00'), 2)) and f"Quarterly_{uniq_month[keys.quarter]}" in month:
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][1] = row[
                                                                                          f"Quarterly_{uniq_month[keys.quarter]}"][
                                                                                          1] + Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][0] = row[
                                                                                          f"Quarterly_{uniq_month[keys.quarter]}"][
                                                                                          0] + Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                else:
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][1] = Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][0] = Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][2] = Decimal(
                                        round(Decimal(uniq_month["future_bgtamount"]), 2))
                    ytd = [Decimal(round(Decimal('0.00'), 2)), Decimal(round(Decimal('0.00'), 2)), ""]
                    for i in [0, 1, 2]:
                        totalsum = Decimal(round(Decimal('0.00'), 2))
                        for sumof_month in month:
                            totalsum = totalsum + row[sumof_month][i]
                        if i == 2:
                            ytd[i] = Decimal(round(Decimal(totalsum), 2))
                        else:
                            ytd[i] = totalsum
                    status.sort(reverse=True)
                    row[keys.status] = status[0]
                    row[keys.YTD] = ytd
                    row['tree_flag'] = 'Y'
                    row[keys.Padding_left] = '10px'
                    row[keys.Padding] = '5px'
                    output.append(row)
                output.append(self.columndata_sum(month, output, '10px'))
            return {"data": output}  # "pagination":expensegrp_data['pagination']
        except:
            return {"data": output}


    def columndata_sum(self, month, output, left_padding):
        keys = Pprutility_keys()
        month.append('YTD')
        columnkeys = month
        overallrow = {}
        overallrow[keys.name] = 'Total :'
        for colmonth in columnkeys:
            overallrow[colmonth] = [self.sum_column(0, colmonth, output), self.sum_column(1, colmonth, output), self.sum_column(2, colmonth, output)]
        overallrow[keys.Padding_left] = left_padding
        overallrow[keys.Padding] = '10px'
        return overallrow

    def sum_column(self, index, month, output):
        total = Decimal(round(Decimal('0.00'), 2))
        for process in output:
            total = total + process[month][index]
        return total

    def budget_expense_list(self, bgt_obj):  # vys_page
        utilitys = Ppr_utilityservice(self._scope())
        masterservice = MASTER_SERVICE(self._scope())
        bgtdata = []
        pro_list = NWisefinList()
        condition = Q(status=2,entity_id=self._entity_id())
        if bgt_obj.get_expense_grp_id() != None and bgt_obj.get_expense_grp_id() != "":
            expense_id_dtls = APexpense.objects.using(self._current_app_schema()).filter(exp_grp_id=bgt_obj.get_expense_grp_id(),entity_id=self._entity_id())
            for exp_id in expense_id_dtls:

                        if bgt_obj.get_branch_id() != None and bgt_obj.get_branch_id() != "":
                            condition &= Q(apinvoicebranch_id=bgt_obj.get_branch_id())
                        if bgt_obj.get_finyear() != None and bgt_obj.get_finyear() != "":
                            condition &= Q(finyear=bgt_obj.get_finyear())
                        if bgt_obj.get_sector_name() != None and bgt_obj.get_sector_name() != "":
                            condition &= Q(sectorname=bgt_obj.get_sector_name())
                        if bgt_obj.get_mstbusiness_segment_name() != None and bgt_obj.get_mstbusiness_segment_name() != "":
                            condition &= Q(bizname=bgt_obj.get_mstbusiness_segment_name())
                        if bgt_obj.get_bs_name() != None and bgt_obj.get_bs_name() != "":
                            condition &= Q(bsname=bgt_obj.get_bs_name())
                        if bgt_obj.get_cc_name() != None and bgt_obj.get_cc_name() != "":
                            condition &= Q(ccname=bgt_obj.get_cc_name())
                        condition &= Q(apexpense_id=exp_id.id)
                        if bgt_obj.get_year_term() == 'Monthly':
                            bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id', 'transactionmonth').annotate(
                                amount=Sum('amount'))
                            # [vys_page.get_offset():vys_page.get_query_limit()]
                        if bgt_obj.get_year_term() == 'Quarterly':
                            bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id', 'quarter').annotate(
                                amount=Sum('amount'))
                            # [vys_page.get_offset():vys_page.get_query_limit()]
                        if len(bgtdata) <= 0:
                            if bgt_obj.get_year_term() == 'Monthly':
                                tranmon1 = 4
                                for f in range(0, 12):
                                    tranmon = tranmon1
                                    if tranmon1 == 13:
                                        tranmon = 1
                                    if tranmon1 == 14:
                                        tranmon = 2
                                    if tranmon1 == 15:
                                        tranmon = 3
                                    pprresponser = pprresponse()
                                    pprresponser.expense_id = exp_id.id
                                    pprresponser.expensename = exp_id.head
                                    pprresponser.expensegrpname = exp_id.group
                                    pprresponser.expensegrp_id = exp_id.exp_grp_id
                                    pprresponser.set_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                                    pprresponser.set_transactionmonth(int(tranmon))
                                    pro_list.data.append(pprresponser)
                                    tranmon1 = tranmon1 + 1
                            if bgt_obj.get_year_term() == 'Quarterly':
                                tranmon1 = 1
                                for f in range(0, 4):
                                    tranmon = tranmon1
                                    pprresponser = pprresponse()
                                    pprresponser.expense_id = exp_id.id
                                    pprresponser.expensename = exp_id.head
                                    pprresponser.expensegrpname = exp_id.group
                                    pprresponser.expensegrp_id = exp_id.exp_grp_id
                                    pprresponser.set_quarter(int(tranmon))
                                    pprresponser.set_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                                    pro_list.data.append(pprresponser)
                                    tranmon1 = tranmon1 + 1
                        else:
                            bgtexpense_ids = []
                            if len(bgtdata) > 0:
                                for i in bgtdata:
                                    bgtexpense_ids.append(i["apexpense_id"])
                            bgtexpense_detials = masterservice.get_expense((bgtexpense_ids))
                            for i in bgtdata:
                                bgtresponser = BudgetBuilderresponse()
                                bgtresponser.set_expense_detial(bgtexpense_detials, i["apexpense_id"])
                                bgtresponser.set_bgtamount(str(Decimal(i['amount']) / bgt_obj.get_divAmount()))
                                if bgt_obj.get_year_term() == 'Monthly':
                                    bgtresponser.set_transactionmonth(int(i["transactionmonth"]))
                                if bgt_obj.get_year_term() == 'Quarterly':
                                    bgtresponser.set_quarter(int(i["quarter"]))
                                pro_list.data.append(bgtresponser)
                        # vpage = PPRNWisefinPaginator(pprdata, vys_page.get_index(), 5)
                        # pro_list.set_pagination(vpage)
            return pro_list

    def future_budget_expense_list(self, bgt_obj,pagequery):  # vys_page
        pprutility = Ppr_utilityservice(self._scope())
        masterservice = MASTER_SERVICE(self._scope())
        bgtdata = []
        condition = Q()
        pro_list = NWisefinList()
        if bgt_obj.get_expense_grp_id() != None and bgt_obj.get_expense_grp_id() != "":
            expense_dtls_list = APexpense.objects.using(self._current_app_schema()).filter(exp_grp_id=bgt_obj.get_expense_grp_id(),entity_id=self._entity_id())
            for expid in expense_dtls_list:
                if bgt_obj.get_status_id() != None and bgt_obj.get_status_id() != "":
                    condition = Q(status=bgt_obj.get_status_id(),entity_id=self._entity_id())
                if pagequery !=None and pagequery != "":
                    if pagequery == "APPROVER":
                        condition = Q(status=3,entity_id=self._entity_id())
                    elif pagequery == "CHECKER":
                        condition = Q(status=2,entity_id=self._entity_id())
                    elif pagequery == "VIEWER":
                        condition = Q(status=4,entity_id=self._entity_id())
                if bgt_obj.get_branch_id() != None and bgt_obj.get_branch_id() != "":
                    condition &= Q(apinvoicebranch_id=bgt_obj.get_branch_id())
                if bgt_obj.get_finyear() != None and bgt_obj.get_finyear() != "":
                    condition &= Q(finyear=f'FY{int(bgt_obj.get_finyear().split("-")[0][-2:]) + 1}-{int(bgt_obj.get_finyear().split("-")[1]) + 1}')
                if bgt_obj.get_sector_name() != None and bgt_obj.get_sector_name() != "":
                    condition &= Q(sectorname=bgt_obj.get_sector_name())
                if bgt_obj.get_mstbusiness_segment_name() != None and bgt_obj.get_mstbusiness_segment_name() != "":
                    condition &= Q(bizname=bgt_obj.get_mstbusiness_segment_name())
                if bgt_obj.get_bs_name() != None and bgt_obj.get_bs_name() != "":
                    condition &= Q(bsname=bgt_obj.get_bs_name())
                if bgt_obj.get_cc_name() != None and bgt_obj.get_cc_name() != "":
                    condition &= Q(ccname=bgt_obj.get_cc_name())
                condition &= Q(apexpense_id=expid.id)
                if bgt_obj.get_year_term() == 'Monthly':
                    bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id', 'transactionmonth','status','remark_key').annotate(
                        fut_bgt_amount=Sum('amount'))
                    # [vys_page.get_offset():vys_page.get_query_limit()]
                if bgt_obj.get_year_term() == 'Quarterly':
                    bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id', 'quarter','status','remark_key').annotate(
                        fut_bgt_amount=Sum('amount'))
                    # [vys_page.get_offset():vys_page.get_query_limit()]
                if len(bgtdata) <= 0:
                    if bgt_obj.get_year_term() == 'Monthly':
                        tranmon1 = 4
                        for f in range(0, 12):
                            tranmon = tranmon1
                            if tranmon1 == 13:
                                tranmon = 1
                            if tranmon1 == 14:
                                tranmon = 2
                            if tranmon1 == 15:
                                tranmon = 3
                            pprresponser = pprresponse()
                            pprresponser.expense_id = expid.id
                            pprresponser.expensename = expid.head
                            pprresponser.expensegrpname = expid.group
                            pprresponser.expensegrp_id = expid.exp_grp_id
                            pprresponser.set_future_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                            pprresponser.set_status(str(Decimal(0.0)))
                            pprresponser.set_remark_key("")
                            pprresponser.set_transactionmonth(int(tranmon))
                            pro_list.data.append(pprresponser)
                            tranmon1 = tranmon1 + 1
                    if bgt_obj.get_year_term() == 'Quarterly':
                        tranmon1 = 1
                        for f in range(0, 4):
                            tranmon = tranmon1
                            pprresponser = pprresponse()
                            pprresponser.expense_id = expid.id
                            pprresponser.expensename = expid.head
                            pprresponser.expensegrpname = expid.group
                            pprresponser.expensegrp_id = expid.exp_grp_id
                            pprresponser.set_quarter(int(tranmon))
                            pprresponser.set_status(str(Decimal(0.0)))
                            pprresponser.set_remark_key("")
                            pprresponser.set_future_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                            pro_list.data.append(pprresponser)
                            tranmon1 = tranmon1 + 1
                else:
                    bgtexpense_ids = []
                    if len(bgtdata) > 0:
                        for i in bgtdata:
                            bgtexpense_ids.append(i["apexpense_id"])
                    bgtexpense_detials = masterservice.get_expense((bgtexpense_ids))
                    for i in bgtdata:
                        bgtresponser = BudgetBuilderresponse()
                        bgtresponser.set_expense_detial_future(bgtexpense_detials, i["apexpense_id"])
                        bgtresponser.set_future_bgtamount(str(Decimal(i["fut_bgt_amount"])/ bgt_obj.get_divAmount()))
                        bgtresponser.set_status(i['status'])
                        bgtresponser.set_remark_key(i['remark_key'])
                        if bgt_obj.get_year_term() == 'Monthly':
                            bgtresponser.set_transactionmonth(int(i["transactionmonth"]))
                        if bgt_obj.get_year_term() == 'Quarterly':
                            bgtresponser.set_quarter(int(i["quarter"]))
                        pro_list.data.append(bgtresponser)
                # vpage = PPRNWisefinPaginator(pprdata, vys_page.get_index(), 5)
                # pro_list.set_pagination(vpage)
            return pro_list

    def new_expense_logic(self, expense_data, ppr_obj):
        expense_data = json.loads(expense_data)
        pprservice = Pprservice(self._scope())
        keys = Pprutility_keys()
        output = []
        expense_datauniq = []
        for i in expense_data:
            if i["expense_id"] != 0 and i["expensegrpname"] != "" and i["expensename"] != "" :
                if 'transactionmonth' in i:
                    if i["transactionmonth"] != "0":
                        expense_datauniq.append(i)
                if 'quarter' in i:
                    if i["quarter"] != 0:
                        expense_datauniq.append(i)
        try:
            if len(expense_datauniq) <= 0:
                pass
            else:
                year_term = ppr_obj.get_year_term()
                if year_term == "Monthly":
                    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                elif year_term == "Quarterly":
                    month = ["Quarterly_1", "Quarterly_2", "Quarterly_3", "Quarterly_4"]
                else:
                    return {"message": Pprdata_warning.month_quaterneed}

                uniqexpenseid = pprservice.remove_duplicate_arrdict(expense_datauniq, '', keys.expense_id, '')
                uniqexpenselen = len(uniqexpenseid) - 1

                for index, expenseid in enumerate(uniqexpenseid):
                    row = {}
                    row[keys.expense_id] = expenseid
                    status = []
                    for imonth in month:
                        row[imonth] = [Decimal(round(Decimal('0.00'), 2)), Decimal(round(Decimal('0.00'), 2)), Decimal(round(Decimal('0.00'), 2))]
                    for uniq_month in expense_datauniq:
                        if expenseid == uniq_month[keys.expense_id]:
                            if int(uniq_month[keys.expense_id]) > 0:
                                if int(uniq_month[keys.status]) not in status:
                                    status.append(int(uniq_month[keys.status]))
                            row[keys.remark_key] = uniq_month[keys.remark_key]
                            if year_term == "Monthly":
                                if row[month[int(uniq_month[keys.transactionmonth]) - 1]][1] != Decimal(
                                        round(Decimal('0.00'), 2)):
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][1] = row[month[
                                        int(uniq_month[keys.transactionmonth]) - 1]][1] + Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][0] = row[month[
                                        int(uniq_month[keys.transactionmonth]) - 1]][0] + Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                else:
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][1] = Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][0] = Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                    if row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] != Decimal(
                                            round(Decimal('0.00'), 2)):
                                        row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] = row[month[
                                            int(uniq_month[keys.transactionmonth]) - 1]][2] + Decimal(
                                            round(Decimal(uniq_month["future_bgtamount"]), 2))
                                    else:
                                        row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] = Decimal(
                                            round(Decimal(uniq_month["future_bgtamount"]), 2))
                            if year_term == "Quarterly":
                                if row[f"Quarterly_{uniq_month[keys.quarter]}"][1] != Decimal(
                                        round(Decimal('0.00000'), 5)) and f"Quarterly_{uniq_month[keys.quarter]}" in month:
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][1] = row[
                                                                                          f"Quarterly_{uniq_month[keys.quarter]}"][
                                                                                          1] + Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][0] = row[
                                                                                          f"Quarterly_{uniq_month[keys.quarter]}"][
                                                                                          0] + Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                else:
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][1] = Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][0] = Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][2] = Decimal(
                                        round(Decimal(uniq_month["future_bgtamount"]), 2))

                            row[keys.name] = uniq_month[keys.expensename]
                            if index == uniqexpenselen:
                                row['page'] = 'Y'
                    ytd = [Decimal(round(Decimal('0.00'), 2)), Decimal(round(Decimal('0.00'), 2)), Decimal(round(Decimal('0.00'), 2))]
                    for i in [0, 1,2]:
                        totalsum = Decimal(round(Decimal('0.00'), 2))
                        for sumof_month in month:
                            totalsum = totalsum + row[sumof_month][i]
                        if i == 2:
                            ytd[i] = Decimal(round(Decimal(totalsum), 2))
                        else:
                            ytd[i] = totalsum
                    status.sort(reverse=True)
                    row[keys.status] = status[0]
                    row[keys.YTD] = ytd
                    row['tree_flag'] = 'Y'
                    row[keys.Padding_left] = '50px'
                    row[keys.Padding] = '5px'
                    output.append(row)

            return {"data": output}  # "pagination": expense_data["pagination"]
        except:
            return {"data": output}

    def budget_subcat_list(self, bgt_obj):  # vys_page
        pprutility = Ppr_utilityservice(self._scope())
        masterservice = MASTER_SERVICE(self._scope())
        bgtdata = []
        condition = Q(status=2,entity_id=self._entity_id())
        if bgt_obj.get_branch_id() != None and bgt_obj.get_branch_id() != "":
            condition &= Q(apinvoicebranch_id=bgt_obj.get_branch_id())
        if bgt_obj.get_finyear() != None and bgt_obj.get_finyear() != "":
            condition &= Q(finyear=bgt_obj.get_finyear())
        if bgt_obj.get_sector_name() != None and bgt_obj.get_sector_name() != "":
            condition &= Q(sectorname=bgt_obj.get_sector_name())
        if bgt_obj.get_mstbusiness_segment_name() != None and bgt_obj.get_mstbusiness_segment_name() != "":
            condition &= Q(bizname=bgt_obj.get_mstbusiness_segment_name())
        if bgt_obj.get_bs_name() != None and bgt_obj.get_bs_name() != "":
            condition &= Q(bsname=bgt_obj.get_bs_name())
        if bgt_obj.get_cc_name() != None and bgt_obj.get_cc_name() != "":
            condition &= Q(ccname=bgt_obj.get_cc_name())
        if bgt_obj.get_expense_id() != None and bgt_obj.get_expense_id() != "":
            condition &= Q(apexpense_id=bgt_obj.get_expense_id())
        if bgt_obj.get_year_term() == 'Monthly':
            bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apsubcat_id', 'transactionmonth',
                                                                    'apexpense_id').annotate(
                amount=Sum('amount'))
            # [vys_page.get_offset():vys_page.get_query_limit()]
        if bgt_obj.get_year_term() == 'Quarterly':
            bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apsubcat_id', 'quarter', 'apexpense_id').annotate(
                amount=Sum('amount'))
            # [vys_page.get_offset():vys_page.get_query_limit()]
        pro_list = NWisefinList()
        if len(bgtdata) <= 0:
            pass
        else:
            subcat_ids = []
            for i in bgtdata:
                subcat_ids.append(i['apsubcat_id'])

            subcat_detials = masterservice.get_subcat(subcat_ids)
            for i in bgtdata:
                bgtresponser = BudgetBuilderresponse()
                bgtresponser.set_subcat_datials_future(subcat_detials, i["apsubcat_id"])
                bgtresponser.set_bgtamount(str(Decimal(i['amount']) / bgt_obj.get_divAmount()))
                if bgt_obj.get_year_term() == 'Monthly':
                    bgtresponser.set_transactionmonth(i["transactionmonth"])
                if bgt_obj.get_year_term() == 'Quarterly':
                    bgtresponser.set_quarter(i["quarter"])
                bgtresponser.set_expense_id(i['apexpense_id'])
                pro_list.data.append(bgtresponser)
        # vpage = PPRNWisefinPaginator(pprdata, vys_page.get_index(), 5)
        # pro_list.set_pagination(vpage)
        return pro_list

    def future_budget_subcat_list(self, bgt_obj,pagequery):  # vys_page
        pprutility = Ppr_utilityservice(self._scope())
        masterservice=MASTER_SERVICE(self._scope())
        bgtdata = []
        condition = Q()
        if bgt_obj.get_status_id() != None and bgt_obj.get_status_id() != "":
            condition = Q(status=bgt_obj.get_status_id(),entity_id=self._entity_id())
        if pagequery != None and pagequery != "":
            if pagequery == "APPROVER":
                condition = Q(status=3,entity_id=self._entity_id())
            elif pagequery == "CHECKER":
                condition = Q(status=2,entity_id=self._entity_id())
            elif pagequery == "VIEWER":
                condition = Q(status=4,entity_id=self._entity_id())
        if bgt_obj.get_branch_id() != None and bgt_obj.get_branch_id() != "":
            condition &= Q(apinvoicebranch_id=bgt_obj.get_branch_id())
        if bgt_obj.get_finyear() != None and bgt_obj.get_finyear() != "":
            condition &= Q(finyear=f'FY{int(bgt_obj.get_finyear().split("-")[0][-2:]) + 1}-{int(bgt_obj.get_finyear().split("-")[1]) + 1}')
        if bgt_obj.get_sector_name() != None and bgt_obj.get_sector_name() != "":
            condition &= Q(sectorname=bgt_obj.get_sector_name())
        if bgt_obj.get_mstbusiness_segment_name() != None and bgt_obj.get_mstbusiness_segment_name() != "":
            condition &= Q(bizname=bgt_obj.get_mstbusiness_segment_name())
        if bgt_obj.get_bs_name() != None and bgt_obj.get_bs_name() != "":
            condition &= Q(bsname=bgt_obj.get_bs_name())
        if bgt_obj.get_cc_name() != None and bgt_obj.get_cc_name() != "":
            condition &= Q(ccname=bgt_obj.get_cc_name())
        if bgt_obj.get_expense_id() != None and bgt_obj.get_expense_id() != "":
            condition &= Q(apexpense_id=bgt_obj.get_expense_id())
        if bgt_obj.get_year_term() == 'Monthly':
            bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apsubcat_id', 'transactionmonth',
                                                                    'apexpense_id','status','remark_key').annotate(
                fut_bgt_amount=Sum('amount'))
            # [vys_page.get_offset():vys_page.get_query_limit()]
        if bgt_obj.get_year_term() == 'Quarterly':
            bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apsubcat_id', 'quarter', 'apexpense_id','status','remark_key').annotate(
                fut_bgt_amount=Sum('amount'))
            # [vys_page.get_offset():vys_page.get_query_limit()]
        pro_list = NWisefinList()
        if len(bgtdata) <= 0:
            pass
        else:
            subcat_ids = []
            for i in bgtdata:
                subcat_ids.append(i['apsubcat_id'])

            subcat_detials = masterservice.get_subcat(subcat_ids)
            for i in bgtdata:
                bgtresponser = BudgetBuilderresponse()
                bgtresponser.set_subcat_datials_future(subcat_detials, i["apsubcat_id"])
                bgtresponser.set_future_bgtamount(str(Decimal(i["fut_bgt_amount"])/ bgt_obj.get_divAmount()))
                bgtresponser.set_status(i['status'])
                bgtresponser.set_remark_key(i['remark_key'])
                if bgt_obj.get_year_term() == 'Monthly':
                    bgtresponser.set_transactionmonth(i["transactionmonth"])
                if bgt_obj.get_year_term() == 'Quarterly':
                    bgtresponser.set_quarter(i["quarter"])
                bgtresponser.set_expense_id(i['apexpense_id'])
                pro_list.data.append(bgtresponser)
        # vpage = PPRNWisefinPaginator(pprdata, vys_page.get_index(), 5)
        # pro_list.set_pagination(vpage)
        return pro_list

    def compare_ppr_bgt_subcat(self, pprdata, bgtdata, bgt_obj):
        # try:
        logger.info('compare subcat start')

        pprdata = json.loads(pprdata)
        bgtdata = json.loads(bgtdata)
        keys = Pprutility_keys()
        yearterm = bgt_obj.get_year_term()
        condition = ""
        valu_mQ = ""
        if yearterm == "Monthly":
            condition = keys.transactionmonth
            valu_mQ = "0"
        if yearterm == "Quarterly":
            condition = keys.quarter
            valu_mQ = 0
        if len(pprdata["data"]) <= 0:
            pprdata["data"] = [{
                condition: valu_mQ,
                "amount": "",
                "cat_id": 0,
                "categoryname": "",
                "expense_id": 0,
                "subcat_id": 0,
                "subcategoryname": ""
            }]
        if len(bgtdata["data"]) <= 0:
            bgtdata["data"] = [{
                condition: valu_mQ,
                "cat_id": 0,
                "expense_id": 0,
                "subcat_id": 0,
                "bgtamount": "",
                "categoryname": "",
                "subcategoryname": ""
            }]
        ppr_df = pd.DataFrame(pprdata["data"])
        bgt_df = pd.DataFrame(bgtdata["data"])
        merge_data = pd.merge(ppr_df, bgt_df, how="left",
                              left_on=[condition, "cat_id", "categoryname", "expense_id", "subcat_id",
                                       "subcategoryname"],
                              right_on=[condition, "cat_id", "categoryname", "expense_id", "subcat_id",
                                        "subcategoryname"])
        final_merge = merge_data[
            [condition, "cat_id", "categoryname", "expense_id", "subcat_id", "subcategoryname", "bgtamount",
             "amount"]].fillna(0)
        logger.info('compare subcat end ')

        return final_merge.to_json(orient="records")
        # except:
        #     return json.dumps([])


    def compare_ppr_bgt_future_subcat(self,future_bgt,ppr_bgt,bgt_obj,pagequery):
        # try:
        logger.info('compare future subcat start')

        future_bgt = json.loads(future_bgt)
        ppr_bgt = json.loads(ppr_bgt)
        keys = Pprutility_keys()
        yearterm = bgt_obj.get_year_term()
        condition = ""
        valu_mQ = ""
        if yearterm == "Monthly":
            condition = keys.transactionmonth
            valu_mQ = "0"
        if yearterm == "Quarterly":
            condition = keys.quarter
            valu_mQ = 0
        if len(ppr_bgt) <= 0:
            ppr_bgt = [{
                condition: valu_mQ,
                "cat_id": 0,
                "categoryname": "",
                "expense_id": 0,
                "subcat_id": 0,
                "subcategoryname": "",
                "bgtamount": "",
                "amount": ""
            }]
        if len(future_bgt["data"]) <= 0:
            future_bgt["data"] = [{
                "cat_id": 0,
                "categoryname": "",
                "expense_id": 0,
                "future_bgtamount": "",
                "subcat_id": 0,
                "subcategoryname": "",
                 "status":0,
                "remark_key":"",
                condition: valu_mQ
            }]
        ppr_bgtDF = pd.DataFrame(ppr_bgt)
        future_bgtDF = pd.DataFrame(future_bgt["data"])
        merge_data = pd.merge(future_bgtDF, ppr_bgtDF, how="outer",
                              left_on=["cat_id", "categoryname",
                                       condition, "expense_id","subcat_id","subcategoryname"],
                              right_on=["cat_id", "categoryname",
                                       condition, "expense_id","subcat_id","subcategoryname"])
        final_merge = merge_data[
            ["cat_id", "categoryname",condition, "expense_id","subcat_id","subcategoryname","future_bgtamount","bgtamount","amount",'status','remark_key']].fillna(0)
        logger.info('compare future subcat end')

        if pagequery !=None and pagequery != "":
            if pagequery == "APPROVER":
                return final_merge[final_merge['status'] == 3.0].to_json(orient="records")
            elif pagequery == "VIEWER":
                return final_merge[final_merge['status'] == 4.0].to_json(orient="records")
            elif pagequery == "CHECKER":
                return final_merge[final_merge['status'] == 2.0].to_json(orient="records")
        if bgt_obj.get_status_id() != None and bgt_obj.get_status_id() != "":
            return final_merge[final_merge['status'] == int(bgt_obj.get_status_id())].to_json(orient="records")


        return final_merge.to_json(orient="records")
        # except:
        #     return json.dumps([])

    def new_subcat_logic(self, subcat_data, ppr_obj):
        subcat_data = json.loads(subcat_data)
        pprservice = Pprservice(self._scope())
        keys = Pprutility_keys()
        output = []
        subcat_datauniq = []
        for i in subcat_data:
            if i["cat_id"] != 0 and i["subcat_id"] != 0 and i["categoryname"] != "" and i["subcategoryname"] != "" and i["expense_id"] != 0:
                if 'transactionmonth' in i:
                    if i["transactionmonth"] != "0":
                        subcat_datauniq.append(i)
                if 'quarter' in i:
                    if i["quarter"] != 0:
                        subcat_datauniq.append(i)
        try:
            if len(subcat_datauniq) <= 0:
                pass
            else:
                year_term = ppr_obj.get_year_term()
                if year_term == "Monthly":
                    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                elif year_term == "Quarterly":
                    month = ["Quarterly_1", "Quarterly_2", "Quarterly_3", "Quarterly_4"]
                else:
                    return {"message": Pprdata_warning.month_quaterneed}
                uniqsubcatname = pprservice.remove_duplicate_arrdict(subcat_datauniq, '', keys.subcat_id, '')
                uniqsubcatlen = len(uniqsubcatname) - 1
                for index, subcat in enumerate(uniqsubcatname):
                    row = {}
                    status = []
                    for imonth in month:
                        row[imonth] = [Decimal(round(Decimal('0.00'), 2)), Decimal(round(Decimal('0.00'), 2)), Decimal(round(Decimal('0.00'), 2))]
                    for uniq_month in subcat_datauniq:
                        if subcat == uniq_month[keys.subcat_id]:
                            row[keys.name] = uniq_month[keys.subcategoryname]
                            if int(uniq_month[keys.status]) not in status:
                                status.append(int(uniq_month[keys.status]))
                            row[keys.remark_key] = uniq_month[keys.remark_key]
                            if year_term == "Monthly":
                                if row[month[int(uniq_month[keys.transactionmonth]) - 1]][1] != Decimal(
                                        round(Decimal('0.00'), 2)):
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][1] = row[month[
                                        int(uniq_month[keys.transactionmonth]) - 1]][1] + Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][0] = row[month[
                                        int(uniq_month[keys.transactionmonth]) - 1]][0] + Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                else:
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][1] = Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][0] = Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                    if row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] != Decimal(
                                            round(Decimal('0.00'), 2)):
                                        row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] = row[month[
                                            int(uniq_month[keys.transactionmonth]) - 1]][2] + Decimal(
                                            round(Decimal(uniq_month["future_bgtamount"]), 2))
                                    else:
                                        row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] = Decimal(
                                            round(Decimal(uniq_month["future_bgtamount"]), 2))
                            if year_term == "Quarterly":
                                if row[f"Quarterly_{uniq_month[keys.quarter]}"][1] != Decimal(
                                        round(Decimal('0.00'), 2)) and f"Quarterly_{uniq_month[keys.quarter]}" in month:
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][1] = row[
                                                                                          f"Quarterly_{uniq_month[keys.quarter]}"][
                                                                                          1] + Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][0] = row[
                                                                                          f"Quarterly_{uniq_month[keys.quarter]}"][
                                                                                          0] + Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                else:
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][1] = Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][0] = Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][2] = Decimal(
                                        round(Decimal(uniq_month["future_bgtamount"]), 2))

                            row[keys.subcat_id] = uniq_month[keys.subcat_id]
                            row[keys.expense_id] = uniq_month[keys.expense_id]
                            if uniqsubcatlen == index:
                                row['page'] = 'Y'
                    ytd = [Decimal(round(Decimal('0.00'), 2)), Decimal(round(Decimal('0.00'), 2)), Decimal(round(Decimal('0.00'), 2))]
                    for i in [0, 1,2]:
                        totalsum = Decimal(round(Decimal('0.00'), 2))
                        for sumof_month in month:
                            totalsum = totalsum + row[sumof_month][i]
                        if i == 2:
                            ytd[i] = Decimal(round(Decimal(totalsum), 2))
                        else:
                            ytd[i] = totalsum
                    status.sort(reverse=True)
                    row[keys.status] = status[0]
                    row[keys.YTD] = ytd
                    row['tree_flag'] = 'Y'
                    row[keys.is_supplier_in] = 'Y'
                    row[keys.Padding_left] = '100px'
                    row[keys.Padding] = '10px'
                    output.append(row)

            return {"data": output}  # "pagination":subcat_data['pagination']
        except:
            return {"data": output}

    def budget_supplier_detials_grp(self,value_obj, supplier_obj):
        if value_obj=='query':
            pro_list = NWisefinList()
            vendorservice=VENDOR_SERVICE(self._scope())
            supplier_detials = vendorservice.get_supplier(supplier_obj.get_supplier_id())
            for supplier in supplier_detials:
                condition = Q(status=4, apexpense_id=supplier_obj.get_apexpense_id(),entity_id=self._entity_id(),
                              apsubcat_id=supplier_obj.get_apsubcat_id(),
                              finyear=supplier_obj.get_finyear())
                groupcondition = ""
                if supplier_obj.get_masterbusinesssegment_name() != None and supplier_obj.get_masterbusinesssegment_name() != "":
                    condition &= Q(bizname=supplier_obj.get_masterbusinesssegment_name())
                if supplier_obj.get_sectorname() != None and supplier_obj.get_sectorname() != "":
                    condition &= Q(sectorname=supplier_obj.get_sectorname())
                if supplier_obj.get_bs_name() != None and supplier_obj.get_bs_name() != "":
                    condition &= Q(bsname=supplier_obj.get_bs_name())
                if supplier_obj.get_cc_name() != None and supplier_obj.get_cc_name() != "":
                    condition &= Q(ccname=supplier_obj.get_cc_name())
                if supplier_obj.get_apinvoicebranch_id() != None and supplier_obj.get_apinvoicebranch_id() != "":
                    condition &= Q(apinvoicebranch_id=supplier_obj.get_apinvoicebranch_id())
                if supplier_obj.get_supplier_id() != None and supplier_obj.get_supplier_id() != "" and len(
                        supplier_obj.get_supplier_id()) > 0:
                    condition &= Q(apinvoicesupplier_id=supplier["supplier_id"])
                if supplier_obj.get_yearterm() == "Monthly":
                    groupcondition = "transactionmonth"
                if supplier_obj.get_yearterm() == "Quarterly":
                    groupcondition = "quarter"
                bgt_obj = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values("apsubcat_id", "apexpense_id", "apinvoicesupplier_id",
                                                                        groupcondition).annotate(
                    totalamount=Sum('amount'))
                if len(bgt_obj) <= 0:
                    supplier_ids = []
                    supplier_ids.append(supplier["supplier_id"])
                    vendorservice = VENDOR_SERVICE(self._scope())
                    supplier_detials = vendorservice.get_supplier(supplier_ids)
                    if supplier_obj.get_yearterm() == 'Monthly':
                        tranmon1 = 4
                        for f in range(0, 12):
                            tranmon = tranmon1
                            if tranmon1 == 13:
                                tranmon = 1
                            if tranmon1 == 14:
                                tranmon = 2
                            if tranmon1 == 15:
                                tranmon = 3
                            bgtresponser = BudgetBuilderresponse()
                            bgtresponser.set_supplier_detial(supplier_detials, supplier["supplier_id"])
                            bgtresponser.set_apexpense_id(supplier_obj.get_apexpense_id())
                            bgtresponser.set_apsubcat_id(supplier_obj.get_apsubcat_id())
                            bgtresponser.set_bgtamount(str(Decimal(0.0) / supplier_obj.get_divAmount()))
                            bgtresponser.set_transactionmonth(str(tranmon))
                            pro_list.data.append(bgtresponser)
                            tranmon1 = tranmon1 + 1
                    if supplier_obj.get_yearterm() == 'Quarterly':
                        tranmon1 = 1
                        for f in range(0, 4):
                            tranmon = tranmon1
                            bgtresponser = BudgetBuilderresponse()
                            bgtresponser.set_supplier_detial(supplier_detials, supplier["supplier_id"])
                            bgtresponser.set_apexpense_id(supplier_obj.get_apexpense_id())
                            bgtresponser.set_apsubcat_id(supplier_obj.get_apsubcat_id())
                            bgtresponser.set_bgtamount(str(Decimal(0.0) / supplier_obj.get_divAmount()))
                            bgtresponser.set_quarter(tranmon)
                            pro_list.data.append(bgtresponser)
                            tranmon1 = tranmon1 + 1
                else:
                    supplier_id = []
                    for i in bgt_obj:
                        supplier_id.append(i["apinvoicesupplier_id"])
                    service = VENDOR_SERVICE(self._scope())
                    supplier_detials = service.get_supplier(supplier_id)
                    for i in bgt_obj:
                        bgtresponser = BudgetBuilderresponse()
                        if supplier_obj.get_yearterm() == "Monthly":
                            bgtresponser.set_transactionmonth(i["transactionmonth"])
                        if supplier_obj.get_yearterm() == "Quarterly":
                            bgtresponser.set_quarter(i["quarter"])
                        bgtresponser.set_bgtamount(str(Decimal(i["totalamount"]) / supplier_obj.get_divAmount()))
                        bgtresponser.set_supplier_detial(supplier_detials, i["apinvoicesupplier_id"])
                        bgtresponser.set_apexpense_id(i["apexpense_id"])
                        bgtresponser.set_apsubcat_id(i["apsubcat_id"])
                        pro_list.data.append(bgtresponser)
            return pro_list
        else:
                condition = Q(status=3, apexpense_id=supplier_obj.get_apexpense_id(),
                              apsubcat_id=supplier_obj.get_apsubcat_id(),entity_id=self._entity_id(),
                              finyear=supplier_obj.get_finyear())
                groupcondition = ""
                if supplier_obj.get_masterbusinesssegment_name() != None and supplier_obj.get_masterbusinesssegment_name() != "":
                    condition &= Q(bizname=supplier_obj.get_masterbusinesssegment_name())
                if supplier_obj.get_sectorname() != None and supplier_obj.get_sectorname() != "":
                    condition &= Q(sectorname=supplier_obj.get_sectorname())
                if supplier_obj.get_bs_name() != None and supplier_obj.get_bs_name() != "":
                    condition &= Q(bsname=supplier_obj.get_bs_name())
                if supplier_obj.get_cc_name() != None and supplier_obj.get_cc_name() != "":
                    condition &= Q(ccname=supplier_obj.get_cc_name())
                if supplier_obj.get_apinvoicebranch_id() != None and supplier_obj.get_apinvoicebranch_id() != "":
                    condition &= Q(apinvoicebranch_id=supplier_obj.get_apinvoicebranch_id())
                if supplier_obj.get_supplier_id() != None and supplier_obj.get_supplier_id() != "" and len(
                        supplier_obj.get_supplier_id()) > 0:
                    condition &= Q(apinvoicesupplier_id__in=supplier_obj.get_supplier_id())
                if supplier_obj.get_yearterm() == "Monthly":
                    groupcondition = "transactionmonth"
                if supplier_obj.get_yearterm() == "Quarterly":
                    groupcondition = "quarter"
                bgt_obj = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values("apsubcat_id",
                                                                                               "apexpense_id",
                                                                                               "apinvoicesupplier_id",
                                                                                               groupcondition).annotate(
                    totalamount=Sum('amount'))
                pro_list = NWisefinList()
                if len(bgt_obj) <= 0:
                    pass
                else:
                    supplier_id = []
                    for i in bgt_obj:
                        supplier_id.append(i["apinvoicesupplier_id"])
                    service = VENDOR_SERVICE(self._scope())
                    supplier_detials = service.get_supplier(supplier_id)
                    for i in bgt_obj:
                        bgtresponser = BudgetBuilderresponse()
                        if supplier_obj.get_yearterm() == "Monthly":
                            bgtresponser.set_transactionmonth(i["transactionmonth"])
                        if supplier_obj.get_yearterm() == "Quarterly":
                            bgtresponser.set_quarter(i["quarter"])
                        bgtresponser.set_bgtamount(str(Decimal(i["totalamount"]) / supplier_obj.get_divAmount()))
                        bgtresponser.set_supplier_detial(supplier_detials, i["apinvoicesupplier_id"])
                        bgtresponser.set_apexpense_id(i["apexpense_id"])
                        bgtresponser.set_apsubcat_id(i["apsubcat_id"])
                        pro_list.data.append(bgtresponser)
                return pro_list

    def compare_ppr_bgt_suppliergrp(self, pprdata, bgtdata, bgt_obj):
        # try:
        logger.info('compare supplier start')
        pprdata = json.loads(pprdata)
        bgtdata = json.loads(bgtdata)
        keys = Pprutility_keys()
        yearterm = bgt_obj.get_yearterm()
        condition = ""
        valu_mQ = ""
        if yearterm == "Monthly":
            condition = keys.transactionmonth
            valu_mQ = "0"
        if yearterm == "Quarterly":
            condition = keys.quarter
            valu_mQ = 0
        if len(pprdata["data"]) <= 0:
            pprdata["data"] = [{
                condition: valu_mQ,
                "supplier_branchname": "",
                "supplier_code": "",
                "supplier_gstno": "",
                "supplier_id": 0,
                "supplier_name": "",
                "supplier_panno": "",
                "totamount": "",
                "apexpense_id": 0,
                "apsubcat_id": 0
            }]
        if len(bgtdata["data"]) <= 0:
            bgtdata["data"] = [{
                condition: valu_mQ,
                "supplier_branchname": "",
                "supplier_code": "",
                "supplier_gstno": "",
                "supplier_id": 0,
                "supplier_name": "",
                "supplier_panno": "",
                "bgtamount": "",
                "apexpense_id": 0,
                "apsubcat_id": 0
            }]
        ppr_df = pd.DataFrame(pprdata["data"])
        bgt_df = pd.DataFrame(bgtdata["data"])
        merge_data = pd.merge(ppr_df, bgt_df, how="left",
                              left_on=["apexpense_id", "apsubcat_id", "supplier_branchname", "supplier_code",
                                       "supplier_gstno", "supplier_id", "supplier_name", "supplier_panno",
                                       condition],
                              right_on=["apexpense_id", "apsubcat_id", "supplier_branchname", "supplier_code",
                                        "supplier_gstno", "supplier_id", "supplier_name", "supplier_panno",
                                        condition])
        final_merge = merge_data[
            ["supplier_branchname", "supplier_code", "supplier_gstno", "supplier_id", "supplier_name",
             "supplier_panno", condition, "totamount", "bgtamount", "apexpense_id", "apsubcat_id"]].fillna(0)
        logger.info('compare supplier end')

        return final_merge.to_json(orient="records")
        # except:
        #     return json.dumps([])

    def get_budget_supplier_zero(self,INarr):
        INarr = json.loads(INarr)
        Outarr = []
        if len(INarr['data']) <= 0:
            pass
        else:
            for i in INarr['data']:
                if i["supplier_id"] == 0 or int(i["supplier_id"]) == -1:
                    i['totamount']="0.00"
                    i['future_bgtamount']="0.00"
                    Outarr.append(i)
        return Outarr

    def budget_suppliergrp_logic(self, supplier_data,supplier_zeroIDArr, supplier_obj):
        # try:
        pprservice = Pprservice(self._scope())
        supplier_data = json.loads(supplier_data)
        if len(supplier_data) > 0:
            keys = Pprutility_keys
            year_term = supplier_obj.get_yearterm()
            if year_term == "Monthly":
                month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            elif year_term == "Quarterly":
                month = ["Quarterly_1", "Quarterly_2", "Quarterly_3", "Quarterly_4"]
            else:
                return {"message": Pprdata_warning.month_quaterneed}
            supplier_datauniq = []
            supplier_data.extend(supplier_zeroIDArr)
            for k in supplier_data:
                if k["supplier_branchname"] != "" and k["supplier_code"] != "" and k["supplier_name"] != "":
                    if 'transactionmonth' in k:
                        if k["transactionmonth"] != "0":
                            supplier_datauniq.append(k)
                    if 'quarter' in k:
                        if k["quarter"] != 0:
                            supplier_datauniq.append(k)
            supplier_name = []
            for i in supplier_datauniq:
                if i['supplier_name'] not in supplier_name:
                    supplier_name.append(i['supplier_name'])
            output = []
            for name in supplier_name:
                supplier_row = {}
                supplier_row[keys.name] = name
                status = []
                for imonth in month:
                    supplier_row[imonth] = [Decimal(round(Decimal('0.00'), 2)), Decimal(round(Decimal('0.00'), 2)),
                                            Decimal(round(Decimal('0.00'), 2))]
                supplier_row[keys.YTD] = Decimal(round(Decimal('0.00'), 2))#str(a).split('.')[0]+'.'+str(a).split('.')[1][0:2]
                for apidata in supplier_datauniq:
                    if apidata['supplier_name'] == name:
                        if int(apidata[keys.status]) not in status:
                            status.append(int(apidata[keys.status]))
                        supplier_row[keys.remark_key] = apidata[keys.remark_key]
                        if year_term == "Monthly":
                            if supplier_row[month[int(apidata[keys.transactionmonth]) - 1]][1] != Decimal(
                                    round(Decimal('0.00'), 2)):
                                supplier_row[month[int(apidata[keys.transactionmonth]) - 1]][1] = supplier_row[month[
                                        int(apidata[keys.transactionmonth]) - 1]][1] + Decimal(
                                        round(Decimal(apidata["totamount"]), 2))
                                supplier_row[month[int(apidata[keys.transactionmonth]) - 1]][0] = supplier_row[month[
                                        int(apidata[keys.transactionmonth]) - 1]][0] + Decimal(
                                        round(Decimal(apidata["bgtamount"]), 2))
                            else:
                                supplier_row[month[int(apidata[keys.transactionmonth]) - 1]][1] = Decimal(
                                    round(Decimal(apidata["totamount"]), 2))
                                supplier_row[month[int(apidata[keys.transactionmonth]) - 1]][0] = Decimal(
                                    round(Decimal(apidata["bgtamount"]), 2))
                                if supplier_row[month[int(apidata[keys.transactionmonth]) - 1]][2] != Decimal(round(Decimal('0.00'), 2)):
                                    supplier_row[month[int(apidata[keys.transactionmonth]) - 1]][2] = supplier_row[month[
                                        int(apidata[keys.transactionmonth]) - 1]][2]+Decimal(
                                        round(Decimal(apidata["future_bgtamount"]), 2))
                                else:
                                    supplier_row[month[int(apidata[keys.transactionmonth]) - 1]][2] = Decimal(
                                        round(Decimal(apidata["future_bgtamount"]), 2))

                        if year_term == "Quarterly":
                            if supplier_row[f"Quarterly_{apidata[keys.quarter]}"][1] != Decimal(
                                    round(Decimal('0.00'), 2)) and f"Quarterly_{apidata[keys.quarter]}" in month:
                                supplier_row[f"Quarterly_{apidata[keys.quarter]}"][1] = supplier_row[
                                                                                            f"Quarterly_{apidata[keys.quarter]}"][
                                                                                            1] + Decimal(
                                    round(Decimal(apidata["totamount"]), 2))
                                supplier_row[f"Quarterly_{apidata[keys.quarter]}"][0] = supplier_row[
                                                                                            f"Quarterly_{apidata[keys.quarter]}"][
                                                                                            0] + Decimal(
                                    round(Decimal(apidata["bgtamount"]), 2))
                            else:
                                supplier_row[f"Quarterly_{apidata[keys.quarter]}"][1] = Decimal(
                                    round(Decimal(apidata["totamount"]), 2))
                                supplier_row[f"Quarterly_{apidata[keys.quarter]}"][0] = Decimal(
                                    round(Decimal(apidata["bgtamount"]), 2))
                                supplier_row[f"Quarterly_{apidata[keys.quarter]}"][2] = Decimal(
                                    round(Decimal(apidata["future_bgtamount"]), 2))

                        pprservice.supplier_need_dict(supplier_row, keys, apidata, year_term)
                        supplier_row[keys.apexpense_id] = apidata[keys.apexpense_id]
                        supplier_row[keys.apsubcat_id] = apidata[keys.apsubcat_id]

                ytd = [Decimal(round(Decimal('0.00'), 2)), Decimal(round(Decimal('0.00'), 2)), ""]
                for i in [0, 1, 2]:
                    totalsum = Decimal(round(Decimal('0.00'), 2))
                    for sumof_month in month:
                        totalsum = totalsum + supplier_row[sumof_month][i]
                    if i == 2:
                        ytd[i] = Decimal(round(Decimal(totalsum), 2))
                    else:
                        ytd[i] = totalsum
                status.sort(reverse=True)
                supplier_row[keys.status] = status[0]
                supplier_row[keys.YTD] = ytd
                supplier_row[keys.Padding_left] = '120px'
                supplier_row[keys.Padding] = '10px'
                supplier_row["new_data"] = "N"
                output.append(supplier_row)
            return {"data": output}
        else:
            return {"data": []}
        # except:
        #     return {"data": []}

    def bgt_future_data_set(self, bgt_data,remark, empid,divAmount):
        keys = Pprutility_keys()
        utility = Ppr_utilityservice(self._scope())
        remark_key_gen = "RE_" + str(datetime.datetime.now().strftime("%y%m%d_%H%M%S"))
        for i in bgt_data:
            condition = Q(finyear=i[keys.finyear], quarter=i[keys.quarter], transactionmonth=i[keys.transactionmonth],
                          transactionyear=i[keys.transactionyear],
                          sectorname=i[keys.sectorname], bizname=i["masterbusinesssegment_name"],entity_id=self._entity_id(),
                          apsubcat_id=i[keys.subcat_id], apexpense_id=i[keys.expense_id])
            branch_id = None
            supplier_id = None
            bs_name = None
            cc_name = None
            if i["branch_id"] != "":
                condition &= Q(apinvoicebranch_id=i["branch_id"])
                branch_id = i["branch_id"]
            if i["supplier_id"] != "":
                condition &= Q(apinvoicesupplier_id=i["supplier_id"])
                supplier_id = i["supplier_id"]
            if i["bs_name"] != "":
                condition &= Q(bsname=i["bs_name"])
                bs_name = i["bs_name"]
            if i["cc_name"] != "":
                condition &= Q(ccname=i["cc_name"])
                cc_name = i["cc_name"]
            future_bgtamount = Decimal(i["future_bgtamount"]) * divAmount.get_divAmount()
            # branch_code_lock = EmployeeBranch.objects.using(DataBase.default_db).get(code=9999)
            # check_branch_exist = Budgetdetial.objects.using(DataBase.fas_db).filter(finyear=i[keys.finyear], quarter=i[keys.quarter], transactionmonth=i[keys.transactionmonth],
            #               transactionyear=i[keys.transactionyear],
            #               sectorname=i[keys.sectorname], bizname=i["masterbusinesssegment_name"],
            #               apinvoicebranch_id=branch_code_lock.id,bsname=i["bs_name"],ccname=i["cc_name"],status=i["status"]).exists()
            # if check_branch_exist == True:
            #     res = budget_reject_response()
            #     res.set_message(res.branch_message)
            #     res.set_status(res.status_message)
            #     return res


            bgtdetials_obj = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).exists()
            if bgtdetials_obj == True:
            # if bgtdetials_obj == True and int(i["supplier_id"]) != 0:
                bgtTdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).update(finyear=i[keys.finyear], quarter=i[keys.quarter],
                                                                         transactionmonth=i[keys.transactionmonth],
                                                                         transactionyear=i[keys.transactionyear],
                                                                         sectorname=i[keys.sectorname],
                                                                         bizname=i["masterbusinesssegment_name"],
                                                                         apsubcat_id=i[keys.subcat_id],
                                                                         apexpense_id=i[keys.expense_id],
                                                                         amount=future_bgtamount,
                                                                         status=i["status"],
                                                                         apinvoicebranch_id=i["branch_id"],
                                                                         updated_date=now(), updated_by=empid,entity_id=self._entity_id())

                remarkKey = Budgetdetial.objects.using(self._current_app_schema()).filter(condition)[0]
                self.audit_function(i,ReftableType().BudgetBuilder,empid,CRUDstatus().update)
                if int(i["status"]) == 2:
                    utility.mantain_history(empid, keys.Budget_maker, i, CRUDstatus().update,remarkKey.remark_key,remark)
            else:
                bgtTdata = Budgetdetial.objects.using(self._current_app_schema()).create(finyear=i[keys.finyear], quarter=i[keys.quarter],
                                                       transactionmonth=i[keys.transactionmonth],
                                                       transactionyear=i[keys.transactionyear],
                                                       sectorname=i[keys.sectorname],
                                                       bizname=i["masterbusinesssegment_name"],
                                                       apsubcat_id=i[keys.subcat_id], apexpense_id=i[keys.expense_id],
                                                       transactiondate=f"{i[keys.transactionyear]}-{i[keys.transactionmonth]}-1",
                                                       valuedate=f"{i[keys.transactionyear]}-{i[keys.transactionmonth]}-1",
                                                       amount=future_bgtamount, status=i["status"],
                                                       apinvoicebranch_id=branch_id,
                                                       apinvoicesupplier_id=supplier_id, bsname=bs_name,
                                                       ccname=cc_name,remark_key=remark_key_gen,
                                                       created_by=empid,entity_id=self._entity_id())
                self.audit_function(i, ReftableType().BudgetBuilder, empid, CRUDstatus().create)
                if int(i["status"]) == 2:
                    utility.mantain_history(empid, keys.Budget_maker, i, CRUDstatus().create,remark_key_gen,remark)
                elif int(i["status"]) == 1:
                    utility.mantain_history(empid, keys.Budget_draft, i, CRUDstatus().create,remark_key_gen,remark)
        suc_obj = Success()
        suc_obj.set_status(successMessage.SUCCESS)
        return suc_obj

    def bgt_future_data_viewer_set(self, bgt_data,remark, empid,divAmount):
        keys = Pprutility_keys()
        utility = Ppr_utilityservice(self._scope())
        for i in bgt_data:
            condition = Q(finyear=i[keys.finyear], quarter=i[keys.quarter], transactionmonth=i[keys.transactionmonth],
                          transactionyear=i[keys.transactionyear],
                          sectorname=i[keys.sectorname], bizname=i["masterbusinesssegment_name"],
                          apsubcat_id=i[keys.subcat_id], apexpense_id=i[keys.expense_id],entity_id=self._entity_id())
            branch_id = None
            supplier_id = None
            bs_name = None
            cc_name = None
            if i["branch_id"] != "":
                condition &= Q(apinvoicebranch_id=i["branch_id"])
                branch_id = i["branch_id"]
            if i["supplier_id"] != "":
                condition &= Q(apinvoicesupplier_id=i["supplier_id"])
                supplier_id = i["supplier_id"]
            if i["bs_name"] != "":
                condition &= Q(bsname=i["bs_name"])
                bs_name = i["bs_name"]
            if i["cc_name"] != "":
                condition &= Q(ccname=i["cc_name"])
                cc_name = i["cc_name"]
            future_bgtamount = Decimal(i["future_bgtamount"]) * divAmount.get_divAmount()

            # branch_code_lock = EmployeeBranch.objects.using(DataBase.default_db).get(code=9999)
            # check_branch_exist = Budgetdetial.objects.using(DataBase.fas_db).filter(finyear=i[keys.finyear],
            #                                                                         quarter=i[keys.quarter],
            #                                                                         transactionmonth=i[
            #                                                                             keys.transactionmonth],
            #                                                                         transactionyear=i[
            #                                                                             keys.transactionyear],
            #                                                                         sectorname=i[keys.sectorname],
            #                                                                         bizname=i[
            #                                                                             "masterbusinesssegment_name"],
            #                                                                         apinvoicebranch_id=branch_code_lock.id,
            #                                                                         bsname=i["bs_name"],
            #                                                                         ccname=i["cc_name"],
            #                                                                         status=i["status"]).exists()
            # if check_branch_exist == True:
            #     res = budget_reject_response()
            #     res.set_message(res.branch_message)
            #     res.set_status(res.status_message)
            #     return res
            bgtdetials_obj = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).exists()
            if bgtdetials_obj == True:
                bgtTdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).update(finyear=i[keys.finyear], quarter=i[keys.quarter],
                                                                         transactionmonth=i[keys.transactionmonth],
                                                                         transactionyear=i[keys.transactionyear],
                                                                         sectorname=i[keys.sectorname],
                                                                         bizname=i["masterbusinesssegment_name"],
                                                                         apsubcat_id=i[keys.subcat_id],
                                                                         apexpense_id=i[keys.expense_id],
                                                                         amount=future_bgtamount,
                                                                         status=i["status"],
                                                                         apinvoicebranch_id=i["branch_id"],entity_id=self._entity_id(),
                                                                         updated_date=now(), updated_by=empid)
                remarkKey = Budgetdetial.objects.using(self._current_app_schema()).filter(condition)[0]
                self.audit_function(i,ReftableType().BudgetApproval,empid,CRUDstatus().update)
                if int(i["status"]) == 3:
                    utility.mantain_history(empid, keys.Budget_checker, i, CRUDstatus().update,remarkKey.remark_key,remark)
                elif int(i["status"]) == 4:
                    utility.mantain_history(empid, keys.Budget_approver, i, CRUDstatus().update, remarkKey.remark_key,
                                            remark)
                elif int(i["status"]) == 6:
                    utility.mantain_history(empid, keys.Budget_reject, i, CRUDstatus().update, remarkKey.remark_key,
                                            remark)
                else:
                    utility.mantain_history(empid, keys.Budget_approver, i, CRUDstatus().update)
            else:
                bgtTdata = Budgetdetial.objects.using(self._current_app_schema()).create(finyear=i[keys.finyear], quarter=i[keys.quarter],
                                                       transactionmonth=i[keys.transactionmonth],
                                                       transactionyear=i[keys.transactionyear],
                                                       sectorname=i[keys.sectorname],
                                                       bizname=i["masterbusinesssegment_name"],
                                                       apsubcat_id=i[keys.subcat_id], apexpense_id=i[keys.expense_id],
                                                       transactiondate=f"{i[keys.transactionyear]}-{i[keys.transactionmonth]}-1",
                                                       valuedate=f"{i[keys.transactionyear]}-{i[keys.transactionmonth]}-1",
                                                       amount=future_bgtamount, status=i["status"],
                                                       apinvoicebranch_id=branch_id,
                                                       apinvoicesupplier_id=supplier_id, bsname=bs_name,
                                                       ccname=cc_name,
                                                       created_by=empid,entity_id=self._entity_id())
                self.audit_function(i, ReftableType().BudgetApproval, empid, CRUDstatus().create)
                utility.mantain_history(empid, keys.Budget_approver, i, CRUDstatus().create)

        suc_obj = Success()
        suc_obj.set_status(successMessage.SUCCESS)
        return suc_obj

    def future_budget_supplier_detials_grp(self,value_obj, supplier_obj,pagequery):
        if value_obj=='query':
            pro_list = NWisefinList()
            service = VENDOR_SERVICE(self._scope())
            supplier_detials = service.get_supplier(supplier_obj.get_supplier_id())
            # pprutility = Ppr_utilityservice(self._scope())
            supplier_ = supplier_obj.get_supplier_id()
            # supplier_detials = pprutility.get_supplier(supplier_obj.get_supplier_id())
            if len(supplier_detials) != 0 and 0 not in supplier_:
                for supplier in supplier_detials:
                    condition = Q(apexpense_id=supplier_obj.get_apexpense_id(),
                                  apsubcat_id=supplier_obj.get_apsubcat_id(),entity_id=self._entity_id(),
                                  finyear=f'FY{int(supplier_obj.get_finyear().split("-")[0][-2:]) + 1}-{int(supplier_obj.get_finyear().split("-")[1]) + 1}')
                    groupcondition = ""
                    if supplier_obj.get_status_id() != None and supplier_obj.get_status_id() != "":
                        condition &= Q(status=supplier_obj.get_status_id())
                    if pagequery != None and pagequery != "":
                        if pagequery == "APPROVER":
                            condition &= Q(status=3)
                        elif pagequery == "CHECKER":
                            condition &= Q(status=2)
                        elif pagequery == "VIEWER":
                            condition &= Q(status=4)
                    if supplier_obj.get_masterbusinesssegment_name() != None and supplier_obj.get_masterbusinesssegment_name() != "":
                        condition &= Q(bizname=supplier_obj.get_masterbusinesssegment_name())
                    if supplier_obj.get_sectorname() != None and supplier_obj.get_sectorname() != supplier_obj.get_sectorname():
                        condition &= Q(sectorname=supplier_obj.get_sectorname())
                    if supplier_obj.get_bs_name() != None and supplier_obj.get_bs_name() != "":
                        condition &= Q(bsname=supplier_obj.get_bs_name())
                    if supplier_obj.get_cc_name() != None and supplier_obj.get_cc_name() != "":
                        condition &= Q(ccname=supplier_obj.get_cc_name())
                    if supplier_obj.get_apinvoicebranch_id() != None and supplier_obj.get_apinvoicebranch_id() != "":
                        condition &= Q(apinvoicebranch_id=supplier_obj.get_apinvoicebranch_id())
                    if supplier_obj.get_supplier_id() != None and supplier_obj.get_supplier_id() != "" and len(
                            supplier_obj.get_supplier_id()) > 0:
                        condition &= Q(apinvoicesupplier_id=supplier["supplier_id"])
                    if supplier_obj.get_yearterm() == "Monthly":
                        groupcondition = "transactionmonth"
                    if supplier_obj.get_yearterm() == "Quarterly":
                        groupcondition = "quarter"
                    bgt_obj = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values("apsubcat_id", "apexpense_id", "apinvoicesupplier_id",'status','remark_key',
                                                                            groupcondition).annotate(
                        fut_bgt_amount=Sum('amount'))
                    if len(bgt_obj) <= 0:
                        supplier_ids = []
                        supplier_ids.append(supplier["supplier_id"])
                        service = VENDOR_SERVICE(self._scope())
                        supplier_detials = service.get_supplier(supplier_ids)
                        if supplier_obj.get_yearterm() == 'Monthly':
                            tranmon1 = 4
                            for f in range(0, 12):
                                tranmon = tranmon1
                                if tranmon1 == 13:
                                    tranmon = 1
                                if tranmon1 == 14:
                                    tranmon = 2
                                if tranmon1 == 15:
                                    tranmon = 3
                                bgtresponser = BudgetBuilderresponse()
                                bgtresponser.set_supplier_detial(supplier_detials, supplier["supplier_id"])
                                bgtresponser.set_apexpense_id(supplier_obj.get_apexpense_id())
                                bgtresponser.set_apsubcat_id(supplier_obj.get_apsubcat_id())
                                bgtresponser.set_future_bgtamount(str(Decimal(0.0) / supplier_obj.get_divAmount()))
                                bgtresponser.set_transactionmonth(str(tranmon))
                                bgtresponser.set_status(0)
                                bgtresponser.set_remark_key("")
                                pro_list.data.append(bgtresponser)
                                tranmon1 = tranmon1 + 1
                        if supplier_obj.get_yearterm() == 'Quarterly':
                            tranmon1 = 1
                            for f in range(0, 4):
                                tranmon = tranmon1
                                bgtresponser = BudgetBuilderresponse()
                                bgtresponser.set_supplier_detial(supplier_detials, supplier["supplier_id"])
                                bgtresponser.set_apexpense_id(supplier_obj.get_apexpense_id())
                                bgtresponser.set_apsubcat_id(supplier_obj.get_apsubcat_id())
                                bgtresponser.set_future_bgtamount(str(Decimal(0.0) / supplier_obj.get_divAmount()))
                                bgtresponser.set_quarter(tranmon)
                                bgtresponser.set_status(0)
                                bgtresponser.set_remark_key("")
                                pro_list.data.append(bgtresponser)
                                tranmon1 = tranmon1 + 1
                    else:
                        supplier_id = []
                        for i in bgt_obj:
                            supplier_id.append(i["apinvoicesupplier_id"])
                        service = VENDOR_SERVICE(self._scope())
                        supplier_detials = service.get_supplier(supplier_id)
                        for i in bgt_obj:
                            bgtresponser = BudgetBuilderresponse()
                            if supplier_obj.get_yearterm() == "Monthly":
                                bgtresponser.set_transactionmonth(i["transactionmonth"])
                            if supplier_obj.get_yearterm() == "Quarterly":
                                bgtresponser.set_quarter(i["quarter"])
                            bgtresponser.set_status(i['status'])
                            bgtresponser.set_remark_key(i['remark_key'])
                            bgtresponser.set_future_bgtamount(str(Decimal(i["fut_bgt_amount"])/ supplier_obj.get_divAmount()))
                            bgtresponser.set_supplier_detial(supplier_detials, i["apinvoicesupplier_id"])
                            bgtresponser.set_apexpense_id(i["apexpense_id"])
                            bgtresponser.set_apsubcat_id(i["apsubcat_id"])
                            pro_list.data.append(bgtresponser)
                return pro_list
            else:
                condition = Q(apexpense_id=supplier_obj.get_apexpense_id(),
                              apsubcat_id=supplier_obj.get_apsubcat_id(),
                              finyear=f'FY{int(supplier_obj.get_finyear().split("-")[0][-2:]) + 1}-{int(supplier_obj.get_finyear().split("-")[1]) + 1}')
                groupcondition = ""
                if supplier_obj.get_status_id() != None and supplier_obj.get_status_id() != "":
                    condition &= Q(status=supplier_obj.get_status_id())
                if pagequery != None and pagequery != "":
                    if pagequery == "APPROVER":
                        condition &= Q(status=3)
                    elif pagequery == "CHECKER":
                        condition &= Q(status=2)
                    elif pagequery == "VIEWER":
                        condition &= Q(status=4)
                if supplier_obj.get_masterbusinesssegment_name() != None and supplier_obj.get_masterbusinesssegment_name() != "":
                    condition &= Q(bizname=supplier_obj.get_masterbusinesssegment_name())
                if supplier_obj.get_sectorname() != None and supplier_obj.get_sectorname() != supplier_obj.get_sectorname():
                    condition &= Q(sectorname=supplier_obj.get_sectorname())
                if supplier_obj.get_bs_name() != None and supplier_obj.get_bs_name() != "":
                    condition &= Q(bsname=supplier_obj.get_bs_name())
                if supplier_obj.get_cc_name() != None and supplier_obj.get_cc_name() != "":
                    condition &= Q(ccname=supplier_obj.get_cc_name())
                if supplier_obj.get_apinvoicebranch_id() != None and supplier_obj.get_apinvoicebranch_id() != "":
                    condition &= Q(apinvoicebranch_id=supplier_obj.get_apinvoicebranch_id())
                if supplier_obj.get_supplier_id() != None and supplier_obj.get_supplier_id() != "" and len(
                        supplier_obj.get_supplier_id()) > 0:
                    condition &= Q(apinvoicesupplier_id__in=supplier_obj.get_supplier_id())
                if supplier_obj.get_yearterm() == "Monthly":
                    groupcondition = "transactionmonth"
                if supplier_obj.get_yearterm() == "Quarterly":
                    groupcondition = "quarter"
                bgt_obj = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values("apsubcat_id",
                                                                                               "apexpense_id",
                                                                                               "apinvoicesupplier_id",
                                                                                               'status', 'remark_key',
                                                                                               groupcondition).annotate(
                    fut_bgt_amount=Sum('amount'))
                pro_list = NWisefinList()
                if len(bgt_obj) <= 0:
                    pass
                else:
                    supplier_id = []
                    for i in bgt_obj:
                        supplier_id.append(i["apinvoicesupplier_id"])
                    service = VENDOR_SERVICE(self._scope())
                    supplier_detials = service.get_supplier(supplier_id)
                    for i in bgt_obj:
                        bgtresponser = BudgetBuilderresponse()
                        if supplier_obj.get_yearterm() == "Monthly":
                            bgtresponser.set_transactionmonth(i["transactionmonth"])
                        if supplier_obj.get_yearterm() == "Quarterly":
                            bgtresponser.set_quarter(i["quarter"])
                        bgtresponser.set_status(i['status'])
                        bgtresponser.set_remark_key(i['remark_key'])
                        bgtresponser.set_future_bgtamount(
                            str(Decimal(i["fut_bgt_amount"]) / supplier_obj.get_divAmount()))
                        bgtresponser.set_supplier_detial(supplier_detials, i["apinvoicesupplier_id"])
                        bgtresponser.set_apexpense_id(i["apexpense_id"])
                        bgtresponser.set_apsubcat_id(i["apsubcat_id"])
                        pro_list.data.append(bgtresponser)
                return pro_list
        else:

                condition = Q(apexpense_id=supplier_obj.get_apexpense_id(),
                              apsubcat_id=supplier_obj.get_apsubcat_id(),
                              finyear=f'FY{int(supplier_obj.get_finyear().split("-")[0][-2:]) + 1}-{int(supplier_obj.get_finyear().split("-")[1]) + 1}')
                groupcondition = ""
                if supplier_obj.get_status_id() != None and supplier_obj.get_status_id() != "":
                    condition &= Q(status=supplier_obj.get_status_id())
                if pagequery != None and pagequery != "":
                    if pagequery == "APPROVER":
                        condition &= Q(status=3)
                    elif pagequery == "CHECKER":
                        condition &= Q(status=2)
                    elif pagequery == "VIEWER":
                        condition &= Q(status=4)
                if supplier_obj.get_masterbusinesssegment_name() != None and supplier_obj.get_masterbusinesssegment_name() != "":
                    condition &= Q(bizname=supplier_obj.get_masterbusinesssegment_name())
                if supplier_obj.get_sectorname() != None and supplier_obj.get_sectorname() != supplier_obj.get_sectorname():
                    condition &= Q(sectorname=supplier_obj.get_sectorname())
                if supplier_obj.get_bs_name() != None and supplier_obj.get_bs_name() != "":
                    condition &= Q(bsname=supplier_obj.get_bs_name())
                if supplier_obj.get_cc_name() != None and supplier_obj.get_cc_name() != "":
                    condition &= Q(ccname=supplier_obj.get_cc_name())
                if supplier_obj.get_apinvoicebranch_id() != None and supplier_obj.get_apinvoicebranch_id() != "":
                    condition &= Q(apinvoicebranch_id=supplier_obj.get_apinvoicebranch_id())
                if supplier_obj.get_supplier_id() != None and supplier_obj.get_supplier_id() != "" and len(
                        supplier_obj.get_supplier_id()) > 0:
                    condition &= Q(apinvoicesupplier_id__in=supplier_obj.get_supplier_id())
                if supplier_obj.get_yearterm() == "Monthly":
                    groupcondition = "transactionmonth"
                if supplier_obj.get_yearterm() == "Quarterly":
                    groupcondition = "quarter"
                bgt_obj = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values("apsubcat_id",
                                                                                               "apexpense_id",
                                                                                               "apinvoicesupplier_id",
                                                                                               'status', 'remark_key',
                                                                                               groupcondition).annotate(
                    fut_bgt_amount=Sum('amount'))
                pro_list = NWisefinList()
                if len(bgt_obj) <= 0:
                    pass
                else:
                    supplier_id = []
                    for i in bgt_obj:
                        supplier_id.append(i["apinvoicesupplier_id"])
                    service = VENDOR_SERVICE(self._scope())
                    supplier_detials = service.get_supplier(supplier_id)
                    for i in bgt_obj:
                        bgtresponser = BudgetBuilderresponse()
                        if supplier_obj.get_yearterm() == "Monthly":
                            bgtresponser.set_transactionmonth(i["transactionmonth"])
                        if supplier_obj.get_yearterm() == "Quarterly":
                            bgtresponser.set_quarter(i["quarter"])
                        bgtresponser.set_status(i['status'])
                        bgtresponser.set_remark_key(i['remark_key'])
                        bgtresponser.set_future_bgtamount(
                            str(Decimal(i["fut_bgt_amount"]) / supplier_obj.get_divAmount()))
                        bgtresponser.set_supplier_detial(supplier_detials, i["apinvoicesupplier_id"])
                        bgtresponser.set_apexpense_id(i["apexpense_id"])
                        bgtresponser.set_apsubcat_id(i["apsubcat_id"])
                        pro_list.data.append(bgtresponser)
                return pro_list

    def compare_future_bgt_supplier(self, future_bgt, ppr_bgt, bgt_obj,pagequery):
        # try:
        logger.info('compare future supplier start')

        future_bgt = json.loads(future_bgt)
        ppr_bgt = json.loads(ppr_bgt)
        keys = Pprutility_keys()
        yearterm = bgt_obj.get_yearterm()
        condition = ""
        valu_mQ = ""
        if yearterm == "Monthly":
            condition = keys.transactionmonth
            valu_mQ = "0"
        if yearterm == "Quarterly":
            condition = keys.quarter
            valu_mQ = 0
        if len(ppr_bgt) <= 0:
            ppr_bgt = [{
                condition: valu_mQ,
                "supplier_branchname": "",
                "supplier_code": "",
                "supplier_gstno": "",
                "supplier_id": 0,
                "supplier_name": "",
                "supplier_panno": "",
                "totamount": "",
                "bgtamount": "",
                "apexpense_id": 0,
                "apsubcat_id": 0
            }]
        if len(future_bgt["data"]) <= 0:
            future_bgt["data"] = [{
                "apexpense_id": 0,
                "apsubcat_id": 0,
                "future_bgtamount": "",
                "supplier_branchname": "",
                "supplier_code": "",
                "supplier_gstno": "",
                "supplier_id": 0,
                "supplier_name": "",
                "supplier_panno": "",
                "status":0,
                "remark_key":"",
                condition: valu_mQ
            }]
        ppr_bgtDF = pd.DataFrame(ppr_bgt)
        future_bgtDF = pd.DataFrame(future_bgt["data"])

        merge_data = pd.merge(future_bgtDF, ppr_bgtDF, how="outer",
                              left_on=["apexpense_id", "apsubcat_id", "supplier_branchname", "supplier_code",
                                       "supplier_gstno", "supplier_id", "supplier_name", "supplier_panno",
                                       condition],
                              right_on=["apexpense_id", "apsubcat_id", "supplier_branchname", "supplier_code",
                                        "supplier_gstno", "supplier_id", "supplier_name", "supplier_panno",
                                        condition])
        final_merge = merge_data[
            ["supplier_branchname", "supplier_code", "supplier_gstno", "supplier_id", "supplier_name",
             "supplier_panno", condition, "totamount", "bgtamount", "future_bgtamount", "apexpense_id",
             "apsubcat_id","status","remark_key"]].fillna(0)
        logger.info('compare future supplier end')

        if pagequery !=None and pagequery != "":
            if pagequery == "APPROVER":
                return final_merge[final_merge['status'] == 3.0].to_json(orient="records")
            elif pagequery == "VIEWER":
                return final_merge[final_merge['status'] == 4.0].to_json(orient="records")
            elif pagequery == "CHECKER":
                return final_merge[final_merge['status'] == 2.0].to_json(orient="records")
        if bgt_obj.get_status_id() != None and bgt_obj.get_status_id() != "":
            return final_merge[final_merge['status'] == int(bgt_obj.get_status_id())].to_json(orient="records")

        return final_merge.to_json(orient="records")
        # except:
        #     return json.dumps([])


    def audit_function(self,data,ref_type,emp_id,action):
        audit_service = PPRAuditService(self._scope())
        audit_res = PprAuditResponse()
        audit_res.set_data(data)
        audit_res.set_reftype(ref_type)
        audit_res.set_userid(emp_id)
        audit_res.set_action(action)
        audit_service.create_audit(audit_res)


    def Builder_employeebranch(self,emp_id,query, vys_page):
        condition = Q()
        employee_branch_id_map = EmployeeBusinessSegmentMapping.objects.filter(Q(emp_id=emp_id)&Q(status=1)&Q(entity_id=self._entity_id()))
        branchid = []
        for i in employee_branch_id_map:
            branchid.append(i.branch_id)
        month = int(datetime.datetime.now().strftime("%m"))
        # month = 4
        year = int(datetime.datetime.now().strftime("%y"))
        # year = 2022
        if month >= 1 and month <= 3:
            finyear_ = f"{year - 1}{year}"
        elif month >= 4 and month <= 12:
            finyear_ = f"{year}{year + 1}"
        branch_code_check = EmployeeBranch.objects.get(status=1,code=1676)
        check_emp_all_access = EmployeeBusinessSegmentMapping.objects.filter(
            emp_id=emp_id, finyear=finyear_, branch_id=branch_code_check.id).exists()
        if check_emp_all_access == True:
            condition = Q(status=1)
        else:
            condition = Q(status=1,id__in=branchid)#control_office_branch=branch_do_code.control_office_branch#
        if query != None:
            condition &= Q(code__icontains=query) | Q(name__icontains=query)
        branch = EmployeeBranch.objects.filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
        pro_list = NWisefinList()
        if len(branch) <= 0:
            pass
        else:
            for i in branch:
                response = EmployeeBranchresponse()
                response.set_id(i.id)
                response.set_code(i.code)
                response.set_name(i.name)
                pro_list.data.append(response)
            vpage = NWisefinPaginator(branch, vys_page.get_index(), 10)
            pro_list.set_pagination(vpage)
        return pro_list

    def get_budget_status_dropdown(self, query):
        status = [1,2,3,4,6]
        pro_list = NWisefinList()
        if query is None:
            for i in status:
                response = BudgetBuilderresponse()
                response.set_budget_status(i)
                pro_list.data.append(response)
        else:
            for i in status:
                if i == int(query):
                    response = BudgetBuilderresponse()
                    response.set_budget_status(i)
                    pro_list.data.append(response)
        return pro_list

    def fetch_finyear_list(self, query, vys_page):
        if query is None:
            finyear_obj = Pprdata.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).all().values('finyear').distinct()[
                          vys_page.get_offset():vys_page.get_query_limit()]
        else:
            finyear_obj = Pprdata.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).all().values('finyear').distinct(). \
                              filter(finyear__icontains=query)[vys_page.get_offset():vys_page.get_query_limit()]
        pro_list = NWisefinList()
        list_length = len(finyear_obj)
        if list_length <= 0:
            pass
        else:
            for i in finyear_obj:
                fromyr = int(i['finyear'].split("-")[0][2:4]) + 1
                toyr = int(i['finyear'].split("-")[1][:2]) + 1
                finyr = 'FY' + str(fromyr) + '-' + str(toyr)
                response = BudgetBuilderresponse()
                response.set_finyear(finyr)
                pro_list.data.append(response)
        vpage = NWisefinPaginator(finyear_obj, vys_page.get_index(), 10)
        pro_list.set_pagination(vpage)
        return pro_list

    def fetch_budget_remarks(self,remark_obj):
        remark_obj_ = PPR_history.objects.using(self._current_app_schema()).filter(remark_key=remark_obj.get_remark_key(),entity_id=self._entity_id()).values('module','user_id',
                                                                                                              'remark','remark_key','created_date__date').annotate(Count('created_date'))
        pro_list = NWisefinList()
        utility = USER_SERVICE(self._scope())
        if len(remark_obj_) <= 0:
            pass
        else:
            empid = []
            for i in remark_obj_:
                empid.append(i['user_id'])
            emp_detial = utility.get_employee_data(empid)
            for i in remark_obj_:
                response = BudgetRemarkResponse()
                response.set_module(i['module'])
                response.set_remark(i['remark'])
                createdDate = i['created_date__date']
                response.set_created_date(createdDate.strftime("%Y-%m-%d"))
                response.set_remark_key(i['remark_key'])
                response.set_user_data(emp_detial,i['user_id'])
                response.set_status(i['module'])
                pro_list.data.append(response)
        return pro_list

    def compare_ppr_bgt_expense(self, pprdata, bgtdata, bgt_obj):
        # try:
        # test
        logger.info('compare expensegrp start')
        pprdata = json.loads(pprdata)
        bgtdata = json.loads(bgtdata)
        keys = Pprutility_keys()
        yearterm = bgt_obj.get_year_term()
        condition = ""
        valu_mQ = ""
        if yearterm == "Monthly":
            condition = keys.transactionmonth
            valu_mQ = "0"
        if yearterm == "Quarterly":
            condition = keys.quarter
            valu_mQ = 0
        if len(pprdata["data"]) <= 0:
            pprdata["data"] = [{
                condition: valu_mQ,
                "amount": "",
                "expense_id": 0,
                "expensegrpname": "",
                "expensename": "",
            }]
        if len(bgtdata["data"]) <= 0:
            bgtdata["data"] = [{
                condition: valu_mQ,
                "expense_id": 0,
                "bgtamount": "",
                "expensegrpname": "",
                "expensename": "",
            }]
        ppr_df = pd.DataFrame(pprdata["data"])
        bgt_df = pd.DataFrame(bgtdata["data"])
        merge_data = pd.merge(ppr_df, bgt_df, how="left",
                              left_on=[condition, "expense_id", "expensegrpname", "expensename"],
                              right_on=[condition, "expense_id", "expensegrpname", "expensename"])
        final_merge = merge_data[
            [condition, "expense_id", "expensegrpname", "expensename", "bgtamount",
             "amount"]].fillna(0)
        logger.info('compare expensegrp end')
        return final_merge.to_json(orient="records")

    def compare_future_bgt_expense(self, future_bgt, ppr_bgt, bgt_obj, pagequery):
        # try:
        logger.info('compare future expensegrp start')
        future_bgt = json.loads(future_bgt)
        ppr_bgt = json.loads(ppr_bgt)
        keys = Pprutility_keys()
        yearterm = bgt_obj.get_year_term()
        condition = ""
        valu_mQ = ""
        if yearterm == "Monthly":
            condition = keys.transactionmonth
            valu_mQ = "0"
        if yearterm == "Quarterly":
            condition = keys.quarter
            valu_mQ = 0
        if len(ppr_bgt) <= 0:
            ppr_bgt = [{
                condition: valu_mQ,
                "expense_id": 0,
                "expensegrpname": "",
                "expensename": "",
                "bgtamount": "",
                "amount": ""
            }]
        if len(future_bgt["data"]) <= 0:
            future_bgt["data"] = [{
                "expense_id": 0,
                "expensegrpname": "",
                "expensename": "",
                "future_bgtamount": "",
                "status": 0,
                "remark_key": "",
                condition: valu_mQ
            }]
        ppr_bgtDF = pd.DataFrame(ppr_bgt)
        future_bgtDF = pd.DataFrame(future_bgt["data"])
        merge_data = pd.merge(future_bgtDF, ppr_bgtDF, how="outer",
                              left_on=["expensegrpname", "expensename",
                                       condition, "expense_id"],
                              right_on=["expensegrpname", "expensename",
                                        condition, "expense_id"])
        final_merge = merge_data[
            ["expense_id", "expensegrpname", "expensename", "bgtamount", "amount", "future_bgtamount", "status",
             "remark_key", condition]].fillna(0)
        logger.info('compare future expensegrp end')
        if pagequery != None and pagequery != "":
            if pagequery == "APPROVER":
                return final_merge[final_merge['status'] == 3.0].to_json(orient="records")
            elif pagequery == "VIEWER":
                return final_merge[final_merge['status'] == 4.0].to_json(orient="records")
            elif pagequery == "CHECKER":
                return final_merge[final_merge['status'] == 2.0].to_json(orient="records")
        if bgt_obj.get_status_id() != None and bgt_obj.get_status_id() != "":
            return final_merge[final_merge['status'] == int(bgt_obj.get_status_id())].to_json(orient="records")

        return final_merge.to_json(orient="records")

    def new_budget_expensegrp_list(self, bgt_obj):
        bgtdata = []
        pro_list = NWisefinList()
        utilitys = MASTER_SERVICE(self._scope())
        condition = Q(status=1,entity_id=self._entity_id())
        expensegrp_id = APexpensegroup.objects.using(self._current_app_schema()).filter(condition)
        for exgrp_id in expensegrp_id:
            expense_id = utilitys.get_new_expgrp_exp([exgrp_id.id])
            if len(expense_id) == 0:
                if bgt_obj.get_year_term() == 'Monthly':
                    tranmon1 = 4
                    for f in range(0, 12):
                        tranmon = tranmon1
                        if tranmon1 == 13:
                            tranmon = 1
                        if tranmon1 == 14:
                            tranmon = 2
                        if tranmon1 == 15:
                            tranmon = 3
                        pprresponser = pprresponse()
                        pprresponser.expensegrp_id = exgrp_id.id
                        pprresponser.expensegrpname = exgrp_id.name
                        pprresponser.set_transactionmonth(int(tranmon))
                        pprresponser.set_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                        pro_list.data.append(pprresponser)
                        tranmon1 = tranmon1 + 1
                if bgt_obj.get_year_term() == 'Quarterly':
                    tranmon1 = 1
                    for f in range(0, 4):
                        tranmon = tranmon1
                        pprresponser = pprresponse()
                        pprresponser.expensegrp_id = exgrp_id.id
                        pprresponser.expensegrpname = exgrp_id.name
                        pprresponser.set_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                        pprresponser.set_quarter(int(tranmon))
                        pro_list.data.append(pprresponser)
                        tranmon1 = tranmon1 + 1
            else:
                for expense in expense_id:
                    condition = Q(status=2,entity_id=self._entity_id())
                    if bgt_obj.get_finyear() != None and bgt_obj.get_finyear() != "":
                        condition &= Q(finyear=bgt_obj.get_finyear())
                    if bgt_obj.get_branch_id() != None and bgt_obj.get_branch_id() != "":
                        condition &= Q(apinvoicebranch_id=bgt_obj.get_branch_id())
                    if bgt_obj.get_sector_name() != None and bgt_obj.get_sector_name() != "":
                        condition &= Q(sectorname=bgt_obj.get_sector_name())
                    if bgt_obj.get_mstbusiness_segment_name() != None and bgt_obj.get_mstbusiness_segment_name() != "":
                        condition &= Q(bizname=bgt_obj.get_mstbusiness_segment_name())
                    if bgt_obj.get_bs_name() != None and bgt_obj.get_bs_name() != "":
                        condition &= Q(bsname=bgt_obj.get_bs_name())
                    if bgt_obj.get_cc_name() != None and bgt_obj.get_cc_name() != "":
                        condition &= Q(ccname=bgt_obj.get_cc_name())
                    condition &= Q(apexpense_id=expense)
                    if bgt_obj.get_year_term() == 'Monthly':
                        bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id',
                                                                                                       'transactionmonth').annotate(
                            amount=Sum('amount'))
                    if bgt_obj.get_year_term() == 'Quarterly':
                        bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id',
                                                                                                       'quarter').annotate(
                            amount=Sum('amount'))
                    if len(bgtdata) <= 0:
                        if bgt_obj.get_year_term() == 'Monthly':
                            tranmon1 = 4
                            for f in range(0, 12):
                                tranmon = tranmon1
                                if tranmon1 == 13:
                                    tranmon = 1
                                if tranmon1 == 14:
                                    tranmon = 2
                                if tranmon1 == 15:
                                    tranmon = 3
                                pprresponser = pprresponse()
                                pprresponser.expensegrp_id = exgrp_id.id
                                pprresponser.expensegrpname = exgrp_id.name
                                pprresponser.set_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                                if bgt_obj.get_year_term() == 'Monthly':
                                    pprresponser.set_transactionmonth(int(tranmon))
                                pro_list.data.append(pprresponser)
                                tranmon1 = tranmon1 + 1
                        if bgt_obj.get_year_term() == 'Quarterly':
                            tranmon1 = 1
                            for f in range(0, 4):
                                tranmon = tranmon1
                                pprresponser = pprresponse()
                                pprresponser.expensegrp_id = exgrp_id.id
                                pprresponser.expensegrpname = exgrp_id.name
                                pprresponser.set_quarter(int(tranmon))
                                pprresponser.set_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                                pro_list.data.append(pprresponser)
                                tranmon1 = tranmon1 + 1
                    else:
                        for i in bgtdata:
                            bgtresponser = BudgetBuilderresponse()
                            bgtresponser.expensegrp_id = exgrp_id.id
                            bgtresponser.expensegrpname = exgrp_id.name
                            bgtresponser.set_bgtamount(str(Decimal(i['amount']) / bgt_obj.get_divAmount()))
                            if bgt_obj.get_year_term() == 'Monthly':
                                bgtresponser.set_transactionmonth(i["transactionmonth"])
                            if bgt_obj.get_year_term() == 'Quarterly':
                                bgtresponser.set_quarter(i["quarter"])
                            pro_list.data.append(bgtresponser)
        return pro_list

    def compare_ppr_bgt_new_expensegrp(self, pprdata, bgtdata, bgt_obj):
        # try:
        # test
        logger.info('compare expensegrp start')
        pprdata = json.loads(pprdata)
        bgtdata = json.loads(bgtdata)
        keys = Pprutility_keys()
        yearterm = bgt_obj.get_year_term()
        condition = ""
        valu_mQ = ""
        if yearterm == "Monthly":
            condition = keys.transactionmonth
            valu_mQ = "0"
        if yearterm == "Quarterly":
            condition = keys.quarter
            valu_mQ = 0
        if len(pprdata["data"]) <= 0:
            pprdata["data"] = [{
                condition: valu_mQ,
                "amount": "",
                "expensegrp_id": 0,
                "expensegrpname": "",
            }]
        if len(bgtdata["data"]) <= 0:
            bgtdata["data"] = [{
                condition: valu_mQ,
                "amount": "",
                "expensegrp_id": 0,
                "expensegrpname": "",
            }]
        ppr_df = pd.DataFrame(pprdata["data"])
        bgt_df = pd.DataFrame(bgtdata["data"])
        merge_data = pd.merge(ppr_df, bgt_df, how="left",
                              left_on=[condition, "expensegrp_id", "expensegrpname"],
                              right_on=[condition, "expensegrp_id", "expensegrpname"])
        final_merge = merge_data[
            [condition, "expensegrp_id", "expensegrpname", "bgtamount",
             "amount"]].fillna(0)
        logger.info('compare expensegrp end')
        return final_merge.to_json(orient="records")
        # except:
        #     return json.dumps([])

    def compare_future_bgt_new_expensegrp(self, future_bgt, ppr_bgt, bgt_obj, pagequery):
        # try:
        logger.info('compare future expensegrp start')
        future_bgt = json.loads(future_bgt)
        ppr_bgt = json.loads(ppr_bgt)
        keys = Pprutility_keys()
        yearterm = bgt_obj.get_year_term()
        condition = ""
        valu_mQ = ""
        if yearterm == "Monthly":
            condition = keys.transactionmonth
            valu_mQ = "0"
        if yearterm == "Quarterly":
            condition = keys.quarter
            valu_mQ = 0
        if len(ppr_bgt) <= 0:
            ppr_bgt = [{
                condition: valu_mQ,
                "expensegrp_id": 0,
                "expensegrpname": "",
                "bgtamount": "",
                "amount": ""
            }]
        if len(future_bgt["data"]) <= 0:
            future_bgt["data"] = [{
                "expensegrp_id": 0,
                "expensegrpname": "",
                "future_bgtamount": "",
                "status": 0,
                "remark_key": "",
                condition: valu_mQ
            }]
        ppr_bgtDF = pd.DataFrame(ppr_bgt)
        future_bgtDF = pd.DataFrame(future_bgt["data"])
        merge_data = pd.merge(future_bgtDF, ppr_bgtDF, how="outer",
                              left_on=["expensegrpname",
                                       condition, "expensegrp_id"],
                              right_on=["expensegrpname",
                                        condition, "expensegrp_id"])

        final_merge = merge_data[
            ["expensegrp_id", "expensegrpname", "bgtamount", "amount", "future_bgtamount", condition, "status",
             "remark_key"]].fillna(0)
        logger.info('compare future expensegrp end')
        if pagequery != None and pagequery != "":
            if pagequery == "APPROVER":
                return final_merge[final_merge['status'] == 3.0].to_json(orient="records")
            elif pagequery == "VIEWER":
                return final_merge[final_merge['status'] == 4.0].to_json(orient="records")
            elif pagequery == "CHECKER":
                return final_merge[final_merge['status'] == 2.0].to_json(orient="records")
        if bgt_obj.get_status_id() != None and bgt_obj.get_status_id() != "":
            return final_merge[final_merge['status'] == int(bgt_obj.get_status_id())].to_json(orient="records")
        return final_merge.to_json(orient="records")

    def expensegrp_logic(self, expensegrp_data, ppr_obj):
        expensegrp_data = json.loads(expensegrp_data)
        pprservice = Pprservice(self._scope())
        keys = Pprutility_keys()
        output = []
        expensegrp_datauniq = []
        for i in expensegrp_data:
            if i["expensegrp_id"] != 0 and i["expensegrpname"] != "":
                if 'transactionmonth' in i:
                    if i["transactionmonth"] != "0":
                        expensegrp_datauniq.append(i)
                if 'quarter' in i:
                    if i["quarter"] != 0:
                        expensegrp_datauniq.append(i)
        try:
            if len(expensegrp_datauniq) <= 0:
                pass
            else:
                year_term = ppr_obj.get_year_term()
                if year_term == "Monthly":
                    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                elif year_term == "Quarterly":
                    month = ["Quarterly_1", "Quarterly_2", "Quarterly_3", "Quarterly_4"]
                else:
                    return {"message": Pprdata_warning.month_quaterneed}
                uniqexpensegrpid = pprservice.remove_duplicate_arrdict(expensegrp_datauniq, '', keys.expensegrp_id,
                                                                       '')
                uniqexpensegrpname = pprservice.remove_duplicate_arrdict(expensegrp_datauniq, '', keys.expensegrpname,
                                                                         '')
                for expensegrp_id, name in zip(uniqexpensegrpid, uniqexpensegrpname):
                    row = {}
                    row[keys.expensegrp_id] = expensegrp_id
                    row[keys.name] = name
                    status = []
                    for imonth in month:
                        row[imonth] = [Decimal(round(Decimal('0.00'), 2)), Decimal(round(Decimal('0.00'), 2)),
                                       Decimal(round(Decimal('0.00'), 2))]
                    for uniq_month in expensegrp_datauniq:
                        if expensegrp_id == uniq_month[keys.expensegrp_id]:
                            if int(uniq_month[keys.expensegrp_id]) > 0:
                                if int(uniq_month[keys.status]) not in status:
                                    status.append(int(uniq_month[keys.status]))
                            row[keys.remark_key] = uniq_month[keys.remark_key]
                            if year_term == "Monthly":
                                if row[month[int(uniq_month[keys.transactionmonth]) - 1]][1] != Decimal(
                                        round(Decimal('0.00'), 2)):
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][1] = row[month[
                                        int(uniq_month[keys.transactionmonth]) - 1]][1] + Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][0] = row[month[
                                        int(uniq_month[keys.transactionmonth]) - 1]][0] + Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                    if row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] != Decimal(
                                            round(Decimal('0.00'), 2)):
                                        row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] = row[month[
                                            int(uniq_month[keys.transactionmonth]) - 1]][2] + Decimal(
                                            round(Decimal(uniq_month["future_bgtamount"]), 2))
                                    else:
                                        row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] = Decimal(
                                            round(Decimal(uniq_month["future_bgtamount"]), 2))
                                else:
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][1] = Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][0] = Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                    if row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] != Decimal(
                                            round(Decimal('0.00'), 2)):
                                        row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] = row[month[
                                            int(uniq_month[keys.transactionmonth]) - 1]][2] + Decimal(
                                            round(Decimal(uniq_month["future_bgtamount"]), 2))
                                    else:
                                        row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] = Decimal(
                                            round(Decimal(uniq_month["future_bgtamount"]), 2))
                            if year_term == "Quarterly":
                                if row[f"Quarterly_{uniq_month[keys.quarter]}"][1] != Decimal(
                                        round(Decimal('0.00'), 2)) and f"Quarterly_{uniq_month[keys.quarter]}" in month:
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][1] = row[
                                                                                          f"Quarterly_{uniq_month[keys.quarter]}"][
                                                                                          1] + Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][0] = row[
                                                                                          f"Quarterly_{uniq_month[keys.quarter]}"][
                                                                                          0] + Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                else:
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][1] = Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][0] = Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][2] = Decimal(
                                        round(Decimal(uniq_month["future_bgtamount"]), 2))
                    ytd = [Decimal(round(Decimal('0.00'), 2)), Decimal(round(Decimal('0.00'), 2)), ""]
                    for i in [0, 1, 2]:
                        totalsum = Decimal(round(Decimal('0.00'), 2))
                        for sumof_month in month:
                            totalsum = totalsum + row[sumof_month][i]
                        if i == 2:
                            ytd[i] = Decimal(round(Decimal(totalsum), 2))
                        else:
                            ytd[i] = totalsum
                    status.sort(reverse=True)
                    row[keys.status] = status[0]
                    row[keys.YTD] = ytd
                    row['tree_flag'] = 'Y'
                    row[keys.Padding_left] = '10px'
                    row[keys.Padding] = '5px'
                    output.append(row)
                output.append(self.columndata_sum(month, output, '10px'))
            return {"data": output}  # "pagination":expensegrp_data['pagination']
        except:
            return {"data": output}

    def future_budget_new_expense_list(self, bgt_obj, pagequery):  # vys_page
        pprutility = MASTER_SERVICE(self._scope())
        bgtdata = []
        pro_list = NWisefinList()
        if bgt_obj.get_expense_grp_id() != None and bgt_obj.get_expense_grp_id() != "":
            expense_dtls_list=pprutility.get_expense_expensegrp_id(bgt_obj.get_expense_grp_id())

            for expid in expense_dtls_list:
                condition = Q(apexpense_id=expid.id,entity_id=self._entity_id())
                if bgt_obj.get_status_id() != None and bgt_obj.get_status_id() != "":
                    condition &= Q(status=bgt_obj.get_status_id())
                if pagequery != None and pagequery != "":
                    if pagequery == "APPROVER":
                        condition = Q(status=3,entity_id=self._entity_id())
                        condition &= Q(apexpense_id=expid.id)
                    elif pagequery == "CHECKER":
                        condition = Q(status=2,entity_id=self._entity_id())
                        condition &= Q(apexpense_id=expid.id)
                    elif pagequery == "VIEWER":
                        condition = Q(status=4,entity_id=self._entity_id())
                        condition &= Q(apexpense_id=expid.id)
                if bgt_obj.get_branch_id() != None and bgt_obj.get_branch_id() != "":
                    condition &= Q(apinvoicebranch_id=bgt_obj.get_branch_id())
                if bgt_obj.get_finyear() != None and bgt_obj.get_finyear() != "":
                    condition &= Q(
                        finyear=f'FY{int(bgt_obj.get_finyear().split("-")[0][-2:]) + 1}-{int(bgt_obj.get_finyear().split("-")[1]) + 1}')
                if bgt_obj.get_sector_name() != None and bgt_obj.get_sector_name() != "":
                    condition &= Q(sectorname=bgt_obj.get_sector_name())
                if bgt_obj.get_mstbusiness_segment_name() != None and bgt_obj.get_mstbusiness_segment_name() != "":
                    condition &= Q(bizname=bgt_obj.get_mstbusiness_segment_name())
                if bgt_obj.get_bs_name() != None and bgt_obj.get_bs_name() != "":
                    condition &= Q(bsname=bgt_obj.get_bs_name())
                if bgt_obj.get_cc_name() != None and bgt_obj.get_cc_name() != "":
                    condition &= Q(ccname=bgt_obj.get_cc_name())

                if bgt_obj.get_year_term() == 'Monthly':
                    bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id',
                                                                                                   'transactionmonth',
                                                                                                   'status',
                                                                                                   'remark_key').annotate(
                        fut_bgt_amount=Sum('amount'))
                    # [vys_page.get_offset():vys_page.get_query_limit()]
                if bgt_obj.get_year_term() == 'Quarterly':
                    bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id',
                                                                                                   'quarter', 'status',
                                                                                                   'remark_key').annotate(
                        fut_bgt_amount=Sum('amount'))
                    # [vys_page.get_offset():vys_page.get_query_limit()]
                if len(bgtdata) <= 0:
                    if bgt_obj.get_year_term() == 'Monthly':
                        tranmon1 = 4
                        for f in range(0, 12):
                            tranmon = tranmon1
                            if tranmon1 == 13:
                                tranmon = 1
                            if tranmon1 == 14:
                                tranmon = 2
                            if tranmon1 == 15:
                                tranmon = 3
                            pprresponser = pprresponse()
                            pprresponser.expense_id = expid.id
                            pprresponser.expensename = expid.head
                            pprresponser.expensegrpname = expid.group
                            pprresponser.expensegrp_id = expid.exp_grp_id
                            pprresponser.set_future_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                            pprresponser.set_status(str(Decimal(0.0)))
                            pprresponser.set_remark_key("")
                            pprresponser.set_transactionmonth(str(tranmon))
                            pro_list.data.append(pprresponser)
                            tranmon1 = tranmon1 + 1
                    if bgt_obj.get_year_term() == 'Quarterly':
                        tranmon1 = 1
                        for f in range(0, 4):
                            tranmon = tranmon1
                            pprresponser = pprresponse()
                            pprresponser.expense_id = expid.id
                            pprresponser.expensename = expid.head
                            pprresponser.expensegrpname = expid.group
                            pprresponser.expensegrp_id = expid.exp_grp_id
                            pprresponser.set_quarter(tranmon)
                            pprresponser.set_status(str(Decimal(0.0)))
                            pprresponser.set_remark_key("")
                            pprresponser.set_future_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                            pro_list.data.append(pprresponser)
                            tranmon1 = tranmon1 + 1
                else:
                    bgtexpense_ids = []
                    if len(bgtdata) > 0:
                        for i in bgtdata:
                            bgtexpense_ids.append(i["apexpense_id"])
                    bgtexpense_detials = pprutility.get_expense((bgtexpense_ids))
                    for i in bgtdata:
                        bgtresponser = BudgetBuilderresponse()
                        bgtresponser.set_expense_detial_future(bgtexpense_detials, i["apexpense_id"])
                        bgtresponser.set_future_bgtamount(str(Decimal(i["fut_bgt_amount"]) / bgt_obj.get_divAmount()))
                        bgtresponser.set_status(i['status'])
                        bgtresponser.set_remark_key(i['remark_key'])
                        if bgt_obj.get_year_term() == 'Monthly':
                            bgtresponser.set_transactionmonth(i["transactionmonth"])
                        if bgt_obj.get_year_term() == 'Quarterly':
                            bgtresponser.set_quarter(i["quarter"])
                        pro_list.data.append(bgtresponser)
                # vpage = PPRNWisefinPaginator(pprdata, vys_page.get_index(), 5)
                # pro_list.set_pagination(vpage)
            return pro_list


    def budget_new_expense_list(self, bgt_obj):  # vys_page
        utilitys = MASTER_SERVICE(self._scope())
        bgtdata = []
        pro_list = NWisefinList()
        condition = Q(status=4)
        if bgt_obj.get_expense_grp_id() != None and bgt_obj.get_expense_grp_id() != "":
            expense_id_dtls=utilitys.get_expense_expensegrp_id(bgt_obj.get_expense_grp_id())
            for exp_id in expense_id_dtls:

                        if bgt_obj.get_branch_id() != None and bgt_obj.get_branch_id() != "":
                            condition &= Q(apinvoicebranch_id=bgt_obj.get_branch_id())
                        if bgt_obj.get_finyear() != None and bgt_obj.get_finyear() != "":
                            condition &= Q(finyear=bgt_obj.get_finyear())
                        if bgt_obj.get_sector_name() != None and bgt_obj.get_sector_name() != "":
                            condition &= Q(sectorname=bgt_obj.get_sector_name())
                        if bgt_obj.get_mstbusiness_segment_name() != None and bgt_obj.get_mstbusiness_segment_name() != "":
                            condition &= Q(bizname=bgt_obj.get_mstbusiness_segment_name())
                        if bgt_obj.get_bs_name() != None and bgt_obj.get_bs_name() != "":
                            condition &= Q(bsname=bgt_obj.get_bs_name())
                        if bgt_obj.get_cc_name() != None and bgt_obj.get_cc_name() != "":
                            condition &= Q(ccname=bgt_obj.get_cc_name())
                        condition &= Q(apexpense_id=exp_id.id)
                        if bgt_obj.get_year_term() == 'Monthly':
                            bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id', 'transactionmonth').annotate(
                                amount=Sum('amount'))
                            # [vys_page.get_offset():vys_page.get_query_limit()]
                        if bgt_obj.get_year_term() == 'Quarterly':
                            bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id', 'quarter').annotate(
                                amount=Sum('amount'))
                            # [vys_page.get_offset():vys_page.get_query_limit()]
                        if len(bgtdata) <= 0:
                            if bgt_obj.get_year_term() == 'Monthly':
                                tranmon1 = 4
                                for f in range(0, 12):
                                    tranmon = tranmon1
                                    if tranmon1 == 13:
                                        tranmon = 1
                                    if tranmon1 == 14:
                                        tranmon = 2
                                    if tranmon1 == 15:
                                        tranmon = 3
                                    pprresponser = pprresponse()
                                    pprresponser.expense_id = exp_id.id
                                    pprresponser.expensename = exp_id.head
                                    pprresponser.expensegrpname = exp_id.group
                                    pprresponser.expensegrp_id = exp_id.exp_grp_id
                                    pprresponser.set_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                                    pprresponser.set_transactionmonth(str(tranmon))
                                    pro_list.data.append(pprresponser)
                                    tranmon1 = tranmon1 + 1
                            if bgt_obj.get_year_term() == 'Quarterly':
                                tranmon1 = 1
                                for f in range(0, 4):
                                    tranmon = tranmon1
                                    pprresponser = pprresponse()
                                    pprresponser.expense_id = exp_id.id
                                    pprresponser.expensename = exp_id.head
                                    pprresponser.expensegrpname = exp_id.group
                                    pprresponser.expensegrp_id = exp_id.exp_grp_id
                                    pprresponser.set_quarter(tranmon)
                                    pprresponser.set_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                                    pro_list.data.append(pprresponser)
                                    tranmon1 = tranmon1 + 1
                        else:
                            bgtexpense_ids = []
                            if len(bgtdata) > 0:
                                for i in bgtdata:
                                    bgtexpense_ids.append(i["apexpense_id"])
                            bgtexpense_detials = utilitys.get_expense((bgtexpense_ids))
                            for i in bgtdata:
                                bgtresponser = BudgetBuilderresponse()
                                bgtresponser.set_expense_detial(bgtexpense_detials, i["apexpense_id"])
                                bgtresponser.set_bgtamount(str(Decimal(i['amount']) / bgt_obj.get_divAmount()))
                                if bgt_obj.get_year_term() == 'Monthly':
                                    bgtresponser.set_transactionmonth(i["transactionmonth"])
                                if bgt_obj.get_year_term() == 'Quarterly':
                                    bgtresponser.set_quarter(i["quarter"])
                                pro_list.data.append(bgtresponser)
                        # vpage = PPRNWisefinPaginator(pprdata, vys_page.get_index(), 5)
                        # pro_list.set_pagination(vpage)
            return pro_list


    def compare_ppr_bgt_new_expense(self, pprdata, bgtdata, bgt_obj):
        # try:
        # test
        logger.info('compare expensegrp start')
        pprdata = json.loads(pprdata)
        bgtdata = json.loads(bgtdata)
        keys = Pprutility_keys()
        yearterm = bgt_obj.get_year_term()
        condition = ""
        valu_mQ = ""
        if yearterm == "Monthly":
            condition = keys.transactionmonth
            valu_mQ = "0"
        if yearterm == "Quarterly":
            condition = keys.quarter
            valu_mQ = 0
        if len(pprdata["data"]) <= 0:
            pprdata["data"] = [{
                condition: valu_mQ,
                "amount": "",
                "expense_id": 0,
                "expensename": "",
            }]
        if len(bgtdata["data"]) <= 0:
            bgtdata["data"] = [{
                condition: valu_mQ,
                "expense_id": 0,
                "bgtamount": "",
                "expensename": "",
            }]
        ppr_df = pd.DataFrame(pprdata["data"])
        bgt_df = pd.DataFrame(bgtdata["data"])
        merge_data = pd.merge(ppr_df, bgt_df, how="left",
                              left_on=[condition, "expense_id", "expensename"],
                              right_on=[condition, "expense_id", "expensename"])
        final_merge = merge_data[
            [condition, "expense_id", "expensename", "bgtamount",
             "amount"]].fillna(0)
        logger.info('compare expensegrp end')
        return final_merge.to_json(orient="records")


    def compare_future_bgt_new_expense(self, future_bgt, ppr_bgt, bgt_obj, pagequery):
        logger.info('compare future expensegrp start')
        future_bgt = json.loads(future_bgt)
        ppr_bgt = json.loads(ppr_bgt)
        keys = Pprutility_keys()
        yearterm = bgt_obj.get_year_term()
        condition = ""
        valu_mQ = ""
        if yearterm == "Monthly":
            condition = keys.transactionmonth
            valu_mQ = "0"
        if yearterm == "Quarterly":
            condition = keys.quarter
            valu_mQ = 0
        if len(ppr_bgt) <= 0:
            ppr_bgt = [{
                condition: valu_mQ,
                "expense_id": 0,
                "expensename": "",
                "bgtamount": "",
                "amount": ""
            }]
        if len(future_bgt["data"]) <= 0:
            future_bgt["data"] = [{
                "expense_id": 0,
                "expensename": "",
                "future_bgtamount": "",
                "status": 0,
                "remark_key": "",
                condition: valu_mQ
            }]
        ppr_bgtDF = pd.DataFrame(ppr_bgt)
        future_bgtDF = pd.DataFrame(future_bgt["data"])
        merge_data = pd.merge(future_bgtDF, ppr_bgtDF, how="outer",
                              left_on=[ "expensename",
                                       condition, "expense_id"],
                              right_on=[ "expensename",
                                        condition, "expense_id"])
        final_merge = merge_data[
            ["expense_id", "expensename", "bgtamount", "amount", "future_bgtamount", "status",
             "remark_key", condition]].fillna(0)
        logger.info('compare future expensegrp end')
        if pagequery != None and pagequery != "":
            if pagequery == "APPROVER":
                return final_merge[final_merge['status'] == 3.0].to_json(orient="records")
            elif pagequery == "VIEWER":
                return final_merge[final_merge['status'] == 4.0].to_json(orient="records")
            elif pagequery == "CHECKER":
                return final_merge[final_merge['status'] == 2.0].to_json(orient="records")
        if bgt_obj.get_status_id() != None and bgt_obj.get_status_id() != "":
            return final_merge[final_merge['status'] == int(bgt_obj.get_status_id())].to_json(orient="records")

        return final_merge.to_json(orient="records")


    def expense_logic(self, expense_data, ppr_obj):
        expense_data = json.loads(expense_data)
        pprservice = Pprservice(self._scope())
        keys = Pprutility_keys()
        output = []
        expense_datauniq = []
        for i in expense_data:
            if i["expense_id"] != 0 and i["expensename"] != "":
                if 'transactionmonth' in i:
                    if i["transactionmonth"] != "0":
                        expense_datauniq.append(i)
                if 'quarter' in i:
                    if i["quarter"] != 0:
                        expense_datauniq.append(i)
        try:
            if len(expense_datauniq) <= 0:
                pass
            else:
                year_term = ppr_obj.get_year_term()
                if year_term == "Monthly":
                    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                elif year_term == "Quarterly":
                    month = ["Quarterly_1", "Quarterly_2", "Quarterly_3", "Quarterly_4"]
                else:
                    return {"message": Pprdata_warning.month_quaterneed}

                uniqexpenseid = pprservice.remove_duplicate_arrdict(expense_datauniq, '', keys.expense_id, '')
                uniqexpenselen = len(uniqexpenseid) - 1

                for index, expenseid in enumerate(uniqexpenseid):
                    row = {}
                    row[keys.expense_id] = expenseid
                    status = []
                    for imonth in month:
                        row[imonth] = [Decimal(round(Decimal('0.00'), 2)), Decimal(round(Decimal('0.00'), 2)),
                                       Decimal(round(Decimal('0.00'), 2))]
                    for uniq_month in expense_datauniq:
                        if expenseid == uniq_month[keys.expense_id]:
                            if int(uniq_month[keys.expense_id]) > 0:
                                if int(uniq_month[keys.status]) not in status:
                                    status.append(int(uniq_month[keys.status]))
                            row[keys.remark_key] = uniq_month[keys.remark_key]
                            if year_term == "Monthly":
                                if row[month[int(uniq_month[keys.transactionmonth]) - 1]][1] != Decimal(
                                        round(Decimal('0.00'), 2)):
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][1] = row[month[
                                        int(uniq_month[keys.transactionmonth]) - 1]][1] + Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][0] = row[month[
                                        int(uniq_month[keys.transactionmonth]) - 1]][0] + Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                else:
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][1] = Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][0] = Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                    if row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] != Decimal(
                                            round(Decimal('0.00'), 2)):
                                        row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] = row[month[
                                            int(uniq_month[keys.transactionmonth]) - 1]][2] + Decimal(
                                            round(Decimal(uniq_month["future_bgtamount"]), 2))
                                    else:
                                        row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] = Decimal(
                                            round(Decimal(uniq_month["future_bgtamount"]), 2))
                            if year_term == "Quarterly":
                                if row[f"Quarterly_{uniq_month[keys.quarter]}"][1] != Decimal(
                                        round(Decimal('0.00000'),
                                              5)) and f"Quarterly_{uniq_month[keys.quarter]}" in month:
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][1] = row[
                                                                                          f"Quarterly_{uniq_month[keys.quarter]}"][
                                                                                          1] + Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][0] = row[
                                                                                          f"Quarterly_{uniq_month[keys.quarter]}"][
                                                                                          0] + Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                else:
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][1] = Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][0] = Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][2] = Decimal(
                                        round(Decimal(uniq_month["future_bgtamount"]), 2))

                            row[keys.name] = uniq_month[keys.expensename]
                            if index == uniqexpenselen:
                                row['page'] = 'Y'
                    ytd = [Decimal(round(Decimal('0.00'), 2)), Decimal(round(Decimal('0.00'), 2)),
                           Decimal(round(Decimal('0.00'), 2))]
                    for i in [0, 1, 2]:
                        totalsum = Decimal(round(Decimal('0.00'), 2))
                        for sumof_month in month:
                            totalsum = totalsum + row[sumof_month][i]
                        if i == 2:
                            ytd[i] = Decimal(round(Decimal(totalsum), 2))
                        else:
                            ytd[i] = totalsum
                    status.sort(reverse=True)
                    row[keys.status] = status[0]
                    row[keys.YTD] = ytd
                    row['tree_flag'] = 'Y'
                    row[keys.Padding_left] = '50px'
                    row[keys.Padding] = '5px'
                    output.append(row)

            return {"data": output}  # "pagination": expense_data["pagination"]
        except:
            return {"data": output}

    def future_budget_cat_list(self, bgt_obj, pagequery):
        pprutility = MASTER_SERVICE(self._scope())
        bgtdata = []
        pro_list = NWisefinList()

        if bgt_obj.get_expense_id() != None and bgt_obj.get_expense_id() != "":
            cat_obj = Apcategory.objects.using(self._current_app_schema()).filter(expense_id=bgt_obj.get_expense_id(),entity_id=self._entity_id())
            for cat in cat_obj:
                cat_ids = []
                cat_ids.append(cat)
                subcat_dtls = pprutility.get_subcat_cat(cat_ids)

                if bgt_obj.get_status_id() != None and bgt_obj.get_status_id() != "":
                    condition = Q(status=bgt_obj.get_status_id(),entity_id=self._entity_id())
                else:
                    condition = Q(apsubcat_id__in=subcat_dtls)
                if pagequery != None and pagequery != "":
                    if pagequery == "APPROVER":
                        condition = Q(status=3,entity_id=self._entity_id())
                        condition &=Q(apsubcat_id__in=subcat_dtls)
                    elif pagequery == "CHECKER":
                        condition = Q(status=2,entity_id=self._entity_id())
                        condition &= Q(apsubcat_id__in=subcat_dtls)
                if bgt_obj.get_branch_id() != None and bgt_obj.get_branch_id() != "":
                    condition &= Q(apinvoicebranch_id=bgt_obj.get_branch_id())
                if bgt_obj.get_finyear() != None and bgt_obj.get_finyear() != "":
                    condition &= Q(
                        finyear=f'FY{int(bgt_obj.get_finyear().split("-")[0][-2:]) + 1}-{int(bgt_obj.get_finyear().split("-")[1]) + 1}')
                        # finyear=f'FY{int(bgt_obj.get_finyear().split("-")[0][-2:]) + 1}-{int(bgt_obj.get_finyear().split("-")[1]) + 1}')
                if bgt_obj.get_sector_name() != None and bgt_obj.get_sector_name() != "":
                    condition &= Q(sectorname=bgt_obj.get_sector_name())
                if bgt_obj.get_mstbusiness_segment_name() != None and bgt_obj.get_mstbusiness_segment_name() != "":
                    condition &= Q(bizname=bgt_obj.get_mstbusiness_segment_name())
                if bgt_obj.get_bs_name() != None and bgt_obj.get_bs_name() != "":
                    condition &= Q(bsname=bgt_obj.get_bs_name())
                if bgt_obj.get_cc_name() != None and bgt_obj.get_cc_name() != "":
                    condition &= Q(ccname=bgt_obj.get_cc_name())
                if bgt_obj.get_expense_id() != None and bgt_obj.get_expense_id() != "":
                    condition &= Q(apexpense_id=bgt_obj.get_expense_id())

                if bgt_obj.get_year_term() == 'Monthly':
                    bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apsubcat_id',
                                                                                                   'transactionmonth',
                                                                                                   'apexpense_id',
                                                                                                   'status',
                                                                                                   'remark_key').annotate(
                        fut_bgt_amount=Sum('amount'))
                    # [vys_page.get_offset():vys_page.get_query_limit()]
                if bgt_obj.get_year_term() == 'Quarterly':
                    bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apsubcat_id',
                                                                                                   'quarter',
                                                                                                   'apexpense_id',
                                                                                                   'status',
                                                                                                   'remark_key').annotate(
                        fut_bgt_amount=Sum('amount'))
                    # [vys_page.get_offset():vys_page.get_query_limit()]
                cat_ids = []
                cat_ids.append(cat.id)
                cat_detials = pprutility.get_category([cat.id])
                if len(bgtdata) <= 0:
                    if bgt_obj.get_year_term() == 'Monthly':
                        tranmon1 = 4
                        for f in range(0, 12):
                            tranmon = tranmon1
                            if tranmon1 == 13:
                                tranmon = 1
                            if tranmon1 == 14:
                                tranmon = 2
                            if tranmon1 == 15:
                                tranmon = 3
                            pprresponser = pprresponse()
                            pprresponser.set_future_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                            pprresponser.set_transactionmonth(int(tranmon))
                            pprresponser.set_new_cat(cat_detials, cat.id)
                            pprresponser.set_status(str(Decimal(0.0)))
                            pprresponser.set_remark_key("")
                            pro_list.data.append(pprresponser)
                            tranmon1 = tranmon1 + 1
                    if bgt_obj.get_year_term() == 'Quarterly':
                        tranmonth1 = 1
                        for f in range(0, 3):
                            tranmon = tranmonth1
                            pprresponser = pprresponse()
                            pprresponser.set_new_cat(cat_detials, cat.id)
                            pprresponser.set_future_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                            pprresponser.set_quarter(int(tranmon))
                            pprresponser.set_status(str(Decimal(0.0)))
                            pprresponser.set_remark_key("")
                            pro_list.data.append(pprresponser)
                            tranmonth1 = tranmonth1 + 1
                else:
                    subcat_ids = []
                    for i in bgtdata:
                        subcat_ids.append(i['apsubcat_id'])
                    subcat_detials = pprutility.get_subcat(subcat_ids)

                    for i in bgtdata:
                        bgtresponser = BudgetBuilderresponse()
                        bgtresponser.set_subcat_datials_future(subcat_detials, i["apsubcat_id"])
                        bgtresponser.set_future_bgtamount(str(Decimal(i["fut_bgt_amount"]) / bgt_obj.get_divAmount()))
                        bgtresponser.set_status(i['status'])
                        bgtresponser.set_remark_key(i['remark_key'])
                        if bgt_obj.get_year_term() == 'Monthly':
                            bgtresponser.set_transactionmonth(int(i["transactionmonth"]))
                        if bgt_obj.get_year_term() == 'Quarterly':
                            bgtresponser.set_quarter(int(i["quarter"]))
                        bgtresponser.set_expense_id(i['apexpense_id'])
                        pro_list.data.append(bgtresponser)
                # vpage = PPRNWisefinPaginator(pprdata, vys_page.get_index(), 5)
                # pro_list.set_pagination(vpage)
            return pro_list

    def budget_cat_list(self, bgt_obj):  # vys_page
        pprutility = MASTER_SERVICE(self._scope())
        bgtdata = []
        pro_list = NWisefinList()
        if bgt_obj.get_expense_id() != None and bgt_obj.get_expense_id() != "":
            cat_obj = Apcategory.objects.using(self._current_app_schema()).filter(expense_id=bgt_obj.get_expense_id(),entity_id=self._entity_id())
            for cat in cat_obj:
                cat_ids = []
                cat_ids.append(cat)
                subcat_dtls = pprutility.get_subcat_cat(cat_ids)
                condition = Q(apsubcat_id__in=subcat_dtls)
                if bgt_obj.get_branch_id() != None and bgt_obj.get_branch_id() != "":
                    condition &= Q(apinvoicebranch_id=bgt_obj.get_branch_id())
                if bgt_obj.get_finyear() != None and bgt_obj.get_finyear() != "":
                    condition &= Q(finyear=bgt_obj.get_finyear())
                if bgt_obj.get_sector_name() != None and bgt_obj.get_sector_name() != "":
                    condition &= Q(sectorname=bgt_obj.get_sector_name())
                if bgt_obj.get_mstbusiness_segment_name() != None and bgt_obj.get_mstbusiness_segment_name() != "":
                    condition &= Q(bizname=bgt_obj.get_mstbusiness_segment_name())
                if bgt_obj.get_bs_name() != None and bgt_obj.get_bs_name() != "":
                    condition &= Q(bsname=bgt_obj.get_bs_name())
                if bgt_obj.get_cc_name() != None and bgt_obj.get_cc_name() != "":
                    condition &= Q(ccname=bgt_obj.get_cc_name())
                if bgt_obj.get_expense_id() != None and bgt_obj.get_expense_id() != "":
                    condition &= Q(apexpense_id=bgt_obj.get_expense_id())

                if bgt_obj.get_year_term() == 'Monthly':
                    bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apsubcat_id',
                                                                                                   'transactionmonth',
                                                                                                   'apexpense_id').annotate(
                        amount=Sum('amount'))
                    # [vys_page.get_offset():vys_page.get_query_limit()]
                if bgt_obj.get_year_term() == 'Quarterly':
                    bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apsubcat_id',
                                                                                                   'quarter',
                                                                                                   'apexpense_id').annotate(
                        amount=Sum('amount'))
                    # [vys_page.get_offset():vys_page.get_query_limit()]
                cat_ids = []
                cat_ids.append(cat.id)
                cat_detials = pprutility.get_category([cat.id])
                if len(bgtdata) <= 0:
                    if bgt_obj.get_year_term() == 'Monthly':
                        tranmon1 = 4
                        for f in range(0, 12):
                            tranmon = tranmon1
                            if tranmon1 == 13:
                                tranmon = 1
                            if tranmon1 == 14:
                                tranmon = 2
                            if tranmon1 == 15:
                                tranmon = 3
                            pprresponser = pprresponse()
                            pprresponser.set_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                            pprresponser.set_transactionmonth(int(tranmon))
                            pprresponser.set_new_cat(cat_detials, cat.id)
                            pro_list.data.append(pprresponser)
                            tranmon1 = tranmon1 + 1
                    if bgt_obj.get_year_term() == 'Quarterly':
                        tranmonth1 = 1
                        for f in range(0, 3):
                            tranmon = tranmonth1
                            pprresponser = pprresponse()
                            pprresponser.set_new_cat(cat_detials, cat.id)
                            pprresponser.set_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                            pprresponser.set_quarter(int(tranmon))
                            pro_list.data.append(pprresponser)
                            tranmonth1 = tranmonth1 + 1
                else:
                    subcat_ids = []
                    for i in bgtdata:
                        subcat_ids.append(i['apsubcat_id'])

                    subcat_detials = pprutility.get_subcat(subcat_ids)
                    for i in bgtdata:
                        bgtresponser = BudgetBuilderresponse()
                        bgtresponser.set_subcat_datials_future(subcat_detials, i["apsubcat_id"])
                        bgtresponser.set_bgtamount(str(Decimal(i['amount']) / bgt_obj.get_divAmount()))
                        if bgt_obj.get_year_term() == 'Monthly':
                            bgtresponser.set_transactionmonth(int(i["transactionmonth"]))
                        if bgt_obj.get_year_term() == 'Quarterly':
                            bgtresponser.set_quarter(int(i["quarter"]))
                        bgtresponser.set_expense_id(i['apexpense_id'])
                        pro_list.data.append(bgtresponser)
                # vpage = PPRNWisefinPaginator(pprdata, vys_page.get_index(), 5)
                # pro_list.set_pagination(vpage)
            return pro_list

    def compare_ppr_bgt_cat(self, pprdata, bgtdata, bgt_obj):
        # try:
        logger.info('compare subcat start')

        pprdata = json.loads(pprdata)
        bgtdata = json.loads(bgtdata)
        keys = Pprutility_keys()
        yearterm = bgt_obj.get_year_term()
        condition = ""
        valu_mQ = ""
        if yearterm == "Monthly":
            condition = keys.transactionmonth
            valu_mQ = "0"
        if yearterm == "Quarterly":
            condition = keys.quarter
            valu_mQ = 0
        if len(pprdata["data"]) <= 0:
            pprdata["data"] = [{
                condition: valu_mQ,
                "amount": "",
                "cat_id": 0,
                "categoryname": "",
                "expense_id": 0,
            }]
        if len(bgtdata["data"]) <= 0:
            bgtdata["data"] = [{
                condition: valu_mQ,
                "cat_id": 0,
                "expense_id": 0,
                "bgtamount": "",
                "categoryname": "",
            }]
        ppr_df = pd.DataFrame(pprdata["data"])
        bgt_df = pd.DataFrame(bgtdata["data"])
        merge_data = pd.merge(ppr_df, bgt_df, how="left",
                              left_on=[condition, "cat_id", "categoryname", "expense_id"],
                              right_on=[condition, "cat_id", "categoryname", "expense_id"])
        final_merge = merge_data[
            [condition, "cat_id", "categoryname", "expense_id", "bgtamount",
             "amount"]].fillna(0)
        logger.info('compare subcat end ')

        return final_merge.to_json(orient="records")

    def compare_ppr_bgt_future_cat(self, future_bgt, ppr_bgt, bgt_obj, pagequery):
        # try:
        logger.info('compare future subcat start')

        future_bgt = json.loads(future_bgt)
        ppr_bgt = json.loads(ppr_bgt)
        keys = Pprutility_keys()
        yearterm = bgt_obj.get_year_term()
        condition = ""
        valu_mQ = ""
        if yearterm == "Monthly":
            condition = keys.transactionmonth
            valu_mQ = "0"
        if yearterm == "Quarterly":
            condition = keys.quarter
            valu_mQ = 0
        if len(ppr_bgt) <= 0:
            ppr_bgt = [{
                condition: valu_mQ,
                "cat_id": 0,
                "categoryname": "",
                "expense_id": 0,
                "bgtamount": "",
                "amount": ""
            }]
        if len(future_bgt["data"]) <= 0:
            future_bgt["data"] = [{
                "cat_id": 0,
                "categoryname": "",
                "expense_id": 0,
                "future_bgtamount": "",
                "status": 0,
                "remark_key": "",
                condition: valu_mQ
            }]
        ppr_bgtDF = pd.DataFrame(ppr_bgt)
        future_bgtDF = pd.DataFrame(future_bgt["data"])
        merge_data = pd.merge(future_bgtDF, ppr_bgtDF, how="outer",
                              left_on=["cat_id", "categoryname",
                                       condition, "expense_id"],
                              right_on=["cat_id", "categoryname",
                                        condition, "expense_id"])
        final_merge = merge_data[
            ["cat_id", "categoryname", condition, "expense_id", "future_bgtamount", "bgtamount", "amount", 'status',
             'remark_key']].fillna(0)
        logger.info('compare future subcat end')

        if pagequery != None and pagequery != "":
            if pagequery == "APPROVER":
                return final_merge[final_merge['status'] == 3.0].to_json(orient="records")
            elif pagequery == "VIEWER":
                return final_merge[final_merge['status'] == 4.0].to_json(orient="records")
            elif pagequery == "CHECKER":
                return final_merge[final_merge['status'] == 2.0].to_json(orient="records")
        if bgt_obj.get_status_id() != None and bgt_obj.get_status_id() != "":
            return final_merge[final_merge['status'] == int(bgt_obj.get_status_id())].to_json(orient="records")

        return final_merge.to_json(orient="records")

    def new_cat_logic(self, cat_data, ppr_obj):
        cat_data = json.loads(cat_data)
        pprservice = Pprservice(self._scope())
        keys = Pprutility_keys()
        output = []
        cat_datauniq = []
        for i in cat_data:
            if i["cat_id"] != 0 and i["categoryname"] != "" and i["expense_id"] != 0:
                if 'transactionmonth' in i:
                    if i["transactionmonth"] != 0:
                        cat_datauniq.append(i)
                if 'quarter' in i:
                    if i["quarter"] != 0:
                        cat_datauniq.append(i)
        try:
            if len(cat_datauniq) <= 0:
                pass
            else:
                year_term = ppr_obj.get_year_term()
                if year_term == "Monthly":
                    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                elif year_term == "Quarterly":
                    month = ["Quarterly_1", "Quarterly_2", "Quarterly_3", "Quarterly_4"]
                else:
                    return {"message": Pprdata_warning.month_quaterneed}
                uniqcatname = pprservice.remove_duplicate_arrdict(cat_datauniq, '', keys.cat_id, '')
                uniqcatlen = len(cat_datauniq) - 1
                for index, cat in enumerate(uniqcatname):
                    row = {}
                    status = []
                    for imonth in month:
                        row[imonth] = [Decimal(round(Decimal('0.00'), 2)), Decimal(round(Decimal('0.00'), 2)),
                                       Decimal(round(Decimal('0.00'), 2))]
                    for uniq_month in cat_datauniq:
                        if cat == uniq_month[keys.cat_id]:
                            row[keys.name] = uniq_month[keys.categoryname]
                            row[keys.cat_id] = uniq_month[keys.cat_id]
                            if int(uniq_month[keys.status]) not in status:
                                status.append(int(uniq_month[keys.status]))
                            row[keys.remark_key] = uniq_month[keys.remark_key]
                            if year_term == "Monthly":
                                if row[month[int(uniq_month[keys.transactionmonth]) - 1]][1] != Decimal(
                                        round(Decimal('0.00'), 2)):
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][1] = row[month[
                                        int(uniq_month[keys.transactionmonth]) - 1]][1] + Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][0] = row[month[
                                        int(uniq_month[keys.transactionmonth]) - 1]][0] + Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                else:
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][1] = Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][0] = Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                    if row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] != Decimal(
                                            round(Decimal('0.00'), 2)):
                                        row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] = row[month[
                                            int(uniq_month[keys.transactionmonth]) - 1]][2] + Decimal(
                                            round(Decimal(uniq_month["future_bgtamount"]), 2))
                                    else:
                                        row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] = Decimal(
                                            round(Decimal(uniq_month["future_bgtamount"]), 2))
                            if year_term == "Quarterly":
                                if row[f"Quarterly_{uniq_month[keys.quarter]}"][1] != Decimal(
                                        round(Decimal('0.00'), 2)) and f"Quarterly_{uniq_month[keys.quarter]}" in month:
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][1] = row[
                                                                                          f"Quarterly_{uniq_month[keys.quarter]}"][
                                                                                          1] + Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][0] = row[
                                                                                          f"Quarterly_{uniq_month[keys.quarter]}"][
                                                                                          0] + Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                else:
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][1] = Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][0] = Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][2] = Decimal(
                                        round(Decimal(uniq_month["future_bgtamount"]), 2))

                            row[keys.expense_id] = uniq_month[keys.expense_id]
                            if uniqcatlen == index:
                                row['page'] = 'Y'
                    ytd = [Decimal(round(Decimal('0.00'), 2)), Decimal(round(Decimal('0.00'), 2)),
                           Decimal(round(Decimal('0.00'), 2))]
                    for i in [0, 1, 2]:
                        totalsum = Decimal(round(Decimal('0.00'), 2))
                        for sumof_month in month:
                            totalsum = totalsum + row[sumof_month][i]
                        if i == 2:
                            ytd[i] = Decimal(round(Decimal(totalsum), 2))
                        else:
                            ytd[i] = totalsum
                    status.sort(reverse=True)
                    row[keys.status] = status[0]
                    row[keys.YTD] = ytd
                    row['tree_flag'] = 'Y'
                    row[keys.is_supplier_in] = 'Y'
                    row[keys.Padding_left] = '75px'
                    row[keys.Padding] = '10px'
                    output.append(row)

            return {"data": output}  # "pagination":subcat_data['pagination']
        except:
            return {"data": output}


    def future_budget_new_subcat_list(self, bgt_obj, pagequery):  # vys_page
        pprutility = MASTER_SERVICE(self._scope())
        bgtdata = []
        pro_list = NWisefinList()
        if bgt_obj.get_category_id() != None and bgt_obj.get_category_id() != "":
            subcat_obj = APsubcategory.objects.using(self._current_app_schema()).filter(category=bgt_obj.get_category_id(),entity_id=self._entity_id())
            for subcat in subcat_obj:
                condition = Q()
                if bgt_obj.get_status_id() != None and bgt_obj.get_status_id() != "":
                    condition = Q(status=bgt_obj.get_status_id())
                if pagequery != None and pagequery != "":
                    if pagequery == "APPROVER":
                        condition = Q(status=3,entity_id=self._entity_id())
                    elif pagequery == "CHECKER":
                        condition = Q(status=2,entity_id=self._entity_id())
                    elif pagequery == "VIEWER":
                        condition = Q(status=4,entity_id=self._entity_id())
                if bgt_obj.get_branch_id() != None and bgt_obj.get_branch_id() != "":
                    condition &= Q(apinvoicebranch_id=bgt_obj.get_branch_id())
                if bgt_obj.get_finyear() != None and bgt_obj.get_finyear() != "":
                    condition &= Q(
                        finyear=f'FY{int(bgt_obj.get_finyear().split("-")[0][-2:]) + 1}-{int(bgt_obj.get_finyear().split("-")[1]) + 1}')
                if bgt_obj.get_sector_name() != None and bgt_obj.get_sector_name() != "":
                    condition &= Q(sectorname=bgt_obj.get_sector_name())
                if bgt_obj.get_mstbusiness_segment_name() != None and bgt_obj.get_mstbusiness_segment_name() != "":
                    condition &= Q(bizname=bgt_obj.get_mstbusiness_segment_name())
                if bgt_obj.get_bs_name() != None and bgt_obj.get_bs_name() != "":
                    condition &= Q(bsname=bgt_obj.get_bs_name())
                if bgt_obj.get_cc_name() != None and bgt_obj.get_cc_name() != "":
                    condition &= Q(ccname=bgt_obj.get_cc_name())
                if bgt_obj.get_expense_id() != None and bgt_obj.get_expense_id() != "":
                    condition &= Q(apexpense_id=bgt_obj.get_expense_id())
                condition &= Q(apsubcat_id=subcat.id)
                if bgt_obj.get_year_term() == 'Monthly':
                    bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apsubcat_id',
                                                                                                   'transactionmonth',
                                                                                                   'apexpense_id',
                                                                                                   'status',
                                                                                                   'remark_key').annotate(
                        fut_bgt_amount=Sum('amount'))
                    # [vys_page.get_offset():vys_page.get_query_limit()]
                if bgt_obj.get_year_term() == 'Quarterly':
                    bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apsubcat_id',
                                                                                                   'quarter',
                                                                                                   'apexpense_id',
                                                                                                   'status',
                                                                                                   'remark_key').annotate(
                        fut_bgt_amount=Sum('amount'))
                    # [vys_page.get_offset():vys_page.get_query_limit()]
                subcat_ids = []
                subcat_ids.append(subcat.id)
                subcat_details = pprutility.get_cat_subcat(subcat_ids)
                if len(bgtdata) <= 0:
                    if bgt_obj.get_year_term() == 'Monthly':
                        tranmon1 = 4
                        for f in range(0, 12):
                            tranmon = tranmon1
                            if tranmon1 == 13:
                                tranmon = 1
                            if tranmon1 == 14:
                                tranmon = 2
                            if tranmon1 == 15:
                                tranmon = 3
                            pprresponser = pprresponse()
                            pprresponser.set_subcat_cat_data(subcat_details, subcat.id)
                            pprresponser.set_future_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                            pprresponser.set_transactionmonth(int(tranmon))
                            pprresponser.set_status(str(Decimal(0.0)))
                            pprresponser.set_remark_key("")
                            pro_list.data.append(pprresponser)
                            tranmon1 = tranmon1 + 1
                    if bgt_obj.get_year_term() == 'Quarterly':
                        tranmon1 = 1
                        for f in range(0, 4):
                            tranmon = tranmon1
                            pprresponser = pprresponse()
                            pprresponser.set_subcat_cat_data(subcat_details, subcat.id)
                            pprresponser.set_future_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                            pprresponser.set_status(str(Decimal(0.0)))
                            pprresponser.set_remark_key("")
                            pprresponser.set_quarter(int(tranmon))
                            pro_list.data.append(pprresponser)
                            tranmon1 = tranmon1 + 1
                else:
                    subcat_ids = []
                    for i in bgtdata:
                        subcat_ids.append(i['apsubcat_id'])

                    subcat_detials = pprutility.get_subcat(subcat_ids)
                    for i in bgtdata:
                        bgtresponser = BudgetBuilderresponse()
                        bgtresponser.set_subcat_datials_future(subcat_detials, i["apsubcat_id"])
                        bgtresponser.set_future_bgtamount(str(Decimal(i["fut_bgt_amount"]) / bgt_obj.get_divAmount()))
                        bgtresponser.set_status(i['status'])
                        bgtresponser.set_remark_key(i['remark_key'])
                        if bgt_obj.get_year_term() == 'Monthly':
                            bgtresponser.set_transactionmonth(int(i["transactionmonth"]))
                        if bgt_obj.get_year_term() == 'Quarterly':
                            bgtresponser.set_quarter(int(i["quarter"]))
                        bgtresponser.set_expense_id(i['apexpense_id'])
                        pro_list.data.append(bgtresponser)
                # vpage = PPRNWisefinPaginator(pprdata, vys_page.get_index(), 5)
                # pro_list.set_pagination(vpage)
            return pro_list

    def budget_new_subcat_list(self, bgt_obj):  # vys_page
        pprutility = MASTER_SERVICE(self._scope())
        bgtdata = []
        pro_list = NWisefinList()
        if bgt_obj.get_category_id() != None and bgt_obj.get_category_id() != "":
            subcat_obj = APsubcategory.objects.using(self._current_app_schema()).filter(category=bgt_obj.get_category_id(),entity_id=self._entity_id())
            for subcat in subcat_obj:
                condition = Q(status=2,entity_id=self._entity_id())
                if bgt_obj.get_branch_id() != None and bgt_obj.get_branch_id() != "":
                    condition &= Q(apinvoicebranch_id=bgt_obj.get_branch_id())
                if bgt_obj.get_finyear() != None and bgt_obj.get_finyear() != "":
                    condition &= Q(finyear=bgt_obj.get_finyear())
                if bgt_obj.get_sector_name() != None and bgt_obj.get_sector_name() != "":
                    condition &= Q(sectorname=bgt_obj.get_sector_name())
                if bgt_obj.get_mstbusiness_segment_name() != None and bgt_obj.get_mstbusiness_segment_name() != "":
                    condition &= Q(bizname=bgt_obj.get_mstbusiness_segment_name())
                if bgt_obj.get_bs_name() != None and bgt_obj.get_bs_name() != "":
                    condition &= Q(bsname=bgt_obj.get_bs_name())
                if bgt_obj.get_cc_name() != None and bgt_obj.get_cc_name() != "":
                    condition &= Q(ccname=bgt_obj.get_cc_name())
                if bgt_obj.get_expense_id() != None and bgt_obj.get_expense_id() != "":
                    condition &= Q(apexpense_id=bgt_obj.get_expense_id())
                condition &= Q(apsubcat_id=subcat.id)
                if bgt_obj.get_year_term() == 'Monthly':
                    bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apsubcat_id',
                                                                                                   'transactionmonth',
                                                                                                   'apexpense_id').annotate(
                        amount=Sum('amount'))
                    # [vys_page.get_offset():vys_page.get_query_limit()]
                if bgt_obj.get_year_term() == 'Quarterly':
                    bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apsubcat_id',
                                                                                                   'quarter',
                                                                                                   'apexpense_id').annotate(
                        amount=Sum('amount'))
                    # [vys_page.get_offset():vys_page.get_query_limit()]
                pro_list = NWisefinList()
                subcat_ids = []
                subcat_ids.append(subcat.id)
                subcat_details = pprutility.get_cat_subcat(subcat_ids)
                if len(bgtdata) <= 0:
                    if bgt_obj.get_year_term() == 'Monthly':
                        tranmon1 = 4
                        for f in range(0, 12):
                            tranmon = tranmon1
                            if tranmon1 == 13:
                                tranmon = 1
                            if tranmon1 == 14:
                                tranmon = 2
                            if tranmon1 == 15:
                                tranmon = 3
                            pprresponser = pprresponse()
                            pprresponser.set_subcat_cat_data(subcat_details, subcat.id)
                            pprresponser.set_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                            pprresponser.set_transactionmonth(int(tranmon))
                            pro_list.data.append(pprresponser)
                            tranmon1 = tranmon1 + 1
                    if bgt_obj.get_year_term() == 'Quarterly':
                        tranmon1 = 1
                        for f in range(0, 4):
                            tranmon = tranmon1
                            pprresponser = pprresponse()
                            pprresponser.set_subcat_cat_data(subcat_details, subcat.id)
                            pprresponser.set_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                            pprresponser.set_quarter(int(tranmon))
                            pro_list.data.append(pprresponser)
                            tranmon1 = tranmon1 + 1
                else:
                    subcat_ids = []
                    for i in bgtdata:
                        subcat_ids.append(i['apsubcat_id'])

                    subcat_detials = pprutility.get_subcat(subcat_ids)
                    for i in bgtdata:
                        bgtresponser = BudgetBuilderresponse()
                        bgtresponser.set_subcat_datials_future(subcat_detials, i["apsubcat_id"])
                        bgtresponser.set_bgtamount(str(Decimal(i['amount']) / bgt_obj.get_divAmount()))
                        if bgt_obj.get_year_term() == 'Monthly':
                            bgtresponser.set_transactionmonth(int(i["transactionmonth"]))
                        if bgt_obj.get_year_term() == 'Quarterly':
                            bgtresponser.set_quarter(int(i["quarter"]))
                        bgtresponser.set_expense_id(i['apexpense_id'])
                        pro_list.data.append(bgtresponser)
                # vpage = PPRNWisefinPaginator(pprdata, vys_page.get_index(), 5)
                # pro_list.set_pagination(vpage)
            return pro_list

    def compare_ppr_bgt_new_subcat(self, pprdata, bgtdata, bgt_obj):
        # try:
        logger.info('compare subcat start')

        # pprdata = {"data":[{'bgtamount': '0', 'cat_id': 47, 'expense_id': 19, 'subcat_id': 375, 'subcategoryname': 'SWEEPING CHARGES', 'transactionmonth': 4}]}
        pprdata = json.loads(pprdata)
        bgtdata = json.loads(bgtdata)
        # bgtdata = {"data":[{'amount': '0.11059', 'cat_id': 47, 'expense_id': 19, 'subcat_id': 375, 'subcategoryname': 'SWEEPING CHARGES', 'transactionmonth': 1}]}
        keys = Pprutility_keys()
        yearterm = bgt_obj.get_year_term()
        condition = ""
        valu_mQ = ""
        if yearterm == "Monthly":
            condition = keys.transactionmonth
            valu_mQ = "0"
        if yearterm == "Quarterly":
            condition = keys.quarter
            valu_mQ = 0
        if len(pprdata["data"]) <= 0:
            pprdata["data"] = [{
                condition: valu_mQ,
                "cat_id": 0,
                "expense_id": 0,
                "subcat_id": 0,
                "amount": "",
                "subcategoryname": ""
            }]
        if len(bgtdata["data"]) <= 0:
            bgtdata["data"] = [{
                condition: valu_mQ,
                "cat_id": 0,
                "expense_id": 0,
                "subcat_id": 0,
                "bgtamount": "",
                "subcategoryname": ""
            }]
        ppr_df = pd.DataFrame(pprdata["data"])
        # ppr_df1 = pd.DataFrame(pprdata["data"])
        bgt_df = pd.DataFrame(bgtdata["data"])
        # bgt_df1 = pd.DataFrame(bgtdata["data"])


        merge_data = pd.merge(ppr_df, bgt_df, how="left",
                              left_on=[condition,"cat_id","expense_id","subcat_id","subcategoryname"],
                              right_on=[condition,"cat_id","expense_id","subcat_id","subcategoryname"])
        final_merge = merge_data[
            [condition, "cat_id", "expense_id", "subcat_id", "subcategoryname", "bgtamount","amount"]].fillna(0)
        logger.info('compare subcat end ')

        return final_merge.to_json(orient="records")


    def compare_ppr_bgt_future_new_subcat(self, future_bgt, ppr_bgt, bgt_obj, pagequery):
        # try:
        logger.info('compare future subcat start')

        future_bgt = json.loads(future_bgt)
        ppr_bgt = json.loads(ppr_bgt)
        keys = Pprutility_keys()
        yearterm = bgt_obj.get_year_term()
        condition = ""
        valu_mQ = ""
        if yearterm == "Monthly":
            condition = keys.transactionmonth
            valu_mQ = "0"
        if yearterm == "Quarterly":
            condition = keys.quarter
            valu_mQ = 0
        if len(ppr_bgt) <= 0:
            ppr_bgt = [{
                condition: valu_mQ,
                "cat_id": 0,
                "expense_id": 0,
                "subcat_id": 0,
                "subcategoryname": "",
                "bgtamount": "",
                "amount": ""
            }]
        if len(future_bgt["data"]) <= 0:
            future_bgt["data"] = [{
                "cat_id": 0,
                "expense_id": 0,
                "subcat_id": 0,
                "subcategoryname": "",
                "future_bgtamount": "",
                "status": 0,
                "remark_key": "",
                condition: valu_mQ
            }]
        ppr_bgtDF = pd.DataFrame(ppr_bgt)
        future_bgtDF = pd.DataFrame(future_bgt["data"])
        merge_data = pd.merge(future_bgtDF, ppr_bgtDF, how="outer",
                              left_on=["cat_id",condition, "expense_id", "subcat_id", "subcategoryname"],
                              right_on=["cat_id",condition, "expense_id", "subcat_id", "subcategoryname"])
        final_merge = merge_data[
            ["cat_id", condition, "expense_id", "subcat_id", "subcategoryname", "future_bgtamount", "bgtamount",
             "amount", 'status', 'remark_key']].fillna(0)
        logger.info('compare future subcat end')

        if pagequery != None and pagequery != "":
            if pagequery == "APPROVER":
                return final_merge[final_merge['status'] == 3.0].to_json(orient="records")
            elif pagequery == "VIEWER":
                return final_merge[final_merge['status'] == 4.0].to_json(orient="records")
            elif pagequery == "CHECKER":
                return final_merge[final_merge['status'] == 2.0].to_json(orient="records")
        if bgt_obj.get_status_id() != None and bgt_obj.get_status_id() != "":
            return final_merge[final_merge['status'] == int(bgt_obj.get_status_id())].to_json(orient="records")

        return final_merge.to_json(orient="records")

    def subcat_logic(self, subcat_data, ppr_obj):
        subcat_data = json.loads(subcat_data)
        pprservice = Pprservice(self._scope())
        keys = Pprutility_keys()
        output = []
        subcat_datauniq = []
        for i in subcat_data:
            if i["cat_id"] != 0 and i["subcat_id"] != 0 and i["subcategoryname"] != "" and i["expense_id"] != 0:
                if 'transactionmonth' in i:
                    if i["transactionmonth"] != "0":
                        subcat_datauniq.append(i)
                if 'quarter' in i:
                    if i["quarter"] != 0:
                        subcat_datauniq.append(i)
        try:
            if len(subcat_datauniq) <= 0:
                pass
            else:
                year_term = ppr_obj.get_year_term()
                if year_term == "Monthly":
                    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                elif year_term == "Quarterly":
                    month = ["Quarterly_1", "Quarterly_2", "Quarterly_3", "Quarterly_4"]
                else:
                    return {"message": Pprdata_warning.month_quaterneed}
                uniqsubcatname = pprservice.remove_duplicate_arrdict(subcat_datauniq, '', keys.subcat_id, '')
                uniqsubcatlen = len(uniqsubcatname) - 1
                for index, subcat in enumerate(uniqsubcatname):
                    row = {}
                    status = []
                    for imonth in month:
                        row[imonth] = [Decimal(round(Decimal('0.00'), 2)), Decimal(round(Decimal('0.00'), 2)),
                                       Decimal(round(Decimal('0.00'), 2))]
                    for uniq_month in subcat_datauniq:
                        if subcat == uniq_month[keys.subcat_id]:
                            row[keys.cat_id] = uniq_month[keys.cat_id]
                            row[keys.name] = uniq_month[keys.subcategoryname]
                            if int(uniq_month[keys.status]) not in status:
                                status.append(int(uniq_month[keys.status]))
                            row[keys.remark_key] = uniq_month[keys.remark_key]
                            if year_term == "Monthly":
                                if row[month[int(uniq_month[keys.transactionmonth]) - 1]][1] != Decimal(
                                        round(Decimal('0.00'), 2)):
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][1] = row[month[
                                        int(uniq_month[keys.transactionmonth]) - 1]][1] + Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][0] = row[month[
                                        int(uniq_month[keys.transactionmonth]) - 1]][0] + Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                else:
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][1] = Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[month[int(uniq_month[keys.transactionmonth]) - 1]][0] = Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                    if row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] != Decimal(
                                            round(Decimal('0.00'), 2)):
                                        row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] = row[month[
                                            int(uniq_month[keys.transactionmonth]) - 1]][2] + Decimal(
                                            round(Decimal(uniq_month["future_bgtamount"]), 2))
                                    else:
                                        row[month[int(uniq_month[keys.transactionmonth]) - 1]][2] = Decimal(
                                            round(Decimal(uniq_month["future_bgtamount"]), 2))
                            if year_term == "Quarterly":
                                if row[f"Quarterly_{uniq_month[keys.quarter]}"][1] != Decimal(
                                        round(Decimal('0.00'), 2)) and f"Quarterly_{uniq_month[keys.quarter]}" in month:
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][1] = row[
                                                                                          f"Quarterly_{uniq_month[keys.quarter]}"][
                                                                                          1] + Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][0] = row[
                                                                                          f"Quarterly_{uniq_month[keys.quarter]}"][
                                                                                          0] + Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                else:
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][1] = Decimal(
                                        round(Decimal(uniq_month["amount"]), 2))
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][0] = Decimal(
                                        round(Decimal(uniq_month["bgtamount"]), 2))
                                    row[f"Quarterly_{uniq_month[keys.quarter]}"][2] = Decimal(
                                        round(Decimal(uniq_month["future_bgtamount"]), 2))

                            row[keys.subcat_id] = uniq_month[keys.subcat_id]
                            row[keys.expense_id] = uniq_month[keys.expense_id]
                            if uniqsubcatlen == index:
                                row['page'] = 'Y'
                    ytd = [Decimal(round(Decimal('0.00'), 2)), Decimal(round(Decimal('0.00'), 2)),
                           Decimal(round(Decimal('0.00'), 2))]
                    for i in [0, 1, 2]:
                        totalsum = Decimal(round(Decimal('0.00'), 2))
                        for sumof_month in month:
                            totalsum = totalsum + row[sumof_month][i]
                        if i == 2:
                            ytd[i] = Decimal(round(Decimal(totalsum), 2))
                        else:
                            ytd[i] = totalsum
                    status.sort(reverse=True)
                    row[keys.status] = status[0]
                    row[keys.YTD] = ytd
                    row['tree_flag'] = 'Y'
                    row[keys.is_supplier_in] = 'Y'
                    row[keys.Padding_left] = '100px'
                    row[keys.Padding] = '10px'
                    output.append(row)

            return {"data": output}  # "pagination":subcat_data['pagination']
        except:
            return {"data": output}


    def new_future_budget_expensegrp_list(self, bgt_obj, pagequery):
        bgtdata = []
        pro_list = NWisefinList()
        pprutility = MASTER_SERVICE(self._scope())

        expensegrp_id = APexpensegroup.objects.using(self._current_app_schema()).filter(status=1,entity_id=self._entity_id())
        for exgrp_id in expensegrp_id:
            expense_id = pprutility.get_new_expgrp_exp([exgrp_id.id])
            if len(expense_id) == 0:
                if bgt_obj.get_year_term() == 'Monthly':
                    tranmon1 = 4
                    for f in range(0, 12):
                        tranmon = tranmon1
                        if tranmon1 == 13:
                            tranmon = 1
                        if tranmon1 == 14:
                            tranmon = 2
                        if tranmon1 == 15:
                            tranmon = 3
                        pprresponser = pprresponse()
                        pprresponser.expensegrp_id = exgrp_id.id
                        pprresponser.expensegrpname = exgrp_id.name
                        pprresponser.set_future_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                        if bgt_obj.get_year_term() == 'Monthly':
                            pprresponser.set_transactionmonth(tranmon)
                        pprresponser.set_status(str(Decimal(0.0)))
                        pprresponser.set_remark_key("")
                        pro_list.data.append(pprresponser)
                        tranmon1 = tranmon1 + 1
                if bgt_obj.get_year_term() == 'Quarterly':
                    tranmon1 = 1
                    for f in range(0, 4):
                        tranmon = tranmon1
                        pprresponser = pprresponse()
                        pprresponser.expensegrp_id = exgrp_id.id
                        pprresponser.expensegrpname = exgrp_id.name
                        pprresponser.set_future_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                        pprresponser.set_quarter(tranmon)
                        pprresponser.set_status(str(Decimal(0.0)))
                        pprresponser.set_remark_key("")
                        pro_list.data.append(pprresponser)
                        tranmon1 = tranmon1 + 1
            else:

                for expense in expense_id:
                    condition = Q(apexpense_id=expense,entity_id=self._entity_id())
                    if bgt_obj.get_status_id() != None and bgt_obj.get_status_id() != "":
                        condition = Q(status=bgt_obj.get_status_id())
                    if pagequery != None and pagequery != "":
                        if pagequery == "APPROVER":
                            condition = Q(status=3,entity_id=self._entity_id())
                        elif pagequery == "CHECKER":
                            condition = Q(status=2,entity_id=self._entity_id())
                        elif pagequery == "VIEWER":
                            condition = Q(status=4,entity_id=self._entity_id())
                    if bgt_obj.get_finyear() != None and bgt_obj.get_finyear() != "":
                        condition &= Q(
                            finyear=f'FY{int(bgt_obj.get_finyear().split("-")[0][-2:]) + 1}-{int(bgt_obj.get_finyear().split("-")[1]) + 1}')
                    if bgt_obj.get_branch_id() != None and bgt_obj.get_branch_id() != "":
                        condition &= Q(apinvoicebranch_id=bgt_obj.get_branch_id())
                    if bgt_obj.get_sector_name() != None and bgt_obj.get_sector_name() != "":
                        condition &= Q(sectorname=bgt_obj.get_sector_name())
                    if bgt_obj.get_mstbusiness_segment_name() != None and bgt_obj.get_mstbusiness_segment_name() != "":
                        condition &= Q(bizname=bgt_obj.get_mstbusiness_segment_name())
                    if bgt_obj.get_bs_name() != None and bgt_obj.get_bs_name() != "":
                        condition &= Q(bsname=bgt_obj.get_bs_name())
                    if bgt_obj.get_cc_name() != None and bgt_obj.get_cc_name() != "":
                        condition &= Q(ccname=bgt_obj.get_cc_name())
                    condition &= Q(apexpense_id=expense)
                    if bgt_obj.get_year_term() == 'Monthly':
                        bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id',
                                                                                                       'transactionmonth',
                                                                                                       'status',
                                                                                                       'remark_key').annotate(
                            fut_bgt_amount=Sum('amount'))
                    if bgt_obj.get_year_term() == 'Quarterly':
                        bgtdata = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id',
                                                                                                       'quarter',
                                                                                                       'status',
                                                                                                       'remark_key').annotate(
                            fut_bgt_amount=Sum('amount'))
                    if len(bgtdata) <= 0:
                        if bgt_obj.get_year_term() == 'Monthly':
                            tranmon1 = 4
                            for f in range(0, 12):
                                tranmon = tranmon1
                                if tranmon1 == 13:
                                    tranmon = 1
                                if tranmon1 == 14:
                                    tranmon = 2
                                if tranmon1 == 15:
                                    tranmon = 3
                                pprresponser = pprresponse()
                                pprresponser.expensegrp_id = exgrp_id.id
                                pprresponser.expensegrpname = exgrp_id.name
                                pprresponser.set_future_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                                pprresponser.set_status(str(Decimal(0.0)))
                                pprresponser.set_transactionmonth(tranmon)
                                pprresponser.set_remark_key("")
                                pro_list.data.append(pprresponser)

                                tranmon1 = tranmon1 + 1
                        if bgt_obj.get_year_term() == 'Quarterly':
                            tranmon1 = 1
                            for f in range(0, 4):
                                tranmon = tranmon1
                                pprresponser = pprresponse()
                                pprresponser.expensegrp_id = exgrp_id.id
                                pprresponser.expensegrpname = exgrp_id.name
                                pprresponser.set_future_bgtamount(str(Decimal(0.0) / bgt_obj.get_divAmount()))
                                pprresponser.set_quarter(tranmon)
                                pprresponser.set_status(str(Decimal(0.0)))
                                pprresponser.set_remark_key("")
                                pro_list.data.append(pprresponser)
                                tranmon1 = tranmon1 + 1
                    else:
                        for i in bgtdata:
                            bgtresponser = BudgetBuilderresponse()
                            bgtresponser.expensegrp_id = exgrp_id.id
                            bgtresponser.expensegrpname = exgrp_id.name
                            bgtresponser.set_future_bgtamount(
                                str(Decimal(i["fut_bgt_amount"]) / bgt_obj.get_divAmount()))
                            bgtresponser.set_status(i['status'])
                            bgtresponser.set_remark_key(i['remark_key'])
                            if bgt_obj.get_year_term() == 'Monthly':
                                bgtresponser.set_transactionmonth(i["transactionmonth"])
                            if bgt_obj.get_year_term() == 'Quarterly':
                                bgtresponser.set_quarter(i["quarter"])
                            bgtresponser.set_status(i['status'])
                            bgtresponser.set_remark_key(i['remark_key'])
                            pro_list.data.append(bgtresponser)
        return pro_list

    def bgt_future_data_checker_set(self, filter_obj):
        status = ReftableType()
        condition = Q(status__in=(1,6),entity_id=self._entity_id())
        if filter_obj.get_branch_id() != None and filter_obj.get_branch_id() != "":
            condition &= Q(apinvoicebranch_id=filter_obj.get_branch_id())
        if filter_obj.get_finyear() != None and filter_obj.get_finyear() != "":
            condition &= Q(
                finyear=f'FY{int(filter_obj.get_finyear().split("-")[0][-2:])}-{int(filter_obj.get_finyear().split("-")[1])}')
        if filter_obj.get_sector_name() != None and filter_obj.get_sector_name() != "":
            condition &= Q(sectorname=filter_obj.get_sector_name())
        if filter_obj.get_mstbusiness_segment_name() != None and filter_obj.get_mstbusiness_segment_name() != "":
            condition &= Q(bizname=filter_obj.get_mstbusiness_segment_name())
        if filter_obj.get_bs_name() != None and filter_obj.get_bs_name() != "":
            condition &= Q(bsname=filter_obj.get_bs_name())
        if filter_obj.get_cc_name() != None and filter_obj.get_cc_name() != "":
            condition &= Q(ccname=filter_obj.get_cc_name())
        bgt_obj = Budgetdetial.objects.using(self._current_app_schema()).filter(condition)
        bgt_obj1 = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).update(status=status.BudgetBuilder)
        suc_obj = Success()
        suc_obj.set_status(successMessage.SUCCESS)
        return suc_obj

    def bgt_future_data_status_set(self, filter_obj, status, level, empid, remark_val):
        util = ReftableType()
        keys = Pprutility_keys()
        utility = Ppr_utilityservice(self._scope())
        if level == "APPROVER":
            condition = Q(status=util.BudgetChecker,entity_id=self._entity_id())
        if level == "CHECKER":
            condition = Q(status=util.BudgetBuilder,entity_id=self._entity_id())
        if filter_obj.get_branch_id() != None and filter_obj.get_branch_id() != "":
            condition &= Q(apinvoicebranch_id=filter_obj.get_branch_id())
        if filter_obj.get_finyear() != None and filter_obj.get_finyear() != "":
            condition &= Q(finyear=filter_obj.get_finyear())
        if filter_obj.get_sector_name() != None and filter_obj.get_sector_name() != "":
            condition &= Q(sectorname=filter_obj.get_sector_name())
        if filter_obj.get_mstbusiness_segment_name() != None and filter_obj.get_mstbusiness_segment_name() != "":
            condition &= Q(bizname=filter_obj.get_mstbusiness_segment_name())
        if filter_obj.get_bs_name() != None and filter_obj.get_bs_name() != "":
            condition &= Q(bsname=filter_obj.get_bs_name())
        if filter_obj.get_cc_name() != None and filter_obj.get_cc_name() != "":
            condition &= Q(ccname=filter_obj.get_cc_name())
        bgt_obj1 = Budgetdetial.objects.using(self._current_app_schema()).filter(condition)[0]
        if level == "APPROVER":
            utility.mantain_history(empid, keys.Budget_approver, {}, CRUDstatus().update, bgt_obj1.remark_key,
                                    remark_val)

        if level == "CHECKER":
            utility.mantain_history(empid, keys.Budget_checker, {}, CRUDstatus().update, bgt_obj1.remark_key,
                                    remark_val)

        bgt_obj = Budgetdetial.objects.using(self._current_app_schema()).filter(condition).update(status=status)
        suc_obj = Success()
        suc_obj.set_status(successMessage.SUCCESS)
        return suc_obj


    def upload(self, request,type,emp_id):
        if not request.FILES['file'] is None:
            try:
                logger.info("s3 starts")
                file_count = len(request.FILES.getlist('file'))
                resp_list = NWisefinList()
                prefix='PPR'
                for i in range(0, file_count):
                    file = request.FILES.getlist('file')[i]
                    file_name = file.name
                    file_size = file.size
                    file_name_new = prefix + str(datetime.now().strftime("%y%m%d_%H%M%S")) + file_name
                    contents = file
                    logger.info("s31" + str(file_name))
                    s3 = boto3.resource('s3')
                    s3_obj = s3.Object(bucket_name=settings.BUCKET_NAME_FOR_ASSETS, key=file_name_new)
                    logger.info("s32" + str(s3_obj))
                    s3_obj.put(Body=contents)
                    doc_obj=PPR_Documents.objects.create(file_name=file_name,gen_filename=file_name_new,file_size=file_size,
                                                         type=type,created_by=emp_id)
                    doc_data = BudgetBuilderresponse()
                    doc_data.set_id(doc_obj.id)
                    doc_data.file_name=doc_obj.file_name
                    doc_data.gen_file_name=doc_obj.gen_filename
                    doc_data.file_size=doc_obj.file_size
                    doc_data.type=doc_obj.type
                    doc_data.status=doc_obj.status
                    doc_data.created_by=doc_obj.created_by
                    doc_data.created_date=str(doc_obj.created_date)
                    resp_list.append(doc_data)
                    logger.info("after s3" + str(doc_data))
                return resp_list
            except KeyError:
                logger.info('Kindly pass file information')
