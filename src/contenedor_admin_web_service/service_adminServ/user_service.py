import django
django.setup()
import os
from django.contrib.auth.models import User

res = User.objects.filter(username=os.environ.get('MASTER_USR_BE', ''))

if len(res) == 0:
    User.objects.create_user(username=os.environ.get('MASTER_USR_BE', ' '), password=os.environ.get('MASTER_PASS_BE', ''))
