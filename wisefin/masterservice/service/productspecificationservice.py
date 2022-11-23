import traceback

import django
from django.db import IntegrityError
from masterservice.models import ProductSpecification,ProductCategory
from masterservice.data.response.productspecificationresponse import ProductSpecificationResponse,ProductSpecificationRes
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.util.masterutil import ModifyStatus,MasterRefType,RequestStatusUtil
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from datetime import datetime

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

now = datetime.now()
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from django.db.models import Q


class ProductSpecificationService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_productspec(self, prdspeci_obj, user_id):
        # cate_data = ProductCategory.objects.get(code=prdspeci_obj.get_productcategory_code())
        # print(cate_data)
        cate_data = ProductCategory.objects.using(self._current_app_schema()).get(id=prdspeci_obj.get_productcategory_id())
        print(cate_data)
        if not prdspeci_obj.get_id() is None:
            try:
                logger.error('PRODUCTSPECIFICATION: ProductSpecification Update Started')
                product_update = ProductSpecification.objects.using(self._current_app_schema()).filter(id=prdspeci_obj.get_id()).update(
                                productcategory_id = cate_data.id,
                                templatename = prdspeci_obj.get_templatename(),
                                updated_date=now,
                                updated_by=user_id)
                prd_var = ProductSpecification.objects.get(id=prdspeci_obj.get_id())

                self.audit_function( user_id, prd_var.id, ModifyStatus.update)
                logger.error('PRODUCTSPECIFICATION: ProductSpecification Update Success' + str(product_update))
            except IntegrityError as error:
                logger.error('ERROR_ProductSpecification_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_ProductSpecification_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        else:
            try:
                logger.error('PRODUCTSPECIFICATION: ProductSpecification Creation Started')
                prd_var = ProductSpecification.objects.using(self._current_app_schema()).create(productcategory_id = cate_data.id,
                                                              templatename = prdspeci_obj.get_templatename(),
                                                              created_by=user_id, entity_id=self._entity_id())

                self.audit_function(prd_var, user_id, prd_var.id, ModifyStatus.create)
                logger.error('PRODUCTSPECIFICATION: ProductSpecification Creation Success' + str(prd_var))
            except IntegrityError as error:
                logger.error('ERROR_ProductSpecification_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_ProductSpecification_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        productspeci_data = ProductSpecificationResponse()
        productspeci_data.set_id(prd_var.id)
        productspeci_data.set_productcategory_id(prd_var.productcategory_id)
        productspeci_data.set_templatename(prd_var.templatename)
        # return productspeci_data
        data = NWisefinSuccess()
        data.set_status(SuccessStatus.SUCCESS)
        data.set_message(SuccessMessage.CREATE_MESSAGE)
        return data

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
        audit_obj.set_relreftype(MasterRefType.PRODUCTSPECIFICATION)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return
    def create_productspec_data(self,request,number,vys_page):
        condition = Q(productcategory_id=number)
        if "data" in request.GET:
            condition &= Q(templatename__icontains=request.GET.get("data"))
        category_dev_map = ProductSpecification.objects.using(self._current_app_schema()).filter(condition).values('id','templatename','productcategory_id')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        print(category_dev_map)
        list_len=len(category_dev_map)
        product_specifi_list = NWisefinList()
        if list_len <=0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PRODUCT_CATEGORY_DATA)
            error_obj.set_description(ErrorDescription.INVALID_PRODUCT_CATEGORY_ID)
            return error_obj
        else:
        # product_specifi_list = NWisefinList()
            for i in category_dev_map:
                print(i['id'])
                print(i['templatename'])
                response = ProductSpecificationRes()
                # response.set_product_cat_id(i['productcategory_id'])
                response.set_template_name(i['templatename'])
                response.set_id(i['id'])
                product_specifi_list.append(response)
            vpage = NWisefinPaginator(category_dev_map, vys_page.get_index(), 10)
            product_specifi_list.set_pagination(vpage)
            return product_specifi_list

