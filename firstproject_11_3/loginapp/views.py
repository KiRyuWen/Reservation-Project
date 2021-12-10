from django.shortcuts import redirect, render
from django.contrib.auth import authenticate
from django.contrib import auth
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.db.models import Q
from loginapp.models import customer, Book, Room
import datetime

from django.core.serializers import serialize
import json

# 測試用


def listall(request):
    customers = customer.objects.all().order_by('cName')
    
    c =[]

    for obj in customers:
        c.append(obj.cName)

    toSend ={
        "users":c
    }    
    #return render(request, "listall.html", locals())
    return JsonResponse(toSend)


def index(request):

    time_choice = Book.time_choice
    room_list = Room.objects.all()
    name = request.user.username
    # 取得當天 資料
    date = datetime.datetime.now().date()  # 年月日  datefield = datetime.datetime()
    book_date = request.GET.get('book_date', date)
    book_list = Book.objects.filter(date=book_date)

    print('book_list', book_list)
    # 自製行程表表格 再將htmls給予index.html存取
    htmls = ""
    for room in room_list:
        htmls += "<tr><td>" + room.rName + "(" + str(room.num) + ")</td>"
        for time in time_choice:

            flag = False
            for book in book_list:
                # 立flag 如果為true 則此格表示 已被預訂
                if book.room.room_id == room.room_id and book.time_id == time[0]:
                    flag = True
                    break

            if flag:
                if request.user.pk == book.user.pk:
                    htmls += "<td class='active item' room_id=" + str(room.room_id) + " time_id=" + str(
                        time[0]) + ">" + book.user.cName + "</td>"
                else:
                    htmls += "<td class='another_active item' room_id=" + str(room.room_id) + " time_id=" + str(
                        time[0]) + ">" + book.user.cName + "</td>"
            else:
                htmls += "<td class='item' room_id=" + \
                    str(room.room_id) + " time_id=" + str(time[0]) + "></td>"

        htmls += '</tr>'

    # print(htmls)
    return render(request, "index.html", locals())


def login(request):
    # 以post 取得資料
    if request.method == 'POST':
        name = request.POST['username']
        password = request.POST['password']
        # 內建驗證系統
        user = authenticate(username=name, password=password)
        if user is not None:
            if user.is_active:
                auth.login(request, user)
                return redirect('/index/')
                message = '登入成功~'
            else:
                message = '帳號尚未啟用'
        else:
            message = '輸入資料有誤 或 未符合格式等 登入失敗!!'
    return render(request, "login.html", locals())


def logout(request):
    auth.logout(request)
    return redirect('/login/')


def rigister(request):
    # 以post將表單給予前端取得資料
    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            post_user = request.POST.get('username')
            post_psw = request.POST.get('password1')
            post_email = request.POST.get('email')
            customer_list = []
            # 新辦帳號
            customer_obj = customer(
                cName=post_user, cEmail=post_email, cPassword=post_psw)
            customer_list.append(customer_obj)
            customer.objects.bulk_create(customer_list)
            return redirect('/login/')  # 重新導向到登入畫面
    context = {
        'form': form
    }
    return render(request, "register.html", context)

# 註冊表單


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

# 預定流程


def book(request):

    # {'SELECTED': {'1': ['5', '7'], '3': ['4']}, 'DEL': {'2': ['9']}}
    # 前端取得之資料 格視為 : { 'room_id1':['time_id1','time_id5'], 'room_id2':['time_id7','time_id8'],...}
    # 房間代碼為索引值 以此索引可得該會議室被前端選取到之時間代碼清單

    post_data = json.loads(request.POST.get('post_data'))
    choose_date = request.POST.get("choose_date")
    print(post_data)
    # 用於檢視狀態 供前端檢視 並檢查
    res = {"state": True, "msg": None}

    # 添加预订
    try:
        customers = customer.objects.all().order_by('cName')
        user_customer = customer.objects.filter(cName=request.user.username)[0]
        book_list = []
        for room_id, time_id_list in post_data["SELECTED"].items():
            for time_id in time_id_list:
                # 房間 時間 日期 這三者 有單一性 若重複預定 會跳exception
                book_obj = Book(user=user_customer, room_id=room_id,
                                time_id=time_id, date=choose_date)
                book_list.append(book_obj)
        print(book_list)
        Book.objects.bulk_create(book_list)

    except Exception as e:
        res["state"] = False
        res["msg"] = str(e)

    return HttpResponse(json.dumps(res))


def cancel(request):
    # {'SELECTED': {'1': ['5', '7'], '3': ['4']}, 'DEL': {'2': ['9']}}
    # 前端取得之資料 格視為 : { 'room_id1':['time_id1','time_id5'], 'room_id2':['time_id7','time_id8'],...}
    # 房間代碼為索引值 以此索引可得該會議室被前端選取到之時間代碼清單

    post_data = json.loads(request.POST.get('post_data'))
    choose_date = request.POST.get("choose_date")

    # 用於檢視狀態 供前端檢視 並檢查
    res = {"state": True, "msg": None}

    # 將合法選取的取消預定
    try:
        customers = customer.objects.all().order_by('cName')
        user_customer = customer.objects.filter(cName=request.user.username)[0]
        # 先將post取得的資料，以filter將所選取之會議室、時間、日期濾出符合的book資料
        remove_book = Q()
        for room_id, time_id_list in post_data["SELECTED"].items():
            for time_id in time_id_list:
                temp = Q()
                temp.children.append(("room_id", room_id))
                temp.children.append(("time_id", time_id))
                temp.children.append(("date", choose_date))
                remove_book.add(temp, "OR")
        _del = Book.objects.all().filter(remove_book)

        res["msg"] = str(remove_book)
        res["msg"] += "sucessful cancel--"
        # 若選取到之資料 會取消到別人的預訂資料 則跳exception ，沒有則單純記下要刪除之預定資訊供debug用
        for _book in _del:
            if _book.user.cName != request.user.username:
                raise Exception(
                    f"permission denield client: {request.user.username} counldn't cancel the booking by client: {_book.user.cName}")
            else:
                res["msg"] += f"room_id: {_book.room_id}, time_id: {_book.time_id}, date:{_book.date}; "

        _del.delete()

    except Exception as e:
        res["state"] = False
        res["msg"] = str(e)

    return HttpResponse(json.dumps(res))
