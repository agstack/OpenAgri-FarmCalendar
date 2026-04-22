from rest_framework import permissions, viewsets

from farm_activities.models import (
    FarmCalendarActivity,
    FarmCalendarActivityType,
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
from ..serializers import (
    FarmCalendarActivitySerializer,
    FarmCalendarActivityTypeSerializer,
    AlertSerializer,
    FertilizationOperationSerializer,
    IrrigationOperationSerializer,
    CropProtectionOperationSerializer,
    YieldPredictionObservationSerializer,
    DiseaseDetectionObservationSerializer,
    VigorEstimationObservationSerializer,
    SprayingRecommendationObservationSerializer,
    ObservationSerializer,
    CropStressIndicatorObservationSerializer,
    CropGrowthStageObservationSerializer,
    CompostOperationSerializer,
    AddRawMaterialOperationSerializer,
    CompostTurningOperationSerializer,
    AnimalActivitySerializer,
    AnimalLactatingActivitySerializer,
)

from ..filters import (
    FarmCalendarActivityFilter,
    AlertFilter,
    FertilizationOperationFilter,
    IrrigationOperationFilter,
    CropProtectionOperationFilter,
    ObservationFilter,
    CropStressIndicatorObservationFilter,
    CropGrowthStageObservationFilter,
    YieldPredictionObservationFilter,
    DiseaseDetectionObservationFilter,
    VigorEstimationObservationFilter,
    SprayingRecommendationObservationFilter,
    CompostOperationFilter,
    AddRawMaterialOperationFilter,
    CompostTurningOperationFilter,
    AnimalActivityFilter,
    AnimalLactatingActivityFilter,
)


class FarmCalendarActivityTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows FarmCalendarActivityType to be viewed or edited.
    """
    queryset = FarmCalendarActivityType.objects.all().order_by('-name')
    serializer_class = FarmCalendarActivityTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['name', 'category']


class FarmCalendarActivityViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows FarmCalendarActivity to be viewed or edited.
    """
    queryset = FarmCalendarActivity.objects.all().order_by('-start_datetime')
    serializer_class = FarmCalendarActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    filterset_class = FarmCalendarActivityFilter


class AlertViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Alert to be viewed or edited.
    """
    queryset = Alert.objects.all().order_by('-start_datetime')
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['title', 'activity_type', 'severity']

    filterset_class = AlertFilter


class FertilizationOperationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows FertilizationOperation to be viewed or edited.
    """
    queryset = FertilizationOperation.objects.all().order_by('-start_datetime')
    serializer_class = FertilizationOperationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = FertilizationOperationFilter


class IrrigationOperationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows IrrigationOperation to be viewed or edited.
    """
    queryset = IrrigationOperation.objects.all().order_by('-start_datetime')
    serializer_class = IrrigationOperationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = IrrigationOperationFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.kwargs.get('compost_operation_pk'):
            queryset = queryset.filter(parent_activity=self.kwargs['compost_operation_pk'])
        return queryset


class CropProtectionOperationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows CropProtectionOperation to be viewed or edited.
    """
    queryset = CropProtectionOperation.objects.all().order_by('-start_datetime')
    serializer_class = CropProtectionOperationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = CropProtectionOperationFilter


class ObservationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Observation to be viewed or edited.
    """
    queryset = Observation.objects.all().order_by('-start_datetime')
    serializer_class = ObservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = ObservationFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.kwargs.get('compost_operation_pk'):
            queryset = queryset.filter(parent_activity=self.kwargs['compost_operation_pk'])
        return queryset


class CropStressIndicatorObservationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows CropStressIndicator to be viewed or edited.
    """
    queryset = CropStressIndicatorObservation.objects.all().order_by('-start_datetime')
    serializer_class = CropStressIndicatorObservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = CropStressIndicatorObservationFilter


class CropGrowthStageObservationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows CropGrowthStageObservation to be viewed or edited.
    """
    queryset = CropGrowthStageObservation.objects.all().order_by('-start_datetime')
    serializer_class = CropGrowthStageObservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = CropGrowthStageObservationFilter


class YieldPredictionObservationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows YieldPrediction to be viewed or edited.
    """
    queryset = YieldPredictionObservation.objects.all().order_by('-start_datetime')
    serializer_class = YieldPredictionObservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = YieldPredictionObservationFilter


class DiseaseDetectionObservationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows DiseaseDetection to be viewed or edited.
    """
    queryset = DiseaseDetectionObservation.objects.all().order_by('-start_datetime')
    serializer_class = DiseaseDetectionObservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = DiseaseDetectionObservationFilter


class VigorEstimationObservationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows VigorEstimation to be viewed or edited.
    """
    queryset = VigorEstimationObservation.objects.all().order_by('-start_datetime')
    serializer_class = VigorEstimationObservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = VigorEstimationObservationFilter


class SprayingRecommendationObservationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows SprayingRecommendation to be viewed or edited.
    """
    queryset = SprayingRecommendationObservation.objects.all().order_by('-start_datetime')
    serializer_class = SprayingRecommendationObservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = SprayingRecommendationObservationFilter


class CompostOperationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows CompostOperation to be viewed or edited.
    """
    queryset = CompostOperation.objects.all().prefetch_related('nested_activities').order_by('-start_datetime')
    serializer_class = CompostOperationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = CompostOperationFilter


class AddRawMaterialOperationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows AddRawMaterialOperation to be viewed or edited.
    """
    queryset = AddRawMaterialOperation.objects.all().order_by('-start_datetime')
    serializer_class = AddRawMaterialOperationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = AddRawMaterialOperationFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.kwargs.get('compost_operation_pk'):
            queryset = queryset.filter(parent_activity=self.kwargs['compost_operation_pk'])
        return queryset


class CompostTurningOperationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows CompostTurningOperation to be viewed or edited.
    """
    queryset = CompostTurningOperation.objects.all().order_by('-start_datetime')
    serializer_class = CompostTurningOperationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = CompostTurningOperationFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.kwargs.get('compost_operation_pk'):
            queryset = queryset.filter(parent_activity=self.kwargs['compost_operation_pk'])
        return queryset

class AnimalActivityViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows AnimalActivity to be viewed or edited.
    """
    queryset = AnimalActivity.objects.all().order_by('-start_datetime')
    serializer_class = AnimalActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = AnimalActivityFilter

class AnimalLactatingActivityViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows AnimalLactatingActivity to be viewed or edited.
    """
    queryset = AnimalLactatingActivity.objects.all().order_by('-start_datetime')
    serializer_class = AnimalLactatingActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = AnimalLactatingActivityFilter
