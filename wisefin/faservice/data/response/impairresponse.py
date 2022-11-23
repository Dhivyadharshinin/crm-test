import json

class cgumapresponse:
    id = None
    name = None
    barcode = None
    cgu_status = None
    cgu_mappeddate = None
    cgu_value = None
    status = None
    created_by = None
    created_date = None
    updated_by = None
    updated_date = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_name(self, name):
        self.name = name

    def set_barcode(self, barcode):
        self.barcode = barcode

    def set_cgu_status(self, cgu_status):
        self.cgu_status = cgu_status

    def set_cgu_mappeddate(self, cgu_mappeddate):
        cgu_mappeddate = str(cgu_mappeddate)
        self.cgu_mappeddate = cgu_mappeddate

    def set_cgu_value(self, cgu_value):
        self.cgu_value = cgu_value

    def set_status(self, status):
        self.status = status

    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_created_date(self, created_date):
        created_date = str(created_date)
        self.created_date = created_date

    def set_updated_by(self, updated_by):
        self.updated_by = updated_by

    def set_updated_date(self, updated_date):
        updated_date = str(updated_date)
        self.updated_date = updated_date

class Cgumasterresponse:
    id = None
    name =None
    code = None
    status = None
    created_by = None
    created_date = None
    updated_by = None
    updated_date = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_name(self, name):
        self.name = name

    def set_code(self, code):
        self.code = code

    def set_status(self, status):
        self.status = status

    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_created_date(self, created_date):
        created_date = str(created_date)
        self.created_date = created_date

    def set_updated_by(self, updated_by):
        self.updated_by = updated_by

    def set_updated_date(self, updated_date):
        updated_date = str(updated_date)
        self.updated_date = updated_date

class impairdetailsresponse:
    id = None
    impair_id = None
    asset_barcode = None
    oldbassetvalue = None
    changedassetvalue = None
    status = None
    created_by =None
    created_date = None
    updated_by = None
    updated_date = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_impair_id(self, impair_id):
        self.impair_id = impair_id

    def set_asset_barcode(self, asset_barcode):
        self.asset_barcode = asset_barcode

    def set_oldbassetvalue(self, oldbassetvalue):
        self.oldbassetvalue = oldbassetvalue

    def set_changedassetvalue(self, changedassetvalue):
        self.changedassetvalue = changedassetvalue

    def set_status(self, status):
        self.status = status

    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_created_date(self, created_date):
        created_date = str(created_date)
        self.created_date = created_date

    def set_updated_by(self, updated_by):
        self.updated_by = updated_by

    def set_updated_date(self, updated_date):
        updated_date = str(updated_date)
        self.updated_date = updated_date

class ImpairHeaderresponse:
    id = None
    cgu_id = None
    old_cguvalue = None
    newcgu_value = None
    date = None
    asset_count = None
    reason = None
    impairheader_status = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_cgu_id(self, cgu_id):
        self.cgu_id = cgu_id

    def set_old_cguvalue(self, old_cguvalue):
        self.old_cguvalue = old_cguvalue

    def set_newcgu_value(self, newcgu_value):
        self.newcgu_value = newcgu_value

    def set_date(self, date):
        date = str(date)
        self.date = date

    def set_asset_count(self, asset_count):
        self.asset_count = asset_count

    def set_status(self, status):
        self.status = status

    def set_reason(self, reason):
        self.reason = reason

    def set_impairheader_status(self,impairheader_status):
        self.impairheader_status =impairheader_status


class impairassetresponse:
    id = None
    assetdetails_id = None
    date = None
    impairasset_status = None
    reason =None
    impairasset_value = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_assetdetails_id(self, assetdetails_id):
        self.assetdetails_id = assetdetails_id

    def set_date(self, date):
        date = str(date)
        self.date = date

    def set_impairasset_status(self, impairasset_status):
        self.impairasset_status = impairasset_status

    def set_reason(self, reason):
        self.reason = reason

    def set_impairasset_value(self, impairasset_value):
        self.impairasset_value = impairasset_value
