from django.shortcuts import redirect, render
from django.contrib.auth import authenticate
from django.contrib import auth
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms

from loginapp.models import customer, Book, Room
import datetime
# Create your views here.


def listall(request):
    customers = customer.objects.all().order_by('cName')
    return render(request, "listall.html", locals())


def index(request):
    # if request.user.is_authenticated:
    #    name = request.user.username

    time_choice = Book.time_choice

    room_list = Room.objects.all()
    name = request.user.username
    # 当天
    date = datetime.datetime.now().date()  # 年月日  datefield = datetime.datetime()
    book_date = request.GET.get('book_date', date)
    book_list = Book.objects.filter(date=book_date)

    print('book_list', book_list)
    htmls = ""
    for room in room_list:
        htmls += "<tr><td>" + room.rName + "(" + str(room.num) + ")</td>"
        for time in time_choice:

            flag = False
            for book in book_list:
                if book.room.pk == room.pk and book.time_id == time[0]:
                    # 意味这个单元格已被预定
                    flag = True
                    break

            if flag:
                if request.user.pk == book.user.pk:
                    htmls += "<td class='active item' room_id=" + str(room.pk) + " time_id=" + str(
                        time[0]) + ">" + book.user.cName + "</td>"
                else:
                    htmls += "<td class='another_active item' room_id=" + str(room.pk) + " time_id=" + str(
                        time[0]) + ">" + book.user.cName + "</td>"
            else:
                htmls += "<td class='item' room_id=" + \
                    str(room.pk) + " time_id=" + str(time[0]) + "></td>"

        htmls += '</tr>'

    # print(htmls)
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
            #
            post_user = request.POST.get('username')
            post_psw = request.POST.get('password1')
            post_email = request.POST.get('email')
            customer_list = []
            customer_obj = customer(
                cName=post_user, cEmail=post_email, cPassword=post_psw)
            customer_list.append(customer_obj)
            customer.objects.bulk_create(customer_list)
            #
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
