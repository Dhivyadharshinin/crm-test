import json
import traceback
from datetime import datetime
from django.http import HttpResponse

from masterservice.service.apsubcategoryservice import SubcategoryService
from masterservice.service.productservice import ProductService
from masterservice.models import CodeGenHeader, CodeGenDetails, APsubcategory
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.api_service import ApiService

class CodegeneratorService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def fetch_codegenerator_list(self, request,codegen_req):
        month_str = ''
        code_list = []
        mst_obj= ProductService(self._scope())  # changed
        subcat_obj=SubcategoryService(self._scope())  # changed
        qty=0
        if isinstance(request, dict):
            # product_data = mst_obj.fetch_product(request['product_id'], codegen_req.user.id)
            subcat_data = request['subcat']
        else:
            subcat_data=codegen_req.subcat_data
            # product_data = mst_obj.fetch_product(int(codegen_req.product), request.user.id)
            if codegen_req.qty >= 1:
                qty=codegen_req.qty
            else:
                qty=1
        if qty==0:
            if 'QTY' in request:
                qty = request['QTY']
        try:
            subcat_data = subcat_obj.fetchsubcategory(subcat_data)
            codegenheader_data = CodeGenHeader.objects.using(self._current_app_schema()).get(modulename='FA', name='FA_ASSET',entity_id=self._entity_id())
            codegendet = CodeGenDetails.objects.using(self._current_app_schema()).get(codegenheader_id=codegenheader_data.id,
                                                wherecondcolumn=subcat_data.code, entity_id=self._entity_id())
        except:
            err=NWisefinError()
            err.set_code(ErrorMessage.INVALID_CODEGENDATA)
            err.set_description(ErrorDescription.INVALID_CODEGEN_DATA)
            return err.get()
        col_prefix = codegendet.columnprefix
        if datetime.today().month is 1:
            month_str = "A"
        if datetime.today().month is 2:
            month_str = "B"
        if datetime.today().month is 3:
            month_str = "C"
        if datetime.today().month is 4:
            month_str = "D"
        if datetime.today().month is 5:
            month_str = "E"
        if datetime.today().month is 6:
            month_str = "F"
        if datetime.today().month is 7:
            month_str = "G"
        if datetime.today().month is 8:
            month_str = "H"
        if datetime.today().month is 9:
            month_str = "I"
        if datetime.today().month is 10:
            month_str = "J"
        if datetime.today().month is 11:
            month_str = "K"
        if datetime.today().month is 12:
            month_str = "L"
        header_format = codegenheader_data.format[11:16]
        rnsl = 0
        for i in range(qty):
            rnsl = int(codegendet.rnsl) + 1
            codegendet.rnsl = str(int(codegendet.rnsl) + 1)
            code = col_prefix + month_str + str(datetime.now().year)[2:] + str(subcat_data.assetcode) + str(rnsl).zfill(
                5) + '/01/01'
            code_list.append(code)
        resp = {'data': code_list}
        codegendet.rnsl = rnsl
        codegendet.save()
        response = HttpResponse(json.dumps(resp), content_type="application/json")
        return response

    def fetch_codegenerator_list_new(self, request, codegen_req):
        month_str = ''
        code_list = []
        common_service = ApiService(self._scope())
        mst_obj = ProductService(self._scope())  # changed
        subcat_obj = SubcategoryService(self._scope())  # changed
        qty = 0
        if isinstance(request, dict):
            # product_data = mst_obj.fetch_product(request['product_id'], codegen_req.user.id)
            subcat_data = request['subcat']
            branch_data = request['branch']
        else:
            subcat_data = codegen_req.subcat_data
            branch_data = codegen_req.branch_data
            # product_data = mst_obj.fetch_product(int(codegen_req.product), request.user.id)
            if codegen_req.qty >= 1:
                qty = codegen_req.qty
            else:
                qty = 1
        if qty == 0:
            if 'QTY' in request:
                qty = request['QTY']
        try:
            subcat_data = subcat_obj.fetchsubcategory(subcat_data)
            codegenheader_data = CodeGenHeader.objects.using(self._current_app_schema()).get(modulename='FA',
                                                                                             name='FA_ASSET',
                                                                                             entity_id=self._entity_id())
            codegendet = CodeGenDetails.objects.using(self._current_app_schema()).filter(
                codegenheader_id=codegenheader_data.id,
                wherecondcolumn=subcat_data.code, entity_id=self._entity_id()).order_by('-id')[0]
        except:
            err = NWisefinError()
            err.set_code(ErrorMessage.INVALID_CODEGENDATA)
            err.set_description(ErrorDescription.INVALID_CODEGEN_DATA)
            return err.get()
        # try:
        branch_data = common_service.fetch_branch_list(branch_data)
        #     codegenheader_data = CodeGenHeader.objects.using(self._current_app_schema()).get(modulename='FA',
        #                                                                                      name='FA_ASSET',
        #                                                                                      entity_id=self._entity_id())
        #     codegendet = CodeGenDetails.objects.using(self._current_app_schema()).get(
        #         codegenheader_id=codegenheader_data.id,
        #         wherecondcolumn=branch_data.Assetcodeprimary, entity_id=self._entity_id())
        # except:
        #     err = NWisefinError()
        #     err.set_code(ErrorMessage.INVALID_CODEGENDATA)
        #     err.set_description(ErrorDescription.INVALID_CODEGEN_DATA)
        #     return err.get()
        col_prefix = codegendet.columnprefix
        if datetime.today().month is 1:
            month_str = "A"
        if datetime.today().month is 2:
            month_str = "B"
        if datetime.today().month is 3:
            month_str = "C"
        if datetime.today().month is 4:
            month_str = "D"
        if datetime.today().month is 5:
            month_str = "E"
        if datetime.today().month is 6:
            month_str = "F"
        if datetime.today().month is 7:
            month_str = "G"
        if datetime.today().month is 8:
            month_str = "H"
        if datetime.today().month is 9:
            month_str = "I"
        if datetime.today().month is 10:
            month_str = "J"
        if datetime.today().month is 11:
            month_str = "K"
        if datetime.today().month is 12:
            month_str = "L"
        header_format = codegenheader_data.format[11:16]
        rnsl = 0
        for i in range(qty):
            rnsl = int(codegendet.rnsl) + 1
            codegendet.rnsl = str(int(codegendet.rnsl) + 1)
            code = str(branch_data.Assetcodeprimary) + str(subcat_data.assetcode) + str(rnsl).zfill(
                5) + '/01/01'
            code_list.append(code)
        resp = {'data': code_list}
        codegendet.rnsl = rnsl
        codegendet.save()
        response = HttpResponse(json.dumps(resp), content_type="application/json")
        return response


    def code_gen_details(self, cgs_data, emp_id):
        month='01'
        year=2020
        day=25
        tablename = 'fa_trn_tassetdetails'
        columnname = 'assetdetails_id'
        columnprefix='NAC'
        rnsl='0'
        displayorder='0'
        remarks='FA'
        status=1
        codegenheader=1

        try:
            sub_data=APsubcategory.objects.using(self._current_app_schema()).get(id=cgs_data['subcat_id'])
            data=CodeGenDetails.objects.using(self._current_app_schema()).filter(wherecondcolumn=sub_data.code)
            if len (data)> 1:
                if 'url' in cgs_data:
                    err=NWisefinError()
                    err.set_code(ErrorMessage.DUPLICATE_ENTRY)
                    err.set_description(ErrorDescription.DUPLICATE_NAME)
                    return err
                else:
                    return None
            cgs_var = CodeGenDetails.objects.using(self._current_app_schema()).create(entity_id=self._entity_id(),
                                                        tablename=tablename, columnname=columnname,
                                                        columnlen=32, columnprefix=columnprefix, month=month,
                                                        year=year, day=day, rnsl=rnsl, displayorder=displayorder,
                                                        remarks=remarks, status=status, codegenheader_id=codegenheader,
                                                        wherecondcolumn=sub_data.code,created_by=emp_id,created_date=datetime.now())
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj

        except Exception as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorMessage.UNEXPECTED_ERROR)
            return error_obj







