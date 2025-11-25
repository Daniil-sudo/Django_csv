from django.shortcuts import render, get_object_or_404
from .models import Phone


def phone_catalog(request):
    phones = Phone.objects.all()

    # Получаем параметр сортировки из URL
    ordering_param = request.GET.get('ordering', 'name')

    # Разрешённые варианты сортировки
    ordering_map = {
        'name': 'name',
        'price_asc': 'price',
        'price_desc': '-price',
    }

    # Если параметр не распознан — сортировать по названию
    ordering = ordering_map.get(ordering_param, 'name')

    phones = phones.order_by(ordering)

    context = {
        'phones': phones,
        'current_ordering': ordering_param,
    }
    return render(request, 'catalog/catalog_list.html', context)


def phone_detail(request, slug):
    phone = get_object_or_404(Phone, slug=slug)
    return render(request, 'catalog/phone_detail.html', {'phone': phone})
