document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#sale-games-button').addEventListener('click', () => load_gamelist('sale-games'));
  document.querySelector('#wishlist-games-button').addEventListener('click', () => load_gamelist('wishlist-games'));
  document.querySelector('#all-games-button').addEventListener('click', () => load_gamelist('all-games'));
  document.querySelector('#search-form').addEventListener('submit', () => search());

  load_gamelist('sale-games');
});

function reset_gamelist_nav_buttons() {
  const nav_buttons = document.querySelectorAll('.gamelist-nav-btn');
  
  nav_buttons.forEach(nav_button => {
    nav_button.className = 'btn btn-sm btn-outline-primary gamelist-nav-btn';
  });
}

function search() {
  console.log("in search");
  // reset_gamelist_nav_buttons();
  

  // get the search entry
  search_entry = document.querySelector('#search-entry').value;

  console.log(`search entry: ${search_entry}`);

  const gamelist_list = document.querySelector('#gamelist-view-list');
  gamelist_list.innerHTML = '';

  // get the list of emails for the requested mailbox
  fetch(`/search/${search_entry}`)
  .then(response => response.json())
  .then(wishlist => {

    console.log(wishlist);

    // for each of the emails
    wishlist.forEach(function(game) {

      // create a row div and set some style properties
      const div_row = document.createElement('div');
      div_row.className = 'row gamelist-game-row';
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
      gamelist_list.append(div_row);
    });
  });

// Show the mailbox name
//   document.querySelector('#mailbox-header').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  
}

function load_gamelist(gamelist) {

  // Show the mailbox and hide other views
  document.querySelector('#gamelist-view').style.display = 'block';

  // set the active nav button
  // and reset the rest
  reset_gamelist_nav_buttons();
  const active_button = document.getElementById(`${gamelist}-button`);
  active_button.className = 'btn btn-sm btn-primary gamelist-nav-btn';
  
  // document.querySelector('#compose-view').style.display = 'none';
  // document.querySelector('#email-view').style.display = 'none';

  // access the div that will contain the list of emails
  // and clear it out
  const gamelist_list = document.querySelector('#gamelist-view-list');
  gamelist_list.innerHTML = '';
  
  // get the list of emails for the requested mailbox
  fetch(`/games/${gamelist}`)
  .then(response => response.json())
  .then(wishlist => {

    // console.log(wishlist);

    // for each of the emails
    wishlist.forEach(function(game) {

      // create a row div and set some style properties
      const div_row = document.createElement('div');
      div_row.className = 'row gamelist-game-row';
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
      gamelist_list.append(div_row);
    });
  });

// Show the mailbox name
//   document.querySelector('#mailbox-header').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
}