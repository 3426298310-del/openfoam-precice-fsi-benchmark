# 来源、版本和沿用内容

本项目是学习用途的 FSI3 分区耦合复现，**不是 preCICE 官方已验证的 CalculiX FSI3 发布版**。

- preCICE tutorials 主线：<https://github.com/precice/tutorials>，提交 `17015c10387c222a70eb73de6702b48187dd29f7`。
- CalculiX FSI3 案例来源：JoSchrdr 向 tutorials 提交的 [PR #304](https://github.com/precice/tutorials/pull/304)，获取时仍未合并；提交 `3cb8e705636dcaf8b0e5f10f3c899200b3867c2e`。
- PR 原始文件保留于 `upstream/turek-hron-fsi3-calculix/`。沿用几何、流体块网格、结构网格和材料输入，以及原始耦合算法及阈值。
- 当前官方 [FSI3 主教程](https://precice.org/tutorials-turek-hron-fsi3) 的结构求解器为 deal.II/Nutils。采用主线 `fluid-openfoam/0/U` 的原生 codedFixedValue 抛物线入口和 0–2 s 余弦启动。
- [OpenFOAM adapter v1.3.0](https://github.com/precice/openfoam-adapter/tree/v1.3.0)，提交 `74b8719ce874c793a581fd009a54c0e1c7923b1e`；该版改用 preCICE v3，CI 默认 OpenFOAM v2312。
- [CalculiX adapter v2.20.2](https://github.com/precice/calculix-adapter/tree/v2.20.2)，提交 `f362a16d54a31985712f4c4302128f6923bd1d00`，基于 CalculiX 2.20。
- [preCICE 3.2.0 release](https://github.com/precice/precice/releases/tag/v3.2.0)，Ubuntu noble 官方二进制包。
- CalculiX 2.20 源码：<https://www.dhondt.de/ccx_2.20.src.tar.bz2>。
- 基准原始论文：J. Hron, S. Turek, *A monolithic FEM solver for an ALE formulation of fluid–structure interaction with configuration for numerical benchmarking*, ECCOMAS CFD 2006，<https://wwwold.mathematik.tu-dortmund.de/papers/HronTurek2006a.pdf>。

## 本项目的修改

1. preCICE XML v2 → v3：移除 solver-interface，网格单独声明维数，provide/receive-mesh，socket acceptor/connector，RBF mapping 新语法。
2. groovyBC → 官方主教程 codedFixedValue；因此加入原 PR 没有的标准平滑入口启动。删除 groovyBC 动态库依赖。
3. 修正仅用于总力监测的 rhoInf 从 1 到 1000（耦合本身原先已经使用 1000）。二维单位厚度力须再除以实际厚度 0.01 m。
4. 增加隔离运行目录、失败传播、日志保存、后处理及中文文档。减少结构场输出频率，保留每个时间窗的 watchpoint。
5. 文件布局改为 fluid/solid/coupling，修正配置相对路径。

## 许可

教程仓库附带 LGPL-3.0（根目录 LICENSE）；沿用教程文件保留该许可。适配器各自保留原仓库 LICENSE：OpenFOAM adapter GPL-3.0；CalculiX adapter 整体 GPL-3.0（其中修改的 CalculiX 文件为 GPL-2.0-or-later）。不将下载的第三方论文或系统二进制打包进 Git。新脚本及文档也按根目录 LGPL-3.0 发布。
