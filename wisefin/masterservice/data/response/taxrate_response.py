import json
from masterservice.data.response.subtax_response import SubTaxResponse


class TaxRateResponse:
    id = None
    subtax_id = None
    code = None
    name = None
    rate = None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_name(self, name):
        self.name = name

    def set_subtax_id(self,subtax_id):
        self.subtax_id = subtax_id

    def set_subtax(self,subtax):
        subtax_data = SubTaxResponse()
        subtax_data.set_id(subtax.id)
        subtax_data.set_code(subtax.code)
        subtax_data.set_name(subtax.name)
        subtax_data.set_tax_id(subtax.tax_id)
        subtax_data.set_remarks(subtax.remarks)
        subtax_data.set_glno(subtax.glno)
        self.subtax_id = subtax_data

    def set_rate(self, rate):
        self.rate = rate
