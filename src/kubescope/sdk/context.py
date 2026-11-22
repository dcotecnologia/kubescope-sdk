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

from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, NamedTuple, Protocol

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


class Ui(Protocol):
    """The window, for an extension that asked for `ui.window`; it is None when
    the app runs without one (a command of the terminal)."""

    window: Any  # the main window: the parent of the boxes the extension shows
    central: Any  # the widget that panels in the corner sit on

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
    ) -> bool:
        """Tell the person through the notifications of the operating system;
        clicking it brings the app forward and then calls `on_click`.

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
