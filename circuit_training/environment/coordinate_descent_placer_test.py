# coding=utf-8
# Copyright 2021 The Circuit Training Team Authors.
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
"""Tests for coordinate_descent_placer."""

import os
import random

from absl import flags
from absl import logging
from absl.testing import parameterized
from circuit_training.environment import coordinate_descent_placer
from circuit_training.environment import environment
from circuit_training.environment import placement_util
from circuit_training.utils import test_utils
import numpy as np

FLAGS = flags.FLAGS


class CoordinateDescentPlacerTest(parameterized.TestCase, test_utils.TestCase):

  def setUp(self):
    super(CoordinateDescentPlacerTest, self).setUp()
    random.seed(666)
    np.random.seed(666)
    # Common CD parameters.
    FLAGS.cd_epochs = 3
    FLAGS.cd_k_distance_bound = 3
    FLAGS.cd_stdcell_place_every_n_macros = 10

  def _cost_fn(self):
    return environment.cost_fn(
        self.plc,
        wirelength_weight=1.0,
        density_weight=0.1,
        congestion_weight=0.1)

  def _create_plc(self, block_name, cd_optimize_only_orientation):
    test_netlist_dir = ('circuit_training/'
                        'environment/test_data')
    test_netlist_dir = os.path.join(FLAGS.test_srcdir, test_netlist_dir,
                                    block_name)
    netlist_file = os.path.join(test_netlist_dir, 'netlist.pb.txt')
    init_placement = os.path.join(test_netlist_dir, 'initial.plc')
    FLAGS.cd_optimize_only_orientation = cd_optimize_only_orientation
    FLAGS.cd_use_stdcell_placer = False

    self.plc = placement_util.create_placement_cost(netlist_file,
                                                    init_placement)
    grid_cols, grid_rows = self.plc.get_grid_num_columns_rows()
    self.grid_size = grid_rows * grid_cols

  def _randomize_placement(self):
    self.plc.unplace_all_nodes()
    macros = self.plc.get_macro_indices()
    num_macros = len(macros)
    # Sample random locations for all nodes.
    locations = random.sample(list(range(self.grid_size)), num_macros)
    self.assertLen(locations, len(macros))
    for i, m in enumerate(macros):
      self.plc.place_node(m, locations[i])

  # TODO(wenjiej): Add a FD test for blocks that have stdcells.
  @parameterized.parameters(
      ('macro_tiles_10x10', True),
      ('macro_tiles_10x10', False),
  )
  def test_cd(self, block_name, cd_optimize_only_orientation):
    self._create_plc(block_name, cd_optimize_only_orientation)
    self.cd_placer = coordinate_descent_placer.CoordinateDescentPlacer(
        self.plc, self._cost_fn)

    self._randomize_placement()
    before_cd_cost = self._cost_fn()[0]
    self.cd_placer.place()
    after_cd_cost = self._cost_fn()[0]
    logging.info('before_cd_cost: %f', before_cd_cost)
    logging.info('after_cd_cost: %f', after_cd_cost)
    self.assertLess(after_cd_cost, before_cd_cost)


if __name__ == '__main__':
  test_utils.main()
