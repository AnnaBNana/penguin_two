from datetime import datetime

from django.utils import timezone
from django.contrib import admin


class MonthFilter(admin.SimpleListFilter):

    title = 'Sold Date Calendar Month'
    parameter_name = 'month_year'

    def lookups(self, request, model_admin):
        unique_sold_dates = model_admin.model.objects.dates('sold_date', 'month', 'DESC')
        return [[item.strftime("%m_%Y"), item.strftime("%B %Y")]for item in unique_sold_dates]

    def queryset(self, request, queryset):
        month_year = self.value()
        if month_year:
            month = month_year[:2]
            year = month_year[3:]
            return queryset.filter(sold_date__month=month, sold_date__year=year)
        else:
            return queryset
