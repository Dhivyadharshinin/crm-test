import json
import traceback
from timeit import timeit

import pandas as pd
from dateutil import parser
from django.db import IntegrityError
from django.db.models import Count,Sum,Max
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils.dateformat import DateFormat, TimeFormat
from django.db.models import Count
from django.db import connection
from django.db import connections

from faservice.data.response.depreciationresponse import DepreciationResponse
from faservice.models.famodels import DepreciationTmp, AssetHeaderTmp, AssetHeader, Depreciation, AssetDetails,ITDepreciation
from faservice.util.fautil import AssetQuery
from faservice.util.fautil_valid import date_validation
from django.http import HttpResponse
from utilityservice.data.response.nwisefinerror import NWisefinError as Error, NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from nwisefin.settings import logger
from django.utils.timezone import now
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from faservice.util.FaApiService import FaApiService
from faservice.util.fautil import DataBase
# from faservice.data.response.depreciationresponse import DepreciationResponse
####DB NAME CHANGE
from environs import Env
from nwisefin.settings import DATABASES
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

# env = Env()
# env.read_env()
# try:
#     DB_NAME_FA = env.str('DB_NAME_FA')
#     self.fa_db = DB_NAME_FA
# except:
#     logger.info('ERROR ON DB NAME-FASERVICE  ')
#     print('ERROR ON DB NAME-FASERVICE')
class DepreciationService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
        self.fa_db_serv = self._current_app_schema()
        print(self.fa_db_serv)
        self.fa_db=DATABASES[self.fa_db_serv]['NAME']
        print(self.fa_db)
    def create_depreciation(self,dep_obj,emp_id):
        try:
            from_date=dep_obj.get_from_date()
            calculate_for=dep_obj.get_calculate_for()
            deptype=dep_obj.get_deptype()
            to_date=dep_obj.get_to_date()
            split_todate=datetime.strptime(to_date,'%Y-%m-%d').date()
            from_date=datetime.strptime(from_date,'%Y-%m-%d').date()

            #split_fromdate=datetime.strptime(from_date,'%Y-%m-%d').date()
            month_val=str(split_todate.month)
            year_val=str(split_todate.year)
            get_querydata = AssetQuery()
            dep_setting_chk=get_querydata.get_depsetting()
            depsettingchk=len(dep_setting_chk)

            if depsettingchk == 0:
                error_obj = Error()
                error_obj.set_code(ErrorMessage.ERROR_ON_DEPRECIATION_SETTINGS_DATA)
                error_obj.set_description(ErrorDescription.NO_DATA)
                return error_obj

            #GROUPING ASSETCAT AND CP DATE------------------------------------------------------------------------------STEP 1
            #DepreciationTmp.objects.all().delete()

            deptruncate_query = ("Truncate table "+str(self.fa_db)+".faservice_depreciationtmp")
            #print(deptruncate_query,'ramesh')
            with connections[self.fa_db_serv].cursor() as cursor:
                cursor.execute(deptruncate_query)


            Depreciation_Grp,first_grp=get_querydata.get_assetDep_Grp(split_todate)
            # first_grp=len(Depreciation_Grp)
            logger.info('fadep_DEPRECIATION_GROUP_COUNT_1 - ' + str(first_grp))

            df=pd.DataFrame.from_records(Depreciation_Grp)
            facat=df['assetcat_id'].to_list()
            facap=df['capdate'].to_list()

            depreciation_data=get_querydata.get_assetDepData(facat,facap)
            grp_len=len(depreciation_data)
            logger.info('fadep_DEPRECIATION_GROUP_COUNT_2 - ' +str(grp_len))

            START_TIME_D = datetime.now()
            START_TIME = START_TIME_D.strftime("%d/%m/%Y %H:%M:%S")
            logger.info('fadep_START_DEPRECIATION - '+START_TIME)
            arr = []
            a=0
            #ab=0
           # print(len(depreciation_data))
            for obj in depreciation_data:
                assetid=obj['id']
                assetbarcode=obj['assetbarcode']
                capdate=obj['capdate']
                assetdeptype=obj['assetcat_deptype']
                assetdeprate=obj['asset_deprate']
                assetdetailscost=obj['assetdetails_cost']
                asset_valueD=obj['assetdetails_value']
                depresglmgmt=obj['depresglmgmt']
                deprate_mgmt=obj['deprate_mgmt']
                # barcode=get_querydata.get_assetbarcode(assetid)
                # clsbalance=get_querydata.get_colsingbalance(barcode)
            #COLSING BALANCE START -----------------------------------------------------------------------------------STEP 2
                clsbalance_sum=get_querydata.get_colsingbalance_sum(assetbarcode,assetid)
                #print(len(clsbalance_sum),'clsbalance')

                clsbalance_len=len(clsbalance_sum)
                if clsbalance_len >0:
                    clsbalancesum=clsbalance_sum[0]['assetheader_revisedcbtot']
                    if clsbalancesum ==None:
                        clsbalancesum=0

                    if clsbalancesum > 1:
                        #logger.info('fadep_clsbalance_len - ' +str(clsbalance_len))
                        a += 1
                        last_depDate_Chk = get_querydata.get_Last_depDate_Chk(from_date, assetid)
                        if last_depDate_Chk == True:
                            error_obj = Error()
                            error_obj.set_code(ErrorMessage.ALREADY_DEPRECIATION_RUN_CHECK)
                            error_obj.set_description(ErrorDescription.INVALID_DATE_CHK)
                            return error_obj

                        #splitfromdate = datetime.strptime(from_date, '%Y-%m-%d').date()
                        datediff = (split_todate - from_date).days
                        DepDaysD = datediff + 1
                        if capdate > from_date:
                            DepDaysD = (split_todate - capdate).days
                            DepDaysD = DepDaysD + 1
                            wdv_fdate = capdate
                            DepCalFrom_DateI = capdate
                        condition = Q(assetdetails_id=assetid)
                        lastdepDateChk = Depreciation.objects.filter(condition).aggregate(Max('depreciation_todate'))
                        lastdepChk=len(lastdepDateChk)
                        if lastdepChk == 0:
                            if capdate < from_date:
                                DepDaysD = (split_todate - capdate).days
                                DepDaysD = DepDaysD + 1
                                wdv_fdate = capdate
                                DepCalFrom_DateI = capdate
                        enddate_deprate = get_querydata.get_enddate_deprate(assetid)
                        asset_deprate_tagged = enddate_deprate[0]['deprate']
                        assetenddateD = enddate_deprate[0]['enddate']
                        formatted_date = DateFormat(assetenddateD)
                        asset_enddateD = formatted_date.format('Y-m-01')
                        DepCalTo_DateD = year_val+month_val+'-01'
                        DepCalTo_DateDI = to_date

                        if str(DepCalTo_DateD) >= asset_enddateD:
                            Is_ast_end_Month = 'Y'
                        else:
                            Is_ast_end_Month = 'N'
                        is_endlifemet='N'
                        if str(split_todate) >= asset_enddateD:
                            #assetenddateD = datetime.strptime(assetenddateD, '%Y-%m-%d').date()
                           # d1 = datetime.strptime(from_date, "%Y-%m-%d")
                            d2 = datetime.strptime(asset_enddateD, "%Y-%m-%d")
                            DepDaysD=(d2 - from_date).days
                            DepDaysD = DepDaysD + 1
                            DepCalTo_DateDI=assetenddateD
                            if DepDaysD <= 0:
                                is_endlifemet = 'Y'
                        if is_endlifemet=='N':

                            clsbalance=get_querydata.get_is_endlifemet(from_date,split_todate,assetdeptype,
                                                                       asset_deprate_tagged,assetdetailscost,
                                                                       capdate,assetid,DepDaysD,asset_valueD)
                            depvaluetotal=clsbalance['depvaluetotal']
                            depreciation_yrclosingblnce = clsbalance['depreciation_yrclosingblnce']
                            if depvaluetotal > asset_valueD :
                                depvaluetotal =asset_valueD - 1
                            deptmp = DepreciationTmp(assetdetails_id=assetid,
                                                     depreciation_fromdate=capdate,
                                                     depreciation_todate=DepCalTo_DateDI,
                                                     depreciation_month=month_val,
                                                     depreciation_year=year_val,
                                                     itcvalue=0,
                                                     cavalue=0,
                                                     mgmtvalue=depvaluetotal,
                                                     resgl=depresglmgmt,
                                                     gl=deprate_mgmt,
                                                     depreciation_value=depvaluetotal,
                                                     yrclosingblnce=depreciation_yrclosingblnce,
                                                     created_by=emp_id,
                                                     created_date=now())

                            arr.append(deptmp)
                if a == 10000:
                    DepreciationTmp.objects.bulk_create(arr)
                    # print(a)
                    a = 0
                    arr = []
            if len(arr) > 0:
                DepreciationTmp.objects.bulk_create(arr)
            logger.info('fadep_depreciation_end')
        ####next step assetdetails delete-----------------------------------------------------------------------------STEP 3
            START_TIME_D = datetime.now()
            START_TIME = START_TIME_D.strftime("%d/%m/%Y %H:%M:%S")
            logger.info('fadep_ASSETHEADER_START - ' + START_TIME)

            AssetHeaderTmp.objects.all().delete()
            #a=AssetHeaderTmp.objects.filter(status=1).delete()
            # assetheader_trn=AssetHeader.objects.all()[0:1000]
            #
            # arr_tmp=[]
            # b=0
            # for assetheader in assetheader_trn:
            #     b+=1
            #     assettmp = AssetHeaderTmp(assetdetailsbarcode=assetheader.barcode,
            #                                 date=assetheader.date,
            #                                 assetheader_month=assetheader.assetheadermonth,
            #                                 assetheader_year=assetheader.assetheaderyear,
            #                                 astvalbeforedeptot=assetheader.astvalbeforedeptot,
            #                                 computeddeptot=assetheader.computeddeptot,
            #                                 reviseddeptot=assetheader.reviseddeptot,
            #                                 revisedcbtot=assetheader.revisedcbtot,
            #                                 deprestot=assetheader.deprestot,
            #                                 assetheader_costtot=assetheader.costtot,
            #                                 assetheader_valuetot=assetheader.valuetot,
            #                                 assetheader_type=assetheader.type,
            #                                 assetheader_issale=assetheader.issale,
            #                                 created_by=emp_id,
            #                                 created_date=now())
            #     arr_tmp.append(assettmp)
            #     if b == 1000:
            #         AssetHeaderTmp.objects.bulk_create(arr_tmp)
            #         b=0
            #         arr_tmp=[]
            # if len(arr_tmp) > 0:
            #     AssetHeaderTmp.objects.bulk_create(arr_tmp)

            barcode_query = ("insert into "+str(self.fa_db)+".faservice_assetheadertmp (assetdetailsbarcode,date,assetheader_month, assetheader_year,"
                             "astvalbeforedeptot,computeddeptot,reviseddeptot,revisedcbtot,deprestot,assetheader_costtot,assetheader_valuetot,"
                             "assetheader_type,assetheader_issale,status,created_by,created_date) select barcode,date,assetheadermonth,"
                             "assetheaderyear,astvalbeforedeptot,computeddeptot,reviseddeptot,revisedcbtot,deprestot,costtot,valuetot,type,"
                             "issale,1,created_by,now() FROM "+str(self.fa_db)+".faservice_assetheader")
            with connections[self.fa_db_serv].cursor() as cursor:
                cursor.execute(barcode_query)

            END_TIME_D = datetime.now()
            END_TIME = END_TIME_D.strftime("%d/%m/%Y %H:%M:%S")
            logger.info('fadep_ASSETHEADER_END - '+ END_TIME)

            END_TIME_D = datetime.now()
            END_TIME = END_TIME_D.strftime("%d/%m/%Y %H:%M:%S")
            logger.info('fadep_BARCODE_UPDATE_START - ' + END_TIME)

            barcode_update = (" update  "+str(self.fa_db)+".faservice_assetheadertmp as z inner join (select sum(case when a.source = 6 or (a.source = 5) "
                             "then assetdetails_cost else 0 end) - sum(Case when a.source = 2  then assetdetails_cost else 0 end) as opening_b,"
                             "barcode,c.assetheader_valuetot as ast_val_bfr_dep,ifnull(sum(case when a.source <> 2 or (a.source <> 8) then d.depreciation_value "
                             "else d.depreciation_value * -1 end ),0) as computed_dep,ifnull(case when c.assetheader_issale = 0 and"
                             "(c.astvalbeforedeptot - c.reviseddeptot) <=  sum(case when a.source <> 2 then d.depreciation_value "
                             "else d.depreciation_value * -1 end ) then (c.astvalbeforedeptot - c.reviseddeptot) -1 when c.assetheader_issale = 1 and "
                             "(c.astvalbeforedeptot - c.reviseddeptot) <  sum(case when a.source <> 2 then d.depreciation_value else "
                             "d.depreciation_value * -1 end ) then (c.astvalbeforedeptot - c.reviseddeptot) else sum(case when a.source <> 2 then "
                             "d.depreciation_value else d.depreciation_value * -1 end ) end,0) as revised_dep,ifnull(((c.astvalbeforedeptot - reviseddeptot) - "
                             "case when c.assetheader_issale = 0 and (c.astvalbeforedeptot - c.reviseddeptot) <=  sum(case when a.source <> 2 "
                             "then d.depreciation_value else d.depreciation_value * -1 end ) then (c.astvalbeforedeptot - c.reviseddeptot) -1 "
                             "when c.assetheader_issale = 1 and   (c.astvalbeforedeptot - c.reviseddeptot) <  sum(case when a.source <> 2 "
                             "then d.depreciation_value else d.depreciation_value * -1 end ) then (c.astvalbeforedeptot - c.reviseddeptot) "
                             "else sum(case when a.source <> 2 then d.depreciation_value else d.depreciation_value * -1 end )end),0)"
                             " as Tot_RevisedCB,ifnull(c.deprestot + sum(case when a.source <> 2 then d.depreciation_value else d.depreciation_value * -1 end ),0) "
                             "as Tot_Deprestot,ifnull(((c.astvalbeforedeptot - reviseddeptot) - case when c.assetheader_issale = 0 and "
                             "(c.astvalbeforedeptot - c.reviseddeptot) <=  sum(case when a.source <> 2 then d.depreciation_value else d.depreciation_value * -1 end )"
                             "then (c.astvalbeforedeptot - c.reviseddeptot) -1 when c.assetheader_issale = 1 and  "
                             " (c.astvalbeforedeptot - c.reviseddeptot) <  sum(case when a.source <> 2 then d.depreciation_value else d.depreciation_value * -1 end )"
                             " then (c.astvalbeforedeptot - c.reviseddeptot) else sum(case when a.source <> 2 then d.depreciation_value "
                             "else d.depreciation_value * -1 end ) end),0) as Tot_Assetvalue,type,depreciation_todate,c.assetheader_issale,"
                             "depreciation_year,depreciation_month from "+str(self.fa_db)+" .faservice_assetdetails as a inner join "+str(self.fa_db)+".faservice_assetheadertmp as c "
                             "on c.assetdetailsbarcode = a.barcode inner join "+str(self.fa_db)+".faservice_depreciationtmp as d on d.assetdetails_id = a.id where"
                             " d.depreciation_month = "+str(month_val)+" and d.depreciation_year = "+str(year_val)+" group by barcode) "
                             "as t1 on t1.barcode = z.assetdetailsbarcode set z.date = t1.depreciation_todate,"
                             "z.astvalbeforedeptot = t1.ast_val_bfr_dep,"
                             "z.assetheader_valuetot = t1.Tot_Assetvalue,"
                             "z.computeddeptot = t1.computed_dep,"
                             "z.reviseddeptot = t1.revised_dep,"
                             "z.revisedcbtot = t1.Tot_RevisedCB,"
                             "z.deprestot = t1.Tot_Deprestot,"
                             "z.assetheader_month = t1.depreciation_month,"
                             "z.assetheader_year = t1.depreciation_year,"
                             "z.updated_by ="+str(emp_id)+","
                             "z.assetheader_type = t1.type")
            #print(barcode_query)
            with connections[self.fa_db_serv].cursor() as cursor:
                cursor.execute(barcode_update)
            # dep_tmp=get_querydata.get_depreciation_assetid(month_val,year_val)
            # asset_barcode = [o['barcode'] for o in dep_tmp]
    #         Headertmp_obj = AssetHeaderTmp.objects.filter(assetdetailsbarcode__in=asset_barcode)
    #         print(len(Headertmp_obj))
    #         header_arr=[]
    #         c=0
    #         for m in dep_tmp:
    #             c+=1
    #             for n in Headertmp_obj:
    #                 if n.assetdetailsbarcode==m['barcode']:
    #                     n.updated_by=1
    #                     n.updated_date=now()
    #                     n.date=m['depreciation_todate']
    #                     n.assetheader_month=m['depreciation_month']
    #                     n.assetheader_year=m['depreciation_year']
    #                     n.assetheader_type=m['type']
    #                     header_arr.append(n)
    #                 if c == 1000:
    #                     AssetHeaderTmp.objects.bulk_update(header_arr,['updated_by','updated_date'])
    #                     c = 0
    #                     header_arr = []
    #         if len(header_arr) > 0:
    #             AssetHeaderTmp.objects.bulk_update(header_arr,['updated_by','updated_date'])


            #         # if ((assetheader_issale == 0) and (sumofdep <= dep_sum)):
            #         #     dep_reviseddeptot = sumofdep - 1
            #         # else:
            #         #     pass
            #         # if ((assetheader_issale == 1) and (sumofdep < dep_sum)):
            #         #     dep_reviseddeptot = sumofdep
            #         # else:
            #         #     dep_reviseddeptot = dep_sum

            print(from_date,'------------------',split_todate)
            barcode_update_final = ("Update "+str(self.fa_db)+".faservice_assetheadertmp as z inner join "+str(self.fa_db)+".faservice_assetdetails as a "
                                    "on a.barcode = z.assetdetailsbarcode "
                                    "set z.reviseddeptot = reviseddeptot + revisedcbtot -1,"
                                    "z.revisedcbtot = 1 where source = 5 and deponhold = 1 "
                                    "and assetdetails_status = 1 and a.enddate >= '"+str(from_date)+"' and"
                                    " a.enddate <= '"+str(split_todate)+"' and a.assetdetails_value <> 0")
            print(barcode_update_final)
            with connections[self.fa_db_serv].cursor() as cursor:
                cursor.execute(barcode_update_final)

            END_TIME_D = datetime.now()
            END_TIME = END_TIME_D.strftime("%d/%m/%Y %H:%M:%S")
            logger.info('fadep_BARCODE_UPDATE_END - ' + END_TIME)

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            #return success_obj
        except Exception  as excep:
            logger.info('FAL_DEPRECIATION_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj
        return success_obj


    def create_depreciationreg(self,dep_obj,emp_id):
        from_date=dep_obj.get_from_date()
        calculate_for=dep_obj.get_calculate_for()
        deptype=dep_obj.get_deptype()
        to_date=dep_obj.get_to_date()
        split_todate=datetime.strptime(to_date,'%Y-%m-%d').date()
        from_date=datetime.strptime(from_date,'%Y-%m-%d').date()
        month_val=str(split_todate.month)
        year_val=str(split_todate.year)
        #GROUPING ASSETCAT AND CP DATE------------------------------------------------------------------------------STEP 1
        #Depreciation.objects.all().delete()

        get_querydata=AssetQuery()
        Depreciation_Grp=get_querydata.get_assetDep_Grp(from_date)
        facat = [i['assetcat_id'] for i in Depreciation_Grp]
        facap = [i['capdate'] for i in Depreciation_Grp]

        depreciation_data=get_querydata.get_assetDepData(facat,facap)

        START_TIME_D = datetime.now()
        START_TIME = START_TIME_D.strftime("%d/%m/%Y %H:%M:%S")
        logger.info('fadep_START_DEPRECIATION_REG - '+START_TIME)
        arr = []
        arr_new = []
        a=0
       # print(len(depreciation_data))
        assetdeptype=0
        assetid=0
        DepValueTotalD=0
        Is_Salvage=0
        for obj in depreciation_data:
            assetid=obj['id']
            capdate=obj['capdate']
            assetbarcode=obj['assetbarcode']
            asset_valueD = obj['assetdetails_value']
            assetdeptype=obj['assetcat_deptype']
            assetdeprate=obj['asset_deprate']
            assetdetailscost=obj['assetdetails_cost']
            depresglmgmt=obj['depresglmgmt']
            deprate_mgmt=obj['deprate_mgmt']
            # barcode=get_querydata.get_assetbarcode(assetid)
            # clsbalance=get_querydata.get_colsingbalance(barcode)
        #COLSING BALANCE START -----------------------------------------------------------------------------------STEP 2
            clsbalance_sum=get_querydata.get_colsingbalance_sum(assetbarcode,assetid)
            clsbalance_len=len(clsbalance_sum)

            if clsbalance_len >0:
                clsbalancesum=clsbalance_sum[0]['assetheader_revisedcbtot']
                if clsbalancesum ==None:
                    clsbalancesum=0

                if clsbalancesum > 1:
                    #splitfromdate = datetime.strptime(from_date, '%Y-%m-%d').date()
                    datediff = (split_todate - from_date).days
                    DepDaysD = datediff + 1
                    if capdate > from_date:
                        DepDaysD = (split_todate - capdate).days
                        DepDaysD = DepDaysD + 1
                        wdv_fdate = capdate
                        DepCalFrom_DateI = capdate
                    clsbalance = get_querydata.get_is_endlifemet(from_date, split_todate, assetdeptype, assetdeprate,assetdetailscost,capdate,assetid,DepDaysD,asset_valueD)
                    depvaluetotal = clsbalance['depvaluetotal']
                    depreciation_yrclosingblnce = clsbalance['depreciation_yrclosingblnce']
                    depregid_new=get_querydata.get_depre_new(assetid)
                    if depregid_new is None :
                        if obj['capdate'] < from_date:
                            depnew = Depreciation(assetdetails_id=assetid,
                                                  depreciation_fromdate=obj['capdate'],
                                                  depreciation_todate=to_date,
                                                  depreciation_month=month_val,
                                                  depreciation_year=year_val,
                                                  itcvalue=0,
                                                  cavalue=0,
                                                  mgmtvalue=0,
                                                  resgl=depresglmgmt,
                                                  gl=deprate_mgmt,
                                                  depreciation_value=depvaluetotal,
                                                  yrclosingblnce=depreciation_yrclosingblnce,
                                                  created_by=emp_id,
                                                  created_date=now())
                            arr_new.append(depnew)
                        Depreciation.objects.bulk_create(arr_new)
                    ###chk last depdate
                    last_depDate_Chk = get_querydata.get_Last_depDate_Chk(from_date, assetid)
                    # if last_depDate_Chk == False:
                    #     error_obj = Error()
                    #     error_obj.set_code(ErrorMessage.ALREADY_DEPRECIATION_RUN_CHECK)
                    #     error_obj.set_description(ErrorDescription.INVALID_DATE_CHK)
                    #     return error_obj
                    a += 1
                    enddate_deprate=get_querydata.get_enddate_deprate(assetid)
                    asset_deprate_tagged=enddate_deprate[0]['deprate']
                    assetenddateD=enddate_deprate[0]['enddate']
                    formatted_date = DateFormat(assetenddateD)
                    asset_enddateD=formatted_date.format('Y-m-01')
                    if (asset_deprate_tagged is not None) and (assetdeptype=='SLM'):
                        asset_deprateD=asset_deprate_tagged

                    #split_date = datetime.strptime(from_date, '%Y-%m-%d').date()
                    datediff = ( split_todate-from_date).days
                    depdays = datediff + 1
                    if capdate > from_date:
                        DepDaysD = (split_todate-capdate).days
                        depdays = DepDaysD + 1
                    #DepCalTo_DateD = datetime.strptime(to_date,'%Y-%m-01').date()
                    DepCalTo_DateD = year_val + '-' +month_val + '-01'
                    DepCalTo_DateD = year_val + '-04-01'
                    if str(DepCalTo_DateD) >= asset_enddateD:
                        Is_ast_end_Month='Y'
                    else:
                        Is_ast_end_Month='N'
                    # if str(split_todate) >=asset_enddateD:
                    #     #assetenddateD = datetime.strptime(assetenddateD, '%Y-%m-%d').date()
                    #     DepDaysD = (split_todate-assetenddateD).days
                    #     print(DepDaysD,123)
                    #     depdays = DepDaysD + 1
                    #     if depdays <=0:
                    #         error_obj = Error()
                    #         error_obj.set_code(ErrorMessage.ERROR_ON_DEPRECIATION_DAYS)
                    #         error_obj.set_description(ErrorDescription.INVALID_DAYS)
                    #         response = HttpResponse(error_obj.get(), content_type="application/json")
                    #         return response
                        Is_Salvage = 'Y'



                    if Is_ast_end_Month=='Y':
                        DepValue = get_querydata.get_enddate_deprate(assetid)
                        DepValueTotalD=DepValue[0]['assetdetails_value']
                        # if DepValueTotalD==0:
                        #     error_obj = Error()
                        #     error_obj.set_code(ErrorMessage.ERROR_ON_DEPRECIATION_END_LIFE)
                        #     error_obj.set_description(ErrorDescription.ERROR_FA_DEP)
                        #     return error_obj
                        # if DepValueTotalD >0:
                        #     error_obj = Error()
                        #     error_obj.set_code(ErrorMessage.ERROR_ON_DEPRECIATION_CALCULATE)
                        #     error_obj.set_description(ErrorDescription.ERROR_FA_DEP)
                        #     return error_obj


                    deptmp = Depreciation(assetdetails_id=assetid,
                                             depreciation_fromdate=obj['capdate'],
                                             depreciation_todate=to_date,
                                             depreciation_month=month_val,
                                             depreciation_year=year_val,
                                             itcvalue=0,
                                             cavalue=0,
                                             mgmtvalue=0,
                                             resgl=depresglmgmt,
                                             gl=deprate_mgmt,
                                             depreciation_value=depvaluetotal,
                                             yrclosingblnce=depreciation_yrclosingblnce,
                                             created_by=emp_id,
                                             created_date=now())
                    arr.append(deptmp)
            if a == 10000:
                Depreciation.objects.bulk_create(arr)
                # print(a)
                a = 0
                arr = []
        if len(arr) > 0:
            Depreciation.objects.bulk_create(arr)

            if assetdeptype == 1:
                value_update = ("UPDATE "+str(self.fa_db)+".faservice_assetdetails SET assetdetails_value = assetdetails_value - cast("+str(DepValueTotalD)+" as decimal(16,2)) "
                "WHERE id = "+str(assetid)+" ")
                with connections[self.fa_db_serv].cursor() as cursor:
                    cursor.execute(value_update)
            else:
                pass


            if Is_Salvage == 'Y':
                value_update2=("update "+str(self.fa_db)+".faservice_assetdetails set assetdetails_value = 1 where id ="+str(assetid)+" ")
                with connections[self.fa_db_serv].cursor() as cursor:
                    cursor.execute(value_update2)
            else:
                pass


        barcode_update_reg = (
                " update  "+str(self.fa_db)+".faservice_assetheader as z inner join (select sum(case when a.source = 6 or (a.source = 5) "
                "then assetdetails_cost else 0 end) - sum(Case when a.source = 2  then assetdetails_cost else 0 end) as opening_b,"
                "a.barcode,c.valuetot as ast_val_bfr_dep,ifnull(sum(case when a.source <> 2 then d.depreciation_value "
                "else d.depreciation_value * -1 end ),0) as computed_dep,ifnull(case when c.issale = 0 and"
                "(c.astvalbeforedeptot - c.reviseddeptot) <=  sum(case when a.source <> 2 then d.depreciation_value "
                "else d.depreciation_value * -1 end ) then (c.astvalbeforedeptot - c.reviseddeptot) -1 when c.issale = 1 and "
                "(c.astvalbeforedeptot - c.reviseddeptot) <  sum(case when a.source <> 2 then d.depreciation_value else "
                "d.depreciation_value * -1 end ) then (c.astvalbeforedeptot - c.reviseddeptot) else sum(case when a.source <> 2 then "
                "d.depreciation_value else d.depreciation_value * -1 end ) end,0) as revised_dep,ifnull(((c.astvalbeforedeptot - reviseddeptot) - "
                "case when c.issale = 0 and (c.astvalbeforedeptot - c.reviseddeptot) <=  sum(case when a.source <> 2 "
                "then d.depreciation_value else d.depreciation_value * -1 end ) then (c.astvalbeforedeptot - c.reviseddeptot) -1 "
                "when c.issale = 1 and   (c.astvalbeforedeptot - c.reviseddeptot) <  sum(case when a.source <> 2 "
                "then d.depreciation_value else d.depreciation_value * -1 end ) then (c.astvalbeforedeptot - c.reviseddeptot) "
                "else sum(case when a.source <> 2 then d.depreciation_value else d.depreciation_value * -1 end )end),0)"
                " as Tot_RevisedCB,ifnull(c.deprestot + sum(case when a.source <> 2 then d.depreciation_value else d.depreciation_value * -1 end ),0) "
                "as Tot_Deprestot,ifnull(((c.astvalbeforedeptot - reviseddeptot) - case when c.issale = 0 and "
                "(c.astvalbeforedeptot - c.reviseddeptot) <=  sum(case when a.source <> 2 then d.depreciation_value else d.depreciation_value * -1 end )"
                "then (c.astvalbeforedeptot - c.reviseddeptot) -1 when c.issale = 1 and  "
                " (c.astvalbeforedeptot - c.reviseddeptot) <  sum(case when a.source <> 2 then d.depreciation_value else d.depreciation_value * -1 end )"
                " then (c.astvalbeforedeptot - c.reviseddeptot) else sum(case when a.source <> 2 then d.depreciation_value "
                "else d.depreciation_value * -1 end ) end),0) as Tot_Assetvalue,d.type,d.depreciation_todate,c.issale,"
                "depreciation_year,depreciation_month from "+str(self.fa_db)+".faservice_assetdetails as a inner join "+str(self.fa_db)+".faservice_assetheader as c "
                "on c.barcode = a.barcode inner join "+str(self.fa_db)+".faservice_depreciation as d on d.assetdetails_id = a.id where"
                " d.depreciation_month = " + str(month_val) + " and d.depreciation_year = " + str(year_val) + " group by barcode) "
                        "as t1 on t1.barcode = z.barcode set z.date = t1.depreciation_todate,"
                        "z.astvalbeforedeptot = t1.ast_val_bfr_dep,"
                        "z.valuetot = t1.Tot_Assetvalue,"
                        "z.computeddeptot = t1.computed_dep,"
                        "z.reviseddeptot = t1.revised_dep,"
                        "z.revisedcbtot = t1.Tot_RevisedCB,"
                        "z.deprestot = t1.Tot_Deprestot,"
                        "z.assetheadermonth = t1.depreciation_month,"
                        "z.assetheaderyear = t1.depreciation_year,"
                        "z.updated_by ="+str(emp_id)+","
                        "z.type = t1.type")
        # print(barcode_update_reg)
        with connections[self.fa_db_serv].cursor() as cursor:
            cursor.execute(barcode_update_reg)

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def depreciation_summary(self,vys_page,user_id,request):
            dep = Depreciation.objects.filter()[vys_page.get_offset():vys_page.get_query_limit()]
            resp_list = NWisefinList()
            scope=request.scope
            fa_obj = FaApiService(scope)
            for dep_record in dep:
                dep_resp = DepreciationResponse()
                dep_resp.set_depreciation_gid(dep_record.id)
                dep_resp.set_assetdetails_gid(dep_record.assetdetails.barcode)
                dep_resp.set_assetdetails_id(dep_record.assetdetails.assetdetails_id)
                dep_resp.set_depreciation_fromdate(dep_record.depreciation_fromdate)
                dep_resp.set_depreciation_todate(dep_record.depreciation_todate)
                dep_resp.set_assetdetails_cost(dep_record.assetdetails.assetdetails_cost)
                dep_resp.set_depreciation_month(dep_record.depreciation_month)
                dep_resp.set_asset_cap_date(dep_record.assetdetails.capdate)
                dep_resp.set_branch_id(fa_obj.fetch_branch(dep_record.assetdetails.branch_id).name)
                dep_resp.set_assetcat_subcatname(dep_record.assetdetails.assetcat.subcatname)
                dep_resp.set_assetcat_deptype(dep_record.assetdetails.assetcat.deptype)
                dep_resp.set_depreciation_year(dep_record.depreciation_year)
                dep_resp.set_depreciation_itcvalue(dep_record.itcvalue)
                dep_resp.set_depreciation_cavalue(dep_record.cavalue)
                dep_resp.set_depreciation_gl(dep_record.gl)
                dep_resp.set_depreciation_resgl(dep_record.resgl)
                dep_resp.set_depreciation_value(dep_record.depreciation_value)
                dep_resp.set_depreciation_type(dep_record.type)
                resp_list.append(dep_resp)
            vpage = NWisefinPaginator(dep, vys_page.get_index(), 10)
            resp_list.set_pagination(vpage)
            return resp_list

    def fa_migration(self,emp_id,post_name,get_name):
        trun_query1 = ("SET FOREIGN_KEY_CHECKS = 0; Truncate table "+str(post_name)+".faservice_assetcat")
        with connections[self.fa_db_serv].cursor() as cursor:
            cursor.execute(trun_query1)
        migration_value1 = ("insert into "+str(post_name)+".faservice_assetcat (subcategory_id, subcatname, lifetime, deptype,deprate_itc,"
                           " deprate_ca, deprate_mgmt, depgl_itc,depgl_ca, depgl_mgmt, depresgl_itc, depresgl_ca,"
                           "depresgl_mgmt, apcatnodep_mgmt, apscatnodep_mgmt,apcatnodepres_mgmt, apscatnodepres_mgmt, deprate,"
                           "barcoderequired, remarks, status, created_by, created_date) select assetcat_subcategorygid, assetcat_subcatname, assetcat_lifetime, "
                           "assetcat_deptype, assetcat_deprate_itc, assetcat_deprate_ca, assetcat_deprate_mgmt,"
                           "assetcat_depgl_itc, assetcat_depgl_ca, assetcat_depgl_mgmt, assetcat_depresgl_itc,"
                           "assetcat_depresgl_ca, assetcat_depresgl_mgmt, assetcat_apcatnodep_mgmt,"
                           "assetcat_apscatnodep_mgmt, assetcat_apcatnodepres_mgmt,assetcat_apscatnodepres_mgmt, "
                           "assetcat_deprate,1, assetcat_remarks,1,create_by, create_date FROM "+str(get_name)+".fa_mst_tassetcat")
        with connections[self.fa_db_serv].cursor() as cursor:
            cursor.execute(migration_value1)
        trun_query2 = ("Truncate table " + str(post_name) + ".faservice_assetlocation")
        with connections[self.fa_db_serv].cursor() as cursor:
            cursor.execute(trun_query2)
        migration_value2 = ("insert into "+str(post_name)+".faservice_assetlocation (refgid, reftablegid, name, floor, remarks, status,"
                            "created_by,created_date) select assetlocation_refgid, assetlocation_reftablegid, "
                            "assetlocation_name, assetlocation_floor, assetlocation_remarks,1,create_by,now()"
                            " FROM "+str(get_name)+".fa_mst_tassetloaction ")
        with connections[self.fa_db_serv].cursor() as cursor:
            cursor.execute(migration_value2)
        trun_query_dep = ("Truncate table " + str(post_name) + ".faservice_depreciation")
        with connections[self.fa_db_serv].cursor() as cursor:
            cursor.execute(trun_query_dep)
        migration_value_dep= ("insert into " + str(
            post_name) + ".faservice_depreciation (assetdetails_id,cavalue,created_by,created_date,"
                         "depreciation_fromdate,depreciation_month,depreciation_todate,depreciation_value,"
                         "depreciation_year,gl,id,itcvalue,mgmtvalue,resgl,source,status,type,updated_by,"
                         "updated_date,yrclosingblnce) select depreciation_assetdetailsgid,"
                         "depreciation_cavalue,create_by,create_date,depreciation_fromdate,depreciation_month,"
                         "depreciation_todate,"
                         "depreciation_value,depreciation_year,depreciation_gl,depreciation_gid,"
                         "depreciation_itcvalue,depreciation_mgmtvalue,"
                         "depreciation_resgl,depreciation_source,1,depreciation_type,update_by,"
                         "update_date,depreciation_yrclosingblnce"
                         " FROM " + str(get_name) + ".fa_trn_tdepreciation ")
        with connections[self.fa_db_serv].cursor() as cursor:
            cursor.execute(migration_value_dep)
        post_mst_name='vys_default'
        trun_query_ap1 = ("SET FOREIGN_KEY_CHECKS = 0;Truncate table " + str(post_mst_name) + ".masterservice_apcategory")
        with connections['default2'].cursor() as cursor:
            cursor.execute(trun_query_ap1)
        migration_value_ap1= ("insert into " + str(
            post_mst_name) + ".masterservice_apcategory (code,expense_id,glno,id,"
                         "isasset,isodit,name,no,status,created_by,created_date,updated_by,updated_date) select category_code,1,"
                         "category_glno,category_gid,"
                         "category_isasset,category_isodit,"
                         "category_name,category_no,1,create_by,create_date,"
                         "update_by,Update_date"
                         " FROM " + str(get_name) + ".ap_mst_tcategory ")
        with connections['default2'].cursor() as cursor:
            cursor.execute(migration_value_ap1)
        trun_query_ap2 = ("SET FOREIGN_KEY_CHECKS = 0;Truncate table " + str(post_mst_name) + ".masterservice_apsubcategory")
        with connections['default2'].cursor() as cursor:
            cursor.execute(trun_query_ap2)
        migration_value_ap2= ("insert into " + str(
            post_mst_name) + ".masterservice_apsubcategory (assetcode,category_id,code,created_by,"
                         "created_date,expense_id,glno,gstblocked,gstrcm,id,name,"
                         "no,status,updated_by,updated_date) select "
                         "subcategory_asst_code,subcategory_categorygid,"
                         "subcategory_code,create_by,create_date,subcategory_expensegid,subcategory_glno,"
                         "subcategory_gstblocked,subcategory_gstrcm,subcategory_gid,"
                         "subcategory_name,subcategory_no,1,"
                         "update_by,Update_date"
                         " FROM " + str(get_name) + ".ap_mst_tsubcategory ")
        with connections['default2'].cursor() as cursor:
            cursor.execute(migration_value_ap2)

        trun_query3 = ("SET FOREIGN_KEY_CHECKS = 0; Truncate table " + str(post_name) + ".faservice_assetheader")
        with connections[self.fa_db_serv].cursor() as cursor:
            cursor.execute(trun_query3)

        migration_value4 = ("insert into "+str(post_name)+".faservice_assetheader (barcode, date, assetheadermonth, "
                            "assetheaderyear,astvalbeforedeptot, computeddeptot, reviseddeptot, revisedcbtot, deprestot, costtot, valuetot, "
                            "type, issale, status, created_by, created_date) select assetheader_assetdetailsbarcode, assetheader_date, "
                            "assetheader_month, assetheader_year, assetheader_astvalbeforedeptot,"
                            "assetheader_computeddeptot, assetheader_reviseddeptot, assetheader_revisedcbtot, "
                            "assetheader_deprestot, assetheader_costtot, assetheader_valuetot,assetheader_type,"
                            "assetheader_issale,1,create_by,now() FROM "+str(get_name)+".fa_trn_tassetheader ")
        with connections[self.fa_db_serv].cursor() as cursor:
            cursor.execute(migration_value4)

        trun_query4 = ("  SET FOREIGN_KEY_CHECKS = 0; Truncate table " + str(post_name) + ".faservice_assetdetails")
        with connections[self.fa_db_serv].cursor() as cursor:
            cursor.execute(trun_query4)

        migration_value5 = ("insert into "+str(post_name)+".faservice_assetdetails (assetdetails_id, qty, barcode, date,"
                            "assetgroup_id,assetcat_id,product_id, cat, subcat, assetdetails_value, assetdetails_cost, "
                            "description, capdate, source, assetdetails_status, requestfor, requeststatus, "
                            "assettfr_id, assetsale_id, not5k, assetowner, lease_startdate, lease_enddate,"
                            "impairasset_id, impairasset, writeoff_id, assetcatchange_id, assetvalue_id,"
                            "assetcapdate_id, assetsplit_id, assetmerge_id, assetcatchangedate, reducedvalue, "
                            "branch_id, assetlocation_id, assetdetails_bs, assetdetails_cc, deponhold, deprate, "
                            "enddate, parent_id, assetserialno, invoice_id, faclringdetails_id, inwheader_id,"
                            "inwdetail_id, inwarddate, mepno, ponum, crnum, debit_id, imagepath, vendorname, "
                            "status, created_by, created_date) select  assetdetails_id, assetdetails_qty,"
                            " assetdetails_barcode, assetdetails_date,assetdetails_assetgroupid, assetdetails_assetcatgid,"
                            " assetdetails_productgid,assetdetails_cat, assetdetails_subcat, assetdetails_value,"
                            " assetdetails_cost,assetdetails_description, assetdetails_capdate,"
                            "case when assetdetails_source in('NEW','New') then 1"
                            " when assetdetails_source = 'FAValN' then"
                            " 2"
                            " when assetdetails_source = 'FATRANN' then 3"
                            " when assetdetails_source = 'FATRANP' then"
                            " 4"
                            " when assetdetails_source = 'FAValP' then"
                            " 5"
                            " when assetdetails_source = 'FAMaker' then"
                            " 6"
                            " when assetdetails_source = 'FASale' then"
                            " 7"
                            " else 0"
                            " end  assetdetails_source,"
                            " case when assetdetails_status = 'ACTIVE' then"
                            " 1"
                            " when assetdetails_status = 'IN_ACTIVE' then"
                            " 2"
                            " when assetdetails_status = 'REJECTED' then"
                            " 3"
                            " when assetdetails_status = 'IN_PROCESS' then"
                            " 4"
                            " when assetdetails_status = 'ENTRY_FAILED' then"
                            " 5"
                            " when assetdetails_status = 'PROCESSED' then"
                            " 6"
                            " else 0"
                            " end  asassetdetails_status,"
                            " case when assetdetails_requestfor ='NEW' then"
                            " 1"
                            " when assetdetails_requestfor = 'TRANSFER' then"
                            " 2"
                            " when assetdetails_requestfor = 'SALE' then"
                            " 3"
                            " when assetdetails_requestfor = 'REJECTED' then"
                            " 4"
                            " when assetdetails_requestfor = 'WRITEOFF' then"
                            " 5"
                            " when assetdetails_requestfor = 'IMPAIRMENT' then"
                            " 6"
                            " when assetdetails_requestfor = 'VALUEREDUCTIONVALUEREDUCTION' then"
                            " 7"
                            " when assetdetails_requestfor = 'CAPDATE' then"
                            " 8"
                            " when assetdetails_requestfor = 'ASSETCAT' then"
                            " 9"
                            " when assetdetails_requestfor = 'SPLIT' then"
                            " 10"
                            " when assetdetails_requestfor = 'MERGE' then"
                            " 11"
                            " else 0"
                            " end  assetdetails_requestfor,"
                            " case when assetdetails_requeststatus ='APPROVED' then"
                            " 1"
                            " when assetdetails_requeststatus = 'REQUESTED' then"
                            " 2"
                            " when assetdetails_requeststatus = 'REJECTED' then"
                            " 3"
                            " when assetdetails_requeststatus = 'SUBMITTED' then"
                            " 4"
                            " when assetdetails_requeststatus = 'PENDING' then"
                            " 5"
                            " else 0"
                            " end  assetdetails_requeststatus,assetdetails_assettfrgid,assetdetails_assetsalegid,"
                            " case when assetdetails_not5k ='Y' then 1 "
                            " else 0 end  assetdetails_not5k,assetdetails_assetowner,"
                            " assetdetails_lease_startdate, assetdetails_lease_enddate, "
                            "assetdetails_impairassetgid,case when "
                            "assetdetails_impairasset ='Y' then 1 else 0 end  assetdetails_impairasset, "
                            "assetdetails_writeoffgid, assetdetails_assetcatchangegid,"
                            "assetdetails_assetvaluegid, assetdetails_assetcapdategid, assetdetails_assetsplitgid,"
                            "assetdetails_assetmergegid, assetdetails_assetcatchangedate, assetdetails_reducedvalue,"
                            "assetdetails_branchgid, assetdetails_assetlocationgid, assetdetails_bs, assetdetails_cc,"
                            "case when assetdetails_deponhold ='Y' then 1"
                            " else 0"
                            " end  assetdetails_deponhold,assetdetails_deprate, "
                            "assetdetails_enddate, assetdetails_parentgid,0,assetdetails_invoicegid,"
                            "assetdetails_faclringdetailsgid,assetdetails_inwheadergid, "
                            "assetdetails_inwdetailgid, assetdetails_inwarddate, "
                            "assetdetails_mepno, assetdetails_ponum, assetdetails_crnum, assetdetails_debitgid,"
                            "assetdetails_imagepath, assetdetails_vendorname,1,create_by, create_date"
                            " FROM "+str(get_name)+".fa_trn_tassetdetails")
        #print(migration_value5)
        with connections[self.fa_db_serv].cursor() as cursor:
            cursor.execute(migration_value5)

        migration_value6 = ("SET FOREIGN_KEY_CHECKS = 0;SET SQL_SAFE_UPDATES = 0; "
                            "update "+str(post_name)+".faservice_assetdetails a,"+str(self.fa_db)+".faservice_assetheader b "
                            "set a.assetheader_id=b.id,a.updated_by=1,a.updated_date=now() "
                            " where a.barcode=b.barcode ")
        #print(migration_value6)
        with connections[self.fa_db_serv].cursor() as cursor:
            cursor.execute(migration_value6)

        migration_value7 = ("insert into "+str(post_name)+".faservice_clearingheader (assettype, invoicecount, totinvoiceamount, "
                            "tottaxamount, totamount, capitalizedamount,balanceamount,expenseamount, groupno,"
                            " clearingheader_status, remarks,status, created_by, created_date,islock) select faclringheader_assettype,"
                            " faclringheader_invcount, faclringheader_totinvamount, faclringheader_tottaxamount, "
                            "faclringheader_totamount, faclringheader_captalizedamount, faclringheader_balanceamount,"
                            "faclringheader_expenseamount, faclringheader_groupno, case when faclringheader_status = 'PROCESSED'"
                            " then 1 when faclringheader_status = 'DUMMY' then 2 when faclringheader_status = 'PARTIALLY_PROCESSED'"
                            " then 3 when faclringheader_status = 'PENDING' then 4 else 0"
                            " end  faclringheader_status, faclringheader_remarks,1,create_by,now(),1 FROM "+str(get_name)+".fa_trn_tfaclringheader ")
        with connections[self.fa_db_serv].cursor() as cursor:
            cursor.execute(migration_value7)

        migration_value8 = (
            "insert into "+str(post_name)+".faservice_clearingdetails (supplier_id, product_id, branch_id, invoice_id,"
            "invoicedtails_id, apsubcat_id, doctype, productname, qty, balanceqty, invoiceno, invoicedate,"
            "taxamount, otheramount, amount, totamount, markedup, mepno, ponum, ecfnum, clearingdetails_status,"
            "inv_debit_tax,clearingheader_id,status, created_by, created_date) "
            "select  faclringdetails_suppliergid,faclringdetails_productgid, faclringdetails_branchgid, faclringdetails_invoicegid,"
            "faclringdetails_invoicedtailsgid, faclringdetails_apsubcatgid, faclringdetails_doctype,"
            "faclringdetails_productname, faclringdetails_qty, faclringdetails_balanceqty,"
            "faclringdetails_invoiceno, faclringdetails_invoicedate, faclringdetails_taxamount,"
            "faclringdetails_otheramount, faclringdetails_amount, faclringdetails_totamount,"
            "faclringdetails_markedup, faclringdetails_mepno, faclringdetails_ponum,"
            "faclringdetails_ecfnum,  case when faclringdetails_status = 'PROCESSED'"
            " then 1 when faclringdetails_status = 'DUMMY' then 2 when faclringdetails_status = 'PARTIALLY_PROCESSED'"
            " then 3 when faclringdetails_status = 'PENDING' then 4 else 0"
            " end  faclringdetails_status,0,faclringdetails_faclringheader_gid,1,create_by,now() FROM "+str(get_name)+".fa_trn_tfaclringdetails ")
        with connections[self.fa_db_serv].cursor() as cursor:
            cursor.execute(migration_value8)

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj
    def create_singledepreciation(self,dep_obj,emp_id):
        try:
            from_date=dep_obj['from_date']
            to_date=dep_obj['to_date']
            deptyp=dep_obj['deptyp']
            assetdetails_id=dep_obj['assetdetails_id']
            assetdetails_source=dep_obj['assetdetails_source']
            split_todate=datetime.strptime(to_date,'%Y-%m-%d').date()
            from_date=datetime.strptime(from_date,'%Y-%m-%d').date()
            month_val=str(split_todate.month)
            year_val=str(split_todate.year)
            #GROUPING ASSETCAT AND CP DATE------------------------------------------------------------------------------STEP 1
            #Depreciation.objects.all().delete()

            get_querydata=AssetQuery()
            Depreciation_Grp=get_querydata.get_assetDepsingle_Grp(from_date,assetdetails_id)
            facat = [i['assetcat_id'] for i in Depreciation_Grp]
            facap = [i['capdate'] for i in Depreciation_Grp]

            depreciation_data=get_querydata.get_assetDepsingleData(facat,facap,assetdetails_id)

            START_TIME_D = datetime.now()
            START_TIME = START_TIME_D.strftime("%d/%m/%Y %H:%M:%S")
            logger.info('fadep_START_DEPRECIATION_REG - '+START_TIME)
            arr = []
            arr_new = []
            #a=0
           # print(len(depreciation_data))
            assetdeptype=0
            assetid=0
            DepValueTotalD=0
            Is_Salvage=0
            for obj in depreciation_data:
                assetid=obj['id']
                capdate=obj['capdate']
                assetbarcode=obj['assetbarcode']
                asset_valueD = obj['assetdetails_value']
                assetdeptype=obj['assetcat_deptype']
                assetdeprate=obj['asset_deprate']
                assetdetailscost=obj['assetdetails_cost']
                depresglmgmt=obj['depresglmgmt']
                deprate_mgmt=obj['deprate_mgmt']
                # barcode=get_querydata.get_assetbarcode(assetid)
                # clsbalance=get_querydata.get_colsingbalance(barcode)
            #COLSING BALANCE START -----------------------------------------------------------------------------------STEP 2
                clsbalance_sum=get_querydata.get_colsingbalance_sum(assetbarcode,assetid)
                clsbalance_len=len(clsbalance_sum)

                if clsbalance_len >0:
                    clsbalancesum=clsbalance_sum[0]['assetheader_revisedcbtot']
                    if clsbalancesum ==None:
                        clsbalancesum=0

                    if clsbalancesum > 1:
                        #splitfromdate = datetime.strptime(from_date, '%Y-%m-%d').date()
                        datediff = (split_todate - from_date).days
                        DepDaysD = datediff + 1
                        if capdate > from_date:
                            DepDaysD = (split_todate - capdate).days
                            DepDaysD = DepDaysD + 1
                            wdv_fdate = capdate
                            DepCalFrom_DateI = capdate
                        clsbalance = get_querydata.get_is_endlifemet(from_date, split_todate, assetdeptype, assetdeprate,assetdetailscost,capdate,assetid,DepDaysD,asset_valueD)
                        depvaluetotal = clsbalance['depvaluetotal']
                        depreciation_yrclosingblnce = clsbalance['depreciation_yrclosingblnce']
                        depregid_new=get_querydata.get_depre_new(assetid)
                        if depregid_new is None :
                            if obj['capdate'] < from_date:
                                depnew = Depreciation(assetdetails_id=assetid,
                                                      depreciation_fromdate=obj['capdate'],
                                                      depreciation_todate=to_date,
                                                      depreciation_month=month_val,
                                                      depreciation_year=year_val,
                                                      itcvalue=0,
                                                      cavalue=0,
                                                      mgmtvalue=0,
                                                      resgl=depresglmgmt,
                                                      gl=deprate_mgmt,
                                                      depreciation_value=depvaluetotal,
                                                      yrclosingblnce=depreciation_yrclosingblnce,
                                                      created_by=emp_id,
                                                      created_date=now())
                                arr_new.append(depnew)
                            Depreciation.objects.bulk_create(arr_new)
                        ###chk last depdate
                        last_depDate_Chk = get_querydata.get_Last_depDate_Chk(from_date, assetid)
                        # if last_depDate_Chk == False:
                        #     error_obj = Error()
                        #     error_obj.set_code(ErrorMessage.ALREADY_DEPRECIATION_RUN_CHECK)
                        #     error_obj.set_description(ErrorDescription.INVALID_DATE_CHK)
                        #     return error_obj
                       # a += 1
                        enddate_deprate=get_querydata.get_enddate_deprate(assetid)
                        asset_deprate_tagged=enddate_deprate[0]['deprate']
                        assetenddateD=enddate_deprate[0]['enddate']
                        formatted_date = DateFormat(assetenddateD)
                        asset_enddateD=formatted_date.format('Y-m-01')
                        if (asset_deprate_tagged is not None) and (assetdeptype=='SLM'):
                            asset_deprateD=asset_deprate_tagged

                        #split_date = datetime.strptime(from_date, '%Y-%m-%d').date()
                        datediff = ( split_todate-from_date).days
                        depdays = datediff + 1
                        if capdate > from_date:
                            DepDaysD = (split_todate-capdate).days
                            depdays = DepDaysD + 1
                        #DepCalTo_DateD = datetime.strptime(to_date,'%Y-%m-01').date()
                        DepCalTo_DateD = year_val + '-' +month_val + '-01'
                        if str(DepCalTo_DateD) >= asset_enddateD:
                            Is_ast_end_Month='Y'
                        else:
                            Is_ast_end_Month='N'
                        # if str(split_todate) >=asset_enddateD:
                        #     #assetenddateD = datetime.strptime(assetenddateD, '%Y-%m-%d').date()
                        #     DepDaysD = (split_todate-assetenddateD).days
                        #     print(DepDaysD,123)
                        #     depdays = DepDaysD + 1
                        #     if depdays <=0:
                        #         error_obj = Error()
                        #         error_obj.set_code(ErrorMessage.ERROR_ON_DEPRECIATION_DAYS)
                        #         error_obj.set_description(ErrorDescription.INVALID_DAYS)
                        #         response = HttpResponse(error_obj.get(), content_type="application/json")
                        #         return response
                            Is_Salvage = 'Y'



                        if Is_ast_end_Month=='Y':
                            DepValue = get_querydata.get_enddate_deprate(assetid)
                            DepValueTotalD=DepValue[0]['assetdetails_value']
                            # if DepValueTotalD==0:
                            #     error_obj = Error()
                            #     error_obj.set_code(ErrorMessage.ERROR_ON_DEPRECIATION_END_LIFE)
                            #     error_obj.set_description(ErrorDescription.ERROR_FA_DEP)
                            #     return error_obj
                            # if DepValueTotalD >0:
                            #     error_obj = Error()
                            #     error_obj.set_code(ErrorMessage.ERROR_ON_DEPRECIATION_CALCULATE)
                            #     error_obj.set_description(ErrorDescription.ERROR_FA_DEP)
                            #     return error_obj


                        deptmp = Depreciation(assetdetails_id=assetid,
                                                 depreciation_fromdate=obj['capdate'],
                                                 depreciation_todate=to_date,
                                                 depreciation_month=month_val,
                                                 depreciation_year=year_val,
                                                 itcvalue=0,
                                                 cavalue=0,
                                                 mgmtvalue=0,
                                                 resgl=depresglmgmt,
                                                 gl=deprate_mgmt,
                                                 depreciation_value=depvaluetotal,
                                                 yrclosingblnce=depreciation_yrclosingblnce,
                                                 created_by=emp_id,
                                                 created_date=now())
                        arr.append(deptmp)
            #     if a == 10000:
            #         Depreciation.objects.bulk_create(arr)
            #         # print(a)
            #         a = 0
            #         arr = []
            # if len(arr) > 0:
                Depreciation.objects.bulk_create(arr)

                if assetdeptype == 1:
                    value_update = ("UPDATE "+str(self.fa_db)+".faservice_assetdetails SET assetdetails_value = assetdetails_value - cast("+str(DepValueTotalD)+" as decimal(16,2)) "
                    "WHERE id = "+str(assetid)+" ")
                    with connections[self.fa_db_serv].cursor() as cursor:
                        cursor.execute(value_update)
                else:
                    pass


                if Is_Salvage == 'Y':
                    value_update2=("update "+str(self.fa_db)+".faservice_assetdetails set assetdetails_value = 1 where id ="+str(assetid)+" ")
                    with connections[self.fa_db_serv].cursor() as cursor:
                        cursor.execute(value_update2)
                else:
                    pass


            barcode_update_reg = (
                    " update  "+str(self.fa_db)+".faservice_assetheader as z inner join (select sum(case when a.source = 6 or (a.source = 5) "
                    "then assetdetails_cost else 0 end) - sum(Case when a.source = 2  then assetdetails_cost else 0 end) as opening_b,"
                    "a.barcode,c.valuetot as ast_val_bfr_dep,ifnull(sum(case when a.source <> 2 then d.depreciation_value "
                    "else d.depreciation_value * -1 end ),0) as computed_dep,ifnull(case when c.issale = 0 and"
                    "(c.astvalbeforedeptot - c.reviseddeptot) <=  sum(case when a.source <> 2 then d.depreciation_value "
                    "else d.depreciation_value * -1 end ) then (c.astvalbeforedeptot - c.reviseddeptot) -1 when c.issale = 1 and "
                    "(c.astvalbeforedeptot - c.reviseddeptot) <  sum(case when a.source <> 2 then d.depreciation_value else "
                    "d.depreciation_value * -1 end ) then (c.astvalbeforedeptot - c.reviseddeptot) else sum(case when a.source <> 2 then "
                    "d.depreciation_value else d.depreciation_value * -1 end ) end,0) as revised_dep,ifnull(((c.astvalbeforedeptot - reviseddeptot) - "
                    "case when c.issale = 0 and (c.astvalbeforedeptot - c.reviseddeptot) <=  sum(case when a.source <> 2 "
                    "then d.depreciation_value else d.depreciation_value * -1 end ) then (c.astvalbeforedeptot - c.reviseddeptot) -1 "
                    "when c.issale = 1 and   (c.astvalbeforedeptot - c.reviseddeptot) <  sum(case when a.source <> 2 "
                    "then d.depreciation_value else d.depreciation_value * -1 end ) then (c.astvalbeforedeptot - c.reviseddeptot) "
                    "else sum(case when a.source <> 2 then d.depreciation_value else d.depreciation_value * -1 end )end),0)"
                    " as Tot_RevisedCB,ifnull(c.deprestot + sum(case when a.source <> 2 then d.depreciation_value else d.depreciation_value * -1 end ),0) "
                    "as Tot_Deprestot,ifnull(((c.astvalbeforedeptot - reviseddeptot) - case when c.issale = 0 and "
                    "(c.astvalbeforedeptot - c.reviseddeptot) <=  sum(case when a.source <> 2 then d.depreciation_value else d.depreciation_value * -1 end )"
                    "then (c.astvalbeforedeptot - c.reviseddeptot) -1 when c.issale = 1 and  "
                    " (c.astvalbeforedeptot - c.reviseddeptot) <  sum(case when a.source <> 2 then d.depreciation_value else d.depreciation_value * -1 end )"
                    " then (c.astvalbeforedeptot - c.reviseddeptot) else sum(case when a.source <> 2 then d.depreciation_value "
                    "else d.depreciation_value * -1 end ) end),0) as Tot_Assetvalue,d.type,d.depreciation_todate,c.issale,"
                    "depreciation_year,depreciation_month from "+str(self.fa_db)+".faservice_assetdetails as a inner join "+str(self.fa_db)+".faservice_assetheader as c "
                    "on c.barcode = a.barcode inner join "+str(self.fa_db)+".faservice_depreciation as d on d.assetdetails_id = a.id where"
                    " d.depreciation_month = " + str(month_val) + " and d.depreciation_year = " + str(year_val) + " group by barcode) "
                            "as t1 on t1.barcode = z.barcode set z.date = t1.depreciation_todate,"
                            "z.astvalbeforedeptot = t1.ast_val_bfr_dep,"
                            "z.valuetot = t1.Tot_Assetvalue,"
                            "z.computeddeptot = t1.computed_dep,"
                            "z.reviseddeptot = t1.revised_dep,"
                            "z.revisedcbtot = t1.Tot_RevisedCB,"
                            "z.deprestot = t1.Tot_Deprestot,"
                            "z.assetheadermonth = t1.depreciation_month,"
                            "z.assetheaderyear = t1.depreciation_year,"
                            "z.updated_by ="+str(emp_id)+","
                            "z.type = t1.type")
            # print(barcode_update_reg)
            with connections[self.fa_db_serv].cursor() as cursor:
                cursor.execute(barcode_update_reg)

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        except Exception  as excep:
            logger.info('FA_DEPRECIATIONSINGEL_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj
        return success_obj

    def create_itdepreciation(self,from_date,to_date,emp_id):
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            FinYearY = str(from_date.year)
            Findate = FinYearY + '-04-01'
            get_querydata = AssetQuery()

            Dynamic_query = (" select a.assetcat_id,a.id,date_format(a.capdate,'%Y-%m-%d') as capdate ,b.deptype,sum(a.assetdetails_value) As assetdetails_value,"
                             "a.assetdetails_cost,b.itcatname,b.deprate_itc"
                             " from "+str(self.fa_db)+". faservice_assetdetails a inner join "+str(self.fa_db)+" "
                            " .faservice_assetcat b on a.assetcat_id=b.id"
                             " where a.assetdetails_status=1 and a.capdate < '"+str(Findate)+"' "
                             " and a.source=6 and a.entity_id="+str(self._entity_id())+" group by itcatname  ")
            logger.info('ENTRY_LOGGER - ' + str(Dynamic_query))
            with connection.cursor() as cursor:
                cursor.execute(Dynamic_query)
                columns = [x[0] for x in cursor.description]
                rows = cursor.fetchall()
                rows = list(rows)
                df_data = pd.DataFrame(rows, columns=columns)
                resp = {"Message": "Found", "DATA": json.loads(df_data.to_json(orient='records'))}
                if (len(resp['DATA']) == 0):
                    error_obj = NWisefinError()
                    error_obj.set_code('INVALID_DATA')
                    error_obj.set_description('IT DEPRECIATION DATA IS EMPTY')
                    return error_obj

                a = resp['DATA']
                add1_dep_val=0
                add2_dep_val=0
                for i in  a:
                    asset_id=i['id']
                    capdate=i['capdate']
                    assetdetails_value=i['assetdetails_value']
                    itcatname=i['itcatname']
                    deprate_itc=i['deprate_itc']

                    dep_itopening=round(float(assetdetails_value) * float(deprate_itc) / 100,2)
                    #print(dep_itopening,'dep_itopening')
                    logger.info('fadep_ITDEPRECIATION ITOPENING - ' + str(dep_itopening))
                    date = datetime.strptime(Findate, '%Y-%m-%d').date()
                    capdate = datetime.strptime(capdate, '%Y-%m-%d').date()
                    deff_date=(date-capdate)
                    day=deff_date.days+1
                    #print(day,'ITday')
                    #chk_180=date+timedelta(days=day)
                    #print(chk_180,asset_id)
                    logger.info('fadep_ITDEPRECIATION DAY - ' + str(day))
                    if day <= 180:
                        add1_dep_val = round(float(assetdetails_value) * (float(deprate_itc)/ 2) / 100, 2)
                    if day > 180:
                        add2_dep_val = round(float(assetdetails_value) * float(deprate_itc) / 100, 2)
                    #print(add1_dep_val,add2_dep_val,'add')
                    # DepITCAL = get_querydata.get_add1Dep(asset_id,chk_180)
                    # if len(DepITCAL)>0:
                    #     Additions_1=DepITCAL[0].assetdetails_value
                    # else:
                    #     Additions_1=0
                    # add1_dep_val=round(float(Additions_1)*(deprate_itc/2)/100,2)
                    # add2_dep_val=round(float(Additions_1)*float(deprate_itc/100),2)
                    #print(add1_dep_val,add2_dep_val)
                    logger.info('fadep_ITDEPRECIATION 180 VALUES - ' + str(add1_dep_val),str(add2_dep_val))
                    # DepITCAL2 = get_querydata.get_add2Dep(asset_id, chk_180)
                    # if len(DepITCAL2) >0:
                    #     Additions_2 = DepITCAL2[0].assetdetails_value
                    # else:
                    #     Additions_2=0

                    dep_totval=float(add1_dep_val)+float(add2_dep_val)+float(assetdetails_value)
                    #print(dep_totval,'dep_totval')
                    clsblnce=(dep_totval-float(assetdetails_value))
                    #print(clsblnce,'clsblnce')
                    depitc=float(dep_itopening)+float(add1_dep_val)+float(add2_dep_val)
                    #print(depitc,'depitc')
                    wdvval=float(depitc)-float(clsblnce)
                    #print(wdvval,'wdvval')
                    logger.info('fadep_ITDEPRECIATION - ' + str(dep_totval), str(clsblnce),str(depitc),str(wdvval))
                    ITdep = ITDepreciation.objects.create(date=capdate,
                                                          assettotcost=0,
                                                          assettotvalue=assetdetails_value,
                                                          itcatname=itcatname,
                                                          dep_itopening=dep_itopening,
                                                          additions=assetdetails_value,
                                                          revadditions_1=add1_dep_val,
                                                          revadditions_2=add2_dep_val,
                                                          revtot_val=dep_totval,
                                                          dep_deletion=assetdetails_value,
                                                          dep_closingblnce=clsblnce,
                                                          dep_totval=depitc,
                                                          dep_wdvval=wdvval,
                                                          dep_saleval=0,
                                                          created_by=emp_id,
                                                          created_date=now(),
                                                          entity_id=self._entity_id())

                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                return success_obj
        except Exception as excep:
            logger.info('FA_ITDEPRECIATION_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

    def itdepreciation_summary(self,vys_page,user_id,request):
            itdep = ITDepreciation.objects.all()[vys_page.get_offset():vys_page.get_query_limit()]
            resp_list = NWisefinList()
            scope=request.scope
            fa_obj = FaApiService(scope)
            for dep_it in itdep:
                dep_resp = DepreciationResponse()
                #dep_resp.set_depreciation_gid(dep_it.id)
                dep_resp.set_It_Catname(dep_it.itcatname)
                dep_resp.set_Opening_WDV(dep_it.dep_itopening)
                dep_resp.set_Additions_GreaterThan_180Days(dep_it.revadditions_1)
                dep_resp.set_Additions_LessThan_180Days(dep_it.revadditions_2)
                dep_resp.set_Sale_Value(dep_it.dep_deletion)
                dep_resp.set_Closing_Balance(dep_it.dep_closingblnce)
                dep_resp.set_Value_Before_Depreciation((dep_it.dep_itopening + dep_it.revadditions_1 + dep_it.revadditions_2)-dep_it.dep_saleval)
                resp_list.append(dep_resp)
            vpage = NWisefinPaginator(itdep, vys_page.get_index(), 10)
            resp_list.set_pagination(vpage)
            return resp_list

