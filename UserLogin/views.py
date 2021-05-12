import calendar
import csv
import io
import sys

import ast
import pytz
from background_task.models import Task
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic import CreateView
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .forms import *
from .meal_timings import *
from .serializers import *
from .tasks import daily_create_mess_objects


# Global timezone variable for easy access.
IST = pytz.timezone('Asia/Kolkata')


# Functions used by several view functions
def create_mess_objects(user_account, numdays=7):
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
    date_start = datetime.date(year=now.year, month=now.month, day=now.day)
    days = [(date_start + datetime.timedelta(days=day)) for day in range(0, numdays)]
    meals = ['Breakfast', 'Lunch', 'Snacks', 'Dinner']
    for day in days:
        for j in meals:
            q = MessAttendance.objects.filter(user=mess_user, date=day, meal=j)
            if q.count() < 1:
                MessAttendance.objects.update_or_create(
                    user=mess_user,
                    date=day,
                    meal=j
                )
    return


def editable_meal(meal, now, date_cur):
    """
    Function to check if a meal is editable
    :param meal: meal name from Breakfast/Lunch/Snacks/Dinner
    :param now: datetime object corresponding to the date and time at the present moment.
    :param date_cur: check the if a meal on date specified by this parameter is editable.
    :return: True for editable, False for not.
    """
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


# _____________________________________ View Functions _____________________________________
def homePage(request):
    """
    Corresponding to the landing page of the website.
    Starts the parallel task if it isn't already running
    Redirects to a login page.
    :param request: Django Request Object
    :return: redirection to Login Page
    """
    tasks = Task.objects.filter(verbose_name='CreatingMessObjs')
    if len(tasks) == 0:
        daily_create_mess_objects(repeat=60*60*24, verbose_name='CreatingMessObjs')
    else:
        pass
    return redirect('web-login')


# _____________________________________ Basic API Functions _____________________________________
@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def logoutuser(request):
    """
    Logout from Mobile App, delete the Authentication Token for the user (log out of all devices)
    :param request: Django Rest Framework Request Object
        :headers Authorization Token
    :return: HTTP 200 Status
    """
    try:
        request.user.auth_token.delete()
    except:
        pass
    return Response(status=status.HTTP_200_OK)


@api_view(['POST', ])
def signup(request):
    """
    API signup for a new user.
    :param request: Django Rest Framework Sign Up
        :headers username, email, type, name, password, validate_password.
    :return: serialised registered user object, if registration was successful
        otherwise, serialiser errors.
    """
    serializer = RegistrationSerializer(data=request.data)
    return_data = {}
    if serializer.is_valid():
        user_account = serializer.save()
        return_data['response'] = 'successful registration'
        return_data['username'] = user_account.username
        return_data['email'] = user_account.email
        return_data['type'] = user_account.type
        create_mess_objects(user_account, numdays=31)
    else:
        return_data = serializer.errors
    return Response(return_data)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def dashboardAPI(request):
    """
    For customer screen corresponding to vendor list.
    :param request: Django Rest Framework (DRF) request object
            :headers Authorization Token
    :return: serialised list of vendors.
    """
    user = request.user
    if user.type == 'vendor':
        raise Http404('please use web app')
    elif user.type == 'customer':
        vendors = User.objects.all().filter(type='vendor')
        serializer = UserSerializer(vendors, many=True)
        return Response(serializer.data)
    raise Http404('invalid user type')


# ============================================ Vendor ===============================================
# The following functions are for Canteen Vendors, etc
def checkVendor(request):
    """
    Function to check if user sending the request is a vendor or not
    Raises 404 error if the user is not a vendor
    :param request: Django Request object.
    :return: None
    """
    user = User.objects.get(username=request.user.username)
    if not user.type == 'vendor':
        raise Http404('Invalid URL')


def vendorDashboard(request):
    """
    Rendors Vendor Dashboard containing all orders that are placed and have not been prepared.
    :param request: Django Request object
    :return: HTML render
    """
    checkVendor(request)
    orders = Cart.objects.filter(item__vendor=request.user, orderPlaced=1).exclude(status='Prepared') \
        .order_by('orderTime')
    args = {'orders': orders, }
    return render(request, 'Vendor/Home.html', args)


def vendorMenu(request):
    """
    Function that renders the Menu screen for a vendor
    :param request: Django request object
    :return: rendered HTML
    """
    checkVendor(request)
    menu = MenuItems.objects.filter(vendor=request.user, hidden=False)
    args = {'menu': menu, }
    return render(request, 'Vendor/Menu.html', args)


