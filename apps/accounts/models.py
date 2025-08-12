from django.db.models import TextChoices
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from apps.common.models import UUIDModel


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number is required")
        user = self.model(phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(phone_number, password, **extra_fields)


class User(UUIDModel, AbstractBaseUser, PermissionsMixin):
    phone_number = PhoneNumberField(
        unique=True, region="IR")  # store E.164 (+98...)
    email = models.EmailField(
        max_length=254, null=True, blank=True, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []  # prompts only for phone + password in createsuperuser

    objects = UserManager()

    def __str__(self):
        return str(self.phone_number)


class UserProfile(UUIDModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile")
    first_name_fa = models.CharField(_("نام"), max_length=80, blank=True)
    last_name_fa = models.CharField(
        _("نام خانوادگی"), max_length=80, blank=True)
    city = models.CharField(_("شهر"), max_length=80, blank=True)
    birthday = models.DateField(null=True, blank=True)

    # SMS consent (single channel for now)
    sms_opt_in = models.BooleanField(default=False)
    sms_opt_in_at = models.DateTimeField(null=True, blank=True)
    # checkout/signup/etc.
    sms_opt_in_source = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"Profile<{self.user_id}>"


class OTPCode(UUIDModel):
    PURPOSE_LOGIN = "login"
    PURPOSE_VERIFY = "verify_phone"
    PURPOSE_RESET = "reset_pass"
    PURPOSE_CHOICES = [
        (PURPOSE_LOGIN, "Login"),
        (PURPOSE_VERIFY, "Verify Phone"),
        (PURPOSE_RESET, "Reset Password"),
    ]

    phone_number = PhoneNumberField(region="IR", db_index=True)
    code_hash = models.CharField(max_length=128)  # never store raw codes
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"OTP<{self.phone_number}, {self.purpose}>"


class OtpPurpose(TextChoices):
    LOGIN = "login", _("ورود")
    VERIFY = "verify_phone", _("تأیید شماره")
    RESET = "reset_pass", _("بازنشانی رمز")
