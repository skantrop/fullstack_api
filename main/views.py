import django_filters.rest_framework as filters
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework import viewsets, mixins, status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .filters import ProductFilter
from .models import Product, Review, Likes, Favorite
from .permissions import IsAuthororAdminPermission
from .serializers import (CategorySerializer, ProductListSerializer,
                          ProductDetailsSerializer, ReviewSerializer, FavoriteListSerializer)


class CategoryCreateView(CreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductDetailsSerializer
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filterset_class = ProductFilter
    ordering_fields = ['title', 'price']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        elif self.action in ['create_review', 'toggle_like', 'toggle_favorites']:
            return [IsAuthenticated()]
        return []

    # api/v1/products/products/id/like/
    @action(detail=True, methods=['GET'])
    def toggle_like(self, request, pk):
        product = self.get_object()
        user = request.user
        like_obj, created = Likes.objects.get_or_create(product=product, user=user)

        like_obj.is_liked = not like_obj.is_liked
        like_obj.save()
        return Response('like toggled')

    # api/v1/products/products/id/favorites/
    @action(detail=True, methods=['GET'])
    def toggle_favorites(self, request, pk):
        product = self.get_object()
        user = request.user
        fav, created = Favorite.objects.get_or_create(product=product, user=user)
        
        fav.favorite = not fav.favorite
        fav.save()
        return Response('favourite toggled')

    @swagger_auto_schema(manual_parameters=[openapi.Parameter('likes_from', openapi.IN_QUERY, 'filter products by amount of likes', True, type=openapi.TYPE_INTEGER)])
    @action(detail=False, methods=["GET"])
    def likes(self, request, pk=None):
        from django.db.models import Count
        q = request.query_params.get("likes_from")  # request.query_params = request.GET
        queryset = self.get_queryset()
        queryset = queryset.annotate(Count('likes')).filter(likes__count__gte=q)

        serializer = ProductListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_serializer_context(self):
        return {'request': self.request}


class ReviewViewSet(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAuthororAdminPermission()]

    def get_serializer_context(self):
        return {'request': self.request}

class FavoriteView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = FavoriteListSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(favorites__user=self.request.user, favorites__favorite=True)
        return queryset

    def get_serializer_context(self):
        return {'request': self.request}
