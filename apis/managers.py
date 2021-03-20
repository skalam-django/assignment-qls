from django.db import models
from qls.utils import printf, loggerf, CustomServerException, CustomClientException, data_handler
from django.db import transaction
from django.db.models.query import QuerySet


class AddressManager(models.Manager):
	def add(self, *args, **kwargs):
		city = args[0].get('city')
		landmark = args[0].get('landmark')
		postal_address = args[0].get('postal_address')
		if city is None: 
			raise CustomClientException(427)
		if landmark is None:
			raise CustomClientException(428)
		if postal_address is None:
			raise CustomClientException(429)
		obj = self.create(
				city = city,
				landmark = landmark,
				postal_address = postal_address
			)
		return obj

class StudentManager(models.Manager):
	def add(self, *args, **kwargs):
		student_name 	= 	args[0].get('student_name')
		standard  		=	args[0].get('standard')
		address 		= 	args[0].get('address')
		if student_name is None:
			raise CustomClientException(424)
		if standard is None:
			raise CustomClientException(422)
		try:
			standard = int(standard)
		except:
			raise CustomClientException(425)

		if address is None:
			raise CustomClientException(426)

		obj = None
		with transaction.atomic(using = self.db):	
			from apis.models import Address		
			addr_obj = Address.objects.add(address)
			obj = self.create(
					student_name 	= 	student_name,
					standard 		=	standard,
					address 		=	addr_obj
				)
		data_arr = data_handler(
						self.filter(id=obj.id), 
						fields=[
							'id',
							'student_name',
							'standard',
							'address__id',
							'address__city',
							'address__landmark',
							'address__postal_address'
						], 
						func_fields={}, 
						new_fields={},  
						idx=None, 
						exception=CustomClientException(423)
					)		
		return self.reformat(data_arr)[0]

	def details(self, *args, **kwargs):
		standard = args[0].get('standard')
		if standard is None:
			raise CustomClientException(422)
		try:
			standard = int(standard)
		except:
			raise CustomClientException(425)	
		data_arr = data_handler(
						self.filter(standard=standard)	, 
						fields=[
							'id',
							'student_name',
							'standard',
							'address__id',
							'address__city',
							'address__landmark',
							'address__postal_address'
						], 
						func_fields={}, 
						new_fields={},  
						idx=None, 
						exception=CustomClientException(423)
					)

		return self.reformat(data_arr)

	def reformat(self, *args, **kwargs):
		new_data_arr = []
		for data in args[0]:
			data['student_id'] = data['id']
			del data['id']
			data['address'] = {
				'address_id' 	: 	data['address__id'],
				'city' 			:	data['address__city'],
				'landmark' 		:	data['address__landmark'],
				'postal_address':	data['address__postal_address']
			}
			del data['address__id']
			del data['address__city']
			del data['address__landmark']
			del data['address__postal_address']
			new_data_arr.append(data)
		return new_data_arr			


