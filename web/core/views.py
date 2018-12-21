import csv

from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic import View
from django.views.generic.edit import UpdateView, CreateView
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.forms import formset_factory


from core.models import Entry, Example
from .forms import EntryForm, ExampleForm


class IndexListView(ListView):
    model = Entry
    paginate_by = 100
    context_object_name = 'entries'
    template_name = 'core/index.html'
    ordering = ['-created_date']


class EntryCreateView(CreateView):
    template_name = 'core/create.html'
    form_class = EntryForm


class EntryExampleUpdateView(View):

    ExampleFormSet = formset_factory(ExampleForm, extra=2)

    def get(self, request, *args, **kwargs):
        entry = get_object_or_404(Entry, pk=kwargs.get('pk'))

        entry_form = EntryForm(instance=entry)
        formset = self.ExampleFormSet(initial=Example.objects.filter(entry=entry).values())

        context = {
            'entry_form': entry_form,
            'example_form': formset
        }
        return render(self.request, template_name='core/update.html', context=context)

    def post(self, request, *args, **kwargs):
        entry_form = EntryForm(request.POST)
        example_form = ExampleForm(request.POST)


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
