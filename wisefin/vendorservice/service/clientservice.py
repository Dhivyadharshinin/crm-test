import django
from django.db import IntegrityError
from nwisefin.settings import logger
from userservice.models import Employee
from vendorservice.data.response.supplierresponse import ContractorResponse, ClientResponse
from vendorservice.data.response.vendorauditresponse import VendorAuditResponse
from vendorservice.models import VendorSubContractor, VendorClient, VendorQueue, VendorModificationRel
from vendorservice.util.vendorutil import VendorRefType, ModifyStatus, RequestStatusUtil
from django.utils import timezone
from vendorservice.service.supplierservice import AddressService
from vendorservice.service.vendorservice import VendorService
from vendorservice.data.request.vendorauditrequest import VendorAuditRequest
from vendorservice.service.vendorauditservice import VendorAuditService
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.utilityservice import NWisefinUtilityService
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from django.db.models import Q


class ContractorService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def create_contractor(self, contractor_obj,vendor_id,user_id):
        req_status = RequestStatusUtil.ONBOARD

        if not contractor_obj.get_id() is None:
            try:
                contractor_update = VendorSubContractor.objects.using(self._current_app_schema()).filter(id=contractor_obj.get_id(), entity_id=self._entity_id()).update(name=contractor_obj.get_name(),
                service=contractor_obj.get_service(),remarks=contractor_obj.get_remarks(),
                updated_by=user_id , updated_date=timezone.now(),vendor_id=vendor_id, portal_flag=contractor_obj.get_portal_flag())

                contractor_auditdata={'id':contractor_obj.get_id(),'name':contractor_obj.get_name(),
                'service':contractor_obj.get_service(),'remarks':contractor_obj.get_remarks(),
                'updated_by':user_id , 'updated_date':timezone.now(),'vendor_id':vendor_id}

                contractor = VendorSubContractor.objects.using(self._current_app_schema()).get(id=contractor_obj.get_id(), entity_id=self._entity_id())

                self.audit_function(contractor_auditdata, vendor_id, user_id, req_status, contractor.id, ModifyStatus.update)


            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except VendorSubContractor.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_SUPPLIERSUBCONTRACTOR_ID)
                error_obj.set_description(ErrorDescription.INVALID_SUPPLIERSUBCONTRACTOR_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                contractor = VendorSubContractor.objects.using(self._current_app_schema()).create(name=contractor_obj.get_name(),
                service=contractor_obj.get_service(),remarks=contractor_obj.get_remarks(),created_by=user_id,
                vendor_id=vendor_id, entity_id=self._entity_id(),portal_flag=contractor_obj.get_portal_flag())

                self.audit_function(contractor, vendor_id, user_id, req_status, contractor.id, ModifyStatus.create)
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

        contractor_data = ContractorResponse()
        contractor_data.set_id(contractor.id)
        contractor_data.set_name(contractor.name)
        contractor_data.set_service(contractor.service)
        contractor_data.set_remarks(contractor.remarks)
        contractor_data.set_vendor_id(contractor.vendor_id)
        contractor_data.set_portal_flag(contractor.portal_flag)

        return contractor_data


    # def fetch_contractor_list(self,user_id):
    #     contractorlist = VendorSubContractor.objects.all()
    #     list_length = len(contractorlist)
    #     logger.info(list_length)
    #     if list_length <= 0:
    #         error_obj = Error()
    #         error_obj.set_code(ErrorMessage.INVALID_SUPPLIERSUBCONTRACTOR_ID)
    #         error_obj.set_description(ErrorDescription.INVALID_SUPPLIERSUBCONTRACTOR_ID)
    #         return error_obj
    #     else:
    #         contractor_list_data = VysfinList()
    #         for contractor in contractorlist:
    #             contractor_data = ContractorResponse()
    #             contractor_data.set_id(contractor.id)
    #             contractor_data.set_name(contractor.name)
    #             contractor_data.set_service(contractor.service)
    #             contractor_data.set_remarks(contractor.remarks)
    #
    #             contractor_list_data.append(contractor_data)
    #         return contractor_list_data

    def fetch_contractor_list(self,request, vys_page,user_id,vendor_id):
        # queue_arr = VendorQueue.objects.select_related('vendor__id').filter(
        #     Q(from_user_id__exact=user_id) | Q(to_user_id__exact=user_id)).values('vendor_id').distinct()
        queue_arr = VendorSubContractor.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id, entity_id=self._entity_id()).values('id')
        condition = None
        for vendor in queue_arr:
            logger.info(str(vendor))
            if condition is None:
                condition = (Q(id__exact=vendor['id'])& (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1))&Q(entity_id=self._entity_id())
            else:
                condition |= (Q(id__exact=vendor['id'])& (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1))&Q(entity_id=self._entity_id())
        if condition is not None:
            contractlist = VendorSubContractor.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        else:
            contractlist = []

        vlist = NWisefinList()
        user_list = []
        for vendor in contractlist:
            user_list.append(vendor.created_by)
        user_list = set(user_list)
        user_list = list(user_list)
        utility_service = NWisefinUtilityService()
        user_list_obj = utility_service.get_user_info(request,user_list)

        for contractor in contractlist:
            contractor_data = ContractorResponse()
            contractor_data.set_id(contractor.id)
            contractor_data.set_name(contractor.name)
            contractor_data.set_service(contractor.service)
            contractor_data.set_remarks(contractor.remarks)
            contractor_data.set_vendor_id(contractor.vendor_id)
            contractor_data.set_created_by(contractor.created_by)
            contractor_data.set_modify_ref_id(contractor.modify_ref_id)
            contractor_data.set_modify_status(contractor.modify_status)
            contractor_data.set_portal_flag(contractor.portal_flag)

            for ul in user_list_obj['data']:
                if ul['id'] == VendorSubContractor.created_by:
                    contractor_data.set_created_by(ul)
            vlist.append(contractor_data)
        vpage = NWisefinPaginator(contractlist, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)

        return vlist

