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

from rest_framework import permissions
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path(r'cargo/', views.cargo_list, name='cargo-list'),
    path(r'cargo/new/', views.add_cargo, name='add-cargo'),
   # path(r'cargo/<int:pk>/put/', views.put_detail, name='cargo-put'),
   

    path(r'cargo/<int:pk>/', views.get_cargo, name='cargo-detail'),
    path(r'cargo/<int:pk>/add/', views.add_cargo_to_order, name='add-cargo-to-order'),
    path(r'cargo/<int:pk>/edit/', views.edit_cargo, name='edit-cargo'),
    path(r'cargo/<int:pk>/delete/', views.delete_cargo, name='delete-cargo'),

    path(r'orders/', views.get_orders, name='orders-list'),

    path(r'order/<int:pk>/', views.get_order_detail, name='order-detail'),
    path(r'order/<int:pk>/update/', views.put_order_detail, name='order-update'),
    path(r'order/<int:pk>/delete/', views.delete_order_detail, name='order-delete'),


    path(r'update_order/<int:pk>/delete/', views.delete_cargo_order, name='delete_cargo_order'),
    path(r'update_order/<int:pk>/put/', views.update_cargo_order_amount, name='update_cargo_order_amount'),


    path(r'update_status/set_user_status/', views.set_user_status, name='set_user_status'),
    path(r'update_status/set_moderator_status/', views.update_moderator_status, name='update_moderator_status'),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),


    path(r'users/login/', views.login_view, name="login"),
    path(r'users/logout/', views.logout_view, name="logout"),
    path(r'users/registration/', views.registration, name='registration'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
 
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




