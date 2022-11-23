import datetime


class SourceRequest:


    def source_request(self, user_obj, emp_id):
        data = dict()

        if 'name' in user_obj:
            data['name'] = user_obj['name']
        if 'type' in user_obj:
            data['type']=user_obj['type']
        if 'id' in user_obj:
            data['id']= user_obj['id']
            data['updated_by'] = emp_id
            data['updated_date'] = datetime.datetime.now()
        else:
            data['created_by'] = emp_id

        return data


