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

logging.basicConfig(format='[{asctime}]{levelname}:{message}',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO,
                    style='{')


app = NDNApp()

myprefix = {}

async def main():
    print('RUN')

@app.route('/hello')
def on_interest(name: FormalName, param: InterestParam, _app_param: Optional[BinaryStr]):
    print(f'>> I: {Name.to_str(name)}, {param}')
    content = "controller".encode()
    app.put_data(name, content=content, freshness_period=5)
    print(f'<< D: {Name.to_str(name)}')
    print(MetaInfo(freshness_period=10000))
    print(f'Content: (size: {len(content)})')
    print('')

@app.route('/regis')
def on_interest(name: FormalName, param: InterestParam, ap):
    global myprefix
    nr = str(bytes(ap))
    print(f'>> I: {Name.to_str(name)}, {param}, {bytes(ap)}')
    content = "OK-Controller".encode()
    app.put_data(name, content=content, freshness_period=5)
    print(f'<< D: {Name.to_str(name)}')
    print(MetaInfo(freshness_period=10000))
    print(f'Content: (size: {len(content)})\n')
    nr = nr.split(",")
    if nr[0].split("'")[1] in myprefix:
        myprefix[nr[0].split("'")[1]]=myprefix[nr[0].split("'")[1]].append(nr[1].split("'")[0])
    else:
        myprefix[nr[0].split("'")[1]]=[nr[1].split("'")[0]]
    print("\n\n\nMy Prefix\n",myprefix)
    with open('myprefix.txt', 'w') as json_file:
        json.dump(myprefix, json_file)


if __name__ == '__main__':
    app.run_forever(after_start=main())
