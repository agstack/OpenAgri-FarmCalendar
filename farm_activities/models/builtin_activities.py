import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from django.conf import settings

from .base import FarmCalendarActivity, Observation, BaseParcelAreaObservation


class FertilizationOperation(FarmCalendarActivity):
    ACTIVITY_NAME = settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['fertilization']['name']
    class Meta:
        verbose_name = "Fertilization Operation"
        verbose_name_plural = "Fertilization Operations"

    # treated_area = models.IntegerField(blank=True, null=True)
    # fertilization_type = models.CharField(max_length=255, blank=True, null=True)
    applied_amount = models.DecimalField(max_digits=10, decimal_places=2)
    applied_amount_unit = models.CharField(max_length=255)

    application_method = models.CharField(max_length=255, blank=True, null=True)

    fertilizer = models.ForeignKey('farm_management.Fertilizer', on_delete=models.SET_NULL, blank=True, null=True)



class IrrigationOperation(FarmCalendarActivity):

    ACTIVITY_NAME = settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['irrigation']['name']

    class Meta:
        verbose_name = "Irrigation Operation"
        verbose_name_plural = "Irrigation Operations"

    class IrrigationSystemChoices(models.TextChoices):
        SPRINKLER = 'sprinkler', _('Sprinkler')
        DRIP = 'drip', _('Drip')
        CENTRE_PIVOT  = 'centre_pivot', _('Centre Pivot')
        FURROW  = 'furrow', _('Furrow')
        TERRACED  = 'terraced', _('Terraced')

    applied_amount = models.DecimalField(max_digits=10, decimal_places=2)
    applied_amount_unit = models.CharField(max_length=255)

    irrigation_system = models.CharField(max_length=50, choices=IrrigationSystemChoices.choices,
                                        default=IrrigationSystemChoices.SPRINKLER)

    # def save(self, *args, **kwargs):
    #     self.activity_type, _ = FarmCalendarActivityType.objects.get_or_create(name=settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['irrigation']['name'])
    #     super().save(*args, **kwargs)


class CropProtectionOperation(FarmCalendarActivity):
    ACTIVITY_NAME = settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['crop_protection']['name']

    class Meta:
        verbose_name = "Crop Protection Operation"
        verbose_name_plural = "Crop Protection Operations"

    applied_amount = models.DecimalField(max_digits=10, decimal_places=2)
    applied_amount_unit = models.CharField(max_length=255)

    pesticide = models.ForeignKey('farm_management.Pesticide', on_delete=models.SET_NULL, blank=True, null=True)


class CropStressIndicatorObservation(Observation):

    ACTIVITY_NAME = settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['crop_stress_indicator']['name']

    class Meta:
        verbose_name = "Crop Stress Indicator Observation"
        verbose_name_plural = "Crop Stress Indicator Observations"

    crop = models.ForeignKey('farm_management.FarmCrop', on_delete=models.CASCADE, blank=False, null=False)


class CropGrowthStageObservation(Observation):
    ACTIVITY_NAME = settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['crop_growth_stage']['name']

    class Meta:
        verbose_name = "Crop Growth Stage Observation"
        verbose_name_plural = "Crop Growth Stage Observations"

    crop = models.ForeignKey('farm_management.FarmCrop', on_delete=models.CASCADE, blank=False, null=False)


class YieldPredictionObservation(BaseParcelAreaObservation):
    ACTIVITY_NAME = settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['yield_prediction']['name']

    class Meta:
        verbose_name = "Yield Prediction Observation"
        verbose_name_plural = "Yield Prediction Observations"


class DiseaseDetectionObservation(BaseParcelAreaObservation):
    ACTIVITY_NAME = settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['disease_detection']['name']

    class Meta:
        verbose_name = "Disease Detection Observation"
        verbose_name_plural = "Disease Detection Observations"


class VigorEstimationObservation(BaseParcelAreaObservation):
    ACTIVITY_NAME = settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['vigor_estimation']['name']

    class Meta:
        verbose_name = "Vigor Estimation Observation"
        verbose_name_plural = "Vigor Estimation Observations"


class SprayingRecommendationObservation(BaseParcelAreaObservation):
    ACTIVITY_NAME = settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['spraying_recommendation']['name']

    class Meta:
        verbose_name = "Spraying Recommendation Observation"
        verbose_name_plural = "Spraying Recommendation Observations"

    pesticide = models.ForeignKey('farm_management.Pesticide', on_delete=models.SET_NULL, blank=True, null=True)


class CompostOperation(FarmCalendarActivity):
    ACTIVITY_NAME = settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['compost_operation']['name']

    class Meta:
        verbose_name = "Compost Operation"
        verbose_name_plural = "Compost Operations"

    compost_pile_id = models.CharField('Operated On Compost Pile', max_length=355)



class CompostTurningOperation(FarmCalendarActivity):
    ACTIVITY_NAME = settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['compost_turning_operation']['name']

    class Meta:
        verbose_name = "Compost Turning Operation"
        verbose_name_plural = "Compost Turning Operations"


class AddRawMaterialOperation(FarmCalendarActivity):
    ACTIVITY_NAME = settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['add_raw_material_operation']['name']

    class Meta:
        verbose_name = "Add Raw Material Operation"
        verbose_name_plural = "Add Raw Material Operations"


    compost_materials = models.ManyToManyField('farm_management.CompostMaterial', through='farm_activities.AddRawMaterialCompostQuantity')


class AddRawMaterialCompostQuantity(models.Model):
    class Meta:
        verbose_name = "Raw Material Quantity for Operation"
        verbose_name_plural = "Raw Material Quantities for Operation"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, db_index=True, editable=False, unique=True,
                          blank=False, null=False, verbose_name='ID')

    operation = models.ForeignKey(AddRawMaterialOperation, on_delete=models.CASCADE)
    material = models.ForeignKey('farm_management.CompostMaterial', on_delete=models.CASCADE)

    applied_amount = models.DecimalField(max_digits=10, decimal_places=2)
    applied_amount_unit = models.CharField(max_length=255)


class AnimalActivity(FarmCalendarActivity):
    ACTIVITY_NAME = settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['animal_activity']['name']

    class Meta:
        verbose_name = "Animal Activity"
        verbose_name_plural = "Animal Activities"

    animal = models.ForeignKey('farm_management.FarmAnimal', on_delete=models.SET_NULL, blank=True, null=True)

class AnimalLactatingActivity(AnimalActivity):
    ACTIVITY_NAME = settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['animal_lactating_activity']['name']

    days_in_milk = models.DecimalField(max_digits=10, decimal_places=2)
    lactation_number = models.DecimalField(max_digits=10, decimal_places=2)
    control = models.CharField(max_length=255)

    total_milk_yield_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_milk_yield_unit = models.CharField(max_length=255)

    milk_yield_amount = models.DecimalField(max_digits=10, decimal_places=2)
    milk_yield_unit = models.CharField(max_length=255)

    rcs_amount = models.DecimalField(max_digits=10, decimal_places=2)
    rcs_unit = models.CharField(max_length=255)

    urea_amount = models.DecimalField(max_digits=10, decimal_places=2)
    urea_unit = models.CharField(max_length=255)

    fat_amount = models.DecimalField(max_digits=10, decimal_places=2)
    fat_unit = models.CharField(max_length=255)

    protein_amount = models.DecimalField(max_digits=10, decimal_places=2)
    protein_unit = models.CharField(max_length=255)

    dry_matter_amount = models.DecimalField(max_digits=10, decimal_places=2)
    dry_matter_unit = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Animal Lactating Activity"
        verbose_name_plural = "Animal Lactating Activities"
