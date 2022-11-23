import json


class RiskResponse:
    id = None
    vendor_id = None
    risktype_id = None
    risktype_description = None
    risk_mitigant = None
    risk_mitigant_review = None
    modify_ref_id = None
    modify_status = None
    created_by = None
    portal_flag = 0

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_vendor_id(self, vendor_id):
        self.vendor_id = vendor_id

    def set_risktype_id(self, risktype_id):
        self.risktype_id = risktype_id

    def set_risktype_description(self, risktype_description):
        self.risktype_description = risktype_description

    def set_risk_mitigant(self, risk_mitigant):
        self.risk_mitigant = risk_mitigant

    def set_risk_mitigant_review(self, risk_mitigant_review):
        self.risk_mitigant_review = risk_mitigant_review

    def set_modify_ref_id(self, modify_ref_id):
        self.modify_ref_id = modify_ref_id

    def set_modify_status(self, modify_status):
        self.modify_status = modify_status

    def set_created_by(self, created_by):
        self.created_by = created_by

    def get_id(self):
        return self.id

    def get_vendor_id(self):
        return self.vendor_id

    def get_risktype_id(self):
        return self.risktype_id

    def get_risktype_description(self):
        return self.risktype_description

    def get_risk_mitigant(self):
        return self.risk_mitigant

    def get_risk_mitigant_review(self):
        return self.risk_mitigant_review

    def get_modify_ref_id(self):
        return self.modify_ref_id

    def get_modify_status(self):
        return self.modify_status

    def get_created_by(self):
        return self.created_by

    def get_portal_flag(self):
        return self.portal_flag

    def set_portal_flag(self, portal_flag):
        self.portal_flag = portal_flag