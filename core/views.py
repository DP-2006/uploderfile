# views.py

import os
import json
import re
from django.conf import Settings
from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone
from .models import (
    FileActionLog, UploadedFile, UserSettings, UserProfile, PasswordPolicy,
    GroupLeader, LoginLog
)

# ========================= Helper Functions =========================

def get_or_create_settings(user):
    """Get or create user settings"""
    settings, created = UserSettings.objects.get_or_create(user=user)
    return settings

# ========================= Login View =========================

def login_view(request):
    """Handle user login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        success = user is not None

        # Record login attempt
        LoginLog.objects.create(
            user=user,
            ip_address=request.META.get('REMOTE_ADDR'),
            success=success
        )

        if user:
            login(request, user)
            return JsonResponse({'success': True, 'uid': user.id, 'role': 'admin' if user.is_staff else 'user'})
        else:
            return JsonResponse({'success': False, 'msg': 'نام کاربری یا رمز عبور اشتباه است'})
    return render(request, 'login.html')

# ========================= Dashboard =========================

@login_required
def dashboard_view(request):
    """User dashboard showing uploaded files"""
    settings = get_or_create_settings(request.user)
    # Get files uploaded by user for left sidebar display
    my_files = UploadedFile.objects.filter(uploaded_by=request.user, is_deleted=False).order_by('-uploaded_at')
    return render(request, 'dashboard.html', {'settings': settings, 'my_files': my_files})

# ========================= File Upload API =========================

@csrf_exempt
@login_required
def upload_files_view(request):
    """Handle file uploads with .exe rejection"""
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        folder_name = request.POST.get('folder_name', 'Unknown')
        uploaded_count = 0
        rejected_count = 0
        for f in files:
            if f.name.lower().endswith('.exe'):
                rejected_count += 1
                continue
            UploadedFile.objects.create(file=f, uploaded_by=request.user, folder_name=folder_name)
            uploaded_count += 1  # Increment uploaded count
        msg = f'{uploaded_count} فایل آپلود شد.'
        if rejected_count > 0:
            msg += f' {rejected_count} فایل EXE مجاز نبود و رد شد.'
        return JsonResponse({'success': True, 'msg': msg})
    return JsonResponse({'success': False, 'msg': 'خطا در آپلود'})

# ========================= Settings API =========================

@csrf_exempt
@login_required
def save_settings_view(request):
    """Save user interface settings"""
    if request.method == 'POST':
        data = json.loads(request.body)
        settings = get_or_create_settings(request.user)
        settings.font_size = int(data.get('font_size', 14))
        settings.menu_size = int(data.get('menu_size', 200))
        settings.button_size = int(data.get('button_size', 40))
        settings.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

# ========================= Admin Panel =========================

@login_required
def admin_panel_view(request):
    """Admin panel view for staff users"""
    if not request.user.is_staff:
        return redirect('dashboard')
    users = User.objects.all()
    history = UploadedFile.objects.select_related('uploaded_by').all().order_by('-uploaded_at')
    return render(request, 'admin_panel.html', {'users': users, 'history': history})

# ========================= Admin Actions =========================

@csrf_exempt
@login_required
def admin_action_view(request):
    """Handle admin actions: create user, change password, block/unblock, delete file"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'msg': 'Unauthorized'})

    if request.method != 'POST':
        return JsonResponse({'success': False, 'msg': 'متد نامعتبر'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'msg': 'داده نامعتبر'}, status=400)

    action = data.get('action')

    # Block user action
    if action == 'block_user':
        user_id = data.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'msg': 'شناسه کاربر نامعتبر'})

        try:
            user = User.objects.get(id=user_id)

            # Prevent blocking self
            if user.id == request.user.id:
                return JsonResponse({'success': False, 'msg': 'نمی‌توانید خودتان را مسدود کنید'})

            user.is_active = False
            user.save()

            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.is_blocked = True
            profile.blocked_at = timezone.now()
            profile.save()

            return JsonResponse({'success': True, 'msg': f'کاربر {user.username} مسدود شد'})

        except User.DoesNotExist:
            return JsonResponse({'success': False, 'msg': 'کاربر یافت نشد'})

    # Unblock user action
    elif action == 'unblock_user':
        user_id = data.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'msg': 'شناسه کاربر نامعتبر'})

        try:
            user = User.objects.get(id=user_id)

            user.is_active = True
            user.save()

            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.is_blocked = False
            profile.blocked_at = None
            profile.save()

            return JsonResponse({'success': True, 'msg': f'کاربر {user.username} آزاد شد'})

        except User.DoesNotExist:
            return JsonResponse({'success': False, 'msg': 'کاربر یافت نشد'})

    # Create user action
    elif action == 'create_user':
        username = data.get('username')
        password = data.get('password')
        is_staff = data.get('is_staff', False)
        groups = data.get('groups', [])

        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'msg': 'نام کاربری تکراری است'})

        user = User.objects.create_user(username=username, password=password)
        user.is_staff = is_staff
        user.save()

        if groups:
            group_objs = Group.objects.filter(id__in=groups)
            user.groups.set(group_objs)

        UserProfile.objects.get_or_create(user=user)
        return JsonResponse({'success': True, 'msg': 'کاربر جدید ساخته شد'})

    # Change password action
    elif action == 'change_password':
        user = get_object_or_404(User, id=data.get('user_id'))
        user.set_password(data.get('new_password'))
        user.save()
        return JsonResponse({'success': True, 'msg': 'رمز عبور تغییر کرد'})

    # Delete file action
    elif action == 'delete_file':
        f = get_object_or_404(UploadedFile, id=data.get('file_id'))
        f.delete()
        return JsonResponse({'success': True, 'msg': 'فایل حذف شد'})

    return JsonResponse({'success': False, 'msg': 'Invalid action'})

