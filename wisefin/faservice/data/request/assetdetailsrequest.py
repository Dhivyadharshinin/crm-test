import json
from copy import copy

from django.http import HttpResponse

from faservice.models import AssetCapDate, AssetDetails, Depreciation
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage


class AssetDetailsRequest:
    id = assetdetails_id = qty = barcode = date = assetgroup_id = product_id = cat = subcat = \
        assetdetails_value = assetdetails_cost = description = capdate = source = \
        assettfr_id = assetsale_id = not5k = assetowner = lease_startdate = \
        lease_enddate = impairasset_id = impairasset = writeoff_id = assetvalue_id = assetcapdate_id = \
        assetsplit_id = assetmerge_id = assetcatchangedate = reducedvalue = branch_id = assetlocation_id = \
        assetdetails_bs = assetdetails_cc = deponhold = deprate = enddate = parent_id = assetserialno = \
        invoice_id = faclringdetails_id = inwheader_id = inwdetail_id = inwarddate = \
        debit_id = imagepath = vendorname  =AssetGroup_Gid=FA_ClearanceDetail_Gids= CC_NO=Doc_Type= None
    AssetGroup_id = FA_ClearanceDetail_ids = MarkedUpRatio = Actual_Capitalize_Amount = ASSET=None
    def __init__(self, assetdetails_data):

        if 'id' in assetdetails_data:
           self.id = assetdetails_data['id']
        if 'assetdetails_id' in assetdetails_data:
            self.assetdetails_id = assetdetails_data['assetdetails_id']
        if 'qty' in assetdetails_data:
           self.qty = assetdetails_data['qty']
        if 'barcode' in assetdetails_data:
            self.barcode = assetdetails_data['barcode']
        if 'date' in assetdetails_data:
            self.date = assetdetails_data['date']
        if 'assetgroup_id' in assetdetails_data:
            self.assetgroup_id = assetdetails_data['assetgroup_id']
        if 'product_id' in assetdetails_data:
            self.product_id = assetdetails_data['product_id']
        if 'cat' in assetdetails_data:
            self.cat = assetdetails_data['cat']
        if 'subcat' in assetdetails_data:
            self.subcat = assetdetails_data['subcat']
        if 'assetdetails_value' in assetdetails_data:
            self.assetdetails_value = assetdetails_data['assetdetails_value']
        if 'assetdetails_cost' in assetdetails_data:
            self.assetdetails_cost = assetdetails_data['assetdetails_cost']
        if 'description' in assetdetails_data:
            self.description = assetdetails_data['description']
        if 'capdate' in assetdetails_data:
            self.capdate = assetdetails_data['capdate']
        if 'source' in assetdetails_data:
            self.source = assetdetails_data['source']
        if 'assettfr_id' in assetdetails_data:
            self.assettfr_id = assetdetails_data['assettfr_id']
        if 'assetdetails_cost' in assetdetails_data:
            self.assetdetails_cost = assetdetails_data['assetdetails_cost']
        if 'not5k' in assetdetails_data:
            self.not5k = assetdetails_data['not5k']
        if 'assetowner' in assetdetails_data:
            self.assetowner = assetdetails_data['assetowner']
        if 'lease_startdate' in assetdetails_data:
            self.lease_startdate = assetdetails_data['lease_startdate']
        if 'lease_enddate' in assetdetails_data:
            self.lease_enddate = assetdetails_data['lease_enddate']
        if 'impairasset_id' in assetdetails_data:
            self.impairasset_id = assetdetails_data['impairasset_id']
        if 'impairasset' in assetdetails_data:
            self.impairasset = assetdetails_data['impairasset']
        if 'writeoff_id' in assetdetails_data:
            self.writeoff_id = assetdetails_data['writeoff_id']
        if 'assetvalue_id' in assetdetails_data:
            self.assetvalue_id = assetdetails_data['assetvalue_id']
        if 'assetcapdate_id' in assetdetails_data:
            self.assetcapdate_id = assetdetails_data['assetcapdate_id']
        if 'assetsplit_id' in assetdetails_data:
            self.assetsplit_id = assetdetails_data['assetsplit_id']
        if 'assetmerge_id' in assetdetails_data:
            self.assetmerge_id = assetdetails_data['assetmerge_id']
        if 'assetcatchangedate' in assetdetails_data:
            self.assetcatchangedate = assetdetails_data['assetcatchangedate']
        if 'reducedvalue' in assetdetails_data:
            self.reducedvalue = assetdetails_data['reducedvalue']
        if 'branch_id' in assetdetails_data:
            self.branch_id = assetdetails_data['branch_id']
        if 'assetlocation_id' in assetdetails_data:
            self.assetlocation_id = assetdetails_data['assetlocation_id']
        if 'assetdetails_bs' in assetdetails_data:
            self.assetdetails_bs = assetdetails_data['assetdetails_bs']
        if 'assetdetails_cc' in assetdetails_data:
            self.assetdetails_cc = assetdetails_data['assetdetails_cc']
        if 'deponhold' in assetdetails_data:
            self.deponhold = assetdetails_data['deponhold']
        if 'deprate' in assetdetails_data:
            self.deprate = assetdetails_data['deprate']
        if 'enddate' in assetdetails_data:
            self.enddate = assetdetails_data['enddate']
        if 'parent_id' in assetdetails_data:
            self.parent_id = assetdetails_data['parent_id']
        if 'assetserialno' in assetdetails_data:
            self.assetserialno = assetdetails_data['assetserialno']
        if 'invoice_id' in assetdetails_data:
            self.invoice_id = assetdetails_data['invoice_id']
        if 'faclringdetails_id' in assetdetails_data:
            self.faclringdetails_id = assetdetails_data['faclringdetails_id']
        if 'inwheader_id' in assetdetails_data:
            self.inwheader_id = assetdetails_data['inwheader_id']
        if 'inwdetail_id' in assetdetails_data:
            self.inwdetail_id = assetdetails_data['inwdetail_id']
        if 'inwarddate' in assetdetails_data:
            self.inwarddate = assetdetails_data['inwarddate']
        if 'debit_id' in assetdetails_data:
            self.debit_id = assetdetails_data['debit_id']
        if 'imagepath' in assetdetails_data:
            self.imagepath = assetdetails_data['imagepath']
        if 'vendorname' in assetdetails_data:
            self.vendorname = assetdetails_data['vendorname']

        if 'Doc_Type' in assetdetails_data:
           self.Doc_Type = assetdetails_data['Doc_Type']
        if 'AssetGroup_id' in assetdetails_data:
            self.AssetGroup_id = assetdetails_data['AssetGroup_id']
        if 'FA_ClearanceDetail_ids' in assetdetails_data:
           self.FA_ClearanceDetail_ids = assetdetails_data['FA_ClearanceDetail_ids']
        if 'MarkedUpRatio' in assetdetails_data:
            self.MarkedUpRatio = assetdetails_data['MarkedUpRatio']
        if 'Actual_Capitalize_Amount' in assetdetails_data:
            self.Actual_Capitalize_Amount = assetdetails_data['Actual_Capitalize_Amount']
        if 'ASSET' in assetdetails_data:
            self.ASSET = Asset(assetdetails_data['ASSET']).get_asset()

    def get_id(self):
        return self.id
    def get_assetdetails_id(self):
        return self.assetdetails_id
    def get_qty(self):
        return self.qty
    def get_Doc_Type(self):
        return self.Doc_Type
    def get_barcode(self):
        return self.barcode
    def get_date(self):
        return self.date
    def get_assetgroup_id(self):
        return self.assetgroup_id
    def get_product_id(self):
        return self.product_id
    def get_cat(self):
        return self.cat
    def get_subcat(self):
        return self.subcat
    def get_assetdetails_value(self):
        return self.assetdetails_value
    def get_assetdetails_cost(self):
        return self.assetdetails_cost
    def get_description(self):
        return self.description
    def get_capdate(self):
        return self.capdate
    def get_source(self):
        return self.source
    def get_assettfr_id(self):
        return self.assettfr_id
    def get_assetsale_id(self):
        return self.assetsale_id
    def get_not5k(self):
        return self.not5k
    def get_assetowner(self):
        return self.assetowner
    def get_lease_startdate(self):
        return self.lease_startdate
    def get_lease_enddate(self):
        return self.lease_enddate
    def get_impairasset_id(self):
        return self.impairasset_id
    def get_impairasset(self):
        return self.impairasset
    def get_writeoff_id(self):
        return self.writeoff_id
    def get_assetvalue_id(self):
        return self.assetvalue_id
    def get_assetcapdate_id(self):
        return self.assetcapdate_id
    def get_assetsplit_id(self):
        return self.assetsplit_id
    def get_assetmerge_id(self):
        return self.assetmerge_id
    def get_assetcatchangedate(self):
        return self.assetcatchangedate
    def get_reducedvalue(self):
        return self.reducedvalue
    def get_branch_id(self):
        return self.branch_id
    def get_assetlocation_id(self):
        return self.assetlocation_id
    def get_assetdetails_bs(self):
        return self.assetdetails_bs
    def get_assetdetails_cc(self):
        return self.assetdetails_cc
    def get_deponhold(self):
        return self.deponhold
    def get_deprate(self):
        return self.deprate
    def get_enddate(self):
        return self.enddate
    def get_parent_id(self):
        return self.parent_id
    def get_assetserialno(self):
        return self.assetserialno
    def get_invoice_id(self):
        return self.invoice_id
    def get_faclringdetails_id(self):
        return self.faclringdetails_id
    def get_inwheader_id(self):
        return self.inwheader_id
    def get_inwdetail_id(self):
        return self.inwdetail_id
    def get_inwarddate(self):
        return self.inwarddate
    def get_debit_id(self):
        return self.debit_id
    def get_imagepath(self):
        return self.imagepath
    def get_vendorname(self):
        return self.vendorname


