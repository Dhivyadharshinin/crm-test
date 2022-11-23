import json


class AssetUpdateRequest:
    id = None
    barcode = None,
    product_name=None,
    branch_code=None,
    branch_name=None,
    asset_cost=None,
    asset_value=None,
    asset_tag = None,
    asset_details_id = None
    make = None
    serial_no = None
    cr_number = None
    kvb_asset_id = None
    condition = None
    status = None
    remarks = None
    pv_done = None
    checker_date = None
    completed_date = None
    control_office_branch = None

    def __init__(self, json_input):
        if 'id' in json_input:
            self.id = json_input['id']
        if 'asset_details_id' in json_input:
            self.asset_details_id = json_input['asset_details_id']
        if 'barcode' in json_input:
            self.barcode = json_input['barcode']
        if 'product_name' in json_input:
            self.product_name = json_input['product_name']
        if 'branch_code' in json_input:
            self.branch_code = json_input['branch_code']
        if 'branch_name' in json_input:
            self.branch_name = json_input['branch_name']
        if 'asset_cost' in json_input:
            self.asset_cost = json_input['asset_cost']
        if 'asset_value' in json_input:
            self.asset_value = json_input['asset_value']
        if 'asset_tag' in json_input:
            self.asset_tag = json_input['asset_tag']
        if 'make' in json_input:
            self.make = json_input['make']
        if 'serial_no' in json_input:
            self.serial_no = json_input['serial_no']
        if 'crnum' in json_input:
            self.cr_number = json_input['crnum']
        if 'kvb_asset_id' in json_input:
            self.kvb_asset_id = json_input['kvb_asset_id']
        if 'condition' in json_input:
            self.condition = json_input['condition']
        if 'status' in json_input:
            self.status = json_input['status']
        if 'remarks' in json_input:
            self.remarks = json_input['remarks']
        if 'pv_done' in json_input:
            self.pv_done = json_input['pv_done']
        if 'checker_date' in json_input:
            self.checker_date = json_input['checker_date']
        if 'completed_date' in json_input:
            self.completed_date = json_input['completed_date']
        if 'control_office_branch' in json_input:
            self.control_office_branch = json_input['control_office_branch']


    def get_id(self):
        return self.id

    def get_asset_details_id(self):
        return self.asset_details_id

    def get_barcode(self):
        return self.barcode
    def get_product_name(self):
        return self.product_name
    def get_branch_code(self):
        return self.branch_code
    def get_branch_name(self):
        return self.branch_name
    def get_asset_cost(self):
        return self.asset_cost
    def get_asset_value(self):
        return self.asset_value
    def get_asset_tag(self):
        return self.asset_tag

    def get_make(self):
        return self.make

    def get_serial_no(self):
        return self.serial_no

    def get_cr_number(self):
        return self.cr_number

    def get_kvb_asset_id(self):
        return self.kvb_asset_id

    def get_condition(self):
        return self.condition

    def get_status(self):
        return self.status

    def get_remarks(self):
        return self.remarks

    def get_pv_done(self):
        return self.pv_done

    def get_control_office_branch(self):
        return self.control_office_branch

    def get_checker_date(self):
        return self.checker_date

    def get_completed_date(self):
        return self.completed_date