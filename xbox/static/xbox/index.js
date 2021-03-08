document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('login').style.display = 'none';
  document.getElementById("add-game").style.display = 'none';
  document.getElementById('message').style.display = 'none';

  // Use buttons to toggle between views
  document.querySelector('#sale-games-button').addEventListener('click', () => load_gamelist('sale-games'));
  document.querySelector('#wishlist-games-button').addEventListener('click', () => load_gamelist('wishlist-games'));
  document.querySelector('#all-games-button').addEventListener('click', () => load_gamelist('all-games'));

  // add the search
  document.querySelector('#search-form').addEventListener('submit', () => search());

  // by default load the sale games view
  load_gamelist('sale-games');
});


function reset_gamelist_nav_buttons() {
  document.getElementById('message').style.display = 'none';
  // reset all the nav buttons, make them unfilled
  const nav_buttons = document.querySelectorAll('.gamelist-nav-btn');
  
  nav_buttons.forEach(nav_button => {
    nav_button.className = 'btn btn-sm btn-outline-primary gamelist-nav-btn';
  });
}


function view_game(game_id) {

  reset_gamelist_nav_buttons();

  view_heading = document.getElementById('view-heading');
  
  // show the game and hide the other views
  document.querySelector('#gamelist-view-list').style.display = 'none';
  document.querySelector('#game-view').style.display = 'block';

  // create an element to display the email and blank it out
  const game_view = document.querySelector('#game-view'); 
  game_view.innerHTML = '';
  console.log('before the fetch');

  fetch(`/game/${game_id}`)
  .then(response => response.json())
  .then(game => {
    console.log(game);
    view_heading.innerHTML = game.title;
    const image_container = document.createElement('div');
    const image = document.createElement('img');
    const current_price = document.createElement('div');
    const regular_price = document.createElement('div');
    const store_link_container = document.createElement('div');
    const store_link = document.createElement('a');


    image.src = game.image;
    image.className = 'img-fluid rounded';
    image.alt = game.title;
    current_price.innerHTML = game.current_price;
    regular_price.innerHTML = game.regular_price;
    store_link.href = game.url;
    store_link.innerHTML = `Store page for ${game.title}`
    console.log('settlings the elements up');

    image_container.append(image);
    store_link_container.append(store_link);

    game_view.append(image_container);
    game_view.append(current_price);
    game_view.append(regular_price);
    game_view.append(store_link_container);

  });
}


