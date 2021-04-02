from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
import string
import random


class Unit(models.Model):
    name = models.CharField(max_length=255)
    label = models.CharField(max_length=10)

    def __str__(self):
        return self.label

class UnitRate(models.Model):
    unit = models.ForeignKey(Unit, related_name="unit_rate", on_delete=models.CASCADE)
    parent = models.ForeignKey(Unit, related_name="unit_parent", on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=6, decimal_places=3)

class Currency(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    label = models.CharField(max_length=16)
    symbol = models.CharField(max_length=3)

    class Meta:
        verbose_name_plural = 'currencies'
    
    def __str__(self):
        return self.name


class CurrencyRate(models.Model):
    original_currency = models.ForeignKey(Currency, related_name="og_currency", on_delete=models.CASCADE)
    rating_currency = models.ForeignKey(Currency, related_name="rating_currency", on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=15, decimal_places=5)


class Ingredient(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    article_number = models.IntegerField(unique=True, db_index=True)
    price = models.DecimalField(max_digits=5, decimal_places = 2)
    currency = models.ForeignKey(Currency, related_name="ingredient_currency", on_delete=models.DO_NOTHING)
    quantity = models.DecimalField(max_digits=6, decimal_places=3)
    unit = models.ForeignKey(Unit, related_name="ingredient_unit", on_delete=models.DO_NOTHING)
    created_by = models.ForeignKey(User, related_name="ingredient_creator", on_delete=models.DO_NOTHING)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        slug = slugify(self.name)
        if self.pk is None:
            slug = generate_unique_slug(slug, Ingredient)
        self.slug = slug
        super(Ingredient, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('manager:ingredient_update', args=[self.slug])

    def get_normalized(self):
        return self.quantity.normalize()

class Recipe(models.Model):
    DIFFICULTY_DICHOICES = (
        ('Beginner', 'Beginner'),
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
        ('Chef', 'Chef'),
    )
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    image = models.ImageField(upload_to="images/recipes/", default='images/recipes/no_image.jpeg')
    recipe_text = models.TextField(blank=True)
    portions = models.IntegerField(default=1)
    difficulty = models.CharField(max_length=255, default='Medium', choices=DIFFICULTY_DICHOICES)
    created_by = models.ForeignKey(User, related_name="recipe_creator", on_delete=models.DO_NOTHING)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        slug = slugify(self.name)
        if self.pk is None:
            slug = generate_unique_slug(slug, Recipe)
        self.slug = slug
        print(self.recipe_text)
        super(Recipe, self).save(*args, **kwargs)

    def get_recipe_text_html(self):
        return '<br/> '.join(self.recipe_text.split('\n'))

    def get_abolsute_url(self):
        return reverse('manager:recipe_update', args=[self.slug])

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, related_name="recipe_name", on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, related_name="recipe_ingredient", on_delete=models.DO_NOTHING)
    quantity = models.DecimalField(max_digits=6, decimal_places=3)
    unit = models.ForeignKey(Unit, related_name="recipe_ingredient_unit", on_delete=models.DO_NOTHING)

    def get_normalized(self):
        return self.quantity.normalize()

    def get_rate_price(self):
        price = 0
        if self.unit == self.ingredient.unit:
            price = self.ingredient.price * self.quantity / self.ingredient.quantity
        else:
            unit_rate = UnitRate.objects.filter(unit=self.unit)
            if len(unit_rate) > 0:
                price = self.ingredient.price * self.quantity / (self.ingredient.quantity / unit_rate[0].rate)
            else:
                unit_rate = UnitRate.objects.get(unit=self.ingredient.unit, parent=self.unit)
                price = self.ingredient.price * (self.quantity / unit_rate.rate) / self.ingredient.quantity
        return price.normalize()


'''

    Parameters: 
        slug - original generated slug
        model - model type

    Returns:
        new slug

    Giving a model and a slug it will check if the slug already exists in the table.
    If exists will concat an hyphen followed by 5 random letters or digits else returns the original slug.

'''
def generate_unique_slug(slug, model):
    model = model.objects.filter(slug=slug).exists()
    letters = string.ascii_letters + string.digits
    if model:
        #Generate unique slug
        slug = slug + '-' + ''.join(random.choice(letters) for i in range(5))
    return slug