from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignUpForm

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            if user is not None:
                login(request, user)
                return redirect('post_list')
            else:
                # If authentication fails, log the error
                return render(request, 'registration/signup.html', {'form': form, 'error': 'Authentication failed'})
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})