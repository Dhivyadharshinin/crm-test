import decimal

import pandas as pd

from faservice.util.FaApiService import DictObj, FaApiService
from masterservice.data.response import apsubcategoryresponse
from masterservice.data.response.Hsnresponse import HsnResponse
from masterservice.data.response.apcategoryresponse import ApcategoryResponse
from masterservice.data.response.apsubcategoryresponse import ApsubcategoryResponse
from masterservice.data.response.productcategoryresponse import ProductcategoryResponse
from masterservice.data.response.productresponse import ProductResponse
from masterservice.data.response.producttyperesponse import ProducttypeResponse
from masterservice.data.response.uomresponse import UomResponse
from masterservice.models import APsubcategory
from utilityservice.data.response.nwisefinsuccess import SuccessMessage,NWisefinSuccess,SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinlitelist import NWisefinLiteList
from faservice.models.famodels import AssetDetails, AssetHeader, DepreciationTmp, AssetHeaderTmp, Depreciation, \
    DepSettings, AssetGroup, FaAudit
from django.db.models import Q
from django.db.models import Count,Sum,Max
from datetime import datetime
from nwisefin.settings import logger
import json
class ClearingLock:
    LOCK=0
    UNLOCK=1
class RepostConst:
    TRNBRANCH='1101'
class AssetSource:
    NEW=1
    FAValN=2
    FATRANN=3
    FATRANP=4
    FAValP=5
    FAMAKER=6
    FAWRITEOFF=7
    FASPLITN=8
    FASPLITP=9
    FAMERN=10
    FAMERP=11
    FAIMPN=12
    FAIMPP=13
    FASALEN=14
    source_dict={'NEW':1,'FAValN':2,'FATRANN':3,'FATRANP':4,'FAValP':5,'FAMAKER':6,'FAWRITEOFF':7,
    'FASPLITN':8,'FASPLITP':9,'FAMERN':10,'FAMERP':11,'FAIMPN':12,'FAIMPP':13,'FASALEN':14}
    def get_val(self,no):
        data_list=list(self.source_dict.values())
        if int(no) in data_list:
            ind=list(self.source_dict.values()).index(int(no))
            return list(self.source_dict.keys())[ind]
        else:
            return ''
class AssetEntryType:

    CREDIT= 2
    DEBIT= 1

    CREDIT_VAL='CREDIT'
    DEBIT_VAL='DEBIT'

class AssetStatus:
    ACTIVE=1
    IN_ACTIVE=2
    REJECTED=3
    PENDING=4
    ENTRY_FAILED=5
    PROCESSED = 6


    ACTIVE_VAL = 'ACTIVE'
    IN_ACTIVE_VAL = 'IN_ACTIVE'
    REJECTED_VAL = 'REJECTED'
    PENDING_VAL = 'PENDING'
    ENTRY_FAILED_VAL = 'ENTRY_FAILED'
    PROCESSED_VAL = 'PROCESSED'

    def get_val(self,data):
        if data==self.ACTIVE:
            return self.ACTIVE_VAL
        elif data==self.REJECTED:
            return self.REJECTED_VAL
        elif data==self.PENDING:
            return self.PENDING_VAL
        elif data==self.ENTRY_FAILED:
            return self.ENTRY_FAILED_VAL
        elif data==self.IN_ACTIVE:
            return self.IN_ACTIVE_VAL
class FaConst:
    SALVAGE_VALUE=1
