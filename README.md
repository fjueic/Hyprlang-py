For reference [my configration](https://github.com/fjueic/.dotfiles/tree/main/.config/hypr)

# Usage
Defining Configurations

To define configurations, use the provided classes. Here's a brief overview:

-   RGBA: Represents a color in RGBA format.
-   Gradient: Represents a gradient between two colors.
-   Vec2: Represents a 2-dimensional vector.
-   Parameters: Represents parameters for handlers.
-   Handler: Represents a handler in Hyprlang.
-   Category: Represents a category in Hyprlang.
-   Hyprlang_config: Manages a Hyprlang configuration.
-   Hyprlang: Main class to manage and watch configuration files.

---

## **Color and Gradient Examples**

### Creating an RGBA Color
```python
color0 = RGBA(r=255, g=0, b=0, a=0.5) # a is optional
# Represents an RGBA color with red (255), green (0), blue (0), and alpha (0.5)
# Output: rgba(255, 0, 0, 0.5) 
```

### Creating an RGBA Color from Hex
```python
color1 = RGBA.from_hex("#ffffff")
# Converts hex color #ffffff to RGBA format
# Output: rgba(255, 255, 255)
```

### Creating a Gradient
```python
gradient = Gradient(s=color0, e=color1, angle=90)
# Defines a gradient from color0 to color1 at a 90-degree angle
# Output: rgba(255, 0, 0, 0.5) rgba(255, 255, 255) 90deg
```

### Creating a 2D Vector
```python
vec = Vec2(x=10, y=20)
# Represents a 2-dimensional vector with x=10 and y=20
# Output: 10 20
```

---

## **Handler and Category Examples**

### Creating Parameters
```python
params = Parameters(10, 20, "Hello")
# Represents parameters with values 10, 20, and "Hello"
# Output: 10, 20, Hello
```

### Creating a Handler
```python
handler = Handler("key", params)
# Creates a handler with keyword "key" and parameters (10, 20, "Hello")
# Output: key = 10, 20, Hello
```

### Creating a Category
```python
category = Category("category", handler)
# Defines a category named "category" with the handler created above
# Output:
# category {
#     key = 10, 20, Hello
# }
```

---

## **Hyprlang Configuration Examples**

### Creating a Hyprlang Config and Adding Entries
```python
conf = Hyprlang_config(__file__)  # Initializes a Hyprlang configuration with the current file name
# only one instance of Hyprlang_config named `config` should be created per file if you want to import it and use watch
# otherwise you can create multiple instances of Hyprlang_config

conf.add_side_effect(lambda: print("Hello"))
# Adds a side effect that prints "Hello" when the file is modified

conf.add_config_entries(
    key1="value1",
    key2=("value2", 10, 20),
    key3={"key4": "value4", "key5": ("value5", 10, 20)},
    key6=[{"key7": "value7"}, ("key8", 10, 20), "value9"]
)
# creating parameters, handlers and categories for each thing is too much work
# so you can use add_config_entries to add them easily, some examples at the end
```

### Writing and Watching the Config File
```python
config = Hyprlang("path_to_output.conf", __file__)
# one per file stored in a variable named `config`

config.add(conf)  # Adds the created conf to the Hyprlang instance
config.write()    # Writes the configuration to the specified output file

config.watch()    # Starts watching the config file for changes
```

### Example Hyprlang Config File Usage
```python
from Hyprlang import *

conf = Hyprlang_config(__file__)
wallpaper = "/home/minoru/Desktop/wallpapers/dragonball/340761.jpg"

def restart_hyprpaper():
    from os import system
    system("killall hyprpaper")
    system("hyprpaper >/dev/null & disown")

def pre_process(wall):
    from os import system
    system(f'magick "{wall}" -resize 1920x1080 -background black -gravity center -extent 1920x1080 /tmp/hyprlang/wallpaper.png')

pre_process(wallpaper)
wallpaper = "/tmp/hyprlang/wallpaper.png"

conf.add_config_entries(
    preload=(wallpaper),
    wallpaper=[(monitor, wallpaper)],
    splash=0,
)
conf.add_side_effect(restart_hyprpaper)

config = Hyprlang("/tmp/hyprlang/hyprpaper.conf", __file__)
config.add(conf)

if __name__ == "__main__":
    config.write()
    config.watch()
    from time import sleep
    sleep(10**9)
```

### Example Using `add_config_entries`
```python
from Hyprlang import *

conf = Hyprlang_config(__file__)
conf.add_config_entries(
    monitor=[
        ("eDP-1", "1920x1080", "0x0", "1"),
        ("HEADLESS-2", "1280x720", "2000x2000", "1"),
    ],
    # Output:
    # monitor = eDP-1, 1920x1080, 0x0, 1
    # monitor = HEADLESS-2, 1280x720, 2000x2000, 1
    env=[("XCURSOR_SIZE", "24"), ("MOZ_ENABLE_WAYLAND", "1")],
    # Output:
    # env = XCURSOR_SIZE, 24
    # env = MOZ_ENABLE_WAYLAND, 1
    input={
        "kb_layout": "us",
        "repeat_rate": 50,
    }
    # Output:
    # input {
    #     kb_layout = us
    #     repeat_rate = 50
    # }
)
```
- if value is a list each item will be parameters in a handler repeated for each item
- if value is a tuple it will be parameters in a handler only once
- if value is a dict it will be a category

