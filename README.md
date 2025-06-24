# Ankithon

![](logo.png)

Convert markdown documents to [anki](https://apps.ankiweb.net/) flashcards with this simple python script. 

This fork is powered by [python-markdown2](https://github.com/trentm/python-markdown2) and [genanki](https://github.com/kerrickstaley/genanki) all with the usage of `uv`

## Features

- Include images
- Markdown image size specifiers
- Tables
- All the basic markdown syntax
    - Bullet Lists
    - Numbered Lists ...
- Style flashcards with CSS
- *Dynamic Sub-Decks*: the number of subdecks is dynamical -> the lowerst heading is the question, all above are levels of subdecks.
- Tags

## Usage

```sh
uv sync # one time to install the dependencies
uv run main.py .\example\example.md
```

Other:

```
usage: uv run main.py [-h] [-o OUTPUT] [-s STYLE] INPUT

Convert markdown to anki deck.

positional arguments:
  INPUT                 Input *.md path.

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output *.apkg path.
  -s STYLE, --style STYLE
                        CSS card style path.
  -q, --questions       Create *_questions.md with stripped answers.
  -w, --web             Create *.html document.
```

## Dependencies

`ankithon` depends on `markdown2` and `genanki`. Which is managed with `uv`, this tool can be installed [with this simple method](https://docs.astral.sh/uv/getting-started/installation/).

If you don't want to use `uv` (which is recommended) you can install them with `pip`

```
pip install genanki
pip install markdown2
```

## Example

Turn this:

```markdown
# Deck name

## Sub deck 1

### A card question?

An answer!

### Another card question?

Another answer... _With an image!_

![](img/image.png)

## Sub deck 2

### Can you use tables?

- Yes!

| This is | a  | table    |
|---------|----|----------|
| This    | is | great!   |
| This    | is | amazing! |
| This    | is | ok!      |

### Bullet-Points?
- Example A
- Example B

### Numbered Lists?
1. Example A
2. Example B
3. Example C

### Inline Math?
$j^1 = -1$, yeah it works, but make sure that in Anki the LaTeX Rendering is set under Edit->Preferences->Review *Generate LaTeX Images*
```

Into this:

![](misc/0.png)

More examples in the `example/` directory of this repository.

### Dynamic Deck Levels

```md
# Deck
## Sub Deck
### Sub Sub Deck
#### A card question?
An answer!
```

The program will detect the lowest level, which is then taken as the *question*. All other levels will get turned into sub-decks. Please note that the heading where the question is has to be the same through the whole file. 

### Anki Tags
You can add tags in anki with a *markdown tag*
```markdown
# This is a Heading
#aTag 
this is a Tag because it does not have a space between the `#` and the name

#tagA #tagB
this should work too
```
Tags should be at the beginning of a line, and not inside of text, better at the end of the card's text.

## CSS styling.

CSS can be added using the `-s PATH/TO/STYLE.css` parameter.
CSS with the filename `style.css` in the same folder as the markdown file will be applied automatically.

Most markdown CSS should work as expected. For example this [github markdown](https://github.com/sindresorhus/github-markdown-css).

## Troubleshooting
### LaTeX Math is not rendered in Anki
This is due to a security issue, you have to enable it manually in the desktop app.
Go to: Edit->Preferences->Review *Generate LaTeX Images*

Then go to Tools->Check Media->Render LaTeX, this will process the LaTeX equations and renders them to a pictures which can be used on mobile devices
