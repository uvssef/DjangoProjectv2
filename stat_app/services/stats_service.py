from collections import Counter
import math
import numpy as np

def format_num(val, decimals=4):
    """Format float cleanly removing unnecessary trailing zeros."""
    if val is None or not np.isfinite(val):
        return "N/A"
    if abs(val - round(val)) < 1e-9:
        return str(int(round(val)))
    formatted = f"{val:.{decimals}f}".rstrip('0').rstrip('.')
    return formatted.replace('.', ',')


def format_num_en(val, decimals=4):
    """Format float cleanly with dot."""
    if val is None or not np.isfinite(val):
        return "N/A"
    if abs(val - round(val)) < 1e-9:
        return str(int(round(val)))
    return f"{val:.{decimals}f}".rstrip('0').rstrip('.')


def calculate_central_tendencies(data):
    """
    Calculate mean, median, and mode with full step-by-step educational explanations.
    """
    if not data or len(data) == 0:
        return None

    n = len(data)
    total_sum = float(sum(data))
    mean_val = total_sum / n
    sorted_data = sorted(data)

    # 1. Moyenne
    if n <= 10:
        sum_formula_str = " + ".join([format_num(x) for x in data])
    else:
        first_few = " + ".join([format_num(x) for x in data[:4]])
        last_few = " + ".join([format_num(x) for x in data[-3:]])
        sum_formula_str = f"{first_few} + ... + {last_few}"

    mean_obj = {
        'name': 'Moyenne arithmétique',
        'symbol': r'\bar{x}',
        'value': round(mean_val, 4),
        'value_formatted': format_num(mean_val, 2),
        'formula_latex': r'\bar{x} = \frac{1}{n} \sum_{i=1}^{n} x_i',
        'formula_applied': f"\\bar{{x}} = \\frac{{{sum_formula_str}}}{{{n}}} = \\frac{{{format_num(total_sum)}}}{{{n}}} = {format_num(mean_val, 2)}",
        'steps': [
            f"1. Calculer la somme de toutes les observations : $\\sum x_i = {format_num(total_sum)}$",
            f"2. Déterminer l'effectif total : $n = {n}$",
            f"3. Diviser la somme par le nombre d'éléments : $\\bar{{x}} = \\frac{{{format_num(total_sum)}}}{{{n}}} \\approx {format_num(mean_val, 2)}$"
        ],
        'explanation': (
            "La moyenne arithmétique est le centre de gravité des données. "
            "À utiliser pour des données quantitatives sans valeurs extrêmes (outliers). "
            "Attention : elle est très sensible aux valeurs exceptionnellement hautes ou basses."
        )
    }

    # 2. Médiane
    if n % 2 == 1:
        mid_idx = n // 2
        median_val = float(sorted_data[mid_idx])
        rank_str = f"\\frac{{n + 1}}{{2}} = \\frac{{{n} + 1}}{{2}} = {mid_idx + 1}"
        med_calc_str = f"Valeur au rang {mid_idx + 1} : x_{{({mid_idx + 1})}} = {format_num(median_val)}"
        is_odd = True
    else:
        mid1 = (n // 2) - 1
        mid2 = n // 2
        val1 = sorted_data[mid1]
        val2 = sorted_data[mid2]
        median_val = float((val1 + val2) / 2.0)
        rank_str = f"\\text{{Moyenne des rangs }} \\frac{{n}}{{2}} = {mid1 + 1} \\text{{ et }} \\frac{{n}}{{2}} + 1 = {mid2 + 1}"
        med_calc_str = f"\\frac{{x_{{({mid1 + 1})}} + x_{{({mid2 + 1})}}}}{{2}} = \\frac{{{format_num(val1)} + {format_num(val2)}}}{{2}} = {format_num(median_val)}"
        is_odd = False

    if n <= 12:
        sorted_preview = ", ".join([format_num(x) for x in sorted_data])
    else:
        sorted_preview = ", ".join([format_num(x) for x in sorted_data[:5]]) + ", ... , " + ", ".join([format_num(x) for x in sorted_data[-4:]])

    median_obj = {
        'name': 'Médiane',
        'symbol': r'Me',
        'value': round(median_val, 4),
        'value_formatted': format_num(median_val, 2),
        'formula_latex': r'Me = x_{\left(\frac{n+1}{2}\right)} \text{ (si n impair) ou } \frac{x_{\left(\frac{n}{2}\right)} + x_{\left(\frac{n}{2}+1\right)}}{2} \text{ (si n pair)}',
        'formula_applied': f"\\text{{Rang : }} {rank_str} \\implies Me = {med_calc_str}",
        'sorted_preview': sorted_preview,
        'is_odd': is_odd,
        'steps': [
            f"1. Trier les données par ordre croissant : [{sorted_preview}]",
            f"2. Examiner la parité de l'effectif : $n = {n}$ ({'impair' if is_odd else 'pair'}).",
            f"3. {'Repérer l\'élément central au rang ' + str((n+1)//2) if is_odd else 'Faire la moyenne des 2 valeurs centrales aux rangs ' + str(n//2) + ' et ' + str(n//2 + 1)} : $Me = {format_num(median_val, 2)}$"
        ],
        'explanation': (
            "La médiane sépare la série ordonnée en deux groupes d'effectifs égaux : 50 % des observations sont inférieures ou égales à cette valeur, et 50 % lui sont supérieures. "
            "Très robuste aux valeurs extrêmes (outliers) et asymétries."
        )
    }

    # 3. Mode
    counts = Counter(data)
    max_freq = max(counts.values()) if counts else 0
    modes = [val for val, freq in counts.items() if freq == max_freq]
    modes.sort()

    all_same_freq = (len(set(counts.values())) == 1 and len(counts) > 1 and max_freq == 1)
    
    if all_same_freq:
        mode_type = "Aucun mode dominant"
        mode_str = "Toutes les valeurs apparaissent une seule fois."
        mode_value_display = "Pas de mode unique"
    elif len(modes) == 1:
        mode_type = "Unimodal"
        mode_str = f"{format_num(modes[0])} (apparaît {max_freq} fois)"
        mode_value_display = format_num(modes[0])
    elif len(modes) == 2:
        mode_type = "Bimodal"
        mode_str = f"{format_num(modes[0])} et {format_num(modes[1])} (chacun {max_freq} fois)"
        mode_value_display = f"{format_num(modes[0])} ; {format_num(modes[1])}"
    else:
        mode_type = f"Multimodal ({len(modes)} modes)"
        mode_str = ", ".join([format_num(m) for m in modes]) + f" (chacun {max_freq} fois)"
        mode_value_display = ", ".join([format_num(m) for m in modes])

    # Top frequency table
    top_counts = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:8]
    freq_table = [
        {
            'val': format_num(k),
            'freq': v,
            'percent': f"{(v / n) * 100:.1f} %",
            'is_mode': (k in modes and not all_same_freq)
        }
        for k, v in top_counts
    ]

    mode_obj = {
        'name': 'Mode',
        'symbol': r'Mo',
        'value': modes if not all_same_freq else [],
        'value_formatted': mode_value_display,
        'mode_type': mode_type,
        'max_freq': max_freq,
        'freq_table': freq_table,
        'formula_latex': r'Mo = \text{Valeur(s) ayant l\'effectif maximal } n_i = \max(n_j)',
        'formula_applied': f"\\text{{Fréquence max = }} {max_freq} \\implies Mo = {mode_str}",
        'steps': [
            f"1. Dresser le tableau des effectifs de chaque valeur unique.",
            f"2. Repérer l'effectif maximal : $\\max(n_i) = {max_freq}$.",
            f"3. Identifier la ou les valeurs correspondantes : {mode_str}."
        ],
        'explanation': (
            "Le mode est la valeur la plus fréquente d'une série statistique. "
            "Il est particulièrement utile pour les données qualitatives ou pour repérer une distribution multimodale."
        )
    }

    # Skewness interpretation
    diff = mean_val - median_val
    if abs(diff) < 0.05 * np.std(data):
        symmetry = "Distribution approximativement symétrique (Moyenne ≈ Médiane)."
    elif diff > 0:
        symmetry = f"Distribution asymétrique à droite (Moyenne {format_num(mean_val, 2)} > Médiane {format_num(median_val, 2)}) : tirée vers le haut par de fortes valeurs."
    else:
        symmetry = f"Distribution asymétrique à gauche (Moyenne {format_num(mean_val, 2)} < Médiane {format_num(median_val, 2)}) : tirée vers le bas par de faibles valeurs."

    return {
        'count': n,
        'mean': mean_obj,
        'median': median_obj,
        'mode': mode_obj,
        'symmetry': symmetry
    }


