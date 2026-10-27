from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ════════════════════════════════════════
# REQ-10  العقار الرئيسي
# ════════════════════════════════════════
class Property(models.Model):

    PROPERTY_TYPES = [
        ('apartment', 'شقة'),
        ('villa',     'فيلا'),
        ('land',      'أرض'),
        ('office',    'مكتب'),
        ('shop',      'محل تجاري'),
        ('building',  'عمارة'),
    ]

    STATUS = [
        ('sale', 'للبيع'),
        ('rent', 'للإيجار'),
    ]

    AD_STATE = [
        ('draft',     'مسودة'),
        ('published', 'منشور'),
        ('archived',  'مؤرشف'),
    ]

    # المحافظات السورية الـ 14
    SYRIAN_GOVERNORATES = [
        ('دمشق',         'دمشق'),
        ('ريف دمشق',     'ريف دمشق'),
        ('حلب',          'حلب'),
        ('حمص',          'حمص'),
        ('حماة',         'حماة'),
        ('اللاذقية',     'اللاذقية'),
        ('طرطوس',        'طرطوس'),
        ('إدلب',         'إدلب'),
        ('درعا',         'درعا'),
        ('السويداء',     'السويداء'),
        ('القنيطرة',     'القنيطرة'),
        ('دير الزور',    'دير الزور'),
        ('الحسكة',       'الحسكة'),
        ('الرقة',        'الرقة'),
    ]

    owner         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_properties')
    title         = models.CharField(max_length=200)
    description   = models.TextField()
    price         = models.DecimalField(max_digits=12, decimal_places=2)
    city          = models.CharField(max_length=100, choices=SYRIAN_GOVERNORATES)
    address       = models.CharField(max_length=300)
    area          = models.FloatField()
    rooms         = models.IntegerField()
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPES)
    status        = models.CharField(max_length=10, choices=STATUS)
    image         = models.ImageField(upload_to='properties/', blank=True, null=True)
    is_active     = models.BooleanField(default=True)
    ad_state      = models.CharField(max_length=20, choices=AD_STATE, default='published')
    is_featured   = models.BooleanField(default=False)
    views_count   = models.IntegerField(default=0)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def avg_rating(self):
        """متوسط التقييم - REQ-24"""
        ratings = self.rating_set.all()
        if not ratings:
            return 0
        return round(sum(r.score for r in ratings) / len(ratings), 1)

    @property
    def ratings_count(self):
        """عدد التقييمات - REQ-55"""
        return self.rating_set.count()

    @property
    def favorites_count(self):
        """عدد المفضلة - REQ-54"""
        return self.favorite_set.count()


# ════════════════════════════════════════
# REQ-22  صور إضافية للعقار
# ════════════════════════════════════════
class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image    = models.ImageField(upload_to='property_images/')
    caption  = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at']

    def __str__(self):
        return f"صورة لـ {self.property.title}"


# ════════════════════════════════════════
# REQ-15,16,17  المفضلة
# ════════════════════════════════════════
class Favorite(models.Model):
    user     = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'property')

    def __str__(self):
        return f"{self.user} - {self.property}"


# ════════════════════════════════════════
# REQ-11  التقييم
# ════════════════════════════════════════
class Rating(models.Model):
    user     = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    score    = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'property')

    def __str__(self):
        return f"{self.user} - {self.score}"


# ════════════════════════════════════════
# REQ-23  البلاغات
# ════════════════════════════════════════
class Report(models.Model):
    REPORT_REASONS = [
        ('fake',       'إعلان وهمي'),
        ('duplicate',  'إعلان مكرر'),
        ('inappropriate', 'محتوى غير لائق'),
        ('wrong_price', 'سعر خاطئ'),
        ('other',      'سبب آخر'),
    ]

    STATUS = [
        ('pending',  'قيد المراجعة'),
        ('resolved', 'تمت المعالجة'),
        ('rejected', 'مرفوض'),
    ]

    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    property   = models.ForeignKey(Property, on_delete=models.CASCADE)
    reason     = models.TextField()
    category   = models.CharField(max_length=20, choices=REPORT_REASONS, default='other')
    status     = models.CharField(max_length=20, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.user}"


# ════════════════════════════════════════
# REQ-44,45,46  التعليقات والردود
# ════════════════════════════════════════
class Comment(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    property   = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='comments')
    text       = models.TextField(max_length=500)
    parent     = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user}: {self.text[:30]}"


# ════════════════════════════════════════
# REQ-40,41,42  المتابعة
# ════════════════════════════════════════
class Follow(models.Model):
    follower    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
    followed    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_set')
    followed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')

    def __str__(self):
        return f"{self.follower} → {self.followed}"


# ════════════════════════════════════════
# REQ-47  حفظ البحث
# ════════════════════════════════════════
class SavedSearch(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    name       = models.CharField(max_length=100)
    query      = models.CharField(max_length=200, blank=True)
    city       = models.CharField(max_length=100, blank=True)
    property_type = models.CharField(max_length=50, blank=True)
    status     = models.CharField(max_length=10, blank=True)
    min_price  = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_price  = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ════════════════════════════════════════
# REQ-48,49,50,51  التنبيهات
# ════════════════════════════════════════
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('comment',    'تعليق جديد'),
        ('rating',     'تقييم جديد'),
        ('favorite',   'إضافة للمفضلة'),
        ('follow',     'متابع جديد'),
        ('property',   'عقار جديد'),
        ('system',     'إشعار النظام'),
    ]

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    actor      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    notif_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message    = models.CharField(max_length=300)
    link       = models.CharField(max_length=300, blank=True)
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user}: {self.message[:30]}"


# ════════════════════════════════════════
# REQ-58  العقارات المُشاهَدة مؤخراً
# ════════════════════════════════════════
class RecentView(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    property   = models.ForeignKey(Property, on_delete=models.CASCADE)
    viewed_at  = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'property')
        ordering = ['-viewed_at']

    def __str__(self):
        return f"{self.user} viewed {self.property}"


# ════════════════════════════════════════
# REQ-60  ملف شخصي موسَّع
# ════════════════════════════════════════
class UserProfile(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone       = models.CharField(max_length=20, blank=True)
    bio         = models.TextField(max_length=500, blank=True)
    avatar      = models.ImageField(upload_to='avatars/', blank=True, null=True)
    city        = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
