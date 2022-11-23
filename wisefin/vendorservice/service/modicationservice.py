import json
from django.http import HttpResponse, JsonResponse
import requests
from userservice.controller.authcontroller import get_authtoken
from nwisefin import settings
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinlist import NWisefinList
from masterservice.service.bankservice import BankService
from masterservice.service.bankbranchservice import BankBranchService
from masterservice.service.paymodeservice import PaymodeService
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
from vendorservice.service.clientservice import ContractorService, ClientService
from vendorservice.data.response.modificationdataresponse import ModificationDataResponse
from vendorservice.service.supplierservice import AddressService, ContactService
from vendorservice.service.riskservice import RiskService
from vendorservice.service.questionnaireservice import QuestionnaireService
from masterservice.service.taxservice import TaxMasterService
from masterservice.service.subtaxservice import SubTaxService
from masterservice.service.taxrateservice import TaxRateService
from masterservice.service.docugroupservice import DocumentGroupService
from masterservice.service.cityservice import CityService
from masterservice.service.stateservice import StateService
from masterservice.service.districtservice import DistrictService
from masterservice.service.pincodeservice import PincodeService
# from masterservice.service.designationservice import DesignationService
from masterservice.service.contacttypeservice import ContactTypeService
from masterservice.service.customercategoryservice import CustomerCategoryService
from masterservice.service.apsubcategoryservice import SubcategoryService
from masterservice.service.apcategoryservice import CategoryService
from masterservice.service.uomservice import UomService
from masterservice.service.productservice import ProductService
from vendorservice.util.vendorutil import getType, getGroup, getOrgType, getClassification, getComposite, get_risk_type
from userservice.service.employeeservice import EmployeeService
from vendorservice.util.vendorutil import getVendorStatus, getVendorActiveStatus, getVendorMainStatus, \
    getVendorRequestStatus, VendorRefType, ModifyStatus,getroleStatus,Validation_vendor_doc
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from django.db import transaction
from vendorservice.models import Vendor, VendorDirector, VendorImage,SupplierBranch,VendorSubContractor,VendorClient,VendorDocument,SupplierProduct,SupplierTax,SupplierPayment,SupplierActivity,ActivityDetail,Catelog,SupplierSubTax, VendorRiskInfo, VendorKYC
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from vendorservice.service.kyc_service import KYCService
from vendorservice.service.vendor_mail import VendorEmail
from vendorservice.util import vendorutil
val_url = settings.VYSFIN_URL


