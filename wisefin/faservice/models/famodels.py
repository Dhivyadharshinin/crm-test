import inspect

from django.db import models
from django.utils.timezone import now
from db.vsolvmodels import VsolvModels as VModels, VSolvQueryset
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
##INHERITING VSOLVMODELS AND REUSE FOR IMPLETMENTING ENTITY SAVE
class VsolvModels(VModels):
    def get_var_from_stack(self,name):
        for f in inspect.stack():
            if name in f[0].f_locals: return f[0].f_locals[name]
        return None

    def get_entity_id(self):
        class DbGet(NWisefinThread):
            app_name_space=self.get_name_appnamespace()
            def __init__(self, scope):
                super().__init__(scope)
                self._set_namespace(self.app_name_space)
            def get_entity(self):
                return self._entity_id()
        request = self.get_var_from_stack('request')
        entity_get = DbGet(request.scope)
        return entity_get.get_entity()

    def get_name_appnamespace(self):
        app_label=self._meta.app_label
        appspace_keys=ApplicationNamespace.__dict__.keys()
        appspace_vals=ApplicationNamespace.__dict__.values()
        if app_label in appspace_vals:
            ind=list(appspace_vals).index(app_label)
            return list(appspace_keys)[ind]
    class Meta:
        abstract = True
    def save(self, verbosity=1, *args, **kwargs):
        self.entity_id=self.get_entity_id()
        super(VsolvModels, self).save(*args, **kwargs)
##Inheriting VsolvQueryset to retain the functionality
class FAQuerySet(VSolvQueryset):
    ##---Function to retrieve request object to FaQuerySet---##
    def get_var_from_stack(self,name):
        for f in inspect.stack():
            if name in f[0].f_locals: return f[0].f_locals[name]
        return None

    def get_entity_id(self):
        class DbGet(NWisefinThread):
            app_name_space=self.get_name_appnamespace()
            def __init__(self, scope):
                super().__init__(scope)
                self._set_namespace(self.app_name_space)
            def get_entity(self):
                return self._entity_id()
        request = self.get_var_from_stack('request')
        entity_get = DbGet(request.scope)
        return entity_get.get_entity()

    def get_name_appnamespace(self):
        app_label=self.model._meta.app_label
        appspace_keys=ApplicationNamespace.__dict__.keys()
        appspace_vals=ApplicationNamespace.__dict__.values()
        if app_label in appspace_vals:
            ind=list(appspace_vals).index(app_label)
            return list(appspace_keys)[ind]

    ##----Overriding all Get query in FA models to retreive data based on Entity----##
    def get(self,*args,**kwargs):
        entity_id=self.get_entity_id()
        return super().get(*args,**dict(kwargs,entity_id=entity_id))
    ##----Overriding all Filter query in FA models to retreive data based on Entity----##

    def filter(self,*args,**kwargs):
        entity_id=self.get_entity_id()
        return super().filter(*args,**dict(kwargs,entity_id=entity_id))

    def latest(self,*args,**kwargs):
        latest_fields=[]
        for fields in args:
           latest_fields.append('-'+fields)
        return self.filter().order_by(*latest_fields)[0]

    def earliest(self,*args,**kwargs):
        earliest_fields=[]
        for fields in args:
           earliest_fields.append(fields)
        return self.filter().order_by(*earliest_fields)[0]

    def first(self,*args,**kwargs):
        self.filter()
        return super().first()

    def last(self,*args,**kwargs):
        self.filter()
        return super().last()
    def create(self,*args,**kwargs):
        entity_id=self.get_entity_id()
        return super().create(*args,**dict(kwargs,entity_id=entity_id))

    def bulk_create(self,*args,**kwargs):
        entity_id = self.get_entity_id()
        for objs in args:
            if isinstance(objs,list):
                for record in objs:
                    record.__dict__['entity_id']=entity_id
        return super().bulk_create(*args,**kwargs)
    def bulk_update(self,*args,**kwargs):
        entity_id = self.get_entity_id()
        for objs in args:
            if isinstance(objs,list):
                for record in objs:
                    record.__dict__['entity_id']=entity_id
        return super().bulk_update(*args,**kwargs)
    def get_or_create(self,*args,**kwargs):
        entity_id = self.get_entity_id()
        return super().get_or_create(*args,**dict(kwargs,entity_id=entity_id))
    def update_or_create(self,*args,**kwargs):
        entity_id = self.get_entity_id()
        return super().update_or_create(*args,**dict(kwargs,entity_id=entity_id))
