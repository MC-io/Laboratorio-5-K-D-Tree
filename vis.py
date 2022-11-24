"""
Implementacion de un K-D Tree Clasico, con visualizacion incluida para dimension K = 2
"""

import pyglet
from pyglet import shapes
import math
import csv
import time

all_neighbors = []

class Node:
    # Constructor
    def __init__(self, vec):
        self.vec = vec
        self.left = None
        self.right = None
        self.top_right = [600,600]      # al conocer los limites del cuadrante del nodo
        self.bot_left = [0,0]           # se pueden dibujar de manera mas facil con pyglet
    def __str__(self):
        r = ''
        for i in self.vec:
            r += str(i) + ' '
        return r

class KDTree:
    def __init__(self, k, xbound = 0, ybound = 0):
        self.k = k
        self.root = None
        self.xbound = xbound    # limites en x y y
        self.ybound = ybound
    
    def insert(self, vec):
        if self.root == None:
            self.root = Node(vec);
            return

        new_node = Node(vec)
        tmp = self.root
        tmp2 = tmp
        height = 0
        while tmp is not None:
            tmp2 = tmp
            if tmp.vec[height % self.k] == new_node.vec[height % self.k]:
                return 
            elif tmp.vec[height % self.k] > new_node.vec[height % self.k]:
                tmp = tmp.left
            else:
                tmp = tmp.right
            height += 1

        height -= 1         # La altura al finalizar el ciclo no es la que queremos para insertar el nuevo nodo

        if tmp2.vec[height % self.k] > new_node.vec[height % self.k]:
            tmp2.left = new_node
            if self.k == 2:
                if height % self.k == 0:
                    new_node.top_right = [tmp2.vec[0], tmp2.top_right[1]]
                    new_node.bot_left = tmp2.bot_left
                else:
                    new_node.top_right = [tmp2.top_right[0], tmp2.vec[1]]
                    new_node.bot_left = tmp2.bot_left
        else:
            tmp2.right = new_node
            if self.k == 2:
                if height % self.k == 0:
                    new_node.top_right = tmp2.top_right
                    new_node.bot_left = [tmp2.vec[0], tmp2.bot_left[1]]
                else:
                    new_node.top_right = tmp2.top_right
                    new_node.bot_left = [tmp2.bot_left[0], tmp2.vec[1]]

    def search(self, vec):
        if self.root == None:
            return None

        tmp = self.root
        height = 0
        while tmp is not None:
            if tmp.vec[height % self.k] > vec[height % self.k]:
                tmp = tmp.left
            elif tmp.vec[height % self.k] < vec[height % self.k]:
                tmp = tmp.right
            else:
                return tmp
            height += 1

        return None
    
    def distance(self, a, b):
        res = 0
        for i in range(self.k):
            res += (a[i] - b[i]) ** 2
        res = math.sqrt(res)
        return res
    
    def closest(self, target, a, b, neighbor_list):
        if a is None:
            return b
        if b is None:
            return a
        if a in neighbor_list:
            return b
        if b in neighbor_list:
            return a
        res_a = self.distance(target, a.vec)
        res_b = self.distance(target, b.vec)
        if res_a < res_b:
            return a
        return b
        
    
    def nearest_neigh(self, node, target, depth, neighbor_list):
        if node is None:
            return None
        next_branch = None
        other_branch = None
        if target[depth % self.k] < node.vec[depth % self.k]:
            next_branch = node.left
            other_branch = node.right
        else:
            next_branch = node.right
            other_branch = node.left
        tmp = self.nearest_neigh(next_branch, target, depth + 1, neighbor_list)
        best = self.closest(target, tmp, node, neighbor_list)

        radius = self.distance(target, best.vec) 
        dist = target[depth % self.k] - node.vec[depth % self.k]

        if radius >= dist:
            tmp = self.nearest_neigh(other_branch, target, depth + 1, neighbor_list)
            best = self.closest(target, tmp, best, neighbor_list)

        return best




        

    def nearest_neighbor(self, target):
        return self.nearest_neigh(self.root, target, 0)
    

    def k_nearest_neighbors(self, target, k):
        neighbor_list = []
        for i in range(k):
            neighbor_list.append(self.nearest_neigh(self.root, target, 0, neighbor_list))
        return neighbor_list

    def prin_in_order(self, node):
        if node is None:
            return
        self.prin_in_order(node.left)
        for i in range(self.k):
            print(node.vec[i], end=' ')
        print()
        self.prin_in_order(node.right)

    def print_in_order(self):
        self.prin_in_order(self.root)

    def rec_dot(self,node,t,f):
        if node is None:
            return
        f.write('{} [label="('.format(t));
        for i in range(self.k):
            f.write('{},'.format(node.vec[i]))
        f.write(')"]\n');

        if node.left is not None:
            f.write('{}  -> {} \n'.format(t,t*2)) 
            self.rec_dot(node.left,t*2,f)
        if node.right is not None:
            f.write('{}  -> {} \n'.format(t,t*2+1))
            self.rec_dot(node.right,t*2 + 1,f)
        
    
    def create_dot(self):
        f = open("kdtree.dot","w")
        f.write("digraph {\n")
        t = 1
        f.write('{} [label="('.format(t));
        for i in range(self.k):
            f.write('{},'.format(self.root.vec[i]))
        f.write(')"]\n');

        if self.root.left is not None:
            f.write('{}  -> {} \n'.format(t,t*2)) 
            self.rec_dot(self.root.left,t*2,f)
        if self.root.right is not None:
            f.write('{}  -> {} \n'.format(t,t*2+1))
            self.rec_dot(self.root.right,t*2 + 1,f)
        f.write('}')
        f.close()
        #os.system('cmd /k "Graphviz/bin/dot -Tpng kdtree.dot -o kdtree.png"')


    

