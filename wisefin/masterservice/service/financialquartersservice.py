import traceback

import django
from django.db import IntegrityError
from django.db.models import Q

from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from masterservice.data.response.financialquartersresponse import FinancialQuartersResponse
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from masterservice.data.response.financialyearresponse import FinancialResponse
from masterservice.models import Financial_Year, Financial_Quarters

from datetime import datetime

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

now = datetime.now()
import json
class financial_quarters_service(NWisefinThread):

    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_finquarters(self, data,emp_id):
        fin_res = FinancialQuartersResponse()
        if not data.get_id() is None:
                logger.error('FINANCIAL QUARTERS: Financial_Quarters Update Started')


                fin_var = Financial_Quarters.objects.using(self._current_app_schema()).filter(id=data.get_id()).update(fin_year=data.get_fin_year(),
                                                        fin_month=data.get_fin_month(),
                                                        # fin_quarter_from_period=data.get_fin_quarter_from_period(),
                                                        # fin_quarter_to_period=data.get_fin_quarter_to_period(),
                                                        status=data.get_status(),
                                                        updated_by = emp_id,
                                                        updated_date = now)

                fin_var = Financial_Quarters.objects.get(id=data.get_id())
                logger.error('FINANCIAL QUARTERS: Financial_Quarters Update Success' + str(fin_var))
        else:
            logger.error('FINANCIAL QUARTERS: Financial_Quarters Creation Started')
            fin_var = Financial_Quarters.objects.using(self._current_app_schema()).create(id=data.get_id(),
                                                                             fin_year=data.get_fin_year(),
                                                                             fin_month=data.get_fin_month(),
                                                                             # fin_quarter_from_period=data.get_fin_quarter_from_period(),
                                                                             # fin_quarter_to_period=data.get_fin_quarter_to_period(),

                                                                             created_by=emp_id,
                                                                             created_date=now)
            logger.error('FINANCIAL QUARTERS: Financial_Quarters Creation Success' + str(fin_var))




        fin_res.set_id(fin_var.id)
        fin_res.set_fin_year(fin_var.fin_year)
        fin_res.set_fin_month(fin_var.fin_month)
        fin_res.set_fin_quarter_from_period(fin_var.fin_quarter_from_period)
        fin_res.set_fin_quarter_to_period(fin_var.fin_quarter_to_period)
        fin_res.set_status(fin_var.status)

        return fin_res


    def fetch_finqtr_list(self,request,vys_page):
        try:
            condition = Q()
            if "year" in request.GET:
                condition &= Q(fin_year__icontains=request.GET.get("year"))
            if "month" in request.GET:
                condition &= Q(fin_month__icontains=request.GET.get("month"))
            fin_list_data = NWisefinList()
            finlist = Financial_Quarters.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                             vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(finlist)
            if list_length >= 0:
                for finobj in finlist:
                    fin_res = FinancialQuartersResponse()
                    fin_res.set_id(finobj.id)
                    fin_res.set_fin_year(finobj.fin_year)
                    fin_res.set_fin_month(finobj.fin_month)
                    fin_res.set_status(finobj.status)
                    fin_list_data.append(fin_res)
                vpage = NWisefinPaginator(finlist, vys_page.get_index(), 10)
                fin_list_data.set_pagination(vpage)
                return fin_list_data
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_Financial_Quarters_ID)
                error_obj.set_description(ErrorDescription.INVALID_Financial_Quarters_ID)
                return error_obj
        except:
            logger.error('ERROR_Financial_Quarters_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_Financial_Quarters_ID)
            error_obj.set_description(ErrorDescription.INVALID_Financial_Quarters_ID)
            return error_obj

    def fin_quarter_yr_activate_inactivate(self, request, fin_obj):

        if (int(fin_obj.status) == 0):

            fin_data = Financial_Quarters.objects.using(self._current_app_schema()).filter(id=fin_obj.id).update(
                status=1)
        else:
            fin_data = Financial_Quarters.objects.using(self._current_app_schema()).filter(id=fin_obj.id).update(
                status=0)
        fin_var = Financial_Quarters.objects.using(self._current_app_schema()).get(id=fin_obj.id)
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


