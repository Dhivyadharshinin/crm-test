import traceback

from django.db import IntegrityError


from masterservice.data.response.apsubcategoryresponse import ApsubcategoryResponse
from masterservice.service.Codegenerator import CodeGen
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from masterservice.data.request.masterauditrequest import MasterAuditRequest
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.util.masterutil import ModifyStatus, MasterRefType, RequestStatusUtil, Code_Gen_Type, Code_Gen_Value
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from masterservice.models import APsubcategory, Apcategory, APexpense, APexpensegroup
from django.utils import timezone
from django.db.models import Q
import json

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class SubcategoryService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_subcategory(self, Subcategory_obj, user_id):
        if not Subcategory_obj.get_id() is None:
            try:
                logger.error('APSUBCATEGORY: APsubcategory Update Started')
                apcategory = Apcategory.objects.get(id=Subcategory_obj.get_category_id())
                cat = apcategory.expense.exp_grp_id
                apexpgrp = APexpensegroup.objects.get(id=cat)
                subcategory_update = APsubcategory.objects.using(self._current_app_schema()).filter(
                    id=Subcategory_obj.get_id(), entity_id=self._entity_id()).update(
                    # code=Subcategory_obj.get_code(),
                    no=Subcategory_obj.get_no(),
                    name=Subcategory_obj.get_name(),
                    code=Subcategory_obj.get_name(),
                    category_id=Subcategory_obj.get_category_id(),
                    glno=Subcategory_obj.get_glno(),
                    expense_id=Subcategory_obj.get_expense_id(),
                    gstblocked=Subcategory_obj.get_gstblocked(),
                    gstrcm=Subcategory_obj.get_gstrcm(),
                    updated_by=user_id,
                    updated_date=timezone.now(),
                    subcat_expensegrp_alei=apexpgrp.expensegrp_alei)
                subcategory = APsubcategory.objects.using(self._current_app_schema()).get(id=Subcategory_obj.get_id(),
                                                                                          entity_id=self._entity_id())
                logger.error('APSUBCATEGORY: APsubcategory Update Success' + str(subcategory_update))
                subcategory_auditdata = {'id': Subcategory_obj.get_id(),
                                         # 'code':Subcategory_obj.get_code(),
                                         'no': Subcategory_obj.get_no(),
                                         'name': Subcategory_obj.get_name(),
                                         'category_id': Subcategory_obj.get_category_id(),
                                         'glno': Subcategory_obj.get_glno(),
                                         'expense_id': Subcategory_obj.get_expense_id(),
                                         'gstblocked': Subcategory_obj.get_gstblocked(),
                                         'gstrcm': Subcategory_obj.get_gstrcm(),
                                         'updated_by': user_id,
                                         'updated_date': timezone.now()}
                self.audit_function(subcategory_auditdata, user_id, subcategory.id, ModifyStatus.update)

            except IntegrityError as error:
                logger.error('ERROR_APsubcategory_Update_EXCEPT:{}'.format(traceback.print_exc()))
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except APsubcategory.DoesNotExist:
                logger.error('ERROR_APsubcategory_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_APsubcategory_ID)
                error_obj.set_description(ErrorDescription.INVALID_APsubcategory_ID)
                return error_obj
            except:
                logger.error('ERROR_APsubcategory_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            condition = Q(name__exact=Subcategory_obj.get_name()) & Q(entity_id=self._entity_id())
            subcategory = APsubcategory.objects.using(self._current_app_schema()).filter(condition)
            if len(subcategory) > 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                return error_obj
            try:
                logger.error('APSUBCATEGORY: APsubcategory Creation Started')
                apcategory = Apcategory.objects.get(id=Subcategory_obj.get_category_id())
                cat = apcategory.expense.exp_grp_id
                apexpgrp = APexpensegroup.objects.get(id=cat)
                subcategory = APsubcategory.objects.using(self._current_app_schema()).create(
                    # code=Subcategory_obj.get_code(),
                    no=Subcategory_obj.get_no(),
                    name=Subcategory_obj.get_name(),
                    code=Subcategory_obj.get_name(),
                    category_id=Subcategory_obj.get_category_id(),
                    glno=Subcategory_obj.get_glno(),
                    # expense_id=Subcategory_obj.get_expense_id(),
                    gstblocked=Subcategory_obj.get_gstblocked(),
                    gstrcm=Subcategory_obj.get_gstrcm(),
                    assetcode=Subcategory_obj.get_code(),
                    created_by=user_id, entity_id=self._entity_id(),
                    subcat_expensegrp_alei=apexpgrp.expensegrp_alei
                )

                # code = APsubcategory.objects.using(self._current_app_schema()).get(code=Subcategory_obj.get_name())
                # subcategory.code = code
                # subcategory.save()
                self.audit_function(subcategory, user_id, subcategory.id, ModifyStatus.create)
                logger.error('APSUBCATEGORY: APsubcategory Creation Success' + str(subcategory))

            except IntegrityError as error:
                logger.error('ERROR_APsubcategory_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_APsubcategory_Create_EXCEPT:{}'.format(traceback.print_exc()))
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        cat_data = ApsubcategoryResponse()
        cat_data.set_id(subcategory.id)
        cat_data.set_code(subcategory.code)
        cat_data.set_no(subcategory.no)
        cat_data.set_name(subcategory.name)
        cat_data.set_category_id(subcategory.category_id)
        # cat_data.set_expense_id(subcategory.expense_id)
        cat_data.set_gstblocked(subcategory.gstblocked)
        cat_data.set_gstrcm(subcategory.gstrcm)
        cat_data.set_glno(subcategory.glno)

        data = NWisefinSuccess()
        data.set_status(SuccessStatus.SUCCESS)
        data.set_message(SuccessMessage.CREATE_MESSAGE)
        return data
    def fetch_subcategory_list_dep(self):
        subcategoryList = APsubcategory.objects.using(self._current_app_schema()).all().values('glno', 'id', 'no', 'category')
        list_length = len(subcategoryList)
        subcategory_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for subcategory in subcategoryList:
               subcategory_list_data.append(subcategory)
        return subcategory_list_data


    def fetchsubcategory(self, subcategory_id):
        try:
            subcategory = APsubcategory.objects.using(self._current_app_schema()).get(id=subcategory_id,
                                                                                      entity_id=self._entity_id())
            cat_data = ApsubcategoryResponse()
            cat_data.set_id(subcategory.id)
            cat_data.set_code(subcategory.code)
            cat_data.set_assetcode(subcategory.assetcode)
            cat_data.set_no(subcategory.no)
            cat_data.set_name(subcategory.name)
            cat_data.set_category(subcategory.category)
            # cat_data.set_expense(subcategory.expense)
            cat_data.set_gstblocked(subcategory.gstblocked)
            cat_data.set_gstrcm(subcategory.gstrcm)
            cat_data.set_glno(subcategory.glno)
            cat_data.set_assetcode(subcategory.assetcode)
            return cat_data
        except APsubcategory.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_category_ID)
            error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
            return error_obj

    def fetch_subcategory_list(self, vys_page):
        subcategoryList = APsubcategory.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id()).order_by('created_date')[
                          vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(subcategoryList)
        subcategory_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for subcategory in subcategoryList:
                cat_data = ApsubcategoryResponse()
                cat_data.set_id(subcategory.id)
                cat_data.set_code(subcategory.code)
                cat_data.set_no(subcategory.no)
                cat_data.set_name(subcategory.name)
                cat_data.set_category(subcategory.category)
                # cat_data.set_expense(subcategory.expense)
                cat_data.set_gstblocked(subcategory.gstblocked)
                cat_data.set_gstrcm(subcategory.gstrcm)
                cat_data.set_glno(subcategory.glno)
                subcategory_list_data.append(cat_data)
                vpage = NWisefinPaginator(subcategoryList, vys_page.get_index(), 10)
                subcategory_list_data.set_pagination(vpage)
        return subcategory_list_data

    def delete_subcategory(self, subcategory_id, user_id):
        subcategory = APsubcategory.objects.using(self._current_app_schema()).filter(id=subcategory_id,
                                                                                     entity_id=self._entity_id()).delete()
        self.audit_function(subcategory, user_id, subcategory_id, ModifyStatus.delete)

        if subcategory[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_CATEGORY_ID)
            error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
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
        audit_obj.set_relreftype(MasterRefType.SUBCATEGORY)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return

    def fetch_subcategory_search(self, query, category_id):
        if query is None:
            category_id = int(category_id)
            subcategoryList = APsubcategory.objects.using(self._current_app_schema()).filter(category_id=category_id,
                                                                                             entity_id=self._entity_id())
        else:
            condition = Q(category_id=category_id) & Q(name__icontains=query) & Q(entity_id=self._entity_id())
            subcategoryList = APsubcategory.objects.using(self._current_app_schema()).filter(condition)
        subcategory_list_data = NWisefinList()
        for subcategory in subcategoryList:
            cat_data = ApsubcategoryResponse()
            cat_data.set_id(subcategory.id)
            cat_data.set_code(subcategory.code)
            cat_data.set_name(subcategory.name)

            cat_data.set_glno(subcategory.glno)
            subcategory_list_data.append(cat_data)
        return subcategory_list_data

    def edit_subcategory(self, Subcategory_obj, user_id):
        subcategory_update = APsubcategory.objects.using(self._current_app_schema()).filter(id=Subcategory_obj.get_id(),
                                                                                            entity_id=self._entity_id()).update(
            gstblocked=Subcategory_obj.get_gstblocked(),
            gstrcm=Subcategory_obj.get_gstrcm(),
            status=Subcategory_obj.get_status(),
            updated_by=user_id,
            updated_date=timezone.now())
        subcategory = APsubcategory.objects.using(self._current_app_schema()).get(id=Subcategory_obj.get_id(),
                                                                                  entity_id=self._entity_id())
        subcategory_auditdata = {'id': Subcategory_obj.get_id(),
                                 'gstblocked': Subcategory_obj.get_gstblocked(),
                                 'gstrcm': Subcategory_obj.get_gstrcm(),
                                 'updated_by': user_id,
                                 'updated_date': timezone.now()}
        self.audit_function(subcategory_auditdata, user_id, subcategory.id, ModifyStatus.update)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    def UpdateStatus(self, subcategory_id, status, user_id):
        subcategory_update = APsubcategory.objects.using(self._current_app_schema()).filter(id=subcategory_id,
                                                                                            entity_id=self._entity_id()).update(
            status=status,
            updated_by=user_id,
            updated_date=timezone.now())
        self.audit_function(subcategory_update, user_id, subcategory_id, ModifyStatus.update)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    def fetch_subcategorylist(self, vys_page):
        try:
            subcategoryList = APsubcategory.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id()).order_by('created_date')[
                              vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(subcategoryList)
            subcategory_list_data = NWisefinList()
            for subcategory in subcategoryList:
                cat_data = ApsubcategoryResponse()
                cat_data.set_id(subcategory.id)
                cat_data.set_code(subcategory.code)
                cat_data.set_no(subcategory.no)
                cat_data.set_name(subcategory.name)
                cat_data.set_category(subcategory.category)
                # cat_data.set_expense(subcategory.expense)
                cat_data.set_gstblocked(subcategory.gstblocked)
                cat_data.set_gstrcm(subcategory.gstrcm)
                cat_data.set_glno(subcategory.glno)
                cat_data.set_status(subcategory.status)
                subcategory_list_data.append(cat_data)
                vpage = NWisefinPaginator(subcategoryList, vys_page.get_index(), 10)
                subcategory_list_data.set_pagination(vpage)
            return subcategory_list_data
        except:
            logger.error('ERROR_APsubcategory_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_APsubcategory_ID)
            error_obj.set_description(ErrorDescription.INVALID_APsubcategory_ID)
            return error_obj

    def subcategorylistactive(self, vys_page):
        condition = Q(status=1) & Q(entity_id=self._entity_id())
        subcategoryList = APsubcategory.objects.using(self._current_app_schema()).filter(condition).order_by(
            'created_date')[
                          vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(subcategoryList)
        subcategory_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for subcategory in subcategoryList:
                cat_data = ApsubcategoryResponse()
                cat_data.set_id(subcategory.id)
                cat_data.set_code(subcategory.code)
                cat_data.set_no(subcategory.no)
                cat_data.set_name(subcategory.name)
                cat_data.set_category(subcategory.category)
                # cat_data.set_expense(subcategory.expense)
                cat_data.set_gstblocked(subcategory.gstblocked)
                cat_data.set_gstrcm(subcategory.gstrcm)
                cat_data.set_glno(subcategory.glno)
                cat_data.set_status(subcategory.status)
                subcategory_list_data.append(cat_data)
                vpage = NWisefinPaginator(subcategoryList, vys_page.get_index(), 10)
                subcategory_list_data.set_pagination(vpage)
        return subcategory_list_data

    def subcategorylistInactive(self, vys_page):
        condition = Q(status=0) & Q(entity_id=self._entity_id())
        subcategoryList = APsubcategory.objects.using(self._current_app_schema()).filter(condition).order_by(
            'created_date')[
                          vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(subcategoryList)
        subcategory_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for subcategory in subcategoryList:
                cat_data = ApsubcategoryResponse()
                cat_data.set_id(subcategory.id)
                cat_data.set_code(subcategory.code)
                cat_data.set_no(subcategory.no)
                cat_data.set_name(subcategory.name)
                cat_data.set_category(subcategory.category)
                #cat_data.set_expense(subcategory.expense)
                cat_data.set_gstblocked(subcategory.gstblocked)
                cat_data.set_gstrcm(subcategory.gstrcm)
                cat_data.set_glno(subcategory.glno)
                cat_data.set_status(subcategory.status)
                subcategory_list_data.append(cat_data)
                vpage = NWisefinPaginator(subcategoryList, vys_page.get_index(), 10)
                subcategory_list_data.set_pagination(vpage)
            return subcategory_list_data


    def fetch_subcat_search(self, query, category_id):
        condition = Q(status=1) & Q(entity_id=self._entity_id())
        if query is not None:
            condition &= Q(name__icontains=query)
        if category_id is not None:
            condition &= Q(category_id=category_id)

        subcategoryList = APsubcategory.objects.using(self._current_app_schema()).filter(condition)
        subcategory_list_data = NWisefinList()

        if len(subcategoryList) > 0:
            for subcategory in subcategoryList:
                cat_data = ApsubcategoryResponse()
                cat_data.set_id(subcategory.id)
                cat_data.set_code(subcategory.code)
                cat_data.set_no(subcategory.no)
                cat_data.set_name(subcategory.name)
                cat_data.set_category(subcategory.category)
                #cat_data.set_expense(subcategory.expense)
                cat_data.set_gstblocked(subcategory.gstblocked)
                cat_data.set_gstrcm(subcategory.gstrcm)
                cat_data.set_glno(subcategory.glno)
                cat_data.set_status(subcategory.status)
                subcategory_list_data.append(cat_data)
        return subcategory_list_data

    def search_subcategory(self, vys_page, subcategory_obj, user_id):
        condition =  Q(entity_id=self._entity_id())
        if 'category_id' in subcategory_obj:
            condition &= Q(category_id=subcategory_obj['category_id'])
        if 'no' in subcategory_obj:
            condition &= Q(no__icontains=subcategory_obj['no'])
        if 'name' in subcategory_obj:
            condition &= Q(name__icontains=subcategory_obj['name'])
        if 'glno' in subcategory_obj:
            condition &= Q(glno__icontains=subcategory_obj['glno'])
        subcategoryList = APsubcategory.objects.using(self._current_app_schema()).filter(condition)[
                          vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(subcategoryList)
        subcategory_list_data = NWisefinList()
        if list_length > 0:
            for subcategory in subcategoryList:
                cat_data = ApsubcategoryResponse()
                cat_data.set_id(subcategory.id)
                cat_data.set_code(subcategory.code)
                cat_data.set_no(subcategory.no)
                cat_data.set_name(subcategory.name)
                cat_data.set_category(subcategory.category)
                cat_data.set_status(subcategory.status)
                #cat_data.set_expense(subcategory.expense)
                cat_data.set_gstblocked(subcategory.gstblocked)
                cat_data.set_gstrcm(subcategory.gstrcm)
                cat_data.set_glno(subcategory.glno)
                subcategory_list_data.append(cat_data)
            vpage = NWisefinPaginator(subcategoryList, vys_page.get_index(), 10)
            subcategory_list_data.set_pagination(vpage)
        return subcategory_list_data

    def search_subcategory_mst(self, vys_page, request, user_id):
        status = request.GET.get('status', 2)
        if status=='':
            status=2
        condition = Q() & Q(entity_id=self._entity_id())
        if int(status) != 2:
            condition = Q(status=status) & Q(entity_id=self._entity_id())
        if 'no' in request.GET:
            condition &= Q(no__icontains=request.GET.get('no'))
        if 'name' in request.GET:
            condition &= Q(name__icontains=request.GET.get('name'))
        if 'glno' in request.GET:
            condition &= Q(glno__icontains=request.GET.get('glno'))
        # condition =  Q(entity_id=self._entity_id())
        # if 'category_id' in subcategory_obj:
        #     condition &= Q(category_id=subcategory_obj['category_id'])
        # if 'no' in subcategory_obj:
        #     condition &= Q(no__icontains=subcategory_obj['no'])
        # if 'name' in subcategory_obj:
        #     condition &= Q(name__icontains=subcategory_obj['name'])
        # if 'glno' in subcategory_obj:
        #     condition &= Q(glno__icontains=subcategory_obj['glno'])
        subcategoryList = APsubcategory.objects.using(self._current_app_schema()).filter(condition)[
                          vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(subcategoryList)
        subcategory_list_data = NWisefinList()
        if list_length > 0:
            for subcategory in subcategoryList:
                cat_data = ApsubcategoryResponse()
                cat_data.set_id(subcategory.id)
                cat_data.set_code(subcategory.code)
                cat_data.set_no(subcategory.no)
                cat_data.set_name(subcategory.name)
                cat_data.set_category(subcategory.category)
                cat_data.set_status(subcategory.status)
                #cat_data.set_expense(subcategory.expense)
                cat_data.set_gstblocked(subcategory.gstblocked)
                cat_data.set_gstrcm(subcategory.gstrcm)
                cat_data.set_glno(subcategory.glno)
                subcategory_list_data.append(cat_data)
            vpage = NWisefinPaginator(subcategoryList, vys_page.get_index(), 10)
            subcategory_list_data.set_pagination(vpage)
        return subcategory_list_data

    def create_subcategory_mtom(self, Subcategory_obj,action, user_id):

        if action == 'active' or action == 'inactive':
            try:
                subcategory_update = APsubcategory.objects.using(self._current_app_schema()).filter(code=Subcategory_obj.get_code(),
                                                           category__code=Subcategory_obj.get_category_code()).update(
                    status=Subcategory_obj.get_status(),
                    updated_date=timezone.now(),
                    updated_by=user_id)
                subcategory = APsubcategory.objects.using(self._current_app_schema()).get(code=Subcategory_obj.get_code(),category__code=Subcategory_obj.get_category_code())
                product_update_auditdata = {'id': subcategory.id,
                                            'code': Subcategory_obj.get_code(),
                                            'status': Subcategory_obj.get_status(),
                                            'updated_date': timezone.now(),
                                            'updated_by': user_id}
                self.audit_function(product_update_auditdata, user_id, subcategory.id, ModifyStatus.update)
                logger.error("Subcategory_obj mtom updated " +str(Subcategory_obj.get_code()))
            except Exception as excep:
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(str(excep))
                return error_obj



        if action=='update':
            try:
                category_id = Apcategory.objects.using(self._current_app_schema()).get(code=Subcategory_obj.get_category_code()).id
                expense_id = APexpense.objects.get(code=Subcategory_obj.get_expense_code()).id
                logger.error("category_id " + str(category_id))
                #logger.error("expense_id " + str(expense_id))
                subcategory_update = APsubcategory.objects.using(self._current_app_schema()).filter(code=Subcategory_obj.get_code(),
                                                      category__code=Subcategory_obj.get_category_code()).update(code=Subcategory_obj.get_code(),
                                                                                 no=Subcategory_obj.get_no(),
                                                                                 #status=Subcategory_obj.get_status(),
                                                                                 name=Subcategory_obj.get_name(),
                                                                                 category_id=category_id,
                                                                                 glno=Subcategory_obj.get_glno(),
                                                                                 #expense_id=expense_id,
                                                                                 gstblocked=Subcategory_obj.get_gstblocked(),
                                                                                 gstrcm=Subcategory_obj.get_gstrcm(),
                                                                                 updated_by=user_id,
                                                                                 updated_date=timezone.now())
                subcategory = APsubcategory.objects.using(self._current_app_schema()).get(code=Subcategory_obj.get_code(),
                                                        category__code=Subcategory_obj.get_category_code())
                subcategory_auditdata = {'id':subcategory.id,
                                                                                 'code':Subcategory_obj.get_code(),
                                                                                 'no':Subcategory_obj.get_no(),
                                                                                 'name':Subcategory_obj.get_name(),
                                                                                 'category_id':category_id,
                                                                                 'glno':Subcategory_obj.get_glno(),
                                                                                 #'expense_id':expense_id,
                                                                                 'gstblocked':Subcategory_obj.get_gstblocked(),
                                                                                 'gstrcm':Subcategory_obj.get_gstrcm(),
                                                                                 'updated_by':user_id,
                                                                                 'updated_date':timezone.now()}
                self.audit_function(subcategory_auditdata, user_id, subcategory.id, ModifyStatus.update)

            except IntegrityError as error:
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except APsubcategory.DoesNotExist:
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
            category_id = Apcategory.objects.using(self._current_app_schema()).get(
                code=Subcategory_obj.get_category_code()).id
            # expense_id = APexpense.objects.get(code=Subcategory_obj.get_expense_code()).id

            condition = Q(name__exact=Subcategory_obj.get_name()) & Q(entity_id=self._entity_id())
            subcategory = APsubcategory.objects.using(self._current_app_schema()).filter(condition)
            logger.error("subcategory " + str(subcategory))
            if len(subcategory) > 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                return error_obj
            try:
                subcategory = APsubcategory.objects.using(self._current_app_schema()).create(
                    code=Subcategory_obj.get_code(),
                    no=Subcategory_obj.get_no(),
                    name=Subcategory_obj.get_name(),
                    category_id=category_id,
                    glno=Subcategory_obj.get_glno(),
                    # expense_id=category_id.expense.id,
                    gstblocked=Subcategory_obj.get_gstblocked(),
                    gstrcm=Subcategory_obj.get_gstrcm(),
                    assetcode=Subcategory_obj.get_assetcode(),
                    created_by=user_id, entity_id=self._entity_id()
                    )
                logger.error("Ap subcategory after insert " + str(subcategory))


                self.audit_function(subcategory, user_id, subcategory.id, ModifyStatus.create)

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
        cat_data = ApsubcategoryResponse()
        cat_data.set_id(subcategory.id)
        cat_data.set_code(subcategory.code)
        cat_data.set_no(subcategory.no)
        cat_data.set_name(subcategory.name)
        cat_data.set_category_id(subcategory.category_id)
        cat_data.set_expense_id(category_id.expense.id)
        cat_data.set_gstblocked(subcategory.gstblocked)
        cat_data.set_gstrcm(subcategory.gstrcm)
        cat_data.set_glno(subcategory.glno)

        return cat_data

    def search_incDebit(self, query, vys_page):
        condition = Q(entity_id=self._entity_id())
        if query is None:
            condition &= Q(status=1) & Q(category_id__no__exact=501)
        else:
            condition &= Q(status=1) & (Q(name__icontains=query) | Q(glno__icontains=query)) & Q(
                category_id__no__exact=501)
        subcategoryList = APsubcategory.objects.using(self._current_app_schema()).filter(condition)[
                          vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(subcategoryList)
        subcategory_list_data = NWisefinList()
        if list_length > 0:
            for subcategory in subcategoryList:
                cat_data = ApsubcategoryResponse()
                cat_data.set_id(subcategory.id)
                cat_data.set_code(subcategory.code)
                cat_data.set_no(subcategory.no)
                cat_data.set_name(subcategory.name)
                cat_data.set_category(subcategory.category)
                cat_data.set_glno(subcategory.glno)
                subcategory_list_data.append(cat_data)
            vpage = NWisefinPaginator(subcategoryList, vys_page.get_index(), 10)
            subcategory_list_data.set_pagination(vpage)
        return subcategory_list_data

    def subcatname_search(self, query, category_id, vys_page):
        category_id = int(category_id)
        if query is None:
            subcategoryList = APsubcategory.objects.using(self._current_app_schema()).filter(category_id=category_id,
                                                                                             entity_id=self._entity_id())[
                              vys_page.get_offset(): vys_page.get_query_limit()]
        else:
            condition = Q(status=1) & (Q(name__icontains=query) | Q(glno__icontains=query)) & Q(
                category_id=category_id) & Q(entity_id=self._entity_id())
            subcategoryList = APsubcategory.objects.using(self._current_app_schema()).filter(condition)[
                              vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(subcategoryList)
        subcategory_list_data = NWisefinList()
        if list_length > 0:
            for subcategory in subcategoryList:
                cat_data = ApsubcategoryResponse()
                cat_data.set_id(subcategory.id)
                cat_data.set_code(subcategory.code)
                cat_data.set_no(subcategory.no)
                cat_data.set_name(subcategory.name)
                cat_data.set_category(subcategory.category)
                cat_data.set_glno(subcategory.glno)
                subcategory_list_data.append(cat_data)
            vpage = NWisefinPaginator(subcategoryList, vys_page.get_index(), 10)
            subcategory_list_data.set_pagination(vpage)
        return subcategory_list_data

    def search_incCredit(self, query, category_id, vys_page):
        category_id = int(category_id)
        condition = Q(entity_id=self._entity_id())
        if query is None:
            condition &= Q(status=1) & Q(category_id=category_id)

        else:
            condition &= Q(status=1) & (Q(name__icontains=query) | Q(glno__icontains=query)) & Q(
                category_id=category_id)
        subcategoryList = APsubcategory.objects.using(self._current_app_schema()).filter(condition)[
                          vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(subcategoryList)
        subcategory_list_data = NWisefinList()
        if list_length > 0:
            for subcategory in subcategoryList:
                cat_data = ApsubcategoryResponse()
                cat_data.set_id(subcategory.id)
                cat_data.set_code(subcategory.code)
                cat_data.set_no(subcategory.no)
                cat_data.set_name(subcategory.name)
                cat_data.set_category(subcategory.category)
                cat_data.set_glno(subcategory.glno)
                subcategory_list_data.append(cat_data)
            vpage = NWisefinPaginator(subcategoryList, vys_page.get_index(), 10)
            subcategory_list_data.set_pagination(vpage)
        return subcategory_list_data

    def fetch_apsubcategory(self, query):
        query = query
        apsubcategory1 = APsubcategory.objects.using(self._current_app_schema()).filter(code=query,
                                                                                        entity_id=self._entity_id())
        if len(apsubcategory1) != 0:
            apsubcategory = apsubcategory1[0]
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj
        apsubcategory_data = {"id": apsubcategory.id, "code": apsubcategory.code, "name": apsubcategory.name}
        apcsubategory_dic = json.dumps(apsubcategory_data, indent=4)
        return apsubcategory_data

    def fetch_apsubcategory_code(self, query):
        query = query
        apsubcategory1 = APsubcategory.objects.using(self._current_app_schema()).filter(code=query,
                                                                                        entity_id=self._entity_id())
        if len(apsubcategory1) != 0:
            apsubcategory = apsubcategory1[0]
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj
        apsubcategory_data = {"id": apsubcategory.id, "code": apsubcategory.code, "name": apsubcategory.name,
                              'gl': apsubcategory.glno}
        apcsubategory_dic = json.dumps(apsubcategory_data, indent=4)
        return apsubcategory_data

    def fetch_apsubcategorylist(request, apsubcategory_ids):
        apsubcategory_id2 = apsubcategory_ids.get('apsubcat_id')
        obj = APsubcategory.objects.using(request._current_app_schema()).filter(code__in=apsubcategory_id2,
                                                                                entity_id=request._entity_id()).values(
            'id', 'name', 'code')
        apsubcategory_list_data = NWisefinList()
        for i in obj:
            data = {"id": i['id'], "name": i['name'], "code": i['code']}
            apsubcategory_list_data.append(data)
        return apsubcategory_list_data.get()

    def apsubcategory_active_inactivate(self, request, apsubcat_obj, user_id):

        if (int(apsubcat_obj.status) == 0):

            apsubcate_data = APsubcategory.objects.using(self._current_app_schema()).filter(id=apsubcat_obj.id).update(
                status=1)
        else:
            apsubcate_data = APsubcategory.objects.using(self._current_app_schema()).filter(id=apsubcat_obj.id).update(
                status=0)
        apsubcat_var = APsubcategory.objects.using(self._current_app_schema()).get(id=apsubcat_obj.id)
        data = ApsubcategoryResponse()
        data.set_status(apsubcat_var.status)
        status = apsubcat_var.status
        data.set_id(apsubcat_var.id)
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

    def get_apcategory(self, id_obj):
        obj = Apcategory.objects.using(self._current_app_schema()).filter(id__in=id_obj["category_id"],
                                                                          entity_id=self._entity_id()).values('id',
                                                                                                              'name',
                                                                                                              'isasset',
                                                                                                              'no')
        arr = []
        for i in obj:
            data = {"id": i['id'], "no": i['no'],
                    "name": i['name'], "isasset": i['isasset']}
            arr.append(data)
        vendor_dic = json.dumps(arr, indent=4)
        return vendor_dic

    def fetch_apcategorydata(self, category_id):
        obj = Apcategory.objects.using(self._current_app_schema()).get(id=category_id, entity_id=self._entity_id())
        emp_data = {"id": obj.id,
                    "code": obj.code,
                    "name": obj.name,
                    "isasset": obj.isasset,
                    "no": obj.no}
        employee_dic = json.dumps(emp_data, indent=4)
        return employee_dic

    def fetch_subcat_name(self, query, vys_page):
        condition = Q(status=1) & Q(entity_id=self._entity_id())
        if query is not None:
            condition &= Q(name__icontains=query)

        subcategoryList = APsubcategory.objects.using(self._current_app_schema()).filter(condition)[
                          vys_page.get_offset(): vys_page.get_query_limit()]
        subcategory_list_data = NWisefinList()

        if len(subcategoryList) > 0:
            for subcategory in subcategoryList:
                cat_data = ApsubcategoryResponse()
                cat_data.set_id(subcategory.id)
                cat_data.set_code(subcategory.code)
                cat_data.set_no(subcategory.no)
                cat_data.set_name(subcategory.name)
                cat_data.set_category(subcategory.category)
                # cat_data.set_expense(subcategory.expense)
                cat_data.set_gstblocked(subcategory.gstblocked)
                cat_data.set_gstrcm(subcategory.gstrcm)
                cat_data.set_glno(subcategory.glno)
                cat_data.set_status(subcategory.status)
                subcategory_list_data.append(cat_data)
        return subcategory_list_data



    def get_apsubcategory_code(self,category_code, subcat_code):
        try:
            print('category_code --> ',category_code, ' subcat_code --> ', subcat_code)
            apcat = Apcategory.objects.using(self._current_app_schema()).filter(code=category_code,
                                                                              entity_id=self._entity_id())

            apsubcat = APsubcategory.objects.using(self._current_app_schema()).filter(code=subcat_code,category_id=apcat[0].id,
                                                                                      entity_id=self._entity_id())

            if len(apsubcat) != 0:
                apsubcategory = apsubcat[0]
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
            apsubcategory_data = {"id": apsubcategory.id, "code": apsubcategory.code, "name": apsubcategory.name,
                                  "no":apsubcategory.no,"glno":apsubcategory.glno}
            #apcsubategory_dic = json.dumps(apsubcategory_data, indeent=4)
            return apsubcategory_data
        except Exception  as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

    def fetch_subcat_glno_list(self, glno, vys_page):
        gl_list = []
        condition = Q(status=1)
        if 'glno' is not None:
            condition &= Q(glno=glno)
        subcategoryList = APsubcategory.objects.using(self._current_app_schema()).filter(condition)[
                          vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(subcategoryList)
        subcategory_list_data = NWisefinList()
        if list_length <= 0:
            return subcategory_list_data
        else:
            for subcategory in subcategoryList:
                cat_data = ApsubcategoryResponse()
                cat_data.subcat_id = subcategory.id
                cat_data.subcat_code = subcategory.code
                cat_data.subcat_no = subcategory.no
                cat_data.subcat_name = subcategory.name
                cat_data.apcat_id = subcategory.category.id
                cat_data.apcat_code = subcategory.category.code
                cat_data.apcat_no = subcategory.category.no
                cat_data.apcat_name = subcategory.category.name
                cat_data.set_glno(subcategory.glno)
                subcategory_list_data.append(cat_data)
                vpage = NWisefinPaginator(subcategoryList, vys_page.get_index(), 10)
                subcategory_list_data.set_pagination(vpage)
            return subcategory_list_data

    def get_subcategory_download(self, vys_page):
        subcategoryList = APsubcategory.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id()).order_by('created_date')
        list_length = len(subcategoryList)
        subcategory_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for subcategory in subcategoryList:
                cat_data = ApsubcategoryResponse()
                cat_data.set_id(subcategory.id)
                cat_data.set_code(subcategory.code)
                cat_data.set_no(subcategory.no)
                cat_data.set_name(subcategory.name)
                try:
                    cat_data.set_category=subcategory.category.name
                except:
                    cat_data.set_category=""
                # cat_data.set_expense(subcategory.expense)
                cat_data.set_gstblocked(subcategory.gstblocked)
                cat_data.set_gstrcm(subcategory.gstrcm)
                cat_data.set_glno(subcategory.glno)
                subcategory_list_data.append(cat_data)
        return subcategory_list_data