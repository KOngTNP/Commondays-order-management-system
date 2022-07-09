"""Commondaysshop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib.auth.views import LogoutView, LoginView
from django.urls import include
from django.views.static import serve
from django.conf.urls import url
from django.conf import settings
from login import views as v
from django.conf.urls.static import static
from rest_framework.authtoken import  views
from mysite import views as mysiteViews

urlpatterns = [
    path('admin/', admin.site.urls),
    path("register/", v.register, name="register"),
    path("", mysiteViews.get_table, name="get_table"),
    path('', include("django.contrib.auth.urls")),
    path('', include('social_django.urls', namespace='social')),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name="login"),
    path('logout/',LogoutView.as_view(template_name=settings.LOGOUT_REDIRECT_URL),name='logout'),
    path('', include('mysite.urls', namespace='mysite')),
    url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = 'mysite.views.custom_page_not_found_view'
handler500 = 'mysite.views.custom_error_view'
handler403 = 'mysite.views.custom_permission_denied_view'
handler400 = 'mysite.views.custom_bad_request_view'