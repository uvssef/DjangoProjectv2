import json
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods, require_POST

from .services import data_service, stats_service, combinatorics_service, probability_service, distribution_service, chart_service, export_service, visualization_service


def get_common_context(request, active_category):
    """Common context helper for dataset and active sidebar state."""
    dataset = data_service.get_active_dataset(request)
    n = len(dataset)
    mean_preview = sum(dataset) / n if n > 0 else 0.0
    source_name = request.session.get('dataset_source', 'Exemple officiel du cours')

    return {
        'active_category': active_category,
        'dataset': dataset,
        'dataset_count': n,
        'dataset_mean': round(mean_preview, 2),
        'dataset_source': source_name,
        'presets': data_service.PRESET_DATASETS,
    }


# ---------------------------------------------------------------------
# 1. DASHBOARD & DATA MANAGEMENT
# ---------------------------------------------------------------------

def dashboard_view(request):
    ctx = get_common_context(request, 'dashboard')
    dataset = ctx['dataset']

    if dataset and len(dataset) > 0:
        ct = stats_service.calculate_central_tendencies(dataset)
        var = stats_service.calculate_variability(dataset)
        chart_ct = chart_service.plot_central_tendencies(
            dataset, ct['mean']['value'], ct['median']['value'], ct['mode']['value']
        )
        chart_box = chart_service.plot_boxplot(dataset)
    else:
        ct = None
        var = None
        chart_ct = None
        chart_box = None

    ctx.update({
        'ct': ct,
        'var': var,
        'chart_ct': chart_ct,
        'chart_box': chart_box,
    })
    return render(request, 'stat_app/dashboard.html', ctx)


# ---------------------------------------------------------------------
# NOUVELLE SECTION : VISUALISATION DES DONNÉES (LES 7 GRAPHIQUES OBLIGATOIRES)
# ---------------------------------------------------------------------

def data_visualizations_view(request):
    """
    Dedicated view for the 7 standard statistical and probability charts:
    1. Histogramme (distribution des valeurs en classes)
    2. Boxplot (dispersion, médiane, quartiles, outliers)
    3. Scatter plot (nuage de points séquentiel / lag / régression)
    4. Courbe - Line Chart (trajectoire, variations, moyenne mobile)
    5. Diagramme en barres (effectifs / pourcentages des modalités)
    6. Graphique de densité - KDE (estimation continue de f(x))
    7. Heatmap de corrélation (matrice des dépendances de Pearson)
    """
    ctx = get_common_context(request, 'visualizations')
    dataset = ctx['dataset']
    chart_id = request.GET.get('chart', request.GET.get('type', 'histogram'))

    # Chart metadata catalog for UI selector
    chart_catalog = list(visualization_service.CHART_METADATA.values())

    # Collect options from query parameters
    options = {
        'bins': request.GET.get('bins', 'auto'),
        'show_kde': request.GET.get('show_kde', 'true'),
        'show_stats': request.GET.get('show_stats', 'true'),
        'orientation': request.GET.get('orientation', 'horizontal' if chart_id == 'boxplot' else 'vertical'),
        'show_points': request.GET.get('show_points', 'true'),
        'mode': request.GET.get('mode', 'index'),
        'show_trend': request.GET.get('show_trend', 'true'),
        'show_sigma': request.GET.get('show_sigma', 'true'),
        'style': request.GET.get('style', 'line_markers'),
        'rolling': request.GET.get('rolling', ''),
        'fill_area': request.GET.get('fill_area', 'true'),
        'show_mean': request.GET.get('show_mean', 'true'),
        'freq_type': request.GET.get('freq_type', 'absolute'),
        'sort_by': request.GET.get('sort_by', 'value'),
        'highlight_mode': request.GET.get('highlight_mode', 'true'),
        'bandwidth': request.GET.get('bandwidth', 'standard'),
        'show_rug': request.GET.get('show_rug', 'true'),
        'compare_normal': request.GET.get('compare_normal', 'true'),
        'fill': request.GET.get('fill', 'true'),
        'lags': request.GET.get('lags', '4'),
        'cmap': request.GET.get('cmap', 'coolwarm'),
        'annot': request.GET.get('annot', 'true'),
        'theme': request.GET.get('theme', 'indigo'),
    }

    multi_columns = request.session.get('multi_column_data', None)

    active_result = None
    all_results = []

    if dataset and len(dataset) > 0:
        if chart_id == 'all':
            for cid in visualization_service.CHART_METADATA.keys():
                res = visualization_service.get_visualization(cid, dataset, options, multi_columns)
                all_results.append(res)
        else:
            active_result = visualization_service.get_visualization(chart_id, dataset, options, multi_columns)
    else:
        active_result = {
            'success': False,
            'chart_id': chart_id,
            'title': visualization_service.CHART_METADATA.get(chart_id, {}).get('title', 'Graphique'),
            'icon': visualization_service.CHART_METADATA.get(chart_id, {}).get('icon', '📊'),
            'meta': visualization_service.CHART_METADATA.get(chart_id, visualization_service.CHART_METADATA['histogram']),
            'error': "Aucune observation disponible pour générer ce graphique. Veuillez saisir des nombres ou importer un fichier Excel."
        }

    ctx.update({
        'chart_id': chart_id,
        'chart_catalog': chart_catalog,
        'current_chart_meta': visualization_service.CHART_METADATA.get(chart_id, visualization_service.CHART_METADATA['histogram']),
        'active_result': active_result,
        'all_results': all_results,
        'options': options,
    })
    return render(request, 'stat_app/data_visualizations.html', ctx)


