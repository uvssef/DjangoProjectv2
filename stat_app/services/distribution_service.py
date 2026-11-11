import math
import numpy as np
from scipy import stats

def format_val(val, decimals=4):
    """Clean float formatting."""
    if val is None or not np.isfinite(val):
        return "N/A"
    if abs(val - round(val)) < 1e-9:
        return str(int(round(val)))
    return f"{val:.{decimals}f}".rstrip('0').rstrip('.')


# ----------------------------------------------------
# 1. LOIS DISCRÈTES
# ----------------------------------------------------

def calculate_bernoulli(p=0.5):
    """Loi de Bernoulli B(p)"""
    p = float(p)
    p = min(max(0.0, p), 1.0)
    q = 1.0 - p
    exp_val = p
    var_val = p * q
    std_val = math.sqrt(var_val)

    return {
        'id': 'bernoulli',
        'type': 'discrete',
        'name': 'Loi de Bernoulli',
        'symbol': r'\mathcal{B}(p)',
        'params': {'p': p},
        'definition': "Modélise une expérience aléatoire unique comportant exactement deux issues possibles : le succès (noté 1) avec probabilité p, et l'échec (noté 0) avec probabilité 1 - p.",
        'use_case': "Lancer d'une pièce de monnaie (pile ou face), résultat d'un match (victoire/défaite), pièce défectueuse ou conforme en sortie d'usine.",
        'formula_latex': r'P(X = k) = p^k (1 - p)^{1 - k} \quad \text{pour } k \in \{0, 1\}',
        'expectation': {
            'latex': r'E(X) = p',
            'value': round(exp_val, 4),
            'formatted': format_val(exp_val, 4)
        },
        'variance': {
            'latex': r'V(X) = p(1 - p)',
            'value': round(var_val, 4),
            'formatted': format_val(var_val, 4)
        },
        'std_dev': {
            'latex': r'\sigma(X) = \sqrt{p(1 - p)}',
            'value': round(std_val, 4),
            'formatted': format_val(std_val, 4)
        },
        'probabilities': [
            {'k': 0, 'label': 'Échec (k=0)', 'prob': round(q, 4), 'percent': f"{q * 100:.2f} %", 'calc': f"1 - {p:.4f} = {q:.4f}"},
            {'k': 1, 'label': 'Succès (k=1)', 'prob': round(p, 4), 'percent': f"{p * 100:.2f} %", 'calc': f"{p:.4f}"}
        ],
        'interpretation': f"Avec un paramètre de succès p = {p:.2f}, le système a {p*100:.1f} % de chances de réussir et {q*100:.1f} % d'échouer. L'espérance E(X) = {exp_val:.2f} correspond au gain moyen théorique."
    }


