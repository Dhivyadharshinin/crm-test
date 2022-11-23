class DepartmentRequest:
    id = None
    name = None
    code = None
    short_notation = None
    description = None

    def __init__(self, dept_obj):
        if 'id' in dept_obj:
            self.id = dept_obj['id']
        if 'name' in dept_obj:
            self.name = dept_obj['name']
        if 'short_notation' in dept_obj:
            self.short_notation = dept_obj['short_notation']
        if 'description' in dept_obj:
            self.description = dept_obj['description']

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_code(self):
        return self.code

    def get_description(self):
        return self.description

    def get_short_notation(self):
        return self.short_notation

class DepartmentSyncRequest:
    id = None
    dept_name = None
    dept_code = None

    def __init__(self, dept_obj):
        if 'id' in dept_obj:
            self.id = dept_obj['id']
        if 'dept_name' in dept_obj:
            self.name = dept_obj['dept_name']
            # notation = dept_obj['dept_name']
            # self.short_notation = notation[0:8]
        if 'dept_code' in dept_obj:
            self.code = dept_obj['dept_code']


    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_code(self):
        return self.code



class DepartmentuploadRequest:
    id = None
    name = None
    remarks = None
    def __init__(self, dept_obj):
        if 'id' in dept_obj:
            self.id = dept_obj['id']
        if 'name' in dept_obj:
            self.name = dept_obj['name']
        if 'remarks' in dept_obj:
            self.remarks = dept_obj['remarks']
    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_remarks(self):
        return self.remarks