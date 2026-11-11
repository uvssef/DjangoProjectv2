import math

def format_big_int(num):
    """Format large numbers with thousand separators in French style."""
    if num is None:
        return "N/A"
    return f"{num:,}".replace(',', ' ')


def calculate_enumeration(n, k):
    """
    Calculate n^k (p-uplets with repetition) and n! (permutations).
    """
    try:
        n = int(n)
        k = int(k)
    except (ValueError, TypeError):
        return None

    if n < 0 or k < 0:
        return None

    # Limit to prevent overflow crashes
    if k > 30 and n > 10:
        val = None
        val_str = "Nombre trop grand pour un affichage direct"
    else:
        val = n ** k
        val_str = format_big_int(val)

    # Detailed steps
    if k == 0:
        steps_str = f"{n}^0 = 1"
    elif k <= 6:
        factors = " \\times ".join([str(n)] * k)
        steps_str = f"{n}^{{{k}}} = {factors} = {val_str}"
    else:
        steps_str = f"{n}^{{{k}}} = \\underbrace{{{n} \\times {n} \\times \\dots \\times {n}}}_{{{k} \\text{{ fois}}}} = {val_str}"

    return {
        'name': 'Énumération (p-uplet avec répétition)',
        'symbol': r'n^k',
        'n': n,
        'k': k,
        'order_matters': 'Oui',
        'repetition_allowed': 'Oui',
        'result': val,
        'result_formatted': val_str,
        'formula_latex': r'N = n^k',
        'formula_applied': f"N = {n}^{{{k}}} = {val_str}",
        'steps': [
            f"1. Pour la 1ère position, il y a {n} choix possibles.",
            f"2. Pour chacune des {k} positions successives, la répétition étant autorisée, il y a toujours {n} choix.",
            f"3. D'après le principe multiplicatif fondamental : $N = {steps_str}$"
        ],
        'example': (
            f"Exemple pratique : Si l'on compose un code secret à {k} chiffres choisis parmi {n} symboles possibles, "
            f"il existe exactement {val_str} combinaisons de codes distincts."
        )
    }


def calculate_arrangement(n, k):
    """
    Calculate A_n^k = n! / (n - k)!
    """
    try:
        n = int(n)
        k = int(k)
    except (ValueError, TypeError):
        return None

    if n < 0 or k < 0 or k > n:
        return {
            'error': f"Conditions non respectées : il faut $0 \\le k \\le n$ (ici n = {n}, k = {k}).",
            'n': n,
            'k': k
        }

    val = math.perm(n, k)
    val_str = format_big_int(val)

    # Factors decomposition: n * (n-1) * ... * (n-k+1)
    if k == 0:
        steps_str = "1"
    elif k <= 6:
        factors = [str(n - i) for i in range(k)]
        steps_str = " \\times ".join(factors) + f" = {val_str}"
    else:
        first_few = " \\times ".join([str(n - i) for i in range(3)])
        last_val = str(n - k + 1)
        steps_str = f"{first_few} \\times \\dots \\times {last_val} = {val_str}"

    return {
        'name': 'Arrangement sans répétition',
        'symbol': r'A_n^k',
        'n': n,
        'k': k,
        'order_matters': 'Oui',
        'repetition_allowed': 'Non',
        'result': val,
        'result_formatted': val_str,
        'formula_latex': r'A_n^k = \frac{n!}{(n - k)!} = n \times (n - 1) \times \dots \times (n - k + 1)',
        'formula_applied': f"A_{{{n}}}^{{{k}}} = \\frac{{{n}!}}{{({n} - {k})!}} = \\frac{{{n}!}}{{{n - k}!}} = {steps_str}",
        'steps': [
            f"1. Vérifier la contrainte : $0 \\le k ({k}) \\le n ({n})$ : respectée.",
            f"2. Décomposer le produit des {k} entiers consécutifs décroissants à partir de {n} :",
            f"   $A_{{{n}}}^{{{k}}} = {steps_str}$",
            f"3. Résultat : il y a {val_str} arrangements possibles."
        ],
        'example': (
            f"Exemple pratique : Pour élire un bureau composé de {k} postes distincts (Président, Trésorier, etc.) "
            f"parmi {n} candidats sans cumul, il y a exactement {val_str} choix ordonnés."
        )
    }


