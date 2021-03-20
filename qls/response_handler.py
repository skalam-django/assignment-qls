from qls.utils import loggerf, printf
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from rest_framework.renderers import JSONRenderer

RESPONSE_DICT = dict()



RESPONSE_DICT[200] = {"success" : True, "error" : False, "status" : 200, "message" : _("Everything went as planned"), "error_description" : None, "error_field" : None, "error_type" : None}
RESPONSE_DICT[201] = {"success" : True, "error" : False, "status" : 201, "message" : _("Student Created!"), "error_description" : None, "error_field" : None, "error_type" : None}

RESPONSE_DICT[422] = {"success" : True, "error" : True, "status" : 422, "message" : None, "error_description" : _("Standard is not provided."), "error_field" : None, "error_type" : 'BAD_REQUEST_ERROR'}
RESPONSE_DICT[423] = {"success" : True, "error" : True, "status" : 422, "message" : None, "error_description" : _("No student data found for this standard."), "error_field" : "standard", "error_type" : 'BAD_REQUEST_ERROR'}
RESPONSE_DICT[424] = {"success" : True, "error" : True, "status" : 422, "message" : None, "error_description" : _("Student name is not provided."), "error_field" : "", "error_type" : 'BAD_REQUEST_ERROR'}
RESPONSE_DICT[425] = {"success" : True, "error" : True, "status" : 422, "message" : None, "error_description" : _("Invalid standard"), "error_field" : "standard", "error_type" : 'BAD_REQUEST_ERROR'}
RESPONSE_DICT[426] = {"success" : True, "error" : True, "status" : 422, "message" : None, "error_description" : _("Address is not provided"), "error_field" : "address", "error_type" : 'BAD_REQUEST_ERROR'}
RESPONSE_DICT[427] = {"success" : True, "error" : True, "status" : 422, "message" : None, "error_description" : _("City is not provided"), "error_field" : "city", "error_type" : 'BAD_REQUEST_ERROR'}
RESPONSE_DICT[428] = {"success" : True, "error" : True, "status" : 422, "message" : None, "error_description" : _("Landmark is not provided"), "error_field" : "landmark", "error_type" : 'BAD_REQUEST_ERROR'}
RESPONSE_DICT[429] = {"success" : True, "error" : True, "status" : 422, "message" : None, "error_description" : _("Postal address is not provided"), "error_field" : "postal_address", "error_type" : 'BAD_REQUEST_ERROR'}

RESPONSE_DICT[500] = {"success" : False, "error" : True, "status" : 500, "message" : None, "error_description" : _("Something went wrong"), "error_field" : None, "error_type" : _("INTERNAL_SERVER_ERROR")}



class CustomResponse(Response):
	def __init__(self, data=None, status=None, content_type='application/json', *args, **kwargs):
		try:
			status = int(str(status))
		except Exception as e:
			loggerf(f"CustomResponse().__init__() Error: {e}, status: {status}")
			self.__init__({}, 500)


		if status in RESPONSE_DICT:
			self.data 	= 	{
							"success" 		: 	RESPONSE_DICT[status]["success"],
							"error" 		:	RESPONSE_DICT[status]["error"],
							"message" 		:	RESPONSE_DICT[status]["message"],
							"error_details"	:	{
												"description" 	: 	RESPONSE_DICT[status]["error_description"],
												"field" 		:	RESPONSE_DICT[status]["error_field"],
												"error_type" 	: 	RESPONSE_DICT[status]["error_type"],
							},
			}

			self.data.update(data)			
			self.status = 	RESPONSE_DICT[status]["status"]	
		else:
			self.__init__({}, 500)	

		self.accepted_renderer =  JSONRenderer()

		self.renderer_context = {}	
		self.accepted_media_type = content_type
					
		super().__init__(data=self.data, status=self.status, content_type=content_type)

