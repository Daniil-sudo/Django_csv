from django.shortcuts import render, get_object_or_404
from models import Phone
from django.db.models import Q  # Для более сложных фильтраций, если понадобятся
from django.views.generic import ListView, DetailView  # Можно использовать и классовые представления


# --- Представление для списка телефонов ---
def phone_catalog(request):
    phones = Phone.objects.all()

    # --- Обработка параметров сортировки из URL ---
    # Параметры сортировки будут передаваться как GET-параметры, например:
    # /catalog/?ordering=price_desc
    ordering_param = request.GET.get('ordering', 'name')  # По умолчанию сортируем по названию

    # Определяем порядок сортировки
    if ordering_param == 'name':
        phones = phones.order_by('name')  # Алфавитный порядок названий
        current_ordering = 'name'
    elif ordering_param == 'name_desc':
        phones = phones.order_by('-name')  # Обратный алфавитный порядок
        current_ordering = 'name_desc'
    elif ordering_param == 'price_asc':
        phones = phones.order_by('price')  # По возрастанию цены
        current_ordering = 'price_asc'
    elif ordering_param == 'price_desc':
        phones = phones.order_by('-price')  # По убыванию цены
        current_ordering = 'price_desc'
    else:  # Если передан неизвестный параметр, используем сортировку по умолчанию
        phones = phones.order_by('name')
        current_ordering = 'name'

    context = {
        'phones': phones,
        'current_ordering': current_ordering,  # Передаем текущий параметр для выделения активной ссылки
    }
    return render(request, 'catalog/catalog_list.html', context)


# --- Представление для детальной страницы телефона ---
def phone_detail(request, slug):
    # Получаем объект Phone по полю slug. get_object_or_404 вернет 404, если объект не найден.
    phone = get_object_or_404(Phone, slug=slug)

    context = {
        'phone': phone,
    }
    return render(request, 'catalog/phone_detail.html', context)

