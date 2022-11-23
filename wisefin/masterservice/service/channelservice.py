import traceback

from django.db import IntegrityError
from django.db.models import Q
from django.utils.timezone import now

from masterservice.models import Channel
from masterservice.data.response.channelresponse import ChannelResponse
from masterservice.service.Codegenerator import CodeGen
from masterservice.util.masterutil import ModifyStatus, Code_Gen_Type, Code_Gen_Value
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone

from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class ChannelService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_documenttype(self, cha_obj, user_id):
        if not cha_obj.get_id() is None:
            try:
                logger.error('CHANNEL: Channel Update Started')
                Channel_var = Channel.objects.using(self._current_app_schema()).filter(id=cha_obj.get_id(),
                                                                                       entity_id=self._entity_id()).update(
                    # code=cha_obj.get_code(),
                    name=cha_obj.get_name(),
                    updated_by=user_id,
                    updated_date=timezone.now())
                Channel_var = Channel.objects.using(self._current_app_schema()).get(id=cha_obj.get_id(),
                                                                                    entity_id=self._entity_id())
                logger.error('CHANNEL: Channel Update Success' + str(Channel_var))
            except IntegrityError as error:
                logger.error('ERROR_Channel_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Channel.DoesNotExist:
                logger.error('ERROR_Channel_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CHANNEL_ID)
                error_obj.set_description(ErrorDescription.INVALID_CHANNEL_ID)
                return error_obj
            except:
                logger.error('ERROR_Channel_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            condition = Q(name__exact=cha_obj.get_name()) & Q(entity_id=self._entity_id())
            channel = Channel.objects.using(self._current_app_schema()).filter(condition)
            if len(channel) > 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CHANNEL_ID)
                error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                return error_obj
            try:
                logger.error('CHANNEL: Channel Creation Started')
                Channel_var = Channel.objects.using(self._current_app_schema()).create(  # code=cha_obj.get_code(),
                    name=cha_obj.get_name(),
                    created_by=user_id, entity_id=self._entity_id())
                try:
                    max_cat_code = Channel.objects.using(self._current_app_schema()).filter(code__icontains='ICNL').order_by('-code')[0].code
                    rnsl = int(max_cat_code[4:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "ICNL" + str(new_rnsl).zfill(3)# code = "ISCT" + str(channel_code)

                Channel_var.code = code
                Channel_var.save()
                logger.error('CHANNEL: Channel Creation Success' + str(Channel_var))
            except IntegrityError as error:
                logger.error('ERROR_Channel_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_Channel_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        channel_data = ChannelResponse()
        channel_data.set_id(Channel_var.id)
        channel_data.set_code(Channel_var.code)
        channel_data.set_name(Channel_var.name)
        channel_data.set_status(Channel_var.status)
        channel_data.set_created_by(Channel_var.created_by)
        channel_data.set_updated_by(Channel_var.updated_by)
        return channel_data

    def fetchchannel(self, channel_id):
        try:
            Channel_var = Channel.objects.using(self._current_app_schema()).get(id=channel_id,
                                                                                entity_id=self._entity_id())
            channel_data = ChannelResponse()
            channel_data.set_id(Channel_var.id)
            channel_data.set_code(Channel_var.code)
            channel_data.set_name(Channel_var.name)
            channel_data.set_status(Channel_var.status)
            channel_data.set_created_by(Channel_var.created_by)
            channel_data.set_updated_by(Channel_var.updated_by)
            return channel_data
        except Channel.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DOCTYPE_ID)
            error_obj.set_description(ErrorDescription.INVALID_DOCTYPE_ID)
            return error_obj

    def fetch_channel_list(self, vys_page, query):
        if query is None:
            ChannelList = Channel.objects.using(self._current_app_schema()).filter(status=1,
                                                                                   entity_id=self._entity_id())[
                          vys_page.get_offset():vys_page.get_query_limit()]
        else:
            condition = Q(name__icontains=query) & Q(entity_id=self._entity_id())
            ChannelList = Channel.objects.using(self._current_app_schema()).filter(condition)[
                          vys_page.get_offset():vys_page.get_query_limit()]

        list_length = len(ChannelList)
        cat_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for Channel_var in ChannelList:
                channel_data = ChannelResponse()
                channel_data.set_id(Channel_var.id)
                channel_data.set_code(Channel_var.code)
                channel_data.set_name(Channel_var.name)
                channel_data.set_status(Channel_var.status)
                channel_data.set_created_by(Channel_var.created_by)
                channel_data.set_updated_by(Channel_var.updated_by)
                cat_list_data.append(channel_data)
            vpage = NWisefinPaginator(ChannelList, vys_page.get_index(), 10)
            cat_list_data.set_pagination(vpage)
        return cat_list_data

    def delete_channel(self, channel_id, user_id):
        Channel_var = Channel.objects.using(self._current_app_schema()).filter(id=channel_id,
                                                                               entity_id=self._entity_id()).update(
            status=ModifyStatus.delete,
            updated_by=user_id,
            updated_date=now())

        if Channel_var == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_CHANNEL_ID)
            error_obj.set_description(ErrorDescription.INVALID_CHANNEL_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def search_channel(self, request, query, vys_page):
        condition = None
        if query is not None:
            condition = (Q(name__icontains=query) | Q(code__icontains=query)) & Q(entity_id=self._entity_id())
        channelList = None
        if condition is not None:
            channelList = Channel.objects.using(self._current_app_schema()).values('id', 'name', 'code').filter(
                condition)[
                          vys_page.get_offset():vys_page.get_query_limit()]
        else:
            channelList = Channel.objects.using(self._current_app_schema()).values('id', 'name', 'code').filter(
                entity_id=self._entity_id())[
                          vys_page.get_offset():vys_page.get_query_limit()]
        vlist = NWisefinList()
        for chl in channelList:
            channel_res = ChannelResponse()
            disp_name = '(' + chl['code'] + ') ' + chl['name']
            channel_res.set_name(disp_name)
            channel_res.set_id(chl['id'])
            channel_res.set_name(chl['name'])
            vlist.append(channel_res)
        vpage = NWisefinPaginator(channelList, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist

    #summarysearch inward
    def channel_summarysearch(self, query, vys_page):
        if query is None:
            condition = Q(status=1)
        else:
            print(query)
            condition = Q(name__icontains=query["name"]) & Q(code__icontains=query["code"]) & Q(status=1)

        channellist = Channel.objects.using(self._current_app_schema()).filter(condition)[
                      vys_page.get_offset(): vys_page.get_query_limit()]
        list_length = len(channellist)
        channel_list_data = NWisefinList()
        if list_length > 0:
            for channelobj in channellist:
                channel_data = ChannelResponse()
                channel_data.set_id(channelobj.id)
                channel_data.set_code(channelobj.code)
                channel_data.set_name(channelobj.name)
                channel_list_data.append(channel_data)
            vpage = NWisefinPaginator(channellist, vys_page.get_index(), 10)
            channel_list_data.set_pagination(vpage)
        return channel_list_data

    #dropdown inward
    def channel_search(self, query, vys_page):
        if query is None:
            condition = Q(status=1)
        else:
            condition = Q(name__icontains=query) & Q(status=1)
        channelList = Channel.objects.using(self._current_app_schema()).filter(condition).values('id', 'name', 'code').order_by('-created_date')[
                      vys_page.get_offset():vys_page.get_query_limit()]
        vlist = NWisefinList()
        list_length = len(channelList)
        if list_length > 0:
            for cou in channelList:
                channel_res = ChannelResponse()
                channel_res.set_id(cou['id'])
                channel_res.set_name(cou['name'])
                channel_res.set_code(cou['code'])
                vlist.append(channel_res)
            vpage = NWisefinPaginator(channelList, vys_page.get_index(), 10)
            vlist.set_pagination(vpage)
        return vlist

    def get_channel(self, channel_data):
        channelIdarr = channel_data.get('channel_id')
        channel = Channel.objects.using(self._current_app_schema()).filter(id__in=channelIdarr).values('id', 'code', 'name')
        channel_list_data = NWisefinList()
        for i in channel:
            data = {"id": i['id'],
                    "code": i['code'],
                    "name": i['name']}
            channel_list_data.append(data)
        return channel_list_data.get()

    def fetch_channeldata(self, channel_id):
        channel = Channel.objects.using(self._current_app_schema()).get(id=channel_id)
        cou_data = {"id": channel.id, "code": channel.code, "name": channel.name}
        return cou_data
