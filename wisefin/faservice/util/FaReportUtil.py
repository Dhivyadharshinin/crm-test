import pandas as pd

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class ReportFAR(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
    def mergeDataframe(self,df1,df2,df3,df4,df5,df6,df7,df8,df9,df10):
        # empty_table = []
        # if df1.empty:
        #     empty_table.append('df1')
        # if df2.empty:
        #     empty_table.append('df2')
        # if df3.empty:
        #     empty_table.append('df3')
        # if df4.empty:
        #     empty_table.append('df4')
        # if df5.empty:
        #     empty_table.append('df5')
        # if df6.empty:
        #     empty_table.append('df6')
        # if df7.empty:
        #     empty_table.append('df7')
        # if df8.empty:
        #     empty_table.append('df8')
        # if df9.empty:
        #     empty_table.append('df9')
        # if df10.empty:
        #     empty_table.append('df10')
        # print(empty_table)
        # dataframe = []
        # for j in empty_table:
        #     if j == 'df1':
        #         dataframe.append({'data': df1})
        #     if j == 'df2':
        #         dataframe.append({'data': df2})
        #     if j == 'df3':
        #         dataframe.append({'data': df3})
        #     if j == 'df4':
        #         dataframe.append({'data': df4})
        #     if j == 'df5':
        #         dataframe.append({'data': df5})
        #     if j == 'df6':
        #         dataframe.append({'data': df6})
        #     if j == 'df7':
        #         dataframe.append({'data': df7})
        #     if j == 'df8':
        #         dataframe.append({'data': df8})
        #     if j == 'df9':
        #         dataframe.append({'data': df9})
        #     if j == 'df10':
        #         dataframe.append({'data': df10})

        if df1.empty:
            DATA7 = pd.DataFrame()
            return DATA7
        if df5.empty:
            pass
        else:
            DATA = pd.merge(df1, df5, how='inner', left_on=['product_id'], right_on=['empproduct_id']) #Product_DATA
        if df4.empty:
            pass
        else:
            DATA = pd.merge(DATA, df4, how='inner', left_on=['branch_id'], right_on=['empbranch_id']) #Branch_DATA
        if df8.empty:
            pass
        else:
            DATA = pd.merge(DATA, df8, how='inner', left_on=['assetcat_id'], #assetCat_DATA
                                     right_on=['empassetcat_id'])
        if df6.empty:
            pass
        else:
            DATA = pd.merge(DATA, df6, how='left', left_on=['subcategory_id'], right_on=['subcat_id']) #subCat_DATA
        if df7.empty:
            pass
        else:
            DATA = pd.merge(DATA, df7, how='left', left_on=['category_id'], right_on=['apcat_id']) #apCat_DATA
        if df3.empty:
            pass
        else:
            DATA = pd.merge(DATA, df3, how='left', left_on=['id'], right_on=['id']) #Depreciation_DATA
        if df9.empty:
            pass
        else:
            DATA = pd.merge(DATA, df9, how='left', left_on=['Asset_ID'],right_on=['IT/OD']) #Header_DATA
        if df2.empty:
            pass
        else:
            DATA = pd.merge(DATA, df2, how='left', left_on=['id'], right_on=['assetdetails']) #deptmp_DATA
        if df10.empty:
            pass
        else:
            DATA = pd.merge(DATA, df10, how='left', left_on=['id'], right_on=['asset_gid'])

        return DATA