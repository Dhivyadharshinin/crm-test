import json


class VendorRequest:
    id = None
    name = None
    panno = None
    gstno = None
    adhaarno = None
    branch_count = None
    emaildays = 1
    director_count = 0
    composite = None
    created_by = None
    code = None
    comregno = None
    group = None
    custcategory_id = None
    classification = None
    type = None
    website = None
    activecontract = None
    nocontract_reason = None
    contractdate_from = None
    contractdate_to = None
    aproxspend = 0.0
    actualspend = 0.0
    orgtype = None
    renewal_date = None
    remarks = None
    requeststatus = None
    mainstatus = None
    rm_id = None
    vendor_status = None
    description = None
    risktype = None
    risktype_description = None
    risk_mitigant = None
    risk_mitigant_review = None
    portal_flag = 0

    def __init__(self, vendorObj):
        if 'id' in vendorObj:
            self.id = vendorObj['id']
        if 'code' in vendorObj:
            self.code = vendorObj['code']
        if 'name' in vendorObj:
            self.name = vendorObj['name']
        if 'panno' in vendorObj:
            self.panno = vendorObj['panno']
        if 'gstno' in vendorObj:
            self.gstno = vendorObj['gstno']
        if 'composite' in vendorObj:
            self.composite = vendorObj['composite']
        if 'adhaarno' in vendorObj:
            self.adhaarno = vendorObj['adhaarno']
        if 'emaildays' in vendorObj:
            self.emaildays = vendorObj['emaildays']
        if 'comregno' in vendorObj:
            self.comregno = vendorObj['comregno']
        if 'group' in vendorObj:
            self.group = vendorObj['group']
        if 'custcategory_id' in vendorObj:
            self.custcategory_id = vendorObj['custcategory_id']
        if 'classification' in vendorObj:
            self.classification = vendorObj['classification']
        if 'type' in vendorObj:
            self.type = vendorObj['type']
        if 'website' in vendorObj:
            self.website = vendorObj['website']
        if 'activecontract' in vendorObj:
            self.activecontract = vendorObj['activecontract']
        if 'nocontract_reason' in vendorObj:
            self.nocontract_reason = vendorObj['nocontract_reason']
        if 'contractdate_from' in vendorObj:
            self.contractdate_from = vendorObj['contractdate_from']
        if 'contractdate_to' in vendorObj:
            self.contractdate_to = vendorObj['contractdate_to']

        if 'aproxspend' in vendorObj:
            self.aproxspend = vendorObj['aproxspend']
        if 'actualspend' in vendorObj:
            self.actualspend = vendorObj['actualspend']
        if 'orgtype' in vendorObj:
            self.orgtype = vendorObj['orgtype']
        if 'renewal_date' in vendorObj:
            self.renewal_date = vendorObj['renewal_date']
        if 'branch_count' in vendorObj:
            self.branch_count = vendorObj['branch_count']
        if 'director_count' in vendorObj:
            self.director_count = vendorObj['director_count']
        if 'remarks' in vendorObj:
            self.remarks = vendorObj['remarks']
        if 'requeststatus' in vendorObj:
            self.requeststatus = vendorObj['requeststatus']
        if 'mainstatus' in vendorObj:
            self.mainstatus = vendorObj['mainstatus']
        if 'rm_id' in vendorObj:
            self.rm_id = vendorObj['rm_id']
        if 'vendor_status' in vendorObj:
            self.vendor_status = vendorObj['vendor_status']
        if 'description' in vendorObj:
            self.description = vendorObj['description']
        if 'risktype' in vendorObj:
            self.risktype = vendorObj['risktype']
        if 'risktype_description' in vendorObj:
            self.risktype_description = vendorObj['risktype_description']
        if 'risk_mitigant' in vendorObj:
            self.risk_mitigant = vendorObj['risk_mitigant']
        if 'risk_mitigant_review' in vendorObj:
            self.risk_mitigant_review = vendorObj['risk_mitigant_review']
        if 'portal_flag' in vendorObj:
            self.portal_flag = vendorObj['portal_flag']

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
        self.comregno = comregno

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
        contractdate_to = str(contractdate_to)
        self.contractdate_to = contractdate_to

    def get_contractdate_to(self):
        return self.contractdate_to

    def set_aproxspend(self, aproxspend):
        self.aproxspend = aproxspend

    def get_aproxspend(self):
        return self.aproxspend

    def set_orgtype(self, orgtype):
        self.website = orgtype

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

    def set_vendor_status(self, vendor_status):
        self.vendor_status = vendor_status

    def get_vendor_status(self):
        return self.vendor_status

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

    def get_portal_flag(self):
        return self.portal_flag

    def set_portal_flag(self, portal_flag):
        self.portal_flag = portal_flag


