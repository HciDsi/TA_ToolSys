import sys
import time
import datetime

import maya.mel as mel
import maya.cmds as cmds
import os
import json

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from moviepy.editor import VideoFileClip, ImageSequenceClip, concatenate_videoclips
from collections import defaultdict

class maya_vision(object):

    def __init__(self, stdio_list, project_list):
        if hasattr(self, 'v_gui'):
            return

        self.fontsize_list = ['small', "large"]
        self.frame_rate_list = ['5', '16', '24', '30', '45']
        self.studio_list = stdio_list
        self.project_list = project_list

        self.required_attrs = ['translateX', 'translateY', 'translateZ',
                               'rotateX', 'rotateY', 'rotateZ',
                               'scaleX', 'scaleY', 'scaleZ',
                               'rotatePivotX', 'rotatePivotY', 'rotatePivotZ']

        self.v_gui = QWidget()
        self.setupUi(self.v_gui)
        self.initHUB()

    def setupUi(self, Form):

        if not Form.objectName():
            Form.setObjectName(u"Maya Vision")
        Form.resize(500, 450)

        # 创建主布局
        self.mainLayout = QWidget(Form)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setGeometry(QRect(50, 20, 400, 400))

        # 创建一个QVBoxLayout作为主布局
        self.verticalLayout = QVBoxLayout(self.mainLayout)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        #HUD相关控件
        self.HUDSetLayout = QVBoxLayout(self.mainLayout)
        self.HUDSetLayout.setObjectName(u"HUDSetLayout")
        self.HUDSetLayout.setContentsMargins(0, 0, 0, 0)

        # 创建Studio布局
        self.StudioLayout = QHBoxLayout()
        self.StudioLayout.setObjectName(u"StudioLayout")

        self.studio = QLabel("Studio:")
        self.studio.setObjectName(u"studio")
        self.StudioLayout.addWidget(self.studio, 1)

        self.studio_in = QComboBox(self.mainLayout)
        self.studio_in.addItems(self.studio_list)
        self.studio_in.setObjectName(u"studio_in")
        self.StudioLayout.addWidget(self.studio_in, 3)

        # 将Studio添加到HUD布局
        self.HUDSetLayout.addLayout(self.StudioLayout)

        # 创建Project布局
        self.ProjectLayout = QHBoxLayout()
        self.ProjectLayout.setObjectName(u"ProjectLayout")

        self.project = QLabel("Project:")
        self.project.setObjectName(u"project")
        self.ProjectLayout.addWidget(self.project, 1)

        self.project_in = QComboBox(self.mainLayout)
        self.project_in.addItems(self.project_list)
        self.project_in.setObjectName(u"project_in")
        self.ProjectLayout.addWidget(self.project_in, 3)

        # 将Project添加到HUD布局
        self.HUDSetLayout.addLayout(self.ProjectLayout)

        # 创建Artist布局
        self.ArtistLayout = QHBoxLayout()
        self.ArtistLayout.setObjectName(u"ArtistLayout")

        self.artist = QLabel("Artist:")
        self.artist.setObjectName(u"artist")
        self.ArtistLayout.addWidget(self.artist, 1)

        self.artist_in = QLineEdit(self.mainLayout)
        self.artist_in.setObjectName(u"artist_in")
        self.ArtistLayout.addWidget(self.artist_in, 3)

        # 将Artist布局添加到HUD布局
        self.HUDSetLayout.addLayout(self.ArtistLayout)

        # 创建Fontset布局
        self.FontsetLayout = QHBoxLayout()
        self.FontsetLayout.setObjectName(u"FontsetLayout")

        self.fontsize = QLabel("Font Size:")
        self.fontsize.setObjectName(u"fontsize")
        self.FontsetLayout.addWidget(self.fontsize, 1)

        self.fontsize_in = QComboBox(self.mainLayout)
        self.fontsize_in.addItems(self.fontsize_list)
        self.fontsize_in.setObjectName(u"fontsize_in")
        self.fontsize_in.setCurrentIndex(1)
        self.fontsize_in.currentIndexChanged.connect(self.setHUDFontSize)
        self.FontsetLayout.addWidget(self.fontsize_in, 3)

        # 将FontsetLayout添加到HUD布局
        self.HUDSetLayout.addLayout(self.FontsetLayout)

        # 创建Camera布局
        self.CamerasLayout = QHBoxLayout()
        self.CamerasLayout.setObjectName(u"CamerasLayout")

        self.curr_camera = QLabel("Current Camera:")

        self.curr_camera.setObjectName(u"curr_camera")
        self.CamerasLayout.addWidget(self.curr_camera, 1)

        self.cameras = QComboBox(self.mainLayout)
        self.cameras.setObjectName(u"cameras")
        self.updateCameraList()
        curr_camera = self.getCurrentCamera()[1:]
        if curr_camera:
            index = self.cameras.findText(curr_camera)
            if index != -1:
                self.cameras.setCurrentIndex(index)
        self.cameras.currentIndexChanged.connect(self.setCurrentCamera)
        self.CamerasLayout.addWidget(self.cameras, 2)

        # 将Cameras布局添加到Record布局
        self.HUDSetLayout.addLayout(self.CamerasLayout)

        # 创建Framerange布局
        self.FramerageLayout = QHBoxLayout()
        self.FramerageLayout.setObjectName(u"FramerageLayout")

        self.framerange = QLabel("Frame Range:")
        self.framerange.setObjectName(u"framerange")
        self.FramerageLayout.addWidget(self.framerange, 1)

        self.Framerage = QHBoxLayout()
        self.Framerage.setObjectName(u"Frame Rage")
        self.start_frame = QLineEdit('1')
        self.start_frame.setObjectName(u"start_frame")
        self.start_frame.setValidator(QIntValidator())
        self.Framerage.addWidget(self.start_frame, 2)
        self.Framerage.addWidget(QLabel("............"), 1)
        self.end_frame = QLineEdit('24')
        self.end_frame.setObjectName(u"end_frame")
        self.end_frame.setValidator(QIntValidator())
        self.Framerage.addWidget(self.end_frame, 2)
        self.FramerageLayout.addLayout(self.Framerage, 3)

        # 将Framerange添加到HUDSetLayout布局
        self.HUDSetLayout.addLayout(self.FramerageLayout)

        self.verticalLayout.addLayout(self.HUDSetLayout)

        # Record相关控件
        self.RecordLayout = QVBoxLayout(self.mainLayout)
        self.RecordLayout.setObjectName("RecordLayout")
        self.RecordLayout.setContentsMargins(0, 0, 0, 0)

        # 创建Filelocation布局
        self.FilelocationLayout = QHBoxLayout()
        self.FilelocationLayout.setObjectName(u"FilelocationLayout")

        self.output_location = QLabel("Output Location:")
        self.output_location.setObjectName(u"output_location")
        self.FilelocationLayout.addWidget(self.output_location, 2)

        self.file_path = QLineEdit(self.mainLayout)
        self.file_path.setObjectName(u"file_path")
        self.FilelocationLayout.addWidget(self.file_path, 4)

        self.file_button = QPushButton("...")
        self.file_button.setObjectName(u"pushButton")
        self.file_button.clicked.connect(self.selectFile)
        self.FilelocationLayout.addWidget(self.file_button, 1)

        # 将Filelocation布局添加到Record布局
        self.RecordLayout.addLayout(self.FilelocationLayout)

        # 在Record布局中添加一个QPushButton
        self.record = QPushButton("Record")
        self.record.setObjectName(u"Record")
        self.record.clicked.connect(self.captureAnimation)
        self.RecordLayout.addWidget(self.record)

        self.verticalLayout.addLayout(self.RecordLayout)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    #初始化HUB
    def initHUB(self):
        # 清除默认HUD
        HUDlist = cmds.headsUpDisplay(listHeadsUpDisplays=True)
        try:
            for h in HUDlist:
                cmds.headsUpDisplay(h, rem=True)
        except:
            pass

        # 创建HUD元素
        cmds.headsUpDisplay('Studio',
                            section=0, block=0,
                            blockSize='large',
                            label='Studio',
                            dataFontSize='large',
                            command=lambda: self.studio_in.currentText(),
                            event='idle')
        cmds.headsUpDisplay('Project',
                            section=0, block=1,
                            blockSize='large',
                            label='Project',
                            dataFontSize='small',
                            command=lambda: self.project_in.currentText(),
                            event='idle')
        cmds.headsUpDisplay('Artist',
                            section=0, block=2,
                            blockSize='large',
                            label='Artist',
                            dataFontSize='large',
                            command=lambda: self.artist_in.text(),
                            event='idle')

        cmds.headsUpDisplay('HUDFrameRange',
                            section=4, block=0,
                            blockSize='large',
                            label='Frame Range',
                            dataFontSize='large',
                            command=lambda: self.start_frame.text() + ' to ' + self.end_frame.text(),  # 这里使用lambda来动态获取帧速率
                            event='idle')
        cmds.headsUpDisplay('HUDFrameRate',
                            section=4, block=1,
                            blockSize='large',
                            label='Frame Rate',
                            dataFontSize='large',
                            command=lambda: '5' + ' fps',
                            event='idle')
        cmds.headsUpDisplay('HUDCurrentFrame',
                            section=4, block=2,
                            blockSize='large',
                            label='Current Frame',
                            dataFontSize='large',
                            preset = 'currentFrame')

        cmds.headsUpDisplay('CurrentCamera',
                            section=5, block=0,
                            blockSize='large',
                            label='Current Camera',
                            dataFontSize='large',
                            command=lambda: self.cameras.currentText(),
                            event='idle')

        cmds.headsUpDisplay('Date',
                            section=9, block=0,
                            blockSize='large',
                            label='Date',
                            dataFontSize='large',
                            command=lambda:  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') ,
                            event='idle')

    #使用拍屏方法
    def captureAnimation(self):

        start_frame = int(self.start_frame.text())
        end_frame = int(self.end_frame.text())
        original_video = 'output_video.mp4'
        output_dir = self.file_path.text()

        if not os.path.exists(output_dir + '/' + original_video):

            current_data = self.getAnimationDataInRange(start_frame, end_frame)
            self.saveAnimationData(output_dir + '/last_animation_data.json', current_data)
            self.captureFrames([frame for frame in range(start_frame, end_frame + 1)], output_dir)

            self.mergeVideos(original_video, output_dir)

        else:

            t = time.perf_counter()
            current_data = self.getAnimationDataInRange(start_frame, end_frame)
            last_data = self.loadAnimationData(output_dir + '/last_animation_data.json')
            self.saveAnimationData(output_dir + '/last_animation_data.json', current_data)
            modified_frames = self.compareAnimationData(current_data, last_data, start_frame, end_frame)
            # 输出有变化的帧
            print("Modified frames:", modified_frames)
            # 筛选出在起始帧和终止帧之间的修改帧
            filtered_frames = [frame for frame in modified_frames if start_frame <= frame <= end_frame]
            print('MayaVision所用时间：' + f'coast:{time.perf_counter() - t:.8f}s')
            # 拍屏有变化的帧
            self.captureFrames(filtered_frames, output_dir)

            self.mergeVideos(original_video, output_dir)

    # 设置各个控件的文本
    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("MayaVision", u"MayaVision", None))

    # 更新HUD参数
    def setHUDFontSize(self):

        hud_elements = cmds.headsUpDisplay(listHeadsUpDisplays=True)

        for hud_name in hud_elements:
            cmds.headsUpDisplay(hud_name, edit=True, dataFontSize=self.fontsize_in.currentText(), labelFontSize=self.fontsize_in.currentText())

    def updateCameraList(self):

        cameras = cmds.ls(type='camera')
        cameras = cmds.listRelatives(cameras, parent=True)
        self.cameras.clear()
        self.cameras.addItems(cameras)

    def getCurrentCamera(self):

        model_panel = cmds.getPanel(withFocus=True)

        if cmds.getPanel(typeOf=model_panel) == 'modelPanel':
            return cmds.modelEditor(model_panel, query=True, camera=True)

        model_panels = cmds.getPanel(type='modelPanel')
        for panel in model_panels:
            if cmds.modelPanel(panel, query=True, camera=True):
                return cmds.modelEditor(panel, query=True, camera=True)
        return None

    def setCurrentCamera(self):

        selected_camera = self.cameras.currentText()
        model_panels = cmds.getPanel(type='modelPanel')
        for panel in model_panels:
            cmds.modelEditor(panel, edit=True, camera=selected_camera)

    # 获取输出文件夹
    def selectFile(self):
        file_path = QFileDialog.getExistingDirectory(self.file_button, "选择文件夹")

        if file_path:
            self.file_path.setText(file_path)

    # 获取当前选定帧范围内所有动画数据
    def getAnimationDataInRange(self, start_frame, end_frame):
        # 使用 defaultdict 创建一个默认值为 dict 的字典，用于存储动画数据
        animation_data = defaultdict(dict)

        # 获取场景中所有变换节点（transform），并缓存其可关键属性
        scene_objects = cmds.ls(type='transform')
        obj_attrs = {obj: [attr for attr in (cmds.listAttr(obj, keyable=True) or []) if attr in self.required_attrs]
                     for obj in scene_objects}

        # 遍历指定范围内的每一帧
        for frame in range(start_frame, end_frame + 1):
            # 设置当前时间到指定帧
            cmds.currentTime(frame, edit=True)
            # 初始化当前帧的数据字典
            frame_data = {}

            # 遍历每个对象及其属性
            for obj, attrs in obj_attrs.items():
                # 获取每个属性在当前帧的值
                obj_data = {attr: cmds.getAttr(f"{obj}.{attr}") for attr in attrs}
                # 如果当前对象有记录的属性数据，将其添加到当前帧数据中
                if obj_data:
                    frame_data[obj] = obj_data

            # 将当前帧的数据存储到总的动画数据字典中
            animation_data[frame] = frame_data

        # 返回包含指定范围内每一帧动画数据的字典
        return dict(animation_data)

    # 比较当前帧与上一次拍屏之间是否存在动画数据变动
    def compareAnimationData(self, current_data, last_data, start_frame, end_frame):
        # 创建一个空集合来存储修改过的帧
        modified_frames = set()

        # 遍历指定范围内的每一帧
        for frame in range(start_frame, end_frame + 1):
            # 获取当前帧的动画数据，如果不存在则返回空字典
            current_frame_data = current_data.get(frame, {})
            # 获取上一次的动画数据，如果不存在则返回空字典
            last_frame_data = last_data.get(str(frame), {})

            # 如果当前帧的动画数据与上次不相同，添加当前帧到修改过的帧集合中
            if current_frame_data != last_frame_data:
                modified_frames.add(frame)

        # 将修改过的帧集合转换为有序列表并返回
        return sorted(list(modified_frames))

    # 保存当前数据到文件
    def saveAnimationData(self, file_path, animation_data):
        with open(file_path, 'w') as f:
            json.dump(animation_data, f, indent=4)

    # 从文件加载数据
    def loadAnimationData(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            return {}

    # 拍屏
    def captureFrames(self, frames, output_dir):

        output_dir = output_dir + '/frame'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for frame in frames:

            cmds.currentTime(frame, edit=True)

            frame_path = f"{output_dir}/frame_{int(frame):04d}.png"
            # 执行playblast命令，将当前帧保存为图像文件
            cmds.playblast(
                frame=frame,
                format='image',
                quality=100,
                compression='png',
                width=1920,
                height=1080,
                completeFilename=frame_path,
                forceOverwrite=True,
                viewer=True
            )

    # 拼接新旧视频
    def mergeVideos(self, original_video, modified_frames_dir):
        modified_frames = [os.path.join(modified_frames_dir + '/frame', f) for f in
                           os.listdir(modified_frames_dir + '/frame') if f.endswith('.png')]

        if modified_frames:

            modified_clip = ImageSequenceClip(modified_frames, fps=5)

            final_clip = concatenate_videoclips([modified_clip])

            output_video_path = os.path.join(modified_frames_dir, original_video)

            print(output_video_path)
            if os.path.exists(output_video_path):
                os.remove(output_video_path)

            final_clip.write_videofile(output_video_path, codec='libx264')
        else:
            print("Failed to take the screen")



stdio_name = ["Studio1", "Studio2", "Studio3"]
project_name = ["Project1", "Project2", "Project3"]
v = maya_vision(stdio_name, project_name)
v.v_gui.show()