from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Property, Favorite, Rating, Report


# ============================================================
# إعداد البيانات المشتركة
# ============================================================
class BaseTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # مستخدم رئيسي
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='test1234'
        )

        # مستخدم ثانوي
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@test.com',
            password='test1234'
        )

        # عقار تجريبي
        self.property = Property.objects.create(
            owner=self.user,
            title='شقة تجريبية',
            description='وصف تجريبي للاختبار',
            price=50000,
            city='الرياض',
            address='حي النرجس',
            area=150,
            rooms=3,
            property_type='apartment',
            status='rent',
            is_active=True,
        )


# ============================================================
# REQ-1: تسجيل الدخول
# ============================================================
class LoginTest(BaseTestCase):

    def test_login_page_loads(self):
        """صفحة تسجيل الدخول تفتح بنجاح"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        print('✅ REQ-1: صفحة تسجيل الدخول تعمل')

    def test_login_valid(self):
        """تسجيل الدخول ببيانات صحيحة"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'test1234'
        })
        self.assertRedirects(response, reverse('home'))
        print('✅ REQ-1: تسجيل الدخول ببيانات صحيحة يعمل')

    def test_login_invalid(self):
        """تسجيل الدخول ببيانات خاطئة"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        print('✅ REQ-1: رفض بيانات الدخول الخاطئة يعمل')


# ============================================================
# REQ-2: إنشاء حساب
# ============================================================
class SignupTest(BaseTestCase):

    def test_signup_page_loads(self):
        """صفحة إنشاء الحساب تفتح"""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        print('✅ REQ-2: صفحة إنشاء الحساب تعمل')

    def test_signup_valid(self):
        """إنشاء حساب جديد بنجاح"""
        response = self.client.post(reverse('signup'), {
            'username':  'newuser',
            'email':     'new@test.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertTrue(User.objects.filter(username='newuser').exists())
        print('✅ REQ-2: إنشاء حساب جديد يعمل')

    def test_signup_duplicate_username(self):
        """رفض اسم مستخدم مكرر"""
        response = self.client.post(reverse('signup'), {
            'username':  'testuser',
            'email':     'dup@test.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 200)
        print('✅ REQ-2: رفض اسم المستخدم المكرر يعمل')


# ============================================================
# REQ-3: تعديل الحساب
# ============================================================
class EditProfileTest(BaseTestCase):

    def test_edit_profile_requires_login(self):
        """صفحة التعديل تتطلب تسجيل دخول"""
        response = self.client.get(reverse('edit_profile'))
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('edit_profile')}")
        print('✅ REQ-3: حماية صفحة التعديل تعمل')

    def test_edit_profile_success(self):
        """تعديل بيانات الحساب بنجاح"""
        self.client.login(username='testuser', password='test1234')
        response = self.client.post(reverse('edit_profile'), {
            'username':   'testuser',
            'email':      'updated@test.com',
            'first_name': 'أحمد',
            'last_name':  'العمري',
        })
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@test.com')
        print('✅ REQ-3: تعديل بيانات الحساب يعمل')


# ============================================================
# REQ-4: حذف الحساب
# ============================================================
class DeleteAccountTest(BaseTestCase):

    def test_delete_account_page_loads(self):
        """صفحة حذف الحساب تفتح"""
        self.client.login(username='testuser', password='test1234')
        response = self.client.get(reverse('delete_account'))
        self.assertEqual(response.status_code, 200)
        print('✅ REQ-4: صفحة حذف الحساب تعمل')

    def test_delete_account_success(self):
        """حذف الحساب بنجاح"""
        # نستخدم مستخدم مؤقت لعدم التأثير على بقية الاختبارات
        temp_user = User.objects.create_user(
            username='tempuser', password='test1234')
        self.client.login(username='tempuser', password='test1234')
        self.client.post(reverse('delete_account'))
        self.assertFalse(
            User.objects.filter(username='tempuser').exists())
        print('✅ REQ-4: حذف الحساب يعمل')


# ============================================================
# REQ-5: عرض الملف الشخصي
# ============================================================
class ProfileTest(BaseTestCase):

    def test_profile_requires_login(self):
        """الملف الشخصي يتطلب تسجيل دخول"""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
        print('✅ REQ-5: حماية الملف الشخصي تعمل')

    def test_profile_loads(self):
        """الملف الشخصي يفتح بعد تسجيل الدخول"""
        self.client.login(username='testuser', password='test1234')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        print('✅ REQ-5: عرض الملف الشخصي يعمل')


# ============================================================
# REQ-6: إضافة عقار
# ============================================================
class AddPropertyTest(BaseTestCase):

    def test_add_property_requires_login(self):
        """إضافة عقار تتطلب تسجيل دخول"""
        response = self.client.get(reverse('add'))
        self.assertEqual(response.status_code, 302)
        print('✅ REQ-6: حماية إضافة العقار تعمل')

    def test_add_property_success(self):
        """إضافة عقار جديد بنجاح"""
        self.client.login(username='testuser', password='test1234')
        count_before = Property.objects.count()
        response = self.client.post(reverse('add'), {
            'title':         'شقة جديدة للاختبار',
            'description':   'وصف الشقة الجديدة',
            'price':         75000,
            'city':          'جدة',
            'address':       'حي الروضة',
            'area':          180,
            'rooms':         3,
            'property_type': 'apartment',
            'status':        'rent',
            'is_active':     True,
        })
        self.assertEqual(Property.objects.count(), count_before + 1)
        print('✅ REQ-6: إضافة عقار جديد تعمل')


# ============================================================
# REQ-7: تعديل عقار
# ============================================================
class EditPropertyTest(BaseTestCase):

    def test_edit_property_by_owner(self):
        """المالك يستطيع تعديل عقاره"""
        self.client.login(username='testuser', password='test1234')
        response = self.client.post(
            reverse('edit', args=[self.property.pk]), {
                'title':         'شقة معدّلة',
                'description':   'وصف معدّل',
                'price':         60000,
                'city':          'الرياض',
                'address':       'حي النرجس',
                'area':          150,
                'rooms':         3,
                'property_type': 'apartment',
                'status':        'rent',
                'is_active':     True,
            })
        self.property.refresh_from_db()
        self.assertEqual(self.property.title, 'شقة معدّلة')
        print('✅ REQ-7: تعديل العقار من المالك يعمل')

    def test_edit_property_by_other_user(self):
        """مستخدم آخر لا يستطيع تعديل العقار"""
        self.client.login(username='testuser2', password='test1234')
        response = self.client.get(
            reverse('edit', args=[self.property.pk]))
        self.assertEqual(response.status_code, 404)
        print('✅ REQ-7: حماية التعديل من مستخدم آخر تعمل')


# ============================================================
# REQ-8: حذف عقار
# ============================================================
class DeletePropertyTest(BaseTestCase):

    def test_delete_property_by_owner(self):
        """المالك يستطيع حذف عقاره"""
        self.client.login(username='testuser', password='test1234')
        prop = Property.objects.create(
            owner=self.user, title='عقار للحذف',
            description='test', price=10000,
            city='الرياض', address='test',
            area=100, rooms=2,
            property_type='apartment', status='rent'
        )
        self.client.post(reverse('delete_property', args=[prop.pk]))
        self.assertFalse(Property.objects.filter(pk=prop.pk).exists())
        print('✅ REQ-8: حذف العقار من المالك يعمل')

    def test_delete_property_by_other(self):
        """مستخدم آخر لا يستطيع حذف العقار"""
        self.client.login(username='testuser2', password='test1234')
        response = self.client.post(
            reverse('delete_property', args=[self.property.pk]))
        self.assertEqual(response.status_code, 404)
        print('✅ REQ-8: حماية الحذف من مستخدم آخر تعمل')


# ============================================================
# REQ-9 & REQ-10: عرض العقارات
# ============================================================
class ViewPropertyTest(BaseTestCase):

    def test_home_page_loads(self):
        """الصفحة الرئيسية تفتح"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.property.title)
        print('✅ REQ-10: الصفحة الرئيسية تعمل')

    def test_property_detail_loads(self):
        """صفحة تفاصيل العقار تفتح"""
        response = self.client.get(
            reverse('detail', args=[self.property.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.property.title)
        print('✅ REQ-9: صفحة تفاصيل العقار تعمل')

    def test_views_count_increments(self):
        """عداد المشاهدات يزيد عند كل زيارة"""
        views_before = self.property.views_count
        self.client.get(reverse('detail', args=[self.property.pk]))
        self.property.refresh_from_db()
        self.assertEqual(self.property.views_count, views_before + 1)
        print('✅ REQ-10: عداد المشاهدات يعمل')


# ============================================================
# REQ-11: تقييم العقار
# ============================================================
class RatingTest(BaseTestCase):

    def test_rate_property(self):
        """تقييم عقار بنجاح"""
        self.client.login(username='testuser2', password='test1234')
        self.client.post(reverse('rate', args=[self.property.pk]),
                         {'score': 5})
        self.assertTrue(
            Rating.objects.filter(
                user=self.user2,
                property=self.property,
                score=5
            ).exists()
        )
        print('✅ REQ-11: تقييم العقار يعمل')

    def test_update_rating(self):
        """تحديث التقييم بدلاً من إضافة جديد"""
        self.client.login(username='testuser2', password='test1234')
        self.client.post(reverse('rate', args=[self.property.pk]),
                         {'score': 3})
        self.client.post(reverse('rate', args=[self.property.pk]),
                         {'score': 5})
        self.assertEqual(
            Rating.objects.filter(
                user=self.user2,
                property=self.property
            ).count(), 1
        )
        print('✅ REQ-11: تحديث التقييم يعمل')


# ============================================================
# REQ-12: تسجيل الخروج
# ============================================================
class LogoutTest(BaseTestCase):

    def test_logout(self):
        """تسجيل الخروج يعمل"""
        self.client.login(username='testuser', password='test1234')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        print('✅ REQ-12: تسجيل الخروج يعمل')


# ============================================================
# REQ-13 & REQ-14 & REQ-25: البحث والتصفية
# ============================================================
class SearchTest(BaseTestCase):

    def setUp(self):
        super().setUp()
        # إضافة عقارات إضافية للبحث
        Property.objects.create(
            owner=self.user, title='فيلا في جدة',
            description='فيلا جميلة', price=3000000,
            city='جدة', address='حي الروضة',
            area=500, rooms=6,
            property_type='villa', status='sale', is_active=True
        )
        Property.objects.create(
            owner=self.user2, title='أرض في الدمام',
            description='أرض سكنية', price=800000,
            city='الدمام', address='حي الشاطئ',
            area=800, rooms=0,
            property_type='land', status='sale', is_active=True
        )

    def test_search_by_title(self):
        """البحث بالعنوان يعمل"""
        response = self.client.get(reverse('search'), {'q': 'فيلا'})
        self.assertContains(response, 'فيلا في جدة')
        self.assertNotContains(response, 'شقة تجريبية')
        print('✅ REQ-13: البحث بالعنوان يعمل')

    def test_filter_by_city(self):
        """التصفية بالمدينة تعمل"""
        response = self.client.get(reverse('search'), {'city': 'جدة'})
        self.assertContains(response, 'فيلا في جدة')
        self.assertNotContains(response, 'أرض في الدمام')
        print('✅ REQ-14: التصفية بالمدينة تعمل')

    def test_filter_by_type(self):
        """التصفية بالنوع تعمل"""
        response = self.client.get(
            reverse('search'), {'type': 'land'})
        self.assertContains(response, 'أرض في الدمام')
        self.assertNotContains(response, 'فيلا في جدة')
        print('✅ REQ-14: التصفية بالنوع تعمل')

    def test_filter_by_price(self):
        """التصفية بالسعر تعمل"""
        response = self.client.get(
            reverse('search'), {'max_price': 100000})
        self.assertContains(response, 'شقة تجريبية')
        self.assertNotContains(response, 'فيلا في جدة')
        print('✅ REQ-14: التصفية بالسعر تعمل')

    def test_sort_by_price(self):
        """الترتيب بالسعر يعمل"""
        response = self.client.get(
            reverse('search'), {'sort': 'price'})
        self.assertEqual(response.status_code, 200)
        print('✅ REQ-25: الترتيب يعمل')


# ============================================================
# REQ-15 & REQ-16 & REQ-17: المفضلة
# ============================================================
class FavoriteTest(BaseTestCase):

    def test_add_favorite(self):
        """إضافة عقار للمفضلة"""
        self.client.login(username='testuser2', password='test1234')
        self.client.get(reverse('fav_add', args=[self.property.pk]))
        self.assertTrue(
            Favorite.objects.filter(
                user=self.user2,
                property=self.property
            ).exists()
        )
        print('✅ REQ-15: إضافة للمفضلة تعمل')

    def test_view_favorites(self):
        """عرض قائمة المفضلة"""
        self.client.login(username='testuser2', password='test1234')
        Favorite.objects.create(
            user=self.user2, property=self.property)
        response = self.client.get(reverse('favorites'))
        self.assertContains(response, self.property.title)
        print('✅ REQ-16: عرض المفضلة يعمل')

    def test_remove_favorite(self):
        """إزالة عقار من المفضلة"""
        self.client.login(username='testuser2', password='test1234')
        Favorite.objects.create(
            user=self.user2, property=self.property)
        self.client.get(
            reverse('fav_remove', args=[self.property.pk]))
        self.assertFalse(
            Favorite.objects.filter(
                user=self.user2,
                property=self.property
            ).exists()
        )
        print('✅ REQ-17: إزالة من المفضلة تعمل')

    def test_no_duplicate_favorite(self):
        """عدم تكرار المفضلة"""
        self.client.login(username='testuser2', password='test1234')
        self.client.get(reverse('fav_add', args=[self.property.pk]))
        self.client.get(reverse('fav_add', args=[self.property.pk]))
        count = Favorite.objects.filter(
            user=self.user2, property=self.property).count()
        self.assertEqual(count, 1)
        print('✅ REQ-15: عدم تكرار المفضلة يعمل')


# ============================================================
# REQ-23: الإبلاغ عن إعلان
# ============================================================
class ReportTest(BaseTestCase):

    def test_report_property(self):
        """الإبلاغ عن إعلان يعمل"""
        self.client.login(username='testuser2', password='test1234')
        self.client.post(
            reverse('report', args=[self.property.pk]),
            {'reason': 'محتوى مخالف للشروط'}
        )
        self.assertTrue(
            Report.objects.filter(
                user=self.user2,
                property=self.property
            ).exists()
        )
        print('✅ REQ-23: الإبلاغ عن الإعلان يعمل')


# ============================================================
# REQ-27 & REQ-28: كلمة المرور
# ============================================================
class PasswordTest(BaseTestCase):

    def test_change_password(self):
        """تغيير كلمة المرور يعمل"""
        self.client.login(username='testuser', password='test1234')
        response = self.client.post(reverse('change_password'), {
            'old_password': 'test1234',
            'new_password1': 'NewPass456!',
            'new_password2': 'NewPass456!',
        })
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass456!'))
        print('✅ REQ-28: تغيير كلمة المرور يعمل')


# ============================================================
# REQ-36 & REQ-37 & REQ-38 & REQ-39: صفحات إضافية
# ============================================================
class ExtraPagesTest(BaseTestCase):

    def test_cities_page(self):
        """صفحة المدن تعمل"""
        response = self.client.get(reverse('cities'))
        self.assertEqual(response.status_code, 200)
        print('✅ REQ-36: صفحة المدن تعمل')

    def test_newest_page(self):
        """صفحة الأحدث تعمل"""
        response = self.client.get(reverse('newest'))
        self.assertEqual(response.status_code, 200)
        print('✅ REQ-37: صفحة الأحدث تعمل')

    def test_popular_page(self):
        """صفحة الأكثر مشاهدة تعمل"""
        response = self.client.get(reverse('popular'))
        self.assertEqual(response.status_code, 200)
        print('✅ REQ-38: صفحة الأكثر مشاهدة تعمل')

    def test_history_page(self):
        """صفحة سجل النشاط تعمل"""
        self.client.login(username='testuser', password='test1234')
        response = self.client.get(reverse('history'))
        self.assertEqual(response.status_code, 200)
        print('✅ REQ-39: سجل النشاط يعمل')