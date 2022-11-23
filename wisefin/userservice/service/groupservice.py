from django.db.models.query_utils import Q
from django.utils.timezone import now
from userservice.data.userutil import ActiveStatus,GroupType, get_grouprole
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from userservice.models import EmployeeGroup, EmployeeGroupMapping, Employee
from userservice.data.response.employeegroupresponse import EmployeeGroupResponse
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from userservice.data.response.employeeresponse import EmployeeResponse

class GroupService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.USER_SERVICE)

    def create_employee_group(self, data_obj, emp_id):
        
        if not data_obj.get_id() is None:
            
            EmployeeGroup.objects.using(self._current_app_schema()).filter(id=data_obj.get_id()).update(name=data_obj.get_name(), updated_by=emp_id,updated_date=now(),entity_id=self._entity_id())
            
            grp_obj = EmployeeGroup.objects.using(self._current_app_schema()).get(id=data_obj.get_id(),entity_id=self._entity_id())

        else:
            grp_obj = EmployeeGroup.objects.using(self._current_app_schema()).create(
                                                    name=data_obj.get_name(),type=GroupType.group,created_by=emp_id,entity_id=self._entity_id())

            code = 'GRP'+str(grp_obj.id)
            grp_obj.code = code
            grp_obj.save()
        grp_obj_data = EmployeeGroupResponse()
        grp_obj_data.set_id(grp_obj.id)
        grp_obj_data.set_name(grp_obj.name)
        grp_obj_data.set_code(grp_obj.code)
        # grp_obj_data.set_type(grp_obj.type)
        # grp_obj_data.set_module(grp_obj.module_id)
        return grp_obj_data



    def fetch_employee_group_list(self, vys_page, request):
        condition = Q(status=ActiveStatus.Active)&Q(entity_id=self._entity_id())
        query = request.GET.get('query')
        if query is not None:
            condition &= Q(name__icontains=query) | Q(code__icontains=query)

        grp_obj_list = EmployeeGroup.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[vys_page.get_offset():vys_page.get_query_limit()]

        grp_obj_list_data = NWisefinList()
        for grp_obj in grp_obj_list:
            grp_obj_data = EmployeeGroupResponse()
            grp_obj_data.set_id(grp_obj.id)
            grp_obj_data.set_name(grp_obj.name)
            grp_obj_data.set_code(grp_obj.code)
            grp_obj_data.set_type(grp_obj.type)
            grp_obj_list_data.append(grp_obj_data)

        vpage = NWisefinPaginator(grp_obj_list, vys_page.get_index(), 10)
        grp_obj_list_data.set_pagination(vpage)
        return grp_obj_list_data


    def mapping_employee_group(self,grp_data,emp_id,is_removed):

        emp_arr=grp_data['emp_arr']
        group_id=grp_data['group_id']
        role_id=grp_data['role_id']
        active_status = ActiveStatus.Active
        if is_removed == '1':
            active_status=ActiveStatus.Delete
        current_empid=EmployeeGroupMapping.objects.using(self._current_app_schema()).filter(employee_id__in=emp_arr,group_id=group_id,role=role_id,entity_id=self._entity_id()).values_list('employee_id',flat=True)

        crt_empid = list(set(emp_arr) - set(current_empid))
        upt_empid = list(set(emp_arr).intersection(current_empid))

        # adding new permission
        crt_empid_arr=[]
        for i in crt_empid:
            e_obj=EmployeeGroupMapping(employee_id=i,group_id=group_id,role=role_id,created_by=emp_id,entity_id=self._entity_id())
            crt_empid_arr.append(e_obj)
        if len(crt_empid_arr) >0:
            EmployeeGroupMapping.objects.using(self._current_app_schema()).bulk_create(crt_empid_arr)

        # updating permission
        if len(upt_empid) >0:
            EmployeeGroupMapping.objects.using(self._current_app_schema()).filter(employee_id__in=upt_empid,group_id=group_id,role=role_id,created_by=emp_id).update(status=active_status,entity_id=self._entity_id())


        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj


    def get_group_by_employee_id(self,emp_id):
        grp_obj=EmployeeGroupMapping.objects.using(self._current_app_schema()).filter(employee_id=emp_id)
        list_data = NWisefinList()
        for i in grp_obj:
            grp=i.group
            grp_obj_data = EmployeeGroupResponse()
            grp_obj_data.set_id(grp.id)
            grp_obj_data.set_name(grp.name)
            grp_obj_data.set_code(grp.code)
            grp_obj_data.set_type(grp.type)
            list_data.append(grp_obj_data)
        return list_data

    def get_employee_by_group_id(self, group_id):
        grp_obj=EmployeeGroupMapping.objects.using(self._current_app_schema()).filter(group_id=group_id, status=ActiveStatus.Active)
        list_data = NWisefinList()
        for i in grp_obj:
            emp_obj=i.employee
            emp_resp = EmployeeResponse()
            emp_resp.set_id(emp_obj.id)
            emp_resp.set_full_name(emp_obj.full_name)
            emp_resp.set_code(emp_obj.code)
            emp_resp.set_role(get_grouprole(i.role))
            list_data.append(emp_resp)
        return list_data


