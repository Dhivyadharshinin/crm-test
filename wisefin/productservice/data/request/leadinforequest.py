from django.utils.timezone import now

class LeadFamilyInfoRequest:

    def leadfamilyinfo_request(self, lead_obj, user_id, lead_id):
        create_arr = []
        update_arr = []
        for data_obj in lead_obj:
            data = dict()
            data['lead_id'] = lead_id
            if 'name' in data_obj:
                data['name'] = data_obj['name']
            if 'relationship' in data_obj:
                data['relationship'] = data_obj['relationship']
            if 'dob' in data_obj:
                data['dob'] = data_obj['dob']

            if 'id' in data_obj:
                data['id'] = data_obj['id']
                data['updated_by'] = user_id
                data['updated_date'] = now()
                update_arr.append(data)
            else:
                data['created_by'] = user_id
                create_arr.append(data)
        val = {'update_arr': update_arr, 'create_arr': create_arr}
        return val

class LeadContactInfoRequest:

    def leadcontactinfo_request(self, lead_obj, user_id, lead_id):
        create_arr = []
        update_arr = []
        for data_obj in lead_obj:
            data = dict()
            data['lead_id'] = lead_id
            if 'c_value' in data_obj:
                data['c_value'] = data_obj['c_value']
            if 'type' in data_obj:
                data['type'] = data_obj['type']


            if 'id' in data_obj:
                data['id'] = data_obj['id']
                data['updated_by'] = user_id
                data['updated_date'] = now()
                update_arr.append(data)
            else:
                data['created_by'] = user_id
                create_arr.append(data)
        vall = {'update_arr': update_arr, 'create_arr': create_arr}
        return vall


class BankAccountRequest:

    def bankaccount_request(self, lead_obj, user_id, lead_id):
        create_arr = []
        update_arr = []
        for data_obj in lead_obj:
            data = dict()
            data['lead_id'] = lead_id
            if 'bank_id' in data_obj:
                data['bank_id'] = data_obj['bank_id']
            if 'branch_id' in data_obj:
                data['branch_id'] = data_obj['branch_id']
            if 'account_number' in data_obj:
                data['account_number'] = data_obj['account_number']
            if 'ifsc_code' in data_obj:
                data['ifsc_code'] = data_obj['ifsc_code']

            if 'id' in data_obj:
                data['id'] = data_obj['id']
                data['updated_by'] = user_id
                data['updated_date'] = now()
                update_arr.append(data)
            else:
                data['created_by'] = user_id
                create_arr.append(data)
        vall = {'update_arr': update_arr, 'create_arr': create_arr}
        return vall

class CrmAddressRequest:

    def crmaddress_request(self, lead_obj, user_id):
        data = dict()
        if 'line1' in lead_obj:
            data['line1'] = lead_obj['line1']
        if 'line2' in lead_obj:
            data['line2'] = lead_obj['line2']
        if 'line3' in lead_obj:
            data['line3'] = lead_obj['line3']
        if 'pincode_id' in lead_obj:
            data['pincode_id'] = lead_obj['pincode_id']
        if 'city_id' in lead_obj:
            data['city_id'] = lead_obj['city_id']
        if 'district_id' in lead_obj:
            data['district_id'] = lead_obj['district_id']
        if 'state_id' in lead_obj:
            data['state_id'] = lead_obj['state_id']
        if 'id' in lead_obj:
            data['updated_by'] = user_id
            data['updated_date'] = now()
        else:
            data['created_by'] = user_id
        return data




