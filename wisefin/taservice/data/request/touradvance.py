import json
from taservice.util.ta_util import Status,Onbehalfof,App_type


class TourAdvanceRequest:
    id = None
    tourgid = None
    reason = None
    reqamount = None
    appamount = reqamount
    invoiceheadergid = None
    status = Status.PENDING
    onbehalfof = Onbehalfof.ZERO
    # apptype = App_type.ADVANCE
    approval = None
    remarks = None
    tour_id = None

    def __init__(self, tour_obj):
        if 'id' in tour_obj:
            self.id = tour_obj['id']
        if 'tourgid' in tour_obj:
            self.tourgid = tour_obj['tourgid']
        if 'reason' in tour_obj:
            self.reason = tour_obj['reason']
        if 'reqamount' in tour_obj:
            self.reqamount = tour_obj['reqamount']
        if 'appamount' in tour_obj:
            self.appamount = tour_obj['appamount']
        if 'invoiceheadergid' in tour_obj:
            self.invoiceheadergid = tour_obj['invoiceheadergid']
        if 'status' in tour_obj:
            self.status = tour_obj['status']
        if 'onbehalfof' in tour_obj:
            self.onbehalfof = tour_obj['onbehalfof']
        if 'apptype' in tour_obj:
            self.apptype = tour_obj['apptype']
        if 'approval' in tour_obj:
            self.approval = tour_obj['approval']
        if 'remarks' in tour_obj:
            self.remarks = tour_obj['remarks']
        if 'tour_id' in tour_obj:
            self.tour_id = tour_obj['tour_id']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_tourgid(self, tourgid):
        self.tourgid = tourgid

    def set_reason(self, reason):
        self.reason = reason

    def set_reqamount(self, reqamount):
        self.reqamount = reqamount

    def set_appamount(self, appamount):
        self.appamount = appamount

    def set_invoiceheadergid(self, invoiceheadergid):
        self.invoiceheadergid = invoiceheadergid

    def set_status(self, status):
        self.status = status

    def set_onbehalfof(self, onbehalfof):
        self.onbehalfof = onbehalfof

    def set_approval(self, approval):
        self.approval = approval

    def set_apptype(self, apptype):
        self.apptype = apptype

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_tour_id(self, tour_id):
        self.tour_id = tour_id

    def get_id(self):
        return self.id

    def get_tourgid(self):
        return self.tourgid

    def get_reason(self):
        return self.reason

    def get_reqamount(self):
        return self.reqamount

    def get_appamount(self):
        return self.appamount

    def get_invoiceheadergid(self):
        return self.invoiceheadergid

    def get_status(self):
        return self.status

    def get_onbehalfof(self):
        if self.onbehalfof >0:
            return self.onbehalfof
        else:
            return 0

    def get_apptype(self):
        return self.apptype

    def get_approval(self):
        return self.approval

    def get_remarks(self):
        return self.remarks

    def get_tour_id(self):
        return self.tour_id


class Advance_Request:
    adjustamount = None
    invoiceheadergid = None
    ppx_headergid = None
    crnno = None
    debit_categorygid = None
    debit_subcategorygid = None

    def __init__(self, tour_obj):
        if 'adjustamount' in tour_obj:
            self.adjustamount = tour_obj['adjustamount']
        if 'invoiceheadergid' in tour_obj:
            self.invoiceheadergid = tour_obj['invoiceheadergid']
        if 'ppx_headergid' in tour_obj:
            self.ppx_headergid = tour_obj['ppx_headergid']
        if 'crnno' in tour_obj:
            self.crnno = tour_obj['crnno']
        if 'debit_categorygid' in tour_obj:
            self.debit_categorygid = tour_obj['debit_categorygid']
        if 'debit_subcategorygid' in tour_obj:
            self.debit_subcategorygid = tour_obj['debit_subcategorygid']

class Ecf_data_req:
    id = None
    tourgid = None
    type = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


    def __init__(self, tour_obj):
        if 'id' in tour_obj:
            self.id = tour_obj['id']
        if 'tourgid' in tour_obj:
            self.tourgid = tour_obj['tourgid']
        if 'type' in tour_obj:
            self.type = tour_obj['type']
