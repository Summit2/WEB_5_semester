from .models import Cargo
from rest_framework import serializers
#  для преобразования в json и обратно

class CargoSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Cargo
        # Поля, которые мы сериализуем
        fields = ["pk", "title", "image_url", "weight", "description", 'is_deleted']