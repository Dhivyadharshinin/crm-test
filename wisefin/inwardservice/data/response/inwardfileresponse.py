import json


class InwardFileResponse:
    id = None
    inwarddetails = None
    commentdoc = None
    file_id = None
    status = None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_inwarddetails(self, inwarddetails):
        self.inwarddetails = inwarddetails

    def set_commentdoc(self, commentdoc):
        self.commentdoc = commentdoc

    def set_file_id(self,file_id ):
        self.file_id = file_id

    def set_status(self, status):
        self.status = status
