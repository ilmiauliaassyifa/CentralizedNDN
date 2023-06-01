# -----------------------------------------------------------------------------
# Copyright (C) 2019-2020 The python-ndn authors
#
# This file is part of python-ndn.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------------------
import ndn.utils
from typing import Optional
from ndn.app import NDNApp
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from ndn.encoding import Name, InterestParam, BinaryStr, FormalName, MetaInfo, Component
import logging
import subprocess
import random, string
import heapq
import json
import time


def djikstra(graph, start, end):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    previous = {node: None for node in graph}
    queue =[(0, start)]
    while queue:
        current_distance, current_node = heapq.heappop(queue)
        if current_node == end:
            break
        if current_distance > distances[current_node]:
            continue
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))

    if end not in previous:
        return None
    path = []
    current_node = end
    while current_node != start:
        path.insert(0, current_node)
        current_node = previous[current_node]
    path.insert(0, start)
    return path



logging.basicConfig(format='[{asctime}]{levelname}:{message}',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO,
                    style='{')


app = NDNApp()

myprefix = {}

nfdc_face_cmd = ['nfdc','face']

process = subprocess.Popen(nfdc_face_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
process.wait()

output, error = process.communicate()

if error:
   print(f'Error:{error.decode()}')
else:
   print(f'Output:{output.decode()}')
out = str(output.decode())
faces = out.split("faceid=")
facelist = {}
fn = {}

for face in faces[1:] :
    key = face.split(" ")[0]
    remote = face.split("remote=")[1].split(" ")[0]
    local = face.split("local=")[1].split(" ")[0]
    api = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    facelist[key] = [remote, local, api]
    print(key, facelist[key])

# add routes
for v in facelist:
    print(v)
    if not ':6363' in facelist[v][0] or not ':6363' in facelist[v][1]:
        continue
    nfdc_route_cmd = ['nfdc','route','add','/'+facelist[v][2],'nexthop',v]

    process = subprocess.Popen(nfdc_route_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()

graph = {}


async def main():
    while True:
        for v in facelist:
                print()
                if not ':6363' in facelist[v][0] or not ':6363' in facelist[v][1]:
                        continue
                try:
                    timestamp = ndn.utils.timestamp()
                    name = Name.from_str('/hello') + [Component.from_timestamp(timestamp)]
                    print(f'Sending Interest {Name.to_str(name)}, {InterestParam(must_be_fresh=True, lifetime=6000, forwarding_hint=[Name.from_str("/276")])}')
                    data_name, meta_info, content = await app.express_interest(
                        name, must_be_fresh=True, can_be_prefix=False, lifetime=6000, forwarding_hint=[[1,facelist[v][2]],[2,"hello"]])

                    print(f'Received Data Name: {Name.to_str(data_name)}')
                    print(meta_info)
                    print(bytes(content) if content else None)
                    facelist[v].append(bytes(content).decode())
                    fn[bytes(content).decode()] = facelist[v][2]
                    print(v, facelist[v])
                    

                except InterestNack as e:
                    print(f'Nacked with reason={e.reason}')
                except InterestTimeout:
                   print(f'Timeout')
                except InterestCanceled:
                   print(f'Canceled')
                except ValidationFailure:
                   print(f'Data failed to validate')

#        with open('face.txt', 'w') as json_file:
#                json.dump(facelist, json_file)


        for v in facelist:
                print()
                if not ':6363' in facelist[v][0] or not ':6363' in facelist[v][1]:
                        continue
                try:
                    timestamp = ndn.utils.timestamp()
                    name = Name.from_str('/facelist') + [Component.from_timestamp(timestamp)]
                    print(f'Sending Interest {Name.to_str(name)}, {InterestParam(must_be_fresh=True, lifetime=6000, forwarding_hint=[Name.from_str("/276")])}')
                    data_name, meta_info, content = await app.express_interest(
                        name, must_be_fresh=True, can_be_prefix=False, lifetime=6000, forwarding_hint=[[1,facelist[v][2]],[2,"facelist"]])

                    print(f'Received Data Name: {Name.to_str(data_name)}')
                    print(meta_info)
                    print(bytes(content) if content else None)
                    #facelist[v].append(bytes(content).decode())
                    print(v, facelist[v])
                    str_data = str(bytes(content)).split("\'")[1].split("\'")[0]
                    print(str_data)
                    faces = json.loads(str_data)
                    temp = {}

                    for k in faces:
                         if len(faces[k]) == 4:
                              if faces[k][3] == "controller":
                                   continue
                              temp[faces[k][3]] = 1
                    graph[facelist[v][3]] = temp

                except InterestNack as e:
                    print(f'Nacked with reason={e.reason}')
                except InterestTimeout:
                   print(f'Timeout')
                except InterestCanceled:
                   print(f'Canceled')
                except ValidationFailure:
                   print(f'Data failed to validate')

        print(graph)

#        for router in start:
        for start in graph:
            for end in myprefix:
                 if start == end:
                    continue
                 shortest_path = djikstra(graph, start, end)
                 print(shortest_path)
                 #App Param
                 cost = len(shortest_path)-1 #costnya 
                 nh = shortest_path[1] #nexthop
                 listprefix = myprefix[end] #prefix
                 #forwarding hint
                 fh = fn[start]
                 for prefix in listprefix:
                     try: 
                         timestamp = ndn.utils.timestamp()
                         name = Name.from_str('/updateroute') + [Component.from_timestamp(timestamp)]
                         appp = bytes(f'{nh},{prefix},{cost}', 'utf-8')
                         print(f'\nSending Interest {Name.to_str(name)}, {InterestParam(must_be_fresh=True, lifetime=6000, forwarding_hint=[Name.from_str("/276")])}\n')
                         data_name, meta_info, content = await app.express_interest(
                             name, app_param=appp, must_be_fresh=True, can_be_prefix=False, lifetime=6000, forwarding_hint=[[1,fh],[2,"updateroute"]])

                         print(f'Received Data Name: {Name.to_str(data_name)}')
                         print(meta_info)
                         print(bytes(content) if content else None)
                         facelist[v].append(bytes(content).decode())
                         print(v, facelist[v])

                     except InterestNack as e:
                         print(f'Nacked with reason={e.reason}')
                     except InterestTimeout:
                         print(f'Timeout')
                     except InterestCanceled:
                         print(f'Canceled')
                     except ValidationFailure:
                         print(f'Data failed to validate')



        time.sleep(5)

#faces = out.split("faceid=")
#facelist = {}

#for face in faces[1:] :
#    key = face.split(" ")[0]
#    remote = face.split("remote=")[1].split(" ")[0]
#    local = face.split("local=")[1].split(" ")[0]
#    api = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
#    facelist[key] = [remote, local, api]
#    print(key, facelist[key]

@app.route('/hello')
def on_interest(name: FormalName, param: InterestParam, _app_param: Optional[BinaryStr]):
    print(f'>> I: {Name.to_str(name)}, {param}')
    content = "controller".encode()
    app.put_data(name, content=content, freshness_period=10000)
    print(f'<< D: {Name.to_str(name)}')
    print(MetaInfo(freshness_period=10000))
    print(f'Content: (size: {len(content)})')
    print('')

@app.route('/facelist')
def on_interest(name: FormalName, param: InterestParam, _app_param: Optional[BinaryStr]):
    print(f'>> I: {Name.to_str(name)}, {param}')
    f = open('face.txt', 'r') 
    content = f.read().encode()
    app.put_data(name, content=content, freshness_period=10000)
    print(f'<< D: {Name.to_str(name)}')
    print(MetaInfo(freshness_period=10000))
    print(f'Content: (size: {len(content)})')

@app.route('/regis')
def on_interest(name: FormalName, param: InterestParam, ap):
    global myprefix
    nr = str(bytes(ap))
    print(f'>> I: {Name.to_str(name)}, {param}, {bytes(ap)}')
    content = "OK-Controller".encode()
    app.put_data(name, content=content, freshness_period=10000)
    print(f'<< D: {Name.to_str(name)}')
    print(MetaInfo(freshness_period=10000))
    print(f'Content: (size: {len(content)})\n')
    nr = nr.split(",")
    if nr[0].split("'")[1] in myprefix:
        myprefix[nr[0].split("'")[1]]=myprefix[nr[0].split("'")[1]].append(nr[1].split("'")[0])
    else:
        myprefix[nr[0].split("'")[1]]=[nr[1].split("'")[0]]
    print("\n\n\nMy Prefix\n",myprefix)


if __name__ == '__main__':
    app.run_forever(after_start=main())
