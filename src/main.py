import supervisely as sly

from supervisely.app.widgets import Container

import src.ui.info as info
import src.ui.repos as repos
import src.ui.edit as edit

layout = Container(widgets=[info.card, repos.card, edit.card])

app = sly.Application(layout=layout)
