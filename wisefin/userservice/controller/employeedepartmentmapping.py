import requests
import json
from requests.auth import HTTPBasicAuth
from userservice.models import Employee ,EmployeeDepartmentPermission,Department , EmployeeBranch
from datetime import datetime
from django.db.models import Q
from django.conf import settings
from nwisefin.settings import logger
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace


class EmpSync(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.USER_SERVICE)

    token = None

    def get_token(self):
        client_url = settings.CLIENT_URL
        token_url = client_url + str("next//v1/oauth/cc/accesstoken")
        # token_url = settings.ADURL_ACCESS
        logger.info("token url "+str(token_url))
        token_data = {"grant_type": "client_credentials"}
        token_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        token = requests.post(token_url, data=token_data, headers=token_headers, verify=False,
                              auth=HTTPBasicAuth(settings.ADURL_KEY, settings.CLIENT_SECRET))
        token_json = json.loads(token.text)
        token = token_json.get('access_token')
        return token

    def retry_emp_info(self, emp_code):
        client_url = settings.CLIENT_URL
        emp_get_url = client_url + str("next/v1/mw/employee-detail")
        # emp_get_url = settings.EMPLOYEEDETAIL_URL
        emp_data = {
            "UserName": settings.EMPUSER_EMPLOYEE_NAME,
            "Password": settings.EMCUSER_EMPLOYEE_PASSWORD,
            "EmpId": str(emp_code),
            "DtlsToBeFetch": "BaseDetails"
        }
        emp_data = json.dumps(emp_data)
        emp_headers = {'Authorization': 'Bearer ' + self.token}
        data = None
        try:
            req_obj = requests.post(emp_get_url, data=emp_data, headers=emp_headers,verify=False)
            logger.info(str(req_obj.status_code))
            if req_obj.status_code == 200:
                resp_json = json.loads(req_obj.text)
                data = resp_json.get('out_msg')
                logger.info("emp_data "+str(data))
        except:
            logger.info("invalid employee code")
        return data

    def get_emp_info(self, emp_code):
        if self.token == None:
            self.token = self.get_token()
        client_url = settings.CLIENT_URL
        emp_get_url = client_url + str("next/v1/mw/employee-detail")
        # emp_get_url = settings.EMPLOYEEDETAIL_URL
        emp_data = {
            "UserName": settings.EMPUSER_EMPLOYEE_NAME,
            "Password": settings.EMCUSER_EMPLOYEE_PASSWORD,
            "EmpId": str(emp_code),
            "DtlsToBeFetch": "BaseDetails"
        }
        emp_data = json.dumps(emp_data)
        emp_headers = {'Authorization': 'Bearer ' + self.token}
        data = None
        try:
            req_obj = requests.post(emp_get_url, data=emp_data, headers=emp_headers,verify=False)
            logger.info(str(req_obj.status_code))
            if req_obj.status_code == 200:
                resp_json = json.loads(req_obj.text)
                data = resp_json.get('out_msg')
                logger.info("emp_data "+str(data))
            elif req_obj.status_code == 401 or req_obj.status_code == 403 or req_obj.status_code == 500:
                self.token = self.get_token()
                data = self.retry_emp_info(emp_code)
        except:
            logger.info("invalid employee code")
        return data


    def empl_dept_mapping(self):
        emp_data = Employee.objects.all()
        arr_id=[]
        arr_code=[]
        for emp in emp_data:
            emp_code = emp.code
            emp_id = emp.id
            data = self.get_emp_info(emp_code)
            edept = data.get('eDept')
            designation = data.get('edesig')
            ebranch = data.get('eBranch')
            if edept is None:
                arr_id.append(emp_id)
                arr_code.append(emp_code)
                continue
            else:
                pass

            if edept == ebranch:
                department_id = self.isdepartment_present(edept)
                self.emp_dept_check(emp_id,department_id)

            else :
                department_id = self.isdepartment_present(ebranch)
                self.emp_dept_check(emp_id, department_id)


            Employee.objects.filter(id=emp_id).update(designation=designation,lastsync_date=datetime.now())
        logger.info("arr_code "+str(arr_code))
        return



    def emp_dept_check(self,emp_id,dept_id):
        condition = Q(employee_id=emp_id) & Q(department_id=dept_id) &Q(entity_id=self._entity_id())
        emp_dept = EmployeeDepartmentPermission.objects.filter(condition)

        if len(emp_dept)>0 :
            pass
        else:
            emp_dept = EmployeeDepartmentPermission.objects.create(employee_id=emp_id,department_id=dept_id,isadmin =True, entity_id=self._entity_id())

        return


    def isdepartment_present(self,dep_name):
        branch = EmployeeBranch.objects.using(self._current_app_schema()).get(code=dep_name, entity_id=self._entity_id())
        branch_name = branch.name
        try:
            dept=Department.objects.using(self._current_app_schema()).get(name = branch_name, entity_id=self._entity_id())
            return dept.id
        except:
            dept=Department.objects.using(self._current_app_schema()).create(name = branch_name,is_sys=True, entity_id=self._entity_id())
            code = "DGRP" + str(dept.id)
            dept.code = code
            dept.save()
            return dept.id

    #  excel load

    def emp_dept_per(self,emp_id,dept_id):
        condition = Q(employee_id=emp_id) & Q(department_id=dept_id) &Q(entity_id=self._entity_id())
        emp_dept = EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(condition)
        if len(emp_dept)>0 :
            pass
        else:
            emp_dept = EmployeeDepartmentPermission.objects.using(self._current_app_schema()).create(employee_id=emp_id,department_id=dept_id,isadmin =True,can_create =True, entity_id=self._entity_id())
        return

    def empl_dept_mapping_excel(self, data):
        emp_code = data.get('code')
        try:
            emp_data = Employee.objects.get(code=emp_code)
            arr_code = []
            emp_id = emp_data.id
            edept = str(data.get('eDept'))
            designation = data.get('edesig')
            ebranch = str(data.get('eBranch'))
            branch_id = self.get_branch_id_from_code(ebranch)
            if branch_id is not None:
                if edept == ebranch:
                    self.isdept_branch_same(branch_id, emp_id)
                    is_branch =True
                else:
                    self.isdept_branch_same(branch_id, emp_id)
                    self.isdepartment_check(edept, branch_id, emp_id)
                    is_branch = False
                self.remove_dept(branch_id,emp_id,edept,is_branch)
            # Employee.objects.filter(id=emp_id).update(designation=designation, lastsync_date=datetime.now())
            return True
        except:
            return emp_code

    def get_branch_id_from_code(self, code):
        branch = EmployeeBranch.objects.using(self._current_app_schema()).get(code=code)
        if branch is not None:
            branch_id = branch.id
            return branch_id
        else:
            return None

    def isdept_branch_same(self, branch_id, empid):
        condition = Q(branch_id=branch_id) & Q(name__isnull=True) &Q(entity_id=self._entity_id())
        dept = Department.objects.using(self._current_app_schema()).filter(condition)
        if len(dept) > 0:
            self.emp_dept_per(empid, dept[0].id)
            return dept[0].id
        else:
            dept = Department.objects.using(self._current_app_schema()).create(branch_id=branch_id,is_sys=True, entity_id=self._entity_id())
            code = "DGRP" + str(dept.id)
            dept.code = code
            dept.save()
            self.emp_dept_per(empid, dept.id)
            return dept.id

    def isdepartment_check(self, dep_code, branch_id, empid):
        condition = Q(branch_id=branch_id) & Q(name=dep_code) &Q(entity_id=self._entity_id())
        dept = Department.objects.using(self._current_app_schema()).filter(condition)
        if len(dept) > 0:
            self.emp_dept_per(empid, dept[0].id)
            return dept[0].id
        else:
            dept = Department.objects.using(self._current_app_schema()).create(name=dep_code, branch_id=branch_id,is_sys= True, entity_id=self._entity_id())
            code = "DGRP" + str(dept.id)
            dept.code = code
            dept.save()
            self.emp_dept_per(empid, dept.id)
            return dept.id

    def remove_dept(self,branch_id,emp_id,dept,is_branch):
        condition = Q(employee_id=emp_id)&Q(isadmin=True) &Q(entity_id=self._entity_id())
        emp_dept = EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(condition)
        arr=[]
        for i in emp_dept:
            dept_branchid = i.department.branch_id
            if dept_branchid != branch_id:
                arr.append(i.id)

            dept_name = i.department.name
            is_sys = i.department.is_sys
            if (dept_name != dept) and (dept_name is not None)and (is_sys==1) and is_branch is False:
                arr.append(i.id)

        if len(arr)> 0:
            emp_dept = EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(id__in=arr, entity_id=self._entity_id()).delete()
            return
