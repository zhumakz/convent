from django.contrib import admin
from .models import Lecture, LectureAttendance


@admin.action(description='Generate QR codes for selected lectures')
def generate_qr_codes(modeladmin, request, queryset):
    for lecture in queryset:
        lecture.generate_qr_code_start()
        lecture.generate_qr_code_end()
        lecture.save()


class LectureAdmin(admin.ModelAdmin):
    list_display = ('title', 'speakers', 'date', 'location')
    actions = [generate_qr_codes]


admin.site.register(Lecture, LectureAdmin)


class LectureAttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'lecture', 'start_scanned', 'end_scanned', 'start_time', 'end_time')


admin.site.register(LectureAttendance, LectureAttendanceAdmin)
