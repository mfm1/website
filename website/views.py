from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from website.models import SiteContent, PublishedDate, Budget, BudgetDate, Savings, Income, Country, UserProfile
from website.forms import UserForm, ExpenseForm, DatePublished, BudgetForm, BudgetDateForm,SavingsForms, IncomeForm, CountryForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404, reverse, Http404
from django.conf import settings
from datetime import datetime, date, timedelta
from website import helpers
from django.core.mail import send_mail
import calendar
import csv
import pandas
import os
from django.db.models import Sum
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models.functions import ExtractWeek, ExtractDay, ExtractMonth
from django.contrib.auth import get_user_model
User = get_user_model()
#from django.contrib.auth.models import User

# Create your views here.
def homepage(request):
    user = request.user
    site = ""
    try:
        s = SiteContent.objects.filter(user = user).order_by("expense_date")
        site = s
    except:
        pass

    return render(
        request = request,
        template_name = "website/home.html",
        context= {
            "site": site
            }
    )
def register(request):
    if request.method == "POST":  
        form = UserForm(request.POST)

        if form.is_valid():
            user = form.save()
            messages.success(request, "Your Account Was Created Successfully")
            login(request, user)
            return redirect("website:homepage")

        else:
            form = UserForm()
    form = UserForm
    return render(
        request = request,
        template_name = "website/register.html",
        context = {"form": form}
    )

def activate_account(request):
    key = request.GET['key']
    if not key:
        raise Http404()
 
    r = get_object_or_404(Author, activation_key=key, email_validated=False)
    r.user.is_active = True
    r.user.save()
    r.email_validated = True
    r.save()
 
    return render(
        request, 
        'website/activated.html'
        )

def logout_request(request):
    """User Logout page"""
    try:
        del request.session["username"]
    except:
        pass
    messages.info(request, "You're now logged out...")
    logout(request)
    return redirect("website:homepage")

def login_request(request):
    """Login page"""
    if request.method == "POST":
        form = AuthenticationForm(request= request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, email = email, password = password)

            if user is not None:
                login(request, user)
                full_name = request.user.get_full_name()
                messages.info(request, "You're now logged in as {}. ".format(full_name))
                return redirect("website:homepage")

            else:
                messages.error(request, "Invalid username or password")
                return render(
                    request = request,
                    template_name = "website/login.html",
                    context= {"form": form}
                )
        else:
            messages.error(request, "Inavlid username or password.")

    form = AuthenticationForm
    return render(
        request = request,
        template_name = "website/login.html",
        context= {"form": form}
    )

@login_required
def create_expense(request):
    user = request.user
    if request.method == "POST":
        form = ExpenseForm(request.POST)

        if form.is_valid():
            users = SiteContent(
                expense_category =  form.cleaned_data["expense_category"],
                spent = form.cleaned_data["spent"],
                expense_date = form.cleaned_data["expense_date"],
                content_bought = form.cleaned_data["content_bought"],
                user = user
            )
            #users = form.save(commit=False)
            users.save()
            messages.success(request, "Your Expense was created successfully.")
            return redirect("website:create-expense")
        else:
            messages.error(request, "Fill all fields")
    form = ExpenseForm
    return render(
        request = request,
        template_name = "website/expense.html",
        context= {"form": form}
    )

@login_required
def check_expense(request):
    total_spent_today = []
    total_spent_w = [] #Total spent this week
    expense_record = ""
    monthly_expense = []
    t_d = date.today() # Todays date
    c = calendar.Calendar() # Calender of the current year
    year = t_d.year
    month = t_d.month
    last = ""
    country = ""
    weeks_in_the_month = ""
    """
        Determine in which week of the month, today fall into,
        then assign weeks_in_the_month according to week today's date
        fall into.
        This will be used to get user weekly record
    """
    if t_d in c.monthdatescalendar(year, month)[0]:
        weeks_in_the_month = c.monthdatescalendar(year, month)[0]

    elif t_d in c.monthdatescalendar(year, month)[1]:
        weeks_in_the_month = c.monthdatescalendar(year, month)[1]
    
    elif t_d in c.monthdatescalendar(year, month)[2]:
        weeks_in_the_month = c.monthdatescalendar(year, month)[2]

    elif t_d in c.monthdatescalendar(year, month)[3]:
        weeks_in_the_month = c.monthdatescalendar(year, month)[3]
    
    elif t_d in c.monthdatescalendar(year, month)[4]:
        weeks_in_the_month = c.monthdatescalendar(year, month)[4]
    
    #one_week = date.today()- timedelta(days=7)

    user = request.user
    if request.method == "POST":
        form = DatePublished(request.POST)
        if form.is_valid():
            dates = PublishedDate(
                date_expense = form.cleaned_data["expense_date"],
                user = user
            )
            dates.save() 
            return redirect("website:check-expense")
        else:
            pass

    datas = SiteContent.objects.filter(user=user).order_by("-id")

    try:
        """
        This is to get users weekly record based on the number of weeks
        in the particular, 
        """
        for data in datas:
            if data.expense_date.month == month:
                monthly_expense.append(data.spent)
            if data.expense_date == date.today():
                # for total amount the user spent today
                total_spent_today.append(data.spent)
            for i in weeks_in_the_month:
                # for total amount the user spent this week
                if data.expense_date == i:
                    total_spent_w.append(data.spent)
        
        
        # Get the last Date that was imputed into PublishedDate
        # So that you can get the user expense record for that date
        l = PublishedDate.objects.filter(user = user).order_by("-id")[0]
        last = l
    
        c = Country.objects.filter(user=user).order_by("-id")[0]
        country = c

        #User expense record for a particular date
        # last is the date the user entered to check the day expense record
        expense_rec = SiteContent.objects.filter(user = user, expense_date = last.date_expense)
        expense_record = expense_rec
    except:
        pass

    # Form Field for users to check past expense record
    form = DatePublished
    return render(
        request,
        "website/check_exp.html", 
        {
            "today": t_d, 
            "datas": datas, 
            "form": form,
            "expense_record": expense_record, 
            "last": last,
            "country": country,
            "monthly_expense": sum(monthly_expense),
            "total_spent_today": sum(total_spent_today),
            "total_spent_w": sum(total_spent_w)
    })

