{% macro wallpapers(selector, enable_reddit=True, overlay="rgba(0,0,0,0.7)", duration=60) %}
// Macro to set the background wallpapers for a given element via `selector`
{% if enable_reddit %}
redditWallpapers({
    isFixed: 'true',
    id: '{{ selector }}',
    isOverlayed: 'true',
    overlay: '{{ overlay }}',
    duration: {{ duration }},
    limit: 100,
    timeout: 1,
    category: ['CityPorn'],
    defaultImg: "{{ url_for('static', filename='images/dbg.jpg') }}"
})
{% else %}
$('{{ selector }}').css({
    'background-size': 'cover',
    'background-repeat': 'no-repeat',
    'background-position': 'center',
    'background-image': "linear-gradient({{ overlay }}, {{ overlay }}), url({{ url_for('static', filename='images/dbg.jpg') }})"
})
{% endif %}
{% endmacro %}
