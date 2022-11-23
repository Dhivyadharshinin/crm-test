import json

from masterservice.service.docugroupservice import DocumentGroupService
from masterservice.service.questiontypeservice import QuestiontypeService
from masterservice.util.masterutil import Vendorclassfication_type, process_type
from userservice.service.groupservice import GroupService
from vendorservice.util.vendorutil import getClassification, getType, getGroup


class VendorclassficationprofileResponse:
    id, type_id, rel_cat, criticality, vendor_type, period, process, dept_id, is_doc, document_group ,set_Questionc,header,order,expiration_date,is_activity= (None,) * 15

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_type_id(self, type_id, arr):
        self.type_id = None
        for i in arr:
            if i.id == type_id:
                self.type_id = i
                break
        # type_val = QuestiontypeService(scope)
        # type_serv = type_val.get_question_type(type_id)
        # self.type_id = type_serv

    def set_rel_cat(self, rel_cat):
        rel_cat_val = getGroup(rel_cat)
        self.rel_cat = rel_cat_val

    def set_criticality(self, criticality):
        criticality_val = getType(criticality)
        self.criticality = criticality_val

    def set_vendor_type(self, vendor_type):
        vendor_type_val = getClassification(vendor_type)
        self.vendor_type = vendor_type_val

    def set_period(self, period):
        period_val = Vendorclassfication_type(period)
        self.period = period_val

    def set_process(self, process):
        process_val = process_type(process)
        self.process = process_val

    def set_dept_id(self, dept_id, scope):
        doc_serv = GroupService(scope)
        dept_id_val = doc_serv.fetch_group_by_id(dept_id)
        self.dept_id = dept_id_val

    def set_is_doc(self, is_doc):
        self.is_doc = is_doc
    def set_Questionc(self, question):
        self.question = question
    def set_header(self, question_header):
        self.question_header = question_header
    def set_document_group(self, document_group, scope):
        if document_group is None:
            self.document_group = ''
        else:
            self.document_group={"id":document_group.id,"name":document_group.name}

    def set_order(self, order):
        self.order = order

    def set_Activity(self, Activity):
        self.Activity = Activity

    def set_type(self,type):
        self.type_id = type

    def set_is_activity(self,is_activity):
        self.is_activity = is_activity

    def set_expiration_date(self,expiration_date):
        self.expiration_date = str(expiration_date)

    def set_sub_options(self, sub_options):
        self.sub_options = sub_options
