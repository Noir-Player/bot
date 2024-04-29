searchInput   = document.querySelector('#searchInput');
cards         = document.querySelectorAll('#card');
cardContainer = document.querySelector('.grid-cols-2');
radioBtnLen   = document.getElementById('len');
radioBtnAdd   = document.getElementById('add');

  // Search
  searchInput.addEventListener('input', function() {
    let searchTerm = searchInput.value.toLowerCase();
    let filteredCards = [];

    cards.forEach(function(card) {
      if (card.classList.contains("col-span-full")) {
        return
      };

      let cardTitle = card.querySelector('.card-title').textContent.toLowerCase();
      
      if (cardTitle.includes(searchTerm)) {
        filteredCards.push(card.outerHTML);
      }
    });
  
    cardContainer.innerHTML = filteredCards.join('');
  });

  // Sort
  filteredCards = [];
  Cards         = [];

  lenghtCards   = [];


    cards.forEach(function(card) {
      filteredCards.push(card.outerHTML);
      Cards.push(card.outerHTML);
      
      if (card.classList.contains("col-span-full")) {
        return
      };
      lenghtCards.push(card.querySelector('#length').innerHTML);
    });

    filteredCards.sort((a, b) => {
      let trackCountA = parseInt(lenghtCards[filteredCards.indexOf(a)]);
      let trackCountB = parseInt(lenghtCards[filteredCards.indexOf(b)]);
      return trackCountB - trackCountA;
    });

  radioBtnAdd.addEventListener('click', function() {
    cardContainer.innerHTML = Cards.join('');
  });

  radioBtnLen.addEventListener('click', function() {
    cardContainer.innerHTML = filteredCards.join('');
  });