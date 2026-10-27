# Calorie & Macro Tracker | حاسبة السعرات ومتتبع الماكروز

[العربية](#العربية) | [English](#english)

---

<a id="العربية"></a>

<div dir="rtl">

# العربية

تطبيق ويب عربي لحساب احتياجك اليومي من السعرات والماء، وتسجيل وجباتك وماكروزك مقابل هدفك، واختيار جدول تمارين حسب عدد أيام تدريبك. يعمل محلياً على جهازك بدون إنترنت وبدون أي مكتبات خارجية.

## المميزات

- **حساب السعرات والماء:** تدخل الجنس والعمر والطول والوزن ومستوى النشاط والهدف (تنزيل، تثبيت، زيادة)، فتحصل على السعرات اليومية والماء والبروتين والكربوهيدرات والدهون ومؤشر كتلة الجسم.
- **تسجيل الماكروز:** سجّل فطورك وغداءك وعشاءك من قائمة أطعمة جاهزة (40 طعاماً بقيم لكل 100 جرام) أو أضف طعاماً مخصصاً بسعراته.
    - عداد ثابت في أعلى الصفحة مثل `508 / 2,358` مع شريط تقدم، ويتحول للأحمر عند تجاوز الهدف.
    - عدادات للبروتين والكربوهيدرات والدهون، وماكروز كل وجبة على حدة.
    - اختيار التاريخ لمراجعة أي يوم، وحذف أي عنصر بضغطة.
- **هدف مخصص:** تقدر تكتب سعراتك وماكروزك وماءك بنفسك. أي ماكروز تتركها فاضية توزع تلقائياً (30% بروتين، 40% كربوهيدرات، 30% دهون).
- **تتبع الماء:** اكتب الكمية بالمل (مثل 500) واضغط **+**، ويظهر عداد مقابل هدف الماء مع زر تصفير.
- **جداول التمارين:** اختر من 2 إلى 6 أيام في الأسبوع واحصل على جداول جاهزة: فل بودي، علوي/سفلي، دفع/سحب/أرجل، وتقسيم العضلات (Bro Split)، مع الأسبوع كاملاً وأيام الراحة والتمارين بالمجموعات والتكرارات.

## التقنيات

| الجزء | التقنية |
|---|---|
| الواجهة | HTML, CSS, JavaScript (بدون مكتبات) |
| الخادم | Python (المكتبة القياسية فقط: `http.server`) |
| قاعدة البيانات | SQLite (`sqlite3`) |
| الحسابات | Mifflin-St Jeor في `calc.py` |

## هيكل المشروع

```
calorie-app/
├── server.py        # الخادم وواجهة الـ API وقاعدة البيانات
├── calc.py          # حسابات السعرات والماء والماكروز
├── foods.py         # قاعدة بيانات الأطعمة
├── workouts.py      # جداول التمارين
├── README.md
└── static/
    ├── index.html       # الصفحة الرئيسية
    ├── calculator.html  # حساب السعرات والماء
    ├── tracker.html     # تسجيل الماكروز والماء
    ├── workouts.html    # جداول التمارين
    ├── style.css
    └── app.js           # دوال مشتركة
```

يتم إنشاء ملف `data.db` تلقائياً عند أول تشغيل، وفيه وجباتك وهدفك وماؤك.

## التشغيل

المتطلبات: Python 3.8 أو أحدث. لا يحتاج تثبيت أي مكتبة.

```bash
python server.py
```

ثم افتح المتصفح على:

```
http://localhost:8000
```

لإيقاف الخادم اضغط `Ctrl + C`. إذا لم يعمل الأمر على ويندوز جرّب `py server.py`.

> افتح الموقع دائماً من الرابط أعلاه والخادم شغال. فتح ملفات HTML مباشرة من المجلد لن يعمل لأن الصفحات تعتمد على الـ API.

## طريقة الحساب

- **BMR:** معادلة Mifflin-St Jeor: `10×الوزن + 6.25×الطول − 5×العمر + 5` للذكور و`− 161` للإناث.
- **الاحتياج الكلي:** BMR مضروباً في معامل النشاط (1.2 إلى 1.9).
- **الهدف:** ناقص 500 سعرة للتنزيل، وزائد 300 للزيادة، بدون تغيير للتثبيت. مع حد أدنى آمن: 1500 للذكور و1200 للإناث.
- **البروتين:** 2.0 جم/كجم للتنزيل، و1.6 للتثبيت، و1.8 للزيادة.
- **الدهون:** 25% من السعرات، والكربوهيدرات هي المتبقي.
- **الماء:** 33 مل لكل كجم، مع إضافة من 0 إلى 1 لتر حسب النشاط.

## واجهة الـ API

| الطريقة | المسار | الوصف |
|---|---|---|
| `POST` | `/api/calc` | حساب السعرات والماء والماكروز |
| `GET` | `/api/foods` | قائمة الأطعمة |
| `GET` / `POST` | `/api/goal` | قراءة وحفظ الهدف (سعرات، ماكروز، ماء) |
| `GET` / `POST` | `/api/log?day=YYYY-MM-DD` | قراءة وإضافة عناصر الوجبات |
| `DELETE` | `/api/log/<id>` | حذف عنصر |
| `GET` / `POST` / `DELETE` | `/api/water?day=YYYY-MM-DD` | قراءة وإضافة وتصفير ماء اليوم |
| `GET` | `/api/plans?days=N` | جداول التمارين لعدد أيام من 2 إلى 6 |

## ملاحظات

- قيم الأطعمة تقريبية، ويمكنك إضافة أطعمة جديدة في `foods.py`، وتعديل الجداول في `workouts.py`.
- التقديرات والجداول عامة وللتوعية فقط، وليست بديلاً عن استشارة مختص تغذية أو مدرب أو طبيب.
- الخادم مخصص للاستخدام المحلي ولا يتضمن تسجيل دخول، لذلك لا تعرضه على الإنترنت كما هو.

## أفكار للتطوير

- تسجيل أوزان وتكرارات التمارين لكل جلسة.
- رسوم بيانية لتقدم السعرات والوزن عبر الأيام.
- إضافة المزيد من الأطعمة والأطباق الشعبية.
- حسابات مستخدمين لتخزين بيانات أكثر من شخص.

</div>

---

<a id="english"></a>

# English

An Arabic-language web app that calculates your daily calorie and water needs, logs your meals and macros against a goal, and suggests weekly workout plans based on how many days you train. It runs locally with no internet connection and no third-party dependencies.

## Features

- **Calorie and water calculator:** enter sex, age, height, weight, activity level and goal (lose, maintain, gain) to get daily calories, water, protein, carbs, fat and BMI.
- **Macro tracker:** log breakfast, lunch and dinner from a built-in food list (40 foods, values per 100 g) or add a custom food with its calories.
    - A sticky counter at the top such as `508 / 2,358` with a progress bar that turns red when you exceed the goal.
    - Protein, carbs and fat counters, plus macros for each meal.
    - A date picker to review any day, and one-click removal of items.
- **Custom goal:** set your own calories, macros and water. Any macro left blank is split automatically (30% protein, 40% carbs, 30% fat).
- **Water tracking:** type an amount in ml (for example 500) and press **+**; a counter shows progress against the water goal, with a reset button.
- **Workout plans:** pick 2 to 6 days per week and get ready-made plans: full body, upper/lower, push/pull/legs and bro split, each with the full week, rest days, and exercises with sets and reps.

## Tech Stack

| Part | Technology |
|---|---|
| Frontend | HTML, CSS, vanilla JavaScript |
| Backend | Python (standard library only: `http.server`) |
| Database | SQLite (`sqlite3`) |
| Calculations | Mifflin-St Jeor in `calc.py` |

## Project Structure

```
calorie-app/
├── server.py        # server, JSON API and database access
├── calc.py          # calorie, water and macro calculations
├── foods.py         # food database
├── workouts.py      # workout plans
├── README.md
└── static/
    ├── index.html       # home page
    ├── calculator.html  # calorie and water calculator
    ├── tracker.html     # macro and water tracker
    ├── workouts.html    # workout plans
    ├── style.css
    └── app.js           # shared helpers
```

A `data.db` file is created automatically on first run and stores your meals, goal and water intake.

## Getting Started

Requirements: Python 3.8 or newer. No packages to install.

```bash
python server.py
```

Then open your browser at:

```
http://localhost:8000
```

Press `Ctrl + C` to stop the server. On Windows, try `py server.py` if `python` is not recognized.

> Always open the site through the URL above while the server is running. Opening the HTML files directly from the folder will not work because the pages rely on the API.

## How It Works

- **BMR:** Mifflin-St Jeor equation: `10×weight + 6.25×height − 5×age + 5` for males and `− 161` for females.
- **Total needs:** BMR multiplied by an activity factor (1.2 to 1.9).
- **Goal:** minus 500 kcal to lose, plus 300 to gain, unchanged to maintain, with a safe floor of 1500 kcal for males and 1200 for females.
- **Protein:** 2.0 g/kg to lose, 1.6 to maintain, 1.8 to gain.
- **Fat:** 25% of calories, with carbohydrates making up the remainder.
- **Water:** 33 ml per kg, plus 0 to 1 liter depending on activity.

## API

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/calc` | Calculate calories, water and macros |
| `GET` | `/api/foods` | List foods |
| `GET` / `POST` | `/api/goal` | Read and save the goal (calories, macros, water) |
| `GET` / `POST` | `/api/log?day=YYYY-MM-DD` | Read and add meal items |
| `DELETE` | `/api/log/<id>` | Delete an item |
| `GET` / `POST` / `DELETE` | `/api/water?day=YYYY-MM-DD` | Read, add and reset the day's water |
| `GET` | `/api/plans?days=N` | Workout plans for 2 to 6 days per week |

## Notes

- Food values are approximate. Add foods in `foods.py` and edit plans in `workouts.py`.
- Estimates and plans are general and for awareness only, not a substitute for advice from a dietitian, trainer or doctor.
- The server is meant for local use and has no authentication, so do not expose it to the internet as is.

## Ideas for Future Work

- Log weights and reps for each workout session.
- Charts of calorie and weight progress over time.
- More foods, including regional dishes.
- User accounts to support more than one person.
