import traceback
from django.db import IntegrityError
from masterservice.models import SubTax, Tax
from nwisefin.settings import logger
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from vendorservice.data.response.subtaxresponse import SubTaxResponse
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from masterservice.data.request.masterauditrequest import MasterAuditRequest
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.util.masterutil import ModifyStatus,MasterRefType,RequestStatusUtil
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from django.db.models import Q


class SubTaxService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_subtax(self, subtax_obj, user_id):
        if not subtax_obj.get_id() is None:
            try:
                logger.error('SUBTAX: SubTax Update Started')
                subtax_update = SubTax.objects.using(self._current_app_schema()).filter(id=subtax_obj.get_id(),
                                                                                        entity_id=self._entity_id()).update(
                    tax_id=subtax_obj.get_tax_id(), name=subtax_obj.get_name(),
                    subtaxamount=subtax_obj.get_subtaxamount(),
                    remarks=subtax_obj.get_remarks(),category_id=subtax_obj.get_category_id(),
                    subcategory_id=subtax_obj.get_subcategory_id(),
                    glno =subtax_obj.get_glno (),
                updated_by=user_id,updated_date=timezone.now())

                subtax = SubTax.objects.using(self._current_app_schema()).get(id=subtax_obj.get_id(),
                                                                              entity_id=self._entity_id())
                logger.error('SUBTAX: SubTax Update Success' + str(subtax_update))
                subtax_auditdata = {'id': subtax_obj.get_id(),
                                   #'code': subtax_obj.get_code(),
                                   'name': subtax_obj.get_name(),
                                   'tax_id': subtax_obj.get_tax_id(),
                                   'remarks': subtax_obj.get_remarks(), 'glno': subtax_obj.get_glno(),
                                   'updated_date': timezone.now(),
                                   'updated_by': user_id}
                self.audit_function(subtax_auditdata, user_id, subtax.id, ModifyStatus.update)

            except IntegrityError as error:
                logger.error('ERROR_SubTax_Update_EXCEPT:{}'.format(traceback.print_exc()))
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except SubTax.DoesNotExist:
                logger.error('ERROR_SubTax_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_subtax_ID)
                error_obj.set_description(ErrorDescription.INVALID_subtax_ID)
                return error_obj
            except:
                logger.error('ERROR_SubTax_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('SUBTAX: SubTax Creation Started')
                subtax = SubTax.objects.using(self._current_app_schema()).create(#code =subtax_obj.get_code (),,
                tax_id =subtax_obj.get_tax_id (),name  =subtax_obj.get_name  (),subtaxamount=subtax_obj.get_subtaxamount(),
                remarks =subtax_obj.get_remarks (),category_id=subtax_obj.get_category_id(),subcategory_id=subtax_obj.get_subcategory_id(),
                    glno =subtax_obj.get_glno (),
                created_by =user_id, entity_id=self._entity_id())

                # code = "ISCT" + str(subtax.id)
                try:
                    max_cat_code = SubTax.objects.using(self._current_app_schema()).filter(code__icontains='ST').order_by('-code')[0].code
                    rnsl = int(max_cat_code[2:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "ST" + str(new_rnsl).zfill(3)
                subtax.code = code
                subtax.save()
                self.audit_function(subtax, user_id, subtax.id, ModifyStatus.create)
                logger.error('SUBTAX: SubTax Creation Success' + str(subtax))
            #
            except IntegrityError as error:
                logger.error('ERROR_SubTax_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_SubTax_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        subtax_data = SubTaxResponse()
        subtax_data.set_id(subtax.id)
        subtax_data.set_code (subtax.code)
        subtax_data.set_name(subtax.name)
        subtax_data.set_subtaxamount(subtax.subtaxamount)
        subtax_data.set_tax_id(subtax.tax_id)
        subtax_data.set_remarks (subtax.remarks)
        subtax_data.set_category_id(subtax.category_id)
        subtax_data.set_subcategory_id(subtax.subcategory_id)
        subtax_data.set_glno(subtax.glno)
        # return subtax_data
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    def fetch_subtax_list(self, vys_page):
        try:
            subtaxlist = SubTax.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by(
                'created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(subtaxlist)
            if list_length >= 0:
                subtax_list_data = NWisefinList()
                for subtax in subtaxlist:
                    subtax_data = SubTaxResponse()
                    subtax_data.set_id(subtax.id)
                    subtax_data.set_code(subtax.code)
                    subtax_data.set_name(subtax.name)
                    subtax_data.set_tax(subtax.tax)
                    subtax_data.set_remarks(subtax.remarks)
                    subtax_data.set_glno(subtax.glno)

                    subtax_list_data.append(subtax_data)
                vpage = NWisefinPaginator(subtaxlist, vys_page.get_index(), 10)
                subtax_list_data.set_pagination(vpage)
                return subtax_list_data
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_subtax_ID)
                error_obj.set_description(ErrorDescription.INVALID_subtax_ID)
                return error_obj
        except:
            logger.error('ERROR_Subtax_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_subtax_ID)
            error_obj.set_description(ErrorDescription.INVALID_subtax_ID)
            return error_obj

    def fetch_subtax(self, subtax_id, user_id):
        try:
            subtax = SubTax.objects.using(self._current_app_schema()).get(id=subtax_id, entity_id=self._entity_id())
            subtax_data = SubTaxResponse()
            subtax_data.set_id(subtax.id)
            subtax_data.set_code(subtax.code)
            subtax_data.set_name(subtax.name)
            subtax_data.set_tax(subtax.tax)
            subtax_data.set_remarks(subtax.remarks)
            subtax_data.set_glno(subtax.glno)
            return subtax_data

        except SubTax.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_subtax_ID)
            error_obj.set_description(ErrorDescription.INVALID_subtax_ID)
            return error_obj

    def delete_subtax(self, subtax_id, user_id):
        subtax = SubTax.objects.using(self._current_app_schema()).filter(id=subtax_id,
                                                                         entity_id=self._entity_id()).delete()
        self.audit_function(subtax, user_id, subtax_id, ModifyStatus.delete)

        if subtax[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_subtax_ID)
            error_obj.set_description(ErrorDescription.INVALID_subtax_ID)
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
        audit_obj.set_relreftype(MasterRefType.SUBTX)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return

    def fetch_subtax_search(self, query, tax_id, vys_page):
        condition = Q(status=1) & Q(entity_id=self._entity_id())

        if query:
            condition &= Q(name__icontains=query)

        if tax_id:
            condition &= Q(tax_id=tax_id)

        subtaxlist = SubTax.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                     vys_page.get_offset():vys_page.get_query_limit()]

        subtax_list_data = NWisefinList()
        for subtax in subtaxlist:
            subtax_data = SubTaxResponse()
            subtax_data.set_id(subtax.id)
            subtax_data.set_code(subtax.code)
            subtax_data.set_name(subtax.name)
            subtax_list_data.append(subtax_data)
            subtax_data.set_tax(subtax.tax)
            subtax_data.set_remarks(subtax.remarks)
            subtax_data.set_glno(subtax.glno)
            vpage = NWisefinPaginator(subtaxlist, vys_page.get_index(), 10)
            subtax_list_data.set_pagination(vpage)
        return subtax_list_data

    def subtaxtds_search(self, query, vys_page):
        condition = (Q(status=1) & ~Q(tax__name__in=['IGST', 'SGST', 'CGST'])) & Q(entity_id=self._entity_id())

        if query:
            condition &= Q(name__icontains=query)

        subtaxlist = SubTax.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                     vys_page.get_offset():vys_page.get_query_limit()]

        subtax_list_data = NWisefinList()
        for subtax in subtaxlist:
            subtax_data = SubTaxResponse()
            subtax_data.set_id(subtax.id)
            subtax_data.set_code(subtax.code)
            subtax_data.set_name(subtax.name)
            subtax_list_data.append(subtax_data)
            vpage = NWisefinPaginator(subtaxlist, vys_page.get_index(), 10)
            subtax_list_data.set_pagination(vpage)
        return subtax_list_data

    def create_subtax_mtom(self, subtax_obj,action,user_id):

        if action=='update':
            try:
                tax_id = Tax.objects.using(self._current_app_schema()).get(code=subtax_obj.get_taxcode()).id
                subtax_update = SubTax.objects.using(self._current_app_schema()).filter(code =subtax_obj.get_code()).update(code =subtax_obj.get_code(),
                name  =subtax_obj.get_name(),tax_id =tax_id,status=subtax_obj.get_status(),
                remarks =subtax_obj.get_remarks (),glno =subtax_obj.get_glno (),
                updated_by=user_id,updated_date=timezone.now())

                subtax = SubTax.objects.using(self._current_app_schema()).get(code =subtax_obj.get_code())
                subtax_auditdata = {'id': subtax.id,
                                   'code': subtax_obj.get_code(),
                                   'name': subtax_obj.get_name(),
                                   'tax_id': tax_id,
                                   'remarks': subtax_obj.get_remarks(), 'glno': subtax_obj.get_glno(),
                                   'updated_date': timezone.now(),
                                   'updated_by': user_id}
                self.audit_function(subtax_auditdata, user_id, subtax.id, ModifyStatus.update)

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except SubTax.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_subtax_ID)
                error_obj.set_description(ErrorDescription.INVALID_subtax_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        elif action=='create':
            try:
                tax_id = Tax.objects.using(self._current_app_schema()).get(code=subtax_obj.get_taxcode()).id
                subtax = SubTax.objects.using(self._current_app_schema()).create(code =subtax_obj.get_code(),
                name  =subtax_obj.get_name(),tax_id =tax_id,
                remarks =subtax_obj.get_remarks(),glno =subtax_obj.get_glno(),
                created_by =user_id, entity_id=self._entity_id())

                self.audit_function(subtax, user_id, subtax.id, ModifyStatus.create)

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

        subtax_data = SubTaxResponse()
        subtax_data.set_id(subtax.id)
        subtax_data.set_code(subtax.code)
        subtax_data.set_name(subtax.name)
        subtax_data.set_tax_id(subtax.tax_id)
        subtax_data.set_remarks(subtax.remarks)
        subtax_data.set_glno(subtax.glno)
        return subtax_data

    def fetch_subtaxlist(self, subtax_ids):
        # subtax_ids = json.loads(request.body)
        subtax_id2 = subtax_ids['subtax_id']
        obj = SubTax.objects.using(self._current_app_schema()).filter(id__in=subtax_id2,
                                                                      entity_id=self._entity_id()).values('id',
                                                                                                          'tax_id',
                                                                                                          'code',
                                                                                                          'name',
                                                                                                          'glno')
        subtax_list_data = NWisefinList()
        for i in obj:
            data = {"id": i['id'], "tax_id": i['tax_id'], "code": i['code'], "name": i['name'], "glno": i['glno']}
            subtax_list_data.append(data)
        return subtax_list_data.get()


    def fetch_subtax_list_download(self, vys_page):
        try:
            subtaxlist = SubTax.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by('created_date')
            list_length = len(subtaxlist)
            if list_length >= 0:
                subtax_list_data = NWisefinList()
                for subtax in subtaxlist:
                    subtax_data = SubTaxResponse()
                    subtax_data.set_id(subtax.id)
                    subtax_data.set_code(subtax.code)
                    subtax_data.set_name(subtax.name)
                    subtax_data.tax=subtax.tax.name
                    subtax_data.set_remarks(subtax.remarks)
                    subtax_data.set_glno(subtax.glno)

                    subtax_list_data.append(subtax_data)
                return subtax_list_data
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_subtax_ID)
                error_obj.set_description(ErrorDescription.INVALID_subtax_ID)
                return error_obj
        except:
            logger.error('ERROR_Subtax_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_subtax_ID)
            error_obj.set_description(ErrorDescription.INVALID_subtax_ID)
            return error_obj