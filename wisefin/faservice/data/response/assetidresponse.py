import json
from faservice.util.fautil import get_sourcetype

class AssetidResponse:
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
    received = False
    captalised =False


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_po_id(self, po_id):
        self.po_id = po_id
    def set_podetails_id(self,podetails_id):
        self.podetails_id = podetails_id
    def set_pono(self, pono):
        self.pono = pono
    def set_receiveddate(self, receiveddate):
        self.receiveddate =receiveddate
    def set_grninwarddetails_id(self, grninwarddetails_id):
        self.grninwarddetails_id = grninwarddetails_id
    def set_source(self, source):
        source=get_sourcetype(source)
        self.source = source
    def set_assetid(self,assetid):
        self.assetid = assetid

    def set_manufacturer(self, manufacturer):
        self.manufacturer =manufacturer
    def set_serialno(self, serialno):
        self.serialno = serialno
    def set_details(self, details):
        self.details = details

    def set_received(self,received):
        self.received = received
    def set_captalised(self,captalised):
        self.captalised = captalised