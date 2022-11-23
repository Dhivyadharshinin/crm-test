import json
import datetime
from datetime import datetime,timedelta
import requests
from pprservice.controller.pprreportcontroller import get_authtoken_PPR
from nwisefin.settings import SERVER_IP, logger
from pprservice.models.pprmodel import Allocation_meta,Pprdata,Pprdata_maintable
from django.db.models import Count
from django.db.models import Q
from django.db import IntegrityError
from pprservice.data.response.success import Success, successMessage
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from masterservice.models.mastermodels import CostCentreBusinessSegmentMaping
from pprservice.data.response.allocationmetaresponse import FromAllocationResponse
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


from pprservice.data.response.pprreportresponse import pprresponse
from django.db.models import Sum
from pprservice.util.pprutility import Ppr_utilityservice, Pprutility_keys,VENDOR_SERVICE,USER_SERVICE,MASTER_SERVICE

class AllocationMeta_service(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.PPR_SERVICE)


    def from_allocation_create(self,request_obj,empid):
        if not request_obj.get_id() is None:
            try:
                # start = datetime.strptime(request_obj.get_validity_from(), "%Y-%m-%d")  # string to date
                # validity_todate = start - timedelta(days=1)
                allometa_obj_from = Allocation_meta.objects.using(self._current_app_schema()).filter(id=request_obj.get_id(),entity_id=self._entity_id()).update(level=request_obj.get_level(),cost_driver=request_obj.get_cost_driver(),
                                                      premium_amount=request_obj.get_allocation_amount(),
                                                                                                   validity_from=request_obj.get_validity_from(),
                                                                                                   validity_to=request_obj.get_validity_to(),
                                                      frombscccode=request_obj.get_frombscccode() ,created_by=empid)
                allometa_obj_from = Allocation_meta.objects.using(self._current_app_schema()).get(id=request_obj.get_id())
                response = FromAllocationResponse()
                response.set_id(allometa_obj_from.id)
                response.set_level_id(allometa_obj_from.level)
                response.set_cost_driver_id(allometa_obj_from.cost_driver)
                response.set_allocation_amount(allometa_obj_from.allocation_amount)
                response.flag = 1
                return response
            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Allocation_meta.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_Allocation_meta_ID)
                error_obj.set_description(ErrorDescription.INVALID_Allocation_meta_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            # try:
                meta_obj=Allocation_meta.objects.using(self._current_app_schema()).filter(Q(frombscccode=request_obj.get_frombscccode())&Q(status=1)).order_by('-created_date')
                start = datetime.strptime(request_obj.get_validity_from(), "%Y-%m-%d")  # string to date
                validity_todate = start - timedelta(days=1)
                if len(meta_obj) !=0:
                    meta_objid=meta_obj[0]
                    meta_obj1 = Allocation_meta.objects.using(self._current_app_schema()).filter(id=meta_objid.id).update(validity_to=validity_todate)

                else:
                    validity_todate=request_obj.get_validity_to()
                allometa_obj_from = Allocation_meta.objects.using(self._current_app_schema()).create(level=request_obj.get_level(),cost_driver=request_obj.get_cost_driver(),
                                                                  premium_amount=request_obj.get_allocation_amount(),validity_from=request_obj.get_validity_from(),
                                                            validity_to=request_obj.get_validity_to(),entity_id=self._entity_id(),
                                                                       frombscccode=request_obj.get_frombscccode(),created_by=empid)
                response = FromAllocationResponse()
                response.set_id(allometa_obj_from.id)
                response.set_level_id(allometa_obj_from.level)
                response.set_cost_driver_id(allometa_obj_from.cost_driver)
                response.set_allocation_amount(allometa_obj_from.allocation_amount)
                response.flag=1
                return response
            # except IntegrityError as error:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj


    def to_allocation_create(self,request_obj,from_obj,empid):
        print(from_obj)
        for i in request_obj.get_to_data():
            if not i.get_id() is None:
                try:

                    allometa_obj_to = Allocation_meta.objects.using(self._current_app_schema()).filter(id=i.get_id(),entity_id=self._entity_id()).update(source_bscc_code_id=from_obj.id,
                                                             level=from_obj.level_id,
                                                             cost_driver=from_obj.cost_driver_id,
                                                             allocation_amount=from_obj.allocation_amount,
                                                             bscc_code=i.get_bscc_code(),
                                                             cc_id=i.get_cc_id(),
                                                             bs_id=i.get_bs_id(),
                                                             parameter=i.get_parameter(),
                                                             input_value=i.get_input_value(),
                                                             ratio=i.get_ratio(),
                                                             premium_amount=i.get_premium_amount(),
                                                             to_amount=i.get_to_amount(),
                                                                status=i.get_status(),
                                                             created_by=empid)
                    # allometa_obj_to = Allocation_meta.objects.get(id=i.get_id())
                    # response = FromAllocationResponse()
                    # response.set_id(allometa_obj_to.id)
                    # response.set_level(allometa_obj_to.level)
                    # response.set_cost_driver(allometa_obj_to.cost_driver)
                    # response.set_allocation_amount(allometa_obj_to.allocation_amount)
                    # response.set_bscc_code(allometa_obj_to.bscc_code)
                    # response.set_cc_id(allometa_obj_to.cc_id)
                    # response.set_bs_id(allometa_obj_to.bs_id)
                    # response.set_parameter(allometa_obj_to.parameter)
                    # response.set_input_value(allometa_obj_to.input_value)
                    # response.set_ratio(allometa_obj_to.ratio)
                    # response.set_to_amount(allometa_obj_to.to_amount)
                except IntegrityError as error:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
                except Allocation_meta.DoesNotExist:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_Allocation_meta_ID)
                    error_obj.set_description(ErrorDescription.INVALID_Allocation_meta_ID)
                    return error_obj
                except:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                    return error_obj
            else:
                # try:

                    allometa_obj_to = Allocation_meta.objects.using(self._current_app_schema()).create(source_bscc_code_id=from_obj.id,
                                                                     level=from_obj.level_id,
                                                                     cost_driver=from_obj.cost_driver_id,
                                                                     allocation_amount=from_obj.allocation_amount,
                                                                     bscc_code=i.get_bscc_code(),
                                                                     cc_id=i.get_cc_id(),
                                                                     bs_id=i.get_bs_id(),
                                                                     parameter=i.get_parameter(),
                                                                     input_value=i.get_input_value(),
                                                                     ratio=i.get_ratio(),
                                                                     to_amount=i.get_to_amount(),
                                                                     premium_amount=i.get_premium_amount(),
                                                                     created_by=empid,entity_id=self._entity_id())
                    # response = FromAllocationResponse()
                    # response.set_id(allometa_obj_to.id)
                    # response.set_level(allometa_obj_to.level)
                    # response.set_cost_driver(allometa_obj_to.cost_driver)
                    # response.set_allocation_amount(allometa_obj_to.allocation_amount)
                    # response.set_bscc_code(allometa_obj_to.bscc_code)
                    # response.set_cc_id(allometa_obj_to.cc_id)
                    # response.set_bs_id(allometa_obj_to.bs_id)
                    # response.set_parameter(allometa_obj_to.parameter)
                    # response.set_input_value(allometa_obj_to.input_value)
                    # response.set_ratio(allometa_obj_to.ratio)
                    # response.set_to_amount(allometa_obj_to.to_amount)
                # except IntegrityError as error:
                #     error_obj = Error()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj
                # except:
                #     error_obj = Error()
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                #     return error_obj


    def fetch_individual(self,id):
        utility = Ppr_utilityservice(self._scope())
        vendorservice=VENDOR_SERVICE(self._scope())
        userservice=USER_SERVICE(self._scope())
        masterservice=MASTER_SERVICE(self._scope())
        condition = Q(id=id,entity_id=self._entity_id())
        From_Allocation_data = Allocation_meta.objects.using(self._current_app_schema()).get(condition)
        from_response = FromAllocationResponse()
        from_response.set_id(From_Allocation_data.id)
        from_response.set_level(From_Allocation_data.level,utility.get_level([From_Allocation_data.level]))
        from_response.set_cost_driver(From_Allocation_data.cost_driver,utility.get_costderiver([From_Allocation_data.cost_driver]))
        from_response.set_allocation_amount(str(From_Allocation_data.allocation_amount))
        from_response.premium_amount=(str(From_Allocation_data.premium_amount))
        from_response.status=From_Allocation_data.status
        from_response.set_validity_from(From_Allocation_data.validity_from)
        from_response.set_validity_to(From_Allocation_data.validity_to)
        from_response.set_bscc(From_Allocation_data.frombscccode,userservice.get_mst_segment([From_Allocation_data.frombscccode]))
        To_Allocation_data = Allocation_meta.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),status=1,source_bscc_code=From_Allocation_data.id)
        response_arr = []
        bscc_id = []
        cc_id = []
        bs_id = []
        for k in To_Allocation_data:
            cc_id.append(k.cc_id)
            bs_id.append(k.bs_id)
            bscc_id.append(k.bscc_code)
        bscc_data = userservice.get_mst_segment(bscc_id)
        cc_data = userservice.get_CC(cc_id)
        bs_data = userservice.get_BS(bs_id)
        for i in To_Allocation_data:
            to_response = FromAllocationResponse()
            to_response.set_id(i.id)
            to_response.set_bscc(i.bscc_code,bscc_data)
            to_response.set_cc(i.cc_id,cc_data)
            to_response.set_bs(i.bs_id,bs_data)
            to_response.set_parameter(i.parameter)
            to_response.set_input_value(str(i.input_value))
            to_response.set_ratio(str(i.ratio))
            to_response.set_to_amount(str(i.to_amount))
            to_response.premium_amount=i.premium_amount
            to_response.set_validity_from(i.validity_from)
            to_response.set_validity_to(i.validity_to)
            response_arr.append(to_response)
        from_response.set_to_data(response_arr)
        return from_response

    def fetch_individual_genrate(self,frombscccode,month,year,date1):
        utility = Ppr_utilityservice(self._scope())
        userservice=USER_SERVICE(self._scope())
        condition = Q(frombscccode=frombscccode,status=1,entity_id=self._entity_id())
        From_Allocation_data = Allocation_meta.objects.using(self._current_app_schema()).filter(condition)
        if len(From_Allocation_data)!=0:
            From_Allocation_data=From_Allocation_data[0]
        else:
            from_response = FromAllocationResponse()
            from_response.set_to_data([])
            return from_response
        from_response = FromAllocationResponse()
        from_response.set_id(From_Allocation_data.id)
        from_response.status = From_Allocation_data.status
        from_response.set_validity_from(From_Allocation_data.validity_from)
        from_response.set_validity_to(From_Allocation_data.validity_to)
        from_response.set_level(From_Allocation_data.level,utility.get_level([From_Allocation_data.level]))
        from_response.set_cost_driver(From_Allocation_data.cost_driver,utility.get_costderiver([From_Allocation_data.cost_driver]))
        from_response.set_allocation_amount(str(From_Allocation_data.allocation_amount))
        from_response.premium_amount=(str(From_Allocation_data.premium_amount))
        from_response.set_bscc(From_Allocation_data.frombscccode,userservice.get_mst_segment([From_Allocation_data.frombscccode]))
        To_Allocation_data = Allocation_meta.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),status=1,source_bscc_code=From_Allocation_data.id)
        response_arr = []
        bscc_id = []
        cc_id = []
        bs_id = []
        for k in To_Allocation_data:
            cc_id.append(k.cc_id)
            bs_id.append(k.bs_id)
            bscc_id.append(k.bscc_code)
        bscc_data = userservice.get_mst_segment(bscc_id)
        cc_data = userservice.get_CC(cc_id)
        bs_data = userservice.get_BS(bs_id)
        for i in To_Allocation_data:
            to_response = FromAllocationResponse()
            to_response.set_id(i.id)
            to_response.set_bscc(i.bscc_code,bscc_data)
            to_response.set_cc(i.cc_id,cc_data)
            to_response.set_bs(i.bs_id,bs_data)
            to_response.set_parameter(i.parameter)
            to_response.set_input_value(str(i.input_value))
            to_response.set_ratio(str(i.ratio))
            to_response.set_to_amount(str(i.to_amount))
            to_response.premium_amount=i.premium_amount
            to_response.set_validity_from(i.validity_from)
            to_response.set_validity_to(i.validity_to)
            response_arr.append(to_response)
        from_response.set_to_data(response_arr)
        return from_response

    def fetch_all(self,vys_page,frombscccode):
        utility = Ppr_utilityservice(self._scope())
        userservice = USER_SERVICE(self._scope())
        condition = Q(source_bscc_code=None,entity_id=self._entity_id())
        if frombscccode != None:
            condition &=Q(frombscccode=frombscccode)
        allocation_data = Allocation_meta.objects.using(self._current_app_schema()).filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
        allocation_arr = []
        level_id = []
        costdriver_id = []
        frombscc_id=[]
        vlist = NWisefinList()
        for i in allocation_data:
            allocation_arr.append(i.id)
            level_id.append(i.level)
            costdriver_id.append(i.cost_driver)
            frombscc_id.append((i.frombscccode))
        level_data = utility.get_level(level_id)
        costdriver_data = utility.get_costderiver(costdriver_id)
        frombsccdata=userservice.get_mst_segment(frombscc_id)
        To_allocation_data = Allocation_meta.objects.using(self._current_app_schema()).filter(status=1,source_bscc_code__in=allocation_arr,entity_id=self._entity_id())
        bscc_id = []
        cc_id = []
        bs_id = []
        for k in To_allocation_data:
            cc_id.append(k.cc_id)
            bs_id.append(k.bs_id)
            bscc_id.append(k.bscc_code)
        bscc_data = userservice.get_mst_segment(bscc_id)
        # cc_data = userservice.get_CC(cc_id)
        # bs_data = userservice.get_BS(bs_id)
        out_response = []

        for i in allocation_data:
            to_response_arr = []
            from_response = FromAllocationResponse()
            from_response.set_id(i.id)
            from_response.set_level(i.level, level_data)
            from_response.set_cost_driver(i.cost_driver,costdriver_data)
            from_response.set_allocation_amount(str(i.allocation_amount))
            from_response.premium_amount=(str(i.premium_amount))
            from_response.status=i.status
            from_response.set_validity_from(i.validity_from)
            from_response.set_validity_to(i.validity_to)
            from_response.set_bscc(i.frombscccode,frombsccdata)
            for j in To_allocation_data:
                if j.source_bscc_code.id==i.id:
                    to_response = FromAllocationResponse()
                    to_response.set_id(j.id)
                    to_response.set_bscc(j.bscc_code, bscc_data)
                    # to_response.set_cc(j.cc_id, cc_data)
                    # to_response.set_bs(j.bs_id, bs_data)
                    to_response.set_parameter(j.parameter)
                    to_response.set_input_value(str(j.input_value))
                    to_response.set_ratio(str(j.ratio))
                    to_response.set_to_amount(str(j.to_amount))
                    to_response_arr.append(to_response)
            from_response.set_to_data(to_response_arr)
            vlist.append(from_response)
            vpage = NWisefinPaginator(allocation_data, vys_page.get_index(), 10)
            vlist.set_pagination(vpage)
        return vlist

    def remsbased_allocation(self,bs_code,cc_code,transactionmonth,transactionyear):
        ppr_obj = Pprdata.objects.using(self._current_app_schema()).filter(Q(bs_code=bs_code) & Q(cc_code=cc_code) & Q(
            transactionmonth=transactionmonth)&Q(entry_crno__icontains='RNT') & Q(transactionyear=transactionyear)& Q(entity_id=self._entity_id()))
        auth_token = get_authtoken_PPR()
        token = 'Token ' + str(auth_token)
        a=1
        for i in ppr_obj:
            allocationfrom_obj = Allocation_meta.objects.using(self._current_app_schema()).create(frombscccode=1,level=1,cost_driver=1,allocation_amount=1000,created_by=1,entity_id=self._entity_id(),)
            # url = SERVER_IP + '/pdserv/occupancyccbs_dtls/' + (str(i.entry_crno))
            url = SERVER_IP + '/pdserv/occupancyccbs_dtls/' + ('RNT2112090002')
            headers = {"content-type": "application/json", "Authorization": "" + token + ""}
            data = dict()
            ro_numberresp = requests.get(url, data=data, headers=headers, verify=False)
            ronumber_json = json.loads(ro_numberresp.content)
            newcrno='RNT2112090002'+'CA'
            # try:
            if 1==1:
                data_obj=ronumber_json['data']
                for inputdata in data_obj:
                    tobscc=CostCentreBusinessSegmentMaping.objects.using(self._current_app_schema()).filter(costcentre_id=inputdata['costcentre_details']['id'],businesssegment_id=inputdata['businesssegment_details']['id'])
                    allocationto_obj = Allocation_meta.objects.using(self._current_app_schema()).create(source_bscc_code_id=allocationfrom_obj.id,
                                                                     level=allocationfrom_obj.level,
                                                                     cost_driver=allocationfrom_obj.cost_driver,
                                                                     allocation_amount=allocationfrom_obj.allocation_amount,
                                                                     bscc_code=tobscc[0].id,
                                                                     cc_id=inputdata['costcentre_details']['id'],
                                                                     bs_id=inputdata['businesssegment_details']['id'],
                                                                     parameter='sq.feet',
                                                                     input_value=inputdata['area'],
                                                                     # ratio=i.get_ratio(),
                                                                     # to_amount=i.get_to_amount(),
                                                                     premium_amount=10,
                                                                      newcr_number=newcrno,
                                                                     created_by=1,entity_id=self._entity_id())
            # except:
            #     pass

            q='oi'
            if a==1:
                break
            # allocation_obj=Allocation_meta.objects.create(frombscccode=i.frombscccode)

    def otherthenrems_allocation(self,bs_code,cc_code,transactionmonth,transactionyear):
        ppr_obj=Pprdata.objects.using(self._current_app_schema()).filter(Q(bs_code=bs_code)&Q(cc_code=cc_code)&~Q(entry_crno__icontains='RNT')&Q(transactionmonth=transactionmonth)&Q(transactionyear=transactionyear)&Q(entity_id=self._entity_id()))
        print('fg',len(ppr_obj))
        data_list = NWisefinList()
        for i in ppr_obj:
            pprresponser = pprresponse()
            pprresponser.id=i.id
            pprresponser.set_bscode(i.bs_code)
            pprresponser.set_cccode(i.cc_code)
            pprresponser.set_bsname(i.bsname)
            pprresponser.set_ccname(i.ccname)
            pprresponser.set_taxamount(str(i.taxamount))
            pprresponser.set_otheramount(str(i.otheramount))
            pprresponser.set_totalamount(str(i.totalamount))
            pprresponser.entry_module=i.entry_module
            pprresponser.entry_crno=i.entry_crno
            data_list.append(pprresponser)
        return data_list

    def tech_allocation(self,bs_code,cd_code,transactionmonth,transactionyear):
        utility = Ppr_utilityservice(self._scope())
        userservice = USER_SERVICE(self._scope())
        ppr_obj=Pprdata.objects.using(self._current_app_schema()).filter(Q(transactionmonth=transactionmonth)&Q(transactionyear=transactionyear)&Q(cc_code=cd_code)&Q(bs_code=bs_code)&Q(entity_id=self._entity_id())).values('cc_code','bs_code').annotate(dcount=Count('cc_code'),dcount1=Count('bs_code'),amount=Sum('totalamount'))
        print('fg',len(ppr_obj))
        data_list = NWisefinList()
        cc_id = []
        bs_id = []
        for k in ppr_obj:
            cc_id.append(k['cc_code'])
            bs_id.append(k['bs_code'])

        cc_data = userservice.get_CC_Code(cc_id)
        bs_data = userservice.get_BS_Code(bs_id)
        for i in ppr_obj:
            pprresponser = pprresponse()
            # pprresponser.id=i.id
            pprresponser.set_cc_codename(i['cc_code'], cc_data)
            pprresponser.set_bs_codename(i['bs_code'], bs_data)
            # pprresponser.set_taxamount(str(i.taxamount))
            # pprresponser.set_otheramount(str(i.otheramount))
            pprresponser.set_totalamount(str(i['amount']))
            # pprresponser.entry_module=i.entry_module
            # pprresponser.entry_crno=i.entry_crno
            data_list.append(pprresponser)
        return data_list

    def allocationtoppr(self,data_obj,empid):
        allocation_array = NWisefinList()
        for allocation_obj in data_obj:
            allocation_arr = Pprdata_maintable(
                                        finyear=allocation_obj.get_finyear(),
                                        quarter=allocation_obj.get_quarter(),
                                        apexpense_id=allocation_obj.get_apexpence_id(),
                                        sectorname=allocation_obj.get_sector(),
                                        categorygid=allocation_obj.get_cat_id(),
                                        status=allocation_obj.get_status(),
                                        apsubcat_id=allocation_obj.get_subcat_id(),
                                        transactionmonth=allocation_obj.get_transactionmonth(),
                                        transactionyear=allocation_obj.get_transactionyear(),
                                        transactiondate=allocation_obj.get_transactiondate(),
                                        valuedate=allocation_obj.get_valuedate(),
                                        cc_code=allocation_obj.get_cc_code(),
                                        bs_code=allocation_obj.get_bs_code(),
                                        apinvoice_id=allocation_obj.get_apinvoice_id(),
                                        bsname=allocation_obj.get_bsname(),
                                        ccname=allocation_obj.get_ccname(),
                                        bizname=allocation_obj.get_bizname(),
                                        level=allocation_obj.get_level(),
                                        cost_driver=allocation_obj.get_cost_driver(),
                                        allocation_amount=allocation_obj.get_allocation_amount(),
                                        bscc_code=allocation_obj.get_bscc_code(),
                                        parameter=allocation_obj.get_parameter(),
                                        input_value=allocation_obj.get_input_value(),
                                        ratio=allocation_obj.get_ratio(),
                                        to_amount=allocation_obj.get_to_amount(),
                                        amount=allocation_obj.get_to_amount(),
                                        source_bscc_code=allocation_obj.get_source_bscc_code(),
                                        frombscccode=allocation_obj.get_frombscccode(),
                                        premium_amount=allocation_obj.get_premium_amount(),
                                               create_by=empid

                                               )
            allocation_array.append(allocation_arr)
        Pprdata_maintable.objects.using(self._current_app_schema()).bulk_create(allocation_array)
        error_obj = NWisefinError()
        error_obj.set_code='success'
        error_obj.set_description='success'
        return error_obj

    def inactive_allocation(self,allocation_id,empid,status):
        allocation_obj=Allocation_meta.objects.using(self._current_app_schema()).filter(id=allocation_id).update(status=status,updated_by=empid,updated_date=datetime.now())
        success_obj = Success()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    def genrate_gl(self,type,bs_id,cc_id,transactionmonth,transactionyear,vys_page):
        utility = Ppr_utilityservice(self._scope())
        userservice = USER_SERVICE(self._scope())
        if type=='OD':
            condition=Q(bs_code=bs_id)&Q(cc_code=cc_id)&~Q(entry_crno__icontains='RNT')&Q(transactionmonth=transactionmonth)&Q(transactionyear=transactionyear)&Q(entity_id=self._entity_id())
        else:
            condition=Q(bs_code=bs_id)&Q(cc_code=cc_id)&Q(transactionmonth=transactionmonth)&Q(transactionyear=transactionyear)&Q(entity_id=self._entity_id())
        ppr_obj=Pprdata.objects.using(self._current_app_schema()).filter(condition).values('apsubcat_id','cc_code','bs_code').annotate(dcount=Count('apsubcat_id'),amount=Sum('totalamount'))[vys_page.get_offset():vys_page.get_query_limit()]
        data_list = NWisefinList()
        cc_id = []
        bs_id = []
        for k in ppr_obj:
            cc_id.append(k['cc_code'])
            bs_id.append(k['bs_code'])

        cc_data = userservice.get_CC_Code(cc_id)
        bs_data = userservice.get_BS_Code(bs_id)
        for i in ppr_obj:
            pprresponser = pprresponse()
            # pprresponser.id=i.id
            pprresponser.set_cc_codename(i['cc_code'], cc_data)
            pprresponser.set_bs_codename(i['bs_code'], bs_data)
            # pprresponser.set_taxamount(str(i.taxamount))
            # pprresponser.set_otheramount(str(i.otheramount))
            pprresponser.set_totalamount(str(i['amount']))
            # pprresponser.entry_module=i.entry_module
            # pprresponser.entry_crno=i.entry_crno
            data_list.append(pprresponser)
            vpage = NWisefinPaginator(ppr_obj, vys_page.get_index(), 10)
            data_list.set_pagination(vpage)
        # return vlist
        return data_list

    def transaction_ratioallocation(self,type,bs_id,cc_id,transactionmonth,transactionyear,frombscccode,vys_page):
        utility = Ppr_utilityservice(self._scope())
        if type=='OD':
            condition=Q(bs_code=bs_id)&Q(cc_code=cc_id)&~Q(entry_crno__icontains='RNT')&Q(transactionmonth=transactionmonth)&Q(transactionyear=transactionyear)&Q(entity_id=self._entity_id())
        else:
            condition=Q(bs_code=bs_id)&Q(cc_code=cc_id)&Q(transactionmonth=transactionmonth)&Q(transactionyear=transactionyear)&Q(entity_id=self._entity_id())
        ppr_obj=Pprdata.objects.using(self._current_app_schema()).filter(condition).values('apsubcat_id','cc_code','bs_code').annotate(dcount=Count('apsubcat_id'),amount1=Sum('totalamount')).values('apexpense_id','apsubcat_id','cc_code','bs_code','amount1')[vys_page.get_offset():vys_page.get_query_limit()]
        # ppr_obj=Pprdata.objects.filter(condition).values('apsubcat_id','cc_code','bs_code').annotate(dcount=Count('apsubcat_id'),amount=Sum('totalamount'))[vys_page.get_offset():vys_page.get_query_limit()]
        data_list = NWisefinList()
        condition = Q(frombscccode=frombscccode, status=1,entity_id=self._entity_id())
        From_Allocation_data = Allocation_meta.objects.using(self._current_app_schema()).filter(condition)
        if len(From_Allocation_data) != 0:
            From_Allocation_data = From_Allocation_data[0]
        else:
            from_response = FromAllocationResponse()
            from_response.set_to_data([])
            return from_response
        subcat_arr = []
        pprutility = Ppr_utilityservice(self._scope())
        masterservice=MASTER_SERVICE(self._scope())
        userservice=USER_SERVICE(self._scope())
        for arr_id in ppr_obj:
            subcat_arr.append(arr_id['apsubcat_id'])
        subcat_cat_data = masterservice.get_subcat(subcat_arr)
        To_Allocation_data = Allocation_meta.objects.using(self._current_app_schema()).filter(status=1, source_bscc_code=From_Allocation_data.id,entity_id=self._entity_id())
        for data1 in ppr_obj:
            gl_amount=data1['amount1']
            for ratioamount in To_Allocation_data:
                ratioamount1=ratioamount.ratio
                percentage_amount = float(ratioamount1)/100*float(gl_amount)
                from_response = FromAllocationResponse()
                # from_response.set_id(From_Allocation_data.id)
                # from_response.status = From_Allocation_data.status
                # from_response.percentage_amount = percentage_amount
                # from_response.set_validity_from(From_Allocation_data.validity_from)
                # from_response.set_validity_to(From_Allocation_data.validity_to)
                # from_response.set_level(From_Allocation_data.level, utility.get_level([From_Allocation_data.level]))
                # from_response.set_cost_driver(From_Allocation_data.cost_driver,
                #                               utility.get_costderiver([From_Allocation_data.cost_driver]))
                # from_response.set_allocation_amount(str(From_Allocation_data.allocation_amount))
                # from_response.premium_amount = (str(From_Allocation_data.premium_amount))
                # from_response.set_bscc(From_Allocation_data.frombscccode,
                #                        utility.get_mst_segment([From_Allocation_data.frombscccode]))
                # To_Allocation_data = Allocation_meta.objects.filter(status=1, source_bscc_code=From_Allocation_data.id)
                response_arr = []
                bscc_id = []
                cc_id = []
                bs_id = []
                for k in To_Allocation_data:
                    cc_id.append(k.cc_id)
                    bs_id.append(k.bs_id)
                    bscc_id.append(k.bscc_code)
                bscc_data = userservice.get_mst_segment(bscc_id)
                cc_data = userservice.get_CC(cc_id)
                bs_data = userservice.get_BS(bs_id)
                # for i in To_Allocation_data:
                to_response = FromAllocationResponse()
                to_response.set_id(ratioamount.id)
                to_response.subcat=data1['apsubcat_id']
                to_response.apexpense_id=data1['apexpense_id']
                to_response.ratioamount=percentage_amount
                to_response.set_bscc(ratioamount.bscc_code, bscc_data)
                to_response.set_cc(ratioamount.cc_id, cc_data)
                to_response.set_bs(ratioamount.bs_id, bs_data)
                to_response.set_parameter(ratioamount.parameter)
                to_response.set_input_value(str(ratioamount.input_value))
                to_response.set_ratio(str(ratioamount.ratio))
                to_response.set_to_amount(str(ratioamount.to_amount))
                to_response.premium_amount = ratioamount.premium_amount
                to_response.set_validity_from(ratioamount.validity_from)
                to_response.set_validity_to(ratioamount.validity_to)
                to_response.set_subcat_cat_data(subcat_cat_data, data1['apsubcat_id'])
                data_list.append(to_response)
                #     response_arr.append(to_response)
                # from_response.set_to_data(response_arr)
        print(len(data_list.data))
        vpage = NWisefinPaginator(ppr_obj, vys_page.get_index(), 10)
        data_list.set_pagination(vpage)
        return data_list

    def genrate_ratioallocation(self,type,bs_id,cc_id,transactionmonth,transactionyear,frombscccode,allocationto_ppr):
        utility = Ppr_utilityservice(self._scope())
        userservice=USER_SERVICE(self._scope())
        if type=='OD':
            condition=Q(bs_code=bs_id)&Q(cc_code=cc_id)&~Q(entry_crno__icontains='RNT')&Q(transactionmonth=transactionmonth)&Q(transactionyear=transactionyear)&Q(entity_id=self._entity_id())
        else:
            condition=Q(bs_code=bs_id)&Q(cc_code=cc_id)&Q(transactionmonth=transactionmonth)&Q(transactionyear=transactionyear)&Q(entity_id=self._entity_id())
        ppr_obj=Pprdata.objects.using(self._current_app_schema()).filter(condition).values('apsubcat_id','cc_code','bs_code').annotate(dcount=Count('apsubcat_id'),amount1=Sum('totalamount')).values('apexpense_id','apsubcat_id','cc_code','bs_code','amount1','categorygid')
        # ppr_obj=Pprdata.objects.filter(condition).values('apsubcat_id','cc_code','bs_code').annotate(dcount=Count('apsubcat_id'),amount=Sum('totalamount'))[vys_page.get_offset():vys_page.get_query_limit()]
        data_list = NWisefinList()
        condition = Q(frombscccode=frombscccode, status=1,entity_id=self._entity_id())
        From_Allocation_data = Allocation_meta.objects.using(self._current_app_schema()).filter(condition)
        if len(From_Allocation_data) != 0:
            From_Allocation_data = From_Allocation_data[0]
        else:
            from_response = FromAllocationResponse()
            from_response.set_to_data([])
            return from_response
        To_Allocation_data = Allocation_meta.objects.using(self._current_app_schema()).filter(status=1, source_bscc_code=From_Allocation_data.id,entity_id=self._entity_id())
        for data1 in ppr_obj:
            gl_amount=data1['amount1']
            for ratioamount in To_Allocation_data:
                ratioamount1=ratioamount.ratio
                percentage_amount = 50/100*float(gl_amount)

                from_response = FromAllocationResponse()
                response_arr = []
                bscc_id = []
                cc_id = []
                bs_id = []
                for k in To_Allocation_data:
                    cc_id.append(k.cc_id)
                    bs_id.append(k.bs_id)
                    bscc_id.append(k.bscc_code)
                bscc_data = userservice.get_mst_segment(bscc_id)
                cc_data = userservice.get_CC(cc_id)
                bs_data = userservice.get_BS(bs_id)
                # for i in To_Allocation_data:
                to_response = FromAllocationResponse()
                to_response.set_id(ratioamount.id)
                to_response.subcat=data1['apsubcat_id']
                to_response.categorygid=data1['categorygid']
                to_response.apexpense_id=data1['apexpense_id']
                to_response.ratioamount=percentage_amount
                to_response.set_bscc(ratioamount.bscc_code, bscc_data)
                to_response.set_cc(ratioamount.cc_id, cc_data)
                to_response.set_bs(ratioamount.bs_id, bs_data)
                to_response.set_parameter(ratioamount.parameter)
                to_response.set_input_value(str(ratioamount.input_value))
                to_response.set_ratio(str(ratioamount.ratio))
                to_response.set_to_amount(str(ratioamount.to_amount))
                to_response.premium_amount = ratioamount.premium_amount
                to_response.set_validity_from(ratioamount.validity_from)
                to_response.set_validity_to(ratioamount.validity_to)
                data_list.append(to_response)
                #     response_arr.append(to_response)
                # from_response.set_to_data(response_arr)
        print(len(data_list.data))
        return data_list

    def checkallocation_genrated(self,level,month,year):
        ppr_obj=Pprdata_maintable.objects.using(self._current_app_schema()).filter(Q(level=level)&Q(transactionmonth=month)&Q(transactionyear=year)&Q(entity_id=self._entity_id()))
        if len(ppr_obj)!=0:
            a=1
            return a
        else:
            b=2
            return b



