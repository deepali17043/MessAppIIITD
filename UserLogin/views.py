import csv, io
import pytz, ast
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic import CreateView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser

from .forms import CustomUserCreationForm, AddMenuItem
from .models import User, MenuItems, Cart, MessUser, MessAttendance
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.urls import resolve
import datetime, calendar
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


# _________________________________________________________________________________________________


IST = pytz.timezone('Asia/Kolkata')

class SignUp(CreateView):
    form_class = CustomUserCreationForm
    success_url = '/login/'

    def __init__(self):
        self.template_name = 'signup.html'


class UserRecordView(APIView):
    """
    API View to create or get a list of all the registered
    users. GET request returns the registered users whereas
    a POST request allows to create a new user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        # print(request.data)
        if serializer.is_valid(raise_exception=ValueError):
            serializer.create(validated_data=request.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                "error": True,
                "error_msg": serializer.error_messages,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


# _________________________________________________________________________________________________


def homePage(request):
    # create account or login to existing.
    return render(request, 'home.html')


def loginUser(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        form.fields['username'].widget.attrs['placeholder'] = 'Username'
        form.fields['username'].label = ''
        form.fields['password'].widget.attrs['placeholder'] = 'Password'
        form.fields['password'].label = ''
        if form.is_valid():
            # print(form)
            user = form.get_user()
            login(request, user)
        else:
            raise Http404('invalid')
    else:
        form = AuthenticationForm()
        form.fields['username'].widget.attrs['placeholder'] = 'Username'
        form.fields['username'].label = ''
        form.fields['password'].widget.attrs['placeholder'] = 'Password'
        form.fields['password'].label = ''
    return render(request, 'registration/login.html', {'form': form})


def logoutuser(request):
    user = User.objects.get(username=request.user.username)
    user.deAuthenticateUser()
    logout(request)
    return redirect('signin')


@api_view(['POST', ])
def signup(request):
    serializer = RegistrationSerializer(data=request.data)
    return_data = {}
    if serializer.is_valid():
        user_account = serializer.save()
        return_data['response'] = 'successful registration'
        return_data['username'] = user_account.username
        return_data['email'] = user_account.email
        return_data['type'] = user_account.type
    else:
        return_data = serializer.errors
    return Response(return_data)


def dashboard(request):
    user = User.objects.get(username=request.user.username)
    if user.type == 'vendor':
        return vendorDashboard(request)
    elif user.type == 'customer':
        vendors = User.objects.all().filter(type='vendor')
        args = {'vendors': vendors, }
        return render(request, 'Customer/Home.html', args)
    raise Http404('invalid user type')


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def dashboardAPI(request):
    user = request.user
    if user.type == 'vendor':
        return vendorDashboardAPI(request)
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vendorDashboardAPI(request):
    vendor = request.user
    orders = Cart.objects.filter(item__vendor=vendor, orderPlaced=1).exclude(status='Prepared') \
        .order_by('orderTime')
    serializer = CartSerializer(orders, many=True)
    return Response(serializer.data)


def checkVendor(request):
    user = User.objects.get(username=request.user.username)
    if user.type == 'customer':
        raise Http404('Invalid URL')


def vendorMenu(request):
    checkVendor(request)
    menu = MenuItems.objects.filter(vendor=request.user, hidden=False)
    args = {'menu': menu, }
    return render(request, 'Vendor/Menu.html', args)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def vendorMenuAPI(request):
    checkVendor(request)
    menu = MenuItems.objects.filter(vendor=request.user, hidden=False)
    serializer = MenuItemsSerializer(menu, many=True)
    return Response(serializer.data)


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


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def addItemAPI(request):
    checkVendor(request)
    serializer = MenuItemsSerializer(request.data)
    response_data = {}
    if serializer.is_valid():
        item = serializer.save()
        # print(item)
        response_data['response'] = 'successful addition to menu'
        response_data['itemName'] = item.itemName
        response_data['vendor'] = item.vendor
        response_data['price'] = item.price
        response_data['hidden'] = item.hidden
    else:
        response_data = serializer.errors
    return Response(response_data)


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


class UploadMenuItems(APIView):
    parser_classes = [FileUploadParser, ]
    permission_classes = [IsAuthenticated, ]

    def post(self, request, format=None):
        if 'file' not in request.data:
            raise ParseError('Empty Content')
        file = request.headers['file']
        if not file.name.endswith('.csv'):
            raise Http404('THIS IS NOT A CSV FILE')
        data_set = file.read().decode('UTF-8')
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
        return Response(status=status.HTTP_201_CREATED)


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


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def removeItemsAPI(request):
    checkVendor(request)
    menu = MenuItems.objects.filter(vendor=request.user)
    serializer = MenuItemsSerializer(menu, many=True)
    return Response(serializer.data)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def removeMenuItemAPI(request):
    checkVendor(request)
    id = request.headers['id']
    instance = MenuItems.objects.get(id=id)
    instance.delete()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def hideItemsAPI(request):
    checkVendor(request)
    menu = MenuItems.objects.filter(vendor=request.user, hidden=False)
    serializer = MenuItemsSerializer(menu, many=True)
    return Response(serializer.data)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def hideMenuItemAPI(request):
    checkVendor(request)
    id = request.headers['id']
    instance = MenuItems.objects.get(id=id)
    instance.hidden = True
    instance.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def unHideItemsAPI(request):
    checkVendor(request)
    menu = MenuItems.objects.filter(vendor=request.user, hidden=True)
    serializer = MenuItemsSerializer(menu, many=True)
    return Response(serializer.data)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def unHideMenuItemAPI(request):
    checkVendor(request)
    id = request.headers['id']
    instance = MenuItems.objects.get(id=id)
    instance.hidden = False
    instance.save()
    return Response(status=status.HTTP_200_OK)


def vendorFines(request):
    pass


def vendorFeedback(request):
    pass


def vendorProfile(request):
    pass


def vendorSettings(request):
    pass


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


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated, ])
def updateOrderStatusAPI(request):
    checkVendor(request)
    vendor = request.user
    cartItemId = request.headers['cartItemID']
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
    response_data = {
        'response' : 'successfully updated'
    }
    return Response(response_data)


# ===========================================Customer==============================================
def checkCustomer(request):
    user = request.user
    if user.type == 'vendor':
        raise Http404('invalid Url')
    return


def viewVendorMenu(request, vendorID):
    checkCustomer(request)
    vendor = User.objects.get(id=vendorID)
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
    menu_row = []
    for i in range(len(Menu) // 4 + 1):
        tmp = []
        for j in range(i * 4, min((i + 1) * 4, len(Menu))):
            tmp.append(Menu[j])
        menu_row.append(tmp)
    cart_row = []
    for i in range(len(cart) // 4 + 1):
        tmp = []
        for j in range(i * 4, min((i + 1) * 4, len(cart))):
            tmp.append(cart[j])
        cart_row.append(tmp)
    ordered_row = []
    for i in range(len(ordered) // 4 + 1):
        tmp = []
        for j in range(i * 4, min((i + 1) * 4, len(ordered))):
            tmp.append(ordered[j])
        ordered_row.append(tmp)
    args = {'menu_row': menu_row, 'cart_row': cart_row, 'vendorID': vendorID, 'ordered_row': ordered_row}
    return render(request, 'Customer/Menu.html', args)


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


def selectvendor(request):
    pass


def selectitem(request, id):
    pass


def addToCart(request, vendorID, itemID):
    checkCustomer(request)
    item = MenuItems.objects.get(id=itemID)
    vendor = User.objects.get(id=vendorID)
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
    url = request.build_absolute_uri('/accounts/view-vendor-menu/') + str(vendorID)
    return redirect(url)


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
    response_data = { 'cart' : customer_cart}
    return Response(response_data)


def reduceQty(request, vendorId, itemId):
    item = Cart.objects.get(id=itemId)
    menu_item = MenuItems.objects.get(id=item.item.id)
    vendor = User.objects.get(id=vendorId)
    checkCustomer(request)
    user = request.user
    if vendor.type != 'vendor' or menu_item.vendor != vendor or item.customer != user:
        raise Http404('The URL has some error')
    item.qty -= 1
    if item.qty == 0:
        item.delete()
    else:
        item.save()
    url = request.build_absolute_uri('/accounts/view-vendor-menu/') + str(vendorId)
    # print(url)
    return redirect(url)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def reduceQtyAPI(request):
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


def increaseQty(request, vendorId, itemId):
    item = Cart.objects.get(id=itemId)
    menu_item = MenuItems.objects.get(id=item.item.id)
    vendor = User.objects.get(id=vendorId)
    checkCustomer(request)
    user = request.user
    if vendor.type != 'vendor' or menu_item.vendor != vendor or item.customer != user:
        raise Http404('The URL has some error')

    item.qty += 1
    item.save()

    url = request.build_absolute_uri('/accounts/view-vendor-menu/') + str(vendorId)
    # print(url)
    return redirect(url)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def increaseQtyAPI(request):
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


def viewCart(request):
    checkCustomer(request)
    user = request.user
    items = Cart.objects.all().filter(customer=user, orderPlaced=0)
    total = 0
    cart = []
    for i in items:
        tmp = i.qty * i.item.price
        total += tmp
        serialized_i = CartSerializer(i)
        cart.append({'item': serialized_i, 'price*qty': tmp})
    args = {'total': total, 'cart': cart}
    return render(request, 'Customer/ViewCart.html', args)


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


def placeOrder(request):
    checkCustomer(request)
    user = request.user
    items = Cart.objects.all().filter(customer=user).exclude(orderPlaced=2)
    for i in items:
        i.orderPlaced = 1
        i.orderTime = datetime.datetime.now(IST)
        if i.status == 'Added to Cart':
            i.status = 'Order Placed'
        i.save()
    return redirect('order-details')


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


def orderDetails(request):
    checkCustomer(request)
    user = request.user
    items = Cart.objects.all().filter(customer=user, orderPlaced=1)
    total = 0
    cart = []
    for i in items:
        tmp = i.item.price * i.qty
        total += tmp
        k = i.status == 'Prepared'
        cart.append((i, tmp, k))
    args = {'cart': cart, 'total': total}
    return render(request, 'Customer/OrderDetails.html', args)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def orderDetailsAPI(request):
    user = request.user
    items = Cart.objects.all().filter(customer=user, orderPlaced=1)
    total = 0
    cart = []
    for i in items:
        tmp = i.item.price * i.qty
        total += tmp
        k = i.status == 'Prepared'
        serialized_i = CartSerializer(i)
        cart.append({'item':serialized_i, 'price*qty': tmp, 'prepared':k})
    # print(cart)
    args = {'cart': cart, 'total': total}
    return Response(args)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def collectedOrderAPI(request):
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
    user = request.user
    # print(user.username)
    mess_user = MessUser.objects.get(user=user)
    now = datetime.datetime.now(IST)
    date_today = datetime.date.today()
    upcoming_attendance = []
    meals = ['Breakfast', 'Lunch', 'Snacks', 'Dinner']
    timings = [8, 13, 17, 20]
    days = [0, 1, 2]  # cur, next and day after
    for i in days:
        for j in range(len(meals)):
            deadline_time = now + datetime.timedelta(hours=3)
            q_date = date_today + datetime.timedelta(days=i)
            # print(q_date)
            attendance_entry = MessAttendance.objects.get(date=q_date, meal=meals[j], user=mess_user)
            if deadline_time.hour < timings[j] or i > 0:
                attendance_entry.attending = False
                attendance_entry.save()
            upcoming_attendance.append(attendance_entry)
    attendance_serializer = MessAttendanceSerializer(upcoming_attendance, many=True)
    serialized_user = MessUserSerializer(mess_user)
    response_data = {
        'deadline_time': deadline_time,
        'attendance': attendance_serializer.data,
        'mess_user': serialized_user.data
    }
    return Response(response_data)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def messScheduleAPI(request):
    mess_user = MessUser.objects.get(user=request.user)
    month = int(request.headers['month'])
    # print('mess-schedule', month)
    year = int(request.headers['year'])
    # print('mess-schedule', year)
    now = datetime.datetime.now(IST)
    date_today = datetime.date(now.year, now.month, now.day)
    attendance = []
    cur_month = date_today.month
    if month != cur_month and month != cur_month+1:
        # print('...')
        raise Http404('Schedule not ready for this month')
    num_days = calendar.monthrange(year, month)[1]
    days = [datetime.date(year, month, day) for day in range(1, num_days+1)]
    meals = ['Breakfast', 'Lunch', 'Snacks', 'Dinner']
    attendance_qset = MessAttendance.objects.all().filter(user=mess_user)
    for day in days:
        qset = attendance_qset.filter(date=day)
        for j in range(len(meals)):
            attendance_entry = qset.get(meal=meals[j])
            attendance.append(attendance_entry)
            # print(attendance_entry.attending, attendance_entry.meal)
            # print(attendance_entry.date, meals[j])
    serializer = MessAttendanceSerializer(attendance, many=True)
    # print(serializer)
    # print(serializer.data)
    response_data = {
        'attendance':
            serializer.data
    }
    return Response(response_data)


def editable_meal(meal, now):
    # print(now)
    if meal == 'Breakfast':
        meal_deadline = 5
    elif meal == 'Lunch':
        meal_deadline = 10
    elif meal == 'Snacks':
        meal_deadline = 14
    else:
        meal_deadline = 17
    # print(now.hour, "sudbcksbuvdbdfkviudbvodn")
    if now.hour < meal_deadline:
        return True
    return False


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def editMessScheduleAPI(request):
    user = request.user
    mess_user = MessUser.objects.get(user=user)
    edit_attendance = ast.literal_eval(request.headers['attendance'])
    print(edit_attendance, type(edit_attendance))
    """ attendance (list of dictionaries) - date, meals(list of meals) """
    attendance_qset = MessAttendance.objects.all().filter(user=mess_user)
    # print(attendance_qset)
    response_data = {}
    now = datetime.datetime.now(IST)
    date_today = datetime.date(now.year, now.month, now.day)
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
            tmp = qset.get(meal=meal)
            if editable_meal(meal, now) or date_today < date_cur:
                tmp.attending = not tmp.attending
                tmp.save()
            else:
                response_data['message'] = 'some dates are not editable'
    response_data['status'] = status.HTTP_200_OK
    return Response(response_data)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def editNextMealAPI(request):
    mess_user = MessUser(user=request.user)
    choice = bool(request.headers['response'])
    now = datetime.datetime.now(IST) + datetime.timedelta(hours=3)
    y = now.year
    m = now.month
    d = now.day
    hr = now.hour
    if hr < 8:
        meal = 'BreakFast'
    elif hr < 13:
        meal = 'Lunch'
    elif hr < 17:
        meal = 'Snacks'
    elif hr < 20:
        meal = 'Dinner'
    else:
        now = now + datetime.timedelta(hours=7)
        y = now.year
        m = now.month
        d = now.day
    next_meal_date = datetime.date(y, m, d)
    attendance_obj = MessAttendance.objects.get(user=mess_user, meal=meal, date=next_meal_date)
    attendance_obj.attending = choice
    attendance_obj.save()
    return Response(status=status.HTTP_200_OK)


def add1month(now):
    month = now.month
    year = now.year + month//12
    month = month % 12 + 1
    ret_date = datetime.date(year, month, now.day)
    return ret_date


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def addData(request):
    user = request.user
    MessUser.objects.update_or_create(user=user)
    mess_user = MessUser.objects.get(user=user)
    # print(user)
    # print(mess_user.id)
    now = datetime.datetime.now(IST)
    date_today = datetime.date(now.year, now.month, now.day)
    num_days = calendar.monthrange(date_today.year, date_today.month)[1]
    days_cur_month = [datetime.date(date_today.year, date_today.month, day) for day in range(1, num_days + 1)]
    date_today = add1month(date_today)
    num_days = calendar.monthrange(date_today.year, date_today.month)[1]
    days_next_month = [datetime.date(date_today.year, date_today.month, day) for day in range(1, num_days + 1)]
    days = days_cur_month + days_next_month
    meals = ['Breakfast', 'Lunch', 'Snacks', 'Dinner']
    for day in days:
        for j in meals:
            MessAttendance.objects.update_or_create(
                user=mess_user,
                meal=j,
                date=day,
            )
    return Response(status=status.HTTP_201_CREATED)
