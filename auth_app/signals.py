from django.conf import settings
from qls.utils import loggerf, printf

def create_groups_permissions(sender, **kwargs):
	printf('Creating groups permissions for apps models in postgres.')
	try:
		from django.contrib.auth.models import Group, Permission
		from django.contrib.contenttypes.models import ContentType
		from auth_app.permissions import MODEL_PERMS
		for user_type in settings.USER_TYPE:
			for user_group in settings.USER_GROUP:
				group, created = Group.objects.get_or_create(name=f"{user_type}-{user_group}")
		for content_type in ContentType.objects.all():
			if MODEL_PERMS.get(content_type.model):
				for perms, groups in MODEL_PERMS.get(content_type.model).items():
					if groups:
						codename= f'{perms}_{content_type.model}'
						name 	= f'Can {perms} {content_type.name}'
						perm_obj, created = Permission.objects.get_or_create(content_type=content_type, codename=codename, name=name)
						for group in groups:
							group_qs = 	Group.objects.filter(name=group)
							if group_qs.exists():
								group_obj = group_qs.first()
								group_obj.permissions.add(perm_obj)
								printf(f'{group_obj.name} Can {perms} {content_type.model}')
	except Exception as e:
		import traceback
		loggerf('In create_groups_permissions() database Error:',e, traceback.format_exc())							

def populate_default_users(sender, **kwargs):
	from django.contrib.auth import get_user_model
	usertype_list 	= 	['qls', ]
	usergroup_list 	=	[('admin', 'staff', 'client'), ]
	email_list 		=	[('admin@gmail.com', 'staff@gmail.com', 'client@gmail.com'), ]
	name_list 		=	[('qls admin', 'qls staff', 'qls client'), ]
	for idx1, usertype in enumerate(usertype_list):
		if usertype in settings.USER_TYPE:
			for idx2, usergroup in enumerate(usergroup_list[idx1]):
				if usergroup in settings.USER_GROUP:
					email = email_list[idx1][idx2]
					username = f'{email}-{settings.USER_TYPE.index(usertype)}-{settings.USER_GROUP.index(usergroup)}'
					if get_user_model().objects.filter(username=username).exists():
						continue
					name = name_list[idx1][idx2]
					first_name = name.split(' ')[:-1] if len(name.split(' '))>1 else name.split(' ')[0]
					last_name = name.split(' ')[-1] if len(name.split(' '))>1 else ''
					get_user_model().objects.create_user(
							usergroup,
							username	=	username,
							email 		=	email,
							first_name 	= 	first_name,
							last_name 	= 	last_name,
							user_type 	= 	settings.USER_TYPE.index(usertype),
							tracking 	= 	False,
						)


def create_auth_token(sender, instance, created, **kwargs):
	if created==True:
		from rest_framework.authtoken.models import Token
		token 	= 	Token.objects.create(user=instance)
		loggerf(f'username: {instance.username}, token: {token.key}')


