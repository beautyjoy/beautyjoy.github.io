$(document).ready(function() {
    normalizeGridHeights();
});

$(window).resize(function() {
    normalizeGridHeights();
});

function normalizeGridHeights() {
    $('.grid-gallery').each(function() {
        var maxHeight = 0;
        $(this).find('.caption').each(function() {
            $(this).height('auto');
            maxHeight = Math.max(maxHeight, $(this).height());
        }).each(function() {
            $(this).height(maxHeight);
        });
    });
}