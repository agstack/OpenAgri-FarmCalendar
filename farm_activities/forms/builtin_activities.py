import json

from django.core.exceptions import ValidationError
from django import forms
from django.conf import settings
from django.forms import modelform_factory
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.urls import reverse

from dal import autocomplete


from ..models import (
    FarmCalendarActivityType,
    FarmCalendarActivity,
    Observation,
    CompostOperation,
    AddRawMaterialOperation,
    AddRawMaterialCompostQuantity,
    FertilizationOperation,
    IrrigationOperation,
    CropProtectionOperation,
    CropStressIndicatorObservation,
    CropGrowthStageObservation,
    CompostTurningOperation,
    YieldPredictionObservation,
    DiseaseDetectionObservation,
    VigorEstimationObservation,
    SprayingRecommendationObservation,
    AnimalActivity,
    AnimalLactatingActivity,
)
from farm_management.models import CompostMaterial

from .base import (
    FarmCalendarActivityForm,
    ObservationForm,
    NestedActivityForm,
    ParentActivityForm,
)
from .widgets import CompostMaterialsWidget


class FertilizationOperationForm(FarmCalendarActivityForm):
    class Meta(FarmCalendarActivityForm.Meta):
        model = FertilizationOperation


class CropProtectionOperationForm(FarmCalendarActivityForm):
    class Meta(FarmCalendarActivityForm.Meta):
        model = CropProtectionOperation


class CropStressIndicatorObservationForm(ObservationForm):
    class Meta(ObservationForm.Meta):
        model = CropStressIndicatorObservation


class CropGrowthStageObservationForm(ObservationForm):
    class Meta(ObservationForm.Meta):
        model = CropGrowthStageObservation


class YieldPredictionObservationForm(ObservationForm):
    class Meta(ObservationForm.Meta):
        model = YieldPredictionObservation


class DiseaseDetectionObservationForm(ObservationForm):
    class Meta(ObservationForm.Meta):
        model = DiseaseDetectionObservation


class VigorEstimationObservationForm(ObservationForm):
    class Meta(ObservationForm.Meta):
        model = VigorEstimationObservation


class SprayingRecommendationObservationForm(ObservationForm):
    class Meta(ObservationForm.Meta):
        model = SprayingRecommendationObservation


class CompostOperationForm(ParentActivityForm):
    class Meta(ParentActivityForm.Meta):
        model = CompostOperation


class IrrigationOperationForm(NestedActivityForm):
    class Meta(NestedActivityForm.Meta):
        model = IrrigationOperation


class CompostTurningOperationForm(NestedActivityForm):
    class Meta(NestedActivityForm.Meta):
        model = CompostTurningOperation

class AddRawMaterialOperationForm(NestedActivityForm):
    compost_materials_json = forms.JSONField(
        label='Compost Materials',
        required=False,  # Make this field optional if needed
        widget=CompostMaterialsWidget()
    )

    class Meta(NestedActivityForm.Meta):
        model = AddRawMaterialOperation
        exclude = ['compost_materials']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            initial_data = []
            compost_quantities = self.instance.compost_materials.through.objects.filter(operation=self.instance)

            for compost_quantity in compost_quantities:
                initial_data.append({
                    'material_name': compost_quantity.material.name,
                    'quantity': str(compost_quantity.applied_amount),
                    'unit': compost_quantity.applied_amount_unit,
                })
            self.initial['compost_materials_json'] = initial_data

    def clean_compost_materials_json(self):
        data = self.cleaned_data.get('compost_materials_json')
        if not isinstance(data, list):
            raise ValidationError("The data should be a list of materials with quantity and unit.")

        for item in data:
            if not isinstance(item, dict):
                raise ValidationError("Each item should be a dictionary.")
            if 'material_name' not in item or 'quantity' not in item or 'unit' not in item:
                raise ValidationError("Each dictionary must have 'material_name', 'quantity', and 'unit'.")

        return data

    def save(self, commit=True):
        instance = super().save(commit=True)

        # Now, handle the intermediary model based on the JSON data
        compost_materials_data = self.cleaned_data.get('compost_materials_json', [])

        # Clear existing relationships (if any)
        instance.compost_materials.clear()

        for item in compost_materials_data:
            # Create the intermediary model objects from the JSON data
            AddRawMaterialCompostQuantity.objects.create(
                operation=instance,
                material=CompostMaterial.objects.get_or_create(name=item['material_name'])[0],
                applied_amount=item['quantity'],
                applied_amount_unit=item['unit']
            )

        return instance


class AnimalActivityForm(ParentActivityForm):
    class Meta(ParentActivityForm.Meta):
        model = AnimalActivity

class AnimalLactatingActivityForm(ParentActivityForm):
    class Meta(ParentActivityForm.Meta):
        model = AnimalLactatingActivity
