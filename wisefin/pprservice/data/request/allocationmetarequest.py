

class from_AllocationMeta_request:
    id=source_bscc_code=level=cost_driver=allocation_amount=bscc_code=cc_id=bs_id=parameter=input_value=ratio=to_amount=None
    to_data = None,
    frombscccode=None,
    validity_from = None,
    validity_to = None,

    def __init__(self,request):
        if 'id' in request:
            self.id=request['id']
        if 'source_bscc_code' in request:
            self.source_bscc_code = request['source_bscc_code']
        if 'level' in request:
            self.level = request['level']
        if 'cost_driver' in request:
            self.cost_driver = request['cost_driver']
        if 'allocation_amount' in request:
            self.allocation_amount = request['allocation_amount']
        if 'to_data' in request:
            self.to_data=request['to_data']
        if 'frombscccode' in request:
            self.frombscccode=request['frombscccode']
        if 'validity_from' in request:
            self.validity_from=request['validity_from']
        if 'validity_to' in request:
            self.validity_to=request['validity_to']


    def get_id(self):
        return self.id
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
    def get_to_data(self):
        arr = []
        for i in self.to_data:
            to_all = to_AllocationMeta_request(i)
            arr.append(to_all)
        return arr

class to_AllocationMeta_request:
    id=bscc_code = cc_id = bs_id = parameter = input_value = ratio = to_amount = None
    premium_amount = '0.0',
    validity_from = None,
    validity_to = None,
    status=1,
    def __init__(self,request):
        if 'id' in request:
            self.id=request['id']
        if 'bscc_code'in request:
            self.bscc_code = request['bscc_code']
        if 'cc_id'in request:
            self.cc_id = request['cc_id']
        if 'bs_id'in request:
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
            self.premium_amount=request['premium_amount']
        if 'validity_from' in request:
            self.validity_from=request['validity_from']
        if 'validity_to' in request:
            self.validity_to=request['validity_to']
        if 'status' in request:
            self.status=request['status']
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
        return  self.premium_amount
    def get_validity_from(self):
        return self.validity_from
    def get_validity_to(self):
        return self.validity_to
    def get_status(self):
        return self.status

class AllocationToPprrequest:
    id=None,
    transactionmonth=None,
    transactionyear=None,
    transactiondate=None,
    valuedate=None,
    cc_code=None,
    bs_code=None,
    apinvoice_id=None,
    bsname=None,
    ccname=None,
    bizname=None,
    level=None,
    cost_driver=None,
    allocation_amount=None,
    bscc_code=None,
    parameter=None,
    input_value=None,
    ratio=None,
    to_amount=None,
    source_bscc_code=None,
    frombscccode=None,
    premium_amount=None,
    finyear=None,
    sector=None,
    apexpence_id=None,
    status=None,
    cat_id=None,
    subcat_id=None,
    quarter=None
    def __init__(self,request):
        if 'id' in request:
            self.id=request['id']
        if 'transactionmonth' in request:
            self.transactionmonth = request['transactionmonth']
        if 'transactionyear' in request:
            self.transactionyear = request['transactionyear']
        if 'transactiondate' in request:
            self.transactiondate = request['transactiondate']
        if 'valuedate' in request:
            self.valuedate = request['valuedate']
        if 'cc_code' in request:
            self.cc_code=request['cc_code']
        if 'bs_code' in request:
            self.bs_code=request['bs_code']
        if 'apinvoice_id' in request:
            self.apinvoice_id=request['apinvoice_id']
        if 'bsname' in request:
            self.bsname=request['bsname']
        if 'ccname' in request:
            self.ccname=request['ccname']
        if 'bizname' in request:
            self.bizname=request['bizname']
        if 'level' in request:
            self.level=request['level']
        if 'cost_driver' in request:
            self.cost_driver=request['cost_driver']
        if 'allocation_amount' in request:
            self.allocation_amount=request['allocation_amount']
        if 'bscc_code' in request:
            self.bscc_code=request['bscc_code']
        if 'parameter' in request:
            self.parameter=request['parameter']
        if 'input_value' in request:
            self.input_value=request['input_value']
        if 'ratio' in request:
            self.ratio=request['ratio']
        if 'to_amount' in request:
            self.to_amount=request['to_amount']
        if 'source_bscc_code' in request:
            self.source_bscc_code=request['source_bscc_code']
        if 'frombscccode' in request:
            self.frombscccode=request['frombscccode']
        if 'premium_amount' in request:
            self.premium_amount=request['premium_amount']
        if 'finyear' in request:
            self.finyear=request['finyear']
        if 'sector' in request:
            self.sector=request['sector']
        if 'apexpence_id' in request:
            self.apexpence_id=request['apexpence_id']
        if 'status' in request:
            self.status=request['status']
        if 'cat_id' in request:
            self.cat_id=request['cat_id']
        if 'subcat_id' in request:
            self.subcat_id=request['subcat_id']
        if 'quarter' in request:
            self.quarter=request['quarter']


    def get_id(self):
        return self.id
    def get_transactionmonth(self):
        return self.transactionmonth
    def get_transactionyear(self):
        return self.transactionyear
    def get_transactiondate(self):
        return self.transactiondate
    def get_valuedate(self):
        return self.valuedate
    def get_cc_code(self):
        return self.cc_code
    def get_bs_code(self):
        return self.bs_code
    def get_apinvoice_id(self):
        return self.apinvoice_id
    def get_bsname(self):
        return self.bsname
    def get_ccname(self):
        return self.ccname
    def get_bizname(self):
        return self.bizname
    def get_level(self):
        return self.level
    def get_cost_driver(self):
        return self.cost_driver
    def get_allocation_amount(self):
        return self.allocation_amount
    def get_bscc_code(self):
        return self.bscc_code
    def get_parameter(self):
        return self.parameter
    def get_input_value(self):
        return self.input_value
    def get_ratio(self):
        return self.ratio
    def get_to_amount(self):
        return self.to_amount
    def get_source_bscc_code(self):
        return self.source_bscc_code
    def get_frombscccode(self):
        return self.frombscccode
    def get_premium_amount(self):
        return self.premium_amount
    def get_finyear(self):
        return self.finyear
    def get_sector(self):
        return self.sector
    def get_apexpence_id(self):
        return self.apexpence_id
    def get_status(self):
        return self.status
    def get_cat_id(self):
        return self.cat_id
    def get_subcat_id(self):
        return self.subcat_id
    def get_quarter(self):
        return self.quarter

