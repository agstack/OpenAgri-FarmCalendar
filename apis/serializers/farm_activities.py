import uuid

from django.conf import settings
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from rest_framework import serializers

from farm_management.models import (
    Fertilizer,
    Pesticide,
    CompostMaterial,
    FarmParcel,
    FarmCrop,
    FarmAnimal,
    AgriculturalMachine
)

from farm_activities.models import (
    FarmCalendarActivityType,
    FarmCalendarActivity,
    Alert,
    FertilizationOperation,
    IrrigationOperation,
    CropProtectionOperation,Observation,
    CropStressIndicatorObservation,
    CropGrowthStageObservation,
    YieldPredictionObservation,
    DiseaseDetectionObservation,
    VigorEstimationObservation,
    SprayingRecommendationObservation,
    CompostOperation,
    AddRawMaterialOperation,
    AddRawMaterialCompostQuantity,
    CompostTurningOperation,
    AnimalActivity,
    AnimalLactatingActivity,
)

from .base import URNRelatedField, URNCharField
from ..schemas import generate_urn


def quantity_value_serializer_factory(unit_field, value_field):

    class GenericQuantityValueFieldSerializer(serializers.Serializer):
        unit = serializers.CharField(source=unit_field, allow_null=True, required=False)
        hasValue = serializers.CharField(source=value_field)


        def to_representation(self, instance):
            value = getattr(instance, value_field)
            unit = getattr(instance, unit_field)
            uuid_orig_str = "".join([
                str(getattr(instance, unit_field, '')),
                str(getattr(instance, value_field, ''),)
            ])
            hash_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, uuid_orig_str))
            return {
                '@id': generate_urn('QuantityValue',obj_id=hash_uuid),
                '@type': 'QuantityValue',
                'unit': unit,
                'hasValue': value,
            }
    return GenericQuantityValueFieldSerializer


def observation_ref_quantity_value_serializer_factory(unit_field, value_field):

    class ObservationQuantityValueFieldSerializer(serializers.Serializer):
        unit = serializers.CharField(allow_null=True, read_only=True, required=False)
        hasValue = serializers.CharField(allow_null=True, read_only=True, required=False)


        def to_representation(self, instance):
            instanced_observation = None
            try:
                instanced_observation = instance.observation
            except Observation.DoesNotExist:
                return {}

            value = getattr(instanced_observation, value_field)
            unit = getattr(instanced_observation, unit_field)
            uuid_orig_str = "".join([
                str(getattr(instanced_observation, unit_field, '')),
                str(getattr(instanced_observation, value_field, ''),)
            ])
            hash_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, uuid_orig_str))
            return {
                '@id': generate_urn('QuantityValue',obj_id=hash_uuid),
                '@type': 'QuantityValue',
                'unit': unit,
                'hasValue': value,
            }
    return ObservationQuantityValueFieldSerializer


