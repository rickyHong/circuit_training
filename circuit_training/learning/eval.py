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
"""Eval job using a variable container to fetch the weights of the policy."""

import functools
import os

from absl import app
from absl import flags
from circuit_training.environment import environment
from circuit_training.learning import eval_lib


from tf_agents.policies import greedy_policy  # pylint: disable=unused-import
from tf_agents.system import system_multiprocessing as multiprocessing

FLAGS = flags.FLAGS


def main(_):
  root_dir = os.path.join(FLAGS.root_dir, str(FLAGS.global_seed))

  create_env_fn = functools.partial(
      environment.create_circuit_environment,
      netlist_file=FLAGS.netlist_file,
      init_placement=FLAGS.init_placement,
      is_eval=True,
      save_best_cost=True,
      output_plc_file=os.path.join(root_dir, 'rl_opt_placement.plc'),
      global_seed=FLAGS.global_seed,
  )

  eval_lib.evaluate(
      root_dir=root_dir,
      variable_container_server_address=FLAGS.variable_container_server_address,
      create_env_fn=create_env_fn,
  )


if __name__ == '__main__':
  flags.mark_flags_as_required(
      ['root_dir', 'variable_container_server_address'])
  multiprocessing.handle_main(functools.partial(app.run, main))