def addItem(request):
    """
    Renders screen for adding a menu item.
    Asks vendor to add details of the item through a form.
    :param request: Django Request object
    :return: rendered HTML
    """
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
    """
    Renders screen for adding menu items read from an uploaded csv file.
    Asks vendor to upload the file using the form.
    :param request: Django Request object
    :return: rendered HTML
    """
    if request.method == 'GET':
        return render(request, 'Vendor/AddMenuItems.html')
    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        raise Http404('THIS IS NOT A CSV FILE')
    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    for row in csv.reader(io_string, delimiter=',', quotechar="|"):
        if len(row) <= 1:
            break
        MenuItems.objects.update_or_create(
            itemName=row[0],
            price=row[1],
            vendor=request.user
        )
    return redirect('vendor-menu')


def removeItems(request):
    """
    Renders the HTML for displaying the list of menu items and providing the options to remove them
    :param request: Django Request object
    :return: rendered HTML
    """
    checkVendor(request)
    menu = MenuItems.objects.filter(vendor=request.user)
    args = {'menu': menu}
    return render(request, 'Vendor/RemoveMenuItems.html', args)


def removeMenuItem(request, id):
    """
    Processes the removal request for a menu item
    :param request: Django Request Object
    :param id: id of the item to be removed
    :return: redirection to vendor/menu/removeitem/
    """
    checkVendor(request)
    instance = MenuItems.objects.get(id=id)
    instance.delete()
    return redirect('remove-item')


def hideItems(request):
    """
    Renders the list of items to an HTML that can be hidden
    :param request: Django Request object
    :return: rendered HTML
    """
    checkVendor(request)
    menu = MenuItems.objects.filter(vendor=request.user, hidden=False)
    args = {'menu': menu}
    return render(request, 'Vendor/HideMenuItems.html', args)


def hideMenuItem(request, id):
    """
    Processes the request for hiding a menu item
    :param request: Django Request Object
    :param id: id of the item to be hidden
    :return: redirection to vendor/menu/hideitem/
    """
    checkVendor(request)
    instance = MenuItems.objects.get(id=id)
    instance.hidden = True
    instance.save()
    return redirect('hide-item')


def unHideItems(request):
    """
    Renders the list of items to an HTML that can be un-hidden
    :param request: Django Request object
    :return: rendered HTML
    """
    checkVendor(request)
    menu = MenuItems.objects.filter(vendor=request.user, hidden=True)
    args = {'menu': menu}
    return render(request, 'Vendor/UnHideMenuItems.html', args)


def unHideMenuItem(request, id):
    """
    Processes request to show a hidden item on menu
    :param request: Django Request object
    :param id: id of the hidden object
    :return: redirection to 'Unhide Items list'
    """
    checkVendor(request)
    instance = MenuItems.objects.get(id=id)
    instance.hidden = False
    instance.save()
    return redirect('un-hide-item')


def updateOrderStatus(request, cartItemId):
    """
    When the vendor views orders they can update the status of the order to 'Being prepared' and then 'Prepared'
    This function caters to these updates
    :param request: Django request object
    :param cartItemId: Id of the item that has to be updated
    :return: redirection to order list view
    """
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


