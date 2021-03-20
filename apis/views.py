from auth_app.views import ClientAuthApi
from qls.utils import (
							printf, loggerf, 
							CustomServerException, CustomClientException, 
							LazyEncoder,
							full_data, 
							data_handler
							)
from qls.response_handler import CustomResponse
from django.conf import settings
from apis.models import Student

class StudentsApi(ClientAuthApi):
	def get(self, request, *args, **kwargs):
		data = {}
		status = 500
		try:
			payload = full_data(request)
			data = Student.objects.details(payload)
			status = 200
		except (CustomServerException, CustomClientException) as e:
			status = e
		except Exception as e:
			status = 500
		return CustomResponse(data={'data' : data}, status=status)


	def post(self, request, *args, **kwargs):
		data = {}
		status = 500
		try:
			payload = full_data(request)
			data = Student.objects.add(payload)
			status = 201
		except (CustomServerException, CustomClientException) as e:
			status = e
		except Exception as e:
			status = 500
		return CustomResponse(data={'data' : data}, status=status)


