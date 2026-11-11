import io
import base64
import math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
from scipy import stats
from collections import Counter

# Palette definitions
THEMES = {
    'indigo': {'primary': '#4f46e5', 'light': '#e0e7ff', 'edge': '#312e81', 'accent': '#f59e0b'},
    'emerald': {'primary': '#059669', 'light': '#d1fae5', 'edge': '#064e3b', 'accent': '#6366f1'},
    'amber': {'primary': '#d97706', 'light': '#fef3c7', 'edge': '#78350f', 'accent': '#4f46e5'},
    'slate': {'primary': '#475569', 'light': '#f1f5f9', 'edge': '#0f172a', 'accent': '#0ea5e9'},
}

CHART_METADATA = {
    'histogram': {
        'id': 'histogram',
        'title': 'Histogramme',
        'icon': '📊',
        'subtitle': 'Visualiser la distribution des valeurs en classes d\'intervalles',
        'desc': 'Représente la répartition des observations groupées en intervalles réguliers (bins). Permet d\'analyser la symétrie, l\'étalement et la concentration.',
        'min_obs': 2,
    },
    'boxplot': {
        'id': 'boxplot',
        'title': 'Boxplot',
        'icon': '📦',
        'subtitle': 'Visualiser la dispersion, la médiane et les valeurs extrêmes',
        'desc': 'Boîte à moustaches indiquant le minimum, Q1, la médiane, Q3, le maximum et les valeurs aberrantes (outliers) selon le critère de Tukey.',
        'min_obs': 4,
    },
    'scatter': {
        'id': 'scatter',
        'title': 'Scatter plot',
        'icon': '🟣',
        'subtitle': 'Nuage de points : dispersion séquentielle et tendance',
        'desc': 'Représente chaque observation sous forme de point individuel (index vs valeur ou lag-plot t vs t+1) avec droite de régression et bandes d\'écart-type.',
        'min_obs': 2,
    },
    'line': {
        'id': 'line',
        'title': 'Courbe (Line Chart)',
        'icon': '📉',
        'subtitle': 'Observer la trajectoire et l\'évolution des données',
        'desc': 'Relie les observations successives par une ligne continue. Idéal pour observer les variations séquentielles, les cycles et moyennes mobiles.',
        'min_obs': 2,
    },
    'bars': {
        'id': 'bars',
        'title': 'Diagramme en barres',
        'icon': '📶',
        'subtitle': 'Représenter les effectifs et fréquences de chaque valeur',
        'desc': 'Affiche la fréquence absolue ou relative de chaque modalité distincte. Met en valeur le mode et permet le tri croissant ou décroissant (Pareto).',
        'min_obs': 1,
    },
    'kde': {
        'id': 'kde',
        'title': 'Graphique de densité (KDE)',
        'icon': '🌊',
        'subtitle': 'Estimation continue de la fonction de densité de probabilité',
        'desc': 'Estime de manière lissée et continue la courbe de probabilité sous-jacente des données (KDE) avec possibilité de comparaison à la loi normale théorique.',
        'min_obs': 3,
    },
    'heatmap': {
        'id': 'heatmap',
        'title': 'Heatmap de corrélation',
        'icon': '🔥',
        'subtitle': 'Matrice des coefficients de corrélation linéaire de Pearson',
        'desc': 'Visualise l\'intensité des dépendances linéaires (matrice d\'autocorrélation entre retards successifs ou entre variables importées).',
        'min_obs': 4,
    },
}


