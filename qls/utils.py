from django.conf import settings
import os, re, datetime, logging, json
from django.utils.translation import gettext_lazy as _
from django.utils.functional import Promise
from django.utils.encoding import force_text
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.query import QuerySet

logger = logging.getLogger(__name__)

def printf(*args):
    if settings.PRINT_EANABLED==True:
        p = ''
        sep = ''
        for a in args:
            p += sep + str(a)
            sep = ' '
        print(p)

def loggerf(*args, **kwargs):
    p = ''
    sep = ''
    for a in args:
        p += sep + str(a)
        sep = ' '
    p = f'{datetime.datetime.now()}     :     {p}'
    if settings.PRINT_EANABLED==True:
        print(f'Logger : {p}')
        pass
    else:
        if kwargs.get('info')==True:
            logger.info(p)
        else:    
            logger.debug(p) 

class CustomServerException(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class CustomClientException(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)


class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(LazyEncoder, self).default(obj)


def full_data(request):
    data = {}
    try:
        data1 = getattr(request, 'GET').dict()
        if data1 is not None:
            data.update(data1)
    except:
        pass


    if hasattr(request, 'body')==True and request.body is not None and len(request.body)>0: 
        try:
            data1 = json.loads(request.body.decode('utf-8'))
            if data1 is not None: 
                data.update(data1)
        except:
            if request.method.lower()=="post" and hasattr(request, 'POST'):
                try:
                    data1 = getattr(request, 'POST').dict()
                    if data1 is not None:
                        data.update(data1)
                except:
                    pass 


    if hasattr(request, 'data')==True and request.data is not None and len(request.data)>0:  
        try:
            data.update(request.data)
        except:
            pass

    if hasattr(request, 'query_params')==True and request.query_params is not None and len(request.query_params)>0:
        try:
            data.update(request.query_params.dict())
        except:
            pass    
    setattr(request, 'full_data', data)
    return data 


def data_handler(qs, fields=[], func_fields={}, new_fields={},  idx=None, exception=Exception('Data not found'), *args, **kwargs):
    def data_formatting(obj, **kwargs):
        if kwargs.get('object', False)==True:
            return obj
        elif kwargs.get('json', False)==True:
            if type(obj)==QuerySet:
                obj = list(obj)
            return json.dumps(obj, cls=LazyEncoder)
        if type(obj)==QuerySet:
            obj = list(obj)
        return json.loads(json.dumps(obj, cls=LazyEncoder))


    if not qs.exists():
        raise exception   
    if len(fields)>0:
        qs = qs.values(*fields)
             
    if len(func_fields)>0 or len(new_fields)>0:
        for obj in qs:
            try:
                for field_name, new_field_dict in new_fields.items():
                    instance = new_field_dict.get('instance')
                    qs1  = instance(obj.get(field_name))
                    fields = new_field_dict.get('fields') 
                    for new_field, field_arr in fields.items():
                        if not qs1.exists():
                            obj[new_field] = None
                            continue
                        obj1 = qs1.first()
                        obj[new_field] = ""
                        for idx1, field2 in enumerate(field_arr):
                            try:
                                val = str(getattr(obj1, field2))
                                sep = (" " if val is not None and val!="" else "") if idx1<len(field_arr)-1 else ""
                                obj[new_field] += str(getattr(obj1, field2))  + sep
                            except Exception as e:
                                pass
            except Exception as e:
                loggerf("data_handler() Error1: ",e)

            for field, func in func_fields.items():
                try: 
                    obj[field] = func(obj.get(field), *args, **kwargs)
                except:
                    obj[field] = None
    if idx is not None:
        return data_formatting(qs[idx], **kwargs)
    return data_formatting(qs, **kwargs)

