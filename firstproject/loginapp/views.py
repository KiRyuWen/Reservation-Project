from django.shortcuts import redirect, render
from django.contrib.auth import authenticate
from django.contrib import auth
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
# Create your views here.


def index(request):
    if request.user.is_authenticated:
        name = request.user.username
    return render(request, "index.html", locals())


def login(request):
    if request.method == 'POST':
        name = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=name, password=password)
        if user is not None:
            if user.is_active:
                auth.login(request, user)
                return redirect('/index/')
                message = '登入成功~'
            else:
                message = '帳號尚未啟用'
        else:
            message = '登入失敗!!'
    return render(request, "login.html", locals())


def logout(request):
    auth.logout(request)
    return redirect('/login/')


def rigister(request):

    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login/')  # 重新導向到登入畫面
    context = {
        'form': form
    }

    return render(request, "register.html", context)


class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label="帳號",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label="電子郵件",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label="密碼",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="密碼確認",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
