// Panel
var MusicControlPanel = document.getElementById('music-control-panel');

// Spans
var PauseIcon = document.getElementById('player_play_icon');
var LoopIcon = document.getElementById('player_loop_icon');

// Track data
var Thumbnail = document.getElementById('track_thumbnail');
var Title = document.getElementById('track_title');
var Author = document.getElementById('track_author');

// Volume
var VolumeRange = document.getElementById('player_volume');

// Timeline
var Timeline = document.getElementById('track_timeline');
var TimelineLoop;

// End of time
var EndTime;


class Player {

    // Connet func
    connect () {
        console.log('Connecting...');
        this.ws = new WebSocket('wss://noirplayer.su/sockets/player');
    };

    fetch_current() {
        console.log('Connected to player');

            let xhr = new XMLHttpRequest();

            xhr.open('GET', '/api/player/current', false);

            xhr.send();

            if (xhr.status != 200) {
                return console.error(xhr.status + ': ' + xhr.statusText);
              };

            let data = JSON.parse(xhr.responseText);

            this.current = data;

            Title.innerHTML = data.title ? data.title : "Добавьте треки в очередь";
            Author.innerHTML = data.author ? data.author : "Наведите курсор здесь и кликните на значок очереди";
            Thumbnail.src = data.thumbnail ? data.thumbnail : "";

            Timeline.max = data.length ? (data.length / 1000) : Timeline.max;

            if (data) {
                Timeline.value = data.position ? (data.position / 1000) : Timeline.value;
                
                if (data.loop == null) {
                    LoopIcon.innerHTML = 'repeat';
                } else if (data.loop == 'queue') {
                    LoopIcon.innerHTML = 'repeat_on'; 
                } else if (data.loop == 'track') {
                    LoopIcon.innerHTML = 'repeat_one_on'; 
                };

            } else {
                Timeline.value = 0;
            };

            

            if (data.pause == false) {
                clearInterval(TimelineLoop);
                TimelineLoop = setInterval(() => {
                    Timeline.value ++;
                }, 1000);

                PauseIcon.innerHTML = 'pause';
            } else {
                clearInterval(TimelineLoop);
                PauseIcon.innerHTML = 'play_arrow';
            }; 

            VolumeRange.value = data.volume ? data.volume : 100;
    }

    // Конструктор
    constructor () {

        this.connect();

        this.ws.onopen = this.fetch_current;

        this.ws.onclose = function (event) {
            console.warn(`Socket closed: ${event.reason} [${event.code}]`);
            console.log('Trying to reconnect...');
            setTimeout(() => {player = new Player();}, 1000);
        };

        this.ws.onerror = function (event) {
            console.error(`Socket error: ${event}`);
        };

        // OnMessage event
        this.ws.onmessage = (event) => {
            let data = JSON.parse(event.data);
            console.log(data);

            if (data.code == 404) {
                return buble("Нет подключения", "подключитесь к войсу, доступному для подключения Noir");
            };

            if (data.action == 'destroy' || data.action == 'disconnect') {
                Title.innerHTML = 'Отключен';
                Thumbnail.src = "";
                Author.innerHTML = 'Noir';
                Timeline.value = 0;

                clearInterval(TimelineLoop);  clearTimeout(EndTime);

                if (window.location.pathname == '/me/queue') {
                    let table = document.getElementById('tracks_table');
                    table.innerHTML = '';
                };

            } else if (data.action == 'connect') {
                this.fetch_current();

            } else if (data.action == 'play') {
                clearInterval(TimelineLoop); clearTimeout(EndTime);

                this.current = data.value;

                Title.innerHTML = data.value ? data.value.title : "Добавьте треки в очередь";
                Author.innerHTML = data.value ? data.value.author : "Наведите курсор здесь и кликните на значок очереди";
                Thumbnail.src = data.value ? data.value.thumbnail : "";

                Timeline.max = data.value ? (data.value.length / 1000) : Timeline.max;

                
                Timeline.value = 0;

                TimelineLoop = setInterval(() => {
                    Timeline.value ++;
                }, 1000);

                PauseIcon.innerHTML = 'pause';
            
                buble('Сейчас играет', `${data.value.title}`, data.value.thumbnail);
        
                document.querySelectorAll('[id^="track_"]').forEach(element => {
                    element.classList.remove('bg-base-300');
                });

                let track = document.getElementById(`track_${data.value.url}`);
                
                track.classList.add('bg-base-300');

                EndTime = setTimeout(() => {
                    document.querySelectorAll('[id^="track_"]').forEach(element => {
                        element.classList.remove('bg-base-300');
                    });
                    this.current = null;
                }, data.value.length);

            } else if (data.action == 'pause') {
                clearInterval(TimelineLoop); clearTimeout(EndTime);

                PauseIcon.innerHTML = 'play_arrow';

                if (data.value == false) {
                    Timeline.value = (data.position / 1000);
                    TimelineLoop = setInterval(() => {
                        Timeline.value ++;
                    }, 1000);

                    PauseIcon.innerHTML = 'pause';

                    EndTime = setTimeout(() => {
                        document.querySelectorAll('[id^="track_"]').forEach(element => {
                            element.classList.remove('bg-base-300');
                        });
                        this.current = null;
                    }, this.current.length - data.position);
                };
                

            } else if (data.action == 'volume') {
                VolumeRange.value = data.value;


            } else if (data.action == 'seek') {
                clearTimeout(EndTime);

                Timeline.value = data.value / 1000;

                EndTime = setTimeout(() => {
                    document.querySelectorAll('[id^="track_"]').forEach(element => {
                        element.classList.remove('bg-base-300');
                    });
                    this.current = null;
                }, this.current.length - data.value);


            } else if (data.action == 'loop') {
                if (data.value == null) {
                    LoopIcon.innerHTML = 'repeat';
                } else if (data.value == 'queue') {
                    LoopIcon.innerHTML = 'repeat_on'; 
                } else if (data.value == 'track') {
                    LoopIcon.innerHTML = 'repeat_one_on'; 
                };
            } else if (data.action == 'put') {
                buble('Добавлено', `${data.value.title}`, data.value.thumbnail);

                if (window.location.pathname == '/me/queue') {
                    let table = document.getElementById('tracks_table');
                    table.insertAdjacentHTML('beforeend', render_track_queue(data.value, table.children.length - 1));
                };

            } else if (data.action == 'put_list') {
                buble('Добавлено', `Добавлен список из ${data.value} треков`);

                if (window.location.pathname == '/me/queue') {
                    page('/me/queue');
                };

            } else if (data.action == 'shuffle') {
                buble('Перемешано', 'Очередь перемешана. Текущий трек в начале списка');

                if (window.location.pathname == '/me/queue') {
                    page('/me/queue');
                };

            } else if (data.action == 'remove') {
                buble('Удалено', `Трек на позиции ${data.value + 1} был удален`);

                

                if (window.location.pathname == '/me/queue') {
                    let table = document.getElementById('tracks_table');
                    table.children.item(data.value).remove();
                };
            } else if (data.action == 'clear') {
                buble('Удалено', `Очередь пуста`);

                if (window.location.pathname == '/me/queue') {
                    let table = document.getElementById('tracks_table');
                    table.innerHTML = '';
                };
            };
        };
    };
    
