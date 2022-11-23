import json
class Glmap_res:
    id= None
    glno= None
    gl_description= None
    tourreason= None
    gender=None
    categorycode=None
    category_description=None
    subcategorycode=None
    subcategory_description=None
    status=None
    entity=1
    created_by=None
    created_date=None
    updated_by=None
    updated_date=None

    def set_id(self,id):
        self.id=id
    def set_glno(self,glno):
        self.glno=glno
    def set_gl_description(self,gl_description):
        self.gl_description=gl_description
    def set_tourreason(self,tourreason):
        self.tourreason=tourreason
    def set_gender(self,gender):
        self.gender=gender
    def set_categorycode(self,categorycode):
        self.categorycode=categorycode
    def set_category_description(self,category_description):
        self.category_description=category_description
    def set_subcategorycode(self,subcategorycode):
        self.subcategorycode=subcategorycode
    def set_subcategory_description(self,subcategory_description):
        self.subcategory_description=subcategory_description
    def set_status(self,status):
        self.status=status
    def set_entity(self,entity):
        self.entity=entity
    def set_updated_by(self,updated_by):
        self.updated_by=updated_by
    def set_created_by(self,created_by):
        self.created_by=created_by
    def set_created_date(self,created_date):
        self.created_date=created_date.strftime("%d-%b-%Y")
        self.created_date_ms =round(created_date.timestamp() * 1000)
    def set_updated_date(self,updated_date):
        self.updated_date=updated_date.strftime("%d-%b-%Y")
        self.updated_date_ms =round(updated_date.timestamp() * 1000)

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

class Dependent_res:
    id= None
    depname= None
    deprelation= None
    depempid= None
    tour_id=None
    travel_id=None
    claimreq_id=None
    dependentname=None
    isdepelig=None
    entity=1
    created_by=None
    created_date=None
    updated_by=None
    updated_date=None
    dependentid=None
    empid=None


    def set_id(self,id):
        self.id=id
    def set_depname(self,depname):
        self.depname=depname
    def set_deprelation(self,deprelation):
        self.deprelation=deprelation
    def set_depempid(self,depempid):
        self.depempid=depempid
    def set_empid(self,empid):
        self.empid=empid
    def set_tour_id(self,tour_id):
        self.tour_id=tour_id
    def set_travel_id(self,travel_id):
        self.travel_id=travel_id
    def set_claimreq_id(self,claimreq_id):
        self.claimreq_id=claimreq_id
    def set_dependentname(self,dependentname):
        self.dependentname=dependentname
    def set_dependentid(self,dependentid):
        self.dependentid=dependentid
    def set_isdepelig(self,isdepelig):
        self.isdepelig=isdepelig
    def set_entity(self,entity):
        self.entity=entity
    def set_updated_by(self,updated_by):
        self.updated_by=updated_by
    def set_created_by(self,created_by):
        self.created_by=created_by
    def set_created_date(self,created_date):
        self.created_date=created_date.strftime("%d-%b-%Y")
        self.created_date_ms =round(created_date.timestamp() * 1000)
    def set_updated_date(self,updated_date):
        self.updated_date=updated_date.strftime("%d-%b-%Y")
        self.updated_date_ms =round(updated_date.timestamp() * 1000)

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)


