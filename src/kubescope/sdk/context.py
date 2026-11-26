"""What an extension sees of the app: the contract, never the app itself.

The app hands the extension one `Context` when it starts. The classes
here only describe it (`Protocol`s) together with the permissions and
the errors that belong to the contract; the code behind them lives in
`kubescope.extensions`. Nothing in `kubescope.sdk` imports the app, so
this package can be published on its own.

The permissions catch mistakes and tell the person what an extension
does; they are not a sandbox, because an extension is Python that runs
in the app, so only install one from a source you trust.
"""

import datetime
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any, NamedTuple, Protocol

from kubescope.sdk.contributions import PageSpec
from kubescope.sdk.events import Events
from kubescope.sdk.models import (
    ClusterEvent,
    ClusterResource,
    PodInfo,
    SearchHit,
    Workload,
)

API_VERSION = "0"  # unstable until it is 1

PERMISSIONS = (
    "cluster.read",
    "cluster.write",
    "aws.read",
    "forward",
    "subprocess",
    "ui.dock",
    "ui.tab",
    "ui.page",
    "ui.settings",
    "ui.theme",
    "ui.window",
    "cli",
)


class PermissionDenied(Exception):
    """The extension did not ask for the permission this needs."""


class WriteModeOff(Exception):
    """The person has not turned on the write mode."""


class ClusterAccess(Protocol):
    """What an extension may read of a cluster, with the credentials and the
    kubeconfig of the context it names.

    Each call may take a while, so it is made off the UI thread; a
    failure raises `ClusterError`.
    """

    LOG_WINDOW_BYTES: int  # the most that is read of the window of a log

    def get_workloads(
        self,
        context: str,
        namespace: str | None = None,
        kinds: tuple[str, ...] = ...,
    ) -> tuple[list[str], list[Workload]]:
        """The namespaces and the replicated workloads (Deployments, ...)."""
        ...

    def get_pods(
        self, context: str, namespace: str | None = None
    ) -> tuple[list[str], list[PodInfo]]:
        """The namespaces and the Pods."""
        ...

    def get_pod_logs(
        self,
        context: str,
        namespace: str,
        pod_name: str,
        container: str,
        tail_lines: int = 500,
        since_time: str | None = None,
        since_seconds: int = 0,
        limit_bytes: int = 0,
    ) -> str:
        """The log of a container of a Pod."""
        ...

    def get_pod_container_usage(
        self, context: str, namespace: str, pod_name: str
    ) -> dict[str, tuple[float, float]] | None:
        """The CPU and the memory in use of each container of a Pod, or None
        where there are no metrics."""
        ...

    def get_usage(
        self, context: str, namespace: str | None = None
    ) -> dict[tuple[str, str, str], tuple[int, float | None, float | None]]:
        """The usage of the workloads, by (kind, namespace, name)."""
        ...

    def get_resources(
        self, context: str, namespace: str | None, kind: str
    ) -> tuple[list[str], list[ClusterResource]]:
        """The namespaces and the resources of a kind, as the lists show
        them."""
        ...

    def get_resource_details(
        self, context: str, kind: str, namespace: str, name: str
    ) -> dict[str, Any]:
        """The document of one resource."""
        ...

    def search_resources(self, context: str) -> list[SearchHit]:
        """The name of the main resources of every namespace, sorted by name
        (`SearchHit`: kind, namespace, name).

        A kind the person may not list is left out instead of failing it
        all.
        """
        ...

    def list_contexts(self) -> list[str]:
        """The names of the contexts of the kubeconfig, signed in or not."""
        ...

    def get_events(
        self, context: str, types: tuple[str, ...] = ("Warning",)
    ) -> list[ClusterEvent]:
        """The most recent events of every namespace whose `type` is one of
        `types` (Normal or Warning), the newest first."""
        ...

    def get_custom_resources(
        self,
        context: str,
        group: str,
        version: str,
        plural: str,
        namespace: str | None = None,
    ) -> dict[str, Any]:
        """The list document of a custom resource (a CRD) of `group`, which has
        a dot in it (`external-secrets.io`), as the cluster gives it.

        A kind the cluster does not serve raises `ClusterError` with the
        words of the cluster ("could not find the requested resource").
        """
        ...

    def environment(self, context: str) -> dict[str, str]:
        """What a program that you start for `context` needs in its environment
        (the keys of its integration account), or nothing; add it to your own
        environment."""
        ...

    def helm_chart_name(self, context: str, namespace: str, release: str) -> str:
        """The chart a Helm release installed, as the add-ons list read it;
        `release` itself when it is not known."""
        ...

    def helm_chart_repository(self, context: str, namespace: str, release: str) -> str:
        """The https address of the repository a Helm release's chart came
        from, when the release says it with the label `kubescope.dev/chart-
        repo` (`host_path`, the `/` of the address written `_`); else an empty
        text."""
        ...

    def eks_target(self, context: str) -> list[str]:
        """The AWS CLI arguments that name the EKS cluster of a context
        (`--cluster-name`, `--region` and `--profile`, as `aws eks update-
        addon` takes them); raises `ClusterError` when it is not an EKS
        context."""
        ...

    def aks_cluster(self, context: str) -> tuple[str, str]:
        """The name and the resource group of the AKS cluster of a context;
        raises `ClusterError` when it is not an AKS context."""
        ...

    def describe_kube(self) -> str:
        """The programs and the kubeconfig the app reads the cluster with, in
        words."""
        ...


