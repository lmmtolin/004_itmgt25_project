from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import (
    StudentProfile,
    OrgProfile,
    OAAProfile,
    Event,
    Participation,
    ClassScheduleForm,
)
from django.utils import timezone


def login_view(request):
    if request.method == "GET":
        template = loader.get_template("core/login_view.html")
        return HttpResponse(template.render({}, request))

    elif request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password.")
            return redirect(request.path_info)

        actual_user_type = None
        if hasattr(user, "studentprofile"):
            actual_user_type = "Student"
        elif hasattr(user, "orgprofile"):
            actual_user_type = "Organization"
        elif hasattr(user, "oaaprofile"):
            actual_user_type = "OAA"

        login(request, user)

        # Redirect to user-type-specific dashboard
        if actual_user_type == "Student":
            return redirect("student_dashboard")
        elif actual_user_type == "Organization":
            return redirect("org_dashboard")
        elif actual_user_type == "OAA":
            return redirect("oaa_dashboard")

        return redirect("")


def register_view(request):
    if request.method == "GET":
        template = loader.get_template("core/register_view.html")
        return HttpResponse(template.render({}, request))

    elif request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user_type = request.POST.get("user_type")

        user = User.objects.create_user(username=username, password=password)

        if user_type == "Student":
            StudentProfile.objects.create(
                user=user,
                id_number=request.POST.get("id_number"),
            )
        elif user_type == "Organization":
            OrgProfile.objects.create(
                user=user,
                name=request.POST.get("name"),
            )
        elif user_type == "OAA":
            OAAProfile.objects.create(
                user=user,
            )
        else:
            user.delete()
            messages.error(request, "Invalid user type.")
            return redirect(request.path_info)

        messages.success(request, "Registration successful! Please log in.")
        return redirect("login_view")


@login_required
def student_dashboard(request):
    user = request.user

    try:
        student_profile = user.studentprofile
    except StudentProfile.DoesNotExist:
        student_profile = None
        return redirect("login_view")
    volunteered_events = student_profile.events.all()

    context = {"student": student_profile, "events": volunteered_events}
    
    if request.method == "GET":
        template = loader.get_template("core/student_dashboard.html")
        return HttpResponse(template.render(context, request))


@login_required
def student_opportunities(request):
    user = request.user
    try:
        student_profile = user.studentprofile
    except StudentProfile.DoesNotExist:
        student_profile = None
        return redirect("login_view")

    now = timezone.now()
    events = Event.objects.filter(start_datetime__gt=now)

    search_query = request.GET.get("search", "")
    events = Event.objects.filter(start_datetime__gt=now)
    if search_query:
        events = events.filter(name__icontains=search_query)

    user_event_status = {}

    filter_conflicts = request.GET.get("filter_conflicts") == "on"

    if filter_conflicts:
        student_classes = student_profile.class_schedules.all()
        filtered_events = []
        for event in events:
            has_conflict = False
            for schedule in student_classes:
                if schedule.day_of_week == event.start_datetime.strftime("%A"):
                    event_start = event.start_datetime.time()
                    event_end = event.end_datetime.time()
                    if (
                        schedule.start_time < event_end
                        and schedule.end_time > event_start
                    ):
                        has_conflict = True
                        break
            if not has_conflict:
                filtered_events.append(event)
        events = filtered_events

    for event in events:
        user_event_status[event.id] = event.is_user_in_event(user)

    context = {
        "student": student_profile,
        "events": events,
        "user_event_status": user_event_status,
        "search_query": search_query,
        "filter_conflicts": filter_conflicts,
    }

    if request.method == "GET":
        template = loader.get_template("core/student_opportunities.html")
        return HttpResponse(template.render(context, request))


@login_required
def student_opportunities_details(request, event_id):
    user = request.user

    try:
        student_profile = user.studentprofile
    except StudentProfile.DoesNotExist:
        student_profile = None
        return redirect("login_view")

    event = Event.objects.get(id=event_id)
    user_event_status = event.is_user_in_event(user)

    context = {
        "student": student_profile,
        "event": event,
        "user_event_status": user_event_status,
    }

    if request.method == "GET":
        template = loader.get_template("core/student_opportunities_details.html")
        return HttpResponse(template.render(context, request))
    elif request.method == "POST":
        participation = Participation(student=student_profile, event=event)
        participation.save()
        return redirect("student_opportunities")


@login_required
def student_calendar(request):
    user = request.user
    try:
        student_profile = user.studentprofile
    except StudentProfile.DoesNotExist:
        student_profile = None
        return redirect("login_view")

    template = loader.get_template("core/student_calendar.html")
    form = ClassScheduleForm()

    if request.method == "POST":
        form = ClassScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.student = student_profile
            schedule.save()
            return redirect("student_calendar")

    context = {"schedules": student_profile.class_schedules.all(), "form": form}
    return HttpResponse(template.render(context, request))


def org_dashboard(request):
    return


def oaa_dashboard(request):
    return
