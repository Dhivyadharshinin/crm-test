import json

from faservice.util.fautil import dictdefault, assetvaluedtl_status


class AssetDetailsResponse:
    id = assetdetails_id = qty = barcode = date = assetgroup_id = product_id = cat = subcat = \
        assetdetails_value = assetdetails_cost = description = capdate = source = assetdetails_status = \
        requestfor = requeststatus = assettfr_id = assetsale_id = not5k = assetowner = lease_startdate = \
        lease_enddate = impairasset_id = impairasset = writeoff_id = assetvalue_id = assetcapdate_id = \
        assetsplit_id = assetmerge_id = assetcatchangedate = reducedvalue = branch_id = assetlocation_id = \
        assetdetails_bs = assetdetails_cc = deponhold = deprate = enddate = parent_id = assetserialno = \
        invoice_id = faclringdetails_id = inwheader_id = inwdetail_id = inwarddate = mepno = ponum = \
        crnum = debit_id = imagepath = vendorname = assetheader_id = expanded = product_name = assetcat = assetlocation = \
        reason = new_cap_date = CP_status = count = createdate = branch_code = branch_name = asset_tag = make = \
        serial_no = condition = status = remarks =apcat=valuetot=costtot= None

    def get(self):
        return json.dumps(self, default=dictdefault)

    def set_id(self, id):
        self.id = id

    def set_expanded(self, expanded):
        self.expanded = expanded

    def set_assetheader_id(self, assetheader_id):
        self.assetheader_id = assetheader_id

    def set_costtot(self, cost):
        self.costtot = cost
    def set_valuetot(self, valuetot):
        self.valuetot = valuetot
    def set_assetcount(self, data):
        self.count = data

    def set_assetdetails_id(self, assetdetails_id):
        self.assetdetails_id = str(assetdetails_id)

    def set_qty(self, qty):
        self.qty = qty

    def set_barcode(self, barcode):
        self.barcode = barcode

    def set_date(self, date):
        self.date = str(date)

    def set_assetgroup_id(self, assetgroup_id):
        self.assetgroup_id = str(assetgroup_id)

    def set_product_id(self, product_id):
        self.product_id = product_id

    def set_product_name(self, product_name):
        self.product_id = product_name

    def set_cat(self, cat):
        self.cat = cat
    def set_apcat(self, apcat):
        self.apcat = apcat

    def set_subcat(self, subcat):
        self.subcat = subcat

    def set_assetdetails_value(self, assetdetails_value):
        self.assetdetails_value = str(assetdetails_value)

    def set_assetdetails_cost(self, assetdetails_cost):
        self.assetdetails_cost = str(assetdetails_cost)

    def set_description(self, description):
        self.description = description

    def set_asset_tag(self, asset_tag):
        self.asset_tag = asset_tag

    def set_make(self, make):
        self.make = make

    def set_serial_no(self, serial_no):
        self.serial_no = serial_no

    def set_condition(self, condition):
        self.condition = condition

    def set_status(self, status):
        self.status = status

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_capdate(self, capdate):
        self.capdate = str(capdate)

    def set_source(self, source):
        self.source = source

    def set_assetdetails_status(self, assetdetails_status):
        self.assetdetails_status = assetdetails_status

    def set_requestfor(self, requestfor):
        self.requestfor = requestfor

    def set_requeststatus(self, requeststatus):
        self.requeststatus = requeststatus

    def set_assettfr_id(self, assettfr_id):
        self.assettfr_id = assettfr_id

    def set_assetsale_id(self, assetsale_id):
        self.assetsale_id = assetsale_id

    def set_not5k(self, not5k):
        self.not5k = not5k

    def set_assetowner(self, assetowner):
        self.assetowner = assetowner

    def set_lease_startdate(self, lease_startdate):
        self.lease_startdate = lease_startdate

    def set_lease_enddate(self, lease_enddate):
        self.lease_enddate = lease_enddate

    def set_impairasset_id(self, impairasset_id):
        self.impairasset_id = impairasset_id

    def set_impairasset(self, impairasset):
        self.impairasset = impairasset

    def set_writeoff_id(self, writeoff_id):
        self.writeoff_id = writeoff_id

    def set_assetcatchange_id(self, assetcatchange_id):
        self.assetcatchange_id = assetcatchange_id

    def set_assetvalue_id(self, assetvalue_id):
        self.assetvalue_id = assetvalue_id

    def set_assetcapdate_id(self, assetcapdate_id):
        self.assetcapdate_id = assetcapdate_id

    def set_assetsplit_id(self, assetsplit_id):
        self.assetsplit_id = assetsplit_id

    def set_assetmerge_id(self, assetmerge_id):
        self.assetmerge_id = assetmerge_id

    def set_assetcatchangedate(self, assetcatchangedate):
        self.assetcatchangedate = assetcatchangedate

    def set_reducedvalue(self, reducedvalue):
        self.reducedvalue = reducedvalue

    def set_branch_id(self, branch_id):
        self.branch_id = branch_id

    def set_branch_code(self, branch_code):
        self.branch_code = branch_code

    def set_branch_name(self, branch_name):
        self.branch_name = branch_name

    def set_assetlocation_id(self, assetlocation_id):
        self.assetlocation_id = assetlocation_id

    def set_assetdetails_bs(self, assetdetails_bs):
        self.assetdetails_bs = assetdetails_bs

    def set_assetdetails_cc(self, assetdetails_cc):
        self.assetdetails_cc = assetdetails_cc

    def set_deponhold(self, deponhold):
        self.deponhold = deponhold

    def set_deprate(self, deprate):
        self.deprate = deprate

    def set_enddate(self, enddate):
        self.enddate = str(enddate)

    def set_parent_id(self, parent_id):
        self.parent_id = parent_id

    def set_assetserialno(self, assetserialno):
        self.assetserialno = assetserialno

    def set_invoice_id(self, invoice_id):
        self.invoice_id = invoice_id

    def set_faclringdetails_id(self, faclringdetails_id):
        self.faclringdetails_id = faclringdetails_id

    def set_inwheader_id(self, inwheader_id):
        self.inwheader_id = inwheader_id

    def set_inwdetail_id(self, inwdetail_id):
        self.inwdetail_id = inwdetail_id

    def set_inwarddate(self, inwarddate):
        self.inwarddate = inwarddate

    def set_mepno(self, mepno):
        self.mepno = mepno

    def set_ponum(self, ponum):
        self.ponum = ponum

    def set_crnum(self, crnum):
        self.crnum = crnum

    def set_debit_id(self, debit_id):
        self.debit_id = debit_id

    def set_imagepath(self, imagepath):
        self.imagepath = imagepath

    def set_vendorname(self, vendorname):
        self.vendorname = vendorname

    def set_writeoff_status(self, writeoff_status):
        self.writeoff_status = writeoff_status

    def set_writeoff_reason(self, writeoff_reason):
        self.writeoff_reason = writeoff_reason

    def set_checkbox(self, checkbox):
        self.checkbox = checkbox

    def set_new_cap_date(self, data):
        self.new_cap_date = data

    def set_assetlocation(self, location):
        self.assetlocation = location

    def set_CP_status(self, status):
        self.CP_status = status

    def set_reason(self, reason):
        self.reason = reason

    def set_assetcat(self, assetcat):
        self.assetcat = assetcat

    def set_create_date(self, createdate):
        self.createdate = createdate

    def set_itcatname(self, itcatname):
        self.itcatname = itcatname