# ======================================== Customer (Interactions with Vendor) ========================================
def checkCustomer(request):
    """
    Function to check if the current user is a customer
    Raises HTTP404 error in case the user is not a customer
    :param request: Django Request Object
    :return: None
    """
    user = request.user
    if not user.type == 'customer':
        raise Http404('invalid Url')
    return


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, ])
def viewVendorMenuAPI(request):
    """
    API request pertaining to Viewing a vendor's menu
    :param request: DRF request object
        headers: Auth Token, vendor (username)
    :return: serialised data containing menu, ordered items, cart items.
    """
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
    """
    Processes API request to add a menu item to cart.
    :param request: Django Rest Framework request object
        headers:    itemID - ID of the item to be added to cart
                    vendorID - Id of the vendor providing the item
                    Authorization Token
    :return: serialised cart object
    """
    checkCustomer(request)
    item = MenuItems.objects.get(id=request.headers['itemID'])
    vendor = User.objects.get(id=request.headers['vendorID'])
    if item.vendor != vendor:
        # The item should be provided by the vendor
        raise Http404('Error in the URL you entered.')
    it = Cart.objects.all().filter(customer=request.user, item=item, status='Added to Cart')
    if len(it) == 0:
        # If the user hasn't already added this item to the cart
        Cart.objects.update_or_create(
            item=item,
            customer=request.user,
            status='Added to Cart',
            orderPlaced=0,
            qty=1,
        )
    else:
        # If the user has already added the item to cart.
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
    """
    Processes API request to reduce the quantity of a menu item in cart.
    :param request: Django Rest Framework request object
        headers:    itemID - ID of the item to be added to cart
                    vendorID - Id of the vendor providing the item
                    Authorization Token
    :return: successful update response
    """
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
        # Delete the item from cart if the quantity was previously one
        item.delete()
    else:
        # Save changes to the item entry if the quantity was > 1
        item.save()
    response_data = {
        'response': 'successfully updated'
    }
    return Response(response_data)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def increaseQtyAPI(request):
    """
    Increase the Quantity of a given item in the cart.
    :param request: Django Rest Framework request object
        headers:    itemID - ID of the item to be added to cart
                    vendorID - Id of the vendor providing the item
                    Authorization Token
    :return: successful update response
    """
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
    """
    API request to view a user's cart.
    :param request: Django Rest Framework request object
        headers: Authorization Token
    :return: Dictionary containing total price of the items in cart and cart items list.
    """
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
    """
    API Request to place order of items present in cart
    :param request: Django Rest Framework request object
        headers: Authorization Token
    :return: succesful update response
    """
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
    """
    API request to view order details
    :param request: Django Rest Framework request object
        headers: Authorization Token
    :return: serialised data containing bill.
    """
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
    args = {'cart': cart, 'total': total}
    return Response(args)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def collectedOrderAPI(request):
    """
    API request to update status of an order that has been collected from the vendor stall
    :param request: Django Rest Framework request object
        headers:     Authorization Token
                    orders: list of orderIDs
    :return: successful update response
    """
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


