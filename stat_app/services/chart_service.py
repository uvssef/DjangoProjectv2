import base64
import io
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import seaborn as sns
from scipy import stats
from collections import Counter

# Configure styling defaults
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica', 'sans-serif']
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#f1f5f9'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7


def fig_to_base64(fig):
    """Convert Matplotlib figure to a base64 encoded PNG data URI and close the figure."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=130, facecolor='#ffffff', edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('utf-8')
    return f"data:image/png;base64,{img_b64}"


def fig_to_png_bytes(fig):
    """Convert Matplotlib figure to raw PNG bytes for HTTP downloads."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=160, facecolor='#ffffff', edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


# ---------------------------------------------------------------------
# 1. TENDANCES CENTRALES & VARIABILITÉ (EXEMPLES COURS)
# ---------------------------------------------------------------------

def plot_central_tendencies(data, mean_val, median_val, modes):
    """
    Histogram with KDE and clear vertical dashed lines for Mean, Median, and Mode.
    """
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.set_facecolor('#ffffff')

    arr = np.array(data)
    n = len(arr)

    # Determine sensible bins
    unique_vals = np.unique(arr)
    if len(unique_vals) <= 10:
        bins = np.arange(min(arr) - 0.5, max(arr) + 1.5, 1.0)
    else:
        bins = min(20, max(5, int(np.sqrt(n))))

    sns.histplot(arr, bins=bins, kde=(len(unique_vals) > 4), color='#c7d2fe', edgecolor='#818cf8',
                 alpha=0.6, stat='density', ax=ax, label='Distribution des données')

    # Mean line
    ax.axvline(mean_val, color='#4f46e5', linestyle='-', linewidth=2.5,
               label=f'Moyenne ({mean_val:.2f})', zorder=5)

    # Median line
    ax.axvline(median_val, color='#10b981', linestyle='--', linewidth=2.5,
               label=f'Médiane ({median_val:.2f})', zorder=5)

    # Mode lines (if any)
    if modes and len(modes) <= 3:
        for idx, m in enumerate(modes):
            lbl = f'Mode ({m:.2f})' if idx == 0 else f'Mode 2 ({m:.2f})'
            ax.axvline(m, color='#f59e0b', linestyle=':', linewidth=2.5, label=lbl, zorder=5)

    ax.set_title("Distribution et Mesures de Tendances Centrales", fontsize=13, fontweight='bold', pad=12, color='#1e293b')
    ax.set_xlabel("Valeurs", fontsize=11, labelpad=8, color='#475569')
    ax.set_ylabel("Densité", fontsize=11, labelpad=8, color='#475569')
    ax.grid(True)
    ax.legend(frameon=True, facecolor='#ffffff', edgecolor='#e2e8f0', fontsize=9, loc='upper right')

    return fig_to_base64(fig)


def plot_variability(data, mean_val, std_val):
    """
    Scatter deviation plot showing distances to mean and ±1σ, ±2σ zones.
    """
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.set_facecolor('#ffffff')

    arr = np.array(data)
    indices = np.arange(1, len(arr) + 1)

    # Shaded bands for ±1σ and ±2σ
    ax.axhspan(mean_val - std_val, mean_val + std_val, color='#e0e7ff', alpha=0.5, label='Bande ±1σ (dispersion standard)')
    ax.axhspan(mean_val - 2 * std_val, mean_val + 2 * std_val, color='#e0e7ff', alpha=0.25, label='Bande ±2σ (zone élargie)')

    # Mean horizontal line
    ax.axhline(mean_val, color='#4f46e5', linestyle='-', linewidth=2, label=f'Moyenne x̄ = {mean_val:.2f}')

    # Vertical deviation lines for each observation
    for idx, val in zip(indices, arr):
        ax.plot([idx, idx], [mean_val, val], color='#94a3b8', linestyle=':', linewidth=1.2)

    # Points
    ax.scatter(indices, arr, color='#6366f1', s=55, edgecolor='#312e81', linewidth=1.2, zorder=6, label='Observations x_i')

    ax.set_title("Écarts à la moyenne et Dispersion (Écart-type)", fontsize=13, fontweight='bold', pad=12, color='#1e293b')
    ax.set_xlabel("Rang de l'observation (i)", fontsize=11, labelpad=8, color='#475569')
    ax.set_ylabel("Valeur de x_i", fontsize=11, labelpad=8, color='#475569')
    ax.grid(True)
    ax.legend(frameon=True, facecolor='#ffffff', edgecolor='#e2e8f0', fontsize=9, loc='upper right')

    return fig_to_base64(fig)