class AssetRequestfor:
    DEFAULT = 0    
    NEW=1
    TRANSFER=2
    SALE=3
    REJECTED=4
    WRITEOFF=5
    IMPAIRMENT=6
    VALUEREDUCTION=7
    CAPDATE=8
    ASSETCAT=9
    SPLIT=10
    MERGE=11
    CAPITALIZE=12
    CLUB=13
    CLUB_VAL='ClUB'
    DEFAULT_VAL='-'
    NEW_VAL='NEW'
    TRANSFER_VAL='TRANSFER'
    SALE_VAL='SALE'
    REJECTED_VAL='REJECTED'
    WRITEOFF_VAL='WRITEOFF'
    IMPAIRMENT_VAL='IMPAIRMENT'
    VALUEREDUCTION_VAL='VALUEREDUCTION'
    CAPDATE_VAL='CAPDATE'
    ASSETCAT_VAL='ASSETCAT'
    SPLIT_VAL='SPLIT'
    MERGE_VAL='MERGE'
    CAPITALIZE_VAL='CAPITALIZE'

    def get_val(self,data):
        if data == 1:
            return self.NEW_VAL
        if data == 0:
            return self.DEFAULT_VAL
        if data == 2:
            return self.TRANSFER_VAL
        if data == 3:
            return self.SALE_VAL
        if data == 4:
            return self.REJECTED_VAL
        if data == 5:
            return self.WRITEOFF_VAL
        if data == 6:
            return self.IMPAIRMENT_VAL
        if data == 7:
            return self.VALUEREDUCTION_VAL
        if data == 8:
            return self.CAPDATE_VAL
        if data == 9:
            return self.ASSETCAT_VAL
        if data == 10:
            return self.SPLIT_VAL
        if data == 11:
            return self.MERGE_VAL
        if data == 12:
            return self.CAPITALIZE_VAL
        if data == 13:
            return self.CLUB_VAL
class AssetDetailsProcess:
    DEFAULT=0
class DEPONHOLD:
    YES=1
    NO=0
class AssetDocs:
    REF_TYPE='FA_ASSET'
    REF_TYPE_VAL=1
    REF_TYPE_VAL_DEPRECIATION=2

    def get_asset_details_type(self,ref_type):
        return self.REF_TYPE_VAL

    def get_PV_details_type(self,ref_type):
        return self.REF_TYPE_VAL_DEPRECIATION

class AssetRequestStatus:
    APPROVED = 1
    REQUESTED=2
    REJECTED=3
    SUBMITTED=4
    PENDING=5

    REQUESTED_VAL='REQUESTED'
    APPROVED_VAL='APPROVED'
    REJECTED_VAL='REJECTED'
    SUBMITTED_VAL='SUBMITTED'
    PENDING_VAL='PENDING'
    def get_val(self,val_id):
        if val_id==self.SUBMITTED:
            return self.SUBMITTED_VAL
        if val_id==self.REQUESTED:
            return self.REQUESTED_VAL
        if val_id==self.REJECTED:
            return self.REJECTED_VAL
        if val_id==self.APPROVED:
            return self.APPROVED_VAL
        if val_id==self.PENDING:
            return self.PENDING_VAL
class AssetDetailsRequestStatus:
    APPROVED = 1
    ENTRY_FAILED=2
    PENDING = 3
    REQUESTED=4
    SUBMITTED = 6
    REJECTED=5


    ENTRY_FAILED_VAL='ENTRY_FAILED'
    REQUESTED_VAL='REQUESTED'
    APPROVED_VAL='APPROVED'
    REJECTED_VAL='REJECTED'
    SUBMITTED_VAL='SUBMITTED'
    PENDING_VAL='PENDING'
    def get_val(self,val_id):
        if val_id==self.SUBMITTED:
            return self.SUBMITTED_VAL
        if val_id==self.ENTRY_FAILED:
            return self.ENTRY_FAILED_VAL
        if val_id==self.REQUESTED:
            return self.REQUESTED_VAL
        if val_id==self.REJECTED:
            return self.REJECTED_VAL
        if val_id==self.APPROVED:
            return self.APPROVED_VAL
        if val_id==self.PENDING:
            return self.PENDING_VAL

class DataBase:
    fa_db = 'fa_service'
    default_db = 'default'

class FaModifyStatus:
    DELETE = 0
    CREATE = 1
    UPDATE = 2

class FaRequestStatusUtil:
    ONBORD = 1
    MODIFICATION = 2

    ONBOARD_VAL = "ONBOARD"
    MODIFICATION_VAL = "MODIFICATION"

class FaRefType:
    ASSETCAT = 1
    DEPRECIATION_SETTING=2
    ASSETLOCATION=3
    CLEARINGHEADER=4
    CLEARINGDETAILS=5
    ASSETDEBIT=6
    ASSETGROUP=7
    ASSETDETAILS=8
    ASSETID = 9
    WRITEOFF = 10
    SPLIT = 11
    MERGE = 12
    IMPAIR = 13
class FA_ROLLBACK_EXCEPTION(Exception):

    '''Raised For Rollback in fa transactions.
     can be used to raise exception and handle manually in outer except to keep transaction intact'''
    ##init for passing any values and converting to variables
    def __init__(self,value=None,*args,**kwargs):
        if value != None:
            self.data=value
        self.__dict__.update(kwargs)

