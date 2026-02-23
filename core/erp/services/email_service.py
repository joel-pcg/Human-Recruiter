import logging

from django.core.mail import EmailMessage
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_html_email(subject, template_name, context, recipient_email):
    try:
        html_content = render_to_string(template_name, context)
        email = EmailMessage(
            subject=subject,
            body=html_content,
            to=[recipient_email],
        )
        email.content_subtype = 'html'
        email.send(fail_silently=False)
        return True
    except Exception:
        logger.exception("Error enviando email a %s (asunto: %s)", recipient_email, subject)
        return False


def send_hiring_notification(employee):
    return send_html_email(
        subject="Felicidades, ha sido contratado!",
        template_name='email/hiring_notification.html',
        context={'employee': employee},
        recipient_email=employee.person.email,
    )


def send_vacation_finished_email(vacation):
    return send_html_email(
        subject="Recordatorio: Vacaciones Finalizadas",
        template_name='Vacations/vacation_finished.html',
        context={'vacations': vacation},
        recipient_email=vacation.empleado.person.email,
    )


def send_vacation_reminder_email(vacation):
    return send_html_email(
        subject="Recordatorio: Tus vacaciones finalizan manana",
        template_name='Vacations/vacation_reminder.html',
        context={'vacations': vacation},
        recipient_email=vacation.empleado.person.email,
    )


def send_password_reset_email(user, reset_link, home_link):
    return send_html_email(
        subject="Solicitud de cambio de contrasena",
        template_name='login/send_email.html',
        context={
            'user': user,
            'link_resetpwd': reset_link,
            'link_home': home_link,
        },
        recipient_email=user.employee.person.email,
    )
