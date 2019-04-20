from zUtils.ui import getIconPath


__all__ = [
    "SELECT_ICON",
    "CLOSE_ICON",
    "MESH_ICON",
    "BRUSH_ICON",
    "LINE_ICON",
    "ZIVA_ICON",
    "ARROW_ICONS"
]


SELECT_ICON = ":/redSelect.png"
CLOSE_ICON = ":/closeTabButton.png"
MESH_ICON = ":/polyMesh.png"
BRUSH_ICON = ":/brush.png"
LINE_ICON = ":/pickLineComp.png"
ZIVA_ICON = getIconPath("zivaLogo.png")
ARROW_ICONS = {True: ":/arrowDown.png", False: ":/arrowRight.png"}
