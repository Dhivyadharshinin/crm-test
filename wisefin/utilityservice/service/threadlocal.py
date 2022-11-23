class NWisefinThread:
    __scope = None
    __token = None
    __entity_info = None
    __default = None
    __employee_id = None
    __user_id = None

    def __init__(self, scope_dict):
        if scope_dict is not None:
            self.__scope = scope_dict
            self.__token = scope_dict['token']
            self.__entity_info = scope_dict['entity_info']
            self.__default = scope_dict['default']
            self.__employee_id = scope_dict['employee_id']
            self.__user_id = scope_dict['user_id']

    def _scope(self):
        return self.__scope

    def _token(self):
        return self.__token

    def _entity_info(self):
        return self.__entity_info

    def _default(self):
        return self.__default

    def _employee_id(self):
        return self.__employee_id

    def _user_id(self):
        return self.__user_id

    def _entity_id(self):
        return self.__default['entity']['id']

    def _entity_name(self):
        return self.__default['entity']['name']

    def _schema(self):
        return self.__default['schema']['name']

    def _app_schema(self, app_namespace):
        schema = None
        entity_id = self._entity_id()
        for entity in self.__entity_info:
            if entity['application']['namespace'] == app_namespace and (entity['entity']['id'] == entity_id):
                schema = entity['schema']['name']
        return schema

    def _current_app_schema(self):
        schema = None
        namespace = self._get_namespace()
        entity_id = self._entity_id()
        if namespace is None:
            return None
        else:
            for entity in self.__entity_info:
                if (entity['application']['namespace'] == namespace) and (entity['entity']['id'] == entity_id):
                    schema = entity['schema']['name']
            return schema

    def _app_schema_bync(self, namespace, entity_id):
        schema = None
        if (entity_id is None) or (namespace is None):
            return None
        else:
            for entity in self.__entity_info:
                if (entity['application']['namespace'] == namespace) and (entity['entity']['id'] == entity_id):
                    schema = entity['schema']['name']
            return schema

    def _set_namespace(self, namespace):
        self.namespace = namespace

    def _get_namespace(self):
        return self.namespace
