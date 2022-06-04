import json
import requests
from django.urls import reverse

from .utils import *
from .utils_toolkit import *
from django.conf import settings
from django.shortcuts import render
from .forms import *
from .forms_toolkit import *
from .scripts import *
from .backtesting import *
from django.views.generic import View, TemplateView, ListView, CreateView


class TickerFormView(View):
    form_class = TickerForm
    template_name = 'stocks_info/ticker_form.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data['ticker']
            stock_data = get_stock_info(ticker)
            shares_float = round(
                float(stock_data['floatShares']) / 1000000000, 2)
            return render(request, self.template_name,
                          {
                              'form': form,
                              'stock_data': stock_data,
                              'shares_float': shares_float,
                          }
                          )

        return render(request, self.template_name, {'form': form})


class SnP500View(TemplateView):
    context_object_name = 'output'
    template_name = 'stocks_info/snp500_eq_weight.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        output = eq_weight_snp500()
        context['output'] = output
        back_test = spy_back_test()
        context['back'] = back_test
        return context


class FinvizNews(View):
    form_class = TickerForm
    template_name = 'stocks_info/finviz_news.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data['ticker'].upper()
            stock_data = finviz_parse_news_form(ticker)
            fundamental_info = get_stock_fundamental_info(ticker)
            return render(request, self.template_name,
                          {
                              'form': form,
                              'news': stock_data,
                              'fundamental_info': fundamental_info,
                          }
                          )

        return render(request, self.template_name, {'form': form})


class GapsView(View):
    form_class = GapsForm
    template_name = 'stocks_info/gaps.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data['ticker'].upper()
            gap = float(form.cleaned_data['gap']) / 100
            gaps_data = gaps(ticker, gap)
            return render(request, self.template_name,
                          {
                              'form': form,
                              'gaps': gaps_data[0],
                              'all_gaps': gaps_data[1],
                              'green': gaps_data[2],
                              'red': gaps_data[3],
                              'all_days': gaps_data[4],
                              'shares_float': gaps_data[5],
                              'market_cap': gaps_data[6],
                              'green_percent': gaps_data[7],
                              'red_percent': gaps_data[8],
                              'gap': gap,
                          }
                          )

        return render(request, self.template_name, {'form': form})


class DeleteAlias(View):
    form_class = DeleteAliasForm
    template_name = 'toolkit/delete_alias.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            alias = form.cleaned_data['alias']
            return render(request, self.template_name, {'form': form, 'alias': alias})

        return render(request, self.template_name, {'form': form})


class PandasDFStocks(View):
    template_name = 'stocks_info/pandas_back_test.html'
    form_class = PandasBackTestForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data['ticker']
            stop_loss = form.cleaned_data['stop_loss']
            take_profit = form.cleaned_data['take_profit']

            list_tickers = ticker.replace(',', ' ').replace('  ', ' ')
            list_tickers = list_tickers.split(' ')

            if len(list_tickers) == 1:

                stock_data = GetPandasDF(ticker, stop_loss, take_profit).get_intraday_data()

                winnloss = f"{take_profit/take_profit}/{stop_loss/take_profit}"
                winrate = stock_data[4]/stock_data[3]*100
                total_profit = stock_data[4]*take_profit
                total_loss = stock_data[5]*stop_loss

                return render(request, self.template_name,
                              {
                                  'form': form,
                                  'output': stock_data[0].round(2).values.tolist(),
                                  'pnl': stock_data[1],
                                  'atr': stock_data[2].round(2),
                                  'ticker': ticker.upper(),
                                  'winrate': winrate,
                                  'all_trades': stock_data[3],
                                  'profit_trades': stock_data[4],
                                  'loss_trades': stock_data[5],
                                  'winnloss': winnloss,
                                  'total_profit': total_profit,
                                  'total_loss': total_loss,
                              }
                              )
            else:
                list_output = {}
                for i in range(len(list_tickers)):
                    stock_data = GetPandasDF(list_tickers[i], stop_loss, take_profit).get_intraday_data()
                    list_output[list_tickers[i]] = {
                                                    'atr': stock_data[2].round(2),
                                                    'pnl': stock_data[1],
                                                   }

                return render(request, self.template_name, {'form': form, 'list_output': list_output})

        return render(request, self.template_name, {'form': form})


class BreakOutMorningRange(View, BreakOutMorningRange):
    form_class = BreakOutRangeForm
    watch_list_form = WatchListForm
    model = WatchListModel
    template_name = 'stocks_info/breakout.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        watch_list_form = self.watch_list_form()
        context = self.model.objects.all()
        return render(request, self.template_name, {'form': form, 'watch_list_form': watch_list_form, 'context': context})

    def post(self, request, *args, **kwargs):
        context = self.model.objects.all()
        form = self.form_class(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data['ticker'].upper().replace('   ', ', ')
            tf = form.cleaned_data['tf']
            period = form.cleaned_data['period']
            profit = form.cleaned_data['profit']

            list_tickers = ticker.replace(',', ' ').replace('  ', ' ')
            list_tickers = list_tickers.split(' ')

            time_frames = tf.replace(',', ' ').replace('  ', ' ')
            time_frames = time_frames.split(' ')

            profits = profit.split(', ')
            profits = [float(i) for i in profits]

            response = []

            for ticker in list_tickers:
                for tp in profits:
                    for tf in time_frames:
                        response.append(self.backtest(ticker, tf, period, tp))

            response = sorted(response, key=lambda x: x[1], reverse=True)

            return render(request, self.template_name,
                          {
                              'form': form,
                              'response': response,
                              'context': context,
                          }
                          )

        return render(request, self.template_name, {'form': form})


class HomeLeftFormView(CreateView):
    form_class = WatchListForm
    model = WatchListModel
    template_name = 'stocks_info/watchlist.html'
    allow_empty = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["objects"] = self.model.objects.all()
        return context

    def get_success_url(self):
        return reverse('watchlist')


#  Toolkit - Facade Infra API communicates
class AliasesMain(AliasesRequestToFacadeMixin, View):
    form_classes = (GetAliasFormMode, CreateAliasFormMode, UpdateAliasFormMode, DeleteAliasFormMode, )
    template_name = 'toolkit/aliases_main.html'


class ToolkitFacadeServicesMain(TemplateView):
    template_name = 'toolkit/toolkit_facade_main.html'


class DomainService(DomainServiceMixin, View):
    form_classes = (RTFCreateDomainFormMode, RTFDeleteDomainFormMode, RTFGetDomainInfoFormMode)
    template_name = 'toolkit/domain_service.html'


class MailboxService(MailboxServiceMixin, View):
    form_classes = (RTFCreateMailboxFormMode, RTFDeleteMailboxFormMode, RTFGetMailboxInfoFormMode,)
    template_name = 'toolkit/mailbox_service.html'


class AliasService(AliasServiceMixin, View):
    form_classes = (RTFGetAliasFormMode, RTFCreateAliasFormMode, RTFUpdateAliasFormMode, RTFDeleteAliasFormMode,)
    template_name = 'toolkit/aliases_service.html'


