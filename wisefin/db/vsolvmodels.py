from django.core.management import call_command
from django.db import connection, models
import inspect
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

class VSolvQueryset(models.QuerySet):

    def delete(self):
        counter, counter_dict = 0, {}
        for obj in self:
            result = obj.delete()
            if result is not None:
                current_counter, current_counter_dict = result
                counter += current_counter
                counter_dict.update(current_counter_dict)
        if counter:
            return counter, counter_dict


class VsolvModels(models.Model):
    auto_drop_schema = False
    auto_create_schema = True
    entity_id = models.BigIntegerField(null=True)
    objects = VSolvQueryset.as_manager()
    scope = None

    class Meta:
        abstract = True

    def save(self, verbosity=1, *args, **kwargs):
        super(VsolvModels, self).save(*args, **kwargs)

    def delete(self, force_drop=False, *args, **kwargs):
        return super(VsolvModels, self).delete(*args, **kwargs)
    
    
class VQuerySet(models.QuerySet):
    def get_request(self):
        name = 'request'
        for f in inspect.stack():
            if name in f[0].f_locals: return f[0].f_locals[name]
        return None

    # def get_entity_id(self):
    #     request = self.get_request()
    #     print(request)
    #     print("filter port")
    #     entity_id = request.scope['entity_id']
    #     print(entity_id)
    #     return entity_id

    def get_entity_id(self):
        request = self.get_request()

        entity_id = request.GET.get('entity_id')
        if entity_id != None:
            return entity_id
        class DbGet(NWisefinThread):
            app_name_space=self.get_name_appnamespace()
            def __init__(self, scope):
                super().__init__(scope)
                self._set_namespace(self.app_name_space)
            def get_entity(self):
                return self._entity_id()
        entity_get = DbGet(request.scope)
        return entity_get.get_entity()

    def get_name_appnamespace(self):
        app_label=self.model._meta.app_label
        appspace_keys=ApplicationNamespace.__dict__.keys()
        appspace_vals=ApplicationNamespace.__dict__.values()
        if app_label in appspace_vals:
            ind=list(appspace_vals).index(app_label)
            return list(appspace_keys)[ind]


    def get(self, *args, **kwargs):
        entity_id = self.get_entity_id()
        return super().get(*args, **dict(kwargs, entity_id=entity_id))

    def filter(self, *args, **kwargs):
        entity_id = self.get_entity_id()
        return super().filter(*args, **dict(kwargs, entity_id=entity_id))

    def latest(self, *args, **kwargs):
        latest_fields = []
        for fields in args:
            latest_fields.append('-' + fields)
        return self.filter().order_by(*latest_fields)[0]

    def earliest(self, *args, **kwargs):
        earliest_fields = []
        for fields in args:
            earliest_fields.append(fields)
        return self.filter().order_by(*earliest_fields)[0]

    def first(self, *args, **kwargs):
        self.filter()
        return super().first()

    def last(self, *args, **kwargs):
        self.filter()
        return super().last()

    def create(self, *args, **kwargs):
        entity_id = self.get_entity_id()
        return super().create(*args, **dict(kwargs, entity_id=entity_id))

    def bulk_create(self, *args, **kwargs):
        entity_id = self.get_entity_id()
        for objs in args:
            if isinstance(objs, list):
                for record in objs:
                    record.__dict__['entity_id'] = entity_id
        return super().bulk_create(*args, **kwargs)

    def bulk_update(self, *args, **kwargs):
        entity_id = self.get_entity_id()
        for objs in args:
            if isinstance(objs, list):
                for record in objs:
                    record.__dict__['entity_id'] = entity_id
        return super().bulk_update(*args, **kwargs)

    def get_or_create(self, *args, **kwargs):
        entity_id = self.get_entity_id()
        return super().get_or_create(*args, **dict(kwargs, entity_id=entity_id))

    def update_or_create(self, *args, **kwargs):
        entity_id = self.get_entity_id()
        return super().update_or_create(*args, **dict(kwargs, entity_id=entity_id))


class Vmanager(models.Manager):
    def get_queryset(self):
        req= super().get_queryset()
        return VQuerySet(self.model, using=self._db)


class VModels(models.Model):
    entity_id = models.BigIntegerField(null=True)
    objects = Vmanager()

    class Meta:
        abstract = True