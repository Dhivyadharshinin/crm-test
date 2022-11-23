import json ,time
from masterservice.util.masterutil import getzoneType

class StatezonecityResponse:
      id = None
      state= None
      statename = None
      zone = None
      count = None
      effectivefrom = None
      effectiveto = None



      def get(self):
            return json.dumps(self, default=lambda o: o.__dict__,
                              sort_keys=True, indent=4)

      def set_id(self, id):
            self.id = id

      def set_state(self, state):
            if state != None :
                  state ={"name":state.name,"id":state.id}
            self.state = state


      def set_zone(self,zone ):
            self.zone = getzoneType(zone)

      def set_count(self, count):
            self.count = count

      def set_effectivefrom(self, effectivefrom):
            if effectivefrom != None:
                  self.effectivefrom=int(time.mktime(effectivefrom.timetuple())*1000)
            else:
                  self.effectivefrom = effectivefrom

      def set_effectiveto(self, effectiveto):
            if effectiveto != None:
                  self.effectiveto= int(time.mktime(effectiveto.timetuple())*1000)
            else:
                  self.effectiveto = effectiveto

