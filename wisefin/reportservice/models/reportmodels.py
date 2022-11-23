from django.db import models
from django.utils.timezone import now
from db.vsolvmodels import VsolvModels


class ModuleDropdown(VsolvModels):
    module_code = models.CharField(max_length=32, null=False, blank=False)
    module_name = models.CharField(max_length=64, null=False, blank=False)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class ModuleNameDropdown(VsolvModels):
    reportname_moduleid = models.CharField(max_length=32, null=False, blank=False)
    reportname_code = models.CharField(max_length=64, null=False, blank=False)
    reportname_name = models.CharField(max_length=64, null=False, blank=False)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class ReportParameter(VsolvModels):
    reportemp_moduleid = models.CharField(max_length=32, null=False, blank=False)
    reportemp_modulenamedropdownid = models.CharField(max_length=64, null=False, blank=False)
    reportemp_empid = models.TextField(null=False)
    reportemp_name = models.TextField(default=0)
    reportemp_column = models.TextField(default=0)
    reportemp_filter = models.TextField(default=0)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)



class ReportDetails(VsolvModels):
    reportdetails_modulenamedropdownid = models.CharField(max_length=64, null=False, blank=False)
    reportdetails_reportemp_id = models.TextField(null=False)
    reportdetails_id = models.TextField(default=0)
    reportdetails_path = models.FileField(null=True, upload_to='Report/')
    reportdetails_status = models.TextField(default=0)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class StampTrailReport(VsolvModels):
    crno = models.CharField(max_length=64, null=False, blank=False)
    gl_no = models.IntegerField(null=False, blank=False)
    gl_code = models.CharField(max_length=64, null=False, blank=False)
    gl_description = models.CharField(max_length=128, null=False, blank=False)
    opening_balance = models.IntegerField(null=False, blank=False)
    debit = models.IntegerField(null=False, blank=False)
    credit = models.IntegerField(null=False, blank=False)
    closing_balance = models.IntegerField(null=False, blank=False)
    invoice_no = models.CharField(max_length=64, null=False, blank=False)
    invoice_date = models.DateTimeField(default=now)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class StampPayCount(VsolvModels):
    particular = models.CharField(max_length=128, null=False, blank=False)
    vendor_payment = models.IntegerField(null=False, blank=False)
    travel_claim = models.IntegerField(null=False, blank=False)
    rcm_payment = models.IntegerField(null=False, blank=False)
    statutory_payment = models.IntegerField(null=False, blank=False)
    foreign_payment = models.IntegerField(null=False, blank=False)
    total = models.IntegerField(null=False, blank=False)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

# class StampVendorReport(VsolvModels):
#     ref_id = models.IntegerField(null=False, blank=False)
#     invoice_no = models.CharField(max_length=64, null=False, blank=False)
#     invoice_date = models.DateField(null=False, blank=False)
#     total_amount = models.DecimalField(null=False, blank=False)
#     base_amount = models.DecimalField(null=False, blank=False)
#     tax_amount = models.DecimalField(null=False, blank=False)
#     tds_amount = models.DecimalField(null=False, blank=False)
#     liq_amount = models.DecimalField(null=False, blank=False)
#     supplier_name = models.CharField(max_length=64, null=False, blank=False)
#     credit_amount = models.DecimalField(null=False, blank=False)
#     debit_amount = models.DecimalField(null=False, blank=False)
#     bank_payment = models.IntegerField(null=False, blank=False)
#     payment_Date = models.DateField(null=False, blank=False)
#     opening_balance = models.IntegerField(null=False, blank=False)
#     closing_balance = models.IntegerField(null=False, blank=False)
#     status = models.SmallIntegerField(default=1)
#     created_by = models.IntegerField(null=False, blank=False)
#     created_date = models.DateTimeField(default=now)
#     updated_by = models.IntegerField(null=True, blank=True)
#     updated_date = models.DateTimeField(null=True, blank=True)

class StampVendorStatement(VsolvModels):
    supplier_id = models.IntegerField(null=False, blank=False)
    closingbalance = models.DecimalField(max_digits=16, decimal_places=2,default=0)
    openingbalance = models.DecimalField(max_digits=16, decimal_places=2,default=0)
    date=models.DateTimeField(default=now)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class VendorModuleEOD(VsolvModels):
    date = models.DateTimeField(null=True, blank=True)
    eodflag = models.SmallIntegerField(default=0)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)