from django.db import models
from django.utils.timezone import now
from db.vsolvmodels import VModels

# PRODUCT
class Product(VModels):
    code = models.CharField(max_length=16, null=True)
    name = models.CharField(max_length=128)
    details = models.CharField(max_length=120,null=True)
    logo = models.IntegerField(null=True)
    category_id = models.IntegerField(null=True)
    subcategory_id = models.IntegerField(null=True)
    additional_info = models.TextField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)

class AgentGroup(VModels):
    name = models.CharField(max_length=128)
    limit = models.IntegerField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)

class AgentGroupRule(VModels):
    agent=models.ForeignKey(AgentGroup,on_delete=models.SET_NULL,null=True)
    rule_type = models.IntegerField(null=True)
    rule_value= models.IntegerField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)

class AgentGroupEmployeeMapping(VModels):
    agent=models.ForeignKey(AgentGroup,on_delete=models.SET_NULL,null=True)
    employee_id =models.IntegerField()
    is_active=models.BooleanField(default=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)

# SOURCE
class Source(VModels):
    code = models.CharField(max_length=16, null=True)
    name = models.CharField(max_length=128)
    type=models.IntegerField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)

class CRMAddress(VModels):
    line1 = models.CharField(max_length=2048)
    line2 = models.CharField(max_length=2048, null=True)
    line3 = models.CharField(max_length=2048, null=True)
    pincode_id = models.IntegerField(null=True)
    city_id = models.IntegerField(null=True)
    district_id = models.IntegerField(null=True)
    state_id = models.IntegerField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)

# LEAD
class Lead(VModels):
    source = models.ForeignKey(Source,on_delete=models.SET_NULL,null=True)# source master
    code = models.CharField(max_length=16, null=True)
    first_name = models.CharField(max_length=120, null=True)
    middle_name = models.CharField(max_length=120, null=True)
    last_name = models.CharField(max_length=120, null=True)
    aadhaar_no = models.CharField(max_length=120, null=True)
    pan_no = models.CharField(max_length=120, null=True)
    dob = models.DateField(null=True)
    present_address = models.IntegerField(null=True)
    permanent_address = models.IntegerField(null=True)
    lead_status = models.SmallIntegerField(default=1)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)

class LeadFamilyInfo(VModels):
    lead = models.ForeignKey(Lead,on_delete=models.CASCADE)
    name = models.CharField(max_length=120, null=True)
    relationship = models.SmallIntegerField(null=True)
    dob = models.DateField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)

class LeadContactInfo(VModels):
    lead = models.ForeignKey(Lead,on_delete=models.CASCADE)
    c_value = models.CharField(max_length=60) # email/phone
    type = models.SmallIntegerField()
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)


class LeadAdditionalInfo(VModels):
    lead = models.ForeignKey(Lead,on_delete=models.CASCADE)
    key = models.CharField(max_length=120)
    value = models.CharField(max_length=120)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)


class BankAccount(VModels):
    bank_id = models.IntegerField()  # bankmaster
    branch_id = models.IntegerField(null=True)  # bankbranch
    account_number = models.IntegerField()
    ifsc_code = models.CharField(max_length=50, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)


class CRNDocuments(VModels):
    rel_id = models.IntegerField(default=-1)
    rel_type = models.IntegerField(default=-1)
    file_name = models.CharField(max_length=256)
    gen_file_name = models.CharField(max_length=512)
    file_id = models.CharField(max_length=64, null=True)
    type = models.IntegerField(null=True)
    status = models.SmallIntegerField(default=1)
    is_user = models.BooleanField(default=True)
    created_by = models.SmallIntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)

class LeadFieldHistory(VModels):
    text =  models.TextField(null=True)
    rel_id = models.IntegerField(default=-1)
    rel_type = models.IntegerField(default=-1)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)

class LeadSourceFile(VModels):
    source_id= models.IntegerField(null=True)
    file_id =models.IntegerField(null=True)
    duplicate_count = models.IntegerField(null=True)
    reject_count = models.IntegerField(null=True)
    new_count = models.IntegerField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)

# PRODUCT - LEAD MAPPING
class ProductLeadMapping(VModels):
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True)
    lead = models.ForeignKey(Lead,on_delete=models.SET_NULL,null=True)
    lead_status = models.SmallIntegerField(default=1)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)


# TASK
class ProductTaskTemplate(VModels):
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True)
    template_name= models.CharField(max_length=128)
    details =models.CharField(max_length=420)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)

class LeadTask(VModels):
    lead_map = models.ForeignKey(ProductLeadMapping,on_delete=models.SET_NULL,null=True)
    task = models.ForeignKey(ProductTaskTemplate,on_delete=models.SET_NULL,null=True)
    hold_period = models.DateField(null=True)
    completed_by = models.IntegerField(null=True)
    is_closed = models.BooleanField(default=False)
    task_status =models.SmallIntegerField(default=1)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)


class CodeGenHistory(VModels):
    ref_table = models.SmallIntegerField()
    ref_code = models.CharField(null=True,max_length=16)
    last_id =models.IntegerField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)

