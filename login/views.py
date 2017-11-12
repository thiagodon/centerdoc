from __future__ import unicode_literals

from django.shortcuts import render
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.views import login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from .forms import SignUpForm

def logout(request, *args, **kwargs):
	kwargs['next_page'] = 'login:login'
	return auth_logout(request, *args, **kwargs)
	
def login(request, *args, **kwargs):
	if request.user.is_authenticated():
		return redirect('ged:home')
	kwargs['extra_context'] = {'next':'/'}
	kwargs['template_name'] = 'login/login.html'
	return auth_login(request, *args, **kwargs)

def signup(request):
	if request.method=='POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			raw_password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=raw_password)
			login(request, user)
			return redirect('login:list')
	else:
			form = SignUpForm()
	return render(request, 'login/user_form.html', {'form': form})

def list(request):
	users = User.objects.filter(is_active=True)
	return render(request, 'login/user_list.html', {'users': users})

def edit(request, pk):
	user = User.objects.get(pk=pk)
	if request.method=='POST':
		form = SignUpForm(request.POST, instance=user)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			raw_password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=raw_password)
			login(request, user)
			return redirect('login:list')
	else:
			form = SignUpForm(instance=user)
	return render(request, 'login/user_form.html', {'form': form})

def delete(request, pk):
	user = User.objects.get(pk=pk)
	user.is_active = False
	user.save()
	return redirect('login:list')