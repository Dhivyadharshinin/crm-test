from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from masterservice.controller import documenttypecontroller, couriercontroller, channelcontroller, commoditycontroller, \
      apexpensecontroller, securityguardcontroller, statezonecitycontroller, \
      minwagestatezonecontroller, holidaycontroller, customercontroller, codegencontroller, bankdetailscontroller, \
      delmatcontroller, \
      bsproductcontroller, clientcodecontroller, ccbsmappingcontroller, ccbscontroller, masterbusinesssegmentcontroller, \
      pmdbranchcontroller, financialcontroller, financialquarterscontroller, appversioncontroller, \
      questiontypecontroller, questionheadercontroller, questioncontroller, questionsubcontroller, \
      vendorclassificationprofilecontroller, questiongroup_mapping_controller, activitycontroller, \
      questiontypemappcontroller,leavegrademappingcontroller
# test
from masterservice.controller import migrationversion
from masterservice.controller import taxcontroller, taxratecontroller, subtraxcontroller, paymodecontroller, \
    bankbranchcontroller, paymodedetail, bankcontroller, uomcontroller, apcategorycontroller, apsubcategorycontroller, \
    customercategorycontroller, \
    mastercontroller, vendorutilcontroller, productcontroller, productspecificationcontroller, \
    productcategorycontroller, producttypecontroller, Hsncontroller, docgroupcontroller, masterauditcontroller, \
    apsectorcontroller, apexpensegroupcontroller,commodityproductmappingcontroller, leaveattendancemastercontroller,\
      gradecontroller

