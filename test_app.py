import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

client = Client()

print("--- TESTING ALL VIEWS INCLUDING NEW VISUALISATION SECTION ---")
urls = [
    ('/', "1. Dashboard"),
    ('/visualisations/', "Section Visualisation des données (Vue d'ensemble)"),
    ('/visualisations/?type=histogram&bins=5', "Visualisation : Histogramme"),
    ('/visualisations/?type=bars', "Visualisation : Diagramme en barres"),
    ('/visualisations/?type=boxplot', "Visualisation : Boxplot"),
    ('/visualisations/?type=distribution', "Visualisation : Courbe de distribution"),
    ('/visualisations/?type=pie', "Visualisation : Diagramme circulaire"),
    ('/tendances-centrales/', "2. Tendances centrales"),
    ('/tendances-variabilite/', "3. Tendances de variabilité"),
    ('/analyse-combinatoire/', "4. Analyse combinatoire"),
    ('/probabilite-discrete/', "5. Probabilité discrète"),
    ('/probabilite-conditionnelle/', "6. Probabilité conditionnelle"),
    ('/lois-de-probabilite/', "7. Lois de probabilité"),
]

for url, label in urls:
    resp = client.get(url)
    assert resp.status_code == 200, f"Failed {label} at {url} with {resp.status_code}"
    print(f"[OK 200] {label}")

print("\n--- TESTING PNG DOWNLOADS ---")
download_types = ['histogram', 'bars', 'boxplot', 'distribution', 'pie']
for dt in download_types:
    resp = client.get(f'/visualisations/telecharger/{dt}/')
    assert resp.status_code == 200, f"Failed download {dt}"
    assert resp['Content-Type'] == 'image/png'
    assert len(resp.content) > 5000
    print(f"[OK 200] PNG Download for {dt}: {len(resp.content)} bytes received")

print("\n--- TESTING DATA REACTION IN VISUALIZATIONS ---")
# Update dataset with custom numbers
resp = client.post('/api/data/manual/', {'data_text': '5, 5, 10, 10, 10, 20, 25, 30, 95'})
assert resp.status_code == 200
assert resp.json()['success'] is True

# Load visualisations page with new dataset
resp = client.get('/visualisations/')
assert resp.status_code == 200
assert b"9 observations" in resp.content
print("[OK] Visualisations dynamically updated with new 9-observation dataset!")

print("\n==========================================")
print("ALL NEW VISUALIZATION TESTS PASSED 100%!")
print("==========================================")