# ========================= User APIs (for sharing) =========================

@login_required
@require_http_methods(["GET"])
def api_users(request):
    """Get list of users"""
    users = User.objects.exclude(id=request.user.id).values('id', 'username', 'first_name', 'last_name')
    return JsonResponse(list(users), safe=False)

@login_required
@require_http_methods(["GET"])
def api_my_files(request):
    """Get files uploaded by current user"""
    files = File.objects.filter(user=request.user).values(
        'id', 'file_name', 'file_size', 'uploaded_at', 'file'
    )
    return JsonResponse(list(files), safe=False)

@login_required
@require_http_methods(["POST"])
def api_send_files(request):
    """Send files to another user"""
    try:
        data = json.loads(request.body)
        recipient_id = data.get('recipient_id')
        file_ids = data.get('file_ids', [])

        if not recipient_id:
            return JsonResponse({'success': False, 'msg': 'کاربر مقصد مشخص نشده'})

        if not file_ids:
            return JsonResponse({'success': False, 'msg': 'فایلی انتخاب نشده'})

        try:
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'msg': 'کاربر یافت نشد'})

        shared_count = 0
        for file_id in file_ids:
            try:
                file_obj = File.objects.get(id=file_id, user=request.user)
                share, created = FileShare.objects.get_or_create(
                    file=file_obj,
                    to_user=recipient,
                    defaults={'from_user': request.user}
                )
                if created:
                    shared_count += 1
            except File.DoesNotExist:
                continue

        return JsonResponse({
            'success': True,
            'msg': f'{shared_count} فایل با موفقیت ارسال شد'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'msg': str(e)})

@login_required
@require_http_methods(["GET"])
def api_shared_with_me(request):
    """Get files shared with current user"""
    shares = FileShare.objects.filter(to_user=request.user).select_related('file', 'from_user')
    files = []
    for share in shares:
        files.append({
            'id': share.file.id,
            'file_name': share.file.file_name,
            'file_size': share.file.file_size,
            'file_url': share.file.file.url,
            'shared_by': f"{share.from_user.first_name} {share.from_user.last_name}".strip() or share.from_user.username,
            'shared_at': share.shared_at.strftime('%Y/%m/%d %H:%M')
        })
    return JsonResponse(files, safe=False)

