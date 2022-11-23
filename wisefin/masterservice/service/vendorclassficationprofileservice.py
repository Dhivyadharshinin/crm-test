import json
from masterservice.data.response.vendorclassficationprofileresponse import VendorclassficationprofileResponse
from masterservice.models import Vendorclassification_Mapping, Questions
from masterservice.service.activityservice import Activityservice
from masterservice.service.questionheaderservice import QuestionheaderService
from masterservice.service.questionservice import QuestionService
from masterservice.service.questiontypeservice import QuestiontypeService
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessMessage, SuccessStatus
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from django.db.models import Q
from masterservice.util.masterutil import ModifyStatus, Is_activity_level, Vendorclassfication_type
from vendorservice.data.response.activityresponse import ActivityResponse
from vendorservice.models import SupplierActivity


class VendorclassficationService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def vendorclassfication_create(self, vendorclassfication_req, emp_id):
        resp = NWisefinSuccess()
        if not vendorclassfication_req.get_id() is None:
            obj = Vendorclassification_Mapping.objects.using(self._current_app_schema()).filter(id=vendorclassfication_req.get_id(), entity_id=self._entity_id()).update(type_id=vendorclassfication_req.get_type_id(),
                                                                                                                        rel_cat=vendorclassfication_req.get_rel_cat(),
                                                                                                                        criticality=vendorclassfication_req.get_criticality(),
                                                                                                                        vendor_type=vendorclassfication_req.get_vendor_type(),
                                                                                                                        period=vendorclassfication_req.get_period(),
                                                                                                                        process=vendorclassfication_req.get_process(),
                                                                                                                        dept_id=vendorclassfication_req.get_dept_id(),
                                                                                                                        is_doc=vendorclassfication_req.get_is_doc(),
                                                                                                                        document_group_id=vendorclassfication_req.get_document_group_id(), updated_by=emp_id,order=vendorclassfication_req.get_order(),expiration_date=vendorclassfication_req.get_expiration_date(),is_activity=vendorclassfication_req.get_is_activity())

            obj = Vendorclassification_Mapping.objects.using(self._current_app_schema()).get(id=vendorclassfication_req.get_id(), entity_id=self._entity_id())
            resp.set_message(SuccessMessage.UPDATE_MESSAGE)
            resp.set_status(SuccessStatus.SUCCESS)



        else:
            # for val in vendorclassfication_req:
            obj = Vendorclassification_Mapping.objects.using(self._current_app_schema()).create(type_id=vendorclassfication_req.get_type_id(),
                                                                                                                        rel_cat=vendorclassfication_req.get_rel_cat(),
                                                                                                                        criticality=vendorclassfication_req.get_criticality(),
                                                                                                                        vendor_type=vendorclassfication_req.get_vendor_type(),
                                                                                                                        period=vendorclassfication_req.get_period(),
                                                                                                                        process=vendorclassfication_req.get_process(),
                                                                                                                        dept_id=vendorclassfication_req.get_dept_id(),
                                                                                                                        is_doc=vendorclassfication_req.get_is_doc(),
                                                                                                                        document_group_id=vendorclassfication_req.get_document_group_id(), created_by=emp_id, entity_id=self._entity_id(),order=vendorclassfication_req.get_order(),expiration_date=vendorclassfication_req.get_expiration_date(),is_activity=vendorclassfication_req.get_is_activity())

            resp.set_message(SuccessMessage.CREATE_MESSAGE)
            resp.set_status(SuccessStatus.SUCCESS)

        return resp


    def fetch_vendorclassficationprofile(self,vys_page,request):
        query = request.GET.get('query')
        condtion = Q(entity_id=self._entity_id(), status=ModifyStatus.create)
        if query is not None and query !='':
            condtion &=Q(type=query)
        vendor_classobj = Vendorclassification_Mapping.objects.using(self._current_app_schema()).filter(condtion).order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        type_data = [i.type.id for i in vendor_classobj]
        type_serv = QuestiontypeService(self._scope())
        type_obj = type_serv.questiontype_info(type_data)
        list_data = NWisefinList()
        for obj in vendor_classobj:
            data_resp = VendorclassficationprofileResponse()
            data_resp.set_id(obj.id)
            data_resp.set_type_id(obj.type.id,type_obj)
            data_resp.set_vendor_type(obj.vendor_type)
            data_resp.set_period(obj.period)
            data_resp.set_process(obj.process)
            data_resp.set_criticality(obj.criticality)
            data_resp.set_dept_id(obj.dept_id,self._scope())
            data_resp.set_document_group(obj.document_group, self._scope())
            data_resp.set_is_doc(obj.is_doc)
            data_resp.set_rel_cat(obj.rel_cat)
            data_resp.set_order(obj.order)
            data_resp.set_is_activity(obj.is_activity)
            data_resp.set_expiration_date(obj.expiration_date)
            list_data.append(data_resp)
        vpage = NWisefinPaginator(vendor_classobj, vys_page.get_index(), 10)
        list_data.set_pagination(vpage)
        return list_data

    def get_vendorclassfication(self, id):
        obj = Vendorclassification_Mapping.objects.using(self._current_app_schema()).get(id=id, entity_id=self._entity_id())
        data_resp = VendorclassficationprofileResponse()
        data_resp.set_id(obj.id)
        type_serv = QuestiontypeService(self._scope())
        type_id = type_serv.question_single_get(obj.type_id)
        data_resp.set_type(type_id)
        data_resp.set_vendor_type(obj.vendor_type)
        data_resp.set_period(obj.period)
        data_resp.set_process(obj.process)
        data_resp.set_criticality(obj.criticality)
        data_resp.set_dept_id(obj.dept_id, self._scope())
        data_resp.set_document_group(obj.document_group, self._scope())
        data_resp.set_is_doc(obj.is_doc)
        data_resp.set_rel_cat(obj.rel_cat)
        data_resp.set_order(obj.order)
        data_resp.set_is_activity(obj.is_activity)
        data_resp.set_expiration_date(obj.expiration_date)

        return data_resp

    def del_vendorclassfication(self, id):
        obj = Vendorclassification_Mapping.objects.using(self._current_app_schema()).filter(id=id,
                                                                                            entity_id=self._entity_id()).update(status=ModifyStatus.delete)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj

    def obj_dict(self,obj):
        return obj.__dict__
    def get_vendorclassfication_type(self, data):
        list_data = NWisefinList()
        vendor_classobj = Vendorclassification_Mapping.objects.using(self._current_app_schema()).filter(criticality=data['criticality'],vendor_type=data['vendor_type'],rel_cat=data['rel_cat'],entity_id=self._entity_id(), is_doc=False,is_activity=False)
        if len(vendor_classobj)>0:
            for obj in vendor_classobj:
                data_resp = VendorclassficationprofileResponse()
                data_resp.set_id(obj.id)
                type_serv = QuestiontypeService(self._scope())
                type = type_serv.question_single_get(obj.type_id)
                data_resp.set_type(type)
                # data_resp.set_type_id(obj.type_id, self._scope())
                data_resp.set_dept_id(obj.dept_id, self._scope())
                # data_resp.set_document_group(obj.document_group, self._scope())
                data_resp.set_is_doc(obj.is_doc)
                # data_resp.set_rel_cat(obj.rel_cat)
                questionservice=QuestionService(self._scope())
                headerservice=QuestionheaderService(self._scope())
                question=questionservice.get_question_type(obj.type_id,data)
                header=headerservice.fetch_questionheaderbased_type(obj.type_id)
                data_resp.set_Questionc(json.loads(question))
                data_resp.set_header(json.loads(header))
                data_resp.set_order(obj.order)
                data_resp.set_period(obj.period)
                list_data.append(data_resp)
            data=json.dumps(list_data, default=self.obj_dict)
        else:
            data='[]'
        return data


    def get_vendorclassfication_mapping(self, v_data):
        list_data = NWisefinList()
        for i in v_data:
            activity = i['activity_id']
            activity =(str(activity))
            activity_serv = Activityservice(self._scope())
            activity_id = activity_serv.get_activity(activity)
            type_data = []
            # activity_var = SupplierActivity.objects.using(self._current_app_schema()).filter(branch__vendor_id=i['branch__vendor_id']).values('activity_id', 'id', 'rel_type', 'name')
            # print("activity",activity_var)
            vendor_classobj = Vendorclassification_Mapping.objects.using(self._current_app_schema()).filter(is_activity=True,rel_cat=i['rel_type'],entity_id=self._entity_id(), is_doc=False)
            if vendor_classobj.count()>0:
                for obj in vendor_classobj:
                    data_resp = VendorclassficationprofileResponse()
                    # ven_resp = ActivityResponse()
                    # ven_resp.set_Activity(v_data)
                    # data_resp.set_id(obj.id)
                    type_serv = QuestiontypeService(self._scope())
                    type = type_serv.question_single_get(obj.type_id)
                    data_resp.set_type(type)
                    # data_resp.set_type_id(obj.type_id, self._scope())
                    data_resp.set_dept_id(obj.dept_id, self._scope())
                    # data_resp.set_document_group(obj.document_group, self._scope())
                    data_resp.set_is_doc(obj.is_doc)
                    # data_resp.set_rel_cat(obj.rel_cat)
                    questionservice=QuestionService(self._scope())
                    headerservice=QuestionheaderService(self._scope())
                    # data_resp.set_sub_options(QuestionService.get_sub_question_arr(self, obj.id))
                    question=questionservice.get_question_mapping(obj.type_id,i)
                    header=headerservice.fetch_questionheaderbased_type(obj.type_id)
                    data_resp.set_Questionc(json.loads(question))
                    data_resp.set_header(json.loads(header))
                    data_resp.set_order(obj.order)
                    data_resp.set_Activity({"activity_id":i['activity_id'],"id":i['id'],"name":i['name']})
                    data_resp.set_period(obj.period)
                    type_data.append(data_resp)
            d = {"activity": activity_id, "type_data": type_data}
            list_data.append(d)
            # data=json.dumps(list_data, default=self.obj_dict)

        return json.dumps(list_data, default=self.obj_dict)

    # VENDOR_CLASSFICATION_DOC_ID
    def get_vendor_documents(self, data,vys_page,query):
        condition=Q(criticality=data['criticality'], vendor_type=data['vendor_type'], rel_cat=data['rel_cat'],
            entity_id=self._entity_id(), is_doc=True,status=1)
        if query:
            condition&=Q(document_group__name__icontains=query)
        # list_data = NWisefinList()
        vendor_classobj = Vendorclassification_Mapping.objects.using(self._current_app_schema()).filter(condition
            )[vys_page.get_offset():vys_page.get_query_limit()]
        print(vendor_classobj)
        list_data = NWisefinList()
        for obj in vendor_classobj:
            data_resp = VendorclassficationprofileResponse()
            data_resp.set_document_group(obj.document_group, self._scope())
            list_data.append(data_resp)
        vpage = NWisefinPaginator(vendor_classobj, vys_page.get_index(), 10)
        list_data.set_pagination(vpage)
        return list_data


    def get_questiontype_by_vendorcat(self,data):
        rel_cat=data['rel_cat']
        criticality=data['criticality']
        vendor_type=data['vendor_type']

        ven_obj=Vendorclassification_Mapping.objects.using(self._current_app_schema()).filter(rel_cat=rel_cat,criticality=criticality,vendor_type=vendor_type,status=ModifyStatus.create)
        arr=[]
        for i in ven_obj:
            type_obj=i.type
            data={"name":type_obj.name,"id":type_obj.id}
            arr.append(data)

        return arr