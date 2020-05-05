import csv, io
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic import CreateView
from .forms import CustomUserCreationForm, AddMenuItem
from .models import User, MenuItems, Cart
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.urls import resolve


# _________________________________________________________________________________________________


class SignUp(CreateView):
    form_class = CustomUserCreationForm
    success_url = '/login/'

    def __init__(self):
        self.template_name = 'signup.html'


# _________________________________________________________________________________________________


def homePage(request):
    # create account or login to existing.
    return render(request, 'home.html')


def loginUser(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
        else:
            raise Http404('invalid')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logoutuser(request):
    user = User.objects.get(username=request.user.username)
    user.deAuthenticateUser()
    logout(request)
    url = request.build_absolute_uri('/').strip("/") + "/login"
    return redirect(url)


def dashboard(request):
    user = User.objects.get(username=request.user.username)
    if user.userType == 'vendor':
        return vendorDashboard(request)
    elif user.userType == 'customer':
        vendors = User.objects.all().filter(userType='vendor')
        args = {'vendors': vendors, }
        return render(request, 'Customer/Home.html', args)
    raise Http404('invalid user type')


# ============================================Vendor===============================================


def vendorDashboard(request):
    return render(request, 'Vendor/Home.html')


def checkVendor(request):
    user = User.objects.get(username=request.user.username)
    if user.userType == 'customer':
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


# ===========================================Customer==============================================
def checkCustomer(request):
    user = request.user
    if user.userType == 'vendor':
        raise Http404('invalid Url')
    return


def viewVendorMenu(request, vendorID):
    checkCustomer(request)
    vendor = User.objects.get(id=vendorID)
    menu = MenuItems.objects.all().filter(vendor=vendor)
    cart = Cart.objects.all().filter(customer=request.user, status='Added to Cart')
    Menu = list()
    for i in menu:
        Menu.append(i)
    for i in cart:
        Menu.remove(i.item)
    print(menu)
    print(cart)
    print(Menu)
    args = {'menu': Menu, 'cart': cart, 'vendorID': vendorID}
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
    if len(it) == 0:
        Cart.objects.update_or_create(
            item=item,
            customer=request.user
        )
    else:
        for i in it:
            i.qty += 1
            i.save()
    url = request.build_absolute_uri('/accounts/view-vendor-menu/') + str(vendorID)
    print(url)
    return redirect(url)


def reduceQty(request, vendorId, itemId):
    menu_item = MenuItems.objects.get(id=itemId)
    item = Cart.objects.get(item=menu_item)
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
    menu_item = MenuItems.objects.get(id=itemId)
    item = Cart.objects.get(item=menu_item)
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
    for i in items:
        total += i.qty * i.item.price
    args = {'total': total, 'cart': items}
    return render(request, 'Customer/ViewCart.html', args)


def placeOrder(request):
    checkCustomer(request)
    user = request.user
    items = Cart.objects.all().filter(customer=user).exclude(orderPlaced=2)
    total = 0
    for i in items:
        i.orderPlaced = 1
        i.status = 'Order Placed'
        i.save()
        total += i.qty * i.item.price
    args = {'total': total, 'cart': items}
    return render(request, 'Customer/OrderDetails.html', args)
