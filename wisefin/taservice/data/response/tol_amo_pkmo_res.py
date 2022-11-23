import json
class Tol_amo_pkmo_res:
    tol_amo=None

    def set_tol_amo(self,tol_amo):
        self.tol_amo=tol_amo

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)