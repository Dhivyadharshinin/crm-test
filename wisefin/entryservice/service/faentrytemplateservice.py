import json

import pandas as pd
#from vysfinutility.data.vysfinlist import VysfinList

from entryservice.models.entrymodels import Entry,ParameterTables,ParameterName,EntryTemplate
from entryservice.data.response.entryparamtemplateresponse import ParamtemplateResponse, EntryTemplateResponse, \
    DebitList, ParamnametemplateResponse, templatenameResponse, CreditList
from django.db.models import Q
from django.utils.timezone import now
from nwisefin.settings import DATABASES
from nwisefin.settings import logger
from django.db import transaction
from datetime import datetime,timedelta
# from vysfinutility.data.error import Error
# from vysfinutility.data.error_const import ErrorDescription,ErrorMessage
from django.db import IntegrityError, connection
from entryservice.util.entryutil import EntryType, APDBService, MASTERDBService, VENDORDBService, FADBService
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.entry_api_service import ApiService
import traceback

class FATemplateService(NWisefinThread):

    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ENTRY_SERVICE)

    def FAquerycondition_check(self,id,module_name,emp_id,scope):
        ###set schema Name
        ap_db = APDBService(scope)
        Dynamic_schema=ap_db.get_ap_schema()
        DB_NAME_apdb=DATABASES.get(Dynamic_schema).get("NAME")

        mst_db = MASTERDBService(scope)
        Dynamicmst_schema = mst_db.get_master_schema()
        DB_NAME_masterdb = DATABASES.get(Dynamicmst_schema).get("NAME")

        vendor_db = VENDORDBService(scope)
        Dynamicven_schema = vendor_db.get_vendor_schema()
        DB_NAME_vendordb = DATABASES.get(Dynamicven_schema).get("NAME")

        vendor_db = FADBService(scope)
        Dynamicven_schema = vendor_db.get_fa_schema()
        DB_NAME_fadb = DATABASES.get(Dynamicven_schema).get("NAME")

        logger.info('ENTRY_LOGGER - ' + str(DB_NAME_apdb),str(DB_NAME_masterdb),str(DB_NAME_vendordb))

        # Dynamic_query=()
        condition = Q(code=module_name)
        parameter_name= ParameterName.objects.using(self._current_app_schema()).filter(condition)
        #params_id=parameter_name[0]['id']
        params_id=parameter_name[0].id
        columnname_and_values=""
        # for i in parameter_name:
        #     import ast
        #     columnnamedebit1=json.loads(json.dumps(i.columnnamedebit))
        #     columnnamedebit = ast.literal_eval(columnnamedebit1)
        #     #print(columnnamedebit)
        #     for j in columnnamedebit:
        #         columnname=j['columnname']
        #         sourcekey=j['source_key']
        #         sourcevalue=j['source_value']
        #         if columnname_and_values == '':
        #             columnname_and_values = columnname+'='+"'"+sourcevalue+"'"
        #         else:
        #             columnname_and_values+= " and "+columnname+'=' + "'" +sourcevalue +"'"
        # logger.info('ENTRY_LOGGER - ' + str(columnname_and_values))
        Dynamic_query = (
            " select assetdetails_cost from "+str(DB_NAME_fadb)+". faservice_assetdetails"
            " where id='"+str(id)+"' ")
            #" and '"+str(columnname)+"' = '"+str(sourcevalue)+"'  ")
        logger.info('ENTRY_LOGGER - ' + str(Dynamic_query))
        #print(Dynamic_query)
        with connection.cursor() as cursor:
            cursor.execute(Dynamic_query)
            columns = [x[0] for x in cursor.description]
            rows = cursor.fetchall()
            rows = list(rows)
            df_data = pd.DataFrame(rows, columns=columns)
            resp = {"Message":"Found","DATA": json.loads(df_data.to_json(orient='records'))}
            if(len(resp['DATA'])==0):
                error_obj = NWisefinError()
                error_obj.set_code('INVALID_PARAMETER')
                error_obj.set_description('PLEASE GIVE CORRECT PARAMETER')
                return error_obj
            else:
                a=resp['DATA']
                amount=a[0]['assetdetails_cost']
                sgst=0
                cgst=0
                igst=0
                totalamount=0

                condition = Q(parametername_id=params_id) & Q(transaction='DEBIT')
                entrytemplate_details = EntryTemplate.objects.using(self._current_app_schema()).filter(condition)
                list_length = len(entrytemplate_details)
                #entry_list_data = NWisefinList()
                entry_list_data=DebitList()
                if list_length <= 0:
                    pass
                else:
                    for entry_val in entrytemplate_details:
                        valuetotaken=entry_val.value_to_taken
                        BASEAMOUNT=amount
                        #DEBITAMOUNT=apdebitamount
                        CGST=cgst
                        SGST=sgst
                        IGST=igst
                        import re
                        print(re.findall('\W+|\w+', valuetotaken))
                        split_formula = re.findall('\W+|\w+', valuetotaken)

                        concat_val=''
                        li_val=['BASEAMOUNT','CGST','SGST','IGST','INVAMOUT']
                        li_val1=['BASEAMOUNT','CGST','SGST','IGST','INVAMOUT']
                        chkval_ind = 0
                        for i in split_formula:
                            if i not in li_val1:
                                if chkval_ind==0:
                                    concat_val=i
                                else:
                                    concat_val=str(concat_val)+i
                            else:
                                chkval_ind1 = 0
                                for j in li_val:

                                    if chkval_ind1==0:
                                        if i=='BASEAMOUNT':
                                            li_val.remove("BASEAMOUNT")
                                            if chkval_ind == 0:
                                                concat_val=str(BASEAMOUNT)

                                                # concat_val=int(INVAMT)
                                            else:
                                                concat_val = str(concat_val) + str(BASEAMOUNT)
                                                # concat_val = str(concat_val) + int(INVAMT)
                                        if i=='CGST':
                                            li_val.remove("CGST")
                                            if chkval_ind == 0:
                                                concat_val=str(CGST)

                                                # concat_val=int(CGST)
                                            else:
                                                concat_val = str(concat_val) + str(CGST)
                                                # concat_val = str(concat_val) + int(CGST)
                                            # concat_val=int(CGST)
                                        if i=='SGST':
                                            li_val.remove("SGST")
                                            if chkval_ind == 0:
                                                concat_val=str(SGST)
                                                # concat_val=int(SGST)
                                            else:
                                                concat_val = str(concat_val) + str(SGST)
                                        if i== 'IGST':
                                            li_val.remove("IGST")
                                            if chkval_ind == 0:
                                                concat_val = str(IGST)
                                                # concat_val=int(SGST)
                                            else:
                                                concat_val = str(concat_val) + str(IGST)
                                        # if i== 'DEBITAMOUNT':
                                        #     li_val.remove("DEBITAMOUNT")
                                        #     if chkval_ind == 0:
                                        #         concat_val = str(DEBITAMOUNT)
                                        #         # concat_val=int(SGST)
                                        #     else:
                                        #         concat_val = str(concat_val) + str(DEBITAMOUNT)
                                        if i == 'INVAMOUT':
                                            concat_val = '0'
                                        chkval_ind1=chkval_ind1+1
                                                # concat_val = str(concat_val) + int(SGST)
                                            # concat_val=int(SGST)

                            chkval_ind = chkval_ind + 1
                        formula_amt = concat_val
                        logger.info('ENTRY_LOGGER - ' + str(formula_amt))

                        addition = eval(formula_amt)
                        sumofamt=round(addition, 2)
                        logger.info('ENTRY_LOGGER - ' + str(sumofamt))

                        for_values=entry_val.value_to_taken
                        entry_data = EntryTemplateResponse()
                        entry_data.set_id(entry_val.id)
                        entry_data.set_gl_no(entry_val.gl_no)
                        entry_data.set_transaction(entry_val.transaction)
                        entry_data.set_Values(entry_val.Values)
                        #entry_data.set_value_to_taken(entry_val.value_to_taken)
                        entry_data.set_wisefin_category(entry_val.wisefin_category)
                        entry_data.set_wisefin_subcategory(entry_val.wisefin_subcategory)
                        entry_data.set_display(entry_val.display)
                        entry_data.amount=sumofamt
                        entry_data.invheaderamount=totalamount
                        # entry_data.cgst=cgst
                        entry_list_data.append(entry_data)
                        # vpage = VysfinPaginator(entrydetails, vys_page.get_index(), 10)
                        # entry_list_data.set_pagination(vpage)
                return entry_list_data
    def FAqueryconditioncr_check(self,id,module_name,emp_id,scope):
        ##set dynamic schema name
        ap_db = APDBService(scope)
        Dynamic_schema = ap_db.get_ap_schema()
        DB_NAME_apdb = DATABASES.get(Dynamic_schema).get("NAME")

        mst_db = MASTERDBService(scope)
        Dynamicmst_schema = mst_db.get_master_schema()
        DB_NAME_masterdb = DATABASES.get(Dynamicmst_schema).get("NAME")

        vendor_db = VENDORDBService(scope)
        Dynamicven_schema = vendor_db.get_vendor_schema()
        DB_NAME_vendordb = DATABASES.get(Dynamicven_schema).get("NAME")

        vendor_db = FADBService(scope)
        Dynamicven_schema = vendor_db.get_fa_schema()
        DB_NAME_fadb = DATABASES.get(Dynamicven_schema).get("NAME")
        ######
        condition = Q(code=module_name)
        parameter_name= ParameterName.objects.using(self._current_app_schema()).filter(condition)
        params_id=parameter_name[0].id
        columnname_and_values=""
        # for i in parameter_name:
        #     import ast
        #     columnnamedebit1=json.loads(json.dumps(i.columnnamedebit))
        #     columnnamedebit = ast.literal_eval(columnnamedebit1)
        #     for j in columnnamedebit:
        #         columnname=j['columnname']
        #         sourcekey=j['source_key']
        #         sourcevalue=j['source_value']
        #         if columnname_and_values == '':
        #             columnname_and_values = columnname+'='+"'"+sourcevalue+"'"
        #         else:
        #             columnname_and_values+= " and "+columnname+'=' + "'" +sourcevalue +"'"
        #"inner join nentry.entryservice_parametername z on z.code='" + str(module_name) + "' " z.id as paramid,
        logger.info('ENTRY_LOGGER - ' + str(columnname_and_values))
        Dynamic_query = (
            " select assetdetails_cost from "+str(DB_NAME_fadb)+". faservice_assetdetails"
            " where id='"+str(id)+"' ")
            #" and '"+str(columnname)+"' = '"+str(sourcevalue)+"'  ")

        #print(Dynamic_query)
        logger.info('ENTRY_LOGGER - ' + str(Dynamic_query))
        with connection.cursor() as cursor:
            cursor.execute(Dynamic_query)
            columns = [x[0] for x in cursor.description]
            rows = cursor.fetchall()
            rows = list(rows)
            df_data = pd.DataFrame(rows, columns=columns)
            resp = {"Message":"Found","DATA": json.loads(df_data.to_json(orient='records'))}
            if(len(resp['DATA'])==0):
                error_obj = NWisefinError()
                error_obj.set_code('INVALID_PARAMETER')
                error_obj.set_description('PLEASE GIVE CORRECT PARAMETER')
                return error_obj
            else:

                #params_id=a[0]['paramid']
                condition = Q(parametername_id=params_id) & Q(transaction='CREDIT')
                entrytemplate_details = EntryTemplate.objects.using(self._current_app_schema()).filter(condition)

                list_length = len(entrytemplate_details)
                entry_list_data=CreditList()
                if list_length <= 0:
                    pass
                else:
                    a = resp['DATA']
                    amount = a[0]['assetdetails_cost']
                    sgst = 0
                    cgst = 0
                    igst = 0
                    totalamount =0
                    logger.info('ENTRY_LOGGER - ' + str(a),str(totalamount))
                    for entry_val in entrytemplate_details:
                        a = resp['DATA']
                        valuetotaken=entry_val.value_to_taken
                        BASEAMOUNT=amount
                        CGST=cgst
                        SGST=sgst
                        IGST=igst
                        INVAMOUT=totalamount
                        import re
                        split_formula = re.findall('\W+|\w+', valuetotaken)
                        logger.info('ENTRY_LOGGER - ' + str(split_formula))
                        concat_val=''
                        li_val=['BASEAMOUNT','CGST','SGST','IGST','INVAMOUT']
                        li_val1=['BASEAMOUNT','CGST','SGST','IGST','INVAMOUT']
                        chkval_ind = 0
                        for i in split_formula:
                            if i not in li_val1:
                                if chkval_ind==0:
                                    concat_val=i
                                else:
                                    concat_val=str(concat_val)+i
                            else:
                                chkval_ind1 = 0
                                for j in li_val:

                                    if chkval_ind1==0:
                                        if i=='BASEAMOUNT':
                                            li_val.remove("BASEAMOUNT")
                                            if chkval_ind == 0:
                                                concat_val=str(BASEAMOUNT)
                                            else:
                                                concat_val = str(concat_val) + str(BASEAMOUNT)

                                        if i=='CGST':
                                            li_val.remove("CGST")
                                            if chkval_ind == 0:
                                                concat_val=str(CGST)

                                            else:
                                                concat_val = str(concat_val) + str(CGST)

                                        if i=='SGST':
                                            li_val.remove("SGST")
                                            if chkval_ind == 0:
                                                concat_val=str(SGST)

                                            else:
                                                concat_val = str(concat_val) + str(SGST)
                                        if i== 'IGST':
                                            li_val.remove("IGST")
                                            if chkval_ind == 0:
                                                concat_val = str(IGST)

                                            else:
                                                concat_val = str(concat_val) + str(IGST)
                                        if i=='INVAMOUT':
                                            li_val.remove("INVAMOUT")
                                            if chkval_ind == 0:
                                                concat_val = str(INVAMOUT)

                                            else:
                                                concat_val = str(concat_val) + str(INVAMOUT)

                                        chkval_ind1=chkval_ind1+1


                            chkval_ind = chkval_ind + 1
                        formula_amt = concat_val
                        #print(formula_amt)

                        addition = eval(formula_amt)
                        sumofamt=round(addition, 2)
                        logger.info('ENTRY_LOGGER - ' + str(sumofamt))
                        entry_data = EntryTemplateResponse()
                        entry_data.set_id(entry_val.id)
                        entry_data.set_gl_no(entry_val.gl_no)
                        entry_data.set_transaction(entry_val.transaction)
                        entry_data.set_Values(entry_val.Values)
                        entry_data.set_wisefin_category(entry_val.wisefin_category)
                        entry_data.set_wisefin_subcategory(entry_val.wisefin_subcategory)
                        entry_data.set_display(entry_val.display)
                        entry_data.amount=sumofamt
                        entry_data.invheaderamount=totalamount
                        entry_list_data.append(entry_data)
                        # vpage = VysfinPaginator(entrydetails, vys_page.get_index(), 10)
                        # entry_list_data.set_pagination(vpage)
                return entry_list_data
    def int_check(self,val):
        try:
            a=int(val)
            return True
        except:
            return False
