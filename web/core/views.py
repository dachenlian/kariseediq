import csv
import logging
import re

from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.views.generic import View, DeleteView, UpdateView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.utils.encoding import escape_uri_path

from .forms import HeadwordForm, SenseForm, SenseUpdateForm, ExampleFormset, PhraseFormset
from core.models import Headword, Sense
from core import utils

logger = logging.getLogger(__name__)
print(logger)


class IndexListView(ListView):
    model = Headword
    paginate_by = 100
    context_object_name = 'headwords'
    template_name = 'core/index.html'

    def get_queryset(self):
        # return Headword.objects.prefetch_related('senses').filter(senses__gt=1)
        # return Headword.objects.prefetch_related('senses').annotate(senses_count=Count('senses'))\
        #     .filter(senses_count__gt=1)
        return Headword.objects.order_by('only_letters').prefetch_related('senses')


class SearchResultsListView(ListView):
    model = Headword
    paginate_by = 100
    context_object_name = 'headwords'
    template_name = 'core/index.html'

    def get_queryset(self):
        logger.debug(self.request.GET)
        reset = self.request.GET.get('search_reset')
        if reset:
            logger.debug('Resetting queryset!')
            self.request.session.pop('search_root', False)
            self.request.session.pop('history_list', False)
            qs = Headword.objects.all().prefetch_related('senses')
        else:
            qs = self.request.session.get('queryset')

        search_root = self.request.GET.get('search_root', "")
        if search_root:
            if search_root == 'exclude':
                logger.debug('Filtering roots.')
                qs = qs.filter(is_root=False)
            elif search_root == 'only':
                logger.debug('Only including roots.')
                qs = qs.filter(is_root=True)

            self.request.session['search_root'] = search_root
        search_filter = self.request.GET.get('search_filter', "")
        search_name = self.request.GET.get('search_name', "")

        self.request.session['search_filter'] = search_filter
        self.request.session['search_name'] = search_name

        if search_filter == 'startswith':
            qs = qs.filter(Q(headword__istartswith=search_name) |
                           Q(senses__meaning__istartswith=search_name) |
                           Q(variant__istartswith=search_name)
                           )
        elif search_filter == 'endswith':
            qs = qs.filter(Q(headword__iendswith=search_name) |
                           Q(senses__meaning__iendswith=search_name) |
                           Q(variant__iendswith=search_name)
                           )
        else:
            qs = qs.filter(Q(headword__icontains=search_name) |
                           Q(senses__meaning__icontains=search_name) |
                           Q(variant__icontains=search_name)
                           )

        qs = qs.order_by('only_letters').distinct()

        self.request.session['queryset'] = qs
        utils.gen_query_history(self.request)

        return qs


