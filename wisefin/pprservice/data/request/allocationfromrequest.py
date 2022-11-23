import json
class AllocationFromRequest:
    id = None
    source = None
    entry_id = None
    entity_code=None
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

    def __init__(self, allocationfrom_obj):
        if 'id' in allocationfrom_obj:
            self.id = allocationfrom_obj['id']
        if 'source' in allocationfrom_obj:
            self.source = allocationfrom_obj['source']
        if 'entry_id' in allocationfrom_obj:
            self.entry_id = allocationfrom_obj['entry_id']
        if 'entity_code' in allocationfrom_obj:
            self.entity_code = allocationfrom_obj['entity_code']
        if 'module' in allocationfrom_obj:
            self.module = allocationfrom_obj['module']
        if 'sync_date' in allocationfrom_obj:
            self.sync_date = allocationfrom_obj['sync_date']
        if 'wiseFin_date' in allocationfrom_obj:
            self.wiseFin_date = allocationfrom_obj['wiseFin_date']
        if 'update_date' in allocationfrom_obj:
            self.update_date = allocationfrom_obj['update_date']
        if 'CBS_date' in allocationfrom_obj:
            self.CBS_date = allocationfrom_obj['CBS_date']
        if 'entry_status' in allocationfrom_obj:
            self.entry_status = allocationfrom_obj['entry_status']
        if 'branch_id' in allocationfrom_obj:
            self.branch_id = allocationfrom_obj['branch_id']
        if 'cr_no' in allocationfrom_obj:
            self.cr_no = allocationfrom_obj['cr_no']
        if 'supplier_id' in allocationfrom_obj:
            self.supplier_id = allocationfrom_obj['supplier_id']
        if 'product_id' in allocationfrom_obj:
            self.product_id = allocationfrom_obj['product_id']
        if 'commodity_id' in allocationfrom_obj:
            self.commodity_id = allocationfrom_obj['commodity_id']
        if 'apcat_id' in allocationfrom_obj:
            self.apcat_id = allocationfrom_obj['apcat_id']
        if 'apsubcat_id' in allocationfrom_obj:
            self.apsubcat_id = allocationfrom_obj['apsubcat_id']
        if 'bs_id' in allocationfrom_obj:
            self.bs_id = allocationfrom_obj['bs_id']
        if 'bscc_id' in allocationfrom_obj:
            self.bscc_id = allocationfrom_obj['bscc_id']
        if 'CBS_GL' in allocationfrom_obj:
            self.CBS_GL = allocationfrom_obj['CBS_GL']
        if 'sort_oder' in allocationfrom_obj:
            self.sort_oder = allocationfrom_obj['sort_oder']
        if 'ALEI' in allocationfrom_obj:
            self.ALEI = allocationfrom_obj['ALEI']
        if 'reporting_level' in allocationfrom_obj:
            self.reporting_level = allocationfrom_obj['reporting_level']
        if 'sorce_bscc_id' in allocationfrom_obj:
            self.sorce_bscc_id = allocationfrom_obj['sorce_bscc_id']
        if 'input' in allocationfrom_obj:
            self.input = allocationfrom_obj['input']
        if 'premise_id' in allocationfrom_obj:
            self.premise_id = allocationfrom_obj['premise_id']
        if 'amount' in allocationfrom_obj:
            self.amount = allocationfrom_obj['amount']

    def get_id(self):
        return self.id
    def get_source(self):
        return self.source
    def get_entry_id(self):
        return self.entry_id
    def get_entity_code(self):
        return self.entity_code
    def get_module(self):
        return self.module
    def get_input(self):
        return self.input
    def get_sync_date(self):
        return self.sync_date
    def get_wiseFin_date(self):
        return self.wiseFin_date
    def get_update_date(self):
        return self.update_date
    def get_CBS_date(self):
        return self.CBS_date
    def get_entry_status(self):
        return self.entry_status
    def get_branch_id(self):
        return self.branch_id
    def get_cr_no(self):
        return self.cr_no
    def get_supplier_id(self):
        return self.supplier_id
    def get_product_id(self):
        return self.product_id
    def get_commodity_id(self):
        return self.commodity_id
    def get_apcat_id(self):
        return self.apcat_id
    def get_apsubcat_id(self):
        return self.apsubcat_id
    def get_bs_id(self):
        return self.bs_id
    def get_bscc_id(self):
        return self.bscc_id
    def get_CBS_GL(self):
        return self.CBS_GL
    def get_sort_oder(self):
        return self.sort_oder
    def get_ALEI(self):
        return self.ALEI
    def get_reporting_level(self):
        return self.reporting_level
    def get_sorce_bscc_id(self):
        return self.sorce_bscc_id
    def get_premise_id(self):
        return self.premise_id
    def get_amount(self):
        return self.amount



