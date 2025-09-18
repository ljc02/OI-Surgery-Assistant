# OI-Surgery-Assistant 分析 APP – 打包与使用说明（v1.0）

> 目标：依据以下 7 点需求完成从“骨骼/皮肤 → 动作周期化 → 视频模型生成/调参 → APP 导入 → 量表评分 → 医患反馈”的一体化流程。  
> 七点需求：1) OpenSim 模型 skin 套皮；2) 将 .mot 动作修改为周期性；3) 在 Colab 上运行 StableAnimator 与 MimicMotion；4) 视频模型调参；5) 导入 APP 界面；6) 问卷打分标准；7) 患者/医生反馈结果。

---

## 项目简介
本项目面向成骨不全症（OI）患者的下肢矫形手术疗效展示。目前，术后效果主要依赖医生的口头描述，患者及家属难以直观理解，导致医患沟通存在障碍。为此，我们基于患者术前、术后 X 光片，模拟其步态变化，并进一步生成 真人行走视频，以多角度对比的形式直观呈现手术效果。项目还设计了 多维度评价问卷（临床准确性、视觉真实性、患者友好度、可展示性、医生友好度），用于系统性收集反馈，确保视频既能真实反映临床情况，又便于患者理解和医生使用，从而提升医患沟通与康复指导的质量。

---

