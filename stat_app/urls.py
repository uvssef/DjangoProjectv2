from django.urls import path
from . import views

app_name = 'stat_app'

urlpatterns = [
    # Navigation Categories
    path('', views.dashboard_view, name='dashboard'),
    path('visualisations/', views.data_visualizations_view, name='visualizations'),
    path('visualisations/telecharger/<str:chart_name>/', views.download_chart_png, name='download_chart_png'),
    path('tendances-centrales/', views.central_tendencies_view, name='central'),
    path('tendances-variabilite/', views.variability_view, name='variability'),
    path('analyse-combinatoire/', views.combinatorics_view, name='combinatorics'),
    path('probabilite-discrete/', views.discrete_probability_view, name='discrete'),
    path('probabilite-conditionnelle/', views.conditional_probability_view, name='conditional'),
    path('lois-de-probabilite/', views.distributions_view, name='distributions'),

    # Data Actions & APIs
    path('api/data/manual/', views.api_update_manual_data, name='api_manual'),
    path('api/data/add/', views.api_add_value, name='api_add'),
    path('api/data/edit/', views.api_edit_value, name='api_edit'),
    path('api/data/delete/', views.api_delete_value, name='api_delete'),
    path('api/data/clear/', views.api_clear_data, name='api_clear'),
    path('api/data/preset/', views.api_load_preset, name='api_preset'),
    path('api/excel/preview/', views.api_upload_excel_preview, name='api_excel_preview'),
    path('api/excel/confirm/', views.api_confirm_excel_import, name='api_excel_confirm'),
    path('export/excel/', views.api_export_excel, name='export_excel'),
]