class AwsScope(NamedTuple):
    """Where an EKS context signs in to AWS."""

    region: str
    profile: str
    account: str  # the account id, or the profile when the context has no ARN


class AwsAccess(Protocol):
    """What the AWS account of a cluster context lets an extension read."""

    def uses_aws(self, context: str | None) -> bool:
        """Whether this computer works with AWS: an account plugged in, a
        profile that signs in with SSO, or `context` is an EKS cluster."""
        ...

    def scope(self, context: str) -> AwsScope:
        """The region, profile and account of an EKS context; raises
        `ClusterError` when it is not one."""
        ...

    def regions(self) -> tuple[str, ...]:
        """The AWS regions."""
        ...

    def run(self, context: str, command: list[str], region: str = "") -> dict[str, Any]:
        """The JSON answer of an AWS CLI command (`["rds", "describe-db-
        instances"]`), with the profile or keys of the context, in `region` or
        else the one of the context.

        Only commands that read are
        run: a service and a verb the app lists, and no option that changes who
        or where it asks. Raises `ClusterError` otherwise.
        """
        ...


class Settings(Protocol):
    """The preferences of one extension, apart from the app's and the
    others'."""

    def get(self, key: str, default: Any = None) -> Any:
        """What was saved under `key`, or `default`."""
        ...

    def set(self, key: str, value: Any) -> None:
        """Save `value` (anything JSON can hold) under `key`."""
        ...


class Writes(Protocol):
    """The changes to a cluster.

    Every one raises `WriteModeOff` unless the person turned on the
    write mode, so an extension asks the person before it calls one;
    each is made off the UI thread.
    """

    def scale_deployment(
        self, context: str, namespace: str, name: str, replicas: int
    ) -> None:
        """Set the replicas of a Deployment."""
        ...

    def restart_deployment(self, context: str, namespace: str, name: str) -> None:
        """Restart the Pods of a Deployment."""
        ...

    def evict_pod(self, context: str, namespace: str, name: str) -> None:
        """Evict a Pod."""
        ...

    def delete_pod(self, context: str, namespace: str, name: str) -> None:
        """Delete a Pod."""
        ...

    def delete_resource(
        self, context: str, kind: str, namespace: str, name: str
    ) -> None:
        """Delete a resource."""
        ...

    def replace_resource(
        self,
        context: str,
        kind: str,
        namespace: str,
        name: str,
        document: dict[str, Any],
    ) -> None:
        """Replace a resource with a document."""
        ...

    def patch_custom_resource(
        self,
        context: str,
        group: str,
        version: str,
        plural: str,
        namespace: str,
        name: str,
        patch: dict[str, Any],
    ) -> None:
        """Merge `patch` (a JSON merge patch) into a custom resource of
        `group`, which has a dot in it."""
        ...

    def run_update(self, context: str, arguments: list[str]) -> str:
        """Run the command that updates what the add-ons list shows as
        installed (`aws eks update-addon`, `helm upgrade`, `az k8s-extension
        update`) with the keys of the context and the kubeconfigs of the app,
        and return what the program printed.

        Nothing else runs: another program or verb raises `ClusterError`.
        """
        ...

    def run_remove(self, context: str, arguments: list[str]) -> str:
        """Run the command that removes what the add-ons list shows as
        installed (`aws eks delete-addon`, `helm uninstall`, `az k8s-extension
        delete`) the way `run_update` runs an update, and return what the
        program printed.

        Nothing else runs: another program or verb raises `ClusterError`.
        """
        ...


