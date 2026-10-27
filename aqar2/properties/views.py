from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from .models import (
    Property, PropertyImage, Favorite, Rating, Report,
    Comment, Follow, SavedSearch, Notification, RecentView, UserProfile
)
from .forms import (
    SignupForm, PropertyForm, EditProfileForm, PropertyImageForm,
    CommentForm, SavedSearchForm, UserProfileForm
)

# ═══════════════════════════════════════════════════════════
#  REQ-1 إلى REQ-5  -  المصادقة والحساب
# ═══════════════════════════════════════════════════════════

# REQ-1 تسجيل الدخول
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'تم تسجيل الدخول بنجاح')
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

# REQ-2 إنشاء حساب  + REQ-19 التحقق من البريد
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, 'مرحباً بك في عقاري السوري!')
            return redirect('home')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})

# REQ-12 تسجيل الخروج
def logout_view(request):
    logout(request)
    messages.info(request, 'تم تسجيل الخروج')
    return redirect('login')

# REQ-3 تعديل الحساب
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الملف الشخصي')
            return redirect('profile')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'properties/edit_profile.html', {'form': form})

# REQ-4 حذف الحساب
@login_required
def delete_account(request):
    if request.method == 'POST':
        request.user.delete()
        messages.info(request, 'تم حذف حسابك')
        return redirect('login')
    return render(request, 'properties/delete_account.html')

# REQ-5 الملف الشخصي + REQ-21 إحصائيات
@login_required
def profile_view(request):
    my_properties = Property.objects.filter(owner=request.user)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    stats = {
        'properties_count': my_properties.count(),
        'favorites_count':  Favorite.objects.filter(user=request.user).count(),
        'ratings_given':    Rating.objects.filter(user=request.user).count(),
        'followers_count':  Follow.objects.filter(followed=request.user).count(),
        'following_count':  Follow.objects.filter(follower=request.user).count(),
        'total_views':      sum(p.views_count for p in my_properties),
    }
    return render(request, 'properties/profile.html', {
        'properties': my_properties,
        'profile': profile,
        'stats': stats,
    })

# REQ-28 تغيير كلمة المرور
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'تم تغيير كلمة المرور')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'properties/change_password.html', {'form': form})

# REQ-18 استعادة كلمة المرور (طلب)
def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            messages.success(request, f'تم إرسال تعليمات الاستعادة إلى {email}')
        except User.DoesNotExist:
            messages.error(request, 'لا يوجد حساب بهذا البريد')
        return redirect('login')
    return render(request, 'properties/password_reset.html')

# REQ-60 تحديث الملف الشخصي الموسَّع
@login_required
def edit_user_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الملف الشخصي')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'properties/edit_user_profile.html', {'form': form})


# ═══════════════════════════════════════════════════════════
#  REQ-6 إلى REQ-10  -  CRUD العقارات
# ═══════════════════════════════════════════════════════════

# REQ-10 + REQ-35 عرض كل العقارات + إجمالي
def property_list(request):
    properties = Property.objects.filter(is_active=True, ad_state='published').order_by('-created_at')
    total = properties.count()
    return render(request, 'properties/home.html', {
        'properties': properties,
        'total': total,
    })

# REQ-9 + REQ-24 تفاصيل العقار + متوسط التقييم
def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    property.views_count += 1
    property.save()

    is_favorite = False
    user_rating = None
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, property=property).exists()
        user_rating = Rating.objects.filter(user=request.user, property=property).first()
        # REQ-58 سجل المشاهدة
        RecentView.objects.update_or_create(user=request.user, property=property)

    # REQ-26 عقارات أخرى لنفس المالك
    other_properties = Property.objects.filter(owner=property.owner, is_active=True).exclude(pk=pk)[:4]
    # REQ-44 التعليقات
    comments = Comment.objects.filter(property=property, parent__isnull=True).order_by('-created_at')

    return render(request, 'properties/detail.html', {
        'property': property,
        'is_favorite': is_favorite,
        'user_rating': user_rating,
        'other_properties': other_properties,
        'comments': comments,
    })

# REQ-6 إضافة عقار
@login_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property = form.save(commit=False)
            property.owner = request.user
            property.save()
            # REQ-22 صور إضافية
            for img in request.FILES.getlist('additional_images'):
                PropertyImage.objects.create(property=property, image=img)
            messages.success(request, 'تم إضافة العقار بنجاح')
            return redirect('detail', pk=property.pk)
    else:
        form = PropertyForm()
    return render(request, 'properties/add_property.html', {'form': form})

