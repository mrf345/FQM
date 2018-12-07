# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from app.getWithAlias import getWithAlias

# flash msgs list
flashMessages = []

PRINTER = {
    'en': getWithAlias(),
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

GUI = {
    'en': {
        '1': u'Select language to change the interface to',
        '2': u'About FQM',
        '3': u'Start',
        '4': u'Start the server',
        '5': u'Stop',
        '6': u'Stop the server',
        '7': u'Select network interface with IP, so the server runs on it',
        '8': u'Select a port, so the server runs through it',
        '9': u'Status of the server',
        '10': u'Server is <u>Running</u> <br> On : ',
        '11': u'Server is <u> Not running </u> <br>',
        '12': u'All credit reserved to the author of FQM version ',
        '13': u', This work is a free, open-source project licensed ',
        '14': u' under Mozilla Public License version 2.0 . <br><br>',
        '15': u' visit us for more infos and how-tos :<br> ',
        '16': u'Exiting while running',
        '17': u'Are you really sure, you want to exit ?',
        '18': u' Opps, a critical error has occurred, we will be ',
        '19': u' grateful if you can help fixing it, by reporting to us at : <br><br> ',
        '20': u'Critical Error'
    },
    'ar': {
        '1': u'إختر لغة لواجهة الإستخدام',
        '2': u'عن النظام',
        '3': u'تشغيل',
        '4': u'قم بتشغيل الخادمة',
        '5': u'إيقاف',
        '6': u'قم بإقاف الخادمة',
        '7': u"إختار عنوان IP ليتم بث الخدمة عليه",
        '8': u"إختار منفذ ليتم بث الخدمة من خلاله",
        '9': u"حالة الخدمة ",
        '10': u"الخدمة <u>مشغــلة</u> و تبث على : <br>",
        '11': u"الــخـدمة <u>متــوقفــة</u><br>",
        '12': u" إدارة الحشود الحر النسخة ",
        '13': u"حقوق نشر هذا البرنامج محفوظة و تخضع لرخصة البرامج الحرة و مفتوحة المصدر ",
        '14': u" Mozilla Public License version 2.0 . <br>",
        '15': u"للمزيد من المعلومات و الشروحات , قم بزيارة : <br>",
        '16': u"تأكيد الخروج",
        '17': u"تريد بالفعل , الخروج و إيقاف البرنامج ؟",
        '18': u"حدث خطأ فادح في تشغيل النظام , سنكون شاكرين لك إن ",
        '19': u"قمت بتبليغنا عنه , ليتم إصلاحه في أقرب وقت <br><br>",
        '20': u"خطأ في التشغيل"
    },
    'it': {
        '1': u"selezionare la lingua dell'interfaccia",
        '2': u'su FQM',
        '3': u'avvia',
        '4': u'avvia il server',
        '5': u'fermare',
        '6': u'fermare il server',
        '7': u"selezionare l'interfaccia di rete con l'indirizzo IP per avviare il server",
        '8': u'selezionare una porta per avviare il server',
        '9': u'stato del server',
        '10': u'il server <u>è in esecuzione</u> <br> su : ',
        '11': u'il server <u> non è in esecuzione </u> <br>',
        '12': u"Tutto il credito è riservato all'autore della versione FQM ",
        '13': u', questo lavoro è un progetto open source gratuito concesso in licenza ',
        '14': u'Mozilla Public License version 2.0 . <br><br>',
        '15': u' visitaci per maggiori informazioni su :<br> ',
        '16': u'uscire',
        '17': u'Sei proprio sicuro, vuoi uscire?',
        '18': u' si è verificato un errore critico. ',
        '19': u' per favore segnalacelo su: : <br><br> ',
        '20': u'errore critico'
    },
    'es': {
        '1': u'seleccionar idioma de la interfaz',
        '2': u'sobre FQM',
        '3': u'iniciar',
        '4': u'iniciar el servidor',
        '5': u'detener',
        '6': u'detener el servidor',
        '7': u'seleccione la interfaz de red con la dirección IP del servidor',
        '8': u'seleccione el puerto para el servidor',
        '9': u'estado del servidor',
        '10': u'el servidor <u>se está ejecutando</u> : <br> ',
        '11': u'el servidor <u>no se está ejecutando</u> <br>',
        '12': u'Todo el crédito reservado al autor de la versión FQM ',
        '13': u', Este trabajo es un proyecto gratuito de código abierto con licencia bajo ',
        '14': u' Mozilla Public License version 2.0 . <br><br>',
        '15': u' visítenos para más información sobre : <br>',
        '16': u'salir',
        '17': u'¿Estás realmente seguro, quieres salir?',
        '18': u' un error crítico ha ocurrido. ',
        '19': u'Por favor reporte este error a nosotros en: <br><br> ',
        '20': u'error crítico'
    },
    'fr': {
        '1': u"sélectionnez la langue de l'interface",
        '2': u'à propos de FQM',
        '3': u'démarrer',
        '4': u'démarrer le serveur',
        '5': u'arrête',
        '6': u'arrête le serveur',
        '7': u"sélectionnez l'interface réseau avec IP pour le serveur",
        '8': u"sélectionnez un port pour le serveur",
        '9': u'état du serveur',
        '10': u'le serveur <u> fonctionne </u> <br> sur : ',
        '11': u'le serveur <u> ne fonctionne pas </u> <br>',
        '12': u"Tout le crédit réservé à l'auteur de la version FQM ",
        '13': u', Ce travail est un projet libre et open-source sous licence ',
        '14': u' Mozilla Public License version 2.0 . <br><br>',
        '15': u" Visitez-nous pour plus d'informations :<br> ",
        '16': u'quitter',
        '17': u'êtes-vous sûr de vouloir quitter ?',
        '18': u' une erreur critique est survenue. veuillez ',
        '19': u' nous signaler cette erreur sur: <br><br> ',
        '20': u'erreur critique'
    }
}