document.addEventListener('DOMContentLoaded', function() {

    // Use buttons to toggle between views
    // document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
    // document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
    // document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
    // document.querySelector('#compose').addEventListener('click', () => compose_email());
  
    // By default, load the inbox
    // load_mailbox('inbox');
    load_wishlist();
  });

  function load_wishlist() {
  
    // Show the mailbox and hide other views
    document.querySelector('#wishlist-view').style.display = 'block';
    // document.querySelector('#compose-view').style.display = 'none';
    // document.querySelector('#email-view').style.display = 'none';
  
    // access the div that will contain the list of emails
    // and clear it out
    const wishlist_list = document.querySelector('#wishlist-view-list');
    wishlist_list.innerHTML = '';
   
    // get the list of emails for the requested mailbox
    fetch(`/wishlist`)
    .then(response => response.json())
    .then(wishlist => {
  
      console.log(wishlist);
  
      // for each of the emails
      wishlist.forEach(function(game) {
  
        // create a row div and set some style properties
        const div_row = document.createElement('div');
        div_row.className = 'row wishlist-game-row';
        div_row.style.border = 'thin solid #007bff';
        div_row.style.padding = '5px';
        div_row.style.margin = '5px';
  
        // div_row.onclick = function() {
        //   load_email(email.id);
        // }
  
        // read emails should have a grey background
        // if (email.read === true) {
        //   div_row.style.backgroundColor = '#CECECE';
        // }
  
        // create columns in the row for sender, subject, and sent time
        const title = document.createElement('div');
        title.className = 'col-sm';
        title.style.textAlign = 'center';
  
        const current_price = document.createElement('div');
        current_price.className = 'col-sm';
        current_price.style.textAlign = 'center';
  
        const sale = document.createElement('div');
        sale.className = 'col-sm';
        sale.style.textAlign = 'center';

        const regular_price = document.createElement('div');
        regular_price.className = 'col-sm';
        regular_price.style.textAlign = 'center';
  
        // add the content to the divs
        title.innerHTML = game.title;
        current_price.innerHTML = game.current_price;
        sale.innerHTML = game.noted_sale_type
        regular_price.innerHTML = game.regular_price;
  
        // add the columns to the row
        div_row.append(title);
        div_row.append(current_price);
        div_row.append(sale);
        div_row.append(regular_price)
  
        // add the row to the list container
        wishlist_list.append(div_row);
      });
    });

  // Show the mailbox name
//   document.querySelector('#mailbox-header').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
}