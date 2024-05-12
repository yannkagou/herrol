from django.shortcuts import render

def home_view(request):
    hello = "Hello World, I'm Herrol"
    return render(request, 'core/index.html', {'hello': hello})

def graph_view(request):
    hello = "Hello World Graph, I'm Herrol"
    return render(request, 'core/graph.html', {'hello': hello})

def files_view(request):
    hello = "Hello World Files, I'm Herrol"
    return render(request, 'core/files.html', {'hello': hello})

def notif_view(request):
    hello = "Hello World Notifications, I'm Herrol"
    return render(request, 'core/notif.html', {'hello': hello})
