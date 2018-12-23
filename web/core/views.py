import csv
import logging

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic.list import ListView
from django.views.generic import View

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from core.models import Entry
from .forms import EntryForm, EntryUpdateForm, ExampleFormSet

logger = logging.getLogger(__name__)
print(logger)


class IndexListView(ListView):
    model = Entry
    paginate_by = 100
    context_object_name = 'entries'
    template_name = 'core/index.html'
    ordering = ['-created_date']


class EntryCreateView(View):
    template_name = 'core/create.html'

    def get(self, request, *args, **kwargs):
        entry_form = EntryForm()
        formset = ExampleFormSet()
        context = {
            'form': entry_form,
            'formset': formset
        }
        return render(self.request, template_name=self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        entry_form = EntryForm(request.POST)
        formset = ExampleFormSet(request.POST)
        if entry_form.is_valid() and formset.is_valid():
            entry = entry_form.save()
            formset.save()
            messages.success('New entry saved!')
            return redirect(entry)
        messages.error(request, 'An error occurred. Please try again.')
        return redirect('core:create')


class EntryExampleUpdateView(View):

    def get(self, request, *args, **kwargs):
        entry = get_object_or_404(Entry, pk=kwargs.get('pk'))

        entry_form = EntryUpdateForm(instance=entry)
        formset = ExampleFormSet(instance=entry)

        context = {
            'form': entry_form,
            'formset': formset
        }
        return render(self.request, template_name='core/update.html', context=context)

    def post(self, request, *args, **kwargs):
        logger.debug(request.POST.get('test'))
        entry = get_object_or_404(Entry, pk=kwargs.get('pk'))
        entry_form = EntryUpdateForm(request.POST, instance=entry)
        formset = ExampleFormSet(request.POST, instance=entry)
        if entry_form.is_valid() and formset.is_valid():
            entry_form.save()
            formset.save()
            messages.success(request, "Entry updated!")
        else:
            logger.warning(entry_form.errors)
            logger.warning(formset.errors)

        return redirect(entry)


class SearchResultsListView(ListView):
    model = Entry
    paginate_by = 50
    context_object_name = 'entries'
    template_name = 'core/index.html'

    def get_queryset(self):
        item_filter = self.request.GET.get('item_filter', "")
        item_name = self.request.GET.get('item_name', "")

        self.request.session['item_filter'] = item_filter
        self.request.session['item_name'] = item_name

        if item_filter == 'startswith':
            query = Entry.objects.filter(item_name__startswith=item_name)
        elif item_filter == 'endswith':
            query = Entry.objects.filter(item_name__endswith=item_name)
        else:
            query = Entry.objects.filter(item_name__contains=item_name)

        fields = EntryForm.Meta.fields
        self.request.session['queryset'] = list(query.values(*fields))
        # print(self.request.session.get('queryset'))
        return query.order_by('created_date')


def export_search_to_csv(request):
    queryset = request.session.get('queryset')
    fieldnames = EntryForm.Meta.fields

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="search_results.csv"'

    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()
    for row in queryset:
        row['word_class'] = ",".join(row['word_class'])
        row['tag'] = ",".join(row['tag'])
        writer.writerow(row)
    return response


def validate_item_name(request):
    item_name = request.GET.get('item_name', None)
    data = {
        'is_taken': Entry.objects.filter(item_name__iexact=item_name).exists()
    }
    if data['is_taken']:
        data['error_message'] = 'This item already exists.'
    return JsonResponse(data)
