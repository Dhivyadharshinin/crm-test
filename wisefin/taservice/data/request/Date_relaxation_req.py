class Date_relaxation_req:
    tour_id= None
    status = None
    id=None
    comments=None
    insured=None
    insurance_no=None


    def __init__(self,obj):
        if 'tour_id' in obj:
            self.tour_id=obj['tour_id']
        if 'status' in obj:
            self.status=obj['status']
        if 'id' in obj:
            self.id=obj['id']
        if 'comments' in obj:
            self.comments=obj['comments']
        if 'insured' in obj:
            self.insured=obj['insured']
        if 'insurance_no' in obj:
            self.insurance_no=obj['insurance_no']

    def get_tour_id(self):
        return self.tour_id
    def get_status(self):
        return self.status
    def get_id(self):
        return self.id
    def get_comments(self):
        return self.comments
    def get_insured(self):
        return self.insured
    def get_insurance_no(self):
        return self.insurance_no
