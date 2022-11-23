from django.db import IntegrityError

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from vendorservice.data.response.contacttyperesponse import contactTypeResponse
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from masterservice.models import ContactType
from django.utils import timezone
from masterservice.data.request.masterauditrequest import MasterAuditRequest
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.util.masterutil import ModifyStatus,MasterRefType,RequestStatusUtil
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator

class ContactTypeService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_contacttype(self, contacttype_obj, user_id):
        if not contacttype_obj.get_id() is None:
            try:
                contacttype_update = ContactType.objects.using(self._current_app_schema()).filter(
                    id=contacttype_obj.get_id(), entity_id=self._entity_id()). \
                    update(  # code =contacttype_obj.get_code (),
                    name=contacttype_obj.get_name(), remarks=contacttype_obj.get_remarks(),
                    updated_by=user_id, updated_date=timezone.now())

                contacttype = ContactType.objects.using(self._current_app_schema()).get(id=contacttype_obj.get_id(),
                                                                                        entity_id=self._entity_id())

                contacttype_auditdata = {'id': contacttype_obj.get_id(),
                                         # 'code': contacttype_obj.get_code(),
                                         'name': contacttype_obj.get_name(),
                                         'remarks': contacttype_obj.get_remarks(),
                                         'updated_date': timezone.now(),
                                         'updated_by': user_id}

                self.audit_function(contacttype_auditdata, user_id, contacttype.id, ModifyStatus.update)
            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except ContactType.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_contacttype_ID)
                error_obj.set_description(ErrorDescription.INVALID_contacttype_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                contacttype = ContactType.objects.using(self._current_app_schema()).create(
                    # code =contacttype_obj.get_code (),
                    name=contacttype_obj.get_name(), remarks=contacttype_obj.get_remarks(),
                    created_by=user_id, entity_id=self._entity_id()
                )
                try:
                    max_cat_code = ContactType.objects.using(self._current_app_schema()).filter(code__icontains='CONT').order_by('-code')[0].code
                    rnsl = int(max_cat_code[4:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "CONT" + str(new_rnsl).zfill(4)
                contacttype.code = code
                contacttype.save()
                self.audit_function(contacttype, user_id, contacttype.id, ModifyStatus.create)
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

        contacttype_data = contactTypeResponse()
        contacttype_data.set_id(contacttype.id)
        contacttype_data.set_code(contacttype.code)
        contacttype_data.set_name(contacttype.name)
        contacttype_data.set_remarks(contacttype.remarks)

        return contacttype_data

    def fetch_contacttype_list(self, user_id, vys_page):
        contacttypelist = ContactType.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id()).order_by('created_date')[
                          vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(contacttypelist)
        if list_length <= 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_contacttype_ID)
            error_obj.set_description(ErrorDescription.INVALID_contacttype_ID)
            return error_obj
        else:
            contacttype_list_data = NWisefinList()
            for contacttype in contacttypelist:
                contacttype_data = contactTypeResponse()
                contacttype_data.set_id(contacttype.id)
                contacttype_data.set_code(contacttype.code)
                contacttype_data.set_name(contacttype.name)
                contacttype_data.set_remarks (contacttype.remarks)
                contacttype_list_data.append(contacttype_data)
                vpage = NWisefinPaginator(contacttypelist, vys_page.get_index(), 10)
                contacttype_list_data.set_pagination(vpage)
            return contacttype_list_data

    def fetch_contacttype(self, contacttype_id, user_id):
        try:
            contacttype = ContactType.objects.using(self._current_app_schema()).get(id=contacttype_id,
                                                                                    entity_id=self._entity_id())
            contacttype_data = contactTypeResponse()
            contacttype_data.set_id(contacttype.id)
            contacttype_data.set_code(contacttype.code)
            contacttype_data.set_name(contacttype.name)
            contacttype_data.set_remarks(contacttype.remarks)
            return contacttype_data

        except ContactType.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_contacttype_ID)
            error_obj.set_description(ErrorDescription.INVALID_contacttype_ID)
            return error_obj

    def delete_contacttype(self, contacttype_id, user_id):
        contacttype = ContactType.objects.using(self._current_app_schema()).filter(id=contacttype_id,
                                                                                   entity_id=self._entity_id()).delete()
        self.audit_function(contacttype, user_id, contacttype_id, ModifyStatus.delete)
        if contacttype[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_contacttype_ID)
            error_obj.set_description(ErrorDescription.INVALID_contacttype_ID)
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
        audit_obj.set_relreftype(MasterRefType.CONTACTTYPE)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return

    def fetch_contacttype_search(self, query, vys_page):
        if query is None:
            contacttypelist = ContactType.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id()).order_by('created_date')[
                              vys_page.get_offset():vys_page.get_query_limit()]
        else:
            contacttypelist = ContactType.objects.using(self._current_app_schema()).filter(name__icontains=query,
                                                                                           entity_id=self._entity_id()).order_by(
                'created_date')[
                              vys_page.get_offset():vys_page.get_query_limit()]
        contacttype_list_data = NWisefinList()
        for contacttype in contacttypelist:
            contacttype_data = contactTypeResponse()
            contacttype_data.set_id(contacttype.id)
            contacttype_data.set_code(contacttype.code)
            contacttype_data.set_name(contacttype.name)
            contacttype_list_data.append(contacttype_data)
            vpage = NWisefinPaginator(contacttypelist, vys_page.get_index(), 10)
            contacttype_list_data.set_pagination(vpage)
        return contacttype_list_data
