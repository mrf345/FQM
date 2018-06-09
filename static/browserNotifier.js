// Dependencies: jQuery, jQuery-ui, FontAwesome

var browserNotifier = function (options={}, callback=function () {}, uniVal='v' + Math.floor(Math.random() * 1000000)) {
    var returnBN = {}; returnBN[uniVal] = {} // unique object name to return

    returnBN[uniVal].options = {
        text: options.text || 'You are not using Firefox, which this project is designed and most suited for.',
        textClass: options.textClass || '',
        textStyle: options.textStyle || {
            'color': 'white',
            'font-family': 'Georgia, Times, serif',
            'text-shadow': '0 0 30px rgba(255,255,255,0.5)'
        },
        iconLink: options.iconLink || 'https://www.mozilla.org/firefox/download/thanks/',
        iconClass: options.iconClass || 'fa fa-firefox',
        iconStyle: options.iconStyle || {
            'color': 'white',
            'text-shadow': '0 0 30px rgba(255,255,255,0.5)',
            'font-size': '800%'
        },
        buttonText: options.buttonText || 'I understand, just continue.',
        buttonClass: options.buttonClass || 'btn btn-lg btn-warning',
        buttonStyle: options.buttonStyle || {
            'font-family': 'Georgia, Times, serif',
            'font-size': '140%',
            'font-weight': 'bold',
            'font-stretch': 'ultra-expanded'
        },
        overlayColor: options.overlayColor || 'rgba(0,0,0,0.85)',
        overlayClass: options.overlayClass || '',
        overlayStyle: options.overlayStyle || {},
        effectDuration: options.effectDuration * 1000 || 1000,
        storeVal: options.storeVal || 'browserNotifier', // value to to identify notifier in localStorage
        validator: options.validator || function () {
            return new Promise(function (resolve, reject) {
                return resolve(true)
            })
        } // if returns true notifier will be activated
    }

    returnBN[uniVal].defaults = { // list of browsers name in navigator and fa- icon names
        elements: { // list of jQuery elements to be appended
            text: $('<h1>').text(returnBN[uniVal].options.text).css(returnBN[uniVal].options.textStyle).addClass('text-center'),
            button: $('<button>').addClass(returnBN[uniVal].options.buttonClass).css(returnBN[uniVal].options.buttonStyle)
            .text(returnBN[uniVal].options.buttonText).click(function () {
                returnBN[uniVal].__exit__()
                callback()
            }),
            icon: $('<a>').attr('href', returnBN[uniVal].options.iconLink).attr('target', '_blank')
            .append(
                $('<span>').addClass(returnBN[uniVal].options.iconClass).css(returnBN[uniVal].options.iconStyle)
                .hover(function () {
                    $(this).animate({'color': 'gray'})
                }, function () {
                    $(this).animate({'color': 'white'})
                })
            )
        }
    }

    returnBN[uniVal].defaults.elements.overlay = $('<div>')
    .attr('id', 'browserNotifier').addClass(returnBN[uniVal].options.overlayClass)
    .css(Object.assign({
        'display': 'flex',
        'position': 'fixed',
        'opacity': '0',
        'background-color': returnBN[uniVal].options.overlayColor,
        'width': '100%',
        'height': '100%',
        'top': '0',
        'bottom': '0',
        'left': '0',
        'right': '0',
        'z-index': '10',
        'flex-direction': 'column',
        'align-items': 'center',
        'justify-content': 'space-around'
    }, returnBN[uniVal].options.overlayStyle))
    .append(returnBN[uniVal].defaults.elements.icon)
    .append(returnBN[uniVal].defaults.elements.text)
    .append(returnBN[uniVal].defaults.elements.button)


    returnBN[uniVal].__init__ = function () {
        var todoTwice = function () {
            returnBN[uniVal].options.validator()
            .then(
                function () {
                    $('body').append(returnBN[uniVal].defaults.elements.overlay)
                    $(returnBN[uniVal].defaults.elements.overlay).animate({'opacity': '1'}, returnBN[uniVal].options.effectDuration)
                }
            ).catch(
                function (e) {
                    callback()
                }
            )
        }
        if (document.readyState === 'complete') todoTwice()
        else $(todoTwice)
    }

    returnBN[uniVal].__exit__ = function () {
        $(returnBN[uniVal].defaults.elements.overlay).animate({'opacity': '0'}, returnBN[uniVal].options.effectDuration,
        complete=function () {
            $(returnBN[uniVal].defaults.elements.overlay).remove()
            localStorage[returnBN[uniVal].options.storeVal] = 'yes'
        })
    }


    if (!localStorage[returnBN[uniVal].options.storeVal]) returnBN[uniVal].__init__()
    else callback()
    return returnBN[uniVal]
}