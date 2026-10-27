from django.contrib import admin
from django.utils.html import format_html, mark_safe
from django.utils import timezone
from django.urls import path, reverse
from django.db.models import Count, Avg, Sum
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from .models import (
    Property, PropertyImage, Favorite, Rating, Report,
    Comment, Follow, SavedSearch, Notification, RecentView, UserProfile
)


# ════════════════════════════════════════════════════════════
# DASHBOARD مخصص — لوحة معلومات احصائية ثرية
# ════════════════════════════════════════════════════════════
class AqariAdminSite(admin.AdminSite):
    site_header  = "عقاري السوري  ·  لوحة الإدارة"
    site_title   = "عقاري السوري"
    index_title  = "اللوحة الرئيسية"
    index_template = "admin/dashboard.html"

    def index(self, request, extra_context=None):
        ctx = extra_context or {}
        ctx.update({
            'total_properties': Property.objects.count(),
            'active_properties': Property.objects.filter(is_active=True).count(),
            'total_users': User.objects.count(),
            'total_ratings': Rating.objects.count(),
            'total_favorites': Favorite.objects.count(),
            'total_reports': Report.objects.count(),
            'pending_reports': Report.objects.filter(status='pending').count(),
            'total_views': sum(Property.objects.values_list('views_count', flat=True)),
            'total_comments': Comment.objects.count(),
            'avg_rating': round(Rating.objects.aggregate(a=Avg('score'))['a'] or 0, 1),
            'recent_properties': Property.objects.order_by('-created_at')[:5],
            'recent_users': User.objects.order_by('-date_joined')[:5],
            'recent_reports': Report.objects.order_by('-created_at')[:5],
            'top_cities': Property.objects.values('city').annotate(c=Count('id')).order_by('-c')[:5],
            'top_viewed': Property.objects.order_by('-views_count')[:5],
        })
        return super().index(request, ctx)


# نُحلّ محل admin.site الافتراضي
aqari_admin_site = AqariAdminSite(name='aqari_admin')


