# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# flash msgs list
msgsl_en = [
    'Error: only administrator can access the page',
    'Error: only main Admin account can access the page',
    'Notice: admin password has benn updated, all good',
    'Notice: settings have been updated , all good',
    'Error: wrong entery, something went wrong',
    "Error: user name already exists, choose another name",
    "Notice: user has been added , all good",
    "Error: user selected does not exist, something wrong !",
    "Error: main admin account cannot be updated ..",
    "Error: must unassign user to an office before updating it !",
    "Notice: user is updated , all good ",
    "Notice: user is deleted , all good",
    "Notice: all unassigned users got deleted, all good",
    "Error: you cannot logout without a login !",
    "Notice: logout is done, all good",
    "Error: operator not assigned by admin yet !",
    "Notice: loged-in and all good",
    "Error: wrong user name or password",
    "Error: operators are not allowed to access the page ",
    'Error: you must have available printer, to use printed',
    "Notice: make sure that printer is properly connected",
    "Error: the office is already reseted",
    "Notice: office has been reseted, all good ..",
    "Error: the task is already reseted",
    "Notice: task has been reseted, all good ..",
    "Error: no tickets left to pull from ..",
    "Notice: Ticket has been pulled ..",
    "Notice: ticket has been issued , all good ..",
    'Error: must disable slide-show before using video',
    'Notice: new video has been set, all good',
    "Notice: templates been updated, all good",
    'Error: must disable video before using slide-show',
    "Notice: new slide added, all good ",
    "Notice: slide settings is done, all good",
    "Error: there is no slides to be removed ",
    "Notice: All slides removed, all good",
    "Error: you have reached the limit of capacity size allowed ",
    "Error: you have reached the amount limit of multimedia files ",
    "Notice: if you followed the rules, it should be uploaded ..",
    "Error: there is no unused multimedia file to be removed !",
    "Notice: multimedia file been removed, all good",
    "Notice: Display customization has been updated, all good ..",
    "Notice: Touchscreen customization has been updated, all good ..",
    "Error: name is used by another one, choose another name",
    "Notice: office has been updated, all good ",
    "Notice: new office been added , all good ",
    "Error: you must reset it, before you delete it ",
    "Notice: office and its all tasks been deleted ",
    "Error: fault in search parameters",
    "Notice: Sorry, no matching results were found ",
    "Notice: task has been updated , all good",
    "Notice: task has been deleted , all good",
    "Notice: New task been added, all good",
    "Error: No offices exist to delete",
    "Error: No tasks exist to be reseted",
    "Error: file uploaded is too large ",
    "Error: something wrong , or the page is non-existing",
    "Notice: Make sure to make the printer shared on the local network",
    "Notice: Make sure to execute the command 'sudo gpasswd -a $(users) lp' and reboot the system",
    "Error: login is required to access the page"
]
msgsl_ar = [
    u'خطأ : يمكن للمدير فقط دخول الصفحة',
    u'خطأ : حساب المدير الرئيسي فقط يمكنه دخول الصفحة',
    u'تنبيه : تم تحديث كلمة سر الحساب الرئيسي بنجاح',
    u'تنبيه : تم تحديث الإعدادات بنجاح',
    u'خطأ : تم حدوث خطأ غير متوقع في النظام',
    u'خطأ : إسم المستخدم المدخل يوجد مثيله في قاعدة البيانات , قم بتغير الإسم',
    u'تنبيه : تم إضافة المستخدم بنجاح',
    u'خطأ : المستخدم المحدد لا وجود له',
    u'خطأ : لا يمكن تحديث حساب المدير الرئيسي',
    u'خطأ : يتوجب إلغاء تحديد المستخدم للمكتب لمكنك تحديث المستخدم',
    u'تنبيه : المستخدم تم تحديثه بنجاح',
    u'تنبيه : المستخدم تم حذفه بنجاح',
    u'تنبيه : تم حذف جميع المستخدميين غير المسجلين بنجاح',
    u'خطأ : ليمكنك تسجيل الخروج من غير تسجيل الدخول ',
    u'تنبيه : تم تسجيل خروج المستخدم بنجاح',
    u'خطأ : المشغل لم يتم تعينه من مدير النظام بعد ',
    u'تنبيه : تم تسجيل الدخول بنجاح ',
    u'خطأ : إسم مستخدم أو كلمة سر خاطئة ',
    u'خطأ : لا يسمح لحساب مشغل دخول الصفحة ',
    u'خطأ : يتوجب توفر طابعة متعرف عليها للتمكن من إختيار التذاكر المطبوعة',
    u'تنبيه : تأكد من أن الطابعة تم توصيلها و تعريفها بشكل صحيح',
    u'خطأ : المكتب معاد التهيئة في الإصل',
    u'تنبيه : تم إعادة تهيئ المكتب بنجاح',
    u'خطأ : المهمة معادة التهيئة في الأصل',
    u'تنبيه : تم إعادة تهيئ المهمة بنجاح',
    u'خطأ : لا يوجد تذاكر في قائمة الإنتضار',
    u'تنبيه : تم سحب التذكرة بنجاح',
    u'تنبيه : تم تسجيل التذكرة بنجاح',
    u'خطأ : يتوجب تعطيل عرض الشرائح لتتمكن من تفعيل عرض الفيديو',
    u'تنبيه : تم إعداد عرض الفيديو بنجاح',
    u'تنبيه : تم إعداد القوالب بنجاح',
    u'خطأ : يتوجب عليك تطيل عرض الفيديو لتتمكن من تفعيل عرض الشرائح',
    u'تنبيه : تم إضافة الشريحة بنجاح',
    u'تنبيه : تم إعداد الشرائح بنجاح',
    u'خطأ : لا يوجد شريحة متوفرة ليتم حذفها',
    u'تنبيه : تم حذف الشرائح بنجاح',
    u'خطأ : لقد تعديت الحد المسموح لحجم الملفات ',
    u'خطأ : لقد تعديت الحد المسموح لعدد الملفات ',
    u'تنبيه : إذا قمت بإتباع التعليمات , يفترض انه تم رفع الملف ',
    u'خطأ : لا يوجد أي ملفات غير مستخدمة ليم حذفها',
    u'تنبيه : تم حذف الملفات بنجاح',
    u'تنبيه : تم إعداد شاشة العرض بنجاح',
    u'تنبيه : تم إعداد شاشة اللمس بنجاح',
    u'خطأ : الإسم مكرر , يتوجب عليك إدخال إسم مميز',
    u'تنبيه : تم تحديث المكتب بنجاح',
    u'تنبيه : تم إضافة مكتب جديد بنجاح',
    u'خطأ : يتوجب إعادة التهيئة قبل الحذف ',
    u'تنبيه : تم حذف المكتب و جميع ملحقاته بنجاح',
    u'خطأ : حقول بحث غير صحيحة',
    u'تنبيه : لم يتم العثور على نتائج بحث متطابقة',
    u'تنبيه : تم تحديث المهمة بنجاح',
    u'تنبيه : تم حذف المهمة بنجاح',
    u'تنبيه : تم إضافة مهمة جديدة بنجاح',
    u'خطأ : لا يوجد أي مكاتب ليتم حذفها',
    u'خطأ : لا يوجد مهمات لتتم إعادة التهيئة',
    u"خطأ : الملف المرفوع حجمه يتعدى الحجم المسموح",
    u'خطأ : الصفحة غير متوفرة أو انها تحتوي على خطأ',
    u'تنبيه : تأكد من أن الطابعة تمت مشاركتها على الشبكة المحلية',
    u"تأكد من إدخال الأمر التالي , و إعادة تشغيل الحاسوب 'sudo gpasswd -a $(users) lp' ",
    u'خطأ : يتوجب تسجيل الدخول أولاً لدخول الصفحة'
]

