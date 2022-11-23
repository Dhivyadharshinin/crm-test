from django.db import models
from datetime import datetime
from django.utils.timezone import now
from masterservice.models.mastermodels import Product

from db.vsolvmodels import VsolvModels

class customFloatField(models.Field):
    def db_type(self, connection):
        return 'float'


class Vendor(models.Model):
    name = models.CharField(max_length=128)
    panno = models.CharField(max_length=16)
    gstno = models.CharField(max_length=16, null=True, blank=True)
    adhaarno = models.CharField(max_length=12, null=True, blank=True)
    emaildays = models.IntegerField(default=1,null=True)
    composite = models.IntegerField()
    director_count = models.IntegerField(default=0,null=True)
    vendor_status = models.SmallIntegerField(default=1)
    code = models.CharField(max_length=128)
    comregno = models.CharField(max_length=126, null=True, blank=True)
    group = models.IntegerField()
    custcategory_id = models.IntegerField(default=-1)
    classification = models.IntegerField()
    type = models.IntegerField()
    website = models.CharField(max_length=126, null=True, blank=True)
    activecontract = models.CharField(max_length=126)
    nocontract_reason = models.CharField(max_length=126, null=True, blank=True)
    contractdate_from = models.DateField(null=True, blank=True, default=None)
    contractdate_to = models.DateField(null=True, blank=True, default=None)
    aproxspend = models.FloatField()
    actualspend = models.FloatField()
    orgtype = models.IntegerField()
    renewal_date = models.DateField(null=True, blank=True, default=None)
    remarks = models.CharField(max_length=126, null=True, blank=True)
    requeststatus = models.SmallIntegerField(default=1)
    mainstatus = models.SmallIntegerField(default=1)
    rm_id = models.IntegerField(default=-1)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    modify_ref_id = models.IntegerField(default=-1)
    modify_status = models.SmallIntegerField(default=-1)
    modified_by = models.IntegerField(default=-1)
    is_delete = models.BooleanField(default=False)
    entity_id = models.BigIntegerField(null=True, blank=True)

    description = models.CharField(max_length=1040, null=True)
    risktype = models.SmallIntegerField(null=True)
    risktype_description = models.CharField(max_length=1040, null=True)
    risk_mitigant = models.CharField(max_length=1040, null=True)
    risk_mitigant_review = models.CharField(max_length=1040, null=True)
    portal_flag = models.BooleanField(default=False)
    portal_code = models.CharField(max_length=32, null=True)



class VendorQueue(VsolvModels):
    vendor_id = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    from_user_id = models.IntegerField(null=False)
    to_user_id = models.IntegerField(null=False)
    created_date = models.DateTimeField(default=now)
    comments = models.CharField(null=False, max_length=2048)
    status = models.SmallIntegerField(default=1)
    is_sys = models.BooleanField(default=False)
    portal_flag = models.BooleanField(default=False)



class VendorDirector(VsolvModels):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    d_sign = models.CharField(max_length=128, null=True)
    d_pan = models.CharField(max_length=16, null=True)
    d_sanctions = models.BooleanField(default=False)
    d_match = models.BooleanField(default=False)
    status = models.IntegerField(null=False, default=1)
    created_by = models.IntegerField(null=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    modify_ref_id = models.IntegerField(default=-1)
    modify_status = models.SmallIntegerField(default=-1)
    modified_by = models.IntegerField(default=-1)
    is_delete = models.BooleanField(default=False)
    portal_flag = models.BooleanField(default=False)



class VendorProfile(VsolvModels):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    year = models.IntegerField(null=True, blank=True)
    associate_year = models.IntegerField(null=True, blank=True)
    award_details = models.CharField(max_length=128, null=True, blank=True)
    permanent_employee = models.IntegerField(null=True, blank=True)
    temporary_employee = models.IntegerField(null=True, blank=True)
    total_employee = models.IntegerField(null=True, blank=True)
    branch = models.IntegerField()
    factory = models.IntegerField(null=True, blank=True)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    modify_ref_id = models.IntegerField(default=-1)
    modify_status = models.SmallIntegerField(default=-1)
    modified_by = models.IntegerField(default=-1)
    is_delete = models.BooleanField(default=False)
    portal_flag = models.BooleanField(default=False)



class VendorAddress(VsolvModels):
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)
    line1 = models.CharField(max_length=128)
    line2 = models.CharField(max_length=128, null=True, blank=True)
    line3 = models.CharField(max_length=128, null=True, blank=True)
    pincode_id = models.IntegerField(default=-1)
    city_id = models.IntegerField(default=-1)
    district_id = models.IntegerField(default=-1)
    state_id = models.IntegerField(default=-1)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    modify_ref_id = models.IntegerField(default=-1)
    modify_status = models.SmallIntegerField(default=-1)
    modified_by = models.IntegerField(default=-1)
    is_delete = models.BooleanField(default=False)
    portal_flag = models.BooleanField(default=False)



