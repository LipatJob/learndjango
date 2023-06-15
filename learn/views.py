from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from .models import Course, Lesson, Enrollment
from django.contrib.auth.models import User
from django.urls import reverse
from django.views import generic, View
from django.http import Http404
from django.contrib.auth import login, logout, authenticate
import logging
logger = logging.getLogger(__name__)

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


def logout_request(request):
    print("Logout the user `{}`".format(request.user.username))
    logout(request)
    return redirect("learn:popular_course_list")


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["psw"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("learn:popular_course_list")
        else:
            return render(request, "learn/user_login.html", context)
    else:
        return render(request, 'learn/user_login.html', context)


def registration_request(request):
    context = {}
    if request.method == "GET":
        return render(request, "learn/user_registration.html", context)
    elif request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            user.save()
            login(request, user)
        return redirect("learn:popular_course_list")
    else:
        return render(request, "learn/user_registration.html", context)
