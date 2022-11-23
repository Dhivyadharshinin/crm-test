import traceback

import django

from django.db import IntegrityError
from django.db.models import Q

from masterservice.data.response.producttyperesponse import ProducttypeResponse
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinlist import NWisefinList
from masterservice.models import ProductType, ProductCategory
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


class ProducttypeService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_producttype(self, protypeobj, emp_id):
        if not protypeobj.get_id() is None:
            try:
                logger.error('PRODUCTTYPE: ProductType Update Started')
                pro = ProductType.objects.using(self._current_app_schema()).filter(id=protypeobj.get_id(),
                                                                                   entity_id=self._entity_id()).update(
                    # code=protypeobj.get_code(),
                    name=protypeobj.get_name(),
                    productcategory_id=protypeobj.get_productcategory_id(),
                    updated_by=emp_id,
                    updated_date=timezone.now()
                )

                pro = ProductType.objects.using(self._current_app_schema()).get(id=protypeobj.get_id(),
                                                                                entity_id=self._entity_id())
                logger.error('PRODUCTTYPE: ProductType Update Success' + str(pro))
                pdttype_auditdata = {'id': protypeobj.get_id(),
                                     # 'code': protypeobj.get_code(),
                                     'name': protypeobj.get_name(),
                                     'productcategory_id': protypeobj.get_productcategory_id(),
                                     'updated_date': timezone.now(),
                                     'updated_by': emp_id}
                self.audit_function(pdttype_auditdata, emp_id, pro.id, ModifyStatus.update)

            except IntegrityError as error:
                logger.error('ERROR_ProductType_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except ProductType.DoesNotExist:
                logger.error('ERROR_ProductType_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_PRODUCTTYPE_ID)
                error_obj.set_description(ErrorDescription.INVALID_PRODUCTTYPE_ID)
                return error_obj
            except:
                logger.error('ERROR_ProductType_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('PRODUCTTYPE: ProductType Creation Started')
                data_len = ProductType.objects.using(self._current_app_schema()).filter(
                    name=protypeobj.get_name()).values()
                if (len(data_len) > 0):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                    return error_obj
                pro = ProductType.objects.using(self._current_app_schema()).create(  # code=protypeobj.get_code(),
                    name=protypeobj.get_name(),
                    productcategory_id=protypeobj.get_productcategory_id(),
                    created_by=emp_id, entity_id=self._entity_id())

                # code = "ISCT" + str(pro.id)
                try:
                    max_cat_code = ProductType.objects.using(self._current_app_schema()).filter(code__icontains='PTYPE').order_by('-code')[0].code
                    rnsl = int(max_cat_code[5:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "PTYPE" + str(new_rnsl).zfill(3)
                pro.code = code
                pro.save()
                logger.error('PRODUCTTYPE: ProductType Creation Success' + str(pro))
                self.audit_function(pro, emp_id, pro.id, ModifyStatus.create)
            except IntegrityError as error:
                logger.error('ERROR_ProductType_Create_EXCEPT:{}'.format(traceback.print_exc()))
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_ProductType_Create_EXCEPT:{}'.format(traceback.print_exc()))
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        protype_res=ProducttypeResponse()
        protype_res.set_id(pro.id)
        protype_res.set_code(pro.code)
        protype_res.set_name(pro.name)
        protype_res.set_productcategory_id(pro.productcategory_id)
        # return protype_res
        data = NWisefinSuccess()
        data.set_status(SuccessStatus.SUCCESS)
        data.set_message(SuccessMessage.CREATE_MESSAGE)
        return data

    def fetch_producttype(self, producttype_id):
        try:
            pro = ProductType.objects.using(self._current_app_schema()).get(id=producttype_id,
                                                                            entity_id=self._entity_id())
            protype_res = ProducttypeResponse()
            protype_res.set_id(pro.id)
            protype_res.set_code(pro.code)
            protype_res.set_name(pro.name)
            protype_res.set_productcategory(pro.productcategory)
            return protype_res
        except ProductType.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PRODUCTTYPE_ID)
            error_obj.set_description(ErrorDescription.INVALID_PRODUCTTYPE_ID)
            return error_obj

    # list all
    def pdttype_list(self, vys_page):
        try:
            obj = ProductType.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())[
                  vys_page.get_offset():vys_page.get_query_limit()]
            list_len = len(obj)
            pro_list = NWisefinList()
            if list_len <= 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_PRODUCTTYPE_ID)
                error_obj.set_description(ErrorDescription.INVALID_PRODUCTTYPE_ID)
                return error_obj
            else:
                for pro in obj:
                    protype_res = ProducttypeResponse()
                    protype_res.set_id(pro.id)
                    protype_res.set_code(pro.code)
                    protype_res.set_name(pro.name)
                    protype_res.set_productcategory(pro.productcategory)
                    pro_list.append(protype_res)
                vpage = NWisefinPaginator(obj, vys_page.get_index(), 10)
                pro_list.set_pagination(vpage)
                return pro_list
        except:
            logger.error('ERROR_ProductType_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PRODUCTTYPE_ID)
            error_obj.set_description(ErrorDescription.INVALID_PRODUCTTYPE_ID)
            return error_obj

    # delete
    def delete_producttype(self, producttype_id, emp_id):
        type = ProductType.objects.using(self._current_app_schema()).filter(id=producttype_id,
                                                                            entity_id=self._entity_id()).delete()
        self.audit_function(type, emp_id, producttype_id, ModifyStatus.delete)
        if type[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PRODUCTTYPE_ID)
            error_obj.set_description(ErrorDescription.INVALID_PRODUCTTYPE_ID)
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
        audit_obj.set_relreftype(MasterRefType.PRODUCTTYPE)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return

    def producttype_search_list(self, vys_page, query, productcat_id):
        condition = Q(status=1) & Q(entity_id=self._entity_id())

        if not query is None:
            condition &= Q(name__icontains=query)
        if not productcat_id is None:
            condition &= Q(productcategory_id=productcat_id)
        obj = ProductType.objects.using(self._current_app_schema()).filter(condition)[
              vys_page.get_offset():vys_page.get_query_limit()]
        list_len = len(obj)
        pro_list = NWisefinList()

        if list_len > 0:
            for pro in obj:
                protype_res = ProducttypeResponse()
                protype_res.set_id(pro.id)
                protype_res.set_code(pro.code)
                protype_res.set_name(pro.name)
                protype_res.set_productcategory(pro.productcategory)
                pro_list.append(protype_res)
            vpage = NWisefinPaginator(obj, vys_page.get_index(), 10)
            pro_list.set_pagination(vpage)
        return pro_list


    def create_producttype_mtom(self,protypeobj,action,emp_id):

        if action=='update':
            try:
                ProductCategory_data = ProductCategory.objects.using(self._current_app_schema()).get(code=protypeobj.get_productcategory_code())
                pro=ProductType.objects.using(self._current_app_schema()).filter(code=protypeobj.get_code()).update(
                                                                    code=protypeobj.get_code(),
                                                                    name=protypeobj.get_name(),
                                                                    productcategory_id=ProductCategory_data.id,
                                                                    status=protypeobj.get_status(),
                                                                    updated_by=emp_id,
                                                                    updated_date=timezone.now()
                                                                 )

                pro=ProductType.objects.using(self._current_app_schema()).get(code=protypeobj.get_code())
                pdttype_auditdata = {'id': pro.id,
                                    'code': protypeobj.get_code(),
                                    'name': protypeobj.get_name(),
                                    'productcategory_id': ProductCategory_data.id,
                                    'updated_date': timezone.now(),
                                    'updated_by': emp_id}
                self.audit_function(pdttype_auditdata, emp_id, pro.id, ModifyStatus.update)

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        elif action=='create':
            try:
                ProductCategory_data = ProductCategory.objects.using(self._current_app_schema()).get(code=protypeobj.get_productcategory_code())
                pro=ProductType.objects.using(self._current_app_schema()).create(code=protypeobj.get_code(),
                                               name=protypeobj.get_name(),
                                               productcategory_id=ProductCategory_data.id,
                                                created_by=emp_id)

                self.audit_function(pro, emp_id, pro.id, ModifyStatus.create)
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

        protype_res=ProducttypeResponse()
        protype_res.set_id(pro.id)
        protype_res.set_code(pro.code)
        protype_res.set_name(pro.name)
        protype_res.set_productcategory_id(pro.productcategory_id)
        return protype_res

    def fetch_producttypedata(self, id):
        logger.error("fetch_productdata : " + str(id))
        try:
            product = ProductType.objects.using(self._current_app_schema()).get(id=id, entity_id=self._entity_id())
            product_data = {"id": product.id,
                            "code": product.code,
                            "name": product.name}
            return product_data
        except ProductType.DoesNotExist as e:
            print(e)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(e) + ' : ' + str(id))
            return error_obj

    def fetch_download_pdttype_list(self, vys_page):
        try:
            obj = ProductType.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())
            list_len = len(obj)
            pro_list = NWisefinList()
            if list_len <= 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_PRODUCTTYPE_ID)
                error_obj.set_description(ErrorDescription.INVALID_PRODUCTTYPE_ID)
                return error_obj
            else:
                for pro in obj:
                    print(pro)
                    protype_res = ProducttypeResponse()
                    protype_res.set_id(pro.id)
                    protype_res.set_code(pro.code)
                    protype_res.set_name(pro.name)
                    protype_res.productcategory=pro.productcategory.name
                    #protype_res.set_productcategory(pro.productcategory)
                    pro_list.append(protype_res)
                return pro_list
        except:
            logger.error('ERROR_ProductType_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PRODUCTTYPE_ID)
            error_obj.set_description(ErrorDescription.INVALID_PRODUCTTYPE_ID)
            return error_obj
