from django.db.models import Q
from nwisefin.settings import logger
from vendorservice.data.response.kyc_response import KYCResponse
from vendorservice.models import VendorModificationRel, VendorKYC, Vendor, VendorFileAttachment
from vendorservice.service.vendorservice import VendorService
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from datetime import datetime
from vendorservice.util.vendorutil import VendorRefType, ModifyStatus, VendorOrgtypeUtil, RequestStatusUtil
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from vendorservice.data.response.documentresponse import AwsResponse
from utilityservice.service.utilityservice import NWisefinUtilityService
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator


class KYCService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def create_kyc(self, vendor_id, dt_obj, user_id):
        vendor = Vendor.objects.using(self._current_app_schema()).filter(id=vendor_id)
        vendor_org_type = vendor[0].orgtype
        success_obj = NWisefinSuccess()
        if vendor_org_type == VendorOrgtypeUtil.INDIVIDUAL:
            if not dt_obj.get_id() is None:
                kyc = VendorKYC.objects.using(self._current_app_schema()
                                              ).filter(id=dt_obj.get_id(),
                                                       entity_id=self._entity_id()).update(
                    vendor_id=vendor_id,
                    organization_name=dt_obj.get_organization_name(),
                    kyc_entity=dt_obj.get_kyc_entity(),
                    sanctions_conducted=dt_obj.get_sanctions_conducted(),
                    match_found=dt_obj.get_match_found(),
                    updated_date=timezone.now(), updated_by=user_id,portal_flag=dt_obj.get_portal_flag())
                kyc = VendorKYC.objects.using(self._current_app_schema()).get(id=dt_obj.get_id(),
                                                                              entity_id=self._entity_id())
            else:
                kyc = VendorKYC.objects.using(self._current_app_schema()
                                              ).create(vendor_id=vendor_id,
                                                       organization_name=dt_obj.get_organization_name(),
                                                       kyc_entity=dt_obj.get_kyc_entity(),
                                                       sanctions_conducted=dt_obj.get_sanctions_conducted(),
                                                       match_found=dt_obj.get_match_found(),
                                                       # authorised_signatories=dt_obj.get_authorised_signatories(),
                                                       # beneficial_owners=dt_obj.get_beneficial_owners(),
                                                       created_by=user_id,
                                                       entity_id=self._entity_id(),portal_flag=dt_obj.get_portal_flag())
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            success_obj.vendor_id = kyc.vendor_id
            success_obj.organization = VendorOrgtypeUtil.INDIVIDUAL_val
        elif vendor_org_type == VendorOrgtypeUtil.SOLE_PROPRIETORSHIP:
            if not dt_obj.get_id() is None:
                kyc = VendorKYC.objects.using(self._current_app_schema()
                                              ).filter(id=dt_obj.get_id(),
                                                       entity_id=self._entity_id()).update(
                    vendor_id=vendor_id,
                    organization_name=dt_obj.get_organization_name(),
                    kyc_entity=dt_obj.get_kyc_entity(),
                    sanctions_conducted=dt_obj.get_sanctions_conducted(),
                    match_found=dt_obj.get_match_found(),
                    # authorised_signatories=dt_obj.get_authorised_signatories(),
                    # beneficial_owners=dt_obj.get_beneficial_owners(),
                    updated_date=timezone.now(), updated_by=user_id, portal_flag=dt_obj.get_portal_flag())
                kyc = VendorKYC.objects.using(self._current_app_schema()).get(id=dt_obj.get_id(),
                                                                              entity_id=self._entity_id())
            else:
                kyc = VendorKYC.objects.using(self._current_app_schema()
                                              ).create(vendor_id=vendor_id,
                                                       organization_name=dt_obj.get_organization_name(),
                                                       kyc_entity=dt_obj.get_kyc_entity(),
                                                       sanctions_conducted=dt_obj.get_sanctions_conducted(),
                                                       match_found=dt_obj.get_match_found(),
                                                       # authorised_signatories=dt_obj.get_authorised_signatories(),
                                                       # beneficial_owners=dt_obj.get_beneficial_owners(),
                                                       created_by=user_id,
                                                       entity_id=self._entity_id(),portal_flag=dt_obj.get_portal_flag())
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            success_obj.vendor_id = kyc.vendor_id
            success_obj.organization = VendorOrgtypeUtil.SOLE_PROPRIETORSHIP_val
        elif (vendor_org_type == VendorOrgtypeUtil.LIMITED_LIABILITY_PARTNERSHIP) \
                | (vendor_org_type == VendorOrgtypeUtil.PARTNERSHIP_FIRM) \
                | (vendor_org_type == VendorOrgtypeUtil.PRIVATE_LIMITED) \
                | (vendor_org_type == VendorOrgtypeUtil.PUBLIC_LIMITED_UNLISTED) \
                | (vendor_org_type == VendorOrgtypeUtil.TRUST) \
                | (vendor_org_type == VendorOrgtypeUtil.SOCIETY):
            if not dt_obj.get_id() is None:
                kyc = VendorKYC.objects.using(self._current_app_schema()
                                              ).filter(id=dt_obj.get_id(),
                                                       entity_id=self._entity_id()).update(
                    vendor_id=vendor_id,
                    organization_name=dt_obj.get_organization_name(),
                    kyc_entity=dt_obj.get_kyc_entity(),
                    sanctions_conducted=dt_obj.get_sanctions_conducted(),
                    match_found=dt_obj.get_match_found(),
                    authorised_signatories=dt_obj.get_authorised_signatories(),
                    beneficial_owners=dt_obj.get_beneficial_owners(),
                    updated_date=timezone.now(), updated_by=user_id,portal_flag=dt_obj.get_portal_flag())
                kyc = VendorKYC.objects.using(self._current_app_schema()).get(id=dt_obj.get_id(),
                                                                              entity_id=self._entity_id())
            else:
                kyc = VendorKYC.objects.using(self._current_app_schema()
                                              ).create(vendor_id=vendor_id,
                                                       organization_name=dt_obj.get_organization_name(),
                                                       kyc_entity=dt_obj.get_kyc_entity(),
                                                       sanctions_conducted=dt_obj.get_sanctions_conducted(),
                                                       match_found=dt_obj.get_match_found(),
                                                       authorised_signatories=dt_obj.get_authorised_signatories(),
                                                       beneficial_owners=dt_obj.get_beneficial_owners(),
                                                       created_by=user_id,
                                                       entity_id=self._entity_id(),portal_flag=dt_obj.get_portal_flag())
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            success_obj.vendor_id = kyc.vendor_id
            success_obj.organization = 'LLP/Partnership/Private Company/Public Unlisted Company/Trust/Society'
        elif vendor_org_type == VendorOrgtypeUtil.PUBLIC_LIMITED_LISTED:
            if not dt_obj.get_id() is None:
                kyc = VendorKYC.objects.using(self._current_app_schema()
                                              ).filter(id=dt_obj.get_id(),
                                                       entity_id=self._entity_id()).update(
                    vendor_id=vendor_id,
                    organization_name=dt_obj.get_organization_name(),
                    kyc_entity=dt_obj.get_kyc_entity(),
                    sanctions_conducted=dt_obj.get_sanctions_conducted(),
                    match_found=dt_obj.get_match_found(),
                    authorised_signatories=dt_obj.get_authorised_signatories(),
                    # beneficial_owners=dt_obj.get_beneficial_owners(),
                    updated_date=timezone.now(), updated_by=user_id, portal_flag=dt_obj.get_portal_flag())
                kyc = VendorKYC.objects.using(self._current_app_schema()).get(id=dt_obj.get_id(),
                                                                              entity_id=self._entity_id())
            else:
                kyc = VendorKYC.objects.using(self._current_app_schema()
                                              ).create(vendor_id=vendor_id,
                                                       organization_name=dt_obj.get_organization_name(),
                                                       kyc_entity=dt_obj.get_kyc_entity(),
                                                       sanctions_conducted=dt_obj.get_sanctions_conducted(),
                                                       match_found=dt_obj.get_match_found(),
                                                       authorised_signatories=dt_obj.get_authorised_signatories(),
                                                       # beneficial_owners=dt_obj.get_beneficial_owners(),
                                                       created_by=user_id,
                                                       entity_id=self._entity_id(),portal_flag=dt_obj.get_portal_flag())
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            success_obj.vendor_id = kyc.vendor_id
            success_obj.organization = VendorOrgtypeUtil.PUBLIC_LIMITED_LISTED
        kyc_data = KYCResponse()
        kyc_data.set_id(kyc.id)
        kyc_data.set_vendor_id(kyc.vendor_id)
        kyc_data.set_kyc_entity(kyc.kyc_entity)
        kyc_data.set_organization_name(kyc.organization_name)
        kyc_data.set_sanctions_conducted(kyc.sanctions_conducted)
        kyc_data.set_beneficial_owners(kyc.beneficial_owners)
        kyc_data.set_match_found(kyc.match_found)
        kyc_data.set_authorised_signatories(kyc.authorised_signatories)
        kyc_data.set_beneficial_owners(kyc.beneficial_owners)
        kyc_data.set_report_file_id(kyc.report_file_id)
        kyc_data.set_portal_flag(kyc.portal_flag)
        return kyc_data

    def create_bulk_director(self, dt_obj, user_id):
        pass

    def get_kyc_list(self,vendor_id, user_id):
        kycList = VendorKYC.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                             vendor_id=vendor_id)
        list_length = len(kycList)
        logger.info(str(list_length))
        dir_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for kyc in kycList:
                kyc_data = KYCResponse()
                kyc_data.set_id(kyc.id)
                kyc_data.set_vendor_id(kyc.vendor_id)
                kyc_data.set_kyc_entity(kyc.kyc_entity)
                kyc_data.set_organization_name(kyc.organization_name)
                kyc_data.set_sanctions_conducted(kyc.sanctions_conducted)
                kyc_data.set_beneficial_owners(kyc.beneficial_owners)
                kyc_data.set_match_found(kyc.match_found)
                kyc_data.set_authorised_signatories(kyc.authorised_signatories)
                kyc_data.set_beneficial_owners(kyc.beneficial_owners)
                kyc_data.set_report_file_id(kyc.report_file_id)
                kyc_data.set_portal_flag(kyc.portal_flag)
                dir_list_data.append(kyc_data)
        return dir_list_data



    def fetch_kyc(self, kyc_id, user_id):
        try:
            kyc = VendorKYC.objects.using(self._current_app_schema()).get(id=kyc_id, entity_id=self._entity_id())
            kyc_data = KYCResponse()
            kyc_data.set_id(kyc.id)
            kyc_data.set_vendor_id(kyc.vendor_id)
            kyc_data.set_kyc_entity(kyc.kyc_entity)
            kyc_data.set_organization_name(kyc.organization_name)
            kyc_data.set_sanctions_conducted(kyc.sanctions_conducted)
            kyc_data.set_beneficial_owners(kyc.beneficial_owners)
            kyc_data.set_match_found(kyc.match_found)
            kyc_data.set_authorised_signatories(kyc.authorised_signatories)
            kyc_data.set_beneficial_owners(kyc.beneficial_owners)
            # kyc_data.set_report_file_id(kyc.report_file_id)
            kyc_data.set_modify_ref_id(kyc.modify_ref_id)
            kyc_data.set_modify_status(kyc.modify_status)
            kyc_data.set_created_by(kyc.created_by)
            kyc_data.set_portal_flag(kyc.portal_flag)
            tab_type = VendorRefType.VENDOR_KYC
            doc = VendorFileAttachment.objects.using(self._current_app_schema()).filter(
                                                Q(representtabel_id=kyc.id)
                                                & Q(tab_type=tab_type)
                                                & Q(status=1)
                                                & Q(entity_id=self._entity_id()))
            date_lenth = len(doc)
            dlist = list()
            if date_lenth > 0:
                for doc in doc:
                    document_data = AwsResponse()
                    document_data.set_id(doc.id)
                    document_data.set_file_name(doc.file_name)
                    document_data.set_gen_file_name(doc.gen_file_name)
                    dlist.append(document_data)
            kyc_data.report_file_id = dlist
            kyc_data.file_id = kyc.report_file_id
            return kyc_data
        except VendorKYC.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_KYC_ID)
            error_obj.set_description(ErrorDescription.INVALID_KYC_ID)
            return error_obj

    def delete_kyc(self, vendor_id, kyc_id, user_id):
        kyc = VendorKYC.objects.using(self._current_app_schema()).filter(
                                id=kyc_id,
                                vendor_id=vendor_id,
                                entity_id=self._entity_id()).delete()
        if kyc[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_KYC_ID)
            error_obj.set_description(ErrorDescription.INVALID_KYC_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    # modification
    def create_kyc_modification(self, vendor_id, dt_obj, user_id):
        if not dt_obj.get_id() is None:
            vendor_service = VendorService(self._scope())
            ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_KYC, dt_obj.get_id())
            if ref_flag == True:
                kyc = VendorKYC.objects.using(self._current_app_schema()).filter(
                                    id=dt_obj.get_id(),
                                    entity_id=self._entity_id()).update(
                                    vendor_id=vendor_id,
                                    organization_name=dt_obj.get_organization_name(),
                                    kyc_entity=dt_obj.get_kyc_entity(),
                                    sanctions_conducted=dt_obj.get_sanctions_conducted(),
                                    match_found=dt_obj.get_match_found(),
                                    authorised_signatories=dt_obj.get_authorised_signatories(),
                                    beneficial_owners=dt_obj.get_beneficial_owners(),portal_flag=dt_obj.get_portal_flag())
                kyc = VendorKYC.objects.using(self._current_app_schema()).get(id=dt_obj.get_id(), entity_id=self._entity_id())
            else:
                kyc = VendorKYC.objects.using(self._current_app_schema()).create(vendor_id=vendor_id,
                             organization_name=dt_obj.get_organization_name(),
                             kyc_entity=dt_obj.get_kyc_entity(),
                             sanctions_conducted=dt_obj.get_sanctions_conducted(),
                             match_found=dt_obj.get_match_found(),
                             authorised_signatories=dt_obj.get_authorised_signatories(),
                             beneficial_owners=dt_obj.get_beneficial_owners(),
                            modify_status=ModifyStatus.update,
                            created_by = user_id,
                            modify_ref_id=dt_obj.get_id(),
                            entity_id=self._entity_id(),portal_flag=dt_obj.get_portal_flag())

                kyc_update = VendorKYC.objects.using(self._current_app_schema()).filter(id=dt_obj.get_id(),
                            entity_id=self._entity_id()).update(
                            modify_ref_id=kyc.id)

                VendorModificationRel.objects.using(self._current_app_schema()).create(
                            vendor_id=vendor_id,
                            ref_id=dt_obj.get_id(),
                            ref_type=VendorRefType.VENDOR_KYC,
                            mod_status=ModifyStatus.update,
                            modify_ref_id=kyc.id,
                            entity_id=self._entity_id())


        else:
            kyc = VendorKYC.objects.using(self._current_app_schema()).create(
                            vendor_id=vendor_id,
                            organization_name=dt_obj.get_organization_name(),
                            kyc_entity=dt_obj.get_kyc_entity(),
                            sanctions_conducted=dt_obj.get_sanctions_conducted(),
                            match_found=dt_obj.get_match_found(),
                            authorised_signatories=dt_obj.get_authorised_signatories(),
                            beneficial_owners=dt_obj.get_beneficial_owners(),
                            modify_status=ModifyStatus.create,
                            created_by = user_id,
                            entity_id=self._entity_id(), portal_flag=dt_obj.get_portal_flag())
            kyc_update=VendorKYC.objects.using(self._current_app_schema()).filter(
                                                            id=kyc.id,
                                                            entity_id=self._entity_id()
                                                            ).update(modify_ref_id=kyc.id)
            VendorModificationRel.objects.using(self._current_app_schema()).create(
                                                vendor_id=vendor_id,
                                                ref_id=kyc.id,
                                                ref_type=VendorRefType.VENDOR_KYC,
                                                mod_status=ModifyStatus.create,
                                                modify_ref_id=kyc.id,
                                                entity_id=self._entity_id())
        kyc_data = KYCResponse()
        kyc_data.set_id(kyc.id)
        kyc_data.set_organization_name(kyc.organization_name)
        kyc_data.set_sanctions_conducted(kyc.sanctions_conducted)
        kyc_data.set_match_found(kyc.match_found)
        kyc_data.set_authorised_signatories(kyc.authorised_signatories)
        kyc_data.set_beneficial_owners(kyc.beneficial_owners)
        kyc_data.set_portal_flag(kyc.portal_flag)
        return kyc_data

    def modification_delete_kyc(self, vendor_id, kyc_id, employee_id):
        try:
            vendor_service = VendorService(self._scope())
            kyc_update = VendorKYC.objects.using(self._current_app_schema()).filter(
                                                    id=kyc_id,
                                                    entity_id=self._entity_id()).update(
                                                    modify_ref_id=kyc_id,
                                                    modify_status=ModifyStatus.delete)
            ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_KYC, kyc_id)
            if ref_flag == True:
                flag_obj = VendorModificationRel.objects.using(self._current_app_schema()).filter(
                                                    Q(modify_ref_id=kyc_id)
                                                    & Q(ref_type=VendorRefType.VENDOR_KYC)
                                                    & Q(entity_id=self._entity_id())
                                                    ).update(mod_status=ModifyStatus.delete)
            else:
                VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id,
                                                                                       ref_id=kyc_id,
                                                                                       ref_type=VendorRefType.VENDOR_KYC,
                                                                                       mod_status=ModifyStatus.delete,
                                                                                       modify_ref_id=kyc_id,
                                                                                       entity_id=self._entity_id())
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj


    def fetch_kyc_modification(self, vendor_id, user_id):
        try:
            kyc = VendorKYC.objects.using(self._current_app_schema()).all().filter(
                                                Q(vendor_id=vendor_id)
                                                & Q(modify_status=1)
                                                & Q(entity_id=self._entity_id()))
            dir_array = []
            for i in kyc:
                kyc_data = KYCResponse()
                kyc_data.set_id(i.id)
                kyc_data.set_vendor_id(i.vendor_id)
                kyc_data.set_organization_name(i.organization_name)
                kyc_data.set_sanctions_conducted(i.sanctions_conducted)
                kyc_data.set_match_found(i.match_found)
                kyc_data.set_authorised_signatories(i.authorised_signatories)
                kyc_data.set_beneficial_owners(i.beneficial_owners)
                kyc_data.set_portal_flag(i.portal_flag)
                dir_array.append(kyc_data)
            return dir_array
        except VendorKYC.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_KYC_ID)
            error_obj.set_description(ErrorDescription.INVALID_KYC_ID)
            return error_obj

    def approve_kyc_modification(self, dic_id, user_id):
        try:
            kyc = VendorKYC.objects.using(self._current_app_schema()).get(Q(id=dic_id) & Q(modify_status=1) & Q(entity_id=self._entity_id()))
            kyc_data = KYCResponse()
            kyc_data.set_id(kyc.id)
            kyc_data.set_vendor_id(kyc.vendor_id)
            kyc_data.set_organization_name(kyc.organization_name)
            kyc_data.set_sanctions_conducted(kyc.sanctions_conducted)
            kyc_data.set_match_found(kyc.match_found)
            kyc_data.set_authorised_signatories(kyc.authorised_signatories)
            kyc_data.set_beneficial_owners(kyc.beneficial_owners)
            kyc_data.set_portal_flag(kyc.portal_flag)
            return kyc_data
        except VendorKYC.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_KYC_ID)
            error_obj.set_description(ErrorDescription.INVALID_KYC_ID)
            return error_obj

    def modification_reject_vendorkyc(self, mod_status, old_id, new_id,vendor_id, user_id):
        if mod_status == ModifyStatus.update:
            VendorKYC.objects.using(self._current_app_schema()).filter(id=new_id).delete()
            vendor_kyc =VendorKYC.objects.using(self._current_app_schema()).filter(id=old_id,
                                                                                   entity_id=self._entity_id()
                                                                                   ).update(modify_ref_id=-1)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_KYC_ID)
            error_obj.set_description(ErrorDescription.INVALID_KYC_ID)
            return error_obj

    def multiple_document_upload(self, resp_obj, tab_type, request, doc_obj, attachment):
        data_count = len(request.FILES.getlist(attachment))
        obj_list = []
        for i in range(0, data_count):
            data_obj = request.FILES.getlist(attachment)[i]
            name = data_obj.name
            file_id = doc_obj.data[i].id
            file_name = doc_obj.data[i].file_name
            file_name_new = str(datetime.now().strftime("%y%m%d_%H%M%S")) + name
            obj = VendorFileAttachment.objects.using(self._current_app_schema()).create(
                representtabel_id=resp_obj.get_id(), tab_type=tab_type, gen_file_name=file_name_new,
                file_name=file_name, entity_id=self._entity_id(), file_id=file_id)
            obj_list.append(obj)
        return obj_list

    def vendor_file_data(self, id, tab_type):
        documentlist = VendorFileAttachment.objects.using(self._current_app_schema()).filter(Q(representtabel_id=id)&Q(tab_type=tab_type)&Q(status=1)&Q(entity_id=self._entity_id()))
        documentlist_ln=len(documentlist)
        vlist = NWisefinList()
        if documentlist_ln==0:
            documentlist=[]
        else:
            for doc in documentlist:
                document_data = AwsResponse()
                document_data.set_id(doc.id)
                document_data.set_file_name(doc.file_name)
                document_data.set_gen_file_name(doc.gen_file_name)
                vlist.append(document_data)
        return vlist

    def fetch_kyc_list(self, request, vys_page,vendor_id):
        queue_arr = VendorKYC.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id, entity_id=self._entity_id()).values('id')
        condition = None
        for vendor in queue_arr:
            logger.info(str(vendor))
            if condition is None:
                condition = (Q(id__exact=vendor['id'])& (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1))&Q(entity_id=self._entity_id())
            else:
                condition |= (Q(id__exact=vendor['id'])& (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1))&Q(entity_id=self._entity_id())
        if condition is not None:
            kyclist = VendorKYC.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        else:
            kyclist = []

        vlist = NWisefinList()
        user_list = []
        for vendor in kyclist:
            user_list.append(vendor.created_by)
        user_list = set(user_list)
        user_list = list(user_list)
        utility_service = NWisefinUtilityService()
        user_list_obj = utility_service.get_user_info(request, user_list)

        for kyc in kyclist:
            kyc_data = KYCResponse()
            kyc_data.set_id(kyc.id)
            kyc_data.set_vendor_id(kyc.vendor_id)
            kyc_data.set_kyc_entity(kyc.kyc_entity)
            kyc_data.set_organization_name(kyc.organization_name)
            kyc_data.set_sanctions_conducted(kyc.sanctions_conducted)
            kyc_data.set_beneficial_owners(kyc.beneficial_owners)
            kyc_data.set_match_found(kyc.match_found)
            kyc_data.set_authorised_signatories(kyc.authorised_signatories)
            kyc_data.set_beneficial_owners(kyc.beneficial_owners)
            # kyc_data.set_report_file_id(kyc.report_file_id)
            kyc_data.set_modify_status(kyc.modify_status)
            kyc_data.set_modify_ref_id(kyc.modify_ref_id)
            kyc_data.set_portal_flag(kyc.portal_flag)
            tab_type = VendorRefType.VENDOR_KYC
            # document_data.set_branch_id(documentobj.ven)
            doc = VendorFileAttachment.objects.using(self._current_app_schema()).filter(
                                            Q(representtabel_id=kyc.id)
                                            & Q(tab_type=tab_type)
                                            & Q(status=1)
                                            & Q(entity_id=self._entity_id()))
            date_lenth = len(doc)
            dlist = list()
            if date_lenth > 0:
                for doc in doc:
                    document_data = AwsResponse()
                    document_data.set_id(doc.id)
                    document_data.set_file_name(doc.file_name)
                    document_data.set_gen_file_name(doc.gen_file_name)
                    dlist.append(document_data)
            kyc_data.report_file_id = dlist
            for ul in user_list_obj['data']:
                if ul['id'] == VendorKYC.created_by:
                    kyc_data.set_created_by(ul)
            vlist.append(kyc_data)
        vpage = NWisefinPaginator(kyclist, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)

        return vlist

    def document_upload(self, resp_obj, tab_type,request, doc_obj):
        data= request.FILES['file']
        data_count = len(request.FILES.getlist('file'))
        obj_list = []
        for i in range(0,data_count):
            data_obj = request.FILES.getlist('file')[i]
            name = data_obj.name
            file_id=doc_obj.data[i].id
            file_name=doc_obj.data[i].file_name
            file_name_new = str(datetime.now().strftime("%y%m%d_%H%M%S")) + name
            obj= VendorFileAttachment.objects.using(self._current_app_schema()).create(representtabel_id=resp_obj.get_id(),tab_type=tab_type, gen_file_name=file_name_new, file_name=file_name,entity_id=self._entity_id(), file_id=file_id)
            obj_list.append(obj)
        return obj_list

    def modification_action_kyc(self,mod_status,old_id,new_id,vendor_id,user_id):
        req_status = RequestStatusUtil.MODIFICATION
        if mod_status == ModifyStatus.update:
            kyc_obj = self.get_kyc(new_id, user_id)
            print("kyc_obj", kyc_obj)
            document_update = VendorKYC.objects.using(self._current_app_schema()).filter(
                                                    id=old_id,
                                                    entity_id=self._entity_id()).update(
                                                    vendor_id=kyc_obj.get_vendor_id(),
                                                    organization_name=kyc_obj.get_organization_name(),
                                                    kyc_entity=kyc_obj.get_kyc_entity(),
                                                    sanctions_conducted=kyc_obj.get_sanctions_conducted(),
                                                    match_found=kyc_obj.get_match_found(),
                                                    authorised_signatories=kyc_obj.get_authorised_signatories(),
                                                    beneficial_owners=kyc_obj.get_beneficial_owners(),
                                                    report_file_id=kyc_obj.get_report_file_id(),
                                                    modify_status=-1,
                                                    modified_by=-1,
                                                    modify_ref_id=-1,portal_flag=kyc_obj.get_portal_flag())
            doc_file = VendorFileAttachment.objects.using(self._current_app_schema()).filter(
                                                    Q(representtabel_id=new_id)
                                                    & Q(tab_type=VendorRefType.VENDOR_KYC)
                                                    & Q(entity_id=self._entity_id())).update(
                                                    representtabel_id=old_id)

            # self.audit_function(document_update, vendor_id, user_id, req_status, old_id, ModifyStatus.update)

        elif mod_status == ModifyStatus.create:
            document_update = VendorKYC.objects.using(self._current_app_schema()).filter(
                                                    id=new_id,
                                                    entity_id=self._entity_id()).update(
                                                    modify_status=-1,
                                                    modify_ref_id=-1,
                                                    modified_by=-1)

            # self.audit_function(document_update, vendor_id, user_id, req_status, new_id, ModifyStatus.update)

        else:
            document = VendorKYC.objects.using(self._current_app_schema()).filter(id=old_id,
                                                                                       entity_id=self._entity_id()
                                                                                       ).delete()

            # self.audit_function(document, vendor_id, user_id, req_status, old_id, ModifyStatus.delete)
        return

    def fetch_vendorkyc_list(self, request, vys_page,vendor_id, employee_id):
        queue_arr = VendorKYC.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id, entity_id=self._entity_id()).values('id')
        vendor_service = VendorService(self._scope())
        condition = None
        for vendor in queue_arr:
            logger.info(str(vendor))
            if condition is None:
                condition = (Q(id__exact=vendor['id'])& (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1))&Q(entity_id=self._entity_id())
            else:
                condition |= (Q(id__exact=vendor['id'])& (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1))&Q(entity_id=self._entity_id())
        if condition is not None:
            kyclist = VendorKYC.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        else:
            kyclist = []

        vlist = NWisefinList()
        user_list = []
        for vendor in kyclist:
            user_list.append(vendor.created_by)
        user_list = set(user_list)
        user_list = list(user_list)
        utility_service = NWisefinUtilityService()
        user_list_obj = utility_service.get_user_info(request, user_list)

        for kyc in kyclist:
            kyc_data = KYCResponse()
            kyc_data.set_id(kyc.id)
            kyc_data.set_vendor_id(kyc.vendor_id)
            kyc_data.set_kyc_entity(kyc.kyc_entity)
            kyc_data.set_organization_name(kyc.organization_name)
            kyc_data.set_sanctions_conducted(kyc.sanctions_conducted)
            kyc_data.set_beneficial_owners(kyc.beneficial_owners)
            kyc_data.set_match_found(kyc.match_found)
            kyc_data.set_authorised_signatories(kyc.authorised_signatories)
            kyc_data.set_beneficial_owners(kyc.beneficial_owners)
            # kyc_data.set_report_file_id(kyc.report_file_id)
            kyc_data.set_modify_status(kyc.modify_status)
            kyc_data.set_modify_ref_id(kyc.modify_ref_id)
            kyc_data.set_portal_flag(kyc.portal_flag)
            tab_type = VendorRefType.VENDOR_KYC
            data_obj = self.vendor_file_data(kyc.id, tab_type)
            if kyc_data.modify_status != 2:
                kyc_data.report_file_id = data_obj.data
            else:
                data_obj1 = self.vendor_file_data(kyc_data.modify_ref_id, tab_type)
                fileary = vendor_service.append_doc(data_obj.data, data_obj1.data)
                kyc_data.report_file_id = fileary

            vendor_id = kyc_data.vendor_id
            vendor_status = vendor_service.get_vendor_status(vendor_id)
            kyc_data.q_modify = False
            if (kyc_data.created_by == employee_id):
                if (vendor_status == 0 or vendor_status == 1):
                    kyc_data.q_modify = True

            # for modification testing
            kyc_data.q_modify = True
            for ul in user_list_obj['data']:
                if ul['id'] == VendorKYC.created_by:
                    kyc_data.set_created_by(ul)
            vlist.append(kyc_data)
        vpage = NWisefinPaginator(kyclist, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)

        return vlist

    def get_kyc(self, kyc_id, user_id):
        try:
            kyc = VendorKYC.objects.using(self._current_app_schema()).get(id=kyc_id, entity_id=self._entity_id())
            kyc_data = KYCResponse()
            kyc_data.set_id(kyc.id)
            kyc_data.set_vendor_id(kyc.vendor_id)
            kyc_data.set_kyc_entity(kyc.kyc_entity)
            kyc_data.set_organization_name(kyc.organization_name)
            kyc_data.sanctions_conducted = kyc.sanctions_conducted
            kyc_data.set_beneficial_owners(kyc.beneficial_owners)
            kyc_data.match_found = kyc.match_found
            kyc_data.set_authorised_signatories(kyc.authorised_signatories)
            kyc_data.set_beneficial_owners(kyc.beneficial_owners)
            kyc_data.set_report_file_id(kyc.report_file_id)
            kyc_data.set_modify_ref_id(kyc.modify_ref_id)
            kyc_data.set_modify_status(kyc.modify_status)
            kyc_data.set_created_by(kyc.created_by)
            kyc_data.set_portal_flag(kyc.portal_flag)
            return kyc_data
        except VendorKYC.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_KYC_ID)
            error_obj.set_description(ErrorDescription.INVALID_KYC_ID)
            return error_obj
