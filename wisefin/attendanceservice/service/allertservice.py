from attendanceservice.models.attendancemodels import AlertMessage
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from attendanceservice.util.attendanceutil import AlertType
from django.db import IntegrityError
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from attendanceservice.util.responsemessage import MessageResponse, StatusType
from utilityservice.data.response.nwisefinsuccess import SuccessMessage
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription
from attendanceservice.data.response.alertresponse import AlertResponse
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.service.attendanceapiservice import AttendanceAPIService
import datetime


class AlertService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ATTENDANCE_SERVICE)

    def create_alert_message(self, alert_type, data_obj):
        if alert_type == AlertType.LEAVE_INFO:
            try:
                alert = AlertMessage.objects.using(self._current_app_schema()
                                                   ).create(leave_data_id=data_obj['leave_data_id'],
                                                            message=data_obj['message'],
                                                            alert_to=data_obj['alert_to'],
                                                            alert_from=data_obj['alert_from'],
                                                            created_date=datetime.datetime.now())
            except IntegrityError as error:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                alert = AlertMessage.objects.using(self._current_app_schema()
                                                   ).create(message=data_obj['message'],
                                                            alert_to=data_obj['alert_to'],
                                                            alert_from=data_obj['alert_from'],
                                                            created_date=datetime.datetime.now())
            except IntegrityError as error:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        data = AlertResponse()
        data.set_id(alert.id)
        if alert_type == AlertType.LEAVE_INFO:
            data.set_leave_data_id(alert.leave_data_id)
        data.set_message(alert.message)
        data.set_status(alert.status)
        data.set_alert_to(alert.alert_to)
        data.set_alert_from(alert.alert_from)
        data.set_seen(alert.status)
        return data

    def update_status(self, alert_id):
        alert = AlertMessage.objects.using(self._current_app_schema()
                                               ).filter(id=alert_id, entity_id=self._entity_id()
                                                        ).update(status=1)
        if alert == 1:
            success_obj = MessageResponse()
            success_obj.set_status(StatusType.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
        else:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj

    def alert_summary(self, vys_page, emp_id):
        alert_list = AlertMessage.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), alert_to=emp_id
        ).order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        list_data = NWisefinList()
        employee = [a.alert_to for a in alert_list]
        alert_from_list = [a.alert_from for a in alert_list]
        employee.extend(alert_from_list)
        employee = set(employee)
        employee = list(employee)
        emp_serv = AttendanceAPIService(self._scope())
        emp_data_list = emp_serv.get_employee_list(employee)
        for alert in alert_list:
            data = AlertResponse()
            data.set_id(alert.id)
            data.set_leave_data_id(alert.leave_data_id)
            data.set_message(alert.message)
            data.set_status(alert.status)
            alert_to = emp_serv.get_id_with_list(alert.alert_to, emp_data_list)
            data.set_alert_to(alert_to)
            alert_from = emp_serv.get_id_with_list(alert.alert_from, emp_data_list)
            data.set_alert_from(alert_from)
            data.set_seen(alert.status)
            list_data.append(data)
        paginator = NWisefinPaginator(alert_list, vys_page.get_index(), 10)
        list_data.set_pagination(paginator)
        return list_data

    def fetch_alert_message(self, alert_id):
        alert = AlertMessage.objects.using(self._current_app_schema()).filter(id=alert_id, entity_id=self._entity_id())
        if len(alert) != 0:
            data = AlertResponse()
            data.set_id(alert.id)
            data.set_leave_data_id(alert.leave_data_id)
            data.set_message(alert.message)
            data.set_status(alert.status)
            data.set_alert_to(alert.alert_to)
            data.set_alert_from(alert.alert_from)
            data.set_seen(alert.status)
            return data
        else:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj

    def delete_alert_message(self, alert_id):
        try:
            leave_delete = AlertMessage.objects.using(self._current_app_schema()).filter(id=alert_id,
                                                                                         entity_id=self._entity_id()
                                                                                         ).delete()
            success_obj = MessageResponse()
            success_obj.set_status(StatusType.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj
