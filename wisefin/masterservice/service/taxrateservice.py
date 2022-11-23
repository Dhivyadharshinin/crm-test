import traceback
from django.db import IntegrityError
from masterservice.models import TaxRate, SubTax
from nwisefin.settings import logger
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from vendorservice.data.response.taxrateresponse import TaxRateResponse
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


class TaxRateService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_taxrate(self, taxrate_obj, user_id):
        if not taxrate_obj.get_id() is None:
            try:
                logger.error('TAXRATE: TaxRate Update Started')
                taxrate_update = TaxRate.objects.using(self._current_app_schema()).filter(id=taxrate_obj.get_id()).update(#code =taxrate_obj.get_code ()
                    rate=taxrate_obj.get_rate(),
                name  =taxrate_obj.get_name  (),subtax_id =taxrate_obj.get_subtax_id (),
                updated_by=user_id,updated_date=timezone.now())

                taxrate = TaxRate.objects.using(self._current_app_schema()).get(id=taxrate_obj.get_id())
                taxrate_auditdata = {'id': taxrate_obj.get_id(),
                                   #'code': taxrate_obj.get_code(),
                                   'name': taxrate_obj.get_name(),
                                   'subtax_id': taxrate_obj.get_subtax_id(),
                                   'updated_date': timezone.now(),
                                   'updated_by': user_id}
                self.audit_function(taxrate_auditdata, user_id, taxrate.id, ModifyStatus.update)
                logger.error('TAXRATE: TaxRate Update Success' + str(taxrate_update))

            except IntegrityError as error:
                logger.error('ERROR_TaxRate_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except TaxRate.DoesNotExist:
                logger.error('ERROR_TaxRate_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_taxrate_ID)
                error_obj.set_description(ErrorDescription.INVALID_taxrate_ID)
                return error_obj
            except:
                logger.error('ERROR_TaxRate_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            #try:
                logger.error('TAXRATE: TaxRate Creation Started')
                taxrate = TaxRate.objects.using(self._current_app_schema()).create(#code =taxrate_obj.get_code (),
                name  =taxrate_obj.get_name  (),subtax_id =taxrate_obj.get_subtax_id (),
                rate =taxrate_obj.get_rate (),
                created_by =user_id, entity_id=self._entity_id())


                # code = "ISCT" + str(taxrate.id)
                try:
                    max_cat_code = TaxRate.objects.using(self._current_app_schema()).filter(code__icontains='TR').order_by('-code')[0].code
                    rnsl = int(max_cat_code[2:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "TR" + str(new_rnsl).zfill(3)
                taxrate.code = code
                taxrate.save()
                self.audit_function(taxrate, user_id, taxrate.id, ModifyStatus.create)
                logger.error('TAXRATE: TaxRate Creation Success' + str(taxrate))

            # except IntegrityError as error:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj

        taxrate_data = TaxRateResponse()
        taxrate_data.set_id(taxrate.id)
        taxrate_data.set_code(taxrate.code)
        taxrate_data.set_name(taxrate.name )
        taxrate_data.set_subtax_id (taxrate.subtax_id )
        taxrate_data.set_rate (taxrate.rate)
        # return taxrate_data
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj
    def fetch_taxrate_list(self,vys_page):
        try:
            taxratelist = TaxRate.objects.using(self._current_app_schema()).filter(is_delete=False,status=1).order_by('created_date')[
                             vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(taxratelist)
            if list_length >= 0:
                taxrate_list_data = NWisefinList()
                for taxrate in taxratelist:
                    taxrate_data = TaxRateResponse()
                    taxrate_data.set_id(taxrate.id)
                    taxrate_data.set_code(taxrate.code)
                    taxrate_data.set_name(taxrate.name)
                    taxrate_data.set_subtax(taxrate.subtax)
                    taxrate_data.set_rate(taxrate.rate)
                    taxrate_list_data.append(taxrate_data)
                vpage = NWisefinPaginator(taxratelist, vys_page.get_index(), 10)
                taxrate_list_data.set_pagination(vpage)
                return taxrate_list_data
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_taxrate_ID)
                error_obj.set_description(ErrorDescription.INVALID_taxrate_ID)
                return error_obj
        except:
            logger.error('ERROR_Taxrate_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_taxrate_ID)
            error_obj.set_description(ErrorDescription.INVALID_taxrate_ID)
            return error_obj


    def fetch_taxrate(self, taxrate_id, user_id):
        try:
            taxrate = TaxRate.objects.using(self._current_app_schema()).get(id=taxrate_id, is_delete=False,
                                                                            entity_id=self._entity_id())
            taxrate_data = TaxRateResponse()
            taxrate_data.set_id(taxrate.id)
            taxrate_data.set_code(taxrate.code)
            taxrate_data.set_name(taxrate.name)
            taxrate_data.set_subtax(taxrate.subtax)
            taxrate_data.set_rate(taxrate.rate)
            return taxrate_data

        except TaxRate.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_taxrate_ID)
            error_obj.set_description(ErrorDescription.INVALID_taxrate_ID)
            return error_obj

    def delete_taxrate(self, taxrate_id, user_id):
        # taxrate = TaxRate.objects.filter(id=taxrate_id).delete()
        taxrate = TaxRate.objects.using(self._current_app_schema()).filter(id=taxrate_id,
                                                                           entity_id=self._entity_id()).update(
            is_delete=True)
        self.audit_function(taxrate, user_id, taxrate_id, ModifyStatus.delete)

        if taxrate == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_taxrate_ID)
            error_obj.set_description(ErrorDescription.INVALID_taxrate_ID)
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
        audit_obj.set_relreftype(MasterRefType.TAX_RATE)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return

    def fetch_taxrate_search(self, vys_page, query, subtax_id, name):
        condition = Q(status=1, is_delete=False) & Q(entity_id=self._entity_id())
        if query:
            condition &= Q(rate__icontains=query)
        if subtax_id:
            condition &= Q(subtax_id=subtax_id)
        if name:
            condition &= Q(name__icontains=name)

        taxratelist = TaxRate.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                      vys_page.get_offset():vys_page.get_query_limit()]

        taxrate_list_data = NWisefinList()
        for taxrate in taxratelist:
            taxrate_data = TaxRateResponse()
            taxrate_data.set_id(taxrate.id)
            taxrate_data.set_code(taxrate.code)
            taxrate_data.set_name(taxrate.name)
            taxrate_data.set_rate(taxrate.rate)
            taxrate_data.set_subtax(taxrate.subtax)
            taxrate_list_data.append(taxrate_data)
            vpage = NWisefinPaginator(taxratelist, vys_page.get_index(), 10)
            taxrate_list_data.set_pagination(vpage)
        return taxrate_list_data

    def create_taxrate_mtom(self, taxrate_obj,action,user_id):

        if action=='update':
            #try:
                subtax_id = SubTax.objects.using(self._current_app_schema()).get(code=taxrate_obj.get_subtax_code()).id
                taxrate_update = TaxRate.objects.using(self._current_app_schema()).filter(code =taxrate_obj.get_code()).update(code =taxrate_obj.get_code(),rate=taxrate_obj.get_rate(),
                name  =taxrate_obj.get_name  (),subtax_id =subtax_id,status =taxrate_obj.get_status(),
                updated_by=user_id,updated_date=timezone.now())

                taxrate = TaxRate.objects.using(self._current_app_schema()).get(code =taxrate_obj.get_code())
                taxrate_auditdata = {'id': taxrate.id,
                                   'code': taxrate_obj.get_code(),
                                   'name': taxrate_obj.get_name(),
                                   'subtax_id': subtax_id,
                                   'updated_date': timezone.now(),
                                   'updated_by': user_id}
                self.audit_function(taxrate_auditdata, user_id, taxrate.id, ModifyStatus.update)

            # except IntegrityError as error:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except TaxRate.DoesNotExist:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.INVALID_taxrate_ID)
            #     error_obj.set_description(ErrorDescription.INVALID_taxrate_ID)
            #     return error_obj
            # except:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj

        elif action=='create':
            #try:
                subtax_id = SubTax.objects.using(self._current_app_schema()).get(code=taxrate_obj.get_subtax_code()).id
                taxrate = TaxRate.objects.using(self._current_app_schema()).create(code =taxrate_obj.get_code (),
                name  =taxrate_obj.get_name  (),subtax_id =subtax_id,
                rate =taxrate_obj.get_rate (),
                created_by =user_id, entity_id=self._entity_id())

                self.audit_function(taxrate, user_id, taxrate.id, ModifyStatus.create)

            # except IntegrityError as error:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj

        taxrate_data = TaxRateResponse()
        taxrate_data.set_id(taxrate.id)
        taxrate_data.set_code(taxrate.code)
        taxrate_data.set_name(taxrate.name)
        taxrate_data.set_subtax_id(taxrate.subtax_id)
        taxrate_data.set_rate(taxrate.rate)
        return taxrate_data

    def inactive_taxrate(self, taxrate_obj, user_id):
        print(taxrate_obj, user_id)
        taxrate_id = TaxRate.objects.using(self._current_app_schema()).get(code=taxrate_obj['tax_code'],
                                                                           entity_id=self._entity_id()).id
        if taxrate_obj['isactive'] == 'N':
            taxrate = TaxRate.objects.using(self._current_app_schema()).filter(code=taxrate_obj['tax_code'],
                                                                               entity_id=self._entity_id()).update(
                is_delete=True)
        if taxrate_obj['isactive'] == 'Y':
            taxrate = TaxRate.objects.using(self._current_app_schema()).filter(code=taxrate_obj['tax_code'],
                                                                               entity_id=self._entity_id()).update(
                is_delete=False)
        self.audit_function(taxrate, user_id, taxrate_id, ModifyStatus.delete)

        if taxrate == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_taxrate_ID)
            error_obj.set_description(ErrorDescription.INVALID_taxrate_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj

    def fetch_taxratelist(self, subtax_ids):
        # subtax_ids = json.loads(request.body)
        subtax_id2 = subtax_ids['subtax_id']
        from masterservice.models.mastermodels import TaxRate
        obj = TaxRate.objects.using(self._current_app_schema()).filter(subtax_id__in=subtax_id2,
                                                                       entity_id=self._entity_id()).values('id',
                                                                                                           'subtax_id',
                                                                                                           'code',
                                                                                                           'name',
                                                                                                           'rate')
        taxrate_list_data = NWisefinList()
        for i in obj:
            data = {"id": i['id'], "subtax_id": i['subtax_id'], "code": i['code'], "name": i['name'], "rate": i['rate']}
            taxrate_list_data.append(data)
        return taxrate_list_data.get()

    def taxrate_active_inactive(self, request,taxrate_obj,user_id):


        if (int(taxrate_obj.status) == 0):

            tax_rate_data = TaxRate.objects.using(self._current_app_schema()).filter(id=taxrate_obj.id).update(
                status=1)
        else:
            tax_rate_data = TaxRate.objects.using(self._current_app_schema()).filter(id=taxrate_obj.id).update(
                status=0)
        taxrate_var = TaxRate.objects.using(self._current_app_schema()).get(id=taxrate_obj.id)
        data = TaxRateResponse()
        data.set_status(taxrate_var.status)
        status = taxrate_var.status
        data.set_id(taxrate_var.id)
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

    def fetch_taxrate_list_download(self, vys_page):
        try:
            taxratelist = TaxRate.objects.using(self._current_app_schema()).filter(is_delete=False, status=1).order_by('created_date')
            list_length = len(taxratelist)
            if list_length >= 0:
                taxrate_list_data = NWisefinList()
                for taxrate in taxratelist:
                    taxrate_data = TaxRateResponse()
                    taxrate_data.set_id(taxrate.id)
                    taxrate_data.set_code(taxrate.code)
                    taxrate_data.set_name(taxrate.name)
                    taxrate_data.subtax_name=taxrate.subtax.name
                    taxrate_data.set_rate(taxrate.rate)
                    taxrate_list_data.append(taxrate_data)
                return taxrate_list_data
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_taxrate_ID)
                error_obj.set_description(ErrorDescription.INVALID_taxrate_ID)
                return error_obj
        except:
            logger.error('ERROR_Taxrate_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_taxrate_ID)
            error_obj.set_description(ErrorDescription.INVALID_taxrate_ID)
            return error_obj
