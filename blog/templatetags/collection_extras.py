from django import template
from math import ceil

from ..models import Category

register = template.Library()

@register.inclusion_tag('widgets/categories.html')
def get_widgets():
    categories_list = Category.objects.order_by('title')
    categories_list_first_part = []
    categories_list_second_part = []
    len_list = len(categories_list)
    middle_list = 0
    if len_list > 3:
        middle_list = ceil(len_list / 2)
        categories_list_first_part = categories_list[:middle_list]
        categories_list_second_part = categories_list[middle_list:]

    return {'categories_list': categories_list, 'middle_list': middle_list,
            'categories_list_first_part': categories_list_first_part,
            'categories_list_second_part': categories_list_second_part}

@register.inclusion_tag('widgets/search.html')
def get_widgets_search(): pass

@register.inclusion_tag('widgets/calendar.html')
def get_widgets_calendar(): pass
