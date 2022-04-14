from django.urls import path

from .views import *

urlpatterns = [
    path('', ticker_form_view, name='home'),
    path('snp500_eq_weight', snp500_view, name='snp500'),
    path('finviz_news', finviz_news, name='news'),
    path('check_ticker', ticker_form_view, name='check_ticker'),
]
