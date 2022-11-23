from django.db import models
from django.utils.timezone import now
#test
from db.vsolvmodels import VsolvModels

class JournalEntry(VsolvModels):
    jecrno = models.CharField(max_length=16, null=True)
    jemode = models.CharField(max_length=1,null=True)
    jebranch = models.CharField(max_length=64, null=True)
    jetype = models.SmallIntegerField(null=False)
    jerefno = models.CharField(max_length=16, null=True)
    jedescription = models.CharField(max_length=128,null=True)
    jetransactiondate = models.DateField(null=True,blank=True)
    jeamount = models.FloatField(default=0.00)
    jestatus = models.SmallIntegerField()
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class JournalDetailEntry(VsolvModels):
    jeentry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE)
    jedtype = models.SmallIntegerField(null=False)
    jeddescription = models.CharField(max_length=128,null=True)
    jedamount = models.FloatField(default=0.00)
    jedcat_code =models.CharField(max_length=16,null=True)
    jedsubcat_code = models.CharField(max_length=16,null=True)
    jedglno = models.CharField(max_length=64, null=True)
    jedcc_code = models.CharField(max_length=16, null=True)
    jedbs_code = models.CharField(max_length=16, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    jedbranch = models.CharField(max_length=64, null=True)

class JVAudit(VsolvModels):
    ref_id = models.IntegerField()
    ref_type = models.CharField(max_length=28, null=True, blank=True)
    data = models.TextField( null=True, blank=True)
    user_id = models.IntegerField()
    date = models.DateTimeField(null=True, blank=True)
    req_status = models.SmallIntegerField()
    rel_refid = models.SmallIntegerField()
    rel_reftype = models.CharField(max_length=28, null=True, blank=True)
    action = models.CharField(max_length=28, null=True, blank=True)

class JVFiles(VsolvModels):
    file_name = models.CharField(max_length=512)
    file_id = models.CharField(max_length=100,default=-1)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    jvfile = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, null=True)


class JVQueue(VsolvModels):
    ref_id = models.IntegerField(default=6)
    ref_type = models.IntegerField(default=6)
    from_user_id = models.IntegerField(null=False)
    to_user_id = models.IntegerField(null=False)
    created_date = models.DateTimeField(default=now)
    comments = models.CharField(null=False, max_length=2048)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    is_sys = models.BooleanField(default=False)