class Forwards(Protocol):
    """The port forwards of the app, listed on its Forwards page."""

    def port_in_use(self, port: int) -> bool:
        """Whether something on this computer already listens on `port`."""
        ...

    def start_ssm(
        self, context: str, title: str, command: list[str], local: int, target: str
    ) -> bool:
        """Run `aws ssm start-session` (`command`, with the document AWS-
        StartPortForwardingSessionToRemoteHost) with the keys of `context`, and
        show it on the Forwards page; `target` is what it reaches, as
        host:port.

        Only in the write mode (raises `WriteModeOff`); anything but
        that command is refused with `ClusterError`. False when `local`
        is already in use.
        """
        ...


class Components(Protocol):
    """The pre-formatted elements of the app, to build a page with the look of
    the others instead of keeping a copy of them.

    Every widget they hand back is a Qt one (typed `Any`: the SDK does
    not import Qt).
    """

    def data_table(
        self, headers: Sequence[str], widths: Sequence[int], checkable: bool = False
    ) -> Any:
        """A table as the lists of the app are: one column for each of
        `headers`, the first `len(widths)` with that width in pixels and the
        last stretched, rows of the same height with a divider, one row
        selected at a time, headers centered and clickable, cells that cannot
        be edited, a text too long cut with an ellipsis, and every cell able to
        be a badge (`set_badge`).

        With `checkable`, the header has a check box in the section of
        the first column (`CheckHeader`: `set_column`, `set_check_state`
        and the `toggled` signal).
        """
        ...

    def header_sorter(
        self, table: Any, apply: Callable[[int, bool], None] | None = None
    ) -> Any:
        """Sort `table` when a header is clicked, ascending first and reversed
        on the next click, by what the cells mean (ages, numbers, versions).

        Without `apply` the sorter moves the rows of the table itself
        (and `reapply()` does it again after the table is filled); with
        it, `apply(column, order)` is called and the owner draws its
        list in that order.
        """
        ...

    def badge_delegate(self, parent: Any) -> Any:
        """The delegate that draws the cells marked by `set_badge` as the
        badges of the app, a rounded pill as wide as its column; `parent` is
        the table.

        `data_table` has it for every column already.
        """
        ...

    def set_badge(self, item: Any, status: str) -> None:
        """Mark a cell (a `QTableWidgetItem`) as a badge in the colors of
        `status`, whatever its case: green when fine (Active, Normal), amber
        while it changes (Updating, Pending), red when it failed, grey for
        anything else."""
        ...

    def set_badge_colors(self, item: Any, text: str, fill: str) -> None:
        """Mark a cell as a badge in those colors, for a state the words of
        `set_badge` do not name."""
        ...

    def button(
        self,
        text: str,
        variant: str = "secondary",
        icon: Any = None,
        on_click: Callable[[], None] | None = None,
    ) -> Any:
        """A button (`QPushButton`) as the app has them.

        `variant` is `primary` (the main action), `secondary` (any
        other) or `link` (a text the person clicks); `icon` is a
        `QIcon`; `on_click` is called when it is clicked.
        """
        ...

    def switch_button(self, text: str, tip: str) -> Any:
        """A square button that stays pressed, as the Aa (match case) and .*
        (regular expression) of a search box."""
        ...

    def search_box(self, placeholder: str = "") -> Any:
        """The search box of the lists: a `QLineEdit` with the size and the
        clear button of the app."""
        ...

    def filter_select(self, items: Sequence[tuple[str, Any]] = ()) -> Any:
        """A select (`QComboBox`) as the filters of the lists, with an item for
        each `(text, data)`."""
        ...

    def text_field(self, placeholder: str = "") -> Any:
        """A line of text (`QLineEdit`) as the fields of the forms of the
        app."""
        ...

    def number_field(self, minimum: int, maximum: int, value: int = 0) -> Any:
        """A field for a whole number (`QSpinBox`) between `minimum` and
        `maximum`, as the forms of the app have them."""
        ...

    def time_field(self) -> Any:
        """A field for a time of the day, as `HH:mm` (`QTimeEdit`)."""
        ...

    def set_time(self, field: Any, text: str) -> None:
        """Show a time given as `HH:mm` in a time field."""
        ...

    def time_text(self, field: Any) -> str:
        """The time of a time field, as `HH:mm`."""
        ...

    def spacer(self, height: int) -> Any:
        """Empty room `height` pixels high between the parts of a column."""
        ...

    def check_matrix(
        self, headers: Sequence[str], rows: Sequence[tuple[str, str]]
    ) -> Any:
        """A table of check boxes: a column for each of `headers` and a line
        for each `(key, text)` of `rows`.

        Returns `(frame, boxes)`: the frame to put in the page, and for
        each header a dict of its check boxes by key.
        """
        ...

    def text_area(self, placeholder: str = "", max_height: int = 0) -> Any:
        """A box of several lines of text to type in (`QPlainTextEdit`)."""
        ...

    def muted_label(self, text: str = "") -> Any:
        """A note in the soft color of the app (`QLabel`)."""
        ...

    def label(
        self, text: str = "", variant: str = "", wrap: bool = False, align: str = ""
    ) -> Any:
        """A text (`QLabel`).

        `variant` is `""` (the normal text), `muted` (a soft note),
        `summary` (the line that says what is listed), `filter` (the
        small title of a filter), `title` (a larger bold title) or
        `mark` (a bold mark); `wrap` breaks it into lines.
        """
        ...

    def checkbox(
        self,
        text: str,
        checked: bool = False,
        on_toggle: Callable[[bool], None] | None = None,
    ) -> Any:
        """A check box (`QCheckBox`); `on_toggle` is told whether it is
        checked."""
        ...

    def icon_button(
        self,
        icon: Any,
        tip: str,
        on_click: Callable[[], None] | None = None,
        variant: str = "link",
    ) -> Any:
        """A button that is only an icon (a `QIcon`), with its tip."""
        ...

    def command_box(self, text: str = "", height: int = 96) -> Any:
        """A box for a command or a text to read and copy (a read-only
        `QPlainTextEdit` in the fixed font)."""
        ...

    def table_item(self, text: str, tip: str = "", checked: bool | None = None) -> Any:
        """A cell for a table (`QTableWidgetItem`) with the text color of the
        theme in use, and `tip` for its tip.

        With `checked` it has a check box, checked or not.
        """
        ...

    def set_item_checked(self, item: Any, checked: bool | None) -> None:
        """Give a cell a check box, checked or not; `None` takes it away."""
        ...

    def item_checked(self, item: Any) -> bool | None:
        """Whether the check box of a cell is checked; `None` when it has
        none."""
        ...

    def menu(self, parent: Any = None) -> Any:
        """A menu (`QMenu`), as the right click of a row opens."""
        ...

    def scroll(self, content: Any) -> Any:
        """`content` in a scroll area without a frame."""
        ...

    def card(self, *items: Any, name: str = "", min_height: int = 0) -> Any:
        """A rounded box (`QFrame`) with `items` one under the other; see
        `column` for what an item can be.

        `name` is its object name.
        """
        ...

    def image_label(self, size: int) -> Any:
        """A square, `size` pixels wide, for an image (`setPixmap`)."""
        ...

    def grid_scroll(self, spacing: int = 12) -> Any:
        """A scroll area with a grid in it, for cards side by side:

        `(area, grid)`, where `area` is a `QScrollArea` to put in the
        page and `grid` a `QGridLayout` to add to.
        """
        ...

    def row(self, *items: Any, spacing: int = 12) -> Any:
        """A row of widgets (`QHBoxLayout`).

        An item is a widget, a layout, `None` for a stretch that pushes
        what follows to the right, or `(widget, stretch)`.
        """
        ...

    def column(self, *items: Any, spacing: int = 10) -> Any:
        """The same, one under the other (`QVBoxLayout`)."""
        ...

    def widget(
        self,
        shown: Callable[[], None] | None = None,
        hidden: Callable[[], None] | None = None,
        load: Callable[[], None] | None = None,
        save: Callable[[], bool] | None = None,
    ) -> Any:
        """The widget of your page, or of your section of the Settings, to give
        to `add_page` or `add_settings_section` and to lay out with `page`.

        The app calls `shown` when the page is opened, and `load` and
        `save` for a section of the Settings; `hidden` is called when
        the widget is hidden. Keep your page as a plain object that
        holds this widget, and do not subclass a Qt class.
        """
        ...

    def copy_text(self, text: str) -> None:
        """Put `text` on the clipboard."""
        ...

    def timer(
        self,
        interval_ms: int,
        callback: Callable[[], None],
        owner: Any = None,
        single_shot: bool = False,
    ) -> Any:
        """A timer that calls `callback` every `interval_ms` once it is
        started, or once with `single_shot`: `start()`, `stop()` and
        `is_active()`.

        It goes away with `owner`, a widget.
        """
        ...

    def after(self, delay_ms: int, owner: Any, callback: Callable[[], None]) -> None:
        """Call `callback` once, in `delay_ms`, unless `owner` is gone."""
        ...

    def icon(self, name: str, color: str, **options: Any) -> Any:
        """An icon of the app by name, in `color`: `update`, `info`, `trash`,
        `bell`, `send`, `stop`, `attach`, `popout`, `dock`, `gear`, `chat-
        trash`, `close`, `plus`, `focus` (`active=True` for the leaving one)
        and `sparkle` (`size` and the `inside` color)."""
        ...

    def open_url(self, url: str) -> None:
        """Open an address in the browser of the person."""
        ...

    def on_context_menu(self, table: Any, handler: Callable[[int, int], None]) -> None:
        """Call `handler(x, y)` on a right click in a table, with the place in
        its rows (`table.rowAt(y)` says which); open the menu with
        `show_menu`."""
        ...

    def show_menu(self, menu: Any, table: Any, x: int, y: int) -> None:
        """Open `menu` at the place `(x, y)` of the rows of `table`."""
        ...

    def image(self, data: bytes, size: int) -> Any:
        """An image of those bytes, scaled to fit `size` pixels; `None` when it
        is not one that can be drawn.

        Give it to `set_image`.
        """
        ...

    def set_image(self, label: Any, image: Any) -> None:
        """Show an image from `image` in a label (see `image_label`)."""
        ...

    def on_resize(self, widget: Any, callback: Callable[[], None]) -> None:
        """Call `callback` when `widget` is resized."""
        ...

    def grid_cell(
        self,
        grid: Any,
        widget: Any,
        row: int,
        column: int,
        column_span: int = 1,
        center: bool = False,
    ) -> None:
        """Put `widget` in a cell of a grid (from `grid_scroll`), over
        `column_span` columns, centered in them when asked."""
        ...

    def bottom_of(self, widget: Any, host: Any) -> int:
        """Where the bottom edge of `widget` is, as a y in the coordinates of
        `host`."""
        ...

    def is_alive(self, widget: Any) -> bool:
        """Whether a widget still exists: the app deletes a page it built when
        it builds its menu again."""
        ...

    def side_panel(
        self,
        host: Any,
        title: str,
        actions: Sequence[Any],
        top: Callable[[], int],
        close_text: str = "✕",
        empty_text: str = "",
    ) -> Any:
        """A panel that slides in from the right edge of `host` (the
        `ui.central` widget), under the top bar (`top()` is where it starts):

        a title, the `actions` buttons in its header, a close button and
        a scrolling list of cards (`show_cards`). It is opened and
        closed with `open_panel()` and `close_panel()`, remembers the
        width the person dragged it to (`on_resized`) and tells when it
        closed (`on_closed`); `is_inside(point)` says a click is of its
        own button, and `opened` says whether it is open.
        """
        ...

    def notice_card(
        self,
        title: str,
        kind: str,
        about: str,
        message: str,
        when: str,
        level: str,
        unread: bool,
        tip: str,
        on_click: Callable[[], None],
        actions: Sequence[tuple[str, Callable[[], None]]] = (),
    ) -> Any:
        """A card for a list of notices: `title` and `kind` on the first line,
        where it is `about`, its `message`, `when` it began and links `(text,
        callback)` under it.

        `level` is `error`, `warning` or `info`; an read one (`unread`
        false) is crossed out. A click on it calls `on_click`.
        """
        ...

    def counter_button(self, icon: Any, tip: str, name: str = "counterButton") -> Any:
        """A flat 32 px button for the top bar, with a red badge for a count
        (`set_unread(count)`); it can be checked while its panel is open and
        takes the colors of the theme (`restyle(themed)`)."""
        ...

    def ask(self, parent: Any, title: str, text: str) -> bool:
        """A Yes or No question; True for Yes, and No is the default."""
        ...

    def guide(
        self,
        parent: Any,
        title: str,
        text: str,
        detail: str,
        buttons: Sequence[tuple[str, Callable[[], None]]],
        close_text: str,
    ) -> None:
        """A message with a longer `detail` and a button for each `(text,
        callback)`, which runs its callback and closes it, and a last one
        (`close_text`) that only closes it."""
        ...

    def let_window_shrink(self, window: Any, shrink: bool) -> None:
        """Let the main window be made as small as its layout allows (a page
        that needs no width), or give back the least it asked."""
        ...

    def palette(self, parent: Any, title: str, placeholder: str, loading: str) -> Any:
        """The window that finds a screen, an action or a resource as one types,
        like a command palette: `open_with(entries)` shows it with entries that
        have `label`, `detail` and `run`; `set_resources(hits, run)` adds what
        was found in the cluster; `resources_failed(text)` says why not."""
        ...

    def background(
        self,
        function: Callable[[], Any],
        on_piece: Callable[[Any], None] | None = None,
        on_done: Callable[[Any], None] | None = None,
        on_error: Callable[[str], None] | None = None,
        on_finished: Callable[[], None] | None = None,
        stream: bool = False,
    ) -> Any:
        """Run `function` off the UI thread and hear from it on it:

        `on_done(answer)`, `on_error(message)` and `on_finished()`. With
        `stream`, `function` is a generator and `on_piece(piece)` hears
        each piece as it is made. The handle has `stopped` (set it to
        cut a stream short; the generator is closed) and `wait(ms)`.
        """
        ...

    def chat_view(self, texts: dict[str, str]) -> Any:
        """A conversation with an assistant laid out as a chat, with its
        composer: bubbles (`add_bubble`), what is attached (`show_chips`),
        the status, the usage ring and the action cards. It tells what the
        person does through signals (`submitted`, `stop_requested`,
        `attach_requested`, `image_pasted`, `files_pasted`, `text_pasted`,
        `ring_clicked`). `texts` are its words in the language of the app."""
        ...

    def chat_dock(self, host: Any, name: str, texts: dict[str, str]) -> Any:
        """The round button in the corner of `host` and the chat panel it
        opens, which can be resized, taken out into a window or made to fill
        the page; `texts` are the words of the panel, by their English text."""
        ...

    def open_file(self, parent: Any, title: str, start: str = "") -> str:
        """Ask the person to choose a file to open; its path, or an empty text
        when they gave up.

        `start` is the folder it opens in.
        """
        ...

    def error_banner(
        self,
        details_text: str = "Details",
        hide_text: str = "Hide",
        dismiss_text: str = "Dismiss",
    ) -> Any:
        """A red banner for what went wrong.

        It starts hidden; put `banner.frame` in the page, and call
        `banner.show_error(text, details)` for a line with the whole
        error one click away (`banner.dismiss()` hides it). The three
        texts name its buttons, in your language.
        """
        ...

    def form(self, rows: Sequence[tuple[str, Any]]) -> Any:
        """Rows of a form (`QFormLayout`): a `(text, field)` for each."""
        ...

    def page(
        self,
        parent: Any,
        *,
        filters: Any = None,
        actions: Any = None,
        notice: Any = None,
        body: Any = None,
        footer: Any = None,
    ) -> Any:
        """Lay `parent` (the widget of your page) out as the pages of the
        app: the `filters` row, the `actions` row, a `notice`, the `body`
        (which takes what is left) and the `footer` row; leave out what the
        page does not have. The rows are layouts, made with `row`."""
        ...

    def dialog(
        self,
        parent: Any,
        title: str,
        body: Any,
        buttons: Sequence[Any],
        width: int = 0,
    ) -> Any:
        """A dialog (`QDialog`) with `body` (a layout or a widget) above a row
        of `buttons` at the right; call `exec()` on it."""
        ...

    def confirm(
        self,
        parent: Any,
        title: str,
        text: str,
        ok: str = "OK",
        detail: str = "",
        warning: bool = False,
    ) -> bool:
        """Ask the person to confirm something; True when they chose `ok`.

        `detail` is a longer text under `text` (the commands about to
        run, say) and `warning` shows the warning icon. Cancel is the
        default answer.
        """
        ...


