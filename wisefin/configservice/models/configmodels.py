from django.db import models


class Entity(models.Model):
    name = models.CharField(max_length=256)
    namespace = models.CharField(max_length=64)
    status = models.SmallIntegerField(default=1)


class Application(models.Model):
    name = models.CharField(max_length=256)
    app_path = models.CharField(max_length=64)
    namespace = models.CharField(max_length=64)
    app_type = models.SmallIntegerField(default=1)
    status = models.SmallIntegerField(default=1)


class Schema(models.Model):
    name = models.CharField(max_length=64)
    is_ro = models.BooleanField(default=False)


class AppSpace(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    schema = models.ForeignKey(Schema, on_delete=models.CASCADE)
