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

async def main():
   print("RUN")

@app.route('/hello')
def on_interest(name: FormalName, param: InterestParam, _app_param: Optional[BinaryStr]):
    print(f'>> I: {Name.to_str(name)}, {param}')
    content = "R1".encode()
    app.put_data(name, content=content, freshness_period=5)
    print(f'<< D: {Name.to_str(name)}')
    print(MetaInfo(freshness_period=10000))
    print(f'Content: (size: {len(content)})')
    print('')

@app.route('/facelist')
def on_interest(name: FormalName, param: InterestParam, _app_param: Optional[BinaryStr]):
    print(f'>> I: {Name.to_str(name)}, {param}')
    f = open('face.txt', 'r') 
    content = f.read().encode()
    app.put_data(name, content=content, freshness_period=5)
    print(f'<< D: {Name.to_str(name)}')
    print(MetaInfo(freshness_period=10000))
    print(f'Content: (size: {len(content)})')
    print('')

@app.route('/updateroute')
def on_interest(name: FormalName, param: InterestParam, ap):
    
    nr = str(bytes(ap))
    print(f'>> I: {Name.to_str(name)}, {param}, {bytes(ap)}') 
    content ="Ok".encode()
    app.put_data(name, content=content, freshness_period=5)
    print(f'<< D: {Name.to_str(name)}')
    print(MetaInfo(freshness_period=10000))
    print(f'Content: (size: {len(content)})')
    nr = nr.split(",")
    #myprefix[nr[0].split("'")[1]]= nr[1].split("'")[0]
    with open('nf.txt') as json_file:
        nf = json.load(json_file)
    nfdc_routeupdate_cmd = ['nfdc','route','add',nr[1].split("'")[0],'nexthop',nf[nr[0].split("'")[1]],'cost',nr[2].split("'")[0]]

    process = subprocess.Popen(nfdc_routeupdate_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()

if __name__ == '__main__':
    app.run_forever(after_start=main())
