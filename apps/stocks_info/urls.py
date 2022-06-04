from django.urls import path

from .views import *

urlpatterns = [
    path('', TickerFormView.as_view(), name='home'),
    path('snp500_eq_weight', SnP500View.as_view(), name='snp500'),
    path('finviz_news', FinvizNews.as_view(), name='news'),
    path('check_ticker', TickerFormView.as_view(), name='check_ticker'),
    path('gaps', GapsView.as_view(), name='gaps'),
    path('aliases_main', AliasesMain.as_view(), name='aliases_main'),
    path('pandas_back_test', PandasDFStocks.as_view(), name='pandas_back_test'),
    path('breakout', BreakOutMorningRange.as_view(), name='breakout'),
    path('watchlist', HomeLeftFormView.as_view(), name='watchlist'),
    path('toolkit_facade', ToolkitFacadeServicesMain.as_view(), name='toolkit_facade'),
    path('aliases_service', AliasService.as_view(), name='aliases_service'),
    path('mailbox_service', MailboxService.as_view(), name='mailbox_service'),
    path('domain_service', DomainService.as_view(), name='domain_service'),
]
