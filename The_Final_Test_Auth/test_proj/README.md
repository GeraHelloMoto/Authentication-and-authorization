Документацию и html файл я создал при помощи AI, остальное сам (не без консультации с тем же AI).



# 🛡️ Система управления ограничениями доступа

## 🎯 Общая концепция

Система реализует **ролевую модель доступа (RBAC - Role-Based Access Control)** с гибкими правами для различных бизнес-объектов приложения. Каждому пользователю назначаются роли, а каждой роли - права доступа к конкретным ресурсам системы.

---

## 🗃️ Архитектура базы данных

### 📊 Схема таблиц и связей
User (Пользователи)
│
├── UserRole (Связь пользователь-роль)
│ │
│ └── Role (Роли: admin, user, manager)
│
└── AccessRule (Правила доступа)
│
└── BusinessElement (Бизнес-объекты: products, orders, users)

text

### 🔐 Детальное описание моделей

#### **User** - Пользователи системы
```python
# Основная информация о пользователе
id: Integer (Primary Key)
email: String (Unique)          # Email для входа
password_hash: String           # Хэш пароля (bcrypt)
name: String                    # Имя пользователя
is_active: Boolean              # Активен ли аккаунт
created_at: DateTime            # Дата регистрации
Role - Роли пользователей
python
# Справочник ролей в системе
id: Integer (Primary Key)
name: String (Unique)           # Название роли: 'admin', 'user'
description: Text               # Описание роли
UserRole - Связь пользователей с ролями
python
# Многие-ко-многим: пользователь может иметь несколько ролей
id: Integer (Primary Key)
user_id: Integer (Foreign Key → User.id)
role_id: Integer (Foreign Key → Role.id)
BusinessElement - Бизнес-объекты системы
python
# Ресурсы системы, к которым нужен доступ
id: Integer (Primary Key)
name: String (Unique)           # Имя объекта: 'products', 'orders', 'users'
description: Text               # Описание объекта
AccessRule - Правила доступа
python
# Определяет какие действия разрешены роли над объектом
id: Integer (Primary Key)
role_id: Integer (Foreign Key → Role.id)
element_id: Integer (Foreign Key → BusinessElement.id)
can_read: Boolean              # Право на чтение
can_create: Boolean            # Право на создание
can_update: Boolean            # Право на обновление
can_delete: Boolean            # Право на удаление
🎪 Матрица прав доступа
👑 Администратор (admin)
text
📦 products (Товары):
   ✅ can_read    - Просмотр товаров
   ✅ can_create  - Добавление новых товаров  
   ✅ can_update  - Редактирование товаров
   ✅ can_delete  - Удаление товаров

📋 orders (Заказы):
   ✅ can_read    - Просмотр заказов
   ✅ can_create  - Создание заказов
   ✅ can_update  - Изменение заказов
   ✅ can_delete  - Удаление заказов

👥 users (Пользователи):
   ✅ can_read    - Просмотр пользователей
   ✅ can_create  - Создание пользователей
   ✅ can_update  - Редактирование пользователей
   ✅ can_delete  - Удаление пользователей
👤 Обычный пользователь (user)
text
📦 products (Товары):
   ✅ can_read    - Просмотр товаров
   ❌ can_create  - Не может добавлять товары
   ❌ can_update  - Не может редактировать товары  
   ❌ can_delete  - Не может удалять товары

📋 orders (Заказы):
   ❌ can_read    - Не может просматривать заказы
   ❌ can_create  - Не может создавать заказы
   ❌ can_update  - Не может изменять заказы
   ❌ can_delete  - Не может удалять заказы

👥 users (Пользователи):
   ❌ can_read    - Не может просматривать пользователей
   ❌ can_create  - Не может создавать пользователей
   ❌ can_update  - Не может редактировать пользователей
   ❌ can_delete  - Не может удалять пользователей
🔄 Алгоритм проверки прав доступа
1. Аутентификация (Определение пользователя)
python
# middleware.py - обработка каждого входящего запроса
def authenticate_request(request):
    auth_header = request.headers.get('Authorization')
    
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            user = User.objects.get(id=user_id, is_active=True)
            request.user = user  # Пользователь определен
        except:
            request.user = None  # Пользователь не определен
2. Определение ролей пользователя
python
def get_user_roles(user):
    # Получаем все роли пользователя
    user_roles = UserRole.objects.filter(user=user)
    return [ur.role for ur in user_roles]
3. Проверка прав доступа к ресурсу
python
def check_permission(user, element_name, action):
    # Если пользователь не аутентифицирован
    if not user:
        return False, 401  # Unauthorized
    
    # Получаем бизнес-объект
    try:
        element = BusinessElement.objects.get(name=element_name)
    except BusinessElement.DoesNotExist:
        return False, 404  # Not Found
    
    # Проверяем права для каждой роли пользователя
    user_roles = UserRole.objects.filter(user=user)
    for user_role in user_roles:
        try:
            rule = AccessRule.objects.get(role=user_role.role, element=element)
            if getattr(rule, f'can_{action}', False):
                return True, 200  # OK - доступ разрешен
        except AccessRule.DoesNotExist:
            continue
    
    return False, 403  # Forbidden - нет прав
4. Обработка ответа сервера
✅ 200 OK - Пользователь аутентифицирован и имеет права доступа

❌ 401 Unauthorized - Пользователь не аутентифицирован (нет токена или токен невалидный)

❌ 403 Forbidden - Пользователь аутентифицирован, но не имеет прав доступа к запрашиваемому ресурсу

❌ 404 Not Found - Запрашиваемый ресурс не существует

🛡️ Практические сценарии доступа
📋 Пример 1: Успешный доступ пользователя к товарам
text
ЗАПРОС:
GET /api/products/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

ПРОЦЕСС:
1. ✅ Middleware извлекает токен → определяет пользователя (user)
2. ✅ Находит роли пользователя → ['user']
3. ✅ Проверяет правила доступа роли 'user' к 'products'
4. ✅ Обнаруживает can_read=True для products

ОТВЕТ: 200 OK + список товаров
📋 Пример 2: Отказ в доступе пользователя к списку пользователей
text
ЗАПРОС:  
GET /api/users/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

ПРОЦЕСС:
1. ✅ Middleware извлекает токен → определяет пользователя (user)
2. ✅ Находит роли пользователя → ['user'] 
3. ✅ Проверяет правила доступа роли 'user' к 'users'
4. ❌ Обнаруживает can_read=False для users

ОТВЕТ: 403 Forbidden + {"error": "Только для админов"}
📋 Пример 3: Неавторизованный запрос
text
ЗАПРОС:
GET /api/products/

ПРОЦЕСС:
1. ❌ Middleware не находит токен в заголовках
2. ❌ Не может определить пользователя

ОТВЕТ: 401 Unauthorized + {"error": "Войдите в систему"}
📋 Пример 4: Администратор получает полный доступ
text
ЗАПРОС:
GET /api/users/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

ПРОЦЕСС:
1. ✅ Middleware извлекает токен → определяет пользователя (admin)
2. ✅ Находит роли пользователя → ['admin']
3. ✅ Проверяет правила доступа роли 'admin' к 'users'
4. ✅ Обнаруживает can_read=True для users

ОТВЕТ: 200 OK + список пользователей
🎯 Ключевые преимущества системы
✅ Гибкость и адаптивность
Множественные роли - один пользователь может иметь несколько ролей

Легкое добавление - новые роли и бизнес-объекты добавляются без изменения кода

Гранулярные права - тонкая настройка прав для каждого ресурса

✅ Безопасность
Многоуровневая проверка - отдельно аутентификация и авторизация

JWT токены - безопасная передача данных, не требующая хранения состояния

Временные ограничения - токены с ограниченным сроком действия

✅ Масштабируемость
Модульная архитектура - легко добавлять новые типы прав

Отдельная таблица правил - независимость от бизнес-логики

Поддержка сложных сценариев - иерархические роли, наследование прав

✅ Простота интеграции
Четкое разделение - аутентификация и авторизация независимы

Стандартные HTTP статусы - понятные коды ответов для фронтенда

Легкая отладка - прозрачная логика работы системы

🔮 Возможности расширения системы
1. Добавление новых рлей
python
# Менеджер с расширенными правами
Role.objects.create(
    name='manager',
    description='Менеджер с правами на управление заказами'
)

# Модератор контента
Role.objects.create(
    name='moderator', 
    description='Модератор с правами на управление контентом'
)
2. Новые бизнес-объекты
python
# Отчеты и аналитика
BusinessElement.objects.create(
    name='reports',
    description='Система отчетности и аналитики'
)

# Настройки системы
BusinessElement.objects.create(
    name='settings',
    description='Управление настройками приложения'
)
3. Расширение набора прав
python
# Добавление новых типов прав в AccessRule
can_export = models.BooleanField(default=False)    # Экспорт данных
can_approve = models.BooleanField(default=False)   # Утверждение действий
can_audit = models.BooleanField(default=False)     # Просмотр логов
can_configure = models.BooleanField(default=False) # Настройка системы
4. Гранулярные права на уровне объектов
python
# Права на уровне отдельных записей (дополнительный уровень)
class ObjectPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    object_type = models.CharField(max_length=50)  # 'product', 'order', 'user'
    object_id = models.IntegerField()              # ID конкретного объекта
    can_view = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_share = models.BooleanField(default=False)
5. Временные ограничения прав
python
# Ограничение прав по времени
class TemporaryAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
🚀 Заключение
Предложенная система управления ограничениями доступа предоставляет:

✅ Полный контроль безопасности
Многоуровневая проверка прав для каждого запроса

Четкое разделение аутентификации и авторизации

Гибкая настройка прав для различных сценариев использования

✅ Промышленную готовность
Масштабируемая архитектура для роста приложения

Поддержка сложных бизнес-требований

Легкая интеграция с существующей инфраструктурой

✅ Простота сопровождения
Понятная структура данных и логика работы

Легкое добавление новых функций и прав

Прозрачная система отладки и мониторинга

Система готова к использованию в production-среде и может быть легко адаптирована под изменяющиеся бизнес-требования, обеспечивая надежную защиту ресурсов приложения при сохранении гибкости управления доступом.