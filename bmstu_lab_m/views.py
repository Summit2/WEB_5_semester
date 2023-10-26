
# django methods
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.db.models import Q


# PostgreSQL
import psycopg2

# ORMs
from bmstu_lab_m.models import Cargo
from bmstu_lab_m.models import CargoOrder
from bmstu_lab_m.models import DeliveryOrders
#from bmstu_lab_m.models import DeliveryOrders
from bmstu_lab_m.models import Users

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

import datetime
'''Заявки на доставку грузов на Марс на Starship. 
Услуги - товары, доставляемыe на Марс на Starship, 
   заявки - заявки на конкретный объем товаров
'''

conn = psycopg2.connect(
    dbname="starship_delivery",
    user="postgres",
    password="1111",
    host="localhost",
    port="5432"
)


def GetAllCargo(request):
    
    res=[]
    input_text = request.GET.get("good_item")
    data = Cargo.objects.filter(is_deleted=False)
    
    if input_text is not None:
        # for elem in data:
        
        #     if input_text in elem.title:
        #         res.append(elem)
        #         #print(elem)

        return render(
        request,'all_cargo.html', {'data' : {
            'items' : Cargo.objects.filter(is_deleted=False, title__contains=input_text),
            'input' : input_text
        } }
                     )
    
    return render(
            request,'all_cargo.html', {
                'data' :
                {
                    'items' : data
                }
            }
            
        )

def GetCurrentCargo(request, id):
    data = Cargo.objects.filter(id_cargo=id)
    
    return render(request, 'current_cargo.html', 
        {'data' : {
        'item' : data[0]
    }}
    )

@csrf_exempt
def DeleteCurrentCargo(request):
        if request.method == 'POST':
            
            id_del = request.POST.get('id_del') #работает,надо только бд прикрутить в all_cargo


            conn = psycopg2.connect(dbname="starship_delivery", host="127.0.0.1", user="postgres", password="1111", port="5432")
            cursor = conn.cursor()
            cursor.execute(f"update cargo set is_deleted = true where id_cargo = {id_del}")
            conn.commit()   # реальное выполнение команд sql1
            cursor.close()
            conn.close()

        redirect_url = reverse('all_cargo') 
        return HttpResponseRedirect(redirect_url)
    



class CargoList(APIView):
    model_class = Cargo
    serializer_class = CargoSerializer
    
    def get(self, request, format=None):
        """
        Возвращает список грузов
        добавляет ид черновика заявки текущего пользователя
        """

        idUser = 2

        
        data = DeliveryOrders.objects.filter(id_user = idUser, order_status = 'введён')
        
        try:
            id_order_draft = data[0].id
        except IndexError:
            id_order_draft = None

        data ={'id_order_draft' : id_order_draft}

    
        cargos = self.model_class.objects.all().order_by('weight')
        serializer = self.serializer_class(cargos, many=True)

        serializer_data = serializer.data

        # Append additional data to the serialized data
        serializer_data.append(data)

        return Response(serializer_data)
    
    def post(self, request, format=None):
        """
        Создает новый груз
        """
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

class CargoDetail(APIView):
    model_class = Cargo
    serializer_class = CargoSerializer
    users_class = Users
    
    def get(self, request, pk, format=None):
        """
        Возвращает информацию о грузe
        """
        cargo = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(cargo)
        return Response(serializer.data)
    
    def post(self, request, pk, format=None):
        '''
        Добавление определенного груза в заявку 
        и формирование заявки, если до этого ее не было

        SELECT Delivery_orders.id_order, Cargo.id_cargo , cargo.title
        FROM Delivery_orders
        INNER JOIN Cargo_Order ON Delivery_orders.id_order = Cargo_order.id_order
        INNER JOIN Cargo ON Cargo_order.id_cargo = Cargo.id_cargo;
        
        '''
        ind_User = 2 #хардкод, потом надо будет убрать
        ind_Moderator = 1

        user_instance = get_object_or_404(Users, pk=ind_User)
        moderator_instance = get_object_or_404(Users, pk=ind_Moderator)

        #добавить можно только те заявки, у которых статус - "не удален"
        cargo_instance = get_object_or_404(Cargo.objects.filter(is_deleted = False), pk=pk) 

        #здесь можно добавить еще проверку на order_status
        #т.е. добавлять новый заказ, если статус старого завершен, отменен, удален
        order = DeliveryOrders.objects.filter(
        Q(order_status='введён') | Q(order_status='в работе'),
        id_user=user_instance,
        id_moderator=moderator_instance
        )

        if not order.exists():
            #здесь добавляем заказ, если его до этого не было
            # и присваиваем ему статус 'введён'
            order_to_add = DeliveryOrders.objects.create(id_user = user_instance,
                                                          id_moderator=moderator_instance, 
                                                          order_status = 'введён',
                                                            date_create = datetime.datetime.now() )
            order_to_add.save()
            order = order_to_add

        # и добавляем в таблицу многие ко многим
        try: #!!!
            print('1 случай:', order)
            order_instance = get_object_or_404(DeliveryOrders, pk = order.id_order)
        except:
            print('2 случай:', order)
            order_instance = get_object_or_404(DeliveryOrders, pk = order[0].id_order)
        
        
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
        return Response(status=status.HTTP_204_NO_CONTENT)
        

