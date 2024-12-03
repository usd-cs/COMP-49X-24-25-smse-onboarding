from django.shortcuts import render


def home(request):
    # return HttpResponse("Hello world. You're at the dashboard.")
    return render(request, 'new_hire_dashboard/home.html')
