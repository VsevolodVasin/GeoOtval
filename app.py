# --coding:utf-8--
import time
import PyQt5
import sys
import os
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox
from PyQt5.QtGui import QIcon
from mydesign import Ui_GEO_OTVAL
from PyQt5.QtCore import *
import folium
import numpy as np
import cv2
from PIL import Image
import matplotlib.pyplot as plt
import geopandas as gpd
import flexpolyline
from shapely.geometry import Point, LineString
import geojson
import requests

apikey = 'yourhereapi-restkey'
#https://www.here.com/

class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_GEO_OTVAL()
        self.ui.setupUi(self)

        self.setWindowTitle('GEO_OTVAL')

        self.setWindowIcon(QIcon('knif.ico'))

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.ui.otr.addItem("Отобразить в исходном состоянии")
        self.ui.otr.addItem("Повернуть на 90° вправо")
        self.ui.otr.addItem("Повернуть на 180° вправо")
        self.ui.otr.addItem("Повернуть на 270° вправо")

        self.ui.makeMap.clicked.connect(self.start)

        self.ui.exit.clicked.connect(self.quit)


    def select(self):
        filepath, type = QtWidgets.QFileDialog.getOpenFileName(self, 'Выберите файлы',".","PNG Файлы(*.png)")
        print(filepath)
        return(filepath)

    def start(self):


        if(self.ui.lineEdit.text() ==''):
            dlina = 6 
        else:
            dlina = int(self.ui.lineEdit.text())
        print(dlina)

        otr = str(self.ui.otr.currentText())
        print(otr)

        if otr == "Отобразить в исходном состоянии":
            povorot = 0

        if otr == "Повернуть на 90° вправо":
            povorot = 1

        if otr == "Повернуть на 180° вправо":
            povorot = 2

        if otr == "Повернуть на 270° вправо":
            povorot = 3




        x_original_point = int(self.ui.edit_x.text())


        y_original_point = int(self.ui.edit_y.text())



        xcords = []
        ycords = []

        xmas = []
        ymas = []

        distdegr = 0
        # Чтение изображения

        font = cv2.FONT_HERSHEY_COMPLEX

        imgpath = self.select()

        img2 = cv2.imread(imgpath, cv2.IMREAD_COLOR)


          
        # Чтение того же изображения в другом
        # переменная и преобразование в серую шкалу.

        img = cv2.imread(imgpath, cv2.IMREAD_GRAYSCALE)


        if(povorot == 1):
            img2 = cv2.rotate(img2, cv2.cv2.ROTATE_90_CLOCKWISE) 
            img = cv2.rotate(img, cv2.cv2.ROTATE_90_CLOCKWISE) 
        elif(povorot == 2):
            img2 = cv2.rotate(img2, cv2.cv2.ROTATE_90_CLOCKWISE) 
            img = cv2.rotate(img, cv2.cv2.ROTATE_90_CLOCKWISE) 
            img2 = cv2.rotate(img2, cv2.cv2.ROTATE_90_CLOCKWISE) 
            img = cv2.rotate(img, cv2.cv2.ROTATE_90_CLOCKWISE) 
        elif(povorot==3):
            img2 = cv2.rotate(img2, cv2.cv2.ROTATE_90_CLOCKWISE) 
            img = cv2.rotate(img, cv2.cv2.ROTATE_90_CLOCKWISE) 
            img2 = cv2.rotate(img2, cv2.cv2.ROTATE_90_CLOCKWISE) 
            img = cv2.rotate(img, cv2.cv2.ROTATE_90_CLOCKWISE) 
            img2 = cv2.rotate(img2, cv2.cv2.ROTATE_90_CLOCKWISE) 
            img = cv2.rotate(img, cv2.cv2.ROTATE_90_CLOCKWISE) 
         

        _, threshold = cv2.threshold(img, 190, 255, cv2.THRESH_BINARY)



        contours, _= cv2.findContours(threshold, cv2.RETR_TREE,

                                       cv2.CHAIN_APPROX_SIMPLE)


        lenghtx = 0
        lenghttempx = 0
        lenghttempy = 0
        lenghty = 0


        for cnt in contours :



            approx = cv2.approxPolyDP(cnt, 0.002 * cv2.arcLength(cnt, True), True)
            cv2.drawContours(img2, [approx], -1, (0, 0, 255), 3) 
            n = approx.ravel() 
            corners = np.int0(approx.ravel())
            i = 0



            for j in n :
                if(i % 2 == 0):
                    x = n[i]
                    y = n[i + 1]
                    string = str(x) + " " + str(y) 
                    meters = 100
                    mx = x * meters + x_original_point
                    my = -y * meters + y_original_point
                    xcords.append(mx)
                    ycords.append(my)
                    lenghtx = lenghtx + (x - lenghttempx) 
                    lenghty = lenghty + (y - lenghttempy) 
                    lenghttempx = x
                    lenghttempy = y
                i = i + 1

        lenght = lenghtx**2+lenghty**2
        lenght = lenght**0.5
        cof = lenght/dlina
        print(dlina)
        print(lenght)

        if(dlina < lenght):
            xcords.clear()
            ycords.clear()
            print('Размер слишком большой, в ', dlina/lenght,' раз')
            i = 0
            lenghtx = 0
            lenghttempx = 0
            lenghttempy = 0
            lenghty = 0
            j=0
            for cnt in contours :
                approx = cv2.approxPolyDP(cnt, 0.002 * cv2.arcLength(cnt, True), True)

                cv2.drawContours(img2, [approx], -1, (0, 0, 255), 3) 

                n = approx.ravel() 
                corners = np.int0(approx.ravel())
                i = 0

                for j in n :

                    if(i % 2 == 0):
                        x = n[i]
                        y = n[i + 1]
                        string = str(x) + " " + str(y) 
                        meters = 100/cof
                        mx = x * meters + x_original_point
                        my = -y * meters + y_original_point
                        xcords.append(mx)
                        ycords.append(my)
                        lenghtx = lenghtx + (x - lenghttempx) 
                        lenghty = lenghty + (y - lenghttempy) 
                        lenghttempx = x
                        lenghttempy = y

                    i = i + 1

        x = self.ui.lineEdit_2.text()
        if x == "":
            pass
        else:
            xcords.append(int(x))

        y = self.ui.lineEdit_3.text()
        if y == "":
            pass
        else:
            ycords.append(int(y))


        x = self.ui.lineEdit_4.text()
        if x == "":
            pass
        else:
            xcords.append(int(x))

        y = self.ui.lineEdit_5.text()
        if y == "":
            pass
        else:
            ycords.append(int(y))

        #a

        def distance(P1, P2):
            """
            This function computes the distance between 2 points defined by
             P1 = (x1,y1) and P2 = (x2,y2) 
            """
            
            return ((P1[0] - P2[0])**2 + (P1[1] - P2[1])**2) ** 0.5




        def optimized_path(coords, start=None):
            """
            This function finds the nearest point to a point
            coords should be a list in this format coords = [ [x1, y1], [x2, y2] , ...] 

            """
            if start is None:
                start = coords[0]
            pass_by = coords
            path = [start]
            pass_by.remove(start)
            while pass_by:
                nearest = min(pass_by, key=lambda x: distance(path[-1], x))
                path.append(nearest)
                pass_by.remove(nearest)
            return path

        del ycords[::2]
        del xcords[::2]
        del xcords[::2]
        del ycords[::2]
        mxy = list(zip(xcords,ycords))
        squeezed = mxy
        mxy = optimized_path(squeezed)


        picture_df = gpd.GeoDataFrame(
            {'id': range(0, len(mxy))}, 
            crs="EPSG:3857", 
            geometry=[Point(resu) for resu in mxy]
        )

        picture_df['geometry'] = picture_df['geometry'].to_crs(epsg=4326)
        picture_df.to_file("marks.geojson", driver='GeoJSON', encoding="utf-8")
        SERVICE = f'https://router.hereapi.com/v8/routes?apiKey={apikey}&transportMode=pedestrian&return=polyline'
        print(SERVICE)
        file = open('marks.geojson')
        data = geojson.load(file).copy()
        file.close()
        coords_list = [feature['geometry']['coordinates'] for feature in data['features']]
        start_point = coords_list[0]
        destination_point = coords_list[len(coords_list) -1]
        coords_list.remove(start_point)
        coords_list.remove(destination_point)
        origin = f'&origin={start_point[1]},{start_point[0]}'
        destination = f'&destination={destination_point[1]},{destination_point[0]}&'
        waypoints = '&'.join([f'via={coords[1]},{coords[0]}' for coords in coords_list])
        routes = requests.get(SERVICE + origin + destination + waypoints).json()
        def decode (section):
            line = flexpolyline.decode(section['polyline'])
            line = [(coord[1], coord[0])  for coord in line]
            return LineString(line)
        geometry = [ decode(section) for section in routes['routes'][0]['sections']]
        route_df = gpd.GeoDataFrame(geometry=geometry)
        route_df.to_file("route.geojson", driver='GeoJSON', encoding="utf-8")
        m = folium.Map(location=[55.744507, 37.594444], zoom_start=10)
        folium.GeoJson('route.geojson', name="geojson").add_to(m)
        m.save('map.html')
        os.system('map.html')

    def quit(self):
        sys.exit()


app = QtWidgets.QApplication([])
application = mywindow()
application.show()
sys.exit(app.exec_())
