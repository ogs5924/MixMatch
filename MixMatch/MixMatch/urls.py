"""MixMatch URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from mainapp import views as main_v
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', main_v.home, name='home'),
    path('admin/', admin.site.urls),

    # Authentication urls
    path('accounts/login/', LoginView.as_view(template_name='mainapp/login.html'), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('accounts/register/', main_v.register, name='register'),
    path('accounts/profile/', main_v.user_profile),

    # Profile urls
    path('all-users', main_v.see_all, name='see-all'),
    path('profile/', main_v.user_profile, name='user-profile'),
    path('profile/see-friends', main_v.see_all_friends, name='see-friends'),

    path('hobby/<int:id>', main_v.see_users_with_hobby, name='users-hobbies'),

    # AJAX urls
    path('profile/ajax/update_details', main_v.ajax_update_details, name='ajax_update_details'),
    path('profile/ajax/send_friend_request', main_v.ajax_send_friend_request, name='send_friend_request'),
    path('profile/ajax/respond_to_request', main_v.ajax_answer_friend_request, name='respond_to_req'),
    path('profile/ajax/filter_users', main_v.ajax_filter_users, name='filter_users'),
    path('profile/ajax/add_hobby', main_v.ajax_add_hobby, name='add_hobby'),
    path('profile/ajax/remove_hobby', main_v.ajax_remove_hobby, name='remove_hobby'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
