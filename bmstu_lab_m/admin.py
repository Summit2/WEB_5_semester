from django.contrib import admin

from .models import Cargo
from .models import Users
from .models import DeliveryOrders
from .models import CargoOrder

admin.site.register(Cargo)
admin.site.register(Users)
admin.site.register(DeliveryOrders)
admin.site.register(CargoOrder)