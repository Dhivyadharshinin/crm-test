import json

class EntryTemplateRequest:

    id = None
    gl_no = None
    transaction = None
    Values = None
    value_to_taken = None
    wisefin_category = None
    wisefin_subcategory = None
    display = None

    def __init__(self, entrytemp_obj):
        if 'id' in entrytemp_obj:
            self.id = entrytemp_obj['id']
        if 'gl_no' in entrytemp_obj:
            self.gl_no = entrytemp_obj['gl_no']
        if 'transaction' in entrytemp_obj:
            self.transaction = entrytemp_obj['transaction']
        if 'Values' in entrytemp_obj:
            self.Values = entrytemp_obj['Values']
        if 'value_to_taken' in entrytemp_obj:
            self.value_to_taken = entrytemp_obj['value_to_taken']
        if 'wisefin_category' in entrytemp_obj:
            self.wisefin_category = entrytemp_obj['wisefin_category']
        if 'wisefin_subcategory' in entrytemp_obj:
            self.wisefin_subcategory = entrytemp_obj['wisefin_subcategory']
        if 'display' in entrytemp_obj:
            self.display = entrytemp_obj['display']

    def get_id(self):
        return self.id
    def get_gl_no(self):
        return self.gl_no
    def get_transaction(self):
        return self.transaction
    # def get_Values(self):
    #     return self.Values
    def get_value_to_taken(self):
        return self.value_to_taken
    def get_wisefin_category(self):
        return self.wisefin_category
    def get_wisefin_subcategory(self):
        return self.wisefin_subcategory
    def get_display(self):
        return self.display