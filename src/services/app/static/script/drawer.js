let playlists_list = document.getElementById('drawer_user_playlists');
let guilds_list    = document.getElementById('drawer_user_guilds');

fetch('/api/playlists/').then(response => response.json().then(data => {

    data.forEach(element => {
        element = `
        <li>
        <a href="/playlists/${element.uuid}">
        <img src="${element.thumbnail ? element.thumbnail : element.tracks[0].thumbnail}" onerror="https://mir-s3-cdn-cf.behance.net/project_modules/disp/a11a4893658133.5e98adbead405.gif'" width="20" height="20" class="rounded-lg aspect-square"/>
        ${element.title}
        </a>
        </li>
        `
        playlists_list.insertAdjacentHTML("beforeend", element);
    });
  }));

  fetch('/api/servers/').then(response => response.json().then(data => {
    console.log(data);

    data.same.forEach(element => {
        element = `
        <li>
        <a href="/me/servers/${element.id}">
        <img src="https://cdn.discordapp.com/icons/${element.id}/${element.icon ? element.icon : 'https://mir-s3-cdn-cf.behance.net/project_modules/disp/a11a4893658133.5e98adbead405.gif'}" onerror="" width="20" height="20" class="rounded-lg aspect-square"/>
        ${element.name}
        </a>
        </li>
        `
        guilds_list.insertAdjacentHTML("beforeend", element);
    });
  }));