from . import views
from django.urls import path
from django.conf.urls import url

urlpatterns = [
    path('', views.homePage, name='HomePage'),
    path('signup/', views.signup, name='signup'),
    # path('login/', views.loginUser, name='signin'),
    # path('logout/', views.logoutuser, name='logout'),

    path('accounts/dashboard/', views.dashboardAPI, name='personalised-dashboard'),

    # path('accounts/view-vendor-menu/', views.selectvendor, name='view-vendor'),
    url(r'^accounts/view-vendor-menu/$', views.viewVendorMenuAPI, name='view-vendor-menu'),
    # url(r'^accounts/view-vendor-menu/(?P<id>\d+)/add-to-cart/$', views.selectitem, name='add-to-cart'),
    # url(r'^accounts/view-vendor-menu/(?P<vendorID>\d+)/add-to-cart/(?P<itemID>\d+)/$', views.addToCart, ),
    url(r'^accounts/view-vendor-menu/add-to-cart/$', views.addToCartAPI, name='add-to-cart'),
    # url(r'^accounts/view-vendor-menu/(?P<vendorId>\d+)/reduce-qty/(?P<itemId>\d+)/$',
    #     views.reduceQty, name='reduce-qty'),
    url(r'^accounts/view-vendor-menu/reduce-qty/$', views.reduceQtyAPI, name='reduce-qty'),
    # url(r'^accounts/view-vendor-menu/(?P<vendorId>\d+)/increase-qty/(?P<itemId>\d+)/$',
    #     views.increaseQty, name='increase-qty'),
    url(r'^accounts/view-vendor-menu/increase-qty/$', views.increaseQtyAPI, name='increase-qty'),
    path('accounts/view-cart/', views.viewCartAPI, name='view-cart'),
    path('accounts/place-order/', views.placeOrderAPI, name='place-order'),
    path('accounts/order-details/', views.orderDetailsAPI, name='order-details'),
    url(r'^accounts/update-order-status/$', views.collectedOrderAPI, name='collected-order'),

    # url(r'^vendor/update-order-status/(?P<cartItemId>\d+)/', views.updateOrderStatus, name='update-order-status'),
    # path('vendor/menu/', views.vendorMenu, name='vendor-menu'),
    # path('vendor/menu/additem/', views.addItem, name='add-item'),
    # path('vendor/menu/additems/', views.addItems, name='add-items'),
    # path('vendor/menu/removeitem/', views.removeItems, name='remove-item'),
    # url(r'^vendor/menu/removeitem/(?P<id>\d+)/', views.removeMenuItem, name='vendor-delete-menu-item'),
    # path('vendor/menu/hideitem/', views.hideItems, name='hide-item'),
    # url(r'^vendor/menu/hideitem/(?P<id>\d+)/', views.hideMenuItem, name='vendor-hide-menu-item'),
    # path('vendor/menu/unhideitem/', views.unHideItems, name='un-hide-item'),
    # url(r'^vendor/menu/unhideitem/(?P<id>\d+)/', views.unHideMenuItem, name='vendor-un-hide-menu-item'),

    url(r'^vendor/update-order-status/$', views.updateOrderStatusAPI, name='update-order-status'),
    path('vendor/menu/', views.vendorMenuAPI, name='vendor-menu'),
    path('vendor/menu/additem/', views.addItemAPI, name='add-item'),
    path('vendor/menu/additems/', views.UploadMenuItems.as_view(), name='add-items'),
    path('vendor/menu/removeitem/', views.removeItemsAPI, name='remove-item'),
    url(r'^vendor/menu/removeitem/$', views.removeMenuItemAPI, name='vendor-delete-menu-item'),
    path('vendor/menu/hideitem/', views.hideItemsAPI, name='hide-item'),
    url(r'^vendor/menu/hideitem/$', views.hideMenuItemAPI, name='vendor-hide-menu-item'),
    path('vendor/menu/unhideitem/', views.unHideItemsAPI, name='un-hide-item'),
    url(r'^vendor/menu/unhideitem/$', views.unHideMenuItemAPI, name='vendor-un-hide-menu-item'),

    path('accounts/home/', views.messAttendanceAPI, name='mess-home'),
    path('accounts/schedule/', views.messScheduleAPI, name='mess-schedule'),
    path('accounts/schedule/edit/', views.editMessScheduleAPI, name='edit-mess-schedule'),
    path('api/accounts/next-meal/', views.editNextMealAPI, name='edit-next-meal'),
    path('dummy/add-data/', views.addData, name='add-data'),

    # apis
    path('user/', views.UserRecordView.as_view(), name='users'),  # login/authenticate
]
