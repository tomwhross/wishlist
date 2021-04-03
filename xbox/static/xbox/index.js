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


function display_view(view) {
  // change the view displayed

  document.getElementById('login').style.display = 'none';
  document.getElementById("add-game").style.display = 'none';
  document.getElementById('message').style.display = 'none';
  document.getElementById('gamelist-view').style.display = 'none';
  document.getElementById('game-view').style.display = 'none';

  switch(view) {
    case 'login':
      document.getElementById('login').style.display = 'block';
      break;
    case 'add-game':
      document.getElementById('add-game').style.display = 'block';
      break;
    case 'message':
      document.getElementById('message').style.display = 'block';
      break;
    case 'gamelist-view':
      document.getElementById('gamelist-view').style.display = 'block';
      break;
    case 'game-view':
      document.getElementById('game-view').style.display = 'block';
      break;
  } 
}


function reset_gamelist_nav_buttons() {
  // reset the nav buttons between views so the current one can be highlighted
  document.getElementById('message').style.display = 'none';
  // reset all the nav buttons, make them unfilled
  const nav_buttons = document.querySelectorAll('.gamelist-nav-btn');
  
  nav_buttons.forEach(nav_button => {
    nav_button.className = 'btn btn-sm btn-outline-primary gamelist-nav-btn';
  });
}


function view_game(game_id) {
  // view for a individual game

  reset_gamelist_nav_buttons();
  // view_heading = document.getElementById('view-heading');
  
  // show the game and hide the other views
  display_view('game-view');

  // locate the game view and blank it out
  const game_view = document.querySelector('#game-view'); 
  game_view.innerHTML = '';

  // fetch a game from the server
  fetch(`/game/${game_id}`)
  .then(response => response.json())
  .then(game => {

    const game_view_card = document.createElement('div');
    game_view_card.className = 'card d-flex flex-column game-view-card';

    const game_view_card_row = document.createElement('div');
    game_view_card_row.className = 'row g-0';

    const game_view_card_image_container = document.createElement('div');
    game_view_card_image_container.className = 'col-3 game-view-card-image-container';

    const game_view_card_image = document.createElement('img');
    game_view_card_image.className = 'card-lg-img-cover img-responsive';
    game_view_card_image.src = game.image;

    const game_view_card_body_container = document.createElement('div');
    game_view_card_body_container.className = 'col';

    const game_view_card_body = document.createElement('div');
    game_view_card_body.className = 'card-body';

    const game_card_title = generate_game_card_title(game);
    const game_card_discount = generate_game_card_discount(game);
    const prices = generate_game_card_prices(game);
    const badges = generate_game_card_badges(game);
    const days_left = generate_game_card_days_left(game);
    const wishlist_cta = generate_game_card_wishlist_cta(game, false);

    game_view_card_body.append(game_card_title);
    game_view_card_body.append(game_card_discount);
    game_view_card_body.append(prices);
    game_view_card_body.append(badges);
    game_view_card_body.append(days_left);
    game_view_card_body.append(wishlist_cta);

    game_view_card_body_container.append(game_view_card_body);

    game_view_card_image_container.append(game_view_card_image);

    game_view_card_row.append(game_view_card_image_container);
    game_view_card_row.append(game_view_card_body_container);

    game_view_card.append(game_view_card_row);

    game_view.append(game_view_card);



    // view_heading.innerHTML = game.title;
    // const image_container = document.createElement('div');
    // const image = document.createElement('img');
    // const current_price = document.createElement('div');
    // const regular_price = document.createElement('div');
    // const store_link_container = document.createElement('div');
    // const store_link = document.createElement('a');

    // image.src = game.image;
    // image.className = 'img-fluid rounded';
    // image.alt = game.title;
    
    // current_price.innerHTML = game.current_price;
    // regular_price.innerHTML = game.regular_price;
    // store_link.href = game.url;
    // store_link.innerHTML = `Store page for ${game.title}`

    // image_container.append(image);
    // store_link_container.append(store_link);

    // game_view.append(image_container);
    // game_view.append(current_price);
    // game_view.append(regular_price);
    // game_view.append(store_link_container);

  });
}


function display_message(gamelist) {
  message = document.getElementById('message');

  if (gamelist === 'wishlist-games') {
    message.innerHTML = 'Add some games to your wishlist!'
  }
  else if (gamelist === 'sale-games') {
    message.innerHTML = 'There are no games currently on sale!'
  }
  else {
    message.innerHTML = 'Something went wrong, try reloading the page'
  }

  message.style.display = 'block';
}


function generate_game_card_image(game) {
  // generate the game card image for the cover

  const card_cover_image = document.createElement('img');
  card_cover_image.className = 'card-img-top card-img-cover';
  card_cover_image.src = game.image;
  card_cover_image.style.filter = 'blur(5px)';
  card_cover_image.style.margin = '-5px 0px 0px';
  card_cover_image.style.overflow = 'hidden';
  card_cover_image.alt = `Cover image for ${game.title}`;

  return card_cover_image;
}


