import functools
import numpy as np
import vtk
import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import qt


class MSPRM(ScriptedLoadableModule):

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "MSPRM"  
        self.parent.categories = ["Tools"]  
        self.parent.dependencies = [] 
        self.parent.contributors = ["Github"] 
        self.parent.helpText = """None"""
        self.parent.acknowledgementText = """None"""



class MSPRMWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):


    def __init__(self, parent=None) -> None:

        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  
        self.logic = None
        self._parameterNode = None
        self._parameterNodeGuiTag = None
        self.changeView=0

    def setup(self) -> None:

        ScriptedLoadableModuleWidget.setup(self)

        uiWidget = slicer.util.loadUI(self.resourcePath('UI/MSPRM.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        uiWidget.setMRMLScene(slicer.mrmlScene)
        
        self.ui.moveSelector.setMRMLScene(slicer.mrmlScene)
        self.ui.fixSelector.setMRMLScene(slicer.mrmlScene)
    

        self.ui.HardTransform.connect('clicked(bool)', self.onHardTransform)
        self.ui.tranComButton.connect('clicked(bool)', self.tranMatrix)
        
        self.ui.bigViewButton.connect('clicked()', self.bigView)
        self.ui.putfixPlane.connect('clicked(bool)', self.putfix)
        self.ui.putmovePlane.connect('clicked(bool)', self.putmove)
        
        self.ui.mprButton.connect('clicked(bool)', self.MPR)

        self.ui.opaciylSlider.connect("valueChanged(double)",self.sliderValueChanged)
        
        self.ui.fixcheckBox.stateChanged.connect(self.onfixcheckBoxChanged)
        self.ui.movecheckBox.stateChanged.connect(self.onmovecheckBoxChanged)
 

    def bigView(self):
        if self.ui.bigViewButton.text=="伸缩视图":
            with open (self.resourcePath('layout.ly'),"r") as f:
                content = f.read()
                customLayout =content
                customLayoutId=501
                layoutManager = slicer.app.layoutManager()
                layoutManager.layoutLogic().GetLayoutNode().AddLayoutDescription(customLayoutId, customLayout)
                layoutManager.setLayout(customLayoutId)
                self.ui.bigViewButton.text="正常视图"

        else:
            slicer.app.layoutManager().setLayout(0)
            self.ui.bigViewButton.text="伸缩视图"

    
    def OnChangeView(self):
        red=slicer.app.layoutManager().sliceWidget('Red').sliceOrientation
        green=slicer.app.layoutManager().sliceWidget('Green').sliceOrientation
        yellow=slicer.app.layoutManager().sliceWidget('Yellow').sliceOrientation
        

        
    def MPR(self):#MPR 开启关闭
        
        appLogic = slicer.app.applicationLogic()
        state=appLogic.GetIntersectingSlicesEnabled(slicer.vtkMRMLApplicationLogic.IntersectingSlicesVisibility)
        if state:
            appLogic.SetIntersectingSlicesEnabled(slicer.vtkMRMLApplicationLogic.IntersectingSlicesVisibility,0)
            appLogic.SetIntersectingSlicesEnabled(slicer.vtkMRMLApplicationLogic.IntersectingSlicesInteractive,0)
            
        else:
            appLogic.SetIntersectingSlicesEnabled(slicer.vtkMRMLApplicationLogic.IntersectingSlicesVisibility,1)
            appLogic.SetIntersectingSlicesEnabled(slicer.vtkMRMLApplicationLogic.IntersectingSlicesInteractive,1)
            appLogic.SetIntersectingSlicesLineThicknessMode(2)
            

    def onfixcheckBoxChanged(self, state):#选择静止数据显示
        if state == 2:  # 2 表示复选框被选中，0 表示未选中
            node=self.ui.fixSelector.currentNode()
            if node:
                slicer.util.setSliceViewerLayers(background=node)
                self.ui.movecheckBox.setChecked(0)
        slicer.util.resetSliceViews()              

            
    def onmovecheckBoxChanged(self, state):#选择移动数据显示
        if state == 2:  # 2 表示复选框被选中，0 表示未选中
            node=self.ui.moveSelector.currentNode()
            if node:
                slicer.util.setSliceViewerLayers(background=node)
                self.ui.fixcheckBox.setChecked(0) 
        slicer.util.resetSliceViews()       
     
    def sliderValueChanged(self):#透明滑块值改变后执行
        value=self.ui.opaciylSlider.value
        slicer.util.setSliceViewerLayers(foregroundOpacity=(value/100))
        

    def onRoTran(self): #平移旋转
        
        #获取移动数据的中心点，作为旋转中心
        data=self.ui.moveSelector.currentNode()
        bounds=[0,0,0,0,0,0]
        data.GetBounds(bounds)
        center=[(bounds[0]+bounds[1])/2,(bounds[2]+bounds[3])/2,(bounds[4]+bounds[5])/2]
        
        #添加新的变换节点 将数据放在变换下
        TransForm=slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLinearTransformNode')
        TransForm.SetName('modeTransForm')
        data.SetAndObserveTransformNodeID(TransForm.GetID())
        
        #添加点
        HandlePoint=slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode')
        HandlePoint.SetName('guidPoint')
        HandlePoint.AddControlPoint(center)
        
        HandlePoint.GetDisplayNode().HandlesInteractiveOn()
        HandlePoint.GetDisplayNode().RotationHandleVisibilityOn()
        HandlePoint.GetDisplayNode().TranslationHandleVisibilityOn()
        HandlePoint.GetDisplayNode().SetTextScale(0)
        
        #将点的变换矩阵赋值给数据
        
        def ApplyTransform(caller, event, TransFormID):
            #首先将数据至原点的变化矩阵求出来
            matrixOfModel=np.array([[1, 0, 0, -center[0]],
                                    [0, 1, 0, -center[1]],
                                    [0, 0, 1, -center[2]],
                                    [0, 0, 0, 1]])
            transNode=slicer.util.getNode(TransFormID)
            #获取点的变换矩阵
            transNodeMatrix=caller.GetInteractionHandleToWorldMatrix()
           
            transNodeMatrixArray=slicer.util.arrayFromVTKMatrix(transNodeMatrix)
            #将数据变换至原点，再赋予点的变换矩阵
            outMatrixArray=np.dot(transNodeMatrixArray,matrixOfModel)
            matrix_new=slicer.util.vtkMatrixFromArray(outMatrixArray)
            transNode.SetMatrixTransformToParent(matrix_new)

        #添加观察者，将点的变换矩阵赋值给模型
        observer_func = functools.partial(ApplyTransform, TransFormID=TransForm.GetID())
        HandlePoint.AddObserver(slicer.vtkMRMLMarkupsFiducialNode.PointModifiedEvent, observer_func)
       
    
    def onHardTransform(self):#固化
    
        try:
            dataNode=self.ui.moveSelector.currentNode()
            dataNode.HardenTransform()
        except:
            pass
        #删除中间不用的节点
        for i in ['modeTransForm','guidPoint','AToBTransForm']:
            try:
                node=slicer.util.getNode(i)
                slicer.mrmlScene.RemoveNode(node)
            except:
                pass
  

    def tranMatrix(self):#开始配准
        
        TransFormNode=slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLinearTransformNode')
        TransFormNode.SetName('AToBTransForm')
 
        #修正变换矩阵,使图像恢复解剖学位姿
        ModifieTrans=np.array([[0,0,-1,0],[-1,0,0,0],[0,1,0,0],[0,0,0,1]])

        #获取平面A到ras的变换矩阵，再赋予给变换节点
        matrix_new=slicer.util.vtkMatrixFromArray(np.dot(ModifieTrans,np.linalg.inv(self.moveTrans)))
        TransFormNode.SetMatrixTransformToParent(matrix_new)

        self.ui.moveSelector.currentNode().SetAndObserveTransformNodeID(TransFormNode.GetID())
        self.ui.moveSelector.currentNode().HardenTransform()
        
        
        #获取平面B到ras的变换矩阵，再赋予给变换节点
        matrix_new=slicer.util.vtkMatrixFromArray(np.dot(ModifieTrans,np.linalg.inv(self.fixTrans)))
        TransFormNode.SetMatrixTransformToParent(matrix_new)

        #再将平面B的数据移动过去
        self.ui.fixSelector.currentNode().SetAndObserveTransformNodeID(TransFormNode.GetID())
        self.ui.fixSelector.currentNode().HardenTransform()
        

        #设置前景和背景数据
        Node1=self.ui.fixSelector.currentNode()
        Node2=self.ui.moveSelector.currentNode()
        slicer.util.setSliceViewerLayers(foreground=Node1,background=Node2)
        slicer.util.setSliceViewerLayers(foregroundOpacity=0.5)

   
        #关闭十字框
        appLogic = slicer.app.applicationLogic()
        appLogic.SetIntersectingSlicesEnabled(slicer.vtkMRMLApplicationLogic.IntersectingSlicesVisibility,0)
        appLogic.SetIntersectingSlicesEnabled(slicer.vtkMRMLApplicationLogic.IntersectingSlicesInteractive,0)
        
        slicer.util.resetSliceViews() 
  
        #调用旋转平移函数
        
        slicer.app.layoutManager().sliceWidget("Red").setSliceOrientation("Axial")
        slicer.app.layoutManager().sliceWidget("Green").setSliceOrientation("Coronal")
        slicer.app.layoutManager().sliceWidget("Yellow").setSliceOrientation("Sagittal")
   
        self.onRoTran()

    def getPlaneIntersectionPoint(self): 
    
        axialNode = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeRed')
        ortho1Node = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeYellow')
        ortho2Node = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeGreen')

        axialSliceToRas = axialNode.GetSliceToRAS()
        n1 = [axialSliceToRas.GetElement(0,2),axialSliceToRas.GetElement(1,2),axialSliceToRas.GetElement(2,2)]
        x1 = [axialSliceToRas.GetElement(0,3),axialSliceToRas.GetElement(1,3),axialSliceToRas.GetElement(2,3)]

        ortho1SliceToRas = ortho1Node.GetSliceToRAS()
        n2 = [ortho1SliceToRas.GetElement(0,2),ortho1SliceToRas.GetElement(1,2),ortho1SliceToRas.GetElement(2,2)]
        x2 = [ortho1SliceToRas.GetElement(0,3),ortho1SliceToRas.GetElement(1,3),ortho1SliceToRas.GetElement(2,3)]

        ortho2SliceToRas = ortho2Node.GetSliceToRAS()
        n3 = [ortho2SliceToRas.GetElement(0,2),ortho2SliceToRas.GetElement(1,2),ortho2SliceToRas.GetElement(2,2)]
        x3 = [ortho2SliceToRas.GetElement(0,3),ortho2SliceToRas.GetElement(1,3),ortho2SliceToRas.GetElement(2,3)]

        x = [0,0,0]    

        n2_xp_n3 = [0,0,0]
        x1_dp_n1 = vtk.vtkMath.Dot(x1,n1)
        vtk.vtkMath.Cross(n2,n3,n2_xp_n3)
        vtk.vtkMath.MultiplyScalar(n2_xp_n3, x1_dp_n1)
        vtk.vtkMath.Add(x,n2_xp_n3,x)

        n3_xp_n1 = [0,0,0]
        x2_dp_n2 = vtk.vtkMath.Dot(x2,n2)
        vtk.vtkMath.Cross(n3,n1,n3_xp_n1)
        vtk.vtkMath.MultiplyScalar(n3_xp_n1, x2_dp_n2)
        vtk.vtkMath.Add(x,n3_xp_n1,x)

        n1_xp_n2 = [0,0,0]
        x3_dp_n3 = vtk.vtkMath.Dot(x3,n3)
        vtk.vtkMath.Cross(n1,n2,n1_xp_n2)
        vtk.vtkMath.MultiplyScalar(n1_xp_n2, x3_dp_n3)
        vtk.vtkMath.Add(x,n1_xp_n2,x)

        normalMatrix = vtk.vtkMatrix3x3()
        normalMatrix.SetElement(0,0,n1[0])
        normalMatrix.SetElement(1,0,n1[1])
        normalMatrix.SetElement(2,0,n1[2])
        normalMatrix.SetElement(0,1,n2[0])
        normalMatrix.SetElement(1,1,n2[1])
        normalMatrix.SetElement(2,1,n2[2])
        normalMatrix.SetElement(0,2,n3[0])
        normalMatrix.SetElement(1,2,n3[1])
        normalMatrix.SetElement(2,2,n3[2])
        normalMatrixDeterminant = normalMatrix.Determinant()
        
        if abs(normalMatrixDeterminant)>0.01:
          vtk.vtkMath.MultiplyScalar(x, 1/normalMatrixDeterminant)
        else:
          x = x1
        
        return x

    def PutPlane(self,name): #获取MPR交点为平面位置，黄色平面法向量为平面向量

        yellow=slicer.util.getNode('vtkMRMLSliceNodeYellow')
        yellowTrans=slicer.util.arrayFromVTKMatrix(yellow.GetSliceToRAS())
        slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode').SetName(name)
        plane=slicer.util.getNode(name) 
        plane.SetNormal(yellowTrans[0:3,2])
        intersectionPoint=self.getPlaneIntersectionPoint()
        plane.SetNthControlPointPosition(0,intersectionPoint)
        
    def putfix(self):#放置静止数据平面
        yellow=slicer.util.getNode('vtkMRMLSliceNodeYellow')
        self.fixTrans=slicer.util.arrayFromVTKMatrix(yellow.GetSliceToRAS())
        qt.QMessageBox.information(slicer.util.mainWindow(),'提示','放置成功 可重新放置')
    
    def putmove(self):#放置移动数据平面
 
       yellow=slicer.util.getNode('vtkMRMLSliceNodeYellow')
       self.moveTrans=slicer.util.arrayFromVTKMatrix(yellow.GetSliceToRAS())
       qt.QMessageBox.information(slicer.util.mainWindow(),'提示','放置成功 可重新放置')
    
   