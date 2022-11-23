import json
import traceback

from django.db import IntegrityError
from django.db.models import Q

from faservice.data.response.assetdebitresponse import AssetDebitResponse
from faservice.data.response.assetgroupresponse import AssetGroupResponse
from faservice.data.response.assetlocationresponse import AssetLocationResponse
from faservice.data.response.faauditresponse import FaAuditResponse
from faservice.models.famodels import AssetLocation, AssetDebit, AssetGroup, AssetCat
from faservice.service.faauditservice import FaAuditService
from faservice.util.fautil import FaModifyStatus, FaRefType, FaRequestStatusUtil
#from inwardservice.models import EscalationType
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from django.utils.timezone import now
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class AssetDebitService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
    def create_assetdebit(self, assetdebit_list, emp_id,doc_type,assetdebit_data):
        reqstatus = FaRequestStatusUtil.ONBORD

        try:
            assetdebit_array=list()
            start_id = int(AssetDebit.objects.latest('pk').pk)+1
            #test=AssetDebit()
            #test.active=True
            for assetdebit_obj in assetdebit_list:
                assetdebit_arr = AssetDebit(assetdetails_id=assetdebit_obj.get_assetdetails_id(),
                                            category_id=assetdebit_obj.get_category_id(),
                                            subcategory_id=assetdebit_obj.get_subcategory_id(),
                                            glno=assetdebit_obj.get_glno(),
                                            amount=assetdebit_obj.get_amount(),
                                            created_by=emp_id)
                assetdebit_array.append(assetdebit_arr)
            AssetDebit.objects.bulk_create(assetdebit_array)
            end_id = int(AssetDebit.objects.latest('pk').pk)+1

            assetdebit_array = NWisefinList()

            for i in range(start_id,end_id):
                assetdebit=AssetDebit.objects.get(pk=i)

                refid = ref_type = -1
                relrefid = assetdebit.id
                self.audit_function(assetdebit, refid, ref_type, relrefid,
                                        emp_id, FaModifyStatus.CREATE, reqstatus,FaRefType.ASSETDEBIT)

                assetdebit_resp = AssetDebitResponse()
                assetdebit_resp.set_id(assetdebit.id)
                assetdebit_resp.set_assetdetails_id(assetdebit.assetdetails_id)
                assetdebit_resp.set_category_id(assetdebit.category_id)
                assetdebit_resp.set_subcategory_id(assetdebit.subcategory_id)
                assetdebit_resp.set_glno(assetdebit.glno)
                assetdebit_resp.set_amount(assetdebit.amount)
                assetdebit_array.append(assetdebit_resp)

            assetgrp_resp=None
            #print(doc_type,type(doc_type))

            #assetgroup_maxnum = AssetGroup.objects.get(status=1)
            #print(assetgroup_maxnum.number, 'number')
            if doc_type == 'BUC':
                #AssetCat()
                #Apcategory
                assetgroup_maxnum = AssetGroup.objects.filter(status=1).values('number').order_by('-number')
                if len(assetgroup_maxnum) > 0:
                    assetgrp_maxnum = assetgroup_maxnum[0]['number']+1
                else:
                    assetgrp_maxnum = 1

                assetvalue=888
                branchg_id=1
                assetgroup = AssetGroup.objects.create(number=assetgrp_maxnum,
                                                    apcatategory = 1 , #it will update
                                                    apsubcatategory = 1 , #it will update
                                                    capdate = assetdebit_data['capdate'],
                                                    assetvalue = assetvalue,
                                                    branchg_id = branchg_id,
                                                    remarks = assetdebit_data['remarks'],
                                                    created_by=emp_id)

                assetgrp_resp=AssetGroupResponse()
                assetgrp_resp.set_id(assetgroup.id)
                assetgrp_resp.set_apcatategory(assetgroup.apcatategory)
                assetgrp_resp.set_apsubcatategory(assetgroup.apsubcatategory)
                assetgrp_resp.set_capdate(assetgroup.capdate)
                assetgrp_resp.set_assetvalue(assetgroup.assetvalue)
                assetgrp_resp.set_branchg_id(assetgroup.branchg_id)
                assetgrp_resp.set_remarks(assetgroup.remarks)


                refid = ref_type = -1
                relrefid = assetgroup.id
                self.audit_function(assetgroup, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.CREATE, reqstatus,FaRefType.ASSETGROUP)

        except IntegrityError as error:
            logger.info('FAL_ASSETDEBIT_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj
        except:
            logger.info('FAL_ASSETDEBIT_EXCEPT:{}'.format(traceback.print_exc()))

            error_obj = Error()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj

        return assetdebit_array,assetgrp_resp

    def audit_function(self, audit_data, refid,relreftype, relrefid, emp_id, action,reqstatus,reftype,request=None):
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
        audit_obj.set_relreftype(relreftype)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)