function generate_game_card_title(game) {
  // generate the title element for the game card

  const card_title = document.createElement('h6');
  card_title.className = 'card-title';
  card_title.style.minHeight = '73px';
  card_title.innerHTML = game.title;

  return card_title;
}


function generate_game_card_discount(game) {
  // generate a discount badge if a game is on sale

  const discount_badge_parapgrah = document.createElement('p');
  discount_badge_parapgrah.style.minHeight = '21px';
  if (game.noted_sale && game.discount) {
    const discount_badge = document.createElement('span');
    discount_badge.className = 'badge bg-danger spaced-badge';
    discount_badge.innerHTML = `${game.discount}% OFF`;


    discount_badge_parapgrah.append(discount_badge);
  }

  return discount_badge_parapgrah;
}


function generate_game_card_prices(game) {

  card_price_data = document.createElement('p');
  card_price_data.className = 'card-text';

  if (game.noted_sale && game.regular_price) {
    const regular_price = document.createElement('span');
    regular_price.className = 'text-muted card-space sale-regular-price';
    regular_price.innerHTML = `$${game.regular_price}`;

    const sale_price = document.createElement('span');
    sale_price.className = 'card-space sale-price';
    sale_price.innerHTML = `$${game.current_price}`;

    card_price_data.append(regular_price);
    card_price_data.append(sale_price);
  }
  else {
    const current_price = document.createElement('span');
    current_price.className = 'card-space sale-price';
    current_price.innerHTML = `$${game.current_price}`;

    card_price_data.append(current_price);
  }

  return card_price_data;
}


function generate_game_card_badges(game) {
  // generate Xbox Live Gold and Game Pass badges

  const badges_paragraph = document.createElement('p');
  badges_paragraph.style.minHeight = '21px';
  if (game.noted_sale_type === 'Xbox Gold Sale' || game.on_gamepass) {
    
    badges_paragraph.className = 'card-text';

    if (game.noted_sale_type === 'Xbox Gold Sale') {
      const gold_sale_badge = document.createElement('span');
      gold_sale_badge.className = 'badge bg-warning text-dark card-badge-space';
      gold_sale_badge.innerHTML = 'GOLD SALE';
      gold_sale_badge.style.marginRight = '10px';
      badges_paragraph.append(gold_sale_badge);
    }

    if (game.on_gamepass) {
      const gamepass_badge = document.createElement('span');
      gamepass_badge.className = 'badge bg-success card-badge-space';
      gamepass_badge.innerHTML = 'GAME PASS';
      badges_paragraph.append(gamepass_badge);
    }
  }

  return badges_paragraph;
}


function generate_game_card_days_left(game) {
  // generate warning badge for number of days game is left on sale

  const days_sale_left_paragraph = document.createElement('p');
  days_sale_left_paragraph.style.minHeight = '22px';

  if (game.days_left_on_sale) {

    days_sale_left_paragraph.className = 'mt-auto align-bottom';
    const days_sale_left_span = document.createElement('span');
    days_sale_left_span.className = 'card-text';
    const days_sale_left_small = document.createElement('small');
    days_sale_left_small.className = 'text-muted';
    days_sale_left_small.innerHTML = `<b>${game.days_left_on_sale}</b> days left on sale`;

    days_sale_left_span.append(days_sale_left_small);
    days_sale_left_paragraph.append(days_sale_left_span);
  }

  return days_sale_left_paragraph;
}


function generate_game_card_wishlist_cta(game, list = true) {
  const wishlist_cta_div = document.createElement('div');
  wishlist_cta_div.className = 'd-grid gap-2 col-12 mx-auto mt-auto align-bottom';

  const wishlist_cta_button = document.createElement('button');
  wishlist_cta_button.className = 'btn-sm btn-primary';

  if (!list) {
    wishlist_cta_button.classList.add('game-view-card-cta');
  }

  wishlist_cta_button.style.fontSize = '13px';
  
  const wishlist_cta_text_span = document.createElement('span');
  const wishlist_cta_icon_span = document.createElement('span');
  const wishlist_cta_icon = document.createElement('i');
  wishlist_cta_icon.className = 'fas fa-star';
  wishlist_cta_icon.style.marginRight = '8px';
  
  if (game.is_wishlist_user) {
    wishlist_cta_icon.style.color = 'orange';
    wishlist_cta_text_span.innerHTML = 'Remove from wishlist';
  }
  else {
    wishlist_cta_icon.style.color = 'white';
    wishlist_cta_text_span.innerHTML = 'Add to wishlist';
  }
  wishlist_cta_div.onclick = function() {
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
        // assuming that an error returned here means that
        // the user is not logged in, so hide everything and show the login view
        view_heading.style.display = 'none';
        document.querySelector('#gamelist-view').style.display = 'none'; 
        document.getElementById('login').style.display = 'block';
      }
      else {
        if (game.is_wishlist_user === true) {
          wishlist_cta_icon.style.color = 'orange';
          wishlist_cta_text_span.innerHTML = 'Remove from wishlist';
        }
        else {
          wishlist_cta_icon.style.color = 'white';
          wishlist_cta_text_span.innerHTML = 'Add to wishlist';
        }
      }
    });
  }

  wishlist_cta_icon_span.append(wishlist_cta_icon);
  wishlist_cta_button.append(wishlist_cta_icon_span);
  wishlist_cta_button.append(wishlist_cta_text_span)
  wishlist_cta_div.append(wishlist_cta_button);

  return wishlist_cta_div;
}

