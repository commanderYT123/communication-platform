from django.shortcuts import render, redirect
from .models import Room, Topic, Message, User
from .forms import RoomFrom, UserForm, MyUserCreationForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout

# Create your views here.


def loginPage(request):
    page = "login"
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "user is not exist")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            messages.error(request, "email or password does not exist")
    context = {"page": page}
    return render(request, "communityApp/login.html", context)


def logoutUser(request):
    logout(request)
    return redirect("index")


def registerPage(request):
    page = "register"
    form = MyUserCreationForm()
    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("index")
        else:
            messages.error(request, "an error occured during registration")
    context = {"page": page, "form": form}
    return render(request, "communityApp/login.html", context)


def index(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)
    )
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    roomMessages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {
        "rooms": rooms,
        "topics": topics,
        "room_count": room_count,
        "roomMessages": roomMessages,
    }
    return render(request, "communityApp/index.html", context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    roomMessages = room.message_set.all().order_by("-created")
    participants = room.participants.all()
    participantsCount = participants.count()
    if request.method == "POST":
        message = Message.objects.create(
            user=request.user, room=room, body=request.POST.get("body")
        )
        return redirect("room", pk=room.id)
    context = {
        "rooms": room,
        "roomMessages": roomMessages,
        "participants": participants,
        "participantsCount": participantsCount,
    }
    room.participants.add(request.user)
    return render(request, "communityApp/room.html", context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    roomMessage = user.message_set.all()
    topics = Topic.objects.all()
    context = {
        "user": user,
        "rooms": rooms,
        "roomMessages": roomMessage,
        "topics": topics,
    }
    return render(request, "communityApp/profile.html", context)


@login_required(login_url="login")
def createRoom(request):
    topics = Topic.objects.all()
    form = RoomFrom()
    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get("name"),
            description=request.POST.get("description"),
        )
        return redirect("index")
    context = {"form": form, "topics": topics}
    return render(request, "communityApp/form room.html", context)


def updateRoom(request, pk):
    topics = Topic.objects.all()
    room = Room.objects.get(id=pk)
    form = RoomFrom(instance=room)
    if request.user != room.host:
        return HttpResponse("you are not allowed here !!")
    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get("name")
        room.topic = topic
        room.description = request.POST.get("description")
        room.save()
        return redirect("index")
    context = {"form": form, "topics": topics, "room": room}
    return render(request, "communityApp/form room.html", context)


def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse("you are not allowed here !!")
    if request.method == "POST":
        room.delete()
        return redirect("index")
    context = {"object": room}
    return render(request, "communityApp/delete.html", context)


def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse("you are not allowed here !!")
    if request.method == "POST":
        message.delete()
        return redirect("index")
    context = {
        "object": message,
    }
    return render(request, "communityApp/delete.html", context)


@login_required(login_url="login")
def updateUser(request):
    user = request.user
    form = UserForm(instance=request.user)
    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user-profile", pk=user.id)
    context = {"user": user, "form": form}
    return render(request, "communityApp/update user.html", context)


def topicsPages(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    topics = Topic.objects.filter(name__icontains=q)
    context = {"topics": topics}
    return render(request, "communityApp/topics_pages.html", context)


def activityPages(request):
    roomMessages = Message.objects.all()
    context = {"roomMessages": roomMessages}
    return render(request, "communityApp/activity_pages.html", context)
