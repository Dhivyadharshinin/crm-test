import json
from django.db import IntegrityError
from django.db.models import Q
from django.utils import timezone
from inwardservice.models import ProductSubCategory
from inwardservice.data.response.inwardproductsubcategoryresponse import ProductsubcategoryResponse
from inwardservice.service.inwardproductcatservice import Productcategoryservice
from datetime import datetime

from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

now = datetime.now()


class ProductsubcategoryService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.INWARD_SERVICE)
    def create_prosubcat(self,prosubcatobj,emp_id):
        if not prosubcatobj.get_id() is None:
            try:
                pro=ProductSubCategory.objects.filter(id=prosubcatobj.get_id()).update(
                                                                    product_id=prosubcatobj.get_product_id(),
                                                                    #code=prosubcatobj.get_code(),
                                                                    name=prosubcatobj.get_name(),
                                                                    remarks=prosubcatobj.get_remarks(),
                                                                    is_sys=prosubcatobj.get_is_sys(),
                                                                    updated_by=emp_id,
                                                                    updated_date=timezone.now())
                pro=ProductSubCategory.objects.get(id=prosubcatobj.get_id())

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
                pro=ProductSubCategory.objects.create(product_id=prosubcatobj.get_product_id(),
                                                      #code=prosubcatobj.get_code(),
                                                      name=prosubcatobj.get_name(),
                                                      remarks=prosubcatobj.get_remarks(),
                                                      is_sys=prosubcatobj.get_is_sys(),
                                                      created_by=emp_id,
                                                      created_date= timezone.now())
                code = "ISCT" + str(pro.id)
                pro.code = code
                pro.save()

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

        prosubcat_res=ProductsubcategoryResponse()
        prosubcat_res.set_id(pro.id)
        prosubcat_res.set_product(pro.product)
        prosubcat_res.set_code(pro.code)
        prosubcat_res.set_name(pro.name)
        prosubcat_res.set_remarks(pro.remarks)
        prosubcat_res.set_is_sys(pro.is_sys)
        return prosubcat_res

    def fetch_prosubcat(self,prosubcat_id):
        try:
            pro=ProductSubCategory.objects.get(id=prosubcat_id)
            prosubcat_res = ProductsubcategoryResponse()
            prosubcat_res.set_id(pro.id)
            prosubcat_res.set_product(pro.product)
            prosubcat_res.set_code(pro.code)
            prosubcat_res.set_name(pro.name)
            prosubcat_res.set_remarks(pro.remarks)
            prosubcat_res.set_is_sys(pro.is_sys)
            return prosubcat_res
        except ProductSubCategory.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_INWARDHEADER_ID)
            error_obj.set_description(ErrorDescription.INVALID_INWARDHEADER_ID)
            return error_obj

#list all
    def prosubcat_list(self,vys_page,query):
        obj = ProductSubCategory.objects.all()[vys_page.get_offset():vys_page.get_query_limit()]
        if query is None:
            objj = ProductSubCategory.objects.filter(status=1)[vys_page.get_offset():vys_page.get_query_limit()]
        else:
            condition = Q(name__icontains=query) & Q(status=1)
            print(condition)
            objj = ProductSubCategory.objects.filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]

        list_len=len(obj)
        pro_list=NWisefinList()
        if list_len <=0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_INWARDHEADER_ID)
            error_obj.set_description(ErrorDescription.INVALID_INWARDHEADER_ID)
            return error_obj
        else:
            for pro in objj:
                product_service= Productcategoryservice()
                prosubcat_res = ProductsubcategoryResponse()
                prosubcat_res.set_id(pro.id)
                prosubcat_res.set_product(pro.product)
                prosubcat_res.set_code(pro.code)
                prosubcat_res.set_name(pro.name)
                prosubcat_res.set_remarks(pro.remarks)
                prosubcat_res.set_is_sys(pro.is_sys)
                if pro.product == None:
                    prosubcat_res.set_product(None)
                elif pro.product != None:
                    prosubcat_res.set_product(product_service.fetch_productcat(pro.product_id))
                    pro_list.append(prosubcat_res)
            vpage = NWisefinPaginator(obj,vys_page.get_index(), 10)
            pro_list.set_pagination(vpage)
            return pro_list

#Display records using foreign key
    def prosubcats_list(self,vys_page,product_id):
        obj=ProductSubCategory.objects.filter(product_id=product_id)[vys_page.get_offset():vys_page.get_query_limit()]
        list_len=len(obj)
        prosubcats_list=NWisefinList()
        if list_len <=0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_INWARDHEADER_ID)
            error_obj.set_description(ErrorDescription.INVALID_INWARDHEADER_ID)
            return error_obj
        else:
            for pdtcat in obj:
                productcat_res = ProductsubcategoryResponse()
                productcat_res.set_id(pdtcat.id)
                productcat_res.set_code(pdtcat.code)
                productcat_res.set_name(pdtcat.name)
                productcat_res.set_product(pdtcat.product)
                productcat_res.set_remarks(pdtcat.remarks)
                productcat_res.set_is_sys(pdtcat.is_sys)
                prosubcats_list.append(productcat_res)
        vpage = NWisefinPaginator(obj, vys_page.get_index(), 10)
        prosubcats_list.set_pagination(vpage)
        return prosubcats_list

#delete
    def delete_prosubcat(self, prosubcat_id):
        report = ProductSubCategory.objects.filter(id=prosubcat_id).delete()
        if report[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_TEMPLATE_ID)
            error_obj.set_description(ErrorDescription.INVALID_TEMPLATE_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def search_prosubcat(self, request, query, vys_page):
        condition = None
        if query is not None:
            condition = Q(name__icontains=query) | Q(code__icontains=query)
        if condition is not None:
            prosubcatList = ProductSubCategory.objects.values('id', 'name', 'code').filter(condition)[
                           vys_page.get_offset():vys_page.get_query_limit()]
        else:
            prosubcatList = ProductSubCategory.objects.values('id','name', 'code').all()[
                           vys_page.get_offset():vys_page.get_query_limit()]
        vlist = NWisefinList()
        for pro in prosubcatList:
            prosubcat_res = ProductsubcategoryResponse()
            disp_name = '(' + pro['code'] + ') ' + pro['name']
            prosubcat_res.set_name(disp_name)
            prosubcat_res.set_id(pro['id'])
            prosubcat_res.set_name(pro['name'])
            vlist.append(prosubcat_res)
        vpage = NWisefinPaginator(prosubcatList, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist
