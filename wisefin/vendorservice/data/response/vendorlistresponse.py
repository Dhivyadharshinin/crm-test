import json
import datetime

class VendorListData:
    id = None
    name = None
    panno = None
    gstno = None
    adhaarno = None
    emaildays = None
    branch_count = None
    director_count = None
    composite = None
    created_by = None
    created_date = None
    code =None
    comregno =None
    group = None
    custcategory_id = None
    classification = None
    type = None
    website =None
    activecontract = None
    nocontract_reason =None
    contractdate_from = None
    contractdate_to = None
    aproxspend = None
    actualspend = None
    orgtype = None
    renewal_date = None
    remarks = None
    requeststatus =None
    mainstatus = None
    rm_id = None
    vendor_status = None
    action = []
    isowner = False
    modify_ref_id = None
    modify_status = False
    description = None
    risktype = None
    risktype_description = None
    risk_mitigant = None
    risk_mitigant_review = None
    portal_flag = 0


    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def get_action(self):
        return self.action

    def set_action(self, action):
        self.action = action

    def get_isowner(self):
        return self.isowner

    def set_isowner(self, isowner):
        self.isowner = isowner

    def set_modify_ref_id(self,modify_ref_id):
        self.modify_ref_id=modify_ref_id

    def get_modify_ref_id(self):
        return self.modify_ref_id

    def set_modify_status(self,modify_status):
        self.modify_status=modify_status

    def get_modify_status(self):
        return self.modify_status

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name


    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_panno(self, panno):
        self.panno = panno
    def set_created_date(self, created_date):
        created_date = created_date.strftime("%m/%d/%Y, %H:%M:%S")

        self.created_date = created_date
    def set_updated_date(self, updated_date):
        if  self.updated_date !=None:
             updated_date=updated_date.strftime("%m/%d/%Y, %H:%M:%S")
        self.updated_date = updated_date

    def get_panno(self):
        return self.panno

    def set_gstno(self, gstno):
        self.gstno = gstno

    def get_gstno(self):
        return self.gstno

    def set_adhaarno(self, adhaarno):
        self.adhaarno = adhaarno

    def get_adhaarno(self):
        return self.adhaarno

    def set_emaildays(self, emaildays):
        self.emaildays = emaildays

    def get_emaildays(self):
        return self.emaildays

    def set_branch_count(self, branch_count):
        self.branch_count = branch_count

    def get_branch_count(self):
        return self.branch_count

    def set_director_count(self, director_count):
        self.director_count = director_count

    def get_director_count(self):
        return self.director_count

    def set_composite(self, composite):
        self.composite = composite

    def get_composite(self):
        return self.composite

    def set_created_by(self, created_by):
        self.created_by = created_by

    def get_created_by(self):
        return self.created_by


    def set_code(self, code):
        self.code = code

    def get_code(self):
        return self.code

    def set_comregno(self, comregno):
        self.comregno= comregno

    def get_comregno(self):
        return self.comregno

    def set_group(self, group):
        self.group = group

    def get_group(self):
        return self.group

    def set_custcategory_id(self, custcategory_id):
        self.custcategory_id = custcategory_id

    def get_custcategory_id(self):
        return self.custcategory_id

    def set_classification(self, classification):
        self.classification = classification

    def get_classification(self):
        return self.classification

    def set_type(self, type):
        self.type = type

    def get_type(self):
        return self.type

    def set_website(self, website):
        self.website = website

    def get_website(self):
        return self.website

    def set_activecontract(self, activecontract):
        self.activecontract = activecontract

    def get_activecontract(self):
        return self.activecontract

    def set_nocontract_reason(self, nocontract_reason):
        self.nocontract_reason = nocontract_reason

    def get_nocontract_reason(self):
        return self.nocontract_reason

    def set_contractdate_from(self, contractdate_from):
        contractdate_from = str(contractdate_from)
        self.contractdate_from = contractdate_from

    def get_contractdate_from(self):
        return self.contractdate_from

    def set_contractdate_to(self, contractdate_to):
        contractdate_to=str(contractdate_to)
        self.contractdate_to = contractdate_to

    def get_contractdate_to(self):
        return self.contractdate_to

    def set_aproxspend(self, aproxspend):
        self.aproxspend = aproxspend

    def get_aproxspend(self):
        return self.aproxspend

    def set_orgtype(self, orgtype):
        self.orgtype = orgtype

    def get_orgtype(self):
        return self.orgtype

    def set_renewal_date(self, renewal_date):
        renewal_date = str(renewal_date)
        self.renewal_date = renewal_date

    def get_renewal_date(self):
        return self.renewal_date

    def set_remarks(self, remarks):
        self.remarks = remarks

    def get_remarks(self):
        return self.remarks

    def set_requeststatus(self, requeststatus):
        self.requeststatus = requeststatus

    def get_requeststatus(self):
        return self.requeststatus

    def set_mainstatus(self, mainstatus):
        self.mainstatus = mainstatus

    def get_mainstatus(self):
        return self.mainstatus

    def set_rm_id(self, rm_id):
        self.rm_id = rm_id

    def get_rm_id(self):
        return self.rm_id


    def set_actualspend(self, actualspend):
        self.actualspend = actualspend

    def get_actualspend(self):
        return self.actualspend

    def set_description(self, description):
        self.description = description

    def get_description(self):
        return self.description

    def set_risktype(self, risktype):
        self.risktype = risktype

    def get_risktype(self):
        return self.risktype

    def set_risktype_description(self, risktype_description):
        self.risktype_description = risktype_description

    def get_risktype_description(self):
        return self.risktype_description

    def set_risk_mitigant(self, risk_mitigant):
        self.risk_mitigant = risk_mitigant

    def get_risk_mitigant(self):
        return self.risk_mitigant

    def set_risk_mitigant_review(self, risk_mitigant_review):
        self.risk_mitigant_review = risk_mitigant_review

    def get_risk_mitigant_review(self):
        return self.risk_mitigant_review

    def set_vendor_status(self, vendor_status ):
        if vendor_status == 0:
            action_arr = {"q_id":2,"q_status":"move to rm","reject_id":0,"reject_status": ""}
            self.set_action(action_arr)
        if vendor_status == 1:
            action_arr = {"q_id":2,"q_status":"move to rm","reject_id":0,"reject_status": ""}
            self.set_action(action_arr)
        if vendor_status == 2:
            action_arr = {"q_id":3,"q_status":"move to checker","reject_id":0,"reject_status": "reject"}
            self.set_action(action_arr)
        if vendor_status == 3:
            action_arr = {"q_id":4,"q_status":"move to header","reject_id":0,"reject_status": "reject"}
            self.set_action(action_arr)
        if vendor_status == 4:
            action_arr = {"q_id":5,"q_status":"approved","reject_id":0,"reject_status": "reject","requeststatus":self.requeststatus}
            self.set_action(action_arr)
        # else:
        #     action_arr = {"q_id": 5, "q_status": "approved", "reject_id": 0, "reject_status": "reject"}
        #     self.set_action(action_arr)

        if vendor_status == 5:
            action_arr = {"q_id":'',"q_status":'',"reject_id":'',"reject_status": ''}
            self.set_action(action_arr)

        if vendor_status == 6:
            action_arr = {"q_id":'',"q_status":'',"reject_id":'',"reject_status": ''}
            self.set_action(action_arr)

        if vendor_status == 7:
            action_arr = {"q_id": 2, "q_status": "move to rm", "reject_id": 0, "reject_status": ""}
            self.set_action(action_arr)

        if vendor_status == 8:
            action_arr = {"q_id": 8, "q_status": "move to compliance", "reject_id": 0, "reject_status": ""}
            self.set_action(action_arr)

        self.vendor_status= vendor_status

    def get_vendor_status(self):
        return self.vendor_status

    def set_portal_flag(self, portal_flag):
        self.portal_flag = portal_flag

    def get_portal_flag(self):
        return self.portal_flag


