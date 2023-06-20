import os

from supervisely.app.widgets import Text, Card, Container, Button, Input, Field
import supervisely as sly

import src.globals as g
import src.ui.edit as edit

from git import Repo

repo_url_input = Input(
    placeholder="e.g. https://github.com/dataset-ninja/some-dataset", minlength=34
)
repo_url_field = Field(
    content=repo_url_input,
    title="Repository URL",
    description="Enter full repository URL to open it in the app.",
)

bad_input_text = Text("Incorrect repo URL was entered.", "warning")
bad_input_text.hide()
lock_button = Button("Lock", icon="zmdi zmdi-lock-outline")
unlock_button = Button("Unlock", icon="zmdi zmdi-lock-open")
unlock_button.hide()


card = Card(
    title="2️⃣ Repository",
    description="Select repository to edit.",
    content=Container(widgets=[repo_url_field, bad_input_text, lock_button]),
    content_top_right=unlock_button,
    collapsable=True,
    lock_message="The repository is selected and locked.",
)


@lock_button.click
def lock():
    bad_input_text.hide()
    repo_url = repo_url_input.get_value()
    lock_button.text = "Cloning..."

    try:
        repo_name = repo_url.split("/")[-1].split(".")[0]
        git_url = f"{repo_url.split('.com/')[-1]}.git"
        ssh_url = f"git@github.com:{git_url}"

        local_repo_path = os.path.join(g.REPOS_DIR, repo_name)
        sly.fs.mkdir(local_repo_path, remove_content_if_exists=True)

        repo = Repo.clone_from(ssh_url, local_repo_path)

        sly.logger.info(f"Cloned repo {repo_url} to {local_repo_path}.")

    except Exception as e:
        sly.logger.error(f"Failed to clone repo {repo_url}. Error: {e}.")
        sly.app.show_dialog(
            title="Error while cloning repository",
            description=(
                "Something went wrong while cloning repository. Please, ensure that you entered correct "
                "repository URL, SSH key is added to your GitHub account and you have access to the repository."
            ),
            status="error",
        )
        bad_input_text.show()
        return

    repo_settings_py = os.path.join(local_repo_path, "src", "settings.py")
    if not os.path.exists(repo_settings_py):
        sly.logger.error(
            "Failed to find settings.py in the src dir o the repository. Please, ensure that you have correct repository structure."
        )
        sly.app.show_dialog(
            title="The repo doesn't contains src/settings.py",
            description=(
                "Failed to find settings.py in the src dir of the repository. Please, ensure that you have correct repository structure."
            ),
            status="error",
        )
        bad_input_text.show()
        return

    unlock_button.show()
    lock_button.hide()
    lock_button.text = "Lock"

    g.AppState.repo_url = repo_url
    g.AppState.repo_name = repo_name
    g.AppState.git_url = git_url
    g.AppState.ssh_url = ssh_url
    g.AppState.local_repo_path = local_repo_path
    g.AppState.repo = repo

    read_settings()
    edit.load_settings()

    card.lock()

    edit.card.unlock()
    edit.card.uncollapse()


def read_settings():
    settings = {}
    settings_py_path = os.path.join(g.AppState.local_repo_path, "src", "settings.py")

    with open(settings_py_path, "r") as file:
        for line in file:
            for field in g.AppState.required_fields:
                if line.startswith(f"{field}:"):
                    settings[field] = line.split("=")[1].strip().strip('"')

            for field in g.AppState.optional_fields:
                if line.startswith(field):
                    settings[field] = line.split("=")[1].strip().strip('"')

    sly.logger.info(f"Read current settings: {settings}.")

    g.AppState.settings = settings


@unlock_button.click
def unlock():
    unlock_button.hide()
    lock_button.show()
    bad_input_text.hide()

    g.AppState.clear()

    edit.card.lock()
    edit.card.collapse()

    card.unlock()
    card.uncollapse()