def plot_boxplot(data):
    """
    Clean horizontal boxplot with quartiles labels.
    """
    fig, ax = plt.subplots(figsize=(8, 3.2))
    ax.set_facecolor('#ffffff')

    arr = np.array(data)
    q1 = np.percentile(arr, 25)
    q2 = np.percentile(arr, 50)
    q3 = np.percentile(arr, 75)

    ax.boxplot(arr, vert=False, patch_artist=True,
               boxprops=dict(facecolor='#e0e7ff', color='#4f46e5', linewidth=1.8),
               medianprops=dict(color='#10b981', linewidth=2.5),
               whiskerprops=dict(color='#64748b', linewidth=1.5),
               capprops=dict(color='#64748b', linewidth=1.5),
               flierprops=dict(marker='o', markerfacecolor='#ef4444', markeredgecolor='#b91c1c', markersize=7))

    ax.text(q1, 1.25, f'Q1: {q1:.1f}', horizontalalignment='center', color='#4338ca', fontsize=9, fontweight='bold')
    ax.text(q2, 1.25, f'Médiane: {q2:.1f}', horizontalalignment='center', color='#047857', fontsize=9, fontweight='bold')
    ax.text(q3, 1.25, f'Q3: {q3:.1f}', horizontalalignment='center', color='#4338ca', fontsize=9, fontweight='bold')

    ax.set_yticks([])
    ax.set_title("Boîte à Moustaches (Boxplot) & Quartiles", fontsize=12, fontweight='bold', pad=14, color='#1e293b')
    ax.set_xlabel("Valeurs", fontsize=11, labelpad=8, color='#475569')
    ax.grid(True, axis='x')

    return fig_to_base64(fig)


# ---------------------------------------------------------------------
# 2. NOUVELLE SECTION DÉDIÉE : VISUALISATION DES DONNÉES DU JEU RÉEL
# ---------------------------------------------------------------------

def plot_histogram_custom(data, bins_count=None, as_bytes=False):
    """
    1. HISTOGRAMME : Visualiser la distribution des valeurs réelles.
    Affiche les effectifs par intervalle, le profil de distribution et les repères x̄ et Me.
    """
    arr = np.array(data)
    n = len(arr)
    unique_vals = np.unique(arr)

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.set_facecolor('#ffffff')

    # Determine bin count if not specified
    if bins_count:
        try:
            k_bins = max(3, min(30, int(bins_count)))
        except (ValueError, TypeError):
            k_bins = min(15, max(5, int(np.ceil(np.sqrt(n)))))
    else:
        if len(unique_vals) <= 8:
            k_bins = len(unique_vals)
        else:
            k_bins = min(15, max(5, int(np.ceil(np.sqrt(n)))))

    counts, bin_edges, patches_bars = ax.hist(
        arr, bins=k_bins, color='#c7d2fe', edgecolor='#4338ca', linewidth=1.4, alpha=0.75, rwidth=0.92
    )

    # Annotate bar counts on top of each bin
    max_c = max(counts) if len(counts) > 0 else 1
    for count, patch in zip(counts, patches_bars):
        if count > 0:
            x_pos = patch.get_x() + patch.get_width() / 2.0
            y_pos = patch.get_height()
            ax.text(x_pos, y_pos + (0.02 * max_c), f"{int(count)}",
                    ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#1e1b4b')

    # Mean & Median reference lines
    mean_val = float(np.mean(arr))
    median_val = float(np.median(arr))

    ax.axvline(mean_val, color='#4f46e5', linestyle='-', linewidth=2.2, label=f'Moyenne x̄ = {mean_val:.2f}', zorder=6)
    ax.axvline(median_val, color='#10b981', linestyle='--', linewidth=2.2, label=f'Médiane Me = {median_val:.2f}', zorder=6)

    ax.set_ylim(0, max_c * 1.18)
    ax.set_title(f"Histogramme de Distribution (n = {n} observations)", fontsize=13, fontweight='bold', pad=14, color='#0f172a')
    ax.set_xlabel("Valeurs de la série", fontsize=11, labelpad=8, color='#334155')
    ax.set_ylabel("Effectif (Nombre d'observations)", fontsize=11, labelpad=8, color='#334155')
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)
    ax.legend(frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=9, loc='upper right')

    return fig_to_png_bytes(fig) if as_bytes else fig_to_base64(fig)


def plot_bar_frequencies(data, as_bytes=False):
    """
    2. DIAGRAMME EN BARRES : Représenter les fréquences / effectifs de chaque valeur.
    Met en valeur le mode et affiche les pourcentages exacts.
    """
    arr = np.array(data)
    n = len(arr)
    unique_vals = np.unique(arr)

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.set_facecolor('#ffffff')

    counts_dict = Counter(arr)

    if len(unique_vals) <= 18:
        # Categorical bars for individual distinct values
        sorted_keys = sorted(counts_dict.keys())
        counts = [counts_dict[k] for k in sorted_keys]
        max_freq = max(counts) if counts else 1
        labels = [f"{k:.1f}".rstrip('0').rstrip('.') for k in sorted_keys]

        # Highlight Mode in Amber, others in Indigo
        colors = ['#f59e0b' if c == max_freq and max_freq > 1 else '#6366f1' for c in counts]

        bars = ax.bar(range(len(sorted_keys)), counts, color=colors, edgecolor='#312e81', linewidth=1.2, width=0.6)
        ax.set_xticks(range(len(sorted_keys)))
        ax.set_xticklabels(labels, rotation=45 if len(labels) > 10 else 0, fontsize=9.5)

        # Values & percentage labels on top
        for bar, c in zip(bars, counts):
            pct = (c / n) * 100
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05 * max_freq,
                    f"{c}\n({pct:.1f}%)", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#1e293b')

        ax.set_ylim(0, max_freq * 1.25)
        ax.set_xlabel("Valeurs distinctes (x_i)", fontsize=11, labelpad=8, color='#334155')
        sub_title = "Fréquences et pourcentages des valeurs distinctes"
    else:
        # Grouped intervals bar chart for large/continuous datasets
        k_groups = min(10, max(5, int(np.sqrt(n))))
        bins = np.linspace(min(arr), max(arr), k_groups + 1)
        binned_counts, bin_edges = np.histogram(arr, bins=bins)
        labels = [f"[{bin_edges[i]:.1f} ; {bin_edges[i+1]:.1f}[" for i in range(len(binned_counts))]
        max_freq = max(binned_counts) if len(binned_counts) > 0 else 1

        bars = ax.bar(range(len(binned_counts)), binned_counts, color='#6366f1', edgecolor='#312e81', linewidth=1.2, width=0.65)
        ax.set_xticks(range(len(binned_counts)))
        ax.set_xticklabels(labels, rotation=30, ha='right', fontsize=9)

        for bar, c in zip(bars, binned_counts):
            if c > 0:
                pct = (c / n) * 100
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05 * max_freq,
                        f"{c}\n({pct:.1f}%)", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#1e293b')

        ax.set_ylim(0, max_freq * 1.25)
        ax.set_xlabel("Classes d'intervalles", fontsize=11, labelpad=8, color='#334155')
        sub_title = "Distribution groupée par tranches de valeurs"

    ax.set_title(f"Diagramme en Barres des Fréquences ({sub_title})", fontsize=13, fontweight='bold', pad=14, color='#0f172a')
    ax.set_ylabel("Effectif (Fréquence absolue)", fontsize=11, labelpad=8, color='#334155')
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)

    # Custom legend for Mode
    custom_legend = [
        patches.Patch(facecolor='#6366f1', edgecolor='#312e81', label='Fréquence standard'),
        patches.Patch(facecolor='#f59e0b', edgecolor='#b45309', label='Mode (fréquence maximale)')
    ]
    ax.legend(handles=custom_legend, frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=8.5, loc='upper right')

    return fig_to_png_bytes(fig) if as_bytes else fig_to_base64(fig)