class VendorCheckListData:
    flag = False
    SupplierBranch = False
    SupplierTax = False
    SupplierPayment = False
    SupplierActivity = False
    ActivityDetail = False
    Catelog = False
    VendorSubContractor = False
    VendorClient = False
    SupplierProduct =False
    VendorDocument =False
    status =None
    Due_diligence = False
    BCP_quest = False
    Intermediary = False
    Category = None
    Composite = None
    Pan = False
    Gst = False
    Cancel_cheque = False
    Board_resolution = False
    Contract = False
    Due_questionnaire = False
    Bcp_questionnaire = False
    Kyc = False

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_SupplierBranch(self, SupplierBranch):
        self.SupplierBranch = SupplierBranch

    def set_SupplierTax(self, SupplierTax):
        self.SupplierTax = SupplierTax

    def set_SupplierPayment(self, SupplierPayment):
        self.SupplierPayment = SupplierPayment

    def set_SupplierActivity(self, SupplierActivity):
        self.SupplierActivity = SupplierActivity

    def set_ActivityDetail(self, ActivityDetail):
        self.ActivityDetail = ActivityDetail

    def set_Catelog(self, Catelog):
        self.Catelog = Catelog

    def set_VendorSubContractor(self, VendorSubContractor):
        self.VendorSubContractor = VendorSubContractor

    def set_VendorClient(self, VendorClient):
        self.VendorClient = VendorClient

    def set_SupplierProduct(self, SupplierProduct):
        self.SupplierProduct = SupplierProduct

    def set_VendorDocument(self, VendorDocument):
        self.VendorDocument = VendorDocument

    def set_status(self,status):
        self.status=status

    def get_status(self):
        return self.status

    def set_due_diligence(self, Due_diligence):
        self.Due_diligence = Due_diligence

    def set_bcp_questionary(self, BCP_quest):
        self.BCP_quest = BCP_quest

    def set_intermediary(self, Intermediary):
        self.Intermediary = Intermediary

    def set_customer_category(self, Category):
        self.Category = Category

    def set_flag(self, flag):
        self.flag = flag

    def set_composite(self, composite):
        self.Composite = composite

    def set_pan(self, pan):
        self.Pan = pan

    def set_gst(self, gst):
        self.Gst = gst

    def set_cancel_cheque(self, cancel_cheque):
        self.Cancel_cheque = cancel_cheque

    def set_broad_resolution(self, broad_resolution):
        self.Board_resolution = broad_resolution

    def set_contract(self, contract):
        self.Contract = contract

    def set_bcp_questions(self, bcp_question):
        self.Bcp_questionnaire = bcp_question

    def set_due_questions(self, due_question):
        self.Due_questionnaire = due_question

    def set_kyc(self, kyc):
        self.Kyc = kyc
