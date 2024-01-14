from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
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
    username = None
    first_name = models.CharField(_('first name'), max_length=30, default=None, blank=True, null=True)
    last_name = models.CharField(_('last name'), max_length=150, default=None, blank=True, null=True)
    password = models.CharField(_('password'), max_length=128, blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True, blank=True, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()
    full_name = models.CharField(max_length=100)
    phone = models.CharField('Cellulare', max_length=20, default=None, blank=True, null=True,
                             help_text='Apponi sempre +39 prima del numero')
    verified = models.BooleanField(default=False)
    CLASSI_CHOICES = [('1AC', '1AC'), ('2AC', '2AC'), ('3AC', '3AC'), ('4AC', '4AC'), ('5AC', '5AC'), ('1BC', '1BC'),
                      ('2BC', '2BC'), ('3BC', '3BC'), ('4BC', '4BC'), ('5BC', '5BC'), ('1CC', '1CC'), ('2CC', '2CC'),
                      ('3CC', '3CC'), ('4CC', '4CC'), ('5CC', '5CC'), ('1DC', '1DC'), ('2DC', '2DC'), ('3DC', '3DC'),
                      ('4DC', '4DC'), ('5DC', '5DC'), ('1EC', '1EC'), ('2EC', '2EC'), ('3EC', '3EC'), ('4EC', '4EC'),
                      ('5EC', '5EC'), ('1AL', '1AL'), ('2AL', '2AL'), ('3AL', '3AL'), ('4AL', '4AL'), ('5AL', '5AL'),
                      ('1BL', '1BL'), ('2BL', '2BL'), ('3BL', '3BL'), ('4BL', '4BL'), ('5BL', '5BL'), ('1CL', '1CL'),
                      ('2CL', '2CL'), ('3CL', '3CL'), ('4CL', '4CL'), ('5CL', '5CL'), ('1DL', '1DL'), ('2DL', '2DL'),
                      ('3DL', '3DL'), ('4DL', '4DL'), ('5DL', '5DL'), ('1EL', '1EL'), ('2EL', '2EL'), ('3EL', '3EL'),
                      ('4EL', '4EL'), ('5EL', '5EL'), ('1FL', '1FL'), ('2FL', '2FL'), ('3FL', '3FL'), ('4FL', '4FL'),
                      ('5FL', '5FL'), ('1GL', '1GL'), ('2GL', '2GL'), ('3GL', '3GL'), ('4GL', '4GL'), ('5GL', '5GL'),
                      ('1HL', '1HL'), ('2HL', '2HL'), ('3HL', '3HL'), ('4HL', '4HL'), ('5HL', '5HL')]

    classe = models.CharField(max_length=3, default=None, blank=True, null=True, choices=CLASSI_CHOICES)
    notes = models.TextField(max_length=500, default=None, blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, default=None, blank=True, null=True)

    def participations_count(self):
        return self.participation_set.filter(is_active=True, presence_type_id=2).count()

    def school_year(self):
        classe = self.classe
        year = int(classe[0])
        return year

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = 'auth_user'
        verbose_name = "utente"
        verbose_name_plural = "utenti"


class UserConsent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    privacy_policy_consent = models.DateTimeField(default=None, blank=True, null=True)