def plot_boxplot_detailed(data, as_bytes=False):
    """
    3. BOXPLOT : Visualiser la dispersion, la médiane, les quartiles (Q1, Q3) et les valeurs extrêmes (outliers).
    Comprend un cartouche d'information avec toutes les métriques de dispersion.
    """
    arr = np.array(data)
    n = len(arr)

    q1 = float(np.percentile(arr, 25))
    median_val = float(np.median(arr))
    q3 = float(np.percentile(arr, 75))
    iqr = q3 - q1

    # Tukey whiskers limits
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    # Identify outliers
    outliers = arr[(arr < lower_bound) | (arr > upper_bound)]

    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    ax.set_facecolor('#ffffff')

    bp = ax.boxplot(
        arr, vert=False, patch_artist=True, widths=0.45,
        boxprops=dict(facecolor='#e0e7ff', color='#4338ca', linewidth=2),
        medianprops=dict(color='#059669', linewidth=2.8),
        whiskerprops=dict(color='#475569', linewidth=1.6, linestyle='-'),
        capprops=dict(color='#475569', linewidth=2),
        flierprops=dict(marker='D', markerfacecolor='#ef4444', markeredgecolor='#991b1b', markersize=8)
    )

    # Overlay jittered data points for transparency
    y_jitter = np.random.normal(1.0, 0.04, size=n)
    ax.scatter(arr, y_jitter, color='#6366f1', alpha=0.55, s=35, edgecolor='#312e81', zorder=4, label='Observations réelles')

    # Annotate Q1, Median, Q3 with markers and text
    ax.text(q1, 1.32, f'Q1 : {q1:.2f}', ha='center', va='bottom', color='#4338ca', fontsize=9.5, fontweight='bold')
    ax.text(median_val, 0.65, f'Médiane : {median_val:.2f}', ha='center', va='top', color='#059669', fontsize=10, fontweight='bold')
    ax.text(q3, 1.32, f'Q3 : {q3:.2f}', ha='center', va='bottom', color='#4338ca', fontsize=9.5, fontweight='bold')

    # Highlight outliers if any
    if len(outliers) > 0:
        for out in outliers:
            ax.text(out, 1.15, f'Outlier: {out:.1f}', ha='center', va='bottom', color='#b91c1c', fontsize=8.5, fontweight='bold')

    # Summary box in corner
    summary_text = (
        f"Minimum : {np.min(arr):.2f}\n"
        f"Q1 : {q1:.2f}\n"
        f"Médiane : {median_val:.2f}\n"
        f"Q3 : {q3:.2f}\n"
        f"Maximum : {np.max(arr):.2f}\n"
        f"IQR (Q3-Q1) : {iqr:.2f}\n"
        f"Outliers détectés : {len(outliers)}"
    )
    props = dict(boxstyle='round,pad=0.6', facecolor='#f8fafc', edgecolor='#cbd5e1', alpha=0.95)
    ax.text(0.02, 0.95, summary_text, transform=ax.transAxes, fontsize=8.5, verticalalignment='top', bbox=props, fontfamily='monospace')

    ax.set_yticks([])
    ax.set_ylim(0.4, 1.55)
    ax.set_title(f"Boîte à Moustaches (Boxplot) & Détection des Outliers (n = {n})", fontsize=13, fontweight='bold', pad=14, color='#0f172a')
    ax.set_xlabel("Valeurs de la série", fontsize=11, labelpad=8, color='#334155')
    ax.grid(True, axis='x', linestyle='--', alpha=0.7)

    return fig_to_png_bytes(fig) if as_bytes else fig_to_base64(fig)


