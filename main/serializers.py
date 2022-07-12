from multiprocessing import context
import re
from rest_framework import serializers
from .models import Category, Likes, Product, Review, Favorite
from django.contrib.auth import get_user_model

User = get_user_model()

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = ('author',)

    def validate(self, attrs):
        request = self.context.get('request')
        attrs['author'] = request.user
        return attrs

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = instance.author.email
        representation['category'] = {"title":instance.category.title, "id":instance.category.id}
        representation['reviews'] = ReviewSerializer(instance.reviews.all(), many=True).data
        representation['likes'] = instance.likes.filter(is_liked=True).count()
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            representation['is_author'] = instance.author == request.user
            representation['liked_by_user'] = Likes.objects.filter(user=request.user, product=instance, is_liked=True).exists()
            representation['favorite_by_user'] = Product.objects.filter(favorites__user=self.request.user, favorites__favorite=True).exists()
        return representation

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        exclude = ('author',)

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
        model = Product
        fields = '__all__'

