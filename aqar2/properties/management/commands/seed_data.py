from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from properties.models import Property, Favorite, Rating
import random

class Command(BaseCommand):
    help = 'إضافة بيانات تجريبية للمشروع - السوق السوري'

    def handle(self, *args, **kwargs):
        self.stdout.write('🚀 جاري إضافة البيانات التجريبية - الجمهورية العربية السورية...')

        # ===== إنشاء مستخدمين =====
        users_data = [
            {'username': 'ahmed',   'email': 'ahmed@aqar.sy',   'first_name': 'أحمد',   'last_name': 'الحموي'},
            {'username': 'sara',    'email': 'sara@aqar.sy',    'first_name': 'سارة',   'last_name': 'الدمشقية'},
            {'username': 'khalid',  'email': 'khalid@aqar.sy',  'first_name': 'خالد',   'last_name': 'الحلبي'},
            {'username': 'noura',   'email': 'noura@aqar.sy',   'first_name': 'نورا',   'last_name': 'اللاذقاني'},
            {'username': 'faisal',  'email': 'faisal@aqar.sy',  'first_name': 'فيصل',   'last_name': 'الحمصي'},
        ]

        users = []
        for u in users_data:
            user, created = User.objects.get_or_create(
                username=u['username'],
                defaults={'email': u['email'], 'first_name': u['first_name'], 'last_name': u['last_name']}
            )
            if created:
                user.set_password('test1234')
                user.save()
                self.stdout.write(f'  ✅ {user.username}')
            users.append(user)

        # ===== بيانات العقارات في 14 محافظة سورية =====
        properties_data = [
            # دمشق - العاصمة
            {'title': 'شقة فاخرة في حي المالكي بدمشق', 'description': 'شقة راقية مساحتها 180م² في قلب دمشق، 4 غرف وصالة، تشطيب فندقي قرب الأسواق.',
             'price': 350000000, 'city': 'دمشق', 'address': 'حي المالكي، شارع أبو رمانة',
             'area': 180, 'rooms': 4, 'property_type': 'apartment', 'status': 'sale'},
            {'title': 'شقة للإيجار في المزة', 'description': 'شقة عصرية في المزة، 3 غرف نوم، قريبة من جامعة دمشق والخدمات.',
             'price': 1500000, 'city': 'دمشق', 'address': 'المزة فيلات شرقية',
             'area': 130, 'rooms': 3, 'property_type': 'apartment', 'status': 'rent'},

            # ريف دمشق
            {'title': 'فيلا في معضمية الشام', 'description': 'فيلا دورين على مساحة 400م² مع حديقة، 5 غرف نوم، مناسبة للعائلات.',
             'price': 850000000, 'city': 'ريف دمشق', 'address': 'معضمية الشام',
             'area': 400, 'rooms': 5, 'property_type': 'villa', 'status': 'sale'},

            # حلب - عاصمة الشمال
            {'title': 'فيلا فاخرة في حلب الجديدة', 'description': 'فيلا حديثة في حلب الجديدة، 6 غرف نوم، مسبح، حديقة، تشطيب لوكس.',
             'price': 1200000000, 'city': 'حلب', 'address': 'حلب الجديدة - السبيل',
             'area': 500, 'rooms': 6, 'property_type': 'villa', 'status': 'sale'},
            {'title': 'محل تجاري في الشهباء', 'description': 'محل تجاري على شارع رئيسي مساحته 80م² مناسب لكل الأنشطة.',
             'price': 180000000, 'city': 'حلب', 'address': 'شارع الشهباء',
             'area': 80, 'rooms': 0, 'property_type': 'shop', 'status': 'sale'},

            # حمص
            {'title': 'شقة في حمص - الإنشاءات', 'description': 'شقة جديدة بمساحة 140م²، 3 غرف، إكساء سوبر ديلوكس.',
             'price': 180000000, 'city': 'حمص', 'address': 'حي الإنشاءات',
             'area': 140, 'rooms': 3, 'property_type': 'apartment', 'status': 'sale'},

            # حماة
            {'title': 'أرض زراعية في سهل الغاب', 'description': 'أرض زراعية خصبة مساحتها 5000م² بئر ارتوازي وشجر مثمر.',
             'price': 250000000, 'city': 'حماة', 'address': 'سهل الغاب',
             'area': 5000, 'rooms': 0, 'property_type': 'land', 'status': 'sale'},

            # اللاذقية - الساحل
            {'title': 'فيلا بإطلالة على البحر - اللاذقية', 'description': 'فيلا رائعة بإطلالة مباشرة على البحر المتوسط، 5 غرف، مسبح خاص.',
             'price': 950000000, 'city': 'اللاذقية', 'address': 'شاطئ الأزرق',
             'area': 450, 'rooms': 5, 'property_type': 'villa', 'status': 'sale'},
            {'title': 'شقة في اللاذقية - الزراعة', 'description': 'شقة حديثة في حي الزراعة، 3 غرف، قريبة من جامعة تشرين.',
             'price': 1200000, 'city': 'اللاذقية', 'address': 'حي الزراعة',
             'area': 120, 'rooms': 3, 'property_type': 'apartment', 'status': 'rent'},

            # طرطوس
            {'title': 'شقة بإطلالة بحرية في طرطوس', 'description': 'شقة جميلة على البحر مباشرة، 3 غرف، تشطيب راقٍ، مناسبة للعطلات.',
             'price': 220000000, 'city': 'طرطوس', 'address': 'كورنيش طرطوس',
             'area': 150, 'rooms': 3, 'property_type': 'apartment', 'status': 'sale'},

            # إدلب
            {'title': 'منزل عربي في إدلب', 'description': 'منزل عربي تقليدي مع حوش داخلي، 4 غرف، موقع هادئ.',
             'price': 95000000, 'city': 'إدلب', 'address': 'مدينة إدلب',
             'area': 200, 'rooms': 4, 'property_type': 'apartment', 'status': 'sale'},

            # درعا
            {'title': 'مكتب تجاري في درعا', 'description': 'مكتب مناسب للشركات والمحاماة، موقع مركزي.',
             'price': 800000, 'city': 'درعا', 'address': 'وسط مدينة درعا',
             'area': 75, 'rooms': 2, 'property_type': 'office', 'status': 'rent'},

            # السويداء
            {'title': 'أرض سكنية في السويداء', 'description': 'أرض سكنية بمساحة 600م² على شارعين، صك نظامي.',
             'price': 75000000, 'city': 'السويداء', 'address': 'حي السلام',
             'area': 600, 'rooms': 0, 'property_type': 'land', 'status': 'sale'},

            # القنيطرة
            {'title': 'أرض زراعية في القنيطرة', 'description': 'أرض زراعية خصبة مساحتها 3000م² بئر ماء، أشجار زيتون.',
             'price': 65000000, 'city': 'القنيطرة', 'address': 'القنيطرة - خان أرنبة',
             'area': 3000, 'rooms': 0, 'property_type': 'land', 'status': 'sale'},

            # دير الزور
            {'title': 'عمارة في دير الزور', 'description': 'عمارة 4 طوابق، 8 شقق، استثمار ممتاز.',
             'price': 480000000, 'city': 'دير الزور', 'address': 'حي الجورة',
             'area': 800, 'rooms': 0, 'property_type': 'building', 'status': 'sale'},

            # الحسكة + الرقة
            {'title': 'شقة عائلية في الحسكة', 'description': 'شقة واسعة بمساحة 160م²، 4 غرف، مناسبة للعائلات.',
             'price': 110000000, 'city': 'الحسكة', 'address': 'حي الناصرة',
             'area': 160, 'rooms': 4, 'property_type': 'apartment', 'status': 'sale'},
        ]

        properties = []
        for i, data in enumerate(properties_data):
            owner = users[i % len(users)]
            prop, created = Property.objects.get_or_create(
                title=data['title'],
                defaults={**data, 'owner': owner, 'is_active': True,
                          'views_count': random.randint(10, 500)})
            if created:
                self.stdout.write(f'  🏠 {prop.title}')
            properties.append(prop)

        # ===== المفضلة =====
        for user in users:
            favs = random.sample(properties, min(4, len(properties)))
            for prop in favs:
                if prop.owner != user:
                    Favorite.objects.get_or_create(user=user, property=prop)

        # ===== التقييمات =====
        for user in users:
            rated = random.sample(properties, min(5, len(properties)))
            for prop in rated:
                if prop.owner != user:
                    Rating.objects.get_or_create(
                        user=user, property=prop,
                        defaults={'score': random.randint(3, 5)})

        self.stdout.write('')
        self.stdout.write('✅ تم إضافة البيانات بنجاح!')
        self.stdout.write('━' * 50)
        self.stdout.write(f'🇸🇾 المحافظات: 14 محافظة سورية')
        self.stdout.write(f'👥 المستخدمون: {User.objects.count()}')
        self.stdout.write(f'🏠 العقارات: {Property.objects.count()}')
        self.stdout.write(f'❤️ المفضلة: {Favorite.objects.count()}')
        self.stdout.write(f'⭐ التقييمات: {Rating.objects.count()}')
        self.stdout.write('━' * 50)
        self.stdout.write('🔑 كلمة المرور للمستخدمين: test1234')
        for u in users_data:
            self.stdout.write(f'   • {u["username"]}')
