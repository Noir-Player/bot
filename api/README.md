### Main

#GET /status `получить статус (сервера, пинг)`

#GET  /login?redirect `зарегистрировать пользователя в discord [redirect="/profile"]`

#GET  /logout?redirect `выйти [redirect="/"]`

### Discovery `/discovery`

#GET /?filter

```json
Получить страницу с треками, плейлистами, миксами
{
"filter": "energy"
}
{
"last_tracks": ...,
"related": {
	"track_name": [...],
	"track_name": [...]
	}
"playlists": ...,
"mixes": ...,
}
```

#GET /search?query?type

```json
Получить треки, плейлисты по поиску
{
"query": "rickroll",
"type": "spotify",
}
{
"tracks": [...],
"playlists": ...,
"mixes": ...,
}
```

### Stars `/stars`

#GET /?page?count?filters

```json
Получить треки, плейлисты по поиску
{
"page": 1,
"count": 50,
"filter": ["blue", "red", "custom tag"]
}
{
"tracks": [...],
"meta": {"page": 1, "count": 50, "found": 483, "filter": ["blue", "red", "custom tag"]}
}
```

#PATH /move?pos1?pos2

```json
Переместить треки
{
"pos1": 10,
"pos2": 2
}
{
204 no content
}
```

#GET /{track_index}

```json
Получить трек по индексу
{
no content
}
{
"track": ...
}
```

#PUT /{track_index}?query?search_type

```json
Вставить трек или плейлист по поиску и индексу track_index
{
"query": "rickroll",
"type": "spotify",
}
{
"tracks": [...],
"meta": {"index": 20}
}
```

#PATH  /{track_index}/tags?tag

```json
Добавить тег 
{
"name": "red",
"color": 123344
}
// Добавление происходит в профиль
{
"track": ...
}
```

#DELETE   /{track_index}/tags?tag

```json
Удалить тег 
{
"name": "red"
}
{
"track": ...
}
```

#DELETE /{track_index}

```json
Удалить трек по индексу
{
no content
}
{
204 no content
}
```

### Playlists `/playlists`

#GET /?page?count

```json
Получить плейлисты юзера
{
"page": 1,
"count": 50
}
{
"playlists": ...,
"meta": {"page": 1, "count": 10, "found": 22}
}
```

#POST /?playlist

```json
Создать плейлист
{
"title": "Playlist name", // Имя плейлиста
"thumbnail": "urltoimg", // Обложка
"description": "# Плейлист для учебы и отдыха\n`by persifox`", // Описание
"public": true // Публичный или нет
}
{
"playlist": ...
}
```

#PUT /?playlist_uuid

```json
Добавить плейлист
{
"uuid": uuid
}
{
204 no content
}
```

#PATH /merge?sender?consumer

```json
Наследовать треки из плейлиста в свой
{
"sender": uuid,
"consumer": uuid
}
{
204 no content
}
```

#GET /{playlist_name}?page?count

```json
Получить плейлист
{
"page": 2, // Если 1, то передается описание и 50 треков. Если больше, передаются только треки
"count": 50
}
{
"title": "Playlist name", // Имя плейлиста
"thumbnail": "urltoimg", // Обложка
"description": "# Плейлист для учебы и отдыха\n`by persifox`", // Описание
"public": true, // Публичный или нет

"tracks": [...],

"meta": {"page": 2, "count": 50, "found": 437}
}
```

#PATH /{playlist_name}?obj

```json
Изменить плейлист
{
"title": "Playlist name", // Имя плейлиста
"thumbnail": "urltoimg", // Обложка
"description": "# Плейлист для учебы и отдыха\n`by persifox`", // Описание
"public": true // Публичный или нет
}
{
"title": "Playlist name", // Имя плейлиста
"thumbnail": "urltoimg", // Обложка
"description": "# Плейлист для учебы и отдыха\n`by persifox`", // Описание
"public": true // Публичный или нет
}
```

#DELETE /{playlist_name}

```json
Удалить плейлист
{
no content
}
{
204 no content
}
```

#PATH /{playlist_name}/move?pos1?pos2

```json
Переместить трек
{
"pos1": 23,
"pos2": 0
}
{
204 no content
}
```

#GET /{playlist_name}/{track_index}

```json
Получить трек
{
no content
}
{
"track": ...
}
```

#PUT /{playlist_name}/{track_index}?query?search_type

```json
Вставить трек или плейлист по поиску и индексу track_index
{
"query": "rickroll",
"type": "spotify",
}
{
"tracks": [...],
"meta": {"index": 20}
}
```

#DELETE /{playlist_name}/{track_index}

```json
Удалить трек
{
no content
}
{
204 no content
}
```

### Guilds `/guilds`

#GET /?page?count

```json
Получить список серверов
{
no content
}
{
"guilds": [...],
"meta": {"page": 2, "count": 10}
}
```

#GET /{guild_id}

```json
Получить сервер
{
no content
}
{
"guild": ...
}
```

#PATH /{guild_id}?obj?webhook

```json
Изменить конфиг сервера
{
"guild": ...,
"webhook": {
	"name": "Noir Player",
	"icon": "https://image.com/cat.png"
	}
}
{
"guild": ...
}
```

#DELETE /{guild_id}

```json
Удалить (Выйти) сервер
{
no content
}
{
204 no content
}
```
### Users `/users`

#GET /{user_id}

```json
Получить объект юзера (пока что только себя)
{
no content
}
{
"user": ...
}
```

#PATH /{user_id}?obj

```json
Изменить объект юзера (пока что только себя)
{
"user": {
	"description": "wasd",
	"theme": "light",
	"decoration": "img hash"
	}
}
{
"user": ...
}
```

#DELETE /{user_id}

```json
Удалить все свои данные
{
no content
}
{
204 no content
}
```

---
Не используется

#PUT /{user_id}/tags/?obj

```json
Создать тег
{
"tag": {
		"color": 123434, // Цвет тега
		"name": "red" // Имя тега
	}
}
{
"tag": {
		"color": 123434, // Цвет тега
		"name": "red", // Имя тега
		"id": uuid // UUID тега
	}
}
```

#PATH  /{user_id}/tags/{uuid}?obj

```json
Изменить тег
{
"tag": {
		"color": 132323, // Цвет тега
		"name": "blue" // Имя тега
	}
}
{
"tag": {
		"color": 132323, // Цвет тега
		"name": "blue", // Имя тега
		"id": uuid // UUID тега
	}
}
```

#DELETE /{user_id}/tags/{uuid}

```json
Удалить тег
{
no content
}
{
204 no content
}
```

---
### Players `/player`

#GET /?page?count?filter 

#DELETE /