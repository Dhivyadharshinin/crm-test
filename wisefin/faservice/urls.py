from django.conf import settings
from django.urls import path

from django.conf.urls.static import static


from faservice.controller import assetcatcontroller, depreciationsettingcontroller, assetlocationcontroller, \
    assetdetailscontroller, assetsalecontroller, depreciationcontroller, \
    categorychangecontroller, splitcontroller, mergecontroller, assetentrycontroller, cwipgroupcontroller, \
    clearingdetailscontroller, clearingheadercontroller, assetdebitcontroller, assetdetailscontroller, \
    assetgroupcontroller, assetidcontroller, assetvaluechangecontroller, assettransfercontroller, writeoffcontroller, \
    cgumastercontroller, impaircontroller, assetupdatecontroller, reportdepreciationcontroller,assetheadercontroller

from faservice.util.FaApiService import ServiceCall


urlpatterns = [
    # pv screens dec
    path('assetdetails', assetdetailscontroller.create_assetdetails, name='assetdetails'),
    # path('assetdetails_pv', assetdetailscontroller.assetdetails_pv, name='assetdetails'),
    path('assetdetails_id', assetdetailscontroller.fetch_asset_id, name='assetdetails_id'),
    path('assetupdate', assetupdatecontroller.assetupdate, name='details'),
    path('assetupdate1', assetupdatecontroller.assetupdate1, name='details_image'),
    path('approver', assetupdatecontroller.approver, name='approver'),
    path('approver_save', assetupdatecontroller.approver_save, name='approver_save'),
    path('approver_branch', assetupdatecontroller.branchupdate1, name='approver_branch'),
    path('approver_full', assetupdatecontroller.fullapproverupdate1, name='approver_full'),
    path('filter_records', assetdetailscontroller.filter_records, name='filter_records'),
    path('branchfilter', assetupdatecontroller.branchfilter, name='branchfilter'),
    path('branchupdate', assetupdatecontroller.branchupdate, name='branchupdate'),
    path('branchfile_download', assetupdatecontroller.branchfile_download, name='branchfile_download'),
    path('fullfile_download', assetupdatecontroller.fullfile_download, name='fullfile_download'),
    path('assetedit_records', assetdetailscontroller.asset_edit_records, name='assetedit_records'),
    # path('file_upload', assetupdatecontroller.file_upload, name='file_upload'),
    path('add_row', assetupdatecontroller.add_row, name='add_row'),
    path('add_row1', assetupdatecontroller.add_row1, name='add_row1'),
    path('update_pv', assetupdatecontroller.update_pv, name='update_pv'),
    path('update_pv1', assetupdatecontroller.update_pv1, name='update_pv1'),
    path('fa_version', assetdetailscontroller.assetdetails, name='fa_version'),
    # path('new_record/<update_id>', assetupdatecontroller.addrow_duplicate, name='new_record'),
   #pv end
    path('assetcat', assetcatcontroller.create_assetcat, name='asset_creation'),
    path('assetcat/<assetcat_id>', assetcatcontroller.fetch_assetcat, name='assetcat_fetch'),
    path('depreciationsetting', depreciationsettingcontroller.create_depreciationsetting, name='depsetting_creation'),
    path('depreciationsetting/<depsetting_id>', depreciationsettingcontroller.fetch_depsetting, name='depsetting_fetch'),
    path('assetlocation', assetlocationcontroller.create_assetlocation, name='assetlocation_creation'),
    path('assetlocation/<assetlocation_id>', assetlocationcontroller.fetch_assetlocation, name='assetlocation_fetch'),
    path('cwipgroup', cwipgroupcontroller.create_cwipgroup, name='cwipgroup_creation'),
    path('doctype', cwipgroupcontroller.fetch_doctype_list, name='doctype_getlist'),
    path('faquery_get', assetdetailscontroller.faquery_get, name='faquery_get'),
    path('faquery_get_download', assetdetailscontroller.faquery_get_download, name='faquery_get_download'),
    path('faquery_get_source', assetdetailscontroller.faquery_source_get, name='faquery_get_source'),
    #new Query Version
    path('faquery_version', assetdetailscontroller.faquery_version, name='faquery_version'),
    path('Assetclubget', assetdetailscontroller.Assetclubget, name='Assetclubget'),
    path('getparentchild/<parentid>', assetdetailscontroller.getparentchild, name='getparentchild'),
    path('parentchildvalidation', assetdetailscontroller.parentchildvalidation, name='parentchildvalidation'),
    path('clubmakerupdate/', assetdetailscontroller.clubmakerupdate, name='clubmakerupdate'),
    path('clumbmakerparentchildget/', assetdetailscontroller.clumbmakerparentchildget, name='clumbmakerparentchildget'),
    # clearingdetails
    path('clearingdetails', clearingdetailscontroller.create_clearingdetails, name='ASSET_MAKER'),
    path('fetch_bussinesssegment', assetdetailscontroller.fetch_businesssegment_list, name='BS'),
    path('fetch_costcentre_list', assetdetailscontroller.fetch_costcentre_list, name='CC'),
    path('fetch_apcat', assetdetailscontroller.fetch_Apcat_list, name='BS'),
    path('fetch_apsubcat', assetdetailscontroller.fetch_Apsubcat_list, name='CC'),
    path('fetch_branch_list', assetdetailscontroller.fetch_branch_list, name='EMP_BRANCH'),

    # clearingheader
    path('bucketsummary',clearingheadercontroller.buc_summary,name="bucket summary"),
    path('bucketnamesearch',clearingheadercontroller.buc_summary_search,name="bucketnamesearch"),
    path('clearingheader', clearingheadercontroller.create_clearingheader, name='clearingheader_creation'),
    path('clearingheader_unlock', clearingheadercontroller.clearingheader_lock_status, name='clearingheader_unlock'),
    path('clearingheaderdetails', clearingdetailscontroller.fetch_clearingheaderdetails, name='clearingdetails'),
    path('capdatemakersummary', assetdetailscontroller.cpdatechange_makersummary, name='capdatemakersummary'),
    path('capdatesummary', assetdetailscontroller.cpdatechange_summary, name='capdatesummary'),
    path('capdatechangemake', assetdetailscontroller.cpdatechange_make, name='cpdatechange_make'),
    path('capdatechangecheck', assetdetailscontroller.cpdatechange_check, name='cpdatechange_check'),
    path('capdatechangechecksum', assetdetailscontroller.cpdatechange_checksummary, name='cpdatechange_checksummary'),

    path('clearingheader/<clearingheader_id>/clearingdetails', clearingdetailscontroller.fetch_clearingdetails_list, name='ASSET_MAKER'),
    path('movetobucket', clearingheadercontroller.clearance_movetobucket, name='clearance_movetobucket'),
    path('clearancebucket', clearingheadercontroller.create_bucket, name='createbucket'),

    path('assetcapitalization', assetdebitcontroller.create_assetdebit, name='asset_assetdebit'),
    path('create_assetdetails', assetdetailscontroller.create_assetdetails, name='asset_details'),
    path('summary_assetdetails', assetdetailscontroller.fetch_assetdetails_sum, name='asset_summary'),
    path('fetch_asset_id', assetdetailscontroller.fetch_assetid_grp, name='asset_details'),
    path('fetch_assetgroup_id', assetgroupcontroller.fetch_assetgroup_assetid, name='asset_details'),
    path('assetchecksummary', assetdetailscontroller.fetch_assetchecker_summary, name='asset_checker_summary'),
    path('assetchecker_view', assetdetailscontroller.fetch_assetchecker_view, name='asset_checker_summary'),
    path('assetchecker_view_nongrp', assetdetailscontroller.fetch_assetchecker_non, name='asset_checker_summary_non'),
    path('assetchecker_approve', assetdetailscontroller.checker_summary_approve, name='asset_checker_summary'),
    path('assetchecker_reject', assetdetailscontroller.checker_summary_reject, name='asset_checker_summary'),
    path('assetgroup', assetgroupcontroller.create_assetgroup, name='asset_assetgroup'),
    path('codegenerator', assetdetailscontroller.codegenerator, name='create_codegenerator'),
    #assetid
    path('assetid', assetidcontroller.create_assetid, name='assetid_creation'),
    path('assetid/<assetid_id>', assetidcontroller.assetid_update, name='assetid_fetch'),
    path('get_source',assetidcontroller.get_source_type,name='get_source'),

    path('depreciation',depreciationcontroller.createdepreciation,name='depreciation'),
    #report depreciation
    path('report_depreciation', reportdepreciationcontroller.reportdepreciation, name='report_depreciation'),
    path('download_forecast', reportdepreciationcontroller.downloadforecast, name='download_forecast'),
    path('temp_forecast', reportdepreciationcontroller.tempreportdepreciation, name='temp_forecast'),
    path('report_depreciation_regular', reportdepreciationcontroller.reportdepreciationregular, name='report_depreciation_regular'),
    path('download_regular', reportdepreciationcontroller.downloadregular, name='download_regular'),
    path('temp_regular', reportdepreciationcontroller.tempreportdepreciationregular, name='temp_regular'),
    path('report_far', reportdepreciationcontroller.reportdepreciationfar, name='report_far'),

    #asset_valuechange
    path('assetvaluechange',assetvaluechangecontroller.fetch_assetvaluechange_list,name='fetch_assetvaluechange_list'),
    path('valuechange',assetvaluechangecontroller.valuechange_summary,name='valuechange_summary'),#plus button summary
    path('valuechange_assetdetails',assetvaluechangecontroller.create_valuechange_assetdetails,name='create_valuechange_assetdetails'),
    path('valuechange_checker',assetvaluechangecontroller.valuechange_checkersummary,name='valuechange_checkersummary'),
    path('valuechange_approve',assetvaluechangecontroller.valuechange_approve,name='valuechange_approve'),
    path('valuechange_reject',assetvaluechangecontroller.valuechange_reject,name='valuechange_reject'),
    #AssetEntry
    path('assetdetails/<assetdetails_id>/assentry', assetentrycontroller.create_assetentry, name='assetentry'),
    path('assentry/<assetdetails_id>/ass', assetentrycontroller.create_fundservice, name='assetentry'),
    path('assent', assetentrycontroller.repost, name='repost'),
    #fasset_transfer
    path('get_assettransfer',assettransfercontroller.get_assettransfer,name='get_assettransfer'),
    path('fetch_assettransfer',assettransfercontroller.fetch_assettransfer,name='fetch_assettransfer'),#plus button summarty
    path('get_assettransferchecker', assettransfercontroller.get_assettransfer_checker, name='get_assettransfer_checker'),
    path('assettransfer',assettransfercontroller.create_assettransfer,name='assettransfer'),
    path('assettransfer_approve',assettransfercontroller.assettransfer_approve,name='assettransfer_approve'),
    #asset_checker_summary
    path('assetchecker_approve', assetdetailscontroller.checker_summary_approve, name='asset_checker_summary'),
    #categorychange
    path('categorychange',categorychangecontroller.create_categorychange,name='categorychange'),
    path('get_categorychange',categorychangecontroller.get_categorychange,name='get_categorychange'),
    path('fetch_categorychange',categorychangecontroller.fetch_categorychange,name='fetch_categorychange'),#plus button summary
    path('get_catchangechecker',categorychangecontroller.get_catchangechecker,name='fetch_catchangechecker'),
    path('catchange_approve',categorychangecontroller.catchange_approve,name='catchange_approve'),
    #Asset Sale
    path('get_assetsale',assetsalecontroller.get_assetsale,name='get_assetsale'),#plus button summary
    path('fetch_assetsale',assetsalecontroller.fetch_assetsale,name='fetch_assetsale'),
    path('assetsale',assetsalecontroller.create_assetsale,name='create_assetsale'),
    path('get_assetsalechecker',assetsalecontroller.get_assetsalechecker,name='get_assetsalechecker'),
    path('assetsaleapprove',assetsalecontroller.assetsaleapprove,name='assetsaleapprove'),
    #Sale PDF
    path('assetsale_invoicepdf/<assetsaleheader_id>',assetsalecontroller.export_fa_invoice_pdf,name='assetsale_invoicepdf'),



    #writeoff
    path('writeoff', writeoffcontroller.create_writeoff, name='writeoff'),
    path('assetdetails_get/<assetdetails_id>', writeoffcontroller.fetch_assetdetails, name='writeoff'),
    path('search_writeoff_add', writeoffcontroller.search_writeoff_add, name='search_writeoff_add'),
    path('writeoff_maker', writeoffcontroller.writeoff_maker, name='writeoff_maker'),
    path('writeoff_maker_summarysearch', writeoffcontroller.writeoff_maker_summarysearch, name='writeoff_maker_summarysearch'),

    path('writeoff_checker', writeoffcontroller.writeoff_checker, name='writeoff_checker'),
    path('writeoff_checker_search', writeoffcontroller.writeoff_checker_search, name='writeoff_checker_search'),
    path('writeoff_add', writeoffcontroller.writeoff_add, name='writeoff_add'),
    # split
    path('split_maker', splitcontroller.create_split, name='split'),
    path('split_get', splitcontroller.split_get, name='split_get'),
    path('split_maker_search', splitcontroller.split_maker_search, name='split_maker_search'),
    path('split_checker', splitcontroller.split_checker, name='split_checker'),
    path('split_checker_search', splitcontroller.split_checker_search, name='split_checker_search'),
    path('split_assetlist', splitcontroller.split_assetlist, name='split_assetlist'),
    path('codegenerator_split', splitcontroller.codegenerator_split, name='codegenerator_split'),

    path('search_subcategory', ServiceCall.search_subcategory, name='search_subcategory'),
    # path('fetch_branch', ServiceCall.fetch_branch, name='fetch_branch'),


    # merge
    path('merge_maker', mergecontroller.create_merge, name='merge'),
    path('merge_maker_search', mergecontroller.merge_maker_search, name='merge_maker_search'),
    path('merge_checker', mergecontroller.merge_checker, name='merge_checker'),
    path('merge_checker_search', mergecontroller.merge_checker_search, name='merge_checker_search'),
    path('merge_get', mergecontroller.merge_get, name='merge_get'),

    # impair
    path('cgumaster', cgumastercontroller.create_cgumaster, name='cgumaster'),
    path('search_cgu_name', cgumastercontroller.search_cgu_name, name='search_cgu_name'),
    path('search_impairmapping', impaircontroller.search_impairmapping, name='search_impairmapping'),
    path('cgu_mapping', impaircontroller.cgu_mapping, name='cgu_mapping'),
    path('search_impair_add', impaircontroller.search_impair_add, name='search_impair_add'),
    path('impair_maker', impaircontroller.impair_maker, name='impair_maker'),
    path('impair_checker', impaircontroller.impair_checker, name='impair_checker'),
    path('impair_checker_search', impaircontroller.impair_checker_search, name='impair_checker_search'),
    path('impair_maker_search', impaircontroller.impair_maker_search, name='impair_maker_search'),

    #### FA MIGRATIONS API
    path('fa_migration_data', depreciationcontroller.fa_migration_data, name='fa_migration_data'),
    #path('fa_depreciation', depreciationcontroller.fa_depreciationsingel, name='fa_depreciation'),
    path('createassetheader', assetheadercontroller.createassetheader, name='createassetheader'),
    path('asset_emp_map', assetdetailscontroller.asset_emp_map, name='asset_emp_map'),
    path('asset_map_activate_inactivate', assetdetailscontroller.asset_map_activate_inactivate, name='asset_map_activate_inactivate'),
    path('itdepreciation',depreciationcontroller.itdepreciation,name='itdepreciation'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)