class Ui(Protocol):
    """The window, for an extension that asked for `ui.window`; it is None when
    the app runs without one (a command of the terminal)."""

    window: Any  # the main window: the parent of the boxes the extension shows
    central: Any  # the widget that panels in the corner sit on
    components: Components  # the pre-formatted elements of the app

    def show_message(self, icon: str, title: str, text: str) -> None:
        """Tell the person something; `icon` is information, warning or
        critical."""
        ...

    def run_action(
        self,
        function: Callable[..., Any],
        on_success: Callable[[Any], None],
        *arguments: Any,
        on_error: Callable[[str], None] | None = None,
        quiet: bool = False,
    ) -> None:
        """Call `function` off the UI thread; the answer comes to
        `on_success`."""
        ...

    def pick_item(self, title: str, label: str, items: list[str]) -> tuple[str, bool]:
        """Ask the person to pick one of `items`; the one picked and whether
        they accepted."""
        ...

    def pick_row(
        self,
        title: str,
        label: str,
        headers: list[str],
        rows: list[list[str]],
        moments: list[datetime.datetime] | None = None,
    ) -> tuple[int, bool]:
        """Ask the person to pick one of `rows` in a table that narrows as they
        type; the index of the one picked and whether they accepted.

        With `moments`, one for each row, the table also has a range of
        dates to filter by.
        """
        ...

    def show_json(self, title: str, document: dict[str, Any]) -> None:
        """Show `document` in a Details tab."""
        ...

    def open_log(self, title: str, name: str, read: Callable[[], str]) -> None:
        """Show a text in a Logs tab, with a refresh button; `read` returns it
        and runs off the UI thread each time it is asked."""
        ...

    def style_box(self, box: Any) -> None:
        """Give a message box the buttons of the window."""
        ...

    def show_settings(self, section: str = "") -> None:
        """Go to the Settings, to the section of the extension named
        `section`."""
        ...

    def themed(self, color: str, text: bool = False) -> str:
        """A color of the design as the theme in use shows it; `text` is for
        the color of a text on the background of the theme."""
        ...

    def show_system_notification(
        self,
        title: str,
        message: str,
        on_click: Callable[[], None] | None = None,
        category: str = "",
    ) -> bool:
        """Tell the person through the notifications of the operating system;
        clicking it brings the app forward and then calls `on_click`.

        `category` says what kind of notice it is (`"action"` for
        something the person asked that was done, `"pod"` for the state
        of a Pod after it, `"task"` for an activity that finished). With
        the notifications extension running, it keeps the notice and the
        person chooses, by category, which are listed and which are told
        to the system; without a category the notice of the system is
        shown at once.

        False when the desktop cannot show one.
        """
        ...

    def add_top_bar_button(self, owner: str, button: Any) -> None:
        """Put `button` (a widget of about 32 px) in the top bar, beside the
        button of the Settings; the app takes it out when `owner`, the id of
        the extension, is unloaded."""
        ...

    def reserve_corner(self, owner: str, pixels: int) -> None:
        """Keep `pixels` of the corner of the window clear for `owner`; 0 gives
        it back."""
        ...

    def content_area(self) -> tuple[int, int, int, int]:
        """Where the pages of the window are, as (x, y, width, height) in the
        coordinates of `central`: everything between the top bar and the
        footer, the side menu included.

        A panel that takes the place of the pages, such as a focus mode,
        fills it and leaves the bars as they are.
        """
        ...

    def hide_side_menu(self, owner: str, hidden: bool) -> None:
        """Hide the side menu of the window while `owner` asks it, so that the
        page takes the whole width; the person's own choice of showing or
        hiding the menu is kept and comes back when every owner gave it back
        (`hidden` False), or when `owner` is unloaded."""
        ...


