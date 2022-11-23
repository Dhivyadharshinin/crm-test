import ast
from django.db.models import Q,Max
from datetime import date

from validationservice.service.tpservice import TPResponse
from vendorservice.data.response.vendorauditresponse import VendorAuditResponse
from vendorservice.service.vendorauditservice import VendorAuditService
import pandas as pd
from vendorservice.data.response.modificationresponse import ModificationRelResponse
from vendorservice.data.response.directorresponse import DirectorResponse
from vendorservice.data.response.vendorlistresponse import VendorListData, VendorCheckListData
from vendorservice.models import Vendor, VendorContact, VendorDirector, VendorQueue, VendorGrpAnswers, VendorProfile, SupplierBranch, \
    SupplierTax, SupplierActivity, SupplierPayment, SupplierProduct, VendorKYC, VendorSubContractor, VendorDocument, \
    VendorClient, ActivityDetail, Catelog, VendorModificationRel, VendorRelAddress, VendorAddress, Codegenerator as Cgen, VendorRelContact
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError
from vendorservice.util.vendorutil import Questionnaire
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from vendorservice.util.vendorutil import getType, Validation_vendor_doc,VendorCompositeUtil
from userservice.service.employeeservice import EmployeeService
from userservice.models import Employee
from utilityservice.service.utilityservice import NWisefinUtilityService
from django.utils import timezone
from userservice.service.roleemployeeservice import RoleEmployeeService
from vendorservice.util.vendorutil import VendorRefType, getVendorRequestStatus
from masterservice.models.mastermodels import *
from vendorservice.data.response.subtaxresponse import SubTaxResponse
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from vendorservice.util.vendorutil import VendorStatusUtil, RequestStatusUtil, ModifyStatus, MainStatusUtil, Code_Gen_Type
from vendorservice.util import vendorutil


