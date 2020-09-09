import csv, io
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic import CreateView
from rest_framework.decorators import api_view

from .forms import CustomUserCreationForm, AddMenuItem
from .models import User, MenuItems, Cart
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.urls import resolve
import datetime
from . serializer import UserSerializer, CartSerializer, MenuItemsSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser


# _________________________________________________________________________________________________


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
    permission_classes = [IsAdminUser]

    def get(self, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
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
            print(form)
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


def dashboard(request):
    user = User.objects.get(username=request.user.username)
    if user.userType == 'vendor':
        return vendorDashboard(request)
    elif user.userType == 'customer':
        vendors = User.objects.all().filter(userType='vendor')
        args = {'vendors': vendors, }
        return render(request, 'Customer/Home.html', args)
    raise Http404('invalid user type')


@api_view(['GET'])
def dashboardAPI(request):
    user = User.objects.get(username=request.headers['username'])
    if user.userType == 'vendor':
        return vendorDashboardAPI(request)
    elif user.userType == 'customer':
        vendors = User.objects.all().filter(userType='vendor')
        serializer = UserSerializer(vendors, many=True)
        return Response(serializer.data)
    raise Http404('invalid user type')


# ============================================Vendor===============================================


def vendorDashboard(request):
    orders = Cart.objects.filter(item__vendor=request.user, orderPlaced=1).exclude(status='Prepared')\
        .order_by('orderTime')
    args = {'orders': orders, }
    return render(request, 'Vendor/Home.html', args)


@api_view(['GET'])
def vendorDashboardAPI(request):
    orders = Cart.objects.filter(item__vendor=request.user, orderPlaced=1).exclude(status='Prepared') \
        .order_by('orderTime')
    serializer = CartSerializer(orders, many=True)
    return Response(serializer.data)


def checkVendor(request):
    user = User.objects.get(username=request.user.username)
    if user.userType == 'customer':
        raise Http404('Invalid URL')


def vendorMenu(request):
    checkVendor(request)
    menu = MenuItems.objects.filter(vendor=request.user, hidden=False)
    args = {'menu': menu, }
    return render(request, 'Vendor/Menu.html', args)


@api_view(['GET'])
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


def addItems(request):
    if request.method == 'GET':
        return render(request, 'Vendor/AddMenuItems.html')

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        raise Http404('THIS IS NOT A CSV FILE')
    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    for row in csv.reader(io_string, delimiter=',', quotechar="|"):
        print(row)
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


# ===========================================Customer==============================================
def checkCustomer(request):
    user = request.user
    if user.userType == 'vendor':
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
    for i in range(len(Menu)//4 + 1):
        tmp = []
        for j in range(i*4, min((i+1)*4, len(Menu))):
            tmp.append(Menu[j])
        menu_row.append(tmp)
    cart_row = []
    for i in range(len(cart)//4 + 1):
        tmp = []
        for j in range(i*4, min((i+1)*4, len(cart))):
            tmp.append(cart[j])
        cart_row.append(tmp)
    ordered_row = []
    for i in range(len(ordered)//4 + 1):
        tmp = []
        for j in range(i*4, min((i+1)*4, len(ordered))):
            tmp.append(ordered[j])
        ordered_row.append(tmp)
    args = {'menu_row': menu_row, 'cart_row': cart_row, 'vendorID': vendorID, 'ordered_row': ordered_row}
    return render(request, 'Customer/Menu.html', args)


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
    for i in it:
        print(i)
        print(i.item.itemName, i.status)
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


def reduceQty(request, vendorId, itemId):
    item = Cart.objects.get(id=itemId)
    menu_item = MenuItems.objects.get(id=item.item.id)
    vendor = User.objects.get(id=vendorId)
    checkCustomer(request)
    user = request.user
    if vendor.userType != 'vendor' or menu_item.vendor != vendor or item.customer != user:
        raise Http404('The URL has some error')

    item.qty -= 1
    if item.qty == 0:
        item.delete()
    else:
        item.save()

    url = request.build_absolute_uri('/accounts/view-vendor-menu/') + str(vendorId)
    print(url)
    return redirect(url)


def increaseQty(request, vendorId, itemId):
    item = Cart.objects.get(id=itemId)
    menu_item = MenuItems.objects.get(id=item.item.id)
    vendor = User.objects.get(id=vendorId)
    checkCustomer(request)
    user = request.user
    if vendor.userType != 'vendor' or menu_item.vendor != vendor or item.customer != user:
        raise Http404('The URL has some error')

    item.qty += 1
    item.save()

    url = request.build_absolute_uri('/accounts/view-vendor-menu/') + str(vendorId)
    print(url)
    return redirect(url)


def viewCart(request):
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
    return render(request, 'Customer/ViewCart.html', args)


def placeOrder(request):
    checkCustomer(request)
    user = request.user
    items = Cart.objects.all().filter(customer=user).exclude(orderPlaced=2)
    for i in items:
        i.orderPlaced = 1
        i.orderTime = datetime.datetime.now()
        if i.status == 'Added to Cart':
            i.status = 'Order Placed'
        i.save()
    return redirect('order-details')


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


def collectedOrder(request, orderId):
    checkCustomer(request)
    user = request.user
    item = Cart.objects.get(id=orderId)
    item.orderPlaced = 2
    item.status = 'Collected'
    item.save()
    return redirect('order-details')
