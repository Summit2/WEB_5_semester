
# django methods
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.urls import reverse

# PostgreSQL
import psycopg2

# ORMs
from bmstu_lab_m.models import Cargo
from bmstu_lab_m.models import CargoOrder
from bmstu_lab_m.models import DeliveryOrders
#from bmstu_lab_m.models import DeliveryOrders
from bmstu_lab_m.models import Users
from django.db.models import Q


# все для Rest Api
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView

# serializers
from bmstu_lab_m.serializers import CargoSerializer
from bmstu_lab_m.serializers import OrdersSerializer
# from bmstu_lab_m.serializers import Cargo_Order_Serializer

from drf_yasg.utils import swagger_auto_schema
from django.utils.text import slugify
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.http import HttpRequest

from django.db.models import Q, F
from drf_yasg import openapi

from django.http import JsonResponse
from rest_framework.decorators import api_view
import hashlib
import secrets

'''Заявки на доставку грузов на Марс на Starship. 
Услуги - товары, доставляемыe на Марс на Starship, 
   заявки - заявки на конкретный объем товаров
'''
import redis

#sudo service redis-server start
def get_instance_redis():
    red =  redis.Redis(
        host='0.0.0.0',
        port=6379,
    )
    return red


def set_key(key, value):
    red = get_instance_redis()
    red.set(key, value, ex=86400)


def get_value(key):
    red = get_instance_redis()
    return red.get(key)


def delete_value(key):
    red = get_instance_redis()
    red.delete(key)

ID_USER = 5
MODERATOR_ID = 6



def check_user(request):
    response = login_view_get(request._request)
    if response.status_code == 200:
        user = Users.objects.get(id_user=response.data.get('id_user').decode())
        return user.is_moderator == False
    return False


def check_moderator(request):
    response = login_view_get(request._request)
    print(response)
    if response.status_code == 200:
        user = Users.objects.get(id_user=response.data.get('id_user'))
        print(user.is_moderator,'check moder')
        return user.is_moderator == True
    
    return False




def check_authorize(request):
    response = login_view_get(request._request)
    if response.status_code == 200:
        user = Users.objects.get(id_user=response.data.get('id_user'))
        print(f'User in check_authorize^ {user}')
        return user
    return None

#ser Domain
@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['first_name', 'last_name', 'email',  'passwd'], #'login',
        properties={
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='Имя пользователя'),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Фамилия пользователя'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Электронная почта пользователя'),
            # 'login': openapi.Schema(type=openapi.TYPE_STRING, description='Логин пользователя'),
            'passwd': openapi.Schema(type=openapi.TYPE_STRING, description='Пароль пользователя'),
            # 'is_moderator' : openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Пользователь является модератором?'),
        }
    ),
    responses={
        201: openapi.Response(description='Пользователь успешно создан'),
        400: openapi.Response(description='Не хватает обязательных полей или пользователь уже существует'),
    },
    operation_description='Регистрация нового пользователя',
)
@api_view(['POST'])
def registration(request, format=None):
    required_fields = ['first_name', 'last_name', 'email',  'passwd',]#''login',is_moderator']
    missing_fields = [field for field in required_fields if field not in request.data]

    if missing_fields:
        return Response({'Ошибка': f'Не хватает обязательных полей: {", ".join(missing_fields)}'}, status=status.HTTP_400_BAD_REQUEST)

    if Users.objects.filter(email=request.data['email']).exists():
        return Response({'Ошибка': 'Пользователь с таким email уже существует'}, status=status.HTTP_400_BAD_REQUEST)

    password_hash = hashlib.sha256(f'{request.data["passwd"]}'.encode()).hexdigest()

    # try:
    Users.objects.create(
        first_name=request.data['first_name'],
        last_name=request.data['last_name'],
        email=request.data['email'],
        # login=request.data['login'],
        passwd=password_hash,
        # is_moderator=request.data['is_moderator'],
    )
    # except:
    #     return Response({'Ошибка': f'Не удалось создать пользователя'}, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Почта пользователя'),
            'passwd': openapi.Schema(type=openapi.TYPE_STRING, description='Пароль пользователя'),
            # 'is_moderator': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Является ли пользователь модератором?'),
            
        },
        required=['email', 'passwd'],
    ),
    responses={
        200: openapi.Response(description='Успешная авторизация', schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'id_user': openapi.Schema(type=openapi.TYPE_INTEGER)})),
        400: openapi.Response(description='Неверные параметры запроса или отсутствуют обязательные поля'),
        401: openapi.Response(description='Неавторизованный доступ'),
    },
    operation_description='Метод для авторизации',
)
@api_view(['POST'])
def login_view(request, format=None):
    existing_session = request.COOKIES.get('session_key')
    if existing_session and get_value(existing_session):
        return Response({'id_user': get_value(existing_session)})

    email_ = request.data.get("email")
    password = request.data.get("passwd")

    if not email_ or not password:
        return Response({'error': 'Необходимы почта и пароль'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = Users.objects.get(email=email_)
    except Users.DoesNotExist:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    password_hash = hashlib.sha256(f'{password}'.encode()).hexdigest()

    if password_hash == user.passwd:
        random_part = secrets.token_hex(8)
        session_hash = hashlib.sha256(f'{user.id_user}:{email_}:{random_part}'.encode()).hexdigest()
        set_key(session_hash, user.id_user)

        response = JsonResponse({'id_user': user.id_user})
        response.set_cookie('session_key', session_hash, max_age=86400)
        return response

    return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def login_view_get(request, format=None):
    existing_session = request.COOKIES.get('session_key')
    if existing_session and get_value(existing_session):
        return Response({'id_user': get_value(existing_session)})
    return Response(status=status.HTTP_401_UNAUTHORIZED)


@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response(description='Успешный выход', schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'message': openapi.Schema(type=openapi.TYPE_STRING)})),
        401: openapi.Response(description='Неавторизованный доступ', schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'error': openapi.Schema(type=openapi.TYPE_STRING)})),
    },
    operation_description='Метод для выхода пользователя из системы',
)
@api_view(['GET'])
def logout_view(request):
    session_key = request.COOKIES.get('session_key')

    if session_key:
        if not get_value(session_key):
            return JsonResponse({'error': 'Вы не авторизованы'}, status=status.HTTP_401_UNAUTHORIZED)
        delete_value(session_key)
        response = JsonResponse({'message': 'Вы успешно вышли из системы'})
        response.delete_cookie('session_key')
        return response
    else:
        return JsonResponse({'error': 'Вы не авторизованы'}, status=status.HTTP_401_UNAUTHORIZED)