##MODELS STARTS HERE##
class AssetCat(VsolvModels):
    subcategory_id = models.IntegerField(null=True, blank=True)
    subcatname = models.CharField(max_length=64, null=True, blank=True)
    lifetime = models.IntegerField(null=True, blank=True)
    deptype = models.CharField(max_length=3, null=True, blank=True)
    itcatname=models.CharField(max_length=64, null=True, blank=True)
    deprate_itc = models.DecimalField(max_digits=16, decimal_places=2)
    deprate_ca = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    deprate_mgmt = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    depgl_itc = models.CharField(max_length=16, null=True, blank=True)
    depgl_ca = models.CharField(max_length=16, null=True, blank=True)
    depgl_mgmt = models.CharField(max_length=16, null=True, blank=True)
    depresgl_itc = models.CharField(max_length=16, null=True, blank=True)
    depresgl_ca = models.CharField(max_length=16, null=True, blank=True)
    depresgl_mgmt = models.CharField(max_length=16, null=True, blank=True)
    apcatnodep_mgmt = models.CharField(max_length=8, null=False, blank=False, default=0)
    apscatnodep_mgmt = models.CharField(max_length=8, null=False, blank=False, default=0)
    apcatnodepres_mgmt = models.CharField(max_length=8, null=False, blank=False, default=0)
    apscatnodepres_mgmt = models.CharField(max_length=8, null=False, blank=False, default=0)
    deprate = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    barcoderequired = models.BooleanField(default=1)  # YES/NO
    remarks = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()
