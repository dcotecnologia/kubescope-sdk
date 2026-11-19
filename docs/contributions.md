# Contributions

A contribution is something an extension **adds** to the app. The app reads it as plain data and builds the
widgets, and it takes everything an extension added back when the extension is unloaded.

## A page in the side menu · `ui.page`

```python
ctx.add_page(
    section="AWS",  # the label that heads a part of the menu
    group="RDS",  # a group that opens and closes
    title="Instances",  # the entry that opens the page; also the title of the page
    factory=lambda: MyPage(ctx),
    subtitle="Databases of the account",
    visible=lambda: ctx.aws.uses_aws(ctx.current_context),
    refresh=lambda: page.load(),
)
```

- `factory` builds the widget **the first time the page is opened**. If the widget has a `shown()` method,
  it is called every time the page is opened.
- `visible` is asked again whenever the window changes (a context, an account). A page that is open when it
  becomes invisible is left for the Overview. An error in it hides the entry.
- `refresh` shows the refresh button of the header of the window, like the other pages, and calls your
  function when it is pressed.
- Entries with the same `section` and `group` share the label and the group.
- Translate the texts you pass: the app does not know your contexts. See *Translations* below.

## A section of the Settings · `ui.settings`

```python
ctx.add_settings_section("My extension", lambda: MyPanel(ctx))
```

The factory builds a widget with two methods (`SettingsPanel`): `load()` shows the preferences as they are
saved, and `save()` keeps what the person typed and returns `False`, after saying why, to stop the save. The
section has its own button and card in the Settings.

## A keyboard shortcut · `ui.window`

```python
ctx.add_shortcut("ask", "Ask the assistant", "Ctrl+Shift+G", handler, application=False)
```

The person can change it in **Settings → Shortcuts**. With `application=True` it works from every window of
the app, not only the main one.

## A command of the terminal · `cli`

```python
ctx.add_cli_command("chat", lambda arguments: run_chat(ctx, arguments))
```

It becomes `kubescope chat ...` and receives the rest of the arguments, returning the exit code. List the
names in `commands` of the manifest too, so the app knows them without running the extension. While it
runs, `ctx.cli` has `choose_context(name)` and `confirm(question)`, and `ctx.ui` is `None`.

## A panel and a kind of tab · `ui.dock`, `ui.tab`

Part of the API, recorded by the app but **not shown by the window yet**. See [api.md](api.md).

## Translations

An extension brings its own: the JSON files of its `languages/` folder (`pt_BR.json`, `es.json`, ...) join the
languages of the app while the extension runs. They have the same shape as the app's:

```json
{"name": "Português (Brasil)", "rtl": false,
 "strings": {"MyPage": {"Instances": "Instâncias"}}}
```

Use contexts of your own (the name of your widget class, with `self.tr("...")`, is what `pyside6-lupdate`
extracts); a context of the app is never replaced. Only the languages the app already has are used.
