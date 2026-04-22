import json
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from django.contrib.messages import constants as messages


 # Load environment variables from .env file
from decouple import config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_ROOT = str(BASE_DIR / "static")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('DJANGO_SECRET_KEY')


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


ALLOWED_HOSTS = ['.localhost', '127.0.0.1', '[::1]']

EXTRA_ALLOWED_HOSTS = config('EXTRA_ALLOWED_HOSTS', default=None)
if EXTRA_ALLOWED_HOSTS is not None:
    EXTRA_ALLOWED_HOSTS = EXTRA_ALLOWED_HOSTS.split(',')
    ALLOWED_HOSTS.extend(EXTRA_ALLOWED_HOSTS)

def default_crsf_from_allowed_host_format(host_list):
    crsf_host_format = []
    for host in host_list:
        if host.startswith('['):
            continue
        crsf_host = host
        if crsf_host.startswith('.'):
            crsf_host = f'*{crsf_host}'
        crsf_host_format.append(f'http://{crsf_host}')
        crsf_host_format.append(f'https://{crsf_host}')
    return ','.join(crsf_host_format)

CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', cast=Csv(), default=default_crsf_from_allowed_host_format(ALLOWED_HOSTS))

APP_PORT = config('APP_PORT', default='8002')

# Application definition
DEFAULT_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
]

LOCAL_APPS =[
    "farm_management.apps.FarmManagementConfig",
    "farm_activities.apps.FarmActivitiesConfig",
    "apis.apps.ApisConfig"
]

THIRD_PARTY_APPS = [
    'django_filters',
    'rest_framework',
    'simple_history',
    'drf_spectacular',
    'crispy_forms',
    'crispy_bootstrap4',
    'dal',
    'dal_select2',
]

INSTALLED_APPS = DEFAULT_APPS + LOCAL_APPS + THIRD_PARTY_APPS

GATEKEEPER_LOGIN_URL = config('GATEKEEPER_LOGIN_URL', default=None)
GATEKEEPER_LOGOUT_API_URL = config('GATEKEEPER_LOGOUT_API_URL', default=None)

if GATEKEEPER_LOGIN_URL == '':
    GATEKEEPER_LOGIN_URL = None
if GATEKEEPER_LOGOUT_API_URL == '':
    GATEKEEPER_LOGOUT_API_URL = None

INTERNAL_SERVICE_NAME = config('INTERNAL_SERVICE_NAME', default='farmcalendar')
INTERNAL_SERVICE_URL = config('INTERNAL_SERVICE_URL', default=f'http://{INTERNAL_SERVICE_NAME}:{APP_PORT}/')
GATEKEEPER_API_LOGIN_URL = None
GATEKEEPER_ENDPOINT_REG_URL = None
FARMCALENDAR_GATEKEEPER_USER = None
FARMCALENDAR_GATEKEEPER_PASSWORD = None
if GATEKEEPER_LOGIN_URL is not None:
    GATEKEEPER_API_LOGIN_URL = config('GATEKEEPER_API_LOGIN_URL')
    GATEKEEPER_ENDPOINT_REG_URL = config('GATEKEEPER_ENDPOINT_REG_URL')

    FARMCALENDAR_GATEKEEPER_USER = config('FARMCALENDAR_GATEKEEPER_USER')
    FARMCALENDAR_GATEKEEPER_PASSWORD = config('FARMCALENDAR_GATEKEEPER_PASSWORD')

none_if_empty_cast = lambda x: None if x == '' else x
AGSTACK_ASSET_REGISTY_API_URL = config('AGSTACK_ASSET_REGISTY_API_URL', default=None, cast=none_if_empty_cast)

AGSTACK_CLIENT_SECRET = None
AGSTACK_API_KEY = None
if AGSTACK_ASSET_REGISTY_API_URL is not None:
    AGSTACK_CLIENT_SECRET = config('AGSTACK_CLIENT_SECRET')
    AGSTACK_API_KEY = config('AGSTACK_API_KEY')
    AGSTACK_ENDPOINTS = {
        'register_field_boundary': config('AGSTACK_ENDPOINT_REGISTER_FIELD_BOUNDARY', default='/register-field-boundary'),
    }



REPORTING_API_ROOT = config('REPORTING_API_ROOT', default='http://localhost:8011/api/v1/')
DISABLE_REPORTING = config('DISABLE_REPORTING', default=False, cast=bool)
if not DISABLE_REPORTING :
    REPORTING_ENDPOINTS = {
        'irrigation': f'{REPORTING_API_ROOT}openagri-report/irrigation-report/',
        'composting': f'{REPORTING_API_ROOT}openagri-report/compost-report/',
        'livestock': f'{REPORTING_API_ROOT}openagri-report/animal-report/',
        'report_result_base': f'{REPORTING_API_ROOT}openagri-report/',
    }


