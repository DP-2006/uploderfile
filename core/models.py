
# from django.db import models
# from django.contrib.auth.models import User
# from django.db import models
# from django.contrib.auth.models import User, Permission, Group


# # class UploadedFile(models.Model):
# #     file = models.FileField(upload_to='')
# #     uploaded_at = models.DateTimeField(auto_now_add=True)
# #     uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
# #     folder_name = models.CharField(max_length=255, blank=True, null=True)
# #     is_deleted = models.BooleanField(default=False)

# #     def __str__(self):
# #         return self.file.name



# class UserSettings(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     font_size = models.IntegerField(default=14)
#     menu_size = models.IntegerField(default=200)
#     button_size = models.IntegerField(default=40)

#     def __str__(self):
#         return f"Settings for {self.user.username}"



# class DownloaderFile(models.Model):  
#     file = models.FileField(upload_to='downloads/')
#     downloaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
#     def __str__(self):
#         return self.file.name



# # class Control_user_(models.Model):
# #     pass 

# # مدل پروفایل کاربر برای ذخیره اطلاعات تکمیلی


# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     first_name = models.CharField(max_length=100, verbose_name="نام")
#     last_name = models.CharField(max_length=100, verbose_name="نام خانوادگی")
#     national_code = models.CharField(max_length=10, verbose_name="کد ملی")
#     is_blocked = models.BooleanField(default=False)
#     blocked_at = models.DateTimeField(null=True, blank=True)


#     def __str__(self):
#         return self.user.username



# # مدل تنظیمات سیاست رمز عبور
# class PasswordPolicy(models.Model):
#     min_password_length = models.IntegerField(default=8, verbose_name="حداقل طول رمز")
#     require_uppercase = models.BooleanField(default=True, verbose_name="نیاز به حروف بزرگ")
#     require_digit = models.BooleanField(default=True, verbose_name="نیاز به عدد")
#     require_special_char = models.BooleanField(default=False, verbose_name="نیاز به کاراکتر خاص")


#     class Meta:
#         verbose_name = "سیاست رمز عبور"
#         verbose_name_plural = "سیاست‌های رمز عبور"


#     def save(self, *args, **kwargs):
#         # مطمئن می‌شویم فقط یک ردیف از تنظیمات وجود داشته باشد
#         if not self.pk and PasswordPolicy.objects.exists():
#             return PasswordPolicy.objects.first().save(update_fields=[])
#         return super().save(*args, **kwargs)


#     def __str__(self):
#         return "تنظیمات رمز عبور"




# class GroupLeader(models.Model):
#     group = models.OneToOneField(Group, on_delete=models.CASCADE)
#     leader = models.ForeignKey(User, on_delete=models.CASCADE)
    
#     class Meta:
#         unique_together = ('group', 'leader')



# class LoginLog(models.Model):
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
#     ip_address = models.GenericIPAddressField(null=True, blank=True)
#     login_time = models.DateTimeField(auto_now_add=True )
#     success = models.BooleanField(default=False)
#     attempts = models.IntegerField(default=0)
    
#     def __str__(self):
#         return f"{self.user.username} - {self.login_time} - {'Success' if self.success else 'Failed'}"



# # اضافه کردن فیلد جدید به مدل UploadedFile
# class UploadedFile(models.Model):
#     file = models.FileField(upload_to='uploads/')
#     uploaded_at = models.DateTimeField(auto_now_add=True)
#     uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
#     folder_name = models.CharField(max_length=255, blank=True, null=True)
#     is_deleted = models.BooleanField(default=False)
#     # فیلد جدید برای ذخیره در فضای ابری
#     save_to_cloud = models.BooleanField(default=True, verbose_name="ذخیره در فضای ابری")
#     # فیلد برای نگهداری فایل ارسال شده به کاربر دیگر
#     sent_to_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_files')

#     def __str__(self):
#         return self.file.name


# # مدل برای مدیریت رهبری گروه‌ها
# class GroupLeader(models.Model):
#     group = models.OneToOneField(Group, on_delete=models.CASCADE)
#     leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_groups')
    
#     class Meta:
#         unique_together = ('group', 'leader')
    
#     def __str__(self):
#         return f"{self.leader.username} - رهبر گروه {self.group.name}"
    


# # مدل لاگ برای ردیابی عملیات روی فایل‌ها - مشکل 5
# class FileActionLog(models.Model):