def download_chart_png(request, chart_name):
    """
    Stream requested chart as a downloadable PNG image for any of the 7 types.
    """
    dataset = data_service.get_active_dataset(request)
    if not dataset or len(dataset) == 0:
        return HttpResponse("Aucune donnée disponible pour générer l'image.", status=400)

    options = {
        'bins': request.GET.get('bins', 'auto'),
        'show_kde': request.GET.get('show_kde', 'true'),
        'show_stats': request.GET.get('show_stats', 'true'),
        'orientation': request.GET.get('orientation', 'horizontal' if chart_name == 'boxplot' else 'vertical'),
        'show_points': request.GET.get('show_points', 'true'),
        'mode': request.GET.get('mode', 'index'),
        'show_trend': request.GET.get('show_trend', 'true'),
        'show_sigma': request.GET.get('show_sigma', 'true'),
        'style': request.GET.get('style', 'line_markers'),
        'rolling': request.GET.get('rolling', ''),
        'fill_area': request.GET.get('fill_area', 'true'),
        'show_mean': request.GET.get('show_mean', 'true'),
        'freq_type': request.GET.get('freq_type', 'absolute'),
        'sort_by': request.GET.get('sort_by', 'value'),
        'highlight_mode': request.GET.get('highlight_mode', 'true'),
        'bandwidth': request.GET.get('bandwidth', 'standard'),
        'show_rug': request.GET.get('show_rug', 'true'),
        'compare_normal': request.GET.get('compare_normal', 'true'),
        'fill': request.GET.get('fill', 'true'),
        'lags': request.GET.get('lags', '4'),
        'cmap': request.GET.get('cmap', 'coolwarm'),
        'annot': request.GET.get('annot', 'true'),
        'theme': request.GET.get('theme', 'indigo'),
    }

    multi_columns = request.session.get('multi_column_data', None)

    # Legacy mapping if old chart names requested
    legacy_map = {
        'distribution': 'kde',
        'pie': 'bars',
    }
    normalized_name = legacy_map.get(chart_name, chart_name)

    res = visualization_service.get_visualization(normalized_name, dataset, options, multi_columns)
    if not res.get('success'):
        return HttpResponse(res.get('error', 'Erreur de génération du graphique'), status=400)

    raw_bytes = res.get('raw_bytes')
    filename = f"statlab_{normalized_name}.png"
    response = HttpResponse(raw_bytes, content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# ---------------------------------------------------------------------
# 2. TENDANCES CENTRALES
# ---------------------------------------------------------------------

def central_tendencies_view(request):
    ctx = get_common_context(request, 'central')
    dataset = ctx['dataset']

    if dataset and len(dataset) > 0:
        ct = stats_service.calculate_central_tendencies(dataset)
        chart_ct = chart_service.plot_central_tendencies(
            dataset, ct['mean']['value'], ct['median']['value'], ct['mode']['value']
        )
    else:
        ct = None
        chart_ct = None

    ctx.update({
        'ct': ct,
        'chart_ct': chart_ct,
    })
    return render(request, 'stat_app/central_tendencies.html', ctx)


# ---------------------------------------------------------------------
# 3. TENDANCES DE VARIABILITÉ
# ---------------------------------------------------------------------

def variability_view(request):
    ctx = get_common_context(request, 'variability')
    dataset = ctx['dataset']

    if dataset and len(dataset) > 0:
        var = stats_service.calculate_variability(dataset)
        chart_var = chart_service.plot_variability(dataset, var['mean'], var['std_dev']['val_sample'])
        chart_box = chart_service.plot_boxplot(dataset)
    else:
        var = None
        chart_var = None
        chart_box = None

    ctx.update({
        'var': var,
        'chart_var': chart_var,
        'chart_box': chart_box,
    })
    return render(request, 'stat_app/variability.html', ctx)


# ---------------------------------------------------------------------
# 4. ANALYSE COMBINATOIRE
# ---------------------------------------------------------------------

def combinatorics_view(request):
    ctx = get_common_context(request, 'combinatorics')

    try:
        n = int(request.GET.get('n', 8))
        k = int(request.GET.get('k', 3))
    except (ValueError, TypeError):
        n, k = 8, 3

    n = max(1, min(n, 30))
    k = max(0, min(k, n))

    comb_results = combinatorics_service.get_all_combinatorics(n, k)
    chart_growth = chart_service.plot_combinatorics_comparison(n)

    ctx.update({
        'n': n,
        'k': k,
        'comb': comb_results,
        'chart_growth': chart_growth,
    })
    return render(request, 'stat_app/combinatorics.html', ctx)


# ---------------------------------------------------------------------
# 5. PROBABILITÉ DISCRÈTE (URNE)
# ---------------------------------------------------------------------

def discrete_probability_view(request):
    ctx = get_common_context(request, 'discrete')

    balls = {
        'Rouge': int(request.GET.get('rouge', 5)),
        'Bleue': int(request.GET.get('bleue', 3)),
        'Verte': int(request.GET.get('verte', 2)),
        'Jaune': int(request.GET.get('jaune', 0)),
    }

    urn_data = probability_service.calculate_discrete_urn(balls)
    chart_urn = chart_service.plot_urn_probabilities(urn_data['balls_distribution'])

    ctx.update({
        'balls': balls,
        'urn': urn_data,
        'chart_urn': chart_urn,
    })
    return render(request, 'stat_app/discrete_probability.html', ctx)


# ---------------------------------------------------------------------
# 6. PROBABILITÉ CONDITIONNELLE
# ---------------------------------------------------------------------

def conditional_probability_view(request):
    ctx = get_common_context(request, 'conditional')

    try:
        p_b = float(request.GET.get('p_b', 0.01))
        p_a_given_b = float(request.GET.get('p_a_given_b', 0.95))
        p_a_given_not_b = float(request.GET.get('p_a_given_not_b', 0.05))
        venn_mode = request.GET.get('venn_mode', 'A_inter_B')
    except (ValueError, TypeError):
        p_b, p_a_given_b, p_a_given_not_b = 0.01, 0.95, 0.05
        venn_mode = 'A_inter_B'

    cond_data = probability_service.calculate_conditional_probabilities(p_b, p_a_given_b, p_a_given_not_b)
    chart_venn = chart_service.plot_venn_diagram(venn_mode)
    chart_tree = chart_service.plot_probability_tree(cond_data['p_b'], cond_data['p_a_given_b'], cond_data['p_a_given_not_b'])

    ctx.update({
        'cond': cond_data,
        'venn_mode': venn_mode,
        'chart_venn': chart_venn,
        'chart_tree': chart_tree,
    })
    return render(request, 'stat_app/conditional_probability.html', ctx)


# ---------------------------------------------------------------------
# 7. LOIS DE PROBABILITÉ
# ---------------------------------------------------------------------

def distributions_view(request):
    ctx = get_common_context(request, 'distributions')

    law_id = request.GET.get('law', 'normal')

    if law_id == 'bernoulli':
        p = float(request.GET.get('p', 0.6))
        law_data = distribution_service.calculate_bernoulli(p)
        chart_law = chart_service.plot_discrete_dist('bernoulli', {'p': p})
    elif law_id == 'binomial':
        n = int(request.GET.get('n', 10))
        p = float(request.GET.get('p', 0.5))
        k = int(request.GET.get('k', 5))
        law_data = distribution_service.calculate_binomial(n, p, k)
        chart_law = chart_service.plot_discrete_dist('binomial', {'n': n, 'p': p}, k_highlight=k)
    elif law_id == 'uniform_discrete':
        a = int(request.GET.get('a', 1))
        b = int(request.GET.get('b', 6))
        k = int(request.GET.get('k', 3))
        law_data = distribution_service.calculate_uniform_discrete(a, b, k)
        chart_law = chart_service.plot_discrete_dist('uniform_discrete', {'a': a, 'b': b}, k_highlight=k)
    elif law_id == 'poisson':
        lambd = float(request.GET.get('lambda', 4.0))
        k = int(request.GET.get('k', 3))
        law_data = distribution_service.calculate_poisson(lambd, k)
        chart_law = chart_service.plot_discrete_dist('poisson', {'lambda': lambd}, k_highlight=k)
    elif law_id == 'uniform_continuous':
        a = float(request.GET.get('a', 0.0))
        b = float(request.GET.get('b', 10.0))
        x1 = float(request.GET.get('x1', 2.0))
        x2 = float(request.GET.get('x2', 6.0))
        law_data = distribution_service.calculate_uniform_continuous(a, b, x1, x2)
        chart_law = chart_service.plot_continuous_dist('uniform_continuous', {'a': a, 'b': b, 'x1': x1, 'x2': x2})
    elif law_id == 'exponential':
        lambd = float(request.GET.get('lambda', 0.5))
        x = float(request.GET.get('x', 2.0))
        law_data = distribution_service.calculate_exponential(lambd, x)
        chart_law = chart_service.plot_continuous_dist('exponential', {'lambda': lambd, 'x': x})
    elif law_id == 'standard_normal':
        z = float(request.GET.get('z', 1.96))
        law_data = distribution_service.calculate_standard_normal(z)
        chart_law = chart_service.plot_z_score_rule(z)
    else:
        law_id = 'normal'
        mu = float(request.GET.get('mu', 100.0))
        sigma = float(request.GET.get('sigma', 15.0))
        x = float(request.GET.get('x', 115.0))
        r1 = float(request.GET.get('range_x1', 85.0))
        r2 = float(request.GET.get('range_x2', 115.0))
        law_data = distribution_service.calculate_normal(mu, sigma, x, r1, r2)
        chart_law = chart_service.plot_continuous_dist('normal', {'mu': mu, 'sigma': sigma, 'range_x1': r1, 'range_x2': r2})

    ctx.update({
        'current_law_id': law_id,
        'law': law_data,
        'chart_law': chart_law,
    })
    return render(request, 'stat_app/distributions.html', ctx)


# ---------------------------------------------------------------------
# DATA MANAGEMENT ACTIONS (API / POST)
# ---------------------------------------------------------------------

@require_POST
def api_update_manual_data(request):
    """Handle raw text manual input."""
    raw_text = request.POST.get('data_text', '')
    valid_nums, invalid_tokens = data_service.parse_manual_input(raw_text)

    if len(valid_nums) > 0:
        data_service.set_active_dataset(request, valid_nums, source_name="Saisie manuelle")
        msg = f"{len(valid_nums)} valeur(s) importée(s) avec succès."
        if invalid_tokens:
            msg += f" ({len(invalid_tokens)} valeur(s) ignorée(s) car invalides : {', '.join(invalid_tokens[:5])})"
        return JsonResponse({'success': True, 'count': len(valid_nums), 'message': msg})
    else:
        return JsonResponse({'success': False, 'error': "Aucun nombre valide n'a été détecté dans votre saisie."})


@require_POST
def api_add_value(request):
    """Add a single number to the active dataset."""
    val_str = request.POST.get('value', '').replace(',', '.')
    try:
        val = float(val_str)
        updated = data_service.add_value(request, val)
        return JsonResponse({'success': True, 'count': len(updated), 'data': updated})
    except ValueError:
        return JsonResponse({'success': False, 'error': "Valeur numérique invalide."})


@require_POST
def api_edit_value(request):
    """Edit value at given index."""
    try:
        idx = int(request.POST.get('index', -1))
        val = float(request.POST.get('value', '').replace(',', '.'))
        updated = data_service.edit_value(request, idx, val)
        return JsonResponse({'success': True, 'count': len(updated), 'data': updated})
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'error': "Paramètres de modification invalides."})


