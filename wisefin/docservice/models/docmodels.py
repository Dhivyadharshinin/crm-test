from django.db import models
from django.utils.timezone import now
from db.vsolvmodels import VsolvModels


class MemoDocuments(VsolvModels):
    # document = models.FileField(null=True, upload_to='memo/')
    file_name = models.CharField(max_length=512)
    gen_file_name = models.CharField(max_length=512, null=True)
    size = models.IntegerField(default=-1)
    rel_id = models.IntegerField(default=-1)
    rel_type = models.IntegerField(default=-1)
    created_date = models.DateTimeField(default=now)
    document = models.FileField(null=True, upload_to='Memo/')


class VendorDocuments(VsolvModels):
    file_name = models.CharField(max_length=512)
    gen_file_name = models.CharField(max_length=512, null=True)
    size = models.IntegerField(default=-1)
    rel_id = models.IntegerField(default=-1)
    rel_type = models.IntegerField(default=-1)
    created_date = models.DateTimeField(default=now)
    document = models.FileField(null=True, upload_to='Vendor/')


class InwardDocuments(VsolvModels):
    file_name = models.CharField(max_length=512)
    gen_file_name = models.CharField(max_length=512, null=True)
    size = models.IntegerField(default=-1)
    rel_id = models.IntegerField(default=-1)
    rel_type = models.IntegerField(default=-1)
    created_date = models.DateTimeField(default=now)
    document = models.FileField(null=True, upload_to='Inward/')


class ProofingDocuments(VsolvModels):
    file_name = models.CharField(max_length=512)
    gen_file_name = models.CharField(max_length=512, null=True)
    size = models.IntegerField(default=-1)
    rel_id = models.IntegerField(default=-1)
    rel_type = models.IntegerField(default=-1)
    created_date = models.DateTimeField(default=now)
    document = models.FileField(null=True, upload_to='Proofing/')


class PdDocuments(VsolvModels):
    file_name = models.CharField(max_length=512)
    gen_file_name = models.CharField(max_length=512, null=True)
    size = models.IntegerField(default=-1)
    rel_id = models.IntegerField(default=-1)
    rel_type = models.IntegerField(default=-1)
    created_date = models.DateTimeField(default=now)
    document = models.FileField(null=True, upload_to='Pd/')


class PrDocuments(VsolvModels):
    file_name = models.CharField(max_length=512)
    gen_file_name = models.CharField(max_length=512, null=True)
    size = models.IntegerField(default=-1)
    rel_id = models.IntegerField(default=-1)
    rel_type = models.IntegerField(default=-1)
    created_date = models.DateTimeField(default=now)
    document = models.FileField(null=True, upload_to='Pr/')


class SgDocuments(VsolvModels):
    file_name = models.CharField(max_length=512)
    gen_file_name = models.CharField(max_length=512, null=True)
    size = models.IntegerField(default=-1)
    rel_id = models.IntegerField(default=-1)
    rel_type = models.IntegerField(default=-1)
    created_date = models.DateTimeField(default=now)
    document = models.FileField(null=True, upload_to='Sg/')


class DtpcDocuments(VsolvModels):
    file_name = models.CharField(max_length=512)
    gen_file_name = models.CharField(max_length=512, null=True)
    size = models.IntegerField(default=-1)
    rel_id = models.IntegerField(default=-1)
    rel_type = models.IntegerField(default=-1)
    created_date = models.DateTimeField(default=now)
    document = models.FileField(null=True, upload_to='Dtpc/')


class TADocs(VsolvModels):
    file_name = models.CharField(max_length=512)
    gen_file_name = models.CharField(max_length=512, null=True)
    size = models.IntegerField(default=-1)
    rel_id = models.IntegerField(default=-1)
    rel_type = models.IntegerField(default=-1)
    created_date = models.DateTimeField(default=now)
    document = models.FileField(null=True, upload_to='TA/')


