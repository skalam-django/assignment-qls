from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
import traceback
from rest_framework.exceptions import server_error
from qls.utils import loggerf, printf
import json



class CustomMiddleware(MiddlewareMixin):
	def __init__(self, get_response, *args, **kwargs):
		return super(CustomMiddleware, self).__init__(get_response, *args, **kwargs)
		
	def process_request(self, request, *args, **kwargs):
		pass

	def process_response(self, request, response):
		return response

	def process_view(self, request, view_func, view_args, view_kwargs):
		self.func_name 		=	view_func.__name__
		self.func_module 	= 	view_func.__module__

	def process_exception(self, request, exception):
		loggerf(traceback.format_exc())
		error = f'[ERROR] {self.func_module}.{self.func_name}(): {exception}'
		loggerf(error)
		return JsonResponse({'detail':str(exception)})




