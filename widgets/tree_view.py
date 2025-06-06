import typing

from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtCore as QtCore
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QMenu
from lib.BattalionXMLLib import BattalionLevelFile, BattalionObject
from collections import OrderedDict
from PyQt6.QtGui import QClipboard, QGuiApplication, QAction
from itertools import chain


class BolHeader(QTreeWidgetItem):
    def __init__(self):
        super().__init__()
        self.setText(0, "BOL Header")


class ObjectGroup(QTreeWidgetItem):
    def __init__(self, name, parent=None, bound_to=None):
        if parent is None:
            super().__init__()
        else:
            super().__init__(parent)
        self.setText(0, name)
        self.bound_to = bound_to

    def remove_children(self):
        self.takeChildren()


class ObjectGroupObjects(ObjectGroup):
    def sort(self):
        """items = []
        for i in range(self.childCount()):
            items.append(self.takeChild(0))

        items.sort(key=lambda x: x.bound_to.objectid)

        for item in items:
            self.addChild(item)"""
        self.sortChildren(0, 0)


# Groups
class EnemyPointGroup(ObjectGroup):
    def __init__(self, parent, bound_to):
        super().__init__("Enemy point group", parent=parent, bound_to=bound_to)
        self.update_name()

    def update_name(self):
        index = self.parent().indexOfChild(self)
        self.setText(0, "Enemy point group {0} (ID: {1})".format(index, self.bound_to.id))


class CheckpointGroup(ObjectGroup):
    def __init__(self, parent, bound_to):
        super().__init__("Checkpoint group", parent=parent, bound_to=bound_to)
        self.update_name()

    def update_name(self):
        index = self.parent().indexOfChild(self)
        self.setText(0, "Checkpoint group {0}".format(index))


class ObjectPointGroup(ObjectGroup):
    def __init__(self, parent, bound_to):
        super().__init__("Object point group", parent=parent, bound_to=bound_to)
        self.update_name()

    def update_name(self):
        index = self.parent().indexOfChild(self)
        self.setText(0, "Object point group {0}".format(index))


# Entries in groups or entries without groups
class NamedItem(QTreeWidgetItem):
    def __init__(self, parent, name, bound_to, index=None):
        super().__init__(parent)
        self.setText(0, name)
        self.setText(1, bound_to.extra_detail_name())
        self.bound_to = bound_to
        self.index = index
        self.update_name()

    def update_name(self):
        self.setText(0, self.bound_to.name)
        self.setText(1, self.bound_to.extra_detail_name())

    def update_details_unused(self):
        self.setText(1, self.bound_to.extra_detail_name()+"(Unused)")


class EnemyRoutePoint(NamedItem):
    def update_name(self):
        group_item = self.parent()
        group = group_item.bound_to
        offset = 0
        groups_item = group_item.parent()

        for i in range(groups_item.childCount()):
            other_group_item = groups_item.child(i)
            if other_group_item == group_item:
                break
            else:
                #print("Hmmm,", other_group_item.text(0), len(other_group_item.bound_to.points), offset)
                group_object = other_group_item.bound_to
                offset += len(group_object.points)


        index = group.points.index(self.bound_to)

        self.setText(0, "Enemy Route Point {0} (pos={1})".format(index+offset, index))


class Checkpoint(NamedItem):
    def update_name(self):
        offset = 0
        group_item = self.parent()
        groups_item = group_item.parent()
        for i in range(groups_item.childCount()):
            other_group_item = groups_item.child(i)
            if other_group_item == group_item:
                break
            else:
                print("Hmmm,",other_group_item.text(0), len(other_group_item.bound_to.points), offset)
                group_object = other_group_item.bound_to
                offset += len(group_object.points)

        group = group_item.bound_to

        index = group.points.index(self.bound_to)

        self.setText(0, "Checkpoint {0} (pos={1})".format(index+1+offset, index))


class ObjectRoutePoint(NamedItem):
    def update_name(self):
        group_item = self.parent()
        group = group_item.bound_to

        index = group.points.index(self.bound_to)

        self.setText(0, "Object Route Point {0}".format(index))