AUTHENTICATION_BACKENDS = (
    'farm_calendar.utils.auth_backends.CustomJWTAuthenticationBackend',
)
if GATEKEEPER_LOGIN_URL is None:
    AUTHENTICATION_BACKENDS = AUTHENTICATION_BACKENDS + ('django.contrib.auth.backends.ModelBackend',)




CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"

CRISPY_TEMPLATE_PACK = "bootstrap4"

# AUTH_USER_MODEL = "harvesthand.DefaultAuthUserExtend"

# https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url
LOGIN_REDIRECT_URL = "calendar"

# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = "login"


JWT_USER_ID_FIELD = 'user_id'
JWT_ALG = 'HS256'

# for HMAC this is the same as the verifying key
JWT_SIGNING_KEY = config('JWT_SIGNING_KEY')
JWT_COOKIE_NAME = config('JWT_COOKIE_NAME')
JWT_LOCAL_USER_ID_FIELD = config('JWT_LOCAL_USER_ID_FIELD', default='username')
AUTO_CREATE_AUTH_USER = config('AUTO_CREATE_AUTH_USER', default=True, cast=bool)
POST_AUTH_TOKEN_ATTRIBUTE = config('POST_AUTH_TOKEN_ATTRIBUTE', default='access_token')

#lets igore RSA-based signing for now...
# with open(str(BASE_DIR / 'public.pem'), 'r') as f:
#     JWT_PUBLIC_KEY = f.read()
# with open(str(BASE_DIR / 'private.pem'), 'r') as f:
#     JWT_PRIVATE_KEY = f.read()

DEFAULT_API_VERSION = config('DEFAULT_API_VERSION', default='1.0.0')
SHORT_API_VERSION = f'v{DEFAULT_API_VERSION.split(".")[0]}'

API_SCHEMA_FILE_PATH = BASE_DIR / 'schema.yml'

REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': SHORT_API_VERSION,
    'ALLOWED_VERSIONS': ['v1',],
    'VERSION_PARAM': 'version',
    'DEFAULT_PAGINATION_CLASS': None,
    # 'PAGE_SIZE': 99999999,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

    'DEFAULT_RENDERER_CLASSES': [
        'apis.renderers.JSONLDRenderer',
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    # 'DEFAULT_PARSER_CLASSES': [
    #     'apis.parsers.JSONLDParser',
    #     'rest_framework.parsers.JSONParser',
    #     'rest_framework.parsers.FormParser',
    #     'rest_framework.parsers.MultiPartParser',
    # ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'farm_calendar.utils.auth_backends.CustomJWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],

}

SPECTACULAR_SETTINGS = {
    'TITLE': 'OpenAgri Farm Calendar API',
    'DESCRIPTION': 'API for farm assets and other farm related things.',
    'VERSION': DEFAULT_API_VERSION,
    'SERVE_INCLUDE_SCHEMA': True,
}



DEFAULT_OCSM_JSONLD_CONTEXT_FILE = (
    BASE_DIR / 'apis' / 'default_ocsm_context'
        / 'v0' / 'ocsm-profile-context.jsonld'
)

OCSM_JSONLD_CONTEXT_FILE = config('OCSM_JSONLD_CONTEXT_FILE', default=DEFAULT_OCSM_JSONLD_CONTEXT_FILE)

# with open(OCSM_JSONLD_CONTEXT_FILE, 'r') as f:
#     OCSM_JSONLD_CONTEXT = json.load(f)

# leave like this for now, it keeps response small and I dont really have
# full knowledge what I can add/remove from the full context
OCSM_JSONLD_CONTEXT  = {
  	"@context": [
	  	"https://w3id.org/ocsm/main-context.jsonld"
   	]
}

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'farm_calendar.utils.auth_middlewares.JWTAuthenticationMiddleware',
]


ROOT_URLCONF = 'farm_calendar.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.static',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'farm_calendar.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB'),
        'USER': config('POSTGRES_USER'),
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': config('POSTGRES_HOST'),
        'PORT': config('POSTGRES_PORT', default=5432, cast=int),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# MESSAGE_TAGS setting maps Django's built-in message levels to CSS classes used by the front-end framework
