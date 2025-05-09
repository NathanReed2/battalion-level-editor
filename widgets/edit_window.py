import typing
import os
import math
import json
from functools import partial
from lib.bw_types import BWMatrix, decompose, recompose
from timeit import default_timer
from widgets.editor_widgets import open_message_dialog
from builtin_plugins.plugin_feature_test import load_icon
from itertools import chain

import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtGui as QtGui
import PyQt6.QtCore as QtCore
from lib.BattalionXMLLib import BattalionObject, BattalionLevelFile
from widgets.editor_widgets import SearchBar

ICONS = {"COPY": None}


ENUMS = {
    "BW1":
        {
         "eObjtag": [
            "TAG_UNTAGGED",
            "TAG_BONE_L_FOOT",
            "TAG_BONE_R_FOOT",
            "TAG_BONE_HEAD",
            "TAG_BONE_HELMET",
            "TAG_BONE_L_HAND",
            "TAG_BONE_R_HAND",
            "TAG_BONE_JAW"
        ],
         "eMaterialLightingMode": [
             "eMATERIAL_LIGHTMODE_MODULATE",
             "eMATERIAL_LIGHTMODE_MODULATE_2X"
         ],
        "eDamageType": [
            "DAMAGE_NO_DAMAGE",
            "DAMAGE_SMALLBULLET",
            "DAMAGE_LARGEBULLET",
            "DAMAGE_ARMOURPIERCING",
            "DAMAGE_IMPACT",
            "DAMAGE_EXPLOSIVE",
            "DAMAGE_FIRE",
            "DAMAGE_CRUSHING",
            "DAMAGE_HEALING",
            "DAMAGE_REPAIR",
            "DAMAGE_PRECALCULATED",
            "DAMAGE_BIGBOMB",
            "DAMAGE_CUSTOM_1",
            "DAMAGE_CUSTOM_2"
        ],
        "eSurfaceType": [
            "INVALID_SURFACE",
            "STONE",
            "WOOD",
            "METAL",
            "FLESH",
            "WATER",
            "GRAVEL",
            "SAND",
            "SNOW",
            "MUD",
            "GRASS",
            "AIRBURST",
            "CLOTH"
        ],

        "eBindingReadType": [
            "BINDING_DEFAULT",
            "ALWAYS_ON",
            "VEHICLE_BRAKING",
            "VEHICLE_THROTTLE",
            "VEHICLE_HEADLIGHT",
            "VEHICLE_HEADLIGHT_DECAL",
            "VEHICLE_DIRT",
            "UNIT_DAMAGE",
            "AMMO_POWER",
            "VEHICLE_SPEED",
            "DAMAGEABLE_BURNING",
            "AIR_VEHICLE_CLOUD"
        ],
        "EPSChannel": [
            "PSC_INTENSITY",
            "PSC_SIZE",
            "PSC_SPEED",
            "PSC_COLOUR"
        ],
        "eWeaponSoundBaseFireTypes": [
            "WSBFT_SINGLE",
            "WSBFT_DOUBLE",
            "WSBFT_ASMANYASITTAKES"
        ],
        "eWeaponEffectiveness": [
            "WE_INEFFECTIVE",
            "WE_POOR",
            "WE_AVERAGE",
            "WE_GOOD",
            "WE_PERFECT"
        ],
        "eCameraType": [
            "eCAMTYPE_STATIC",
            "eCAMTYPE_CHASETARGET",
            "eCAMTYPE_LOOKAT",
            "eCAMTYPE_ISOMETRIC",
            "eCAMTYPE_CIRCLECAM",
            "eCAMTYPE_WAYPOINTCAM"
        ],
        "eZoneType": [
            "ZONETYPE_DEFAULT",
            "ZONETYPE_WORLDBOUNDARY",
            "ZONETYPE_MISSIONBOUNDARY",
            "ZONETYPE_NOGOAREA",
            "ZONETYPE_FORD"
        ],
        "ePickupState": [
            "PICKUP_STATE_UNSPAWNED",
            "PICKUP_STATE_ACTIVE"
        ],
        "ePickupType": [
            "PICKUP_TYPE_SECONDARY_WPN_UPGRADE",
            "PICKUP_TYPE_SECONDARY_WPN_AMMO",
            "PICKUP_TYPE_TROOP_HEALTH",
            "PICKUP_TYPE_VEHICLE_HEALTH",
            "PICKUP_TYPE_UNPICKUPABLE"
        ],
        "eAdvancedWeaponType": [
            "AW_BAZOOKA",
            "AW_FLAMETHROWER",
            "AW_MISSILE",
            "AW_CHAINGUN",
            "AW_RIFLE",
            "AW_MORTAR",
            "AW_SHOTGUN"
        ],
        "ePhase": [
            "PHASE_ATTACK",
            "PHASE_SUSTAIN",
            "PHASE_RELEASE"
        ],
        "eEffectCameraAnchorType": [
            "eEFFECT_NO_ANCHOR_CAMERA",
            "eEFFECT_ANCHOR_TO_CAMERA_POS",
            "eEFFECT_ANCHOR_TO_CAMERA_POS_DIR"
        ],
        "eArmyAllegiance": [
            "ALLEGIANCE_ALLY",
            "ALLEGIANCE_NEUTRAL",
            "ALLEGIANCE_ENEMY"
        ],
        "eSeatDisplayType": [
            "SEATDISPLAY_SOLDER_INVISIBLE",
            "SEATDISPLAY_SOLDER_HEADONLY",
            "SEATDISPLAY_SOLDER_TOSHOULDERS",
            "SEATDISPLAY_SOLDER_STANDING",
            "SEATDISPLAY_SOLDER_SITTING"
        ],
        "eCurveController": [
            "ECC_POWER",
            "ECC_SPEED"
        ],
        "eAirVehicleCurveController": [
            "EAVCC_ROTORSPEED",
            "EAVCC_SPEED"
        ],
        "eTroopVoicePriority": [
            "ETVP_CRITICAL",
            "ETVP_NORMAL",
            "ETVP_EARCANDY"
        ],
        "eAiUnitState": [
            "AI_STATE_NONE",
            "AI_STATE_UNSPAWNED",
            "AI_STATE_NORMAL",
            "AI_STATE_DYING",
            "AI_STATE_DEAD",
            "AI_STATE_PERMANENTLY_DEAD",
            "AI_STATE_IN_LIMBO"
        ],
        "eArmy": [
            "eNoArmy",
            "eWesternFrontier",
            "eXylvanian",
            "eTundranTerritories",
            "eSolarEmpire",
            "eUnderWorld",
            "eNeutral"
        ],
        "eAttackStyle": [
            "ATTACKSTYLE_FROM_DEFENSIVE_AREA",
            "ATTACKSTYLE_HUNT_AND_DESTROY"
        ],
        "eMoveStyle": [
            "MOVESTYLE_RESPOND_TO_ATTACKS",
            "MOVESTYLE_ATTACK_ON_SIGHT"
        ],
        "eHUDs": [
            "PLAYER_ONE_HUD",
            "PLAYER_TWO_HUD"
        ],
        "eCommandIconType": [
            "ICON_NO_ICON",
            "ICON_COMMANDER",
            "ICON_FOLLOWING",
            "ICON_EMPTY",
            "ICON_MOVE_TO_POSITION",
            "ICON_MOVE_TO_HEALTH_PICKUP",
            "ICON_MOVE_TO_ENTER_VEHICLE",
            "ICON_SEEN_ENEMY",
            "ICON_RADIO_MESSAGE",
            "ICON_ATTACK",
            "ICON_DEAD",
            "ICON_GUARD_AREA",
            "ICON_MOVE_TO_REPAIR_PICKUP",
            "ICON_INACTIVE"
        ],
        "eTextJustification": [
            "JUSTIFY_LEFT",
            "JUSTIFY_CENTRE",
            "JUSTIFY_RIGHT"
        ],
        "eSpriteIndex": [
            "eUnitIconGrunt",
            "eUnitIconVetHMG",
            "eUnitIconVetAnitArmour",
            "eUnitIconFlamer",
            "eUnitIconGrenade",
            "eUnitIconVetAntiAir",
            "eUnitIconShotGun",
            "eUnitIconRecon",
            "eUnitIconLightTransport",
            "eUnitIconHeavyTransport",
            "eUnitIconLightTank",
            "eUnitIconHeavyTank",
            "eUnitIconArtillary",
            "eUnitIconAnitAir",
            "eUnitIconBattleStation",
            "eUnitIconFighter",
            "eUnitIconGunship",
            "eUnitIconTransport",
            "eUnitIconBomber",
            "eUnitIconStratofortress",
            "eUnitIconBuilding"
        ],
        "eTerrainParticleFrame": [
            "eTERRAIN_PARTICLE_FRAMES_1X1",
            "eTERRAIN_PARTICLE_FRAMES_2X2",
            "eTERRAIN_PARTICLE_FRAMES_4X4"
        ],
        "sAlphaMode": [
            "ALPHA_MODE_BLEND",
            "ALPHA_MODE_ADDITIVE",
            "ALPHA_MODE_SUBTRACTIVE"
        ],
        "eBoolean": [
            "eFalse",
            "eTrue"
        ],
        "eTerrainParticleAnimation": [
            "eTERRAIN_PARTICLE_NO_ANIMATION",
            "eTERRAIN_PARTICLE_SKEW_ANIMATION",
            "eTERRAIN_PARTICLE_TEXTURE_ANIMATION"
        ],
        "eTroopVoicePriority": [
            "ETVP_CRITICAL",
            "ETVP_NORMAL",
            "ETVP_EARCANDY"
        ]

    },
    "BW2":
        {
        "eUnitClass": [
            "UNIT_MAN_GRUNT",
            "UNIT_MAN_CHAINGUN",
            "UNIT_MAN_BAZOOKA",
            "UNIT_MAN_FLAMER",
            "UNIT_MAN_MORTAR",
            "UNIT_MAN_ANTI_AIR",
            "UNIT_MAN_SHOTGUN",
            "UNIT_VEH_RECON",
            "UNIT_VEH_LIGHT_TRANSPORT",
            "UNIT_VEH_HEAVY_TRANSPORT",
            "UNIT_VEH_LIGHT_TANK",
            "UNIT_VEH_HEAVY_TANK",
            "UNIT_VEH_ARTILLARY",
            "UNIT_VEH_ANTI_AIR",
            "UNIT_VEH_BATTLESTATION",
            "UNIT_AIR_FIGHTER",
            "UNIT_AIR_GUNSHIP",
            "UNIT_AIR_TRANSPORT",
            "UNIT_AIR_BOMBER",
            "UNIT_AIR_STRATOFORTRESS",
            "UNIT_BUILDING",
            "UNIT_SEA_BATTLESHIP",
            "UNIT_SEA_FRIGATE",
            "UNIT_SEA_SUBMARINE",
            "UNIT_SEA_GUNBOAT",
            "UNIT_SEA_DREADNAUGHT",
            "UNIT_INVALID"
        ],
        "eLevelType": [
            "eFrontend",
            "eSinglePlayer",
            "eMultiPlayerAssault",
            "eMultiplayerSkirmish",
            "eMultiplayerCoop"
        ],
        "eInvisType": [
            "INVIS_NONE",
            "INVIS_SUBMERGE",
            "INVIS_TYPE_1",
            "INVIS_TYPE_2",
            "INVIS_TYPE_3",
            "INVIS_TYPE_4",
            "INVIS_TYPE_5",
            "INVIS_TYPE_6",
            "INVIS_TYPE_7"
        ],
        "ePathingGradient": [
            "ePFGradient_Flat",
            "ePFGradient_Gentle",
            "ePFGradient_Steep",
            "ePFGradient_Extreme",
            "ePFGradient_Infinite"
        ],
        "ePathingWaterDepth": [
            "ePFWater_Dry",
            "ePFWater_Shallow",
            "ePFWater_Deep",
            "ePFWater_VeryDeep",
            "ePFWater_Infinite"
        ],
        "eKWUnitClass": [
            "KW_UNIT_UNDEFINED",
            "KW_UNIT_PEASANT",
            "KW_UNIT_CAVALRY",
            "KW_UNIT_KNIGHT",
            "KW_UNIT_ARCHER",
            "KW_UNIT_SPEARMAN",
            "KW_UNIT_HERO",
            "KW_UNIT_OGRE",
            "KW_UNIT_GIANT",
            "KW_UNIT_DRAGON",
            "KW_UNIT_TREBUCHET",
            "KW_UNIT_BALLISTA",
            "KW_UNIT_SIEGE_TOWER",
            "KW_UNIT_BATTERING_RAM",
            "KW_UNIT_OILER_STATION",
            "KW_UNIT_MOUNTED_TREBUCHET"
        ],
        "eObjtag": [
            "TAG_UNTAGGED",
            "TAG_BONE_L_FOOT",
            "TAG_BONE_R_FOOT",
            "TAG_BONE_HEAD",
            "TAG_BONE_HELMET",
            "TAG_BONE_L_HAND",
            "TAG_BONE_R_HAND",
            "TAG_BONE_JAW"
        ],
        "eMaterialLightingMode": [
            "eMATERIAL_LIGHTMODE_MODULATE",
            "eMATERIAL_LIGHTMODE_MODULATE_2X"
        ],
        "eScreenFilterMode": [
            "eSCREENFILTER_NONE",
            "eSCREENFILTER_DEFLICKER",
            "eSCREENFILTER_DEFLICKER_MIX"
        ],
        "eBloomBlurFilter": [
            "BBF_CHEAP",
            "BBF_GAUSSIAN_5",
            "BBF_GAUSSIAN_7",
            "BBF_GAUSSIAN_9",
            "BBF_GAUSSIAN_11",
            "BBF_GAUSSIAN_13",
            "BBF_GAUSSIAN_15"
        ],
        "eDamageType": [
            "DAMAGE_NO_DAMAGE",
            "DAMAGE_SMALLBULLET",
            "DAMAGE_LARGEBULLET",
            "DAMAGE_ARMOURPIERCING",
            "DAMAGE_IMPACT",
            "DAMAGE_EXPLOSIVE",
            "DAMAGE_FIRE",
            "DAMAGE_CRUSHING",
            "DAMAGE_HEALING",
            "DAMAGE_REPAIR",
            "DAMAGE_PRECALCULATED",
            "DAMAGE_BIGBOMB",
            "DAMAGE_CUSTOM_1",
            "DAMAGE_CUSTOM_2",
            "DAMAGE_ANTIAIR",
            "DAMAGE_SHIP_0",
            "DAMAGE_SHIP_1",
            "DAMAGE_SHIP_2",
            "DAMAGE_SHIP_3",
            "DAMAGE_GENERIC_0",
            "DAMAGE_GENERIC_1",
            "DAMAGE_GENERIC_2",
            "DAMAGE_GENERIC_3",
            "DAMAGE_GENERIC_4",
            "DAMAGE_GENERIC_5",
            "DAMAGE_GENERIC_6",
            "DAMAGE_GENERIC_7",
            "DAMAGE_GENERIC_8",
            "DAMAGE_GENERIC_9"
        ],
        "eSurfaceType": [
            "INVALID_SURFACE",
            "STONE",
            "WOOD",
            "METAL",
            "FLESH",
            "WATER",
            "GRAVEL",
            "SAND",
            "SNOW",
            "MUD",
            "GRASS",
            "AIRBURST",
            "ROAD",
            "CLOTH",
            "UNDERWATER",
            "PATH",
            "FOLIAGE",
            "CORNFIELD",
            "METAL_WOOD_HYBRID",
            "ARMOUR",
            "ST_SWORD",
            "CHAINMAIL",
            "SPECIALCASE3RDSTRIKE",
            "SPECIALCASEBLOCKBREAKER",
            "XYLVANIAN_STONE",
            "ICE",
            "CONCRETE",
            "NEROCYTE"
        ],
        "eBindingReadType": [
            "BINDING_DEFAULT",
            "ALWAYS_ON",
            "VEHICLE_BRAKING",
            "VEHICLE_THROTTLE",
            "VEHICLE_HEADLIGHT",
            "VEHICLE_HEADLIGHT_DECAL",
            "VEHICLE_DIRT",
            "UNIT_DAMAGE",
            "AMMO_POWER",
            "VEHICLE_SPEED",
            "DAMAGEABLE_BURNING",
            "AIR_VEHICLE_CLOUD",
            "MELEE_BLOCK",
            "VEHICLE_SPRAY_LEFT",
            "VEHICLE_SPRAY_RIGHT",
            "WATER_VEHICLE_SPEED",
            "WATER_VEHICLE_THROTTLE",
            "LEVEL_DAYLIGHT",
            "LEVEL_NIGHT",
            "WATER_VEHICLE_SUBMERGED",
            "ALWAYS_ON_STICKTOWATER",
            "WATER_VEHICLE_SPEED_STICKTOWATER",
            "WATER_VEHICLE_THROTTLE_STICKTOWATER",
            "WATER_VEHICLE_SUBMERGED_STICKTOWATER"
        ],
        "EPSChannel": [
            "PSC_INTENSITY",
            "PSC_SIZE",
            "PSC_SPEED",
            "PSC_COLOUR"
        ],
        "eAirVehicleCurveController": [
            "EAVCC_ROTORSPEED",
            "EAVCC_SPEED"
        ],
        "eSIType": [
            "FACTORY",
            "BARRACKS",
            "AIRBASE",
            "PORT",
            "HEADQUARTERS",
            "MOBILE_LAND_BASE",
            "MOBILE_SEA_BASE"
        ],
        "ePhysicEngineType": [
            "physEngODE",
            "physEngAgeia",
            "physEngMax"
        ],
        "eCurveController": [
            "ECC_POWER",
            "ECC_SPEED"
        ],
        "eWeaponSoundBaseFireTypes": [
            "WSBFT_SINGLE",
            "WSBFT_DOUBLE",
            "WSBFT_ASMANYASITTAKES"
        ],
        "eWeaponEffectiveness": [
            "WE_INEFFECTIVE",
            "WE_AVERAGE",
            "WE_GOOD",
            "WE_PERFECT"
        ],
        "eAdvancedWeaponType": [
            "AW_BAZOOKA",
            "AW_FLAMETHROWER",
            "AW_MISSILE",
            "AW_CHAINGUN",
            "AW_RIFLE",
            "AW_MORTAR",
            "AW_SHOTGUN"
        ],
        "ePhase": [
            "PHASE_ATTACK",
            "PHASE_SUSTAIN",
            "PHASE_RELEASE"
        ],
        "eHighLow": [
            "eHigh",
            "eLow"
        ],
        "eCoverTagList": [
            "COVER_NONE",
            "COVER_A",
            "COVER_B",
            "COVER_C",
            "COVER_D",
            "COVER_E",
            "COVER_F",
            "COVER_G",
            "COVER_H"
        ],
        "eSceneryClusterAlphaFade": [
            "SCNCLUSTER_ALPHA_FADE_AUTO",
            "SCNCLUSTER_ALPHA_FADE_ON",
            "SCNCLUSTER_ALPHA_FADE_OFF"
        ],
        "eCameraType": [
            "eCAMTYPE_STATIC",
            "eCAMTYPE_CHASETARGET",
            "eCAMTYPE_LOOKAT",
            "eCAMTYPE_ISOMETRIC",
            "eCAMTYPE_CIRCLECAM",
            "eCAMTYPE_WAYPOINTCAM"
        ],
        "eZoneType": [
            "ZONETYPE_DEFAULT",
            "ZONETYPE_WORLDBOUNDARY",
            "ZONETYPE_MISSIONBOUNDARY",
            "ZONETYPE_NOGOAREA",
            "ZONETYPE_FORD"
        ],
        "ePickupState": [
            "PICKUP_STATE_UNSPAWNED",
            "PICKUP_STATE_ACTIVE"
        ],
        "ePickupType": [
            "PICKUP_TYPE_SECONDARY_WPN_UPGRADE",
            "PICKUP_TYPE_SECONDARY_WPN_AMMO",
            "PICKUP_TYPE_TROOP_HEALTH",
            "PICKUP_TYPE_VEHICLE_HEALTH",
            "PICKUP_TYPE_UNPICKUPABLE",
            "PICKUP_TYPE_GOLDCOIN"
        ],
        "eEffectCameraAnchorType": [
            "eEFFECT_NO_ANCHOR_CAMERA",
            "eEFFECT_ANCHOR_TO_CAMERA_POS",
            "eEFFECT_ANCHOR_TO_CAMERA_POS_DIR"
        ],
        "eArmyAllegiance": [
            "ALLEGIANCE_ALLY",
            "ALLEGIANCE_NEUTRAL",
            "ALLEGIANCE_ENEMY"
        ],
        "eTroopVoicePriority": [
            "ETVP_CRITICAL",
            "ETVP_NORMAL",
            "ETVP_EARCANDY"
        ],
        "eSeatDisplayType": [
            "SEATDISPLAY_SOLDER_INVISIBLE",
            "SEATDISPLAY_SOLDER_HEADONLY",
            "SEATDISPLAY_SOLDER_TOSHOULDERS",
            "SEATDISPLAY_SOLDER_STANDING",
            "SEATDISPLAY_SOLDER_SITTING"
        ],
        "eBuildingIconType": [
            "eNoIconType",
            "eSkyLineIconType",
            "eExplosionIconType",
            "eAntennaeIconType",
            "eMGNIconType"
        ],
        "eRaiseAnimType": [
            "eRaiseAnim_PullFlag",
            "eRaiseAnim_TurnHandle",
            "eRaiseAnim_Spare3",
            "eRaiseAnim_Spare4",
            "eRaiseAnim_Spare5",
            "eRaiseAnim_Spare6",
            "eRaiseAnim_Spare7",
            "eRaiseAnim_Spare8"
        ],
        "eCapturePointType": [
            "eFlag",
            "eHelipad",
            "eDetonator"
        ],
        "eGUIJustification": [
            "eGUIJustification_Left",
            "eGUIJustification_Centre",
            "eGUIJustification_Right",
            "eGUIJustification_Full1",
            "eGUIJustification_Full2"
        ],
        "eHUDs": [
            "PLAYER_ONE_HUD",
            "PLAYER_TWO_HUD",
            "PLAYER_THREE_HUD",
            "PLAYER_FOUR_HUD"
        ],
        "eCommandIconType": [
            "ICON_NO_ICON",
            "ICON_COMMANDER",
            "ICON_FOLLOWING",
            "ICON_EMPTY",
            "ICON_MOVE_TO_POSITION",
            "ICON_MOVE_TO_HEALTH_PICKUP",
            "ICON_MOVE_TO_ENTER_VEHICLE",
            "ICON_SEEN_ENEMY",
            "ICON_RADIO_MESSAGE",
            "ICON_ATTACK",
            "ICON_DEAD",
            "ICON_WAIT",
            "ICON_GUARD",
            "ICON_MOVE_TO_REPAIR_PICKUP",
            "ICON_INACTIVE"
        ],
        "eReticuleBlendMode": [
            "RBM_Modulated",
            "RBM_Additive"
        ],
        "eTextJustification": [
            "JUSTIFY_LEFT",
            "JUSTIFY_CENTRE",
            "JUSTIFY_RIGHT"
        ],
        "eMPTextMode": [
            "MPTEXTMODE_BOTH",
            "MPTEXTMODE_SP",
            "MPTEXTMODE_MP",
            "MPTEXTMODE_MP_COOP"
        ],
        "eSpriteIndex": [
            "eUnitIconGrunt",
            "eUnitIconVetHMG",
            "eUnitIconVetAnitArmour",
            "eUnitIconFlamer",
            "eUnitIconGrenade",
            "eUnitIconVetAntiAir",
            "eUnitIconShotGun",
            "eUnitIconRecon",
            "eUnitIconLightTransport",
            "eUnitIconHeavyTransport",
            "eUnitIconLightTank",
            "eUnitIconHeavyTank",
            "eUnitIconArtillary",
            "eUnitIconAnitAir",
            "eUnitIconBattleStation",
            "eUnitIconFighter",
            "eUnitIconGunship",
            "eUnitIconTransport",
            "eUnitIconBomber",
            "eUnitIconStratofortress",
            "eUnitIconBuilding",
            "eUnitIconHeadquarters",
            "eUnitIconFactory",
            "eUnitIconBarracks",
            "eUnitIconAirbase",
            "eUnitIconDocks",
            "eUnitIconRadar",
            "eNoUnitIconSet",
            "eArmyIconWesternFrontier",
            "eArmyIconXylvanian",
            "eArmyIconTundranTerritories",
            "eArmyIconSolarEmpire",
            "eArmyIconUnderworld",
            "eArmyIconAngloIsles"
        ],
        "eTerrainParticleFrame": [
            "eTERRAIN_PARTICLE_FRAMES_1X1",
            "eTERRAIN_PARTICLE_FRAMES_2X2",
            "eTERRAIN_PARTICLE_FRAMES_4X4"
        ],
        "sAlphaMode": [
            "ALPHA_MODE_BLEND",
            "ALPHA_MODE_ADDITIVE",
            "ALPHA_MODE_SUBTRACTIVE"
        ],
        "eTerrainParticleAnimation": [
            "eTERRAIN_PARTICLE_NO_ANIMATION",
            "eTERRAIN_PARTICLE_SKEW_ANIMATION",
            "eTERRAIN_PARTICLE_TEXTURE_ANIMATION"
        ],
        "eGUI3DBlendMode": [
            "eGUI3DBlendMode_BLEND",
            "eGUI3DBlendMode_ADDITIVE",
            "eGUI3DBlendMode_SUBTRACTIVE",
            "eGUI3DBlendMode_COPY",
            "eGUI3DBlendMode_INVBLEND",
            "eGUI3DBlendMode_DESTBLENDADDSOURCE",
            "eGUI3DBlendMode_COPYDEST"
        ],
        "eGUI3DTextureFormat": [
            "eGUI3DTextureFormat_I4",
            "eGUI3DTextureFormat_I8",
            "eGUI3DTextureFormat_IA4",
            "eGUI3DTextureFormat_IA8",
            "eGUI3DTextureFormat_RGB565",
            "eGUI3DTextureFormat_RGB5A3",
            "eGUI3DTextureFormat_RGBA8",
            "eGUI3DTextureFormat_CMPR"
        ],
        "eGUIModXMode": [
            "eGUIModXOff",
            "eGUIModX2",
            "eGUIModX4"
        ],
        "eGUIOrientation": [
            "eGUIOrientation_None",
            "eGUIOrientation_Horizontal",
            "eGUIOrientation_Vertical"
        ],
        "eGUIZPlane": [
            "eGUIZPlane_00",
            "eGUIZPlane_01",
            "eGUIZPlane_02",
            "eGUIZPlane_03",
            "eGUIZPlane_04",
            "eGUIZPlane_05",
            "eGUIZPlane_06",
            "eGUIZPlane_07",
            "eGUIZPlane_08",
            "eGUIZPlane_09",
            "eGUIZPlane_10",
            "eGUIZPlane_11",
            "eGUIZPlane_12",
            "eGUIZPlane_13",
            "eGUIZPlane_14",
            "eGUIZPlane_15",
            "eGUIZPlane_16",
            "eGUIZPlane_17",
            "eGUIZPlane_18",
            "eGUIZPlane_19",
            "eGUIZPlane_20",
            "eGUIZPlane_21",
            "eGUIZPlane_22",
            "eGUIZPlane_23",
            "eGUIZPlane_24",
            "eGUIZPlane_25",
            "eGUIZPlane_26",
            "eGUIZPlane_27",
            "eGUIZPlane_28",
            "eGUIZPlane_29",
            "eGUIZPlane_30",
            "eGUIZPlane_31"
        ],
        "eGUIEvent": [
            "eGUIEvent_None",
            "eGUIEvent_OnOpen",
            "eGUIEvent_OnClose",
            "eGUIEvent_OnUpdate",
            "eGUIEvent_OnRender",
            "eGUIEvent_OnSelect",
            "eGUIEvent_OnDeselect",
            "eGUIEvent_OnActivated",
            "eGUIEvent_OnActivateHeld",
            "eGUIEvent_OnActivateReleased",
            "eGUIEvent_OnCancel",
            "eGUIEvent_OnAB",
            "eGUIEvent_Start",
            "eGUIEvent_StartHeld",
            "eGUIEvent_StartReleased",
            "eGUIEvent_Start",
            "eGUIEvent_StartHeld",
            "eGUIEvent_StartReleased",
            "eGUIEvent_Home",
            "eGUIEvent_Select",
            "eGUIEvent_SelectHeld",
            "eGUIEvent_SelectReleased",
            "eGUIEvent_Select",
            "eGUIEvent_SelectHeld",
            "eGUIEvent_SelectReleased",
            "eGUIEvent_1",
            "eGUIEvent_2",
            "eGUIEvent_Left",
            "eGUIEvent_Right",
            "eGUIEvent_Up",
            "eGUIEvent_UpHeld",
            "eGUIEvent_UpReleased",
            "eGUIEvent_Down",
            "eGUIEvent_DownHeld",
            "eGUIEvent_DownReleased",
            "eGUIEvent_OnChanged"
        ],
        "eBoolean": [
            "eFalse",
            "eTrue"
        ],
        "eAiUnitState": [
            "AI_STATE_NONE",
            "AI_STATE_UNSPAWNED",
            "AI_STATE_NORMAL",
            "AI_STATE_DYING",
            "AI_STATE_DEAD",
            "AI_STATE_PERMANENTLY_DEAD",
            "AI_STATE_IN_LIMBO"
        ],
        "eAttackStyle": [
            "ATTACKSTYLE_FROM_DEFENSIVE_AREA",
            "ATTACKSTYLE_HUNT_AND_DESTROY"
        ],
        "eMoveStyle": [
            "MOVESTYLE_RESPOND_TO_ATTACKS",
            "MOVESTYLE_ATTACK_ON_SIGHT"
        ],
        "eArmy": [
            "eNoArmy",
            "eWesternFrontier",
            "eXylvanian",
            "eTundranTerritories",
            "eSolarEmpire",
            "eUnderWorld",
            "eNeutral",
            "eAngloIsles"
        ]

        }
}

