# OI-Surgery-Assistant
# OpenSim + StableAnimator/MimicMotion 分析 APP – 打包与使用说明（v1.0）

> 目标：依据以下 7 点需求完成从“骨骼/皮肤 → 动作周期化 → 视频模型生成/调参 → APP 导入 → 量表评分 → 医患反馈”的一体化流程，并给出可复用的目录结构、配置示例、脚本命令与排错建议。  
> 七点需求：1) OpenSim 模型 skin 套皮；2) 将 .mot 动作修改为周期性；3) 在 Colab 上运行 StableAnimator 与 MimicMotion；4) 视频模型调参；5) 导入 APP 界面；6) 问卷打分标准；7) 患者/医生反馈结果。

---

## 目录
- [0. 项目结构（建议）](#0-项目结构建议)
- [1) OpenSim 模型 skin 套皮](#1-opensim-模型-skin-套皮)
- [2) 将 .mot 修改为周期性（循环播放）](#2-将-mot-修改为周期性循环播放)
- [3) 在 Colab 上运行视频生成模型](#3-在-colab-上运行视频生成模型)
- [4) 视频模型调参参考](#4-视频模型调参参考)
- [5) 导入 APP 界面（打包规范）](#5-导入-app-界面打包规范)
- [6) 问卷打分标准（示例）](#6-问卷打分标准示例)
- [7) 患者/医生反馈结果（汇总与报告）](#7-患者医生反馈结果汇总与报告)
- [8) 快速上手（从 0 到可展示）](#8-快速上手从-0-到可展示)
- [9) 常见问题（FAQ / 排错）](#9-常见问题faq--排错)
- [10) 版本控制与可复现性](#10-版本控制与可复现性)
- [11) 术语速查](#11-术语速查)
- [12) 后续可扩展](#12-后续可扩展)
- [许可证](#许可证)
- [引用](#引用)

---

## 0. 项目结构（建议）

```text
project_root/
├─ data/
│  ├─ opensim/
│  │  ├─ models/                # .osim 模型、缩放模型
│  │  ├─ geometry/              # 皮肤网格 .obj/.stl/.vtp
│  │  ├─ motions_raw/           # 原始 .mot/.sto 动作
│  │  └─ motions_cyclic/        # 周期化后的 .mot
│  ├─ video/
│  │  ├─ inputs/                # 原视频/参考视频
│  │  ├─ stableanimator/        # 输出帧/视频
│  │  └─ mimicmotion/           # 输出帧/视频
│  ├─ survey/
│  │  ├─ forms/                 # 量表定义 .csv/.json
│  │  ├─ responses/             # 受试者填写结果 .csv
│  │  └─ scoring/               # 评分结果与报告
│  └─ exports/                  # 面向 APP 的打包产物（glb/mp4/json）
├─ app/
│  ├─ assets/                   # 前端静态资源
│  ├─ config/app.manifest.json  # APP 读取的清单
│  └─ (src/或Unity/Flutter项目)
├─ scripts/
│  ├─ make_cyclic_mot.py        # 将 .mot 周期化
│  ├─ score_surveys.py          # 量表评分
│  ├─ build_manifest.py         # 生成 app.manifest.json
│  └─ export_report.py          # 汇总医患反馈与 PDF 报告
└─ README.md
```
统一以 app/config/app.manifest.json 作为 APP 入口清单：指定可加载的模型、动作、视频与评分文件。


# 1) OpenSim 模型 skin 套皮

> 目标：将外部皮肤网格（OBJ/STL/VTP）以刚性随动方式挂到 .osim 各个 Body 上，并与 .mot 动作联动预览。

---

## 1.1 前置准备

推荐目录结构：<br>
data/opensim/<br>
models/ # .osim 骨骼模型（已完成 Scale/IK 校验）<br>
geometry/ # 皮肤网格（OBJ/STL/VTP）<br>
skin_pelvis.obj<br>
skin_femur_r.obj<br>
skin_tibia_r.obj<br>
skin_femur_l.obj<br>
skin_tibia_l.obj<br>
motions_raw/ # .mot/.sto 动作（用于联动预览）

php-template
复制代码

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
      <translation>0 -0.074760043291802247 0</translation>
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
说明：在 .osim 中，修改<mesh_file>的路径即可改变皮肤模型，修改<translation>和<orientation>以改变皮肤模型与人体的适配程度，修改<scale_factors>以改变皮肤模型大小。


# 2) 将 .mot 修改为周期性（循环播放）
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
输入：参考视频（data/video/inputs/*.mp4）；

关键参数：<br>
prompt/negative_prompt（画面语义）；<br>
num_inference_steps（建议 20-50）；<br>
guidance_scale（建议 3.5-7.5）；<br>
fps（与源视频匹配 24/30/60）；<br>
分辨率 W×H（512）。

输出：逐帧图像与合成视频，保存至 data/video/stableanimator/。

## 3.3 MimicMotion（用于正面动作生成）<br>
输入：参考视频（data/video/inputs/*.mp4）；

关键参数：<br>
pose_strength（动作保真度，0.5-1.0）；<br>
denoise_strength（外观重绘强度，0.2-0.6）；<br>
seed（复现性）；<br>
face_restore/consistency（人脸与帧间一致性）。<br>

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


# 5) 导入 APP 界面（打包规范）

---
## 5.1 上传接口 (/api/schemes/upload)
简述：upload 是方案上传接口，用于提交视频、图片及相关描述信息。成功请求后，系统会返回上传结果。

请求方式：POST http://<server-ip>:8080/api/schemes/upload

请求参数：
| 参数名               | 类型   | 说明                |
| ----------------- | ---- | ----------------- |
| **schemeVideo**   | File | 方案视频文件            |
| **userId**        | Text | 用户 ID（通过用户查询接口获取） |
| **schemeNumber**  | Text | 方案步骤编号            |
| **schemeContent** | Text | 方案描述              |
| **schemeImage**   | File | 方案图片              |

使用步骤（Postman 示例）：<br>
1.打开 Postman，选择 POST 请求。<br>
2.在 URL 栏输入：http://<server-ip>:8080/api/schemes/upload。<br>
3.切换到 Body → form-data。<br>
4.添加字段并填写：<br>
  schemeVideo → 上传 .mp4 文件<br>
  userId → 例如 1<br>
  schemeNumber → 例如 1<br>
  schemeContent → 例如 原始步骤<br>
  schemeImage → 上传 .png 图片<br>
  点击 Send 发送请求。

## 5.2 创建用户接口 (/api/users)
简述：用于新建用户信息。

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

treatmentNumber：病历号/治疗编号

name：患者姓名

age：年龄

height：身高 (cm)

weight：体重 (kg)

5.3 一键生成清单（scripts/build_manifest.py）
自动扫描 data/… 目录生成/更新 app.manifest.json，避免手改遗漏。

## 6) 问卷打分标准（示例）
6.1 量表定义（data/survey/forms/scale_def_v1.json）
json
复制代码
{
  "name": "Rehab-Kinematics-UX",
  "scales": [
    {"id": "pain", "label": "疼痛程度", "items": 3, "type": "likert", "range": [0,10], "direction": "higher-worse"},
    {"id": "fatigue", "label": "疲劳", "items": 2, "type": "likert", "range": [0,5],  "direction": "higher-worse"},
    {"id": "adherence", "label": "依从性", "items": 4, "type": "likert", "range": [1,5],  "direction": "higher-better"}
  ],
  "composite": [
    {"id": "comfort", "formula": "(10-pain_norm)*0.6 + (5-fatigue_norm)*0.4"},
    {"id": "overall", "formula": "comfort*0.5 + adherence_norm*0.5"}
  ],
  "thresholds": {
    "overall": {"good": ">=0.7", "warn": "0.4~0.7", "bad": "<0.4"}
  }
}
说明：各量表先按量程归一化为 [0,1]（若 higher-worse 则取反），再计算复合指标与阈值分级。

6.2 评分脚本（scripts/score_surveys.py）
bash
复制代码
python scripts/score_surveys.py \
  --def data/survey/forms/scale_def_v1.json \
  --in  data/survey/responses/*.csv \
  --out data/survey/scoring/summary_v1.csv
功能：

合并多份受试者答卷；

自动归一化、计算复合分、根据阈值打标签（good/warn/bad）；

产出患者维度与时间维度的统计。

响应 CSV 模板：subject_id, visit_date, pain_q1, pain_q2, …, adherence_q4。

## 7) 患者/医生反馈结果（汇总与报告）
7.1 汇总口径
患者侧：疼痛、疲劳、可用性、依从性趋势（折线图/箱线图）；

医生侧：关键阈值达标率、异常告警清单、典型案例；

模型侧：OpenSim 与视频生成的关键参数→效果对照表，便于回溯。

7.2 导出报告
bash
复制代码
python scripts/export_report.py \
  --manifest app/config/app.manifest.json \
  --scoring  data/survey/scoring/summary_v1.csv \
  --out      data/exports/report_v1.pdf
报告包含：封面、方法流程、模型/视频样例帧、量表结果图、医患建议与结论。

7.3 数据合规与匿名化
存储前将 subject_id 以 hash(subject_id + salt) 处理；

单独保存 re-id 映射表于加密位置（不随 APP 分发）。

## 8) 快速上手（从 0 到可展示）
套皮与动作：完成 *_skinned.osim 与 *_cyclic.mot；

视频生成：在 Colab 分别跑 StableAnimator/MimicMotion，落盘到 data/video/...；

量表：放置量表定义与受试者 CSV 到 data/survey/...；

清单：python scripts/build_manifest.py 生成 app.manifest.json；

评分：python scripts/score_surveys.py 输出 summary_v1.csv；

报告：python scripts/export_report.py 生成 report_v1.pdf；

APP 启动：读取 app.manifest.json 自动加载资源与评分结果。

## 9) 常见问题（FAQ / 排错）
皮肤网格错位/翻转：检查单位（cm→m）、法线与旋转顺序（XYZ）。

.mot 循环跳帧：增大 --blend 或提高 fps；确保最后一帧与第一帧数值一致。

Colab 显存不足：先降分辨率与步数，再分段生成、最后拼接。

视频闪烁：提高时间一致性、降低 denoise，或启用光流/参考帧稳像。

量表维度不一致：在定义中声明 range 与 direction，脚本自动归一化。

清单加载失败：校验路径大小写与相对/绝对路径；使用 JSON 校验器检查格式。

## 10) 版本控制与可复现性
所有关键结果（OpenSim 模型、mot、视频、量表评分）均在文件名与 metadata 中写入参数指纹；

建议使用 git lfs 管理大文件，并保存 environment.yml/requirements.txt 与 Colab .ipynb；

重大里程碑导出 data/exports/<tag>/ 快照。

## 11) 术语速查
OpenSim：肌骨建模/仿真平台；IK（逆运动学）、Scale Tool（个体化缩放）。

.mot：随时间变化的关节角度/力学量时序文件。

StableAnimator/MimicMotion：基于扩散或姿态跟随的视频生成/转描模型。

Likert 量表：常用主观评分量表（如 1–5/0–10）。

## 12) 后续可扩展
将 .mot → FBX/GLB 烘焙，便于游戏引擎/网页端展示；

引入 自动化 CI（如 GitHub Actions）生成 manifest、评分与报告；

添加 异常监测（如疼痛突增、依从性骤降的阈值告警）。

