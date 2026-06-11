


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

admin.site.register(UserSettings)
admin.site.register(DownloaderFile)
admin.site.register(UserProfile)
admin.site.register(PasswordPolicy)
admin.site.register(GroupLeader)
admin.site.register(FileActionLog)
admin.site.register(UploadedFile)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