class FarmCalendarActivitySerializer(serializers.ModelSerializer):
    activityType = URNRelatedField(class_names=['FarmCalendarActivityType'], source='activity_type', queryset=FarmCalendarActivityType.objects.all())
    hasStartDatetime = serializers.DateTimeField(source='start_datetime')
    hasEndDatetime = serializers.DateTimeField(source='end_datetime', allow_null=True, required=False)

    responsibleAgent = serializers.CharField(source='responsible_agent', allow_null=True, required=False)

    usesAgriculturalMachinery = URNRelatedField(class_names=['AgriculturalMachine'], source='agricultural_machinery', many=True, queryset=AgriculturalMachine.objects.all())

    hasAgriParcel = URNRelatedField(
        source='parcel',
        class_names=['Parcel'],
        queryset=FarmParcel.objects.all(),
        allow_null=True, required=False
    )

    isPartOfActivity = URNRelatedField(
        class_names=['FarmCalendarActivity'],
        queryset=FarmCalendarActivity.objects.all(),
        source='parent_activity',
        allow_null=True,
        required=False
    )

    class Meta:
        model = FarmCalendarActivity
        fields = [
            'id',
            'activityType', 'title', 'details',
            'hasStartDatetime', 'hasEndDatetime',
            'hasAgriParcel',
            'responsibleAgent', 'usesAgriculturalMachinery',
            'isPartOfActivity'
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        json_ld_representation = {
            '@type': 'FarmCalendarActivity',
            '@id': generate_urn(instance.__class__.__name__, obj_id=representation.pop('id')),
            **representation
        }

        return json_ld_representation


class FarmCalendarActivityTypeSerializer(serializers.ModelSerializer):
    activity_endpoint = serializers.SerializerMethodField(
        allow_null=True, required=False,
        read_only=True,
        help_text="The farm activitie API endpoint with the specific details of this activity type."
    )

    class Meta:
        model = FarmCalendarActivityType

        fields = [
            'id',
            'name', 'description', 'category',
            'background_color', 'border_color', 'text_color',
            'activity_endpoint',
        ]

    def _get_reverse_for_built_in_activity(self, obj):
        for key, val in settings.DEFAULT_CALENDAR_ACTIVITY_TYPES.items():
            if str(obj.pk) == str(val['id']):
                built_in_class = val.get('built_in_class')
                app_label, model_name = built_in_class.split('.')
                built_in_model = apps.get_model(app_label=app_label, model_name=model_name)
                model_name = built_in_model._meta.model_name
                return reverse(f'{model_name}-list', args=[settings.SHORT_API_VERSION])
        return None

    def get_activity_endpoint(self, obj):
        built_in_reverse = self._get_reverse_for_built_in_activity(obj)
        if built_in_reverse:
            return built_in_reverse

        if obj.category == FarmCalendarActivityType.ActivityCategoryChoices.ACTIVITY:
            return reverse('farmcalendaractivity-list', args=[settings.SHORT_API_VERSION])
        elif obj.category == FarmCalendarActivityType.ActivityCategoryChoices.OBSERVATION:
            return reverse('observation-list', args=[settings.SHORT_API_VERSION])
        elif obj.category == FarmCalendarActivityType.ActivityCategoryChoices.ALERT:
            return reverse('alert-list', args=[settings.SHORT_API_VERSION])

        return reverse('farmcalendaractivity-list', args=[settings.SHORT_API_VERSION])

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        json_ld_representation = {
            '@type': 'FarmActivityType',
            '@id': generate_urn('FarmActivityType', obj_id=representation.pop('id')),
            **representation
        }

        return json_ld_representation


class AppliedAmmountFieldSerializer(serializers.Serializer):
    unit = serializers.CharField(source='applied_amount_unit')
    numericValue = serializers.DecimalField(source='applied_amount', max_digits=17, decimal_places=2)


    def to_representation(self, instance):
        uuid_orig_str = "".join([
            str(getattr(instance, 'applied_amount_unit', '')),
            str(getattr(instance, 'applied_amount', ''),)
        ])
        hash_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, uuid_orig_str))
        return {
            '@id': generate_urn('QuantityValue',obj_id=hash_uuid),
            '@type': 'QuantityValue',
            'unit': instance.applied_amount_unit,
            'numericValue': instance.applied_amount,
        }

class GenericOperationSerializer(FarmCalendarActivitySerializer):
    hasAppliedAmount = AppliedAmmountFieldSerializer(source='*')

    operatedOn = URNRelatedField(
        class_names=['Parcel'],
        queryset=FarmParcel.objects.all(),
        source='parcel'
    )

