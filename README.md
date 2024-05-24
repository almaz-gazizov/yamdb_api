## YaMDb API

### Описание:

>Проект YaMDb API хранит отзывы, созданные пользователями на различные произведения, а также предоставляет интерфейс для обмена данными в формате JSON.

>Позволяет выдавать информацию сторонним клиентам и обрабатывать полученные от них данные.

**Описание представлений:**

* `CategoriesViewSet` - Обрабатывает информацию о категориях произведений (заранее определены).*
* `GenresViewSet` - Обрабатывает информацию о жанрах произведений (заранее определены).*
* `TitleViewSet` - Обрабатывает информацию о произведениях, опубликованных на сайте.*
* `UsersViewSet` - Обрабатывает информацию о юзерах, кастомная модель.*
* `ReviewViewSet` - Обрабатывает информацию об отзывах, опубликованных пользователями к произведениям на сайте.*
* `CommentViewSet` - Обрабатывает информацию о комментариях, оставленных пользователями к отзывам.*

### Стек используемых технологий:

Windows, Linux, MacOS, SQLite, Python, Django, DRF, Git.

### Как развернуть проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/fantomv1/api_final_yatube.git
```

```
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

### Примеры:

>GET /titles/

```
{
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "id": 0,
      "name": "string",
      "year": 0,
      "rating": 0,
      "description": "string",
      "genre": [
        {
          "name": "string",
          "slug": "string"
        }
      ],
      "category": {
        "name": "string",
        "slug": "string"
      }
    }
  ]
}
```

>POST /titles/

Request:

```
{
  "name": "string",
  "year": 0,
  "description": "string",
  "genre": [
    "string"
  ],
  "category": "string"
}
```

Responce:

```
{
  "id": 0,
  "name": "string",
  "year": 0,
  "rating": 0,
  "description": "string",
  "genre": [
    {
      "name": "string",
      "slug": "string"
    }
  ],
  "category": {
    "name": "string",
    "slug": "string"
  }
}
```

>GET /titles/{title_id}/reviews/

```
{
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "id": 0,
      "text": "string",
      "author": "string",
      "score": 1,
      "pub_date": "2019-08-24T14:15:22Z"
    }
  ]
}
```

>POST /titles/{title_id}/reviews/

Request:

```
{
  "text": "string",
  "score": 1
}
```

Responce:

```
{
  "id": 0,
  "text": "string",
  "author": "string",
  "score": 1,
  "pub_date": "2019-08-24T14:15:22Z"
}
```

>Авторы: [fantomv1](https://github.com/fantomv1), [MiraCham](https://github.com/MiraCham), [almaz-gazizov](https://github.com/almaz-gazizov).