class App(Protocol):
    """What the extension may know about the app."""

    @property
    def write_mode(self) -> bool:
        """Whether the person turned on the write mode."""
        ...

    @property
    def language(self) -> str:
        """The language chosen in the Settings (`auto` follows the system)."""
        ...

    @property
    def resolved_language(self) -> str:
        """The code of the language the app shows: what `language` is, or the
        one of the system when it is `auto`."""
        ...

    @property
    def language_names(self) -> tuple[str, ...]:
        """The English names of every language the app has, English first, then
        in alphabetical order."""
        ...

    @property
    def language_name(self) -> str:
        """The name of that language in English, to tell an assistant which one
        to answer in."""
        ...


class Cli(Protocol):
    """What the terminal lends to a command of an extension, which runs with
    the cluster already set up as the person configured it."""

    def choose_context(self, name: str | None) -> str:
        """The context to use: `name` if it is one of the kubeconfig, or the
        one the person picks (asked in the terminal)."""
        ...

    def confirm(self, question: str) -> bool:
        """Ask the person a question that is answered with yes or no."""
        ...


class SettingsPanel(Protocol):
    """What the factory of a section of the Settings builds: a widget that has
    these two methods."""

    def load(self) -> None:
        """Show the preferences as they are saved."""
        ...

    def save(self) -> bool:
        """Keep what the person typed; False (after saying why) stops the
        save."""
        ...


