from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Codes(models.Model):
    code = models.CharField(
        verbose_name="код активации",
        unique=False,
        default="qwertyuiop"
    )
    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE,
        related_name="user_code",
        verbose_name="пользователь"
    )
    created_at = models.DateTimeField(
        verbose_name="дата создания",
        default=timezone.now
    )

    class Meta:
        ordering = ("created_at",)
        verbose_name = "код активации"
        verbose_name_plural = "коды активации"

    def __str__(self):
        return f"{self.user.username} | {self.created_at}"
class UserLoginData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_ip = models.GenericIPAddressField(null=True, blank=True)
    confirmed_ips = models.JSONField(default=list, blank=True)  # список подтвержденных IP

    def __str__(self):
        return f"{self.user.username} login data"