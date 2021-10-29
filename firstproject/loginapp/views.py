from django.shortcuts import redirect, render
from django.contrib.auth import authenticate
from django.contrib import auth
from django.http import HttpResponse
from django.contrib.auth.models import User

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        name=request.user.username
    return render(request,"index.html",locals())

def login(request):
    if request.method =='POST':
        name=request.POST['username']
        password=request.POST['password']
        user = authenticate(username=name,password=password)
        if user is not None:
            if user.is_active:
                auth.login(request,user)
                return redirect('/index/')
                message = '登入成功~'
            else:
                message = '帳號尚未啟用'
        else:
            message = '登入失敗!!'
    return render(request,"login.html",locals())

def logout(request):
    auth.logout(request)
    return redirect('/index/')

