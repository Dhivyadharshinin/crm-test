class VendorAccessorResponse:
    vendor_id = None
    user_id = None
    created_date = None
    updated_date = None
    is_sys = None

    def set_vendor_id(self, vendor_id):
        self.vendor_id = vendor_id

    def set_user_id(self, user_id):
        self.user_id = user_id

    def set_created_date(self, created_date):
        self.created_date = created_date

    def set_updated_date(self, updated_date):
        self.updated_date = updated_date

    def set_is_sys(self, is_sys):
        self.is_sys = is_sys

    def get_vendor_id(self):
        return self.vendor_id

    def get_user_id(self):
        return self.user_id

    def get_created_date(self):
        return str(self.created_date)

    def get_updated_date(self):
        return str(self.updated_date)

    def get_is_sys(self):
        return self.is_sys