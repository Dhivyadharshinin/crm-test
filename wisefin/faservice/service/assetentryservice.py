import json
import traceback

import requests
from django.db.models import Q
from requests.auth import HTTPBasicAuth
from faservice.util.fautil import AssetStatus, RepostConst, AssetDetailsRequestStatus, Fa_Doctype, Asset_Doctype_Code, \
    AssetRequestfor, RequestStatus, AssetEntryType
from nwisefin import settings
from nwisefin.settings import logger
from django.utils.timezone import now
from faservice.data.request.assetentryrequest import CreditDebitRequest
from faservice.data.response.assetentryresponse import AssetEntryResponse
from faservice.models import AssetEntry, AssetDetails, ClearingDetails, AssetEntrySync, AssetGroup
from faservice.util.FaApiService import FaApiService, DictObj
from masterservice.service.Hsnservice import Hsnservice
from masterservice.service.stateservice import StateService
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from vendorservice.service.branchservice import branchservice
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessMessage, SuccessStatus
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage

#create:
class AssetentryService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
    def create_assetentry(self,emp_id,assetdetails_id,request,data_dict):
        asstdetails = AssetDetails.objects.filter(id__in=assetdetails_id['assetdetails_id'])
        scope=request.scope
        fa_obj=FaApiService(scope)
        response=[]
        for asstdet in asstdetails:
            cr,dt=data_dict[asstdet.id]
            sub_data_deb=fa_obj.fetchsubcategory(asstdet.subcat,request)
            product_data = fa_obj.fetch_product(asstdet.product_id,emp_id,request)
            branch_data = fa_obj.fetch_branch(asstdet.branch_id,request)
            logger.info("assetentry")
            if isinstance(branch_data,dict):
                branch_data=DictObj(branch_data)
            print("branch",branch_data.code)
            doctype = ClearingDetails.objects.get(id=asstdet.faclringdetails_id)
            deb_request=CreditDebitRequest()
            ##CALL FA TEMPLATE API FROM ENTRYSERVICE
            ##GENERATING CREDIT DATA
            credit_list=[]
            debit_list=[]
            for cred_data in cr.apcredit:
                cred_request = CreditDebitRequest()
                sub_data = Asset_Doctype_Code()
                if cred_data.subcategory_code['code']=='DYNAMIC':
                    try:
                        cred_request.gl = sub_data.get_gl_no(doctype.doctype, request)['gl']  ##gl from doctype
                    except:
                        err = Error()
                        err.set_code(ErrorMessage.NO_SUBCAT_GL_DATA)
                        err.set_description(ErrorDescription.NO_SUBCAT_GL_DATA)
                        return err
                else:
                    cred_request.gl=cred_data.gl_no
                cred_request.InvoiceHeader_Gid=asstdet.id
                cred_request.crno = asstdet.barcode
                cred_request.branchgid = asstdet.branch_id
                cred_request.refgid = asstdet.id
                cred_request.ApCatNo = asstdet.cat
                cred_request.ApSubCatNo = asstdet.subcat
                cred_request.entry_amt = cred_data.amount


                cred_request.TransactionDate = now().date()
                cred_request.ValueDate = now().date()
                cred_request.TransactionTime = now().time()
                cred_request.Period = now().month
                cred_request.Module = 4
                cred_request.Screen = 1
                cred_request.type = AssetEntryType.CREDIT
                cred_request.Entry_Remarks = branch_data.code+asstdet.barcode+product_data.name
                credit_list.append(cred_request)
            logger.info("debitsuccess")
            ##GENERTING DEBIT DATA LIST
            for deb_data in dt.apdebit:
                if deb_data.subcategory_code['code']=='DYNAMIC':
                    gl_data=sub_data_deb.glno
                else:
                    gl_data=deb_data.gl_no
                deb_request.InvoiceHeader_Gid = asstdet.id
                deb_request.crno = asstdet.barcode
                deb_request.branchgid = asstdet.branch_id
                deb_request.refgid = asstdet.id
                deb_request.ApCatNo = asstdet.cat
                deb_request.ApSubCatNo = asstdet.subcat
                deb_request.entry_amt = deb_data.amount
                deb_request.gl = gl_data ##Gl from subcategory
                deb_request.TransactionDate = now().date()
                deb_request.ValueDate = now().date()
                deb_request.TransactionTime = now().time()
                deb_request.Period = now().month
                deb_request.Module = 4
                deb_request.Screen = 1
                deb_request.type = AssetEntryType.DEBIT
                deb_request.Entry_Remarks = branch_data.code+asstdet.barcode+product_data.name
                debit_list.append(deb_request)
            logger.info("creditsuccess")
            credeb = credit_list+debit_list
            data_list=[]
            for data in credeb:
                invh = {"branch_id":data.branchgid,
                        "fiscalyear": now().year,
                        "period": data.Period,
                        "module": data.Module,
                        "screen": data.Screen,
                        "transactiondate": now().date(),
                        "transactiontime": now().time(),
                        "valuedate": now().date(),
                        "valuetime": now().time(),
                        "cbsdate": now(),
                        "localcurrency": 1,
                        "localexchangerate": "12",
                        "currency": "1",
                        "exchangerate":"10",
                        "isprevyrentry": "1",
                        "reversalentry": "2",
                        "refno": data.crno,
                        "crno":data.crno,
                        "refid": data.refgid,
                        "reftableid": "1",
                        "type": data.type,
                        "gl": data.gl,
                        "apcatno": data.ApCatNo,
                        "apsubcatno": data.ApSubCatNo,
                        "wisefinmap": "12",
                        "glremarks": data.Entry_Remarks,
                        "amount": data.entry_amt,##AMOUNT FROM ENTRYSERVICE TEMPLATE METHOD
                        "fcamount":"12",
                        "ackrefno": "123",
                        "created_by":emp_id,
                        "created_date":now()}
                data_list.append(invh)
            ## CALL AFTER FA ASSET ENTRY TEMPLATE API
            resp_list=[]

            resp=fa_obj.asset_entry_create(request,emp_id,data_list)
            if isinstance(resp,NWisefinSuccess):
                if resp.status==SuccessStatus.SUCCESS:
                    AssetDetails.objects.filter(id=asstdet.id).update(
                        assetdetails_status=AssetStatus.ACTIVE,
                        requestfor=AssetRequestfor.DEFAULT,
                        requeststatus=AssetDetailsRequestStatus.APPROVED,
                        status=AssetStatus.ACTIVE
                    )
            else:
                AssetDetails.objects.filter(id=asstdet.id).update(
                    assetdetails_status=AssetStatus.ENTRY_FAILED
                )


            # print("assetentry", invh)
            # dict_obj=DictObj()
            # invh=dict_obj.get_obj(invh)
            # invh.id=resp.entry_id
            # invh_data = AssetEntryResponse()
            # invh_data.set_id(invh.id)
            # invh_data.set_branch_id(invh.branch_id)
            # invh_data.set_fiscalyear(invh.fiscalyear)
            # invh_data.set_period(invh.period)
            # invh_data.set_module(invh.module)
            # invh_data.set_screen(invh.screen)
            # invh_data.set_transactiondate(invh.transactiondate)
            # invh_data.set_transactiontime(invh.transactiontime)
            # invh_data.set_valuedate(invh.valuedate)
            # invh_data.set_valuetime(invh.valuetime)
            # invh_data.set_cbsdate(invh.cbsdate)
            # invh_data.set_localcurrency(invh.localcurrency)
            # invh_data.set_localexchangerate(invh.localexchangerate)
            # invh_data.set_currency(invh.currency)
            # invh_data.set_exchangerate(invh.exchangerate)
            # invh_data.set_isprevyrentry(invh.isprevyrentry)
            # invh_data.set_reversalentry(invh.reversalentry)
            # invh_data.set_refno(invh.refno)
            # invh_data.set_crno(invh.crno)
            # invh_data.set_refid(invh.refid)
            # invh_data.set_reftableid(invh.reftableid)
            # invh_data.set_type(invh.type)
            # invh_data.set_gl(invh.gl)
            # invh_data.set_apcatno(invh.apcatno)
            # invh_data.set_apsubcatno(invh.apsubcatno)
            # invh_data.set_wisefinmap(invh.wisefinmap)
            # invh_data.set_amount(invh.amount)
            # invh_data.set_fcamount(invh.fcamount)
            # invh_data.set_glremarks(invh.glremarks)
            # invh_data.set_ackrefno(invh.ackrefno)
            # response.append(invh_data)
        logger.info("inserted")
        return resp_list

    def create_fundservice(self,assentry_id_list,request):
        scope=request.scope
        fa_obj=FaApiService(scope)
        asstent_datas = list(AssetEntry.objects.filter(id__in=assentry_id_list))
        asst_list=[]
        for asst in asstent_datas[::2]:
            asst_list.append([asstent_datas[asstent_datas.index(asst)],asstent_datas[(asstent_datas.index(asst)+1)]])
        for asstent_data in asst_list:
            asstent = asstent_data[0]
            astd = asstent.refid
            asst_data=AssetDetails.objects.get(id=astd)
            clearingdet_data=ClearingDetails.objects.get(id=asst_data.faclringdetails_id)
            sub_cat_data=None
            if clearingdet_data.doctype==str(Fa_Doctype.REG):
                sub_cat_data=fa_obj.fetch_code_subcategory(Asset_Doctype_Code.REGULAR,request)
            if clearingdet_data.doctype==str(Fa_Doctype.CWIP):
                sub_cat_data=fa_obj.fetch_code_subcategory(Asset_Doctype_Code.CAP_WORK_IN_PROGRESS,request)
            if clearingdet_data.doctype==str(Fa_Doctype.BUC):
                sub_cat_data=fa_obj.fetch_code_subcategory(Asset_Doctype_Code.BUILDING,request)

            prod = {
                "productType": "DP"
            }

            cbs_date={'UAT_DATE':str(now().date())}
            fa_obj = FaApiService(scope)
            branch_data = fa_obj.fetch_branch(asstent.branch_id, request)
            print("branch",branch_data.__dict__)
            logger.info("fund entry")
            date=now().date()
            try:
                cbdate=str(date.day)+'/'+str(date.month)+'/'+str(date.year)
            except:
                cbdate="22/01/2022"

            fund = {
          "Src_Channel": "EMS",
          "ApplicationId": asst_data.barcode,
          "TransactionBranch": RepostConst.TRNBRANCH,
          "Txn_Date":cbdate,
          "productType": "DP",
          "Fund_Transfer_Dtls": [
            {
              "Amount":int(asstent.amount),
              "CBSDATE": str(asstent.cbsdate.strftime('%d/%m/%Y')),
              "Brn_Code": fa_obj.fetch_branch(asstent.branch_id).code,
              "Entry_Gid": asstent.id,
              "Narration": "1234",
              "Cr_Dr_Flag": "D",
              "Account_Number": asstent.gl,
              "GL_Reference_No": ""

            },
            {
              "Amount":int(asstent.amount),
              "CBSDATE": str(asstent.cbsdate.strftime('%d/%m/%Y')),
              "Brn_Code": fa_obj.fetch_branch(asstent.branch_id).code,
              "Entry_Gid": asstent.id,
              "Narration": "1234",
              "Cr_Dr_Flag": "C",
              "Account_Number": sub_cat_data['gl'],#Doc_Type Gl_no
              "GL_Reference_No": ""
            }
          ]
        }
            print("fund",fund)
            logger.info("inserted")
            prod = {
                "productType": "DP"
            }
            logger.info("date inserted")
            # token = self.get_token()
            fd = self.amttransfer(fund,astd)
            if isinstance(fd,Error):
                return fd
            ###RAVI CODE
            asstdet = AssetDetails.objects.filter(id=astd).update(
                assetdetails_status=AssetStatus.ACTIVE,
                requestfor=AssetRequestfor.DEFAULT,
                requeststatus=AssetDetailsRequestStatus.APPROVED,
                status=AssetStatus.ACTIVE
            )
            cbdd = self.cbsdate(prod)
            try:
                grn_var = AssetEntry.objects.filter(id__in=assentry_id_list).update(
                    ackrefno = 888,
                    status = 1
                    )
            except:
                AssetEntry.objects.filter(id__in=assentry_id_list).update(
                    status=AssetStatus.ACTIVE##BYPASS_AMOUNT_TRANSFER CHANGE BACK TO ENTRY FAIL
                )
        logger.info("ackno updated")
        return fd

    def get_token(self):
        client_url = settings.CLIENT_URL
        token_url = client_url + str("next//v1/oauth/cc/accesstoken")
        # token_url = settings.ADURL_ACCESS
        logger.info("token url " + str(token_url))
        token_data = {"grant_type": "client_credentials"}
        token_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        token = requests.post(token_url, data=token_data, headers=token_headers, verify=False,
                              auth=HTTPBasicAuth(settings.ADURL_KEY, settings.CLIENT_SECRET))
        token_json = json.loads(token.text)
        token = token_json.get('access_token')
        return token

    def amttransfer(self,fund,assetdet_id=None):
        vysfin_url = settings.CLIENT_URL
        ecf_post_url = vysfin_url + str("nbfc/v1/mwr/amount-transfer")
        resp_data = fund
        print("mono", resp_data)
        token_data='Bearer ' + self.get_token()
        print(token_data)
        # resp = requests.post(ecf_post_url, headers={'Authorization': token_data,'Content-Type':'application/json'},params={},data=json.dumps(resp_data),
        #                      verify=False)
        # results = resp.content.decode("utf-8")
        # results = json.loads(results)
        # print(resp.text)
        # try:
        #     # results = json.loads(resp.text)
        CBSReferenceNo = 888#results.get("CbsStatus")[0].get("CBSReferenceNo")
        # except:
        asstdet = AssetDetails.objects.filter(id=assetdet_id).update(
        assetdetails_status = AssetStatus.ACTIVE,             ##BYPASS_AMOUNT_TRANSFER CHANGE BACK TO ENTRY FAIL
        requestfor = AssetRequestfor.DEFAULT,##Remove below
        requeststatus = RequestStatus.APPROVED,
        status = AssetStatus.ACTIVE
        )


        print("refno",CBSReferenceNo)
        return None

    def cbsdate(self,cbsd):
        vysfin_url = settings.CLIENT_URL
        ecf_post_url = vysfin_url + str("nbfc/v1/mwr/uat-date")
        resp_data = cbsd
        print("mono", resp_data)
        token=self.get_token()
        resp = requests.get(ecf_post_url, headers={'Authorization': 'Bearer ' + token,'Content_type':'application/json'},data=json.dumps(resp_data))
        # results = resp..decode("utf-8")
        results = json.loads(resp.text)
        print("result:", results)
        return results

    def repost(self,assetid_list,emp_id,request):
        if 'assetdetails_id' in assetid_list:
            if isinstance(assetid_list['assetdetails_id'],list):
                pass
            else:
                assetid_list['assetdetails_id']=[assetid_list['assetdetails_id']]
        if assetid_list["assetgroup"] != '0':
            try:
                grp=AssetGroup.objects.get(number=assetid_list['assetgroup'])
                condition=Q(assetgroup_id=grp.id)
                condition&=Q(assetdetails_status=AssetStatus.ENTRY_FAILED)
                asstdet = AssetDetails.objects.filter(condition)
                ast_det = []
                for i in asstdet:
                    ast_det.append(i.id)
            except:
                err=Error()
                err.set_code(ErrorMessage.INVALID_ASSETGROUP_ID)
                err.set_code(ErrorDescription.INVALID_ASSETGROUP_ID)
                return err
        else:
            ast_det=assetid_list['assetdetails_id']
            print("assr",ast_det)
        for j in ast_det:
            asstent = AssetEntry.objects.filter(refno=j[:-6])
            sas = []
            for k in asstent:
                sas.append(k.id)
            repost = self.create_fundservice(sas,request)
            print("result:", repost)
            return repost

    def Assetentry_get(self,barcode,reqest):
        response = []
        invh_data = AssetEntryResponse()
        try:
            invh = AssetEntry.objects.get(crno=barcode)

            invh_data.set_id(invh.id)
            invh_data.set_branch_id(invh.branch_id)
            invh_data.set_fiscalyear(invh.fiscalyear)
            invh_data.set_period(invh.period)
            invh_data.set_module(invh.module)
            invh_data.set_screen(invh.screen)
            invh_data.set_transactiondate(invh.transactiondate)
            invh_data.set_transactiontime(invh.transactiontime)
            invh_data.set_valuedate(invh.valuedate)
            invh_data.set_valuetime(invh.valuetime)
            invh_data.set_cbsdate(invh.cbsdate)
            invh_data.set_localcurrency(invh.localcurrency)
            invh_data.set_localexchangerate(invh.localexchangerate)
            invh_data.set_currency(invh.currency)
            invh_data.set_exchangerate(invh.exchangerate)
            invh_data.set_isprevyrentry(invh.isprevyrentry)
            invh_data.set_reversalentry(invh.reversalentry)
            invh_data.set_refno(invh.refno)
            invh_data.set_crno(invh.crno)
            invh_data.set_refid(invh.refid)
            invh_data.set_reftableid(invh.reftableid)
            invh_data.set_type(invh.type)
            invh_data.set_gl(invh.gl)
            invh_data.set_apcatno(invh.apcatno)
            invh_data.set_apsubcatno(invh.apsubcatno)
            invh_data.set_wisefinmap(invh.wisefinmap)
            invh_data.set_amount(invh.amount)
            invh_data.set_fcamount(invh.fcamount)
            invh_data.set_glremarks(invh.glremarks)
            invh_data.set_ackrefno(invh.ackrefno)
            response=invh_data
            logger.info("Get")

        except AssetEntry.DoesNotExist:
            logger.info('FAL_ENTRY_EXCEPT:{}'.format(traceback.print_exc()))
            response=invh_data

        return response