class VowVendorRequest:
    main_name = None
    pan_no = None
    gst_no = None
    rm_id = None
    rm_name = None
    created_by = None
    line_1 = None
    line_2 = None
    line_3 = None
    pincode_id = None
    city_id = None
    district_id = None
    state_id = None
    cont_name = None
    designation = None
    mobile_1 = None
    mobile_2 = None
    email = None
    activity_name = None
    activity_type = None
    product_name = None
    catelog_category = None
    catelog_subcategory = None

    def __init__(self, data_obj):
        if 'name' in data_obj:
            self.main_name = data_obj['name']
        if 'panno' in data_obj:
            self.pan_no = data_obj['panno']
        if 'gstno' in data_obj:
            self.gst_no = data_obj['gstno']
        if 'rm_id' in data_obj:
            rm = data_obj['rm_id']
            if 'id' in rm:
                self.rm_id = rm['id']
            if 'name' in rm:
                self.rm_name = rm['name']
        if 'created_by' in data_obj:
            self.created_by = data_obj['created_by']
        if 'address' in data_obj:
            address_data = data_obj['address']
            if 'line_1' in address_data:
                self.line_1 = address_data['line_1']
            if 'line_2' in address_data:
                self.line_2 = address_data['line_2']
            if 'line_3' in address_data:
                self.line_3 = address_data['line_3']
            if 'pincode_id' in address_data:
                self.pincode_id = address_data['pincode_id']
            if 'city_id' in address_data:
                self.city_id = address_data['city_id']
            if 'district_id' in address_data:
                self.district_id = address_data['district_id']
            if 'state_id' in address_data:
                self.state_id = address_data['state_id']
        if 'contact' in data_obj:
            contact_data = data_obj['contact']
            if 'name' in contact_data:
                self.cont_name = contact_data['name']
            if 'designation' in contact_data:
                self.designation = contact_data['designation']
            if 'mobile_1' in contact_data:
                self.mobile_1 = contact_data['mobile_1']
            if 'mobile_2' in contact_data:
                self.mobile_2 = contact_data['mobile_2']
            if 'email' in contact_data:
                self.email = contact_data['email']
        if 'activity' in data_obj:
            activity_data = data_obj['activity']
            if 'name' in activity_data:
                self.activity_name = activity_data['name']
            if 'type' in activity_data:
                self.activity_type = activity_data['type']
        if 'catelog' in data_obj:
            catelog_data = data_obj['catelog']
            if 'product_name' in catelog_data:
                self.product_name = catelog_data['product_name']
            if 'catelog_category' in catelog_data:
                self.catelog_category = catelog_data['catelog_category']
            if 'catelog_subcategory' in catelog_data:
                self.catelog_subcategory = catelog_data['catelog_subcategory']

    def get_main_name(self):
        return self.main_name

    def get_pan_no(self):
        return self.pan_no

    def get_gst_no(self):
        return self.gst_no

    def get_line_1(self):
        return self.line_1

    def get_line_2(self):
        return self.line_2

    def get_line_3(self):
        return self.line_3

    def get_pincode_id(self):
        return self.pincode_id

    def get_city_id(self):
        return self.city_id

    def get_district_id(self):
        return self.district_id

    def get_state_id(self):
        return self.state_id

    def get_cont_name(self):
        return self.cont_name

    def get_designation(self):
        return self.designation

    def get_mobile_1(self):
        return self.mobile_1

    def get_mobile_2(self):
        return self.mobile_2

    def get_email(self):
        return self.email

    def get_created_by(self):
        return self.created_by

    def get_rm_id(self):
        return self.rm_id

    def get_rm_name(self):
        return self.rm_name

    def get_activity_name(self):
        return self.activity_name

    def get_activity_type(self):
        return self.activity_type

    def get_product_name(self):
        return self.product_name

    def get_catelog_category(self):
        return self.catelog_category

    def get_catelog_subcategory(self):
        return self.catelog_subcategory


class VowActivityRequest:
    activity_name = None
    activity_type = None
    product_name = None
    catelog_category = None
    catelog_subcategory = None

    def __init__(self, data_obj):
        if 'activity' in data_obj:
            activity_data = data_obj['activity']
            if 'name' in activity_data:
                self.activity_name = activity_data['name']
            if 'type' in activity_data:
                self.activity_type = activity_data['type']
        if 'catelog' in data_obj:
            catelog_data = data_obj['catelog']
            if 'product_name' in catelog_data:
                self.product_name = catelog_data['product_name']
            if 'catelog_category' in catelog_data:
                self.catelog_category = catelog_data['catelog_category']
            if 'catelog_subcategory' in catelog_data:
                self.catelog_subcategory = catelog_data['catelog_subcategory']

    def get_activity_name(self):
        return self.activity_name

    def get_activity_type(self):
        return self.activity_type

    def get_product_name(self):
        return self.product_name

    def get_catelog_category(self):
        return self.catelog_category

    def get_catelog_subcategory(self):
        return self.catelog_subcategory
