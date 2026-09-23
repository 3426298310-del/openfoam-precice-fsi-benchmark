# 简历表述（仅描述实际完成的内容）

> 约束：只写已完成并能在面试中讲清楚的工作。不写未完成的 FSI3 完整计算、不写
> 网格/时间步无关性研究（都还没做）。以下 bullet 可直接粘贴或再精简。

## 中文（3 条）

1. 基于 OpenFOAM（流体 pimpleFoam）+ CalculiX（结构 ccx_preCICE）+ preCICE 3.2
   实现 Turek–Hron FSI1（Re=20）的分区式双向流固耦合仿真，完整跑通 20 s、2000
   个耦合时间窗且全部收敛（IQN-ILS 加速，平均每窗 2.06 次耦合迭代）。
2. 尖端位移与阻力/升力结果与 Hron & Turek 2006 基准参考值吻合（力误差 <1%，
   位移误差约 1–3%），并用 Python 编写后处理，生成位移/力时间曲线、耦合收敛
   统计以及压力/速度/涡量流场图。
3. 用 Bash/Python 实现可复现的自动化流程（依赖安装、算例隔离运行、后处理），并
   整理为含 README、技术报告与版本/来源说明的 Git 项目。

## English（3 条）

1. Implemented a partitioned two-way fluid–structure interaction simulation of
   the Turek–Hron FSI1 benchmark (Re = 20) coupling OpenFOAM and CalculiX via
   preCICE, completing a full 20 s run of 2000 coupling windows with every
   window converged (mean 2.06 IQN-ILS iterations).
2. Obtained tip displacement and drag/lift in agreement with the published
   benchmark reference (forces within 1 %, displacements within ~3 %), and
   built Python post-processing for displacement/force time series, coupling
   convergence, and pressure/velocity/vorticity field visualization.
3. Developed automated Bash/Python workflows for dependency installation,
   isolated case execution, and post-processing, and packaged the work as a
   documented, reproducible Git repository.