# ========================= Super Admin Panel =========================

@login_required
def super_admin_panel(request):
    """Super admin panel view"""
    # Check user status
    if not request.user.is_superuser:
        messages.error(request, "شما دسترسی به این صفحه را ندارید!")
        return redirect('/dashboard/')

    # Get or create password policy settings
    policy, created = PasswordPolicy.objects.get_or_create(pk=1)

    # Get all permissions
    all_perms = Permission.objects.all()

    # Get all users with their profiles
    users = User.objects.select_related('userprofile').all()

    # Get all groups
    all_roles = Group.objects.all()

    context = {
        'policy': policy,
        'all_perms': all_perms,
        'users': users,
        'all_roles': all_roles,
    }
    return render(request, 'super_admin_panel.html', context)

# ========================= Super Admin Actions API =========================

@csrf_exempt
@login_required
def super_admin_action(request):
    """Handle super admin actions"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'msg': 'دسترسی غیرمجاز'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')

            if action == 'update_policy':
                # Update password policy
                policy = PasswordPolicy.objects.first()
                if policy:
                    policy.min_password_length = data.get('min_length')
                    policy.require_uppercase = data.get('require_uppercase')
                    policy.require_digit = data.get('require_digit')
                    policy.require_special_char = data.get('require_special_char')
                    policy.save()
                return JsonResponse({'success': True, 'msg': 'سیاست رمز عبور با موفقیت ذخیره شد.'})

            elif action == 'create_role_with_perms':
                # Create new role with permissions
                role_name = data.get('role_name')
                perm_ids = data.get('permissions')
                leader_id = data.get('leader_id')

                if not role_name:
                    return JsonResponse({'success': False, 'msg': 'نام نقش نمی‌تواند خالی باشد.'})

                # Check for duplicate role name
                if Group.objects.filter(name=role_name).exists():
                    return JsonResponse({'success': False, 'msg': 'نقش با این نام قبلاً وجود دارد'})

                # Create new role
                group = Group.objects.create(name=role_name)

                # Assign permissions
                if perm_ids:
                    permissions = Permission.objects.filter(id__in=perm_ids)
                    group.permissions.set(permissions)

                # Assign group leader
                if leader_id:
                    try:
                        leader = User.objects.get(id=leader_id)
                        GroupLeader.objects.create(group=group, leader=leader)
                    except User.DoesNotExist:
                        pass

                return JsonResponse({'success': True, 'msg': f'نقش {role_name} با موفقیت ساخته شد.'})

            return JsonResponse({'success': False, 'msg': 'درخواست نامعتبر است.'})

        except Exception as e:
            return JsonResponse({'success': False, 'msg': str(e)})

# ========================= Login Logs View =========================

@login_required
def login_logs_view(request):
    """View login logs for super admin"""
    if not request.user.is_superuser:
        return redirect('dashboard')

    logs = LoginLog.objects.all().order_by('-login_time')
    paginator = Paginator(logs, 6)  # 6 logs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'total_logs': logs.count()
    }

    return render(request, 'login_logs.html', context)

# ========================= Create Role (Form View) =========================

@login_required
def create_role(request):
    """Create new role with group leader limit (max 2 groups per leader)"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'دسترسی ندارید'}, status=403)

    if request.method == 'POST':
        role_name = request.POST.get('role_name')
        leader_id = request.POST.get('leader_id')
        permissions = request.POST.getlist('permissions')

        if not role_name:
            messages.error(request, 'نام نقش نمی‌تواند خالی باشد')
            return redirect('super_admin_panel')

        try:
            # Check for duplicate role name
            if Group.objects.filter(name=role_name).exists():
                messages.error(request, f'نقش با نام "{role_name}" قبلاً وجود دارد')
            else:
                group = Group.objects.create(name=role_name)

                # Assign permissions
                if permissions:
                    group.permissions.set(permissions)

                # Assign group leader with limit check
                if leader_id:
                    try:
                        leader = User.objects.get(id=leader_id)

                        # Check leader limit (max 2 groups per leader)
                        current_leader_groups = GroupLeader.objects.filter(leader=leader).count()

                        if current_leader_groups >= 2:
                            messages.error(request, f'کاربر {leader.username} قبلاً رهبر 2 گروه است. امکان اختصاص گروه جدید وجود ندارد.')
                        else:
                            GroupLeader.objects.create(group=group, leader=leader)
                            messages.success(request, f'نقش "{role_name}" با موفقیت ایجاد شد')
                    except User.DoesNotExist:
                        messages.error(request, 'کاربر مورد نظر برای رهبری یافت نشد')
                else:
                    messages.success(request, f'نقش "{role_name}" با موفقیت ایجاد شد')

        except Exception as e:
            messages.error(request, f'خطا در ایجاد نقش: {str(e)}')

        return redirect('super_admin_panel')

    return redirect('super_admin_panel')

