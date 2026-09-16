from rest_framework import serializers


class IngredientSerializer(serializers.Serializer):
    id = serializers.CharField(required=False, allow_blank=True)
    is_in_taxonomy = serializers.IntegerField(required=False)
    percent_estimate = serializers.FloatField(required=False, default=0)
    percent_max = serializers.FloatField(required=False)
    percent_min = serializers.FloatField(required=False)
    text = serializers.CharField(required=False, allow_blank=True, default="")


class OpenFoodFactsProductSerializer(serializers.Serializer):
    product_name = serializers.CharField(required=False, allow_blank=True, default="")
    image_url = serializers.URLField(required=False, allow_blank=True, default="")
    image_front_url = serializers.URLField(required=False, allow_blank=True, default="")
    additives_tags = serializers.ListField(child=serializers.CharField(), default=list)
    allergens_tags = serializers.ListField(child=serializers.CharField(), default=list)
    ingredients = IngredientSerializer(many=True, default=list)
    ingredients_text = serializers.CharField(required=False, allow_blank=True, default="")
    nutriments = serializers.DictField(required=False, default=dict)


class OpenFoodFactsSerializer(serializers.Serializer):
    code = serializers.CharField(required=False, allow_blank=True)
    product = OpenFoodFactsProductSerializer()
    status = serializers.IntegerField(required=False)
    status_verbose = serializers.CharField(required=False, allow_blank=True)