#     ACTION_CHOICES = [
#         ('download', 'دانلود'),
#         ('delete', 'حذف'),
#         ('upload', 'آپلود'),
#         ('send', 'ارسال'),
#     ]

    
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
#     action = models.CharField(max_length=20, choices=ACTION_CHOICES)
#     file_name = models.CharField(max_length=255)
#     file_size = models.BigIntegerField(null=True, blank=True)
#     ip_address = models.GenericIPAddressField(null=True, blank=True)
#     action_time = models.DateTimeField(auto_now_add=True)
#     recipient_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_file_logs')
#     details = models.TextField(blank=True, null=True)
    
#     class Meta:
#         ordering = ['-action_time']
#         verbose_name = 'لاگ عملیات فایل'
#         verbose_name_plural = 'لاگ‌های عملیات فایل'
    
#     def __str__(self):
#         return f"{self.user.username} - {self.get_action_display()} - {self.file_name}"























































# # models.py

# from django.db import models
# from django.contrib.auth.models import User

# class File(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
#     file = models.FileField(upload_to='uploads/%Y/%m/%d/')
#     file_name = models.CharField(max_length=255)
#     file_size = models.BigIntegerField()
#     uploaded_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         ordering = ['-uploaded_at']
    
#     def __str__(self):
#         return self.file_name

# class FileShare(models.Model):
#     file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='shares')
#     from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_shares')
#     to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_shares')
#     shared_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         unique_together = ['file', 'to_user']
#         ordering = ['-shared_at']
    
#     def __str__(self):
#         return f"{self.file.file_name} → {self.to_user.username}"



















































# from django.db import models
# from django.contrib.auth.models import User, Group


# class UploadedFile(models.Model):
#     file = models.FileField(upload_to='uploads/')
#     uploaded_at = models.DateTimeField(auto_now_add=True)
#     uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
#     folder_name = models.CharField(max_length=255, blank=True, null=True)
#     is_deleted = models.BooleanField(default=False)
#     save_to_cloud = models.BooleanField(default=True)
#     sent_to_user = models.ForeignKey(
#         User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_files'
#     )
#     def __str__(self): return self.file.name


# class UserSettings(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     font_size = models.IntegerField(default=14)
#     menu_size = models.IntegerField(default=200)
#     def __str__(self): return f"Settings for {self.user.username}"


# class DownloaderFile(models.Model):
#     file = models.FileField(upload_to="downloads/")
#     downloaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
#     def __str__(self): return self.file.name


# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     national_code = models.CharField(max_length=10)
#     is_blocked = models.BooleanField(default=False)
#     blocked_at = models.DateTimeField(null=True, blank=True)
#     def __str__(self): return self.user.username


# class PasswordPolicy(models.Model):
#     min_password_length = models.IntegerField(default=8)
#     require_uppercase = models.BooleanField(default=True)
#     require_digit = models.BooleanField(default=True)
#     require_special_char = models.BooleanField(default=False)

#     class Meta:
#         verbose_name = "سیاست رمز عبور"
#         verbose_name_plural = "سیاست‌های رمز عبور"

#     def save(self, *args, **kwargs):
#         if not self.pk and PasswordPolicy.objects.exists():
#             return PasswordPolicy.objects.first().save(update_fields=[])
#         return super().save(*args, **kwargs)


# class GroupLeader(models.Model):
#     group = models.OneToOneField(Group, on_delete=models.CASCADE)
#     leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_groups')

#     class Meta:
#         unique_together = ('group', 'leader')

#     def __str__(self): return f"{self.leader.username} - رهبر گروه {self.group.name}"


# class FileActionLog(models.Model):
#     ACTION_CHOICES = [
#         ('download', 'دانلود'),
#         ('delete', 'حذف'),
#         ('upload', 'آپلود'),
#         ('send', 'ارسال'),
#     ]

#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     action = models.CharField(max_length=20, choices=ACTION_CHOICES)
#     file_name = models.CharField(max_length=255)
#     file_size = models.BigIntegerField(null=True)
#     ip_address = models.GenericIPAddressField(null=True)
#     action_time = models.DateTimeField(auto_now_add=True)
#     recipient_user = models.ForeignKey(
#         User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_file_logs'
#     )
#     details = models.TextField(blank=True, null=True)

#     class Meta:
#         ordering = ['-action_time']

#     # def __str__(self): return f"{self.user} - {self.action} - {self.file_name}

