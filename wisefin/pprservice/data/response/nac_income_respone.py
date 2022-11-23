import json

class Income_details_response:
    activeclient = None
    month = None
    disbursal_amount = None
    total_disbursalamount =None
    beginning_fee_due = None
    fee_due = None
    collected_fee = None
    interest_amount =None
    eir_amount = None
    opening_pos = None
    closing_pos = None
    principal_gl = None
    interest_gl = None
    fee_gl = None
    eir_gl =None
    flag = None
    id=None
    status = None
    created_by = None
    created_date = None
    updated_by = None
    updated_date = None
    expensegroup_id = None
    name = None
    asset_id = None
    client_id = None
    product_id = None
    business_id = None
    apexpense_id = None
    category_id = None
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_name(self, name):
        self.name = name
    def set_activeclient(self, activeclient):
        self.activeclient_id = activeclient
    def set_month(self, month):
        self.month =month
    def set_average(self, average):
        self.average =average
    def set_average_own(self, average):
        self.average_own =average
    def set_average_enable(self, average):
        self.average_enable =average
    def set_growth(self, growth):
        self.growth =growth
    def set_disbursal_amount(self, disbursal_amount):
        self.disbursal_amount =disbursal_amount
    def set_disbursal_amount_owned(self, disbursal_amount):
        self.disbursal_amount_owned =disbursal_amount
    def set_disbursal_amount_enable(self, disbursal_amount):
        self.disbursal_amount_enable =disbursal_amount
    def set_total_disbursalamount(self, total_disbursalamount):
        self.total_disbursalamount =total_disbursalamount
    def set_volume(self, volume):
        self.volume =volume
    def set_volume_own(self, volume):
        self.volume_own =volume
    def set_volume_enable(self, volume):
        self.volume_enable =volume
    def set_total_disbursalamount_owned(self, total_disbursalamount):
        self.total_disbursalamount_owned =total_disbursalamount
    def set_total_disbursalamount_enable(self, total_disbursalamount):
        self.total_disbursalamount_enable =total_disbursalamount
    def set_beginning_fee_due(self,beginning_fee_due):
        self.beginning_fee_due = beginning_fee_due
    def set_fee_due(self,fee_due):
        self.fee_due = fee_due
    def set_interest_amount(self,interest_amount):
        self.interest_amount=interest_amount
    def set_amount(self,amount):
        self.amount=amount
    def set_eir_amount(self,eir_amount):
        self.eir_amount=eir_amount
    def set_opening_pos(self,opening_pos):
        self.opening_pos=opening_pos
    def set_opening_pos_own(self,opening_pos):
        self.opening_pos_own=opening_pos
    def set_opening_pos_enable(self,opening_pos):
        self.opening_pos_enable=opening_pos
    def set_closing_pos(self,closing_pos):
        self.closing_pos=closing_pos
    def set_closing_pos_own(self,closing_pos):
        self.closing_pos_own=closing_pos
    def set_closing_pos_enable(self,closing_pos):
        self.closing_pos_enable=closing_pos
    def set_principal_gl(self,principal_gl):
        self.principal_gl=principal_gl
    def set_created_by(self,created_by):
        self.created_by=created_by
    def set_updated_by(self,updated_by):
        self.updated_by=updated_by

    def set_created_time(self, created_time):
        if created_time is None:
            self.created_time = created_time
        else:
            self.created_time = created_time.strftime("%Y-%b-%d %H:%M:%S")
            # self.from_time_ms =round(from_time.timestamp() * 1000)

    def set_updated_date(self, updated_date):
        if updated_date is None:
            self.updated_date = updated_date
        else:
            self.updated_date = updated_date.strftime("%Y-%b-%d %H:%M:%S")
            # self.from_time_ms =round(from_time.timestamp() * 1000)

    def set_interest_gl(self, interest_gl):
        self.interest_gl = interest_gl
    def set_fee_gl(self, fee_gl):
        self.fee_gl = fee_gl
    def set_eir_gl(self, eir_gl):
        self.eir_gl = eir_gl
    def set_flag(self, flag):
        self.flag = flag
    def set_fee_type(self, fee_type):
        self.fee_type = fee_type
    def set_assest_class(self, assest_class):
        self.assest_class = assest_class
    def set_collected_fee(self, collected_fee):
        self.collected_fee = collected_fee
    def set_assest_id(self, assest_id):
        self.assest_id = assest_id
    def set_expensegrp_id(self,expensegroup_id):
        self.expensegroup_id = expensegroup_id
    def set_apexpense_id(self,apexpense_id):
        self.apexpense_id = apexpense_id
    def set_category_id(self,category_id):
        self.category_id = category_id

