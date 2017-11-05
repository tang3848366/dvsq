# =============================================================================
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
# ==============================================================================

"""Routine for decoding the NUS-WIDE binary file format."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from six.moves import xrange  # pylint: disable=redefined-builtin
import tensorflow as tf

from scipy.misc import imread, imresize
import cv2
import numpy as np
import h5py

# Process images of this size. Note that this differs from the original nus-wide
# image size of 224 x 224. If one alters this number, then the entire model
# architecture will change and any model would need to be retrained.

# Global constants describing the NUS-WIDE data set.

class dataset(object):
    def __init__(self, modal, path, train=True):
        self.lines = open(path, 'r').readlines()
        self.n_samples = len(self.lines)
        self.train = train
        assert modal == 'img'
        if modal == 'img':
            self.modal = 'img'
            self._img  = [0] * self.n_samples
            self._label = [0] * self.n_samples
            self._load = [0] * self.n_samples
            self._load_num = 0            
            self._status = 0
            self.data = self.img_data
            self.all_data = self.img_all_data

    def img_data(self, index):
        if self._status:
            return (self._img[index, :], self._label[index, :])
        else:
            ret_img = []
            ret_label = []
            for i in index:
                try:
                    if self.train:
                        if not self._load[i]:
                            self._img[i] = cv2.resize(cv2.imread(self.lines[i].strip().split()[0]), (256, 256))
                            self._label[i] = [int(j) for j in self.lines[i].strip().split()[1:]]
                            self._load[i] = 1
                            self._load_num += 1
                        ret_img.append(self._img[i])
                        ret_label.append(self._label[i])
                    else:
                        self._label[i] = [int(j) for j in self.lines[i].strip().split()[1:]]
                        ret_img.append(cv2.resize(cv2.imread(self.lines[i].strip().split()[0]), (256, 256)))
                        ret_label.append([int(j) for j in self.lines[i].strip().split()[1:]])
                except:
                    print('cannot open', self.lines[i])
                #else:
                    #print(self.lines[i])
                
            if self._load_num == self.n_samples:
                self._status = 1
                self._img = np.asarray(self._img)
                self._label = np.asarray(self._label)
            return (np.asarray(ret_img), np.asarray(ret_label))

    def img_all_data(self):
        if self._status:
            return (self._img, self._label)

    def get_labels(self):
        for i in xrange(self.n_samples):
            if self._label[i] == 0:
                self._label[i] = [int(j) for j in self.lines[i].strip().split()[1:]]
        return np.asarray(self._label)

def import_train(config):
    '''
    return (img_tr, txt_tr)
    '''
    return (dataset('img', config["img_tr"],
                    train=True))

def import_validation(config):
    '''
    return (img_te, txt_te, img_db, txt_db)
    '''
    return (dataset('img', config["img_te"],
                    train=False),
            dataset('img', config["img_db"],
                    train=False))
