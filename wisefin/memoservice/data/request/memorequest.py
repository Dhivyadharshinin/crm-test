class MemoReq:
    id = None
    subject = None
    req_date = None
    category = None
    sub_category = None

    def __init__(self, memo_data):
        if 'id' in memo_data:
            self.id = memo_data['id']
        if 'subject' in memo_data:
            self.subject = memo_data['subject']
        if 'req_date' in memo_data:
            self.req_date = memo_data['req_date']
        if 'category' in memo_data:
            self.category = memo_data['category']
        if 'sub_category' in memo_data:
            self.sub_category = memo_data['sub_category']

    def get_id(self):
        return self.id

    def get_subject(self):
        return self.subject

    def get_req_date(self):
        return self.req_date

    def get_category(self):
        return self.category

    def get_sub_category(self):
        return self.sub_category
