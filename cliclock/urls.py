"""
URL configuration for cliclock project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

from scenario import views


urlpatterns = [
    path('admin/', admin.site.urls),

    path("stats/get_all", views.get_all_stats),

    path("player/get_all", views.get_all_players),
    path("puzzle/get_all", views.get_all_puzzles),

    path("player/<str:player_slug>/get_data", views.get_player_data),
    path("player/<str:player_slug>/exist", views.player_exist),
    path("player/<str:player_slug>/move_item", views.move_item),
    path("player/<str:player_slug>/puzzle/<str:puzzle_slug>/display", views.display_puzzle),
    path("player/<str:player_slug>/puzzle/<str:puzzle_slug>/unlock", views.unlock_puzzle),
    path("player/<str:player_slug>/puzzle/<str:puzzle_slug>/solve", views.solve_puzzle),

    path("trade/start", views.trade_start),
    path("trade/<str:trade_id>/accept", views.trade_accept),
    path("trade/<str:trade_id>/withdraw", views.trade_withdraw),
    path("trade/<str:trade_id>/update", views.trade_update),
    path("trade/<str:trade_id>/cancel", views.trade_cancel),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]