function view_games(games) {

  document.querySelector('#login').style.display = 'none';
  document.querySelector('#game-view').style.display = 'none';
  document.getElementById("add-game").style.display = 'none';
  document.querySelector('#gamelist-view-list').style.display = 'block'
  const view_heading = document.getElementById('view-heading');

  if (games.length === 0) {
    console.log('Add games to wishlist');
    message = document.getElementById('message');
    message.innerHTML = 'Add some games to your wishlist!'
    message.style.display = 'block';
  }

  const gamelist_list = document.querySelector('#gamelist-view-list');
  gamelist_list.innerHTML = '';

  // for each of the emails
  games.forEach(function(game) {

    // create a row div and set some style properties
    const div_row = document.createElement('div');
    div_row.className = 'row gamelist-game-row';
    div_row.style.border = 'thin solid #007bff';
    div_row.style.padding = '5px';
    div_row.style.margin = '5px';
    
    

    

    // read emails should have a grey background
    // if (email.read === true) {
    //   div_row.style.backgroundColor = '#CECECE';
    // }

    // create columns in the row for sender, subject, and sent time

    const image_container = document.createElement('div');
    image_container.className = 'col-sm';
    // image_container.style.textAlign = 'center';
    image_container.style.textAlign = 'left';

    const wishlist_indicator_container = document.createElement('div');
    const wishlist_indicator = document.createElement('i');
    console.log(game.is_wishlist_user);
    if (game.is_wishlist_user === true) {
      wishlist_indicator.className = 'fas fa-star';
      wishlist_indicator.style.color = '#007bff';
    }
    else {
      wishlist_indicator.className = 'far fa-star';
      wishlist_indicator.style.color = '#007bff';
    }
    
    wishlist_indicator_container.append(wishlist_indicator);

    wishlist_indicator_container.onclick = function() {
      // star_game(game.id);
      fetch(`/game/${game.id}`, {
        method: 'PUT',
        mode: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': get_cookie('csrftoken') 
        },
        body: JSON.stringify({
            starred: true
        })
      })
      .then(response => response.json())
      .then(game => {
        if (game.error) {
          // load_gamelist('sale-games');
          view_heading.style.display = 'none';
          document.querySelector('#gamelist-view').style.display = 'none'; 
          document.getElementById('login').style.display = 'block';
        }
        else {
          console.log(game);
          if (game.is_wishlist_user === true) {
            wishlist_indicator.className = 'fas fa-star';
            wishlist_indicator.style.color = '#007bff';
          }
          else {
            wishlist_indicator.className = 'far fa-star';
            wishlist_indicator.style.color = '#007bff';
          }
        }
      });
    }

    const image = document.createElement('img');
    image.className = 'img-fluid rounded';
    // image.className = 'img-thumbnail rounded';
    console.log(game.image);
    image.src = game.image;

    image_container.append(image);

    const title = document.createElement('div');
    title.className = 'col-sm';
    // title.style.textAlign = 'center';
    title.style.textAlign = 'left';
    title.style.fontWeight = 'bold';

    const current_price = document.createElement('div');
    current_price.className = 'col-sm';
    // current_price.style.textAlign = 'center';
    current_price.style.textAlign = 'left';

    const sale = document.createElement('div');
    sale.className = 'col-sm';
    sale.style.textAlign = 'center';

    const regular_price = document.createElement('div');
    regular_price.className = 'col-sm';
    regular_price.style.textAlign = 'center';

    // linkable_elements = [title, image_container];
    // linkable_elements = [div_col_image, div_col_info];
    // linkable_elements.forEach(function(linkable_element) {
    //   linkable_element.onclick = function() {
    //     view_game(game.id);
    //   }
    // });

    // add the content to the divs
    title.innerHTML = game.title;
    current_price.innerHTML = game.current_price;
    sale.innerHTML = game.noted_sale_type
    regular_price.innerHTML = game.regular_price;

    // add the columns to the row
    // div_row.append(image_container);
  
    // TODO: old divs, remove these
    // div_row.append(title);
    // div_row.append(current_price);
    // div_row.append(sale);
    // div_row.append(regular_price)
    // div_row.append(wishlist_indicator_container)

    const div_col_image = document.createElement('div');
    div_col_image.className = 'col-2';
    div_col_image.style.textAlign = 'left';
    const div_col_info = document.createElement('div');
    div_col_info.className = 'col-8';
    const div_col_actions = document.createElement('div');
    div_col_actions.className = 'col-2';
    div_col_actions.style.textAlign = 'right';

    const div_row_info_title = document.createElement('div');
    div_row_info_title.className = 'row';
    div_row_info_title.style.textAlign = 'left';
    
    const div_row_info_price = document.createElement('div');
    div_row_info_price.className = 'row';
    div_row_info_price.style.textAlign = 'left';

    wishlist_indicator.style.textAlign = 'right';

    linkable_elements = [div_col_image, div_col_info];
    linkable_elements.forEach(function(linkable_element) {
      linkable_element.onclick = function() {
        view_game(game.id);
      }
    });

    div_col_image.append(image_container);
    div_row_info_title.append(title);
    div_row_info_price.append(current_price);
    div_col_info.append(div_row_info_title);
    div_col_info.append(div_row_info_price);
    div_col_actions.append(wishlist_indicator_container);

    div_row.append(div_col_image);
    div_row.append(div_col_info);
    div_row.append(div_col_actions);

    console.log(div_row);

    // add the row to the list container
    gamelist_list.append(div_row);
  });
}


function search() {

  // update the heading
  const view_heading = document.getElementById('view-heading');
  view_heading.innerHTML = 'Search Results';
  view_heading.style.display = 'block';

  // get the search entry
  search_entry = document.querySelector('#search-entry').value;

  // clear the search field
  document.getElementById("search-entry").value = ""

  if (search_entry === '' || search_entry === undefined || search_entry === null) {
    load_gamelist('all-games');
  }
  else {
    // get the games with titles matching the search entry
    fetch(`/search/${search_entry}`)
    .then(response => response.json())
    .then(games => {
      if (games.length > 0) {
        view_games(games);
      }
      else {
        document.querySelector('#gamelist-view').style.display = 'none';
        document.getElementById('add-game').style.display = 'block';
      }
    });
  }

// Show the mailbox name
//   document.querySelector('#mailbox-header').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  
}


function load_gamelist(gamelist) {

  // update the hading
  const view_heading = document.getElementById('view-heading');

  if (gamelist == 'sale-games') {
    view_heading.innerHTML = 'Games on Sale';
  }
  else if (gamelist == 'wishlist-games') {
    view_heading.innerHTML = 'Wishlist';
  }
  else if (gamelist == 'all-games') {
    view_heading.innerHTML = 'All Games';
  }
  else {
    view_heading.innerHTML = 'Xbox Deals';
  }
  view_heading.style.display = 'block';

  // Show the mailbox and hide other views
  document.querySelector('#gamelist-view').style.display = 'block';

  // set the active nav button
  // and reset the rest
  reset_gamelist_nav_buttons();
  const active_button = document.getElementById(`${gamelist}-button`);
  active_button.className = 'btn btn-sm btn-primary gamelist-nav-btn';
  
  // document.querySelector('#compose-view').style.display = 'none';
  // document.querySelector('#email-view').style.display = 'none';

  // get the list of emails for the requested mailbox
  fetch(`/games/${gamelist}`)
  .then(response => response.json())
  .then(games => {
    if (games.error) {
      // load_gamelist('sale-games');
      view_heading.style.display = 'none';
      document.querySelector('#gamelist-view').style.display = 'none'; 
      document.getElementById('login').style.display = 'block';
    }
    else {
      console.log(games);
      view_games(games)
    }
    
  });

// Show the mailbox name
//   document.querySelector('#mailbox-header').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
}


function get_cookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}