import numpy as np

"""
// The MIT License (MIT)
//
// Copyright (c) 2012-2013 Mikola Lysenko
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
// 
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.

/**
 * SurfaceNets in JavaScript
 *
 * Written by Mikola Lysenko (C) 2012
 *
 * MIT License
 *
 * Based on: S.F. Gibson, "Constrained Elastic Surface Nets". (1998) MERL Tech Report.
 */

 /**
 * SurfaceNets in python
 *
 * Written by Markus Joppich (C) 2020
 *
 * MIT License
 *
 * Based on: SurfaceNets in JavaScript, S.F. Gibson, "Constrained Elastic Surface Nets". (1998) MERL Tech Report.
 */
"""

class SurfaceNets:

    def __init__(self):

        self.cube_edges = None
        self.edge_table = None

        k = 0
        cube_edges = {}
        for  i in range(0,8):
            for j in [1,2,4]:
                p = i^j

                if i <= p:
                    cube_edges[k] = i
                    k += 1
                    cube_edges[k] = p
                    k += 1

        self.cube_edges = [0] * k

        for x in cube_edges:
            self.cube_edges[x] = cube_edges[x]

        self.cube_edges = tuple(self.cube_edges)


        self.edge_table = [0] * 256
        for i in range(0, 256):
            em = 0

            for j in range(0, 24, 2):
                a = not (i & (1 << cube_edges[j]))
                b = not (i & (1 << cube_edges[j+1]))

                em |= (1 << (j >> 1)) if a != b else 0

            self.edge_table[i] = em
            
        self.edge_table = tuple(self.edge_table)


    def surface_net(self, data, level=1):

        R = [0] * 3
        x = [0] * 3
        grid = [0] * 8

        vertices = []
        faces = []

        buf_no = 1
        n = 0
        m = 0

        dims = data.shape
        
        print(dims)

        R[0] = 1
        R[1] =  dims[0] + 1
        R[2] = (dims[0] + 1) * (dims[1] + 1)

        buffer = [0] * 4096

        if R[2] * 2 >= len(buffer):
            buffer = [0] * (R[2]*2)

        vdata = np.array(data, copy=True)
        vdata = np.reshape(vdata, dims[0]*dims[1]*dims[2])
                
        vdata = [0] * dims[0]*dims[1]*dims[2]
        vdata = np.array(vdata)
        
        for i in range(0, dims[0]):
            for j in range(0, dims[1]):
                for k in range(0, dims[2]):       
                    
                    vidx = i + dims[0] * j + dims[0]*dims[1] * k
                    
                    if vidx >= len(vdata):
                        print(i,j,k, dims)
                    
                    vdata[vidx]= data[i,j,k]

        visIdx = set()
        
        x[2] = 0
        while x[2] < dims[2]-1: # outerloop
            m = 1 + (dims[0]+1) * (1 + (buf_no * (dims[1]+1)))

            x[1] = 0
            while x[1] < dims[1]-1: # middleloop

                x[0] = 0
                while x[0] < dims[0]-1: # innerloop
                    
                    mask = 0
                    g = 0
                    idx = n
                    
                    if idx in visIdx:
                        print("double index")
                    
                    visIdx.add(idx)

                    for k in range(0,2):
                        for j in range(0,2):
                            for i in range(0,2):

                                p = vdata[idx] - level

                                grid[g] = p
                                mask |= (1 << g) if (p<0) else 0

                                # loop stuff

                                #i += 1
                                g += 1
                                idx += 1

                            #j += 1
                            idx += dims[0]-2

                        idx += dims[0] * (dims[1]-2)

                    
                    #print(n, vdata[n], mask, x, dims)
                    if mask == 0 or mask == 0xff:
                        
                        #if mask == 0xff:
                        #    inObj[x[0], x[1], x[2]] = 1
                        #elif mask == 0:
                        #    outObj[x[0], x[1], x[2]] = 0
                            
                        
                        # innerloop
                        x[0] += 1
                        n += 1
                        m += 1
                        continue

                    
                    edge_mask = self.edge_table[mask]

                    v = [0] * 3
                    e_count = 0

                    for i in range(0, 12):


                        if (edge_mask & (1<<i)) == 0:
                            continue

                            
                        e_count += 1

                        e0 = self.cube_edges[ i << 1]
                        e1 = self.cube_edges[(i << 1) + 1]

                        g0 = grid[e0]
                        g1 = grid[e1]

                        t = g0-g1

                        if abs(t) > 1e-2:
                            t = g0 / t
                        else:
                            continue

                        k=1

                        for j in range(0, 3):

                            a = e0 & k
                            b = e1 & k

                            if (a!= b):
                                v[j] += 1.0-t if a else t
                            else:
                                v[j] += 1.0 if a else 0.0

                            k = k << 1



                    s = 1.0/e_count

                    for i in range(0, 3):
                        v[i] = x[i] + s * v[i]


                    #print(m, len(buffer), len(vertices))
                    buffer[m] = len(vertices)
                    vertices.append(v)

                    for i in range(0,3):


                        if not (edge_mask & (1 << i)):
                            continue

                            
                        iu = (i+1)%3
                        iv = (i+2)%3

                        if x[iu] == 0 or x[iv] == 0:
                            continue

                            
                        du = R[iu]
                        dv = R[iv]

                        #print(m, iu, iv, du, dv, m-du-dv, m-du, m-dv)
                        
                        if (mask & 1):
                        
                            faces.append((
                                buffer[m], buffer[m-du-dv], buffer[m-du]
                            ))

                            faces.append((
                                buffer[m], buffer[m-dv], buffer[m-du-dv]
                            ))
                            
                        else:
                            faces.append((
                                buffer[m], buffer[m-du-dv], buffer[m-dv]
                            ))

                            faces.append((
                                buffer[m], buffer[m-du], buffer[m-du-dv]
                            ))
                            
                            
                        
                    ## inner loop update
                    x[0] += 1
                    n += 1
                    m += 1    
                    
                ## middle loop update
                x[1] += 1
                n += 1
                m += 2
                                        

            
            if x[2] % 10 == 0:
                print(x)
            
            ## outer loop update
            x[2] += 1
            n += dims[0]
            buf_no ^= 1
            R[2] = -R[2]
                    
        print("visIdx", len(visIdx), dims[0]*dims[1]*dims[2])
                
        return vertices, faces

sn = SurfaceNets()