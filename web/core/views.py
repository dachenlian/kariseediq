from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from core.models import Entry


class IndexListView(ListView):
    model = Entry
    paginate_by = 100
    context_object_name = 'entries'
    template_name = 'core/index.html'
    ordering = ['-time']

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total'] = Entry.objects.all().count()
        return context


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

    def get_queryset(self):
        item_filter = self.request.GET.get('itemFilter')
        item_name = self.request.GET.get('itemName')

        if item_filter == 'contains':
            return super().get_queryset(itemName__contains=item_name)
        elif item_filter == 'startswith':
            return super().get_queryset(itemName__startswith=item_name)
        elif item_filter == 'endswith':
            return super().get_queryset(itemName__endswith=item_name)

