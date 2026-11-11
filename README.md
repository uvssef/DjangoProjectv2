# Plateforme Éducative de Statistiques & Probabilités

Application web moderne, interactive et complète développée en **Python** & **Django**, spécialement conçue pour les étudiants afin de maîtriser les concepts, les formules et les calculs fondamentaux de la statistique descriptive et des probabilités.

L'application s'appuie directement sur le cours de référence : **Chapitre 1 — Fondements mathématiques de l'IA : Statistiques et probabilité (Pr. CHADI)**.

---

## 🚀 Fonctionnalités Principales

### 1. Gestion des Données en Temps Réel
- **Saisie manuelle dynamique** : Accepte les nombres séparés par des virgules, espaces ou retours à la ligne, avec prise en charge automatique des formats de virgules ou points décimaux (`12,5` ou `12.5`).
- **Gestion granulaire** : Ajout d'une valeur, modification inline, suppression d'une observation spécifique ou réinitialisation complète.
- **Jeux de données prédéfinis** :
  - *Exemple officiel du cours* : `12, 15, 18, 20, 15, 25, 30` (7 valeurs).
  - *Notes d'examen* : Distribution classique d'une classe (15 valeurs).
  - *Distribution avec Outlier* : Idéal pour comparer l'impact sur la moyenne vs la robustesse de la médiane.
  - *Distribution bimodale* : Pour observer deux modes distincts.
- **Importation Excel & CSV** :
  - Compatible `.xlsx`, `.xls` et `.csv`.
  - Détection automatique de toutes les colonnes numériques.
  - Sélecteur de colonne avec prévisualisation des données brutes avant validation.
  - Nettoyage automatique des valeurs manquantes et non-numériques.
- **Exportation Excel (.xlsx)** :
  - Téléchargement d'un classeur complet avec données brutes, écarts à la moyenne $(x_i - \bar{x})^2$ et rapport de synthèse statistique formaté.

---

## 🧭 Organisation des Sections (Sidebar Fixe à Gauche)

L'application propose une navigation moderne et structurée dans sa barre latérale :

1. **Dashboard** : Vue d'ensemble des données actives, saisie manuelle, importation Excel, métriques clés instantanées ($n$, $\bar{x}$, $Me$, $s$, $E$) et graphiques récapitulatifs.
2. **Visualisation des données** (Nouvelle section avancée) :
   - **Histogramme** : Distribution des valeurs réelles avec nombre d'intervalles (bins) personnalisable, annotations des effectifs et repères $\bar{x}$ et $Me$.
   - **Diagramme en barres** : Fréquences et pourcentages exacts des modalités, avec mise en valeur du mode.
   - **Boxplot** : Dispersion, quartiles ($Q_1$, Médiane, $Q_3$), intervalle interquartile ($IQR$) et détection des valeurs extrêmes (outliers).
   - **Courbe de distribution** : Estimation de densité par noyau (KDE), rug plot des observations et fonction de répartition empirique cumulée $F(x) = P(X \le x)$.
   - **Diagramme circulaire** : Répartition des proportions et pourcentages (par valeur ou tranches de quartiles) sous forme de Donut avec effectif central.
   - **Téléchargement PNG** direct pour chaque graphique.
3. **Tendances centrales** :
   - **Moyenne arithmétique** ($\bar{x} = \frac{\sum x_i}{n}$) avec étapes détaillées de calcul et diagnostic de sensibilité aux valeurs extrêmes.
   - **Médiane** ($Me$) avec tri, détermination de parité ($n$ impair vs $n$ pair), repérage des rangs médians et justification de robustesse.
   - **Mode** ($Mo$) avec détection unimodale, bimodale, multimodale ou uniforme, et tableau complet des fréquences d'apparition.
   - **Diagnostic d'asymétrie** comparant Moyenne et Médiane.
   - Visualisation : Histogramme + KDE avec droites verticales de repère.
3. **Tendances de variabilité** :
   - **Étendue** ($E = x_{\max} - x_{\min}$).
   - **Variance** : Distinction essentielle entre la **Variance de l'Échantillon** ($s^2$ avec correction de Bessel en $n-1$) et la **Variance de la Population** ($\sigma^2$ en $N$). Tableau complet de décomposition des écarts et de la Somme des Carrés des Écarts (SCE).
   - **Écart-type** ($s$ et $\sigma$) dans la même unité que les observations.
   - **Quartiles, Écart Interquartile (IQR)** et **Coefficient de Variation (CV)**.
   - Visualisations : Boîte à moustaches (Boxplot) annotée & graphique des écarts individuels avec bandes $\pm 1\sigma$ et $\pm 2\sigma$.