#modification#
    def fetch_contractor_list_modification(self,request, vys_page,user_id,vendor_id):
        # queue_arr = VendorQueue.objects.select_related('vendor__id').filter(
        #     Q(from_user_id__exact=user_id) | Q(to_user_id__exact=user_id)).values('vendor_id').distinct()
        queue_arr = VendorSubContractor.objects.using(self._current_app_schema()).filter(Q(vendor_id=vendor_id) & Q(modify_status=1)&Q(entity_id=self._entity_id())).values('id')
        condition = None
        for vendor in queue_arr:
            logger.info(str(vendor))
            if condition is None:
                condition = Q(id__exact=vendor['id']) &Q(entity_id=self._entity_id())
            else:
                condition |= Q(id__exact=vendor['id']) &Q(entity_id=self._entity_id())
        if condition is not None:
            contractlist = VendorSubContractor.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        else:
            contractlist = []

        vlist = NWisefinList()
        user_list = []
        for vendor in contractlist:
            user_list.append(vendor.created_by)
        user_list = set(user_list)
        user_list = list(user_list)
        utility_service = NWisefinUtilityService()
        user_list_obj = utility_service.get_user_info(request,user_list)

        for contractor in contractlist:
            contractor_data = ContractorResponse()
            contractor_data.set_id(contractor.id)
            contractor_data.set_name(contractor.name)
            contractor_data.set_service(contractor.service)
            contractor_data.set_remarks(contractor.remarks)
            contractor_data.set_vendor_id(contractor.vendor_id)
            contractor_data.set_created_by(contractor.created_by)
            contractor_data.set_portal_flag(contractor.portal_flag)
            vlist.append(contractor_data)

            # for ul in user_list_obj['data']:
            #     if ul['id'] == VendorSubContractor.created_by:
            #         contractor_data.set_created_by(ul)
            # vlist.append(contractor_data)
            # vpage = VysfinPaginator(contractlist, vys_page.get_index(), 10)
            # vlist.set_pagination(vpage)
        return vlist




    def fetch_contractor(self, contractor_id,user_id,vendor_id):
        try:
            contractor = VendorSubContractor.objects.using(self._current_app_schema()).get(id=contractor_id, entity_id=self._entity_id())
            contractor_data = ContractorResponse()
            contractor_data.set_id(contractor.id)
            contractor_data.set_name(contractor.name)
            contractor_data.set_service(contractor.service)
            contractor_data.set_remarks(contractor.remarks)
            contractor_data.set_modify_ref_id(contractor.modify_ref_id)
            contractor_data.set_modify_status(contractor.modify_status)
            contractor_data.set_vendor_id(contractor.vendor_id)
            contractor_data.set_created_by(contractor.created_by)
            contractor_data.set_portal_flag(contractor.portal_flag)

            return contractor_data
        except VendorSubContractor.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_SUPPLIERSUBCONTRACTOR_ID)
            error_obj.set_description(ErrorDescription.INVALID_SUPPLIERSUBCONTRACTOR_ID)
            return error_obj

    def delete_contractor(self, contractor_id,vendor_id,user_id):

        contractor = VendorSubContractor.objects.using(self._current_app_schema()).filter(id=contractor_id, entity_id=self._entity_id()).delete()

        req_status = RequestStatusUtil.ONBOARD
        self.audit_function(contractor, vendor_id, user_id, req_status, contractor_id, ModifyStatus.delete)

        if contractor[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_SUPPLIERSUBCONTRACTOR_ID)
            error_obj.set_description(ErrorDescription.INVALID_SUPPLIERSUBCONTRACTOR_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)

            return success_obj

    # modification

    def contractor_modification(self,contractor_obj,vendor_id,user_id):
        vendor_service = VendorService(self._scope())

        if not contractor_obj.get_id() is None:
            try:
                ref_flag=vendor_service.checkmodify_rel(VendorRefType.VENDOR_CONTRACT,contractor_obj.get_id())
                if ref_flag==True:
                    contractor = VendorSubContractor.objects.using(self._current_app_schema()).filter(id=contractor_obj.get_id(), entity_id=self._entity_id()).update(name=contractor_obj.get_name(),
                                                                    service=contractor_obj.get_service(),
                                                                    remarks=contractor_obj.get_remarks(),
                                                                    portal_flag=contractor_obj.get_portal_flag()
                                                                    )

                else:
                    contractor = VendorSubContractor.objects.using(self._current_app_schema()).create(name=contractor_obj.get_name(),
                    service=contractor_obj.get_service(),remarks=contractor_obj.get_remarks(),created_by=user_id,
                    vendor_id=vendor_id,modify_status=ModifyStatus.update,modify_ref_id=contractor_obj.get_id(),
                                                                    modified_by=user_id, entity_id=self._entity_id(),portal_flag=contractor_obj.get_portal_flag())
                    contractor_update =VendorSubContractor.objects.using(self._current_app_schema()).filter(id=contractor_obj.get_id(), entity_id=self._entity_id()).update(
                        modify_ref_id=contractor.id)
                    VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=contractor_obj.get_id(),
                                                         ref_type=VendorRefType.VENDOR_CONTRACT,
                                                         mod_status=ModifyStatus.update,
                                                         modify_ref_id=contractor.id, entity_id=self._entity_id())

                contractorupdate_auditdata={'id':contractor_obj.get_id(),'modify_ref_id':contractor.id}


                req_status = RequestStatusUtil.MODIFICATION
                self.audit_function(contractor, vendor_id, user_id, req_status, contractor.id, ModifyStatus.create)
                self.audit_function(contractorupdate_auditdata, vendor_id, user_id, req_status, contractor_obj.get_id(), ModifyStatus.update)

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
        else:
            try:
                contractor = VendorSubContractor.objects.using(self._current_app_schema()).create(name=contractor_obj.get_name(),
                service=contractor_obj.get_service(),remarks=contractor_obj.get_remarks(),created_by=user_id,
                vendor_id=vendor_id,modify_status=ModifyStatus.create,modified_by=user_id, entity_id=self._entity_id(),portal_flag=contractor_obj.get_portal_flag())

                contractor_update=VendorSubContractor.objects.using(self._current_app_schema()).filter(id=contractor.id, entity_id=self._entity_id()).update(modify_ref_id=contractor.id)

                VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=contractor.id,
                                                     ref_type=VendorRefType.VENDOR_CONTRACT, mod_status=ModifyStatus.create,
                                                     modify_ref_id=contractor.id, entity_id=self._entity_id())


                req_status = RequestStatusUtil.MODIFICATION
                self.audit_function(contractor, vendor_id, user_id, req_status, contractor.id, ModifyStatus.create)
                self.audit_function(contractor_update, vendor_id, user_id, req_status, contractor.id, ModifyStatus.update)

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


        contractor_data = ContractorResponse()
        contractor_data.set_id(contractor.id)
        contractor_data.set_name(contractor.name)
        contractor_data.set_service(contractor.service)
        contractor_data.set_remarks(contractor.remarks)
        contractor_data.set_vendor_id(contractor.vendor_id)
        contractor_data.set_portal_flag(contractor.portal_flag)

        return contractor_data

    def modification_delete_contractor(self, contractor_id, vendor_id,user_id):
        # try:
            vendor_service=VendorService(self._scope())
            ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_CONTRACT, contractor_id)

            contractor = VendorSubContractor.objects.using(self._current_app_schema()).filter(id=contractor_id, entity_id=self._entity_id()).update(modify_ref_id=contractor_id,
                                                                             modify_status=ModifyStatus.delete)
            if ref_flag==True:

                flag_obj = VendorModificationRel.objects.using(self._current_app_schema()).filter(Q(modify_ref_id=contractor_id)&Q(ref_type=VendorRefType.VENDOR_CONTRACT)&Q(entity_id=self._entity_id())).update(mod_status=ModifyStatus.delete)
            else:
                VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=contractor_id,
                                                 ref_type=VendorRefType.VENDOR_CONTRACT, mod_status=ModifyStatus.delete,
                                                 modify_ref_id=contractor_id, entity_id=self._entity_id())

            req_status = RequestStatusUtil.MODIFICATION
            # self.audit_function(contractor, vendor_id, user_id, req_status, contractor.id, ModifyStatus.update)

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

        # except:
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
        #     return error_obj


    def modification_action_contractor(self, mod_status, old_id, new_id,vendor_id,user_id):

        if mod_status == ModifyStatus.update:
            contractor_obj = self.fetch_contractor(new_id,user_id,vendor_id)

            contractor_update = VendorSubContractor.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(name=contractor_obj.get_name(),
                               service=contractor_obj.get_service(),remarks=contractor_obj.get_remarks(),
                                modify_status=-1,modify_ref_id=-1,modified_by=-1,portal_flag=contractor_obj.get_portal_flag())



            req_status = RequestStatusUtil.MODIFICATION
            self.audit_function(contractor_update, vendor_id, user_id, req_status, old_id, ModifyStatus.update)
            # self.audit_function(contractor_del, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)

        elif mod_status == ModifyStatus.create:
            contractor_update=VendorSubContractor.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).update(modify_status=-1,
                                                            modify_ref_id=-1,modified_by=-1)
            req_status = RequestStatusUtil.MODIFICATION
            self.audit_function(contractor_update, vendor_id, user_id, req_status, new_id, ModifyStatus.update)
        else:
            contractor = VendorSubContractor.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).delete()

            req_status = RequestStatusUtil.MODIFICATION
            self.audit_function(contractor, vendor_id, user_id, req_status, old_id, ModifyStatus.delete)

    def modification_reject_contractor(self, mod_status, old_id, new_id, vendor_id, user_id):

        if mod_status == ModifyStatus.update:
            contractor_del=VendorSubContractor.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()
            contractor =VendorSubContractor.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(modify_ref_id=-1,modified_by=-1)


            req_status = RequestStatusUtil.MODIFICATION
            self.audit_function(contractor_del, vendor_id, user_id, req_status, old_id, ModifyStatus.delete)
            self.audit_function(contractor, vendor_id, user_id, req_status, old_id, ModifyStatus.update)

        elif mod_status == ModifyStatus.create:
            contractor = VendorSubContractor.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()

            req_status = RequestStatusUtil.MODIFICATION
            self.audit_function(contractor, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)
        else:
            contractor=VendorSubContractor.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(modify_ref_id=-1,modified_by=-1)

            req_status = RequestStatusUtil.MODIFICATION
            self.audit_function(contractor, vendor_id, user_id, req_status, old_id, ModifyStatus.update)



    def audit_function(self, contractor, vendor_id, user_id, req_status, id, action):
        if action == ModifyStatus.delete:
            data = None
        elif action == ModifyStatus.update:
            data = contractor
        else:
            data = contractor.__dict__
            del data['_state']
        audit_service = VendorAuditService(self._scope())
        audit_obj = VendorAuditResponse()
        audit_obj.set_refid(vendor_id)
        audit_obj.set_reftype(VendorRefType.VENDOR)
        audit_obj.set_userid(user_id)
        audit_obj.set_reqstatus(req_status)
        audit_obj.set_relrefid(id)
        audit_obj.set_relreftype(VendorRefType.VENDOR_CONTRACT)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_vendoraudit(audit_obj)

        return


