
from django.http import HttpResponse
from django.shortcuts import render

from datetime import date 

'''Заявки на доставку грузов на Марс на Starship. 
Услуги - товары, доставляемыe на Марс на Starship, 
   заявки - заявки на конкретный объем товаров
'''
# def hello(request):
#     
#     return render(request, 'index.html', {
#         'data' :    {'current_date': date.today(),
#                      'list' : [1,2,3]
#                      }

        
#     })


    # кроме html видимо можно передавать еще и типа json (или словарей)



def GetAllCargo(request):
    return render(
        request,'all_cargo.html', {'data' : {
        'current_date': date.today(),
        'items': [
            {'title': 'Книга с картинками', 'id': 1},
            {'title': 'Бутылка с водой', 'id': 2},
            {'title': 'Коврик для мышки', 'id': 3},
        ]
    }}
    )

def GetCurrentCargo(request, id):
    return render(request, 'current_cargo.html', {'data' : {
        'current_date': date.today(),
        'id': id
    }})