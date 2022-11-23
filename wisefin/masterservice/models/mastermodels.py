from django.db import models
from django.utils.timezone import now
from db.vsolvmodels import VsolvModels


class Designation(VsolvModels):
    code = models.CharField(max_length=8, null=True, blank=True)
    name = models.CharField(max_length=64)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Country(VsolvModels):
    code = models.CharField(max_length=8, null=True, blank=True)
    name = models.CharField(max_length=64)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class State(VsolvModels):
    code = models.CharField(max_length=8, null=True, blank=True)
    name = models.CharField(max_length=64)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class District(VsolvModels):
    code = models.CharField(max_length=8, null=True, blank=True)
    name = models.CharField(max_length=64)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class City(VsolvModels):
    code = models.CharField(max_length=8, null=True, blank=True)
    name = models.CharField(max_length=64)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Pincode(VsolvModels):
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    no = models.CharField(max_length=8)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Address(VsolvModels):
    line1 = models.CharField(max_length=128)
    line2 = models.CharField(max_length=128, null=True, blank=True)
    line3 = models.CharField(max_length=128, null=True, blank=True)
    pincode = models.ForeignKey(Pincode, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Bank(VsolvModels):
    code = models.CharField(max_length=8, null=True, blank=True)
    name = models.CharField(max_length=64, unique=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class PayMode(VsolvModels):
    code = models.CharField(max_length=8, null=True, blank=True)
    name = models.CharField(max_length=64, unique=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    gl_flag = models.CharField(max_length=1, null=True)  # P-payable,A-adjustable,R-recivable


class BankBranch(VsolvModels):
    bank = models.ForeignKey(Bank, on_delete=models.SET_NULL, null=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=8, null=True, blank=True)
    ifsccode = models.CharField(max_length=11, unique=True)
    microcode = models.CharField(max_length=12, null=False, blank=False)
    name = models.CharField(max_length=128, null=False, blank=False)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Uom(VsolvModels):
    code = models.CharField(max_length=8, null=True, blank=True)
    name = models.CharField(max_length=128, unique=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class APexpense(VsolvModels):
    code = models.CharField(max_length=16, null=True, unique=True)
    head = models.CharField(max_length=128)
    linedesc = models.CharField(max_length=128)
    group = models.CharField(max_length=128)
    sch16 = models.CharField(max_length=128)
    sch16desc = models.CharField(max_length=128)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    exp_grp_id = models.IntegerField(null=True, blank=True)


class Apcategory(VsolvModels):
    code = models.CharField(max_length=128, null=True, blank=True)
    no = models.IntegerField()
    name = models.CharField(max_length=128, unique=True)
    glno = models.IntegerField()
    isasset = models.CharField(max_length=1)
    isodit = models.SmallIntegerField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    expense = models.ForeignKey(APexpense, on_delete=models.SET_NULL, null=True)


class APexpensegroup(VsolvModels):
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=64)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    expensegrp_alei = models.CharField(max_length=1, null=True, blank=True)


class APsubcategory(VsolvModels):
    code = models.CharField(max_length=64, null=True, blank=True)
    no = models.CharField(max_length=16)
    name = models.CharField(max_length=64)
    category = models.ForeignKey(Apcategory, on_delete=models.SET_NULL, null=True)
    glno = models.BigIntegerField(null=True, blank=True)
    gstblocked = models.CharField(max_length=1)
    gstrcm = models.CharField(max_length=1)
    assetcode = models.CharField(max_length=16, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    subcat_expensegrp_alei = models.CharField(max_length=1, null=True, blank=True)


class Apsector(VsolvModels):
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=64)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class CustomerCategory(VsolvModels):
    code = models.CharField(max_length=8, null=True, blank=True)
    name = models.CharField(max_length=64, unique=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Tax(VsolvModels):
    code = models.CharField(max_length=8, null=True, blank=True)
    name = models.CharField(max_length=64, unique=True)
    receivable = models.BooleanField()
    payable = models.BooleanField()
    glno = models.CharField(max_length=16)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class SubTax(VsolvModels):
    tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=8, null=True, blank=True)
    name = models.CharField(max_length=64)
    remarks = models.CharField(max_length=128)
    glno = models.CharField(max_length=16)
    subtaxamount = models.DecimalField(default=0.0, decimal_places=2, max_digits=20)
    category = models.ForeignKey(Apcategory, on_delete=models.CASCADE, null=True)
    subcategory = models.ForeignKey(APsubcategory, on_delete=models.CASCADE, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class TaxRate(VsolvModels):
    subtax = models.ForeignKey(SubTax, on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=8, null=True, blank=True)
    name = models.CharField(max_length=64)
    rate = models.FloatField()
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    is_delete = models.BooleanField(default=False)


class ContactType(VsolvModels):
    code = models.CharField(max_length=8, unique=True, null=True, blank=True)
    name = models.CharField(max_length=64, unique=True)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class DocumentType(VsolvModels):
    code = models.CharField(max_length=8, null=True, blank=True)
    name = models.CharField(max_length=64)
    module_id = models.SmallIntegerField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Contact(VsolvModels):
    type_id = models.IntegerField(default=-1)
    name = models.CharField(max_length=128)
    designation_id = models.IntegerField(default=-1)
    landline = models.CharField(max_length=16, null=True, blank=True)
    landline2 = models.CharField(max_length=16, null=True, blank=True)
    mobile = models.CharField(max_length=16)
    mobile2 = models.CharField(max_length=16, null=True, blank=True)
    email = models.CharField(max_length=128)
    # dob = models.DateField(null=True, blank=True)
    # wedding_date = models.DateField(null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Courier(VsolvModels):
    code = models.CharField(max_length=8, null=True, blank=True)
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=64, null=True)
    contactperson = models.CharField(max_length=128, null=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True)
    all_branch = models.BooleanField(default=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Channel(VsolvModels):
    code = models.CharField(max_length=8, null=True, blank=True)
    name = models.CharField(max_length=64)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class MigrationVersion(VsolvModels):
    module = models.IntegerField(default=0)


class Masteraudit(VsolvModels):
    ref_id = models.IntegerField(default=-1)
    ref_type = models.CharField(max_length=28, null=True, blank=True)
    data = models.TextField(null=True, blank=True)
    user_id = models.IntegerField()
    date = models.DateTimeField(null=True, blank=True)
    req_status = models.SmallIntegerField()
    rel_refid = models.SmallIntegerField()
    rel_reftype = models.CharField(max_length=28, null=True, blank=True)
    action = models.CharField(max_length=28, null=True, blank=True)


class ProductCategory(VsolvModels):
    code = models.CharField(max_length=8, null=True, blank=True)
    name = models.CharField(max_length=64)
    product_client_id = models.IntegerField(default=1)
    isprodservice = models.IntegerField()
    stockimpact = models.BooleanField()
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    client_id = models.IntegerField(null=True)


class ProductType(VsolvModels):
    code = models.CharField(max_length=8, null=True, blank=True)
    name = models.CharField(max_length=64)
    productcategory = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Hsn(VsolvModels):
    code = models.CharField(max_length=8, null=True, blank=True)
    description = models.CharField(max_length=128)
    cgstrate = models.FloatField()
    sgstrate = models.FloatField()
    igstrate = models.FloatField()
    cgstrate_id = models.IntegerField(default=-1)
    sgstrate_id = models.IntegerField(default=-1)
    igstrate_id = models.IntegerField(default=-1)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class PmdBranch(VsolvModels):
    branch_name = models.CharField(max_length=128, null=True, blank=True)
    branch_code = models.CharField(max_length=128, null=True, blank=True)
    location = models.CharField(max_length=128, null=True, blank=True)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    gst_number = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Product(VsolvModels):
    hsn = models.ForeignKey(Hsn, on_delete=models.SET_NULL, null=True)
    uom = models.ForeignKey(Uom, on_delete=models.CASCADE, null=True)
    category = models.ForeignKey(Apcategory, on_delete=models.CASCADE, null=True)
    subcategory = models.ForeignKey(APsubcategory, on_delete=models.CASCADE, null=True)
    productcategory = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True)
    producttype = models.ForeignKey(ProductType, on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=128, null=True, blank=True)
    name = models.CharField(max_length=128, null=False, blank=False)
    productdisplayname = models.CharField(max_length=128, null=False, blank=False, default=0)
    producttradingitem = models.SmallIntegerField(default=1)
    weight = models.DecimalField(max_digits=16, decimal_places=2)
    unitprice = models.DecimalField(max_digits=16, decimal_places=2)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(default=0, null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    product_details = models.TextField(null=True, blank=True)
    product_isblocked = models.CharField(max_length=1, default='N')
    product_isrcm = models.CharField(max_length=1, default='N')


class DocumentGroup(VsolvModels):
    partnertype = models.CharField(max_length=2)
    isparent = models.CharField(max_length=1)
    parent_id = models.IntegerField()
    name = models.CharField(max_length=64, unique=True)
    docname = models.CharField(max_length=128, null=False, blank=False)
    period = models.CharField(max_length=64)
    mand = models.CharField(max_length=1)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(default=0, null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class CodeGenHeader(VsolvModels):
    code = models.CharField(max_length=8, null=True, blank=True)
    name = models.CharField(max_length=64, null=False, blank=False)
    type = models.CharField(max_length=64, null=False,
                            blank=False)  # COMMENT 'RunSLNO/DDMMYY/YYYYMMDD/DDMMYYRNSL/YYYYMMDDRNSL/TABLECOLRNSL'
    format = models.CharField(max_length=32, null=False, blank=False)
    modulename = models.CharField(max_length=128, null=False, blank=False)
    currentvalue = models.CharField(max_length=32, null=False, blank=False)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class CodeGenDetails(VsolvModels):
    codegenheader = models.ForeignKey(CodeGenHeader, on_delete=models.CASCADE, default=0)
    tablename = models.CharField(max_length=128, null=False, blank=False)
    columnname = models.CharField(max_length=128, null=False, blank=False)
    columnlen = models.IntegerField(null=False, blank=False, default=0)
    columnprefix = models.CharField(max_length=8, null=True, blank=True)
    columnsufix = models.CharField(max_length=8, null=True, blank=True)
    year = models.CharField(max_length=8, null=True, blank=True)
    month = models.CharField(max_length=8, null=True, blank=True)
    day = models.CharField(max_length=8, null=True, blank=True)
    rnsl = models.CharField(max_length=8, null=True, blank=True)
    displayorder = models.IntegerField(null=False, blank=False, default=0)
    wherecondcolumn = models.CharField(max_length=128, null=True, blank=True)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Commodity(VsolvModels):
    code = models.CharField(max_length=8)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class CommodityProductMaping(models.Model):
    commodity_id = models.IntegerField(null=True)
    product_id = models.IntegerField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class PaymodeDetails(VsolvModels):
    glno = models.CharField(max_length=16, null=True)
    name = models.CharField(max_length=64)
    category = models.ForeignKey(Apcategory, on_delete=models.SET_NULL, null=True)
    sub_category = models.ForeignKey(APsubcategory, on_delete=models.SET_NULL, null=True)
    paymode = models.ForeignKey(PayMode, on_delete=models.SET_NULL, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


# master for SG

class Employeementcatgorymaster(VsolvModels):
    empcat = models.CharField(max_length=120)
    empcatdesc = models.CharField(max_length=250)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)


class EmployeementTypemaster(VsolvModels):
    empcat = models.ForeignKey(Employeementcatgorymaster, on_delete=models.CASCADE, null=True)
    emptype = models.CharField(max_length=120)
    emptypedesc = models.CharField(max_length=250)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)


class NewStateZone(VsolvModels):
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True)
    noofzones = models.IntegerField()
    effectivefrom = models.DateField(null=True)
    effectiveto = models.DateField(null=True)
    name = models.CharField(max_length=120, null=True)
    code = models.CharField(max_length=20, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)


class NewStateZoneMapping(VsolvModels):
    state = models.ForeignKey(NewStateZone, on_delete=models.CASCADE, null=True)
    zone = models.CharField(max_length=120)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)


class Holidaymst(VsolvModels):
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True)
    year = models.SmallIntegerField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class ProductSpecification(VsolvModels):
    productcategory = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True)
    templatename = models.CharField(max_length=128)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Customer(VsolvModels):
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    customer_entitygid = models.IntegerField(default=0)
    customer_code = models.CharField(max_length=32, null=True, blank=True)
    customer_name = models.CharField(max_length=128, null=True, blank=True)
    customer_billingname = models.CharField(max_length=128, null=False, blank=False)
    customer_type = models.CharField(max_length=32, null=True, blank=True)
    customer_subtype = models.CharField(max_length=32, null=True, blank=True)
    custgroup_id = models.IntegerField(default=0)
    category_id = models.IntegerField(default=0)
    location_gid = models.IntegerField(default=0)
    customer_constitution = models.IntegerField(default=0)
    customer_salemode = models.IntegerField(default=0)
    customer_size = models.IntegerField(default=0)
    customer_landmark = models.CharField(max_length=128, null=False, blank=False)
    insert_flag = models.SmallIntegerField(default=0)
    update_flag = models.SmallIntegerField(default=0)
    sodetails_status = models.SmallIntegerField(default=0)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class CustomerGroup(VsolvModels):
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    customergroup_entitygid = models.IntegerField(default=0)
    customergroup_code = models.CharField(max_length=32, null=True, blank=True)
    customergroup_name = models.CharField(max_length=128, null=True, blank=True)
    customergroup_cpdesignation = models.CharField(max_length=128, null=False, blank=False)
    customergroup_cpmobileno = models.CharField(max_length=128, null=False, blank=False)
    customergroup_cplandline = models.CharField(max_length=128, null=False, blank=False)
    customergroup_cpname2 = models.CharField(max_length=128, null=False, blank=False)
    customergroup_cpdesignation2 = models.CharField(max_length=128, null=False, blank=False)
    customergroup_cpmobileno2 = models.CharField(max_length=128, null=False, blank=False)
    customergroup_cplandline2 = models.CharField(max_length=128, null=False, blank=False)
    insert_flag = models.SmallIntegerField(default=0)
    update_flag = models.SmallIntegerField(default=0)
    sodetails_status = models.SmallIntegerField(default=0)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class BankDetails(VsolvModels):
    bankbranch = models.ForeignKey(BankBranch, on_delete=models.SET_NULL, null=True)
    account_no = models.CharField(max_length=16, null=False, blank=False)
    accountholder = models.CharField(max_length=128, null=False, blank=False)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class MasterBusinessSegment(VsolvModels):
    code = models.CharField(max_length=16)
    sector_id = models.IntegerField()
    no = models.IntegerField()
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=128, null=True, blank=True)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class BusinessSegment(VsolvModels):
    masterbussinesssegment = models.ForeignKey(MasterBusinessSegment, on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=128, unique=True)
    no = models.IntegerField()
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=128, null=True, blank=True)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class CostCentre(VsolvModels):
    businesssegment = models.ForeignKey(BusinessSegment, on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=128)
    no = models.IntegerField()
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=128, null=True, blank=True)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class CostCentreBusinessSegmentMaping(VsolvModels):
    no = models.IntegerField()
    name = models.CharField(max_length=64)
    costcentre = models.ForeignKey(CostCentre, on_delete=models.SET_NULL, null=True)
    businesssegment = models.ForeignKey(BusinessSegment, on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=16)
    glno = models.CharField(max_length=20)
    description = models.CharField(max_length=128, null=True, blank=True)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Codegenerator(VsolvModels):
    trans_type = models.IntegerField()
    serial_no = models.IntegerField(null=True)
    status = models.IntegerField(default=1)
    Updated_by = models.IntegerField()
    Updated_date = models.DateTimeField(null=True, blank=True)


