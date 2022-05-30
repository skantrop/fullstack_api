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

class ProductListSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Product
        fields = ('id', 'title', 'price', 'image')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = instance.author.email
        representation['category'] = instance.category.title
        representation['reviews'] = instance.reviews.all().count()
        representation['likes'] = instance.likes.filter(is_liked=True).count()
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if Likes.objects.filter(user=request.user, product=instance, is_liked=True).exists():
                representation['liked_by_user'] = True
        return representation

class ProductDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def validate(self, attrs):
        request = self.context.get('request')
        attrs['author'] = request.user
        return attrs

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = instance.author.email
        representation['category'] = instance.category.title
        representation['reviews'] = ReviewSerializer(instance.reviews.all(), many=True).data
        representation['likes'] = instance.likes.filter(is_liked=True).count()
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if instance.author == request.user:
                representation['is_author'] = True
            if Likes.objects.filter(user=request.user, product=instance, is_liked=True).exists():
                representation['liked_by_user'] = True
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

