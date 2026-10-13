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

"""订阅系统状态并在 Qt 窗口中实时展示."""

import datetime
import sys

import rclpy
from rclpy.node import Node
from status_interfaces.msg import SystemStatus

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QMainWindow,
    QWidget,
)


class StatusGuiNode(Node):
    """订阅 ``system_status`` 话题的 ROS2 节点."""

    def __init__(self):
        super().__init__('status_gui')
        self.on_status = None
        self.subscription = self.create_subscription(
            SystemStatus,
            'system_status',
            self._status_callback,
            10,
        )

    def _status_callback(self, msg):
        """收到消息后转交给窗口回调."""
        if self.on_status is not None:
            self.on_status(msg)


def format_bytes(value):
    """将字节数转换为人类可读的字符串."""
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if abs(value) < 1024.0:
            return '%.2f %s' % (value, unit)
        value /= 1024.0
    return '%.2f PB' % value


class StatusWindow(QMainWindow):
    """展示系统状态信息的主窗口."""

    FIELDS = (
        ('时间', 'time'),
        ('主机名', 'hostname'),
        ('CPU 使用率', 'cpu_percent'),
        ('内存使用率', 'memory_percent'),
        ('内存总大小', 'memory_total'),
        ('剩余内存', 'memory_available'),
        ('网络发送数据量', 'net_sent'),
        ('网络接收数据量', 'net_recv'),
    )

    def __init__(self, node):
        super().__init__()
        self.node = node
        self.node.on_status = self.update_display

        self._value_labels = {}
        self._build_ui()

        # 用定时器驱动 rclpy 事件循环，避免阻塞 Qt 事件循环
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._spin_once)
        self._timer.start(100)

    def _build_ui(self):
        self.setWindowTitle('系统状态监控')
        self.resize(440, 380)

        central = QWidget(self)
        self.setCentralWidget(central)

        layout = QGridLayout(central)
        layout.setVerticalSpacing(12)
        layout.setColumnStretch(1, 1)

        for row, (name, key) in enumerate(self.FIELDS):
            name_label = QLabel(name + '：')
            value_label = QLabel('--')
            value_label.setStyleSheet('font-weight: bold;')
            self._value_labels[key] = value_label
            layout.addWidget(name_label, row, 0)
            layout.addWidget(value_label, row, 1)

    def _spin_once(self):
        if not self.node.context.ok():
            self._timer.stop()
            self.close()
            return
        rclpy.spin_once(self.node, timeout_sec=0.0)

    def update_display(self, msg):
        """根据收到的消息刷新窗口内容."""
        self._value_labels['time'].setText(self._format_time(msg.stamp))
        self._value_labels['hostname'].setText(msg.hostname)
        self._value_labels['cpu_percent'].setText('%.1f %%' % msg.cpu_percent)
        self._value_labels['memory_percent'].setText(
            '%.1f %%' % msg.memory_percent)
        self._value_labels['memory_total'].setText(
            format_bytes(msg.memory_total))
        self._value_labels['memory_available'].setText(
            format_bytes(msg.memory_available))
        self._value_labels['net_sent'].setText(format_bytes(msg.net_sent))
        self._value_labels['net_recv'].setText(format_bytes(msg.net_recv))

    @staticmethod
    def _format_time(stamp):
        seconds = stamp.sec + stamp.nanosec * 1e-9
        return datetime.datetime.fromtimestamp(seconds).strftime(
            '%Y-%m-%d %H:%M:%S')


def main(args=None):
    """节点入口函数."""
    rclpy.init(args=args)
    node = StatusGuiNode()

    app = QApplication(sys.argv)
    window = StatusWindow(node)
    window.show()

    exit_code = app.exec_()

    if rclpy.ok():
        node.destroy_node()
        rclpy.shutdown()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
