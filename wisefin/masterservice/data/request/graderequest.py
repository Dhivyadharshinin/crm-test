class GradeRequest:
    id=None
    name=None
    is_active=None
    code=None
    points=None

    def __init__(self,grade_obj):
        if 'id' in grade_obj:
            self.id=grade_obj['id']
        if 'name' in grade_obj:
            self.name= grade_obj['name']
        if 'is_active' in grade_obj:
            self.is_active=grade_obj['is_active']
        if 'code' in grade_obj:
            self.code = grade_obj['code']
        if 'points' in grade_obj:
            self.points = grade_obj['points']

    def get_id(self):
        return self.id
    def get_name(self):
        return self.name
    def get_is_active(self):
        return self.is_active
    def get_code(self):
        return self.code
    def get_points(self):
        return self.points



class DesignationGradeMappingRequest:
    id=None
    designation_id=None
    grade_id=None
    status=None
    created_by=None
    created_date=None
    updated_by=None
    updated_date=None

    def __init__(self,grade_obj):
        if 'id' in grade_obj:
            self.id=grade_obj['id']
        if 'designation_id' in grade_obj:
            self.designation_id=grade_obj['designation_id']
        if 'grade_id' in grade_obj:
            self.grade_id=grade_obj['grade_id']
        if 'status' in grade_obj:
            self.status=grade_obj['status']
        if 'created_by' in grade_obj:
            self.created_by=grade_obj['created_by']
        if 'created_date' in grade_obj:
            self.created_date=grade_obj['created_date']
        if 'updated_by' in grade_obj:
            self.updated_by = grade_obj['updated_by']
        if 'updated_date' in grade_obj:
            self.updated_date = grade_obj['updated_date']

    def get_id(self):
        return self.id
    def get_designation_id(self):
        return self.designation_id
    def get_grade_id(self):
        return self.grade_id
    def get_status(self):
        return self.status
    def get_created_by(self):
        return self.created_by
    def get_created_date(self):
        return self.created_date
    def get_updated_by(self):
        return self.updated_by
    def get_updated_date(self):
        return self.updated_date