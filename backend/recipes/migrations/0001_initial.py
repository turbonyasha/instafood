# Generated by Django 3.2.3 on 2024-11-24 20:23

import core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteRecipes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'рецепт в избранном',
                'verbose_name_plural': 'Рецепты в избранном',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='Название')),
                ('measurement_unit', models.CharField(max_length=64, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'ингридиент',
                'verbose_name_plural': 'Ингридиенты',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Название')),
                ('image', models.ImageField(default='media/', upload_to='static/recipe/', verbose_name='Картинка')),
                ('text', models.TextField(verbose_name='Текст')),
                ('cooking_time', models.PositiveIntegerField(default=1, validators=[core.validators.validate_cooking_time], verbose_name='Время приготовления (в минутах)')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('short_link', models.CharField(blank=True, max_length=150, null=True, unique=True, verbose_name='Короткая ссылка')),
                ('is_favorited', models.BooleanField(default=False)),
                ('is_in_shopping_cart', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ('-pub_date',),
            },
        ),
        migrations.CreateModel(
            name='RecipeIngredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(validators=[core.validators.validate_amount], verbose_name='Количество')),
            ],
            options={
                'verbose_name': 'ингридиент в рецепте',
                'verbose_name_plural': 'Ингридиенты в рецепте',
                'default_related_name': 'recipe_ingredients',
            },
        ),
        migrations.CreateModel(
            name='RecipeTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'тег рецепта',
                'verbose_name_plural': 'Теги рецептов',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='Название')),
                ('slug', models.SlugField(unique=True, verbose_name='Идентификатор метки')),
            ],
            options={
                'verbose_name': 'метка',
                'verbose_name_plural': 'Метки',
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shoppingcart', to='recipes.recipe', verbose_name='Рецепт')),
            ],
            options={
                'verbose_name': 'рецепт в корзине',
                'verbose_name_plural': 'Рецепты в корзине',
                'abstract': False,
            },
        ),
    ]
