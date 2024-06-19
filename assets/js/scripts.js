---
---

$(document).ready(function() {
  normalizeGridHeights();
  fitHeaderText();
  setupContactForm();
  setupResourcesContent();
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
