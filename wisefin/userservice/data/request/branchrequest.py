import json

class EmployeeBranchRequest:
    id = None
    code = None
    name = None
    tanno = None
    glno = None
    stdno = None
    incharge = None
    address_id = None
    contact_id = None
    entity= None
    entity_detail =None
    gstin = None
    control_office_branch = None
    status = None
    assetcodeprimary=None
    
    def __init__(self, branch_obj):
        if 'id' in branch_obj:
            self.id = branch_obj['id']
        if 'code' in branch_obj:
            self.code = branch_obj['code']
        if 'name' in branch_obj:
            self.name = branch_obj['name']
        if 'tanno' in branch_obj:
            self.tanno = branch_obj['tanno']
        if 'glno' in branch_obj:
            self.glno = branch_obj['glno']
        if 'stdno' in branch_obj:
            self.stdno = branch_obj['stdno']
        if 'incharge' in branch_obj:
            self.incharge = branch_obj['incharge']
        if 'address_id' in branch_obj:
            self.address_id = branch_obj['address_id']
        if 'contact_id' in branch_obj:
            self.contact_id = branch_obj['contact_id']
        if 'entity' in branch_obj:
            self.entity = branch_obj['entity']
        if 'entity_detail' in branch_obj:
            self.entity_detail = branch_obj['entity_detail']
        if 'gstin' in branch_obj:
            self.gstin = branch_obj['gstin']
        if 'control_office_branch' in branch_obj:
            self.control_office_branch = branch_obj['control_office_branch']
        if 'status' in branch_obj:
            self.status = branch_obj['status']
        if 'assetcodeprimary' in branch_obj:
            self.assetcodeprimary = branch_obj['assetcodeprimary']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_name(self, name):
        self.name = name

    def set_tanno(self, tanno):
        self.tanno = tanno

    def set_glno(self, glno):
        self.glno = glno

    def set_stdno(self, stdno):
        self.stdno = stdno

    def set_incharge(self, incharge):
        self.incharge = incharge

    def set_address_id(self, address_id):
        self.address_id = address_id

    def set_contact_id(self, contact_id):
        self.contact_id = contact_id

    def set_assetcodeprimary(self, assetcodeprimary):
        self.assetcodeprimary = assetcodeprimary

    def get_id(self):
        return self.id
    def get_status(self):
        return self.status

    def get_code(self):
        return self.code

    def get_tanno(self):
        return self.tanno

    def get_glno(self):
        return self.glno

    def get_name(self):
        return self.name

    def get_stdno(self):
        return self.stdno

    def get_incharge(self):
        return self.incharge

    def get_address_id(self):
        return self.address_id

    def get_contact_id(self):
        return self.contact_id

    def get_entity(self):
        return self.entity

    def get_entity_detail(self):
        return self.entity_detail

    def get_gstin(self):
        return self.gstin

    def get_control_office_branch(self):
        return self.control_office_branch

    def get_assetcodeprimary(self):
        return self.assetcodeprimary

class EmployeeBranchSyncRequest:
    id = None
    code = None
    name = None
    tanno = None
    glno = None
    stdno = None
    incharge = None
    address_id = None
    contact_id = None
    entity = None
    entity_detail = None
    gstin = None
    control_office_branch = None


    def __init__(self, branch_obj):
        if 'id' in branch_obj:
            self.id = branch_obj['id']
        if 'CODE' in branch_obj:
            self.code = branch_obj['CODE']
        if 'NAME' in branch_obj:
            if branch_obj['NAME'] == '':
                self.name = None
            else:
                self.name = branch_obj['NAME']
        if 'BRANCH_TAN' in branch_obj:
            if branch_obj['BRANCH_TAN'] == '':
                self.tanno = None
            else:
                self.tanno = branch_obj['BRANCH_TAN']
        if 'GLNO' in branch_obj:
            if branch_obj['GLNO'] == '':
                self.glno = None
            else:
                self.glno = branch_obj['GLNO']
        if 'STD_CODE' in branch_obj:
            if branch_obj['STD_CODE'] == '':
                self.stdno = None
            else:
                self.stdno = branch_obj['STD_CODE']
        if 'INCHARGE' in branch_obj:
            if branch_obj['INCHARGE'] == '':
                self.incharge = None
            else:
                self.incharge = branch_obj['INCHARGE']
        if 'address_id' in branch_obj:
            self.address_id = branch_obj['address_id']
        if 'contact_id' in branch_obj:
            self.contact_id = branch_obj['contact_id']
        if 'ENTITY' in branch_obj:
            if branch_obj['ENTITY'] == '':
                self.entity = None
            else:
                self.entity = branch_obj['ENTITY']
        if 'ENTITY_DETAIL' in branch_obj:
            if branch_obj['ENTITY_DETAIL'] == '':
                self.entity_detail = None
            else:
                self.entity_detail = branch_obj['ENTITY_DETAIL']
        if 'GSTIN' in branch_obj:
            if branch_obj['GSTIN'] == '':
                self.gstin = None
            else:
                self.gstin = branch_obj['GSTIN']

        if 'CONTROL_OFFICE_BRANCH' in branch_obj:
            if branch_obj['CONTROL_OFFICE_BRANCH'] == '':
                self.control_office_branch = None
            else:
                self.control_office_branch = branch_obj['CONTROL_OFFICE_BRANCH']


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_tanno(self):
        return self.tanno

    def get_glno(self):
        return self.glno

    def get_name(self):
        return self.name

    def get_stdno(self):
        return self.stdno

    def get_incharge(self):
        return self.incharge

    def get_address_id(self):
        return self.address_id

    def get_contact_id(self):
        return self.contact_id

    def get_entity(self):
        return self.entity

    def get_entity_detail(self):
        return self.entity_detail

    def get_gstin(self):
        return self.gstin

    def get_control_office_branch(self):
        return self.control_office_branch

class BranchLogRequest:

    maindata = None
    range_from = None
    range_to = None

    def __init__(self, user_obj):
        if 'ESM_BRANCH_Master' in user_obj:
            self.maindata = user_obj['ESM_BRANCH_Master']
        if 'RangeTo' in user_obj:
            self.range_to = user_obj['RangeTo']
        if 'RangeFrom' in user_obj:
            self.range_from = user_obj['RangeFrom']

    def get_maindata(self):
        return str(self.maindata)
    def get_range_from(self):
        return self.range_from
    def get_range_to(self):
        return self.range_to
