
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
            {'title': 'Канистра с водой', 'id': 1, "text":
             """Борщ - это не только вкусное блюдо, но и отличный источник питательных веществ 
             для наших космонавтов. Внутри каждой кастрюли борща скрывается богатое сочетание
               овощей, мяса и специй, которое придает энергию и позволяет нашим астронавтам
                 чувствовать себя на высоте в космических условиях. Важно, чтобы борщ был готов 
             с заботой и предельно гигиенично, чтобы он сохранял свои качества и на борту МКС. """,
             'image_name' : 'water.jpg'},
            {'title': 'Хлеб', 'id': 2, 'image_name' : 'bread_for_astronauts.jpg' },
            {'title': 'Молоток', 'id': 3, 'image_name' : 'space_hammer.jpg'},
            {'title': 'Гаечный ключ', 'id': 4, 'image_name' : 'wrench.jpg'},
            {'title': 'Борщ', 'id': 5, 'image_name' : 'borsh.jpg'},
            {'title': 'Кофе', 'id': 6, 'image_name' : 'coffee.jpg'},
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
    