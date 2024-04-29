// BASE CLASSES

class BasePlaylistAPI {

    async get () {
    return await fetch(`/api/playlists/`);
    };

    async get_playlist(uuid) {
        return await fetch(`/api/playlists/${uuid}`);
    };

    async create (info) {
        return await fetch(`/api/playlists/create`, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(info)});
    };

    async edit (uuid, info) {
        return await fetch(`/api/playlists/${uuid}/edit`, {method: 'PATCH', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(info)});
    };

    async add_track (uuid, query) {
        return await fetch(`/api/playlists/${uuid}/add-track`, {method: 'PATCH', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({"query": query})});
    };

    async remove_track (uuid, url) {
        return await fetch(`/api/playlists/${uuid}/remove-track`, {method: 'PATCH', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({"url": url})});
    };

    async move_track (uuid, url, pos) {
        return await fetch(`/api/playlists/${uuid}/move-track`, {method: 'PATCH', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({"url": url, "pos": pos})});
    };

    async merge (uuid1, uuid2) {
        return await fetch(`/api/playlists/merge`, {method: 'PATCH', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({"uuid1": uuid1, "uuid2": uuid2})});
    };

    async add_to_library (uuid) {
        return await fetch(`/api/playlists/${uuid}/add-to-library`, {method: 'PATCH', headers: {'Content-Type': 'application/json'}});
    };

    async delete (uuid) {
        return await fetch(`/api/playlists/${uuid}/delete`, {method: 'DELETE', headers: {'Content-Type': 'application/json'}});
    };
};


class BaseStarsAPI {

    async get () {
        return await fetch(`/api/stars/`);
    };

    async add_track (query) {
        return await fetch(`/api/stars/add-track`, {method: 'PATCH', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({"query": query})});
    };

    async remove_track (url) {
        return await fetch(`/api/stars/remove-track`, {method: 'PATCH', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({"url": url})});
    };

    async move_track (url, pos) {
        return await fetch(`/api/stars/move-track`, {method: 'PATCH', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({"url": url, "pos": pos})});
    };
};


class BaseServersAPI {

    async get () {
        return await fetch(`/api/servers/`);
    };

    async get_guild (id) {
        return await fetch(`/api/servers/${id}`);
    };

    async edit (id, info) {
        return await fetch(`/api/servers/${id}/edit`, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(info)});
    };

    async create_webhook (id, name, channel) {
        return await fetch(`/api/servers/${id}/create-webhook`, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({"name": name, "channel": channel})});
    };
};


class BasePlayerAPI {
    async current () {
        return await fetch(`/api/player/current`);
    };

    async queue () {
        return await fetch(`/api/player/queue`);
    };

    async suggestion (query) {
        return await fetch(`/api/player/suggestion`, {method: 'PATCH', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({"query": query})});
    };
};

// ============================================================================================================================================================================================================================================
// ADDITIONAL AND RESPONSIVE CLASSES

class Playlists {

    constructor () {
        this.http = new BasePlaylistAPI();
    };

    // =============================================================================

    create (element) {
        let form = document.forms[0];

        let info = {
        "title": form.title.value,
        "public": form.public.checked,
        "thumbnail": form.thumbnail.value,
        "description": form.description.value
        };

        loading('Создать ', element);

        this.http.create(info);

        page(`/me/playlists`);
    };

    edit (uuid) {
        let form = document.forms[0];

        let info = {
        "uuid": uuid,
        "title": form.title.value,
        "public": form.public.checked,
        "thumbnail": form.thumbnail.value,
        "description": form.description.value
        };

        this.http.edit(uuid, info);

        document.getElementById('edit').close();

        page(`/playlists/${uuid}`);
    };

    delete (element, uuid) {
        if (element.textContent != 'Подтвердить ') {
            element.innerHTML = 'Подтвердить ';
        } else {
            loading('Подтвердить ', element);

            this.http.delete(uuid);

            page(`/me/playlists`);
          };
    };

