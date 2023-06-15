from django.shortcuts import render
from .models import Course

# Create your views here.
def course_list(request):
    course = Course.objects.get(pk=1)
    template = course.name
    return HttpResponse(content=template)