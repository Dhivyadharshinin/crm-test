import traceback

import django
from django.db import IntegrityError
from masterservice.data.response.productresponse import ProductResponse ,ProducSearchResponse,productcat_type_list,ProductCategory_dev_Response,HsnResponse
from masterservice.service.Hsnservice import Hsnservice
from masterservice.service.productcategoryservice import Productcategoryservice
from masterservice.service.producttypeservice import ProducttypeService
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from masterservice.models import Product, Hsn, Uom, Apcategory, APsubcategory, ProductCategory,ProductType
from datetime import datetime

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

now = datetime.now()
from masterservice.data.request.masterauditrequest import MasterAuditRequest
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.util.masterutil import ModifyStatus, MasterRefType, RequestStatusUtil, Master_Drop_down
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from django.db.models import Q
import json


class ProductService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_product(self, prdct_obj, user_id):
        if not prdct_obj.get_id() is None:
            try:
                logger.error('PRODUCT: Product Update Started')
                product_update = Product.objects.using(self._current_app_schema()).filter(id=prdct_obj.get_id(),
                                                                                          entity_id=self._entity_id()).update(
                    code=prdct_obj.get_code(),
                    name=prdct_obj.get_name(),
                    productdisplayname=prdct_obj.get_productdisplayname(),
                    weight=prdct_obj.get_weight(),
                    unitprice=prdct_obj.get_unitprice(),
                    uom_id=prdct_obj.get_uomid(),
                    hsn_id=prdct_obj.get_hsn_id(),
                    category_id=prdct_obj.get_categoryid(),
                    subcategory_id=prdct_obj.get_subcategoryid(),
                    productcategory_id=prdct_obj.get_productcategoryid(),
                    producttype_id=prdct_obj.get_producttypeid(),
                    producttradingitem=prdct_obj.get_producttradingitem(),
                    product_details=prdct_obj.get_product_details(),
                    product_isblocked=prdct_obj.get_product_isblocked(),
                    product_isrcm=prdct_obj.get_product_isrcm(),
                    updated_date=now,
                    updated_by=user_id)
                prdct_var = Product.objects.using(self._current_app_schema()).get(id=prdct_obj.get_id(),
                                                                                  entity_id=self._entity_id())
                logger.error('PRODUCT: Product Update Success' + str(product_update))
                product_auditdata = {'id': prdct_obj.get_id(),
                                     'code': prdct_obj.get_code(),
                                     'name': prdct_obj.get_name(),
                                     'weight': prdct_obj.get_weight(),
                                     'unitprice': prdct_obj.get_unitprice(),
                                     'uom_id': prdct_obj.get_uomid(),
                                     'category_id': prdct_obj.get_categoryid(),
                                     'subcategory_id': prdct_obj.get_subcategoryid(),
                                     'updated_date': now,
                                     'updated_by': user_id}
                self.audit_function(product_auditdata, user_id, prdct_var.id, ModifyStatus.update)
            except IntegrityError as error:
                logger.error('ERROR_Product_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Product.DoesNotExist:
                logger.error('ERROR_Product_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CATEGORY_ID)
                error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
                return error_obj
            except:
                logger.error('ERROR_Product_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('PRODUCT: Product Creation Started')
                prdct_var = Product.objects.using(self._current_app_schema()).create(
                                                name=prdct_obj.get_name(),
                                                weight=prdct_obj.get_weight(),
                                                unitprice=prdct_obj.get_unitprice(),
                                                uom_id=prdct_obj.get_uomid(),
                                                hsn_id=prdct_obj.get_hsn_id(),
                                                category_id=prdct_obj.get_categoryid(),
                                                subcategory_id=prdct_obj.get_subcategoryid(),
                                                # type=prdct_obj.get_type(),
                                                productcategory_id=prdct_obj.get_productcategoryid(),
                                                producttype_id=prdct_obj.get_producttypeid(),
                                                product_details=prdct_obj.get_product_details(),
                                                productdisplayname=prdct_obj.get_productdisplayname(),
                                                producttradingitem=prdct_obj.get_producttradingitem(),
                                                product_isblocked=prdct_obj.get_product_isblocked(),
                                                product_isrcm=prdct_obj.get_product_isrcm(),
                                                created_by=user_id, entity_id=self._entity_id())
                try:
                    max_cat_code = Product.objects.using(self._current_app_schema()).filter(code__regex='^[P]\d*[0-9]').order_by('-code')[0].code
                    rnsl = int(max_cat_code[1:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "P" + str(new_rnsl).zfill(5)
                # max_cat_code = ProductCategory.objects.filter(code__icontains='VPDT').order_by('-code')[0].code
                # rnsl = int(max_cat_code[3:])
                # new_rnsl = rnsl + 1
                # code = "VPDT" + str(new_rnsl).zfill(5)
                # code = "VPDT" + str(prdct_var.id)
                prdct_var.code = code
                prdct_var.save()
                logger.error('PRODUCT: Product Creation Success' + str(prdct_var))
                self.audit_function(prdct_var, user_id, prdct_var.id, ModifyStatus.create)
            except IntegrityError as error:
                logger.error('ERROR_Product_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_Product_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        product_data = ProductResponse()
        product_data.set_id(prdct_var.id)
        product_data.set_code(prdct_var.code)
        product_data.set_name(prdct_var.name)
        product_data.set_weight(prdct_var.weight)
        product_data.set_unitprice(prdct_var.unitprice)
        product_data.set_product_details(prdct_var.product_details)
        product_data.set_productdisplayname(prdct_var.productdisplayname)
        product_data.set_producttradingitem(prdct_var.producttradingitem)
        # return product_data
        data = NWisefinSuccess()
        data.set_status(SuccessStatus.SUCCESS)
        data.set_message(SuccessMessage.CREATE_MESSAGE)
        return data
    def fetch_product_dep(self):
        productlist = Product.objects.using(self._current_app_schema()).all().values('id', 'name')
        list_length = len(productlist)
        if list_length >= 0:
            product_list_data = NWisefinList()
            for productobj in productlist:
                product_list_data.append(productobj)
            return product_list_data
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PRODUCT_ID)
            error_obj.set_description(ErrorDescription.INVALID_PRODUCT_ID)
            return error_obj

    def fetch_product_list(self,request,vys_page):
        try:
            # condition = Q(status=1)
            # if "data" in request.GET:
            #     print("ss")
            #     condition &= Q(hsn_id__icontains=request.GET.get("data"))
            # productlist = Product.objects.filter(status=1).order_by('created_date')[
                          # vys_page.get_offset():vys_page.get_query_limit()]
            condition = Q()
            if "data" in request.GET:
                condition &= Q(name__icontains=request.GET.get("data"))
            # condition = Q(name__icontains=, status=1)
            # productlist = Product.objects.filter(condition)
            productlist = Product.objects.using(self._current_app_schema()).filter(condition).order_by('id')[
                             vys_page.get_offset():vys_page.get_query_limit()]
            # print(productlist)

            list_length = len(productlist)
            if list_length >= 0:
                product_list_data = NWisefinList()
                for productobj in productlist:
                    hsn_service = Hsnservice(self._scope())  # changed
                    product_data = ProductResponse()
                    pducttype_service = ProducttypeService(self._scope())  # changed
                    pductcat_service = Productcategoryservice(self._scope())  # changed
                    product_data.set_status(productobj.status)
                    product_data.set_id(productobj.id)
                    product_data.set_code(productobj.code)
                    product_data.set_name(productobj.name)
                    product_data.set_weight(productobj.weight)
                    product_data.set_unitprice(productobj.unitprice)
                    product_data.set_uomid(productobj.uom)
                    product_data.set_hsn_id(productobj.hsn)
                    product_data.set_categoryid(productobj.category)
                    product_data.set_subcategoryid(productobj.subcategory)
                    product_data.set_product_details(productobj.product_details)
                    product_data.set_productdisplayname(productobj.productdisplayname)
                    product_data.set_producttradingitem(productobj.producttradingitem)
                    product_data.set_product_isrcm(productobj.product_isrcm)
                    product_data.set_product_isblocked(productobj.product_isblocked)
                    # landlorddetail_data.set_address(address_service.fetch_address(landlorddetails.address_id,emp_id))
                    product_data.set_hsn_id(hsn_service.fetch_hsn(productobj.hsn_id))
                    # product_data.set_uomid(uom_service.)
                    # product_data.set_prod(pducttype_service.fetch_producttype(productobj.producttype_id))
                    product_data.set_producttypeid(pducttype_service.fetch_producttype(productobj.producttype_id))
                    product_data.set_productcategoryid(pductcat_service.fetch_productcat(productobj.productcategory_id))
                    product_data.set_status(productobj.status)
                    product_list_data.append(product_data)


                vpage = NWisefinPaginator(productlist, vys_page.get_index(), 10)
                product_list_data.set_pagination(vpage)
                return product_list_data
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_PRODUCT_ID)
                error_obj.set_description(ErrorDescription.INVALID_PRODUCT_ID)
                return error_obj
        except:
            logger.error('ERROR_Product_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PRODUCT_ID)
            error_obj.set_description(ErrorDescription.INVALID_PRODUCT_ID)
            return error_obj

    def fetch_product(self, product_id, user_id):
        try:
            hsn_service = Hsnservice(self._scope())  # changed
            producttype_service = ProducttypeService(self._scope())  # changed
            productcat_service = Productcategoryservice(self._scope())  # changed
            prdct_var = Product.objects.using(self._current_app_schema()).get(id=product_id,
                                                                              entity_id=self._entity_id())
            product_data = ProductResponse()
            product_data.set_id(prdct_var.id)
            product_data.set_code(prdct_var.code)
            product_data.set_name(prdct_var.name)
            product_data.set_weight(prdct_var.weight)
            product_data.set_unitprice(prdct_var.unitprice)
            product_data.set_uomid(prdct_var.uom)
            product_data.set_categoryid(prdct_var.category)
            product_data.set_product_details(prdct_var.product_details)
            product_data.set_productdisplayname(prdct_var.productdisplayname)
            product_data.set_producttradingitem(prdct_var.producttradingitem)
            product_data.set_subcategoryid(prdct_var.subcategory)
            product_data.set_hsn_id(hsn_service.fetch_hsn(prdct_var.hsn_id))
            product_data.set_producttypeid(producttype_service.fetch_producttype(prdct_var.producttype_id))
            product_data.set_productcategoryid(productcat_service.fetch_productcat(prdct_var.productcategory_id))
            # product_data.set_product_details(prdct_var.product_details)
            return product_data
        except Product.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PRODUCT_ID)
            error_obj.set_description(ErrorDescription.INVALID_PRODUCT_ID)
            return error_obj

    def fetch_product_code(self, product_code, user_id):
        try:
            hsn_service = Hsnservice(self._scope())  # changed
            producttype_service = ProducttypeService(self._scope())  # changed
            productcat_service = Productcategoryservice(self._scope())  # changed
            prdct_var = Product.objects.using(self._current_app_schema()).get(code=product_code,
                                                                              entity_id=self._entity_id())
            product_data = ProductResponse()
            product_data.set_id(prdct_var.id)
            product_data.set_code(prdct_var.code)
            product_data.set_name(prdct_var.name)
            product_data.set_weight(prdct_var.weight)
            product_data.set_unitprice(prdct_var.unitprice)
            product_data.set_uomid(prdct_var.uom)
            product_data.set_categoryid(prdct_var.category)
            product_data.set_subcategoryid(prdct_var.subcategory)
            product_data.set_hsn_id(hsn_service.fetch_hsn(prdct_var.hsn_id))
            product_data.set_producttypeid(producttype_service.fetch_producttype(prdct_var.producttype_id))
            product_data.set_productcategoryid(productcat_service.fetch_productcat(prdct_var.productcategory_id))
            product_data.set_product_details(prdct_var.product_details)
            return product_data
        except Product.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PRODUCT_ID)
            error_obj.set_description(ErrorDescription.INVALID_PRODUCT_ID)
            return error_obj

    def delete_product(self, product_id, user_id):
        product = Product.objects.using(self._current_app_schema()).filter(id=product_id,
                                                                           entity_id=self._entity_id()).delete()
        self.audit_function(product, user_id, product_id, ModifyStatus.delete)
        if product[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PRODUCT_ID)
            error_obj.set_description(ErrorDescription.INVALID_PRODUCT_ID)
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
        audit_obj.set_relreftype(MasterRefType.PRODUCT)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return

    def fetch_product_search(self, query, vys_page):
        if query is None:
            productlist = Product.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id()).order_by('created_date')[
                          vys_page.get_offset():vys_page.get_query_limit()]
        else:
            condition = Q(name__icontains=query) & Q(entity_id=self._entity_id())
            productlist = Product.objects.using(self._current_app_schema()).filter(condition)[
                          vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(productlist)
        if list_length >= 0:
            product_list_data = NWisefinList()
            for productobj in productlist:
                product_data = ProducSearchResponse()
                product_data.set_id(productobj.id)
                product_data.set_status(productobj.status)
                product_data.set_code(productobj.code)
                product_data.set_name(productobj.name)
                product_data.set_hsn_id(productobj.hsn)
                product_data.set_category(productobj.category)
                product_data.set_subcategory(productobj.subcategory)
                product_data.set_productcategoryid(productobj.productcategory)
                product_data.set_producttypeid(productobj.producttype)
                product_data.set_weight(productobj.weight)
                product_data.set_unitprice(productobj.unitprice)
                product_data.set_product_details(productobj.product_details)
                product_data.set_uom_id(productobj.uom)
                product_data.set_productdisplayname(productobj.productdisplayname)
                product_data.set_producttradingitem(productobj.producttradingitem)
                product_list_data.append(product_data)
                vpage = NWisefinPaginator(productlist, vys_page.get_index(), 10)
                product_list_data.set_pagination(vpage)
            return product_list_data
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PRODUCT_ID)
            error_obj.set_description(ErrorDescription.INVALID_PRODUCT_ID)
            return error_obj

    def create_product_mtom(self, prdct_obj,action, user_id):
        try:
            hsn_data = Hsn.objects.using(self._current_app_schema()).get(code=prdct_obj.get_hsn_code())
            uom_data = Uom.objects.using(self._current_app_schema()).get(code=prdct_obj.get_uom_code())
            apcategory_data = Apcategory.objects.using(self._current_app_schema()).get(code=prdct_obj.get_category_code())
            apsubcategory_data = APsubcategory.objects.using(self._current_app_schema()).get(code=prdct_obj.get_subcategory_code(),category_id=apcategory_data.id)
            productcat_data = ProductCategory.objects.using(self._current_app_schema()).get(code=prdct_obj.get_productcategory_code())
            product_type = ProductType.objects.using(self._current_app_schema()).get(code=prdct_obj.get_producttype_code())
        except Exception  as excep:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj
        if not prdct_obj.get_product_details() is None:
            if not prdct_obj.get_id() is None:
                try:
                    product_update = Product.objects.using(self._current_app_schema()).filter(id=prdct_obj.get_id()).update(
                                    code=prdct_obj.get_code(),
                                    name=prdct_obj.get_name(),
                                    weight=prdct_obj.get_weight(),
                                    unitprice=prdct_obj.get_unitprice(),
                                    uom_id=uom_data.id,
                                    hsn_id=hsn_data.id,
                                    category_id=apcategory_data.id,
                                    subcategory_id=apsubcategory_data.id,
                                    productcategory_id=productcat_data.id,
                                    producttype_id=product_type.id,
                                    product_details = prdct_obj.get_product_details(),
                                    updated_date=now,
                                    updated_by=user_id)
                    prdct_var = Product.objects.using(self._current_app_schema()).get(id=prdct_obj.get_id())
                    product_auditdata={'id':prdct_obj.get_id(),
                                    'code':prdct_obj.get_code(),
                                    'name':prdct_obj.get_name(),
                                    'weight':prdct_obj.get_weight(),
                                    'unitprice':prdct_obj.get_unitprice(),
                                    'uom_id':uom_data.id,
                                    'category_id':apcategory_data.id,
                                    'subcategory_id':apsubcategory_data.id,
                                    'updated_date':now,
                                    'updated_by':user_id}
                    self.audit_function(product_auditdata, user_id, prdct_var.id, ModifyStatus.update)
                    logger.error("product mtom updated")
                except IntegrityError as error:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
                except Product.DoesNotExist:
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
                    prdct_var = Product.objects.using(self._current_app_schema()).create(
                                                    code=prdct_obj.get_code(),
                                                    name=prdct_obj.get_name(),
                                                    weight=prdct_obj.get_weight(),
                                                    unitprice=prdct_obj.get_unitprice(),
                                                    uom_id=uom_data.id,
                                                    hsn_id=hsn_data.id,
                                                    category_id=apcategory_data.id,
                                                    subcategory_id=apsubcategory_data.id,
                                                    productcategory_id=productcat_data.id,
                                                    producttype_id=product_type.id,
                                                    product_details=prdct_obj.get_product_details(),
                                                    created_by=user_id, entity_id=self._entity_id())

                    self.audit_function(prdct_var, user_id, prdct_var.id, ModifyStatus.create)
                    logger.error("product mtom created")
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
            product_data = ProductResponse()
            product_data.set_id(prdct_var.id)
            product_data.set_code(prdct_var.code)
            product_data.set_hsn_id(prdct_var.hsn_id)
            product_data.set_name(prdct_var.name)
            product_data.set_weight(prdct_var.weight)
            product_data.set_unitprice(prdct_var.unitprice)
            return product_data
        else:
            if action=='update':
                try:
                    product_update = Product.objects.using(self._current_app_schema()).filter(id=prdct_obj.get_id(),
                                                                                              entity_id=self._entity_id()).update(
                        code=prdct_obj.get_code(),
                        name=prdct_obj.get_name(),
                        weight=prdct_obj.get_weight(),
                        unitprice=prdct_obj.get_unitprice(),
                        uom_id=uom_data.id,
                        hsn_id=hsn_data.id,
                        category_id=apcategory_data.id,
                        subcategory_id=apsubcategory_data.id,
                        productcategory_id=productcat_data.id,
                        producttype_id=product_type.id,
                        status=prdct_obj.get_status(),
                        updated_date=now,
                        updated_by=user_id)
                    prdct_var = Product.objects.using(self._current_app_schema()).get(code=prdct_obj.get_code())
                    product_auditdata = {'id': prdct_var.id,
                                         'code': prdct_obj.get_code(),
                                         'name': prdct_obj.get_name(),
                                         'weight': prdct_obj.get_weight(),
                                         'unitprice': prdct_obj.get_unitprice(),
                                         'uom_id': uom_data.id,
                                         'category_id': apcategory_data.id,
                                         'subcategory_id': apsubcategory_data.id,
                                         'updated_date': now,
                                         'updated_by': user_id}
                    self.audit_function(product_auditdata, user_id, prdct_var.id, ModifyStatus.update)
                    logger.error("product mtom updated")
                except IntegrityError as error:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
                except Product.DoesNotExist:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_CATEGORY_ID)
                    error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
                    return error_obj
                except:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                    return error_obj
            elif action=='create' :
                try:
                    prdct_var = Product.objects.using(self._current_app_schema()).create(
                        code=prdct_obj.get_code(),
                        name=prdct_obj.get_name(),
                        weight=prdct_obj.get_weight(),
                        unitprice=prdct_obj.get_unitprice(),
                        uom_id=uom_data.id,
                        hsn_id=hsn_data.id,
                        category_id=apcategory_data.id,
                        subcategory_id=apsubcategory_data.id,
                        productcategory_id=productcat_data.id,
                        producttype_id=product_type.id,
                        # product_details=prdct_obj.get_product_details(),
                        created_by=user_id, entity_id=self._entity_id())

                    self.audit_function(prdct_var, user_id, prdct_var.id, ModifyStatus.create)
                    logger.error("product mtom created")
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
            product_data = ProductResponse()
            product_data.set_id(prdct_var.id)
            product_data.set_code(prdct_var.code)
            product_data.set_hsn_id(prdct_var.hsn_id)
            product_data.set_name(prdct_var.name)
            product_data.set_weight(prdct_var.weight)
            product_data.set_unitprice(prdct_var.unitprice)
            return product_data

    def search_productname(self, query):
        try:
            condition = Q(name__exact=query) & Q(entity_id=self._entity_id())
            hsn_service = Hsnservice(self._scope())  # changed
            producttype_service = ProducttypeService(self._scope())  # changed
            productcat_service = Productcategoryservice(self._scope())  # changed
            prdct_var = Product.objects.using(self._current_app_schema()).filter(condition)
            product_list = []
            for i in prdct_var:
                product_data = ProductResponse()
                product_data.set_id(i.id)
                product_data.set_code(i.code)
                product_data.set_name(i.name)
                product_data.set_weight(i.weight)
                product_data.set_unitprice(i.unitprice)
                product_data.set_uomid(i.uom)
                product_data.set_hsn_id(hsn_service.fetch_hsn(i.hsn_id))
                product_data.set_producttypeid(producttype_service.fetch_producttype(i.producttype_id))
                product_data.set_productcategoryid(productcat_service.fetch_productcat(i.productcategory_id))
                product_list.append(product_data.get())
            return product_list
        except Product.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PRODUCT_ID)
            error_obj.set_description(ErrorDescription.INVALID_PRODUCT_ID)
            return error_obj

    def search_productcode(self, query):
        try:
            condition = Q(code=query) & Q(entity_id=self._entity_id())
            hsn_service = Hsnservice(self._scope())  # changed
            producttype_service = ProducttypeService(self._scope())  # changed
            productcat_service = Productcategoryservice(self._scope())  # changed
            prdct_var = Product.objects.using(self._current_app_schema()).get(condition)
            product_data = ProductResponse()
            product_data.set_id(prdct_var.id)
            product_data.set_code(prdct_var.code)
            product_data.set_name(prdct_var.name)
            product_data.set_weight(prdct_var.weight)
            product_data.set_unitprice(prdct_var.unitprice)
            product_data.set_uomid(prdct_var.uom)
            product_data.set_hsn_id(hsn_service.fetch_hsn(prdct_var.hsn_id))
            product_data.set_producttypeid(producttype_service.fetch_producttype(prdct_var.producttype_id))
            product_data.set_productcategoryid(productcat_service.fetch_productcat(prdct_var.productcategory_id))
            product_data.set_product_isrcm(prdct_var.product_isrcm)
            product_data.set_product_isblocked(prdct_var.product_isblocked)
            return product_data
        except Product.DoesNotExist as e:
            print(e)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PRODUCT_ID)
            error_obj.set_description(str(e)+' : '+query)
            return error_obj
        except Exception as e:
            from nwisefin.settings import logger
            logger.error(e)
            import traceback
            traceback.print_exc()

    def search_product(self, query):
        if query is None:
            productlist = Product.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())
        else:
            condition = Q(name__icontains=query) & Q(entity_id=self._entity_id())
            productlist = Product.objects.using(self._current_app_schema()).filter(condition)
        list_length = len(productlist)
        product_list_data = NWisefinList()
        if list_length > 0:
            for productobj in productlist:
                product_data = ProductResponse()
                product_data.set_id(productobj.id)
                product_data.set_name(productobj.name)
                product_data.set_code(productobj.code)
                product_data.set_uomid(productobj.uom)
                product_data.set_hsn_id(productobj.hsn)
                product_data.set_product_isrcm(productobj.product_isrcm)
                product_list_data.append(product_data)
        return product_list_data

    def fetch_productone(self, product_code):
        product = Product.objects.using(self._current_app_schema()).get(code=product_code, entity_id=self._entity_id())
        product_data = {"id": product.id, "code": product.code, "name": product.name}
        product_dic = json.dumps(product_data, indent=4)
        return product_data


    # prpo
    def fetch_productlistget(request, product_data):
        productId_arr = product_data['product_id']
        product = Product.objects.using(request._current_app_schema()).filter(id__in=productId_arr,
                                                                              entity_id=request._entity_id()).values(
            'id', 'code', 'name')
        product_list_data = NWisefinList()
        for i in product:
            data = {"id": i['id'], "code": i['code'], "name": i['name']}
            product_list_data.append(data)
        return product_list_data.get()

    # prpo
    def productcat_list(self, product_data):
        productId_arr = product_data['product_id']
        product = Product.objects.using(self._current_app_schema()).filter(id__in=productId_arr,
                                                                           entity_id=self._entity_id()).values('id',
                                                                                                               'productcategory_id',
                                                                                                               'producttype_id')
        product_list_data = NWisefinList()
        prod_cat_arr = []
        if len(product) > 0:
            for i in product:
                if i['productcategory_id'] not in prod_cat_arr:
                    print("i['productcategory_id']", i['productcategory_id'])
                    prod_cat_arr.append(i['productcategory_id'])
            data = {"id": prod_cat_arr}
            product_list_data.append(data)
        return product_list_data

    def pdtcat_name(self, product_data, query):
        productId_arr = product_data['product_id']
        condition = Q(id__in=productId_arr) | Q(productcategory_id__name__icontains=query) | Q(status=1)
        product = Product.objects.using(self._current_app_schema()).filter(condition).values('id',
                                                           'productcategory_id',
                                                           'producttype_id')
        prod_cat_arr = []
        product_list_data = NWisefinList()
        if len(product) > 0:
            for i in product:
                if i['productcategory_id'] not in prod_cat_arr:
                    print("i['productcategory_id']", i['productcategory_id'])
                    prod_cat_arr.append(i['productcategory_id'])
            data = {"id": prod_cat_arr}
            product_list_data.append(data)
        return product_list_data

    def producttype_name(request, product_data, productcategory_id, pdtype_name):
        productId_arr = product_data['product_id']
        condition = (Q(id__in=productId_arr) & Q(productcategory_id=productcategory_id)) | Q(
            producttype_id__name__icontains=pdtype_name)
        print("producttype_name", condition)
        product = Product.objects.using(request._current_app_schema()).filter(condition).values('id',
                                                           'productcategory_id',
                                                           'producttype_id')
        product_list_data = NWisefinList()
        prod_type_arr = []
        prod_arr = []
        if len(product) > 0:
            for i in product:
                if i['producttype_id'] not in prod_type_arr:
                    print("i['producttype_id']", i['producttype_id'])
                    prod_type_arr.append(i['producttype_id'])
                    prod_arr.append(i['producttype_id'])
            data = {"id": prod_type_arr}
            product_list_data.append(data)
        return product_list_data

    def producttype_list(self, product_data, productcategory_id):
        productId_arr = product_data['product_id']
        product = Product.objects.using(self._current_app_schema()).filter(id__in=productId_arr,
                                                                           entity_id=self._entity_id(),
                                                                           productcategory_id=productcategory_id).values(
            'id',
            'productcategory_id',
            'producttype_id')
        product_list_data = NWisefinList()
        prod_cat_arr = []
        if len(product) > 0:
            for i in product:
                if i['producttype_id'] not in prod_cat_arr:
                    print("i['producttype_id']", i['producttype_id'])
                    prod_cat_arr.append(i['producttype_id'])
            data = {"id": prod_cat_arr}
            product_list_data.append(data)
        return product_list_data

    # prpo m2m service
    def product_get(self, product_data):
        logger.error("product_get : " + str(product_data))
        productId_arr = product_data.get('product_id')
        product = Product.objects.using(self._current_app_schema()).filter(id__in=productId_arr,
                                                                           entity_id=self._entity_id()).values('id',
                                                                                                               'code',
                                                                                                               'name')
        product_list_data = NWisefinList()
        for i in product:
            data = {"id": i['id'], "code": i['code'], "name": i['name']}
            product_list_data.append(data)
        return product_list_data.get()

    def fetch_productdata(self, product_id):
        logger.error("fetch_productdata : " + str(product_id))
        try:
            product = Product.objects.using(self._current_app_schema()).get(id=product_id, entity_id=self._entity_id())
            product_data = {"id": product.id,
                            "code": product.code,
                            "name": product.name,
                            "uom_id": product.uom_id,
                            "category_id": product.category_id}
            return product_data
        except Product.DoesNotExist as e:
            print(e)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PRODUCT_ID)
            error_obj.set_description(str(e) + ' : ' + str(product_id))
            return error_obj

    def product_name(self, query):
        product = Product.objects.using(self._current_app_schema()).filter(name__icontains=query,
                                                                           entity_id=self._entity_id()).values_list(
            'id', flat=True)
        prod_arr = []
        for i in product:
            prod_arr.append(i)
        product_data = {"id": prod_arr}
        print(prod_arr)
        return product_data

    def product_cat_type(self, product_category_id, product_type_id):
        condition1 = Q(productcategory_id=product_category_id) \
                     & Q(producttype_id=product_type_id) & Q(entity_id=self._entity_id())
        product = Product.objects.using(self._current_app_schema()).filter(condition1).values_list('id', flat=True)
        prod_arr = []
        for i in product:
            prod_arr.append(i)
        product_data = {"id": prod_arr}
        print(prod_arr)
        return product_data

    def fetch_product_listid(self, list):
        productlist = Product.objects.using(self._current_app_schema()).filter(id__in=list, entity_id=self._entity_id())
        list_length = len(productlist)
        if list_length >= 0:
            product_list_data = NWisefinList()
            for productobj in productlist:
                product_data = ProducSearchResponse()
                product_data.set_id(productobj.id)
                product_data.set_code(productobj.code)
                product_data.set_name(productobj.name)
                product_data.set_hsn_id(productobj.hsn_id)
                product_data.set_category(productobj.category)
                product_data.set_subcategory(productobj.subcategory)
                product_data.set_productcategoryid(productobj.productcategory_id)
                product_data.set_producttypeid(productobj.producttype_id)
                product_list_data.append(product_data)
            return product_list_data

    # prpo
    def get_productcode(self, code):
        logger.error("get_productcode : " + str(code))
        try:
            product = Product.objects.using(self._current_app_schema()).get(code=code, entity_id=self._entity_id())
            product_data = {"id": product.id,
                            "code": product.code,
                            "name": product.name,
                            "category_id": product.category_id}
            return product_data
        except Product.DoesNotExist as e:
            print(e)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PRODUCT_ID)
            error_obj.set_description(str(e) + ' : ' + str(code))
            return error_obj

    def productcategory_list(self, product_data):
        productId_arr = product_data.get('product_id')
        product = Product.objects.using(self._current_app_schema()).filter(id__in=productId_arr,
                                                                           entity_id=self._entity_id()).values('id',
                                                                                                               'productcategory_id',
                                                                                                               'producttype_id')
        product_list_data = NWisefinList()
        prod_cat_arr = []
        if len(product) > 0:
            for i in product:
                if i['productcategory_id'] not in prod_cat_arr:
                    print("i['productcategory_id']", i['productcategory_id'])
                    prod_cat_arr.append(i['productcategory_id'])
            data = {"id": prod_cat_arr}
            product_list_data.append(data)
        return product_list_data.get()

    def productcat_name(self, product_data, query):
        productId_arr = product_data.get('product_id')
        product = Product.objects.using(self._current_app_schema()).filter(id__in=productId_arr,status=1,
                                         productcategory_id__name__icontains=query).values('id',
                                                                                           'productcategory_id',
                                                                                           'producttype_id')
        prod_cat_arr = []
        product_list_data = NWisefinList()
        if len(product) > 0:
            for i in product:
                if i['productcategory_id'] not in prod_cat_arr:
                    print("i['productcategory_id']", i['productcategory_id'])
                    prod_cat_arr.append(i['productcategory_id'])
            data = {"id": prod_cat_arr}
            product_list_data.append(data)
        return product_list_data.get()

    def get_producttype(self, product_data, productcategory_id):
        productId_arr = product_data.get('product_id')
        product = Product.objects.using(self._current_app_schema()).filter(id__in=productId_arr,status=1,
                                         productcategory_id=productcategory_id).values('id',
                                                                                       'productcategory_id',
                                                                                       'producttype_id')
        product_list_data = NWisefinList()
        prod_cat_arr = []
        if len(product) > 0:
            for i in product:
                if i['producttype_id'] not in prod_cat_arr:
                    print("i['producttype_id']", i['producttype_id'])
                    prod_cat_arr.append(i['producttype_id'])
            data = {"id": prod_cat_arr}
            product_list_data.append(data)
        return product_list_data.get()

    def get_producttype_name(self, product_data, productcategory_id, pdtype_name):
        productId_arr = product_data.get('product_id')
        product = Product.objects.using(self._current_app_schema()).filter(id__in=productId_arr, productcategory_id=productcategory_id,status=1,
                                         producttype_id__name__icontains=pdtype_name).values('id',
                                                                                             'productcategory_id',
                                                                                             'producttype_id')
        product_list_data = NWisefinList()
        prod_type_arr = []
        prod_arr = []
        if len(product) > 0:
            for i in product:
                if i['producttype_id'] not in prod_type_arr:
                    print("i['producttype_id']", i['producttype_id'])
                    prod_type_arr.append(i['producttype_id'])
                    prod_arr.append(i['producttype_id'])
            data = {"id": prod_type_arr}
            product_list_data.append(data)
        return product_list_data.get()

    def fetch_apcategorydata(self, category_id):
        obj = Apcategory.objects.using(self._current_app_schema()).get(id=category_id)
        emp_data = {"id": obj.id,
                    "code": obj.code,
                    "name": obj.name,
                    "isasset": obj.isasset,
                    "no": obj.no}
        return emp_data

    # def product_devision(self,div_obj):
    #
    #
    #     if not div_obj.get_id() is None:
    #         try:
    #             product_devision_template = ProductDevision.objects.filter(id=div_obj.get_id()).update(
    #                                                                 type = div_obj.get_type(),
    #                                                                 created_by = div_obj.get_created_by(),
    #                                                             created_date = div_obj.get_created_date(),
    #                                                             updated_by = div_obj.get_updated_by(),
    #                                                             updated_date = div_obj.get_updated_date()
    #
    #                 )
    #             devision = ProductDevision.objects.get(id=div_obj.get_id())
    #             print(devision)
    #         except:
    #             pass
    #     else:
    #         # try:
    #         devision = ProductDevision.objects.create (type=div_obj.get_type(),
    #                                                     created_by=div_obj.get_created_by(),
    #                                                   created_date=div_obj.get_created_date(),
    #                                                 # updated_by = div_obj.get_updated_by(),
    #                                                 #     updated_date = div_obj.get_updated_date()
    #                                                    )
    #
    #
    #
    #
    #             # return product_dev
    #         # except:
    #         #     pass
    #
        # product_dev = product_devision()
    #     product_dev.set_id(devision.id),
    #     product_dev.set_type(devision.type),
    #     product_dev.set_created_by(devision.created_by),
    #     product_dev.set_created_date(devision.created_date),
    #     product_dev.set_updated_by(devision.updated_by),
    #     product_dev.set_updated_date(devision.updated_date)
    #     print(product_dev)
    #     return product_dev
    def productclassication_service_cat_map(self,request,number,vys_page):
        condition=Q(isprodservice=number,status=1)
        if "data" in request.GET:
           condition &= Q(name__icontains=request.GET.get("data"))
        # if "data" in request.GET:
        #    condition &= Q(name=request.GET.get("data"))
        category_dev_map=ProductCategory.objects.using(self._current_app_schema()).filter(condition).values('id','code','name','isprodservice')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        print(category_dev_map)
        # list=productcat_type_list()
        product_cat_list= NWisefinList()
        data=len(category_dev_map)
        if data<=0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_PRODUCT_CATEGORY_ID)
            return error_obj


        else:    
            for i in category_dev_map:
                # print(i['code'])
                response=ProductCategory_dev_Response()
                # classification_details=self.get_classication_data(number)
                # print(classification_details)
                response.set_product_category(i['name'])
                response.set_id(i['id'])
                product_cat_list.append(response)
            vpage = NWisefinPaginator(category_dev_map, vys_page.get_index(), 10)
            product_cat_list.set_pagination(vpage)
            return product_cat_list

    # def get_product_category(self,no):
    #     product_cat_data = ProductCategory.objects.filter(isprodservice=no).values('code','name','isprodservice')
    #     print(product_cat_data)
    #     return product_cat_data[0]
    def get_product_subcategory(self,id):
        product_subcategory=ProductType.objects.using(self._current_app_schema()).filter(productcategory__in=id).values('code','name','productcategory_id','productcategory')
        return product_subcategory

    def get_classication_data(self, number):
        from masterservice.util.masterutil import ProductClassification
        app_service=ProductClassification()
        resp_obj = app_service.getclassificationType_one(number)
        employee_dic = json.dumps(resp_obj, indent=4)
        return employee_dic

    def product_classication_service_subcat_map(self,request,product_cat_id,vys_page):
        condition = Q(productcategory_id=product_cat_id,status=1)
        # condition = Q(productcategory__in=product_cat_id)
        if "data" in request.GET:
            condition &= Q(name__icontains=request.GET.get("data"))
        product_subcategory = ProductType.objects.using(self._current_app_schema()).filter(condition).values('id','code', 'name','productcategory_id',
                                                                                        )[
                         vys_page.get_offset():vys_page.get_query_limit()]
        print(product_subcategory)
        # list = productcat_type_list()
        product_subcat_list = NWisefinList()
        data= len(product_subcategory)

        if data<=0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_SUB_CATEGORY_ID)
            return error_obj
        else:
            for i in product_subcategory:
                # print(i['code'])
                response = ProductCategory_dev_Response()

                response.set_product_subcategory(i['name'])
                response.set_id(i['id'])
                product_subcat_list.append(response)
            vpage = NWisefinPaginator(product_subcategory, vys_page.get_index(), 10)
            product_subcat_list.set_pagination(vpage)
            return product_subcat_list

    def get_hsn_service(self,request,vys_page):
        condition = Q()
        if "data" in request.GET:
            condition &= Q(code__icontains=request.GET.get("data"))
        hsn_data = Hsn.objects.using(self._current_app_schema()).filter(condition).values('id', 'code','igstrate')[
                              vys_page.get_offset():vys_page.get_query_limit()]
        # list = productcat_type_list()
        data=len(hsn_data)
        if data  <=0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_HSN_DATA)
            return error_obj
        else:
            hsn_list = NWisefinList()
            for i in hsn_data:
                # print(i['code'])
                response = HsnResponse()
                response.set_id(i['id'])
                response.set_code(i['code'])
                response.set_igstrate(i['igstrate'])
                hsn_list.append(response)
            vpage = NWisefinPaginator(hsn_data, vys_page.get_index(), 10)
            hsn_list.set_pagination(vpage)
            return hsn_list

    def create_product_inactivate(self,request,prdct_obj,product_id):
        # print(prdct_obj.status)
        if(int(prdct_obj.status)==0):

            product_data = Product.objects.using(self._current_app_schema()).filter(id=product_id).update(
                    status=1)
        else:
            product_data = Product.objects.using(self._current_app_schema()).filter(id=product_id).update(
                    status=0)
        prdct_var = Product.objects.using(self._current_app_schema()).get(id=product_id)
        data = ProductResponse()
        data.set_status(prdct_var.status)
        status=prdct_var.status
        # print(status)
        data.set_id(prdct_var.id)

        if status==1:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.INACTIVATED)
            return data
        else:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.ACTIVATED)
            return data

        # return data


    def fetch_first_product(self):
        productobj = Product.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())[0]
        product_data = ProductResponse()
        product_data.set_id(productobj.id)
        product_data.set_name(productobj.name)
        product_data.set_code(productobj.code)
        product_data.set_uomid(productobj.uom)
        product_data.set_hsn_id(productobj.hsn)
        product_data.set_product_isrcm(productobj.product_isrcm)
        return product_data

    def fetch_product_download(self,request):
        try:
            condition = Q()
            productlist = Product.objects.using(self._current_app_schema()).filter(condition).order_by('id')
            list_length = len(productlist)
            if list_length >= 0:
                product_list_data = NWisefinList()
                for productobj in productlist:
                    product_data = ProductResponse()
                    product_data.Code = productobj.code
                    product_data.Name = productobj.name
                    product_data.Weight = productobj.weight
                    product_data.Unitprice = productobj.unitprice
                    from utilityservice.service.prpo_api_service import ApiService
                    if productobj.uom_id is not None:
                        product_data.Uom_Name = Uom.objects.using(self._current_app_schema()).get(id=productobj.uom_id).name
                    else:
                        product_data.Uom_Name = ""
                    if productobj.hsn_id is not None:
                        product_data.Hsn_Code = Hsn.objects.using(self._current_app_schema()).get(id=productobj.hsn_id).code
                    else:
                        product_data.Hsn_Code = ""
                    try:
                        product_data.AP_Category_Name = Apcategory.objects.using(self._current_app_schema()).get(id=productobj.category_id).name
                    except:
                        product_data.AP_Category_Name = ""
                    try:
                        product_data.AP_SubCategory_Name = APsubcategory.objects.using(self._current_app_schema()).get(id=productobj.subcategory_id).name
                    except:
                        product_data.AP_SubCategory_Name = ""
                    if productobj.product_details is not None:
                        product_data.Product_Details = productobj.product_details
                    else:
                        product_data.Product_Details = ""
                    product_data.Product_Display_Name = productobj.productdisplayname
                    product_trading = Master_Drop_down()
                    if productobj.producttradingitem == product_trading.Yes:
                        product_data.Product_Trading_Item = product_trading.Yes_VALUE
                    if productobj.producttradingitem == product_trading.No:
                        product_data.Product_Trading_Item = product_trading.No_VALUE
                    product_data.Product_Is_RCM = productobj.product_isrcm
                    product_data.Product_Is_Blocked = productobj.product_isblocked
                    if productobj.productcategory_id is not None:
                        product_data.Product_Category_Name=ProductCategory.objects.using(self._current_app_schema()).get(id=productobj.productcategory_id).name
                    else:
                        product_data.Product_Category_Name = ""
                    if productobj.producttype_id is not None:
                        product_data.Product_Type_Name = ProductType.objects.using(self._current_app_schema()).get(id=productobj.producttype_id).name
                    else:
                        product_data.Product_Type_Name = ""
                    from masterservice.util.masterutil import MasterStatus
                    status = MasterStatus()
                    if productobj.status == status.Active:
                        product_data.Status = status.Active_VALUE
                    if productobj.status == status.Inactive:
                        product_data.Status = status.Inactive_VALUE
                    product_list_data.append(product_data)
                return product_list_data
            else:
                logger.error('ERROR_Product_Summary_EXCEPT:{}'.format(traceback.format_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_PRODUCT_ID)
                error_obj.set_description(ErrorDescription.INVALID_PRODUCT_ID)
                return error_obj
        except:
            logger.error('ERROR_Product_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PRODUCT_ID)
            error_obj.set_description(ErrorDescription.INVALID_PRODUCT_ID)
            return error_obj