function generate_game_card(game) {
  const col = document.createElement('div');
  col.className = 'col';

  const card = document.createElement('div');
  card.className = 'card h-100 d-flex flex-column';
  card.style.overflow = 'hidden';

  const card_cover_div = document.createElement('div');
  card_cover_div.style.overflow = 'hidden';
  const card_cover_image = generate_game_card_image(game);

  const card_body = document.createElement('div');
  card_body.className = 'card-body px-2 d-flex flex-column';

  const card_title = generate_game_card_title(game);
  card_body.append(card_title);

  const card_line = document.createElement('hr');
  card_line.className = 'mx-0 text-muted';
  card_body.append(card_line);

  const discount_badge_parapgrah = generate_game_card_discount(game);
  card_body.append(discount_badge_parapgrah);

  const card_price_data = generate_game_card_prices(game);
  card_body.append(card_price_data);

  const badges_paragraph = generate_game_card_badges(game);
  card_body.append(badges_paragraph);

  const days_sale_left_paragraph = generate_game_card_days_left(game);
  card_body.append(days_sale_left_paragraph);

  const wishlist_cta_div = generate_game_card_wishlist_cta(game);
  card_body.append(wishlist_cta_div);

  linkable_elements = [
    card_cover_image,
    card_title,
    card_line,
    discount_badge_parapgrah,
    card_price_data,
    badges_paragraph,
    days_sale_left_paragraph,
  ];

  linkable_elements.forEach(function(linkable_element) {
    linkable_element.onclick = function() {
      view_game(game.id);
    }
  });

  card.onmouseover = function() {
    card_title.style.color = '#007bff';
    card_cover_image.style.filter = 'blur(0px)';
    card.style.boxShadow = '0px 5px 13px 5px rgba(0,0,0,0.75)';
    card.style.cursor = 'pointer';
  }
  card.onmouseout = function() {
    card_title.style.color = '#000000';
    card_cover_image.style.filter = 'blur(5px)';
    card.style.boxShadow = 'none';
    card.style.cursor = 'default';
  }
  
  card_cover_div.append(card_cover_image);
  card.append(card_cover_div);
  card.append(card_body);

  col.append(card);

  return col;
}

function view_games(games, gamelist) {
  // reset the page
  display_view('gamelist-view');

  // get the element that will contain everything
  gamelist_view = document.getElementById('gamelist-view');
  gamelist_view.innerHTML = '';

  // create the rows-cols container
  rows_cols = document.createElement('div');
  rows_cols.className = 'row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 row-cols-xl-5 row-cols-xxl-6 g-4';

  // if there are no games to display show a message
  if (games.length === 0) {
    display_message(gamelist);
  }
  else {
    document.getElementById('message').style.display = 'none';
  }

  // generate a col-card element and populate with game data for each game
  games.forEach(function(game) {
    col = generate_game_card(game);
    rows_cols.append(col);
  });

  // append the rows-cols to the main container div
  gamelist_view.append(rows_cols);
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

  // if there is no search entry on submit, show all games
  if (search_entry === '' || search_entry === undefined || search_entry === null) {
    load_gamelist('all-games');
  }
  else {
    // get the games with titles matching the search entry
    fetch(`/search/${search_entry}`)
    .then(response => 
      response.json())
    .then(games => {
      if (games.length > 0) {
        view_games(games);
      }
      else {
        const message = document.getElementById('message');
        message.innerHTML = 'There are no games matching that title, try a new search or add a URL from the Xbox Store (Canada)';
        document.querySelector('#gamelist-view').style.display = 'none';
        document.getElementById('add-game').style.display = 'block';
        message.style.display = 'block';
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
      display_view('login'); 
    }
    else {
      view_games(games, gamelist)
    }
    
  });

// Show the mailbox name
//   document.querySelector('#mailbox-header').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
}


function get_cookie(name) {
  let cookie_value = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookie_value = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookie_value;
}