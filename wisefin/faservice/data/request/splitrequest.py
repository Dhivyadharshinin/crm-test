class AssetSplitHeaderRequest:
    id = None
    assetdetailsid = None
    date = None
    assetsplitheader_value = None
    assetsplitheader_status = None
    reason = None

    def __init__(self, data_obj):
        if 'id' in data_obj:
            self.id = data_obj['id']
        if 'assetdetails_id' in data_obj:
            self.assetdetails_id = data_obj['assetdetails_id']
        if 'date' in data_obj:
            self.date = data_obj['date']
        if 'assetsplitheader_value' in data_obj:
            self.assetsplitheader_value = data_obj['assetsplitheader_value']
        if 'assetsplitheader_status' in data_obj:
            self.assetsplitheader_status = data_obj['assetsplitheader_status']
        if 'reason' in data_obj:
            self.reason = data_obj['reason']


    def get_id(self):
        return self.id

    def get_assetdetails_id(self):
        return self.assetdetails_id

    def get_date(self):
        return self.date

    def get_assetsplitheader_value(self):
        return self.assetsplitheader_value

    def get_assetsplitheader_statuse(self):
        return self.assetsplitheader_status

    def get_reason(self):
        return self.reason



class AssetSplitDetailsRequest:
    id = None
    assetsplitheader = None
    newassetdetailsid = None
    assetsplitdetails_value = None

    def __init__(self, data_obj):
        if 'id' in data_obj:
            self.id = data_obj['id']
        if 'assetsplitheader' in data_obj:
            self.assetsplitheader = data_obj['assetsplitheader']
        if 'newassetdetailsid' in data_obj:
            self.newassetdetailsid = data_obj['newassetdetailsid']
        if 'assetsplitdetails_value' in data_obj:
            self.assetsplitdetails_value = data_obj['assetsplitdetails_value']

    def get_id(self):
        return self.id

    def get_assetsplitheader(self):
        return self.assetsplitheader

    def get_newassetdetailsid(self):
        return self.newassetdetailsid

    def get_assetsplitdetails_value(self):
        return self.assetsplitdetails_value
