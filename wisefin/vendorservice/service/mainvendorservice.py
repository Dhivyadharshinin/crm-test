import json
from django.http import HttpResponse, JsonResponse
from nwisefin import settings
from nwisefin.settings import logger
from vendorservice.service.vendorservice import VendorService
from vendorservice.service.vendoraddressservice import VendorAddressService
from vendorservice.service.branchservice import branchservice
from vendorservice.service.productservice import productservice
from vendorservice.service.documentservice import DocumentService
from vendorservice.service.suppliertaxservice import TaxService
from vendorservice.service.paymentservice import paymentservice
from vendorservice.service.activityservice import ActivityService
from vendorservice.service.activitydetailsservice import ActivityDetailsService
from vendorservice.service.catelogservice import CatelogService
from vendorservice.service.venodrcontactservice import VendorContactService
from vendorservice.service.profileservice import ProfileService
from vendorservice.service.directorservice import DirectorService
from vendorservice.service.riskservice import RiskService
from vendorservice.service.kyc_service import KYCService
from vendorservice.service.questionnaireservice import QuestionnaireService
from vendorservice.service.clientservice import ContractorService, ClientService
from userservice.service.employeeservice import EmployeeService
from vendorservice.util.vendorutil import VendorRefType, Validation_vendor_doc
from userservice.models import Employee
from vendorservice.util import vendorutil
from vendorservice.service.vendoraccessorservice import VendorAccessorService
from vendorservice.models import Vendor, VendorDocument
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from vendorservice.util.vendorutil import Questionnaire
from masterservice.models.mastermodels import CustomerCategory, DocumentGroup
from vendorservice.service.vendor_mail import VendorEmail
val_url = settings.VYSFIN_URL