def calculate_variability(data):
    """
    Calculate range (étendue), variance (sample and population), and standard deviation
    with full educational steps and distinction between sample (n-1) and population (N).
    """
    if not data or len(data) == 0:
        return None

    n = len(data)
    min_val = float(min(data))
    max_val = float(max(data))
    mean_val = float(sum(data)) / n
    range_val = max_val - min_val

    # Deviations and sum of squared deviations
    deviations = [x - mean_val for x in data]
    squared_deviations = [d ** 2 for d in deviations]
    sum_sq_dev = float(sum(squared_deviations))

    # Variance & Standard Deviation
    var_pop = sum_sq_dev / n
    std_pop = math.sqrt(var_pop)

    if n > 1:
        var_sample = sum_sq_dev / (n - 1)
        std_sample = math.sqrt(var_sample)
    else:
        var_sample = 0.0
        std_sample = 0.0

    # Quartiles & IQR
    q1 = float(np.percentile(data, 25))
    q2 = float(np.percentile(data, 50))
    q3 = float(np.percentile(data, 75))
    iqr = q3 - q1

    # Coefficient of variation
    cv = (std_sample / mean_val * 100.0) if abs(mean_val) > 1e-9 else 0.0

    # Table of first few deviations for demonstration
    preview_limit = min(8, n)
    dev_table = [
        {
            'i': idx + 1,
            'xi': format_num(data[idx]),
            'diff': format_num(deviations[idx], 3),
            'sq': format_num(squared_deviations[idx], 3)
        }
        for idx in range(preview_limit)
    ]

    range_obj = {
        'name': 'Étendue',
        'symbol': r'E',
        'value': round(range_val, 4),
        'value_formatted': format_num(range_val, 2),
        'min_val': format_num(min_val),
        'max_val': format_num(max_val),
        'formula_latex': r'E = x_{\max} - x_{\min}',
        'formula_applied': f"E = {format_num(max_val)} - {format_num(min_val)} = {format_num(range_val, 2)}",
        'steps': [
            f"1. Identifier le maximum de la série : $x_{{\\max}} = {format_num(max_val)}$",
            f"2. Identifier le minimum de la série : $x_{{\\min}} = {format_num(min_val)}$",
            f"3. Soustraire le minimum du maximum : $E = {format_num(max_val)} - {format_num(min_val)} = {format_num(range_val, 2)}$"
        ],
        'explanation': (
            "L'étendue donne un aperçu rapide de l'amplitude totale des données. "
            "Attention : elle est extrêmement sensible aux valeurs extrêmes car elle ne dépend que des deux observations les plus éloignées."
        )
    }

    var_obj = {
        'name': 'Variance',
        'symbol_pop': r'\sigma^2',
        'symbol_sample': r's^2',
        'val_pop': round(var_pop, 4),
        'val_sample': round(var_sample, 4),
        'val_pop_formatted': format_num(var_pop, 2),
        'val_sample_formatted': format_num(var_sample, 2),
        'sum_sq_dev': round(sum_sq_dev, 4),
        'sum_sq_dev_formatted': format_num(sum_sq_dev, 2),
        'dev_table': dev_table,
        'has_more_rows': n > preview_limit,
        'formula_pop_latex': r'\sigma^2 = \frac{1}{N} \sum_{i=1}^{N} (x_i - \mu)^2',
        'formula_sample_latex': r's^2 = \frac{1}{n - 1} \sum_{i=1}^{n} (x_i - \bar{x})^2',
        'formula_pop_applied': f"\\sigma^2 = \\frac{{{format_num(sum_sq_dev, 2)}}}{{{n}}} = {format_num(var_pop, 2)}",
        'formula_sample_applied': f"s^2 = \\frac{{{format_num(sum_sq_dev, 2)}}}{{{n} - 1}} = \\frac{{{format_num(sum_sq_dev, 2)}}}{{{n - 1}}} = {format_num(var_sample, 2)}",
        'steps': [
            f"1. Calculer la moyenne : $\\bar{{x}} = {format_num(mean_val, 2)}$",
            f"2. Calculer chaque écart à la moyenne $(x_i - \\bar{{x}})$ et l'élever au carré.",
            f"3. Faire la somme des carrés des écarts (SCE) : $\\sum (x_i - \\bar{{x}})^2 = {format_num(sum_sq_dev, 2)}$",
            f"4. Pour un **échantillon**, diviser par $(n - 1) = {n - 1}$ (correction de Bessel sans biais) : $s^2 = {format_num(var_sample, 2)}$",
            f"5. Pour une **population entière**, diviser par $N = {n}$ : $\\sigma^2 = {format_num(var_pop, 2)}$"
        ],
        'explanation': (
            "La variance mesure la dispersion moyenne des données au carré autour de la moyenne. "
            "On utilise le diviseur $(n - 1)$ pour un échantillon car l'estimation de la moyenne consomme un degré de liberté (estimateur sans biais). "
            "Comme elle s'exprime en unités au carré, elle est complétée par l'écart-type."
        )
    }

    std_obj = {
        'name': 'Écart-type',
        'symbol_pop': r'\sigma',
        'symbol_sample': r's',
        'val_pop': round(std_pop, 4),
        'val_sample': round(std_sample, 4),
        'val_pop_formatted': format_num(std_pop, 2),
        'val_sample_formatted': format_num(std_sample, 2),
        'formula_pop_latex': r'\sigma = \sqrt{\sigma^2} = \sqrt{\frac{\sum (x_i - \mu)^2}{N}}',
        'formula_sample_latex': r's = \sqrt{s^2} = \sqrt{\frac{\sum (x_i - \bar{x})^2}{n - 1}}',
        'formula_pop_applied': f"\\sigma = \\sqrt{{{format_num(var_pop, 2)}}} = {format_num(std_pop, 2)}",
        'formula_sample_applied': f"s = \\sqrt{{{format_num(var_sample, 2)}}} = {format_num(std_sample, 2)}",
        'steps': [
            f"1. Prendre la racine carrée de la variance correspondante.",
            f"2. Échantillon : $s = \\sqrt{{{format_num(var_sample, 2)}}} = {format_num(std_sample, 2)}$",
            f"3. Population : $\\sigma = \\sqrt{{{format_num(var_pop, 2)}}} = {format_num(std_pop, 2)}$"
        ],
        'explanation': (
            "L'écart-type est la mesure de dispersion la plus utilisée car il s'exprime dans la **même unité** que les données d'origine. "
            "Il quantifie l'éloignement typique des observations par rapport à la moyenne."
        )
    }

    quartiles_obj = {
        'q1': format_num(q1, 2),
        'q2_median': format_num(q2, 2),
        'q3': format_num(q3, 2),
        'iqr': format_num(iqr, 2),
        'cv_percent': f"{cv:.1f} %",
        'explanation_iqr': "L'écart interquartile (IQR = Q3 - Q1) mesure l'étendue des 50 % des données centrales, totalement insensible aux valeurs aberrantes."
    }

    return {
        'count': n,
        'mean': round(mean_val, 4),
        'mean_formatted': format_num(mean_val, 2),
        'range': range_obj,
        'variance': var_obj,
        'std_dev': std_obj,
        'quartiles': quartiles_obj
    }
