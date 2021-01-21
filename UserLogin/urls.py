from . import views
from django.urls import path
from django.conf.urls import url

urlpatterns = [
    path('', views.homePage, name='HomePage'),
    path('api/signup/', views.signup, name='signup'),
    path('api/logout/', views.logoutuser, name='logout'),

    path('api/accounts/dashboard/', views.dashboardAPI, name='personalised-dashboard'),

    # path('accounts/view-vendor-menu/', views.selectvendor, name='view-vendor'),
    url(r'^api/accounts/view-vendor-menu/$', views.viewVendorMenuAPI, name='view-vendor-menu'),
    # url(r'^accounts/view-vendor-menu/(?P<id>\d+)/add-to-cart/$', views.selectitem, name='add-to-cart'),
    # url(r'^accounts/view-vendor-menu/(?P<vendorID>\d+)/add-to-cart/(?P<itemID>\d+)/$', views.addToCart, ),
    url(r'^api/accounts/view-vendor-menu/add-to-cart/$', views.addToCartAPI, name='add-to-cart'),
    # url(r'^accounts/view-vendor-menu/(?P<vendorId>\d+)/reduce-qty/(?P<itemId>\d+)/$',
    #     views.reduceQty, name='reduce-qty'),
    url(r'^api/accounts/view-vendor-menu/reduce-qty/$', views.reduceQtyAPI, name='reduce-qty'),
    # url(r'^accounts/view-vendor-menu/(?P<vendorId>\d+)/increase-qty/(?P<itemId>\d+)/$',
    #     views.increaseQty, name='increase-qty'),
    url(r'^api/accounts/view-vendor-menu/increase-qty/$', views.increaseQtyAPI, name='increase-qty'),
    path('api/accounts/view-cart/', views.viewCartAPI, name='view-cart'),
    path('api/accounts/place-order/', views.placeOrderAPI, name='place-order'),
    path('api/accounts/order-details/', views.orderDetailsAPI, name='order-details'),
    url(r'^api/accounts/update-order-status/$', views.collectedOrderAPI, name='collected-order'),

    path('api/accounts/home/', views.messAttendanceAPI, name='mess-home'),
    path('api/accounts/schedule/', views.messScheduleAPI, name='mess-schedule'),
    path('api/accounts/schedule/edit/', views.editMessScheduleAPI, name='edit-mess-schedule'),
    path('api/accounts/feedback/', views.sendFeedback, name='send-feedback'),
    path('api/accounts/view-feedback/', views.viewPrevFeedbacks, name='view-prev-feedback'),
    path('dummy/add-data/', views.addData, name='add-data'),

    # common Web app pages
    path('web/signup/', views.web_signup, name='web-signup'),
    path('web/login/', views.web_login, name='web-login'),
    path('web/logout/', views.web_logout, name='web-logout'),
    path('web/home/', views.home, name='web-home'),

    # vendor
    path('vendor/home/', views.vendorDashboard, name='vendor-home'),
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

    # Mess Admin
    path('mess/home/', views.messHome, name='mess-home'), #both admin and vendor
    path('mess/view-attendance/cur-month/', views.getMarkedAttendanceCurMonth, name='mess-attendance-cur'), #both admin and vendor
    path('mess-admin/upload-attendance/', views.uploadAttendance, name='upload-attendance'),
    path('mess-admin/list-defaulters/', views.listDefaulters, name='list-defaulters'),
    path('mess-admin/view-users/', views.viewUsers, name='view-users'),
    url(r'^mess-admin/renew-coupons/(?P<user_id>\d+)/$', views.addData, name='renew-coupons'),
    url(r'^mess-admin/delete-user/(?P<user_id>\d+)/$', views.deleteUser, name='delete-user'),
    url(r'^mess-admin/give-user-admin-rights/(?P<user_id>\d+)/$', views.giveAdminRights, name='admin-rights-give'),
    url(r'^mess-admin/remove-user-admin-rights/(?P<user_id>\d+)/$', views.removeAdminRights, name='admin-rights-remove'),
    path('mess-admin/view-feedback/', views.viewFeedback, name='mess-feedback'),
    url(r'^mess-admin/view-feedback/penalise/(?P<feedbackid>\d+)/$', views.penalise, name='mess-feedback-penalise'),
    url(r'^mess-admin/view-feedback/approve/(?P<feedbackid>\d+)/$', views.approve, name='mess-feedback-approve'),
    url(r'^mess-admin/view-feedback/maybe/(?P<feedbackid>\d+)/$', views.maybe, name='mess-feedback-maybe'),
]
