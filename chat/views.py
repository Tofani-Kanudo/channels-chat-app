from django.shortcuts import render

# Create your views here.


def chat_list(request):
    return render(request, 'chat_list.html', {})


def chat(request, code):
    return render(request, 'chatroom.html', {'chatroom': code})