## 目录
- [0. 项目结构](#0-项目结构)
- [1) OpenSim 模型 skin 套皮](#1-opensim-模型-skin-套皮)
- [2) 将 .mot 修改为周期性](#2-将-mot-修改为周期性)
- [3) 在 Colab 上运行视频生成模型](#3-在-colab-上运行视频生成模型)
- [4) 视频模型调参参考](#4-视频模型调参参考)
- [5) 导入 APP 界面](#5-导入-app-界面)
- [6) 问卷打分标准](#6-问卷打分标准)
- [7) 患者/医生反馈结果（待完善）](#7-患者医生反馈结果待完善)
- [8) 常见问题（FAQ）](#8-常见问题faq)
- [许可证](#许可证)
- [引用](#引用)

---

## 0. 项目结构

```text
project_root/
├─ data/
│  ├─ opensim/
│  │  ├─ models/                # .osim 模型、缩放模型
│  │  ├─ geometry/              # 皮肤网格 .obj/.stl/.vtp
│  │  ├─ motions_raw/           # 原始 .mot/.sto 动作
│  │  └─ motions_cyclic/        # 周期化后的 .mot
│  ├─ video/
│  │  ├─ inputs_side/           # 原视频/侧面参考视频
│  │  ├─ inputs_side_frame/     # 原视频/侧面参考视频提取帧
│  │  ├─ inputs-front/          # 原视频/正面参考视频
├─ app/
│  ├─ 2025_1.apk/               # APP
│  ├─ OILLOSPAS.zip             # APP 后端源码
│  └─ SurgeryService.zip        # APP 前端源码
├─ scripts/
│  └─ make_cyclic_mot.py        # 将 .mot 周期化
└─ README.md
```


# 1) OpenSim 模型 skin 套皮

> 目标：将外部皮肤网格（OBJ/STL/VTP）以刚性随动方式挂到 .osim 各个 Body 上，并与 .mot 动作联动预览。

---

## 1.1 前置准备

推荐目录结构：<br>
- data/opensim/<br>
  - models/ # .osim 骨骼模型（已完成 Scale/IK 校验）<br>
    - geometry/ # 皮肤网格（OBJ/STL/VTP）<br>
      - skin_pelvis.obj<br>
      - skin_femur_r.obj<br>
      - skin_tibia_r.obj<br>
      - skin_femur_l.obj<br>
      - skin_tibia_l.obj<br>
- motions_raw/ # .mot/.sto 动作（用于联动预览）


约定与要求：
- 单位使用米（m），右手坐标系。
- 旋转在 OpenSim 中按 XYZ 顺序应用，GUI 中以度（deg）显示最直观。
- 网格命名尽量与 Body 对应（如 pelvis/femur_r/tibia_r），便于批量处理。
- OpenSim 套皮为刚性随动。如需更自然的外观，将皮肤拆分为多段分别附着到相邻 Body。

---

## 1.2 编辑 .osim 文件以装配皮肤

```BodySet
<Body name="skin_hand_r">
  <!--The geometry used to display the axes of this Frame.-->
  <FrameGeometry name="frame_geometry">
    <!--Path to a Component that satisfies the Socket 'frame' of type Frame.-->
    <socket_frame>..</socket_frame>
    <!--Scale factors in X, Y, Z directions respectively.-->
    <scale_factors>0.29999999999999999 0.29999999999999999 0.29999999999999999</scale_factors>
  </FrameGeometry>
  <!--List of geometry attached to this Frame. Note, the geometry are treated as fixed to the frame and they share the transform of the frame when visualized-->
  <attached_geometry>
    <Mesh name="skin_hand_right">
      <!--Path to a Component that satisfies the Socket 'frame' of type Frame.-->
      <socket_frame>..</socket_frame>
      <!--Scale factors in X, Y, Z directions respectively.-->
      <scale_factors>1 1 1</scale_factors>
      <!--Default appearance attributes for this Geometry-->
      <Appearance>
        <!--Flag indicating whether the associated Geometry is visible or hidden.-->
        <visible>true</visible>
        <!--The opacity used to display the geometry between 0:transparent, 1:opaque.-->
        <opacity>1</opacity>
        <!--The color, (red, green, blue), [0, 1], used to display the geometry. -->
        <color>0.16862745583057404 0.20784313976764679 0.3803921639919281</color>
        <!--Visuals applied to surfaces associated with this Appearance.-->
        <SurfaceProperties>
          <!--The representation (1:Points, 2:Wire, 3:Shaded) used to display the object.-->
          <representation>3</representation>
        </SurfaceProperties>
      </Appearance>
      <!--Name of geometry file.-->
      <mesh_file>C:\Users\twili\OneDrive\Desktop\main1\main\hand_r.stl</mesh_file>
    </Mesh>
  </attached_geometry>
  <!--The mass of the body (kg)-->
  <mass>1.6941896825604743</mass>
  <!--The location (Vec3) of the mass center in the body frame.-->
  <mass_center>0 0 0</mass_center>
</Body>
```
```JointSet
<WeldJoint name="hand_r_skin_attachment">
  <!--Path to a Component that satisfies the Socket 'parent_frame' of type PhysicalFrame (description: The parent frame for the joint.).-->
  <socket_parent_frame>hand_r_offset</socket_parent_frame>
  <!--Path to a Component that satisfies the Socket 'child_frame' of type PhysicalFrame (description: The child frame for the joint.).-->
  <socket_child_frame>hand_r_skin_frame</socket_child_frame>
  <!--Physical offset frames owned by the Joint that are typically used to satisfy the owning Joint's parent and child frame connections (sockets). PhysicalOffsetFrames are often used to describe the fixed transformation from a Body's origin to another location of interest on the Body (e.g., the joint center). When the joint is deleted, so are the PhysicalOffsetFrame components in this list.-->
  <frames>
    <PhysicalOffsetFrame name="hand_r_offset">
      <!--The geometry used to display the axes of this Frame.-->
      <FrameGeometry name="frame_geometry">
        <!--Path to a Component that satisfies the Socket 'frame' of type Frame.-->
        <socket_frame>..</socket_frame>
        <!--Scale factors in X, Y, Z directions respectively.-->
        <scale_factors>1 1 1</scale_factors>
      </FrameGeometry>
      <!--Path to a Component that satisfies the Socket 'parent' of type C (description: The parent frame to this frame.).-->
      <socket_parent>/bodyset/hand_r</socket_parent>
      <!--Translational offset (in meters) of this frame's origin from the parent frame's origin, expressed in the parent frame.-->
      <translation>0 -0.07 0</translation>
      <!--Orientation offset (in radians) of this frame in its parent frame, expressed as a frame-fixed x-y-z rotation sequence.-->
      <orientation>0 0 0</orientation>
    </PhysicalOffsetFrame>
    <PhysicalOffsetFrame name="hand_r_skin_frame">
      <!--The geometry used to display the axes of this Frame.-->
      <FrameGeometry name="frame_geometry">
        <!--Path to a Component that satisfies the Socket 'frame' of type Frame.-->
        <socket_frame>..</socket_frame>
        <!--Scale factors in X, Y, Z directions respectively.-->
        <scale_factors>1 1 1</scale_factors>
      </FrameGeometry>
      <!--Path to a Component that satisfies the Socket 'parent' of type C (description: The parent frame to this frame.).-->
      <socket_parent>/bodyset/skin_hand_r</socket_parent>
      <!--Translational offset (in meters) of this frame's origin from the parent frame's origin, expressed in the parent frame.-->
      <translation>0 0 0</translation>
      <!--Orientation offset (in radians) of this frame in its parent frame, expressed as a frame-fixed x-y-z rotation sequence.-->
      <orientation>0 0 0</orientation>
    </PhysicalOffsetFrame>
  </frames>
</WeldJoint>
```
说明：在 .osim 中，修改<mesh_file>C:\Users\twili\OneDrive\Desktop\main1\main\hand_r.stl</mesh_file>的路径即可改变皮肤模型，修改<translation>0 -0.07 0</translation>和<orientation>0 0 0</orientation>以改变皮肤模型与人体的适配程度，修改<scale_factors>1 1 1</scale_factors>以改变皮肤模型大小。


# 2) 将 .mot 修改为周期性
## 2.1 方法概述<br>
将首尾关键帧 过渡混合（blend），并重采样到统一长度，使 state(t=0) ≈ state(t=T)，避免循环跳变。

## 2.2 手动组合/Python 脚本（待完成）<br>
依赖：numpy, pandas。输入/输出：.mot（列含时间与各关节角度）。

## 2.3 录制行走视频<br>
方便后续输入动画生成模型生成类真人行走视频。


# 3) 在 Colab 上运行视频生成模型

## 3.1 Colab 通用设置及链接<br>
运行时类型：GPU（A100首选）；  

StableAnimator_jupyter.ipynb: https://colab.research.google.com/drive/1-9Tsus8XdsJbzBE1Pvu59aSDXdABV65U?usp=sharing  

MimicMotion.ipynb: https://colab.research.google.com/drive/1LTlkepWvFSDk4-9RvKO5hKCa9-jGvZEU?usp=sharing

## 3.2 StableAnimator（用于侧面动作生成）<br>
使用说明：环境配好后，运行下段程序将target folder提取到pose folder中然后在UI中运行即可，调参在test.yaml中

```
!python DWPose/skeleton_extraction.py --target_image_folder_path="/content/t2" --ref_image_path="/content/d75.png" --poses_folder_path="/content/p2"
```

输入：参考视频（data/video/inputs/*.mp4）；

关键参数及推荐设置：

- Width / Height：输出分辨率，目前仅支持 512×512 和 576×1024。分辨率越高画质越好，但显存/推理时间越大。

- Guidance Scale：CFG 引导强度。推荐值 3.0。↑更贴合输入图像外观，但可能僵硬或闪烁；↓更自然但易偏离输入。

- Inference Steps：扩散步数。推荐 25。↑细节更好但速度慢；↓速度快但容易模糊。

- FPS：输出帧率。直接决定视频播放的流畅度（不改变动作时长）。常用 8–15。

- Overlap Frames：分块生成时相邻视频片段的重叠帧数。推荐 4。↑可缓解拼接痕迹，但生成更慢。

- Tile Size：渲染时的切片大小。推荐 16。小显存可尝试 4–8，显存足够保持 16。

- Noise Augmentation Strength：运动噪声增强。推荐 0.02。↑能增强动态一致性，↓更贴近输入。

- Decode Chunk Size：解码时的批次大小。推荐 4 或 16。显存不足时用 4，速度优先用 16。

- Random Seed：随机种子（-1 表示随机）。固定数值可复现结果。

```
Width: 512
Height: 512
Guidance scale: 3.0
Inference steps: 25
FPS: 12
Overlap Frames: 4
Tile Size: 16
Noise Augmentation Strength: 0.02
Decode Chunk Size: 16
Random Seed: 42
```

输出：逐帧图像与合成视频，保存至 data/video/stableanimator/。

## 3.3 MimicMotion（用于正面动作生成）<br>
使用说明：环境配好后，将参考视频和人物正面照上传至云端，在inference.py中输入视频及照片绝对路径运行即可，调参在test.yaml中

输入：参考视频（data/video/inputs/*.mp4）；

关键参数及推荐设置：

- base_model_path：底座 SVD 模型（一般不改）。

- ckpt_path：MimicMotion 权重路径（与你环境一致即可）。

- ref_video_path / ref_image_path：动作来源视频 & 人物外观图。

- num_frames：生成帧数。越大越长，显存与时间线性增加。

- resolution：长边分辨率（短边按模型比例等比缩放）。分辨率越高越清晰、显存/耗时越大。

- frames_overlap：滑动窗口拼接时相邻片段的重叠帧数。越大越平滑但速度更慢。

- num_inference_steps：扩散步数。越大细节越好、耗时越久。常用 20–35。

- noise_aug_strength：运动噪声增强。0–0.2常用；抖动/卡顿可适当↑，脸漂或形变则↓。

- guidance_scale：CFG 引导强度。1.5–3.5常用；↑更贴合参考图外观但易僵硬/闪烁，↓更顺滑。

- sample_stride：采样步长。2较稳；想更快可 3，但细节会降。

- fps：目标帧率（不改变动作时长仅改变视频流畅度/时基）。

- seed：随机种子，可复现；换 seed 可探索不同细节。

```
num_frames: 72
resolution: 576
frames_overlap: 6
num_inference_steps: 25
noise_aug_strength: 0.05
guidance_scale: 2.0
sample_stride: 2
fps: 15
```

输出：data/video/mimicmotion/。

建议：同一段素材，先跑一遍得到初步套皮结果后，再用生成的视频输入模型Dwpose Extraction提取行走步态会更稳定。


# 4) 视频模型调参参考
| 目的       | 关键项                        | 建议范围     | 说明                                    | 提升细节                      |
|------------|-------------------------------|--------------|-----------------------------------------|--------------------------------|
| 稳定风格   | num_inference_steps            | 30–60        | 步数越大细节越多但速度更慢              | 适当提高步数可提升画面质量     |
| 降低漂移   | seed                           | 固定数       | 便于复现实验                            | 保持一致性，减少随机性         |
| 时间一致性 | guidance_scale                 | 3–6          | 过大可能使动作失真                      | 控制动作自然度                 |
|            | consistency / temporal_weight  | 0.6–0.9      | 越大越稳但易拖影                        | 平衡稳定性与动态流畅度         |
| 面部质量   | face_restore / GFPGAN          | on           | 人像场景建议开启                        | 提升人脸清晰度与细节           |
| 分辨率     | width / height                 | 512–768      | 先小后大，注意显存                      | 分阶段提升，避免显存溢出       |


调参流程：

固定 seed 与 fps，跑 8–12 帧小样；
微调 guidance_scale 和 denoise_strength 找平衡；
提升 num_inference_steps 与分辨率；
若出现闪烁/形变：提高一致性权重或引入光流稳定；
记录 配置→效果（保存到 app.manifest.json 的 metadata 字段）。


# 5) 导入 APP 界面

Postman邀请链接：https://app.getpostman.com/join-team?invite_code=3be8ecf562c8de22a0cb4f64172f94670794024f1035fe27c4a8df1fc3eb7ba0&target_code=e53cc6859ed9fb895cf27fbaf2e799a9

## 5.1 上传接口 (/api/schemes/upload)
简述：upload 是方案上传接口，用于提交视频、图片及相关描述信息。成功请求后，系统会返回上传结果。

![72afbe038f8820b8db69e9e764932487](https://github.com/user-attachments/assets/07149c37-5b47-44da-a447-608b3a899749)

请求方式：POST http://<server-ip>:8080/api/schemes/upload

请求参数：
| 参数名               | 类型   | 说明                |
| ----------------- | ---- | ----------------- |
| **schemeVideo**   | File | 方案视频文件            |
| **userId**        | Text | 用户 ID（通过用户查询接口获取） |
| **schemeNumber**  | Text | 方案步骤编号            |
| **schemeContent** | Text | 方案描述              |
| **schemeImage**   | File | 方案图片              |

使用步骤（Postman 示例）：

1.打开 Postman，选择 POST 请求。

2.在 URL 栏输入：http://<server-ip>:8080/api/schemes/upload。

3.切换到 Body → form-data。

4.添加字段并填写：

说明：

- schemeVideo → 上传 .mp4 文件

- userId → 例如 1

- schemeNumber → 例如 1

- schemeContent → 例如 原始步骤

- schemeImage → 上传 .png 图片

- 点击 Send 发送请求。

## 5.2 创建用户接口 (/api/users)
简述：用于新建用户信息。

<img width="2417" height="358" alt="ea8c949176a0bcb0736cf33a588dab1b" src="https://github.com/user-attachments/assets/e0693464-37fb-45cc-a070-212e5ec0d073" />

请求方式：POST http://<server-ip>:8080/api/users

```json
{
  "treatmentNumber": "HZ010802",
  "name": "李四",
  "age": 36,
  "height": 177,
  "weight": 77
}
```

说明：

- treatmentNumber：病历号/治疗编号

- name：患者姓名

- age：年龄

- height：身高 (cm)

- weight：体重 (kg)

## 5.3 查询所有用户（/api/allUsers）
简述：获取系统中所有已注册用户的信息。
当忘记用户 id 或者需要查看用户基本资料时，可以使用该接口。

请求方式：GET http://<server-ip>:8080/api/allUsers

```
  {
    "id": 1,
    "treatmentNumber": "HZ010802",
    "name": "李四",
    "age": 36,
    "height": 177,
    "weight": 77
  },
  {
    "id": 2,
    "treatmentNumber": "HZ010803",
    "name": "王五",
    "age": 40,
    "height": 170,
    "weight": 68
  }
```

## 6) 问卷打分标准
<br>
视觉真实性<br>
1. 您觉得视频中的衣服搭配是否自然、符合真实场景？<br>
👉 1 = 非常不自然，5 = 非常自然<br>
2. 您觉得视频中的面部表情是否真实、自然？<br>
👉 1 = 完全不真实，5 = 非常真实<br>
3. 您觉得视频背景是否贴近真实环境？<br>
👉 1 = 完全不真实，5 = 非常真实<br>

患者友好度<br>
4. 您觉得视频播放的速度是否合适？<br>
👉 1 = 完全不合适，5 = 非常合适<br>
5. 您在观看过程中是否感觉到卡顿？<br>
👉 1 = 经常卡顿，5 = 完全流畅<br>
6. 您觉得字幕内容是否容易理解？<br>
👉 1 = 非常难懂，5 = 非常容易理解<br>

可展示性<br>
7. 您觉得视频是否能从多个角度全面展示手术效果？<br>
👉 1 = 完全不能，5 = 完全覆盖<br>
8. 您更倾向于单个视频播放还是对比播放？<br>
👉 1 = 单个更好，5 = 对比更好<br>

医生友好度<br>
9. 您觉得视频中是否包含清晰的量化指标（如步速、步幅、地反力等）？<br>
👉 1 = 完全没有，5 = 非常清晰<br>
10. 您觉得演示端是否易于操作、便于临床使用？<br>
👉 1 = 非常难操作，5 = 非常容易操作<br>

## 7) 患者/医生反馈结果（待完善）
7.1 问卷数据


7.2 数据合规与匿名化



## 8) 常见问题（FAQ）
皮肤网格错位/翻转：检查单位（cm→m）、法线与旋转顺序（XYZ）。

.mot 循环跳帧：增大 --blend 或提高 fps；确保最后一帧与第一帧数值一致。

Colab 显存不足：先降分辨率与步数，再分段生成、最后拼接。

视频闪烁：提高时间一致性、降低 denoise，或启用光流/参考帧稳像。


## 引用
> 本项目使用 MimicMotion (2024) 和 StableAnimator (2024) 作为动作生成与序列建模工具。
```
@misc{mimicmotion2024,
  title   = {MimicMotion: High-Fidelity Human Motion Generation via Diffusion Models},
  author  = {Authors et al.},
  year    = {2024},
  archivePrefix = {arXiv},
  eprint  = {xxxx.xxxxx},
  url     = {https://github.com/MimicMotionRepo}
}

@misc{stableanimator2024,
  title   = {StableAnimator: Consistent Video Generation with Stable Diffusion},
  author  = {Authors et al.},
  year    = {2024},
  archivePrefix = {arXiv},
  eprint  = {xxxx.xxxxx},
  url     = {https://github.com/StableAnimatorRepo}
}
```