def plot_distribution_curve(data, as_bytes=False):
    """
    4. COURBE DE DISTRIBUTION : Observer la répartition globale (Densité KDE + ECDF cumulée).
    Deux panneaux synchronisés pour analyser la forme de la loi et la fonction de répartition.
    """
    arr = np.array(data)
    n = len(arr)

    fig, (ax_dens, ax_ecdf) = plt.subplots(1, 2, figsize=(10, 4.6), gridspec_kw={'width_ratios': [1.1, 1]})
    ax_dens.set_facecolor('#ffffff')
    ax_ecdf.set_facecolor('#ffffff')

    # Panel 1: Smooth KDE density curve
    if len(np.unique(arr)) > 2:
        sns.kdeplot(arr, ax=ax_dens, color='#4338ca', linewidth=2.5, fill=True, alpha=0.35, label='Densité estimée (KDE)')
    sns.rugplot(arr, ax=ax_dens, color='#6366f1', height=0.08, linewidth=1.5, label='Observations individuelles')

    mean_val = float(np.mean(arr))
    median_val = float(np.median(arr))
    std_val = float(np.std(arr, ddof=1)) if n > 1 else 0.0

    ax_dens.axvline(mean_val, color='#ef4444', linestyle='-', linewidth=2, label=f'x̄ = {mean_val:.2f}')
    ax_dens.axvline(median_val, color='#10b981', linestyle='--', linewidth=2, label=f'Me = {median_val:.2f}')

    ax_dens.set_title("Courbe de Densité de Probabilité (KDE)", fontsize=11.5, fontweight='bold', pad=10, color='#0f172a')
    ax_dens.set_xlabel("Valeurs (x)", fontsize=10, labelpad=6, color='#334155')
    ax_dens.set_ylabel("Densité de probabilité", fontsize=10, labelpad=6, color='#334155')
    ax_dens.grid(True, linestyle='--', alpha=0.7)
    ax_dens.legend(frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=8, loc='upper right')

    # Panel 2: Empirical Cumulative Distribution Function (ECDF)
    sorted_arr = np.sort(arr)
    y_ecdf = np.arange(1, n + 1) / n

    ax_ecdf.step(sorted_arr, y_ecdf, where='post', color='#059669', linewidth=2.2, label='Fonction de Répartition F(x)')
    ax_ecdf.scatter(sorted_arr, y_ecdf, color='#047857', s=25, zorder=5)

    # 50% median marker on ECDF
    ax_ecdf.axhline(0.5, color='#94a3b8', linestyle=':', linewidth=1.2)
    ax_ecdf.axvline(median_val, color='#10b981', linestyle=':', linewidth=1.2)
    ax_ecdf.text(median_val, 0.52, f" Me ({median_val:.1f}) = 50%", color='#047857', fontsize=8.5, fontweight='bold')

    ax_ecdf.set_ylim(-0.02, 1.05)
    ax_ecdf.set_title("Fonction de Répartition Empirique F(x) = P(X ≤ x)", fontsize=11.5, fontweight='bold', pad=10, color='#0f172a')
    ax_ecdf.set_xlabel("Valeurs (x)", fontsize=10, labelpad=6, color='#334155')
    ax_ecdf.set_ylabel("Probabilité cumulée", fontsize=10, labelpad=6, color='#334155')
    ax_ecdf.grid(True, linestyle='--', alpha=0.7)
    ax_ecdf.legend(frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=8, loc='lower right')

    plt.suptitle(f"Analyse de la Répartition des Données (n = {n} valeurs)", fontsize=13, fontweight='bold', y=1.02, color='#0f172a')
    plt.tight_layout()

    return fig_to_png_bytes(fig) if as_bytes else fig_to_base64(fig)


