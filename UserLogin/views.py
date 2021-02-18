import csv, io
import pytz, ast
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.views.generic import CreateView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.authtoken import views

from .forms import *
from .models import User, MenuItems, Cart, MessUser, MessAttendance
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.urls import resolve
import datetime, calendar
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from .meal_timings import *

import urllib
import json
import sys

# _________________________________________________________________________________________________


IST = pytz.timezone('Asia/Kolkata')


class SignUp(CreateView):
    form_class = CustomUserCreationForm
    success_url = '/login/'

    def __init__(self):
        self.template_name = 'signup.html'


# _________________________________________________________________________________________________


def homePage(request):
    # create account or login to existing.
    return redirect('web-login')


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def logoutuser(request):
    try:
        request.user.auth_token.delete()
    except:
        pass
    return Response(status=status.HTTP_200_OK)


@api_view(['POST', ])
def signup(request):
    serializer = RegistrationSerializer(data=request.data)
    # print(request.data)
    return_data = {}
    if serializer.is_valid():
        user_account = serializer.save()
        return_data['response'] = 'successful registration'
        return_data['username'] = user_account.username
        return_data['email'] = user_account.email
        return_data['type'] = user_account.type

        # Remove when coupon system resumes:
        create_mess_objects(user_account)
    else:
        return_data = serializer.errors
    return Response(return_data)


def create_mess_objects(user_account):
    user = User.objects.get(username=user_account.username)
    mess_user_qset = MessUser.objects.filter(user=user)
    if len(mess_user_qset) <= 0:
        MessUser.objects.update_or_create(user=user)
        mess_user = MessUser.objects.get(user=user)
    else:
        mess_user = MessUser.objects.get(user=user)
        mess_user.breakfast_coupons = 20
        mess_user.lunch_coupons = 20
        mess_user.snacks_coupons = 20
        mess_user.dinner_coupons = 20
    now = datetime.datetime.now(IST)
    days_cur_month = [datetime.date(now.year, now.month, now.day + day) for day in range(0, 7)]
    days = days_cur_month
    meals = ['Breakfast', 'Lunch', 'Snacks', 'Dinner']
    attendance_qset = MessAttendance.objects.filter(user=mess_user)
    for day in days:
        qset = attendance_qset.filter(date=day)
        if qset.count() == 4:
            continue
        for j in meals:
            if qset.filter(meal=j).count() <= 0:
                MessAttendance.objects.update_or_create(
                    user=mess_user,
                    meal=j,
                    date=day,
                )


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def dashboardAPI(request):
    user = request.user
    if user.type == 'vendor':
        raise Http404('please use web app')
    elif user.type == 'customer':
        vendors = User.objects.all().filter(type='vendor')
        serializer = UserSerializer(vendors, many=True)
        return Response(serializer.data)
    raise Http404('invalid user type')


# ============================================Vendor===============================================


def vendorDashboard(request):
    orders = Cart.objects.filter(item__vendor=request.user, orderPlaced=1).exclude(status='Prepared') \
        .order_by('orderTime')
    args = {'orders': orders, }
    return render(request, 'Vendor/Home.html', args)


def checkVendor(request):
    user = User.objects.get(username=request.user.username)
    if user.type == 'customer':
        raise Http404('Invalid URL')


def vendorMenu(request):
    checkVendor(request)
    menu = MenuItems.objects.filter(vendor=request.user, hidden=False)
    args = {'menu': menu, }
    return render(request, 'Vendor/Menu.html', args)


def addItem(request):
    checkVendor(request)
    if request.method == 'POST':
        form = AddMenuItem(request.POST)
        item = form.save(commit=False)
        MenuItems.objects.update_or_create(
            itemName=item.itemName,
            price=item.price,
            vendor=request.user
        )
        return redirect('vendor-menu')
    else:
        form = AddMenuItem()
    arg = {'form': form}
    return render(request, 'Vendor/AddMenuItem.html', arg)


def addItems(request):
    if request.method == 'GET':
        return render(request, 'Vendor/AddMenuItems.html')

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        raise Http404('THIS IS NOT A CSV FILE')
    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    for row in csv.reader(io_string, delimiter=',', quotechar="|"):
        # print(row)
        if len(row) <= 1:
            break
        MenuItems.objects.update_or_create(
            itemName=row[0],
            price=row[1],
            vendor=request.user
        )
    return redirect('vendor-menu')


def removeItems(request):
    checkVendor(request)
    menu = MenuItems.objects.filter(vendor=request.user)
    args = {'menu': menu}
    return render(request, 'Vendor/RemoveMenuItems.html', args)