class FADocs(VsolvModels):
    file_name = models.CharField(max_length=512)
    gen_file_name = models.CharField(max_length=512, null=True)
    size = models.IntegerField(default=-1)
    rel_id = models.IntegerField(default=-1)
    rel_type = models.IntegerField(default=-1)
    created_date = models.DateTimeField(default=now)
    document = models.FileField(null=True, upload_to='Fa/')


class APDocuments(VsolvModels):
    file_name = models.CharField(max_length=512)
    gen_file_name = models.CharField(max_length=512, null=True)
    size = models.IntegerField(default=-1)
    rel_id = models.IntegerField(default=-1)
    rel_type = models.IntegerField(default=-1)
    created_date = models.DateTimeField(default=now)
    document = models.FileField(null=True, upload_to='Ap/')


class EcfDocuments(VsolvModels):
    file_name = models.CharField(max_length=512)
    gen_file_name = models.CharField(max_length=512, null=True)
    size = models.IntegerField(default=-1)
    rel_id = models.IntegerField(default=-1)
    rel_type = models.IntegerField(default=-1)
    created_date = models.DateTimeField(default=now)
    document = models.FileField(null=True, upload_to='ECF/')


class ReportDocuments(VsolvModels):
    file_name = models.CharField(max_length=512)
    gen_file_name = models.CharField(max_length=512, null=True)
    size = models.IntegerField(default=-1)
    rel_id = models.IntegerField(default=-1)
    rel_type = models.IntegerField(default=-1)
    created_date = models.DateTimeField(default=now)
    document = models.FileField(null=True, upload_to='Report/')


class JVDocuments(VsolvModels):
    file_name = models.CharField(max_length=512)
    gen_file_name = models.CharField(max_length=512, null=True)
    size = models.IntegerField(default=-1)
    rel_id = models.IntegerField(default=-1)
    rel_type = models.IntegerField(default=-1)
    created_date = models.DateTimeField(default=now)
    document = models.FileField(null=True, upload_to='JV/')


class MasterDocuments(VsolvModels):
    file_name = models.CharField(max_length=512)
    gen_file_name = models.CharField(max_length=512, null=True)
    size = models.IntegerField(default=-1)
    rel_id = models.IntegerField(default=-1)
    rel_type = models.IntegerField(default=-1)
    created_date = models.DateTimeField(default=now)
    document = models.FileField(null=True, upload_to='Master/')


class CMSDocuments(VsolvModels):
    file_name = models.CharField(max_length=512)
    gen_file_name = models.CharField(max_length=512, null=True)
    size = models.IntegerField(default=-1)
    rel_id = models.IntegerField(default=-1)
    rel_type = models.IntegerField(default=-1)
    created_date = models.DateTimeField(default=now)
    document = models.FileField(null=True, upload_to='CMS/')


class QuesDocuments(VsolvModels):
    file_name = models.CharField(max_length=512)
    gen_file_name = models.CharField(max_length=512, null=True)
    size = models.IntegerField(default=-1)
    rel_id = models.IntegerField(default=-1)
    rel_type = models.IntegerField(default=-1)
    created_date = models.DateTimeField(default=now)
    document = models.FileField(null=True, upload_to='QUES/')


class AttendanceDocuments(VsolvModels):
    file_name = models.CharField(max_length=512)
    gen_file_name = models.CharField(max_length=512, null=True)
    size = models.IntegerField(default=-1)
    rel_id = models.IntegerField(default=-1)
    rel_type = models.IntegerField(default=-1)
    created_date = models.DateTimeField(default=now)
    document = models.FileField(null=True, upload_to='ATD/')

class HRMSDocuments(VsolvModels):
    file_name = models.CharField(max_length=512)
    gen_file_name = models.CharField(max_length=512, null=True)
    size = models.IntegerField(default=-1)
    rel_id = models.IntegerField(default=-1)
    rel_type = models.IntegerField(default=-1)
    created_date = models.DateTimeField(default=now)
    document = models.FileField(null=True, upload_to='HRMS/')