class Delmat(VsolvModels):
    type = models.SmallIntegerField()
    limit = models.FloatField()
    delmat_status = models.CharField(max_length=64)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    commodity_id = models.IntegerField(null=True)
    employee_id = models.IntegerField(null=True)
    two_level_approval = models.SmallIntegerField(default=0)
    two_level_employee_id = models.IntegerField(null=True)


class Clientcode(VsolvModels):
    client_code = models.CharField(max_length=16)
    client_name = models.CharField(max_length=64)
    status = models.SmallIntegerField(default=1)
    rm_name = models.IntegerField(null=True, default=0)
    entity = models.CharField(max_length=126, null=True, blank=False)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Businessproductcode(VsolvModels):
    bsproduct_code = models.CharField(max_length=16)
    bsproduct_name = models.CharField(max_length=64)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Financial_Year(models.Model):
    fin_year = models.CharField(max_length=5, null=True, blank=True)
    fin_month = models.CharField(max_length=5, null=True, blank=True)
    fin_year_from_period = models.DateField(null=True, blank=True)
    fin_year_to_period = models.DateField(null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Financial_Quarters(models.Model):
    fin_year = models.CharField(max_length=5, null=True, blank=True)
    fin_month = models.CharField(max_length=5, null=True, blank=True)
    fin_quarter_from_period = models.DateField(null=True, blank=True)
    fin_quarter_to_period = models.DateField(null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class RisksType(VsolvModels):
    name = models.CharField(max_length=128)
    code = models.CharField(max_length=8, null=True, blank=True)
    status = models.IntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Asset_Type(VsolvModels):
    name = models.CharField(max_length=1064, null=True)
    code = models.CharField(max_length=128, null=True)
    description = models.CharField(max_length=1064, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)


class Business_type(VsolvModels):
    name = models.CharField(max_length=1064, null=True)
    code = models.CharField(max_length=128, null=True)
    description = models.CharField(max_length=264, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)


class Nac_Revenue(VsolvModels):
    category = models.ForeignKey(Apcategory, on_delete=models.SET_NULL, null=True)
    subcategory = models.ForeignKey(APsubcategory, on_delete=models.SET_NULL, null=True)
    gl_name = models.CharField(max_length=164, null=True)
    gl_number = models.CharField(max_length=164, null=True)
    ppr_incomehead = models.IntegerField(null=True)
    income_head = models.IntegerField(null=True, blank=True)
    income_group = models.IntegerField(null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)


class Business_Asset_maping(VsolvModels):
    bussiness_type = models.ForeignKey(Business_type, on_delete=models.SET_NULL, null=True)
    asset_type = models.ForeignKey(Asset_Type, on_delete=models.SET_NULL, null=True)
    entity_number = models.IntegerField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)


class Nac_Client(VsolvModels):
    client_name = models.CharField(max_length=1064, null=True)
    client_code = models.CharField(max_length=1064, null=True)
    cin_number = models.CharField(max_length=264, null=True)
    assettype = models.ForeignKey(Asset_Type, on_delete=models.SET_NULL, null=True)
    rm_name = models.IntegerField(null=True)
    email_rm = models.EmailField(max_length=264, null=True)
    is_active = models.BooleanField(null=True)
    is_entity = models.SmallIntegerField(null=True)
    name = models.CharField(max_length=1064)
    email_id = models.EmailField(max_length=264)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)


