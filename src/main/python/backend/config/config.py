
from .data.params import DEFAULT_PARAMETER
from .paramter import Parameter

from collections import OrderedDict
import os 
import pickle
import matplotlib

matplotlib.rcParams['font.sans-serif'] = "Arial"
# Then, "ALWAYS use sans-serif fonts"
matplotlib.rcParams['font.family'] = "sans-serif"
sepConverter = {"tab":"\t","space":"\s+"}
class Config(object):
    ""
    def __init__(self, mainController):
        ""
        self.parameters = OrderedDict()
        self.mC = mainController
        self.loadDefaults()
        self.saveParameters()
        self.lastConfigGroup = None
    
    def clearSettings(self):
        "Clears parameters"
        self.parameters.clear()

    def loadDefaults(self):
        "Resets default setting"
        self.clearSettings()
        savedDefaultParam = self.loadParameters()
        if savedDefaultParam is None:
            print("falling back to default")
            savedDefaultParam = DEFAULT_PARAMETER
        
        self.updateParamsFromProfile(savedDefaultParam)
    
    def loadParameters(self,settingName = "current"):
        "Load Parameters from pickled file"
        configFolder = os.path.abspath(os.path.join(self.mC.mainPath,"conf"))
        if not os.path.exists(configFolder):
            os.mkdir(configFolder)
        fileName = '{}.ic'.format(settingName)
        filePath = os.path.join(configFolder,fileName)
            
        if os.path.exists(filePath):
            with open(filePath, 'rb') as paramFle:
                l = pickle.load(paramFle)
                if isinstance(l,list):
                    return l
    
    def loadProfile(self,profileName):
        ""
        savedParams = self.loadParameters(profileName)
        self.updateParamsFromProfile(savedParams)
        self.saveParameters()

    def getParam(self,paramName):
        ""
        if not paramName not in self.parameters:
            #check if it in default params (e.g. if an old profile config was used)
            self.updateParamsFromProfile(DEFAULT_PARAMETER,overwriteOnlyWhenNotPresent=True)

        if paramName in self.parameters:
            value = self.parameters[paramName].getAttr("value")
            if value in sepConverter: return sepConverter[value]
            return value
            
        
    def getParams(self, paramNames):
        ""
        if isinstance(paramNames,list):
            ps = []
            for paramName in paramNames:
                ps.append(self.getParam(paramName))
            return ps

    def getParamRange(self,paramName):
        ""
        if paramName in self.parameters:
            return self.parameters[paramName].getAttr("range")
        else:
            return []

    def getConfigPath(self):
        ""
        return os.path.abspath(os.path.join(self.mC.mainPath,"conf"))

    def getParentTypes(self):
        "Returns Parameters Parent Type"

        parentTypes = []
        for p in self.parameters.values():
            pType = p.getAttr("parentType")
            if pType is None:
                p.getAttr("name")
            if pType not in parentTypes and pType is not None:
                parentTypes.append(pType)
        return parentTypes

    def getParametersByType(self,parentType):
        "Get Parameters of a specific type"
        return [p for p in self.parameters.values() if p.getAttr("parentType") == parentType]
    
    def getSavedProfiles(self):
        ""
        savedProfiles = [x[:-3] for x in os.listdir(self.getConfigPath()) if x.endswith(".ic")]
        return savedProfiles

    def saveParameters(self, settingName = "current", overWriteCurrent = True):
        ""
        configFolder = self.getConfigPath()
        if not os.path.exists(configFolder):
            os.mkdir(configFolder)
        fileName = '{}.ic'.format(settingName)
        filePath = os.path.join(configFolder,fileName)
        
        with open(filePath, 'wb') as paramFle:
                pickle.dump([p.params for p in self.parameters.values()], paramFle)
        if overWriteCurrent and settingName != "current":
            self.overWriteCurrent()
            
    def overWriteCurrent(self):
        ""
        fileName = 'current.ic'
        filePath = os.path.join(self.getConfigPath(),fileName)
        with open(filePath, 'wb') as paramFle:
            pickle.dump([p.params for p in self.parameters.values()], paramFle)
    
    def paramExists(self,paramName):
        ""
        return paramName in self.parameters
            
    def saveProfile(self,settingName, overWriteCurrent=True):
        ""
        self.saveParameters(settingName,overWriteCurrent)

    def setParam(self,paramName,value):
        ""
        if paramName in self.parameters:
            self.parameters[paramName].setAttr("value",value)
            self.parameters[paramName].updateAttrInParent()

    def setParamRange(self,paramName,paramRange):
        ""
        if paramName in self.parameters and isinstance(paramRange,list):
            self.parameters[paramName].setAttr("range", paramRange, ignoreRange = True)
            self.parameters[paramName].updateAttrInParent()

    def toggleParam(self,paramName):
        ""
        try:
            if paramName in self.parameters:
                prevValue = self.parameters[paramName].getAttr("value")
                if isinstance(prevValue,bool):
                    self.parameters[paramName].setAttr("value",not prevValue)
        except Exception as e:
            print(e)

    def resetFactoryDefaults(self):
        ""
        savedDefaultParam = DEFAULT_PARAMETER
        self.updateParamsFromProfile(savedDefaultParam)
        self.saveParameters()


    def updateParamInParent(self, objectName, paramName, paramValue):
        ""

        if hasattr(self.mC,objectName):
            obj = getattr(self.mC,objectName)
            setattr(obj,paramName,paramValue)
            
    
    def updateAllParamsInParent(self):
        ""
        for param in self.parameters.values():
            param.updateAttrInParent()

    def updateParamsFromProfile(self,savedParams,overwriteOnlyWhenNotPresent=False):
        ""
        for n,dictAttr in enumerate(savedParams):
            param = Parameter(paramID=n, updateParamInParent = self.updateParamInParent)
            param.readFromDict(dictAttr)
            paramName = param.getAttr("name")
            if not overwriteOnlyWhenNotPresent:
                self.parameters[paramName] = param
            elif overwriteOnlyWhenNotPresent and paramName not in self.parameters:
                self.parameters[paramName] = param
            else:
                continue
            param.updateAttrInParent()