class Asset:
    FAClearnceHeader_id = FAClearnceDetails_id =inv_debit_tax= Product_id = QTY = \
       crnum = Asset_Value = Branch_id = Asset_Cat_id = CP_Date = IMAGE = Location_id =is_appor= BS_NO=file=CC_NO=None
    asset_obj_list = []
    def __init__(self, asset_data):
        self.asset_obj_list = []
        for asset in asset_data:
            if 'faclringheader_gid' in asset:
                self.FAClearnceHeader_id = asset['faclringheader_gid']
            if 'inv_debit_tax' in asset:
                self.inv_debit_tax = asset['inv_debit_tax']
            if 'faclringdetails_gid' in asset:
                self.FAClearnceDetails_id = asset['faclringdetails_gid']
            if 'Product_id' in asset:
                self.Product_id = asset['Product_id']
            if 'QTY' in asset:
                self.QTY = asset['QTY']
            if 'Asset_Value' in asset:
                self.Asset_Value = asset['Asset_Value']
            if 'Branch_id' in asset:
                self.Branch_id = asset['Branch_id']
            if 'Asset_Cat_id' in asset:
                self.Asset_Cat_id = asset['Asset_Cat_id']
            if 'CP_Date' in asset:
                self.CP_Date = asset['CP_Date']
            if 'Location_id' in asset:
                self.Location_id = asset['Location_id']
            if 'BS_NO' in asset:
                self.BS_NO = asset['BS_NO']
            if 'CC_NO' in asset:
                self.CC_NO = asset['CC_NO']
            if 'files' in asset:
                self.files = asset['files']
            if 'crnum' in asset:
                self.crnum = asset['crnum']
            if 'isChecked_apportion' in asset:
                self.is_appor=asset['isChecked_apportion']
            self.asset_obj_list.append(copy(self))
    def get_asset(self):
        return self.asset_obj_list