# ════════════════════════════════════════════════════════════
# Property — الإدارة الرئيسية
# ════════════════════════════════════════════════════════════
class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ['image', 'caption']


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):

    list_display = [
        'property_image_thumb', 'title_with_link', 'owner_link', 'city',
        'formatted_price', 'property_type_badge', 'status_badge',
        'active_badge', 'rating_display', 'views_display', 'created_at',
    ]
    list_filter   = ['status', 'property_type', 'is_active', 'ad_state', 'is_featured', 'city', 'created_at']
    search_fields = ['title', 'city', 'description', 'owner__username', 'address']
    ordering      = ['-created_at']
    list_per_page = 20
    date_hierarchy = 'created_at'
    list_display_links = None  # نستخدم title_with_link كرابط مخصص
    inlines = [PropertyImageInline]

    # ─── صورة مصغرة احترافية ────────────────────────────
    @admin.display(description='🖼️ الصورة')
    def property_image_thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:60px;height:50px;object-fit:cover;'
                'border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.3);'
                'border:2px solid rgba(201,168,76,0.2);">',
                obj.image.url
            )
        return mark_safe(
            '<div style="width:60px;height:50px;background:linear-gradient(135deg,#1A1F2B,#252A38);'
            'border-radius:8px;display:flex;align-items:center;justify-content:center;'
            'font-size:22px;border:2px solid rgba(255,255,255,0.05);">🏠</div>'
        )

    # ─── عنوان بـ رابط ──────────────────────────────────
    @admin.display(description='🏷️ العنوان')
    def title_with_link(self, obj):
        url = reverse('admin:properties_property_change', args=[obj.pk])
        return format_html(
            '<a href="{}" style="color:#C9A84C;font-weight:700;font-size:14px;'
            'text-decoration:none;">{}</a>'
            '<div style="color:#8A8A96;font-size:11px;margin-top:2px;">{}</div>',
            url, obj.title[:40], obj.address[:35],
        )

    # ─── المالك مع رابط ────────────────────────────────
    @admin.display(description='👤 المالك', ordering='owner__username')
    def owner_link(self, obj):
        return format_html(
            '<span style="background:rgba(74,158,255,0.1);color:#4A9EFF;'
            'padding:4px 10px;border-radius:6px;font-weight:600;font-size:12px;'
            'border:1px solid rgba(74,158,255,0.2);">{}</span>',
            obj.owner.username
        )

    # ─── السعر منسَّق ────────────────────────────────────
    @admin.display(description='💰 السعر', ordering='price')
    def formatted_price(self, obj):
        price = f"{int(obj.price):,}"
        return format_html(
            '<span style="color:#C9A84C;font-weight:800;font-size:14px;">{} </span>'
            '<span style="color:#8A8A96;font-size:11px;">ريال</span>',
            price
        )

    # ─── نوع العقار - شارة ───────────────────────────────
    @admin.display(description='🏘️ النوع', ordering='property_type')
    def property_type_badge(self, obj):
        colors = {
            'apartment': ('#4A9EFF', 'شقة'),
            'villa':     ('#00A699', 'فيلا'),
            'land':      ('#C9A84C', 'أرض'),
            'office':    ('#FF5A5F', 'مكتب'),
            'shop':      ('#A66DD4', 'محل'),
            'building':  ('#FF8C42', 'عمارة'),
        }
        color, label = colors.get(obj.property_type, ('#8A8A96', obj.property_type))
        return format_html(
            '<span style="background:rgba(0,0,0,0.4);color:{};border:1px solid {};'
            'padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700;">{}</span>',
            color, color, label
        )

    # ─── حالة الإعلان ────────────────────────────────────
    @admin.display(description='📋 الحالة', ordering='status')
    def status_badge(self, obj):
        styles = {
            'sale': ('#4A9EFF', '🏷️ للبيع'),
            'rent': ('#E8C96A', '🔑 للإيجار'),
        }
        color, label = styles.get(obj.status, ('#8A8A96', obj.status))
        return format_html(
            '<span style="background:rgba(0,0,0,0.3);color:{};border:1px solid {};'
            'padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700;">{}</span>',
            color, color, label
        )

    # ─── النشاط ─────────────────────────────────────────
    @admin.display(description='⚡ النشاط', ordering='is_active')
    def active_badge(self, obj):
        if obj.is_active:
            return mark_safe(
                '<span style="background:rgba(0,166,153,0.15);color:#00A699;'
                'border:1px solid rgba(0,166,153,0.3);padding:4px 12px;'
                'border-radius:20px;font-size:11px;font-weight:700;">✅ نشط</span>'
            )
        return mark_safe(
            '<span style="background:rgba(138,138,150,0.1);color:#8A8A96;'
            'border:1px solid rgba(138,138,150,0.2);padding:4px 12px;'
            'border-radius:20px;font-size:11px;font-weight:700;">⏸️ معطل</span>'
        )

    # ─── متوسط التقييم ─────────────────────────────────
    @admin.display(description='⭐ التقييم')
    def rating_display(self, obj):
        avg = obj.avg_rating
        count = obj.ratings_count
        if count == 0:
            return mark_safe('<span style="color:#5A5A66;font-size:11px;">— لم يُقيَّم —</span>')
        stars = '⭐' * int(avg) + '☆' * (5 - int(avg))
        return format_html(
            '<div style="line-height:1.2;">'
            '<span style="font-size:11px;letter-spacing:1px;">{}</span>'
            '<div style="color:#C9A84C;font-weight:700;font-size:12px;">{}/5  '
            '<span style="color:#8A8A96;font-weight:400;">({} تقييم)</span></div>'
            '</div>',
            stars, avg, count
        )

    # ─── المشاهدات ───────────────────────────────────
    @admin.display(description='👁️ المشاهدات', ordering='views_count')
    def views_display(self, obj):
        return format_html(
            '<span style="background:rgba(166,109,212,0.1);color:#A66DD4;'
            'padding:4px 10px;border-radius:6px;font-weight:700;font-size:12px;'
            'border:1px solid rgba(166,109,212,0.2);">{}</span>',
            f"{obj.views_count:,}"
        )

    # ─── تنظيم النموذج ─────────────────────────────────
    fieldsets = (
        ('📋 المعلومات الأساسية', {
            'fields': ('owner', 'title', 'description', 'image'),
            'description': '<div style="color:#C9A84C;padding:8px;background:rgba(201,168,76,0.05);border-radius:6px;">معلومات الإعلان الأساسية</div>',
        }),
        ('🏠 تفاصيل العقار', {
            'fields': (('property_type', 'status'), ('price', 'area', 'rooms'), 'is_featured'),
        }),
        ('📍 الموقع', {
            'fields': ('city', 'address'),
        }),
        ('⚙️ الإعدادات والإحصائيات', {
            'fields': (('is_active', 'ad_state'), 'views_count'),
            'classes': ('collapse',),
        }),
    )

    # ─── إجراءات جماعية ─────────────────────────────────
    actions = [
        'activate_properties', 'deactivate_properties',
        'feature_properties', 'unfeature_properties',
        'archive_properties',
    ]

    @admin.action(description='✅ تفعيل المحدد')
    def activate_properties(self, request, queryset):
        n = queryset.update(is_active=True, ad_state='published')
        self.message_user(request, f'تم تفعيل {n} عقاراً')

    @admin.action(description='⏸️ تعطيل المحدد')
    def deactivate_properties(self, request, queryset):
        n = queryset.update(is_active=False)
        self.message_user(request, f'تم تعطيل {n} عقاراً')

    @admin.action(description='⭐ تمييز المحدد')
    def feature_properties(self, request, queryset):
        n = queryset.update(is_featured=True)
        self.message_user(request, f'تم تمييز {n} عقاراً')

    @admin.action(description='○ إلغاء تمييز المحدد')
    def unfeature_properties(self, request, queryset):
        n = queryset.update(is_featured=False)
        self.message_user(request, f'تم إلغاء تمييز {n} عقاراً')

    @admin.action(description='📦 أرشفة المحدد')
    def archive_properties(self, request, queryset):
        n = queryset.update(ad_state='archived', is_active=False)
        self.message_user(request, f'تم أرشفة {n} عقاراً')