def calculate_binomial(n=10, p=0.5, k=5):
    """Loi Binomiale B(n, p)"""
    n = max(1, int(n))
    p = min(max(0.0, float(p)), 1.0)
    k = min(max(0, int(k)), n)
    q = 1.0 - p

    exp_val = n * p
    var_val = n * p * q
    std_val = math.sqrt(var_val)

    # Probabilities
    prob_exact = stats.binom.pmf(k, n, p)
    prob_leq = stats.binom.cdf(k, n, p)
    prob_geq = 1.0 - stats.binom.cdf(k - 1, n, p) if k > 0 else 1.0

    comb_nk = math.comb(n, k)
    steps_exact = f"\\binom{{{n}}}{{{k}}} \\times {p:.3f}^{{{k}}} \\times {q:.3f}^{{{n-k}}} = {comb_nk} \\times {p**k:.6f} \\times {q**(n-k):.6f} \\approx {prob_exact:.4f}"

    return {
        'id': 'binomial',
        'type': 'discrete',
        'name': 'Loi Binomiale',
        'symbol': rf'\mathcal{{B}}({n},\, {p:.2f})',
        'params': {'n': n, 'p': p, 'k': k},
        'definition': f"Compte le nombre total k de succès obtenus lors de la répétition indépendante et identique de n expériences de Bernoulli de paramètre p.",
        'use_case': "Nombre de piles obtenus en n lancers d'une pièce, nombre de pièces défectueuses dans un échantillon industriel de taille n, nombre d'étudiants admis parmi n candidats.",
        'formula_latex': r'P(X = k) = \binom{n}{k} p^k (1 - p)^{n - k} \quad \text{pour } k \in \{0, 1, \dots, n\}',
        'expectation': {
            'latex': r'E(X) = n \times p',
            'value': round(exp_val, 4),
            'formatted': format_val(exp_val, 4),
            'calc': f"{n} \\times {p:.3f} = {exp_val:.2f}"
        },
        'variance': {
            'latex': r'V(X) = n \times p \times (1 - p)',
            'value': round(var_val, 4),
            'formatted': format_val(var_val, 4),
            'calc': f"{n} \\times {p:.3f} \\times {q:.3f} = {var_val:.4f}"
        },
        'std_dev': {
            'latex': r'\sigma(X) = \sqrt{n p (1 - p)}',
            'value': round(std_val, 4),
            'formatted': format_val(std_val, 4),
            'calc': f"\\sqrt{{{var_val:.4f}}} = {std_val:.4f}"
        },
        'query': {
            'k': k,
            'prob_exact': round(prob_exact, 4),
            'prob_exact_percent': f"{prob_exact * 100:.2f} %",
            'prob_exact_calc': steps_exact,
            'prob_leq': round(prob_leq, 4),
            'prob_leq_percent': f"{prob_leq * 100:.2f} %",
            'prob_geq': round(prob_geq, 4),
            'prob_geq_percent': f"{prob_geq * 100:.2f} %",
        },
        'interpretation': f"Pour {n} essais indépendants avec probabilité unitaire {p*100:.1f} %, on s'attend en moyenne à {exp_val:.2f} succès. La probabilité d'obtenir exactement k = {k} succès est de {prob_exact*100:.2f} %."
    }


def calculate_uniform_discrete(a=1, b=6, k=3):
    """Loi Uniforme Discrète U{a, b}"""
    a = int(a)
    b = int(b)
    if b < a:
        a, b = b, a
    n = b - a + 1
    k = int(k)
    k_valid = (a <= k <= b)

    prob_exact = (1.0 / n) if k_valid else 0.0
    exp_val = (a + b) / 2.0
    var_val = (n ** 2 - 1) / 12.0
    std_val = math.sqrt(var_val)

    prob_leq = ((k - a + 1) / n) if k_valid else (1.0 if k > b else 0.0)

    return {
        'id': 'uniform_discrete',
        'type': 'discrete',
        'name': 'Loi Uniforme Discrète',
        'symbol': rf'\mathcal{{U}}\{{{a}, \dots, {b}\}}',
        'params': {'a': a, 'b': b, 'n': n, 'k': k},
        'definition': f"Modélise une variable aléatoire prenant un nombre fini n = {n} de valeurs entières équitablement réparties entre a = {a} et b = {b}, avec équiprobabilité stricte.",
        'use_case': "Lancer d'un dé équilibré à 6 faces, tirage d'un numéro au loto parmi n boules, roulette équilibrée.",
        'formula_latex': r'P(X = k) = \frac{1}{n} = \frac{1}{b - a + 1} \quad \text{pour } k \in \{a, \dots, b\}',
        'expectation': {
            'latex': r'E(X) = \frac{a + b}{2}',
            'value': round(exp_val, 4),
            'formatted': format_val(exp_val, 4),
            'calc': f"\\frac{{{a} + {b}}}{{2}} = {exp_val:.2f}"
        },
        'variance': {
            'latex': r'V(X) = \frac{n^2 - 1}{12} = \frac{(b - a + 1)^2 - 1}{12}',
            'value': round(var_val, 4),
            'formatted': format_val(var_val, 4),
            'calc': f"\\frac{{{n}^2 - 1}}{{12}} = \\frac{{{n**2 - 1}}}{{12}} = {var_val:.4f}"
        },
        'std_dev': {
            'latex': r'\sigma(X) = \sqrt{\frac{n^2 - 1}{12}}',
            'value': round(std_val, 4),
            'formatted': format_val(std_val, 4),
            'calc': f"\\sqrt{{{var_val:.4f}}} = {std_val:.4f}"
        },
        'query': {
            'k': k,
            'k_valid': k_valid,
            'prob_exact': round(prob_exact, 4),
            'prob_exact_percent': f"{prob_exact * 100:.2f} %",
            'prob_leq': round(prob_leq, 4),
            'prob_leq_percent': f"{prob_leq * 100:.2f} %",
        },
        'interpretation': f"Chaque valeur entre {a} et {b} possède rigoureusement la même probabilité d'apparition de 1/{n} = {prob_exact*100:.2f} %."
    }