def removeMenuItem(request, id):
    checkVendor(request)
    instance = MenuItems.objects.get(id=id)
    instance.delete()
    return redirect('remove-item')


def hideItems(request):
    checkVendor(request)
    menu = MenuItems.objects.filter(vendor=request.user, hidden=False)
    args = {'menu': menu}
    return render(request, 'Vendor/HideMenuItems.html', args)


def hideMenuItem(request, id):
    checkVendor(request)
    instance = MenuItems.objects.get(id=id)
    instance.hidden = True
    instance.save()
    return redirect('hide-item')


def unHideItems(request):
    checkVendor(request)
    menu = MenuItems.objects.filter(vendor=request.user, hidden=True)
    args = {'menu': menu}
    return render(request, 'Vendor/UnHideMenuItems.html', args)


def unHideMenuItem(request, id):
    checkVendor(request)
    instance = MenuItems.objects.get(id=id)
    instance.hidden = False
    instance.save()
    return redirect('un-hide-item')


def updateOrderStatus(request, cartItemId):
    checkVendor(request)
    vendor = request.user
    cartItem = Cart.objects.get(id=cartItemId)
    if cartItem.item.vendor != vendor:
        raise Http404('you are not authorized update the status of this order')
    if cartItem.status == 'Added to Cart' or cartItem.status == 'Prepared' or cartItem.status == 'Collected':
        raise Http404('you are not authorized update the status of this order')
    if cartItem.status == 'Order Placed':
        cartItem.status = 'Being Prepared'
    else:
        cartItem.status = 'Prepared'
    cartItem.save()
    return redirect('personalised-dashboard')


