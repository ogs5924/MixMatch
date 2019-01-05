import json
import datetime
from typing import List, Dict

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from .forms import SignUpForm as UserCreationForm
from .models import PendingRequest, Hobby, Message, User
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.


@login_required(login_url='login')
def home(request):
    user: User = request.user  # using type-hinting to force PyCharm to give template variable hints.
    return render(request, 'mainapp/home.html', {'user': user, 'hobbies': Hobby.objects.all()})


def register(request):
    """
    Creates a new user from the information given. Since the User Model is made by extended the Django User Model,
    the password is automatically hashed by a Django PasswordHasher. The new user is only added into the database if
    the form details are valid and if the username is unique.
    :param request:
    :return:
    """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            # img = request.FILES['imgInp']
            email = form.cleaned_data.get('email')
            raw_pass = form.cleaned_data.get('password1')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            gender = form.cleaned_data.get('gender')
            dob = form.cleaned_data.get('dob')
            user = authenticate(username=username, email=email, password=raw_pass, first_name=first_name,
                                last_name=last_name, gender=gender, dob=dob)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'mainapp/register.html', context={'form': form})


def see_users_with_hobby(request, id):
    hobby = Hobby.objects.get(pk=id);    users = hobby.users.all()
    user: User = request.user  # using type-hinting to force PyCharm to give template variable hints.
    return render(request, 'mainapp/all_user_view.html',
                  context={'user': user, 'users': users, 'title': f"Users with {hobby.name} hobby"})


@login_required(login_url='login')
def user_profile(request):
    user: User = request.user
    return render(request, 'mainapp/profile_view.html', {'user': user})


@login_required(login_url='login')
def see_all_friends(request):
    user: User = request.user  # using type-hinting to force PyCharm to give template variable hints.
    friends = user.friends.all()
    return render(request, 'mainapp/all_user_view.html',
                  context={'user': user, 'users': friends, 'title': f"{user.username} Friends"})


@login_required(login_url='login')
def see_a_message(request, id):
    user: User = request.user  # using type-hinting to force PyCharm to give template variable hints.
    msg = Message.objects.get(pk=id)  # pk shouldn't raise an error ... it's unique
    return render(request, 'mainapp/message_view.html', context={'user': user, 'msg': msg})


@login_required(login_url='login')
def see_all(request):
    user: User = request.user  # using type-hinting to force PyCharm to give template variable hints.
    return render(request, 'mainapp/all_user_view.html',
                  context={'user': user, 'users': User.objects.all(), 'title': "All users"})


# ----- AJAX PROCESSING -----


def ajax_filter_users(request):
    if request.is_ajax():
        gender = request.GET.get("gender")
        min_age = request.GET.get("min_age")
        max_age = request.GET.get("max_age")
        if gender is not None:
            users = User.objects.filter(gender=gender)
        else:
            users = User.objects.all()
        results: Dict[User] = []
        if min_age is not None:
            for u in users:
                birth_year = u.dob.year
                this_year = datetime.datetime.now().year
                min_year = this_year - min_age
                max_year = this_year - max_age
                if min_year >= birth_year >= max_year:
                    results[u.id] = u
        return JsonResponse({"users": results})


def ajax_send_friend_request(request):
    if request.is_ajax() and request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        recipient_id = data["recipient"] if "recipient" in data else None
        user: User = request.user
        if user.is_authenticated:
            recipient = User.objects.get(pk=recipient_id)
            if recipient is None:
                response = JsonResponse({"error": "recipient cannot be found!"})
                response.status_code = 403  # To announce that the user isn't allowed to publish
                return response
            try:
                PendingRequest.objects.get(sender=user, recipient=recipient)
                response = JsonResponse({"error": "Already sent a request to this user"})
                response.status_code = 403  # To announce that the user isn't allowed to publish
                return response
            except ObjectDoesNotExist:
                req = PendingRequest(sender=user, recipient=recipient)
                req.save()
                return JsonResponse({"msg": "Success"})
        else:
            response = JsonResponse({"error": "Must be authenticated"})
            response.status_code = 403  # To announce that the user isn't allowed to publish
            return response


def ajax_answer_friend_request(request):
    if request.is_ajax() and request.method == "PUT":
        data = json.loads(request.body.decode('utf-8'))
        answer = data["answer"] if "answer" in data else None
        req = PendingRequest.objects.get(pk=data["req_id"])
        req.respond(True if answer == "True" else False)
        response = JsonResponse({"msg": "Success"})
        response.status_code = 200
        return response


def ajax_add_hobby(request):
    if request.is_ajax():
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            hobby_id = data['hobby_id']
            user: User = request.user
            user.hobbies.add(Hobby.objects.get(pk=hobby_id))
            return JsonResponse({"msg": "Success"})


def ajax_remove_hobby(request):
    if request.is_ajax():
        if request.method == "DELETE":
            data = json.loads(request.body.decode('utf-8'))
            hobby_id = data['hobby_id']
            user: User = request.user
            user.hobbies.remove(Hobby.objects.get(pk=hobby_id))
            return JsonResponse({"msg": "Success"})


def ajax_send_message(request):
    if request.is_ajax():
        if request.method == "POST":
            # data = json.loads(request.body.decode('utf-8'))
            # content = data["content"]
            content = request.POST.get("content")
            recipient_id = request.POST.get("recipient")
            recipient = User.objects.get(pk=recipient_id)
            msg = Message(sender=request.user, recipient=recipient, content=content)
            try:
                msg.save()
                return JsonResponse({"msg": "Success"})
            except ValueError:
                response = JsonResponse({"error": "Error sending message"})
                response.status_code = 403  # To announce that the user isn't allowed to publish
                return response


def ajax_update_details(request):
    """
    User will make a request to update their personal details via the 'Profile' page.
    The request will be made as an AJAX POST request and sent here where the data provided is used to
    update their respective User object into the database.
    :param request: Latest request made
    :return: JsonResponse
    """
    if request.is_ajax():
        if request.method == "PUT":
            # Strip the data
            data = json.loads(request.body.decode('utf-8'))
            first_name = data['first_name']
            last_name = data['last_name']
            username = data['username']
            email = data['email']

            # Retrieve user object
            user = User.objects.get(username=username)

            # Update user object
            user.first_name = first_name
            user.last_name = last_name
            user.email = email

            # Save user object
            user.save()
            return JsonResponse({"result": True})


# ----- HELPERS -----


def _add_user_to_context(request, context) -> dict:
    user: User = request.user  # using type-hinting to force PyCharm to give template variable hints.
    context["user"] = user
    return context