class AppVersion(VsolvModels):
    no = models.CharField(max_length=16, null=True)
    ref_no = models.CharField(max_length=3, null=True)
    remarks = models.CharField(max_length=32, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)


class vendoroutsourcequestionnaire(VsolvModels):
    questions = models.TextField(null=True, blank=True)
    ques_type = models.CharField(max_length=32, null=True)
    ques_id = models.IntegerField()
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)


class AuditChecklist(VsolvModels):
    type = models.IntegerField()
    group = models.CharField(max_length=64)
    code = models.CharField(max_length=32)
    question = models.CharField(max_length=512)
    solution = models.CharField(max_length=512)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    is_delete = models.BooleanField(default=False)


class Question_Type(VsolvModels):
    name = models.CharField(max_length=128)
    remarks = models.CharField(max_length=32, null=True)
    module_id = models.SmallIntegerField(null=True)
    display_name = models.CharField(max_length=128, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Question_Header(VsolvModels):
    name = models.CharField(max_length=128)
    type = models.ForeignKey(Question_Type, on_delete=models.SET_NULL, null=True)
    # slno=models.CharField(max_length=125, null=True)
    order = models.IntegerField(null=True)
    is_input = models.BooleanField(default=False)
    input_type = models.SmallIntegerField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Questions(VsolvModels):
    text = models.TextField(null=True, blank=True)
    header = models.ForeignKey(Question_Header, on_delete=models.SET_NULL, null=True)
    type_id = models.IntegerField(null=True)
    ref_id=models.IntegerField(null=True)
    input_type = models.SmallIntegerField(null=True)
    is_score=models.BooleanField(default=False)
    min = models.FloatField(default=0)
    max = models.FloatField(default=0)
    order = models.IntegerField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class Questions_Typemapping(VsolvModels):
    type = models.ForeignKey(Question_Type, on_delete=models.SET_NULL, null=True)
    question = models.ForeignKey(Questions, on_delete=models.SET_NULL, null=True)
    header = models.IntegerField(null=True)
    is_checked = models.BooleanField(default=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Questions_flagmaster(VsolvModels):
    questionmapping_id = models.IntegerField(null=True)
    ref_type = models.IntegerField(null=True)
    ref_id = models.IntegerField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Questions_suboptions(VsolvModels):
    options = models.TextField(null=True)
    question = models.ForeignKey(Questions, on_delete=models.SET_NULL, null=True)
    order = models.IntegerField(null=True)
    # input_type = models.SmallIntegerField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Vendorclassification_Mapping(VsolvModels):
    type = models.ForeignKey(Question_Type, on_delete=models.SET_NULL, null=True)
    rel_cat = models.IntegerField(null=True)
    criticality = models.IntegerField(null=True)
    vendor_type = models.IntegerField(null=True)
    is_activity = models.BooleanField(default=False)
    expiration_date = models.DateField(null=True)
    period = models.IntegerField(null=True)
    process = models.SmallIntegerField(null=True)
    dept_id = models.SmallIntegerField(null=True)
    is_doc = models.BooleanField(default=False)
    document_group = models.ForeignKey(DocumentGroup, on_delete=models.SET_NULL, null=True)
    order = models.IntegerField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class QuestionGroupMapping(VsolvModels):
    type = models.ForeignKey(Question_Type, on_delete=models.SET_NULL, null=True)
    group_id = models.IntegerField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Activity(VsolvModels):
    name = models.CharField(max_length=1064, null=True)
    code = models.CharField(max_length=128, null=True)
    description = models.CharField(max_length=1064, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)


class OrgDetails(VsolvModels):
    latitude = models.CharField(max_length=32, null=True)
    longitude = models.CharField(max_length=32, null=True)
    radius = models.CharField(max_length=32,null=True)
    code = models.CharField(max_length=128, null=True)
    name = models.CharField(max_length=256, null=True)
    status = models.SmallIntegerField(default=1)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)

class OrgArcDetails(VsolvModels):
    org_id = models.IntegerField()
    latitude = models.CharField(max_length=32, null=True)
    longitude = models.CharField(max_length=32, null=True)
    radius = models.CharField(max_length=32,null=True)
    name = models.CharField(max_length=256, null=True)
    arc_type =models.SmallIntegerField(default=1)
    status = models.SmallIntegerField(default=1)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)

