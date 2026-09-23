# Turek-Hron FSI benchmark: partitioned OpenFOAM + CalculiX + preCICE

这是一个**学习用途**的流固耦合（FSI）数值复现项目，目标是完整走通一个经典
FSI benchmark 的「建模 → 分区耦合求解 → 后处理 → 与文献参考值对比」闭环，
用于展示 FSI 工程实践能力。

> English summary: A learning-oriented, fully partitioned fluid–structure
> interaction (FSI) reproduction of the classical Turek & Hron benchmark
> (steady case **FSI1**), coupling **OpenFOAM** (fluid, finite volume) with
> **CalculiX** (structure, finite element) through **preCICE**. The flow past a
> fixed cylinder with an attached elastic beam is solved by a serial-implicit
> IQN-ILS coupling scheme; tip displacement and force time series are compared
> against the published reference of Hron & Turek (ECCOMAS CFD 2006).

## 1. 案例与基准版本

选用的基准是 **Turek & Hron FSI1**（稳态层流，Re = 20）。该案例与 FSI2/FSI3
共用同一几何，仅流体/固体参数不同：

- 计算域：长 2.5 m × 高 0.41 m 的二维通道；
- 障碍物：圆心 (0.2, 0.2) m、半径 0.05 m 的刚性圆柱；
- 弹性梁：长 0.35 m × 厚 0.02 m，固支端 x = 0.25 m，自由端 x = 0.6 m（监测点
  A = (0.6, 0.2)）；
- 固体为三维，沿 z 向挤出 0.01 m（z ∈ [−0.005, 0.005]），流体用 `empty`
  前后面按二维处理。

本仓库同时保留了 **FSI3**（Re = 200，周期性拍动）的完整配置与短时试运行结果，
但受虚拟机计算资源限制，其完整 20 s 计算暂未完成（详见「限制与说明」）。

## 2. 软件栈与版本（已在本机验证）

| 组件 | 版本 | 说明 |
| --- | --- | --- |
| 操作系统 | Ubuntu 24.04.4 LTS (Noble) | kernel 7.0.0-31 |
| 流体 | OpenFOAM **v2312** | `/usr/lib/openfoam/openfoam2312`，pimpleFoam |
| 结构 | CalculiX **2.20**（耦合版 `ccx_preCICE`） | 由源码 + calculix-adapter 2.20.2 构建 |
| 耦合库 | preCICE **3.2.0** | Ubuntu 二进制包 `libprecice3` |
| OpenFOAM 适配器 | **v1.3.0** | 源码构建 `libpreciceAdapterFunctionObject.so` |
| CalculiX 适配器 | **v2.20.2** | 生成 `ccx_preCICE` |
| 可视化 | ParaView 5.11.2 | 后处理用 `pvpython`/VTK |
| 后处理 | Python 3.12.3 | numpy / scipy / matplotlib / vtk |
| MPI | OpenMPI 4.1.6 | 串行运行，预留并行扩展 |

详细来源、提交号和沿用/修改说明见 [docs/SOURCES.md](docs/SOURCES.md)。

## 3. 目录结构

```
.
├── README.md               # 本文件
├── docs/                   # 基准参数、版本信息、来源说明、技术报告
├── fluid/                  # OpenFOAM 算例（0/、constant/、system/）
├── solid/                  # CalculiX 输入（.msh/.inp/.nam/config.yml）
├── coupling/               # preCICE XML 配置
├── variants/fsi3/          # FSI3 变体（独立 fluid/solid/coupling）
├── scripts/                # 安装、运行、后处理脚本
├── results/                # 后处理产物（图、CSV、汇总 JSON）与安装日志
└── upstream/               # 第三方源码（gitignore，不提交）
```

`results/runs/`（原始运行目录）与 `upstream/`、下载的论文等均被 `.gitignore`
排除，只提交配置与可复现的分析结果。

## 4. 安装与运行

### 4.1 前置依赖

Ubuntu 24.04 上安装系统包（本机已装好）：

```bash
sudo apt-get update
sudo apt-get install -y openfoam2312 openfoam2312-dev calculix-ccx libprecice3 \
  paraview python3-vtk9 python3-numpy python3-scipy python3-matplotlib
```

preCICE 的 OpenFOAM 适配器与 CalculiX 适配器需要从源码构建（仓库内的
`scripts/install.sh` / `scripts/build-adapters.sh` 封装了完整流程）。由于适配器
编译产物与第三方源码体积较大，这里不直接打包，`docs/SOURCES.md` 记录了确切的
版本与提交号，可据此离线复现。

### 4.2 短时试运行（冒烟测试）

```bash
source scripts/env.sh
bash scripts/run.sh smoke 0.01 0.01 fsi1
```

### 4.3 完整 FSI1 计算（20 s，约 2000 个耦合窗）

```bash
bash scripts/run.sh fsi1-full 20 0.01 fsi1
```

运行结束后，结果位于 `results/runs/fsi1-full/`，随后执行：

```bash
python3 scripts/postprocess.py results/runs/fsi1-full
python3 scripts/render_fields.py results/runs/fsi1-full
```

在 `results/fsi1-full/` 下生成尖端位移、力、耦合收敛统计与流场图。

## 5. 结果与参考值对比

（此节在完整计算与后处理完成后填写，见 `results/fsi1-full/summary.json` 与
`docs/technical-report.md`。）

## 6. 限制与说明

- 本复现沿用 preCICE tutorials 中一个**尚未合并**的 CalculiX FSI3 案例 PR 的
  几何与网格，并移植到 preCICE v3；并非 preCICE 官方已发布的 CalculiX 验证版。
- 流体力换算：OpenFOAM 的 `forces` 函数对象对 0.01 m 厚的三维面做积分，结果
  除以 0.01 m 得到单位厚度力（N/m），方可与文献参考值（N/m）比较。
- 位移收敛的绝对容差由原 PR 的 `1e-10` 放宽到 `1e-8`（原值在 dt=0.01 s 下
  100 次迭代内不收敛），同时收紧流体线性求解器容差，见
  `docs/benchmark.json` 中的 `_tuning_note`。
- 尚未做网格无关性与时间步无关性研究，数值接近文献不等于模型已验证。

## 7. 许可与致谢

根目录 `LICENSE` 为 LGPL-3.0；教程与适配器文件各自保留原许可证（OpenFOAM
adapter GPL-3.0，CalculiX adapter GPL-3.0，其中修改的 CalculiX 文件为
GPL-2.0-or-later）。基准数据来源：J. Hron, S. Turek, *A monolithic FEM solver
for an ALE formulation of fluid–structure interaction with configuration for
numerical benchmarking*, ECCOMAS CFD 2006。
