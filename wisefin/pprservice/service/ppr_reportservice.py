import io
import json
import datetime
from pprservice.models.pprmodel import Pprdata, PprdataLog, PprdataExpGrpMeta,PPR_files,Budgetdetial
from django.db.models import Count
from django.db.models import Q
from pprservice.data.response.success import Success, successMessage
from userservice.service.employeeservice import EmployeeService
from utilityservice.data.response.nwisefinerror import NWisefinError
from pprservice.data.response.warning import Pprdata_warning
from pprservice.data.response.pprreportresponse import pprresponse
from utilityservice.data.response.nwisefinlist import NWisefinList
from masterservice.models.mastermodels import Apcategory, APexpense, APsubcategory
from pprservice.util.pprutility import Ppr_utilityservice, Pprutility_keys,MASTER_SERVICE,USER_SERVICE,VENDOR_SERVICE
from decimal import Decimal
from nwisefin.settings import logger
from pprservice.data.response.pprreportresponse import PPRlogresonse,PPRecfresponse
from pprservice.data.response.pprfilterresponse import Finyearresponse, PprSupplierresponse, Ppr_MBS_BS_CCresponse
from pprservice.data.request.pprinsertrequest import pprinrequest
from ast import literal_eval


from utilityservice.service.applicationconstants import ApplicationNamespace
from vendorservice.models.vendormodels import SupplierBranch
from userservice.models.usermodels import EmployeeBranch
from userservice.models.usermodels import EmployeeBusinessSegmentMapping,EmployeeBranch
from masterservice.models.mastermodels import MasterBusinessSegment, BusinessSegment, CostCentre
from masterservice.models.mastermodels import APexpensegroup, Apsector
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from django.db.models import Sum
# from pprservice.util.ppr_paginator import NWisefinPaginator
from userservice.controller.authcontroller import get_authtoken
from nwisefin import settings
import requests
import pandas as pd
from pprservice.util.fasDB import DataBase
# from vysfinutility.service.dbutil import DataBase
# from dtpcservice.controller.invoiceheadercontroller import monotoken
from django.http import StreamingHttpResponse
from utilityservice.service.threadlocal import NWisefinThread
import io
import boto3
val_url = settings.VYSFIN_URL



