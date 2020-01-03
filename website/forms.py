from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from .models import SiteContent,PublishedDate, Budget, BudgetDate, Country
from django.db import models
from django.core.exceptions import ValidationError
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from django.contrib.auth import get_user_model
User = get_user_model()

class UserForm(forms.Form):
    first_name = forms.CharField(max_length=20, label="Name")
    last_name = forms.CharField(max_length=20, label="Surname")
    #username = forms.CharField(label="Username", min_length=4, max_length=10)
    email = forms.EmailField(label="Email")
    password1 = forms.CharField(label="Password", widget= forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget= forms.PasswordInput)


    """ def clean_username(self):
        username = self.cleaned_data["username"]
        r = User.objects.filter(username=username)

        if r.count():
            raise ValidationError("Username already exist")
        return username"""
      
    def clean_password(self):
        password1 = self.cleaned_data["password1"]
        password2 = self.cleaned_data["password2"]

        if password1 and password2 and password1 != password2:
            raise ValidationError("Password Doesn't Match")
        return password2
    
    def clean_email(self):
        email = self.cleaned_data["email"]
        r = User.objects.filter(email=email)

        if r.count():
            raise ValidationError("Email Being Used By A Different User")
        return email
    def save(self, commit=True):
        user = User.objects.create_user(
            first_name = self.cleaned_data["first_name"],
            last_name = self.cleaned_data["last_name"],
            email = self.cleaned_data["email"],
            password = self.cleaned_data["password2"]
        )
        return user

class ExpenseForm(forms.Form):
    expense_category = forms.CharField(max_length=100, widget= forms.TextInput(
        attrs= {"class": "form-control",
        "placeholder": "Category E.g Clothes, Food, Transport"}
    ))

    spent = forms.DecimalField(max_digits=7, decimal_places=2)

    expense_date = forms.DateField(
        widget= forms.widgets.DateInput(attrs=
        {"type": "date"})
    )
    content_bought = forms.CharField(max_length=100, widget= forms.Textarea(
        attrs= {"class": "form-control",
        "placeholder": "Content Bought E.g Shoe, Rice"}
    ))

class DatePublished(forms.Form):
    expense_date = forms.DateField(widget= forms.widgets.DateInput(attrs=
    {"type": "date"}))

class BudgetForm(forms.Form): 
    category = forms.CharField(max_length=100, widget= forms.widgets.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Budget Category, E.g Food, Transport, Clothes"
    })) 
    amount = forms.DecimalField(max_digits=7, decimal_places=2)
    
    budget_date = forms.DateField(widget= forms.widgets.DateInput(attrs=
    {
        "type": "date"
    })) 

class BudgetDateForm(forms.Form):
    date_budget = forms.DateField(widget= forms.widgets.DateInput(attrs=
    {
        "type": "date"
    })) 

class SavingsForms(forms.Form):
    savings = forms.DecimalField(max_digits=9, decimal_places=2)

class IncomeForm(forms.Form):
    income = forms.DecimalField(max_digits=9, decimal_places=2)

class CountryForm(forms.Form):
    COUNTRY_CURRENCIES = [
        ("₽","₽"),
        ("$", "$"),
        ("€", "€"),
        ("#", "#"),
        ("£", "£"),
    ]
    country = CountryField(blank_label='(Select country)').formfield()
    currency = forms.ChoiceField(widget= forms.Select, choices=COUNTRY_CURRENCIES)