FLAGS = {
    "BW1": {
        "e32CollideTypeWithNoArmies": [
            ("COL_PLATFORM", 8),
            ("COL_DUMMYTARGET", 0x10),
            ("COL_BACKGROUND", 0x200000),
            ("COL_BLOCKSPATHFINDING", 0x400000),
            ("COL_TANKCRUSHABLE", 0x1000000),
            ("COL_SOLID", 0x80000000)
        ],
        "e32CollideType": [
            ("COL_PLATFORM", 8),
            ("COL_DUMMYTARGET", 0x10),
            ("COL_VEHICLE", 0x40),
            ("COL_AIRCRAFT", 0x80),
            ("COL_INFANTRY", 0x100),
            ("COL_ACTIVEBUILDING", 0x200),
            ("COL_BACKGROUND", 0x200000),
            ("COL_BLOCKSPATHFINDING", 0x400000),
            ("COL_TANKCRUSHABLE", 0x1000000),
            ("COL_SOLID", 0x80000000)
        ],
        "eSysFlag": [
            ("SYSFLAG_FLASHBLIP", 0x40),
            ("SYSFLAG_DORMANT", 0x80),
            ("SYSFLAG_ALWAYSUPDATE", 0x100),
            ("SYSFLAG_NEVERUPDATE", 0x200),
            ("SYSFLAG_ALWAYSCOLLIDE", 0x400),
            ("SYSFLAG_MISSIONOBJECT", 0x800),
            ("SYSFLAG_INVISIBLE", 0x1000),
            ("SYSFLAG_NORADARIMG", 0x2000),
            ("SYSFLAG_DISABLED", 0x800000),
            ("SYSFLAG_DESTROYABLE", 0x2000000),
            ("SYSFLAG_AI_UNIT", 0x8000000),
            ("SYSFLAG_CONTAINER", 0x10000000)
        ],
        "eWaypointFlags": [
            ("WP_TOP_SPEED", 1),
            ("WP_FACE_DIRECTION_ON_PAUSE", 2),
            ("WP_FACE_DIRECTION_ON_STOP", 4),
            ("WP_PAUSE_AT_WAYPOINT", 0x10),
            ("WP_ROAD_WAYPOINT", 8),
            ("WP_CAMERA_WAYPOINT", 0x20),
            ("WP_ROAD_INFANTRY_ONLY", 0x40),
            ("WP_ROAD_INFO_DELETE_ADJACENT", 0x80)
        ],
        "eAnimationTriggeredEffectChainItemFlags": [
            ("IGNORE_ORIENTATION", 1),
            ("USE_TERRAIN_NORMAL", 2),
            ("USE_OFFSET", 4)
        ],
        "eSpriteProperty": [
            ("SPRPROP_NONE", 0),
            ("SPRPROP_ROTATED", 1),
            ("SPRPROP_SCALED", 2),
            ("SPRPROP_TILEDFORANIM", 4),
            ("SPRPROP_ALPHATEST", 8),
            ("SPRPROP_ANIMATE", 0x10),
            ("SPRPROP_LOOPED", 0x20),
            ("SPRPROP_ADDITIVE", 0x40),
            ("SPRPROP_USETEXCOORDS", 0x80),
            ("SPRPROP_SCALEDCOORDS", 0x100),
            ("SPRPROP_FRONTEND", 0x800),
            ("SPRPROP_ANIMATE_RANDOM", 0x1000),
            ("SPRPROP_XMIRRORED", 0x2000),
            ("SPRPROP_SUBTRACTIVE", 0x4000),
            ("SPRPROP_PINGPONG", 0x8000)
        ],
        "eStaticFlag": [
            ("TF_NONE", 0),
            ("TF_SELECTDOWN", 1),
            ("TF_FIREPRESSED", 2),
            ("TF_TOGGLE", 4),
            ("TF_INVISIBLE", 0x80)
        ],
        "eWeaponBaseFlag": [
            ("sWeaponBase::WEPFLAG_FIREBARRELGRANDCHILDREN", 1),
            ("sWeaponBase::WEPFLAG_FIREFROMBARRELCHIDLREN", 2),
            ("sWeaponBase::WEPFLAG_MULTIBARRELFIRE", 4),
            ("sWeaponBase::WEPFLAG_YROTATETURRET", 8),
            ("sWeaponBase::WEPFLAG_XROTATEBARREL", 0x10),
            ("sWeaponBase::WEPFLAG_NOPARENTVEL", 0x20),
            ("sWeaponBase::WEPFLAG_INFINITEAMMO", 0x40),
            ("sWeaponBase::WEPFLAG_SHOTLEAD", 0x80),
            ("sWeaponBase::WEPFLAG_HUMAN_WEAPON", 0x100),
            ("sWeaponBase::WEPFLAG_IGNORE_LOS", 0x200),
            ("sWeaponBase::WEPFLAG_NEVER_ATTACK_IF_INEFFECTIVE", 0x1000)
        ],

        "eDestroyFlags": [
            ("DESTROYFLAG_PARTICLES_ON_DAMAGE", 1),
            ("DESTROYFLAG_EXPLODE_ON_DEATH", 2),
            ("DESTROYFLAG_IGNITE_ON_CRIT_DAMAGE", 4),
            ("DESTROYFLAG_DIE_ON_IGNITE", 8),
            ("DESTROYFLAG_VANISH_ON_DEATH", 0x10),
            ("DESTROYFLAG_MATCHSLOPE", 0x20),
            ("DESTROYFLAG_DONT_INHERIT_COLOUR_LINK_OBJECTS", 0x40),
            ("DESTROYFLAG_INVINCIBLE", 0x80),
            ("DESTROYFLAG_BLOCKVEHICLESNEARBY", 0x100),
            ("DESTROYFLAG_USE_OBJECT_MASS", 0x200)
        ],
        "eDestroyableInstanceFlags": [
            ("DIFLAG_IS_NAVIGABLE_BRIDGE", 1),
            ("DIFLAG_DONT_LINK_ROAD_TRACKS", 2),
            ("DIFLAG_DONT_LINK_ARCH_TRACKS", 4),
            ("DIFLAG_ROAD_IS_BLOCKED", 8),
            ("DIFLAG_ARCH_IS_BLOCKED", 0x10),
            ("DIFLAG_INFANTRY_ONLY_BRIDGE", 0x20),
            ("DIFLAG_IS_NAVIGABLE_WALL", 0x100),
            ("DIFLAG_DONT_LINK_WALL_TRACKS", 0x200),
            ("DIFLAG_RAMP_FROM_WALL_TO_FLOOR", 0x400),
            ("DIFLAG_WALL_HAS_ARCH_OR_GATEWAY", 0x800),
            ("DIFLAG_NODEGRAPH_RES_HINT_8M", 0x10000),
            ("DIFLAG_NODEGRAPH_RES_HINT_4M", 0x20000),
            ("DIFLAG_BLOCKVEHICLESNEARBY", 0x40000)
        ],
        "eSceneryClusterFlags": [
            ("SCNCLUSTER_FLAG_EXPENSIVELIGHTING", 0x40),
            ("SCNCLUSTER_FLAG_RANDOMANGLES", 0x80),
            ("SCNCLUSTER_FLAG_90DEGREEANGLES", 0x100),
            ("SCNCLUSTER_FLAG_RANDOMSIZE", 0x400),
            ("SCNCLUSTER_FLAG_STRAIGHTLINE", 0x800),
            ("SCNCLUSTER_FLAG_RECTANGLE", 0x1000)
        ],
        "eCameraFlag": [
            ("eCAMFLAG_INTERPOLATEFROMCHOPPERHEIGHTANDSPEED", 1),
            ("eCAMFLAG_INTERPOLATEFOVFROMCHOPPERSPEED", 4),
            ("eCAMFLAG_EXTERNALFOV", 8),
            ("eCAMFLAG_DOLOOKOFFSETY", 0x10),
            ("eCAMFLAG_ALWAYSFACEFORWARDS", 0x200),
            ("eCAMFLAG_INTERPOLATELAG", 0x400),
            ("eCAMFLAG_DOESSHAKE", 0x800),
            ("eCAMFLAG_INTERPOLATEMOTIONBLUR", 0x1000)
        ],
        "eCamInstanceFlag": [
            ("eCINST_FIRSTCAM", 1),
            ("eCINST_CUTCAM", 2),
            ("eCINST_SCREEN_1_CAM", 4),
            ("eCINST_SCREEN_2_CAM", 8),
            ("eCINST_PLAYER_CAM", 0x10)
        ],
        "e32DamageZoneUnits": [
            ("COL_VEHICLE", 0x40),
            ("COL_AIRCRAFT", 0x80),
            ("COL_INFANTRY", 0x100)
        ],

        "eZoneFlags": [
            ("ZONEFLAG_3D", 1)
        ],
        "eExplodeFlags": [
            ("EXPLODEFLAG_FRAGMENTMODEL", 1),
            ("EXPLODEFLAG_SINGLEFRAGMENT", 2),
            ("EXPLODEFLAG_FRAGMENTALLBUTROOT", 4),
            ("EXPLODEFLAG_SIZEFROMEXPLODER", 8),
            ("EXPLODEFLAG_LIGHTOBJECTS", 0x10),
            ("EXPLODEFLAG_LIGHTLANDSCAPE", 0x20),
            ("EXPLODEFLAG_SCREENFLASH", 0x40),
            ("EXPLODEFLAG_DARKENOBJECT", 0x80),
            ("EXPLODEFLAG_SCORCHMARK", 0x200),
            ("EXPLODEFLAG_ROOTNODEFLYOFF", 0x400),
            ("EXPLODEFLAG_MODELS_HALF_ALPHA", 0x800),
            ("EXPLODEFLAG_PARTICLES_USEVECTOR", 0x1000),
            ("EXPLODEFLAG_WAVEMODEL_ROTATE", 0x2000),
            ("EXPLODEFLAG_THROWLIVEMODEL", 0x4000),
            ("EXPLODEFLAG_USEREALVERTICAL", 0x8000),
            ("EXPLODEFLAG_CATASTROPHIC", 0x10000),
            ("EXPLODEFLAG_SEQUENCED", 0x20000),
            ("EXPLODEFLAG_STICKEMITTERTOMODEL", 0x40000),
            ("EXPLODEFLAG_UNDERWATER", 0x80000),
            ("EXPLODEFLAG_SCORCHLASTFOREVER", 0x100000),
            ("EXPLODEFLAG_MAKECAMERASHAKE", 0x200000)
        ],
        "eIncidentalFlag": [
            ("IFLAG_BOUNCEONGROUND", 1),
            ("IFLAG_SHATTERONGROUND", 2),
            ("IFLAG_VANISHOFFSCREEN", 4),
            ("IFLAG_FACEALONGMOVEMENT", 8),
            ("IFLAG_RANDOMTUMBLE", 0x20),
            ("IFLAG_PICK_RANDOM_MODEL", 0x40)
        ],


        "eProjectileFlag": [
            ("sProjectileBase::BULLETFLAG_GUIDED", 1),
            ("sProjectileBase::BULLETFLAG_SMOKETRAIL", 2),
            ("sProjectileBase::BULLETFLAG_FALLATENDOFLIFE", 4),
            ("sProjectileBase::BULLETFLAG_GROUNDIMPACTBURST", 8),
            ("sProjectileBase::BULLETFLAG_DOSHM", 0x10),
            ("sProjectileBase::BULLETFLAG_FLAMETHROWER", 0x20),
            ("sProjectileBase::BULLETFLAG_HEAT_DURING_FLIGHT", 0x40),
            ("sProjectileBase::BULLETFLAG_GROUNDEXPLOSION", 0x80),
            ("sProjectileBase::BULLETFLAG_WATERIMPACTBURST", 0x100),
            ("sProjectileBase::BULLETFLAG_EXPLODEONMISS", 0x200),
            ("sProjectileBase::BULLETFLAG_BOUNCE", 0x400),
            ("sProjectileBase::BULLETFLAG_SHOTGUN_CONE", 0x800),
            ("sProjectileBase::BULLETFLAG_BALLISTIC_TRAJECTORY", 0x1000)
        ],

        "eSeatFlags": [
            ("SEATFLAG_ACTIVE", 1),
            ("SEATFLAG_SOLDIER", 2),
            ("SEATFLAG_VEHICLE", 4),
            ("SEATFLAG_AUTOMATIC", 0x20),
            ("SEATFLAG_PHANTOM", 0x40),
            ("SEATFLAG_UNLOCKED", 0x80),
            ("SEATFLAG_NO_EXIT", 0x100)
        ],

        "VehicleFlags": [
            ("AIUNIT_ALWAYS_STATIC", 0x80),
            ("AIUNIT_NO_COL_REACTION", 0x100),
            ("AIUNIT_EXPLODE_LAUNCH", 0x2000),
            ("AIUNIT_ENEMIES_CAN_GET_IN", 0x100000)
        ],
        "sTroopAvoidFlags": [
            ("AIV_AVOID_CHECK_OBJECTS", 1),
            ("AIV_AVOID_CHECK_WATER", 2),
            ("AIV_AVOID_CHECK_FIRE", 4)
        ],
        "eTroopVoiceFlags": [
            ("IS_INTERRUPTIBLE", 2),
            ("PLAY_IMMEDIATE", 1)
        ],

        "eAutoTransferable": [
            ("AUTO_TRANSFERABLE", 1)
        ],
        "eInitiallyDontIdleTurn": [
            ("INITIALLY_DONT_IDLE_TURN", 1)
        ],
        "eNeverIdleTurn": [
            ("NEVER_IDLE_TURN", 1)
        ],
        "eAiUnitFlags": [
            ("AIUNIT_ORGANIC", 1),
            ("UNKNOWN", 2),
            ("AIUNIT_UPRIGHT", 8),
            ("AIUNIT_UPRIGHT_Z", 0x10),
            ("AIUNIT_ALWAYS_STATIC", 0x80),
            ("AIUNIT_NO_COL_REACTION", 0x100),
            ("AIUNIT_DETAILED_BULLET_COL", 0x1000),
            ("AIUNIT_EXPLODE_LAUNCH", 0x2000),
            ("AIUNIT_AVOID_PLAYER", 0x4000),
            ("AIUNIT_REACT_TO_BULLET_HIT", 0x8000),
            ("AIUNIT_NO_AVOIDANCE", 0x20000),
            ("AIUNIT_WATER_AVOID", 0x40000),
            ("AIUNIT_NO_TARGET_AIM_ROTX", 0x80000),
            ("AIUNIT_ENEMIES_CAN_GET_IN", 0x100000)
        ],
        "eAiUnitInstanceFlags": [
            ("AIUNIT_INITIALLY_DONT_IDLE_TURN", 1),
            ("AIUNIT_NEVER_IDLE_TURN", 2),
            ("AIUNIT_INACTIVE", 4),
            ("AIUNIT_NOT_SCORED", 8)
        ],

        "BuildingFlags": [
            ("AIUNIT_ENEMIES_CAN_GET_IN", 0x100000)
        ],
        "eObjectiveFlags": [
            ("OBJECTIVE_VISIBLE", 1),
            ("OBJECTIVE_COMPLETE", 2),
            ("OBJECTIVE_SECONDARY", 4)
        ],
        "eObjectiveMarkerFlags": [
            ("OBJECTIVE_MARKER_VISIBLE", 1),
            ("OBJECTIVE_MARKER_AUTOINVISIBLE", 2),
            ("OBJECTIVE_MARKER_START_EFFECT_MOVES", 4),
            ("OBJECTIVE_MARKER_END_EFFECT_MOVES", 8)
        ],

        "eTerrainParticleFlags": [
            ("eTERRAIN_PARTICLE_FLAG_NO_UNDERWATER", 1),
            ("eTERRAIN_PARTICLE_FLAG_SIZE_BASED_ON_BLEND", 2),
            ("eTERRAIN_PARTICLE_FLAG_UV_FLIP_VARIATION", 4),
            ("eTERRAIN_PARTICLE_FLAG_SIZE_VARIATION_2X", 8),
            ("eTERRAIN_PARTICLE_FLAG_SIZE_NO_SHRINK", 0x10)
        ],
        "eAmbientAreaPointSounds": [
            ("AAPS_VARY_POSITION", 1),
            ("AAPS_NOT_USER_ACTIVE", 4)
        ],
        "eSoundFlags": [
            ("PLAY_PAN", 1),
            ("PLAY_ATTENUATE", 2),
            ("PLAY_DOPPLER", 4),
            ("PLAY_STATIONARY", 0x10)
        ]
    },
    "BW2": {
            "e32CollideTypeWithNoArmies": [
                ("COL_PLATFORM", 8),
                ("COL_DUMMYTARGET", 0x10),
                ("COL_BACKGROUND", 0x200000),
                ("COL_BLOCKSPATHFINDING", 0x400000),
                ("COL_TANKCRUSHABLE", 0x1000000),
                ("COL_SOLID", 0x80000000)
            ],
            "e32CollideType": [
                ("COL_PLATFORM", 8),
                ("COL_DUMMYTARGET", 0x10),
                ("COL_VEHICLE", 0x40),
                ("COL_AIRCRAFT", 0x80),
                ("COL_INFANTRY", 0x100),
                ("COL_ACTIVEBUILDING", 0x200),
                ("COL_BACKGROUND", 0x200000),
                ("COL_BLOCKSPATHFINDING", 0x400000),
                ("COL_TREAT_AS_TERRAIN", 0x800000),
                ("COL_TANKCRUSHABLE", 0x1000000),
                ("COL_SOLID", 0x80000000)
            ],
            "eWaypointFlags": [
                ("WP_TOP_SPEED", 1),
                ("WP_FACE_DIRECTION_ON_PAUSE", 2),
                ("WP_FACE_DIRECTION_ON_STOP", 4),
                ("WP_PAUSE_AT_WAYPOINT", 0x10),
                ("WP_ROAD_WAYPOINT", 8),
                ("WP_CAMERA_WAYPOINT", 0x20),
                ("WP_ROAD_INFANTRY_ONLY", 0x40),
                ("WP_ROAD_INFO_DELETE_ADJACENT", 0x80)
            ],
            "eAnimationTriggeredEffectChainItemFlags": [
                ("IGNORE_ORIENTATION", 1),
                ("USE_TERRAIN_NORMAL", 2),
                ("USE_OFFSET", 4)
            ],
            "SPRPROP_NONE": [
                ("SPRPROP_ROTATED", 1),
                ("SPRPROP_SCALED", 2),
                ("SPRPROP_TILEDFORANIM", 4),
                ("SPRPROP_ALPHATEST", 8),
                ("SPRPROP_ANIMATE", 0x10),
                ("SPRPROP_LOOPED", 0x20),
                ("SPRPROP_ADDITIVE", 0x40),
                ("SPRPROP_USETEXCOORDS", 0x80),
                ("SPRPROP_SCALEDCOORDS", 0x100),
                ("SPRPROP_FRONTEND", 0x800),
                ("SPRPROP_ANIMATE_RANDOM", 0x1000),
                ("SPRPROP_XMIRRORED", 0x2000),
                ("SPRPROP_SUBTRACTIVE", 0x4000),
                ("SPRPROP_PINGPONG", 0x8000)
            ],
            "eStaticFlag": [
                ("TF_NONE", 0),
                ("TF_SELECTDOWN", 1),
                ("TF_FIREPRESSED", 2),
                ("TF_TOGGLE", 4),
                ("TF_INVISIBLE", 0x80)
            ],
            "eObjectiveFlags": [
                ("OBJECTIVE_VISIBLE", 1),
                ("OBJECTIVE_COMPLETE", 2),
                ("OBJECTIVE_SECONDARY", 4)
            ],
            "eObjectivePlayers": [
                ("OBJECTIVE_PLAYER_1", 1),
                ("OBJECTIVE_PLAYER_2", 2),
                ("OBJECTIVE_PLAYER_3", 4),
                ("OBJECTIVE_PLAYER_4", 8)
            ],
            "eObjectiveMarkerFlags": [
                ("OBJECTIVE_MARKER_VISIBLE", 1),
                ("OBJECTIVE_MARKER_AUTOINVISIBLE", 2),
                ("OBJECTIVE_MARKER_START_EFFECT_MO", 4),
                ("OBJECTIVE_MARKER_END_EFFECT_MOVE", 8)
            ],
            "VehicleFlags": [
                ("AIUNIT_ALWAYS_STATIC", 0x80),
                ("AIUNIT_NO_COL_REACTION", 0x100),
                ("AIUNIT_EXPLODE_LAUNCH", 0x2000),
                ("AIUNIT_ENEMIES_CAN_GET_IN", 0x100000)
            ],
            "eWaterVehicleFlags": [
                ("cWaterVehicleBase::WVF_SUBMERSIB", 1),
                ("cWaterVehicleBase::WVF_INVIS_WHE", 2),
                ("cWaterVehicleBase::WVF_ALT_PHYSI", 4),
                ("cWaterVehicleBase::WVF_DECLOAK_W", 8)
            ],
            "eWeaponBaseFlag": [
                ("sWeaponBase::WEPFLAG_FIREBARRELG", 1),
                ("sWeaponBase::WEPFLAG_FIREFROMBAR", 2),
                ("sWeaponBase::WEPFLAG_MULTIBARREL", 4),
                ("sWeaponBase::WEPFLAG_YROTATETURR", 8),
                ("sWeaponBase::WEPFLAG_XROTATEBARR", 0x10),
                ("sWeaponBase::WEPFLAG_NOPARENTVEL", 0x20),
                ("sWeaponBase::WEPFLAG_INFINITEAMM", 0x40),
                ("sWeaponBase::WEPFLAG_SHOTLEAD", 0x80),
                ("sWeaponBase::WEPFLAG_HUMAN_WEAPO", 0x100),
                ("sWeaponBase::WEPFLAG_IGNORE_LOS", 0x200),
                ("sWeaponBase::WEPFLAG_NEVER_ATTAC", 0x1000),
                ("sWeaponBase::WEPFLAG_INSTANT", 0x2000),
                ("sWeaponBase::WEPFLAG_CAN_DRIVE_A", 0x4000),
                ("sWeaponBase::WEPFLAG_USE_AIM_ASS", 0x8000),
                ("sWeaponBase::WEPFLAG_BALLISTIC_H", 0x10000),
                ("sWeaponBase::WEPFLAG_AI_SCATTER_", 0x20000),
                ("sWeaponBase::WEPFLAG_FIRE_ALL_IN", 0x40000)
            ],
            "eDestroyFlags": [
                ("UNKNOWN 1", 1),
                ("DESTROYFLAG_EXPLODE_ON_DEATH", 2),
                ("UNKNOWN 2", 4),
                ("DESTROYFLAG_DIE_ON_IGNITE", 8),
                ("DESTROYFLAG_VANISH_ON_DEATH", 0x10),
                ("DESTROYFLAG_MATCHSLOPE", 0x20),
                ("DESTROYFLAG_DONT_INHERIT_COLOUR_", 0x40),
                ("DESTROYFLAG_INVINCIBLE", 0x80),
                ("DESTROYFLAG_BLOCKVEHICLESNEARBY", 0x100),
                ("DESTROYFLAG_USE_OBJECT_MASS", 0x200),
                ("DESTROYFLAG_MELEE_INVINCIBLE", 0x400),
                ("DESTROYFLAG_NO_ALPHA_FADE", 0x800),
                ("DESTROYFLAG_NO_BURNT_COLOUR", 0x1000),
                ("DESTROYFLAG_DONT_HIDE_BEHIND", 0x2000),
                ("DESTROYFLAG_PLAYER_CRUSH_ONLY", 0x4000)
            ],
            "eDestroyableInstanceFlags": [
                ("DIFLAG_IS_NAVIGABLE_BRIDGE", 1),
                ("DIFLAG_DONT_LINK_ROAD_TRACKS", 2),
                ("DIFLAG_DONT_LINK_ARCH_TRACKS", 4),
                ("DIFLAG_ROAD_IS_BLOCKED", 8),
                ("DIFLAG_ARCH_IS_BLOCKED", 0x10),
                ("DIFLAG_INFANTRY_ONLY_BRIDGE", 0x20),
                ("DIFLAG_IS_NAVIGABLE_WALL", 0x100),
                ("DIFLAG_DONT_LINK_WALL_TRACKS", 0x200),
                ("DIFLAG_RAMP_FROM_WALL_TO_FLOOR", 0x400),
                ("DIFLAG_WALL_HAS_ARCH_OR_GATEWAY", 0x800),
                ("DIFLAG_NODEGRAPH_RES_HINT_8M", 0x10000),
                ("DIFLAG_NODEGRAPH_RES_HINT_4M", 0x20000),
                ("DIFLAG_BLOCKVEHICLESNEARBY", 0x40000),
                ("DIFLAG_SCRIPTED_INVINCIBLE", 0x80000),
                ("DIFLAG_FORCE_BRIDGE_RENDER", 0x100000),
                ("DIFLAG_IGNORE_LINKED_COLISIONS", 0x200000)
            ],
            "eSceneryClusterFlags": [
                ("SCNCLUSTER_FLAG_EXPENSIVELIGHTIN", 0x40),
                ("SCNCLUSTER_FLAG_RANDOMANGLES", 0x80),
                ("SCNCLUSTER_FLAG_90DEGREEANGLES", 0x100),
                ("SCNCLUSTER_FLAG_RANDOMSIZE", 0x400),
                ("SCNCLUSTER_FLAG_STRAIGHTLINE", 0x800),
                ("SCNCLUSTER_FLAG_RECTANGLE", 0x1000),
                ("SCNCLUSTER_FLAG_ALIGNTOTERRAINNO", 0x4000)
            ],
            "eCameraFlag": [
                ("eCAMFLAG_INTERPOLATEFROMCHOPPERH", 1),
                ("eCAMFLAG_INTERPOLATEFOVFROMCHOPP", 4),
                ("eCAMFLAG_EXTERNALFOV", 8),
                ("eCAMFLAG_DOLOOKOFFSETY", 0x10),
                ("eCAMFLAG_ALWAYSFACEFORWARDS", 0x200),
                ("eCAMFLAG_INTERPOLATELAG", 0x400),
                ("eCAMFLAG_DOESSHAKE", 0x800),
                ("eCAMFLAG_INTERPOLATEMOTIONBLUR", 0x1000)
            ],
            "eCamInstanceFlag": [
                ("eCINST_FIRSTCAM", 1),
                ("eCINST_CUTCAM", 2),
                ("eCINST_SCREEN_1_CAM", 4),
                ("eCINST_SCREEN_2_CAM", 8),
                ("eCINST_PLAYER_CAM", 0x10),
                ("eCINST_SCREEN_3_CAM", 0x20),
                ("eCINST_SCREEN_4_CAM", 0x40),
                ("eCINST_FORCELODBIAS", 0x80)
            ],
            "e32DamageZoneUnits": [
                ("COL_VEHICLE", 0x40),
                ("COL_AIRCRAFT", 0x80),
                ("COL_INFANTRY", 0x100)
            ],
            "eZoneFlags": [
                ("ZONEFLAG_3D", 1)
            ],
            "eExplodeFlags": [
                ("EXPLODEFLAG_FRAGMENTMODEL", 1),
                ("EXPLODEFLAG_SINGLEFRAGMENT", 2),
                ("EXPLODEFLAG_FRAGMENTALLBUTROOT", 4),
                ("EXPLODEFLAG_SIZEFROMEXPLODER", 8),
                ("EXPLODEFLAG_LIGHTOBJECTS", 0x10),
                ("EXPLODEFLAG_LIGHTLANDSCAPE", 0x20),
                ("EXPLODEFLAG_SCREENFLASH", 0x40),
                ("EXPLODEFLAG_DARKENOBJECT", 0x80),
                ("EXPLODEFLAG_SCORCHMARK", 0x200),
                ("EXPLODEFLAG_ROOTNODEFLYOFF", 0x400),
                ("EXPLODEFLAG_MODELS_HALF_ALPHA", 0x800),
                ("EXPLODEFLAG_PARTICLES_USEVECTOR", 0x1000),
                ("EXPLODEFLAG_WAVEMODEL_ROTATE", 0x2000),
                ("EXPLODEFLAG_THROWLIVEMODEL", 0x4000),
                ("EXPLODEFLAG_USEREALVERTICAL", 0x8000),
                ("EXPLODEFLAG_CATASTROPHIC", 0x10000),
                ("EXPLODEFLAG_SEQUENCED", 0x20000),
                ("EXPLODEFLAG_STICKEMITTERTOMODEL", 0x40000),
                ("EXPLODEFLAG_UNDERWATER", 0x80000),
                ("EXPLODEFLAG_SCORCHLASTFOREVER", 0x100000),
                ("EXPLODEFLAG_MAKECAMERASHAKE", 0x200000),
                ("EXPLODEFLAG_DAMAGEONLYSUBMERGED", 0x400000)
            ],
            "eIncidentalFlag": [
                ("IFLAG_BOUNCEONGROUND", 1),
                ("IFLAG_SHATTERONGROUND", 2),
                ("IFLAG_VANISHOFFSCREEN", 4),
                ("IFLAG_FACEALONGMOVEMENT", 8),
                ("IFLAG_RANDOMTUMBLE", 0x20),
                ("IFLAG_PICK_RANDOM_MODEL", 0x40),
                ("IFLAG_HITFLOOR_LOWEST", 0x100),
                ("IFLAG_HITFLOOR_HIGHEST", 0x80)
            ],
            "eProjectileFlag": [
                ("sProjectileBase::BULLETFLAG_GUIDED", 1),
                ("sProjectileBase::BULLETFLAG_SMOKETRAIL", 2),
                ("sProjectileBase::BULLETFLAG_FALLATENDOFLIFE", 4),
                ("sProjectileBase::BULLETFLAG_GROUNDIMPACTBURST", 8),
                ("sProjectileBase__BULLETFLAG_DOSH", 0x10),
                ("sProjectileBase::BULLETFLAG_FLAMETHROWER", 0x20),
                ("sProjectileBase::BULLETFLAG_HEAT_DURING_FLIGHT", 0x40),
                ("sProjectileBase::BULLETFLAG_GROUNDEXPLOSION", 0x80),
                ("sProjectileBase::BULLETFLAG_WATERIMPACTBURST", 0x100),
                ("sProjectileBase::BULLETFLAG_EXPLODEONMISS", 0x200),
                ("sProjectileBase::BULLETFLAG_BOUNCE", 0x400),
                ("sProjectileBase::BULLETFLAG_SHOTGUN_CONE", 0x800),
                ("sProjectileBase::BULLETFLAG_BALLISTIC_TRAJECTORY", 0x1000),
                ("sProjectileBase::BULLETFLAG_UNDERWATER", 0x2000),
                ("sProjectileBase::BULLETFLAG_UNDERWATERTRAIL", 0x4000),
                ("sProjectileBase::BULLETFLAG_DEPTHTRIGGER", 0x8000),
                ("sProjectileBase::BULLETFLAG_RUNNINGDEPTH", 0x10000),
                ("sProjectileBase::BULLETFLAG_MELEEBLOCKABLE", 0x20000),
                ("sProjectileBase::BULLETFLAG_GUIDEDBOMB", 0x40000)
            ],
            "eWorldObjFlags": [
                ("eWORLDOBJ_FLAG_DRAW_REFLECTION", 1)
            ],
            "eIdleActionStateFlags": [
                ("IDLE_INWATER", 1),
                ("IDLE_OUTOFWATER", 2),
                ("IDLE_ACTIONWAIT", 4),
                ("IDLE_ACTIONFOLLOW", 8),
                ("IDLE_ACTIONGUARD", 0x10),
                ("IDLE_ACTIONPOW", 0x20),
                ("IDLE_PLAYER", 0x40),
                ("IDLE_VEHCILEDRIVER", 0x100000),
                ("IDLE_VEHCILEPASSENGER", 0x200000),
                ("IDLE_VEHCILEGUNNER", 0x400000)
            ],
            "eTroopVoiceFlags": [
                ("IS_INTERRUPTIBLE", 2),
                ("PLAY_IMMEDIATE", 1)
            ],
            "eSeatFlags": [
                ("SEATFLAG_ACTIVE", 1),
                ("SEATFLAG_SOLDIER", 2),
                ("SEATFLAG_VEHICLE", 4),
                ("SEATFLAG_AUTOMATIC", 0x20),
                ("SEATFLAG_PHANTOM", 0x40),
                ("SEATFLAG_UNLOCKED", 0x80),
                ("SEATFLAG_NO_EXIT", 0x100)
            ],
            "eAiUnitFlags": [
                ("AIUNIT_ORGANIC", 1),
                ("UNKNOWN", 2),
                ("UNKNOWN 2", 4),
                ("AIUNIT_UPRIGHT", 8),
                ("AIUNIT_UPRIGHT_Z", 0x10),
                ("AIUNIT_ALWAYS_STATIC", 0x80),
                ("AIUNIT_NO_COL_REACTION", 0x100),
                ("AIUNIT_DETAILED_BULLET_COL", 0x1000),
                ("AIUNIT_EXPLODE_LAUNCH", 0x2000),
                ("AIUNIT_AVOID_PLAYER", 0x4000),
                ("AIUNIT_REACT_TO_BULLET_HIT", 0x8000),
                ("AIUNIT_NO_AVOIDANCE", 0x20000),
                ("AIUNIT_WATER_AVOID", 0x40000),
                ("AIUNIT_NO_TARGET_AIM_ROTX", 0x80000),
                ("AIUNIT_ENEMIES_CAN_GET_IN", 0x100000)
            ],
            "eAiUnitInstanceFlags": [
                ("AIUNIT_INITIALLY_DONT_IDLE_TURN", 1),
                ("AIUNIT_NEVER_IDLE_TURN", 2),
                ("AIUNIT_INACTIVE", 4),
                ("AIUNIT_NOT_SCORED", 8),
                ("AIUNIT_NOT_COMMANDABLE", 0x10),
                ("AIUNIT_CAN_IGNORE_BOUNDARY", 0x20),
                ("AIUNIT_STARTS_AS_POW", 0x40)
            ],
            "BuildingFlags": [
                ("AIUNIT_ENEMIES_CAN_GET_IN", 0x100000)
            ],
            "eTerrainParticleFlags": [
                ("eTERRAIN_PARTICLE_FLAG_NO_UNDERW", 1),
                ("eTERRAIN_PARTICLE_FLAG_SIZE_BASE", 2),
                ("eTERRAIN_PARTICLE_FLAG_UV_FLIP_V", 4),
                ("eTERRAIN_PARTICLE_FLAG_SIZE_VARI", 8),
                ("eTERRAIN_PARTICLE_FLAG_SIZE_NO_S", 0x10)
            ],
            "eSoundFlags": [
                ("PLAY_PAN", 1),
                ("PLAY_ATTENUATE", 2),
                ("PLAY_DOPPLER", 4),
                ("PLAY_STATIONARY", 0x10),
                ("PLAY_NOT_TV", 0x800),
                ("PLAY_REMOTE", 0x1000)
            ],
            "eAmbientAreaPointSounds": [
                ("AAPS_VARY_POSITION", 1),
                ("AAPS_NOT_USER_ACTIVE", 4)
            ],
            "eGUIRendFlags": [
                ("eGUIRendFlagSolidAlpha", 1)
            ],
            "eActionParameterFlags": [
                ("AP_SHOOT_ON_SIGHT", 1),
                ("AP_RETURN_FIRE", 2),
                ("AP_RETURN_FIRE_IF_ALLY_SHOT", 4),
                ("AP_SHOOT_IF_IN_PERSONAL_SPACE", 8),
                ("AP_FOLLOW_TARGET_FOREVER", 0x10),
                ("AP_ATTACK_UNTIL_NO_TARGETS", 0x20),
                ("AP_ALLOW_REGROUP", 0x100),
                ("AP_USE_COVER", 0x200),
                ("AP_USE_PICKUPS", 0x400),
                ("AP_ALLOW_HIDING", 0x800),
                ("AP_RESPOND_TO_SUMMARY_ICONS", 0x1000),
                ("AP_INCLUDE_BONUS_FOR_PLAYERS_CUR", 0x2000)
            ]
    }
}

