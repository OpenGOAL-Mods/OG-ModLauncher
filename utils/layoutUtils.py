import PySimpleGUI as sg
from utils import githubUtils


def generate(splashfile, loadingimage, LATEST_TABLE_DATA, table_headings, col_vis, col_width):
    return \
        [
            [
                sg.Frame(
                    title="",
                    key="-SPLASHFRAME-",
                    border_width=0,  # Set border_width to 0
                    visible=True,
                    element_justification="center",
                    vertical_alignment="center",
                    layout=[
                        [
                            sg.Image(
                                key="-SPLASHIMAGE-",
                                source=githubUtils.resize_image(splashfile, 970, 607),
                                pad=(0, 0),  # Set padding to 0
                                expand_x=True,
                                expand_y=True,
                            )
                        ]
                    ],
                )
            ],
            [
                sg.Frame(
                    title="",
                    key="-LOADINGFRAME-",
                    border_width=0,  # Set border_width to 0
                    visible=False,
                    element_justification="center",
                    vertical_alignment="center",
                    layout=[
                        [
                            sg.Image(
                                key="-LOADINGIMAGE-",
                                source=githubUtils.resize_image(loadingimage, 970, 607),
                                pad=(0, 0),  # Set padding to 0
                                expand_x=True,
                                expand_y=True,
                            )
                        ]
                    ],
                )
            ],
            [
                sg.Frame(
                    title="",
                    key="-MAINFRAME-",
                    border_width=0,
                    visible=False,
                    layout=[
                        [
                            __side_panel(),
                            sg.VerticalSeparator(),
                            __main_panel(LATEST_TABLE_DATA, table_headings, col_vis, col_width)
                        ]
                    ]
                )
            ],
        ]


def __side_panel():
    return sg.Column(  # nav sidebar
        [
            [sg.Text("JAK 1", font=("Helvetica", 16, "bold"))],
            [__default_radio("Mods", "filter", "jak1/mods")],
            [__radio("Texture Packs", "filter", "jak1/tex")],

            [sg.Text("")],

            [sg.Text("JAK 2", font=("Helvetica", 16, "bold"))],
            [__radio("Mods", "filter", "jak2/mods")],
            [__radio("Texture Packs", "filter", "jak2/tex")],

            [sg.VPush()],

            [__button("View iso_data Folder", "-VIEWISOFOLDER-")],
            [__button("jakmods.dev", "-JAKMODSWEB-")],
        ],
        expand_y=True,
    )


def __main_panel(LATEST_TABLE_DATA, table_headings, col_vis, col_width):
    install_filter = sg.Checkbox(
        text="Show Installed",
        default=True,
        enable_events=True,
        key="-SHOWINSTALLED-",
    )

    uninstall_filter = sg.Checkbox(
        text="Show Uninstalled",
        default=True,
        enable_events=True,
        key="-SHOWUNINSTALLED-",
    )

    search_bar = sg.Input(
        expand_x=True,
        enable_events=True,
        key="-FILTER-"
    )

    mod_table = sg.Table(
        values=LATEST_TABLE_DATA,
        headings=table_headings,
        visible_column_map=col_vis,
        col_widths=col_width,
        auto_size_columns=False,
        num_rows=15,
        text_color="black",
        background_color="lightblue",
        alternating_row_color="white",
        justification="left",
        selected_row_colors="black on yellow",
        key="-MODTABLE-",
        expand_x=True,
        expand_y=True,
        enable_click_events=True
    )

    mod_image = sg.Frame(
        title="",
        element_justification="center",
        vertical_alignment="center",
        border_width=0,
        layout=[
            [
                sg.Image(
                    key="-SELECTEDMODIMAGE-", expand_y=True
                )
            ]
        ],
        size=(450, 300),
    )

    button_panel_with_mod_info = sg.Column(
        [
            [sg.Text("", key="-SELECTEDMODNAME-", font=("Helvetica", 13), metadata={"id": "", "url": ""})],
            [sg.Text("", key="-SELECTEDMODDESC-", size=(45, 7))],
            [sg.Text("Tags:", key="-SELECTEDMODTAGS-")],
            [sg.Text("Contributors:", key="-SELECTEDMODCONTRIBUTORS-")],
            [sg.Text("")],
            [__button("Launch", "-LAUNCH-"), __button("Re-extract", "-REEXTRACT-"),
             __button("Recompile", "-RECOMPILE-"), __button("Uninstall", "-UNINSTALL-")],
            [__button("View Folder", "-VIEWFOLDER-"), __button_with_metadata("Website", "-WEBSITE-"),
             __button_with_metadata("Video(s)", "-VIDEOS-")]
        ],
        size=(200, 300),
        expand_x=True,
        expand_y=True,
    )

    return sg.Column(
        [
            [button_panel_with_mod_info, mod_image],
            [sg.HorizontalSeparator()],
            [sg.Text("Search"), search_bar, install_filter, uninstall_filter],
            [mod_table]

        ]
    )


def __button(button_text, key):
    return sg.Btn(
        button_text=button_text,
        key=key,
        expand_x=True,
    )


def __button_with_metadata(button_text, key):
    return sg.Btn(
        button_text=button_text,
        key=key,
        expand_x=True,
        metadata={"url": ""}
    )


def __radio(text, group_id, key):
    return sg.Radio(
        text=text,
        group_id=group_id,
        font=("Helvetica", 12),
        enable_events=True,
        key=key
    )


def __default_radio(text, group_id, key):
    return sg.Radio(
        text=text,
        group_id=group_id,
        font=("Helvetica", 12),
        enable_events=True,
        key=key,
        default=True
    )
