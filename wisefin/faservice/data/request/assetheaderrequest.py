class AssetHeaderRequest:
    id = None
    barcode = None
    date = None
    assetheadermonth = None
    assetheaderyear = None
    astvalbeforedeptot = None
    computeddeptot = None
    reviseddeptot = None
    revisedcbtot = None
    deprestot = None
    costtot = None
    valuetot = None
    type = None
    issale = None

    def __init__(self, assetheader_obj):
        if 'id' in assetheader_obj:
            self.id = assetheader_obj['id']
        if 'barcode' in assetheader_obj:
            self.barcode = assetheader_obj['barcode']
        if 'date' in assetheader_obj:
            self.date = assetheader_obj['date']
        if 'assetheadermonth' in assetheader_obj:
            self.assetheadermonth = assetheader_obj['assetheadermonth']
        if 'assetheaderyear' in assetheader_obj:
            self.assetheaderyear = assetheader_obj['assetheaderyear']
        if 'astvalbeforedeptot' in assetheader_obj:
            self.astvalbeforedeptot = assetheader_obj['astvalbeforedeptot']
        if 'computeddeptot' in assetheader_obj:
            self.computeddeptot = assetheader_obj['computeddeptot']
        if 'reviseddeptot' in assetheader_obj:
            self.reviseddeptot = assetheader_obj['reviseddeptot']
        if 'revisedcbtot' in assetheader_obj:
            self.revisedcbtot = assetheader_obj['revisedcbtot']
        if 'deprestot' in assetheader_obj:
            self.deprestot = assetheader_obj['deprestot']
        if 'costtot' in assetheader_obj:
            self.costtot = assetheader_obj['costtot']
        if 'valuetot' in assetheader_obj:
            self.valuetot = assetheader_obj['valuetot']
        if 'issale' in assetheader_obj:
            self.issale = assetheader_obj['issale']
        if 'type' in assetheader_obj:
            self.type = assetheader_obj['type']


    def get_id(self):
        return self.id
    def get_barcode(self):
        return self.barcode
    def get_date(self):
        return self.date
    def get_assetheadermonth(self):
        return self.assetheadermonth
    def get_assetheaderyear(self):
        return self.assetheaderyear
    def get_astvalbeforedeptot(self):
        return self.astvalbeforedeptot
    def get_computeddeptot(self):
        return self.computeddeptot
    def get_reviseddeptot(self):
        return self.reviseddeptot
    def get_revisedcbtot(self):
        return self.revisedcbtot
    def get_deprestot(self):
        return self.deprestot
    def get_costtot(self):
        return self.costtot
    def get_valuetot(self):
        return self.valuetot
    def get_type(self):
        return self.type
    def get_issale(self):
        return self.issale