# ========================= Assign Role to User =========================

@login_required
def assign_role_to_user(request):
    """Assign or remove role from user"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'دسترسی ندارید'}, status=403)

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        role_id = request.POST.get('role_id')
        action = request.POST.get('action', 'add')

        try:
            user = User.objects.get(id=user_id)
            role = Group.objects.get(id=role_id)

            if action == 'add':
                user.groups.add(role)
                message = f'نقش {role.name} به کاربر {user.username} اضافه شد'
            else:
                user.groups.remove(role)
                message = f'نقش {role.name} از کاربر {user.username} حذف شد'

            return JsonResponse({'success': True, 'message': message})

        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'کاربر یافت نشد'}, status=404)

        except Group.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'نقش یافت نشد'}, status=404)

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'error': 'متد نامعتبر'}, status=405)

# ========================= Toggle User Block =========================

@login_required
def toggle_user_block(request):
    """Toggle user block status"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'دسترسی ندارید'}, status=403)

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            # Prevent blocking self
            if user.id == request.user.id:
                return JsonResponse({'success': False, 'error': 'نمی‌توانید خودتان را مسدود کنید'}, status=400)

            profile, created = UserProfile.objects.get_or_create(user=user)
            # Toggle block status
            profile.is_blocked = not profile.is_blocked
            if profile.is_blocked:
                from django.utils import timezone
                profile.blocked_at = timezone.now()
                user.is_active = False
            else:
                profile.blocked_at = None
                user.is_active = True

            profile.save()
            user.save()

            status = 'مسدود' if profile.is_blocked else 'فعال'
            return JsonResponse({
                'success': True,
                'message': f'کاربر {user.username} {status} شد',
                'is_blocked': profile.is_blocked
            })

        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'کاربر یافت نشد'}, status=404)

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'error': 'متد نامعتبر'}, status=405)

# ========================= Delete User =========================

