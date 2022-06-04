from django import forms
from django.core.exceptions import ValidationError

from .models import RTFModel


class RTFForm(forms.ModelForm):

    class Meta:
        model = RTFModel
        fields = '__all__'
        widgets = {
            'alias': forms.TextInput(attrs={'placeholder': 'Enter alias', 'class': 'form-control', }),
            'domain_name': forms.TextInput(attrs={'placeholder': 'Domain name', 'class': 'form-control', }),
            'mailbox': forms.TextInput(attrs={'placeholder': 'Enter mailbox', 'class': 'form-control', }),
            'new_alias': forms.TextInput(attrs={'placeholder': 'Enter new alias', 'class': 'form-control', }),
            'old_alias': forms.TextInput(attrs={'placeholder': 'Enter old alias', 'class': 'form-control', }),
            'is_active': forms.CheckboxInput(attrs={'type': 'checkbox', 'class': 'form-check-input', }),
            'local_part': forms.TextInput(attrs={'placeholder': 'Enter local part', 'class': 'form-control', }),
            'password': forms.PasswordInput(attrs={'placeholder': 'Enter password', 'class': 'form-control', }),
            'quota': forms.NumberInput(attrs={'class': 'form-control', }),
            'is_trial': forms.CheckboxInput(attrs={'type': 'checkbox', 'class': 'form-check-input', }),
            'plan_id': forms.TextInput(attrs={'placeholder': 'Enter plan ID', 'class': 'form-control', }),
            'user_name': forms.TextInput(attrs={'placeholder': 'Enter user name', 'class': 'form-control', }),
        }


class RTFGetAliasFormMode(RTFForm):
    RTFForm.Meta.fields = ['mailbox']
    method = forms.CharField(widget=forms.HiddenInput(), initial='get_mailbox_aliases')


class RTFCreateAliasFormMode(RTFForm):
    RTFForm.Meta.fields = ['alias', 'domain_name', 'mailbox']
    RTFForm.Meta.widgets['domain_name'] = forms.HiddenInput(attrs={'value': 'value', })
    method = forms.CharField(widget=forms.HiddenInput(), initial='create_mailbox_alias')


class RTFUpdateAliasFormMode(RTFForm):
    RTFForm.Meta.fields = ['domain_name', 'mailbox', 'old_alias', 'new_alias']
    RTFForm.Meta.widgets['mailbox'] = forms.HiddenInput()
    method = forms.CharField(widget=forms.HiddenInput(), initial='update_mailbox_alias')


class RTFDeleteAliasFormMode(RTFForm):
    RTFForm.Meta.fields = ['alias']
    method = forms.CharField(widget=forms.HiddenInput(), initial='delete_mailbox_alias')
    active_mailbox = forms.CharField(widget=forms.HiddenInput(), initial='')


class RTFCreateMailboxFormMode(RTFForm):
    RTFForm.Meta.fields = ['domain_name', 'is_active', 'local_part', 'password', 'quota']
    RTFForm.Meta.widgets['domain_name'] = forms.TextInput(
        attrs={'placeholder': 'Domain name', 'class': 'form-control', })
    method = forms.CharField(widget=forms.HiddenInput(), initial='create_mailbox')


class RTFDeleteMailboxFormMode(RTFForm):
    RTFForm.Meta.fields = ['mailbox']
    RTFForm.Meta.widgets['mailbox'] = forms.TextInput(
        attrs={'placeholder': 'Enter mailbox', 'class': 'form-control', })
    method = forms.CharField(widget=forms.HiddenInput(), initial='delete_mailbox')


class RTFGetMailboxInfoFormMode(RTFForm):
    RTFForm.Meta.fields = ['mailbox']
    method = forms.CharField(widget=forms.HiddenInput(), initial='get_mailbox_info')


class RTFCreateDomainFormMode(RTFForm):
    RTFForm.Meta.fields = ['domain_name', 'is_trial', 'plan_id', 'user_name']
    RTFForm.Meta.widgets['domain_name'] = forms.TextInput(
        attrs={'placeholder': 'Domain name', 'class': 'form-control',})
    method = forms.CharField(widget=forms.HiddenInput(), initial='create_domain')


class RTFDeleteDomainFormMode(RTFForm):
    RTFForm.Meta.fields = ['domain_name']
    method = forms.CharField(widget=forms.HiddenInput(), initial='delete_domain')


class RTFGetDomainInfoFormMode(RTFForm):
    RTFForm.Meta.fields = ['domain_name']
    method = forms.CharField(widget=forms.HiddenInput(), initial='get_domain_info')
