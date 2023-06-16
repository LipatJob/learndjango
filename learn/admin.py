from django.contrib import admin

# Register your models here.
from .models import *


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 5


class QuestionsInLine(admin.StackedInline):
    list_display = ['text']
    model = Question
    extra = 2
    show_change_link = True


class CourseAdmin(admin.ModelAdmin):
    fields = ['pub_date', 'name', 'description']
    inlines = [LessonInline, QuestionsInLine]


class InstructorAdmin(admin.ModelAdmin):
    fields = ["user", "full_time"]


class LessonAdmin(admin.ModelAdmin):
    list_display = ['title']
    fields = ['course', 'title', 'order', 'content']


class ChoiceInline(admin.StackedInline):
    list_display = ['text']
    model = Choice
    extra = 2


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text']
    inlines = [ChoiceInline]


admin.site.register(Course, CourseAdmin)
admin.site.register(Instructor, InstructorAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)