class Asset_Doctype_Code:
    CAP_WORK_IN_PROGRESS = 'CWIP'
    REGULAR='REGULAR'
    BUILDING='BUC'
    def get_gl_no(self,doc_type,request=None):
        scope=request.scope
        fa_obj=FaApiService(scope)
        sub_data=None
        if doc_type=='1':
            sub_data=fa_obj.fetch_code_subcategory(self.REGULAR)
            print(sub_data)
        if doc_type=='2':
            sub_data=fa_obj.fetch_code_subcategory(self.CAP_WORK_IN_PROGRESS)
            print(sub_data)
        if doc_type=='3':
            sub_data=fa_obj.fetch_code_subcategory(self.BUILDING)
            print(sub_data)
        return sub_data
class Fa_Doctype:
    REG = 1 #Regular
    CWIP = 2
    BUC = 3
    FORE = 4

    REG_VAL = "REGULAR"
    CWIP_VAL = "CWIP"
    BUC_VAL = "BUC"
    FORE_VAL = "FORECASTING"

class ClearingHeader_Status:
    PROCESSED=1
    PROCESSED_VAL='PROCESSED'
class RequestForUtil:
    CLUB = 11
    CLUB_VAL='ClUB'
class RequestStatus:
    PENDING=0
    APPROVED=1
    REJECTED=2
    PENDING_VAL ='PENDING'
    APPROVED_VAL = 'APPROVED'
    REJECTED_VAL = 'REJECTED'
def club_requeststatus(number):
    number = int(number)
    if number == RequestStatus.PENDING:
        return RequestStatus.PENDING_VAL
    if number == RequestStatus.APPROVED:
        return RequestStatus.APPROVED_VAL
    if number == RequestStatus.REJECTED:
        return RequestStatus.REJECTED_VAL
def club_requestfor(number):
    number = int(number)
    if number == RequestForUtil.CLUB:
        return RequestForUtil.CLUB_VAL
def assetrequst_status(status_number):
    status_number=int(status_number)
    if status_number == AssetRequestStatus.REQUESTED:
        return AssetRequestStatus.REQUESTED_VAL
    if status_number == AssetRequestStatus.APPROVED:
        return AssetRequestStatus.APPROVED_VAL
    if status_number == AssetRequestStatus.REJECTED:
        return AssetRequestStatus.REJECTED_VAL
    if status_number == AssetRequestStatus.SUBMITTED:
        return AssetRequestStatus.SUBMITTED_VAL
    if status_number == AssetRequestStatus.PENDING:
        return AssetRequestStatus.PENDING_VAL

    else:
        return None

def assetvaluedtl_status(status_number):
    status_number=int(status_number)
    if status_number == AssetStatus.ACTIVE:
        return AssetStatus.ACTIVE_VAL
    elif status_number == AssetStatus.IN_ACTIVE:
        return AssetStatus.IN_ACTIVE_VAL
    elif status_number == AssetStatus.REJECTED:
        return AssetStatus.REJECTED_VAL
    elif status_number == AssetStatus.ENTRY_FAILED:
        return AssetStatus.ENTRY_FAILED_VAL
    elif status_number == AssetStatus.PROCESSED:
        return AssetStatus.PROCESSED_VAL
    else:
        return None

def asset_requestfor_status(requestfor_number):
    requestfor_number=int(requestfor_number)

    if requestfor_number == AssetRequestfor.NEW:
        return AssetRequestfor.NEW_VAL
    elif requestfor_number == AssetRequestfor.TRANSFER:
        return AssetRequestfor.TRANSFER_VAL
    elif requestfor_number == AssetRequestfor.SALE:
        return AssetRequestfor.SALE_VAL
    elif requestfor_number == AssetRequestfor.REJECTED:
        return AssetRequestfor.REJECTED_VAL
    elif requestfor_number == AssetRequestfor.WRITEOFF:
        return AssetRequestfor.WRITEOFF_VAL
    elif requestfor_number == AssetRequestfor.IMPAIRMENT:
        return AssetRequestfor.IMPAIRMENT_VAL
    elif requestfor_number == AssetRequestfor.VALUEREDUCTION:
        return AssetRequestfor.VALUEREDUCTION_VAL
    elif requestfor_number == AssetRequestfor.CAPDATE:
        return AssetRequestfor.CAPDATE_VAL
    elif requestfor_number == AssetRequestfor.ASSETCAT:
        return AssetRequestfor.ASSETCAT_VAL
    elif requestfor_number == AssetRequestfor.SPLIT:
        return AssetRequestfor.SPLIT_VAL
    elif requestfor_number == AssetRequestfor.MERGE:
        return AssetRequestfor.MERGE_VAL
    else:
        return None

