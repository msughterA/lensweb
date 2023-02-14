"""lensweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.urls import path, include
from django_tus.views import TusUpload, FileDownloadListAPIView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("examples", include("examples.urls")),
    path("ocr", include("ocr.urls")),
    path("accounts/", include("accounts.urls")),
    path("payments/", include("payments.urls")),
    path("summarizer/", include("summarizer.urls")),
    path("mathematics/", include("mathematics.urls")),
    path("chemistry/", include("chemistry.urls")),
    path("upload/", TusUpload.as_view(), name="tus_upload"),
    path("upload/<uuid:resource_id>", TusUpload.as_view(), name="tus_upload_chunks"),
    path("gst/", include("gst.urls")),
    path("notifications/", include("notification.urls")),
]
