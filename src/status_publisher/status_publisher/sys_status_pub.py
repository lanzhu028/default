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

"""系统状态采集与发布节点."""

import platform

import psutil
import rclpy
from rclpy.node import Node
from status_interfaces.msg import SystemStatus


class SysStatusPub(Node):
    """采集系统实时状态并发布到 ``system_status`` 话题."""

    def __init__(self):
        super().__init__('sys_status_pub')
        self.publisher_ = self.create_publisher(
            SystemStatus, 'system_status', 10)
        timer_period = 1.0  # 每秒采集并发布一次
        self.timer = self.create_timer(timer_period, self.timer_callback)
        # 首次调用返回 0.0，这里先调用一次以初始化统计基线
        psutil.cpu_percent(interval=None)

    def timer_callback(self):
        """定时采集系统状态并发布消息."""
        msg = SystemStatus()
        msg.stamp = self.get_clock().now().to_msg()
        msg.hostname = platform.node()

        msg.cpu_percent = psutil.cpu_percent(interval=None)

        memory = psutil.virtual_memory()
        msg.memory_percent = memory.percent
        msg.memory_total = float(memory.total)
        msg.memory_available = float(memory.available)

        net = psutil.net_io_counters()
        msg.net_sent = float(net.bytes_sent)
        msg.net_recv = float(net.bytes_recv)

        self.publisher_.publish(msg)
        self.get_logger().info(
            'host=%s cpu=%.1f%% mem=%.1f%%'
            % (msg.hostname, msg.cpu_percent, msg.memory_percent))


def main(args=None):
    """节点入口函数."""
    rclpy.init(args=args)
    node = SysStatusPub()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
