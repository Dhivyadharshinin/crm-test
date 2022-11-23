import traceback

import django

from django.db import IntegrityError
from django.db.models import Q

from masterservice.data.response.productcategoryresponse import ProductcategoryResponse
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinlist import NWisefinList
from masterservice.models import ProductCategory
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from django.utils import timezone
from django.utils.timezone import now
from masterservice.data.request.masterauditrequest import MasterAuditRequest
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.util.masterutil import ModifyStatus,MasterRefType,RequestStatusUtil
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class Productcategoryservice(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_productcatprocess(self, productcat_obj, emp_id):
        if not productcat_obj.get_id() is None:
            try:
                logger.error('PRODUCTCATEGORY: ProductCategory Update Started')
                pdtcat = ProductCategory.objects.using(self._current_app_schema()).filter(id=productcat_obj.get_id(),
                                                                                          entity_id=self._entity_id()).update(
                    # code=productcat_obj.get_code(),
                    name=productcat_obj.get_name(),
                    product_client_id=productcat_obj.get_client_id(),
                    isprodservice=productcat_obj.get_isprodservice(),
                    stockimpact=productcat_obj.get_stockimpact(),
                    updated_by=emp_id,
                    updated_date=timezone.now()
                )

                pdtcat = ProductCategory.objects.using(self._current_app_schema()).get(id=productcat_obj.get_id(),
                                                                                       entity_id=self._entity_id())
                logger.error('PRODUCTCATEGORY: ProductCategory Update Success' + str(pdtcat))
                pdtcat_auditdata = {'id': productcat_obj.get_id(),
                                    # 'code': productcat_obj.get_code(),
                                    'name': productcat_obj.get_name(),
                                    'product_client_id': productcat_obj.get_client_id(),
                                    'isprodservice': productcat_obj.get_isprodservice(),
                                    'stockimpact': productcat_obj.get_stockimpact(),
                                    'updated_date': timezone.now(),
                                    'updated_by': emp_id}
                self.audit_function(pdtcat_auditdata, emp_id, pdtcat.id, ModifyStatus.update)

            except IntegrityError as error:
                logger.error('ERROR_ProductCategory_Update_EXCEPT:{}'.format(traceback.print_exc()))
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return
            except ProductCategory.DoesNotExist:
                logger.error('ERROR_ProductCategory_Update_EXCEPT:{}'.format(traceback.print_exc()))
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_PRODUCTCATEGORY_ID)
                error_obj.set_description(ErrorDescription.INVALID_PRODUCTCATEGORY_ID)
                return error_obj
            except:
                logger.error('ERROR_ProductCategory_Update_EXCEPT:{}'.format(traceback.print_exc()))
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('PRODUCTCATEGORY: ProductCategory Creation Started')
                data_len = ProductCategory.objects.using(self._current_app_schema()).filter(
                    name=productcat_obj.get_name()).values()
                if (len(data_len) > 0):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                    return error_obj
                pdtcat = ProductCategory.objects.using(self._current_app_schema()).create(
                    # code=productcat_obj.get_code(),
                    name=productcat_obj.get_name(),
                    product_client_id=productcat_obj.get_client_id(),
                    isprodservice=productcat_obj.get_isprodservice(),
                    stockimpact=productcat_obj.get_stockimpact(),
                    created_by=emp_id, entity_id=self._entity_id())

                # code = "ISCT" + str(pdtcat.id)
                try:
                    max_cat_code = ProductCategory.objects.using(self._current_app_schema()).filter(code__icontains='PDCT').order_by('-code')[0].code
                    rnsl = int(max_cat_code[4:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "PDCT" + str(new_rnsl).zfill(4)
                pdtcat.code = code
                pdtcat.save()
                self.audit_function(pdtcat, emp_id, pdtcat.id, ModifyStatus.create)
                logger.error('PRODUCTCATEGORY: ProductCategory Creation Success' + str(pdtcat))

            except IntegrityError as error:
                logger.error('ERROR_ProductCategory_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_ProductCategory_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        # productcat_res = ProductcategoryResponse()
        # productcat_res.set_id(pdtcat.id)
        # productcat_res.set_code(pdtcat.code)
        # productcat_res.set_name(pdtcat.name)
        # productcat_res.set_client_id(pdtcat.client_id)
        # productcat_res.set_isprodservice(pdtcat.isprodservice)
        # productcat_res.set_stockimpact(pdtcat.stockimpact)
        # if id
        data=NWisefinSuccess()
        data.set_status(SuccessStatus.SUCCESS)
        data.set_message(SuccessMessage.CREATE_MESSAGE)
        return data


            # data = NWisefinSuccess()
            # data.set_status(SuccessStatus.SUCCESS)
            # data.set_message(SuccessMessage.UPDATE_MESSAGE)
            # return data
        # return productcat_res

    def fetch_productcat(self, productcat_id):
        try:
            pdtcat = ProductCategory.objects.using(self._current_app_schema()).get(id=productcat_id,
                                                                                   entity_id=self._entity_id())
            productcat_res = ProductcategoryResponse()
            productcat_res.set_id(pdtcat.id)
            productcat_res.set_code(pdtcat.code)
            productcat_res.set_name(pdtcat.name)
            # productcat_res.set_client_id(pdtcat.client_id)
            productcat_res.set_isprodservice(pdtcat.isprodservice)
            productcat_res.set_stockimpact(pdtcat.stockimpact)
            return productcat_res
        except ProductCategory.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PRODUCTCATEGORY_ID)
            error_obj.set_description(ErrorDescription.INVALID_PRODUCTCATEGORY_ID)
            return error_obj
#list all
    def pdtcat_list(self, vys_page):
        try:
            obj = ProductCategory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())[
                  vys_page.get_offset():vys_page.get_query_limit()]
            list_len = len(obj)
            pdtcat_list = NWisefinList()
            if list_len <= 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_PRODUCTCATEGORY_ID)
                error_obj.set_description(ErrorDescription.INVALID_PRODUCTCATEGORY_ID)
                return error_obj
            else:
                for pdtcat in obj:
                    productcat_res = ProductcategoryResponse()
                    productcat_res.set_id(pdtcat.id)
                    productcat_res.set_code(pdtcat.code)
                    productcat_res.set_name(pdtcat.name)
                    # productcat_res.set_client_id(pdtcat.client_id)
                    productcat_res.set_isprodservice(pdtcat.isprodservice)
                    productcat_res.set_stockimpact(pdtcat.stockimpact)
                    pdtcat_list.append(productcat_res)
                vpage = NWisefinPaginator(obj, vys_page.get_index(), 10)
                pdtcat_list.set_pagination(vpage)
                return pdtcat_list
        except:
            logger.error('ERROR_ProductCategory_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PRODUCTCATEGORY_ID)
            error_obj.set_description(ErrorDescription.INVALID_PRODUCTCATEGORY_ID)
            return error_obj


    def delete_productcat(self, productcat_id, emp_id):
        product = ProductCategory.objects.using(self._current_app_schema()).filter(id=productcat_id,
                                                                                   entity_id=self._entity_id()).delete()
        self.audit_function(product, emp_id, productcat_id, ModifyStatus.delete)
        if product[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PRODUCTCATEGORY_ID)
            error_obj.set_description(ErrorDescription.INVALID_PRODUCTCATEGORY_ID)
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
        audit_obj.set_relreftype(MasterRefType.PRODUCTCATEGORY)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return

    def productcat_search_list(self, vys_page, query):
        condition = Q(status=1) & Q(entity_id=self._entity_id())

        if not query is None:
            condition &= Q(name__icontains=query)
        obj = ProductCategory.objects.using(self._current_app_schema()).filter(condition).order_by('created_by')[
              vys_page.get_offset():vys_page.get_query_limit()]
        list_len = len(obj)
        pdtcat_list = NWisefinList()
        if list_len > 0:
            for pdtcat in obj:
                productcat_res = ProductcategoryResponse()
                productcat_res.set_id(pdtcat.id)
                productcat_res.set_code(pdtcat.code)
                productcat_res.set_name(pdtcat.name)
                productcat_res.set_client_id(pdtcat.client_id)
                productcat_res.set_isprodservice(pdtcat.isprodservice)
                productcat_res.set_stockimpact(pdtcat.stockimpact)
                pdtcat_list.append(productcat_res)
            vpage = NWisefinPaginator(obj, vys_page.get_index(), 10)
            pdtcat_list.set_pagination(vpage)
        return pdtcat_list


    def create_productcatprocess_mtom(self, productcat_obj,action, emp_id):
        if action=='update':
            #try:
                pdtcat=ProductCategory.objects.using(self._current_app_schema()).filter(code=productcat_obj.get_code()).update(code=productcat_obj.get_code(),
                                                                                         name=productcat_obj.get_name(),
                                                                                         status=productcat_obj.get_status(),
                                                                                          client_id=productcat_obj.get_client_id(),
                                                                                          isprodservice=productcat_obj.get_isprodservice(),
                                                                                          stockimpact=productcat_obj.get_stockimpact(),
                                                                                          updated_by = emp_id,
                                                                                         updated_date=timezone.now()
                                                                                        )

                pdtcat=ProductCategory.objects.using(self._current_app_schema()).get(code=productcat_obj.get_code())
                pdtcat_auditdata = {'id': pdtcat.id,
                                         'code': productcat_obj.get_code(),
                                         'name': productcat_obj.get_name(),
                                         'client_id': productcat_obj.get_client_id(),
                                         'isprodservice': productcat_obj.get_isprodservice(),
                                         'stockimpact': productcat_obj.get_stockimpact(),
                                         'updated_date': timezone.now(),
                                         'updated_by': emp_id}
                self.audit_function(pdtcat_auditdata, emp_id, pdtcat.id, ModifyStatus.update)

            # except IntegrityError as error:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return
            # except:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj
        elif action=='create':
            try:
                print('code ',productcat_obj.get_code())
                pdtcat=ProductCategory.objects.using(self._current_app_schema()).create(code=productcat_obj.get_code(),
                                                  name=productcat_obj.get_name(),
                                                   client_id=productcat_obj.get_client_id(),
                                                    isprodservice=productcat_obj.get_isprodservice(),
                                                    stockimpact=productcat_obj.get_stockimpact(),
                                                     created_by=emp_id, entity_id=self._entity_id())


                self.audit_function(pdtcat, emp_id, pdtcat.id, ModifyStatus.create)

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

        productcat_res=ProductcategoryResponse()
        productcat_res.set_id(pdtcat.id)
        productcat_res.set_code(pdtcat.code)
        productcat_res.set_name(pdtcat.name)
        productcat_res.set_client_id(pdtcat.client_id)
        productcat_res.set_isprodservice(pdtcat.isprodservice)
        productcat_res.set_stockimpact(pdtcat.stockimpact)
        return productcat_res

        # prpo

    def fetch_productcatdata(self, productcat_id):
        logger.error("fetch_productcatdata : " + str(productcat_id))
        try:
            product = ProductCategory.objects.using(self._current_app_schema()).get(id=productcat_id,
                                                                                    entity_id=self._entity_id())
            product_data = {"id": product.id,
                            "code": product.code,
                            "name": product.name}
            return product_data
        except ProductCategory.DoesNotExist as e:
            print(e)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(e) + ' : ' + str(productcat_id))
            return error_obj

    def fetch_product_category_download(self, vys_page):
        try:
            obj = ProductCategory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())
            list_len = len(obj)
            pdtcat_list = NWisefinList()
            if list_len <= 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_PRODUCTCATEGORY_ID)
                error_obj.set_description(ErrorDescription.INVALID_PRODUCTCATEGORY_ID)
                return error_obj
            else:
                for pdtcat in obj:
                    productcat_res = ProductcategoryResponse()
                    productcat_res.set_id(pdtcat.id)
                    productcat_res.set_code(pdtcat.code)
                    productcat_res.set_name(pdtcat.name)
                    productcat_res.set_isprodservice(pdtcat.isprodservice)
                    productcat_res.set_stockimpact(pdtcat.stockimpact)
                    pdtcat_list.append(productcat_res)
                return pdtcat_list
        except:
            logger.error('ERROR_ProductCategory_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PRODUCTCATEGORY_ID)
            error_obj.set_description(ErrorDescription.INVALID_PRODUCTCATEGORY_ID)
            return error_obj