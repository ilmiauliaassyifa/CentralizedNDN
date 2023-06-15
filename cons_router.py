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
import logging
import ndn.utils
from typing import Optional
from ndn.app import NDNApp
from ndn.encoding import Name, Component, InterestParam, BinaryStr, FormalName, MetaInfo
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
import subprocess
import logging
import random, string
import json
import time


logging.basicConfig(format='[{asctime}]{levelname}:{message}',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO,
                    style='{')


app = NDNApp()

myprefix = {}
nf = {}


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
async def main():
        while True:  
                for v in facelist:
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
                            if len(facelist[v]) == 3 :
                                facelist[v].append(bytes(content).decode())
                            else :
                                facelist[v][3] = bytes(content).decode()
                            nf[bytes(content).decode()] = v
                            print(v, facelist[v])

                        except InterestNack as e:
                            print(f'Nacked with reason={e.reason}')
                            if len(facelist[v]) == 3 :
                                facelist[v].append("")
                            else :
                                facelist[v][3] = ""
                        except InterestTimeout:
                            print(f'Timeout')
                            if len(facelist[v]) == 3 :
                                facelist[v].append("")
                            else :
                                facelist[v][3] = ""
                        except InterestCanceled:
                            print(f'Canceled')
                            if len(facelist[v]) == 3 :
                                facelist[v].append("")
                            else :
                                facelist[v][3] = ""
                        except ValidationFailure:
                            print(f'Data failed to validate')
                            if len(facelist[v]) == 3 :
                                facelist[v].append("")
                            else :
                                facelist[v][3] = ""
                with open('face.txt', 'w') as json_file:
                    json.dump(facelist, json_file)
                time.sleep(60)

if __name__ == '__main__':
    app.run_forever(after_start=main())
