# Generated by Django 5.1.4 on 2024-12-14 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0002_alter_product_description_cart"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="description",
            field=models.TextField(
                blank=True,
                help_text="1024 символа с фото, 4096 без",
                null=True,
                verbose_name="Описание продукта",
            ),
        ),
    ]