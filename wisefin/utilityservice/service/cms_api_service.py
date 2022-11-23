import json

from cmsservice.models import QuestionProjectMapping, ProposedContract
from cmsservice.service.quesansservice import Quesansservice
from masterservice.models import Commodity, Question_Type, Questions, Question_Header, Questions_Typemapping,Questions_suboptions,Vendorclassification_Mapping
# from masterservice.service.apcategoryservice import CategoryService
# from masterservice.service.apsubcategoryservice import SubcategoryService
from masterservice.service.apcategoryservice import CategoryService
from masterservice.service.apsubcategoryservice import SubcategoryService
from masterservice.service.commodityservice import CommodityService
from masterservice.service.productservice import ProductService
from masterservice.service.questionheaderservice import QuestionheaderService
from masterservice.service.questionservice import QuestionService
from masterservice.service.questiontypeservice import QuestiontypeService
from userservice.service.employeeservice import EmployeeService
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from vendorservice.util.vendorutil import getGroup, getType, getClassification
from wisefinapi.employeeapi import EmployeeAPI
from userservice.service.groupservice import GroupService
from userservice.controller.vowusercontroller import VowUser
from userservice.models import EmployeeGroup, Employee
from userservice.service.vowemployeeservice import VowEmployeeServ
from cmsservice.util.cmsutil import ActiveStatus

class ApiService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.CMS_SERVICE)
    MICRO_SERVICE = True

#user
    def get_emp_id(self, request):
        user_id = request.user.id
        if self.MICRO_SERVICE:
            emp_ser = EmployeeService(self._scope())
            emp = emp_ser.get_employee_from_userid(user_id)
            emp = emp.__dict__
            emp['is_user'] = True
            return emp

        else:
            is_user = True
            emp_api = EmployeeAPI()
            emp = emp_api.get_emp_by_userid(request, user_id)
            emp['is_user'] = is_user
            return emp


    def get_multi_emp(self,request,empid_arr):
        if self.MICRO_SERVICE:
            emp_ser = EmployeeService(self._scope())
            emp = emp_ser.get_employee_info(empid_arr)
            return emp
        else:
            emp_api = EmployeeAPI()
            emp = emp_api.fetch_multi_empolyee(request, empid_arr)
            return emp

    def get_group_info_by_id(self,grp_id):
        if self.MICRO_SERVICE:
            grp_serv = GroupService(self._scope())
            obj = grp_serv.fetch_group_by_id(grp_id)
            return obj
        else:
            pass

    def get_multi_group_info_by_id(self,arr):
        if self.MICRO_SERVICE:
            grp_serv = GroupService(self._scope())
            obj = grp_serv.fetch_multi_group_by_id(arr)
            return obj
        else:
            pass

    def employeelist_by_grpid(self,grp_arr):
        if self.MICRO_SERVICE:
            grp_serv = GroupService(self._scope())
            obj = grp_serv.get_employeelist_by_grpid(grp_arr)
            return obj
        else:
            pass

    def grouplist_by_empid(self,emp_id):
        if self.MICRO_SERVICE:
            grp_serv = GroupService(self._scope())
            obj = grp_serv.get_group_by_empid(emp_id)
            return obj
        else:
            pass

