from django.shortcuts import render


# Create your views here.
def custom_404(request, exception=None):
    return render(request, '404.html')


def custom_500(request):
    return render(request, '500.html')