def draw_board(tree,shape_list, batch=None):
    shape_list.append(shapes.Circle(300,300,10,color=(234,123,12),batch=batch))
    pre_order(tree.root,0,shape_list,batch)

def pre_order(node, depth, shape_list, batch):
    if node is None:
        return
    point = shapes.Circle(node.vec[0],node.vec[1],10, batch=batch)
    if node in all_neighbors:
        point.color = (123,59,200)
    
    if depth % 2 == 0:
        line = shapes.Line(node.vec[0],node.bot_left[1],node.vec[0],node.top_right[1],color=(255, 0, 0),batch=batch)
        shape_list.append(line)
    else:
        line = shapes.Line(node.bot_left[0],node.vec[1],node.top_right[0],node.vec[1],color=(0, 255, 0),batch=batch)
        shape_list.append(line)
    shape_list.append(point)

    pre_order(node.left, depth + 1, shape_list, batch=batch)
    pre_order(node.right, depth + 1, shape_list, batch=batch)



if __name__ == "__main__":
    kd = 2;
    xbound = 600
    ybound = 600
    arbol = KDTree(kd,xbound,ybound)
    arbol.insert([350,420])
    arbol.insert([520,100])
    arbol.insert([320,237])
    arbol.insert([200,134])
    arbol.insert([50,450])
    arbol.insert([270,350])
    arbol.insert([380,126])
    arbol.insert([586,67])
    arbol.insert([235,123])
    arbol.insert([240,329])
    arbol.insert([560,500])
    arbol.insert([230,39])
    arbol.insert([256,207])
    arbol.insert([301,405])
    arbol.insert([207,440])
    arbol.insert([290,180])
    arbol.insert([15,342])

    all_neighbors = arbol.k_nearest_neighbors([300,300],6)

    # Visualization for 2-D Tree
    window = pyglet.window.Window(600, 600, "Visualizacion 2-D Tree")
    batch = pyglet.graphics.Batch()

    shape_list = []
    draw_board(arbol,shape_list, batch=batch)


    @window.event
    def on_draw():
        window.clear()
        batch.draw()

    pyglet.app.run()
    
    