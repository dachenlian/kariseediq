import csv

from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.http import HttpResponse


from core.models import Entry
from .forms import UpdateEntryForm


class IndexListView(ListView):
    model = Entry
    paginate_by = 100
    context_object_name = 'entries'
    template_name = 'core/index.html'
    ordering = ['-time']


class EntryUpdateView(UpdateView):
    form_class = UpdateEntryForm
    template_name = 'core/update.html'
    model = Entry

    # def get_initial(self):
    #     print(self.kwargs.get('pk'))
    #     entry = get_object_or_404(Entry, id=self.kwargs.get('pk'))
    #     initial = model_to_dict(entry)
    #     return initial


class SearchResultsListView(ListView):
    model = Entry
    paginate_by = 50
    context_object_name = 'entries'
    template_name = 'core/index.html'

    def get_queryset(self):
        item_filter = self.request.GET.get('itemFilter', "")
        item_name = self.request.GET.get('itemName', "")

        self.request.session['item_filter'] = item_filter
        self.request.session['item_name'] = item_name

        if item_filter == 'startswith':
            query = Entry.objects.filter(itemName__startswith=item_name)
        elif item_filter == 'endswith':
            query = Entry.objects.filter(itemName__endswith=item_name)
        else:
            query = Entry.objects.filter(itemName__contains=item_name)

        self.request.session['queryset'] = query.values(UpdateEntryForm.Meta.fields)
        return query.order_by('-time')


def output_search_to_csv(request):
    queryset = request.session.get('item_filter')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="search_results.csv"'

    writer = csv.writer(response)
    writer.writerow(Entry._meta.get_fields())
