
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
        request,'all_cargo.html', 
        {'data' : # в data вложены items имеет смысл исправить
        {
        'items': [
            {'title': 'Канистра с водой', 'id': 1, 'image_name' : ''},
            {'title': 'Хлеб', 'id': 2, 'image_name' : '/home/ilya/Рабочий стол/BMSTU/5 semester/WEB/bmstu_lab/bmstu_lab/static/images/bread_for_astronauts.jpg' },
            {'title': 'Молоток', 'id': 3, 'image_name' : 'bmstu_lab/bmstu_lab/static/images/space_hammer.jpg'},
        ]
    }}
    )

def GetCurrentCargo(request, id):
    return render(request, 'current_cargo.html', 
        {'data' : {
        'id': id
    }})


def sendText(request):
    input_text = request.POST['text']
    