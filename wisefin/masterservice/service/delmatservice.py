import json
import traceback

import requests
from django.utils.timezone import now
from django.db import IntegrityError
from django.db.models import Q
from requests import Response

from masterservice.models import Delmat
from masterservice.util.masterutil import ModifyStatus, MasterStatus
# from masterservice.controller.delmatcontroller import get_authtoken_micro
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.prpo_api_service import ApiService
from nwisefin.settings import logger, SERVER_IP
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from masterservice.data.response.delmatresponse import DelmatResponse
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.util.masterutil import PrModifyStatus, PrRefType, DelmatType
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class DelmatService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_Delmat(self, delmat_obj, emp_id):
        if not delmat_obj.get_id() is None:
            try:
                logger.error('DELMAT: Delmat Update Started')
                delmat_var = Delmat.objects.using(self._current_app_schema()).filter(id=delmat_obj.get_id(),
                                                                                     entity_id=self._entity_id()).update(
                    commodity_id=delmat_obj.get_commodity(),
                    employee_id=delmat_obj.get_employee(),
                    type=delmat_obj.get_type(),
                    limit=delmat_obj.get_limit(),
                    two_level_approval=delmat_obj.get_two_level_approval(),
                    two_level_employee_id=delmat_obj.get_two_level_employee_id(),
                    delmat_status="PENDING",
                    updated_by=emp_id,
                    updated_date=now(),
                    entity_id=self._entity_id())
                delmat = Delmat.objects.using(self._current_app_schema()).get(id=delmat_obj.get_id(),
                                                                              entity_id=self._entity_id())
                self.audit_function(delmat, delmat.id, delmat.commodity_id, emp_id,
                                    PrModifyStatus.UPDATE, PrRefType.DELMAT)
                logger.error('DELMAT: Delmat Update Success' + str(delmat))
            except IntegrityError as error:
                logger.error('ERROR_Delmat_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Delmat.DoesNotExist:
                logger.error('ERROR_Delmat_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DELMAT_ID)
                error_obj.set_description(ErrorDescription.INVALID_DELMAT_ID)
                return error_obj
            except:
                logger.error('ERROR_Delmat_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        else:
            condition = (Q(type__exact=delmat_obj.get_type()) & Q(commodity_id__exact=delmat_obj.get_commodity())
                         & Q(employee_id__exact=delmat_obj.get_employee())) & Q(status=1) \
                        & Q(entity_id=self._entity_id())
            delmat = Delmat.objects.using(self._current_app_schema()).filter(condition)
            if len(delmat) > 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                return error_obj
            try:
                logger.error('DELMAT: Delmat Creation Started')
                delmat = Delmat.objects.using(self._current_app_schema()).create(
                    commodity_id=delmat_obj.get_commodity(),
                    employee_id=delmat_obj.get_employee(),
                    type=delmat_obj.get_type(),
                    limit=delmat_obj.get_limit(),
                    two_level_approval=delmat_obj.get_two_level_approval(),
                    two_level_employee_id=delmat_obj.get_two_level_employee_id(),
                    delmat_status="PENDING",
                    created_by=emp_id, entity_id=self._entity_id())
                self.audit_function(delmat, delmat.id, delmat.commodity_id, emp_id,
                                    PrModifyStatus.CREATE, PrRefType.DELMAT)
                logger.error('DELMAT: Delmat Creation Success' + str(delmat))
            except IntegrityError as error:
                logger.error('ERROR_Delmat_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_Delmat_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        delmat_data = DelmatResponse()
        delmat_data.set_id(delmat.id)
        delmat_data.set_commodity(delmat.commodity_id)
        delmat_data.set_employee(delmat.employee_id)
        delmat_data.set_type(delmat.type)
        delmat_data.set_limit(delmat.limit)
        delmat_data.set_delmat_status(delmat.delmat_status)
        delmat_data.set_status(delmat.status)
        return delmat_data

    def delete_Delmat(self, delmat_id, emp_id):
        delmat = Delmat.objects.using(self._current_app_schema()).filter(id=delmat_id,
                                                                         entity_id=self._entity_id()).delete()
        self.audit_function(delmat, delmat_id, delmat_id, emp_id, PrModifyStatus.DELETE, PrRefType.DELMAT)
        if delmat[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DELMAT_ID)
            error_obj.set_description(ErrorDescription.INVALID_DELMAT_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def fetch_Delmat(self, delmat_id, emp_id, request):
        try:
            delmat = Delmat.objects.using(self._current_app_schema()).get(id=delmat_id, entity_id=self._entity_id())
            delmat_data = DelmatResponse()

            apicall = ApiService(self._scope())
            master_commodity = apicall.fetch_commoditydata(request, delmat.commodity_id)  # commodity
            user_employee = apicall.fetch_employeedata(request, delmat.employee_id)  # employee

            delmat_data.set_id(delmat.id)
            delmat_data.set_commodity(master_commodity)
            delmat_data.set_employee(user_employee)
            delmat_data.set_type(delmat.type)
            delmat_data.set_limit(delmat.limit)
            delmat_data.set_delmat_status(delmat.delmat_status)
            delmat_data.set_status(delmat.status)
            delmat_data.set_type_id(delmat.type)
            if delmat.type == DelmatType.PR:
                delmat_data.set_type(DelmatType.PR_Type)
            elif delmat.type == DelmatType.PO:
                delmat_data.set_type(DelmatType.PO_Type)
            elif delmat.type == DelmatType.ECF:
                delmat_data.set_type(DelmatType.ECF_Type)
            elif delmat.type == DelmatType.BRANCH_EXP:
                delmat_data.set_type(DelmatType.BRANCH_EXP_Type)
            return delmat_data
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DELMAT_ID)
            error_obj.set_description(ErrorDescription.INVALID_DELMAT_ID)
            return error_obj

    def fetch_Delmat_list(self, vys_page, emp_id, request):
        try:
            logger.error('DELMAT: Delmat Summary Started')
            delmat_list = Delmat.objects.using(self._current_app_schema()).all().order_by('-created_date')[
                          vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(delmat_list)
            delmat_list_data = NWisefinList()
            # emp_arr = []
            # c_arr = []
            # if list_length > 0:
            #     for i in delmat_list:
            #         emp_arr.append(i.employee_id)
            #         c_arr.append(i.commodity_id)
            apicall = ApiService(self._scope())
            # emp_data = apicall.get_employee_details(request, emp_arr)
            # if isinstance(emp_data,Response):
            #     emp_data=json.loads(emp_data.content)
            #     pass
            # commodity_data = apicall.get_commodity(request, c_arr)

            if list_length <= 0:
                return delmat_list_data
            else:
                for delmat in delmat_list:
                    delmat_data = DelmatResponse()
                    delmat_data.set_id(delmat.id)
                    try:
                        emp_data = apicall.get_employee_details(request, delmat.employee_id)
                        if isinstance(emp_data, Response):
                            emp_data = json.loads(emp_data.content)
                        delmat_data.set_employee_id(emp_data)
                        delmat_data.set_employee_name(emp_data['name'])
                    except:
                        delmat_data.employee_id = ""
                        delmat_data.employee_name = ""
                    try:
                        comd_data = apicall.get_commodity_apexpense(request, delmat.commodity_id)
                        if isinstance(comd_data, Response):
                            comd_data = json.loads(comd_data.content)
                        delmat_data.set_commodity_id(comd_data)
                    except:
                        delmat_data.commodity_id = ""

                    delmat_data.set_type(delmat.type)
                    delmat_data.set_limit(delmat.limit)
                    delmat_data.set_delmat_status(delmat.delmat_status)
                    delmat_data.set_status(delmat.status)
                    delmat_data.set_remarks(delmat.remarks)
                    delmat_data.set_type_id(delmat.type)
                    if delmat.type == DelmatType.PR:
                        delmat_data.set_type(DelmatType.PR_Type)
                    elif delmat.type == DelmatType.PO:
                        delmat_data.set_type(DelmatType.PO_Type)
                    elif delmat.type == DelmatType.ECF:
                        delmat_data.set_type(DelmatType.ECF_Type)
                    elif delmat.type == DelmatType.BRANCH_EXP:
                        delmat_data.set_type(DelmatType.BRANCH_EXP_Type)
                    delmat_list_data.append(delmat_data)

                vpage = NWisefinPaginator(delmat_list, vys_page.get_index(), 10)
                delmat_list_data.set_pagination(vpage)
            logger.error('DELMAT: Delmat Summary' + str(delmat_list_data))
            return delmat_list_data

        except:
            logger.error('ERROR_Delmat_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DELMAT_ID)
            error_obj.set_description(ErrorDescription.INVALID_DELMAT_ID)
            return error_obj

    def fetch_delmat_download(self, emp_id, request):
        try:
            logger.error('DELMAT: Delmat Maker Download Summary Started')
            delmat_list = Delmat.objects.using(self._current_app_schema()).all().order_by('-created_date')
            list_length = len(delmat_list)
            delmat_list_data = NWisefinList()
            apicall = ApiService(self._scope())
            if list_length <= 0:
                return delmat_list_data
            else:
                for delmat in delmat_list:
                    delmat_data = DelmatResponse()
                    # delmat_data.Id = delmat.id
                    try:
                        emp_data = apicall.get_employee_details(request, delmat.employee_id)
                        # if isinstance(emp_data, Response):
                        emp_data = json.loads(emp_data.content)
                        # delmat_data.set_employee_id(emp_data)
                        delmat_data.Employee_Name = emp_data['name']
                    except:
                        # delmat_data.employee_id=""
                        delmat_data.Employee_Name = ""
                    try:
                        comd_data = apicall.get_commodity_apexpense(request, delmat.commodity_id)
                        # if isinstance(comd_data, Response):
                        comd_data = json.loads(comd_data.content)
                        delmat_data.Commodity_Name = comd_data['name']
                    except:
                        delmat_data.Commodity_Name = ""
                    delmat_data.Type = delmat.type
                    delmat_data.Limit = delmat.limit
                    delmat_data.Delmat_Status = delmat.delmat_status
                    # delmat_data.Status = delmat.status
                    status = MasterStatus()
                    if delmat.status == status.Active:
                        delmat_data.Status = status.Active_VALUE
                    if delmat.status == status.Inactive:
                        delmat_data.Status = status.Inactive_VALUE
                    delmat_data.Remarks = delmat.remarks
                    # delmat_data.type_id = delmat.type
                    if delmat.type == DelmatType.PR:
                        delmat_data.Type = DelmatType.PR_Type
                    elif delmat.type == DelmatType.PO:
                        delmat_data.Type = DelmatType.PO_Type
                    elif delmat.type == DelmatType.ECF:
                        delmat_data.Type = DelmatType.ECF_Type
                    elif delmat.type == DelmatType.BRANCH_EXP:
                        delmat_data.Type = DelmatType.BRANCH_EXP_Type
                    delmat_list_data.append(delmat_data)
            # logger.error('DELMAT: Delmat maker Download Summary' + str(delmat_list_data))
            return delmat_list_data
        except:
            logger.error('ERROR_Delmat_Excel_Download_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DELMAT_ID)
            error_obj.set_description(ErrorDescription.INVALID_DELMAT_ID)
            return error_obj



    def fetch_DelmatPending_list(self, vys_page, emp_id, request):
        try:
            logger.error('DELMAT APPROVAL: Delmat Approval Summary Started')
            condition = Q(delmat_status='PENDING') & Q(status=1) & Q(entity_id=self._entity_id())
            delmat_list = Delmat.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[
                          vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(delmat_list)
            delmat_list_data = NWisefinList()
            emp_arr = []
            c_arr = []
            # if list_length > 0:
            #     for i in delmat_list:
            #         emp_arr.append(i.employee_id)
            #         c_arr.append(i.commodity_id)
            apicall = ApiService(self._scope())
            # emp_data = apicall.get_employeedata(request)
            # print(json.loads(emp_data.content))
            # emp_data=json.loads(emp_data.content)
            # commodity_data = apicall.get_commodity_apexpense(request, c_arr)
            if list_length <= 0:
                return delmat_list_data
            else:
                for delmat in delmat_list:
                    delmat_data = DelmatResponse()
                    delmat_data.set_id(delmat.id)
                    try:
                        emp_data = apicall.get_employee_details(request, delmat.employee_id)
                        if isinstance(emp_data, Response):
                            emp_data = json.loads(emp_data.content)
                        delmat_data.set_employee_id(emp_data)
                        delmat_data.set_employee_name(emp_data['name'])
                    except:
                        delmat_data.employee_id = ""
                        delmat_data.employee_name = ""
                    try:
                        comd_data = apicall.get_commodity_apexpense(request, delmat.commodity_id)
                        if isinstance(comd_data, Response):
                            comd_data = json.loads(comd_data.content)
                        delmat_data.set_commodity_id(comd_data)
                    except:
                        delmat_data.commodity_id = ""
                    delmat_data.set_type(delmat.type)
                    delmat_data.set_limit(delmat.limit)
                    delmat_data.set_delmat_status(delmat.delmat_status)
                    delmat_data.set_status(delmat.status)
                    delmat_data.set_type_id(delmat.type)
                    if delmat.type == DelmatType.PR:
                        delmat_data.set_type(DelmatType.PR_Type)
                    elif delmat.type == DelmatType.PO:
                        delmat_data.set_type(DelmatType.PO_Type)
                    elif delmat.type == DelmatType.ECF:
                        delmat_data.set_type(DelmatType.ECF_Type)
                    elif delmat.type == DelmatType.BRANCH_EXP:
                        delmat_data.set_type(DelmatType.BRANCH_EXP_Type)
                    delmat_list_data.append(delmat_data)
                vpage = NWisefinPaginator(delmat_list, vys_page.get_index(), 10)
                delmat_list_data.set_pagination(vpage)
            # logger.error('DELMAT Approval: Delmat Approval Summary' + str(delmat_list_data))
            return delmat_list_data
        except:
            logger.error('ERROR_Delmat_Approval_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DELMAT_ID)
            error_obj.set_description(ErrorDescription.INVALID_DELMAT_ID)
            return error_obj

    def fetch_delmat_approval_download(self, emp_id, request):
        try:
            logger.error('DELMAT APPROVAL: Delmat Approval Download Summary Started')
            condition = Q(delmat_status='PENDING') & Q(status=1) & Q(entity_id=self._entity_id())
            delmat_list = Delmat.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')
            list_length = len(delmat_list)
            delmat_list_data = NWisefinList()
            emp_arr = []
            c_arr = []
            apicall = ApiService(self._scope())
            if list_length <= 0:
                return delmat_list_data
            else:
                for delmat in delmat_list:
                    delmat_data = DelmatResponse()
                    try:
                        emp_data = apicall.get_employee_details(request, delmat.employee_id)
                        if isinstance(emp_data, Response):
                            emp_data = json.loads(emp_data.content)
                        delmat_data.Employee_Name = emp_data['name']
                    except:
                        delmat_data.Employee_Name = ""
                    try:
                        comd_data = apicall.get_commodity_apexpense(request, delmat.commodity_id)
                        if isinstance(comd_data, Response):
                            comd_data = json.loads(comd_data.content)
                        delmat_data.Commodity_Name = comd_data['name']
                    except:
                        delmat_data.Commodity_Name = ""
                    delmat_data.Type = delmat.type
                    delmat_data.Limit = delmat.limit
                    delmat_data.Delmat_Status = delmat.delmat_status
                    status = MasterStatus()
                    if delmat.status == status.Active:
                        delmat_data.Status = status.Active_VALUE
                    if delmat.status == status.Inactive:
                        delmat_data.Status = status.Inactive_VALUE
                    if delmat.type == DelmatType.PR:
                        delmat_data.Type = DelmatType.PR_Type
                    elif delmat.type == DelmatType.PO:
                        delmat_data.Type = DelmatType.PO_Type
                    elif delmat.type == DelmatType.ECF:
                        delmat_data.Type = DelmatType.ECF_Type
                    elif delmat.type == DelmatType.BRANCH_EXP:
                        delmat_data.Type = DelmatType.BRANCH_EXP_Type
                    delmat_list_data.append(delmat_data)
            return delmat_list_data
        except:
            logger.error('ERROR_Delmat_Approval_Excel_Download_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DELMAT_ID)
            error_obj.set_description(ErrorDescription.INVALID_DELMAT_ID)
            return error_obj


    def fetch_Delmat_listActive(self, vys_page, emp_id, request):
        condition = Q(status=1) & Q(entity_id=self._entity_id())
        delmat_list = Delmat.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[
                      vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(delmat_list)
        delmat_list_data = NWisefinList()
        emp_arr = []
        c_arr = []
        if list_length > 0:
            for i in delmat_list:
                emp_arr.append(i.employee_id)
                c_arr.append(i.commodity_id)
        apicall = ApiService(self._scope())
        emp_data = apicall.get_employee(request, emp_arr)
        commodity_data = apicall.get_commodity(request, c_arr)
        if list_length <= 0:
            pass
        else:
            for delmat in delmat_list:
                delmat_data = DelmatResponse()
                delmat_data.set_id(delmat.id)
                delmat_data.set_employee_id(delmat.employee_id, emp_data['data'])
                delmat_data.set_commodity_id(delmat.commodity_id, commodity_data['data'])
                delmat_data.set_type(delmat.type)
                delmat_data.set_limit(delmat.limit)
                delmat_data.set_delmat_status(delmat.delmat_status)
                delmat_data.set_status(delmat.status)
                delmat_data.set_type_id(delmat.type)
                if delmat.type == DelmatType.PR:
                    delmat_data.set_type(DelmatType.PR_Type)
                elif delmat.type == DelmatType.PO:
                    delmat_data.set_type(DelmatType.PO_Type)
                elif delmat.type == DelmatType.ECF:
                    delmat_data.set_type(DelmatType.ECF_Type)
                elif delmat.type == DelmatType.BRANCH_EXP:
                    delmat_data.set_type(DelmatType.BRANCH_EXP_Type)
                delmat_list_data.append(delmat_data)
            vpage = NWisefinPaginator(delmat_list, vys_page.get_index(), 10)
            delmat_list_data.set_pagination(vpage)
        return delmat_list_data

    def fetch_Delmat_listInActive(self, vys_page, emp_id, request):
        condition = Q(status=0) & Q(entity_id=self._entity_id())
        delmat_list = Delmat.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[
                      vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(delmat_list)
        delmat_list_data = NWisefinList()
        emp_arr = []
        c_arr = []
        if list_length > 0:
            for i in delmat_list:
                emp_arr.append(i.employee_id)
                c_arr.append(i.commodity_id)
        apicall = ApiService(self._scope())
        emp_data = apicall.get_employee(request, emp_arr)
        commodity_data = apicall.get_commodity(request, c_arr)
        if list_length <= 0:
            pass
        else:
            for delmat in delmat_list:
                delmat_data = DelmatResponse()
                delmat_data.set_id(delmat.id)
                delmat_data.set_employee_id(delmat.employee_id, emp_data['data'])
                delmat_data.set_commodity_id(delmat.commodity_id, commodity_data['data'])
                delmat_data.set_type(delmat.type)
                delmat_data.set_limit(delmat.limit)
                delmat_data.set_delmat_status(delmat.delmat_status)
                delmat_data.set_status(delmat.status)
                delmat_data.set_type_id(delmat.type)
                if delmat.type == DelmatType.PR:
                    delmat_data.set_type(DelmatType.PR_Type)
                elif delmat.type == DelmatType.PO:
                    delmat_data.set_type(DelmatType.PO_Type)
                elif delmat.type == DelmatType.ECF:
                    delmat_data.set_type(DelmatType.ECF_Type)
                elif delmat.type == DelmatType.BRANCH_EXP:
                    delmat_data.set_type(DelmatType.BRANCH_EXP_Type)
                delmat_list_data.append(delmat_data)
            vpage = NWisefinPaginator(delmat_list, vys_page.get_index(), 10)
            delmat_list_data.set_pagination(vpage)
        return delmat_list_data

    def audit_function(self, audit_data, refid, relrefid, emp_id, action, reqstatus):
        if action == PrModifyStatus.DELETE:
            data = None
        else:
            data = audit_data.__dict__
            del data['_state']
        audit_service = MasterAuditService(self._scope())
        audit_obj = MasterAuditResponse()
        audit_obj.set_refid(refid)
        audit_obj.set_reqstatus(reqstatus)
        audit_obj.set_reftype(PrRefType.DELMAT)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(PrRefType.DELMAT)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)

    def status_UpdateApproved(self, delmat_data, emp_id):
        try:
            delmat_id = delmat_data.get('id')
            remarks = delmat_data.get('remarks')
            delmat = Delmat.objects.using(self._current_app_schema()).get(id=delmat_id, entity_id=self._entity_id())
            creatby = delmat.created_by
            if creatby != emp_id:
                delmat_var = Delmat.objects.using(self._current_app_schema()).filter(id=delmat_id,
                                                                                     entity_id=self._entity_id()).update(
                    delmat_status="APPROVED",
                    remarks=remarks,
                    updated_by=emp_id,
                    updated_date=now())
                delmat = Delmat.objects.using(self._current_app_schema()).get(id=delmat_id, entity_id=self._entity_id())
                self.audit_function(delmat, delmat.id, delmat.id, emp_id,
                                    PrModifyStatus.UPDATE, PrRefType.DELMAT)
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.APPROVED_MESSAGE)
                return success_obj
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_APPROVER_ID)
                error_obj.set_description(ErrorDescription.INVALID_APPROVER_ID)
                return error_obj

        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
            return error_obj

    def status_UpdateRejected(self, delmat_data, emp_id):
        try:
            delmat_id = delmat_data.get('id')
            remarks = delmat_data.get('remarks')
            delmat = Delmat.objects.using(self._current_app_schema()).get(id=delmat_id, entity_id=self._entity_id())
            creatby = delmat.created_by
            if creatby != emp_id:
                delmat_var = Delmat.objects.using(self._current_app_schema()).filter(id=delmat_id,
                                                                                     entity_id=self._entity_id()).update(
                    delmat_status="REJECTED",
                    remarks=remarks,
                    updated_by=emp_id,
                    updated_date=now())
                delmat = Delmat.objects.using(self._current_app_schema()).get(id=delmat_id, entity_id=self._entity_id())
                self.audit_function(delmat, delmat.id, delmat.id, emp_id,
                                    PrModifyStatus.UPDATE, PrRefType.DELMAT)
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.REJECTED_MESSAGE)
                return success_obj
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_APPROVER_ID)
                error_obj.set_description(ErrorDescription.INVALID_APPROVER_ID)
                return error_obj

        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
            return error_obj

    def search_DelmatAll(self, vys_page, delmat_obj, emp_id, request):
        condition = Q(status=1) & Q(entity_id=self._entity_id())
        if 'commodity_id' in delmat_obj:
            condition &= Q(commodity_id=delmat_obj['commodity_id'])
        if 'employee_id' in delmat_obj:
            condition &= Q(employee_id=delmat_obj['employee_id'])
        if 'type' in delmat_obj:
            condition &= Q(type__icontains=delmat_obj['type'])
        delmat_list = Delmat.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[
                      vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(delmat_list)
        delmat_list_data = NWisefinList()
        emp_arr = []
        c_arr = []
        if list_length > 0:
            for i in delmat_list:
                emp_arr.append(i.employee_id)
                c_arr.append(i.commodity_id)
        apicall = ApiService(self._scope())
        emp_data = apicall.get_employee(request, emp_arr)
        commodity_data = apicall.get_commodity(request, c_arr)
        if list_length <= 0:
            pass
        else:
            for delmat in delmat_list:
                delmat_data = DelmatResponse()
                delmat_data.set_id(delmat.id)
                delmat_data.set_employee_id(delmat.employee_id, emp_data['data'])
                delmat_data.set_commodity_id(delmat.commodity_id, commodity_data['data'])
                delmat_data.set_type(delmat.type)
                delmat_data.set_limit(delmat.limit)
                delmat_data.set_type_id(delmat.type)
                delmat_data.set_delmat_status(delmat.delmat_status)
                delmat_data.set_status(delmat.status)
                if delmat.type == DelmatType.PR:
                    delmat_data.set_type(DelmatType.PR_Type)
                elif delmat.type == DelmatType.PO:
                    delmat_data.set_type(DelmatType.PO_Type)
                elif delmat.type == DelmatType.ECF:
                    delmat_data.set_type(DelmatType.ECF_Type)
                elif delmat.type == DelmatType.BRANCH_EXP:
                    delmat_data.set_type(DelmatType.BRANCH_EXP_Type)
                delmat_list_data.append(delmat_data)
            vpage = NWisefinPaginator(delmat_list, vys_page.get_index(), 10)
            delmat_list_data.set_pagination(vpage)
        return delmat_list_data

    def search_DelmatAll_mst(self, vys_page, delmat_obj, emp_id, request):
        logger.error('DELMAT Search: Delmat Search Summary Started')
        status = request.GET.get('status', 2)
        if status == '':
            status = 2
        condition = Q() & Q(entity_id=self._entity_id())
        if int(status) != 2:
            condition = Q(status=status) & Q(entity_id=self._entity_id())
        # condition = Q(status=1) & Q(entity_id=self._entity_id())
        if 'commodity_id' in delmat_obj:
            condition &= Q(commodity_id=delmat_obj['commodity_id'])
        if 'employee_id' in delmat_obj:
            condition &= Q(employee_id=delmat_obj['employee_id'])
        if 'type' in delmat_obj:
            condition &= Q(type__icontains=delmat_obj['type'])
        # if 'status' in delmat_obj:
        #     condition &= Q(status__icontains=delmat_obj['status'])
        delmat_list = Delmat.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[
                      vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(delmat_list)
        delmat_list_data = NWisefinList()
        emp_arr = []
        c_arr = []
        if list_length > 0:
            for i in delmat_list:
                emp_arr.append(i.employee_id)
                c_arr.append(i.commodity_id)
        apicall = ApiService(self._scope())
        emp_data = apicall.get_employee(request, emp_arr)
        commodity_data = apicall.get_commodity(request, c_arr)
        if list_length <= 0:
            pass
        else:
            for delmat in delmat_list:
                delmat_data = DelmatResponse()
                delmat_data.set_id(delmat.id)
                emp_data = apicall.get_employee_details(request, delmat.employee_id)
                if isinstance(emp_data, Response):
                    emp_data = json.loads(emp_data.content)
                delmat_data.set_employee_id(emp_data)
                delmat_data.set_employee_name(emp_data['name'])
                comd_data = apicall.get_commodity_apexpense(request, delmat.commodity_id)
                if isinstance(comd_data, Response):
                    comd_data = json.loads(comd_data.content)
                delmat_data.set_commodity_id(comd_data)
                delmat_data.set_type(delmat.type)
                delmat_data.set_limit(delmat.limit)
                delmat_data.set_type_id(delmat.type)
                delmat_data.set_delmat_status(delmat.delmat_status)
                delmat_data.set_status(delmat.status)
                if delmat.type == DelmatType.PR:
                    delmat_data.set_type(DelmatType.PR_Type)
                elif delmat.type == DelmatType.PO:
                    delmat_data.set_type(DelmatType.PO_Type)
                elif delmat.type == DelmatType.ECF:
                    delmat_data.set_type(DelmatType.ECF_Type)
                elif delmat.type == DelmatType.BRANCH_EXP:
                    delmat_data.set_type(DelmatType.BRANCH_EXP_Type)
                delmat_list_data.append(delmat_data)
            vpage = NWisefinPaginator(delmat_list, vys_page.get_index(), 10)
            delmat_list_data.set_pagination(vpage)
        logger.error('DELMAT Search: Delmat Search Summary' + str(delmat_list_data))
        return delmat_list_data

    def search_DelmatPendingAll(self, delmat_obj, emp_id, vys_page, request):
        condition = Q(delmat_status='PENDING') & Q(status=1) & Q(entity_id=self._entity_id())
        if 'commodity_id' in delmat_obj:
            condition &= Q(commodity_id=delmat_obj['commodity_id'])
        if 'employee_id' in delmat_obj:
            condition &= Q(employee_id=delmat_obj['employee_id'])
        if 'type' in delmat_obj:
            condition &= Q(type__icontains=delmat_obj['type'])
        print(condition)

        delmat_list = Delmat.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[
                      vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(delmat_list)
        delmat_list_data = NWisefinList()
        emp_arr = []
        c_arr = []
        if list_length > 0:
            for i in delmat_list:
                emp_arr.append(i.employee_id)
                c_arr.append(i.commodity_id)
        apicall = ApiService(self._scope())
        emp_data = apicall.get_employee(request, emp_arr)
        commodity_data = apicall.get_commodity(request, c_arr)
        if list_length <= 0:
            pass
        else:
            for delmat in delmat_list:
                delmat_data = DelmatResponse()
                delmat_data.set_id(delmat.id)
                delmat_data.set_employee_id(delmat.employee_id, emp_data['data'])
                delmat_data.set_commodity_id(delmat.commodity_id, commodity_data['data'])
                delmat_data.set_type(delmat.type)
                delmat_data.set_limit(delmat.limit)
                delmat_data.set_delmat_status(delmat.delmat_status)
                delmat_data.set_type_id(delmat.type)
                if delmat.type == DelmatType.PR:
                    delmat_data.set_type(DelmatType.PR_Type)
                elif delmat.type == DelmatType.PO:
                    delmat_data.set_type(DelmatType.PO_Type)
                elif delmat.type == DelmatType.ECF:
                    delmat_data.set_type(DelmatType.ECF_Type)
                elif delmat.type == DelmatType.BRANCH_EXP:
                    delmat_data.set_type(DelmatType.BRANCH_EXP_Type)
                delmat_list_data.append(delmat_data)
            vpage = NWisefinPaginator(delmat_list, vys_page.get_index(), 10)
            delmat_list_data.set_pagination(vpage)
        return delmat_list_data

    def search_DelmatPendingAll_mst(self, delmat_obj, emp_id, vys_page, request):
        logger.error('DELMAT Approval Search: Delmat Approval Search Summary Started')
        condition = Q(delmat_status='PENDING') & Q(status=1) & Q(entity_id=self._entity_id())
        if 'commodity_id' in delmat_obj:
            condition &= Q(commodity_id=delmat_obj['commodity_id'])
        if 'employee_id' in delmat_obj:
            condition &= Q(employee_id=delmat_obj['employee_id'])
        if 'type' in delmat_obj:
            condition &= Q(type__icontains=delmat_obj['type'])

        delmat_list = Delmat.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[
                      vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(delmat_list)
        delmat_list_data = NWisefinList()
        emp_arr = []
        c_arr = []
        if list_length > 0:
            for i in delmat_list:
                emp_arr.append(i.employee_id)
                c_arr.append(i.commodity_id)
        apicall = ApiService(self._scope())
        emp_data = apicall.get_employee(request, emp_arr)
        commodity_data = apicall.get_commodity(request, c_arr)
        if list_length <= 0:
            pass
        else:
            for delmat in delmat_list:
                delmat_data = DelmatResponse()
                delmat_data.set_id(delmat.id)
                emp_data = apicall.get_employee_details(request, delmat.employee_id)
                if isinstance(emp_data, Response):
                    emp_data = json.loads(emp_data.content)
                delmat_data.set_employee_id(emp_data)
                delmat_data.set_employee_name(emp_data['name'])
                comd_data = apicall.get_commodity_apexpense(request, delmat.commodity_id)
                if isinstance(comd_data, Response):
                    comd_data = json.loads(comd_data.content)
                delmat_data.set_commodity_id(comd_data)
                delmat_data.set_type(delmat.type)
                delmat_data.set_limit(delmat.limit)
                delmat_data.set_delmat_status(delmat.delmat_status)
                delmat_data.set_type_id(delmat.type)
                if delmat.type == DelmatType.PR:
                    delmat_data.set_type(DelmatType.PR_Type)
                elif delmat.type == DelmatType.PO:
                    delmat_data.set_type(DelmatType.PO_Type)
                elif delmat.type == DelmatType.ECF:
                    delmat_data.set_type(DelmatType.ECF_Type)
                elif delmat.type == DelmatType.BRANCH_EXP:
                    delmat_data.set_type(DelmatType.BRANCH_EXP_Type)
                delmat_list_data.append(delmat_data)
            vpage = NWisefinPaginator(delmat_list, vys_page.get_index(), 10)
            delmat_list_data.set_pagination(vpage)
        logger.error('DELMAT Approval Search: Delmat Approval Search Summary' + str(delmat_list_data))
        return delmat_list_data

    def updatestatus(self, delmat_id, status, emp_id):
        status = int(status)
        delmat_id = int(delmat_id)
        if status == 1:
            delmatget = Delmat.objects.using(self._current_app_schema()).get(id=delmat_id, entity_id=self._entity_id())
            delmat_comm = delmatget.commodity_id
            delmat_emp = delmatget.employee_id
            delmat_type = delmatget.type
            delmat_status = delmatget.status
            dellist1 = Delmat.objects.using(self._current_app_schema()).filter(type__exact=delmat_type,
                                                                               commodity_id__exact=delmat_comm,
                                                                               employee_id__exact=delmat_emp,
                                                                               entity_id=self._entity_id())
            list_length1 = len(dellist1)
            if list_length1 > 0:
                for delmat in dellist1:
                    delmat_data = DelmatResponse()
                    delmat_data.set_id(delmat.id)
                    if delmat.status == 1:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                        error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                        return error_obj

                    elif delmat.status == 0:
                        dellist2 = Delmat.objects.using(self._current_app_schema()).filter(type__exact=delmat_type,
                                                                                           commodity_id__exact=delmat_comm,
                                                                                           employee_id__exact=delmat_emp,
                                                                                           status=1,
                                                                                           entity_id=self._entity_id())
                        list_length2 = len(dellist2)
                        if list_length2 == 0:
                            delmat_update = Delmat.objects.using(self._current_app_schema()).filter(
                                id=delmat_id).update(status=status,
                                                     updated_by=emp_id,
                                                     updated_date=now(), entity_id=self._entity_id())

                            success_obj = NWisefinSuccess()
                            success_obj.set_status(SuccessStatus.SUCCESS)
                            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                            return success_obj
                        else:
                            traceback.print_exception(True)
                            error_obj = NWisefinError()
                            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                            error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                            return error_obj

        if status == 0:
            delmat_update = Delmat.objects.using(self._current_app_schema()).filter(id=delmat_id).update(status=status,
                                                                                                         updated_by=emp_id,
                                                                                                         updated_date=now(),
                                                                                                         entity_id=self._entity_id())
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj

    def delmat_activate_inactivate(self, request, fin_obj):

        if (int(fin_obj.status) == 0):

            fin_data = Delmat.objects.using(self._current_app_schema()).filter(id=fin_obj.id).update(
                status=1)
        else:
            fin_data = Delmat.objects.using(self._current_app_schema()).filter(id=fin_obj.id).update(
                status=0)
        delmat_var = Delmat.objects.using(self._current_app_schema()).get(id=fin_obj.id)
        data = DelmatResponse()
        data.set_status(delmat_var.status)
        status = delmat_var.status
        # print(status)
        data.set_id(delmat_var.id)
        # return data
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


    # mono to micro sync:
    # mono to micro sync: create
    def create_Delmat_mtom(self, delmat_obj, action, emp_id, request):
        try:
            master_apicall = ApiService(self._scope())
            master_commodity = master_apicall.fetch_commoditycode(request, delmat_obj.get_commodity_code())
            print('master_commodity', master_commodity)
            commodity_id = master_commodity["id"]
            # emp_getbycode?code=''
            # for cat & subcat from pd rems
            # auth_token = get_authtoken_micro()
            # token = 'Token ' + str(auth_token)
            token = request.headers['Authorization']
            ip_addr = SERVER_IP
            logger.error("ip_addr " + str(ip_addr))
            print('employee_code', delmat_obj.get_employee_code())
            url = ip_addr + '/usrserv/emp_getbycode?code=' + str(delmat_obj.get_employee_code())
            logger.error("/usrserv/emp_getbycode?  url: " + str(url))
            headers = {"content-type": "application/json", "Authorization": "" + token + ""}
            emp_getbycode_resp = requests.get(url, headers=headers, verify=False)
            print('emp_getbycode_resp', emp_getbycode_resp)
            api_resp = json.loads(emp_getbycode_resp.content)
            print('api_resp', api_resp)
            employee_id = api_resp.get('data')[0].get("id")
            print('employee_id ', employee_id)

        except Exception as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

        if action == 'active' or action == 'inactive':
            try:
                commodity_update = Delmat.objects.filter(id=delmat_obj.get_id(), entity_id=self._entity_id()).update(
                    status=delmat_obj.get_status(),
                    updated_date=now(),
                    updated_by=emp_id)

                delmat = Delmat.objects.get(id=delmat_obj.get_id(), entity_id=self._entity_id())
                delmat_update = {'id': delmat.id,
                                 # 'code': delmat_obj.get_code(),
                                 'status': delmat_obj.get_status(),
                                 'updated_date': now(),
                                 'updated_by': emp_id}
                self.audit_function(delmat, delmat.id, delmat.id, emp_id, ModifyStatus.update, PrRefType.DELMAT)
                # logger.error("delmat mtom  active inactive " + str(delmat_obj.get_code()))
            except Exception as excep:
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(str(excep))
                return error_obj

        if action == 'update':
            try:
                delmat_var = Delmat.objects.using(self._current_app_schema()).filter(id=delmat_obj.get_id(),
                                                                                     entity_id=self._entity_id()).update(
                    commodity_id=commodity_id,
                    employee_id=employee_id,
                    type=delmat_obj.get_type(),
                    limit=delmat_obj.get_limit(),
                    delmat_status="PENDING",
                    updated_by=emp_id,
                    updated_date=now())
                delmat = Delmat.objects.using(self._current_app_schema()).get(id=delmat_obj.get_id(),
                                                                              entity_id=self._entity_id())
                self.audit_function(delmat, delmat.id, delmat.commodity_id, emp_id,
                                    PrModifyStatus.UPDATE, PrRefType.DELMAT)

            except IntegrityError as error:
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Delmat.DoesNotExist:
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DELMAT_ID)
                error_obj.set_description(ErrorDescription.INVALID_DELMAT_ID)
                return error_obj
            except:
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        if action == 'create':

            condition = (Q(type__exact=delmat_obj.get_type()) & Q(commodity_id=commodity_id)
                         & Q(employee_id=employee_id)) & Q(status=1) & Q(entity_id=self._entity_id())
            delmat = Delmat.objects.using(self._current_app_schema()).filter(condition)
            if len(delmat) > 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                return error_obj
            try:
                delmat = Delmat.objects.using(self._current_app_schema()).create(commodity_id=commodity_id,
                                                                                 employee_id=employee_id,
                                                                                 type=delmat_obj.get_type(),
                                                                                 limit=delmat_obj.get_limit(),
                                                                                 delmat_status="PENDING",
                                                                                 created_by=emp_id,
                                                                                 entity_id=self._entity_id())
                self.audit_function(delmat, delmat.id, delmat.commodity_id, emp_id,
                                    PrModifyStatus.CREATE, PrRefType.DELMAT)
            except IntegrityError as error:
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        delmat_data = DelmatResponse()
        delmat_data.set_id(delmat.id)
        delmat_data.set_commodity(delmat.commodity_id)
        delmat_data.set_employee(delmat.employee_id)
        delmat_data.set_type(delmat.type)
        delmat_data.set_limit(delmat.limit)
        delmat_data.set_delmat_status(delmat.delmat_status)
        delmat_data.set_status(delmat.status)
        return delmat_data

    # mono to micro sync: approve
    def delmatapprove_mtom(self, delmat_data, emp_id, request):
        try:
            logger.error("employee_code:" + str(delmat_data.get('employee_code')))
            logger.error("commodity_code:" + str(delmat_data.get('commodity_code')))
            logger.error("delmat_type:" + str(delmat_data.get('delmat_type')))
            print("employee_code:", delmat_data.get('employee_code'))
            print("commodity_code:", delmat_data.get('commodity_code'))
            print("delmat_type:", delmat_data.get('delmat_type'))
            # commodity_id = Commodity.objects.using(self._current_app_schema()).get(code=delmat_data.get('commodity_code')).id
            # employee_id = Employee.objects.using(self._current_app_schema()).get(code=delmat_data.get('employee_code')).id
            apicall = ApiService(self._scope())
            master_commodity = apicall.get_commoditycode(request, delmat_data.get('commodity_code'))
            user_employee = apicall.get_employeecode(request, delmat_data.get('employee_code'))
            commodity_id = master_commodity['id']
            employee_id = user_employee['id']
            delmat_type = delmat_data.get('delmat_type')
            remarks = delmat_data.get('remarks')

            print(commodity_id, employee_id, delmat_type)
            logger.error("DELMAT APPROVE")
            logger.error(str(commodity_id) + str(employee_id) + str(delmat_type))

            condition = Q(commodity_id=commodity_id) & Q(employee_id=employee_id) & Q(type=delmat_type) & Q(status=1) \
                        & Q(entity_id=self._entity_id())
            delmat_var = Delmat.objects.using(self._current_app_schema()).filter(condition).update(
                delmat_status="APPROVED",
                remarks=remarks,
                updated_by=emp_id,
                updated_date=now(), entity_id=self._entity_id())
            delmat = Delmat.objects.using(self._current_app_schema()).get(condition)
            self.audit_function(delmat, delmat.id, delmat.id, emp_id,
                                PrModifyStatus.UPDATE, PrRefType.DELMAT)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.APPROVED_MESSAGE)
            return success_obj

        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
            return error_obj

    # mono to micro sync: reject
    def delmatreject_mtom(self, delmat_data, emp_id, request):
        try:
            logger.error("employee_code:" + str(delmat_data.get('employee_code')))
            logger.error("commodity_code:" + str(delmat_data.get('commodity_code')))
            logger.error("delmat_type:" + str(delmat_data.get('delmat_type')))
            print("employee_code:", delmat_data.get('employee_code'))
            print("commodity_code:", delmat_data.get('commodity_code'))
            print("delmat_type:", delmat_data.get('delmat_type'))

            apicall = ApiService(self._scope())
            master_commodity = apicall.get_commoditycode(request, delmat_data.get('commodity_code'))
            user_employee = apicall.get_employeecode(request, delmat_data.get('employee_code'))
            commodity_id = master_commodity['id']
            employee_id = user_employee['id']
            delmat_type = delmat_data.get('delmat_type')
            remarks = delmat_data.get('remarks')

            print(commodity_id, employee_id, delmat_type)
            logger.error("DELMAT REJECT")
            logger.error(str(commodity_id) + str(employee_id) + str(delmat_type))
            condition = Q(commodity_id=commodity_id) & Q(employee_id=employee_id) & Q(type=delmat_type) & Q(status=1) \
                        & Q(entity_id=self._entity_id())
            delmat_var = Delmat.objects.using(self._current_app_schema()).filter(condition).update(
                delmat_status="REJECTED",
                remarks=remarks,
                updated_by=emp_id,
                updated_date=now(), entity_id=self._entity_id())
            delmat = Delmat.objects.using(self._current_app_schema()).get(condition)
            self.audit_function(delmat, delmat.id, delmat.id, emp_id,
                                PrModifyStatus.UPDATE, PrRefType.DELMAT)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.REJECTED_MESSAGE)
            return success_obj
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
            return error_obj

    def search_employeelimit(self, query, emp_id, vys_page, request):
        commodityid = query.get('commodityid')
        type = query.get('type')
        employee = query.get('employee')
        # print(employee)
        apicall = ApiService(self._scope())
        if type == DelmatType.PR_Type:
            typeid = DelmatType.PR
        elif type == DelmatType.PO_Type:
            typeid = DelmatType.PO
        elif type == DelmatType.ECF_Type:
            typeid = DelmatType.ECF
        elif type == DelmatType.BRANCH_EXP_Type:
            typeid = DelmatType.BRANCH_EXP
        # apicall = EmployeeAPI()
        user_employee = apicall.get_employeename(request, employee)
        # user_employee = json.loads(user_employee.content)
        employee1 = user_employee['data'][0]
        employee_id = employee1['id']
        print(employee1)
        # employee_id = []
        # for i in employee1:
        #     employee_id.append(i["id"])
        condition = Q(commodity_id=commodityid) & Q(type=typeid) & Q(employee_id__in=employee_id) \
                    & Q(status=1) & Q(delmat_status="APPROVED") & Q(entity_id=self._entity_id())
        delmatlist = Delmat.objects.using(self._current_app_schema()).filter(condition)
        list_length = len(delmatlist)
        employee_list = []
        limit_list = []
        for delmat in delmatlist:
            if delmat.employee_id != emp_id:
                delmat_data = DelmatResponse()
                delmat_data.set_employee(delmat.employee_id)
                limit = int(delmat.limit)
                del_limit = round(limit, 2)
                delmat_data.set_limit(delmat.limit)
                employee_list.append(delmat.employee_id)
                limit_list.append(str(del_limit))
        employeeList_data1 = []
        user_employee = apicall.get_employeedata(request)
        print("1", user_employee)
        # print("2",user_employee.content)
        # user_employee = json.loads(user_employee.content)
        employee1 = user_employee['data'][0]
        empp = employee1['id']

        employeeList1 = []
        for i in empp:
            employeeList1.append(i)
        for i in employeeList1:
            if (i != emp_id) & (i not in employee_list):
                employeeList_data1.append(i)

        user_employee = apicall.get_employee1(request, employee_list)
        # user_employee = json.loads(user_employee.content)
        # employeeList = user_employee['data'][0]
        employeeList = user_employee['data']
        print(employeeList)
        print("limit_list", limit_list)
        employeeList_data = NWisefinList()
        for (i, emp) in zip(limit_list, employeeList):
            design = emp['designation']
            if (design == None):
                designation = ''
            else:
                designation = design
            data = {"id": emp['id'],
                    "code": emp['code'],
                    "name": emp['name'],
                    "limit": i,
                    "full_name": '(' + emp['code'] + ')' ' ' + emp['name'] + ' ' '--' + designation + ' ' '--' + i}
            employeeList_data.append(data)

        if (employee != '') & (employee is not None):
            user_employee = apicall.get_employeename_data(request, employeeList_data1, employee)
            employeeListl = user_employee['data']
        else:
            employee = ''
            user_employee = apicall.get_employeename_data(request, employeeList_data1, employee)
            employeeListl = user_employee['data']
        print(employeeListl)
        for i in employeeListl:
            design = i['designation']
            if (design == None):
                designation = ''
            else:
                designation = design
            data = {"id": i['id'],
                    "code": i['code'],
                    "name": i['name'],
                    "full_name": '(' + i['code'] + ')' ' ' + i['name'] + ' ' '--' + designation}
            employeeList_data.append(data)

        return employeeList_data
