from django.forms import ModelForm
from django import forms
from .models import Ingredient, Recipe, Unit, Currency

class IngredientForm(ModelForm):

    input_attrs = {
        'article_number':{},
        'price': {
            'min': 0,
            'max': 999.999
        },
        'quantity': {
            'min': 0,
            'max': 999.999
        }
    }

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.input_attrs['article_number']['value'] = self.get_last_article_number()
        self.remove_empty_labels()
        for field_name in self.input_attrs:
            for attr in self.input_attrs[field_name].keys():
                self.fields[field_name].widget.attrs[attr] = self.input_attrs[field_name][attr]

    def remove_empty_labels(self):
        self.fields['currency'].empty_label = None
        self.fields['unit'].empty_label = None

    def get_last_article_number(self):
        return Ingredient.objects.all().order_by('-article_number')[0].article_number + 1

    class Meta:
        model = Ingredient
        fields = ['name', 'article_number', 'price', 'currency', 'quantity', 'unit']
        labels = {
            'name': 'Ingredient', 
        }


class RecipeForm(ModelForm):
    input_attrs = {
        'recipe_text': {
            'class': 'materialize-textarea'
        }
    }

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        for field_name in self.input_attrs:
            for attr in self.input_attrs[field_name].keys():
                self.fields[field_name].widget.attrs[attr] = self.input_attrs[field_name][attr]

    class Meta:
        model = Recipe
        fields = ['name', 'image', 'recipe_text', 'portions', 'difficulty']
        labels = {
            'name': 'Recipe Name',
            'recipe_text': 'Recipe'
        }