class ClientService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def create_client(self, client_obj,client_json,user_id,vendor_id,add_id):

        req_status = RequestStatusUtil.ONBOARD
        if not client_obj.get_id() is None:
            # try:
                client_update = VendorClient.objects.using(self._current_app_schema()).filter(id=client_obj.get_id(), entity_id=self._entity_id()).update(name=client_obj.get_name()
                ,address_id=add_id,updated_by=user_id , updated_date=timezone.now(),vendor_id=vendor_id,
                portal_flag=client_obj.get_portal_flag()
                )

                client_auditdata={'id':client_obj.get_id(),'name':client_obj.get_name()
                ,'address_id':add_id,'updated_by':user_id , 'updated_date':timezone.now(),'vendor_id':vendor_id}

                client = VendorClient.objects.using(self._current_app_schema()).get(id=client_obj.get_id(), entity_id=self._entity_id())

                self.audit_function(client_auditdata, vendor_id, user_id, req_status, client.id, ModifyStatus.update)




            # except IntegrityError as error:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except VendorClient.DoesNotExist:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_SUPPLIERCLIENT_ID)
            #     error_obj.set_description(ErrorDescription.INVALID_SUPPLIERCLIENT_ID)
            #     return error_obj
            # except:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj
        else:
            # try:
                client = VendorClient.objects.using(self._current_app_schema()).create(name=client_obj.get_name(),address_id=add_id,created_by=user_id,
                                                     vendor_id=vendor_id, entity_id=self._entity_id(),
                                                     portal_flag=client_obj.get_portal_flag()
                )
                self.audit_function(client, vendor_id, user_id, req_status, client.id, ModifyStatus.create)

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

        client_data = ClientResponse()
        client_data.set_id(client.id)
        client_data.set_name(client.name)
        client_data.set_address_id(client.address_id)
        client_data.set_vendor_id(client.vendor_id)
        client_data.set_portal_flag(client.portal_flag)




        return client_data


    # def fetch_client_list(self,user_id):
    #         clientlist = VendorClient.objects.all()
    #         list_length = len(clientlist)
    #         logger.info(list_length)
    #         if list_length <= 0:
    #             error_obj = Error()
    #             error_obj.set_code(ErrorMessage.INVALID_SUPPLIERCLIENT_ID)
    #             error_obj.set_description(ErrorDescription.INVALID_SUPPLIERCLIENT_ID)
    #             return error_obj
    #         else:
    #             client_list_data = VysfinList()
    #             for client in clientlist:
    #                 client_data = ClientResponse()
    #                 client_data.set_id(client.id)
    #                 client_data.set_name(client.name)
    #                 client_data.set_address_id(client.address_id)
    #
    #                 client_list_data.append(client_data)
    #             return client_list_data

    #monesh##

    def fetch_client_list(self,request, vys_page,user_id,vendor_id):
        queue_arr = VendorClient.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id, entity_id=self._entity_id()).values('id')
        condition = None
        for vendor in queue_arr:
            logger.info(str(vendor))
            if condition is None:
                condition = (Q(id__exact=vendor['id'])& (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1))&Q(entity_id=self._entity_id())
            else:
                condition |= (Q(id__exact=vendor['id'])& (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1))&Q(entity_id=self._entity_id())
        if condition is not None:
            clientlist = VendorClient.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        else:
            clientlist = []
        vlist = NWisefinList()
        user_list = []
        for vendor in clientlist:
            user_list.append(vendor.created_by)
        user_list = set(user_list)
        user_list = list(user_list)
        utility_service = NWisefinUtilityService()
        user_list_obj = utility_service.get_user_info(request,user_list)

        for client in clientlist:
            client_data = ClientResponse()
            client_data.set_id(client.id)
            client_data.set_name(client.name)
            client_data.set_address_id(client.address_id)
            client_data.set_vendor_id(client.vendor_id)
            client_data.set_created_by(client.created_by)
            client_data.set_modify_ref_id(client.modify_ref_id)
            client_data.set_modify_status(client.modify_status)
            client_data.set_portal_flag(client.portal_flag)

            for ul in user_list_obj['data']:
                if ul['id'] == VendorClient.created_by:
                    client_data.set_created_by(ul)
            vlist.append(client_data)
        vpage = NWisefinPaginator(clientlist, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist




    def fetch_client(self, client_id):
        try:
            client = VendorClient.objects.using(self._current_app_schema()).get(id=client_id, entity_id=self._entity_id())
            client_data = ClientResponse()
            client_data.set_id(client.id)
            client_data.set_name(client.name)
            client_data.set_address_id(client.address_id)
            client_data.set_vendor_id(client.vendor_id)
            client_data.set_created_by(client.created_by)
            client_data.set_modify_ref_id(client.modify_ref_id)
            client_data.set_modify_status(client.modify_status)
            client_data.set_portal_flag(client.portal_flag)

            return client_data
        except VendorClient.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_SUPPLIERCLIENT_ID)
            error_obj.set_description(ErrorDescription.INVALID_SUPPLIERCLIENT_ID)
            return error_obj

    def delete_client(self, client_id,vendor_id,user_id):

        client = VendorClient.objects.using(self._current_app_schema()).filter(id=client_id, entity_id=self._entity_id()).delete()
        if client[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_SUPPLIERCLIENT_ID)
            error_obj.set_description(ErrorDescription.INVALID_SUPPLIERCLIENT_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)

            Audit_Action = ModifyStatus.delete
            req_status = RequestStatusUtil.ONBOARD
            self.audit_function(client, vendor_id, user_id, req_status, client_id, Audit_Action)
            return success_obj


    def client_modification(self,client_obj,user_id,vendor_id,add_id):


        req_status = RequestStatusUtil.MODIFICATION
        vendor_service = VendorService(self._scope())
        if not client_obj.get_id() is None:
            # try:
                ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_CLIENT, client_obj.get_id())
                if ref_flag==True:
                    client = VendorClient.objects.using(self._current_app_schema()).filter(id=client_obj.get_id(), entity_id=self._entity_id()).update(name=client_obj.get_name(), address_id=add_id)
                    client = VendorClient.objects.using(self._current_app_schema()).get(id=client_obj.get_id(), entity_id=self._entity_id())
                else:
                    client = VendorClient.objects.using(self._current_app_schema()).create(name=client_obj.get_name(), address_id=add_id,
                                                         created_by=user_id,
                                                         vendor_id=vendor_id, modify_status=ModifyStatus.update,
                                                         modified_by=user_id, entity_id=self._entity_id(),portal_flag=client_obj.get_portal_flag())
                    VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=client_obj.get_id(),
                                                         ref_type=VendorRefType.VENDOR_CLIENT,
                                                         mod_status=ModifyStatus.update,
                                                         modify_ref_id=client.id, entity_id=self._entity_id())

                    client_update=VendorClient.objects.using(self._current_app_schema()).filter(id=client_obj.get_id(), entity_id=self._entity_id()).update(
                        modify_ref_id=client.id)

                # clientupdate_auditdata={'id':client_obj.get_id(),'modify_ref_id':client.id}


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
        else:
            # try:

                client = VendorClient.objects.using(self._current_app_schema()).create(name=client_obj.get_name(), address_id=add_id, created_by=user_id,
                                                     vendor_id=vendor_id, modify_status=ModifyStatus.create,
                                                                modified_by=user_id, entity_id=self._entity_id(),portal_flag=client_obj.get_portal_flag())

                client_update=VendorClient.objects.using(self._current_app_schema()).filter(id=client.id, entity_id=self._entity_id()).update(modify_ref_id=client.id)


                VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=client.id,
                                                     ref_type=VendorRefType.VENDOR_CLIENT, mod_status=ModifyStatus.create,
                                                     modify_ref_id=client.id, entity_id=self._entity_id())


                # self.audit_function(client_update, vendor_id, user_id, req_status, client.id, ModifyStatus.create)
                # self.audit_function(client, vendor_id, user_id, req_status, client.id, ModifyStatus.create)



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

        client_data = ClientResponse()
        client_data.set_id(client.id)
        client_data.set_name(client.name)
        client_data.set_address_id(client.address_id)
        client_data.set_vendor_id(client.vendor_id)
        client_data.set_portal_flag(client.portal_flag)



        return client_data

    # modification
    def modification_delete_client(self, client_id,user_id,vendor_id):
        try:
            vendor_service=VendorService(self._scope())
            ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_CLIENT, client_id)
            client_update = VendorClient.objects.using(self._current_app_schema()).filter(id=client_id, entity_id=self._entity_id()).update(modify_ref_id=client_id,
                                                                             modify_status=ModifyStatus.delete)
            if ref_flag==True:
                VendorModificationRel.objects.using(self._current_app_schema()).filter(Q(ref_type=VendorRefType.VENDOR_CLIENT)&Q(modify_ref_id=client_id)&Q(entity_id=self._entity_id())).update( mod_status=ModifyStatus.delete)
            else:
                VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=client_id,
                                                     ref_type=VendorRefType.VENDOR_CLIENT,
                                                     mod_status=ModifyStatus.delete,
                                                     modify_ref_id=client_id, entity_id=self._entity_id())

            client = VendorClient.objects.using(self._current_app_schema()).get(id=client_id, entity_id=self._entity_id())
            Audit_Action = ModifyStatus.update
            req_status = RequestStatusUtil.MODIFICATION
            # self.audit_function(client_update, vendor_id, user_id, req_status, client_id, Audit_Action)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj



    def modification_action_client(self, mod_status, old_id, new_id, vendor_id, user_id):


        req_status = RequestStatusUtil.MODIFICATION
        vendor_old_id = self.get_address_id(old_id)
        vendor_new_id = self.get_address_id(new_id)
        address_service = AddressService(self._scope())
        address_service.modification_action_address(mod_status, vendor_old_id.address_id,
                                                    vendor_new_id.address_id, vendor_id, user_id)

        if mod_status == ModifyStatus.update:
            client_obj = self.fetch_client(new_id)

            client_update = VendorClient.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(name=client_obj.get_name(),
                                                                              modify_status=-1, modify_ref_id=-1,
                                                                              modified_by=-1,
                                                                              updated_by=user_id,
                                                                              updated_date=timezone.now(), portal_flag=client_obj.get_portal_flag())


            self.audit_function(client_update, vendor_id, user_id, req_status, old_id, ModifyStatus.update)
            # self.audit_function(contractor_del, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)

        elif mod_status == ModifyStatus.create:

            client_update=VendorClient.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).update(modify_status=-1, modify_ref_id=-1,
                                                          modified_by=-1,
                                                          updated_by=user_id,
                                                          updated_date=timezone.now())
            self.audit_function(client_update, vendor_id, user_id, req_status, new_id, ModifyStatus.update)

        else:
            client_del=VendorClient.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).delete()
            self.audit_function(client_del, vendor_id, user_id, req_status, old_id, ModifyStatus.delete)


        return

    def modification_reject_client(self, mod_status, old_id, new_id, vendor_id, user_id):

        req_status = RequestStatusUtil.MODIFICATION
        vendor_old_id = self.get_address_id(old_id)
        vendor_new_id = self.get_address_id(new_id)
        address_service = AddressService(self._scope())
        address_service.modification_reject_address(mod_status, vendor_old_id.address_id,
                                                    vendor_new_id.address_id, vendor_id, user_id)

        if mod_status == ModifyStatus.update:

            client_del=VendorClient.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()
            client = VendorClient.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(modify_ref_id=-1,modified_by=-1)

            self.audit_function(client_del, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)
            self.audit_function(client, vendor_id, user_id, req_status, old_id, ModifyStatus.update)


        elif mod_status == ModifyStatus.create:

            client = VendorClient.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()

            self.audit_function(client, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)
        else:
            client =VendorClient.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(modify_ref_id=-1)

            self.audit_function(client, vendor_id, user_id, req_status, old_id, ModifyStatus.update)

        return

    def audit_function(self, client, vendor_id, user_id, req_status, id, action):
        if action == ModifyStatus.delete:
            data = None
        elif action == ModifyStatus.update:
            data = client
        else:
            data = client.__dict__
            del data['_state']
        audit_service = VendorAuditService(self._scope())
        audit_obj = VendorAuditResponse()
        audit_obj.set_refid(vendor_id)
        audit_obj.set_reftype(VendorRefType.VENDOR)
        audit_obj.set_userid(user_id)
        audit_obj.set_reqstatus(req_status)
        audit_obj.set_relrefid(id)
        audit_obj.set_relreftype(VendorRefType.VENDOR_CLIENT)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_vendoraudit(audit_obj)

        return

    def get_address_id(self,client_id):
        client = VendorClient.objects.using(self._current_app_schema()).get(id=client_id, entity_id=self._entity_id())

        client_data = ClientResponse()
        adaddress_id=client.address_id
        client_data.set_address_id(adaddress_id)

        return client_data