@api_view(['Put'])
def put_detail(request, pk, format=None):
    """
    Обновляет картинку в услуге

    например на default path:
    {
    "new_image_path" : ""
    }
    """
    # cargo = get_object_or_404(Cargo, pk=pk)
    # serializer = CargoSerializer(cargo, data=request.data, partial=True)
    # if serializer.is_valid():
    #     serializer.save()
    #     return Response(serializer.data)
    # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    cargo_to_update = get_object_or_404(Cargo, pk=pk)
    
    def new_method(bi_image_path):
        with open(bi_image_path, 'rb') as file:
            binary_data = file.read()
        return binary_data
    # serializer = CargoSerializer(cargo_to_update,data=request.data)
        
    
    bi_image_path = request.data.get('new_image_path')
    binary_data = new_method(bi_image_path)
    print(bi_image_path )
    cargo_to_update.image_binary=binary_data
    cargo_to_update.save()
    return Response(status=status.HTTP_204_NO_CONTENT)
    # return Response(status=status.HTTP_400_BAD_REQUEST)





class OrdersList(APIView):
    model_class = DeliveryOrders
    serializer_class = OrdersSerializer

    def get(self, request, format=None):
        idUser = 2
        all_orders = self.model_class.objects.all().order_by('order_status', 'date_create')
        serializer = self.serializer_class(all_orders, many=True)
        
        
        serialized_data = serializer.data  # this is a list of dictionaries
        
        
        return Response(serialized_data)


    # def get(self, request, format=None):
    #     """
    #     Возвращает список заказов
    #     """

    #     idUser = 2

    #     all_orders = self.model_class.objects.all().order_by('order_status', 'date_create')


    #     #также надо добавить id черновика для этого пользователя
    #     serializer = self.serializer_class(all_orders, many=True)

    #     # data = {
    #     #     'id_order_draft': self.model_class.objects.filter(id_user=idUser, order_status='введён')
    #     # }
    #     # print(type(serializer))
    #     data = self.model_class.objects.filter(id_user =idUser, order_status = 'введён')
    #     # print('data {}'.format(data))
    #     # for i in data:
    #     #     print(i)
    #     try:
    #         serializer['id_order_draft'] = data[0]
    #     except:
    #         # data = {'id_order_draft' : None}
    #         serializer['id_order_draft'] = '-1'
    #     return Response(serializer.data)
    


class OrderDetail(APIView):
    '''
    Обработка конкретных заявок
    '''
    model_class = DeliveryOrders
    serializer_class = OrdersSerializer
    
    def get(self, request, pk, format=None):
        """
        Возвращает информацию о заявке (заказе)
        """
        order = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(order)

        responce = serializer.data  #берем данные нашей заявки


        # здесь через таблицу М-М берем те грузы, которые есть в нашей заявке
        cargo_in_order_ids = CargoOrder.objects.filter(id_order = pk)
        list_of_cargo_ids = [i.id_cargo.id_cargo for i in cargo_in_order_ids]
        cargo_in_order = Cargo.objects.filter(id_cargo__in = list_of_cargo_ids)


        cargo_serializer = CargoSerializer(cargo_in_order, many=True)

        # добавляем новое поле - это и будут наши товары в заявке
        responce['cargo_in_order'] = cargo_serializer.data
        return Response(responce)
    
    def put(self, request, pk, format=None):
        """
        Обновляет информацию об заказе (для модератора)
        модератор может назначить статусы - отменён / завершен
        
        Статус отменён - если заявка была в статусе - введён
        Статус завершен - если заявка была в статусе - в работе
        """
        idModerator = 1


        moderators = Users.objects.all().filter(id_user = idModerator, is_moderator = True)
        # print(moderators)
        if (not moderators.exists()) :
             return Response(status=status.HTTP_403_FORBIDDEN)

        order = get_object_or_404(self.model_class, pk=pk)
        if order.order_status == 'введён':
            order.order_status = 'отменён'
            order.date_accept = datetime.datetime.now()
            order.date_finish = datetime.datetime.now()
            order.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        elif order.order_status == 'в работе':
            order.order_status = 'завершен'
            order.date_accept = datetime.datetime.now()
            order.date_finish = datetime.datetime.now()
            order.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        # serializer = self.serializer_class(order, data=request.data, partial=True)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data)

        
        return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk, format=None):
        """
        Меняет статус заказа на удалён
        Может делать только создатель
        """
        order = get_object_or_404(self.model_class, pk=pk)
        order.order_status = "удалён"
        order.save()
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