FLAG_TYPES_USAGES = {
    "mUnitInstanceFlags": ("eAiUnitInstanceFlags",
                           ["cAirVehicle", "cTroop", "cGroundVehicle"]),
    "mUnitFlags": ("eAiUnitFlags",
                   ["sTroopBase", "sAirVehicleBase", "cGroundVehicleBase"]),
}

FLAG_TYPES = {}
for fieldname, data in FLAG_TYPES_USAGES.items():
    flag_name, usages = data

    for usage in usages:
        FLAG_TYPES[usage, fieldname] = flag_name

FLAG_TYPES["cSoundBase", "mFlags"] = "eSoundFlags"
FLAG_TYPES["cCameraBase", "mCamFlags"] = "eCameraFlag"
FLAG_TYPES["cWaypoint", "Flags"] = "eWaypointFlags"
FLAG_TYPES["sExplodeBase", "mObjFlags"] = "eExplodeFlags"
FLAG_TYPES["cIncidentalBase", "ObjFlags"] = "eIncidentalFlag"
FLAG_TYPES["cCamera", "mInstanceFlags"] = "eCamInstanceFlag"
FLAG_TYPES["sDestroyBase", "ObjFlags"] = "eDestroyFlags"
FLAG_TYPES["sSceneryClusterBase", "ObjFlags"] = "eSceneryClusterFlags"
FLAG_TYPES["cAnimationTriggeredEffectChainItemGroundImpact", "mFlags"] = "eAnimationTriggeredEffectChainItemFlags"
FLAG_TYPES["cAdvancedWeaponBase", "Flags"] = "eWeaponBaseFlag"
FLAG_TYPES["sProjectileBase", "mObjFlags"] = "eProjectileFlag"
FLAG_TYPES["sWeaponBase", "Flags"] = "eWeaponBaseFlag"
FLAG_TYPES["cSeatBase", "SeatFlags"] = "eSeatFlags"
FLAG_TYPES["sExplodeBase", "mObjFlags"] = "eExplodeFlags"
FLAG_TYPES["cIncidentalBase", "ObjFlags"] = "eIncidentalFlag"
FLAG_TYPES["cTerrainParticleGeneratorBase", "miFlags"] = "eTerrainParticleFlags"
FLAG_TYPES["cMapZone", "mFlags"] = "eZoneFlags"
FLAG_TYPES["cAnimationTriggeredEffectChainItemSound", "mFlags"] = "eAnimationTriggeredEffectChainItemFlags"
FLAG_TYPES["cAnimationTriggeredEffectChainItemTequilaEffect", "mFlags"] = "eAnimationTriggeredEffectChainItemFlags"
FLAG_TYPES["cTroopVoiceMessageBase", "mFlags"] = "eTroopVoiceFlags"
FLAG_TYPES["cObjective", "mFlags"] = "eObjectiveFlags"
FLAG_TYPES["cAmbientAreaPointSoundSphere", "mFlags"] = "eAmbientAreaPointSounds"
FLAG_TYPES["cDestroyableObject", "mInstanceFlags"] = "eDestroyableInstanceFlags"
FLAG_TYPES["cObjectiveMarker", "mFlags"] = "eObjectiveMarkerFlags"
FLAG_TYPES["cAmbientAreaPointSoundBox", "mFlags"] = "eAmbientAreaPointSounds"
FLAG_TYPES["cBuildingImpBase", "mUnitFlags"] = "eAiUnitFlags"
FLAG_TYPES["cBuilding", "mUnitInstanceFlags"] = "eAiUnitInstanceFlags"
FLAG_TYPES["cCapturePointBase", "mUnitFlags"] = "eAiUnitFlags"
FLAG_TYPES["cCapturePoint", "mUnitInstanceFlags"] = "eAiUnitInstanceFlags"
FLAG_TYPES["cDamageZone", "mUnitsDamagedFlags"] = "e32DamageZoneUnits"
FLAG_TYPES["cDamageZone", "mFlags"] = "eZoneFlags"
FLAG_TYPES["cCoastZone", "mFlags"] = "eZoneFlags"
FLAG_TYPES["cNogoHintZone", "mFlags"] = "eZoneFlags"
#FLAG_TYPES["cWaterVehicle", "mUnitInstanceFlags"]