def get_id(self):
    return self.id

    # FAClearnceHeader_Gid = FAClearnceDetails_Gid = Product_Gid = QTY = \
    #     Asset_Value = Branch_Gid = Asset_SubCat_Gid = CP_Date = Location_Gid = BS_NO = CC_NO


# def get_assetdetails_id(self):
#     return self.assetdetails_id
def get_qty(self):
    return self.qty
    def get_Doc_Type(self):
        return self.Doc_Type

class CheckerSummaryRequest:
    page=capdate=cat=branch=Grp_by=user_id=assetgroup=assetdetails_id=crno=reason=None
    def __init__(self,request):
        self.capdate = request.GET.get('capdate', None)
        self.cat=request.GET.get('cat',None)
        self.crno = request.GET.get('crno', None)
        self.user_id= request.GET.get('cat', None)
        self.branch = request.GET.get('branch', None)
        self.Grp_by = request.GET.get('Grp_by')
        self.assetgroup=request.GET.get('assetgroup')
        self.assetdetails_id=request.GET.get('assetdetails_id')

        if 'asset_id' in request.GET:
            self.asset_id=int(request.GET.get('asset_id',''))
        if 'reason' in request.GET:
            self.reason=request.GET.get('reason','')
        self.user_id= request.user.id

class CheckerSumRequest:
    assetgroup=None
    assetdetails_id=None

    def __init__(self, assetdetails_data):

        if 'assetgroup' in assetdetails_data:
           self.id = assetdetails_data['assetgroup']
        if 'assetdetails_id' in assetdetails_data:
           self.id = assetdetails_data['assetdetails_id']

    def get_assetdetails_id(self):
        return self.assetdetails_id
    def get_assetgroup(self):
        return self.assetgroup

