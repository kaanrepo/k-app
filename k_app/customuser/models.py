import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError
# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, is_active=True, is_staff=False, is_superuser=False):
        if not username:
            raise ValidationError('Username is required.')
        if not email:
            raise ValidationError('Email is required.')
        if not password:
            raise ValidationError('Password is required.')
        
        user = self.model(
            username = username,
            email = self.normalize_email(email)
        )
        user.set_password(password)
        user.staff = is_staff
        user.superuser = is_superuser
        user.active = is_active
        user.save(using=self._db)
        return user




    def create_staff(self, username, email, password=None):
        user = self.create_user(
            username,
            email,
            password=password,
            is_staff=True
        )
        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(
            username,
            email,
            password=password,
            is_staff=True,
            is_superuser=True
        )
        return user

class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=200, unique=True)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    superuser = models.BooleanField(default=False)
    updated = models.DateField(auto_now=True)
    created = models.DateField(auto_now_add=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
    

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_superuser(self):
        return self.superuser

    @property
    def is_active(self):
        return self.active