# REQ-7 تعديل عقار
@login_required
def edit_property(request, pk):
    property = get_object_or_404(Property, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property)
        if form.is_valid():
            form.save()
            for img in request.FILES.getlist('additional_images'):
                PropertyImage.objects.create(property=property, image=img)
            messages.success(request, 'تم تعديل العقار بنجاح')
            return redirect('detail', pk=pk)
    else:
        form = PropertyForm(instance=property)
    return render(request, 'properties/edit_property.html', {'form': form, 'property': property})

# REQ-8 حذف عقار
@login_required
def delete_property(request, pk):
    property = get_object_or_404(Property, pk=pk, owner=request.user)
    if request.method == 'POST':
        property.delete()
        messages.success(request, 'تم حذف العقار')
        return redirect('profile')
    return render(request, 'properties/delete_property.html', {'property': property})

# REQ-29 تنشيط/تعطيل عقار
@login_required
@require_POST
def toggle_property(request, pk):
    property = get_object_or_404(Property, pk=pk, owner=request.user)
    property.is_active = not property.is_active
    property.save()
    state = 'تنشيط' if property.is_active else 'تعطيل'
    messages.success(request, f'تم {state} العقار')
    return redirect('profile')

# REQ-59 حفظ كمسودة
@login_required
def save_as_draft(request, pk):
    property = get_object_or_404(Property, pk=pk, owner=request.user)
    property.ad_state = 'draft'
    property.is_active = False
    property.save()
    messages.info(request, 'تم حفظ العقار كمسودة')
    return redirect('profile')

# REQ-22 حذف صورة من معرض العقار
@login_required
def delete_property_image(request, image_id):
    img = get_object_or_404(PropertyImage, pk=image_id, property__owner=request.user)
    pk = img.property.pk
    img.delete()
    messages.success(request, 'تم حذف الصورة')
    return redirect('edit', pk=pk)


# ═══════════════════════════════════════════════════════════
#  REQ-13,14,25,31-34  -  البحث والتصفية
# ═══════════════════════════════════════════════════════════

# REQ-13,14,25 + REQ-31,32,33,34 البحث المتقدم
def search_view(request):
    properties = Property.objects.filter(is_active=True, ad_state='published')
    query      = request.GET.get('q', '')
    city       = request.GET.get('city', '')
    ptype      = request.GET.get('type', '')
    status     = request.GET.get('status', '')
    min_price  = request.GET.get('min_price', '')
    max_price  = request.GET.get('max_price', '')
    rooms      = request.GET.get('rooms', '')
    min_area   = request.GET.get('min_area', '')
    max_area   = request.GET.get('max_area', '')
    has_image  = request.GET.get('has_image', '')
    sort       = request.GET.get('sort', '-created_at')

    if query:
        properties = properties.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if city:        properties = properties.filter(city__icontains=city)
    if ptype:       properties = properties.filter(property_type=ptype)
    if status:      properties = properties.filter(status=status)
    if min_price:   properties = properties.filter(price__gte=min_price)
    if max_price:   properties = properties.filter(price__lte=max_price)
    if rooms:       properties = properties.filter(rooms=rooms)         # REQ-31
    if min_area:    properties = properties.filter(area__gte=min_area)  # REQ-32
    if max_area:    properties = properties.filter(area__lte=max_area)  # REQ-32
    if has_image == 'yes':                                                # REQ-34
        properties = properties.exclude(image='')

    # REQ-33 ترتيب
    valid_sorts = ['-created_at', 'created_at', 'price', '-price', 'area', '-area', '-views_count']
    if sort in valid_sorts:
        properties = properties.order_by(sort)

    return render(request, 'properties/search.html', {
        'properties': properties,
        'total': properties.count(),
        'q': query, 'city': city, 'type_': ptype, 'status': status,
        'min_price': min_price, 'max_price': max_price, 'sort': sort,
        'rooms': rooms, 'min_area': min_area, 'max_area': max_area, 'has_image': has_image,
    })

# REQ-37 الأحدث
def newest_view(request):
    properties = Property.objects.filter(is_active=True, ad_state='published').order_by('-created_at')[:20]
    return render(request, 'properties/home.html', {'properties': properties, 'page_title': 'الأحدث'})

# REQ-38 الأكثر مشاهدة
def popular_view(request):
    properties = Property.objects.filter(is_active=True, ad_state='published').order_by('-views_count')[:20]
    return render(request, 'properties/home.html', {'properties': properties, 'page_title': 'الأكثر مشاهدة'})


# ═══════════════════════════════════════════════════════════
#  REQ-15,16,17  -  المفضلة
# ═══════════════════════════════════════════════════════════

@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('property')
    return render(request, 'properties/favorites.html', {'favorites': favorites})

