---
---

$(document).ready(function() {
    normalizeGridHeights();
    fitHeaderText();

    // JS to show/hide resources by tags
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
            });
        }
    });
});

$(window).on('resize orientation', function() {
    normalizeGridHeights();
    fitHeaderText();
});

/**
 * Make the captions in our grid galleries to be of the same height.
 */
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

/**
 * If window width is too small such that the page header is split across multiple lines,
 * shrink it in proportion to the window width so it fits width-wise.
 */
function fitHeaderText() {
    $('.jumbotron h1').each(function() {
        $(this).css('font-size', '');
        if ($(this).height() > 60) {
            $(this).css('font-size', $(this).width() / 10);
        }
    });
}