# (e.g., Bootstrap).
# This allows messages from Django's messaging framework to be styled appropriately in the web interface.
MESSAGE_TAGS = {
    messages.DEBUG: "alert-info",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'
# TIME_ZONE = 'Europe/Amsterdam'

USE_L10N = True
USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = str(BASE_DIR / "static_root")

STATICFILES_DIRS = [str(BASE_DIR / "static")]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

FIXTURE_DIRS = [(BASE_DIR / "fixtures")]



DEFAULT_CALENDAR_ACTIVITY_TYPES = {
    'fertilization': {
        'name': 'Fertilization',
        'description': 'Fertilization operation',
        "background_color": "#F5E8C7",
        "border_color": "#8B4513",
        "text_color": "#2F4F4F",
        'category': 'activity',
        "id": "00000000-0000-0000-0000-000000000001",
        'built_in_class': 'farm_activities.FertilizationOperation',
    },
    'irrigation': {
        'name': 'Irrigation',
        'description': 'Irrigation operation',
        'background_color': '#B3E5FC',
        'border_color': '#0288D1',
        'text_color': '#01579B',
        'category': 'activity',
        "id": "00000000-0000-0000-0000-000000000002",
        'built_in_class': 'farm_activities.IrrigationOperation',
    },
    'crop_protection':{
        'name': 'Pesticides',
        'description': 'Pesticide application',
        'background_color': '#C5E1A5',
        'border_color': '#8E7F2F',
        'text_color': '#4E342E',
        'category': 'activity',
        "id": "00000000-0000-0000-0000-000000000003",
        'built_in_class': 'farm_activities.CropProtectionOperation',
    },
    'crop_stress_indicator':{
        'name': 'Crop Stress Indicator',
        'description': 'Crop Stress Indicator Observation',
        'background_color': '#FFCCCB',
        'border_color': '#C62828',
        'text_color': '#BF360C',
        'category': 'observation',
        "id": "00000000-0000-0000-0000-000000000004",
        'built_in_class': 'farm_activities.CropStressIndicatorObservation',
    },
    'crop_growth_stage':{
        'name': 'Crop Growth Stage Observation',
        'description': 'Crop Stress Indicator Observation',
        "background_color": "#F5E8C7",
        "border_color": "#8B4513",
        "text_color": "#2F4F4F",
        'category': 'observation',
        "id": "00000000-0000-0000-0000-000000000005",
        'built_in_class': 'farm_activities.CropGrowthStageObservation',
    },
    'compost_operation':{
        'name': 'Compost Operation',
        'description': 'Compost Operation',
        'background_color': '#A3C585',
        'border_color': '#6B4226',
        'text_color': '#3E4A34',
        'category': 'activity',
        'id': '00000000-0000-0000-0000-000000000006',
        'built_in_class': 'farm_activities.CompostOperation',
    },
    'add_raw_material_operation':{
        'name': 'Add Raw Material Operation',
        'description': 'Add Raw Material Operation',
        'background_color': '#D9E58A',
        'border_color': '#8A5A2B',
        'text_color': '#4A5320',
        'category': 'activity',
        'id': '00000000-0000-0000-0000-000000000007',
        'built_in_class': 'farm_activities.AddRawMaterialOperation',
    },
    'compost_turning_operation': {
        'name': 'Compost Turning Operation',
        'description': 'Compost Turning Operation',
        'background_color': '#BFD982',
        'border_color': '#72512D',
        'text_color': '#3C4F2E',
        'category': 'activity',
        'id': '00000000-0000-0000-0000-000000000008',
        'built_in_class': 'farm_activities.CompostTurningOperation',
    },
    'yield_prediction': {
        'name': 'Yield Prediction Observation',
        'description': 'Yield Prediction',
        'background_color': '#E6F3C3',
        'border_color': '#5A7247',
        'text_color': '#2A3B1E',
        'category': 'observation',
        'id': '00000000-0000-0000-0000-000000000009',
        'built_in_class': 'farm_activities.YieldPredictionObservation',
    },
    'disease_detection': {
        'name': 'Disease Detection Observation',
        'description': 'Disease Detection',
        'background_color': '#F3C3C3',
        'border_color': '#72475A',
        'text_color': '#3B1E2A',
        'category': 'observation',
        'id': '00000000-0000-0000-0000-000000000010',
        'built_in_class': 'farm_activities.DiseaseDetectionObservation',
    },
    'vigor_estimation': {
        'name': 'Vigor Estimation Observation',
        'description': 'Vigor Estimation',
        'background_color': '#C3E6F3',
        'border_color': '#475A72',
        'text_color': '#1E2A3B',
        'category': 'observation',
        'id': '00000000-0000-0000-0000-000000000011',
        'built_in_class': 'farm_activities.VigorEstimationObservation',
    },
    'spraying_recommendation': {
        'name': 'Spraying Recommendation Observation',
        'description': 'Spraying Recommendation',
        'background_color': '#F3E6C3',
        'border_color': '#725A47',
        'text_color': '#3B2A1E',
        'category': 'observation',
        'id': '00000000-0000-0000-0000-000000000012',
        'built_in_class': 'farm_activities.SprayingRecommendationObservation',
    },
    'animal_activity': {
        'name': 'Animal Activity',
        'description': 'Animal Activity',
        'background_color': "#C8AF6A",
        'border_color': "#725A33",
        'text_color': '#3B2A1E',
        'category': 'activity',
        'id': '00000000-0000-0000-0000-000000000013',
        'built_in_class': 'farm_activities.AnimalActivity',
    },
    'animal_lactating_activity': {
        'name': 'Animal Lactating Activity',
        'description': 'Animal Lactating Activity',
        'background_color': "#F9ECC6",
        'border_color': "#335872",
        'text_color': "#101B37",
        'category': 'activity',
        'id': '00000000-0000-0000-0000-000000000014',
        'built_in_class': 'farm_activities.AnimalLactatingActivity',
    }
}
