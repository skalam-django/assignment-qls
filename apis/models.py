from django.db import models
from apis.managers import AddressManager, StudentManager

class Address(models.Model):
	city 			=	models.CharField(max_length=255)
	landmark  		=	models.CharField(max_length=255)
	postal_address  =	models.CharField(max_length=255)
	created_at 		=	models.DateTimeField(auto_now_add=True)
	updated_at 		=	models.DateTimeField(auto_now=True)
	objects 		=	AddressManager()
	class Meta:
		managed = True
		db_table = 'address'

class Student(models.Model):
	student_name 	=	models.CharField(max_length=255)
	standard		=	models.SmallIntegerField()
	address 		=	models.ForeignKey(Address, on_delete=models.CASCADE)
	created_at 		=	models.DateTimeField(auto_now_add=True)
	updated_at 		=	models.DateTimeField(auto_now=True)
	objects 		=	StudentManager()
	class Meta:
		managed = True
		db_table = 'student'