FLAG_TYPES["cWaterVehicleBase", "mWaterVehicleFlags"] = "eWaterVehicleFlags"

FLAG_TYPES["cSeatBase", "SeatFlags"] = "eSeatFlags"





def get_field_name(object_type, fieldname):
    return FLAG_TYPES.get((object_type, fieldname))


def make_getter(obj, attr, index=None):
    def get():
        val = getattr(obj, attr)
        if isinstance(val, list):
            return val[index]
        else:
            return val

    return get


def make_setter(obj, attr, index=None):
    def changed(newval):
        val = getattr(obj, attr)
        if isinstance(val, list):
            val[index] = newval
        else:
            setattr(obj, attr, newval)

    return changed


def make_getter_index(obj, index):
    def get():
        return obj[index]

    return get


def make_setter_index(obj, index):
    def changed(newval):
        obj[index] = newval

    return changed


class PythonIntValidator(QtGui.QValidator):
    def __init__(self, min, max, parent):
        super().__init__(parent)
        self.min = min
        self.max = max

    def validate(self, p_str, p_int):
        if p_str == "" or p_str == "-":
            return QtGui.QValidator.State.Intermediate, p_str, p_int

        try:
            result = int(p_str)
        except:
            return QtGui.QValidator.State.Invalid, p_str, p_int

        if self.min <= result <= self.max:
            return QtGui.QValidator.State.Acceptable, p_str, p_int
        else:
            return QtGui.QValidator.State.Invalid, p_str, p_int

    def fixup(self, s):
        pass


