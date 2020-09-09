from . import views
from django.urls import path
from django.conf.urls import url

urlpatterns = [
    path('', views.homePage, name='HomePage'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('login/', views.loginUser, name='signin'),
    path('logout/', views.logoutuser, name='logout'),

    path('accounts/dashboard/', views.dashboard, name='personalised-dashboard'),

    path('accounts/view-vendor-menu/', views.selectvendor, name='view-vendor'),
    url(r'^accounts/view-vendor-menu/(?P<vendorID>\d+)/$', views.viewVendorMenu, ),
    url(r'^accounts/view-vendor-menu/(?P<id>\d+)/add-to-cart/$', views.selectitem, name='add-to-cart'),
    url(r'^accounts/view-vendor-menu/(?P<vendorID>\d+)/add-to-cart/(?P<itemID>\d+)/$', views.addToCart, ),
    url(r'^accounts/view-vendor-menu/(?P<vendorId>\d+)/reduce-qty/(?P<itemId>\d+)/$',
        views.reduceQty, name='reduce-qty'),
    url(r'^accounts/view-vendor-menu/(?P<vendorId>\d+)/increase-qty/(?P<itemId>\d+)/$',
        views.increaseQty, name='increase-qty'),
    path('accounts/view-cart/', views.viewCart, name='view-cart'),
    path('accounts/place-order/', views.placeOrder, name='place-order'),
    path('accounts/order-details/', views.orderDetails, name='order-details'),
    url(r'^accounts/order-details/(?P<orderId>\d+)/', views.collectedOrder, name='collected-order'),

    url(r'^vendor/update-order-status/(?P<cartItemId>\d+)/', views.updateOrderStatus, name='update-order-status'),
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

    #apis
    path('user/', views.UserRecordView.as_view(), name='users'), #login/authenticate

    path('user/dashboard/', views.dashboardAPI, name='dashAPI'),
    path('user/vendor/menu/', views.vendorMenuAPI, name='vendor-menu-api'),
]
