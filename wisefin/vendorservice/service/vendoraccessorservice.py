from django.db.models import Q
from django.utils.timezone import now
import json
from userservice.data.response.roleresponse import RoleModuleResponse
from vendorservice.util.vendorutil import getType
from userservice.service.employeeservice import EmployeeService
from userservice.models import RoleEmployee, Employee
from userservice.service.roleemployeeservice import RoleEmployeeService
from vendorservice.models import VendorAccessor ,Vendor , VendorQueue
from vendorservice.service.vendorservice import VendorService
from vendorservice.util.vendorutil import QueueStatus, Role
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.utilityservice import NWisefinUtilityService
from vendorservice.data.response.vendorlistresponse import VendorListData
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace


class VendorAccessorService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def set_accessor(self, vendor_id, user_id, status):
        condition = Q(vendor_id__exact=vendor_id) & Q(status__exact=status) &Q(entity_id=self._entity_id())
        try:
            vendor_accessor = VendorAccessor.objects.using(self._current_app_schema()).get(condition)
            vendor_accessor.updated_date = now()
            vendor_accessor.status = status
            vendor_accessor.user_id = user_id
            vendor_accessor.save()
        except:
            vendor_accessor=VendorAccessor.objects.using(self._current_app_schema()).create(vendor_id = vendor_id, user_id = user_id, status = status, entity_id=self._entity_id())

    def update_accessor(self, vendor_id, user_id):

        condition = Q(vendor_id__exact=vendor_id) & Q(user_id__exact=0) &Q(entity_id=self._entity_id())
        try:
            vendor_accessor = VendorAccessor.objects.using(self._current_app_schema()).filter(condition).update(user_id = user_id)

            update_vendor =VendorQueue.objects.using(self._current_app_schema()).filter(Q(vendor_id_id=vendor_id)& Q(to_user_id=0)&Q(entity_id=self._entity_id())).update(to_user_id=user_id)

        except:
            pass


    def check_employeeStatus(self,employee_id ):
        #if request.method == 'GET':
        roleemployee_service = RoleEmployeeService(self._scope())  # changed
        userid_check = False
        role_obj = roleemployee_service.fetch_employee_submodule(employee_id, userid_check)
        emprole_obj=role_obj.data
        role_Arr = []
        if len(emprole_obj)>0 :
            for i in emprole_obj :

                modulename = i.name
                if modulename == 'Vendor':
                    role = i.role
                    for j in role:
                        rolename = j.name
                        role_Arr.append(rolename)
                    return role_Arr
        return role_Arr

    def check_status(self, vendor_id, employee_id):
        status_service = NWisefinUtilityService()
        vendor = Vendor.objects.using(self._current_app_schema()).get(id=vendor_id, entity_id=self._entity_id())
        vobj = vendor.vendor_status
        vobj= int(vobj)

        creat_by = vendor.created_by
        creat_by=int(creat_by)

        RM_id = vendor.rm_id
        RM_id=int(RM_id)

        type=[]
        if employee_id == creat_by:
            type.append(Role.maker)
            return type
        elif employee_id == RM_id:
            type.append(Role.rm)
            if employee_id == creat_by :
                type.append(Role.maker)
            return type
        elif vobj == 3:
            type.append(Role.checker)
            if employee_id == creat_by :
                type.append(Role.maker)
            return type
        elif vobj == 4:
            type.append(Role.header)
            if employee_id == creat_by :
                type.append(Role.maker)
            return type
        else :
            return type
        # condition = Q(id=vendor_id)
        # vlist = Vendor.objects.get(condition)
        # vendor_list=[]
        # for vendor_status in vlist:
        #     vendor_list.append(vendor_status.id)
        # return vendor_list

    def get_vendor_list(self,request,user_id, status,vys_page,query,right_check):

        #role_obj = self.check_employeeStatus(employee_id)

        # condition = Q(status__exact = status) & Q(user_id__exact=user_id)

        vendor_service=VendorService(self._scope())
        ismaker_obj=vendor_service.ismaker(user_id,True)
        condition = Q(id__exact=user_id) &Q(entity_id=self._entity_id())

        #logger.info(condition)
        # vendor_accessor_arr = VendorAccessor.objects.filter(condition).distinct('vendor_id')[vys_page.get_offset():vys_page.get_query_limit()]
        vendor_accessor_arr = VendorAccessor.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')
        #logger.info(vys_page.get_index())

        vendor_list=[]
        for vendor_accessor in vendor_accessor_arr:
            vendor_list.append(vendor_accessor.vendor_id)
        #logger.info(len(vendor_list))

        if (status == 3 or status == 4):
            # vendor_list = []
            condition = Q(vendor_status__exact=status) &Q(entity_id=self._entity_id())
            vlist = Vendor.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')
            for vendor_accessor in vlist:
                vendor_list.append(vendor_accessor.id)
        if status==1:
            condition = Q(modify_status__exact=-1) &Q(entity_id=self._entity_id())
            vlist = Vendor.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')
            for vendor_accessor in vlist:
                vendor_list.append(vendor_accessor.id)
        if status==None:
            condition = Q(rm_id__exact=user_id) &Q(entity_id=self._entity_id())
            vlist = Vendor.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')
            for vendor_accessor in vlist:
                vendor_list.append(vendor_accessor.id)
        if right_check==True:
            condition = ((Q(vendor_status__exact=3) | Q(vendor_status__exact=4)))&Q(entity_id=self._entity_id())
            vlist = Vendor.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')
            for vendor_accessor in vlist:
                vendor_list.append(vendor_accessor.id)

        vendor_list = set(vendor_list)
        vendor_list = list(vendor_list)
        start_index = (vys_page.get_index() - 1) * 10
        end_index = start_index + 11
        if end_index > len(vendor_list):
            end_index = len(vendor_list)

        #logger.info(start_index, end_index)
        #logger.info(len(vendor_list))
        # vendor_list = []
        vendorList = []
        # for vendor_accessor in vendor_accessor_arr:
        #     vendor_list.append(vendor_accessor.vendor_id)

        new_arr = []
        vendor_list.sort(reverse=True)
        for i in range(start_index, end_index):
            new_arr.append(vendor_list[i])
            #logger.info(i)
        #logger.info(new_arr)

        # if (status == 3 or status ==4):
        #     vendor_list =[]
        #     condition = Q(vendor_status__exact=status)
        #     vlist = Vendor.objects.filter(condition)
        #     for vendor_accessor in vlist:
        #         vendor_list.append(vendor_accessor.id)

        condition = None
        # search -monesh
        if (query == None):
            for vendor_id in new_arr:
                if condition is None:
                    condition = Q(id__exact=vendor_id) & Q(entity_id=self._entity_id())
                else:
                    condition |= Q(id__exact=vendor_id) &Q(entity_id=self._entity_id())
        else:
            name = query.get('name')
            panno = query.get('panno')
            gstno = query.get('gstno')
            code = query.get('code')
            type = query.get('type')
            renewal_date = query.get('renewal_date')
            rm_id = query.get('rm_id')
            vendor_status = query.get('vendor_status')
            #logger.info(query)


            condition = Q(modify_status=-1) &Q(entity_id=self._entity_id())
            if name != None:
                condition &= (Q(name__icontains=name)|Q(code__icontains=name))
            if panno != None:
                condition &= Q(panno__icontains=panno)
            if gstno != None:
                condition &= Q(gstno__icontains=gstno)
            # if code != None:
            #     condition &= Q(code__icontains=code)
            if type != None:
                condition &= Q(type__icontains=type)
            if renewal_date != None:
                condition &= Q(renewal_date__icontains=renewal_date)
            if rm_id != None:
                condition &= Q(rm_id__icontains=rm_id)
            if vendor_status != None:
                condition &= Q(vendor_status__icontains=vendor_status)
           # condition = (Q(name__icontains=name) | Q(panno__icontains=panno) | Q(gstno__icontains=gstno) | Q(code__icontains=code) | Q(type__icontains=type) | Q(renewal_date__icontains=renewal_date) | Q(rm_id__icontains=rm_id)| Q(vendor_status__icontains=vendor_status)) & Q(modify_status=-1)
        #logger.info(condition)

        # if (query is not None) & (condition is not None):
        #     vendorList = Vendor.objects.filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
        print(condition)
        if condition is not None:
            vendorList = Vendor.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[
                        vys_page.get_offset():vys_page.get_query_limit()]
            # vendorList = Vendor.objects.filter(condition).order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        vlist = NWisefinList()
        user_list = []
        for vendor in vendorList:
            user_list.append(vendor.created_by)
        user_list = set(user_list)
        user_list = list(user_list)
        utility_service = NWisefinUtilityService()
        user_list_obj = utility_service.get_user_info(request, user_list)
        logger.info(str(len(vendorList)))
        if len(vendorList) >= 1:
            for vendor in vendorList:
                vobj = VendorListData()
                vobj.set_panno(vendor.panno)
                vobj.set_id(vendor.id)
                vobj.set_name(vendor.name)
                vobj.set_gstno(vendor.gstno)
                # vobj.set_branch_count(vendor.branch_count)
                vobj.set_director_count(vendor.director_count)
                vobj.set_composite(vendor.composite)
                vobj.set_code(vendor.code)
                vobj.set_comregno(vendor.comregno)
                vobj.set_group(vendor.group)
                vobj.set_custcategory_id(vendor.custcategory_id)
                vobj.set_classification(vendor.classification)
                vobj.set_type(vendor.type)
                vobj.set_website(vendor.website)
                vobj.set_activecontract(vendor.activecontract)
                vobj.set_nocontract_reason(vendor.nocontract_reason)
                vobj.set_contractdate_from(vendor.contractdate_from)
                vobj.set_contractdate_to(vendor.contractdate_to)
                vobj.set_aproxspend(vendor.aproxspend)
                vobj.set_actualspend(vendor.actualspend)
                vobj.set_orgtype(vendor.orgtype)
                vobj.set_renewal_date(vendor.renewal_date)
                vobj.set_comregno(vendor.remarks)
                vobj.set_remarks(vendor.group)
                vobj.set_requeststatus(vendor.requeststatus)
                vobj.set_mainstatus(vendor.mainstatus)
                vobj.set_modify_ref_id(vendor.modify_ref_id)
                vobj.set_rm_id(vendor.rm_id)
                vobj.set_vendor_status(vendor.vendor_status)
                vobj.set_created_by(vendor.created_by)
                vobj.set_description(vendor.description)
                vobj.set_portal_flag(vendor.portal_flag)
                # vobj.set_risktype(vendor.risktype)
                # vobj.set_risktype_description(vendor.risktype_description)
                # vobj.set_risk_mitigant(vendor.risk_mitigant)
                # vobj.set_risk_mitigant_review(vendor.risk_mitigant_review)
                employee_service = EmployeeService(self._scope())
                rm_id = vobj.rm_id

                employee = Employee.objects.filter(id=rm_id)
                if len(employee) > 0:
                    rmname = employee_service.get_employee(rm_id, user_id)
                    vobj.rm_id = rmname
                else:
                    rm_dict = dict()
                    rm_dict['full_name'] = rm_id
                    rm_dict['id'] = rm_id
                    vobj.rm_id = rm_dict

                type_id = vobj.type
                type = getType(type_id)
                vobj.type = type

                for ul in user_list_obj['data']:
                    if ul['id'] == vendor.created_by:
                        vobj.set_created_by(ul)
                # status_obj = self.check_status(vendor.id,employee_id)
                # rolestatus_obj = self.check_role_status(role_obj,status_obj)
                # if(rolestatus_obj == True):
                vlist.append(vobj)
                vpage = NWisefinPaginator(vendorList, vys_page.get_index(), 10)
                vlist.set_pagination(vpage)
            return vlist
        else:
            vpage = NWisefinPaginator(vendorList, vys_page.get_index(), 10)
            vlist.set_pagination(vpage)
            return vlist

    def check_role_status(self,role_obj,status_obj):
        for i in role_obj:
            for j in status_obj:
                if i == j:
                    return True
        if Role.rm in status_obj :
              return True
        return False

    def get_checkerheader_list(self, request, user_id, status, vys_page, query, right_check):

            vendor_service = VendorService(self._scope())
            ismaker_obj = vendor_service.ismaker(user_id, True)


            employee_id = user_id
            vendor_list = []


            if (status == 3 or status == 4):
                # vendor_list = []
                condition = (Q(vendor_status__exact=status) | (Q(rm_id__exact=employee_id) &Q(vendor_status__exact=2)))&Q(entity_id=self._entity_id())
                vlist = Vendor.objects.using(self._current_app_schema()).filter(condition)
                for vendor_accessor in vlist:
                    vendor_list.append(vendor_accessor.id)

            if status == None:
                condition = Q(rm_id__exact=employee_id) &Q(vendor_status__exact=2)&Q(entity_id=self._entity_id())
                vlist = Vendor.objects.using(self._current_app_schema()).filter(condition)
                for vendor_accessor in vlist:
                    vendor_list.append(vendor_accessor.id)
            if right_check == True:
                condition = (Q(vendor_status__exact=3) | Q(vendor_status__exact=4) | (Q(rm_id__exact=employee_id) &Q(vendor_status__exact=2)))&Q(entity_id=self._entity_id())
                vlist = Vendor.objects.using(self._current_app_schema()).filter(condition)
                for vendor_accessor in vlist:
                    vendor_list.append(vendor_accessor.id)

            vendor_list = set(vendor_list)
            vendor_list = list(vendor_list)
            start_index = (vys_page.get_index() - 1) * 10
            end_index = start_index + 11
            if end_index > len(vendor_list):
                end_index = len(vendor_list)

            logger.info(str(start_index)+' '+str(end_index))
            logger.info(str(len(vendor_list)))
            # vendor_list = []
            vendorList = []
            # for vendor_accessor in vendor_accessor_arr:
            #     vendor_list.append(vendor_accessor.vendor_id)

            new_arr = []

            for i in range(start_index, end_index):
                new_arr.append(vendor_list[i])
                logger.info(str(i))
            logger.info(str(new_arr))

            # if (status == 3 or status ==4):
            #     vendor_list =[]
            #     condition = Q(vendor_status__exact=status)
            #     vlist = Vendor.objects.filter(condition)
            #     for vendor_accessor in vlist:
            #         vendor_list.append(vendor_accessor.id)

            condition = None
            # search -monesh
            if (query == None):
                for vendor_id in new_arr:
                    if condition is None:
                        condition = Q(id__exact=vendor_id)&Q(entity_id=self._entity_id())
                    else:
                        condition |= Q(id__exact=vendor_id)&Q(entity_id=self._entity_id())
            else:
                name = query.get('name')
                panno = query.get('panno')
                gstno = query.get('gstno')
                type = query.get('type')
                code = query.get('code')
                renewal_date = query.get('renewal_date')
                rm_id = query.get('rm_id')
                vendor_status = query.get('vendor_status')


                logger.info(str(query))
                condition = (Q(name__icontains=name) | Q(panno__icontains=panno) | Q(gstno__icontains=gstno)
                             |Q(type__icontains=type) | Q(code__icontains=code) | Q(renewal_date__icontains=renewal_date)
                             | Q(rm_id__icontains=rm_id) | Q(vendor_status__icontains=vendor_status)) & Q(modify_status=-1) &Q(entity_id=self._entity_id())
            logger.info(str(condition))
            # if (query is not None) & (condition is not None):
            #     vendorList = Vendor.objects.filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
            if condition is not None:
                vendorList = Vendor.objects.using(self._current_app_schema()).filter(condition)
            vlist = NWisefinList()
            emp_list = []
            for vendor in vendorList:
                emp_list.append(vendor.created_by)
            emp_list = set(emp_list)
            emp_list = list(emp_list)
            utility_service = NWisefinUtilityService()
            user_list_obj = utility_service.get_emp_info_by_id(request, emp_list)
            logger.info(str(len(vendorList)))

            for vendor in vendorList:
                vobj = VendorListData()
                vobj.set_panno(vendor.panno)
                vobj.set_id(vendor.id)
                vobj.set_name(vendor.name)
                vobj.set_gstno(vendor.gstno)
                # vobj.set_branch_count(vendor.branch_count)
                vobj.set_director_count(vendor.director_count)
                vobj.set_composite(vendor.composite)
                vobj.set_code(vendor.code)
                vobj.set_comregno(vendor.comregno)
                vobj.set_group(vendor.group)
                vobj.set_custcategory_id(vendor.custcategory_id)
                vobj.set_classification(vendor.classification)
                vobj.set_type(vendor.type)
                vobj.set_website(vendor.website)
                vobj.set_activecontract(vendor.activecontract)
                vobj.set_nocontract_reason(vendor.nocontract_reason)
                vobj.set_contractdate_from(vendor.contractdate_from)
                vobj.set_contractdate_to(vendor.contractdate_to)
                vobj.set_aproxspend(vendor.aproxspend)
                vobj.set_actualspend(vendor.actualspend)
                vobj.set_orgtype(vendor.orgtype)
                vobj.set_renewal_date(vendor.renewal_date)
                vobj.set_comregno(vendor.remarks)
                vobj.set_remarks(vendor.group)
                vobj.set_requeststatus(vendor.requeststatus)
                vobj.set_mainstatus(vendor.mainstatus)
                vobj.set_rm_id(vendor.rm_id)
                vobj.set_vendor_status(vendor.vendor_status)
                vobj.set_created_by(vendor.created_by)
                vobj.set_modify_ref_id(vendor.modify_ref_id)
                vobj.set_description(vendor.description)
                # vobj.set_risktype(vendor.risktype)
                # vobj.set_risktype_description(vendor.risktype_description)
                # vobj.set_risk_mitigant(vendor.risk_mitigant)
                # vobj.set_risk_mitigant_review(vendor.risk_mitigant_review)

                for ul in user_list_obj['data']:
                    if ul['id'] == vendor.created_by:
                        vobj.set_created_by(ul)
                # status_obj = self.check_status(vendor.id,employee_id)
                # rolestatus_obj = self.check_role_status(role_obj,status_obj)
                # if(rolestatus_obj == True):
                vlist.append(vobj)
            vpage = NWisefinPaginator(vendorList, vys_page.get_index(), 10)
            vlist.set_pagination(vpage)
            return vlist

        # else :
        #     return False

    def get_report(self,body_obj,employee_id,vys_page):
        condition=None
        # if 'type' in body_obj:
            # if 'from_date' in body_obj and 'to_date' in body_obj:
            #     condition=Q(requeststatus=int(body_obj['type'])) & Q(mainstatus=2) & Q(updated_date__range=[body_obj['from_date'], body_obj['to_date']])

        if 'request_for' in body_obj:
            if 'from_date' in body_obj and 'to_date' in body_obj:
                if body_obj['type'] != 2:
                    condition = Q(requeststatus=int(body_obj['type'])) & Q(vendor_status=body_obj['request_for']) &  Q(
                        created_date__range=[body_obj['from_date'], body_obj['to_date']])&Q(entity_id=self._entity_id())
                else:
                    condition = Q(requeststatus=int(body_obj['type'])) & Q(vendor_status=body_obj['request_for']) & Q(
                        updated_date__range=[body_obj['from_date'], body_obj['to_date']])&Q(entity_id=self._entity_id())
        vlist = NWisefinList()
        if condition is not None:
            vendorList = Vendor.objects.using(self._current_app_schema()).filter(condition)
        for vendor in vendorList:
            vobj = VendorListData()
            vobj.set_panno(vendor.panno)
            vobj.set_id(vendor.id)
            vobj.set_name(vendor.name)
            vobj.set_gstno(vendor.gstno)
            # vobj.set_branch_count(vendor.branch_count)
            vobj.set_director_count(vendor.director_count)
            vobj.set_composite(vendor.composite)
            vobj.set_code(vendor.code)
            vobj.set_comregno(vendor.comregno)
            vobj.set_group(vendor.group)
            vobj.set_custcategory_id(vendor.custcategory_id)
            vobj.set_classification(vendor.classification)
            vobj.set_type(vendor.type)
            vobj.set_website(vendor.website)
            vobj.set_activecontract(vendor.activecontract)
            vobj.set_nocontract_reason(vendor.nocontract_reason)
            vobj.set_contractdate_from(vendor.contractdate_from)
            vobj.set_contractdate_to(vendor.contractdate_to)
            vobj.set_aproxspend(vendor.aproxspend)
            vobj.set_actualspend(vendor.actualspend)
            vobj.set_orgtype(vendor.orgtype)
            vobj.set_renewal_date(vendor.renewal_date)
            vobj.set_comregno(vendor.remarks)
            vobj.set_remarks(vendor.group)
            vobj.set_requeststatus(vendor.requeststatus)
            vobj.set_mainstatus(vendor.mainstatus)
            vobj.set_rm_id(vendor.rm_id)
            # vobj.set_updated_date(vendor.updated_date)
            vobj.set_created_date(vendor.created_date)
            vobj.set_vendor_status(vendor.vendor_status)
            vobj.set_created_by(vendor.created_by)
            vobj.set_modify_ref_id(vendor.modify_ref_id)
            vobj.set_description(vendor.description)
            # vobj.set_risktype(vendor.risktype)
            # vobj.set_risktype_description(vendor.risktype_description)
            # vobj.set_risk_mitigant(vendor.risk_mitigant)
            # vobj.set_risk_mitigant_review(vendor.risk_mitigant_review)

            # for ul in user_list_obj['data']:
            #     if ul['id'] == vendor.created_by:
            #         vobj.set_created_by(ul)
            # status_obj = self.check_status(vendor.id,employee_id)
            # rolestatus_obj = self.check_role_status(role_obj,status_obj)
            # if(rolestatus_obj == True):
            vlist.append(vobj)
        # vpage = VysfinPaginator(vendorList, vys_page.get_index(), 10)
        # vlist.set_pagination(vpage)
        return vlist
