class BaseSocket {

    connect () {
        this.ws = new WebSocket(this.url);
    };

    constructor (url) {
        this.url = url;

        this.connect();

        this.ws.onopen = function () {
            console.log('Connected');
        };

        this.ws.onclose = function (event) {
            console.warn(`Socket closed: ${event.reason} [${event.code}]`);
            if (event.code != 1000) {
            console.log('Trying to reconnect...');
            socket = new BaseSocket(this.url);
            };
        };

        this.ws.onerror = function (event) {
            console.error(`Socket error: ${event}`);
        };
    };
    

    self () {
        return this.ws;
    };


    send (data) {
        this.ws.send(data);
    };


}