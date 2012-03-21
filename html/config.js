{% if apertium_api_key %}
var APERTIUM_API_KEY = '{{ apertium_api_key }}';
{% endif %}
{% if apertium_langs %}
var APERTIUM_LANGS = [
{% for lang in apertium_langs %}
    '{{ lang }}',
{% endfor %}
];
{% endif %}
{% if microsoft_api_key %}
var MICROSOFT_API_KEY = '{{ microsoft_api_key }}';
{% endif %}
{% if microsoft_langs %}
var MICROSOFT_LANGS = [{% for lang in microsoft_langs %}'{{ lang }}',{% endfor %}];
{% endif %}
