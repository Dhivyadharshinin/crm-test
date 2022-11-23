class Projectquesrequest:
    id = None
    q_type = None
    project_id = None
    text = None
    order = None

    def __init__(self,obj_ans):
        if 'id' in obj_ans:
            self.id=obj_ans['id']
        if 'q_type' in obj_ans:
            self.q_type=obj_ans['q_type']
        if 'project_id' in obj_ans:
            self.project_id=obj_ans['project_id']
        if 'text' in obj_ans:
            self.text=obj_ans['text']
        if 'order' in obj_ans:
            self.order=obj_ans['order']

    def get_id(self):
        return self.id
    def get_q_type(self):
        return self.q_type
    def get_project_id(self):
        return self.project_id
    def get_text(self):
        return self.text
    def get_order(self):
        return self.order

class Projectproquesrequest:
    id = None
    question_id = None
    answer = None
    ref_type = None
    ref_id = None
    val_type = None

    def __init__(self,obj_ans):
        if 'id' in obj_ans:
            self.id=obj_ans['id']
        if 'question_id' in obj_ans:
            self.question_id=obj_ans['question_id']
        if 'answer' in obj_ans:
            self.answer=obj_ans['answer']
        if 'ref_type' in obj_ans:
            self.ref_type=obj_ans['ref_type']
        if 'ref_id' in obj_ans:
            self.ref_id=obj_ans['ref_id']
        if 'val_type' in obj_ans:
            self.val_type = obj_ans['val_type']

    def get_id(self):
        return self.id
    def get_question_id(self):
        return self.question_id
    def get_answer(self):
        return self.answer
    def get_ref_type(self):
        return self.ref_type
    def get_ref_id(self):
        return self.ref_id
    def get_val_type(self):
        return self.val_type

class CMSActivityrequest:
    id = None
    project_id = None
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

    def __init__(self,obj_ans):
        if 'id' in obj_ans:
            self.id=obj_ans['id']
        if 'project_id' in obj_ans:
            self.project_id=obj_ans['project_id']
        if 'supplier_code' in obj_ans:
            self.supplier_code=obj_ans['supplier_code']
        if 'type' in obj_ans:
            self.type=obj_ans['type']
        if 'name' in obj_ans:
            self.name=obj_ans['name']
        if 'description' in obj_ans:
            self.description = obj_ans['description']
        if 'start_date' in obj_ans:
            self.start_date = obj_ans['start_date']
        if 'end_date' in obj_ans:
            self.end_date = obj_ans['end_date']
        if 'contract_spend' in obj_ans:
            self.contract_spend = obj_ans['contract_spend']
        if 'rm' in obj_ans:
            self.rm = obj_ans['rm']
        if 'fidelity' in obj_ans:
            self.fidelity = obj_ans['fidelity']
        if 'bidding' in obj_ans:
            self.bidding = obj_ans['bidding']
        if 'raisor' in obj_ans:
            self.raisor = obj_ans['raisor']
        if 'approver' in obj_ans:
            self.approver = obj_ans['approver']
        if 'productname' in obj_ans:
            self.productname = obj_ans['productname']
        if 'category' in obj_ans:
            self.category = obj_ans['category']
        if 'subcategory' in obj_ans:
            self.subcategory = obj_ans['subcategory']
        if 'is_user' in obj_ans:
            self.is_user = obj_ans['is_user']

    def get_id(self):
        return self.id
    def get_project_id(self):
        return self.project_id
    def get_supplier_code(self):
        return self.supplier_code
    def get_type(self):
        return self.type
    def get_name(self):
        return self.name
    def get_description(self):
        return self.description
    def get_start_date(self):
        return self.start_date
    def get_end_date(self):
        return self.end_date
    def get_contract_spend(self):
        return self.contract_spend
    def get_rm(self):
        return self.rm
    def get_fidelity(self):
        return self.fidelity
    def get_bidding(self):
        return self.bidding
    def get_raisor(self):
        return self.raisor
    def get_approver(self):
        return self.approver
    def get_productname(self):
        return self.productname
    def get_category(self):
        return self.category
    def get_subcategory(self):
        return self.subcategory
    def get_is_user(self):
        return self.is_user