    // Вспомогательная функция
    _send (data) {
        this.ws.send(data);
    };

    // MAIN
    // additional funcs

    search (query) {
        this.ws.send(JSON.stringify({"type": "search", "query": query}));
    };

    recs () {
        this.ws.send(JSON.stringify({"action": "get_recommendations"}));
    };

    add_playlist (uuid, element) {
        loading("Отправлено ", element);
        element.removeAttribute('onclick');
        this.ws.send(JSON.stringify({"action": "play_playlist", "uuid": uuid}));

    };

    add_track (url) {
        try {
        loading("Отправлено ", document.getElementById(`track_add_btn_${url}`));
        document.getElementById(`track_add_btn_${url}`).removeAttribute('onclick');
        } catch {};
        this.ws.send(JSON.stringify({"action": "play", "query": url}));
    };

    // queue

    skip (count = 0) {
        this.ws.send(JSON.stringify({"action": "skip"}));
    };

    prev (count = 0) {
        this.ws.send(JSON.stringify({"action": "prev"}));
    };

    jump (url) {

        let i = 0;

        document.getElementById('tracks_table').querySelectorAll('.track').forEach(el => {
            if (el.id.endsWith(url)) {
                return this.ws.send(JSON.stringify({"action": "jump", "pos": i}));
            };
            i++;
        });

    };

    pause () {
        this.ws.send(JSON.stringify({"action": "pause"}));
    };

    loop () {
        this.ws.send(JSON.stringify({"action": "loop"}));
    };

    remove (url) {

        let i = 0;

        document.getElementById('tracks_table').querySelectorAll('.track').forEach(el => {
            if (el.id.endsWith(url)) {
                return this.ws.send(JSON.stringify({"action": "remove", "pos": i}));
            };
            i++;
        });

    }

    shuffle () {
        this.ws.send(JSON.stringify({"action": "shuffle"}));
    };

    volume (value = 100) {
        this.ws.send(JSON.stringify({"action": "set_volume", "kwargs": {"volume": value}}));
    };

    like () {
        this.ws.send(JSON.stringify({"action": "star"}));
        document.getElementById('player_remove_tip').setAttribute('data-tip', 'Добавлено!');
        setTimeout(() => {document.getElementById('player_remove_tip').setAttribute('data-tip', 'В избранное');}, 1500);
    };

    clear () {
        this.ws.send(JSON.stringify({"action": "clear"}));
        if (window.location.pathname == '/me/queue') {
            let table = document.getElementById('tracks_table');
            table.innerHTML = '';
        };
    };
};