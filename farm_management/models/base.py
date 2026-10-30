import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords



from farm_management.asset_registry.agstack import AgstackClient


class BaseModel(models.Model):
    class BaseModelStatus(models.IntegerChoices):
        INACTIVE = 0, 'Inactive'
        ACTIVE = 1, 'Active'
        DELETED = 2, 'Deleted'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, db_index=True, editable=False, unique=True,
                          blank=False, null=False, verbose_name='ID')

    status = models.IntegerField(choices=BaseModelStatus.choices, default=BaseModelStatus.ACTIVE, verbose_name='Status')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Deleted At')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    # Dynamically set the history table name based on the model name
    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        self.status = self.BaseModelStatus.DELETED
        self.deleted_at = timezone.now()
        self.save(update_fields=['status', 'deleted_at'])


class LocationBaseModel(models.Model):
    latitude = models.DecimalField(_('Latitude'), max_digits=17, decimal_places=14, blank=True, null=True)
    longitude = models.DecimalField(_('Longitude'), max_digits=17, decimal_places=14, blank=True, null=True)

    geometry = models.TextField(_('Geometry (WKT EPSG:4326)'), blank=True, null=True)
    geo_id = models.CharField(_('Geographic Data ID'), unique=False, blank=True, null=True)

    class Meta:
        abstract = True

    def _check_geometry_is_new(self, geometry):
        if self.pk is None:
            return True

        query = self.__class__.objects.filter(pk=self.pk).values('geometry')
        if not query.exists():
            return True
        prev_geometry = query.get()['geometry']
        return prev_geometry != geometry

    def save(self, *args, **kwargs):
        if self.geometry:
            if settings.AGSTACK_ASSET_REGISTY_API_URL:
                if self._check_geometry_is_new(self.geometry):
                    try:
                        agstack_client = AgstackClient()
                        self.geo_id = f'{settings.AGSTACK_GEOID_PREFIX}{agstack_client.register_field_boundary(self.geometry)}'
                    except Exception as e:
                        if settings.AGSTACK_AUTO_FALLBACK:
                            # fallback to internal id UUID based on the geometry string
                            self.geo_id = uuid.uuid5(uuid.NAMESPACE_DNS, self.geometry)
                        else:
                            raise e
            else:
                # Generate UUID based on the geometry string
                self.geo_id = uuid.uuid5(uuid.NAMESPACE_DNS, self.geometry)
        elif not self.geometry:
            self.geo_id = None
        super().save(*args, **kwargs)

    @property
    def coordinates(self):
        if self.latitude is not None and self.longitude is not None:
            return f"{self.latitude}, {self.longitude}"
        return "0.0,0.0"


class ActivePageManager(models.Manager):
    def get_queryset(self):
        # Exclude records with status set to DELETED (status=2)
        return super().get_queryset().filter(status__lt=BaseModel.BaseModelStatus.DELETED)


class NamedHistoricalBaseModel(BaseModel):

    name = models.CharField(max_length=100)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name
