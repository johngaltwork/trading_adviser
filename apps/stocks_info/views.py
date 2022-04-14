from django.shortcuts import render
from .forms import *
from .scripts import *


def ticker_form_view(request):
    if request.method == 'POST':
        form = TickerForm(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data['ticker']
            stock_data = get_stock_info(ticker)
            shares_float = round(float(stock_data['floatShares'])/1000000000, 2)
            return render(request, 'stocks_info/ticker_form.html',
                          {
                              'form': form,
                              'stock_data': stock_data,
                              'shares_float': shares_float,
                          }
                          )
    else:
        form = TickerForm()
        return render(request, 'stocks_info/ticker_form.html', {'form': form})


def snp500_view(request):
    output = eq_weight_snp500()
    return render(request, 'stocks_info/snp500_eq_weight.html', {'output': output})


def finviz_news(request):
    req = finviz_parse_news()
    return render(request, 'stocks_info/finviz_news.html', {'news': req})
