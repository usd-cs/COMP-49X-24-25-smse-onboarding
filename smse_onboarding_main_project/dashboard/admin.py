from django.contrib import admin
from django.contrib.admin import AdminSite

# Customize admin site
admin.site.site_header = "SMSE Administration"
admin.site.site_title = "SMSE Admin Portal"
admin.site.index_title = "Welcome to SMSE Admin Portal"

# Register your models here.
