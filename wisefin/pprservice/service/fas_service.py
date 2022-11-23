
from django.db.models import Count,Sum
from django.db.models import Q
from pprservice.models.pprmodel import Pprdata_maintable

from pprservice.data.response.fasresponse import FasResponse
from pprservice.data.response.success import Success,successMessage
from pprservice.util.pprutility import Ppr_utilityservice, MASTER_SERVICE

from decimal import Decimal
from pprservice.util.pprutility import Ppr_utilityservice, Pprutility_keys

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from pprservice.util.pprutility import USER_SERVICE




class FasService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.PPR_SERVICE)

    def incomedata_create(self, obj,empid,levelquery,sectorquery):
        utility = Ppr_utilityservice(self._scope())
        masterservice = MASTER_SERVICE(self._scope())
        userservice=USER_SERVICE(self._scope())
        bulk_arr = []
        glno =[]
        branch_code = []
        bs_code = []
        cc_code = []
        for i in obj:
            glno.append(int(i['AC_NO']))
            branch_code.append(i['V_BRANCH_CODE'])
            bs_code.append(i["BS_Code"])
            cc_code.append(i["CC_Code"])
        subcat_cat_expense = masterservice.get_subcat_glno_new(glno)
        branch_id = userservice.get_branch_code(branch_code)
        bs_id = userservice.get_BS_Code(bs_code)
        cc_id = userservice.get_CC_Code(cc_code)
        print(bs_id)
        print(cc_id)
        for i in obj:
            date = utility.get_finyear_quter_transationmonth(str(i['FIC_MIS_DATE'].date()))
            subcat_cat_expense__ = {}
            branch = 0
            bsID = None
            ccID = None
            for l in bs_id:
                if int(l["code"]) == int(i["BS_Code"]):
                    bsID = l["id"]
            for p in cc_id:
                if int(p["code"]) == int(i["CC_Code"]):
                    ccID = p["id"]
            for k in branch_id:
                if k.code == i['V_BRANCH_CODE']:
                    branch = k.id
            for j in subcat_cat_expense:
                if j['glno'] == i['AC_NO']:
                    subcat_cat_expense__ = j
            fas_val = Pprdata_maintable(
                finyear=date['finyear'],
                quarter=date['quater'],
                transactionmonth=date['transationmonth'],
                transactionyear=date['year'],
                transactiondate=i["FIC_MIS_DATE"],
                bsname=i['BS'],
                ccname=i['CC'],
                bs_code=bsID,
                cc_code=ccID,
                bizname=i['VERTICAL_CLASS'],
                sectorname=str(sectorquery),
                amount=float(i['LCY_AMOUNT']),
                account_no=i['AC_NO'],
                DRCR_IN=i['DRCR_IND'],
                apinvoicebranch_id=branch,
                categorygid=subcat_cat_expense__['category__id'],
                apsubcat_id=subcat_cat_expense__['id'],
                apexpense_id=subcat_cat_expense__['category__expense__id'],
                status=1,
                create_by=empid,
                level=int(levelquery)
            )
            bulk_arr.append(fas_val)
        Pprdata_maintable.objects.bulk_create(bulk_arr)
        suc_obj = Success()
        suc_obj.set_status(successMessage.SUCCESS)
        return suc_obj


    def get_BS_CC_ID(self,arr):
        userservice = USER_SERVICE(self._scope())
        pprutility = Ppr_utilityservice(self._scope())
        bs_code = []
        cc_code = []
        for i in arr:
            bs_code.append(i['bs_code'])
            cc_code.append(i['cc_code'])
        bs_ids = userservice.get_BS_Code(bs_code)
        cc_ids = userservice.get_CC_Code(cc_code)
        return {"bs_id":bs_ids,"cc_id":cc_ids}

    def level_fetch(self,request_obj):
        pprutility = MASTER_SERVICE(self._scope())
        ppr_service = Ppr_utilityservice(self._scope())
        condition = Q(status=1,entity_id=self._entity_id())
        groupcondition = ""
        if request_obj.get_finyear() != None and request_obj.get_finyear() != '':
            condition&=Q(finyear=request_obj.get_finyear())
        if request_obj.get_bs_code() != None and request_obj.get_bs_code() != '':
            condition&=Q(bs_code=request_obj.get_bs_code())
        if request_obj.get_cc_code() != None and request_obj.get_cc_code() != '':
            condition&=Q(cc_code=request_obj.get_cc_code())
        if request_obj.get_bizname() != None and request_obj.get_bizname() != '':
            condition&=Q(bizname=request_obj.get_bizname())
        if request_obj.get_sectorname() != None and request_obj.get_sectorname() != '':
            condition&=Q(sectorname=request_obj.get_sectorname())
        if request_obj.get_branch_id() != None and request_obj.get_branch_id() != '':
            condition&=Q(apinvoicebranch_id=request_obj.get_branch_id())
        if request_obj.get_yearterm() == "Monthly":
            groupcondition = "transactionmonth"
        if request_obj.get_yearterm() == "Quarterly":
            groupcondition = "quarter"
        if request_obj.get_expensegrp() != None and request_obj.get_expensegrp() != '' and len(request_obj.get_expensegrp()) > 0:
            expense_id = pprutility.get_expense_expensegrp(request_obj.get_expensegrp())
            condition &= Q(apexpense_id__in=expense_id)
        fas_var = Pprdata_maintable.objects.using(self._current_app_schema()).filter(condition).values('level',groupcondition).annotate(Income_amount=Sum('amount')).order_by('level')
        fasList = fas_custom_list()
        if len(fas_var) <= 0:
            pass
        else:
            level_ids = []
            for i in fas_var:
                level_ids.append(i["level"])
            level_detials = ppr_service.get_level(level_ids)
            for i in fas_var:
                response = FasResponse()
                # response.set_level_name('LEVEL-0 INCOME DATA')
                # response.set_level_id(i['level'])
                response.set_level_data(level_detials,i['level'])
                if request_obj.get_yearterm() == "Monthly":
                    response.set_transactionmonth(i[groupcondition])
                if request_obj.get_yearterm() == "Quarterly":
                    response.set_quarter(i[groupcondition])
                response.set_income_amount(Decimal(i['Income_amount']/request_obj.get_divAmount()))
                fasList.append(response.get())
        return fasList

    def level_logic(self,IN_arr,request_obj):
        output = []
        keys = Pprutility_keys()
        return_obj = fas_custom_list()
        if len(IN_arr) <=0:
            pass
        else:
            try:
                key_transactionmonth = keys.transactionmonth
                key_name = keys.name
                key_quarter = keys.quarter
                key_level_id = keys.level_id
                key_level_name = keys.level_name
                key_income_amount = keys.income_amount
                level_data = IN_arr
                yearTeam = request_obj.get_yearterm()
                if yearTeam == "Monthly":
                    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                elif yearTeam == "Quarterly":
                    month = ["Quarterly_1", "Quarterly_2", "Quarterly_3", "Quarterly_4"]
                level_id = []
                for l in level_data:
                    if l[key_level_id] not in level_id:
                        level_id.append(l[key_level_id])
                for k in level_id:
                    level_row = {}
                    for m in month:
                        level_row[m]=Decimal(round(Decimal('0.00'), 2))
                    for j in level_data:
                        if k == j[key_level_id]:
                            level_row[key_name] = j[key_level_name]
                            level_row[key_level_id] = j[key_level_id]
                            if yearTeam == "Monthly":
                                if level_row[month[int(j[key_transactionmonth])-1]] != Decimal(round(Decimal('0.00'), 2)):
                                    level_row[month[int(j[key_transactionmonth])-1]] = Decimal(level_row[month[int(j[key_transactionmonth])-1]])+Decimal(
                                            round(Decimal(j[key_income_amount]), 2))
                                else:
                                    level_row[month[int(j[key_transactionmonth])-1]] = Decimal(
                                            round(Decimal(j[key_income_amount]), 2))
                            elif yearTeam == "Quarterly":
                                if level_row[f"Quarterly_{j[key_quarter]}"] != Decimal(round(Decimal('0.00'), 2)):
                                    level_row[f"Quarterly_{j[key_quarter]}"] = Decimal(level_row[f"Quarterly_{j[key_quarter]}"])+Decimal(
                                            round(Decimal(j[key_income_amount]), 2))
                                else:
                                    level_row[f"Quarterly_{j[key_quarter]}"] = Decimal(
                                            round(Decimal(j[key_income_amount]), 2))
                    totalsum = Decimal(round(Decimal('0.00'), 2))
                    for sumof_month in month:
                        totalsum = totalsum + level_row[sumof_month]
                    level_row['YTD'] = totalsum
                    level_row['tree_flag'] = 'Y'
                    level_row[keys.Padding_left] = '10px'
                    level_row[keys.Padding] = '5px'
                    output.append(level_row)
                output.append(self.columndata_sum(month,output,'10px'))
            except Exception as e:
                return_obj.set_output(str(e))
                return return_obj.get_dict_return()
        return_obj.set_output(output)
        return return_obj.get_dict_return()


    def fas_expenseGrp_fetch(self,request_obj):
        pprutility = MASTER_SERVICE(self._scope())
        condition = Q(status=1,entity_id=self._entity_id())
        groupcondition = ""
        if request_obj.get_level_id() != None and request_obj.get_level_id() != '':
            condition &= Q(level=request_obj.get_level_id())
        if request_obj.get_finyear() != None and request_obj.get_finyear() != '':
            condition &= Q(finyear=request_obj.get_finyear())
        if request_obj.get_bs_code() != None and request_obj.get_bs_code() != '':
            condition &= Q(bs_code=request_obj.get_bs_code())
        if request_obj.get_cc_code() != None and request_obj.get_cc_code() != '':
            condition &= Q(cc_code=request_obj.get_cc_code())
        if request_obj.get_bizname() != None and request_obj.get_bizname() != '':
            condition &= Q(bizname=request_obj.get_bizname())
        if request_obj.get_sectorname() != None and request_obj.get_sectorname() != '':
            condition &= Q(sectorname=request_obj.get_sectorname())
        if request_obj.get_branch_id() != None and request_obj.get_branch_id() != '':
            condition &= Q(apinvoicebranch_id=request_obj.get_branch_id())
        if request_obj.get_yearterm() == "Monthly":
            groupcondition = "transactionmonth"
        if request_obj.get_yearterm() == "Quarterly":
            groupcondition = "quarter"
        if request_obj.get_expensegrp() != None and request_obj.get_expensegrp() != '' and len(
                request_obj.get_expensegrp()) > 0:
            expense_id = pprutility.get_expense_expensegrp(request_obj.get_expensegrp())
            condition &= Q(apexpense_id__in=expense_id)
        fas_var = Pprdata_maintable.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id','level', groupcondition).annotate(
            Income_amount=Sum('amount'))
        fasList = fas_custom_list()
        if len(fas_var) <= 0:
            pass
        else:
            expense_ids = []
            for j in fas_var:
                expense_ids.append(j['apexpense_id'])
            expense_detials = pprutility.get_expense(expense_ids)
            for i in fas_var:
                response = FasResponse()
                response.set_expense_data(expense_detials,i['apexpense_id'])
                response.set_level_id(i['level'])
                if request_obj.get_yearterm() == "Monthly":
                    response.set_transactionmonth(i[groupcondition])
                if request_obj.get_yearterm() == "Quarterly":
                    response.set_quarter(i[groupcondition])
                response.set_income_amount(Decimal(i['Income_amount']/request_obj.get_divAmount()))
                fasList.append(response.get())
        return fasList

    def expenseGrp_logic(self,IN_arr,request_obj):
        output = []
        keys = Pprutility_keys()
        return_obj = fas_custom_list()
        if len(IN_arr) <=0:
            pass
        else:
            try:
                key_transactionmonth = keys.transactionmonth
                key_name = keys.name
                key_quarter = keys.quarter
                key_level_id = keys.level_id
                key_expensegrpname = keys.expensegrpname
                key_income_amount = keys.income_amount
                expenseGrp_data = IN_arr
                yearTeam = request_obj.get_yearterm()
                if yearTeam == "Monthly":
                    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                elif yearTeam == "Quarterly":
                    month = ["Quarterly_1", "Quarterly_2", "Quarterly_3", "Quarterly_4"]
                expenseGrp_names = []
                for l in expenseGrp_data:
                    if l[key_expensegrpname] not in expenseGrp_names:
                        expenseGrp_names.append(l[key_expensegrpname])
                for k in expenseGrp_names:
                    expenseGrp_row = {}
                    expenseGrp_row[key_name] = k
                    for m in month:
                        expenseGrp_row[m]=Decimal(round(Decimal('0.00'), 2))
                    for j in expenseGrp_data:
                        if k == j[key_expensegrpname]:
                            expenseGrp_row[key_level_id] = j[key_level_id]
                            if yearTeam == "Monthly":
                                if expenseGrp_row[month[int(j[key_transactionmonth])-1]] != Decimal(round(Decimal('0.00'), 2)):
                                    expenseGrp_row[month[int(j[key_transactionmonth])-1]] = Decimal(expenseGrp_row[month[int(j[key_transactionmonth])-1]])+Decimal(
                                            round(Decimal(j[key_income_amount]), 2))
                                else:
                                    expenseGrp_row[month[int(j[key_transactionmonth])-1]] = Decimal(
                                            round(Decimal(j[key_income_amount]), 2))
                            elif yearTeam == "Quarterly":
                                if expenseGrp_row[f"Quarterly_{j[key_quarter]}"] != Decimal(round(Decimal('0.00'), 2)):
                                    expenseGrp_row[f"Quarterly_{j[key_quarter]}"] = Decimal(expenseGrp_row[f"Quarterly_{j[key_quarter]}"])+Decimal(
                                            round(Decimal(j[key_income_amount]), 2))
                                else:
                                    expenseGrp_row[f"Quarterly_{j[key_quarter]}"] = Decimal(
                                            round(Decimal(j[key_income_amount]), 2))
                    totalsum = Decimal(round(Decimal('0.00'), 2))
                    for sumof_month in month:
                        totalsum = totalsum + expenseGrp_row[sumof_month]
                    expenseGrp_row['YTD'] = totalsum
                    expenseGrp_row['tree_flag'] = 'Y'
                    expenseGrp_row[keys.Padding_left] = '50px'
                    expenseGrp_row[keys.Padding] = '5px'
                    output.append(expenseGrp_row)
            except Exception as e:
                return_obj.set_output(str(e))
                return return_obj.get_dict_return()
        return_obj.set_output(output)
        return return_obj.get_dict_return()


    def fas_expense_fetch(self,request_obj):
        pprutility = MASTER_SERVICE(self._scope())
        condition = Q(status=1,entity_id=self._entity_id())
        groupcondition = ""
        if request_obj.get_level_id() != None and request_obj.get_level_id() != '':
            condition &= Q(level=request_obj.get_level_id())
        if request_obj.get_finyear() != None and request_obj.get_finyear() != '':
            condition &= Q(finyear=request_obj.get_finyear())
        if request_obj.get_bs_code() != None and request_obj.get_bs_code() != '':
            condition &= Q(bs_code=request_obj.get_bs_code())
        if request_obj.get_cc_code() != None and request_obj.get_cc_code() != '':
            condition &= Q(cc_code=request_obj.get_cc_code())
        if request_obj.get_bizname() != None and request_obj.get_bizname() != '':
            condition &= Q(bizname=request_obj.get_bizname())
        if request_obj.get_sectorname() != None and request_obj.get_sectorname() != '':
            condition &= Q(sectorname=request_obj.get_sectorname())
        if request_obj.get_branch_id() != None and request_obj.get_branch_id() != '':
            condition &= Q(apinvoicebranch_id=request_obj.get_branch_id())
        if request_obj.get_yearterm() == "Monthly":
            groupcondition = "transactionmonth"
        if request_obj.get_yearterm() == "Quarterly":
            groupcondition = "quarter"
        if request_obj.get_expensegrp_individual() != None and request_obj.get_expensegrp_individual() != '':
            expense_id = pprutility.get_new_expense_expensegrp(request_obj.get_expensegrp_individual())
            condition &= Q(apexpense_id__in=expense_id)
        fas_var = Pprdata_maintable.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id', 'level',
                                                                                            groupcondition).annotate(Income_amount=Sum('amount'))
        fasList = fas_custom_list()
        if len(fas_var) <= 0:
            pass
        else:
            expense_ids = []
            for j in fas_var:
                expense_ids.append(j['apexpense_id'])
            expense_detials = pprutility.get_expense(expense_ids)
            for i in fas_var:
                response = FasResponse()
                response.set_expense_data(expense_detials, i['apexpense_id'])
                response.set_level_id(i['level'])
                if request_obj.get_yearterm() == "Monthly":
                    response.set_transactionmonth(i[groupcondition])
                if request_obj.get_yearterm() == "Quarterly":
                    response.set_quarter(i[groupcondition])
                response.set_income_amount(Decimal(i['Income_amount'] / request_obj.get_divAmount()))
                fasList.append(response.get())
        return fasList

    def expense_logic(self,IN_arr,request_obj):
        output = []
        keys = Pprutility_keys()
        return_obj = fas_custom_list()
        if len(IN_arr) <=0:
            pass
        else:
            try:
                key_transactionmonth = keys.transactionmonth
                key_name = keys.name
                key_quarter = keys.quarter
                key_level_id = keys.level_id
                key_expense_id = keys.expense_id
                key_expense_name = keys.expensename
                key_income_amount = keys.income_amount
                expense_data = IN_arr
                yearTeam = request_obj.get_yearterm()
                if yearTeam == "Monthly":
                    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                elif yearTeam == "Quarterly":
                    month = ["Quarterly_1", "Quarterly_2", "Quarterly_3", "Quarterly_4"]
                expenseIDS = []
                for l in expense_data:
                    if l[key_expense_id] not in expenseIDS:
                        expenseIDS.append(l[key_expense_id])

                for k in expenseIDS:
                    expense_row = {}
                    for m in month:
                        expense_row[m]=Decimal(round(Decimal('0.00'), 2))
                    for j in expense_data:
                        if k == j[key_expense_id]:
                            expense_row[key_name] = j[key_expense_name]
                            expense_row[key_level_id] = j[key_level_id]
                            expense_row[key_expense_id]=j[key_expense_id]
                            if yearTeam == "Monthly":
                                if expense_row[month[int(j[key_transactionmonth])-1]] != Decimal(round(Decimal('0.00'), 2)):
                                    expense_row[month[int(j[key_transactionmonth])-1]] = Decimal(expense_row[month[int(j[key_transactionmonth])-1]])+Decimal(
                                            round(Decimal(j[key_income_amount]), 2))
                                else:
                                    expense_row[month[int(j[key_transactionmonth])-1]] = Decimal(
                                            round(Decimal(j[key_income_amount]), 2))
                            elif yearTeam == "Quarterly":
                                if expense_row[f"Quarterly_{j[key_quarter]}"] != Decimal(round(Decimal('0.00'), 2)):
                                    expense_row[f"Quarterly_{j[key_quarter]}"] = Decimal(expense_row[f"Quarterly_{j[key_quarter]}"])+Decimal(
                                            round(Decimal(j[key_income_amount]), 2))
                                else:
                                    expense_row[f"Quarterly_{j[key_quarter]}"] = Decimal(
                                            round(Decimal(j[key_income_amount]), 2))
                    totalsum = Decimal(round(Decimal('0.00'), 2))
                    for sumof_month in month:
                        totalsum = totalsum + expense_row[sumof_month]
                    expense_row['YTD'] = totalsum
                    expense_row['tree_flag'] = 'Y'
                    expense_row[keys.Padding_left] = '100px'
                    expense_row[keys.Padding] = '5px'
                    output.append(expense_row)
            except Exception as e:
                return_obj.set_output(str(e))
                return return_obj.get_dict_return()
        return_obj.set_output(output)
        return return_obj.get_dict_return()


    def fas_cat_fetch(self,request_obj):
        pprutility = MASTER_SERVICE(self._scope())
        condition = Q(status=1,entity_id=self._entity_id())
        groupcondition = ""
        if request_obj.get_level_id() != None and request_obj.get_level_id() != '':
            condition &= Q(level=request_obj.get_level_id())
        if request_obj.get_finyear() != None and request_obj.get_finyear() != '':
            condition &= Q(finyear=request_obj.get_finyear())
        if request_obj.get_bs_code() != None and request_obj.get_bs_code() != '':
            condition &= Q(bs_code=request_obj.get_bs_code())
        if request_obj.get_cc_code() != None and request_obj.get_cc_code() != '':
            condition &= Q(cc_code=request_obj.get_cc_code())
        if request_obj.get_bizname() != None and request_obj.get_bizname() != '':
            condition &= Q(bizname=request_obj.get_bizname())
        if request_obj.get_sectorname() != None and request_obj.get_sectorname() != '':
            condition &= Q(sectorname=request_obj.get_sectorname())
        if request_obj.get_branch_id() != None and request_obj.get_branch_id() != '':
            condition &= Q(apinvoicebranch_id=request_obj.get_branch_id())
        if request_obj.get_yearterm() == "Monthly":
            groupcondition = "transactionmonth"
        if request_obj.get_yearterm() == "Quarterly":
            groupcondition = "quarter"
        if request_obj.get_expense_id() != None and request_obj.get_expense_id() != '':
            condition&=Q(apexpense_id=request_obj.get_expense_id())
        fas_var = Pprdata_maintable.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id','categorygid', 'level',
                                                                                            groupcondition).annotate(
            Income_amount=Sum('amount'))
        fasList = fas_custom_list()
        if len(fas_var) <= 0:
            pass
        else:
            cat_ids = []
            for i in fas_var:
                cat_ids.append(i['categorygid'])
            cat_detials = pprutility.get_cat_data(cat_ids)
            for i in fas_var:
                response = FasResponse()
                response.set_cat_data(cat_detials,i['categorygid'])
                response.set_level_id(i['level'])
                response.set_expense_id(i['apexpense_id'])
                if request_obj.get_yearterm() == "Monthly":
                    response.set_transactionmonth(i[groupcondition])
                if request_obj.get_yearterm() == "Quarterly":
                    response.set_quarter(i[groupcondition])
                response.set_income_amount(Decimal(i['Income_amount'] / request_obj.get_divAmount()))
                fasList.append(response.get())
        return fasList

    def cat_logic(self,IN_arr,request_obj):
        output = []
        keys = Pprutility_keys()
        return_obj = fas_custom_list()
        if len(IN_arr) <=0:
            pass
        else:
            try:
                key_transactionmonth = keys.transactionmonth
                key_name = keys.name
                key_quarter = keys.quarter
                key_level_id = keys.level_id
                key_expense_id = keys.expense_id
                key_cat_id = keys.cat_id
                key_cat_name = keys.cat_name
                key_income_amount = keys.income_amount
                cat_data = IN_arr
                yearTeam = request_obj.get_yearterm()
                if yearTeam == "Monthly":
                    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                elif yearTeam == "Quarterly":
                    month = ["Quarterly_1", "Quarterly_2", "Quarterly_3", "Quarterly_4"]
                catIDS = []
                for l in cat_data:
                    if l[key_cat_id] not in catIDS:
                        catIDS.append(l[key_cat_id])

                for k in catIDS:
                    cat_row = {}
                    for m in month:
                        cat_row[m]=Decimal(round(Decimal('0.00'), 2))
                    for j in cat_data:
                        if k == j[key_cat_id]:
                            cat_row[key_name] = j[key_cat_name]
                            cat_row[key_cat_id]=j[key_cat_id]
                            cat_row[key_level_id] = j[key_level_id]
                            cat_row[key_expense_id]=j[key_expense_id]
                            if yearTeam == "Monthly":
                                if cat_row[month[int(j[key_transactionmonth])-1]] != Decimal(round(Decimal('0.00'), 2)):
                                    cat_row[month[int(j[key_transactionmonth])-1]] = Decimal(cat_row[month[int(j[key_transactionmonth])-1]])+Decimal(
                                            round(Decimal(j[key_income_amount]), 2))
                                else:
                                    cat_row[month[int(j[key_transactionmonth])-1]] = Decimal(
                                            round(Decimal(j[key_income_amount]), 2))
                            elif yearTeam == "Quarterly":
                                if cat_row[f"Quarterly_{j[key_quarter]}"] != Decimal(round(Decimal('0.00'), 2)):
                                    cat_row[f"Quarterly_{j[key_quarter]}"] = Decimal(cat_row[f"Quarterly_{j[key_quarter]}"])+Decimal(
                                            round(Decimal(j[key_income_amount]), 2))
                                else:
                                    cat_row[f"Quarterly_{j[key_quarter]}"] = Decimal(
                                            round(Decimal(j[key_income_amount]), 2))
                    totalsum = Decimal(round(Decimal('0.00'), 2))
                    for sumof_month in month:
                        totalsum = totalsum + cat_row[sumof_month]
                    cat_row['YTD'] = totalsum
                    cat_row['tree_flag'] = 'Y'
                    cat_row[keys.Padding_left] = '150px'
                    cat_row[keys.Padding] = '5px'
                    output.append(cat_row)
            except Exception as e:
                return_obj.set_output(str(e))
                return return_obj.get_dict_return()
        return_obj.set_output(output)
        return return_obj.get_dict_return()


    def fas_subcat_fetch(self,request_obj):
        pprutility = MASTER_SERVICE(self._scope())
        condition = Q(status=1,entity_id=self._entity_id())
        groupcondition = ""
        if request_obj.get_level_id() != None and request_obj.get_level_id() != '':
            condition &= Q(level=request_obj.get_level_id())
        if request_obj.get_finyear() != None and request_obj.get_finyear() != '':
            condition &= Q(finyear=request_obj.get_finyear())
        if request_obj.get_bs_code() != None and request_obj.get_bs_code() != '':
            condition &= Q(bs_code=request_obj.get_bs_code())
        if request_obj.get_cc_code() != None and request_obj.get_cc_code() != '':
            condition &= Q(cc_code=request_obj.get_cc_code())
        if request_obj.get_bizname() != None and request_obj.get_bizname() != '':
            condition &= Q(bizname=request_obj.get_bizname())
        if request_obj.get_sectorname() != None and request_obj.get_sectorname() != '':
            condition &= Q(sectorname=request_obj.get_sectorname())
        if request_obj.get_branch_id() != None and request_obj.get_branch_id() != '':
            condition &= Q(apinvoicebranch_id=request_obj.get_branch_id())
        if request_obj.get_yearterm() == "Monthly":
            groupcondition = "transactionmonth"
        if request_obj.get_yearterm() == "Quarterly":
            groupcondition = "quarter"
        if request_obj.get_expense_id() != None and request_obj.get_expense_id() != '':
            condition &= Q(apexpense_id=request_obj.get_expense_id())
        if request_obj.get_cat_id() != None and request_obj.get_cat_id() != '':
            condition&=Q(categorygid=request_obj.get_cat_id())
        fas_var = Pprdata_maintable.objects.using(self._current_app_schema()).filter(condition).values('apsubcat_id','apexpense_id',
                                                                                            'categorygid', 'level',
                                                                                            groupcondition).annotate(
            Income_amount=Sum('amount'))
        fasList = fas_custom_list()
        if len(fas_var) <= 0:
            pass
        else:
            subcatIDS = []
            for i in fas_var:
                subcatIDS.append(i['apsubcat_id'])
            subcat_detials = pprutility.get_subcat(subcatIDS)
            for i in fas_var:
                response = FasResponse()
                response.set_subcat_data(subcat_detials,i['apsubcat_id'])
                response.set_cat_id(i['categorygid'])
                response.set_level_id(i['level'])
                response.set_expense_id(i['apexpense_id'])
                if request_obj.get_yearterm() == "Monthly":
                    response.set_transactionmonth(i[groupcondition])
                if request_obj.get_yearterm() == "Quarterly":
                    response.set_quarter(i[groupcondition])
                response.set_income_amount(Decimal(i['Income_amount'] / request_obj.get_divAmount()))
                fasList.append(response.get())
        return fasList

    def subcat_logic(self,IN_arr,request_obj):
        output = []
        keys = Pprutility_keys()
        return_obj = fas_custom_list()
        if len(IN_arr) <=0:
            pass
        else:
            try:
                key_transactionmonth = keys.transactionmonth
                key_name = keys.name
                key_quarter = keys.quarter
                key_level_id = keys.level_id
                key_expense_id = keys.expense_id
                key_cat_id = keys.cat_id
                key_subcat_id = keys.subcat_id
                key_subcat_name = keys.subcat_name
                key_income_amount = keys.income_amount
                cat_data = IN_arr
                yearTeam = request_obj.get_yearterm()
                if yearTeam == "Monthly":
                    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                elif yearTeam == "Quarterly":
                    month = ["Quarterly_1", "Quarterly_2", "Quarterly_3", "Quarterly_4"]
                subcatIDS = []
                for l in cat_data:
                    if l[key_subcat_id] not in subcatIDS:
                        subcatIDS.append(l[key_subcat_id])

                for k in subcatIDS:
                    subcat_row = {}
                    for m in month:
                        subcat_row[m]=Decimal(round(Decimal('0.00'), 2))
                    for j in cat_data:
                        if k == j[key_subcat_id]:
                            subcat_row[key_name] = j[key_subcat_name]
                            subcat_row[key_subcat_id] = j[key_subcat_id]
                            subcat_row[key_cat_id]=j[key_cat_id]
                            subcat_row[key_level_id] = j[key_level_id]
                            subcat_row[key_expense_id]=j[key_expense_id]
                            if yearTeam == "Monthly":
                                if subcat_row[month[int(j[key_transactionmonth])-1]] != Decimal(round(Decimal('0.00'), 2)):
                                    subcat_row[month[int(j[key_transactionmonth])-1]] = Decimal(subcat_row[month[int(j[key_transactionmonth])-1]])+Decimal(
                                            round(Decimal(j[key_income_amount]), 2))
                                else:
                                    subcat_row[month[int(j[key_transactionmonth])-1]] = Decimal(
                                            round(Decimal(j[key_income_amount]), 2))
                            elif yearTeam == "Quarterly":
                                if subcat_row[f"Quarterly_{j[key_quarter]}"] != Decimal(round(Decimal('0.00'), 2)):
                                    subcat_row[f"Quarterly_{j[key_quarter]}"] = Decimal(subcat_row[f"Quarterly_{j[key_quarter]}"])+Decimal(
                                            round(Decimal(j[key_income_amount]), 2))
                                else:
                                    subcat_row[f"Quarterly_{j[key_quarter]}"] = Decimal(
                                            round(Decimal(j[key_income_amount]), 2))
                    totalsum = Decimal(round(Decimal('0.00'), 2))
                    for sumof_month in month:
                        totalsum = totalsum + subcat_row[sumof_month]
                    subcat_row['YTD'] = totalsum
                    subcat_row['tree_flag'] = 'Y'
                    subcat_row[keys.Padding_left] = '200px'
                    subcat_row[keys.Padding] = '5px'
                    output.append(subcat_row)
            except Exception as e:
                return_obj.set_output(str(e))
                return return_obj.get_dict_return()
        return_obj.set_output(output)
        return return_obj.get_dict_return()



    def columndata_sum(self, month, output, left_padding):
        keys = Pprutility_keys()
        month.append('YTD')
        columnkeys = month
        overallrow = {}
        overallrow[keys.name] = 'Total :'
        overalltotalsum = Decimal(round(Decimal('0.00'), 2))
        for colmonth in columnkeys:
            for processdata in output:
                if processdata[colmonth] != "" and processdata[colmonth] != None:
                    overalltotalsum = overalltotalsum + processdata[colmonth]
            overallrow[colmonth] = overalltotalsum
            overalltotalsum = Decimal(round(Decimal('0.00'), 2))
        overallrow[keys.Padding_left] = left_padding
        overallrow[keys.Padding] = '10px'
        return overallrow


    def hr_data_create(self,hr_obj,empid):
        bulk_arr = []
        masterservice = MASTER_SERVICE(self._scope())
        userservice = USER_SERVICE(self._scope())
        pprutility = Ppr_utilityservice(self._scope())
        gl_no = []
        branch_code = []
        for i in hr_obj:
            gl_no.append(i['glno'])
            branch_code.append(i['branch_code'])
        subcat_detials = masterservice.get_subcat_glno(gl_no)
        bs_cc_ids = self.get_BS_CC_ID(hr_obj)
        branch_detias = userservice.get_branch_code(branch_code)
        level = 3
        for i in hr_obj:
            date_ = pprutility.get_finyear_quter_transationmonth(str(i['transactiondate'].date()))
            subcat_id = None
            expense_id = None
            cat_id = None
            bs_id = None
            bs_name = None
            cc_id = None
            cc_name = None
            branch_id = None
            for branch in branch_detias:
                if branch.code == i['branch_code']:
                    branch_id=branch.id
            for j in subcat_detials:
                if j['glno'] == i['glno']:
                    subcat_id = j["id"]
                    expense_id = j["expense"]
                    cat_id = j["category"]
            for bs in bs_cc_ids["bs_id"]:
                if bs['code'] == i['bs_code']:
                    bs_id = bs["id"]
                    bs_name=bs['name']
            for cc in bs_cc_ids["cc_id"]:
                if cc['code'] == i['cc_code']:
                    cc_id = cc["id"]
                    cc_name = cc['name']
            fas_val = Pprdata_maintable(
                finyear=date_['finyear'],
                quarter=date_['quater'],
                transactionmonth=date_['transationmonth'],
                transactionyear=date_['year'],
                transactiondate=date_['date'],
                cc_code=cc_id,
                bs_code=bs_id,
                bsname=bs_name,
                ccname=cc_name,
                bizname=i['bizname'],
                sectorname=i['sectorname'],
                amount=i['hr_amount'],
                categorygid=cat_id,
                apsubcat_id=subcat_id,
                apinvoicebranch_id=branch_id,
                apexpense_id=expense_id,
                level=level,
                create_by=empid,
                status=1
            )
            bulk_arr.append(fas_val)
        Pprdata_maintable.objects.bulk_create(bulk_arr)
        suc_obj = Success()
        suc_obj.set_status(successMessage.SUCCESS)
        return suc_obj

    def level_four(self,request_obj):
        masterservice = MASTER_SERVICE(self._scope())
        userservice = USER_SERVICE(self._scope())
        condition = Q(status=1,entity_id=self._entity_id())
        groupcondition = ""
        if request_obj.get_level_id() != None and request_obj.get_level_id() != '':
            condition &= Q(level=request_obj.get_level_id())
        if request_obj.get_finyear() != None and request_obj.get_finyear() != '':
            condition &= Q(finyear=request_obj.get_finyear())
        if request_obj.get_bs_code() != None and request_obj.get_bs_code() != '':
            condition &= Q(bs_code=request_obj.get_bs_code())
        if request_obj.get_cc_code() != None and request_obj.get_cc_code() != '':
            condition &= Q(cc_code=request_obj.get_cc_code())
        if request_obj.get_bizname() != None and request_obj.get_bizname() != '':
            condition &= Q(bizname=request_obj.get_bizname())
        if request_obj.get_sectorname() != None and request_obj.get_sectorname() != '':
            condition &= Q(sectorname=request_obj.get_sectorname())
        if request_obj.get_branch_id() != None and request_obj.get_branch_id() != '':
            condition &= Q(apinvoicebranch_id=request_obj.get_branch_id())
        if request_obj.get_yearterm() == "Monthly":
            groupcondition = "transactionmonth"
        if request_obj.get_yearterm() == "Quarterly":
            groupcondition = "quarter"

        fas_var = Pprdata_maintable.objects.using(self._current_app_schema()).filter(condition).values('bs_code',
                                                                                            'cc_code', 'level',
                                                                                            groupcondition).annotate(
            Income_amount=Sum('amount'))
        fasList = fas_custom_list()
        if len(fas_var) <= 0:
            pass
        else:
            bsIDS = []
            ccIDS = []
            for i in fas_var:
                bsIDS.append(i['bs_code'])
                ccIDS.append(i['cc_code'])
            ccbs_detials = userservice.get_ccbs(bsIDS,ccIDS)
            for i in fas_var:
                response = FasResponse()
                response.set_ccbs_data(i["bs_code"],i["cc_code"],ccbs_detials)
                response.set_bs_code(i["bs_code"])
                response.set_cc_code(i["cc_code"])
                response.set_level_id(i['level'])
                if request_obj.get_yearterm() == "Monthly":
                    response.set_transactionmonth(i[groupcondition])
                if request_obj.get_yearterm() == "Quarterly":
                    response.set_quarter(i[groupcondition])
                response.set_income_amount(Decimal(i['Income_amount'] / request_obj.get_divAmount()))
                fasList.append(response.get())
        return fasList

    def level_four_logic(self,IN_arr,request_obj):
        output = []
        keys = Pprutility_keys()
        return_obj = fas_custom_list()
        if len(IN_arr) <= 0:
            pass
        else:
            try:
                key_transactionmonth = keys.transactionmonth
                key_name = keys.name
                key_quarter = keys.quarter
                key_level_id = keys.level_id
                key_income_amount = keys.income_amount
                key_ccbs_code = keys.ccbs_code
                key_ccbs_name = keys.ccbs_name
                key_bs_id = keys.bs_code
                key_cc_id = keys.cc_code
                level_four_data = IN_arr
                yearTeam = request_obj.get_yearterm()
                if yearTeam == "Monthly":
                    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                elif yearTeam == "Quarterly":
                    month = ["Quarterly_1", "Quarterly_2", "Quarterly_3", "Quarterly_4"]
                ccbs_code = []
                for i in level_four_data:
                    if i[key_ccbs_code] not in ccbs_code:
                        ccbs_code.append(i[key_ccbs_code])

                for k in ccbs_code:
                    ccbs_row = {}
                    for m in month:
                        ccbs_row[m]=Decimal(round(Decimal('0.00'), 2))
                    for j in level_four_data:
                        if k == j[key_ccbs_code]:
                            ccbs_row[key_name] = j[key_ccbs_name]
                            ccbs_row[key_level_id] = j[key_level_id]
                            ccbs_row[key_bs_id] = j[key_bs_id]
                            ccbs_row[key_cc_id] = j[key_cc_id]
                            if yearTeam == "Monthly":
                                if ccbs_row[month[int(j[key_transactionmonth])-1]] != Decimal(round(Decimal('0.00'), 2)):
                                    ccbs_row[month[int(j[key_transactionmonth])-1]] = Decimal(ccbs_row[month[int(j[key_transactionmonth])-1]])+Decimal(
                                            round(Decimal(j[key_income_amount]), 2))
                                else:
                                    ccbs_row[month[int(j[key_transactionmonth])-1]] = Decimal(
                                            round(Decimal(j[key_income_amount]), 2))
                            elif yearTeam == "Quarterly":
                                if ccbs_row[f"Quarterly_{j[key_quarter]}"] != Decimal(round(Decimal('0.00'), 2)):
                                    ccbs_row[f"Quarterly_{j[key_quarter]}"] = Decimal(ccbs_row[f"Quarterly_{j[key_quarter]}"])+Decimal(
                                            round(Decimal(j[key_income_amount]), 2))
                                else:
                                    ccbs_row[f"Quarterly_{j[key_quarter]}"] = Decimal(
                                            round(Decimal(j[key_income_amount]), 2))
                    totalsum = Decimal(round(Decimal('0.00'), 2))
                    for sumof_month in month:
                        totalsum = totalsum + ccbs_row[sumof_month]
                    ccbs_row['YTD'] = totalsum
                    ccbs_row['tree_flag'] = 'N'
                    ccbs_row[keys.Padding_left] = '50px'
                    ccbs_row[keys.Padding] = '5px'
                    output.append(ccbs_row)
                output.append(self.columndata_sum(month, output, '10px'))
            except Exception as e:
                return_obj.set_output(str(e))
                return return_obj.get_dict_return()
        return_obj.set_output(output)
        return return_obj.get_dict_return()


class fas_custom_list:
    data = []

    def __init__(self):
        self.data = []

    def get(self):
        return self.data

    def append(self,append_):
        self.data.append(append_)

    def set_output(self,arr):
        self.data=arr
    def get_dict_return(self):
        return self.__dict__

