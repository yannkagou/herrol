from django.shortcuts import render

def home_view(request):
    hello = "Hello World, I'm Herrol"
    return render(request, 'core/index.html', {'hello': hello})
