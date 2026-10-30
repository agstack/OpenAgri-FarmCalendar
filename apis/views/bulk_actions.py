# views/bulk_actions.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, inline_serializer
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers

from farm_management.models import FarmAnimal
from farm_activities.models import AnimalLactatingActivity
from ..serializers import FarmAnimalSerializer, AnimalLactatingActivitySerializer


# Define inline serializer for the bulk request/response
class BulkAnimalActivityItemSerializer(serializers.Serializer):
    animal = FarmAnimalSerializer()
    activities = AnimalLactatingActivitySerializer(many=True)


class BulkAnimalLactatingActivitiesView(APIView):

    @extend_schema(
        request=BulkAnimalActivityItemSerializer(many=True),
        responses={
            201: OpenApiResponse(
                response=BulkAnimalActivityItemSerializer(many=True),
                description="Successfully created animals and activities"
            ),
            400: OpenApiResponse(
                description="Bad request - validation error"
            ),
        },
        description="""
        Create multiple animals and their lactating activities in a single request.

        Each item in the list should contain:
        - `animal`: Animal data (same as FarmAnimals endpoint)
        - `activities`: List of lactating activities (same as AnimalLactatingActivities endpoint)

        The entire operation is atomic - if any animal or activity fails validation,
        nothing will be saved.
        """,
        tags=['bulk']
    )
    @transaction.atomic
    def post(self, request, version=None):
        results = []

        for item in request.data:
            # Create the animal first
            national_id = item['animal'].get('nationalID')
            created_activities = []

            animal = FarmAnimal.objects.filter(national_id=national_id).first()

            if animal:
                # Use existing animal
                animal_serializer = FarmAnimalSerializer(animal)
            else:
                # Create new animal
                animal_serializer = FarmAnimalSerializer(data=item['animal'])
                animal_serializer.is_valid(raise_exception=True)
                animal = animal_serializer.save()

            # Create lactating activities referencing this animal
            for activity_data in item['activities']:
                activity_data['hasAnimal'] = f"urn:farmcalendar:FarmAnimal:{animal.id}"
                # Add empty list for agricultural machinery
                activity_data['usesAgriculturalMachinery'] = []
                activity_serializer = AnimalLactatingActivitySerializer(data=activity_data)
                activity_serializer.is_valid(raise_exception=True)


                validated_data = activity_serializer.validated_data

                duplicate_exists = activity_serializer.Meta.model.objects.filter(
                    animal_id=animal.id,
                    activity_type=validated_data.get('activity_type'),
                    start_datetime=validated_data.get('start_datetime'),
                    title=validated_data.get('title')
                ).exists()

                if not duplicate_exists:
                    activity_serializer.save()
                    created_activities.append(activity_serializer.data)

            results.append({
                'animal': animal_serializer.data,
                'activities': created_activities
            })

        return Response(results, status=status.HTTP_201_CREATED)