# ======================================== Customer (Interactions with Mess) ========================================
@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def messAttendanceAPI(request):
    """
    API request to get data for the home screen of Mess Attendance Interface Dashboard. (Present Dashboard)
    [TESTED + INTEGRATED]
    :param request: Django Rest Framework request object
        headers: Authorization Token
    :return: serialised data containing corresponding MessUser object details and their attendance for upcoming 3 days.
    """
    checkCustomer(request)
    user = request.user
    mess_user = MessUser.objects.get(user=user)
    now = datetime.datetime.now(IST)
    upcoming_attendance = []
    meals = ['Breakfast', 'Lunch', 'Snacks', 'Dinner']
    attendance_qset = MessAttendance.objects.all().filter(user=mess_user)
    days = [(now + datetime.timedelta(days=day)).date() for day in range(3)]  # cur, next and day after
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
    """
    API request corresponding to calendar schedule page. Returns the attendance objects for 31 days
    (starting from "today" - for the user)
    [TESTED + INTEGRATED]
    :param request: Django Rest Framework request object
        headers: Authorization Token
    :return: serialised attendance objects for 31 days.
    """
    checkCustomer(request)
    mess_user = MessUser.objects.get(user=request.user)
    now = datetime.datetime.now(IST)
    attendance = []
    # numdays = 7  # returning the data for seven days.
    # date_start = now.date()
    # date_end = (now + datetime.timedelta(days=numdays-1)).date()
    # print(date_end)

    numdays = calendar.monthrange(now.year, now.month)[1]
    date_start = datetime.date(year=now.year, month=now.month, day=now.day)
    date_end = date_start + datetime.timedelta(days=numdays)

    attendance_qset = MessAttendance.objects.filter(user=mess_user).filter(date__range=[date_start, date_end])\
        .order_by('date')
    # Check to see if the objects exist - they would because of the parallel task that runs along with the server
    cnt = numdays * 4
    if attendance_qset.count() < cnt:
        create_mess_objects(request.user, numdays)
        attendance_qset = MessAttendance.objects.filter(user=mess_user).filter(date__range=[date_start, date_end])\
            .order_by('date')
        print(attendance_qset.count())
    prev = False
    for q in attendance_qset:
        if not q.editable:
            attendance.append(q)
            continue
        if not prev:
            # check if a meal is editable only if the previous meal was not editable, i.e. deadline had passed.
            q.editable = editable_meal(q.meal, now, q.date)
            q.save()
            prev = q.editable
        attendance.append(q)
    serializer = MessAttendanceSerializer(attendance, many=True)
    response_data = {'attendance': serializer.data, }
    return Response(response_data)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def editMessScheduleAPI(request):
    """
    API request corresponding to editing the marked attendance for meals on dates specified by the user.
    [TESTED + INTEGRATED]
    :param request: Django Rest Framework request object
        headers: Authorization Token
                attendance: list of dictionaries with each dictionary containing: date, meals (list of meals)
                            example: [{'date': '2021-05-10', 'meals': ['Breakfast', 'Lunch']}, ..]
    :return: HTTP 200 Ok response, with any dates that were uneditable.
    """
    checkCustomer(request)
    user = request.user
    mess_user = MessUser.objects.get(user=user)
    edit_attendance = ast.literal_eval(request.headers['attendance'])  # convert the data into a JSON object
    attendance_qset = MessAttendance.objects.all().filter(user=mess_user)
    response_data = {}
    now = datetime.datetime.now(IST)
    uneditable = list()
    for day in edit_attendance:
        year = int(day['date'][0:4])
        month = int(day['date'][5:7])
        d = int(day['date'][8:])
        date_cur = datetime.date(year, month, d)
        qset = attendance_qset.filter(date=date_cur)
        for meal in day['meals']:
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
    """
    API request corresponding to sending feedback for the mess.
    [TESTED + INTEGRATED]
    :param request: Django Rest Framework request object
        headers: Authorization Token, meal, ForDate, feedback
    :return: any serialisation errors.
    """
    checkCustomer(request)
    user = request.user
    serializer = FeedbackSerializer(data=request.headers)
    return_data = {}
    if serializer.is_valid():
        user_feedback = serializer.validated_data
        return_data['response'] = 'successful submission'
        return_data['feedback'] = user_feedback['feedback']
        return_data['ForDate'] = request.headers['ForDate']
        return_data['meal'] = user_feedback['meal']
        Feedback.objects.update_or_create(
            user=user,
            meal=user_feedback['meal'],
            date=request.headers['ForDate'],
            feedback=user_feedback['feedback']
        )
    else:
        return_data = serializer.errors
    return Response(return_data)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def viewPrevFeedbacks(request):
    """
    API request corresponding to viewing a user's own feedback status for the mess.
    [TESTED + INTEGRATED]
    :param request: Django Rest Framework request object
        headers: Authorization Token
    :return: serialised response of list of feedback objects
    """
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
    """
    API request corresponding to viewing Special (Occasional) Mess Menu .
    [TESTED + INTEGRATED]
    :param request: Django Rest Framework request object
        headers: Authorization Token, ForDate
    :return: serialised menu for specified date
    """
    checkCustomer(request)
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    date_str = request.headers['ForDate']
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
    """
    API request corresponding to viewing Weekly Mess Menu .
    [TESTED + INTEGRATED]
    :param request: Django Rest Framework request object
        headers: Authorization Token
    :return: Serialised Weekly Menu
    """
    checkCustomer(request)
    weekly_menu = DefaultMessMenu.objects.all()
    serializer = DefaultMessMenuSerializer(weekly_menu, many=True)
    response_data = {'weekly_menu': serializer.data}
    return Response(response_data)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def sendAppFeedback(request):
    """
    API request corresponding to sending feedback for app.
    [TESTED + INTEGRATED]
    :param request: Django Rest Framework request object
        headers: Authorization Token, feedback
    :return: any serialiser errors, if not Okay response.
    """
    checkCustomer(request)
    user = request.user
    serializer = AppFeedbackSerializer(data=request.headers)
    return_data = {}
    if serializer.is_valid():
        user_feedback = serializer.validated_data
        return_data['status'] = status.HTTP_200_OK
        now = datetime.datetime.now(IST)
        resp = user_feedback['feedback']
        AppFeedback.objects.update_or_create(
            user=user,
            feedback=resp,
            timestamp=now,
        )
    else:
        return_data = serializer.errors
    return Response(return_data)