@login_required
def delete_user(request, user_id):
    """Delete a user (superadmin only)"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'دسترسی ندارید'}, status=403)

    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            # Prevent deleting self
            if user.id == request.user.id:
                return JsonResponse({'success': False, 'error': 'نمی‌توانید خودتان را حذف کنید'}, status=400)

            username = user.username
            user.delete()
            return JsonResponse({'success': True, 'message': f'کاربر {username} با موفقیت حذف شد'})

        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'کاربر یافت نشد'}, status=404)

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'error': 'متد نامعتبر'}, status=405)

# ========================= Edit User =========================

@login_required
def edit_user(request, user_id):
    """Edit user information page"""
    if not request.user.is_superuser:
        return redirect('login')

    user = get_object_or_404(User, id=user_id)
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        # Update user info
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.is_active = request.POST.get('is_active') == 'on'
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.save()

        # Update profile
        profile.first_name = user.first_name
        profile.last_name = user.last_name
        profile.national_code = request.POST.get('national_code', '')
        profile.save()

        messages.success(request, f'اطلاعات کاربر {user.username} با موفقیت به‌روزرسانی شد')
        return redirect('super_admin_panel')

    context = {
        'edit_user': user,
        'profile': profile,
        'all_roles': Group.objects.all(),
    }
    return render(request, 'edit_user.html', context)

# ========================= Save Permissions for Role =========================

@login_required
def save_permissions(request):
    """Save permissions for a role"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'دسترسی ندارید'}, status=403)

    if request.method == 'POST':
        role_id = request.POST.get('role_id')
        permissions = request.POST.getlist('permissions')

        if not role_id:
            messages.error(request, 'لطفاً یک نقش انتخاب کنید')
            return redirect('super_admin_panel')

        try:
            role = Group.objects.get(id=role_id)
            # Clear existing permissions and set new ones
            role.permissions.clear()
            if permissions:
                role.permissions.set(permissions)
            messages.success(request, f'دسترسی‌ها برای نقش {role.name} با موفقیت ذخیره شد')

        except Group.DoesNotExist:
            messages.error(request, 'نقش مورد نظر یافت نشد')

        except Exception as e:
            messages.error(request, f'خطا: {str(e)}')

        return redirect('super_admin_panel')

    return redirect('super_admin_panel')

# ========================= Admin Manager Panel =========================

@login_required
def admin_manager_panel(request):
    """Admin manager panel view"""
    if not request.user.is_staff:
        return render(request, 'login.html')

    users = User.objects.all()
    history = UploadedFile.objects.filter(is_deleted=False)
    all_roles = Group.objects.all()

    # Debug output
    print("=" * 50)
    print(f"[admin_manager_panel] Number of groups: {all_roles.count()}")
    print(f"[admin_manager_panel] Group list: {list(all_roles.values_list('name', flat=True))}")
    print("=" * 50)

    context = {
        'users': users,
        'history': history,
        'all_roles': all_roles,
    }
    return render(request, 'admin_panel.html', context)

# ========================= User Detail View =========================

