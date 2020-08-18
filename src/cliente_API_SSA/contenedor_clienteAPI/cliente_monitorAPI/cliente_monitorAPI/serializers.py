from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ['username', 'password']
	
	def create_user(self, validated_data):
		user = User(
			username=validated_data['username'],
			password=validated_data['password']
		)
        	user.save()
        	return user
	
	def delete_user(self, validated_data):
		user = User(username=validated_data['username'])
		user.delete