urlpatterns = [
      # contacttype
      path('contacttype', mastercontroller.contacttype, name='contacttype'),
      path('contacttype/<contacttype_id>', mastercontroller.fetch_contacttype, name='fetch_contacttype'),
      # designation
      path('designation', mastercontroller.designation, name='designation'),
      path('designation_download',mastercontroller.designation_download,name='designation_download'),
      path('designationmtom', mastercontroller.designation_mtom, name='designation'),
      path('designation/<designation_id>', mastercontroller.fetch_designation, name='fetch_designation'),
      path('pmd_branch', pmdbranchcontroller.pmd_branch_create, name='pmd_branch_create'),
      path('pmd_activate_inactivate',pmdbranchcontroller.pmd_activate_inactivate,name='pmd_activate_inactivate'),
      # country
      path('country', mastercontroller.country, name='country'),
      path('country/<country_id>', mastercontroller.fetch_country, name='fetch_country'),
      # district
      path('district', mastercontroller.district, name='district'),
      path('district_download',mastercontroller.district_download,name='district_download'),
      path('districtmtom', mastercontroller.district_mtom, name='district_mtom'),
      path('district/<district_id>', mastercontroller.fetch_district, name='fetch_district'),
      path('state_dist_city', mastercontroller.fetch_state_dist_city, name='fetch_state_dist_city'),
      path('fetch_district_state', mastercontroller.fetch_district_state, name='fetch_district_state'),
      path('fetch_district_city_state', mastercontroller.fetch_district_city_state,name='fetch_district_city_state'),
      path('district_scroll/<state_id>', mastercontroller.fetch_district_scroll,name='fetch_district_scroll'),
      # STATE
      path('state', mastercontroller.state, name='state'),
      path('state_download',mastercontroller.state_download,name='state_download'),
      path('statemtom', mastercontroller.state_mtom, name='state'),
      path('state/<state_id>', mastercontroller.fetch_state, name='fetch_state'),
      path('state_new/<state_id>', mastercontroller.fetch_state_id, name='fetch_state'),
      path('fetch_state_scroll/<country_id>', mastercontroller.fetch_state_scroll,name='fetch_state_scroll'),
      # city
      path('city', mastercontroller.city, name='city'),
      path('city_download',mastercontroller.city_download,name='city_download'),
      path('citymtom', mastercontroller.city_mtom, name='city'),
      path('city/<city_id>', mastercontroller.fetch_city, name='fetch_city'),
      path('city_scroll/<state_id>', mastercontroller.fetch_city_scroll, name='fetch_city_scroll'),
      # pincode
      path('pincode', mastercontroller.pincode, name='pincode'),
      path('pincode_download',mastercontroller.pincode_download,name='pincode_download'),
      path('pincodemtom', mastercontroller.pincode_mtom, name='pincode'),
      path('pincode/<pincode_id>', mastercontroller.fetch_pincode, name='fetch_pincode'),
      path('pincode_stateid', mastercontroller.fetch_pincode_stateid, name='fetch_pincode_stateid'),
      # MasterDocumenttype
      path('Documenttype', documenttypecontroller.Documenttype, name='creat_documenttype'),
      path('Documenttype/<doctype_id>', documenttypecontroller.fetch_doctype, name='fetch_documenttype'),
      path('search_doctype', documenttypecontroller.search_doctype, name='search_documenttype'),

      # courier MST
      path('courier', couriercontroller.courier, name='courier_creation'),
      path('courier/<courier_id>', couriercontroller.fetch_courier, name='courier_get'),
      path('search_courier', couriercontroller.search_courier, name='search_courier'),
      # channel mst
      path('channel', channelcontroller.channel, name='channel_creation'),
      path('channel/<channel_id>', channelcontroller.fetch_channel, name='channel_get'),
      path('search_channel', channelcontroller.search_channel, name='search_channel'),

      path('migrationversion', migrationversion.migration_version, name='migrationversion'),

      # docugroup
      path('documentgroup', docgroupcontroller.docugroup, name='create_documentgroup'),
      path('documentgroup/<docugroup_id>', docgroupcontroller.fetch_docugroup, name='fetch_documentgroup'),

      # product
      path('product', productcontroller.product, name='create_product'),
      path('productactiveinactive/<product_id>', productcontroller.fetch_product_data,name='fetch_product_data'),
      path('productmtom', productcontroller.product_mtom, name='create_productm2m'),
      path('product/<product_id>', productcontroller.fetch_product, name='fetch_product'),
      path('product_code/<product_code>', productcontroller.fetch_product_code, name='fetch_product_code'),

      path('fetch_productdata/<product_id>', productcontroller.fetch_productdata, name='fetch_productdata'),
      path('product_get', productcontroller.product_get, name='product_get'),
      path('get_product_download', productcontroller.get_product_download, name='get_product_download'),
      path('search_productcode/<product_code>', productcontroller.search_productcode,name='search_productcode'),
      path('productsearch', productcontroller.productsearch, name='productsearch'),
      path('search_productname', productcontroller.search_productname, name='search_productname'),
      path('product_name', productcontroller.product_name, name='product_name'),
      path('producttype_list/<productcategory_id>', productcontroller.producttype_list,name='producttype_list'),
      path('productcat_list', productcontroller.productcat_list, name='productcat_list'),
      path('product_cat_type/<product_category_id>/<product_type_id>', productcontroller.product_cat_type,name='product_cat_type'),
      path('pdtcat_name', productcontroller.pdtcat_name, name='pdtcat_name'),
      path('producttype_name/<product_category_id>', productcontroller.producttype_name,name='producttype_name'),
      path('get_productcode', productcontroller.get_productcode, name='get_productcode'),
      path('fetch_productcode', productcontroller.fetch_productcode, name='get_productcode'),
      path('fetch_commoditycode', commoditycontroller.fetch_commoditycode, name='fetch_commoditycode'),
      path('productclassification', productcontroller.productclassification_resp,name='productclassification'),
      path('productclassification/<number>', productcontroller.get_product_classification,name='productclassification'),
      path('productcat/<product_cat_id>', productcontroller.get_product_classification_cat,name='productcat'),
      # productspecification
      path('productspecificationmtom', productspecificationcontroller.productspecification,name='create_productspecification'),
      path('productspecification_data/<number>', productspecificationcontroller.productspecification_data,name='productspecification_data'),
      # vendor_util
      path('type', vendorutilcontroller.fetch_type_list, name='type'),
      path('org_type', vendorutilcontroller.fetch_org_type_list, name='org_type'),
      path('group', vendorutilcontroller.fetch_group_list, name='group'),
      path('classification', vendorutilcontroller.fetch_classification_list, name='classification'),
      path('composite', vendorutilcontroller.fetch_composite_list, name='composite'),


      # MasterAudit
      path('masteraudit', masterauditcontroller.masteraudit, name='creat_masteraudit'),
      path('fetch_masteraudit/<masteraudit_id>', masterauditcontroller.fetch_masteraudit,name='fetch_masteraudit'),

      # master - tax
      path('tax', taxcontroller.tax, name='tax'),
      path('taxmtom', taxcontroller.tax_mtom, name='tax_mtom'),
      path('tax/<tax_id>', taxcontroller.fetch_tax, name='fetch_tax'),
      path('newtaxsummary', taxcontroller.newtaxsummary, name='newtaxsummary'),
      path('taxname', taxcontroller.taxname, name='taxname'),
      path('subtaxname/<tax_id>', taxcontroller.subtaxname, name='subtaxname'),
      path('taxratename/<subtax_id>', taxcontroller.taxratename, name='taxratename'),
      path('get_tax_download', taxcontroller.get_tax_download, name='get_tax_download'),
      path('hsn_taxrateget', Hsncontroller.hsn_taxrateget, name='hsn_taxrateget'),
      # subtax
      path('subtax', subtraxcontroller.subtax, name='subtax'),
      path('subtaxmtom', subtraxcontroller.subtax_mtom, name='subtaxmtom'),
      path('subtax/<subtax_id>', subtraxcontroller.fetch_subtax, name='fetch_subtax'),
      path('get_sub_tax_download', subtraxcontroller.get_sub_tax_download, name='get_sub_tax_download'),

      # taxrate
      path('taxrate', taxratecontroller.taxrate, name='taxrate'),
      path('taxratemtom', taxratecontroller.taxrate_mtom, name='taxrate'),
      path('taxrate/<taxrate_id>', taxratecontroller.fetch_taxrate, name='fetch_taxrate'),
      path('taxrate_inactive', taxratecontroller.taxrate_inactive, name='fetch_taxrate'),
      path('taxrate_active_inactive', taxratecontroller.taxrate_active_inactive,name='taxrate_active_inactive'),
      path('get_tax_rate_download', taxratecontroller.get_tax_rate_download,name='get_tax_rate_download'),

      # paymode
      path('paymode', paymodecontroller.paymode, name='paymode'),
      path('paymodemtom', paymodecontroller.paymode_mtom, name='paymode'),
      path('paymode/<paymode_id>', paymodecontroller.fetch_paymode, name='fetch_paymode'),
      path('paymode_name', paymodecontroller.paymode_name, name='paymode_name'),
      path('get_paymode_download', paymodecontroller.get_paymode_download, name='get_paymode_download'),

      # paymodedetail
      path('paymodedtllist', paymodedetail.paymodedtl, name='paymodedtl'),

      # bank
      path('bank', bankcontroller.bank, name='bank_creation'),
      path('bankmtom', bankcontroller.bank_mtom, name='bankm2m_creation'),
      path('bank/<bank_id>', bankcontroller.fetch_bank, name='bank_get'),
      path('get_bank_download', bankcontroller.get_bank_download, name='get_bank_download'),

      # bankbranch

      path('bankbranch', bankbranchcontroller.bankbranch, name='bankbranch_creation'),
      path('bankbranchsummary/<bank_id>', bankbranchcontroller.bankbranch_summary,name='bankbranch_summary'),
      path('bankbranchmtom', bankbranchcontroller.bankbranch_mtom, name='bankbranch_creationm2m'),
      path('bankbranch/<bankbranch_id>', bankbranchcontroller.fetch_bankbranch, name='bankbranch_get'),
      path('ifsc', bankbranchcontroller.ifsc_bankbranch, name='ifsc_bankbranch'),
      path('get_bank_branch_download', bankbranchcontroller.get_bank_branch_download, name='get_bank_branch_download'),

      # productcategory

      path('pdtcat', productcategorycontroller.create_productcat, name='createproductcat'),
      path('pdtcatmtom', productcategorycontroller.create_productcat_mtom, name='createproductcatmtom'),
      path('pdtcat/<productcat_id>', productcategorycontroller.fetch_productcat, name='fetch_productcat'),
      path('get_productcat_download', productcategorycontroller.get_productcat_download, name='get_productcat_download'),

      # producttype
      path('pdttype', producttypecontroller.create_producttype, name='createproducttype'),
      path('pdttypemtom', producttypecontroller.create_producttype_mtom, name='createproducttypem2m'),
      path('pdttype/<producttype_id>', producttypecontroller.fetch_producttype, name='fetchproducttype'),
      path('get_productype_download', producttypecontroller.get_productype_download, name='fetchproducttype'),

      # HSN
      path('hsn', Hsncontroller.create_hsn, name='createhsn'),
      path('hsnmtom', Hsncontroller.create_hsn_mtom, name='createhsn'),
      path('hsn/<hsn_id>', Hsncontroller.fetch_hsn, name='fetchhsn'),
      path('search_hsn', Hsncontroller.search_hsn, name='search_hsn'),
      path('search_hsncode', Hsncontroller.search_hsncode, name='search_hsncode'),
      path('fetch_hsn/<hsn_id>', Hsncontroller.fetch_hsndata, name='fetch_hsndata'),
      path('hsnid/<hsn_id>', Hsncontroller.hsn_get_iddata, name='fetchhsn'),
      path('hsn_taxrateget', Hsncontroller.hsn_taxrateget, name='hsn_taxrateget'),
      path('hsn_activate_inactivate', Hsncontroller.hsn_activate_inactivate,name='hsn_activate_inactivate'),
      path('get_hsn_download', Hsncontroller.get_hsn_download,name='get_hsn_download'),

      # uom
      path('uom', uomcontroller.uom, name='uom'),
      path('uommtom', uomcontroller.uom_mtom, name='uomm2m'),
      path('uom/<uom_id>', uomcontroller.fetch_uom, name='fetch_uom'),
      path('fetch_uomdata/<uom_id>', uomcontroller.fetch_uomdata, name='fetch_uomdata'),
      path('get_uom_download', uomcontroller.get_uom_download, name='get_uom_download'),
      # apcategory

      path('Apcategory', apcategorycontroller.Apcategory1, name='Apcategory'),
      path('Apcategorymtom', apcategorycontroller.Apcategory_mtom, name='Apcategorymtom'),
      path('Apcategory/<category_id>', apcategorycontroller.fetch_category, name='fetch_category'),
      path('Apcategory_search', apcategorycontroller.Apcategory_search, name='Apcategory_search'),
      path('Apcategory_search_fa', apcategorycontroller.Apcategory_search_fa, name='Apcategory_search'),
      path('get_apcategory_download', apcategorycontroller.get_apcategory_download, name='get_apcategory_download'),
      ##new apcat common API
      path('apcategorycommon', apsubcategorycontroller.get_apcategory, name='Apcategorycommon'),
      path('apsubcategorycommon', apcategorycontroller.get_apsubcategory, name='Apsubcategorycommon'),
      path('apsubcategorycommon_data', apcategorycontroller.get_apsubcategory_data,name='Apsubcategorycommon_data'),
      path('fetch_apcategorydata/<category_id>', apsubcategorycontroller.fetch_apcategorydata,name='fetch_apcategorydata'),

      path('categorystatus/<category_id>', apcategorycontroller.updateStatus, name='updateStatus'),
      path('updateisasset', apcategorycontroller.updateisasset, name='updateisasset'),
      path('categorysearch', apcategorycontroller.categorysearch, name='categorysearch_list'),
      path('categorysearch_mst', apcategorycontroller.categorysearch_mst, name='categorysearch_list_mst'),
      path('categorylist', apcategorycontroller.categorylist, name='categorylist'),
      path('categorylistinactive', apcategorycontroller.categorylistinactive, name='categorylistinactive'),
      path('categorylistactive', apcategorycontroller.categorylistactive, name='categorylistactive'),
      path('categorytype', apcategorycontroller.categorytype, name='categorytype'),
      path('categoryname_search', apcategorycontroller.categoryname_search, name='categoryname_search'),
      path('category_income', apcategorycontroller.category_income, name='category_income'),
      path('apcategory_active_inactivate', apcategorycontroller.apcategory_active_inactivate,name='apcategory_active_inactivate'),
      path('Apcat_search', apcategorycontroller.Apcat_search, name='Apcat_search'),
      # sub apcategory
      path('Apsubcategory', apsubcategorycontroller.Apsubcategory, name='Apsubcategory'),
      path('Apsubcategorymtom', apsubcategorycontroller.Apsubcategory_mtom, name='Apsubcategorymtom'),
      path('Apsubcategory/<subcategory_id>', apsubcategorycontroller.fetch_subcategory,name='fetch_subcategory'),
      path('Apsubcategory_search', apsubcategorycontroller.apsubcategory_search, name='Apsubcategory'),
      path('apsubcategory_active_inactivate', apsubcategorycontroller.apsubcategory_active_inactivate,name='apsubcategory_active_inactivate'),

      path('subcategorystatus/<subcategory_id>', apsubcategorycontroller.updatestatus, name='updatestatus'),
      path('subcategorylist', apsubcategorycontroller.subcategorylist, name='subcategorylist'),
      path('subcategorylistactive', apsubcategorycontroller.subcategorylistactive,name='subcategorylistactive'),
      path('subcategorylistinactive', apsubcategorycontroller.subcategorylistinactive,name='subcategorylistinactive'),
      path('editsubcategory', apsubcategorycontroller.editsubcategory, name='editsubcategory'),
      path('subcategorysearch', apsubcategorycontroller.subcategorysearch, name='subcategorysearch'),
      path('subcategorysearch_mst', apsubcategorycontroller.subcategorysearch_mst, name='subcategorysearch_mst'),
      path('search_subcategoryname', apsubcategorycontroller.search_subcategoryname,name='search_subcategoryname'),

      path('Apsubcat_search', apsubcategorycontroller.apsubcat_search, name='Apsubcat_search'),

      path('catsubsearch_credit', apsubcategorycontroller.catsubsearch_credit, name='catsubsearch_credit'),
      path('catsubsearch_debit', apsubcategorycontroller.catsubsearch_debit, name='catsubsearch_debit'),
      path('subcatname_search', apsubcategorycontroller.subcatname_search, name='subcatname_search'),
      path('fetch_subcat_gl_list', apsubcategorycontroller.fetch_subcat_gl_list, name='fetch_subcat_gl_list'),
      path('get_apsubcategory_download', apsubcategorycontroller.get_apsubcategory_download, name='get_apsubcategory_download'),

      # customercategory
      path('customercategory', customercategorycontroller.customercategory, name='customercategory'),
      path('customercategory/<customercategory_id>', customercategorycontroller.fetch_customercategory,name='fetch_customercategory'),
      path('customercategory_search', customercategorycontroller.customercategory_search,name='customercategory_search'),
      # address search
      path('district_search', mastercontroller.district_search, name='district_search'),
      path('state_search', mastercontroller.state_search, name='state_search'),
      path('city_search', mastercontroller.city_search, name='city_search'),
      path('city_search_new', mastercontroller.city_search_new, name='city_search'),
      path('new_city_search', mastercontroller.new_city_search, name='new_city_search'),
      path('pincode_search', mastercontroller.get_pincode_searchlist, name='pincode_search'),
      path('pincodesearch', mastercontroller.get_pincode_searchlist, name='get_pincode_searchlist'),
      path('codegenerator', codegencontroller.codegenerator_list, name='get_codegenerator_list'),

      # contact search
      path('contacttype_search', mastercontroller.contacttype_search, name='contacttype'),
      path('designation_search', mastercontroller.designation_search, name='designation'),
      # tax search
      path('tax_search', taxcontroller.tax_search, name='tax_search'),
      path('subtax_search', subtraxcontroller.subtax_search, name='subtax_search'),
      path('tds_subtax_search', subtraxcontroller.tds_subtax_search, name='tds_subtax_search'),
      path('taxrate_search', taxratecontroller.taxrate_search, name='taxrate_search'),
      # bank
      path('paymode_search', paymodecontroller.paymode_search, name='paymode_search'),
      path('bank_search', bankcontroller.bank_search, name='bank_creation_search'),
      path('bankbranch_search', bankbranchcontroller.bankbranch_search, name='bankbranch_search'),
      # product search
      path('product_search', productcontroller.product_search, name='product_search'),
      path('hsn_data', productcontroller.get_hsn, name='hsn'),
      # uom_search
      path('uom_search', uomcontroller.uom_search, name='uom_search'),
      # productcategory_search
      path('productcat_search', productcategorycontroller.productcat_search, name='producttype_search'),
      # Producttype_search
      path('producttype_search', producttypecontroller.producttype_search, name='producttype_search'),
      # documentgroup_search
      path('documentgroup_search', docgroupcontroller.documentgroup_search, name='documentgroup_search'),

      # commodity
      path('commodity', commoditycontroller.create_commodity, name='commodity'),
      path('commodity_download', commoditycontroller.commodity_download, name='commodity_download'),
      path('commoditymtom', commoditycontroller.create_commodity_mtom, name='create_commodity_mtom'),
      path('commodity/<commodity_id>', commoditycontroller.fetch_commodity, name='fetch_commodity'),
      path('commoditysearch', commoditycontroller.commoditysearch, name='commoditysearch'),
      path('commoditystatus/<commodity_id>', commoditycontroller.update_commodityStatus,name='update_commodityStatus'),
      path('fetch_commoditydata_delmat/<commodity_id>', commoditycontroller.fetch_commoditydata_delmat,name='fetch_commoditydata_delmat'),

      path('commodity_get', commoditycontroller.commodity_get, name='commodity_get'),
      path('fetch_commoditydata/<commodity_id>', commoditycontroller.fetch_commoditydata,name='fetch_commoditydata'),
      path('commodity_name', commoditycontroller.commodity_name, name='commodity_name'),
      path('searchcommodity', commoditycontroller.searchcommodity, name='searchcommodity'),
      path('search_commoditycode/<commodity_code>', commoditycontroller.search_commoditycode,name='search_commoditycode'),
      path('search_commodityname', commoditycontroller.search_commodityname, name='search_commodityname'),
      path('get_commoditycode', commoditycontroller.get_commoditycode, name='get_commoditycode'),
      #commodityproductmapping
      path('cpmapping', commodityproductmappingcontroller.cpmapping, name='cpmapping'),
      path('cpmapping/<cpmap_id>', commodityproductmappingcontroller.fetch_cpmapping, name='fetch_cpmapping'),
      path('cpMap/<commodity_id>', commodityproductmappingcontroller.fetch_cpmap, name='cpMap'),
      path('commodity_productsearch/<product_id>', commodityproductmappingcontroller.commodity_productsearch, name='commodity_productsearch'),
      path('cpmapping_code', commodityproductmappingcontroller.cpmapping_code, name='cpmapping_code'),
      path('commodity_product', commodityproductmappingcontroller.commodity_product, name='commodity_product'),

      # path('cpMap/<commodity_id>', commoditycontroller.fetch_cpmap, name='cpMap'),
      # expense
      path('expense', apexpensecontroller.create_expense, name='expense'),
      path('expense/<expense_id>', apexpensecontroller.fetch_expense, name='fetch_expense'),
      path('search_expense', apexpensecontroller.search_expense, name='search_expense'),
      # Security Guard
      path('employeementcat', securityguardcontroller.create_employeementcat, name='employeementcat'),
      path('deleteemployeementcat/<employeecat_id>', securityguardcontroller.delete_employeementcat,name='delete_employeementcat'),
      path('employeetype', securityguardcontroller.create_employeementtypecat, name='employeetype'),
      path('statezonecity', statezonecitycontroller.create_statezonecity, name='statezonecity'),
      path('statezone_mapping', statezonecitycontroller.create_stateandzone, name='stateandzone'),
      path('minwage', minwagestatezonecontroller.create_minwage, name='minwage'),
      path('holidaymst', holidaycontroller.create_holiday, name='holiday'),

      path('get_employeecat', securityguardcontroller.get_employee_catgory, name='employeementcat'),
      path('get_employeetype', securityguardcontroller.get_employee_type, name='employeementcat'),
      path('get_employeetype_name', securityguardcontroller.fetch_employee_type_name,name='employeementcat'),
      path('get_statezone', securityguardcontroller.get_state_zone, name='employeementcat'),
      path('get_statezone_mapping', securityguardcontroller.get_state_zone_mapping, name='employeementcat'),

      # security Guard dropdown
      path('searchemployeecatdesc', securityguardcontroller.search_empcatdesc,name='searchemployeecatdesc'),
      path('statezonesearch', statezonecitycontroller.search_statezone, name='statezonesearch'),
      path('zonetype', statezonecitycontroller.zonetype, name='zonetype'),
      # Apsector
      path('sector', apsectorcontroller.Apsector, name='sector'),
      path('sector_search', apsectorcontroller.sector_search, name='sector_search'),
      path('apsector_activate_inactivate', apsectorcontroller.apsector_activate_inactivate,name='apsector_activate_inactivate'),
      path('apexpense_activate_inactivate', apexpensegroupcontroller.apexpense_activate_inactivate,name='apexpensector_activate_inactivate'),
      # ApExpenseGroup
      path('expensegrp', apexpensegroupcontroller.ApExpenseGroup, name='expensegrp'),
      path('expensegrp_search', apexpensegroupcontroller.expensegrp_search, name='sector_search'),
      # microtomicro
      path('get_city/<city_id>', mastercontroller.fetch_city, name='get_city'),
      path('get_pincode/<pincode_id>/<city_id>', mastercontroller.fetch_pincode, name='get_pincode'),
      path('get_state/<state_id>', mastercontroller.fetch_state, name='get_state'),

      # microtomicro
      path('get_commodity/<commodity_id>', commoditycontroller.fetch_commoditys, name='get_commodity'),
      path('get_commoditylist', commoditycontroller.fetch_commoditylist, name='fetch_commoditylist'),
      path('get_state/<state_id>', mastercontroller.fetch_stateone, name='get_state'),
      path('get_statelist', mastercontroller.fetch_statelist, name='fetch_statelist'),
      path('get_product/<product_code>', productcontroller.fetch_productone, name='fetch_product'),
      path('get_productlist', productcontroller.fetch_productlistget, name='fetch_productlist'),
      path('get_apcategory', apsubcategorycontroller.fetch_apcategory1, name='fetch_apcategory'),
      path('get_apcategorylist', apsubcategorycontroller.fetch_apcategorylist, name='fetch_apcategorylist'),
      path('get_apsubcategory', apsubcategorycontroller.fetch_apsubcategory, name='fetch_apsubcategory'),
      path('get_apsubcategorylist', apsubcategorycontroller.fetch_apsubcategorylist,name='fetch_apsubcategorylist'),
      path('get_bank/<bank_id>', bankcontroller.fetch_bankone, name='fetch_bank'),
      path('get_banklist', bankcontroller.fetch_banklist, name='fetch_banklist'),
      path('get_paymode/<paymode_id>', paymodecontroller.fetch_paymodeone, name='fetch_paymode'),
      path('get_paymodelist', paymodecontroller.fetch_paymodelist, name='fetch_paymodelist'),
      path('get_hsn', Hsncontroller.fetch_hsnone, name='fetch_hsnone'),
      path('get_hsn_ta', Hsncontroller.fetch_hsnone_ta, name='fetch_hsnone_ta'),
      # supplierbranch_payment
      path('supplierbranch_payment/<supplierbranch_id>', paymodecontroller.supplierbranch_payment,name='supplier_payment'),

      path('paymodecreditgl/<pay_id>', paymodedetail.getcreditgl, name='getcreditgl'),
      path('paymodedetail_create', paymodedetail.paymodedetail_create, name='paymodedetail_create'),
      path('paymodedetails_active_inactive', paymodedetail.paymodedetails_active_inactive,name='paymodedetails_active_inactive'),

      # customer
      path('customer', customercontroller.create_customer, name='get_customer'),
      # ecf
      path('get_subtax', subtraxcontroller.fetch_subtaxlist, name='fetch_subtaxlist'),
      path('get_taxrate', taxratecontroller.fetch_taxratelist, name='fetch_taxratelist'),

      # TA

      path('state_id/<city_name>', customercontroller.ta_state_id, name='ta_state_id'),
      path('category_id/<id>', customercontroller.ta_category_id, name='category_id'),
      path('subcategory_id/<id>', customercontroller.ta_subcategory_id, name='subcategory_id'),
      path('category_no_get/<id>', customercontroller.category_no_get, name='category_no_get'),
      path('subcategory_no_get/<no>/no/<id>', customercontroller.subcategory_no_get,name='subcategory_no_get'),

      # inward

      path('state_id/<city_name>', customercontroller.ta_state_id, name='ta_state_id'),
      path('category_id/<id>', customercontroller.ta_category_id, name='category_id'),
      path('subcategory_id/<id>', customercontroller.ta_subcategory_id, name='subcategory_id'),
      path('category_no_get/<id>', customercontroller.category_no_get, name='category_no_get'),
      path('subcategory_no_get/<no>/no/<id>', customercontroller.subcategory_no_get,name='subcategory_no_get'),

      # ccbs mapping
      path('searchbusinesssegment', ccbsmappingcontroller.searchbusinesssegment,name='searchbusinesssegment'),
      path('ccbsmapping', ccbsmappingcontroller.ccbsmapping, name='ccbsmapping'),
      path('ccbsmapping_download', ccbsmappingcontroller.ccbsmapping_download, name='ccbsmapping_download'),
      path('ccbsmapping/<ccbsmapping_id>', ccbsmappingcontroller.fetch_ccbsmapping, name='ccbsmapping_get'),
      path('search_ccbs', ccbsmappingcontroller.search_ccbs, name='search_ccbs'),
      path('listactive', ccbsmappingcontroller.listactive, name='listactive'),
      path('listinactive', ccbsmappingcontroller.listinactive, name='listinactive'),
      path('searchbs_cc', ccbsmappingcontroller.searchbs_cc, name='searchbs_cc'),
      # cost centre
      path('costcentre', ccbscontroller.costcentre, name='costcentre'),
      path('costcentremtom', ccbscontroller.costcentre_mtom, name='costcentre'),
      path('costcentre/<costcentre_id>', ccbscontroller.fetch_costcentre, name='costcentre_get'),
      path('costcentrelist', ccbscontroller.costcentrelist, name='costcentrelist'),
      path('costcentre_download',ccbscontroller.costcentre_download,name='costcentre_download'),
      path('cclistactive', ccbscontroller.cclistactive, name='cclistactive'),
      path('cclistinactive', ccbscontroller.cclistinactive, name='cclistinactive'),
      path('costcentrestatus/<costcentre_id>', ccbscontroller.updateccstatus, name='updateStatus'),
      path('costcentresearch', ccbscontroller.costcentresearch, name='costcentresearch'),
      path('costcentresearch_overall', ccbscontroller.costcentresearch_overall, name='costcentresearch'),
      path('costcentresearch_overall_mst', ccbscontroller.costcentresearch_overall_mst, name='costcentresearch_mst'),
      # business segment
      path('businesssegment', ccbscontroller.businesssegment, name='businesssegment'),
      path('businesssegmentmtom', ccbscontroller.businesssegment_mtom, name='businesssegment_mtom'),
      path('businesssegment/<businesssegment_id>', ccbscontroller.fetch_businesssegment,name='businesssegment_get'),
      path('bs_name_list', ccbscontroller.bs_name_get, name='bs_name_list_get'),
      path('bs_activate_inactivate', ccbscontroller.bs_activate_inactivate, name='bs_activate_inactivate'),
      path('cc_activate_inactivate', ccbscontroller.cc_activate_inactivate, name='cc_activate_inactivate'),
      path('create_masterbusinesssegment', ccbscontroller.create_masterbusinesssegment,name='cc_activate_inactivate'),
      path('apsectorname_get', ccbscontroller.apsectorname_get, name='apsectorname_get'),
      path('masterbusinesssegment', ccbscontroller.mastersegmentname, name='mastersegmentname'),
      # new common API
      # path('businesssegmentcommon', ccbscontroller.get_business, name='businesssegmentcommon_get'),
      # path('costcentrecommon', ccbscontroller.get_costcentre, name='costcentrecommon_get'),
      path('businesssegmentlist', ccbscontroller.businesssegmentlist, name='businesssegmentlist'),
      path('businesssegment_download',ccbscontroller.businesssegment_download,name='businesssegment_download'),
      path('bslistactive', ccbscontroller.bslistactive, name='bslistactive'),
      path('bslistinactive', ccbscontroller.bslistinactive, name='bslistinactive'),
      path('businesssegmentstatus/<businesssegment_id>', ccbscontroller.updatebsstatus,name='updateStatus'),
      path('businesssegmentsearch', ccbscontroller.businesssegmentsearch, name='businesssegmentsearch'),
      path('businesssegmentsearch_mst', ccbscontroller.businesssegmentsearch_mst, name='businesssegmentsearch_mst'),
      # masterbusinessegment
      path('masterbusinesssegment', masterbusinesssegmentcontroller.master_business_segment,name='masterbusinesssegment'),
      path('masterbusinesssegment_search', masterbusinesssegmentcontroller.master_business_segment_seatch,name="masterbusinesssegment_search"),

      # Delmat
      path('delmat', delmatcontroller.create_delmat, name='delmat'),
      path('delmat_download', delmatcontroller.delmat_download, name='delmat_download'),
      path('download_file/<file_id>', delmatcontroller.download_file, name='download_file'),
      path('delmat/<delmat_id>', delmatcontroller.fetch_delmat, name='fetch_delmat'),
      path('delmattype', delmatcontroller.fetch_delmattype, name='delmattype'),
      path('listactive', delmatcontroller.listactive, name='listactive'),
      path('listinactive', delmatcontroller.listinactive, name='listinactive'),
      path('delmatsearch', delmatcontroller.delmatsearch, name='delmatsearch'),
      path('delmatsearch_mst', delmatcontroller.delmatsearch_mst, name='delmatsearch_mst'),
      path('searchpending', delmatcontroller.searchpending, name='searchpending'),
      path('searchpending_mst', delmatcontroller.searchpending_mst, name='searchpending_mst'),
      path('pending_list', delmatcontroller.pending_list, name='pending_list'),
      path('delmat_approval_download', delmatcontroller.delmat_approval_download, name='delmat_approval_download'),
      path('updateapproved', delmatcontroller.updateapproved, name='updateapproved'),
      path('updaterejected', delmatcontroller.updaterejected, name='updaterejected'),
      path('delmatstatus/<delmat_id>', delmatcontroller.updatestatus, name='updatestatus'),
      path('search_employeelimit', delmatcontroller.search_employeelimit, name='search_employeelimit'),
      path('delmat_activate_inactivate',delmatcontroller.delmat_activate_inactivate,name='delmat_activate_inactivate'),
      # delmat - mono to micro sync
      path('delmatmtom', delmatcontroller.create_delmat_mtom, name='delmatmtom'),
      path('delmatapprove_mtom', delmatcontroller.delmatapprove_mtom, name='delmatapprove_mtom'),
      path('delmatreject_mtom', delmatcontroller.delmatreject_mtom, name='delmatreject_mtom'),
      # businessproduct-clientcode-ecf
      path('create_bsproduct', bsproductcontroller.create_bsproduct, name='businessproduct_create'),
      path('create_client', clientcodecontroller.create_clientcode, name='client_creation'),
      path('clientcode_activate_inactivate',clientcodecontroller.clientcode_activate_inactivate,name='clientcode_activate_inactivate'),
      path('clientcode_download',clientcodecontroller.clientcode_download,name='clientcode_download'),
      path('rm_drop_down',clientcodecontroller.rm_drop_down,name='rm_drop_down'),
      # inward

      path('channel_summarysearch', channelcontroller.channel_summarysearch, name='channel_summarysearch'),
      path('courier_summarysearch', couriercontroller.courier_summarysearch, name='courier_summarysearch'),
      path('document_summarysearch', documenttypecontroller.document_summarysearch,name='document_summarysearch'),

      path('channel_search', channelcontroller.channel_search, name='channel_search'),
      path('courier_search', couriercontroller.courier_search, name='courier_search'),
      path('risk_type', vendorutilcontroller.fetch_risk_type, name='risk_type'),

      #finyr
      path('financial_year',financialcontroller.financial_year,name='financial_year'),
      path('finyr_activate_inactivate',financialcontroller.finyr_activate_inactivate,name='finyr_activate_inactivate'),
      #finqtr
      path('financial_quarters_year',financialquarterscontroller.financial_quarters_year,name='financial_quarters_year'),
      path('fin_quarter_yr_activate_inactivate',financialquarterscontroller.fin_quarter_yr_activate_inactivate,name='financialquarterscontroller'),
      # bank_details
      # path('bankbranch_new',bankbranchcontroller.bankbranch_new,name='bankbranch_new'),
      path('bankdetails', bankdetailscontroller.bank_details, name='bank_details_creation'),
      path('bankdetails/<bankdetails_id>', bankdetailscontroller.fetch_bankdetails, name='bankdtls_get'),

      # risk type
      path('risktype', vendorutilcontroller.create_risk_type, name='risk_type'),
      path('risktype_download', vendorutilcontroller.risktype_download, name='risktype_download'),
      path('risktype/<risk_id>', vendorutilcontroller.fetch_risktype, name='risktype_get'),
      #ta
      path('category_get_ta', customercontroller.ta_get_catgory, name='category_get_ta'),
      path('sub_category_get_ta', customercontroller.ta_get_subcatgory, name='sub_category_get_ta'),
      path('commodity_ta', customercontroller.commodity_ta, name='commodity_ta'),

      #App Version
      path('appversion', appversioncontroller.version, name='appversion'),
      # path('appschemadropdown', appversioncontroller.fetch_Schema_Dropdown, name='appschemadropdown'),
      path('appversion_server/<entity_id>', appversioncontroller.fetch_version_server, name='appversion_server'),
      path('appversionactiveinactive', appversioncontroller.appversion_activate_inactivate, name='appversionactiveinactive'),
      path('create_subcat_code_gen', codegencontroller.create_subcat_code_gen, name='create_subcat_code_gen'),
      path('composite_search', vendorutilcontroller.search_composite, name='composite_search'),
      path('org_type_search', vendorutilcontroller.search_org_type_list, name='org_type'),


      #QUESTIONTYPE
      path('question_type', questiontypecontroller.create_question_type, name='question_type'),
      path('question_type/<id>', questiontypecontroller.get_question_type, name='question_type'),
      #questionheader
      path('questionheader', questionheadercontroller.create_question_header, name='question_header'),
      path('questionheader/<id>', questionheadercontroller.get_question_header, name='question_header'),

      #question
      path('question', questioncontroller.create_question, name='question'),
      path('question_typeget/type_id', questioncontroller.question_typeget, name='question'),
      path('question/<id>', questioncontroller.get_question, name='question'),
      #get_api_for_question_and_question_sub
      path('question/<question_id>/ques_subquestion_get', questioncontroller.get_question_sub_question,name='question'),
      #questionsuboption
      path('questionsuboptions', questionsubcontroller.create_questionsub_options, name='questionsuboptions'),
      path('questionsuboptions/<id>', questionsubcontroller.get_questionsub_options, name='questionsuboptions'),

      #question_type_and_question_header_search
      path('type_base_headername', questionheadercontroller.type_base_headername, name='questiontype'),

      #vendorclassficationprofile
      path('vendorclassfication_create', vendorclassificationprofilecontroller.vendorclassfication_create, name='vendorclassfication'),
      path('get_vendorclassficationtype', vendorclassificationprofilecontroller.get_vendorclassficationtype, name='vendorclassfication'),
      path('get_vendorclassfication/<id>',vendorclassificationprofilecontroller.get_vendorclassfication,name='vendorclassfication'),
      path('period_drop_down', vendorclassificationprofilecontroller.period_drop_down, name='period_drop_down'),
      path('period_drop_down/<type_id>', vendorclassificationprofilecontroller.period_drop_downget, name='period_drop_down'),
      path('process_drop_down', vendorclassificationprofilecontroller.process_drop_down, name='process_drop_down'),
      path('questiontype_by_vendorcat',vendorclassificationprofilecontroller.questiontype_by_vendorcat,name='questiontype_by_vendorcat'),

      #input_type_drop_down
      path('input_type_drop_down', questiontypecontroller.input_type_drop_down, name='input_type_drop_down'),

      #type_id_based_record
      path('question_type_info/<type_id>',questiontypecontroller.question_type_info,name='question_type_info'),
      path('cmsquestion_type/<pro_id>',questiongroup_mapping_controller.fetch_questype,name='question_type_info'),
      path('vowwquestion_type/<pro_id>',questiongroup_mapping_controller.vow_fetch_projansw,name='question_type_info'),

      #header_based_question
      path('header_based_question/<id>', questionheadercontroller.header_based_question, name='question_header'),

      path('question_group_mapping/<type_id>', questiongroup_mapping_controller.question_group_mapping, name='question_header'),

      # master data for vow
      path('master_table_data', vendorutilcontroller.get_masters_data, name='master data'),
      path('master_table_data_list', vendorutilcontroller.get_masters_data_list, name='master data list'),
      path('master_drop_down', vendorutilcontroller.masters_drop_down, name='master dropdown'),
      #activity_create
      path('activity', activitycontroller.create_activity, name='create_activity'),
      path('get_activity/<id>', activitycontroller.get_activity, name='get_activity'),

      #questiontype_mapping
      path('create_questiontype_mapping', questiontypemappcontroller.create_questiontype_mapping, name='question_type_mapping'),
      path('get_questiontype_mapping/<id>', questiontypemappcontroller.get_questiontype_mapping, name='question_type_mapping'),
      path('questiontype_mapping_is_checked', questiontypemappcontroller.questiontype_mapping_is_checked, name='question_type_mapping'),
      path('create_flagmaster', questiontypemappcontroller.create_flagmaster, name='flagmaster'),
      path('get_flagmaster/<id>', questiontypemappcontroller.get_flagmaster, name='flagmaster'),

      # leave and attendance
      path('org_ip', leaveattendancemastercontroller.org_ip, name='Org IP'),
      path('org_ip/<org_id>', leaveattendancemastercontroller.fetch_ip_org, name='Get Org IP'),
      path('org_details_ip/<org_id>', leaveattendancemastercontroller.fetch_org_detail_ips, name='Org IPS'),
      path('org_details', leaveattendancemastercontroller.org_details, name='Org Details'),
      path('org_details/<detail_id>', leaveattendancemastercontroller.fetch_org_details, name='Get Org Details'),
      path('org_details/<org_id>/org_arc', leaveattendancemastercontroller.org_arc_details, name = 'orgdetailsarc'),
      path('attendance', leaveattendancemastercontroller.attendance, name='Attendance'),
      path('attendance/<attendance_id>', leaveattendancemastercontroller.fetch_attendance, name='Get Attendance'),
      path('leave_type', leaveattendancemastercontroller.leave_type, name='Leave Type'),
      path('leave_type/<type_id>', leaveattendancemastercontroller.fetch_leave_type, name='Get Leave Type'),
      path('holiday', leaveattendancemastercontroller.holiday, name='Holiday'),
      path('holiday/<holiday_id>', leaveattendancemastercontroller.fetch_holiday, name='Get Holiday'),


      # # Master service1
      path('grade',gradecontroller.create_grade, name=' work'),
      path('search/<name>', gradecontroller.search_grade, name=' search'),
      path('grade/<id>', gradecontroller.fetch_grade, name=' get'),
      path('grademapping', gradecontroller.create_designationgrademapping, name=' get'),
      path('grademapping/<id>', gradecontroller.del_designationgrademapping, name=' get'),
      #  grade leavetype mapping
      path('grade_leave_mapping', leavegrademappingcontroller.grade_leave_mapping, name='leavegrademappingcontroller'),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
