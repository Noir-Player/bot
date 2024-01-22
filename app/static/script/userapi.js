function setDescription(description) {


  let resp = fetch(`/api/me/set-description`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      description: description
    })
  });
};


function setTheme(name) {

  document.documentElement.setAttribute('data-theme', name);

  document.cookie = `theme=${name}; path=/`;

  let resp = fetch(`/api/me/set-theme/${name}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json'
    }
  });
};


if (document.cookie.replace(/(?:(?:^|.*;\s*)theme\s*\=\s*([^;]*).*$)|^.*$/, "$1")) {
  document.documentElement.setAttribute('data-theme', document.cookie.replace(/(?:(?:^|.*;\s*)theme\s*\=\s*([^;]*).*$)|^.*$/, "$1"));

  document.cookie = `theme=${document.cookie.replace(/(?:(?:^|.*;\s*)theme\s*\=\s*([^;]*).*$)|^.*$/, "$1")}; path=/`;
} else {
  setTheme("sunset");
};



