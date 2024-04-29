page('/', homeHandler);

page('/playlists', playlistsHandler);
page('/playlists/:uuid', playlistHandler);

page('/me', meHandler);
page('/me/playlists', mePlaylistsHandler);
page('/me/stars', meStarsHandler);
page('/me/queue', meQueueHandler);
page('/me/servers', meServersHandler);
page('/me/servers/:id', meServerHandler);

page('/privacy', privacyHandler);
page('/terms', termsHandler);



// ---------------------------------------------------------------------------------------------------------
// Skeleton element

var skeleton = document.createElement('div');

skeleton.className = "hero min-h-screen bg-base-200";
skeleton.innerHTML = `
<div class="hero-content flex-col lg:flex-row">
    <div class="skeleton w-96 h-96"></div>
    <div>   
        <div class="skeleton h-6 w-96 my-2"></div>

        <div class="skeleton h-6 w-90 my-2"></div>
        <div class="skeleton h-12 w-32"></div>
    </div> 
</div>
`;

// ---------------------------------------------------------------------------------------------------------
// Some funcs

async function getPageContent(url) {
  try {
    let response = await fetch(url);
    if (response.ok) {
      let pageContent = await response.text();
      return pageContent;
    } else {
      throw new Error("Failed to fetch page content");
    };
  } catch (error) {
    console.error(error);
    return "";
  };
};

async function getMainContent(url) {
  replaceMainContent(skeleton.outerHTML);

  let pageContent = await getPageContent(url);

  let parser = new DOMParser();
  let doc = parser.parseFromString(pageContent, "text/html");
  let mainElement = doc.querySelector("main");

  if (mainElement) {
    return mainElement.innerHTML;
  } else {
    return await getMainContent('/404');
  };
};

function replaceMainContent(content) {
  let mainElement = document.querySelector('main');
  mainElement.innerHTML = content;

  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  });
};

// ---------------------------------------------------------------------------------------------------------

async function homeHandler() {
  replaceMainContent(await getMainContent('/'));
  loadMainScripts();
};

async function playlistsHandler() {
  replaceMainContent(await getMainContent('/playlists'));
  loadMainScripts(['/static/script/playlist_search.js']);
};

async function playlistHandler(ctx) {
  let uuid = ctx.params.uuid;
  replaceMainContent(await getMainContent(`/playlists/${uuid}`));
  loadMainScripts(['/static/script/dragndrop.js', '/static/script/add_menu.js']);
};

async function meHandler() {
  replaceMainContent(await getMainContent(`/me`));
  loadMainScripts();
};

async function mePlaylistsHandler() {
  replaceMainContent(await getMainContent(`/me/playlists`));
  loadMainScripts([]);
};

async function meStarsHandler() {
  replaceMainContent(await getMainContent(`/me/stars`));
  loadMainScripts(['/static/script/dragndrop.js', '/static/script/add_menu.js']);
};

async function meQueueHandler() {
  replaceMainContent(await getMainContent(`/me/queue`));
  loadMainScripts(['/static/script/add_menu.js']);
};

async function meServersHandler() {
  replaceMainContent(await getMainContent(`/me/servers`));
  loadMainScripts();
};

async function meServerHandler(ctx) {
  let id = ctx.params.id;
  replaceMainContent(await getMainContent(`/me/servers/${id}`));
  loadMainScripts();
};

async function privacyHandler() {
  replaceMainContent(await getMainContent(`/privacy`));
  loadMainScripts();
};

async function termsHandler() {
  replaceMainContent(await getMainContent(`/terms`));
  loadMainScripts();
};

async function notfound() {
  replaceMainContent(await getMainContent('/404'));
  loadMainScripts();
};

page();

// ---------------------------------------------------------------------------------------------------------

function loadMainScripts(urls = []) {
let tempscript  = document.querySelector('tempscript');

let scripts = tempscript.querySelectorAll('script');

// Удаляем старые скрипты из DOM
scripts.forEach(script => {
  script.remove();
});

// Создаем и добавляем новые скрипты в DOM
urls.forEach(script => {
  let newScript = document.createElement('script');
  newScript.src = script;
  tempscript.appendChild(newScript);
});


if (player && player.current) {
  try {
    let track = document.getElementById(`track_${player.current.url}`);
    track.classList.add('bg-base-300');
  } catch {};
};

};

// ---------------------------------------------------------------------------------------------------------

var playlistws;
var starsws;
var serverws;

var table;
var items;

var searchInput;
var cards;
var cardContainer;
var radioBtnLen;
var radioBtnAdd;

var filteredCards;
var Cards;        
var lenghtCards;

var uuid;

var apiplaylists;
var apistars;
var apiservers;