class Totalcount:
    cap_count = writeoff_count = impair_count = assetvalue_count = merge_count = transfer_count = \
        split_count = cat_count = sale_count = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def writeoff_count(self, writeoff_count):
        self.writeoff_count = writeoff_count

    def cap_count(self, cap_count):
        self.cap_count = cap_count

    def impair_count(self, impair_count):
        self.impair_count = impair_count

    def assetvalue_count(self, assetvalue_count):
        self.assetvalue_count = assetvalue_count

    def merge_count(self, merge_count):
        self.merge_count = merge_count

    def transfer_count(self, transfer_count):
        self.transfer_count = str(transfer_count)

    def set_product_id(self, split_count):
        self.split_count = split_count

    def split_count(self, split_count):
        self.split_count = split_count

    def cat_count(self, cat_count):
        self.cat_count = cat_count

    def sale_count(self, sale_count):
        self.sale_count = sale_count
class FapvRespon:
    id = emp_name  = barcode=status=None
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def set_id(self, id):
        self.id = id

    def set_emp_name(self, emp_ename):
        self.emp_name = emp_ename

    def set_barcode(self, barcode):
        self.barcode = barcode

    def set_status(self, status):
        self.status = status

    def set_product_name(self, product_name):
        self.product_name = product_name

    def set_from_date(self, from_date):
        self.from_date = str(from_date)  if from_date !=None else ''

    def set_to_date(self, to_date):
        self.to_date = str(to_date) if to_date !=None else ''