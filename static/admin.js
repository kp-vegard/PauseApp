/* Runs function WindowLoad when loading the site */
if (window.addEventListener) {
    window.addEventListener('load', WindowLoad, false);
} else if (window.attachEvent) {
    window.attachEvent('onload', WindowLoad)
}

/* Runs saveState when manually refreshing site */
window.addEventListener('beforeunload', function(event){
    event.preventDefault();
    saveState();
});

/* Automaticly scrolls to last known postition */
function WindowLoad(event) {
    if (window.location.href.indexOf('page_y') != -1) {
        var page_y = window.location.href.split('=')[1];
        setTimeout(function(){
            window.scrollTo(0, page_y)
        }, 2)
    }
}

/* Saves current scroll position to the end of url */
var saveState = function SS() {
    var page_y = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
    if (window.location.href.indexOf('page_y') == -1) {
        window.location.href = window.location.href + '?page_y=' + page_y;
    } else {
        var s = window.location.href.split('?')[0];
        window.location.href = s + '?page_y=' + page_y
    }
}

/* Updates site every 10 seconds */
setTimeout(function(){
    saveState()
}, 10000)