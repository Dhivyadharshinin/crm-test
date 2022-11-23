from django.db import models
from django.utils.timezone import now

from db.vsolvmodels import VsolvModels


class InwardHeader(VsolvModels):
    no = models.CharField(max_length=64)
    date = models.DateTimeField()
    channel_id = models.IntegerField(default=0)
    branch_id = models.IntegerField(null=True, default=0)
    courier_id = models.IntegerField(default=0)
    awbno = models.CharField(max_length=32,null=True)
    noofpockets = models.IntegerField()
    inwardfrom = models.CharField(max_length=64,null=True, blank=True)
    # receivedby = models.IntegerField(null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    inwardstatus = models.IntegerField(default=1)
class Meta:
    db_table="InwardHeader"


class EscalationType(VsolvModels):
    code = models.CharField(max_length=8, unique=True,null=True)
    name = models.CharField(max_length=64)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
class Meta:
    db_table = 'EscalationType'


class EscalationSubType(VsolvModels):
    code = models.CharField(max_length=8, unique=True,null=True)
    name = models.CharField(max_length=64)
    escalationtype = models.ForeignKey(EscalationType, on_delete=models.CASCADE)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
class Meta:
    db_table = 'EscalationSubType'


class ProductCategory(VsolvModels):
    code = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=32)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    is_sys = models.BooleanField(default=False)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    branch_id = models.IntegerField(default=0)


class ProductSubCategory(VsolvModels):
    product = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    code = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=32)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    is_sys = models.BooleanField(default=False)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class InwardTemplate(VsolvModels):
    template_name = models.CharField(max_length=64)
    template_content = models.TextField( null=True, blank=True)
    escalationsubtype = models.ForeignKey(EscalationSubType, on_delete=models.CASCADE)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class Meta:
    db_table="InwardTemplate"


class InwardDetails(VsolvModels):
    inwardheader = models.ForeignKey(InwardHeader, on_delete=models.CASCADE)
    packetno = models.IntegerField(default=0)
    doccount = models.IntegerField(default=0)
    docnumber = models.CharField(max_length=16)
    doctype_id = models.IntegerField(default=0)
    docsubject = models.CharField(max_length=128)
    pagecount = models.IntegerField(default=0)
    receivedfrom = models.CharField(max_length=64)
    remarks = models.CharField(max_length=32,null=True, blank=True)
    docstatus = models.IntegerField(default=1)
    status = models.SmallIntegerField(default=1)
    assigndept_id = models.IntegerField(null=True,default=0)
    assignemployee_id = models.IntegerField(default=0,null=True)
    actiontype = models.SmallIntegerField(null=True)
    tenor = models.IntegerField(null=True,default=0)
    docaction = models.SmallIntegerField(default=0)
    rmucode = models.CharField(max_length=32)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    assignremarks = models.CharField(max_length=32, null=True, blank=True)

class Meta:
    db_table="InwardDetails"


class CommentDoc(VsolvModels):
    inwarddetails = models.ForeignKey(InwardDetails, on_delete=models.CASCADE)
    employee_id = models.IntegerField()
    branch_id = models.IntegerField()
    comment = models.TextField(null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class InwardFiles(VsolvModels):
    inwarddetails = models.ForeignKey(InwardDetails, on_delete=models.CASCADE)
    commentdoc = models.ForeignKey(CommentDoc, on_delete=models.CASCADE, null=True)
    file_id = models.CharField(max_length=64, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class Meta:
    db_table="InwardFiles"


class InwardAudit(VsolvModels):
    ref_id = models.IntegerField()
    ref_type = models.CharField(max_length=28, null=True, blank=True)
    data = models.TextField( null=True, blank=True)
    user_id = models.IntegerField()
    req_status = models.SmallIntegerField()
    rel_refid = models.SmallIntegerField()
    rel_reftype = models.CharField(max_length=28, null=True, blank=True)
    action = models.CharField(max_length=28, null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)

class Meta:
    db_table="InwardAudit"


class Courier_Branch(VsolvModels):
    branch_id = models.IntegerField(default=0)
    courier_id = models.IntegerField(default=0)

class Meta:
    db_table="Courier_Branch"


class InwardQueue(VsolvModels):
    ref_id = models.IntegerField(null=True)
    ref_type = models.IntegerField(null=True)
    from_user_id = models.IntegerField(null=False)
    to_user_id = models.IntegerField(null=False)
    created_date = models.DateTimeField(default=now)
    comments = models.CharField(null=False, max_length=2048)
    status = models.SmallIntegerField(default=1)
    is_sys = models.BooleanField(default=False)
    remarks = models.CharField(max_length=128, null=True, blank=True)