# ===========================================Customer==============================================
def checkCustomer(request):
    user = request.user
    if user.type == 'vendor' or user.type == 'mess-vendor':
        raise Http404('invalid Url')
    return


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, ])
def viewVendorMenuAPI(request):
    checkCustomer(request)
    vendor = User.objects.get(username=request.headers['vendor'])
    menu = MenuItems.objects.all().filter(vendor=vendor, hidden=False)
    ordered = Cart.objects.all().filter(customer=request.user, orderPlaced=1)
    cart = Cart.objects.all().filter(customer=request.user, orderPlaced=0)
    Menu = list()
    for i in menu:
        Menu.append(i)
    for i in cart:
        Menu.remove(i.item)
    for i in ordered:
        Menu.remove(i.item)
    menu_serializer = CartSerializer(Menu, many=True)
    ordered_serializer = CartSerializer(ordered, many=True)
    cart_serializer = CartSerializer(cart, many=True)
    response_data = {
        'menu': menu_serializer,
        'ordered_items': ordered_serializer,
        'cart_items': cart_serializer
    }
    return Response(response_data)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def addToCartAPI(request):
    checkCustomer(request)
    item = MenuItems.objects.get(id=request.headers['itemID'])
    vendor = User.objects.get(id=request.headers['vendorID'])
    if item.vendor != vendor:
        raise Http404('Error in the URL you entered.')
    it = Cart.objects.all().filter(customer=request.user, item=item, status='Added to Cart')
    if len(it) == 0:
        Cart.objects.update_or_create(
            item=item,
            customer=request.user,
            status='Added to Cart',
            orderPlaced=0,
            qty=1,
        )
    else:
        for i in it:
            i.qty += 1
            i.save()
    cart = Cart.objects.all().filter(customer=request.user, status='Added to Cart')
    customer_cart = CartSerializer(cart, many=True)
    response_data = {'cart': customer_cart}
    return Response(response_data)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def reduceQtyAPI(request):
    checkCustomer(request)
    itemID = request.headers['itemID']
    vendorID = request.headers['vendorID']
    item = Cart.objects.get(id=itemID)
    menu_item = MenuItems.objects.get(id=item.item.id)
    vendor = User.objects.get(id=vendorID)
    checkCustomer(request)
    user = request.user
    if vendor.type != 'vendor' or menu_item.vendor != vendor or item.customer != user:
        raise Http404('The URL has some error')
    item.qty -= 1
    if item.qty == 0:
        item.delete()
    else:
        item.save()
    response_data = {
        'response': 'successfully updated'
    }
    return Response(response_data)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def increaseQtyAPI(request):
    checkCustomer(request)
    itemID = request.headers['itemID']
    vendorID = request.headers['vendorID']
    item = Cart.objects.get(id=itemID)
    menu_item = MenuItems.objects.get(id=item.item.id)
    vendor = User.objects.get(id=vendorID)
    checkCustomer(request)
    user = request.user
    if vendor.type != 'vendor' or menu_item.vendor != vendor or item.customer != user:
        raise Http404('The URL has some error')

    item.qty += 1
    item.save()
    response_data = {
        'response': 'successfully updated'
    }
    return Response(response_data)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def viewCartAPI(request):
    checkCustomer(request)
    user = request.user
    items = Cart.objects.all().filter(customer=user, orderPlaced=0)
    total = 0
    cart = []
    for i in items:
        tmp = i.qty * i.item.price
        total += tmp
        cart.append((i, tmp))
    args = {'total': total, 'cart': cart}
    return Response(args)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def placeOrderAPI(request):
    checkCustomer(request)
    user = request.user
    items = Cart.objects.all().filter(customer=user, orderPlaced=0)
    for i in items:
        i.orderPlaced = 1
        i.orderTime = datetime.datetime.now(IST)
        if i.status == 'Added to Cart':
            i.status = 'Order Placed'
        i.save()
    response_data = {
        'response': 'successfully placed order'
    }
    return Response(response_data)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def orderDetailsAPI(request):
    checkCustomer(request)
    user = request.user
    items = Cart.objects.all().filter(customer=user, orderPlaced=1)
    total = 0
    cart = []
    for i in items:
        tmp = i.item.price * i.qty
        total += tmp
        k = i.status == 'Prepared'
        serialized_i = CartSerializer(i)
        cart.append({'item': serialized_i, 'price*qty': tmp, 'prepared': k})
    # print(cart)
    args = {'cart': cart, 'total': total}
    return Response(args)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def collectedOrderAPI(request):
    checkCustomer(request)
    orders = request.headers['orders']
    for orderId in orders:
        item = Cart.objects.get(id=orderId)
        item.orderPlaced = 2
        item.status = 'Collected'
        item.save()
    response_data = {
        'response': 'successfully placed order'
    }
    return Response(response_data)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def messAttendanceAPI(request):
    checkCustomer(request)
    user = request.user
    # print(user.username)
    mess_user = MessUser.objects.get(user=user)
    now = datetime.datetime.now(IST)
    # date_today = datetime.date.today()
    upcoming_attendance = []
    meals = ['Breakfast', 'Lunch', 'Snacks', 'Dinner']
    attendance_qset = MessAttendance.objects.all().filter(user=mess_user)
    days = [datetime.date(now.year, now.month, now.day + day) for day in range(3)]  # cur, next and day after
    for i in days:
        qset = attendance_qset.filter(date=i)
        for j in range(len(meals)):
            attendance_entry = qset.get(meal=meals[j])
            upcoming_attendance.append(attendance_entry)
    attendance_serializer = MessAttendanceSerializer(upcoming_attendance, many=True)
    serialized_user = MessUserSerializer(mess_user)
    response_data = {
        'attendance': attendance_serializer.data,
        'mess_user': serialized_user.data
    }
    return Response(response_data)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def messScheduleAPI(request):
    checkCustomer(request)
    mess_user = MessUser.objects.get(user=request.user)
    now = datetime.datetime.now(IST)
    attendance = []
    days = [datetime.date(now.year, now.month, day) for day in range(now.day, now.day + 7)]
    meals = ['Breakfast', 'Lunch', 'Snacks', 'Dinner']
    attendance_qset = MessAttendance.objects.all().filter(user=mess_user)
    for day in days:
        try:
            qset = attendance_qset.filter(date=day)
            for j in range(len(meals)):
                attendance_entry = qset.get(meal=meals[j])
                attendance_entry.editable = editable_meal(meals[j], now, day)
                attendance_entry.save()
                attendance.append(attendance_entry)
        except:
            create_mess_objects(request.user)
    serializer = MessAttendanceSerializer(attendance, many=True)
    response_data = {
        'attendance':
            serializer.data
    }
    return Response(response_data)


