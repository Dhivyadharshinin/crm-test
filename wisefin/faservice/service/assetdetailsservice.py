import base64
import datetime
import json
import traceback

import tzlocal
from pandas.core.computation import scope

from faservice.util.fautil import AssetQuery, put_checker_reason_to_audit, ClearingLock, FaConst, AssetEntryType
from faservice.data.request.assetheaderrequest import AssetHeaderRequest
from faservice.service.assetheaderservice import AssetheaderService
import pandas
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.db.models import Q, Count, QuerySet
import boto3
import pandas as pd
import dateutil.tz
from dateutil import parser
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponse
from PIL import  Image
from django.utils import timezone
# from faservice.controller.assetdetailscontroller import fetch_codegenerator_list
from decimal import Decimal
import faservice.controller.assetdetailscontroller
from docservice.util.docutil import DocModule, DocPrefix
from faservice.data.request.assetdetailsrequest import validate_data
from faservice.data.response.assetdetailsresponse import AssetDetailsResponse, FapvRespon
from faservice.data.response.assetlocationresponse import AssetLocationResponse
from faservice.data.response.assetupdateresponse import AssetUpdateResponse , Asset_Details_Response
from faservice.data.response.faauditresponse import FaAuditResponse
from faservice.models.famodels import AssetLocation, AssetDetails, AssetGroup, AssetCat, ClearingHeader, ClearingDetails,AssetHeader
from faservice.service.assetcatservice import AssetCatService
from faservice.service.assetdetailupdateservice import AssetUpdateService
from faservice.service.assetentryservice import AssetentryService
from faservice.service.assetgroupservice import AssetGroupService
from faservice.service.assetlocationservice import AssetLocationService
from faservice.service.faauditservice import FaAuditService
from faservice.util.FaApiService import FaApiService, DictObj
from faservice.util.fautil import FaModifyStatus, FaRefType, FaRequestStatusUtil, ClearingHeaderStatus, AssetStatus, \
    AssetDocs, dictdefault, AssetSource, AssetDetailsProcess, DEPONHOLD, Fa_Doctype, AssetDetailsRequestStatus, \
    assetvaluedtl_status, RequestStatus
from faservice.util.fautil import FaModifyStatus, FaRefType, FaRequestStatusUtil, AssetRequestfor, AssetRequestStatus
from faservice.data.response.assetdetailsresponse import AssetDetailsResponse, Totalcount
from faservice.data.response.assetlocationresponse import AssetLocationResponse
from faservice.data.response.faauditresponse import FaAuditResponse
from faservice.models.famodels import *
from faservice.service.clearingdetailsservice import ClearingDetailsService
from faservice.service.clearingheaderservice import ClearingHeaderService
from faservice.service.faauditservice import FaAuditService
from faservice.util.FaApiService import FaApiService
from faservice.util.fautil import FaModifyStatus, FaRefType, FaRequestStatusUtil
from nwisefin import settings
from nwisefin.settings import logger
from userservice.service.employeeservice import EmployeeService
from utilityservice.data.response.nwisefinerror import NWisefinError as Error, NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinlist import NWisefinList

from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from faservice.models.famodels import AssetCapDate



from django.db import transaction

from utilityservice.service.api_service import ApiService
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