TTS = {
    'en-us': [
        "The name ",
        "The number ",
        " , please proceed to the office number : "
    ],
    'ar': [
        "الرجاء من المدعوا ",
        "الرجاء من صاحب الرقم ",
        " , التوجه إلى مكتب رقم "
    ],
    'fr': [
        "le nom ",
        "le nombre ",
        " , s'il vous plaît procéder au numéro de bureau : "
    ],
    'es': [
        "el nombre ",
        "el número ",
        " , por favor diríjase al número de la oficina : "
    ],
    'it': [
        "il nome ",
        "il numero ",
        " , si prega di procedere al numero dell'ufficio : "
    ]
}

PRINTER = {
    'en': [
        "Version ",
        "\nOffice : ",
        "\nCurrent ticket : ",
        "\nTickets ahead : ",
        "\nTask : ",
        "\nTime : "
    ],
    'it': [
        "Versione ",
        "\nUfficio : ",
        "\nBiglietto corrente: ",
        "\nbiglietti in anticipo : ",
        "\nCompito : ",
        "\nTempo : "
    ],
    'es': [
        u"Version ",
        "\nOficina : ",
        "\nBillete actual : ",
        "\nBilletes antes : ",
        "\nTarea : ",
        "\nHora : "
    ],
    'fr': [
        "Version ",
        "\nBureau : ",
        "\nBillet actuel : ",
        "\nBillets devant : ",
        "\nTache : ",
        "\nTemps : "
    ]
}