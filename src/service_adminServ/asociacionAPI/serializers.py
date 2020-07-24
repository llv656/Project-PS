from rest_framework import serializers
from .models import *

class AdminSerializer(serializers.ModelSerializer):
	servers = serializers.StringRelatedField(many=True)
	class Meta:
		model = Admin
		fields = ['user_admin','servers']
