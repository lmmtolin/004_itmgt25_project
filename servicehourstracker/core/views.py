from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import StudentProfile, OrgProfile, OAAProfile

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

        return redirect("index")
    
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