# ════════════════════════════════════════════════════════════
# Favorite
# ════════════════════════════════════════════════════════════
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display  = ['user_link', 'property_link', 'added_at']
    search_fields = ['user__username', 'property__title']
    ordering      = ['-added_at']
    list_per_page = 25

    @admin.display(description='👤 المستخدم')
    def user_link(self, obj):
        return format_html(
            '<span style="color:#4A9EFF;font-weight:600;">{}</span>',
            obj.user.username
        )

    @admin.display(description='🏠 العقار')
    def property_link(self, obj):
        return format_html(
            '<span style="color:#C9A84C;font-weight:600;">{}</span>',
            obj.property.title
        )


# ════════════════════════════════════════════════════════════
# Rating
# ════════════════════════════════════════════════════════════
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display  = ['user', 'property', 'stars_display', 'score', 'created_at']
    list_filter   = ['score', 'created_at']
    search_fields = ['user__username', 'property__title']
    list_per_page = 25

    @admin.display(description='⭐ النجوم')
    def stars_display(self, obj):
        stars = '⭐' * obj.score + '☆' * (5 - obj.score)
        return format_html(
            '<span style="font-size:15px;letter-spacing:2px;">{}</span>',
            stars
        )


# ════════════════════════════════════════════════════════════
# Report
# ════════════════════════════════════════════════════════════
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display  = ['status_badge', 'user', 'property_link', 'category_badge', 'short_reason', 'created_at']
    list_filter   = ['status', 'category', 'created_at']
    search_fields = ['user__username', 'property__title', 'reason']
    ordering      = ['-created_at']
    list_per_page = 25
    list_editable = []
    actions = ['mark_resolved', 'mark_rejected']

    @admin.display(description='⚠️ الحالة', ordering='status')
    def status_badge(self, obj):
        styles = {
            'pending':  ('#E8C96A', 'rgba(232,201,106,0.15)', '⏳ قيد المراجعة'),
            'resolved': ('#00A699', 'rgba(0,166,153,0.15)',   '✓ تمت المعالجة'),
            'rejected': ('#8A8A96', 'rgba(138,138,150,0.15)', '✗ مرفوض'),
        }
        color, bg, label = styles.get(obj.status, ('#8A8A96', 'rgba(0,0,0,0.2)', obj.status))
        return format_html(
            '<span style="background:{};color:{};border:1px solid {};'
            'padding:4px 10px;border-radius:20px;font-size:11px;font-weight:700;">{}</span>',
            bg, color, color, label
        )

    @admin.display(description='🏷️ النوع', ordering='category')
    def category_badge(self, obj):
        return format_html(
            '<span style="background:rgba(255,90,95,0.1);color:#FF5A5F;'
            'padding:3px 8px;border-radius:6px;font-size:10px;font-weight:600;'
            'border:1px solid rgba(255,90,95,0.2);">{}</span>',
            obj.get_category_display()
        )

    @admin.display(description='🏠 العقار')
    def property_link(self, obj):
        return format_html(
            '<span style="color:#C9A84C;font-weight:600;">{}</span>',
            obj.property.title
        )

    @admin.display(description='📝 السبب')
    def short_reason(self, obj):
        reason = obj.reason[:50] + '...' if len(obj.reason) > 50 else obj.reason
        return format_html('<span style="color:#8A8A96;font-size:12px;">{}</span>', reason)

    @admin.action(description='✓ علّم كـ معالَج')
    def mark_resolved(self, request, queryset):
        n = queryset.update(status='resolved')
        self.message_user(request, f'تمت معالجة {n} بلاغاً')

    @admin.action(description='✗ علّم كـ مرفوض')
    def mark_rejected(self, request, queryset):
        n = queryset.update(status='rejected')
        self.message_user(request, f'تم رفض {n} بلاغاً')


