class Glmap_req:
    id= None
    glno= None
    gl_description = None
    tourreason = None
    gender = None
    categorycode = None
    category_description = None
    subcategorycode = None
    subcategory_description = None
    entity = 1


    def __init__(self,hol_obj):
        if 'id' in hol_obj:
            self.id=hol_obj['id']
        if 'glno' in hol_obj:
            self.glno=hol_obj['glno']
        if 'gl_description' in hol_obj:
            self.gl_description=hol_obj['gl_description']
        if 'tourreason' in hol_obj:
            self.tourreason=hol_obj['tourreason']
        if 'gender' in hol_obj:
            self.gender=hol_obj['gender']
        if 'categorycode' in hol_obj:
            self.categorycode=hol_obj['categorycode']
        if 'category_description' in hol_obj:
            self.category_description=hol_obj['category_description']
        if 'subcategorycode' in hol_obj:
            self.subcategorycode=hol_obj['subcategorycode']
        if 'subcategory_description' in hol_obj:
            self.subcategory_description=hol_obj['subcategory_description']
        if 'entity' in hol_obj:
            self.entity=hol_obj['entity']


    def get_id(self):
        return self.id
    def get_glno(self):
        return self.glno
    def get_gl_description(self):
        return self.gl_description
    def get_tourreason(self):
        return self.tourreason
    def get_gender(self):
        return self.gender
    def get_categorycode(self):
        return self.categorycode
    def get_category_description(self):
        return self.category_description
    def get_subcategorycode(self):
        return self.subcategorycode
    def get_subcategory_description(self):
        return self.subcategory_description
    def get_entity(self):
        return self.entity

class Dependent_req:
    id = None
    depname = None
    deprelation = None
    depempid = None
    tour_id = None
    travel_id = None
    claimreq_id = None
    dependentname = None
    isdepelig = None
    entity = 1
    created_by = None
    created_date = None
    updated_by = None
    updated_date = None
    dependentid=None
    empid=None


    def __init__(self,dep_obj):
        if 'id' in dep_obj:
            self.id=dep_obj['id']
        if 'depname' in dep_obj:
            self.depname=dep_obj['depname']
        if 'deprelation' in dep_obj:
            self.deprelation=dep_obj['deprelation']
        if 'depempid' in dep_obj:
            self.depempid=dep_obj['depempid']
        if 'tour_id' in dep_obj:
            self.tour_id=dep_obj['tour_id']
        if 'travel_id' in dep_obj:
            self.travel_id=dep_obj['travel_id']
        if 'claimreq_id' in dep_obj:
            self.claimreq_id=dep_obj['claimreq_id']
        if 'dependentname' in dep_obj:
            self.dependentname=dep_obj['dependentname']
        if 'isdepelig' in dep_obj:
            self.isdepelig=dep_obj['isdepelig']
        if 'entity' in dep_obj:
            self.entity=dep_obj['entity']
        if 'empid' in dep_obj:
            self.empid=dep_obj['empid']
        if 'dependentid' in dep_obj:
            self.dependentid=dep_obj['dependentid']
        if 'entity' in dep_obj:
            self.entity=dep_obj['entity']



