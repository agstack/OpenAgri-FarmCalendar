from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import NamedHistoricalBaseModel, BaseModel


class FarmAsset(NamedHistoricalBaseModel):
    class Meta:
        # keep as abstract for now, maybe if we need to query
        # all assets in general, then it would make sense to have a
        # table for this model
        abstract = True

    description = models.TextField(blank=True, null=True)
    parcel = models.ForeignKey('FarmParcel', on_delete=models.SET_NULL,blank=True, null=True,
                               related_name="%(class)ss")


class GenericFarmAsset(NamedHistoricalBaseModel):
    class Meta:
        verbose_name = "Generic Farm Asset"
        verbose_name_plural = "Generic Farm Assets"

    description = models.TextField(blank=True, null=True)
    parcel = models.ForeignKey('FarmParcel', on_delete=models.SET_NULL,blank=True, null=True,
                               related_name="%(class)ss")

    def __str__(self):
        return f"{self.name}"


class FarmCrop(FarmAsset):
    class Meta:
        verbose_name = "Farm Crop"
        verbose_name_plural = "Farm Crops"

    species = models.CharField(max_length=255)
    variety = models.CharField(max_length=255, blank=True, null=True)

    growth_stage = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.species} - {self.variety} - {self.growth_stage}"


class FarmAnimal(FarmAsset):
    class Meta:
        verbose_name = "Farm Animal"
        verbose_name_plural = "Farm Animals"

    class SexChoices(models.IntegerChoices):
        NONE = 0, _('N/A')
        FEMALE = 1, _('Female')
        MALE = 2, _('Male')

    name = models.CharField(_('Name'), max_length=100, blank=True, null=True)
    national_id = models.CharField(_('National ID'), blank=True, null=True)
    species = models.CharField(max_length=255)
    breed = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateTimeField()
    sex = models.IntegerField(choices=SexChoices.choices, default=SexChoices.NONE)
    castrated = models.BooleanField(default=False)
    animal_group = models.CharField(max_length=255, blank=True, null=True)
    entry_date = models.DateField(null=True, blank=True)
    leaving_date = models.DateField(null=True, blank=True)
    previous_owner = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        s = f"{self.species} - {self.breed}"
        if self.animal_group:
            s += f' ({self.animal_group})'
        if self.name:
            s = f'{self.name} - ' + s
        if self.national_id:
            s = f'{self.national_id} - ' + s
        return s


class AgriculturalMachine(FarmAsset):
    class Meta:
        verbose_name = "Farm Machine"
        verbose_name_plural = "Farm Machines"

    purchase_date = models.DateField()
    manufacturer = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    seria_number = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name} - {self.manufacturer} - {self.model}'


class FarmSensor(FarmAsset):
    class Meta:
        verbose_name = "Farm Sensor"
        verbose_name_plural = "Farm Sensors"

    # not sure this should be here... gonna leave out for now
    # data_stream_uri = models.URLField()
    sensor_type = models.CharField()
    public = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} - {self.sensor_type}'