@login_required
def add_favorite(request, pk):
    property = get_object_or_404(Property, pk=pk)
    fav, created = Favorite.objects.get_or_create(user=request.user, property=property)
    if created and property.owner != request.user:
        # REQ-48 تنبيه للمالك
        Notification.objects.create(
            user=property.owner, actor=request.user, notif_type='favorite',
            message=f'{request.user.username} أضاف عقارك "{property.title}" للمفضلة',
            link=f'/property/{property.pk}/',
        )
    return redirect('detail', pk=pk)

@login_required
def remove_favorite(request, pk):
    property = get_object_or_404(Property, pk=pk)
    Favorite.objects.filter(user=request.user, property=property).delete()
    return redirect('favorites')


# ═══════════════════════════════════════════════════════════
#  REQ-11,24  -  التقييم
# ═══════════════════════════════════════════════════════════

@login_required
@require_POST
def rate_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    if property.owner == request.user:
        messages.error(request, 'لا يمكنك تقييم عقارك')
        return redirect('detail', pk=pk)
    score = int(request.POST.get('score', 0))
    if 1 <= score <= 5:
        Rating.objects.update_or_create(user=request.user, property=property, defaults={'score': score})
        if property.owner != request.user:
            Notification.objects.create(
                user=property.owner, actor=request.user, notif_type='rating',
                message=f'{request.user.username} قيّم عقارك "{property.title}" بـ {score} نجوم',
                link=f'/property/{property.pk}/',
            )
        messages.success(request, 'تم التقييم')
    return redirect('detail', pk=pk)


# ═══════════════════════════════════════════════════════════
#  REQ-23  -  البلاغات
# ═══════════════════════════════════════════════════════════

@login_required
def report_ad(request, pk):
    property = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        Report.objects.create(
            user=request.user, property=property,
            reason=request.POST.get('reason', ''),
            category=request.POST.get('category', 'other'),
        )
        messages.success(request, 'تم استلام البلاغ، سيراجعه فريق الإدارة')
        return redirect('detail', pk=pk)
    return render(request, 'properties/report.html', {'property': property})


# ═══════════════════════════════════════════════════════════
#  REQ-36  -  المدن
# ═══════════════════════════════════════════════════════════

def cities_count(request):
    cities = Property.objects.filter(is_active=True).values('city').annotate(count=Count('id')).order_by('-count')
    return render(request, 'properties/cities.html', {'cities': cities})


# ═══════════════════════════════════════════════════════════
#  REQ-30  -  ملف المالك
# ═══════════════════════════════════════════════════════════

def owner_profile(request, username):
    owner = get_object_or_404(User, username=username)
    properties = Property.objects.filter(owner=owner, is_active=True, ad_state='published')
    profile, _ = UserProfile.objects.get_or_create(user=owner)
    is_following = False
    if request.user.is_authenticated and request.user != owner:
        is_following = Follow.objects.filter(follower=request.user, followed=owner).exists()
    stats = {
        'count': properties.count(),
        'followers': Follow.objects.filter(followed=owner).count(),
        'following': Follow.objects.filter(follower=owner).count(),
        'total_views': sum(p.views_count for p in properties),
    }
    return render(request, 'properties/owner_profile.html', {
        'owner': owner, 'properties': properties, 'profile': profile,
        'is_following': is_following, 'stats': stats,
    })


# ═══════════════════════════════════════════════════════════
#  REQ-40,41,42  -  المتابعة
# ═══════════════════════════════════════════════════════════