class FertilizationOperationSerializer(GenericOperationSerializer):
    usesFertilizer = URNRelatedField(
        class_names=['Fertilizer'],
        queryset=Fertilizer.objects.all(),
        source='fertilizer',
        allow_null=True
    )
    hasApplicationMethod = serializers.CharField(source='application_method', allow_null=True)
    class Meta:
        model = FertilizationOperation

        fields = [
            'id',
            'activityType', 'title', 'details',
            'hasStartDatetime', 'hasEndDatetime',
            'responsibleAgent', 'usesAgriculturalMachinery',
            'hasAppliedAmount', 'hasApplicationMethod',
            'usesFertilizer', 'operatedOn',
            'isPartOfActivity',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update({'@type': 'FertilizationOperation'})
        json_ld_representation = representation

        return json_ld_representation


class IrrigationOperationSerializer(GenericOperationSerializer):
    usesIrrigationSystem = serializers.ChoiceField(
        choices=IrrigationOperation.IrrigationSystemChoices.choices,
        source='irrigation_system'
    )

    class Meta:
        model = IrrigationOperation

        fields = [
            'id',
            'activityType', 'title', 'details',
            'hasStartDatetime', 'hasEndDatetime',
            'responsibleAgent', 'usesAgriculturalMachinery',
            'hasAppliedAmount',
            'usesIrrigationSystem', 'operatedOn',
            'isPartOfActivity',
        ]


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update({'@type': 'IrrigationOperation'})
        json_ld_representation = representation

        return json_ld_representation


    def create(self, validated_data):
        if self.context['view'].kwargs.get('compost_operation_pk'):
            validated_data['parent_activity'] = CompostOperation.objects.get(pk=self.context['view'].kwargs.get('compost_operation_pk'))

        return super().create(validated_data)


class CropProtectionOperationSerializer(GenericOperationSerializer):
    usesPesticide = URNRelatedField(
        class_names=['Pesticide'],
        queryset=Pesticide.objects.all(),
        source='pesticide',
        allow_null=True
    )
    class Meta:
        model = CropProtectionOperation
        fields = [
            'id',
            'activityType', 'title', 'details',
            'hasStartDatetime', 'hasEndDatetime',
            'responsibleAgent', 'usesAgriculturalMachinery',
            'hasAppliedAmount',
            'usesPesticide', 'operatedOn',
            'isPartOfActivity',
        ]


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update({'@type': 'CropProtectionOperation'})
        json_ld_representation = representation

        return json_ld_representation


class MadeBySensorFieldSerializer(serializers.Serializer):
    name = serializers.CharField(source='sensor_id', allow_null=True)

    def to_representation(self, instance):
        uuid_orig_str = getattr(instance, 'sensor_id', '')
        if uuid_orig_str is None or uuid_orig_str == '':
            return {}
        hash_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, uuid_orig_str))
        return {
            '@id': generate_urn('Sensor',obj_id=hash_uuid),
            '@type': 'Sensor',
            'name': instance.sensor_id,
        }

class ObservationSerializer(FarmCalendarActivitySerializer):
    phenomenonTime = serializers.DateTimeField(source='start_datetime')
    observedProperty = serializers.CharField(source='observed_property')
    hasResult = quantity_value_serializer_factory('value_unit', 'value')(source='*')
    madeBySensor = MadeBySensorFieldSerializer(source='*', allow_null=True, required=False)

    class Meta:
        model = Observation
        fields = [
            'id',
            'activityType',
            'title', 'details',
            'phenomenonTime',
            'hasEndDatetime',
            'hasAgriParcel',
            'madeBySensor',
            # 'responsibleAgent', 'usesAgriculturalMachinery',
            'hasResult',
            'observedProperty',
            'isPartOfActivity',
        ]


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update({'@type': 'Observation'})
        json_ld_representation = representation

        return json_ld_representation


    def create(self, validated_data):
        if self.context['view'].kwargs.get('compost_operation_pk'):
            validated_data['parent_activity'] = CompostOperation.objects.get(pk=self.context['view'].kwargs.get('compost_operation_pk'))

        return super().create(validated_data)



