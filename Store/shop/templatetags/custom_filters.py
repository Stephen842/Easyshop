from django import template
from shop.models import Products

register = template.Library()

# Custom filter to get products by category
@register.filter
def filter_by_category(products, category_id):
    return products.filter(category__id=category_id)