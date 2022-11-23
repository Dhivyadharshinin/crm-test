import json


class Questionansmapresponse:
    id = None
    q_type = None
    project_id = None
    text = None
    order = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_q_type(self, q_type):
        self.q_type = q_type

    def set_project_id(self, project_id):
        self.project_id = project_id

    def set_text(self, text):
        self.text = text

    def set_order(self, order):
        self.order = order


class Projectproquesresponse:
    id = None
    question_id = None
    answer = None
    ref_type = None
    ref_id = None
    val_type = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_question_id(self, question_id):
        self.question_id = question_id

    def set_answer(self, answer):
        self.answer = answer

    def set_ref_type(self, ref_type):
        self.ref_type = ref_type

    def set_ref_id(self, ref_id):
        self.ref_id = ref_id

    def set_val_type(self, val_type):
        self.val_type = val_type


class CMSActivityresponse:
    id = None
    proposal_id = None
    supplier_code = None
    type = None
    name = None
    description = None
    start_date = None
    end_date = None
    contract_spend = None
    rm = None
    fidelity = None
    bidding = None
    raisor = None
    approver = None
    productname = None
    category = None
    subcategory = None
    is_user = None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_proposal_id(self, proposal_id):
        self.proposal_id = proposal_id
    def set_supplier_code(self, supplier_code):
        self.supplier_code = supplier_code
    def set_type(self, type):
        self.type = type
    def set_name(self, name):
        self.name = name
    def set_description(self, description):
        self.description = description
    def set_start_date(self, start_date):
        start_date = str(start_date)
        self.start_date = start_date
    def set_end_date(self, end_date):
        end_date = str(end_date)
        self.end_date = end_date
    def set_contract_spend(self, contract_spend):
        self.contract_spend = contract_spend
    def set_rm(self, rm,arr):
        self.rm = None
        for i in arr:
            if i['id']==rm:
                self.rm = i
                break

    def set_fidelity(self, fidelity):
        self.fidelity = fidelity
    def set_bidding(self, bidding):
        self.bidding = bidding
    def set_raisor(self, raisor,arr):
        self.raisor = None
        for i in arr:
            if i['id'] == raisor:
                self.raisor = i
                break

    def set_approver(self, approver,arr):
        self.approver = None
        for i in arr:
            if i['id'] == approver:
                self.approver = i
                break

    def set_productname(self, productname):
        self.productname = productname
    def set_category(self, category):
        self.category = category
    def set_subcategory(self, subcategory):
        self.subcategory = subcategory
    def set_is_user(self, is_user):
        self.is_user = is_user