def make_labeled_widget(parent, text, widget: QtWidgets.QWidget):
    labelwidget = QtWidgets.QWidget(parent)
    layout = QtWidgets.QHBoxLayout(labelwidget)
    layout.setContentsMargins(0, 0, 0, 0)
    labelwidget.setLayout(layout)
    label = QtWidgets.QLabel(labelwidget)
    label.setText(text)
    layout.addWidget(label)
    layout.addWidget(widget)

    return labelwidget


class DecimalInputNormal(QtWidgets.QLineEdit):
    changed = QtCore.pyqtSignal()

    def __init__(self, parent, get_value, set_value, min=-math.inf, max=math.inf):
        super().__init__(parent)
        self.get_value = get_value
        self.set_value = set_value

        self.min = None
        self.max = None

        self.setValidator(QtGui.QDoubleValidator(min, max, 6, self))
        self.textChanged.connect(self.changed_value)

    def get_searchable_values(self):
        return [self.text()]

    def update_value(self):
        val = self.get_value()
        self.blockSignals(True)
        self.setText(str(val))
        self.blockSignals(False)

    def changed_value(self, value):
        val = float(value)
        self.set_value(val)
        self.changed.emit()


class DecimalInput(QtWidgets.QLineEdit):
    changed = QtCore.pyqtSignal()

    def __init__(self, parent, get_value, set_value, min=-math.inf, max=math.inf):
        super().__init__(parent)
        self.get_value = get_value
        self.set_value = set_value

        self.min = None
        self.max = None

        self.setValidator(QtGui.QDoubleValidator(min, max, 6, self))
        self.textChanged.connect(self.changed_value)

        self.start_x = None
        self.setCursor(QtCore.Qt.CursorShape.SizeHorCursor)
        self.scaling_factor = 1
        self.scale_down = False
        self.currvalue = None

    def get_searchable_values(self):
        return [self.text()]

    def keyPressEvent(self, a0: typing.Optional[QtGui.QKeyEvent]) -> None:
        super().keyPressEvent(a0)
        event: QtGui.QKeyEvent = a0

        if event.key() == QtCore.Qt.Key.Key_Shift:
            self.scale_down = True

    def keyReleaseEvent(self, a0: typing.Optional[QtGui.QKeyEvent]) -> None:
        super().keyReleaseEvent(a0)
        event: QtGui.QKeyEvent = a0

        if event.key() == QtCore.Qt.Key.Key_Shift:
            self.scale_down = False

    def mousePressEvent(self, a0: typing.Optional[QtGui.QMouseEvent]) -> None:
        super().mousePressEvent(a0)

        event: QtGui.QMouseEvent = a0
        self.currvalue = self.get_value()
        self.start_x = event.pos().x()

    def mouseMoveEvent(self, a0: typing.Optional[QtGui.QMouseEvent]) -> None:
        if self.start_x is not None:
            event: QtGui.QMouseEvent = a0
            diff = event.pos().x() - self.start_x

            if self.scale_down:
                value = round(self.currvalue + diff * self.scaling_factor * 0.01, 6)
            else:
                value = round(self.currvalue + diff * self.scaling_factor, 6)
            self.setText(str(value))

    def mouseReleaseEvent(self, a0: typing.Optional[QtGui.QMouseEvent]) -> None:
        self.start_x = None
        self.scale_down = False

    def update_value(self):
        val = self.get_value()
        self.blockSignals(True)
        self.setText(str(val))
        self.blockSignals(False)

    def changed_value(self, value):
        val = float(value)
        self.set_value(val)
        self.changed.emit()


