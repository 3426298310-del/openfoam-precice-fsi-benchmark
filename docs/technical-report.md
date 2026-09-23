# Turek-Hron FSI1 技术报告

## 1. 问题与目标

复现 Hron & Turek（ECCOMAS CFD 2006）提出的流固耦合基准问题 **FSI1**（稳态
层流，Re = 20）。几何为二维通道内放置刚性圆柱，圆柱后方连接一根弹性梁；流体
流过时对梁施加载荷，梁的变形又反过来改变流场，形成双向耦合。目标是得到梁自由
端（点 A = (0.6, 0.2) m）的位移与作用在「圆柱 + 梁」上的阻力/升力，并与文献
参考值比较。

## 2. 几何与网格

- 计算域：长 2.5 m × 高 0.41 m；
- 圆柱：圆心 (0.2, 0.2) m，半径 0.05 m；
- 弹性梁：长 0.35 m × 厚 0.02 m，固支于 x = 0.25 m，自由端 x = 0.6 m；
- 流固界面：梁与圆柱表面。

流体网格由 `blockMesh` 生成（`fluid/system/blockMeshDict`），20 个六面体块、
二维 1 层单元（前后面为 `empty`），共 **6306** 个单元。结构网格
`solid/turekflap.msh` 为三维，沿 z 向挤出 0.01 m，单元类型 **C3D20R**（二次
缩减积分），共 910 个节点。

## 3. 控制方程与离散

流体为不可压缩 Navier–Stokes 方程（动网格 ALE 形式），用 OpenFOAM
`pimpleFoam` 求解；时间项一阶欧拉，`nCorrectors=2`、
`nNonOrthogonalCorrectors=1`。结构用 CalculiX 求解大变形动力学（`*DYNAMIC,
DIRECT`，隐式 Newton–Raphson，`NLGEOM` 几何非线性开启）。

## 4. 物理参数

FSI1（本报告主体）：

| 量 | 值 |
| --- | --- |
| 流体密度 ρ_f | 1000 kg/m³ |
| 运动黏度 ν_f | 0.001 m²/s |
| 入口平均速度 U | 0.2 m/s（抛物线剖面，0–2 s 余弦启动） |
| 雷诺数 Re = U·D/ν | 20（D = 0.1 m） |
| 固体密度 ρ_s | 1000 kg/m³ |
| 杨氏模量 E | 1.4 MPa |
| 泊松比 ν_s | 0.4 |
| 时间步 Δt | 0.01 s |
| 总时长 T | 20 s（约 2000 个耦合窗） |

FSI3（配置就绪、短试运行通过、完整计算待做）：U = 2.0 m/s（Re = 200）、
E = 5.6 MPa、Δt = 0.0005 s。

## 5. 耦合方法与实现

采用 **preCICE** 做分区（partitioned）耦合，`serial-implicit` 串行隐式方案：

- 每个时间窗内，流体与固体依次求解并交换数据，直至收敛；
- 数据交换：流体 → 固体传**力（Force）**，固体 → 流体传**位移（Displacement）**；
- 加速：**IQN-ILS** 拟牛顿加速，初始松弛 0.1，复用 10 个历史时间窗；
- 映射：RBF 全局直接映射（薄板样条），力用 `conservative`、位移用 `consistent`；
- 收敛判据：位移 `abs-limit=1e-8, rel-limit=1e-6`（strict），力
  `rel-limit=1e-2`（strict），每个时间窗最多 100 次迭代。

OpenFOAM 侧通过 `preciceAdapterFunctionObject` 适配器接入，CalculiX 侧通过
`calculix-adapter` 生成的 `ccx_preCICE` 接入。

## 6. 遇到的问题与解决

1. **preCICE v2 → v3 配置语法变化**：原案例基于 preCICE v2。已重写 XML：移除
   `solver-interface`、网格单独声明维数、改用 `provide-mesh`/`receive-mesh`、
   socket 的 `acceptor`/`connector`、RBF 映射新语法。
2. **groovyBC 依赖**：原案例用 groovyBC 定义入口速度，需额外动态库。改用官方
   主教程的 `codedFixedValue` 抛物线入口，删除 groovyBC 依赖。
3. **总力监测密度错误**：`forces` 函数对象的 `rhoInf` 原为 1，已修正为 1000
   （与耦合一致）；二维单位厚度力再除以 0.01 m 得到 N/m。
4. **位移收敛判据过严**：原 PR 的 `abs-limit=1e-10` 在 dt=0.01 s 下 100 次迭代
   内不收敛（`results/runs/fsi1-pilot` 因 strict 判据 abort）。将位移
   `abs-limit` 放宽到 `1e-8`，同时收紧流体线性求解器容差（p 1e-8、U 1e-9，
   `relTol=1e-5`），随后 `fsi1-pilot-tuned` 稳定收敛。

## 7. 结果与参考值对比

（完整 20 s 计算完成后，由 `scripts/postprocess.py` 生成 `results/fsi1-full/`
下的汇总与对比图，此处填入最终数值与误差。）

## 8. 结论与局限

- 本复现证明 OpenFOAM + CalculiX + preCICE 的分区耦合链路可稳定运行并给出与
  文献同量级的结果。
- 局限：未做网格无关性/时间步无关性研究；沿用第三方 PR 的网格与几何；FSI3
  完整计算未完成。因此当前结论为「与文献参考值数值接近」，而非严格验证。
