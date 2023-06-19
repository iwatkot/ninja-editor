from supervisely.app.widgets import (
    Select,
    Field,
    Card,
    Container,
    RadioTabs,
    Button,
    Input,
    InputNumber,
)
from dataset_tools.templates import License, Industry, CVTask, AnnotationType

licensies = [
    subclass for subclass in License.__dict__.values() if isinstance(subclass, type)
]
license_values = [subclass.__name__ for subclass in licensies]
license_labels = [subclass().name for subclass in licensies]

license_items = [
    Select.Item(value, label) for value, label in zip(license_values, license_labels)
]
license_select = Select(license_items, filterable=True, placeholder="Select license")
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

release_year_input = InputNumber(value=2020, min=1900)
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

# TODO: READ GITHUB FROM APPSTATE!

download_original_url_input = Input(placeholder="Enter download original URL")
download_original_url_field = Field(
    title="Download original URL",
    description="Enter download original URL of the dataset.",
    content=download_original_url_input,
)

settings_container = Container(
    widgets=[
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

edit_tabs = RadioTabs(
    titles=["Settings", "Options"],
    contents=[settings_container, options_container],
)

apply_button = Button("Apply", icon="zmdi zmdi-check")

card = Card(
    title="3️⃣ Edit repository",
    description="Prepare settings for the dataset.",
    content=edit_tabs,
    collapsable=True,
    lock_message="Select and clone repository on step 2️⃣.",
    content_top_right=apply_button,
)
# card.lock()
# card.collapse()
