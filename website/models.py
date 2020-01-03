from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

class SiteContent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    expense_date = models.DateField("published")
    expense_category = models.CharField(max_length=120)
    spent = models.DecimalField(max_digits=7, decimal_places=2)
    content_bought = models.CharField(max_length=300)
    #history = HistoricalRecords()

    class Meta:
        verbose_name_plural = "Contents"

    def __str__(self):
        return self.expense_category

class PublishedDate(models.Model):
    date_expense = models.DateField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE)
    
    class Meta:
        verbose_name_plural = "Dates"

class Budget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(decimal_places= 2, max_digits= 7)
    budget_date = models.DateField()
    class Meta:
        verbose_name_plural = "Budgets"
    def __str__(self):
        return self.category

class BudgetDate(models.Model):
    date_budget = models.DateField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE)
    
    class Meta:
        verbose_name_plural = "Dates"

class Savings(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    savings = models.DecimalField(decimal_places=2, max_digits=9)
    pub_date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Savings"


class Income(models.Model):
    income = models.DecimalField(max_digits=9, decimal_places=2)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    pub_date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Income"

class Country(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    country = CountryField(blank_label="(select country)")
    currency = models.CharField(max_length=20)
    
    class Meta:
        verbose_name_plural = "Countries"
    
    def __str__(self):
        return self.country

class UserProfile(models.Model):        
    # required to associate Author model with User model (Important)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
 
    # additional fields
    activation_key = models.CharField(max_length=255, default=1)
    email_validated = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email
    
 

