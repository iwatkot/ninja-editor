import os
import supervisely as sly

from supervisely.app.widgets import (
    Select,
    Field,
    Card,
    Container,
    RadioTabs,
    Button,
    Input,
    InputNumber,
    Text,
    Flexbox,
    Editor,
)
from dataset_tools.templates import License, Industry, CVTask, AnnotationType

import src.globals as g

bad_settings_text = Text("Incorrect settings were entered.", "error")
bad_settings_text.hide()

status_text = Text()
status_text.hide()

project_name_input = Input(placeholder="Input project name")
project_name_field = Field(
    title="* Project name",
    description="Enter project name which will be used on Ninja website.",
    content=project_name_input,
)

project_name_full_input = Input(placeholder="Input project name")
project_name_full_field = Field(
    title="Project name (full)",
    description="Enter the full project name which will be used on Ninja website.",
    content=project_name_full_input,
)

licensies = [
    subclass for subclass in License.__dict__.values() if isinstance(subclass, type)
]
license_values = [subclass.__name__ for subclass in licensies]
license_labels = [subclass().name for subclass in licensies]

license_items = [
    Select.Item(value, label) for value, label in zip(license_values, license_labels)
]
license_select = Select(license_items, filterable=True, placeholder="Select license")
license_select.set_value(None)
license_field = Field(
    title="* License",
    description="Select license to apply to the dataset.",
    content=license_select,
)

industries = [
    subclass for subclass in Industry.__dict__.values() if isinstance(subclass, type)
]
industry_values = [subclass.__name__ for subclass in industries]
industry_items = [Select.Item(value) for value in industry_values]
industry_select = Select(
    industry_items, filterable=True, placeholder="Select industry", multiple=True
)
industry_field = Field(
    title="* Industries",
    description="Select industry to apply to the dataset.",
    content=industry_select,
)
cvtasks = [
    subclass for subclass in CVTask.__dict__.values() if isinstance(subclass, type)
]
cvtasks_values = [subclass.__name__ for subclass in cvtasks]
cvtasks_items = [Select.Item(value) for value in cvtasks_values]
cvtask_select = Select(
    cvtasks_items, filterable=True, placeholder="Select CV task", multiple=True
)
cvtask_field = Field(
    title="* CV tasks",
    description="Select CV tasks to apply to the dataset.",
    content=cvtask_select,
)

annotation_types = [
    subclass
    for subclass in AnnotationType.__dict__.values()
    if isinstance(subclass, type)
]
annotation_types_values = [subclass.__name__ for subclass in annotation_types]
annotation_types_items = [Select.Item(value) for value in annotation_types_values]
annotation_types_select = Select(
    annotation_types_items,
    filterable=True,
    placeholder="Select annotation type",
    multiple=True,
)
annotation_types_field = Field(
    title="* Annotation types",
    description="Select annotation types to apply to the dataset.",
    content=annotation_types_select,
)

release_year_input = InputNumber()
release_year_field = Field(
    title="* Release year",
    description="Enter release year of the dataset.",
    content=release_year_input,
)

homepage_url_input = Input(placeholder="Enter homepage URL")
homepage_url_field = Field(
    title="* Homepage URL",
    description="Enter homepage URL of the dataset.",
    content=homepage_url_input,
)

preview_image_id_input = InputNumber(value=0)
preview_image_id_field = Field(
    title="* Preview image ID",
    description="Enter ID of the preview image (after upload).",
    content=preview_image_id_input,
)

download_original_url_input = Input(placeholder="Enter download original URL")
download_original_url_field = Field(
    title="Download original URL",
    description="Enter download original URL of the dataset.",
    content=download_original_url_input,
)

settings_container = Container(
    widgets=[
        bad_settings_text,
        project_name_field,
        project_name_full_field,
        license_field,
        industry_field,
        cvtask_field,
        annotation_types_field,
        release_year_field,
        homepage_url_field,
        preview_image_id_field,
    ]
)
options_container = Container(widgets=[])

settings_preview = Editor(height_lines=80, language_mode="python")

settings_tabs = RadioTabs(
    titles=["Edit", "Preview"],
    contents=[settings_container, settings_preview],
)

edit_tabs = RadioTabs(
    titles=["Settings", "Options"],
    contents=[settings_tabs, options_container],
)

apply_button = Button("Apply", icon="zmdi zmdi-check")

push_button = Button("Push", icon="zmdi zmdi-github-alt", button_type="success")
push_button.disable()

buttons_flexbox = Flexbox([apply_button, push_button])


card = Card(
    title="3️⃣ Edit repository",
    description="Prepare settings for the dataset.",
    content=Container([status_text, edit_tabs]),
    collapsable=True,
    lock_message="Select and clone repository on step 2️⃣.",
    content_top_right=buttons_flexbox,
)
card.lock()
card.collapse()


