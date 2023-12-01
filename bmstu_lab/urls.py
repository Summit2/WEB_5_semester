"""
URL configuration for bmstu_lab project.

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
from django.urls import include, path
from rest_framework import routers

from bmstu_lab_m import views

router = routers.DefaultRouter()

''' 
на сайте мы создаем свои уникальные идентификаsторы - urls
'''
urlpatterns = [
    path('admin/', admin.site.urls),

    # path('', include(router.urls)),
    # path(r'cargo/', views.get_list, name='cargo-list'),
    # path(r'cargo/post/', views.post_list, name='cargo-post'),
    # path(r'cargo/<int:pk>/', views.get_detail, name='cargo-detail'),
    # path(r'cargo/<int:pk>/put/', views.put_detail, name='cargo-put'),
    # path(r'cargo/<int:pk>/delete/', views.delete_detail, name='cargo-delete'),
    path(r'cargo/', views.CargoList.as_view(), name='cargo-list'),
    path(r'cargo/<int:pk>/', views.CargoDetail.as_view(), name='cargo-detail'),
    path(r'cargo/<int:pk>/put/', views.put_detail, name='cargo-put'),
   

    path(r'orders/', views.OrdersList.as_view(), name='orders-list'),
    path(r'order/<int:pk>/', views.OrderDetail.as_view(), name='order-detail'),

    path(r'update_order/<int:pk>/', views.Cargo_Order_methods.as_view(), name='update_order'),

    path(r'update/form/', views.UpdateUserStatus.as_view(), name='update_status_user'),
    path(r'update/unform/', views.UpdateModeratorStatus.as_view(), name='order-update_status_moderator'),


    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),


    path('', views.GetAllCargo, name="all_cargo"),
    path('item/<int:id>/', views.GetCurrentCargo, name='item_url'), # конкретный груз и его описание

    path('deleteCargo/', views.DeleteCurrentCargo, name = 'del_cur_cargo')
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
