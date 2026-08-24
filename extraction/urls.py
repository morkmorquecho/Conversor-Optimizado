from django.urls import path

from .views import (
    ProcessInvoicePdfView,
    ProcessInvoiceXlsxView,
    ProcessInvoiceXmlView,
)

urlpatterns = [
    path(
        "process-xlsx/",
        ProcessInvoiceXlsxView.as_view(),
        name="process-invoice-xlsx",
    ),
    path("process-xml/", ProcessInvoiceXmlView.as_view(), name="process-invoice-xml"),
    path("process-pdf/", ProcessInvoicePdfView.as_view(), name="process-invoice-pdf"),
]
