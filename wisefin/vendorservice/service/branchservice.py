from datetime import datetime
from masterservice.models.mastermodels import State
from vendorservice.util import gst_util
import django
from django.db import IntegrityError
from django.utils.timezone import now
from masterservice.service.cityservice import CityService
from masterservice.service.stateservice import StateService
from vendorservice.data.response.vendoraddressresponse import AddressResponse
from nwisefin.settings import logger
from userservice.models import Employee
from vendorservice.data.response.supplierresponse import BranchResponse
from vendorservice.models import SupplierBranch, VendorQueue, Vendor, VendorModificationRel, VendorProfile, \
    VendorRelAddress, SupplierPayment, VendorRelContact
from vendorservice.service.profileservice import ProfileService
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from vendorservice.data.request.vendorauditrequest import VendorAuditRequest
from vendorservice.service.vendorauditservice import VendorAuditService
from vendorservice.data.response.vendorauditresponse import VendorAuditResponse
from utilityservice.service.utilityservice import NWisefinUtilityService
from django.db.models import Q
from vendorservice.util.vendorutil import VendorRefType , ModifyStatus, Code_Gen_Type
from vendorservice.service.supplierservice import AddressService , ContactService
from vendorservice.util.vendorutil import VendorStatusUtil , RequestStatusUtil
from vendorservice.service.vendorservice import VendorService
from vendorservice.models.vendormodels import Catelog , SupplierActivity , ActivityDetail
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from vendorservice.data.response.vendorlistresponse import VendorCheckListData


