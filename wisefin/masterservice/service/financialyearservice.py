import traceback

import django
from django.db import IntegrityError
from django.db.models import Q
from django.db.models import Q
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.service.Codegenerator import CodeGen
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.util.masterutil import ModifyStatus, MasterRefType, RequestStatusUtil, Code_Gen_Type, Code_Gen_Value
from nwisefin.settings import logger
from pprservice.data.response.success import Success
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from datetime import datetime
import json
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from masterservice.data.response.financialyearresponse import FinancialResponse
from masterservice.models import Financial_Year
from datetime import datetime

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

now = datetime.now()
import json
class Financial_year_service(NWisefinThread):

    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_finyear(self, data,emp_id):

        if not data.get_id() is None:
                logger.error('FINANCIAL YEAR: Financial_Year Update Started')

                fin_var = Financial_Year.objects.using(self._current_app_schema()).filter(id=data.get_id()).update(fin_year=data.get_fin_year(),
                                                        fin_month=data.get_fin_month(),
                                                        # fin_year_from_period= data.get_fin_year_from_period(),
                                                        # fin_year_to_period=data.get_fin_year_to_period(),
                                                        updated_by = emp_id,
                                                        updated_date = now,
                                                        status = data.get_status())

                fin_var = Financial_Year.objects.get(id=data.get_id())
                logger.error('FINANCIAL YEAR: Financial_Year Update Success' + str(fin_var))
        else:
            logger.error('FINANCIAL YEAR: Financial_Year Creation Started')
            fin_var = Financial_Year.objects.using(self._current_app_schema()).create(id=data.get_id(),
                                                                             fin_year=data.get_fin_year(),
                                                                             fin_month=data.get_fin_month(),
                                                                             # fin_year_from_period=data.get_fin_year_from_period(),
                                                                             # fin_year_to_period=data.get_fin_year_to_period(),
                                                                             created_by=emp_id,
                                                                             created_date=now,
                                                                             # status=data.get_status()
                                                                            )
            logger.error('FINANCIAL YEAR: Financial_Year Creation Success' + str(fin_var))

        fin_res = FinancialResponse()
        fin_res.set_id(fin_var.id)
        fin_res.set_fin_year(fin_var.fin_year)
        fin_res.set_fin_month(fin_var.fin_month)
        fin_res.set_fin_year_from_period(fin_var.fin_year_from_period)
        fin_res.set_fin_year_to_period(fin_var.fin_year_to_period)
        fin_res.set_status(fin_var.status)

        return fin_res


    def fetch_finyr_list(self,request,vys_page):
        try:
            condition = Q()
            if "year" in request.GET:
                condition &= Q(fin_year__icontains=request.GET.get("year"))
            if "month" in request.GET:
                condition &= Q(fin_month__icontains=request.GET.get("month"))
            fin_list_data = NWisefinList()
            finlist = Financial_Year.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                             vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(finlist)
            if list_length >= 0:
                for finobj in finlist:
                    fin_res = FinancialResponse()
                    fin_res.set_id(finobj.id)
                    fin_res.set_fin_year(finobj.fin_year)
                    fin_res.set_fin_month(finobj.fin_month)
                    # fin_res.set_fin_year_from_period(finobj.fin_year_from_period)
                    # fin_res.set_fin_year_to_period(finobj.fin_year_period)
                    fin_res.set_status(finobj.status)
                    fin_list_data.append(fin_res)
                vpage = NWisefinPaginator(finlist, vys_page.get_index(), 10)
                fin_list_data.set_pagination(vpage)
                return fin_list_data
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_Financial_Year_ID)
                error_obj.set_description(ErrorDescription.INVALID_Financial_Year_ID)
                return error_obj
        except:
            logger.error('ERROR_Financial_Year_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_Financial_Year_ID)
            error_obj.set_description(ErrorDescription.INVALID_Financial_Year_ID)
            return error_obj

    def finyr_activate_inactivate(self, request, fin_obj):

        if (int(fin_obj.status) == 0):

            fin_data = Financial_Year.objects.using(self._current_app_schema()).filter(id=fin_obj.id).update(
                status=1)
        else:
            fin_data = Financial_Year.objects.using(self._current_app_schema()).filter(id=fin_obj.id).update(
                status=0)
        fin_var = Financial_Year.objects.using(self._current_app_schema()).get(id=fin_obj.id)
        data = FinancialResponse()
        data.set_status(fin_var.status)
        status = fin_var.status
        # print(status)
        data.set_id(fin_var.id)
        # return data
        if status == 1:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.ACTIVATED)
            return data
        else:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.INACTIVATED)
            return data