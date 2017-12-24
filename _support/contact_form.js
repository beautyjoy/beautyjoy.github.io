var AWS = require('aws-sdk');
var ses = new AWS.SES();

// This must be verified to work.
var DESTINATION = 'cycomachead@gmail.com'; // testing...
// var DESTINATION = 'contact@bjc.berkeley.edu';

exports.handler = function(event, context) {
  console.log('Received event:', event)
  sendEmail(event, function(err, data) {
    context.done(err, null)
  })
}

function sendEmail(event, done) {
  var params = {
    Destination: {
      ToAddresses: [ DESTINATION ]
    },
    ReplyToAddresses: [
      event.email
    ],
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
  return '<tr><th style="text-align: left">' + keyName + ':</th><td>' + keyValue + '</td></tr>';
}

function buildEmail(event) {
  var body;

  body = 'Hello ' + event.name + ',<br>Thank you for your message.';
  body += '<br><br><table><tbody>';
  for (key in event) {
    body += tableRow(key, event[key]);
  }

  body += '</tbody></table>';
  return body;
}
