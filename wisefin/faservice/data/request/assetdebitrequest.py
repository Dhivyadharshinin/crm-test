import json

class AssetDebitRequest:

    id =  assetdetails_id = category_id = subcategory_id = glno = amount = None


    def __init__(self, assetdebit_data):
        if 'id' in assetdebit_data:
            self.id = assetdebit_data['id']
        if 'assetdetails_id' in assetdebit_data:
            self.assetdetails_id = assetdebit_data['assetdetails_id']
        if 'category_id' in assetdebit_data:
            self.category_id = assetdebit_data['category_id']
        if 'subcategory_id' in assetdebit_data:
            self.subcategory_id = assetdebit_data['subcategory_id']
        if 'glno' in assetdebit_data:
            self.glno = assetdebit_data['glno']
        if 'amount' in assetdebit_data:
            self.amount = assetdebit_data['amount']


    def get_id(self):
        return self.id
    def get_assetdetails_id(self):
        return self.assetdetails_id
    def get_category_id(self):
        return self.category_id
    def get_subcategory_id(self):
        return self.subcategory_id
    def get_glno(self):
        return self.glno
    def get_amount(self):
        return self.amount
