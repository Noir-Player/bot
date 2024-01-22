async function listen_tracks(query, list, uuid = null) {
  let api = new BasePlayerAPI();

  list.innerHTML = '';

  if (query != '') {
    
    let response = await api.suggestion(query);

    response = await response.json();

    console.log(response);

    response.forEach(element => {

      let trackstring;

      if (window.location.pathname.startsWith('/playlists/')) {
        trackstring = `<a onclick="apiplaylists.add_track(this, '${uuid}', '${element.url}'); document.getElementById('search_list').innerHTML = ''"><figure><img src="${element.thumbnail}" onerror="this.src='https://cataas.com/cat?type=square&amp;width=300'" width="20" height="20" class="rounded-lg aspect-square"></figure> ${element.title} - ${element.author}</li>`;
      } else if (window.location.pathname.startsWith('/me/queue')) {
        trackstring = `<a onclick="player.add_track('${element.url}'); document.getElementById('search_list').innerHTML = ''"><figure><img src="${element.thumbnail}" onerror="this.src='https://cataas.com/cat?type=square&amp;width=300'" width="20" height="20" class="rounded-lg aspect-square"></figure> ${element.title} - ${element.author}</li>`;
      } else if (window.location.pathname.startsWith('/me/stars')) {
        trackstring = `<a onclick="apistars.add_track(this, '${element.url}'); document.getElementById('search_list').innerHTML = ''"><figure><img src="${element.thumbnail}" onerror="this.src='https://cataas.com/cat?type=square&amp;width=300'" width="20" height="20" class="rounded-lg aspect-square"></figure> ${element.title} - ${element.author}</li>`;
      }
      let child = document.createElement('li');

      child.innerHTML = trackstring;

      list.appendChild(child);

    });
  };
};