@require_POST
def api_delete_value(request):
    """Delete value at given index."""
    try:
        idx = int(request.POST.get('index', -1))
        updated = data_service.delete_value(request, idx)
        return JsonResponse({'success': True, 'count': len(updated), 'data': updated})
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'error': "Index invalide."})


@require_POST
def api_clear_data(request):
    """Clear entire active dataset."""
    data_service.clear_dataset(request)
    return JsonResponse({'success': True, 'count': 0})


@require_POST
def api_load_preset(request):
    """Load a predefined educational preset."""
    preset_key = request.POST.get('preset', 'cours')
    loaded = data_service.reset_to_default(request, preset_key)
    return JsonResponse({'success': True, 'count': len(loaded), 'data': loaded})


@require_POST
def api_upload_excel_preview(request):
    """Inspect uploaded file and return columns + preview."""
    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return JsonResponse({'success': False, 'error': "Aucun fichier reçu."})

    res = data_service.inspect_uploaded_file(uploaded_file)
    return JsonResponse(res)


@require_POST
def api_confirm_excel_import(request):
    """Extract chosen column from uploaded file and set as active dataset."""
    uploaded_file = request.FILES.get('file')
    col_name = request.POST.get('column_name')

    if not uploaded_file or not col_name:
        return JsonResponse({'success': False, 'error': "Fichier ou nom de colonne manquant."})

    data, err = data_service.extract_column_data_from_file(uploaded_file, col_name)
    if err:
        return JsonResponse({'success': False, 'error': err})

    data_service.set_active_dataset(request, data, source_name=f"Fichier {uploaded_file.name} [{col_name}]")
    return JsonResponse({'success': True, 'count': len(data), 'message': f"{len(data)} valeurs importées de la colonne '{col_name}'."})


def api_export_excel(request):
    """Download current statistical results as an Excel workbook."""
    dataset = data_service.get_active_dataset(request)
    if not dataset or len(dataset) == 0:
        return HttpResponse("Aucune donnée à exporter.", status=400)

    excel_bytes = export_service.export_stats_to_excel(dataset)
    response = HttpResponse(
        excel_bytes,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="statistiques_resultats.xlsx"'
    return response
