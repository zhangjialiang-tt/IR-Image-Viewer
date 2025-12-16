# Implementation Plan

- [x] 1. 设置项目结构和核心数据模型





  - 创建项目目录结构（src/ui, src/core, src/utils, tests/）
  - 实现 ImageConfig 数据类，包含验证方法
  - 实现 FileInfo 和 FrameData 数据类
  - 创建 requirements.txt 文件
  - _Requirements: 10.1, 10.2, 10.4_

- [ ]* 1.1 编写数据模型的单元测试
  - 测试 ImageConfig 验证逻辑
  - 测试 get_bytes_per_pixel 方法
  - 测试边界情况（负数、零值）
  - _Requirements: 2.1, 2.2_

- [x] 2. 实现文件加载器（FileLoader）





  - 实现基本文件读取功能
  - 实现大文件内存映射逻辑（>100MB）
  - 实现 get_file_info 方法返回文件元数据
  - 添加文件访问错误处理
  - _Requirements: 1.2, 1.3, 1.4_

- [ ]* 2.1 编写文件加载器的单元测试
  - 测试小文件加载
  - 测试大文件内存映射
  - 测试文件不存在错误
  - 测试空文件处理
  - _Requirements: 1.2, 1.3, 9.1, 9.5_

- [ ]* 2.2 编写属性测试：文件读取完整性
  - **Property 1: 文件读取完整性**
  - **Validates: Requirements 1.2**
  - 生成随机二进制数据，验证读取字节数等于文件大小
  - _Requirements: 1.2_


- [ ]* 2.3 编写属性测试：错误处理一致性
  - **Property 2: 错误处理一致性**
  - **Validates: Requirements 1.4, 8.2**
  - 生成无效文件场景，验证错误消息显示且状态不变
  - _Requirements: 1.4, 8.2_

- [x] 3. 实现图像解析器（ImageParser）




  - 实现 parse_frame 方法，支持8位和16位数据
  - 实现字节序转换（大端/小端）
  - 实现行偏移功能
  - 实现 calculate_frame_size 和 calculate_total_frames 方法
  - 实现 validate_parameters 方法
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ]* 3.1 编写图像解析器的单元测试
  - 测试8位图像解析
  - 测试16位图像解析
  - 测试大端/小端字节序
  - 测试行偏移
  - 测试参数验证
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ]* 3.2 编写属性测试：分辨率解析正确性
  - **Property 4: 分辨率解析正确性**
  - **Validates: Requirements 2.1**
  - 生成随机分辨率配置，验证解析后的图像维度匹配
  - _Requirements: 2.1_

- [ ]* 3.3 编写属性测试：位深度解析正确性
  - **Property 5: 位深度解析正确性**
  - **Validates: Requirements 2.2**
  - 生成随机位深度设置，验证每像素字节数正确
  - _Requirements: 2.2_

- [ ]* 3.4 编写属性测试：字节序转换正确性
  - **Property 6: 字节序转换正确性**
  - **Validates: Requirements 2.3**
  - 生成随机16位数据，验证大端↔小端转换的round-trip一致性
  - _Requirements: 2.3_

- [ ]* 3.5 编写属性测试：行偏移解析正确性
  - **Property 7: 行偏移解析正确性**
  - **Validates: Requirements 2.4**
  - 生成随机偏移量，验证从正确位置开始解析
  - _Requirements: 2.4_


- [ ]* 3.6 编写属性测试：帧数计算正确性
  - **Property 11: 帧数计算正确性**
  - **Validates: Requirements 4.1**
  - 生成随机文件大小和帧配置，验证帧数计算公式
  - _Requirements: 4.1_

- [ ]* 3.7 编写属性测试：帧索引访问正确性
  - **Property 12: 帧索引访问正确性**
  - **Validates: Requirements 4.2**
  - 生成随机帧索引，验证读取位置正确
  - _Requirements: 4.2_

- [x] 4. 实现帧管理器（FrameManager）





  - 实现帧索引管理（set_current_frame, get_current_frame）
  - 实现帧导航（next_frame, previous_frame）
  - 实现播放控制（play, pause, is_playing）
  - 使用 QTimer 实现动画播放
  - _Requirements: 4.2, 4.3, 4.4, 4.5_

- [ ]* 4.1 编写帧管理器的单元测试
  - 测试帧索引设置和获取
  - 测试帧导航（下一帧、上一帧）
  - 测试播放和暂停功能
  - 测试边界情况（帧索引超出范围）
  - _Requirements: 4.2, 4.3, 4.4_

