from . import views
from django.urls import path, include
from django.conf.urls import url

urlpatterns = [
    path('', views.homePage, name='HomePage'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('login/', views.loginUser, name="SignIn"),
    path('logout/', views.logoutuser, name='logout'),

    path('accounts/dashboard/', views.dashboard, name='personalised-dashboard'),

    path('vendor/menu/', views.vendorMenu, name='vendor-menu'),
    path('vendor/menu/additem/', views.addItem, name='add-item'),
    path('vendor/menu/additems/', views.addItems, name='add-items'),
    path('vendor/menu/removeitem/', views.removeItems, name='remove-item'),
    url(r'^vendor/menu/removeitem/(?P<id>\d+)/', views.removeMenuItem, name='vendor-delete-menu-item'),
    path('vendor/menu/hideitem/', views.hideItems, name='hide-item'),
    url(r'^vendor/menu/hideitem/(?P<id>\d+)/', views.hideMenuItem, name='vendor-hide-menu-item'),
    path('vendor/menu/unhideitem/', views.unHideItems, name='un-hide-item'),
    url(r'^vendor/menu/unhideitem/(?P<id>\d+)/', views.unHideMenuItem, name='vendor-un-hide-menu-item'),

    path('vendor/fines/', views.vendorFines, name='vendor-fines'),

    path('vendor/feedback/', views.vendorFeedback, name='vendor-feedback'),

    path('vendor/profile/', views.vendorProfile, name='vendor-profile'),

    path('vendor/settings/', views.vendorSettings, name='vendor-settings'),
]
