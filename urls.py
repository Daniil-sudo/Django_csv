from django.urls import path
import views

urlpatterns = [
    # URL для каталога телефонов
    # request.GET.get('ordering') будет использоваться в view
    path('catalog/', views.phone_catalog, name='phone_catalog'),

    # URL для детальной страницы телефона.
    # <slug:slug> - это переменная часть URL, которая будет передана в view как аргумент 'slug'
    path('catalog/<slug:slug>/', views.phone_detail, name='phone_detail'),
]

