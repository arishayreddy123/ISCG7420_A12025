from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import Reservation

@receiver(post_save, sender=Reservation)
def email_booking_confirmation(sender, instance, created, **kwargs):
    if not created:
        return
    # build subject & message
    subject = f"Booking Confirmed: {instance.room.name}"
    start = instance.start_time.strftime("%Y-%m-%d %H:%M")
    end   = instance.end_time.strftime("%Y-%m-%d %H:%M")
    message = (
        f"Hi {instance.user.username},\n\n"
        f"Your reservation for room “{instance.room.name}”\n"
        f"from {start} to {end} is confirmed.\n\n"
        "Thanks!"
    )
    # send via your SendGrid‐backed email settings
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [instance.user.email],
        fail_silently=False,
    )