def plot_pie_proportions(data, as_bytes=False):
    """
    5. DIAGRAMME CIRCULAIRE (DONUT) : Afficher les proportions et pourcentages.
    Intelligent : affiche les valeurs exactes si <= 8 valeurs uniques, ou les tranches de quartiles si > 8.
    """
    arr = np.array(data)
    n = len(arr)
    unique_vals = np.unique(arr)

    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    ax.set_facecolor('#ffffff')

    palette = ['#4f46e5', '#06b6d4', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6', '#3b82f6', '#14b8a6', '#f97316', '#64748b']

    if len(unique_vals) <= 8:
        # Exact values proportions
        counts_dict = Counter(arr)
        sorted_items = sorted(counts_dict.items(), key=lambda x: -x[1])
        labels = [f"Valeur {k:.1f}".rstrip('0').rstrip('.') for k, v in sorted_items]
        sizes = [v for k, v in sorted_items]
        colors = palette[:len(labels)]
        title_suffix = "par valeur distincte"
    else:
        # Quantile binning for large datasets to keep pie readable
        q_bins = [
            np.min(arr),
            np.percentile(arr, 25),
            np.percentile(arr, 50),
            np.percentile(arr, 75),
            np.max(arr)
        ]
        # Remove duplicate bin edges if identical
        q_bins = sorted(list(set(q_bins)))
        if len(q_bins) < 3:
            q_bins = np.linspace(np.min(arr), np.max(arr), 5)

        counts, edges = np.histogram(arr, bins=q_bins)
        labels = [f"[{edges[i]:.1f} ; {edges[i+1]:.1f}]" for i in range(len(counts))]
        sizes = counts
        colors = palette[:len(labels)]
        title_suffix = "par tranches de quartiles"

    # Filter out empty slices
    active_labels = [l for l, s in zip(labels, sizes) if s > 0]
    active_colors = [c for c, s in zip(colors, sizes) if s > 0]
    active_sizes = [s for s in sizes if s > 0]

    # Donut pie chart
    wedges, texts, autotexts = ax.pie(
        active_sizes,
        labels=None,
        autopct='%1.1f%%',
        pctdistance=0.75,
        startangle=140,
        colors=active_colors,
        wedgeprops=dict(width=0.48, edgecolor='#ffffff', linewidth=2.5)
    )

    for autotext in autotexts:
        autotext.set_color('#ffffff')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(9)

    # Center circle for Donut effect with total count
    ax.text(0, 0, f"Total\n{n}\nobs.", ha='center', va='center', fontsize=12, fontweight='bold', color='#1e293b')

    # Legend on the side with counts
    legend_labels = [f"{lbl} : {s} ({s/n*100:.1f}%)" for lbl, s in zip(active_labels, active_sizes)]
    ax.legend(wedges, legend_labels, title="Légende & Effectifs", loc="center left", bbox_to_anchor=(1.02, 0.5),
              frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=9)

    ax.set_title(f"Diagramme Circulaire des Proportions ({title_suffix})", fontsize=13, fontweight='bold', pad=14, color='#0f172a')

    return fig_to_png_bytes(fig) if as_bytes else fig_to_base64(fig)


# ---------------------------------------------------------------------
# 3. ANALYSE COMBINATOIRE
# ---------------------------------------------------------------------

def plot_combinatorics_comparison(n_val=8):
    """
    Comparative growth curves of n^k vs A_n^k vs C_n^k for a fixed n.
    """
    n_val = min(max(3, int(n_val)), 12)
    k_vals = np.arange(0, n_val + 1)

    c_vals = [math.comb(n_val, k) for k in k_vals]
    a_vals = [math.perm(n_val, k) for k in k_vals]
    enum_vals = [n_val ** k for k in k_vals]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.set_facecolor('#ffffff')

    ax.plot(k_vals, enum_vals, marker='s', color='#ef4444', linewidth=2, label=f'Énumération ({n_val}^k)')
    ax.plot(k_vals, a_vals, marker='o', color='#3b82f6', linewidth=2, label=f'Arrangement (A_{{{n_val}}}^k)')
    ax.plot(k_vals, c_vals, marker='^', color='#10b981', linewidth=2, label=f'Combinaison (C_{{{n_val}}}^k)')

    ax.set_yscale('log')
    ax.set_title(f"Comparaison de la croissance combinatoire pour n = {n_val} (Échelle log)", fontsize=13, fontweight='bold', pad=12, color='#1e293b')
    ax.set_xlabel("Nombre d'éléments choisis (k)", fontsize=11, labelpad=8, color='#475569')
    ax.set_ylabel("Nombre de possibilités (log)", fontsize=11, labelpad=8, color='#475569')
    ax.grid(True, which="both")
    ax.legend(frameon=True, facecolor='#ffffff', edgecolor='#e2e8f0', fontsize=9)

    return fig_to_base64(fig)


# ---------------------------------------------------------------------
# 4. PROBABILITÉ DISCRÈTE (URNE)
# ---------------------------------------------------------------------

def plot_urn_probabilities(balls_distribution):
    """
    Two subplots: Visual Urne representation on the left, Bar chart on the right.
    """
    fig, (ax_urn, ax_bar) = plt.subplots(1, 2, figsize=(9.5, 4.2), gridspec_kw={'width_ratios': [1, 1.2]})
    ax_urn.set_facecolor('#f8fafc')
    ax_bar.set_facecolor('#ffffff')

    total = sum(balls_distribution.values())
    colors_map = {
        'Rouge': '#ef4444',
        'Bleue': '#3b82f6',
        'Verte': '#10b981',
        'Jaune': '#f59e0b',
        'Violette': '#8b5cf6'
    }

    # Left: Draw Urn vase and balls
    urn_contour = patches.Polygon([[0.15, 0.9], [0.15, 0.2], [0.25, 0.08], [0.75, 0.08], [0.85, 0.2], [0.85, 0.9]],
                                  closed=True, fill=True, facecolor='#f1f5f9', edgecolor='#64748b', linewidth=2.5)
    ax_urn.add_patch(urn_contour)

    # Generate ball positions inside the urn
    np.random.seed(42)
    flat_balls = []
    for col, count in balls_distribution.items():
        flat_balls.extend([col] * count)

    n_b = len(flat_balls)
    cols = max(3, int(np.ceil(np.sqrt(n_b))))
    rows = int(np.ceil(n_b / cols))

    x_coords = np.linspace(0.28, 0.72, cols)
    y_coords = np.linspace(0.18, 0.75, max(rows, 1))

    pos_idx = 0
    for y in y_coords:
        for x in x_coords:
            if pos_idx >= n_b:
                break
            b_color = flat_balls[pos_idx]
            hex_c = colors_map.get(b_color, '#6366f1')
            circle = patches.Circle((x, y), 0.045, facecolor=hex_c, edgecolor='#334155', linewidth=1.2, zorder=5)
            ax_urn.add_patch(circle)
            refl = patches.Circle((x - 0.012, y + 0.015), 0.012, facecolor='#ffffff', alpha=0.7, zorder=6)
            ax_urn.add_patch(refl)
            pos_idx += 1

    ax_urn.set_xlim(0, 1)
    ax_urn.set_ylim(0, 1)
    ax_urn.axis('off')
    ax_urn.set_title(f"Urne : {total} boules au total (Ω)", fontsize=12, fontweight='bold', color='#1e293b')

    categories = list(balls_distribution.keys())
    counts = [balls_distribution[c] for c in categories]
    probs = [c / total for c in counts]
    bar_colors = [colors_map.get(c, '#6366f1') for c in categories]

    bars = ax_bar.bar(categories, probs, color=bar_colors, edgecolor='#334155', linewidth=1.2, width=0.55)
    ax_bar.set_ylim(0, max(probs) * 1.25 if probs else 1.0)
    ax_bar.set_title("Probabilités P(Couleur)", fontsize=12, fontweight='bold', color='#1e293b')
    ax_bar.set_ylabel("Probabilité P(A)", fontsize=10, color='#475569')
    ax_bar.grid(True, axis='y')

    for bar, p in zip(bars, probs):
        y_val = bar.get_height()
        ax_bar.text(bar.get_x() + bar.get_width() / 2, y_val + 0.02,
                    f"{p*100:.1f}%\n({simplify_fraction_str(round(p*total), total)})",
                    ha='center', va='bottom', fontsize=9, fontweight='bold', color='#1e293b')

    return fig_to_base64(fig)


def simplify_fraction_str(num, den):
    g = math.gcd(int(num), int(den))
    s_num = int(num) // g
    s_den = int(den) // g
    return f"{s_num}/{s_den}"


# ---------------------------------------------------------------------
# 5. PROBABILITÉ CONDITIONNELLE & VENN & ARBRE
# ---------------------------------------------------------------------

def plot_venn_diagram(mode='A_inter_B'):
    """
    Generate an educational Venn diagram highlighting the requested region:
    'A', 'A_union_B', 'A_inter_B', 'A_prime', 'union_prime', 'inter_prime'
    """
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.set_facecolor('#ffffff')

    # Universe rectangle
    universe = patches.Rectangle((-2.4, -1.8), 4.8, 3.6, facecolor='#f8fafc', edgecolor='#64748b', linewidth=2)
    ax.add_patch(universe)
    ax.text(-2.2, 1.5, r'$\Omega$ (Univers)', fontsize=11, fontweight='bold', color='#334155')

    c_a = (-0.6, 0.0)
    c_b = (0.6, 0.0)
    r = 1.1

    x = np.linspace(-2.4, 2.4, 400)
    y = np.linspace(-1.8, 1.8, 400)
    X, Y = np.meshgrid(x, y)

    in_A = ((X - c_a[0])**2 + (Y - c_a[1])**2) <= r**2
    in_B = ((X - c_b[0])**2 + (Y - c_b[1])**2) <= r**2
    in_Universe = (X >= -2.4) & (X <= 2.4) & (Y >= -1.8) & (Y <= 1.8)

    title_map = {
        'A': ("Événement A", in_A),
        'A_union_B': ("Union : A ∪ B", in_A | in_B),
        'A_inter_B': ("Intersection : A ∩ B", in_A & in_B),
        'A_prime': ("Complémentaire : A'", in_Universe & (~in_A)),
        'union_prime': ("Complémentaire de l'Union : (A ∪ B)'", in_Universe & (~(in_A | in_B))),
        'inter_prime': ("Complémentaire de l'Intersection : (A ∩ B)'", in_Universe & (~(in_A & in_B)))
    }

    title, mask = title_map.get(mode, title_map['A_inter_B'])

    ax.contourf(X, Y, mask.astype(int), levels=[0.5, 1.5], colors=['#818cf8'], alpha=0.5)

    circle_a = patches.Circle(c_a, r, fill=False, edgecolor='#4338ca', linewidth=2.5)
    circle_b = patches.Circle(c_b, r, fill=False, edgecolor='#047857', linewidth=2.5)
    ax.add_patch(circle_a)
    ax.add_patch(circle_b)

    ax.text(-1.1, 0.0, "A", fontsize=14, fontweight='bold', color='#312e81', ha='center', va='center')
    ax.text(1.1, 0.0, "B", fontsize=14, fontweight='bold', color='#064e3b', ha='center', va='center')
    ax.text(0.0, 0.0, "A ∩ B", fontsize=10, fontweight='bold', color='#1e293b', ha='center', va='center')

    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-1.9, 1.9)
    ax.axis('off')
    ax.set_title(f"Diagramme de Venn — Région : {title}", fontsize=12, fontweight='bold', pad=10, color='#1e293b')

    return fig_to_base64(fig)


