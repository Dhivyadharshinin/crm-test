import json


class StateResponse:
    id = None
    code = None
    name = None
    country_id = None
    created_by = None
    updated_by = None
    status = None
    district = None
    city= None
    country_name=None
    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_name(self, name):
        self.name = name
    def set_country_id(self, country_id):
        self.country_id = country_id

    def set_status(self, status):
        self.status = status

    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_updated_by(self, updated_by):
        self.updated_by = updated_by
    def set_country_name(self,country_name):
        self.country_name=country_name

    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_name(self):
        return self.name

    def get_country_id(self):
        return self.country_id

    def get_status(self):
        return self.status
    def get_created_by(self):
        return self.created_by
    def get_updated_by(self):
        return self.updated_by

    def set_district(self, district):
        self.district = district

    def set_city(self, city):
        self.city = city