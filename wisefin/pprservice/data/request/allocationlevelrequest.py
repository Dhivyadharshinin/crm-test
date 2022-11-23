import json
class AllocationLevelRequest:
    id = None
    code = None
    name = None
    arrange=None
    reportlevel = None

    def __init__(self, allocationlevel_obj):
        if 'id' in allocationlevel_obj:
            self.id = allocationlevel_obj['id']
        if 'code' in allocationlevel_obj:
            self.code = allocationlevel_obj['code']
        if 'name' in allocationlevel_obj:
            self.name = allocationlevel_obj['name']
        if 'arrange' in allocationlevel_obj:
            self.arrange = allocationlevel_obj['arrange']
        if 'reportlevel' in allocationlevel_obj:
            self.reportlevel = allocationlevel_obj['reportlevel']

    def get_id(self):
        return self.id
    def get_code(self):
        return self.code
    def get_name(self):
        return self.name
    def get_arrange(self):
        return self.arrange
    def get_reportlevel(self):
        return self.reportlevel

class New_AllocationLevelRequest:
    id = None
    code = None
    name = None
    total_amount = None
    bs_id = None
    cc_id = None
    core_bscc = None
    level_id = None
    transaction_month = None
    bscc_id = None

    def __init__(self, allocationlevel_obj):
        if 'id' in allocationlevel_obj:
            self.id = allocationlevel_obj['id']
        if 'code' in allocationlevel_obj:
            self.code = allocationlevel_obj['code']
        if 'name' in allocationlevel_obj:
            self.name = allocationlevel_obj['name']
        if 'total_amount' in allocationlevel_obj:
            self.total_amount = allocationlevel_obj['total_amount']
        if 'bs_id' in allocationlevel_obj:
            self.bs_id = allocationlevel_obj['bs_id']
        if 'cc_id' in allocationlevel_obj:
            self.cc_id = allocationlevel_obj['cc_id']
        if 'core_bscc' in allocationlevel_obj:
            self.core_bscc = allocationlevel_obj['core_bscc']
        if 'level_id' in allocationlevel_obj:
            self.level_id = allocationlevel_obj['level_id']
        if 'transaction_month' in allocationlevel_obj:
            self.transaction_month = allocationlevel_obj['transaction_month']
        if 'bscc_id' in allocationlevel_obj:
            self.bscc_id = allocationlevel_obj['bscc_id']

    def get_id(self):
        return self.id
    def get_code(self):
        return self.code
    def get_name(self):
        return self.name
    def get_total_amount(self):
        return self.total_amount
    def get_bs_id(self):
        return self.bs_id
    def get_cc_id(self):
        return self.cc_id
    def get_core_bscc(self):
        return self.core_bscc
    def get_level_id(self):
        return self.level_id
    def get_tranaction_month(self):
        return self.transaction_month
    def get_bscc_id(self):
        return self.bscc_id

class allocation_request:
    id = source_bscc_code = level = cost_driver = None
    allocation_amount = bscc_code = cc_id = bs_id = parameter = input_value = ratio = to_amount = None
    to_data = None
    frombscccode = None
    validity_from = None
    validity_to = None
    core_bscc_code = None

    def __init__(self, request):
        if 'id' in request:
            self.id = request['id']
        if 'source_bscc_code' in request:
            self.source_bscc_code = request['source_bscc_code']
        if 'core_bscc_code' in request:
            self.core_bscc_code = request['core_bscc_code']
        if 'bscc_code' in request:
            if request['bscc_code'] != "":
                self.bscc_code = request['bscc_code']
        if 'level' in request:
            self.level = request['level']
        if 'cost_driver' in request:
            self.cost_driver = request['cost_driver']
        if 'allocation_amount' in request:
            self.allocation_amount = request['allocation_amount']
        if 'to_data' in request:
            self.to_data = request['to_data']
        if 'frombscccode' in request:
            if request['frombscccode'] != "":
                self.frombscccode = request['frombscccode']
        if 'validity_from' in request:
            self.validity_from = request['validity_from']
        if 'validity_to' in request:
            self.validity_to = request['validity_to']
        if 'ratio' in request:
            self.ratio = request['ratio']
        if 'cc_id' in request:
            if request['cc_id'] != "":
                self.cc_id = request['cc_id']
        if 'bs_id' in request:
            if request['bs_id'] != "":
                self.bs_id = request['bs_id']

    def get_id(self):
        return self.id

    def get_core_bscc(self):
        return self.core_bscc_code

    def get_source_bscc_code(self):
        return self.source_bscc_code

    def get_level(self):
        return self.level

    def get_cost_driver(self):
        return self.cost_driver

    def get_allocation_amount(self):
        return self.allocation_amount

    def get_frombscccode(self):
        return self.frombscccode

    def get_validity_from(self):
        return self.validity_from

    def get_validity_to(self):
        return self.validity_to

    def get_bscc_code(self):
        return self.bscc_code

    def get_cc_id(self):
        return self.cc_id

    def get_ratio(self):
        return self.ratio

    def get_to_amount(self):
        return self.to_amount

    def get_to_data(self):
        arr = []
        for i in self.to_data:
            to_all = to_AllocationMeta_request(i)
            arr.append(to_all)
        return arr

    def get_bs_id(self):
        return self.bs_id


class to_AllocationMeta_request:
    id = bscc_code = cc_id = bs_id = parameter = input_value = ratio = to_amount = None
    premium_amount = '0.0'
    validity_from = None
    validity_to = None
    status = 1,

    def __init__(self, request):
        if 'id' in request:
            self.id = request['id']
        if 'bscc_code' in request:
            if request['bscc_code'] != "":
                self.bscc_code = request['bscc_code']
        if 'cc_id' in request:
            if request['cc_id'] != "":
                self.cc_id = request['cc_id']
        if 'bs_id' in request:
            if request['bs_id'] != "":
                self.bs_id = request['bs_id']
        if 'parameter' in request:
            self.parameter = request['parameter']
        if 'input_value' in request:
            self.input_value = request['input_value']
        if 'ratio' in request:
            self.ratio = request['ratio']
        if 'to_amount' in request:
            self.to_amount = request['to_amount']
        if 'premium_amount' in request:
            self.premium_amount = request['premium_amount']
        if 'validity_from' in request:
            self.validity_from = request['validity_from']
        if 'validity_to' in request:
            self.validity_to = request['validity_to']
        if 'status' in request:
            self.status = request['status']

    def get_id(self):
        return self.id

    def get_bscc_code(self):
        return self.bscc_code

    def get_cc_id(self):
        return self.cc_id

    def get_bs_id(self):
        return self.bs_id

    def get_parameter(self):
        return self.parameter

    def get_input_value(self):
        return self.input_value

    def get_ratio(self):
        return self.ratio

    def get_to_amount(self):
        return self.to_amount

    def get_premium_amount(self):
        return self.premium_amount

    def get_validity_from(self):
        return self.validity_from

    def get_validity_to(self):
        return self.validity_to

    def get_status(self):
        return self.status