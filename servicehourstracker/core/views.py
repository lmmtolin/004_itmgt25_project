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
    ClassSchedule
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

    search_query = request.GET.get("search", "")
    events = Event.objects.filter(start_datetime__gt=now, approved=True)
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
        if "to_delete_schedule_id" in request.POST:
            schedule_id = request.POST.get("to_delete_schedule_id")
            schedule = ClassSchedule.objects.filter(id=schedule_id, student=student_profile)
            schedule.delete()
            return redirect("student_calendar")
        else:    
            form = ClassScheduleForm(request.POST)
            if form.is_valid():
                schedule = form.save(commit=False)
                schedule.student = student_profile
                schedule.save()
                return redirect("student_calendar")
    WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    schedules = list(student_profile.class_schedules.all())
    schedules.sort(key=lambda s: WEEKDAY_ORDER.index(s.day_of_week))
    context = {"schedules": schedules, "form": form}
    return HttpResponse(template.render(context, request))


def org_dashboard(request):
    return


@login_required
def oaa_dashboard(request):
    user = request.user
    try:
        oaa_profile = user.oaaprofile
    except OAAProfile.DoesNotExist:
        oaa_profile = None
        return redirect("login_view")

    template = loader.get_template("core/oaa_dashboard.html")
    context = {}
    return HttpResponse(template.render(context, request))


@login_required
def oaa_students(request):
    user = request.user
    try:
        oaa_profile = user.oaaprofile
    except OAAProfile.DoesNotExist:
        oaa_profile = None
        return redirect("login_view")
    students = StudentProfile.objects.all()
    template = loader.get_template("core/oaa_students.html")
    context = {"students": students}
    return HttpResponse(template.render(context, request))


@login_required
def oaa_students_detail(request, student_id):
    user = request.user
    try:
        oaa_profile = user.oaaprofile
    except OAAProfile.DoesNotExist:
        oaa_profile = None
        return redirect("login_view")
    student = StudentProfile.objects.get(id=student_id)
    template = loader.get_template("core/oaa_students_detail.html")

    if request.method == "POST":
        submitted_required_service_hours = request.POST["required_service_hours"]
        submitted_penalty_service_hours = request.POST["penalty_service_hours"]
        submitted_completed_service_hours = request.POST["completed_service_hours"]

        student.required_service_hours = submitted_required_service_hours
        student.penalty_service_hours = submitted_penalty_service_hours
        student.completed_service_hours = submitted_completed_service_hours
        student.save()

        context = {"student": student}
        return HttpResponse(template.render(context, request))
    context = {"student": student}
    return HttpResponse(template.render(context, request))


@login_required
def oaa_events(request):
    user = request.user
    try:
        oaa_profile = user.oaaprofile
    except OAAProfile.DoesNotExist:
        oaa_profile = None
        return redirect("login_view")
    template = loader.get_template("core/oaa_events.html")
    events = Event.objects.all()

    search_query = request.GET.get("search", "")
    if search_query:
        events = events.filter(name__icontains=search_query)

    unapproved_only = request.GET.get("unapproved_only") == "on"
    if unapproved_only:
        events = events.filter(approved=False)

    context = {"events": events, "unapproved_only": unapproved_only}
    return HttpResponse(template.render(context, request))


@login_required
def oaa_events_detail(request, event_id):
    user = request.user
    try:
        oaa_profile = user.oaaprofile
    except OAAProfile.DoesNotExist:
        oaa_profile = None
        return redirect("login_view")
    template = loader.get_template("core/oaa_events_detail.html")
    event = Event.objects.get(id=event_id)

    if request.method == "POST":
        event.approved = True
        event.save()
        context = {"event": event}
        return HttpResponse(template.render(context, request))

    context = {"event": event}
    return HttpResponse(template.render(context, request))
