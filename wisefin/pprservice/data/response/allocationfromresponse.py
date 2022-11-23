import json

class AllocationFromResponse:
    id = None
    source = None
    entry_id = None
    entity_code = None
    module = None
    sync_date = None
    wiseFin_date = None
    update_date = None
    CBS_date = None
    entry_status = None
    branch_id = None
    cr_no = None
    supplier_id = None
    product_id = None
    commodity_id = None
    apcat_id = None
    apsubcat_id = None
    bs_id = None
    bscc_id = None
    CBS_GL = None
    sort_oder = None
    ALEI = None
    reporting_level = None
    sorce_bscc_id = None
    input = None
    premise_id = None
    amount = None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_source(self, source):
        self.source = source
    def set_entry_id(self, entry_id):
        self.entry_id = entry_id
    def set_entity_code(self, entity_code):
        self.entity_code = entity_code
    def set_module(self, module):
        self.module = module
    def set_sync_date(self, sync_date):
        self.sync_date = sync_date
    def set_wiseFin_date(self, wiseFin_date):
        self.wiseFin_date = wiseFin_date
    def set_update_date(self, update_date):
        self.update_date = update_date
    def set_CBS_date(self, CBS_date):
        self.CBS_date = CBS_date
    def set_entry_status(self, entry_status):
        self.entry_status = entry_status
    def set_branch_id(self, branch_id):
        self.branch_id = branch_id
    def set_cr_no(self, cr_no):
        self.cr_no = cr_no
    def set_supplier_id(self, supplier_id):
        self.supplier_id = supplier_id
    def set_product_id(self, product_id):
        self.product_id = product_id
    def set_commodity_id(self, commodity_id):
        self.commodity_id = commodity_id
    def set_apcat_id(self, apcat_id):
        self.apcat_id = apcat_id
    def set_apsubcat_id(self, apsubcat_id):
        self.apsubcat_id = apsubcat_id
    def set_bs_id(self, bs_id):
        self.bs_id = bs_id
    def set_bscc_id(self, bscc_id):
        self.bscc_id = bscc_id
    def set_CBS_GL(self, CBS_GL):
        self.CBS_GL = CBS_GL
    def set_sort_oder(self, sort_oder):
        self.sort_oder = sort_oder
    def set_ALEI(self, ALEI):
        self.ALEI = ALEI
    def set_reporting_level(self, reporting_level):
        self.reporting_level = reporting_level
    def set_sorce_bscc_id(self, sorce_bscc_id):
        self.sorce_bscc_id = sorce_bscc_id
    def set_input(self, input):
        self.input = input
    def set_premise_id(self, premise_id):
        self.premise_id = premise_id
    def set_amount(self, amount):
        self.amount = amount

    # def set_allocation_from(self, bscc_id, arr):
    #     if bscc_id != None:
    #         for i in arr:
    #             if i['id'] == bscc_id:
    #                 self.allocation_from = i
    #                 break
    #
    # def set_allocation_level(self, allocationlevel_id, arr):
    #     if allocationlevel_id != None:
    #         for i in arr:
    #             if i['id'] == allocationlevel_id:
    #                 self.allocation_level = i
    #                 break
    #
    # def set_costdriver(self, costdriver_id, arr):
    #     if costdriver_id != None:
    #         for i in arr:
    #             if i['id'] == costdriver_id:
    #                 self.costdriver = i
    #                 break
    #
    # def set_amount(self,amount):
    #     self.amount=amount