class ModicationService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def modication_view(self, user_id, vendor_id):
        vendor_service = VendorService(self._scope())
        logger.info('DEBUG_VENDOR_ID' + '=' + str(vendor_id))
        resp_obj = vendor_service.modification_serviceview(vendor_id)
        # user_id = request.user.id
        x = resp_obj.data
        vlist = NWisefinList()
        # create_code = ModifyStatus.create
        # delete_code = ModifyStatus.delete
        bcp_flag = False
        due_flag = False
        for i in x:
            mod_status = i.mod_status
            if mod_status == ModifyStatus.active_in:

                if i.ref_type == VendorRefType.VENDOR_BRANCH:
                    branch_id = i.modify_ref_id
                    branch_ref_id = i.ref_id
                    branch_service = branchservice(self._scope())
                    contact_service = ContactService(self._scope())
                    address_service = AddressService(self._scope())
                    state_service = StateService(self._scope())
                    city_service = CityService(self._scope())
                    district_service = DistrictService(self._scope())
                    pincode_service = PincodeService(self._scope())
                    contacttype_service = ContactTypeService(self._scope())
                    # designation_service = DesignationService(self._scope())

                    branch_old_resp = branch_service.fetch_branch(branch_ref_id)
                    # contact
                    cont_id = branch_old_resp.contact_id
                    contact = contact_service.fetch_contact(cont_id, user_id)
                    branch_old_resp.contact_id = contact
                    # address
                    add_id = branch_old_resp.address_id
                    address = address_service.fetch_address(add_id, user_id)
                    branch_old_resp.address_id = address
                    city_id = branch_old_resp.address_id.city_id
                    city = city_service.fetch_city(city_id, user_id)
                    branch_old_resp.address_id.city_id = city
                    state_id = branch_old_resp.address_id.state_id
                    state = state_service.fetchstate(state_id)
                    branch_old_resp.address_id.state_id = state
                    district_id = branch_old_resp.address_id.district_id
                    district = district_service.fetchdistrict(district_id)
                    branch_old_resp.address_id.district_id = district
                    pincode_id = branch_old_resp.address_id.pincode_id
                    pincode = pincode_service.fetch_pincode(pincode_id, user_id)
                    branch_old_resp.address_id.pincode_id = pincode
                    # contact

                    # designation_id = branch_old_resp.contact_id.designation_id
                    # designation = designation_service.fetch_designation(designation_id)
                    # branch_old_resp.contact_id.designation_id = designation
                    # new data
                    branch_new_resp = branch_service.fetch_branch(branch_id)
                    # contact
                    cont_id = branch_new_resp.contact_id
                    contact = contact_service.fetch_contact(cont_id, user_id)
                    branch_new_resp.contact_id = contact
                    # address
                    add_id = branch_new_resp.address_id
                    address = address_service.fetch_address(add_id, user_id)
                    branch_new_resp.address_id = address
                    city_id = branch_new_resp.address_id.city_id
                    city = city_service.fetch_city(city_id, user_id)
                    branch_new_resp.address_id.city_id = city
                    state_id = branch_new_resp.address_id.state_id
                    state = state_service.fetchstate(state_id)
                    branch_new_resp.address_id.state_id = state
                    district_id = branch_new_resp.address_id.district_id
                    district = district_service.fetchdistrict(district_id)
                    branch_new_resp.address_id.district_id = district
                    pincode_id = branch_new_resp.address_id.pincode_id
                    pincode = pincode_service.fetch_pincode(pincode_id, user_id)
                    branch_new_resp.address_id.pincode_id = pincode
                    # contact

                    # designation_id = branch_new_resp.contact_id.designation_id
                    # designation = designation_service.fetch_designation(designation_id)
                    # branch_new_resp.contact_id.designation_id = designation

                    branch_response = ModificationDataResponse()
                    branch_response.set_action(mod_status)
                    branch_response.set_type_name(i.ref_type)
                    branch_response.set_old_data(branch_old_resp)
                    branch_response.set_new_data(branch_new_resp)
                    vlist.append(branch_response)

                if i.ref_type == VendorRefType.VENDOR_PAYMENT:
                    payment_id = i.modify_ref_id
                    payment_ref_id = i.ref_id
                    payment_service = paymentservice(self._scope())
                    bank_service = BankService(self._scope())
                    paymode_service = PaymodeService(self._scope())
                    bankbranch_service = BankBranchService(self._scope())
                    branch_service = branchservice(self._scope())
                    # new data
                    new_payment_resp = payment_service.fetch_payment(payment_id)
                    bank_id = new_payment_resp.bank_id
                    bank = bank_service.fetch_bank(bank_id, user_id)
                    new_payment_resp.bank_id = bank

                    branch_id = new_payment_resp.branch_id
                    branch = bankbranch_service.fetch_bankbranch(branch_id, user_id)
                    new_payment_resp.branch_id = branch

                    paymode_id = new_payment_resp.paymode_id
                    paymode = paymode_service.fetchpaymode(paymode_id)
                    new_payment_resp.paymode_id = paymode

                    supplierbranch_id = new_payment_resp.supplierbranch_id
                    supplierbranch = branch_service.fetch_branch(supplierbranch_id)
                    new_payment_resp.supplierbranch_id = supplierbranch

                    # old data
                    old_payment_resp = payment_service.fetch_payment(payment_ref_id)
                    bank_id = old_payment_resp.bank_id
                    bank = bank_service.fetch_bank(bank_id, user_id)
                    old_payment_resp.bank_id = bank

                    branch_id = old_payment_resp.branch_id
                    branch = bankbranch_service.fetch_bankbranch(branch_id, user_id)
                    old_payment_resp.branch_id = branch

                    paymode_id = old_payment_resp.paymode_id
                    paymode = paymode_service.fetchpaymode(paymode_id)
                    old_payment_resp.paymode_id = paymode

                    supplierbranch_id = old_payment_resp.supplierbranch_id
                    supplierbranch = branch_service.fetch_branch(supplierbranch_id)
                    old_payment_resp.supplierbranch_id = supplierbranch

                    payment_response = ModificationDataResponse()
                    payment_response.set_action(mod_status)
                    payment_response.set_type_name(i.ref_type)
                    payment_response.set_new_data(new_payment_resp)
                    payment_response.set_old_data(old_payment_resp)
                    vlist.append(payment_response)
            if mod_status in (ModifyStatus.create, ModifyStatus.delete):
                if i.ref_type == VendorRefType.VENDOR_CONTRACT:
                    contract_id = i.modify_ref_id
                    contract_service = ContractorService(self._scope())
                    con_resp = contract_service.fetch_contractor(contract_id, user_id, vendor_id)
                    contract_response = ModificationDataResponse()
                    contract_response.set_action(mod_status)
                    contract_response.set_type_name(i.ref_type)
                    contract_response.set_data(con_resp)
                    vlist.append(contract_response)
                if i.ref_type == VendorRefType.VENDOR_BRANCH:
                    branch_id = i.modify_ref_id
                    branch_service = branchservice(self._scope())
                    contact_service = ContactService(self._scope())
                    address_service = AddressService(self._scope())
                    state_service = StateService(self._scope())
                    city_service = CityService(self._scope())
                    district_service = DistrictService(self._scope())
                    pincode_service = PincodeService(self._scope())
                    contacttype_service = ContactTypeService(self._scope())
                    # designation_service = DesignationService(self._scope())

                    branch_resp = branch_service.fetch_branch(branch_id)
                    # contact
                    cont_id = branch_resp.contact_id
                    contact = contact_service.fetch_contact(cont_id, user_id)
                    branch_resp.contact_id = contact
                    # address
                    add_id = branch_resp.address_id
                    address = address_service.fetch_address(add_id, user_id)
                    branch_resp.address_id = address
                    city_id = branch_resp.address_id.city_id
                    city = city_service.fetch_city(city_id, user_id)
                    branch_resp.address_id.city_id = city
                    state_id = branch_resp.address_id.state_id
                    state = state_service.fetchstate(state_id)
                    branch_resp.address_id.state_id = state
                    district_id = branch_resp.address_id.district_id
                    district = district_service.fetchdistrict(district_id)
                    branch_resp.address_id.district_id = district
                    pincode_id = branch_resp.address_id.pincode_id
                    pincode = pincode_service.fetch_pincode(pincode_id, user_id)
                    branch_resp.address_id.pincode_id = pincode
                    # contact

                    # designation_id = branch_resp.contact_id.designation_id
                    # designation = designation_service.fetch_designation(designation_id)
                    # branch_resp.contact_id.designation_id = designation

                    branch_response = ModificationDataResponse()
                    branch_response.set_action(mod_status)
                    branch_response.set_type_name(i.ref_type)
                    branch_response.set_data(branch_resp)
                    vlist.append(branch_response)
                if i.ref_type == VendorRefType.VENDOR_CLIENT:
                    client_id = i.modify_ref_id
                    client_service = ClientService(self._scope())
                    address_service = AddressService(self._scope())
                    city_service = CityService(self._scope())
                    district_service = DistrictService(self._scope())
                    state_service = StateService(self._scope())
                    pincode_service = PincodeService(self._scope())
                    client_resp = client_service.fetch_client(client_id)
                    # logger.info(client_resp)
                    address_id = client_resp.address_id
                    address_resp = address_service.fetch_address(address_id, user_id)
                    client_resp.address_id = address_resp
                    # #city
                    city_id = client_resp.address_id.city_id
                    city_resp = city_service.fetch_city(city_id, user_id)
                    client_resp.address_id.city_id = city_resp
                    # pincode
                    pincode_id = client_resp.address_id.pincode_id
                    pincode_resp = pincode_service.fetch_pincode(pincode_id, user_id)
                    client_resp.address_id.pincode_id = pincode_resp
                    # #district
                    district_id = client_resp.address_id.district_id
                    district_resp = district_service.fetchdistrict(district_id)
                    client_resp.address_id.district_id = district_resp
                    # #state
                    state_id = client_resp.address_id.state_id
                    state_resp = state_service.fetchstate(state_id)
                    client_resp.address_id.state_id = state_resp
                    client_response = ModificationDataResponse()
                    client_response.set_action(mod_status)
                    client_response.set_type_name(i.ref_type)
                    client_response.set_data(client_resp)
                    vlist.append(client_response)
                if i.ref_type == VendorRefType.VENDOR_PRODUCT:
                    product_id = i.modify_ref_id
                    product_service = productservice(self._scope())
                    contact_service = ContactService(self._scope())
                    contacttype_service = ContactTypeService(self._scope())
                    # designation_service = DesignationService(self._scope())
                    product_resp = product_service.fetch_product(product_id, vendor_id)
                    # contact1
                    con_client_id1 = product_resp.client1_id
                    contact_resp1 = contact_service.fetch_contact(con_client_id1, user_id)
                    product_resp.client1_id = contact_resp1
                    # contacttype

                    # designation
                    # designation_id = product_resp.client1_id.designation_id
                    # designation_resp = designation_service.fetch_designation(designation_id)
                    # product_resp.client1_id.designation_id = designation_resp

                    # contact 2
                    con_client_id2 = product_resp.client2_id
                    contact_resp2 = contact_service.fetch_contact(con_client_id2, user_id)
                    product_resp.client2_id = contact_resp2
                    # contacttype

                    # designation
                    # designation_id = product_resp.client2_id.designation_id
                    # designation_resp = designation_service.fetch_designation(designation_id)
                    # product_resp.client2_id.designation_id = designation_resp

                    # contact 3
                    con_customer_id1 = product_resp.customer1_id
                    contact_resp3 = contact_service.fetch_contact(con_customer_id1, user_id)
                    product_resp.customer1_id = contact_resp3
                    # contacttype

                    # designation
                    # designation_id = product_resp.customer1_id.designation_id
                    # designation_resp = designation_service.fetch_designation(designation_id)
                    # product_resp.customer1_id.designation_id = designation_resp

                    # contact 4
                    con_customer_id2 = product_resp.customer2_id
                    contact_resp4 = contact_service.fetch_contact(con_customer_id2, user_id)
                    product_resp.customer2_id = contact_resp4
                    # contacttype

                    # designation
                    # designation_id = product_resp.customer2_id.designation_id
                    # designation_resp = designation_service.fetch_designation(designation_id)
                    # product_resp.customer2_id.designation_id = designation_resp

                    product_response = ModificationDataResponse()
                    product_response.set_action(mod_status)
                    product_response.set_type_name(i.ref_type)
                    product_response.set_data(product_resp)
                    vlist.append(product_response)
                if i.ref_type == VendorRefType.VENDOR_DOCUMENT:
                    document_id = i.modify_ref_id
                    document_service = DocumentService(self._scope())
                    document_resp = document_service.fetch_document(document_id)
                    tab_type = VendorRefType.VENDOR_DOCUMENT
                    data_obj = document_service.vendor_file_data(document_id, tab_type)
                    document_resp.file_id = data_obj.data
                    docu_service = DocumentGroupService(self._scope())
                    docgroup_id = document_resp.docgroup_id
                    docugroup = docu_service.fetch_docugroup(docgroup_id)
                    document_resp.docgroup_id = docugroup

                    document_response = ModificationDataResponse()
                    document_response.set_action(mod_status)
                    document_response.set_type_name(i.ref_type)
                    document_response.set_data(document_resp)
                    vlist.append(document_response)
                if i.ref_type == VendorRefType.VENDOR_SUPPLIERTAX:
                    suppliertax_id = i.modify_ref_id
                    tax_service = TaxService(self._scope())
                    branch_service = branchservice(self._scope())
                    document_service = DocumentService(self._scope())
                    taxmaster_service = TaxMasterService(self._scope())
                    subtax_service = SubTaxService(self._scope())
                    taxrate_service = TaxRateService(self._scope())
                    suppliertax_resp = tax_service.fetch_suppliertax(suppliertax_id)
                    suppliertax_response = ModificationDataResponse()
                    tab_type = VendorRefType.VENDOR_SUPPLIERTAX
                    data_obj = document_service.vendor_file_data(suppliertax_id, tab_type)
                    suppliertax_resp.attachment = data_obj.data

                    tax1_id = suppliertax_resp.tax
                    tax = taxmaster_service.fetch_tax(tax1_id, user_id)
                    suppliertax_resp.tax = tax
                    subtax_id = suppliertax_resp.subtax
                    subtax = subtax_service.fetch_subtax(subtax_id, user_id)
                    suppliertax_resp.subtax = subtax
                    if suppliertax_resp.taxrate == 0:
                        suppliertax_resp.taxrate = None
                    else:
                        taxrate_id = suppliertax_resp.taxrate
                        taxrate = taxrate_service.fetch_taxrate(taxrate_id, user_id)
                        suppliertax_resp.taxrate = taxrate

                    supplierbranch_id = suppliertax_resp.branch_id
                    supplierbranch = branch_service.fetch_branch(supplierbranch_id)
                    suppliertax_resp.branch_id = supplierbranch
                    suppliertax_response.set_action(mod_status)
                    suppliertax_response.set_type_name(i.ref_type)
                    suppliertax_response.set_data(suppliertax_resp)
                    vlist.append(suppliertax_response)
                if i.ref_type == VendorRefType.VENDOR_PAYMENT:
                    payment_id = i.modify_ref_id
                    payment_service = paymentservice(self._scope())
                    bank_service = BankService(self._scope())
                    paymode_service = PaymodeService(self._scope())
                    bankbranch_service = BankBranchService(self._scope())
                    branch_service = branchservice(self._scope())
                    payment_resp = payment_service.fetch_payment(payment_id)
                    bank_id = payment_resp.bank_id
                    bank = bank_service.fetch_bank(bank_id, user_id)
                    payment_resp.bank_id = bank

                    branch_id = payment_resp.branch_id
                    branch = bankbranch_service.fetch_bankbranch(branch_id, user_id)
                    payment_resp.branch_id = branch

                    paymode_id = payment_resp.paymode_id
                    paymode = paymode_service.fetchpaymode(paymode_id)
                    payment_resp.paymode_id = paymode

                    supplierbranch_id = payment_resp.supplierbranch_id
                    supplierbranch = branch_service.fetch_branch(supplierbranch_id)
                    payment_resp.supplierbranch_id = supplierbranch

                    payment_response = ModificationDataResponse()
                    payment_response.set_action(mod_status)
                    payment_response.set_type_name(i.ref_type)
                    payment_response.set_data(payment_resp)
                    vlist.append(payment_response)
                if i.ref_type == VendorRefType.VENDOR_ACTIVITY:
                    activity_id = i.modify_ref_id
                    activity_service = ActivityService(self._scope())
                    contact_service = ContactService(self._scope())
                    activity_resp = activity_service.fetch_activity(activity_id)
                    contact_id = activity_resp.contact_id
                    contact_resp = contact_service.fetch_contact(contact_id, user_id)
                    activity_resp.contact_id = contact_resp
                    activity_response = ModificationDataResponse()
                    activity_response.set_action(mod_status)
                    activity_response.set_type_name(i.ref_type)
                    activity_response.set_data(activity_resp)
                    vlist.append(activity_response)
                if i.ref_type == VendorRefType.VENDOR_ACTIVITYDETAIL:
                    activitydtl_id = i.modify_ref_id
                    activitydtl_service = ActivityDetailsService(self._scope())
                    activitydtl_resp = activitydtl_service.fetch_activitydtl(activitydtl_id)
                    activity_service = ActivityService(self._scope())
                    activity_id = activitydtl_resp.activity_id
                    activity = activity_service.fetch_activity(activity_id)
                    activitydtl_resp.activity_id = activity

                    emp_service = EmployeeService(self._scope())
                    raisor_id = activitydtl_resp.raisor
                    raisor = emp_service.get_employee(raisor_id, user_id)
                    activitydtl_resp.raisor = raisor

                    approver_id = activitydtl_resp.approver
                    approver = emp_service.get_employee(approver_id, user_id)
                    activitydtl_resp.approver = approver
                    activitydtl_response = ModificationDataResponse()
                    activitydtl_response.set_action(mod_status)
                    activitydtl_response.set_type_name(i.ref_type)
                    activitydtl_response.set_data(activitydtl_resp)
                    vlist.append(activitydtl_response)
                if i.ref_type == VendorRefType.VENDOR_CATELOG:
                    catelog_id = i.modify_ref_id
                    catelog_service = CatelogService(self._scope())
                    subcategory_service = SubcategoryService(self._scope())
                    category_service = CategoryService(self._scope())
                    product_service = ProductService(self._scope())
                    activitydetail_service = ActivityDetailsService(self._scope())
                    uom_service = UomService(self._scope())
                    catelog_resp = catelog_service.fetch_catelog(catelog_id)
                    activitydetail_id = catelog_resp.activitydetail_id
                    activity = activitydetail_service.fetch_activitydtl(activitydetail_id)
                    catelog_resp.activitydetail_id = activity

                    category_id = catelog_resp.category
                    category = category_service.fetchcategory(category_id)
                    catelog_resp.category = category

                    uom_id = catelog_resp.uom
                    if uom_id is not None:
                        uom = uom_service.fetch_uom(uom_id, user_id)
                        catelog_resp.uom = uom

                    subcategory_id = catelog_resp.subcategory
                    subcategory = subcategory_service.fetchsubcategory(subcategory_id)
                    catelog_resp.subcategory = subcategory

                    product_id = catelog_resp.productname
                    product = product_service.fetch_product(product_id, user_id)
                    catelog_resp.productname = product
                    #
                    catelog_response = ModificationDataResponse()
                    catelog_response.set_action(mod_status)
                    catelog_response.set_type_name(i.ref_type)
                    catelog_response.set_data(catelog_resp)
                    vlist.append(catelog_response)
                if i.ref_type == VendorRefType.VENDOR_RISK:
                    risk_id = i.modify_ref_id
                    risk_service = RiskService(self._scope())
                    risk_resp = risk_service.fetch_risk(vendor_id, risk_id)
                    risk_response = ModificationDataResponse()
                    risk_response.set_action(mod_status)
                    risk_response.set_type_name(i.ref_type)
                    risk_response.set_data(risk_resp)
                    vlist.append(risk_response)
                if i.ref_type == VendorRefType.VENDOR_KYC:
                    kyc_id = i.modify_ref_id
                    kyc_service = KYCService(self._scope())
                    kyc_resp = kyc_service.fetch_kyc(kyc_id, user_id)
                    kyc_response = ModificationDataResponse()
                    kyc_response.set_action(mod_status)
                    kyc_response.set_type_name(i.ref_type)
                    kyc_response.set_data(kyc_resp)
                    vlist.append(kyc_response)
                if i.ref_type == VendorRefType.BCP_QUESION:
                    bcp_service = QuestionnaireService(self._scope())
                    old_bcp_resp = bcp_service.fetch_questionnaries_bcp(vendor_id, '1')
                    new_bcp_resp = bcp_service.bcp_question_list(vendor_id, '1')
                    bcp_response = ModificationDataResponse()
                    bcp_response.set_action(mod_status)
                    bcp_response.set_type_name(i.ref_type)
                    bcp_response.set_old_data(old_bcp_resp)
                    bcp_response.set_new_data(new_bcp_resp)
                    if bcp_flag == False:
                        vlist.append(bcp_response)
                        bcp_flag = True
                if i.ref_type == VendorRefType.DUE_DELIGENCE:
                    due_service = QuestionnaireService(self._scope())
                    old_due_resp = due_service.fetch_questionnaries_due(vendor_id, '2')
                    new_due_resp = due_service.due_question_list(vendor_id, '2')
                    due_response = ModificationDataResponse()
                    due_response.set_action(mod_status)
                    due_response.set_type_name(i.ref_type)
                    due_response.set_old_data(old_due_resp)
                    due_response.set_new_data(new_due_resp)
                    if due_flag == False:
                        vlist.append(due_response)
                        due_flag = True
            if mod_status == ModifyStatus.update:
                if i.ref_type == VendorRefType.VENDOR:
                    vendor_id = i.modify_ref_id
                    vendor_ref_id = i.ref_id
                    vendor_service = VendorService(self._scope())
                    address_service = VendorAddressService(self._scope())
                    contact_service = VendorContactService(self._scope())
                    director_service = DirectorService(self._scope())
                    profile_service = ProfileService(self._scope())
                    state_service = StateService(self._scope())
                    city_service = CityService(self._scope())
                    district_service = DistrictService(self._scope())
                    pincode_service = PincodeService(self._scope())
                    contacttype_service = ContactTypeService(self._scope())
                    # designation_service = DesignationService(self._scope())
                    customercategory_service = CustomerCategoryService(self._scope())

                    vendor_old_resp = vendor_service.fetch_vendor(vendor_ref_id, user_id)
                    # address
                    address = address_service.fetch_vendoraddress(vendor_ref_id, user_id)
                    vendor_old_resp.address = address
                    city_id = vendor_old_resp.address.city_id
                    city = city_service.fetch_city(city_id, user_id)
                    vendor_old_resp.address.city_id = city
                    state_id = vendor_old_resp.address.state_id
                    state = state_service.fetchstate(state_id)
                    vendor_old_resp.address.state_id = state
                    district_id = vendor_old_resp.address.district_id
                    district = district_service.fetchdistrict(district_id)
                    vendor_old_resp.address.district_id = district
                    pincode_id = vendor_old_resp.address.pincode_id
                    pincode = pincode_service.fetch_pincode(pincode_id, user_id)
                    vendor_old_resp.address.pincode_id = pincode
                    # contact
                    contact = contact_service.fetch_vendorcontact(vendor_ref_id, user_id)
                    vendor_old_resp.contact = contact

                    # designation_id = vendor_old_resp.contact.designation_id
                    # designation = designation_service.fetch_designation(designation_id)
                    # vendor_old_resp.contact.designation_id = designation
                    # profile
                    profile = profile_service.fetch_profile(vendor_ref_id, user_id)
                    vendor_old_resp.profile = profile
                    director = director_service.fetch_director(vendor_ref_id, user_id)
                    vendor_old_resp.director = director
                    # orgtype
                    orgtype_id = vendor_old_resp.orgtype
                    orgtype = getOrgType(orgtype_id)
                    vendor_old_resp.orgtype = orgtype

                    # classification
                    classification_id = vendor_old_resp.classification
                    classification = getClassification(classification_id)
                    vendor_old_resp.classification = classification

                    # group
                    group_id = vendor_old_resp.group
                    group = getGroup(group_id)
                    vendor_old_resp.group = group

                    # composite
                    composite_id = vendor_old_resp.composite
                    composite = getComposite(composite_id)
                    vendor_old_resp.composite = composite

                    # type
                    type_id = vendor_old_resp.type
                    type = getType(type_id)
                    vendor_old_resp.type = type

                    # rmname
                    employee_service = EmployeeService(self._scope())
                    rm_id = vendor_old_resp.rm_id
                    rmname = employee_service.get_employee(rm_id, user_id)
                    vendor_old_resp.rm_id = rmname

                    custcategory_id = vendor_old_resp.custcategory_id
                    custcategory = customercategory_service.fetch_customercategory(custcategory_id, user_id)
                    vendor_old_resp.custcategory_id = custcategory

                    # user_id
                    vendor_old_resp.user_id = user_id
                    vendor_status = vendor_old_resp.vendor_status

                    vendorstatus_get = getVendorStatus(vendor_status)
                    vendor_old_resp.vendor_status_name = vendorstatus_get

                    vendormainstatus_get = getVendorMainStatus(vendor_old_resp.mainstatus)
                    vendor_old_resp.mainstatus_name = vendormainstatus_get
                    vendorrequeststatus_get = getVendorRequestStatus(vendor_old_resp.requeststatus)
                    vendor_old_resp.requeststatus_name = vendorrequeststatus_get

                    # new data
                    mod_ref_new_id = i.modify_ref_id
                    vendor_new_resp = vendor_service.fetch_vendor(mod_ref_new_id, user_id)
                    # address
                    address = address_service.fetch_vendoraddress_modification(mod_ref_new_id, user_id)
                    vendor_new_resp.address = address
                    city_id = vendor_new_resp.address.city_id
                    city = city_service.fetch_city(city_id, user_id)
                    vendor_new_resp.address.city_id = city
                    state_id = vendor_new_resp.address.state_id
                    state = state_service.fetchstate(state_id)
                    vendor_new_resp.address.state_id = state
                    district_id = vendor_new_resp.address.district_id
                    district = district_service.fetchdistrict(district_id)
                    vendor_new_resp.address.district_id = district
                    pincode_id = vendor_new_resp.address.pincode_id
                    pincode = pincode_service.fetch_pincode(pincode_id, user_id)
                    vendor_new_resp.address.pincode_id = pincode
                    # contact
                    contact = contact_service.fetch_vendorcontact_modification(mod_ref_new_id, user_id)
                    vendor_new_resp.contact = contact

                    # designation_id = vendor_new_resp.contact.designation_id
                    # designation = designation_service.fetch_designation(designation_id)
                    # vendor_new_resp.contact.designation_id = designation
                    # # profile
                    profile = profile_service.fetch_profile_modification(mod_ref_new_id, user_id)
                    vendor_new_resp.profile = profile
                    director = director_service.fetch_director_modification(mod_ref_new_id, user_id)
                    vendor_new_resp.director = director
                    # orgtype
                    orgtype_id = vendor_new_resp.orgtype
                    orgtype = getOrgType(orgtype_id)
                    vendor_new_resp.orgtype = orgtype

                    # classification
                    classification_id = vendor_new_resp.classification
                    classification = getClassification(classification_id)
                    vendor_new_resp.classification = classification

                    # group
                    group_id = vendor_new_resp.group
                    group = getGroup(group_id)
                    vendor_new_resp.group = group

                    # composite
                    composite_id = vendor_new_resp.composite
                    composite = getComposite(composite_id)
                    vendor_new_resp.composite = composite

                    # type
                    type_id = vendor_new_resp.type
                    type = getType(type_id)
                    vendor_new_resp.type = type

                    # rmname
                    employee_service = EmployeeService(self._scope())
                    rm_id = vendor_new_resp.rm_id
                    rmname = employee_service.get_employee(rm_id, user_id)
                    vendor_new_resp.rm_id = rmname

                    custcategory_id = vendor_new_resp.custcategory_id
                    custcategory = customercategory_service.fetch_customercategory(custcategory_id, user_id)
                    vendor_new_resp.custcategory_id = custcategory

                    # user_id
                    vendor_new_resp.user_id = user_id
                    vendor_status = vendor_new_resp.vendor_status

                    vendorstatus_get = getVendorStatus(vendor_status)
                    vendor_new_resp.vendor_status_name = vendorstatus_get

                    vendormainstatus_get = getVendorMainStatus(vendor_new_resp.mainstatus)
                    vendor_new_resp.mainstatus_name = vendormainstatus_get
                    vendorrequeststatus_get = getVendorRequestStatus(vendor_new_resp.requeststatus)
                    vendor_new_resp.requeststatus_name = vendorrequeststatus_get

                    # risk type
                    # vendorrisktype_get = get_risk_type(vendor_new_resp.risktype)
                    # vendor_new_resp.risktype = vendorrisktype_get

                    vendor_response = ModificationDataResponse()
                    vendor_response.set_action(mod_status)
                    vendor_response.set_type_name(i.ref_type)
                    vendor_response.set_old_data(vendor_old_resp)
                    vendor_response.set_new_data(vendor_new_resp)
                    vlist.append(vendor_response)

                if i.ref_type == VendorRefType.VENDOR_CONTRACT:
                    contract_id = i.modify_ref_id
                    contract_ref_id = i.ref_id
                    contract_service = ContractorService(self._scope())
                    con_old_resp = contract_service.fetch_contractor(contract_ref_id, user_id, vendor_id)
                    con_new_resp = contract_service.fetch_contractor(contract_id, user_id, vendor_id)
                    contract_response = ModificationDataResponse()
                    contract_response.set_action(mod_status)
                    contract_response.set_type_name(i.ref_type)
                    contract_response.set_old_data(con_old_resp)
                    contract_response.set_new_data(con_new_resp)
                    vlist.append(contract_response)
                if i.ref_type == VendorRefType.VENDOR_BRANCH:
                    branch_id = i.modify_ref_id
                    branch_ref_id = i.ref_id
                    branch_service = branchservice(self._scope())
                    contact_service = ContactService(self._scope())
                    address_service = AddressService(self._scope())
                    state_service = StateService(self._scope())
                    city_service = CityService(self._scope())
                    district_service = DistrictService(self._scope())
                    pincode_service = PincodeService(self._scope())
                    contacttype_service = ContactTypeService(self._scope())
                    # designation_service = DesignationService(self._scope())

                    branch_old_resp = branch_service.fetch_branch(branch_ref_id)
                    # contact
                    cont_id = branch_old_resp.contact_id
                    contact = contact_service.fetch_contact(cont_id, user_id)
                    branch_old_resp.contact_id = contact
                    # address
                    add_id = branch_old_resp.address_id
                    address = address_service.fetch_address(add_id, user_id)
                    branch_old_resp.address_id = address
                    city_id = branch_old_resp.address_id.city_id
                    city = city_service.fetch_city(city_id, user_id)
                    branch_old_resp.address_id.city_id = city
                    state_id = branch_old_resp.address_id.state_id
                    state = state_service.fetchstate(state_id)
                    branch_old_resp.address_id.state_id = state
                    district_id = branch_old_resp.address_id.district_id
                    district = district_service.fetchdistrict(district_id)
                    branch_old_resp.address_id.district_id = district
                    pincode_id = branch_old_resp.address_id.pincode_id
                    pincode = pincode_service.fetch_pincode(pincode_id, user_id)
                    branch_old_resp.address_id.pincode_id = pincode
                    # contact

                    # designation_id = branch_old_resp.contact_id.designation_id
                    # designation = designation_service.fetch_designation(designation_id)
                    # branch_old_resp.contact_id.designation_id = designation
                    # new data
                    branch_new_resp = branch_service.fetch_branch(branch_id)
                    # contact
                    cont_id = branch_new_resp.contact_id
                    contact = contact_service.fetch_contact(cont_id, user_id)
                    branch_new_resp.contact_id = contact
                    # address
                    add_id = branch_new_resp.address_id
                    address = address_service.fetch_address(add_id, user_id)
                    branch_new_resp.address_id = address
                    city_id = branch_new_resp.address_id.city_id
                    city = city_service.fetch_city(city_id, user_id)
                    branch_new_resp.address_id.city_id = city
                    state_id = branch_new_resp.address_id.state_id
                    state = state_service.fetchstate(state_id)
                    branch_new_resp.address_id.state_id = state
                    district_id = branch_new_resp.address_id.district_id
                    district = district_service.fetchdistrict(district_id)
                    branch_new_resp.address_id.district_id = district
                    pincode_id = branch_new_resp.address_id.pincode_id
                    pincode = pincode_service.fetch_pincode(pincode_id, user_id)
                    branch_new_resp.address_id.pincode_id = pincode
                    # contact

                    # designation_id = branch_new_resp.contact_id.designation_id
                    # designation = designation_service.fetch_designation(designation_id)
                    # branch_new_resp.contact_id.designation_id = designation

                    branch_response = ModificationDataResponse()
                    branch_response.set_action(mod_status)
                    branch_response.set_type_name(i.ref_type)
                    branch_response.set_old_data(branch_old_resp)
                    branch_response.set_new_data(branch_new_resp)
                    vlist.append(branch_response)
                if i.ref_type == VendorRefType.VENDOR_CLIENT:
                    client_id = i.modify_ref_id
                    client_ref_id = i.ref_id
                    client_service = ClientService(self._scope())
                    address_service = AddressService(self._scope())
                    state_service = StateService(self._scope())
                    city_service = CityService(self._scope())
                    district_service = DistrictService(self._scope())
                    pincode_service = PincodeService(self._scope())

                    client_old_resp = client_service.fetch_client(client_ref_id)
                    # address
                    address_id = client_old_resp.address_id
                    address_resp = address_service.fetch_address(address_id, user_id)
                    client_old_resp.address_id = address_resp
                    # pincode
                    pincode_id = client_old_resp.address_id.pincode_id
                    pincode_resp = pincode_service.fetch_pincode(pincode_id, user_id)
                    client_old_resp.address_id.pincode_id = pincode_resp
                    # city
                    city_id = client_old_resp.address_id.city_id
                    city_resp = city_service.fetch_city(city_id, user_id)
                    client_old_resp.address_id.city_id = city_resp
                    # state
                    state_id = client_old_resp.address_id.state_id
                    state_resp = state_service.fetchstate(state_id)
                    client_old_resp.address_id.state_id = state_resp
                    # district
                    district_id = client_old_resp.address_id.district_id
                    district_resp = district_service.fetchdistrict(district_id)
                    client_old_resp.address_id.district_id = district_resp

                    client_new_resp = client_service.fetch_client(client_id)
                    # address
                    address_id = client_new_resp.address_id
                    address_resp = address_service.fetch_address(address_id, user_id)
                    client_new_resp.address_id = address_resp
                    # pincode
                    pincode_id = client_new_resp.address_id.pincode_id
                    pincode_resp = pincode_service.fetch_pincode(pincode_id, user_id)
                    client_new_resp.address_id.pincode_id = pincode_resp
                    # city
                    city_id = client_new_resp.address_id.city_id
                    city_resp = city_service.fetch_city(city_id, user_id)
                    client_new_resp.address_id.city_id = city_resp
                    # state
                    state_id = client_new_resp.address_id.state_id
                    state_resp = state_service.fetchstate(state_id)
                    client_new_resp.address_id.state_id = state_resp
                    # district
                    district_id = client_new_resp.address_id.district_id
                    district_resp = district_service.fetchdistrict(district_id)
                    client_new_resp.address_id.district_id = district_resp

                    client_response = ModificationDataResponse()
                    client_response.set_action(mod_status)
                    client_response.set_type_name(i.ref_type)
                    client_response.set_old_data(client_old_resp)
                    client_response.set_new_data(client_new_resp)
                    vlist.append(client_response)
                if i.ref_type == VendorRefType.VENDOR_PRODUCT:
                    product_id = i.modify_ref_id
                    product_ref_id = i.ref_id
                    product_service = productservice(self._scope())
                    contacttype_service = ContactTypeService(self._scope())
                    # designation_service = DesignationService(self._scope())
                    contact_service = ContactService(self._scope())
                    product_old_resp = product_service.fetch_product(product_ref_id, vendor_id)
                    # contact1
                    con_client_id1 = product_old_resp.client1_id
                    contact_resp1 = contact_service.fetch_contact(con_client_id1, user_id)
                    product_old_resp.client1_id = contact_resp1
                    # contacttype

                    # designation
                    # designation_id = product_old_resp.client1_id.designation_id
                    # designation_resp = designation_service.fetch_designation(designation_id)
                    # product_old_resp.client1_id.designation_id = designation_resp

                    # contact 2
                    con_client_id2 = product_old_resp.client2_id
                    contact_resp2 = contact_service.fetch_contact(con_client_id2, user_id)
                    product_old_resp.client2_id = contact_resp2
                    # contacttype

                    # designation
                    # designation_id = product_old_resp.client2_id.designation_id
                    # designation_resp = designation_service.fetch_designation(designation_id)
                    # product_old_resp.client2_id.designation_id = designation_resp

                    # contact 3
                    con_customer_id1 = product_old_resp.customer1_id
                    contact_resp3 = contact_service.fetch_contact(con_customer_id1, user_id)
                    product_old_resp.customer1_id = contact_resp3
                    # contacttype

                    # designation
                    # designation_id = product_old_resp.customer1_id.designation_id
                    # designation_resp = designation_service.fetch_designation(designation_id)
                    # product_old_resp.customer1_id.designation_id = designation_resp

                    # contact 4
                    con_customer_id2 = product_old_resp.customer2_id
                    contact_resp4 = contact_service.fetch_contact(con_customer_id2, user_id)
                    product_old_resp.customer2_id = contact_resp4
                    # contacttype

                    # designation
                    # designation_id = product_old_resp.customer2_id.designation_id
                    # designation_resp = designation_service.fetch_designation(designation_id)
                    # product_old_resp.customer2_id.designation_id = designation_resp

                    product_new_resp = product_service.fetch_product(product_id, vendor_id)
                    # contact1
                    con_client_id1 = product_new_resp.client1_id
                    contact_resp1 = contact_service.fetch_contact(con_client_id1, user_id)
                    product_new_resp.client1_id = contact_resp1
                    # contacttype

                    # designation
                    # designation_id = product_new_resp.client1_id.designation_id
                    # designation_resp = designation_service.fetch_designation(designation_id)
                    # product_new_resp.client1_id.designation_id = designation_resp

                    # contact 2
                    con_client_id2 = product_new_resp.client2_id
                    contact_resp2 = contact_service.fetch_contact(con_client_id2, user_id)
                    product_new_resp.client2_id = contact_resp2
                    # contacttype

                    # designation
                    # designation_id = product_new_resp.client2_id.designation_id
                    # designation_resp = designation_service.fetch_designation(designation_id)
                    # product_new_resp.client2_id.designation_id = designation_resp

                    # contact 3
                    con_customer_id1 = product_new_resp.customer1_id
                    contact_resp3 = contact_service.fetch_contact(con_customer_id1, user_id)
                    product_new_resp.customer1_id = contact_resp3
                    # contacttype

                    # designation
                    # designation_id = product_new_resp.customer1_id.designation_id
                    # designation_resp = designation_service.fetch_designation(designation_id)
                    # product_new_resp.customer1_id.designation_id = designation_resp

                    # contact 4
                    con_customer_id2 = product_new_resp.customer2_id
                    contact_resp4 = contact_service.fetch_contact(con_customer_id2, user_id)
                    product_new_resp.customer2_id = contact_resp4
                    # contacttype

                    # designation
                    # designation_id = product_new_resp.customer2_id.designation_id
                    # designation_resp = designation_service.fetch_designation(designation_id)
                    # product_new_resp.customer2_id.designation_id = designation_resp

                    product_response = ModificationDataResponse()
                    product_response.set_action(mod_status)
                    product_response.set_type_name(i.ref_type)
                    product_response.set_old_data(product_old_resp)
                    product_response.set_new_data(product_new_resp)
                    vlist.append(product_response)
                if i.ref_type == VendorRefType.VENDOR_DOCUMENT:
                    document_id = i.modify_ref_id
                    document_ref_id = i.ref_id
                    document_service = DocumentService(self._scope())
                    vendor_service = VendorService(self._scope())
                    document_old_resp = document_service.fetch_document(document_ref_id)
                    tab_type = VendorRefType.VENDOR_DOCUMENT

                    docu_service = DocumentGroupService(self._scope())
                    docgroup_id = document_old_resp.docgroup_id
                    docugroup = docu_service.fetch_docugroup(docgroup_id)
                    document_old_resp.docgroup_id = docugroup

                    data_obj1 = document_service.vendor_file_data(document_ref_id, tab_type)
                    document_old_resp.file_id = data_obj1.data
                    # doc_json.append(data_obj.data)
                    document_new_resp = document_service.fetch_document(document_id)
                    data_obj = document_service.vendor_file_data(document_id, tab_type)
                    doc_arry = vendor_service.append_doc(data_obj1.data, data_obj.data)
                    docgroup_id = document_new_resp.docgroup_id
                    docugroup = docu_service.fetch_docugroup(docgroup_id)
                    document_new_resp.docgroup_id = docugroup

                    document_new_resp.file_id = doc_arry
                    document_response = ModificationDataResponse()
                    document_response.set_action(mod_status)
                    document_response.set_type_name(i.ref_type)
                    document_response.set_old_data(document_old_resp)
                    document_response.set_new_data(document_new_resp)
                    vlist.append(document_response)
                if i.ref_type == VendorRefType.VENDOR_SUPPLIERTAX:
                    suppliertax_id = i.modify_ref_id
                    suppliertax_ref_id = i.ref_id
                    tax_service = TaxService(self._scope())
                    document_service = DocumentService(self._scope())
                    branch_service = branchservice(self._scope())
                    vendor_service = VendorService(self._scope())
                    taxmaster_service = TaxMasterService(self._scope())
                    subtax_service = SubTaxService(self._scope())
                    taxrate_service = TaxRateService(self._scope())
                    suppliertax_old_resp = tax_service.fetch_suppliertax(suppliertax_ref_id)
                    tab_type = VendorRefType.VENDOR_SUPPLIERTAX
                    data1_obj = document_service.vendor_file_data(suppliertax_ref_id, tab_type)
                    suppliertax_old_resp.attachment = data1_obj.data

                    tax1_id = suppliertax_old_resp.tax
                    tax = taxmaster_service.fetch_tax(tax1_id, user_id)
                    suppliertax_old_resp.tax = tax
                    subtax_id = suppliertax_old_resp.subtax
                    subtax = subtax_service.fetch_subtax(subtax_id, user_id)
                    suppliertax_old_resp.subtax = subtax
                    if suppliertax_old_resp.taxrate == 0:
                        suppliertax_old_resp.taxrate = None
                    else:
                        taxrate_id = suppliertax_old_resp.taxrate
                        taxrate = taxrate_service.fetch_taxrate(taxrate_id, user_id)
                        suppliertax_old_resp.taxrate = taxrate

                    supplierbranch_id = suppliertax_old_resp.branch_id
                    supplierbranch = branch_service.fetch_branch(supplierbranch_id)
                    suppliertax_old_resp.branch_id = supplierbranch

                    suppliertax_new_resp = tax_service.fetch_suppliertax(suppliertax_id)
                    data_obj = document_service.vendor_file_data(suppliertax_id, tab_type)
                    doc_arry = vendor_service.append_doc(data1_obj.data, data_obj.data)
                    suppliertax_new_resp.attachment = doc_arry

                    tax1_id = suppliertax_new_resp.tax
                    tax = taxmaster_service.fetch_tax(tax1_id, user_id)
                    suppliertax_new_resp.tax = tax
                    subtax_id = suppliertax_new_resp.subtax
                    subtax = subtax_service.fetch_subtax(subtax_id, user_id)
                    suppliertax_new_resp.subtax = subtax
                    if suppliertax_new_resp.taxrate == 0:
                        suppliertax_new_resp.taxrate = None
                    else:
                        taxrate_id = suppliertax_new_resp.taxrate
                        taxrate = taxrate_service.fetch_taxrate(taxrate_id, user_id)
                        suppliertax_new_resp.taxrate = taxrate

                    supplierbranch_id = suppliertax_new_resp.branch_id
                    supplierbranch = branch_service.fetch_branch(supplierbranch_id)
                    suppliertax_new_resp.branch_id = supplierbranch

                    suppliertax_response = ModificationDataResponse()
                    suppliertax_response.set_action(mod_status)
                    suppliertax_response.set_type_name(i.ref_type)
                    suppliertax_response.set_old_data(suppliertax_old_resp)
                    suppliertax_response.set_new_data(suppliertax_new_resp)
                    vlist.append(suppliertax_response)
                if i.ref_type == VendorRefType.VENDOR_PAYMENT:
                    payment_id = i.modify_ref_id
                    payment_ref_id = i.ref_id
                    payment_service = paymentservice(self._scope())
                    bank_service = BankService(self._scope())
                    paymode_service = PaymodeService(self._scope())
                    bankbranch_service = BankBranchService(self._scope())
                    branch_service = branchservice(self._scope())
                    payment_old_resp = payment_service.fetch_payment(payment_ref_id)
                    bank_id = payment_old_resp.bank_id
                    bank = bank_service.fetch_bank(bank_id, user_id)
                    payment_old_resp.bank_id = bank

                    branch_id = payment_old_resp.branch_id
                    branch = bankbranch_service.fetch_bankbranch(branch_id, user_id)
                    payment_old_resp.branch_id = branch

                    paymode_id = payment_old_resp.paymode_id
                    paymode = paymode_service.fetchpaymode(paymode_id)
                    payment_old_resp.paymode_id = paymode

                    supplierbranch_id = payment_old_resp.supplierbranch_id
                    supplierbranch = branch_service.fetch_branch(supplierbranch_id)
                    payment_old_resp.supplierbranch_id = supplierbranch

                    payment_new_resp = payment_service.fetch_payment(payment_id)
                    bank_id = payment_new_resp.bank_id
                    bank = bank_service.fetch_bank(bank_id, user_id)
                    payment_new_resp.bank_id = bank

                    branch_id = payment_new_resp.branch_id
                    branch = bankbranch_service.fetch_bankbranch(branch_id, user_id)
                    payment_new_resp.branch_id = branch

                    paymode_id = payment_new_resp.paymode_id
                    paymode = paymode_service.fetchpaymode(paymode_id)
                    payment_new_resp.paymode_id = paymode

                    supplierbranch_id = payment_new_resp.supplierbranch_id
                    supplierbranch = branch_service.fetch_branch(supplierbranch_id)
                    payment_new_resp.supplierbranch_id = supplierbranch

                    payment_response = ModificationDataResponse()
                    payment_response.set_action(mod_status)
                    payment_response.set_type_name(i.ref_type)
                    payment_response.set_old_data(payment_old_resp)
                    payment_response.set_new_data(payment_new_resp)
                    vlist.append(payment_response)
                if i.ref_type == VendorRefType.VENDOR_ACTIVITY:
                    activity_id = i.modify_ref_id
                    activity_ref_id = i.ref_id
                    activity_service = ActivityService(self._scope())
                    contact_service = ContactService(self._scope())
                    contacttype_service = ContactTypeService(self._scope())
                    # designation_service = DesignationService(self._scope())
                    activity_old_resp = activity_service.fetch_activity(activity_ref_id)
                    # contact
                    contact_id = activity_old_resp.contact_id
                    contact_resp = contact_service.fetch_contact(contact_id, user_id)
                    activity_old_resp.contact_id = contact_resp
                    # contacttype

                    # designation
                    # designation_id = activity_old_resp.contact_id.designation_id
                    # designation_resp = designation_service.fetch_designation(designation_id)
                    # activity_old_resp.contact_id.designation_id = designation_resp

                    activity_new_resp = activity_service.fetch_activity(activity_id)
                    # contact
                    contact_id = activity_new_resp.contact_id
                    contact_resp = contact_service.fetch_contact(contact_id, user_id)
                    activity_new_resp.contact_id = contact_resp
                    # contacttype

                    # designation
                    # designation_id = activity_new_resp.contact_id.designation_id
                    # designation_resp = designation_service.fetch_designation(designation_id)
                    # activity_new_resp.contact_id.designation_id = designation_resp

                    activity_response = ModificationDataResponse()
                    activity_response.set_action(mod_status)
                    activity_response.set_type_name(i.ref_type)
                    activity_response.set_old_data(activity_old_resp)
                    activity_response.set_new_data(activity_new_resp)
                    vlist.append(activity_response)
                if i.ref_type == VendorRefType.VENDOR_ACTIVITYDETAIL:
                    activitydtl_id = i.modify_ref_id
                    activitydtl_ref_id = i.ref_id
                    activitydtl_service = ActivityDetailsService(self._scope())
                    activitydtl_old_resp = activitydtl_service.fetch_activitydtl(activitydtl_ref_id)
                    activity_service = ActivityService(self._scope())
                    activity_id = activitydtl_old_resp.activity_id
                    activity = activity_service.fetch_activity(activity_id)
                    activitydtl_old_resp.activity_id = activity

                    emp_service = EmployeeService(self._scope())
                    raisor_id = activitydtl_old_resp.raisor
                    raisor = emp_service.get_employee(raisor_id, user_id)
                    activitydtl_old_resp.raisor = raisor

                    approver_id = activitydtl_old_resp.approver
                    approver = emp_service.get_employee(approver_id, user_id)
                    activitydtl_old_resp.approver = approver
                    activitydtl_new_resp = activitydtl_service.fetch_activitydtl(activitydtl_id)

                    activity_id = activitydtl_new_resp.activity_id
                    activity = activity_service.fetch_activity(activity_id)
                    activitydtl_new_resp.activity_id = activity

                    raisor_id = activitydtl_new_resp.raisor
                    raisor = emp_service.get_employee(raisor_id, user_id)
                    activitydtl_new_resp.raisor = raisor

                    approver_id = activitydtl_new_resp.approver
                    approver = emp_service.get_employee(approver_id, user_id)
                    activitydtl_new_resp.approver = approver
                    activitydtl_response = ModificationDataResponse()
                    activitydtl_response.set_action(mod_status)
                    activitydtl_response.set_type_name(i.ref_type)
                    activitydtl_response.set_old_data(activitydtl_old_resp)
                    activitydtl_response.set_new_data(activitydtl_new_resp)
                    vlist.append(activitydtl_response)
                if i.ref_type == VendorRefType.VENDOR_CATELOG:
                    catelog_id = i.modify_ref_id
                    catelog_ref_id = i.ref_id
                    catelog_service = CatelogService(self._scope())
                    subcategory_service = SubcategoryService(self._scope())
                    category_service = CategoryService(self._scope())
                    product_service = ProductService(self._scope())
                    activitydetail_service = ActivityDetailsService(self._scope())
                    uom_service = UomService(self._scope())
                    catelog_old_resp = catelog_service.fetch_catelog(catelog_ref_id)

                    activitydetail_id = catelog_old_resp.activitydetail_id
                    activity = activitydetail_service.fetch_activitydtl(activitydetail_id)
                    catelog_old_resp.activitydetail_id = activity

                    category_id = catelog_old_resp.category
                    category = category_service.fetchcategory(category_id)
                    catelog_old_resp.category = category

                    uom_id = catelog_old_resp.uom
                    if uom_id is not None:
                        uom = uom_service.fetch_uom(uom_id, user_id)
                        catelog_old_resp.uom = uom

                    subcategory_id = catelog_old_resp.subcategory
                    subcategory = subcategory_service.fetchsubcategory(subcategory_id)
                    catelog_old_resp.subcategory = subcategory

                    product_id = catelog_old_resp.productname
                    product = product_service.fetch_product(product_id, user_id)
                    catelog_old_resp.productname = product

                    catelog_new_resp = catelog_service.fetch_catelog(catelog_id)

                    activitydetail_id = catelog_new_resp.activitydetail_id
                    activity = activitydetail_service.fetch_activitydtl(activitydetail_id)
                    catelog_new_resp.activitydetail_id = activity

                    category_id = catelog_new_resp.category
                    category = category_service.fetchcategory(category_id)
                    catelog_new_resp.category = category

                    uom_id = catelog_new_resp.uom
                    if uom_id is not None:
                        uom = uom_service.fetch_uom(uom_id, user_id)
                        catelog_new_resp.uom = uom

                    subcategory_id = catelog_new_resp.subcategory
                    subcategory = subcategory_service.fetchsubcategory(subcategory_id)
                    catelog_new_resp.subcategory = subcategory

                    product_id = catelog_new_resp.productname
                    product = product_service.fetch_product(product_id, user_id)
                    catelog_new_resp.productname = product

                    catelog_response = ModificationDataResponse()
                    catelog_response.set_action(mod_status)
                    catelog_response.set_type_name(i.ref_type)
                    catelog_response.set_old_data(catelog_old_resp)
                    catelog_response.set_new_data(catelog_new_resp)
                    vlist.append(catelog_response)


                if i.ref_type == VendorRefType.VENDOR_RISK:
                    new_risk_id = i.modify_ref_id
                    old_risk_id = i.ref_id
                    risk_service = RiskService(self._scope())
                    new_risk_resp = risk_service.fetch_risk(vendor_id, new_risk_id)
                    old_risk_resp = risk_service.fetch_risk(vendor_id, old_risk_id)
                    risk_response = ModificationDataResponse()
                    risk_response.set_action(mod_status)
                    risk_response.set_type_name(i.ref_type)
                    risk_response.set_old_data(old_risk_resp)
                    risk_response.set_new_data(new_risk_resp)
                    vlist.append(risk_response)
                if i.ref_type == VendorRefType.VENDOR_KYC:
                    new_kyc_id = i.modify_ref_id
                    old_kyc_id = i.ref_id
                    tab_type = VendorRefType.VENDOR_KYC
                    kyc_service = KYCService(self._scope())
                    document_service = DocumentService(self._scope())

                    document_new_resp = kyc_service.fetch_kyc(new_kyc_id, user_id)
                    document_old_resp = kyc_service.fetch_kyc(old_kyc_id, user_id)

                    data_old = document_service.vendor_file_data(old_kyc_id, tab_type)
                    document_old_resp.report_file_id = data_old.data

                    data_new = document_service.vendor_file_data(new_kyc_id, tab_type)
                    # document_new_resp.report_file_id = data_new.data
                    doc_arry = vendor_service.append_doc(data_old.data, data_new.data)
                    document_new_resp.report_file_id = doc_arry

                    document_response = ModificationDataResponse()
                    document_response.set_action(mod_status)
                    document_response.set_type_name(i.ref_type)
                    document_response.set_old_data(document_old_resp)
                    document_response.set_new_data(document_new_resp)
                    vlist.append(document_response)
                if i.ref_type == VendorRefType.BCP_QUESION:
                    bcp_service = QuestionnaireService(self._scope())
                    old_bcp_resp = bcp_service.fetch_questionnaries_bcp(vendor_id,'1')
                    new_bcp_resp = bcp_service.bcp_question_list(vendor_id,'1')
                    bcp_response = ModificationDataResponse()
                    bcp_response.set_action(mod_status)
                    bcp_response.set_type_name(i.ref_type)
                    bcp_response.set_old_data(old_bcp_resp)
                    bcp_response.set_new_data(new_bcp_resp)
                    vlist.append(bcp_response)
                if i.ref_type == VendorRefType.DUE_DELIGENCE:
                    due_service = QuestionnaireService(self._scope())
                    old_due_resp = due_service.fetch_questionnaries_due(vendor_id,'2')
                    new_due_resp = due_service.due_question_list(vendor_id,'2')
                    due_response = ModificationDataResponse()
                    due_response.set_action(mod_status)
                    due_response.set_type_name(i.ref_type)
                    due_response.set_old_data(old_due_resp)
                    due_response.set_new_data(new_due_resp)
                    vlist.append(due_response)
        final_data = vlist

        return HttpResponse(final_data.get(), content_type='application/json')

    def modication_approve(self, request, vendor_id, employee_id):
        vendor_service = VendorService(self._scope())
        vendor_rmidobj = Vendor.objects.using(self._current_app_schema()).get(id=vendor_id, entity_id=self._entity_id())
        vendor_statusid = vendor_rmidobj.vendor_status
        data = json.loads(request.body)
        if vendor_statusid == 4:
            isheader_obj = vendor_service.isheader(request)
            valid_header = vendor_service.valid_checker(vendor_id, employee_id)
            logger.info(str(valid_header)+ ' valid_header')
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
        resp_obj = vendor_service.modificationapprove_serviceview(vendor_id)
        x = resp_obj.data
        user_id = request.user.id
        emp_service = EmployeeService(self._scope())
        employee_id = emp_service.get_empid_from_userid(user_id)
        vendor_resp = vendor_service.fetch_vendor(vendor_id, employee_id)
        request_sts = vendor_resp.requeststatus
        if request_sts == 5:
            resp_obj = vendor_service.modification_approve_status(vendor_id, request_sts, employee_id, data)

        if request_sts == 2:
            for i in x:
                mod_status = i.mod_status
                old_id = i.ref_id
                new_id = i.modify_ref_id
                mod_type = i.ref_type
                if mod_status != ModifyStatus.delete:
                    #     resp_obj = vendor_service.modify_delrecursion(vendor_id, old_id,user_id)
                    if mod_type == VendorRefType.VENDOR:
                        resp_obj = vendor_service.modification_action_vendor(mod_status, old_id, new_id, employee_id)
                    if mod_type == VendorRefType.VENDOR_ADDRESS:
                        address_service = VendorAddressService(self._scope())
                        resp_obj = address_service.modification_action_vendoraddress(mod_status, old_id, new_id,
                                                                                     vendor_id, employee_id)
                    if mod_type == VendorRefType.VENDOR_CONTACT:
                        contact_service = VendorContactService(self._scope())
                        resp_obj = contact_service.modification_action_vendorcontact(mod_status, old_id, new_id,
                                                                                     vendor_id, employee_id)
                    if mod_type == VendorRefType.VENDOR_PROFILE:
                        profile_service = ProfileService(self._scope())
                        resp_obj = profile_service.modification_action_vendorprofile(mod_status, old_id, new_id,
                                                                                     vendor_id, employee_id)
                    if mod_type == VendorRefType.VENDOR_DIRECTOR:
                        director_service = DirectorService(self._scope())
                        resp_obj = director_service.modification_action_vendordirector(mod_status, old_id, new_id,
                                                                                       vendor_id,
                                                                                       employee_id)
                    if mod_type == VendorRefType.VENDOR_BRANCH:
                        branch_service = branchservice(self._scope())
                        resp_obj = branch_service.modification_action_branch(mod_status, old_id, new_id, vendor_id,
                                                                             employee_id)
                    if mod_type == VendorRefType.VENDOR_CONTRACT:
                        contract_service = ContractorService(self._scope())
                        resp_obj = contract_service.modification_action_contractor(mod_status, old_id, new_id,
                                                                                   vendor_id, employee_id)
                    if mod_type == VendorRefType.VENDOR_CLIENT:
                        client_service = ClientService(self._scope())
                        resp_obj = client_service.modification_action_client(mod_status, old_id, new_id, vendor_id,
                                                                             employee_id)
                    if mod_type == VendorRefType.VENDOR_PRODUCT:
                        product_service = productservice(self._scope())
                        resp_obj = product_service.modification_action_product(mod_status, old_id, new_id, vendor_id,
                                                                               employee_id)
                    if mod_type == VendorRefType.VENDOR_DOCUMENT:
                        document_service = DocumentService(self._scope())
                        resp_obj = document_service.modification_action_document(mod_status, old_id, new_id, vendor_id,
                                                                                 employee_id)
                    if mod_type == VendorRefType.VENDOR_SUPPLIERTAX:
                        suppliertax_service = TaxService(self._scope())
                        resp_obj = suppliertax_service.modification_action_suppliertax(mod_status, old_id, new_id,
                                                                                       vendor_id,
                                                                                       employee_id)
                    if mod_type == VendorRefType.VENDOR_PAYMENT:
                        payment_service = paymentservice(self._scope())
                        resp_obj = payment_service.modification_action_payment(mod_status, old_id, new_id, vendor_id,
                                                                               employee_id)
                    if mod_type == VendorRefType.VENDOR_ACTIVITY:
                        activity_service = ActivityService(self._scope())
                        resp_obj = activity_service.modification_action_activity(mod_status, old_id, new_id, vendor_id,
                                                                                 employee_id)
                    if mod_type == VendorRefType.VENDOR_ACTIVITYDETAIL:
                        activitydtl_service = ActivityDetailsService(self._scope())
                        resp_obj = activitydtl_service.modification_action_activitydetail(mod_status, old_id, new_id,
                                                                                          vendor_id,
                                                                                          employee_id)
                    if mod_type == VendorRefType.VENDOR_CATELOG:
                        catelog_service = CatelogService(self._scope())
                        resp_obj = catelog_service.modification_action_catelog(mod_status, old_id, new_id, vendor_id,
                                                                               employee_id)
                    if mod_type == VendorRefType.VENDOR_RISK:
                        risk_service = RiskService(self._scope())
                        resp_obj = risk_service.modification_action_risk(mod_status, old_id, new_id, vendor_id,
                                                                               employee_id)
                    if mod_type == VendorRefType.VENDOR_KYC:
                        kyc_service = KYCService(self._scope())
                        resp_obj = kyc_service.modification_action_kyc(mod_status,
                                                                       old_id, new_id, vendor_id, employee_id)
                    if mod_type == VendorRefType.BCP_QUESION:
                        bcp_service = QuestionnaireService(self._scope())
                        resp_obj = bcp_service.modification_action_bcp(vendor_id,'1',employee_id)

                    if mod_type == VendorRefType.DUE_DELIGENCE:
                        due_service = QuestionnaireService(self._scope())
                        resp_obj = due_service.modification_action_due(vendor_id,'2',employee_id)

                if mod_status == ModifyStatus.delete:
                    #     resp_obj = vendor_service.modify_delrecursion(vendor_id, old_id,user_id)
                    if mod_type == VendorRefType.VENDOR:
                        resp_obj = vendor_service.modification_action_vendor(mod_status, old_id, new_id, employee_id)
                    if mod_type == VendorRefType.VENDOR_ADDRESS:
                        address_service = VendorAddressService(self._scope())
                        resp_obj = address_service.modification_action_vendoraddress(mod_status, old_id, new_id,
                                                                                     vendor_id,
                                                                                     employee_id)
                    if mod_type == VendorRefType.VENDOR_CONTACT:
                        contact_service = VendorContactService(self._scope())
                        resp_obj = contact_service.modification_action_vendorcontact(mod_status, old_id, new_id,
                                                                                     vendor_id,
                                                                                     employee_id)
                    if mod_type == VendorRefType.VENDOR_PROFILE:
                        profile_service = ProfileService(self._scope())
                        resp_obj = profile_service.modification_action_vendorprofile(mod_status, old_id, new_id,
                                                                                     vendor_id,
                                                                                     employee_id)
                    if mod_type == VendorRefType.VENDOR_DIRECTOR:
                        director_service = DirectorService(self._scope())
                        resp_obj = director_service.modification_action_vendordirector(mod_status, old_id, new_id,
                                                                                       vendor_id,
                                                                                       employee_id)
                    if mod_type == VendorRefType.VENDOR_BRANCH:
                        branch_service = branchservice(self._scope())
                        resp_obj = branch_service.modification_action_branch(mod_status, old_id, new_id, vendor_id,
                                                                             employee_id)
                    if mod_type == VendorRefType.VENDOR_CONTRACT:
                        contract_service = ContractorService(self._scope())
                        resp_obj = contract_service.modification_action_contractor(mod_status, old_id, new_id,
                                                                                   vendor_id,
                                                                                   employee_id)
                    if mod_type == VendorRefType.VENDOR_CLIENT:
                        client_service = ClientService(self._scope())
                        resp_obj = client_service.modification_action_client(mod_status, old_id, new_id, vendor_id,
                                                                             employee_id)
                    if mod_type == VendorRefType.VENDOR_PRODUCT:
                        product_service = productservice(self._scope())
                        resp_obj = product_service.modification_action_product(mod_status, old_id, new_id, vendor_id,
                                                                               employee_id)
                    if mod_type == VendorRefType.VENDOR_DOCUMENT:
                        document_service = DocumentService(self._scope())
                        resp_obj = document_service.modification_action_document(mod_status, old_id, new_id, vendor_id,
                                                                                 employee_id)
                    if mod_type == VendorRefType.VENDOR_SUPPLIERTAX:
                        suppliertax_service = TaxService(self._scope())
                        resp_obj = suppliertax_service.modification_action_suppliertax(mod_status, old_id, new_id,
                                                                                       vendor_id,
                                                                                       employee_id)
                    if mod_type == VendorRefType.VENDOR_PAYMENT:
                        payment_service = paymentservice(self._scope())
                        resp_obj = payment_service.modification_action_payment(mod_status, old_id, new_id, vendor_id,
                                                                               employee_id)
                    if mod_type == VendorRefType.VENDOR_ACTIVITY:
                        activity_service = ActivityService(self._scope())
                        resp_obj = activity_service.modification_action_activity(mod_status, old_id, new_id, vendor_id,
                                                                                 employee_id)
                    if mod_type == VendorRefType.VENDOR_ACTIVITYDETAIL:
                        activitydtl_service = ActivityDetailsService(self._scope())
                        resp_obj = activitydtl_service.modification_action_activitydetail(mod_status, old_id, new_id,
                                                                                          vendor_id,
                                                                                          employee_id)
                    if mod_type == VendorRefType.VENDOR_CATELOG:
                        catelog_service = CatelogService(self._scope())
                        resp_obj = catelog_service.modification_action_catelog(mod_status, old_id, new_id, vendor_id,
                                                                               employee_id)
                    if mod_type == VendorRefType.VENDOR_RISK:
                        risk_service = RiskService(self._scope())
                        resp_obj = risk_service.modification_action_risk(mod_status, old_id, new_id, vendor_id,
                                                                                 employee_id)
                    if mod_type == VendorRefType.VENDOR_KYC:
                        kyc_service = KYCService(self._scope())
                        resp_obj = kyc_service.modification_action_kyc(mod_status, old_id, new_id, vendor_id,
                                                                                 employee_id)
            for i in x:
                mod_status = i.mod_status
                old_id = i.ref_id
                new_id = i.modify_ref_id
                mod_type = i.ref_type
                if mod_status == ModifyStatus.update or mod_status == ModifyStatus.active_in:
                    if mod_type == VendorRefType.VENDOR:
                        vendor_del = Vendor.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()
                    if mod_type == VendorRefType.VENDOR_BRANCH:
                        branch = SupplierBranch.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()
                    if mod_type == VendorRefType.VENDOR_CONTRACT:
                        contractor_del = VendorSubContractor.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()
                    if mod_type == VendorRefType.VENDOR_CLIENT:
                        client_del = VendorClient.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()
                    if mod_type == VendorRefType.VENDOR_PRODUCT:
                        product_del = SupplierProduct.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()
                    if mod_type == VendorRefType.VENDOR_DOCUMENT:
                        document = VendorDocument.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()
                    if mod_type == VendorRefType.VENDOR_SUPPLIERTAX:
                        try:
                            subt_new_id = SupplierSubTax.objects.using(self._current_app_schema()).get(suppliertax_id=new_id, entity_id=self._entity_id())
                            subt_new_id = subt_new_id.id
                            tax = SupplierTax.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()
                            subtax = SupplierSubTax.objects.using(self._current_app_schema()).filter(suppliertax_id=new_id, entity_id=self._entity_id()).delete()
                        except:
                            pass
                    if mod_type == VendorRefType.VENDOR_PAYMENT:
                        payment = SupplierPayment.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()
                    if mod_type == VendorRefType.VENDOR_ACTIVITY:
                        activity = SupplierActivity.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()
                    if mod_type == VendorRefType.VENDOR_ACTIVITYDETAIL:
                        activitydtl_del = ActivityDetail.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()
                    if mod_type == VendorRefType.VENDOR_CATELOG:
                        catelog_del = Catelog.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()
                    if mod_type == VendorRefType.VENDOR_RISK:
                        risk_del = VendorRiskInfo.objects.using(self._current_app_schema()).filter(id=new_id, entity_id=self._entity_id()).delete()
                    if mod_type == VendorRefType.VENDOR_KYC:
                        kyc_del = VendorKYC.objects.using(self._current_app_schema()).filter(id=new_id,
                                                                                                   entity_id=self._entity_id()).delete()
            resp_obj = vendor_service.modification_approve_status(vendor_id, request_sts, employee_id, data)
            # if request_sts == 2:
                # try:
                #     resp_data = vendor_service.fetch_data(vendor_id)
                #     if resp_data == 'product_mapping_norecords':
                #         transaction.set_rollback(True)
                #         error_obj = NWisefinError()
                #         error_obj.set_code(ErrorMessage.INVALID_NEW_PCODE)
                #         error_obj.set_description(ErrorMessage.INVALID_NEW_PCODE)
                #         return HttpResponse(error_obj.get(), content_type='application/json')
                #     token = "Bearer  " + get_authtoken()
                #     headers = {"content-type": "application/json", "Authorization": "" + token + ""}
                #     # datas = JsonResponse(resp_obj)
                #     datas = json.dumps(resp_data, indent=4)
                #     print(datas)
                #     logger.info(datas)
                #     resp = requests.post(
                #         "" + val_url + 'atma_main_insert?Group=New_Atma_Api_frm_Memo&Action=New_Atma_Api',
                #         data=datas,
                #         headers=headers,
                #         verify=False)
                #     results = resp.content.decode("utf-8")
                #     results = json.loads(results)
                #     logger.info(results)
                #     if results['MESSAGE'] == ['SUCCESS']:
                #         return HttpResponse(resp_obj.get(), content_type='application/json')
                #
                #     else:
                #         transaction.set_rollback(True)
                #         error_obj = NWisefinError()
                #         error_obj.set_code(ErrorMessage.INVALID_NEW_TOOLD_ATMA)
                #         # error_obj.set_description(ErrorMessage.INVALID_NEW_TOOLD_ATMA)
                #         error_obj.set_description(results)
                #         return HttpResponse(error_obj.get(), content_type='application/json')
                # except Exception as e:
                #     transaction.set_rollback(True)
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_NEW_TOOLD_ATMA)
                #     error_obj.set_description(e)
                #     # error_obj.set_description(ErrorDescription.INVALID_NEW_TOOLD_ATMA)
                #     response = HttpResponse(error_obj.get(), content_type="application/json")
                #     return HttpResponse(response, content_type='application/json')
        try:
            mail_service = VendorEmail(self._scope())
            mail_sent = mail_service.vendor_mail(vendor_id)
        except:
            logger.info('Error on vendor mail sending')
        return HttpResponse(resp_obj.get(), content_type='application/json')

    def modication_view_type(self, vendor_id):
        vendor_service = VendorService(self._scope())
        resp_obj = vendor_service.modification_serviceview(vendor_id)
        x = resp_obj.data
        set_data = set()
        for i in x:
            mod_status = i.mod_status
            if mod_status == ModifyStatus.active_in:
                if i.ref_type == VendorRefType.VENDOR_BRANCH:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.VENDOR_PAYMENT:
                    set_data.add(i.ref_type)
            if mod_status in (ModifyStatus.create, ModifyStatus.delete):
                if i.ref_type == VendorRefType.VENDOR_CONTRACT:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.VENDOR_BRANCH:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.VENDOR_CLIENT:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.VENDOR_PRODUCT:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.VENDOR_DOCUMENT:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.VENDOR_SUPPLIERTAX:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.VENDOR_PAYMENT:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.VENDOR_ACTIVITY:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.VENDOR_ACTIVITYDETAIL:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.VENDOR_CATELOG:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.VENDOR_RISK:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.VENDOR_KYC:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.BCP_QUESION:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.DUE_DELIGENCE:
                    set_data.add(i.ref_type)
            if mod_status == ModifyStatus.update:
                if i.ref_type == VendorRefType.VENDOR:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.VENDOR_CONTRACT:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.VENDOR_BRANCH:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.VENDOR_CLIENT:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.VENDOR_PRODUCT:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.VENDOR_DOCUMENT:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.VENDOR_SUPPLIERTAX:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.VENDOR_PAYMENT:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.VENDOR_ACTIVITY:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.VENDOR_ACTIVITYDETAIL:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.VENDOR_CATELOG:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.VENDOR_RISK:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.VENDOR_KYC:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.BCP_QUESION:
                    set_data.add(i.ref_type)
                if i.ref_type == VendorRefType.DUE_DELIGENCE:
                    set_data.add(i.ref_type)
        data_list = list(set_data)
        vlist = NWisefinList()
        ref_data = VendorRefType()
        for data in data_list:
            resp = ref_data.get_ref_data(data)
            vlist.append(resp)
        return HttpResponse(vlist.get(), content_type='application/json')
