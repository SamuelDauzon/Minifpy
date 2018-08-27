# Minifpy : merge and/or minify your JS/CSS files

## Installation

You must have Python3 installed.
Clone this projet and install requirements by using the command `pip3 -r requirements.txt`(or `py -m pip3 -r requirements.txt`in Windows).
You should copy/paste *minifpy.py* file in your project root (or where you want if you use Minifpy in CLI mode only).


## How to use it

You can choose many ways to use Minifpy. You can use it without configuration with CLI or create a *minifpy_settings.json* file.

## In CLI mode without configuration

You can use the following command for a *.js* or *.css* file : 

```
python3 minifpy.py -f path/file.js
```

This command will minify file in *path/file.min.js* file. An CSS file will result in *.min.css* file.

## In standalone mode without configuration

If you use the following command

```
python3 minifpy.py -r
```

in a folder, all JS/CSS files will be minified in *.min.js* or *.min.css* automatically when system detect file changes.

## In CLI mode with project configured

The configuration of project is explained below.

The command

```
python3 minifpy.py
```

read *minifpy_settings.json* file then merge and minify all files defined in settings.

If you run *-f* argument in a file in a project (with minifpy_settings), Minifpy will merge it with others if it defined and minify it.


## In standalone mode with project configured

The configuration of project is explained below.

The command

```
python3 minifpy.py -r
```

monitor modifications in project and merge and minify files in accordance with *minifpy_settings.json* file.

## Write minifpy_settings.json file

The *minifpy_settings.json* file provide a way to define how Minifpy to merge and minify files. The syntax is the following : 

```
{
    "js": {
        "minify_files": [
            {"from": "static/js/admin_feature.js", "to":"static/js/admin_feature.min.js"},
        ],
        "merge_files": [
            {"from" : ["static/js/user_feature.js", "static/js/pricing_feature.js"], "to":"static/js/public.js", "to_min": "static/js/public.min.js"}
        ]
    },
    "css" : {
        "minify_files": [
            {"from": "static/css/admin_feature.css", "to":"static/css/admin_feature.min.css"},
        ],
        "merge_files": [
            {"from" : ["static/css/user_feature.css", "static/css/pricing_feature.css"], "to":"static/css/public.css", "to_min": "static/css/public.min.css"}
        ]
    }
}
```