# #core core/__pycache__ core/migrations core/__init__.py core/admin.py core/apps.py core/models.py core/tests.py core/views.py kiosk kiosk/__pycache__ kiosk/__init__.py kiosk/asgi.py kiosk/main.py kiosk/settings.py kiosk/urls.py kiosk/wsgi.py templates templates/admin_panel.html templates/dashboard.html templates/login.html templates/super_admin_panel.html uploads uploads/1f0eaaf8d4b2a44b3ec94aaa026ef50c_2fgj1fn.mp4 uploads/1f0eaaf8d4b2a44b3ec94aaa026ef50c_3mq0ZzF.mp4 uploads/1f0eaaf8d4b2a44b3ec94aaa026ef50c_GWNuJaI.mp4 uploads/1f0eaaf8d4b2a44b3ec94aaa026ef50c.mp4 uploads/2d9c181852a550b642f8b361719dc6f5_GcbdB8w.mp4 uploads/2d9c181852a550b642f8b361719dc6f5.mp4 uploads/8b294e2da5819290b01940668a9222d6_aeNlEF3.mp4 uploads/8b294e2da5819290b01940668a9222d6_t79XNUl.mp4 uploads/8b294e2da5819290b01940668a9222d6.mp4 uploads/14bc82288ad9b25171472220697b1c85_NxOyqPM.mp4 uploads/14bc82288ad9b25171472220697b1c85.mp4 uploads/barrty-status_HNEzUIF.txt uploads/barrty-status.txt uploads/ceasar.png uploads/df7eda2817af797a953de90780bfb51e_d2SQcVl.mp4 uploads/df7eda2817af797a953de90780bfb51e_wMplgl6.mp4 uploads/df7eda2817af797a953de90780bfb51e.mp4 uploads/Episode_01_-_Structure_of_Cell_M7lvhya.pdf uploads/Episode_01_-_Structure_of_Cell.pdf uploads/Episode_02_-_DNA_Structure_and_Replication_xSn53aW.pdf uploads/Episode_02_-_DNA_Structure_and_Replication.pdf uploads/Episode_03_-_RNA_Structure_u88mO0r.pdf uploads/Episode_03_-_RNA_Structure.pdf uploads/Episode_04_-_Protein_N4aB2ej.pdf uploads/Episode_04_-_Protein.pdf uploads/Episode_05_-_Pairwise_Alignment_FuCSSXg.pdf uploads/Episode_05_-_Pairwise_Alignment.pdf uploads/Episode_06_-_Multiple_Alignment_1_RnibKeX.pdf uploads/Episode_06_-_Multiple_Alignment_1.pdf uploads/Episode_06_-_Multiple_Alignment_DWvAcEI.pdf uploads/Episode_06_-_Multiple_Alignment.pdf uploads/Episode_07_-_Microarray_NGS_Sequencing_MNihMVQ.pdf uploads/Episode_07_-_Microarray_NGS_Sequencing.pdf uploads/Episode_08_-_Short_Read_Alignment_1_8oi3LyW.pdf uploads/Episode_08_-_Short_Read_Alignment_1.pdf uploads/Episode_08_-_Short_Read_Alignment_vPAAOuI.pdf uploads/Episode_08_-_Short_Read_Alignment.pdf uploads/Episode_09_-_Hypothesis_Testing_1_l3FZQkR.pdf uploads/Episode_09_-_Hypothesis_Testing_1.pdf uploads/Episode_09_-_Hypothesis_Testing_gAXVSaH.pdf uploads/Episode_09_-_Hypothesis_Testing.pdf uploads/Episode_10_-_Bulk_RNA_Seq_Analysis_dsTopFs.pdf uploads/Episode_10_-_Bulk_RNA_Seq_Analysis.pdf uploads/Episode_11_-_Evolutionary_Tree_TqGk4C4.pdf uploads/Episode_11_-_Evolutionary_Tree.pdf uploads/Episode_12_-_BLAST__FASTA-Shorten_ME5sOzX.pdf uploads/Episode_12_-_BLAST__FASTA-Shorten.pdf uploads/Episode_13_-_Motifs_Finding_BqnPCOK.pdf uploads/Episode_13_-_Motifs_Finding.pdf uploads/Episode_14_-_Single_Cell_xpGi2pe.pdf uploads/Episode_14_-_Single_Cell.pdf uploads/french_fries.png uploads/hamburger.png uploads/Help_For_Project_-_FastQ_FastQC_vk3I2Mb.pdf uploads/Help_For_Project_-_FastQ_FastQC.pdf uploads/Hw20 uploads/Hw20_yrqjgCq uploads/images.png uploads/p uploads/part1.css uploads/part1.html uploads/part1.js uploads/part5.mp4 uploads/part6.mp4 uploads/salad.png uploads/soda.png uploads/TinyURL.zip venv venv/bin venv/include venv/lib venv/lib64 venv/pyvenv.cfg db.sqlite3 manage.py README.md




































# models.py - نسخه تمیز و بدون تکرار

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