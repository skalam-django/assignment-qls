from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.permissions import SAFE_METHODS, OperandHolder, OR
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.exceptions import APIException
from django.core.cache import caches
import traceback
from qls.utils import printf, loggerf, CustomServerException, CustomClientException
from django.conf import settings
from rest_framework.renderers import JSONRenderer
from qls.response_handler import CustomResponse

class IsAuthenticatedAdmin(IsAuthenticated):
	def has_permission(self, request, view):
		if request.method in SAFE_METHODS and request.method=='OPTIONS':
			return True
		response=  super().has_permission(request, view)
		return response and request.user.is_authenticated==True and request.user.user_type==settings.USER_TYPE.index("qls") and request.user.groups.filter(name="qls-admin").exists()


class IsAuthenticatedStaff(IsAuthenticated):
	def has_permission(self, request, view):
		if request.method in SAFE_METHODS and request.method=='OPTIONS':
			return True
		response=  super().has_permission(request, view)
		return response and request.user.is_authenticated==True and request.user.user_type==settings.USER_TYPE.index("qls") and request.user.groups.filter(name="qls-staff").exists()



class IsAuthenticatedClient(IsAuthenticated):
	def has_permission(self, request, view):
		if request.method in SAFE_METHODS and request.method=='OPTIONS':
			return True
		response=  super().has_permission(request, view)
		return response and request.user.is_authenticated==True and request.user.user_type==settings.USER_TYPE.index("qls") and request.user.groups.filter(name="qls-client").exists()



class PostAnonRateThrottle(AnonRateThrottle):
	scope = 'post_anon'
	cache = caches['throttling']

	def allow_request(self, request, view):
		if request.method == "GET":
			return True
		return super().allow_request(request, view)

	def get_cache_key(self, request, view):
		cache_format 	= 	super().get_cache_key(request, view)
		ident 	=	self.get_ident(request)
		if ident is not None:
			request.ident 	= 	ident
		return cache_format


class GetAnonRateThrottle(AnonRateThrottle):
	scope =	'get_anon'
	cache = caches['throttling']

	def allow_request(self, request, view):
		if request.method == "POST":
			return True
		return super().allow_request(request, view)

	def get_cache_key(self, request, view):
		cache_format 	= 	super().get_cache_key(request, view)
		ident 	=	self.get_ident(request)
		if ident is not None:
			request.ident 	= 	ident
		return cache_format


class PostUserRateThrottle(UserRateThrottle):
	scope = 'post_user'
	cache = caches['throttling']

	def allow_request(self, request, view):
		if request.method == "GET":
			return True
		return super().allow_request(request, view)

	def get_cache_key(self, request, view):
		cache_format 	= 	super().get_cache_key(request, view)
		ident 	=	self.get_ident(request)
		if ident is not None:
			request.ident 	= 	ident
		return cache_format

class GetUserRateThrottle(UserRateThrottle):
	scope = 'get_user'
	cache = caches['throttling']

	def allow_request(self, request, view):
		if request.method == "POST":
			return True
		return super().allow_request(request, view)

	def get_cache_key(self, request, view):
		cache_format 	= 	super().get_cache_key(request, view)
		ident 	=	self.get_ident(request)
		if ident is not None:
			request.ident 	= 	ident
		return cache_format