class HeadwordUpdateView(View):
    template_name = 'core/update_headword.html'
    success_message = 'Headword successfully updated!'

    def get(self, request, *args, **kwargs):
        headword = Headword.objects.get(headword=kwargs.get('hw'))
        form = HeadwordForm(instance=headword)
        context = {'form': form}
        return render(self.request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        headword = get_object_or_404(Headword, headword=kwargs.get('hw'))
        form = HeadwordForm(instance=headword, data=request.POST)
        if form.is_valid():
            headword = form.save()
            messages.success(request, self.success_message)
            return redirect(headword)
        else:
            messages.error(request, 'Something happened. Please try again.')
            logger.debug(form.errors)
            return redirect(headword)


class SenseCreateView(View):
    template_name = 'core/create_sense.html'
    success_message = 'New entry saved!'

    def get(self, request, *args, **kwargs):
        sense_form = SenseForm()
        example_formset = ExampleFormset()
        phrase_formset = PhraseFormset()
        context = {
            'form': sense_form,
            'example_formset': example_formset,
            'phrase_formset': phrase_formset
        }
        return render(self.request, template_name=self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        updated_request = request.POST.copy()
        sense_form = SenseForm(updated_request)
        example_formset = ExampleFormset(updated_request)
        phrase_formset = PhraseFormset(updated_request)

        headword = sense_form.data['headword']
        headword, created = Headword.objects.get_or_create(headword=headword,
                                                           defaults={
                                                               'only_letters': utils.only_letters(headword)
                                                           })
        sense_form.data['headword'] = headword
        sense_form.data['headword_sense_no'] = headword.senses.count() + 1
        if sense_form.is_valid() and example_formset.is_valid() and phrase_formset.is_valid():

            sense = sense_form.save(commit=False)
            sense.headword = headword
            sense.save()

            examples = example_formset.save(commit=False)

            for example in examples:
                example.sense = sense
                example.save()

            phrases = phrase_formset.save(commit=False)
            for phrase in phrases:
                phrase.sense = sense
                phrase.save()

            messages.success(request, self.success_message)
            if created:
                messages.info(request, 'New headword created. Please update info.')
                return redirect(headword)
            return redirect(sense)
        logger.error(sense_form.errors)
        logger.error(phrase_formset.errors)
        logger.error(example_formset.errors)
        messages.error(request, 'An error occurred. Please try again.')
        return redirect('core:create_sense')


class SenseUpdateView(View):

    def get(self, request, *args, **kwargs):
        headword = get_object_or_404(Headword, headword=kwargs.get('hw'))
        sense = get_object_or_404(Sense, headword=headword, headword_sense_no=kwargs.get('sense'))
        sense_form = SenseUpdateForm(instance=sense)
        example_formset = ExampleFormset(instance=sense)
        phrase_formset = PhraseFormset(instance=sense)

        context = {
            'headword': headword,
            'headword_sense_no': sense.headword_sense_no,
            'form': sense_form,
            'example_formset': example_formset,
            'phrase_formset': phrase_formset,
        }
        return render(self.request, template_name='core/update_sense.html', context=context)

    def post(self, request, *args, **kwargs):
        logger.debug('Inside Update view.')

        headword = get_object_or_404(Headword, headword=kwargs.get('hw'))
        sense = get_object_or_404(Sense, headword=headword, headword_sense_no=kwargs.get('sense'))
        sense_form = SenseUpdateForm(instance=sense, data=request.POST)
        example_formset = ExampleFormset(instance=sense, data=request.POST)
        phrase_formset = PhraseFormset(instance=sense, data=request.POST)

        if sense_form.is_valid() and example_formset.is_valid() and phrase_formset.is_valid():
            logger.debug(sense_form.cleaned_data)
            sense = sense_form.save()
            example_formset.save()
            phrase_formset.save()
            messages.success(request, "Sense updated!")
        else:
            logger.warning(sense_form.errors)
            logger.warning(example_formset.errors)
            logger.warning(phrase_formset.errors)
            messages.error(request, 'An error occurred. Please try again.')
        return redirect(sense)


class SenseDeleteView(DeleteView):
    model = Sense
    success_url = reverse_lazy('core:index')
    success_message = 'Entry successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(request, self.success_message)
        return super().delete(request, *args, **kwargs)

    def get_object(self, queryset=None):
        headword = get_object_or_404(Headword, headword=self.kwargs.get('hw'))
        return get_object_or_404(self.model, headword=headword, headword_sense_no=self.kwargs.get('sense'))


class PendingListView(ListView):
    model = Headword
    paginate_by = 1000
    context_object_name = 'senses'
    template_name = 'core/pending.html'

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            logger.debug('Ajax request received!')
            queryset = self.get_queryset()
            return JsonResponse({'pending_count': len(queryset)})
        else:
            return super().get(request, *args, **kwargs)

    def get_queryset(self):
        roots = Sense.objects.all().distinct().values('root')
        headwords = Headword.objects.filter(is_root=True).values_list('headword', flat=True).distinct()
        roots_without_entries = roots.difference(headwords).values_list('headword', flat=True)
        roots_without_entries = sorted(filter(bool, roots_without_entries))
        roots_without_entries = Sense.objects.filter(root__in=roots_without_entries).order_by('root')
        return roots_without_entries


class RootAutoComplete(View):
    def get(self, *args, **kwargs):
        logger.debug('Autocomplete Called')
        q = self.request.GET.get('q')
        logger.debug(q)
        if q:
            queryset = Headword.objects.filter(
                Q(headword__icontains=q) &
                Q(is_root=True)). \
                values_list('headword', flat=True)
        else:
            queryset = None

        logger.debug(queryset)

        return JsonResponse(list(queryset), safe=False)


class RootSenseAutoComplete(View):
    def get(self, *args, **kwargs):
        logger.debug('Autocomplete Called')
        q = self.request.GET.get('q')
        logger.debug(q)
        if q:
            hw = Headword.objects.filter(
                Q(headword__icontains=q) &
                Q(is_root=True)).prefetch_related('senses').first()
            hw = utils.build_autocomplete_response(hw)
        else:
            queryset = None

        logger.debug(hw)

        return JsonResponse(list(queryset), safe=False)


class HeadwordAutoComplete(View):
    def get(self, *args, **kwargs):
        logger.debug('Item name autocomplete called')
        q = self.request.GET.get('q')
        logger.debug(q)
        if q:
            queryset = Headword.objects.filter(headword__icontains=q).values_list('headword', flat=True)
        else:
            queryset = None

        logger.debug(queryset)

        return JsonResponse(list(queryset), safe=False)


def export_search_to_csv(request, query_idx):
    query_dict = request.session.get('history_list')[query_idx]

    queryset = query_dict['queryset']
    query_str = query_dict['query_str']
    # some chars aren't allowed in filenames
    query_str = query_str.replace(' | ', '_')
    query_str = re.sub(r'<strong>(.+?)</strong>:', r'\1=', query_str)
    filename = escape_uri_path(f'{query_str}.csv')
    logger.debug(query_str)

    queryset = utils.get_related(queryset)
    fieldnames = queryset[0].keys()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()
    for row in queryset:
        writer.writerow(row)
    return response


def get_root_senses(request):
    root = request.GET.get('root', None)
    try:
        headword = Headword.objects.get(headword=root)
    except Headword.DoesNotExist:
        data = {
            'success': False,
            'senses': []
        }
        return JsonResponse(data)
    else:
        senses = [f'({idx}) {s.meaning}' for idx, s in enumerate(headword.senses.all(), 1)]
        data = {
            'success': True,
            'senses': senses
        }
        return JsonResponse(data)
