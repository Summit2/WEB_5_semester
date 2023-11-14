
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from bmstu_lab_m import views




#for auth
from rest_framework import permissions
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet, basename='user')



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
   
    
    # path(r'cargo/', views.get_list, name='cargo-list'),
    # path(r'cargo/post/', views.post_list, name='cargo-post'),
    # path(r'cargo/<int:pk>/', views.get_detail, name='cargo-detail'),
    # path(r'cargo/<int:pk>/put/', views.put_detail, name='cargo-put'),
    # path(r'cargo/<int:pk>/delete/', views.delete_detail, name='cargo-delete'),


    path('', include(router.urls)),
    path(r'cargo/', views.CargoList.as_view(), name='cargo-list'),
    path(r'cargo/<int:pk>/', views.CargoDetail.as_view(), name='cargo-detail'),
    path(r'cargo/<int:pk>/put/', views.put_detail, name='cargo-put'),
   

    path(r'orders/', views.OrdersList.as_view(), name='orders-list'),
    path(r'order/<int:pk>/', views.OrderDetail.as_view(), name='order-detail'),

    path(r'update_order/<int:pk>/', views.Cargo_Order_methods.as_view(), name='update_order'),
    

    
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('login',  views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
 

    # path('', views.GetAllCargo, name="all_cargo"),
    # path('item/<int:id>/', views.GetCurrentCargo, name='item_url'), # конкретный груз и его описание

    # path('deleteCargo/', views.DeleteCurrentCargo, name = 'del_cur_cargo')
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)