# ════════════════════════════════════════════════════════════
# Comment, Follow, SavedSearch, Notification, RecentView, UserProfile
# ════════════════════════════════════════════════════════════
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display  = ['user', 'property', 'short_text', 'created_at']
    search_fields = ['user__username', 'property__title', 'text']
    ordering      = ['-created_at']
    list_per_page = 25

    @admin.display(description='💬 التعليق')
    def short_text(self, obj):
        return format_html('<span style="color:#C0C0CC;">{}</span>', obj.text[:60])


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display  = ['follower', 'followed', 'followed_at']
    search_fields = ['follower__username', 'followed__username']
    ordering      = ['-followed_at']
    list_per_page = 25


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display  = ['name', 'user', 'city', 'property_type', 'created_at']
    search_fields = ['name', 'user__username']
    list_per_page = 25


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ['user', 'notif_type', 'short_message', 'is_read', 'created_at']
    list_filter   = ['notif_type', 'is_read']
    search_fields = ['user__username', 'message']
    list_per_page = 25

    @admin.display(description='💭 الرسالة')
    def short_message(self, obj):
        return format_html('<span style="color:#C0C0CC;">{}</span>', obj.message[:60])


@admin.register(RecentView)
class RecentViewAdmin(admin.ModelAdmin):
    list_display  = ['user', 'property', 'viewed_at']
    search_fields = ['user__username', 'property__title']
    list_per_page = 25


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'phone', 'city', 'is_verified', 'created_at']
    search_fields = ['user__username', 'phone', 'city']
    list_filter   = ['is_verified']
    list_per_page = 25


# ════════════════════════════════════════════════════════════
# تخصيص admin.site الافتراضي ليُمرّر بيانات الـ dashboard
# ════════════════════════════════════════════════════════════
admin.site.site_header = "🏠 عقاري السوري  ·  لوحة الإدارة"
admin.site.site_title  = "عقاري السوري"
admin.site.index_title = "اللوحة الرئيسية"

_orig_index = admin.site.index

def _enhanced_index(request, extra_context=None):
    ctx = extra_context or {}
    ctx.update({
        'total_properties': Property.objects.count(),
        'active_properties': Property.objects.filter(is_active=True).count(),
        'total_users': User.objects.count(),
        'total_ratings': Rating.objects.count(),
        'total_favorites': Favorite.objects.count(),
        'total_reports': Report.objects.count(),
        'pending_reports': Report.objects.filter(status='pending').count(),
        'total_views': sum(Property.objects.values_list('views_count', flat=True)),
        'total_comments': Comment.objects.count(),
        'avg_rating': round(Rating.objects.aggregate(a=Avg('score'))['a'] or 0, 1),
        'recent_properties': Property.objects.order_by('-created_at')[:5],
        'recent_users': User.objects.order_by('-date_joined')[:5],
        'recent_reports': Report.objects.order_by('-created_at')[:5],
        'top_cities': Property.objects.values('city').annotate(c=Count('id')).order_by('-c')[:5],
        'top_viewed': Property.objects.order_by('-views_count')[:5],
    })
    return _orig_index(request, ctx)

admin.site.index = _enhanced_index
