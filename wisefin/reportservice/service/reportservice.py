from datetime import datetime

from django.db.models import Q
from django.utils.timezone import now

from nwisefin.settings import logger
from reportservice.data.response.reportresponse import templateResponse
from reportservice.models import ModuleDropdown, ModuleNameDropdown, ReportParameter
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
START_TIME_D = datetime.now()
START_TIME = START_TIME_D.strftime("%d/%m/%Y %H:%M:%S")

class ReportService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.REPORT_SERVICE)

    def fetch_moduledropdownservice(self):
        condition = Q(status=1)
        try:
            logger.info('Module Drop Down - ' + START_TIME)
            module = ModuleDropdown.objects.using(self._current_app_schema()).filter(condition)
            print(self._current_app_schema())
            list_length = len(module)
            module_list_data = NWisefinList()
            if list_length <= 0:
                pass
            else:
                for i in module:
                    module_data = templateResponse()
                    module_data.set_id(i.id)
                    module_data.set_code(i.module_code)
                    module_data.set_name(i.module_name)
                    module_list_data.append(module_data)
                    # vpage = VysfinPaginator(entrydetails, vys_page.get_index(), 10)
                    # entry_list_data.set_pagination(vpage)
                    logger.info('Module Drop Down - ' + START_TIME)
                return module_list_data
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(e))
            logger.info('Module Drop Down Error - ' + str(e))
            return error_obj

    def fetch_modulenamedropdownservice(self, trans_id):
        condition = Q(status=1) & Q(reportname_moduleid=trans_id)
        try:
            logger.info('Module Name Drop Down - ' + START_TIME)
            module = ModuleNameDropdown.objects.using(self._current_app_schema()).filter(condition)
            list_length = len(module)
            module_list_data = NWisefinList()
            if list_length <= 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(str('No Data'))
                return error_obj
            else:
                for i in module:
                    module_data = templateResponse()
                    module_data.set_id(i.id)
                    module_data.set_code(i.reportname_code)
                    module_data.set_name(i.reportname_name)
                    module_list_data.append(module_data)
                    logger.info('Module Drop Down - ' + START_TIME)
                    # vpage = VysfinPaginator(entrydetails, vys_page.get_index(), 10)
                    # entry_list_data.set_pagination(vpage)
                return module_list_data
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(e))
            logger.info('Module Drop Down - ' + str(e))
            return error_obj


    def create_moduleparameter(self,module_id,report_id,emp_id,paramname, columnname,filtername,scope):
            try:
                logger.info('Module Parameter Create - ' + START_TIME)
                module_name = ModuleNameDropdown.objects.using(self._current_app_schema()). \
                    create(reportname_moduleid=module_id,
                           reportname_code=paramname,
                           reportname_name=paramname,
                           entity_id=self._entity_id(),
                           status=1,
                           created_by=emp_id,
                           created_date=now())
                module_name.save()

                id = ModuleNameDropdown.objects.using(self._current_app_schema()).latest('id')
                module_name_id = id.id

                ParameterName_Detail = ReportParameter.objects .using(self._current_app_schema()). \
                                        create(reportemp_moduleid=module_id, reportemp_modulenamedropdownid=module_name_id,
                                               reportemp_empid=emp_id,
                                               reportemp_name=paramname,
                                               reportemp_column=columnname,
                                               reportemp_filter=filtername,
                                               entity_id=self._entity_id(),
                                               created_by=emp_id,
                                               created_date=now())
                ParameterName_Detail.save()

                logger.info('Module Parameter Create - ' + START_TIME)
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.CREATE_MESSAGE)

            except Exception as excep:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(str(excep))
                logger.info('Module Parameter Create - ' + str(excep))
                return error_obj
            return success_obj