4. **Analyse combinatoire** :
   - Guide de choix interactif basé sur les 2 questions du cours (*L'ordre compte-t-il ?* / *Répétition permise ?*).
   - **Énumération** ($n^k$).
   - **Arrangement** ($A_n^k = \frac{n!}{(n-k)!}$).
   - **Combinaison** ($C_n^k = \binom{n}{k} = \frac{n!}{k!(n-k)!}$).
   - Champs de saisie interactifs pour $n$ et $k$ avec limitation sécurisée, décompositions factorielles et exemples concrets (codes PIN, podium, mains de cartes).
   - Visualisation : Graphique comparatif de la croissance combinatoire en échelle logarithmique.
5. **Probabilité discrète** :
   - Univers $\Omega$, Cardinal $\text{Card}(\Omega)$, axiomes de probabilité et formule du cas équiprobable $P(A) = \frac{\text{Card}(A)}{\text{Card}(\Omega)}$.
   - **Simulateur interactif d'urne** : Personnalisation en direct du nombre de boules (Rouges, Bleues, Vertes, Jaunes).
   - Calcul des probabilités, fractions simplifiées, pourcentages et événements complémentaires $P(A')$.
   - Deux tirages successifs : **Avec remise** (indépendance) vs **Sans remise** (probabilité conditionnelle).
   - Visualisations : Illustration graphique de l'urne physique avec boules colorées + diagramme en bâtons des probabilités.
6. **Probabilité conditionnelle** :
   - Définition $P(A|B) = \frac{P(A \cap B)}{P(B)}$, Intersection $A \cap B$, Union $A \cup B$, Complémentaire $A'$.
   - **Théorème de Bayes** et **Théorème des probabilités totales** appliqués au modèle de test de dépistage / contrôle qualité.
   - Explication détaillée du paradoxe des faux positifs pour les étudiants.
   - **Diagrammes de Venn interactifs** : 6 modes commutables correspondant aux illustrations du cours ($A$, $A \cup B$, $A \cap B$, $A'$, $(A \cup B)'$, $(A \cap B)'$).
   - **Arbre pondéré de probabilités** : Arbre complet à 2 niveaux avec probabilités le long des branches et calcul des intersections sur les feuilles.
7. **Lois de probabilité** :
   - **Lois discrètes** (probabilité = hauteur d'un bâton en un point précis) :
     - *Loi de Bernoulli* $\mathcal{B}(p)$
     - *Loi Binomiale* $\mathcal{B}(n, p)$
     - *Loi Uniforme discrète* $\mathcal{U}\{a, b\}$
     - *Loi de Poisson* $\mathcal{P}(\lambda)$
   - **Lois continues** (probabilité = aire sous la courbe de densité) :
     - *Loi Uniforme continue* $\mathcal{U}[a, b]$
     - *Loi Exponentielle* $\mathcal{E}(\lambda)$
     - *Loi Normale (Gaussienne)* $\mathcal{N}(\mu, \sigma^2)$
     - *Loi Normale centrée réduite & Z-Score* $\mathcal{N}(0, 1)$ avec la **règle des 68-95-99.7%**.
   - Pour chaque loi : Définition, Formule mathématique, Cas d'usage, Paramètres interactifs, Calcul de probabilités (ponctuelle, cumulée, intervalle), Espérance $E(X)$, Variance $V(X)$, Écart-type $\sigma(X)$, Visualisation graphique Matplotlib avec aires ombrées et interprétation pédagogique.

---

## 🛠️ Stack Technique

- **Backend** : Python 3.13, Django 6.1
- **Stockage** : **Aucune base de données requise** (utilisation de sessions chiffrées en cookies signés `django.contrib.sessions.backends.signed_cookies`).
- **Calculs & Traitement** : NumPy, SciPy, Pandas, OpenPyXL
- **Visualisations** : Matplotlib, Seaborn (génération côté serveur sans interface graphique `Agg`, encodage Base64 direct)
- **Frontend** : HTML5, Tailwind CSS, Vanilla JavaScript, KaTeX pour les formules mathématiques $\LaTeX$.

---

## 💻 Démarrage Rapide

1. Ouvrez un terminal dans le répertoire de l'application :
```bash
cd "C:\Users\visca\.gemini\antigravity\scratch\stat_prob_app"
```

2. Lancez le serveur de développement Django :
```bash
python manage.py runserver
```

3. Ouvrez votre navigateur web à l'adresse :
```
http://127.0.0.1:8000/
```

4. Fichiers de test disponibles dans le dossier `samples/` :
   - `samples/donnees_etudiants.csv`
   - `samples/notes_controle_continu.xlsx`