def calculate_combination(n, k):
    """
    Calculate C_n^k = binom(n, k) = n! / (k! * (n - k)!)
    """
    try:
        n = int(n)
        k = int(k)
    except (ValueError, TypeError):
        return None

    if n < 0 or k < 0 or k > n:
        return {
            'error': f"Conditions non respectées : il faut $0 \\le k \\le n$ (ici n = {n}, k = {k}).",
            'n': n,
            'k': k
        }

    val = math.comb(n, k)
    val_str = format_big_int(val)
    arr_val = math.perm(n, k)
    k_fact = math.factorial(k)

    # Factors decomposition
    if k == 0 or k == n:
        calc_details = f"\\binom{{{n}}}{{{k}}} = 1"
    elif k <= 5:
        num_factors = " \\times ".join([str(n - i) for i in range(k)])
        den_factors = " \\times ".join([str(i + 1) for i in range(k)])
        calc_details = f"\\frac{{{num_factors}}}{{{den_factors}}} = \\frac{{{format_big_int(arr_val)}}}{{{format_big_int(k_fact)}}} = {val_str}"
    else:
        calc_details = f"\\frac{{A_{{{n}}}^{{{k}}}}}{{{k}!}} = \\frac{{{format_big_int(arr_val)}}}{{{format_big_int(k_fact)}}} = {val_str}"

    return {
        'name': 'Combinaison sans répétition',
        'symbol': r'C_n^k \text{ ou } \binom{n}{k}',
        'n': n,
        'k': k,
        'order_matters': 'Non',
        'repetition_allowed': 'Non',
        'result': val,
        'result_formatted': val_str,
        'formula_latex': r'C_n^k = \binom{n}{k} = \frac{n!}{k!(n - k)!} = \frac{A_n^k}{k!}',
        'formula_applied': f"\\binom{{{n}}}{{{k}}} = \\frac{{{n}!}}{{{k}! \\times ({n} - {k})!}} = {calc_details}",
        'symmetry_property': f"\\binom{{{n}}}{{{k}}} = \\binom{{{n}}}{{{n - k}}} = {val_str}",
        'steps': [
            f"1. L'ordre n'a pas d'importance, on divise donc le nombre d'arrangements par $k! = {k}! = {format_big_int(k_fact)}$.",
            f"2. Calcul du numérateur (arrangements) : $A_{{{n}}}^{{{k}}} = {format_big_int(arr_val)}$.",
            f"3. Division par la permutation des {k} éléments : $\\binom{{{n}}}{{{k}}} = \\frac{{{format_big_int(arr_val)}}}{{{format_big_int(k_fact)}}} = {val_str}$."
        ],
        'example': (
            f"Exemple pratique : Choisir une équipe de {k} personnes parmi un groupe de {n} collègues sans hiérarchie, "
            f"ou tirer simultanément une main de {k} cartes parmi un paquet de {n} cartes : {val_str} combinaisons."
        )
    }


def get_all_combinatorics(n=8, k=3):
    """Return all 3 combinatorics calculations for given n and k."""
    return {
        'enumeration': calculate_enumeration(n, k),
        'arrangement': calculate_arrangement(n, k),
        'combination': calculate_combination(n, k),
        'decision_guide': [
            {'concept': 'Énumération', 'order': 'OUI', 'repetition': 'OUI', 'formula': 'n^k', 'example': 'Codes PIN, cadenas à molettes'},
            {'concept': 'Arrangement', 'order': 'OUI', 'repetition': 'NON', 'formula': 'A_n^k = n! / (n-k)!', 'example': 'Podium de course, tirages ordonnés sans remise'},
            {'concept': 'Combinaison', 'order': 'NON', 'repetition': 'NON', 'formula': 'C_n^k = n! / (k!(n-k)!)', 'example': 'Mains de cartes, comités, loterie (Loto)'}
        ]
    }
