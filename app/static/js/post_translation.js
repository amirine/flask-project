/* Handles 'Translate' button click */

function translate(postTextElem, postText, sourceLang, destLang) {
    let current_text = $(postTextElem).text();
    $.post('/translate', {
        text_to_translate: $(postTextElem).text(),
        source_language: sourceLang,
        destination_language: destLang
    }).done(function (response) {
        if (current_text === postText) {
            $(postTextElem).text(response['text']);
        } else {
            $(postTextElem).text(postText);
        }
    }).fail(function () {
        if (current_text === postText) {
            $(postTextElem).text("{{ _('Error: Could not contact server.') }}");
        } else {
            $(postTextElem).text(postText);
        }
    });
}
