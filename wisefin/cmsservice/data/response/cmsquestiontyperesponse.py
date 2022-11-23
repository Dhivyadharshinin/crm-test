import json

class Cmsquestiontyperesponse:
    id = None
    question_type_id = None
    vendor_id = None
    cat_id = None
    subcat_id = None
    group_id = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id
    def set_question_type_id(self,question_type_id):
        self.question_type_id = question_type_id
    def set_vendor_id(self,vendor_id):
        self.vendor_id = vendor_id
    def set_cat_id(self,cat_id):
        self.cat_id = cat_id
    def set_subcat_id(self,subcat_id):
        self.subcat_id = subcat_id
    def set_group_id(self,group_id):
        self.group_id = group_id

class Cmsquestypemapresponse:
    id = None
    question_id = None
    mapping_id = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id
    def set_question_id(self,question_id):
        self.question_id = question_id
    def set_mapping_id(self,mapping_id):
        self.mapping_id = mapping_id

class QuestionnaireTimerResponse:
    id = None
    timer_on,parallel_approval= None,None
    tag_timer = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_timer_on(self, timer_on):
        self.timer_on = timer_on

    def set_tag_timer(self, tag_timer):
        self.tag_timer = tag_timer

    def set_parallel_approval(self, parallel_approval):
        self.parallel_approval = parallel_approval