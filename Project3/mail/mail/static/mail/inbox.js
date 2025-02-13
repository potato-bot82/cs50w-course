document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => sent_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => archive_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  
  document.querySelector('#compose-form').addEventListener('submit', submit_email);
  
  // By default, load the inbox
  // archive_mailbox('archive');
  load_mailbox('inbox');

});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  
  // fetch emails for the selected mailbox
  fetch('/emails/inbox')
    .then(response => response.json())
    .then(emails => {
      // Clear previous emails
      document.querySelector('#emails-view').innerHTML += '<div id="emails-container"></div>';
      const emailsContainer = document.querySelector('#emails-container');

      // Loop through emails and display them
      emails.forEach(email => {
        const emailDiv = document.createElement('div')
        emailDiv.className = "email-box"; //Apply styles
        emailDiv.style.backgroundColor = email.read ? '#d3d3d3' : '#ffffff';
        emailDiv.innerHTML = `
            <strong>From:</strong> ${email.sender} <br>
            <strong>Subject:</strong> ${email.subject} <br>
            <small>${email.timestamp}</small>
        `;

      // Add a click event to view email details
      emailDiv.addEventListener('click', () => view_email(email.id))

      // Append email to the container
      emailsContainer.appendChild(emailDiv);
      })
    })
}

function submit_email(event) {
  event.preventDefault();

  const recipients = document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;
  
  fetch('/emails', {
    method: 'POST',
    headers: {
      'Content-Type' : 'application/json'
    },
    body: JSON.stringify({
        recipients: recipients,
        subject: subject,
        body: body
    })
  })
  .then(response => response.json())
  .then(result => {
    if (result.error) {
      alert('Error: ${result.error}');
    }  else {
      alert('Email sent successfully!')
      sent_mailbox('sent');
    }
  });
}

function view_email(email_id) {
  // Fetch the email data
  fetch(`/emails/${email_id}`)
    .then(response => response.json())
    .then(email => {
        // Hide the emails list and show the email view
        document.querySelector('#emails-view').style.display = 'none';
        document.querySelector('#compose-view').style.display = 'none';

        // Create a container for the email
        const emailView = document.querySelector('#emails-view');
        emailView.style.display = 'block';
        emailView.innerHTML = `
            <h3>${email.subject}</h3>
            <p><strong>From:</strong> ${email.sender}</p>
            <p><strong>To:</strong> ${email.recipients.join(', ')}</p>
            <p><strong>Timestamp:</strong> ${email.timestamp}</p>
            <hr>
            <p>${email.body.replace(/\n/g, '<br>')}</p>
            <hr>
            <button id="reply-btn">Reply</button>
            <button id="archive-btn">${email.archived ? 'Unarchive' : 'Archive'}</button>
          `;

        // Mark the email as read
        if (!email.read) {
            fetch(`/emails/${email_id}`, {
                method: 'PUT',
                body: JSON.stringify({ 
                  read: true 
                })
            });
        }

        // Add a reply button event listener
        document.querySelector('#reply-btn').addEventListener('click', () => reply_email(email_id));
        // Archive button
        document.querySelector('#archive-btn').addEventListener('click', () => toggle_archive(email_id, !email.archived));
        // Delete message
        // document.querySelector('#delete-btn').addEventListener('click', () => delete_mail(email_id));
      });
}

function toggle_archive(email_id, archiveStatus) { 
  // contoh console log 
  // console.log(`Archiving email ${email_id}: ${archiveStatus ? 'Archiving' : 'Unarchiving'}`);

  fetch(`/emails/${email_id}`, {
      method: 'PUT',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({ archived: archiveStatus })
  })
  .then(response => {
      // console.log("Fetch Response:", response);
      if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.text();
  })
  .then(archiveStatus => {
      // console.log("Server Response:", result);
      alert(archiveStatus ? 'Email archived successfully!' : 'Email unarchived successfully!');
      load_mailbox(archiveStatus='inbox'); 
  })
  .catch(error => console.error('Error:', error));
}



function sent_mailbox(mailbox) {
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Fetch sent emails
  fetch('/emails/sent')
    .then(response => response.json())
    .then(emails => {
        // Clear previous emails
        document.querySelector('#emails-view').innerHTML += '<div id="emails-container"></div>';
        const emailsContainer = document.querySelector('#emails-container');

        // Loop through emails and display them
        emails.forEach(email => {
            const emailDiv = document.createElement('div');
            emailDiv.classList.add('email-box');
            emailDiv.style.backgroundColor = email.read ? '#d3d3d3' : '#ffffff';
            emailDiv.innerHTML = `
                <strong>To:</strong> ${email.recipients.join(', ')} <br>
                <strong>Subject:</strong> ${email.subject} <br>
                <small>${email.timestamp}</small>
            `;

            // Add a click event to view email details
            emailDiv.addEventListener('click', () => view_email(email.id));

            // Append email to the container
            emailsContainer.appendChild(emailDiv);
        });
    });
}

// function delete_mail(email_id) { 
//   fetch(`/emails/${email_id}`, {
//       method: 'PUT',
//       headers: {
//           'Content-Type': 'application/json'
//       },
//       body: JSON.stringify({
//           deleted: true  // ✅ Marks email as "deleted" instead of actually deleting it
//       })
//   })
//   .then(result => {
//       if (result.error) {
//           alert(`Error: ${result.error}`);
//       } else {
//           alert('Email deleted successfully!');
//           load_mailbox('inbox'); // ✅ Reload inbox after deletion
//       }
//   })
//   .catch(error => console.error('Error:', error));
// }



function archive_mailbox(mailbox) {
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch('/emails/archive')
    .then(response => response.json())
    .then(emails => {
        // Clear previous emails
        document.querySelector('#emails-view').innerHTML += '<div id="emails-container"></div>';
        const emailsContainer = document.querySelector('#emails-container');

        // Loop through emails and display them
        emails.forEach(email => {
          if (email.archived) {  // Ensure filtering is applied
            const emailDiv = document.createElement('div');
            emailDiv.classList.add('email-box');
            emailDiv.style.backgroundColor = email.read ? '#d3d3d3' : '#ffffff';
            emailDiv.style.border = '1px solid #ccc';
            emailDiv.style.padding = '10px';
            emailDiv.style.marginBottom = '5px';
            emailDiv.style.cursor = 'pointer';

            emailDiv.innerHTML = `
                <strong>From:</strong> ${email.sender} <br>
                <strong>Subject:</strong> ${email.subject} <br>
                <small>${email.timestamp}</small>
            `;

            // Add event listener to view the email
            emailDiv.addEventListener('click', () => view_email(email.id));

            emailsContainer.appendChild(emailDiv);
        }
    });
})
.catch(error => console.error("Error loading archived emails:", error));
}

function reply_email(email_id) {
  // console.log(`test ${email_id}`);
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';


  fetch(`/emails/${email_id}`)
    .then(response => response.json())
    .then(emails => { 
      // console.log(`${emails.recipients}`);
  // Clear out composition fields
  document.querySelector('#compose-recipients').value = `${emails.sender}`;
  document.querySelector('#compose-subject').value = `Re: ${emails.subject}`;
  document.querySelector('#compose-body').value = `${emails.timestamp}, ${emails.recipients} wrote:`;
    });
}