#master
    def get_cat_id(self, cat_id):
        if self.MICRO_SERVICE:
            categoryservice = CategoryService(self._scope())
            obj = categoryservice.fetchcategory(cat_id)
            return obj
        else:
            pass

    def get_subcat_id(self, subcat_id):
        if self.MICRO_SERVICE:
            subcategoryservice = SubcategoryService(self._scope())
            obj = subcategoryservice.fetchsubcategory(subcat_id)
            return obj
        else:
            pass

    def get_commodity_id(self, commodity_id):
        if self.MICRO_SERVICE:
            categoryservice = CommodityService(self._scope())
            obj = categoryservice.fetch_Commodity(commodity_id, None)
            return obj
        else:
            pass

    def get_product(self, product_id):
        if self.MICRO_SERVICE:
            productservice = ProductService(self._scope())
            obj = productservice.fetch_productdata(product_id)
            return obj
        else:
            pass

    def get_empsingle_id(self, request, emp_id):
        if self.MICRO_SERVICE:
            emp_ser = EmployeeService(self._scope())
            emp = emp_ser.fetch_employee_by_empname(emp_id)
            return emp
        else:
            emp_api = EmployeeAPI()
            emp = emp_api.get_emp_by_empid(request, emp_id)
            print('empsingle', emp)
            return emp

    def fetch_vow_employee_by_id(self, empid):
        serv = VowEmployeeServ()
        data = serv.get_vowemployee_details(empid)
        return data

    def fetch_vow_multi_employee(self, arr):
        serv = VowEmployeeServ()
        data = serv.get_multi_vowemployee_details(arr)
        return data

    def get_questype_id(self, ques_id):
        if self.MICRO_SERVICE:
            quesservice = QuestiontypeService(self._scope())
            obj = quesservice.get_question_type(ques_id)
            return obj
        else:
            pass

    def get_questype(self, type_id):
        if self.MICRO_SERVICE:
            quesservice = QuestiontypeService(self._scope())
            obj = quesservice.get_cmsquestion_type(type_id)
            return obj
        else:
            pass

    def get_ques_id(self, ques_id):
        if self.MICRO_SERVICE:
            quesservice = QuestionService(self._scope())
            obj = quesservice.get_question(ques_id)
            return obj
        else:
            pass

    def get_ques(self, ques_id):
        if self.MICRO_SERVICE:
            quesservice = QuestionService(self._scope())
            obj = quesservice.get_cmsquestion(ques_id)
            return obj
        else:
            pass

    def get_sub_ques(self, ques_id):
        if self.MICRO_SERVICE:
            quesservice = QuestionService(self._scope())
            obj = quesservice.get_cms_subquestion(ques_id)
            return obj
        else:
            pass

    def get_classify_id(self, request,ques_id):
        if self.MICRO_SERVICE:
            quesservice = Quesansservice(self._scope())
            obj = quesservice.fetch_classify(request,ques_id)
            return obj
        else:
            pass

    def get_proquesmap_id(self, pro_id):
        if self.MICRO_SERVICE:
            quesservice = Quesansservice(self._scope())
            obj = quesservice.fetch_projquesmap(pro_id)
            return obj
        else:
            pass

    def get_quesheader_id(self, ques_id):
        if self.MICRO_SERVICE:
            quesservice = QuestionheaderService(self._scope())
            obj = quesservice.fetch_cmsquestionheader_type(ques_id)
            return obj
        else:
            pass

    # def fetch_questype(self,qtype_id):
    #     qutype = Question_Type.objects.using(self._current_app_schema()).filter(id__in=qtype_id)
    #     print(qutype)
    #     return qutype

    def get_rel_cat(self, rel_cat):
        rel_cat_val = getGroup(rel_cat)
        return rel_cat_val

    def get_criticality(self, criticality):
        criticality_val = getType(criticality)
        return criticality_val

    def get_vendor_type(self, vendor_type):
        vendor_type_val = getClassification(vendor_type)
        return vendor_type_val

    def get_question_id_by_type(self,type_id):
        arr=Questions_Typemapping.objects.filter(type_id=type_id).values_list('question_id',flat=True)
        obj=Questions.objects.filter(id__in=arr).values()
        return obj

    def get_ques_suboption(self,q_id):
        obj=Questions_suboptions.objects.filter(question_id__in=q_id,status=ActiveStatus.Active)
        return obj

    def get_vendor_classification(self,rel_cat,criticality,vendor_type,q_type_arr):
        obj=Vendorclassification_Mapping.objects.filter(rel_cat=rel_cat,criticality=criticality,vendor_type=vendor_type,type_id__in=q_type_arr,status=ActiveStatus.Active)
        return obj

class CmsCommonService:
    def __init__(self, request):
        vowuser_info = VowUser().get_user(request)

        self.emp_id = vowuser_info['user_id']
        self.entity_id = vowuser_info['entity_id']
        self.is_user = vowuser_info['is_user']
        self.schema = vowuser_info['schema']

    def fetch_group_by_id(self, group_id):
        grp_obj_list = EmployeeGroup.objects.using(self.schema).filter(id=group_id).values('id', 'name', 'code')
        if len(grp_obj_list) > 0:
            grp_obj = grp_obj_list[0]
        else:
            grp_obj = None
        return grp_obj

    def fetch_multi_group_by_id(self, arr):
        grp_obj_list = EmployeeGroup.objects.using(self.schema).filter(id__in=arr).values('id', 'name', 'code')

        return grp_obj_list

