from functools import lru_cache


from django_filters import rest_framework as filters
from django.utils.translation import gettext_lazy as _

from shapely.wkt import loads
from shapely.geometry import Point

from farm_management.models import FarmParcel
from farm_activities.models import (
    FarmCalendarActivity,
    Alert,
    FertilizationOperation,
    IrrigationOperation,
    CropProtectionOperation,
    YieldPredictionObservation,
    DiseaseDetectionObservation,
    VigorEstimationObservation,
    SprayingRecommendationObservation,
    Observation,
    CropStressIndicatorObservation,
    CropGrowthStageObservation,
    CompostOperation,
    AddRawMaterialOperation,
    CompostTurningOperation,
    AnimalActivity,
    AnimalLactatingActivity,
)


@lru_cache(maxsize=10)
def is_point_in_geometry(geometry_wkt, point):
    """Check if point is contained in geometry WKT"""
    if not geometry_wkt:
        return False
    try:
        return loads(geometry_wkt).contains(point)
    except:
        return False


class FarmParcelFilter(filters.FilterSet):
    contains_point = filters.CharFilter(
        label=_("Contains point (lat,lon)"),
        method='filter_contains_point',
        help_text=_("Filter parcels containing this point. Format (EPSG:4326): 'latitude,longitude'")
    )

    class Meta:
        model = FarmParcel
        fields = ['identifier', 'farm', 'parcel_type', 'geo_id', 'status']

    def filter_contains_point(self, queryset, name, value):
        """
        Filter farm parcels that contain the given point.
        Input format: "latitude,longitude" (WGS84 coordinates)
        Both point and parcel geometries are in EPSG:4326.
        """
        try:
            lat, lon  = map(float, value.split(','))
            point = Point(lon, lat)

            query_set_values = queryset.values_list('id', 'geometry')

            matching_ids = [
                parcel_id for parcel_id, geometry in query_set_values
                if is_point_in_geometry(geometry, point)
            ]

            return queryset.filter(id__in=matching_ids)

        except (ValueError, TypeError, AttributeError):
            return queryset.none()

class BaseCalendarActivityFilter(filters.FilterSet):
    fromDate = filters.DateTimeFilter(field_name='start_datetime', lookup_expr='gte')
    toDate = filters.DateTimeFilter(field_name='start_datetime', lookup_expr='lte')

    class Meta:
        fields = ['title', 'activity_type', 'parcel', 'responsible_agent']

class FarmCalendarActivityFilter(BaseCalendarActivityFilter):
    class Meta(BaseCalendarActivityFilter.Meta):
        model = FarmCalendarActivity

class AlertFilter(BaseCalendarActivityFilter):
    class Meta(BaseCalendarActivityFilter.Meta):
        model = Alert
        fields = ['title', 'activity_type', 'parcel', 'severity']

class FertilizationOperationFilter(BaseCalendarActivityFilter):
    class Meta(BaseCalendarActivityFilter.Meta):
        model = FertilizationOperation
        fields = ['title', 'activity_type', 'parcel', 'responsible_agent']

class IrrigationOperationFilter(BaseCalendarActivityFilter):
    class Meta(BaseCalendarActivityFilter.Meta):
        model = IrrigationOperation
        fields = ['title', 'activity_type', 'parcel', 'responsible_agent']

class CropProtectionOperationFilter(BaseCalendarActivityFilter):
    class Meta(BaseCalendarActivityFilter.Meta):
        model = CropProtectionOperation
        fields = ['title', 'activity_type', 'parcel', 'responsible_agent']

class ObservationFilter(BaseCalendarActivityFilter):
    class Meta(BaseCalendarActivityFilter.Meta):
        model = Observation
        fields = ['title', 'activity_type', 'parcel']

class CropStressIndicatorObservationFilter(BaseCalendarActivityFilter):
    class Meta(BaseCalendarActivityFilter.Meta):
        model = CropStressIndicatorObservation
        fields = ['title', 'activity_type', 'parcel', 'responsible_agent']

class CropGrowthStageObservationFilter(BaseCalendarActivityFilter):
    class Meta(BaseCalendarActivityFilter.Meta):
        model = CropGrowthStageObservation
        fields = ['title', 'activity_type', 'parcel', 'responsible_agent']

class YieldPredictionObservationFilter(BaseCalendarActivityFilter):
    class Meta(BaseCalendarActivityFilter.Meta):
        model = YieldPredictionObservation
        fields = ['title', 'activity_type', 'parcel']

class DiseaseDetectionObservationFilter(BaseCalendarActivityFilter):
    class Meta(BaseCalendarActivityFilter.Meta):
        model = DiseaseDetectionObservation
        fields = ['title', 'activity_type', 'parcel']

class VigorEstimationObservationFilter(BaseCalendarActivityFilter):
    class Meta(BaseCalendarActivityFilter.Meta):
        model = VigorEstimationObservation
        fields = ['title', 'activity_type', 'parcel']

class SprayingRecommendationObservationFilter(BaseCalendarActivityFilter):
    class Meta(BaseCalendarActivityFilter.Meta):
        model = SprayingRecommendationObservation
        fields = ['title', 'activity_type', 'parcel']

class CompostOperationFilter(BaseCalendarActivityFilter):
    class Meta(BaseCalendarActivityFilter.Meta):
        model = CompostOperation
        fields = ['title', 'activity_type', 'parcel', 'compost_pile_id']

class AddRawMaterialOperationFilter(BaseCalendarActivityFilter):
    class Meta(BaseCalendarActivityFilter.Meta):
        model = AddRawMaterialOperation
        fields = ['title', 'activity_type', 'parcel']

class CompostTurningOperationFilter(BaseCalendarActivityFilter):
    class Meta(BaseCalendarActivityFilter.Meta):
        model = CompostTurningOperation
        fields = ['title', 'activity_type', 'parcel']

class AnimalActivityFilter(BaseCalendarActivityFilter):
    class Meta(BaseCalendarActivityFilter.Meta):
        model = AnimalActivity
        fields = ['title', 'activity_type', 'parcel', 'animal']

class AnimalLactatingActivityFilter(BaseCalendarActivityFilter):
    class Meta(BaseCalendarActivityFilter.Meta):
        model = AnimalLactatingActivity
        fields = ['title', 'activity_type', 'parcel', 'animal']
