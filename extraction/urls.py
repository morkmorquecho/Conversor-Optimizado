from django.urls import path

from .views import ProcessInvoiceXlsxView, ProcessInvoiceXmlView

urlpatterns = [
    path(
        "process-xlsx/",
        ProcessInvoiceXlsxView.as_view(),
        name="process-invoice-xlsx",
    ),
    path("process-xml/", ProcessInvoiceXmlView.as_view(), name="process-invoice-xml"),
]