def calculate_poisson(lambd=4.0, k=3):
    """Loi de Poisson P(lambda)"""
    lambd = max(0.01, float(lambd))
    k = max(0, int(k))

    exp_val = lambd
    var_val = lambd
    std_val = math.sqrt(lambd)

    prob_exact = stats.poisson.pmf(k, lambd)
    prob_leq = stats.poisson.cdf(k, lambd)
    prob_geq = 1.0 - stats.poisson.cdf(k - 1, lambd) if k > 0 else 1.0

    k_fact = math.factorial(k)
    steps_exact = f"\\frac{{{lambd:.2f}^{{{k}}} \\times e^{{-{lambd:.2f}}}}}{{{k}!}} = \\frac{{{lambd**k:.4f} \\times {math.exp(-lambd):.6f}}}{{{k_fact}}} = {prob_exact:.4f}"

    return {
        'id': 'poisson',
        'type': 'discrete',
        'name': 'Loi de Poisson',
        'symbol': rf'\mathcal{{P}}(\lambda = {lambd:.2f})',
        'params': {'lambda': lambd, 'k': k},
        'definition': "Décrit le nombre d'occurrences d'un événement rare et indépendant sur un intervalle de temps ou d'espace fixe, connaissant sa fréquence moyenne lambda.",
        'use_case': "Nombre d'appels reçus par heure à un standard, nombre de pannes de serveurs par semaine, nombre de fautes d'impression par page de livre, trafic réseau.",
        'formula_latex': r'P(X = k) = \frac{\lambda^k e^{-\lambda}}{k!} \quad \text{pour } k \in \mathbb{N}',
        'expectation': {
            'latex': r'E(X) = \lambda',
            'value': round(exp_val, 4),
            'formatted': format_val(exp_val, 4),
            'calc': f"\\lambda = {exp_val:.2f}"
        },
        'variance': {
            'latex': r'V(X) = \lambda',
            'value': round(var_val, 4),
            'formatted': format_val(var_val, 4),
            'calc': f"\\lambda = {var_val:.2f}"
        },
        'std_dev': {
            'latex': r'\sigma(X) = \sqrt{\lambda}',
            'value': round(std_val, 4),
            'formatted': format_val(std_val, 4),
            'calc': f"\\sqrt{{{lambd:.2f}}} = {std_val:.4f}"
        },
        'query': {
            'k': k,
            'prob_exact': round(prob_exact, 4),
            'prob_exact_percent': f"{prob_exact * 100:.2f} %",
            'prob_exact_calc': steps_exact,
            'prob_leq': round(prob_leq, 4),
            'prob_leq_percent': f"{prob_leq * 100:.2f} %",
            'prob_geq': round(prob_geq, 4),
            'prob_geq_percent': f"{prob_geq * 100:.2f} %",
        },
        'interpretation': f"Avec en moyenne lambda = {lambd:.2f} événements par période, la probabilité d'observer précisément k = {k} événements est de {prob_exact*100:.2f} %."
    }


# ----------------------------------------------------
# 2. LOIS CONTINUES
# ----------------------------------------------------

