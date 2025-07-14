import uuid

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from loguru import logger

from users.models import Codes
from users.tasks import send_activation_email  # Импортируем celery-задачу

@receiver(post_save, sender=User)
def post_registration(sender, instance, created, **kwargs):
    if created:
        temp = str(uuid.uuid4())
        code = Codes(user=instance, code=temp)
        code.save()
        try:
            # Запускаем celery-задачу вместо прямой отправки письма
            send_activation_email.delay(
                email=instance.email,
                username=instance.username,
                code=temp
            )
            logger.info(f"Задача на отправку письма активации создана для {instance.email}")
        except Exception as e:
            logger.error(f"Ошибка при создании задачи отправки письма: {e}")
        return
    logger.info("это после обновления")