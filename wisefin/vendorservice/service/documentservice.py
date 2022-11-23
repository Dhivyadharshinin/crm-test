import django

from django.db import IntegrityError
from nwisefin.settings import logger
from userservice.models import Employee
from vendorservice.models import VendorDocument ,VendorModificationRel,VendorFileAttachment
from vendorservice.data.response.documentresponse import DocumentResponse ,AwsResponse
# from memoservice.models import Documents
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from datetime import datetime
now = datetime.now()
from utilityservice.service.utilityservice import NWisefinUtilityService
from django.db.models import Q
from vendorservice.util.vendorutil import VendorRefType ,ModifyStatus,RequestStatusUtil
from vendorservice.service.vendorauditservice import VendorAuditService
from vendorservice.data.response.vendorauditresponse import VendorAuditResponse
from vendorservice.service.vendorservice import VendorService


class DocumentService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def create_document(self, document_obj, user_id,vendor_id,ref_id):

        req_status = RequestStatusUtil.ONBOARD
        if not document_obj.get_id() is None:
            try:
                document_var = VendorDocument.objects.using(self._current_app_schema()).filter(id=document_obj.get_id(), entity_id=self._entity_id()).update(
                    partner_id=vendor_id,
                    docgroup_id=document_obj.get_docgroup_id(),
                    period=document_obj.get_period(),
                    remarks=document_obj.get_remarks(),
                    file_id=ref_id,
                                updated_date=now,
                                updated_by=user_id,portal_flag=document_obj.get_portal_flag())

                document_auditdata={'id':document_obj.get_id(),
                    'partner_id':vendor_id,
                    'docgroup_id':document_obj.get_docgroup_id(),
                    # period=document_obj.get_period(),
                    'remarks':document_obj.get_remarks(),
                    'file_id':ref_id,
                                'updated_date':now,
                                'updated_by':user_id}

                document_var = VendorDocument.objects.using(self._current_app_schema()).get(id=document_obj.get_id(), entity_id=self._entity_id())
                Action =ModifyStatus.update
                self.audit_function(document_auditdata, vendor_id, user_id, req_status, document_var.id, Action)
            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except VendorDocument.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CATEGORY_ID)
                error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                document_var = VendorDocument.objects.using(self._current_app_schema()).create(partner_id=vendor_id,
                                docgroup_id=document_obj.get_docgroup_id(),
                                period=document_obj.get_period(),
                                remarks=document_obj.get_remarks(),
                                file_id=ref_id,
                                created_by=user_id, entity_id=self._entity_id(),portal_flag=document_obj.get_portal_flag())
                Action =ModifyStatus.create
            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        # audit
        req_status = RequestStatusUtil.ONBOARD
        self.audit_function(document_var, vendor_id, user_id, req_status, document_var.id, Action)

        document_data = DocumentResponse()
        document_data.set_id(document_var.id)
        document_data.set_partner_id(document_var.partner_id)
        document_data.set_docgroup_id(document_var.docgroup_id)
        document_data.set_period(document_var.period)
        document_data.set_remarks(document_var.remarks)
        document_data.set_file_id(document_var.file_id)
        document_data.set_portal_flag(document_var.portal_flag)
        # document_data.set_branch_id(document_var.branch_id)
        return document_data

    # def fetch_document_list(self,user_id,request,vys_page):
    #     documentlist = VendorDocument.objects.all()
    #     list_length = len(documentlist)
    #     logger.info(list_length)
    #     if list_length <= 0:
    #         error_obj = Error()
    #         error_obj.set_code(ErrorMessage.INVALID_DOCUMENT_ID)
    #         error_obj.set_description(ErrorDescription.INVALID_DOCUMENT_ID)
    #         return error_obj
    #     else:
    #         document_list_data = VysfinList()
    #         for documentobj in documentlist:
    #             document_data = DocumentResponse()
    #             document_data.set_id(documentobj.id)
    #             document_data.set_partner_id(documentobj.partner_id)
    #             document_data.set_docgroup_id(documentobj.docgroup_id)
    #             # document_data.set_period(documentobj.period)
    #             document_data.set_remarks(documentobj.remarks)
    #             document_data.set_file_id(documentobj.file_id)
    #             document_data.set_created_by(documentobj.created_by)
    #             # document_data.set_branch_id(documentobj.ven)
    #             document_list_data.append(document_data)
    #
    #         return document_list_data

    def fetch_document_list(self, user_id, request, vys_page,vendor_id):

        queue_arr = VendorDocument.objects.using(self._current_app_schema()).filter(partner_id=vendor_id, entity_id=self._entity_id()).values('id')
        condition = None
        for vendor in queue_arr:
            logger.info(str(vendor))
            if condition is None:
                condition = (Q(id__exact=vendor['id'])& (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1))&Q(entity_id=self._entity_id())
            else:
                condition |= (Q(id__exact=vendor['id'])& (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1))&Q(entity_id=self._entity_id())
        if condition is not None:
            documentlist = VendorDocument.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        else:
            documentlist = []

        vlist = NWisefinList()
        user_list = []
        for vendor in documentlist:
            user_list.append(vendor.created_by)
        user_list = set(user_list)
        user_list = list(user_list)
        utility_service = NWisefinUtilityService()
        user_list_obj = utility_service.get_user_info(request, user_list)

        for documentobj in documentlist:
            document_data = DocumentResponse()
            document_data.set_id(documentobj.id)
            document_data.set_partner_id(documentobj.partner_id)
            document_data.set_docgroup_id(documentobj.docgroup_id)
            document_data.set_period(documentobj.period)
            document_data.set_remarks(documentobj.remarks)
            document_data.set_file_id(documentobj.file_id)
            document_data.set_created_by(documentobj.created_by)
            document_data.set_modify_ref_id(documentobj.modify_ref_id)
            document_data.set_modify_status(documentobj.modify_status)
            document_data.set_portal_flag(documentobj.portal_flag)

            # document_data.set_branch_id(documentobj.ven)

            for ul in user_list_obj['data']:
                if ul['id'] == VendorDocument.created_by:
                    document_data.set_created_by(ul)
            vlist.append(document_data)
        vpage = NWisefinPaginator(documentlist, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)

        return vlist


    def fetch_document(self,document_id):
        try:
            document_var = VendorDocument.objects.using(self._current_app_schema()).get(id=document_id, entity_id=self._entity_id())
            document_data = DocumentResponse()
            document_data.set_id(document_var.id)
            document_data.set_partner_id(document_var.partner_id)
            document_data.set_docgroup_id(document_var.docgroup_id)
            document_data.set_period(document_var.period)
            document_data.set_remarks(document_var.remarks)
            document_data.set_file_id(document_var.file_id)
            document_data.set_modify_ref_id(document_var.modify_ref_id)
            document_data.set_modify_status(document_var.modify_status)
            # document_data.set_branch_id(document_var.branch_id)
            document_data.set_created_by(document_var.created_by)
            document_data.set_portal_flag(document_var.portal_flag)


            return document_data
        except VendorDocument.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DOCUMENT_ID)
            error_obj.set_description(ErrorDescription.INVALID_DOCUMENT_ID)
            return error_obj

    def delete_document(self, document_id,vendor_id,user_id):

        document = VendorDocument.objects.using(self._current_app_schema()).filter(id=document_id, entity_id=self._entity_id()).delete()
        # audit
        req_status = RequestStatusUtil.ONBOARD
        self.audit_function(document, vendor_id, user_id, req_status, document_id, ModifyStatus.delete)

        if document[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DOCUMENT_ID)
            error_obj.set_description(ErrorDescription.INVALID_DOCUMENT_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    # def  aws_file_data(self,id):
    #     aws_var = Documents.objects.get(id=id)
    #     document_data = AwsResponse()
    #     document_data.set_id(aws_var.id)
    #     document_data.set_file_name(aws_var.file_name)
    #     document_data.set_gen_file_name(aws_var.gen_file_name)
    #
    #     return document_data

    def  vendor_file_data(self,id,tab_type):
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

    # modification
    def modification_create_document(self, document_obj, user_id,vendor_id,ref_id):

        vendor_service = VendorService(self._scope())
        if not document_obj.get_id() is None:
            try:
                ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_DOCUMENT, document_obj.get_id())
                if ref_flag==True:
                    document_var = VendorDocument.objects.using(self._current_app_schema()).filter(id=document_obj.get_id(), entity_id=self._entity_id()).update(partner_id=vendor_id,
                                                                 docgroup_id=document_obj.get_docgroup_id(),
                                                                 period=document_obj.get_period(),
                                                                 remarks=document_obj.get_remarks(),
                                                                 portal_flag=document_obj.get_portal_flag()
                                                                 )
                    document_var=VendorDocument.objects.using(self._current_app_schema()).get(id=document_obj.get_id(), entity_id=self._entity_id())
                else:

                    document_var = VendorDocument.objects.using(self._current_app_schema()).create(partner_id=vendor_id,
                                    docgroup_id=document_obj.get_docgroup_id(),period=document_obj.get_period(),
                                    remarks=document_obj.get_remarks(),file_id=ref_id,created_by=user_id,
                                    modify_status=ModifyStatus.update,modified_by=user_id,modify_ref_id=document_obj.get_id(), entity_id=self._entity_id(), portal_flag=document_obj.get_portal_flag())

                    document_update = VendorDocument.objects.using(self._current_app_schema()).filter(id=document_obj.get_id(), entity_id=self._entity_id()).update(
                        modify_ref_id=document_var.id)

                # documentupdate_auditdata={'id':document_obj.get_id(),'modify_ref_id':document_var.id}

                    VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=document_obj.get_id(),
                                                         ref_type=VendorRefType.VENDOR_DOCUMENT,
                                                         mod_status=ModifyStatus.update,
                                                         modify_ref_id=document_var.id, entity_id=self._entity_id())

                # document_var = VendorDocument.objects.get(id=document_obj.get_id())


                req_status = RequestStatusUtil.MODIFICATION
                docu_id = document_obj.get_id()
                self.audit_function(document_var, vendor_id, user_id, req_status, document_var.id, ModifyStatus.create)
                # self.audit_function(documentupdate_auditdata, vendor_id, user_id, req_status,docu_id, ModifyStatus.update)

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except VendorDocument.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CATEGORY_ID)
                error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        else :
            try:
                document_var = VendorDocument.objects.using(self._current_app_schema()).create(partner_id=vendor_id,
                                                             docgroup_id=document_obj.get_docgroup_id(),
                                                             period=document_obj.get_period(),
                                                             remarks=document_obj.get_remarks(), file_id=ref_id,
                                                             created_by=user_id,
                                                             modify_status=ModifyStatus.create,modified_by=user_id, entity_id=self._entity_id(),portal_flag=document_obj.get_portal_flag())

                document_var.modify_ref_id = document_var.id
                document_var.save()

                VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=document_var.id,
                                                     ref_type=VendorRefType.VENDOR_DOCUMENT,
                                                     mod_status=ModifyStatus.create,
                                                     modify_ref_id=document_var.id, entity_id=self._entity_id())


                req_status = RequestStatusUtil.MODIFICATION
                self.audit_function(document_var, vendor_id, user_id, req_status, document_var.id, ModifyStatus.create)

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except VendorDocument.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CATEGORY_ID)
                error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        document_data = DocumentResponse()
        document_data.set_id(document_var.id)
        document_data.set_partner_id(document_var.partner_id)
        document_data.set_docgroup_id(document_var.docgroup_id)
        document_data.set_remarks(document_var.remarks)
        document_data.set_portal_flag(document_var.portal_flag)
        # document_data.set_file_id(document_var.file_id)
        return document_data

    def modification_delete_document(self, document_id, vendor_id,user_id):
        try:
            vendor_service = VendorService(self._scope())
            document_update = VendorDocument.objects.using(self._current_app_schema()).filter(id=document_id, entity_id=self._entity_id()).update(
                modify_ref_id=document_id,modify_status=ModifyStatus.delete)
            ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_DOCUMENT, document_id)
            if ref_flag==True:
                flag_obj = VendorModificationRel.objects.using(self._current_app_schema()).filter(Q(modify_ref_id=document_id)&Q(ref_type=VendorRefType.VENDOR_DOCUMENT)&Q(entity_id=self._entity_id())).update(mod_status=ModifyStatus.delete)
            else:
                VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=document_id,
                                                     ref_type=VendorRefType.VENDOR_DOCUMENT,
                                                     mod_status=ModifyStatus.delete,
                                                     modify_ref_id=document_id, entity_id=self._entity_id())
            req_status = RequestStatusUtil.MODIFICATION
            # self.audit_function(document_update, vendor_id, user_id, req_status, document_id, ModifyStatus.update)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj

    def modification_action_document(self,mod_status,old_id,new_id,vendor_id,user_id):

        req_status = RequestStatusUtil.MODIFICATION
        if mod_status == ModifyStatus.update:
            doucment_obj = self.fetch_document(new_id)

            document_update = VendorDocument.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(partner_id=doucment_obj.get_partner_id(),
            docgroup_id=doucment_obj.get_docgroup_id(),period=doucment_obj.get_file_id(),
            remarks=doucment_obj.get_remarks(), file_id=doucment_obj.get_file_id(),modify_status=-1,modified_by=-1,
            modify_ref_id = -1, portal_flag=doucment_obj.get_portal_flag())
            doc_file=VendorFileAttachment.objects.using(self._current_app_schema()).filter(Q(representtabel_id=new_id)&Q(tab_type=VendorRefType.VENDOR_DOCUMENT)&Q(entity_id=self._entity_id())).update(representtabel_id=old_id)



            self.audit_function(document_update, vendor_id, user_id, req_status, old_id, ModifyStatus.update)
            # self.audit_function(document, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)

        elif mod_status == ModifyStatus.create:
            document_update=VendorDocument.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).update(modify_status=-1,
                modify_ref_id=-1,modified_by=-1)

            self.audit_function(document_update, vendor_id, user_id, req_status, new_id, ModifyStatus.update)

        else:
            document=VendorDocument.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).delete()

            self.audit_function(document, vendor_id, user_id, req_status, old_id, ModifyStatus.delete)
        return

    def modification_reject_document(self, mod_status, old_id, new_id,vendor_id,user_id):


        req_status = RequestStatusUtil.MODIFICATION
        if mod_status == ModifyStatus.update:
            document = VendorDocument.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()
            document_update=VendorDocument.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(modify_ref_id=-1)

            self.audit_function(document, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)
            self.audit_function(document_update, vendor_id, user_id, req_status, old_id, ModifyStatus.update)

        elif mod_status == ModifyStatus.create:
            document = VendorDocument.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()

            self.audit_function(document, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)
        else:
            document_update=VendorDocument.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(modify_ref_id=-1)

            self.audit_function(document_update, vendor_id, user_id, req_status, old_id, ModifyStatus.update)
        return

    def audit_function(self, doucment, vendor_id, user_id, req_status, id, action):

        if action == ModifyStatus.delete:
            data = None
        elif action == ModifyStatus.update:
            data = doucment
        else:
            data = doucment.__dict__
            del data['_state']
        audit_service = VendorAuditService(self._scope())
        audit_obj = VendorAuditResponse()
        audit_obj.set_refid(vendor_id)
        audit_obj.set_reftype(VendorRefType.VENDOR)
        audit_obj.set_userid(user_id)
        audit_obj.set_reqstatus(req_status)
        audit_obj.set_relrefid(id)
        audit_obj.set_relreftype(VendorRefType.VENDOR_DOCUMENT)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_vendoraudit(audit_obj)
        return

    def document_upload(self, resp_obj, tab_type,request, doc_obj):
        data= request.FILES['file']
        # file_name=request.FILES['file'].name
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

    def multiple_document_upload(self, resp_obj, tab_type, request, doc_obj, attachment):
        data = request.FILES[attachment]
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
