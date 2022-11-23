import datetime
import json
import traceback

from nwisefin.settings import logger
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

now = datetime.datetime.now()
from masterservice.data.response.pmdbranchresponse import PmdBranchResponse
from masterservice.models import PmdBranch
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessMessage, SuccessStatus
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from userservice.service.addresscontactservice import AddressService, ContactService
from django.db.models import Q


class PmdBranchService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_pmd_branch(self, pmd_branch_obj, user_id):
        if not pmd_branch_obj.get_id() is None:
            logger.error('PMDBRANCH: PmdBranch Update Started')
            pmd_branch = PmdBranch.objects.using(self._current_app_schema()).filter(id=pmd_branch_obj.get_id(),
                                                                                    entity_id=self._entity_id(), ).update(
                branch_code=pmd_branch_obj.get_branch_code(),
                branch_name=pmd_branch_obj.get_branch_name(),
                location=pmd_branch_obj.get_location(),
                gst_number=pmd_branch_obj.get_gst_number(),
                remarks=pmd_branch_obj.get_remarks(),
                status=pmd_branch_obj.get_status(),
                updated_by=user_id,
                updated_date=now)

            pmd_branch = PmdBranch.objects.get(id=pmd_branch_obj.get_id())
            logger.error('PMDBRANCH: PmdBranch Update Success' + str(pmd_branch))

        else:
            logger.error('PMDBRANCH: PmdBranch Creation Started')

            pmd_branch = PmdBranch.objects.using(self._current_app_schema()).create(
                branch_code=pmd_branch_obj.get_branch_code(),
                branch_name=pmd_branch_obj.get_branch_name(),
                location=pmd_branch_obj.get_location(),
                gst_number=pmd_branch_obj.get_gst_number(),
                remarks=pmd_branch_obj.get_remarks(),
                status=pmd_branch_obj.get_status(),
                created_by=user_id, entity_id=self._entity_id(),
                created_date=now)
            logger.error('PMDBRANCH: PmdBranch Creation Success' + str(pmd_branch))
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.CREATE_MESSAGE)
            return data

        # data_obj = PmdBranchResponse()
        # data_obj.set_id(pmd_branch.id)
        # data_obj.set_branch_code(pmd_branch.branch_code)
        # data_obj.set_branch_name(pmd_branch.branch_name)
        # data_obj.set_location(pmd_branch.location)
        # data_obj.set_gst_number(pmd_branch.gst_number)
        # data_obj.set_status(pmd_branch.status)
        # data_obj.set_remarks(pmd_branch.remarks)
        # return data_obj
        # data=NWisefinSuccess()
        # data.set_status(SuccessStatus.SUCCESS)
        # data.set_message(SuccessMessage.CREATE_MESSAGE)
        # return data

    def fetch_pmd_branch_list(self, user_id, vys_page, request):
        try:
            conditions = Q()
            if 'name' in request.GET:
                conditions &= Q(branch_name__icontains=request.GET.get('name'))
            if 'code' in request.GET:
                conditions &= Q(branch_code__icontains=request.GET.get('code'))
            if 'location' in request.GET:
                conditions &= Q(location__icontains=request.GET.get('location'))

            branchList = PmdBranch.objects.using(self._current_app_schema()).filter(conditions).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
            # print(branchList)
            list_length = len(branchList)
            branch_list_data = NWisefinList()
            if list_length > 0:
                for branch in branchList:
                    data_obj = PmdBranchResponse()
                    data_obj.set_id(branch.id)
                    data_obj.set_branch_code(branch.branch_code)
                    data_obj.set_branch_name(branch.branch_name)
                    data_obj.set_location(branch.location)
                    data_obj.set_gst_number(branch.gst_number)
                    data_obj.set_status(branch.status)
                    data_obj.set_remarks(branch.remarks)
                    branch_list_data.append(data_obj)
                vpage = NWisefinPaginator(branchList, vys_page.get_index(), 10)
                branch_list_data.set_pagination(vpage)
                return branch_list_data
            else:
                return branch_list_data
        except:
            logger.error('ERROR_PmdBranch_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PmdBranch_ID)
            error_obj.set_description(ErrorDescription.INVALID_PmdBranch_ID)
            return error_obj

    def pmd_activate_inactivate(self, request, data_request_obj):
        if (int(data_request_obj.status) == 0):

            pmd_data = PmdBranch.objects.using(self._current_app_schema()).filter(id=data_request_obj.id).update(
                status=1)
        else:
            pmd_data = PmdBranch.objects.using(self._current_app_schema()).filter(id=data_request_obj.id).update(
                status=0)
        pmd_var = PmdBranch.objects.using(self._current_app_schema()).get(id=data_request_obj.id)
        data = PmdBranchResponse()
        data.set_status(pmd_var.status)
        status = pmd_var.status
        data.set_id(pmd_var.id)
        # return data
        if status == 1:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.ACTIVATED)

            return data
        if status == 0:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.INACTIVATED)
            return data
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj
