#!/usr/bin/env python3
# Copyright 2022 The Pigweed Authors
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
"""Tests for bloaty configuration tooling."""

import unittest

from pw_bloat import bloaty_config


class BloatyConfigTest(unittest.TestCase):
    """Tests that the bloaty config tool produces the expected config."""

    def test_map_segments_to_memory_regions(self) -> None:
        """Ensures the mapping works correctly based on a real example."""
        segments = {
            3: (134279784, 135266816),
            5: (536888912, 537003600),
            6: (537003600, 537067520),
            1: (134218240, 134279264),
            4: (536871432, 536888912),
            2: (536870912, 536871432),
            0: (134217728, 134218240),
        }
        memory_regions = {
            'FLASH': {0: (134218240, 135266816)},
            'RAM': {0: (536870912, 537067520)},
            'VECTOR_TABLE': {0: (134217728, 134218240)},
        }
        expected = {
            3: 'FLASH',
            5: 'RAM',
            6: 'RAM',
            1: 'FLASH',
            4: 'RAM',
            2: 'RAM',
            0: 'VECTOR_TABLE',
        }
        actual = bloaty_config.map_segments_to_memory_regions(
            segments=segments, memory_regions=memory_regions
        )
        self.assertEqual(expected, actual)

    def test_generate_memoryregions_data_source(self) -> None:
        """Ensures the formatted generation works correctly."""
        segments_to_memory_regions = {
            0: 'RAM',
            1: 'RAM',
            13: 'FLASH',
        }
        config = bloaty_config.generate_memoryregions_data_source(
            segments_to_memory_regions
        )
        expected = '\n'.join(
            (
                r'custom_data_source: {',
                r'  name: "memoryregions"',
                r'  base_data_source: "segments"',
                r'  rewrite: {',
                r'    pattern:"^LOAD #0 \\[.*\\]$"',
                r'    replacement:"RAM"',
                r'  }',
                r'  rewrite: {',
                r'    pattern:"^LOAD #1 \\[.*\\]$"',
                r'    replacement:"RAM"',
                r'  }',
                r'  rewrite: {',
                r'    pattern:"^LOAD #13 \\[.*\\]$"',
                r'    replacement:"FLASH"',
                r'  }',
                r'  rewrite: {',
                r'    pattern:".*"',
                r'    replacement:"Not resident in memory"',
                r'  }',
                r'}',
                r'',
            )
        )
        self.assertEqual(expected, config)

    def test_generate_utilization_data_source(self) -> None:
        config = bloaty_config.generate_utilization_data_source()
        expected = '\n'.join(
            (
                'custom_data_source: {',
                '  name:"utilization"',
                '  base_data_source:"sections"',
                '  rewrite: {',
                '    pattern:"unused_space"',
                '    replacement:"Free space"',
                '  }',
                '  rewrite: {',
                '    pattern:".*"',
                '    replacement:"Used space"',
                '  }',
                '}',
                '',
            )
        )
        self.assertEqual(expected, config)


if __name__ == '__main__':
    unittest.main()