class IntegerInput(QtWidgets.QLineEdit):
    changed = QtCore.pyqtSignal()

    def __init__(self, parent, type, get_value, set_value):
        super().__init__(parent)
        self.get_value = get_value
        self.set_value = set_value

        self.min = None
        self.max = None
        # print(type)
        if type == "sInt8":
            self.min, self.max = -128, 127
        elif type == "sInt16":
            self.min, self.max = -(2 ** 15), (2 ** 15) - 1
        elif type == "sInt32":
            self.min, self.max = -(2 ** 31), (2 ** 31) - 1
        elif type == "sUInt8":
            self.min, self.max = 0, 255
        elif type == "sUInt16":
            self.min, self.max = 0, (2 ** 16) - 1
        elif type == "sUInt32":
            self.min, self.max = 0, (2 ** 32) - 1

        self.setValidator(PythonIntValidator(self.min, self.max, self))
        self.textChanged.connect(self.changed_value)

    def get_searchable_values(self):
        return [self.text()]

    def update_value(self):
        value = int(self.get_value())
        if value < self.min:
            print(f"WARNING: Value out of range: {value} will be capped to {self.min}")
            value = self.min
        if value > self.max:
            print(f"WARNING: Value out of range: {value} will be capped to {self.max}")
            value = self.max

        self.blockSignals(True)
        self.setText(str(value))
        self.blockSignals(False)

    def changed_value(self, value):
        val = int(value)
        if self.min <= val <= self.max:
            self.set_value(val)
            self.changed.emit()


class StrongFocusComboBox(QtWidgets.QComboBox):
    def __init__(self, *args, editable=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setStyleSheet("QComboBox {combobox-popup: 0;}")

        self.items_total = []
        self.optimize = False
        self.callback = lambda: True
        if editable:
            self.setEditable(True)

    def get_searchable_values(self):
        return [self.currentText()]

    def full_callback(self, func):
        self.callback = func

    def showPopup(self) -> None:
        if self.optimize:
            self.callback()

        super().showPopup()

    def optimize_large_sets(self):
        self.optimize = True
        self.setMinimumContentsLength(int(self.minimumContentsLength() * 1.2))
        self.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)

    def wheelEvent(self, event) -> None:
        if not self.hasFocus():
            event.ignore()
        else:
            super().wheelEvent(event)


class EnumBox(StrongFocusComboBox):
    changed = QtCore.pyqtSignal()

    def __init__(self, parent, items, get_value, set_value):
        super().__init__(parent)
        self.items = []
        for item in items:
            self.addItem(item)
            self.items.append(item)

        self.get_value = get_value
        self.set_value = set_value
        self.currentTextChanged.connect(self.change)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

    def get_searchable_values(self):
        return [self.currentText()]

    def update_value(self):
        value = self.get_value()
        self.blockSignals(True)
        if value not in self.items:
            self.setCurrentIndex(0)
        else:
            self.setCurrentText(value)
        self.blockSignals(False)

    def change(self, value):
        assert value in self.items

        self.set_value(value)
        self.changed.emit()


class BooleanEnumBox(EnumBox):
    def __init__(self, parent, get_value, set_value):
        super().__init__(parent, ["False", "True"], get_value, set_value)

    def update_value(self):
        value = self.get_value()
        self.blockSignals(True)
        if value:
            self.setCurrentIndex(1)
        else:
            self.setCurrentIndex(0)
        self.blockSignals(False)

    def change(self, value):
        self.set_value(value == "True")
        self.changed.emit()


class DecimalVector4Edit(QtWidgets.QWidget):
    changed = QtCore.pyqtSignal()

    def __init__(self, parent, get_value):
        super().__init__(parent)
        self.vector_layout = QtWidgets.QHBoxLayout(self)
        self.vector_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.setLayout(self.vector_layout)
        self.edits = []
        vector = get_value()
        for i in ("x", "y", "z", "w"):
            getter = make_getter(vector, i)
            setter = make_setter(vector, i)

            labeled_widget = QtWidgets.QWidget(self)
            label_layout = QtWidgets.QHBoxLayout(labeled_widget)
            labeled_widget.setLayout(label_layout)
            label_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

            label = QtWidgets.QLabel(i, self)
            decimal_edit = DecimalInput(self, getter, setter)
            label_layout.addWidget(label)
            label_layout.addWidget(decimal_edit)

            self.edits.append(decimal_edit)
            self.vector_layout.addWidget(labeled_widget)

            decimal_edit.changed.connect(lambda x: self.changed.emit())

    def get_searchable_values(self):
        return [x.text() for x in self.edits]

    def update_value(self) -> None:
        for edit in self.edits:
            edit.update_value()