# master
#     def fetch_cat_id(self, cat_id):
#         cat_obj_list = Apcategory.objects.using(self.schema).filter(id=cat_id).values('id', 'name', 'code')
#         if len(cat_obj_list) > 0:
#             cat_obj = cat_obj_list[0]
#         else:
#             cat_obj = None
#         return cat_obj

    # def fetch_subcat_id(self, cat_id):
    #     subcat_obj_list = Apcategory.objects.using(self.schema).filter(id=cat_id).values('id', 'name', 'code')
    #     if len(subcat_obj_list) > 0:
    #         subcat_obj = subcat_obj_list[0]
    #     else:
    #         subcat_obj = None
    #     return subcat_obj

    def vow_get_commodity_id(self, commodity_id):
        obj_list = Commodity.objects.using(self.schema).filter(id=commodity_id).values('id', 'name', 'code')
        if len(obj_list) > 0:
            cat_obj = obj_list[0]
        else:
            cat_obj = None
        return cat_obj

    def get_empsingle_id(self,emp_id):
        employee = Employee.objects.get(id=emp_id)
        emp_data = {"id": employee.id, "code": employee.code, "name": employee.full_name}
        return emp_data


    def fetch_vow_employee_by_id(self, empid):
        serv = VowEmployeeServ()
        data = serv.get_vowemployee_details(empid)
        return data

    def fetch_vow_multi_employee(self, arr):
        serv = VowEmployeeServ()
        data = serv.get_multi_vowemployee_details(arr)
        return data

    def fetch_Questype(self, ques_id):
        ques_type_list = Question_Type.objects.using(self.schema).filter(id=ques_id).values('id', 'name', 'remarks')
        if len(ques_type_list) > 0:
            ques_obj = ques_type_list[0]
        else:
            ques_obj = None
        return ques_obj
    def get_vow_multi_emp(self,request,empid_arr):
        emp_ser = VowEmployeeServ()
        emp = emp_ser.get_vowemployee_info(empid_arr)
        return emp
    def get_employee_info(self,empid_arr):
        obj_data=Employee.objects.filter(id__in=empid_arr).values('id',"full_name","code","employee_branch__code","employee_branch__name")
        vlist = []
        for employee in obj_data:
            employe_name='(' + employee['code'] + ') ' + employee['full_name']
            emp_resp = {"id":employee['id'], "code": employee['code'], "full_name": employe_name,
                        "branch_name": employee['employee_branch__name'],"branch_code":employee['employee_branch__code']}

            vlist.append(emp_resp)
        return vlist

    def fetch_Question(self, ques_id):
        ques_type_list = Questions.objects.using(self.schema).filter(id=ques_id).values('id', 'text','input_type','header_id','order')
        if len(ques_type_list) > 0:
            ques_obj = ques_type_list[0]
        else:
            ques_obj = None
        return ques_obj

    def get_proquesmap(self, pro_id):
        quesclass = QuestionProjectMapping.objects.using(self.schema).filter(project_id=pro_id,status=ActiveStatus.Active).values_list('type_id',flat=True)
        return quesclass

    def get_project(self, pro_id):
        quesclass = ProposedContract.objects.using(self.schema).filter(id=pro_id,status=ActiveStatus.Active)
        return quesclass

    def vow_get_questype(self, type_id):
        questioin_type = Question_Type.objects.using(self.schema).filter(id__in=type_id,status=ActiveStatus.Active)
        return questioin_type

    def vow_get_ques(self, typeid):
        qid_obj = Questions_Typemapping.objects.using(self.schema).filter(type_id__in=typeid)
        qid_arr = [q.question_id for q in qid_obj]

        obj = Questions.objects.using(self.schema).filter(id__in=qid_arr)
        for i in obj:
            for j in qid_obj:
                if j.question_id == i.id:
                    i.type_id = j.type_id
                    break
        return obj

    def vow_get_quesheader_id(self, queshdr_id):
        questionheader_obj = Question_Header.objects.using(self.schema).filter(type_id__in=queshdr_id,status=ActiveStatus.Active)
        return questionheader_obj

    def vow_get_question(self, ques_id):
        obj = Questions_Typemapping.objects.using(self.schema).filter(type_id=ques_id,status=ActiveStatus.Active).values_list("id",flat=True)
        return obj

    def vow_question_suboption(self,ques_id):
        obj=Questions_suboptions.objects.using(self.schema).filter(question_id__in=ques_id,status=ActiveStatus.Active)
        return obj