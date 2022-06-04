from django.contrib import admin


class AppAdmin(admin.ModelAdmin):
    list_per_page = 15
    ordering = ("-created_at",)
