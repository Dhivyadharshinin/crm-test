import json


class AllocationLevelResponse:
    id = None
    code = None
    name = None
    arrange = None
    reportlevel = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_name(self, name):
        self.name = name

    def set_arrange(self, arrange):
        self.sector = arrange

    def set_reportlevel(self,reportlevel):
        self.reportlevel=reportlevel

class New_AllocationLevelResponse:
    id = None
    code = None
    name = None
    bscc_code = None
    source_bscc_code = None
    ratio = None
    average = None
    from_bscc_code = None
    to_bscc_code = None
    coreccbbs_data = None
    toccbbs_data = None
    cc_data = None
    bs_data = None
    final_total = None
    transaction_month = None
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_name(self, name):
        self.name = name

    def set_bscc_code(self,bscc_code):
        self.bscc_code = bscc_code

    def set_source_bscc_code(self,source_bscc_code):
        self.source_bscc_code = source_bscc_code

    def set_ratio(self,ratio):
        self.ratio = ratio

    def set_average(self,average):
        self.average = average

    def set_amount(self,amount):
        self.amount = amount

    def set_from_bscc_code(self,from_bscc_code):
        self.from_bscc_code = from_bscc_code

    def set_to_bscc_code(self,to_bscc_code):
        self.to_bscc_code = to_bscc_code

    def set_coreccbbs_data(self,id,arr):
        data_arr = []
        for i in arr:
            if i['id']==id:
                data_arr=i
        self.coreccbbs_data=data_arr

    def set_toccbbs_data(self,id,arr):
        data_arr = []
        for i in arr:
            if i['id']==id:
                data_arr=i
        self.toccbs_data=data_arr

    def set_cc_data(self,id,arr):
        data_arr = []
        for i in arr:
            if i['id']==id:
                data_arr=i
        self.cc_data=data_arr

    def set_bs_data(self,id,arr):
        data_arr = []
        for i in arr:
            if i['id']==id:
                data_arr=i
        self.bs_data=data_arr

    def set_final_total(self,final_total):
        self.final_total = final_total

    def set_transaction_month(self,transaction_month):
        self.transaction_month = transaction_month

class allocation_response:

    id = None
    source_bscc_code = None
    level_id = None
    level_name = None
    level_code = None
    level_data = None
    frombscccode = None
    allocation_amount = None
    bscc_data = None
    bscc_code = None
    bscc_name = None
    bscc_id = None
    bs_name = None
    cc_name = None
    cc_id = None
    cc_data = None
    bs_id = None
    bs_data = None
    parameter = None
    input_value = None
    ratio = None
    to_amount = None
    to_data = None
    validity_from = None,
    validity_to = None,
    subcat_cat_data = None,
    corebscc = None,
    status = None,
    amount = None,

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_source_bscc_code(self, source_bscc_code):
        self.source_bscc_code = source_bscc_code

    def set_frombscccode(self, frombscccode):
        self.corebscc = frombscccode

    def set_level(self, level_id, arr):
        data_arr = []
        for i in arr:
            if i['id'] == level_id:
                data_arr = i
        self.level_data = data_arr

    def set_level_id(self, level_id):
        self.level_id = level_id

    def set_cost_driver(self, cost_driver_id, arr):
        data_arr = []
        for i in arr:
            if i['id'] == cost_driver_id:
                data_arr = i
        self.cost_driver_data = data_arr

    def set_cost_driver_id(self, cost_driver_id):
        self.cost_driver_id = cost_driver_id

    def set_allocation_amount(self, allocation_amount):
        self.allocation_amount = allocation_amount

    def set_bscc(self, bscc_id, arr):
        data_arr = []
        bsccdata1 = data_arr
        for i in arr:
            # bsccdata1=data_arr
            if i["id"] == bscc_id:
                bsccdata1 = i

        self.bscc_data = bsccdata1

    def set_cc(self, cc_id, arr):
        data_arr = []
        for i in arr:
            if i['id'] == cc_id:
                data_arr = i
        self.cc_data = data_arr

    def set_bs(self, bs_id, arr):
        data_arr = []
        bsdata1 = data_arr
        for i in arr:
            if i['id'] == bs_id:
                bsdata1 = i
        self.bs_data = bsdata1

    def set_parameter(self, parameter):
        self.parameter = parameter

    def set_input_value(self, input_value):
        self.input_value = input_value

    def set_ratio(self, ratio):
        self.ratio = ratio

    def set_to_amount(self, to_amount):
        self.to_amount = to_amount

    def set_to_data(self, to_data):
        self.to_data = to_data

    def set_validity_from(self, validity_from):
        self.validity_from = str(validity_from)

    def set_validity_to(self, validity_to):
        self.validity_to = str(validity_to)

    def set_subcat_cat_data(self, arr, subcat_id):
        for i in arr:
            if i['subcat_id'] == subcat_id:
                self.subcat_id = i['subcat_id']
                self.cat_id = i['category_id']
                self.subcategoryname = i['subcat_name']
                self.categoryname = i['category_name']

    def set_amount(self, amount):
        # amount+=amount
        self.amount = amount

    def set_status(self, status):
        self.status = status