def asset_requeststatus(requeststatus_number):
    requeststatus_number=int(requeststatus_number)

    if requeststatus_number == AssetRequestStatus.REQUESTED:
        return AssetRequestStatus.REQUESTED_VAL
    elif requeststatus_number == AssetRequestStatus.APPROVED:
        return AssetRequestStatus.APPROVED_VAL
    elif requeststatus_number == AssetRequestStatus.REJECTED:
        return AssetRequestStatus.REJECTED_VAL
    elif requeststatus_number == AssetRequestStatus.SUBMITTED:
        return AssetRequestStatus.SUBMITTED_VAL
    elif requeststatus_number == AssetRequestStatus.PENDING:
        return AssetRequestStatus.PENDING_VAL
    else:
        return None


def get_fadoctype_list():
    id_array = [Fa_Doctype.REG, Fa_Doctype.CWIP,Fa_Doctype.BUC]
    type_array = [Fa_Doctype.REG_VAL,Fa_Doctype.CWIP_VAL,Fa_Doctype.BUC_VAL]
    length = len(id_array)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = id_array[x]
        vyslite.text = type_array[x]
        vyslist.append(vyslite)

    return vyslist

# source
class SourceType:
    PO = 1
    SPLIT = 2
    MERGE = 3
    NON_PO = 4

    PO_VAL = "PO"
    SPLIT_VAL = "SPLIT"
    MERGE_VAL = "MERGE"
    NON_PO_VAL = "NON_PO"

def get_sourcetype_list():
    id_array = [SourceType.PO, SourceType.SPLIT,SourceType.MERGE,SourceType.NON_PO]
    type_array = [SourceType.PO_VAL,SourceType.SPLIT_VAL,SourceType.MERGE_VAL,SourceType.NON_PO_VAL]
    length = len(id_array)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = id_array[x]
        vyslite.text = type_array[x]
        vyslist.append(vyslite)
    return vyslist

def get_sourcetype(source):
    if source == SourceType.PO:
        obj ={"id":SourceType.PO,"text":SourceType.PO_VAL}
        return obj
    elif source == SourceType.MERGE:
        obj = {"id": SourceType.MERGE, "text": SourceType.MERGE_VAL}
        return obj
    elif source == SourceType.SPLIT:
        obj = {"id": SourceType.SPLIT, "text": SourceType.SPLIT_VAL}
        return obj
    elif source == SourceType.NON_PO:
        obj = {"id": SourceType.NON_PO, "text": SourceType.NON_PO_VAL}
        return obj
    else:
        return None

# ClearingHeaderStatus
class ClearingHeaderStatus:
    PARTIALLY_CAPITALIZED=1
    CAPITALIZED=2
    PENDING =-1
    PARTIALLY_CAPITALIZED_VAL = "PARTIALLY_CAPITALIZED"
    CAPITALIZED_VAL = "CAPITALIZED"
    PENDING_VAL = 'PENDING'

def get_clearingheader_status(source):
    if source == ClearingHeaderStatus.PARTIALLY_CAPITALIZED:
        obj ={"id":ClearingHeaderStatus.PARTIALLY_CAPITALIZED,"text":ClearingHeaderStatus.PARTIALLY_CAPITALIZED_VAL}
        return obj
    elif source == ClearingHeaderStatus.CAPITALIZED:
        obj = {"id": ClearingHeaderStatus.CAPITALIZED, "text": ClearingHeaderStatus.CAPITALIZED_VAL}
        return obj
    elif source == ClearingHeaderStatus.PENDING:
        obj = {"id": ClearingHeaderStatus.PENDING, "text": ClearingHeaderStatus.PENDING_VAL}
        return obj
    else:
        return None

