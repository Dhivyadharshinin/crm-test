import json

class AssetCatRequest:

    id=subcategory_id=subcatname =lifetime = deptype = deprate_itc =itcatname=  deprate_ca = deprate_mgmt = \
    depgl_itc = depgl_ca = depgl_mgmt =depresgl_itc =depresgl_ca =depresgl_mgmt =apcatnodep_mgmt =\
    apscatnodep_mgmt =apcatnodepres_mgmt = apscatnodepres_mgmt =deprate = barcoderequired = remarks =  None

    def __init__(self, assetcat_data):
        if 'id' in assetcat_data:
            self.id = assetcat_data['id']
        if 'subcategory_id' in assetcat_data:
            self.subcategory_id = assetcat_data['subcategory_id']
        if 'subcatname' in assetcat_data:
            self.subcatname = assetcat_data['subcatname']
        if 'lifetime' in assetcat_data:
            self.lifetime = assetcat_data['lifetime']
        if 'deptype' in assetcat_data:
            self.deptype = assetcat_data['deptype']
        if 'deprate_itc' in assetcat_data:
            self.deprate_itc = assetcat_data['deprate_itc']
        if 'itcatname' in assetcat_data:
            self.itcatname = assetcat_data['itcatname']
        if 'deprate_ca' in assetcat_data:
            self.deprate_ca = assetcat_data['deprate_ca']
        if 'deprate_mgmt' in assetcat_data:
            self.deprate_mgmt = assetcat_data['deprate_mgmt']
        if 'depgl_itc' in assetcat_data:
            self.depgl_itc = assetcat_data['depgl_itc']
        if 'depgl_ca' in assetcat_data:
            self.depgl_ca = assetcat_data['depgl_ca']
        if 'depgl_mgmt' in assetcat_data:
            self.depgl_mgmt = assetcat_data['depgl_mgmt']
        if 'depresgl_itc' in assetcat_data:
            self.depresgl_itc = assetcat_data['depresgl_itc']
        if 'depresgl_ca' in assetcat_data:
            self.depresgl_ca = assetcat_data['depresgl_ca']
        if 'depresgl_mgmt' in assetcat_data:
            self.depresgl_mgmt = assetcat_data['depresgl_mgmt']
        if 'apcatnodep_mgmt' in assetcat_data:
            self.apcatnodep_mgmt = assetcat_data['apcatnodep_mgmt']
        if 'apscatnodep_mgmt' in assetcat_data:
            self.apscatnodep_mgmt = assetcat_data['apscatnodep_mgmt']
        if 'apcatnodepres_mgmt' in assetcat_data:
            self.apcatnodepres_mgmt = assetcat_data['apcatnodepres_mgmt']
        if 'apscatnodepres_mgmt' in assetcat_data:
            self.apscatnodepres_mgmt = assetcat_data['apscatnodepres_mgmt']
        if 'deprate' in assetcat_data:
            self.deprate = assetcat_data['deprate']
        if 'barcoderequired' in assetcat_data:
            self.barcoderequired = assetcat_data['barcoderequired']
        if 'remarks' in assetcat_data:
            self.remarks = assetcat_data['remarks']



    def get_id(self):
        return self.id
    def get_subcategory_id(self):
        return self.subcategory_id
    def get_subcatname(self):
        return self.subcatname
    def get_lifetime(self):
        return self.lifetime
    def get_deptype(self):
        return self.deptype
    def get_deprate_itc(self):
        return self.deprate_itc
    def get_itcatname(self):
        return self.itcatname
    def get_deprate_ca(self):
        return self.deprate_ca
    def get_deprate_mgmt(self):
        return self.deprate_mgmt
    def get_depgl_itc(self):
        return self.depgl_itc
    def get_depgl_ca(self):
        return self.depgl_ca
    def get_depgl_mgmt(self):
        return self.depgl_mgmt
    def get_depresgl_itc(self):
        return self.depresgl_itc
    def get_depresgl_ca(self):
        return self.depresgl_ca
    def get_depresgl_mgmt(self):
        return self.depresgl_mgmt
    def get_apcatnodep_mgmt(self):
        return self.apcatnodep_mgmt
    def get_apscatnodep_mgmt(self):
        return self.apscatnodep_mgmt
    def get_apcatnodepres_mgmt(self):
        return self.apcatnodepres_mgmt
    def get_apscatnodepres_mgmt(self):
        return self.apscatnodepres_mgmt
    def get_deprate(self):
        return self.deprate
    def get_barcoderequired(self):
        return self.barcoderequired
    def get_remarks(self):
        return self.remarks

