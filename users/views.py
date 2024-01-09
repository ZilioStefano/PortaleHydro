from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from users.forms import LoginForm
from django.contrib import messages


def log_in(request):

    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'users/login.html', {'form': form})

    elif request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f'Sei entrato come {username.title()}')
                return redirect('view_portate-home')

        # form is not valid or user is not authenticated
        messages.error(request, f'Password/username errati')
        return render(request, 'users/login.html', {'form': form})

def log_out(request):
    logout(request)
    messages.success(request, f'Sei stato disconnesso.')
    return redirect('login')