class Context(Protocol):
    """What `activate(ctx)` receives."""

    @property
    def id(self) -> str:
        """The id of the extension, as its manifest says."""
        ...

    @property
    def permissions(self) -> frozenset[str]:
        """What its manifest asked for."""
        ...

    @property
    def events(self) -> Events:
        """The events the app tells it about."""
        ...

    @property
    def settings(self) -> Settings:
        """Its own preferences."""
        ...

    @property
    def cluster(self) -> ClusterAccess:
        """The read paths of the cluster; needs `cluster.read`."""
        ...

    @property
    def aws(self) -> AwsAccess:
        """The AWS account of the cluster contexts, to read; needs
        `aws.read`."""
        ...

    @property
    def forwards(self) -> Forwards:
        """The port forwards; needs `forward`."""
        ...

    @property
    def writes(self) -> Writes:
        """The writes; needs `cluster.write`."""
        ...

    @property
    def current_context(self) -> str | None:
        """The cluster context the window is on."""
        ...

    def snapshot(self) -> str:
        """What the window shows, in words."""
        ...

    def invoke(self, command: str, /, **arguments: Any) -> Any:
        """Do in the window what the person could do by hand."""
        ...

    @property
    def cli(self) -> Cli | None:
        """The terminal, when a command of the extension is what runs; None in
        the window."""
        ...

    @property
    def data_directory(self) -> Path:
        """A folder that is the extension's own, for what it writes down (it
        may not exist yet)."""
        ...

    @property
    def ui(self) -> Ui | None:
        """The window; needs `ui.window`, and is None without one."""
        ...

    @property
    def app(self) -> App:
        """What the app says about itself."""
        ...

    def register_command(self, name: str, command: Callable[..., Any]) -> None:
        """Offer a command to the app, named `<id of the extension>.<name>`."""
        ...

    def add_shortcut(
        self,
        action: str,
        label: str,
        default: str,
        handler: Callable[[], None],
        application: bool = False,
    ) -> None:
        """Add a keyboard shortcut the person can change in the Settings; needs
        `ui.window`.

        With `application` it works from every window of the app.
        """
        ...

    def on_unload(self, callback: Callable[[], None]) -> None:
        """Call `callback` when the extension is unloaded or reloaded, to close
        what it created (a panel, a thread)."""
        ...

    def add_dock(
        self, key: str, factory: Callable[..., Any], shortcut: str = ""
    ) -> None:
        """Add a panel in the corner of the window; needs `ui.dock`."""
        ...

    def add_page(
        self,
        section: str,
        group: str,
        title: str,
        factory: Callable[..., Any],
        subtitle: str = "",
        visible: Callable[[], bool] | None = None,
        refresh: Callable[[], None] | None = None,
    ) -> None:
        """Add a page to the side menu: an entry `title`, in the menu `group`
        of the `section`, that opens the widget `factory` builds (when it is
        first shown).

        `visible` says whether the entry shows now; it is asked again
        whenever the window changes. If the widget has a `shown()`
        method, it is called each time the page is opened. With
        `refresh`, the header of the window shows its refresh button
        while the page is open, like the other pages, and calls it.
        Needs `ui.page`.
        """
        ...

    def set_pages(self, key: str, pages: Sequence[PageSpec]) -> None:
        """Give the side menu the pages `pages`, for entries that are known
        only while the app runs (the custom resources of a cluster).

        It replaces the pages an earlier `set_pages` with the same `key`
        gave and builds the menu again, so a page that is open is left
        for the Overview: call it only when the entries change. It is
        made on the UI thread. Needs `ui.page`.
        """
        ...

    def add_tab_kind(self, key: str, factory: Callable[..., Any]) -> None:
        """Add a kind of tab; needs `ui.tab`."""
        ...

    def add_settings_section(self, title: str, factory: Callable[..., Any]) -> None:
        """Add a section to the Settings; needs `ui.settings`."""
        ...

    def add_theme(self, theme_id: str, document: Mapping[str, Any]) -> None:
        """Offer a color theme, chosen in **Settings → Theme** like the ones of
        the app.

        `document` is what a theme file holds (`{"name": "Midnight",
        "base": "dark", "colors": {"page": "#0b0f14"}}`); one the app
        finds invalid is skipped and logged. The theme goes with the
        extension. Needs `ui.theme`.
        """
        ...

    def add_cli_command(self, name: str, run: Callable[[list[str]], int]) -> None:
        """Add a subcommand of `kubescope`; needs `cli`."""
        ...