    add_to_library (element, uuid) {
        loading('Добавление ', element);

        if (this.http.add_to_library(uuid)) {
            element.innerHTML = 'Добавлено';
        };
    };

    async add_track (element, uuid, query) {
        loading('Добавление ', element);

        let response = await this.http.add_track(uuid, query);

        response = await response.json();

        if (window.location.pathname.startsWith('/me/playlists/')) {
            let table = document.getElementById('tracks_table');

            table.insertAdjacentHTML('beforeend', render_track(response));
        };
    };

    remove_track (element, uuid, url) {
        loading('Удаление ', element);

        this.http.remove_track(uuid, url);

        if (window.location.pathname.startsWith('/me/playlists/')) {
            document.getElementById(`track_${url}`).remove();
        };
    };

    move_track (uuid, url, pos) {
        this.http.move_track(uuid, url, pos);
    };

    merge (element, uuid1, uuid2) {
        loading('Слияние ', element);

        if (this.http.merge(uuid1, uuid2)) {
            element.remove();
        };
    };
};


class Stars {

    constructor () {
        this.http = new BaseStarsAPI();
    };

    // =============================================================================

    async add_track (element, query) {
        loading('Добавление ', element);
        
        let response = await this.http.add_track(query);

        response = await response.json();

        if (typeof uuid !== 'undefined') {
            element.innerHTML = 'В звездочках';
            return;
        };
        
        if (window.location.pathname.startsWith('/me/stars')) {
            let table = document.getElementById('tracks_table');

            table.insertAdjacentHTML('beforeend', render_track(response));
        };

    };

    remove_track (element, url) {
        loading('Удаление ', element);

        this.http.remove_track(url);

        if (window.location.pathname.startsWith('/me/stars')) {
            document.getElementById(`track_${url}`).remove();
        };
    };

    move_track (url, pos) {
        this.http.move_track(url, pos);
    };
};


class Servers {
    constructor () {
        this.http = new BaseServersAPI();
    };

    // =============================================================================

    async create_webhook (element, id, name, channel) {
        let response = await this.http.create_webhook(id, name, channel);

        if (response.ok) {
            element.innerHTML = `
            <div class="mb-3">
                      <label class="label">
                        <span> Url Иконки Вебхука</span>
                      </label>
                      <input class="input input-bordered w-full" name="hook_icon" id="Hook_icon">
                      <label class="label">
                        <span class="label-text-alt">Кастомный бот для отображения вашей иконки</span>
                      </label>
                    </div>
                    <div class="mb-3">
                      <label class="label">
                        <span> Имя Вебхука</span>
                      </label>
                      <input class="input input-bordered w-full" name="hook_name" id="Hook_name" value="Noir Player">
                      <label class="label">
                        <span class="label-text-alt">Имя для заданного вебхука</span>
                      </label>
                    </div>
            `;
        } else {
            buble('Предупреждение', 'Не удалось создать вебхук. Пересмотрите id канала или права Noir');
        };
    };

    async edit (form, id) {

        let formData = new FormData(form);
        let data = {};

        data['radio'] = Boolean(formData.get('radio'));
        data['role'] = Number(formData.get('role'));
        data['color'] = formData.get('color');
        data['channel'] = Number(formData.get('channel'));
        data['volume_step'] = Number(formData.get('volume_step'));
        data['disable_eq'] = Boolean(formData.get('disable_eq'));
        data['webhook'] = {};
        data['webhook']['name'] = formData.get('hook_name');
        data['webhook']['icon'] = formData.get('hook_icon');

        // for (let [key, value] of formData.entries()) {
        //     if (!key.startsWith('hook')) {
        //     data[key] = value;
        //     } else {

        //     }
        // };

        console.log(data);

        let response = await this.http.edit(id, data);

        page(`/me/servers/${id}`);
    }
};
