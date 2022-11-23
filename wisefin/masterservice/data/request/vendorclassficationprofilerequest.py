class VendorclassficationprofileRequest:
    id, type_id, rel_cat, criticality, vendor_type, period, process, dept_id, is_doc, document_group_id, order, is_activity,expiration_date = (None,) * 13

    def __init__(self, user_obj):
        if 'id' in user_obj:
            self.id = user_obj['id']
        if 'type_id' in user_obj:
            self.type_id = user_obj['type_id']
        if 'rel_cat' in user_obj:
            self.rel_cat = user_obj['rel_cat']
        if 'criticality' in user_obj:
            self.criticality = user_obj['criticality']
        if 'vendor_type' in user_obj:
            self.vendor_type = user_obj['vendor_type']
        if 'period' in user_obj:
            self.period = user_obj['period']
        if 'process' in user_obj:
            self.process = user_obj['process']
        if 'dept_id' in user_obj:
            self.dept_id = user_obj['dept_id']
        if 'is_doc' in user_obj:
            self.is_doc = user_obj['is_doc']
        if 'document_group_id' in user_obj:
            if user_obj['document_group_id'] != '':
                self.document_group_id = user_obj['document_group_id']
        if 'order' in user_obj:
            if user_obj['order']!='':
                self.order = user_obj['order']
        if 'is_activity' in user_obj:
            self.is_activity = user_obj['is_activity']
        if 'expiration_date' in user_obj:
            if user_obj['expiration_date'] !='':
                self.expiration_date = user_obj['expiration_date']


    def get_id(self):
        return self.id

    def get_type_id(self):
        return self.type_id

    def get_rel_cat(self):
        return self.rel_cat

    def get_criticality(self):
        return self.criticality

    def get_vendor_type(self):
        return self.vendor_type

    def get_period(self):
        return self.period

    def get_process(self):
        return self.process

    def get_dept_id(self):
        return self.dept_id

    def get_is_doc(self):
        return self.is_doc

    def get_document_group_id(self):
        return self.document_group_id

    def get_order(self):
        return self.order

    def get_is_activity(self):
        return self.is_activity

    def get_expiration_date(self):
        return self.expiration_date
