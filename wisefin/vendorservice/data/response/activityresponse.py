import  json

from vendorservice.util.vendorutil import getGroup


class ActivityResponse:
    id = None
    type = None
    name = None
    description = None
    branch = None
    start_date = None
    end_date = None
    contract_spend = None
    rm = None
    fidelity = None
    bidding = None
    reason = None
    status = None
    contact = None
    activity_status = None
    created_by =None
    modify_ref_id = None
    modify_status = None
    portal_flag = 0
    rel_type = None
    activity_id = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_type(self, type):
        self.type = type

    def set_name(self, name):
        self.name = name

    def set_description(self, description):
        self.description = description

    def set_branch(self, branch):
        self.branch = branch

    def set_contact(self, contact):
        self.contact_id = contact

    def set_enddate(self, end_date):
        end_date=str(end_date)
        self.end_date = end_date

    def set_startdate(self, start_date):
        start_date=str(start_date)
        self.start_date = start_date

    def set_contractspend(self, contract_spend):
        self.contract_spend = contract_spend

    def set_rm(self, rm):
        self.rm = rm

    def set_fidelity(self, fidelity):
        self.fidelity = fidelity

    def set_bidding(self, bidding):
        self.bidding = bidding

    def set_reason(self, reason):
        self.type = reason

    def set_status(self, status):
        self.status = status

    def set_activity_status(self,activity_status):
        self.activity_status=activity_status

    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_modify_ref_id(self, modify_ref_id):
        self.modify_ref_id = modify_ref_id

    def set_modify_status(self, modify_status):
        self.modify_status = modify_status

    def set_rel_type(self, rel_type):
        rel_type_val = getGroup(rel_type)
        self.rel_type = rel_type_val

    def set_activity(self, activity_id,arr):
        self.activity_id = None
        for i in arr:
            if i.id == activity_id:
                self.activity_id = i
                break

    def set_activity_id(self, activity_id):
        self.activity_id = activity_id

    def set_Activity(self, Activity):
        self.Activity = Activity


    def get_id(self):
        return self.id

    def get_type(self):
        return self.type

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description

    def get_branch(self):
        return self.branch

    def get_startdate(self):
        return self.start_date

    def get_enddate(self):
        return self.end_date

    def get_contractspend(self):
        return self.contract_spend

    def get_rm(self):
        return self.rm

    def get_fidelity(self):
        return self.fidelity

    def get_bidding(self):
        return self.bidding

    def get_reason(self):
        return self.reason

    def get_activity_status(self):
        return self.activity_status

    def get_contact(self):
        return self.contact_id

    def set_portal_flag(self, portal_flag):
        self.portal_flag = portal_flag

    def get_portal_flag(self):
        return self.portal_flag

    def get_rel_type(self):
        return self.rel_type

    def get_activity_id(self):
        return self.activity_id

class VendorActivityDetails:
    id = None
    activity_id_id = None
    name = None
    detailname = None
    raisor = None
    approver = None
    remarks = None
    created_by =None
    modify_ref_id = None
    modify_status = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_activity_id_id(self, activity_id_id):
        self.activity_id_id = activity_id_id

    def set_name(self, name):
        self.name = name

    def set_detailname(self, detailname):
        self.detailname = detailname

    def set_raisor(self, raisor):
        self.raisor = raisor

    def set_approver(self, approver):
        self.approver = approver

    def set_remarks(self,remarks):
        self.remarks=remarks

    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_modify_ref_id(self, modify_ref_id):
        self.modify_ref_id = modify_ref_id

    def set_modify_status(self, modify_status):
        self.modify_status = modify_status

    def get_id(self):
        return self.id

    def get_activity_id_id(self):
        return self.activity_id_id

    def get_name(self):
        return self.name

    def get_detailname(self):
        return self.detailname

    def get_raisor(self):
        return self.raisor

    def get_approver(self):
        return self.approver

    def get_remarks(self):
        return self.remarks


class VendorCatalog:
    id = None
    activitydetail_id = None
    detailname = None
    productname = None
    category = None
    subcategory = None
    name = None
    specification = None
    size = None
    remarks = None
    uom = None
    unitprice = None
    fromdate = None
    todate = None
    packing_price = None
    delivery_date = None
    capacity = None
    direct_to = None
    created_by =None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_activitydetail_id(self, activitydetail_id):
        self.activitydetail_id = activitydetail_id

    def set_detailname(self, detailname):
        self.detailname = detailname

    def set_productname(self, productname):
        self.productname = productname

    def set_category(self, category):
        self.category = category

    def set_subcategory(self, subcategory):
        self.subcategory = subcategory

    def set_name(self,name):
        self.name=name

    def set_specification(self,specification):
        self.specification=specification

    def set_size(self,size):
        self.size=size

    def set_remarks(self,remarks):
        self.remarks=remarks

    def set_uom(self,uom):
        self.uom=uom

    def set_unitprice(self,unitprice):
        self.unitprice=unitprice

    def set_fromdate(self,fromdate):
        fromdate=str(fromdate)
        self.fromdate=fromdate

    def set_todate(self,todate):
        todate=str(todate)
        self.todate=todate

    def set_packing_price(self,packing_price):
        self.packing_price=packing_price

    def set_delivery_date(self,delivery_date):
        self.delivery_date=delivery_date

    def set_capacity(self,capacity):
        self.capacity=capacity

    def set_direct_to(self,direct_to):
        self.direct_to=direct_to

    def set_created_by(self, created_by):
        self.created_by = created_by

    def get_id(self):
        return self.id

    def get_activitydetail_id(self):
        return self.activitydetail_id

    def get_detailname(self):
        return self.detailname

    def get_productname(self):
        return self.productname

    def get_category(self):
        return self.category

    def get_subcategory(self):
        return self.subcategory

    def get_name(self):
        return self.name

    def get_specification(self):
        return self.specification

    def get_size(self):
        return self.size

    def get_remarks(self):
        return self.remarks

    def get_uom(self):
        return self.uom

    def get_unitprice(self):
        return self.unitprice

    def get_fromdate(self):
        return self.fromdate

    def get_todate(self):
        return self.todate

    def get_packing_price(self):
        return self.packing_price

    def get_delivery_date(self):
        return self.delivery_date

    def get_capacity(self):
        return self.capacity

    def get_direct_to(self):
        return self.direct_to