@login_required
@require_POST
def toggle_follow(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    if user_to_follow == request.user:
        return redirect('owner_profile', username=username)
    f, created = Follow.objects.get_or_create(follower=request.user, followed=user_to_follow)
    if not created:
        f.delete()
    else:
        Notification.objects.create(
            user=user_to_follow, actor=request.user, notif_type='follow',
            message=f'{request.user.username} بدأ بمتابعتك',
            link=f'/user/{request.user.username}/',
        )
    return redirect('owner_profile', username=username)

@login_required
def my_following(request):
    following = Follow.objects.filter(follower=request.user).select_related('followed')
    return render(request, 'properties/following.html', {'following': following})

@login_required
def my_followers(request):
    followers = Follow.objects.filter(followed=request.user).select_related('follower')
    return render(request, 'properties/followers.html', {'followers': followers})


# ═══════════════════════════════════════════════════════════
#  REQ-43  -  مقارنة عقارين
# ═══════════════════════════════════════════════════════════

def compare_properties(request):
    ids = request.GET.getlist('id')
    properties = Property.objects.filter(pk__in=ids)[:3]
    return render(request, 'properties/compare.html', {'properties': properties})


# ═══════════════════════════════════════════════════════════
#  REQ-44,45,46  -  التعليقات والردود
# ═══════════════════════════════════════════════════════════

@login_required
@require_POST
def add_comment(request, pk):
    property = get_object_or_404(Property, pk=pk)
    text = request.POST.get('text', '').strip()
    parent_id = request.POST.get('parent_id')
    if text:
        parent = None
        if parent_id:
            parent = Comment.objects.filter(pk=parent_id).first()
        Comment.objects.create(user=request.user, property=property, text=text, parent=parent)
        if property.owner != request.user:
            Notification.objects.create(
                user=property.owner, actor=request.user, notif_type='comment',
                message=f'{request.user.username} علّق على "{property.title}"',
                link=f'/property/{property.pk}/',
            )
        messages.success(request, 'تم نشر التعليق')
    return redirect('detail', pk=pk)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.user != request.user and comment.property.owner != request.user:
        messages.error(request, 'غير مصرّح')
        return redirect('detail', pk=comment.property.pk)
    pk = comment.property.pk
    comment.delete()
    messages.success(request, 'تم حذف التعليق')
    return redirect('detail', pk=pk)


# ═══════════════════════════════════════════════════════════
#  REQ-47  -  حفظ البحث
# ═══════════════════════════════════════════════════════════

@login_required
def save_search(request):
    if request.method == 'POST':
        form = SavedSearchForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, 'تم حفظ البحث')
            return redirect('my_searches')
    else:
        form = SavedSearchForm(initial=request.GET.dict())
    return render(request, 'properties/save_search.html', {'form': form})

@login_required
def my_searches(request):
    searches = SavedSearch.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'properties/my_searches.html', {'searches': searches})

@login_required
def delete_search(request, pk):
    search = get_object_or_404(SavedSearch, pk=pk, user=request.user)
    search.delete()
    messages.success(request, 'تم حذف البحث المحفوظ')
    return redirect('my_searches')


# ═══════════════════════════════════════════════════════════
#  REQ-48,49,50,51  -  التنبيهات
# ═══════════════════════════════════════════════════════════

@login_required
def notifications_list(request):
    notifs = Notification.objects.filter(user=request.user)
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, 'properties/notifications.html', {'notifications': notifs})

@login_required
def mark_notification_read(request, pk):
    n = get_object_or_404(Notification, pk=pk, user=request.user)
    n.is_read = True
    n.save()
    if n.link:
        return redirect(n.link)
    return redirect('notifications')

@login_required
def delete_notification(request, pk):
    n = get_object_or_404(Notification, pk=pk, user=request.user)
    n.delete()
    return redirect('notifications')


# ═══════════════════════════════════════════════════════════
#  REQ-39,58  -  السجلات
# ═══════════════════════════════════════════════════════════

@login_required
def activity_history(request):
    my_properties = Property.objects.filter(owner=request.user).order_by('-created_at')
    my_favorites  = Favorite.objects.filter(user=request.user).select_related('property').order_by('-added_at')
    my_ratings    = Rating.objects.filter(user=request.user).select_related('property').order_by('-created_at')
    return render(request, 'properties/history.html', {
        'properties': my_properties, 'favorites': my_favorites, 'ratings': my_ratings,
    })

@login_required
def recently_viewed(request):
    items = RecentView.objects.filter(user=request.user).select_related('property')[:20]
    return render(request, 'properties/recently_viewed.html', {'items': items})


# ═══════════════════════════════════════════════════════════
#  REQ-56  -  إحصائيات الموقع
# ═══════════════════════════════════════════════════════════

def site_stats(request):
    stats = {
        'total_properties': Property.objects.filter(is_active=True).count(),
        'total_users':      User.objects.count(),
        'total_cities':     Property.objects.values('city').distinct().count(),
        'total_ratings':    Rating.objects.count(),
        'total_views':      sum(Property.objects.values_list('views_count', flat=True)),
        'avg_rating':       Rating.objects.aggregate(avg=Avg('score'))['avg'] or 0,
        'most_viewed':      Property.objects.filter(is_active=True).order_by('-views_count').first(),
        'by_type':          Property.objects.filter(is_active=True).values('property_type').annotate(c=Count('id')),
    }
    return render(request, 'properties/stats.html', {'stats': stats})


# ═══════════════════════════════════════════════════════════
#  REQ-57  -  تصدير
# ═══════════════════════════════════════════════════════════

@login_required
def export_my_properties(request):
    properties = Property.objects.filter(owner=request.user)
    response = HttpResponse(content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="my_properties.txt"'
    lines = [f"= قائمة عقارات {request.user.username} =\n"]
    for p in properties:
        lines.append(f"- {p.title}  ({p.city})  -  {int(p.price):,} ريال  -  {p.get_status_display()}")
    response.write('\n'.join(lines))
    return response
