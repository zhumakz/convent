from django.contrib import admin
from .models import Lecture, LectureAttendance

class LectureAdmin(admin.ModelAdmin):
    list_display = ('title', 'speakers', 'date', 'location')
    actions = ['generate_qr_codes']

    def generate_qr_codes(self, request, queryset):
        for lecture in queryset:
            lecture.generate_qr_code_start()
            lecture.generate_qr_code_end()
            lecture.save()
        self.message_user(request, "QR codes generated successfully.")
    generate_qr_codes.short_description = "Generate QR codes for selected lectures"

admin.site.register(Lecture, LectureAdmin)
admin.site.register(LectureAttendance)
