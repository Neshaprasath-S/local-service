from django.contrib import admin
from .models import All_User, CustomerProfileModel, ProviderProfileModel

# Register your models here.



class All_UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number', 'is_customer', 'is_service_provider')
    search_fields = ('username', 'email')
    list_filter = ('is_customer', 'is_service_provider')


class CustomerProfileModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'username', 'mobile_no', 'email', 'district', 'city')
    search_fields = ('user__username', 'email')
    list_filter = ('district', 'city')
    

class ProviderProfileModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'username', 'service_name', 'mobile_no', 'email', 'district', 'city')
    search_fields = ('user__username', 'email', 'service_name')
    list_filter = ('district', 'city')
    


admin.site.register(All_User, All_UserAdmin)
admin.site.register(CustomerProfileModel, CustomerProfileModelAdmin)
admin.site.register(ProviderProfileModel, ProviderProfileModelAdmin)