- [ ]* 4.2 编写属性测试：播放速度控制正确性
  - **Property 13: 播放速度控制正确性**
  - **Validates: Requirements 4.5**
  - 生成随机帧率设置，验证帧间隔时间正确
  - _Requirements: 4.5_

- [x] 5. 实现数据转换工具（converters.py）





  - 实现二进制到十六进制转换
  - 实现十六进制到二进制转换
  - 实现字节到ASCII字符转换
  - 实现 NumPy 数组到 QImage 转换
  - _Requirements: 3.1, 5.1, 5.3_


- [ ]* 5.1 编写转换工具的单元测试
  - 测试二进制到十六进制转换
  - 测试十六进制到二进制转换
  - 测试ASCII转换（可打印和不可打印字符）
  - 测试图像数据转换
  - _Requirements: 5.1, 5.3, 3.1_

- [ ]* 5.2 编写属性测试：十六进制转换正确性
  - **Property 14: 十六进制转换正确性（Round-trip）**
  - **Validates: Requirements 5.1**
  - 生成随机二进制数据，验证 binary → hex → binary 转换一致性
  - _Requirements: 5.1_

- [ ]* 5.3 编写属性测试：ASCII转换正确性
  - **Property 16: ASCII转换正确性**
  - **Validates: Requirements 5.3**
  - 生成随机字节值，验证ASCII表示正确
  - _Requirements: 5.3_

- [ ]* 5.4 编写属性测试：图像数据转换正确性
  - **Property 8: 图像数据转换正确性**
  - **Validates: Requirements 3.1**
  - 生成随机像素数据，验证转换为QImage后尺寸匹配
  - _Requirements: 3.1_


- [x] 6. 实现错误处理器（ErrorHandler）




  - 实现 handle_file_error 方法
  - 实现 handle_parse_error 方法
  - 实现 validate_config 方法
  - 创建错误对话框显示函数
  - _Requirements: 1.4, 8.2, 8.5, 9.1, 9.2, 9.3_

- [ ]* 6.1 编写错误处理器的单元测试
  - 测试文件错误处理
  - 测试解析错误处理
  - 测试配置验证
  - 测试各种边界情况
  - _Requirements: 1.4, 8.2, 8.5, 9.1, 9.2, 9.3_


- [ ]* 6.2 编写属性测试：无效操作提示一致性
  - **Property 20: 无效操作提示一致性**
  - **Validates: Requirements 8.5, 9.1, 9.2, 9.3**
  - 生成各种无效操作场景，验证错误提示显示
  - _Requirements: 8.5, 9.1, 9.2, 9.3_

- [x] 7. 实现图像视图组件（ImageView）





  - 创建 ImageView 类继承 QWidget
  - 实现 display_image 方法显示图像
  - 实现缩放功能（zoom_in, zoom_out, fit_to_window）
  - 实现鼠标悬停显示像素信息（mouseMoveEvent）
  - 实现 get_pixel_info 方法
  - 添加滚动条支持
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ]* 7.1 编写图像视图的单元测试
  - 测试图像显示功能
  - 测试缩放功能
  - 测试像素信息获取
  - 测试滚动条显示
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ]* 7.2 编写属性测试：像素信息准确性
  - **Property 9: 像素信息准确性**
  - **Validates: Requirements 3.2**
  - 生成随机图像数据和坐标，验证返回的像素值正确
  - _Requirements: 3.2_

- [ ]* 7.3 编写属性测试：图像缩放一致性
  - **Property 10: 图像缩放一致性**
  - **Validates: Requirements 3.4, 3.5**
  - 生成随机缩放因子，验证缩放后的图像尺寸正确
  - _Requirements: 3.4, 3.5_

- [x] 8. 实现十六进制视图组件（HexView）





  - 创建 HexView 类继承 QWidget
  - 实现 display_hex_data 方法
  - 实现 format_hex_line 方法（地址、十六进制、ASCII）
  - 实现虚拟滚动优化性能
  - 实现 search_pattern 方法
  - 实现 highlight_matches 方法
  - 实现 scroll_to_position 方法
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 6.2, 6.3, 6.4_


- [ ]* 8.1 编写十六进制视图的单元测试
  - 测试十六进制显示格式
  - 测试地址偏移量显示
  - 测试ASCII字符显示
  - 测试搜索功能
  - 测试高亮显示
  - _Requirements: 5.1, 5.2, 5.3, 6.2, 6.3_

- [ ]* 8.2 编写属性测试：地址偏移量正确性
  - **Property 15: 地址偏移量正确性**
  - **Validates: Requirements 5.2**
  - 生成随机行号，验证地址偏移量计算正确
  - _Requirements: 5.2_