class ObjectEntry(NamedItem):
    def __init__(self, parent, name, bound_to):
        super().__init__(parent, name, bound_to)
        bound_to.widget = self

    def update_name(self):
        self.setText(0, get_full_name(self.bound_to.objectid))

    def __lt__(self, other):
        return self.bound_to.objectid < other.bound_to.objectid


class KartpointEntry(NamedItem):
    def update_name(self):
        playerid = self.bound_to.playerid
        if playerid == 0xFF:
            result = "All"
        else:
            result = "ID:{0}".format(playerid)
        self.setText(0, "Kart Start Point {0}".format(result))


class AreaEntry(NamedItem):
    def update_name(self):
        self.setText(0, "Area (Type: {0})".format(self.bound_to.area_type))


class CameraEntry(NamedItem):
    def update_name(self):
        self.setText(0, "Camera {0} (Type: {1})".format(self.index, self.bound_to.camtype))


class RespawnEntry(NamedItem):
    def update_name(self):
        self.setText(0, "Respawn Point (ID: {0})".format(self.bound_to.respawn_id))


class LightParamEntry(NamedItem):
    def update_name(self):
        self.setText(0, "LightParam {0}".format(self.index))


class MGEntry(NamedItem):
    def update_name(self):
        self.setText(0, "MG")


class ReadOnlyDelegate(QtWidgets.QItemDelegate):
    def createEditor(self, parent, option, index) -> typing.Optional[QtWidgets.QWidget]:
        editor = super().createEditor(parent, option, index)
        editor.setReadOnly(True)
        return editor


