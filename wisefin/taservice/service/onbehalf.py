from datetime import datetime

import pytz
from django.db.models import Q

from nwisefin.settings import logger
from taservice.data.request.onbehalfrequest import Onbehalfrequest
from taservice.data.response.onbehalfresponse import Onbehalfresponse, Ccbs_resp
from taservice.models.tamodels import Onbehalfof, TravelHistory,Ccbs
# from taservice.service.emp_name_get import emp_dtl
from taservice.util.ta_util import Filterstatus ,Timecalculation
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants  import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess, SuccessStatus, SuccessMessage
from django.db import IntegrityError, transaction
import json
from django.utils import timezone
from utilityservice.data.response.nwisefinlist  import NWisefinList
# from utilityservice.service.dbutil import DataBase
from utilityservice.service.ta_api_service import ApiService
from utilityservice.data.response.nwisefinpaginator  import NWisefinPaginator
# IST = pytz.timezone('Asia/Kolkata')
# datetime_ist = datetime.now(IST)
# today = datetime_ist.strftime('%Y-%m-%d %H:%M:%S')
time_function=Timecalculation()
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
class Onbehalf_service(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)
    def insert_onbehalfof(self,request_obj,user_id):
        success_obj = NWisefinSuccess()
        logger.info('ta_ insert_onbehalfof- ' + str(user_id) + str(request_obj))
        for dtl in request_obj:
            request = Onbehalfrequest(dtl)
            if request.get_id() is not None:
                try:
                    # 13/1 onbehalfof duplicate entry check Ste
                    onb_present_data = self.onbehalf_present_check(request.get_employeegid(),
                                                                   request.get_onbehalf_employeegid(),request.get_branchgid())
                    if request.get_employeegid()==request.get_onbehalf_employeegid():
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.INVALID_DATA)
                        error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
                        return error_obj
                    if onb_present_data is False:
                        onbehalf = Onbehalfof.objects.using(self._current_app_schema()).filter(id=request.get_id(),entity_id=self._entity_id()).update(employeegid = request.get_employeegid(),
                                                                                        branchgid = request.get_branchgid(),
                                                                                        onbehalf_employeegid = request.get_onbehalf_employeegid(),
                                                                                        updated_by = user_id,
                                                                                        updated_date=timezone.now(),entity_id=self._entity_id())

                        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                    else:

                        success_obj.set_message("ALREADY CREATED")

                except IntegrityError as error:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
                except Onbehalfof.DoesNotExist:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                    error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                    return error_obj
                except:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
                # success_obj = NWisefinSuccess()
                # success_obj.set_status(SuccessStatus.SUCCESS)
                # success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                # return success_obj
            else:
                try:
                    onb_present_data=self.onbehalf_present_check( request.get_employeegid(), request.get_onbehalf_employeegid(),request.get_branchgid())
                    if request.get_employeegid()==request.get_onbehalf_employeegid():
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.INVALID_DATA)
                        error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
                        return error_obj
                    if onb_present_data is False:
                        onbehalf = Onbehalfof.objects.using(self._current_app_schema()).create( employeegid = request.get_employeegid(),
                                                                 branchgid=request.get_branchgid(),
                                                                 onbehalf_employeegid=request.get_onbehalf_employeegid(),
                                                                 created_by = user_id,entity_id=self._entity_id())

                        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                    else:

                        success_obj.set_message("ALREADY CREATED")

                    # resp_list = Approveresponse()
                    # resp_list.set_branchid(approve.branchid)
                    # return resp_list



                except IntegrityError as error:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
                except Exception as e:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(str(e))
                    return error_obj

        success_obj.set_status(SuccessStatus.SUCCESS)
        return success_obj
        # print("issue")

    def onbehalf_present_check(self,empid,onbid,branch):
        onbehalf_data=Onbehalfof.objects.using(self._current_app_schema()).filter(employeegid=empid,onbehalf_employeegid=onbid,branchgid=branch,entity_id=self._entity_id())
        return bool(len(onbehalf_data))

    def get_onbehalfof(self,vys_page,request):
        onbehalf = Onbehalfof.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).all()[vys_page.get_offset():vys_page.get_query_limit()]
        req_data = Onbehalfresponse()
        empdtl = ApiService(self._scope())
        res_list=NWisefinList()
        for i in onbehalf:
            resp_list = Onbehalfresponse()
            resp_list.set_id(i.id)
            employee_name = empdtl.employee_details_get(i.employeegid, request)
            branch_name=empdtl.get_branch_data(i.branchgid,request)
            onbehalf_name=empdtl.employee_details_get(i.onbehalf_employeegid,request)
            resp_list.set_employee_name(employee_name.full_name)
            resp_list.set_branch_name(branch_name.name)
            resp_list.set_onbehalf_employee_name(onbehalf_name.full_name)
            resp_list.set_status(i.status)
            res_list.append(json.loads(resp_list.get()))
        req_data.set_data(res_list)

        vpage = NWisefinPaginator(onbehalf, vys_page.get_index(), 10)
        res_list.set_pagination(vpage)
        return res_list
        # print("issue")

    def delete_onbehalfof(self, delete_id):
        try:
            onbehalf = Onbehalfof.objects.using(self._current_app_schema()).get(id=delete_id,entity_id=self._entity_id()).delete()
        except IntegrityError as error:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj
        # print("issue")

    def get_onbehalfof_byid(self,employee_id):
        onbehalf = Onbehalfof.objects.using(self._current_app_schema()).get(id = employee_id,entity_id=self._entity_id())
        resp_list = Onbehalfresponse()
        resp_list.set_id(onbehalf.id)
        resp_list.set_employeegid(onbehalf.employeegid)
        resp_list.set_branchgid(onbehalf.branchgid)
        resp_list.set_onbehalf_employeegid(onbehalf.onbehalf_employeegid)
        return resp_list

    def branch_based_onb_get(self,request,branch,employee_id,vys_page,maker):
        common_service=ApiService(self._scope())
        employee_data=common_service.branch_employee_get(branch,vys_page,request,maker)

        for each_employee in employee_data['data']:
            onb_header_id=0
            if type(each_employee)==dict:
                ta_onb_status = 0
                present_status=0
                onbehalf_status=Onbehalfof.objects.using(self._current_app_schema()).filter(branchgid=branch, onbehalf_employeegid=employee_id,employeegid=each_employee['id'],entity_id=self._entity_id()).first()
                if onbehalf_status is not None:
                    present_status=1
                    ta_onb_status=onbehalf_status.status
                    onb_header_id=onbehalf_status.id
                each_employee['ta_onb_status']=ta_onb_status
                each_employee['onb_header_id']=onb_header_id
                each_employee['onb_present_status']=present_status
            else:
                ta_onb_status = 0
                present_status=0
                onbehalf_status=Onbehalfof.objects.using(self._current_app_schema()).filter(branchgid=branch, onbehalf_employeegid=employee_id,employeegid=each_employee.id,entity_id=self._entity_id()).first()
                if onbehalf_status is not None:
                    present_status = 1
                    ta_onb_status=onbehalf_status.status
                    onb_header_id = onbehalf_status.id
                each_employee.ta_onb_status=ta_onb_status
                each_employee.onb_header_id=onb_header_id
                each_employee.onb_present_status=present_status

        req_data = Onbehalfresponse()
        empdtl = ApiService(self._scope())
        res_list = VysfinList_onb()
        if type(employee_data['data'][0]) ==dict:
            for i in employee_data['data']:
                resp_list = Onbehalfresponse()
                employee_name = empdtl.employee_details_get(i['id'], request)
                resp_list.set_employee(employee_name)
                resp_list.set_status(i['ta_onb_status'])
                resp_list.set_onb_header_id(i['onb_header_id'])
                resp_list.set_onb_present_status(i['onb_present_status'])
                res_list.append(json.loads(resp_list.get()))
            req_data.set_data(res_list)

            res_list.set_pagination(employee_data['pagination'])
            return res_list
        else:
            res_list = NWisefinList()
            for i in employee_data['data']:
                resp_list = Onbehalfresponse()
                employee_name = empdtl.employee_details_get(i.id, request)
                resp_list.set_employee(employee_name)
                resp_list.set_status(i.ta_onb_status)
                resp_list.set_onb_header_id(i.onb_header_id)
                resp_list.set_onb_present_status(i.onb_present_status)
                res_list.append(json.loads(resp_list.get()))
            req_data.set_data(res_list)

            res_list.set_pagination(employee_data['pagination'])
            return res_list


    @transaction.atomic
    def insert_Ccbs(self,request,user_id,req_id,type):
        success_obj = NWisefinSuccess()
        for request_obj in request:
            if 'id' in request_obj:
                # try:
                ccbs = Ccbs.objects.using(self._current_app_schema()).filter(id=request_obj['id'],entity_id=self._entity_id()).update(tour_id = request_obj['tourgid'],
                                                                        # requestid = req_id,
                                                                        ccid = request_obj['ccid'],
                                                                        bsid = request_obj['bsid'],
                                                                        percentage = round(float(request_obj['percentage']),2),
                                                                        amount = round(float(request_obj['amount']),2),
                                                                        status = 1,
                                                                        ccbs_type = type,
                                                                        updated_by=user_id,
                                                                        updated_date=timezone.now(),entity_id=self._entity_id())



                # except IntegrityError as error:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj
                # except Ccbs.DoesNotExist:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                #     error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                #     return error_obj
                # except:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                #     return error_obj
                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            else:
                # try:

                ccbs = Ccbs.objects.using(self._current_app_schema()).create(tour_id=request_obj['tourgid'],
                                           requestid=req_id,
                                           ccid=request_obj['ccid'],
                                           bsid=request_obj['bsid'],
                                           percentage=round(float(request_obj['percentage']),2),
                                           amount=round(float(request_obj['amount']),2),
                                           ccbs_type=type,
                                           created_by=user_id,entity_id=self._entity_id())

                # except IntegrityError as error:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj
                # except Exception as e:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                #     return error_obj

                success_obj.set_message(SuccessMessage.CREATE_MESSAGE)

        success_obj.set_status(SuccessStatus.SUCCESS)
        return success_obj

    def ccbs_id_tour_id_check(self,ccbs_data,tour_id):
        tour_id=int(tour_id)
        if tour_id==0:
            for data in ccbs_data:
                if "id" in data:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.WITHOUT_CCBSID)
                    return error_obj


        elif tour_id>0:
            for data in ccbs_data:
                if 'id' in data:
                    amt_data=Ccbs.objects.using(self._current_app_schema()).get(id=data['id'],entity_id=self._entity_id())
                    if amt_data.tour_id!=tour_id:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        error_obj.set_description(ErrorDescription.INVALID_ID)
                        return error_obj
        return True



    def onbehalf_ifpresent(self,request_obj,user_id):
        onbehalf = Onbehalfof.objects.using(self._current_app_schema()).get(onbehalf_employeegid = user_id,
                                          branchgid =request_obj['branchgid'] ,status = request_obj['status'],entity_id=self._entity_id())
        resp_list = Onbehalfresponse()
        resp_list.set_id(onbehalf.id)
        resp_list.set_employeegid(onbehalf.employeegid)
        resp_list.set_branchgid(onbehalf.branchgid)
        resp_list.set_onbehalf_employeegid(onbehalf.onbehalf_employeegid)
        return resp_list


    def onbehalf_ifnotpresent(self,request_obj,user_id):
        onbehalf = Onbehalfof.objects.using(self._current_app_schema()).get(onbehalf_employeegid = user_id,status = request_obj['status'],entity_id=self._entity_id())
        resp_list = Onbehalfresponse()
        resp_list.set_id(onbehalf.id)
        resp_list.set_employeegid(onbehalf.employeegid)
        resp_list.set_branchgid(onbehalf.branchgid)
        resp_list.set_onbehalf_employeegid(onbehalf.onbehalf_employeegid)
        return resp_list


    def nac_onbehalf_emp_get_check(self, employee_id, request, query, vys_page):
        onb=self.nac_onbehalf_emp_get(employee_id, request, query, vys_page)
        if len(onb.data)>0:
            return json.dumps({"onbehalf":True})
        else:
            return json.dumps({"onbehalf":False})


    def nac_onbehalf_emp_get(self, employee_id, request, query, vys_page):
        api_service=ApiService(self._scope())
        onb_permission_ck=api_service.onb_permission(request, employee_id)
        onb_permission_ck=json.loads(onb_permission_ck)
        if onb_permission_ck["ceo"]==True or onb_permission_ck["admin"]==True or onb_permission_ck["hr"]==True:
            resp_list=api_service.all_emp_list(request, query, vys_page,[employee_id])
            return resp_list
        else:
            # condition = None
            # if query is not None:
            #     condition = (Q(full_name__icontains=query) | Q(code__icontains=query) | Q(
            #         designation__icontains=query)) & Q(status=1)
            # employeeList = None
            # if condition is not None:
            #     employee_list = Onbehalfof.objects.using(self._current_app_schema()).filter(onbehalf_employeegid=employee_id,
            #                                                                 status=Filterstatus.one,entity_id=self._entity_id()).all()[
            #                 vys_page.get_offset():vys_page.get_query_limit()]
            # else:
            employee_list = Onbehalfof.objects.using(self._current_app_schema()).filter(onbehalf_employeegid=employee_id,
                                                                        status=Filterstatus.one,entity_id=self._entity_id()).all()[
                        vys_page.get_offset():vys_page.get_query_limit()]
            vlist = NWisefinList()
            for employee in employee_list:
                emp_resp =Onbehalfresponse()
                empdtl = ApiService(self._scope())
                employee = empdtl.employee_details_get(employee.employeegid, request)
                disp_name = '(' + employee.code + ') ' + employee.full_name
                emp_resp.set_full_name(disp_name)
                emp_resp.set_employee_name(employee.full_name)
                emp_resp.set_code(employee.code)
                emp_resp.set_branch_code(None)
                emp_resp.set_branch_id(employee.employee_branch_id)
                emp_resp.set_branch_name(employee.employee_branch_name)
                emp_resp.set_id(employee.id)
                # emp_resp.set_employee_data(employee)
                if employee.full_name is not None:
                    if query is not None:
                        if query.lower() in employee.full_name.lower():
                            vlist.append(emp_resp)
                    else:
                        vlist.append(emp_resp)
                # vlist.append(emp_resp)
            vpage = NWisefinPaginator(employee_list, vys_page.get_index(), 10)
            vlist.set_pagination(vpage)
            return vlist

            # employee_list = Onbehalfof.objects.using(self._current_app_schema()).filter(onbehalf_employeegid=employee_id,
            #                                                                 status=Filterstatus.one,entity_id=self._entity_id()).all()[
            #                 vys_page.get_offset():vys_page.get_query_limit()]
            # res_list = NWisefinList()
            # for onbehalf in employee_list:
            #     resp_list = Onbehalfresponse()
            #     resp_list.set_employeegid(onbehalf.employeegid)
            #     resp_list.set_onbehalf_employeegid(onbehalf.onbehalf_employeegid)
            #     empdtl = ApiService(self._scope())
            #     employee = empdtl.employee_details_get(onbehalf.employeegid, request)
            #     resp_list.set_employee_name(employee.full_name)
            #     resp_list.set_employee_data(employee)
            #     onb_name = empdtl.employee_details_get(onbehalf.onbehalf_employeegid, request)
            #     resp_list.set_onbehalf_employee_name(onb_name.full_name)
            #     resp_list.set_onbehalf_employee_data(onb_name)
            #     if employee.full_name is not None:
            #         if query is not None:
            #             if query.lower() in employee.full_name:
            #                 res_list.append(resp_list)
            #         else:
            #             res_list.append(resp_list)
            #
            # # req_data.set_data(res_list)
            #
            # vpage = NWisefinPaginator(employee_list, vys_page.get_index(), 10)
            # res_list.set_pagination(vpage)
            # return res_list

    def onbehalf_emp_get(self,user_id,request):
        employee = Onbehalfof.objects.using(self._current_app_schema()).filter(onbehalf_employeegid = user_id ,status = Filterstatus.one,entity_id=self._entity_id()).all()
        # arr=[]
        # for onbehalf in employee:
        #     resp_list = Onbehalfresponse()
        #     resp_list.set_employeegid(onbehalf.employeegid)
        #     resp_list.set_onbehalf_employeegid(onbehalf.onbehalf_employeegid)
        #     empdtl = ApiService()
        #     employee = empdtl.employee_details_get(onbehalf.employeegid, request)
        #     resp_list.set_employee_name(employee.full_name)
        #     onb_name = empdtl.employee_details_get(onbehalf.onbehalf_employeegid, request)
        #     resp_list.set_onbehalf_employee_name(onb_name.full_name)
        #     arr.append(resp_list)
        # return arr

        resp_list = Onbehalfresponse()
        resp_list.set_status(bool(len(employee)))
        return resp_list

    def onbehalf_emp_get_branch(self,user_id,branch,request,query,vys_page):
        employee_list = Onbehalfof.objects.using(self._current_app_schema()).filter(onbehalf_employeegid = user_id,branchgid=branch ,status = Filterstatus.one,entity_id=self._entity_id()).all()[vys_page.get_offset():vys_page.get_query_limit()]
        arr=[]
        req_data = Onbehalfresponse()

        res_list = NWisefinList()
        for onbehalf in employee_list:
            resp_list = Onbehalfresponse()
            resp_list.set_employeegid(onbehalf.employeegid)
            resp_list.set_onbehalf_employeegid(onbehalf.onbehalf_employeegid)
            empdtl = ApiService(self._scope())
            employee = empdtl.employee_details_get(onbehalf.employeegid, request)
            resp_list.set_employee_name(employee.full_name)
            resp_list.set_employee_code(employee.code)
            onb_name = empdtl.employee_details_get(onbehalf.onbehalf_employeegid, request)
            resp_list.set_onbehalf_employee_name(onb_name)
            res_list.append(json.loads(resp_list.get()))
        req_data.set_data(res_list)

        vpage = NWisefinPaginator(employee_list, vys_page.get_index(), 10)
        res_list.set_pagination(vpage)
        return res_list

    def update_approvedby(self,request_obj):
        onbehalf = TravelHistory.objects.using(self._current_app_schema()).filter(id = request_obj['id']).update(tour_id = request_obj['tour_id'], approveddate=time_function.ist_time(), entity_id=self._entity_id())
        return request_obj['id']
    def update_status(self,id,status):
        success_obj = NWisefinSuccess()

        try:
            Onbehalfof.objects.using(self._current_app_schema()).get(id=id,entity_id=self._entity_id())
            onbehalf_status=Onbehalfof.objects.using(self._current_app_schema()).filter(id=id,entity_id=self._entity_id()).update(status=status,entity_id=self._entity_id())
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            success_obj.set_status(SuccessStatus.SUCCESS)
            return success_obj
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
            return error_obj

from django.template.defaultfilters import length
class VysfinList_onb:
    data = []
    pagination = None
    count = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def __init__(self):
        self.data = []

    def append(self, obj):
        self.data.append(obj)

    def set_pagination(self, pagination):
        self.pagination = pagination
        if length(self.data) > pagination['limit']:
            self.data.pop()

    def get_pagination(self):
        return self.pagination