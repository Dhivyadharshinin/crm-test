import django
from django.db import IntegrityError
from nwisefin.settings import logger
from userservice.models import Employee
from vendorservice.data.response.supplierresponse import ProductResponse
from vendorservice.data.response.vendorauditresponse import VendorAuditResponse
from vendorservice.models import SupplierProduct, VendorQueue, VendorModificationRel
from vendorservice.util.vendorutil import ModifyStatus, VendorRefType, RequestStatusUtil
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.utilityservice import NWisefinUtilityService
from django.utils import timezone
from vendorservice.service.vendorservice import VendorService
from vendorservice.data.request.vendorauditrequest import VendorAuditRequest
from vendorservice.service.vendorauditservice import VendorAuditService
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from django.db.models import Q


class productservice(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def create_product(self, product_obj, user_id, client1, client2, customer1, customer2, vendor_id):

        if not product_obj.get_id() is None:
            # try:

                product_update = SupplierProduct.objects.using(self._current_app_schema()).filter(id=product_obj.get_id(), entity_id=self._entity_id()).update(vendor_id=vendor_id,
                name=product_obj.get_name(),
                type=product_obj.get_type(),age=product_obj.get_age(),
                client1_id=client1,client2_id=client2,customer1_id=customer1,
                customer2_id=customer2,
                updated_by=user_id,updated_date=timezone.now(),portal_flag=product_obj.get_portal_flag())

                product_auditdata={'id':product_obj.get_id(),'vendor_id':vendor_id,
                'name':product_obj.get_name(),
                'type':product_obj.get_type(),'age':product_obj.get_age(),
                'client1_id':client1,'client2_id':client2,'customer1_id':customer1,
                'customer2_id':customer2,
                'updated_by':user_id,'updated_date':timezone.now()}

                product = SupplierProduct.objects.using(self._current_app_schema()).get(id=product_obj.get_id(), entity_id=self._entity_id())

                Audit_Action = ModifyStatus.update
                req_status = RequestStatusUtil.ONBOARD
                self.audit_function(product_auditdata, vendor_id, user_id, req_status, product.id, Audit_Action)


            # except IntegrityError as error:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except SupplierProduct.DoesNotExist:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_SUPPLIERPRODUCT_ID)
            #     error_obj.set_description(ErrorDescription.INVALID_SUPPLIERPRODUCT_ID)
            #     return error_obj
            # except:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj
        else:
            # try:

                product = SupplierProduct.objects.using(self._current_app_schema()).create(vendor_id=vendor_id,
                name=product_obj.get_name(),
                type=product_obj.get_type(),age=product_obj.get_age(),
                client1_id=client1,client2_id=client2,customer1_id=customer1,
                customer2_id=customer2,created_by=user_id, entity_id=self._entity_id(),portal_flag=product_obj.get_portal_flag())
                Audit_Action = ModifyStatus.create
                req_status = RequestStatusUtil.ONBOARD
                self.audit_function(product, vendor_id, user_id, req_status, product.id, Audit_Action)

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

        product_data = ProductResponse()
        product_data.set_id(product.id)
        product_data.set_name(product.name)
        product_data.set_type(product.type)
        product_data.set_age(product.age)
        product_data.set_client1_id(product.client1_id)
        product_data.set_client2_id(product.client2_id)
        product_data.set_customer1_id(product.customer1_id)
        product_data.set_customer2_id(product.customer2_id)
        product_data.set_vendor_id(product.vendor_id)
        product_data.set_portal_flag(product.portal_flag)




        return product_data

    # def fetch_product_list(self,user_id):
    #     productlist = SupplierProduct.objects.all()
    #     list_length = len(productlist)
    #     logger.info(list_length)
    #     if list_length <= 0:
    #         error_obj = Error()
    #         error_obj.set_code(ErrorMessage.INVALID_SUPPLIERPRODUCT_ID)
    #         error_obj.set_description(ErrorDescription.INVALID_SUPPLIERPRODUCT_ID)
    #         return error_obj
    #     else:
    #         product_list_data = VysfinList()
    #         for product in productlist:
    #             product_data = ProductResponse()
    #             product_data.set_id(product.id)
    #             product_data.set_name(product.name)
    #             product_data.set_type(product.type)
    #             product_data.set_age(product.age)
    #             product_data.set_client1_id(product.client1_id)
    #             product_data.set_client2_id(product.client2_id)
    #             product_data.set_customer1_id(product.customer1_id)
    #             product_data.set_customer2_id(product.customer2_id)
    #             product_list_data.append(product_data)
    #         return product_list_data

    def fetch_product_list(self,request, vys_page,user_id,vendor_id):
        # queue_arr = VendorQueue.objects.select_related('vendor__id').filter(#     Q(from_user_id__exact=user_id) | Q(to_user_id__exact=user_id)).values('vendor_id').distinct()

        queue_arr = SupplierProduct.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id, entity_id=self._entity_id()).values('id')

        condition = None
        for vendor in queue_arr:
            logger.info(str(vendor))
            if condition is None:
                condition = (Q(id__exact=vendor['id'])& (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1))&Q(entity_id=self._entity_id())
            else:
                condition |= (Q(id__exact=vendor['id'])& (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1))&Q(entity_id=self._entity_id())
        if condition is not None:
            productlist = SupplierProduct.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        else:
            productlist = []

        vlist = NWisefinList()
        user_list = []
        for vendor in productlist:
            user_list.append(vendor.created_by)
        user_list = set(user_list)
        user_list = list(user_list)
        utility_service = NWisefinUtilityService()
        user_list_obj = utility_service.get_user_info(request, user_list)

        product_list_data = NWisefinList()
        for product in productlist:
            product_data = ProductResponse()
            product_data.set_id(product.id)
            product_data.set_name(product.name)
            product_data.set_type(product.type)
            product_data.set_age(product.age)
            product_data.set_client1_id(product.client1_id)
            product_data.set_client2_id(product.client2_id)
            product_data.set_customer1_id(product.customer1_id)
            product_data.set_customer2_id(product.customer2_id)
            product_data.set_vendor_id(product.vendor_id)
            product_data.set_created_by(product.created_by)
            product_data.set_modify_ref_id(product.modify_ref_id)
            product_data.set_modify_status(product.modify_status)
            product_data.set_portal_flag(product.portal_flag)

            for ul in user_list_obj['data']:
                if ul['id'] == SupplierProduct.created_by:
                    product_data.set_created_by(ul)
            vlist.append(product_data)
        vpage = NWisefinPaginator(productlist, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist

    def fetch_product(self, product_id,vendor_id):
        try:
            product = SupplierProduct.objects.using(self._current_app_schema()).get(id=product_id, entity_id=self._entity_id())
            product_data = ProductResponse()
            product_data.set_id(product.id)
            product_data.set_name(product.name)
            product_data.set_type(product.type)
            product_data.set_age(product.age)
            product_data.set_vendor_id(product.vendor_id)
            product_data.set_client1_id(product.client1_id)
            product_data.set_client2_id(product.client2_id)
            product_data.set_customer1_id(product.customer1_id)
            product_data.set_customer2_id(product.customer2_id)
            product_data.set_created_by(product.created_by)
            product_data.set_modify_ref_id(product.modify_ref_id)
            product_data.set_modify_status(product.modify_status)
            product_data.set_portal_flag(product.portal_flag)

            return product_data

        except SupplierProduct.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_SUPPLIERPRODUCT_ID)
            error_obj.set_description(ErrorDescription.INVALID_SUPPLIERPRODUCT_ID)
            return error_obj

    def delete_product(self, product_id, vendor_id,user_id):

        product = SupplierProduct.objects.using(self._current_app_schema()).filter(id=product_id, entity_id=self._entity_id()).delete()

        Audit_Action = ModifyStatus.delete
        req_status = RequestStatusUtil.ONBOARD
        self.audit_function(product, vendor_id, user_id, req_status, product_id, Audit_Action)
        if product[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_CATEGORY_ID)
            error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)

            return success_obj



    def product_modification(self, product_obj,user_id,client1,client2,customer1,customer2,vendor_id):

        req_status = RequestStatusUtil.ONBOARD
        vendor_service = VendorService(self._scope())
        if product_obj.get_id():
            # try:
                ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_PRODUCT, product_obj.get_id())
                if ref_flag==True:
                    product = SupplierProduct.objects.using(self._current_app_schema()).filter(id=product_obj.get_id(), entity_id=self._entity_id()).update(
                                                             name=product_obj.get_name(),
                                                             type=product_obj.get_type(), age=product_obj.get_age(),
                                                             client1_id=client1, client2_id=client2,
                                                             customer1_id=customer1,
                                                             customer2_id=customer2,portal_flag=product_obj.get_portal_flag())
                    product=SupplierProduct.objects.using(self._current_app_schema()).get(id=product_obj.get_id(), entity_id=self._entity_id())
                else:
                    product = SupplierProduct.objects.using(self._current_app_schema()).create(vendor_id=vendor_id,
                            name=product_obj.get_name(),
                            type=product_obj.get_type(),age=product_obj.get_age(),
                            client1_id=client1,client2_id=client2,customer1_id=customer1,
                            customer2_id=customer2,created_by=user_id,
                             modify_status=ModifyStatus.update,modify_ref_id=product_obj.get_id(),
                             modified_by=user_id, entity_id=self._entity_id(),portal_flag=product_obj.get_portal_flag())
                    product_update=SupplierProduct.objects.using(self._current_app_schema()).filter(id=product_obj.get_id()).update(
                        modify_ref_id=product.id)

                # productupdate_auditdata={'id':product_obj.get_id(),'modify_ref_id':product.id}

                    VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=product_obj.get_id(),
                                                         ref_type=VendorRefType.VENDOR_PRODUCT,
                                                         mod_status=ModifyStatus.update,
                                                         modify_ref_id=product.id, entity_id=self._entity_id())



                # self.audit_function(product, vendor_id, user_id, req_status, product.id, ModifyStatus.create)
                # self.audit_function(productupdate_auditdata, vendor_id, user_id, req_status, product_update.id, ModifyStatus.update)

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
                product = SupplierProduct.objects.using(self._current_app_schema()).create(vendor_id=vendor_id,
                        name=product_obj.get_name(),
                        type=product_obj.get_type(),age=product_obj.get_age(),
                        client1_id=client1,client2_id=client2,customer1_id=customer1,
                        customer2_id=customer2,created_by=user_id, modify_status=ModifyStatus.create,
                                                                modified_by=user_id, entity_id=self._entity_id(),portal_flag=product_obj.get_portal_flag())
                product_update=SupplierProduct.objects.using(self._current_app_schema()).filter(id=product.id, entity_id=self._entity_id()).update(modify_ref_id=product.id)

                VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=product.id,
                                                     ref_type=VendorRefType.VENDOR_PRODUCT, mod_status=ModifyStatus.create,
                                                     modify_ref_id=product.id, entity_id=self._entity_id())

                vendor_service = VendorService(self._scope())
                ref_id = vendor_service.checkmodification_flag(vendor_id, VendorRefType.VENDOR_PRODUCT, product.id)
                flag_obj = VendorModificationRel.objects.using(self._current_app_schema()).filter(Q(ref_id=ref_id) & Q(is_flag=False)&Q(ref_type=VendorRefType.VENDOR_PRODUCT)&Q(entity_id=self._entity_id()))
                if len(flag_obj) == 0:
                    VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=product.id,
                                                         ref_type=VendorRefType.VENDOR_PRODUCT,
                                                         mod_status=ModifyStatus.create, is_flag=False,
                                                         modify_ref_id=product.id, entity_id=self._entity_id())
                else:
                    VendorModificationRel.objects.using(self._current_app_schema()).filter(Q(ref_id=ref_id) & Q(is_flag=False)&Q(ref_type=VendorRefType.VENDOR_PRODUCT)&Q(entity_id=self._entity_id())).update(
                        modify_ref_id=product.id,
                        mod_status=ModifyStatus.update)

                # self.audit_function(product, vendor_id, user_id, req_status, product.id, ModifyStatus.create)
                # self.audit_function(product_update, vendor_id, user_id, req_status, product_update.id,
                #                     ModifyStatus.update)


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

        product_data = ProductResponse()
        product_data.set_id(product.id)
        product_data.set_name(product.name)
        product_data.set_type(product.type)
        product_data.set_age(product.age)
        product_data.set_client1_id(product.client1_id)
        product_data.set_client2_id(product.client2_id)
        product_data.set_customer1_id(product.customer1_id)
        product_data.set_customer2_id(product.customer2_id)
        product_data.set_vendor_id(product.vendor_id)
        product_data.set_portal_flag(product.portal_flag)


        return product_data


    def modification_action_product(self, mod_status, old_id, new_id, vendor_id, user_id):

        req_status = RequestStatusUtil.MODIFICATION
        if mod_status == ModifyStatus.update:
            product_obj = self.fetch_product(new_id,vendor_id)
            product = SupplierProduct.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(vendor_id=vendor_id,
                name=product_obj.get_name(),
                type=product_obj.get_type(),age=product_obj.get_age(),
                client1_id=product_obj.get_client1_id(),client2_id=product_obj.get_client2_id(),
                 customer1_id=product_obj.get_customer1_id(),
                customer2_id=product_obj.get_customer2_id(),
                updated_by=user_id,updated_date=timezone.now(),
                modify_status=-1,
                modify_ref_id=-1,modified_by=-1,portal_flag=product_obj.get_portal_flag())


            self.audit_function(product, vendor_id, user_id, req_status, old_id, ModifyStatus.update)
            # self.audit_function(product_del, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)

        elif mod_status == ModifyStatus.create:
            product =SupplierProduct.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).update(modify_status=-1,
                                                     modify_ref_id=-1,modified_by=-1)


            self.audit_function(product, vendor_id, user_id, req_status, new_id, ModifyStatus.update)

        else:
            product = SupplierProduct.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).delete()

            self.audit_function(product, vendor_id, user_id, req_status, old_id,  ModifyStatus.delete)

    def modification_delete_product(self, product_id,user_id,vendor_id):
        try:
            vendor_service = VendorService(self._scope())
            SupplierProduct.objects.using(self._current_app_schema()).get(id=product_id, entity_id=self._entity_id())
            ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_PRODUCT, product_id)
            product =SupplierProduct.objects.using(self._current_app_schema()).filter(id=product_id, entity_id=self._entity_id()).update(modify_ref_id=product_id,modify_status=ModifyStatus.delete)
            if ref_flag == True:
                VendorModificationRel.objects.using(self._current_app_schema()).filter(
                    Q(ref_type=VendorRefType.VENDOR_PRODUCT) & Q(modify_ref_id=product_id)&Q(entity_id=self._entity_id())).update(
                    mod_status=ModifyStatus.delete)
            else:
                VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id, ref_id=product_id,
                                                     ref_type=VendorRefType.VENDOR_PRODUCT,
                                                     mod_status=ModifyStatus.delete,
                                                     modify_ref_id=product_id, entity_id=self._entity_id())



            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)

            req_status = RequestStatusUtil.MODIFICATION
            # self.audit_function(product, vendor_id, user_id, req_status, product.id, ModifyStatus.update)
            return success_obj

        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj


    def modification_reject_product(self, mod_status, old_id, new_id, vendor_id, user_id):

        req_status = RequestStatusUtil.MODIFICATION
        if mod_status == ModifyStatus.update:
            product_del = SupplierProduct.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()
            product =SupplierProduct.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(modify_ref_id=-1,modified_by=-1)

            self.audit_function(product_del, vendor_id, user_id, req_status, new_id,  ModifyStatus.delete)
            self.audit_function(product, vendor_id, user_id, req_status, old_id,  ModifyStatus.update)

        elif mod_status == ModifyStatus.create:
            product = SupplierProduct.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()

            self.audit_function(product, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)
        else:
            product =SupplierProduct.objects.using(self._current_app_schema()).filter(id=old_id, entity_id=self._entity_id()).update(modify_ref_id=-1,modified_by=-1)

            self.audit_function(product, vendor_id, user_id, req_status, old_id, ModifyStatus.update)

    def audit_function(self, product, vendor_id, user_id, req_status, id, action):
        if action == ModifyStatus.delete:
            data = None
        elif action == ModifyStatus.update:
            data = product
        else:
            data = product.__dict__
            del data['_state']
        audit_service = VendorAuditService(self._scope())
        audit_obj = VendorAuditResponse()
        audit_obj.set_refid(vendor_id)
        audit_obj.set_reftype(VendorRefType.VENDOR)
        audit_obj.set_userid(user_id)
        audit_obj.set_reqstatus(req_status)
        audit_obj.set_relrefid(id)
        audit_obj.set_relreftype(VendorRefType.VENDOR_PRODUCT)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_vendoraudit(audit_obj)
        return