class CargoList(APIView):
    model_class = Cargo
    serializer_class = CargoSerializer
    
    def get(self, request, format=None):
        """
        Возвращает список грузов
        также есть фильтр filter
        
        """
        
        user = check_authorize(request)
        
        if not user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        how_to_filter = request.GET.get('filter', None)
        if_search = request.GET.get('search', None)
        
        idUser = user.id_user
        

        data = DeliveryOrders.objects.filter(id_user = idUser, order_status = 'введён')
        
        try:
            id_order_draft = data[0].id_order
        except IndexError:
            id_order_draft = None

        if how_to_filter is not None:

            if how_to_filter == 'weight' or how_to_filter=='title':
                cargos = self.model_class.objects.all().filter(is_deleted = False).order_by(f'{how_to_filter}')

            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        else:
            cargos = self.model_class.objects.all().filter(is_deleted = False)

        if if_search is not None:

            
            cargos = self.model_class.objects.all().filter(is_deleted = False, title__icontains = f'{if_search}')

            

        else:
            cargos = self.model_class.objects.all().filter(is_deleted = False)

        serializer = self.serializer_class(cargos, many=True)

        serializer_data = serializer.data

        # Return a dictionary containing the list of orders and the id_order_draft
        response_data = {
            'data': serializer_data,
            'id_order_draft': id_order_draft
        }

        return Response(response_data)
   

    def post(self, request, format=None):
        # user = check_authorize(request)
        # if not user:
        #     return Response(status=status.HTTP_403_FORBIDDEN)
        """
        Добавляет новый груз
        """
        # user = check_authorize(request)
        # print(user)
        # if not user and user.is_moderator != True:
        #     return Response(status=status.HTTP_403_FORBIDDEN)



        # !!!!!

        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            bi_image_path = request.data.get('image_binary')
            binary_data = self.new_method(bi_image_path)
            serializer.save(image_binary=binary_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def new_method(self, bi_image_path):
        with open(bi_image_path, 'rb') as file:
            binary_data = file.read()
        return binary_data
    


from datetime import datetime

class CargoDetail(APIView):
    model_class = Cargo
    serializer_class = CargoSerializer
    users_class = Users
    
    def get(self, request, pk, format=None):
        """
        Возвращает информацию o грузe
        """
        
        cargo = Cargo.objects.filter(id_cargo = pk , is_deleted = False)[0]#get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(cargo)
        return Response(serializer.data)
    
    def post(self, request, pk, format=None):
        
        user = check_authorize(request)
        print(request)
        if not user:
            print('POST cargo/id/ , user = None')
            return Response(status=status.HTTP_403_FORBIDDEN)
        '''
        Добавление определенного груза в заявку 

        SELECT Delivery_orders.id_order, Cargo.id_cargo , cargo.title
        FROM Delivery_orders
        INNER JOIN Cargo_Order ON Delivery_orders.id_order = Cargo_order.id_order
        INNER JOIN Cargo ON Cargo_order.id_cargo = Cargo.id_cargo;
        
        '''
        
        
        ind_User = user.id_user 
        ind_Moderator = 1

        user_instance = get_object_or_404(Users, pk=ind_User)
        moderator_instance = get_object_or_404(Users, pk=ind_Moderator)
        cargo_instance = get_object_or_404(Cargo, pk=pk)
        
        order = DeliveryOrders.objects.all().filter(id_user=user_instance, id_moderator=moderator_instance, order_status = 'введён')
        
       
        if not order.exists():
            #здесь добавляем заказ, если его до этого не было
            # и присваиваем ему статус 'введён'
            order_to_add = DeliveryOrders.objects.create(id_user = user_instance,
                                                          id_moderator=moderator_instance, 
                                                          order_status = 'введён' ,
                                                          date_create = datetime.now())
            order_to_add.save()
            order = order_to_add


        # for i in order:
        #     print(i)
        # order_instance = get_object_or_404(DeliveryOrders, pk = order[0].id_order)
        try:
            for order_item in order:
                order_instance = get_object_or_404(DeliveryOrders, pk=order_item.id_order)
                break
            # и добавляем в таблицу многие ко многим
        except:
            pass
        try:
            many_to_many = CargoOrder.objects.create(id_cargo=cargo_instance, 
                                                        id_order=order_instance,
                                                        amount = 1) #amount пока 1, потом можно будет поменять
            many_to_many.save()
        except:
            # значит в таблице многие ко многим уже существует запись
            pass
        

        return Response(status=status.HTTP_201_CREATED)
        

    
        

    def put(self, request, pk, format=None):
        """
        Обновляет информацию о грузe(для модератора)
        """

        ind_Moderator = 1 # хардкод
        if Users.objects.all().filter(id_user = ind_Moderator)[0].is_moderator == True:
        

            cargo = get_object_or_404(self.model_class, pk=pk)
            serializer = self.serializer_class(cargo, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
        

    def delete(self, request, pk, format=None):
        """
        Удаляет запись груза логически(через статус)
        """
        del_item = get_object_or_404(self.model_class, pk=pk)
        del_item.is_deleted = True
        del_item.save()
        
        print(del_item)
        return Response(status=status.HTTP_200_OK)
        

@api_view(['Put'])
def put_detail(request, pk, format=None):
    """
    Обновляет информацию о грузe (для пользователя)
    """
    cargo = get_object_or_404(Cargo, pk=pk)
    serializer = CargoSerializer(cargo, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.utils.dateparse import parse_date

class OrdersList(APIView):
    model_class = DeliveryOrders
    serializer_class = OrdersSerializer

   
    
    def get(self, request, format=None):

        user = check_authorize(request)
        if not user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if not check_moderator(request):
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        date_create = request.GET.get('date_create', None)
        date_accept = request.GET.get('date_accept', None)
        date_finish = request.GET.get('date_finished', None)
        order_status = request.GET.get('order_status', None)

        print(user)
        idUser = user.id_user
        
        all_orders = self.model_class.objects.filter(id_user = idUser)

        if order_status is not None:
            
            all_orders = self.model_class.objects.filter(id_user = idUser, order_status = order_status)

        if date_create is not None:
            
            if date_finish is not None:
                all_orders = self.model_class.objects.filter(id_user = idUser, date_create = date_create,date_finish =date_finish)
            else:
                all_orders = self.model_class.objects.filter(id_user = idUser, date_create = '1980-01-01',date_finish =date_finish)
        else:
            all_orders = self.model_class.objects.filter(id_user = idUser)

        

        
        data = []
        for order in all_orders:
            user = Users.objects.get(id_user=order.id_user.id_user)
            moderator = Users.objects.get(id_user=order.id_moderator.id_user)
            data.append({
                "pk": order.pk,
                "id_order": order.id_order,
                "user_email": user.email,
                "id_moderator": moderator.id_user,
                "order_status": order.order_status,
                "date_create": order.date_create,
                "date_accept": order.date_accept,
                "date_finish": order.date_finish
            })
        return Response(data)


    


class OrderDetail(APIView):
    model_class = DeliveryOrders
    serializer_class = OrdersSerializer
    
    def get(self, request, pk, format=None):
        """
        Возвращает информацию об акции
        """
        if not check_moderator(request):
            return Response(status=status.HTTP_403_FORBIDDEN)

        order = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(order)

        responce = serializer.data

        cargo_in_order_ids = CargoOrder.objects.filter(id_order = pk)
        list_of_cargo_ids = [i.id_cargo.id_cargo for i in cargo_in_order_ids]
        print(list_of_cargo_ids)
        cargo_in_order = Cargo.objects.filter(id_cargo__in = list_of_cargo_ids)

        print(cargo_in_order)

        cargo_serializer = CargoSerializer(cargo_in_order, many=True)

        responce['Cargo_in_Order'] = cargo_serializer.data
        return Response(responce)
    
    def put(self, request, pk, format=None):
        """
        Обновляет информацию об акции (для модератора)
        """
        order = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        """
        Меняет статус заказа на удалён
        Может делать только создатель
        """
        order = get_object_or_404(self.model_class, pk=pk)
        order.order_status = "удалён"
        order.save()  # Save the changes to the database
        return Response(status=status.HTTP_204_NO_CONTENT)




class UpdateUserStatus(APIView):
    model_class = DeliveryOrders
    serializer_class = OrdersSerializer
    def put(self, request, format=None):
        if not check_moderator(request):
            return Response(status=status.HTTP_403_FORBIDDEN)
        """
        Обновляет статус для пользователя

{
    "id_user" : 2,
    "id_moderator" :1 

}
        """
        
        try:
            idUser = request.data.get('id_user')
            idModer = request.data.get('id_moderator')
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        self.model_class.objects.filter(id_user = idUser, id_moderator = idModer, order_status = 'введён').update(order_status = 'в работе', date_accept = datetime.now())
        return Response(status=status.HTTP_204_NO_CONTENT)

        




class UpdateModeratorStatus(APIView):
    model_class = DeliveryOrders
    serializer_class = OrdersSerializer

    def put(self, request, format=None):
        """
        Обновляет статус для модератора
        """
        
        try:
            idUser = request.data.get('id_user')
            idModer = request.data.get('id_moderator')
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        order = self.model_class.objects.filter(id_user = idUser, order_status = 'в работе').update(date_finished= datetime.now(),order_status = 'завершён')
        

        return Response(status=status.HTTP_204_NO_CONTENT)




class Cargo_Order_methods(APIView):

    def delete(self, request, pk, format=None):
        '''
        удаление услуги из заявки для конкретного пользователя
        если услуга была последняя, то и заявка тоже удаляется

        запрос для получения всех заказов со всеми грузами в них:
            select * from delivery_orders as dor 
            inner join cargo_order as ca on ca.id_order = dor.id_order;
        '''
        idUser = 2
        idModerator = 1 
        # del_object = get_object_or_404(self.method_class, pk=pk)
        active_order = DeliveryOrders.objects.filter( Q(order_status = 'введён') | Q(order_status = 'в работе'), id_user = idUser)
        
        if active_order.exists():
    
            del_result = CargoOrder.objects.filter(id_order = active_order[0].id_order, id_cargo = pk).delete()
            #del_res - tuple (number_of_deleted, dict of deleted)
            print('deleted:', del_result)
            if del_result[0] == 0:
                return Response(status=status.HTTP_404_NOT_FOUND)


            return Response(status=status.HTTP_204_NO_CONTENT)


        return Response(status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, pk, format=None):
        '''
         изменение количества в м-м
         pk - номер груза, количество которого надо изменить
        '''

        idUser = 2
        idModerator = 1 
        new_amount = request.data['amount']
        active_order = DeliveryOrders.objects.filter( Q(order_status = 'введён') | Q(order_status = 'в работе'), id_user = idUser)
        # print('PUT update_order (updating amount). Current order: ', active_order)
        if active_order.exists():

            CargoOrder.objects.filter(id_order = active_order[0].id_order,
                                       id_cargo = pk,
                                       ).update(amount = new_amount)


            return Response(status=status.HTTP_204_NO_CONTENT)


        return Response(status=status.HTTP_404_NOT_FOUND)
    


    #!!!!!
    