def calculate_uniform_continuous(a=0.0, b=10.0, x1=2.0, x2=5.0):
    """Loi Uniforme Continue U[a, b]"""
    a = float(a)
    b = float(b)
    if b <= a:
        b = a + 1.0

    length = b - a
    density = 1.0 / length
    exp_val = (a + b) / 2.0
    var_val = (length ** 2) / 12.0
    std_val = length / math.sqrt(12.0)

    x1 = float(x1)
    x2 = float(x2)
    if x2 < x1:
        x1, x2 = x2, x1

    # Probability between x1 and x2
    low = max(a, x1)
    high = min(b, x2)
    if high > low:
        prob_range = (high - low) / length
    else:
        prob_range = 0.0

    return {
        'id': 'uniform_continuous',
        'type': 'continuous',
        'name': 'Loi Uniforme Continue',
        'symbol': rf'\mathcal{{U}}([{a:.2f},\, {b:.2f}])',
        'params': {'a': a, 'b': b, 'x1': x1, 'x2': x2},
        'definition': "Une variable aléatoire continue a une densité constante sur tout l'intervalle [a, b]. Toute sous-plage de même longueur a exactement la même probabilité.",
        'use_case': "Temps d'attente d'un bus arrivant au hasard toutes les 10 minutes, erreur d'arrondi de calcul numérique entre -0.5 et +0.5.",
        'density_latex': r'f(x) = \frac{1}{b - a} \quad \text{pour } x \in [a, b]',
        'density_value': round(density, 4),
        'expectation': {
            'latex': r'E(X) = \frac{a + b}{2}',
            'value': round(exp_val, 4),
            'formatted': format_val(exp_val, 4),
            'calc': f"\\frac{{{a:.2f} + {b:.2f}}}{{2}} = {exp_val:.2f}"
        },
        'variance': {
            'latex': r'V(X) = \frac{(b - a)^2}{12}',
            'value': round(var_val, 4),
            'formatted': format_val(var_val, 4),
            'calc': f"\\frac{{({b:.2f} - {a:.2f})^2}}{{12}} = \\frac{{{length:.2f}^2}}{{12}} = {var_val:.4f}"
        },
        'std_dev': {
            'latex': r'\sigma(X) = \frac{b - a}{\sqrt{12}}',
            'value': round(std_val, 4),
            'formatted': format_val(std_val, 4),
            'calc': f"\\frac{{{length:.2f}}}{{\\sqrt{{12}}}} = {std_val:.4f}"
        },
        'query': {
            'x1': x1,
            'x2': x2,
            'prob_range': round(prob_range, 4),
            'prob_range_percent': f"{prob_range * 100:.2f} %",
            'calc': f"P({x1:.2f} \\le X \\le {x2:.2f}) = \\int_{{{low:.2f}}}^{{{high:.2f}}} \\frac{{1}}{{{length:.2f}}}\\,dx = \\frac{{{high:.2f} - {low:.2f}}}{{{length:.2f}}} = {prob_range:.4f}"
        },
        'interpretation': f"La densité vaut {density:.4f} sur [{a:.2f}, {b:.2f}]. La probabilité que la valeur tombe entre {x1:.2f} et {x2:.2f} est de {prob_range*100:.2f} %."
    }


