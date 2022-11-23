import datetime
from masterservice.models.mastermodels import OrgIP, OrgDetails, AttendanceConfig, LeaveType, Holiday,OrgArcDetails
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from masterservice.service.Codegenerator import CodeGen
from django.db import IntegrityError
from django.db.models import Q
from attendanceservice.util.responsemessage import MessageResponse, StatusType
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription
from utilityservice.data.response.nwisefinsuccess import SuccessMessage
from masterservice.util.masterutil import Code_Gen_Type, Code_Gen_Value,ModifyStatus
from attendanceservice.util.attendanceutil import holiday_type_get,time_to_m_sec,date_to_m_sec
from masterservice.data.response.leaveattendanceresponse import OrgIpResponse, OrgDetailsResponse, \
    AttendanceConfigResponse, LeaveTypeResponse, HolidayResponse
from math import sin, cos, sqrt, atan2, radians


class OrgIpService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_org_ip(self, resp_obj):
        update = False
        if resp_obj.get_id() is not None:
            update = True
            try:
                ip_update = OrgIP.objects.using(self._current_app_schema()).filter(
                    id=resp_obj.get_id(), entity_id=self._entity_id()).update(ip=resp_obj.get_ip())
                # org_ip = OrgIP.objects.using(self._current_app_schema()).get(id=resp_obj.get_id(),
                #                                                              entity_id=self._entity_id())
            except IntegrityError as error:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_DATA)
                return error_obj
            except OrgIP.DoesNotExist:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_CITY_ID)
                return error_obj
            except:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                org_ip = OrgIP.objects.using(self._current_app_schema()).create(ip=resp_obj.get_ip(),org_detail_id=resp_obj.get_org_detail_id(),entity_id=self._entity_id())

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

        # data = OrgIpResponse()
        # data.set_id(org_ip.id)
        # data.set_ip(org_ip.ip)
        # data.set_status(org_ip.status)
        # data.set_org_detail_id(org_ip.org_detail_id)
        # return data
        success_obj = MessageResponse()
        success_obj.set_status(StatusType.SUCCESS)
        if update is True:
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        else:
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def org_ip_list(self, vys_page, query):
        condition = Q(entity_id=self._entity_id())
        if (query is not None) and (query != ''):
            condition &= Q(ip__icontains=str(query))
        org_ip_list = OrgIP.objects.using(self._current_app_schema()).filter(condition).order_by('id')[
                      vys_page.get_offset():vys_page.get_query_limit()]
        org_id_arr = [i.org_detail_id for i in org_ip_list]
        serv = OrgDetailsService(self._scope())
        org_detail_arr = serv.get_org_list_by_arr(org_id_arr)
        list_data = NWisefinList()
        for org_ip in org_ip_list:
            data = OrgIpResponse()
            data.set_id(org_ip.id)
            data.set_ip(org_ip.ip)
            data.set_status(org_ip.status)
            org_details = self.get_org_id_in_arr(org_ip.org_detail_id, org_detail_arr)
            data.set_org_detail_id(org_details)
            list_data.append(data)
        paginator = NWisefinPaginator(org_ip_list, vys_page.get_index(), 10)
        list_data.set_pagination(paginator)
        return list_data

    def fetch_org_ip(self, org_id):
        try:
            org_ip = OrgIP.objects.using(self._current_app_schema()).get(id=org_id, entity_id=self._entity_id())
            data = OrgIpResponse()
            data.set_id(org_ip.id)
            data.set_ip(org_ip.ip)
            data.set_status(org_ip.status)
            serv = OrgDetailsService(self._scope())
            org_details = serv.fetch_org_details(org_ip.org_detail_id)
            data.set_org_detail_id(org_details)
            return data
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj

    def delete_org_ip(self, org_id):
        try:
            ip_delete = OrgIP.objects.using(self._current_app_schema()).filter(id=org_id).delete()
            success_obj = MessageResponse()
            success_obj.set_status(StatusType.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj

    def get_org_id_in_arr(self, org_id, org_arr):
        for i in org_arr:
            if org_id == i.id:
                return i
        return None

    def bulk_create_org_ip(self, resp_obj):
        try:
            arr = []
            ip_list = resp_obj.get_ip_arr()
            for ip in ip_list:
                ip_val = str(ip['name'])
                trim_val = ip_val.strip()
                ip_data = OrgIP(ip=trim_val, org_detail_id=resp_obj.get_org_detail_id(), entity_id=self._entity_id())
                arr.append(ip_data)
            org_ip = OrgIP.objects.using(self._current_app_schema()).bulk_create(arr)
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj

        success_obj = MessageResponse()
        success_obj.set_status(StatusType.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def get_org_details_ips(self, org_id, vys_page):
        org_ip_list = OrgIP.objects.using(self._current_app_schema()).filter(org_detail_id=org_id).order_by('-id')[
                      vys_page.get_offset():vys_page.get_query_limit()]
        list_data = NWisefinList()
        for org_ip in org_ip_list:
            data = OrgIpResponse()
            data.set_id(org_ip.id)
            data.set_ip(org_ip.ip)
            data.set_status(org_ip.status)
            data.set_org_detail_id(org_ip.org_detail_id)
            list_data.append(data)
        paginator = NWisefinPaginator(org_ip_list, vys_page.get_index(), 10)
        list_data.set_pagination(paginator)
        return list_data


    def get_org_arc_info(self,arr):
        org_arc_obj = OrgArcDetails.objects.using(self._current_app_schema()).filter(id__in=arr,status=ModifyStatus.create).values('id','name')
        org_arc_list = list(org_arc_obj)
        return org_arc_list


class OrgDetailsService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_org_details(self, resp_obj, addressid,emp_id):
        update = False
        if resp_obj.get_id() is not None:
            update = True
            try:
                ip_update = OrgDetails.objects.using(self._current_app_schema()).filter(
                    id=resp_obj.get_id(), entity_id=self._entity_id()).update(latitude=resp_obj.get_latitude(),
                                                                              longitude=resp_obj.get_longitude(),
                                                                              radius=resp_obj.get_radius(),
                                                                              name=resp_obj.get_name(),
                                                                              address_id=addressid)
                # org_details = OrgDetails.objects.using(self._current_app_schema()).get(id=resp_obj.get_id(),
                #                                                                        entity_id=self._entity_id())
            except IntegrityError as error:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_DATA)
                return error_obj
            except OrgDetails.DoesNotExist:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_CITY_ID)
                return error_obj
            except:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                org_details = OrgDetails.objects.using(self._current_app_schema()).create(
                    latitude=resp_obj.get_latitude(),
                    longitude=resp_obj.get_longitude(),
                    name=resp_obj.get_name(),
                    radius=resp_obj.get_radius(),
                    address_id=addressid,
                    entity_id=self._entity_id())
                code_ger = CodeGen(self._scope())
                code = code_ger.codegenerator(Code_Gen_Type.ORG_DETAILS, self._entity_id(), emp_id,
                                              Code_Gen_Value.ORG_DETAILS)
                org_details.code = code
                org_details.save()
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

        # data = OrgDetailsResponse()
        # data.set_id(org_details.id)
        # data.set_latitude(org_details.latitude)
        # data.set_longitude(org_details.longitude)
        # data.set_name(org_details.name)
        # data.set_status(org_details.status)
        # data.set_code(org_details.code)
        # return data
        success_obj = MessageResponse()
        success_obj.set_status(StatusType.SUCCESS)
        if update is True:
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        else:
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def org_details_list(self, vys_page, query):
        condition = Q(entity_id=self._entity_id())
        if (query is not None) and (query != ''):
            condition &= Q(name__icontains=query) | Q(code__icontains=query)
        org_details_list = OrgDetails.objects.using(self._current_app_schema()).filter(condition).order_by(
            'id')[vys_page.get_offset():vys_page.get_query_limit()]
        list_data = NWisefinList()
        for org_details in org_details_list:
            data = OrgDetailsResponse()
            data.set_id(org_details.id)
            data.set_latitude(org_details.latitude)
            data.set_longitude(org_details.longitude)
            data.set_radius(org_details.radius)
            data.set_name(org_details.name)
            data.set_status(org_details.status)
            data.set_code(org_details.code)
            list_data.append(data)
        paginator = NWisefinPaginator(org_details_list, vys_page.get_index(), 10)
        list_data.set_pagination(paginator)
        return list_data

    def fetch_org_details(self, details_id):
        try:
            org_details = OrgDetails.objects.using(self._current_app_schema()).get(id=details_id,
                                                                                   entity_id=self._entity_id())
            data = OrgDetailsResponse()
            data.set_id(org_details.id)
            data.set_latitude(org_details.latitude)
            data.set_longitude(org_details.longitude)
            data.set_radius(org_details.radius)
            data.set_name(org_details.name)
            data.set_status(org_details.status)
            data.set_code(org_details.code)
            return data
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj
    def get_orgdetails_by_id(self,orgid):
        orgdetails = OrgDetails.objects.using(self._current_app_schema()).get(id=orgid)
        data = OrgDetailsResponse()
        data.set_latitude(orgdetails.latitude)
        data.set_longitude(orgdetails.longitude)
        data.set_radius(orgdetails.radius)
        data.set_name(orgdetails.name)
        return data

    def delete_org_details(self, org_id):
        try:
            details_delete = OrgDetails.objects.using(self._current_app_schema()).filter(id=org_id).delete()
            success_obj = MessageResponse()
            success_obj.set_status(StatusType.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj

    def get_org_list_by_arr(self, id_arr):
        org_details_list = OrgDetails.objects.using(self._current_app_schema()).filter(id__in=id_arr)
        list_data = []
        for org_details in org_details_list:
            data = OrgDetailsResponse()
            data.set_id(org_details.id)
            data.set_latitude(org_details.latitude)
            data.set_longitude(org_details.longitude)
            data.set_radius(org_details.radius)
            data.set_name(org_details.name)
            data.set_status(org_details.status)
            data.set_code(org_details.code)
            list_data.append(data)
        return list_data

    def create_org_arc_details(self, resp_obj, addressid, org_id):
        if resp_obj.get_id() is not None:
            org_arc_update = OrgArcDetails.objects.using(self._current_app_schema()).filter(id=resp_obj.get_id(),
                                                                                            entity_id=self._entity_id()).update(
                latitude=resp_obj.get_latitude(),
                longitude=resp_obj.get_longitude(),
                radius=resp_obj.get_radius(),
                name=resp_obj.get_name(),
                address_id=addressid)
            success_obj = MessageResponse()
            success_obj.set_status(StatusType.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj
        else:
            org_arc_create = OrgArcDetails.objects.using(self._current_app_schema()).create(
                org_id=org_id,
                latitude=resp_obj.get_latitude(),
                longitude=resp_obj.get_longitude(),
                radius=resp_obj.get_radius(),
                name=resp_obj.get_name(),
                arc_type=resp_obj.get_arc_type(),
                address_id=addressid,
                entity_id=self._entity_id())
            success_obj = MessageResponse()
            success_obj.set_status(StatusType.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return success_obj

    def fetch_org_arc_details(self, org_id):
        org_arc_details = OrgArcDetails.objects.using(self._current_app_schema()).filter(org_id=org_id,
                                                                                         status=ModifyStatus.create,
                                                                                         entity_id=self._entity_id())
        org_list_data = NWisefinList()
        for orgarc_details in org_arc_details:
            data = OrgDetailsResponse()
            data.set_id(orgarc_details.id)
            data.set_latitude(orgarc_details.latitude)
            data.set_longitude(orgarc_details.longitude)
            data.set_radius(orgarc_details.radius)
            data.set_name(orgarc_details.name)
            data.set_arc_type(orgarc_details.arc_type)
            data.set_status(orgarc_details.status)
            org_list_data.append(data)
        return org_list_data

    def org_arc_deactivate(self, org_id):
        org_arc_deactivate = OrgArcDetails.objects.using(self._current_app_schema()).filter(id=org_id).update(
            status=ModifyStatus.delete)
        success_obj = MessageResponse()
        success_obj.set_status(StatusType.SUCCESS)
        success_obj.set_message(SuccessMessage.INACTIVATED)
        return success_obj


class AttendanceConfigService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_attendance_config(self, resp_obj, emp_id):
        update = False
        if resp_obj.get_id() is not None:
            update = True
            try:
                attendance_update = AttendanceConfig.objects.using(self._current_app_schema()).filter(
                    id=resp_obj.get_id(), entity_id=self._entity_id()).update(
                    check_in_mode=resp_obj.get_check_in_mode(), namespace=resp_obj.get_namespace())
                # attendance = AttendanceConfig.objects.using(self._current_app_schema()).get(id=resp_obj.get_id(),
                #                                                                             entity_id=self._entity_id())
            except IntegrityError as error:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_DATA)
                return error_obj
            except AttendanceConfig.DoesNotExist:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_CITY_ID)
                return error_obj
            except:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                attendance = AttendanceConfig.objects.using(self._current_app_schema()).create(
                    check_in_mode=resp_obj.get_check_in_mode(),
                    entity_id=self._entity_id(), namespace=resp_obj.get_namespace())
                code_ger = CodeGen(self._scope())
                code = code_ger.codegenerator(Code_Gen_Type.ATTENDANCE_CONFIG, self._entity_id(), emp_id,
                                              Code_Gen_Value.ATTENDANCE_CONFIG)
                attendance.code = code
                attendance.save()
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

        # data = AttendanceConfigResponse()
        # data.set_id(attendance.id)
        # data.set_check_in_mode(attendance.check_in_mode)
        # data.set_namespace(attendance.namespace)
        # data.set_status(attendance.status)
        # data.set_code(attendance.code)
        # return data
        success_obj = MessageResponse()
        success_obj.set_status(StatusType.SUCCESS)
        if update is True:
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        else:
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def attendance_config_list(self, vys_page, query):
        condition = Q(entity_id=self._entity_id())
        if (query is not None) and (query != ''):
            condition &= Q(check_in_mode__icontains=query) | Q(code__icontains=query)
        attendance_config_list = AttendanceConfig.objects.using(self._current_app_schema()).filter(condition).order_by(
            'id')[vys_page.get_offset():vys_page.get_query_limit()]
        list_data = NWisefinList()
        for attendance in attendance_config_list:
            data = AttendanceConfigResponse()
            data.set_id(attendance.id)
            data.set_check_in_mode(attendance.check_in_mode)
            data.set_namespace(attendance.namespace)
            data.set_status(attendance.status)
            data.set_code(attendance.code)
            list_data.append(data)
        paginator = NWisefinPaginator(attendance_config_list, vys_page.get_index(), 10)
        list_data.set_pagination(paginator)
        return list_data

    def fetch_attendance_config(self, attendance_id):
        try:
            attendance = AttendanceConfig.objects.using(self._current_app_schema()).get(id=attendance_id,
                                                                                        entity_id=self._entity_id())
            data = AttendanceConfigResponse()
            data.set_id(attendance.id)
            data.set_check_in_mode(attendance.check_in_mode)
            data.set_namespace(attendance.namespace)
            data.set_status(attendance.status)
            data.set_code(attendance.code)
            return data
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj

    def delete_attendance_config(self, attendance_id):
        try:
            attendance_delete = AttendanceConfig.objects.using(self._current_app_schema()).filter(
                id=attendance_id).delete()
            success_obj = MessageResponse()
            success_obj.set_status(StatusType.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj

    def get_id_and_namespace(self, namespace):
        namespace = str(namespace)
        attendance = AttendanceConfig.objects.using(self._current_app_schema()).filter(namespace=namespace)
        if len(attendance) != 0:
            id_data = attendance[0].id
            return id_data
        else:
            return


class LeaveTypeService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_leave_type(self, resp_obj, emp_id):
        update = False
        if resp_obj.get_id() is not None:
            update = True
            leave_type_update = LeaveType.objects.using(self._current_app_schema()).filter(
                    id=resp_obj.get_id(), entity_id=self._entity_id()).update(name=resp_obj.get_name(),has_attendance=resp_obj.get_has_attendance(),has_salary=resp_obj.get_has_salary())
        else:
            leave_type = LeaveType.objects.using(self._current_app_schema()).create(
                name=resp_obj.get_name(),
                has_attendance=resp_obj.get_has_attendance(),
                has_salary=resp_obj.get_has_salary(),
                entity_id=self._entity_id())
            code_ger = CodeGen(self._scope())
            code = code_ger.codegenerator(Code_Gen_Type.LEAVE_TYPE, self._entity_id(), emp_id,
                                          Code_Gen_Value.LEAVE_TYPE)
            leave_type.code = code
            leave_type.save()
        success_obj = MessageResponse()
        success_obj.set_status(StatusType.SUCCESS)
        if update is True:
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        else:
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def leave_type_list(self, vys_page, query):
        condition = Q(entity_id=self._entity_id())
        if (query is not None) and (query != ''):
            condition &= Q(name__icontains=query) | Q(code__icontains=query)
        leave_type_list = LeaveType.objects.using(self._current_app_schema()).filter(condition).order_by('id')[
                          vys_page.get_offset():vys_page.get_query_limit()]
        list_data = NWisefinList()
        for leave_type in leave_type_list:
            data = LeaveTypeResponse()
            data.set_id(leave_type.id)
            data.set_name(leave_type.name)
            data.set_has_attendance(leave_type.has_attendance)
            data.set_has_salary(leave_type.has_salary)
            data.set_status(leave_type.status)
            data.set_code(leave_type.code)
            list_data.append(data)
        paginator = NWisefinPaginator(leave_type_list, vys_page.get_index(), 10)
        list_data.set_pagination(paginator)
        return list_data

    def fetch_leave_type(self, type_id):
        try:
            leave_type = LeaveType.objects.using(self._current_app_schema()).get(id=type_id,
                                                                                 entity_id=self._entity_id())
            data = LeaveTypeResponse()
            data.set_id(leave_type.id)
            data.set_name(leave_type.name)
            data.set_has_attendance(leave_type.has_attendance)
            data.set_has_salary(leave_type.has_salary)
            data.set_status(leave_type.status)
            data.set_code(leave_type.code)
            return data
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj

    def fetch_leave_type_arr(self, type_arr):
            leave_type_list = LeaveType.objects.using(self._current_app_schema()).filter(id__in=type_arr)
            list_data = []
            for leave_type in leave_type_list:
                data = LeaveTypeResponse()
                data.set_id(leave_type.id)
                data.set_name(leave_type.name)
                data.set_has_attendance(leave_type.has_attendance)
                data.set_has_salary(leave_type.has_salary)
                data.set_status(leave_type.status)
                data.set_code(leave_type.code)
                list_data.append(data)
            return list_data

    def delete_leave_type(self, type_id):
        try:
            leave_type_delete = LeaveType.objects.using(self._current_app_schema()).filter(id=type_id).delete()
            success_obj = MessageResponse()
            success_obj.set_status(StatusType.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj


class HolidayService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_holiday(self, resp_obj, emp_id):
        update = False
        if resp_obj.get_id() is not None:
            update = True
            try:
                holiday_update = Holiday.objects.using(self._current_app_schema()).filter(
                    id=resp_obj.get_id(), entity_id=self._entity_id()).update(name=resp_obj.get_name(),
                                                                              holiday_date=resp_obj.get_holiday_date(),
                                                                              type=resp_obj.get_type())
                # holiday = Holiday.objects.using(self._current_app_schema()).get(id=resp_obj.get_id(),
                #                                                                 entity_id=self._entity_id())
            except IntegrityError as error:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_DATA)
                return error_obj
            except Holiday.DoesNotExist:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_CITY_ID)
                return error_obj
            except:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                holiday = Holiday.objects.using(self._current_app_schema()).create(
                    name=resp_obj.get_name(),
                    holiday_date=resp_obj.get_holiday_date(),
                    type=resp_obj.get_type(),
                    entity_id=self._entity_id())
                code_ger = CodeGen(self._scope())
                code = code_ger.codegenerator(Code_Gen_Type.HOLIDAY, self._entity_id(), emp_id,
                                              Code_Gen_Value.HOLIDAY)
                holiday.code = code
                holiday.save()
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

        # data = HolidayResponse()
        # data.set_id(holiday.id)
        # data.set_name(holiday.name)
        # data.set_holiday_date(holiday.holiday_date)
        # data.set_type(holiday.type)
        # data.set_code(holiday.code)
        # return data
        success_obj = MessageResponse()
        success_obj.set_status(StatusType.SUCCESS)
        if update is True:
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        else:
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def holiday_list(self, vys_page, query):
        condition = Q(entity_id=self._entity_id())
        if (query is not None) and (query != ''):
            condition &= Q(name__icontains=query) | Q(code__icontains=query)
        holiday_list = Holiday.objects.using(self._current_app_schema()).filter(condition).order_by('id')[
                       vys_page.get_offset():vys_page.get_query_limit()]
        list_data = NWisefinList()
        for holiday in holiday_list:
            data = HolidayResponse()
            data.set_id(holiday.id)
            data.set_name(holiday.name)
            data.set_holiday_date(holiday.holiday_date)
            holiday_type = holiday_type_get(holiday.type)
            data.set_type(holiday_type)
            data.set_code(holiday.code)
            list_data.append(data)
        paginator = NWisefinPaginator(holiday_list, vys_page.get_index(), 10)
        list_data.set_pagination(paginator)
        return list_data

    def fetch_holiday(self, holiday_id):
        try:
            holiday = Holiday.objects.using(self._current_app_schema()).get(id=holiday_id,
                                                                            entity_id=self._entity_id())
            data = HolidayResponse()
            data.set_id(holiday.id)
            data.set_name(holiday.name)
            data.set_holiday_date(holiday.holiday_date)
            holiday_type = holiday_type_get(holiday.type)
            data.set_type(holiday_type)
            data.set_code(holiday.code)
            return data
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj

    def delete_holiday(self, holiday_id):
        try:
            holiday_delete = Holiday.objects.using(self._current_app_schema()).filter(id=holiday_id).delete()
            success_obj = MessageResponse()
            success_obj.set_status(StatusType.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj

    def get_today_holiday(self):
        holiday_list = Holiday.objects.using(self._current_app_schema()).filter(holiday_date=datetime.datetime.today(),
                                                                                entity_id=self._entity_id())
        return holiday_list

    def get_holiday_by_date(self,h_date):
        holiday_list = Holiday.objects.using(self._current_app_schema()).filter(holiday_date=h_date,entity_id=self._entity_id())
        return holiday_list

    def get_holiday_by_month(self, month, year):
        state = 1
        condition = Q(holiday_date__month=month) & Q(holiday_date__year=year) & Q(holiday_mst__state_id=state)
        holiday_details = Holiday.objects.using(self._current_app_schema()).filter(condition)
        holiday_date = []
        for i in holiday_details:
            hdetails = {"date": date_to_m_sec(i.holiday_date), "name": i.name}
            holiday_date.append(hdetails)
        return holiday_date


class CalculationService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def location_finder(self, latitude, longitude):
        location_list = OrgDetails.objects.using(self._current_app_schema()).all()
        latitude = float(latitude)
        longitude = float(longitude)
        inside = False
        base = ''
        loc_id = ''
        for location in location_list:
            center_latitude = float(location.latitude)
            center_longitude = float(location.longitude)
            radius = float(location.radius)
            v1 = (latitude - center_latitude)
            v2 = (longitude - center_longitude)
            lat_diff = (v1 * v1) + (v2 * v2)
            cent_rad = radius * radius
            if lat_diff <= cent_rad:
                inside = True
                base = location.name
                loc_id = location.id
                data = {'inside': inside, 'base': base, 'id': loc_id}
                return data
        data = {'inside': inside, 'base': base, 'id': loc_id}
        return data

    def check_ip(self, ip_code):
        ip_details = OrgIP.objects.using(self._current_app_schema()).filter(ip=str(ip_code), status=1)
        if len(ip_details) != 0:
            valid = True
            base = ip_details[0].org_detail.name
            loc_id = ip_details[0].org_detail_id
        else:
            valid = False
            base = ''
            loc_id = ''
        data = {'valid': valid, 'base': base, 'id': loc_id}
        return data

    # employee location finder
    def employee_location_finder(self, latitude, longitude,org_id):
        location_list = OrgArcDetails.objects.using(self._current_app_schema()).filter(org_id=org_id,status=ModifyStatus.create)
        if len(location_list ) == 0:
            d={"status":False,"msg":"Employee Org mapping missing"}
            return d

        for  location in location_list:
            # approximate radius of earth in km
            R = 6373.0
            # location = location_list[0]
            print(location)
            lat1 = radians(latitude)
            lon1 = radians(longitude)
            lat2 = radians(float(location.latitude))
            lon2 = radians(float(location.longitude))

            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distance = (R * c)*1000
            org_radius =int(location.radius)
            print('org_radius',org_radius)
            print('distance',distance)
            if org_radius > distance:
                d = {"status": True, "msg": "Location IN","location":location.name,"org_arc_id":location.id}

                return d


        d = {"status": False, "msg": "Location out of range","location":None,"org_arc_id":None}
        return d
