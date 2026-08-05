---
---

$(document).ready(function() {
  normalizeGridHeights();
  fitHeaderText();
  setupContactForm();
  setupResourcesContent();
  setupPublicationsFilter();
});

$(window).on('resize orientation', function() {
  normalizeGridHeights();
  fitHeaderText();
});

/*
  TODO
*/
function setupResourcesContent() {
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
        } else {
          $(this).hide();
        }
      });
    }
  });

  $('[data-toggle=collapse]').each(toggleResourceCarets);
}

/*
  Filter the Research page publications list by free-text search, publication
  type, and year. All filtering happens client-side over the rendered list
  (see research.html), so the page keeps working without a server.
*/
function setupPublicationsFilter() {
  var $list = $('.js-publications');
  if (!$list.length) {
    return;
  }

  var $items = $list.find('.publication');
  var $search = $('#pub-search');
  var $category = $('#pub-category');
  var $affiliation = $('#pub-affiliation');
  var $year = $('#pub-year');
  var $count = $('.publications-count');
  var $empty = $('.publications-empty');

  function applyFilters() {
    var query = $.trim($search.val()).toLowerCase();
    var category = $category.val();
    var affiliation = $affiliation.val();
    var year = $year.val();
    var visible = 0;

    $items.each(function() {
      var $item = $(this);
      var matchesQuery = !query || $item.attr('data-search').indexOf(query) !== -1;
      var matchesCategory = category === 'all' || $item.attr('data-category') === category;
      var matchesAffiliation = affiliation === 'all' || $item.attr('data-affiliation') === affiliation;
      var matchesYear = year === 'all' || $item.attr('data-year') === year;
      var show = matchesQuery && matchesCategory && matchesAffiliation && matchesYear;

      $item.toggle(show);
      if (show) {
        visible += 1;
      }
    });

    var total = $items.length;
    if (visible === total) {
      $count.text('Showing all ' + total + ' publications');
    } else {
      $count.text('Showing ' + visible + ' of ' + total + ' publications');
    }
    $empty.prop('hidden', visible !== 0);
  }

  $search.on('input', applyFilters);
  $category.on('change', applyFilters);
  $affiliation.on('change', applyFilters);
  $year.on('change', applyFilters);
  applyFilters();
}

/**
 * Make the captions in our grid galleries to be of the same height.
 * TODO: Consider moving this to flexbox
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
 * Shrink Large Header text so it should no span more than 1 line.
 * This might look funky on excessively small screens?
 * TODO: This confuses me and I think it should be re-written...
 * but it mostly works.
 */
function fitHeaderText() {
  $('.jumbotron h1').each(function() {
    $(this).css('font-size', '');
    if ($(this).height() > 60) {
      $(this).css('font-size', Math.min($(this).width() / 12, 48));
    }
  });
}

/*
    Install an onclick handler to an item that toggles a caret between open
    and closed when clicked. (This assumes the state is always 'synced' so that
    it doesn't really need to know whether something _should_ be open or
    closed.)
*/
function toggleResourceCarets(idx, elm) {
  var hasCaret = $('.fa-caret-right', $(elm)).length;
  if (!hasCaret) {
    return;
  }
  $(elm).on('click', function() {
    var caret = $('[class*=fa-caret]', this);

    if (caret.hasClass('fa-rotate-90')) {
      caret.removeClass('fa-rotate-90');
    } else {
      caret.addClass('fa-rotate-90');
    }
  });
}

function setupContactForm() {
  function restoreButtonText() {
    $('.js-contactForm').find('button').text('Submit').removeAttr('disabled');
  }

  function buildAlert(type, text) {
    var alertButton = '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>';
    var $messageContainer = $('.js-submitMessageTarget');
    var $alert = $('<div>').addClass('alert').addClass('alert-' + type);
    $alert.append(alertButton).append(text);
    $alert.alert();
    $messageContainer.append($alert);
    $('html, body').animate({
      scrollTop: $messageContainer.offset().top
    }, 1000);
  }

  function handleSuccess() {
    buildAlert('success', 'Thanks for your message! We\'ll be in touch.');
    $('.js-contactForm').trigger('reset');
  }

  function handleFailure() {
    buildlAret('error', 'Uh-oh! You\'re message couldn\'t be sent. Please try again, or send a message to <a href="mailto:{{site.email}}">{{site.email}}</a>');
  }

  $('.js-contactForm').submit(function (event) {
    event.preventDefault();
    var $form = $('.js-contactForm');
    var formURL = 'https://arp3ezzi5l.execute-api.us-west-2.amazonaws.com/prod/send-email';
    var formData = $form.serializeArray().reduce(function(acc, curr) {
      acc[curr.name] = curr.value;
      return acc;
    }, {});

    $form.find('button').html(
      '<i class="fa fa-spin fa-spinner" aria-hidden=true></i>&nbsp;Sending...'
    ).attr('disabled', true);
    $.ajax({
      type: 'POST',
      url: formURL,
      dataType: 'json',
      contentType: 'application/json',
      data: JSON.stringify(formData),
      success: handleSuccess,
      error: handleFailure,
      complete: restoreButtonText
    })
  });
}
