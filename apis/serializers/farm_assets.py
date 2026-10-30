import uuid

from rest_framework import serializers

from ..schemas import generate_urn
from .base import URNRelatedField

from farm_management.models import (
    GenericFarmAsset,
    FarmCrop, FarmAnimal,
    AgriculturalMachine, FarmParcel
)


class BaseFarmAssetSerializer(serializers.ModelSerializer):
    hasAgriParcel = URNRelatedField(
        source='parcel',
        class_names=['Parcel'],
        queryset=FarmParcel.objects.all(),
    )
    dateCreated = serializers.DateTimeField(source='created_at', read_only=True)
    dateModified = serializers.DateTimeField(source='updated_at', read_only=True)
    invalidatedAtTime = serializers.DateTimeField(source='deleted_at', read_only=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        json_ld_representation = {
            '@id': generate_urn(instance.__class__.__name__, obj_id=representation.pop('id')),
            **representation
        }

        return json_ld_representation


class GenericFarmAssetSerializer(BaseFarmAssetSerializer):

    class Meta:
        model = GenericFarmAsset
        fields = [
            'status', 'invalidatedAtTime', 'dateCreated', 'dateModified',
            'id', 'name', 'description',
            'hasAgriParcel',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        json_ld_representation = {
            '@type': 'FarmAsset',
            **representation
        }

        return json_ld_representation



class CropSpeciesSerializerField(serializers.Serializer):
    name = serializers.CharField(source='species')
    variety = serializers.CharField()

    def to_representation(self, instance):
        variety = (getattr(instance, 'variety', '') or '')
        uuid_orig_str = "".join([
            getattr(instance, 'species', ''),
            variety,
        ])
        hash_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, uuid_orig_str))
        return {
            '@id': generate_urn('CropType', obj_id=hash_uuid),
            '@type': 'CropType',
            'name': getattr(instance, 'species', ''),
            'variety': variety,
        }


class FarmCropSerializer(BaseFarmAssetSerializer):
    cropSpecies = CropSpeciesSerializerField(source='*')

    class Meta:
        model = FarmCrop
        fields = [
            'status', 'invalidatedAtTime', 'dateCreated', 'dateModified',
            'id', 'name', 'description',
            'hasAgriParcel', 'cropSpecies',
            'growth_stage',
            'kc_init', 'kc_mid', 'kc_end'
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        json_ld_representation = {
            '@type': 'Crop',
            **representation
        }

        return json_ld_representation


class FarmAnimalGroupSerializerField(serializers.Serializer):
    hasName = serializers.CharField(source='animal_group', required=False)

    def to_representation(self, instance):
        uuid_orig_str = getattr(instance, 'animal_group', '')
        if uuid_orig_str is None or uuid_orig_str is '':
            return {}
        hash_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, uuid_orig_str))
        return {
            '@id': generate_urn('AnimalGroup', obj_id=hash_uuid),
            '@type': 'AnimalGroup',
            'hasName': uuid_orig_str
        }

class FarmAnimalSerializer(BaseFarmAssetSerializer):
    nationalID = serializers.CharField(source='national_id', required=False)
    birthdate = serializers.DateTimeField(source='birth_date')
    isMemberOfAnimalGroup = FarmAnimalGroupSerializerField(source='*', required=False, allow_null=False)
    isCastrated = serializers.BooleanField(source='castrated', required=False)

    class Meta:
        model = FarmAnimal
        fields = [
            'id', 'nationalID', 'name', 'description',
            'hasAgriParcel',
            'sex', 'isCastrated', 'species', 'breed', 'birthdate', 'isMemberOfAnimalGroup',
            'status', 'invalidatedAtTime', 'dateCreated', 'dateModified',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        json_ld_representation = {
            '@type': 'Animal',
            **representation
        }

        return json_ld_representation


class AgriculturalMachineSerializer(BaseFarmAssetSerializer):
    class Meta:
        model = AgriculturalMachine
        fields = [
            'id', 'name', 'description',
            'hasAgriParcel',
            'purchase_date', 'manufacturer', 'model', 'seria_number',
            'status', 'invalidatedAtTime', 'dateCreated', 'dateModified',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        json_ld_representation = {
            '@type': 'AgriculturalMachine',
            **representation
        }

        return json_ld_representation
