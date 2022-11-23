import json
from datetime import datetime
import requests
from django.db import IntegrityError
from taservice.data.request.employeemaping import EmployeemappingRequest
from taservice.data.request.glmap_req import Dependent_req
from taservice.data.response.employeemapping import EmployeemappingResponse
from taservice.data.response.glmap_res import Dependent_res
from taservice.models import Employeemapping, Dependent, Traveldependent
# from taservice.service.emp_name_get import emp_dtl
from taservice.util.ta_util import Validation
# from userservice.controller.authcontroller import UserLogin_scheduler
from nwisefin import settings
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.data.response.nwisefinlist  import NWisefinList
# from utilityservice.service.dbutil import DataBase

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.ta_api_service import ApiService

from utilityservice.service.threadlocal import NWisefinThread
class EmployeemappingData(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)
    def create_employeemapping(self, request_obj):
        for dtl in request_obj:
            data = EmployeemappingRequest(dtl)
            if data.get_gid() is not None:
                try:
                    employeemappingdata = Employeemapping.objects.using(self._current_app_schema()).filter(gid=data.get_gid()).update(designation=data.get_designation(),
                                                                                  grade=data.get_grade(),
                                                                                  orderno=data.get_orderno(),
                                                                                  status=data.get_status(),entity_id=self._entity_id())

                except Exception as e:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(str(e))
                    return error_obj
                # except IntegrityError as error:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj
                # except Employeemapping.DoesNotExist:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj
                # except:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                #     return error_obj


                # success_obj = NWisefinSuccess()
                # success_obj.set_status(SuccessStatus.SUCCESS)
                # success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                # return success_obj
            else:
                try:
                    employeemappimgdata = Employeemapping.objects.using(self._current_app_schema()).create(designation=data.get_designation(),
                                                                         grade=data.get_grade(),
                                                                         orderno=data.get_orderno(),
                                                                         status=data.get_status(),entity_id=self._entity_id())

                except Exception as e:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(str(e))
                    return error_obj
                # except IntegrityError as error:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj
                # except:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                #     return error_obj
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj
    def get_employeemapping(self):
        employeemapping = Employeemapping.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).all()
        resp_list = EmployeemappingResponse()
        arr = []
        for i in employeemapping:
            req_data = EmployeemappingResponse()
            req_data.set_gid(i.gid)
            req_data.set_designation(i.designation)
            req_data.set_grade(i.grade)
            req_data.set_orderno(i.orderno)
            req_data.set_status(i.status)
            arr.append(json.loads(req_data.get()))
        resp_list.set_data(arr)
        return resp_list
    def delete_employeemapping(self,delete_id):
        try:
            employeemapping = Employeemapping.objects.using(self._current_app_schema()).get(gid=delete_id,entity_id=self._entity_id()).delete()
        # except IntegrityError as error:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.INVALID_DATA)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
        #     return error_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj
    def get_employeemapping_id(self,fetchgid):
        employeemapping = Employeemapping.objects.using(self._current_app_schema()).get(gid=fetchgid,entity_id=self._entity_id())
        req_data = EmployeemappingResponse()
        req_data.set_gid(employeemapping.gid)
        req_data.set_designation(employeemapping.designation)
        req_data.set_grade(employeemapping.grade)
        req_data.set_orderno(employeemapping.orderno)
        req_data.set_status(employeemapping.status)
        return req_data

    def get_emp_designation(self,designation):
        employeemapping = Employeemapping.objects.using(self._current_app_schema()).filter(designation=designation,entity_id=self._entity_id())
        arr=[]
        for empmap in employeemapping:
            req_data = EmployeemappingResponse()
            req_data.set_gid(empmap.gid)
            req_data.set_designation(empmap.designation)
            req_data.set_grade(empmap.grade)
            req_data.set_orderno(empmap.orderno)
            req_data.set_status(empmap.status)
            arr.append(req_data)
        return arr

    def dependencies(self,jsondata,employee_id):
        success_obj = NWisefinSuccess()
        for data in jsondata['data']:
            detail=Dependent_req(data)
            if detail.id is None:
                Dependent.objects.using(self._current_app_schema()).create(depname=detail.depname,deprelation=detail.deprelation,depempid=detail.depempid,
                                         created_by=employee_id,created_date=datetime.now(),entity_id=self._entity_id())
                success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            else:
                Dependent.objects.using(self._current_app_schema()).filter(id=detail.id).update(depname=detail.depname, deprelation=detail.deprelation,
                                         depempid=detail.depempid,
                                         updated_by=employee_id, updated_date=datetime.now(),entity_id=self._entity_id())
                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        success_obj.set_status(SuccessStatus.SUCCESS)
        return success_obj

    def get_all_dependencies(self):
        dep_list = Dependent.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).all()
        resp_list =  NWisefinList()
        for dep in dep_list:
            req_data = Dependent_res()
            req_data.set_id(dep.id)
            req_data.set_depname(dep.depname)
            req_data.set_deprelation(dep.deprelation)
            req_data.set_depempid(dep.depempid)
            resp_list.append(req_data)
        return resp_list

    def travel_dependencies(self,jsondata,employee_id):
        success_obj = NWisefinSuccess()
        for data in jsondata['data']:
            detail = Dependent_req(data)
            if detail.id is None:
                Traveldependent.objects.using(self._current_app_schema()).create(tour_id=detail.tour_id,claimreq_id=detail.claimreq_id,travel_id=detail.travel_id,empid=detail.empid,dependentid=detail.dependentid,
                                         dependentname=detail.dependentname,deprelation=detail.deprelation,
                                         isdepelig=detail.isdepelig,created_by=employee_id,created_date=datetime.now(),entity_id=self._entity_id())
                success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            else:
                Traveldependent.objects.using(self._current_app_schema()).filter(id=detail.id).update(tour_id=detail.tour_id,claimreq_id=detail.claimreq_id,travel_id=detail.travel_id,empid=detail.empid,dependentid=detail.dependentid,
                                         dependentname=detail.dependentname,deprelation=detail.deprelation,
                                         isdepelig=detail.isdepelig,updated_by=employee_id,updated_date=datetime.now(),entity_id=self._entity_id())
                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        success_obj.set_status(SuccessStatus.SUCCESS)
        return success_obj

    def get_all_travel_dependencies(self):
        dep_list = Traveldependent.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).all()
        resp_list =  NWisefinList()
        for dep in dep_list:
            req_data = Dependent_res()
            req_data.set_id(dep.id)
            req_data.set_tour_id(dep.tour_id)
            req_data.set_claimreq_id(dep.claimreq_id)
            req_data.set_travel_id(dep.travel_id)
            req_data.set_empid(dep.empid)
            req_data.set_dependentid(dep.dependentid)
            req_data.set_dependentname(dep.dependentname)
            req_data.set_deprelation(dep.deprelation)
            req_data.set_isdepelig(dep.isdepelig)
            resp_list.append(req_data)
        return resp_list

    def get_travel_dependencies_id(self,travel_id,employee_id):
        tour_data=((Traveldependent.objects.using(self._current_app_schema()).filter(travel_id=travel_id,entity_id=self._entity_id())).first())
        if tour_data is not None:
            tour_id=tour_data.tour_id
            service = Validation(self._scope())
            permission = service.permisssion_check(tour_id, employee_id)
            if permission is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.VALID_USER)
                return error_obj

        dep_list = Traveldependent.objects.using(self._current_app_schema()).filter(travel_id=travel_id,entity_id=self._entity_id())
        resp_list =  NWisefinList()
        for dep in dep_list:
            req_data = Dependent_res()
            req_data.set_id(dep.id)
            req_data.set_tour_id(dep.tour_id)
            req_data.set_claimreq_id(dep.claimreq_id)
            req_data.set_travel_id(dep.travel_id)
            req_data.set_empid(dep.empid)
            req_data.set_dependentid(dep.dependentid)
            req_data.set_dependentname(dep.dependentname)
            req_data.set_deprelation(dep.deprelation)
            req_data.set_isdepelig(dep.isdepelig)
            resp_list.append(req_data)
        return resp_list

    def delete_depenceies_id(self,id,employee_id):
        try:
            tour_id=(Traveldependent.objects.using(self._current_app_schema()).get(id=id,entity_id=self._entity_id())).tour_id
            service = Validation(self._scope())
            permission = service.tour_maker_check(tour_id, employee_id)
            if permission is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.VALID_USER)
                return error_obj
            Traveldependent.objects.using(self._current_app_schema()).get(id=id,entity_id=self._entity_id()).delete()
            msg_obj = NWisefinSuccess()
            msg_obj.set_status(SuccessMessage.DELETE_MESSAGE)
            msg_obj.set_message({"id": id})
            return msg_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj



    # 17/1travel dependencies data format changes
    def get_dependencies(self,emp_id,request):
        employee_detail=ApiService(self._scope())
        employee_code=str((employee_detail.employee_details_get(emp_id,request)).code)
        if employee_code[0:2].upper() == 'VS':
            dep_list= Dependent.objects.using(self._current_app_schema()).filter(depempid=emp_id,entity_id=self._entity_id())
            resp_list = Dpendata_vysfinlist()
            for dep in dep_list:
                req_data = Dependent_res()
                req_data.set_id(dep.id)
                req_data.set_empid(emp_id)
                req_data.set_dependentname(dep.depname)
                req_data.set_deprelation(dep.deprelation)
                req_data.set_dependentid(dep.depempid)
                req_data.set_isdepelig(1)
                resp_list.append(req_data)
            return resp_list
        else:

            # token_service=ApiService()
            token = self.UserLogin_scheduler()
            client_api = settings.CLIENT_URL
            apiname = 'EMCUSER'
            apipassword = '9f'
            headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token}

            employee_code = "003443"
            data_depent = {
                "UserName": apiname,
                "Password": apipassword,
                "EmpId": str(employee_code),
                "DtlsToBeFetch": "DependentDetails"
            }
            data_depent = json.dumps(data_depent)
            result = requests.post("" + client_api + "/next/v1/mw/employee-detail", headers=headers,
                                    data=data_depent,
                                    verify=False)
            results_data = json.loads(result.content.decode("utf-8"))
            status = results_data.get("out_msg").get("ErrorMessage")
            if (status == "Success"):
                data_dependent = results_data.get("out_msg").get('item')
                for i in data_dependent:
                    i['empid'] = emp_id
                    i['dependentname'] = i.get('FamilyMemberName')
                    i['deprelation'] = i.get('FamilyMemberRelation')
                    i['dependentid'] = int(i.get('FamilyMemberId'))
                    i["isdepelig"] =1
                ld_dict = {"DATA": data_dependent,
                           "MESSAGE": 'FOUND'}
                return (ld_dict)

    # 13/1 UserLogin_scheduler-Ste
    def UserLogin_scheduler(self):
        client_url = settings.CLIENT_URL
        url = client_url + str("next//v1/oauth/cc/accesstoken")
        #     url = settings.ADURL_ACCESS

        entity_id = settings.ADURL_KEY
        client_secret = settings.CLIENT_SECRET
        grant_type = 'client_credentials'
        response = requests.post(url, auth=(entity_id, client_secret),
                                 data={'grant_type': grant_type, 'entity_id': entity_id,
                                       'client_secret': client_secret})
        datas = json.loads(response.content.decode("utf-8"))
        access_token = datas.get("access_token")
        print('Token---->', access_token)
        return access_token

import json

class Dpendata_vysfinlist:
    DATA = []
    pagination = None
    count=None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def __init__(self):
        self.DATA = []

    def append(self, obj):
        self.DATA.append(obj)







