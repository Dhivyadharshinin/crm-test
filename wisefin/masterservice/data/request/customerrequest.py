import json

class CustomerRequest:
    id = None
    customer_clientgid = 1
    customer_code = None
    customer_name =None
    customer_billingname =None
    customer_type =None
    customer_subtype =None
    custgroup_id = 1
    category_id = 1
    location_gid = 1
    customer_constitution = 1
    customer_salemode = 1
    customer_size = 0
    customer_landmark =1
    insert_flag=0
    update_flag=0
    remarks=None
    customer_entitygid=None
    def __init__(self, customer_obj):
        if 'id' in customer_obj:
            self.id = customer_obj['id']
        if 'customer_clientgid' in customer_obj:
            self.customer_clientgid = customer_obj['customer_clientgid']
        if 'customer_code' in customer_obj:
            self.customer_code = customer_obj['customer_code']
        if 'customer_name' in customer_obj:
            self.customer_name = customer_obj['customer_name']

        if 'customer_entitygid' in customer_obj:
            self.customer_entitygid=customer_obj['customer_entitygid']
        if 'customer_billingname' in customer_obj:
            self.customer_billingname = customer_obj['customer_billingname']
        if 'customer_type' in customer_obj:
            self.customer_type = customer_obj['customer_type']
        if 'customer_subtype' in customer_obj:
            self.customer_subtype = customer_obj['customer_subtype']
        if 'custgroup_id' in customer_obj:
            self.custgroup_id = customer_obj['custgroup_id']
        if 'category_id' in customer_obj:
            self.category_id = customer_obj['category_id']
        if 'location_gid' in customer_obj:
            self.location_gid = customer_obj['location_gid']
        if 'customer_constitution' in customer_obj:
            self.customer_constitution = customer_obj['customer_constitution']
        if 'customer_landmark' in customer_obj:
            self.customer_landmark = customer_obj['customer_landmark']
        if 'customer_salemode' in customer_obj:
            self.customer_salemode = customer_obj['customer_salemode']
        if 'customer_size' in customer_obj:
            self.customer_size = customer_obj['customer_size']
        if 'insert_flag' in customer_obj:
            self.insert_flag = customer_obj['insert_flag']

        if 'update_flag' in customer_obj:
            self.update_flag = customer_obj['update_flag']
        if 'remarks' in customer_obj:
            self.remarks = customer_obj['remarks']




    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_id(self):
        return self.id

    def get_customer_clientgid(self):
        return self.customer_clientgid
    def get_customer_code(self):
        return self.customer_code
    def get_customer_name(self):
        return self.customer_name
    def get_customer_billingname(self):
        return self.customer_billingname
    def get_customer_type(self):
        return self.customer_type
    def get_customer_subtype(self):
        return self.customer_subtype
    def get_custgroup_id(self):
        return self.custgroup_id
    def get_category_id(self):
        return self.category_id
    def get_location_gid(self):
        return self.location_gid
    def get_customer_constitution(self):
        return self.customer_constitution
    def get_customer_entitygid(self):
        return self.customer_entitygid
    def get_customer_salemode(self):
        return self.customer_salemode
    def get_customer_size(self):
        return self.customer_size
    def get_customer_landmark(self):
        return self.customer_landmark
    def get_insert_flag(self):
        return self.insert_flag
    def get_update_flag(self):
        return self.update_flag
    def get_remarks(self):
        return self.remarks



