from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from core.models import Entry


class IndexListView(ListView):
    model = Entry
    paginate_by = 100
    context_object_name = 'entries'
    template_name = 'core/index.html'
    ordering = ['-time']


class EntryUpdate(UpdateView):
    model = Entry
    fields = ['itemName', 'wordRoot', 'variant', 'toda', 'truku',
              'isRoot', 'isPlant', 'meaning', 'meaningEn',
              'sentence', 'sentenceCh', 'sentenceEn', 'wordClass',
              ]


class SearchResultsListView(ListView):
    model = Entry
    paginate_by = 25
    context_object_name = 'entries'
    template_name = 'core/index.html'

    def get_queryset(self):
        item_filter = self.request.GET.get('itemFilter')
        item_name = self.request.GET.get('itemName')

        if item_filter == 'startswith':
            query = Entry.objects.filter(itemName__startswith=item_name)
        elif item_filter == 'endswith':
            query = Entry.objects.filter(itemName__endswith=item_name)
        else:
            query = Entry.objects.filter(itemName__contains=item_name)

        return query.order_by('-time')