def fig_to_base64_and_bytes(fig):
    """Save figure to buffer and return (base64_str, raw_bytes)."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=140, facecolor='#ffffff', edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    raw = buf.getvalue()
    b64 = f"data:image/png;base64,{base64.b64encode(raw).decode('utf-8')}"
    return b64, raw


# ---------------------------------------------------------------------
# 1. HISTOGRAMME
# ---------------------------------------------------------------------

def render_histogram(data, bins='auto', show_kde=True, show_stats=True, theme='indigo'):
    arr = np.array(data, dtype=float)
    n = len(arr)
    t = THEMES.get(theme, THEMES['indigo'])

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.set_facecolor('#ffffff')

    # Bins determination
    unique_vals = np.unique(arr)
    if bins == 'auto' or not bins:
        k_bins = min(20, max(5, int(np.ceil(np.sqrt(n))))) if len(unique_vals) > 6 else len(unique_vals)
    else:
        try:
            k_bins = max(3, min(30, int(bins)))
        except (ValueError, TypeError):
            k_bins = 10

    counts, bin_edges, patches_bars = ax.hist(
        arr, bins=k_bins, color=t['light'], edgecolor=t['primary'], linewidth=1.4, alpha=0.8, rwidth=0.92
    )

    max_c = max(counts) if len(counts) > 0 else 1
    for count, patch in zip(counts, patches_bars):
        if count > 0:
            ax.text(patch.get_x() + patch.get_width() / 2.0, patch.get_height() + 0.02 * max_c,
                    f"{int(count)}", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#1e1b4b')

    mean_val = float(np.mean(arr))
    median_val = float(np.median(arr))

    if show_stats:
        ax.axvline(mean_val, color=t['primary'], linestyle='-', linewidth=2.2, label=f'Moyenne x̄ = {mean_val:.2f}', zorder=5)
        ax.axvline(median_val, color='#10b981', linestyle='--', linewidth=2.2, label=f'Médiane Me = {median_val:.2f}', zorder=5)

    if show_kde and len(unique_vals) > 3:
        ax2 = ax.twinx()
        sns.kdeplot(arr, ax=ax2, color=t['edge'], linewidth=2.0, alpha=0.7)
        ax2.set_ylabel("Densité lissée (KDE)", fontsize=9.5, color='#475569')
        ax2.set_yticks([])

    ax.set_ylim(0, max_c * 1.2)
    ax.set_title(f"Histogramme de Distribution des Valeurs (n = {n} observations)", fontsize=13, fontweight='bold', pad=14, color='#0f172a')
    ax.set_xlabel("Valeurs de la série", fontsize=11, labelpad=8, color='#334155')
    ax.set_ylabel("Effectif (Nombre d'occurrences)", fontsize=11, labelpad=8, color='#334155')
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)
    ax.legend(frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=9, loc='upper right')

    b64, raw_bytes = fig_to_base64_and_bytes(fig)

    # Interpretation
    skewness = (mean_val - median_val)
    if abs(skewness) < 0.05 * (np.std(arr) or 1):
        skew_text = "La distribution est approximativement symétrique (Moyenne ≈ Médiane)."
    elif skewness > 0:
        skew_text = f"La distribution présente une asymétrie à droite (Moyenne {mean_val:.2f} > Médiane {median_val:.2f}), indiquant un étirement causé par des valeurs élevées."
    else:
        skew_text = f"La distribution présente une asymétrie à gauche (Moyenne {mean_val:.2f} < Médiane {median_val:.2f}), tirée vers le bas par des valeurs faibles."

    modal_bin_idx = int(np.argmax(counts))
    modal_interval = f"[{bin_edges[modal_bin_idx]:.2f} ; {bin_edges[modal_bin_idx + 1]:.2f}]"

    interpretation = {
        'title': "Interprétation de l'Histogramme",
        'points': [
            f"**Étendue globale** : Les données s'étendent de {np.min(arr):.2f} à {np.max(arr):.2f} (amplitude = {np.ptp(arr):.2f}).",
            f"**Classe modale** : L'intervalle le plus fréquent est {modal_interval} avec {int(counts[modal_bin_idx])} observations (soit {counts[modal_bin_idx]/n*100:.1f} % du total).",
            f"**Symétrie & Tendance** : {skew_text}",
            f"**Repères clés** : Le centre de gravité se situe à x̄ = {mean_val:.2f}, et 50 % des observations sont inférieures ou égales à Me = {median_val:.2f}."
        ]
    }

    return b64, raw_bytes, interpretation


# ---------------------------------------------------------------------
# 2. BOXPLOT
# ---------------------------------------------------------------------

def render_boxplot(data, orientation='horizontal', show_points=True, theme='indigo'):
    arr = np.array(data, dtype=float)
    n = len(arr)
    t = THEMES.get(theme, THEMES['indigo'])

    q1 = float(np.percentile(arr, 25))
    med = float(np.median(arr))
    q3 = float(np.percentile(arr, 75))
    iqr = q3 - q1

    low_whisker = q1 - 1.5 * iqr
    high_whisker = q3 + 1.5 * iqr
    outliers = arr[(arr < low_whisker) | (arr > high_whisker)]

    vert = (orientation == 'vertical')
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.set_facecolor('#ffffff')

    ax.boxplot(
        arr, vert=vert, patch_artist=True, widths=0.45,
        boxprops=dict(facecolor=t['light'], color=t['primary'], linewidth=2),
        medianprops=dict(color='#059669', linewidth=2.8),
        whiskerprops=dict(color='#475569', linewidth=1.6),
        capprops=dict(color='#475569', linewidth=2),
        flierprops=dict(marker='D', markerfacecolor='#ef4444', markeredgecolor='#991b1b', markersize=8)
    )

    if show_points:
        jitter = np.random.normal(1.0, 0.04, size=n)
        if vert:
            ax.scatter(jitter, arr, color=t['primary'], alpha=0.5, s=35, edgecolor=t['edge'], zorder=4, label='Observations réelles')
        else:
            ax.scatter(arr, jitter, color=t['primary'], alpha=0.5, s=35, edgecolor=t['edge'], zorder=4, label='Observations réelles')

    if vert:
        ax.set_xticks([])
        ax.set_ylabel("Valeurs de la série", fontsize=11, labelpad=8, color='#334155')
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        ax.text(1.28, q1, f'Q1: {q1:.2f}', va='center', color=t['primary'], fontsize=9, fontweight='bold')
        ax.text(0.72, med, f'Me: {med:.2f}', va='center', ha='right', color='#059669', fontsize=9.5, fontweight='bold')
        ax.text(1.28, q3, f'Q3: {q3:.2f}', va='center', color=t['primary'], fontsize=9, fontweight='bold')
    else:
        ax.set_yticks([])
        ax.set_xlabel("Valeurs de la série", fontsize=11, labelpad=8, color='#334155')
        ax.grid(True, axis='x', linestyle='--', alpha=0.7)
        ax.text(q1, 1.32, f'Q1 : {q1:.2f}', ha='center', color=t['primary'], fontsize=9, fontweight='bold')
        ax.text(med, 0.65, f'Médiane : {med:.2f}', ha='center', color='#059669', fontsize=9.5, fontweight='bold')
        ax.text(q3, 1.32, f'Q3 : {q3:.2f}', ha='center', color=t['primary'], fontsize=9, fontweight='bold')

    ax.set_title(f"Boxplot (Boîte à Moustaches) & Analyse des Quartiles (n = {n})", fontsize=13, fontweight='bold', pad=14, color='#0f172a')

    # Summary box
    summary_text = (
        f"Min : {np.min(arr):.2f}\n"
        f"Q1 : {q1:.2f}\n"
        f"Me : {med:.2f}\n"
        f"Q3 : {q3:.2f}\n"
        f"Max : {np.max(arr):.2f}\n"
        f"IQR : {iqr:.2f}\n"
        f"Outliers : {len(outliers)}"
    )
    props = dict(boxstyle='round,pad=0.5', facecolor='#f8fafc', edgecolor='#cbd5e1', alpha=0.95)
    ax.text(0.02, 0.95, summary_text, transform=ax.transAxes, fontsize=8.5, verticalalignment='top', bbox=props, fontfamily='monospace')

    b64, raw_bytes = fig_to_base64_and_bytes(fig)

    outlier_desc = (
        f"**{len(outliers)} valeur(s) aberrante(s)** détectée(s) : {', '.join([f'{x:.2f}' for x in outliers])}."
        if len(outliers) > 0 else
        "**Aucune valeur aberrante** détectée : toutes les observations se trouvent à l'intérieur des moustaches [Q1 - 1.5×IQR ; Q3 + 1.5×IQR]."
    )

    interpretation = {
        'title': "Interprétation du Boxplot",
        'points': [
            f"**Médiane (Q2)** : La valeur centrale est {med:.2f}. Exactement la moitié des données sont en dessous et la moitié au-dessus.",
            f"**Cœur de la distribution (IQR = {iqr:.2f})** : Les 50 % des observations centrales sont comprises entre Q1 ({q1:.2f}) et Q3 ({q3:.2f}).",
            f"**Dispersion des moustaches** : Les moustaches s'étendent de {np.min(arr[arr >= low_whisker]):.2f} à {np.max(arr[arr <= high_whisker]):.2f}.",
            outlier_desc
        ]
    }

    return b64, raw_bytes, interpretation


# ---------------------------------------------------------------------
# 3. SCATTER PLOT (NUAGE DE POINTS)
# ---------------------------------------------------------------------

def render_scatterplot(data, mode='index', show_trend=True, show_sigma=True, theme='indigo'):
    arr = np.array(data, dtype=float)
    n = len(arr)
    t = THEMES.get(theme, THEMES['indigo'])

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.set_facecolor('#ffffff')

    mean_val = float(np.mean(arr))
    std_val = float(np.std(arr, ddof=1)) if n > 1 else 0.0

    if mode == 'lag' and n > 2:
        x_vals = arr[:-1]
        y_vals = arr[1:]
        x_label = "Observation précédente x_t"
        y_label = "Observation suivante x_{t+1}"
        title = f"Scatter Plot (Lag-Plot) : Dépendance séquentielle x_t vs x_{{t+1}}"
    elif mode == 'sorted':
        x_vals = np.arange(1, n + 1) / n * 100
        y_vals = np.sort(arr)
        x_label = "Rang centile empirique (%)"
        y_label = "Valeur ordonnée x_(i)"
        title = "Scatter Plot : Quantiles empiriques vs Valeurs"
    else:  # 'index' default
        x_vals = np.arange(1, n + 1)
        y_vals = arr
        x_label = "Rang de l'observation (i)"
        y_label = "Valeur observée (x_i)"
        title = f"Scatter Plot (Nuage de Points) : Séquence des Observations (n = {n})"

    # Scatter points
    ax.scatter(x_vals, y_vals, color=t['primary'], s=60, edgecolor=t['edge'], linewidth=1.2, zorder=5, label='Observations')

    # Trend line (linear regression)
    r_val = 0.0
    slope = 0.0
    if show_trend and len(x_vals) > 1 and np.ptp(x_vals) > 0:
        slope, intercept, r_val, p_val, std_err = stats.linregress(x_vals, y_vals)
        trend_y = slope * x_vals + intercept
        ax.plot(x_vals, trend_y, color='#ef4444', linewidth=2.0, linestyle='--',
                label=f'Régression linéaire (pente = {slope:.3f}, r = {r_val:.2f})', zorder=6)

    # Sigma band for index mode
    if show_sigma and mode == 'index':
        ax.axhline(mean_val, color=t['primary'], linestyle='-', linewidth=1.8, label=f'Moyenne x̄ = {mean_val:.2f}')
        ax.axhspan(mean_val - std_val, mean_val + std_val, color=t['light'], alpha=0.5, label=f'Bande ±1σ ({mean_val - std_val:.1f} à {mean_val + std_val:.1f})')

    ax.set_title(title, fontsize=12.5, fontweight='bold', pad=14, color='#0f172a')
    ax.set_xlabel(x_label, fontsize=11, labelpad=8, color='#334155')
    ax.set_ylabel(y_label, fontsize=11, labelpad=8, color='#334155')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend(frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=8.5, loc='upper right')

    b64, raw_bytes = fig_to_base64_and_bytes(fig)

    if mode == 'lag':
        corr_val = np.corrcoef(x_vals, y_vals)[0, 1] if len(x_vals) > 1 else 0.0
        points = [
            f"**Lag-plot d'ordre 1** : Compare chaque valeur $x_t$ à sa valeur suivante $x_{{t+1}}$ (coefficient r = {corr_val:.3f}).",
            "**Diagnostic d'indépendance** : " + (
                "Les points montrent une dépendance séquentielle significative (autocorrélation)." if abs(corr_val) > 0.4 else
                "Les points sont dispersés sans alignement strict, confirmant l'indépendance des tirages consécutifs."
            ),
        ]
    else:
        in_1sigma = np.sum((arr >= mean_val - std_val) & (arr <= mean_val + std_val))
        pct_1sigma = (in_1sigma / n) * 100
        trend_desc = (
            f"Tendance à la hausse (pente positive de {slope:.3f})" if slope > 0.05 else
            (f"Tendance à la baisse (pente négative de {slope:.3f})" if slope < -0.05 else "Stabilité globale sans tendance marquée")
        )
        points = [
            f"**Tendance globale** : {trend_desc} le long de la série.",
            f"**Règle empirique de dispersion** : {in_1sigma}/{n} observations ({pct_1sigma:.1f} %) se situent dans la bande ±1 écart-type.",
            f"**Étendue des valeurs** : Minimum = {np.min(arr):.2f}, Maximum = {np.max(arr):.2f}."
        ]

    interpretation = {
        'title': "Interprétation du Scatter Plot",
        'points': points
    }

    return b64, raw_bytes, interpretation


# ---------------------------------------------------------------------
# 4. COURBE (LINE CHART)
# ---------------------------------------------------------------------

def render_linechart(data, style='line_markers', show_mean=True, fill_area=True, rolling_window=None, theme='indigo'):
    arr = np.array(data, dtype=float)
    n = len(arr)
    t = THEMES.get(theme, THEMES['indigo'])

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.set_facecolor('#ffffff')

    x_indices = np.arange(1, n + 1)
    mean_val = float(np.mean(arr))

    # Area fill
    if fill_area:
        ax.fill_between(x_indices, arr, alpha=0.25, color=t['light'], label='Aire sous la courbe')

    # Main line
    marker = 'o' if style == 'line_markers' else None
    drawstyle = 'steps-mid' if style == 'step' else 'default'
    ax.plot(x_indices, arr, marker=marker, markersize=5.5, color=t['primary'], linewidth=2.2,
            drawstyle=drawstyle, label='Valeur observée x_i', zorder=5)

    # Rolling average if requested
    if rolling_window and n >= int(rolling_window):
        w = max(2, int(rolling_window))
        rolling_series = pd.Series(arr).rolling(window=w, center=True).mean()
        ax.plot(x_indices, rolling_series, color='#f59e0b', linewidth=2.2, linestyle='--',
                label=f'Moyenne mobile (fenêtre = {w})', zorder=6)

    # Mean reference
    if show_mean:
        ax.axhline(mean_val, color='#ef4444', linestyle=':', linewidth=1.8, label=f'Moyenne x̄ = {mean_val:.2f}')

    # Highlight min and max
    min_idx = int(np.argmin(arr))
    max_idx = int(np.argmax(arr))
    ax.scatter([min_idx + 1], [arr[min_idx]], color='#ef4444', s=70, zorder=7)
    ax.scatter([max_idx + 1], [arr[max_idx]], color='#10b981', s=70, zorder=7)
    ax.text(min_idx + 1, arr[min_idx], f" Min ({arr[min_idx]:.1f})", color='#b91c1c', fontsize=8.5, fontweight='bold', va='top')
    ax.text(max_idx + 1, arr[max_idx], f" Max ({arr[max_idx]:.1f})", color='#047857', fontsize=8.5, fontweight='bold', va='bottom')

    ax.set_title(f"Courbe d'Évolution des Valeurs (Line Chart, n = {n})", fontsize=13, fontweight='bold', pad=14, color='#0f172a')
    ax.set_xlabel("Ordre de l'observation (i)", fontsize=11, labelpad=8, color='#334155')
    ax.set_ylabel("Valeur", fontsize=11, labelpad=8, color='#334155')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend(frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=8.5, loc='upper right')

    b64, raw_bytes = fig_to_base64_and_bytes(fig)

    diffs = np.abs(np.diff(arr)) if n > 1 else [0]
    avg_diff = float(np.mean(diffs))

    interpretation = {
        'title': "Interprétation de la Courbe",
        'points': [
            f"**Amplitude crête à creux** : Le signal varie entre un creux de {arr[min_idx]:.2f} (au rang {min_idx + 1}) et un sommet de {arr[max_idx]:.2f} (au rang {max_idx + 1}).",
            f"**Volatilité moyenne** : L'écart moyen absolu entre deux observations successives est de {avg_diff:.2f}.",
            f"**Stabilité** : Les données gravitent autour de la moyenne de référence x̄ = {mean_val:.2f}."
        ]
    }

    return b64, raw_bytes, interpretation


# ---------------------------------------------------------------------
# 5. DIAGRAMME EN BARRES
# ---------------------------------------------------------------------

def render_barchart(data, freq_type='absolute', sort_by='value', highlight_mode=True, orientation='vertical', theme='indigo'):
    arr = np.array(data, dtype=float)
    n = len(arr)
    t = THEMES.get(theme, THEMES['indigo'])
    counts_dict = Counter(arr)

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.set_facecolor('#ffffff')

    unique_vals = np.unique(arr)
    if len(unique_vals) <= 18:
        # Discrete items
        if sort_by == 'frequency':
            items = sorted(counts_dict.items(), key=lambda x: (-x[1], x[0]))
        else:
            items = sorted(counts_dict.items(), key=lambda x: x[0])

        keys = [x[0] for x in items]
        counts = [x[1] for x in items]
        labels = [f"{k:.1f}".rstrip('0').rstrip('.') for k in keys]
    else:
        # Grouped classes for large continuous data
        k_groups = min(10, max(5, int(np.sqrt(n))))
        bins = np.linspace(min(arr), max(arr), k_groups + 1)
        binned_counts, bin_edges = np.histogram(arr, bins=bins)
        labels = [f"[{bin_edges[i]:.1f}; {bin_edges[i+1]:.1f}[" for i in range(len(binned_counts))]
        counts = list(binned_counts)
        if sort_by == 'frequency':
            sorted_zip = sorted(zip(labels, counts), key=lambda x: -x[1])
            labels = [x[0] for x in sorted_zip]
            counts = [x[1] for x in sorted_zip]

    y_vals = [(c / n * 100) if freq_type == 'relative' else c for c in counts]
    max_c = max(counts) if counts else 1
    max_y = max(y_vals) if y_vals else 1

    # Colors
    colors = []
    for c in counts:
        if highlight_mode and c == max_c and max_c > 1:
            colors.append(t['accent'])
        else:
            colors.append(t['primary'])

    if orientation == 'horizontal':
        bars = ax.barh(range(len(labels)), y_vals, color=colors, edgecolor=t['edge'], linewidth=1.1, height=0.6)
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels, fontsize=9)
        ax.invert_yaxis()
        for bar, c, y_v in zip(bars, counts, y_vals):
            label_text = f"{y_v:.1f}%" if freq_type == 'relative' else f"{c} ({c/n*100:.1f}%)"
            ax.text(bar.get_width() + 0.02 * max_y, bar.get_y() + bar.get_height() / 2,
                    label_text, va='center', fontsize=8.5, fontweight='bold', color='#1e293b')
        ax.set_xlim(0, max_y * 1.25)
        ax.set_xlabel("Pourcentage (%)" if freq_type == 'relative' else "Effectif absolu", fontsize=11, labelpad=8, color='#334155')
        ax.set_ylabel("Modalités / Valeurs", fontsize=11, labelpad=8, color='#334155')
    else:
        bars = ax.bar(range(len(labels)), y_vals, color=colors, edgecolor=t['edge'], linewidth=1.1, width=0.6)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45 if len(labels) > 9 else 0, fontsize=9)
        for bar, c, y_v in zip(bars, counts, y_vals):
            label_text = f"{y_v:.1f}%" if freq_type == 'relative' else f"{c}\n({c/n*100:.1f}%)"
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.03 * max_y,
                    label_text, ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#1e293b')
        ax.set_ylim(0, max_y * 1.25)
        ax.set_ylabel("Pourcentage (%)" if freq_type == 'relative' else "Effectif absolu", fontsize=11, labelpad=8, color='#334155')
        ax.set_xlabel("Modalités / Valeurs", fontsize=11, labelpad=8, color='#334155')

    ax.set_title(f"Diagramme en Barres des Fréquences ({'Pourcentages' if freq_type == 'relative' else 'Effectifs'})", fontsize=13, fontweight='bold', pad=14, color='#0f172a')
    ax.grid(True, axis='x' if orientation == 'horizontal' else 'y', linestyle='--', alpha=0.7)

    b64, raw_bytes = fig_to_base64_and_bytes(fig)

    modes = [k for k, v in counts_dict.items() if v == max_c]
    modes_str = ", ".join([f"{m:.1f}".rstrip('0').rstrip('.') for m in modes])

    interpretation = {
        'title': "Interprétation du Diagramme en Barres",
        'points': [
            f"**Mode dominant** : La modalité la plus fréquente est **{modes_str}** avec {max_c} occurrences (soit {max_c/n*100:.1f} % de l'ensemble).",
            f"**Diversité** : La série comporte {len(unique_vals)} valeurs distinctes pour {n} observations totales.",
            f"**Concentration** : {'Une part importante des observations se concentre sur les premières modalités.' if max_c / n > 0.3 else 'Les effectifs sont répartis de manière relativement homogène.'}"
        ]
    }

    return b64, raw_bytes, interpretation


# ---------------------------------------------------------------------
# 6. GRAPHIQUE DE DENSITÉ (KDE)
# ---------------------------------------------------------------------

def render_kde(data, bandwidth='standard', show_rug=True, compare_normal=True, fill=True, theme='indigo'):
    arr = np.array(data, dtype=float)
    n = len(arr)
    t = THEMES.get(theme, THEMES['indigo'])

    bw_factor = 0.5 if bandwidth == 'fine' else (1.8 if bandwidth == 'smooth' else 1.0)

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.set_facecolor('#ffffff')

    mean_val = float(np.mean(arr))
    std_val = float(np.std(arr, ddof=1)) if n > 1 else 1.0

    # KDE curve
    sns.kdeplot(arr, ax=ax, bw_adjust=bw_factor, color=t['primary'], linewidth=2.5,
                fill=fill, alpha=0.35, label=f'Densité empirique KDE (lissage={bandwidth})')

    # Rug plot
    if show_rug:
        sns.rugplot(arr, ax=ax, color=t['edge'], height=0.08, linewidth=1.5, label='Observations réelles (rug)')

    # Theoretical Normal comparison
    if compare_normal and std_val > 1e-6:
        x_norm = np.linspace(np.min(arr) - 2 * std_val, np.max(arr) + 2 * std_val, 400)
        y_norm = stats.norm.pdf(x_norm, mean_val, std_val)
        ax.plot(x_norm, y_norm, color='#ef4444', linestyle='--', linewidth=2.0,
                label=f'Loi Normale théorique N({mean_val:.1f}, {std_val:.1f}²)')

    # Vertical Mean and Median lines
    ax.axvline(mean_val, color=t['primary'], linestyle='-', linewidth=1.8, label=f'x̄ = {mean_val:.2f}')
    ax.axvline(float(np.median(arr)), color='#10b981', linestyle=':', linewidth=1.8, label=f'Me = {float(np.median(arr)):.2f}')

    ax.set_title(f"Estimation de la Densité de Probabilité (KDE, n = {n})", fontsize=13, fontweight='bold', pad=14, color='#0f172a')
    ax.set_xlabel("Valeurs de la variable (x)", fontsize=11, labelpad=8, color='#334155')
    ax.set_ylabel("Densité de probabilité f(x)", fontsize=11, labelpad=8, color='#334155')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend(frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=8.5, loc='upper right')

    b64, raw_bytes = fig_to_base64_and_bytes(fig)

    # Skewness and kurtosis
    skew_val = float(stats.skew(arr)) if n >= 3 else 0.0
    kurt_val = float(stats.kurtosis(arr)) if n >= 4 else 0.0

    interpretation = {
        'title': "Interprétation de la Densité (KDE)",
        'points': [
            f"**Forme de la densité** : Asymétrie (skewness) = {skew_val:.2f} &bull; Aplatissement (kurtosis) = {kurt_val:.2f}.",
            "**Comparaison à la gaussienne** : " + (
                "La distribution empirique colle remarquablement bien à la cloche normale théorique." if abs(skew_val) < 0.3 and abs(kurt_val) < 0.8 else
                "La courbe s'écarte de la loi normale théorique (forme asymétrique ou queues plus lourdes)."
            ),
            f"**Aire sous la courbe** : Par définition d'une densité de probabilité continue, l'aire totale sous la courbe vaut rigoureusement 1."
        ]
    }

    return b64, raw_bytes, interpretation


# ---------------------------------------------------------------------
# 7. HEATMAP DE CORRÉLATION
# ---------------------------------------------------------------------

def render_heatmap(data, multi_columns_dict=None, lags=4, cmap='coolwarm', annot=True):
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    ax.set_facecolor('#ffffff')

    arr = np.array(data, dtype=float)
    n = len(arr)

    # Case A: Multi-column dataframe exists
    if multi_columns_dict and len(multi_columns_dict) >= 2:
        df = pd.DataFrame(multi_columns_dict)
        corr_matrix = df.corr()
        title_suffix = "entre les variables importées"
    else:
        # Case B: Lag-correlation matrix for 1D series (Auto-correlation)
        k_lags = max(1, min(int(lags), max(1, n - 2), 6))
        lag_dict = {'x_t': arr[k_lags:]}
        for lag_i in range(1, k_lags + 1):
            lag_dict[f'Lag_{lag_i} (x_{{t-{lag_i}}})'] = arr[k_lags - lag_i:-lag_i]

        df_lags = pd.DataFrame(lag_dict)
        corr_matrix = df_lags.corr().fillna(0.0)
        title_suffix = f"d'Autocorrélation temporelle (retards de 1 à {k_lags})"

    # Heatmap rendering
    sns.heatmap(
        corr_matrix, ax=ax, cmap=cmap, vmin=-1.0, vmax=1.0,
        annot=annot, fmt=".2f", annot_kws={"size": 10, "weight": "bold"},
        cbar_kws={'label': 'Coefficient de Corrélation de Pearson (r)'},
        linewidths=1.2, linecolor='#ffffff'
    )

    ax.set_title(f"Heatmap des Corrélations Linéaires ({title_suffix})", fontsize=12.5, fontweight='bold', pad=14, color='#0f172a')
    plt.xticks(rotation=20, ha='right', fontsize=9.5)
    plt.yticks(rotation=0, fontsize=9.5)

    b64, raw_bytes = fig_to_base64_and_bytes(fig)

    # Calculate lag-1 correlation interpretation
    if 'Lag_1 (x_{t-1})' in corr_matrix.columns:
        r1 = corr_matrix.loc['x_t', 'Lag_1 (x_{t-1})']
        auto_text = (
            f"Forte dépendance séquentielle positive ($r_1 = {r1:.2f}$) : chaque valeur tend à rester proche de la précédente."
            if r1 > 0.5 else
            (f"Dépendance séquentielle négative ($r_1 = {r1:.2f}$) : alternance de valeurs hautes et basses."
             if r1 < -0.5 else f"Faible autocorrélation ($r_1 = {r1:.2f}$) : les observations successives sont indépendantes.")
        )
    else:
        auto_text = "La matrice mesure la corrélation deux à deux entre les colonnes du tableau."

    interpretation = {
        'title': "Interprétation de la Heatmap de Corrélation",
        'points': [
            "**Échelle de Pearson** : r = +1 indique une relation linéaire positive parfaite, r = -1 une relation négative parfaite, et r = 0 une absence de corrélation linéaire.",
            f"**Diagnostic** : {auto_text}",
            "**Règle de lecture** : La diagonale vaut toujours 1.0 (corrélation d'une variable avec elle-même)."
        ]
    }

    return b64, raw_bytes, interpretation


# ---------------------------------------------------------------------
# MASTER DISPATCHER FOR THE 7 CHARTS
# ---------------------------------------------------------------------

def get_visualization(chart_id, data, options=None, multi_columns=None):
    """
    Generate the requested chart among the 7 types with its interactive options.
    Returns:
        dict with:
            success: bool
            chart_id: str
            title: str
            b64_image: str (for <img>)
            raw_bytes: bytes (for PNG download)
            interpretation: dict
            error: str or None
    """
    if options is None:
        options = {}

    meta = CHART_METADATA.get(chart_id, CHART_METADATA['histogram'])
    min_obs = meta['min_obs']

    if not data or len(data) < min_obs:
        return {
            'success': False,
            'chart_id': chart_id,
            'title': meta['title'],
            'icon': meta['icon'],
            'meta': meta,
            'error': f"Données insuffisantes pour générer ce graphique : {len(data) if data else 0} observation(s) disponible(s), au moins {min_obs} requises."
        }

    try:
        if chart_id == 'histogram':
            b64, raw, interp = render_histogram(
                data,
                bins=options.get('bins', 'auto'),
                show_kde=(options.get('show_kde', 'true') == 'true'),
                show_stats=(options.get('show_stats', 'true') == 'true'),
                theme=options.get('theme', 'indigo')
            )
        elif chart_id == 'boxplot':
            b64, raw, interp = render_boxplot(
                data,
                orientation=options.get('orientation', 'horizontal'),
                show_points=(options.get('show_points', 'true') == 'true'),
                theme=options.get('theme', 'indigo')
            )
        elif chart_id == 'scatter':
            b64, raw, interp = render_scatterplot(
                data,
                mode=options.get('mode', 'index'),
                show_trend=(options.get('show_trend', 'true') == 'true'),
                show_sigma=(options.get('show_sigma', 'true') == 'true'),
                theme=options.get('theme', 'indigo')
            )
        elif chart_id == 'line':
            rw = options.get('rolling', '')
            b64, raw, interp = render_linechart(
                data,
                style=options.get('style', 'line_markers'),
                show_mean=(options.get('show_mean', 'true') == 'true'),
                fill_area=(options.get('fill_area', 'true') == 'true'),
                rolling_window=int(rw) if rw and rw.isdigit() else None,
                theme=options.get('theme', 'indigo')
            )
        elif chart_id == 'bars':
            b64, raw, interp = render_barchart(
                data,
                freq_type=options.get('freq_type', 'absolute'),
                sort_by=options.get('sort_by', 'value'),
                highlight_mode=(options.get('highlight_mode', 'true') == 'true'),
                orientation=options.get('orientation', 'vertical'),
                theme=options.get('theme', 'indigo')
            )
        elif chart_id == 'kde':
            b64, raw, interp = render_kde(
                data,
                bandwidth=options.get('bandwidth', 'standard'),
                show_rug=(options.get('show_rug', 'true') == 'true'),
                compare_normal=(options.get('compare_normal', 'true') == 'true'),
                fill=(options.get('fill', 'true') == 'true'),
                theme=options.get('theme', 'indigo')
            )
        elif chart_id == 'heatmap':
            b64, raw, interp = render_heatmap(
                data,
                multi_columns_dict=multi_columns,
                lags=int(options.get('lags', 4)),
                cmap=options.get('cmap', 'coolwarm'),
                annot=(options.get('annot', 'true') == 'true')
            )
        else:
            return {
                'success': False,
                'chart_id': chart_id,
                'error': f"Type de graphique '{chart_id}' non reconnu."
            }

        return {
            'success': True,
            'chart_id': chart_id,
            'title': meta['title'],
            'icon': meta['icon'],
            'meta': meta,
            'b64_image': b64,
            'raw_bytes': raw,
            'interpretation': interp,
            'error': None
        }

    except Exception as e:
        return {
            'success': False,
            'chart_id': chart_id,
            'title': meta['title'],
            'icon': meta['icon'],
            'meta': meta,
            'error': f"Erreur lors de la génération du graphique : {str(e)}"
        }
