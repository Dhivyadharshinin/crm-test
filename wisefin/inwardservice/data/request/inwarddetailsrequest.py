import json

class DetailsRequest:
    id = None
    packetno = None
    doctype_id = 0
    count = 0
    remarks = None
    inwardheader_id = None
    escalationtype_id = None
    escalationsubtype_id = None
    product_category=None
    product_subcategory=None
    update_key = None
    doccount = None
    docnumber = None
    docsubject = None
    pagecount = None
    receivedfrom = None
    docstatus = None
    status = None
    assigndept_id = None
    assignemployee_id = None
    actiontype = None
    tenor = None
    bulk = None
    docaction = None
    rmucode = None
    assignremarks = None

    def __init__(self, details_obj):
        if 'id' in details_obj:
            self.id = details_obj['id']
        if 'packetno' in details_obj:
            self.packetno = details_obj['packetno']
        if 'doctype_id' in details_obj:
            self.doctype = details_obj['doctype_id']
        if 'count' in details_obj:
            self.count = details_obj['count']
        if 'remarks' in details_obj:
            self.remarks = details_obj['remarks']
        if 'inwardheader_id' in details_obj:
            self.inwardheader_id = details_obj['inwardheader_id']
        if 'escalationtype_id' in details_obj:
            self.escalationtype_id = details_obj['escalationtype_id']
        if 'escalationsubtype_id' in details_obj:
            self.escalationsubtype_id = details_obj['escalationsubtype_id']
        if 'product_category' in details_obj:
            self.product_category = details_obj['product_category']
        if 'product_subcategory' in details_obj:
            self.product_subcategory = details_obj['product_subcategory']
        if 'update_key' in details_obj:
            self.update_key = details_obj['update_key']
        if 'doccount' in details_obj:
            self.doccount = details_obj['doccount']
        if 'docnumber' in details_obj:
            self.docnumber = details_obj['docnumber']
        if 'docsubject' in details_obj:
            self.docsubject = details_obj['docsubject']
        if 'pagecount' in details_obj:
            self.pagecount = details_obj['pagecount']
        if 'receivedfrom' in details_obj:
            self.receivedfrom = details_obj['receivedfrom']
        if 'docstatus' in details_obj:
            self.docstatus = details_obj['docstatus']
        if 'status' in details_obj:
            self.status = details_obj['status']
        if 'assigndept_id' in details_obj:
            self.assigndept = details_obj['assigndept_id']
        if 'assignemployee_id' in details_obj:
            self.assignemployee = details_obj['assignemployee_id']
        if 'actiontype' in details_obj:
            self.actiontype = details_obj['actiontype']
        if 'tenor' in details_obj:
            self.tenor = details_obj['tenor']
        if 'docaction' in details_obj:
            self.docaction = details_obj['docaction']
        if 'rmucode' in details_obj:
            self.rmucode = details_obj['rmucode']
        if 'assignremarks' in details_obj:
            self.assignremarks = details_obj['assignremarks']

        if 'bulk' in details_obj:
            self.bulk = details_obj['bulk']


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_id(self):
        return self.id

    def get_packetno(self):
        return self.packetno

    def get_doctype(self):
        return self.doctype

    def get_count(self):
        return self.count

    def get_remarks(self):
        return self.remarks

    def get_inwardheader_id(self):
        return self.inwardheader_id

    def get_escalationtype_id(self):
        return self.escalationtype_id

    def get_escalationsubtype_id(self):
        return self.escalationsubtype_id

    def get_product_subcategory(self):
        return self.product_subcategory

    def get_product_category(self):
        return self.product_subcategory

    def get_assignremarks(self):
        return self.assignremarks
    #
    # def get_inwardfrom(self):
    #     return self.inwardfrom
    #
    # def get_receivedby(self):
    #     return self.receivedby

    def get_doccount(self):
        return self.doccount
    def get_docnumber(self):
        return self.docnumber
    def get_docsubject(self):
        return self.docsubject
    def get_pagecount(self):
        return self.pagecount
    def get_receivedfrom(self):
        return self.receivedfrom
    def get_docstatus(self):
        return self.docstatus
    def get_status(self):
        return self.status
    def get_assigndept(self):
        return self.assigndept
    def get_assignemployee(self):
        return self.assignemployee
    def get_actiontype(self):
        return self.actiontype
    def get_tenor(self):
        return self.tenor
    def get_docaction(self):
        return self.docaction
    def get_rmucode(self):
        return self.rmucode
    def get_bulk(self):
        return self.bulk