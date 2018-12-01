from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from core.models import Entry


class SearchListView(ListView):

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
