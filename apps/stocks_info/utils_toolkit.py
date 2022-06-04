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


class RTFFormsRender:

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


class RTFFormsGet:
    form_classes = None
    template_name = None

    def get(self, request, *args, **kwargs):
        form = RTFFormsRender(self.form_classes, request).get_forms_render()
        return render(request, self.template_name, {'form': form})


class RTFFormsPost:
    form_classes = None
    template_name = None
    handler_data = None

    def post(self, request, *args, **kwargs):
        method = request.POST.get('method')
        form = RTFFormsRender(self.form_classes, request, method).get_forms_render()
        request_form = RTFFormsRender(self.form_classes, request, method).post_forms_render()
        if request_form.is_valid():
            response = self.handler_request_to_facade(request_form.cleaned_data)
            return render(request, self.template_name,
                          {'form': form, 'response': response, })


class PayloadSerializer:
    def __init__(self, cleaned_data):
        self.cleaned_data = cleaned_data

    def payload_preparation(self):
        payload = {}
        for key in self.cleaned_data:
            i = key.replace('_', ' ').title().replace(' ', '')
            payload[i] = self.cleaned_data[key]
        if 'DomainName' in payload:
            payload['DomainName'] = payload['Mailbox'].split('@')[1]
        return payload


class CheckerIfMailboxExist:

    def __init__(self, mailbox):
        self.mailbox = mailbox

    def check_if_mailbox_exist(self):
        response = RequestToFacade('get_mailbox_info', {'Mailbox': self.mailbox, }).send_request()
        return response


class CheckerIfAliasDoNotRepeated:

    def __init__(self, alias, mailbox):
        self.alias = alias
        self.mailbox = mailbox

    def check_if_mailbox_alias_do_not_repeat(self):
        response = RequestToFacade('get_mailbox_info', {'Mailbox': self.mailbox, }).send_request()
        aliases = response['result']
        if any(row['Alias'] == self.alias for row in aliases):
            error_message = 'Alias ' + self.alias + ' is already exist for mailbox ' + self.mailbox
            return False, {'error': error_message}
        else:
            return True,


class CheckerIfDomainExist:
    pass


class AliasServiceHandler:

    def __init__(self, method, cleaned_data):
        self.cleaned_data = cleaned_data
        self.method = method
        self.handler = self.handler[method](self)

    def handle_get_mailbox_alias(self):
        """
        - check if mailbox exist
        - request to and response from facade with aliases list or error
        """

        return 'Hello Get', self.cleaned_data

    def handle_create_mailbox_alias(self):
        """
        - check if alias don't repeat
        - request to and response from facade that alias created or error
        """
        return 'Hello Create'

    def handle_update_mailbox_alias(self):
        """
        - check if alias don't repeat
        - request to and response from facade that alias updated or error
        """
        return 'Hello Update'

    def handle_delete_mailbox_alias(self):
        """
        - request to and response from facade that alias deleted or error
        """
        return 'Hello Delete'

    handler = {
        'get_mailbox_aliases': handle_get_mailbox_alias,
        'create_mailbox_alias': handle_create_mailbox_alias,
        'update_mailbox_alias': handle_update_mailbox_alias,
        'delete_mailbox_alias': handle_delete_mailbox_alias,
    }


class DomainServiceMixin(RTFFormsGet, RTFFormsPost):

    def handler_request_to_facade(self):
        return 'Domain'

class MailboxServiceMixin(RTFFormsGet, RTFFormsPost):

    def handler_request_to_facade(self):
        return 'Mailbox'

class AliasServiceMixin(RTFFormsGet, RTFFormsPost):

    def handler_request_to_facade(self, cleaned_data):
        method = cleaned_data.pop('method')
        response = AliasServiceHandler(method, cleaned_data).handler
        return response
