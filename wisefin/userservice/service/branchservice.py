from django.db import IntegrityError
from django.db.models import Q

from masterservice.util.masterutil import MasterStatus
from nwisefin.settings import logger
from userservice.data.response.branchresponse import EmployeeBranchResponse
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from userservice.service.addresscontactservice import AddressService,ContactService
from masterservice.service.designationservice import DesignationService
from masterservice.service.pincodeservice import PincodeService
from masterservice.service.districtservice import DistrictService
from masterservice.service.cityservice import CityService
from masterservice.service.stateservice import StateService
from utilityservice.data.response.nwisefinlist import NWisefinList
from userservice.models import EmployeeBranch ,Employee , BranchType ,Department, EmployeeContact,EmployeeAddress
from django.utils import timezone
import json
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from userservice.service.addresscontactservice import AddressService,ContactService
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from django.db.models import Q

class EmployeeBranchService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.USER_SERVICE)

    def create_branch(self, branch_obj, user_id, address_id, contact_id):
        if not branch_obj.get_id() is None:
            try:
                logger.error('EMPLOYEEBRANCH: EmployeeBranch Update Started')
                branch = EmployeeBranch.objects.using(self._current_app_schema()).filter(id=branch_obj.get_id()).update(code=branch_obj.get_code(),
                                                                                      name=branch_obj.get_name(),
                                                                                      tanno=branch_obj.get_tanno(),
                                                                                      glno=branch_obj.get_glno(),
                                                                                      stdno=branch_obj.get_stdno(),
                                                                                      incharge=branch_obj.get_incharge(),
                                                                                      address_id=address_id,
                                                                                      contact_id=contact_id,
                                                                                      assetcodeprimary=branch_obj.get_assetcodeprimary(),
                                                                                      control_office_branch = branch_obj.get_control_office_branch(),
                                                                                      updated_by=user_id,
                                                                                      updated_date=timezone.now(),entity=branch_obj.get_entity(),
                                                       entity_detail=branch_obj.get_entity_detail(),
                                                       gstin=branch_obj.get_gstin(),lastsync_date=timezone.now())
                branch = EmployeeBranch.objects.using(self._current_app_schema()).get(id=branch_obj.get_id())
                logger.error('EMPLOYEEBRANCH: EmployeeBranch Update Success' + str(branch))
                data = NWisefinSuccess()
                data.set_status(SuccessStatus.SUCCESS)
                data.set_message(SuccessMessage.UPDATE_MESSAGE)
                return data
            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except EmployeeBranch.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_EMPLOYEEBRANCH_ID)
                error_obj.set_description(ErrorDescription.INVALID_EMPLOYEEBRANCH_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        else:
            try:
                data=EmployeeBranch.objects.using(self._current_app_schema()).filter(name=branch_obj.get_name()).value()
                if (len(data) > 0):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                    return error_obj
                logger.error('EMPLOYEEBRANCH: EmployeeBranch Creation Started')
                branch = EmployeeBranch.objects.using(self._current_app_schema()).create(code=branch_obj.get_code(), name=branch_obj.get_name(),
                                                       tanno=branch_obj.get_tanno(), glno=branch_obj.get_glno(),
                                                       stdno=branch_obj.get_stdno(),
                                                       incharge=branch_obj.get_incharge(),
                                                       address_id=address_id,
                                                       contact_id=contact_id,
                                                       control_office_branch=branch_obj.get_control_office_branch(),
                                                       assetcodeprimary=branch_obj.get_assetcodeprimary(),
                                                       created_by=user_id,
                                                       entity=branch_obj.get_entity(),
                                                       entity_detail=branch_obj.get_entity_detail(),
                                                       gstin=branch_obj.get_gstin(),lastsync_date=timezone.now())
                logger.error('EMPLOYEEBRANCH: EmployeeBranch Creation Success' + str(branch))
                data = NWisefinSuccess()
                data.set_status(SuccessStatus.SUCCESS)
                data.set_message(SuccessMessage.CREATE_MESSAGE)
                return data
            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        # data_obj = EmployeeBranchResponse()
        # data_obj.set_id(branch.id)
        # data_obj.set_code(branch.code)
        # data_obj.set_name(branch.name)
        # data_obj.set_tanno(branch.tanno)
        # data_obj.set_glno(branch.glno)
        # data_obj.set_stdno(branch.stdno)
        # data_obj.set_incharge(branch.incharge)
        # data_obj.set_address_id(branch.address_id)
        # data_obj.set_contact_id(branch.contact_id)
        # data_obj.set_control_office_branch(branch.control_office_branch)
        # return data_obj
    def fetch_branch_list_dep(self):
        branchList = EmployeeBranch.objects.all().order_by('created_date').values('id', 'code', 'name')
        list_length = len(branchList)
        branch_list_data = NWisefinList()
        for data in branchList:
            branch_list_data.append(data)
        return branch_list_data
    def fetch_branch_using_code(self,employeebranch_id):
        employeebranch = EmployeeBranch.objects.using(self._current_app_schema()).get(code=employeebranch_id)
        emp_data = {"id": employeebranch.id, "code": employeebranch.code, "name": employeebranch.name,
                    "fullname": employeebranch.code + "--" + employeebranch.name,
                    "address_id": employeebranch.address_id,
                    "contact_id": employeebranch.contact_id,
                    "gstin": employeebranch.gstin}

        return json.dumps(emp_data)
    def fetch_employeebranch_get(self, branch_id,userid,request):
        try:
            branch = EmployeeBranch.objects.using(self._current_app_schema()).get(id=branch_id)
            data_obj = EmployeeBranchResponse()
            data_obj.set_id(branch.id)
            data_obj.set_code(branch.code)
            data_obj.set_name(branch.name)
            data_obj.set_tanno(branch.tanno)
            data_obj.set_glno(branch.glno)
            data_obj.set_stdno(branch.stdno)
            data_obj.set_incharge(branch.incharge)
            data_obj.set_status(branch.status)
            data_obj.set_address_id(branch.address_id)
            data_obj.set_assetcodeprimary(branch.assetcodeprimary)
            from utilityservice.service.api_service import ApiService
            scope=request.scope
            common_serv=ApiService(scope)
            if branch.address_id is not None:
                employeebranchaddress=EmployeeAddress.objects.using(self._current_app_schema()).get(id=branch.address_id)
                data_obj.address={'id':employeebranchaddress.id,'line1':employeebranchaddress.line1,'line2':employeebranchaddress.line2,'line3':employeebranchaddress.line3,
                'pincode':{'id':employeebranchaddress.pincode_id,'no':common_serv.fetch_pincode(employeebranchaddress.pincode_id,userid,request).no},'city':{'id':employeebranchaddress.city_id,
                'city_name':common_serv.fetch_city(employeebranchaddress.city_id,userid,request).name},'district':{'id':employeebranchaddress.district_id,
                                  'name':common_serv.fetch_district(employeebranchaddress.district_id,request).name},
                                  'state':{'id':employeebranchaddress.state_id,'name':common_serv.fetch_state(employeebranchaddress.state_id,request).name}}
            else:
                data_obj.address=""

            data_obj.set_contact_id(branch.contact_id)

            try:
                employeebranchcontact=EmployeeContact.objects.using(self._current_app_schema()).get(id=branch.contact_id)
                data_obj.contact={'type_id':employeebranchcontact.type_id,'name':employeebranchcontact.name,'designation':{'id':employeebranchcontact.designation_id,'name':common_serv.fetch_designation(employeebranchcontact.designation_id,request).name},
                'landline':employeebranchcontact.landline,'landline2':employeebranchcontact.landline2,'mobile':employeebranchcontact.mobile,
                'mobile2':employeebranchcontact.mobile2,'email':employeebranchcontact.email,'dob':employeebranchcontact.dob,
                'wedding_date':employeebranchcontact.wedding_date}
            except:
                data_obj.contact =""
            control_office_branch=EmployeeBranch.objects.using(self._current_app_schema()).get(id=branch.control_office_branch)

            data_obj.control_office_branch={'id':control_office_branch.id,'name':control_office_branch.name}
            data_obj.set_gstin(branch.gstin)
            return data_obj
        except EmployeeBranch.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_branch_ID)
            error_obj.set_description(ErrorDescription.INVALID_branch_ID)
            return error_obj
    def fetch_branch(self, branch_id):
        # try:
            branch = EmployeeBranch.objects.using(self._current_app_schema()).get(id=branch_id)
            data_obj = EmployeeBranchResponse()
            data_obj.set_id(branch.id)
            data_obj.set_code(branch.code)
            data_obj.set_name(branch.name)
            data_obj.set_tanno(branch.tanno)
            data_obj.set_glno(branch.glno)
            data_obj.set_stdno(branch.stdno)
            data_obj.set_incharge(branch.incharge)
            data_obj.set_status(branch.status)
            data_obj.set_address_id(branch.address_id)
            data_obj.set_contact_id(branch.contact_id)
            data_obj.set_assetcodeprimary(branch.assetcodeprimary)
            data_obj.set_control_office_branch(branch.control_office_branch)
            data_obj.set_gstin(branch.gstin)
            return data_obj
        # except EmployeeBranch.DoesNotExist:
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.INVALID_branch_ID)
        #     error_obj.set_description(ErrorDescription.INVALID_branch_ID)
        #     return error_obj

    def fetch_branch_list(self,request, vys_page):
        conditions = Q()
        if "code" in request.GET:
            conditions &= Q(code__icontains=request.GET.get("code"))
        if "name" in request.GET:
            conditions &= Q(name__icontains=request.GET.get("name"))
        branchList = EmployeeBranch.objects.using(self._current_app_schema()).filter(conditions).order_by('created_date')[
                     vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(branchList)
        branch_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for branch in branchList:
                data_obj = EmployeeBranchResponse()
                data_obj.set_id(branch.id)
                data_obj.set_code(branch.code)
                data_obj.set_name(branch.name)
                data_obj.set_tanno(branch.tanno)
                data_obj.set_glno(branch.glno)
                data_obj.set_stdno(branch.stdno)
                data_obj.set_incharge(branch.incharge)
                data_obj.set_address_id(branch.address_id)
                data_obj.set_contact_id(branch.contact_id)
                if branch.control_office_branch is not None:
                    data_obj.control_office_branch = EmployeeBranch.objects.using(self._current_app_schema()).get(
                        id=branch.control_office_branch).name
                else:
                    data_obj.control_office_branch = ""
                data_obj.set_status(branch.status)
                branch_list_data.append(data_obj)
                vpage = NWisefinPaginator(branchList, vys_page.get_index(), 10)
                branch_list_data.set_pagination(vpage)
        return branch_list_data

    def fetch_employeebranch_download(self,request):
        conditions = Q()
        branchList = EmployeeBranch.objects.using(self._current_app_schema()).filter(conditions).order_by('created_date')
        list_length = len(branchList)
        branch_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for branch in branchList:
                data_obj = EmployeeBranchResponse()
                data_obj.Code = branch.code
                data_obj.Name = branch.name
                data_obj.Tanno = branch.tanno
                data_obj.Glno = branch.glno
                data_obj.Stdno = branch.stdno
                data_obj.Incharge = branch.incharge
                data_obj.address_id = branch.address_id
                data_obj.contact_id = branch.contact_id
                if branch.control_office_branch is not None:
                    data_obj.control_office_branch=EmployeeBranch.objects.using(self._current_app_schema()).get(id=branch.control_office_branch).name
                else:
                    data_obj.control_office_branch = ""
                status = MasterStatus()
                if branch.status == status.Active:
                    data_obj.Status = status.Active_VALUE
                if branch.status == status.Inactive:
                    data_obj.Status = status.Inactive_VALUE
                branch_list_data.append(data_obj)
        return branch_list_data

    def delete_branch(self, branch_id):
        branch = EmployeeBranch.objects.using(self._current_app_schema()).filter(id=branch_id).delete()
        if branch[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_BRANCH_ID)
            error_obj.set_description(ErrorDescription.INVALID_BRANCH_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def get_contact_address_id(self, branch_id):
        branch = EmployeeBranch.objects.using(self._current_app_schema()).get(id=branch_id)

        data_obj = EmployeeBranchResponse()
        data_obj.set_address_id(branch.address)
        data_obj.set_contact_id(branch.contact)
        return data_obj

    def isbranchid_get(self,branch_code):
        try:
            branch=EmployeeBranch.objects.using(self._current_app_schema()).get(code = branch_code)
            return branch.id
        except:
            return None




    def Fetch_All_Branch_List(self, datefilter):
        condition = Q(lastsync_date__gte=datefilter)
        branchList = EmployeeBranch.objects.using(self._current_app_schema()).filter(condition)
        list_length = len(branchList)
        branch_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for branch in branchList:
                data_obj = EmployeeBranchResponse()
                data_obj.set_id(branch.id)
                data_obj.set_code(branch.code)
                data_obj.set_name(branch.name)
                data_obj.set_tanno(branch.tanno)
                data_obj.set_glno(branch.glno)
                data_obj.set_gstin(branch.gstin)
                data_obj.set_stdno(branch.stdno)
                data_obj.set_incharge(branch.incharge)
                data_obj.set_address_id(branch.address_id)
                data_obj.set_contact_id(branch.contact_id)
                data_obj.set_control_office_branch(branch.control_office_branch)
                contact_service = ContactService(self._scope())
                address_service = AddressService(self._scope())
                designation_service = DesignationService(self._scope())
                pincode_service = PincodeService(self._scope())
                district_service = DistrictService(self._scope())
                city_service = CityService(self._scope())
                state_service = StateService(self._scope())
                if branch.contact_id is not None:
                    contact = contact_service.fetch_employeecontact(branch.contact_id)
                    designation = contact.designation_id
                    designation = designation_service.fetch_designation(designation,None)
                    contact.designation_id = [designation]
                    data_obj.contact = [contact]
                else:
                    data_obj.contact = []

                if branch.address_id is not None:
                    address = address_service.fetch_employeeaddress(branch.address_id)
                    pincode = address.pincode_id
                    city = address.city_id
                    district = address.district_id
                    state = address.state_id
                    if pincode is not None:
                        pincode = pincode_service.fetch_pincode(pincode,None)
                        address.pincode_id = [pincode]
                    else:
                        address.pincode_id = []
                    if city is not None:
                        city = city_service.fetch_city(city,None)
                        address.city_id = [city]
                    else:
                        address.city_id = []
                    if district is not None:
                        district = district_service.fetchdistrict(district)
                        address.district_id =[district]
                    else:
                        address.district_id =[]
                    if state is not None:
                        state = state_service.fetchstate(state)
                        address.state_id = [state]
                    else:
                        address.state_id = []
                    data_obj.address = [address]
                else:
                    data_obj.address = []
                branch_list_data.append(data_obj)
        return branch_list_data
      
    def current_user_branch(self,user_id):
        contact_service = ContactService(self._scope())
        address_service = AddressService(self._scope())
        try:
            branchobj = Employee.objects.get(id=user_id)
            branch_id = branchobj.employee_branch_id

            branch = EmployeeBranch.objects.using(self._current_app_schema()).get(id=branch_id)
            data_obj = EmployeeBranchResponse()
            data_obj.set_id(branch.id)
            data_obj.set_code(branch.code)
            data_obj.set_name(branch.name)
            data_obj.set_tanno(branch.tanno)
            data_obj.set_glno(branch.glno)
            data_obj.set_stdno(branch.stdno)
            data_obj.set_incharge(branch.incharge)
            if branch.address_id is not None:
                data_obj.address=(address_service.fetch_employeeaddress(branch.address_id))
            else:
                data_obj.address =None
            if branch.contact_id is not None:
                data_obj.contact=(contact_service.fetch_employeecontact(branch.contact_id))
            else:
                data_obj.contact =None
            return data_obj
        except:
            return None

    def search_branch(self,vys_page,query):

        if query == None:
            branchList = EmployeeBranch.objects.using(self._current_app_schema()).all().values('id','code','name').order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        else:
            condition = Q(name__icontains=query) | Q(code__icontains=query)
            branchList = EmployeeBranch.objects.using(self._current_app_schema()).filter(condition).values('id','code','name').order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        branch_list_data = NWisefinList()
        for branch in branchList:
            data_obj = EmployeeBranchResponse()
            data_obj.set_id(branch['id'])
            data_obj.set_code(branch['code'])
            data_obj.set_name(branch['name'])
            branch_list_data.append(data_obj)
            vpage = NWisefinPaginator(branchList, vys_page.get_index(), 10)
            branch_list_data.set_pagination(vpage)
        return branch_list_data

    def branchtype(self,branch_code):
        branchtype = BranchType.objects.using(self._current_app_schema()).filter(branch__code=branch_code, entity_id=self._entity_id())
        if len(branchtype) > 0:
            for i in branchtype:
                i.is_branchoffice = True
                i.save()
        else:
            codition = Q(branch__code=branch_code) &Q(entity_id=self._entity_id())
            department = Department.objects.using(self._current_app_schema()).filter(codition)
            for dept in department:
                dept_id = dept.id
                branch_id = dept.branch_id
                try:
                    BranchType.objects.using(self._current_app_schema()).get(branch_id=branch_id, department_id=dept_id, entity_id=self._entity_id())
                except:
                    branchtype = BranchType.objects.using(self._current_app_schema()).create(branch_id=branch_id, department_id=dept_id,
                                                           is_branchoffice=True, entity_id=self._entity_id())

        return

    def current_emp_branch(self,emp_id):
        contact_service = ContactService(self._scope())
        address_service = AddressService(self._scope())
        try:
            branchobj = Employee.objects.get(id=emp_id)
            branch_id = branchobj.employee_branch_id

            branch = EmployeeBranch.objects.using(self._current_app_schema()).get(id=branch_id)
            data_obj = EmployeeBranchResponse()
            data_obj.set_id(branch.id)
            data_obj.set_code(branch.code)
            data_obj.set_name(branch.name)
            data_obj.set_tanno(branch.tanno)
            data_obj.set_glno(branch.glno)
            data_obj.set_stdno(branch.stdno)
            data_obj.set_incharge(branch.incharge)
            if branch.address_id is not None:
                data_obj.address=(address_service.fetch_employeeaddress(branch.address_id))
            else:
                data_obj.address =None
            if branch.contact_id is not None:
                data_obj.contact=(contact_service.fetch_employeecontact(branch.contact_id))
            else:
                data_obj.contact =None
            return data_obj
        except:
            return None


    def add_dept_branch(self):
        emp_branch=EmployeeBranch.objects.using(self._current_app_schema()).all().values_list('id',flat =True)
        emp_branch =list(emp_branch)

        department=Department.objects.using(self._current_app_schema()).filter(branch_id__in=emp_branch,name=None, entity_id=self._entity_id).values_list('branch_id',flat =True)

        department_list =list(department)

        missing_data= list(set(emp_branch) - set(department_list))

        if len(missing_data)>0:
            for i in missing_data:
                dept_obj=Department.objects.using(self._current_app_schema()).create(name=None,branch_id=i,is_sys=True, entity_id=self._entity_id())
                code = "DGRP" + str(dept_obj.id)
                dept_obj.code = code
                dept_obj.save()

            success_obj = NWisefinSuccess()
            success_obj.set_message("ADDED")
            return success_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_message("NO CHANGE")
            return success_obj

    def ctr_office_info(self,branch_json):
        branch_arr = branch_json['branch_arr']
        branch_obj=EmployeeBranch.objects.using(self._current_app_schema()).filter(code__in=branch_arr).values('id','code','name','control_office_branch')
        data=[]
        ctr_off_code=[]
        data_obj = NWisefinList()
        for i in branch_obj:
            brch_resp=EmployeeBranchResponse()
            brch_resp.set_id(i['id'])
            brch_resp.set_code(i['code'])
            brch_resp.set_name(i['name'])
            brch_resp.set_control_office_branch(i['control_office_branch'])
            ctr_off_code.append(i['control_office_branch'])
            data_obj.append(brch_resp)

        ctr_branch_obj = EmployeeBranch.objects.using(self._current_app_schema()).filter(code__in=ctr_off_code).values('id', 'code', 'name')

        for j in data_obj.data :
            control_office_branch=j.control_office_branch
            for ctr_off in ctr_branch_obj:
                ctr_code = ctr_off['code']

                if control_office_branch == ctr_code :
                    ctr_dict ={"code":ctr_code,"name":ctr_off['name'],"id":ctr_off['id']}
                    j.control_office_branch = ctr_dict

        return data_obj



    def fetch_branch_data(self,branch_json):
        branch_arr = branch_json['arr']
        branch_obj=EmployeeBranch.objects.using(self._current_app_schema()).filter(id__in=branch_arr).values('id','code','name')
        data_obj = NWisefinList()
        for i in branch_obj:
            brch_resp=EmployeeBranchResponse()
            brch_resp.set_id(i['id'])
            brch_resp.set_code(i['code'])
            brch_resp.set_name(i['name'])
            data_obj.append(brch_resp)
        return data_obj

    def search_empbranch(self, vys_page, query):
        if query is None:
            condition = Q(status=1)
        else:
            condition = (Q(code__icontains=query) | Q(name__icontains=query)) & Q(status=1)
        branchList = EmployeeBranch.objects.using(self._current_app_schema()).filter(condition)[
                     vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(branchList)
        branch_list_data = NWisefinList()
        if list_length > 0:
            for branch in branchList:
                data_obj = EmployeeBranchResponse()
                data_obj.set_id(branch.id)
                data_obj.set_code(branch.code)
                data_obj.set_name(branch.name)
                disp_name = branch.code + '--' + branch.name
                data_obj.set_codename(disp_name)
                branch_list_data.append(data_obj)
                vpage = NWisefinPaginator(branchList, vys_page.get_index(), 10)
                branch_list_data.set_pagination(vpage)
        return branch_list_data


    def fetch_branch_listid(self, list):
        branchList = EmployeeBranch.objects.using(self._current_app_schema()).filter(id__in=list)
        list_length = len(branchList)
        branch_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for branch in branchList:
                data_obj = EmployeeBranchResponse()
                data_obj.set_id(branch.id)
                data_obj.set_code(branch.code)
                data_obj.set_name(branch.name)
                data_obj.set_tanno(branch.tanno)
                data_obj.set_glno(branch.glno)
                data_obj.set_stdno(branch.stdno)
                data_obj.set_incharge(branch.incharge)
                data_obj.set_address_id(branch.address_id)
                data_obj.set_contact_id(branch.contact_id)
                data_obj.set_control_office_branch(branch.control_office_branch)
                branch_list_data.append(data_obj)

        return branch_list_data

    def empbranch(self, user_id):
        try:
            employee = Employee.objects.get(id=user_id)
            branch_id = employee.employee_branch_id
            branch = EmployeeBranch.objects.using(self._current_app_schema()).get(id=branch_id)
            data_obj = EmployeeBranchResponse()
            data_obj.set_id(branch.id)
            data_obj.set_code(branch.code)
            # data_obj.set_name(branch.name)
            fullname = '(' + branch.code + ') ' + branch.name
            data_obj.set_name(fullname)
            return data_obj
        except EmployeeBranch.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_branch_ID)
            error_obj.set_description(ErrorDescription.INVALID_branch_ID)
            return error_obj

    def employeebranch_activate_inactivate(self, request,branch_obj):
        if (int(branch_obj.status) == 0):

            employeebranch_data = EmployeeBranch.objects.using(self._current_app_schema()).filter(id=branch_obj.id).update(
                status=1)
        else:
            employeebranch_data = EmployeeBranch.objects.using(self._current_app_schema()).filter(id=branch_obj.id).update(
                status=0)
        employeebranch_var = EmployeeBranch.objects.using(self._current_app_schema()).get(id=branch_obj.id)
        data = EmployeeBranchResponse()
        data.set_status(employeebranch_var.status)
        status = employeebranch_var.status

        data.set_id(employeebranch_var.id)

        if status == 1:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.ACTIVATED)
            return data
        else:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.INACTIVATED)
            return data