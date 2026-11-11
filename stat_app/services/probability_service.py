import math

def simplify_fraction(num, den):
    """Simplify fraction and return formatted string."""
    if den == 0:
        return "Indéfini"
    g = math.gcd(int(num), int(den))
    s_num = int(num) // g
    s_den = int(den) // g
    if s_den == 1:
        return f"{s_num}"
    return f"{s_num}/{s_den}"


def calculate_discrete_urn(balls):
    """
    Calculate discrete probabilities for an urn containing colored balls.
    balls: dict like {'Rouge': 5, 'Bleue': 3, 'Verte': 2, 'Jaune': 0}
    """
    cleaned_balls = {}
    total = 0
    colors_info = {
        'Rouge': {'hex': '#ef4444', 'label': 'Rouges'},
        'Bleue': {'hex': '#3b82f6', 'label': 'Bleues'},
        'Verte': {'hex': '#10b981', 'label': 'Vertes'},
        'Jaune': {'hex': '#f59e0b', 'label': 'Jaunes'},
        'Violette': {'hex': '#8b5cf6', 'label': 'Violettes'},
    }

    for color, count in balls.items():
        try:
            c = max(0, int(count))
        except (ValueError, TypeError):
            c = 0
        if c > 0:
            cleaned_balls[color] = c
            total += c

    if total == 0:
        # Fallback to course example (5 rouges, 3 bleues)
        cleaned_balls = {'Rouge': 5, 'Bleue': 3}
        total = 8

    # Probability per color
    prob_list = []
    for color, count in cleaned_balls.items():
        p_val = count / total
        frac_str = f"{count}/{total}"
        frac_simp = simplify_fraction(count, total)
        percent_str = f"{p_val * 100:.2f} %"
        hex_color = colors_info.get(color, {}).get('hex', '#6366f1')

        prob_list.append({
            'color': color,
            'count': count,
            'hex': hex_color,
            'prob': round(p_val, 4),
            'prob_percent': percent_str,
            'fraction': frac_str,
            'fraction_simplified': frac_simp,
            'formula_latex': f"P(\\text{{{color}}}) = \\frac{{\\text{{Card}}(\\text{{{color}}})}}{{\\text{{Card}}(\\Omega)}} = \\frac{{{count}}}{{{total}}} \\approx {p_val:.4f}",
            'complementary': {
                'count': total - count,
                'prob': round(1.0 - p_val, 4),
                'percent': f"{(1.0 - p_val) * 100:.2f} %",
                'fraction': f"{total - count}/{total}",
                'fraction_simplified': simplify_fraction(total - count, total),
                'formula_latex': f"P(\\text{{{color}}}') = 1 - P(\\text{{{color}}}) = 1 - \\frac{{{count}}}{{{total}}} = \\frac{{{total - count}}}{{{total}}}"
            }
        })

    # Successive draws for the first color (if available)
    first_item = prob_list[0]
    n_c = first_item['count']
    color_name = first_item['color']

    # Two draws with replacement
    p_with_rep = (n_c / total) * (n_c / total)
    # Two draws without replacement
    if total > 1 and n_c > 1:
        p_without_rep = (n_c / total) * ((n_c - 1) / (total - 1))
        frac_without = f"{n_c * (n_c - 1)}/{total * (total - 1)}"
        frac_without_simp = simplify_fraction(n_c * (n_c - 1), total * (total - 1))
    else:
        p_without_rep = 0.0
        frac_without = "0"
        frac_without_simp = "0"

    two_draws = {
        'color': color_name,
        'with_replacement': {
            'formula_latex': f"P(C_1 \\cap C_2) = P(C_1) \\times P(C_2) = \\left(\\frac{{{n_c}}}{{{total}}}\\right)^2 = \\frac{{{n_c**2}}}{{{total**2}}} \\approx {p_with_rep:.4f}",
            'percent': f"{p_with_rep * 100:.2f} %",
            'desc': f"Tirer 2 boules {color_name}s successivement AVEC remise"
        },
        'without_replacement': {
            'formula_latex': f"P(C_1 \\cap C_2) = P(C_1) \\times P(C_2|C_1) = \\frac{{{n_c}}}{{{total}}} \\times \\frac{{{max(0, n_c - 1)}}}{{{max(1, total - 1)}}} = \\frac{{{frac_without_simp}}} \\approx {p_without_rep:.4f}",
            'percent': f"{p_without_rep * 100:.2f} %",
            'desc': f"Tirer 2 boules {color_name}s successivement SANS remise"
        }
    }

    return {
        'total_balls': total,
        'omega_card': total,
        'balls_distribution': cleaned_balls,
        'prob_list': prob_list,
        'two_draws': two_draws,
        'properties': [
            {'name': 'Équiprobabilité des issues élémentaires', 'formula': r'P(\omega_i) = \frac{1}{\text{Card}(\Omega)} = \frac{1}{' + str(total) + r'}'},
            {'name': 'Probabilité de l\'événement certain', 'formula': r'P(\Omega) = \frac{\text{Card}(\Omega)}{\text{Card}(\Omega)} = 1'},
            {'name': 'Probabilité de l\'événement impossible', 'formula': r'P(\emptyset) = 0'},
            {'name': 'Encadrement d\'une probabilité', 'formula': r'0 \le P(A) \le 1'}
        ]
    }


