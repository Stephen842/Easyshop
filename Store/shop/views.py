from django.shortcuts import render

# Create your views here.
def home(request):
    context = {
        'title': 'Elvix Luxe – Fashion That Inspires Confidence',
    }
    return render(request, 'pages/store.html', context)