def plot_probability_tree(p_b, p_a_given_b, p_a_given_not_b):
    """
    Render a clean probability tree diagram with two levels and path probabilities.
    """
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.set_facecolor('#ffffff')

    p_not_b = 1.0 - p_b
    p_not_a_given_b = 1.0 - p_a_given_b
    p_not_a_given_not_b = 1.0 - p_a_given_not_b

    root = (0.05, 0.5)
    node_b = (0.45, 0.75)
    node_not_b = (0.45, 0.25)

    leaf_ba = (0.85, 0.88)
    leaf_bnot_a = (0.85, 0.62)
    leaf_not_ba = (0.85, 0.38)
    leaf_not_bnot_a = (0.85, 0.12)

    lines = [
        (root, node_b, f"P(B) = {p_b:.3f}", '#4f46e5'),
        (root, node_not_b, f"P(B') = {p_not_b:.3f}", '#64748b'),
        (node_b, leaf_ba, f"P(A|B) = {p_a_given_b:.3f}", '#10b981'),
        (node_b, leaf_bnot_a, f"P(A'|B) = {p_not_a_given_b:.3f}", '#64748b'),
        (node_not_b, leaf_not_ba, f"P(A|B') = {p_a_given_not_b:.3f}", '#f59e0b'),
        (node_not_b, leaf_not_bnot_a, f"P(A'|B') = {p_not_a_given_not_b:.3f}", '#64748b'),
    ]

    for start, end, label, col in lines:
        ax.plot([start[0], end[0]], [start[1], end[1]], color=col, linewidth=2)
        mid_x = (start[0] + end[0]) / 2.0
        mid_y = (start[1] + end[1]) / 2.0 + 0.04
        ax.text(mid_x, mid_y, label, fontsize=9, fontweight='bold', color=col, ha='center', va='bottom')

    def draw_node(pos, text, bg='#e0e7ff', border='#4338ca'):
        ax.scatter(pos[0], pos[1], s=550, color=bg, edgecolor=border, linewidth=1.5, zorder=5)
        ax.text(pos[0], pos[1], text, fontsize=10, fontweight='bold', color=border, ha='center', va='center', zorder=6)

    draw_node(root, "Ω", '#f1f5f9', '#334155')
    draw_node(node_b, "B", '#e0e7ff', '#4338ca')
    draw_node(node_not_b, "B'", '#f1f5f9', '#64748b')

    draw_node(leaf_ba, "A", '#d1fae5', '#047857')
    draw_node(leaf_bnot_a, "A'", '#f1f5f9', '#64748b')
    draw_node(leaf_not_ba, "A", '#fef3c7', '#b45309')
    draw_node(leaf_not_bnot_a, "A'", '#f1f5f9', '#64748b')

    p1 = p_b * p_a_given_b
    p2 = p_b * p_not_a_given_b
    p3 = p_not_b * p_a_given_not_b
    p4 = p_not_b * p_not_a_given_not_b

    ax.text(leaf_ba[0] + 0.05, leaf_ba[1], f"P(B ∩ A) = {p1:.4f}", fontsize=9, fontweight='bold', color='#047857', va='center')
    ax.text(leaf_bnot_a[0] + 0.05, leaf_bnot_a[1], f"P(B ∩ A') = {p2:.4f}", fontsize=9, color='#64748b', va='center')
    ax.text(leaf_not_ba[0] + 0.05, leaf_not_ba[1], f"P(B' ∩ A) = {p3:.4f}", fontsize=9, fontweight='bold', color='#b45309', va='center')
    ax.text(leaf_not_bnot_a[0] + 0.05, leaf_not_bnot_a[1], f"P(B' ∩ A') = {p4:.4f}", fontsize=9, color='#64748b', va='center')

    ax.set_xlim(0, 1.15)
    ax.set_ylim(0.05, 0.98)
    ax.axis('off')
    ax.set_title("Arbre Pondéré de Probabilités", fontsize=13, fontweight='bold', pad=12, color='#1e293b')

    return fig_to_base64(fig)


