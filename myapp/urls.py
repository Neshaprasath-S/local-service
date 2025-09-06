
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from . import views

app_name = 'mainapp'

urlpatterns = [
   path('admin/', admin.site.urls),
   path('', views.home, name='home'),
   path('about/', views.about, name='about'),
   path('login/', views.login, name='login'),
   path('register/', views.register, name='register'),
   path("service/", views.service, name='service'),
   path('providerdetails/<str:provider_slug>/',views.providerdetails,name="providerdetails"),
   path('dashboard/',views.dashboard,name="dashboard"),
   path('customer/profile/',views.CustomerProfile,name='CustomerProfile'),
   path('provider/profile/',views.ProviderProfile,name='ProviderProfile'),
   path('provider/profile/create/', views.ProviderProfileCreate, name='ProviderProfileCreate'),
   path('changepassword/', views.changepassword, name='changepassword'),
   path('customer/profile/edit/', views.CustomerProfileEdit, name='CustomerProfileEdit'),
   path('provider/profile/edit/', views.ProviderProfileEdit, name='ProviderProfileEdit'),
   path('logout/', views.logout, name='logout'),
   path('service/booking/<str:provider_slug>/', views.service_booking, name='service_booking'),
   path('add_previous_work/', views.Add_previous_work, name='Add_previous_work'),
   path('booking/status/update/<int:booking_id>/<str:action>/', views.update_booking_status, name='update_booking_status'),
   path('booking/review/<int:booking_id>/', views.booking_review, name='booking_review'),
   path('rewrite_booking_review/<int:review_id>/', views.rewrite_booking_review, name='rewrite_booking_review'),
   path('previous_work/edit/<int:work_id>/', views.previous_work_Edit, name='previous_work_Edit'),
   path('previous_work/delete/<int:work_id>/', views.previous_work_delete, name='previous_work_delete'),
   path('forgotpassword/', views.forgotpassword, name='forgotpassword'),
] #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)