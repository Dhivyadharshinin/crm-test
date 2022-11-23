from datetime import datetime
import pandas as pd
from faservice.models.famodels import DepreciationTmp, AssetCat, AssetDetails, AssetHeaderTmp, Depreciation, \
    AssetHeader, Asset_update
from faservice.util.FaApiService import FaApiService, ServiceCall
from faservice.util.FaReportUtil import ReportFAR
from nwisefin.settings import logger
import numpy as np

from masterservice.models.mastermodels import APsubcategory, Product, Apcategory
from userservice.models.usermodels import EmployeeBranch
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class ReportDepreciationService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
    def report_depreciation_fin(self, user_id, request):
        scope=request.scope
        START_TIME_D = datetime.now()
        START_TIME = START_TIME_D.strftime("%d/%m/%Y %H:%M:%S")
        logger.info('Depreciation_Excel_Start - ' + START_TIME)
        conditiondate = DepreciationTmp.objects.latest('depreciation_todate')
        df1 = AssetDetails.objects.filter(status=1, capdate__lte=str(conditiondate.depreciation_todate)).values(
            'barcode', 'id', 'assetcat_id', 'branch_id', 'date', 'product_id', 'assetdetails_value',
            'assetdetails_cost', 'capdate', 'deprate', 'assetdetails_status', 'enddate')

        # print(df1.query)
        df1 = pd.DataFrame(df1)
        df_agg = {'date': 'first', 'assetdetails_value': 'first', 'assetdetails_cost': 'first', 'capdate': 'first',
                  'assetdetails_status': 'first', 'enddate': 'first', 'assetcat_id': 'first', 'branch_id': 'first',
                  'product_id': 'first', 'deprate': 'first', 'id': 'first'}
        df1 = pd.DataFrame(df1.groupby(by=['barcode'], as_index=False).agg(df_agg))
        df1.rename(columns={'barcode': 'Asset_ID', 'date': 'Asset_Create_Date', 'assetdetails_value': 'Asset_Value',
                            'assetdetails_cost': 'Purchase_cost', 'capdate': 'Cap_Date',
                            'assetdetails_status': 'Assert_Status', 'enddate': 'End_Date',
                            'deprate': 'Dep_Rate'}, inplace=True)

        df2 = DepreciationTmp.objects.all().values('assetdetails', 'depreciation_fromdate', 'depreciation_todate',
                                                   'yrclosingblnce')
        df2 = pd.DataFrame(df2)
        df2.rename(columns={'assetdetails_id': 'assetdetails', 'depreciation_fromdate': 'Dep_From_Date',
                            'depreciation_todate': 'Dep_To_Date', 'yrclosingblnce': 'Dep_Yr_Closing_Balance'},
                   inplace=True)

        df3 = Depreciation.objects.all().values('id', 'depreciation_todate')
        df3 = pd.DataFrame(df3)
        # print('df3', df3)
        fa_obj=FaApiService(scope)
        df4 = fa_obj.emp_branch_list()
        df4 = pd.DataFrame(df4.data)
        df4.rename(columns={'id': 'empbranch_id', 'code': 'Branch_Code', 'name': 'Branch_Name'}, inplace=True)

        df5 = fa_obj.fetch_product_dep()
        df5 = pd.DataFrame(df5.data)
        df5.rename(columns={'id': 'empproduct_id', 'name': 'Product_Name'}, inplace=True)

        df6 = fa_obj.fetchsubcategory_dep()
        df6 = pd.DataFrame(df6.data)
        df6.rename(columns={'id': 'subcat_id', 'no': 'Sub_Cat_No', 'glno': 'Asset_GL', 'category': 'category_id'},
                   inplace=True)

        df7 = fa_obj.fetchcategory_dep()
        df7 = pd.DataFrame(df7.data)
        df7.rename(columns={'id': 'apcat_id', 'no': 'Cat_No'}, inplace=True)

        df8 = AssetCat.objects.all().values('id', 'subcategory_id', 'deptype', 'depgl_mgmt', 'subcatname')
        df8 = pd.DataFrame(df8)
        df8.rename(columns={'id': 'empassetcat_id', 'deptype': 'Dep_Type', 'depgl_mgmt': 'Dep_GL'}, inplace=True)

        df9 = AssetHeaderTmp.objects.all().values('assetdetailsbarcode', 'revisedcbtot', 'astvalbeforedeptot',
                                                  'assetheader_issale', 'reviseddeptot')
        df9 = pd.DataFrame(df9)
        df9.rename(columns={'assetdetailsbarcode': 'IT/OD', 'astvalbeforedeptot': 'Asset_Val_Before_Dep',
                            'revisedcbtot': 'Closing_Balance'}, inplace=True)
        QUERY_TIME_D = datetime.now()
        QUERY_TIME = QUERY_TIME_D.strftime("%d/%m/%Y %H:%M:%S")
        logger.info('QUERY_GENERATED - ' + QUERY_TIME)

        # table merge
        Product_DATA = pd.merge(df1, df5, how='inner', left_on=['product_id'], right_on=['empproduct_id'])
        Branch_DATA = pd.merge(Product_DATA, df4, how='inner', left_on=['branch_id'], right_on=['empbranch_id'])
        assetCat_DATA = pd.merge(Branch_DATA, df8, how='inner', left_on=['assetcat_id'], right_on=['empassetcat_id'])
        subCat_DATA = pd.merge(assetCat_DATA, df6, how='inner', left_on=['subcategory_id'], right_on=['subcat_id'])
        apCat_DATA = pd.merge(subCat_DATA, df7, how='inner', left_on=['category_id'], right_on=['apcat_id'])
        if df3.empty:
            Header_DATA = pd.merge(apCat_DATA, df9, how='inner', left_on=['Asset_ID'], right_on=['IT/OD'])
            DATA7 = pd.merge(Header_DATA, df2, how='left', left_on=['id'], right_on=['assetdetails'])
        else:
            Depreciation_DATA = pd.merge(apCat_DATA, df3, how='left', left_on=['id'], right_on=['id'])
            Header_DATA = pd.merge(Depreciation_DATA, df9, how='inner', left_on=['Asset_ID'], right_on=['IT/OD'])
            DATA7 = pd.merge(Header_DATA, df2, how='left', left_on=['id'], right_on=['assetdetails'])
        # print(DATA7)

        if df3.empty:
            pass
        else:
            DATA7['depreciation_todate'] = pd.to_datetime(DATA7['depreciation_todate'])
            DATA7['depreciation_todate'] = DATA7['depreciation_todate'].dt.date
        DATA7['Cap_Date'] = pd.to_datetime(DATA7['Cap_Date'])
        DATA7['Cap_Date'] = DATA7['Cap_Date'].dt.date
        DATA7['IT/OD'] = DATA7['IT/OD'].apply(lambda x: 'I' if x[6] == 'I' else 'O')

        DATA7['acc_branch_code'] = '-'

        def calculate(a, b):
            # print('new', a, b)
            if a == 'WDV':
                return 'F&F'
            elif b == 'Vehicle':
                return 'VCH'
            else:
                return 'F&F'

        DATA7['Class'] = ''
        DATA7["Class"] = DATA7.apply(lambda x: calculate(x["Dep_Type"], x["subcatname"]), axis=1)
        # DATA7['Class'] = DATA7['Dep_Type'].apply(lambda x: 'L&B' if x == 'WDV' else 'F&F')
        # DATA7['Class'] = DATA7['subcatname'].apply(lambda x: 'VCH' if 'Vehicle' in x else 'F&F')

        # print('Closing_Balance ', DATA7['Closing_Balance'])
        # print('Asset_Value ', DATA7['Asset_Value'])
        # print('Product_Name ', DATA7['Product_Name'])

        # DATA7['Dep_Value'] = DATA7['Closing_Balance']
        DATA7['Additions_After_Last_Dep'] = 0

        # conditions = [
        #     (DATA7['Asset_Value'] == 1),
        #     (DATA7['Product_Name'] == 'Land')
        # ]
        # values = [0, 0]
        # DATA7['Dep_Value'] = np.select(conditions, values, default=DATA7['Closing_Balance'])

        # print('dep_value ',DATA7['Dep_Value'])
        def condition(a, b, c):
            # print('new', a, b)
            if a == 1:
                return 0
            elif b == 'Land':
                return 0
            else:
                return c

        # Applying the conditions
        DATA7['Dep_Value'] = ''
        DATA7["Dep_Value"] = DATA7.apply(lambda x: condition(x["Asset_Value"], x["Product_Name"], x['reviseddeptot']),
                                         axis=1)

        # DATA7['Dep_Value'] = DATA7['Product_Name'].apply(calculate)
        # DATA7['Dep_Value'] = DATA7['Asset_Value'].apply(lambda x: 0 if DATA7['Asset_Value'] == 1 else 0)
        # DATA7['Dep_Value'] = DATA7['Product_Name'].apply(lambda x: 0 if x == 'Land' else 2)
        # DATA7['Dep_Value'] = DATA7['Dep_Value'].apply(lambda x: DATA7['Closing_Balance'] if x == 2 else 0)

        def sold(a):
            # print('new', a)
            if a == 1:
                return 'YES'
            else:
                return 'NO'

        DATA7['SOLD'] = ''
        DATA7['SOLD'] = DATA7.apply(lambda x: sold(x["assetheader_issale"]), axis=1)

        if df3.empty:
            pass
        else:
            def depcal(a,b,c):
                if a == '':
                    return c
                elif a < b:
                    return c
                else:
                    return 0

            DATA7['Additions_After_Last_Dep'] = ''
            DATA7['Additions_After_Last_Dep'] = DATA7.apply(lambda x: depcal(x["depreciation_todate"],x['Cap_Date'],
                                                                           x['Purchase_cost']), axis=1)
            # conditions = [
            #     (DATA7['depreciation_todate'] == ''),
            #     (DATA7['depreciation_todate'] < DATA7['Cap_Date'])
            # ]
            # values = [DATA7['Purchase_cost'], DATA7['Purchase_cost']]
            # DATA7['Additions_After_Last_Dep'] = np.select(conditions, values)
        DATA7['Removal'] = '-'

        # print(DATA7)

        dataDropFinal = DATA7.drop(columns=['id', 'assetcat_id', 'branch_id', 'product_id', 'empproduct_id',
                                            'empbranch_id', 'empassetcat_id', 'subcategory_id', 'assetheader_issale',
                                            'category_id'])

        IndexData = dataDropFinal.reindex(
            columns=['Asset_ID', 'Product_Name', 'Branch_Code', 'Branch_Name', 'Dep_Type', 'Dep_GL',
                     'Asset_GL', 'Dep_From_Date', 'Dep_To_Date', 'Class', 'Cat_No', 'Sub_Cat_No',
                     'Asset_Create_Date', 'Cap_Date', 'End_Date', 'Dep_Rate', 'Purchase_cost',
                     'Dep_Yr_Closing_Balance', 'Additions_After_Last_Dep', 'Removal', 'Asset_Val_Before_Dep',
                     'Dep_Value', 'Closing_Balance', 'acc_branch_code', 'Assert_Status', 'IT/OD', 'SOLD'])

        # print('Depreciation_Excel_Data ', IndexData)
        END_TIME_D = datetime.now()
        END_TIME = END_TIME_D.strftime("%d/%m/%Y %H:%M:%S")
        logger.info('Depreciation_Excel_Generate - ' + END_TIME)

        return IndexData

    def report_depreciation_regular(self, user_id, request):
        START_TIME_D = datetime.now()
        START_TIME = START_TIME_D.strftime("%d/%m/%Y %H:%M:%S")
        logger.info('Depreciation_Excel_Start - ' + START_TIME)
        conditiondate = DepreciationTmp.objects.latest('depreciation_todate')
        df1 = AssetDetails.objects.filter(status=1, capdate__lte=str(conditiondate.depreciation_todate)).values(
            'barcode', 'id', 'assetcat_id', 'branch_id', 'date', 'product_id', 'assetdetails_value',
            'assetdetails_cost', 'capdate', 'deprate', 'assetdetails_status', 'enddate')

        # print(df1.query)
        df1 = pd.DataFrame(df1)
        df_agg = {'date': 'first', 'assetdetails_value': 'first', 'assetdetails_cost': 'first', 'capdate': 'first',
                  'assetdetails_status': 'first', 'enddate': 'first', 'assetcat_id': 'first', 'branch_id': 'first',
                  'product_id': 'first', 'deprate': 'first', 'id': 'first'}
        df1 = pd.DataFrame(df1.groupby(by=['barcode'], as_index=False).agg(df_agg))
        df1.rename(columns={'barcode': 'Asset_ID', 'date': 'Asset_Create_Date', 'assetdetails_value': 'Asset_Value',
                            'assetdetails_cost': 'Purchase_cost', 'capdate': 'Cap_Date',
                            'assetdetails_status': 'Assert_Status', 'enddate': 'End_Date',
                            'deprate': 'Dep_Rate'}, inplace=True)

        # print(df1)

        df2 = Depreciation.objects.all().values('id', 'depreciation_fromdate', 'depreciation_todate',
                                                'yrclosingblnce')
        df2 = pd.DataFrame(df2)
        if df2.empty:
            pass
        else:
            df2.rename(columns={'depreciation_fromdate': 'Dep_From_Date',
                                'depreciation_todate': 'Dep_To_Date', 'yrclosingblnce': 'Dep_Yr_Closing_Balance'},
                       inplace=True)
            # print(df2.empty)

        df4 = EmployeeBranch.objects.all().values('id', 'code', 'name')
        df4 = pd.DataFrame(df4)
        df4.rename(columns={'id': 'empbranch_id', 'code': 'Branch_Code', 'name': 'Branch_Name'}, inplace=True)

        df5 = Product.objects.all().values('id', 'name')
        df5 = pd.DataFrame(df5)
        df5.rename(columns={'id': 'empproduct_id', 'name': 'Product_Name'}, inplace=True)

        df6 = APsubcategory.objects.all().values('glno', 'id', 'no', 'category')
        df6 = pd.DataFrame(df6)
        df6.rename(columns={'id': 'subcat_id', 'no': 'Sub_Cat_No', 'glno': 'Asset_GL', 'category': 'category_id'},
                   inplace=True)

        df7 = Apcategory.objects.all().values('id', 'no')
        df7 = pd.DataFrame(df7)
        df7.rename(columns={'id': 'apcat_id', 'no': 'Cat_No'}, inplace=True)

        df8 = AssetCat.objects.all().values('id', 'subcategory_id', 'deptype', 'depgl_mgmt', 'subcatname')
        df8 = pd.DataFrame(df8)
        df8.rename(columns={'id': 'empassetcat_id', 'deptype': 'Dep_Type', 'depgl_mgmt': 'Dep_GL'}, inplace=True)

        df9 = AssetHeader.objects.all().values('barcode', 'revisedcbtot', 'astvalbeforedeptot',
                                               'issale', 'reviseddeptot')
        df9 = pd.DataFrame(df9)
        df9.rename(columns={'barcode': 'IT/OD', 'astvalbeforedeptot': 'Asset_Val_Before_Dep',
                            'revisedcbtot': 'Closing_Balance'}, inplace=True)
        QUERY_TIME_D = datetime.now()
        QUERY_TIME = QUERY_TIME_D.strftime("%d/%m/%Y %H:%M:%S")
        logger.info('QUERY_GENERATED - ' + QUERY_TIME)

        # table merge
        Product_DATA = pd.merge(df1, df5, how='inner', left_on=['product_id'], right_on=['empproduct_id'])
        Branch_DATA = pd.merge(Product_DATA, df4, how='inner', left_on=['branch_id'], right_on=['empbranch_id'])
        assetCat_DATA = pd.merge(Branch_DATA, df8, how='inner', left_on=['assetcat_id'],
                                 right_on=['empassetcat_id'])
        subCat_DATA = pd.merge(assetCat_DATA, df6, how='inner', left_on=['subcategory_id'], right_on=['subcat_id'])
        apCat_DATA = pd.merge(subCat_DATA, df7, how='inner', left_on=['category_id'], right_on=['apcat_id'])
        Header_DATA = pd.merge(apCat_DATA, df9, how='inner', left_on=['Asset_ID'], right_on=['IT/OD'])
        if df2.empty:
            DATA7 = Header_DATA
        else:
            DATA7 = pd.merge(Header_DATA, df2, how='left', left_on=['id'], right_on=['id'])
            # print(DATA7)

        if df2.empty:
            pass
        else:
            DATA7['Dep_To_Date'] = pd.to_datetime(DATA7['Dep_To_Date'])
            DATA7['Dep_To_Date'] = DATA7['Dep_To_Date'].dt.date
        DATA7['Cap_Date'] = pd.to_datetime(DATA7['Cap_Date'])
        DATA7['Cap_Date'] = DATA7['Cap_Date'].dt.date
        DATA7['IT/OD'] = DATA7['IT/OD'].apply(lambda x: 'I' if x[6] == 'I' else 'O')
        DATA7['acc_branch_code'] = '-'

        def calculate(a, b):
            # print('new', a, b)
            if a == 'WDV':
                return 'F&F'
            elif b == 'Vehicle':
                return 'VCH'
            else:
                return 'F&F'

        DATA7['Class'] = ''
        DATA7["Class"] = DATA7.apply(lambda x: calculate(x["Dep_Type"], x["subcatname"]), axis=1)

        # DATA7['Class'] = ''
        # DATA7['Class'] = DATA7['Dep_Type'].apply(lambda x: 'L&B' if x == 'WDV' else 'F&F')
        # DATA7['Class'] = DATA7['subcatname'].apply(lambda x: 'VCH' if 'Vehicle' in x else 'F&F')

        print('Closing_Balance ', DATA7['Closing_Balance'])
        print('Asset_Value ', DATA7['Asset_Value'])
        print('Product_Name ', DATA7['Product_Name'])

        def condition(a, b, c):
            print('new', a, b)
            if a == 1:
                return 0
            elif b == 'Land':
                return 0
            else:
                return c

        # Applying the conditions
        DATA7['Dep_Value'] = ''
        DATA7["Dep_Value"] = DATA7.apply(lambda x: condition(x["Asset_Value"], x["Product_Name"], x['reviseddeptot']),
                                         axis=1)

        # DATA7['Dep_Value'] = DATA7['Closing_Balance']
        # DATA7['Additions_After_Last_Dep'] = 0
        # conditions = [
        #     (DATA7['Asset_Value'] == 1),
        #     (DATA7['Product_Name'] == 'Land')
        # ]
        # values = [0, 0]
        # DATA7['Dep_Value'] = np.select(conditions, values, default=DATA7['Closing_Balance'])

        # print('dep_value ',DATA7['Dep_Value'])
        # DATA7['Dep_Value'] = DATA7['Asset_Value'].apply(lambda x: 0 if x == 1 else 2)
        # DATA7['Dep_Value'] = DATA7['Product_Name'].apply(lambda x: 0 if x == 'Land' else 2)
        # DATA7['Dep_Value'] = DATA7['Dep_Value'].apply(lambda x: DATA7['Closing_Balance'] if x == 2 else 0)

        def sold(a):
            print('new', a)
            if a == 1:
                return 'YES'
            else:
                return 'NO'

        DATA7['SOLD'] = ''
        DATA7['SOLD'] = DATA7.apply(lambda x: sold(x["issale"]), axis=1)

        # DATA7['SOLD'] = 'NO'
        # DATA7['SOLD'] = DATA7['issale'].apply(lambda x: 'YES' if x == 1 else 'NO')

        if df2.empty:
            pass
        else:
            def depcal(a,b,c):
                if a == '':
                    return c
                elif a < b:
                    return c
                else:
                    return 0

            DATA7['Additions_After_Last_Dep'] = ''
            DATA7['Additions_After_Last_Dep'] = DATA7.apply(lambda x: depcal(x["depreciation_todate"],x['Cap_Date'],
                                                                           x['Purchase_cost']), axis=1)

            # DATA7['Additions_After_Last_Dep'] = 0
            # conditions = [
            #     (DATA7['Dep_To_Date'] == ''),
            #     (DATA7['Dep_To_Date'] < DATA7['Cap_Date'])
            # ]
            # values = [DATA7['Purchase_cost'], DATA7['Purchase_cost']]
            # DATA7['Additions_After_Last_Dep'] = np.select(conditions, values)
        DATA7['Removal'] = '-'

        print(DATA7)

        dataDropFinal = DATA7.drop(columns=['id', 'assetcat_id', 'branch_id', 'product_id', 'empproduct_id',
                                            'empbranch_id', 'empassetcat_id', 'subcategory_id',
                                            'issale',
                                            'category_id'])

        if df2.empty:
            IndexData = dataDropFinal.reindex(
                columns=['Asset_ID', 'Product_Name', 'Branch_Code', 'Branch_Name', 'Dep_Type', 'Dep_GL',
                         'Asset_GL', 'Dep_From_Date', 'Dep_To_Date', 'Class', 'Cat_No', 'Sub_Cat_No',
                         'Asset_Create_Date', 'Cap_Date', 'End_Date', 'Dep_Rate', 'Purchase_cost',
                         'Additions_After_Last_Dep', 'Removal', 'Asset_Val_Before_Dep',
                         'Dep_Value', 'Closing_Balance', 'acc_branch_code', 'Assert_Status', 'IT/OD', 'SOLD'])
        else:
            IndexData = dataDropFinal.reindex(
                columns=['Asset_ID', 'Product_Name', 'Branch_Code', 'Branch_Name', 'Dep_Type', 'Dep_GL',
                         'Asset_GL', 'Dep_From_Date', 'Dep_To_Date', 'Class', 'Cat_No', 'Sub_Cat_No',
                         'Asset_Create_Date', 'Cap_Date', 'End_Date', 'Dep_Rate', 'Purchase_cost',
                         'Dep_Yr_Closing_Balance', 'Additions_After_Last_Dep', 'Removal', 'Asset_Val_Before_Dep',
                         'Dep_Value', 'Closing_Balance', 'acc_branch_code', 'Assert_Status', 'IT/OD', 'SOLD'])

        print('Depreciation_Excel_Data ', IndexData)

        END_TIME_D = datetime.now()
        END_TIME = END_TIME_D.strftime("%d/%m/%Y %H:%M:%S")
        logger.info('Depreciation_Excel_Generate - ' + END_TIME)

        return IndexData

        # DATA7['Dep_Value'] = DATA7['Closing_Balance']
        # conditions = [
        #     (DATA7['Asset_Value'] == 1),
        #     (DATA7['Product_Name'] == 'Land'),
        # ]
        # values = [0, 0]
        # DATA7['Dep_Value'] = np.select(conditions, values)
        # print(DATA7)

        # DATA7['SOLD'] = 'NO'
        # conditions = [
        #     (DATA7['assetheader_issale'] == 1)
        # ]
        # values = ['YES']
        # DATA7['SOLD'] = np.select(conditions, values)
        # print(DATA7)

        # asst_data = AssetDetails.objects.all()[0:100]
        # asset_data = AssetDetails.objects.filter(status=1).annotate(barcode__in=Count('assetheader__barcode'))
        # print(asset_data)
        #
        # branchID = []
        # subcatID = []
        # productID = []
        # assetID = []
        # a = 0
        # for i in asset_data:
        #     assetID.append(i.id)
        #     subcatID.append(i.assetcat.subcategory_id)
        #     branchID.append(i.branch_id)
        #     productID.append(i.product_id)
        #
        # subcatDATA = APsubcategory.objects.filter(id__in=subcatID)
        # print(subcatDATA)
        # branchDATA = EmployeeBranch.objects.filter(id__in=branchID)
        # print(branchDATA)
        # productDATA = Product.objects.filter(id__in=productID)
        # depDATA = Depreciation.objects.filter(assetdetails_id__in=assetID)
        # print("depDATA ",depDATA)
        # deptmpDATA = DepreciationTmp.objects.filter(assetdetails_id__in=assetID)
        # print("deptmpDATA ",deptmpDATA)
        #
        # output = []
        # for asst_data in asset_data:
        #     dep_resp = DepreciationSettingResponse()
        #     dep_resp.set_Asset_ID(asst_data.assetdetails_id)
        #     dep_resp.set_branchdata(asst_data.branch_id,branchDATA)
        #     dep_resp.set_productdata(asst_data.product_id,productDATA)
        #     dep_resp.set_Dep_Type(asst_data.assetcat.deptype)
        #     dep_resp.set_Dep_GL(asst_data.assetcat.depgl_mgmt)
        #     dep_resp.set_sucatdata(asst_data.assetcat.subcategory_id,subcatDATA)
        #     dep_resp.set_Asset_Create_Date(asst_data.date)
        #     dep_resp.set_Cap_Date(asst_data.capdate)
        #     dep_resp.set_End_Date(asst_data.enddate)
        #     dep_resp.set_Dep_Rate(asst_data.deprate)
        #     dep_resp.set_Purchase_cost(asst_data.assetdetails_cost)
        #     dep_resp.set_depdata(asst_data.id,deptmpDATA)
        #     dep_resp.set_Asset_Val_Before_Dep(asst_data.assetheader.astvalbeforedeptot)
        #     dep_resp.set_Closing_Balance(asst_data.assetheader.revisedcbtot)
        #     dep_resp.set_acc_branch_code('-')
        #     dep_resp.set_Assert_Status(asst_data.status)
        #     dep_resp.set_ITOD(asst_data.assetheader.barcode)
        #     dep_resp.set_SOLD(asst_data.assetheader.issale)
        #     dep_resp.set_deptmpdata(asst_data.id,depDATA)
        #
        #     if asst_data.assetcat.deptype == 'WDV':
        #         dep_resp.set_Class('L&B')
        #     elif "Vehicle" in asst_data.assetcat.subcatname:
        #         dep_resp.set_Class("VCH")
        #     else:
        #         dep_resp.set_Class("F&F")
        #     if dep_resp.get_dep_todate() == None or dep_resp.get_dep_todate() < asst_data.capdate:
        #         dep_resp.set_Additions_After_Last_Dep(asst_data.assetdetails_cost)
        #     else:
        #         dep_resp.set_Additions_After_Last_Dep(0)
        #         dep_resp.set_Removal('-')
        #
        #     if asst_data.assetdetails_value == 1:
        #         dep_resp.set_Dep_Value(0)
        #     elif asst_data.product_id == 'land':
        #         dep_resp.set_Dep_Value(0)
        #     else:
        #         dep_resp.set_Dep_Value(asst_data.assetheader.revisedcbtot)
        #
        #     if asst_data.assetheader.issale == 1:
        #         dep_resp.set_SOLD("YES")
        #     else:
        #         dep_resp.set_SOLD("NO")
        #     if a == 10000:
        #         A.objects.bulk_create(dep_resp.get())
        #         output.append(dep_resp.get())
        #     print('Data ',dep_resp)
        # return output

        # json_resp=dict()
        # asst_data = AssetDetails.objects.filter(status=1).annotate(barcode__in=Count('assetheader__barcode'))[0:10000]
        # for i in asst_data:
        #     branch_data = fa_obj.fetch_branch(i.branch_id)
        #     dep_data = DepreciationTmp.objects.filter(assetdetails_id=i.id)
        #     deptrn_data = Depreciation.objects.filter(assetdetails_id=i.id)
        #
        #     dep_resp = DepreciationSettingResponse()
        #     asset_id=list(i.values_list('assetdetails_id', flat=True))
        #     product = dep_resp.set_Product_Name(fa_obj.fetch_product.values_list(i.product_id, user_id).name)
        #     branch_code=list(branch_data.values_list(branch_data.code))
        #     branch_name=list(branch_data.values_list(branch_data.name))
        #     deptype=list(i.assetcat.deptype.values_list('deptype', flat=True))
        #     gl_no = dep_resp.set_Asset_GL(fa_obj.fetchsubcategory(i.assetcat.subcategory_id).glno)
        #     depreciation_fromdate=list(dep_data.values_list('depreciation_fromdate', flat=True))
        #     depreciation_todate=list(dep_data.values_list('depreciation_todate', flat=True))
        #     cat_no = dep_resp.set_Cat_No(fa_obj.fetchcategory(i.assetcat.id).id)
        #     subcat_no = dep_resp.set_Sub_Cat_No(fa_obj.fetchsubcategory(i.assetcat.subcategory_id).no)
        #     date= [d.strftime('%Y-%m-%d::%H-%M') for d in i.values_list('date', flat=True)]
        #     capdate=list(i.values_list('capdate', flat=True))
        #     enddate=list(i.values_list('enddate', flat=True))
        #     deprate=list(i.values_list('deprate', flat=True))
        #     assetdetails_cost=list(i.values_list('assetdetails_cost', flat=True))
        #     yrclosingblnce=list(dep_data.values_list('yrclosingblnce', flat=True))
        #     astvalbeforedeptot=list(i.assetheader.values_list('astvalbeforedeptot', flat=True))
        #     revisedcbtot=list(i.assetheader.values_list('revisedcbtot', flat=True))
        #     acc_branch_code=list('-')
        #     status=list(i.values_list('status', flat=True))
        #     headerbarcode=list(i.assetheader.values_list('barcode', flat=True))
        #
        #     json_resp['name']=asset_id
        #     json_resp['product']=product
        #     json_resp['branch_code']=branch_code
        #     json_resp['branch_name']=branch_name
        #     json_resp['deptype']=deptype
        #     json_resp['depreciation_fromdate']=depreciation_fromdate
        #     json_resp['depreciation_todate']=depreciation_todate
        #     json_resp['cat_no']=cat_no
        #     json_resp['subcat_no']=subcat_no
        #     json_resp['date'] = date
        #     json_resp['capdate'] = capdate
        #     json_resp['enddate'] = enddate
        #     json_resp['deprate'] = deprate
        #     json_resp['assetdetails_cost'] = assetdetails_cost
        #     json_resp['yrclosingblnce'] = yrclosingblnce
        #     json_resp['astvalbeforedeptot'] = astvalbeforedeptot
        #     json_resp['revisedcbtot'] = revisedcbtot
        #     json_resp['acc_branch_code'] = acc_branch_code
        #     json_resp['status'] = status
        #     json_resp['headerbarcode'] = headerbarcode
        #     # print(len(json_resp['date']))
        #     print(json_resp)
        #     return json_resp


    def report_depreciation_far(self, user_id, request,scope):
        START_TIME_D = datetime.now()
        START_TIME = START_TIME_D.strftime("%d/%m/%Y %H:%M:%S")
        logger.info('Depreciation_Excel_Start - ' + START_TIME)
        df1 = AssetDetails.objects.filter(status=1).values(
            'barcode', 'id', 'assetcat_id', 'branch_id', 'date', 'product_id', 'assetdetails_value',
            'assetdetails_cost', 'capdate', 'deprate', 'assetdetails_status', 'enddate', 'cat', 'subcat')

        print(df1.query)
        df1 = pd.DataFrame(df1)
        df_agg = {'date': 'first', 'assetdetails_value': 'first', 'assetdetails_cost': 'first', 'capdate': 'first',
                  'assetdetails_status': 'first', 'enddate': 'first', 'assetcat_id': 'first', 'branch_id': 'first',
                  'product_id': 'first', 'deprate': 'first', 'id': 'first', 'cat':'first', 'subcat':'first'}
        if df1.empty:
            df1 = pd.DataFrame(df1)
        else:
            df1 = pd.DataFrame(df1.groupby(by=['barcode'], as_index=False).agg(df_agg))
        df1.rename(columns={'barcode': 'Asset_ID', 'date': 'Asset_Create_Date', 'assetdetails_value': 'Asset_Value',
                            'assetdetails_cost': 'Purchase_cost', 'capdate': 'Cap_Date',
                            'assetdetails_status': 'Assert_Status', 'enddate': 'End_Date',
                            'deprate': 'Dep_Rate'}, inplace=True)

        df2 = DepreciationTmp.objects.all().values('assetdetails', 'depreciation_fromdate', 'depreciation_todate',
                                                   'yrclosingblnce')
        df2 = pd.DataFrame(df2)
        df2.rename(columns={'assetdetails_id': 'assetdetails', 'depreciation_fromdate': 'Dep_From_Date',
                            'depreciation_todate': 'Dep_To_Date', 'yrclosingblnce': 'Dep_Yr_Closing_Balance'},
                   inplace=True)

        df3 = Depreciation.objects.all().values('id', 'depreciation_todate')
        df3 = pd.DataFrame(df3)
        print('df3', df3)
        fa_obj = ServiceCall(scope)
        df4 = fa_obj.emp_branch_list()
        df4 = pd.DataFrame(df4.data)
        df4.rename(columns={'id': 'empbranch_id', 'code': 'Branch_Code', 'name': 'Branch_Name'}, inplace=True)
        print('df4', df4)

        df5 = fa_obj.fetch_product_dep(request)
        df5 = pd.DataFrame(df5.data)
        df5.rename(columns={'id': 'empproduct_id', 'name': 'Product_Name'}, inplace=True)

        df6 = fa_obj.fetchsubcategory_dep()
        df6 = pd.DataFrame(df6.data)
        df6.rename(columns={'id': 'subcat_id', 'no': 'Sub_Cat_No', 'glno': 'Asset_GL', 'category': 'category_id'},
                   inplace=True)

        df7 = fa_obj.fetchcategory_dep()
        df7 = pd.DataFrame(df7.data)
        df7.rename(columns={'id': 'apcat_id', 'no': 'Cat_No'}, inplace=True)

        df8 = AssetCat.objects.all().values('id', 'subcategory_id', 'deptype', 'depgl_mgmt', 'subcatname', 'lifetime', 'deprate_mgmt')
        df8 = pd.DataFrame(df8)
        df8.rename(columns={'id': 'empassetcat_id', 'deptype': 'Depreciation_Method', 'depgl_mgmt': 'Dep_GL',
                            'lifetime': 'Useful_Life', 'deprate_mgmt':'Asset_Mgmt_Rate'}, inplace=True)

        df9 = AssetHeaderTmp.objects.all().values('assetdetailsbarcode', 'revisedcbtot', 'astvalbeforedeptot',
                                                  'assetheader_issale', 'reviseddeptot')

        df9 = pd.DataFrame(df9)
        df9.rename(columns={'assetdetailsbarcode': 'IT/OD', 'astvalbeforedeptot': 'Asset_Val_Before_Dep',
                            'revisedcbtot': 'Closing_Balance'}, inplace=True)
        print(df9)
        df10 = Asset_update.objects.all().values('asset_details_id', 'status', 'condition','barcode')
        df10 = pd.DataFrame(df10)
        df10.rename(columns={'status': 'Is_asset_Phyiscal_Available',
                             'condition': 'Is_asset_in_good_condition',
                            'asset_details_id': 'asset_gid','barcode':'barcode_a'}, inplace=True)
        QUERY_TIME_D = datetime.now()
        QUERY_TIME = QUERY_TIME_D.strftime("%d/%m/%Y %H:%M:%S")
        logger.info('QUERY_GENERATED - ' + QUERY_TIME)

        reportUtil = ReportFAR(scope)
        DATA7 = reportUtil.mergeDataframe(df1,df2,df3,df4,df5,df6,df7,df8,df9,df10)
        if df1.empty:
            arr = []
            return arr
        else:
            # table merge
            # Product_DATA = pd.merge(df1, df5, how='inner', left_on=['product_id'], right_on=['empproduct_id'])
            # Branch_DATA = pd.merge(Product_DATA, df4, how='inner', left_on=['branch_id'], right_on=['empbranch_id'])
            # assetCat_DATA = pd.merge(Branch_DATA, df8, how='inner', left_on=['assetcat_id'], right_on=['empassetcat_id'])
            # subCat_DATA = pd.merge(assetCat_DATA, df6, how='left', left_on=['subcategory_id'], right_on=['subcat_id'])
            # apCat_DATA = pd.merge(subCat_DATA, df7, how='left', left_on=['category_id'], right_on=['apcat_id'])
            #
            #
            # if df3.empty:
            #     Header_DATA = pd.merge(apCat_DATA, df9, how='left', left_on=['Asset_ID'])#, right_on=['IT/OD'])
            #     deptmp_DATA = pd.merge(Header_DATA, df2, how='left', left_on=['id'], right_on=['assetdetails'])
            #     DATA7 = pd.merge(deptmp_DATA, df10, how='left', left_on=['id'], right_on=['asset_gid'])
            # else:
            #     Depreciation_DATA = pd.merge(apCat_DATA, df3, how='left', left_on=['id'], right_on=['id'])
            #     Header_DATA = pd.merge(Depreciation_DATA, df9, how='left', left_on=['Asset_ID'])#, right_on=['IT/OD'])
            #     deptmp_DATA = pd.merge(Header_DATA, df2, how='left', left_on=['id'], right_on=['assetdetails'])
            #     DATA7 = pd.merge(deptmp_DATA, df10, how='left', left_on=['id'], right_on=['asset_gid'])
            # print(DATA7)

            if df3.empty:
                pass
            else:
                DATA7['depreciation_todate'] = pd.to_datetime(DATA7['depreciation_todate'])
                DATA7['depreciation_todate'] = DATA7['depreciation_todate'].dt.date
            DATA7['Cap_Date'] = pd.to_datetime(DATA7['Cap_Date'])
            DATA7['Cap_Date'] = DATA7['Cap_Date'].dt.date
            if df9.empty:
                pass
            else:
                DATA7['IT/OD'] = DATA7['IT/OD'].apply(lambda x: 'I' if x[6] == 'I' else 'O')

            DATA7['acc_branch_code'] = '-'

            def calculate(a, b):
                print('new', a, b)
                if a == 'WDV':
                    return 'L&B'
                elif b == 'Vehicle':
                    return 'VCH'
                else:
                    return 'F&F'

            DATA7['Class'] = ''
            DATA7["Class"] = DATA7.apply(lambda x: calculate(x["Depreciation_Method"], x["subcatname"]), axis=1)
            # DATA7['Class'] = DATA7['Dep_Type'].apply(lambda x: 'L&B' if x == 'WDV' else 'F&F')
            # DATA7['Class'] = DATA7['subcatname'].apply(lambda x: 'VCH' if 'Vehicle' in x else 'F&F')

            #print('Closing_Balance ', DATA7['Closing_Balance'])
            print('Asset_Value ', DATA7['Asset_Value'])
            print('Product_Name ', DATA7['Product_Name'])

            # DATA7['Dep_Value'] = DATA7['Closing_Balance']
            DATA7['Additions_After_Last_Dep'] = 0

            if df9.empty:
                pass
            else:
                conditions = [
                    (DATA7['Asset_Value'] == 1),
                    (DATA7['Product_Name'] == 'Land')
                ]
                values = [0, 0]
                DATA7['Dep_Value'] = np.select(conditions, values, default=DATA7['Closing_Balance'])

            # print('dep_value ',DATA7['Dep_Value'])
            # def condition(a, b, c):
            #     print('new', a, b)
            #     if a == 1:
            #         return 0
            #     elif b == 'Land':
            #         return 0
            #     else:
            #         return c
            #
            # # Applying the conditions
            # DATA7['Dep_Value'] = ''
            # DATA7["Dep_Value"] = DATA7.apply(lambda x: condition(x["Asset_Value"], x["Product_Name"], x['reviseddeptot']),
            #                                  axis=1)

            # DATA7['Dep_Value'] = DATA7['Product_Name'].apply(calculate)
            # DATA7['Dep_Value'] = DATA7['Asset_Value'].apply(lambda x: 0 if DATA7['Asset_Value'] == 1 else 0)
            # DATA7['Dep_Value'] = DATA7['Product_Name'].apply(lambda x: 0 if x == 'Land' else 2)
            # DATA7['Dep_Value'] = DATA7['Dep_Value'].apply(lambda x: DATA7['Closing_Balance'] if x == 2 else 0)

            if df9.empty:
                pass
            else:
                def sold(a):
                    print('new', a)
                    if a == 1:
                        return 'YES'
                    else:
                        return 'NO'

                DATA7['SOLD'] = ''
                DATA7['SOLD'] = DATA7.apply(lambda x: sold(x["assetheader_issale"]), axis=1)

            if df3.empty:
                pass
            else:
                def depcal(a, b, c):
                    if a == '':
                        return c
                    elif a < b:
                        return c
                    else:
                        return 0

                DATA7['Additions_After_Last_Dep'] = ''
                DATA7['Additions_After_Last_Dep'] = DATA7.apply(lambda x: depcal(x["depreciation_todate"], x['Cap_Date'],
                                                                                 x['Purchase_cost']), axis=1)
                # conditions = [
                #     (DATA7['depreciation_todate'] == ''),
                #     (DATA7['depreciation_todate'] < DATA7['Cap_Date'])
                # ]
                # values = [DATA7['Purchase_cost'], DATA7['Purchase_cost']]
                # DATA7['Additions_After_Last_Dep'] = np.select(conditions, values)
            DATA7['Removal'] = '-'

            print(DATA7)

            if df9.empty:
                dataDropFinal = DATA7.drop(columns=['id', 'assetcat_id', 'branch_id', 'product_id', 'empproduct_id',
                                                    'empbranch_id', 'empassetcat_id', 'subcategory_id',
                                                    'category_id', 'Branch_Code',
                                                    'Asset_Create_Date', 'Assert_Status'])
            else:
                dataDropFinal = DATA7.drop(columns=['id', 'assetcat_id', 'branch_id', 'product_id', 'empproduct_id',
                                                    'empbranch_id', 'empassetcat_id', 'subcategory_id', 'assetheader_issale',
                                                    'category_id','Branch_Code',
                                                    'Asset_Create_Date', 'Assert_Status'])
            IndexData = dataDropFinal.reindex(
                columns=['Asset_ID', 'Product_Name', 'Branch_Name', 'Useful_Life', 'Depreciation_Method',
                         'Asset_GL', 'Dep_GL', 'Class', 'Cat_No', 'Sub_Cat_No', 'End_Date', 'Asset_Mgmt_Rate',
                         'Cap_Date',  'Dep_Rate', 'Purchase_cost', 'Additions_After_Last_Dep', 'Removal',
                         'Dep_Yr_Closing_Balance', 'Asset_Val_Before_Dep',
                         'Dep_Value', 'Closing_Balance', 'acc_branch_code', 'SOLD','Is_asset_Phyiscal_Available',
                         'Is_asset_in_good_condition','asset_gid'])

            print('Depreciation_Excel_Data ', IndexData)
            END_TIME_D = datetime.now()
            END_TIME = END_TIME_D.strftime("%d/%m/%Y %H:%M:%S")
            logger.info('Depreciation_Excel_Generate - ' + END_TIME)

            return IndexData
