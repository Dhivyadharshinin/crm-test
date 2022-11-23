class DepreciationRequest:
    id = None
    calculate_for = None
    from_date = None
    to_date = None
    deptype = None

    def __init__(self, depreciation_obj):
        if 'id' in depreciation_obj:
            self.id = depreciation_obj['id']
        if 'calculate_for' in depreciation_obj:
            self.calculate_for = depreciation_obj['calculate_for']
        if 'from_date' in depreciation_obj:
            self.from_date = depreciation_obj['from_date']
        if 'to_date' in depreciation_obj:
            self.to_date = depreciation_obj['to_date']
        if 'deptype' in depreciation_obj:
            self.deptype = depreciation_obj['deptype']
    def get_id(self):
        return self.id
    def get_calculate_for(self):
        return self.calculate_for
    def get_from_date(self):
        return self.from_date
    def get_to_date(self):
        return self.to_date

    def get_deptype(self):
        return self.deptype