@login_required
def create_budget(request):
    user = request.user

    if request.method == "POST":
        form = BudgetForm(request.POST)
        if form.is_valid():
            data = Budget(
                user= user,
                category = form.cleaned_data["category"],
                amount = form.cleaned_data["amount"],
                budget_date = form.cleaned_data["budget_date"]
            )
            data.save()
            messages.success(request, "Your budget was created successfully.")
            return redirect("website:create-budget")
        else:
            pass
    
    form = BudgetForm
    return render(
        request,
        "website/budget.html",
        {
            "form": form
        }
    )

def check_budget(request):
    user = request.user
    budget_record = ""
    today = date.today()
    last = ""
    country = ""
    t = datetime.now() # t for time
    d = t.strftime("%b.%d,%Y ")  # t_d for Today's date
    t_d = date.today() - timedelta(days=7)

    if request.method == "POST":
        form = BudgetDateForm(request.POST)
        if form.is_valid():
            data = BudgetDate(
                date_budget = form.cleaned_data["date_budget"],
                user = user
            )
            data.save()
            return redirect("website:check-budget")
        else:
            pass

    budgets = Budget.objects.filter(user = user).order_by("budget_date")



    try:
        l = BudgetDate.objects.filter(user=user).order_by("-id")[0]
        last = l
        budget_rec = Budget.objects.filter(user=user, budget_date = last.date_budget)
        budget_record = budget_rec
        c = Country.objects.filter(user=user).order_by("-id")[0]
        country = c
    except:
        pass
      
    form = BudgetDateForm()  

    return render(
        request,
        "website/check_budget.html",
        {
            "today": today,
            "budgets": budgets,
            "last": last,
            "country": country,
            "form": form,
            "budget_records": budget_record
        }
    )

def user_page(request):
    total_saving = []
    total_income = []
    monthly_savings = []
    monthly_incomes = []
    country = ""
    user = request.user # Request for current logged in user
    year = date.today().year
    months = date.today().month
    c = calendar.Calendar()
    days_in_the_month = c.itermonthdates(year, months)

    # Savings input form field.
    if request.method == "POST":
        form = SavingsForms(request.POST)
        if form.is_valid():
            data = Savings(
                savings = form.cleaned_data["savings"],
                user = user
            )
            data.save()
            messages.success(request, "Savings Added")
            return redirect("website:profile")
        else:
            pass
    #income input form view
    if request.method == "POST":
        form = IncomeForm(request.POST)
        if form.is_valid():
            data = Income(
                income = form.cleaned_data["income"],
                user = user
            )
            data.save()
            messages.success(request, "Income Added")
            return redirect("website:profile")
        else:
            pass
    #savings form
    form = SavingsForms()
    #income form
    income_form = IncomeForm()
    
    # To determine total savings for the month
    td = date.today()
    d = Savings.objects.filter(user = user).order_by("-id").annotate(month = ExtractMonth("pub_date")).values("month", "savings")
    
    datas = Savings.objects.filter(user=user)
    for data in datas:
        total_saving.append(data.savings)
        if data.pub_date.month == months:
            monthly_savings.append(data.savings)

    # To determine total income for the month
    incomes = Income.objects.filter(user=user)
    for income in incomes:
        total_income.append(income.income)
        if income.pub_date.month == months:
            monthly_incomes.append(income.income)

    try:
        # To get most recent user country and currency
        c = Country.objects.filter(user=user).order_by("-id")[0]
        country = c
    except:
        pass
    
    return render(
        request,
        "website/profile.html",
        {
            "monthly_savings": sum(monthly_savings),
            "monthly_incomes": sum(monthly_incomes),
            "form":form,
            "income_form": income_form,
            "country": country,
            "incomes": incomes,
            "total_saving": sum(total_saving),
            "total_income": sum(total_income)
        }
    )
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('website:change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(
        request, 
        'website/change_password.html', 
    {
        'form': form
    })
def settings_view(request):
    countries = '' # to get user country and currency from Country model
    user = request.user
    if request.method == "POST":
        form = CountryForm(request.POST)
        if form.is_valid():
            user = Country(
                user = user,
                country = form.cleaned_data["country"],
                currency = form.cleaned_data["currency"],
            )
            user.save()
            return redirect("website:settings")
        else:
            form = CountryForm()
    
    try:
        #get the most recent added data from Country model
        country = Country.objects.filter(user = user).order_by("-id")[0]
        countries = country

    except:
        pass
    
    form = CountryForm()
    return render(
        request,
        "website/settings.html",
        {
            "form": form,
            "country": countries,
        }
    )
   
    