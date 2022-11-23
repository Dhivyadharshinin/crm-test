from attendanceservice.models.attendancemodels import LeaveApproveQueue,LeaveRequest
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from attendanceservice.data.response.leaveresponse import LeaveApproveResponse
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from attendanceservice.util.responsemessage import MessageResponse, StatusType
from utilityservice.data.response.nwisefinsuccess import SuccessMessage
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription
from nwisefin.settings import logger
from django.db import IntegrityError
import datetime
from django.utils import timezone
from attendanceservice.util.attendanceutil import LeaveApproveType,ActiveStatus

class LeaveApproveService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ATTENDANCE_SERVICE)

    def create_leave_approve(self, resp_obj, emp_id):
        if resp_obj.get_id() is not None:
            try:
                update = LeaveApproveQueue.objects.using(self._current_app_schema()).filter(
                    id=resp_obj.get_id(), entity_id=self._entity_id()).update(remarks=resp_obj.get_remarks())
                leave_data = LeaveApproveQueue.objects.using(self._current_app_schema()).get(id=resp_obj.get_id())
                logger.info('leave approve update status (' + str(update) + '), for id :' + str(leave_data.id))
            except IntegrityError as error:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_DATA)
                return error_obj
            except LeaveApproveQueue.DoesNotExist:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_ATTENDANCE_ID)
                return error_obj
            except:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                leave_data = LeaveApproveQueue.objects.using(self._current_app_schema()
                                                        ).create(leave_request_id=resp_obj.get_leave_request_id(),
                                                                 remarks=resp_obj.get_remarks(),
                                                                 created_by=emp_id,
                                                                 created_date=datetime.datetime.now(),
                                                                 entity_id=self._entity_id())
                logger.info('leave request created for id : '+str(leave_data.id))
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

        # data = LeaveApproveResponse()
        # data.set_id(leave_data.id)
        # data.set_leave_request_id(leave_data.leave_request_id)
        # data.set_remarks(leave_data.remarks)
        # data.set_status(leave_data.status)
        # data.set_created_date(leave_data.created_date)
        # data.set_created_by(leave_data.created_by)
        # return data
        success_obj = MessageResponse()
        success_obj.set_status(StatusType.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def leave_approve_list(self, vys_page):
        leave_list = LeaveApproveQueue.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id()).order_by('created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        list_data = NWisefinList()
        for leave in leave_list:
            data = LeaveApproveResponse()
            data.set_id(leave.id)
            data.set_leave_request_id(leave.leave_request_id)
            data.set_remarks(leave.remarks)
            data.set_status(leave.status)
            data.set_created_date(leave.created_date)
            data.set_created_by(leave.created_by)
            list_data.append(data)
        paginator = NWisefinPaginator(leave_list, vys_page.get_index(), 10)
        list_data.set_pagination(paginator)
        return list_data

    def fetch_leave_approve(self, leave_id):
        try:
            leave = LeaveApproveQueue.objects.using(self._current_app_schema()).get(id=leave_id, entity_id=self._entity_id())
            data = LeaveApproveResponse()
            data.set_id(leave.id)
            data.set_leave_request_id(leave.leave_request_id)
            data.set_remarks(leave.remarks)
            data.set_status(leave.status)
            data.set_created_date(leave.created_date)
            data.set_created_by(leave.created_by)
            return data
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj

    def delete_leave_approve(self, leave_id):
        try:
            leave_delete = LeaveApproveQueue.objects.using(self._current_app_schema()).filter(id=leave_id).delete()
            logger.info('leave approve deleted status('+str(leave_delete)+'), for id : '+str(leave_id))
            success_obj = MessageResponse()
            success_obj.set_status(StatusType.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj

    def get_approve_status(self, leave_id, approve_status):
        if approve_status != -1:
            leave = LeaveApproveQueue.objects.using(self._current_app_schema()).filter(leave_request_id=leave_id, entity_id=self._entity_id())
            leave= leave[0]
            data = LeaveApproveResponse()
            data.set_id(leave.id)
            data.set_remarks(leave.remarks)
            return data
        else:
            data = LeaveApproveResponse()
            data.set_id(-1)
            data.set_remarks('')
            return data

    def approved_status(self,leave_id):
        leaverequest = LeaveRequest.objects.using(self._current_app_schema()).filter(id=leave_id, status=ActiveStatus.Active)
        if len(leaverequest) != 0:
            approvestatus=leaverequest[0].approve_status
            if approvestatus == LeaveApproveType.PENDING:
                return True
        else:
            return False
    def approve_status_data(self,data):
        status = int(data['status'])
        if status == LeaveApproveType.APPROVE or status == LeaveApproveType.REJECTED:
            return True
        else:
            return False
    def approve_status_update(self,user_id,data,leave_id):
        status = data['status']
        remarks = data['remarks']
        leaverequest = LeaveRequest.objects.using(self._current_app_schema()).filter(id=leave_id).update(approve_status=status,approved_by=user_id,updated_by=user_id,updated_date=timezone.now(), entity_id=self._entity_id())
        leaveapprovequeue = LeaveApproveQueue.objects.using(self._current_app_schema()).create(remarks=remarks,leave_request_id=leave_id, entity_id=self._entity_id(),created_by=user_id)
        success_obj = MessageResponse()
        success_obj.set_status(StatusType.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj
