import uuid

from django.db.models.signals import (
    pre_delete, post_delete, pre_save, post_save
)
from django.contrib.auth.signals import (
    user_logged_in, user_logged_out, user_login_failed
)
from django.dispatch import receiver
from django.contrib.auth.models import User
from loguru import logger
from django.conf import settings
from common.mail import send_email
from users.models import Codes, UserLoginData


@receiver(signal=post_save, sender=User)
def post_registration(
    sender: User, instance: User, created: bool, **kwargs
):
    if created:
        temp = str(uuid.uuid4())
        code = Codes(user=instance, code=temp)
        code.save()
        try:
            send_email(
                template="activation.html", 
                context={
                    "username": instance.username, 
                    "code": ("http://127.0.0.1:8000/"
                        f"api/v1/users/activate/{temp}")},
                to=instance.email, title="Confirm your account"
            )
            logger.info(f"Письмо активации ушло на {instance.email}")
        except Exception:
            pass
        return
    # какая-то логика
    logger.info("это после обновления")

    
@receiver(signal=pre_save, sender=User)
def log_something(instance: User, **kwargs):
    user = User.objects.get(pk=instance.pk)
    # if user.password != instance.password:
    #     send_email()
    #     return
    
@receiver(user_logged_in)
def check_ip_on_login(sender, user, request, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    login_data, created = UserLoginData.objects.get_or_create(user=user)
    if ip not in login_data.confirmed_ips:
        send_email(
            'Подтверждение нового IP-адреса',
            f'Обнаружен вход с нового IP: {ip}. Подтвердите, что это вы.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True,
        )
    login_data.last_ip = ip
    if ip not in login_data.confirmed_ips:
        login_data.confirmed_ips.append(ip)
    login_data.save()