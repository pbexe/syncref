from django.contrib import admin

from .models import Group, GroupMembership, Reference, ReferenceType, ReferenceField, ReferenceFile

# Register the releveant models with the admin interface
admin.site.register(Group)
admin.site.register(GroupMembership)
admin.site.register(Reference)
admin.site.register(ReferenceType)
admin.site.register(ReferenceField)
admin.site.register(ReferenceFile)