#   response function

    def fetch_group_by_id(self,group_id):
        grp_obj_list = EmployeeGroup.objects.using(self._current_app_schema()).filter(id=group_id).values('id','name','code')
        if len(grp_obj_list) >0 :
            grp_obj=grp_obj_list[0]
        else:
            grp_obj=None
        return grp_obj

    # only employee id
    def get_group_by_empid(self,emp_id):
        grp_obj_list = EmployeeGroupMapping.objects.using(self._current_app_schema()).filter(employee_id=emp_id,status=ActiveStatus.Active).values_list('group_id',flat=True)
        grp_obj_list = list(grp_obj_list)
        return grp_obj_list

    def fetch_multi_group_by_id(self, arr):
        grp_obj_list = EmployeeGroup.objects.using(self._current_app_schema()).filter(id__in=arr).values('id', 'name','code')

        return grp_obj_list


    def get_employeelist_by_grpid(self,arr):
        grp_obj_list = EmployeeGroupMapping.objects.using(self._current_app_schema()).filter(group_id__in=arr)
        grp_dict=dict()
        grp_arr=[]
        for i in grp_obj_list:
            if i.group_id  not in grp_arr:
                grp_arr.append(i.group_id)
                grp_dict[i.group_id]=[i.employee_id]
            else:
                g=grp_dict[i.group_id]
                g.append(i.employee_id)
                grp_dict[i.group_id]=g

        return grp_dict

    def group_employee(self, emp_id, request):
        request = request
        emp_code = request.GET.get('emp_code')
        grp_obj = EmployeeGroup.objects.using(self._current_app_schema()).filter(code=emp_code)
        if len(grp_obj) > 0:
            msg_obj = NWisefinError()
            msg_obj.set_code(ErrorMessage.DUPLICATE_ENTRY)
            msg_obj.set_description(ErrorDescription.DUPLICATE_CODE)
            return msg_obj
        else:
            empl = Employee.objects.using(self._current_app_schema()).get(code=emp_code)
            emp_grp = EmployeeGroup.objects.using(self._current_app_schema()).create(
                                                    name=empl.full_name,
                                                    code=emp_code,
                                                    type=GroupType.employee,
                                                    created_by=emp_id,
                                                    created_date=now(),
                                                    entity_id=self._entity_id())
            EmployeeGroupMapping.objects.using(self._current_app_schema()).create(employee_id=empl.id,group_id=emp_grp.id,created_by=emp_id,
                                                    created_date=now(),
                                                    entity_id=self._entity_id(),status=ActiveStatus.Active)
            msg_obj = NWisefinSuccess()
            msg_obj.set_status(SuccessStatus.SUCCESS)
            msg_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return msg_obj


    def group_employeeall(self, emp_id):
        emp = Employee.objects.using(self._current_app_schema()).filter(status=ActiveStatus.Active).values('code')
        emp_grpp = EmployeeGroup.objects.using(self._current_app_schema()).filter(status=ActiveStatus.Active).values('code')
        if len(emp) > 0:
            # exists_code = []
            for x in emp:
                if x not in emp_grpp:
                    empl = Employee.objects.using(self._current_app_schema()).get(code=x['code'])
                    emp_grp = EmployeeGroup.objects.using(self._current_app_schema()).create(
                        name=empl.full_name,
                        code=x['code'],
                        type=GroupType.employee,
                        created_by=emp_id,
                        created_date=now(),
                        entity_id=self._entity_id())
                    EmployeeGroupMapping.objects.using(self._current_app_schema()).create(employee_id=empl.id,
                                                                                          group_id=emp_grp.id,
                                                                                          created_by=emp_id,
                                                                                          created_date=now(),
                                                                                          entity_id=self._entity_id(),
                                                                                          status=ActiveStatus.Active)

                else:
                    # exists_code.append(x['code'])
                    print("already exists emp_code in grp tble : ", x['code'])
            msg_obj = NWisefinSuccess()
            msg_obj.set_status(SuccessStatus.SUCCESS)
            msg_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return msg_obj
        else:
            msg_obj = NWisefinError()
            msg_obj.set_code(ErrorMessage.DUPLICATE_ENTRY)
            msg_obj.set_description(ErrorDescription.DUPLICATE_CODE)
            return msg_obj
    def employee_group_fetch(self,type,vys_page,name,request):
        condition=Q(status=ActiveStatus.Active)
        employee_id=request.employee_id
        employee_code=request.user
        if name!=None:
            condition&=Q(name__icontains=name)|Q(code__icontains=name)

        if int(type)==GroupType.group:
            condition&=Q(type=GroupType.group)
            tab=EmployeeGroup.objects.using(self._current_app_schema()).filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
        elif int(type)==GroupType.employee:
            condition &= Q(type=GroupType.employee)
            tab = EmployeeGroup.objects.using(self._current_app_schema()).filter(condition)[
                  vys_page.get_offset():vys_page.get_query_limit()]
        else:
            tab = EmployeeGroup.objects.using(self._current_app_schema()).filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
        grp_obj_list_data = NWisefinList()
        for grp_obj in tab:
            grp_obj_data = EmployeeGroupResponse()
            grp_obj_data.set_id(grp_obj.id)
            grp_obj_data.set_name(grp_obj.name)
            grp_obj_data.set_code(grp_obj.code)
            grp_obj_data.set_type(grp_obj.type)
            if int(type)==GroupType.employee and str(employee_code)==str(grp_obj.code):
                pass
            else:
                grp_obj_list_data.append(grp_obj_data)

        vpage = NWisefinPaginator(tab, vys_page.get_index(), 10)
        grp_obj_list_data.set_pagination(vpage)
        return grp_obj_list_data



