$(document).ready(function() {
    normalizeGridHeights();
    fitHeaderText();

    $('.resources-filter').change(function() {
        var selectedTag = $(this).val();
        if (selectedTag == "all") {
            $(this).parents('.section').nextAll('.section').show();
            $('.resources-list').find('li').show();
        } else {
            // Show only resources which have the selected filter as a class
            $(this).parents('.section').nextAll('.section').hide();
            $('.resources-list').find('li').each(function() {
                if ($(this).hasClass(selectedTag)) {
                    $(this).show();
                    $(this).parents('.section').show();
                }
                else {
                    $(this).hide();
                }
            })
        }
    });
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