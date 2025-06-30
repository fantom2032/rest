from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=20, unique=True)
    invite_code = models.CharField(max_length=6, unique=True, editable=False)
    activated_invite_code = models.CharField(max_length=6, null=True, blank=True)
    invited_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='invited_users')

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} | {self.phone}"

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