class APIAuthenticateView(APIView):
	parser_classes 		= 	[JSONParser, MultiPartParser, FormParser]
	throttle_classes 	= 	[
								PostAnonRateThrottle, 
								GetAnonRateThrottle, 
								PostUserRateThrottle, 
								GetUserRateThrottle,
							]

	def finalize_response(self, request, response, *args, **kwargs):
		response = super().finalize_response(request, response, *args, **kwargs)
		if request.user is not None and request.user.is_authenticated and request.user.tracking == True:
			UserTracking.objects.track(request, response)
		return response	

	def handle_exception(self, exc):
		log_label 	= 	'Error'	
		trace 		= 	traceback.format_exc()
		info 		= 	False
		if isinstance(exc, CustomClientException):
			log_label= 	'CustomClientException'
			info	 = 	True
			tracking = self.request.user.tracking if self.request.user.is_authenticated else False
			if settings.TRACEBACK_OFF == True and tracking==False:
				trace = ""
			response = 	CustomResponse(data={}, status=exc)
		elif isinstance(exc, APIException):
			response = super().handle_exception(exc)
		elif isinstance(exc, CustomServerException):
			response 	= 	CustomResponse(data={}, status=exc)
		else:
			response 	= 	CustomResponse(data={}, status=500)
		
		loggerf(f"************************ {log_label} ************************ : {exc}\n", trace, info=info)		
					

		return self.process_response(self.request, response)

	def process_response(self, request, response):
		try:			
			if hasattr(response, 'data')==False or response.data is None:
				response.data = dict()
			response.data['success'] 	= response.data['success'] if 'success' in response.data else (True if response.status_code in settings.SAFE_STATUS_CODE else False)
			response.data['error'] 		= response.data['error'] if 'error' in response.data else (False if response.status_code in settings.SAFE_STATUS_CODE else True)
			response.data['message'] 	= response.data['message'] if 'message' in response.data else None
			if 'error_details' not in response.data:
				response.data['error_details'] = {
													"description" : str(response.data['detail']) if 'detail' in response.data else "Something went wrong",
													"field" : None,
													"error_type" : "BAD_REQUEST_ERROR" if 'detail' in response.data else "INTERNAL_SERVER_ERROR"
												}
				if 'detail' in response.data:								
					response.data.pop("detail")					
			status_code = response.status_code
	
			response.status_code = (200 if status_code not in settings.SAFE_STATUS_CODE else status_code) if status_code!=500 else status_code				
			response.data['status_code']= status_code
			response.data['status_text']= response.status_text
			response.accepted_renderer =  JSONRenderer()
			response.renderer_context = {}	
			response.accepted_media_type = "application/json"

			return response

		except (APIException, CustomServerException, CustomClientException) as e:
			raise type(e)(e)
		except Exception as e:
			import traceback
			loggerf(traceback.format_exc())
			loggerf(f"APIAuthenticateView().process_response() Error: {e}")
			raise type(e)(e)	





######################### using these classes below, user can be authenticated only by Token #####################


class AdminTokenAuthApi(APIAuthenticateView):
	authentication_classes 		= 	(TokenAuthentication,)
	permission_classes 			= 	[IsAuthenticatedAdmin,]


class StaffTokenAuthApi(APIAuthenticateView):
	authentication_classes 		= 	(TokenAuthentication,)
	permission_classes 			= 	[OperandHolder(OR, IsAuthenticatedStaff, IsAuthenticatedAdmin),]


class ClientTokenAuthApi(APIAuthenticateView):
	authentication_classes 		= 	(TokenAuthentication,)
	permission_classes 			= 	[OperandHolder(OR, OperandHolder(OR, IsAuthenticatedClient, IsAuthenticatedStaff), IsAuthenticatedAdmin), ]

class AllUserTokenAuthApi(APIAuthenticateView):
	authentication_classes 		= 	(TokenAuthentication,)
	permission_classes 			= 	[IsAuthenticated,]

#########################################################################################################################



######################### using these classes below, user can be authenticated only by Basic #####################

class AdminBasicAuthApi(APIAuthenticateView):
	authentication_classes 		= 	(BasicAuthentication,)
	permission_classes 			= 	[IsAuthenticatedAdmin,]


class StaffBasicAuthApi(APIAuthenticateView):
	authentication_classes 		= 	(BasicAuthentication,)
	permission_classes 			= 	[OperandHolder(OR, IsAuthenticatedStaff, IsAuthenticatedAdmin),]


class ClientBasicAuthApi(APIAuthenticateView):
	authentication_classes 		= 	(BasicAuthentication,)
	permission_classes 			= 	[OperandHolder(OR, OperandHolder(OR, IsAuthenticatedClient, IsAuthenticatedStaff), IsAuthenticatedAdmin), ]


class AllUserBasicAuthApi(APIAuthenticateView):
	authentication_classes 		= 	(BasicAuthentication,)
	permission_classes 			= 	[IsAuthenticated,]

####################################################################################################################


######################### using these classes below, user can be authenticated either by Token or by Basic #####################
class AdminAuthApi(APIAuthenticateView):
	authentication_classes 		= 	(TokenAuthentication, BasicAuthentication,)
	permission_classes 			= 	[IsAuthenticatedAdmin,]


class StaffAuthApi(APIAuthenticateView):
	authentication_classes 		= 	(TokenAuthentication, BasicAuthentication,)
	permission_classes 			= 	[OperandHolder(OR, IsAuthenticatedStaff, IsAuthenticatedAdmin),]


class ClientAuthApi(APIAuthenticateView):
	authentication_classes 		= 	(TokenAuthentication, BasicAuthentication,)
	permission_classes 			= 	[OperandHolder(OR, OperandHolder(OR, IsAuthenticatedClient, IsAuthenticatedStaff), IsAuthenticatedAdmin),]


class AllUserAuthApi(APIAuthenticateView):
	authentication_classes 		= 	(TokenAuthentication, BasicAuthentication,)
	permission_classes 			= 	[IsAuthenticated,]	

################################################################################################################




