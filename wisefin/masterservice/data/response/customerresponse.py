import json


class CustomerResponse:
        id = None
        code = None
        name=None

        customer_entitygid = None
        customer_code = None
        customer_name = None
        customer_billingname = None
        customer_type = None
        customer_subtype = None
        custgroup_id = None
        category_id = None
        location_gid = None
        customer_constitution = None
        customer_salemode = None
        customer_size = None
        customer_landmark = None
        insert_flag = 0
        update_flag = 0
        remarks = None
        address = None


        def get(self):
            return json.dumps(self, default=lambda o: o.__dict__,
                              sort_keys=True, indent=4)

        def set_id(self, id):
            self.id = id
        def set_code(self, code):
            self.code = code
        def set_name(self, name):
            self.name = name



        def set_customer_entitygid(self, customer_entitygid):
            self.customer_entitygid = customer_entitygid
        def set_customer_code(self, customer_code):
            self.customer_code = customer_code
        def set_customer_name(self, customer_name):
            self.customer_name = customer_name
        def set_customer_billingname(self, customer_billingname):
            self.customer_billingname = customer_billingname
        def set_customer_type(self, customer_type):
            self.customer_type = customer_type

        def set_customer_subtype(self, customer_subtype):
            self.customer_subtype = customer_subtype

        def set_custgroup_id(self, custgroup_id):
            self.custgroup_id = custgroup_id

        def set_category_id(self, category_id):
            self.category_id = category_id

        def set_location_gid(self, location_gid):
            self.location_gid = location_gid

        def set_customer_constitution(self, customer_constitution):
            self.customer_constitution = customer_constitution

        def set_customer_salemode(self, customer_salemode):
            self.customer_salemode = customer_salemode

        def set_customer_size(self, customer_size):
            self.customer_size = customer_size

        def set_customer_landmark(self, customer_landmark):
            self.customer_landmark = customer_landmark

        def set_insert_flag(self, insert_flag):
            self.insert_flag = insert_flag

        def set_update_flag(self, update_flag):
            self.update_flag = update_flag

        def set_remarks(self, remarks):
            self.remarks = remarks


        def set_address(self, address):
            self.address = address




