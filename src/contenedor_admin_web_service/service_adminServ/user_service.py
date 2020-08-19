import django
django.setup()
import os
from django.contrib.auth.models import User

try:
	User.objects.get(username=os.environ.get('MASTER_USR_BE', ''))
except:
	usuario = User.objects.create_user(username=os.environ.get('MASTER_USR_BE', ' '), password=os.environ.get('MASTER_PASS_BE', ''))
	usuario.is_staff = True
	usuario.save()
finally:
	exit()
