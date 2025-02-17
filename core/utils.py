import boto3
from django.conf import settings
from botocore.exceptions import NoCredentialsError

BUKET_NAME = settings.AWS_STORAGE_BUCKET_NAME
AWS_REGION = settings.AWS_S3_REGION_NAME
AWS_KEY_ID = settings.AWS_ACCESS_KEY_ID
AWS_SECRET = settings.AWS_SECRET_ACCESS_KEY

s3_client = boto3.client('s3',
                         region_name=AWS_REGION,
                         aws_access_key_id=AWS_KEY_ID,
                         aws_secret_access_key=AWS_SECRET)


def generate_presigned_url(bucket_name, object_key, expiration=3600):
    try:
        url = s3_client.generate_presigned_url('get_object',
                                               Params={'Bucket': bucket_name,
                                                       'Key': object_key,
                                                       'ResponseContentDisposition': 'inline'
                                                       },
                                               ExpiresIn=expiration)
        return url
    except NoCredentialsError:
        return None


def age_check_middleware(get_response):
    from engine.models import Address
    from django.shortcuts import redirect
    from django.urls import resolve
    def middleware(request):
        cookie = request.COOKIES.get('confirmed_age', 'false')
        resolver_match = resolve(request.path)
        view_name = resolver_match.view_name
        exclude_path = ['admin:index', 'profile', 'login', 'logout', 'signup', 'social', 'index']
        admin_path = 'admin'
        if request.path.startswith(f'/{admin_path}/'):
            return get_response(request)
        if view_name in exclude_path:
            return get_response(request)
        if request.user.is_authenticated:
            try:
                address = Address.objects.get(user=request.user)
                if not address.confirmed_age:
                    if cookie == 'false':
                        return redirect('profile', username=request.user.username)
                    elif cookie == 'true':
                        address.confirmed_age = True
                        address.save()
                        return get_response(request)
                else:
                    response = get_response(request)
                    response.set_cookie('confirmed_age', 'true')
                    return response
            except Address.DoesNotExist:
                Address.objects.create(user=request.user)
                return get_response(request)
        response = get_response(request)
        return response

    return middleware
