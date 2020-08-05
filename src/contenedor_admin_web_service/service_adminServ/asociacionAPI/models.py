from django.db import models

class Admin(models.Model):
	user_admin = models.CharField(max_length=20, null=False, blank=False, unique=True)

class Servers(models.Model):
	admin = models.ForeignKey(Admin, related_name='servers', on_delete=models.CASCADE)
	ip_server = models.GenericIPAddressField(null=False, blank=False, unique=True)

	class Meta:
		unique_together = ['admin', 'ip_server']
		ordering = ['ip_server']

	def __str__(self):
		return '%s' % (self.ip_server)