class OrgIP(VsolvModels):
    org_detail = models.ForeignKey(OrgDetails, on_delete=models.SET_NULL, null=True)
    ip = models.CharField(max_length=64, null=True)
    status = models.SmallIntegerField(default=1)


class AttendanceConfig(VsolvModels):
    check_in_mode = models.CharField(max_length=128, null=True)
    namespace = models.CharField(max_length=128, null=True)
    status = models.SmallIntegerField(default=1)
    code = models.CharField(max_length=128, null=True)

# leave type
class LeaveType(VsolvModels):
    name = models.CharField(max_length=128, null=True)
    has_attendance = models.BooleanField(default=False)
    has_salary = models.BooleanField(default=False)
    status = models.SmallIntegerField(default=1)
    code = models.CharField(max_length=128, null=True)
    is_leave = models.BooleanField(default=True)

# holiday master
class Holiday(VsolvModels):
    holiday_mst = models.ForeignKey(Holidaymst, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=128, null=True)
    holiday_date = models.DateField(null=True)
    type = models.IntegerField(null=True)  # need to remove
    code = models.CharField(max_length=128, null=True) # need to remove
    status = models.SmallIntegerField(default=1)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)

# grade master
class Grade(VsolvModels):
    name = models.CharField(max_length=128, null=True)
    is_active = models.BooleanField(default=True)
    code = models.CharField(max_length=20, null=True)
    points = models.IntegerField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)

# ******
class DesignationGradeMapping(VsolvModels):
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True)
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)

#  leave - grade mapping
class LeaveGradeMapping(VsolvModels):
    leave =models.ForeignKey(LeaveType, on_delete=models.SET_NULL, null=True)
    grade =models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True)
    leave_count = models.IntegerField(null=True)
    effective_to =  models.DateField(null=True)
    effective_from =  models.DateField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)
