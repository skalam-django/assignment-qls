import datetime, json
from django.db import models
from django.contrib.auth.models import UserManager, Group
from django.db import transaction
from django.conf import settings
from qls.utils import printf, loggerf, CustomServerException, CustomClientException, LazyEncoder
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password
import traceback


class AuthUserManager(UserManager):
	def create_superuser(self, *args, **kwargs):
		auth_obj = None
		with transaction.atomic(using = self.db):					
			auth_obj 			= 	super().create_superuser(*args, **kwargs)
			printf(f"Superuser with username: {kwargs.get('username')} created.")	
			group_qs  			=   Group.objects.filter(name__in = [f"{settings.USER_TYPE[0]}-{user_group}" for user_group in settings.USER_GROUP])
			for group_obj in group_qs:
				auth_obj.groups.add(group_obj)
				print(f"Added to group : {group_obj.name}")
		return auth_obj

	def create_user(self, *args, **kwargs):
		auth_obj = None
		with transaction.atomic(using = self.db):
			usertype = settings.USER_TYPE[kwargs.get('user_type')]
			if kwargs.get("password") is None and len(args) > 0:
				kwargs["password"] = make_password(f"{usertype}-{args[0]}@123")

			auth_obj 			= 	self.create(**kwargs)

			printf(f"User with username: {kwargs.get('username')} Email: {kwargs.get('email')}, user type: {usertype} created.")						

			if len(args) > 0:
				group_qs  		=   Group.objects.filter(name__in = [f"{usertype}-{user_group}" for user_group in settings.USER_GROUP[settings.USER_GROUP.index(args[0]):] ])
				for group_obj in group_qs:
					auth_obj.groups.add(group_obj)	
					print(f"Added to group : {group_obj.name}")		
		return auth_obj		
			


class UserTrackingManager(models.Manager):
	def track(self, *args, **kwargs):
		try:
			request 	= 	args[0]
			response 	= 	args[1]
			self.create(
					user_id 		= 	request.user.id if request.user.is_authenticated else None,
					ident 			=	request.ident,
					user_agent		=	request.headers.get('User-Agent'),
					authorization 	= 	request.headers.get("Authorization"),
					url 			=	str(request.path_info),
					request_payload =	json.dumps(request.data,cls=LazyEncoder),
					response_data	= 	json.dumps(response.data, cls=LazyEncoder),
					response_status	= 	str(response.status_code)
				)
		except Exception as e:
			import traceback
			loggerf(f"UserTrackingManager().track() Error: {e}", traceback.format_exc())	


