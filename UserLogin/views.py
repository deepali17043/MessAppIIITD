import csv, io
from django.http import Http404
from django.shortcuts import render, redirect
# from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from .forms import CustomUserCreationForm, AddMenuItem
from .models import User, MenuItems
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.forms import Form

# Create your views here.


# ___________________________CLASSES_________________________________


class SignUp(CreateView):
    form_class = CustomUserCreationForm
    success_url = '/login/'

    def __init__(self):
        self.template_name = 'signup.html'


# ___________________________Functions_________________________________


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
        return render(request, 'Vendor/Home.html')
    elif user.userType == 'customer':
        return render(request, 'Customer/Home.html')
    raise Http404('invalid user type')


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