class branchservice(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def create_branch ( self , branch_obj , user_id , vendor_id , add_id , cont_id , address_obj ) :
        req_status = RequestStatusUtil.ONBOARD
        ven_serv = VendorService(self._scope())
        if not branch_obj.get_id ( ) is None :
            # try:
            branch_update = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_obj.get_id(),entity_id=self._entity_id()).update (
                name=branch_obj.get_name ( ) ,
                vendor_id=vendor_id ,
                remarks=branch_obj.get_remarks ( ) ,
                limitdays=branch_obj.get_limitdays ( ) ,
                creditterms=branch_obj.get_creditterms ( ) ,
                gstno=branch_obj.get_gstno ( ) ,
                panno=branch_obj.get_panno ( ) ,
                address_id=add_id ,
                contact_id=cont_id ,
                updated_by=user_id ,
                updated_date=timezone.now ( ),portal_flag=branch_obj.get_portal_flag())
            branch_auditdata = {'id' : branch_obj.get_id ( ) , 'name' : branch_obj.get_name ( ) ,
                                'vendor_id' : vendor_id ,
                                'remarks' : branch_obj.get_remarks ( ) , 'limitdays' : branch_obj.get_limitdays ( ) ,
                                'creditterms' : branch_obj.get_creditterms ( ) , 'gstno' : branch_obj.get_gstno ( ) ,
                                'panno' : branch_obj.get_panno ( ) ,
                                'address_id' : add_id , 'contact_id' : cont_id ,
                                'updated_by' : user_id , 'updated_date' : timezone.now ( )}

            branch = SupplierBranch.objects.using(self._current_app_schema()).get (id=branch_obj.get_id(), entity_id=self._entity_id())

            self.audit_function ( branch_auditdata , vendor_id , user_id , req_status , branch.id ,
                                  ModifyStatus.update )

            # except IntegrityError as error:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except SupplierBranch.DoesNotExist:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_SUPPLIERBRANCH_ID)
            #     error_obj.set_description(ErrorDescription.INVALID_SUPPLIERBRANCH_ID)
            #     return error_obj
            # except:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj
        else :
            # try:
            if (branch_obj.get_gstno ( ) != "") and (branch_obj.get_gstno() != 'GSTNOTAVAILABLE') :
                Branch = SupplierBranch.objects.using(self._current_app_schema()).filter ( gstno=branch_obj.get_gstno ( ), entity_id=self._entity_id()).exists ( )
                if Branch == True :
                    branch_table = SupplierBranch.objects.using(self._current_app_schema()).filter (gstno=branch_obj.get_gstno(), entity_id=self._entity_id())

                    for x in branch_table:
                        logger.info(str(x.address_id))
                        logger.info(str(x.vendor_id))
                    address = VendorRelAddress.objects.using(self._current_app_schema()).get(id=x.address_id, entity_id=self._entity_id())
                    state = address.state_id
                    if vendor_id == x.vendor_id:
                        if address_obj.get_state_id() == state:

                            branch = SupplierBranch.objects.using(self._current_app_schema()).create(vendor_id=vendor_id ,
                                                                     name=branch_obj.get_name(),
                                                                     remarks=branch_obj.get_remarks(),
                                                                     limitdays=branch_obj.get_limitdays(),
                                                                     creditterms=branch_obj.get_creditterms(),
                                                                     gstno=branch_obj.get_gstno(),
                                                                     panno=branch_obj.get_panno(),
                                                                     address_id=add_id,
                                                                     contact_id=cont_id,
                                                                     created_by=user_id, entity_id=self._entity_id(),portal_flag=branch_obj.get_portal_flag())
                            supplier = ven_serv.codegenerator(Code_Gen_Type.supplier, user_id)
                            code = "SU" + str(supplier)
                            branch.code = code
                            branch.save()
                            self.audit_function ( branch , vendor_id , user_id , req_status , branch.id ,
                                                  ModifyStatus.create )

                        else :
                            return "NOTVALID_GST"

                    else :
                        return "GSTEXSIST"
                else :
                    branch = SupplierBranch.objects.using(self._current_app_schema()).create ( vendor_id=vendor_id , name=branch_obj.get_name ( ) ,
                                                             remarks=branch_obj.get_remarks ( ) ,
                                                             limitdays=branch_obj.get_limitdays ( ) ,
                                                             creditterms=branch_obj.get_creditterms ( ) ,
                                                             gstno=branch_obj.get_gstno ( ) ,
                                                             panno=branch_obj.get_panno ( ) ,
                                                             address_id=add_id ,
                                                             contact_id=cont_id ,
                                                             created_by=user_id, entity_id=self._entity_id(),portal_flag=branch_obj.get_portal_flag())
                    supplier = ven_serv.codegenerator(Code_Gen_Type.supplier, user_id)
                    code = "SU" + str(supplier)
                    branch.code = code
                    branch.save()
                    self.audit_function ( branch , vendor_id , user_id , req_status , branch.id , ModifyStatus.create )

            else :
                branch = SupplierBranch.objects.using(self._current_app_schema()).create ( vendor_id=vendor_id , name=branch_obj.get_name ( ) ,
                                                         remarks=branch_obj.get_remarks ( ) ,
                                                         limitdays=branch_obj.get_limitdays ( ) ,
                                                         creditterms=branch_obj.get_creditterms ( ) ,
                                                         gstno=branch_obj.get_gstno ( ) ,
                                                         panno=branch_obj.get_panno ( ) ,
                                                         address_id=add_id ,
                                                         contact_id=cont_id ,
                                                         created_by=user_id, entity_id=self._entity_id(),portal_flag=branch_obj.get_portal_flag())
                supplier = ven_serv.codegenerator(Code_Gen_Type.supplier, user_id)
                code = "SU" + str (supplier)
                branch.code = code
                branch.save ( )

                self.audit_function ( branch , vendor_id , user_id , req_status , branch.id , ModifyStatus.create )

            # except IntegrityError as error:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj

        branch_data = BranchResponse ( )
        branch_data.set_vendor_id ( branch.vendor_id )
        branch_data.set_id ( branch.id )
        branch_data.set_name ( branch.name )
        branch_data.set_code ( branch.code )
        branch_data.set_remarks ( branch.remarks )
        branch_data.set_limitdays ( branch.limitdays )
        branch_data.set_creditterms ( branch.creditterms )
        branch_data.set_gstno ( branch.gstno )
        branch_data.set_is_active ( branch.is_active )
        branch_data.set_panno ( branch.panno )
        branch_data.set_address_id ( branch.address_id )
        branch_data.set_contact_id ( branch.contact_id )
        branch_data.set_portal_flag(branch.portal_flag)
        return branch_data

    # def fetch_branch_list(self,user_id):
    #     branchlist = SupplierBranch.objects.all()
    #     list_length = len(branchlist)
    #     logger.info(list_length)
    #     if list_length <= 0:
    #         error_obj = Error()
    #         error_obj.set_code(ErrorMessage.INVALID_SUPPLIERBRANCH_ID)
    #         error_obj.set_description(ErrorDescription.INVALID_SUPPLIERBRANCH_ID)
    #         return error_obj
    #     else:
    #         branch_list_data = VysfinList()
    #         for branch in branchlist:
    #             branch_data = BranchResponse()
    #             branch_data.set_vendor_id(branch.vendor_id)
    #             branch_data.set_id(branch.id)
    #             branch_data.set_name(branch.name)
    #             branch_data.set_remarks(branch.remarks)
    #             branch_data.set_limitdays(branch.limitdays)
    #             branch_data.set_creditterms(branch.creditterms)
    #             branch_data.set_gstno(branch.gstno)
    #             branch_data.set_panno(branch.panno)
    #             branch_data.set_address_id(branch.address_id)
    #             branch_data.set_contact_id(branch.contact_id)
    #
    #             branch_list_data.append(branch_data)
    # #        return branch_list_data
    #

    def fetch_branch_list ( self , request , vys_page , user_id , vendor_id ) :
        queue_arr = SupplierBranch.objects.using(self._current_app_schema()).filter ( vendor_id=vendor_id, entity_id=self._entity_id()).values ( 'id' )
        condition = None
        for vendor in queue_arr :
            logger.info (str(vendor))
            if condition is None :
                condition = (Q ( id__exact=vendor [ 'id' ] ) & (
                            Q ( modify_status__exact=-1 ) | Q ( modify_status__exact=0 )) & Q ( modified_by=-1 ))&Q(entity_id=self._entity_id())
            else :
                condition |= (Q ( id__exact=vendor [ 'id' ] ) & (
                            Q ( modify_status__exact=-1 ) | Q ( modify_status__exact=0 )) & Q ( modified_by=-1 ))&Q(entity_id=self._entity_id())
        if condition is not None :
            branchlist = SupplierBranch.objects.using(self._current_app_schema()).filter ( condition ).order_by ( 'created_date' ) [
                         vys_page.get_offset ( ) :vys_page.get_query_limit ( ) ]
        else :
            branchlist = [ ]

        vlist = NWisefinList ( )
        user_list = [ ]
        for vendor in branchlist :
            user_list.append ( vendor.created_by )
        user_list = set ( user_list )
        user_list = list ( user_list )
        utility_service = NWisefinUtilityService ( )
        user_list_obj = utility_service.get_user_info ( request , user_list )

        for branch in branchlist :
            branch_data = BranchResponse ( )
            branch_data.set_vendor_id ( branch.vendor_id )
            branch_data.set_id ( branch.id )
            branch_data.set_name ( branch.name )
            branch_data.set_code ( branch.code )
            branch_data.set_remarks ( branch.remarks )
            branch_data.set_limitdays ( branch.limitdays )
            branch_data.set_creditterms ( branch.creditterms )
            branch_data.set_gstno ( branch.gstno )
            branch_data.set_panno ( branch.panno )
            branch_data.set_modify_ref_id ( branch.modify_ref_id )
            branch_data.set_modify_status ( branch.modify_status )
            branch_data.set_address_id ( branch.address_id )
            branch_data.set_is_active ( branch.is_active )
            branch_data.set_contact_id ( branch.contact_id )
            branch_data.set_created_by ( branch.created_by )
            branch_data.set_portal_flag(branch.portal_flag)

            for ul in user_list_obj [ 'data' ] :
                if ul [ 'id' ] == SupplierBranch.created_by :
                    branch_data.set_created_by ( ul )
            vlist.append ( branch_data )
        vpage = NWisefinPaginator ( branchlist , vys_page.get_index ( ) , 10 )
        vlist.set_pagination ( vpage )
        return vlist

    def fetch_branch ( self , branch_id ) :
        try :
            branch = SupplierBranch.objects.using(self._current_app_schema()).get ( id=branch_id, entity_id=self._entity_id())
            branch_data = BranchResponse ( )
            branch_data.set_vendor_id ( branch.vendor_id )
            branch_data.set_id ( branch.id )
            branch_data.set_name ( branch.name )
            branch_data.set_code ( branch.code )
            branch_data.set_remarks ( branch.remarks )
            branch_data.set_limitdays ( branch.limitdays )
            branch_data.set_creditterms ( branch.creditterms )
            branch_data.set_gstno ( branch.gstno )
            branch_data.set_panno ( branch.panno )
            branch_data.set_modify_ref_id ( branch.modify_ref_id )
            branch_data.set_modify_status ( branch.modify_status )
            branch_data.set_address_id ( branch.address_id )
            branch_data.set_contact_id ( branch.contact_id )
            branch_data.set_created_by ( branch.created_by )
            branch_data.set_is_active ( branch.is_active )
            branch_data.set_portal_flag(branch.portal_flag)
            if branch.is_active == 1:
                branch_data.branch_active_status = 'Active'
            else:
                branch_data.branch_active_status = 'Inactive'
            return branch_data

        except SupplierBranch.DoesNotExist :
            error_obj = NWisefinError ( )
            error_obj.set_code ( ErrorMessage.INVALID_SUPPLIERBRANCH_ID )
            error_obj.set_description ( ErrorDescription.INVALID_SUPPLIERBRANCH_ID )
            return error_obj


    def fetch_single_supplierbranch ( self , branch_id ) :
        try :
            branch = SupplierBranch.objects.using(self._current_app_schema()).get ( id=branch_id, entity_id=self._entity_id())
            branch_data = BranchResponse ( )
            branch_data.set_vendor_id ( branch.vendor_id )
            branch_data.set_id ( branch.id )
            branch_data.set_name ( branch.name )
            branch_data.set_code ( branch.code )
            branch_data.set_remarks ( branch.remarks )
            branch_data.set_limitdays ( branch.limitdays )
            branch_data.set_creditterms ( branch.creditterms )
            branch_data.set_gstno ( branch.gstno )
            branch_data.set_panno ( branch.panno )
            branch_data.set_modify_ref_id ( branch.modify_ref_id )
            branch_data.set_modify_status ( branch.modify_status )
            branch_data.set_address_id ( branch.address_id )
            branch_data.set_contact_id ( branch.contact_id )
            branch_data.set_created_by ( branch.created_by )
            branch_data.set_is_active ( branch.is_active )
            branch_data.vendor_name=(branch.vendor.name)
            branch_data.set_portal_flag(branch.portal_flag)
            if branch.is_active == 1:
                branch_data.branch_active_status = 'Active'
            else:
                branch_data.branch_active_status = 'Inactive'
            return branch_data

        except SupplierBranch.DoesNotExist :
            error_obj = NWisefinError ( )
            error_obj.set_code ( ErrorMessage.INVALID_SUPPLIERBRANCH_ID )
            error_obj.set_description ( ErrorDescription.INVALID_SUPPLIERBRANCH_ID )
            return error_obj


    def delete_branch ( self , branch_id , vendor_id , user_id ) :

        branch = SupplierBranch.objects.using(self._current_app_schema()).get ( id=branch_id, entity_id=self._entity_id())
        contact_id = branch.contact_id
        address_id = branch.address_id

        branch = SupplierBranch.objects.using(self._current_app_schema()).filter ( id=branch_id, entity_id=self._entity_id()).delete ( )
        req_status = RequestStatusUtil.ONBOARD
        self.audit_function ( branch , vendor_id , user_id , req_status , branch_id , ModifyStatus.delete )

        address_service = AddressService (self._scope())
        address_service.delete_address ( address_id , vendor_id , user_id )
        contact_service = ContactService (self._scope())
        contact_service.delete_contact ( contact_id , vendor_id , user_id )

        if branch [ 0 ] == 0 :
            error_obj = NWisefinError ( )
            error_obj.set_code ( ErrorMessage.INVALID_SUPPLIERBRANCH_ID )
            error_obj.set_description ( ErrorDescription.INVALID_SUPPLIERBRANCH_ID )
            return error_obj
        else :
            success_obj = NWisefinSuccess ( )
            success_obj.set_status ( SuccessStatus.SUCCESS )
            success_obj.set_message ( SuccessMessage.DELETE_MESSAGE )
            return success_obj

    # VENDOR STATUS FROM BRANCH ID

    def get_vendorstatus_branch ( self , branch_id ) :
        branch = SupplierBranch.objects.using(self._current_app_schema()).get ( id=branch_id, entity_id=self._entity_id())
        vendor_id = branch.vendor_id

        vendor = Vendor.objects.using(self._current_app_schema()).get ( id=vendor_id, entity_id=self._entity_id())
        vobj = vendor.vendor_status

        return vobj

    # modification

    def modification_create_branch ( self , branch_obj , user_id , vendor_id , add_id , cont_id ) :
        req_status = RequestStatusUtil.MODIFICATION
        vendor_service = VendorService (self._scope())

        if not branch_obj.get_id ( ) is None :
            # try:
            ref_flag = vendor_service.checkmodify_rel ( VendorRefType.VENDOR_BRANCH , branch_obj.get_id ( ) )
            if ref_flag == True :
                branch = SupplierBranch.objects.using(self._current_app_schema()).filter ( id=branch_obj.get_id(), entity_id=self._entity_id()).update ( vendor_id=vendor_id ,
                                                                                             name=branch_obj.get_name ( ) ,
                                                                                             remarks=branch_obj.get_remarks ( ) ,
                                                                                             limitdays=branch_obj.get_limitdays ( ) ,
                                                                                             creditterms=branch_obj.get_creditterms ( ) ,
                                                                                             gstno=branch_obj.get_gstno ( ) ,
                                                                                             panno=branch_obj.get_panno ( ) ,
                                                                                             address_id=add_id ,
                                                                                             contact_id=cont_id ,portal_flag=branch_obj.get_portal_flag())
                branch = SupplierBranch.objects.using(self._current_app_schema()).get ( id=branch_obj.get_id ( ), entity_id=self._entity_id())
            else :

                branch = SupplierBranch.objects.using(self._current_app_schema()).create ( vendor_id=vendor_id , name=branch_obj.get_name ( ) ,
                                                         code=branch_obj.get_code ( ) ,
                                                         remarks=branch_obj.get_remarks ( ) ,
                                                         limitdays=branch_obj.get_limitdays ( ) ,
                                                         creditterms=branch_obj.get_creditterms ( ) ,
                                                         gstno=branch_obj.get_gstno ( ) ,
                                                         panno=branch_obj.get_panno ( ) , address_id=add_id ,
                                                         contact_id=cont_id ,
                                                         created_by=user_id , modify_status=ModifyStatus.update ,
                                                         modified_by=user_id ,
                                                         modify_ref_id=branch_obj.get_id ( ), entity_id=self._entity_id(),portal_flag=branch_obj.get_portal_flag())

                branch_update = SupplierBranch.objects.using(self._current_app_schema()).filter ( id=branch_obj.get_id(), entity_id=self._entity_id()).update (
                    modify_ref_id=branch.id )
                branchupdate_auditdata = {'id' : branch_obj.get_id ( ) , 'modify_ref_id' : branch.id}

                VendorModificationRel.objects.using(self._current_app_schema()).create ( vendor_id=vendor_id , ref_id=branch_obj.get_id ( ) ,
                                                       ref_type=VendorRefType.VENDOR_BRANCH ,
                                                       mod_status=ModifyStatus.update ,
                                                       modify_ref_id=branch.id, entity_id=self._entity_id())

            vendor_check = vendor_service.branchvalidate ( branch_obj.get_id ( ) )
            if vendor_check == True :
                vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter ( id=branch_obj.get_id(), entity_id=self._entity_id()).update (
                    is_validate=True )

            # branch = SupplierBranch.objects.get(id=branch_obj.get_id())
            branch_update_id = branch_obj.get_id ( )
            self.audit_function ( branch , vendor_id , user_id , req_status , branch.id , ModifyStatus.create )


        else :
            # try:
            branch = SupplierBranch.objects.using(self._current_app_schema()).create ( vendor_id=vendor_id , name=branch_obj.get_name ( ) ,
                                                     remarks=branch_obj.get_remarks ( ) ,
                                                     limitdays=branch_obj.get_limitdays ( ) ,
                                                     code=branch_obj.get_code ( ) ,
                                                     creditterms=branch_obj.get_creditterms ( ) ,
                                                     gstno=branch_obj.get_gstno ( ) ,
                                                     panno=branch_obj.get_panno ( ) , address_id=add_id ,
                                                     contact_id=cont_id ,
                                                     created_by=user_id , modify_status=ModifyStatus.create ,
                                                     modified_by=user_id, entity_id=self._entity_id(), portal_flag=branch_obj.get_portal_flag())

            branch.modify_ref_id = branch.id
            ven_serv = VendorService(self._scope())
            supplier = ven_serv.codegenerator(Code_Gen_Type.supplier, user_id)
            code = "SU" + str(supplier)
            branch.code = code
            branch.save()
            # branch.modify_ref_id = branch.id
            #
            # code = "SU" + str ( branch.id )
            # branch.code = code
            # branch.save ( )
            logger.info (str(branch))

            VendorModificationRel.objects.using(self._current_app_schema()).create ( vendor_id=vendor_id , ref_id=branch.id ,
                                                   ref_type=VendorRefType.VENDOR_BRANCH ,
                                                   mod_status=ModifyStatus.create ,
                                                   modify_ref_id=branch.id, entity_id=self._entity_id())
            vendor_check = vendor_service.branchvalidate ( branch.id )
            if vendor_check == True :
                vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter ( id=branch.id, entity_id=self._entity_id()).update ( is_validate=True )

            self.audit_function ( branch , vendor_id , user_id , req_status , branch.id , ModifyStatus.create )

        branch_data = BranchResponse ( )
        branch_data.set_vendor_id ( branch.vendor_id )
        branch_data.set_id ( branch.id )
        branch_data.set_name ( branch.name )
        branch_data.set_code ( branch.code )
        branch_data.set_remarks ( branch.remarks )
        branch_data.set_limitdays ( branch.limitdays )
        branch_data.set_creditterms ( branch.creditterms )
        branch_data.set_gstno ( branch.gstno )
        branch_data.set_panno ( branch.panno )
        branch_data.set_address_id ( branch.address_id )
        branch_data.set_contact_id ( branch.contact_id )
        branch_data.set_is_active ( branch.is_active )
        branch_data.set_portal_flag(branch.portal_flag)
        return branch_data

    def modification_delete_branch ( self , branch_id , vendor_id , user_id ) :
        try :
            vendor_service = VendorService (self._scope())
            ref_flag = vendor_service.checkmodify_rel ( VendorRefType.VENDOR_BRANCH , branch_id )
            branch = SupplierBranch.objects.using(self._current_app_schema()).get ( id=branch_id, entity_id=self._entity_id())
            vendor_check = vendor_service.branchvalidate ( branch_id )
            if vendor_check == True :
                vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter ( id=branch_id, entity_id=self._entity_id()).update ( is_validate=True )

            branch_update = SupplierBranch.objects.using(self._current_app_schema()).filter ( id=branch_id, entity_id=self._entity_id()).update (
                modify_ref_id=branch_id , modify_status=ModifyStatus.delete )
            if ref_flag == True :
                VendorModificationRel.objects.using(self._current_app_schema()).filter (
                    Q ( ref_type=VendorRefType.VENDOR_BRANCH ) & Q ( modify_ref_id=branch_id )&Q(entity_id=self._entity_id())).update (
                    mod_status=ModifyStatus.delete )
            else :
                VendorModificationRel.objects.using(self._current_app_schema()).create ( vendor_id=vendor_id , ref_id=branch_id ,
                                                       ref_type=VendorRefType.VENDOR_BRANCH ,
                                                       mod_status=ModifyStatus.delete ,
                                                       modify_ref_id=branch_id, entity_id=self._entity_id())
            # audit
            req_status = RequestStatusUtil.MODIFICATION
            # self.audit_function(branch_update, vendor_id, user_id, req_status, branch_id, ModifyStatus.update)

            contact_id = branch.contact_id
            address_id = branch.address_id

            address_service = AddressService (self._scope())
            address_service.modification_delete_address ( address_id , vendor_id , user_id )

            contact_service = ContactService (self._scope())
            contact_service.modification_delete_contact ( contact_id , vendor_id , user_id )

            success_obj = NWisefinSuccess ( )
            success_obj.set_status ( SuccessStatus.SUCCESS )
            success_obj.set_message ( SuccessMessage.DELETE_MESSAGE )
            return success_obj
        except :
            error_obj = NWisefinError ( )
            error_obj.set_code ( ErrorMessage.UNEXPECTED_ERROR )
            error_obj.set_description ( ErrorDescription.UNEXPECTED_ERROR )
            return error_obj

    def modification_action_branch ( self , mod_status , old_id , new_id , vendor_id , user_id ) :

        req_status = RequestStatusUtil.MODIFICATION
        vendor_old_id = self.get_contact_address_id ( old_id )
        vendor_new_id = self.get_contact_address_id ( new_id )
        address_service = AddressService (self._scope())
        address_service.modification_action_address ( mod_status , vendor_old_id.address_id ,
                                                      vendor_new_id.address_id , vendor_id , user_id )
        contact_service = ContactService (self._scope())
        contact_service.modification_action_contact ( mod_status , vendor_old_id.contact_id ,
                                                      vendor_new_id.contact_id , vendor_id , user_id )

        if mod_status == ModifyStatus.update :
            branch_obj = self.fetch_branch ( new_id )

            branch_update = SupplierBranch.objects.using(self._current_app_schema()).filter ( id=old_id,entity_id=self._entity_id()).update ( name=branch_obj.get_name ( ) ,
                                                                                 remarks=branch_obj.get_remarks ( ) ,
                                                                                 limitdays=branch_obj.get_limitdays ( ) ,
                                                                                 code=branch_obj.get_code ( ) ,
                                                                                 creditterms=branch_obj.get_creditterms ( ) ,
                                                                                 gstno=branch_obj.get_gstno ( ) ,
                                                                                 panno=branch_obj.get_panno ( ) ,
                                                                                 modify_status=-1 , modified_by=-1,
                                                                                 modify_ref_id=-1, portal_flag=branch_obj.get_portal_flag())

            # audit
            self.audit_function ( branch_update , vendor_id , user_id , req_status , old_id , ModifyStatus.update )
            # self.audit_function(branch, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)
        elif mod_status == ModifyStatus.create :
            # branch_check=branch_modification_count_check
            branch = SupplierBranch.objects.using(self._current_app_schema()).filter ( id=new_id, entity_id=self._entity_id()).update ( modify_status=-1 ,
                                                                          modify_ref_id=-1 , modified_by=-1 )
            # audit
            self.audit_function ( branch , vendor_id , user_id , req_status , new_id , ModifyStatus.update )
        elif mod_status == ModifyStatus.active_in :
            branch_obj = self.fetch_branch ( new_id )

            branch_update = SupplierBranch.objects.using(self._current_app_schema()).filter ( id=old_id, entity_id=self._entity_id()).update ( is_active=branch_obj.is_active ,
                                                                                 modify_status=-1 , modified_by=-1 ,
                                                                                 modify_ref_id=-1,portal_flag=branch_obj.get_portal_flag())

            # audit
            self.audit_function ( branch_update , vendor_id , user_id , req_status , old_id , ModifyStatus.active_in )

        else :

            branch = SupplierBranch.objects.using(self._current_app_schema()).filter ( id=old_id, entity_id=self._entity_id()).delete ( )
            # audit
            self.audit_function ( branch , vendor_id , user_id , req_status , old_id , ModifyStatus.delete )

        return

    def modification_reject_branch ( self , mod_status , old_id , new_id , vendor_id , user_id ) :

        req_status = RequestStatusUtil.MODIFICATION
        vendor_old_id = self.get_contact_address_id ( old_id )
        vendor_new_id = self.get_contact_address_id ( new_id )
        address_service = AddressService (self._scope())
        address_service.modification_reject_address ( mod_status , vendor_old_id.address_id ,
                                                      vendor_new_id.address_id , vendor_id , user_id )
        contact_service = ContactService (self._scope())
        contact_service.modification_reject_contact ( mod_status , vendor_old_id.contact_id ,
                                                      vendor_new_id.contact_id , vendor_id , user_id )

        if mod_status == ModifyStatus.update :
            branch_delete = SupplierBranch.objects.using(self._current_app_schema()).filter ( id=new_id, entity_id=self._entity_id()).delete ( )
            branch = SupplierBranch.objects.using(self._current_app_schema()).filter ( id=old_id, entity_id=self._entity_id()).update ( modify_ref_id=-1 )
            # audit
            self.audit_function ( branch_delete , vendor_id , user_id , req_status , new_id , ModifyStatus.delete )
            self.audit_function ( branch , vendor_id , user_id , req_status , old_id , ModifyStatus.update )
        elif mod_status == ModifyStatus.active_in :
            branch_delete = SupplierBranch.objects.using(self._current_app_schema()).filter ( id=new_id, entity_id=self._entity_id()).delete ( )
            branch = SupplierBranch.objects.using(self._current_app_schema()).filter ( id=old_id, entity_id=self._entity_id()).update ( modify_ref_id=-1 )
            # audit
            self.audit_function ( branch_delete , vendor_id , user_id , req_status , new_id , ModifyStatus.delete )
            self.audit_function ( branch , vendor_id , user_id , req_status , old_id , ModifyStatus.active_in )
        elif mod_status == ModifyStatus.create :
            branch = SupplierBranch.objects.using(self._current_app_schema()).filter ( id=new_id, entity_id=self._entity_id()).delete ( )
            # audit
            self.audit_function ( branch , vendor_id , user_id , req_status , new_id , ModifyStatus.delete )
        else :
            branch = SupplierBranch.objects.using(self._current_app_schema()).filter ( id=old_id, entity_id=self._entity_id()).update ( modify_ref_id=-1 )
            # audit
            self.audit_function ( branch , vendor_id , user_id , req_status , old_id , ModifyStatus.update )

        return

    def audit_function ( self , branch , vendor_id , user_id , req_status , id , action ) :

        if action == ModifyStatus.delete :
            data = None
        elif action == ModifyStatus.update :
            data = branch
        elif action == ModifyStatus.active_in :
            data = branch
        else :
            data = branch.__dict__
            del data [ '_state' ]
        audit_service = VendorAuditService(self._scope())
        audit_obj = VendorAuditResponse()
        audit_obj.set_refid ( vendor_id )
        audit_obj.set_reftype ( VendorRefType.VENDOR )
        audit_obj.set_userid ( user_id )
        audit_obj.set_reqstatus ( req_status )
        audit_obj.set_relrefid ( id )
        audit_obj.set_relreftype ( VendorRefType.VENDOR_BRANCH )
        audit_obj.set_action ( action )
        audit_obj.set_data ( data )
        audit_service.create_vendoraudit ( audit_obj )

        return

    def get_contact_address_id ( self , branch_id ) :
        branch = SupplierBranch.objects.using(self._current_app_schema()).get ( id=branch_id, entity_id=self._entity_id())

        branch_data = BranchResponse ( )
        branch_data.set_address_id ( branch.address_id )
        branch_data.set_contact_id ( branch.contact_id )

        return branch_data

    def branch_modification_count_check ( self , vendor_id ) :
        try :
            vendor_newobj = Vendor.objects.using(self._current_app_schema()).get ( id=vendor_id, entity_id=self._entity_id())
            vendorprofile_mod_status = VendorModificationRel.objects.using(self._current_app_schema()).get ( ref_type=VendorRefType.VENDOR_PROFILE ,
                                                                           vendor_id=vendor_newobj.modify_ref_id, entity_id=self._entity_id())
        except :
            vendorprofile_mod_status = None

        if not vendorprofile_mod_status is None :
            vendor_newid = vendorprofile_mod_status.modify_ref_id
            branch_count = VendorProfile.objects.using(self._current_app_schema()).get ( id=vendor_newid,entity_id=self._entity_id()).branch
        else :
            branch_count = VendorProfile.objects.using(self._current_app_schema()).get ( vendor_id=vendor_id, entity_id=self._entity_id()).branch

        try :
            branch_mod_status = VendorModificationRel.objects.using(self._current_app_schema()).get ( ref_type=VendorRefType.VENDOR_BRANCH ,
                                                                    mod_status=ModifyStatus.update ,
                                                                    vendor_id=vendor_id, entity_id=self._entity_id())
        except :
            branch_mod_status = None
        condition = Q(is_active=1)
        if not branch_mod_status is None :
            branch_old_id = branch_mod_status.ref_id
            condition &= (Q ( vendor_id=vendor_id ) & (Q ( modify_status=1 ) | Q ( modify_status=-1 ))) &Q(entity_id=self._entity_id())
            active_branch = SupplierBranch.objects.using(self._current_app_schema()).filter ( condition )
        else :
            condition &= (Q ( vendor_id=vendor_id ) & (Q ( modify_status=1 ) | Q ( modify_status=-1 )))&Q(entity_id=self._entity_id())
            active_branch = SupplierBranch.objects.using(self._current_app_schema()).filter ( condition )

        active_branch_length = len ( active_branch )

        if branch_count > active_branch_length :
            branch_check = True
        else :
            branch_check = False
        return branch_check

    def branch_count_check ( self , vendor_id ) :
        branch_count = VendorProfile.objects.using(self._current_app_schema()).get ( vendor_id=vendor_id, entity_id=self._entity_id()).branch
        active_branch = SupplierBranch.objects.using(self._current_app_schema()).filter ( vendor_id=vendor_id , modify_ref_id=-1, entity_id=self._entity_id())
        active_branch_count = len ( active_branch )
        if branch_count > active_branch_count :
            branch_check = True
        else :
            branch_check = False
        logger.info (str(branch_check))
        return branch_check

    def pendingbranch_list ( self , request , vys_page , user_id , vendor_id ) :

        branchlist = SupplierBranch.objects.using(self._current_app_schema()).filter (
            Q ( vendor_id=vendor_id ) & Q ( is_validate=False ) & Q ( status=1 ) &Q(entity_id=self._entity_id())).order_by ( 'created_date' ) [
                     vys_page.get_offset ( ) :vys_page.get_query_limit ( ) ]
        vlist = NWisefinList ( )
        user_list = [ ]
        if len ( branchlist ) == 0 :
            branchlist = [ ]
        else :

            for vendor in branchlist :
                user_list.append ( vendor.created_by )
            user_list = set ( user_list )
            user_list = list ( user_list )
            utility_service = NWisefinUtilityService ( )
            user_list_obj = utility_service.get_user_info ( request , user_list )

            for branch in branchlist :
                branch_data = BranchResponse ( )
                branch_data.set_vendor_id ( branch.vendor_id )
                branch_data.set_id ( branch.id )
                branch_data.set_name ( branch.name )
                branch_data.set_code ( branch.code )
                branch_data.set_remarks ( branch.remarks )
                branch_data.set_limitdays ( branch.limitdays )
                branch_data.set_creditterms ( branch.creditterms )
                branch_data.set_gstno ( branch.gstno )
                branch_data.set_panno ( branch.panno )
                branch_data.set_modify_ref_id ( branch.modify_ref_id )
                branch_data.set_modify_status ( branch.modify_status )
                branch_data.set_address_id ( branch.address_id )
                branch_data.set_contact_id ( branch.contact_id )
                branch_data.set_created_by ( branch.created_by )
                branch_data.set_is_active ( branch.is_active )
                branch_data.set_portal_flag(branch.portal_flag)
                for ul in user_list_obj [ 'data' ] :
                    if ul [ 'id' ] == SupplierBranch.created_by :
                        branch_data.set_created_by ( ul )
                vlist.append ( branch_data )
            vpage = NWisefinPaginator ( branchlist , vys_page.get_index ( ) , 10 )
            vlist.set_pagination ( vpage )
            return vlist

    def landlordbranch_list ( self , vys_page , user_id , query ) :
        condition = Q ( modify_status=-1 ) &Q(entity_id=self._entity_id())
        if query != None :
            condition &= (Q ( name__icontains=query ) | Q ( code__icontains=query ))
            branchlist = SupplierBranch.objects.using(self._current_app_schema()).filter ( condition ).order_by ( 'created_date' ) [
                         vys_page.get_offset ( ) :vys_page.get_query_limit ( ) ]
        else :
            branchlist = SupplierBranch.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by ( 'created_date' ) [
                         vys_page.get_offset ( ) :vys_page.get_query_limit ( ) ]
        vlist = NWisefinList ( )
        if len ( branchlist ) != 0 :
            for branch in branchlist :
                branch_data = BranchResponse ( )
                branch_data.set_id ( branch.id )
                branch_data.set_vendor_id ( branch.vendor_id )
                branch_data.set_name ( branch.name )
                branch_data.set_code ( branch.code )
                vlist.append ( branch_data )
            vpage = NWisefinPaginator ( branchlist , vys_page.get_index ( ) , 10 )
            vlist.set_pagination ( vpage )
        return vlist

    def get_check ( self , branch_obj , vendor_id ) :
        Branch = SupplierBranch.objects.using(self._current_app_schema()).filter ( gstno=branch_obj.get_gstno(), entity_id=self._entity_id()).exists ( )
        if Branch == True :
            branch_table = SupplierBranch.objects.using(self._current_app_schema()).filter ( gstno=branch_obj.get_gstno(), entity_id=self._entity_id())
            for x in branch_table :
                logger.info (str(x.address_id))
                logger.info (str(x.vendor_id))
            address = VendorRelAddress.objects.using(self._current_app_schema()).get ( id=x.address_id, entity_id=self._entity_id())
            state = address.state_id
            if vendor_id == x.vendor_id :
                if branch_obj.get_state_id ( ) == state :
                    return 'VALID_GST'
                else :
                    return 'NOTVALID_GST'
            else :
                return 'GSTEXSIST'
        else :
            return 'VALID_GST'

    def get_branch_modification_count ( self , vendor_id ) :
        try :
            vendor_newobj = Vendor.objects.using(self._current_app_schema()).get ( id=vendor_id, entity_id=self._entity_id())
            vendorprofile_mod_status = VendorModificationRel.objects.using(self._current_app_schema()).get ( ref_type=VendorRefType.VENDOR_PROFILE ,
                                                                           vendor_id=vendor_newobj.modify_ref_id, entity_id=self._entity_id())
        except :
            vendorprofile_mod_status = None
        if not vendorprofile_mod_status is None :
            vendor_newid = vendorprofile_mod_status.modify_ref_id
            branch_count = VendorProfile.objects.using(self._current_app_schema()).get ( id=vendor_newid, entity_id=self._entity_id()).branch
        else :
            branch_count = VendorProfile.objects.using(self._current_app_schema()).get ( vendor_id=vendor_id, entity_id=self._entity_id()).branch
        try :
            branch_mod_status = VendorModificationRel.objects.using(self._current_app_schema()).get ( ref_type=VendorRefType.VENDOR_BRANCH ,
                                                                    mod_status=ModifyStatus.update ,
                                                                    vendor_id=vendor_id, entity_id=self._entity_id())
        except :
            branch_mod_status = None
        if not branch_mod_status is None :
            branch_old_id = branch_mod_status.ref_id
            condition = (Q ( vendor_id=vendor_id ) & (Q ( modify_status__in=[1,-1,3] )))&Q(entity_id=self._entity_id(), is_active=1)
            active_branch = SupplierBranch.objects.using(self._current_app_schema()).filter ( condition )
        else :
            condition = (Q ( vendor_id=vendor_id ) & (Q ( modify_status__in = [1,-1,3] )))&Q(entity_id=self._entity_id(), is_active=1)
            active_branch = SupplierBranch.objects.using(self._current_app_schema()).filter ( condition )
        count = 0
        for branch in active_branch:
            if branch.modify_ref_id != -1:
                if branch.modify_status == 3:
                    mod_branch = SupplierBranch.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), is_active=0,id=branch.modify_ref_id)
                    if len(mod_branch) != 0:
                        count = count + 1
                else:
                    mod_branch = SupplierBranch.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), is_active= 0, id=branch.modify_ref_id)
                    if len(mod_branch) == 0:
                        count = count + 1
            else:
                count = count + 1
        # active_branch_length = len ( count )
        if branch_count == count:
            branch_check = True
        else :
            branch_check = False
        return branch_check

    def get_branch_count ( self , vendor_id ) :
        branch_count = VendorProfile.objects.using(self._current_app_schema()).get ( vendor_id=vendor_id, entity_id=self._entity_id()).branch
        active_branch = SupplierBranch.objects.using(self._current_app_schema()).filter ( vendor_id=vendor_id , modify_ref_id=-1, entity_id=self._entity_id())
        active_branch_count = len ( active_branch )
        if branch_count == active_branch_count :
            branch_check = True
        else :
            branch_check = False
        logger.info (str(branch_check))
        return branch_check

    # def updatebranch ( self , branchdata , employee_id , mod_status ) :
    #     vendor_service = VendorService ( )
    #     if mod_status == False :
    #         ref_flag = vendor_service.checkmodify_rel ( VendorRefType.VENDOR_BRANCH , branchdata [ 'branch_id' ] )
    #         if ref_flag == True :
    #             branch = SupplierBranch.objects.filter ( id=branchdata [ 'branch_id' ] ).update (
    #                 status=branchdata [ 'status' ] )
    #             branch = SupplierBranch.objects.get ( id=branchdata [ 'branch_id' ] )
    #         else :
    #             branch_obj = SupplierBranch.objects.get ( id=branchdata [ 'branch_id' ] )
    #
    #             branch = SupplierBranch.objects.create ( vendor_id=branchdata [ 'vendor_id' ] ,
    #                                                      name=branch_obj.get_name ( ) ,
    #                                                      code=branch_obj.get_code ( ) ,
    #                                                      remarks=branch_obj.get_remarks ( ) ,
    #                                                      limitdays=branch_obj.get_limitdays ( ) ,
    #                                                      creditterms=branch_obj.get_creditterms ( ) ,
    #                                                      gstno=branch_obj.get_gstno ( ) ,
    #                                                      panno=branch_obj.get_panno ( ) , address_id=add_id ,
    #                                                      contact_id=cont_id ,
    #                                                      created_by=user_id , modify_status=ModifyStatus.update ,
    #                                                      modified_by=user_id ,
    #                                                      modify_ref_id=branch_obj.get_id ( ) )
    #
    #             branch_update = SupplierBranch.objects.filter ( id=branch_obj.get_id ( ) ).update (
    #                 modify_ref_id=branch.id )
    #             branchupdate_auditdata = {'id' : branch_obj.get_id ( ) , 'modify_ref_id' : branch.id}
    #
    #             VendorModificationRel.objects.create ( vendor_id=vendor_id , ref_id=branch_obj.get_id ( ) ,
    #                                                    ref_type=VendorRefType.VENDOR_BRANCH ,
    #                                                    mod_status=ModifyStatus.update ,
    #                                                    modify_ref_id=branch.id )
    #
    #         vendor_check = vendor_service.branchvalidate ( branch_obj.get_id ( ) )
    #         if vendor_check == True :
    #             vendor_branchupdate = SupplierBranch.objects.filter ( id=branch_obj.get_id ( ) ).update (
    #                 is_validate=True )
    #
    #         # branch = SupplierBranch.objects.get(id=branch_obj.get_id())
    #         branch_update_id = branch_obj.get_id ( )
    #         self.audit_function ( branch , vendor_id , user_id , req_status , branch.id , ModifyStatus.create )
    #         # self.audit_function(branchupdate_auditdata, vendor_id, user_id, req_status, branch_update_id,
    #         #                     ModifyStatus.update)
    #
    #
    #     else :
    #         branch_update = SupplierBranch.objects.filter ( id=branchdata [ 'branch_id' ] ).update (
    #             status=branchdata [ 'status' ] , updated_date=timezone.now ( ) )
    #         branch_auditdata = {'id' : branchdata [ 'branch_id' ] , 'status' : branchdata [ 'status' ] ,
    #                             'updated_by' : employee_id , 'updated_date' : timezone.now ( )}
    #
    #         branch = SupplierBranch.objects.get ( id=branchdata [ 'branch_id' ] )
    #
    #         self.audit_function ( branch_auditdata , branchdata [ 'vendor_id' ] , employee_id , 1 , branch.id ,
    #                               ModifyStatus.update )

    def fetch_productdts ( self , product_id , dts , vys_page , employee_id , query ) :
        currentdate = datetime.strftime ( now ( ) , '%Y-%m-%d' )

        # condition=Q(productname=product_id)&Q(direct_to=dts)
        condition = Q ( productname=product_id ) & Q ( direct_to=dts ) \
                    & Q ( activitydetail_id__activity_id__branch_id__vendor_id__vendor_status=5 ) & \
                    Q ( activitydetail_id__activity_id__branch_id__vendor_id__mainstatus=2 ) \
                    & Q ( todate__gte=currentdate )&Q(entity_id=self._entity_id())
        if query is not None :
            condition &= Q ( activitydetail_id__activity_id__branch_id__name__icontains=query )
        catelog_obj = Catelog.objects.using(self._current_app_schema()).filter ( condition ) [ vys_page.get_offset ( ) :vys_page.get_query_limit ( ) ]
        vlist = NWisefinList ( )
        for catelog in catelog_obj :
            branch_name = catelog.activitydetail.activity.branch.name
            branch_code = catelog.activitydetail.activity.branch.code
            branch_id = catelog.activitydetail.activity.branch.id
            code_name = '(' + branch_code + ') ' + branch_name
            branc_resaponse = BranchResponse ( )
            branc_resaponse.set_id ( branch_id )
            branc_resaponse.set_name ( code_name )
            vlist.append ( branc_resaponse )
            vpage = NWisefinPaginator ( catelog_obj , vys_page.get_index ( ) , 10 )
            vlist.set_pagination ( vpage )
        return vlist

    def fetch_product_catalog ( self , product_id , dts , catalog_name , vys_page , employee_id , query ) :
        currentdate = datetime.strftime ( now ( ) , '%Y-%m-%d' )
        # condition=Q(productname=product_id)&Q(direct_to=dts)&Q(name=catalog_name)
        condition = Q ( productname=product_id ) & Q ( direct_to=dts ) & Q ( name=catalog_name ) \
                    & (Q ( activitydetail_id__activity_id__branch_id__vendor_id__vendor_status=5 ) | Q (
            activitydetail_id__activity_id__branch_id__vendor_id__vendor_status=1 )) & \
                    Q ( activitydetail_id__activity_id__branch_id__vendor_id__mainstatus=2 ) \
                    & Q ( todate__gte=currentdate )&Q(entity_id=self._entity_id())

        if query is not None :
            condition &= Q ( activitydetail_id__activity_id__branch_id__name__icontains=query )
        catelog_obj = Catelog.objects.using(self._current_app_schema()).filter ( condition ) [ vys_page.get_offset ( ) :vys_page.get_query_limit ( ) ]
        vlist = NWisefinList ( )
        for catelog in catelog_obj :
            branch_name = catelog.activitydetail.activity.branch.name
            branch_code = catelog.activitydetail.activity.branch.code
            branch_id = catelog.activitydetail.activity.branch.id
            code_name = '(' + branch_code + ') ' + branch_name
            branc_resaponse = BranchResponse ( )
            branc_resaponse.set_id ( branch_id )
            branc_resaponse.set_name ( code_name )
            branc_resaponse.unit_price = catelog.unitprice
            vlist.append ( branc_resaponse )
            vpage = NWisefinPaginator ( catelog_obj , vys_page.get_index ( ) , 10 )
            vlist.set_pagination ( vpage )
        return vlist

    def fetch_catalogproduct_supplier ( self , product_id , dts , catalog_name , vys_page , employee_id , query ) :
        currentdate = datetime.strftime ( now ( ) , '%Y-%m-%d' )
        condition = Q ( productname__in=product_id ) & Q ( direct_to=dts ) & Q ( name__in=catalog_name ) &Q(entity_id=self._entity_id())
        if (query == '') | (query is None) :
            condition &= Q ( status=1 ) & (
                        Q ( activitydetail_id__activity_id__branch_id__vendor_id__vendor_status=5 ) | Q (
                    activitydetail_id__activity_id__branch_id__vendor_id__vendor_status=1 )) & \
                         Q ( activitydetail_id__activity_id__branch_id__vendor_id__mainstatus=2 ) \
                         & Q ( todate__gte=currentdate )
        else :
            condition &= Q ( activitydetail_id__activity_id__branch_id__name__icontains=query ) & Q ( status=1 ) \
                         & (Q ( activitydetail_id__activity_id__branch_id__vendor_id__vendor_status=5 ) | Q (
                activitydetail_id__activity_id__branch_id__vendor_id__vendor_status=1 )) & \
                         Q ( activitydetail_id__activity_id__branch_id__vendor_id__mainstatus=2 ) \
                         & Q ( todate__gte=currentdate )

        # catelog_obj=Catelog.objects.filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
        catelog_obj = Catelog.objects.using(self._current_app_schema()).filter ( condition )
        vlist = NWisefinList ( )
        for catelog in catelog_obj :
            branch_name = catelog.activitydetail.activity.branch.name
            branch_code = catelog.activitydetail.activity.branch.code
            branch_id = catelog.activitydetail.activity.branch.id
            code_name = '(' + branch_code + ') ' + branch_name
            branc_resaponse = BranchResponse ( )
            branc_resaponse.set_id ( branch_id )
            branc_resaponse.set_name ( code_name )
            branc_resaponse.unit_price = catelog.unitprice
            vlist.append ( branc_resaponse )
            # vpage = VysfinPaginator(catelog_obj, vys_page.get_index(), 10)
            # vlist.set_pagination(vpage)
        return vlist

    def search_suppliername ( self , vys_page , query ) :
        sup_id = query.get ( 'sup_id' )
        name = query.get ( 'name' )
        if sup_id != '' :
            condition = (Q ( id=sup_id ) & Q ( name__icontains=name ) & (
                        Q ( vendor_id__vendor_status=5 ) | Q ( vendor_id__vendor_status=1 )) & Q (
                vendor_id__mainstatus=2 ) & Q ( status=1 ) &Q(vendor_id__entity_id=self._entity_id()))&Q(entity_id=self._entity_id()) &Q(is_active=1) &Q(modify_status=-1)
        if sup_id == '' :
            condition = (Q ( name__icontains=name ) & (
                        Q ( vendor_id__vendor_status=5 ) | Q ( vendor_id__vendor_status=1 )) & Q (
                vendor_id__mainstatus=2 ) & Q ( status=1 ) &Q(vendor_id__entity_id=self._entity_id()))&Q(entity_id=self._entity_id()) &Q(is_active=1) &Q(modify_status=-1)
        branchlist = SupplierBranch.objects.using(self._current_app_schema()).filter ( condition ) [
                     vys_page.get_offset ( ) :vys_page.get_query_limit ( ) ]
        list_length = len ( branchlist )
        supplier_list_data = NWisefinList ( )
        if list_length > 0 :
            for branch in branchlist :
                payment = SupplierPayment.objects.using(self._current_app_schema()).filter(supplierbranch_id=branch.id,
                                                                                           is_active=True, modify_status=-1)
                if len(payment) != 0:
                    branch_data = BranchResponse ( )
                    branch_data.set_id ( branch.id )
                    branch_data.set_name ( branch.name )
                    supplier_list_data.append ( branch_data )
            vpage = NWisefinPaginator ( branchlist , vys_page.get_index ( ) , 10 )
            supplier_list_data.set_pagination ( vpage )
        return supplier_list_data

    def supplierbranch ( self , vys_page , sup_id , emp_id ) :
        condition = Q ( id=sup_id ) & Q ( status=1 ) &Q(entity_id=self._entity_id())
        branch = SupplierBranch.objects.using(self._current_app_schema()).get ( condition )
        branch_data = BranchResponse ( )
        branch_data.set_id ( branch.id )
        branch_data.set_name ( branch.name )
        branch_data.set_code ( branch.code )
        branch_data.set_gstno ( branch.gstno )
        branch_data.set_panno ( branch.panno )
        branch_data.set_is_active ( branch.is_active )
        branch_data.set_portal_flag(branch.portal_flag)
        address = VendorRelAddress.objects.using(self._current_app_schema()).get ( id=branch.address_id, entity_id=self._entity_id())
        add_data = AddressResponse ( )
        add_data.set_line1 ( address.line1 )
        add_data.set_line2 ( address.line2 )
        add_data.set_line3 ( address.line3 )

        city_service = CityService (self._scope())
        city = city_service.fetch_city ( address.city_id , emp_id )
        add_data.set_city_id ( city )

        state_service = StateService (self._scope())
        state_id = state_service.fetchstate ( address.state_id )
        add_data.set_state_id ( state_id )
        branch_data.set_address_id ( add_data )
        return branch_data

    def search_supplier_list ( self , query , vys_page , emp_id ) :
        panno = query.get ( 'panno' )
        gstno = query.get ( 'gstno' )
        code = query.get ( 'code' )
        if ((code == '') & (gstno == '') & (panno == '')) :
            branchlist = [ ]
        else :
            condition = Q ( panno__icontains=panno ) & Q ( gstno__icontains=gstno ) & Q ( code__icontains=code ) \
                        & Q ( vendor_id__vendor_status=5 ) & Q ( vendor_id__mainstatus=2 ) \
                        & Q ( status=1 )& Q (vendor_id__entity_id=self._entity_id()) &Q(entity_id=self._entity_id()) &Q(is_active=1)
            branchlist = SupplierBranch.objects.using(self._current_app_schema()).filter ( condition ).order_by ( '-created_date' ) [
                         vys_page.get_offset ( ) :vys_page.get_query_limit ( ) ]
        list_length = len ( branchlist )
        supplier_list_data = NWisefinList ( )
        if list_length > 0 :
            for branch in branchlist :
                payment = SupplierPayment.objects.using(self._current_app_schema()).filter(supplierbranch_id=branch.id,
                                                                                           is_active=True)
                if len(payment) != 0:
                    branch_data = BranchResponse ( )
                    branch_data.set_id ( branch.id )
                    branch_data.set_name ( branch.name )
                    branch_data.set_code ( branch.code )
                    branch_data.set_gstno ( branch.gstno )
                    branch_data.set_is_active ( branch.is_active )
                    branch_data.set_panno ( branch.panno )
                    branch_data.set_portal_flag(branch.portal_flag)
                    address = VendorRelAddress.objects.using(self._current_app_schema()).get ( id=branch.address_id, entity_id=self._entity_id())

                    add_data = AddressResponse ( )
                    add_data.set_line1 ( address.line1 )
                    add_data.set_line2 ( address.line2 )
                    add_data.set_line3 ( address.line3 )
                    # add_data.set_city_id(address.city_id)
                    city_service = CityService (self._scope())
                    city = city_service.fetch_city ( address.city_id , emp_id )
                    add_data.set_city_id ( city )

                    state_service = StateService (self._scope())
                    state_id = state_service.fetchstate ( address.state_id )
                    add_data.set_state_id ( state_id )
                    branch_data.set_address_id ( add_data )
                    supplier_list_data.append ( branch_data )
            vpage = NWisefinPaginator ( branchlist , vys_page.get_index ( ) , 10 )
            supplier_list_data.set_pagination ( vpage )
        return supplier_list_data

    def search_supplier_list_name( self , query , vys_page , emp_id ) :
        query=query

        condition = Q ( name__icontains=query ) & Q ( status=1 ) &Q(entity_id=self._entity_id())
        branchlist = SupplierBranch.objects.using(self._current_app_schema()).filter ( condition ).order_by ( '-created_date' ) [
                     vys_page.get_offset ( ) :vys_page.get_query_limit ( ) ]
        list_length = len ( branchlist )
        supplier_list_data = NWisefinList ( )
        if list_length > 0 :
            for branch in branchlist :
                branch_data = BranchResponse ( )
                branch_data.set_id ( branch.id )
                branch_data.set_name ( branch.name )
                branch_data.set_code ( branch.code )
                branch_data.set_gstno ( branch.gstno )
                branch_data.set_is_active ( branch.is_active )
                branch_data.set_panno ( branch.panno )
                branch_data.set_portal_flag(branch.portal_flag)
                address = VendorRelAddress.objects.using(self._current_app_schema()).get ( id=branch.address_id, entity_id=self._entity_id())

                add_data = AddressResponse ( )
                add_data.set_line1 ( address.line1 )
                add_data.set_line2 ( address.line2 )
                add_data.set_line3 ( address.line3 )
                # add_data.set_city_id(address.city_id)
                city_service = CityService (self._scope())
                city = city_service.fetch_city ( address.city_id , emp_id )
                add_data.set_city_id ( city )

                state_service = StateService (self._scope())
                state_id = state_service.fetchstate ( address.state_id )
                add_data.set_state_id ( state_id )
                branch_data.set_address_id ( add_data )
                supplier_list_data.append ( branch_data )
        vpage = NWisefinPaginator ( branchlist , vys_page.get_index ( ) , 10 )
        supplier_list_data.set_pagination ( vpage )
        return supplier_list_data

    def branchactive ( self , branchdata , empid ) :
        update = SupplierBranch.objects.using(self._current_app_schema()).filter ( id=branchdata.id, entity_id=self._entity_id()).update ( is_active=branchdata.is_active )
        if update :
            branch = SupplierBranch.objects.using(self._current_app_schema()).get ( id=branchdata.id, entity_id=self._entity_id())
        branch_data = BranchResponse ( )
        branch_data.set_id ( branch.id )
        branch_data.set_name ( branch.name )
        branch_data.set_code ( branch.code )
        branch_data.set_gstno ( branch.gstno )
        branch_data.set_is_active ( branch.is_active )
        return branch_data

    def branchactivemodification ( self , branch_obj , user_id , vendor_id , cont_id , add_id ) :
        req_status = RequestStatusUtil.MODIFICATION
        vendor_service = VendorService (self._scope())

        if not branch_obj.get_id ( ) is None :
            # try:
            ref_flag = vendor_service.checkmodify_rel ( VendorRefType.VENDOR_BRANCH , branch_obj.get_id ( ) )
            if ref_flag == True :
                branch = SupplierBranch.objects.using(self._current_app_schema()).filter ( id=branch_obj.get_id(), entity_id=self._entity_id()).update (
                    is_active=branch_obj.get_is_active ( ) )
                branch = SupplierBranch.objects.using(self._current_app_schema()).get ( id=branch_obj.get_id(), entity_id=self._entity_id())
            else :

                branch = SupplierBranch.objects.using(self._current_app_schema()).create ( vendor_id=vendor_id , name=branch_obj.get_name ( ) ,
                                                         code=branch_obj.get_code ( ) ,
                                                         remarks=branch_obj.get_remarks ( ) ,
                                                         limitdays=branch_obj.get_limitdays ( ) ,
                                                         creditterms=branch_obj.get_creditterms ( ) ,
                                                         gstno=branch_obj.get_gstno ( ) ,
                                                         panno=branch_obj.get_panno ( ) , address_id=add_id ,
                                                         contact_id=cont_id ,
                                                         is_active=branch_obj.get_is_active ( ) ,
                                                         created_by=user_id , modify_status=ModifyStatus.active_in ,
                                                         modified_by=user_id ,
                                                         modify_ref_id=branch_obj.get_id ( ),entity_id=self._entity_id(), portal_flag=branch_obj.get_portal_flag())

                branch_update = SupplierBranch.objects.using(self._current_app_schema()).filter ( id=branch_obj.get_id(), entity_id=self._entity_id()).update (
                    modify_ref_id=branch.id )
                branchupdate_auditdata = {'id' : branch_obj.get_id ( ) , 'modify_ref_id' : branch.id}

                VendorModificationRel.objects.using(self._current_app_schema()).create ( vendor_id=vendor_id , ref_id=branch_obj.get_id ( ) ,
                                                       ref_type=VendorRefType.VENDOR_BRANCH ,
                                                       mod_status=ModifyStatus.active_in ,
                                                       modify_ref_id=branch.id, entity_id=self._entity_id())

            vendor_check = vendor_service.branchvalidate ( branch_obj.get_id ( ) )
            if vendor_check == True :
                vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter ( id=branch_obj.get_id(), entity_id=self._entity_id()).update (
                    is_validate=True )

            # branch = SupplierBranch.objects.get(id=branch_obj.get_id())
            branch_update_id = branch_obj.get_id ( )
            self.audit_function ( branch , vendor_id , user_id , req_status , branch.id , ModifyStatus.active_in )


        else :
            # try:
            branch = SupplierBranch.objects.using(self._current_app_schema()).create ( vendor_id=vendor_id , name=branch_obj.get_name ( ) ,
                                                     remarks=branch_obj.get_remarks ( ) ,
                                                     limitdays=branch_obj.get_limitdays ( ) ,
                                                     code=branch_obj.get_code ( ) ,
                                                     creditterms=branch_obj.get_creditterms ( ) ,
                                                     gstno=branch_obj.get_gstno ( ) ,
                                                     panno=branch_obj.get_panno ( ) , address_id=add_id ,
                                                     contact_id=cont_id , is_active=branch_obj.get_is_active ( ) ,
                                                     created_by=user_id , modify_status=ModifyStatus.create ,
                                                     modified_by=user_id, entity_id=self._entity_id(),portal_flag=branch_obj.get_portal_flag())

            branch.modify_ref_id = branch.id

            code = "SU" + str ( branch.id )
            branch.code = code
            branch.save ( )
            logger.info (str(branch))

            VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=branch.id ,
                                                   ref_type=VendorRefType.VENDOR_BRANCH,
                                                   mod_status=ModifyStatus.create,
                                                   modify_ref_id=branch.id, entity_id=self._entity_id())
            vendor_check = vendor_service.branchvalidate(branch.id)
            if vendor_check == True:
                vendor_branchupdate = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch.id, entity_id=self._entity_id()).update(is_validate=True)

            self.audit_function(branch, vendor_id, user_id, req_status, branch.id, ModifyStatus.create)

        branch_data = BranchResponse()
        branch_data.set_vendor_id(branch.vendor_id)
        branch_data.set_id(branch.id)
        branch_data.set_name(branch.name)
        branch_data.set_code(branch.code)
        branch_data.set_remarks(branch.remarks)
        branch_data.set_limitdays(branch.limitdays)
        branch_data.set_creditterms(branch.creditterms)
        branch_data.set_gstno(branch.gstno)
        branch_data.set_panno(branch.panno)
        branch_data.set_is_active(branch.is_active)
        branch_data.set_address_id(branch.address_id)
        branch_data.set_contact_id(branch.contact_id)
        branch_data.set_portal_flag(branch.portal_flag)

        return branch_data

    def get_barnch_composite(self, vendor_id):
        branchcom = Vendor.objects.using(self._current_app_schema()).get(id=vendor_id, entity_id=self._entity_id())
        regcom = branchcom.composite
        return regcom

    def search_supplier_branch(self, supplierbranch_name):
        condition1 = ((Q(name__icontains=supplierbranch_name) | Q(code__icontains=supplierbranch_name)) & Q(status=1)) &Q(entity_id=self._entity_id())
        supplierbranch = SupplierBranch.objects.filter(condition1).values('id', 'code', 'name')
        emp_list_data = NWisefinList()
        for i in supplierbranch:
            data = {"id": i['id'], "code": i['code'], "name": i['name'],
                    "fullname": i['code'] + "--" + i['name']}
            emp_list_data.append(data)
        return emp_list_data

    def supplierbranch_get(self, supplierbranch_data):
        supplierbranchId_arr = supplierbranch_data['supplierbranch_id']
        supplierbranch = SupplierBranch.objects.using(self._current_app_schema()).filter(id__in=supplierbranchId_arr, entity_id=self._entity_id()).values('id', 'code',
                                                                                           'name', 'gstno',
                                                                                           'address_id', 'vendor_id')
        supplierbranch_list_data = NWisefinList()
        for i in supplierbranch:
            data = {"id": i['id'],
                    "code": i['code'],
                    "name": i['name'],
                    "gstno": i['gstno'],
                    "address_id": i['address_id'],
                    "vendor_id": i['vendor_id'],
                    "fullname": i['code'] + "--" + i['name']}
            supplierbranch_list_data.append(data)
        return supplierbranch_data

    def fetch_supplierbranchdata(self, supplierbranch_id):
        supplierbranch = SupplierBranch.objects.using(self._current_app_schema()).get(id=supplierbranch_id, entity_id=self._entity_id())
        supplierbranch_data = {"id": supplierbranch.id,
                               "code": supplierbranch.code,
                               "name": supplierbranch.name,
                               "gstno": supplierbranch.gstno,
                               "address_id": supplierbranch.address_id,
                               "vendor_id": supplierbranch.vendor_id,
                               "fullname": supplierbranch.code + "--" + supplierbranch.name}

        return supplierbranch_data

    def check_state_gst(self, resp_obj):
        if resp_obj['gstno'] == None or resp_obj['gstno'] == '' or resp_obj['gstno'] == 'GSTNOTAVAILABLE':
            flag = True
        else:
            gst = str(resp_obj['gstno'])
            state_gst = gst[:2]
            address = resp_obj.get("address")
            state_id = address['state_id']
            state = State.objects.using(self._app_schema(ApplicationNamespace.MASTER_SERVICE)).filter(id=state_id)
            flag = gst_util.check_state_gst(state[0].name, state_gst)
        return flag

    def branch_count_flag(self, vendor_id):
        flag = True
        venres_obj = VendorCheckListData()
        vendor_service = VendorService(self._scope())
        mod_status = vendor_service.get_modification_status(vendor_id)
        if mod_status:
            new_vendor = Vendor.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),modify_ref_id=vendor_id).order_by('created_date')
            if len(new_vendor) != 0:
                profile = VendorProfile.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),vendor_id=new_vendor[0].id)
                branch_count = int(profile[0].branch)
                old_branch = SupplierBranch.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),vendor_id=vendor_id, modify_status=-1,is_active = 1)
                new_branch = SupplierBranch.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),vendor_id=vendor_id, modify_status__in=[ModifyStatus.create, ModifyStatus.active_in],is_active = 1)
                branch_length = len(old_branch)+len(new_branch)
                in_active_branch = SupplierBranch.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(), vendor_id=vendor_id, is_active=0,
                    modify_status=ModifyStatus.active_in)
                if len(in_active_branch) != 0:
                    branch_length = branch_length - len(in_active_branch)
                if branch_count <= branch_length:
                    flag = False
            else:
                profile = VendorProfile.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),vendor_id=vendor_id)
                branch_count = int(profile[0].branch)
                old_branch = SupplierBranch.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),vendor_id=vendor_id,
                                                                                             modify_status=-1,is_active = 1)
                new_branch = SupplierBranch.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),vendor_id=vendor_id,is_active=1,
                                                                                             modify_status__in=[ModifyStatus.create, ModifyStatus.active_in])
                branch_length = len(old_branch) + len(new_branch)
                in_active_branch = SupplierBranch.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),vendor_id=vendor_id,is_active=0,
                                                                                             modify_status=ModifyStatus.active_in)
                if len(in_active_branch) != 0:
                    branch_length = branch_length - len(in_active_branch)
                if branch_count <= branch_length:
                    flag = False
        else:
            profile = VendorProfile.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),vendor_id=vendor_id)
            branch_count = int(profile[0].branch)
            supplier = SupplierBranch.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),vendor_id=vendor_id)
            if branch_count <= len(supplier):
                flag = False
        venres_obj.set_flag(flag)
        return venres_obj


    def search_suppliername_dropdown ( self , vys_page , query ) :
        condition = Q(status=1)
        if query != '' and query != None:
            condition = (Q ( name__icontains=query ) & (
                        Q ( vendor_id__vendor_status=5 ) | Q ( vendor_id__vendor_status=1 )) & Q (
                vendor_id__mainstatus=2 ) & Q ( status=1 ) &Q(vendor_id__entity_id=self._entity_id()))&Q(entity_id=self._entity_id()) &Q(is_active=1)
        branchlist = SupplierBranch.objects.using(self._current_app_schema()).filter ( condition ) [
                     vys_page.get_offset ( ) :vys_page.get_query_limit ( ) ]
        list_length = len ( branchlist )
        supplier_list_data = NWisefinList ( )
        if list_length > 0 :
            for branch in branchlist :
                payment = SupplierPayment.objects.using(self._current_app_schema()).filter(supplierbranch_id=branch.id,
                                                                                           is_active=True)
                if len(payment) != 0:
                    branch_data = BranchResponse ( )
                    branch_data.set_id ( branch.id )
                    branch_data.set_name ( branch.name )
                    supplier_list_data.append ( branch_data )
            vpage = NWisefinPaginator ( branchlist , vys_page.get_index ( ) , 10 )
            supplier_list_data.set_pagination ( vpage )
        return supplier_list_data

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
                                                                                        entity_id=self._entity_id(),portal_flag=branch.portal_flag)

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
                                                                                        entity_id=self._entity_id(),portal_flag=address_obj.get_portal_flag())

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

    def fetch_branch_by_code(self, code):
        try:
            branch = SupplierBranch.objects.using(self._current_app_schema()).get(code=code, entity_id=self._entity_id(),
                                                                                  modify_status=-1)
            branch_data = BranchResponse()
            branch_data.set_vendor_id(branch.vendor_id)
            branch_data.set_id(branch.id)
            branch_data.set_name(branch.name)
            branch_data.set_code(branch.code)
            branch_data.set_remarks(branch.remarks)
            branch_data.set_limitdays(branch.limitdays)
            branch_data.set_creditterms(branch.creditterms)
            branch_data.set_gstno(branch.gstno)
            branch_data.set_panno(branch.panno)
            branch_data.set_modify_ref_id(branch.modify_ref_id)
            branch_data.set_modify_status(branch.modify_status)
            branch_data.set_address_id(branch.address_id)
            branch_data.set_contact_id(branch.contact_id)
            branch_data.set_created_by(branch.created_by)
            branch_data.set_is_active(branch.is_active)
            vendor_branch = self.get_vendor_and_branch_details(branch.id)
            branch_data.vendor_and_branch_detail = vendor_branch
            if branch.is_active == 1:
                branch_data.branch_active_status = 'Active'
            else:
                branch_data.branch_active_status = 'Inactive'
            return branch_data

        except SupplierBranch.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_SUPPLIERBRANCH_ID)
            error_obj.set_description(ErrorDescription.INVALID_SUPPLIERBRANCH_ID)
            return error_obj

    def get_vendor_and_branch_details(self, branch_id):
        branch_data = SupplierBranch.objects.using(self._current_app_schema()).filter(id=branch_id,
                                                                                      entity_id=self._entity_id())
        if len(branch_data)!=0:
            vendor_id = branch_data[0].vendor_id
            vendor = Vendor.objects.using(self._current_app_schema()).get(id=vendor_id, entity_id=self._entity_id())
            branch_list = SupplierBranch.objects.using(self._current_app_schema()).filter(vendor_id=vendor.id,
                                                                                         modify_status=-1,
                                                                                         entity_id=self._entity_id())
            vendor_data = NWisefinError()
            vendor_data.id = vendor.id
            vendor_data.code = vendor.code
            vendor_data.name = vendor.name
            vendor_data.relationship_cat = vendor.custcategory_id
            list_data = NWisefinList()
            for branch in branch_list:
                branch_resp = BranchResponse()
                branch_resp.set_id(branch.id)
                branch_resp.set_code(branch.code)
                branch_resp.set_name(branch.name)
                branch_resp.relationship_cat = vendor.custcategory_id
                list_data.append(branch_resp)
            vendor_data.branch_data = list_data
            return vendor_data
