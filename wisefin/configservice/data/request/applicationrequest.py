class ApplicationRequest:
    id = None
    name = None
    path = None
    type = None
    namespace = None

    def __init__(self, app_req):
        if 'id' in app_req:
            self.id = app_req['id']
        if 'name' in app_req:
            self.name = app_req['name']
        if 'path' in app_req:
            self.path = app_req['path']
        if 'namespace' in app_req:
            self.namespace = app_req['namespace']

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_path(self):
        return self.path

    def get_namespace(self):
        return self.namespace