class ppr_clientresponse:
    asset_id = None
    client_id = None
    product_id = None
    month = None
    bop = None
    new_client = None
    attrition = None
    closing = None
    amount = None
    status = None
    Asset_name = None
    client_name = None
    product_name = None
    type_id = None
    flag_id = None
    type_name = None
    flag_name = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_asset_id(self, asset_id):
        self.asset_id = asset_id

    def set_client_id(self, client_id):
        self.client_id = client_id

    def set_product_id(self, product_id):
        self.product_id = product_id

    def set_month(self, month):
        self.month = month

    def set_bop(self, bop):
        self.bop = bop

    def set_new_client(self, new_client):
        self.new_client = new_client

    def set_attrition(self, attrition):
        self.attrition = attrition

    def set_closing(self, closing):
        self.closing = closing

    def set_amount(self, amount):
        self.amount = amount

    def set_asset_name(self, asset_name):
        self.asset_name = asset_name

    def set_client_name(self, client_name):
        self.client_name = client_name

    def set_product_name(self, product_name):
        self.product_name = product_name

    def set_status(self,status):
        self.status = status

    def set_flag_id(self,flag_id):
        self.flag_id = flag_id

    def set_type_id(self,type_id):
        self.type_id = type_id

    def set_flag_name(self,flag_name):
        self.flag_name = flag_name

    def set_type_name(self,type_name):
        self.type_name = type_name

    def set_asset_dtls(self,number):
        if number == 1:
            self.asset_id = number
            self.asset_name = "AGRI"
        if number == 2:
            self.asset_id = number
            self.asset_name = "AHF"
        if number == 3:
            self.asset_id = number
            self.asset_name = "BD"
        if number == 4:
            self.asset_id = number
            self.asset_name = "CF"
        if number == 5:
            self.asset_id = number
            self.asset_name = "CONS"
        if number == 6:
            self.asset_id = number
            self.asset_name = "CORP"
        if number == 7:
            self.asset_id = number
            self.asset_name = "INTER_COMPANY"
        if number == 8:
            self.asset_id = number
            self.asset_name = "MFI"
        if number == 9:
            self.asset_id = number
            self.asset_name = "OTH"
        if number == 10:
            self.asset_id = number
            self.asset_name = "SBL"
        if number == 11:
            self.asset_id = number
            self.asset_name = "SME"
        if number == 12:
            self.asset_id = number
            self.asset_name = "VF"

        if number ==13:
            self.asset_id = number
            self.asset_name = "CC"
        if number==14:
            self.asset_id = number
            self.asset_name = "CL"
        if number==15:
            self.asset_id = number
            self.asset_name = "VL"
        if number==16:
            self.asset_id = number
            self.asset_name = "Consumer Finance"
        if number==17:
            self.asset_id = number
            self.asset_name = "CV"
        if number==18:
            self.asset_id = number
            self.asset_name = "Gold Loans"

class ppr_source_response:
    code = None
    name = None
    gl_no = None
    source_id = None
    head_group_id = None
    description = None
    date = None
    credit = None
    debit = None
    opening_balance = None
    closing_balance = None
    source_name = None
    head_group_name = None
    month_balance = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_code(self,code):
        self.code = code

    def set_name(self,name):
        self.name = name

    def set_gl_no(self,gl_no):
        self.gl_no = gl_no

    def set_id(self,id):
        self.id = id

    def set_source_id(self,source_id):
        self.source_id = source_id

    def set_head_group_id(self,head_group_id):
        self.head_group_id = head_group_id

    def set_description(self,description):
        self.description = description

    def set_date(self,date):
        self.date = date

    def set_credit(self,credit):
        self.credit = credit

    def set_debit(self,debit):
        self.debit = debit

    def set_opening_balance(self,opening_balance):
        self.opening_balance = opening_balance

    def set_closing_balance(self,closing_balance):
        self.closing_balance = closing_balance

    def set_source_name(self,source_name):
        self.source_name = source_name

    def set_head_group_name(self,head_group_name):
        self.head_group_name = head_group_name


    def set_month_balance(self,month_balance):
        self.month_balance = month_balance