class VendorService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def create_vendor(self, vendorObj, vendor_json, user_id):
        req_status = RequestStatusUtil.ONBOARD
        vendorreftype = 1
        id = -1
        pan_status=self.pan_check(vendorObj)
        if pan_status == 'PANNO_EXISTS':
            return pan_status

        if not vendorObj.get_id() is None:
            # try:
            logger.info(str(vendorObj.get_group())+ ' group_test')
            vendor = Vendor.objects.using(self._current_app_schema()).filter(id=vendorObj.get_id(),entity_id=self._entity_id()).update(name=vendorObj.get_name(),
                                                                         panno=vendorObj.get_panno(),
                                                                         gstno=vendorObj.get_gstno(),
                                                                         adhaarno=vendorObj.get_adhaarno(),
                                                                         emaildays=vendorObj.get_emaildays(),
                                                                         # code=vendorObj.get_code(),
                                                                         composite=vendorObj.get_composite(),
                                                                         comregno=vendorObj.get_comregno(),
                                                                         group=vendorObj.get_group(),
                                                                         custcategory_id=vendorObj.get_custcategory_id(),
                                                                         classification=vendorObj.get_classification(),
                                                                         type=vendorObj.get_type(),
                                                                         website=vendorObj.get_website(),
                                                                         activecontract=vendorObj.get_activecontract(),
                                                                         nocontract_reason=vendorObj.get_nocontract_reason(),
                                                                         contractdate_from=vendorObj.get_contractdate_from(),
                                                                         contractdate_to=vendorObj.get_contractdate_to(),
                                                                         aproxspend=vendorObj.get_aproxspend(),
                                                                         actualspend=vendorObj.get_actualspend(),
                                                                         orgtype=vendorObj.get_orgtype(),
                                                                         renewal_date=vendorObj.get_renewal_date(),
                                                                         director_count=vendorObj.get_director_count(),
                                                                         remarks=vendorObj.get_remarks(),
                                                                         # requeststatus=vendorObj.get_requeststatus(), mainstatus=vendorObj.get_mainstatus(),
                                                                         rm_id=vendorObj.get_rm_id(),
                                                                         updated_by=user_id, updated_date=timezone.now(),
                                                                        description=vendorObj.get_description(),
                                                                        portal_flag=vendorObj.get_portal_flag()
                                                                        # risktype=vendorObj.get_risktype(),
                                                                        # risktype_description=vendorObj.get_risktype_description(),
                                                                        # risk_mitigant=vendorObj.get_risk_mitigant(),
                                                                        # risk_mitigant_review=vendorObj.get_risk_mitigant_review()
                                                                         )
            supplier_obj = SupplierBranch.objects.using(self._current_app_schema()).filter(vendor_id=vendorObj.get_id(), entity_id=self._entity_id()).update(
                panno=vendorObj.get_panno())
            vendor_auditdata = {'id': vendorObj.get_id(), 'name': vendorObj.get_name(), 'panno': vendorObj.get_panno(),
                                'gstno': vendorObj.get_gstno(),
                                'adhaarno': vendorObj.get_adhaarno(), 'emaildays': vendorObj.get_emaildays(),
                                # 'code' :vendorObj.get_code(),
                                'composite': vendorObj.get_composite(), 'comregno': vendorObj.get_comregno(),
                                'group': vendorObj.get_group(),
                                'custcategory_id': vendorObj.get_custcategory_id(),
                                'classification': vendorObj.get_classification(), 'type': vendorObj.get_type(),
                                'website': vendorObj.get_website(), 'activecontract': vendorObj.get_activecontract(),
                                'nocontract_reason': vendorObj.get_nocontract_reason(),
                                'contractdate_from': vendorObj.get_contractdate_from(),
                                'contractdate_to': vendorObj.get_contractdate_to(),
                                'aproxspend': vendorObj.get_aproxspend(), 'actualspend': vendorObj.get_actualspend(),
                                'orgtype': vendorObj.get_orgtype(),
                                'renewal_date': vendorObj.get_renewal_date(),
                                'director_count': vendorObj.get_director_count(), 'remarks': vendorObj.get_remarks(),
                                # requeststatus=vendorObj.get_requeststatus(), mainstatus=vendorObj.get_mainstatus(),'code' :vendorObj.get_code(),
                                'rm_id': vendorObj.get_rm_id(),
                                # vendor_status =vendorObj.get_vendor_status (),
                                'updated_by': user_id, 'updated_date': timezone.now(), 'description': vendorObj.get_description()
                                # 'risktype':vendorObj.get_risktype(), 'risktype_description':vendorObj.get_risktype_description(),
                                # 'risk_mitigant':vendorObj.get_risk_mitigant(), 'risk_mitigant_review':vendorObj.get_risk_mitigant_review()
                                }

            vendor = Vendor.objects.using(self._current_app_schema()).get(id=vendorObj.get_id(), entity_id=self._entity_id())
            self.audit_function(vendor_auditdata, vendor.id, user_id, req_status, id, ModifyStatus.update,
                                vendorreftype)

        # except IntegrityError as error:
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.INVALID_DATA)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
        #     return error_obj
        # except Vendor.DoesNotExist:
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.INVALID_VENDOR_ID)
        #     error_obj.set_description(ErrorDescription.INVALID_VENDOR_ID)
        #     return error_obj
        # except:
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
        #     return error_obj

        else:
            vendor = Vendor.objects.using(self._current_app_schema()).create(name=vendorObj.get_name(), panno=vendorObj.get_panno(),
                                           gstno=vendorObj.get_gstno(), adhaarno=vendorObj.get_adhaarno(),
                                           emaildays=vendorObj.get_emaildays(),
                                           composite=vendorObj.get_composite(),
                                           comregno=vendorObj.get_comregno(), group=vendorObj.get_group(),
                                           custcategory_id=vendorObj.get_custcategory_id(),
                                           classification=vendorObj.get_classification(), type=vendorObj.get_type(),
                                           website=vendorObj.get_website(),
                                           activecontract=vendorObj.get_activecontract(),
                                           nocontract_reason=vendorObj.get_nocontract_reason(),
                                           contractdate_from=vendorObj.get_contractdate_from(),
                                           contractdate_to=vendorObj.get_contractdate_to(),
                                           aproxspend=vendorObj.get_aproxspend(),
                                           actualspend=vendorObj.get_actualspend(), orgtype=vendorObj.get_orgtype(),
                                           renewal_date=vendorObj.get_renewal_date(),
                                           director_count=vendorObj.get_director_count(),
                                           remarks=vendorObj.get_remarks(),
                                           # requeststatus=vendorObj.get_requeststatus(),code=vendorObj.get_code(),
                                           # mainstatus=vendorObj.get_mainstatus(),
                                           rm_id=vendorObj.get_rm_id(),
                                           # vendor_status=vendorObj.get_vendor_status(),
                                           created_by=user_id, entity_id=self._entity_id(),
                                            description=vendorObj.get_description(),
                                            portal_flag=vendorObj.get_portal_flag()
                                            # risktype= vendorObj.get_risktype(),
                                            # risktype_description= vendorObj.get_risktype_description(),
                                            # risk_mitigant = vendorObj.get_risk_mitigant(),
                                            # risk_mitigant_review = vendorObj.get_risk_mitigant_review()
                                           )
            VendorQueue.objects.using(self._current_app_schema()).create(vendor_id_id=vendor.id, from_user_id=user_id, to_user_id=user_id,
                                       created_date=vendor.created_date,
                                       comments='Vendor in Draft state', is_sys=True, entity_id=self._entity_id()
                                       )
            vendor_code =self.codegenerator(Code_Gen_Type.vendor, user_id)

            code = "PA" + str(vendor_code)
            vendor.code = code
            vendor.save()
            self.audit_function(vendor, vendor.id, user_id, req_status, id, ModifyStatus.create, vendorreftype)

        vobj = VendorListData()
        vobj.set_panno(vendor.panno)
        vobj.set_id(vendor.id)
        vobj.set_name(vendor.name)
        vobj.set_gstno(vendor.gstno)
        vobj.set_adhaarno(vendor.adhaarno)
        vobj.set_emaildays(vendor.emaildays)
        vobj.set_director_count(vendor.director_count)
        vobj.set_composite(vendor.composite)
        vobj.set_code(vendor.code)
        vobj.set_comregno(vendor.comregno)
        vobj.set_group(vendor.group)
        vobj.set_custcategory_id(vendor.custcategory_id)
        vobj.set_classification(vendor.classification)
        vobj.set_type(vendor.type)
        vobj.set_website(vendor.website)
        vobj.set_activecontract(vendor.activecontract)
        vobj.set_nocontract_reason(vendor.nocontract_reason)
        vobj.set_contractdate_from(vendor.contractdate_from)
        vobj.set_contractdate_to(vendor.contractdate_to)
        vobj.set_aproxspend(vendor.aproxspend)
        vobj.set_actualspend(vendor.actualspend)
        vobj.set_orgtype(vendor.orgtype)
        vobj.set_renewal_date(vendor.renewal_date)
        vobj.set_comregno(vendor.remarks)
        vobj.set_remarks(vendor.group)
        vobj.set_requeststatus(vendor.requeststatus)
        vobj.set_mainstatus(vendor.mainstatus)
        vobj.set_rm_id(vendor.rm_id)
        vobj.set_modify_ref_id(vendor.modify_ref_id)
        vobj.set_vendor_status(vendor.vendor_status)
        vobj.set_description(vendor.description)
        vobj.set_portal_flag(vendor.portal_flag)
        # vobj.set_risktype(vendor.risktype)
        # vobj.set_risktype_description(vendor.risktype_description)
        # vobj.set_risk_mitigant(vendor.risk_mitigant)
        # vobj.set_risk_mitigant_review(vendor.risk_mitigant_review)
        employee_service = EmployeeService(self._scope())
        employee = Employee.objects.filter(id=vendor.rm_id)
        if len(employee) > 0:
            rmname = employee_service.get_employee(vendor.rm_id, user_id)
            vobj.rm_id = rmname
        else:
            rm_dict = dict()
            rm_dict['full_name'] = vendor.rm_id
            rm_dict['id'] = vendor.rm_id
            vobj.rm_id = rm_dict

        return vobj

    def create_director(self, directorobj, vendor_id, user_id):

        director = VendorDirector.objects.using(self._current_app_schema()).create(name=directorobj['name'], status=1, create_by=user_id,
                                                 vendor_id_id=vendor_id, entity_id=self._entity_id())
        req_status = RequestStatusUtil.ONBOARD
        vendorreftype = VendorRefType.VENDOR_DIRECTOR
        self.audit_function(director, vendor_id, user_id, req_status, director.id, ModifyStatus.create, vendorreftype)
        dobj = DirectorResponse()
        dobj.set_id(director.id)
        dobj.set_name(director.name)
        dobj.set_vendor_id(director.vendor_id_id)
        return dobj

    def fetch_data(self, vendor_id):
        vendor = Vendor.objects.using(self._current_app_schema()).filter(id=vendor_id,status=1, entity_id=self._entity_id()).values('code', 'name', 'contractdate_from', 'contractdate_to',
                                                            'requeststatus')
        requeststatus = getVendorRequestStatus(vendor[0]['requeststatus'])
        vdf = pd.DataFrame.from_records(vendor)
        logger.info(str(vendor[0]['requeststatus']))
        vdf['requeststatus'] = requeststatus
        vdf['requestfor'] = requeststatus
        vdf['contractdate_from'] = pd.to_datetime(vdf["contractdate_from"]).dt.strftime('%Y-%m-%d')
        vdf['contractdate_to'] = pd.to_datetime(vdf["contractdate_to"]).dt.strftime('%Y-%m-%d')
        vendor = vdf.to_dict('records')
        brancharray = list(SupplierBranch.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id,status=1, entity_id=self._entity_id()).values_list('id', flat=True))
        bdf = pd.DataFrame.from_records(
            SupplierBranch.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id,status=1, entity_id=self._entity_id()).values('code', 'name', 'limitdays', 'creditterms',
                                                                      'gstno', 'panno', 'address_id', 'contact_id','is_active'))
        bdf['gstapplicable'] = "Y"
        bdf.loc [ (bdf [ 'is_active' ] == 1) , 'is_active' ] = 'Y'
        bdf.loc [ (bdf [ 'is_active' ] == 0) , 'is_active' ] = 'N'
        bdf.rename ( columns={'is_active' : 'supplier_active'} , inplace=True )

        vendor[0]['SUPPLIER_BRANCH'] = bdf.to_dict('records')

        for i in range(len(brancharray)):
            activitylist = list (SupplierActivity.objects.using(self._current_app_schema()).filter ( branch_id=brancharray[i], status=1, entity_id=self._entity_id()).values_list ( 'id' , flat=True ) )
            for j in range(len(activitylist)):
                activity_detailslist = list (ActivityDetail.objects.using(self._current_app_schema()).filter ( activity_id=activitylist[j], status=1, entity_id=self._entity_id()).values_list ( 'id' , flat=True ) )
                for k in range ( len ( activity_detailslist ) ) :
                    product_data = Catelog.objects.using(self._current_app_schema()).filter(activitydetail_id=activity_detailslist[k],status=1, entity_id=self._entity_id()).values(
                'productname', 'unitprice',
                'direct_to', 'fromdate',
                'todate')

            if (len(product_data) == 0):
                Message = 'product_mapping_norecords'
                return Message
            p_df = pd.DataFrame.from_records(product_data)
            p_df.columns = ['product_gid', 'unitprice', 'dts', 'validfrom', 'validto']
            p_df.loc[(p_df['dts'] == True), 'dts'] = 'Y'
            p_df.loc[(p_df['dts'] == False), 'dts'] = 'N'
            p_df['validfrom'] = pd.to_datetime(p_df["validfrom"]).dt.strftime('%Y-%m-%d')
            p_df['validto'] = pd.to_datetime(p_df["validto"]).dt.strftime('%Y-%m-%d')
            p_df.loc[(p_df['validto'] == "NaT"), ['validfrom', 'validto']] = '0000-00-00'
            p_df["packingprice"] = "1"
            for index, j in p_df.iterrows():
                if (j['product_gid'] != 0):
                    p_df.loc[index, 'product_code'] = Product.objects.using(self._app_schema(ApplicationNamespace.MASTER_SERVICE)).filter(id=j['product_gid'],status=1, entity_id=self._entity_id()).values_list('code')[0]



            vendor[0]['SUPPLIER_BRANCH'][i]["product"] = p_df.to_dict('records')
            payment_data = list(
                SupplierPayment.objects.using(self._current_app_schema()).filter(supplierbranch_id=brancharray[i],status=1, entity_id=self._entity_id()).values('paymode_id', 'bank_id',
                                                                                        'branch_id', 'account_no',
                                                                                        'beneficiary','id','is_active'))
            Pay_df = pd.DataFrame.from_records(payment_data)

            Pay_df.loc[(pd.isnull(Pay_df['branch_id']) == True), 'branch_id'] = '0'
            Pay_df.loc[(pd.isnull(Pay_df['bank_id']) == True), 'bank_id'] = '0'
            Pay_df.loc[(Pay_df['bank_id'] == 0), ['bank_id', 'branch_id']] = '0'
            Pay_df.loc [ (Pay_df [ 'is_active' ] == 1) , 'is_active' ] = 'Y'
            Pay_df.loc [ (Pay_df [ 'is_active' ] == 0) , 'is_active'  ] = 'N'
            Pay_df.rename ( columns={'is_active' : 'payment_active'} , inplace=True )

            for index, j in Pay_df.iterrows():
                if (j['bank_id'] != '0'):
                    Pay_df.loc[index, 'bank_code'] = Bank.objects.using(self._app_schema(ApplicationNamespace.MASTER_SERVICE)).filter(id=j['bank_id'],status=1, entity_id=self._entity_id()).values_list('code')[0]
                else:
                    Pay_df.loc[index, 'bank_code']='0'

                if (j['branch_id'] != '0'):
                    Pay_df.loc[index, 'branch_ifsccode'] = BankBranch.objects.using(self._app_schema(ApplicationNamespace.MASTER_SERVICE)).filter(id=j['branch_id'],status=1, entity_id=self._entity_id()).values_list('ifsccode')[0]
                else:
                    Pay_df.loc[index, 'branch_ifsccode']='0'
                if (j['paymode_id'] != 0):
                    Pay_df.loc[index, 'paymode_code'] =  PayMode.objects.using(self._app_schema(ApplicationNamespace.MASTER_SERVICE)).filter(id=j['paymode_id'],status=1, entity_id=self._entity_id()).values_list('code')[0]

            vendor[0]['SUPPLIER_BRANCH'][i]['payment'] = Pay_df.to_dict('records')

        branch_data = Vendor.objects.using(self._current_app_schema()).select_related('suppliertax', 'suppliersubtax').filter(
            id=vendor_id, entity_id=self._entity_id()).values('suppliertax__suppliersubtax__excemrate', 'suppliertax__msme',
                                 'suppliertax__tax_id', 'code', 'suppliertax__suppliersubtax__excemfrom',
                                 'suppliertax__suppliersubtax__excemto',
                                 'suppliertax__suppliersubtax__rate_id',
                                 'suppliertax__suppliersubtax__excemthrosold',
                                 'suppliertax__suppliersubtax__isexcempted', 'suppliertax__subtax_id',
                                 'suppliertax__type')
        df = pd.DataFrame.from_records(branch_data)
        l = pd.isnull(df['suppliertax__tax_id'])
        if l[0] != True:

            df.columns = ['excemrate', 'msme', 'tax_id', 'branch_code', 'excemfrom', 'excemto', 'taxrate_id',
                          'excemthrosold', 'isexcempted', 'subtax_id', 'type']
            df['tds'] = "N"
            df['taxno'] = "EGVPS8320E"
            df['taxrate'] = 0
            for index, j in df.iterrows():
                if (j['taxrate_id'] != 0):
                    df.loc[index, 'taxrate_code'] = TaxRate.objects.using(self._app_schema(ApplicationNamespace.MASTER_SERVICE)).filter(id=j['taxrate_id'],status=1, entity_id=self._entity_id()).values_list('code')[0]
                if (j['subtax_id'] != 0):
                    df.loc[index, 'subtax_code'] = SubTax.objects.using(self._app_schema(ApplicationNamespace.MASTER_SERVICE)).filter(id=j['subtax_id'],status=1, entity_id=self._entity_id()).values_list('code')[0]
                if (j['tax_id'] != 0):
                    df.loc[index, 'tax_code'] = Tax.objects.using(self._app_schema(ApplicationNamespace.MASTER_SERVICE)).filter(id=j['tax_id'],status=1, entity_id=self._entity_id()).values_list('code')[0]
                else:
                    df.loc[index, 'tax_code']='0'



            df['excemfrom'] = pd.to_datetime(df["excemfrom"]).dt.strftime('%Y-%m-%d')
            df['excemto'] = pd.to_datetime(df["excemto"]).dt.strftime('%Y-%m-%d')
            # df.loc[(df['type'] == None), 'type'] = 'S'
            df.loc[(df['msme'] == True), 'msme'] = 'YES'
            df.loc[(df['msme'] == False), 'msme'] = 'NO'
            df.loc[(df['isexcempted'] == "N"), ['excemto', 'excemfrom']] = '0000-00-00'
            df.loc[(df['isexcempted'] == "N"), ['excemthrosold', 'excemrate']] = '0'
            df.loc[(pd.isnull(df['type']) == True), 'type'] = 'S'
            vendor[0]['SUPPLIER_TAX'] = df.to_dict('records')
        else:
            vendor[0]['SUPPLIER_TAX'] = []

        vendor = {"Params": vendor[0],
                  "Classification": {
                      "Create_By": 1,
                      "Update_By": 1,
                      "Entity_Gid": 1,
                      "Entity_Detail_Gid": "1"
                  }
                  }
        return vendor

    def get_vendor_list(self, request, query, vys_page, user_id):
        queue_arr = VendorQueue.objects.using(self._current_app_schema()).select_related('vendor__id').filter(
            (Q(from_user_id__exact=user_id) | Q(to_user_id__exact=user_id))&Q(entity_id=self._entity_id())).values('vendor_id').distinct()
        condition = None
        for vendor in queue_arr:
            logger.info(str(vendor))
            if condition is None:
                condition = Q(id__exact=vendor['vendor_id']) &Q(entity_id=self._entity_id())
            else:
                condition |= Q(id__exact=vendor['vendor_id']) &Q(entity_id=self._entity_id())
        if condition is not None:
            vendorList = Vendor.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        else:
            vendorList = []
        vlist = NWisefinList()
        user_list = []
        for vendor in vendorList:
            user_list.append(vendor.created_by)
        user_list = set(user_list)
        user_list = list(user_list)
        utility_service = NWisefinUtilityService()
        user_list_obj = utility_service.get_user_info(request, user_list)
        for vendor in vendorList:
            vobj = VendorListData()
            vobj.set_panno(vendor.panno)
            vobj.set_id(vendor.id)
            vobj.set_name(vendor.name)
            vobj.set_gstno(vendor.gstno)
            vobj.set_adhaarno(vendor.adhaarno)
            vobj.set_emaildays(vendor.emaildays)
            vobj.set_director_count(vendor.director_count)
            vobj.set_composite(vendor.composite)
            vobj.set_code(vendor.code)
            vobj.set_comregno(vendor.comregno)
            vobj.set_group(vendor.group)
            vobj.set_custcategory_id(vendor.custcategory_id)
            vobj.set_classification(vendor.classification)
            vobj.set_type(vendor.type)
            vobj.set_website(vendor.website)
            vobj.set_activecontract(vendor.activecontract)
            vobj.set_nocontract_reason(vendor.nocontract_reason)
            vobj.set_contractdate_from(vendor.contractdate_from)
            vobj.set_contractdate_to(vendor.contractdate_to)
            vobj.set_aproxspend(vendor.aproxspend)
            vobj.set_actualspend(vendor.actualspend)
            vobj.set_orgtype(vendor.orgtype)
            vobj.set_renewal_date(vendor.renewal_date)
            vobj.set_comregno(vendor.remarks)
            vobj.set_remarks(vendor.group)
            vobj.set_requeststatus(vendor.requeststatus)
            vobj.set_mainstatus(vendor.mainstatus)
            vobj.set_rm_id(vendor.rm_id)
            vobj.set_modify_ref_id(vendor.modify_ref_id)
            vobj.set_vendor_status(vendor.vendor_status)
            vobj.set_description(vendor.description)
            vobj.set_portal_flag(vendor.portal_flag)
            # vobj.set_risktype(vendor.risktype)
            # vobj.set_risktype_description(vendor.risktype_description)
            # vobj.set_risk_mitigant(vendor.risk_mitigant)
            # vobj.set_risk_mitigant_review(vendor.risk_mitigant_review)

            for ul in user_list_obj['data']:
                if ul['id'] == vendor.created_by:
                    vobj.set_created_by(ul)
            vlist.append(vobj)

        vpage = NWisefinPaginator(vendorList, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist

    def fetch_vendor(self, vendor_id, user_id):
        queue_obj = VendorQueue.objects.using(self._current_app_schema()).select_related('vendor__id').filter(((
                                                                                    Q(from_user_id__exact=user_id) | Q(
                                                                                to_user_id__exact=user_id)) & Q(
            vendor_id_id=vendor_id))&Q(entity_id=self._entity_id())).values('vendor_id').distinct()
        vendor = Vendor.objects.using(self._current_app_schema()).get(id=vendor_id, entity_id=self._entity_id())
        # logger.info(vendor_obj)
        vobj = VendorListData()

        vobj.set_panno(vendor.panno)
        vobj.set_id(vendor.id)
        vobj.set_name(vendor.name)
        vobj.set_gstno(vendor.gstno)
        vobj.set_adhaarno(vendor.adhaarno)
        vobj.set_emaildays(vendor.emaildays)
        vobj.set_director_count(vendor.director_count)
        vobj.set_composite(vendor.composite)
        vobj.set_code(vendor.code)
        vobj.set_comregno(vendor.comregno)
        vobj.set_group(vendor.group)
        vobj.set_custcategory_id(vendor.custcategory_id)
        vobj.set_classification(vendor.classification)
        vobj.set_type(vendor.type)
        vobj.set_website(vendor.website)
        vobj.set_activecontract(vendor.activecontract)
        vobj.set_nocontract_reason(vendor.nocontract_reason)
        vobj.set_contractdate_from(vendor.contractdate_from)
        vobj.set_contractdate_to(vendor.contractdate_to)
        vobj.set_aproxspend(vendor.aproxspend)
        vobj.set_actualspend(vendor.actualspend)
        vobj.set_orgtype(vendor.orgtype)
        vobj.set_renewal_date(vendor.renewal_date)
        vobj.set_remarks(vendor.remarks)
        vobj.set_requeststatus(vendor.requeststatus)
        vobj.set_mainstatus(vendor.mainstatus)

        vobj.set_rm_id(vendor.rm_id)
        vobj.set_vendor_status(vendor.vendor_status)
        vobj.set_modify_ref_id(vendor.modify_ref_id)
        vobj.set_modify_status(vendor.modify_status)
        vobj.set_created_by(vendor.created_by)
        vobj.set_description(vendor.description)
        vobj.set_portal_flag(vendor.portal_flag)
        # vobj.set_risktype(vendor.risktype)
        # vobj.set_risktype_description(vendor.risktype_description)
        # vobj.set_risk_mitigant(vendor.risk_mitigant)
        # vobj.set_risk_mitigant_review(vendor.risk_mitigant_review)
        if user_id == vendor.created_by:
            vobj.set_isowner(True)
        else:
            vobj.set_isowner(False)

        return vobj
    def fetch_vendor_code(self, vendor_code, user_id):
        vendor = Vendor.objects.using(self._current_app_schema()).get(code=vendor_code, entity_id=self._entity_id())
        # logger.info(vendor_obj)
        vobj = VendorListData()
        vobj.set_panno(vendor.panno)
        vobj.set_id(vendor.id)
        vobj.set_name(vendor.name)
        vobj.set_gstno(vendor.gstno)
        vobj.set_adhaarno(vendor.adhaarno)
        vobj.set_emaildays(vendor.emaildays)
        vobj.set_director_count(vendor.director_count)
        vobj.set_composite(vendor.composite)
        vobj.set_code(vendor.code)
        vobj.set_comregno(vendor.comregno)
        vobj.set_group(vendor.group)
        vobj.set_custcategory_id(vendor.custcategory_id)
        vobj.set_classification(vendor.classification)
        vobj.set_type(vendor.type)
        vobj.set_website(vendor.website)
        vobj.set_activecontract(vendor.activecontract)
        vobj.set_nocontract_reason(vendor.nocontract_reason)
        vobj.set_contractdate_from(vendor.contractdate_from)
        vobj.set_contractdate_to(vendor.contractdate_to)
        vobj.set_aproxspend(vendor.aproxspend)
        vobj.set_actualspend(vendor.actualspend)
        vobj.set_orgtype(vendor.orgtype)
        vobj.set_renewal_date(vendor.renewal_date)
        vobj.set_remarks(vendor.remarks)
        vobj.set_requeststatus(vendor.requeststatus)
        vobj.set_mainstatus(vendor.mainstatus)

        vobj.set_rm_id(vendor.rm_id)
        vobj.set_vendor_status(vendor.vendor_status)
        vobj.set_modify_ref_id(vendor.modify_ref_id)
        vobj.set_modify_status(vendor.modify_status)
        vobj.set_created_by(vendor.created_by)
        vobj.set_description(vendor.description)
        vobj.set_portal_flag(vendor.portal_flag)
        # vobj.set_risktype(vendor.risktype)
        # vobj.set_risktype_description(vendor.risktype_description)
        # vobj.set_risk_mitigant(vendor.risk_mitigant)
        # vobj.set_risk_mitigant_review(vendor.risk_mitigant_review)
        if user_id == vendor.created_by:
            vobj.set_isowner(True)
        else:
            vobj.set_isowner(False)

        return vobj

    def vow_fetch_vendor_code(self, vendor_code, user_id):
        vendor = Vendor.objects.using(self._current_app_schema()).get(code=vendor_code, entity_id=self._entity_id(),
                                                                      modify_status=-1)
        vobj = VendorListData()
        vobj.set_panno(vendor.panno)
        vobj.set_id(vendor.id)
        vobj.set_name(vendor.name)
        vobj.set_gstno(vendor.gstno)
        vobj.set_adhaarno(vendor.adhaarno)
        vobj.set_emaildays(vendor.emaildays)
        vobj.set_director_count(vendor.director_count)
        vobj.set_composite(vendor.composite)
        vobj.set_code(vendor.code)
        vobj.set_comregno(vendor.comregno)
        vobj.set_group(vendor.group)
        vobj.set_custcategory_id(vendor.custcategory_id)
        vobj.set_classification(vendor.classification)
        vobj.set_type(vendor.type)
        vobj.set_website(vendor.website)
        vobj.set_activecontract(vendor.activecontract)
        vobj.set_nocontract_reason(vendor.nocontract_reason)
        vobj.set_contractdate_from(vendor.contractdate_from)
        vobj.set_contractdate_to(vendor.contractdate_to)
        vobj.set_aproxspend(vendor.aproxspend)
        vobj.set_actualspend(vendor.actualspend)
        vobj.set_orgtype(vendor.orgtype)
        vobj.set_renewal_date(vendor.renewal_date)
        vobj.set_remarks(vendor.remarks)
        vobj.set_requeststatus(vendor.requeststatus)
        vobj.set_mainstatus(vendor.mainstatus)
        vobj.set_rm_id(vendor.rm_id)
        vobj.set_vendor_status(vendor.vendor_status)
        vobj.set_modify_ref_id(vendor.modify_ref_id)
        vobj.set_modify_status(vendor.modify_status)
        vobj.set_created_by(vendor.created_by)
        vobj.set_description(vendor.description)
        vobj.set_portal_flag(vendor.portal_flag)
        if user_id == vendor.created_by:
            vobj.set_isowner(True)
        else:
            vobj.set_isowner(False)

        return vobj

    def is_active(self, vendor_id):
        try:
            vendor_obj = Vendor.objects.using(self._current_app_schema()).filter(id=vendor_id, entity_id=self._entity_id())
            return vendor_obj.status
        except:
            return -1

    def get_director_count(self, vendor_id):
        status = self.is_active(vendor_id)
        if status:
            try:
                vendor_obj = Vendor.objects.using(self._current_app_schema()).filter(id=vendor_id, entity_id=self._entity_id())
                return vendor_obj.director_count
            except:
                return -1
        else:
            return -1

    def status_update(self, vendor_id, user_id, request_statusid, data):

        created_by_id = Vendor.objects.using(self._current_app_schema()).get(id=vendor_id, entity_id=self._entity_id())
        created_by_id = created_by_id.created_by
        logger.info(str(created_by_id))
        comments = data['comments']
        Vendor.objects.using(self._current_app_schema()).filter(id=vendor_id, entity_id=self._entity_id()).update(remarks=comments)
        to_user = data['assign_to']
        status = data['status']
        supplierprocess = data['supplierprocess']
        if status == 5:
            if request_statusid == 4:
                main_status = MainStatusUtil.DEACTIVATED
            if request_statusid == 6:
                main_status = MainStatusUtil.TERMINATED
            if request_statusid in (1, 2, 3, 5):
                main_status = MainStatusUtil.APPROVED

            vendor = Vendor.objects.using(self._current_app_schema()).filter(id=vendor_id, entity_id=self._entity_id()).update(vendor_status=status, mainstatus=main_status,updated_by=user_id,updated_date=now())
            vendor_auditdata = {'vendor_status': status, 'mainstatus': main_status}

        else:
            vendor = Vendor.objects.using(self._current_app_schema()).filter(id=vendor_id, entity_id=self._entity_id()).update(vendor_status=status)
            vendor_auditdata = {'vendor_status': status}
        if (status == 0):
            to_user = created_by_id

        if (status == 7):
            to_user = created_by_id

        if (to_user == None):
            to_user = created_by_id

        req_status = RequestStatusUtil.ONBOARD
        vendorreftype = 1
        id = -1
        self.audit_function(vendor_auditdata, vendor_id, user_id, req_status, vendor_id, ModifyStatus.update,
                            vendorreftype)

        # for user in to_user:
        # update_vendor = VendorQueue.objects.filter(
        #     # Q(from_user_id=user_id) & Q(vendor_id_id=vendor_id)).update(to_user_id=to_user, comments=comments)
        #     Q(vendor_id_id=vendor_id)).update(to_user_id=to_user, comments=comments)

        update_vendor = VendorQueue.objects.using(self._current_app_schema()).create(vendor_id_id=vendor_id, from_user_id=user_id, to_user_id=to_user,
                                                   created_date=timezone.now(),
                                                   comments=comments, is_sys=True, entity_id=self._entity_id()
                                                   )

        # logger.info(update_vendor)
        if update_vendor == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj

    def get_vendor_status(self, vendor_id):
        vendor = Vendor.objects.using(self._current_app_schema()).get(id=vendor_id, entity_id=self._entity_id())
        vobj = vendor.vendor_status

        return vobj

    def q_validation(self, vendor_id):
        vendor = Vendor.objects.using(self._current_app_schema()).get(id=vendor_id, entity_id=self._entity_id())
        arr = []
        ven_obj = VendorCheckListData()
        try:
            vendor_id = int(vendor_id)

            try:
                logger.info('q_validation vendor id' + '=' + str(vendor_id))
                branch = SupplierBranch.objects.using(self._current_app_schema()).filter(Q(vendor_id=vendor_id) & Q(modify_status=-1)&Q(entity_id=self._entity_id()))
                logger.info('supplier branch count' + '=' + str(len(branch)))
                if len(branch) == 0:
                    arr.append(False)
                    ven_obj.set_SupplierBranch(False)
                else:
                    branch_obj = branch[0]
                    branch_id = branch_obj.id
                    logger.info('debug supplier branch' + '=' + str(branch_id))
                    ven_obj.set_SupplierBranch(True)
                    arr.append(True)
            except:
                logger.info('suppelier branch exception')
                ven_obj.set_SupplierBranch(False)

            try:
                if vendor.composite == 2:
                    logger.info('suppalier composite tax branch id' + '=' + str(branch_id))
                    tax = SupplierTax.objects.using(self._current_app_schema()).filter(branch_id=branch_id, entity_id=self._entity_id())
                    logger.info('composite supplier tax count' + '=' + str(len(tax)))
                    if len(tax) == 0:
                        ven_obj.set_SupplierTax(False)
                        arr.append(False)
                    else:
                        tax_obj = tax[0]
                        tax_id = tax_obj.id
                        ven_obj.set_SupplierTax(True)
                        arr.append(True)
                else:
                    logger.info('un regsister suppalier tax branch id' + '=' + str(branch_id))
                    tax = SupplierTax.objects.using(self._current_app_schema()).filter(branch_id=branch_id, entity_id=self._entity_id())
                    logger.info('un register supplier tax count' + '=' + str(len(tax)))
                    if len(tax) != 0:
                        ven_obj.set_SupplierTax(True)
                    else:
                        ven_obj.set_SupplierTax(False)
            except:
                logger.info('suppelier tax exception')
                ven_obj.set_SupplierTax(False)
            try:
                logger.info('suppalier payment branch id' + '=' + str(branch_id))
                payment = SupplierPayment.objects.using(self._current_app_schema()).filter(supplierbranch_id=branch_id, entity_id=self._entity_id())
                logger.info(' supplier payment count' + '=' + str(len(payment)))
                if len(payment) == 0:
                    ven_obj.set_SupplierPayment(False)
                    arr.append(False)
                else:
                    payment_obj = payment[0]
                    payment_id = payment_obj.id
                    ven_obj.set_SupplierPayment(True)
                    arr.append(True)
            except:
                logger.info('suppelier payment exception')
                ven_obj.set_SupplierPayment(False)
            try:
                logger.info('suppalier activity branch id' + '=' + str(branch_id))
                activity = SupplierActivity.objects.using(self._current_app_schema()).filter(Q(branch_id=branch_id) & Q(modify_status=-1)&Q(entity_id=self._entity_id()))
                logger.info(' supplier activity count' + '=' + str(len(activity)))
                if len(activity) == 0:
                    ven_obj.set_SupplierActivity(False)
                    arr.append(False)
                else:
                    activity_obj = activity[0]
                    activity_id = activity_obj.id
                    ven_obj.set_SupplierActivity(True)
                    arr.append(True)
            except:
                logger.info('suppelier activity exception')
                ven_obj.set_SupplierActivity(False)
            try:
                logger.info('suppalier activity details activity id' + '=' + str(activity_id))
                activitydetail = ActivityDetail.objects.using(self._current_app_schema()).filter(Q(activity_id=activity_id) & Q(modify_status=-1)&Q(entity_id=self._entity_id()))
                logger.info(' supplier activity count' + '=' + str(len(activitydetail)))
                if len(activitydetail) == 0:
                    ven_obj.set_ActivityDetail(False)
                    arr.append(False)
                else:
                    activitydetail_obj = activitydetail[0]
                    activitydetail_id = activitydetail_obj.id
                    ven_obj.set_ActivityDetail(True)
                    arr.append(True)
            except:
                logger.info('suppelier activity details exception')
                ven_obj.set_ActivityDetail(False)
            try:
                logger.info('catelog activity details id' + '=' + str(activitydetail_id))
                catalog = Catelog.objects.using(self._current_app_schema()).filter(activitydetail_id=activitydetail_id, entity_id=self._entity_id())
                logger.info(' supplier activity count' + '=' + str(len(catalog)))
                if len(catalog) == 0:
                    ven_obj.set_Catelog(False)
                    arr.append(False)
                else:
                    catalog_obj = catalog[0]
                    catalog_id = catalog_obj.id
                    ven_obj.set_Catelog(True)
                    arr.append(True)
            except:
                logger.info('catelog exception')
                ven_obj.set_Catelog(False)
            try:
                contract = VendorSubContractor.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id, entity_id=self._entity_id())
                if len(contract) == 0:
                    ven_obj.set_VendorSubContractor(False)
                    arr.append(False)
                else:
                    contract_obj = contract[0]
                    contract_id = contract_obj.id
                    ven_obj.set_VendorSubContractor(True)
                    arr.append(True)
            except:
                ven_obj.set_VendorSubContractor(False)
            try:
                client = VendorClient.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id, entity_id=self._entity_id())
                if len(client) == 0:
                    ven_obj.set_VendorClient(False)
                    arr.append(False)
                else:
                    client_obj = client[0]
                    client_id = client_obj.id
                    ven_obj.set_VendorClient(True)
                    arr.append(True)
            except:
                ven_obj.set_VendorClient(False)

            try:
                product = SupplierProduct.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id, entity_id=self._entity_id())
                if len(product) == 0:
                    ven_obj.set_SupplierProduct(False)
                    arr.append(False)
                else:
                    product_obj = product[0]
                    product_id = product_obj.id
                    ven_obj.set_SupplierProduct(True)
                    arr.append(True)
            except:
                ven_obj.set_SupplierProduct(False)
            try:
                document = VendorDocument.objects.using(self._current_app_schema()).filter(partner_id=vendor_id, entity_id=self._entity_id())
                if len(document) == 0:
                    ven_obj.set_VendorDocument(False)
                    arr.append(False)
                else:
                    document_obj = document[0]
                    document_id = document_obj.id
                    ven_obj.set_VendorDocument(True)
                    arr.append(True)
            except:
                ven_obj.set_VendorDocument(False)
            logger.info(str(arr))
            ven_obj.set_status(1)
            for i in arr:
                if (i == False):
                    ven_obj.set_status(0)
                    logger.info(str(i))


        except:
            ven_obj.set_status(0)

        return ven_obj

    def get_rmdata(self, modify_refid):
        vendor1 = Vendor.objects.using(self._current_app_schema()).filter(id=modify_refid, entity_id=self._entity_id()).values('rm_id')
        logger.info(str(vendor1[0]['rm_id']))
        re = Vendor.objects.using(self._current_app_schema()).filter(modify_ref_id=modify_refid, entity_id=self._entity_id()).update(rm_id=vendor1[0]['rm_id'])
        return re

    # modification
    def create_vendor_modification(self, vendorObj, vendor_json, user_id):
        pan_status = self.pan_check(vendorObj)
        if pan_status == 'PANNO_EXISTS':
            return pan_status
        if not vendorObj.get_id() is None:
            vendor1 = Vendor.objects.using(self._current_app_schema()).get(id=vendorObj.get_id(), entity_id=self._entity_id())
            # try:
            ref_flag = self.checkmodify_rel(VendorRefType.VENDOR, vendorObj.get_id())
            if ref_flag == True:
                vendor = Vendor.objects.using(self._current_app_schema()).filter(id=vendorObj.get_id(), entity_id=self._entity_id()).update(name=vendorObj.get_name(),
                                                                             panno=vendorObj.get_panno(),
                                                                             gstno=vendorObj.get_gstno(),
                                                                             adhaarno=vendorObj.get_adhaarno(),
                                                                             emaildays=vendorObj.get_emaildays(),
                                                                             director_count=vendorObj.get_director_count(),
                                                                             composite=vendorObj.get_composite(),
                                                                             code=vendor1.code,
                                                                             comregno=vendorObj.get_comregno(),
                                                                             group=vendorObj.get_group(),
                                                                             custcategory_id=vendorObj.get_custcategory_id(),
                                                                             classification=vendorObj.get_classification(),
                                                                             type=vendorObj.get_type(),
                                                                             website=vendorObj.get_website(),

                                                                             activecontract=vendorObj.get_activecontract(),
                                                                             nocontract_reason=vendorObj.get_nocontract_reason(),
                                                                             contractdate_from=vendorObj.get_contractdate_from(),
                                                                             contractdate_to=vendorObj.get_contractdate_to(),
                                                                             aproxspend=vendorObj.get_aproxspend(),
                                                                             actualspend=vendorObj.get_actualspend(),
                                                                             orgtype=vendorObj.get_orgtype(),
                                                                             renewal_date=vendorObj.get_renewal_date(),

                                                                             remarks=vendorObj.get_remarks(),
                                                                             rm_id=vendorObj.get_rm_id(),
                                                                            description=vendorObj.get_description(),
                                                                            portal_flag=vendorObj.get_portal_flag()
                                                                            # risktype=vendorObj.get_risktype(),
                                                                            # risktype_description=vendorObj.get_risktype_description(),
                                                                            # risk_mitigant=vendorObj.get_risk_mitigant(),
                                                                            # risk_mitigant_review=vendorObj.get_risk_mitigant_review()
                                                                                                                    )
                # supplier_obj = SupplierBranch.objects.using(self._current_app_schema()).filter(vendor_id=vendorObj.get_id(), entity_id=self._entity_id()).update(
                #     panno=vendorObj.get_panno())
                vendor = Vendor.objects.using(self._current_app_schema()).get(id=vendorObj.get_id(), entity_id=self._entity_id())

            else:

                vendor = Vendor.objects.using(self._current_app_schema()).create(name=vendorObj.get_name(), panno=vendorObj.get_panno(),
                                               gstno=vendorObj.get_gstno(), adhaarno=vendorObj.get_adhaarno(),
                                               emaildays=vendorObj.get_emaildays(),
                                               composite=vendorObj.get_composite(), code=vendor1.code,
                                               comregno=vendorObj.get_comregno(), group=vendorObj.get_group(),
                                               custcategory_id=vendorObj.get_custcategory_id(),
                                               classification=vendorObj.get_classification(), type=vendorObj.get_type(),
                                               website=vendorObj.get_website(),
                                               activecontract=vendorObj.get_activecontract(),
                                               nocontract_reason=vendorObj.get_nocontract_reason(),
                                               contractdate_from=vendorObj.get_contractdate_from(),
                                               contractdate_to=vendorObj.get_contractdate_to(),
                                               aproxspend=vendorObj.get_aproxspend(),
                                               actualspend=vendorObj.get_actualspend(), orgtype=vendorObj.get_orgtype(),
                                               renewal_date=vendorObj.get_renewal_date(),
                                               director_count=vendorObj.get_director_count(),
                                               remarks=vendorObj.get_remarks(),
                                               requeststatus=vendor1.requeststatus,
                                               mainstatus=vendor1.mainstatus,
                                               modify_ref_id=vendorObj.get_id(),
                                               rm_id=vendorObj.get_rm_id(),
                                               modify_status=1,
                                               created_by=user_id, entity_id=self._entity_id(),
                                                description=vendorObj.get_description(),
                                                portal_flag=vendorObj.get_portal_flag()
                                                # risktype=vendorObj.get_risktype(),
                                                # risktype_description=vendorObj.get_risktype_description(),
                                                # risk_mitigant=vendorObj.get_risk_mitigant(),
                                                # risk_mitigant_review=vendorObj.get_risk_mitigant_review()

                                               )
                # supplier_obj = SupplierBranch.objects.using(self._current_app_schema()).filter(vendor_id=vendorObj.get_id(), entity_id=self._entity_id()).update(panno=vendorObj.get_panno())
                vendor_update = Vendor.objects.using(self._current_app_schema()).filter(id=vendorObj.get_id()).update(modify_ref_id=vendor.id,
                                                                                    modified_by=user_id)

                VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendorObj.get_id(), ref_id=vendorObj.get_id(),
                                                     ref_type=VendorRefType.VENDOR, mod_status=ModifyStatus.update,
                                                     modify_ref_id=vendor.id, entity_id=self._entity_id())
        else:
            vendor = Vendor.objects.using(self._current_app_schema()).create(name=vendorObj.get_name(), panno=vendorObj.get_panno(),
                                           gstno=vendorObj.get_gstno(), adhaarno=vendorObj.get_adhaarno(),
                                           emaildays=vendorObj.get_emaildays(),
                                           composite=vendorObj.get_composite(),
                                           comregno=vendorObj.get_comregno(), group=vendorObj.get_group(),
                                           custcategory_id=vendorObj.get_custcategory_id(),
                                           classification=vendorObj.get_classification(), type=vendorObj.get_type(),
                                           website=vendorObj.get_website(),
                                           activecontract=vendorObj.get_activecontract(),
                                           nocontract_reason=vendorObj.get_nocontract_reason(),
                                           contractdate_from=vendorObj.get_contractdate_from(),
                                           contractdate_to=vendorObj.get_contractdate_to(),
                                           aproxspend=vendorObj.get_aproxspend(),
                                           actualspend=vendorObj.get_actualspend(), orgtype=vendorObj.get_orgtype(),
                                           renewal_date=vendorObj.get_renewal_date(),
                                           director_count=vendorObj.get_director_count(),
                                           remarks=vendorObj.get_remarks(),
                                           requeststatus=2,
                                           mainstatus=1,

                                           rm_id=vendorObj.get_rm_id(),
                                           modify_status=1,
                                           created_by=user_id, entity_id=self._entity_id(),
                                            description=vendorObj.get_description(),
                                            portal_flag=vendorObj.get_portal_flag()
                                            # risktype=vendorObj.get_risktype(),
                                            # risktype_description=vendorObj.get_risktype_description(),
                                            # risk_mitigant=vendorObj.get_risk_mitigant(),
                                            # risk_mitigant_review=vendorObj.get_risk_mitigant_review()
                                           )
            vendor_code = self.codegenerator(Code_Gen_Type.vendor, user_id)
            code = "PA" + str(vendor_code)
            vendor.code = code
            vendor.save()
            vendor_update = Vendor.objects.using(self._current_app_schema()).filter(id=vendor.id, entity_id=self._entity_id()).update(modify_ref_id=vendor.id,
                                                                       modified_by=user_id)

            VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor.id, ref_id=vendor.id,
                                                 ref_type=VendorRefType.VENDOR, mod_status=ModifyStatus.create,
                                                 modify_ref_id=vendor.id, entity_id=self._entity_id())

        vobj = VendorListData()
        vobj.set_panno(vendor.panno)
        vobj.set_id(vendor.id)
        vobj.set_name(vendor.name)
        vobj.set_gstno(vendor.gstno)
        vobj.set_adhaarno(vendor.adhaarno)
        vobj.set_emaildays(vendor.emaildays)
        vobj.set_director_count(vendor.director_count)
        vobj.set_composite(vendor.composite)
        vobj.set_code(vendor.code)
        vobj.set_comregno(vendor.comregno)
        vobj.set_group(vendor.group)
        vobj.set_custcategory_id(vendor.custcategory_id)
        vobj.set_classification(vendor.classification)
        vobj.set_type(vendor.type)
        vobj.set_website(vendor.website)
        vobj.set_activecontract(vendor.activecontract)
        vobj.set_nocontract_reason(vendor.nocontract_reason)
        vobj.set_contractdate_from(vendor.contractdate_from)
        vobj.set_contractdate_to(vendor.contractdate_to)
        vobj.set_aproxspend(vendor.aproxspend)
        vobj.set_actualspend(vendor.actualspend)
        vobj.set_orgtype(vendor.orgtype)
        vobj.set_renewal_date(vendor.renewal_date)
        vobj.set_comregno(vendor.remarks)
        vobj.set_remarks(vendor.group)
        vobj.set_requeststatus(vendor.requeststatus)
        vobj.set_mainstatus(vendor.mainstatus)
        vobj.set_rm_id(vendor.rm_id)
        vobj.set_modify_ref_id(vendor.modify_ref_id)
        vobj.set_vendor_status(vendor.vendor_status)
        vobj.set_description(vendor.description)
        vobj.set_portal_flag(vendor.portal_flag)
        # vobj.set_risktype(vendor.risktype)
        # vobj.set_risktype_description(vendor.risktype_description)
        # vobj.set_risk_mitigant(vendor.risk_mitigant)
        # vobj.set_risk_mitigant_review(vendor.risk_mitigant_review)

        return vobj

    def modification_serviceview(self, vendor_id):
        vlist = NWisefinList()
        vendor_modify = VendorModificationRel.objects.using(self._current_app_schema()).filter(Q(vendor_id=vendor_id) & Q(is_flag=True)&Q(entity_id=self._entity_id())).order_by(
            '-created_date')
        logger.info(str(vendor_modify.query))
        logger.info('GETDATA' + '=' + str(len(vendor_modify)))
        for vendor in vendor_modify:
            vobj = ModificationRelResponse()
            vobj.set_vendor_id(vendor.vendor_id)
            vobj.set_ref_id(vendor.ref_id)
            vobj.set_id(vendor.id)
            vobj.set_ref_type(vendor.ref_type)
            vobj.set_mod_status(vendor.mod_status)
            vobj.set_modify_ref_id(vendor.modify_ref_id)
            vlist.append(vobj)

        return vlist

    def modificationapprove_serviceview(self, vendor_id):
        vlist = NWisefinList()
        vendor_modify = VendorModificationRel.objects.using(self._current_app_schema()).filter(Q(vendor_id=vendor_id) & Q(is_flag=True)&Q(entity_id=self._entity_id())).order_by(
            '-created_date')
        logger.info(str(vendor_modify.query))
        logger.info('GETDATA' + '=' + str(len(vendor_modify)))
        for vendor in vendor_modify:
            vobj = ModificationRelResponse()
            vobj.set_vendor_id(vendor.vendor_id)
            vobj.set_ref_id(vendor.ref_id)
            vobj.set_id(vendor.id)
            vobj.set_ref_type(vendor.ref_type)
            vobj.set_mod_status(vendor.mod_status)
            vobj.set_modify_ref_id(vendor.modify_ref_id)
            vlist.append(vobj)

        vendor_obj = Vendor.objects.using(self._current_app_schema()).get(id=vendor_id)
        vendor_modifyid = VendorModificationRel.objects.using(self._current_app_schema()).filter(vendor_id=vendor_obj.modify_ref_id, entity_id=self._entity_id()).order_by(
            '-created_date')
        for vendor in vendor_modifyid:
            vobj = ModificationRelResponse()
            vobj.set_vendor_id(vendor.vendor_id)
            vobj.set_ref_id(vendor.ref_id)
            vobj.set_id(vendor.id)
            vobj.set_ref_type(vendor.ref_type)
            vobj.set_mod_status(vendor.mod_status)
            vobj.set_modify_ref_id(vendor.modify_ref_id)
            vlist.append(vobj)

        return vlist

    def modification_action_vendor(self, mod_status, old_id, new_id, user_id):
        if mod_status == 2:
            vendorObj = self.fetch_vendor(new_id, user_id)
            if vendorObj.get_contractdate_from() == str(None):
                from_date = None
            else:
                from_date = vendorObj.get_contractdate_from()
            if vendorObj.get_contractdate_to() == str(None):
                to_date = None
            else:
                to_date = vendorObj.get_contractdate_to()
            if vendorObj.get_renewal_date() == str(None):
                renewal_date = None
            else:
                renewal_date = vendorObj.get_renewal_date()
            vendor = Vendor.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(name=vendorObj.get_name(),
                                                             panno=vendorObj.get_panno(),
                                                             gstno=vendorObj.get_gstno(),
                                                             adhaarno=vendorObj.get_adhaarno(),
                                                             emaildays=vendorObj.get_emaildays(),
                                                             composite=vendorObj.get_composite(),
                                                             code=vendorObj.get_code(),
                                                             comregno=vendorObj.get_comregno(),
                                                             group=vendorObj.get_group(),
                                                             custcategory_id=vendorObj.get_custcategory_id(),
                                                             classification=vendorObj.get_classification(),
                                                             type=vendorObj.get_type(),
                                                             website=vendorObj.get_website(),
                                                             activecontract=vendorObj.get_activecontract(),
                                                             nocontract_reason=vendorObj.get_nocontract_reason(),
                                                             contractdate_from=from_date,
                                                             contractdate_to=to_date,
                                                             aproxspend=vendorObj.get_aproxspend(),
                                                             actualspend=vendorObj.get_actualspend(),
                                                             orgtype=vendorObj.get_orgtype(),
                                                             renewal_date=renewal_date,
                                                             director_count=vendorObj.get_director_count(),
                                                             remarks=vendorObj.get_remarks(),
                                                             # requeststatus=vendorObj.get_requeststatus(), mainstatus=vendorObj.get_mainstatus(),
                                                             rm_id=vendorObj.get_rm_id(),
                                                             # vendor_status =vendorObj.get_vendor_status (),
                                                             modify_status=-1, modified_by=-1,
                                                             modify_ref_id=-1,
                                                            description=vendorObj.get_description(),
                                                            portal_flag=vendorObj.get_portal_flag()
                                                            # risktype=vendorObj.get_risktype(),
                                                            # risktype_description=vendorObj.get_risktype_description(),
                                                            # risk_mitigant=vendorObj.get_risk_mitigant(),
                                                            # risk_mitigant_review=vendorObj.get_risk_mitigant_review()
                                                             )

            supplier_obj = SupplierBranch.objects.using(self._current_app_schema()).filter(vendor_id=old_id, entity_id=self._entity_id()).update(
                panno=vendorObj.get_panno())
            req_status = RequestStatusUtil.MODIFICATION
            vendorreftype = -1
            id = -1
            self.audit_function(vendor, old_id, user_id, req_status, id, ModifyStatus.update, vendorreftype)
            # self.audit_function(vendor_delete, new_id, user_id, req_status, id, ModifyStatus.delete, vendorreftype)

        if mod_status == 1:
            vendor_obj = Vendor.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).update(modify_status=-1, modified_by=-1,
                                                                 modify_ref_id=-1)

        if mod_status == 0:
            vendor_obj = Vendor.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).delete()
        return

    def get_modification_status(self, vendor_id):
        if vendor_id == None:
            mod_status = False
        else:
            vendor = Vendor.objects.using(self._current_app_schema()).get(id=vendor_id, entity_id=self._entity_id())
            if vendor.requeststatus in (RequestStatusUtil.MODIFICATION, RequestStatusUtil.RENEWAL):
                mod_status = True
            else:
                mod_status = False
        return mod_status

    def get_modification_data(self, request, query, vys_page, supplierprocess, user_id):
        if supplierprocess == '1':
            vendorList = Vendor.objects.using(self._current_app_schema()).filter(
                (Q(vendor_status=VendorStatusUtil.APPROVED) & Q(mainstatus=MainStatusUtil.APPROVED))&Q(entity_id=self._entity_id())).order_by(
                '-created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        elif supplierprocess == '2':
            vendorList = Vendor.objects.using(self._current_app_schema()).filter(Q(requeststatus=RequestStatusUtil.MODIFICATION) & ~Q(modify_status=-1)
                                                                                 & Q(entity_id=self._entity_id())).values('code').annotate(id=Max('id')).values_list('id',flat=True)
            id_list = list(vendorList)
            vendorList = Vendor.objects.using(self._current_app_schema()).filter(id__in=id_list).order_by('-created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        elif supplierprocess == '3':
            vendorList = Vendor.objects.using(self._current_app_schema()).filter(
                (Q(requeststatus=RequestStatusUtil.ACTIVATION))&Q(entity_id=self._entity_id())).order_by('-created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]

        elif supplierprocess == '4':
            vendorList = Vendor.objects.using(self._current_app_schema()).filter(
                (Q(requeststatus=RequestStatusUtil.DEACTIVATION))&Q(entity_id=self._entity_id())).order_by('-created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        elif supplierprocess == '5':
            vendorList = Vendor.objects.using(self._current_app_schema()).filter(
                (Q(requeststatus=RequestStatusUtil.RENEWAL))&Q(entity_id=self._entity_id())).order_by('-created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        elif supplierprocess == '6':
            vendorList = Vendor.objects.using(self._current_app_schema()).filter(
                (Q(requeststatus=RequestStatusUtil.TERMINATION))&Q(entity_id=self._entity_id())).order_by('-created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        elif supplierprocess == '8':
            vendorList = Vendor.objects.using(self._current_app_schema()).filter(
                (Q(vendor_status=VendorStatusUtil.PENDING_RM) | Q(vendor_status=VendorStatusUtil.PENDING_CHECKER) | Q(
                    vendor_status=VendorStatusUtil.PENDING_HEADER))&Q(entity_id=self._entity_id())).order_by('-created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]

        emp_list = []
        vlist = NWisefinList()
        for vendor in vendorList:
            emp_list.append(vendor.created_by)
        emp_list = set(emp_list)
        emp_list = list(emp_list)
        utility_service = NWisefinUtilityService()
        user_list_obj = utility_service.get_emp_info_by_id(request, emp_list)

        for vendor in vendorList:
            vobj = VendorListData()
            vobj.set_panno(vendor.panno)
            vobj.set_id(vendor.id)
            vobj.set_name(vendor.name)
            vobj.set_gstno(vendor.gstno)
            vobj.set_adhaarno(vendor.adhaarno)
            vobj.set_emaildays(vendor.emaildays)
            vobj.set_director_count(vendor.director_count)
            vobj.set_composite(vendor.composite)
            vobj.set_code(vendor.code)
            vobj.set_comregno(vendor.comregno)
            vobj.set_group(vendor.group)
            vobj.set_custcategory_id(vendor.custcategory_id)
            vobj.set_classification(vendor.classification)
            vobj.set_type(vendor.type)
            vobj.set_website(vendor.website)
            vobj.set_activecontract(vendor.activecontract)
            vobj.set_nocontract_reason(vendor.nocontract_reason)
            vobj.set_contractdate_from(vendor.contractdate_from)
            vobj.set_contractdate_to(vendor.contractdate_to)
            vobj.set_aproxspend(vendor.aproxspend)
            vobj.set_actualspend(vendor.actualspend)
            vobj.set_orgtype(vendor.orgtype)
            vobj.set_renewal_date(vendor.renewal_date)
            vobj.set_comregno(vendor.remarks)
            vobj.set_remarks(vendor.group)
            vobj.set_requeststatus(vendor.requeststatus)
            vobj.set_mainstatus(vendor.mainstatus)
            vobj.set_rm_id(vendor.rm_id)
            vobj.set_modify_ref_id(vendor.modify_ref_id)
            vobj.set_vendor_status(vendor.vendor_status)
            vobj.set_description(vendor.description)
            vobj.set_portal_flag(vendor.portal_flag)
            # vobj.set_risktype(vendor.risktype)
            # vobj.set_risktype_description(vendor.risktype_description)
            # vobj.set_risk_mitigant(vendor.risk_mitigant)
            # vobj.set_risk_mitigant_review(vendor.risk_mitigant_review)
            employee_service = EmployeeService(self._scope())
            rm_id = vobj.rm_id
            rmname = employee_service.get_employee(rm_id, user_id)
            vobj.rm_id = rmname
            type_id = vobj.type
            type = getType(type_id)
            vobj.type = type

            for ul in user_list_obj['data']:
                if ul['id'] == vendor.created_by:
                    vobj.set_created_by(ul)
            vlist.append(vobj)
        vpage = NWisefinPaginator(vendorList, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist

    def modificationstatus_update(self, vendor_id, supplierprocess, user_id):
        try:
            if supplierprocess in ('1', '3', '5'):
                if (supplierprocess == '1'):
                    request_status = RequestStatusUtil.DEACTIVATION
                if (supplierprocess == '3'):
                    request_status = RequestStatusUtil.ACTIVATION
                if (supplierprocess == '5'):
                    request_status = RequestStatusUtil.TERMINATION
                vendorList = Vendor.objects.using(self._current_app_schema()).filter(id=vendor_id, entity_id=self._entity_id()).update(vendor_status=VendorStatusUtil.PENDING_RM,
                                                                        requeststatus=request_status,updated_by=user_id,updated_date=now())
                vendor_modifyauditdata = {'id': vendor_id, 'vendor_status': VendorStatusUtil.PENDING_RM,
                                          'requeststatus': request_status}
            else:
                if (supplierprocess == '2'):
                    request_status = RequestStatusUtil.MODIFICATION
                if (supplierprocess == '4'):
                    request_status = RequestStatusUtil.RENEWAL
                vendorList = Vendor.objects.using(self._current_app_schema()).filter(id=vendor_id, entity_id=self._entity_id()).update(vendor_status=VendorStatusUtil.DRAFT,
                                                                        requeststatus=request_status,updated_by=user_id,updated_date=now())
                vendor_modifyauditdata = {'id': vendor_id, 'vendor_status': VendorStatusUtil.DRAFT,
                                          'requeststatus': request_status}
            req_status = RequestStatusUtil.MODIFICATION
            vendorreftype = 1
            id = -1
            logger.info('STATUS CATED')
            self.audit_function(vendor_modifyauditdata, vendor_id, user_id, req_status, vendor_id, ModifyStatus.update,
                                vendorreftype)

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj

        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj

    def modification_reject_vendor(self, mod_status, old_id, new_id, user_id):
        if mod_status == ModifyStatus.update:
            vendor_delete = Vendor.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()
            vendor = Vendor.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(modify_ref_id=-1)
            req_status = RequestStatusUtil.MODIFICATION
            vendorreftype = -1
            id = -1
            self.audit_function(vendor_delete, new_id, user_id, req_status, id, ModifyStatus.delete, vendorreftype)
            self.audit_function(vendor, old_id, user_id, req_status, id, ModifyStatus.update, vendorreftype)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj

    def modification_approve_status(self, vendor_id, request_sts, user_id, data):
        comments = data['comments']
        if request_sts == 2:
            vendor = Vendor.objects.using(self._current_app_schema()).filter(id=vendor_id, entity_id=self._entity_id()).update(vendor_status=VendorStatusUtil.APPROVED,
                                                                remarks=comments,updated_by=user_id,updated_date=now())
            req_status = RequestStatusUtil.MODIFICATION
            VendorModificationRel.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id, entity_id=self._entity_id()).delete()
            vendorapprove_auditdata = {'id': vendor_id, 'vendor_status': VendorStatusUtil.APPROVED}
        if request_sts == 5:
            vendor = Vendor.objects.using(self._current_app_schema()).filter(id=vendor_id, entity_id=self._entity_id()).update(vendor_status=VendorStatusUtil.RENEWAL_APPROVED,
                                                                remarks=comments,updated_by=user_id,updated_date=now())
            req_status = RequestStatusUtil.RENEWAL
            vendorapprove_auditdata = {'id': vendor_id, 'vendor_status': VendorStatusUtil.APPROVED}
        vendorreftype = 1
        id = -1
        self.audit_function(vendorapprove_auditdata, vendor_id, user_id, req_status, vendor_id, ModifyStatus.update,
                            vendorreftype)
        VendorQueue.objects.using(self._current_app_schema()).create(vendor_id_id=vendor_id, from_user_id=user_id, to_user_id=user_id,
                                   created_date=timezone.now(),
                                   comments=comments, is_sys=True, entity_id=self._entity_id()
                                   )

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    def modification_reject_status(self, vendor_id, user_id, data):
        comments = data['comments']
        status = data['status']
        if status == 0:
            vendor = Vendor.objects.using(self._current_app_schema()).filter(id=vendor_id, entity_id=self._entity_id()).update(vendor_status=VendorStatusUtil.REJECTED, remarks=comments)
            req_status = RequestStatusUtil.MODIFICATION
            vendorreftype = -1
            id = -1
            self.audit_function(vendor, vendor_id, user_id, req_status, id, ModifyStatus.update, vendorreftype)
            VendorQueue.objects.using(self._current_app_schema()).create(vendor_id_id=vendor_id, from_user_id=user_id, to_user_id=user_id,
                                       comments=comments, is_sys=True, entity_id=self._entity_id())
            VendorModificationRel.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id, entity_id=self._entity_id()).delete()
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj
        else:
            vendor = Vendor.objects.using(self._current_app_schema()).filter(id=vendor_id,
                                                                             entity_id=self._entity_id()).update(
                vendor_status=VendorStatusUtil.RETURN, remarks=comments)
            req_status = RequestStatusUtil.MODIFICATION
            vendorreftype = -1
            id = -1
            self.audit_function(vendor, vendor_id, user_id, req_status, id, ModifyStatus.update, vendorreftype)
            VendorQueue.objects.using(self._current_app_schema()).create(vendor_id_id=vendor_id, from_user_id=user_id,
                                                                         to_user_id=user_id,
                                                                         comments=comments, is_sys=True,
                                                                         entity_id=self._entity_id())
            VendorModificationRel.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id,
                                                                                   entity_id=self._entity_id()).delete()
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj

    def audit_function(self, vendor, vendor_id, user_id, req_status, id, action, relreftype):
        logger.info(str(vendor)+ 'VENDOR TESTING'+ str(relreftype))
        if action == ModifyStatus.delete:
            data = None
        elif action == ModifyStatus.update:
            data = vendor
        else:
            data = vendor.__dict__
            del data['_state']
        audit_service = VendorAuditService(self._scope())
        audit_obj = VendorAuditResponse()
        audit_obj.set_refid(vendor_id)
        audit_obj.set_reftype(VendorRefType.VENDOR)
        audit_obj.set_userid(user_id)
        audit_obj.set_reqstatus(req_status)
        audit_obj.set_relrefid(id)
        audit_obj.set_relreftype(relreftype)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_vendoraudit(audit_obj)

        return

    def modify_delrecursion(self, ref_id):
        try:
            obj = VendorModificationRel.objects.using(self._current_app_schema()).filter(modify_ref_id=ref_id, entity_id=self._entity_id())[0]
            c = obj.ref_id
            VendorModificationRel.objects.using(self._current_app_schema()).get(id=obj.id, entity_id=self._entity_id()).delete()
            self.modify_delrecursion(c)

        except:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj

    def ismaker(self, user_id, userid_check):
        roleemployee_service = RoleEmployeeService(self._scope())
        maker_condition = False
        resp_obj = roleemployee_service.fetch_employee_submodule(user_id, userid_check)
        if len(resp_obj.data) != 0:
            for i in resp_obj.data:
                if i.name == 'Vendor':
                    for j in i.role:
                        if j.name == 'Maker':
                            maker_condition = True
            return maker_condition

        else:
            return maker_condition

    def ischecker(self, request):
        roleemployee_service = RoleEmployeeService(self._scope())
        user_id = request.employee_id
        userid_check = True
        checker_condition = False
        resp_obj = roleemployee_service.fetch_employee_submodule(user_id, userid_check)
        if len(resp_obj.data) != 0:
            for i in resp_obj.data:
                if i.name == 'Vendor':
                    for j in i.role:
                        if j.name == 'Checker':
                            checker_condition = True
            return checker_condition

        else:
            return checker_condition

    def isheader(self, request):
        roleemployee_service = RoleEmployeeService(self._scope())
        user_id = request.employee_id
        userid_check = True
        header_condition = False
        resp_obj = roleemployee_service.fetch_employee_submodule(user_id, userid_check)
        if len(resp_obj.data) != 0:
            for i in resp_obj.data:
                if i.name == 'Vendor':
                    for j in i.role:
                        if j.name == 'Header':
                            header_condition = True

            return header_condition
        else:
            return header_condition

    def iscompliance(self, request):
        roleemployee_service = RoleEmployeeService(self._scope())
        user_id = request.employee_id
        userid_check = True
        Compliance_condition = False
        resp_obj = roleemployee_service.fetch_employee_submodule(user_id, userid_check)
        if len(resp_obj.data) != 0:
            for i in resp_obj.data:
                if i.name == 'Vendor':
                    for j in i.role:
                        if j.name == 'Compliance':
                            Compliance_condition = True

            return Compliance_condition
        else:
            return Compliance_condition

    def checkmodification_flag(self, vendor_id, ref_type, modify_ref_id):
        try:
            venrel_obj = VendorModificationRel.objects.using(self._current_app_schema()).get(
                Q(vendor_id=vendor_id) & Q(ref_type=ref_type) & Q(modify_ref_id=modify_ref_id) & Q(is_flag=True)&Q(entity_id=self._entity_id()))
            new_mod_ref_id = venrel_obj.ref_id
            ref_id = venrel_obj.modify_ref_id
            if new_mod_ref_id == ref_id:
                return ref_id
            else:
                return self.checkmodification_flag(vendor_id, ref_type, new_mod_ref_id)

        except:
            return modify_ref_id

    def append_doc(self, val1, val2):
        arry = []
        if len(val1) != 0:
            for i in val1:
                arry.append(i)
        if len(val2) != 0:
            for i in val2:
                arry.append(i)
        return arry

    def checkmodify_rel(self, type, id):
        flag = False
        modifyrel_obj = VendorModificationRel.objects.using(self._current_app_schema()).filter(Q(ref_type=type) & Q(modify_ref_id=id)&Q(entity_id=self._entity_id()))
        if len(modifyrel_obj) > 0:
            flag = True
        return flag

    def branchvalidate(self, branch_id):
        vendor_obj = SupplierBranch.objects.using(self._current_app_schema()).get(id=branch_id, entity_id=self._entity_id())
        vendor_id = vendor_obj.vendor.id
        composite_obj = Vendor.objects.using(self._current_app_schema()).get(id=vendor_id, entity_id=self._entity_id())
        composite = composite_obj.composite
        # activty
        activty_obj = SupplierActivity.objects.using(self._current_app_schema()).filter(Q(branch_id=branch_id) & Q(modify_status=-1)&Q(entity_id=self._entity_id())).values('id')
        activty_rel_abj1 = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_ACTIVITY) & Q(mod_status=ModifyStatus.create) & Q(is_flag=True) & Q(
                vendor_id=vendor_id)&Q(entity_id=self._entity_id())).values('ref_id')
        activty_venrel_delete1 = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_ACTIVITY) & Q(mod_status=ModifyStatus.delete) & Q(is_flag=True) & Q(
                vendor_id=vendor_id)&Q(entity_id=self._entity_id())).values('ref_id')
        activty_rel_abj = []
        for a1 in activty_rel_abj1:
            relobj = SupplierActivity.objects.using(self._current_app_schema()).filter(Q(branch_id=branch_id) & Q(id=a1['ref_id'])&Q(entity_id=self._entity_id())).values('id')
            if len(relobj) != 0:
                activty_rel_abj.append(a1)

        activty_venrel_delete = []
        for a2 in activty_venrel_delete1:
            relobj = SupplierActivity.objects.using(self._current_app_schema()).filter(
                Q(branch_id=branch_id) & Q(id=a2['ref_id'])&Q(entity_id=self._entity_id())).values('id')
            if len(relobj) != 0:
                activty_venrel_delete.append(a2)

        a = []
        if len(activty_obj) != 0:

            for i in activty_obj:
                a.append(i['id'])
        if len(activty_rel_abj) != 0:
            for j in activty_rel_abj:
                a.append(j['ref_id'])
        d = []
        if len(a) != 0:
            for b in a:
                if len(activty_venrel_delete) != 0:
                    for c in activty_venrel_delete:
                        if b != c['ref_id']:
                            d.append(b)
                else:
                    d.append(b)

        activity_flag = True
        if len(d) != 0:
            for e in d:
                activty_obj1 = SupplierActivity.objects.using(self._current_app_schema()).filter(Q(id=e) & Q(is_validate=True)&Q(entity_id=self._entity_id()))
                if len(activty_obj1) == 0:
                    activity_flag = False
        else:
            activity_flag = False

        # tax
        if composite == 2:
            tax_obj = SupplierTax.objects.using(self._current_app_schema()).filter(Q(branch_id=branch_id) & Q(modify_status=-1)&Q(entity_id=self._entity_id()))
            tax_venrel_create1 = VendorModificationRel.objects.filter(
                Q(ref_type=VendorRefType.VENDOR_SUPPLIERTAX) & Q(mod_status=ModifyStatus.create) & Q(is_flag=True) & Q(
                    vendor_id=vendor_id)&Q(entity_id=self._entity_id())).values('ref_id')
            tax_venrel_delete1 = VendorModificationRel.objects.using(self._current_app_schema()).filter(
                Q(ref_type=VendorRefType.VENDOR_SUPPLIERTAX) & Q(mod_status=ModifyStatus.delete) & Q(is_flag=True) & Q(
                    vendor_id=vendor_id)&Q(entity_id=self._entity_id())).values('ref_id')
            tax_venrel_create = []
            for a1 in tax_venrel_create1:
                relobj = SupplierTax.objects.using(self._current_app_schema()).filter(
                    Q(branch_id=branch_id) & Q(id=a1['ref_id'])&Q(entity_id=self._entity_id())).values('id')
                if len(relobj) != 0:
                    tax_venrel_create.append(a1)

            tax_venrel_delete = []
            for a2 in tax_venrel_delete1:
                relobj = SupplierTax.objects.using(self._current_app_schema()).filter(
                    Q(branch_id=branch_id) & Q(id=a2['ref_id'])&Q(entity_id=self._entity_id())).values('id')
                if len(relobj) != 0:
                    tax_venrel_delete.append(a2)

            tax_obj_len = len(tax_obj)
            tax_venrel_create_len = len(tax_venrel_create)
            tax_venrel_delete_len = len(tax_venrel_delete)
            tax_count = tax_obj_len + tax_venrel_create_len
            tax_flag = True
            if tax_count > 0:
                tax_flag = True
        else:
            tax_flag = True
        # payment
        payment_obj = SupplierPayment.objects.using(self._current_app_schema()).filter(Q(supplierbranch_id=branch_id) & Q(modify_status=-1) & Q(status=1)&Q(entity_id=self._entity_id()))
        payment_venrel_create1 = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_PAYMENT) & Q(mod_status=ModifyStatus.create) & Q(is_flag=True) & Q(
                vendor_id=vendor_id)&Q(entity_id=self._entity_id())).values('ref_id')
        payment_venrel_delete1 = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_PAYMENT) & Q(mod_status=ModifyStatus.delete) & Q(is_flag=True) & Q(
                vendor_id=vendor_id)&Q(entity_id=self._entity_id())).values('ref_id')

        payment_venrel_create = []
        for a1 in payment_venrel_create1:
            relobj = SupplierPayment.objects.using(self._current_app_schema()).filter(
                Q(supplierbranch_id=branch_id) & Q(id=a1['ref_id'])&Q(entity_id=self._entity_id())).values('id')
            if len(relobj) != 0:
                payment_venrel_create.append(a1)

        payment_venrel_delete = []
        for a2 in payment_venrel_delete1:
            relobj = SupplierPayment.objects.using(self._current_app_schema()).filter(
                Q(supplierbranch_id=branch_id) & Q(id=a2['ref_id'])&Q(entity_id=self._entity_id())).values('id')
            if len(relobj) != 0:
                payment_venrel_delete.append(a2)

        payment_obj_len = len(payment_obj)
        payment_venrel_create_len = len(payment_venrel_create)
        payment_venrel_delete_len = len(payment_venrel_delete)
        payment_count = payment_obj_len + payment_venrel_create_len
        payment_flag = False
        if payment_count > 0:
            payment_flag = True
        flag = False
        if (activity_flag & payment_flag & tax_flag) == True:
            flag = True
        return flag

    def activitydtlcatalog_validate(self, activitydtl_id):
        flag = False
        catelog_obj = Catelog.objects.using(self._current_app_schema()).filter(Q(activitydetail_id=activitydtl_id) & Q(modify_status=-1)&Q(entity_id=self._entity_id()))
        catelog_venrel_create1 = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_CATELOG) & Q(mod_status=ModifyStatus.create) & Q(is_flag=True)&Q(entity_id=self._entity_id())).values(
            'ref_id')
        catelog_venrel_delete1 = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_CATELOG) & Q(mod_status=ModifyStatus.delete) & Q(is_flag=True)&Q(entity_id=self._entity_id())).values(
            'ref_id')

        catelog_venrel_create = []
        for a1 in catelog_venrel_create1:
            relobj = Catelog.objects.using(self._current_app_schema()).filter(
                Q(activitydetail_id=activitydtl_id) & Q(id=a1['ref_id'])&Q(entity_id=self._entity_id())).values('id')
            if len(relobj) != 0:
                catelog_venrel_create.append(a1)

        catelog_venrel_delete = []
        for a2 in catelog_venrel_delete1:
            relobj = Catelog.objects.using(self._current_app_schema()).filter(
                Q(activitydetail_id=activitydtl_id) & Q(id=a2['ref_id'])&Q(entity_id=self._entity_id())).values('id')
            if len(relobj) != 0:
                catelog_venrel_delete.append(a2)

        catelog_obj_len = len(catelog_obj)
        catelog_venrel_create_len = len(catelog_venrel_create)
        catelog_venrel_delete_len = len(catelog_venrel_delete)
        catelog_count = catelog_obj_len + catelog_venrel_create_len
        if catelog_count > 0:
            flag = True
        return flag

    def activtydtl_validate(self, activty_id):

        activty_obj = ActivityDetail.objects.using(self._current_app_schema()).filter(Q(activity_id=activty_id) & Q(modify_status=-1)&Q(entity_id=self._entity_id())).values('id')
        activty_venrel_create1 = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_ACTIVITYDETAIL) & Q(mod_status=ModifyStatus.create) & Q(
                is_flag=True)&Q(entity_id=self._entity_id())).values('ref_id')
        catelog_venrel_delete1 = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_ACTIVITYDETAIL) & Q(mod_status=ModifyStatus.delete) & Q(
                is_flag=True)&Q(entity_id=self._entity_id())).values('ref_id')

        activty_venrel_create = []
        for a1 in activty_venrel_create1:
            relobj = ActivityDetail.objects.using(self._current_app_schema()).filter(
                Q(activity_id=activty_id) & Q(id=a1['ref_id'])&Q(entity_id=self._entity_id())).values('id')
            if len(relobj) != 0:
                activty_venrel_create.append(a1)

        catelog_venrel_delete = []
        for a2 in catelog_venrel_delete1:
            relobj = ActivityDetail.objects.using(self._current_app_schema()).filter(
                Q(activity_id=activty_id) & Q(id=a2['ref_id'])&Q(entity_id=self._entity_id())).values('id')
            if len(relobj) != 0:
                catelog_venrel_delete.append(a2)

        a = []
        if len(activty_obj) != 0:
            for i in activty_obj:
                a.append(i['id'])
        if len(activty_venrel_create) != 0:
            for j in activty_venrel_create:
                a.append(j['ref_id'])
        d = []
        if len(a) != 0:
            for b in a:
                if len(catelog_venrel_delete) != 0:
                    for c in catelog_venrel_delete:
                        if b != c['ref_id']:
                            d.append(b)
                else:
                    d.append(b)

        activitydtl_flag = True
        if len(d) != 0:
            for e in d:
                activty_obj1 = ActivityDetail.objects.using(self._current_app_schema()).filter(Q(id=e) & Q(is_validate=True)&Q(entity_id=self._entity_id()))
                if len(activty_obj1) == 0:
                    activitydtl_flag = False
        else:
            activitydtl_flag = False
        return activitydtl_flag

    def vendor_validate(self, vendor_id):
        # branch
        branch_obj = SupplierBranch.objects.using(self._current_app_schema()).filter(Q(vendor_id=vendor_id) & Q(modify_status=-1)&Q(entity_id=self._entity_id())).values('id')
        branch_venrel_create = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_BRANCH) & Q(mod_status=ModifyStatus.create) & Q(is_flag=True) & Q(
                vendor_id=vendor_id)&Q(entity_id=self._entity_id())).values('ref_id')
        branch_venrel_delete = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_BRANCH) & Q(mod_status=ModifyStatus.delete) & Q(is_flag=True) & Q(
                vendor_id=vendor_id)&Q(entity_id=self._entity_id())).values('ref_id')

        a = []
        if len(branch_obj) != 0:
            for i in branch_obj:
                a.append(i['id'])
            if len(branch_venrel_create) != 0:
                for j in branch_venrel_create:
                    a.append(j['ref_id'])
        d = []
        if len(a) != 0:
            for b in a:
                if len(branch_venrel_delete) != 0:
                    for c in branch_venrel_delete:
                        if b != c['ref_id']:
                            d.append(b)
                else:
                    d.append(b)

        branch_flag = True
        if len(d) != 0:
            for e in d:
                activty_obj1 = SupplierBranch.objects.using(self._current_app_schema()).filter(Q(id=e) & Q(is_validate=True)&Q(entity_id=self._entity_id()))
                if len(activty_obj1) == 0:
                    branch_flag = False
        else:
            branch_flag = False

        # Client
        client_obj = VendorClient.objects.using(self._current_app_schema()).filter(Q(vendor_id=vendor_id) & Q(modify_status=-1)&Q(entity_id=self._entity_id()))
        client_venrel_create = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_CLIENT) & Q(mod_status=ModifyStatus.create) & Q(is_flag=True) & Q(
                vendor_id=vendor_id)&Q(entity_id=self._entity_id()))
        client_venrel_delete = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_CLIENT) & Q(mod_status=ModifyStatus.delete) & Q(is_flag=True) & Q(
                vendor_id=vendor_id)&Q(entity_id=self._entity_id()))
        client_obj_len = len(client_obj)
        client_venrel_create_len = len(client_venrel_create)
        client_venrel_delete_len = len(client_venrel_delete)
        client_count = client_obj_len + client_venrel_create_len
        client_flag = False
        if client_count > 0:
            client_flag = True
        # subcontractor
        contractor_obj = VendorSubContractor.objects.using(self._current_app_schema()).filter(Q(vendor_id=vendor_id) & Q(modify_status=-1)&Q(entity_id=self._entity_id()))
        contractor_venrel_create = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_CONTRACT) & Q(mod_status=ModifyStatus.create) & Q(is_flag=True) & Q(
                vendor_id=vendor_id)&Q(entity_id=self._entity_id()))
        contractor_venrel_delete = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_CONTRACT) & Q(mod_status=ModifyStatus.delete) & Q(is_flag=True) & Q(
                vendor_id=vendor_id)&Q(entity_id=self._entity_id()))
        contractor_obj_len = len(contractor_obj)
        contractor_venrel_create_len = len(contractor_venrel_create)
        contractor_venrel_delete_len = len(contractor_venrel_delete)
        contractor_count = contractor_obj_len + contractor_venrel_create_len
        contractor_flag = False
        if contractor_count > 0:
            contractor_flag = True
        # product
        product_obj = SupplierProduct.objects.using(self._current_app_schema()).filter(Q(vendor_id=vendor_id) & Q(modify_status=-1)&Q(entity_id=self._entity_id()))
        product_venrel_create = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_PRODUCT) & Q(mod_status=ModifyStatus.create) & Q(is_flag=True) & Q(
                vendor_id=vendor_id)&Q(entity_id=self._entity_id()))
        product_venrel_delete = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_PRODUCT) & Q(mod_status=ModifyStatus.delete) & Q(is_flag=True) & Q(
                vendor_id=vendor_id)&Q(entity_id=self._entity_id()))
        product_obj_len = len(product_obj)
        product_venrel_create_len = len(product_venrel_create)
        product_venrel_delete_len = len(product_venrel_delete)
        product_count = product_obj_len + product_venrel_create_len
        product_flag = False
        if product_count > 0:
            product_flag = True
        # document
        document_obj = VendorDocument.objects.using(self._current_app_schema()).filter(Q(partner_id=vendor_id) & Q(modify_status=-1)&Q(entity_id=self._entity_id()))
        document_venrel_create = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_DOCUMENT) & Q(mod_status=ModifyStatus.create) & Q(is_flag=True) & Q(
                vendor_id=vendor_id)&Q(entity_id=self._entity_id()))
        document_venrel_delete = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_DOCUMENT) & Q(mod_status=ModifyStatus.delete) & Q(is_flag=True) & Q(
                vendor_id=vendor_id)&Q(entity_id=self._entity_id()))
        document_obj_len = len(document_obj)
        document_venrel_create_len = len(document_venrel_create)
        document_venrel_delete_len = len(document_venrel_delete)
        document_count = document_obj_len + document_venrel_create_len
        document_flag = False
        vendor_obj = Vendor.objects.using(self._current_app_schema()).get(id=vendor_id, entity_id=self._entity_id())
        comosite = vendor_obj.composite
        # gst validation
        mod_edit = self.check_if_mod_edit(vendor_id)
        if mod_edit['edit'] == True:
            comosite = mod_edit['new_vendor'].composite
        if comosite is not VendorCompositeUtil.UNREGISTER:
            branch_flag = self.check_branch_gst(vendor_obj.id)
        validate = self.ven_catagory_validation(vendor_obj)
        # active supplier
        active_supplier = self.get_active_supplier(vendor_obj.id)
        branch_count = self.branch_count_flag(vendor_id)
        if active_supplier == False or branch_count == False:
            branch_flag = False
        if branch_flag == True:
            branch_flag = self.vendor_active_payment(vendor_obj.id)
        if (document_count > 0) and (validate['vendor_doc'] == True):
            document_flag = True
        flag = False
        venres_obj = VendorCheckListData()
        status = 0
        if (branch_flag & client_flag & contractor_flag & product_flag & document_flag) == True:
            flag = True
        if (branch_flag & document_flag & validate['kyc']) == True:
            status = 1
        venres_obj.set_SupplierBranch(branch_flag)
        venres_obj.set_VendorSubContractor(contractor_flag)
        venres_obj.set_VendorClient(client_flag)
        venres_obj.set_VendorDocument(document_flag)
        venres_obj.set_SupplierProduct(product_flag)
        venres_obj.set_composite(comosite)
        venres_obj.set_gst(validate["gst"])
        venres_obj.set_pan(validate["pan"])
        venres_obj.set_contract(validate["contract"])
        venres_obj.set_cancel_cheque(validate["cheque"])
        venres_obj.set_broad_resolution(validate["board"])
        venres_obj.set_bcp_questionary(validate['bcp_quest'])
        venres_obj.set_due_diligence(validate['due_deligence'])
        # venres_obj.set_intermediary(validate['intermediary'])
        venres_obj.set_customer_category(validate['category'])
        venres_obj.set_kyc(validate['kyc'])
        venres_obj.set_status(status)
        return venres_obj

    def vendortransaction_validate(self, vendor_id):
        # branch
        branch_obj = SupplierBranch.objects.using(self._current_app_schema()).filter(Q(vendor_id=vendor_id) & Q(modify_status=-1)&Q(entity_id=self._entity_id())).values('id')
        branch_venrel_create = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_BRANCH) & Q(mod_status=ModifyStatus.create) & Q(is_flag=True) & Q(
                vendor_id=vendor_id)&Q(entity_id=self._entity_id())).values('ref_id')
        branch_venrel_delete = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_BRANCH) & Q(mod_status=ModifyStatus.delete) & Q(is_flag=True) & Q(
                vendor_id=vendor_id)&Q(entity_id=self._entity_id())).values('ref_id')

        a = []
        if len(branch_obj) != 0:
            for i in branch_obj:
                a.append(i['id'])
            if len(branch_venrel_create) != 0:
                for j in branch_venrel_create:
                    a.append(j['ref_id'])
        d = []
        if len(a) != 0:
            for b in a:
                if len(branch_venrel_delete) != 0:
                    for c in branch_venrel_delete:
                        if b != c['ref_id']:
                            d.append(b)
                else:
                    d.append(b)

        branch_flag = True
        if len(d) != 0:
            for e in d:
                activty_obj1 = SupplierBranch.objects.using(self._current_app_schema()).filter(Q(id=e) & Q(is_validate=True)&Q(entity_id=self._entity_id()))
                if len(activty_obj1) == 0:
                    branch_flag = False
        else:
            branch_flag = False

        # Client
        client_obj = VendorClient.objects.using(self._current_app_schema()).filter(Q(vendor_id=vendor_id) & Q(modify_status=-1)&Q(entity_id=self._entity_id()))
        client_venrel_create = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_CLIENT) & Q(mod_status=ModifyStatus.create) & Q(is_flag=True) & Q(
                vendor_id=vendor_id)&Q(entity_id=self._entity_id()))
        client_venrel_delete = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_CLIENT) & Q(mod_status=ModifyStatus.delete) & Q(is_flag=True) & Q(
                vendor_id=vendor_id)&Q(entity_id=self._entity_id()))
        client_obj_len = len(client_obj)
        client_venrel_create_len = len(client_venrel_create)
        client_venrel_delete_len = len(client_venrel_delete)
        client_count = client_obj_len + client_venrel_create_len
        client_flag = False
        if client_count > 0:
            client_flag = True
        # subcontractor
        contractor_obj = VendorSubContractor.objects.using(self._current_app_schema()).filter(Q(vendor_id=vendor_id) & Q(modify_status=-1)&Q(entity_id=self._entity_id()))
        contractor_venrel_create = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_CONTRACT) & Q(mod_status=ModifyStatus.create) & Q(is_flag=True) & Q(
                vendor_id=vendor_id)&Q(entity_id=self._entity_id()))
        contractor_venrel_delete = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_CONTRACT) & Q(mod_status=ModifyStatus.delete) & Q(is_flag=True) & Q(
                vendor_id=vendor_id)&Q(entity_id=self._entity_id()))
        contractor_obj_len = len(contractor_obj)
        contractor_venrel_create_len = len(contractor_venrel_create)
        contractor_venrel_delete_len = len(contractor_venrel_delete)
        contractor_count = contractor_obj_len + contractor_venrel_create_len
        contractor_flag = False
        if contractor_count > 0:
            contractor_flag = True
        # product
        product_obj = SupplierProduct.objects.using(self._current_app_schema()).filter(Q(vendor_id=vendor_id) & Q(modify_status=-1)&Q(entity_id=self._entity_id()))
        product_venrel_create = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_PRODUCT) & Q(mod_status=ModifyStatus.create) & Q(is_flag=True) & Q(
                vendor_id=vendor_id)&Q(entity_id=self._entity_id()))
        product_venrel_delete = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_PRODUCT) & Q(mod_status=ModifyStatus.delete) & Q(is_flag=True) & Q(
                vendor_id=vendor_id)&Q(entity_id=self._entity_id()))
        product_obj_len = len(product_obj)
        product_venrel_create_len = len(product_venrel_create)
        product_venrel_delete_len = len(product_venrel_delete)
        product_count = product_obj_len + product_venrel_create_len
        product_flag = False
        if product_count > 0:
            product_flag = True
        # document
        document_obj = VendorDocument.objects.using(self._current_app_schema()).filter(Q(partner_id=vendor_id) & Q(modify_status=-1)&Q(entity_id=self._entity_id()))
        document_venrel_create = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_DOCUMENT) & Q(mod_status=ModifyStatus.create) & Q(is_flag=True) & Q(
                vendor_id=vendor_id)&Q(entity_id=self._entity_id()))
        document_venrel_delete = VendorModificationRel.objects.using(self._current_app_schema()).filter(
            Q(ref_type=VendorRefType.VENDOR_DOCUMENT) & Q(mod_status=ModifyStatus.delete) & Q(is_flag=True) & Q(
                vendor_id=vendor_id)&Q(entity_id=self._entity_id()))
        document_obj_len = len(document_obj)
        document_venrel_create_len = len(document_venrel_create)
        document_venrel_delete_len = len(document_venrel_delete)
        document_count = document_obj_len + document_venrel_create_len
        document_flag = False
        if document_count > 0:
            document_flag = True
        flag = False
        venres_obj = VendorCheckListData()
        if (branch_flag & client_flag & contractor_flag & product_flag & document_flag) == True:
            flag = True

        return flag

    # def get_unitprice(self, suplier_id, product_id):
    #     map_obj = ProductMapping.objects.get(Q(branch_id=suplier_id) & Q(product_id=product_id) & Q(dts=0))
    #     data = {"unitprice": map_obj.unitprice}
    #     return data

    def getvendor_name(self, query, vys_page, user_id):
        condition = Q(mainstatus=2)&Q(entity_id=self._entity_id())
        if query is not None:
            condition &= (Q(name__icontains=query) | Q(code__icontains=query))

        vendorList = Vendor.objects.using(self._current_app_schema()).filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
        vlist = NWisefinList()
        for vendor in vendorList:
            vobj = VendorListData()
            vobj.set_id(vendor.id)
            disp_name = '(' + vendor.code + ') ' + vendor.name
            vobj.set_name(disp_name)
            vlist.append(vobj)
            vpage = NWisefinPaginator(vendorList, vys_page.get_index(), 10)
            vlist.set_pagination(vpage)
        return vlist

    def landlord_tax(self, vendor_id, query, vys_page, user_id):
        vendorList = SupplierTax.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id, entity_id=self._entity_id()).values_list('subtax_id', flat=True)
        vlist = NWisefinList()
        subtax_obj = SubTax.objects.using(self._app_schema(ApplicationNamespace.MASTER_SERVICE)).filter(id__in=vendorList, entity_id=self._entity_id())[vys_page.get_offset():vys_page.get_query_limit()]
        for subtax in subtax_obj:
            subtax_data = SubTaxResponse()
            subtax_data.set_id(subtax.id)
            subtax_data.set_name(subtax.name)
            vlist.append(subtax_data)
            vpage = NWisefinPaginator(vendorList, vys_page.get_index(), 10)
            vlist.set_pagination(vpage)
        return vlist

    def product_supplier(self, product_id, query, vys_page, user_id, dts):
        # condition=Q(product_id__in=product_id)
        if query != None:
            condition = Q(product_id__in=product_id) & Q(dts__in=dts)
            condition &= (Q(branch__name__icontains=query) | Q(branch__code__icontains=query))
        if len(dts) != 0:
            condition = Q(product_id__in=product_id) & Q(dts__in=dts) & Q(status=1) & Q(todate__gte=date.today())
        else:
            condition = Q(product_id__in=product_id) & Q(status=1) & Q(todate__gte=date.today())
        condition &= Q(entity_id=self._entity_id())

        # logger.info(map_obj)
        # from collections import Counter
        # a = dict(Counter(map_obj))
        b = []
        # for i in a:
        #     if a[i] == len(product_id):
        #         b.append(i)
        vlist = NWisefinList()
        for product in b:
            sup_obj = SupplierBranch.objects.using(self._current_app_schema()).get(id=product, entity_id=self._entity_id())
            subtax_data = SubTaxResponse()
            subtax_data.set_id(sup_obj.id)
            disp_name = '(' + sup_obj.code + ') ' + sup_obj.name
            subtax_data.set_name(disp_name)

            vlist.append(subtax_data)
            vpage = NWisefinPaginator(1, vys_page.get_index(), 10)
            vlist.set_pagination(vpage)
        return vlist

    def checkis_maker(self, vendor_id, employee_id):
        condition = Q(vendor_id_id=vendor_id) &Q(entity_id=self._entity_id())
        update_vendor = VendorQueue.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[0]
        from_user_id = update_vendor.from_user_id
        if from_user_id == employee_id:
            return False
        else:
            return True

    def valid_checker(self, vendor_id, employee_id):
        condition = Q(vendor_id_id=vendor_id)&Q(entity_id=self._entity_id())
        update_vendor = VendorQueue.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[0]
        from_user_id = update_vendor.from_user_id
        if from_user_id == employee_id:
            return False
        else:
            return True
    def pan_check(self,vendorObj):
        if not vendorObj.get_id() is None:
            getstatus=Vendor.objects.using(self._current_app_schema()).filter(modify_ref_id=vendorObj.get_id(), entity_id=self._entity_id())
            if getstatus:
                test_vendor = Vendor.objects.using(self._current_app_schema()).filter(~Q(id=vendorObj.get_id()),~Q(modify_ref_id=vendorObj.get_id())&Q(entity_id=self._entity_id())).values_list('panno', flat=True)
            else:
                test_vendor = Vendor.objects.using(self._current_app_schema()).filter(~Q(id=vendorObj.get_id())&Q(entity_id=self._entity_id())).values_list('panno', flat=True)
        else:
            test_vendor = Vendor.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).values_list('panno', flat=True)
        modf_str_list = [i for i in test_vendor if i]
        string_list = [x.lower() for x in modf_str_list]
        # test_vendor_1 = Vendor.objects.values_list('gstno', flat=True)
        # modf_str_list_1 = [i for i in test_vendor_1 if i]
        # string_list_1 = [x.lower() for x in modf_str_list_1]
        if vendorObj.get_panno() != 'PANNOTAVBL':
            if vendorObj.get_panno().lower() in string_list:
                return 'PANNO_EXISTS'

    def get_product(self, product_type_id, dts, vys_page, user_id, query):
        condition = Q(producttype_id=product_type_id) & Q(name__icontains=query) &Q(entity_id=self._entity_id())
        map_obj = Product.objects.using(self._app_schema(ApplicationNamespace.MASTER_SERVICE)).filter(condition)
        # map_obj=Product.objects.filter(producttype_id=product_type_id) & (name__icontains=query)
        product = []
        for x in map_obj:
            product.append(x.id)
        product_id = []
        li = []


        vlist = NWisefinList()
        for z in product:
            product_obj = Product.objects.using(self._app_schema(ApplicationNamespace.MASTER_SERVICE)).get(id=z, entity_id=self._entity_id())
            subtax_data = SubTaxResponse()
            subtax_data.set_name(product_obj.name)
            subtax_data.set_id(product_obj.id)
            uom_name = Uom.objects.using(self._app_schema(ApplicationNamespace.MASTER_SERVICE)).get(id=product_obj.uom_id, entity_id=self._entity_id())
            subtax_data.set_uom_name(uom_name.name)
            vlist.append(subtax_data)
            vpage = NWisefinPaginator(map_obj, vys_page.get_index(), 10)
            vlist.set_pagination(vpage)
        return vlist


    def common_search_vendor(self,vys_page, query):
        if query == None:
            vendorlist = Vendor.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())[vys_page.get_offset():vys_page.get_query_limit()]
        else:
            vendorlist = Vendor.objects.using(self._current_app_schema()).filter(name__icontains=query, entity_id=self._entity_id())[vys_page.get_offset():vys_page.get_query_limit()]

        # print(list_length)
        employeecat_list = NWisefinList()
        for vendor in vendorlist:
            vendor_data = VendorListData()
            vendor_data.set_id(vendor.id)
            vendor_data.set_name(vendor.name)
            employeecat_list.append(vendor_data)
            vpage = NWisefinPaginator(vendorlist, vys_page.get_index(), 10)
            employeecat_list.set_pagination(vpage)
        return employeecat_list

    def for_monoaddress_report(self,type,addressarray):
        addressarray=ast.literal_eval(addressarray)
        if type=='Supplier':
            brancharray = list(SupplierBranch.objects.using(self._current_app_schema()).filter(code__in=addressarray, entity_id=self._entity_id()).values_list('address_id', flat=True))
            addressarray = VendorRelAddress.objects.using(self._current_app_schema()).select_related('supplierbranch').filter(id__in=brancharray, entity_id=self._entity_id()).values('supplierbranch__code','line1','line2','line3','pincode_id','city_id','state_id','district_id')
            pincodearray=list(VendorRelAddress.objects.using(self._current_app_schema()).filter(id__in=brancharray, entity_id=self._entity_id()).values_list('pincode_id', flat=True))
            cityarray=list(VendorRelAddress.objects.using(self._current_app_schema()).filter(id__in=brancharray, entity_id=self._entity_id()).values_list('city_id', flat=True))
            districtarray=list(VendorRelAddress.objects.using(self._current_app_schema()).filter(id__in=brancharray, entity_id=self._entity_id()).values_list('district_id', flat=True))
            add=Pincode.objects.using(self._app_schema(ApplicationNamespace.MASTER_SERVICE)).filter(id__in=pincodearray,city__in=cityarray,district__in=districtarray, entity_id=self._entity_id()).values('id','no','district__code','city__code','district__state__code')
            dfp = pd.DataFrame.from_records(add)
            bdf = pd.DataFrame.from_records(addressarray)
            if dfp.empty==False:
                dfp.columns = ['pincode_id', 'pincode', 'district_code', 'city_code', 'state_code']

                res = bdf.merge(dfp, on=['pincode_id'])
                res['type']='Supplier'
                addressarray = res
                return addressarray.to_dict('records')
            else:
                 addressarray=[]
                 return  addressarray


        elif type=='Vendor':
            vendorarray = list(Vendor.objects.using(self._current_app_schema()).filter(code__in=addressarray, entity_id=self._entity_id()).values_list('id', flat=True))
            addressarray = VendorAddress.objects.using(self._current_app_schema()).filter(vendor__in=vendorarray, entity_id=self._entity_id()).values('line1','line2','line3','vendor__code','pincode_id','city_id','state_id','district_id')
            pincodearray = list(
                VendorAddress.objects.using(self._current_app_schema()).filter(vendor__in=vendorarray, entity_id=self._entity_id()).values_list('pincode_id', flat=True))
            cityarray = list(VendorAddress.objects.using(self._current_app_schema()).filter(vendor__in=vendorarray, entity_id=self._entity_id()).values_list('city_id', flat=True))
            districtarray = list(
                VendorAddress.objects.using(self._current_app_schema()).filter(vendor__in=vendorarray, entity_id=self._entity_id()).values_list('district_id', flat=True))
            add = Pincode.objects.using(self._app_schema(ApplicationNamespace.MASTER_SERVICE)).filter(id__in=pincodearray, city__in=cityarray, district__in=districtarray, entity_id=self._entity_id()).values(
                'id', 'no', 'district__code', 'city__code', 'district__state__code')
            dfp = pd.DataFrame.from_records(add)
            bdf = pd.DataFrame.from_records(addressarray)
            if dfp.empty==False:
                dfp.columns = ['pincode_id', 'pincode', 'district_code', 'city_code', 'state_code']

                res = bdf.merge(dfp, on=['pincode_id'])
                res['type']='Vendor'
                addressarray = res

                return addressarray.to_dict('records')
            else:
                 addressarray=[]
                 return  addressarray

    def get_schema(self):
        return self._current_app_schema()

    def get_entity_id(self):
        return self._entity_id()

    def codegenerator(self, trans_type, emp_id):
        generator = Cgen.objects.using(self._current_app_schema()).filter(trans_type=trans_type, entity_id=self._entity_id(),
                                                 status=1)

        if len(generator) == 0:
            c_gen = Cgen.objects.using(self._current_app_schema()).create(trans_type=trans_type, entity_id=self._entity_id(),
                                                 Updated_by=emp_id,
                                                 Updated_date=timezone.now(), serial_no=1)
            serial_no = c_gen.serial_no

        else:
            old_serial_no = generator[0].serial_no
            serial_no = old_serial_no + 1
            Cgen.objects.using(self._current_app_schema()).filter(trans_type=trans_type,
                                         entity_id=self._entity_id()).update(Updated_by=emp_id,
                                                                     Updated_date=timezone.now(), serial_no=serial_no)

        return serial_no

    def fetch_supplier(self, supplier_id):
        supplier = SupplierBranch.objects.using(self._current_app_schema()).get(id=supplier_id, entity_id=self._entity_id())
        supplier_data = {"id": supplier.id, "code": supplier.code, "name": supplier.name, "gstno": supplier.gstno,
                         "address_id": supplier.address_id, "vendor_id": supplier.vendor_id}
        return supplier_data

    def fetch_supplierlist(self, supplier_ids):
        supplier_id2 = supplier_ids['supplier_id']
        obj = SupplierBranch.objects.using(self._current_app_schema()).filter(id__in=supplier_id2, entity_id=self._entity_id()).values('id', 'name')
        supplier_list_data = NWisefinList()
        for i in obj:
            data = {"id": i['id'], "name": i['name']}
            supplier_list_data.append(data)
        return supplier_list_data

    def get_vendor(self, id_obj):
        obj = Vendor.objects.using(self._current_app_schema()).filter(id__in=id_obj["vendor_id"],entity_id=self._entity_id()).values('id', 'name', 'code')
        arr = []
        for i in obj:
            data = {"id": i['id'], "name": i['name'], "code": i['code']}
            arr.append(data)
        return arr

    def ven_catagory_validation(self, vendor_rmidobj):
        pan_flag = False
        Gst_flag = False
        board_flag = False
        contract_flag = False
        cheque_flag = False
        document_validation = True
        # outsourcing
        due_diligence = False
        bcp_quest = False
        # third party
        intermediary = False
        # kyc and questionnaire
        kyc = False
        composite = vendor_rmidobj.composite
        vendor_id = vendor_rmidobj.id
        vendor_custgrp = vendor_rmidobj.group
        mod_edit = self.check_if_mod_edit(vendor_id)
        if mod_edit['edit'] == True:
            composite = mod_edit['new_vendor'].composite
            vendor_custgrp = mod_edit['new_vendor'].group
        cust_grp = vendorutil.getGroup(vendor_custgrp)
        custgrp_name = cust_grp.text
        # custcat_obj = CustomerCategory.objects.using(self._app_schema(ApplicationNamespace.MASTER_SERVICE)).filter(
        #     id=vendor_custcat)
        # custcat_name = custcat_obj[0].name
        if mod_edit['modify'] == True:
            condition = Q(partner_id=vendor_id,entity_id=self._entity_id())&(~Q(modify_status=0))
        else:
            condition = Q(partner_id=vendor_id,entity_id=self._entity_id()) &Q(modify_status=-1)
        ven_doc = VendorDocument.objects.using(self._current_app_schema()).filter(condition).values_list(
            'docgroup_id', flat=True)
        ven_doc = list(ven_doc)
        doc_group = DocumentGroup.objects.using(self._app_schema(ApplicationNamespace.MASTER_SERVICE)).filter(
            id__in=ven_doc).values_list('name', flat=True)
        doc_group = list(doc_group)
        outsourcing_values = list(Validation_vendor_doc.outsourcing_dict.values())
        # third_party_intermediary_values = list(Validation_vendor_doc.Third_party_intermediary_dict.values())
        # if custgrp_name == Validation_vendor_doc.OUTSOURCING:
        #     if Validation_vendor_doc.outsourcing_dict['due_deligence'] in doc_group:
        #         due_diligence = True
        #     if Validation_vendor_doc.outsourcing_dict['bcp_quest'] in doc_group:
        #         bcp_quest = True
        #     if set(outsourcing_values).issubset(doc_group):
        #         document_validation = True
        # elif custcat_name == Validation_vendor_doc.THIRD_PARTY_INTERMEDIARY:
        #     if Validation_vendor_doc.Third_party_intermediary_dict['intermediary'] in doc_group:
        #         intermediary = True
        #     if set(third_party_intermediary_values).issubset(doc_group):
        #         document_validation = True
        # else:
        #     document_validation = True
        # other mandatory
        if Validation_vendor_doc.CANCEL_CHEQUE in doc_group:
            cheque_flag = True
        if Validation_vendor_doc.GST in doc_group:
            Gst_flag = True
        if Validation_vendor_doc.PAN in doc_group:
            pan_flag = True
        if Validation_vendor_doc.BOARD_RESOLUTION in doc_group:
            board_flag = True
        if Validation_vendor_doc.CONTRACT in doc_group:
            contract_flag = True
        if document_validation == True:
            if composite is VendorCompositeUtil.UNREGISTER:
                if set(Validation_vendor_doc.MANDATORY_FIELD_UNREG).issubset(doc_group):
                    document_validation = True
                else:
                    document_validation = False
            else:
                if set(Validation_vendor_doc.MANDATORY_FIELD_REG).issubset(doc_group):
                    document_validation = True
                else:
                    document_validation = False
        # kyc, questionnaire(bcp & due)
        if custgrp_name == Validation_vendor_doc.OUTSOURCING:
            bcp = VendorGrpAnswers.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id, ques_type=Questionnaire.BCP_QUESTIONNAIRE)
            if len(bcp) != 0:
                bcp_quest = True
            due = VendorGrpAnswers.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id,
                                                                                    ques_type=Questionnaire.DUE_DILIGENCE)
            if len(due) != 0:
                due_diligence = True
            if mod_edit['modify'] == True:
                condition = Q(vendor_id=vendor_id) & (~Q(modify_status=0))
            else:
                condition = Q(vendor_id=vendor_id) & Q(modify_status=-1)
            kyc_resp = VendorKYC.objects.using(self._current_app_schema()).filter(condition)
            if len(kyc_resp) != 0:
                kyc = True
            if (bcp_quest == False) or (due_diligence == False):
                document_validation = False
        else:
            kyc = True

        validation_dict = {"vendor_doc":document_validation,"due_deligence":due_diligence,"bcp_quest":bcp_quest,
                           "intermediary":intermediary,"category":custgrp_name,"cheque":cheque_flag, "pan":pan_flag,
                           "gst":Gst_flag,"board":board_flag, "contract":contract_flag, "kyc":kyc}

        return validation_dict

    def check_branch_gst(self,vendor_id):
        gst_validate = True
        mod_edit = self.check_if_mod_edit(vendor_id)
        if mod_edit['edit'] == True:
            branch_list = SupplierBranch.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), vendor_id=vendor_id, is_validate=True)
            for branch in branch_list:
                if (branch.gstno == None) or (branch.gstno=="") or (branch.gstno=='GSTNOTAVAILABLE'):
                    new_branch_list = SupplierBranch.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), modify_ref_id=branch.id)
                    if (len(new_branch_list) !=0) and ((new_branch_list[0].gstno != None) and (new_branch_list[0].gstno != "") and (new_branch_list[0].gstno != 'GSTNOTAVAILABLE')):
                        pass
                    else:
                        gst_validate = False
                        return gst_validate
        else:
            branch_list = SupplierBranch.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),vendor_id=vendor_id,is_validate=True)
            for branch in branch_list:
                if (branch.gstno == None) or (branch.gstno=="") or (branch.gstno=='GSTNOTAVAILABLE'):
                    gst_validate = False
                    return gst_validate
        return gst_validate

    def vendor_active_payment(self, vendor_id):
        paymant_flag = False
        branch_list = SupplierBranch.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),vendor_id=vendor_id,is_validate=True).values_list('id', flat=True)
        branch_list = list(branch_list)
        payment_list = SupplierPayment.objects.using(self._current_app_schema()).filter(supplierbranch_id__in=branch_list, is_active=1, entity_id=self._entity_id(), modify_ref_id=-1)
        if len(payment_list) != 0:
            paymant_flag = True
            return paymant_flag
        else:
            modifiy_array = [ModifyStatus.create, ModifyStatus.update, ModifyStatus.active_in]
            active = SupplierPayment.objects.using(self._current_app_schema()).filter(
                supplierbranch_id__in=branch_list, is_active=1, entity_id=self._entity_id(),modify_status__in=modifiy_array)
            if len(active) != 0:
                paymant_flag = True
                return paymant_flag
        return paymant_flag

    def get_vendor_category(self, vendor_id):
        flag = False
        modify_status = self.get_modification_status(vendor_id)
        if modify_status == True:
            vendor = Vendor.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), id=vendor_id)
            new_vendor = Vendor.objects.using(self._current_app_schema()).filter(id=vendor[0].modify_ref_id)
            if len(new_vendor) == 0:
                group = vendor[0].group
                group_obj = vendorutil.getGroup(group)
                # cust_category = CustomerCategory.objects.using(
                #     self._app_schema(ApplicationNamespace.MASTER_SERVICE)).filter(
                #     id=category)
                # category_name = cust_category[0].name
                group_name = group_obj.text
            else:
                group = new_vendor[0].group
                group_obj = vendorutil.getGroup(group)
                # cust_category = CustomerCategory.objects.using(
                #     self._app_schema(ApplicationNamespace.MASTER_SERVICE)).filter(
                #     id=category)
                # category_name = cust_category[0].name
                group_name = group_obj.text
        else:
            vendor = Vendor.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), id=vendor_id)
            group = vendor[0].group
            group_obj = vendorutil.getGroup(group)
            # cust_category = CustomerCategory.objects.using(self._app_schema(ApplicationNamespace.MASTER_SERVICE)).filter(
            #     id=category)
            # category_name = cust_category[0].name
            group_name = group_obj.text
        if group_name == Validation_vendor_doc.OUTSOURCING:
            flag = True
        return flag

    def check_vendor_category(self, vendor_id):
        flag = False
        mod_status = self.get_modification_status(vendor_id)
        if mod_status == True:
            vendor = Vendor.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                             id=vendor_id)
            new_vendor = Vendor.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), id=vendor[0].modify_ref_id).order_by('created_date')
            if len(new_vendor) != 0:
                vendor_group = new_vendor[0].group
                group_obj = vendorutil.getGroup(vendor_group)
                # custcat_obj = CustomerCategory.objects.using(
                #     self._app_schema(ApplicationNamespace.MASTER_SERVICE)).filter(
                #     id=vendor_category)
                # custcat_name = custcat_obj[0].name
                group_name = group_obj.text
                if group_name == Validation_vendor_doc.OUTSOURCING:
                    flag = True
            else:
                vendor_group = vendor[0].group
                group_obj = vendorutil.getGroup(vendor_group)
                # custcat_obj = CustomerCategory.objects.using(
                #     self._app_schema(ApplicationNamespace.MASTER_SERVICE)).filter(
                #     id=vendor_category)
                # custcat_name = custcat_obj[0].name
                group_name = group_obj.text
                if group_name == Validation_vendor_doc.OUTSOURCING:
                    flag = True
        else:
            vendor = Vendor.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), id=vendor_id,modify_status=-1)
            vendor_group = vendor[0].group
            group_obj = vendorutil.getGroup(vendor_group)
            # custcat_obj = CustomerCategory.objects.using(self._app_schema(ApplicationNamespace.MASTER_SERVICE)).filter(
            #     id=vendor_category)
            # custcat_name = custcat_obj[0].name
            group_name = group_obj.text
            if group_name == Validation_vendor_doc.OUTSOURCING:
                flag = True
        return flag

    def get_active_supplier(self, vendor_id):
        mod_status = self.get_modification_status(vendor_id)
        if mod_status == True:
            supplier = SupplierBranch.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                       vendor_id=vendor_id, is_active=1,
                                                                                       modify_ref_id=-1)
            if len(supplier) == 0:
                modifiy_array = [ModifyStatus.create,ModifyStatus.update,ModifyStatus.active_in]
                active = SupplierBranch.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), vendor_id=vendor_id, modify_status__in=modifiy_array, is_active=1)
                in_active = SupplierBranch.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), vendor_id=vendor_id, modify_status__in=modifiy_array, is_active=0)

                if len(active) >= len(in_active):
                    supplier_active_flag = True
                else:
                    supplier_active_flag = False
                # for value in supplier_list:
                #     pass
                # mod_supplier = SupplierBranch.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),vendor_id=vendor_id, is_active=1, modify_status=3)
                # edit_supplier = SupplierBranch.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),vendor_id=vendor_id)
                # if len(mod_supplier) == 0:
                #     supplier_active_flag = False
                # else:
                #     supplier_active_flag = True
            else:
                supplier_active_flag = True
        else:
            supplier = SupplierBranch.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                       vendor_id=vendor_id, is_active=1,
                                                                                       modify_ref_id=-1)
            if len(supplier) == 0:
                supplier_active_flag = False
            else:
                supplier_active_flag = True
        return supplier_active_flag

    def check_if_mod_edit(self, vendor_id):
        edit = False
        new_ven = None
        if vendor_id == None:
            mod_status = False
        else:
            vendor = Vendor.objects.using(self._current_app_schema()).get(id=vendor_id, entity_id=self._entity_id())
            if vendor.requeststatus in (RequestStatusUtil.MODIFICATION, RequestStatusUtil.RENEWAL):
                mod_status = True
            else:
                mod_status = False
        if mod_status == True:
            vendor = Vendor.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                             id=vendor_id)
            new_vendor = Vendor.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                 id=vendor[0].modify_ref_id).order_by(
                'created_date')
            if len(new_vendor) != 0:
                edit = True
                new_ven = new_vendor[0]
        result = {'edit': edit, 'modify': mod_status, 'new_vendor': new_ven}
        return result

    def branch_count_flag(self, vendor_id):
        flag = False
        mod_status = self.get_modification_status(vendor_id)
        if mod_status:
            new_vendor = Vendor.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),modify_ref_id=vendor_id).order_by('created_date')
            if len(new_vendor) != 0:
                profile = VendorProfile.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),vendor_id=new_vendor[0].id)
                branch_count = int(profile[0].branch)
                old_branch = SupplierBranch.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),vendor_id=vendor_id, modify_status=-1)
                new_branch = SupplierBranch.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),vendor_id=vendor_id, modify_status=ModifyStatus.create)
                branch_length = len(old_branch)+len(new_branch)
                if branch_count <= branch_length:
                    flag = True
            else:
                profile = VendorProfile.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),vendor_id=vendor_id)
                branch_count = int(profile[0].branch)
                old_branch = SupplierBranch.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),vendor_id=vendor_id,
                                                                                             modify_status=-1)
                new_branch = SupplierBranch.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),vendor_id=vendor_id,
                                                                                             modify_status=ModifyStatus.create)
                branch_length = len(old_branch) + len(new_branch)
                if branch_count <= branch_length:
                    flag = True
        else:
            profile = VendorProfile.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),vendor_id=vendor_id)
            branch_count = int(profile[0].branch)
            supplier = SupplierBranch.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),vendor_id=vendor_id)
            if branch_count <= len(supplier):
                flag = True
        return flag

    def get_org_type(self, vendor_id, employee_id):
        is_rm = False
        mod_status = self.get_modification_status(vendor_id)
        if mod_status == True:
            vendor = Vendor.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                             id=vendor_id)
            new_vendor = Vendor.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                 id=vendor[0].modify_ref_id).order_by(
                'created_date')
            if len(new_vendor) != 0:
                vendor_org = new_vendor[0].orgtype
                vendor_rm = new_vendor[0].rm_id
                org_obj = vendorutil.getOrgType(vendor_org)
                org_name = org_obj.text
            else:
                vendor_org = vendor[0].orgtype
                vendor_rm = vendor[0].rm_id
                org_obj = vendorutil.getOrgType(vendor_org)
                org_name = org_obj.text
        else:
            vendor = Vendor.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), id=vendor_id,
                                                                             modify_status=-1)
            vendor_org = vendor[0].orgtype
            vendor_rm = vendor[0].rm_id
            org_obj = vendorutil.getOrgType(vendor_org)
            group_name = org_obj.text
            org_name = org_obj.text
        # maker and rm flag
        if vendor_rm == employee_id:
            is_rm = True
        data = {'org_name':org_name, 'vendor_rm':is_rm}
        return data

    def vendor_name_validation(self, value):
        vendor = Vendor.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), name__exact=value)
        resp = TPResponse()
        if len(vendor) > 0:
            logger.info('Error')
            resp.set_status(False)
        else:
            logger.info('Success')
            resp.set_status(True)
        return resp.get()

    def update_branch_pan(self, vendor_id, employee_id, new_pan):
        branch_list = SupplierBranch.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id, entity_id=self._entity_id(), modify_status=-1)
        for branch in branch_list:
            mod_branch = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch.modify_ref_id, entity_id=self._entity_id())
            if len(mod_branch)==0:
                contact_id = self.create_mod_bcontact(vendor_id, branch.contact_id, employee_id)
                address_id = self.create_mod_baddress(vendor_id, branch.address_id, employee_id)
                branch = self.create_mod_branch(vendor_id,branch,new_pan,employee_id,address_id,contact_id)
            else:
                update_branch = SupplierBranch.objects.using(self._current_app_schema()).filter(id=mod_branch[0].id).update(panno=new_pan)

    def create_mod_bcontact(self,vendor_id,contact_id, employee_id):
        contact_data = VendorRelContact.objects.using(self._current_app_schema()).filter(id=contact_id,entity_id=self._entity_id())
        if len(contact_data) != 0:
            contact_obj = contact_data[0]
            contact = VendorRelContact.objects.using(self._current_app_schema()).create(name=contact_obj.name,
                                                                                        designation=contact_obj.designation,
                                                                                        landline=contact_obj.landline,
                                                                                        landline2=contact_obj.landline2,
                                                                                        mobile=contact_obj.mobile,
                                                                                        mobile2=contact_obj.mobile2,
                                                                                        email=contact_obj.email,
                                                                                        dob=contact_obj.dob,
                                                                                        wedding_date=contact_obj.wedding_date,
                                                                                        created_by=employee_id,
                                                                                        modify_status=ModifyStatus.update,
                                                                                        modified_by=employee_id,
                                                                                        modify_ref_id=contact_obj.id,
                                                                                        entity_id=self._entity_id())

            contact_update = VendorRelContact.objects.using(self._current_app_schema()).filter(id=contact_obj.id,
                                                                                               entity_id=self._entity_id()).update(
                modify_ref_id=contact.id)
            VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id,
                                                                                   ref_id=contact_obj.id,
                                                                                   ref_type=VendorRefType.VENDOR_REL_CONTACT,
                                                                                   mod_status=ModifyStatus.update,
                                                                                   modify_ref_id=contact.id,
                                                                                   entity_id=self._entity_id())
            return contact.id
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj

    def create_mod_branch(self, vendor_id, branch, new_pan, employee_id, address_id, contact_id):
        create_branch = SupplierBranch.objects.using(self._current_app_schema()).create(vendor_id=vendor_id,
                                                                                        name=branch.name,
                                                                                        code=branch.code,
                                                                                        remarks=branch.remarks,
                                                                                        limitdays=branch.limitdays,
                                                                                        creditterms=branch.creditterms,
                                                                                        gstno=branch.gstno,
                                                                                        panno=new_pan,
                                                                                        address_id=address_id,
                                                                                        contact_id=contact_id,
                                                                                        created_by=branch.created_by,
                                                                                        modify_status=ModifyStatus.update,
                                                                                        modified_by=employee_id,
                                                                                        modify_ref_id=branch.id,
                                                                                        entity_id=self._entity_id())

        VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id,
                                                                               ref_id=branch.id,
                                                                               ref_type=VendorRefType.VENDOR_BRANCH,
                                                                               mod_status=ModifyStatus.update,
                                                                               modify_ref_id=create_branch.id,
                                                                               entity_id=self._entity_id())
        old_branch_update = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch.id).update(
            modify_ref_id=create_branch.id)
        vendor_check = self.branchvalidate(branch.id)
        if vendor_check == True:
            vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(
                id=branch.id, entity_id=self._entity_id()).update(
                is_validate=True)

    def create_mod_baddress(self, vendor_id, address_id, employee_id):
        address_data = VendorRelAddress.objects.using(self._current_app_schema()).filter(id=address_id,entity_id=self._entity_id())
        if len(address_data) != 0:
            address_obj = address_data[0]
            address = VendorRelAddress.objects.using(self._current_app_schema()).create(line1=address_obj.line1,
                                                                                        line2=address_obj.line2,
                                                                                        line3=address_obj.line3,
                                                                                        pincode_id=address_obj.pincode_id,
                                                                                        city_id=address_obj.city_id,
                                                                                        district_id=address_obj.district_id,
                                                                                        state_id=address_obj.state_id,
                                                                                        created_by=employee_id,
                                                                                        modify_status=ModifyStatus.update,
                                                                                        modified_by=employee_id,
                                                                                        modify_ref_id=address_obj.id,
                                                                                        entity_id=self._entity_id())

            address_update = VendorRelAddress.objects.using(self._current_app_schema()).filter(id=address_obj.id,
                                                                                               entity_id=self._entity_id()).update(
                modify_ref_id=address.id)
            VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=address.id,
                                                                                   ref_type=VendorRefType.VENDOR_REL_ADDRESS,
                                                                                   mod_status=ModifyStatus.update,
                                                                                   modify_ref_id=address.id,
                                                                                   entity_id=self._entity_id())
            return address.id
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj

    def get_old_vendor_id(self, vendor_id):
        vendor = Vendor.objects.using(self._current_app_schema()).filter(id=vendor_id,modify_status=-1, entity_id=self._entity_id())
        if len(vendor)==0:
            vendor_new = Vendor.objects.using(self._current_app_schema()).filter(id=vendor_id,
                                                                             entity_id=self._entity_id())
            if (vendor_new[0].modify_ref_id != -1) and (len(vendor_new)!=0):
                new_vendor = Vendor.objects.using(self._current_app_schema()).filter(id=vendor_new[0].modify_ref_id, entity_id=self._entity_id())
                vendor_id = new_vendor[0].id
            else:
                vendor_id = vendor[0].id
        else:
            vendor_id = vendor[0].id
        return vendor_id

    def get_contact_details(self, query, type, vys_page):
        list_data = NWisefinList()
        condition = Q(entity_id=self._entity_id())
        if (query is not None) and (query != ''):
            condition &= (Q(code__icontains=query) | Q(name__icontains=query))
        if type == 1:
            vendor_list = Vendor.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
            for vendor in vendor_list:
                resp = VendorListData()
                contact = VendorContact.objects.using(self._current_app_schema()).filter(vendor_id=vendor.id)
                resp.set_id(vendor.id)
                resp.set_code(vendor.code)
                resp.set_name(vendor.name)
                if len(contact)==0:
                    resp.email_id = None
                    resp.mobile_1 = None
                    resp.mobile_2 = None
                else:
                    resp.email_id = contact[0].email
                    resp.mobile_1 = contact[0].mobile
                    resp.mobile_2 = contact[0].mobile2
                list_data.append(resp)
            vpage = NWisefinPaginator(vendor_list, vys_page.get_index(), 10)
            list_data.set_pagination(vpage)
            return list_data
        elif type == 2:
            branch_list = SupplierBranch.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
            for branch in branch_list:
                resp = VendorListData()
                resp.set_id(branch.id)
                resp.set_code(branch.code)
                resp.set_name(branch.name)
                contact = branch.contact
                if contact ==None:
                    resp.email_id = None
                    resp.mobile_1 = None
                    resp.mobile_2 = None
                else:
                    resp.email_id = contact.email
                    resp.mobile_1 = contact.mobile
                    resp.mobile_2 = contact.mobile2
                list_data.append(resp)
            vpage = NWisefinPaginator(branch_list, vys_page.get_index(), 10)
            list_data.set_pagination(vpage)
            return list_data
        else:
            error = NWisefinError()
            error.set_code(ErrorMessage.INVALID_DATA)
            error.set_description(ErrorDescription.INVALID_DATA)
            return error

    def get_vendor_code_by_id(self, code):
        if code != '':
            vendor = Vendor.objects.using(self._current_app_schema()).filter(code=code, modify_status=-1,
                                                                             entity_id=self._entity_id())
            if len(vendor) != 0:
                return vendor[0].id
            else:
                return
        else:
            return

    def get_branch_code_by_id(self, code):
        if code != '':
            branch = SupplierBranch.objects.using(self._current_app_schema()).filter(code=code, modify_status=-1,
                                                                                     entity_id=self._entity_id())
            if len(branch) != 0:
                return branch[0].id
            else:
                return
        else:
            return

    def portal_flag_update(self, vendor_id, vendor_obj):
        vendordata = Vendor.objects.filter(id=vendor_id).update(portal_flag=vendor_obj.get_portal_flag(),
                                                         portal_code=vendor_obj.get_portal_code())

        vendor_data = Vendor.objects.get(id=vendor_id)

        print(vendor_data)



