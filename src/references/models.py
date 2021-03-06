from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models


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

    def __str__(self):
        return self.user.username + " is a member of " + self.group.name


class Reference(models.Model):
    name = models.CharField(max_length=200)
    bibtex_dump = JSONField()
    created = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    fulltext = models.TextField(default="", null=True)

    def __str__(self):
        return self.name


class ReferenceType(models.Model):
    name = models.CharField(max_length=200, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ReferenceField(models.Model):
    name = models.CharField(max_length=200)
    referenceType = models.ForeignKey(ReferenceType, on_delete=models.CASCADE)

    def __str__(self):
        return self.referenceType.name + " " + self.name


class ReferenceFile(models.Model):
    pdf = models.FileField(upload_to='papers')
    reference = models.ForeignKey(Reference, on_delete=models.CASCADE)

    def __str__(self):
        return "PDF of " + self.reference.name


class APIKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=32, unique=True)