class VendorContact(VsolvModels):
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)
    type_id = models.IntegerField(default=-1)
    name = models.CharField(max_length=128)
    designation = models.CharField(max_length=128, null=True)
    landline = models.CharField(max_length=16, null=True, blank=True)
    landline2 = models.CharField(max_length=16, null=True, blank=True)
    mobile = models.CharField(max_length=16, null=True, blank=True)
    mobile2 = models.CharField(max_length=16, null=True, blank=True)
    email = models.CharField(max_length=128, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    wedding_date = models.DateField(null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    modify_ref_id = models.IntegerField(default=-1)
    modify_status = models.SmallIntegerField(default=-1)
    modified_by = models.IntegerField(default=-1)
    is_delete = models.BooleanField(default=False)
    portal_flag = models.BooleanField(default=False)



class VendorRelAddress(VsolvModels):
    line1 = models.CharField(max_length=128)
    line2 = models.CharField(max_length=128, null=True, blank=True)
    line3 = models.CharField(max_length=128, null=True, blank=True)
    pincode_id = models.IntegerField(default=-1)
    city_id = models.IntegerField(default=-1)
    district_id = models.IntegerField(default=-1)
    state_id = models.IntegerField(default=-1)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    modify_ref_id = models.IntegerField(default=-1)
    modify_status = models.SmallIntegerField(default=-1)
    modified_by = models.IntegerField(default=-1)
    is_delete = models.BooleanField(default=False)
    portal_flag = models.BooleanField(default=False)



class VendorRelContact(VsolvModels):
    type_id = models.IntegerField(default=-1)
    name = models.CharField(max_length=128, null=True)
    designation = models.CharField(max_length=128, null=True)
    landline = models.CharField(max_length=16, null=True, blank=True)
    landline2 = models.CharField(max_length=16, null=True, blank=True)
    mobile = models.CharField(max_length=16, null=True, blank=True)
    mobile2 = models.CharField(max_length=16, null=True, blank=True)
    email = models.CharField(max_length=128)
    dob = models.DateField(null=True, blank=True)
    wedding_date = models.DateField(null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    modify_ref_id = models.IntegerField(default=-1)
    modify_status = models.SmallIntegerField(default=-1)
    modified_by = models.IntegerField(default=-1)
    is_delete = models.BooleanField(default=False)
    portal_flag = models.BooleanField(default=False)



class VendorClient(VsolvModels):
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=128)
    address = models.ForeignKey(VendorRelAddress, on_delete=models.SET_NULL, null=True)
    is_validate = models.BooleanField(default=False)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    modify_ref_id = models.IntegerField(default=-1)
    modify_status = models.SmallIntegerField(default=-1)
    modified_by = models.IntegerField(default=-1)
    is_delete = models.BooleanField(default=False)
    portal_flag = models.BooleanField(default=False)



class VendorSubContractor(VsolvModels):
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=128)
    service = models.CharField(max_length=128)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    is_validate = models.BooleanField(default=False)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    modify_ref_id = models.IntegerField(default=-1)
    modify_status = models.SmallIntegerField(default=-1)
    modified_by = models.IntegerField(default=-1)
    is_delete = models.BooleanField(default=False)
    portal_flag = models.BooleanField(default=False)



class SupplierBranch(VsolvModels):
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=128)
    code = models.CharField(max_length=128, null=True, blank=True)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    limitdays = models.IntegerField(null=True)
    creditterms = models.CharField(max_length=256)
    gstno = models.CharField(max_length=16, null=True, blank=True)
    panno = models.CharField(max_length=16)
    address = models.ForeignKey(VendorRelAddress, on_delete=models.SET_NULL, null=True)
    contact = models.ForeignKey(VendorRelContact, on_delete=models.SET_NULL, null=True)
    is_validate = models.BooleanField(default=False)
    status = models.SmallIntegerField(default=1)
    is_active = models.BooleanField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    modify_ref_id = models.IntegerField(default=-1)
    modify_status = models.SmallIntegerField(default=-1)
    modified_by = models.IntegerField(default=-1)
    is_delete = models.BooleanField(default=False)
    portal_flag = models.BooleanField(default=False)