class AssetHeader(VsolvModels):
    barcode = models.CharField(max_length=32, default=0,db_index=True)
    date = models.DateTimeField(null=False, blank=False)
    assetheadermonth = models.IntegerField(null=False, blank=False, default=0)
    assetheaderyear = models.IntegerField(null=False, blank=False, default=0)
    astvalbeforedeptot = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    computeddeptot = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    reviseddeptot = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    revisedcbtot = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    deprestot = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    costtot = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    valuetot = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    warrenty_startdate = models.DateTimeField(null=True, blank=True)
    warrenty_enddate = models.DateTimeField(null=True, blank=True)
    serial_no = models.CharField(max_length=70, null=True, default="")
    remarks = models.CharField(max_length=70, null=True, default="")
    type = models.IntegerField(null=False, blank=False, default=0)
    issale = models.IntegerField(null=False, blank=False, default=0)
    emp_code = models.CharField(max_length=32, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()

class AssetHeaderTmp(VsolvModels):
    assetdetailsbarcode = models.CharField(max_length=32,null=False,blank=False,db_index=True)
    date = models.DateField(null=False,blank=False)
    assetheader_month = models.IntegerField(null=False, blank=False)
    assetheader_year = models.IntegerField(null=False, blank=False)
    astvalbeforedeptot=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    computeddeptot=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    reviseddeptot=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    revisedcbtot=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    deprestot=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    assetheader_costtot=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    assetheader_valuetot=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    assetheader_type = models.IntegerField(default=0)
    assetheader_issale = models.SmallIntegerField(default=1)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()

class AssetDetails(VsolvModels):
    assetcat = models.ForeignKey(AssetCat, on_delete=models.SET_NULL, null=True)
    #assetheadertmp = models.ForeignKey(AssetHeaderTmp, on_delete=models.SET_NULL, null=True)
    assetheader = models.ForeignKey(AssetHeader, on_delete=models.SET_NULL, null=True)
    branch_id = models.IntegerField(null=False, blank=False, default=0)
    assetdetails_id = models.CharField(max_length=32, null=False, blank=False)
    qty = models.SmallIntegerField(null=False, blank=False)
    barcode = models.CharField(max_length=32, default=0,db_index=True)
    date = models.DateTimeField(null=False, blank=False,default=now)
    assetgroup_id = models.IntegerField(null=False, blank=False)
    product_id = models.IntegerField(null=False, blank=False)
    cat = models.CharField(max_length=64, null=False, blank=False)
    subcat = models.CharField(max_length=64, null=False, blank=False)
    assetdetails_value = models.DecimalField(max_digits=16, decimal_places=2, default=0.00,db_index=True)
    assetdetails_cost = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    description = models.CharField(max_length=128, null=False, blank=False)
    capdate = models.DateField(null=False, blank=False,db_index=True)
    source = models.CharField(max_length=128, null=False, blank=False,db_index=True)
    assetdetails_status = models.IntegerField(null=False, blank=False,default=0,db_index=True)#COMMENT 'NEW/TRANSFER/WRITEOFF/IMPAIRMENT/SALE/VALUEREDUCTION/CAPDATE/ASSETCAT/SPLIT/MERGE'
    requestfor = models.IntegerField(null=False, blank=False,default=0)# COMMENT 'Submited/Pending/Approved/Rejected''
    requeststatus = models.CharField(max_length=128, null=False, blank=False, default=0)
    assettfr_id = models.IntegerField(null=False, blank=False)
    assetsale_id = models.IntegerField(null=False, blank=False)
    not5k = models.BooleanField(default=False)
    assetowner = models.CharField(max_length=32, null=False, blank=False)
    lease_startdate = models.DateTimeField(null=True, blank=False,default=now)  # default '0000-00-00'
    lease_enddate = models.DateTimeField(null=True, blank=False,default=now)  # default '0000-00-00'
    impairasset_id = models.IntegerField(null=False, blank=False, default=0)
    impairasset = models.BooleanField(default=False)
    writeoff_id = models.IntegerField(null=False, blank=False, default=0)
    assetcatchange_id = models.IntegerField(null=False, blank=False, default=0)
    assetvalue_id = models.IntegerField(null=False, blank=False, default=0)
    assetcapdate_id = models.IntegerField(null=False, blank=False, default=0)
    assetsplit_id = models.IntegerField(null=False, blank=False, default=0)
    assetmerge_id = models.IntegerField(null=False, blank=False, default=0)
    assetcatchangedate = models.DateTimeField(null=True, blank=False)  # default '0000-00-00'
    reducedvalue = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    assetlocation_id = models.IntegerField(null=False, blank=False, default=0)
    assetdetails_bs = models.CharField(max_length=8, null=False, blank=False)
    assetdetails_cc = models.CharField(max_length=8, null=False, blank=False)
    deponhold = models.BooleanField(default=False,db_index=True)
    deprate = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    enddate = models.DateTimeField(null=False, blank=False,default=now)  # default '0000-00-00'
    parent_id = models.IntegerField(null=False, blank=False, default=0)
    assetserialno = models.CharField(max_length=128, null=False, blank=False)
    invoice_id = models.IntegerField(null=False, blank=False, default=0)
    faclringdetails_id = models.IntegerField(null=False, blank=False, default=0)
    inwheader_id = models.IntegerField(null=False, blank=False, default=0)
    inwdetail_id = models.IntegerField(null=False, blank=False, default=0)
    inwarddate = models.DateTimeField(null=True, blank=False,default=now)  # default '0000-00-00'
    mepno = models.CharField(max_length=32, null=False, blank=False)
    ponum = models.CharField(max_length=32, null=False, blank=False)
    crnum = models.CharField(max_length=32, null=False, blank=False)
    debit_id = models.IntegerField(null=False, blank=False, default=0)
    imagepath = models.CharField(max_length=128, null=True, blank=False, default=0)
    vendorname = models.CharField(max_length=128, null=False, blank=False)
    reason = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True,default=now)
    objects=FAQuerySet.as_manager()

    class meta:
        indexes=[models.Index(fields=['barcode',])]
class AssetLocation(VsolvModels):
    refgid = models.IntegerField(null=True, blank=True)
    reftablegid = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=128, null=False, blank=False)
    floor = models.CharField(max_length=128, null=False, blank=False)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()


