import json

from datetime import datetime

from django.utils.timezone import now
from django.db import IntegrityError
from django.utils import timezone
from django.db.models import Q
from django.core import serializers
# from inwardservice.service.escalationsubtypeservice import EscalationSubTypeService
# from inwardservice.service.escalationtypeservice import EscalationTypeService
# from inwardservice.service.inwardproductcatservice import Productcategoryservice
# from inwardservice.service.inwardproductsubcategoryservice import ProductsubcategoryService
from inwardservice.data.response.commentdocresponse import CommentDocResponse
from inwardservice.data.response.inwardauditresponse import InwardAuditResponse
from inwardservice.data.response.inwarddetailsresponse import DetailsResponse
from inwardservice.data.response.inwardfileresponse import InwardFileResponse
from inwardservice.data.response.inwardheaderresponse import InwardHeaderResponse
from inwardservice.data.response.inwardresponse import InwardResponse
from inwardservice.data.response.inwardtranresponse import InwardTranResponse
from inwardservice.models import InwardHeader, InwardDetails, InwardFiles, Courier_Branch, InwardQueue, CommentDoc
from inwardservice.util.inwardutil import InwardRefType, ModifyStatus, RequestStatusUtil, get_inward_status, \
    inward_docaction, inward_status, inward_action, inward_doc_status, RefType, Inward_Status
from inwardservice.service.inwardauditservice import InwardAuditService
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.inward_api_service import ApiService
from utilityservice.service.threadlocal import NWisefinThread


