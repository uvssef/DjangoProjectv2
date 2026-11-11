import os
import io
import django
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

client = Client()

print("--- TESTING CSV AND EXCEL UPLOAD ---")

# 1. Test CSV upload
csv_content = b"etudiant,note_maths,age\nAlice,16.5,21\nBob,14.0,22\nCharlie,18.0,20\nDavid,12.5,23\nEva,15.0,21\n"
csv_file = SimpleUploadedFile("notes_examen.csv", csv_content, content_type="text/csv")

resp = client.post('/api/excel/preview/', {'file': csv_file})
assert resp.status_code == 200
data = resp.json()
assert data['success'] is True
assert 'note_maths' in data['numeric_columns']
assert data['total_rows'] == 5
print(f"[OK] CSV preview succeeded: {data['numeric_columns']}, {data['total_rows']} rows")

# 2. Confirm CSV import
csv_file.seek(0)
resp = client.post('/api/excel/confirm/', {'file': csv_file, 'column_name': 'note_maths'})
assert resp.status_code == 200
data = resp.json()
assert data['success'] is True and data['count'] == 5
print(f"[OK] CSV confirm import succeeded: {data['count']} values imported")

# 3. Check active dataset in dashboard
resp = client.get('/')
assert resp.status_code == 200
assert b"notes_examen.csv" in resp.content
print("[OK] Active dataset correctly reflects the imported CSV!")

# 4. Test Excel XLSX generation and upload
df = pd.DataFrame({'valeurs_test': [25.0, 30.0, 35.0, 40.0, 45.0, 50.0], 'texte': ['a', 'b', 'c', 'd', 'e', 'f']})
xlsx_buf = io.BytesIO()
df.to_excel(xlsx_buf, index=False)
xlsx_buf.seek(0)
xlsx_file = SimpleUploadedFile("donnees_test.xlsx", xlsx_buf.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

resp = client.post('/api/excel/preview/', {'file': xlsx_file})
assert resp.status_code == 200
data = resp.json()
assert data['success'] is True
assert 'valeurs_test' in data['numeric_columns']
print(f"[OK] XLSX preview succeeded: {data['numeric_columns']}")

xlsx_file.seek(0)
resp = client.post('/api/excel/confirm/', {'file': xlsx_file, 'column_name': 'valeurs_test'})
assert resp.status_code == 200
data = resp.json()
assert data['success'] is True and data['count'] == 6
print(f"[OK] XLSX confirm import succeeded: {data['count']} values imported")

print("\n--- ALL UPLOAD TESTS PASSED SUCCESSFULLY! ---")
