from django.db import models
from db.vsolvmodels import VsolvModels

class MemoRequest(VsolvModels):
    subject = models.CharField(max_length=256)
    req_date = models.DateField()
    category = models.CharField(max_length=256)
    sub_category = models.CharField(max_length=256)
