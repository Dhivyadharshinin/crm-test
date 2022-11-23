import json

from django.db import IntegrityError
from django.db.models import Q

from userservice.models import EmployeeModuleMapping, Employee
from userservice.data.response.moduleresponse import ModuleMappingResponse
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from django.db.models import Max
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace


class ModuleMappingService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.USER_SERVICE)

    def addmodule(self,employee_id,module_list):
        module_arr=[]
        module_list = module_list.get('module_id')
        user = EmployeeModuleMapping.objects.using(self._current_app_schema()).filter(employee_id=employee_id, entity_id=self._entity_id()).aggregate(Max('order'))
        max_order = user.get('order__max')

        if max_order is None:
            count = 0
            for i in module_list:
                count = count + 1
                obj = EmployeeModuleMapping(employee_id=employee_id, module_id=i, order=count, entity_id=self._entity_id())
                module_arr.append(obj)

            emp = EmployeeModuleMapping.objects.using(self._current_app_schema()).bulk_create(module_arr)

        else:
            count = max_order
            for i in module_list:
                condition = Q(employee_id__exact=employee_id) & Q(module_id__exact=i) & Q(entity_id=self._entity_id())
                modulemapping = EmployeeModuleMapping.objects.using(self._current_app_schema()).filter(condition).exists()
                if modulemapping is False:
                    count = max_order + 1
                    obj = EmployeeModuleMapping(employee_id=employee_id, module_id=i, order=count, entity_id=self._entity_id())
                    module_arr.append(obj)

            emp = EmployeeModuleMapping.objects.using(self._current_app_schema()).bulk_create(module_arr)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)

            return success_obj

        return emp

    def removemodule(self,employee_id,module_list):
        module_list = module_list.get('module_id')
        for i in module_list:
            EmployeeModuleMapping.objects.using(self._current_app_schema()).filter(module_id=i,entity_id=self._entity_id()).delete()

        modulemapping = EmployeeModuleMapping.objects.using(self._current_app_schema()).filter(employee_id=employee_id,entity_id=self._entity_id()).order_by('order')
        count =0
        for i in modulemapping:
            count = count + 1
            order = i.order
            module = i.module_id
            condition = Q(employee_id__exact=employee_id) & Q(module_id__exact=module) & Q(entity_id=self._entity_id())
            if order != count:
                EmployeeModuleMapping.objects.using(self._current_app_schema()).filter(employee_id=condition).update(order=count)
        return

    def module_order(self,module_obj):
        module_obj = module_obj.get('data')
        for i in module_obj:
            employee =i.get('employee')
            module= i.get('module')
            order = i.get('order')

            condition = Q(employee_id__exact=employee) & Q(module_id__exact=module) & Q(entity_id=self._entity_id())
            modulemapping = EmployeeModuleMapping.objects.using(self._current_app_schema()).filter(condition).update(order=0)

            condition =  Q(employee_id__exact=employee) & Q(order__gte = order) & Q(entity_id=self._entity_id())
            modulemapping = EmployeeModuleMapping.objects.using(self._current_app_schema()).filter(condition).order_by('order')
            count = order
            for j in modulemapping:
                count = count + 1
                module_order = j.order
                condition =  Q(employee_id__exact=employee) & Q(module_id__exact=j.module_id) & Q(entity_id=self._entity_id())
                if module_order != count:
                    EmployeeModuleMapping.objects.using(self._current_app_schema()).filter(employee_id=condition).update(order=count)

            condition = Q(employee_id__exact=employee) & Q(module_id__exact=module) & Q(entity_id=self._entity_id())
            modulemapping = EmployeeModuleMapping.objects.using(self._current_app_schema()).filter(condition).update(order=order)

        return

    def listmodule(self, employee_id):
        module_list = EmployeeModuleMapping.objects.using(self._current_app_schema()).filter(employee_id=employee_id,entity_id=self._entity_id())
        module_list_data = NWisefinList()
        for module in module_list:
            module_data = ModuleMappingResponse()
            module_data.set_id(module.module.id)
            module_data.set_order(module.order)
            module_data.set_name(module.module.name)
            module_data.set_logo(module.module.logo)
            module_data.set_url(module.module.url)
            module_list_data.append(module_data)
        return module_list_data


    def module_order_assinging(self,emp_id,module_data):
        # employee = Employee.objects.get(user_id=emp_id).id
        for i in module_data:
            c = EmployeeModuleMapping.objects.filter(module_id=i['module_id'], employee_id=emp_id, entity_id=self._entity_id()).update(order=i['order'])

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)

        return success_obj
            # uplode = EmployeeModuleMapping.objects.using(self._current_app_schema()).create(employee_id=employee, entity_id=self._entity_id())
        # uplode = EmployeeModuleMapping.objects.filter(employee_id=employee,entity_id=self._entity_id())
        # uplode.order = uplode.id
        # uplode.save()
        # module_data = ModuleMappingResponse()
        # module_data.set_order(uplode.order)
        # return module_data

    def assign_module(self, emp_id, module_data):
        # employee = Employee.objects.get(user_id=emp_id).id
        generator = EmployeeModuleMapping.objects.using(self._current_app_schema()).filter(employee_id=emp_id, entity_id=self._entity_id(), module_id=module_data['module_id'])

        if len(generator) == 0:
            update_create = EmployeeModuleMapping.objects.using(self._current_app_schema()).create(employee_id=emp_id,entity_id=self._entity_id(), module_id=module_data['module_id'], order=0)
            x = EmployeeModuleMapping.objects.using(self._current_app_schema()).all()
            order = len(x)
            update_create.order = order
            update_create.save()
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)

            return success_obj
        else:
            error = NWisefinError()
            error.set_code(200)
            error.set_description("INVALID")
            return error