- [ ]* 8.3 编写属性测试：十六进制搜索输入验证
  - **Property 17: 十六进制搜索输入验证**
  - **Validates: Requirements 6.1**
  - 生成随机字符串，验证验证逻辑正确
  - _Requirements: 6.1_

- [ ]* 8.4 编写属性测试：十六进制搜索完整性
  - **Property 18: 十六进制搜索完整性**
  - **Validates: Requirements 6.2**
  - 生成随机数据和搜索模式，验证所有匹配位置都被找到
  - _Requirements: 6.2_

- [ ]* 8.5 编写属性测试：搜索结果高亮正确性
  - **Property 19: 搜索结果高亮正确性**
  - **Validates: Requirements 6.3**
  - 生成随机匹配位置，验证高亮标记正确
  - _Requirements: 6.3_

- [x] 9. 实现控制面板组件（ControlPanel）





  - 创建 ControlPanel 类继承 QWidget
  - 添加分辨率下拉框（预设：640×512, 320×256, 1280×1024等）
  - 添加位深度单选按钮（8位/16位）
  - 添加字节序单选按钮（小端/大端）
  - 添加行偏移输入框
  - 添加帧控制组件（当前帧显示、前进/后退按钮）
  - 添加播放控制按钮（播放/暂停）
  - 定义并连接所有信号
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 4.2, 4.3, 4.4_


- [ ]* 9.1 编写控制面板的单元测试
  - 测试UI组件初始化
  - 测试信号发射
  - 测试参数更新
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 4.2_


- [x] 10. 实现主窗口（MainWindow）



  - 创建 IRImageViewer 类继承 QMainWindow
  - 实现 setup_ui 方法创建菜单栏、工具栏、状态栏
  - 创建 QTabWidget 包含图像视图和十六进制视图
  - 添加控制面板到左侧
  - 实现 load_file 方法（打开文件对话框）
  - 连接控制面板信号到相应处理函数
  - 实现 update_status 方法更新状态栏
  - 实现 show_error 方法显示错误对话框
  - _Requirements: 1.1, 1.5, 7.1, 7.2, 7.3, 7.4, 7.5, 8.3_

- [ ]* 10.1 编写主窗口的单元测试
  - 测试窗口初始化
  - 测试菜单栏和工具栏创建
  - 测试标签页切换
  - 测试文件加载流程
  - _Requirements: 7.1, 7.2, 7.4, 7.5_

- [ ]* 10.2 编写属性测试：文件信息显示完整性
  - **Property 3: 文件信息显示完整性**
  - **Validates: Requirements 1.5**
  - 生成随机文件，验证状态栏显示包含文件名、大小和路径
  - _Requirements: 1.5_

- [x] 11. 集成所有组件并实现完整工作流





  - 在主窗口中集成 FileLoader、ImageParser、FrameManager
  - 实现文件加载到图像显示的完整流程
  - 实现参数变更触发图像重新解析
  - 实现帧切换功能
  - 实现播放动画功能
  - 实现十六进制视图数据加载
  - 实现十六进制搜索功能
  - _Requirements: 1.1, 1.2, 2.1, 2.2, 2.3, 2.4, 3.1, 4.1, 4.2, 4.3, 5.1, 6.2_


- [ ]* 11.1 编写集成测试
  - 测试完整的文件加载到显示流程
  - 测试参数变更触发重新解析
  - 测试帧切换和播放
  - 测试十六进制视图和搜索
  - _Requirements: 1.1, 1.2, 2.1, 3.1, 4.2, 5.1, 6.2_

- [x] 12. Checkpoint - 确保所有测试通过




  - 确保所有测试通过，如有问题请询问用户

- [x] 13. 创建应用程序入口和文档




  - 创建 main.py 作为应用程序入口点
  - 实现命令行参数支持（可选：直接打开指定文件）
  - 创建 README.md 包含使用说明
  - 创建 setup.py 用于安装
  - 添加代码注释和文档字符串
  - _Requirements: 10.3_

- [ ]* 13.1 编写使用示例和测试
  - 创建示例二进制文件
  - 编写使用示例代码
  - 测试命令行参数功能
  - _Requirements: 10.3_

- [ ] 14. 性能优化和最终测试
  - 验证大文件（>100MB）使用内存映射
  - 验证十六进制视图虚拟滚动性能
  - 测试帧缓存功能
  - 进行内存使用分析
  - 测试各种边界情况
  - _Requirements: 1.3, 5.4, 9.1, 9.2, 9.3, 9.4_

- [ ]* 14.1 编写性能测试
  - 测试大文件加载性能
  - 测试十六进制视图滚动性能
  - 测试帧切换性能
  - _Requirements: 1.3, 5.4_

- [ ] 15. Final Checkpoint - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户
