import json


class AssetCatResponse:
    id = subcategory_id = subcatname = lifetime = deptype = deprate_itc = deprate_ca = deprate_mgmt = \
    depgl_itc = depgl_ca = depgl_mgmt = depresgl_itc = depresgl_ca = depresgl_mgmt = apcatnodep_mgmt = \
    apscatnodep_mgmt = apcatnodepres_mgmt = apscatnodepres_mgmt = deprate = barcoderequired = remarks = itcatname = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_subcategory_id(self, subcategory_id):
        self.subcategory_id = subcategory_id
    def set_itcatname(self, itcatname):
        self.itcatname = itcatname
    def set_subcatname(self, subcatname):
        self.subcatname = subcatname
    def set_lifetime(self, lifetime):
        self.lifetime = lifetime
    def set_deptype(self, deptype):
        self.deptype = deptype
    def set_deprate_itc(self, deprate_itc):
        self.deprate_itc = str(deprate_itc)
    def set_deprate_ca(self, deprate_ca):
        self.deprate_ca = str(deprate_ca)
    def set_deprate_mgmt(self, deprate_mgmt):
        self.deprate_mgmt = str(deprate_mgmt)
    def set_depgl_itc(self, depgl_itc):
        self.depgl_itc = depgl_itc
    def set_depgl_ca(self, depgl_ca):
        self.depgl_ca = depgl_ca
    def set_depgl_mgmt(self, depgl_mgmt):
        self.depgl_mgmt = depgl_mgmt
    def set_depresgl_itc(self, depresgl_itc):
        self.depresgl_itc = depresgl_itc
    def set_depresgl_ca(self, depresgl_ca):
        self.depresgl_ca = depresgl_ca
    def set_depresgl_mgmt(self, depresgl_mgmt):
        self.depresgl_mgmt = depresgl_mgmt
    def set_apcatnodep_mgmt(self, apcatnodep_mgmt):
        self.apcatnodep_mgmt = apcatnodep_mgmt
    def set_apscatnodep_mgmt(self, apscatnodep_mgmt):
        self.apscatnodep_mgmt = apscatnodep_mgmt
    def set_apcatnodepres_mgmt(self, apcatnodepres_mgmt):
        self.apcatnodepres_mgmt = apcatnodepres_mgmt
    def set_apscatnodepres_mgmt(self, apscatnodepres_mgmt):
        self.apscatnodepres_mgmt = apscatnodepres_mgmt
    def set_deprate(self, deprate):
        self.deprate =str(deprate)
    def set_barcoderequired(self, barcoderequired):
        self.barcoderequired = barcoderequired
    def set_remarks(self, remarks):
        self.remarks = remarks



