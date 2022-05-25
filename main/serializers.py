from rest_framework import serializers
from .models import Product, Review, Favorite
from django.contrib.auth import get_user_model

User = get_user_model()


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'title', 'price', 'image')


class ProductDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        # exclude = ('author', )

    def validate(self, attrs):
        request = self.context.get('request')
        attrs['author'] = request.user
        return attrs

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['author'] = ReviewAuthorSerializer(instance.author).data
        return rep


    def get_likes(self, instance):
        total_likes = sum(instance.likes.values_list('is_liked', flat=True))
        likes = total_likes if total_likes > 0 else 0
        return likes

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = instance.author.email
        representation['reviews'] = ReviewSerializer(instance.reviews.all(), many=True).data
        representation['likes'] = self.get_likes(instance)
        return representation


class ReviewAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'last_name')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not instance.name and not instance.last_name:
            representation['full_name'] = 'Anonymous User'
        return representation


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        exclude = ('id', 'author')

    def validate_product(self, product):
        request = self.context.get('request')
        if product.reviews.filter(author=request.user).exists():
            raise serializers.ValidationError('You cannot add second review to this product')
        return product

    def validate(self, attrs):
        request = self.context.get('request')
        attrs['author'] = request.user
        return attrs

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['author'] = instance.author.email
        return rep


class FavoriteListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product'] = ProductDetailsSerializer(Product.objects.filter(favorites=instance.id),
                                                             many=True, context=self.context).data
        return representation

