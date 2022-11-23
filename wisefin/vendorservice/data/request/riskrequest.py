class RiskRequest:
    id = None
    vendor_id = None
    risktype_id = None
    risktype_description = None
    risk_mitigant = None
    risk_mitigant_review = None
    portal_flag = 0

    def __init__(self, risk_obj):

        if 'id' in risk_obj:
            self.id = risk_obj['id']
        if 'vendor_id' in risk_obj:
            self.vendor_id = risk_obj['vendor_id']
        if 'risktype_id' in risk_obj:
            self.risktype_id = risk_obj['risktype_id']
        if 'risktype_description' in risk_obj:
            self.risktype_description = risk_obj['risktype_description']
        if 'risk_mitigant' in risk_obj:
            self.risk_mitigant = risk_obj['risk_mitigant']
        if 'risk_mitigant_review' in risk_obj:
            self.risk_mitigant_review = risk_obj['risk_mitigant_review']
        if 'portal_flag' in risk_obj:
            self.portal_flag = risk_obj['portal_flag']

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

    def get_portal_flag(self):
        return self.portal_flag