class MainVendorService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def status_update(self, request, vendor_id, user_id):
        vendor_service = VendorService(self._scope())
        vendor_rmidobj = Vendor.objects.using(self._current_app_schema()).get(id=vendor_id, entity_id=self._entity_id())
        vendor_rmid = vendor_rmidobj.rm_id
        vendor_statusid = vendor_rmidobj.vendor_status
        emp = Employee.objects.get(id=user_id)
        employee_id = emp.id
        branch_service = branchservice(self._scope())
        mod_status = vendor_service.get_modification_status(vendor_id)
        if mod_status:
            branch_count = branch_service.get_branch_modification_count(vendor_id)
        else:
            branch_count = branch_service.get_branch_count(vendor_id)
        if branch_count == False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_branch_ID)
            error_obj.set_description(ErrorDescription.INVALID_branch_ID)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response
        #
        # if vendor_statusid == 1:
        #     cust_cat_validation = self.ven_catagory_validation(vendor_rmidobj)
        #     if cust_cat_validation == False:
        #         error_obj = NWisefinError()
        #         error_obj.set_code(ErrorMessage.INVALID_DATA)
        #         error_obj.set_description('Invalid document')
        #         response = HttpResponse(error_obj.get(), content_type="application/json")
        #         return HttpResponse(response, content_type='application/json')

        if vendor_statusid == 2:
            if vendor_rmid != employee_id:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_RM_ID)
                error_obj.set_description(ErrorDescription.INVALID_RM_ID)
                response = HttpResponse(error_obj.get(), content_type="application/json")
                return response

        if vendor_statusid == 3:
            ischecker_obj = vendor_service.ischecker(request)

            if vendor_rmidobj.created_by == employee_id:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CHECKER_ID)
                error_obj.set_description(ErrorDescription.INVALID_MAKER_CHECKER_ID)
                response = HttpResponse(error_obj.get(), content_type="application/json")
                return response

            if vendor_rmid == employee_id:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CHECKER_ID)
                error_obj.set_description(ErrorDescription.INVALID_CHECKER_RM_ID)
                response = HttpResponse(error_obj.get(), content_type="application/json")
                return response

            if ischecker_obj == False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CHECKER_ID)
                error_obj.set_description(ErrorDescription.INVALID_CHECKER_ID)
                response = HttpResponse(error_obj.get(), content_type="application/json")
                return response

        if vendor_statusid == 4:
            isheader_obj = vendor_service.isheader(request)
            valid_header = vendor_service.valid_checker(vendor_id, employee_id)
            logger.info(str(valid_header) + ' valid_header')

            if vendor_rmidobj.created_by == employee_id:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CHECKER_ID)
                error_obj.set_description(ErrorDescription.INVALID_MAKER_HEADER_ID)
                response = HttpResponse(error_obj.get(), content_type="application/json")
                return response

            if vendor_rmid == employee_id:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CHECKER_ID)
                error_obj.set_description(ErrorDescription.INVALID_HEADER_RM_ID)
                response = HttpResponse(error_obj.get(), content_type="application/json")
                return response

            if valid_header == False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_HEADER_ID)
                error_obj.set_description(ErrorDescription.INVALID_HEADER_CHECKER_ID)
                response = HttpResponse(error_obj.get(), content_type="application/json")
                return response

            if isheader_obj == False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_HEADER_ID)
                error_obj.set_description(ErrorDescription.INVALID_HEADER_CHECKER_ID)
                response = HttpResponse(error_obj.get(), content_type="application/json")
                return response
        if vendor_statusid == 8:
            iscompilance_obj = vendor_service.iscompliance(request)
            valid_header = vendor_service.valid_checker(vendor_id, employee_id)
            logger.info(str(valid_header)+ ' valid_post_rm')
            if iscompilance_obj == False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.COMPLIANCE)
                error_obj.set_description(ErrorDescription.COMPLIANCE)
                response = HttpResponse(error_obj.get(), content_type="application/json")
                return response
            if valid_header == False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.COMPLIANCE)
                error_obj.set_description(ErrorDescription.COMPLIANCE)
                response = HttpResponse(error_obj.get(), content_type="application/json")
                return response
        q_status = vendor_service.vendor_validate(vendor_id)
        if q_status.get_status() == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response

        # logger.info("Somthing")
        emp_service = EmployeeService(self._scope())
        employee_id = emp_service.get_empid_from_userid(user_id)
        vendor_resp = vendor_service.fetch_vendor(vendor_id, user_id)
        request_statusid = vendor_resp.requeststatus
        data = json.loads(request.body)

        # vendor_id = data['vendor_id']
        # logger.info(data, 'data testing')
        status = data['status']
        assign_to = data['assign_to']
        accessor_service = VendorAccessorService(self._scope())
        # for id in assign_to:
        accessor_service.update_accessor(vendor_id, employee_id)
        accessor_service.set_accessor(vendor_id, assign_to, status)
        resp_obj = vendor_service.status_update(vendor_id, employee_id, request_statusid, data)
        try:
            mail_service = VendorEmail(self._scope())
            mail_send = mail_service.vendor_mail(vendor_id)
        except:
            logger.info('Error on vendor mail sending')
        # if status == 5:
        #     try:
        #         resp_data = vendor_service.fetch_data(vendor_id)
        #         logger.info(resp_data)
        #         print("_____________________________")
        #         print(resp_data)
        #         if resp_data == 'product_mapping_norecords':
        #             transaction.set_rollback(True)
        #             error_obj = NWisefinError()
        #             error_obj.set_code(ErrorMessage.INVALID_NEW_PCODE)
        #             error_obj.set_description(ErrorMessage.INVALID_NEW_PCODE)
        #             return HttpResponse(error_obj.get(), content_type='application/json')
        #
        #         token = "Bearer  " + get_authtoken()
        #
        #         logger.info('atma_main_insert')
        #         logger.info(token)
        #         headers = {"content-type": "application/json", "Authorization": "" + token + ""}
        #         logger.info(headers)
        #         # datas = JsonResponse(resp_obj)
        #         datas = json.dumps(resp_data, indent=4)
        #         print(datas)
        #         logger.info(datas, status)
        #         logger.info("" + val_url + 'atma_main_insert?Group=New_Atma_Api_frm_Memo&Action=New_Atma_Api')
        #         resp = requests.post(
        #             "" + val_url + 'atma_main_insert?Group=New_Atma_Api_frm_Memo&Action=New_Atma_Api',
        #             data=datas,
        #             headers=headers,
        #             verify=False)
        #         logger.info(resp)
        #         results = resp.content.decode("utf-8")
        #         results = json.loads(results)
        #         logger.info(results)
        #         if results['MESSAGE'] == ['SUCCESS']:
        #             return HttpResponse(resp_obj.get(), content_type='application/json')
        #         else:
        #             transaction.set_rollback(True)
        #             error_obj = NWisefinError()
        #             error_obj.set_code(ErrorMessage.INVALID_NEW_TOOLD_ATMA)
        #             error_obj.set_description(results)
        #             response = HttpResponse(error_obj.get(), content_type="application/json")
        #             return HttpResponse(response, content_type='application/json')
        #     except Exception as e:
        #         transaction.set_rollback(True)
        #         error_obj = NWisefinError()
        #         error_obj.set_code(ErrorMessage.INVALID_NEW_TOOLD_ATMA)
        #         error_obj.set_description(e)
        #         response = HttpResponse(error_obj.get(), content_type="application/json")
        #         return HttpResponse(response, content_type='application/json')

        return HttpResponse(resp_obj.get(), content_type='application/json')

    def modification_reject(self, request, vendor_id):
        vendor_service = VendorService(self._scope())
        vendor_rmidobj = Vendor.objects.using(self._current_app_schema()).get(id=vendor_id, entity_id=self._entity_id())
        vendor_statusid = vendor_rmidobj.vendor_status
        user_id = request.user.id
        emp = Employee.objects.get(user_id=user_id)
        user_id = emp.id
        data = json.loads(request.body)
        if vendor_statusid == (4 or 1):
            isheader_obj = vendor_service.isheader(request)
            if isheader_obj == False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_HEADER_ID)
                error_obj.set_description(ErrorDescription.INVALID_HEADER_ID)
                response = HttpResponse(error_obj.get(), content_type="application/json")
                return HttpResponse(response, content_type='application/json')
        resp_obj1 = vendor_service.modification_serviceview(vendor_id)
        x = resp_obj1.data
        # user_id = request.user.id
        for i in x:
            mod_status = i.mod_status
            old_id = i.ref_id
            new_id = i.modify_ref_id
            mod_type = i.ref_type
            if mod_type == VendorRefType.VENDOR:
                resp_obj = vendor_service.modification_reject_vendor(mod_status, old_id, new_id, user_id)
            if mod_type == VendorRefType.VENDOR_ADDRESS:
                address_service = VendorAddressService(self._scope())
                resp_obj = address_service.modification_reject_vendoraddress(mod_status, old_id, new_id, user_id,
                                                                             vendor_id)
            if mod_type == VendorRefType.VENDOR_CONTACT:
                contact_service = VendorContactService(self._scope())
                resp_obj = contact_service.modification_reject_vendorcontact(mod_status, old_id, new_id, user_id,
                                                                             vendor_id)
            if mod_type == VendorRefType.VENDOR_PROFILE:
                profile_service = ProfileService(self._scope())
                resp_obj = profile_service.modification_reject_vendorprofile(mod_status, old_id, new_id, user_id,
                                                                             vendor_id)
            if mod_type == VendorRefType.VENDOR_DIRECTOR:
                director_service = DirectorService(self._scope())
                resp_obj = director_service.modification_reject_vendordirector(mod_status, old_id, new_id, user_id)
            if mod_type == VendorRefType.VENDOR_BRANCH:
                branch_service = branchservice(self._scope())
                resp_obj = branch_service.modification_reject_branch(mod_status, old_id, new_id, vendor_id, user_id)
            if mod_type == VendorRefType.VENDOR_CONTRACT:
                contract_service = ContractorService(self._scope())
                resp_obj = contract_service.modification_reject_contractor(mod_status, old_id, new_id, vendor_id,
                                                                           user_id)
            if mod_type == VendorRefType.VENDOR_CLIENT:
                client_service = ClientService(self._scope())
                resp_obj = client_service.modification_reject_client(mod_status, old_id, new_id, vendor_id, user_id)
            if mod_type == VendorRefType.VENDOR_PRODUCT:
                product_service = productservice(self._scope())
                resp_obj = product_service.modification_reject_product(mod_status, old_id, new_id, vendor_id, user_id)
            if mod_type == VendorRefType.VENDOR_DOCUMENT:
                document_service = DocumentService(self._scope())
                resp_obj = document_service.modification_reject_document(mod_status, old_id, new_id, vendor_id, user_id)
            if mod_type == VendorRefType.VENDOR_SUPPLIERTAX:
                suppliertax_service = TaxService(self._scope())
                resp_obj = suppliertax_service.modification_reject_suppliertax(mod_status, old_id, new_id, vendor_id,
                                                                               user_id)
            if mod_type == VendorRefType.VENDOR_PAYMENT:
                payment_service = paymentservice(self._scope())
                resp_obj = payment_service.modification_reject_payment(mod_status, old_id, new_id, vendor_id, user_id)
            if mod_type == VendorRefType.VENDOR_ACTIVITY:
                activity_service = ActivityService(self._scope())
                resp_obj = activity_service.modification_reject_activity(mod_status, old_id, new_id, vendor_id, user_id)
            if mod_type == VendorRefType.VENDOR_ACTIVITYDETAIL:
                activitydtl_service = ActivityDetailsService(self._scope())
                resp_obj = activitydtl_service.modification_reject_activitydetail(mod_status, old_id, new_id, vendor_id,
                                                                                  user_id)
            if mod_type == VendorRefType.VENDOR_CATELOG:
                catelog_service = CatelogService(self._scope())
                resp_obj = catelog_service.modification_reject_catelog(mod_status, old_id, new_id, vendor_id, user_id)
            if mod_type == VendorRefType.VENDOR_RISK:
                risk_service = RiskService(self._scope())
                resp_obj = risk_service.modification_reject_risk(mod_status, old_id, new_id, vendor_id, user_id)
            if mod_type == VendorRefType.VENDOR_KYC:
                kyc_service = KYCService(self._scope())
                resp_obj = kyc_service.modification_reject_vendorkyc(mod_status, old_id, new_id, vendor_id, user_id)
            if mod_type == VendorRefType.BCP_QUESION:
                bcp_service = QuestionnaireService(self._scope())
                resp_obj = bcp_service.modification_reject_bcp(vendor_id, Questionnaire.BCP_QUESTIONNAIRE)
            if mod_type == VendorRefType.DUE_DELIGENCE:
                due_service = QuestionnaireService(self._scope())
                resp_obj = due_service.modification_reject_due(vendor_id, Questionnaire.DUE_DILIGENCE)


        resp_obj = vendor_service.modification_reject_status(vendor_id, user_id, data)
        return HttpResponse(resp_obj.get(), content_type='application/json')

    # def ven_catagory_validation(self, vendor_rmidobj):
    #     validation = False
    #     vendor_id = vendor_rmidobj.id
    #     vendor_custcat = vendor_rmidobj.custcategory_id
    #     custcat_obj = CustomerCategory.objects.using(self._app_schema(ApplicationNamespace.MASTER_SERVICE)).filter(
    #         id=vendor_custcat)
    #     custcat_name = custcat_obj[0].name
    #     ven_doc = VendorDocument.objects.using(self._current_app_schema()).filter(partner_id=vendor_id).values_list(
    #         'docgroup_id', flat=True)
    #     ven_doc = list(ven_doc)
    #     doc_group = DocumentGroup.objects.using(self._app_schema(ApplicationNamespace.MASTER_SERVICE)).filter(
    #         id__in=ven_doc).values_list('name', flat=True)
    #     doc_group = list(doc_group)
    #     if custcat_name == Validation_vendor_doc.OUTSOURCING:
    #         if set(Validation_vendor_doc.outsourcing_values).issubset(doc_group):
    #             validation = True
    #             return validation
    #     elif custcat_name == Validation_vendor_doc.THIRD_PARTY_INTERMEDIARY:
    #         if set(Validation_vendor_doc.Third_party_intermediary_values).issubset(doc_group):
    #             validation = True
    #             return validation
    #     else:
    #         validation = True
    #         return validation
    #
    #     return validation
