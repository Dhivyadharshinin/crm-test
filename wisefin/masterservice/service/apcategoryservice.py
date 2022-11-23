import traceback

from django.db import IntegrityError
from masterservice.data.response.apcategoryresponse import ApcategoryResponse
from masterservice.service.Codegenerator import CodeGen
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from masterservice.models import APexpense, APsubcategory
from masterservice.models import Apcategory
from django.utils import timezone
from masterservice.data.request.masterauditrequest import MasterAuditRequest
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.util.masterutil import ModifyStatus, MasterRefType, RequestStatusUtil, Code_Gen_Type, Code_Gen_Value, \
    dictdefault
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from django.db.models import Q
from nwisefin.settings import logger
import json

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class CategoryService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_category(self, Category_obj, user_id):
        if not Category_obj.get_id() is None:
            try:
                logger.error('APCATEGORY: Apcategory Update Started')
                category_update = Apcategory.objects.using(self._current_app_schema()).filter(id=Category_obj.get_id(),
                    code=Category_obj.get_name(),
                    entity_id=self._entity_id()).update(
                    # code=Category_obj.get_code(),
                    no=Category_obj.get_no(), name=Category_obj.get_name(), glno=Category_obj.get_glno(),
                    isasset=Category_obj.get_isasset(),
                    updated_by=user_id, updated_date=timezone.now())
                logger.error('APCATEGORY: Apcategory Update Success' + str(category_update))

                category = Apcategory.objects.using(self._current_app_schema()).get(id=Category_obj.get_id(),
                                                                                    entity_id=self._entity_id())
                category_auditdata = {'id': Category_obj.get_id(),
                                      #'code': Category_obj.get_code(),
                                     'no': Category_obj.get_no(),
                                     'name': Category_obj.get_name(), 'glno': Category_obj.get_glno(),
                                     'isasset':  Category_obj.get_isasset(),
                                      'expense_id':Category_obj.get_expense_id(),
                                     'updated_by': user_id, 'updated_date': timezone.now()}
                self.audit_function(category_auditdata, user_id, category.id, ModifyStatus.update)

            except IntegrityError as error:
                logger.error('ERROR_Apcategory_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Apcategory.DoesNotExist:
                logger.error('ERROR_Apcategory_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_District_ID)
                error_obj.set_description(ErrorDescription.INVALID_District_ID)
                return error_obj
            except:
                logger.error('ERROR_Apcategory_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('APCATEGORY: Apcategory Creation Started')
                category = Apcategory.objects.using(self._current_app_schema()).create(  # code=Category_obj.get_code(),
                    no=Category_obj.get_no(),
                    name=Category_obj.get_name(),
                    glno=Category_obj.get_glno(),
                    isasset=Category_obj.get_isasset(),
                    isodit=Category_obj.get_isodit(),
                    code=Category_obj.get_name(),
                    created_by=user_id, entity_id=self._entity_id()
                )
                logger.error('APCATEGORY: Apcategory Creation Success' + str(category))
                # code=Apcategory.objects.using(self._current_app_schema()).get(code=Category_obj.get_name())
                # category.code = code
                # category.save()
                self.audit_function(category, user_id, category.id, ModifyStatus.create)

            except IntegrityError as error:
                logger.error('ERROR_Apcategory_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_Apcategory_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        cat_data = ApcategoryResponse()
        cat_data.set_id(category.id)
        cat_data.set_code(category.code)
        cat_data.set_no(category.no)
        cat_data.set_name(category.name)
        cat_data.set_glno(category.glno)
        cat_data.set_expense_id(category.expense_id)
        cat_data.set_isasset(category.isasset)
        cat_data.set_isodit(category.isodit)
        # return cat_data
        data = NWisefinSuccess()
        data.set_status(SuccessStatus.SUCCESS)
        data.set_message(SuccessMessage.CREATE_MESSAGE)
        return data


    def categorylistActive_dep(self):
        condition = Q(status=1)
        categoryList = Apcategory.objects.using(self._current_app_schema()).all().values('id', 'no')
        list_length = len(categoryList)
        category_list_data = NWisefinList()
        if list_length > 0:
            for category in categoryList:
                category_list_data.append(category)
        return category_list_data

    def fetchcategory(self, category_id):
        try:
            category = Apcategory.objects.using(self._current_app_schema()).get(id=category_id,
                                                                                entity_id=self._entity_id())
            cat_data = ApcategoryResponse()
            cat_data.set_id(category.id)
            cat_data.set_code(category.code)
            cat_data.set_no(category.no)
            cat_data.set_name(category.name)
            cat_data.set_glno(category.glno)
            cat_data.set_isasset(category.isasset)
            cat_data.set_expense(category.expense)
            return cat_data
        except Apcategory.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_category_ID)
            error_obj.set_description(ErrorDescription.INVALID_category_ID)
            return error_obj

    def fetch_category_list(self, vys_page):
        categoryList = Apcategory.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id()).order_by('created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(categoryList)
        category_list_data = NWisefinList()
        if list_length >= 0:
            for category in categoryList:
                cat_data = ApcategoryResponse()
                cat_data.set_id(category.id)
                cat_data.set_code(category.code)
                cat_data.set_no(category.no)
                cat_data.set_name(category.name)
                cat_data.set_glno(category.glno)
                cat_data.set_isasset(category.isasset)
                cat_data.set_expense(category.expense)
                category_list_data.append(cat_data)
            vpage = NWisefinPaginator(categoryList, vys_page.get_index(), 10)
            category_list_data.set_pagination(vpage)
            return category_list_data
        else:
            pass

    def delete_category(self, category_id, user_id):
        category = Apcategory.objects.using(self._current_app_schema()).filter(id=category_id,
                                                                               entity_id=self._entity_id()).delete()
        self.audit_function(category, user_id, category_id, ModifyStatus.delete)

        if category[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_CATEGORY_ID)
            error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def fetch_category_search_list(self, query, vys_page):
        condition = Q(entity_id=self._entity_id())
        if query is None:
            categoryList = Apcategory.objects.using(self._current_app_schema()).filter(condition).order_by(
                'created_date')[
                           vys_page.get_offset():vys_page.get_query_limit()]
        else:
            condition &= Q(name__icontains=query)
            categoryList = Apcategory.objects.using(self._current_app_schema()).filter(condition).order_by(
                'created_date')[
                           vys_page.get_offset():vys_page.get_query_limit()]
            # condition = Q(name__icontains=query)
            # categoryList = Apcategory.objects.filter(condition)
        list_length = len(categoryList)
        category_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for category in categoryList:
                cat_data = ApcategoryResponse()
                cat_data.set_id(category.id)
                cat_data.set_code(category.code)
                cat_data.set_name(category.name)
                # cat_data.set_expense(category.expense)
                category_list_data.append(cat_data)
                vpage = NWisefinPaginator(categoryList, vys_page.get_index(), 10)
                category_list_data.set_pagination(vpage)
        return category_list_data

    def fetch_cat_search_list(self, query):
        condition = Q(status=1) & Q(entity_id=self._entity_id())
        if query is not None:
            condition &= Q(name__icontains=query)
        categoryList = Apcategory.objects.using(self._current_app_schema()).filter(condition)

        list_length = len(categoryList)
        category_list_data = NWisefinList()
        if list_length > 0:
            for category in categoryList:
                cat_data = ApcategoryResponse()
                cat_data.set_id(category.id)
                cat_data.set_code(category.code)
                cat_data.set_name(category.name)
                cat_data.set_no(category.no)
                cat_data.set_expense(category.expense)
                category_list_data.append(cat_data)
        return category_list_data

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
        audit_obj.set_relreftype(MasterRefType.CATEGORY)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return

    def UpdateIsasset(self, Category_obj, emp_id):
        category_update = Apcategory.objects.using(self._current_app_schema()).filter(id=Category_obj.get_id(),
                                                                                      entity_id=self._entity_id()).update(
            isasset=Category_obj.get_isasset(),
            updated_by=emp_id, updated_date=timezone.now())
        category = Apcategory.objects.using(self._current_app_schema()).get(id=Category_obj.get_id())
        category_auditdata = {'id': Category_obj.get_id(),
                              'isasset': Category_obj.get_isasset(),
                              'updated_by': emp_id, 'updated_date': timezone.now()}
        self.audit_function(category_auditdata, emp_id, category.id, ModifyStatus.update)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    def UpdateStatus(self, category_id, status, emp_id):
        category = Apcategory.objects.using(self._current_app_schema()).filter(id=category_id,
                                                                               entity_id=self._entity_id()).update(
            status=status,
            updated_by=emp_id,
            updated_date=timezone.now())
        self.audit_function(category, emp_id, category_id, ModifyStatus.update)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    def categorySearch_list(self, vys_page, query):
        no = query.get('no')
        name = query.get('name')
        condition = Q(no__icontains=no) & Q(name__icontains=name) & Q(entity_id=self._entity_id())
        categoryList = Apcategory.objects.using(self._current_app_schema()).filter(condition)[
                       vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(categoryList)
        category_list_data = NWisefinList()
        if list_length > 0:
            for category in categoryList:
                cat_data = ApcategoryResponse()
                cat_data.set_id(category.id)
                cat_data.set_code(category.code)
                cat_data.set_no(category.no)
                cat_data.set_name(category.name)
                cat_data.set_glno(category.glno)
                cat_data.set_isasset(category.isasset)
                cat_data.set_status(category.status)
                category_list_data.append(cat_data)
            vpage = NWisefinPaginator(categoryList, vys_page.get_index(), 10)
            category_list_data.set_pagination(vpage)
        return category_list_data
    def categorySearch_list_mst(self, vys_page, request):
        status=request.GET.get('status',2)
        condition=Q() & Q(entity_id=self._entity_id())
        if status == '':
            status = 2
        if int(status)!=2:
            condition = Q(status=status) & Q(entity_id=self._entity_id())
        if 'no' in request.GET:
            condition&=Q(no__icontains=request.GET.get('no'))
        if 'name' in request.GET:
            condition&=Q(name__icontains=request.GET.get('name'))
        categoryList = Apcategory.objects.using(self._current_app_schema()).filter(condition)[
                       vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(categoryList)
        category_list_data = NWisefinList()
        if list_length > 0:
            for category in categoryList:
                cat_data = ApcategoryResponse()
                cat_data.set_id(category.id)
                cat_data.set_code(category.code)
                cat_data.set_no(category.no)
                cat_data.set_name(category.name)
                cat_data.set_glno(category.glno)
                cat_data.set_isasset(category.isasset)
                cat_data.set_status(category.status)
                category_list_data.append(cat_data)
            vpage = NWisefinPaginator(categoryList, vys_page.get_index(), 10)
            category_list_data.set_pagination(vpage)
        return category_list_data

    def fetch_prcategorylist(self, vys_page):
        try:
            categoryList = Apcategory.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id()).order_by('created_date')[vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(categoryList)
            category_list_data = NWisefinList()
            if list_length > 0:
                for category in categoryList:
                    cat_data = ApcategoryResponse()
                    cat_data.set_id(category.id)
                    cat_data.set_code(category.code)
                    cat_data.set_no(category.no)
                    cat_data.set_name(category.name)
                    cat_data.set_glno(category.glno)
                    cat_data.set_isasset(category.isasset)
                    cat_data.set_status(category.status)
                    category_list_data.append(cat_data)
                vpage = NWisefinPaginator(categoryList, vys_page.get_index(), 10)
                category_list_data.set_pagination(vpage)
            return category_list_data
        except:
            logger.error('ERROR_APCATEGORY_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_CATEGORY_ID)
            error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
            return error_obj

    def categorylistActive(self, vys_page):
        condition = Q(status=1) & Q(entity_id=self._entity_id())
        categoryList = Apcategory.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                       vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(categoryList)
        category_list_data = NWisefinList()
        if list_length > 0:
            for category in categoryList:
                cat_data = ApcategoryResponse()
                cat_data.set_id(category.id)
                cat_data.set_code(category.code)
                cat_data.set_no(category.no)
                cat_data.set_name(category.name)
                cat_data.set_glno(category.glno)
                cat_data.set_isasset(category.isasset)
                cat_data.set_status(category.status)
                category_list_data.append(cat_data)
            vpage = NWisefinPaginator(categoryList, vys_page.get_index(), 10)
            category_list_data.set_pagination(vpage)
        return category_list_data

    def categorylistInactive(self, vys_page):
        condition = Q(status=0) & Q(entity_id=self._entity_id())
        categoryList = Apcategory.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                       vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(categoryList)
        category_list_data = NWisefinList()
        if list_length > 0:
            for category in categoryList:
                cat_data = ApcategoryResponse()
                cat_data.set_id(category.id)
                cat_data.set_code(category.code)
                cat_data.set_no(category.no)
                cat_data.set_name(category.name)
                cat_data.set_glno(category.glno)
                cat_data.set_isasset(category.isasset)
                cat_data.set_status(category.status)
                category_list_data.append(cat_data)
            vpage = NWisefinPaginator(categoryList, vys_page.get_index(), 10)
            category_list_data.set_pagination(vpage)
        return category_list_data

    def search_categoryNo(self, Category_obj, vys_page):
        condition = None
        if 'no' in Category_obj:
            condition = Q(no__icontains=Category_obj['no']) & Q(entity_id=self._entity_id())

        if condition is not None:
            categoryList = Apcategory.objects.using(self._current_app_schema()).filter(condition)[
                           vys_page.get_offset():vys_page.get_query_limit()]
        else:
            categoryList = []
        list_length = len(categoryList)
        if list_length > 0:
            category_list_data = NWisefinList()
            for category in categoryList:
                cat_data = ApcategoryResponse()
                cat_data.set_id(category.id)
                cat_data.set_no(category.no)
                category_list_data.append(cat_data)
            vpage = NWisefinPaginator(categoryList, vys_page.get_index(), 10)
            category_list_data.set_pagination(vpage)
            return category_list_data

    def search_categoryName(self, Category_obj, vys_page):
        condition = None
        if 'name' in Category_obj:
            condition = Q(name__icontains=Category_obj['name']) & Q(entity_id=self._entity_id())

        categoryList = Apcategory.objects.using(self._current_app_schema()).filter(condition)[
                       vys_page.get_offset():vys_page.get_query_limit()]

        list_length = len(categoryList)
        if list_length > 0:
            category_list_data = NWisefinList()
            for category in categoryList:
                cat_data = ApcategoryResponse()
                cat_data.set_id(category.id)
                cat_data.set_name(category.name)
                category_list_data.append(cat_data)
            vpage = NWisefinPaginator(categoryList, vys_page.get_index(), 10)
            category_list_data.set_pagination(vpage)
            return category_list_data

    def categoryname_search(self, query, vys_page):
        if query is None:
            categoryList = Apcategory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())[
                           vys_page.get_offset():vys_page.get_query_limit()]
        else:
            condition = Q(status=1) & Q(entity_id=self._entity_id()) & (
                        Q(name__icontains=query) | Q(glno__icontains=query))
            categoryList = Apcategory.objects.using(self._current_app_schema()).filter(condition)[
                           vys_page.get_offset():vys_page.get_query_limit()]

        list_length = len(categoryList)
        category_list_data = NWisefinList()
        if list_length > 0:
            for category in categoryList:
                cat_data = ApcategoryResponse()
                cat_data.set_id(category.id)
                cat_data.set_name(category.name)
                cat_data.set_glno(category.glno)
                cat_data.set_code(category.code)
                cat_data.set_no(category.no)
                category_list_data.append(cat_data)
            vpage = NWisefinPaginator(categoryList, vys_page.get_index(), 10)
            category_list_data.set_pagination(vpage)
        return category_list_data

    def create_category_mtom(self, Category_obj, action, user_id):
        if not Category_obj.get_id() is None:
            try:
                product_update = Apcategory.objects.filter(code=Category_obj.get_code()).update(
                    status=Category_obj.get_status(),
                    updated_date=timezone.now(),
                    updated_by=user_id)
                category = Apcategory.objects.get(code=Category_obj.get_code())
                product_update_auditdata = {'id': category.id,
                                            'code': Category_obj.get_code(),
                                            'status': Category_obj.get_status(),
                                            'updated_date': timezone.now(),
                                            'updated_by': user_id}
                self.audit_function(product_update_auditdata, user_id, category.id, ModifyStatus.update)
                logger.error("Apcategory mtom updated " +str(Category_obj.get_code()))
            except Exception as excep:
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(str(excep))
                return error_obj

                # category_update = Apcategory.objects.using(self._current_app_schema()).filter(id=Category_obj.get_id(),
                #                                                                               entity_id=self._entity_id()).update(
                #     code=Category_obj.get_code(),
                #     no=Category_obj.get_no(), name=Category_obj.get_name(), glno=Category_obj.get_glno(),
                #     isasset=Category_obj.get_isasset(),
                #     updated_by=user_id, updated_date=timezone.now())
                #
                # logger.error("cat_json_obj update" + str(category_update))

                # category = Apcategory.objects.using(self._current_app_schema()).get(id=Category_obj.get_id(),
                #                                                                     entity_id=self._entity_id())
                # logger.error("cat_json_obj after update" + str(category))
                # category_auditdata = {'id': Category_obj.get_id(),
                #                       'code': Category_obj.get_code(),
                #                       'no': Category_obj.get_no(),
                #                       'name': Category_obj.get_name(), 'glno': Category_obj.get_glno(),
                #                       'isasset': Category_obj.get_isasset(),
                #                       'updated_by': user_id, 'updated_date': timezone.now()}
                # self.audit_function(category_auditdata, user_id, category.id, ModifyStatus.update)

            except IntegrityError as error:
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Apcategory.DoesNotExist:
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_District_ID)
                error_obj.set_description(ErrorDescription.INVALID_District_ID)
                return error_obj
            except:
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error("cat_json_obj insert" + str(Category_obj))
                category = Apcategory.objects.using(self._current_app_schema()).create(code=Category_obj.get_code(),
                                                                                       no=Category_obj.get_no(),
                                                                                       name=Category_obj.get_name(),
                                                                                       glno=Category_obj.get_glno(),
                                                                                       isasset=Category_obj.get_isasset(),
                                                                                       isodit=Category_obj.get_isodit(),
                                                                                       created_by=user_id,
                                                                                       entity_id=self._entity_id()
                                                                                       )
                logger.error("cat_json_obj after insert" + str(category))

                self.audit_function(category, user_id, category.id, ModifyStatus.create)

            except IntegrityError as error:
                traceback.print_exc()
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
        cat_data = ApcategoryResponse()
        cat_data.set_id(category.id)
        cat_data.set_code(category.code)
        cat_data.set_no(category.no)
        cat_data.set_name(category.name)
        cat_data.set_glno(category.glno)
        cat_data.set_expense_id(category.expense_id)
        cat_data.set_isasset(category.isasset)
        cat_data.set_isodit(category.isodit)
        return cat_data

    def category_income(self, query, vys_page):
        if query is None:
            condition = Q(status=1) & (Q(no__gte=900) & Q(no__lte=999)) & Q(entity_id=self._entity_id())
        else:
            condition = Q(entity_id=self._entity_id()) & Q(status=1) & (Q(no__gte=900) & Q(no__lte=999)) & (
                        Q(name__icontains=query) | Q(glno__icontains=query))
        categoryList = Apcategory.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                       vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(categoryList)
        category_list_data = NWisefinList()
        if list_length > 0:
            for category in categoryList:
                cat_data = ApcategoryResponse()
                cat_data.set_id(category.id)
                cat_data.set_code(category.code)
                cat_data.set_no(category.no)
                cat_data.set_name(category.name)
                cat_data.set_glno(category.glno)
                cat_data.set_expense(category.expense)
                cat_data.set_isasset(category.isasset)
                cat_data.set_status(category.status)
                category_list_data.append(cat_data)
            vpage = NWisefinPaginator(categoryList, vys_page.get_index(), 10)
            category_list_data.set_pagination(vpage)
        return category_list_data

    def fetch_apcategory1(self, query):
        query = query
        apcategory1 = Apcategory.objects.using(self._current_app_schema()).filter(code=query,
                                                                                  entity_id=self._entity_id())
        if len(apcategory1) != 0:
            apcategory = apcategory1[0]
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj
        apcategory_data = {"id": apcategory.id, "code": apcategory.code, "name": apcategory.name,"no":apcategory.no }
        apcategory_dic = json.dumps(apcategory_data, indent=4)
        return apcategory_data

    def fetch_apcategorylist(self, apcategory_ids):
        apcategory_id2 = apcategory_ids.get('apcat_id')
        obj = Apcategory.objects.using(self._current_app_schema()).filter(code__in=apcategory_id2,
                                                                          entity_id=self._entity_id()).values('id',
                                                                                                              'name',
                                                                                                              'code')
        apcategory_list_data = NWisefinList()
        for i in obj:
            data = {"id": i['id'], "name": i['name'], "code": i['code']}
            apcategory_list_data.append(data)
        return apcategory_list_data.get()

    def get_apsubcategory(self, id_obj):
        obj = APsubcategory.objects.using(self._current_app_schema()).filter(id__in=id_obj["subcategory_id"],
                                                                             entity_id=self._entity_id()).values('id',
                                                                                                                 'name',
                                                                                                                 'glno')
        arr = []
        for i in obj:
            data = {"id": i['id'], "name": i['name'], "gl": i['glno']}
            arr.append(data)
        vendor_dic = json.dumps(arr, indent=4)
        return vendor_dic

    def get_apsubcategory_data(self, id_obj):
        obj = APsubcategory.objects.using(self._current_app_schema()).filter(id__in=id_obj["subcategory_id"],
                                                                             entity_id=self._entity_id())
        arr = []
        for i in obj:
            arr.append(i)
        vendor_dic = json.dumps(arr, indent=4, default=dictdefault)
        return vendor_dic

    # apcategory_active_inactivate
    def apcategory_active_inactivate(self, request, apcat_obj, user_id):

        if (int(apcat_obj.status) == 0):
            apcat_data = Apcategory.objects.using(self._current_app_schema()).filter(id=apcat_obj.id).update(
                status=1)
        else:
            apcat_data = Apcategory.objects.using(self._current_app_schema()).filter(id=apcat_obj.id).update(
                status=0)
        apcat_var = Apcategory.objects.using(self._current_app_schema()).get(id=apcat_obj.id)
        data = ApcategoryResponse()
        data.set_status(apcat_var.status)
        status = apcat_var.status
        data.set_id(apcat_var.id)
        # return data
        if status == 1:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.ACTIVATED)

            return data
        if status == 0:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.INACTIVATED)
            return data
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_taxrate_ID)
            error_obj.set_description(ErrorDescription.INVALID_taxrate_ID)
            return error_obj

    def fetch_category_download(self, vys_page):
        categoryList = Apcategory.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id()).order_by('created_date')
        list_length = len(categoryList)
        category_list_data = NWisefinList()
        if list_length >= 0:
            for category in categoryList:
                cat_data = ApcategoryResponse()
                cat_data.set_id(category.id)
                cat_data.set_code(category.code)
                cat_data.set_no(category.no)
                cat_data.set_name(category.name)
                cat_data.set_glno(category.glno)
                cat_data.set_isasset(category.isasset)
                try:
                    cat_data.expense=category.expense.head
                except:
                    cat_data.expense = ""
                category_list_data.append(cat_data)
            return category_list_data