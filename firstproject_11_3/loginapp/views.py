from typing import ContextManager
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate
from django.contrib import auth
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import Form, models
from django.db.models import Q
from loginapp.models import customer, Book, Room
import datetime

from django.core.serializers import serialize
import json

from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string


# 測試用
def test(request):
    customers = customer.objects.all().order_by(
        'cName').exclude(cName=request.user.username)
    c = []

    for obj in customers:
        c.append(obj.cName)

    toSend = {
        "users": c
    }
    return render(request, "listall.html", locals())
    # return JsonResponse(toSend)


def listall(request):
    customers = customer.objects.all().order_by(
        'cName').exclude(cName=request.user.username)
    c = []

    for obj in customers:
        c.append(obj.cName)

    toSend = {
        "users": c
    }
    # return render(request, "listall.html", locals())
    return JsonResponse(toSend)


def listInvited(request):
    # 過濾出使用者名單
    user_customer = customer.objects.filter(cName=request.user.username)[0]
    hostBooks = Book.objects.filter(user=user_customer.id)
    anotherBooks = Book.objects.filter(sessionMember=user_customer)

    tosend = {}
    for obj in hostBooks:
        tosend[obj.id] = {}
        tosend[obj.id]['host'] = str(obj.user)
        tosend[obj.id]['room'] = str(obj.room)
        tosend[obj.id]['date'] = str(obj.date)
        tosend[obj.id]['time_choice'] = str(
            obj.time_choice[int(obj.time_id)-1][1])
        tosend[obj.id]['meetingName'] = str(obj.meetingName)
        tosend[obj.id]['meetingInfo'] = str(obj.meetingInfo)
    for obj in anotherBooks:
        tosend[obj.id] = {}
        tosend[obj.id]['host'] = str(obj.user)
        tosend[obj.id]['room'] = str(obj.room)
        tosend[obj.id]['date'] = str(obj.date)
        tosend[obj.id]['time_choice'] = str(
            obj.time_choice[int(obj.time_id)-1][1])
        tosend[obj.id]['meetingName'] = str(obj.meetingName)
        tosend[obj.id]['meetingInfo'] = str(obj.meetingInfo)

    for i in tosend:
        print(tosend[i])

    return JsonResponse(tosend)


