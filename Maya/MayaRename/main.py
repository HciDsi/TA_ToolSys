import maya.cmds as cmds

def rename_gui():
    gui_name = "RenameTool"
    gui_title = "Rename"

    try:
        cmds.deleteUI(gui_name)
    except:
        pass

    cmds.window(gui_name, t = gui_title)

    cmds.columnLayout( adj = True)

    cmds.rowLayout(numberOfColumns = 2, columnWidth2 = (120, 60), adj = 2)
    cmds.text("Name:",w = 90)
    cmds.textField("NameInput")
    cmds.setParent('..')

    cmds.rowLayout(numberOfColumns = 3, columnWidth3 = (120, 150, 60), adj = 2)
    cmds.text("Strating&Padding")
    cmds.textField("Padding" , tx = "1,3")
    cmds.checkBox("Strip")
    cmds.setParent("..")

    cmds.button("Rename",h = 60, c = "raname_ativit()")

    cmds.window(gui_name,e = True, h = 1, w = 1)
    cmds.showWindow()

def raname_ativit():
    list_obj = cmds.ls(sl = True)
    str_input = cmds.textField("NameInput", q = True, tx = True)
    str_padding = cmds.textField("Padding", q = True, tx = True)
    str_starting,str_padding = str_padding.split(",")

    str_number = str_starting.zfill(int(str_padding))
    print(str_input + "__")

    for name_l in list_obj:
        name_s = name_l
        if("|" in name_l):
            name_s = name_l.split("|")[1]

        t_input = str_input;
        t_number = str_number;

        if("," in t_input):
            a1, a2 = t_input.split(',')
            if(a1 in name_s):
                n_name = name_s.replace(a1, a2)
                cmds.rename(name_s, n_name)
        
        else:
            cmds.rename(name_s, str_input + str_number)

        str_number = str(int(str_number) + 1).zfill(int(str_padding))

rename_gui()

# for i in range(5):
#     cmds.polySphere(r = 3)