class SupplierTax(VsolvModels):
    branch = models.ForeignKey(SupplierBranch, on_delete=models.CASCADE, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True)
    vendor_code = models.CharField(max_length=128, null=True)
    tax_id = models.IntegerField(default=-1)
    subtax_id = models.IntegerField(default=-1)
    msme = models.BooleanField()
    msme_reg_no = models.CharField(max_length=128, null=True)
    type = models.CharField(max_length=128, null=True, blank=True)
    panno = models.CharField(max_length=16)
    status = models.IntegerField(null=False, default=1)
    created_by = models.IntegerField(null=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    modify_ref_id = models.IntegerField(default=-1)
    modify_status = models.SmallIntegerField(default=-1)
    modified_by = models.IntegerField(default=-1)
    is_delete = models.BooleanField(default=False)
    portal_flag = models.BooleanField(default=False)



class SupplierSubTax(VsolvModels):
    suppliertax = models.ForeignKey(SupplierTax, on_delete=models.CASCADE, null=True)
    isexcempted = models.CharField(max_length=1)
    excemfrom = models.DateField(null=True, blank=True)
    excemto = models.DateField(null=True, blank=True)
    excemthrosold = models.FloatField(default=0.00)
    rate_id = models.IntegerField(default=-1)
    excemrate = models.FloatField(default=0.00)
    attachment = models.IntegerField(null=True, blank=True)
    status = models.IntegerField(null=False, default=1)
    created_by = models.IntegerField(null=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    modify_ref_id = models.IntegerField(default=-1)
    modify_status = models.SmallIntegerField(default=-1)
    modified_by = models.IntegerField(default=-1)
    is_delete = models.BooleanField(default=False)
    portal_flag = models.BooleanField(default=False)



class SupplierPayment(VsolvModels):
    supplierbranch = models.ForeignKey(SupplierBranch, on_delete=models.SET_NULL, null=True)
    supplier = models.CharField(max_length=128, null=True, blank=True)
    paymode_id = models.IntegerField(default=-1)
    bank_id = models.IntegerField(default=-1, null=True, blank=True)
    branch_id = models.IntegerField(default=-1, null=True, blank=True)
    account_type = models.CharField(max_length=128, null=True, blank=True)
    account_no = models.CharField(max_length=32, null=True, blank=True)
    beneficiary = models.CharField(max_length=128, null=True)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    is_active = models.BooleanField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    modify_ref_id = models.IntegerField(default=-1)
    modify_status = models.SmallIntegerField(default=-1)
    modified_by = models.IntegerField(default=-1)
    is_delete = models.BooleanField(default=False)
    portal_flag = models.BooleanField(default=False)



class SupplierProduct(VsolvModels):
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    age = models.IntegerField(null=True)
    client1 = models.ForeignKey(VendorRelContact, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name="client1")
    client2 = models.ForeignKey(VendorRelContact, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name="client2")
    customer1 = models.ForeignKey(VendorRelContact, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name="customer1")
    customer2 = models.ForeignKey(VendorRelContact, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name="custmer2")
    is_validate = models.BooleanField(default=False)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    modify_ref_id = models.IntegerField(default=-1)
    modify_status = models.SmallIntegerField(default=-1)
    modified_by = models.IntegerField(default=-1)
    is_delete = models.BooleanField(default=False)
    portal_flag = models.BooleanField(default=False)


# class SupplierDocument(VsolvModels):
#     branch_id = models.ForeignKey(SupplierBranch, on_delete=models.SET_NULL, null=True)
#     group = models.CharField(max_length=128)
#     name = models.CharField(max_length=128)
#     description = models.CharField(max_length=128)
#
#     class Meta:
#         db_table="SupplierDocument"
#


class SupplierActivity(VsolvModels):
    type = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=128, null=True, blank=True)
    branch = models.ForeignKey(SupplierBranch, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    contract_spend = models.IntegerField(null=True)
    rm = models.CharField(max_length=128)
    rel_type = models.IntegerField(null=True)
    activity_id= models.IntegerField(null=True)
    fidelity = models.CharField(max_length=128)
    bidding = models.CharField(max_length=128)
    activity_status = models.CharField(max_length=128)
    contact = models.ForeignKey(VendorRelContact, on_delete=models.SET_NULL, null=True)
    is_validate = models.BooleanField(default=False)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    modify_ref_id = models.IntegerField(default=-1)
    modify_status = models.SmallIntegerField(default=-1)
    modified_by = models.IntegerField(default=-1)
    is_delete = models.BooleanField(default=False)
    portal_flag = models.BooleanField(default=False)



class ActivityDetail(VsolvModels):
    activity = models.ForeignKey(SupplierActivity, on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=128)
    detailname = models.CharField(max_length=128, null=True)
    raisor = models.CharField(max_length=128)
    approver = models.CharField(max_length=128)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    is_validate = models.BooleanField(default=False)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    modify_ref_id = models.IntegerField(default=-1)
    modify_status = models.SmallIntegerField(default=-1)
    modified_by = models.IntegerField(default=-1)
    is_delete = models.BooleanField(default=False)
    portal_flag = models.BooleanField(default=False)



class Catelog(VsolvModels):
    activitydetail = models.ForeignKey(ActivityDetail, on_delete=models.SET_NULL, null=True)
    detailname = models.CharField(max_length=128,null=True)
    productname = models.CharField(max_length=128)
    category = models.CharField(max_length=128)
    subcategory = models.CharField(max_length=128)
    name = models.CharField(max_length=128,null=True)
    specification = models.CharField(max_length=128, null=True, blank=True)
    size = models.CharField(max_length=128, null=True, blank=True)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    uom = models.CharField(max_length=128, null=True)
    unitprice = models.IntegerField(null=True)
    fromdate = models.DateField(null=True)
    todate = models.DateField(null=True)
    packing_price = models.IntegerField(null=True)
    deliverydate = models.IntegerField(default=0,null=True)
    capacity = models.CharField(max_length=128, null=True, blank=True)
    direct_to = models.BooleanField()
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    modify_ref_id = models.IntegerField(default=-1)
    modify_status = models.SmallIntegerField(default=-1)
    modified_by = models.IntegerField(default=-1)
    is_delete = models.BooleanField(default=False)
    portal_flag = models.BooleanField(default=False)



class VendorAccessor(VsolvModels):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    user_id = models.IntegerField(null=False)
    created_date = models.DateTimeField(default=now)
    updated_date = models.DateTimeField(null=True)
    status = models.SmallIntegerField(default=-1)
    is_sys = models.BooleanField(default=False)
    portal_flag = models.BooleanField(default=False)


class Vendoraudit(VsolvModels):
    ref_id = models.IntegerField()
    ref_type = models.CharField(max_length=28, null=True, blank=True)
    data = models.TextField(null=True, blank=True)
    user_id = models.IntegerField()
    date = models.DateTimeField(null=True, blank=True)
    req_status = models.SmallIntegerField()
    rel_refid = models.BigIntegerField()
    rel_reftype = models.CharField(max_length=28, null=True, blank=True)
    action = models.CharField(max_length=28, null=True, blank=True)
    portal_flag = models.BooleanField(default=False)



class VendorModificationRel(VsolvModels):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    ref_id = models.IntegerField(default=-1)
    ref_type = models.IntegerField(default=-1)
    mod_status = models.SmallIntegerField(default=-1)
    modify_ref_id = models.IntegerField(default=-1)
    is_flag = models.BooleanField(default=True)
    created_date = models.DateTimeField(default=now)
    portal_flag = models.BooleanField(default=False)



class VendorDocument(VsolvModels):
    partner_id = models.IntegerField()
    docgroup_id = models.IntegerField()
    period = models.CharField(max_length=64, null=True, blank=True)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    file_id = models.IntegerField(null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    is_validate = models.BooleanField(default=False)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    modify_ref_id = models.IntegerField(default=-1)
    modify_status = models.SmallIntegerField(default=-1)
    modified_by = models.IntegerField(default=-1)
    is_delete = models.BooleanField(default=False)
    portal_flag = models.BooleanField(default=False)



class VendorFileAttachment(VsolvModels):
    representtabel_id = models.IntegerField(null=True, blank=True)
    tab_type = models.IntegerField(null=True, blank=True)
    file_name = models.CharField(max_length=256)
    gen_file_name = models.CharField(max_length=512)
    status = models.SmallIntegerField(default=1)
    file_id = models.CharField(max_length=256, default=-1)
    portal_flag = models.BooleanField(default=False)



class VendorImage(VsolvModels):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    file_id = models.CharField(max_length=256, default=-1)
    file_name = models.CharField(max_length=256)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    portal_flag = models.BooleanField(default=False)



# class VendorLandlordMaping(VsolvModels):
#     branch = models.IntegerField(null=True)
#     landlorddetails = models.ForeignKey(LandLordDetails, on_delete=models.CASCADE)
#     status = models.SmallIntegerField(default=1)
#     created_by = models.IntegerField()
#     created_date = models.DateTimeField(default=now)

# class Vendorsupplierproduct(VsolvModels):
#     vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)
#     supplier = models.ForeignKey(SupplierBranch, on_delete=models.SET_NULL, null=True)
#     product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
#     unitprice = models.FloatField()
#     fromdate=models.DateField()
#     todate=models.DateField()
#     dts=models.BooleanField()
#     created_by = models.IntegerField()
#     created_date = models.DateTimeField(default=now)
#     updated_by = models.IntegerField(null=True, blank=True)
#     updated_date = models.DateTimeField(null=True, blank=True)

class Codegenerator(VsolvModels):
    trans_type = models.IntegerField()
    serial_no = models.IntegerField(null=True)
    status = models.IntegerField(default=1)
    Updated_by = models.IntegerField()
    Updated_date = models.DateTimeField(null=True, blank=True)
    portal_flag = models.BooleanField(default=False)


class VendorRiskInfo(VsolvModels):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    risktype_id = models.SmallIntegerField(null=True)
    risktype_description = models.CharField(max_length=1040, null=True)
    risk_mitigant = models.CharField(max_length=1040, null=True)
    risk_mitigant_review = models.CharField(max_length=1040, null=True)
    status = models.IntegerField(null=False, default=1)
    created_by = models.IntegerField(null=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    modify_ref_id = models.IntegerField(default=-1)
    modify_status = models.SmallIntegerField(default=-1)
    modified_by = models.IntegerField(default=-1)
    is_delete = models.BooleanField(default=False)
    portal_flag = models.BooleanField(default=False)


class VendorKYC(VsolvModels):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    kyc_entity = models.CharField(max_length=28, null=True)
    organization_name = models.CharField(max_length=28, null=True)
    sanctions_conducted = models.BooleanField(default=False)
    match_found = models.BooleanField(default=False)
    report_file_id = models.IntegerField(null=True, blank=True)
    authorised_signatories = models.CharField(max_length=28, null=True)
    beneficial_owners = models.CharField(max_length=28, null=True)
    status = models.IntegerField(null=False, default=1)
    created_by = models.IntegerField(null=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    modify_ref_id = models.IntegerField(default=-1)
    modify_status = models.SmallIntegerField(default=-1)
    modified_by = models.IntegerField(default=-1)
    is_delete = models.BooleanField(default=False)
    portal_flag = models.BooleanField(default=False)


class VendorGrpAnswers(VsolvModels):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    ans_bool = models.CharField(max_length=8, null=True)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    direction = models.CharField(max_length=128, null=True, blank=True)
    ques_type = models.CharField(max_length=32, null=True)
    ques_id = models.IntegerField()
    status = models.IntegerField(null=False, default=1)
    created_by = models.IntegerField(null=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    modify_ref_id = models.IntegerField(default=-1)
    modify_status = models.SmallIntegerField(default=-1)
    modified_by = models.IntegerField(default=-1)
    is_delete = models.BooleanField(default=False)
    portal_flag = models.BooleanField(default=False)


class VendorMail(VsolvModels):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    vendor_code = models.CharField(max_length=128, null=True)
    maker_id = models.IntegerField(null=True)
    rm_id = models.IntegerField(null=True)
    mail_type = models.IntegerField(null=True)
    is_rm = models.BooleanField(default=False)
    is_header = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    compliance_type = models.BooleanField(default=False)
    rejected_by = models.IntegerField(default=-1)
    returned_by = models.IntegerField(default=-1)
    status = models.IntegerField(null=False, default=1)
    portal_flag = models.BooleanField(default=False)


class Question_Answers(VsolvModels):
    question_id = models.IntegerField(null=True)
    type_id = models.IntegerField(null=True)
    file = models.BooleanField(default=False)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE,null=True)
    activity_id = models.IntegerField(null=False)
    header_id = models.IntegerField(null=True)
    answer = models.TextField(null=True)
    status = models.SmallIntegerField(default=1)
    approving_level = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Suboption_Answers(VsolvModels):
    question_ans=models.ForeignKey(Question_Answers,on_delete=models.CASCADE,null=True)
    option_id = models.IntegerField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)



class Questions_approvalqueue(VsolvModels):
    question_type=models.IntegerField(null=True)
    approving_level = models.SmallIntegerField(default=1)
    approving_count = models.IntegerField(null=True)
    is_group=models.BooleanField(default=False)
    dept_id=models.IntegerField(null=True)
    remarks=models.CharField(max_length=128,null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)

class Questions_files(VsolvModels):
    question_ans = models.ForeignKey(Question_Answers, on_delete=models.CASCADE,null=True)
    file_name=models.CharField(max_length=128,null=True)
    file_id = models.CharField(max_length=100,default=-1)
    remarks=models.CharField(max_length=128,null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class Questions_Queue(VsolvModels):
    question_ans = models.ForeignKey(Question_Answers, on_delete=models.CASCADE,null=True)
    ref_id = models.IntegerField(null=True)#1.vendor 2.Activity
    ref_type= models.IntegerField(null=True)
    from_user_id = models.IntegerField(null=False)
    to_user_id = models.IntegerField(null=False)
    created_date = models.DateTimeField(default=now)
    comments = models.CharField(null=False, max_length=2048)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    is_sys = models.BooleanField(default=False)

class Question_vendor_mapping(VsolvModels):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE,null=True)
    Activity = models.IntegerField(null=True)
    question_type=models.IntegerField(null=True)
    period=models.IntegerField(null=True)
    # periodicity=models.IntegerField(null=True)
    period_start = models.DateTimeField(null=True)
    period_end = models.DateTimeField(null=True)
    remarks=models.CharField(max_length=128,null=True)
    type_status=models.IntegerField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)