# ---------------------------------------------------------------------
# 6. LOIS DE PROBABILITÉ (DISCRÈTES & CONTINUES)
# ---------------------------------------------------------------------

def plot_discrete_dist(law_id, params, k_highlight=None):
    """
    Bar chart for discrete distributions with highlighted target value k.
    """
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ax.set_facecolor('#ffffff')

    if law_id == 'bernoulli':
        p = params.get('p', 0.5)
        x_vals = np.array([0, 1])
        probs = np.array([1.0 - p, p])
    elif law_id == 'binomial':
        n = int(params.get('n', 10))
        p = float(params.get('p', 0.5))
        x_vals = np.arange(0, n + 1)
        probs = stats.binom.pmf(x_vals, n, p)
    elif law_id == 'uniform_discrete':
        a = int(params.get('a', 1))
        b = int(params.get('b', 6))
        x_vals = np.arange(a, b + 1)
        probs = np.full_like(x_vals, 1.0 / len(x_vals), dtype=float)
    elif law_id == 'poisson':
        lambd = float(params.get('lambda', 4.0))
        max_k = max(12, int(lambd + 4 * np.sqrt(lambd)))
        x_vals = np.arange(0, max_k + 1)
        probs = stats.poisson.pmf(x_vals, lambd)
    else:
        return ""

    colors = []
    for x in x_vals:
        if k_highlight is not None and x == k_highlight:
            colors.append('#f59e0b')
        else:
            colors.append('#6366f1')

    bars = ax.bar(x_vals, probs, color=colors, edgecolor='#312e81', linewidth=1.2, width=0.6)

    ax.set_title(f"Distribution Discrète — Bâtons de Probabilité P(X = k)", fontsize=12, fontweight='bold', pad=12, color='#1e293b')
    ax.set_xlabel("Valeur k", fontsize=10, labelpad=8, color='#475569')
    ax.set_ylabel("Probabilité P(X = k)", fontsize=10, labelpad=8, color='#475569')
    ax.grid(True, axis='y')

    if k_highlight is not None and k_highlight in x_vals:
        idx = list(x_vals).index(k_highlight)
        p_k = probs[idx]
        ax.text(k_highlight, p_k + 0.015, f"P(X={k_highlight}) = {p_k:.3f}",
                ha='center', va='bottom', fontsize=9, fontweight='bold', color='#b45309')

    return fig_to_base64(fig)