# ======================================== Mess Admin and Mess Vendors ========================================
# All have been tested.
def web_signup(request):
    """
    Sign up page on web App
    :param request: Django request object
    :return: rendered HTML
    """
    try:
        # If the request object has details of an authorised user, redirect them to their dashboard.
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
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('web-home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})


def web_login(request):
    """
    Login page on web App
    :param request: Django request object
    :return: rendered HTML
    """
    try:
        # If the request object has details of an authorised user, redirect them to their dashboard.
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
            user = form.get_user()
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
    """
    Web App processes logout request.
    :param request: Django request object
    :return: redirection to login page.
    """
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if user.type == 'customer':
        raise Http404('Not authorized')
    # Library function called
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
    """
    Processing data to be presented on Admin/Vendor's home page.
    :param request: Django Request object
    :return: rendered HTML
    """
    # Check if the user is an admin
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not (user.type == 'admin' or user.type == 'mess-vendor'):
        raise Http404('Not authorized')

    # Get Attendance for today and tomorrow.
    now = datetime.datetime.now(IST)
    meals = ['Breakfast', 'Lunch', 'Snacks', 'Dinner']
    attendance_qset = MessAttendance.objects.all()
    first = {}  # Today's attendance
    activef = {}  # Today's meals boolean values to tell if the meal has finished
    second = {}  # Tomorrow's attendance
    today = now.date()
    tomorrow = today + datetime.timedelta(days=1)
    qset = attendance_qset.filter(date=today)
    for j in range(len(meals)):
        tmp_qset = qset.filter(meal=meals[j])
        attendance_entry = 0
        for q in tmp_qset:
            if q.attending:
                attendance_entry += 1
        first[meals[j]] = attendance_entry
        activef[meals[j]] = now.hour < (time[meals[j]]+meal_duration)
    qset = attendance_qset.filter(date=tomorrow)
    for j in range(len(meals)):
        tmp_qset = qset.filter(meal=meals[j])
        attendance_entry = 0
        for q in tmp_qset:
            if q.attending:
                attendance_entry += 1
        second[meals[j]] = attendance_entry

    # Chart Data
    date_start = now.date()
    date_end = date_start + datetime.timedelta(days=7)
    attendance_qset = MessAttendance.objects.filter(date__range=[date_start, date_end]).order_by('date')

    chart_data_breakfast = dict()
    chart_data_lunch = dict()
    chart_data_snacks = dict()
    chart_data_dinner = dict()
    labels = list()  # To preserve the order of dates (increasing order) and not have to sort data again
    for q in attendance_qset:
        dt = q.date.strftime('%d-%m-%Y')
        if q.meal == 'Breakfast':
            if dt in chart_data_breakfast:
                chart_data_breakfast[dt] += int(q.attending)
            else:
                chart_data_breakfast[dt] = int(q.attending)
                labels.append(dt)
        elif q.meal == 'Lunch':
            if dt in chart_data_lunch:
                chart_data_lunch[dt] += int(q.attending)
            else:
                chart_data_lunch[dt] = int(q.attending)
        elif q.meal == 'Snacks':
            if dt in chart_data_snacks:
                chart_data_snacks[dt] += int(q.attending)
            else:
                chart_data_snacks[dt] = int(q.attending)
        else:  # q.meal = 'Dinner'
            if dt in chart_data_dinner:
                chart_data_dinner[dt] += int(q.attending)
            else:
                chart_data_dinner[dt] = int(q.attending)
    data_points_breakfast = [chart_data_breakfast[k] for k in labels]
    data_points_lunch = [chart_data_lunch[k] for k in labels]
    data_points_snacks = [chart_data_snacks[k] for k in labels]
    data_points_dinner = [chart_data_dinner[k] for k in labels]

    response_data = {
        'user': user,
        'first': first,
        'active': activef,
        'second': second,
        'today_date': today,
        'tom_date': tomorrow,
        'labels': labels,
        'breakfast_data': data_points_breakfast,
        'lunch_data': data_points_lunch,
        'snacks_data': data_points_snacks,
        'dinner_data': data_points_dinner
    }
    if user.type == 'admin':
        return render(request, 'Mess/home.html', response_data)
    return render(request, 'MessVendor/home.html', response_data)


def MealDeadlinePage(request):
    """
    Function to handle the Meal Deadlines page.
    :param request: Django Request object
    :return: rendered HTML
    """
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not (user.type == 'admin'):
        raise Http404('Not authorized')
    if request.method == 'POST':
        data = request.POST
        if ('meal' in data) and ('hours' in data):
            if 'date' in data:
                # Special Deadline Form
                specialDeadlineForm = MealDeadlineForm(data=data)
                item = specialDeadlineForm.save(commit=False)
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
                # Default Deadline Form
                default_deadline_form = DefaultDeadlineForm(data=data)
                item = {
                    'meal': default_deadline_form.data['meal'],
                    'hours': default_deadline_form.data['hours']
                }
                # If the entry already exists, update, otherwise add to DB
                defDeadlineQSet = DefaultDeadline.objects.filter(meal=item['meal'])
                if defDeadlineQSet.count() > 0:
                    # Entry already exists.
                    entry = DefaultDeadline.objects.get(meal=item['meal'])
                    entry.hours = item['hours']
                    entry.save()
                else:
                    # Entry does not exist
                    DefaultDeadline.objects.update_or_create(
                        meal=item['meal'],
                        hours=item['hours']
                    )
            return redirect('meal-deadline')
    else:
        # Form has not been submitted
        default_deadlines = DefaultDeadline.objects.all()
        defaultDeadlinesForms = list()
        for d in default_deadlines:
            tmpForm = DefaultDeadlineForm()
            tmp = (d, tmpForm)
            defaultDeadlinesForms.append(tmp)

        splDeadlineForm = MealDeadlineForm()
        splDeadlines = MealDeadline.objects.all()
    args = {
        'user': user,
        'splDeadlineForm': splDeadlineForm,
        'deadlines': defaultDeadlinesForms,
        'splDeadlines': splDeadlines
    }
    return render(request, 'Mess/view_deadlines.html', args)


def deleteMealDeadline(request, deadlineID):
    """
    Delete a special meal deadline entry/object
    :param request: Django request object
    :param deadlineID: remove deadline with this ID
    :return: redirection to meal deadline page.
    """
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not (user.type == 'admin'):
        raise Http404('Not authorized')
    deadline = MealDeadline.objects.get(id=deadlineID)
    deadline.delete()
    return redirect('meal-deadline')


def editMealDeadline(request):
    """
    [No longer in use] Special page for editing meal deadlines.
    :param request:
    :return:
    """
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
    """
    [No longer in use] Special page for editing default meal deadlines.
    :param request:
    :return:
    """
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
    deadlineForms = list()
    for d in deadlines:
        tmpForm = DefaultDeadlineForm()
        tmp = (d, tmpForm)
        deadlineForms.append(tmp)
    arg = {'form': form, 'deadlines': deadlineForms, 'user': user}
    return render(request, 'Mess/view_deadlines.html', arg)


def listAttendees(request):
    """
    Generate and return the list of attendees for a date and meal specified in the form (on submission)
    :param request: Django request.
    :return: rendered HTML
    """
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')
    form_data = dict()
    if request.method == 'GET':
        form = AttendeesForm()
        qset = list()
        form_data = {
            'date': '',
            'meal': ''
        }
    else:
        form = AttendeesForm(data=request.POST)
        if form.is_valid():
            form_data['date'] = form.cleaned_data['date']
            form_data['meal'] = form.cleaned_data['meal']
            qset = MessAttendance.objects.filter(date=form_data['date'])
            qset = qset.filter(meal=form_data['meal'])
        else:
            raise Http404('bad data')
    list_attendees = []
    i = 0
    cnt = 0
    for q in qset:
        cnt += 1
        if q.attending:
            tmp = dict()
            i += 1
            tmp['id'] = i
            tmp['name'] = q.user.user.name
            tmp['email'] = q.user.user.email
            list_attendees.append(tmp)
    pie_chart_data = [i, cnt]
    args = {
        'form': form,
        'list_attendees': list_attendees,
        'user': user,
        'attendees_cnt': pie_chart_data,
        'form_date': form_data['date'],
        'form_meal': form_data['meal'],
    }
    return render(request, 'Mess/list_attendees.html', args)


def customListAttendees(request, meal, day):
    """
    Generate and show a list of attendees for the meal and day passed as parameters
    :param request: Django request obj
    :param meal: (int) 0 - Breakfast, 1 - Lunch, 2 - Snacks and 3 for Dinner.
    :param day: (int) 0 for today, 1 for tomorrow.
    :return: rendered HTML
    """
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
    date = datetime.datetime.now(IST).date()
    if day == '0' or day == 0:
        pass
    elif day == '1':
        date = date + datetime.timedelta(days=1)
    else:
        raise Http404('Incorrect URL')
    qset = MessAttendance.objects.filter(date=date, meal=meal)
    list_attendees = []
    i = 0
    cnt = 0
    try:
        for q in qset:
            if q.attending:
                tmp = dict()
                i += 1
                tmp['id'] = i
                tmp['name'] = q.user.user.name
                tmp['email'] = q.user.user.email
                list_attendees.append(tmp)
            cnt += 1
    except:
        pass
    pie_chart_vars = [i, cnt]
    args = {
        'list_attendees': list_attendees,
        'user': user,
        'meal': meal,
        'date_today': date,
        'attendees_cnt': pie_chart_vars
    }
    return render(request, 'Mess/custom_list_attendees.html', args)


def getMarkedAttendanceCurMonth(request):
    """
    Renders the webpage that shows number of attendees for each meal in the current month
    :param request: Django request obj
    :return: rendered HTML
    """
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not (user.type == 'admin' or user.type == 'mess-vendor'):
        raise Http404('Not authorized')
    now = datetime.datetime.now(IST)
    response_data = dict()
    num_days = calendar.monthrange(now.year, now.month)[1]
    date_start = datetime.date(year=now.year, month=now.month, day=1)
    date_end = date_start + datetime.timedelta(days=num_days-1)
    attendance_qset = MessAttendance.objects.filter(date__range=[date_start, date_end]).order_by('date')
    for q in attendance_qset:
        if q.date in response_data:
            response_data[q.date][q.meal] += int(q.attending)
        else:
            response_data[q.date] = {'Date': q.date, 'Breakfast': 0, 'Lunch': 0, 'Snacks': 0, 'Dinner': 0}
            response_data[q.date][q.meal] += int(q.attending)
    response_data = {'response': response_data.values(), 'user': user}
    # Rendered HTML is given the number of attendees as a list of dictionaries
    # containing attendance counts for each meal for a given date.
    if user.type == 'admin':
        return render(request, 'Mess/attendance.html', response_data)
    return render(request, 'MessVendor/view_attendance.html', response_data)


def getMarkedAttendancePrevMonth(request):
    """
    [DOES NOT HAVE CORRESPONDING WEBPAGE|No longer in use]
    Renders the webpage that shows number of attendees for each meal in the coming month
    :param request: Django request obj
    :return: rendered HTML
    """
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
    """
    Upload a csv containing today's attendance for a particular meal
    :param request:
    :return:
    """
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
        if len(row) <= 1:
            break
        username = row[0]
        attended = (row[1] == '1')
        user = User.objects.get(username=username)
        mess_user = MessUser.objects.get(user=user)
        attendance_obj = qset.get(user=mess_user)
        attendance_obj.attended = attended
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
    return redirect('mess-home')


def listDefaulters(request):
    """
    Get the list of users whose marked attendance was incongruent with their physical attendance
    :param request:
    :return:
    """
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')
    defaulter_list = []
    if request.method == 'GET':
        form = AttendanceList()
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


def appFeedback(request):
    """
    Process App Feedbacks to be presented on the App Feedback page.
    :param request: Django Request Object
    :return: rendered HTML
    """
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')
    feedbackqset = AppFeedback.objects.filter(status='Sent').order_by('-timestamp')
    response_data = {
        'feedback': feedbackqset,
        'user': user
    }
    return render(request, 'Mess/app_feedback.html', response_data)


def resolvedAppFeedback(request, feedback_id):
    """
    update the app feedback status to 'Resolved' for the specified feedback
    :param request: Django request object
    :param feedback_id: ID that has to be updated
    :return: redirection to App Feedback webpage.
    """
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')

    feedback = AppFeedback(id=feedback_id)
    feedback.status = 'Resolved'
    feedback.save()
    return redirect('app-feedback')


def viewFeedback(request):
    """
    View Mess Feedback.
    :param request: Django Request Object.
    :return: rendered HTML
    """
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
    """
    [No longer in use]
    :param request:
    :param feedbackid:
    :return:
    """
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
    """
    Change status of a mess feedback object to 'Approved'
    :param request: Django request obj
    :param feedbackid: feedback id for which the status has to be updated
    :return: redirection to Mess Feedback webpage.
    """
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
    """
    Let the person providing the feedback know that further communcation will be taken up via email.
    :param request: Django request obj
    :param feedbackid: feedback id for which the status has to be updated
    :return: redirection to Mess Feedback webpage.
    """
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
    """
    View all the users registered on the app.
    :param request: Django Request Obj
    :return: rendered HTML
    """
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')
    Users = User.objects.all()
    return render(request, 'Mess/view_users.html', {'users': Users, 'user': user})


def addData(request, user_id):
    """
    [CURRENTLY NOT IN USE]
    for renewal of coupons to 20 coupons a month for a given user.
    :param request: django request object
    :param user_id: The user's id, requesting for renewal
    :return: redirection to View Users page.
    """
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
    now = datetime.datetime.now(IST)
    date_today = datetime.date(now.year, now.month, now.day)
    num_days = calendar.monthrange(date_today.year, date_today.month)[1]
    days = [(now + datetime.timedelta(days=day)) for day in range(1, num_days)]
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
    """
    Delete the data for the specified user.
    :param request: django request object
    :param user_id: ID of the user whose data is to be deleted.
    :return: redirection to View Users page.
    """
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')
    User.objects.get(id=user_id).delete()
    return redirect('view-users')


def giveAdminRights(request, user_id):
    """
    Make the specified user an admin
    :param request: django request object
    :param user_id: ID of the user who is to be made admin
    :return: redirection to View Users page.
    """
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
    """
    Take away admin rights of a user
    :param request: django request object
    :param user_id: ID of the user who is to be removed as an admin
    :return: redirection to View Users page.
    """
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
    """
    [No longer in use]
    Webpage for uploading special (occasional) mess menu
    :param request:
    :return:
    """
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
    """
    [No longer in use]
    Webpage for uploading weekly mess menu
    :param request:
    :return:
    """
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
            item_entry.items = item.items
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
    """
    Processing data for View Menu Webpage
    :param request: django request object
    :return: rendered HTML
    """
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')
    args = dict()
    meals = {'Breakfast': 0, 'Lunch': 1, 'Snacks': 2, 'Dinner': 3}
    # Default Menu - i.e. weekly
    weekly_menu = DefaultMessMenu.objects.all()
    weekly_menu_table = {}
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                'Friday', 'Saturday', 'Sunday']
    for day in weekdays:
        weekly_menu_table[day] = ['-' for k in range(4)]
    for it in weekly_menu:
        tmp = meals[it.meal]
        form = DefaultMessMenuForm()
        spl_menu = it.special_menu
        egg = it.contains_egg
        chi = it.contains_chicken
        weekly_menu_table[it.day][tmp] = (it, form, spl_menu, egg, chi)

    # Search for Custom Menu - i.e. date wise
    if request.method == 'POST':
        form = DefaultMessMenuForm(data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            entry = DefaultMessMenu.objects.get(day=data['day'], meal=data['meal'])
            entry.items = data['items']
            entry.special_menu = data['special_menu']
            entry.contains_egg = data['contains_egg']
            entry.contains_chicken = data['contains_chicken']
            entry.save()
            return redirect('admin-view-mess-menu')
        else:
            form2 = MessMenuForm(data=request.POST)
            if form2.is_valid():
                data = form2.cleaned_data
                MessMenu.objects.update_or_create(
                    date=data['date'],
                    meal=data['meal'],
                    occasion=data['occasion'],
                    items=data['items']
                )
                return redirect('admin-view-mess-menu')
    else:
        form2 = MessMenuForm()
    splmenu = MessMenu.objects.all()
    args['list'] = splmenu
    args['user'] = user
    args['weekly_menu'] = weekly_menu_table
    args['form2'] = form2
    return render(request, 'Mess/view_menu.html', args)


def deleteMessMenuItem(request, itemid):
    """
    Delete Mess Menu entry for a special Mess Menu
    :param request: django request obj
    :param itemid: id of the item to be deleted.
    :return: redirection to view mess menu page.
    """
    try:
        user = User.objects.get(username=request.user)
    except:
        raise Http404('Not authorized')
    if not user.type == 'admin':
        raise Http404('Not authorized')
    menu_entry = MessMenu.objects.get(id=itemid)
    menu_entry.delete()
    return redirect('admin-view-mess-menu')


# _____________________________________Extra - Random Functions_______________________________
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
            # print(user.username, '*************')
            try:
                mess_user = MessUser.objects.get(user=user)
                cnt = MessAttendance.objects.filter(user=mess_user).count()
                # print(cnt)
                cntr += 1
            except:
                pass
                # print('!!!!!!!!!!!!!!!!!!!!!!', user.username)
        else:
            pass
            # print(user.username, 'hjcvjhdvd', user.type)
    # print('total_customers', cntr)
    return redirect('default-deadline')


def automated_midnight_checks():
    pass
