# Generated by Django 3.1.7 on 2021-04-02 02:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='recipe_text',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(default='images/recipes/no_image.jpeg', upload_to='images/recipes/'),
        ),
        migrations.DeleteModel(
            name='RecipeStep',
        ),
    ]
