import logging
import uuid
from core.erp.models import Employee
from crum import get_current_request
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import model_to_dict
from config.settings import MEDIA_URL, STATIC_URL

logger = logging.getLogger(__name__)


class User(AbstractUser):
    image = models.ImageField(upload_to='users/%Y/%m/%d', null=True, blank=True)
    token = models.UUIDField(primary_key=False, editable=False, null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Employee", unique=False,null=True)


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
            groups = self.groups.all()
            if groups.exists():
                if 'group_id' not in request.session:
                    request.session['group_id'] = groups[0].id
        except Exception:
            logger.exception("Error setting group session for user %s", self.username)

    
