from django import forms
from django.core.exceptions import ValidationError

from .models import AliasModel, WatchListModel


class TickerForm(forms.Form):
    ticker = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter ticker', 'class': 'form-control'})
    )


class GapsForm(forms.Form):
    ticker = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter ticker', 'class': 'form-control'})
    )

    gap = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter gap %', 'class': 'form-control'})
    )


class DeleteAliasForm(forms.Form):
    alias = forms.EmailField(
        label="",
        required=True,
        max_length=100,
        widget=forms.TextInput({"placeholder": "Enter alias", "class": "form-control"}),
    )


class GetAliasForm(forms.Form):
    mailbox = forms.EmailField(
        label="",
        required=True,
        max_length=100,
        widget=forms.TextInput({"placeholder": "Enter mailbox", "class": "form-control"}),
    )


class PandasBackTestForm(forms.Form):
    ticker = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter ticker', 'class': 'form-control'})
    )

    stop_loss = forms.FloatField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter stop-loss', 'class': 'form-control'})
    )

    take_profit = forms.FloatField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter take-profit', 'class': 'form-control'})
    )


class AliasForm(forms.ModelForm):

    class Meta:
        model = AliasModel
        fields = ['alias', 'domain_name', 'mailbox', 'mailbox', 'new_alias', 'old_alias']
        widgets = {
            'alias': forms.TextInput(attrs={'placeholder': 'Enter alias', 'class': 'form-control',}),
            'domain_name': forms.HiddenInput(attrs={'value': 'value',}),
            'mailbox': forms.TextInput(attrs={'placeholder': 'Enter mailbox', 'class': 'form-control',}),
            'new_alias': forms.TextInput(attrs={'placeholder': 'Enter new alias', 'class': 'form-control',}),
            'old_alias': forms.TextInput(attrs={'placeholder': 'Enter old alias', 'class': 'form-control',}),
        }


class GetAliasFormMode(AliasForm):
    AliasForm.Meta.fields = ['mailbox']
    method = forms.CharField(widget=forms.HiddenInput(), initial='get_mailbox_aliases')


class CreateAliasFormMode(AliasForm):
    AliasForm.Meta.fields = ['alias', 'domain_name', 'mailbox']
    method = forms.CharField(widget=forms.HiddenInput(), initial='create_mailbox_alias')


class UpdateAliasFormMode(AliasForm):
    AliasForm.Meta.fields = ['domain_name', 'mailbox', 'old_alias', 'new_alias']
    AliasForm.Meta.widgets['mailbox'] = forms.HiddenInput()
    method = forms.CharField(widget=forms.HiddenInput(), initial='update_mailbox_alias')


class DeleteAliasFormMode(AliasForm):
    AliasForm.Meta.fields = ['alias']
    method = forms.CharField(widget=forms.HiddenInput(), initial='delete_mailbox_alias')
    active_mailbox = forms.CharField(widget=forms.HiddenInput(), initial='')


class BreakOutRangeForm(forms.Form):
    ticker = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter ticker', 'class': 'form-control'})
    )

    tf = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter time-frame', 'class': 'form-control'})
    )

    period = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter period', 'class': 'form-control'})
    )

    profit = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter take-profit', 'class': 'form-control'})
    )


class WatchListForm(forms.ModelForm):

    class Meta:
        model = WatchListModel
        fields = '__all__'

        widgets = {
            'ticker': forms.TextInput(attrs={'placeholder': 'Enter ticker', 'class': 'form-control form-control-sm'}),
            'pnl': forms.TextInput(attrs={'placeholder': 'Enter PnL', 'class': 'form-control form-control-sm'}),
            'winrate': forms.TextInput(attrs={'placeholder': 'Enter Winrate', 'class': 'form-control form-control-sm'}),
            'timeframe': forms.TextInput(attrs={'placeholder': 'Enter Time Frame', 'class': 'form-control form-control-sm'}),
            'winloss': forms.TextInput(attrs={'placeholder': 'Enter Win Loss', 'class': 'form-control form-control-sm'}),
        }

    def clean_ticker(self):
        ticker = self.cleaned_data['ticker']
        if len(ticker) > 5:
            raise ValidationError('Ticker name length must be up to 5 symbols')

        return ticker

