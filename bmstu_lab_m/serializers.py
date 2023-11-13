from .models import Cargo
from .models import DeliveryOrders
from .models import CargoOrder
from rest_framework import serializers
#  для преобразования в json и обратно

class CargoSerializer(serializers.ModelSerializer):
    class Meta:
        
        # Модель, которую мы сериализуем
        model = Cargo
        # Поля, которые мы сериализуем
        fields = ["pk", "title", "image_url", "weight", "description", 'is_deleted','image_binary'] # 
   
class OrdersSerializer(serializers.ModelSerializer):
    class Meta:
        email = serializers.CharField(source='Users.email', read_only=True)
        # Модель, которую мы сериализуем
        model = DeliveryOrders
        # Поля, которые мы сериализуем
        fields = ["pk", "id_order", "id_user", "id_moderator", "order_status", 
                  'date_create','date_accept', 'date_finish']
        

class Cargo_Order_Serializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = CargoOrder
        # Поля, которые мы сериализуем
        fields = [] # 



#auth
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    is_moderator = serializers.BooleanField(default=False, required=False)
   
    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'is_moderator']