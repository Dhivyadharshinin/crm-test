import traceback

import django
from django.utils import timezone
from django.db import IntegrityError
from masterservice.models import PaymodeDetails
from masterservice.data.response.paymodedetailresponse import  PaymodedetailResponse
from masterservice.service.paymodeservice import PaymodeService
from masterservice.service.apcategoryservice import CategoryService
from masterservice.service.apsubcategoryservice import SubcategoryService
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

from django.db.models import Q

class paymodedetailservice(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def fetch_paymodedtl_list(self,vys_page):

        paymodelist = PaymodeDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())
        list_length = len(paymodelist)
        paymodedtl_list_data = NWisefinList()
        if list_length > 0:
            for paymode in paymodelist:
                paym_data = PaymodedetailResponse()
                paym_data.set_id(paymode.id)
                paym_data.set_glno(paymode.glno)
                paym_data.set_name(paymode.name)
                category_service = CategoryService(self._scope())   # changed
                paym_data.set_category(category_service.fetchcategory(paymode.category_id))
                subcategory_service = SubcategoryService(self._scope())   # changed
                paym_data.set_sub_category(subcategory_service.fetchsubcategory(paymode.sub_category_id))
                paymode_service = PaymodeService(self._scope())  # changed
                paym_data.set_paymode(paymode_service.fetchpaymode(paymode.paymode_id))

                paymodedtl_list_data.append(paym_data)
        return paymodedtl_list_data
    def fetch_creditgl_list(self,pay_id):
        try:
            print('pay_id',pay_id)
            condition = Q(paymode_id=pay_id) &Q(entity_id=self._entity_id())
            paymodelist = PaymodeDetails.objects.using(self._current_app_schema()).filter(condition)
            print('paymodelist',len(paymodelist))
            list_length = len(paymodelist)
            paymodedtl_list_data = NWisefinList()
            if list_length > 0:
                for paymode in paymodelist:
                    paym_data = PaymodedetailResponse()
                    paym_data.set_id(paymode.id)
                    paym_data.set_glno(paymode.glno)
                    paym_data.set_name(paymode.name)
                    paym_data.set_status(paymode.status)
                    category_service = CategoryService(self._scope())   # changed
                    paym_data.set_category(category_service.fetchcategory(paymode.category_id))
                    subcategory_service = SubcategoryService(self._scope())   # changed
                    paym_data.set_sub_category(subcategory_service.fetchsubcategory(paymode.sub_category_id))
                    paymode_service = PaymodeService(self._scope())   # changed
                    paym_data.set_paymode(paymode_service.fetchpaymode(paymode.paymode_id))
                    paymodedtl_list_data.append(paym_data)
            return paymodedtl_list_data
        except:
            logger.error('ERROR_PaymodeDetails_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj


    def paymodedetail_create(self,paymode_obj,user_id):
        if not paymode_obj.get_id() is None:
            try:
                paymode_update = PaymodeDetails.objects.using(self._current_app_schema()).filter(id=paymode_obj.get_id(),entity_id=self._entity_id()).update(  # code=paymode_obj.get_code(),
                    name=paymode_obj.get_name(),
                    paymode_id=paymode_obj.get_paymode_id(),
                    category_id=paymode_obj.get_category_id(),
                    sub_category_id=paymode_obj.get_sub_category_id(),
                    glno=paymode_obj.get_glno(),
                    updated_by=user_id,
                    updated_date=timezone.now())
                paymode_details = PaymodeDetails.objects.get(id=paymode_obj.get_id())
                data = NWisefinSuccess()
                data.set_status(SuccessStatus.SUCCESS)
                data.set_message(SuccessMessage.UPDATE_MESSAGE)
                return data



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
                paymode_details = PaymodeDetails.objects.using(self._current_app_schema()).create(  # code=paymode_obj.get_code(),
                    name=paymode_obj.get_name(),
                    paymode_id=paymode_obj.get_paymode_id(),
                    category_id=paymode_obj.get_category_id(),
                    sub_category_id=paymode_obj.get_sub_category_id(),
                    glno=paymode_obj.get_glno(),
                    entity_id=self._entity_id(),
                    created_by=user_id)
                data = NWisefinSuccess()
                data.set_status(SuccessStatus.SUCCESS)
                data.set_message(SuccessMessage.CREATE_MESSAGE)
                return data


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
        # paymodedetails_data = PaymodedetailResponse()
        # paymodedetails_data.set_id(paymode_details.id)
        # paymodedetails_data.set_name(paymode_details.name)
        # paymodedetails_data.set_paymode(paymode_details.paymode)
        # paymodedetails_data.set_category(paymode_details.category)
        # paymodedetails_data.set_sub_category(paymode_details.sub_category)
        # paymodedetails_data.set_glno(paymode_details.glno)
        # #return paymodedetails_data
        # data = NWisefinSuccess()
        # data.set_status(SuccessStatus.SUCCESS)
        # data.set_message(SuccessMessage.CREATE_MESSAGE)
        # return data

    def paymodedetails_active_inactive(self, request, paymodedetails_obj, user_id):

        if (int(paymodedetails_obj.status) == 0):

            paymodedetails_data = PaymodeDetails.objects.using(self._current_app_schema()).filter(id=paymodedetails_obj.id).update(
                status=1)
        else:
            paymodedetails_data = PaymodeDetails.objects.using(self._current_app_schema()).filter(id=paymodedetails_obj.id).update(
                status=0)
        paymodedetail_var = PaymodeDetails.objects.using(self._current_app_schema()).get(id=paymodedetails_obj.id)
        data = PaymodedetailResponse()
        data.set_status(paymodedetail_var.status)
        status = paymodedetail_var.status
        data.set_id(paymodedetail_var.id)
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