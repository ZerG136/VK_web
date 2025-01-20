"""
URL configuration for askme project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from app import views
from django.conf.urls.static import static

from askme import settings

urlpatterns = [
    path('', views.index, name = 'index'),
    path('hot/', views.hot, name = 'hot'),
    path('login/', views.login, name = 'login'),
    path('signup/', views.signup, name = 'signup'),
    path('ask/', views.ask, name = 'ask'),
    path('tags/<str:tag_name>', views.tag, name = 'tag'),
    path('question/<int:question_id>', views.one_question, name = 'one_question'),
    path('admin/', admin.site.urls),
    path('logout/', views.logout, name='logout'),
    path('profile/edit/', views.settings, name = 'settings'),
    path('rate_question/', views.rate_question, name = 'rate_question'),
    path('rate_answer/', views.rate_answer, name = 'rate_answer'),
    path('mark_answer/', views.mark_answer, name='mark_answer'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_URL)