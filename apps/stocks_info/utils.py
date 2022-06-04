import json
import requests
from django.shortcuts import render

from django.conf import settings


class RequestToFacade:
    __slots__ = ('method', 'data')

    def __init__(self, method, data):
        self.method = method
        self.data = data

    def send_request(self):
        payload = {
            'method': self.method,
            'params': self.data,
            'jsonrpc': '2.0',
            'id': 10,
        }
        response = requests.post(url=settings.FACADE_API_URL, data=json.dumps(payload),
                                 headers={'Authorization': settings.FACADE_API_TOKEN,
                                          "Content-Type": "application/json"}
                                 )
        return response.json()


class FormsRenderInterface:

    def __init__(self, forms, request, post_method=None):
        self.forms = forms  # tuple forms instances
        self.request = request  # request.POST
        self.post_method = post_method  # request method to Facade from request.POST.get('method')

    def get_forms_render(self):

        render_forms = {}
        for form in self.forms:
            method = form()['method'].initial
            render_forms[method] = form()
        return render_forms

    def post_forms_render(self):

        for form in self.forms:
            method = form()['method'].initial
            if method == self.post_method:
                request_form = form(self.request.POST)
        return request_form



class AliasesRequestToFacadeMixin:
    form_classes = None
    template_name = None
    __allowed_method_names = [
        'get_mailbox_aliases',
        'create_mailbox_alias',
        'update_mailbox_alias',
        'delete_mailbox_alias',
    ]

    @staticmethod
    def payload_preparation(data):
        """ - convert dictionary keys to camel case view and return payload,
            - take 'domain_name' from 'mailbox' and set to the payload
            - converting data to the correct schema """

        # delete field 'method' from payload
        del data['method']

        payload = {}
        for key in data:
            i = key.replace('_', ' ').title().replace(' ', '')
            payload[i] = data[key]
        if 'DomainName' in payload:
            payload['DomainName'] = payload['Mailbox'].split('@')[1]
        return payload

    @staticmethod
    def check_if_alias_is_not_repeated(payload, data, method):
        """ check if the 'alias' is not repeated """
        current_alias = data['Alias'] if method == 'create_mailbox_alias' else data['NewAlias']
        get_aliases = RequestToFacade('get_mailbox_aliases', payload).send_request()
        aliases = get_aliases['result']
        if any(row['Alias'] == current_alias for row in aliases):
            error_message = 'Alias ' + current_alias + ' is already exist for mailbox ' + data['Mailbox']
            return False, {'error': error_message}
        else:
            return True,

    def check_if_mailbox_exist(self, method, data):
        """ check if the 'mailbox' is existed """
        if method == 'delete_mailbox_alias' or method == 'get_mailbox_aliases':
            return True,
        else:
            payload = {'Mailbox': data['Mailbox']}
            check_mailbox = RequestToFacade('get_mailbox_info', payload).send_request()
            if 'result' in check_mailbox and len(check_mailbox['result']) > 0:
                alias_existence = self.check_if_alias_is_not_repeated(payload, data, method)
                if alias_existence[0]:
                    return True,
                else:
                    return False, alias_existence[1]
            elif 'error' in check_mailbox:
                return False, check_mailbox
            else:
                return False, {'error': 'Error'}

    # def forms_render(self):
    #     """ rendering forms from dict 'form_classes' that received from view """
    #     form = {}
    #     for key in self.form_classes:
    #         form[key] = self.form_classes[key]()
    #     return form

    def get(self, request, *args, **kwargs):
        # form = self.forms_render()
        form = FormsRenderInterface(self.form_classes, request).get_forms_render()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        # defining request method to facade from hidden field of post form
        method = request.POST.get('method')

        # rendering forms
        # form = self.forms_render()
        form = FormsRenderInterface(self.form_classes, request, method).get_forms_render()

        # setting the request data to active form
        # request_form = form[method] = self.form_classes[method](request.POST)
        request_form = FormsRenderInterface(self.form_classes, request, method).post_forms_render()

        # clean form fields
        # form[method] = self.form_classes[method]()

        if request_form.is_valid():
            # get method for request to facade
            method = request_form.cleaned_data['method']

            # set active mailbox to render if method 'delete'
            if method == 'delete_mailbox_alias':
                mailbox = request_form.cleaned_data['active_mailbox']
                del request_form.cleaned_data['active_mailbox']
            else:
                mailbox = request_form.cleaned_data.get('mailbox', '')

            # set extra_data payload fot render
            extra_data = {
                'mailbox': mailbox,
                'method': method,
                'cleaned_data': request_form.cleaned_data
            }

            # checking if method to facade is allowed
            if method not in self.__allowed_method_names:
                raise AttributeError(
                    "The method name '%s' is not accepted as request method to the PE Facade Infra API" % method)

            # transforming payload data to format of request schema to facade
            data = self.payload_preparation(request_form.cleaned_data)

            # check if the 'mailbox' is existed and the 'alias' is not repeated
            check_mailbox = self.check_if_mailbox_exist(method, data)

            if check_mailbox[0]:
                try:
                    # request to Facade infra API
                    json_response = RequestToFacade(method, data).send_request()
                    return render(request, self.template_name,
                                  {'form': form, 'response': json_response, 'extra_data': extra_data, })
                except requests.exceptions.RequestException as exc:
                    return render(request, self.template_name, {'form': form, 'response': exc, })
            else:
                return render(request, self.template_name, {'form': form, 'response': check_mailbox[1],})
        return render(request, self.template_name, {'form': form,})
