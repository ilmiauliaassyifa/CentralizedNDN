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
from typing import Optional
from ndn.app import NDNApp
from ndn.encoding import Name, InterestParam, BinaryStr, FormalName, MetaInfo
import logging
import subprocess


logging.basicConfig(format='[{asctime}]{levelname}:{message}',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO,
                    style='{')


app = NDNApp()

myprefix = {}

nfdc_face_cmd = ['nfdc','face']

#process = subprocess.Popen(nfdc_face_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#process.wait()

#output, error = process.communicate()

#if error:
#   print(f'Error:{error.decode()}')
#else:
#   print(f'Output:{output.decode()}')


@app.route('/hello')
def on_interest(name: FormalName, param: InterestParam, app_param):
    print(f'>> I: {Name.to_str(name)}, {param}, {bytes(app_param)}')
    content = "R1".encode()
    app.put_data(name, content=content, freshness_period=10000)
    print(f'<< D: {Name.to_str(name)}')
    print(MetaInfo(freshness_period=10000))
    print(f'Content: (size: {len(content)})')
    print('')

@app.route('/facelist')
def on_interest(name: FormalName, param: InterestParam, app_param):
    print(f'>> I: {Name.to_str(name)}, {param}, {app_param}')
    f = open('face.txt', 'r') 
    content = f.read().encode()
    app.put_data(name, content=content, freshness_period=10000)
    print(f'<< D: {Name.to_str(name)}')
    print(MetaInfo(freshness_period=10000))
    print(f'Content: (size: {len(content)})')
    print('')

@app.route('/regis')
def on_interest(name: FormalName, param: InterestParam, ap):
    global myprefix
    nr = str(bytes(ap))
    print(f'>> I: {Name.to_str(name)}, {param}, {bytes(ap)}') 
    content ="Ok".encode()
    app.put_data(name, content=content, freshness_period=10000)
    print(f'<< D: {Name.to_str(name)}')
    print(MetaInfo(freshness_period=10000))
    print(f'Content: (size: {len(content)})')
    nr = nr.split(",")
    myprefix[nr[0].split("'")[1]]= nr[1].split("'")[0]
    print(myprefix)




#app_param = {}
#myprefix = {}

#def main():
#    global app_param, myprefix
#    for nr in app_param.items():
#        nr = nr[0].split(",")
#        myprefix[nr[0]]= nr[1]
#        print(myprefi)

#app_param_str =str(app_param)
#nr = app_param_str.split(",")
#myprefix[nr[0]]= nr[1]
#print(myprefix)



if __name__ == '__main__':
    app.run_forever()