def calculate_exponential(lambd=0.5, x=2.0):
    """Loi Exponentielle E(lambda)"""
    lambd = max(0.001, float(lambd))
    x = max(0.0, float(x))

    exp_val = 1.0 / lambd
    var_val = 1.0 / (lambd ** 2)
    std_val = 1.0 / lambd

    prob_leq = 1.0 - math.exp(-lambd * x)
    prob_gt = math.exp(-lambd * x)

    return {
        'id': 'exponential',
        'type': 'continuous',
        'name': 'Loi Exponentielle',
        'symbol': rf'\mathcal{{E}}(\lambda = {lambd:.3f})',
        'params': {'lambda': lambd, 'x': x},
        'definition': "Modélise la durée de vie ou le temps d'attente avant la survenue du premier événement d'un processus sans mémoire (loi de Poisson continue).",
        'use_case': "Temps avant la panne d'un équipement informatique, durée d'une communication téléphonique, délai d'attente d'une requête HTTP.",
        'density_latex': r'f(x) = \lambda e^{-\lambda x} \quad \text{pour } x \ge 0',
        'expectation': {
            'latex': r'E(X) = \frac{1}{\lambda}',
            'value': round(exp_val, 4),
            'formatted': format_val(exp_val, 4),
            'calc': f"\\frac{{1}}{{{lambd:.3f}}} = {exp_val:.2f}"
        },
        'variance': {
            'latex': r'V(X) = \frac{1}{\lambda^2}',
            'value': round(var_val, 4),
            'formatted': format_val(var_val, 4),
            'calc': f"\\frac{{1}}{{{lambd:.3f}^2}} = {var_val:.4f}"
        },
        'std_dev': {
            'latex': r'\sigma(X) = \frac{1}{\lambda}',
            'value': round(std_val, 4),
            'formatted': format_val(std_val, 4),
            'calc': f"\\frac{{1}}{{{lambd:.3f}}} = {std_val:.4f}"
        },
        'query': {
            'x': x,
            'prob_leq': round(prob_leq, 4),
            'prob_leq_percent': f"{prob_leq * 100:.2f} %",
            'prob_leq_calc': f"1 - e^{{-{lambd:.3f} \\times {x:.2f}}} = 1 - e^{{-{lambd*x:.3f}}} = {prob_leq:.4f}",
            'prob_gt': round(prob_gt, 4),
            'prob_gt_percent': f"{prob_gt * 100:.2f} %",
            'prob_gt_calc': f"e^{{-{lambd:.3f} \\times {x:.2f}}} = {prob_gt:.4f}"
        },
        'interpretation': f"Le temps moyen d'attente est de E(X) = {exp_val:.2f} unités de temps. La probabilité que l'événement survienne avant t = {x:.2f} est de {prob_leq*100:.2f} %."
    }


def calculate_normal(mu=0.0, sigma=1.0, x=1.0, range_x1=-1.0, range_x2=1.0):
    """Loi Normale Gaussienne N(mu, sigma^2)"""
    mu = float(mu)
    sigma = max(0.001, float(sigma))
    x = float(x)
    range_x1 = float(range_x1)
    range_x2 = float(range_x2)
    if range_x2 < range_x1:
        range_x1, range_x2 = range_x2, range_x1

    exp_val = mu
    var_val = sigma ** 2
    std_val = sigma

    # Probabilities
    prob_leq_x = stats.norm.cdf(x, mu, sigma)
    prob_geq_x = 1.0 - prob_leq_x
    prob_between = stats.norm.cdf(range_x2, mu, sigma) - stats.norm.cdf(range_x1, mu, sigma)

    z_score_x = (x - mu) / sigma

    return {
        'id': 'normal',
        'type': 'continuous',
        'name': 'Loi Normale (Gaussienne)',
        'symbol': rf'\mathcal{{N}}(\mu = {mu:.2f},\, \sigma^2 = {var_val:.2f})',
        'params': {'mu': mu, 'sigma': sigma, 'x': x, 'range_x1': range_x1, 'range_x2': range_x2},
        'definition': "La loi fondamentale de la statistique. Décrit des variables résultant de la somme d'un grand nombre de petits effets indépendants (Théorème Central Limite).",
        'use_case': "Tailles humaines, notes à un examen national, erreurs de mesure scientifique, rendements financiers.",
        'density_latex': r'f(x) = \frac{1}{\sigma \sqrt{2\pi}} e^{-\frac{1}{2}\left(\frac{x - \mu}{\sigma}\right)^2}',
        'expectation': {
            'latex': r'E(X) = \mu',
            'value': round(exp_val, 4),
            'formatted': format_val(exp_val, 4),
            'calc': f"\\mu = {exp_val:.2f}"
        },
        'variance': {
            'latex': r'V(X) = \sigma^2',
            'value': round(var_val, 4),
            'formatted': format_val(var_val, 4),
            'calc': f"\\sigma^2 = {sigma:.2f}^2 = {var_val:.4f}"
        },
        'std_dev': {
            'latex': r'\sigma(X) = \sigma',
            'value': round(std_val, 4),
            'formatted': format_val(std_val, 4),
            'calc': f"\\sigma = {std_val:.4f}"
        },
        'query': {
            'x': x,
            'z_score': round(z_score_x, 3),
            'prob_leq': round(prob_leq_x, 4),
            'prob_leq_percent': f"{prob_leq_x * 100:.2f} %",
            'prob_geq': round(prob_geq_x, 4),
            'prob_geq_percent': f"{prob_geq_x * 100:.2f} %",
            'range_x1': range_x1,
            'range_x2': range_x2,
            'prob_between': round(prob_between, 4),
            'prob_between_percent': f"{prob_between * 100:.2f} %",
        },
        'interpretation': f"La distribution est symétrique autour de mu = {mu:.2f}. Une valeur x = {x:.2f} correspond à un score z = {z_score_x:.2f} écarts-types par rapport à la moyenne."
    }