class AssetQuery:
    def get_assetDep_Grp(self,split_todate):
        from django.db.models import F
        condition = Q(assetdetails_status=AssetStatus.ACTIVE) & ~Q(assetdetails_value=1) & Q(capdate__lte=split_todate) & Q(deponhold=0)\
                    #& Q(barcode='KVBB22OBOFF00002')
        obj = AssetDetails.objects.values('assetcat__id','id','capdate','assetcat__deptype').filter(condition).order_by().annotate(assetcat_id=F('assetcat__id'))
        obj_count=obj.count()
            #.distinct().annotate(id=Count("id"))
        logger.info('fadep_DEPRECIATION_GROUP_QUERY_1 - ' + str(obj.query))
        #[0:1000]
        #print(obj.query)
        arr = []
        # for i in obj:
        #     data = {"assetcat_id": i['assetcat__id'], "capdate": i['capdate']}
        #     arr.append(data)
        return obj,obj_count
    def get_assetitDep_Grp(self,split_todate):
        from django.db.models import F
        condition = Q(assetdetails_status=AssetStatus.ACTIVE) & Q(capdate__lt=split_todate) & Q(source=6)\
                    #& Q(barcode='KVBB22OBOFF00002')
        obj = AssetDetails.objects.values('assetcat__itcatname')\
            .filter(condition).order_by().annotate(assetcat__itcatname=Count('assetcat__itcatname'))
        obj_count=obj.count()
        logger.info('fadep_ITDEPRECIATION_GROUP_QUERY_1 - ' + str(obj.query),str(obj_count))
        return obj
    def get_add1Dep(self,asset_id,octdata):
        from django.db.models import F
        condition = Q(id=asset_id) & Q(capdate__lt=octdata)
        obj = AssetDetails.objects.filter(condition)
        logger.info('fadep_ITDEPRECIATION_GROUP_QUERY_1 - ' + str(obj.query))
        return obj
    def get_add2Dep(self,asset_id,octdata):
        from django.db.models import F
        condition = Q(id=asset_id) & Q(capdate__gte=octdata)
        obj = AssetDetails.objects.filter(condition)
        #print(obj_count)
        #print(len(obj),'asdf')
        # if len(obj)==0:
        #     obj=0
        #print(obj.query)
       # logger.info('fadep_ITDEPRECIATION_GROUP_QUERY_1 - ' + str(obj.query))
        return obj

    def get_assetDepData(self,assetcat,grpfromdate):
        from django.db.models import F
        condition = Q(assetdetails_status=AssetStatus.ACTIVE) & ~Q(assetdetails_value=1) & Q(capdate__in=grpfromdate) & \
                    Q(deponhold=0)& Q(assetcat_id__in=assetcat)\
                    #& Q(barcode='KVBB22OBOFF00002')
        #condition1 =~Q(assetcat__depgl_mgmt=0)|~Q(assetcat__deprate_ca=0)|~Q(assetcat__deprate_mgmt=0)
        #condition2=condition&condition1
        obj = AssetDetails.objects.values('capdate','assetdetails_cost',
                                          'assetdetails_value','assetcat__deptype','assetcat__deprate','assetcat__lifetime',
                                          'assetcat__deprate_mgmt','assetcat__depresgl_mgmt','id','barcode'
                                          ).annotate(assetcat__id=Count("assetcat__id"),assetcat_id=F('assetcat__id'),
                                                     assetcat_deptype=F('assetcat__deptype'),asset_deprate=F('assetcat__deprate'),
                                                     assetcat_lifetime=F('assetcat__lifetime'),deprate_mgmt=F('assetcat__deprate_mgmt'),
                                                     depresglmgmt=F('assetcat__depresgl_mgmt'),assetbarcode=F('barcode')).filter(condition).order_by()
        #[0:1000]
        #print(obj.query)
        # logger.info('fadep_DEPRECIATION_GROUP_QUERY_2 - ' + str(obj.query))
        # arr = []
        # for i in obj:
        #     data = {"capdate": i['capdate'],"assetdetails_cost": i['assetdetails_cost'],
        #             "assetdetails_value": i['assetdetails_value'],"assetcat_deptype": i['assetcat__deptype'],
        #             "asset_deprate":i['assetcat__deprate'],"assetcat_lifetime": i['assetcat__lifetime'],
        #             "deprate_mgmt":i['assetcat__deprate_mgmt'],"depresglmgmt":i['assetcat__depresgl_mgmt'],
        #             "id":i['id'],"assetbarcode":i['barcode']}
        #     arr.append(data)
        return obj
    #asset_colsing_balance
    def get_assetbarcode(self,assetdetailsid):
        condition = Q(assetdetails_id=assetdetailsid)
        obj = AssetDetails.objects.filter(condition).values('id','barcode')
        arr = []
        # for i in obj:
        #     data = {"id": i['id'], "barcode": i['barcode']}
        #     arr.append(data)
        return obj

    def get_colsingbalance(self,asset_barcode):
        condition = Q(barcode=asset_barcode)
        obj = AssetHeader.objects.filter(condition).order_by('-id')[0].values('id','revisedcbtot')
        arr = []
        # for i in obj:
        #     data = {"id": i['id'], "revisedcbtot": i['revisedcbtot']}
        #     arr.append(data)
        return obj

    def get_colsingbalance_sum(self,asset_barcode,assetid):
        from django.db.models import F
        condition =  Q(id=assetid) \
                     #& Q(assetheader__barcode=asset_barcode)
        obj = AssetDetails.objects.filter(condition).values('barcode').annotate(assetheader_revisedcbtot=Sum('assetheader__revisedcbtot'),)
        arr = []
        # for i in obj:
        #     data = {"assetheader_revisedcbtot":i['assetheader_revisedcbtot'],"barcode":i['barcode']}
        #     arr.append(data)
        return obj

    def get_Last_depDate_Chk(self,from_date,assetid):
        condition =  Q(assetdetails_id=assetid)
        obj = Depreciation.objects.filter(condition).aggregate(Max('depreciation_todate'))
        depreciation_todate=obj['depreciation_todate__max']
        if depreciation_todate is not None:
            if from_date <= depreciation_todate:
                return True
        return False

    def get_is_endlifemet(self,from_date,split_todate,assetdeptype,assetdeprate,assetdetailscost,capdate,assetid,DepDaysD,asset_valueD):
        #split_fromdate = datetime.strptime(from_date, '%Y-%m-%d').date()
        split_fromdate = from_date
        todate_day=split_todate.day
        DepCalTo_year = int(split_todate.year)
        DepCalTo_month = int(split_todate.month)
        FinYearY = int(split_fromdate.year)
        month_val = int(split_fromdate.month)
        finyear=FinYearY+1
        finyear365_check=finyear %4
        if finyear365_check==0:
            yrdays=366
        else:
            yrdays=365
        if assetdeptype=='SLM':
            depvalueperday= round(((assetdetailscost * assetdeprate) / 100),2)/yrdays
            depvaluetotal=round(DepDaysD*depvalueperday,2)
            depreciationyrclosingblnce = 0
        elif assetdeptype=='WDV':
            finyear = int(split_fromdate.year)
            if (month_val >=1) and (month_val <=3):
                finyear=FinYearY-1
            FinYearD=str(finyear)+'-04'+'-01'
            FinYearD = datetime.strptime(FinYearD, '%Y-%m-%d').date()
            dateFinYear=(FinYearD-capdate)
            num_months = (FinYearD.year - capdate.year) * 12 + (FinYearD.month - capdate.month)
            CheckFinYear=(dateFinYear.days/3)+1
            #print(CheckFinYear,'dep')
            if CheckFinYear > 0:
                fin_date=(str(FinYearY+1)+'-04'+'-01')
                conditions=Q(assetdetails=assetid)& Q(depreciation_fromdate__lte=FinYearD)& \
                           Q(depreciation_fromdate__gt=fin_date)
                obj=Depreciation.objects.filter(conditions).aggregate(Sum('depreciation_value'))
                WDV_AssetValue = obj['depreciation_value__sum']
                if WDV_AssetValue is None:
                    WDV_AssetValue = 0
            elif CheckFinYear <= 0:
                WDV_AssetValue=0
                fin_date = (str(FinYearY+1)+'-04'+'-01')
                conditions = Q(assetdetails=assetid) & Q(depreciation_fromdate__lte=FinYearD) & \
                             Q(depreciation_fromdate__gt=fin_date)
                obj = Depreciation.objects.filter(conditions).aggregate(Sum('depreciation_value'))

                if obj['depreciation_value__sum'] is not None:
                    WDV_AssetValue = obj['depreciation_value__sum']
                else:
                    WDV_AssetValue=0
            else:
                WDV_AssetValue=0
            WDV_AssetValue_fc = 0
            WDV_Yr_Closing_Blnce = 0
            conditions = Q(assetdetails=assetid) & Q(depreciation_month=3) & \
                         Q(depreciation_year=FinYearY)
            objtmp = DepreciationTmp.objects.filter(conditions).values('yrclosingblnce')
            if len(objtmp)>0:
                WDV_Yr_Closing_Blnce = objtmp[0]['yrclosingblnce']
                if WDV_Yr_Closing_Blnce is not None and WDV_Yr_Closing_Blnce != 0:
                    depvaluetotal = WDV_Yr_Closing_Blnce
            wdv_asset_value = asset_valueD + WDV_AssetValue
            DepValuePerDay = round(((wdv_asset_value * assetdeprate) / 100), 2) / yrdays
            depvaluetotal = round(DepDaysD * DepValuePerDay, 2)
            depreciationyrclosingblnce = 0
            if DepCalTo_month ==3 and todate_day== 31:
                fin_date = (str(FinYearY + 1) + '-04' + '-01')
                conditions = Q(assetdetails=assetid) & Q(depreciation_fromdate__lte=FinYearD) & \
                             Q(depreciation_fromdate__gt=fin_date)
                obj = DepreciationTmp.objects.filter(conditions).aggregate(Sum('depreciation_value'))
                if obj['depreciation_value__sum'] is not None:
                    Forecast_DepValue_DB = obj['depreciation_value__sum']
                    depreciationyrclosingblnce=asset_valueD-depvaluetotal
                    depreciationyrclosingblnce=round(depreciationyrclosingblnce-Forecast_DepValue_DB,2)

        dict_data={'depvaluetotal':depvaluetotal,'depreciation_yrclosingblnce':depreciationyrclosingblnce}
        return dict_data
    def get_depreciation_assetid(self,month_val,year_val):
        condition = Q(depreciation_month=month_val)& Q(depreciation_year=year_val)
        obj = DepreciationTmp.objects.filter(condition).values('assetdetails__id','assetdetails__source','depreciation_fromdate',
                                                                   'depreciation_value','assetdetails__barcode',
                                                                   'depreciation_todate','depreciation_month',
                                                                   'depreciation_year','type'
                                                                   #'assetdetails__assetheadertmp__id','assetdetails__assetheadertmp__assetdetailsbarcode'
                                                                    ).annotate(id=Count('id'))[0:200000]
        print(len(obj))
        #print(obj.query)
        arr = []
        for i in obj:
            source=i['assetdetails__source']
            depreciation_value=i['depreciation_value']
            if source != 2:
                dep_sum = depreciation_value
            else:
                dep_sum = depreciation_value * -1
            data = {"id": i['id'], "assetdetails_id": i['assetdetails__id'],
                    "source": i['assetdetails__source'], "depreciation_value": i['depreciation_value'],
                    "depreciation_fromdate": i['depreciation_fromdate'],
                    "depreciation_todate": i['depreciation_todate'],
                    "depreciation_month": i['depreciation_month'], "depreciation_year": i['depreciation_year'],
                    "type": i['type'],
                    "barcode": i['assetdetails__barcode'], "dep_sum": dep_sum}
            arr.append(data)
            # print(arr)
        return arr
    def get_assettmpdetails(self,barcode):
        condition = Q(assetdetailsbarcode__in=barcode)
        obj = AssetHeaderTmp.objects.filter(condition)
        return obj
    def get_enddate_deprate(self, asset_id):
        condition = Q(id=asset_id)
        obj = AssetDetails.objects.filter(condition).values('deprate','enddate','assetdetails_value')
        return obj

    def get_depre_new(self, asset_id):
        condition = Q(assetdetails_id=asset_id)
        obj = Depreciation.objects.filter(condition).values('id')
        return obj
    def get_depsetting(self):
        condition = Q(status=1)& Q(doctype='MGMT')
        obj=DepSettings.objects.filter(condition).values('doctype')
        return obj

    def get_AssetGroup(self,grpid):
        obj = AssetGroup.objects.filter(status=1,id=grpid)
        obj1=len(obj)
        if obj1 ==0:
            grp_no=None
        else:
            grp_no = obj[0].number
        return grp_no

    def get_assetDepsingle_Grp(self,split_todate,assetdetails_id):
        condition = Q(assetdetails_status=AssetStatus.ACTIVE) & ~Q(assetdetails_value=1) & Q(capdate__lte=split_todate) & Q(deponhold=0)\
                    & Q(id=assetdetails_id)
        obj = AssetDetails.objects.values('assetcat__id','id','capdate','assetcat__deptype').filter(condition).order_by()
            #.distinct().annotate(id=Count("id"))
        logger.info('fadep_DEPRECIATION_GROUP_QUERY_1 - ' + str(obj.query))
        #[0:1000]
        #print(obj.query)
        arr = []
        for i in obj:
            data = {"assetcat_id": i['assetcat__id'], "capdate": i['capdate']}
            arr.append(data)
        return arr
    def get_assetDepsingleData(self,assetcat,grpfromdate,assetdetails_id):
        condition = Q(assetdetails_status=AssetStatus.ACTIVE) & ~Q(assetdetails_value=1) & Q(capdate__in=grpfromdate) & \
                    Q(deponhold=0)& Q(assetcat_id__in=assetcat) & Q(id=assetdetails_id)
        obj = AssetDetails.objects.values('capdate','assetdetails_cost',
                                          'assetdetails_value','assetcat__deptype','assetcat__deprate','assetcat__lifetime',
                                          'assetcat__deprate_mgmt','assetcat__depresgl_mgmt','id','barcode'
                                          ).annotate(assetcat__id=Count("assetcat__id")).filter(condition).order_by()

        logger.info('fadep_DEPRECIATION_GROUP_QUERY_2 - ' + str(obj.query))
        #print(obj.query)
        arr = []
        for i in obj:
            data = {"capdate": i['capdate'],"assetdetails_cost": i['assetdetails_cost'],
                    "assetdetails_value": i['assetdetails_value'],"assetcat_deptype": i['assetcat__deptype'],
                    "asset_deprate":i['assetcat__deprate'],"assetcat_lifetime": i['assetcat__lifetime'],
                    "deprate_mgmt":i['assetcat__deprate_mgmt'],"depresglmgmt":i['assetcat__depresgl_mgmt'],
                    "id":i['id'],"assetbarcode":i['barcode']}
            arr.append(data)
        return arr


