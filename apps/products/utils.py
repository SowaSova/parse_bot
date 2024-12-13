import os
import uuid


def product_image_path(instance, filename):
    # Получаем расширение исходного файла
    ext = filename.split(".")[-1]
    # Генерируем уникальный идентификатор для имени файла
    unique_filename = f"{uuid.uuid4()}.{ext}"
    # Возвращаем путь и имя файла, например 'products/unique-uuid.jpg'
    return os.path.join("products", unique_filename)
