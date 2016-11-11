$(document).ready(function() {
    normalizeGridHeights();
    fitHeaderText();
});

$(window).on('resize orientation', function() {
    normalizeGridHeights();
    fitHeaderText();
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

function fitHeaderText() {
    $('.jumbotron h1').each(function() {
        $(this).css('font-size', '');
        if ($(this).height() > 60) {
            $(this).css('font-size', $(this).width() / 10);
        }
    });
}