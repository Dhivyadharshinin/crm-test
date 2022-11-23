class ClientcodeRequest:
    id = None
    client_code = None
    client_name = None
    status = None
    rm_name = None
    entity =None

    def __init__(self, cli_data):
        if 'id' in cli_data:
            self.id = cli_data['id']
        if 'client_code' in cli_data:
            self.client_code = cli_data['client_code']
        if 'client_name' in cli_data:
            self.client_name = cli_data['client_name']
        if 'status' in cli_data:
            self.status = cli_data['status']
        if 'rm_name' in cli_data:
            self.rm_name = cli_data['rm_name']
        if 'entity' in cli_data:
            self.entity = cli_data['entity']


    def get_id(self):
        return self.id

    def get_client_code(self):
        return self.client_code

    def get_client_name(self):
        return self.client_name
    def get_status(self):
        return self.status
    def get_rm_name(self):
        return self.rm_name
    def get_entity(self):
        return self.entity

#test