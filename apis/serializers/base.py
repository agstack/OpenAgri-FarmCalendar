from uuid import UUID

from django.db.models.fields.related import ForeignKey, OneToOneField, ManyToManyField

from rest_framework.relations import PrimaryKeyRelatedField, PKOnlyObject
from rest_framework.relations import PrimaryKeyRelatedField, PKOnlyObject
from rest_framework import serializers

from ..schemas import OCSM_SCHEMA, generate_urn_prefix


class URNCharField(serializers.CharField):
    def __init__(self, class_names, **kwargs):
        """
        :param class_name: The class name added to the prefix for the URN, e.g., 'urn:myapp:farm'.
        :param kwargs: Additional arguments for PrimaryKeyRelatedField.
        """
        if class_names is None:
            class_names = ['{class_name}']
        self.class_name = class_names[0]
        self.urn_prefix = generate_urn_prefix(class_names)
        super().__init__(**kwargs)

    def to_representation(self, value):
        """
        Converts the related object to a URN string.
        """

        uuid_value = value

        json_ld_dict = {
            "@type": self.class_name,
            "@id": f"{self.urn_prefix}:{uuid_value}",
        }
        return json_ld_dict

    def to_internal_value(self, data):
        """
        Converts a URN string into a model instance.
        """
        if data is None:
            return data
        if not self.class_name == '{class_name}':
            if not isinstance(data, dict) or '@type' not in data or '@id' not in data:
                raise serializers.ValidationError((
                    f"Invalid URN ref dict format. Expected a dictionary with "
                    f"@type' (e.g., '{self.class_name}') and '@id' (e.g, with prefix '{self.urn_prefix}:')."
                    f" Received'{data}' instead."
                ))
            urn_data = data["@id"]


        # Extract the ID from the URN
        raw_id = urn_data.split(':')[-1]

        # Ensure the ID is valid (UUID or integer depending on the target field)
        # try:
        #     raw_id = UUID(raw_id)
        # except (ValueError, TypeError):
        #     raise serializers.ValidationError("Invalid ID in URN.")

        # Fetch the related instance
        return super().to_internal_value(raw_id)


class URNRelatedField(PrimaryKeyRelatedField):
    """
    A custom DRF field for representing relations using URNs.
    """
    def __init__(self, class_names, **kwargs):
        """
        :param class_name: The class name added to the prefix for the URN, e.g., 'urn:myapp:farm'.
        :param kwargs: Additional arguments for PrimaryKeyRelatedField.
        """
        if class_names is None:
            class_names = ['{class_name}']
        self.class_name = class_names[0]
        self.urn_prefix = generate_urn_prefix(class_names)
        super().__init__(**kwargs)

    def to_representation(self, value):
        """
        Converts the related object to a URN string.
        """

        if isinstance(value, PKOnlyObject):
            uuid_value = value.pk
        else:
            uuid_value = value.id

        json_ld_dict = {
            "@type": self.class_name,
            "@id": f"{self.urn_prefix}:{uuid_value}",
        }
        return json_ld_dict

    def to_internal_value(self, data):
        """
        Converts a URN string into a model instance.
        """
        if data is None:
            return data
        if isinstance(data, str):
            urn_data = data
        else:
            if not self.class_name == '{class_name}':
                if not isinstance(data, dict) or '@type' not in data or '@id' not in data:
                    raise serializers.ValidationError((
                        f"Invalid URN ref dict format. Expected a dictionary with "
                        f"@type' (e.g., '{self.class_name}') and '@id' (e.g, with prefix '{self.urn_prefix}:')."
                        f" Received'{data}' instead."
                    ))
            urn_data = data["@id"]


        # Extract the ID from the URN
        raw_id = urn_data.split(':')[-1]

        # Ensure the ID is valid (UUID or integer depending on the target field)
        try:
            raw_id = UUID(raw_id)
        except (ValueError, TypeError):
            raise serializers.ValidationError("Invalid ID in URN.")

        # Fetch the related instance
        return super().to_internal_value(raw_id)

    def get_choices(self, cutoff=None):
        """
        Overrides `get_choices` to return valid choices for the DRF browsable API.
        """
        queryset = self.get_queryset()
        if queryset is None:
            # Ensure that field.choices returns something sensible
            # even when accessed with a read-only field.
            return {}

        if cutoff is not None:
            queryset = queryset[:cutoff]

        choices = {
            self.to_representation(item)['@id']: self.display_value(item) for item in queryset
        }

        return choices



class JSONLDSerializer(serializers.ModelSerializer):

    def _check_is_relationship_field(self, instance, field_name):
        # Get the model's meta information
        model = instance.__class__
        field = model._meta.get_field(field_name)

        return isinstance(field, (ForeignKey, OneToOneField, ManyToManyField))


    def _prepare_represetation(self, instance):
        json_dict_rep = super().to_representation(instance)
        base_rep = {}
        for field, value in json_dict_rep.items():
            correct_value = value
            if not self._check_is_relationship_field(instance, field):
                correct_value = getattr(instance, field)
            base_rep[field] = correct_value
        return base_rep

    def to_representation(self, instance):
        class_key = self.Meta.model.__name__
        try:
            ClassSchema = OCSM_SCHEMA[class_key]
        except KeyError:
            return super().to_representation(instance)
        representation = self._prepare_represetation(instance)
        json_ld_representation = ClassSchema().dump(representation)
        return json_ld_representation