def editable_meal(meal, now, date_cur):
    if now.date() > date_cur:
        return False
    try:
        deadline = MealDeadline.objects.get(date=date_cur, meal=meal)
        hrs = deadline.hours
    except:
        default_deadline = DefaultDeadline.objects.get(meal=meal)
        hrs = default_deadline.hours
    meal_deadline = now + datetime.timedelta(hours=hrs)
    if meal_deadline.date() < date_cur:
        return True
    elif meal_deadline.date() > date_cur:
        return False
    if meal == 'Breakfast':
        return meal_deadline.hour < breakfast_time
    elif meal == 'Lunch':
        return meal_deadline.hour < lunch_time
    elif meal == 'Snacks':
        return meal_deadline.hour < snacks_time
    else:
        return meal_deadline.hour < dinner_time


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def editMessScheduleAPI(request):
    checkCustomer(request)
    user = request.user
    mess_user = MessUser.objects.get(user=user)
    edit_attendance = ast.literal_eval(request.headers['attendance'])
    # print(edit_attendance, type(edit_attendance))
    """ attendance (list of dictionaries) - date, meals(list of meals) """
    attendance_qset = MessAttendance.objects.all().filter(user=mess_user)
    # print(attendance_qset)
    response_data = {}
    now = datetime.datetime.now(IST)
    date_today = datetime.date(now.year, now.month, now.day)
    uneditable = list()
    for day in edit_attendance:
        year = int(day['date'][0:4])
        month = int(day['date'][5:7])
        d = int(day['date'][8:])
        date_cur = datetime.date(year, month, d)
        # print('date_cur', date_cur)
        qset = attendance_qset.filter(date=date_cur)
        # print(qset)
        for meal in day['meals']:
            # print(meal)
            try:
                tmp = qset.get(meal=meal)
            except:
                create_mess_objects(request.user)
            if editable_meal(meal, now, date_cur):
                tmp.attending = not tmp.attending
                tmp.save()
            else:
                uneditable.append({'date': date_cur, 'meal': meal})
                response_data['message'] = 'some dates are not editable'
    response_data['status'] = status.HTTP_200_OK
    if len(uneditable) > 0:
        response_data['uneditable'] = uneditable
    return Response(response_data)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def sendFeedback(request):
    checkCustomer(request)
    user = request.user
    serializer = FeedbackSerializer(data=request.headers)
    # print(request.headers)
    return_data = {}
    if serializer.is_valid():
        user_feedback = serializer.validated_data
        return_data['response'] = 'successful submission'
        return_data['feedback'] = user_feedback['feedback']
        return_data['date'] = user_feedback['date']
        return_data['meal'] = user_feedback['meal']
        Feedback.objects.update_or_create(
            user=user,
            meal=user_feedback['meal'],
            date=user_feedback['date'],
            feedback=user_feedback['feedback']
        )
    else:
        return_data = serializer.errors
    return Response(return_data)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def viewPrevFeedbacks(request):
    # checkCustomer(request)
    user = request.user
    if user.type == 'customer' or user.type == 'admin':
        Feedbacks = Feedback.objects.filter(user=user).order_by('-date')
        serializer = FeedbackStatusSerializer(Feedbacks, many=True)
        return Response(serializer.data)
    else:
        raise Http404('Unauthorized')


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def getDateBasedMessMenu(request):
    checkCustomer(request)
    # user = request.user
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    date_str = request.headers['date']
    year = int(date_str[:4])
    month = int(date_str[5:7])
    day = int(date_str[8:])
    date = datetime.date(year, month, day)
    weekday = days[date.weekday()]
    menu_items_list = []
    default_qset = DefaultMessMenu.objects.filter(day=weekday)
    queryset = MessMenu.objects.filter(date=date)
    if default_qset.count() > 0:
        for q in default_qset:
            q_custom = queryset.filter(meal=q.meal)
            if q_custom.count() > 0:
                q_custom = queryset.get(meal=q.meal)
                serialized_q = DateMessMenuSerializer(q_custom)
            else:
                serialized_q = DateDefaultMessMenuSerializer(q)
            menu_items_list.append(serialized_q.data)
    else:
        for q in queryset:
            serialized_q = DateMessMenuSerializer(q)
            menu_items_list.append(serialized_q.data)
    response_data = {'CustomMenu': menu_items_list}
    return Response(response_data)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def getDefaultMessMenu(request):
    checkCustomer(request)
    weekly_menu = DefaultMessMenu.objects.all()
    serializer = DefaultMessMenuSerializer(weekly_menu, many=True)
    response_data = {'weekly_menu': serializer.data}
    return Response(response_data)


