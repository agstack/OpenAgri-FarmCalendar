from django.conf import settings

from ..models import FarmCalendarActivityType
from .base import *
from .builtin_activities import *


def get_generic_farm_calendar_activity_form(activity_type):
    activity_type_modelform_map = {
        settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['fertilization']['name']: FertilizationOperationForm,
        settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['irrigation']['name']: IrrigationOperationForm,
        settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['crop_protection']['name']: CropProtectionOperationForm,
        settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['crop_stress_indicator']['name']: CropStressIndicatorObservationForm,
        settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['crop_growth_stage']['name']: CropGrowthStageObservationForm,
        settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['yield_prediction']['name']: YieldPredictionObservationForm,
        settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['disease_detection']['name']: DiseaseDetectionObservationForm,
        settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['vigor_estimation']['name']: VigorEstimationObservationForm,
        settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['spraying_recommendation']['name']: SprayingRecommendationObservationForm,
        settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['compost_operation']['name']: CompostOperationForm,
        settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['add_raw_material_operation']['name']: AddRawMaterialOperationForm,
        settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['compost_turning_operation']['name']: CompostTurningOperationForm,
        settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['animal_activity']['name']: AnimalActivityForm,
        settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['animal_lactating_activity']['name']: AnimalLactatingActivityForm,
    }

    activity_type_instance = FarmCalendarActivityType.objects.filter(name=activity_type).first()
    if activity_type_instance is None:
        return None
    is_observation = activity_type_instance.category == FarmCalendarActivityType.ActivityCategoryChoices.OBSERVATION
    is_alert = activity_type_instance.category == FarmCalendarActivityType.ActivityCategoryChoices.ALERT

    ActivityModelForm = activity_type_modelform_map.get(activity_type)
    if ActivityModelForm is None:
        if is_observation:
            ActivityModelForm = ObservationForm
        elif is_alert:
            ActivityModelForm = AlertForm
        else:
            ActivityModelForm = FarmCalendarActivityForm

    return ActivityModelForm
