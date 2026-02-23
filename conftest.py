import pytest
from django.contrib.auth.models import Group, Permission


@pytest.fixture
def admin_group(db):
    group = Group.objects.create(name='Administrador')
    all_permissions = Permission.objects.all()
    group.permissions.set(all_permissions)
    return group
