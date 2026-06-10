


from django.db import models
from django.contrib.auth.models import User, Group, Permission


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, verbose_name="نام")
    last_name = models.CharField(max_length=100, verbose_name="نام خانوادگی")
    national_code = models.CharField(max_length=10, verbose_name="کد ملی")
    is_blocked = models.BooleanField(default=False)
    blocked_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.user.username


class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    font_size = models.IntegerField(default=14)
    menu_size = models.IntegerField(default=200)
    button_size = models.IntegerField(default=40)
    
    def __str__(self):
        return f"Settings for {self.user.username}"


class PasswordPolicy(models.Model):
    min_password_length = models.IntegerField(default=8)
    require_uppercase = models.BooleanField(default=True)
    require_digit = models.BooleanField(default=True)
    require_special_char = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "سیاست رمز عبور"
        verbose_name_plural = "سیاست‌های رمز عبور"
    
    def save(self, *args, **kwargs):
        if not self.pk and PasswordPolicy.objects.exists():
            return PasswordPolicy.objects.first().save(update_fields=[])
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return "تنظیمات رمز عبور"


class GroupLeader(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_groups')
    
    class Meta:
        unique_together = ('group', 'leader')
    
    def __str__(self):
        return f"{self.leader.username} - رهبر گروه {self.group.name}"


class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    folder_name = models.CharField(max_length=255, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    save_to_cloud = models.BooleanField(default=True)
    sent_to_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_files'
    )
    
    def __str__(self):
        return self.file.name


class FileActionLog(models.Model):
    ACTION_CHOICES = [
        ('download', 'دانلود'),
        ('delete', 'حذف'),
        ('upload', 'آپلود'),
        ('send', 'ارسال'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField(null=True)
    ip_address = models.GenericIPAddressField(null=True)
    action_time = models.DateTimeField(auto_now_add=True)
    recipient_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_file_logs'
    )
    details = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-action_time']
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.file_name}"


class File(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.file_name


class FileShare(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='shares')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_shares')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_shares')
    shared_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['file', 'to_user']
        ordering = ['-shared_at']
    
    def __str__(self):
        return f"{self.file.file_name} → {self.to_user.username}"


class DownloaderFile(models.Model):
    file = models.FileField(upload_to='downloads/')
    downloaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.file.name


class LoginLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    login_time = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time} - {'Success' if self.success else 'Failed'}"
