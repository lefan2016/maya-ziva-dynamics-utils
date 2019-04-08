from maya import cmds, mel


# ----------------------------------------------------------------------------


SHELF_NAME = "ZivaUtils"
SHELF_TOOLS = [
    {
        "label": "automaticallyNameZivaNodes",
        "command": "import zUtils.naming;zUtils.naming.autoNameSelected()",
        "annotation": "Automatically name selected Ziva nodes",
        "image1": ":/zivaLogo.png",
        "sourceType": "python",
        "imageOverlayLabel": "AUTO\nNAME",
        "overlayLabelColor": [0, 0, 0],
        "overlayLabelBackColor": [0, 0, 0, 0],
    },
]


# ----------------------------------------------------------------------------


def shelf():
    """
    Add a new shelf in Maya with all the tools that are provided in the
    SHELF_TOOLS variable. If a tab already exist new buttons that weren't
    registered yet will be added to the shelf.
    """
    # get top shelf
    gShelfTopLevel = mel.eval("$tmpVar=$gShelfTopLevel")

    # get top shelf names
    shelves = cmds.tabLayout(gShelfTopLevel, query=1, ca=1)

    # delete shelf if it exists
    if SHELF_NAME in shelves:
        cmds.deleteUI(SHELF_NAME)

    # create shelf
    cmds.shelfLayout(SHELF_NAME, parent=gShelfTopLevel)

    # add modules
    for tool in SHELF_TOOLS:
        if tool.get("image1"):
            cmds.shelfButton(style="iconOnly", parent=SHELF_NAME, **tool)
        else:
            cmds.shelfButton(style="textOnly", parent=SHELF_NAME, **tool)
