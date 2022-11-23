class AssetidRequest:
    id = None
    po_id = None
    podetails_id = None
    pono = None
    receiveddate = None
    grninwarddetails_id = None
    assetid = None
    source = None
    manufacturer = None
    serialno = None
    details = None

    def __init__(self, assetid_data):
        if 'id' in assetid_data:
            self.id = assetid_data['id']
        if 'po_id' in assetid_data:
            self.po_id = assetid_data['po_id']
        if 'podetails_id' in assetid_data:
            self.podetails_id = assetid_data['podetails_id']
        if 'pono' in assetid_data:
            self.pono = assetid_data['pono']
        if 'receiveddate' in assetid_data:
            self.receiveddate = assetid_data['receiveddate']
        if 'grninwarddetails_id' in assetid_data:
            self.grninwarddetails_id = assetid_data['grninwarddetails_id']

        if 'source' in assetid_data:
            self.source = assetid_data['source']
        if 'manufacturer' in assetid_data:
            self.manufacturer = assetid_data['manufacturer']
        if 'serialno' in assetid_data:
            self.serialno = assetid_data['serialno']
        if 'details' in assetid_data:
            self.details = assetid_data['details']
        if 'assetid' in assetid_data:
            self.assetid = assetid_data['assetid']

    def get_id(self):
        return self.id

    def get_po_id(self):
        return self.po_id

    def get_podetails_id(self):
        return self.podetails_id

    def get_pono(self):
        return self.pono

    def get_receiveddate(self):
        return self.receiveddate

    def get_grninwarddetails_id(self):
        return self.grninwarddetails_id

    def get_source(self):
        return self.source

    def get_manufacturer(self):
        return self.manufacturer

    def get_serialno(self):
        return self.serialno

    def get_details(self):
        return self.details

    def get_assetid(self):
        return self.assetid
