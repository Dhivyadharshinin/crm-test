import json


class statezoneResponse:
      id = None
      state_id = None
      zone = None
      city_id = None





      def get(self):
            return json.dumps(self, default=lambda o: o.__dict__,
                              sort_keys=True, indent=4)

      def set_id(self, id):
            self.id = id

      def set_state_id(self, state_id):
            self.state_id = state_id

      def set_zone(self,zone ):
            self.zone = zone

      def set_city_id(self, city_id):
            self.city_id = city_id