def plot_continuous_dist(law_id, params, x_highlight=None, range_x=(None, None)):
    """
    Density curve for continuous distributions with shaded probability area.
    """
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ax.set_facecolor('#ffffff')

    if law_id == 'uniform_continuous':
        a = float(params.get('a', 0.0))
        b = float(params.get('b', 10.0))
        margin = (b - a) * 0.2
        x = np.linspace(a - margin, b + margin, 500)
        y = np.where((x >= a) & (x <= b), 1.0 / (b - a), 0.0)

        x1 = params.get('x1', a)
        x2 = params.get('x2', b)
        shade_x = np.linspace(max(a, x1), min(b, x2), 200)
        shade_y = np.full_like(shade_x, 1.0 / (b - a))
        ax.fill_between(shade_x, shade_y, color='#818cf8', alpha=0.5, label=f'P({x1:.1f} ≤ X ≤ {x2:.1f})')

    elif law_id == 'exponential':
        lambd = float(params.get('lambda', 0.5))
        max_x = max(6.0, 5.0 / lambd)
        x = np.linspace(0, max_x, 500)
        y = stats.expon.pdf(x, scale=1.0/lambd)

        target_x = float(params.get('x', 2.0))
        shade_x = np.linspace(0, target_x, 200)
        shade_y = stats.expon.pdf(shade_x, scale=1.0/lambd)
        ax.fill_between(shade_x, shade_y, color='#818cf8', alpha=0.5, label=f'P(X ≤ {target_x:.1f})')

    elif law_id == 'normal':
        mu = float(params.get('mu', 0.0))
        sigma = float(params.get('sigma', 1.0))
        x = np.linspace(mu - 4 * sigma, mu + 4 * sigma, 500)
        y = stats.norm.pdf(x, mu, sigma)

        r1 = params.get('range_x1', mu - sigma)
        r2 = params.get('range_x2', mu + sigma)
        shade_x = np.linspace(r1, r2, 200)
        shade_y = stats.norm.pdf(shade_x, mu, sigma)
        ax.fill_between(shade_x, shade_y, color='#818cf8', alpha=0.5, label=f'P({r1:.1f} ≤ X ≤ {r2:.1f})')

    else:
        return ""

    ax.plot(x, y, color='#4338ca', linewidth=2.5)
    ax.set_title("Courbe de Densité de Probabilité f(x) et Aire sous la courbe", fontsize=12, fontweight='bold', pad=12, color='#1e293b')
    ax.set_xlabel("x", fontsize=10, labelpad=8, color='#475569')
    ax.set_ylabel("Densité f(x)", fontsize=10, labelpad=8, color='#475569')
    ax.grid(True)
    ax.legend(frameon=True, facecolor='#ffffff', edgecolor='#e2e8f0', fontsize=9, loc='upper right')

    return fig_to_base64(fig)


def plot_z_score_rule(z_selected=1.96):
    """
    Standard normal bell curve with 68-95-99.7% empirical rule shaded bands and target Z.
    """
    fig, ax = plt.subplots(figsize=(8, 4.4))
    ax.set_facecolor('#ffffff')

    z_vals = np.linspace(-4, 4, 600)
    pdf = stats.norm.pdf(z_vals)

    ax.plot(z_vals, pdf, color='#1e293b', linewidth=2)

    z_3 = np.linspace(-3, 3, 300)
    ax.fill_between(z_3, stats.norm.pdf(z_3), color='#e0e7ff', alpha=0.35, label='±3σ : 99.73 %')

    z_2 = np.linspace(-2, 2, 300)
    ax.fill_between(z_2, stats.norm.pdf(z_2), color='#c7d2fe', alpha=0.5, label='±2σ : 95.45 %')

    z_1 = np.linspace(-1, 1, 300)
    ax.fill_between(z_1, stats.norm.pdf(z_1), color='#a5b4fc', alpha=0.65, label='±1σ : 68.27 %')

    if z_selected is not None:
        p_z = stats.norm.cdf(z_selected)
        ax.axvline(z_selected, color='#ef4444', linestyle='--', linewidth=2.2,
                   label=f'Z = {z_selected:.2f} (P(Z ≤ {z_selected:.2f}) = {p_z*100:.1f}%)')
        z_left = np.linspace(-4, z_selected, 300)
        ax.fill_between(z_left, stats.norm.pdf(z_left), color='#f43f5e', alpha=0.25)

    ax.set_title("Loi Normale Centrée Réduite N(0, 1) & Règle des 68-95-99.7%", fontsize=12, fontweight='bold', pad=12, color='#1e293b')
    ax.set_xlabel("Z-score (Nombre d'écarts-types par rapport à la moyenne)", fontsize=10, labelpad=8, color='#475569')
    ax.set_ylabel("Densité φ(z)", fontsize=10, labelpad=8, color='#475569')
    ax.grid(True)
    ax.legend(frameon=True, facecolor='#ffffff', edgecolor='#e2e8f0', fontsize=8.5, loc='upper right')

    return fig_to_base64(fig)
