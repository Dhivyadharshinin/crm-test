import json
from decimal import Decimal
import requests
from django.db import IntegrityError
from django.db.models import Q
from django.db.models.aggregates import Sum
from nwisefin.settings import SERVER_IP
from pprservice.models import AllocationLevel, Allocation_meta
from pprservice.util.pprutility import MASTER_SERVICE, USER_SERVICE, Ppr_utilityservice
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from datetime import datetime

from wisefinapi.internal.tokenhandler import TokenHandler

now = datetime.now()
from pprservice.data.response.allocationlevelresponse import AllocationLevelResponse,New_AllocationLevelResponse,allocation_response
from pprservice.models.pprmodel import Pprdata_maintable, Ppr_Expense_Alldata, Pprdata


class AllocationLevelService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.PPR_SERVICE)
    def create_allocationlevel(self, allocationlevel_obj, user_id):
        if not allocationlevel_obj.get_id() is None:
            try:
                allocation_update = AllocationLevel.objects.using(self._current_app_schema()).filter(id=allocationlevel_obj.get_id(),entity_id=self._entity_id()).update(
                                name=allocationlevel_obj.get_name(),
                                arrange=allocationlevel_obj.get_arrange(),
                                reportlevel=allocationlevel_obj.get_reportlevel(),
                                updated_date=now,
                                updated_by=user_id)

                allocation_update = AllocationLevel.objects.using(self._current_app_schema()).get(id=allocationlevel_obj.get_id())

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except AllocationLevel.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CATEGORY_ID)
                error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                allocation_update = AllocationLevel.objects.using(self._current_app_schema()).create(
                                                    name=allocationlevel_obj.get_name(),
                                                    arrange=allocationlevel_obj.get_arrange(),
                                                    reportlevel=allocationlevel_obj.get_reportlevel(),
                                                    created_by=user_id,entity_id=self._entity_id())
                code = "AL" + str(allocation_update.id)
                allocation_update.code = code
                allocation_update.save()

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        allocation_data = AllocationLevelResponse()
        allocation_data.set_id(allocation_update.id)
        allocation_data.set_code(allocation_update.code)
        allocation_data.set_name(allocation_update.name)
        allocation_data.set_arrange(allocation_update.arrange)
        allocation_data.set_reportlevel(allocation_update.reportlevel)
        return allocation_data

    def fetch_allocationlevel_list(self,vys_page,query):
        conditions = Q(status=1,entity_id=self._entity_id())
        if query is not None:
            conditions &= Q(name__icontains=query)
        cost_obj = AllocationLevel.objects.using(self._current_app_schema()).filter(conditions).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(cost_obj)
        cost_list_data = NWisefinList()
        if list_length >= 0:
            for catobj in cost_obj:
                cost_data = AllocationLevelResponse()
                cost_data.set_id(catobj.id)
                cost_data.set_code(catobj.code)
                cost_data.set_name(catobj.name)
                cost_data.set_arrange(catobj.arrange)
                cost_data.set_reportlevel(catobj.reportlevel)
                cost_list_data.append(cost_data)
                vpage = NWisefinPaginator(cost_obj, vys_page.get_index(), 10)
                cost_list_data.set_pagination(vpage)
        return cost_list_data

    def fetch_allocationlevel(self, allocation_id,user_id):
        try:
            cost_var = AllocationLevel.objects.using(self._current_app_schema()).get(id=allocation_id,entity_id=self._entity_id())
            cost_data = AllocationLevelResponse()
            cost_data.set_id(cost_var.id)
            cost_data.set_code(cost_var.code)
            cost_data.set_name(cost_var.name)
            cost_data.set_arrange(cost_var.arrange)
            cost_data.set_reportlevel(cost_var.reportlevel)
            return cost_data
        except AllocationLevel.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_BANK_ID)
            error_obj.set_description(ErrorDescription.INVALID_BANK_ID)
            return error_obj

    def delete_allocation(self, allocation_id,user_id):
        cost_obj = AllocationLevel.objects.using(self._current_app_schema()).filter(id=allocation_id,entity_id=self._entity_id()).delete()

        if cost_obj[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_BANK_ID)
            error_obj.set_description(ErrorDescription.INVALID_BANK_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def fetch_costdriver_search(self,query,vys_page):
        condition=Q(status=1,entity_id=self._entity_id())
        if query is not None:
            condition &=Q(name__icontains=query)
        cost_obj = AllocationLevel.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        cost_list_data = NWisefinList()
        for catobj in cost_obj:
            cost_data = AllocationLevelResponse()
            cost_data.set_id(catobj.id)
            cost_data.set_code(catobj.code)
            cost_data.set_name(catobj.name)
            cost_data.set_arrange(catobj.arrange)
            cost_data.set_reportlevel(catobj.reportlevel)
            cost_list_data.append(cost_data)
            vpage = NWisefinPaginator(cost_obj, vys_page.get_index(), 10)
            cost_list_data.set_pagination(vpage)
        return cost_list_data

    def fetch_new_allocation_level(self,business_obj):
        masterservice = MASTER_SERVICE(self._scope())
        userservice = USER_SERVICE(self._scope())
        srce_condition = Q(status = 1,entity_id=self._entity_id())
        if business_obj.get_core_bscc() != None and business_obj.get_core_bscc() != "":
            srce_condition &= Q(frombscccode=business_obj.get_core_bscc())
        else:
            srce_condition &= Q(frombscccode = None)
        if business_obj.get_cc_id() != None and business_obj.get_cc_id() != "":
            srce_condition &= Q(cc_id=business_obj.get_cc_id())
        else:
            srce_condition &= Q(cc_id=None)
        if business_obj.get_bs_id() != None and business_obj.get_bs_id() != "":
            srce_condition &= Q(bs_id=business_obj.get_bs_id())
        else:
            srce_condition &= Q(bs_id=None)
        srce_condition &= Q(source_bscc_code = None)
        source_obj = Allocation_meta.objects.using(self._current_app_schema()).filter(srce_condition)
        list_data = NWisefinList()
        total_amount = 0.00
        for source_id in source_obj:
            condition = Q(status=1, entity_id=self._entity_id())
            # if business_obj.get_bscc_id() != None and business_obj.get_bscc_id() != "":
            #     condition &= Q(bscc_code=business_obj.get_bscc_id())
            # else:
            #     condition &= Q(bscc_code = None)
            # if business_obj.get_cc_id() != None and business_obj.get_cc_id() != "":
            #     condition &= Q(cc_id=business_obj.get_cc_id())
            # else:
            #     condition &= Q(cc_id = None)
            # if business_obj.get_bs_id() != None and business_obj.get_bs_id() != "":
            #     condition &= Q(bs_id=business_obj.get_bs_id())
            # else:
            #     condition &= Q(bs_id=None)
            condition &= Q(source_bscc_code=source_id.id)
            condition &= ~Q(cc_id=None)
            condition &= Q(frombscccode=None)
            allocation_obj = Allocation_meta.objects.using(self._current_app_schema()).filter(condition)\
                                        .values("bscc_code","source_bscc_code","ratio","to_amount","cc_id","bs_id","id")
            if len(allocation_obj) == 0:
                condition = Q(status=1, entity_id=self._entity_id())
                condition &= Q(source_bscc_code=source_id.id)
                condition &= Q(cc_id=None)
                condition &= Q(frombscccode=None)
                allocation_obj = Allocation_meta.objects.using(self._current_app_schema()).filter(condition) \
                    .values("bscc_code", "source_bscc_code", "ratio", "to_amount", "cc_id", "bs_id", "id")
                ppr_condition = Q(status=1)
                if business_obj.get_bs_id() != None and business_obj.get_bs_id() != "" \
                        and business_obj.get_cc_id() != None and business_obj.get_cc_id() != ""\
                        and business_obj.get_core_bscc() != None and business_obj.get_core_bscc() != "":
                    ppr_condition &= Q(bs_code=business_obj.get_bs_id())
                    ppr_condition &= Q(cc_code=business_obj.get_cc_id())
                    ppr_condition &= Q(bscc_code=business_obj.get_core_bscc())
                    ppr_condition &= Q(transactionmonth=business_obj.get_tranaction_month())
                    ppr_obj = Pprdata_maintable.objects.using(self._current_app_schema()).filter(
                        ppr_condition).values("bs_code","cc_code","bscc_code").annotate(
                        net_amount=Sum('amount')).values("net_amount")
                if business_obj.get_bs_id() != None and business_obj.get_bs_id() != "" \
                        and business_obj.get_core_bscc() != None and business_obj.get_core_bscc() != ""\
                        and business_obj.get_cc_id() == None or business_obj.get_cc_id() == "":
                    ppr_condition &= Q(bs_code=business_obj.get_bs_id())
                    # ppr_condition &= Q(cc_code=business_obj.get_cc_id())
                    ppr_condition &= Q(bscc_code=business_obj.get_core_bscc())
                    ppr_condition &= Q(transactionmonth=business_obj.get_tranaction_month())
                    ppr_obj = Pprdata_maintable.objects.using(self._current_app_schema()).filter(
                        ppr_condition).values("bs_code","bscc_code").annotate(
                        net_amount=Sum('amount')).values("net_amount")
                # if business_obj.get_cc_id() != None and business_obj.get_cc_id() != "":
                #     ppr_condition &= Q(cc_code=business_obj.get_cc_id())
                # if business_obj.get_core_bscc() != None and business_obj.get_core_bscc() != "":
                #     ppr_condition &= Q(bscc_code=business_obj.get_core_bscc())
                # if business_obj.get_tranaction_month() != None and business_obj.get_tranaction_month() != "":
                #     ppr_condition &= Q(transactionmonth=business_obj.get_tranaction_month())
                # ppr_obj = Pprdata_maintable.objects.using(self._current_app_schema()).filter(ppr_condition).annotate(
                #     net_amount=Sum('amount')).values("net_amount")
                if len(ppr_obj) != 0:
                    total_amount = 0.00
                    for obj1 in ppr_obj:
                        total_amount = total_amount + float(obj1["net_amount"])
                else:
                    masterservice = MASTER_SERVICE(self._scope())
                    subcat_expensegrp = masterservice.get_subcat_expense()
                    my_list = [foo for foo in subcat_expensegrp]
                    xp_condition = Q(status=1, apsubcat_id__in=my_list)
                    if business_obj.get_bs_id() != None and business_obj.get_bs_id() != "" \
                            and business_obj.get_cc_id() != None and business_obj.get_cc_id() != "" \
                            and business_obj.get_core_bscc() != None and business_obj.get_core_bscc() != "":
                        xp_condition &= Q(bs_id=business_obj.get_bs_id())
                        xp_condition &= Q(cc_id=business_obj.get_cc_id())
                        xp_condition &= Q(biz_id=business_obj.get_core_bscc())
                        xp_condition &= Q(transactiondate__month=business_obj.get_tranaction_month())
                        exp_obj = Ppr_Expense_Alldata.objects.using(self._current_app_schema()).filter(
                            xp_condition).values("bs_id","cc_id","biz_id").annotate(net_amount=Sum('amount')).values("net_amount")
                    if business_obj.get_bs_id() != None and business_obj.get_bs_id() != "" \
                            and business_obj.get_core_bscc() != None and business_obj.get_core_bscc() != "" \
                            and business_obj.get_cc_id() == None or business_obj.get_cc_id() == "":
                        xp_condition &= Q(bs_id=business_obj.get_bs_id())
                        # xp_condition &= Q(cc_id=business_obj.get_cc_id())
                        xp_condition &= Q(biz_id=business_obj.get_core_bscc())
                        xp_condition &= Q(transactiondate__month=business_obj.get_tranaction_month())
                        exp_obj = Ppr_Expense_Alldata.objects.using(self._current_app_schema()).filter(
                            xp_condition).values("bs_id","biz_id").annotate(net_amount=Sum('amount')).values("net_amount")
                    # if business_obj.get_bs_id() != None and business_obj.get_bs_id() != "":
                    #     xp_condition &= Q(bs_id=business_obj.get_bs_id())
                    # if business_obj.get_cc_id() != None and business_obj.get_cc_id() != "":
                    #     xp_condition &= Q(cc_id=business_obj.get_cc_id())
                    # if business_obj.get_core_bscc() != None and business_obj.get_core_bscc() != "":
                    #     xp_condition &= Q(biz_id=business_obj.get_core_bscc())
                    # if business_obj.get_tranaction_month() != None and business_obj.get_tranaction_month() != "":
                    #     xp_condition &= Q(transactiondate__month=business_obj.get_tranaction_month())
                    # exp_obj = Ppr_Expense_Alldata.objects.using(self._current_app_schema()).filter(
                    #     xp_condition).annotate(net_amount=Sum('amount')).values("net_amount")
                    if len(exp_obj) != 0:
                        total_amount = 0.00
                        for obj2 in exp_obj:
                            total_amount = total_amount + obj2["net_amount"]
                from_bscc = []
                to_bscc = []
                bs_id = []
                cc_id = []
                for x in allocation_obj:
                    from_bscc.append(x['id'])
                    to_bscc.append(x['bscc_code'])
                    cc_id.append(x["cc_id"])
                    bs_id.append(x["bs_id"])
                from_bscc_data = masterservice.get_mstbissegment(from_bscc)
                to_bscc_data = masterservice.get_mstbissegment(to_bscc)
                cc_data = masterservice.get_BS_id(cc_id)
                bs_data = masterservice.get_CC_id(bs_id)
                for obj in allocation_obj:
                    cost_responser = New_AllocationLevelResponse()
                    cost_responser.set_coreccbbs_data(obj["id"], from_bscc_data)
                    cost_responser.set_toccbbs_data(obj["bscc_code"], to_bscc_data)
                    cost_responser.set_cc_data(obj["cc_id"], cc_data)
                    cost_responser.set_bs_data(obj["bs_id"], bs_data)
                    cost_responser.set_ratio(str(obj["ratio"]))
                    total_n = Decimal(total_amount)
                    net_ratio = obj["ratio"]
                    avg_var = (net_ratio * total_n) / 100
                    cost_responser.set_average(float(avg_var))
                    cost_responser.set_final_total(float(total_n))
                    # cost_responser.set_transaction_month(obj1["transactionmonth"])
                    list_data.append(cost_responser)
            else:
                total_amount = 0.00
                ppr_condition = Q(status=1)
                if business_obj.get_bs_id() != None and business_obj.get_bs_id() != "":
                    ppr_condition &= Q(bs_code=business_obj.get_bs_id())
                if business_obj.get_cc_id() != None and business_obj.get_cc_id() != "":
                    ppr_condition &= Q(cc_code=business_obj.get_cc_id())
                if business_obj.get_core_bscc() != None and business_obj.get_core_bscc() != "":
                    ppr_condition &= Q(bscc_code=business_obj.get_core_bscc())
                if business_obj.get_tranaction_month() != None and business_obj.get_tranaction_month() != "":
                    ppr_condition &=  Q(transactionmonth = business_obj.get_tranaction_month())
                ppr_obj = Pprdata_maintable.objects.using(self._current_app_schema()).filter(ppr_condition).annotate(net_amount=Sum('amount')).values("net_amount")
                if len(ppr_obj) != 0:
                    total_amount = 0.00
                    for obj1 in ppr_obj:
                        total_amount = total_amount + float(obj1["net_amount"])
                else:
                    masterservice = MASTER_SERVICE(self._scope())
                    subcat_expensegrp = masterservice.get_subcat_expense()
                    my_list = [foo for foo in subcat_expensegrp]
                    xp_condition = Q(status=1,apsubcat_id__in=my_list)
                    if business_obj.get_bs_id() != None and business_obj.get_bs_id() != "":
                        xp_condition &= Q(bs_id=business_obj.get_bs_id())
                    if business_obj.get_cc_id() != None and business_obj.get_cc_id() != "":
                        xp_condition &= Q(cc_id=business_obj.get_cc_id())
                    if business_obj.get_core_bscc() != None and business_obj.get_core_bscc() != "":
                        xp_condition &= Q(biz_id=business_obj.get_core_bscc())
                    if business_obj.get_tranaction_month() != None and business_obj.get_tranaction_month() != "":
                        xp_condition &= Q(transactiondate__month=business_obj.get_tranaction_month())
                    exp_obj = Ppr_Expense_Alldata.objects.using(self._current_app_schema()).filter(xp_condition).annotate(net_amount=Sum('amount')).values("net_amount")
                    if len(exp_obj) != 0:
                        total_amount = 0.00
                        for obj2 in exp_obj:
                                total_amount = total_amount+obj2["net_amount"]
                from_bscc = []
                to_bscc = []
                bs_id = []
                cc_id = []
                for x in allocation_obj:
                    from_bscc.append(x['id'])
                    to_bscc.append(x['bscc_code'])
                    cc_id.append(x["cc_id"])
                    bs_id.append(x["bs_id"])
                from_bscc_data = masterservice.get_mstbissegment(from_bscc)
                to_bscc_data = masterservice.get_mstbissegment(to_bscc)
                cc_data = masterservice.get_BS_id(cc_id)
                bs_data = masterservice.get_CC_id(bs_id)
                for obj in allocation_obj:
                    cost_responser = New_AllocationLevelResponse()
                    cost_responser.set_coreccbbs_data(obj["id"],from_bscc_data)
                    cost_responser.set_toccbbs_data(obj["bscc_code"],to_bscc_data)
                    cost_responser.set_cc_data(obj["cc_id"],cc_data)
                    cost_responser.set_bs_data(obj["bs_id"],bs_data)
                    cost_responser.set_ratio(str(obj["ratio"]))
                    total_n = Decimal(total_amount)
                    net_ratio = obj["ratio"]
                    avg_var = (net_ratio*total_n)/100
                    cost_responser.set_average(float(avg_var))
                    cost_responser.set_final_total(float(total_n))
                    # cost_responser.set_transaction_month(obj1["transactionmonth"])
                    list_data.append(cost_responser)
        return list_data

    def allocation_ppr_create(self, filterobj, employee_id, request, load_data):
        token_handler = TokenHandler()
        headers = token_handler.get_token(request)
        token = headers['Authorization']
        ip_addr = SERVER_IP
        _url = ip_addr + "/pprservice/new_allocation_list"
        headers = {"content-type": "application/json", "Authorization": "" + token + ""}
        resp = requests.post(_url,
                             data=json.dumps(load_data),
                             headers=headers,
                             verify=False)
        resp = json.loads(resp.text)
        if len(resp["data"]) == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.NO_DATA_FOUND)
            return error_obj
        else:
            t1 = 0.00
            for i in resp["data"]:
                t1 = t1 + float(i["average"])
            t2_amount = t1 - float(i["final_total"])
            check_allocobj = Pprdata_maintable.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id(),
                bscc_code=filterobj.get_core_bscc(),
                cc_code=filterobj.get_cc_id(),
                bs_code=filterobj.get_bs_id(),
                source_bscc_code=None)
            if len(check_allocobj) != 0:
                for id in check_allocobj:
                    child_allocobj = Pprdata_maintable.objects.using(self._current_app_schema()).filter(
                                                    entity_id=self._entity_id(),
                                                    bscc_code=filterobj.get_core_bscc(),
                                                    cc_code=filterobj.get_cc_id(),
                                                    bs_code=filterobj.get_bs_id(),
                                                    source_bscc_code=id.id)
                    tot_amount = 0.00
                    for data in child_allocobj:
                        total = tot_amount+data[data.amount]
                    final_amount = total-id.amount
                for id in check_allocobj:
                    ppr_allocobj = Pprdata_maintable.objects.using(self._current_app_schema()).filter(id=id.id) \
                        .update(amount=int(final_amount),
                        # .update(amount=int(t2_amount),
                                updated_by=employee_id,
                                updated_date=datetime.now())
                    ppr_allocobj = Pprdata_maintable.objects.using(self._current_app_schema()).get(id=id.id)
            else:
                for i in resp["data"]:
                    t3_amount = i["final_total"]
                ppr_allocobj = Pprdata_maintable.objects.using(self._current_app_schema()).create(
                    entity_id=self._entity_id(),
                    bscc_code=filterobj.get_core_bscc(),
                    cc_code=filterobj.get_cc_id(),
                    bs_code=filterobj.get_bs_id(),
                    amount = int(t3_amount),
                    # amount=int(t2_amount),
                    frombscccode=1,
                    transactiondate=datetime.now(),
                    level=filterobj.get_level_id(),
                    create_by=employee_id,
                    status=1)
        id_created = ppr_allocobj.id
        arr = []
        for data in resp["data"]:
            if data["cc_data"] != []:
                cc_data = data["cc_data"]["id"]
            else:
                cc_data = None
            if data["bs_data"] != []:
                bs_data = data["bs_data"]["id"]
            else:
                bs_data = None
            if data["bs_data"] != []:
                bs_name = data["bs_data"]["name"]
            else:
                bs_name = 0
            if data["cc_data"] != []:
                cc_name = data["cc_data"]["name"]
            else:
                cc_name = 0
            if data["toccbs_data"] != []:
                ccbs_data = data["toccbs_data"]["id"]
            else:
                ccbs_data = None
            ppr_allocobj = Pprdata_maintable(
                entity_id=self._entity_id(),
                bscc_code=ccbs_data,
                cc_code=cc_data,
                bs_code=bs_data,
                bsname=bs_name,
                ccname=cc_name,
                amount=data["average"],
                transactiondate=datetime.now(),
                source_bscc_code=id_created,
                create_by=employee_id,
                created_date=datetime.now(),
                level=filterobj.get_level_id(),
                status=1
            )
            arr.append(ppr_allocobj)
        Pprdata_maintable.objects.using(self._current_app_schema()).bulk_create(arr)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def get_core_level(self, filter_obj, vys_page):
        masterservice = MASTER_SERVICE(self._scope())
        userservice = USER_SERVICE(self._scope())
        prolist = NWisefinList()
        condition = Q(status=1)
        if filter_obj.get_core_bscc() != None and filter_obj.get_core_bscc() != "":
            condition &= Q(bscc_code=filter_obj.get_core_bscc())
        if filter_obj.get_bs_id() != None and filter_obj.get_bs_id() != "":
            condition &= Q(bs_code=filter_obj.get_bs_id())
        if filter_obj.get_cc_id() != None and filter_obj.get_cc_id() != "":
            condition &= Q(cc_code=filter_obj.get_cc_id())
        if filter_obj.get_level() != None and filter_obj.get_level() != "":
            condition &= Q(level=filter_obj.get_level())
        condition &= Q(source_bscc_code=None)
        from_obj = Pprdata_maintable.objects.using(self._current_app_schema()).filter(condition)
        allocation_arr = []
        bs_id = []
        cc_id = []
        bscc_id = []
        vlist = NWisefinList()
        if len(from_obj) == 0:
            # error_obj = NWisefinError()
            # error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            # error_obj.set_description(ErrorDescription.NO_DATA_FOUND)
            return vlist
        else:
            for i in from_obj:
                allocation_arr.append(i.id)
                bscc_id.append((i.bscc_code))
                bs_id.append(i.bs_code)
                cc_id.append(i.cc_code)
            bsccdata1 = masterservice.get_mstsegment_id(bscc_id)
            # bscc_value.append(bsccdata1)
            bsdata1 = masterservice.get_BS_id(bs_id)
            # bs_value.append(bsdata1)
            ccdata1 = masterservice.get_CC_id(cc_id)
            # cc_value.append(ccdata1)

            To_allocation_data = Pprdata_maintable.objects.using(self._current_app_schema()).filter(
                source_bscc_code__in=allocation_arr,
                entity_id=self._entity_id())
            bscc = []
            bscc_val = []
            cc_id = []
            cc_val = []
            bs = []
            bs_val = []
            # for k in To_allocation_data:
            #     cc_id.append(k.cc_code)
            #     bs_id.append(k.bs_code)
            #     bscc.append(k.bscc_code)
            #     bsccdata2 = masterservice.get_mstsegment(bscc)
            #     bscc_val.append(bsccdata2)
            #     bs_data2 = userservice.get_BS(bs_id)
            #     bs_val.append(bs_data2)
            #     cc_data2 = userservice.get_CC(cc_id)
            #     cc_val.append(cc_data2)

            for i in from_obj:
                to_response_arr = []
                from_response = allocation_response()
                from_response.set_id(i.id)
                # from_response.set_validity_from(i.validity_from)
                # from_response.set_validity_to(i.validity_to)
                if i.bscc_code != None:
                    from_response.set_bscc(int(i.bscc_code), bsccdata1)
                else:
                    from_response.bscc_data = []
                if i.cc_code != None:
                    from_response.set_cc(int(i.cc_code), ccdata1)
                else:
                    from_response.cc_data = []
                if i.bs_code != None:
                    from_response.set_bs(int(i.bs_code), bsdata1)
                else:
                    from_response.bs_data = []
                from_response.set_amount(str(i.amount))
                if len(To_allocation_data) != 0:
                    for j in To_allocation_data:
                        if j.source_bscc_code == i.id:
                            cc_id.append(j.cc_code)
                            bs.append(j.bs_code)
                            bscc.append(j.bscc_code)
                            bsccdata2 = masterservice.get_mstsegment_id(bscc)
                            bscc_val.append(bsccdata2)
                            bs_data2 = masterservice.get_BS_id(bs)
                            bs_val.append(bs_data2)
                            cc_data2 = masterservice.get_CC_id(cc_id)
                            cc_val.append(cc_data2)
                            # cc_id.append(j.cc_code)
                            # bs_id.append(j.bs_code)
                            # bscc_id.append(j.bscc_code)
                            # bsccdata1 = masterservice.get_mstsegment(bscc_id)
                            # bs_data1 = userservice.get_BS(bs_id)
                            #
                            # cc_data1 = userservice.get_CC(cc_id)

                            # bsccdata1 = masterservice.get_mstsegment([j.bscc_code])
                            # BS = userservice.get_BS(bs_id)
                            # CC = userservice.get_CC(cc_id)
                            to_response = allocation_response()
                            to_response.set_id(j.id)
                            if j.bscc_code != None:
                                to_response.set_bscc(j.bscc_code, bsccdata2)
                            else:
                                to_response.bscc_data = []
                            if j.cc_code != None:
                                to_response.set_cc(int(j.cc_code), cc_data2)
                            else:
                                to_response.cc_data = []
                            if j.bs_code != None:
                                to_response.set_bs(int(j.bs_code), bs_data2)
                            else:
                                to_response.bs_data = []
                            to_response.amount = str(j.amount)
                            to_response_arr.append(to_response)
                            from_response.set_to_data(to_response_arr)
                else:
                    from_response.set_to_data(to_response_arr)
                vlist.data.append(from_response)
                vpage = NWisefinPaginator(from_obj, vys_page.get_index(), 10)
                vlist.set_pagination(vpage)
            return vlist

    def get_corelevel_logic(self,allocbj):
        vlist = NWisefinList()
        pprdata = json.loads(allocbj)
        if pprdata["data"] == []:
            error_obj = NWisefinError()
            # error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            # error_obj.set_description(ErrorDescription.NO_DATA_FOUND)
            return vlist
        prolist = NWisefinList()
        bscc_data = []
        from_bscc_data = []
        amount = []
        for data in pprdata["data"]:

            # if data["bscc_data"] != []:
            #     from_bscc_data.append(data["bscc_data"]["name"])
            if data["bs_data"] != []:
                from_bscc_data.append(data["bs_data"]["name"])
            elif data["cc_data"] != []:
                from_bscc_data.append(data["cc_data"]["name"])
            # amount.append(data["amount"])
            for data1 in data["to_data"]:
                # if data1["bscc_data"] != []:
                #     bscc_data.append(data1["bscc_data"]["name"]+" -("+str(data["bs_data"]["name"])+")")
                if data1["bs_data"] != []:
                    bscc_data.append(data1["bs_data"]["name"])
                elif data1["cc_data"] != []:
                    bscc_data.append(data1["cc_data"]["name"])
                amount.append(data1["amount"])
            row = {"name":from_bscc_data,"value":bscc_data,"amount":amount}
            prolist.append(row)
        return prolist

    def ppr_mstbusinesssegement(self, query, vys_page):  #
        masterservice = MASTER_SERVICE(self._scope())
        pro_list = masterservice.ppr_mstbusinesssegement(query, vys_page)
        return pro_list

    def ppr_businesssegement(self, query, vys_page):  #
        emp_service = MASTER_SERVICE(self._scope())
        pro_list = emp_service.businesssegement(query, vys_page)
        return pro_list

    def ppr_cc(self, query, vys_page):
        emp_service = MASTER_SERVICE(self._scope())
        pro_list = emp_service.cc(query, vys_page)
        return pro_list

    def insert_allocation(self, request_obj, empid):
        allometa_obj_from = Allocation_meta.objects.create(level=request_obj.get_level(),
                                                           frombscccode=request_obj.get_frombscccode(),
                                                           bscc_code=request_obj.get_bscc_code(),
                                                           bs_id=request_obj.get_bs_id(),
                                                           cc_id=request_obj.get_cc_id(),
                                                           cost_driver=request_obj.get_cost_driver(),
                                                           allocation_amount=request_obj.get_allocation_amount(),
                                                           ratio=request_obj.get_ratio(),
                                                           to_amount=request_obj.get_to_amount(),
                                                           validity_from=request_obj.get_validity_from(),
                                                           validity_to=request_obj.get_validity_to(),
                                                           created_by=empid,
                                                           created_date=datetime.now(),
                                                           entity_id=self._entity_id()
                                                           )
        return allometa_obj_from

    def edit_allocationfrom(self, request_obj, empid):
        if request_obj.get_id() is not None:
            allometa_obj_from = Allocation_meta.objects.using(self._current_app_schema()).filter(
                id=request_obj.get_id(), entity_id=self._entity_id()).update(
                frombscccode=request_obj.get_frombscccode(),
                bs_id=request_obj.get_bs_id(),
                cc_id=request_obj.get_cc_id(),
                validity_from=request_obj.get_validity_from(),
                validity_to=request_obj.get_validity_to(),
                updated_by=empid, updated_date=datetime.now())

            return allometa_obj_from

    def to_allocation_create(self, from_obj, request_obj, empid):
        allocation_array = []

        for i in from_obj.get_to_data():
            allometa_obj_to = Allocation_meta(
                source_bscc_code_id=request_obj.id,
                bscc_code=i.get_bscc_code(),
                cc_id=i.get_cc_id(),
                bs_id=i.get_bs_id(),
                ratio=i.get_ratio(),
                created_by=empid, entity_id=self._entity_id())

            allocation_array.append(allometa_obj_to)
        Allocation_meta.objects.using(self._current_app_schema()).bulk_create(allocation_array)
        error_obj = NWisefinError()
        error_obj.set_code = 'success'
        error_obj.set_description = 'success'
        return error_obj

    def edit_allocationto(self, request_obj, empid):
        for i in request_obj.get_to_data():
            if i.get_id() is not None:
                allocation = Allocation_meta.objects.using(self._current_app_schema()).filter(id=i.get_id()).update(
                    source_bscc_code_id=request_obj.id,
                    bscc_code=i.get_bscc_code(),
                    cc_id=i.get_cc_id(),
                    bs_id=i.get_bs_id(),
                    ratio=i.get_ratio(),
                    updated_by=empid,
                    updated_date=datetime.now(),
                    entity_id=self._entity_id())
            else:
                allocation = Allocation_meta.objects.using(self._current_app_schema()).create(
                    source_bscc_code_id=request_obj.id,
                    bscc_code=i.get_bscc_code(),
                    cc_id=i.get_cc_id(),
                    bs_id=i.get_bs_id(),
                    ratio=i.get_ratio(),
                    created_by=empid, entity_id=self._entity_id())

        error_obj = NWisefinError()
        error_obj.set_code = 'success'
        error_obj.set_description = 'success'
        return error_obj

    def fetch_allocation(self, id, user_id):
        arr = []
        try:
            from_vari = Allocation_meta.objects.using(self._current_app_schema()).get(id=id,
                                                                                      entity_id=self._entity_id())
            from_vari = Allocation_meta.objects.using(self._current_app_schema()).filter(source_bscc_code=id)
            allocation = MASTER_SERVICE(self._scope())
            allocation_user = USER_SERVICE(self._scope())
            for i in from_vari:
                allocation_var = allocation_response()
                allocation_var.frombscccode = allocation.get_mstsegment([from_vari.frombscccode])
                allocation_var.bs_id = allocation_user.get_BS([i.bs_id])
                allocation_var.cc_id = allocation_user.get_CC([i.cc_id])
                arr.append(allocation_var)

            return arr

        except Allocation_meta.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_BANK_ID)
            error_obj.set_description(ErrorDescription.INVALID_BANK_ID)
            return error_obj

    def fetch_all(self, id, vys_page):
        userservice = USER_SERVICE(self._scope())
        masterservice = MASTER_SERVICE(self._scope())
        condition = Q(entity_id=self._entity_id())
        if id != None:
            condition &= Q(id=id)
        allocation_data = Allocation_meta.objects.using(self._current_app_schema()).filter(condition)[
                          vys_page.get_offset():vys_page.get_query_limit()]
        allocation_arr = []
        bs_val = []
        cc_val = []
        frombscc_id = []
        vlist = NWisefinList()
        if len(allocation_data) == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.NO_DATA_FOUND)
            return error_obj
        else:
            for i in allocation_data:
                allocation_arr.append(i.id)
                frombscc_id.append((i.frombscccode))
                bs_val.append(i.bs_id)
                cc_val.append(i.cc_id)
            frombscc = masterservice.get_mstsegment_id(frombscc_id)
            bs = masterservice.get_BS_id(bs_val)
            cc = masterservice.get_CC_id(cc_val)

            To_allocation_data = Allocation_meta.objects.using(self._current_app_schema()).filter(status=1,
                                                                                                  source_bscc_code__in=allocation_arr,
                                                                                                  entity_id=self._entity_id())
            bscc_id = []
            cc_id = []
            bs_id = []
            for k in To_allocation_data:
                cc_id.append(k.cc_id)
                bs_id.append(k.bs_id)
                bscc_id.append(k.bscc_code)
            # frombsccdata=masterservice.get_mstsegment(bscc_id)
            # bs_data = userservice.get_bs(bs_id)
            # cc_data = userservice.get_cc(cc_id)
            for i in allocation_data:
                to_response_arr = []
                from_response = allocation_response()
                from_response.set_id(i.id)
                from_response.set_validity_from(i.validity_from)
                from_response.set_validity_to(i.validity_to)
                if i.frombscccode != None:
                    from_response.set_bscc(int(i.frombscccode), frombscc)
                else:
                    from_response.bscc_data = []
                if i.bs_id != None:
                    from_response.set_bs(int(i.bs_id), bs)
                else:
                    from_response.bs_data = []
                if i.cc_id != None:
                    from_response.set_cc(int(i.cc_id), cc)
                else:
                    from_response.cc_data = []
                # from_response.set_ratio()
                for j in To_allocation_data:
                    if j.source_bscc_code.id == i.id:
                        bsccdata = masterservice.get_mstsegment_id([j.bscc_code])
                        bs_data = masterservice.get_BS_id(bs_id)
                        cc_data = masterservice.get_CC_id(cc_id)
                        to_response = allocation_response()
                        to_response.set_id(j.id)
                        if j.bscc_code != None:
                            to_response.set_bscc(int(j.bscc_code), bsccdata)
                        else:
                            to_response.bscc_data = []
                        if j.cc_id != None:
                            to_response.set_cc(int(j.cc_id), cc_data)
                        else:
                            to_response.cc_data = []
                        if j.bs_id != None:
                            to_response.set_bs(int(j.bs_id), bs_data)
                        else:
                            to_response.bs_data = []
                        to_response.set_ratio(float(j.ratio))
                        to_response_arr.append(to_response)
                from_response.set_to_data(to_response_arr)
                vlist.data.append(from_response)
                vpage = NWisefinPaginator(allocation_data, vys_page.get_index(), 10)
                vlist.set_pagination(vpage)
                return vlist


    def fetch_allocationsearch(self, query, from_date, vys_page, to_date):

        condition = Q(status=1, entity_id=self._entity_id())
        if from_date != None and from_date != "" and to_date != None and to_date != "":
            condition &= Q(validity_from__range=[from_date, to_date])

        category_obj = Allocation_meta.objects.using(self._current_app_schema()).filter(condition)[
                       vys_page.get_offset():vys_page.get_query_limit()]
        cate_list_data = NWisefinList()
        for catobj in category_obj:
            cat_data = USER_SERVICE(self._scope())
            cat_data.get_asset_name(catobj.id)
            vpage = NWisefinPaginator(category_obj, vys_page.get_index(), 10)
            cate_list_data.set_pagination(vpage)
        return cate_list_data

    def total_amount(self, bizname, bs_code, cc_code):
        arr = NWisefinList()
        condition = Q(status=1)
        if bizname != None and bizname != "":
            condition &= Q(bizname=bizname)
            filter_var = Pprdata.objects.using(self._current_app_schema()).filter(condition).values(
                "bizname").annotate(amount=Sum("amount"))
            for i in filter_var:
                pprresponse = allocation_response()
                pprresponse.set_amount(float(i["amount"]))
            # arr.append(pprresponse)
        if bs_code != None and bs_code != "":
            condition &= Q(bs_code=bs_code)
            filter_var = Pprdata.objects.using(self._current_app_schema()).filter(condition).values("bs_code").annotate(
                amount=Sum("amount"))
            for i in filter_var:
                pprresponse = allocation_response()
                pprresponse.set_amount(i["amount"])
        if cc_code != None and cc_code != "":
            condition &= Q(cc_code=cc_code)
            filter_var = Pprdata.objects.using(self._current_app_schema()).filter(condition).values("cc_code").annotate(
                amount=Sum("amount"))
            for i in filter_var:
                pprresponse = allocation_response()
                pprresponse.set_amount(i["amount"])
        if bizname != None and bizname != "" and bs_code != None and bs_code != "":
            condition &= Q(bizname=bizname) & Q(bs_code=bs_code)
            filter_var = Pprdata.objects.using(self._current_app_schema()).filter(condition).values(
                "bizname", "bs_code").annotate(amount=Sum("amount"))
            for i in filter_var:
                pprresponse = allocation_response()
                pprresponse.set_amount(float(i["amount"]))
        if bizname != None and bizname != "" and cc_code != None and cc_code != "":
            condition &= Q(bizname=bizname) & Q(cc_code=cc_code)
            filter_var = Pprdata.objects.using(self._current_app_schema()).filter(condition).values(
                "bizname", "cc_code").annotate(amount=Sum("amount"))
            for i in filter_var:
                pprresponse = allocation_response()
                pprresponse.set_amount(float(i["amount"]))
        if bs_code != None and bs_code != "" and cc_code != None and cc_code != "":
            condition &= Q(bs_code=bs_code) & Q(cc_code=cc_code)
            filter_var = Pprdata.objects.using(self._current_app_schema()).filter(condition).values("bs_id").annotate(
                amount=Sum("amount"))
            for i in filter_var:
                pprresponse = allocation_response()
                pprresponse.set_amount(i["amount"])
        arr.append(pprresponse)
        return arr

    def fetch(self, request,vys_page):
        data = MASTER_SERVICE(self._scope())
        userservice = USER_SERVICE(self._scope())
        val = Ppr_utilityservice(self._scope())
        condition = Q(source_bscc_code=None, entity_id=self._entity_id())
        if 'core_bscc' in request.GET and request.GET.get('core_bscc') != '' and request.GET.get('core_bscc') != None:
            condition &= Q(frombscccode__in=request.GET.get('core_bscc'))
        if 'bs_id' in request.GET and request.GET.get('bs_id') != '' and request.GET.get('bs_id') != None:
            condition &= Q(bs_id=request.GET.get('bs_id'))
        if 'cc_id' in request.GET and request.GET.get('cc_id') != '' and request.GET.get('cc_id') != None:
            condition &= Q(cc_id=request.GET.get('cc_id'))

        category_obj = Allocation_meta.objects.using(self._current_app_schema()).filter(condition)[
                       vys_page.get_offset():vys_page.get_query_limit()]
        cate_list_data = NWisefinList()
        if len(category_obj) == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.NO_DATA_FOUND)
            return error_obj
        else:
            for catobj in category_obj:
                bs_id = []
                cc_id = []
                bs_id.append(catobj.bs_id)
                cc_id.append(catobj.cc_id)
                bs_data = data.get_BS_id(bs_id)
                cc_data = data.get_CC_id(cc_id)
                allocation = allocation_response()
                allocation.set_id(catobj.id)
                # allocation.set_frombscccode(catobj.frombscccode)
                allocation.corebscc = data.get_mstsegment_id([catobj.frombscccode])
                if catobj.cc_id != None:
                    allocation.set_cc(catobj.cc_id, cc_data)
                else:
                    allocation.cc_data = []
                if catobj.bs_id != None:
                    allocation.set_bs(catobj.bs_id, bs_data)
                else:
                    allocation.bs_data = []
                # allocation.set_cc(catobj.cc_id, cc_data)
                # allocation.set_bs(catobj.bs_id, bs_data)
                allocation.ratio = val.get_ratio(catobj.id)
                allocation.set_status(catobj.status)
                allocation.set_validity_from(catobj.validity_from)
                allocation.set_validity_to(catobj.validity_to)
                cate_list_data.append(allocation)
                vpage = NWisefinPaginator(category_obj, vys_page.get_index(), 10)
                cate_list_data.set_pagination(vpage)
        return cate_list_data

    def implement_status(self, query, status, user_id):
        arr = []
        condition = Q(status=1, entity_id=self._entity_id())
        if query != None and query != "" and query != None and query != "":
            condition &= Q(id=query)
            variable = Allocation_meta.objects.using(self._current_app_schema()).filter(condition).update(status=status,
                                                                                                          updated_by=user_id,
                                                                                                          updated_date=datetime.now())
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        return success_obj

    def business_search(self, query, vys_page):
        val = Ppr_utilityservice(self._scope())
        data = MASTER_SERVICE(self._scope())
        userservice = USER_SERVICE(self._scope())
        condition = Q(status=1, entity_id=self._entity_id())
        if query != None and query != "" and query != None and query != "":
            condition &= Q(id__in=query)
        category_obj = Allocation_meta.objects.using(self._current_app_schema()).filter(condition)[
                       vys_page.get_offset():vys_page.get_query_limit()]
        cate_list_data = NWisefinList()
        for catobj in category_obj:
            bs_id = []
            cc_id = []
            bs_id.append(catobj.bs_id)
            cc_id.append(catobj.cc_id)
            bs_data = userservice.get_BS(bs_id)
            cc_data = userservice.get_CC(cc_id)
            cat_data = MASTER_SERVICE(self._scope())
            allocation = allocation_response()
            allocation.set_id(catobj.id)
            # allocation.set_frombscccode(catobj.frombscccode)
            allocation.corebscc = data.get_mstsegment([catobj.frombscccode])
            if catobj.cc_id != None:
                allocation.set_cc(catobj.cc_id, cc_data)
            else:
                allocation.cc_data = []
            if catobj.bs_id != None:
                allocation.set_bs(catobj.bs_id, bs_data)
            else:
                allocation.bs_data = []
            allocation.ratio = val.get_ratio(catobj.id)
            allocation.set_status(catobj.status)
            allocation.set_validity_from(catobj.validity_from)
            allocation.set_validity_to(catobj.validity_to)
            cate_list_data.append(allocation)
            cate_list_data.append(cat_data.get_mstsegment(catobj.id))
            vpage = NWisefinPaginator(category_obj, vys_page.get_index(), 10)
            cate_list_data.set_pagination(vpage)
        return cate_list_data













