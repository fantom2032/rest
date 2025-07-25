# from django.db import models
# from django.contrib.auth.models import User


# class Chat(models.Model):
#     is_group = models.BooleanField(
#         verbose_name="групповой чат",
#         default=False
#     )
#     title = models.CharField(
#         verbose_name="заголовок",
#         max_length=100,
#         blank=True,
#         null=True
#     )
#     users = models.ManyToManyField(
#         to=User,
#         related_name="users_chats",
#         verbose_name="пользователи"
#     )

#     class Meta:
#         ordering = ("id",)
#         verbose_name = "чат"
#         verbose_name_plural = "чаты"

#     def __str__(self):
#         return f"{self.pk} -> {self.is_group}"


# class Message(models.Model):
#     text = models.TextField(
#         verbose_name="текст",
#         max_length=2000,
#         blank=True,
#         null=True
#     )
#     sender = models.ForeignKey(
#         to=User,
#         verbose_name="отправитель",
#         on_delete=models.SET_DEFAULT,
#         default="аноним",
#         related_name="messages_sender"
#     )
#     chat = models.ForeignKey(
#         to=Chat,
#         verbose_name="чат",
#         on_delete=models.CASCADE,
#         related_name="chat_messages"
#     )
#     sent_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name="отправлено"
#     )
#     parent = models.ForeignKey(
#         to="self",
#         on_delete=models.CASCADE,
#         verbose_name="ответ на...",
#         related_name="parent_message",
#         blank=True,
#         null=True
#     )

#     class Meta:
#         ordering = ("id",)
#         verbose_name = "сообщение"
#         verbose_name_plural = "сообщения"

#     def __str__(self):
#         return (f"{self.text[:20]} | {self.sender} "
#             f"| {self.sent_at} | {self.chat}")
