import json
from faservice.util.fautil import get_sourcetype

class AssetSaleResponse:
    id = None
    oldvalue = None
    assetvalue = None
    assetvalue_status = None
    reason = None
    assetvalue_date = None
    capdate = None
    assetdetails_id = None
    assetdtls_id = None
    branch_id = None
    branch_name = None
    assetdetails_status = None
    assetdetails_value = None
    assetcat_subcatname = None
    barcode = None

    request_for = None
    requeststatus = None
    cost_total = None
    value_total = None
    location_id = None
    location = None
    newvalue = None
    approval_flag = None
    product_name=None
    assetcat_id=None
    assetbranch_from=None
    assetbranch_to=None
    hsn_details=None
    status=None
    cb_value=None
    end_date=None
    last_dep_rundate=None
    depreciation_value=None
    assetsale_amount=None
    assetsale_status=None
    customer_name=None
    customer_details=None
    gst_details=None

    sgst = None
    cgst = None
    igst = None
    hsncode= None
    assetsaleheader_id= None






    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_oldvalue(self, oldvalue):
        self.oldvalue = str(oldvalue)
    def set_assetvalue(self,assetvalue):
        self.assetvalue = str(assetvalue)
    def set_assetvalue_status(self,assetvalue_status):
        self.assetvalue_status = assetvalue_status
    def set_reason(self,reason):
        self.reason = reason
    def set_assetvalue_date(self,assetvalue_date):
        self.assetvalue_date = str(assetvalue_date.date())
    def set_capdate(self,capdate):
        self.capdate = str(capdate)
    def set_assetdetails_id(self,assetdetails_id):
        self.assetdetails_id = assetdetails_id
    def set_assetdtls_id(self,assetdtls_id):
        self.assetdtls_id = assetdtls_id
    def set_assetdetails_status(self,assetdetails_status):
        self.assetdetails_status = assetdetails_status
    def set_assetdetails_value(self,assetdetails_value):
        self.assetdetails_value = str(assetdetails_value)
    def set_branch_id(self, branch_id):
        self.branch_id = branch_id
    def set_branch_name(self, branch_name):
        self.branch_name = branch_name
    def set_assetcat_subcatname(self, assetcat_subcatname):
        self.assetcat_subcatname = assetcat_subcatname
    def set_assetcat_id(self, assetcat_id):
        self.assetcat_id = assetcat_id

    def set_request_for(self, request_for):
        self.request_for = request_for
    def set_request_status(self, request_status):
        self.request_status = request_status
    def set_cost_total(self, cost_total):
        self.cost_total = str(cost_total)
    def set_value_total(self, value_total):
        self.value_total = str(value_total)
    def set_location(self, location):
        self.location = location
    def set_location_id(self, location_id):
        self.location_id = location_id
    def set_barcode(self, barcode):
        self.barcode = barcode
    def set_newvalue(self, newvalue):
        self.newvalue = newvalue
    def set_approval_flage(self, approval_flag):
        self.approval_flag = approval_flag

    def set_product_name(self, product_name):
        self.product_name = product_name
    def set_status(self, status):
        self.status = status


    def set_hsn_details(self, hsn_details):
        self.hsn_details = hsn_details

    def set_assetbranch_from(self, assetbranch_from):
        self.assetbranch_from = assetbranch_from
    def set_assetbranch_to(self, assetbranch_to):
        self.assetbranch_to = assetbranch_to

    def set_cb_value(self, cb_value):
        self.cb_value = str(cb_value)

    def set_depreciation_value(self, depreciation_value):
        self.depreciation_value = depreciation_value

    def set_assetsale_amount(self, assetsale_amount):
        self.assetsale_amount = str(assetsale_amount)

    def set_assetsale_status(self, assetsale_status):
        self.assetsale_status = assetsale_status

    def set_end_date(self, end_date):
        self.end_date = str(end_date.date())
    def set_last_dep_rundate(self, last_dep_rundate):
        self.last_dep_rundate = last_dep_rundate


    def set_customer_name(self, customer_name):
        self.customer_name = customer_name
    def set_assetsale_date(self, assetsale_date):
        self.assetsale_date = str(assetsale_date)



    def set_customer_details(self, customer_details):
        self.customer_details =customer_details

    def set_gst_details(self, gst_details):
        self.gst_details =gst_details






    def set_sgst(self, sgst):
        self.sgst = str(sgst)
    def set_cgst(self, cgst):
        self.cgst = str(cgst)
    def set_igst(self, igst):
        self.igst =str(igst)
    def set_hsncode(self, hsncode):
        self.hsncode =hsncode


    def set_assetsaleheader_id(self, assetsaleheader_id):
        self.assetsaleheader_id =assetsaleheader_id






