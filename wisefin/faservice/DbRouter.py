import inspect
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
def get_var_from_stack(name) :
    for f in inspect.stack() :
        if name in f[0].f_locals : return f[0].f_locals[name]
    return None

class DBRouter:
    fa_label='faservice'
    def db_for_read(self, model, **hints):
        class FaDbGet(NWisefinThread):
            def __init__(self, scope):
                super().__init__(scope)
                self._set_namespace(ApplicationNamespace.FA_SERVICE)
        if (model._meta.app_label == self.fa_label) :
            request=get_var_from_stack('request')
            fa_db=FaDbGet(request.scope)
            return fa_db._current_app_schema()

        return None
    def db_for_write(self, model, **hints):
        class FaDbGet(NWisefinThread):
            def __init__(self, scope):
                super().__init__(scope)
                self._set_namespace(ApplicationNamespace.FA_SERVICE)

        if (model._meta.app_label == self.fa_label):
            request = get_var_from_stack('request')
            fa_db = FaDbGet(request.scope)
            return  fa_db._current_app_schema()

        return None

    # def allow_migrate(self, db, app_label, model_name=None, **hints):
    #     class FaDbGet(NWisefinThread):
    #         def __init__(self, scope):
    #             super().__init__(scope)
    #             self._set_namespace(ApplicationNamespace.FA_SERVICE)
    #
    #     request = get_var_from_stack('request')
    #     fa_db = FaDbGet(request.scope)
    #     if db == 'fa_service':
    #         if app_label  in ['faservice']:
    #             return True
    #         else:
    #             return False
    #     elif app_label  in ['faservice']:
    #         return False
    #     return None