class CapDateRequest:
    assetid_list=capdate=reason=capdate_id=status=None
    def __init__(self,json_data):
        if 'assetid_list' in json_data:
            self.assetid_list=json_data['assetid_list']
        if 'capdate' in json_data:
            self.capdate=json_data['capdate']
        if 'reason' in json_data:
            self.reason=json_data['reason']
        if 'status' in json_data:
            self.status=json_data['status']
        if 'capdate_id' in json_data:
            self.capdate_id=json_data['capdate_id']
def validate_data(data,create_by):
    err=Error()
    validations = {}
    cap_data=AssetCapDate.objects.filter(id__in=data.capdate_id)
    for capdata in cap_data:
        asst_data=AssetDetails.objects.filter(assetdetails_id=capdata.assetdetails_id)
        try:
            dep_data=Depreciation.objects.get(asset_id=asst_data.id)
            if dep_data !=None:
                validations['dep_change']=False
            else:
                validations['dep_change']=True
        except:
            validations['dep_change'] = True

        if capdata.created_by==create_by:
            validations['checker']=False
        else:
            validations['checker']=True

        for key,value in validations.items():
            if value==False:
                if key=='checker':
                    err.set_code(ErrorMessage.INVALID_APPROVER_ID)
                if key=='dep_change':
                    err.set_code(ErrorMessage.DEPRECIATION_RECORD)
                err.set_description(ErrorDescription.VALIDATION_ERROR)
                err=HttpResponse(err.get(),content_type='application/json')
                return err
    return True

class FapvReq:
    id = emp_id  = asset_barcode=status= to_date=from_date= None

    def __init__(self,json_data):
        if 'emp_id' in json_data:
            self.emp_id=json_data['emp_id']
        if 'asset_barcode' in json_data:
            self.asset_barcode=json_data['asset_barcode']
        if 'id' in json_data:
            self.id=json_data['id']
        if 'status' in json_data:
            self.status = json_data['status']
        if 'from_date' in json_data:
            self.from_date = json_data['from_date']
        if 'to_date' in json_data:
            self.to_date = json_data['to_date']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def get_id(self):
        self.id = id

    def get_emp_ename(self):
       return self.emp_id

    def get_asset_barcode(self):
        return self.asset_barcode

    def get_status(self):
        return self.status

    def get_from_date(self):
        return self.from_date

    def get_to_date(self):
        return self.to_date