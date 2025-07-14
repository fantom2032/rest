from datetime import timedelta, date

from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.utils import timezone
from loguru import logger

from settings.celery import app
from common.mail import send_email


@app.task(name="send-congrats")
def send_congrats():
    lookup_date: date = \
        (timezone.now() - timedelta(days=22)).date()
    users: QuerySet[User] = User.objects.filter(
        # username__icontains="qwe",
        date_joined__date=lookup_date
    )
    if not users:
        logger.info(
            "Нет пользователей зарегистрированных 22 дня назад"
        )
        return
    to = [user.email for user in users]
    send_email(
        to=to,
        template="congrats.html", 
        title="Спасибо что вы с нами"
    )
    logger.info("Message sent")

@app.task(name="send-activation-email")
def send_activation_email(email, username, code):
    send_email(
        template="activation.html",
        context={
            "username": username,
            "code": f"http://127.0.0.1:8000/api/v1/users/activate/{code}"
        },
        to=email,
        title="Confirm your account"
    )