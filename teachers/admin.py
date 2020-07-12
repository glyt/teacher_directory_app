from django.contrib import admin
from .models import Teacher, Subject


class TeacherAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject')


admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Subject, SubjectAdmin)


