var AWS = require('aws-sdk');
var ses = new AWS.SES();

// This must be verified to work.
// var DESTINATION = 'cycomachead@gmail.com'; // testing...
var DESTINATION = 'contact@bjc.berkeley.edu';

exports.handler = function(event, context) {
  console.log('Received event:', event)
  sendEmail(event, function(err, data) {
    context.done(err, null)
  })
}

function capitalize(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

function sendEmail(event, done) {
  var params = {
    Destination: {
      ToAddresses: [ DESTINATION ]
    },
    ReplyToAddresses: [ event.email ],
    Message: {
      Body: {
        Html: {
          Data: buildEmail(event),
          Charset: 'UTF-8'
        }
      },
      Subject: {
        Data: 'BJC Contact: ' + event.subject,
        Charset: 'UTF-8'
      }
    },
    Source: DESTINATION
  }
  ses.sendEmail(params, done);
}

function tableRow(keyName, keyValue) {
  return '<tr><th style="text-align: left">' + capitalize(keyName) + ':</th><td>' + keyValue + '</td></tr>';
}

function buildEmail(event) {
  var body;

  body = 'A new message has been sent.';
  body += '<br><br><table><tbody>';
  for (var key in event) {
    body += tableRow(key, event[key]);
  }

  body += '</tbody></table>';
  return body;
}
