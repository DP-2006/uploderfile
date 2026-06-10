from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static
from  core import views
from django.conf.urls.static import static
from django.conf import setting

urlpatterns = [
    path('', views.login_view, name='login'),
    path('admin/', admin.site.urls),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin-panel/', views.admin_panel_view, name='admin_panel'),
    path('super-admin/', views.super_admin_panel, name='super_admin_panel'),
    #path('admin-manager/', views.admin_manager_panel, name='admin_manager_panel'),
    path('api/login-logs/', views.login_logs_view, name='login_logs'),
    
    path('api/upload/', views.upload_files_view, name='upload_files'),
    path('api/settings/', views.save_settings_view, name='save_settings'),
    path('api/admin-action/', views.admin_action_view, name='admin_action_api'),
    path('api/super-admin-action/', views.super_admin_action, name='super_admin_action'),
    
    path('api/create-role/', views.create_role, name='create_role'),
    path('api/assign-role/', views.assign_role_to_user, name='assign_role'),
    path('api/toggle-block/', views.toggle_user_block, name='toggle_block'),
    path('api/delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('api/save-permissions/', views.save_permissions, name='save_permissions'),
    # path('api/send-files/', views.send_files_view, name='send_files'),
    path('api/send-files/', views.upload_files_view, name='upload_files_view'),
    path('api/download-file/<int:file_id>/', views.download_file_view, name='download_file'),
    path('api/admin-delete-file/', views.admin_delete_file_view, name='admin_delete_file'),
    path('api/users/', views.get_users_view, name='get_users'),
    path('admin-manager/', views.admin_manager_panel, name='admin_manager_panel'),
    path('api/my-files/', views.api_my_files, name='api_my_files'),
    path('api/send-files/', views.api_send_files, name='api_send_files'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
