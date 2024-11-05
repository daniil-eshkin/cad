Используемые библиотеки:

```
numpy
sklearn
progressbar
meshlib
json
yaml
pyvista
collections
```

Формат модели:
```json
[
  {
    // Координаты вершин в формате x1, y1, z1, x2, y2, z2...
    "Coords": [0, 0, 0, 0, 0, 1, 0, 1, 0],
    // Треугольные грани с индексами из массива Coords
    "Indices": [0, 1, 2],
    "Category": "Floors"
  },
  ...
]
```

Формат входных данных:
```json
{
  "start": {
    "x": -5358,
    "y": 6208,
    "z": 3500
  },
  "end": {
    "x": 5441,
    "y": -991,
    "z": 3500
  }
}
```

Формат конфигурации:
```yaml
grid:                    # Характеристики сетки
  starting_point:        # Точка отсчета
    x: 0
    y: 0
    z: 0
  length: 100            # Ширина сетки
wire_width: 10           # Радиус провода
default_distance: 100    # Допустимое расстояние до объектов по умолчанию
distances:               # Допустимое расстояние до объектов конкретных категорий
  Floors: 0
  Ducts: 10
```

Запуск:
```bash
python3 main.py <conf> <model> <input>
```

Запуск примеров:
```bash
make sample{1-7}
```
или
```bash
make sample2_1
```

Запуск тестов:
```bash
make test
```