import psycopg2
from io import BytesIO
from PIL import Image

# Подключение к базе данных
conn = psycopg2.connect(
    dbname="starship_delivery",
    user="postgres",
    password="1111",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Выберите изображение из базы данных
cur.execute("SELECT image_binary FROM cargo WHERE id_cargo = 23")
image_binary = cur.fetchone()[0]

# Создайте объект изображения из бинарных данных
image = Image.open(BytesIO(image_binary))
image.show()

# Закрыть соединение
cur.close()
conn.close()