class LevelDataTreeView(QTreeWidget):
    select_all = pyqtSignal(ObjectGroup)
    reverse = pyqtSignal(ObjectGroup)
    duplicate = pyqtSignal(ObjectGroup)
    split = pyqtSignal(EnemyPointGroup, EnemyRoutePoint)
    split_checkpoint = pyqtSignal(CheckpointGroup, Checkpoint)

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.setMaximumWidth(600)
        self.resize(200, self.height())
        self.setColumnCount(2)
        self.setHeaderLabels(["XML Objects", "Details"])

        self.setItemDelegate(ReadOnlyDelegate(self))
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.SelectedClicked)

        #self.bolheader = BolHeader()
        #self.addTopLevelItem(self.bolheader)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.run_context_menu)
        self.expanded.connect(self.resizeheader)

        self.units = None
        self.components = None
        self.mapobjects = None
        self.scenery = None
        self.assets = None
        self.hud = None
        self.scripts = None
        self.effects = None
        self.preload = None
        self.other: ObjectGroup = None

        self.setup_groups()

    def setup_groups(self):
        self.units = self._add_group("Units")
        self.components = self._add_group("Components")
        self.mapobjects = self._add_group("Map")
        self.scenery = self._add_group("Scenery")
        self.assets = self._add_group("Assets")
        self.hud = self._add_group("HUD")
        self.scripts = self._add_group("Scripts")
        self.effects = self._add_group("Effects")
        self.preload = self._add_group("Preload")
        self.other: ObjectGroup = self._add_group("Other")

        categorydistributionreverse = {
            "mapobjects":
                ["cWaypoint", "cCamera", "cCameraBase", "cObjectiveMarker", "cMapZone",
                 "cObjective", "cObjectiveMarkerBase", "cCoastZone", "cDamageZone", "cNogoHintZone"],
            "assets":
                ["cSoundBase", "cSprite", "cTextureResource", "sSampleResource", "sSpriteBasetype",
                 "cNodeHierarchyResource", "cAnimationResource", "cGroundVehicleEngineSoundBase",
                 "cGroundVehiclePhysicsBase", "cGroundVehicleSoundBase", "cPanelSprites"],
            "units":
                ["cAirVehicle", "cGroundVehicle", "cTroop", "cGroundVehicleBase", "sTroopBase", "sAirVehicleBase",
                 "cWaterVehicle", "cWaterVehicleBase"],
            "components":
                ["cAdvancedWeaponBase", "cAirVehicleEngineSoundBase", "cAirVehiclePhysicsBase", "cAirVehicleSoundBase",
                 "cProjectileSoundBase", "cTroopAnimationSet", "cTroopVoiceManagerBase", "cTroopVoiceMessageBase",
                 "cWaterVehiclePhysicsBase", "cWaterVehicleSoundBase", "cWeaponSoundBase", "sDestroyBase", "sExplodeBase",
                 "sWeaponBase", "cFlightData", "cSeatBase", "cImpactBase", "cImpactTableBase",
                 "cImpactTableTaggedEffectBase", "cIncidentalBase"],
            "hud":
                ["cHUD", "cHUDSoundBlock", "cHUDTutorial", "cHUDVariables"],
            "scenery":
                ["cBuilding", "cBuildingImpBase", "cDestroyableObject", "cSceneryCluster", "sSceneryClusterBase",
                 "cCapturePoint", "cCapturePointBase", "cMorphingBuilding", "cStrategicInstallation",
                 "cPickupReflected", "sPickupBase"],
            "scripts":
                ["cGlobalScriptEntity", "cGameScriptResource", "cInitialisationScriptEntity"],
            "effects":
                ["cAnimationTriggeredEffect", "cAnimationTriggeredEffectChainItemGroundImpact",
                 "cAnimationTriggeredEffectChainItemSound", "cAnimationTriggeredEffectChainItemTequilaEffect",
                 "cAnimationTriggeredEffectManager", "cTequilaEffectResource", "cSimpleTequilaTaggedEffectBase",
                 "cTerrainParticleGeneratorBase"],
            "preload":
                ['cPhysicsMaterial', 'cPhysicsGlobalParams', 'cTerrainParticleAnimationBase', 'cWorldFreeListSizeLoader',
                 'cPhysicsGlobalParamSet', 'cDamageArmourBonus', 'cBailOutData', 'cLevelSettings']
        }

        self._categorydistribution = {}
        for k, v in categorydistributionreverse.items():
            for name in v:
                self._categorydistribution[name] = getattr(self, k)

    def get_top_categories(self):
        return (self.other, self.units, self.components, self.mapobjects, self.scenery,
                        self.assets, self.hud, self.scripts, self.effects, self.preload)

    def resizeheader(self):
        self.resizeColumnToContents(0)

    def run_context_menu(self, pos):
        item = self.itemAt(pos)
        print(item.text(0))
        QGuiApplication.clipboard().setText("\"{0}\"".format(item.text(0)))
        """if isinstance(item, (EnemyRoutePoint, )):
            context_menu = QMenu(self)
            split_action = QAction("Split Group At", self)

            def emit_current_split():
                item = self.itemAt(pos)
                group_item = item.parent()
                self.split.emit(group_item, item)

            split_action.triggered.connect(emit_current_split)

            context_menu.addAction(split_action)
            context_menu.exec(self.mapToGlobal(pos))
            context_menu.destroy()
            del context_menu
        elif isinstance(item, (Checkpoint, )):
            context_menu = QMenu(self)
            split_action = QAction("Split Group At", self)

            def emit_current_split():
                item = self.itemAt(pos)
                group_item = item.parent()
                self.split_checkpoint.emit(group_item, item)

            split_action.triggered.connect(emit_current_split)

            context_menu.addAction(split_action)
            context_menu.exec(self.mapToGlobal(pos))
            context_menu.destroy()
            del context_menu
        elif isinstance(item, (EnemyPointGroup, ObjectPointGroup, CheckpointGroup)):
            context_menu = QMenu(self)
            select_all_action = QAction("Select All", self)
            reverse_action = QAction("Reverse", self)

            def emit_current_selectall():
                item = self.itemAt(pos)
                self.select_all.emit(item)

            def emit_current_reverse():
                item = self.itemAt(pos)
                self.reverse.emit(item)



            select_all_action.triggered.connect(emit_current_selectall)
            reverse_action.triggered.connect(emit_current_reverse)

            context_menu.addAction(select_all_action)
            context_menu.addAction(reverse_action)

            if isinstance(item, EnemyPointGroup):
                def emit_current_duplicate():
                    item = self.itemAt(pos)
                    self.duplicate.emit(item)

                duplicate_action = QAction("Duplicate", self)
                duplicate_action.triggered.connect(emit_current_duplicate)
                context_menu.addAction(duplicate_action)

            context_menu.exec(self.mapToGlobal(pos))
            context_menu.destroy()
            del context_menu"""

    def _add_group(self, name, customgroup=None):
        if customgroup is None:
            group = ObjectGroup(name)
        else:
            group = customgroup(name)
        self.addTopLevelItem(group)
        return group

    def reset(self):
        for section in (self.other, self.units, self.components, self.mapobjects, self.scenery,
                        self.assets, self.hud, self.scripts, self.effects, self.preload):
            section.remove_children()

    def choose_category(self, objecttype):
        if objecttype in self._categorydistribution:
            return self._categorydistribution[objecttype]
        else:
            return self.other

    def set_objects(self, leveldata: BattalionLevelFile, preload: BattalionLevelFile, remember_position=False):
        expanded = {}
        scrollvalue = self.verticalScrollBar().value()

        if remember_position:
            model = self.model()
            for i in range(model.rowCount(self.rootIndex())):
                index = model.index(i, 0)
                item = self.itemFromIndex(index)
                if item.isExpanded():
                    expanded[item.text(0)] = True
                childmodel = index.model()
                for j in range(model.rowCount(index)):
                    childindex = childmodel.index(j, 0, index)
                    item2 = self.itemFromIndex(childindex)
                    if item2.isExpanded():
                        expanded[item2.text(0)] = True

                #QtWidgets.QApplication.processEvents()

        self.reset()

        extra_categories = {}

        levelsettings = None
        for obj in preload.objects.values():
            if obj.type == "cLevelSettings":
                levelsettings = obj
                break
        sorteditems = []
        for objectid, object in chain(leveldata.objects.items(), preload.objects.items()):
            sorteditems.append((object.name, object))
        sorteditems.sort(key=lambda x: x[0])

        for name, object in sorteditems:
            object: BattalionObject
            objecttype = object.type
            if objecttype not in extra_categories:
                extra_categories[objecttype] = ObjectGroup(objecttype)
                #print(objecttype)

            parent = extra_categories[objecttype]
            name = object.name
            unused = False
            if levelsettings is not None:
                if object.type == "cDamageArmourBonus":
                    if levelsettings.mDamageArmourBonus.id != object.id:
                        unused = True

            item = NamedItem(parent, name, object)
            itemflag = QtCore.Qt.ItemFlag
            item.setFlags(itemflag.ItemIsEnabled | itemflag.ItemIsSelectable | itemflag.ItemIsEditable)

            if unused:
                item.update_details_unused()

        for categoryname in sorted(extra_categories.keys()):
            category = extra_categories[categoryname]
            target = self.choose_category(categoryname)
            target.addChild(category)

        if remember_position:
            model = self.model()
            for i in range(model.rowCount(self.rootIndex())):
                index = model.index(i, 0)
                item = self.itemFromIndex(index)
                if item.text(0) in expanded:
                    item.setExpanded(True)
                childmodel = index.model()
                for j in range(model.rowCount(index)):
                    childindex = childmodel.index(j, 0, index)
                    item2 = self.itemFromIndex(childindex)
                    if item2.text(0) in expanded:
                        item2.setExpanded(True)
            self.verticalScrollBar().setValue(scrollvalue)

    def updatenames(self):
        levelsettings = None
        damagesettings = []

        category: QTreeWidgetItem


        for category in (self.units, self.components, self.mapobjects, self.scenery, self.assets, self.hud,
                         self.scripts, self.effects, self.preload, self.other):
            for i in range(category.childCount()):
                subcategory = category.child(i)
                for j in range(subcategory.childCount()):
                    item = subcategory.child(j)
                    if item.bound_to.type == "cLevelSettings":
                        levelsettings = item.bound_to
                    elif item.bound_to.type == "cDamageArmourBonus":
                        damagesettings.append(item)
                    item.update_name()
        
        if levelsettings is not None:
            for item in damagesettings:
                if item.bound_to.id != levelsettings.mDamageArmourBonus.id:
                    item.update_details_unused()

    def sort_objects(self):
        self.objects.sort()
        """items = []
        for i in range(self.objects.childCount()):
            items.append(self.objects.takeChild(0))

        items.sort(key=lambda x: x.bound_to.objectid)

        for item in items:
            self.objects.addChild(item)"""