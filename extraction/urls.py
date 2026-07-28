from django.urls import path

from .views import ProcessInvoiceXlsxView

urlpatterns = [
    path(
        "process-xlsx/",
        ProcessInvoiceXlsxView.as_view(),
        name="process-invoice-xlsx",
    ),
]