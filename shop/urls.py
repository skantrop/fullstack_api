"""shop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include, reverse_lazy
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from rest_framework.routers import SimpleRouter
from main.views import CategoryCreateView, ReviewViewSet, ProductViewSet, FavoriteView, CategoryListView

router = SimpleRouter()
router.register('products', ProductViewSet)
router.register('reviews', ReviewViewSet)


schema_view = get_schema_view(
    openapi.Info(
        title='Shop API',
        default_version='v1',
        description='Makers coding bootcamp'
    ),
    public=True,
    permission_classes=[AllowAny],
)

urlpatterns = [
    path('', lambda request: redirect(reverse_lazy('docs'))),
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/category/', CategoryCreateView.as_view()),
    path('api/v1/category/list/', CategoryListView.as_view()),
    path('api/v1/account/', include('account.urls')),
    path('api/v1/favorites/', FavoriteView.as_view()),
    path('api/v1/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='docs'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