class ColorView(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.color = QtGui.QColor(0, 0, 0, 255)
        self.setMinimumSize(32, 32)
        sizepolicy = self.sizePolicy()
        sizepolicy.setVerticalPolicy(QtWidgets.QSizePolicy.Policy.Fixed)
        sizepolicy.setHorizontalPolicy(QtWidgets.QSizePolicy.Policy.Fixed)
        self.setSizePolicy(sizepolicy)

    def paintEvent(self, a0) -> None:
        painter = QtGui.QPainter(self)
        h = self.height()
        painter.fillRect(0, 0, h, h, self.color)

    def change_color(self, r, g, b, a):
        self.color = QtGui.QColor(r, g, b, a)


class HighlightArrow(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.color = QtGui.QColor(0, 0, 0, 255)
        self.setMinimumSize(32, 32)
        sizepolicy = self.sizePolicy()
        sizepolicy.setVerticalPolicy(QtWidgets.QSizePolicy.Policy.Fixed)
        sizepolicy.setHorizontalPolicy(QtWidgets.QSizePolicy.Policy.Fixed)
        self.setSizePolicy(sizepolicy)

    def paintEvent(self, a0) -> None:
        painter = QtGui.QPainter(self)
        h = self.height()
        w = self.width()

        painter.setPen(self.color)
        painter.setBrush(self.color)
        """upper = h//4
        lower = upper*3
        mid = h//2
        painter.drawPolygon([
            QtCore.QPoint(0, upper),
            QtCore.QPoint(0, lower),
            QtCore.QPoint(mid, lower),
            QtCore.QPoint(mid, h),
            QtCore.QPoint(h, mid),
            QtCore.QPoint(mid, 0),
            QtCore.QPoint(mid, upper)],
            QtCore.Qt.FillRule.WindingFill
            )"""
        painter.fillRect(0, 0, w, h, self.color)

    def change_color(self, r, g, b, a):
        self.color = QtGui.QColor(r, g, b, a)


class MatrixEdit(QtWidgets.QWidget):
    changed = QtCore.pyqtSignal()

    def __init__(self, parent, get_value):
        super().__init__(parent)
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)

        self.get_value = get_value

        matrix: BWMatrix = self.get_value()
        self.edits = []
        self.decomposed = list(decompose(matrix))

        self.grid_layout.addWidget(QtWidgets.QLabel("Position", self), 0, 0)
        self.grid_layout.addWidget(QtWidgets.QLabel("Scale", self), 1, 0)
        self.grid_layout.addWidget(QtWidgets.QLabel("Angle", self), 2, 0)

        for iy in range(3):
            for ix in range(3):
                getter = make_getter_index(self.decomposed, iy * 3 + ix)
                setter = make_setter_index(self.decomposed, iy * 3 + ix)

                text = ["x", "y", "z"][ix]

                if iy == 1:
                    index_edit = DecimalInput(self, getter, setter, min=0.0001)
                else:
                    index_edit = DecimalInput(self, getter, setter)

                labeled = make_labeled_widget(self, text, index_edit)

                self.grid_layout.addWidget(labeled, iy, ix + 1)
                self.edits.append(index_edit)
                index_edit.textChanged.connect(self.recompose_matrix)

        """
        for ix in range(4):
            for iy in range(4):
                getter = make_getter_index(matrix.mtx, iy*4+ix)
                setter = make_setter_index(matrix.mtx, iy*4+ix)

                index_edit = DecimalInput(self, getter, setter)
                self.grid_layout.addWidget(index_edit, ix, iy)
                self.edits.append(index_edit)"""

    def get_searchable_values(self):
        return [x.text() for x in self.edits] + ["Position", "Scale", "Angle", "x", "y", "z"]

    def update_value(self):
        for edit in self.edits:
            edit.blockSignals(True)
            edit.update_value()
            edit.blockSignals(False)

    def recompose_matrix(self):
        matrix = self.get_value()
        recomposed = recompose(*self.decomposed)
        matrix.mtx[:15] = recomposed.mtx[:15]
        self.changed.emit()


class Vector4Edit(QtWidgets.QWidget):
    changed = QtCore.pyqtSignal()

    def __init__(self, parent, vtype, get_value):
        super().__init__(parent)
        assert vtype in ("sVector4", "sU8Color", "sVectorXZ", "cU8Color")
        self.vector_layout = QtWidgets.QHBoxLayout(self)
        self.vector_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.setLayout(self.vector_layout)
        self.edits = []

        self.get_value = get_value
        vector = get_value()

        components = ("x", "y", "z", "w")
        if vtype == "sVectorXZ":
            components = ("x", "z")

        for i in components:
            getter = make_getter(vector, i)
            setter = make_setter(vector, i)

            labeled_widget = QtWidgets.QWidget(self)
            label_layout = QtWidgets.QHBoxLayout(labeled_widget)
            labeled_widget.setLayout(label_layout)
            label_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

            if vtype == "sVector4" or vtype == "sVectorXZ":
                label = QtWidgets.QLabel(i, self)
                decimal_edit = DecimalInput(self, getter, setter)
            elif vtype == "sU8Color" or vtype == "cU8Color":
                comp = {"x": "Red", "y": "Green", "z": "Blue", "w": "Alpha"}[i]
                label = QtWidgets.QLabel(comp, self)
                decimal_edit = IntegerInput(self, "sUInt8", getter, setter)

            label_layout.addWidget(label)
            label_layout.addWidget(decimal_edit)
            decimal_edit.changed.connect(lambda: self.changed.emit())

            self.edits.append(decimal_edit)
            self.vector_layout.addWidget(labeled_widget)

        if vtype == "sU8Color" or vtype == "cU8Color":
            self.color = ColorView(self)
            self.vector_layout.addWidget(self.color)
            for edit in self.edits:
                edit: IntegerInput
                edit.textChanged.connect(self.update_color)
        else:
            self.color = None

    def get_searchable_values(self):
        return [x.text() for x in self.edits]

    def update_color(self):
        if self.color is not None:
            col = self.get_value()
            self.color.change_color(int(col.x), int(col.y), int(col.z), int(col.w))
            self.color.update()

    def update_value(self) -> None:
        for edit in self.edits:
            edit.update_value()
        self.update_color()


class FlagBox(QtWidgets.QWidget):
    changed = QtCore.pyqtSignal()

    def __init__(self, parent, items, get_value, set_value):
        super().__init__(parent)
        self.flag_layout = QtWidgets.QGridLayout(self)
        self.setLayout(self.flag_layout)

        self.flags = []

        self.get_value = get_value
        self.set_value = set_value

        self.value = QtWidgets.QLabel(self)
        self.flag_layout.addWidget(self.value)

        i = 0
        for flagname, value in items:
            checkbutton = QtWidgets.QCheckBox(self)
            checkbutton.setText(flagname)

            self.flags.append((checkbutton, value))

            row = i // 2 + 1
            column = i % 2
            self.flag_layout.addWidget(checkbutton, row, column)
            checkbutton.stateChanged.connect(self.change)
            i += 1

    def get_searchable_values(self):
        out = []
        for button, value in self.flags:
            out.append(button.text())

        return out

    def update_value(self):
        val = self.get_value()
        checked = 0
        for button, value in self.flags:
            print(button.text())
            button: QtWidgets.QRadioButton
            button.blockSignals(True)
            button.setChecked(val & value)
            button.blockSignals(False)
            checked += value

        self.value.setText(f"Combined flag value: {val}")

        if (val & ~checked) != 0:
            raise RuntimeError(f"WARNING: Bits unaccounted for with value {val} vs {checked}")

    def change(self):
        newval = 0
        for button, value in self.flags:
            if button.isChecked():
                newval |= value
        self.value.setText(f"Combined flag value: {newval}")
        self.set_value(newval)
        self.changed.emit()


SUBSETS = {
    "cUnit": ["cTroop", "cGroundVehicle", "cWaterVehicle", "cAirVehicle", "cBuilding"],
    "sWeaponBase": ["cAdvancedWeaponBase"],
    "cAnimationTriggeredEffectChainItemBase": [
        "cAnimationTriggeredEffectChainItemGroundImpact",
        "cAnimationTriggeredEffectChainItemSound",
        "cAnimationTriggeredEffectChainItemTequilaEffect"],
    "cTaggedEffectBase": [
        "cSimpleTequilaTaggedEffectBase",
        "cImpactTableTaggedEffectBase"
    ],
    "cEntity": ["cWaypoint", "cCamera", "cMapZone", "cAmbientAreaPointSoundSphere",
                "cDestroyableObject", "cSceneryCluster", "cTroop", "cGroundVehicle",
                "cAirVehicle", "cObjectiveMarker", "cReflectedUnitGroup", "cPickupReflected",
                "cAmbientAreaPointSoundBox", "cBuilding", "cCapturePoint", "cDamageZone",
                "cMorphingBuilding", "cCoastZone", "cWaterVehicle", "cNogoHintZone"],
    "cGUIMetaNumber": ["cGUINumberNumber", "cGUINumberFromFunction", "cGUINumberFromLabel"],
    "cGUIMetaVector": ["cGUIVectorVector", "cGUIVectorFromLabel", "cGUIVectorFromFunction"],
    "cGUIMetaColour": ["cGUIColourColour", "cGUIColourFromFunction", "cGUIColourFromLabel",
                       "cGUIColourNumber"],
    "cGUIMetaScale": ["cGUIScaleVector", "cGUIScaleFromFunction", "cGUIScaleFromLabel"],
    "cGUIMetaBool": ["cGUIBoolFromLabel", "cGUIBoolBool", "cGUIBoolFromFunction"],
    "cGUIMetaString": ["cGUIStringFromLabel", "cGUIStringString", "cGUIStringFromFunction"],
    "cGUIWidget": ["cGUIButtonWidget", "cGUISpriteWidget", "cGUITextureWidget", "cGUICustomWidget",
                   "cGUITextBoxWidget", "cGUIRectWidget", "cGUIVertexColouredRectWidget",
                   "cGUITequilaWidget", "cGUI3DObjectWidget", "cGUIListBoxWidget", "cGUISliderWidget"],
    "cGUISpriteWidget": ["cGUIButtonWidget"],
    "cGUIMetaMatrix": ["cGUIMatrixFromLabel"]

}

SUBSETS["cWorldObject"] = SUBSETS["cEntity"]


class ReferenceEdit(QtWidgets.QWidget):
    changed = QtCore.pyqtSignal()

    def __init__(self, parent,
                 objects: BattalionLevelFile,
                 preload: BattalionLevelFile,
                 type,
                 get_value,
                 set_value):
        super().__init__(parent)
        self.objects = objects
        self.preload = preload
        self.get_value = get_value
        self.set_value = set_value
        self.type = type

        # line_1_holder = QtWidgets.QWidget(self)
        # line_2_holder = QtWidgets.QWidget(self)
        line_1 = QtWidgets.QHBoxLayout(self)
        # line_2 = QtWidgets.QHBoxLayout(self)
        # line_1_holder.setLayout(line_1)
        # line_2_holder.setLayout(line_2)

        self.gridlayout = QtWidgets.QGridLayout(self)
        # line_1.setContentsMargins(0, 0, 0, 0)
        # line_2.setContentsMargins(0, 0, 0, 0)

        self.object_combo_box = StrongFocusComboBox(self, editable=True)
        self.object_combo_box.optimize_large_sets()
        self.object_combo_box.setMaxVisibleItems(20)
        self.edit_button = QtWidgets.QPushButton("Edit", self)
        self.set_to_selected_button = QtWidgets.QPushButton("Set To Selected", self)
        self.goto_button = QtWidgets.QPushButton("Goto/Select", self)
        self.object_combo_box.currentIndexChanged.connect(self.change_object)
        self.object_combo_box.lineEdit().editingFinished.connect(self.change_object_text)

        self.copy_button = QtWidgets.QPushButton(parent=self, icon=ICONS["COPY"])
        self.copy_button.setToolTip("Copy ID into Clipboard")
        self.copy_button.pressed.connect(self.copy_id_into_clipboard)

        self.object_combo_box.setMinimumWidth(200)
        line_1.addWidget(self.object_combo_box)
        line_1.addWidget(self.copy_button)
        line_1.addWidget(self.edit_button)
        line_1.addWidget(self.set_to_selected_button)
        line_1.addWidget(self.goto_button)

        # self.gridlayout.addWidget(line_1_holder, 0, 0)
        # self.gridlayout.addWidget(line_2_holder, 1, 0)
        self.setLayout(line_1)

    def get_searchable_values(self):
        obj = self.get_value()

        if obj is None:
            return []
        else:
            return [obj.id, obj.name]

    def install_filter(self, filt):
        self.installEventFilter(filt)
        self.object_combo_box.installEventFilter(filt)

    def change_object_text(self, *args, **kwargs):
        print("text changed", self.object_combo_box.currentText())
        curr = self.get_value()
        default = "None" if curr is None else curr.name

        id = self.object_combo_box.currentText()
        if id in self.objects.objects:
            obj = self.objects.objects[id]
        elif id in self.preload.objects:
            obj = self.preload.objects[id]
        else:
            obj = None

        if obj is not None:
            check_types = [self.type]
            if self.type in SUBSETS:
                check_types.extend(SUBSETS[self.type])

            if obj.type not in check_types:
                open_message_dialog(
                    f"Warning!\n"
                    f"Object {obj.name} cannot be used because it has incompatible type {obj.type})")
                self.object_combo_box.setCurrentText(default)
            else:
                self.set_value(obj)
                self.object_combo_box.setCurrentText(obj.name)
                self.changed.emit()
        elif id == "0":
            self.set_value(None)
            self.object_combo_box.setCurrentIndex(0)
            self.changed.emit()
        else:
            self.object_combo_box.setCurrentText(default)

    def copy_id_into_clipboard(self):
        obj = self.get_value()
        if obj is None:
            value = 0
        else:
            value = obj.id

        clipboard = QtGui.QGuiApplication.clipboard()
        clipboard.setText(str(value))

    def update_value(self, item_cache=None, large_set_optimize=False):
        self.object_combo_box.blockSignals(True)
        self.object_combo_box.clear()

        currobj = self.get_value()

        if large_set_optimize:
            self.object_combo_box.addItem(currobj.name)
            self.object_combo_box.full_callback(partial(self.update_value, item_cache))
            self.object_combo_box.setCurrentIndex(0)
        else:

            """
            noitem = QtWidgets.QListWidgetItem()
            noitem.setText("None")
            noitem.obj = None
            curritem = noitem
            items = []
            for objtype, objlist in chain(self.objects.category.items(), self.preload.category.items()):
                if self.is_instance(objtype):
                    for objid, object in objlist.items():
                        item = QtWidgets.QListWidgetItem()
                        item.setText(object.name)
                        item.obj = object
                        items.append(item)
                        if object == currobj:
                            curritem = item

            if currobj is not None and curritem == noitem:
                self.object_combo_box.blockSignals(False)
                raise RuntimeError(f"Failed to assign object: {currobj.type}")

            items.sort(key=lambda x: x.text())
            items.insert(0, noitem)
            currindex = items.index(curritem)
            self.items = items
            for item in items:
                self.object_combo_box.addItem(item.text(), item.obj)"""
            noitem = ("None", None)
            curritem = noitem

            items = []
            wrong_object = None
            # for objtype, objlist in chain(self.objects.category.items(), self.preload.category.items()):
            #    if self.is_instance(objtype):
            check_types = [self.type]
            if self.type in SUBSETS:
                check_types.extend(SUBSETS[self.type])

            if item_cache is None or self.type not in item_cache:
                for category in [self.objects.category, self.preload.category]:
                    for objtype in check_types:
                        if objtype in category:
                            objlist = category[objtype]
                            for objid, object in objlist.items():
                                item = (object.name, object)

                                items.append(item)
                                if object == currobj:
                                    curritem = item

                if currobj is not None and curritem == noitem:
                    checkedtypes = ", ".join(check_types)
                    open_message_dialog(f"Warning!\n"
                                        f"Tried to fit object {currobj.name} with type {currobj.type} into field that expects "
                                        f"one of {checkedtypes}.")
                    wrong_object = currobj
                    # self.object_combo_box.blockSignals(False)
                    # raise RuntimeError(f"Failed to assign object: {currobj.type}")

                items.sort(key=lambda x: x[0])
                items.insert(0, noitem)

                self.items = items
                # for item in items:
                self.object_combo_box.addItems([x[0] for x in items])
                if wrong_object is not None:
                    currindex = len(items)
                    self.object_combo_box.addItem(wrong_object.name)
                    self.wrong_object = wrong_object
                else:
                    currindex = items.index(curritem)
                self.object_combo_box.setCurrentIndex(currindex)

                if item_cache is not None:
                    item_cache[self.type] = self.items

            elif item_cache is not None and self.type in item_cache:
                if currobj is not None:
                    curritem = (currobj.name, currobj)
                else:
                    curritem = None

                items = item_cache[self.type]
                self.object_combo_box.addItems([x[0] for x in items])
                self.items = items

                try:
                    currindex = items.index(curritem)
                except ValueError:
                    if curritem is not None:
                        currindex = len(items)
                        self.object_combo_box.addItem(currobj.name)
                        checkedtypes = ", ".join(check_types)
                        open_message_dialog(f"Warning!\n"
                                            f"Tried to fit object {currobj.name} with type {currobj.type} into field that expects "
                                            f"one of {checkedtypes}.")
                    else:
                        currindex = 0

                self.object_combo_box.setCurrentIndex(currindex)
        self.object_combo_box.blockSignals(False)

    def change_object(self):
        result = self.object_combo_box.currentIndex()
        if result != -1:
            if result < len(self.items):
                obj = self.items[result][1]
                self.set_value(obj)
                if obj is not None:
                    obj.updatemodelname()
                self.changed.emit()
            else:
                currobj = self.get_value()
                if currobj is not None:
                    try:
                        index = self.items.index((currobj.name, currobj))
                    except ValueError:
                        pass
                    else:
                        self.object_combo_box.setCurrentIndex(index)
                        open_message_dialog(f"Selected object type doesn't match, selection reverted."
                                            "")

    def is_instance(self, other_type):
        if self.type == other_type:
            return True
        elif self.type in SUBSETS:
            return other_type in SUBSETS[self.type]

        return False


class DocFile(object):
    def __init__(self, classname):
        self.classname = classname
        self.docs = {}

    @classmethod
    def from_file(cls, path):
        basename: str = os.path.basename(path)
        objname = basename.removesuffix(".doc")
        doc = cls(objname)

        with open(path, "r") as f:
            lines = f.readlines()

        i = 0
        end = len(lines)
        game = None
        field = None
        fielddoc = []

        state = 0

        for i in range(0, end):
            if lines[i][0] in (">", "-") and fielddoc:
                doc.add_doc(game, objname, field, fielddoc)

            if lines[i].startswith(">"):
                state = 1
                game = lines[i][1:].strip().removesuffix(":")

            elif lines[i].startswith("-"):
                field = lines[i][1:].strip().removesuffix(":")
                fielddoc = []
                state = 2
            elif state == 2:
                assert game is not None and field is not None, "Parsing failure when reading {}".format(path)
                line = lines[i]
                fielddoc.append(line)

                if i == end - 1:
                    doc.add_doc(game, objname, field, fielddoc)

        return doc

    def add_doc(self, game, objname, field, doc):
        while doc[-1] == "\n":
            doc.pop(-1)

        if game == "BOTH":
            self.docs[("BW1", objname, field)] = "".join(doc)
            self.docs[("BW2", objname, field)] = "".join(doc)
        else:
            self.docs[(game, objname, field)] = "".join(doc)


class FieldDocumentationHolder(object):
    def __init__(self, doc_folder):
        self.docs = {}
        self.doc_folder = doc_folder
        self.last_changed = {}

        doc_files = os.listdir(doc_folder)

        for fname in doc_files:
            if fname.endswith(".doc"):
                self.read_object_doc(os.path.join(doc_folder, fname))

    def doc_needs_update(self, classname):
        if classname not in self.last_changed:
            return True

        doc_file = os.path.join(self.doc_folder, classname+".doc")
        return os.stat(doc_file).st_mtime > self.last_changed[classname]

    def update(self, classname):
        print("Checking if", classname, "needs update")
        if self.doc_needs_update(classname):
            print("Updating...")
            try:
                self.read_object_doc(os.path.join(self.doc_folder, classname+".doc"))
            except FileNotFoundError:
                pass

    def read_object_doc(self, fpath):
        objdoc: DocFile = DocFile.from_file(fpath)
        self.last_changed[objdoc.classname] = os.stat(fpath).st_mtime
        for item, doc in objdoc.docs.items():
            self.docs[item] = doc

    def add_doc(self, game, classname, fieldtype, doc):
        self.docs[(game, classname, fieldtype)] = doc

    def get_doc(self, game, classname, fieldtype):
        return self.docs.get((game, classname, fieldtype), "")

BW_DOCUMENTATION = FieldDocumentationHolder("objecthelp/")


class FieldEdit(QtCore.QObject):
    edit_obj = QtCore.pyqtSignal(str, int)
    editor_refresh = QtCore.pyqtSignal()

    def __init__(self, parent, editor, object, tag, name, type, elements, item_cache=None):
        super().__init__()
        self.object = object
        #self.edit_layout = QtWidgets.QVBoxLayout(self)
        self.name = QtWidgets.QLabel(name, parent)
        tooltip = "Data Type: {}".format(type)
        doc = BW_DOCUMENTATION

        if doc is not None:
            doc.update(object.type)
            game = "BW2" if editor.level_file.bw2 else "BW1"
            tooltip_extra = doc.get_doc(game, object.type, name)

            if tooltip_extra:
                tooltip += "\n" + tooltip_extra

        self.name.setToolTip(tooltip)
        #self.edit_layout.addWidget(self.name)
        #self.setLayout(self.edit_layout)

        #self.edit_layout.setSpacing(0)
        #self.edit_layout.setContentsMargins(0, 0, 0, 0)
        self.lines = []
        self.contents = []
        for i in range(elements):
            print("Adding", name)
            line, content = self.add_field(editor, parent, name, tag, type, i, item_cache)
            assert content is not None
            self.contents.append(content)
            self.lines.append(line)

        self.edit_button = None

    def find_text(self, text, case_sensitive):
        target = text if case_sensitive else text.lower()

        if case_sensitive:
            if target in self.name.text():
                return True, self.name
        else:
            if target in self.name.text().lower():
                return True, self.name

        for line, content in zip(self.lines, self.contents):
            if hasattr(content, "get_searchable_values"):
                values = content.get_searchable_values()

                for val in values:
                    if case_sensitive:
                        if target in val:
                            return True, content
                    else:
                        if target in val.lower():
                            return True, content

        return False, None

    def add_field(self, editor: "bw_editor.LevelEditor", parent, name, tag, type, element, item_cache=None):
        line = QtWidgets.QWidget(parent)
        #line.setContentsMargins(0, 0, 0, 0)
        line_layout = QtWidgets.QHBoxLayout(line)
        line_layout.setContentsMargins(0, 0, 0, 0)
        #line_layout.setSpacing(0)
        line_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        line_layout.addSpacing(30)

        if tag == "Enum":
            pass

        val = getattr(self.object, name)
        if isinstance(val, list):
            val = val[element]

        if editor.level_file.bw2:
            game = "BW2"
        else:
            game = "BW1"

        if tag == "Enum":
            items = ENUMS[game][type]
            getter = make_getter(self.object, name, element)
            setter = make_setter(self.object, name, element)
            if type == "eBoolean":
                content = BooleanEnumBox(line, getter, setter)
            else:
                content = EnumBox(line, items, getter, setter)
            content.update_value()
            line_layout.addWidget(content)
        elif tag == "Attribute" and get_field_name(self.object.type, name) is not None:
            flagtype = get_field_name(self.object.type, name)
            items = FLAGS[game][flagtype]

            getter = make_getter(self.object, name, element)
            setter = make_setter(self.object, name, element)

            content = FlagBox(line, items, getter, setter)
            content.update_value()
            line_layout.addWidget(content)
        elif tag == "Attribute" and type in ("sInt8", "sInt16", "sInt32",
                                                         "sUInt8", "sUInt16", "sUInt32"):
            getter = make_getter(self.object, name, element)
            setter = make_setter(self.object, name, element)

            content = IntegerInput(line, type, getter, setter)
            content.update_value()
            line_layout.addWidget(content)
        elif tag == "Attribute" and type in ("sFloat", "sFloat32"):
            getter = make_getter(self.object, name, element)
            setter = make_setter(self.object, name, element)

            content = DecimalInput(line, getter, setter)
            content.update_value()
            line_layout.addWidget(content)
        elif tag == "Attribute" and type in ("sVector4", "sU8Color", "sVectorXZ", "cU8Color"):
            getter = make_getter(self.object, name, element)

            content = Vector4Edit(line, type, getter)
            content.update_value()
            line_layout.addWidget(content)
        elif tag == "Attribute" and type in ("sMatrix4x4", "cMatrix4x4"):
            getter = make_getter(self.object, name, element)

            content = MatrixEdit(line, getter)
            content.update_value()
            line_layout.addWidget(content)
        elif tag == "Attribute" and type in ("cFxString8", "cFxString16"):
            getter = make_getter(self.object, name, element)
            setter = make_setter(self.object, name, element)

            content = StringEdit(line, getter, setter)
            content.update_value()
            line_layout.addWidget(content)
        elif tag in ("Pointer", "Resource"):
            getter = make_getter(self.object, name, element)
            setter = make_setter(self.object, name, element)

            content = ReferenceEdit(line, editor.level_file, editor.preload_file, type, getter, setter)
            content.edit_button.pressed.connect(lambda: self.edit_obj.emit(name, element))

            def model_refresh():
                for obj in editor.level_file.objects.values():
                    obj.updatemodelname()

            content.changed.connect(model_refresh)

            def set_to_selected():
                selected_obj = editor.get_selected_obj()
                if selected_obj is not None and content.is_instance(selected_obj.type):
                    setter(selected_obj)
                content.update_value()
                model_refresh()
                self.trigger_editor_refresh()

            def select_goto():
                obj = getter()
                if obj is not None:
                    editor.level_view.selected = [obj]
                    editor.pik_control.goto_object(obj.id)
                    editor.level_view.select_update.emit()

            content.set_to_selected_button.pressed.connect(set_to_selected)
            content.goto_button.pressed.connect(select_goto)

            content.update_value(item_cache)
            line_layout.addWidget(content)
        else:
            raise RuntimeError("Unknown Type")

        content.changed.connect(self.trigger_editor_refresh)

        #self.lines.append(line)
        return line, content

    def update_value(self):
        for content in self.contents:
            content.update_value()

    def trigger_editor_refresh(self):
        self.editor_refresh.emit()


class StringEdit(QtWidgets.QLineEdit):
    changed = QtCore.pyqtSignal()

    def __init__(self, parent, get_value, set_value):
        super().__init__(parent)

        self.get_value = get_value
        self.set_value = set_value
        self.textChanged.connect(self.change_value)
        self.editingFinished.connect(self.emit_change)

    def install_filter(self, filt):
        self.installEventFilter(filt)

    def get_searchable_values(self):
        return [self.text()]

    def update_value(self):
        val = self.get_value()
        if val is None:
            val = ""
        self.blockSignals(True)
        self.setText(str(val))
        self.blockSignals(False)

    def change_value(self, val):
        self.set_value(val)

    def emit_change(self):
        self.changed.emit()


class CustomNameEdit(QtWidgets.QLineEdit):
    def __init__(self, parent, get_value, set_value):
        super().__init__(parent)

        self.get_value = get_value
        self.set_value = set_value
        self.textChanged.connect(self.change_value)

    def find_text(self, value, case_sensitive):
        if case_sensitive:
            return value in self.text(), self
        else:
            return value.lower() in self.text().lower(), self

    def update_value(self):
        val = self.get_value()
        if val is None:
            val = ""
        self.blockSignals(True)
        self.setText(str(val))
        self.blockSignals(False)

    def change_value(self, val):
        val = val.strip()
        if not val:
            self.set_value(None)
        else:
            self.set_value(val)


class LuaNameEdit(QtWidgets.QWidget):
    def __init__(self, parent, get_value, set_value, name_usages, obj):
        super().__init__(parent)

        self.textinput = QtWidgets.QLineEdit(self)
        self.vbox = QtWidgets.QVBoxLayout(self)
        self.already_exists = QtWidgets.QLabel("Lua name already exists! Please use a different one.", self)
        self.vbox.addWidget(self.textinput)
        self.vbox.addWidget(self.already_exists)
        self.already_exists.setVisible(False)

        self.get_value = get_value
        self.set_value = set_value
        self.name_usages = name_usages
        self.textinput.textChanged.connect(self.change_value)
        self.object = obj
    
    def find_text(self, value, case_sensitive):
        if case_sensitive:
            return value in self.textinput.text(), self
        else:
            return value.lower() in self.textinput.text(), self

    def get_searchable_values(self):
        return [self.textinput.text()]

    def display_already_exists(self):
        self.already_exists.setVisible(True)

    def hide_already_exists(self):
        self.already_exists.setVisible(False)

    def update_value(self):
        val = self.get_value()
        if val is None:
            val = ""
        self.blockSignals(True)
        self.textinput.setText(str(val))
        self.blockSignals(False)

    def change_value(self, val):
        val = val.strip()
        if not val:
            self.hide_already_exists()
            self.set_value(None)
        else:
            usages = self.name_usages(val)
            if len(usages) > 1 or len(usages) == 1 and self.object.id not in usages:
                self.display_already_exists()
            else:
                self.hide_already_exists()
                self.set_value(val)


class TooltippedLabel(QtWidgets.QLabel):
    def __init__(self, name, parent, tooltip):
        super().__init__(name, parent)
        self.setToolTip(tooltip)


class NewEditWindow(QtWidgets.QMdiSubWindow):
    closing = QtCore.pyqtSignal()
    main_window_changed = QtCore.pyqtSignal(object)
    object_edited = QtCore.pyqtSignal(object)

    def __init__(self, parent, object: BattalionObject, editor: "bw_editor.LevelEditor", makewindow):
        super().__init__(parent)
        self.resize(900, 500)
        self.setMinimumSize(QtCore.QSize(300, 300))

        self.highlight = HighlightArrow(self)
        self.highlight.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.highlight.change_color(255, 255, 0, 50)
        self.highlight.hide()
        self.installEventFilter(self)
        if ICONS["COPY"] is None:
            ICONS["COPY"] = load_icon("resources/Copy-32x32.png")

        self.is_autoupdate = False
        self.editor = editor
        self.object = object
        self.makewindow = makewindow
        self.setWindowTitle(f"Edit Object: {object.name}")

        self.scroll_area = QtWidgets.QScrollArea(self)

        self.content_holder = QtWidgets.QWidget(self.scroll_area)

        self.scroll_area.setWidget(self.content_holder)

        self.area_layout = QtWidgets.QGridLayout(self.content_holder)
        self.area_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.content_holder.setLayout(self.area_layout)
        self.setWidget(self.scroll_area)
        self.scroll_area.setWidgetResizable(True)
        self.keep_window_on_top = False
        self.setup_rows(object)

        self.scheduled_scrollbar_pos = None
        self.scroll_area.verticalScrollBar().rangeChanged.connect(self.scroll_area_bar_update)

        self.object_edited.connect(self.update_water_level)
        self.object_edited.connect(self.reset_highlight)

        self.search_curr_row = 0

        self.find_shortcut = QtGui.QShortcut("Ctrl+F", self)
        self.find_shortcut.activated.connect(self.goto_find_box)

    def eventFilter(self, object, event) -> bool:
        result = super().eventFilter(object, event)
        if (event.type() == QtCore.QEvent.Type.MouseButtonPress):
            self.reset_highlight()
        return result

    def changeEvent(self, changeEvent: QtCore.QEvent) -> None:
        super().changeEvent(changeEvent)
        print(changeEvent.type())
        if changeEvent.type() == QtCore.QEvent.Type.ActivationChange:
            self.reset_highlight()

    def mousePressEvent(self, mouseEvent: typing.Optional[QtGui.QMouseEvent]) -> None:
        super().mousePressEvent(mouseEvent)
        self.highlight.hide()
        self.search_curr_row = 0

    def attach_highlight(self, widget):
        self.highlight.setParent(widget)
        self.highlight.setFixedSize(widget.width(), widget.height())
        self.highlight.show()

    def reset_highlight(self):
        self.highlight.hide()
        self.search_curr_row = 0

    def goto_find_box(self):
        self.search_bar.textinput.setFocus()
        self.scroll_area.ensureWidgetVisible(self.search_bar)

    def search(self, text):
        maxrows = len(self.fields)

        if self.search_curr_row >= maxrows:
            self.search_curr_row = 0

        for i in range(self.search_curr_row, maxrows):
            field = self.fields[i]

            found, widget = field.find_text(text, False)

            if found:
                self.attach_highlight(widget)
                self.scroll_area.ensureWidgetVisible(widget)
                self.search_curr_row = i+1
                break
        else:
            self.search_curr_row = 0

    def closeEvent(self, event):
        self.closing.emit()

    def change_object(self, object):
        remember_scrollbar = object.type == self.object.type
        pos = self.scroll_area.verticalScrollBar().value()

        start = default_timer()
        self.content_holder.hide()
        self.content_holder.deleteLater()
        self.content_holder.setParent(None)

        self.content_holder = QtWidgets.QWidget()
        self.scroll_area.setWidget(self.content_holder)

        self.area_layout = QtWidgets.QGridLayout(self.content_holder)
        self.area_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.content_holder.setLayout(self.area_layout)

        self._curr_row = 0
        self.search_curr_row = 0
        self.object = object
        self.setWindowTitle(f"Edit Object: {object.name}")
        print("Edit reset in", default_timer()-start, "s")
        self.setup_rows(object)

        if remember_scrollbar:
            self.scheduled_scrollbar_pos = pos
        else:
            self.scheduled_scrollbar_pos = None

    # Have to update the scrollbar position on range change, otherwise it takes no effect
    def scroll_area_bar_update(self):
        scrollbar = self.scroll_area.verticalScrollBar()
        if scrollbar.maximum() > 0 and self.scheduled_scrollbar_pos is not None:
            scrollbar.setValue(self.scheduled_scrollbar_pos)
            self.scheduled_scrollbar_pos = None

    def change_window_on_top_state(self, state):
        self.keep_window_on_top = state

        if state == QtCore.Qt.CheckState.Checked:
            print("turning ontop on", state)
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowType.WindowStaysOnTopHint)
        else:
            print("turning ontop off", state)
            self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowType.WindowStaysOnTopHint)

        self.show()

    def store_autoupdate_status(self):
        self.is_autoupdate = self.autoupdate_checkbox.isChecked()

    def setup_rows(self, object: BattalionObject):
        start = default_timer()
        self.fields = []
        editor = self.editor
        parent = None

        self._curr_row = 0


        self.search_bar = SearchBar(self.content_holder)
        self.add_row(name=QtWidgets.QLabel("Search"),
                     widget=self.search_bar)
        self.search_bar.find.connect(self.search)

        getter = make_getter(object, "customname")
        setter = lambda x: object.set_custom_name(x)

        checkbox_widget = QtWidgets.QCheckBox(self.content_holder)
        self.add_row(TooltippedLabel("Keep Window On Top",
                                     parent,
                                     "If set, this window will stay on top of other windows no matter which one is in focus."),
                    checkbox_widget)
        checkbox_widget.setChecked(self.keep_window_on_top==QtCore.Qt.CheckState.Checked)
        checkbox_widget.checkStateChanged.connect(self.change_window_on_top_state)

        self.autoupdate_checkbox = QtWidgets.QCheckBox(self.content_holder)
        self.add_row(TooltippedLabel(
            "Change Context to Selected Object",
            parent,
            "If set, selecting an object in the editor will change this edit window to show that object's data."

        ), self.autoupdate_checkbox)
        self.autoupdate_checkbox.setChecked(self.is_autoupdate)
        self.autoupdate_checkbox.checkStateChanged.connect(self.store_autoupdate_status)
        self.autoupdate_checkbox.checkStateChanged.connect(lambda x: self.main_window_changed.emit(self))

        # Add custom name field
        getter = make_getter(object, "customname")
        setter = lambda x: object.set_custom_name(x)

        customname_edit = CustomNameEdit(self.content_holder, getter, setter)
        self.fields.append(customname_edit)
        self.add_row(TooltippedLabel("Custom Name",
                                      parent,
                                      "A user-decided object name for reference in the editor."),
                                     customname_edit)
        customname_edit.update_value()
        customname_edit.editingFinished.connect(self.refresh_editor)

        # Add Lua name field
        def getter():
            if editor.lua_workbench.entityinit is not None:
                return editor.lua_workbench.entityinit.get_name(object.id)
            return ""

        def setter(x):
            if x is None:
                editor.lua_workbench.entityinit.delete_name(object.id)
            else:
                editor.lua_workbench.entityinit.set_name(object.id, x)
        item_cache = {}
        luaname_edit = LuaNameEdit(self.content_holder, getter, setter, editor.lua_workbench.entityinit.name_usages, object)
        luaname_edit.textinput.installEventFilter(self)

        self.fields.append(luaname_edit)
        self.add_row(TooltippedLabel("Lua Name", parent, "Lua variable which references this object."), luaname_edit)
        luaname_edit.update_value()
        for tag, name, type, elements in object.fields():
            field = FieldEdit(self.content_holder, editor, object, tag, name, type, elements, item_cache)
            field.editor_refresh.connect(self.object_was_updated)
            field.editor_refresh.connect(self.refresh_editor)
            field.edit_obj.connect(self.open_window)
            self.fields.append(field)

            name, firstitem = field.name, field.lines[0]
            self.add_row(name, firstitem)
            if len(field.lines) > 1:
                for i in range(1, len(field.lines)):
                    self.add_row(None, field.lines[i])
        print("Added widgets in", default_timer()-start, "s")

    def object_was_updated(self):
        self.object_edited.emit(self.object)

    def update_water_level(self, obj):
        if obj is not None and obj.type == "cRenderParams":
            self.editor.level_view.waterheight = obj.mWaterHeight

    def refresh_editor(self):
        self.editor.level_view.do_redraw(forcelightdirty=True)
        self.editor.leveldatatreeview.updatenames()
        self.editor.set_has_unsaved_changes(True)

    def add_row(self, name=None, widget=None):
        if name is not None:
            self.area_layout.addWidget(name, self._curr_row, 0)

        if widget is not None:
            self.area_layout.addWidget(widget, self._curr_row, 1)
        self._curr_row += 1

    def open_window(self, attr, i):
        val = getattr(self.object, attr)
        if isinstance(val, list):
            obj = val[i]
        else:
            obj = val

        self.makewindow(self.editor, obj)

    def activate(self):
        self.setWindowState(
            self.windowState() & ~QtCore.Qt.WindowState.WindowMinimized | QtCore.Qt.WindowState.WindowActive)
        self.activateWindow()
        self.show()