@apply_button.click
def apply():
    bad_settings_text.hide()
    status_text.hide()

    try:
        new_settings = {
            "PROJECT_NAME": f'"{project_name_input.get_value()}"',
            "LICENSE": f"License.{license_select.get_value()}()",
            "INDUSTRIES": str(
                [f"Industry.{industry}()" for industry in industry_select.get_value()]
            ).replace("'", ""),
            "CV_TASKS": str(
                [f"CVTask.{cvtask}()" for cvtask in cvtask_select.get_value()]
            ).replace("'", ""),
            "ANNOTATION_TYPES": str(
                [
                    f"AnnotationType.{annotation_type}()"
                    for annotation_type in annotation_types_select.get_value()
                ]
            ).replace("'", ""),
            "RELEASE_YEAR": release_year_input.get_value(),
            "HOMEPAGE_URL": f'"{homepage_url_input.get_value()}"',
            "PREVIEW_IMAGE_ID": preview_image_id_input.get_value(),
            "GITHUB_URL": f'"{g.AppState.repo_url}"',
        }
    except Exception as e:
        sly.logger.error(f"Error while reading new settings: {e}")
        bad_settings_text.show()
        return

    if any([value is None for value in new_settings.values()]):
        sly.logger.error("Some settings are empty, stopping")
        bad_settings_text.show()
        return

    optional_settings = {
        "PROJECT_NAME_FULL": f'"{project_name_full_input.get_value()}"',
    }

    new_settings.update(optional_settings)

    sly.logger.debug(f"New settings: {new_settings}")

    settings_py_path = os.path.join(g.AppState.local_repo_path, "src", "settings.py")

    sly.logger.info(f"Updating settings.py: {settings_py_path}")

    with open(settings_py_path, "r") as file:
        lines = file.readlines()
        for key, value in new_settings.items():
            for i, line in enumerate(lines):
                if line.startswith(f"{key}:"):
                    sly.logger.info(
                        f"Found needed line: {line} with key: {key} for editing"
                    )

                    line_beginning = f"{line.rsplit('=', 1)[0].strip()} = "
                    line_ending = str(value)
                    new_line = line_beginning + line_ending + "\n"

                    sly.logger.info(f"Will replace the line with new line: {new_line}")

                    lines[i] = new_line

    sly.logger.info(
        f"Finish updating settings.py: {settings_py_path}, will write to file"
    )

    with open(settings_py_path, "w") as file:
        file.writelines(lines)

    sly.logger.info(f"Finish writing to settings.py: {settings_py_path}")

    settings_tabs.loading = True
    settings_preview.loading = True

    settings_preview.set_text("".join(lines))
    push_button.enable()

    settings_tabs.loading = False
    settings_preview.loading = False

    settings_tabs.set_active_tab("Preview")


@push_button.click
def push():
    status_text.hide()
    push_button.text = "Pushing..."
    apply_button.disable()
    settings_file_string = settings_preview.get_text()
    settings_py_path = os.path.join(g.AppState.local_repo_path, "src", "settings.py")

    with open(settings_py_path, "w") as file:
        file.write(settings_file_string)

    sly.logger.info(
        f"Readed contents from the widget and saved it into settings.py: {settings_py_path}"
    )

    repo = g.AppState.repo

    index = repo.index
    index.add([settings_py_path])

    sly.logger.info(f"Added settings.py to index: {settings_py_path}")

    if not index.diff("HEAD"):
        sly.logger.info("No files was added to index in repo. Nothing to commit.")
        status_text.text = "No files was added to index in repo. Nothing to commit."
        status_text.status = "info"
        return

    repo.index.commit("Automatic commit by repo-updater.")
    sly.logger.info("Created commit. Pushing...")

    remote = repo.remote("origin")
    remote.push()

    sly.logger.info("Pushed commit to remote.")

    push_button.text = "Push"
    apply_button.enable()

    status_text.text = "Pushed commit to remote."
    status_text.status = "success"
    status_text.show()


def load_settings():
    settings = g.AppState.settings

    for key, value in settings.items():
        if value == "None":
            settings[key] = None

    sly.logger.info("Trying to load settings from file to widgets...")

    if settings.get("PROJECT_NAME"):
        project_name_input.set_value(settings["PROJECT_NAME"].strip('"'))

    if settings.get("PROJECT_NAME_FULL"):
        project_name_full_input.set_value(settings["PROJECT_NAME_FULL"].strip('"'))

    if settings.get("LICENSE"):
        license_select.set_value(settings["LICENSE"].split(".")[-1].strip("()"))

    if settings.get("INDUSTRIES"):
        industries = settings["INDUSTRIES"].replace("[", "").replace("]", "").split(",")
        industry_select.set_value(
            [industry.split(".")[-1].strip("()") for industry in industries]
        )

    if settings.get("CV_TASKS"):
        cvtasks = settings["CV_TASKS"].replace("[", "").replace("]", "").split(",")
        cvtask_select.set_value(
            [cvtask.split(".")[-1].strip("()") for cvtask in cvtasks]
        )

    if settings.get("ANNOTATION_TYPES"):
        annotation_types = (
            settings["ANNOTATION_TYPES"].replace("[", "").replace("]", "").split(",")
        )
        annotation_types_select.set_value(
            [
                annotation_type.split(".")[-1].strip("()")
                for annotation_type in annotation_types
            ]
        )

    if settings.get("RELEASE_YEAR"):
        release_year_input.value = int(settings["RELEASE_YEAR"].strip('"'))

    if settings.get("HOMEPAGE_URL"):
        homepage_url_input.set_value(settings["HOMEPAGE_URL"].strip('"'))

    if settings.get("PREVIEW_IMAGE_ID"):
        preview_image_id_input.value = int(settings["PREVIEW_IMAGE_ID"].strip('"'))


"""
def check_inputs(value=None):
    push_button.disable()

    widgets_to_check = [
        project_name_input,
        license_select,
        industry_select,
        cvtask_select,
        annotation_types_select,
        release_year_input,
        homepage_url_input,
    ]

    values = [widget.get_value() for widget in widgets_to_check]
    print(values)

    if any([not widget.get_value() for widget in widgets_to_check]):
        apply_button.disable()
    else:
        apply_button.enable()


project_name_input.value_changed(check_inputs)
license_select.value_changed(check_inputs)
industry_select.value_changed(check_inputs)
cvtask_select.value_changed(check_inputs)
annotation_types_select.value_changed(check_inputs)
release_year_input.value_changed(check_inputs)
homepage_url_input.value_changed(check_inputs)
"""