def calculate_standard_normal(z=1.96):
    """Loi Normale Centrée Réduite N(0, 1) et Règle des 68-95-99.7%"""
    z = float(z)
    prob_leq_z = stats.norm.cdf(z)
    prob_between_sym = stats.norm.cdf(abs(z)) - stats.norm.cdf(-abs(z))

    rule_68 = stats.norm.cdf(1) - stats.norm.cdf(-1)  # ~ 68.27%
    rule_95 = stats.norm.cdf(2) - stats.norm.cdf(-2)  # ~ 95.45%
    rule_99 = stats.norm.cdf(3) - stats.norm.cdf(-3)  # ~ 99.73%

    return {
        'id': 'standard_normal',
        'type': 'continuous',
        'name': 'Loi Normale Centrée Réduite (Z-Score)',
        'symbol': r'\mathcal{N}(0, 1)',
        'params': {'z': z},
        'definition': "Toute variable normale X ~ N(mu, sigma^2) est standardisée en Z = (X - mu) / sigma pour suivre la loi normale standard N(0, 1). Cela permet de comparer des grandeurs d'échelles différentes.",
        'use_case': "Calcul des probabilités à l'aide de la table normale unifiée, tests d'hypothèses Z-test, intervalles de confiance (z=1.96 pour 95%), détection d'outliers.",
        'formula_latex': r'Z = \frac{X - \mu}{\sigma} \sim \mathcal{N}(0, 1)',
        'density_latex': r'\phi(z) = \frac{1}{\sqrt{2\pi}} e^{-\frac{z^2}{2}}',
        'expectation': {
            'latex': r'E(Z) = 0',
            'value': 0.0,
            'formatted': "0"
        },
        'variance': {
            'latex': r'V(Z) = 1',
            'value': 1.0,
            'formatted': "1"
        },
        'std_dev': {
            'latex': r'\sigma(Z) = 1',
            'value': 1.0,
            'formatted': "1"
        },
        'empirical_rule': [
            {'interval': r'[\mu - \sigma,\, \mu + \sigma]', 'z_range': r'[-1,\, +1]', 'prob': round(rule_68, 4), 'percent': f"{rule_68 * 100:.2f} %", 'desc': 'Environ 68.3 % des observations'},
            {'interval': r'[\mu - 2\sigma,\, \mu + 2\sigma]', 'z_range': r'[-2,\, +2]', 'prob': round(rule_95, 4), 'percent': f"{rule_95 * 100:.2f} %", 'desc': 'Environ 95.5 % des observations (seuil classique à 5%)'},
            {'interval': r'[\mu - 3\sigma,\, \mu + 3\sigma]', 'z_range': r'[-3,\, +3]', 'prob': round(rule_99, 4), 'percent': f"{rule_99 * 100:.2f} %", 'desc': 'Environ 99.7 % des observations (presque la totalité)'}
        ],
        'query': {
            'z': z,
            'prob_leq': round(prob_leq_z, 4),
            'prob_leq_percent': f"{prob_leq_z * 100:.2f} %",
            'prob_between_sym': round(prob_between_sym, 4),
            'prob_between_sym_percent': f"{prob_between_sym * 100:.2f} %",
            'calc_latex': f"\\Phi({z:.2f}) = P(Z \\le {z:.2f}) = {prob_leq_z:.4f} \\text{{ ({prob_leq_z*100:.2f} \\%)}}"
        },
        'interpretation': f"Un score Z = {z:.2f} signifie que l'observation est située à {abs(z):.2f} écart-type(s) au-{'dessus' if z >= 0 else 'dessous'} de la moyenne. {prob_leq_z*100:.2f} % des observations sont inférieures ou égales à cette valeur."
    }