class CwipGroup(VsolvModels):
    code = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=64, null=False, blank=False)
    gl = models.CharField(max_length=16, null=False, blank=False, default=0)
    doctype = models.SmallIntegerField(null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()


class DepSettings(VsolvModels):
    doctype = models.CharField(max_length=8, null=True, blank=True)
    depgl = models.CharField(max_length=16, null=True, blank=True)
    depreservegl = models.CharField(max_length=16, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()


class AssetCapDate(VsolvModels):
    assetdetails_id = models.CharField(max_length=32, null=True, blank=True)
    date = models.DateTimeField(null=False, blank=False)
    capdate_status = models.SmallIntegerField(default=1)
    reason = models.CharField(max_length=128, null=True, blank=True)
    capdate = models.DateTimeField(null=False, blank=False)
    oldcapdate = models.DateTimeField(null=False, blank=False)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()


class AssetCatChange(VsolvModels):
    assetdetails=models.ForeignKey(AssetDetails,on_delete=models.CASCADE,null=True)
    date = models.DateTimeField(null=False, blank=False)
    catchange_status = models.SmallIntegerField(default=1)
    reason = models.CharField(max_length=128, null=True, blank=True)
    category = models.CharField(max_length=64, null=True, blank=True)
    oldcat = models.CharField(max_length=64, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()


class AssetDebit(VsolvModels):
    assetdetails_id = models.CharField(max_length=32, null=True, blank=True)
    category_id = models.IntegerField(null=False, blank=False)
    subcategory_id = models.IntegerField(null=False, blank=False)
    glno = models.CharField(max_length=16, null=False, blank=False, default=0)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()


class AssetGroup(VsolvModels):
    number = models.IntegerField(null=False, blank=False)
    apcatategory = models.IntegerField(null=True, blank=True, default=0)  # ap_catategory FK will update
    apsubcatategory = models.IntegerField(null=True, blank=True, default=0)  # ap_subcat FK will update
    capdate = models.DateTimeField(null=False, blank=False)
    assetvalue = models.DecimalField(max_digits=16, decimal_places=2)
    branch_id = models.IntegerField(null=False, blank=False)
    remarks = models.CharField(max_length=16, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()


class AssetValue(VsolvModels):
    assetdetails = models.ForeignKey(AssetDetails, on_delete=models.SET_NULL, null=True)
    asset_barcode = models.CharField(max_length=32, default=0)
    date = models.DateTimeField(null=False, blank=False)
    assetvalue_status = models.SmallIntegerField(null=False, blank=False)
    reason = models.CharField(max_length=32, null=True)
    asset_value = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    asset_oldvalue = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()


class CwipReleaseDetail(VsolvModels):
    cwiprelease_id = models.IntegerField(null=False, blank=False)
    product_id = models.IntegerField(null=False, blank=False)
    qty = models.DecimalField(max_digits=16, decimal_places=2, default=0.000)
    releasedqty = models.DecimalField(max_digits=16, decimal_places=2, default=0.000)
    cwipreleasedetail_status = models.SmallIntegerField(default=1)  # COMMENT 'Pending/Partial Release/Fully Released/'
    branch_id = models.IntegerField(null=False, blank=False)
    remarks = models.CharField(max_length=128, null=True, blank=False)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()


class CwipRelease(VsolvModels):
    requestno = models.CharField(max_length=16, null=False, blank=False)
    requestor_id = models.IntegerField(null=False, blank=False)
    date = models.DateTimeField(null=False, blank=False)
    cwiiprelease_status = models.SmallIntegerField(default=1)  # COMMENT 'Pending/Approved/Reject'
    remarks = models.CharField(max_length=128, null=True, blank=False)
    closed = models.SmallIntegerField(default=1)  # COMMENT DEFAULT 'N' COMMENT 'Opend/CLosed'
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()


class ImpairAsset(VsolvModels):
    assetdetails_id = models.CharField(max_length=32, null=False, blank=False)
    date = models.DateTimeField(null=False, blank=False)
    impairasset_status = models.SmallIntegerField(null=False, blank=False)
    reason = models.CharField(max_length=32, null=True, blank=False)
    impairasset_value = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()

class AssetMerge(VsolvModels):
    assetmergeheader_id = models.IntegerField(null=True, blank=True)
    assetdetails_id = models.CharField(max_length=32, null=False, blank=False)
    assetmerge_value = models.CharField(max_length=16, null=False, blank=False)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()


class AssetMergeHeader(VsolvModels):
    newassetid = models.CharField(max_length=32, default=0)
    date = models.DateTimeField(null=False, blank=False)
    assetmergeheader_status = models.SmallIntegerField(null=False,
                                                       blank=False)  # COMMENT 'Submited/Pending/Approved/Rejected'
    reason = models.CharField(max_length=16, null=False, blank=False)
    assetmergeheader_value = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()


class FaAudit(VsolvModels):
    ref_id = models.IntegerField()
    ref_type = models.CharField(max_length=28, null=True, blank=True)
    data = models.TextField(null=True, blank=True)
    user_id = models.IntegerField()
    req_status = models.SmallIntegerField()
    rel_refid = models.SmallIntegerField(null=True, blank=True)
    rel_reftype = models.CharField(max_length=28, null=True, blank=True)
    action = models.CharField(max_length=28, null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()


class Meta:
    db_table = "FaAudit"


class ClearingHeader(VsolvModels):
    assettype = models.CharField(max_length=32, null=False, blank=False)
    invoicecount = models.IntegerField(null=False, blank=False)
    totinvoiceamount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    tottaxamount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    totamount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    capitalizedamount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    expenseamount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    balanceamount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    groupno = models.CharField(max_length=32, null=False, blank=False, default=0)
    clearingheader_status = models.IntegerField(default=-1)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    islock=models.SmallIntegerField(default=1)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()


class ClearingDetails(VsolvModels):
    clearingheader = models.ForeignKey(ClearingHeader, on_delete=models.CASCADE)
    supplier_id = models.IntegerField(null=False, blank=False)
    product_id = models.IntegerField(null=False, blank=False, default=0)
    branch_id = models.IntegerField(null=False, blank=False, default=0)
    invoice_id = models.IntegerField(null=False, blank=False, default=0)
    invoicedtails_id = models.IntegerField(null=False, blank=False, default=0)
    apsubcat_id = models.IntegerField(null=False, blank=False, default=0)
    doctype = models.CharField(max_length=16, null=False, blank=False)
    productname = models.CharField(max_length=128, null=True, blank=False)
    qty = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    balanceqty = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    invoiceno = models.CharField(max_length=32, null=True, blank=False)
    invoicedate = models.DateTimeField(null=False, blank=False)  # DEFAULT '0000-00-00'
    taxamount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    otheramount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    amount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    totamount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    markedup = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    mepno = models.CharField(max_length=32, null=True, blank=False)
    ponum = models.CharField(max_length=32, null=True, blank=False)
    ecfnum = models.CharField(max_length=32, null=True, blank=False)
    clearingdetails_status = models.SmallIntegerField(
        default=-1)  # 'PENDING' COMMENT 'PENDING,PROCESSED,PARTIALLY_PROCESSED'
    inv_debit_tax = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()


class AssetId(VsolvModels):
    po_id = models.IntegerField()
    podetails_id = models.IntegerField()
    pono = models.CharField(max_length=16)
    assetid = models.CharField(max_length=32, unique=True)
    received = models.BooleanField(default=False)
    receiveddate = models.DateField(null=True)
    grninwarddetails_id = models.IntegerField(null=True)
    captalised = models.BooleanField(default=False)
    source = models.SmallIntegerField(null=True)
    manufacturer = models.CharField(max_length=128, null=True, blank=False)
    serialno = models.CharField(max_length=64, null=True, blank=False)
    details = models.TextField(null=True, blank=False)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()

class AssetEntry(VsolvModels):
    branch_id = models.IntegerField(null=False, blank=False, default=0)
    fiscalyear = models.IntegerField(null=False, blank=False, default=0)
    period = models.IntegerField(null=False, blank=False, default=0)
    module = models.CharField(max_length=16, null=False, blank=False,default=0)
    screen = models.CharField(max_length=30, null=False, blank=False, default=0)
    transactiondate = models.DateField(null=False, blank=False)
    transactiontime = models.TimeField(null=False, blank=False)
    valuedate = models.DateField(null=False, blank=False)
    valuetime = models.TimeField(null=False, blank=False)
    cbsdate = models.DateTimeField(null=False, blank=False)
    localcurrency = models.IntegerField(null=False, blank=False, default=0)
    localexchangerate = models.IntegerField(null=False, blank=False, default=0)
    currency = models.IntegerField(null=False, blank=False, default=0)
    exchangerate = models.IntegerField(null=False, blank=False, default=0)
    isprevyrentry = models.IntegerField(null=False, blank=False, default=0)
    reversalentry = models.IntegerField(null=False, blank=False, default=0)
    refno = models.CharField(max_length=30, null=False, blank=False, default=0)
    crno = models.CharField(max_length=30, null=False, blank=False, default=0)
    refid = models.IntegerField(null=False, blank=False, default=0)
    reftableid = models.IntegerField(null=False, blank=False, default=0)
    type = models.IntegerField(null=False, blank=False, default=0)
    gl = models.BigIntegerField(null=False, blank=False, default=0)
    apcatno = models.IntegerField(null=False, blank=False, default=0)
    apsubcatno = models.IntegerField(null=False, blank=False, default=0)
    wisefinmap = models.IntegerField(null=False, blank=False, default=0)
    glremarks = models.CharField(max_length=250, null=False, blank=False, default=0)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    fcamount = models.DecimalField(max_digits=16, decimal_places=2,null=True, blank=True, default=0)
    ackrefno = models.CharField(max_length=128, null=True, blank=True, default=0)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()

class DepreciationTmp(VsolvModels):
    assetdetails=models.ForeignKey(AssetDetails, on_delete=models.SET_NULL, null=True)
    depreciation_fromdate = models.DateField(null=False,blank=False)
    depreciation_todate =models.DateField(null=False,blank=False)
    depreciation_month = models.IntegerField(null=False, blank=False,db_index=True)
    depreciation_year = models.IntegerField(null=False, blank=False,db_index=True)
    itcvalue=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    cavalue=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    mgmtvalue=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    resgl=models.CharField(max_length=32,null=False,blank=False)
    gl=models.CharField(max_length=32,blank=False)
    depreciation_value=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    yrclosingblnce=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    type = models.IntegerField(default=0)
    source = models.SmallIntegerField(default=1)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()

class AssetSplitHeader(VsolvModels):
    assetdetailsid = models.CharField(max_length=32,null=False,blank=False)
    date = models.DateField(null=False,blank=False)
    assetsplitheader_value=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    assetsplitheader_status = models.IntegerField(default=0)
    reason = models.CharField(max_length=128,null=True,blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()

class AssetSplitDetails(VsolvModels):
    assetsplitheader = models.ForeignKey(AssetSplitHeader, on_delete=models.CASCADE)
    newassetdetailsid = models.CharField(max_length=128,null=False,blank=False)
    assetsplitdetails_value=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()

class AssetTFR(VsolvModels):
    assetdetails=models.ForeignKey(AssetDetails,on_delete=models.CASCADE,null=True)
    date = models.DateField(null=False, blank=False)
    assettfr_from = models.IntegerField()
    assettfr_to = models.IntegerField()
    assettfr_status = models.SmallIntegerField(default=1)
    reason = models.CharField(max_length=128, null=True, blank=True)
    newassetdetailsid = models.CharField(max_length=32, null=False, blank=False)
    assettfr_value = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    emp_code = models.CharField(max_length=32,null=True,blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    objects=FAQuerySet.as_manager()

class WriteOff(VsolvModels):
    assetdetailsid = models.CharField(max_length=32, null=False, blank=False)
    date = models.DateField()
    barcode = models.CharField(max_length=32, default=0)
    writeoff_status = models.IntegerField(null=False, blank=False, default=0)
    reason = models.CharField(max_length=128, null=True, blank=False)
    value = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()


class Depreciation(VsolvModels):
    assetdetails=models.ForeignKey(AssetDetails, on_delete=models.SET_NULL, null=True)
    depreciation_fromdate = models.DateField(null=False,blank=False)
    depreciation_todate =models.DateField(null=False,blank=False)
    depreciation_month = models.IntegerField(null=False, blank=False,db_index=True)
    depreciation_year = models.IntegerField(null=False, blank=False,db_index=True)
    itcvalue=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    cavalue=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    mgmtvalue=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    resgl=models.CharField(max_length=32,null=False,blank=False)
    gl=models.CharField(max_length=32,blank=False)
    depreciation_value=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    yrclosingblnce=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    type = models.IntegerField(default=0)
    source = models.SmallIntegerField(default=1)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()

class AssetsaleHeader(VsolvModels):
    customergid = models.IntegerField(null=False, blank=False)
    salebranchgid =models.IntegerField(null=False, blank=False)
    saledate =models.DateField(null=False,blank=False)
    saletotalamount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    invoiceheadergid = models.IntegerField(null=False, blank=False,default=0)
    assetsaleheader_status=models.SmallIntegerField(default=0)
    assetsaleheader_remarks=models.CharField(max_length=128,blank=False)
    issalenote=models.SmallIntegerField(default=0)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()

class AssetsaleDetails(VsolvModels):
    assetsaleheader=models.ForeignKey(AssetsaleHeader,on_delete=models.CASCADE)
    assetdetails=models.ForeignKey(AssetDetails,on_delete=models.CASCADE,null=True)
    saledetailsdate =models.DateField(null=False,blank=False)
    assetsaledetails_status=models.SmallIntegerField(default=0)
    reason=models.CharField(max_length=128,null=True, blank=True)
    customer=models.CharField(max_length=32,null=True, blank=True)
    assetsaledetails_value = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    sgst = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    cgst = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    igst = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    invoiceheadergid = models.IntegerField(null=True, blank=True,default=0)
    hsncode=models.CharField(max_length=32,null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()

class SOHeader(VsolvModels):
    gstno = models.CharField(max_length=32,null=False,blank=False)
    soheader_date =models.DateField(null=True,blank=True)
    employee_id=models.IntegerField(default=0)
    refgid=models.IntegerField(default=0)
    reftablegid=models.IntegerField(default=0)
    channel=models.CharField(max_length=32,null=False, blank=False)
    remarks=models.CharField(max_length=128,null=True, blank=True)
    amount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    taxamount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    pono=models.CharField(max_length=128,null=True, blank=True)
    creditdays = models.IntegerField(null=True,blank=True,default=0)
    soheader_status = models.SmallIntegerField(default=0)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()

class InvoiceHeader(VsolvModels):
    customer_id = models.IntegerField(default=0)
    invoiceheader_no =models.CharField(max_length=32,null=True, blank=True,unique=True)
    invoiceheader_gstno =models.CharField(max_length=16,null=True, blank=True)
    invoiceheader_date =models.DateField(null=False,blank=False)
    employee_id=models.IntegerField(default=0)
    invoiceheader_channel =models.CharField(max_length=128,null=False, blank=False)
    invoiceheader_remarks =models.CharField(max_length=128,null=True, blank=False)
    invoiceheader_status=models.SmallIntegerField(default=0)
    amount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    taxamount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    outstanding = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    customergstno =models.CharField(max_length=16,null=False, blank=False)
    despatch_id = models.IntegerField(default=0)
    isprint=models.SmallIntegerField(default=0)
    branch_id=models.IntegerField(default=0)
    custqrytag =models.CharField(max_length=128,null=False, blank=False)
    creditdays=models.IntegerField(default=0)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()

class InvoiceDetails(VsolvModels):
    invoiceheader=models.ForeignKey(InvoiceHeader,on_delete=models.CASCADE)
    campaign_id = models.IntegerField(default=0)
    product_id = models.IntegerField(default=0)
    product_code =models.CharField(max_length=32,null=True, blank=True)
    uom_id=models.IntegerField(default=0)
    unitprice = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    qty=models.IntegerField(null=True, blank=True)
    hsncode=models.CharField(max_length=32,null=False, blank=False)
    invoiceheader_channel =models.CharField(max_length=128,null=False, blank=False)
    invoiceheader_remarks =models.CharField(max_length=128,null=False, blank=False)
    invoiceheader_status=models.SmallIntegerField(default=0)
    dealerprice = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    nrpprice = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    sgst = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    cgst = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    igst = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    taxamount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()

class SODetails(VsolvModels):
    soheader=models.ForeignKey(SOHeader,on_delete=models.CASCADE)
    campaign_id = models.IntegerField(default=0)
    product_id = models.IntegerField(default=0)
    uom_id = models.IntegerField(default=0)
    product_code =models.CharField(max_length=32,null=True, blank=True)
    sodetails_unitprice = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    sodetails_qty = models.IntegerField(default=0)
    sodetails_hsncode=models.CharField(max_length=32,null=True, blank=True)
    sodetails_cgst = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    sodetails_sgst = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    sodetails_igst = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    sodetails_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    sodetails_discount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    sodetails_taxamount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    sodetails_total = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    insert_flag=models.SmallIntegerField(default=0)
    update_flag=models.SmallIntegerField(default=0)
    sodetails_status=models.SmallIntegerField(default=0)
    remarks=models.CharField(max_length=128,null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()

class CGUAssetMap(VsolvModels):
    name =models.CharField(max_length=32,null=False, blank=False)
    barcode = models.CharField(max_length=32,null=False, blank=False)
    cgu_status = models.SmallIntegerField(default=0)
    cgu_mappeddate = models.DateField(null=False,blank=False)
    cgu_value =models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()


class ImpairHeader(VsolvModels):
    cgu_id = models.IntegerField(null=True, blank=True)
    old_cguvalue = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    newcgu_value = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    date = models.DateField(null=False, blank=False)
    asset_count = models.IntegerField(null=True, blank=True)
    reason = models.CharField(max_length=128, null=True, blank=False)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    impairheader_status = models.SmallIntegerField(default=0)
    objects=FAQuerySet.as_manager()

class ImpairDetails(VsolvModels):
    impair_id = models.ForeignKey(ImpairHeader, on_delete=models.CASCADE)
    asset_barcode = models.CharField(max_length=32,null=False, blank=False)
    oldbassetvalue = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    changedassetvalue = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()

class CGUMASTER(VsolvModels):
    name = models.CharField(max_length=32,null=False, blank=False)
    code = models.CharField(max_length=32,null=False, blank=False)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()

class Asset_update(VsolvModels):
    asset_details = models.ForeignKey(AssetDetails, on_delete=models.CASCADE, null=True)
    asset_tag = models.CharField(max_length=70, null=True, default="")
    make = models.CharField(max_length=70, null=True, default="")
    serial_no = models.CharField(max_length=70, null=True, default="")
    condition = models.CharField(max_length=70, null=True, default="")
    status = models.CharField(max_length=70, null=True, default="")
    remarks = models.CharField(max_length=70, null=True, default="")
    update_record = models.CharField(max_length=70, null=True, default="")
    pv_done = models.CharField(max_length=70, null=True, default="")
    maker_date = models.DateField(default=now)
    checker_date = models.DateField(blank=True, null=True)
    completed_date = models.DateField(blank=True, null=True)
    barcode = models.CharField(max_length=70, null=True, default="")
    product_name = models.CharField(max_length=70, null=True, default="")
    branch_code = models.CharField(max_length=70, null=True, default="")
    branch_name = models.CharField(max_length=70, null=True, default="")
    asset_cost = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    asset_value = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    document_id = models.IntegerField(blank=True, null=True)
    cr_number = models.CharField(max_length=70, null=True, default="")
    kvb_asset_id = models.CharField(max_length=70, null=True, default="")
    control_office_branch = models.CharField(max_length=70, null=True, default="")
    warrenty_startdate = models.DateTimeField(null=True, blank=True)
    warrenty_enddate = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()

class AssetEntrySync(VsolvModels):
    assetdetails_id=models.CharField(max_length=16, null=False, default="")
    hand_shake=models.CharField(max_length=20, null=True, default="")
    status=models.CharField(max_length=70, null=True, default="")
    created_date = models.DateTimeField(default=now)
    objects=FAQuerySet.as_manager()

class ITDepreciation(VsolvModels):
    date = models.DateField(null=True, blank=True)
    assettotcost=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    assettotvalue=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    itcatname=models.CharField(max_length=64,blank=True)
    dep_itopening=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    additions=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    revadditions_1=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    revadditions_2=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    revtot_val=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    dep_deletion=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    dep_closingblnce=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    dep_totval=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    dep_wdvval=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    dep_saleval=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    objects=FAQuerySet.as_manager()
    
class AssetBarcodeMap(VsolvModels):
    asset_barcode= models.CharField(max_length=70, null=True, default="")
    emp_id = models.IntegerField(blank=True, null=True)
    status = models.SmallIntegerField(default=1)
    from_date=models.DateField(null=True)
    to_date=models.DateField(null=True)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

