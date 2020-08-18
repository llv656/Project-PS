import django
django.setup()
import os
from django.contrib.auth.models import User

try:
	User.objects.get(username=os.environ.get('USR_MASTER_SERVICE', ''))
except:
	usuario = User.objects.create_user(username=os.environ.get('USR_MASTER_SERVICE', ' '), password=os.environ.get('PASS_MASTER_SERVICE', ''))
	usuario.is_staff = True
	usuario.save()

