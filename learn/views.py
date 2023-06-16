from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from django.contrib.auth.models import User
from django.urls import reverse
from django.views import generic, View
from django.http import Http404
from django.contrib.auth import login, logout, authenticate
import logging
logger = logging.getLogger(__name__)

# Create your views here.


class EnrollView(View):
    def post(self, request, *args, **kwargs):
        course_id = kwargs.get('course_id')
        course = get_object_or_404(Course, pk=course_id)
        user = request.user

        is_enrolled = check_if_enrolled(user, course)
        if not is_enrolled and user.is_authenticated:
            # Create an enrollment
            Enrollment.objects.create(user=user, course=course, mode='honor')
            course.total_enrollment += 1
            course.save()

        return HttpResponseRedirect(reverse(viewname='learn:course_details', args=(course.id,)))


class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailsView(generic.DetailView):
    model = Course
    template_name = "learn/course_details.html"


def logout_request(request):
    print("Logout the user `{}`".format(request.user.username))
    logout(request)
    return redirect("learn:index")


class LoginView(View):
    def post(self, request, *args, **kwargs):
        username = request.POST["username"]
        password = request.POST["psw"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("learn:index")
        else:
            return render(request, "learn/user_login.html", {})

    def get(self, request, *args, **kwargs):
        return render(request, "learn/user_login.html", {})


class RegistrationView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "learn/user_registration.html", {})

    def post(self, request, *args, **kwargs):
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
        return redirect("learn:index")


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(
            user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


class ExamResultView(View):
    def post(self, request, *args, **kwargs):
        course_id = kwargs.get('pk')
        course = get_object_or_404(Course, pk=course_id)
        enrollment = course.enrollment_set.get(user=request.user)
        submission = Submission.objects.create(enrollment=enrollment)
        answers = self.extract_answers(request)
        submission.choices.clear()
        for answer in answers:
            choice = get_object_or_404(Choice, pk=answer)
            submission.choices.add(choice)
        return HttpResponseRedirect(reverse(viewname='learn:result', args=(submission.id,)))

    def extract_answers(self, request):
        return [int(v) for k, v in request.POST.items() if k.startswith("choice")]

    def get(self, request, *args, **kwargs):
        submission_id = kwargs.get('pk')
        submission = get_object_or_404(Submission, pk=submission_id)
        choices = submission.choices.all()
        choice_id = [choice.id for choice in choices]
        print(choice_id)
        score = self.calculate_score(submission)
        total_possible_score = self.get_total_possible_score(
            submission.enrollment.course)
        return render(
            request,
            "learn/exam_result.html",
            {
                "course": submission.enrollment.course,
                "selected_choice_ids": choice_id,
                "score": score,
                "total_possible_score": total_possible_score,
                "passed": (score/total_possible_score) > 0.5
            }
        )

    def get_total_possible_score(self, course):
        questions = course.question_set.all()
        total_score = 0
        for question in questions:
            total_score += question.grade
        return total_score

    def calculate_score(self, submission):
        score = 0
        questions = submission.enrollment.course.question_set.all()
        selected_ids = [choice.id for choice in submission.choices.all()]
        for question in questions:
            if question.is_correct(selected_ids):
                score += question.grade
        return score
