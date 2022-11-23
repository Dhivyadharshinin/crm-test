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
from entryservice.util.entryutil import EntryType, APDBService, MASTERDBService, VENDORDBService
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.entry_api_service import ApiService
import traceback

# from environs import Env
# env = Env()
# env.read_env()
# DB_NAME_masterdb = env.str('DB_NAME_masterdb')
# DB_NAME_vendordb = env.str('DB_NAME_vendordb')
#DB_NAME_apdb = 'napservice'
#DB_NAME_apdb = env.str('DB_NAME_masterdb')
class ParmaTemplateService(NWisefinThread):

    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ENTRY_SERVICE)
    def create_parametername(self,emp_id,paramname,code,entry_template,columnnamecredit,columnnamedebit,scope):
            try:
                from django.db import transaction
                with transaction.atomic(using=self._current_app_schema()):
                #master='nmaster'
                    ParameterName_Detail = ParameterName.objects .using(self._current_app_schema()). \
                                            create(code=code, paramname=paramname, columnname=0,
                                                   columnnamecredit=columnnamecredit,
                                                   columnnamedebit=columnnamedebit,
                                                   entity_id=self._entity_id(),
                                                   created_by=emp_id,
                                                   created_date=now())

                    id = ParameterName_Detail.id
                    for i in entry_template[0]:
                        gl_no = i['gl_no']
                        transaction = i['transaction']
                        value_to_taken = i['valuetobetaken']
                        #Values = i['value']
                        #Values = value
                        wisefin_category = i['wisefincat']
                        wisefin_subcategory = i['wisefinsubcat']
                        display = i['display']
                        entry_type = EntryTemplate.objects.using(self._current_app_schema()).create(parametername_id=id,
                                                                                           gl_no=gl_no,
                                                                                           transaction=transaction,
                                                                                           #Values=Values,
                                                                                           value_to_taken=value_to_taken,
                                                                                           wisefin_category=wisefin_category,
                                                                                           wisefin_subcategory=wisefin_subcategory,
                                                                                           display=display,
                                                                                           entity_id=self._entity_id(),
                                                                                           created_by=emp_id,
                                                                                           created_date=now())
                    success_obj = NWisefinSuccess()
                    success_obj.set_status(SuccessStatus.SUCCESS)
                    success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                    return success_obj
            except Exception as excep:
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(str(excep))
                return error_obj

    def fetch_columnparameterservice(self ,user_id,trans_id):
        condition =  ~Q(is_parent=0)
        entryclmname = ParameterTables.objects.using(self._current_app_schema()).filter(condition)
        list_length = len(entryclmname)
        entry_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for entry_val in entryclmname:
                entry_data = ParamtemplateResponse()
                entry_data.set_id(entry_val.id)
                entry_data.set_name(entry_val.name)
                entry_data.set_is_parent(entry_val.is_parent)
                entry_data.set_displayname(entry_val.displayname)
                entry_list_data.append(entry_data)
                # vpage = VysfinPaginator(entrydetails, vys_page.get_index(), 10)
                # entry_list_data.set_pagination(vpage)
            return entry_list_data

    def querycondition_check(self,crno,invoiceheader_id,invoicedetails_id,module_name,emp_id,scope):
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
        #print(DB_NAME_apdb,DB_NAME_masterdb,DB_NAME_vendordb)

        logger.info('ENTRY_LOGGER - ' + str(DB_NAME_apdb),str(DB_NAME_masterdb),str(DB_NAME_vendordb))
        #logger.info('ENTRY_LOGGER - ' + str(DB_NAME_apdb))
        # Dynamic_query=()
        condition = Q(code=module_name)
        parameter_name= ParameterName.objects.using(self._current_app_schema()).filter(condition)
        #params_id=parameter_name[0]['id']
        params_id=parameter_name[0].id
        columnname_and_values=""
        for i in parameter_name:
            import ast
            columnnamedebit1=json.loads(json.dumps(i.columnnamedebit))
            columnnamedebit = ast.literal_eval(columnnamedebit1)
            #print(columnnamedebit)
            for j in columnnamedebit:
                columnname=j['columnname']
                sourcekey=j['source_key']
                sourcevalue=j['source_value']
                if columnname_and_values == '':
                    columnname_and_values = columnname+'='+"'"+sourcevalue+"'"
                else:
                    columnname_and_values+= " and "+columnname+'=' + "'" +sourcevalue +"'"
        logger.info('ENTRY_LOGGER - ' + str(columnname_and_values))
        Dynamic_query = (
            " select c.amount,c.sgst,c.cgst,c.igst,a.aptype,b.invoicegst as is_gst,b.totalamount,d.code as product_code,e.code "
            " as hsn_code,g.code as branch_code,g.name as branch_name,h.name as supplier_name,h.code as supplier_code "
            " from "+str(DB_NAME_apdb)+" .apservice_apheader a inner join "+str(DB_NAME_apdb)+" .apservice_apinvoiceheader "
            " b on a.id=b.apheader_id "
            " inner join "+str(DB_NAME_apdb)+" .apservice_apinvoicedetail c on b.id=c.apinvoiceheader_id "
            " left join "+str(DB_NAME_masterdb)+" .masterservice_product d on c.productcode=d.code "
            " left join "+str(DB_NAME_masterdb)+" .masterservice_hsn e on e.code=c.hsn "
            " left join "+str(DB_NAME_masterdb)+" .masterservice_uom f on c.uom=f.code "
            " left join userservice_employeebranch g on g.id=a.raiserbranch "
            " left join "+str(DB_NAME_vendordb)+" .vendorservice_supplierbranch h on h.id=b.supplier_id "
            " where a.crno='"+str(crno)+"' and b.id="+str(invoiceheader_id)+" and c.id="+str(invoicedetails_id)+" "
            " and "+str(columnname_and_values)+"  ")
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
                amount=a[0]['amount']
                sgst=a[0]['sgst']
                cgst=a[0]['cgst']
                igst=a[0]['igst']
                totalamount=a[0]['totalamount']
                # condition = Q(parametername_id=params_id) & Q(transaction='DEBIT')
                # entrytemplate_details = EntryTemplate.objects.using(self._current_app_schema()).filter(condition)
                logger.info('ENTRY_LOGGER - ' + str(a),str(totalamount))
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
                        #split_formula = ['INVAMT', '+', 'CGST', '/', '2', '+', 'SGST', '/', '5']
                        # sdr = ['+', '-', '/', '*']

                        concat_val=''
                        # fgh=8+1000128/1000128+1000128/1000128
                        # INVAMT=1000
                        # CGST=12
                        # SGST=8
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
                        #print(addition,sumofamt)
                        # import re
                        # re.split('; |, |\*|\n', a)
                        # vf=int(INVAMT)+int(CGST)/2+int(SGST)/2
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
    def queryconditioncr_check(self,crno,invoiceheader_id,invoicedetails_id,module_name,emp_id,scope):
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
        ######
        condition = Q(code=module_name)
        parameter_name= ParameterName.objects.using(self._current_app_schema()).filter(condition)
        params_id=parameter_name[0].id
        columnname_and_values=""
        for i in parameter_name:
            import ast
            columnnamedebit1=json.loads(json.dumps(i.columnnamedebit))
            columnnamedebit = ast.literal_eval(columnnamedebit1)
            for j in columnnamedebit:
                columnname=j['columnname']
                sourcekey=j['source_key']
                sourcevalue=j['source_value']
                if columnname_and_values == '':
                    columnname_and_values = columnname+'='+"'"+sourcevalue+"'"
                else:
                    columnname_and_values+= " and "+columnname+'=' + "'" +sourcevalue +"'"
        #"inner join nentry.entryservice_parametername z on z.code='" + str(module_name) + "' " z.id as paramid,
        logger.info('ENTRY_LOGGER - ' + str(columnname_and_values))
        Dynamic_query = (
            " select c.amount,c.sgst,c.cgst,c.igst,a.aptype,b.invoicegst as is_gst,b.totalamount,d.code as product_code,e.code "
            " as hsn_code,g.code as branch_code,g.name as branch_name,h.name as supplier_name,h.code as supplier_code "
            " from "+str(DB_NAME_apdb)+" .apservice_apheader a inner join "+str(DB_NAME_apdb)+" .apservice_apinvoiceheader "
            " b on a.id=b.apheader_id "
            " inner join "+str(DB_NAME_apdb)+" .apservice_apinvoicedetail c on b.id=c.apinvoiceheader_id "
            " left join "+str(DB_NAME_masterdb)+" .masterservice_product d on c.productcode=d.code "
            " left join "+str(DB_NAME_masterdb)+" .masterservice_hsn e on e.code=c.hsn "
            " left join "+str(DB_NAME_masterdb)+" .masterservice_uom f on c.uom=f.code "
            " left join userservice_employeebranch g on g.id=a.raiserbranch "
            " left join "+str(DB_NAME_vendordb)+" .vendorservice_supplierbranch h on h.id=b.supplier_id "
            " where a.crno='"+str(crno)+"' and b.id="+str(invoiceheader_id)+" "
                                                                           # "and c.id="+str(invoicedetails_id)+" "
            " and "+str(columnname_and_values)+"  ")
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
                    amount = a[0]['amount']
                    sgst = a[0]['sgst']
                    cgst = a[0]['cgst']
                    igst = a[0]['igst']
                    totalamount = a[0]['totalamount']
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
                        #print(re.findall('\W+|\w+', valuetotaken))
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
                                        if i=='INVAMOUT':
                                            li_val.remove("INVAMOUT")
                                            if chkval_ind == 0:
                                                concat_val = str(INVAMOUT)
                                                # concat_val=int(SGST)
                                            else:
                                                concat_val = str(concat_val) + str(INVAMOUT)
                                            #concat_val='0'
                                        chkval_ind1=chkval_ind1+1
                                                # concat_val = str(concat_val) + int(SGST)
                                            # concat_val=int(SGST)

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

    def fetch_all_paramname_list(self,query,vys_page,emp_id,request):
        condition=Q(status=1)
        if 'code' in request.GET and request.GET.get('code') != '' or "" or None:
            condition &= Q(code__icontains=request.GET.get('code'))
        if 'name' in request.GET and request.GET.get('name') != '' or "" or None:
            condition &= Q(paramname__icontains=request.GET.get('name'))
        params_tables = ParameterName.objects.using(self._current_app_schema()).filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
        #print(params_tables.query)
        list_length = len(params_tables)
        entry_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for entry_val in params_tables:
                entry_data = ParamnametemplateResponse()
                entry_data.set_id(entry_val.id)
                entry_data.set_code(entry_val.code)
                entry_data.set_paramname(entry_val.paramname)
                entry_data.set_columnnamedebit(entry_val.columnnamedebit)
                entry_list_data.append(entry_data)
                vpage = NWisefinPaginator(params_tables, vys_page.get_index(), 10)
                entry_list_data.set_pagination(vpage)
        return entry_list_data

    def inactiveparametername(self,param_id,emp_id):
            try:
                ParameterName_Detail = ParameterName.objects .using(self._current_app_schema())\
                    .filter(id=param_id).update(updated_by=emp_id,status=0,
                                                 updated_date=now())
                ParameterName_Detail = EntryTemplate.objects.using(self._current_app_schema()) \
                    .filter(parametername_id=param_id).update(updated_by=emp_id,
                                                updated_date=now())
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.CREATE_MESSAGE)

            except Exception as excep:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(str(excep))
                return error_obj
            return success_obj

    def fetch_parametername(self,query, vys_page, param_id, request):
        condition=Q(parametername_id=param_id)
        params_tables = EntryTemplate.objects.using(self._current_app_schema())\
                        .filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
        #print(params_tables.query)
        list_length = len(params_tables)
        entry_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for entry_val in params_tables:
                entry_data = templatenameResponse()
                entry_data.set_id(entry_val.id)
                entry_data.set_gl_no(entry_val.gl_no)
                entry_data.set_transaction(entry_val.transaction)
                entry_data.set_Values(entry_val.Values)
                entry_data.set_value_to_taken(entry_val.value_to_taken)
                entry_data.set_wisefin_category(entry_val.wisefin_category)
                entry_data.set_wisefin_subcategory(entry_val.wisefin_subcategory)
                entry_data.set_display(entry_val.display)
                entry_list_data.append(entry_data)
                vpage = NWisefinPaginator(params_tables, vys_page.get_index(), 10)
                entry_list_data.set_pagination(vpage)
        return entry_list_data

    def entrytemplate_update(self,emp_id,template_obj):
            try:
                EntryTempDetail = EntryTemplate.objects.using(self._current_app_schema()).filter(id=template_obj.get_id()).update(
                                                        gl_no=template_obj.get_gl_no(),
                                                        transaction=template_obj.get_transaction(),
                                                        #Values=template_obj.get_Values(),
                                                        value_to_taken=template_obj.get_value_to_taken(),
                                                        wisefin_category=template_obj.get_wisefin_category(),
                                                        wisefin_subcategory=template_obj.get_wisefin_subcategory(),
                                                        display=template_obj.get_display(),
                                                        updated_by=emp_id,
                                                        updated_date=now())
                #EntryDetail = Entry.objects.get(id=entry_obj.get_id())
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)

            except Exception as excep:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(str(excep))
                return error_obj
            return success_obj