import traceback

from django.db import IntegrityError

from masterservice.models import PayMode
from nwisefin.settings import logger

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from vendorservice.data.response.paymoderesponse import PaymodeResponse
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
import json
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus

class PaymodeService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_paymode(self, paymode_obj, user_id):
        if not paymode_obj.get_id() is None:
            try:
                logger.error('PAYMODE: PayMode Update Started')
                paymode_update = PayMode.objects.using(self._current_app_schema()).filter(id=paymode_obj.get_id(),
                                                                                          entity_id=self._entity_id()).update(
                    # code=paymode_obj.get_code(),
                    name=paymode_obj.get_name(),
                    updated_by=user_id,
                    updated_date=timezone.now())
                paymode = PayMode.objects.using(self._current_app_schema()).get(id=paymode_obj.get_id(),
                                                                                entity_id=self._entity_id())
                paymode_auditdata = {'id': paymode_obj.get_id(),
                                     # 'code': paymode_obj.get_code(),
                                     'name': paymode_obj.get_name(),
                                     'updated_date': timezone.now(),
                                     'updated_by': user_id}
                self.audit_function(paymode_auditdata, user_id, paymode.id, ModifyStatus.update)
                logger.error('PAYMODE: PayMode Update Success' + str(paymode_update))
            except IntegrityError as error:
                logger.error('ERROR_PayMode_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except PayMode.DoesNotExist:
                logger.error('ERROR_PayMode_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_PAYMODE_ID)
                error_obj.set_description(ErrorDescription.INVALID_PAYMODE_ID)
                return error_obj
            except:
                logger.error('ERROR_PayMode_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('PAYMODE: PayMode Creation Started')
                data_len = PayMode.objects.using(self._current_app_schema()).filter(
                    name=paymode_obj.get_name()).values()
                if (len(data_len) > 0):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                    return error_obj
                paymode = PayMode.objects.using(self._current_app_schema()).create(  # code=paymode_obj.get_code(),
                    name=paymode_obj.get_name(),
                    created_by=user_id, entity_id=self._entity_id())
                try:
                    max_cat_code = PayMode.objects.using(self._current_app_schema()).filter(code__icontains='PM').order_by('-code')[0].code
                    rnsl = int(max_cat_code[3:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "PM" + str(new_rnsl).zfill(3)
                # code = "ISCT" + str(paymode.id)
                paymode.code = code
                paymode.save()
                self.audit_function(paymode, user_id, paymode.id, ModifyStatus.create)
                logger.error('PAYMODE: PayMode Creation Success' + str(paymode))

            except IntegrityError as error:
                logger.error('ERROR_PayMode_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_PayMode_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        paymode_data = PaymodeResponse()
        paymode_data.set_id(paymode.id)
        paymode_data.set_code(paymode.code)
        paymode_data.set_name(paymode.name)
        # return paymode_data
        data = NWisefinSuccess()
        data.set_status(SuccessStatus.SUCCESS)
        data.set_message(SuccessMessage.CREATE_MESSAGE)
        return data
    def fetchpaymode(self, paymode_id):
        try:
            paymode = PayMode.objects.using(self._current_app_schema()).get(id=paymode_id, entity_id=self._entity_id())
            paymode_data = PaymodeResponse()
            paymode_data.set_id(paymode.id)
            paymode_data.set_code(paymode.code)
            paymode_data.set_name(paymode.name)
            paymode_data.gl_flag=(self.paymode_gl_flag(paymode.gl_flag))
            return paymode_data
        except PayMode.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PAYMODE_ID)
            error_obj.set_description(ErrorDescription.INVALID_PAYMODE_ID)
            return error_obj

    def fetch_paymode_list(self, vys_page):
        try:
            paymodeList = PayMode.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by(
                'created_date')[
                          vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(paymodeList)
            pay_list_data = NWisefinList()
            if list_length >= 0:
                for paymode in paymodeList:
                    paymode_data = PaymodeResponse()
                    paymode_data.set_id(paymode.id)
                    paymode_data.set_code(paymode.code)
                    paymode_data.set_name(paymode.name)
                    pay_list_data.append(paymode_data)
                vpage = NWisefinPaginator(paymodeList, vys_page.get_index(), 10)
                pay_list_data.set_pagination(vpage)
                return pay_list_data
            else:
                pass
        except:
            logger.error('ERROR_Paymode_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PAYMODE_ID)
            error_obj.set_description(ErrorDescription.INVALID_PAYMODE_ID)
            return error_obj


    def delete_paymode(self, paymode_id, user_id):
        paymode = PayMode.objects.using(self._current_app_schema()).filter(id=paymode_id,
                                                                           entity_id=self._entity_id()).delete()
        self.audit_function(paymode, user_id, paymode_id, ModifyStatus.delete)

        if paymode[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PAYMODE_ID)
            error_obj.set_description(ErrorDescription.INVALID_PAYMODE_ID)
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
        audit_obj.set_relreftype(MasterRefType.PAYMODE)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return

    def fetch_paymode_search(self, query, vys_page):
        if query is None:
            paymodeList = PayMode.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id()).order_by('created_date')[
                          vys_page.get_offset():vys_page.get_query_limit()]
        else:
            paymodeList = PayMode.objects.using(self._current_app_schema()).filter(name__icontains=query,
                                                                                   entity_id=self._entity_id()).order_by(
                'created_date')[vys_page.get_offset():vys_page.get_query_limit()]

        pay_list_data = NWisefinList()
        from masterservice.service.paymodedetailservice import paymodedetailservice
        apymd_dtls = paymodedetailservice(self._scope())
        for paymode in paymodeList:
            paymode_data = PaymodeResponse()
            paymode_data.set_id(paymode.id)
            paymode_data.set_code(paymode.code)
            paymode_data.set_name(paymode.name)
            paymode_data.gl_flag=(self.paymode_gl_flag(paymode.gl_flag))
            if paymode.gl_flag == "P":
                paymode_data.paymode_details=apymd_dtls.fetch_creditgl_list(paymode.id)
            else:
                paymode_data.paymode_details=[]
            pay_list_data.append(paymode_data)
            vpage = NWisefinPaginator(paymodeList, vys_page.get_index(), 10)
            pay_list_data.set_pagination(vpage)
        return pay_list_data

    def create_paymode_mtom(self, paymode_obj,action, user_id):
        if action =='update':
            try:
                paymode_update = PayMode.objects.using(self._current_app_schema()).filter(code=paymode_obj.get_code()).update(code=paymode_obj.get_code(),
                                                                                 name=paymode_obj.get_name(),
                                                                                 status=paymode_obj.get_status(),
                                                                                 updated_by=user_id,
                                                                                 updated_date=timezone.now())
                paymode = PayMode.objects.using(self._current_app_schema()).get(code=paymode_obj.get_code())
                paymode_auditdata = {'id': paymode_obj.get_id(),
                                     'code': paymode_obj.get_code(),
                                     'name': paymode_obj.get_name(),
                                     'updated_date': timezone.now(),
                                     'updated_by': user_id}
                self.audit_function(paymode_auditdata, user_id, paymode.id, ModifyStatus.update)

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except PayMode.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_PAYMODE_ID)
                error_obj.set_description(ErrorDescription.INVALID_PAYMODE_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        elif action =='create':
            try:
                paymode = PayMode.objects.using(self._current_app_schema()).create(code=paymode_obj.get_code(),
                                                     name=paymode_obj.get_name(),
                                                                         created_by=user_id, entity_id=self._entity_id())


                self.audit_function(paymode, user_id, paymode.id, ModifyStatus.create)

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
            paymode_data = PaymodeResponse()
        paymode_data.set_id(paymode.id)
        paymode_data.set_code(paymode.code)
        paymode_data.set_name(paymode.name)
        return paymode_data

    def fetch_paymodeone(self, paymode_id):
        paymode = PayMode.objects.using(self._current_app_schema()).get(id=paymode_id, entity_id=self._entity_id())
        paymode_data = {"id": paymode.id, "code": paymode.code, "name": paymode.name}
        paymode_dic = json.dumps(paymode_data, indent=4)
        return paymode_data

    def fetch_paymodelist(request, paymode_ids):
        paymode_ids = json.loads(request.body)
        paymode_id2 = paymode_ids['paymode_id']
        obj = PayMode.objects.using(request._current_app_schema()).filter(id__in=paymode_id2,
                                                                          entity_id=request._entity_id()).values('id',
                                                                                                                 'name',
                                                                                                                 'code')
        paymode_list_data = NWisefinList()
        for i in obj:
            data = {"id": i['id'], "name": i['name'], "code": i['code']}
            paymode_list_data.append(data)
        return paymode_list_data

    def paymode_name(self, query):
        paymode = PayMode.objects.using(self._current_app_schema()).get(name=query, entity_id=self._entity_id())
        paymode_data = {"id": paymode.id, "code": paymode.code, "name": paymode.name}
        employee_dic = json.dumps(paymode_data, indent=4)
        return employee_dic

    def paymode_gl_flag(self,string):
        if string =="P":
            return "Payable"
        elif string =="A":
            return "Adjustable"
        elif string =="R":
            return "Recivable"
        else:
            return "NA"

    def fetch_paymode_list_download(self, vys_page):
        try:
            paymodeList = PayMode.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by('created_date')
            list_length = len(paymodeList)
            pay_list_data = NWisefinList()
            if list_length >= 0:
                for paymode in paymodeList:
                    paymode_data = PaymodeResponse()
                    paymode_data.set_id(paymode.id)
                    paymode_data.set_code(paymode.code)
                    paymode_data.set_name(paymode.name)
                    pay_list_data.append(paymode_data)
                return pay_list_data
            else:
                pass
        except:
            logger.error('ERROR_Paymode_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PAYMODE_ID)
            error_obj.set_description(ErrorDescription.INVALID_PAYMODE_ID)
            return error_obj
