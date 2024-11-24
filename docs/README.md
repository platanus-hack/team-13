# JSEXT API Documentation

## Endpoints

### POST `/text`

This endpoint accepts a JSON body with the following structure:

```json
{
    "label": "",
    "content": ""
}
```

- **label**: A string representing the label.
- **content**: A string representing the content.

### POST `/mouse`

This endpoint accepts a JSON body with the following structure:

```json
{
    "x": 0,
    "y": 0,
    "width": 0,
    "height": 0
}
```

- **x**: An integer representing the x-coordinate.
- **y**: An integer representing the y-coordinate.
- **width**: An integer representing the width.
- **height**: An integer representing the height.

### POST `/network`

This endpoint accepts a JSON body with the following structure:

```json
{
    "url": "",
    "type": ""
}
```

- **url**: A string representing the URL.
- **type**: A string representing the type of network resource. Possible values are `font`, `script`, or `img`.

### GET `/is_blocked`

This endpoint returns a JSON body with the following structure:

```json
{
    "blocked": true
}
```

- **blocked**: A boolean indicating whether the resource is blocked.