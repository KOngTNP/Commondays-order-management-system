
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, response
from django.urls import reverse
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login


def register(request):
	if request.method == "POST":
		form = RegisterForm(request.POST)
		if form.is_valid():
			form.save()
			data = request.POST
			# get_user = User.objects.get(username = username)
			# get_user_staff = User.objects.filter(username = username).update(is_active = False)
			return HttpResponseRedirect(reverse('mysite:homepage'))
	else:
		form = RegisterForm()

	return render(request, "registration/register.html", {"form":form})