@login_required
def user_detail_view(request, user_id):
    """View complete user details for super admin"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'msg': 'دسترسی غیرمجاز'}, status=403)

    try:
        user = User.objects.select_related('userprofile').get(id=user_id)
        profile = user.userprofile

        user_groups = user.groups.all()
        user_permissions = user.user_permissions.all()
        led_groups = GroupLeader.objects.filter(leader=user).select_related('group')
        recent_uploads = UploadedFile.objects.filter(uploaded_by=user).order_by('-uploaded_at')[:10]
        login_history = LoginLog.objects.filter(user=user).order_by('-login_time')[:5]

        context = {
            'target_user': user,
            'profile': profile,
            'user_groups': user_groups,
            'user_permissions': user_permissions,
            'led_groups': led_groups,
            'recent_uploads': recent_uploads,
            'login_history': login_history,
        }

        return render(request, 'user_detail.html', context)

    except User.DoesNotExist:
        messages.error(request, 'کاربر یافت نشد')
        return redirect('super_admin_panel')

# ========================= Get Users List (for sharing) =========================

@csrf_exempt
@login_required
def get_users_view(request):
    """Get list of active users for file sharing"""
    if request.method == 'GET':
        users = User.objects.filter(is_active=True).values('id', 'first_name', 'last_name', 'username')
        return JsonResponse(list(users), safe=False)
    return JsonResponse({'success': False, 'msg': 'متد نامعتبر'})

# ========================= Send Files View =========================

@csrf_exempt
@login_required
def send_files_view(request):
    """Send files to another user with optional cloud storage"""
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        files = request.FILES.getlist('files')
        save_to_cloud = request.POST.get('save_to_cloud', 'true') == 'true'

        if not recipient_id or not files:
            return JsonResponse({'success': False, 'msg': 'اطلاعات ناقص'})

        try:
            recipient = User.objects.get(id=recipient_id)

            if save_to_cloud:
                for f in files:
                    if f.name.lower().endswith('.exe'):
                        continue
                    # Create file for recipient
                    UploadedFile.objects.create(
                        file=f,
                        uploaded_by=request.user,  # Original sender
                        folder_name='ارسال شده',
                        save_to_cloud=True,
                        sent_to_user=recipient
                    )

                FileActionLog.objects.create(
                    user=request.user,
                    action='send',
                    file_name=', '.join([f.name for f in files]),
                    recipient_user=recipient,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    details=f'ارسال فایل به {recipient.username} - ذخیره در فضای ابری: بله'
                )

                return JsonResponse({'success': True, 'msg': f'فایل‌ها با موفقیت ارسال و در فضای ابری ذخیره شدند'})
            else:
                FileActionLog.objects.create(
                    user=request.user,
                    action='send',
                    file_name=', '.join([f.name for f in files]),
                    recipient_user=recipient,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    details=f'ارسال فایل به {recipient.username} - ذخیره در فضای ابری: خیر'
                )

                return JsonResponse({'success': True, 'msg': 'فایل‌ها ارسال شدند (بدون ذخیره در فضای ابری)'})

        except User.DoesNotExist:
            return JsonResponse({'success': False, 'msg': 'کاربر مورد نظر یافت نشد'})

    return JsonResponse({'success': False, 'msg': 'متد نامعتبر'})

# ========================= Download File with Logging =========================

@login_required
def download_file_view(request, file_id):
    """Download file with logging"""
    try:
        uploaded_file = UploadedFile.objects.get(id=file_id, is_deleted=False)

        # Check access: admin/superadmin or file owner
        if not (request.user.is_staff or request.user.is_superuser or uploaded_file.uploaded_by == request.user):
            return JsonResponse({'success': False, 'msg': 'دسترسی ندارید'}, status=403)

        # Create download log
        FileActionLog.objects.create(
            user=request.user,
            action='download',
            file_name=uploaded_file.file.name,
            file_size=uploaded_file.file.size,
            ip_address=request.META.get('REMOTE_ADDR'),
            details=f'دانلود فایل توسط {request.user.username}'
        )

        return redirect(uploaded_file.file.url)

    except UploadedFile.DoesNotExist:
        return JsonResponse({'success': False, 'msg': 'فایل یافت نشد'}, status=404)

# ========================= Admin Delete File with Logging =========================

@csrf_exempt
@login_required
def admin_delete_file_view(request):
    """Delete file by admin with full logging"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'msg': 'دسترسی غیرمجاز'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            file_id = data.get('file_id')

            uploaded_file = UploadedFile.objects.get(id=file_id)

            file_name = uploaded_file.file.name
            file_size = uploaded_file.file.size
            uploaded_by = uploaded_file.uploaded_by.username

            if uploaded_file.file:
                uploaded_file.file.delete()
            uploaded_file.delete()

            # Create delete log with full details
            FileActionLog.objects.create(
                user=request.user,
                action='delete',
                file_name=file_name,
                file_size=file_size,
                ip_address=request.META.get('REMOTE_ADDR'),
                details=f'حذف فایل توسط ادمین {request.user.username} - مالک اصلی: {uploaded_by}'
            )

            return JsonResponse({'success': True, 'msg': 'فایل با موفقیت حذف شد'})

        except UploadedFile.DoesNotExist:
            return JsonResponse({'success': False, 'msg': 'فایل یافت نشد'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'msg': str(e)}, status=400)

    return JsonResponse({'success': False, 'msg': 'متد نامعتبر'}, status=405)

# ========================= Additional Login Logs View (Duplicate Protection) =========================
# Note: This appears to be a duplicate; kept as-is per your request.

@login_required
def login_logs_view(request):
    """View login logs for super admin"""
    if not request.user.is_superuser:
        return redirect('dashboard')

    logs = LoginLog.objects.all().order_by('-login_time')
    paginator = Paginator(logs, 6)  # 6 logs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'total_logs': logs.count()
    }
    return render(request, 'login_logs.html', context)
