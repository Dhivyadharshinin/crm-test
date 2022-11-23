from userservice.models import Vow_user, Vow_userEntityMapping
from django.db.models import Q
from django.contrib.auth.models import User


class VowEmployeeServ:
    def get_multi_vowemployee_details(self, empid):
        arr=[]
        emp_obj = Vow_user.objects.filter(vow_employee_id__in=empid)

        for i in emp_obj:
            d={"id":i.vow_employee_id,"full_name":"("+ str(i.code)+ ") "+str(i.full_name),"code":i.code}
            arr.append(d)
        return arr

    def get_vowemployee_details(self,id):
        obj=Vow_user.objects.get(vow_employee_id=id)
        d = {"id": obj.vow_employee_id, "full_name": obj.full_name, "code": obj.code}
        return d
    def get_vowemployee_info(self,empid_arr):
        obj_data=Vow_user.objects.filter(id__in=empid_arr).values('id',"full_name","code","employee_branch__code","employee_branch__name")
        vlist = []
        for employee in obj_data:
            employe_name='(' + employee['code'] + ') ' + employee['full_name']
            emp_resp = {"id":employee['id'], "code": employee['code'], "name": employe_name,
                        "branch_name": employee['employee_branch__name'],"branch_code":employee['employee_branch__code']}

            vlist.append(emp_resp)
        return vlist

    # changes for vow(v-0.1)
    def get_vow_user_id(self, user_id):
        vow_obj = Vow_user.objects.get(user_id=user_id)
        return vow_obj.vow_employee_id

    # changes for vow(v-0.1)
    def get_vow_entityids(self, vow_user_id):
        map_obj = Vow_userEntityMapping.objects.using('default').filter(employee_id=vow_user_id)
        entity_ids = []
        if len(map_obj) > 0:
            for map in map_obj:
                entity_ids.append(map.entity_id)
        return entity_ids

    # changes for vow(v-0.1)
    def get_default_vow_entity(self, vow_user_id):
        condition = Q(employee_id__exact=vow_user_id) & Q(is_default__exact=True)
        map_obj = Vow_userEntityMapping.objects.using('default').filter(condition)
        if len(map_obj) > 0:
            map_obj = map_obj[0]
            return map_obj.entity_id
        else:
            return None

    # changes for vow(v-0.1)
    def get_user_type(self, user_id):
        user = User.objects.get(id=user_id)
        user_type = user.is_staff
        return int(user_type)