class InwardService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.INWARD_SERVICE)

    def create_inward(self, request, inward_req, user_id):
        api_serv = ApiService(self._scope())
        branchs = api_serv.fetch_employeedata(request, user_id)
        branchdata = branchs['employee_branch_id']
        emp_code = branchs['code']
        if not inward_req.get_id() is None:
            if (inward_req.get_awbno() == '') & (inward_req.get_courier() == ''):
                courier = 0
                awbno = inward_req.get_awbno()
            else:
                courier = inward_req.get_courier()
                awbno = inward_req.get_awbno()
            logger.info("schema" + str(self._current_app_schema()))
            inward_objj = InwardHeader.objects.using(self._current_app_schema()).filter(id=inward_req.get_id()).update(
                date=inward_req.get_date(),
                channel_id=inward_req.get_channel(),
                courier_id=courier,
                branch_id=branchdata,
                awbno=awbno,
                inwardfrom=inward_req.get_inwardfrom(),
                updated_by=user_id,
                updated_date=now())
            inward_obj = InwardHeader.objects.using(self._current_app_schema()).get(id=inward_req.get_id())
            req_status = RequestStatusUtil.ONBORD
            self.inward_audit(inward_obj, inward_obj.id, user_id, req_status, inward_obj.id,
                              ModifyStatus.UPDATE, InwardRefType.INWARD_HEADRER)
        else:
            # try:
            if (inward_req.get_awbno() == '') & (inward_req.get_courier() == ''):
                courier = 0
                awbno = inward_req.get_awbno()
            else:
                courier = inward_req.get_courier()
                awbno = inward_req.get_awbno()
            logger.info("schema" + str(self._current_app_schema()))
            inward_obj = InwardHeader.objects.using(self._current_app_schema()).create(
                # no=inward_req.get_no(),
                date=inward_req.get_date(),
                channel_id=inward_req.get_channel(),
                courier_id=courier,
                awbno=awbno,
                branch_id=branchdata,
                inwardstatus=Inward_Status.NEW,
                noofpockets=inward_req.get_noofpockets(),
                inwardfrom=inward_req.get_inwardfrom(),
                created_by=user_id)
            from datetime import datetime
            no = "INW" + str(datetime.now().strftime("%y%m%d")) + str(inward_obj.id).zfill(3)
            inward_obj.no = no
            inward_obj.save()
            detail_arr = []
            for i in range(int(inward_req.get_noofpockets())):
                inward_details = InwardDetails(inwardheader_id=inward_obj.id,
                                               packetno=i + 1,
                                               doccount=1,
                                               docstatus=inward_status.OPEN,
                                               created_by=user_id,
                                              )
                detail_arr.append(inward_details)
                inward_dtl = InwardDetails.objects.using(self._current_app_schema()).filter(
                                            inwardheader_id=inward_obj.id, status=1)
                for d in inward_dtl:
                    InwardQueue.objects.using(self._current_app_schema()).create(ref_id=d.id,
                                                                        ref_type=RefType.INWARDDETAIL,
                                                                        from_user_id=user_id,
                                                                        to_user_id=user_id,
                                                                        created_date=now(),
                                                                        comments='input from user' + str(emp_code),
                                                                        is_sys=True)
            InwardDetails.objects.using(self._current_app_schema()).bulk_create(detail_arr)

            inwddtl_array = serializers.serialize("json", InwardDetails.objects.using(self._current_app_schema()).filter(inwardheader_id=inward_obj.id))
            req_status = RequestStatusUtil.ONBORD
            self.inward_audit(inward_obj.__dict__, inward_obj.id, user_id, req_status, inward_obj.id,
                              ModifyStatus.CREATE, InwardRefType.INWARD_HEADRER)
            self.inward_audit(json.loads(inwddtl_array), inward_obj.id, user_id, req_status, inward_obj.id,
                              ModifyStatus.CREATE, InwardRefType.INWARD_DETAIL)

        header_data = InwardResponse()
        header_data.set_id(inward_obj.id)
        header_data.set_no(inward_obj.no)
        header_data.set_date(inward_obj.date)
        header_data.set_channel(inward_obj.channel_id)
        header_data.set_branch(inward_obj.branch_id)
        header_data.set_courier(inward_obj.courier_id)
        header_data.set_awbno(inward_obj.awbno)
        header_data.set_noofpockets(inward_obj.noofpockets)
        header_data.set_inwardfrom(inward_obj.inwardfrom)
        return header_data

    def fetch_inward(self, request, header_id):
        try:
            inwardheader = InwardHeader.objects.using(self._current_app_schema()).get(id=header_id)
            apicall = ApiService(self._scope())
            cha_data = apicall.fetch_channeldata(request, inwardheader.channel_id)
            # cou_data = apicall.fetch_courierdata(request, inwardheader.courier_id)
            createby_data = apicall.fetch_employeedata(request, inwardheader.created_by)
            employee_branch_code = createby_data["employee_branch_code"]
            employee_branch_name = createby_data["employee_branch_name"]
            # employeebranch_name = employee_branch_code + ' -- ' + employee_branch_name
            employeebranch_name = '(' + employee_branch_code + ') ' + employee_branch_name

            header_data = InwardHeaderResponse()
            header_data.set_id(inwardheader.id)
            header_data.set_no(inwardheader.no)
            header_data.set_date(inwardheader.date)
            header_data.set_channel(cha_data)
            if inwardheader.courier_id == 0 or inwardheader.courier_id == -1 or inwardheader.courier_id is None:
                header_data.courier = None
            else:
                cou_data = apicall.fetch_courierdata(request, inwardheader.courier_id)
                header_data.set_courier(cou_data)
            header_data.set_awbno(inwardheader.awbno)
            header_data.set_noofpockets(inwardheader.noofpockets)
            header_data.set_status(get_inward_status(inwardheader.inwardstatus))
            header_data.employeebranch_name = employeebranch_name
            return header_data
        except InwardHeader.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_INWARDHEADER_ID)
            error_obj.set_description(ErrorDescription.INVALID_INWARDHEADER_ID)
            return error_obj

    def delete_inward(self, id, user_id):
        inwardheader = InwardHeader.objects.using(self._current_app_schema()).filter(id=id).delete()
        self.inward_audit(inwardheader, id, user_id, RequestStatusUtil.ONBORD, id, ModifyStatus.DELETE, InwardRefType.INWARD_HEADRER)
        if inwardheader[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_INWARDHEADER_ID)
            error_obj.set_description(ErrorDescription.INVALID_INWARDHEADER_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def fetch_inward_list(self, vys_page, request):
        condition = Q(status=1)
        inward_header = InwardHeader.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(inward_header)
        inwd_list_data = NWisefinList()
        cou_arr = []
        cha_arr = []
        # c_by_arr = []
        # emp_br_arr = []
        if list_length > 0:
            for i in inward_header:
                cou_arr.append(i.courier_id)
                cha_arr.append(i.channel_id)
                # c_by_arr.append(i.created_by)
        apicall = ApiService(self._scope())
        cou_data = apicall.get_courier(request, cou_arr)
        cha_data = apicall.get_channel(request, cha_arr)
        # c_by_data = apicall.get_employee(request, c_by_arr)
        if list_length > 0:
            for inwdheader in inward_header:
                header_data = InwardHeaderResponse()
                header_data.set_id(inwdheader.id)
                header_data.set_no(inwdheader.no)
                header_data.set_date(inwdheader.date)
                header_data.set_channel_id(inwdheader.channel_id, cha_data['data'])
                if inwdheader.courier_id == -1 or inwdheader.courier_id == 0 or inwdheader.courier_id is None:
                    header_data.courier_id = '-'
                else:
                    header_data.set_courier_id(inwdheader.courier_id, cou_data['data'])
                header_data.set_awbno(inwdheader.awbno)
                header_data.set_noofpockets(inwdheader.noofpockets)
                # header_data.set_created_by(inwdheader.created_by, c_by_data['data'])
                header_data.set_status(inwdheader.status)
                inwd_list_data.append(header_data)
            vpage = NWisefinPaginator(inward_header, vys_page.get_index(), 10)
            inwd_list_data.set_pagination(vpage)
        return inwd_list_data

    def delete_inwdfile(self, files, user_id):
        inwd_file = InwardFiles.objects.using(self._current_app_schema()).get(files=files)
        inwardheader = InwardFiles.objects.using(self._current_app_schema()).filter(files=files).delete()
        self.inward_audit(inwardheader, inwd_file.id, user_id, RequestStatusUtil.ONBORD, inwd_file.id, ModifyStatus.DELETE, InwardRefType.INWARD_FILE)
        if inwardheader[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_INWARDHEADER_ID)
            error_obj.set_description(ErrorDescription.INVALID_INWARDHEADER_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

# inward detail list
    def fetch_inwarddetails_list(self, request, inward_id, vys_page):
        inward_details = InwardDetails.objects.using(self._current_app_schema()).filter(inwardheader_id=inward_id).order_by(
            'created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(inward_details)
        doc_arr = []
        if list_length > 0:
            for i in inward_details:
                doc_arr.append(i.doctype_id)
        apicall = ApiService(self._scope())
        doc_data = apicall.get_doctype(request, doc_arr)
        inwd_list_data = NWisefinList()
        if list_length > 0:
            for inwarddetails in inward_details:
                details_data = DetailsResponse()
                # escalsubtypeserv = EscalationSubTypeService()
                # escaltypeserv = EscalationTypeService()
                # productcat_sev = Productcategoryservice()
                # productsubcat_sev = ProductsubcategoryService()

                details_data.set_id(inwarddetails.id)
                details_data.set_packetno(inwarddetails.packetno)
                if inwarddetails.doctype_id != 0:
                    details_data.set_doctype_id(inwarddetails.doctype_id, doc_data['data'])

                else:
                    details_data.doctype_id = None
                details_data.set_inwardheader(self.fetch_inward(request, inwarddetails.inwardheader_id))
                # if inwarddetails.escalationsubtype_id != None:
                #     details_data.set_escalationsubtype(
                #         escalsubtypeserv.fetch_escalationsub(inwarddetails.escalationsubtype_id))
                # else:
                #     details_data.escalationsubtype = None
                # if inwarddetails.escalationtype_id != None:
                #     details_data.set_escalationtype(escaltypeserv.fetch_escalation(inwarddetails.escalationtype_id))
                # else:
                #     details_data.set_escalationtype(None)
                # if inwarddetails.productcategory_id != None:
                #     details_data.set_product_category(productcat_sev.fetch_productcat(inwarddetails.productcategory_id))
                # else:
                #     details_data.product_category = None
                # if inwarddetails.productsubcategory_id != None:
                #     details_data.set_product_subcategory(
                #         productsubcat_sev.fetch_prosubcat(inwarddetails.productsubcategory_id))
                # else:
                #     details_data.set_product_subcategory(None)
                details_data.set_doccount(inwarddetails.doccount)
                inwfile = InwardFiles.objects.using(self._current_app_schema()).filter(inwarddetails_id=inwarddetails.id)
                date_lenth = len(inwfile)
                file_list = list()
                if date_lenth > 0:
                    for doc in inwfile:
                        file_data = InwardFileResponse()
                        file_data.set_id(doc.id)
                        file_data.set_file_id(doc.file_id)
                        file_data.set_inwarddetails(doc.inwarddetails_id)
                        file_data.set_commentdoc(doc.commentdoc_id)
                        file_list.append(file_data)
                doc_data.set_file_data(file_list)
                # frontend purpose
                details_data.countkey = False
                details_data.doctypekey = False
                details_data.esckey = False
                details_data.escsubtypekey = False
                details_data.productcatkey = False
                details_data.productsubcatkey = False
                details_data.remarkkey = False
                details_data.set_remarks(inwarddetails.remarks)
                inwd_list_data.append(details_data)
            vpage = NWisefinPaginator(inward_details, vys_page.get_index(), 10)
            inwd_list_data.set_pagination(vpage)
        return inwd_list_data

# inward detail get
#InwardFiles
    def fetch_inwddetails(self, request, inward_id, detail_id):
        try:
            inwarddetails = InwardDetails.objects.using(self._current_app_schema()).get(id=detail_id, inwardheader_id=inward_id)
            details_data = DetailsResponse()
            apicall = ApiService(self._scope())
            details_data.set_id(inwarddetails.id)
            details_data.set_packetno(inwarddetails.packetno)
            if inwarddetails.doctype_id != 0:
                doc_data = apicall.fetch_doctypedata(request, inwarddetails.doctype_id)
                details_data.set_doctype(doc_data)
            else:
                details_data.set_doctype(None)
            details_data.set_doccount(inwarddetails.doccount)
            details_data.set_remarks(inwarddetails.remarks)
            details_data.set_inwardheader(self.fetch_inward(request, inwarddetails.inwardheader_id))
            inwfile = InwardFiles.objects.using(self._current_app_schema()).filter(inwarddetails_id=inwarddetails.id)
            date_lenth = len(inwfile)
            file_list = list()
            if date_lenth > 0:
                for doc in inwfile:
                    file_data = InwardFileResponse()
                    file_data.set_id(doc.id)
                    file_data.set_file_id(doc.file_id)
                    file_data.set_inwarddetails(doc.inwarddetails_id)
                    file_data.set_commentdoc(doc.commentdoc_id)
                    file_list.append(file_data)
            details_data.set_file_data(file_list)
            return details_data
        except InwardDetails.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_INWARDHEADER_ID)
            error_obj.set_description(ErrorDescription.INVALID_INWARDHEADER_ID)
            return error_obj

# inward detail update
    def update_inwarddetails(self, inwarddtl_data, detail_id, user_id, request):
        # try:
        api_serv = ApiService(self._scope())
        branchs = api_serv.fetch_employeedata(request, user_id)
        emp_code = branchs['code']
        InwardDetails.objects.using(self._current_app_schema()).filter(id=detail_id).update(
                                                            # packetno=inwarddtl_data.packetno,
                                                            doctype_id=inwarddtl_data['doctype_id'],
                                                            doccount=inwarddtl_data['doccount'],
                                                            # escalationtype_id=inwarddtl_data['escalationtype'],
                                                            # escalationsubtype_id=inwarddtl_data['escalationsubtype'],
                                                            # productcategory=inwarddtl_data['product_category'],
                                                            # productsubcategory=inwarddtl_data['product_subcategory'],
                                                            remarks=inwarddtl_data['remarks'],
                                                            updated_by=user_id, updated_date=timezone.now())

        inwarddetails = InwardDetails.objects.using(self._current_app_schema()).get(id=detail_id)
        self.inward_audit(inwarddetails.__dict__, inwarddetails.id, user_id, RequestStatusUtil.ONBORD, inwarddetails.id,
                          ModifyStatus.UPDATE, InwardRefType.INWARD_DETAIL)
        InwardQueue.objects.using(self._current_app_schema()).create(ref_id=inwarddetails.id,
                                                             ref_type=RefType.INWARDDETAIL,
                                                             from_user_id=user_id,
                                                             to_user_id=user_id,
                                                             created_date=now(),
                                                             comments='updated by ' + str(emp_code),
                                                             remarks=inwarddtl_data['remarks'],
                                                             is_sys=True)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        return success_obj
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

# inward detail delete
    def delete_inwarddetail(self, inwarddtl_id, user_id):
        inwarddtls = InwardDetails.objects.using(self._current_app_schema()).filter(id=inwarddtl_id).delete()
        self.inward_audit(inwarddtls, inwarddtl_id, user_id, RequestStatusUtil.ONBORD, inwarddtl_id,
                          ModifyStatus.DELETE, InwardRefType.INWARD_DETAIL)
        if inwarddtls[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_INWARDHEADER_ID)
            error_obj.set_description(ErrorDescription.INVALID_INWARDHEADER_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

# inward detail clone
    def inwarddetail_clone(self, request, inward_id, inwarddtl_id, user_id):
        try:
            inwarddtl_data = InwardDetails.objects.using(self._current_app_schema()).get(id=inwarddtl_id)
            packetno = inwarddtl_data.packetno
            inwarddetails = InwardDetails.objects.using(self._current_app_schema()).create(inwardheader_id=inwarddtl_data.inwardheader_id,
                                                                            packetno=inwarddtl_data.packetno,
                                                                            doctype_id=inwarddtl_data.doctype_id,
                                                                            doccount=inwarddtl_data.doccount,
                                                                            actiontype=inwarddtl_data.actiontype,
                                                                            pagecount=inwarddtl_data.pagecount,
                                                                            receivedfrom=inwarddtl_data.receivedfrom,
                                                                            docsubject=inwarddtl_data.docsubject,
                                                                            docstatus=inward_status.OPEN,
                                                                            # escalationtype_id=inwarddtl_data.escalationtype_id,
                                                                            # escalationsubtype_id=inwarddtl_data.escalationsubtype_id,
                                                                            # productcategory_id=inwarddtl_data.productcategory_id,
                                                                            # productsubcategory_id=inwarddtl_data.productsubcategory_id,
                                                                            remarks=inwarddtl_data.remarks,
                                                                            created_by=user_id,
                                                                            created_date=now())

            inwarddtl = InwardDetails.objects.using(self._current_app_schema()).filter(inwardheader_id=inward_id,
                                                                               packetno=packetno, status=1)

            doccount = 0
            for d in inwarddtl:
                count = d.doccount + 1
                doccount = count
                inwarddtl = InwardDetails.objects.using(self._current_app_schema()).filter(inwardheader_id=inward_id,
                                                                            packetno=packetno,
                                                                            status=1
                                                                            ).update(doccount=doccount)

            self.inward_audit(inwarddetails.__dict__, inwarddetails.id, user_id, RequestStatusUtil.ONBORD, inwarddetails.id,
                              ModifyStatus.CREATE, InwardRefType.INWARD_DETAIL)

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
        inwdheader = InwardHeader.objects.using(self._current_app_schema()).get(id=inwarddetails.inwardheader_id)
        header_data = InwardHeaderResponse()
        apicall = ApiService(self._scope())
        header_data.set_id(inwdheader.id)
        header_data.set_no(inwdheader.no)
        header_data.set_date(inwdheader.date)
        cha_data = apicall.fetch_channeldata(request, inwdheader.channel_id)
        header_data.set_channel(cha_data)
        cou_data = apicall.fetch_courierdata(request, inwdheader.courier_id)
        header_data.set_courier(cou_data)
        header_data.set_awbno(inwdheader.awbno)
        header_data.set_noofpockets(inwdheader.noofpockets)
        header_data.set_status(get_inward_status(inwdheader.status))
        header_data.doccount = doccount
        createby_data = apicall.fetch_employeedata(request, inwdheader.created_by)
        employee_branch_code = createby_data["employee_branch_code"]
        employee_branch_name = createby_data["employee_branch_name"]
        # header_data.employeebranch_name = employee_branch_code + ' -- ' + employee_branch_name
        employeebranch_name = '(' + employee_branch_code + ') ' + employee_branch_name
        header_data.set_awbno(inwdheader.awbno)
        header_data.set_noofpockets(inwdheader.noofpockets)
        inwarddetail_arr = []
        inward_details = InwardDetails.objects.using(self._current_app_schema()).filter(id=inwarddetails.id)
        doc_arr = []
        for i in inward_details:
            doc_arr.append(i.doctype_id)
        apicall = ApiService(self._scope())
        doc_data = apicall.get_doctype(request, doc_arr)
        for inwarddetails in inward_details:
            detail_data = DetailsResponse()
            detail_data.set_id(inwarddetails.id)
            detail_data.set_doccount(inwarddetails.doccount)
            detail_data.set_packetno(inwarddetails.packetno)
            detail_data.set_docstatus(inwarddetails.docstatus)
            detail_data.set_docnumber(inwarddetails.docnumber)
            detail_data.set_receivedfrom(inwarddetails.receivedfrom)
            detail_data.set_pagecount(inwarddetails.pagecount)
            detail_data.set_docsubject(inwarddetails.docsubject)
            if inwarddetails.doctype_id != 0:
                detail_data.set_doctype_id(inwarddetails.doctype_id, doc_data['data'])
            else:
                detail_data.doctype_id = None
            # detail_data.doctype_id = inwarddetails.doctype_id
            detail_data.set_packetno(inwarddetails.packetno)
            detail_data.set_remarks(inwarddetails.remarks)
            # frontend purpose
            detail_data.doctypekey = False
            detail_data.docsubkey = False
            detail_data.pagecountkey = False
            detail_data.receivedfromkey = False
            detail_data.statuskey = False
            detail_data.documentnokey = False
            file_name = "file" + str(inwarddetails.id)
            detail_data.file_key = [file_name]
            detail_data.file_name = file_name
            detail_data.filearray = []
            detail_data.remarkkey = False
            detail_data.set_inwardheader(self.fetch_inward(request, inwarddetails.inwardheader_id))
            detail_data.inwardheader_id = inwarddetails.inwardheader_id
            detail_data.set_assignemployee(inwarddetails.assignemployee_id)
            inwarddetail_arr.append(json.loads(detail_data.get()))
        header_data.inwarddetails_detail = inwarddetail_arr
        return header_data

    def search_inward(self, request, search_obj, vys_page):
        scond = None
        if 'courier_id' in search_obj:
            if scond is None:
                scond = Q(courier_id__exact=search_obj['courier_id'])
            else:
                scond |= Q(courier_id__exact=search_obj['courier_id'])
        if 'channel_id' in search_obj:
            if scond is None:
               scond = Q(channel_id__exact=search_obj['channel_id'])
            else:
                scond &= Q(channel_id__exact=search_obj['channel_id'])
        # print(scond)
        if scond is not None:
            inward_list = InwardHeader.objects.using(self._current_app_schema()).filter(scond)
        else:
            inward_list = []
        list_length = len(inward_list)
        if list_length <= 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
            return error_obj
        else:
            cou_arr = []
            cha_arr = []
            apicall = ApiService(self._scope())
            for i in inward_list:
                cou_arr.append(i.courier_id)
                cha_arr.append(i.channel_id)
            cou_data = apicall.get_courier(request, cou_arr)
            cha_data = apicall.get_channel(request, cha_arr)
            inwd_list_data = NWisefinList()
            for inwdheader in inward_list:
                header_data = InwardHeaderResponse()
                header_data.set_id(inwdheader.id)
                header_data.set_no(inwdheader.no)
                header_data.set_date(inwdheader.date)
                header_data.set_channel_id(inwdheader.channel_id, cha_data['data'])
                header_data.set_courier_id(inwdheader.courier_id, cou_data['data'])
                header_data.set_awbno(inwdheader.awbno)
                header_data.set_noofpockets(inwdheader.noofpockets)
                inwd_list_data.append(header_data)
            vpage = NWisefinPaginator(inward_list, vys_page.get_index(), 10)
            inwd_list_data.set_pagination(vpage)
            return inwd_list_data

    def update_inwarddtlscount(self, inwarddtl_data, detail_id, user_id):
        try:
            InwardDetails.objects.using(self._current_app_schema()).filter(id=detail_id).update(
                                                              doccount=inwarddtl_data['doccount'],
                                                              updated_by=user_id, updated_date=timezone.now())

            inwarddetails = InwardDetails.objects.using(self._current_app_schema()).get(id=detail_id)
            self.inward_audit(inwarddetails.__dict__, inwarddetails.id, user_id, RequestStatusUtil.ONBORD, inwarddetails.id,
                              ModifyStatus.UPDATE, InwardRefType.INWARD_DETAIL)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            return success_obj
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

    #no use
    # def fetch_inwdminidetails(self, detail_id):
    #     inwd_list_data = list()
    #     try:
    #         inwarddetails = InwardDetails.objects.using(self._current_app_schema()).get(id=detail_id)
    #         inward_file = InwardDocuments.objects.using(self._current_app_schema()).filter(rel_id=detail_id)
    #         details_data = DetailsResponse()
    #         doctype_serv = DocumenttypeService()
    #
    #         details_data.set_id(inwarddetails.id)
    #         details_data.set_doccount(inwarddetails.doccount)
    #         if inwarddetails.doctype != 0:
    #             details_data.set_doctype(doctype_serv.fetchdoctype(inwarddetails.doctype))
    #         else:
    #             details_data.set_doctype(None)
    #         for files in inward_file:
    #             doc_resp = InwardDocumentResponse()
    #             doc_resp.set_file_id('Inwd_'+str(files.id))
    #             doc_resp.set_file_name(files.file_name)
    #             doc_resp.set_inwarddetails_id(files.rel_id)
    #             inwd_list_data.append(doc_resp)
    #             details_data.set_attachment(inwd_list_data)
    #         return details_data
    #
    #     except InwardDetails.DoesNotExist:
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.INVALID_INWARDHEADER_ID)
    #         error_obj.set_description(ErrorDescription.INVALID_INWARDHEADER_ID)
    #         return error_obj

#no use
    # def fetch_inwardminidetails_list(self, inward_id, vys_page):
    #     inward_details = InwardDetails.objects.using(self._current_app_schema()).filter(inwardheader_id=inward_id)[vys_page.get_offset():vys_page.get_query_limit()]
    #     list_length = len(inward_details)
    #     inwd_list_data = NWisefinList()
    #     doc_arr = []
    #     if list_length > 0:
    #         for i in inward_details:
    #             doc_arr.append(i.doctype_id)
    #     apicall = ApiService(self._scope())
    #     doc_data = apicall.get_doctype(request, doc_arr)
    #     if list_length > 0:
    #         for inwarddetails in inward_details:
    #             inward_file = InwardDocuments.objects.using(self._current_app_schema()).filter(rel_id=inwarddetails.id)
    #             details_data = DetailsResponse()
    #             # doctype_serv = DocumenttypeService()
    #             # escalsubtypeserv = EscalationSubTypeService()
    #             # escaltypeserv = EscalationTypeService()
    #             inwd_filelen = len(inward_file)
    #             inwddtl_list = list()
    #             if inwd_filelen > 0:
    #                 for files in inward_file:
    #                     doc_resp = InwardDocumentResponse()
    #                     doc_resp.set_file_id('Inwd_' + str(files.id))
    #                     doc_resp.set_file_name(files.file_name)
    #                     doc_resp.set_inwarddetails_id(files.rel_id)
    #                     inwddtl_list.append(doc_resp)
    #             details_data.set_attachment(inwddtl_list)
    #             details_data.set_id(inwarddetails.id)
    #             details_data.set_doccount(inwarddetails.doccount)
    #             if inwarddetails.doctype != 0:
    #                 details_data.set_doctype_id(inwarddetails.doctype_id, doc_data['data'])
    #             else:
    #                 details_data.set_doctype(None)
    #             inwd_list_data.append(details_data)
    #         vpage = NWisefinPaginator(inward_details, vys_page.get_index(), 10)
    #         inwd_list_data.set_pagination(vpage)
    #     return inwd_list_data

    def courier_branch(self, branch_id, courier_id):
        try:
            courier_branch = Courier_Branch.objects.using(self._current_app_schema()).create(
                                                                                branch_id=branch_id,
                                                                                courier_id=courier_id)

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            return success_obj
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj

    # used in masterservice courier create api [jp done]
    # def get_emp_branch(self, user_id):
    #     employee = Employee.objects.using(self._current_app_schema()).get(id=user_id)
    #     branch_id = employee.employee_branch_id
    #     return branch_id

    # used in inwd fe jp done in userservice empbranch [jp done]
    # def fetchemployee_branch(self, emp_id):
    #     try:
    #         employee = Employee.objects.using(self._current_app_schema()).get(id=emp_id)
    #         branch_id = employee.employee_branch_id
    #         branch = EmployeeBranch.objects.using(self._current_app_schema()).get(id=branch_id)
    #         data_obj = EmployeeBranchResponse()
    #         data_obj.set_id(branch.id)
    #         data_obj.set_code(branch.code)
    #         data_obj.set_name(branch.name)
    #         return data_obj
    #     except EmployeeBranch.DoesNotExist:
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.INVALID_branch_ID)
    #         error_obj.set_description(ErrorDescription.INVALID_branch_ID)
    #         return error_obj

    # def fetch_branchcourier(self, vys_page, emp_id):
    #     employee = Employee.using(DataBase.INWARD_DB).get(id=emp_id)
    #     branch_id = employee.employee_branch_id
    #     # branch = EmployeeBranch.objects.using(self._current_app_schema()).get(id=branch_id)
    #     conditions=Q(branch_id=None)  | Q(branch_id=branch_id)
    #     branch_courier = Courier_Branch.objects.using(self._current_app_schema()).filter(conditions)
    #     # print(len(branch_courier),'branch_courierlen')
    #     br_courier_lis = list()
    #     for br_courier in branch_courier:
    #         br_courier_lis.append(br_courier.courier_id)
    #
    #     # if query is None:
    #     courierlist = Courier.objects.using(self._current_app_schema()).filter(id__in=br_courier_lis,status=1)[vys_page.get_offset():vys_page.get_query_limit()]
    #     list_length = len(courierlist)
    #     courier_list_data = NWisefinList()
    #     if list_length <= 0:
    #         pass
    #     else:
    #         for courierobj in courierlist:
    #             address_service = AddressService()
    #             contact_service = ContactService()
    #             courier_data = CourierResponse()
    #             courier_data.set_id(courierobj.id)
    #             courier_data.set_code(courierobj.code)
    #             courier_data.set_name(courierobj.name)
    #             courier_data.set_type(courierobj.type)
    #             courier_data.set_contactperson(courierobj.contactperson)
    #             # print(courierobj.contact_id,'courierobj.contact_id')
    #             if courierobj.contact_id == None:
    #                 courier_data.set_contact_id(None)
    #             elif courierobj.contact_id != None:
    #                 courier_data.set_contact_id(contact_service.fetchcontact(courierobj.contact_id))
    #             if courierobj.address_id == None:
    #                 courier_data.set_address_id(None)
    #             elif courierobj.address_id != None:
    #                 courier_data.set_address_id(address_service.fetch_address(courierobj.address_id, emp_id))
    #             courier_list_data.append(courier_data)
    #         vpage = NWisefinPaginator(courierlist, vys_page.get_index(), 10)
    #         courier_list_data.set_pagination(vpage)
    #     return courier_list_data

    # def inward_details_assign_validation(self, details_obj, detail_id):
    #     details = InwardDetails.objects.using(self._current_app_schema()).get(id=detail_id)
    #     docnumber = "DOC" + str(datetime.now().strftime("%y%m%d")) + str(details.id).zfill(4)
    #     details.docnumber = docnumber
    #     details.save()
    #     escalationtype_id = details.escalationtype_id
    #     escalationsubtype_id = details.escalationsubtype_id
    #     productcategory_id = details.productcategory_id
    #     productsubcategory_id = details.productsubcategory_id
    #     doccount = details.doccount
    #     doctype_id = details.doctype_id
    #     remarks = details.remarks
    #     pagecount = details.remarks
    #     details_obj['docstatus'] = inward_status.OPEN
    #     print(details_obj)
    #     if 'pagecount' not in details_obj or details_obj['pagecount'] is None:
    #         details_obj['pagecount'] = pagecount
    #     if 'doctype_id' not in details_obj or details_obj['doctype_id'] is None:
    #         details_obj['doctype_id'] = doctype_id
    #     if 'doccount' not in details_obj or details_obj['doccount'] is None:
    #         details_obj['doccount'] = doccount
    #     if 'remarks' not in details_obj or details_obj['remarks'] is None:
    #         details_obj['remarks'] = remarks
    #     if 'escalationtype_id' not in details_obj or details_obj['escalationtype_id'] is None:
    #         details_obj['escalationtype_id'] = escalationtype_id
    #     if 'escalationsubtype_id' not in details_obj or details_obj['escalationsubtype_id'] is None:
    #         details_obj['escalationsubtype_id'] = escalationsubtype_id
    #     if 'product_category' not in details_obj or details_obj['product_category'] is None:
    #         details_obj['product_category'] = productcategory_id
    #     if 'product_subcategory' not in details_obj or details_obj['product_subcategory'] is None:
    #         details_obj['product_subcategory'] = productsubcategory_id
    #     return details_obj

    def inward_details_assign_validation(self, details_obj, detail_id):
        details = InwardDetails.objects.using(self._current_app_schema()).get(id=detail_id)

        docnumber = "DOC" + str(datetime.now().strftime("%y%m%d")) + str(details.id).zfill(4)
        details.docnumber = docnumber
        details.save()
        escalationtype_id = details.escalationtype_id
        escalationsubtype_id = details.escalationsubtype_id
        productcategory_id = details.productcategory_id
        productsubcategory_id = details.productsubcategory_id
        doccount = details.doccount
        doctype_id = details.doctype_id
        remarks = details.remarks
        pagecount = details.remarks
        details_obj['docstatus'] = inward_status.OPEN
        print(details_obj)
        if 'pagecount' not in details_obj or details_obj['pagecount'] is None:
            details_obj['pagecount'] = pagecount
        if 'doctype_id' not in details_obj or details_obj['doctype_id'] is None:
            details_obj['doctype_id'] = doctype_id
        if 'doccount' not in details_obj or details_obj['doccount'] is None:
            details_obj['doccount'] = doccount
        if 'remarks' not in details_obj or details_obj['remarks'] is None:
            details_obj['remarks'] = remarks
        if 'escalationtype_id' not in details_obj or details_obj['escalationtype_id'] is None:
            details_obj['escalationtype_id'] = escalationtype_id
        if 'escalationsubtype_id' not in details_obj or details_obj['escalationsubtype_id'] is None:
            details_obj['escalationsubtype_id'] = escalationsubtype_id
        if 'product_category' not in details_obj or details_obj['product_category'] is None:
            details_obj['product_category'] = productcategory_id
        if 'product_subcategory' not in details_obj or details_obj['product_subcategory'] is None:
            details_obj['product_subcategory'] = productsubcategory_id
        return details_obj

    def inward_audit(self, inward_data, inward_id, user_id, req_status, inwardrel_id, action, inwardrel_type):
        if action == ModifyStatus.DELETE:
            data = None
        else:
            data = inward_data

        audit_service = InwardAuditService(self._scope())
        audit_obj = InwardAuditResponse()
        audit_obj.set_refid(inward_id)
        audit_obj.set_reftype(InwardRefType.INWARD_HEADRER)
        audit_obj.set_userid(user_id)
        audit_obj.set_reqstatus(req_status)
        audit_obj.set_relrefid(inwardrel_id)
        audit_obj.set_relreftype(inwardrel_type)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return

    def fetch_ap_inward_list(self,request,search_json,  vys_page,emp_id):
        contions = Q(doctype_id=1)
        if 'inward_hdr_no' in search_json:
            contions &= Q(inwardheader__no__icontains=search_json['inward_hdr_no'])
        if 'airway_no' in search_json:
            contions &= Q(inwardheader__awbno__icontains=search_json['airway_no'])
        if 'inward_date' in search_json:
            contions &= Q(inwardheader__date=search_json['inward_date'])
        if 'inward_status' in search_json:
            contions &= Q(inwardheader__inwardstatus=search_json['inward_status'])
        print("schema", self._current_app_schema())
        logger.info("schema" + str(self._current_app_schema()))
        inward_details = InwardDetails.objects.using(self._current_app_schema()).filter(contions).order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(inward_details)
        inwd_list_data = NWisefinList()
        doc_arr = []
        if list_length > 0:
            for i in inward_details:
                doc_arr.append(i.doctype_id)
        apicall = ApiService(self._scope())
        doc_data = apicall.get_doctype(request, doc_arr)
        if list_length > 0:
            for inwarddetails in inward_details:
                details_data = DetailsResponse()
                details_data.set_id(inwarddetails.id)
                details_data.set_packetno("PACKET-"+str(inwarddetails.packetno))
                details_data.set_doccount(inwarddetails.doccount)
                details_data.set_remarks(inwarddetails.remarks)
                # details_data.doctype_id=inwarddetails.doctype_id
                if inwarddetails.doctype_id != 0:
                    details_data.set_doctype_id(inwarddetails.doctype_id, doc_data['data'])
                else:
                    details_data.doctype_id = None
                details_data.set_inwardheader(self.fetch_inward(request,inwarddetails.inwardheader_id))
                details_data.inwardheader_id = inwarddetails.inwardheader_id
                inwd_list_data.append(details_data)
            vpage = NWisefinPaginator(inward_details, vys_page.get_index(), 10)
            inwd_list_data.set_pagination(vpage)
        return inwd_list_data

    def inwardstatus_change(self, header_data, emp_id):
        try:
            inwarddtl = InwardDetails.objects.using(self._current_app_schema()).filter(id=header_data['inwarddetails_id'])[0]
            inwardheader = InwardHeader.objects.using(self._current_app_schema()).filter(id=inwarddtl.inwardheader_id).update(
                inwardstatus=header_data['status_id'],
                updated_date=now(),
                updated_by=emp_id)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj
        except Exception as excep:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

    def inward_summarysearch(self, vys_page, inward_obj, request):
        condition = Q(status=1)
        if 'awb_no' in inward_obj:
            condition &= Q(awbno__icontains=inward_obj['awb_no'])
        if 'fromdate' in inward_obj:
            condition &= Q(date__range=(inward_obj['fromdate'], inward_obj['todate']))
        if 'channel_id' in inward_obj:
            condition &= Q(channel_id=inward_obj['channel_id'])
        if 'courier_id' in inward_obj:
            condition &= Q(courier_id=inward_obj['courier_id'])
        inward_header = InwardHeader.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[
                    vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(inward_header)
        inwd_list_data = NWisefinList()
        cou_arr = []
        cha_arr = []
        if list_length > 0:
            for i in inward_header:
                cou_arr.append(i.courier_id)
                cha_arr.append(i.channel_id)
        apicall = ApiService(self._scope())
        cou_data = apicall.get_courier(request, cou_arr)
        cha_data = apicall.get_channel(request, cha_arr)
        if (len(inward_header) > 0):
            for inwdheader in inward_header:
                header_data = InwardHeaderResponse()
                header_data.set_id(inwdheader.id)
                header_data.set_no(inwdheader.no)
                header_data.set_date(inwdheader.date)
                header_data.set_channel_id(inwdheader.channel_id, cha_data['data'])
                if inwdheader.courier_id == 0 or inwdheader.courier_id == -1 or inwdheader.courier_id is None :
                    header_data.courier_id = '-'
                else:
                    header_data.set_courier_id(inwdheader.courier_id, cou_data['data'])
                header_data.set_awbno(inwdheader.awbno)
                header_data.set_status(inwdheader.status)
                header_data.set_noofpockets(inwdheader.noofpockets)
                header_data.set_inwardfrom(inwdheader.inwardfrom)
                header_data.set_inwardstatus(inwdheader.inwardstatus)
                # for can't edit once data completed
                condi1 = Q(inwardheader_id=inwdheader.id) & Q(status=1)
                inwarddtl1 = InwardDetails.objects.using(self._current_app_schema()).filter(condi1)
                len_all1 = len(inwarddtl1)

                condi2 = Q(inwardheader_id=inwdheader.id) & Q(docnumber__icontains="DOC") & Q(status=1)
                inwarddtl2 = InwardDetails.objects.using(self._current_app_schema()).filter(condi2)
                len_all2 = len(inwarddtl2)
                if len_all1 == len_all2:
                    header_data.detail_complete = True
                else:
                    header_data.detail_complete = False
                #
                inwd_list_data.append(header_data)
            vpage = NWisefinPaginator(inward_header, vys_page.get_index(), 10)
            inwd_list_data.set_pagination(vpage)
        return inwd_list_data

# inward detail clone
    def fetch_inward_headerdetails(self, request, inwardheader_id, inwarddetail_id, vys_page, tcount):
        try:
            condition = Q(inwardheader_id=inwardheader_id) & Q(id=inwarddetail_id) & Q(status=1)
            inward_details = InwardDetails.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[vys_page.get_offset():vys_page.get_query_limit()]
            inwd_dtls = InwardDetails.objects.using(self._current_app_schema()).get(id=inwarddetail_id, status=1)
            count = inwd_dtls.doccount
            acount = int(tcount)-count
            InwardDetails.objects.using(self._current_app_schema()).filter(id=inwarddetail_id, status=1).update(doccount=tcount)
            cnt = InwardDetails.objects.using(self._current_app_schema()).get(id=inwarddetail_id)
            print(cnt)
            n = int(acount)
            if(int(tcount) < count):
                print("Enter larger value")
            list_length = len(inward_details)
            # doctype_serv = DocumenttypeService()
            # escalsubtypeserv = EscalationSubTypeService()
            # escaltypeserv = EscalationTypeService()
            # productcat_sev = Productcategoryservice()
            # productsubcat_sev = ProductsubcategoryService()
            inwd_list_data = NWisefinList()
            doc_arr = []
            if list_length > 0:
                for i in inward_details:
                    doc_arr.append(i.doctype_id)
            apicall = ApiService(self._scope())
            doc_data = apicall.get_doctype(request, doc_arr)
            if list_length > 0:
                for i in range(n):
                    for inwarddetails in inward_details:
                        detail_data = DetailsResponse()
                        detail_data.set_id(inwarddetails.id)
                        detail_data.set_packetno(inwarddetails.packetno)
                        if inwarddetails.doctype_id != 0:
                            detail_data.set_doctype_id(inwarddetails.doctype_id, doc_data['data'])
                        else:
                            detail_data.doctype_id = None
                        # if inwarddetails.escalationsubtype_id != None:
                        #     detail_data.set_escalationsubtype(escalsubtypeserv.fetch_escalationsub(inwarddetails.escalationsubtype_id))
                        # else:
                        #     detail_data.set_escalationsubtype(None)
                        # if inwarddetails.escalationtype_id != None:
                        #     detail_data.set_escalationtype(escaltypeserv.fetch_escalation(inwarddetails.escalationtype_id))
                        # else:
                        #     detail_data.set_escalationtype(None)
                        # if inwarddetails.productcategory_id != None:
                        #     detail_data.set_product_category(productcat_sev.fetch_productcat(inwarddetails.productcategory_id))
                        # else:
                        #     detail_data.set_product_category(None)
                        # if inwarddetails.productsubcategory_id != None:
                        #     detail_data.set_product_subcategory(productsubcat_sev.fetch_prosubcat(inwarddetails.productsubcategory_id))
                        # else:
                        #     detail_data.set_product_subcategory(None)
                        detail_data.set_doccount(inwarddetails.doccount)
                        detail_data.set_remarks(inwarddetails.remarks)
                        # frontend purpose
                        detail_data.countkey = False
                        detail_data.doctypekey = False
                        detail_data.esckey = False
                        detail_data.escsubtypekey = False
                        detail_data.productcatkey = False
                        detail_data.productsubcatkey = False
                        detail_data.remarkkey = False
                        detail_data.set_inwardheader(self.fetch_inward(request,inwarddetails.inwardheader_id))
                        inwd_list_data.append(detail_data)
                vpage = NWisefinPaginator(inward_details, vys_page.get_index(), 10)
                inwd_list_data.set_pagination(vpage)
            return inwd_list_data
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj

    def inward_details_summarysearch(self, vys_page, inward_obj, request):
        condition = Q(status=1)
        if 'fromdate' in inward_obj:
            condition &= Q(date__range=(inward_obj['fromdate'], inward_obj['todate']))
        if 'channel_id' in inward_obj:
            condition &= Q(channel_id=inward_obj['channel_id'])
        if 'branch_id' in inward_obj:
            condition &= Q(branch_id=inward_obj['branch_id'])
        inward_header = InwardHeader.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[
                        vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(inward_header)
        inwd_list_data = NWisefinList()
        cou_arr = []
        c_by_arr = []
        cha_arr = []
        emp_br_arr = []
        if list_length > 0:
            for i in inward_header:
                cou_arr.append(i.courier_id)
                c_by_arr.append(i.created_by)
                cha_arr.append(i.channel_id)
                emp_br_arr.append(i.branch_id)
            apicall = ApiService(self._scope())
            cou_data = apicall.get_courier(request, cou_arr)
            c_by_data = apicall.get_employee(request, c_by_arr)
            emp_br_data = apicall.get_employeebranch(request, emp_br_arr)
            cha_data = apicall.get_channel(request, cha_arr)
            for inwdheader in inward_header:
                header_data = InwardHeaderResponse()
                header_data.set_id(inwdheader.id)
                header_data.set_no(inwdheader.no)
                header_data.set_date(inwdheader.date)
                header_data.set_channel_id(inwdheader.channel_id, cha_data['data'])
                header_data.set_branch_id(inwdheader.branch_id, emp_br_data['data'])
                if inwdheader.courier_id == -1 or inwdheader.courier_id is None:
                    header_data.courier_id = '-'
                else:
                    header_data.set_courier_id(inwdheader.courier_id, cou_data['data'])
                header_data.set_awbno(inwdheader.awbno)
                header_data.set_noofpockets(inwdheader.noofpockets)
                header_data.set_created_by(inwdheader.created_by, c_by_data['data'])
                header_data.set_status(inwdheader.status)
                header_data.set_inwardstatus(inwdheader.inwardstatus)
                # for can't edit once data completed
                condi1 = Q(inwardheader_id=inwdheader.id) & Q(status=1)
                inwarddtl1 = InwardDetails.objects.using(self._current_app_schema()).filter(condi1)
                len_all1 = len(inwarddtl1)

                condi2 = Q(inwardheader_id=inwdheader.id) & Q(docnumber__icontains="DOC") & Q(status=1)
                inwarddtl2 = InwardDetails.objects.using(self._current_app_schema()).filter(condi2)
                len_all2 = len(inwarddtl2)
                if len_all1 == len_all2:
                    header_data.detail_complete = True
                else:
                    header_data.detail_complete = False
                #
                inwd_list_data.append(header_data)
            vpage = NWisefinPaginator(inward_header, vys_page.get_index(), 10)
            inwd_list_data.set_pagination(vpage)
        return inwd_list_data

    def documentsummarysearch(self, vys_page, inward_obj, request):
        condition = Q(status=1) & Q(docstatus=1) & ~Q(docnumber="") & Q(rmucode="")
        if 'awb_no' in inward_obj:
            condition &= Q(inwardheader_id__awbno__icontains=inward_obj['awb_no'])
        if 'fromdate' in inward_obj:
            condition &= Q(inwardheader_id__date__range=(inward_obj['fromdate'], inward_obj['todate']))
        if 'channel_id' in inward_obj:
            condition &= Q(inwardheader_id__channel_id=inward_obj['channel_id'])
        if 'courier_id' in inward_obj:
            condition &= Q(inwardheader_id__courier_id=inward_obj['courier_id'])
        if 'docaction' in inward_obj:
            condition &= Q(docaction=inward_obj['docaction'])
        if 'assignedto' in inward_obj:
            if inward_obj['assignedto'] == inward_doc_status.UNASSIGNED:
                condition &= Q(assignemployee_id=0)
            elif inward_obj['assignedto'] == inward_doc_status.ALL:
                condition &= Q(assignemployee_id=0) | ~Q(assignemployee_id=0)
            else:
                condition &= ~Q(assignemployee_id=0)
        else:
            condition &= Q(assignemployee_id=0)
        if 'docstatus' in inward_obj:
            condition &= Q(docstatus=inward_obj['docstatus'])
        if 'doctype_id' in inward_obj:
            condition &= Q(doctype_id=inward_obj['doctype_id'])
        if 'branch_id' in inward_obj:
            condition &= Q(inwardheader_id__branch_id=inward_obj['branch_id'])
        print("con", condition)
        documentassign = InwardDetails.objects.using(self._current_app_schema()).filter(condition).order_by(
            '-created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(documentassign)
        doc_list_data = NWisefinList()
        apicall = ApiService(self._scope())
        cou_arr = []
        cha_arr = []
        doc_arr = []
        br_arr = []
        assemp_arr = []
        dept_arr = []
        if list_length > 0:
            for i in documentassign:
                cou_arr.append(i.inwardheader.courier_id)
                cha_arr.append(i.inwardheader.channel_id)
                br_arr.append(i.inwardheader.branch_id)
                doc_arr.append(i.doctype_id)
                if i.assignemployee_id != 0:
                    assemp_arr.append(i.assignemployee_id)
                if i.assigndept_id != 0:
                    dept_arr.append(i.assigndept_id)

        cou_data = apicall.get_courier(request, cou_arr)
        cha_data = apicall.get_channel(request, cha_arr)
        docu_data = apicall.get_doctype(request, doc_arr)
        br_data = apicall.get_employeebranch(request, br_arr)
        if len(assemp_arr)>0:
            assemp_data = apicall.get_employee(request, assemp_arr)
        else:
            assemp_data = []
        if len(dept_arr) > 0:
            assdept_data = apicall.get_department(request, dept_arr)
        else:
            assdept_data = []
        if (len(documentassign) > 0):
            for docassign in documentassign:
                doc_data = DetailsResponse()
                if docassign.doctype_id != 0:
                    doc_data.set_doctype_id(docassign.doctype_id, docu_data['data'])
                else:
                    doc_data.doctype_id = None
                doc_data.set_id(docassign.id)
                doc_data.set_inwardheader_id(docassign.inwardheader_id)
                # fe purpose
                doc_data.check_key = False
                doc_data.assigncheck_key = False

                doc_data.set_awbno(docassign.inwardheader.awbno)
                doc_data.set_date(docassign.inwardheader.date)
                doc_data.set_branch_id(docassign.inwardheader.branch_id, br_data['data'])
                # action type
                # comment
                doc_data.set_channel_id(docassign.inwardheader.channel_id, cha_data['data'])
                if docassign.inwardheader.courier_id == -1 or docassign.inwardheader.courier_id is None:
                    doc_data.courier_id=None
                else:
                    doc_data.set_courier_id(docassign.inwardheader.courier_id, cou_data['data'])
                doc_data.set_docnumber(docassign.docnumber)
                doc_data.set_tenor(docassign.tenor)
                if docassign.doctype_id != 0:
                    doc_data.set_doctype_id(docassign.doctype_id, docu_data['data'])
                else:
                    doc_data.doctype_id = None
                doc_data.set_status(docassign.status)
                doc_data.set_docaction(docassign.docaction)
                if docassign.docstatus == inward_status.REOPEN:
                    doc_data.set_docstatus(inward_status.REOPEN_Type)
                elif docassign.docstatus == inward_status.OPEN:
                    doc_data.set_docstatus(inward_status.OPEN)
                elif docassign.docstatus == inward_status.CLOSED:
                    doc_data.set_docstatus(inward_status.CLOSED_Type)

                if docassign.assigndept_id != 0:
                    doc_data.set_assigndept_id(docassign.assigndept_id, assdept_data['data'])  # reffered dept
                else:
                    doc_data.assigndept_id = None

                if docassign.assignemployee_id != 0:
                    doc_data.set_assignemployee_id(docassign.assignemployee_id, assemp_data['data'])
                else:
                    doc_data.assignemployee_id = None
                doc_data.set_actiontype(docassign.actiontype)
                inwfile = InwardFiles.objects.using(self._current_app_schema()).filter(inwarddetails_id=docassign.id)
                date_lenth = len(inwfile)
                file_list = list()
                if date_lenth > 0:
                    for doc in inwfile:
                        file_data = InwardFileResponse()
                        file_data.set_id(doc.id)
                        file_data.set_file_id(doc.file_id)
                        file_data.set_inwarddetails(doc.inwarddetails_id)
                        file_data.set_commentdoc(doc.commentdoc_id)
                        file_list.append(file_data)
                doc_data.set_file_data(file_list)
                doc_data.set_rmucode(docassign.rmucode)
                doc_data.set_remarks(docassign.remarks)
                doc_data.set_assignremarks(docassign.assignremarks)

                #FE PURPOSE
                file_name = "file" + str(docassign.id)
                doc_data.file_key = [file_name]
                doc_data.file_name = file_name
                doc_data.filearray = []
                doc_data.fieldkey = False
                doc_list_data.append(doc_data)
            vpage = NWisefinPaginator(documentassign, vys_page.get_index(), 10)
            doc_list_data.set_pagination(vpage)
        return doc_list_data

    def documentassignupdate(self, request, inward_req, emp_id, id_arr):
        if inward_req.get_bulk() == 0:
            logger.info("documentassignupdate single" +str(id_arr))
            for x in id_arr:
                inward_obj = InwardDetails.objects.using(self._current_app_schema()).filter(
                                                                        id=x).update(
                                                                        actiontype=inward_req.get_actiontype(),
                                                                        tenor=inward_req.get_tenor(),
                                                                        assigndept_id=inward_req.get_assigndept(),
                                                                        assignemployee_id=inward_req.get_assignemployee(),
                                                                        docaction=inward_req.get_docaction(),
                                                                        docstatus=inward_status.OPEN,
                                                                        assignremarks=inward_req.get_assignremarks(),
                                                                       # pagecount=inward_req.get_pagecount(),
                                                                       # remarks=inward_req.get_remarks(),
                                                                        updated_by=emp_id,
                                                                        updated_date=now())
                inward_obj = InwardDetails.objects.using(self._current_app_schema()).get(id=x)

                api_serv = ApiService(self._scope())
                assignto = api_serv.fetch_employeedata(request, inward_obj.assignemployee_id)
                emp_code = assignto['code']
                InwardQueue.objects.using(self._current_app_schema()).create(ref_id=inward_obj.id,
                                                                     ref_type=RefType.INWARDDETAIL,
                                                                     from_user_id=emp_id,
                                                                     to_user_id=inward_obj.assignemployee_id,
                                                                     created_date=now(),
                                                                     comments="Assign to " + str(emp_code),
                                                                     status=inward_obj.docstatus,
                                                                     is_sys=True,
                                                                     remarks=inward_obj.assignremarks)
                if inward_obj.docaction == inward_docaction.RETAINED_AT_BRANCH:
                    condition = ~Q(rmucode="") & ~Q(rmucode="-")
                    inward_rmu = InwardDetails.objects.using(self._current_app_schema()).filter(condition).order_by(
                        '-rmucode').values("rmucode")
                    if len(inward_rmu) > 0:
                        last_current_rmuno = inward_rmu[0]
                        rmucode = last_current_rmuno["rmucode"]
                        split_last_current_rmuno = rmucode[-4:]
                        final_rmucode = int(split_last_current_rmuno) + 1

                    else:
                        final_rmucode = 1
                    rmucode = "RMU" + str(datetime.now().strftime("%y%m%d")) + str(final_rmucode).zfill(4)
                    inward_obj.rmucode = rmucode
                    inward_obj.save()
                elif inward_obj.docaction == inward_docaction.DISPATCHED_TO_BRANCH:
                    inward_obj.rmucode = "-"
                    inward_obj.save()
                api_serv = ApiService(self._scope())
                assignto = api_serv.fetch_employeedata(request, emp_id)
                assignemployee = assignto['name']

                detail_data = DetailsResponse()
                detail_data.set_id(inward_obj.id)
                # if inward_obj.docaction == inward_docaction.RETAINED_AT_BRANCH:
                #     detail_data.set_docaction(inward_docaction.RETAINED_AT_BRANCH_Type)
                # elif inward_obj.docaction == inward_docaction.DISPATCHED_TO_BRANCH:
                #     detail_data.set_docaction(inward_docaction.DISPATCHED_TO_BRANCH_Type)
                # detail_data.set_tenor(inward_obj.tenor)
                # if inward_obj.actiontype == inward_action.INFORMATION_ONLY:
                #     detail_data.set_actiontype(inward_action.INFORMATION_ONLY_Type)
                # elif inward_obj.actiontype == inward_action.REPLY_MUST:
                #     detail_data.set_actiontype(inward_action.REPLY_MUST_Type)
                # elif inward_obj.actiontype == inward_action.ACTION_MUST:
                #     detail_data.set_actiontype(inward_action.ACTION_MUST_Type)
                detail_data.set_actiontype(inward_obj.actiontype)
                # if inward_obj.docstatus == inward_status.OPEN:
                #     detail_data.set_docstatus(inward_status.OPEN_Type)
                if inward_obj.docstatus == inward_status.REOPEN:
                    detail_data.set_docstatus(inward_status.REOPEN_Type)
                else:
                    detail_data.set_docstatus(inward_obj.docstatus)
                detail_data.set_docnumber(inward_obj.docnumber)
                # detail_data.set_status(inward_obj.status)
                detail_data.assigndept_id = api_serv.fetch_departmentdata(request, inward_obj.assigndept_id)
                detail_data.assignemployee_id = api_serv.fetch_employeedata(request, inward_obj.assignemployee_id)
                detail_data.set_rmucode(inward_obj.rmucode)
                detail_data.set_tenor(inward_obj.tenor)
                detail_data.set_remarks(inward_obj.remarks)
                detail_data.set_assignremarks(inward_obj.assignremarks)
                detail_data.id_arr = id_arr
                detail_data.ref = False
                # fe purpose
                detail_data.assigncheck_key = False
                detail_data.check_key = False
                # detail_data.escsubtypekey = False
                # detail_data.productcatkey = False
                # detail_data.productsubcatkey = False
                # detail_data.remarkkey = False
                return detail_data
        else:
            logger.info("documentassignupdate bulk" + str(id_arr))
            for x in id_arr:
                inward_obj = InwardDetails.objects.using(self._current_app_schema()).filter(id=x).update(
                    actiontype=inward_req.get_actiontype(),
                    tenor=inward_req.get_tenor(),
                    assigndept_id=inward_req.get_assigndept(),
                    assignemployee_id=inward_req.get_assignemployee(),
                    updated_by=emp_id,
                    updated_date=now())
                inward_obj = InwardDetails.objects.using(self._current_app_schema()).get(id=x)
                api_serv = ApiService(self._scope())
                assignto = api_serv.fetch_employeedata(request, inward_obj.assignemployee_id)
                emp_code = assignto['code']
                InwardQueue.objects.using(self._current_app_schema()).create(ref_id=inward_obj.id,
                                                                     ref_type=RefType.INWARDDETAIL,
                                                                     from_user_id=emp_id,
                                                                     to_user_id=inward_obj.assignemployee_id,
                                                                     created_date=now(),
                                                                     comments="Assign to " + str(emp_code),
                                                                     status=inward_obj.docstatus,
                                                                     is_sys=True,
                                                                     remarks=inward_req.get_remarks())
                api_serv = ApiService(self._scope())
                assignto = api_serv.fetch_employeedata(request, emp_id)
                assignemployee = assignto['name']

                detail_data = DetailsResponse()
                detail_data.set_id(inward_obj.id)
                detail_data.set_tenor(inward_obj.tenor)
                detail_data.assigndept_id = api_serv.fetch_departmentdata(request, inward_obj.assigndept_id)
                detail_data.assignemployee_id = api_serv.fetch_employeedata(request, inward_obj.assignemployee_id)
                detail_data.set_assignemployee(assignemployee)
                detail_data.set_rmucode(inward_obj.rmucode)
                detail_data.id_arr = id_arr
                #fe purpose
                detail_data.assigncheck_key = False
                detail_data.check_key = False
                # if inward_obj.docaction == inward_docaction.RETAINED_AT_BRANCH:
                #     detail_data.set_docaction(inward_docaction.RETAINED_AT_BRANCH_Type)
                # elif inward_obj.docaction == inward_docaction.DISPATCHED_TO_BRANCH:
                #     detail_data.set_docaction(inward_docaction.DISPATCHED_TO_BRANCH_Type)

                # if inward_obj.actiontype == inward_action.INFORMATION_ONLY:
                #     detail_data.set_actiontype(inward_action.INFORMATION_ONLY_Type)
                # elif inward_obj.actiontype == inward_action.REPLY_MUST:
                #     detail_data.set_actiontype(inward_action.REPLY_MUST_Type)
                # elif inward_obj.actiontype == inward_action.ACTION_MUST:
                #     detail_data.set_actiontype(inward_action.ACTION_MUST_Type)
                detail_data.set_actiontype(inward_obj.actiontype)
            return detail_data

    def documentresponseupdate(self, request, inward_req, emp_id):
        inward_obj = InwardDetails.objects.using(self._current_app_schema()).filter(id=inward_req.get_id()).update(
                                                    assigndept_id=inward_req.get_assigndept(),
                                                    assignemployee_id=inward_req.get_assignemployee(),
                                                    docstatus=inward_req.get_docstatus(),
                                                    remarks=inward_req.get_remarks(),
                                                    updated_by=emp_id,
                                                    updated_date=now())
        inward_obj = InwardDetails.objects.using(self._current_app_schema()).get(id=inward_req.get_id())

        api_serv = ApiService(self._scope())
        assignto = api_serv.fetch_employeedata(request, emp_id)
        emp_code = assignto['code']
        assignemployee = assignto['name']

        InwardQueue.objects.using(self._current_app_schema()).create(ref_id=inward_obj.id,
                                                             ref_type=RefType.INWARDDETAIL,
                                                             from_user_id=emp_id,
                                                             to_user_id=emp_id,
                                                             created_date=now(),
                                                             comments="updated by" + str(emp_code),
                                                             status=inward_obj.docstatus,
                                                             is_sys=True,
                                                             remarks=inward_req.get_remarks())
        detail_data = DetailsResponse()
        detail_data.set_id(inward_obj.id)
        if inward_obj.docstatus == inward_status.CLOSED:
            detail_data.set_docstatus(inward_status.CLOSED)
        detail_data.set_assigndept(inward_obj.assigndept_id)
        detail_data.set_assignemployee(assignemployee)
        # detail_data.set_docstatus(inward_obj.docstatus)
        detail_data.set_remarks(inward_obj.remarks)
        return detail_data

    def fetch_inwarddetails(self, inward_id):
        inward_details = InwardDetails.objects.using(self._current_app_schema()).filter(inwardheader_id=inward_id, status=1)
        list_length = len(inward_details)
        header_data = InwardHeaderResponse()
        assemp_arr = []
        for i in inward_details:
            if i.assignemployee_id != 0:
                assemp_arr.append(i.assignemployee_id)
        if len(assemp_arr) > 0:
            assigned = True
        else:
            assigned = False

        inwarddetail_arr = []
        packetno_arr = []
        id_arr = []
        for i in inward_details:

            if i.packetno not in packetno_arr:
                packetno_arr.append(i.packetno)
                id_arr.append(i.id)
        for (packetno,id) in zip(packetno_arr, id_arr):
            detail_data = DetailsResponse()
            detail_data.set_id(id)
            detail_data.set_packetno(packetno)
            detail_data.inwardheader_id = inward_id
            detail_data.assigned = assigned
            inwarddtl = InwardDetails.objects.using(self._current_app_schema()).get(id=id)
            detail_data.set_doccount(inwarddtl.doccount)
            # fe purpose
            detail_data.details = []
            inwarddetail_arr.append(json.loads(detail_data.get()))
            header_data.inwarddetails_detail = inwarddetail_arr
        return header_data

    def inwarddetails(self, inward_id, packet_no, request):
        inwdheader = InwardHeader.objects.using(self._current_app_schema()).get(id=inward_id)
        header_data = InwardHeaderResponse()
        apicall = ApiService(self._scope())
        header_data.set_id(inwdheader.id)
        header_data.set_no(inwdheader.no)
        header_data.set_date(inwdheader.date)
        cha_data = apicall.fetch_channeldata(request, inwdheader.channel_id)
        header_data.set_channel(cha_data)
        print("cha_data", cha_data)
        if inwdheader.courier_id == 0 or inwdheader.courier_id == -1 or inwdheader.courier_id is None:
            header_data.courier = None
        else:
            cou_data = apicall.fetch_courierdata(request, inwdheader.courier_id)
            header_data.set_courier(cou_data)
            print("cou_data", cou_data)
        # header_data.set_courier(courierdata_resp)
        header_data.set_awbno(inwdheader.awbno)
        header_data.set_noofpockets(inwdheader.noofpockets)
        header_data.set_status(get_inward_status(inwdheader.status))
        createby_data = apicall.fetch_employeedata(request, inwdheader.created_by)
        employee_branch_id = createby_data["employee_branch_id"]
        employee_branch_code = createby_data["employee_branch_code"]
        employee_branch_name = createby_data["employee_branch_name"]
        employeebranch_name = '(' + employee_branch_code + ') ' + employee_branch_name
        # header_data.employeebranch_name = employee_branch_code + ' -- ' + employee_branch_name
        header_data.employeebranch_name = employeebranch_name
        header_data.set_awbno(inwdheader.awbno)
        header_data.set_noofpockets(inwdheader.noofpockets)
        inwarddetail_arr = []
        inward_details = InwardDetails.objects.using(self._current_app_schema()).filter(
            inwardheader_id=inward_id, packetno=packet_no, status=1).order_by('created_date')
        doc_arr = []
        for i in inward_details:
            doc_arr.append(i.doctype_id)
        apicall = ApiService(self._scope())
        doc_data = apicall.get_doctype(request, doc_arr)
        for inwarddetails in inward_details:
            detail_data = DetailsResponse()
            detail_data.set_id(inwarddetails.id)
            #detail_data.set_file_key(inwarddetails.file_key)
            detail_data.set_doccount(inwarddetails.doccount)
            detail_data.set_packetno(inwarddetails.packetno)
            detail_data.set_assignemployee(inwarddetails.assignemployee_id)
            detail_data.set_docstatus(inwarddetails.docstatus)
            detail_data.set_docnumber(inwarddetails.docnumber)
            detail_data.set_receivedfrom(inwarddetails.receivedfrom)
            detail_data.set_pagecount(inwarddetails.pagecount)
            detail_data.set_docsubject(inwarddetails.docsubject)
            if inwarddetails.doctype_id != 0:
                detail_data.set_doctype_id(inwarddetails.doctype_id, doc_data['data'])
            else:
                detail_data.doctype_id=None
            # detail_data.doctype_id = inwarddetails.doctype_id

            inwfile = InwardFiles.objects.using(self._current_app_schema()).filter(inwarddetails_id=inwarddetails.id)
            # doc_file = apicall.get_docfile(request, doc_arr)
            date_lenth = len(inwfile)
            file_list = list()
            if date_lenth > 0:
                for doc in inwfile:
                    file_data = InwardFileResponse()
                    file_data.set_id(doc.id)
                    file_data.set_file_id(doc.file_id)
                    file_data.set_inwarddetails(doc.inwarddetails_id)
                    file_data.set_commentdoc(doc.commentdoc_id)
                    file_list.append(file_data)
            detail_data.set_file_data(file_list)
            #detail_data.set_docnumber(inwarddetails.docnumber)
            # if inwarddetails.doctype_id != 0:
            #     detail_data.set_doctype_id(inwarddetails.doctype_id, doc_data['data'])
            #
            # else:
            #     detail_data.doctype_id=None
            detail_data.set_packetno(inwarddetails.packetno)
            detail_data.set_remarks(inwarddetails.remarks)
            detail_data.set_inwardheader(self.fetch_inward(request, inwarddetails.inwardheader_id))
            detail_data.inwardheader_id = inwarddetails.inwardheader_id
            # frontend purpose
            detail_data.doctypekey = False
            detail_data.docsubkey = False
            detail_data.pagecountkey = False
            detail_data.receivedfromkey = False
            detail_data.statuskey = False
            detail_data.documentnokey = False
            file_name = "file" + str(inwarddetails.id)
            detail_data.file_key = [file_name]
            detail_data.file_name = file_name
            detail_data.filearray = []
            # detail_data.(file + str(inwarddetails.id)) = []
           # detail_data.filekey = False
            detail_data.remarkkey = False
            inwarddetail_arr.append(json.loads(detail_data.get()))
        header_data.inwarddetails_detail = inwarddetail_arr
        return header_data

    def clone_packet_count(self, request, emp_id, inwardheader_id, packetno, count):
        try:
            inwardhdr_data = InwardHeader.objects.using(self._current_app_schema()).get(id=inwardheader_id)
            count_range = range(count)
            print("count_range", count_range)
            logger.info("count_range" + str(count_range))
            id_arr = []
            for i in count_range:
                print("i", i)
                inwarddetails = InwardDetails.objects.using(self._current_app_schema()).create(inwardheader_id=inwardheader_id,
                                                                                    packetno=packetno,
                                                                                    created_by=emp_id,
                                                                                    created_date=now())

                self.inward_audit(inwarddetails.__dict__, inwarddetails.id, emp_id, RequestStatusUtil.ONBORD, inwarddetails.id,
                                  ModifyStatus.CREATE, InwardRefType.INWARD_DETAIL)
                id_arr.append(inwarddetails.id)
            inwarddtl = InwardDetails.objects.using(self._current_app_schema()).filter(inwardheader_id=inwardheader_id,
                                                                               packetno=packetno,
                                                                               status=1)
            inwarddtl1 = inwarddtl[0]
            inwarddtl2 = InwardDetails.objects.using(self._current_app_schema()).get(id=inwarddtl1.id)
            doccount = inwarddtl2.doccount + count
            for d in inwarddtl:
                inwarddtl = InwardDetails.objects.using(self._current_app_schema()).filter(inwardheader_id=inwardheader_id,
                                                                                   packetno=packetno,
                                                                                   status=1
                                                                                   ).update(doccount=doccount)

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
        inwdheader = InwardHeader.objects.using(self._current_app_schema()).get(id=inwardheader_id)
        header_data = InwardHeaderResponse()
        apicall = ApiService(self._scope())
        header_data.set_id(inwdheader.id)
        header_data.set_no(inwdheader.no)
        header_data.set_date(inwdheader.date)
        cha_data = apicall.fetch_channeldata(request, inwdheader.channel_id)
        header_data.set_channel(cha_data)
        print("cha_data", cha_data)
        cou_data = apicall.fetch_courierdata(request, inwdheader.courier_id)
        header_data.set_courier(cou_data)
        print("cou_data", cou_data)
        header_data.set_awbno(inwdheader.awbno)
        header_data.set_noofpockets(inwdheader.noofpockets)
        header_data.set_status(get_inward_status(inwdheader.status))
        createby_data = apicall.fetch_employeedata(request, inwdheader.created_by)
        employee_branch_id = createby_data["employee_branch_id"]
        employee_branch_code = createby_data["employee_branch_code"]
        employee_branch_name = createby_data["employee_branch_name"]
        header_data.employeebranch_name = employee_branch_code + ' -- ' + employee_branch_name

        header_data.set_awbno(inwdheader.awbno)
        header_data.set_noofpockets(inwdheader.noofpockets)
        inwarddtl = InwardDetails.objects.using(self._current_app_schema()).filter(inwardheader_id=inwdheader.id,
                                                                           packetno=packetno, status=1)

        doccount = 0
        for d in inwarddtl:
            count = d.doccount
            doccount += count
        header_data.doccount = doccount
        inwarddetail_arr = []
        inward_details = InwardDetails.objects.using(self._current_app_schema()).filter(id__in=id_arr)
        doc_arr = []
        for i in inward_details:
            doc_arr.append(i.doctype_id)
        apicall = ApiService(self._scope())
        doc_data = apicall.get_doctype(request, doc_arr)
        for inwarddetails in inward_details:
            detail_data = DetailsResponse()
            detail_data.set_id(inwarddetails.id)
            # detail_data.set_file_key(inwarddetails.file_key)
            detail_data.set_doccount(inwarddetails.doccount)
            detail_data.set_packetno(inwarddetails.packetno)
            detail_data.set_assignemployee(inwarddetails.assignemployee_id)
            detail_data.set_docstatus(inwarddetails.docstatus)
            detail_data.set_docnumber(inwarddetails.docnumber)
            detail_data.set_receivedfrom(inwarddetails.receivedfrom)
            detail_data.set_pagecount(inwarddetails.pagecount)
            detail_data.set_docsubject(inwarddetails.docsubject)
            detail_data.set_docnumber(inwarddetails.docnumber)
            if inwarddetails.doctype_id != 0:
                detail_data.set_doctype_id(inwarddetails.doctype_id, doc_data['data'])
            else:
                detail_data.doctype_id = None
            detail_data.set_packetno(inwarddetails.packetno)
            detail_data.set_remarks(inwarddetails.remarks)
            # frontend purpose
            detail_data.doctypekey = False
            detail_data.docsubkey = False
            detail_data.pagecountkey = False
            detail_data.receivedfromkey = False
            detail_data.statuskey = False
            detail_data.documentnokey = False
            #detail_data.filekey = False
            file_name = "file" + str(inwarddetails.id)
            detail_data.file_key = [file_name]
            detail_data.file_name = file_name
            detail_data.filearray = []
            detail_data.remarkkey = False
            detail_data.set_inwardheader(self.fetch_inward(request, inwarddetails.inwardheader_id))
            detail_data.inwardheader_id = inwarddetails.inwardheader_id
            inwarddetail_arr.append(json.loads(detail_data.get()))
        header_data.inwarddetails_detail = inwarddetail_arr
        return header_data

    def inwarddetailupdate(self, request, inward_req, emp_id):
        inward_obj = InwardDetails.objects.using(self._current_app_schema()).filter(id=inward_req.get_id()).update(
            actiontype=inward_req.get_actiontype(),
            pagecount=inward_req.get_pagecount(),
            receivedfrom=inward_req.get_receivedfrom(),
            docsubject=inward_req.get_docsubject(),
            doctype_id=inward_req.get_doctype(),
            docstatus=inward_status.OPEN,
            remarks=inward_req.get_remarks(),
            updated_by=emp_id,
            updated_date=now())
        inward_obj = InwardDetails.objects.using(self._current_app_schema()).get(id=inward_req.get_id())

        condition = ~Q(docnumber="")
        inward_doc = InwardDetails.objects.using(self._current_app_schema()).filter(condition).order_by('-docnumber').values(
            "docnumber")
        if len(inward_doc) > 0:
            last_current_docnumber = inward_doc[0]
            docnumber = last_current_docnumber["docnumber"]
            split_last_current_docnumber = docnumber[-4:]
            final_docnumber = int(split_last_current_docnumber) + 1

        else:
            final_docnumber = 1

        docnumber = inward_obj.docnumber
        # print("docnumber", docnumber)
        if (docnumber == '') | (docnumber == None):
            docnumber = "DOC" + str(datetime.now().strftime("%y%m%d")) + str(final_docnumber).zfill(4)
            inward_obj.docnumber = docnumber
            inward_obj.save()

        detail_data = DetailsResponse()
        detail_data.set_id(inward_obj.id)
        if inward_obj.actiontype == inward_action.INFORMATION_ONLY:
            detail_data.set_actiontype(inward_action.INFORMATION_ONLY_Type)
        elif inward_obj.actiontype == inward_action.REPLY_MUST:
            detail_data.set_actiontype(inward_action.REPLY_MUST_Type)
        elif inward_obj.actiontype == inward_action.ACTION_MUST:
            detail_data.set_actiontype(inward_action.ACTION_MUST_Type)
        if inward_obj.docstatus == inward_status.OPEN:
            detail_data.set_docstatus(inward_status.OPEN_Type)
        else:
            detail_data.set_docstatus(inward_obj.docstatus)
        detail_data.set_docnumber(inward_obj.docnumber)
        detail_data.set_docsubject(inward_obj.docsubject)
        detail_data.set_doctype(inward_obj.doctype_id)
        detail_data.set_receivedfrom(inward_obj.receivedfrom)
        detail_data.set_pagecount(inward_obj.pagecount)
        detail_data.set_remarks(inward_obj.remarks)
        print ("create data", detail_data)
        return detail_data

    def inward_details_clone(self, request, inwarddtl_id, user_id):
        try:
            inwarddtl_data = InwardDetails.objects.using(self._current_app_schema()).get(id=inwarddtl_id)
            doccount= inwarddtl_data.doccount + 1
            inwarddtl = InwardDetails.objects.using(self._current_app_schema()).filter(id=inwarddtl_id).update(
                doccount=doccount)
            inwarddetails = InwardDetails.objects.using(self._current_app_schema()).create(
                inwardheader_id=inwarddtl_data.inwardheader_id,
                packetno=inwarddtl_data.packetno,
                doctype_id=inwarddtl_data.doctype_id,
                doccount=doccount,
                actiontype=inwarddtl_data.actiontype,
                pagecount=inwarddtl_data.pagecount,
                receivedfrom=inwarddtl_data.receivedfrom,
                docsubject=inwarddtl_data.docsubject,
                docstatus=inward_status.OPEN,
                remarks=inwarddtl_data.remarks,
                created_by=user_id,
                created_date=now())
            self.inward_audit(inwarddetails.__dict__, inwarddetails.id, user_id, RequestStatusUtil.ONBORD,
                              inwarddetails.id,
                              ModifyStatus.CREATE, InwardRefType.INWARD_DETAIL)

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
        # inwdheader = InwardHeader.objects.using(self._current_app_schema()).get(id=inwarddetails.inwardheader_id)
        # header_data = InwardHeaderResponse()
        # apicall = ApiService(self._scope())
        # header_data.set_id(inwdheader.id)
        # header_data.set_no(inwdheader.no)
        # header_data.set_date(inwdheader.date)
        # cha_data = apicall.fetch_channeldata(request, inwdheader.channel_id)
        # header_data.set_channel(cha_data)
        # cou_data = apicall.fetch_courierdata(request, inwdheader.courier_id)
        # header_data.set_courier(cou_data)
        # header_data.set_awbno(inwdheader.awbno)
        # header_data.set_noofpockets(inwdheader.noofpockets)
        # header_data.set_status(get_inward_status(inwdheader.status))
        # createby_data = apicall.fetch_employeedata(request, inwdheader.created_by)
        # employee_branch_code = createby_data["employee_branch_code"]
        # employee_branch_name = createby_data["employee_branch_name"]
        # header_data.employeebranch_name = employee_branch_code + ' -- ' + employee_branch_name
        #
        # header_data.set_awbno(inwdheader.awbno)
        # header_data.set_noofpockets(inwdheader.noofpockets)
        inwarddetail_arr = []
        inward_details = InwardDetails.objects.using(self._current_app_schema()).filter(id=inwarddetails.id)
        doc_arr = []
        for i in inward_details:
            doc_arr.append(i.doctype_id)
        apicall = ApiService(self._scope())
        doc_data = apicall.get_doctype(request, doc_arr)
        for inwarddetails in inward_details:
            detail_data = DetailsResponse()
            detail_data.set_id(inwarddetails.id)
            detail_data.set_doccount(inwarddetails.doccount)
            detail_data.set_packetno(inwarddetails.packetno)
            detail_data.set_assignemployee(inwarddetails.assignemployee_id)
            detail_data.set_docstatus(inwarddetails.docstatus)
            detail_data.set_docnumber(inwarddetails.docnumber)
            detail_data.set_receivedfrom(inwarddetails.receivedfrom)
            detail_data.set_pagecount(inwarddetails.pagecount)
            detail_data.set_docsubject(inwarddetails.docsubject)
            if inwarddetails.doctype_id != 0:
                detail_data.set_doctype_id(inwarddetails.doctype_id, doc_data['data'])
            else:
                detail_data.doctype_id = None
            detail_data.set_packetno(inwarddetails.packetno)
            detail_data.set_remarks(inwarddetails.remarks)
            # frontend purpose
            detail_data.doctypekey = False
            detail_data.docsubkey = False
            detail_data.pagecountkey = False
            detail_data.receivedfromkey = False
            detail_data.statuskey = False
            detail_data.documentnokey = False
            detail_data.filekey = False
            detail_data.remarkkey = False
            detail_data.set_inwardheader(self.fetch_inward(request, inwarddetails.inwardheader_id))
            detail_data.inwardheader_id = inwarddetails.inwardheader_id
            inwarddetail_arr.append(json.loads(detail_data.get()))
        #header_data.inwarddetails_detail = inwarddetail_arr
        return detail_data

    # def doc_responsesummarysearch(self, emp_id, vys_page, inward_obj, request):
    #     condition = Q(assignemployee_id=emp_id) & Q(status=1) & Q(docstatus=1) & ~Q(docnumber="")
    #     if 'awb_no' in inward_obj:
    #         condition &= Q(inwardheader_id__awbno__icontains=inward_obj['awb_no'])
    #     if 'fromdate' in inward_obj:
    #         condition &= Q(inwardheader_id__date__range=(inward_obj['fromdate'], inward_obj['todate']))
    #     if 'channel_id' in inward_obj:
    #         condition &= Q(inwardheader_id__channel_id=inward_obj['channel_id'])
    #     if 'courier_id' in inward_obj:
    #         condition &= Q(inwardheader_id__courier_id=inward_obj['courier_id'])
    #     if 'docaction' in inward_obj:
    #         condition &= Q(docaction=inward_obj['docaction'])
    #     if 'assignedto' in inward_obj:
    #         if inward_obj['assignedto'] != inward_doc_status.ASSIGNED_Type:
    #             condition &= ~Q(assignemployee_id=None)
    #         elif inward_obj['assignedto'] != inward_doc_status.ALL_Type:
    #             condition &= Q(assignemployee_id=None) | ~Q(assignemployee_id=None)
    #         else:
    #             condition &= Q(assignemployee_id=None)
    #     if 'docstatus' in inward_obj:
    #         condition &= Q(docstatus=inward_obj['docstatus'])
    #     if 'doctype_id' in inward_obj:
    #         condition &= Q(doctype_id=inward_obj['doctype_id'])
    #     if 'branch_id' in inward_obj:
    #         condition &= Q(inwardheader_id__branch_id=inward_obj['branch_id'])
    #     documentassign = InwardDetails.objects.using(self._current_app_schema()).filter(condition).order_by(
    #         '-created_date')[
    #                      vys_page.get_offset():vys_page.get_query_limit()]
    #     list_length = len(documentassign)
    #     doc_list_data = NWisefinList()
    #     apicall = ApiService(self._scope())
    #     cou_arr = []
    #     cha_arr = []
    #     doc_arr = []
    #     br_arr = []
    #     assemp_arr = []
    #     dept_arr = []
    #     if list_length > 0:
    #         for i in documentassign:
    #             cou_arr.append(i.inwardheader.courier_id)
    #             cha_arr.append(i.inwardheader.channel_id)
    #             br_arr.append(i.inwardheader.branch_id)
    #             doc_arr.append(i.doctype_id)
    #             if i.assignemployee_id != 0:
    #                 assemp_arr.append(i.assignemployee_id)
    #             if i.assigndept_id != 0:
    #                 dept_arr.append(i.assigndept_id)
    #
    #     cou_data = apicall.get_courier(request, cou_arr)
    #     cha_data = apicall.get_channel(request, cha_arr)
    #     docu_data = apicall.get_doctype(request, doc_arr)
    #     br_data = apicall.get_employeebranch(request, br_arr)
    #     if len(assemp_arr)>0:
    #         assemp_data = apicall.get_employee(request, assemp_arr)
    #     else:
    #         assemp_data = []
    #     if len(dept_arr) > 0:
    #         assdept_data = apicall.get_department(request, dept_arr)
    #     else:
    #         assdept_data = []
    #     if (len(documentassign) > 0):
    #         for docassign in documentassign:
    #             doc_data = DetailsResponse()
    #             if docassign.doctype_id != 0:
    #                 doc_data.set_doctype_id(docassign.doctype_id, docu_data['data'])
    #             else:
    #                 doc_data.doctype_id = None
    #             doc_data.set_id(docassign.id)
    #             doc_data.set_inwardheader_id(docassign.inwardheader_id)
    #             # fe purpose
    #             doc_data.check_key = False
    #             doc_data.assigncheck_key = False
    #             doc_data.set_awbno(docassign.inwardheader.awbno)
    #             doc_data.set_date(docassign.inwardheader.date)
    #             doc_data.set_branch_id(docassign.inwardheader.branch_id, br_data['data'])
    #             doc_data.set_channel_id(docassign.inwardheader.channel_id, cha_data['data'])
    #             if docassign.inwardheader.courier_id == -1 or docassign.inwardheader.courier_id is None:
    #                 doc_data.courier_id=None
    #             else:
    #                 doc_data.set_courier_id(docassign.inwardheader.courier_id, cou_data['data'])
    #             doc_data.set_docnumber(docassign.docnumber)
    #             doc_data.set_tenor(docassign.tenor)
    #             doc_data.set_assignremarks(docassign.assignremarks)
    #             if docassign.doctype_id != 0:
    #                 doc_data.set_doctype_id(docassign.doctype_id, docu_data['data'])
    #             else:
    #                 doc_data.doctype_id = None
    #             doc_data.set_status(docassign.status)
    #            # doc_data.set_docstatus(docassign.docstatus)
    #             doc_data.set_docaction(docassign.docaction)
    #             #doc_data.reffered_dept = ""
    #
    #             if docassign.docstatus == inward_status.REOPEN:
    #                 doc_data.set_docstatus(inward_status.REOPEN_Type)
    #             elif docassign.docstatus == inward_status.OPEN:
    #                 doc_data.set_docstatus(inward_status.OPEN)
    #             elif docassign.docstatus == inward_status.CLOSED:
    #                 doc_data.set_docstatus(inward_status.CLOSED_Type)
    #
    #             if docassign.assigndept_id != 0:
    #                 doc_data.set_assigndept_id(docassign.assigndept_id, assdept_data['data'])  # reffered dept
    #             else:
    #                 doc_data.assigndept_id = None
    #
    #             if docassign.assignemployee_id != 0:
    #                 doc_data.set_assignemployee_id(docassign.assignemployee_id, assemp_data['data'])
    #             else:
    #                 doc_data.assignemployee_id = None
    #             doc_data.set_actiontype(docassign.actiontype)
    #             inwfile = InwardFiles.objects.using(self._current_app_schema()).filter(inwarddetails_id=docassign.id)
    #             date_lenth = len(inwfile)
    #             file_list = list()
    #             if date_lenth > 0:
    #                 for doc in inwfile:
    #                     file_data = InwardFileResponse()
    #                     file_data.set_id(doc.id)
    #                     file_data.set_file_id(doc.file_id)
    #                     file_data.set_inwarddetails(doc.inwarddetails_id)
    #                     file_data.set_commentdoc(doc.commentdoc_id)
    #                     file_list.append(file_data)
    #             doc_data.set_file_data(file_list)
    #             cmnt_docu = CommentDoc.objects.using(self._current_app_schema()).filter(inwarddetails_id=docassign.id)
    #             date_lenth = len(cmnt_docu)
    #             cmnt_docuq = list()
    #             if date_lenth > 0:
    #                 apicall = ApiService(self._scope())
    #                 for cmnt_doc in cmnt_docu:
    #                     cmnt_resp = CommentDocResponse()
    #                     cmnt_resp.set_id(cmnt_doc.id)
    #                     cmnt_resp.set_branch(apicall.fetch_employeebranchdata(request, cmnt_doc.branch_id))
    #                     cmnt_resp.set_employee(apicall.fetch_employeedata(request, cmnt_doc.employee_id))
    #                     cmnt_resp.created_by=apicall.fetch_employeedata(request, cmnt_doc.created_by)
    #                     cmnt_resp.set_comment(cmnt_doc.comment)
    #                     cmnt_resp.created_date = str(cmnt_doc.created_date)
    #                     cmnt_docuq.append(cmnt_resp)
    #             doc_data.comment_data=cmnt_docuq
    #             doc_data.set_rmucode(docassign.rmucode)
    #             doc_data.set_remarks(docassign.remarks)
    #             file_name = "file" + str(docassign.id)
    #             doc_data.file_key = [file_name]
    #             doc_data.file_name = file_name
    #             doc_data.filearray = []
    #             doc_data.fieldkey = False
    #             doc_list_data.append(doc_data)
    #         vpage = NWisefinPaginator(documentassign, vys_page.get_index(), 10)
    #         doc_list_data.set_pagination(vpage)
    #     return doc_list_data

    # def doc_responsesummarysearch(self, emp_id, vys_page, inward_obj, request):
    #     # condition = Q(ref_type=RefType.INWARDDETAIL)
    #     # if 'assignedto' in inward_obj:
    #     #     if inward_obj['assignedto'] == inward_doc_status.UNASSIGNED:
    #     #         condition &= ~Q(to_user_id=emp_id)
    #     #     elif inward_obj['assignedto'] == inward_doc_status.ALL:
    #     #         condition &= Q(from_user_id=emp_id) | Q(to_user_id=emp_id)
    #     #     else:
    #     #         condition &= Q(to_user_id=emp_id)
    #     # else:
    #     #     condition &= Q(to_user_id=emp_id)
    #     # inwardtranlist = InwardQueue.objects.using(self._current_app_schema()).filter(condition)
    #     # inwd_arr = []
    #     # for i in inwardtranlist:
    #     #     if i.ref_id not in inwd_arr:
    #     #         inwd_arr.append(i.ref_id)
    #
    #     condition = Q(status=1) & Q(docstatus=1) & ~Q(docnumber="")
    #     if 'awb_no' in inward_obj:
    #         condition &= Q(inwardheader_id__awbno__icontains=inward_obj['awb_no'])
    #     if 'fromdate' in inward_obj:
    #         condition &= Q(inwardheader_id__date__range=(inward_obj['fromdate'], inward_obj['todate']))
    #     if 'channel_id' in inward_obj:
    #         condition &= Q(inwardheader_id__channel_id=inward_obj['channel_id'])
    #     if 'courier_id' in inward_obj:
    #         condition &= Q(inwardheader_id__courier_id=inward_obj['courier_id'])
    #     if 'docaction' in inward_obj:
    #         condition &= Q(docaction=inward_obj['docaction'])
    #     if 'assignedto' in inward_obj:
    #         if inward_obj['assignedto'] != inward_doc_status.ASSIGNED_Type:
    #             condition &= ~Q(assignemployee_id=None)
    #         elif inward_obj['assignedto'] != inward_doc_status.ALL_Type:
    #             condition &= Q(assignemployee_id=None) | ~Q(assignemployee_id=None)
    #         else:
    #             condition &= Q(assignemployee_id=None)
    #     if 'docstatus' in inward_obj:
    #         condition &= Q(docstatus=inward_obj['docstatus'])
    #     if 'doctype_id' in inward_obj:
    #         condition &= Q(doctype_id=inward_obj['doctype_id'])
    #     if 'branch_id' in inward_obj:
    #         condition &= Q(inwardheader_id__branch_id=inward_obj['branch_id'])
    #     documentassign = InwardDetails.objects.using(self._current_app_schema()).filter(condition).order_by(
    #         '-created_date')[
    #                      vys_page.get_offset():vys_page.get_query_limit()]
    #     list_length = len(documentassign)
    #     doc_list_data = NWisefinList()
    #     apicall = ApiService(self._scope())
    #     cou_arr = []
    #     cha_arr = []
    #     doc_arr = []
    #     br_arr = []
    #     assemp_arr = []
    #     dept_arr = []
    #     if list_length > 0:
    #         for i in documentassign:
    #             cou_arr.append(i.inwardheader.courier_id)
    #             cha_arr.append(i.inwardheader.channel_id)
    #             br_arr.append(i.inwardheader.branch_id)
    #             doc_arr.append(i.doctype_id)
    #             if i.assignemployee_id != 0:
    #                 assemp_arr.append(i.assignemployee_id)
    #             if i.assigndept_id != 0:
    #                 dept_arr.append(i.assigndept_id)
    #
    #     cou_data = apicall.get_courier(request, cou_arr)
    #     cha_data = apicall.get_channel(request, cha_arr)
    #     docu_data = apicall.get_doctype(request, doc_arr)
    #     br_data = apicall.get_employeebranch(request, br_arr)
    #     if len(assemp_arr)>0:
    #         assemp_data = apicall.get_employee(request, assemp_arr)
    #     else:
    #         assemp_data = []
    #     if len(dept_arr) > 0:
    #         assdept_data = apicall.get_department(request, dept_arr)
    #     else:
    #         assdept_data = []
    #     if (len(documentassign) > 0):
    #         for docassign in documentassign:
    #             doc_data = DetailsResponse()
    #             if docassign.doctype_id != 0:
    #                 doc_data.set_doctype_id(docassign.doctype_id, docu_data['data'])
    #             else:
    #                 doc_data.doctype_id = None
    #             doc_data.set_id(docassign.id)
    #             doc_data.set_inwardheader_id(docassign.inwardheader_id)
    #             # fe purpose
    #             doc_data.check_key = False
    #             doc_data.assigncheck_key = False
    #             doc_data.set_awbno(docassign.inwardheader.awbno)
    #             doc_data.set_date(docassign.inwardheader.date)
    #             doc_data.set_branch_id(docassign.inwardheader.branch_id, br_data['data'])
    #             doc_data.set_channel_id(docassign.inwardheader.channel_id, cha_data['data'])
    #             if docassign.inwardheader.courier_id == -1 or docassign.inwardheader.courier_id is None:
    #                 doc_data.courier_id=None
    #             else:
    #                 doc_data.set_courier_id(docassign.inwardheader.courier_id, cou_data['data'])
    #             doc_data.set_docnumber(docassign.docnumber)
    #             doc_data.set_tenor(docassign.tenor)
    #             doc_data.set_assignremarks(docassign.assignremarks)
    #             if docassign.doctype_id != 0:
    #                 doc_data.set_doctype_id(docassign.doctype_id, docu_data['data'])
    #             else:
    #                 doc_data.doctype_id = None
    #             doc_data.set_status(docassign.status)
    #            # doc_data.set_docstatus(docassign.docstatus)
    #             doc_data.set_docaction(docassign.docaction)
    #             #doc_data.reffered_dept = ""
    #
    #             if docassign.docstatus == inward_status.REOPEN:
    #                 doc_data.set_docstatus(inward_status.REOPEN_Type)
    #             elif docassign.docstatus == inward_status.OPEN:
    #                 doc_data.set_docstatus(inward_status.OPEN)
    #             elif docassign.docstatus == inward_status.CLOSED:
    #                 doc_data.set_docstatus(inward_status.CLOSED_Type)
    #
    #             if docassign.assigndept_id != 0:
    #                 doc_data.set_assigndept_id(docassign.assigndept_id, assdept_data['data'])  # reffered dept
    #             else:
    #                 doc_data.assigndept_id = None
    #
    #             if docassign.assignemployee_id != 0:
    #                 doc_data.set_assignemployee_id(docassign.assignemployee_id, assemp_data['data'])
    #             else:
    #                 doc_data.assignemployee_id = None
    #             doc_data.set_actiontype(docassign.actiontype)
    #             inwfile = InwardFiles.objects.using(self._current_app_schema()).filter(inwarddetails_id=docassign.id)
    #             date_lenth = len(inwfile)
    #             file_list = list()
    #             if date_lenth > 0:
    #                 for doc in inwfile:
    #                     file_data = InwardFileResponse()
    #                     file_data.set_id(doc.id)
    #                     file_data.set_file_id(doc.file_id)
    #                     file_data.set_inwarddetails(doc.inwarddetails_id)
    #                     file_data.set_commentdoc(doc.commentdoc_id)
    #                     file_list.append(file_data)
    #             doc_data.set_file_data(file_list)
    #             cmnt_docu = CommentDoc.objects.using(self._current_app_schema()).filter(inwarddetails_id=docassign.id)
    #             date_lenth = len(cmnt_docu)
    #             cmnt_docuq = list()
    #             if date_lenth > 0:
    #                 apicall = ApiService(self._scope())
    #                 for cmnt_doc in cmnt_docu:
    #                     cmnt_resp = CommentDocResponse()
    #                     cmnt_resp.set_id(cmnt_doc.id)
    #                     cmnt_resp.set_branch(apicall.fetch_employeebranchdata(request, cmnt_doc.branch_id))
    #                     cmnt_resp.set_employee(apicall.fetch_employeedata(request, cmnt_doc.employee_id))
    #                     cmnt_resp.created_by=apicall.fetch_employeedata(request, cmnt_doc.created_by)
    #                     cmnt_resp.set_comment(cmnt_doc.comment)
    #                     cmnt_resp.created_date = str(cmnt_doc.created_date)
    #                     cmnt_docuq.append(cmnt_resp)
    #             doc_data.comment_data=cmnt_docuq
    #             doc_data.set_rmucode(docassign.rmucode)
    #             doc_data.set_remarks(docassign.remarks)
    #             #FE PURPOSE
    #             file_name = "file" + str(docassign.id)
    #             doc_data.file_key = [file_name]
    #             doc_data.file_name = file_name
    #             doc_data.filearray = []
    #             doc_data.fieldkey = False
    #             docassign.docstatus == inward_status.REOPEN
    #             doc_list_data.append(doc_data)
    #         vpage = NWisefinPaginator(documentassign, vys_page.get_index(), 10)
    #         doc_list_data.set_pagination(vpage)
    #     return doc_list_data

    def inwardtran(self, details_id, emp_id, vys_page, request):
        condition = Q(ref_type=RefType.INWARDDETAIL) & Q(ref_id=details_id)
        inwardtranlist = InwardQueue.objects.using(self._current_app_schema()).filter(condition)
        list_length = len(inwardtranlist)
        print(list_length)
        inwardtrans = NWisefinList()
        if list_length > 0:
            apicall = ApiService(self._scope())
            for iwd_tran in inwardtranlist:
                inwardtran_data = InwardTranResponse()
                inwardtran_data.set_id(iwd_tran.id)
                inwardtran_data.set_ref_id(self.fetch_inward_details(iwd_tran.ref_id, emp_id, request))
                inwardtran_data.set_ref_type(iwd_tran.ref_type)
                user_fromemployee = apicall.fetch_employeedata(request, iwd_tran.from_user_id)
                user_toemployee = apicall.fetch_employeedata(request, iwd_tran.to_user_id)
                inwardtran_data.set_from_user_id(user_fromemployee)
                inwardtran_data.set_to_user_id(user_toemployee)
                inwardtran_data.set_created_date(iwd_tran.created_date)
                inwardtran_data.set_comments(iwd_tran.comments)
                inwardtran_data.set_remarks(iwd_tran.remarks)
                inwardtrans.append(inwardtran_data)
            vpage = NWisefinPaginator(inwardtranlist, vys_page.get_index(), 10)
            inwardtrans.set_pagination(vpage)
        return inwardtrans

    def fetch_inward_details(self, details_id, emp_id, request):
        inwarddetails = InwardDetails.objects.using(self._current_app_schema()).get(id=details_id)
        header_data = DetailsResponse()
        apicall = ApiService(self._scope())
        header_data.set_id(inwarddetails.id)
        header_data.set_packetno(inwarddetails.packetno)
        doc_data = apicall.fetch_doctypedata(request, inwarddetails.doctype_id)
        header_data.set_doctype(doc_data)
        header_data.set_doccount(inwarddetails.doccount)
        header_data.set_remarks(inwarddetails.remarks)
        header_data.set_inwardheader_id(inwarddetails.inwardheader_id)
        header_data.set_docnumber(inwarddetails.docnumber)
        header_data.set_docsubject(inwarddetails.docsubject)
        header_data.set_pagecount(inwarddetails.pagecount)
        header_data.set_receivedfrom(inwarddetails.receivedfrom)
        header_data.set_docstatus(inwarddetails.docstatus)
        header_data.set_status(inwarddetails.status)
        header_data.assigndept_id = inwarddetails.assigndept_id
        header_data.assignemployee_id = inwarddetails.assignemployee_id
        header_data.actiontype = inwarddetails.actiontype
        header_data.set_tenor(inwarddetails.tenor)
        header_data.set_docaction(inwarddetails.docaction)
        header_data.set_rmucode(inwarddetails.rmucode)
        return header_data

    def inward_delete(self, inward_id, detail_id, packet_no, emp_id):
        logger.info("inward detail line item delete: " + str(detail_id))
        inwarddetails = InwardDetails.objects.using(self._current_app_schema()).get(
            id=detail_id, inwardheader_id=inward_id)
        if inwarddetails.doccount != 1:
            doccount = inwarddetails.doccount - 1
            inwarddetailss = InwardDetails.objects.using(self._current_app_schema()).filter(
                id=detail_id,inwardheader_id=inward_id,packetno=packet_no).update(
                                                                status=0,
                                                                doccount=doccount,
                                                                updated_by=emp_id,
                                                                updated_date=now())
            inwarddtl = InwardDetails.objects.using(self._current_app_schema()).filter(inwardheader_id=inward_id,
                                                                               packetno=packet_no,
                                                                               status=1
                                                                               ).update(doccount=doccount,
                                                                                        updated_by=emp_id,
                                                                                        updated_date=now()
                                                                                        )

            inward_obj = InwardDetails.objects.using(self._current_app_schema()).get(id=detail_id)
            header_data = DetailsResponse()
            header_data.set_id(inward_obj.id)
            header_data.set_doccount(inward_obj.doccount)
            header_data.DELETE=True
            return header_data
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_INWARDHEADER_ID)
            error_obj.set_description(ErrorDescription.INVALID_INWARDHEADER_ID)
            return error_obj

    # condition = Q(assignemployee_id=emp_id) & Q(status=1) & Q(docstatus=1) & ~Q(docnumber="")
    # if 'awb_no' in inward_obj:
    #     condition &= Q(inwardheader_id__awbno__icontains=inward_obj['awb_no'])
    # if 'fromdate' in inward_obj:
    #     condition &= Q(inwardheader_id__date__range=(inward_obj['fromdate'], inward_obj['todate']))
    # if 'channel_id' in inward_obj:
    #     condition &= Q(inwardheader_id__channel_id=inward_obj['channel_id'])
    # if 'courier_id' in inward_obj:
    #     condition &= Q(inwardheader_id__courier_id=inward_obj['courier_id'])
    # if 'docaction' in inward_obj:
    #     condition &= Q(docaction=inward_obj['docaction'])
    #
    # # if 'assignemployee_id' in inward_obj:
    # #     if inward_obj['assignemployee_id'] != 0:
    # #         condition &= ~Q(assignemployee_id=emp_id)
    # #         condition &= ~Q(assignemployee_id=None)
    # #     elif inward_obj['assignedto'] != inward_doc_status.ALL_Type:
    # #         condition &= Q(assignemployee_id=None) | ~Q(assignemployee_id=None)
    # #     else:
    # #         condition &= Q(assignemployee_id=None)
    # #
    # if 'assignedto' in inward_obj:
    #     if inward_obj['assignedto'] != inward_doc_status.ASSIGNED_Type:
    #         condition &= ~Q(assignemployee_id=None)
    #     elif inward_obj['assignedto'] != inward_doc_status.ALL_Type:
    #         condition &= Q(assignemployee_id=None) | ~Q(assignemployee_id=None)
    #     else:
    #         condition &= Q(assignemployee_id=None)
    # if 'docstatus' in inward_obj:
    #     condition &= Q(docstatus=inward_obj['docstatus'])
    # if 'doctype_id' in inward_obj:
    #     condition &= Q(doctype_id=inward_obj['doctype_id'])
    # if 'branch_id' in inward_obj:
    #     condition &= Q(inwardheader_id__branch_id=inward_obj['branch_id'])

    def inwardfile(self, detail_id, document_json, emp_id):
        print(detail_id, document_json)
        for doc_json in document_json:
            inwardfiles=InwardFiles.objects.using(self._current_app_schema()).create(
                    inwarddetails_id=detail_id,
                    file_id=doc_json['id'],
                    # file_name=doc_json['file_name'],
                    created_by=emp_id,
                    created_date=now())


    def inwarddetails_file(self, request, doc_module, detail_id, emp_id):
        try:
            inwarddetails = InwardDetails.objects.using(self._current_app_schema()).get(id=detail_id, status=1)
            details_data = DetailsResponse()
            details_data.set_id(inwarddetails.id)
            inwfile = InwardFiles.objects.using(self._current_app_schema()).filter(
                                                inwarddetails_id=inwarddetails.id, status=1)
            date_lenth = len(inwfile)
            file_list = list()
            if date_lenth > 0:
                api_serv = ApiService(self._scope())
                for doc in inwfile:
                    file_data = InwardFileResponse()
                    file_data.set_id(doc.id)
                    file_data.set_file_id(doc.file_id)
                    file_id = str(doc.file_id)
                    file_id = int(file_id[5:])
                    print("ff", file_id)
                    resp_obj = api_serv.file_get(request, doc_module, file_id)
                    print("r", resp_obj)
                    # print("r", resp_obj.get())
                    file_data.filedata=resp_obj
                    file_data.set_inwarddetails(doc.inwarddetails_id)
                    file_data.set_commentdoc(doc.commentdoc_id)
                    file_list.append(file_data)
            details_data.set_file_data(file_list)
            return details_data
        except InwardDetails.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_INWARDHEADER_ID)
            error_obj.set_description(ErrorDescription.INVALID_INWARDHEADER_ID)
            return error_obj

    def inwarddetails_doc_file(self, request, doc_module, detail_id, comment_id, emp_id):
        try:
            commentdoc = CommentDoc.objects.using(self._current_app_schema()).get(id=comment_id,
                                                                             inwarddetails_id=detail_id, status=1)
            details_data = DetailsResponse()
            details_data.set_id(commentdoc.id)
            inwfile = InwardFiles.objects.using(self._current_app_schema()).filter(
                                                commentdoc_id=commentdoc.id, status=1)
            date_lenth = len(inwfile)
            file_list = list()
            if date_lenth > 0:
                api_serv = ApiService(self._scope())
                for doc in inwfile:
                    file_data = InwardFileResponse()
                    file_data.set_id(doc.id)
                    file_data.set_file_id(doc.file_id)
                    file_id = str(doc.file_id)
                    print("ff1", file_id)
                    file_id = int(file_id[5:])
                    print("ff2", file_id)
                    resp_obj = api_serv.file_get(request, doc_module, file_id)
                    print("r", resp_obj)
                    # print("r", resp_obj.get())
                    file_data.filedata=resp_obj
                    file_data.set_inwarddetails(doc.inwarddetails_id)
                    file_data.set_commentdoc(doc.commentdoc_id)
                    file_list.append(file_data)
            details_data.set_file_data(file_list)
            return details_data
        except InwardDetails.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_INWARDHEADER_ID)
            error_obj.set_description(ErrorDescription.INVALID_INWARDHEADER_ID)
            return error_obj


    # Get Inward No using inwarddtls id For AP
    def get_inward_no_using_inwaddtls_id(self,request,inwarddtl_id):
        try:
            inwarddetails = InwardDetails.objects.using(self._current_app_schema()).get(id=inwarddtl_id,status=1)
            inwhdr = self.fetch_inward(request, inwarddetails.inwardheader_id)
            return inwhdr
        except Exception as excep:
            import traceback
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

