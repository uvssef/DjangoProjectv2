import io
import re
import numpy as np
import pandas as pd

DEFAULT_DATASET = [12.0, 15.0, 18.0, 20.0, 15.0, 25.0, 30.0]

PRESET_DATASETS = {
    'cours': {
        'name': 'Exemple du cours (7 valeurs)',
        'data': [12.0, 15.0, 18.0, 20.0, 15.0, 25.0, 30.0],
        'desc': 'Exemple officiel de référence : 12, 15, 18, 20, 15, 25, 30'
    },
    'notes': {
        'name': 'Notes d\'étudiants (15 valeurs)',
        'data': [11.5, 14.0, 8.5, 16.0, 12.0, 15.5, 9.0, 14.0, 13.5, 17.0, 10.0, 14.0, 12.5, 15.0, 18.0],
        'desc': 'Distribution typique d\'une classe d\'étudiants'
    },
    'outliers': {
        'name': 'Distribution avec Outlier (10 valeurs)',
        'data': [10.0, 12.0, 11.5, 13.0, 12.0, 11.0, 10.5, 12.5, 11.8, 85.0],
        'desc': 'Idéal pour comparer la moyenne (sensible) et la médiane (robuste)'
    },
    'bimodale': {
        'name': 'Distribution bimodale (12 valeurs)',
        'data': [5.0, 5.0, 5.0, 6.0, 7.0, 8.0, 14.0, 15.0, 15.0, 15.0, 16.0, 17.0],
        'desc': 'Deux modes distincts (5 et 15)'
    }
}


def get_active_dataset(request):
    """Retrieve active dataset list from session or default if missing."""
    session_data = request.session.get('dataset')
    if session_data is None or not isinstance(session_data, list) or len(session_data) == 0:
        return list(DEFAULT_DATASET)
    # Ensure float conversion
    try:
        return [float(x) for x in session_data]
    except (ValueError, TypeError):
        return list(DEFAULT_DATASET)


def set_active_dataset(request, data, source_name='Saisie manuelle'):
    """Save cleaned float dataset into session."""
    cleaned = [float(x) for x in data if np.isfinite(x)]
    request.session['dataset'] = cleaned
    request.session['dataset_source'] = source_name
    request.session.modified = True
    return cleaned


def parse_manual_input(text):
    """
    Parse a text string containing numbers separated by commas, spaces, semicolons, or newlines.
    Handles French comma decimals ('12,5' -> 12.5) when separated by spaces/newlines,
    or comma-separated lists ('12, 15, 18').
    Returns:
        valid_numbers: list of floats
        invalid_tokens: list of strings that couldn't be parsed
    """
    if not text or not text.strip():
        return [], []

    raw = text.strip()
    
    # Check if string uses comma as list separator vs comma as decimal separator.
    # If there are semicolons, newlines, or spaces between comma-decimal numbers like "12,5 14,2"
    if ';' in raw or '\n' in raw:
        # Split by newline or semicolon first
        tokens = re.split(r'[;\n\r\t]+', raw)
    elif ',' in raw and ' ' not in raw:
        # Standard CSV single line "12,15,18,20"
        tokens = raw.split(',')
    else:
        # Can have commas or spaces
        # If pattern looks like "12.5, 15, 18.2" or "12, 15, 18"
        tokens = re.split(r'[, \t\n\r]+', raw)

    valid_numbers = []
    invalid_tokens = []

    for t in tokens:
        item = t.strip()
        if not item:
            continue
        # Normalize french comma decimal if needed (e.g. "12,5" -> "12.5")
        normalized = item.replace(',', '.')
        try:
            val = float(normalized)
            if np.isfinite(val):
                valid_numbers.append(val)
            else:
                invalid_tokens.append(item)
        except ValueError:
            invalid_tokens.append(item)

    return valid_numbers, invalid_tokens


def inspect_uploaded_file(uploaded_file):
    """
    Inspect an uploaded XLSX, XLS, or CSV file.
    Returns:
        dict with:
            success: bool
            filename: str
            columns: list of column names
            numeric_columns: list of numeric column names
            preview_rows: list of dicts (up to 5 rows)
            total_rows: int
            error: str (if any)
    """
    filename = uploaded_file.name.lower()
    try:
        content = uploaded_file.read()
        uploaded_file.seek(0)
        
        if filename.endswith('.csv'):
            # Try utf-8 then latin-1, try comma or semicolon
            try:
                df = pd.read_csv(io.BytesIO(content), sep=None, engine='python', encoding='utf-8')
            except Exception:
                df = pd.read_csv(io.BytesIO(content), sep=None, engine='python', encoding='latin-1')
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(content))
        else:
            return {
                'success': False,
                'error': "Format non supporté. Veuillez importer un fichier .xlsx, .xls ou .csv"
            }

        # Identify numeric columns
        numeric_cols = []
        for col in df.columns:
            # Check if column is numeric or can be converted to numeric
            converted = pd.to_numeric(df[col], errors='coerce')
            valid_count = converted.notna().sum()
            if valid_count > 0:
                numeric_cols.append(str(col))

        preview_df = df.head(5).fillna('')
        preview_rows = preview_df.to_dict(orient='records')

        return {
            'success': True,
            'filename': uploaded_file.name,
            'columns': [str(c) for c in df.columns],
            'numeric_columns': numeric_cols,
            'preview_rows': preview_rows,
            'total_rows': len(df),
            'error': None
        }

    except Exception as e:
        return {
            'success': False,
            'error': f"Erreur lors de la lecture du fichier : {str(e)}"
        }


def extract_column_data_from_file(uploaded_file, column_name):
    """
    Extract numeric float data from the specified column of an uploaded file.
    """
    filename = uploaded_file.name.lower()
    try:
        content = uploaded_file.read()
        if filename.endswith('.csv'):
            try:
                df = pd.read_csv(io.BytesIO(content), sep=None, engine='python', encoding='utf-8')
            except Exception:
                df = pd.read_csv(io.BytesIO(content), sep=None, engine='python', encoding='latin-1')
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(content))
        else:
            return None, "Format de fichier invalide."

        if column_name not in df.columns:
            # Try string match
            matches = [c for c in df.columns if str(c) == str(column_name)]
            if matches:
                column_name = matches[0]
            else:
                return None, f"Colonne '{column_name}' introuvable."

        series = pd.to_numeric(df[column_name], errors='coerce').dropna()
        data = [float(x) for x in series.tolist() if np.isfinite(x)]
        if len(data) == 0:
            return None, "La colonne sélectionnée ne contient aucune valeur numérique valide."
        return data, None
    except Exception as e:
        return None, f"Erreur d'extraction : {str(e)}"


def add_value(request, val):
    data = get_active_dataset(request)
    data.append(float(val))
    return set_active_dataset(request, data, source_name="Modification manuelle")


def edit_value(request, index, new_val):
    data = get_active_dataset(request)
    if 0 <= index < len(data):
        data[index] = float(new_val)
        return set_active_dataset(request, data, source_name="Modification manuelle")
    return data


def delete_value(request, index):
    data = get_active_dataset(request)
    if 0 <= index < len(data):
        data.pop(index)
        return set_active_dataset(request, data, source_name="Modification manuelle")
    return data


def clear_dataset(request):
    request.session['dataset'] = []
    request.session['dataset_source'] = "Données effacées"
    request.session.modified = True
    return []


def reset_to_default(request, preset_key='cours'):
    preset = PRESET_DATASETS.get(preset_key, PRESET_DATASETS['cours'])
    return set_active_dataset(request, preset['data'], source_name=preset['name'])
