from django.urls import path
from . import views

urlpatterns = [
    # ───── المصادقة (REQ-1, 2, 12, 18) ─────
    path('login/',           views.login_view,            name='login'),
    path('signup/',          views.signup_view,           name='signup'),
    path('logout/',          views.logout_view,           name='logout'),
    path('password-reset/',  views.password_reset_request, name='password_reset'),

    # ───── الحساب (REQ-3, 4, 5, 28, 60) ─────
    path('profile/',                views.profile_view,       name='profile'),
    path('profile/edit/',           views.edit_profile,       name='edit_profile'),
    path('profile/edit-ext/',       views.edit_user_profile,  name='edit_user_profile'),
    path('profile/delete/',         views.delete_account,     name='delete_account'),
    path('change-password/',        views.change_password,    name='change_password'),

    # ───── العقارات (REQ-6, 7, 8, 9, 10, 29, 35, 59) ─────
    path('',                              views.property_list,    name='home'),
    path('property/<int:pk>/',            views.property_detail,  name='detail'),
    path('property/add/',                 views.add_property,     name='add'),
    path('property/<int:pk>/edit/',       views.edit_property,    name='edit'),
    path('property/<int:pk>/delete/',     views.delete_property,  name='delete_property'),
    path('property/<int:pk>/toggle/',     views.toggle_property,  name='toggle_property'),
    path('property/<int:pk>/draft/',      views.save_as_draft,    name='save_as_draft'),
    path('image/<int:image_id>/delete/',  views.delete_property_image, name='delete_property_image'),

    # ───── البحث (REQ-13, 14, 25, 31-34, 37, 38) ─────
    path('search/',  views.search_view,  name='search'),
    path('newest/',  views.newest_view,  name='newest'),
    path('popular/', views.popular_view, name='popular'),

    # ───── المفضلة (REQ-15, 16, 17) ─────
    path('favorites/',                 views.favorites_list,  name='favorites'),
    path('favorites/add/<int:pk>/',    views.add_favorite,    name='fav_add'),
    path('favorites/remove/<int:pk>/', views.remove_favorite, name='fav_remove'),

    # ───── التقييم والبلاغ (REQ-11, 23, 24) ─────
    path('property/<int:pk>/rate/',   views.rate_property, name='rate'),
    path('property/<int:pk>/report/', views.report_ad,     name='report'),

    # ───── المدن والإحصائيات (REQ-36, 56) ─────
    path('cities/', views.cities_count, name='cities'),
    path('stats/',  views.site_stats,   name='stats'),

    # ───── المالكون والمتابعة (REQ-26, 30, 40, 41, 42) ─────
    path('user/<str:username>/',           views.owner_profile, name='owner_profile'),
    path('user/<str:username>/follow/',    views.toggle_follow, name='toggle_follow'),
    path('my/following/',                  views.my_following,  name='my_following'),
    path('my/followers/',                  views.my_followers,  name='my_followers'),

    # ───── المقارنة (REQ-43) ─────
    path('compare/', views.compare_properties, name='compare'),

    # ───── التعليقات (REQ-44, 45, 46) ─────
    path('property/<int:pk>/comment/',      views.add_comment,    name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

    # ───── البحث المحفوظ (REQ-47) ─────
    path('save-search/',           views.save_search,   name='save_search'),
    path('my-searches/',           views.my_searches,   name='my_searches'),
    path('search/<int:pk>/delete/', views.delete_search, name='delete_search'),

    # ───── التنبيهات (REQ-48, 49, 50, 51) ─────
    path('notifications/',              views.notifications_list,   name='notifications'),
    path('notification/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notification/<int:pk>/delete/', views.delete_notification, name='delete_notification'),

    # ───── السجلات والتصدير (REQ-39, 57, 58) ─────
    path('history/',         views.activity_history,    name='history'),
    path('recently-viewed/', views.recently_viewed,     name='recently_viewed'),
    path('export/',          views.export_my_properties, name='export'),
]
