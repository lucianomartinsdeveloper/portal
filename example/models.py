import uuid

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.contrib.auth.models import UserManager as BaseUserManager
from django.core.mail import send_mail
from django.db import models
from django.db.models import UUIDField
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    AUTONOMO = "AT"
    OCCUPATION_CHOICES = [
        (AUTONOMO, "Autônomo"),
    ]
    MIG = "MIG"
    PRO = "PRO"
    CUR = "CUR"
    TYPE_OF_AUDIENCE_CHOICES = [
        (MIG, "Migrando para a área de agilidade"),
        (PRO, "Profissional da área de agilidade"),
        (CUR, "Curioso sobre o universo da agilidade"),
    ]
    username = models.CharField("Nome", max_length=150)
    uid = UUIDField(default=uuid.uuid4, editable=False)
    email = models.EmailField("Email", unique=True)
    occupation = models.CharField(
        max_length=2,
        choices=OCCUPATION_CHOICES,
        default=AUTONOMO,
    )
    birth_date = models.DateField("Data de Nascimento")
    type_of_audience = models.CharField(
        "Tipo de público", max_length=3, choices=TYPE_OF_AUDIENCE_CHOICES
    )
    cpf = models.CharField(max_length=11, null=True, blank=True)
    registered = models.BooleanField("Inscrito", default=False)
    subscriber = models.BooleanField("Assinante", default=False)
    is_deleted = models.BooleanField("Foi deletado?", default=False)
    deleted_at = models.DateTimeField("Data da Deleção", null=True, blank=True)
    address = models.ForeignKey(
        "Address",
        on_delete=models.CASCADE,
        related_name="addressies",
        blank=True,
        null=True,
    )
    telephone = models.ForeignKey(
        "Telephone",
        on_delete=models.CASCADE,
        related_name="telephones",
        blank=True,
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin site."
        ),
    )
    is_active = models.BooleanField("Ativo", default=True)
    date_joined = models.DateTimeField("Data da Entrada", auto_now_add=True)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "birth_date"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.email

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = f"{self.username}"
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.username

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)


# @receiver(post_save, sender=User)
# def send_email_on_user_creation(sender, instance, created, **kwargs):
#     if created:
#         send_mail(
#             'Novo usuário criado',
#             f'Um novo usuário com email {instance.email} foi criado.',
#             'from@example.com',
#             ['to@example.com'],
#             fail_silently=False,
#         )


class Occupation(models.Model):
    name = models.CharField("Nome", max_length=30)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Profissão"
        verbose_name_plural = "Profissões"


class Telephone(models.Model):
    TYPE_PHONE = [
        ("cel", "Celular"),
        ("fix", "Fixo"),
    ]

    number = models.CharField("Número", max_length=20)
    type = models.CharField("Número", choices=TYPE_PHONE, max_length=3)

    def __str__(self):
        return f"{self.number}"

    class Meta:
        verbose_name = "Telefone"
        verbose_name_plural = "Telefones"


class Address(models.Model):
    public_place = models.CharField("Logradouro", max_length=100)
    neighborhood = models.CharField("Bairro", max_length=255, blank=True)
    city = models.CharField("Cidade", max_length=50, blank=True)
    zip_code = models.IntegerField("CEP")
    number = models.IntegerField("Número")
    complement = models.CharField(
        "Complemento", max_length=10, null=True, blank=True
    )

    def __str__(self):
        return f"{self.public_place}, {self.number} - {self.complement}"

    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"