def dictdefault(data):
    if isinstance(data,ProductResponse):
        return data.__dict__
    if isinstance(data,ApcategoryResponse):
        return data.__dict__
    if isinstance(data,APsubcategory):
        return data.__dict__
    if isinstance(data,HsnResponse):
        return data.__dict__
    if isinstance(data,UomResponse):
        return data.__dict__
    if isinstance(data,datetime):
        return str(data)
    if isinstance(data,decimal.Decimal):
        return int(data)
    if isinstance(data,ApsubcategoryResponse):
        return data.__dict__
    if isinstance(data,ProducttypeResponse):
        return data.__dict__
    if isinstance(data,ProductcategoryResponse):
        return data.__dict__
    else:
        try:
            return data.__dict__
        except:
            return str(data)


def data_group_by(queryset,fields):
    all_fields=queryset[0].keys()
    agg_funcs=dict.fromkeys(all_fields,'first')
    df=pd.DataFrame(queryset).groupby(by=fields).agg(agg_funcs)
    df_records=df.to_dict('records')
    obj_list=[]
    for data in df_records:
        dictobj=DictObj()
        obj_list.append(data)
    return obj_list
def get_checker_reason_from_audit(ref_type,ref_id):
    try:
        audit_data=FaAudit.objects.filter(ref_type=ref_type,ref_id=ref_id).order_by('-id')[0]
        data=json.loads((audit_data.data).replace("'",'"'))
        data_obj=DictObj()
        data_obj=data_obj.get_obj(data)
        checker_reason=data.reason
        return checker_reason
    except:
        return 'None'
def put_checker_reason_to_audit(ref_type,ref_id,data,request):
    try:
        user=request.user.id
        audit_data=FaAudit.objects.create( ref_id = ref_id,
        ref_type =ref_type,
        data =json.dumps(data),
        user_id = user,
        req_status = AssetStatus.ACTIVE)
    except:
        pass

