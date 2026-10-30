from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import BaseModel, LocationBaseModel, ActivePageManager
from .validators import *


class Farm(BaseModel):
    name = models.CharField(
        _('Farm Name'), max_length=255, unique=False,
        blank=False, null=False,
        default="Unnamed Farm", validators=[]
    )
    description = models.TextField(_('Farm Description'), blank=True, null=True)
    administrator = models.CharField(_('Farm Administrator'), max_length=255, blank=True, null=True, validators=[])
    contact_person_firstname = models.CharField(
        _('Contact Person First Name'), max_length=255, blank=True, null=True, validators=[])
    contact_person_lastname = models.CharField(
        _('Contact Person Last Name'), max_length=255, blank=True, null=True, validators=[])
    telephone = models.CharField(_('Contact Telephone'), max_length=20, blank=True, null=True, validators=[])
    vat_id = models.CharField(_('VAT ID'), max_length=50, blank=True, null=True, validators=[])

    admin_unit_l1 = models.CharField(_('Admin Unit Line 1'), max_length=255, blank=True, null=True, validators=[])
    admin_unit_l2 = models.CharField(_('Admin Unit Line 2'), max_length=255, blank=True, null=True, validators=[])
    address_area = models.CharField(_('Address Area'), max_length=255, blank=True, null=True, validators=[])
    municipality = models.CharField(_('Municipality'), max_length=255, blank=True, null=True, validators=[])
    community = models.CharField(_('Community'), max_length=255, blank=True, null=True, validators=[])
    locator_name = models.CharField(_('Locator Name'), max_length=255, blank=True, null=True, validators=[])

    objects = models.Manager()
    active_objects = ActivePageManager()

    class Meta:
        verbose_name = "Farm"
        verbose_name_plural = "Farms"

    def __str__(self):
        return f"{self.name}"

class FarmParcel(BaseModel, LocationBaseModel):

    identifier = models.CharField(max_length=255, unique=False, blank=False, null=False,
                                  validators=[])
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, blank=False, null=False,
                             related_name="farm_parcels")
    description = models.TextField(blank=True, null=True)
    parcel_type = models.CharField(_('Type of Parcel'), max_length=50)

    valid_from = models.DateTimeField(blank=True, null=True, validators=[])
    valid_to = models.DateTimeField(blank=True, null=True, validators=[])

    in_region = models.CharField(max_length=255, blank=True, null=True, validators=[])
    has_toponym = models.CharField(max_length=255, blank=True, null=True, validators=[])
    area = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    is_nitro_area = models.BooleanField(default=False)
    is_natura2000_area = models.BooleanField(default=False)
    is_pdopg_area = models.BooleanField(default=False)
    is_irrigated = models.BooleanField(default=False)
    is_cultivated_in_levels = models.BooleanField(default=False)
    is_ground_slope = models.BooleanField(default=False)
    depiction = models.URLField(max_length=500, blank=True, null=True)
    # irrigation_system = models.ForeignKey(IrrigationSystem, on_delete=models.SET_NULL, null=True, blank=True, related_name="parcels")
    irrigation_flow = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, validators=[])

    objects = models.Manager()
    active_objects = ActivePageManager()

    class Meta:
        verbose_name = "Farm Parcel"
        verbose_name_plural = "Farm Parcels"

    def __str__(self):
        return f"{self.farm} - {self.identifier} - ({self.parcel_type})"

