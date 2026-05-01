
# from django.contrib import admin
# from .models import UploadedFile, UserSettings, DownloaderFile, UserProfile, PasswordPolicy

# # برای نمایش UserProfile در کنار کاربر
# class UserProfileInline(admin.StackedInline):
#     model = UserProfile
#     can_delete = False
#     verbose_name_plural = 'پروفایل'

# class UserAdmin(admin.ModelAdmin):
#     inlines = (UserProfileInline, )

# # لغو ثبت قبلی و ثبت مجدد User برای اضافه کردن Inline
# from django.contrib.auth.models import User
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)

# admin.site.register(UploadedFile)
# admin.site.register(UserSettings)
# admin.site.register(DownloaderFile)
# admin.site.register(PasswordPolicy)
    

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),  
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('api/upload/', views.upload_files_view, name='upload_files'),
    path('api/settings/', views.save_settings_view, name='save_settings'),
    path('admin-panel/', views.admin_panel_view, name='admin_panel'),
    # path('api/admin-action/', views.admin_action_view, name='admin_action'),  
    path('super-admin/', views.super_admin_panel, name='super_admin_panel'),
    path('api/super-admin-action/', views.super_admin_action, name='super_admin_action'),
    #path('admin-manager/', views.admin_manager_panel, name='admin_panel.html'),

#     path('api/admin-action/', views.admin_action_api, name='admin_action_api'),  
#     path('api/admin-action/', views.admin_action_api, name='admin_action_api'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)










# your_app/admin.py

from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    UserSettings, 
    DownloaderFile, 
    UserProfile, 
    PasswordPolicy, 
    GroupLeader, 
    FileActionLog,
    UploadedFile
)

# سفارشی‌سازی User Admin
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_groups')
    list_filter = ('is_staff', 'is_superuser', 'groups')
    
    def get_groups(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])
    get_groups.short_description = 'نقش‌ها'
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'email')}),
        ('دسترسی‌ها', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('تاریخ‌ها', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'groups'),
        }),
    )
    
    filter_horizontal = ('groups', 'user_permissions',)

# ثبت مدل‌ها
admin.site.register(UserSettings)
admin.site.register(DownloaderFile)
admin.site.register(UserProfile)
admin.site.register(PasswordPolicy)
admin.site.register(GroupLeader)
admin.site.register(FileActionLog)
admin.site.register(UploadedFile)

# ثبت User Admin سفارشی
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)