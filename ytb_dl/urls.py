"""
URL configuration for ytb_dl project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import path
from django.views import View

from downloader.views import download_video
from profiles.views import signup, verify_email, home
from django.contrib.auth.views import LoginView, LogoutView


class EmptyView(View):
    def get(self, request):
        return HttpResponse()


urlpatterns = [
    path('signup/', signup, name='signup'),
    path('verify-email/<str:uidb64>/<str:token>/', verify_email, name='verify_email'),
    path('download/', download_video, name='download_video'),
    path('admin/', admin.site.urls),
    path('', login_required(home), name='home'),
    path('login/', LoginView.as_view(template_name='profiles/login.html',
                                     redirect_authenticated_user=True), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('favicon.ico', EmptyView.as_view(), name='favicon'),
]