class Pprservice(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.PPR_SERVICE)
    def create_ppr(self, ppr_obj):
        arr = []
        for obj in ppr_obj:
            pprTb_obj = Pprdata(finyear=obj.get_finyear(),
                                quarter=obj.get_quarter(),
                                transactionmonth=obj.get_month(),
                                transactionyear=obj.get_year(),
                                transactiondate=obj.get_trndate(),
                                valuedate=obj.get_valuedate(),
                                apinvoice_id=obj.get_invoiceid(),
                                apinvoicebranch_id=obj.get_branchid(),
                                apinvoicesupplier_id=obj.get_supplierid(),
                                apinvoicedetails_id=obj.get_invoicedetialid(),
                                apsubcat_id=obj.get_subcatid(),
                                apexpense_id=obj.get_expenseid(),
                                cc_code=obj.get_cc_code(),
                                bs_code=obj.get_bs_code(),
                                bsname=obj.get_bsname(),
                                ccname=obj.get_ccname(),
                                bizname=obj.get_bussinessname(),
                                sectorname=obj.get_sectorname(),
                                amount=obj.get_amount(),
                                taxamount=obj.get_taxamount(),
                                otheramount=obj.get_otheramount(),
                                totalamount=obj.get_totalamount(),
                                categorygid=obj.get_cat_id(),
                                ccbsdtl_bs=obj.get_ccbsdtl_bs(),
                                ccbsdtl_cc=obj.get_ccbsdtl_cc(),
                                entry_module=obj.get_entry_module(),
                                entry_crno=obj.get_entry_crno(),
                                status=obj.get_status(),
                                create_by=obj.get_createby(),
                                fas_flag=obj.get_fas_flag(),entity_id=self._entity_id()
                                )
            arr.append(pprTb_obj)
        Pprdata.objects.using(self._current_app_schema()).bulk_create(arr)
        suc_obj = Success()
        suc_obj.set_status(successMessage.SUCCESS)
        return suc_obj

    def create_pprlog(self, ppr_obj):
        try:
            ppr_val = PprdataLog.objects.using(self._current_app_schema()).create(maindata=ppr_obj.get_maindata(),entity_id=self._entity_id(),
                                                range_from=ppr_obj.get_range_from(),
                                                range_to=ppr_obj.get_range_to(),
                                                lastsync_date=ppr_obj.get_current_datetime())
            pprlogres = PPRlogresonse()
            pprlogres.set_id(ppr_val.id)
            pprlogres.set_range_from(ppr_val.range_from)
            pprlogres.set_range_to(ppr_val.range_to)
            return pprlogres
        except Exception as e:
            logger.info(str(e))

    # def pprlog_fromdate(self):
    #     try:
    #         ppr_val = PprdataLog.objects.using(DataBase.fas_db).latest("lastsync_date")
    #         return str(ppr_val.lastsync_date)
    #     except Exception as e:
    #         ppr_val = "0000-00-00 00:00:00"
    #         return ppr_val
    def pprlog_fromdate(self):
        ppr_val = PprdataLog.objects.using(self._current_app_schema()).filter(status=1,entity_id=self._entity_id()).last()
        if ppr_val is None:
            ppr_val = "0000-00-00 00:00:00"
            return ppr_val
        else:
            return str(ppr_val.lastsync_date).replace("+"," ")

    def pprlog_main(self,start_index,end_index):
        ppr_val = PprdataLog.objects.using(self._current_app_schema()).filter(lastsync_date__date=str(datetime.datetime.now().strftime("%Y-%m-%d")),status=1,entity_id=self._entity_id())[start_index:end_index]
        arr = []
        if len(ppr_val) <= 0:
            return arr
        else:
            for i in ppr_val:
                maindata = literal_eval(i.maindata)
                try:
                    created_by = maindata["created_by"]
                    maindata = json.loads(maindata["pprlog_logdata"])
                    maindata = maindata["pprdata"]
                    utility = USER_SERVICE(self._scope())
                    ids = utility.code_id_fields(maindata)
                    for data in maindata:
                        reqData = pprinrequest(data, ids)
                        arr.append(reqData)
                except:
                    pass
            return arr

    def pprlog_check_currentdata_status(self):
        check_val = PprdataLog.objects.using(self._current_app_schema()).filter(lastsync_date__date=str(datetime.datetime.now().strftime("%Y-%m-%d")),entity_id=self._entity_id()).update(status=0)

    def ppr_list(self, ppr_obj):
        pprutility = MASTER_SERVICE(self._scope())
        condition = Q(status=1,entity_id=self._entity_id())  # ,entry_module='AP'
        if ppr_obj.get_branch_id() != None and ppr_obj.get_branch_id() != "":
            condition &= Q(apinvoicebranch_id=ppr_obj.get_branch_id())
        if ppr_obj.get_finyear() != None and ppr_obj.get_finyear() != "":
            condition &= Q(finyear=ppr_obj.get_finyear())
        if ppr_obj.get_sector_name() != None and ppr_obj.get_sector_name() != "":
            condition &= Q(sectorname=ppr_obj.get_sector_name())
        if ppr_obj.get_mstbusiness_segment_name() != None and ppr_obj.get_mstbusiness_segment_name() != "":
            condition &= Q(bizname=ppr_obj.get_mstbusiness_segment_name())
        if ppr_obj.get_bs_name() != None and ppr_obj.get_bs_name() != "":
            condition &= Q(bsname=ppr_obj.get_bs_name())
        if ppr_obj.get_cc_name() != None and ppr_obj.get_cc_name() != "":
            condition &= Q(ccname=ppr_obj.get_cc_name())
        if ppr_obj.get_expensegrp_name_arr() != None and ppr_obj.get_expensegrp_name_arr() != "" and len(
                ppr_obj.get_expensegrp_name_arr()) > 0:
            expense_id = pprutility.get_expense_expensegrp(ppr_obj.get_expensegrp_name_arr())
            condition &= Q(apexpense_id__in=expense_id)
        pprTb_obj = Pprdata.objects.using(self._current_app_schema()).filter(condition)
        subcat_arr = []
        expense_arr = []
        for arr_id in pprTb_obj:
            subcat_arr.append(arr_id.apsubcat_id)
            expense_arr.append(arr_id.apexpense_id)
        subcat_cat_data = pprutility.get_subcat(subcat_arr)
        expense_data = pprutility.get_expense(expense_arr)
        pro_list = NWisefinList()
        for i in pprTb_obj:
            pprresponser = pprresponse()
            pprresponser.set_finyear(i.finyear)
            pprresponser.set_quarter(i.quarter)
            pprresponser.set_transactionmonth(i.transactionmonth)
            pprresponser.set_transactionyear(i.transactionyear)
            pprresponser.set_transactiondate(str(i.transactiondate))
            pprresponser.set_valuedate(str(i.valuedate))
            pprresponser.set_apinvoiceid(i.apinvoice_id)
            pprresponser.set_apinvoicebranchid(i.apinvoicebranch_id)
            pprresponser.set_apinvoicesupplierid(i.apinvoicesupplier_id)
            pprresponser.set_apinvoicedetailsid(i.apinvoicedetails_id)
            pprresponser.set_bscode(i.bs_code)
            pprresponser.set_cccode(i.cc_code)
            pprresponser.set_bsname(i.bsname)
            pprresponser.set_ccname(i.ccname)
            pprresponser.set_bizname(i.bizname)
            pprresponser.set_sectorname(i.sectorname)
            pprresponser.set_amount(str(Decimal(i.amount) / ppr_obj.get_divAmount()))
            pprresponser.set_taxamount(str(i.taxamount))
            pprresponser.set_otheramount(str(i.otheramount))
            pprresponser.set_totalamount(str(i.totalamount))
            pprresponser.set_subcat_cat_data(subcat_cat_data, i.apsubcat_id)
            pprresponser.set_expense_data(expense_data, i.apexpense_id)
            pro_list.data.append(pprresponser)

        return pro_list

    def ppr_businesslogic(self, api_obj, ppr_obj):
        keys = Pprutility_keys()
        rowdata = json.loads(api_obj)
        rowdata = rowdata['data']
        year_term = ppr_obj.get_year_term()
        if year_term == "Monthly":
            month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        elif year_term == "Quarterly":
            month = ["Quarterly_1", "Quarterly_2", "Quarterly_3", "Quarterly_4"]
        else:
            return {"message": Pprdata_warning.month_quaterneed}
        output = []
        if len(rowdata) > 0:
            expensegrpname = self.remove_duplicate_arrdict(rowdata, '', keys.expensegrpname, '')
            for grpname in expensegrpname:
                output.append(self.expensegroup_name(grpname, month))
                expensename = self.remove_duplicate_arrdict(rowdata, keys.expensegrpname, keys.expensename, grpname)
                for exname in expensename:
                    output.append(self.expense_name(exname, month))
                    subcatname_arr = self.subcatname_arr(rowdata, grpname, exname)
                    for subcat in subcatname_arr:
                        output.append(self.subcat_name_data(subcat, month, rowdata, grpname, exname, year_term))
            output.append(self.columndata_sum(month, output, '100px'))
        return {"data": output}

    def remove_duplicate_arrdict(self, arr, conditionkey, neededkey, arrconditionkey):
        final = []
        if conditionkey == '' and arrconditionkey == '':
            for i in arr:
                if i[neededkey] not in final:
                    final.append(i[neededkey])
        else:
            for j in arr:
                if j[conditionkey] == arrconditionkey:
                    if j[neededkey] not in final:
                        final.append(j[neededkey])
        return final

    def get_monthsdict(self, dict, arr, value):
        for month in arr:
            dict[month] = value
        return dict

    def expensegroup_name(self, grpname, month):
        keys = Pprutility_keys()
        exgrprow = {}
        exgrprow[keys.name] = grpname
        self.get_monthsdict(exgrprow, month, "")
        exgrprow[keys.YTD] = ""
        exgrprow[keys.Padding_left] = "10px"
        exgrprow[keys.Padding] = '5px'
        return exgrprow

    def expense_name(self, exname, month):
        keys = Pprutility_keys()
        exnamerow = {}
        exnamerow[keys.name] = exname
        self.get_monthsdict(exnamerow, month, "")
        exnamerow[keys.YTD] = ""
        exnamerow[keys.Padding_left] = '50px'
        exnamerow[keys.Padding] = '5px'
        return exnamerow

    def subcatname_arr(self, rowdata, grpname, exname):
        keys = Pprutility_keys()
        arr = []
        for api in rowdata:
            if api[keys.expensegrpname] == grpname and api[keys.expensename] == exname:
                if api[keys.subcategoryname] not in arr:
                    arr.append(api[keys.subcategoryname])
        return arr

    def subcat_name_data(self, subcat, month, rowdata, grpname, exname, year_term):
        keys = Pprutility_keys()
        subcatrow = {}
        subcatrow[keys.name] = subcat
        self.get_monthsdict(subcatrow, month, Decimal(round(Decimal('0.00'), 2)))
        for apidata in rowdata:
            if apidata[keys.expensegrpname] == grpname and apidata[keys.expensename] == exname and apidata[
                keys.subcategoryname] == subcat:
                if year_term == "Monthly":
                    if subcatrow[month[int(apidata[keys.transactionmonth]) - 1]] != (round(Decimal('0.00'), 2)):
                        subcatrow[month[int(apidata[keys.transactionmonth]) - 1]] = Decimal(
                            subcatrow[month[int(apidata[keys.transactionmonth]) - 1]]) + Decimal(
                            round(Decimal(apidata[keys.amount]), 2))
                    else:
                        subcatrow[month[int(apidata[keys.transactionmonth]) - 1]] = Decimal(
                            round(Decimal(apidata[keys.amount]), 2))
                elif year_term == "Quarterly":
                    if subcatrow[f"Quarterly_{apidata[keys.quarter]}"] != (
                            round(Decimal('0.00'), 2)) and f"Quarterly_{apidata[keys.quarter]}" in month:
                        subcatrow[f"Quarterly_{apidata[keys.quarter]}"] = Decimal(
                            subcatrow[f"Quarterly_{apidata[keys.quarter]}"]) + Decimal(
                            round(Decimal(apidata[keys.amount]), 2))
                    else:
                        subcatrow[f"Quarterly_{apidata[keys.quarter]}"] = Decimal(
                            round(Decimal(apidata[keys.amount]), 2))
                self.subcat_needed_dict(subcatrow, apidata)
        totalsum = Decimal(round(Decimal('0.00'), 2))
        for sumof_month in month:
            totalsum = totalsum + subcatrow[sumof_month]
        subcatrow[keys.YTD] = totalsum
        subcatrow[keys.Padding_left] = '100px'
        subcatrow[keys.Padding] = '10px'
        return subcatrow

    def subcat_needed_dict(self, subcatrow, apidata):
        keys = Pprutility_keys()
        subcatrow[keys.is_supplier_in] = 'YES'
        subcatrow[keys.expense_id] = apidata[keys.expense_id]
        subcatrow[keys.apinvoicebranch_id] = apidata[keys.apinvoicebranch_id]
        subcatrow[keys.apinvoicedetails_id] = apidata[keys.apinvoicedetails_id]
        subcatrow[keys.apinvoice_id] = apidata[keys.apinvoice_id]
        subcatrow[keys.apinvoicesupplier_id] = apidata[keys.apinvoicesupplier_id]
        subcatrow[keys.subcat_id] = apidata[keys.subcat_id]
        subcatrow[keys.bizname] = apidata[keys.bizname]
        subcatrow[keys.bs_code] = apidata[keys.bs_code]
        subcatrow[keys.bsname] = apidata[keys.bsname]
        subcatrow[keys.cat_id] = apidata[keys.cat_id]
        subcatrow[keys.categoryname] = apidata[keys.categoryname]
        subcatrow[keys.cc_code] = apidata[keys.cc_code]
        subcatrow[keys.ccname] = apidata[keys.ccname]
        subcatrow[keys.expensegrpname] = apidata[keys.expensegrpname]
        subcatrow[keys.expensename] = apidata[keys.expensename]
        subcatrow[keys.finyear] = apidata[keys.finyear]
        subcatrow[keys.otheramount] = apidata[keys.otheramount]
        subcatrow[keys.quarter] = apidata[keys.quarter]
        subcatrow[keys.sectorname] = apidata[keys.sectorname]
        subcatrow[keys.subcategoryname] = apidata[keys.subcategoryname]
        subcatrow[keys.taxamount] = apidata[keys.taxamount]
        subcatrow[keys.totalamount] = apidata[keys.totalamount]
        subcatrow[keys.transactionmonth] = apidata[keys.transactionmonth]
        subcatrow[keys.transactionyear] = apidata[keys.transactionyear]
        return subcatrow

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

    def fetch_finyear_search_list(self, query, vys_page):
        if query is None:
            ase=self._current_app_schema()
            filter_val = Pprdata.objects.using(self._current_app_schema()).values('finyear').annotate(Count('finyear')).values('finyear').filter(
                status=1)[
                         vys_page.get_offset():vys_page.get_query_limit()]
        else:
            filter_val = Pprdata.objects.using(self._current_app_schema()).values('finyear').annotate(Count('finyear')).values('finyear').filter(
                Q(finyear__icontains=query), status=1,entity_id=self._entity_id())[
                         vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(filter_val)
        pro_list = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for i in filter_val:
                filter_response = Finyearresponse()
                filter_response.set_finyear(i['finyear'])
                pro_list.data.append(filter_response)
        vpage = NWisefinPaginator(filter_val, vys_page.get_index(), 10)
        pro_list.set_pagination(vpage)
        return pro_list

    def supplier_detial_individual(self, supplier_obj, vys_page):
        condition = Q(status=1, apexpense_id=supplier_obj.get_apexpense_id(),
                      apsubcat_id=supplier_obj.get_apsubcat_id(),entity_id=self._entity_id(),
                      finyear=supplier_obj.get_finyear())  # ,entry_module='AP'
        if supplier_obj.get_sectorname() != None and supplier_obj.get_sectorname() != "":
            condition &= Q(sectorname=supplier_obj.get_sectorname())
        if supplier_obj.get_masterbusinesssegment_name() != None and supplier_obj.get_masterbusinesssegment_name() != "":
            condition &= Q(bizname=supplier_obj.get_masterbusinesssegment_name())
        if supplier_obj.get_bs_name() != None and supplier_obj.get_bs_name() != "":
            condition &= Q(bsname=supplier_obj.get_bs_name())
        if supplier_obj.get_cc_name() != None and supplier_obj.get_cc_name() != "":
            condition &= Q(ccname=supplier_obj.get_cc_name())
        if supplier_obj.get_transactionmonth() != None and supplier_obj.get_transactionmonth() != "":
            condition &= Q(transactionmonth=supplier_obj.get_transactionmonth())
        if supplier_obj.get_quarter() != None and supplier_obj.get_quarter() != "":
            condition &= Q(quarter=supplier_obj.get_quarter())
        if supplier_obj.get_apinvoicebranch_id() != None and supplier_obj.get_apinvoicebranch_id() != "":
            condition &= Q(apinvoicebranch_id=supplier_obj.get_apinvoicebranch_id())
        ppr_obj = Pprdata.objects.using(self._current_app_schema()).filter(condition).values("apsubcat_id", "apexpense_id",
                                                           'apinvoicesupplier_id').annotate(
            totalamount=Sum('amount'), ecf_count=Count('id'))[
                  vys_page.get_offset():vys_page.get_query_limit()]
        pro_list = NWisefinList()
        if len(ppr_obj) <= 0:
            pass
        else:
            supplier_id = []
            for i in ppr_obj:
                supplier_id.append(i['apinvoicesupplier_id'])

            pprutility = VENDOR_SERVICE(self._scope())
            supplier_detials = pprutility.get_supplier(supplier_id)

            if len(supplier_detials) <= 0:
                pass
            else:
                for i in ppr_obj:
                    ppr_response = PprSupplierresponse()
                    ppr_response.set_ecf_count(i["ecf_count"])
                    ppr_response.set_totamount(str(Decimal(i["totalamount"]) / supplier_obj.get_divAmount()))
                    ppr_response.set_supplier_detial(supplier_detials, i["apinvoicesupplier_id"])
                    ppr_response.set_apexpense_id(i["apexpense_id"])
                    ppr_response.set_apsubcat_id(i["apsubcat_id"])
                    pro_list.data.append(ppr_response)
        vpage = NWisefinPaginator(ppr_obj, vys_page.get_index(), 10)
        pro_list.set_pagination(vpage)
        return pro_list
    #
    def ppr_mstbusinesssegement(self, sectorid, query, vys_page,emp_id,branchid,budget_builder_dropDown):#
        emp_service=EmployeeService(self._scope())
        pro_list=emp_service.ppr_businesssegement(sectorid, query, vys_page,emp_id,branchid,budget_builder_dropDown)
        return pro_list

    def businesssegement(self, mstbusinessid, query, vys_page,empid,branchid,budget_builder_dropDown):#
        api_service=EmployeeService(self._scope())
        pro_list=api_service.ppr_bs(mstbusinessid, query, vys_page,empid,branchid,budget_builder_dropDown)
        return pro_list

    def Suppliergrp_logic(self, data):
        pro_list = NWisefinList()
        try:
            data = json.loads(data)
            if len(data['data']) <= 0:
                pass
            else:
                ppr_keys = Pprutility_keys()
                uniq_code = []
                for i in data['data']:
                    if i['supplier_code'] not in uniq_code:
                        uniq_code.append(i['supplier_code'])
                output = []
                for i in uniq_code:
                    total = 0
                    totalecf = 1
                    row = {}
                    for j in data['data']:
                        if j[ppr_keys.supplier_code] == i:
                            total += Decimal(j[ppr_keys.totamount])
                            row[ppr_keys.supplier_id] = j[ppr_keys.supplier_id]
                            row[ppr_keys.supplier_name] = j[ppr_keys.supplier_name]
                            row[ppr_keys.supplier_code] = j[ppr_keys.supplier_code]
                            row[ppr_keys.quarter] = j[ppr_keys.quarter]
                            row[ppr_keys.transactionmonth] = j[ppr_keys.transactionmonth]
                            row[ppr_keys.transactiondate] = j[ppr_keys.transactiondate]
                            row[ppr_keys.supplier_branchname] = j[ppr_keys.supplier_branchname]
                            row[ppr_keys.supplier_panno] = j[ppr_keys.supplier_panno]
                            row[ppr_keys.supplier_gstno] = j[ppr_keys.supplier_gstno]
                            row[ppr_keys.pprdata_id] = j[ppr_keys.pprdata_id]
                            row[ppr_keys.totamount] = str(Decimal(total))
                            totalecf += 1
                            row[ppr_keys.ecf_count] = totalecf
                    output.append(row)

                out_page = output
                for i in out_page:
                    ppr_response = PprSupplierresponse()
                    ppr_response.set_suppliergid(i[ppr_keys.supplier_id])
                    ppr_response.set_supplier_name(i[ppr_keys.supplier_name])
                    ppr_response.set_supplier_code(i[ppr_keys.supplier_code])
                    ppr_response.set_quarter(i[ppr_keys.quarter])
                    ppr_response.set_transactionmonth(i[ppr_keys.transactionmonth])
                    ppr_response.set_transactiondate(str(i[ppr_keys.transactiondate]))
                    ppr_response.set_supplier_branchname(i[ppr_keys.supplier_branchname])
                    ppr_response.set_supplier_panno(i[ppr_keys.supplier_panno])
                    ppr_response.set_supplier_gstno(i[ppr_keys.supplier_gstno])
                    ppr_response.set_pprdata_id(i[ppr_keys.pprdata_id])
                    ppr_response.set_totamount(str(i[ppr_keys.totamount]))
                    ppr_response.set_ecf_count(i[ppr_keys.ecf_count])
                    pro_list.data.append(ppr_response)

            return pro_list
        except:
            return pro_list

    def supplier_detials_grp(self, value_obj, supplier_obj):
        if value_obj == 'query':
            pro_list = NWisefinList()

            pprutility = VENDOR_SERVICE(self._scope())
            # service = ApiService(self._scope())
            supplier_detials = pprutility.get_supplier(supplier_obj.get_supplier_id())
            for supplier in supplier_detials:
                condition = Q(status=1, apexpense_id=supplier_obj.get_apexpense_id(),
                              apsubcat_id=supplier_obj.get_apsubcat_id(),
                              finyear=supplier_obj.get_finyear())  # ,entry_module='AP'

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
                ppr_obj = Pprdata.objects.using(self._current_app_schema()).filter(condition).values("apsubcat_id", "apexpense_id",
                                                                                          "apinvoicesupplier_id",
                                                                                          groupcondition).annotate(
                    totalamount=Sum('amount'))
                if len(ppr_obj) <= 0:
                    supplier_ids = []
                    supplier_ids.append(supplier["supplier_id"])
                    # service = ApiService(self._scope())
                    supplier_detials = pprutility.get_supplier(supplier_ids)
                    # supplier_detials = service.get_supplier(supplier_ids)

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
                            ppr_response = PprSupplierresponse()
                            ppr_response.set_supplier_detial(supplier_detials, supplier["supplier_id"])
                            ppr_response.set_apexpense_id(supplier_obj.get_apexpense_id())
                            ppr_response.set_apsubcat_id(supplier_obj.get_apsubcat_id())
                            ppr_response.set_totamount(str(Decimal(0.0) / supplier_obj.get_divAmount()))
                            ppr_response.set_transactionmonth(str(tranmon))
                            pro_list.data.append(ppr_response)
                            tranmon1 = tranmon1 + 1
                    if supplier_obj.get_yearterm() == 'Quarterly':
                        tranmon1 = 1
                        for f in range(0, 4):
                            tranmon = tranmon1
                            ppr_response = PprSupplierresponse()
                            ppr_response.set_supplier_detial(supplier_detials, supplier["supplier_id"])
                            ppr_response.set_apexpense_id(supplier_obj.get_apexpense_id())
                            ppr_response.set_apsubcat_id(supplier_obj.get_apsubcat_id())
                            ppr_response.set_totamount(str(Decimal(0.0) / supplier_obj.get_divAmount()))
                            ppr_response.set_quarter(tranmon)
                            pro_list.data.append(ppr_response)
                            tranmon1 = tranmon1 + 1
                else:
                    supplier_id = []
                    for i in ppr_obj:
                        supplier_id.append(i["apinvoicesupplier_id"])
                    service = VENDOR_SERVICE(self._scope())
                    supplier_detials = service.get_supplier(supplier_obj.get_supplier_id())
                    for i in ppr_obj:
                        ppr_response = PprSupplierresponse()
                        if supplier_obj.get_yearterm() == "Monthly":
                            ppr_response.set_transactionmonth(i["transactionmonth"])
                        if supplier_obj.get_yearterm() == "Quarterly":
                            ppr_response.set_quarter(i["quarter"])
                        ppr_response.set_totamount(str(Decimal(i["totalamount"]) / supplier_obj.get_divAmount()))
                        ppr_response.set_supplier_detial(supplier_detials, i["apinvoicesupplier_id"])
                        ppr_response.set_apexpense_id(i["apexpense_id"])
                        ppr_response.set_apsubcat_id(i["apsubcat_id"])
                        pro_list.data.append(ppr_response)
            return pro_list
        else:

            condition = Q(status=1, apexpense_id=supplier_obj.get_apexpense_id(),
                          apsubcat_id=supplier_obj.get_apsubcat_id(),
                          finyear=supplier_obj.get_finyear())  # ,entry_module='AP'
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
            ppr_obj = Pprdata.objects.using(self._current_app_schema()).filter(condition).values("apsubcat_id", "apexpense_id",
                                                                                      "apinvoicesupplier_id",
                                                                                      groupcondition).annotate(
                totalamount=Sum('amount'))
            pro_list = NWisefinList()
            if len(ppr_obj) <= 0:
                pass
            else:
                supplier_id = []
                for i in ppr_obj:
                    supplier_id.append(i["apinvoicesupplier_id"])
                service = VENDOR_SERVICE(self._scope())
                supplier_detials = service.get_supplier(supplier_id)
                for i in ppr_obj:
                    ppr_response = PprSupplierresponse()
                    if supplier_obj.get_yearterm() == "Monthly":
                        ppr_response.set_transactionmonth(i["transactionmonth"])
                    if supplier_obj.get_yearterm() == "Quarterly":
                        ppr_response.set_quarter(i["quarter"])
                    ppr_response.set_totamount(str(Decimal(i["totalamount"]) / supplier_obj.get_divAmount()))
                    ppr_response.set_supplier_detial(supplier_detials, i["apinvoicesupplier_id"])
                    ppr_response.set_apexpense_id(i["apexpense_id"])
                    ppr_response.set_apsubcat_id(i["apsubcat_id"])
                    pro_list.data.append(ppr_response)
            return pro_list

    def suppliergrp_logic(self, supplier_data, supplier_obj):
        try:
            supplier_data = json.loads(supplier_data)
            if len(supplier_data['data']) > 0:
                keys = Pprutility_keys
                year_term = supplier_obj.get_yearterm()
                if year_term == "Monthly":
                    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                elif year_term == "Quarterly":
                    month = ["Quarterly_1", "Quarterly_2", "Quarterly_3", "Quarterly_4"]
                else:
                    return {"message": Pprdata_warning.month_quaterneed}
                supplier_name = []
                for i in supplier_data['data']:
                    if i['supplier_name'] not in supplier_name:
                        supplier_name.append(i['supplier_name'])
                output = []
                for name in supplier_name:
                    supplier_row = {}
                    supplier_row[keys.name] = name
                    self.get_monthsdict(supplier_row, month, Decimal(round(Decimal('0.00'), 2)))
                    supplier_row[keys.YTD] = Decimal(round(Decimal('0.00'), 2))
                    for apidata in supplier_data['data']:
                        if apidata['supplier_name'] == name:
                            supplier_row[keys.apexpense_id] = apidata[keys.apexpense_id]
                            supplier_row[keys.apsubcat_id] = apidata[keys.apsubcat_id]
                            if year_term == "Monthly":
                                if supplier_row[month[int(apidata[keys.transactionmonth]) - 1]] != (
                                        round(Decimal('0.00'), 2)):
                                    supplier_row[month[int(apidata[keys.transactionmonth]) - 1]] = Decimal(
                                        supplier_row[month[int(apidata[keys.transactionmonth]) - 1]]) + Decimal(
                                        round(Decimal(apidata[keys.totamount]), 2))
                                else:
                                    supplier_row[month[int(apidata[keys.transactionmonth]) - 1]] = Decimal(
                                        round(Decimal(apidata[keys.totamount]), 2))
                            elif year_term == "Quarterly":
                                if supplier_row[f"Quarterly_{apidata[keys.quarter]}"] != (
                                        round(Decimal('0.00'), 2)) and f"Quarterly_{apidata[keys.quarter]}" in month:
                                    supplier_row[f"Quarterly_{apidata[keys.quarter]}"] = Decimal(
                                        supplier_row[f"Quarterly_{apidata[keys.quarter]}"]) + Decimal(
                                        round(Decimal(apidata[keys.totamount]), 2))
                                else:
                                    supplier_row[f"Quarterly_{apidata[keys.quarter]}"] = Decimal(
                                        round(Decimal(apidata[keys.totamount]), 2))
                        self.supplier_need_dict(supplier_row, keys, apidata, year_term)
                    totalsum = Decimal(round(Decimal('0.00'), 2))
                    for sumof_month in month:
                        totalsum = totalsum + supplier_row[sumof_month]
                    supplier_row[keys.YTD] = totalsum
                    supplier_row[keys.Padding_left] = '120px'
                    supplier_row[keys.Padding] = '10px'
                    output.append(supplier_row)
                return {"data": output}
            else:
                return {"data": []}
        except:
            return {"data": []}

    def supplier_need_dict(self, dict, keys, arr, year_term):
        dict[keys.supplier_id] = arr[keys.supplier_id]
        dict[keys.supplier_code] = arr[keys.supplier_code]
        dict[keys.supplier_branchname] = arr[keys.supplier_branchname]
        dict[keys.supplier_panno] = arr[keys.supplier_panno]
        dict[keys.supplier_gstno] = arr[keys.supplier_gstno]
        if year_term == "Monthly":
            dict[keys.transactionmonth] = arr[keys.transactionmonth]
        if year_term == "Quarterly":
            dict[keys.quarter] = arr[keys.quarter]

        return dict

    def fetch_ppr_ccbs(self, ccbs_obj, vys_page):

        condition = Q(status=1,entity_id=self._entity_id(),
                      apexpense_id=ccbs_obj.get_apexpense_id(),
                      apsubcat_id=ccbs_obj.get_apsubcat_id(),
                      finyear=ccbs_obj.get_finyear())  # ,entry_module='AP'
        if ccbs_obj.get_masterbusinesssegment_name() != None and ccbs_obj.get_masterbusinesssegment_name() != "":
            condition &= Q(bizname=ccbs_obj.get_masterbusinesssegment_name())
        if ccbs_obj.get_sectorname() != None and ccbs_obj.get_sectorname() != "":
            condition &= Q(sectorname=ccbs_obj.get_sectorname())
        if ccbs_obj.get_bs_name() != None and ccbs_obj.get_bs_name() != "":
            condition &= Q(bsname=ccbs_obj.get_bs_name())
        if ccbs_obj.get_cc_name() != None and ccbs_obj.get_cc_name() != "":
            condition &= Q(ccname=ccbs_obj.get_cc_name())
        if ccbs_obj.get_yearterm() == 'Quarterly':
            condition &= Q(quarter=ccbs_obj.get_quarter())
        if ccbs_obj.get_yearterm() == 'Monthly':
            condition &= Q(transactionmonth=ccbs_obj.get_transactionmonth())
        ppr_obj = Pprdata.objects.using(self._current_app_schema()).filter(condition).values('bsname', 'ccname', 'bizname', 'sectorname',
                                                           'apexpense_id').annotate(
            totalamount=Sum('amount'))[
                  vys_page.get_offset():vys_page.get_query_limit()]
        pro_list = NWisefinList()
        if len(ppr_obj) <= 0:
            pass
        else:
            expense_id = []
            for i in ppr_obj:
                expense_id.append(i["apexpense_id"])
            pprutilits = MASTER_SERVICE(self._scope())
            expense_detial = pprutilits.get_expense(expense_id)
            if len(expense_detial) <= 0:
                pass
            else:
                for i in ppr_obj:
                    ccbs_response = pprresponse()
                    ccbs_response.set_bsname(i["bsname"])
                    ccbs_response.set_ccname(i["ccname"])
                    ccbs_response.set_bizname(i["bizname"])
                    ccbs_response.set_sectorname(i["sectorname"])
                    ccbs_response.set_totalamount(str(Decimal(i["totalamount"]) / ccbs_obj.get_divAmount()))
                    ccbs_response.set_expense_data(expense_detial, i["apexpense_id"])
                    pro_list.data.append(ccbs_response)
        vpage = NWisefinPaginator(ppr_obj, vys_page.get_index(), 10)
        pro_list.set_pagination(vpage)
        return pro_list

    def ccbs_logic(self, ccbs_data):
        ccbs_data = json.loads(ccbs_data)
        output = []
        if len(ccbs_data['data']) <= 0:
            pass
        else:
            bscc_arr = []
            for i in ccbs_data['data']:
                bscc_arr.append([i['bsname'], i['ccname']])
            pprutility = USER_SERVICE(self._scope())
            keys = Pprutility_keys
            bscc_arrUniq = pprutility.get_uniqarr(bscc_arr)
            for bs_cc in bscc_arrUniq:
                row = {}
                total = 0
                for apidata in ccbs_data['data']:
                    if apidata[keys.bsname] == bs_cc[0] and apidata[keys.ccname] == bs_cc[1]:
                        total = total + Decimal(apidata[keys.totalamount])
                        row[keys.totalamount] = total
                        row[keys.bizname] = apidata[keys.bizname]
                        row[keys.bsname] = apidata[keys.bsname]
                        row[keys.ccname] = apidata[keys.ccname]
                        row[keys.expense_id] = apidata[keys.expense_id]
                        row[keys.expensegrpname] = apidata[keys.expensegrpname]
                        row[keys.expensename] = apidata[keys.expensename]
                        row[keys.sectorname] = apidata[keys.sectorname]
                output.append(row)
        return output

    def ccbs_uniqdataresponse(self, arr):
        pro_list = NWisefinList()
        keys = Pprutility_keys
        if len(arr) <= 0:
            pass
        else:
            for i in arr:
                ccbs_response = pprresponse()
                ccbs_response.set_bsname(i[keys.bsname])
                ccbs_response.set_ccname(i[keys.ccname])
                ccbs_response.set_bizname(i[keys.bizname])
                ccbs_response.set_sectorname(i[keys.sectorname])
                ccbs_response.set_totalamount(str(i[keys.totalamount]))
                ccbs_response.set_expensename(i[keys.expensename])
                ccbs_response.set_expensegrpname(i[keys.expensegrpname])
                ccbs_response.set_apexpenseid(i[keys.expense_id])
                pro_list.data.append(ccbs_response)
        return pro_list

    def new_expense_list(self, ppr_obj):  # vys_page
        pprutility = MASTER_SERVICE(self._scope())
        pprdata = []
        pro_list = NWisefinList()
        condition = Q(status=1,entity_id=self._entity_id())
        if ppr_obj.get_expense_grp_id() != None and ppr_obj.get_expense_grp_id() != "":
            expense_dtls = APexpense.objects.using(self._current_app_schema()).filter(exp_grp_id=ppr_obj.get_expense_grp_id(),entity_id=self._entity_id(),)
            print(expense_dtls)
            for expense in expense_dtls:
                if ppr_obj.get_branch_id() != None and ppr_obj.get_branch_id() != "":
                    condition &= Q(apinvoicebranch_id=ppr_obj.get_branch_id())
                if ppr_obj.get_finyear() != None and ppr_obj.get_finyear() != "":
                    condition &= Q(finyear=ppr_obj.get_finyear())
                if ppr_obj.get_sector_name() != None and ppr_obj.get_sector_name() != "":
                    condition &= Q(sectorname=ppr_obj.get_sector_name())
                if ppr_obj.get_mstbusiness_segment_name() != None and ppr_obj.get_mstbusiness_segment_name() != "":
                    condition &= Q(bizname=ppr_obj.get_mstbusiness_segment_name())
                if ppr_obj.get_bs_name() != None and ppr_obj.get_bs_name() != "":
                    condition &= Q(bsname=ppr_obj.get_bs_name())
                if ppr_obj.get_cc_name() != None and ppr_obj.get_cc_name() != "":
                    condition &= Q(ccname=ppr_obj.get_cc_name())
                    condition &= Q(apexpense_id=expense.id)
                if ppr_obj.get_year_term() == 'Monthly':
                    pprdata = Pprdata.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id',
                                                                                              'transactionmonth').annotate(
                        amount=Sum('amount'))
                    # [vys_page.get_offset():vys_page.get_query_limit()]
                if ppr_obj.get_year_term() == 'Quarterly':
                    pprdata = Pprdata.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id',
                                                                                              'quarter').annotate(
                        amount=Sum('amount'))
                    # [vys_page.get_offset():vys_page.get_query_limit()]
                if len(pprdata) == 0:
                    if ppr_obj.get_year_term() == 'Monthly':
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
                            pprresponser.expense_id = expense.id
                            pprresponser.expensename = expense.head
                            pprresponser.expensegrpname = expense.group
                            pprresponser.expensegrp_id = expense.exp_grp_id
                            pprresponser.set_amount(str(Decimal(0.0) / ppr_obj.get_divAmount()))
                            pprresponser.set_transactionmonth(str(tranmon))
                            pro_list.data.append(pprresponser)
                            tranmon1 = tranmon1 + 1
                    if ppr_obj.get_year_term() == 'Quarterly':
                        tranmon1 = 1
                        for f in range(0, 4):
                            tranmon = tranmon1
                            pprresponser = pprresponse()
                            pprresponser.expense_id = expense.id
                            pprresponser.expensename = expense.head
                            pprresponser.expensegrpname = expense.group
                            pprresponser.expensegrp_id = expense.exp_grp_id
                            pprresponser.set_quarter(str(tranmon))
                            pprresponser.set_amount(str(Decimal(0.0) / ppr_obj.get_divAmount()))
                            pro_list.data.append(pprresponser)
                            tranmon1 = tranmon1 + 1
                else:
                    expense_ids = []
                    for i in pprdata:
                        expense_ids.append(i['apexpense_id'])
                    expense_detials = pprutility.get_expense(expense_ids)
                    for i in pprdata:
                        pprresponser = pprresponse()
                        pprresponser.set_expense_data(expense_detials, i["apexpense_id"])
                        pprresponser.set_amount(str(Decimal(i['amount']) / ppr_obj.get_divAmount()))
                        if ppr_obj.get_year_term() == 'Monthly':
                            pprresponser.set_transactionmonth(i["transactionmonth"])
                        if ppr_obj.get_year_term() == 'Quarterly':
                            pprresponser.set_quarter(i["quarter"])
                        pro_list.data.append(pprresponser)
                # vpage = PPRNWisefinPaginator(pprdata, vys_page.get_index(), 5)
                # pro_list.set_pagination(vpage)
            return pro_list

    def new_expense_logic(self, expense_data, ppr_obj):
        expense_data = json.loads(expense_data)
        keys = Pprutility_keys()
        output = []
        if len(expense_data['data']) <= 0:
            pass
        else:
            year_term = ppr_obj.get_year_term()
            if year_term == "Monthly":
                month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            elif year_term == "Quarterly":
                month = ["Quarterly_1", "Quarterly_2", "Quarterly_3", "Quarterly_4"]
            else:
                return {"message": Pprdata_warning.month_quaterneed}

            uniqexpenseid = self.remove_duplicate_arrdict(expense_data['data'], '', keys.expense_id, '')
            uniqexpenselen = len(uniqexpenseid) - 1

            for index, expenseid in enumerate(uniqexpenseid):
                row = {}
                row[keys.expense_id] = expenseid
                self.get_monthsdict(row, month, Decimal(round(Decimal('0.00'), 2)))
                for uniq_month in expense_data['data']:
                    if expenseid == uniq_month[keys.expense_id]:
                        if year_term == "Monthly":
                            if row[month[int(uniq_month[keys.transactionmonth]) - 1]] != Decimal(
                                    round(Decimal('0.00'), 2)):
                                row[month[int(uniq_month[keys.transactionmonth]) - 1]] = row[month[
                                    int(uniq_month[keys.transactionmonth]) - 1]] + Decimal(
                                    round(Decimal(uniq_month[keys.amount]), 2))
                            else:
                                row[month[int(uniq_month[keys.transactionmonth]) - 1]] = Decimal(
                                    round(Decimal(uniq_month[keys.amount]), 2))
                        if year_term == "Quarterly":
                            if row[f"Quarterly_{uniq_month[keys.quarter]}"] != Decimal(
                                    round(Decimal('0.00'), 2)) and f"Quarterly_{uniq_month[keys.quarter]}" in month:
                                row[f"Quarterly_{uniq_month[keys.quarter]}"] = row[
                                                                                   f"Quarterly_{uniq_month[keys.quarter]}"] + Decimal(
                                    round(Decimal(uniq_month[keys.amount]), 2))
                            else:
                                row[f"Quarterly_{uniq_month[keys.quarter]}"] = Decimal(
                                    round(Decimal(uniq_month[keys.amount]), 2))
                        row[keys.name] = uniq_month[keys.expensename]
                        if index == uniqexpenselen:
                            row['page'] = 'Y'
                totalsum = Decimal(round(Decimal('0.00'), 2))
                for sumof_month in month:
                    totalsum = totalsum + row[sumof_month]
                row[keys.YTD] = totalsum
                row['tree_flag'] = 'Y'
                row[keys.Padding_left] = '50px'
                row[keys.Padding] = '5px'
                output.append(row)

        return {"data": output}  # "pagination": expense_data["pagination"]

    def new_expensegrp_list(self, ppr_obj):
        pprutility = MASTER_SERVICE(self._scope())
        pro_list = NWisefinList()
        condition = Q(status=1)
        expensegrp_id = APexpensegroup.objects.using(self._current_app_schema()).filter(condition)
        for exgrp_id in expensegrp_id:
            expense_id = pprutility.get_new_expgrp_exp([exgrp_id.id])
            if len(expense_id) == 0:
                if ppr_obj.get_year_term() == 'Monthly':
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
                        pprresponser.set_amount(str(Decimal(0.0) / ppr_obj.get_divAmount()))
                        pprresponser.set_transactionmonth(tranmon)
                        pro_list.data.append(pprresponser)
                        tranmon1 = tranmon1 + 1
                if ppr_obj.get_year_term() == 'Quarterly':
                    tranmon1 = 1
                    for f in range(0, 4):
                        tranmon = tranmon1
                        pprresponser = pprresponse()
                        pprresponser.expensegrp_id = exgrp_id.id
                        pprresponser.expensegrpname = exgrp_id.name
                        pprresponser.set_amount(str(Decimal(0.0) / ppr_obj.get_divAmount()))
                        pprresponser.set_quarter(tranmon)
                        pro_list.data.append(pprresponser)
                        tranmon1 = tranmon1 + 1
            else:
                for expense in expense_id:

                    if ppr_obj.get_branch_id() != None and ppr_obj.get_branch_id() != "":
                        condition &= Q(apinvoicebranch_id=ppr_obj.get_branch_id())
                    if ppr_obj.get_finyear() != None and ppr_obj.get_finyear() != "":
                        condition &= Q(finyear=ppr_obj.get_finyear())
                    if ppr_obj.get_sector_name() != None and ppr_obj.get_sector_name() != "":
                        condition &= Q(sectorname=ppr_obj.get_sector_name())
                    if ppr_obj.get_mstbusiness_segment_name() != None and ppr_obj.get_mstbusiness_segment_name() != "":
                        condition &= Q(bizname=ppr_obj.get_mstbusiness_segment_name())
                    if ppr_obj.get_bs_name() != None and ppr_obj.get_bs_name() != "":
                        condition &= Q(bsname=ppr_obj.get_bs_name())
                    if ppr_obj.get_cc_name() != None and ppr_obj.get_cc_name() != "":
                        condition &= Q(ccname=ppr_obj.get_cc_name())
                    condition &= Q(apexpense_id=expense)
                    if ppr_obj.get_year_term() == 'Monthly':
                        pprdata = Pprdata.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id',
                                                                                                  'transactionmonth').annotate(
                            amount=Sum('amount'))
                    if ppr_obj.get_year_term() == 'Quarterly':
                        pprdata = Pprdata.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id',
                                                                                                  'quarter').annotate(
                            amount=Sum('amount'))
                    expense_ids = []
                    expense_ids.append(expense)
                    expense_detials = pprutility.get_expense(expense_id)
                    if len(pprdata) == 0:
                        if ppr_obj.get_year_term() == 'Monthly':
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
                                pprresponser.set_amount(str(Decimal(0.0) / ppr_obj.get_divAmount()))
                                pprresponser.set_transactionmonth(tranmon)
                                pro_list.data.append(pprresponser)
                                tranmon1 = tranmon1 + 1
                        if ppr_obj.get_year_term() == 'Quarterly':
                            tranmon1 = 1
                            for f in range(0, 4):
                                tranmon = tranmon1
                                pprresponser = pprresponse()
                                pprresponser.expensegrp_id = exgrp_id.id
                                pprresponser.expensegrpname = exgrp_id.name
                                pprresponser.set_quarter(tranmon)
                                pro_list.data.append(pprresponser)
                                tranmon1 = tranmon1 + 1

                    else:
                        for i in pprdata:
                            pprresponser = pprresponse()
                            pprresponser.expensegrp_id = exgrp_id.id
                            pprresponser.expensegrpname = exgrp_id.name
                            pprresponser.set_amount(str(Decimal(i['amount']) / ppr_obj.get_divAmount()))
                            if ppr_obj.get_year_term() == 'Monthly':
                                pprresponser.set_transactionmonth(i["transactionmonth"])
                            if ppr_obj.get_year_term() == 'Quarterly':
                                pprresponser.set_quarter(i["quarter"])
                            pro_list.data.append(pprresponser)
                        # vpage = PPRNWisefinPaginator(pprdata, vys_page.get_index(), 5)
                        # pro_list.set_pagination(vpage)
        return pro_list


    def new_expensegrp_logic(self, expensegrp_data, ppr_obj):
        expensegrp_data = json.loads(expensegrp_data)
        keys = Pprutility_keys()
        output = []
        if len(expensegrp_data['data']) <= 0:
            pass
        else:
            year_term = ppr_obj.get_year_term()
            if year_term == "Monthly":
                month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            elif year_term == "Quarterly":
                month = ["Quarterly_1", "Quarterly_2", "Quarterly_3", "Quarterly_4"]
            else:
                return {"message": Pprdata_warning.month_quaterneed}
            uniqexpensegrpname = self.remove_duplicate_arrdict(expensegrp_data['data'], '', keys.expensegrpname, '')
            for expensegrp in uniqexpensegrpname:
                row = {}
                row[keys.name] = expensegrp
                self.get_monthsdict(row, month, Decimal(round(Decimal('0.00'), 2)))
                for uniq_month in expensegrp_data['data']:
                    if expensegrp == uniq_month[keys.expensegrpname]:
                        if year_term == "Monthly":
                            if row[month[int(uniq_month[keys.transactionmonth]) - 1]] != Decimal(
                                    round(Decimal('0.00'), 2)):
                                row[month[int(uniq_month[keys.transactionmonth]) - 1]] = row[month[
                                    int(uniq_month[keys.transactionmonth]) - 1]] + Decimal(
                                    round(Decimal(uniq_month[keys.amount]), 2))
                            else:
                                row[month[int(uniq_month[keys.transactionmonth]) - 1]] = Decimal(
                                    round(Decimal(uniq_month[keys.amount]), 2))
                        if year_term == "Quarterly":
                            if row[f"Quarterly_{uniq_month[keys.quarter]}"] != Decimal(
                                    round(Decimal('0.00'), 2)) and f"Quarterly_{uniq_month[keys.quarter]}" in month:
                                row[f"Quarterly_{uniq_month[keys.quarter]}"] = row[
                                                                                   f"Quarterly_{uniq_month[keys.quarter]}"] + Decimal(
                                    round(Decimal(uniq_month[keys.amount]), 2))
                            else:
                                row[f"Quarterly_{uniq_month[keys.quarter]}"] = Decimal(
                                    round(Decimal(uniq_month[keys.amount]), 2))

                totalsum = Decimal(round(Decimal('0.00'), 2))
                for sumof_month in month:
                    totalsum = totalsum + row[sumof_month]
                row[keys.YTD] = totalsum
                row['tree_flag'] = 'Y'
                row[keys.Padding_left] = '10px'
                row[keys.Padding] = '5px'
                output.append(row)
            output.append(self.columndata_sum(month, output, '10px'))
        return {"data": output}  # "pagination":expensegrp_data['pagination']

    def new_subcat_list(self, ppr_obj):  # vys_page
        pprutility = MASTER_SERVICE(self._scope())
        pprdata = []
        condition = Q(status=1,entity_id=self._entity_id())  # ,entry_module='AP'
        if ppr_obj.get_branch_id() != None and ppr_obj.get_branch_id() != "":
            condition &= Q(apinvoicebranch_id=ppr_obj.get_branch_id())
        if ppr_obj.get_finyear() != None and ppr_obj.get_finyear() != "":
            condition &= Q(finyear=ppr_obj.get_finyear())
        if ppr_obj.get_sector_name() != None and ppr_obj.get_sector_name() != "":
            condition &= Q(sectorname=ppr_obj.get_sector_name())
        if ppr_obj.get_mstbusiness_segment_name() != None and ppr_obj.get_mstbusiness_segment_name() != "":
            condition &= Q(bizname=ppr_obj.get_mstbusiness_segment_name())
        if ppr_obj.get_bs_name() != None and ppr_obj.get_bs_name() != "":
            condition &= Q(bsname=ppr_obj.get_bs_name())
        if ppr_obj.get_cc_name() != None and ppr_obj.get_cc_name() != "":
            condition &= Q(ccname=ppr_obj.get_cc_name())
        if ppr_obj.get_expense_id() != None and ppr_obj.get_expense_id() != "":
            condition &= Q(apexpense_id=ppr_obj.get_expense_id())
        if ppr_obj.get_year_term() == 'Monthly':
            pprdata = Pprdata.objects.using(self._current_app_schema()).filter(condition).values('apsubcat_id', 'transactionmonth',
                                                               'apexpense_id').annotate(
                amount=Sum('amount'))
            # [vys_page.get_offset():vys_page.get_query_limit()]
        if ppr_obj.get_year_term() == 'Quarterly':
            pprdata = Pprdata.objects.using(self._current_app_schema()).filter(condition).values('apsubcat_id', 'quarter', 'apexpense_id').annotate(
                amount=Sum('amount'))
            # [vys_page.get_offset():vys_page.get_query_limit()]
        pro_list = NWisefinList()
        if len(pprdata) <= 0:
            pass
        else:
            subcat_ids = []
            for i in pprdata:
                subcat_ids.append(i['apsubcat_id'])

            subcat_detials = pprutility.get_subcat(subcat_ids)
            for i in pprdata:
                pprresponser = pprresponse()
                pprresponser.set_subcat_cat_data(subcat_detials, i["apsubcat_id"])
                pprresponser.set_amount(str(Decimal(i['amount']) / ppr_obj.get_divAmount()))
                if ppr_obj.get_year_term() == 'Monthly':
                    pprresponser.set_transactionmonth(i["transactionmonth"])
                if ppr_obj.get_year_term() == 'Quarterly':
                    pprresponser.set_quarter(i["quarter"])
                pprresponser.set_apexpenseid(i['apexpense_id'])
                pro_list.data.append(pprresponser)
        # vpage = PPRNWisefinPaginator(pprdata, vys_page.get_index(), 5)
        # pro_list.set_pagination(vpage)
        return pro_list

    def new_subcat_logic(self, subcat_data, ppr_obj):
        subcat_data = json.loads(subcat_data)
        keys = Pprutility_keys()
        output = []
        if len(subcat_data['data']) <= 0:
            pass
        else:
            year_term = ppr_obj.get_year_term()
            if year_term == "Monthly":
                month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            elif year_term == "Quarterly":
                month = ["Quarterly_1", "Quarterly_2", "Quarterly_3", "Quarterly_4"]
            else:
                return {"message": Pprdata_warning.month_quaterneed}
            uniqsubcatname = self.remove_duplicate_arrdict(subcat_data['data'], '', keys.subcategoryname, '')
            uniqsubcatlen = len(uniqsubcatname) - 1
            for index, subcat in enumerate(uniqsubcatname):
                row = {}
                row[keys.name] = subcat
                self.get_monthsdict(row, month, Decimal(round(Decimal('0.00'), 2)))
                for uniq_month in subcat_data['data']:
                    if subcat == uniq_month[keys.subcategoryname]:
                        if year_term == "Monthly":
                            if row[month[int(uniq_month[keys.transactionmonth]) - 1]] != Decimal(
                                    round(Decimal('0.00'), 2)):
                                row[month[int(uniq_month[keys.transactionmonth]) - 1]] = row[month[
                                    int(uniq_month[keys.transactionmonth]) - 1]] + Decimal(
                                    round(Decimal(uniq_month[keys.amount]), 2))
                            else:
                                row[month[int(uniq_month[keys.transactionmonth]) - 1]] = Decimal(
                                    round(Decimal(uniq_month[keys.amount]), 2))
                        if year_term == "Quarterly":
                            if row[f"Quarterly_{uniq_month[keys.quarter]}"] != Decimal(
                                    round(Decimal('0.00'), 2)) and f"Quarterly_{uniq_month[keys.quarter]}" in month:
                                row[f"Quarterly_{uniq_month[keys.quarter]}"] = row[
                                                                                   f"Quarterly_{uniq_month[keys.quarter]}"] + Decimal(
                                    round(Decimal(uniq_month[keys.amount]), 2))
                            else:
                                row[f"Quarterly_{uniq_month[keys.quarter]}"] = Decimal(
                                    round(Decimal(uniq_month[keys.amount]), 2))
                        row[keys.subcat_id] = uniq_month[keys.subcat_id]
                        row[keys.expense_id] = uniq_month[keys.expense_id]
                        if uniqsubcatlen == index:
                            row['page'] = 'Y'
                totalsum = Decimal(round(Decimal('0.00'), 2))
                for sumof_month in month:
                    totalsum = totalsum + row[sumof_month]
                row[keys.YTD] = totalsum
                row['tree_flag'] = 'Y'
                row[keys.is_supplier_in] = 'Y'
                row[keys.Padding_left] = '100px'
                row[keys.Padding] = '10px'
                output.append(row)

        return {"data": output}  # "pagination":subcat_data['pagination']

    def new_expensegrptable(self):
        pprdata = Pprdata.objects.using(self._current_app_schema()).filter(status=1,entity_id=self._entity_id()).values('finyear', 'quarter', 'transactionmonth', 'transactionyear',
                                                          'apinvoicebranch_id', 'apexpense_id', 'bizname',
                                                          'sectorname').annotate(amount=Sum('amount')).order_by(
            'quarter', 'transactionmonth', 'apexpense_id', 'bizname')  # entry_module='AP',
        if len(pprdata) <= 0:
            pass
        else:
            for i in pprdata:
                condition = Q(finyear=i['finyear'], quarter=i['quarter'], transactionmonth=i['transactionmonth'],
                              transactionyear=i['transactionyear'], apinvoicebranch_id=i['apinvoicebranch_id'],
                              apexpense_id=i['apexpense_id'], bizname=i['bizname'], sectorname=i['sectorname'])
                expensegrpMeta_exist = PprdataExpGrpMeta.objects.using(self._current_app_schema()).filter(condition).exists()
                if expensegrpMeta_exist == True:
                    expensegrpMeta = PprdataExpGrpMeta.objects.using(self._current_app_schema()).update(amount=i['amount'])
                else:
                    expensegrpMeta = PprdataExpGrpMeta.objects.using(self._current_app_schema()).create(finyear=i['finyear'], quarter=i['quarter'],
                                                                      transactionmonth=i['transactionmonth'],
                                                                      transactionyear=i['transactionyear'],
                                                                      apinvoicebranch_id=i['apinvoicebranch_id'],
                                                                      apexpense_id=i['apexpense_id'],
                                                                      bizname=i['bizname'], sectorname=i['sectorname'],
                                                                      amount=i['amount'])

        suc_obj = Success()
        suc_obj.set_status(successMessage.SUCCESS)
        return suc_obj

    def ECF_detials(self, supplier_obj, vys_page):
        condition = Q(status=1, apexpense_id=supplier_obj.get_apexpense_id(),entity_id=self._entity_id(),
                      apsubcat_id=supplier_obj.get_apsubcat_id(),
                      sectorname=supplier_obj.get_sectorname(),
                      finyear=supplier_obj.get_finyear(),
                      apinvoicesupplier_id=supplier_obj.get_apinvoicesupplier_id())  # ,entry_module='AP'
        if supplier_obj.get_masterbusinesssegment_name() != None and supplier_obj.get_masterbusinesssegment_name() != "":
            condition &= Q(bizname=supplier_obj.get_masterbusinesssegment_name())
        if supplier_obj.get_bs_name() != None and supplier_obj.get_bs_name() != "":
            condition &= Q(bsname=supplier_obj.get_bs_name())
        if supplier_obj.get_cc_name() != None and supplier_obj.get_cc_name() != "":
            condition &= Q(ccname=supplier_obj.get_cc_name())
        if supplier_obj.get_transactionmonth() != None and supplier_obj.get_transactionmonth() != "":
            condition &= Q(transactionmonth=supplier_obj.get_transactionmonth())
        if supplier_obj.get_quarter() != None and supplier_obj.get_quarter() != "":
            condition &= Q(quarter=supplier_obj.get_quarter())
        if supplier_obj.get_apinvoicebranch_id() != None and supplier_obj.get_apinvoicebranch_id() != "":
            condition &= Q(apinvoicebranch_id=supplier_obj.get_apinvoicebranch_id())
        ppr_obj = Pprdata.objects.using(self._current_app_schema()).filter(condition).values("apinvoice_id")
        if len(ppr_obj) <= 0:
            pass
        else:
            invoive_id = [0]
            for i in ppr_obj:
                invoive_id.append(i["apinvoice_id"])

            payload_ = {
                "Params": {
                    "invoive_ids": invoive_id
                }, "Classification": {
                    "Entity_Gid": "1",
                    "Create_By": "0ADMIN"
                }
            }

            token_ = "Bearer  " + get_authtoken()
            headers_ = {"content-type": "application/json", "Authorization": "" + token_ + ""}
            resp_ = requests.post("" + val_url + "pprMonoMicro_split?Group=Mono_Get&Action=Micro_mono_PPR_ecf",
                                  data=json.dumps(payload_),
                                  headers=headers_,
                                  verify=False).json()
            if len(resp_["DATA"]) <= 0:
                return json.dumps({"data": []})
            else:
                df = pd.DataFrame(resp_["DATA"])
                dataType = {"invoiceheader_gid":int,"invoiceheader_crno":str,"invoiceheader_invoicedate":str,"invoiceheader_invoiceno":str,
                            "invoiceheader_branchgid":str,"branch_code":str,"branch_name":str,"invoiceheader_amount":float}
                df = df.astype(dataType)
                df = df.assign(invoiceheader_amount=lambda x: (x['invoiceheader_amount'] / supplier_obj.get_divAmount()))
                return json.dumps({"data": df.to_dict(orient="records")})
        return json.dumps({"data": []})

    def Ecf_filesList(self,ecf_obj):
        payload_ = {
            "Params": {
                "pprdata_apinvoicegid": ecf_obj.get_invoiceheader_gid()
            }, "Classification": {
                "Entity_Gid": "1",
                "Create_By": "0ADMIN"
            }
        }
        token_ = "Bearer  " + get_authtoken()
        headers_ = {"content-type": "application/json", "Authorization": "" + token_ + ""}
        resp_ = requests.post("" + val_url + "pprMonoMicro_split?Group=Mono_Get&Action=Filelist_Fetch",
                              data=json.dumps(payload_),
                              headers=headers_,
                              verify=False).json()
        pro_list = NWisefinList()
        if len(resp_["DATA"]) <= 0:
            pass
        else:
            for i in resp_["DATA"]:
                response = PPRecfresponse()
                response.set_file_reftablegid(i['file_reftablegid'])
                response.set_file_isduplicate(i['file_isduplicate'])
                response.set_file_name(i['file_name'])
                response.set_file_path(i['file_path'])
                response.set_file_gid(i['file_gid'])
                response.set_ref_name(i['ref_name'])
                response.set_cr_no(ecf_obj.get_cr_no())
                response.set_invoiceheaderid(ecf_obj.get_invoiceheader_gid())
                pro_list.data.append(response)

        return pro_list


    def Ecf_FileDownload(self,file_name,cr_no,mono_fileid,mono_invoiceheaderid,empid):
        filter_obj = PPR_files.objects.using(self._current_app_schema()).filter(cr_no=cr_no,file_name=file_name,mono_file_id=mono_fileid,mono_invoiceheader_id=mono_invoiceheaderid,entity_id=self._entity_id()).exists()
        if filter_obj == True:
            file_obj = PPR_files.objects.using(self._current_app_schema()).filter(cr_no=cr_no,file_name=file_name,mono_file_id=mono_fileid,mono_invoiceheader_id=mono_invoiceheaderid)
            s3 = boto3.resource('s3')
            s3_obj = s3.Object(bucket_name=settings.BUCKET_NAME_FOR_ASSETS, key=file_obj[0].file_id)
            body = s3_obj.get()['Body']
            response = StreamingHttpResponse(body, content_type='application/octet-stream')
            response['Content-Disposition'] = 'inline; filename="{}"'.format(file_name)
            return response
        else:
            token_ = "Bearer  " + get_authtoken()
            headers_ = {"content-type": "application/json", "Authorization": "" + token_ + ""}
            resp_ = requests.get("" + val_url + "ppr_file_downloader/?filename=" + file_name, headers=headers_,
                                 verify=False)
            inmemory_content = io.BytesIO(resp_.content)
            file_name_new = "PPR_" + str(datetime.datetime.now().strftime("%y%m%d_%H%M%S")) + file_name
            s3 = boto3.resource('s3')
            s3_obj = s3.Object(bucket_name=settings.BUCKET_NAME_FOR_ASSETS, key=file_name_new)
            s3_obj.put(Body=inmemory_content)
            file_obj = PPR_files.objects.create(cr_no=cr_no,file_name=file_name,mono_file_id=mono_fileid,mono_invoiceheader_id=mono_invoiceheaderid,file_id=file_name_new,created_by=empid)
            file_obj.save()
            inmemory_content.seek(0)
            response = StreamingHttpResponse(inmemory_content, content_type='application/octet-stream')
            response['Content-Disposition'] = 'inline; filename="{}"'.format(file_name)
            return response

    def supplier_dropdown(self,request_obj):
        pprutility = VENDOR_SERVICE(self._scope())
        condition = Q(status=1, apexpense_id=request_obj.get_apexpense_id(),
                      apsubcat_id=request_obj.get_apsubcat_id(),
                      bizname=request_obj.get_masterbusinesssegment_name(),
                      sectorname=request_obj.get_sectorname(),entity_id=self._entity_id(),
                      finyear=request_obj.get_finyear())  # ,entry_module='AP'
        if request_obj.get_bs_name() != None and request_obj.get_bs_name() != "":
            condition &= Q(bsname=request_obj.get_bs_name())
        if request_obj.get_cc_name() != None and request_obj.get_cc_name() != "":
            condition &= Q(ccname=request_obj.get_cc_name())
        ppr_obj = Pprdata.objects.using(self._current_app_schema()).filter(condition).values("apinvoicesupplier_id")
        pro_list = NWisefinList()
        if len(ppr_obj) <= 0:
            pass
        else:
            supplier_ids = []
            for i in ppr_obj:
                supplier_ids.append(i['apinvoicesupplier_id'])
            supplier_detials = pprutility.get_supplier(supplier_ids)
            for i in ppr_obj:
                ppr_response = PprSupplierresponse()
                ppr_response.set_supplier_detial(supplier_detials, i["apinvoicesupplier_id"])
                pro_list.data.append(ppr_response)
        return pro_list

    def pprsupplier_dropdown(self, request_obj, query):
        pprutility = Ppr_utilityservice(self._scope())
        condition = Q(status=1, apexpense_id=request_obj.get_apexpense_id(),entity_id=self._entity_id(),
                      apsubcat_id=request_obj.get_apsubcat_id(),
                      bizname=request_obj.get_masterbusinesssegment_name(),
                      sectorname=request_obj.get_sectorname(),
                      finyear=request_obj.get_finyear())  # ,entry_module='AP'

        if request_obj.get_bs_name() != None and request_obj.get_bs_name() != "":
            condition &= Q(bsname=request_obj.get_bs_name())
        if request_obj.get_cc_name() != None and request_obj.get_cc_name() != "":
            condition &= Q(ccname=request_obj.get_cc_name())
        if request_obj.get_apinvoicebranch_id() != None and request_obj.get_apinvoicebranch_id() != "":
            condition &= Q(apinvoicebranch_id=request_obj.get_apinvoicebranch_id())
        bgtcondition = Q(apexpense_id=request_obj.get_apexpense_id(), apsubcat_id=request_obj.get_apsubcat_id(),
                         bizname=request_obj.get_masterbusinesssegment_name(), sectorname=request_obj.get_sectorname(),
                         finyear=f'FY{int(request_obj.get_finyear().split("-")[0][-2:]) + 1}-{int(request_obj.get_finyear().split("-")[1]) + 1}')
        if request_obj.get_bs_name() != None and request_obj.get_bs_name() != "":
            bgtcondition &= Q(bsname=request_obj.get_bs_name())
        if request_obj.get_cc_name() != None and request_obj.get_cc_name() != "":
            bgtcondition &= Q(ccname=request_obj.get_cc_name())
        if request_obj.get_apinvoicebranch_id() != None and request_obj.get_apinvoicebranch_id() != "":
            bgtcondition &= Q(apinvoicebranch_id=request_obj.get_apinvoicebranch_id())
        ppr_obj = Pprdata.objects.using(self._current_app_schema()).filter(bgtcondition).values(
            "apinvoicesupplier_id").annotate(count=Count('apinvoicesupplier_id')).order_by()
        bgt_obj = Budgetdetial.objects.using(self._current_app_schema()).filter(bgtcondition).values(
            "apinvoicesupplier_id").annotate(count=Count('apinvoicesupplier_id')).order_by()
        data = []
        for i in ppr_obj:
            data.append({"apinvoicesupplier_id":i["apinvoicesupplier_id"]})
        for i in bgt_obj:
            if {"apinvoicesupplier_id":i["apinvoicesupplier_id"]} not in data:
                data.append({"apinvoicesupplier_id":i["apinvoicesupplier_id"]})
        ppr_obj = data
        pro_list = NWisefinList()
        if len(ppr_obj) <= 0:
            pass
        else:
            supplier_ids = []
            for i in ppr_obj:
                supplier_ids.append(i['apinvoicesupplier_id'])
            supplier_service=VENDOR_SERVICE(self._scope())
            supplier_detials = supplier_service.supplier_list(supplier_ids, query)
            for i in ppr_obj:
                ppr_response = PprSupplierresponse()
                ppr_response.set_supplier_detial(supplier_detials, i["apinvoicesupplier_id"])
                if len(json.loads(ppr_response.get())) > 0:
                    pro_list.data.append(ppr_response)
        return pro_list



    def ppr_exp_cat_logic(self,ppr_obj):
        pprutility = MASTER_SERVICE(self._scope())
        pro_list = NWisefinList()
        if ppr_obj.get_expense_id() != None and ppr_obj.get_expense_id() != "":
            cat_obj = Apcategory.objects.using(self._current_app_schema()).filter(expense_id = ppr_obj.get_expense_id(),entity_id=self._entity_id())
            for cat in cat_obj:
                condition = Q(status=1,entity_id=self._entity_id())
                if ppr_obj.get_branch_id() != None and ppr_obj.get_branch_id() != "":
                    condition &= Q(apinvoicebranch_id=ppr_obj.get_branch_id())
                if ppr_obj.get_finyear() != None and ppr_obj.get_finyear() != "":
                    condition &= Q(finyear=ppr_obj.get_finyear())
                if ppr_obj.get_sector_name() != None and ppr_obj.get_sector_name() != "":
                    condition &= Q(sectorname=ppr_obj.get_sector_name())
                if ppr_obj.get_mstbusiness_segment_name() != None and ppr_obj.get_mstbusiness_segment_name() != "":
                    condition &= Q(bizname=ppr_obj.get_mstbusiness_segment_name())
                if ppr_obj.get_bs_name() != None and ppr_obj.get_bs_name() != "":
                    condition &= Q(bsname=ppr_obj.get_bs_name())
                if ppr_obj.get_expense_id() != None and ppr_obj.get_expense_id() != "":
                    condition &= Q(apexpense_id=ppr_obj.get_expense_id())
                if ppr_obj.get_cc_name() != None and ppr_obj.get_cc_name() != "":
                    condition &= Q(ccname=ppr_obj.get_cc_name())
                condition &= Q(categorygid=cat.id)
                if ppr_obj.get_year_term() == 'Monthly':
                    pprdata = Pprdata.objects.using(self._current_app_schema()).filter(condition).values('categorygid','apexpense_id',
                                                                                              'transactionmonth').annotate(
                        amount=Sum('amount'))
                if ppr_obj.get_year_term() == 'Quarterly':
                    pprdata = Pprdata.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id','categorygid',
                                                                                              'quarter').annotate(
                        amount=Sum('amount'))
                cat_ids = []
                cat_ids.append(cat.id)
                cat_detials = pprutility.get_category(cat_ids)

                if len(pprdata) == 0:
                    if ppr_obj.get_year_term() == 'Monthly':
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
                            pprresponser.set_amount(str(Decimal(0.0) / ppr_obj.get_divAmount()))
                            pprresponser.set_transactionmonth(tranmon)
                            pprresponser.set_cat_data(cat_detials, cat.id)
                            pro_list.data.append(pprresponser)
                            tranmon1 = tranmon1+1

                    if ppr_obj.get_year_term() == 'Quarterly':
                        tranmonth1 = 1
                        for f in range(0, 3):
                            tranmon = tranmonth1
                            pprresponser = pprresponse()
                            pprresponser.set_cat_data(cat_detials, cat.id)
                            pprresponser.set_amount(str(Decimal(0.0) / ppr_obj.get_divAmount()))
                            pprresponser.set_quarter(tranmon)
                            pro_list.data.append(pprresponser)
                            tranmonth1 = tranmonth1 + 1

                else:
                    for i in pprdata:
                        pprresponser = pprresponse()
                        pprresponser.set_cat_data(cat_detials, i['categorygid'])
                        pprresponser.set_amount(str(Decimal(i['amount']) / ppr_obj.get_divAmount()))
                        if ppr_obj.get_year_term() == 'Monthly':
                            pprresponser.set_transactionmonth(i["transactionmonth"])
                        if ppr_obj.get_year_term() == 'Quarterly':
                            pprresponser.set_quarter(i["quarter"])
                        pro_list.data.append(pprresponser)
        return pro_list

    # def new_expensegrp_masterlist(self, ppr_obj):
    #     pprutility = Ppr_utilityservice()
    #     pprdata = []
    #     pro_list = NWisefinList()
    #     expense_allobj = APexpensegroup.objects.filter(status=1)
    #     for ex_obj in expense_allobj:
    #         condition = Q(status=1)
    #         if ppr_obj.get_branch_id() != None and ppr_obj.get_branch_id() != "":
    #             condition &= Q(apinvoicebranch_id=ppr_obj.get_branch_id())
    #         if ppr_obj.get_finyear() != None and ppr_obj.get_finyear() != "":
    #             condition &= Q(finyear=ppr_obj.get_finyear())
    #         if ppr_obj.get_sector_name() != None and ppr_obj.get_sector_name() != "":
    #             condition &= Q(sectorname=ppr_obj.get_sector_name())
    #         if ppr_obj.get_mstbusiness_segment_name() != None and ppr_obj.get_mstbusiness_segment_name() != "":
    #             condition &= Q(bizname=ppr_obj.get_mstbusiness_segment_name())
    #         if ppr_obj.get_bs_name() != None and ppr_obj.get_bs_name() != "":
    #             condition &= Q(bsname=ppr_obj.get_bs_name())
    #         if ppr_obj.get_cc_name() != None and ppr_obj.get_cc_name() != "":
    #             condition &= Q(ccname=ppr_obj.get_cc_name())
    #         if ppr_obj.get_expensegrp_name_arr() != None and ppr_obj.get_expensegrp_name_arr() != "" and len(
    #                 ppr_obj.get_expensegrp_name_arr()) > 0:
    #             expense_val = pprutility.get_expense_expensegrp(ppr_obj.get_expensegrp_name_arr())
    #             condition &= Q(apexpense_id__in=expense_val)
    #         else:
    #             expense_val = APexpense.objects.filter(exp_grp_id=ex_obj.id).values_list('id', flat=True)
    #             condition &= Q(apexpense_id__in=expense_val)
    #         exname = []
    #         exname.append(ex_obj.name)
    #         print(condition)
    #         if ppr_obj.get_year_term() == 'Monthly':
    #             pprdata = Pprdata.objects.using(DataBase.fas_db).filter(condition).values('apexpense_id',
    #                                                                                       'transactionmonth').annotate(
    #                 amount=Sum('amount'))
    #         if ppr_obj.get_year_term() == 'Quarterly':
    #             pprdata = Pprdata.objects.using(DataBase.fas_db).filter(condition).values('apexpense_id',
    #                                                                                       'quarter').annotate(
    #                 amount=Sum('amount'))
    #         expense_detials = pprutility.get_expense(expense_val)
    #         if len(pprdata) == 0:
    #             for k in expense_detials:
    #                 if ppr_obj.get_year_term() == 'Monthly':
    #                     tranmon1 = 4
    #                     for f in range(0, 12):
    #                         tranmon = tranmon1
    #                         if tranmon1 == 13:
    #                             tranmon = 1
    #                         if tranmon1 == 14:
    #                             tranmon = 2
    #                         if tranmon1 == 15:
    #                             tranmon = 3
    #                         pprresponser = pprresponse()
    #                         pprresponser.set_expense_data(expense_detials, k['expense_id'])
    #                         pprresponser.set_amount(str(Decimal(0.0) / ppr_obj.get_divAmount()))
    #                         if ppr_obj.get_year_term() == 'Monthly':
    #                             pprresponser.set_transactionmonth(tranmon)
    #                         pro_list.data.append(pprresponser)
    #                         tranmon1 = tranmon1 + 1
    #                 if ppr_obj.get_year_term() == 'Quarterly':
    #                     tranmonth1 = 1
    #                     for f in range(0, 4):
    #                         tranmon = tranmonth1
    #                         pprresponser = pprresponse()
    #                         pprresponser.set_expense_data(expense_detials, k['expense_id'])
    #                         pprresponser.set_amount(str(Decimal(0.0) / ppr_obj.get_divAmount()))
    #                         pprresponser.set_quarter(tranmon)
    #                         pro_list.data.append(pprresponser)
    #                         tranmonth1 = tranmonth1 + 1
    #
    #         else:
    #                 for i in pprdata:
    #                     pprresponser = pprresponse()
    #                     pprresponser.set_expense_data(expense_detials, i["apexpense_id"])
    #                     pprresponser.set_amount(str(Decimal(i['amount']) / ppr_obj.get_divAmount()))
    #                     if ppr_obj.get_year_term() == 'Monthly':
    #                         pprresponser.set_transactionmonth(i["transactionmonth"])
    #                     if ppr_obj.get_year_term() == 'Quarterly':
    #                         pprresponser.set_quarter(i["quarter"])
    #                     pro_list.data.append(pprresponser)
    #                     # vpage = PPRNWisefinPaginator(pprdata, vys_page.get_index(), 5)
    #                     # pro_list.set_pagination(vpage)
    #     return pro_list
    #

    def new_cat_logic(self, expense_data, ppr_obj):
        expense_data = json.loads(expense_data)
        keys = Pprutility_keys()
        output = []
        if len(expense_data['data']) <= 0:
            pass
        else:
            year_term = ppr_obj.get_year_term()
            if year_term == "Monthly":
                month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            elif year_term == "Quarterly":
                month = ["Quarterly_1", "Quarterly_2", "Quarterly_3", "Quarterly_4"]
            else:
                return {"message": Pprdata_warning.month_quaterneed}

            uniqexpenseid = self.remove_duplicate_arrdict(expense_data['data'], '', keys.cat_id, '')
            uniqexpenselen = len(uniqexpenseid) - 1

            for index, id in enumerate(uniqexpenseid):
                row = {}
                row[keys.cat_id] = id
                self.get_monthsdict(row, month, Decimal(round(Decimal('0.00'), 2)))
                for uniq_month in expense_data['data']:
                    if id == uniq_month[keys.cat_id]:
                        if year_term == "Monthly":
                            if row[month[int(uniq_month[keys.transactionmonth]) - 1]] != Decimal(
                                    round(Decimal('0.00'), 2)):
                                row[month[int(uniq_month[keys.transactionmonth]) - 1]] = row[month[
                                    int(uniq_month[keys.transactionmonth]) - 1]] + Decimal(
                                    round(Decimal(uniq_month[keys.amount]), 2))
                            else:
                                row[month[int(uniq_month[keys.transactionmonth]) - 1]] = Decimal(
                                    round(Decimal(uniq_month[keys.amount]), 2))
                        if year_term == "Quarterly":
                            if row[f"Quarterly_{uniq_month[keys.quarter]}"] != Decimal(
                                    round(Decimal('0.00'), 2)) and f"Quarterly_{uniq_month[keys.quarter]}" in month:
                                row[f"Quarterly_{uniq_month[keys.quarter]}"] = row[
                                                                                   f"Quarterly_{uniq_month[keys.quarter]}"] + Decimal(
                                    round(Decimal(uniq_month[keys.amount]), 2))
                            else:
                                row[f"Quarterly_{uniq_month[keys.quarter]}"] = Decimal(
                                    round(Decimal(uniq_month[keys.amount]), 2))
                        row[keys.name] = uniq_month[keys.categoryname]
                        if index == uniqexpenselen:
                            row['page'] = 'Y'
                totalsum = Decimal(round(Decimal('0.00'), 2))
                for sumof_month in month:
                    totalsum = totalsum + row[sumof_month]
                row[keys.YTD] = totalsum
                row['tree_flag'] = 'Y'
                row[keys.Padding_left] = '75px'
                row[keys.Padding] = '5px'
                output.append(row)
        return {"data": output}

    def ppr_exp_subcat_logic(self, ppr_obj):
        pprutility = MASTER_SERVICE(self._scope())
        pro_list = NWisefinList()
        if ppr_obj.get_category_id() != None and ppr_obj.get_category_id() != "":
            subcat_obj = APsubcategory.objects.using(self._current_app_schema()).filter(category=ppr_obj.get_category_id(),entity_id=self._entity_id())
            for subcat in subcat_obj:
                condition = Q(status=1,entity_id=self._entity_id())
                if ppr_obj.get_branch_id() != None and ppr_obj.get_branch_id() != "":
                    condition &= Q(apinvoicebranch_id=ppr_obj.get_branch_id())
                if ppr_obj.get_finyear() != None and ppr_obj.get_finyear() != "":
                    condition &= Q(finyear=ppr_obj.get_finyear())
                if ppr_obj.get_sector_name() != None and ppr_obj.get_sector_name() != "":
                    condition &= Q(sectorname=ppr_obj.get_sector_name())
                if ppr_obj.get_mstbusiness_segment_name() != None and ppr_obj.get_mstbusiness_segment_name() != "":
                    condition &= Q(bizname=ppr_obj.get_mstbusiness_segment_name())
                if ppr_obj.get_bs_name() != None and ppr_obj.get_bs_name() != "":
                    condition &= Q(bsname=ppr_obj.get_bs_name())
                if ppr_obj.get_cc_name() != None and ppr_obj.get_cc_name() != "":
                    condition &= Q(ccname=ppr_obj.get_cc_name())
                condition &= Q(apsubcat_id=subcat.id)
                if ppr_obj.get_year_term() == 'Monthly':
                    pprdata = Pprdata.objects.using(self._current_app_schema()).filter(condition).values('categorygid',
                                                                                              'apsubcat_id',
                                                                                              'transactionmonth').annotate(
                        amount=Sum('amount'))
                if ppr_obj.get_year_term() == 'Quarterly':
                    pprdata = Pprdata.objects.using(self._current_app_schema()).filter(condition).values(
                        'categorygid', 'apsubcat_id',
                        'quarter').annotate(
                        amount=Sum('amount'))
                subcat_ids = []
                subcat_ids.append(subcat.id)
                subcat_details = pprutility.get_cat_subcat(subcat_ids)
                if len(pprdata) == 0:
                    if ppr_obj.get_year_term() == 'Monthly':
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
                            pprresponser.set_amount(str(Decimal(0.0) / ppr_obj.get_divAmount()))
                            if ppr_obj.get_year_term() == 'Monthly':
                                pprresponser.set_transactionmonth(tranmon)
                            pro_list.data.append(pprresponser)
                            tranmon1 = tranmon1 + 1
                    if ppr_obj.get_year_term() == 'Quarterly':
                        tranmon1 = 1
                        for f in range(0, 4):
                            tranmon = tranmon1
                            pprresponser = pprresponse()
                            pprresponser.set_subcat_cat_data(subcat_details, subcat.id)
                            pprresponser.set_amount(str(Decimal(0.0) / ppr_obj.get_divAmount()))
                            pprresponser.set_quarter(tranmon)
                            pro_list.data.append(pprresponser)
                            tranmon1 = tranmon1 + 1
                else:
                    for i in pprdata:
                        pprresponser = pprresponse()
                        pprresponser.set_subcat_data(subcat_details, i['apsubcat_id'])
                        pprresponser.set_amount(str(Decimal(i['amount']) / ppr_obj.get_divAmount()))
                        if ppr_obj.get_year_term() == 'Monthly':
                            pprresponser.set_transactionmonth(i["transactionmonth"])
                        if ppr_obj.get_year_term() == 'Quarterly':
                            pprresponser.set_quarter(i["quarter"])
                        pro_list.data.append(pprresponser)
        return pro_list

    # def new_expense_masterlist(self, ppr_obj):  # vys_page
    #     pprutility = Ppr_utilityservice()
    #     pro_list = NWisefinList()
    #     if ppr_obj.get_expensegrp_name_arr() != None and ppr_obj.get_expensegrp_name_arr() != "":
    #         expense_id = pprutility.get_new_expense_expensegrp(ppr_obj.get_expensegrp_name_arr())
    #
    #         pprdata = []
    #         for expense_val in expense_id:
    #             condition = Q(status=1)  # ,entry_module='AP'
    #             if ppr_obj.get_branch_id() != None and ppr_obj.get_branch_id() != "":
    #                 condition &= Q(apinvoicebranch_id=ppr_obj.get_branch_id())
    #             if ppr_obj.get_finyear() != None and ppr_obj.get_finyear() != "":
    #                 condition &= Q(finyear=ppr_obj.get_finyear())
    #             if ppr_obj.get_sector_name() != None and ppr_obj.get_sector_name() != "":
    #                 condition &= Q(sectorname=ppr_obj.get_sector_name())
    #             if ppr_obj.get_mstbusiness_segment_name() != None and ppr_obj.get_mstbusiness_segment_name() != "":
    #                 condition &= Q(bizname=ppr_obj.get_mstbusiness_segment_name())
    #             if ppr_obj.get_bs_name() != None and ppr_obj.get_bs_name() != "":
    #                 condition &= Q(bsname=ppr_obj.get_bs_name())
    #             if ppr_obj.get_cc_name() != None and ppr_obj.get_cc_name() != "":
    #                 condition &= Q(ccname=ppr_obj.get_cc_name())
    #
    #             condition &= Q(apexpense_id=expense_val)
    #             if ppr_obj.get_year_term() == 'Monthly':
    #                 pprdata = Pprdata.objects.using(DataBase.fas_db).filter(condition).values('apexpense_id',
    #                                                                                           'transactionmonth').annotate(
    #                     amount=Sum('amount'))
    #                 # [vys_page.get_offset():vys_page.get_query_limit()]
    #             if ppr_obj.get_year_term() == 'Quarterly':
    #                 pprdata = Pprdata.objects.using(DataBase.fas_db).filter(condition).values('apexpense_id',
    #                                                                                           'quarter').annotate(
    #                     amount=Sum('amount'))
    #                 # [vys_page.get_offset():vys_page.get_query_limit()]
    #             expense_ids = []
    #             # for i in pprdata:
    #             expense_ids.append(expense_val)
    #             expense_detials = pprutility.get_expense(expense_ids)
    #             if len(pprdata) == 0:
    #                 for k in expense_val:
    #                     if ppr_obj.get_year_term() == 'Monthly':
    #                         tranmon1 = 4
    #                         for f in range(0, 12):
    #                             tranmon = tranmon1
    #                             if tranmon1 == 13:
    #                                 tranmon = 1
    #                             if tranmon1 == 14:
    #                                 tranmon = 2
    #                             if tranmon1 == 15:
    #                                 tranmon = 3
    #                             pprresponser = pprresponse()
    #                             pprresponser.set_expense_data(expense_detials, k)
    #                             pprresponser = pprresponse()
    #                             pprresponser.set_expense_data(expense_detials, expense_val)
    #                             pprresponser.set_amount(str(Decimal(0.0) / ppr_obj.get_divAmount()))
    #                             if ppr_obj.get_year_term() == 'Monthly':
    #                                 pprresponser.set_transactionmonth(tranmon)
    #                             pro_list.data.append(pprresponser)
    #                             tranmon1 = tranmon1 + 1
    #                     if ppr_obj.get_year_term() == 'Quarterly':
    #                         tranmon1 = 1
    #                         for f in range(0, 4):
    #                             tranmon = tranmon1
    #                             pprresponser = pprresponse()
    #                             pprresponser.set_expense_data(expense_detials, k)
    #                             pprresponser.set_amount(str(Decimal(0.0) / ppr_obj.get_divAmount()))
    #                             pprresponser.set_quarter(tranmon)
    #                             pro_list.data.append(pprresponser)
    #                             tranmon1 = tranmon1 + 1
    #
    #             else:
    #                 for i in pprdata:
    #                     pprresponser = pprresponse()
    #                     # pprresponser.expense_id=1
    #                     # pprresponser.expensename=(expense_detials, i["apexpense_id"])
    #                     # pprresponser.exp ensegrpname=(expense_detials, i["apexpense_id"])
    #                     pprresponser.set_expense_data(expense_detials, i["apexpense_id"])
    #                     a = pprresponser.set_expense_datacheck(expense_detials, i["apexpense_id"])
    #                     if a == True:
    #                         pprresponser.set_amount(str(Decimal(i['amount']) / ppr_obj.get_divAmount()))
    #                     else:
    #                         pprresponser.set_amount(str(Decimal(0.0) / ppr_obj.get_divAmount()))
    #                     if ppr_obj.get_year_term() == 'Monthly':
    #                         pprresponser.set_transactionmonth(i["transactionmonth"])
    #                     if ppr_obj.get_year_term() == 'Quarterly':
    #                         pprresponser.set_quarter(i["quarter"])
    #                     pro_list.data.append(pprresponser)
    #
    #     return pro_list

    def new_expensegrp_masterlist(self, ppr_obj,flag):
        pprutility = MASTER_SERVICE(self._scope())
        pprdata = []
        pro_list = NWisefinList()
        is_con=Q(status=1,entity_id=self._entity_id())
        if flag=="N":
            is_con &=~Q(name='Assets')
        else:
            is_con &=Q(name='Assets')
        expense_allobj = APexpensegroup.objects.using(self._current_app_schema()).filter(is_con)
        for ex_obj in expense_allobj:
            condition = Q(status=1)
            if ppr_obj.get_branch_id() != None and ppr_obj.get_branch_id() != "":
                condition &= Q(apinvoicebranch_id=ppr_obj.get_branch_id())
            if ppr_obj.get_finyear() != None and ppr_obj.get_finyear() != "":
                condition &= Q(finyear=ppr_obj.get_finyear())
            if ppr_obj.get_sector_name() != None and ppr_obj.get_sector_name() != "":
                condition &= Q(sectorname=ppr_obj.get_sector_name())
            if ppr_obj.get_mstbusiness_segment_name() != None and ppr_obj.get_mstbusiness_segment_name() != "":
                condition &= Q(bizname=ppr_obj.get_mstbusiness_segment_name())
            if ppr_obj.get_bs_name() != None and ppr_obj.get_bs_name() != "":
                condition &= Q(bsname=ppr_obj.get_bs_name())
            if ppr_obj.get_cc_name() != None and ppr_obj.get_cc_name() != "":
                condition &= Q(ccname=ppr_obj.get_cc_name())
            if ppr_obj.get_expensegrp_name_arr() != None and ppr_obj.get_expensegrp_name_arr() != "" and len(
                    ppr_obj.get_expensegrp_name_arr()) > 0:
                expense_val = pprutility.get_expense_expensegrp(ppr_obj.get_expensegrp_name_arr())
                condition &= Q(apexpense_id__in=expense_val)
            else:
                expense_val = APexpense.objects.using(self._current_app_schema()).filter(group__icontains=ex_obj.name,entity_id=self._entity_id()).values_list('id', flat=True)
                condition &= Q(apexpense_id__in=expense_val)
            exname = []
            exname.append(ex_obj.name)
            print(condition)
            if ppr_obj.get_year_term() == 'Monthly':
                pprdata = Pprdata.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id',
                                                                                          'transactionmonth').annotate(
                    amount=Sum('amount'))
            if ppr_obj.get_year_term() == 'Quarterly':
                pprdata = Pprdata.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id',
                                                                                          'quarter').annotate(
                    amount=Sum('amount'))
            expense_detials = pprutility.get_expense(expense_val)
            if len(pprdata) == 0:
                for k in expense_val:
                    if ppr_obj.get_year_term() == 'Monthly':
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
                            pprresponser.set_expense_data(expense_detials, k)
                            pprresponser.set_amount(str(Decimal(0.0) / ppr_obj.get_divAmount()))
                            if ppr_obj.get_year_term() == 'Monthly':
                                pprresponser.set_transactionmonth(tranmon)
                            pro_list.data.append(pprresponser)
                            tranmon1 = tranmon1 + 1
                    if ppr_obj.get_year_term() == 'Quarterly':
                        if ppr_obj.get_year_term() == 'Monthly':
                            tranmon1 = 1
                            for f in range(0, 4):
                                tranmon=tranmon1
                                pprresponser = pprresponse()
                                pprresponser.set_expense_data(expense_detials, k)
                                pprresponser.set_amount(str(Decimal(0.0) / ppr_obj.get_divAmount()))
                                pprresponser.set_quarter(tranmon)
                                pro_list.data.append(pprresponser)
                                tranmon1 = tranmon1 + 1

            else:
                for i in pprdata:
                    pprresponser = pprresponse()
                    # pprresponser.expense_id=1
                    # pprresponser.expensename=(expense_detials, i["apexpense_id"])
                    # pprresponser.exp ensegrpname=(expense_detials, i["apexpense_id"])
                    pprresponser.set_expense_data(expense_detials, i["apexpense_id"])
                    a = pprresponser.set_expense_datacheck(expense_detials, i["apexpense_id"])
                    if a == True:
                        pprresponser.set_amount(str(Decimal(i['amount']) / ppr_obj.get_divAmount()))
                    else:
                        pprresponser.set_amount(str(Decimal(0.0) / ppr_obj.get_divAmount()))
                    if ppr_obj.get_year_term() == 'Monthly':
                        pprresponser.set_transactionmonth(i["transactionmonth"])
                    if ppr_obj.get_year_term() == 'Quarterly':
                        pprresponser.set_quarter(i["quarter"])
                    pro_list.data.append(pprresponser)

        return pro_list

    def new_expense_masterlist(self, ppr_obj):  # vys_page
        pprutility = MASTER_SERVICE(self._scope())
        pro_list = NWisefinList()
        if ppr_obj.get_expensegrp_name_arr() != None and ppr_obj.get_expensegrp_name_arr() != "":
            expense_id = pprutility.get_new_expense_expensegrp(ppr_obj.get_expensegrp_name_arr())

            pprdata = []
            for expense_val in expense_id:
                condition = Q(status=1,entity_id=self._entity_id())  # ,entry_module='AP'
                if ppr_obj.get_branch_id() != None and ppr_obj.get_branch_id() != "":
                    condition &= Q(apinvoicebranch_id=ppr_obj.get_branch_id())
                if ppr_obj.get_finyear() != None and ppr_obj.get_finyear() != "":
                    condition &= Q(finyear=ppr_obj.get_finyear())
                if ppr_obj.get_sector_name() != None and ppr_obj.get_sector_name() != "":
                    condition &= Q(sectorname=ppr_obj.get_sector_name())
                if ppr_obj.get_mstbusiness_segment_name() != None and ppr_obj.get_mstbusiness_segment_name() != "":
                    condition &= Q(bizname=ppr_obj.get_mstbusiness_segment_name())
                if ppr_obj.get_bs_name() != None and ppr_obj.get_bs_name() != "":
                    condition &= Q(bsname=ppr_obj.get_bs_name())
                if ppr_obj.get_cc_name() != None and ppr_obj.get_cc_name() != "":
                    condition &= Q(ccname=ppr_obj.get_cc_name())
                # if ppr_obj.get_expensegrp_name_arr() != None and ppr_obj.get_expensegrp_name_arr() != "":
                #     expense_ids = pprutility.get_new_expense_expensegrp(ppr_obj.get_expensegrp_name_arr())
                condition &= Q(apexpense_id=expense_val)
                if ppr_obj.get_year_term() == 'Monthly':
                    pprdata = Pprdata.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id',
                                                                                              'transactionmonth').annotate(
                        amount=Sum('amount'))
                    # [vys_page.get_offset():vys_page.get_query_limit()]
                if ppr_obj.get_year_term() == 'Quarterly':
                    pprdata = Pprdata.objects.using(self._current_app_schema()).filter(condition).values('apexpense_id',
                                                                                              'quarter').annotate(
                        amount=Sum('amount'))
                    # [vys_page.get_offset():vys_page.get_query_limit()]
                expense_ids = []
                # for i in pprdata:
                expense_ids.append(expense_val)
                expense_detials = pprutility.get_expense(expense_ids)
                if len(pprdata) == 0:
                    if ppr_obj.get_year_term() == 'Monthly':
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
                            pprresponser.set_expense_data(expense_detials, expense_val)
                            pprresponser.set_amount(str(Decimal(0.0) / ppr_obj.get_divAmount()))
                            if ppr_obj.get_year_term() == 'Monthly':
                                pprresponser.set_transactionmonth(tranmon)
                            pro_list.data.append(pprresponser)
                            tranmon1 = tranmon1 + 1
                    if ppr_obj.get_year_term() == 'Quarterly':
                        tranmon1 = 1
                        for f in range(0, 4):
                            tranmon = tranmon1
                            pprresponser = pprresponse()
                            pprresponser.set_expense_data(expense_detials, expense_val)
                            pprresponser.set_amount(str(Decimal(0.0) / ppr_obj.get_divAmount()))
                            pprresponser.set_quarter(tranmon)
                            pro_list.data.append(pprresponser)
                            tranmon1 = tranmon1 + 1

                else:
                    for i in pprdata:
                        pprresponser = pprresponse()
                        pprresponser.set_expense_data(expense_detials, i["apexpense_id"])
                        pprresponser.set_amount(str(Decimal(i['amount']) / ppr_obj.get_divAmount()))
                        if ppr_obj.get_year_term() == 'Monthly':
                            pprresponser.set_transactionmonth(i["transactionmonth"])
                        if ppr_obj.get_year_term() == 'Quarterly':
                            pprresponser.set_quarter(i["quarter"])
                        pro_list.data.append(pprresponser)
                # vpage = PPRNWisefinPaginator(pprdata, vys_page.get_index(), 5)
                # pro_list.set_pagination(vpage)
            return pro_list