# ___________________________________Web____________________________________
def web_signup(request):
    try:
        User.objects.get(username=request.user)
        return redirect('web-home')
    except:
        pass
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            # print('sjkbvhbodisbvoisdfbv')
            user = authenticate(username=username, password=raw_password)
            # print('something')
            login(request, user)
            # print('blah')
            return redirect('web-home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})


def web_login(request):
    # print(request.user)
    try:
        User.objects.get(username=request.user)
        return redirect('web-home')
    except:
        pass
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        form.fields['username'].widget.attrs['placeholder'] = 'Username'
        form.fields['username'].label = 'Username'
        form.fields['password'].widget.attrs['placeholder'] = 'Password'
        form.fields['password'].label = 'Password'
        if form.is_valid():
            # print(form)
            user = form.get_user()
            # print(user)
            login(request, user)
        else:
            raise Http404('invalid')
    else:
        form = AuthenticationForm()
        form.fields['username'].widget.attrs['placeholder'] = 'Username'
        form.fields['username'].label = 'Username'
        form.fields['password'].widget.attrs['placeholder'] = 'Password'
        form.fields['password'].label = 'Password'
    return render(request, 'login.html', {'form': form})


def web_logout(request):
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if user.type == 'customer':
        raise Http404('Not authorized')
    logout(request)
    return redirect('web-login')


def home(request):
    try:
        user = User.objects.get(username=request.user)
    except:
        return redirect('web-login')
    if user.type == 'customer':
        raise Http404('Not authorized')
    if user.type == 'vendor':
        return redirect('vendor-home')
    return redirect('mess-home')


def messHome(request):
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not (user.type == 'admin' or user.type == 'mess-vendor'):
        raise Http404('Not authorized')
    now = datetime.datetime.now(IST)
    meals = ['Breakfast', 'Lunch', 'Snacks', 'Dinner']
    attendance_qset = MessAttendance.objects.all()
    response_data = []
    first = {}
    days = [datetime.date(now.year, now.month, now.day + day) for day in range(2)]  # cur, next
    for i in days:
        qset = attendance_qset.filter(date=i)
        feedback_qset = Feedback.objects.filter(date=i)
        for j in range(len(meals)):
            tmp_qset = qset.filter(meal=meals[j])
            attendance_entry = 0
            for q in tmp_qset:
                if q.attending:
                    attendance_entry += 1
            if i.day == now.day:
                first[meals[j]] = attendance_entry
            feedback_count = feedback_qset.filter(meal=meals[j]).exclude(status='sent').count()
            response_data.append({'date': i, 'meal': meals[j], 'count': attendance_entry, 'fcount': feedback_count})
    response_data = {'response': response_data, 'user': user, 'first': first}
    # print(response_data)
    if user.type == 'admin':
        return render(request, 'Mess/home.html', response_data)
    return render(request, 'MessVendor/home.html', response_data)


def editMealDeadline(request):
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not (user.type == 'admin'):
        raise Http404('Not authorized')
    if request.method == 'POST':
        form = MealDeadlineForm(request.POST)
        item = form.save(commit=False)
        try:
            deadline = MealDeadline.objects.get(
                date=item.date, meal=item.meal)
            deadline.hours = item.hours
            deadline.save()
        except:
            MealDeadline.objects.update_or_create(
                date=item.date,
                meal=item.meal,
                hours=item.hours
            )
        return redirect('meal-deadline')
    else:
        form = MealDeadlineForm()
    # Show all past/upcoming deadlines
    deadlines = MealDeadline.objects.all()
    arg = {'form': form, 'deadlines': deadlines, 'user': user}
    return render(request, 'Mess/meal_deadline.html', arg)


def defualtMealDeadline(request):
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not (user.type == 'admin'):
        raise Http404('Not authorized')
    if request.method == 'POST':
        form = DefaultDeadlineForm(request.POST)
        item = {
            'meal': form.data['meal'],
            'hours': form.data['hours']
        }
        try:
            deadline = DefaultDeadline.objects.get(meal=item['meal'])
            deadline.hours = item['hours']
            deadline.save()
        except:
            DefaultDeadline.objects.update_or_create(
                meal=item['meal'],
                hours=item['hours']
            )
        return redirect('default-deadline')
    else:
        form = DefaultDeadlineForm()
    # Show all past/upcoming deadlines
    deadlines = DefaultDeadline.objects.all()
    arg = {'form': form, 'deadlines': deadlines, 'user': user}
    return render(request, 'Mess/default_deadline.html', arg)


def listAttendees(request):
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')
    if request.method == 'GET':
        form = AttendeesForm()
        # date = datetime.datetime.now(IST)
        # date = datetime.date(date.year, date.month, date.day)
        qset = list()
    else:
        form = AttendeesForm(data=request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            print(type(date), 'type dateeeeeeeeeeee')
            meal = form.cleaned_data['meal']
            qset = MessAttendance.objects.filter(date=date)
            print(qset)
            qset = qset.filter(meal=meal)
            print(qset)
        else:
            raise Http404('bad data')
    list_attendees = []
    try:
        print("qsert:", qset)
        for q in qset:
            # print(tmp['email'])
            if q.attending:
                print('q', q)
                tmp = dict()
                tmp['username'] = q.user.user.username
                # print(tmp['username'])
                tmp['name'] = q.user.user.name
                # print(tmp['name'])
                tmp['email'] = q.user.user.email
                list_attendees.append(tmp)
    except:
        print('asdfghjk')
        e = sys.exc_info()[0]
        print(e)
        pass
    args = {'form': form, 'list_attendees': list_attendees, 'user': user}
    print('list_ttendess', list_attendees)
    return render(request, 'Mess/list_attendees.html', args)


def customListAttendees(request, meal):
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')
    if meal == '0':
        meal = 'Breakfast'
    elif meal == '1':
        meal = 'Lunch'
    elif meal == '2':
        meal = 'Snacks'
    elif meal == '3':
        meal = 'Dinner'
    else:
        raise Http404('Incorrect URL')
    date = datetime.datetime.now(IST)
    date = datetime.date(date.year, date.month, date.day)
    qset = MessAttendance.objects.filter(date=date, meal=meal)
    list_attendees = []
    try:
        print("qsert:", qset)
        for q in qset:
            # print(tmp['email'])
            if q.attending:
                print('q', q)
                tmp = dict()
                tmp['username'] = q.user.user.username
                # print(tmp['username'])
                tmp['name'] = q.user.user.name
                # print(tmp['name'])
                tmp['email'] = q.user.user.email
                list_attendees.append(tmp)
    except:
        print('asdfghjk')
        e = sys.exc_info()[0]
        print(e)
        pass
    args = {'list_attendees': list_attendees, 'user': user, 'meal': meal, 'date_today': date}
    return render(request, 'Mess/custom_list_attendees.html', args)


def getMarkedAttendanceCurMonth(request):
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not (user.type == 'admin' or user.type == 'mess-vendor'):
        raise Http404('Not authorized')
    now = datetime.datetime.now(IST)
    meals = ['Breakfast', 'Lunch', 'Snacks', 'Dinner']
    attendance_qset = MessAttendance.objects.all()
    response_data = []
    num_days = calendar.monthrange(now.year, now.month)[1]
    days = [datetime.date(now.year, now.month, day) for day in range(1, num_days + 1)]
    for i in days:
        qset = attendance_qset.filter(date=i)
        for j in range(len(meals)):
            attendance_entry = qset.filter(meal=meals[j])
            # try:
            # attendance_entry1 = attendance_entry.filter(attending=True)
            # print(attendance_entry1)
            attendance_cnt = 0
            for a in attendance_entry:
                if a.attending:
                    attendance_cnt += 1
            # except:
            #     attendance_cnt = 0
            response_data.append({'date': i, 'meal': meals[j], 'count': attendance_cnt})
    response_data = {'response': response_data, 'user': user}
    if user.type == 'admin':
        return render(request, 'Mess/attendance.html', response_data)
    return render(request, 'MessVendor/view_attendance.html', response_data)


def getMarkedAttendancePrevMonth(request):
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')

    meals = ['Breakfast', 'Lunch', 'Snacks', 'Dinner']
    now = datetime.datetime.now(IST) - datetime.timedelta(months=1)
    attendance_qset = MessAttendance.objects.all()
    response_data = []
    num_days = calendar.monthrange(now.year, now.month)[1]
    days = [datetime.date(now.year, now.month, day) for day in range(1, num_days + 1)]
    for i in days:
        qset = attendance_qset.filter(date=i)
        for j in range(len(meals)):
            attendance_tmp = qset.filter(meal=meals[j])
            attendance_entry = 0
            for a in attendance_tmp:
                if a.attending:
                    attendance_entry += 1
            response_data.append({'date': i, 'meal': meals[j], 'count': attendance_entry})
    response_data = {'response': response_data, 'user': user}
    return render(request, 'Mess/home.html', response_data)


def uploadAttendance(request):
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')
    if request.method == 'GET':
        form = AttendanceList()
        return render(request, 'Mess/upload_attendance.html', {'form': form, 'user': user})

    form = AttendanceList(data=request.POST)
    if form.is_valid():
        meal = form.cleaned_data['meal']
        date = form.cleaned_data['date']
        qset = MessAttendance.objects.filter(meal=meal,
                                             date=date)
    else:
        raise Http404('bad data')
    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        raise Http404('THIS IS NOT A CSV FILE')
    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    for row in csv.reader(io_string, delimiter=',', quotechar="|"):
        # print(row)
        if len(row) <= 1:
            break
        username = row[0]
        attended = (row[1] == '1')
        user = User.objects.get(username=username)
        mess_user = MessUser.objects.get(user=user)
        # print(user)
        attendance_obj = qset.get(user=mess_user)
        attendance_obj.attended = attended
        # meal = attendance_obj.meal
        attendance_obj.defaulter = not (attended == attendance_obj.attending)
        attendance_obj.save()
        # if attended:
        #     if meal == 'Breakfast':
        #         mess_user.breakfast_coupons -= 1
        #     if meal == 'Lunch':
        #         mess_user.lunch_coupons -= 1
        #         # print('something')
        #     if meal == 'Snacks':
        #         mess_user.snacks_coupons -= 1
        #     if meal == 'Dinner':
        #         mess_user.dinner_coupons -= 1
        mess_user.save()
        # print(mess_user.lunch_coupons)
    return redirect('mess-home')


def listDefaulters(request):
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')
    defaulter_list = []
    if request.method == 'GET':
        form = AttendanceList()
        # meal = 'Breakfast'
        # date = datetime.datetime.now(IST)
        # date = datetime.date(date.year, date.month, date.day)
        qset = []
        feedbackset = []
    else:
        form = AttendanceList(data=request.POST)
        if form.is_valid():
            meal = form.cleaned_data['meal']
            date = form.cleaned_data['date']
            qset = MessAttendance.objects.filter(meal=meal, date=date)
            feedbackset = Feedback.objects.filter(meal=meal, date=date)
        else:
            raise Http404('bad data')
    for elem in qset:
        if elem.defaulter:
            tmp = {}
            try:
                feedback = feedbackset.get(user=elem.user.user)
                tmp['feedback'] = feedback.feedback
                tmp['status'] = feedback.status
            except:
                tmp['feedback'] = ''
                tmp['status'] = ''
            tmp['username'] = elem.user.user.username
            if meal == 'Breakfast':
                tmp['coupons'] = elem.user.breakfast_coupons
            elif meal == 'Lunch':
                tmp['coupons'] = elem.user.lunch_coupons
            elif meal == 'Snacks':
                tmp['coupons'] = elem.user.snacks_coupons
            elif meal == 'Dinner':
                tmp['coupons'] = elem.user.dinner_coupons
            tmp['marked'] = elem.attending
            tmp['attended'] = elem.attended

            defaulter_list.append(tmp)
    args = {'form': form, 'defaulter_list': defaulter_list, 'user': user}
    return render(request, 'Mess/defaulter.html', args)


def viewFeedback(request):
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')
    feedbackqset = Feedback.objects.filter(status='sent').order_by('-date')
    response_data = {
        'feedback': feedbackqset,
        'user': user
    }
    return render(request, 'Mess/feedback.html', response_data)


def penalise(request, feedbackid):
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')
    feedback = Feedback.objects.get(id=feedbackid)
    feedback.status = 'penalised'
    user = feedback.user
    mess_user = MessUser.objects.get(user=user)
    mess_attendance_obj = MessAttendance.objects.get(user=mess_user, meal=feedback.meal, date=feedback.date)
    if not mess_attendance_obj.attended:
        if feedback.meal == 'Breakfast':
            if mess_user.breakfast_coupons > 0:
                mess_user.breakfast_coupons -= 1
        elif feedback.meal == 'Lunch':
            if mess_user.lunch_coupons > 0:
                mess_user.lunch_coupons -= 1
        elif feedback.meal == 'Snacks':
            if mess_user.snacks_coupons > 0:
                mess_user.snacks_coupons -= 1
        elif feedback.meal == 'Dinner':
            if mess_user.dinner_coupons > 0:
                mess_user.dinner_coupons -= 1
        mess_user.save()
    feedback.save()
    return redirect('mess-feedback')


def approve(request, feedbackid):
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')
    feedback = Feedback.objects.get(id=feedbackid)
    feedback.status = 'approved'
    feedback.save()
    return redirect('mess-feedback')


def maybe(request, feedbackid):
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')
    feedback = Feedback.objects.get(id=feedbackid)
    feedback.status = 'check mail'
    feedback.save()
    return redirect('mess-feedback')


def viewUsers(request):
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')
    Users = User.objects.filter(type='customer')
    return render(request, 'Mess/view_users.html', {'users': Users, 'user': user})


def addData(request, user_id):
    # MessUser.objects.all().delete()
    # MessAttendance.objects.all().delete()
    user = User.objects.get(id=user_id)
    mess_user_qset = MessUser.objects.filter(user=user)
    if len(mess_user_qset) <= 0:
        MessUser.objects.update_or_create(user=user)
        mess_user = MessUser.objects.get(user=user)
    else:
        mess_user = MessUser.objects.get(user=user)
        mess_user.breakfast_coupons = 20
        mess_user.lunch_coupons = 20
        mess_user.snacks_coupons = 20
        mess_user.dinner_coupons = 20
    # print(user)
    # print(mess_user.id)
    now = datetime.datetime.now(IST)
    date_today = datetime.date(now.year, now.month, now.day)
    num_days = calendar.monthrange(date_today.year, date_today.month)[1]
    days_cur_month = [datetime.date(date_today.year, date_today.month, day) for day in range(1, num_days + 1)]
    days = days_cur_month
    meals = ['Breakfast', 'Lunch', 'Snacks', 'Dinner']
    for day in days:
        for j in meals:
            MessAttendance.objects.update_or_create(
                user=mess_user,
                meal=j,
                date=day,
            )
    return redirect('view-users')


def deleteUser(request, user_id):
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')
    User.objects.get(id=user_id).delete()
    return redirect('view-users')


def giveAdminRights(request, user_id):
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')
    usr = User.objects.get(id=user_id)
    usr.type = 'admin'
    usr.save()
    return redirect('view-users')


def removeAdminRights(request, user_id):
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')
    usr = User.objects.get(id=user_id)
    usr.type = 'customer'
    usr.save()
    return redirect('view-users')


def setMessMenu(request):
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')

    if request.method == 'POST':
        form = MessMenuForm(request.POST)
        item = form.save(commit=False)
        MessMenu.objects.update_or_create(
            items=item.items,
            date=item.date,
            meal=item.meal
        )
        return redirect('admin-view-mess-menu')
    else:
        form = MessMenuForm()
    args = {'user': user, 'form': form}
    return render(request, 'Mess/set_menu.html', args)


def setDefaultMessMenu(request):
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')

    if request.method == 'POST':
        form = DefaultMessMenuForm(request.POST)
        item = form.save(commit=False)
        try:
            item_entry = DefaultMessMenu.objects.get(day=item.day, meal=item.meal)
            print(item_entry, 'itemmmmm entryyyy')
            item_entry.items = item.items
            print(item_entry.items)
            item_entry.save()
        except:
            DefaultMessMenu.objects.update_or_create(
                items=item.items,
                day=item.day,
                meal=item.meal
            )
        return redirect('admin-view-mess-menu')
    else:
        form = DefaultMessMenuForm()
    args = {'user': user, 'form': form}
    return render(request, 'Mess/set_default_menu.html', args)


def adminViewMessMenu(request):
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')
    args = dict()

    # Default Menu - i.e. weekly
    weekly_menu = DefaultMessMenu.objects.all()
    args['weekly_menu'] = weekly_menu

    # Search for Custom Menu - i.e. date wise
    if request.method == 'POST':
        form = MessMenuSearchForm(data=request.POST)
        if form.is_valid():
            date_entered = form.cleaned_data['date']
            custom_menu = MessMenu.objects.filter(date=date_entered)
    else:
        form = MessMenuSearchForm()
        custom_menu = dict()
    args['form'] = form
    args['custom_menu'] = custom_menu
    args['user'] = user
    return render(request, 'Mess/view_menu.html', args)


def deleteDefaultMessMenuItem(request, itemid):
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')
    default_menu_entry = DefaultMessMenu.objects.get(id=itemid)
    default_menu_entry.delete()
    return redirect('admin-view-mess-menu')


def deleteMessMenuItem(request, itemid):
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')
    menu_entry = MessMenu.objects.get(id=itemid)
    menu_entry.delete()
    return redirect('admin-view-mess-menu')


# _____________________________________Extra_______________________________
def renew(request):
    # users = User.objects.all()
    # for user in users:
    #     try:
    #         mess_user_tmp = MessUser.objects.get(user=user)
    #         if user.type == 'customer':
    #             continue
    #         mess_user_tmp.delete()
    #     except:
    #         MessUser.objects.update_or_create(user=user)
    # mess_users = MessUser.objects.all()
    # now = datetime.datetime.now(IST)
    # num_days = calendar.monthrange(now.year, now.month)[1]
    # days_cur_month = [datetime.date(now.year, now.month, day) for day in range(1, num_days + 1)]
    # days = days_cur_month
    # meals = ['Breakfast', 'Lunch', 'Snacks', 'Dinner']
    # for mess_user in mess_users:
    #     for day in days:
    #         for j in meals:
    #             try:
    #                 MessAttendance.objects.get(user=mess_user, date=day, meal=j)
    #             except:
    #                 MessAttendance.objects.update_or_create(
    #                     user=mess_user,
    #                     meal=j,
    #                     date=day,
    #                 )
    users = User.objects.all()
    cntr = 0
    for user in users:
        if user.type == 'customer':
            print(user.username, '*************')
            try:
                mess_user = MessUser.objects.get(user=user)
                cnt = MessAttendance.objects.filter(user=mess_user).count()
                print(cnt)
                cntr += 1
            except:
                print('!!!!!!!!!!!!!!!!!!!!!!', user.username)
        else:
            print(user.username, 'hjcvjhdvd', user.type)
    print('total_customers', cntr)
    return redirect('default-deadline')
