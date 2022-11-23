import json


class KYCRequest:
    id = None
    vendor_id = None
    kyc_entity = None
    organization_name = None
    sanctions_conducted = False
    match_found = False
    report_file_id = None
    authorised_signatories = None
    beneficial_owners = None
    created_by = None
    portal_flag = 0

    def __init__(self, kyc_obj):
        if 'id' in kyc_obj:
            self.id = kyc_obj['id']
        if 'vendor_id' in kyc_obj:
            self.vendor_id = kyc_obj['vendor_id']
        if 'kyc_entity' in kyc_obj:
            self.kyc_entity = kyc_obj['kyc_entity']
        if 'organization_name' in kyc_obj:
            self.organization_name = kyc_obj['organization_name']
        if 'sanctions_conducted' in kyc_obj:
            if kyc_obj['sanctions_conducted'] == 'Y':
                self.sanctions_conducted = True
        if 'match_found' in kyc_obj:
            if kyc_obj['match_found'] == 'Y':
                self.match_found = True
        if 'report_file_id' in kyc_obj:
            self.report_file_id = kyc_obj['report_file_id']
        if 'authorised_signatories' in kyc_obj:
            self.authorised_signatories = kyc_obj['authorised_signatories']
        if 'beneficial_owners' in kyc_obj:
            self.beneficial_owners = kyc_obj['beneficial_owners']
        if 'portal_flag' in kyc_obj:
            self.portal_flag = kyc_obj['portal_flag']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


    def get_id(self):
        return self.id

    def get_vendor_id(self):
        return self.vendor_id

    def get_kyc_entity(self):
        return self.kyc_entity

    def get_organization_name(self):
        return self.organization_name

    def get_sanctions_conducted(self):
        return self.sanctions_conducted

    def get_match_found(self):
        return self.match_found

    def get_report_file_id(self):
        return self.report_file_id

    def get_authorised_signatories(self):
        return self.authorised_signatories

    def get_beneficial_owners(self):
        return self.beneficial_owners

    def set_id(self, id):
        self.id = id

    def set_vendor_id(self, id):
        self.vendor_id = id

    def set_kyc_entity(self, kyc_entity):
        self.kyc_entity = kyc_entity

    def set_organization_name(self, organization_name):
        self.organization_name = organization_name

    def set_sanctions_conducted(self, sanctions_conducted):
        if sanctions_conducted == True:
            value = {'id': 'Y', 'name': 'YES'}
        else:
            value = {'id': 'N', 'name': 'NO'}
        self.sanctions_conducted = value

    def set_beneficial_owners(self, beneficial_owners):
        self.beneficial_owners = beneficial_owners

    def set_authorised_signatories(self, authorised_signatories):
        self.authorised_signatories = authorised_signatories

    def set_match_found(self, match_found):
        if match_found == True:
            value = {'id': 'Y', 'name': 'YES'}
        else:
            value = {'id': 'N', 'name': 'NO'}
        self.match_found = value

    def set_report_file_id(self, report_file_id):
        self.report_file_id = report_file_id

    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_portal_flag(self, portal_flag):
        self.portal_flag = portal_flag

    def get_portal_flag(self):
        return self.portal_flag

