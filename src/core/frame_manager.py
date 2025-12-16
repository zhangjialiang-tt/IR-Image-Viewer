"""帧管理器

管理多帧图像的播放和导航功能。
"""

from typing import Optional, Callable
from PyQt5.QtCore import QTimer, QObject, pyqtSignal


class FrameManager(QObject):
    """帧管理器
    
    负责管理多帧图像的索引、导航和播放控制。
    使用QTimer实现动画播放功能。
    
    Attributes:
        total_frames: 总帧数
        current_frame: 当前帧索引（从0开始）
        
    Signals:
        frame_changed: 当帧索引改变时发出，参数为新的帧索引
    """
    
    # 定义信号
    frame_changed = pyqtSignal(int)
    
    def __init__(self, total_frames: int):
        """初始化帧管理器
        
        Args:
            total_frames: 总帧数，必须大于0
            
        Raises:
            ValueError: 如果total_frames <= 0
        """
        super().__init__()
        
        if total_frames <= 0:
            raise ValueError("总帧数必须大于0")
        
        self._total_frames = total_frames
        self._current_frame = 0
        self._is_playing = False
        
        # 创建定时器用于播放动画
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer_tick)
    
    def set_current_frame(self, frame_index: int) -> None:
        """设置当前帧索引
        
        Args:
            frame_index: 帧索引（从0开始）
            
        Raises:
            ValueError: 如果frame_index超出有效范围
        """
        if frame_index < 0 or frame_index >= self._total_frames:
            raise ValueError(
                f"帧索引 {frame_index} 超出范围 [0, {self._total_frames - 1}]"
            )
        
        if self._current_frame != frame_index:
            self._current_frame = frame_index
            self.frame_changed.emit(self._current_frame)
    
    def get_current_frame(self) -> int:
        """获取当前帧索引
        
        Returns:
            int: 当前帧索引（从0开始）
        """
        return self._current_frame
    
    def next_frame(self) -> int:
        """切换到下一帧
        
        如果当前是最后一帧，则循环到第一帧。
        
        Returns:
            int: 新的帧索引
        """
        new_frame = (self._current_frame + 1) % self._total_frames
        self.set_current_frame(new_frame)
        return new_frame
    
    def previous_frame(self) -> int:
        """切换到上一帧
        
        如果当前是第一帧，则循环到最后一帧。
        
        Returns:
            int: 新的帧索引
        """
        new_frame = (self._current_frame - 1) % self._total_frames
        self.set_current_frame(new_frame)
        return new_frame
    
    def play(self, fps: int = 10) -> None:
        """开始播放动画
        
        按指定帧率自动切换帧。
        
        Args:
            fps: 帧率（每秒帧数），必须大于0，默认为10
            
        Raises:
            ValueError: 如果fps <= 0
        """
        if fps <= 0:
            raise ValueError("帧率必须大于0")
        
        if not self._is_playing:
            self._is_playing = True
            # 计算定时器间隔（毫秒）
            interval_ms = int(1000 / fps)
            self._timer.start(interval_ms)
    
    def pause(self) -> None:
        """暂停播放动画
        
        停止自动切换帧。
        """
        if self._is_playing:
            self._is_playing = False
            self._timer.stop()
    
    def is_playing(self) -> bool:
        """检查是否正在播放
        
        Returns:
            bool: 如果正在播放返回True，否则返回False
        """
        return self._is_playing
    
    def get_total_frames(self) -> int:
        """获取总帧数
        
        Returns:
            int: 总帧数
        """
        return self._total_frames
    
    def set_total_frames(self, total_frames: int) -> None:
        """设置总帧数
        
        如果当前帧索引超出新的范围，会自动调整到最后一帧。
        如果正在播放，会先暂停。
        
        Args:
            total_frames: 新的总帧数，必须大于0
            
        Raises:
            ValueError: 如果total_frames <= 0
        """
        if total_frames <= 0:
            raise ValueError("总帧数必须大于0")
        
        # 如果正在播放，先暂停
        if self._is_playing:
            self.pause()
        
        self._total_frames = total_frames
        
        # 如果当前帧超出范围，调整到最后一帧
        if self._current_frame >= self._total_frames:
            self.set_current_frame(self._total_frames - 1)
    
    def _on_timer_tick(self) -> None:
        """定时器触发时的回调函数
        
        自动切换到下一帧。
        """
        self.next_frame()
