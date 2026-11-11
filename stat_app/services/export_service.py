import io
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from .stats_service import calculate_central_tendencies, calculate_variability

def export_stats_to_excel(data):
    """
    Generate an Excel workbook with statistical calculations and return bytes.
    """
    wb = openpyxl.Workbook()

    # Style definitions
    header_font = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
    header_fill = PatternFill(start_color='4F46E5', end_color='4F46E5', fill_type='solid')
    sub_fill = PatternFill(start_color='EEF2FF', end_color='EEF2FF', fill_type='solid')
    title_font = Font(name='Calibri', size=14, bold=True, color='1E1B4B')
    bold_font = Font(name='Calibri', size=11, bold=True)
    regular_font = Font(name='Calibri', size=11)
    thin_border = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )

    # 1. Sheet: Données
    ws_data = wb.active
    ws_data.title = "Données Brutes"
    ws_data.views.sheetView[0].showGridLines = True

    ws_data['A1'] = "Application de Statistiques & Probabilités — Série de Données"
    ws_data['A1'].font = title_font
    ws_data.merge_cells('A1:D1')

    headers_data = ["Index (i)", "Valeur (x_i)", "Écart (x_i - x̄)", "Écart² (x_i - x̄)²"]
    for col_idx, h in enumerate(headers_data, start=1):
        cell = ws_data.cell(row=3, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center')

    mean_val = float(sum(data)) / len(data) if data else 0.0

    for idx, val in enumerate(data, start=1):
        diff = val - mean_val
        diff_sq = diff ** 2
        r = idx + 3
        c1 = ws_data.cell(row=r, column=1, value=idx)
        c2 = ws_data.cell(row=r, column=2, value=val)
        c3 = ws_data.cell(row=r, column=3, value=round(diff, 4))
        c4 = ws_data.cell(row=r, column=4, value=round(diff_sq, 4))
        for c in (c1, c2, c3, c4):
            c.border = thin_border
            c.font = regular_font
            c.alignment = Alignment(horizontal='right')
        c1.alignment = Alignment(horizontal='center')

    # Total row
    tot_row = len(data) + 4
    ws_data.cell(row=tot_row, column=1, value="Somme").font = bold_font
    ws_data.cell(row=tot_row, column=2, value=sum(data)).font = bold_font
    ws_data.cell(row=tot_row, column=3, value=0.0).font = bold_font
    ws_data.cell(row=tot_row, column=4, value=sum((x - mean_val)**2 for x in data)).font = bold_font

    # 2. Sheet: Synthèse Statistique
    ws_summary = wb.create_sheet(title="Synthèse Statistique")
    ws_summary.views.sheetView[0].showGridLines = True

    ws_summary['A1'] = "Rapport Statistique Détaillé"
    ws_summary['A1'].font = title_font
    ws_summary.merge_cells('A1:C1')

    ct = calculate_central_tendencies(data)
    var = calculate_variability(data)

    headers_sum = ["Indicateur", "Valeur Calculée", "Formule / Définition"]
    for col_idx, h in enumerate(headers_sum, start=1):
        cell = ws_summary.cell(row=3, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center')

    rows_info = [
        ("Nombre d'observations (n)", len(data), "Effectif total de la série"),
        ("Moyenne arithmétique (x̄)", ct['mean']['value'], "x̄ = Σ x_i / n"),
        ("Médiane (Me)", ct['median']['value'], "Valeur centrale (50% supérieurs, 50% inférieurs)"),
        ("Mode (Mo)", ct['mode']['value_formatted'], "Valeur(s) la (les) plus fréquente(s)"),
        ("Étendue (E)", var['range']['value'], "E = x_max - x_min"),
        ("Variance Échantillon (s²)", var['variance']['val_sample'], "s² = Σ (x_i - x̄)² / (n - 1)"),
        ("Variance Population (σ²)", var['variance']['val_pop'], "σ² = Σ (x_i - μ)² / N"),
        ("Écart-type Échantillon (s)", var['std_dev']['val_sample'], "s = √(s²)"),
        ("Écart-type Population (σ)", var['std_dev']['val_pop'], "σ = √(σ²)"),
        ("Premier Quartile (Q1)", var['quartiles']['q1'], "25% des observations lui sont inférieures"),
        ("Troisième Quartile (Q3)", var['quartiles']['q3'], "75% des observations lui sont inférieures"),
        ("Écart Interquartile (IQR)", var['quartiles']['iqr'], "IQR = Q3 - Q1"),
        ("Coefficient de variation", var['quartiles']['cv_percent'], "CV = (s / x̄) * 100%"),
    ]

    for idx, (ind, val, form) in enumerate(rows_info, start=4):
        c1 = ws_summary.cell(row=idx, column=1, value=ind)
        c2 = ws_summary.cell(row=idx, column=2, value=val)
        c3 = ws_summary.cell(row=idx, column=3, value=form)
        c1.font = bold_font
        c2.font = regular_font
        c3.font = regular_font
        for c in (c1, c2, c3):
            c.border = thin_border

    # Adjust column widths
    for ws in (ws_data, ws_summary):
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 14)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()
