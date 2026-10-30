from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings

from rest_framework_nested import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


from .views import (
    FarmViewSet,
    FarmParcelViewSet,
    GenericFarmAssetSerializerViewSet,
    FarmCropViewSet,
    FarmAnimalViewSet,
    AgriculturalMachineViewSet,
    FarmCalendarActivityViewSet,
    FarmCalendarActivityTypeViewSet,
    AlertViewSet,
    FertilizationOperationViewSet,
    FertilizerViewSet,
    IrrigationOperationViewSet,
    CropProtectionOperationViewSet,
    YieldPredictionObservationViewSet,
    DiseaseDetectionObservationViewSet,
    VigorEstimationObservationViewSet,
    SprayingRecommendationObservationViewSet,
    PesticideViewSet,
    ObservationViewSet,
    CropStressIndicatorObservationViewSet,
    CropGrowthStageObservationViewSet,
    CompostOperationViewSet,
    AddRawMaterialOperationViewSet,
    CompostTurningOperationViewSet,
    AnimalActivityViewSet,
    AnimalLactatingActivityViewSet,
    BulkAnimalLactatingActivitiesView
)

router = routers.DefaultRouter()

router.register(r'Farm', FarmViewSet)
router.register(r'FarmParcels', FarmParcelViewSet)
router.register(r'GenericFarmAssets', GenericFarmAssetSerializerViewSet)
router.register(r'FarmCrops', FarmCropViewSet)
router.register(r'FarmAnimals', FarmAnimalViewSet)
router.register(r'AgriculturalMachines', AgriculturalMachineViewSet)
router.register(r'FarmCalendarActivities', FarmCalendarActivityViewSet)
router.register(r'FarmCalendarActivityTypes', FarmCalendarActivityTypeViewSet)
router.register(r'Alerts', AlertViewSet)
router.register(r'FertilizationOperations', FertilizationOperationViewSet)
router.register(r'Fertilizers', FertilizerViewSet)
router.register(r'IrrigationOperations', IrrigationOperationViewSet)
router.register(r'CropProtectionOperations', CropProtectionOperationViewSet)
router.register(r'YieldPrediction', YieldPredictionObservationViewSet)
router.register(r'DiseaseDetection', DiseaseDetectionObservationViewSet)
router.register(r'VigorEstimation', VigorEstimationObservationViewSet)
router.register(r'SprayingRecommendation', SprayingRecommendationObservationViewSet)
router.register(r'Pesticides', PesticideViewSet)
router.register(r'Observations', ObservationViewSet)
router.register(r'CropStressIndicatorObservations', CropStressIndicatorObservationViewSet)
router.register(r'CropGrowthStageObservations', CropGrowthStageObservationViewSet)
router.register(r'AddRawMaterialOperations', AddRawMaterialOperationViewSet)
router.register(r'CompostOperations', CompostOperationViewSet)
router.register(r'CompostTurningOperations', CompostTurningOperationViewSet)
router.register(r'AnimalActivities', AnimalActivityViewSet)
router.register(r'AnimalLactatingActivities', AnimalLactatingActivityViewSet)



compost_operations_router = routers.NestedSimpleRouter(router, r'CompostOperations', lookup='compost_operation')
compost_operations_router.register(r'AddRawMaterialOperations', AddRawMaterialOperationViewSet, basename=f'compost-operation-addrawmaterialoperation')
compost_operations_router.register(r'IrrigationOperations', IrrigationOperationViewSet, basename=f'compost-operation-irrigationoperation')
compost_operations_router.register(r'Observations', ObservationViewSet, basename=f'compost-operation-observation')
compost_operations_router.register(r'CompostTurningOperations', CompostTurningOperationViewSet, basename=f'compost-turning-operation-observation')




urlpatterns = [
    path('api/', lambda request: redirect('api-root', settings.SHORT_API_VERSION)),
    path('api/<str:version>/', include([
        path('', include(router.urls)),  # Register versioned API routes
        path('', include(compost_operations_router.urls)),  # Register versioned API routes
        path('bulk/animal-lactating-activities/', BulkAnimalLactatingActivitiesView.as_view(), name='bulk-animal-lactating-activities'),
        path('schema/', SpectacularAPIView.as_view(), name='schema'),  # Schema generation
        path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),  # Swagger UI
        path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),  # ReDoc
    ])),
]
