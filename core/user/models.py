import logging
import uuid
from datetime import timedelta

from core.erp.models import Employee
from crum import get_current_request
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import model_to_dict
from django.utils import timezone
from config.settings import MEDIA_URL, STATIC_URL, PASSWORD_RESET_TOKEN_EXPIRY_HOURS

logger = logging.getLogger(__name__)


class User(AbstractUser):
    image = models.ImageField(upload_to='users/%Y/%m/%d', null=True, blank=True)
    token = models.UUIDField(primary_key=False, editable=False, null=True, blank=True)
    token_created_at = models.DateTimeField(null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Employee", unique=False, null=True)

    def generate_reset_token(self):
        self.token = uuid.uuid4()
        self.token_created_at = timezone.now()
        self.save()

    def is_token_valid(self):
        if self.token is None or self.token_created_at is None:
            return False
        expiry = self.token_created_at + timedelta(hours=PASSWORD_RESET_TOKEN_EXPIRY_HOURS)
        return timezone.now() < expiry


    def get_image(self):
        if self.image:
            return '{}{}'.format(MEDIA_URL, self.image)
        return '{}{}'.format(STATIC_URL, 'img/empty.png')

    def toJson(self):
        item = model_to_dict(self, exclude=['password', 'user_permissions',  'last_login'])
        if self.last_login:
            item['last_login'] = self.last_login.strftime('%Y-%m-%d')
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['image'] = self.get_image()
        item['groups'] = [{'id': g.id, 'name': g.name} for g in self.groups.all()]
        item['full_name'] = self.employee.get_full_name()

        if self.employee:
            item['employee__firstname'] = self.employee.person.firstname
            item['employee__lastname'] = self.employee.person.lastname
            self.first_name = self.employee.person.firstname
            self.last_name = self.employee.person.lastname
        return item


    def get_group_session(self):
        try:
            request = get_current_request()
            group = self.groups.all()
            if group.exists():
                if 'group' not in request.session:
                    request.session['group'] = group[0]
        except Exception:
            logger.warning("Failed to set group session", exc_info=True)

    
