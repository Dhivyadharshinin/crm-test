import json
from decimal import Decimal

import requests
from django.db.models import Q, Sum
from masterservice.models import APexpensegroup, APexpense, Apcategory, APsubcategory
from nwisefin import settings
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from pprservice.util.pprutility import MASTER_SERVICE
from pprservice.util.pprutility import Fees_type, Client_flag, Activestatus, Asset_class, USER_SERVICE
val_url = settings.VYSFIN_URL
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessMessage, SuccessStatus
from pprservice.models.pprmodel import Ppr_Expense_Alldata
from pprservice.data.response.nac_expense_response import ppr_expense_response as expense_response
from wisefinapi.internal.queryhandler import QueryHandler
from wisefinapi.internal.tokenhandler import TokenHandler
from nwisefin.settings import SERVER_IP
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinerror import NWisefinError
class Expense_Service(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.PPR_SERVICE)

    def expense_overall_upload(self, payload, employee_id,request):
        token_handler = TokenHandler()
        headers = token_handler.get_token(request)
        token = headers['Authorization']
        ip_addr = SERVER_IP
        _url = ip_addr +"/entryserv/entry_succss_data"
        headers = {"content-type": "application/json", "Authorization": "" + token + ""}
        resp = requests.post(_url,
                             data=json.dumps(payload),
                             headers=headers,
                             verify=False)
        resp = json.loads(resp.text)
        if resp["Message"] == "Found":
            arr = []
            for obj in resp["DATA"]:
                pprexp_obj = Ppr_Expense_Alldata(
                    entity_id=self._entity_id(),
                    transactiondate=obj["transactiondate"],
                    valuedate=obj["valuedate"],
                    apinvoice_id=obj["ap_invoice_id"],
                    apinvoicebranch_id=obj["apinvoicebranch_id"],
                    apinvoicesupplier_id=obj["apinvoicesupplier_id"],
                    apinvoicedetails_id=obj["apinvoicedetails_id"],
                    apsubcat_id=obj["apsubcat_id"],
                    apexpense_id=obj["apexpense_id"],
                    bs_id=obj["bs_id"],
                    cc_id=obj["cc_id"],
                    biz_id=obj["biz_id"],
                    product_id=obj["product_id"],
                    client_id=obj["client_id"],
                    expensegroup_id=obj["expense_group_id"],
                    sector_id=obj["sector_id"],
                    amount=obj["amount"],
                    taxamount=obj['tax_amount'],
                    otheramount=obj['other_amount'],
                    totalamount=obj['totalamount'],
                    categorygid=obj["categorygid"],
                    entry_module=obj["entry_module"],
                    entry_crno=obj["crno"],
                    status=1,
                    create_by=employee_id,
                )
                arr.append(pprexp_obj)
            Ppr_Expense_Alldata.objects.using(self._current_app_schema()).bulk_create(arr)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return success_obj
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.NO_DATA_FOUND)
            return error_obj

    def ppr_expensegrp_list(self, filter_obj):
        masterservice=MASTER_SERVICE(self._scope())
        subcat_expensegrp = masterservice.get_subcat_expense()
        my_list = [foo for foo in subcat_expensegrp]
        condition = Q(status=1)
        condition &= Q(apsubcat_id__in = my_list)
        # subcat_expensegrp = masterservice.get_subcat_expense()
        if filter_obj.get_from_date() != None and filter_obj.get_from_date() != "" and filter_obj.get_to_date() != None and filter_obj.get_to_date() != "":
            condition &= Q(transactiondate__range=[filter_obj.get_from_date(), filter_obj.get_to_date()])
        if filter_obj.get_product_id() != None and filter_obj.get_product_id() != "":
            condition &= Q(product_id=filter_obj.get_product_id())
        if filter_obj.get_client_id() != None and filter_obj.get_client_id() != "":
            condition &= Q(client_id=filter_obj.get_client_id())
        if filter_obj.get_assest_class() != None and filter_obj.get_assest_class() != "" and len(filter_obj.get_assest_class()) != 0:
            condition &= Q(bs_id__in=filter_obj.get_assest_class())
        if filter_obj.get_business_id() != None and filter_obj.get_business_id() != "":
            # if filter_obj.get_business_id() != 4:
            condition &= Q(biz_id=filter_obj.get_business_id())
        filter_var = Ppr_Expense_Alldata.objects.using(self._current_app_schema()).filter(condition).values(
            "bs_id","expensegroup_id").annotate(amount=Sum("amount")).values("expensegroup_id","bs_id","amount")
        prolist = NWisefinList()
        if len(filter_var) == 0:
            pass
        else:
            for data in filter_var:
                ppr_response = expense_response()
                expgrp_dtls=masterservice.get_expense_grp(data['expensegroup_id'])
                # expgrp_dtls = APexpensegroup.objects.using(self._current_app_schema()).filter(
                #     id=data["expensegroup_id"]).values("id", "name")
                for k in expgrp_dtls:
                    ppr_response.set_id(k["id"])
                    ppr_response.set_name(k["name"])
                ppr_response.set_amount(data["amount"])
                # if data["bs_id"] == Asset_class.AGRI:
                #     ppr_response.set_asset_name(Asset_class.AGRI_VAL)
                # elif data["bs_id"] == Asset_class.BD:
                #     ppr_response.set_asset_name(Asset_class.BD_VAL)
                # elif data["bs_id"] == Asset_class.CC:
                #     ppr_response.set_asset_name(Asset_class.CC_VAL)
                # elif data["bs_id"] == Asset_class.CF:
                #     ppr_response.set_asset_name(Asset_class.CF_VAL)
                # elif data["bs_id"] == Asset_class.CL:
                #     ppr_response.set_asset_name(Asset_class.CL_VAL)
                # elif data["bs_id"] == Asset_class.AHF:
                #     ppr_response.set_asset_name(Asset_class.AHF_VAL)
                # elif data["bs_id"] == Asset_class.CONS:
                #     ppr_response.set_asset_name(Asset_class.CONS_VAL)
                # elif data["bs_id"] == Asset_class.CORP:
                #     ppr_response.set_asset_name(Asset_class.CORP_VAL)
                # elif data["bs_id"] == Asset_class.INTER_COMPANY:
                #     ppr_response.set_asset_name(Asset_class.INTER_COMPANY_VAL)
                # elif data["bs_id"] == Asset_class.MFI:
                #     ppr_response.set_asset_name(Asset_class.MFI_VAL)
                # elif data["bs_id"] == Asset_class.OTH:
                #     ppr_response.set_asset_name(Asset_class.OTH_VAL)
                # elif data["bs_id"] == Asset_class.SBL:
                #     ppr_response.set_asset_name(Asset_class.SBL_VAL)
                # elif data["bs_id"] == Asset_class.VF:
                #     ppr_response.set_asset_name(Asset_class.VF_VAL)
                # elif data["bs_id"] == Asset_class.Consumer_Finance:
                #     ppr_response.set_asset_name(Asset_class.Consumer_Finance_VAL)
                # elif data["bs_id"] == Asset_class.Gold_Loans:
                #     ppr_response.set_asset_name(Asset_class.Gold_Loans_VAL)
                # elif data["bs_id"] == Asset_class.CV:
                #     ppr_response.set_asset_name(Asset_class.CV_VAL)
                # elif data["bs_id"] == Asset_class.VL:
                #     ppr_response.set_asset_name(Asset_class.VL_VAL)
                # elif data["bs_id"] == Asset_class.SME:
                #     ppr_response.set_asset_name(Asset_class.SME_VAL)
                user_dtls = masterservice.get_BS_id([data["bs_id"]])
                ppr_response.set_asset_name(user_dtls[0]["name"])
                prolist.append(ppr_response)
        return prolist

    def ppr_expensegrp_logic(self,params_data,pprdata,asset_data):
        pro_list = NWisefinList()
        pprdata = json.loads(pprdata)
        if pprdata["data"] == []:
            return pro_list
        expgrpname = []
        assetname = []
        value = []
        amount_ary=[]
        expensegrp_id=''
        expense_id=''
        cat_id=''
        prolist = NWisefinList()
        row = {}

        for x in pprdata["data"]:
            # ref_id = x["expensegroup_id"]
            if x["name"] not in expgrpname:
                expgrpname.append(x["name"])
            if x["asset_name"] not in assetname:
                assetname.append(x["asset_name"])
            if x["id"] not in value:
                value.append(x["id"])
        if params_data != 1:
            assetname=asset_data
        # assetname.append("Total")
        # value.append(0)
        append_flag=0
        ast_name=''
        for a1,a in zip(expgrpname,value):
            amount_ary = []
            ytd_val=0
            for a2 in assetname:
                asst_amt=0
                ast_name = a2
                flag = False
                for a3 in pprdata["data"]:
                    if a1==a3['name']:
                        if a2==a3['asset_name']:
                            flag=True
                            ytd_val=ytd_val+a3['amount']
                            asst_amt=asst_amt+a3['amount']
                            # amount_ary.append(a3['amount'])
                if flag==False:
                    if ast_name!='Total':
                        amount_ary.append(0.00)
                else:
                    amount_ary.append(asst_amt)
            amount_ary.append(ytd_val)

            if int(params_data)==1:
                if append_flag==0:
                    assetname.append('Total')

                data = {"id":a,"name":a1,"asset_name":assetname,"amount":amount_ary,"expensegrp_id":expensegrp_id}
                append_flag=append_flag+1
                prolist.append(data)

            if int(params_data)==2:
                if append_flag==0:
                    assetname.append('Total')
                if len(pprdata["data"])!=0:
                    expensegrp_id=pprdata["data"][0]['expensegroup_id']
                data = {"id":a,"name":a1,"asset_name":assetname,"amount":amount_ary,"expensegrp_id":expensegrp_id}
                append_flag = append_flag + 1
                prolist.append(data)
            if int(params_data)==3:
                if append_flag==0:
                    assetname.append('Total')
                if len(pprdata["data"])!=0:
                    expensegrp_id=pprdata["data"][0]['expensegroup_id']
                    expense_id=pprdata["data"][0]['apexpense_id']
                data = {"id":a,"name":a1,"asset_name":assetname,"amount":amount_ary,"expensegrp_id":expensegrp_id,"expense_id":expense_id}
                append_flag = append_flag + 1
                prolist.append(data)
            if int(params_data)==4:
                if append_flag==0:
                    assetname.append('Total')
                if len(pprdata["data"])!=0:
                    expensegrp_id=pprdata["data"][0]['expensegroup_id']
                    expense_id=pprdata["data"][0]['apexpense_id']
                    cat_id=pprdata["data"][0]['category_id']
                data = {"id":a,"name":a1,"asset_name":assetname,"amount":amount_ary,"expensegrp_id":expensegrp_id,"expense_id":expense_id,"cat_id":cat_id}
                append_flag = append_flag + 1
                prolist.append(data)
        if int(params_data) == 1:
            total_ary=[]
            aa11=prolist.get()
            aa12=json.loads(aa11)
            for index,assetname_obj, in enumerate(assetname):
                amount_val=0
                for exp_obj in aa12['data']:
                    if assetname_obj==exp_obj['asset_name'][index]:
                        amount_val=amount_val+exp_obj['amount'][index]
                total_ary.append(amount_val)
            data = {"name": "Total","asset_name": assetname, "amount": total_ary,
                    }
            prolist.append(data)
        return prolist

    def ppr_expensehead_list(self, filter_obj):
        masterservice=MASTER_SERVICE(self._scope())
        subcat_expensegrp = masterservice.get_subcat_expense()
        my_list = [foo for foo in subcat_expensegrp]
        condition = Q(status=1,apsubcat_id__in = my_list)
        if filter_obj.get_from_date() != None and filter_obj.get_from_date() != "" and filter_obj.get_to_date() != None and filter_obj.get_to_date() != "":
            condition &= Q(transactiondate__range=[filter_obj.get_from_date(), filter_obj.get_to_date()])
        if filter_obj.get_product_id() != None and filter_obj.get_product_id() != "":
            condition &= Q(product_id=filter_obj.get_product_id())
        if filter_obj.get_client_id() != None and filter_obj.get_client_id() != "":
            condition &= Q(client_id=filter_obj.get_client_id())
        if filter_obj.get_assest_class() != None and filter_obj.get_assest_class() != "" and len(
                filter_obj.get_assest_class()) != 0:
            condition &= Q(bs_id__in=filter_obj.get_assest_class())
        if filter_obj.get_business_id() != None and filter_obj.get_business_id() != "":
            if filter_obj.get_business_id() != 4:
                condition &= Q(biz_id=filter_obj.get_business_id())
        if filter_obj.get_expensegroup_id() != None and filter_obj.get_expensegroup_id() != "":
            condition &= Q(expensegroup_id=filter_obj.get_expensegroup_id())
        filter_var = Ppr_Expense_Alldata.objects.using(self._current_app_schema()).filter(condition).values(
            "bs_id","expensegroup_id","apexpense_id").annotate(amount=Sum("amount")).values("expensegroup_id","apexpense_id","bs_id","amount")
        prolist = NWisefinList()
        if len(filter_var) == 0:
            pass
        else:
            for data in filter_var:
                ppr_response = expense_response()
                ppr_response.set_expensegroup_id(data["expensegroup_id"])
                expgrp_dtls=masterservice.get_expense_head(data["apexpense_id"])
                # expgrp_dtls = APexpense.objects.using(self._current_app_schema()).filter(
                #     id=data["apexpense_id"]).values("id", "head")
                for k in expgrp_dtls:
                    ppr_response.set_id(k["id"])
                    ppr_response.set_name(k["head"])
                ppr_response.set_amount(data["amount"])
                # if data["bs_id"] == Asset_class.AGRI:
                #     ppr_response.set_asset_name(Asset_class.AGRI_VAL)
                # elif data["bs_id"] == Asset_class.BD:
                #     ppr_response.set_asset_name(Asset_class.BD_VAL)
                # elif data["bs_id"] == Asset_class.CC:
                #     ppr_response.set_asset_name(Asset_class.CC_VAL)
                # elif data["bs_id"] == Asset_class.CF:
                #     ppr_response.set_asset_name(Asset_class.CF_VAL)
                # elif data["bs_id"] == Asset_class.CL:
                #     ppr_response.set_asset_name(Asset_class.CL_VAL)
                # elif data["bs_id"] == Asset_class.AHF:
                #     ppr_response.set_asset_name(Asset_class.AHF_VAL)
                # elif data["bs_id"] == Asset_class.CONS:
                #     ppr_response.set_asset_name(Asset_class.CONS_VAL)
                # elif data["bs_id"] == Asset_class.CORP:
                #     ppr_response.set_asset_name(Asset_class.CORP_VAL)
                # elif data["bs_id"] == Asset_class.INTER_COMPANY:
                #     ppr_response.set_asset_name(Asset_class.INTER_COMPANY_VAL)
                # elif data["bs_id"] == Asset_class.MFI:
                #     ppr_response.set_asset_name(Asset_class.MFI_VAL)
                # elif data["bs_id"] == Asset_class.OTH:
                #     ppr_response.set_asset_name(Asset_class.OTH_VAL)
                # elif data["bs_id"] == Asset_class.SBL:
                #     ppr_response.set_asset_name(Asset_class.SBL_VAL)
                # elif data["bs_id"] == Asset_class.VF:
                #     ppr_response.set_asset_name(Asset_class.VF_VAL)
                # elif data["bs_id"] == Asset_class.Consumer_Finance:
                #     ppr_response.set_asset_name(Asset_class.Consumer_Finance_VAL)
                # elif data["bs_id"] == Asset_class.Gold_Loans:
                #     ppr_response.set_asset_name(Asset_class.Gold_Loans_VAL)
                # elif data["bs_id"] == Asset_class.CV:
                #     ppr_response.set_asset_name(Asset_class.CV_VAL)
                # elif data["bs_id"] == Asset_class.VL:
                #     ppr_response.set_asset_name(Asset_class.VL_VAL)
                # elif data["bs_id"] == Asset_class.SME:
                #     ppr_response.set_asset_name(Asset_class.SME_VAL)
                user_dtls = masterservice.get_BS_id([data["bs_id"]])
                ppr_response.set_asset_name(user_dtls[0]["name"])
                prolist.append(ppr_response)
        return prolist

    def ppr_cat_list(self, filter_obj):
        masterservice=MASTER_SERVICE(self._scope())
        subcat_expensegrp = masterservice.get_subcat_expense()
        my_list = [foo for foo in subcat_expensegrp]
        condition = Q(status=1, apsubcat_id__in=my_list)
        # condition = Q(status=1)
        if filter_obj.get_from_date() != None and filter_obj.get_from_date() != "" and filter_obj.get_to_date() != None and filter_obj.get_to_date() != "":
            condition &= Q(transactiondate__range=[filter_obj.get_from_date(), filter_obj.get_to_date()])
        if filter_obj.get_product_id() != None and filter_obj.get_product_id() != "":
            condition &= Q(product_id=filter_obj.get_product_id())
        if filter_obj.get_client_id() != None and filter_obj.get_client_id() != "":
            condition &= Q(client_id=filter_obj.get_client_id())
        if filter_obj.get_assest_class() != None and filter_obj.get_assest_class() != "" and len(
                filter_obj.get_assest_class()) != 0:
            condition &= Q(bs_id__in=filter_obj.get_assest_class())
        if filter_obj.get_business_id() != None and filter_obj.get_business_id() != "":
            if filter_obj.get_business_id() != 4:
                condition &= Q(biz_id=filter_obj.get_business_id())
        if filter_obj.get_expensegroup_id() != None and filter_obj.get_expensegroup_id() != "":
            condition &= Q(expensegroup_id=filter_obj.get_expensegroup_id())
        if filter_obj.get_apexpense_id() != None and filter_obj.get_apexpense_id() != "":
            condition &= Q(apexpense_id=filter_obj.get_apexpense_id())
        filter_var = Ppr_Expense_Alldata.objects.using(self._current_app_schema()).filter(condition).values(
            "bs_id","expensegroup_id","apexpense_id","categorygid").annotate(amount=Sum("amount")).values("expensegroup_id","apexpense_id","categorygid","bs_id","amount")
        prolist = NWisefinList()
        if len(filter_var) == 0:
            pass
        else:
            for data in filter_var:
                ppr_response = expense_response()
                ppr_response.set_expensegroup_id(data["expensegroup_id"])
                ppr_response.set_apexpense_id(data["apexpense_id"])
                cat_dtls = masterservice.get_cat_dtls([data["categorygid"]])
                # cat_dtls = Apcategory.objects.using(self._current_app_schema()).filter(
                #     id=data["categorygid"]).values("id", "name")
                for k in cat_dtls:
                    ppr_response.set_id(k["id"])
                    ppr_response.set_name(k["name"])
                ppr_response.set_amount(data["amount"])
                # if data["bs_id"] == Asset_class.AGRI:
                #     ppr_response.set_asset_name(Asset_class.AGRI_VAL)
                # elif data["bs_id"] == Asset_class.BD:
                #     ppr_response.set_asset_name(Asset_class.BD_VAL)
                # elif data["bs_id"] == Asset_class.CC:
                #     ppr_response.set_asset_name(Asset_class.CC_VAL)
                # elif data["bs_id"] == Asset_class.CF:
                #     ppr_response.set_asset_name(Asset_class.CF_VAL)
                # elif data["bs_id"] == Asset_class.CL:
                #     ppr_response.set_asset_name(Asset_class.CL_VAL)
                # elif data["bs_id"] == Asset_class.AHF:
                #     ppr_response.set_asset_name(Asset_class.AHF_VAL)
                # elif data["bs_id"] == Asset_class.CONS:
                #     ppr_response.set_asset_name(Asset_class.CONS_VAL)
                # elif data["bs_id"] == Asset_class.CORP:
                #     ppr_response.set_asset_name(Asset_class.CORP_VAL)
                # elif data["bs_id"] == Asset_class.INTER_COMPANY:
                #     ppr_response.set_asset_name(Asset_class.INTER_COMPANY_VAL)
                # elif data["bs_id"] == Asset_class.MFI:
                #     ppr_response.set_asset_name(Asset_class.MFI_VAL)
                # elif data["bs_id"] == Asset_class.OTH:
                #     ppr_response.set_asset_name(Asset_class.OTH_VAL)
                # elif data["bs_id"] == Asset_class.SBL:
                #     ppr_response.set_asset_name(Asset_class.SBL_VAL)
                # elif data["bs_id"] == Asset_class.VF:
                #     ppr_response.set_asset_name(Asset_class.VF_VAL)
                # elif data["bs_id"] == Asset_class.Consumer_Finance:
                #     ppr_response.set_asset_name(Asset_class.Consumer_Finance_VAL)
                # elif data["bs_id"] == Asset_class.Gold_Loans:
                #     ppr_response.set_asset_name(Asset_class.Gold_Loans_VAL)
                # elif data["bs_id"] == Asset_class.CV:
                #     ppr_response.set_asset_name(Asset_class.CV_VAL)
                # elif data["bs_id"] == Asset_class.VL:
                #     ppr_response.set_asset_name(Asset_class.VL_VAL)
                # elif data["bs_id"] == Asset_class.SME:
                #     ppr_response.set_asset_name(Asset_class.SME_VAL)
                user_dtls = masterservice.get_BS_id([data["bs_id"]])
                ppr_response.set_asset_name(user_dtls[0]["name"])
                prolist.append(ppr_response)
        return prolist

    def ppr_subcat_list(self, filter_obj):
        masterservice=MASTER_SERVICE(self._scope())
        subcat_expensegrp = masterservice.get_subcat_expense()
        my_list = [foo for foo in subcat_expensegrp]
        condition = Q(status=1, apsubcat_id__in=my_list)
        # condition = Q(status=1)
        if filter_obj.get_from_date() != None and filter_obj.get_from_date() != "" and filter_obj.get_to_date() != None and filter_obj.get_to_date() != "":
            condition &= Q(transactiondate__range=[filter_obj.get_from_date(), filter_obj.get_to_date()])
        if filter_obj.get_product_id() != None and filter_obj.get_product_id() != "":
            condition &= Q(product_id=filter_obj.get_product_id())
        if filter_obj.get_client_id() != None and filter_obj.get_client_id() != "":
            condition &= Q(client_id=filter_obj.get_client_id())
        if filter_obj.get_assest_class() != None and filter_obj.get_assest_class() != "" and len(
                filter_obj.get_assest_class()) != 0:
            condition &= Q(bs_id__in=filter_obj.get_assest_class())
        if filter_obj.get_business_id() != None and filter_obj.get_business_id() != "":
            if filter_obj.get_business_id() != 4:
                condition &= Q(biz_id=filter_obj.get_business_id())
        if filter_obj.get_expensegroup_id() != None and filter_obj.get_expensegroup_id() != "":
            condition &= Q(expensegroup_id=filter_obj.get_expensegroup_id())
        if filter_obj.get_apexpense_id() != None and filter_obj.get_apexpense_id() != "":
            condition &= Q(apexpense_id=filter_obj.get_apexpense_id())
        if filter_obj.get_categorygid() != None and filter_obj.get_categorygid() != "":
            condition &= Q(categorygid=filter_obj.get_categorygid())
        filter_var = Ppr_Expense_Alldata.objects.using(self._current_app_schema()).filter(condition).values(
            "bs_id","expensegroup_id","apexpense_id","categorygid","apsubcat_id").annotate(amount=Sum("amount")).values("expensegroup_id","apexpense_id","categorygid","apsubcat_id","bs_id","amount")
        prolist = NWisefinList()
        if len(filter_var) == 0:
            pass
        else:
            for data in filter_var:
                ppr_response = expense_response()
                ppr_response.set_expensegroup_id(data["expensegroup_id"])
                ppr_response.set_apexpense_id(data["apexpense_id"])
                ppr_response.set_category_id(data["categorygid"])
                subcat_dtls = masterservice.get_cat_subcat([data["apsubcat_id"]])
                # subcat_dtls = APsubcategory.objects.using(self._current_app_schema()).filter(
                #     id=data["apsubcat_id"]).values("id", "name","glno")
                for k in subcat_dtls:
                    ppr_response.set_id(k["subcat_id"])
                    ppr_response.set_name(k["subcat_name"]+" -("+str(k['glno'])+")")
                ppr_response.set_amount(data["amount"])
                # if data["bs_id"] == Asset_class.AGRI:
                #     ppr_response.set_asset_name(Asset_class.AGRI_VAL)
                # elif data["bs_id"] == Asset_class.BD:
                #     ppr_response.set_asset_name(Asset_class.BD_VAL)
                # elif data["bs_id"] == Asset_class.CC:
                #     ppr_response.set_asset_name(Asset_class.CC_VAL)
                # elif data["bs_id"] == Asset_class.CF:
                #     ppr_response.set_asset_name(Asset_class.CF_VAL)
                # elif data["bs_id"] == Asset_class.CL:
                #     ppr_response.set_asset_name(Asset_class.CL_VAL)
                # elif data["bs_id"] == Asset_class.AHF:
                #     ppr_response.set_asset_name(Asset_class.AHF_VAL)
                # elif data["bs_id"] == Asset_class.CONS:
                #     ppr_response.set_asset_name(Asset_class.CONS_VAL)
                # elif data["bs_id"] == Asset_class.CORP:
                #     ppr_response.set_asset_name(Asset_class.CORP_VAL)
                # elif data["bs_id"] == Asset_class.INTER_COMPANY:
                #     ppr_response.set_asset_name(Asset_class.INTER_COMPANY_VAL)
                # elif data["bs_id"] == Asset_class.MFI:
                #     ppr_response.set_asset_name(Asset_class.MFI_VAL)
                # elif data["bs_id"] == Asset_class.OTH:
                #     ppr_response.set_asset_name(Asset_class.OTH_VAL)
                # elif data["bs_id"] == Asset_class.SBL:
                #     ppr_response.set_asset_name(Asset_class.SBL_VAL)
                # elif data["bs_id"] == Asset_class.VF:
                #     ppr_response.set_asset_name(Asset_class.VF_VAL)
                # elif data["bs_id"] == Asset_class.Consumer_Finance:
                #     ppr_response.set_asset_name(Asset_class.Consumer_Finance_VAL)
                # elif data["bs_id"] == Asset_class.Gold_Loans:
                #     ppr_response.set_asset_name(Asset_class.Gold_Loans_VAL)
                # elif data["bs_id"] == Asset_class.CV:
                #     ppr_response.set_asset_name(Asset_class.CV_VAL)
                # elif data["bs_id"] == Asset_class.VL:
                #     ppr_response.set_asset_name(Asset_class.VL_VAL)
                # elif data["bs_id"] == Asset_class.SME:
                #     ppr_response.set_asset_name(Asset_class.SME_VAL)
                user_dtls = masterservice.get_BS_id([data["bs_id"]])
                ppr_response.set_asset_name(user_dtls[0]["name"])
                prolist.append(ppr_response)
        return prolist