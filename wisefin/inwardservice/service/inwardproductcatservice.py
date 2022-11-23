from inwardservice.data.response.inwardproductcatresponse import ProductcategoryResponse
from django.db.models import Q
from inwardservice.models import ProductCategory
from inwardservice.service.inwardauditservice import InwardAuditService
from django.db import IntegrityError
from inwardservice.util.inwardutil import InwardRefType, ModifyStatus, RequestStatusUtil
from inwardservice.data.response.inwardauditresponse import InwardAuditResponse
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class Productcategoryservice(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.INWARD_SERVICE)
    def create_productcatprocess(self, productcat_obj, emp_id):
        if not productcat_obj.get_id() is None:
            try:
                pdtcat=ProductCategory.objects.filter(id=productcat_obj.get_id()).update(#code=productcat_obj.get_code(),
                                                                                         name=productcat_obj.get_name(),
                                                                                          remarks=productcat_obj.get_remarks(),
                                                                                          is_sys=productcat_obj.get_is_sys())
                pdtcat=ProductCategory.objects.get(id=productcat_obj.get_id())
                self.inward_audit(pdtcat.__dict__, pdtcat.id, emp_id, RequestStatusUtil.ONBORD,
                                  pdtcat.id,
                                  ModifyStatus.UPDATE, InwardRefType.INWARD_PRODUCTCAT)

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                return error_obj
            except ProductCategory.DoesNotExist:
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
                pdtcat=ProductCategory.objects.create(#code=productcat_obj.get_code(),
                                                  name=productcat_obj.get_name(),
                                                   remarks=productcat_obj.get_remarks(),
                                                   is_sys=productcat_obj.get_is_sys(),
                                                    created_by=emp_id)
                code = "ICAT" + str(pdtcat.id)
                pdtcat.code = code
                pdtcat.save()
                req_status = RequestStatusUtil.ONBORD
                self.inward_audit(pdtcat.__dict__, pdtcat.id, emp_id, req_status, pdtcat.id,
                                  ModifyStatus.CREATE, InwardRefType.INWARD_PRODUCTCAT)
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
        productcat_res.set_remarks(pdtcat.remarks)
        productcat_res.set_is_sys(pdtcat.is_sys)
        return productcat_res

    def fetch_productcat(self,productcat_id):
        try:
            pdtcat=ProductCategory.objects.get(id=productcat_id)
            productcat_res = ProductcategoryResponse()
            productcat_res.set_id(pdtcat.id)
            productcat_res.set_code(pdtcat.code)
            productcat_res.set_name(pdtcat.name)
            productcat_res.set_remarks(pdtcat.remarks)
            productcat_res.set_is_sys(pdtcat.is_sys)
            return productcat_res
        except ProductCategory.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_CATEGORY_ID)
            error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
            return error_obj
#list all
    def pdtcat_list(self, vys_page, query):
        obj = ProductCategory.objects.all()[vys_page.get_offset():vys_page.get_query_limit()]
        if query is None:
            pdtcatlist = ProductCategory.objects.filter(status=1)[vys_page.get_offset():vys_page.get_query_limit()]
        else:
            condition = Q(code__icontains=query)|Q(name__icontains=query) & Q(status=1)
            print(condition)
            pdtcatlist = ProductCategory.objects.filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]

        list_len=len(obj)
        pdtcat_list=NWisefinList()
        if list_len <=0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj
        else:
            for pdtcat in pdtcatlist:
                productcat_res = ProductcategoryResponse()
                productcat_res.set_id(pdtcat.id)
                productcat_res.set_code(pdtcat.code)
                productcat_res.set_name(pdtcat.name)
                productcat_res.set_remarks(pdtcat.remarks)
                productcat_res.set_is_sys(pdtcat.is_sys)
                pdtcat_list.append(productcat_res)
            vpage = NWisefinPaginator(obj, vys_page.get_index(), 10)
            pdtcat_list.set_pagination(vpage)
        return pdtcat_list

    def delete_productcat(self, productcat_id,emp_id):
        report = ProductCategory.objects.filter(id=productcat_id).delete()
        self.inward_audit(report, productcat_id, emp_id, RequestStatusUtil.ONBORD, productcat_id,
                          ModifyStatus.DELETE, InwardRefType.INWARD_PRODUCTCAT)
        if report[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_CATEGORY_ID)
            error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def inward_audit(self, inward_data, inward_id, user_id, req_status, inwardrel_id, action, inwardrel_type):
        if action == ModifyStatus.DELETE:
            data = None
        else:
            data = inward_data
        audit_service = InwardAuditService()
        audit_obj = InwardAuditResponse()
        audit_obj.set_refid(inward_id)
        audit_obj.set_reftype(InwardRefType.INWARD_HEADRER)
        audit_obj.set_userid(user_id)
        audit_obj.set_reqstatus(req_status)
        audit_obj.set_relrefid(inwardrel_id)
        audit_obj.set_relreftype(inwardrel_type)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return audit_service

    def search_productcat(self, request, query, vys_page):
        condition = None
        if query is not None:
            condition = Q(name__icontains = query) | Q(code__icontains=query)
        if condition is not None:
            productcatList = ProductCategory.objects.values('id', 'name', 'code').filter(condition)[
                           vys_page.get_offset():vys_page.get_query_limit()]
        else:
            productcatList = ProductCategory.objects.values('id','name', 'code').all()[
                           vys_page.get_offset():vys_page.get_query_limit()]
        vlist = NWisefinList()
        for procat in productcatList:
            productcat_res = ProductcategoryResponse()
            disp_name = '(' + procat['code'] + ') ' + procat['name']
            productcat_res.set_name(disp_name)
            productcat_res.set_id(procat['id'])
            productcat_res.set_name(procat['name'])
            vlist.append(productcat_res)
        vpage = NWisefinPaginator(productcatList, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist
