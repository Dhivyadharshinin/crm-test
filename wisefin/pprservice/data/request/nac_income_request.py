class ppr_clientrequest:
    asset_id = None
    client_id = None
    product_id = None
    month = None
    assest_class=None
    Rm_id=None
    def __init__(self, client_obj):
        if 'asset_id' in client_obj:
            self.asset_id = client_obj['asset_id']
        if 'client_id' in client_obj:
            self.client_id = client_obj['client_id']
        if 'product_id' in client_obj:
            self.product_id = client_obj['product_id']
        if 'month' in client_obj:
            self.month = client_obj['month']
        if 'assest_class' in client_obj:
            self.assest_class = client_obj['assest_class']
        if 'Rm_id' in client_obj:
            self.Rm_id = client_obj['Rm_id']

    def get_asset_id(self):
        return self.asset_id
    def get_client_id(self):
        return self.client_id
    def get_product_id(self):
        return self.product_id
    def get_month(self):
        return self.month
    def get_assest_class(self):
        return self.assest_class
    def get_Rm_id(self):
        return self.Rm_id

class ppr_source_request:
    id = None
    code = None
    name = None
    gl_no = None
    source = None
    head_group = None
    description = None
    date = None
    type = None
    from_date = None
    to_date = None
    asset_ref = None
    asset_id = None
    client_id = None
    product_id = None
    Rm_id = None
    business_id = None
    expgrp_id = None
    exp_id = None
    cat_id = None
    subcat_id = None
    def __init__(self, client_obj):
        if 'id' in client_obj:
            self.id = client_obj['id']
        if 'code' in client_obj:
            self.code = client_obj['code']
        if 'name' in client_obj:
            self.name = client_obj['name']
        if 'gl_no' in client_obj:
            self.gl_no = client_obj['gl_no']
        if 'source' in client_obj:
            self.source = client_obj['source']
        if 'head_group' in client_obj:
            self.head_group = client_obj['head_group']
        if 'description' in client_obj:
            self.description = client_obj['description']
        if 'date' in client_obj:
            self.date = client_obj['date']
        if 'type' in client_obj:
            self.type = client_obj['type']
        if 'from_date' in client_obj:
            self.from_date = client_obj['from_date']
        if 'to_date' in client_obj:
            self.to_date = client_obj['to_date']
        if 'asset_ref' in client_obj:
            self.asset_ref = client_obj['asset_ref']
        if 'asset_id' in client_obj:
            self.asset_id = client_obj['asset_id']
        if 'client_id' in client_obj:
            self.client_id = client_obj['client_id']
        if 'product_id' in client_obj:
            self.product_id = client_obj['product_id']
        if 'assest_class' in client_obj:
            self.assest_class = client_obj['assest_class']
        if 'Rm_id' in client_obj:
            self.Rm_id = client_obj['Rm_id']
        if 'business_id' in client_obj:
            self.business_id = client_obj['business_id']
        if 'expgrp_id' in client_obj:
            self.expgrp_id = client_obj['expgrp_id']
        if 'cat_id' in client_obj:
            self.cat_id = client_obj['cat_id']
        if 'subcat_id' in client_obj:
            self.subcat_id = client_obj['subcat_id']
        if 'exp_id' in client_obj:
            self.exp_id = client_obj['exp_id']
    def get_id(self):
        return self.id
    def get_code(self):
        return self.code
    def get_name(self):
        return self.name
    def get_gl_no(self):
        return self.gl_no
    def get_source(self):
        return self.source
    def get_head_group(self):
        return self.head_group
    def get_description(self):
        return self.description
    def get_date(self):
        return self.date
    def get_type(self):
        return self.type
    def get_from_date(self):
        return self.from_date
    def get_to_date(self):
        return self.to_date
    def get_asset_ref(self):
        return self.asset_ref
    def get_asset_id(self):
        return self.asset_id
    def get_client_id(self):
        return self.client_id
    def get_product_id(self):
        return self.product_id
    def get_assest_class(self):
        return self.assest_class
    def get_Rm_id(self):
        return self.Rm_id
    def get_business_id(self):
        return self.business_id
    def get_expgrp_id(self):
        return self.expgrp_id
    def get_cat_id(self):
        return self.cat_id
    def get_subcat_id(self):
        return self.subcat_id
    def get_exp_id(self):
        return self.exp_id


