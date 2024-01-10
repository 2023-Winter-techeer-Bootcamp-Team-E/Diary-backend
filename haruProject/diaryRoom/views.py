from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'template/chat/index.html')


def room(request, diary_id):
    return render(request, "chat/room.html", {"diary_id": diary_id})