class AlertSerializer(FarmCalendarActivitySerializer):
    validFrom = serializers.DateTimeField(source='start_datetime')
    validTo = serializers.DateTimeField(source='end_datetime')
    dateIssued = serializers.DateTimeField(source='parent_activity.start_datetime', allow_null=True, read_only=True, required=False)
    isPartOfActivity = None
    relatedObservation = URNRelatedField(
        class_names=['Observation'],
        queryset=Observation.objects.all(),
        source='parent_activity',
        allow_null=True
    )
    quantityValue = observation_ref_quantity_value_serializer_factory('value_unit', 'value')(source='parent_activity', required=False)

    class Meta:
        model = Alert
        fields = [
            'id',
            'activityType',
            'title', 'details',
            'severity',
            'hasAgriParcel',
            'validFrom',
            'validTo',
            'dateIssued',
            'quantityValue',
            'relatedObservation',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update({'@type': 'Alert'})
        json_ld_representation = representation
        return json_ld_representation


class CropStressIndicatorObservationSerializer(ObservationSerializer):
    hasAgriCrop = URNRelatedField(
        class_names=['FarmCrop'],
        queryset=FarmCrop.objects.all(),
        source='crop'
    )
    class Meta:
        model = CropStressIndicatorObservation
        fields = [
            'id',
            'activityType', 'title', 'details',
            'phenomenonTime',
            'hasEndDatetime',
            'madeBySensor',
            'hasAgriParcel',
            # 'responsibleAgent', 'usesAgriculturalMachinery',
            'hasAgriCrop',
            'hasResult',
            'observedProperty',
            'isPartOfActivity',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update({'@type': 'CropStressIndicatorObservation'})
        json_ld_representation = representation

        return json_ld_representation


class CropGrowthStageObservationSerializer(ObservationSerializer):
    hasAgriCrop = URNRelatedField(
        class_names=['FarmCrop'],
        queryset=FarmCrop.objects.all(),
        source='crop'
    )
    class Meta:
        model = CropGrowthStageObservation
        fields = [
            'id',
            'activityType', 'title', 'details',
            'phenomenonTime',
            'hasEndDatetime',
            'madeBySensor',
            # 'responsibleAgent', 'usesAgriculturalMachinery',
            'hasAgriParcel',
            'hasAgriCrop',
            'hasResult',
            'observedProperty',
            'isPartOfActivity',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update({'@type': 'CropGrowthStageObservation'})
        json_ld_representation = representation

        return json_ld_representation



class BaseParcelAreaObservationSerializer(ObservationSerializer):
    hasArea = serializers.DecimalField(source='area', max_digits=15, decimal_places=2)

    class Meta:
        fields = [
            'id',
            'activityType', 'title', 'details',
            'phenomenonTime',
            'hasEndDatetime',
            'madeBySensor',
            'hasAgriParcel',
            'hasArea',
            'hasResult',
            'observedProperty',
            'isPartOfActivity',
        ]


class YieldPredictionObservationSerializer(BaseParcelAreaObservationSerializer):
    class Meta(BaseParcelAreaObservationSerializer.Meta):
        model = YieldPredictionObservation

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update({'@type': 'YieldPrediction'})
        json_ld_representation = representation

        return json_ld_representation


class DiseaseDetectionObservationSerializer(BaseParcelAreaObservationSerializer):
    class Meta(BaseParcelAreaObservationSerializer.Meta):
        model = DiseaseDetectionObservation

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update({'@type': 'DiseaseDetection'})
        json_ld_representation = representation

        return json_ld_representation


class VigorEstimationObservationSerializer(BaseParcelAreaObservationSerializer):
    class Meta(BaseParcelAreaObservationSerializer.Meta):
        model = VigorEstimationObservation

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update({'@type': 'VigorEstimation'})
        json_ld_representation = representation

        return json_ld_representation


class SprayingRecommendationObservationSerializer(BaseParcelAreaObservationSerializer):
    usesPesticide = URNRelatedField(
        class_names=['Pesticide'],
        queryset=Pesticide.objects.all(),
        source='pesticide',
        allow_null=True
    )
    class Meta(BaseParcelAreaObservationSerializer.Meta):
        model = SprayingRecommendationObservation
        fields = BaseParcelAreaObservationSerializer.Meta.fields + ['usesPesticide']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update({'@type': 'SprayingRecommendation'})
        json_ld_representation = representation

        return json_ld_representation


class AddRawMaterialCompostQuantitySerializer(serializers.ModelSerializer):
    quantityValue = AppliedAmmountFieldSerializer(source='*')
    typeName = serializers.CharField(source='material.name')

    class Meta:
        model = AddRawMaterialCompostQuantity
        fields = [
            'id',
            'typeName',
            'quantityValue',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        json_ld_representation = {
            '@type': 'CompostMaterial',
            '@id': generate_urn('CompostMaterial', obj_id=representation.pop('id')),
            **representation
        }
        return json_ld_representation


class AddRawMaterialOperationSerializer(GenericOperationSerializer):
    hasCompostMaterial = AddRawMaterialCompostQuantitySerializer(source='addrawmaterialcompostquantity_set', many=True)

    class Meta:
        model = AddRawMaterialOperation

        fields = [
            'id',
            'activityType', 'title', 'details',
            'hasStartDatetime', 'hasEndDatetime',
            'operatedOn',
            'responsibleAgent', 'usesAgriculturalMachinery',
            'hasCompostMaterial',
            'isPartOfActivity',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update({'@type': 'AddRawMaterialOperation'})
        json_ld_representation = representation

        return json_ld_representation



    def create(self, validated_data):
        if self.context['view'].kwargs.get('compost_operation_pk'):
            validated_data['parent_activity'] = CompostOperation.objects.get(pk=self.context['view'].kwargs.get('compost_operation_pk'))

        compost_data = validated_data.pop('addrawmaterialcompostquantity_set', [])
        operation = super().create(validated_data)

        for compost in compost_data:
            material = CompostMaterial.objects.get_or_create(name=compost.pop('material')['name'])[0]
            AddRawMaterialCompostQuantity.objects.create(operation=operation, material=material, **compost)

        return operation

    def update(self, instance, validated_data):
        compost_data = validated_data.pop('addrawmaterialcompostquantity_set', [])
        instance = super().update(instance, validated_data)

        instance.addrawmaterialcompostquantity_set.all().delete()
        for compost in compost_data:
            material = CompostMaterial.objects.get_or_create(name=compost.pop('material')['name'])[0]

            AddRawMaterialCompostQuantity.objects.create(operation=instance, material=material, **compost)

        return instance


class CompostTurningOperationSerializer(GenericOperationSerializer):

    class Meta:
        model = CompostTurningOperation

        fields = [
            'id',
            'activityType', 'title', 'details',
            'hasStartDatetime', 'hasEndDatetime',
            'operatedOn',
            'responsibleAgent', 'usesAgriculturalMachinery',
            'isPartOfActivity',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update({'@type': 'CompostTurningOperation'})
        json_ld_representation = representation

        return json_ld_representation

    def create(self, validated_data):
        if self.context['view'].kwargs.get('compost_operation_pk'):
            validated_data['parent_activity'] = CompostOperation.objects.get(pk=self.context['view'].kwargs.get('compost_operation_pk'))

        return super().create(validated_data)


class CompostPileFieldSerializer(serializers.Serializer):
    # pile_id = serializers.CharField(source='compost_pile_id')

    def to_representation(self, instance):
        return {
            '@id': generate_urn('CompostPile',obj_id=instance),
            '@type': 'CompostPile',
        }
    def to_internal_value(self, data):
        return data['']


class CompostOperationSerializer(FarmCalendarActivitySerializer):
    AllOWED_NESTED_OPERATIONS = [
        settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['irrigation']['name'],
        settings.DEFAULT_CALENDAR_ACTIVITY_TYPES['add_raw_material_operation']['name']
    ]

    hasNestedOperation = URNRelatedField(
        class_names=None, source='nested_activities', many=True,
        read_only=True
    )

    hasMeasurement = URNRelatedField(
        class_names=None, source='nested_activities', many=True,
        read_only=True
    )

    # isOperatedOn = serializers.CharField(source='compost_pile_id')
    # isOperatedOn = CompostPileFieldSerializer(source='compost_pile_id')
    isOperatedOn = URNCharField(
        class_names=['CompostPile'], source='compost_pile_id', read_only=False
    )
    class Meta:
        model = CompostOperation

        fields = [
            'id',
            'activityType', 'title', 'details',
            'hasStartDatetime', 'hasEndDatetime',
            'responsibleAgent', 'usesAgriculturalMachinery',
            'hasAgriParcel',
            'isOperatedOn',
            'hasNestedOperation', 'hasMeasurement',
            'isPartOfActivity',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update({'@type': 'CompostOperation'})
        json_ld_representation = representation
        clean_nested_activities = []
        clean_nested_obs = []
        json_and_instances_list = zip(
            json_ld_representation['hasNestedOperation'],
            instance.nested_activities.all()
        )
        for json_activity, nested_activity in json_and_instances_list:
            class_name = 'Observation'
            for field in ['addrawmaterialoperation', 'irrigationoperation', 'compostturningoperation']:
                try:
                    class_name = getattr(nested_activity, field).__class__.__name__
                    break
                except ObjectDoesNotExist as e:
                    continue

            fixed_id = json_activity['@id'].format(class_name=class_name)
            fixed_type = json_activity['@type'].format(class_name=class_name)
            json_activity['@id'] = fixed_id
            json_activity['@type'] = fixed_type
            if class_name == 'Observation':
                clean_nested_obs.append(json_activity)
            else:
                clean_nested_activities.append(json_activity)

        json_ld_representation['hasNestedOperation'] = clean_nested_activities
        json_ld_representation['hasMeasurement'] = clean_nested_obs
        return json_ld_representation


class AnimalActivitySerializer(FarmCalendarActivitySerializer):

    hasAnimal = URNRelatedField(
        class_names=['FarmAnimal'],
        queryset=FarmAnimal.objects.all(),
        source='animal',
        allow_null=True
    )

    class Meta:
        model = AnimalActivity
        fields = [
            'id',
            'activityType', 'title', 'details',
            'hasStartDatetime', 'hasEndDatetime',
            'hasAgriParcel',
            'hasAnimal',
            'responsibleAgent', 'usesAgriculturalMachinery',
            'isPartOfActivity','hasMeasurement',
        ]


    hasMeasurement = URNRelatedField(
        class_names=['Observation'], source='nested_activities', many=True,
        read_only=True
    )



class AnimalLactatingActivitySerializer(AnimalActivitySerializer):

    hasDaysInMilk = serializers.CharField(source='days_in_milk')
    hasLactationNumber = serializers.CharField(source='lactation_number')
    hasControl = serializers.CharField(source='control')

    hasTotalMilkYield = quantity_value_serializer_factory('total_milk_yield_unit', 'total_milk_yield_amount')(source='*', required=True)
    hasMilkYield = quantity_value_serializer_factory('milk_yield_unit', 'milk_yield_amount')(source='*', required=True)
    hasRCS = quantity_value_serializer_factory('rcs_unit', 'rcs_amount')(source='*', required=True)
    hasUrea = quantity_value_serializer_factory('urea_unit', 'urea_amount')(source='*', required=True)
    hasFat = quantity_value_serializer_factory('fat_unit', 'fat_amount')(source='*', required=True)
    hasProtein = quantity_value_serializer_factory('protein_unit', 'protein_amount')(source='*', required=True)
    hasDryMatter = quantity_value_serializer_factory('dry_matter_unit', 'dry_matter_amount')(source='*', required=True)

    class Meta:
        model = AnimalLactatingActivity
        fields = [
            'id',
            'activityType', 'title', 'details',
            'hasStartDatetime', 'hasEndDatetime',
            'hasAgriParcel',
            'hasAnimal',
            'responsibleAgent', 'usesAgriculturalMachinery',
            'isPartOfActivity','hasMeasurement',
            'hasDaysInMilk',
            'hasLactationNumber',
            'hasControl',
            'hasTotalMilkYield',
            'hasMilkYield',
            'hasRCS',
            'hasUrea',
            'hasFat',
            'hasProtein',
            'hasDryMatter'
        ]
