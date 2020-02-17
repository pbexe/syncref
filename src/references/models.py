from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User


class Group(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class GroupMembership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)


class Reference(models.Model):
    name = models.CharField(max_length=200)
    bibtex_dump = JSONField()
    created = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class ReferenceType(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    

class ReferenceField(models.Model):
    name = models.CharField(max_length=200)
    referenceType = models.ForeignKey(ReferenceType, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.type_.name + " " + self.name