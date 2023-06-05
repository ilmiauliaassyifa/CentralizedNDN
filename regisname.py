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
from ndn.app import NDNApp
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from ndn.encoding import Name, Component, InterestParam
import subprocess
import random, string
import json
import sys

logging.basicConfig(format='[{asctime}]{levelname}:{message}',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO,
                    style='{')


app = NDNApp()

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



async def main(prefix):
        for v in facelist:
                print()
                if not ':6363' in facelist[v][0] or not ':6363' in facelist[v][1]:
                        continue
                try:
                    timestamp = ndn.utils.timestamp()
                    name = Name.from_str('/regis') + [Component.from_timestamp(timestamp)]
                    appp = bytes(prefix, 'utf-8')
                    print(f'Sending Interest {Name.to_str(name)}, {InterestParam(must_be_fresh=True, lifetime=6000, forwarding_hint=[Name.from_str("/276")])}')
                    data_name, meta_info, content = await app.express_interest(
                        name, app_param=appp, must_be_fresh=True, can_be_prefix=False, lifetime=6000, forwarding_hint=[[1,facelist[v][2]],[2,"hello"]])

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

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print(f'Usage: {sys.argv[0]} <prefix>')
        exit(0)

    print(sys.argv[1])
    app.run_forever(after_start=main(sys.argv[1]))
