import json


class DetailsResponse:
    id = None
    packetno = None
    doctype = None
    doctype_id = None
    count = None
    remarks = None
    inwardheader = None
    inwardheader_id = None
    escalationtype = None
    escalationsubtype = None
    product_category=None
    product_subcategory=None
    status = None
    docstatus = None
    doccount = None
    docnumber = None
    docsubject = None
    pagecount = None
    receivedfrom = None
    assigndept = None
    assigndept_id = None
    assignemployee = None
    assignemployee_id = None
    actiontype = None
    tenor = None
    docaction = None
    rmucode = None
    branch = None
    branch_id = None
    no = None
    date = None
    channel = None
    channel_id = None
    courier = None
    courier_id = None
    awbno = None
    noofpockets = None
    file_data = None
    assignremarks = None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_packetno(self, packetno):
        self.packetno = packetno

    def set_doctype(self, doctype):
        self.doctype = doctype

    def set_doctype_id(self, doctype_id, arr):
        if doctype_id != None:
            for i in arr:
                if i['id'] == doctype_id:
                    self.doctype_id = i
                    break

    def set_doccount(self, doccount):
        self.doccount = doccount

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_inwardheader(self, inwardheader):
        self.inwardheader = inwardheader

    def set_inwardheader_id(self, inwardheader_id):
        self.inwardheader_id = inwardheader_id

    def set_escalationtype(self, escalationtype):
        self.escalationtype = escalationtype

    def set_escalationsubtype(self, escalationsubtype):
        self.escalationsubtype = escalationsubtype

    def set_product_category(self, product_category):
        self.product_category = product_category

    def set_product_subcategory(self, product_subcategory):
        self.product_subcategory = product_subcategory

    def set_attachment(self, attachment):
        self.attachment = attachment

    def set_no(self, no):
        self.no = no

    def set_date(self, date):
        date = str(date)
        self.date = date

    def set_channel(self, channel):
        self.channel = channel

    def set_channel_id(self, channel_id, arr):
        if channel_id != None:
            for i in arr:
                if i['id'] == channel_id:
                    self.channel_id = i
                    break

    def set_courier(self, courier):
        self.courier = courier

    def set_courier_id(self, courier_id, arr):
        if courier_id != None:
            for i in arr:
                if i['id'] == courier_id:
                    self.courier_id = i
                    break

    def set_awbno(self, awbno):
        self.awbno = awbno

    def set_actiontype(self, actiontype):
        self.actiontype = actiontype

    def set_noofpockets(self, noofpockets):
        self.noofpockets = noofpockets

    def set_assignemployee(self, assignemployee):
        self.assignemployee = assignemployee

    def set_assignemployee_id(self, assignemployee_id, arr):
        if assignemployee_id != None:
            for i in arr:
                if i['id'] == assignemployee_id:
                    self.assignemployee_id = i
                    break

    def set_assigndept(self, assigndept):
        self.assigndept = assigndept

    def set_assigndept_id(self, assigndept_id, arr):
        if assigndept_id != None:
            for i in arr:
                if i['id'] == assigndept_id:
                    self.assigndept_id = i
                    break

    def set_docnumber(self, docnumber):
        self.docnumber = docnumber

    def set_receivedfrom(self, receivedfrom):
        self.receivedfrom = receivedfrom


    def set_tenor(self, tenor):
        self.tenor = tenor

    def set_status(self, status):
        self.status = status

    def set_docstatus(self, docstatus):
        self.docstatus = docstatus

    def set_docaction(self, docaction):
        self.docaction = docaction

    def set_rmucode(self, rmucode):
        self.rmucode = rmucode

    def set_branch(self, branch):
        self.branch = branch

    def set_branch_id(self, branch_id, arr):
        if branch_id != None:
            for i in arr:
                if i['id'] == branch_id:
                    self.branch_id = i
                    break

    def set_docsubject(self, docsubject):
        self.docsubject = docsubject

    def set_pagecount(self, pagecount):
        self.pagecount = pagecount

    def set_remark(self, remark):
        self.remark = remark

    def set_file_data(self, file_data):
        self.file_data = file_data

    def set_assignremarks(self, assignremarks):
        self.assignremarks = assignremarks
