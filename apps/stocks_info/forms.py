from django import forms


class TickerForm(forms.Form):
    ticker = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter ticker', 'class': 'form-control'})
    )
