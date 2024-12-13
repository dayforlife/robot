from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from robots.models import Robot
from .models import Order

@receiver(post_save, sender=Robot)
def notify_customers(sender, instance, created, **kwargs):
    if created:
        # Найти заказы, ожидающие эту модель и версию
        waiting_orders = Order.objects.filter(robot_serial=instance.serial)
        print(waiting_orders)
        for order in waiting_orders:
            # Отправляем письмо клиенту
            send_mail(
                subject="Ваш робот доступен!",
                message=f"Добрый день!\n\nНедавно вы интересовались нашим роботом модели {instance.model}, версии {instance.version}. Этот робот теперь в наличии. Если вам подходит этот вариант - пожалуйста, свяжитесь с нами.",
                from_email="noreply@company.com",
                recipient_list=[order.customer.email],
            )
