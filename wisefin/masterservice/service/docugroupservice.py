import django
from django.db import IntegrityError
from django.db.models import Q
from vendorservice.service.vendorservice import VendorService
from masterservice.models import DocumentGroup
from masterservice.data.response.docugroupresponse import DocumentGroupResponse
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from datetime import datetime

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

now = datetime.now()
from masterservice.data.request.masterauditrequest import MasterAuditRequest
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.util.masterutil import ModifyStatus,MasterRefType,RequestStatusUtil
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator

class DocumentGroupService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_docugroup(self, docugroup_obj, user_id):
        if not docugroup_obj.get_id() is None:
            try:
                docugroup_update = DocumentGroup.objects.using(self._current_app_schema()).filter(
                    id=docugroup_obj.get_id(), entity_id=self._entity_id()).update(
                    partnertype=docugroup_obj.get_partnertype(),
                    name=docugroup_obj.get_name(),
                    parent_id=docugroup_obj.get_parent_id(),
                    docname=docugroup_obj.get_docname(),
                    isparent=docugroup_obj.get_isparent(),
                    period=docugroup_obj.get_period(),
                    mand=docugroup_obj.get_mand(),
                    updated_date=now,
                    updated_by=user_id)

                docugroup_var = DocumentGroup.objects.using(self._current_app_schema()).get(id=docugroup_obj.get_id(),
                                                                                            entity_id=self._entity_id())
                docugroup_auditdata = {'id': docugroup_obj.get_id(),
                                       'partnertype': docugroup_obj.get_partnertype(),
                                       'name': docugroup_obj.get_name(),
                                       'parent_id': docugroup_obj.get_parent_id(),
                                       'docname': docugroup_obj.get_docname(),
                                       'isparent': docugroup_obj.get_isparent(),
                                       'period': docugroup_obj.get_period(),
                                       'mand': docugroup_obj.get_mand(),
                                       'updated_date': now,
                                       'updated_by': user_id}
                self.audit_function(docugroup_auditdata, user_id, docugroup_var.id, ModifyStatus.update)

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except DocumentGroup.DoesNotExist:
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
                docugroup_var = DocumentGroup.objects.using(self._current_app_schema()).create(
                    partnertype=docugroup_obj.get_partnertype(),
                    name=docugroup_obj.get_name(),
                    parent_id=docugroup_obj.get_parent_id(),
                    docname=docugroup_obj.get_docname(),
                    isparent=docugroup_obj.get_isparent(),
                    period=docugroup_obj.get_period(),
                    mand=docugroup_obj.get_mand(), created_by=user_id, entity_id=self._entity_id())
                self.audit_function(docugroup_var, user_id, docugroup_var.id, ModifyStatus.create)

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

        docugroup_data = DocumentGroupResponse()
        docugroup_data.set_id(docugroup_var.id)
        docugroup_data.set_name(docugroup_var.name)
        docugroup_data.set_partnertype(docugroup_var.partnertype)
        docugroup_data.set_isparent(docugroup_var.isparent)
        docugroup_data.set_parent_id(docugroup_var.parent_id)
        docugroup_data.set_docname(docugroup_var.docname)
        docugroup_data.set_period(docugroup_var.period)
        docugroup_data.set_mand(docugroup_var.mand)
        return docugroup_data

    def fetch_docugroup_list(self, vys_page):
        docugrouplist = DocumentGroup.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id()).order_by('created_date')[
                        vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(docugrouplist)
        if list_length <= 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DOCUMENTGROUP_ID)
            error_obj.set_description(ErrorDescription.INVALID_DOCUMENTGROUP_ID)
            return error_obj
        else:
            docugroup_list_data = NWisefinList()
            for docugroupobj in docugrouplist:
                docugroup_data = DocumentGroupResponse()
                docugroup_data.set_id(docugroupobj.id)
                docugroup_data.set_name(docugroupobj.name)
                docugroup_data.set_partnertype(docugroupobj.partnertype)
                docugroup_data.set_isparent(docugroupobj.isparent)
                docugroup_data.set_parent_id(docugroupobj.parent_id)
                docugroup_data.set_docname(docugroupobj.docname)
                docugroup_data.set_period(docugroupobj.period)
                docugroup_data.set_mand(docugroupobj.mand)
                docugroup_list_data.append(docugroup_data)
                vpage = NWisefinPaginator(docugrouplist, vys_page.get_index(), 10)
                docugroup_list_data.set_pagination(vpage)
            return docugroup_list_data

    def fetch_docugroup(self, docugroup_id):
        try:
            docugroup_var = DocumentGroup.objects.using(self._current_app_schema()).get(id=docugroup_id,
                                                                                        entity_id=self._entity_id())
            docugroup_data = DocumentGroupResponse()
            docugroup_data.set_id(docugroup_var.id)
            docugroup_data.set_name(docugroup_var.name)
            docugroup_data.set_partnertype(docugroup_var.partnertype)
            docugroup_data.set_isparent(docugroup_var.isparent)
            docugroup_data.set_parent_id(docugroup_var.parent_id)
            docugroup_data.set_docname(docugroup_var.docname)
            docugroup_data.set_period(docugroup_var.period)
            docugroup_data.set_mand(docugroup_var.mand)
            return docugroup_data

        except DocumentGroup.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DOCUMENTGROUP_ID)
            error_obj.set_description(ErrorDescription.INVALID_DOCUMENTGROUP_ID)
            return error_obj

    def delete_docugroup(self, docugrp_id, user_id):
        docugroup = DocumentGroup.objects.using(self._current_app_schema()).filter(id=docugrp_id,
                                                                                   entity_id=self._entity_id()).delete()
        self.audit_function(docugroup, user_id, docugrp_id, ModifyStatus.delete)

        if docugroup[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DOCUMENTGROUP_ID)
            error_obj.set_description(ErrorDescription.INVALID_DOCUMENTGROUP_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def audit_function(self, data_obj, user_id, id, action):
        if action == ModifyStatus.delete:
            data = None
        elif action == ModifyStatus.update:
            data = data_obj
        else:
            data = data_obj.__dict__
            del data['_state']
        audit_service = MasterAuditService(self._scope())  # changed
        audit_obj = MasterAuditResponse()
        audit_obj.set_refid(-1)
        audit_obj.set_reftype(MasterRefType.MASTER)
        audit_obj.set_userid(user_id)
        audit_obj.set_reqstatus(RequestStatusUtil.ONBOARD)
        audit_obj.set_relrefid(id)
        audit_obj.set_relreftype(MasterRefType.DOCUMENT_GROUP)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return

    def fetch_documentgroup_list(self, vys_page, query):
        print(self._entity_id())
        # vendor_service = VendorService(self._scope())
        # category = vendor_service.get_vendor_category(vendor_id)
        condition = Q(status=1) & Q(entity_id=self._entity_id()) &Q(partnertype='re')
        # if category == False:
        #     condition &= Q(partnertype='re')
        if query:
            condition &= Q(name__icontains=query)

        docugrouplist = DocumentGroup.objects.using(self._current_app_schema()).filter(condition).order_by('mand')[
                        vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(docugrouplist)
        docugroup_list_data = NWisefinList()
        if list_length > 0:
            for docugroupobj in docugrouplist:
                docugroup_data = DocumentGroupResponse()
                docugroup_data.set_id(docugroupobj.id)
                docugroup_data.set_name(docugroupobj.name)
                docugroup_data.set_partnertype(docugroupobj.partnertype)
                docugroup_data.set_isparent(docugroupobj.isparent)
                docugroup_data.set_parent_id(docugroupobj.parent_id)
                docugroup_data.set_docname(docugroupobj.docname)
                docugroup_data.set_period(docugroupobj.period)
                docugroup_data.set_mand(docugroupobj.mand)
                docugroup_list_data.append(docugroup_data)
                vpage = NWisefinPaginator(docugrouplist, vys_page.get_index(), 10)
                docugroup_list_data.set_pagination(vpage)
        return docugroup_list_data

    def fetch_docugroup_ids(self, docugroup_ids,vys_page):
        docugrouplist = DocumentGroup.objects.using(self._current_app_schema()).filter(id__in=docugroup_ids,
                                                                                    entity_id=self._entity_id())[
                    vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(docugrouplist)
        docugroup_list_data = NWisefinList()
        if list_length > 0:
            for docugroupobj in docugrouplist:
                docugroup_data = DocumentGroupResponse()
                docugroup_data.set_id(docugroupobj.id)
                docugroup_data.set_name(docugroupobj.name)
                docugroup_data.set_partnertype(docugroupobj.partnertype)
                docugroup_data.set_isparent(docugroupobj.isparent)
                docugroup_data.set_parent_id(docugroupobj.parent_id)
                docugroup_data.set_docname(docugroupobj.docname)
                docugroup_data.set_period(docugroupobj.period)
                docugroup_data.set_mand(docugroupobj.mand)
                docugroup_list_data.append(docugroup_data)
                vpage = NWisefinPaginator(docugrouplist, vys_page.get_index(), 10)
                docugroup_list_data.set_pagination(vpage)
        return docugroup_list_data

