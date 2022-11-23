import json

class Commentsrequest:
    id = None
    ref_id = None
    ref_type = None
    comment = None
    type =  1
    is_user = 1
    reply_id = None

    def __init__(self,obj_cmt):
        if 'id' in obj_cmt:
            self.id=obj_cmt['id']
        if 'ref_id' in obj_cmt:
            self.ref_id = obj_cmt['ref_id']
        if 'ref_type' in obj_cmt:
            self.ref_type = obj_cmt['ref_type']
        if 'comment' in obj_cmt:
            self.comment = obj_cmt['comment']
        if 'type' in obj_cmt:
            self.type = obj_cmt['type']
        if 'is_user' in obj_cmt:
            self.is_user = obj_cmt['is_user']
        if 'reply_id' in obj_cmt:
            self.reply_id = obj_cmt['reply_id']

    def get_id(self):
        return self.id
    def get_ref_id(self):
        return self.ref_id
    def get_ref_type(self):
        return self.ref_type
    def get_comment(self):
        return self.comment
    def get_type(self):
        return self.type
    def get_is_user(self):
        return self.is_user
    def get_reply_id(self):
        return self.reply_id