def index(request):

    time_choice = Book.time_choice
    room_list = Room.objects.all()
    name = request.user.username
    # 取得當天 資料
    date = datetime.datetime.now().date()  # 年月日  datefield = datetime.datetime()
    book_date = request.GET.get('book_date', date)
    book_list = Book.objects.filter(date=book_date)

    # 過濾日期是今天以前的刪除後臺資料

    #print('book_list', book_list)
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
                    htmls += "<td class='host item' room_id=" + str(room.room_id) + " time_id=" + str(
                        time[0]) + ">" + book.user.cName + "</td>"
                else:
                    isIncluded = book.is_beincluded(name)
                    print(isIncluded)
                    if name and (book.user.cName==name):
                        htmls += "<td class='host item' room_id=" + str(room.room_id) + " time_id=" + str(
                        time[0]) + ">" + book.user.cName + "</td>"
                    elif name and isIncluded:
                        htmls += "<td class='myRoom item' room_id=" + str(room.room_id) + " time_id=" + str(
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

            ######電子郵件內容模板:####

            email_template = render_to_string(
                'signup_success_email.html',
                {'username': post_user}
            )

            email = EmailMessage(
                '註冊成功通知信',  # 電子郵件標題
                email_template,  # 電子郵件內容
                settings.EMAIL_HOST_USER,  # 寄件者
                [post_email]  # 收件者
            )

            # email.fail_silently = False
            # email.send()
            # #########################

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
    # print(post_data)
    # 用於檢視狀態 供前端檢視 並檢查
    res = {"state": True, "msg": None}

    # 添加预訂
    try:

        # 先將post取得的資料，以filter將所選取之會議室、時間、日期濾出符合的book資料
        remove_book = Q()
        for room_id, time_id_list in post_data["SELECTED"].items():
            for time_id in time_id_list:
                temp = Q()
                temp.children.append(("room_id", room_id))
                temp.children.append(("time_id", time_id))
                temp.children.append(("date", choose_date))
                remove_book.add(temp, "OR")
        selectedBook = Book.objects.all().filter(remove_book)

        # 判斷合法性
        if selectedBook:
            print(
                f"selected: {selectedBook}, there are one or more books be reserved by the others people")
            raise Exception("selected books invalid")

        # 過濾出使用者名單
        customers = customer.objects.all().order_by('cName')
        membersNameFilter = Q()
        hasmembers = False
        for _name in post_data["MEMBERS"]:
            hasmembers = True
            temp = Q()
            temp.children.append(("cName", _name))
            membersNameFilter.add(temp, "OR")
        members = customers.filter(membersNameFilter)

        # 創建book class 加入後台
        book_list = []
        user_customer = customer.objects.filter(cName=request.user.username)[0]
        for room_id, time_id_list in post_data["SELECTED"].items():
            for time_id in time_id_list:
                # 房間 時間 日期 這三者 有單一性 若重複預定 會跳exception
                book_obj = Book.objects.create(user=user_customer, room_id=room_id,
                                               time_id=time_id, date=choose_date)
                book_list.append(book_obj)

                # 有參與成員的話 加入資料庫
                if hasmembers:
                    book_obj.sessionMember.set(members)
                    #print(f"session member: {book_obj.sessionMember.all()}")

        #v ###### ###### ######    電子郵件內容模板:   ###### ###### ###### ###### ######
        print("sucessful reserveation go to mail section")

        for _book in book_list:
            # _msg = ""
            print(f"\n{ user_customer.cName } 您好:")
            print(f"host: { user_customer.cName } 預約會議成功 ，請前往查看!!")
            print(f"meeting room: {_book.room.rName}")
            print(f"time: { _book.time_choice[int(_book.time_id)-1][1] }")
            print(f"meetint name: {  _book.meetingName }")
            print(f"meeting info: { _book.meetingInfo }\n")

            _hostname = str(user_customer.cName)
            _roomName = str(_book.room.rName)
            _timeslot = str(_book.time_choice[int(_book.time_id)-1][1])
            _meetingName = str(_book.meetingName)
            _meetingInfo = str(_book.meetingInfo)

            #  先寄給host
            email_template = render_to_string(
                'meeting_notification.html',
                {'username': str(user_customer.cName),
                 'hostname': _hostname,
                 'roomName': _roomName,
                 'timeslot': _timeslot,
                 'meetingName': _meetingName,
                 'meetingInfo': _meetingInfo}
            )

            email = EmailMessage(
                '預定成功通知信',  # 電子郵件標題
                email_template,  # 電子郵件內容
                settings.EMAIL_HOST_USER,  # 寄件者
                [user_customer.cEmail]  # 收件者
            )

            # email.fail_silently = False
            # email.send()
            # /////////////////////////////////

            # # 逐一寄給予會嘉賓
            for _member in members:

                email_template = render_to_string(
                    'meeting_notification.html',
                    {'username': str(_member.cName),
                     'hostname': _hostname,
                     'roomName': _roomName,
                     'timeslot': _timeslot,
                     'meetingName': _meetingName,
                     'meetingInfo': _meetingInfo}
                )
                print(f"\n{ _member.cName } 您好:")
                print(f"host: { user_customer.cName } 預約會議成功 ，請前往查看!!")
                print(f"meeting room: {_book.room.rName}")
                print(f"time: { _book.time_choice[int(_book.time_id)-1][1] }")
                print(f"meetint name: {  _book.meetingName }")
                print(f"meeting info: { _book.meetingInfo }\n")

                email = EmailMessage(
                    '註冊成功通知信',  # 電子郵件標題
                    email_template,  # 電子郵件內容
                    settings.EMAIL_HOST_USER,  # 寄件者
                    [_member.cEmail]  # 收件者
                )

                # email.fail_silently = False
                # email.send()
            # /////////////////////////////////
        #############################################################################################

    except Exception as e:
        res["state"] = False
        res["msg"] = str(e)
        print(res["msg"])

    return HttpResponse(json.dumps(res))
    # return render(request, "meeting_notification.html", msgs)


def checkEdit(request):
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
        selectedBook = Book.objects.all().filter(remove_book)

        res["msg"] = str(remove_book)
        res["msg"] += "sucessful cancel--"
        # 若選取到之資料 會取消到別人的預訂資料 則跳exception ，沒有則單純記下要刪除之預定資訊供debug用
        for _book in selectedBook:
            if _book.user.cName != request.user.username:
                raise Exception(
                    f"permission denield client: {request.user.username} counldn't cancel the booking by client: {_book.user.cName}")
            else:
                res["msg"] += f"room_id: {_book.room_id}, time_id: {_book.time_id}, date:{_book.date}; "

        # //////////////////////////////////////////////////
        # email
        # for i in members:
        #      mail(i.cEmail,msg)
        # ///////////////////////////////////////////////////

        # 將資料延續到edit 可繼續使用
        # 透過django內建的session app
        request.session['post_data'] = post_data
        request.session['choose_date'] = choose_date

    except Exception as e:
        res["state"] = False
        res["msg"] = str(e)

    return HttpResponse(json.dumps(res))


class editBookForm(Form):
    meetingName = forms.CharField(
        label="會議名稱",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    meetingInfo = forms.CharField(
        label="會議資訊",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    memberGroup = forms.MultipleChoiceField(
        label="參與成員",
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-control'})
    )
    # memberGroup = forms.MultipleChoiceField(
    #     label="參與成員",
    #     widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    # )
    # def save(self):
    #     _book = super(editBookForm, self).save(commit=False)
    #     _book.save()
    #     return _book


def edit(request):

    # 延用資料
    post_data = request.session.get('post_data')
    choose_date = request.session.get('choose_date')
    members = customer.objects.all().order_by(
        'cName').exclude(cName=request.user.username)
    # print(post_data)
    # print(choose_date)

    res = {"op": "edit", "state": True, "msg": ""}
    try:
        # 過濾出要編輯的book
        remove_book = Q()
        for room_id, time_id_list in post_data["SELECTED"].items():
            for time_id in time_id_list:
                temp = Q()
                temp.children.append(("room_id", room_id))
                temp.children.append(("time_id", time_id))
                temp.children.append(("date", choose_date))
                remove_book.add(temp, "OR")
        selectedBook = Book.objects.all().filter(remove_book)

        editForm = editBookForm()
        if request.method == "POST":
            # 取得表單
            editForm = editBookForm(request.POST)
            if editForm.is_valid:

                _meetingName = request.POST.get('meetingName')
                _meetingInfo = request.POST.get('meetingInfo')
                _memberGroup = request.POST.getlist('memberGroup')

                # 將表單資料更新至選取的book
                for _book in selectedBook:
                    _book.meetingName = _meetingName
                    _book.meetingInfo = _meetingInfo
                    _book.sessionMember.set(_memberGroup)
                    _book.save()
                    res["msg"] += f"book host: {_book.user.cName},book time: {_book.time_id}, book room: {_book.room},\n meeting name: { _book.meetingName},\n meetingInfo: {_book.meetingInfo}"

                #v ###### ###### ######    電子郵件內容模板:   ###### ###### ###### ###### ######
                user_customer = customer.objects.filter(
                    cName=request.user.username)[0]
                print("sucessful reserveation go to mail section")
                for _book in selectedBook:
                    # _msg = ""
                    print(f"\n{ user_customer.cName } 您好:")
                    print(f"host: { user_customer.cName } 已編輯會議資訊 ，如下所示!!!!")
                    print(f"meeting room: {_book.room.rName}")
                    print(
                        f"time: { _book.time_choice[int(_book.time_id)-1][1] }")
                    print(f"meetint name: {  _book.meetingName }")
                    print(f"meeting info: { _book.meetingInfo }\n")

                    _hostname = str(user_customer.cName)
                    _roomName = str(_book.room.rName)
                    _timeslot = str(_book.time_choice[int(_book.time_id)-1][1])
                    _meetingName = str(_book.meetingName)
                    _meetingInfo = str(_book.meetingInfo)

                    #  先寄給host
                    email_template = render_to_string(
                        'edit_meeting_notification.html',
                        {'username': str(user_customer.cName),
                         'hostname': _hostname,
                         'roomName': _roomName,
                         'timeslot': _timeslot,
                         'meetingName': _meetingName,
                         'meetingInfo': _meetingInfo}
                    )

                    email = EmailMessage(
                        '編輯會議通知信',  # 電子郵件標題
                        email_template,  # 電子郵件內容
                        settings.EMAIL_HOST_USER,  # 寄件者
                        [user_customer.cEmail]  # 收件者
                    )

                    # email.fail_silently = False
                    # email.send()
                    # /////////////////////////////////

                    # # 逐一寄給予會嘉賓
                    members = _book.get_sessionMembers()
                    print(members)
                    for _member in members:
                        email_template = render_to_string(
                            'edit_meeting_notification.html',
                            {'username': str(_member.cName),
                             'hostname': _hostname,
                             'roomName': _roomName,
                             'timeslot': _timeslot,
                             'meetingName': _meetingName,
                             'meetingInfo': _meetingInfo}
                        )
                        print(f"\n{ _member.cName } 您好:")
                        print(f"host: { user_customer.cName } 已編輯會議資訊 ，如下所示!!")
                        print(f"meeting room: {_book.room.rName}")
                        print(
                            f"time: { _book.time_choice[int(_book.time_id)-1][1] }")
                        print(f"meetint name: {  _book.meetingName }")
                        print(f"meeting info: { _book.meetingInfo }\n")

                        email = EmailMessage(
                            '取消預定通知信',  # 電子郵件標題
                            email_template,  # 電子郵件內容
                            settings.EMAIL_HOST_USER,  # 寄件者
                            [_member.cEmail]  # 收件者
                        )

                        # email.fail_silently = False
                        # email.send()
                    # /////////////////////////////////
                #############################################################################################

                print(
                    f"op: {res['op']}, state: {res['state']}, msg: \n{res['msg'] }")
                return redirect("/index/")
            else:
                raise Exception("form is not valid")

    except Exception as e:
        res["state"] = False
        res["msg"] = str(e)

    print(f"op: {res['op']}; state: {res['state']}; msg: \n{res['msg'] }")
    return render(request, "edit.html", locals())


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

        #v ###### ###### ######    電子郵件內容模板:   ###### ###### ###### ###### ######
        print("sucessful reserveation go to mail section")
        for _book in _del:
            # _msg = ""
            print(f"\n{ user_customer.cName } 您好:")
            print(f"host: { user_customer.cName } 已取消會議預約 ，請前往查看!!!!")
            print(f"meeting room: {_book.room.rName}")
            print(f"time: { _book.time_choice[int(_book.time_id)-1][1] }")
            print(f"meetint name: {  _book.meetingName }")
            print(f"meeting info: { _book.meetingInfo }\n")

            _hostname = str(user_customer.cName)
            _roomName = str(_book.room.rName)
            _timeslot = str(_book.time_choice[int(_book.time_id)-1][1])
            _meetingName = str(_book.meetingName)
            _meetingInfo = str(_book.meetingInfo)

            #  先寄給host
            email_template = render_to_string(
                'cancal_meeting_notification.html',
                {'username': str(user_customer.cName),
                 'hostname': _hostname,
                 'roomName': _roomName,
                 'timeslot': _timeslot,
                 'meetingName': _meetingName,
                 'meetingInfo': _meetingInfo}
            )

            email = EmailMessage(
                '取消預定通知信',  # 電子郵件標題
                email_template,  # 電子郵件內容
                settings.EMAIL_HOST_USER,  # 寄件者
                [user_customer.cEmail]  # 收件者
            )

            # email.fail_silently = False
            # email.send()
            # /////////////////////////////////

            # # 逐一寄給予會嘉賓
            members = _book.get_sessionMembers()
            print(members)
            for _member in members:
                email_template = render_to_string(
                    'cancal_meeting_notification.html',
                    {'username': str(_member.cName),
                     'hostname': _hostname,
                     'roomName': _roomName,
                     'timeslot': _timeslot,
                     'meetingName': _meetingName,
                     'meetingInfo': _meetingInfo}
                )
                print(f"\n{ _member.cName } 您好:")
                print(f"host: { user_customer.cName } 已取消會議預約 ，請前往查看!!!!")
                print(f"meeting room: {_book.room.rName}")
                print(f"time: { _book.time_choice[int(_book.time_id)-1][1] }")
                print(f"meetint name: {  _book.meetingName }")
                print(f"meeting info: { _book.meetingInfo }\n")

                email = EmailMessage(
                    '取消預定通知信',  # 電子郵件標題
                    email_template,  # 電子郵件內容
                    settings.EMAIL_HOST_USER,  # 寄件者
                    [_member.cEmail]  # 收件者
                )

                # email.fail_silently = False
                # email.send()
            # /////////////////////////////////
        #############################################################################################
        _del.delete()

    except Exception as e:
        res["state"] = False
        res["msg"] = str(e)
        print(res["msg"])

    return HttpResponse(json.dumps(res))