def calculate_conditional_probabilities(p_b=0.01, p_a_given_b=0.95, p_a_given_not_b=0.05):
    """
    Calculate conditional probabilities, Bayes theorem, and total probability.
    Parameters modeled on the classic screening / diagnosis test:
    - B : Événement cible (ex: Maladie M présente) -> Prior probability P(B)
    - A : Indicateur positif (ex: Test positif T)
    - P(A|B) : Sensibilité (probabilité que le test soit positif si la maladie est présente)
    - P(A|B') : Taux de faux positifs (test positif alors que la maladie est absente)
    """
    try:
        p_b = float(p_b)
        p_a_given_b = float(p_a_given_b)
        p_a_given_not_b = float(p_a_given_not_b)
    except (ValueError, TypeError):
        p_b, p_a_given_b, p_a_given_not_b = 0.01, 0.95, 0.05

    # Clamp between 0 and 1
    p_b = min(max(0.0001, p_b), 0.9999)
    p_a_given_b = min(max(0.0, p_a_given_b), 1.0)
    p_a_given_not_b = min(max(0.0, p_a_given_not_b), 1.0)

    p_not_b = 1.0 - p_b
    p_not_a_given_b = 1.0 - p_a_given_b
    p_not_a_given_not_b = 1.0 - p_a_given_not_b

    # Branches intersections: P(A ∩ B) = P(B) * P(A|B)
    p_a_inter_b = p_b * p_a_given_b
    p_not_a_inter_b = p_b * p_not_a_given_b
    p_a_inter_not_b = p_not_b * p_a_given_not_b
    p_not_a_inter_not_b = p_not_b * p_not_a_given_not_b

    # Total probability theorem: P(A) = P(A ∩ B) + P(A ∩ B')
    p_a = p_a_inter_b + p_a_inter_not_b

    # Bayes theorem: P(B|A) = P(A ∩ B) / P(A)
    p_b_given_a = (p_a_inter_b / p_a) if p_a > 1e-12 else 0.0

    # P(B|A')
    p_not_a = 1.0 - p_a
    p_b_given_not_a = (p_not_a_inter_b / p_not_a) if p_not_a > 1e-12 else 0.0

    # Union: P(A ∪ B) = P(A) + P(B) - P(A ∩ B)
    p_a_union_b = p_a + p_b - p_a_inter_b

    return {
        'inputs': {
            'p_b': p_b,
            'p_a_given_b': p_a_given_b,
            'p_a_given_not_b': p_a_given_not_b,
        },
        'p_b': round(p_b, 4),
        'p_not_b': round(p_not_b, 4),
        'p_a_given_b': round(p_a_given_b, 4),
        'p_a_given_not_b': round(p_a_given_not_b, 4),
        'p_a_inter_b': round(p_a_inter_b, 5),
        'p_a_inter_not_b': round(p_a_inter_not_b, 5),
        'p_a': round(p_a, 5),
        'p_not_a': round(p_not_a, 5),
        'p_b_given_a': round(p_b_given_a, 4),
        'p_b_given_a_percent': f"{p_b_given_a * 100:.2f} %",
        'p_a_union_b': round(p_a_union_b, 4),
        'bayes': {
            'formula_latex': r'P(B|A) = \frac{P(A|B) P(B)}{P(A)} = \frac{P(A|B) P(B)}{P(A|B) P(B) + P(A|B\') P(B\')}',
            'calculation_latex': (
                f"P(B|A) = \\frac{{{p_a_given_b:.3f} \\times {p_b:.4f}}}{{{p_a_inter_b:.5f} + {p_a_inter_not_b:.5f}}} "
                f"= \\frac{{{p_a_inter_b:.5f}}}{{{p_a:.5f}}} \\approx {p_b_given_a:.4f} \\text{{ ({p_b_given_a*100:.2f} \\%)}}"
            ),
            'steps': [
                f"1. Calculer le numérateur : $P(A \\cap B) = P(B) \\times P(A|B) = {p_b:.4f} \\times {p_a_given_b:.3f} = {p_a_inter_b:.5f}$",
                f"2. Calculer le dénominateur par les probabilités totales : $P(A) = P(A \\cap B) + P(A \\cap B') = {p_a_inter_b:.5f} + ({p_not_b:.4f} \\times {p_a_given_not_b:.3f}) = {p_a:.5f}$",
                f"3. Appliquer la formule de Bayes : $P(B|A) = \\frac{{{p_a_inter_b:.5f}}}{{{p_a:.5f}}} = {p_b_given_a:.4f} \\text{{ ({p_b_given_a*100:.2f} \\%)}}$"
            ],
            'interpretation': (
                f"Sachant que l'événement A s'est produit (ex: test positif), "
                f"la probabilité a posteriori que B soit vrai passe de {p_b*100:.2f} % (probabilité a priori) "
                f"à {p_b_given_a*100:.2f} %."
            )
        },
        'total_probability': {
            'formula_latex': r'P(A) = P(A|B)P(B) + P(A|B\')P(B\')',
            'calculation_latex': f"P(A) = ({p_a_given_b:.3f} \\times {p_b:.4f}) + ({p_a_given_not_b:.3f} \\times {p_not_b:.4f}) = {p_a_inter_b:.5f} + {p_a_inter_not_b:.5f} = {p_a:.5f}",
            'explanation': "Le théorème des probabilités totales permet de calculer la probabilité globale de A en sommant les contributions de toutes les branches disjointes."
        },
        'tree_branches': [
            {'path': 'B puis A', 'expr': r'P(B \cap A)', 'calc': f"{p_b:.4f} \\times {p_a_given_b:.3f}", 'val': f"{p_a_inter_b:.5f}"},
            {'path': 'B puis A\'', 'expr': r'P(B \cap A\')', 'calc': f"{p_b:.4f} \\times {p_not_a_given_b:.3f}", 'val': f"{p_not_a_inter_b:.5f}"},
            {'path': 'B\' puis A', 'expr': r'P(B\' \cap A)', 'calc': f"{p_not_b:.4f} \\times {p_a_given_not_b:.3f}", 'val': f"{p_a_inter_not_b:.5f}"},
            {'path': 'B\' puis A\'', 'expr': r'P(B\' \cap A\')', 'calc': f"{p_not_b:.4f} \\times {p_not_a_given_not_b:.3f}", 'val': f"{p_not_a_inter_not_b:.5f}"},
        ],
        'venn_regions': [
            {'code': 'A', 'title': 'Événement A', 'desc': 'Tout l\'ensemble A (composé de A ∩ B et A ∩ B\')'},
            {'code': 'A_union_B', 'title': 'Union A ∪ B', 'desc': 'Tout ce qui est dans A ou dans B (ou les deux) : P(A ∪ B) = P(A) + P(B) - P(A ∩ B)'},
            {'code': 'A_inter_B', 'title': 'Intersection A ∩ B', 'desc': 'La partie commune simultanée à A et à B'},
            {'code': 'A_prime', 'title': 'Complémentaire A\'', 'desc': 'Tout ce qui n\'est pas dans A : P(A\') = 1 - P(A)'},
            {'code': 'union_prime', 'title': 'En dehors (A ∪ B)\'', 'desc': 'Extérieur aux deux ensembles, dans l\'univers Ω'},
            {'code': 'inter_prime', 'title': 'Sauf partie commune (A ∩ B)\'', 'desc': 'Tout l\'univers sauf l\'intersection centrale'}
        ]
    }
