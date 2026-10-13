# Copyright 2026 lanzhu
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

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """同时启动系统状态发布节点和 Qt 展示节点."""
    return LaunchDescription([
        Node(
            package='status_publisher',
            executable='sys_status_pub',
            name='sys_status_pub',
            output='screen',
        ),
        Node(
            package='status_publisher',
            executable='status_gui',
            name='status_gui',
            output='screen',
        ),
    ])
