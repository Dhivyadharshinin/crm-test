import json
from django.utils.timezone import now

class EmpBankDetailsRequest:

    def empbankdetails_request(self, emp_obj, user_id, employee_id):

            data = dict()
            data['employee_id'] = employee_id
            if 'account_name' in emp_obj:
                data['account_name'] = emp_obj['account_name']
            if 'bank_id' in emp_obj:
                data['bank_id'] = emp_obj['bank_id']
            if 'bank_branch' in emp_obj:
                data['bank_branch'] = emp_obj['bank_branch']
            if 'account_no' in emp_obj:
                data['account_no'] = emp_obj['account_no']
            if 'ifsc' in emp_obj:
                data['ifsc'] = emp_obj['ifsc']

            if 'id' in emp_obj:
                data['id'] = emp_obj['id']
                data['updated_by'] = user_id
                data['updated_date'] = now()

            else:
                data['created_by'] = user_id

            return data