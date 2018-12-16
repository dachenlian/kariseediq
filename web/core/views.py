import csv

from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.http import HttpResponse
from django.shortcuts import get_object_or_404


from core.models import Entry
from .forms import UpdateEntryForm


class IndexListView(ListView):
    model = Entry
    paginate_by = 100
    context_object_name = 'entries'
    template_name = 'core/index.html'
    ordering = ['-created_date']


class EntryUpdateView(UpdateView):
    form_class = UpdateEntryForm
    template_name = 'core/update.html'
    model = Entry

    def get_initial(self):
        print('Inside initial!')
        initial = super().get_initial()
        print(initial)
        tags = list(get_object_or_404(Entry, pk=self.kwargs.get(self.pk_url_kwarg)).tag)
        print(tags)
        initial['tag'] = tags
        print(initial)
        return initial


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

        fields = UpdateEntryForm.Meta.fields
        self.request.session['queryset'] = list(query.values(*fields))
        # print(self.request.session.get('queryset'))
        return query.order_by('created_date')


def export_search_to_csv(request):
    queryset = request.session.get('queryset')
    fieldnames = UpdateEntryForm.Meta.fields

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="search_results.csv"'

    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()
    for row in queryset:
        row['word_class'] = ",".join(row['word_class'])
        row['tag'] = ",".join(row['tag'])
        writer.writerow(row)
    return response

    # return redirect('core:index')
