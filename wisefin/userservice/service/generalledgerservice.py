import traceback

import django
from django.db.models import Q
from django.db import IntegrityError

from nwisefin.settings import logger
from userservice.models import General_Ledger
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from userservice.data.response.generalledgerresponse import General_LedgerResponse
from datetime import datetime
now = datetime.now()
from masterservice.data.request.masterauditrequest import MasterAuditRequest
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.util.masterutil import ModifyStatus,MasterRefType,RequestStatusUtil

from userservice.data.response.generalledgerresponse import General_LedgerResponse
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
class General_LedgerService(NWisefinThread):
    # class UomService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.USER_SERVICE)

    def create_gl(self, gl_obj):
        # if not gl_obj.get_id() is None:
        #     try:
        #         logger.error('GENERAL LEDGER: General_Ledger update Started')
        #         gl_var = General_Ledger.objects.using(self._current_app_schema()).filter(id=masterbusiness_obj.get_id(), entity_id=self._entity_id()).update(
        #             no=gl_obj.get_no(),
        #             description=gl_obj.get_description(),
        #             currency=gl_obj.get_currency(),
        #             sortorder=gl_obj.get_sortorder(),
        #             sortorderdesc=gl_obj.get_sortorder_description(),
        #             sch16_desc_bank=gl_obj.get_sch16_descbank(),
        #             type=gl_obj.get_type(),
        #             sch16_sortorder=gl_obj.get_sch16_sortorder()
        #             , lastsync_date=datetime.now())
        #         logger.error('GENERAL LEDGER: General_Ledger Creation Success' + str(gl_var))
        #     except IntegrityError as error:
        #         logger.error('ERROR_General_Ledger_Update_EXCEPT:{}'.format(traceback.print_exc()))
        #         error_obj = NWisefinError()
        #         error_obj.set_code(ErrorMessage.INVALID_DATA)
        #         error_obj.set_description(ErrorDescription.INVALID_DATA)
        #         return error_obj
        #     except General_Ledger.DoesNotExist:
        #         logger.error('ERROR_General_Ledger_Update_EXCEPT:{}'.format(traceback.print_exc()))
        #         error_obj = NWisefinError()
        #         error_obj.set_code(ErrorMessage.INVALID_costcentre_ID)
        #         error_obj.set_description(ErrorDescription.INVALID_costcentre_ID)
        #         return error_obj
        #     except:
        #         logger.error('ERROR_General_Ledger_Update_EXCEPT:{}'.format(traceback.print_exc()))
        #         error_obj = NWisefinError()
        #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #         error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
        #         return error_obj
        # else:
        #     try:
        logger.error('GENERAL LEDGER: General_Ledger Creation Started')
        gl_var = General_Ledger.objects.using(self._current_app_schema()).create(
                                             no=gl_obj.get_no(),
                                             description=gl_obj.get_description(),
                                             currency=gl_obj.get_currency(),
                                             sortorder=gl_obj.get_sortorder(),
                                             sortorderdesc=gl_obj.get_sortorder_description(),
                                             sch16_desc_bank = gl_obj.get_sch16_descbank(),
                                             type = gl_obj.get_type(),
                                             sch16_sortorder = gl_obj.get_sch16_sortorder()
                                             ,lastsync_date=datetime.now())
        logger.error('GENERAL LEDGER: General_Ledger Creation Success' + str(gl_var))
            # except IntegrityError as error:
            #     logger.error('ERROR_General_Ledger_Create_EXCEPT:{}'.format(traceback.print_exc()))
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except:
            #     logger.error('ERROR_General_Ledger_Create_EXCEPT:{}'.format(traceback.print_exc()))
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj

        gl_data = General_LedgerResponse()
        # gl_data.set_id(gl_var.id)
        # gl_data.set_description(gl_var.description)
        # gl_data.set_no(gl_var.no)
        # gl_data.set_sortorder(gl_var.sortorder)
        # gl_data.set_currency(gl_var.currency)
        # gl_data.set_sortorderdescription(gl_var.sortorderdescription)
        # gl_data.set_sch16_descbank(gl_var.sch16_descbank)
        # gl_data.set_type(gl_var.type)
        # gl_data.set_sch16_sortorder(gl_var.sch16_sortorder)
        return gl_data



    def Fetch_All_Gl_List(self, datefilter):
        condition = Q(lastsync_date__gte=datefilter)
        glList = General_Ledger.objects.using(self._current_app_schema()).filter(condition)
        list_length = len(glList)
        gl_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for gl in glList:
                data_obj = General_LedgerResponse()
                data_obj.set_id(gl.id)
                data_obj.set_no(gl.no)
                data_obj.set_description(gl.description)
                data_obj.set_currency(gl.currency)
                data_obj.set_sortorder(gl.sortorder)
                data_obj.set_sortorderdescription(gl.sortorderdesc)
                data_obj.set_sch16_descbank(gl.sch16_desc_bank)
                data_obj.set_type(gl.type)
                data_obj.set_sch16_sortorder(gl.sch16_sortorder)
                gl_list_data.append(data_obj)
        return gl_list_data

    def fetch_gl_summary(self, request,vys_page):
        try:
            condition = Q()
            if "data" in request.GET:
                condition &= Q(no__icontains=request.GET.get("data"))

            if 'status' in request.GET:
                if request.GET.get('status')=="ACTIVE":
                    condition &= Q(status=1)
                else:
                    condition &= Q(status=0)

            glList = General_Ledger.objects.using(self._current_app_schema()).filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(glList)
            gl_list_data = NWisefinList()
            if list_length <= 0:
                pass
            else:
                for gl in glList:
                    data_obj = General_LedgerResponse()
                    data_obj.set_id(gl.id)
                    data_obj.set_no(gl.no)
                    data_obj.set_description(gl.description)
                    data_obj.set_currency(gl.currency)
                    data_obj.set_sortorder(gl.sortorder)
                    data_obj.set_sortorderdescription(gl.sortorderdesc)
                    data_obj.set_sch16_descbank(gl.sch16_desc_bank)
                    data_obj.set_type(gl.type)
                    data_obj.set_sch16_sortorder(gl.sch16_sortorder)
                    data_obj.set_status(gl.status)
                    gl_list_data.append(data_obj)
                vpage = NWisefinPaginator(glList, vys_page.get_index(), 10)
                gl_list_data.set_pagination(vpage)
            return gl_list_data
        except:
            logger.error('ERROR_General_Ledger_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj
    def fetch_gl_no(self, request,gl_no):
        condition=Q(no=int(gl_no),status=1)
        glList = General_Ledger.objects.using(self._current_app_schema()).filter(condition).values()
        chk_list=len(glList)
        if chk_list==0:
            description = None
        else:
           description=glList[0]['description']
        return description

    def fetch_gl_no_api(self, request,gl_no):
        condition=Q(no=int(gl_no),status=1)
        glList = General_Ledger.objects.using(self._current_app_schema()).filter(condition).values()
        chk_list=len(glList)
        gl_list_data = NWisefinList()
        if chk_list>0:
            data_obj = General_LedgerResponse()
            data_obj.id=(glList[0]['id'])
            data_obj.gl_description=(glList[0]['description'])
            data_obj.gl_no=(glList[0]['no'])
            gl_list_data.append(data_obj)
        return gl_list_data


    def gl_activate_inactivate(self,request,data_request_obj):
        if (int(data_request_obj.status) == 0):

            gl_data = General_Ledger.objects.using(self._current_app_schema()).filter(id=data_request_obj.id).update(
                status=1)
        else:
            gl_data = General_Ledger.objects.using(self._current_app_schema()).filter(id=data_request_obj.id).update(
                status=0)
        gl_var = General_Ledger.objects.using(self._current_app_schema()).get(id=data_request_obj.id)
        data = General_LedgerResponse()
        data.set_status(gl_var.status)
        status = gl_var.status
        data.set_id(gl_var.id)
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
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj