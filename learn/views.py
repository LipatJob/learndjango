from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from .models import Course, Lesson, Enrollment
from django.urls import reverse
from django.views import generic, View
from django.http import Http404

# Create your views here.


# def course_list(request):
#     course = Course.objects.get(pk=1)
#     template = course.name
#     return HttpResponse(content=template)


# def popular_course_list(request):
#     context = {}
#     if request.method == "GET":
#         course_list = Course.objects.order_by("-total_enrollment")[:10]
#         context["course_list"] = course_list
#         return render(request, "learn/course_list.html", context=context)


# def enroll(request, course_id):
#     if request.method == "POST":
#         course = get_object_or_404(Course, pk=course_id)
#         course.total_enrollment += 1
#         course.save()
#         return HttpResponseRedirect(reverse(viewname='learn:course_details', args=(course.id,)))


# def course_details(request, course_id):
#     context = {}
#     if request.method == "GET":
#         try:
#             course = Course.objects.get(pk=course_id)
#             context["course"] = course
#             return render(request, "learn/course_details.html", context=context)
#         except Course.DoesNotExist:
#             raise Http404("No course matches the given id.")


# class CourseListView(View):
#     def get(self, request):
#         context = {}
#         course_list = Course.objects.order_by('-total_enrollment')[:10]
#         context['course_list'] = course_list
#         return render(request, 'learn/course_list.html', context)

class EnrollView(View):
    def post(self, request, *args, **kwargs):
        course_id = kwargs.get('course_id')
        course = get_object_or_404(Course, pk=course_id)
        course.total_enrollment += 1
        course.save()
        return HttpResponseRedirect(reverse(viewname='learn:course_details', args=(course.id,)))

# class CourseDetailsView(View):
#     def get(self, request, *args, **kwargs):
#         context = {}
#         course_id = kwargs.get("course_id")
#         try:
#             course = Course.objects.get(pk=course_id)
#             context['course'] = course
#             return render(request, 'learn/course_details.html', context)
#         except Course.DoesNotExist:
#             raise Http404("No course matches the given id.")

class CourseListView(generic.ListView):
    template_name = "learn/course_list.html"
    context_object_name = "course_list"

    def get_queryset(self):
        courses = Course.objects.order_by("-total_enrollment")[:10]
        return courses

class CourseDetailsView(generic.DetailView):
    model = Course
    template_name = "learn/course_details.html"