@transaction.atomic
class AssetDetailsService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
    #Create assetdetails(REG,CWIP,BUC)
    def create_assetdetails(self, assetdtlsobj_list, emp_id,request,assetgroup_id,assetdetails_id=None):
        scope=request.scope
        fa_obj = FaApiService(scope)
        reqstatus = FaRequestStatusUtil.ONBORD
        clearing_head = assetdtlsobj_list.ASSET[0].FAClearnceHeader_id
        clearing_head_data = ClearingHeader.objects.get(id=clearing_head)
        clearing_head_data.islock = ClearingLock.LOCK
        clearing_head_data.save()
        capped_amount=0
        try:
            ponum=mepno=initial_id=1
            initial_date=now()

            assetdtls_array=list()
            clearing_head=assetdtlsobj_list.ASSET[0].FAClearnceHeader_id
            clearing_head_data=ClearingHeader.objects.get(id=clearing_head)
            clearing_head_data.islock=ClearingLock.LOCK
            try:
                start_id = int(AssetDetails.objects.latest('pk').pk) + 1
            except:
                start_id=1
            totval = 0
            assetgrp_id=0
            subsequent_cap = None
            is_apo_list=[]
            appo_id=[]
            for assetdetails in assetdtlsobj_list.ASSET:
                is_apo_list.append(assetdetails.is_appor)
                if assetdetails.is_appor==True:
                    appo_id.append(assetdetails.FAClearnceDetails_id)
            if all(is_apo_list):
                apo=False
            else:
                apo=True
            for assetdetails_obj in assetdtlsobj_list.ASSET:
                clearing_det=ClearingDetails.objects.get(id=assetdetails_obj.FAClearnceDetails_id)
                vendor_name = fa_obj.fetch_data(clearing_det.supplier_id, request)['name']

                if clearing_det.balanceqty-assetdetails_obj.QTY >0:
                    if clearing_det.doctype != 3:
                        clearing_det.balanceqty-=assetdetails_obj.QTY
                elif clearing_det.balanceqty-assetdetails_obj.QTY==0:
                    not_in=[Fa_Doctype.CWIP,Fa_Doctype.BUC]
                    if int(clearing_det.doctype) not in not_in:
                        clearing_det.balanceqty -= assetdetails_obj.QTY
                        clearing_det.status=ClearingHeaderStatus.CAPITALIZED
                else:
                    pass #return error obj
                clearing_det.updated_by=emp_id
                clearing_det.updated_date=now()
                clearing_det.save()
                if assetdtlsobj_list.Doc_Type == 'REGULAR':
                    if apo:
                        if assetdetails_obj.is_appor==True:
                                clearing_det.status=0
                                clearing_det.save()
                                continue
                        else:
                            clrng_list=ClearingDetails.objects.filter(clearingheader_id=clearing_det.clearingheader_id).exclude(id__in=appo_id)
                            for record in clrng_list:
                                record.markedup=assetdtlsobj_list.MarkedUpRatio
                                record.save()
                    else:
                        pass
                    if assetdetails_obj.QTY > 1:#check Qty > 1 for regular doc_type
                        if assetgroup_id==None:#Create new assetgroup for assetgroupid=nil and
                            try:
                                asset_grpdata=[AssetGroup.objects.latest('id')]
                            except:
                                asset_grpdata=[]
                            if len(asset_grpdata)>0:
                                num = asset_grpdata[0].number + 1
                            else:
                                num=1
                            subcat=fa_obj.fetchsubcategory(AssetCat.objects.get(id=assetdetails_obj.Asset_Cat_id).subcategory_id,request)
                            asset_grp_data=AssetGroup()
                            asset_grp_data.number=num
                            if isinstance(subcat,DictObj):
                                asset_grp_data.apcatategory=subcat.category_id
                            else:
                                if isinstance(subcat,list):
                                    asset_grp_data.apcatategory=subcat[1]['category_id']
                                else:
                                    asset_grp_data.apcatategory=subcat.category_id.id
                            if isinstance(subcat,list):
                                asset_grp_data.apsubcatategory = subcat[0]
                            else:
                                asset_grp_data.apsubcatategory=subcat.id
                            print(assetdetails_obj.CP_Date['dates'])
                            asset_grp_data.capdate=parser.parse(assetdetails_obj.CP_Date['dates'])
                            asset_grp_data.assetvalue=assetdetails_obj.Asset_Value
                            asset_grp_data.branch_id=str(assetdetails_obj.Branch_id)
                            asset_grp_data.created_by=emp_id
                            asset_grp_data.save()
                            assetgrp_id=asset_grp_data.id
                        else:
                            assetgrp_id=assetgroup_id
                        assetgrp_id=assetgrp_id
                else:

                    if assetgroup_id == None:  # Create new assetgroup for assetgroupid=nil and
                        try:
                            asset_grp_data = [AssetGroup.objects.latest('id')]
                        except:
                            asset_grp_data=[]
                        if len(asset_grp_data) > 0:
                            num = asset_grp_data[0].number + 1
                        else:
                            num=1
                        subcat = fa_obj.fetchsubcategory(
                            AssetCat.objects.get(id=assetdetails_obj.Asset_Cat_id).subcategory_id,request)
                        if isinstance(subcat,list):
                            dict_obj=DictObj()
                            subcat=dict_obj.get_obj(subcat[1])
                            cat_id=subcat.category_id
                        else:
                            cat_id=subcat.category_id.id
                        asset_grp_data=AssetGroup.objects.create(
                            number=num,
                            apcatategory=cat_id,
                            apsubcatategory=subcat.id,
                            capdate=parser.parse(assetdetails_obj.CP_Date['dates']),
                            assetvalue=assetdetails_obj.Asset_Value,
                            branch_id=str(assetdetails_obj.Branch_id),
                            created_by=emp_id,
                            created_date=now()
                        )
                        assetgrp_id=asset_grp_data.id
                    else:
                        asst_srv = AssetGroupService(scope)
                        asstgrp_data=AssetGroup.objects.get(number=assetgroup_id)
                        assetgrp_id =asstgrp_data.id
                        subsequent_cap=True
                asset_data=None
                if subsequent_cap:
                    details_id=assetdtlsobj_list.assetdetails_id
                    get_id=details_id.split('/')
                    asset_data=AssetDetails.objects.filter(assetdetails_id__icontains=get_id[0],assetdetails_status=AssetStatus.ACTIVE).order_by('id').latest('id')
                    if asset_data.branch_id!=assetdetails_obj.Branch_id:
                        clr_id = clearing_head_data.id
                        clearing_head_data = ClearingHeader.objects.get(id=clr_id)
                        clearing_head_data.islock = ClearingLock.UNLOCK
                        clearing_head_data.save()
                        err=Error()
                        err.set_code(ErrorMessage.INVALID_branch_ID)
                        err.set_description(ErrorDescription.SAME_BRANCH_NEED_TO_SELECT)
                        return err
                    if asset_data.assetlocation_id!=assetdetails_obj.Location_id:
                        clr_id = clearing_head_data.id
                        clearing_head_data = ClearingHeader.objects.get(id=clr_id)
                        clearing_head_data.islock = ClearingLock.UNLOCK
                        clearing_head_data.save()
                        err=Error()
                        err.set_code(ErrorMessage.INVALID_ASSETLOCATION_ID)
                        err.set_description(ErrorDescription.SAME_LOCATION_NEED_TO_SELECT)
                        return err
                    if asset_data.assetdetails_bs!=assetdetails_obj.BS_NO:
                        clr_id = clearing_head_data.id
                        clearing_head_data = ClearingHeader.objects.get(id=clr_id)
                        clearing_head_data.islock = ClearingLock.UNLOCK
                        clearing_head_data.save()
                        err=Error()
                        err.set_code(ErrorMessage.INVALID_CCBS_ID)
                        err.set_description(ErrorDescription.SAME_BS_CC_NEED_TO_SELECT)
                        return err
                    if asset_data.assetdetails_cc!=assetdetails_obj.CC_NO:
                        clr_id = clearing_head_data.id
                        clearing_head_data = ClearingHeader.objects.get(id=clr_id)
                        clearing_head_data.islock = ClearingLock.UNLOCK
                        clearing_head_data.save()
                        err=Error()
                        err.set_code(ErrorMessage.INVALID_CCBS_ID)
                        err.set_description(ErrorDescription.SAME_BS_CC_NEED_TO_SELECT)
                        return err

                    details_id=asset_data.assetdetails_id
                    get_id=details_id.split('/')
                    asset_id=get_id[0]+'/'+str(int(get_id[1])+1).zfill(2)+'/'+str(int(get_id[2])+1).zfill(2)
                    asset_dtls_id_list={'data':[asset_id,]}
                else:
                    asst_obj=FaApiService(scope)
                    subcat=AssetCat.objects.get(id=assetdetails_obj.Asset_Cat_id).subcategory_id
                    params={'product_id':assetdetails_obj.Product_id,'subcat':subcat,'QTY':assetdetails_obj.QTY,'branch':assetdetails_obj.Branch_id}
                    asset_dtls_id_list=asst_obj.fetch_codegenerator_list_new(params,request)
                    asset_dtls_id_list=json.loads(asset_dtls_id_list.content.decode('utf-8'))
                img_resp=None
                resp=[]
                fa_obj=FaApiService(scope)
                for file in assetdetails_obj.files:
                    for request_file in request.FILES.getlist('file'):
                        if file == request_file.name:
                            fa_docs = AssetDocs()
                            mod_obj=DocModule()
                            doc_param = {"module": mod_obj.FA, "ref_type": fa_docs.REF_TYPE_VAL, "ref_id": assetdetails_obj.FAClearnceDetails_id}
                            img_resp = fa_obj.upload_single_file(request_file,doc_param,request)
                            resp.append(json.loads(img_resp))
                print(asset_dtls_id_list)
                if assetdetails_obj.QTY==1 and clearing_det.doctype==str(Fa_Doctype.REG):
                    assetgrp_id=0
                for i,asst_id in zip(range(assetdetails_obj.QTY),asset_dtls_id_list['data']):
                    if subsequent_cap == True:                        #
                        try:
                            asst_hdr = AssetHeader.objects.filter(barcode=asst_id[:-6])
                            if len(asst_hdr) > 0:
                                asst_head_id = asst_hdr[0].id
                                asst_head_data = AssetHeader.objects.get(id=asst_head_id)
                                asst_head_data.valuetot+=assetdetails_obj.Asset_Value
                                asst_head_data.astvalbeforedeptot+=assetdetails_obj.Asset_Value
                                asst_head_data.costtot+=assetdetails_obj.Asset_Value
                                asst_head_data.revisedcbtot+=assetdetails_obj.Asset_Value
                                asst_head_data.astvalbeforedeptot+=assetdetails_obj.Asset_Value
                                asst_head_data.save()
                            else:
                                continue  ### return error
                        except Exception as e:
                            clearing_head_data.islock=ClearingLock.UNLOCK
                            clearing_head_data.save()
                            errr = str(e)

                    else:

                        asst_header = AssetheaderService(scope)
                        header_data = {"barcode":asst_id[:-6], "date":now(), "assetheadermonth":datetime.datetime.now().month,
                        "assetheaderyear": datetime.datetime.now().month, "astvalbeforedeptot": assetdetails_obj.Asset_Value/assetdetails_obj.QTY, "computeddeptot": 0, "reviseddeptot": 0,
                        "revisedcbtot":assetdetails_obj.Asset_Value/assetdetails_obj.QTY, "deprestot": 0, "costtot":(assetdetails_obj.Asset_Value/assetdetails_obj.QTY)*float(assetdtlsobj_list.MarkedUpRatio), "valuetot":(assetdetails_obj.Asset_Value/assetdetails_obj.QTY)*float(assetdtlsobj_list.MarkedUpRatio), "type": "1", "issale": 0}
                        asst_head_obj = AssetHeaderRequest(header_data)
                        res=asst_header.create_assetheader(asst_head_obj)
                        asst_head_data=AssetHeader.objects.get(id=res.id)

                    fa_obj=FaApiService(scope)
                    asst_cat_data=AssetCat.objects.get(id=assetdetails_obj.Asset_Cat_id)
                    subcat=fa_obj.fetchsubcategory(asst_cat_data.subcategory_id,request)
                    if isinstance(subcat,list):
                        dict_obj=DictObj()
                        subcat=dict_obj.get_obj(subcat[1])

                    asst_dep_rate=asst_cat_data.deprate
                    end_date=parser.parse(assetdetails_obj.CP_Date['dates'])+relativedelta(months=asst_cat_data.lifetime)-relativedelta(days=1)
                    if subsequent_cap:
                        diffdate = relativedelta(asset_data.enddate.astimezone(tzlocal.get_localzone()),parser.parse(assetdetails_obj.CP_Date['dates']).astimezone(tzlocal.get_localzone()).astimezone(tzlocal.get_localzone()))
                        diff=asset_data.enddate.astimezone(tzlocal.get_localzone())-parser.parse(assetdetails_obj.CP_Date['dates']).astimezone(tzlocal.get_localzone()).astimezone(tzlocal.get_localzone())
                        dep_rate_cal = (365 / (diff.days)) * 100
                        print(dep_rate_cal)
                        asst_dep_rate = dep_rate_cal
                        end_date=asset_data.enddate
                    if asst_cat_data.deptype=='WDV':
                        sal_val=FaConst()
                        asst_dep_rate=1-((sal_val.SALVAGE_VALUE/(assetdetails_obj.Asset_Value/assetdetails_obj.QTY)*float(assetdtlsobj_list.MarkedUpRatio))**(1/(asst_cat_data.lifetime/12)))
                        asst_dep_rate=asst_dep_rate*100
                        asst_dep_rate=round(asst_dep_rate,2)
                    if isinstance(subcat,list):
                        cat=fa_obj.fetchcategory(subcat,request)
                    if isinstance(subcat,DictObj):
                        cat=subcat.category_id
                    else:
                        cat=subcat.category_id.id
                    assetdtls_data = AssetDetails(assetdetails_id=asst_id,
                    qty =1, #assetdetails_obj.get_qty(),
                    barcode = asst_id[:-6],
                    date = now(),
                    assetgroup_id = assetgrp_id,
                    assetheader=asst_head_data,
                    product_id = assetdetails_obj.Product_id,
                    cat = cat,#apcat
                    subcat = subcat.id,#apsubcat
                    assetcat_id=assetdetails_obj.Asset_Cat_id,
                    assetdetails_value = (assetdetails_obj.Asset_Value/assetdetails_obj.QTY)*float(assetdtlsobj_list.MarkedUpRatio),
                    assetdetails_cost = (assetdetails_obj.Asset_Value/assetdetails_obj.QTY)*float(assetdtlsobj_list.MarkedUpRatio),
                    description = initial_id,
                    capdate =parser.parse(assetdetails_obj.CP_Date['dates']),
                    source = AssetSource.FAMAKER,
                    assetdetails_status =AssetStatus.PENDING,
                    requestfor = AssetRequestfor.CAPITALIZE,
                    assettfr_id = AssetDetailsProcess.DEFAULT,
                    assetsale_id = AssetDetailsProcess.DEFAULT,
                    not5k = AssetDetailsProcess.DEFAULT,
                    assetowner = AssetDetailsProcess.DEFAULT,
                    lease_startdate = initial_date,
                    lease_enddate = initial_date,
                    impairasset_id = AssetDetailsProcess.DEFAULT,
                    impairasset = AssetDetailsProcess.DEFAULT,
                    writeoff_id = AssetDetailsProcess.DEFAULT,
                    assetcatchange_id = AssetDetailsProcess.DEFAULT,
                    assetvalue_id = AssetDetailsProcess.DEFAULT,
                    assetcapdate_id = AssetDetailsProcess.DEFAULT,
                    assetsplit_id = AssetDetailsProcess.DEFAULT,
                    assetmerge_id = AssetDetailsProcess.DEFAULT,
                    assetcatchangedate = initial_date,#Need to change default date
                    reducedvalue = AssetDetailsProcess.DEFAULT,
                    branch_id = assetdetails_obj.Branch_id,
                    assetlocation_id = assetdetails_obj.Location_id,
                    assetdetails_bs = assetdetails_obj.BS_NO,
                    assetdetails_cc = assetdetails_obj.CC_NO,
                    deponhold = DEPONHOLD.NO,
                    deprate = asst_dep_rate,
                    enddate = end_date,
                    parent_id = AssetDetailsProcess.DEFAULT,
                    assetserialno = AssetDetailsProcess.DEFAULT,#From prpo
                    invoice_id = AssetDetailsProcess.DEFAULT, #need to from faclearing
                    faclringdetails_id = assetdetails_obj.FAClearnceDetails_id,#faclearing invoide id
                    inwheader_id = AssetDetailsProcess.DEFAULT,
                    inwdetail_id = AssetDetailsProcess.DEFAULT,
                    inwarddate = initial_date,#default date
                    mepno = mepno,
                    ponum = ponum,
                    crnum = assetdetails_obj.crnum,
                    debit_id = AssetDetailsProcess.DEFAULT,
                    imagepath = str(list(data['gen_file_name']for data in resp)),
                    vendorname = vendor_name,
                    created_by=emp_id,
                    status=AssetStatus.ACTIVE)
                    assetdtls_array.append(assetdtls_data)
                if assetdtlsobj_list.Doc_Type !=3:
                    totval = int(float(assetdetails_obj.Asset_Value)+(assetdetails_obj.inv_debit_tax/2))
                else:
                    totval = int(float(assetdetails_obj.Asset_Value)+float(assetdetails_obj.inv_debit_tax))
                clearing_head_obj = ClearingHeader.objects.filter(id=clearing_head)
                for record in clearing_head_obj:
                    record.capitalizedamount=float(record.capitalizedamount)+ float(assetdetails_obj.Asset_Value*assetdtlsobj_list.MarkedUpRatio)
                    record.balanceamount=float(record.balanceamount) - float(assetdetails_obj.Asset_Value*assetdtlsobj_list.MarkedUpRatio)
                    record.updated_by=emp_id
                    record.updated_date=now()
                    if record.balanceamount < 0:
                        clearing_head_data.islock=ClearingLock.UNLOCK
                        clearing_head_data.save()
                        error=Error()
                        error.set_code(ErrorMessage.INVALID_DATA)
                        error.set_description(ErrorMessage.INVALID_DATA)
                        return error
                    elif record.balanceamount == 0 :
                        record.status=ClearingHeaderStatus.CAPITALIZED
                    elif record.balanceamount>0:
                        record.status=ClearingHeaderStatus.PARTIALLY_CAPITALIZED

                    record.save()
            AssetDetails.objects.bulk_create(assetdtls_array)

            end_id = int(AssetDetails.objects.latest('pk').pk) + 1
            assetdtls_list = NWisefinList()

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            #return success_obj

            for i in range(start_id, end_id):
                assetdetails = AssetDetails.objects.get(pk=i)

            #     assetdetails_resp = AssetDetailsResponse()
            #     assetdetails_resp.set_id(assetdetails.id)
            #     assetdetails_resp.set_assetdetails_id(assetdetails.assetdetails_id)
            #     assetdetails_resp.set_qty(assetdetails.qty)
            #     assetdetails_resp.set_barcode(assetdetails.barcode)
            #     assetdetails_resp.set_date(assetdetails.date)
            #     assetdetails_resp.set_assetgroup_id(assetdetails.assetgroup_id)
            #     assetdetails_resp.set_product_id(assetdetails.product_id)
            #     assetdetails_resp.set_cat(assetdetails.cat)
            #     assetdetails_resp.set_subcat(assetdetails.subcat)
            #     assetdtls_list.append(assetdetails_resp)

                refid = ref_type = -1
                relrefid = assetdetails.id
                self.audit_function(assetdetails, refid, ref_type, relrefid,
                                        emp_id, FaModifyStatus.CREATE, reqstatus,request)

        except IntegrityError as error:
            traceback.print_exc()
            clr_id = clearing_head_data.id
            clearing_head_data = ClearingHeader.objects.get(id=clr_id)
            clearing_head_data.islock=ClearingLock.UNLOCK
            clearing_head_data.save()
            error_obj = Error()
            error_obj.set_code(ErrorMessage.ERROR_ON_BALANCE_AMOUNT)
            error_obj.set_description(ErrorDescription.ERROR_ON_BALANCE_AMOUNT)
            return error_obj

        except Exception as e:
            traceback.print_exc()
            clr_id = clearing_head_data.id
            clearing_head_data = ClearingHeader.objects.get(id=clr_id)
            clearing_head_data.islock=ClearingLock.UNLOCK
            clearing_head_data.save()
            logger.info('FAL_CAPITALIZE_EXCEPT:{}'.format(traceback.print_exc()))
            errr = str(e)
            err=Error()
            err.set_description(errr)
            err.set_code(ErrorMessage.ERROR_ON_BALANCE_AMOUNT)
            return err
        except:
            clr_id = clearing_head_data.id
            clearing_head_data = ClearingHeader.objects.get(id=clr_id)
            clearing_head_data.islock=ClearingLock.UNLOCK
            clearing_head_data.save()
            logger.info('FAL_CAPITALIZE_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj
        clr_id=clearing_head_data.id
        clearing_head_data=ClearingHeader.objects.get(id=clr_id)
        clearing_head_data.islock=ClearingLock.UNLOCK
        clearing_head_data.save()
        return success_obj

    def fetch_assetdetails_list(self,barcode,query, vys_page,request):
        scope=request.scope
        api_obj = FaApiService(scope)
        condition=Q(status=1)
        if barcode is not None :
            condition&=Q(barcode__icontains=barcode)

        assetdetails_data = AssetDetails.objects.filter(condition).order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(assetdetails_data)
        #print(list_length)
        assetdetails_list = NWisefinList()
        if list_length > 0:
            for assetdetails in assetdetails_data:
                assetdetails_resp = AssetDetailsResponse()
                assetdetails_resp.set_id(assetdetails.id)
                assetdetails_resp.set_assetdetails_id(assetdetails.assetdetails_id)
                assetdetails_resp.set_qty(assetdetails.qty)
                assetdetails_resp.set_barcode(assetdetails.barcode)
                assetdetails_resp.set_branch_id ( api_obj.fetch_branch ( assetdetails.branch_id , request=None ) )
                assetdetails_resp.set_date(assetdetails.date)
                assetdetails_resp.set_assetgroup_id(assetdetails.assetgroup_id)
                assetdetails_resp.set_product_id(assetdetails.product_id)
                assetdetails_resp.set_cat(assetdetails.cat)
                assetdetails_resp.set_subcat(assetdetails.subcat)
                assetdetails_list.append(assetdetails_resp)
            vpage = NWisefinPaginator(assetdetails_data, vys_page.get_index(), 10)
            assetdetails_list.set_pagination(vpage)
        return assetdetails_list
    def fetch_assetdetails_sum(self,request, vys_page):
        scope=request.scope
        fa_obj=FaApiService(scope)
        condition=Q(assetdetails_status__in=[AssetStatus.ACTIVE,AssetStatus.IN_ACTIVE,AssetStatus.PENDING,AssetStatus.ENTRY_FAILED,AssetStatus.REJECTED])
        if 'assetid' in request.GET:
            condition &= Q(assetdetails_id__icontains=request.GET.get('assetid'))
        if 'cat' in request.GET:
            condition &= Q(assetcat_id=request.GET.get('cat'))
        if 'branch' in request.GET:
            condition&=Q(branch_id=request.GET.get('branch'))
        if 'capdate' in request.GET:
            date= parser.parse(request.GET.get('capdate'))
            condition&=Q(capdate=date)
        if 'asset_value' in request.GET:
            condition&=Q(assetdetails_value=float(request.GET.get('asset_value')))
        if 'crno' in request.GET:
            condition&=Q(crnum__icontains=request.GET.get('crno'))
        assetdetails_data = AssetDetails.objects.filter(condition).order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(assetdetails_data)
        #print(list_length)
        assetdetails_list = NWisefinList()
        if list_length > 0:
            for assetdetails in assetdetails_data:
                fa_aud=FaAudit.objects.filter(ref_type=AssetRequestfor.CAPITALIZE,ref_id=assetdetails.id)

                assetdetails_resp = AssetDetailsResponse()
                assetdetails_resp.set_id(assetdetails.id)
                if len(fa_aud)>0:
                    fa_aud=fa_aud[0]
                    aud_data=json.loads(fa_aud.data.replace("'",'"').replace('None','"None"'))
                    print(aud_data)
                    if 'reason' in aud_data:
                        assetdetails_resp.reason = aud_data['reason']
                    else:
                        assetdetails_resp.reason='None'
                else:
                    assetdetails_resp.reason='None'
                assetdetails_resp.set_barcode(assetdetails.barcode)
                assetdetails_resp.set_crnum(assetdetails.crnum)
                assetdetails_resp.set_cat(assetdetails.cat)
                req_for_obj=AssetRequestfor()
                assetdetails_resp.set_requestfor(req_for_obj.get_val(assetdetails.requestfor))
                assetdetails_resp.set_assetdetails_id(assetdetails.assetdetails_id)
                assetdetails_resp.set_qty(assetdetails.qty)
                assetdetails_resp.set_barcode(assetdetails.barcode)
                assetdetails_resp.set_date(assetdetails.capdate)
                assetdetails_resp.set_assetgroup_id(assetdetails.assetgroup_id)
                assetdetails_resp.set_product_id(fa_obj.fetch_product(assetdetails.product_id,request.user.id,request))
                assetdetails_resp.set_cat(assetdetails.cat)
                assetdetails_resp.set_subcat(assetdetails.subcat)
                assetdetails_resp.set_branch_id(fa_obj.fetch_branch(assetdetails.branch_id,request))
                assetdetails_list.append(assetdetails_resp)
                as_obj=AssetStatus()
                assetdetails_resp.set_assetdetails_status(as_obj.get_val(assetdetails.assetdetails_status))
                assetdetails_resp.set_vendorname(assetdetails.vendorname)
                assetdetails_resp.set_assetdetails_value(assetdetails.assetdetails_value)
            vpage = NWisefinPaginator(assetdetails_data, vys_page.get_index(), 10)
            assetdetails_list.set_pagination(vpage)
        return assetdetails_list
    def fetch_asset_id(self,query, vys_page):
        condition=Q()
        if query != '' :
            condition&=Q(assetdetails_id__icontains=query)
        assetdetails_data = AssetDetails.objects.filter(condition).order_by('-id')[vys_page.get_offset():vys_page.get_limit()]
        list_length = len(assetdetails_data)
        #print(list_length)
        assetdetails_list = NWisefinList()
        if list_length > 0:
            for assetdetails in assetdetails_data:
                assetdetails_resp = AssetDetailsResponse()
                assetdetails_resp.set_id(assetdetails.id)
                assetdetails_resp.set_cat(assetdetails.assetcat.subcatname)
                assetdetails_resp.set_assetdetails_id(assetdetails.assetdetails_id)
                assetdetails_resp.set_barcode(assetdetails.barcode)
                assetdetails_resp.set_assetgroup_id(assetdetails.assetgroup_id)
                assetdetails_list.append(assetdetails_resp)
            vpage = NWisefinPaginator(assetdetails_data, vys_page.get_index(),30)
            assetdetails_list.set_pagination(vpage)
        return assetdetails_list

    def fetch_asset_checkersum(self,vys_page,query_data,page,request=None):
        scope=request.scope
        asset_ef_list = []
        assetdetails_data= None
        condition = Q(requestfor=AssetRequestfor.CAPITALIZE,source=AssetSource.FAMAKER)
        if ('capdate' in query_data.__dict__.keys()):
            if query_data.capdate != '' and query_data.capdate != None:
                condition &= Q(capdate=query_data.capdate)
        if ('crno' in query_data.__dict__.keys()):
            if query_data.crno != '' and query_data.crno != None:
                condition &= Q(crnum__icontains=query_data.crno)
        if ('branch' in query_data.__dict__.keys()):
            if query_data.branch != '' and query_data.branch != None:
                condition &= Q(branch_id=query_data.branch)
        if ('cat' in query_data.__dict__.keys()):
            if query_data.cat != '' and query_data.cat != None:
                condition &= Q(assetcat_id=query_data.cat)
        if query_data.assetgroup!=None and query_data.assetgroup!='0':
            grp_data=AssetGroup.objects.get(number=query_data.assetgroup)
            condition&=Q(assetgroup_id=grp_data.id)
            assetdetails_data=AssetDetails.objects.filter(condition).exclude(assetdetails_status__in=[AssetStatus.ENTRY_FAILED,AssetStatus.ACTIVE,AssetStatus.IN_ACTIVE,AssetStatus.REJECTED])[
                                    vys_page.get_offset():vys_page.get_query_limit()]
        elif query_data.assetgroup == '0':
            condition&=Q(assetgroup_id='0',assetdetails_id=query_data.assetdetails_id)
            assetdetails_data=AssetDetails.objects.filter(condition).exclude(assetdetails_status__in=[AssetStatus.ACTIVE,AssetStatus.IN_ACTIVE,AssetStatus.REJECTED])[
                                    vys_page.get_offset():vys_page.get_query_limit()]
        else:
            asst_grp_id = []
            assetdetails_data=[]
            asset_ef_list = []
            if query_data.Grp_by=='Y':

                condition&=Q(requestfor=AssetRequestfor.CAPITALIZE)
                asset_det_list=AssetDetails.objects.filter(condition).exclude(assetdetails_status__in=[AssetStatus.ACTIVE,AssetStatus.IN_ACTIVE,AssetStatus.REJECTED])
                group_list=[]
                zero_ids=[]
                for record in asset_det_list:
                    if (record.assetgroup_id not in group_list) or str(record.assetgroup_id)=='0':
                        group_list.append(record.assetgroup_id)
                        if str(record.assetgroup_id)=='0':
                            zero_ids.append(record.assetdetails_id)
                page_grp=group_list[vys_page.get_offset():vys_page.get_query_limit()]
                grp=[]
                ef_grp=[]
                assetdetails_data = []
                for record in asset_det_list:
                    entry_pending_check = 0
                    if record.assetdetails_status == AssetStatus.ENTRY_FAILED:
                        if record.assetgroup_id not in ef_grp :
                            entry_pending_check = AssetDetails.objects.filter(
                                assetgroup_id=record.assetgroup_id).exclude(
                                assetdetails_status=AssetStatus.ENTRY_FAILED)
                            ef_grp.append(record.assetgroup_id)
                            asset_ef_list.append(record)
                        continue
                    if record.assetgroup_id in page_grp:
                        if (record.assetgroup_id not in grp) and str(record.assetgroup_id)!='0':
                            entry_pending_check = AssetDetails.objects.filter(assetgroup_id=record.assetgroup_id).exclude(assetdetails_status=AssetStatus.ENTRY_FAILED)
                            grp.append(record.assetgroup_id)
                            assetdetails_data.append(record)
                        elif str(record.assetgroup_id)=='0' and record.assetgroup_id not in grp:
                            asst=AssetDetails.objects.filter(assetdetails_id__in=zero_ids)
                            assetdetails_data.extend(asst)
                            grp.append(record.assetgroup_id)

                    if entry_pending_check!=0:
                        if record.assetgroup_id not in grp:
                            assetdetails_data.append(entry_pending_check[0])

            elif query_data.Grp_by=='N':
                if condition!=None:
                    assetdetails_data = AssetDetails.objects.filter(condition).exclude(assetdetails_status__in=[AssetStatus.ACTIVE,AssetStatus.IN_ACTIVE,AssetStatus.ENTRY_FAILED,AssetStatus.REJECTED]).order_by('id')[
                                    vys_page.get_offset():vys_page.get_query_limit()]
        if query_data.Grp_by!='N' and query_data.Grp_by!=None:
            assetdetails_data.extend(asset_ef_list)
            assetdetails_data=assetdetails_data[vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(assetdetails_data)
        # print(list_length)
        assetdetails_list = NWisefinList()
        api_obj=FaApiService(scope)
        assgrp_serv=AssetGroupService(scope)
        if list_length > 0:
            for assetdetails in assetdetails_data:
                img_bsf = []
                assetdetails_resp = AssetDetailsResponse()
                assetdetails_resp.set_id(assetdetails.id)
                assetdetails_resp.set_assetdetails_id(assetdetails.assetdetails_id)
                if assetdetails.assetgroup_id!=0:
                    group=assgrp_serv.fetch_assetgroup(assetdetails.assetgroup_id)
                    group=group.no
                else:
                    group=0
                if isinstance(group,Error):
                    return HttpResponse(group.get(),content_type='application/json')
                assetdetails_resp.set_assetgroup_id(group)
                assetdetails_resp.set_product_id(api_obj.fetch_product(assetdetails.product_id,query_data.user_id,request))
                assetdetails_resp.set_cat(assetdetails.assetcat)
                fa_obj = FaApiService(scope)
                apcat = fa_obj.fetchcategory(assetdetails.cat)
                assetdetails_resp.set_apcat(apcat)
                assetdetails_resp.set_crnum(assetdetails.crnum)
                assetdetails_resp.set_capdate(assetdetails.capdate)
                assetdetails_resp.set_vendorname(assetdetails.vendorname)
                asst_dtls=AssetDetails.objects.filter(assetgroup_id=assetdetails.assetgroup_id,crnum=assetdetails.crnum,assetdetails_status=AssetStatus.PENDING)
                asst_val=0
                valu=0
                if query_data.Grp_by=='Y':
                    for asst in asst_dtls:
                        # qty=ClearingDetails.objects.filter(id=asst.faclringdetails_id)[0].qty
                        asst_val=(float(asst_val)+float(asst.assetdetails_value))#/float(qty)
                    valu=assetdetails.assetdetails_value
                    count = len(AssetDetails.objects.filter(assetgroup_id=assetdetails.assetgroup_id,
                                                            requestfor=AssetRequestfor.CAPITALIZE,source=AssetSource.FAMAKER).exclude(
                        assetdetails_status__in=[AssetStatus.ENTRY_FAILED,
                                                 AssetStatus.REJECTED]))
                    if assetdetails.assetgroup_id!=0:
                        assetdetails_resp.set_assetdetails_value(float(valu) * float(count))
                    else:
                        assetdetails_resp.set_assetdetails_value(float(valu))
                else:
                    asst_val=assetdetails.assetdetails_value
                    valu = assetdetails.assetdetails_value
                    assetdetails_resp.set_assetdetails_value(float(valu))
                # if query_data.Grp_by=='Y':
                #     count = len(AssetDetails.objects.filter(assetgroup_id=assetdetails.assetgroup_id,
                #                                         requestfor=AssetRequestfor.CAPITALIZE).exclude(
                #     assetdetails_status__in=[AssetDetailsRequestStatus.ENTRY_FAILED,
                #                              AssetDetailsRequestStatus.REJECTED]))
                #
                #     assetdetails_resp.set_assetdetails_value(float(valu)*float(count))
                # else:
                #     assetdetails_resp.set_assetdetails_value(float(valu))
                assetdetails_resp.set_branch_id(api_obj.fetch_branch(assetdetails.branch_id,request))
                stat_obj=AssetStatus()
                assetdetails_resp.set_assetdetails_status(stat_obj.get_val(assetdetails.assetdetails_status))
                if assetdetails.assetdetails_status==AssetStatus.ENTRY_FAILED:
                    count = len(AssetDetails.objects.filter(assetgroup_id=assetdetails.assetgroup_id,
                                                            requestfor=AssetRequestfor.CAPITALIZE,
                                                            assetdetails_status=AssetStatus.ENTRY_FAILED))
                else:
                    count = len(AssetDetails.objects.filter(assetgroup_id=assetdetails.assetgroup_id,requestfor=AssetRequestfor.CAPITALIZE).exclude(assetdetails_status__in=[AssetStatus.ENTRY_FAILED,AssetStatus.REJECTED]))
                if str(assetdetails.assetgroup_id)=='0':
                    count=1
                assetdetails_resp.set_assetcount(count)
                # assetdetails_resp.set_assetdetails_status(assetdetails.status)
                assetdetails_resp.set_subcat(assetdetails.subcat)
                not_in=['0','[]','',None]
                if assetdetails.imagepath not in not_in :
                    image_data=json.loads(assetdetails.imagepath.replace("'",'"'))
                    for images in image_data:
                        s3 = boto3.resource('s3')
                        s3_obj = s3.Object(bucket_name=settings.BUCKET_NAME_FOR_ASSETS, key=images)
                        body = s3_obj.get()['Body']
                        img_bsf.append(base64.b64encode(body.read()))
                assetdetails_resp.set_imagepath(img_bsf)
                assetdetails_list.append(assetdetails_resp)
        vpage = NWisefinPaginator(assetdetails_data, vys_page.get_index(), 10)
        assetdetails_list.set_pagination(vpage)
        return assetdetails_list


    def audit_function(self, audit_data, refid,reftype, relrefid, emp_id, action,reqstatus,request):
        if action == FaModifyStatus.DELETE:
            data = None
        else:
            data = audit_data.__dict__
            del data['_state']
        scope=request.scope
        audit_service = FaAuditService(scope)
        audit_obj = FaAuditResponse()
        audit_obj.set_refid(refid)
        audit_obj.set_reqstatus(reqstatus)
        audit_obj.set_reftype(reftype)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(FaRefType.ASSETDETAILS)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)

    #assetdetails  writeoff
    def assetdetails_writeoff(self, assetdetails_id, emp_id,request):
        a_reqfor = AssetRequestfor.WRITEOFF             #5
        a_reqstatus = AssetRequestStatus.SUBMITTED      #4
        reqstatus = FaRequestStatusUtil.MODIFICATION
        try:
            assetdetailss = AssetDetails.objects.filter(id=assetdetails_id).update(
                                                        requestfor=a_reqfor,
                                                        requeststatus=a_reqstatus,
                                                        updated_by=emp_id,
                                                        updated_date=now())
            assetdetails = AssetDetails.objects.get(id=assetdetails_id)
            refid = ref_type = -1
            relrefid = assetdetails.id
            self.audit_function(assetdetails, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.UPDATE, reqstatus,request)

            success_obj = SuccessStatus.SUCCESS
            return success_obj
        except IntegrityError as error:
            logger.info('FAL_WRITEOFF_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = ErrorMessage.INVALID_DATA
            return error_obj
        except AssetDetails.DoesNotExist:
            logger.info('FAL_WRITEOFF_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = str(ErrorMessage.INVALID_ASSETID_ID)+' : '+str(assetdetails_id)
            return error_obj
        except:
            logger.info('FAL_WRITEOFF_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = ErrorMessage.UNEXPECTED_ERROR
            return error_obj

    # assetdetails  split
    def assetdetails_split(self, assetdetails_id, emp_id,request):
        a_reqfor = AssetRequestfor.SPLIT  # 10
        a_reqstatus = AssetRequestStatus.PENDING  # 4
        reqstatus = FaRequestStatusUtil.MODIFICATION
        assetdetails_status = AssetStatus.ACTIVE
        try:
            assetdetailss = AssetDetails.objects.filter(assetdetails_id=assetdetails_id).update(
                requestfor=a_reqfor,
                requeststatus=a_reqstatus,
                assetdetails_status=assetdetails_status,
                updated_by=emp_id,
                updated_date=now())
            assetdetails = AssetDetails.objects.get(assetdetails_id=assetdetails_id)
            refid = ref_type = -1
            relrefid = assetdetails.id
            self.audit_function(assetdetails, refid, ref_type, relrefid,
                                emp_id, FaModifyStatus.UPDATE, reqstatus,request)
            success_obj = SuccessStatus.SUCCESS
            return success_obj

        except IntegrityError as error:
            logger.info('FAL_SPLIT_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = ErrorMessage.INVALID_DATA
            return error_obj

        except AssetDetails.DoesNotExist:
            logger.info('FAL_SPLIT_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = str(ErrorMessage.INVALID_ASSETID_ID) + ' : ' + str(assetdetails_id)
            return error_obj
        except:
            logger.info('FAL_SPLIT_EXCEPT:{}'.format(traceback.print_exc()))
            traceback.print_exc()
            error_obj = ErrorMessage.UNEXPECTED_ERROR
            return error_obj

    # assetdetails  merge
    def assetdetails_merge(self, data_arr, emp_id,request):
        a_reqfor = AssetRequestfor.MERGE  # 11
        a_reqstatus = AssetRequestStatus.SUBMITTED  # 4
        reqstatus = FaRequestStatusUtil.MODIFICATION
        assetdetails_status = AssetStatus.IN_ACTIVE
        try:
            for assetdetails_id in data_arr:
                assetdetailss = AssetDetails.objects.filter(id=assetdetails_id).update(
                    requestfor=a_reqfor,
                    requeststatus=a_reqstatus,
                    assetdetails_status=assetdetails_status,
                    updated_by=emp_id,
                    updated_date=now())
                assetdetails = AssetDetails.objects.get(id=assetdetails_id)
                refid = ref_type = -1
                relrefid = assetdetails.id
                self.audit_function(assetdetails, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.UPDATE, reqstatus,request)
            success_obj = SuccessStatus.SUCCESS
            return success_obj

        except IntegrityError as error:
            logger.info('FAL_MERGE_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = ErrorMessage.INVALID_DATA
            return error_obj

        except AssetDetails.DoesNotExist:
            logger.info('FAL_MERGE_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = ErrorMessage.INVALID_ASSETID_ID
            return error_obj

        except:
            logger.info('FAL_MERGE_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = ErrorMessage.UNEXPECTED_ERROR
            return error_obj

    def fetch_asset_id_grp(self, vys_page,asset_grp_id):

        asset_details_data=AssetDetails.objects.filter(assetgroup_id=asset_grp_id,assetdetails_status=AssetStatus.ACTIVE).exclude(assetdetails_status=AssetStatus.PENDING)[vys_page.get_offset():vys_page.get_query_limit()]
        asset_details_list=NWisefinList()
        for asset_details in asset_details_data:
            asset_id_obj=AssetDetailsResponse()
            asset_id_obj.set_id(asset_details.id)
            asset_id_obj.set_assetdetails_id(asset_details.assetdetails_id)
            asset_id_obj.set_assetgroup_id(asset_details.assetgroup_id)
            asset_details_list.append(json.loads(asset_id_obj.get()))
        vpage = NWisefinPaginator(asset_details_data, vys_page.get_index(), 10)
        asset_details_list.set_pagination(vpage)
        return asset_details_list
    # FA QUERY
    #
    def fa_queryget(self, query_data, vys_page, user_id, request):
        scope=request.scope
        condition = Q()
        if 'capstart_date' in query_data.keys():
            condition &= Q(capdate__range=(query_data['capstart_date'], query_data['capend_date']))
        if 'enddatefrom' in query_data.keys():
            condition &= Q(
                enddate__range=(query_data['enddatefrom'], query_data['enddateto']))

        if 'assetfrom_value' in query_data.keys():
            condition &= Q(
                assetdetails_value__range=(query_data['assetfrom_value'], query_data['assetto_value']))
        if 'lease_startdate' in query_data.keys():
            condition &= Q(lease_startdate=query_data['lease_startdate'],
                           lease_enddate=query_data['lease_enddate'])
        if 'branch' in query_data.keys():
            condition &= Q(branch_id=query_data['branch'])
        if 'vendorname' in query_data.keys():
            condition &= Q(vendorname=query_data['vendorname'])
        if 'asstsrc' in query_data.keys() and query_data['asstsrc']!='':
            condition &= Q(source__in=query_data['asstsrc'])
        if 'cat' in query_data.keys():
            condition &= Q(cat=query_data['cat'])
        if 'assetdetails_id' in query_data.keys():
            condition &= Q(assetdetails_id__icontains=query_data['assetdetails_id'])
        if 'ponum' in query_data.keys():
            condition &= Q(ponum=query_data['ponum'])
        if 'mepno' in query_data.keys():
            condition &= Q(mepno=query_data['mepno'])
        if 'crnum' in query_data.keys():
            condition &= Q(crnum=query_data['crnum'])
        if 'branchfrom' in query_data.keys():
            btrn = list(AssetTFR.objects.filter(assettfr_from=query_data['branchfrom'],
                                                assettfr_to=query_data['branchto']).values_list('assetdetails_id', flat=True))
            condition &= Q(id__in=btrn)
        if 'invoiceno' in query_data.keys():
            invoiceno = list(ClearingDetails.objects.filter(invoiceno=query_data['invoiceno']).values_list('id', flat=True))
            condition &= Q(faclringdetails_id__in=invoiceno)
        if 'amount' in query_data.keys():
            amount = list(ClearingDetails.objects.filter(amount=query_data['amount']).values_list('id', flat=True))
            condition &= Q(faclringdetails_id__in=amount)
        if 'invoicedate' in query_data.keys():
            invoicedate = list(ClearingDetails.objects.filter(invoicedate=query_data['invoicedate']).values_list('id', flat=True))
            condition &= Q(faclringdetails_id__in=invoicedate)
        if 'deponhold' in query_data.keys():
            condition &= Q(deponhold=query_data['deponhold'])

        if condition != None:
            query_count = AssetDetails.objects.filter(condition).count()
            assetdetails_data = AssetDetails.objects.filter(condition).order_by('-id')[
                                vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(assetdetails_data)
        assetdetails_list = NWisefinList()
        invoice = ClearingDetailsService(scope)
        assetgrp = AssetQuery()
        api_obj = FaApiService(scope)
        if list_length > 0:
            for assetdetails in assetdetails_data:
                assetdetails_resp = AssetDetailsResponse()
                asst_rfor=AssetRequestfor()
                assetdetails_resp.requestfor=asst_rfor.get_val(assetdetails.requestfor)
                asst_src=AssetSource()
                assetdetails_resp.set_source(asst_src.get_val(assetdetails.source))
                assetdetails_resp.set_assetdetails_id(assetdetails.assetdetails_id)
                print(assetdetails.assetcat.itcatname)
                assetdetails_resp.set_barcode(assetdetails.barcode)
                try:
                    d=AssetBarcodeMap.objects.filter(asset_barcode=assetdetails.barcode)[0]
                    emp_res=ApiService(request.scope)
                    emp_data=emp_res.get_empsingle_id(request,d.emp_id)
                    assetdetails_resp.emp=str(emp_data.get('code')+'-'+emp_data.get('name'))
                except:
                    traceback.print_exc()
                    assetdetails_resp.emp=''
                assetdetails_resp.set_assetgroup_id(assetgrp.get_AssetGroup(assetdetails.assetgroup_id))
                assetdetails_resp.set_product_id(api_obj.fetch_product(assetdetails.product_id, user_id, request))
                assetdetails_resp.set_cat(api_obj.fetchcategory(assetdetails.cat))
                assetdetails_resp.set_capdate(assetdetails.capdate)
                assetdetails_resp.set_vendorname(assetdetails.vendorname)
                assetdetails_resp.set_assetdetails_value(assetdetails.assetdetails_value)
                assetdetails_resp.set_branch_id(api_obj.fetch_branch(assetdetails.branch_id))
                asst_status=AssetStatus()
                assetdetails_resp.set_assetdetails_status(asst_status.get_val(assetdetails.assetdetails_status))
                assetdetails_resp.set_ponum(assetdetails.ponum)
                assetdetails_resp.set_crnum(assetdetails.crnum)
                assetdetails_resp.set_enddate(assetdetails.enddate)
                assetdetails_resp.set_subcat(api_obj.fetchsubcategory(assetdetails.subcat))
                assetdetails_resp.set_invoice_id(invoice.fetch_invoicedetailsforfaqery(assetdetails.faclringdetails_id))
                assetdetails_resp.set_valuetot(assetdetails.assetheader.valuetot)
                assetdetails_resp.set_costtot(assetdetails.assetheader.costtot)
                assetdetails_resp.set_itcatname(assetdetails.assetcat.itcatname)
                assetdetails_list.append(assetdetails_resp)
            assetdetails_list.set_listcount(query_count)
            vpage = NWisefinPaginator(assetdetails_data, vys_page.get_index(), 10)
            assetdetails_list.set_pagination(vpage)

        return assetdetails_list
    def fa_queryget_download(self, query_data, vys_page, user_id, request):
        scope=request.scope
        condition = Q()
        if 'capstart_date' in query_data.keys():
            condition &= Q(capdate__range=(query_data['capstart_date'], query_data['capend_date']))
        if 'enddatefrom' in query_data.keys():
            condition &= Q(
                enddate__range=(query_data['enddatefrom'], query_data['enddateto']))

        if 'assetfrom_value' in query_data.keys():
            condition &= Q(
                assetdetails_value__range=(query_data['assetfrom_value'], query_data['assetto_value']))
        if 'lease_startdate' in query_data.keys():
            condition &= Q(lease_startdate=query_data['lease_startdate'],
                           lease_enddate=query_data['lease_enddate'])
        if 'branch' in query_data.keys():
            condition &= Q(branch_id=query_data['branch'])
        if 'vendorname' in query_data.keys():
            condition &= Q(vendorname=query_data['vendorname'])
        if 'asstsrc' in query_data.keys() and query_data['asstsrc']!='':
            condition &= Q(source__in=query_data['asstsrc'])
        if 'cat' in query_data.keys():
            condition &= Q(cat=query_data['cat'])
        if 'assetdetails_id' in query_data.keys():
            condition &= Q(assetdetails_id__icontains=query_data['assetdetails_id'])
        if 'ponum' in query_data.keys():
            condition &= Q(ponum=query_data['ponum'])
        if 'mepno' in query_data.keys():
            condition &= Q(mepno=query_data['mepno'])
        if 'crnum' in query_data.keys():
            condition &= Q(crnum=query_data['crnum'])
        if 'branchfrom' in query_data.keys():
            btrn = list(AssetTFR.objects.filter(assettfr_from=query_data['branchfrom'],
                                                assettfr_to=query_data['branchto']).values_list('assetdetails_id', flat=True))
            condition &= Q(id__in=btrn)
        if 'invoiceno' in query_data.keys():
            invoiceno = list(ClearingDetails.objects.filter(invoiceno=query_data['invoiceno']).values_list('id', flat=True))
            condition &= Q(faclringdetails_id__in=invoiceno)
        if 'amount' in query_data.keys():
            amount = list(ClearingDetails.objects.filter(amount=query_data['amount']).values_list('id', flat=True))
            condition &= Q(faclringdetails_id__in=amount)
        if 'invoicedate' in query_data.keys():
            invoicedate = list(ClearingDetails.objects.filter(invoicedate=query_data['invoicedate']).values_list('id', flat=True))
            condition &= Q(faclringdetails_id__in=invoicedate)
        if 'deponhold' in query_data.keys():
            condition &= Q(deponhold=query_data['deponhold'])

        if condition != None:
            query_count = AssetDetails.objects.filter(condition).count()
        assetdetails_data = AssetDetails.objects.filter(condition).order_by('-id')
        list_length = len(assetdetails_data)
        assetdetails_list = NWisefinList()
        invoice = ClearingDetailsService(scope)
        assetgrp = AssetQuery()
        api_obj = FaApiService(scope)
        if list_length > 0:
            for assetdetails in assetdetails_data:
                assetdetails_resp = AssetDetailsResponse()
                asst_rfor=AssetRequestfor()
                assetdetails_resp.requestfor=asst_rfor.get_val(assetdetails.requestfor)
                asst_src=AssetSource()
                assetdetails_resp.set_source(asst_src.get_val(assetdetails.source))
                assetdetails_resp.set_assetdetails_id(assetdetails.assetdetails_id)
                assetdetails_resp.set_barcode(assetdetails.barcode)
                assetdetails_resp.set_assetgroup_id(assetgrp.get_AssetGroup(assetdetails.assetgroup_id))
                prod=api_obj.fetch_product(assetdetails.product_id, user_id, request)
                if isinstance(prod,dict):
                    prod=prod['name']
                else:
                    prod=prod.name
                assetdetails_resp.set_product_id(prod)
                cat_data=api_obj.fetchcategory(assetdetails.cat)
                if isinstance(cat_data,dict):
                    cat_data=cat_data['name']
                else:
                    cat_data=cat_data.name
                assetdetails_resp.set_cat(cat_data)
                assetdetails_resp.set_capdate(assetdetails.capdate)
                assetdetails_resp.set_vendorname(assetdetails.vendorname)
                assetdetails_resp.set_assetdetails_value(assetdetails.assetdetails_value)
                brn_data=api_obj.fetch_branch(assetdetails.branch_id)
                if isinstance(brn_data,dict):
                    brn_data=brn_data['name']
                else:
                    brn_data=brn_data.name
                assetdetails_resp.set_branch_id(brn_data)
                asst_status=AssetStatus()
                assetdetails_resp.set_assetdetails_status(asst_status.get_val(assetdetails.assetdetails_status))
                assetdetails_resp.set_ponum(assetdetails.ponum)
                assetdetails_resp.set_crnum(assetdetails.crnum)
                assetdetails_resp.set_enddate(assetdetails.enddate)
                sub_cat_data_temp=api_obj.fetchsubcategory(assetdetails.subcat)
                if isinstance(sub_cat_data_temp,dict):
                    sub_cat_data=sub_cat_data_temp['name']
                else:
                    sub_cat_data=sub_cat_data_temp.name
                assetdetails_resp.set_subcat(sub_cat_data)
                invoice_data_temp=invoice.fetch_invoicedetailsforfaqery(assetdetails.faclringdetails_id)
                if isinstance(invoice_data_temp,dict):
                    invoice_data=invoice_data_temp['invoiceno']
                else:
                    invoice_data=invoice_data_temp.invoiceno
                assetdetails_resp.set_invoice_id(invoice_data)
                assetdetails_resp.expense_gl=sub_cat_data_temp.glno
                assetdetails_resp.invoice_date=invoice_data_temp.invoicedate
                assetdetails_resp.set_valuetot(assetdetails.assetheader.valuetot)
                assetdetails_resp.set_costtot(assetdetails.assetheader.costtot)
                assetdetails_list.append(assetdetails_resp)
            assetdetails_list.set_listcount(query_count)
            vpage = NWisefinPaginator(assetdetails_data, vys_page.get_index(), 10)
            assetdetails_list.set_pagination(vpage)
        return assetdetails_list
    def get_countfa(self,type):
        assetdetails_resp = Totalcount()
        condition = Q(status=1)
        if 1 in type:
            query_count = AssetCapDate.objects.filter(condition).count()
            assetdetails_resp.cap_count(query_count)
        if 2 in type:
            query_count = WriteOff.objects.filter(condition).count()
            assetdetails_resp.writeoff_count(query_count)
        if 3 in type:
            query_count = ImpairAsset.objects.filter(condition).count()
            assetdetails_resp.impair_count(query_count)
        if 4 in type:
            query_count = AssetValue.objects.filter(condition).count()
            assetdetails_resp.assetvalue_count(query_count)
        if 5 in type:
            query_count = AssetMerge.objects.filter(condition).count()
            assetdetails_resp.merge_count(query_count)
        if 6 in type:
            query_count = AssetSplitHeader.objects.filter(condition).count()
            assetdetails_resp.split_count(query_count)
        if 7 in type:
            query_count = AssetTFR.objects.filter(condition).count()
            assetdetails_resp.transfer_count(query_count)
        if 8 in type:
            query_count = AssetCat.objects.filter(condition).count()
            assetdetails_resp.cat_count(query_count)
        if 9 in type:
            query_count = AssetCapDate.objects.filter(condition).count()
            assetdetails_resp.sale_count(query_count)
        return assetdetails_resp


    def checker_sum_approve(self,user_id,assdet,request):
        fund=None
        scope=request.scope
        emp_id=request.employee_id
        asstentry = AssetentryService(scope)
        fa_obj = FaApiService(scope)

        data_dict={}
        for i in assdet['assetdetails_id']:
            resp_list = []
            types=[AssetEntryType.CREDIT_VAL,AssetEntryType.DEBIT_VAL]
            for type in types:
                if type==AssetEntryType.CREDIT_VAL:
                    resp=fa_obj.asset_approve_cr(i,"FA-CAPITALIZE",request)
                else:
                    resp=fa_obj.asset_approve(i,"FA-CAPITALIZE",request)
                resp_list.append(resp)
            data_dict[i]=resp_list.copy()
        entry = asstentry.create_assetentry(user_id,assdet,request,data_dict)
        if isinstance(entry,Error):
            return entry
        for data in assdet['assetdetails_id']:
            ref_type=AssetRequestfor.CAPITALIZE
            ref_id= data
            put_checker_reason_to_audit(ref_type,ref_id,assdet,request)
        # print("Entry",entry)


        # fund = asstentry.create_fundservice(sas,request)
        # if isinstance(fund,Error):
        #     return fund
        # # if fund['CbsStatus'][0]['Status']=='Success':
        logger.error("FA_ASSET_APPROVE: "+str(resp_list))
        resp=NWisefinSuccess()
        resp.set_status(SuccessStatus.SUCCESS)
        resp.set_message(SuccessMessage.APPROVED_MESSAGE)
        fund=resp
        print("fund", fund)
        return fund
    def checker_sum_reject(self, query_obj, request):
        try:
            assetdet_id=query_obj.assetdetails_id
            subsequent=False
            if int(assetdet_id[-2:])>1:
                subsequent=True

            asset_det=AssetDetails.objects.get(id=assetdet_id)
            clrng_det_id=asset_det.faclringdetails_id
            clring_dtls_data=ClearingDetails.objects.get(id=clrng_det_id)
            clring_dtls_datas=ClearingDetails.objects.filter(clearingheader_id=clring_dtls_data.clearingheader_id)
            clring_hdr_data=ClearingHeader.objects.get(id=clring_dtls_data.clearingheader_id)
            if not subsequent:
                for clrng_det in clring_dtls_datas:
                    asset_check=AssetDetails.objects.filter(faclringdetails_id=clrng_det.id,requeststatus=AssetStatus.ACTIVE)
                    if(len(asset_check))>0:
                        err=Error()
                        err.set_code(ErrorMessage.CANT_REJECT_APPROVED)
                        err.set_description(ErrorDescription.CANT_REJECT_APPROVED)
                        return err
                    asset_data=AssetDetails.objects.filter(faclringdetails_id=clrng_det.id)

                    for record in asset_data:
                        ref_type = AssetRequestfor.CAPITALIZE
                        ref_id = record.id
                        put_checker_reason_to_audit(ref_type, ref_id, record.__dict__, request)
                        assetheader_data = AssetHeader.objects.get(id=record.assetheader_id)

                        assetheader_data.costtot=assetheader_data.costtot-record.assetdetails_value
                        assetheader_data.astvalbeforedeptot=assetheader_data.astvalbeforedeptot-record.assetdetails_value
                        assetheader_data.revisedcbtot=assetheader_data.revisedcbtot-record.assetdetails_value
                        assetheader_data.valuetot =assetheader_data.valuetot - record.assetdetails_value
                        assetheader_data.astvalbeforedeptot=assetheader_data.valuetot - record.assetdetails_value
                        assetheader_data.save()
                        fa_aud = FaAudit()
                        fa_aud.ref_type = AssetRequestfor.CAPITALIZE
                        fa_aud.ref_id = record.id
                        fa_aud.data = query_obj.__dict__
                        fa_aud.req_status = AssetStatus.ACTIVE
                        fa_aud.user_id = request.user.id
                        fa_aud.save()
                        record.assetdetails_status=AssetStatus.REJECTED
                        record.save()
                    clrng_det.balanceqty=clrng_det.qty
                    clrng_det.status=AssetStatus.ACTIVE
                    clrng_det.save()
                clring_hdr_data.balanceamount+=clring_hdr_data.capitalizedamount
                clring_hdr_data.capitalizedamount=0
                clring_hdr_data.status=AssetStatus.ACTIVE
                clring_hdr_data.save()
            else:
                asset_det.assetdetails_status=AssetStatus.REJECTED
                assetheader_data = AssetHeader.objects.get(id=asset_det.assetheader_id)
                assetheader_data.costtot = assetheader_data.costtot - asset_det.assetdetails_value
                assetheader_data.astvalbeforedeptot = assetheader_data.astvalbeforedeptot - asset_det.assetdetails_value
                assetheader_data.revisedcbtot = assetheader_data.revisedcbtot - asset_det.assetdetails_value
                assetheader_data.valuetot = assetheader_data.valuetot - asset_det.assetdetails_value
                assetheader_data.save()
                fa_aud = FaAudit()
                fa_aud.ref_type = AssetRequestfor.CAPITALIZE
                fa_aud.ref_id = asset_det.id
                fa_aud.data = query_obj.__dict__
                fa_aud.req_status = AssetStatus.ACTIVE
                fa_aud.user_id = request.user.id
                fa_aud.save()
                asset_det.assetdetails_status = AssetStatus.REJECTED
                asset_det.save()
                clring_dtls_data.balanceqty = clring_dtls_data.qty
                clring_dtls_data.status = AssetStatus.ACTIVE
                clring_dtls_data.save()
                clring_hdr_data.balanceamount +=  asset_det.assetdetails_value
                clring_hdr_data.capitalizedamount = clring_hdr_data.capitalizedamount-asset_det.assetdetails_value
                clring_hdr_data.status = AssetStatus.ACTIVE
                clring_hdr_data.save()
        except:
            logger.info('FAL_ASSETCHECK_REJECT_EXCEPT:{}'.format(traceback.print_exc()))
            traceback.print_exc()
            err_obj=Error()
            err_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            err_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return err_obj
        check_reponse=NWisefinSuccess()
        check_reponse.set_status(SuccessStatus.SUCCESS)
        check_reponse.set_message(SuccessMessage.REJECTED_MESSAGE)
        return check_reponse

    def clubmakerupdate ( self , data , empid , reqfor , requeststatus ) :
        try :
            for i in data :
                if requeststatus!=1:
                    assetheader = AssetHeader.objects.get ( barcode=i['barcode'] )

                    update = AssetDetails.objects.filter ( id=i['id'] ).update ( requestfor=reqfor ,
                                                                                requeststatus=requeststatus ,
                                                                                updated_by=empid ,
                                                                                parent_id=assetheader.id ,
                                                                                updated_date=timezone.now ( )
                                                                                )
                else:
                    update = AssetDetails.objects.filter ( id=i [ 'id' ] ).update ( requestfor=reqfor ,
                                                                                    requeststatus=requeststatus ,
                                                                                    updated_by=empid ,

                                                                                    updated_date=timezone.now ( )
                                                                                    )
            success_obj = NWisefinSuccess()
            success_obj.set_status ( SuccessStatus.SUCCESS )
            return success_obj
        except Exception as e :
            logger.info('FAL_CLUB_MAKE_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error ( )
            error_obj.set_code ( ' Update FAILED' )
            error_obj.set_description ( e )
            return error_obj

    def get_clubapproverqueue ( self , emp , requeststatus , vys_page ,query_data, request ) :
        condition = Q ( status=1 , requeststatus=requeststatus )
        if 'capstart_date' in query_data.keys ( ) :
            condition &= Q ( capdate=query_data [ 'capstart_date' ] )
        if 'barcode' in query_data.keys ( ) :
            condition &= Q ( barcode=query_data [ 'barcode' ] )
        if 'assetvalue' in query_data.keys ( ) :
            condition &= Q ( assetdetails_value=query_data [ 'assetvalue' ] )
        if 'cat' in query_data.keys ( ) :
            condition &= Q ( cat=query_data [ 'cat' ] )
        if 'branch' in query_data.keys ( ) :
            condition &= Q ( branch_id=query_data [ 'branch' ] )
        assetdetails_data = AssetDetails.objects.filter ( condition ) [
                            vys_page.get_offset ( ) :vys_page.get_query_limit ( ) ]
        scope=request.scope
        api_obj = FaApiService (scope )
        list_length = len ( assetdetails_data )
        assetdetails_list = NWisefinList ( )
        location = AssetLocationService (scope )
        if list_length > 0 :
            for assetdetails in assetdetails_data :
                assetdetails_resp = AssetDetailsResponse ( )
                assetdetails_resp.set_assetdetails_id ( assetdetails.assetdetails_id )
                assetdetails_resp.set_id ( assetdetails.id )
                assetdetails_resp.set_barcode ( assetdetails.barcode )
                assetdetails_resp.set_assetgroup_id ( assetdetails.assetgroup_id )
                assetdetails_resp.set_product_id ( api_obj.fetch_product ( assetdetails.product_id , emp , request ) )
                assetdetails_resp.set_cat ( api_obj.fetchcategory ( assetdetails.cat ) )
                assetdetails_resp.set_capdate ( assetdetails.capdate )
                assetdetails_resp.set_parent_id ( assetdetails.parent_id )
                assetdetails_resp.set_assetdetails_value ( assetdetails.assetdetails_value )
                assetdetails_resp.set_branch_id ( api_obj.fetch_branch ( assetdetails.branch_id ) )
                assetdetails_resp.set_assetdetails_status ( assetdetails.status )
                assetdetails_resp.set_requestfor ( assetdetails.requestfor )
                assetdetails_resp.set_requeststatus ( assetdetails.requeststatus )
                assetdetails_resp.set_assetlocation_id ( location.fetch_assetlocation ( assetdetails.assetlocation_id ) )
                assetdetails_list.append ( assetdetails_resp )
            # assetdetails_list.set_listcount(query_count)
            vpage = NWisefinPaginator ( assetdetails_data , vys_page.get_index ( ) , 10 )
            assetdetails_list.set_pagination ( vpage )
        return assetdetails_list

    def parentdetail_get ( self , parent_id , vys_page , emp , request ) :
        scope=request.scope
        condition = Q ( status=1 , parent_id=parent_id )
        assetdetails_data = AssetDetails.objects.filter ( condition ) [
                            vys_page.get_offset ( ) :vys_page.get_query_limit ( ) ]

        api_obj = FaApiService ( scope=scope)
        list_length = len ( assetdetails_data )
        assetdetails_list = NWisefinList ( )
        if list_length > 0 :
            for assetdetails in assetdetails_data :
                assetdetails_resp = AssetDetailsResponse ( )
                assetdetails_resp.set_assetdetails_id ( assetdetails.assetdetails_id )
                assetdetails_resp.set_id ( assetdetails.id )
                assetdetails_resp.set_barcode ( assetdetails.barcode )
                assetdetails_resp.set_assetgroup_id ( assetdetails.assetgroup_id )
                assetdetails_resp.set_product_id ( api_obj.fetch_product ( assetdetails.product_id , emp , request ) )
                assetdetails_resp.set_cat ( api_obj.fetchcategory ( assetdetails.cat ) )
                assetdetails_resp.set_capdate ( assetdetails.capdate )
                assetdetails_resp.set_parent_id ( assetdetails.parent_id )
                assetdetails_resp.set_assetdetails_value ( assetdetails.assetdetails_value )
                assetdetails_resp.set_branch_id ( api_obj.fetch_branch ( assetdetails.branch_id ) )
                fa_stat=AssetStatus()
                assetdetails_resp.set_assetdetails_status ( fa_stat.get_val(assetdetails.status) )
                location = AssetLocationService(scope)
                assetdetails_resp.set_assetlocation_id (
                    location.fetch_assetlocation ( assetdetails.assetlocation_id ) )

                # assetdetails_resp.set_crnum(assetdetails.crnum)
                # assetdetails_resp.set_deponhold(assetdetails.deponhold)
                # assetdetails_resp.set_enddate(assetdetails.enddate)
                # assetdetails_resp.set_subcat(api_obj.fetchsubcategory(assetdetails.subcat))
                # assetdetails_resp.set_invoice_id(invoice.fetch_invoicedetailsforfaqery(assetdetails.invoice_id))
                assetdetails_list.append ( assetdetails_resp )
            # assetdetails_list.set_listcount(query_count)
            vpage = NWisefinPaginator ( assetdetails_data , vys_page.get_index ( ) , 10 )
            assetdetails_list.set_pagination ( vpage )

        return assetdetails_list

    def getparentasset ( self , emp , requestfor , vys_page ,query_data, request ) :
        condition=Q(status=AssetStatus.ACTIVE)
        if requestfor!='':
            excondition = Q ( barcode=query_data['id'] ,requeststatus=RequestStatus.PENDING,
                              assetdetails_status=AssetStatus.ACTIVE,requestfor=AssetRequestfor.CLUB)
        else:
            condition &= Q(requeststatus__in=[0, 1], assetdetails_status=AssetStatus.ACTIVE)
        if 'capstart_date' in query_data.keys ( ) :
            condition &= Q ( capdate=query_data [ 'capstart_date' ] )
        if 'barcode' in query_data.keys ( ) :
            condition &= Q ( barcode=query_data [ 'barcode' ] )
        if 'assetvalue' in query_data.keys ( ) :
            condition &= Q ( assetdetails_value=query_data [ 'assetvalue' ] )
        if 'cat' in query_data.keys ( ) :
            condition &= Q ( cat=query_data [ 'cat' ] )
        if 'branch' in query_data.keys ( ) :
            condition &= Q ( branch_id=query_data [ 'branch' ] )
        if requestfor!='':

            assetdetails_data = AssetDetails.objects.filter ( condition).exclude(excondition) [
                            vys_page.get_offset ( ) :vys_page.get_query_limit ( ) ]
        else:
            assetdetails_data = AssetDetails.objects.filter(condition)[
                                vys_page.get_offset():vys_page.get_query_limit()]
        scope=request.scope
        api_obj = FaApiService ( scope)
        list_length = len ( assetdetails_data )
        location = AssetLocationService ( scope)
        assetdetails_list = NWisefinList ( )
        if list_length > 0 :
            for assetdetails in assetdetails_data :
                assetdetails_resp = AssetDetailsResponse ( )
                assetdetails_resp.set_assetdetails_id ( assetdetails.assetdetails_id )
                assetdetails_resp.set_id ( assetdetails.id )
                assetdetails_resp.set_barcode ( assetdetails.barcode )
                assetdetails_resp.set_assetgroup_id ( assetdetails.assetgroup_id )
                assetdetails_resp.set_product_id ( api_obj.fetch_product ( assetdetails.product_id , emp , request ) )
                assetdetails_resp.set_cat ( api_obj.fetchcategory ( assetdetails.cat ) )
                assetdetails_resp.set_capdate ( assetdetails.capdate )
                assetdetails_resp.set_parent_id ( assetdetails.parent_id )
                assetdetails_resp.set_assetdetails_value ( assetdetails.assetdetails_value )
                assetdetails_resp.set_branch_id ( api_obj.fetch_branch ( assetdetails.branch_id ) )
                assetdetails_resp.set_assetdetails_status ( assetdetails.status )
                assetdetails_resp.set_requestfor ( assetdetails.requestfor )
                assetdetails_resp.set_requeststatus ( assetdetails.requeststatus )
                assetdetails_resp.set_assetlocation_id ( location.fetch_assetlocation ( assetdetails.assetlocation_id ) )
                assetdetails_list.append ( assetdetails_resp )
            # assetdetails_list.set_listcount(query_count)
            vpage = NWisefinPaginator ( assetdetails_data , vys_page.get_index ( ) , 10 )
            assetdetails_list.set_pagination ( vpage )

        return assetdetails_list

    def getclubsummary ( self , query_data , vys_page , emp , request ) :
        scope=request.scope
        condition = Q ( status=1 )
        if 'capstart_date' in query_data.keys ( ) :
            condition &= Q ( capdate=query_data [ 'capstart_date' ] )
        if 'barcode' in query_data.keys ( ) :
            condition &= Q ( barcode=query_data [ 'barcode' ] )
        if 'assetvalue' in query_data.keys ( ) :
            condition &= Q ( assetdetails_value=query_data [ 'assetvalue' ] )
        if 'cat' in query_data.keys ( ) :
            condition &= Q ( cat=query_data [ 'cat' ] )
        if 'branch' in query_data.keys ( ) :
            condition &= Q ( branch_id=query_data [ 'branch' ] )
        assetdetails_data = AssetDetails.objects.filter ( condition ).annotate ( dcount=Count ( 'parent_id' ) ) [
                            vys_page.get_offset ( ) :vys_page.get_query_limit ( ) ]
        api_obj = FaApiService ( scope)
        list_length = len ( assetdetails_data )
        location = AssetLocationService (scope )
        assetdetails_list = NWisefinList ( )
        if list_length > 0 :
            for assetdetails in assetdetails_data :
                assetdetails_resp = AssetDetailsResponse ( )
                assetdetails_resp.set_assetdetails_id ( assetdetails.assetdetails_id )
                assetdetails_resp.set_id ( assetdetails.id )
                assetdetails_resp.set_barcode ( assetdetails.barcode )
                assetdetails_resp.set_assetgroup_id ( assetdetails.assetgroup_id )
                assetdetails_resp.set_product_id ( api_obj.fetch_product ( assetdetails.product_id , emp , request ) )
                assetdetails_resp.set_cat ( api_obj.fetchcategory ( assetdetails.cat ) )
                assetdetails_resp.set_capdate ( assetdetails.capdate )
                assetdetails_resp.set_parent_id ( assetdetails.parent_id )
                assetdetails_resp.set_assetdetails_value ( assetdetails.assetdetails_value )
                assetdetails_resp.set_branch_id ( api_obj.fetch_branch ( assetdetails.branch_id ) )
                fa_stat = AssetStatus()
                assetdetails_resp.set_assetdetails_status (fa_stat.get_val( assetdetails.assetdetails_status ))
                assetdetails_resp.set_requestfor ( assetdetails.requestfor )
                assetdetails_resp.set_assetlocation_id (
                    location.fetch_assetlocation ( assetdetails.assetlocation_id ) )

                assetdetails_resp.set_requeststatus (assetdetails.requeststatus )
                assetdetails_resp.set_expanded ( False )
                assetdetails_list.append ( assetdetails_resp )
            # assetdetails_list.set_listcount(query_count)
            vpage = NWisefinPaginator ( assetdetails_data , vys_page.get_index ( ) , 10 )
            assetdetails_list.set_pagination ( vpage )

        return assetdetails_list
# PV--Anand
    def create_asset_details(self,resp_obj):
        return_json = dict()

        if not resp_obj.get_id() is None:
            asset_details = AssetDetails.objects.filter(id=resp_obj.get_id()).update(
                assetdetails_gid=resp_obj.get_assetdetails_gid(),
                assetdetails_productgid=resp_obj.get_assetdetails_productgid(),
                assetdetails_branchgid=resp_obj.get_assetdetails_branchgid(),
                branch_name=resp_obj.get_assetdetails_branch_name())
            asset_details = AssetDetails.objects.get(id=resp_obj.get_id())

        else:
            asset_details = AssetDetails.objects.create(assetdetails_gid=resp_obj.get_assetdetails_gid(),
                                                                assetdetails_productgid=resp_obj.get_assetdetails_productgid(),
                                                                assetdetails_branchgid=resp_obj.get_assetdetails_branchgid(),
                                                                branch_name=resp_obj.get_assetdetails_branch_name())

        assetdetailsresponse = Asset_Details_Response()
        assetdetailsresponse.set_id(asset_details.id)
        assetdetailsresponse.set_assetdetails_gid(asset_details.assetdetails_gid)
        assetdetailsresponse.set_assetdetails_productgid(asset_details.assetdetails_productgid)
        assetdetailsresponse.set_assetdetails_branchgid(asset_details.assetdetails_branchgid)
        assetdetailsresponse.set_branch_name(asset_details.branch_name)
        print(assetdetailsresponse)
        return assetdetailsresponse

    def get_all_assetdetails(self, vys_page, user_id, request):
        scope=request.scope
        asset_details=AssetDetails.objects.filter(status=1).order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(asset_details)
        api_obj = FaApiService(scope)
        assetdetails_list = NWisefinList()
        if len(asset_details) > 0:

            for asset in asset_details:
                assetdetails_resp = AssetDetailsResponse()
                assetdetails_resp.set_id(asset.id)
                assetdetails_resp.set_assetdetails_id(asset.assetdetails_id)
                assetdetails_resp.set_barcode(asset.barcode)
                assetdetails_resp.set_product_id(api_obj.fetch_product(asset.product_id, user_id, request).name)
                assetdetails_resp.set_branch_id(api_obj.fetch_branch(asset.branch_id))
                assetdetails_resp.set_assetdetails_value(asset.assetdetails_value)
                assetdetails_resp.set_assetdetails_cost(asset.assetdetails_cost)
                print (assetdetails_resp)
                assetdetails_list.append(assetdetails_resp)
                vpage = NWisefinPaginator(asset_details, vys_page.get_index(), 10)
                assetdetails_list.set_pagination(vpage)
            return assetdetails_list

    def get_asset_update_records(self,brn_id,user_id,request,vys_page):
        scope=request.scope
        return_list = NWisefinList ( )
        api_obj = FaApiService(scope)
        condition = Q(status=1)
        if 'init' in request.GET:
            condition &=Q(branch_id=brn_id)
        if 'barcode' in request.GET:
            condition &= Q(barcode=request.GET.get('barcode'))
        if 'branch' in request.GET:
            condition &= Q(branch_id=request.GET.get('branch'))
        if 'asset_edit' in request.GET:
            condition &= Q(barcode=request.GET.get('asset_edit'))

        print(condition, 'condition')
        invoice = ClearingDetailsService(scope)
        # query_count = AssetDetails.objects.filter(condition).count()
        query_count = AssetDetails.objects.filter(condition).values('barcode', 'assetheader')\
            .annotate(barcode__in=Count('assetheader__barcode')).count()
        asset_update_date=Asset_update.objects.filter(status='Available')
        asset_id=[]
        for data in asset_update_date:
            if data.barcode not in asset_id:
                asset_id.append(data.barcode)
        asset_details = AssetDetails.objects.exclude(barcode__in=asset_id).filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
        # a = []
        # for i in asset_details:
        #     temp = {}
        #     temp['id'] = i.id
        #     temp['assetdetails_value'] = i.assetdetails_value
        #     temp['assetdetails_cost'] = i.assetdetails_cost
        #     temp['assetdetails_id'] = i.assetdetails_id
        #     temp['barcode'] = i.barcode
        #     temp['product_id'] = i.product_id
        #     temp['branch_id'] = i.branch_id
        #     temp['assetheader__barcode'] = i.assetheader__barcode
        #     temp['description'] = i.description
        #
        #     if i.description__startswith == '(':
        #         temp['description']=i.description
        #     a.append(temp)
        #
        # df = pd.DataFrame(a).rename(columns={'assetheader__barcode':'header'})
        df = pd.DataFrame(asset_details.values('id','assetdetails_value','assetdetails_cost','assetdetails_id',
                                             'barcode','product_id','branch_id','assetheader__barcode','description',
                                             'faclringdetails_id')).rename(columns={'assetheader__barcode':'header'})
        df_agg = {'id': 'first', 'assetdetails_value': 'first', 'assetdetails_cost': 'first', 'assetdetails_id': 'first',
                 'barcode': 'first', 'product_id': 'first', 'branch_id': 'first', 'faclringdetails_id': 'first',
                 'description': 'first'}
        df = pd.DataFrame(df.groupby(by=['header'], as_index=False).agg(df_agg))
        df=df.to_dict('records')
        print('df',df)
        if len(asset_details) > 0:
            for data in df:
                asset=DictObj()
                asset=asset.get_obj(data)
                assetdetails_resp = AssetDetailsResponse()
                assetdetails_resp.set_id(asset.id)
                assetdetails_resp.set_assetdetails_id(asset.assetdetails_id)
                assetdetails_resp.set_barcode(asset.barcode)
                assetdetails_resp.set_product_id(api_obj.fetch_product(asset.product_id, user_id, request).name)
                assetdetails_resp.set_branch_id(api_obj.fetch_branch(asset.branch_id, request))
                assetdetails_resp.set_assetdetails_value(asset.assetdetails_value)
                assetdetails_resp.set_assetdetails_cost(asset.assetdetails_cost)
                assetdetails_resp.set_invoice_id(invoice.fetch_invoicedetailsforfaqery(asset.faclringdetails_id))
                assetdetails_resp.set_description(asset.description)
                print(assetdetails_resp)
                return_list.append(assetdetails_resp)
                return_list.set_listcount(query_count)
                vpage = NWisefinPaginator(asset_details, vys_page.get_index(), 10)
                return_list.set_pagination(vpage)
            return return_list


    def get_asset_update_edit_records(self,request,vys_page):
        scope=request.scope
        return_list = NWisefinList ( )
        api_obj = FaApiService(scope)
        condition = Q(pv_done= None)
        if 'Asset_edit' in request.GET:
            condition &= Q(barcode=request.GET.get('Asset_edit'))

        print(condition, 'condition')
        invoice = ClearingDetailsService(scope)
        # query_count = AssetDetails.objects.filter(condition).count()
        query_count = Asset_update.objects.filter(condition).values('barcode','asset_details')\
            .annotate(barcode__in=Count('asset_details__barcode')).count()
        asset_upd = Asset_update.objects.filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
        df = pd.DataFrame(asset_upd.values('id', 'asset_value','barcode', 'asset_cost', 'product_name', 'branch_code',
                                               'branch_name', 'kvb_asset_id', 'cr_number','control_office_branch',
                                           'make', 'serial_no', 'asset_tag', 'condition', 'status', 'remarks',
                                           'asset_details_id'))\
            .rename(columns={'product_name': 'product_id', 'cr_number': 'ecfnum', 'asset_cost': 'assetdetails_cost',
                            'asset_value': 'assetdetails_value'})
        print('df_query',df)
        df_agg = {'id': 'first', 'assetdetails_value': 'first', 'assetdetails_cost': 'first', 'branch_code': 'first',
                  'product_id': 'first', 'branch_name': 'first', 'kvb_asset_id': 'first', 'ecfnum': 'first',
                  'control_office_branch': 'first', 'asset_details_id': 'first', 'make': 'first',
                  'serial_no': 'first', 'asset_tag': 'first', 'condition': 'first', 'status': 'first',
                  'remarks': 'first'}

        df = pd.DataFrame(df.groupby(by=['barcode'], as_index=False).agg(df_agg))
        print('df_group', df)
        df=df.to_dict('records')
        print('df',df)
        if len(asset_upd) > 0:
            for data in df:
                asset=DictObj()
                asset=asset.get_obj(data)
                assetdetails_resp = AssetDetailsResponse()
                assetdetails_resp.set_id(asset.id)
                assetdetails_resp.set_assetdetails_id(asset.asset_details_id)
                assetdetails_resp.set_barcode(asset.barcode)
                assetdetails_resp.set_product_id(asset.product_id)
                assetdetails_resp.set_branch_code(asset.branch_code)
                assetdetails_resp.set_branch_name(asset.branch_name)
                assetdetails_resp.set_branch_id(asset.control_office_branch)
                assetdetails_resp.set_assetdetails_value(asset.assetdetails_value)
                assetdetails_resp.set_assetdetails_cost(asset.assetdetails_cost)
                assetdetails_resp.set_invoice_id(asset.ecfnum)
                assetdetails_resp.set_description(asset.kvb_asset_id)
                assetdetails_resp.set_asset_tag(asset.asset_tag)
                assetdetails_resp.set_make(asset.make)
                assetdetails_resp.set_serial_no(asset.serial_no)
                assetdetails_resp.set_condition(asset.condition)
                assetdetails_resp.set_status(asset.status)
                assetdetails_resp.set_remarks(asset.remarks)
                print(assetdetails_resp)
                return_list.append(assetdetails_resp)
                return_list.set_listcount(query_count)
                vpage = NWisefinPaginator(asset_upd, vys_page.get_index(), 10)
                return_list.set_pagination(vpage)
            return return_list

    # *****************************


# assetdetails impair
    def assetdetails_impair(self, data_arr, reversed_value, oldtotal_value, emp_id):
        a_reqfor = AssetRequestfor.IMPAIRMENT  # 6
        a_reqstatus = AssetRequestStatus.SUBMITTED  # 4
        reqstatus = FaRequestStatusUtil.MODIFICATION
        assetdetails_status = AssetStatus.IN_ACTIVE
        # try:
        for barcode in data_arr:
            assetdetails = AssetDetails.objects.get(barcode=barcode)
            end_date = assetdetails.enddate
            asset_value = assetdetails.assetdetails_value
            # revised_value
            balance_value = round(Decimal(oldtotal_value),2) - round(Decimal(reversed_value),2)
            value1 = round(Decimal(balance_value),2) / round(Decimal(oldtotal_value),2)
            value2 = asset_value*value1
            revised_value = asset_value - value2
            print(revised_value)

            # source, rate
            to_date = now()
            print(to_date, end_date)
            from datetime import datetime
            d = int(datetime.strftime(end_date, '%d'))
            m = int(datetime.strftime(end_date, '%m'))
            y = int(datetime.strftime(end_date, '%Y'))
            import datetime
            today = datetime.date.today()
            end_date = datetime.date(y, m, d)
            diff = end_date - today
            a = diff.days
            rate = (365 / (a + 1)) * 100
            print(rate)
            if rate > 0:
                source = AssetSource.FAIMPP
            else:
                source = AssetSource.FAIMPN
            print(source)
            assetdetailss = AssetDetails.objects.filter(barcode=barcode).update(deprate=rate,
                                                                                source=source,
                                                                                reducedvalue=revised_value,
                                                                                requestfor=a_reqfor,
                                                                                requeststatus=a_reqstatus,
                                                                                # assetdetails_status=assetdetails_status,
                                                                                updated_by=emp_id,
                                                                                updated_date=now())
            refid = ref_type = -1
            relrefid = assetdetails.id
            self.audit_function(assetdetails, refid, ref_type, relrefid,
                                emp_id, FaModifyStatus.UPDATE, reqstatus)
        success_obj = SuccessStatus.SUCCESS
        return success_obj
    def cpdate_makersum(self,vys_page,request,user_id):
        condition=Q(assetdetails_status=AssetStatus.ACTIVE,requestfor__in=[AssetRequestfor.DEFAULT,AssetRequestfor.NEW])
        if 'assetid' in request.GET:
            condition&=Q(assetdetails_id__icontains=request.GET.get('assetid'))
        if 'asset_value' in request.GET:
            condition&=Q(assetdetails_value=float(request.GET.get('asset_value')))
        if 'capdate' in request.GET:
            condition&=Q(capdate=parser.parse(request.GET.get('capdate')))
        if 'cat' in request.GET:
            condition&=Q(assetcat_id=request.GET.get('cat'))
        if 'branch' in request.GET:
            condition&=Q(branch_id=request.GET.get('branch'))
        summary_data=AssetDetails.objects.filter(condition).values().annotate(asset_count=Count('barcode')).exclude(assetheader_id=0,requeststatus=AssetRequestStatus.SUBMITTED).order_by('-id','-assetdetails_id')
        if len(summary_data)>0:
            fields=list(summary_data[0].keys())
            agg=dict.fromkeys(fields,'first')
            df=pd.DataFrame(summary_data).groupby(by=['barcode']).agg(agg)
            summary_data=df.to_dict('records')
            summary_data=summary_data[vys_page.get_offset():vys_page.get_query_limit()]
        scope=request.scope
        fa_obj=FaApiService(scope)
        resp_list=NWisefinList()
        dictobj=DictObj()
        for record in summary_data:

            record=dictobj.get_obj(record)
            print(record)
            asset_movement_validation = self.cap_date_validations(record)
            resp_obj = AssetDetailsResponse()
            resp_obj.set_id(record.id)
            resp_obj.validations=(asset_movement_validation)
            resp_obj.set_assetdetails_id(record.assetdetails_id)
            resp_obj.set_barcode(record.barcode)
            resp_obj.set_product_name(fa_obj.fetch_product(record.product_id,user_id,request))
            catname=AssetCat.objects.get(id=record.assetcat_id)
            resp_obj.set_cat(catname.subcatname)
            resp_obj.set_capdate(record.capdate)
            asst_header_data=AssetHeader.objects.filter(id=record.assetheader_id)
            if len(asst_header_data)>0:
                asst_header_data=asst_header_data[0]
            else:
                continue
            resp_obj.set_assetdetails_value(asst_header_data.valuetot)
            resp_obj.set_create_date(str(record.created_date))
            resp_obj.set_branch_id(fa_obj.fetch_branch(record.branch_id,request))
            stat=AssetStatus()
            resp_obj.set_assetdetails_status(stat.get_val(record.assetdetails_status))
            resp_list.append(resp_obj)
        vpage = NWisefinPaginator(resp_list.data, vys_page.get_index(), 10)
        resp_list.set_pagination(vpage)
        return resp_list.get()
    def cpdate_sum(self,vys_page,request,user_id):
        scope=request.scope
        asset_cat_ser=AssetCatService(scope)
        req_val_obj=AssetRequestStatus()
        asst_stat=AssetStatus()
        condition =Q(status=1)#& Q(capdate_status__in=[4,3,1])
        condition2 =Q(assetdetails_status__in=[AssetStatus.ACTIVE],source=AssetSource.FAMAKER)
        if 'assetid' in request.GET:
            condition2&=Q(barcode=request.GET.get('assetid'))
            condition &= Q(assetdetails_id__icontains=request.GET.get('assetid'))
        if 'asset_value' in request.GET:
            condition2=Q(assetdetails_value__icontains=float(request.GET.get('asset_value')))
        if 'capdate' in request.GET:
            if request.GET.get('capdate')!='':
                condition&=Q(oldcapdate__icontains=parser.parse(request.GET.get('capdate')))
        if 'category' in request.GET:
            condition2&=Q(assetcat_id=request.GET.get('category'))
        if 'branch' in request.GET:
            condition2&=Q(branch_id=request.GET.get('branch'))
        summary_data=AssetCapDate.objects.filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
        #************
        # resp_list = NWisefinList()
        # # resp_list=[]
        # for i in summary_data:
        #     asst_loc_obj = AssetLocationService(scope)
        #     fa_obj = FaApiService(scope)
        #     resp_obj = AssetDetailsResponse()
        #     try:
        #         assetdata=AssetDetails.objects.filter(condition2,assetdetails_id=i.assetdetails_id)[0]
        #     except:
        #         # traceback.print_exc()
        #         continue
        #     resp_obj.set_id(i.id)
        #     resp_obj.set_assetcapdate_id(i.assetdetails_id)
        #     resp_obj.set_product_name(fa_obj.fetch_product(assetdata.product_id, user_id, request))
        #     resp_obj.set_cat(asset_cat_ser.fetch_assetcat(assetdata.assetcat_id))
        #     resp_obj.set_capdate(i.oldcapdate)
        #     resp_obj.set_new_cap_date(i.capdate)
        #     resp_obj.set_barcode(assetdata.barcode)
        #     try:
        #         resp_obj.set_assetdetails_value(assetdata.assetheader.valuetot)
        #     except:
        #         continue
        #     resp_obj.set_branch_id(fa_obj.fetch_branch(assetdata.branch_id, request))
        #     resp_obj.set_assetlocation(asst_loc_obj.fetch_assetlocation(assetdata.assetlocation_id))
        #     fa_aud = FaAudit.objects.filter(ref_type=AssetRequestfor.CAPDATE, ref_id=i.id)
        #     if len(fa_aud) > 0:
        #         fa_aud = fa_aud[0]
        #         check_reason = fa_aud.data
        #         if req_val_obj.get_val(i.capdate_status) == 'REJECTED':
        #             resp_obj.checker_reason = check_reason['reason']
        #     else:
        #         resp_obj.checker_reason = 'APPROVED'
        #     resp_obj.set_reason(i.reason)
        #     resp_obj.set_assetdetails_status(asst_stat.get_val(assetdata.assetdetails_status))
        #     resp_obj.set_CP_status(req_val_obj.get_val(i.capdate_status))
        #     resp_list.append(resp_obj)
        # print(resp_list)
        # # resp_list=resp_list[vys_page.get_offset():vys_page.get_query_limit()]
        # vpage = NWisefinPaginator(resp_list.data, vys_page.get_index(), 10)
        # resp_list.set_pagination(vpage)
        #*******
        fa_obj=FaApiService(scope)
        asst_loc_obj=AssetLocationService(scope)
        asset_id_list=[]
        cap_id_list=[]
        for record in summary_data:
            if record.assetdetails_id not in asset_id_list:
                asset_id_list.append(record.assetdetails_id)
        condition2&=Q(assetdetails_id__in=asset_id_list)
        cap_date_data=AssetDetails.objects.filter(condition2)
        for record in cap_date_data:
            if record.assetdetails_id  in asset_id_list:
                cap_id_list.append(record.assetdetails_id)
        resp_list=NWisefinList()

        if len(summary_data) > 0:
            for record in summary_data:
                assetdet_record=None
                if record.assetdetails_id in cap_id_list:
                    ind=cap_id_list.index(record.assetdetails_id)
                    assetdet_record=cap_date_data[ind]
                    resp_obj = AssetDetailsResponse()
                    resp_obj.set_id(assetdet_record.id)
                    resp_obj.set_assetdetails_id(assetdet_record.assetdetails_id)
                    resp_obj.set_product_name(fa_obj.fetch_product(assetdet_record.product_id,user_id,request))
                    resp_obj.set_cat(asset_cat_ser.fetch_assetcat(assetdet_record.assetcat_id,request))#subcat
                    resp_obj.set_capdate(record.oldcapdate)
                    resp_obj.set_new_cap_date(record.capdate)
                    resp_obj.set_barcode(assetdet_record.barcode)
                    try:
                        resp_obj.set_assetdetails_value(assetdet_record.assetheader.valuetot)
                    except:
                        continue
                    resp_obj.set_branch_id(fa_obj.fetch_branch(assetdet_record.branch_id,request))
                    resp_obj.set_assetlocation(asst_loc_obj.fetch_assetlocation(assetdet_record.assetlocation_id))
                    fa_aud=FaAudit.objects.filter(ref_type=AssetRequestfor.CAPDATE,ref_id=record.id)
                    if len(fa_aud)>0:
                        fa_aud=fa_aud[0]
                        check_reason=fa_aud.data
                        if req_val_obj.get_val(record.capdate_status)=='REJECTED':
                            data=json.loads(check_reason.replace("'",'"'))
                            if 'reason' in data:
                                resp_obj.checker_reason=data['reason']
                            else:
                                resp_obj.checker_reason='None'
                    else:
                        resp_obj.checker_reason=''
                    resp_obj.set_reason(record.reason)
                    resp_obj.set_assetdetails_status(asst_stat.get_val(assetdet_record.assetdetails_status))
                    resp_obj.set_CP_status(req_val_obj.get_val(record.capdate_status))
                    resp_list.append(resp_obj)
            vpage = NWisefinPaginator(summary_data, vys_page.get_index(), 10)
            resp_list.set_pagination(vpage)
        else:
            vpage = NWisefinPaginator(resp_list.data, vys_page.get_index(), 10)
            resp_list.set_pagination(vpage)
            return resp_list.get()
        return json.dumps(resp_list.__dict__, default=dictdefault)
    def cpdate_checksum(self,vys_page,request,asset_id,user_id):
        scope=request.scope
        req_val_obj=AssetRequestStatus()
        asst_stat=AssetStatus()
        con=Q(capdate_status=AssetRequestStatus.SUBMITTED)
        summary_data=AssetCapDate.objects.filter(con)
        fa_obj=FaApiService(scope)
        asst_loc_obj=AssetLocationService(scope)
        asset_id_list=[]
        cap_id_list=[]
        for record in summary_data:
            if record.assetdetails_id not in asset_id_list:
                asset_id_list.append(record.assetdetails_id)
        if 'assetid' not in request.GET:
            con2=Q(assetdetails_id__in=asset_id_list,requestfor=AssetRequestfor.CAPDATE)
        else:
            con2=Q(barcode__icontains=request.GET.get('assetid'))
            con2&=Q(assetdetails_id__in=asset_id_list)
        if 'capdate' in request.GET:
            con= Q(capdate=request.GET.get('capdate'))
        if 'asset_value' in request.GET:
            con2&=Q(assetdetails_value=float(request.GET.get('asset_value')))
        if 'cat' in request.GET:
            con2&=Q(assetcat_id=request.GET.get('cat'))
        if 'branch' in request.GET:
            con2&=Q(branch_id=request.GET.get('branch'))
        cap_list=AssetCapDate.objects.filter(con)
        cap_data_filter=[]
        for data in cap_list:
            if data.assetdetails_id not in cap_data_filter:
                cap_data_filter.append(data.assetdetails_id)
        con2&=Q(assetdetails_id__in=cap_data_filter)
        cap_date_data=AssetDetails.objects.filter(con2)
        for record in cap_date_data:
            cap_id_list.append(record.barcode)
        resp_list=NWisefinList()
        asstcat_serv=AssetCatService(scope)
        for record in summary_data:
            assetdet_record=None
            if record.assetdetails_id[:-6] in cap_id_list:
                ind=cap_id_list.index(record.assetdetails_id[:-6])
                assetdet_record=cap_date_data[ind]
                resp_obj = AssetDetailsResponse()
                resp_obj.set_id(record.id)
                resp_obj.set_assetcat(asstcat_serv.fetch_assetcat(assetdet_record.assetcat_id,request))
                resp_obj.set_assetdetails_id(assetdet_record.assetdetails_id)
                resp_obj.set_product_name(fa_obj.fetch_product(assetdet_record.product_id,user_id,request))
                resp_obj.set_cat(assetdet_record.cat)
                resp_obj.set_capdate(record.oldcapdate)
                resp_obj.set_new_cap_date(record.capdate)
                resp_obj.set_barcode(assetdet_record.barcode)
                resp_obj.set_assetdetails_value(assetdet_record.assetdetails_value)
                resp_obj.set_branch_id(fa_obj.fetch_branch(assetdet_record.branch_id,request))
                resp_obj.set_assetlocation(asst_loc_obj.fetch_assetlocation(assetdet_record.assetlocation_id))
                resp_obj.set_reason(record.reason)
                resp_obj.set_assetdetails_status(asst_stat.get_val(assetdet_record.status))
                resp_obj.set_CP_status(req_val_obj.get_val(record.capdate_status))
                resp_list.append(resp_obj)
        vpage = NWisefinPaginator(resp_list.data, vys_page.get_index(), 10)
        resp_list.set_pagination(vpage)
        return json.dumps(resp_list.__dict__, default=dictdefault)
    def cpdate_make(self,capdate_obj,request,user_id):
        try:
            asset_datas=AssetDetails.objects.filter(id__in=capdate_obj.assetid_list)
            for record in asset_datas:

                record.requestfor=AssetRequestfor.CAPDATE
                record.requeststatus=AssetRequestStatus.SUBMITTED

                AssetCapDate.objects.create(
                    assetdetails_id=record.assetdetails_id,
                    date=now(),
                    capdate_status=AssetRequestStatus.SUBMITTED,
                    reason=capdate_obj.reason,
                    capdate=parser.parse(capdate_obj.capdate),
                    oldcapdate=record.capdate,
                    status=AssetStatus.ACTIVE,
                    created_by=user_id
                )
                record.save()
            resp=NWisefinSuccess()
            resp.set_status(SuccessStatus.SUCCESS)
            resp.set_message(SuccessMessage.CREATE_MESSAGE)
        except Exception as e:
            logger.info('FAL_CPDATE_EXCEPT:{}'.format(traceback.print_exc()))
            resp = Error()
            resp.set_code(ErrorMessage.INVALID_DATA)
            resp.set_description(e)
        return resp
    def cpdate_check(self,capdate_obj,request,user_id):
        validate=validate_data(capdate_obj,user_id)
        if isinstance(validate,Error):
            return validate
        capdate_datas=AssetCapDate.objects.filter(id__in=capdate_obj.capdate_id)
        barcode_list=[]
        for data in capdate_datas:
            if data.assetdetails_id not in barcode_list:
                barcode_list.append(data.assetdetails_id)
        asset_det_data=AssetDetails.objects.filter(assetdetails_id__in=barcode_list)
        asset_id_list=[]
        for asset in asset_det_data:
            if asset.assetdetails_id not in asset_id_list:
                asset_id_list.append(asset.assetdetails_id)
        for record in capdate_datas:
            if capdate_obj.status=='APPROVE':
                record.capdate_status=AssetRequestStatus.APPROVED
                asst_data=AssetDetails.objects.filter(assetdetails_id=record.assetdetails_id)[0]
                asst_cat_data = AssetCat.objects.get(id=asst_data.assetcat_id)

                end_date = record.capdate+ relativedelta(months=asst_cat_data.lifetime)-relativedelta(days=1)
                capdate=record.capdate
                ind=asset_id_list.index(record.assetdetails_id)
                asset_det=asset_det_data[ind]
                asset_det.enddate = end_date
                asset_det.requestfor=AssetRequestfor.DEFAULT
                asset_det.requeststatus=AssetRequestStatus.APPROVED
                asset_det.capdate=capdate
                record.save()
                asset_det.save()
                resp = NWisefinSuccess()
                resp.set_status(SuccessStatus.SUCCESS)
                resp.set_message(SuccessMessage.APPROVED_MESSAGE)
            elif capdate_obj.status=='REJECT':
                fa_aud=FaAudit()
                fa_aud.ref_type=AssetRequestfor.CAPDATE
                fa_aud.ref_id=record.id
                fa_aud.data=capdate_obj.__dict__
                fa_aud.req_status=AssetStatus.ACTIVE
                fa_aud.user_id=user_id
                fa_aud.save()
                record.capdate_status = AssetRequestStatus.REJECTED
                ind = asset_id_list.index(record.assetdetails_id)
                asset_det = asset_det_data[ind]
                asset_det.requestfor = AssetRequestfor.DEFAULT
                asset_det.requeststatus = AssetRequestStatus.REJECTED
                record.save()
                asset_det.save()
                resp = NWisefinSuccess()
                resp.set_status(SuccessStatus.SUCCESS)
                resp.set_message(SuccessMessage.REJECTED_MESSAGE)
        return resp
    def fetch_asset_id_grp_non(self, vys_page,asset_id,request):
        scope=request.scope
        fa_obj=FaApiService(scope)
        assetdetails_data=AssetDetails.objects.filter(id=asset_id.asset_id)#[vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(assetdetails_data)
        assetdetails_list = NWisefinList()
        api_obj = FaApiService(scope)
        if list_length > 0:
            for assetdetails in assetdetails_data:
                img_bsf = []
                assetdetails_resp = AssetDetailsResponse()
                assetdetails_resp.set_id(assetdetails.id)
                assetdetails_resp.set_assetdetails_id(assetdetails.assetdetails_id)
                assetdetails_resp.set_assetgroup_id(assetdetails.assetgroup_id)
                assetdetails_resp.set_product_id(
                    api_obj.fetch_product(assetdetails.product_id, request.user.id, request))
                assetdetails_resp.set_cat(assetdetails.assetcat)
                assetdetails_resp.set_apcat(fa_obj.fetchcategory(assetdetails.cat,request))
                assetdetails_resp.set_crnum(assetdetails.crnum)
                assetdetails_resp.set_capdate(assetdetails.capdate)
                assetdetails_resp.set_vendorname(assetdetails.vendorname)
                assetdetails_resp.set_assetdetails_value(assetdetails.assetdetails_value)
                assetdetails_resp.set_branch_id(api_obj.fetch_branch(assetdetails.branch_id, request))
                stat_obj = AssetStatus()
                assetdetails_resp.set_assetdetails_status(stat_obj.get_val(assetdetails.status))
                # assetdetails_resp.set_assetdetails_status(assetdetails.status)
                assetdetails_resp.set_subcat(assetdetails.subcat)
                not_in = ['0', '[]', '', None]
                if assetdetails.imagepath not in not_in:
                    image_data = json.loads(assetdetails.imagepath.replace("'", '"'))
                    for images in image_data:
                        s3 = boto3.resource('s3')
                        s3_obj = s3.Object(bucket_name=settings.BUCKET_NAME_FOR_ASSETS, key=images)
                        body = s3_obj.get()['Body']
                        img_bsf.append(base64.b64encode(body.read()))
                assetdetails_resp.set_imagepath(img_bsf)
                assetdetails_list.append(assetdetails_resp)
            vpage = NWisefinPaginator(assetdetails_data, vys_page.get_index(), 10)
            assetdetails_list.set_pagination(vpage)
        return assetdetails_list

    def parentchildvalidation(self,listofbarcode):
        for i in listofbarcode:
            parent_id=list(AssetDetails.objects.filter (barcode=i ).values_list('parent_id',flat=True))[0]
            if parent_id:
                barcode_parent_id=list(AssetDetails.objects.filter(parent_id=parent_id).values_list('barcode',flat=True))
                newlist=set(listofbarcode)&set(barcode_parent_id)
                difflist = list ( set ( listofbarcode ).difference ( barcode_parent_id ) )
                if difflist==[]:
                    continue
                matchlist = list ( set ( listofbarcode ).intersection ( barcode_parent_id ) )
                if matchlist==listofbarcode:
                    success_obj = NWisefinSuccess ( )
                    success_obj.set_status ( 'valid asset' )
                    return success_obj
        success_obj = NWisefinSuccess( )
        success_obj.set_status ( 'valid asset' )
        return success_obj
    #sms data get barcode

    def get_barcode(self,barcode,request=None):
        scope=request.scope
        condition = Q(barcode__in=barcode) & Q(status=1)
        obj = AssetDetails.objects.filter(condition).values('id','barcode','assetdetails_status','product_id','assetcat__subcategory_id')
        arr = []
        from faservice.util.FaApiService import FaApiService
        # from faservice.service.apsubcategoryservice import SubcategoryService
        sub_serv = FaApiService(scope)
        for i in obj:
            data = {"id": i['id'], "barcode": i['barcode'],"assetdetails_status":i['assetdetails_status'],
                    "product_id": sub_serv.fetch_product(i['product_id']),
                    "assetcat__subcategory_id": sub_serv.fetchsubcategory(i['assetcat__subcategory_id'])}
            arr.append(data)
        return arr

    # def get_asset_name(self,name):
    #     condition = Q(name__in=name) & Q(status=1)
    #     mst_prod = masterservice_Product.objects.filter(condition)
    #     mst_prod = { "name": mst_prod.name}
    #     mstsrv_prod = json.dumps(mst_prod, indent=5)
    #     return HttpResponse(mstsrv_prod, content_type='application/json')
    #
    # def get_branch_name(self,name):
    #     condition = Q(name__in=name) & Q(status=1)
    #     brn_name = userservice_employeebranch.objects.filter(condition)
    #     brn_name = { "name": brn_name.name}
    #     branch_name = json.dumps(brn_name, indent=5)
    #     return HttpResponse(branch_name, content_type='application/json')

    def cap_date_validations(self,assetdetail):
        validations={}
        asst_check=AssetDetails.objects.filter(barcode=assetdetail.barcode,assetdetails_status  =AssetStatus.ACTIVE,status=1)
        if len(asst_check)>1:
            validations['disable']=True
        else:
            validations['disable']=False
        return validations
    def get_source(self):
        asst_src=AssetSource.source_dict
        out=[]
        for key,value in asst_src.items():
            out_data={}
            out_data['key']=key
            out_data['value']=value
            out.append(out_data)
        return json.dumps(out)

    def create_asset_map(self, data, emp_id):

        if not data.get_id() is None:
            asset_barcode = AssetBarcodeMap.objects.using(self._current_app_schema()).filter(id=data.get_id(),
                                                                                             entity_id=self._entity_id()).update(
                asset_barcode=data.get_asset_barcode(),
                status=data.get_status(),
                emp_id=data.get_emp_ename(),
                from_date=data.get_from_date(),
                to_date=data.get_to_date(),
                updated_by=emp_id,
                updated_date=now())
            asset_barcode = AssetBarcodeMap.objects.using(self._current_app_schema()).get(id=data.get_id())

        else:
            try:
                emp_check=AssetBarcodeMap.objects.filter(asset_barcode=data.get_asset_barcode(),status=1)
                if len(emp_check)>0:
                    resp=Error()
                    resp.set_code(ErrorMessage.DUPLICATE_ENTRY)
                    resp.set_description(ErrorDescription.ALEADY_MAPPED)
                    return resp
                asset_barcode = AssetBarcodeMap.objects.create(
                    asset_barcode=data.get_asset_barcode(),

                    status=data.get_status(),
                    emp_id=data.get_emp_ename(),
                    from_date=data.get_from_date(),
                    to_date=data.get_to_date(),
                    created_by=emp_id,
                    created_date=now())
                # assetdetails_resp = FapvRespon()
                # assetdetails_resp.set_id(asset_barcode.id)
                # assetdetails_resp.set_barcode(asset_barcode.barcode)

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

    def fetch_emp_map(self, vys_page, barcode, emp, emp_id, request):
        condition = Q(status=1)
        if emp != "" and emp != None:
            condition &= Q(emp_id=emp)
        if barcode != "" and barcode != None:
            condition &= Q(asset_barcode__icontains=barcode)

        asset_barcode = AssetBarcodeMap.objects.filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
        asset_lst = NWisefinList()
        if len(asset_barcode) > 0:
            for asset in asset_barcode:
                assetdetails_resp = FapvRespon()
                assetdetails_resp.set_id(asset.id)
                api_obj = ApiService(request.scope)
                assetdetails_resp.set_emp_name(api_obj.get_empsingle_id(request, asset.emp_id))
                asset_dtls = AssetDetails.objects.filter(barcode=asset.asset_barcode, status=1).order_by('id')
                if len(asset_dtls)>0:

                    assetdetails_resp.set_product_name(api_obj.fetch_productdata(request, asset_dtls[0].product_id))
                else:
                    assetdetails_resp.set_product_name("")
                assetdetails_resp.set_barcode(asset.asset_barcode)
                assetdetails_resp.set_status(asset.status)
                assetdetails_resp.set_from_date(asset.from_date)
                assetdetails_resp.set_to_date(asset.to_date)
                asset_lst.append(assetdetails_resp)
            vpage = NWisefinPaginator(asset_barcode, vys_page.get_index(), 10)
            asset_lst.set_pagination(vpage)
            return asset_lst

    def asset_barcode_map_activate_inactivate(self, request, asset_obj):
        ast_data = AssetBarcodeMap.objects.get(id=asset_obj.id).asset_barcode
        asset_data = AssetBarcodeMap.objects.filter(asset_barcode=ast_data,status=1).exclude(id=asset_obj.id)
        if len(asset_data) > 0:
            resp = Error()
            resp.set_code(ErrorMessage.DUPLICATE_ENTRY)
            resp.set_description(ErrorDescription.ALEADY_MAPPED)
            return resp

        if (int(asset_obj.status) == 0):

            asset_data = AssetBarcodeMap.objects.get(id=asset_obj.id)
            asset_data.status=1
            asset_data.save()
        else:
            asset_data = AssetBarcodeMap.objects.get(id=asset_obj.id)
            asset_data.status = 0
            asset_data.to_date=datetime.datetime.now()
            asset_data.save()


        if int(asset_obj.status) == 1:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.INACTIVATED)
            return data
        else:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.ACTIVATED)
            return data

import requests as rq
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def asset_entry_sync(request=None):
    data=AssetEntrySync.objects.filter().exclude(hand_shake=1)
    barcode_list=[]
    for record in data:
        if record.assetdetails_id[0:-6] not in barcode_list:
            barcode_list.append(record.assetdetails_id[0:-6])

    sync_datas=AssetEntry.objects.filter().exclude(crno__in=barcode_list)
    response_data=[]
    scope=request.scope
    fa_obj=FaApiService(scope)
    if request ==None:
        request=create_req_obj()
        for sync_data in sync_datas:
            sync_data.__dict__.pop('_state')
        dict_data=sync_data.__dict__
        apcat=fa_obj.fetchcategory(dict_data['apcatno'],request)
        apsubcat=fa_obj.fetchsubcategory(dict_data['apsubcatno'],request)
        dict_data['apcatno']=apcat
        dict_data['apsubcatno']=apsubcat
        params = json.dumps(dict_data.__dict__, default=dictdefault)
        response_data.append(params)
    return HttpResponse(response_data,content_type='application/json')
            # rq.post()
class req:
    headers={}
def create_req_obj():
    request_obj=req()
    auth_params={
            "username": "apuser",
            "password": "dnNvbHYxMjM="
        }
    url=settings.SERVER_IP+'/usrserv/auth_token'
    resp=rq.post(url,json.dumps(auth_params))
    try:
        resp_data=json.loads(resp.text)
    except:
        traceback.print_exc()
    request_obj.headers['Authorization']=resp_data['token']
    return request_obj

def custom500(request, *args, **argv):
    print(request)
    print(args)
    print(argv)
    pass





