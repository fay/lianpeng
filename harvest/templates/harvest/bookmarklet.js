//bookmarklet specific variable names
var __containerId = 'LP___container';
var __frameName = 'LP__frame';
var __current_y = scrollY // remember where user scroll to in current page;

// build a form that will be posted to the iframe
// this allows information from the current page to be passed to
// the iframe without causing a cross site scripting related
// unauthorized exception to be thrown
function __buildForm($, f) {
    var note = $('meta[name="description"]').attr('content');
    if(note) {
        note = note.slice(0, 250);
    }
    f.append(
        $('<input type="hidden" name="url" />')
            .attr('value', window.location)
    ).append(
        $('<input type="hidden" name="note" />').attr('value', note)
    ).append(
        $('<input type="hidden" name="title" />').attr('value', window.document.title)
    ).append(
        $('<input type="hidden" name="domain" />').attr('value', window.document.domain)
    ).append(
        $('<input type="hidden" name="charset" />').attr('value', window.document.charset ? window.document.charset :  window.document.characterSet)
    );
    f.submit();
    __watchForCommands($);
}

function __watchForCommands($) {
    var __detail = location.hash.match(/#c=([^&]+)(?:&v=([^&]+))?/);

    if (__detail) {
        var __cmd = __detail[1];
        if (__detail[2]) {
            var __val = __detail[2];
        }
        if (__cmd == 'close') {
            history.go(-1);
            $('#' + __containerId).fadeOut();
        }
    }
    setTimeout(function() { __watchForCommands($); }, 200);
}

function __initBookmarklet($) {
    var init = function () {
        var container = $('<div />');
        var frame = $('<iframe />');
        var form = $('<form />');

        $('#' + __containerId).remove();

        $('body').append(
            container
                .attr('id', __containerId)
                .css({
                    'position': 'fixed',
                    'top': '0px',
                    'right': '0px',
                    'height': '100%',
                    'width': '100%',
                    'background-color': 'transparent',
                    'z-index': '2147483647',
                    'display': 'none'
                })
                .append(
                    frame
                        .attr('name', __frameName)
                        .attr('id', __frameName)
                        .attr('frameborder', '0')
                        .css({
                            'border': '0 none',
                            'margin': '0',
                            'padding': '0',
                            'height': '100%',
                            'width': '100%'
                        })
                        .load(function () {
                            $('#' + __containerId).fadeIn();
                        })
                )
                .append(
                    form
                        .attr('method', 'get')
                        .attr('action', __postPath) // __postPath is defined in the bookmarklet
                        .attr('target', __frameName)
                )
        );

        __buildForm($, form);
    };
    init();
}

jQueryBookmarklet = function() {
    var callback, tag;
        
    var log = function() {
        if (typeof (console) != 'undefined') {
            var args = Array.prototype.slice.call(arguments);         // convert args to normal array
            var type = args[0];                                     // capture the console operation name http://getfirebug.com/wiki/index.php/Console_API
            if (typeof (console[type]) != 'undefined') {
                var consoleArgs = args.slice(1 || args.length);     // remove index 0 from array
                args.push.apply(args, consoleArgs);
                if (typeof (console[type].apply) != 'undefined') {  // internet explorers console won't support using apply this way, so logging will be disabled there
                    console[type].apply(console, consoleArgs);         // will expand consoleArgs so elements are passed as individual args, splat operator
                }
            }
        }
    };

    var ensurejQuery = function(version) {
        log('group', 'ensure jQuery');
        if (!window.jQuery
            || version > window.jQuery.fn.jquery) {
            log('info', 'inserting jQuery');
            tag = document.createElement('script');
            tag.type = 'text/javascript';
            tag.src = ('https:' == document.location.protocol ? 'https://' : 'http://') + 'ajax.microsoft.com/ajax/jquery/jquery-' + version + '.min.js'; 	// use Microsoft CDN for jQuery
            tag.onload = tag.onreadystatechange = function () {
                if (tag.readyState
                    || tag.readyState == 'loaded'
                    || tag.readyState == 'completed') {
                    tag.onreadystatechange = null;
                    initJQuery();
                }
                else {
                    initJQuery();
                }
            };
            document.getElementsByTagName('head')[0].appendChild(tag);
        }
        else {
            var jq = window.jQuery;
            log('info', 'jQuery %v found', jq.fn.jquery);
            execLoadedCallback(jq);
        }
    };

    var initJQuery = function() {
        var jq = window.jQuery;
        jq.noConflict(true);
        jq(tag).remove();
        log('info', 'jQuery %v loaded', jq.fn.jquery);
        execLoadedCallback(jq);
    };

    var execLoadedCallback = function(jq) {
        log('groupEnd');
        callback(jq);
    };

    return {
        $: null,
        init: function(version, loadedCallback) {
            if(this.$) {
                loadedCallback(this.$);
            }
            else {
                callback = function(jq){
                    jQueryBookmarklet.$ = jq;
                    loadedCallback(jQueryBookmarklet.$);
                };
                ensurejQuery(version);
            }
        }
    };
}();
