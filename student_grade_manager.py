#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生成绩查询与统计工具
=======================
核心功能：
  1. 从文件导入学生成绩数据（学号、姓名、多科成绩）
  2. 按学号或姓名查询学生成绩
  3. 计算每个学生的总分与平均分
  4. 按平均分排序并输出排名
扩展功能：
  5. 新增、删除、修改学生成绩
  6. 将统计结果导出为新文件
"""

import os
import sys
from typing import List, Optional, Dict


# ============================================================
# 学生类 —— 对应"结构体/类"知识点
# ============================================================
class Student:
    """学生数据结构：学号、姓名、多科成绩"""

    # 科目列表（可扩展）
    SUBJECTS: List[str] = ["语文", "数学", "英语", "物理", "化学"]

    def __init__(self, student_id: str, name: str, scores: Dict[str, float]):
        self.student_id = student_id      # 学号
        self.name = name                  # 姓名
        self.scores = scores              # 科目→成绩 字典

    # ---- 计算属性 ----
    @property
    def total(self) -> float:
        """总分"""
        return sum(self.scores.values())

    @property
    def average(self) -> float:
        """平均分"""
        n = len(self.scores)
        return round(self.total / n, 2) if n > 0 else 0.0

    # ---- 展示用 ----
    def __repr__(self) -> str:
        score_str = "  ".join(
            f"{sub}:{self.scores.get(sub, 'N/A')}" for sub in self.SUBJECTS
        )
        return (
            f"学号: {self.student_id}  姓名: {self.name}\n"
            f"  成绩 → {score_str}\n"
            f"  总分: {self.total}  平均分: {self.average}"
        )

    # ---- 序列化 ----
    def to_line(self) -> str:
        """转为文件中的一行"""
        score_values = ",".join(str(self.scores.get(s, "")) for s in self.SUBJECTS)
        return f"{self.student_id},{self.name},{score_values}"

    @classmethod
    def from_line(cls, line: str) -> "Student":
        """从文件中的一行解析出 Student 对象"""
        parts = line.strip().split(",")
        if len(parts) < 2 + len(cls.SUBJECTS):
            raise ValueError(f"数据行格式不正确: {line}")
        student_id = parts[0]
        name = parts[1]
        scores: Dict[str, float] = {}
        for i, subject in enumerate(cls.SUBJECTS):
            val = parts[2 + i].strip()
            scores[subject] = float(val) if val else 0.0
        return cls(student_id, name, scores)


# ============================================================
# 成绩管理器 —— 对应"数组/链表" + CRUD 知识点
# ============================================================
class GradeManager:
    """学生成绩管理器：内部使用列表存储 Student 对象"""

    def __init__(self):
        self.students: List[Student] = []

    # ===================== 文件读写 =====================
    def load_from_file(self, filepath: str) -> int:
        """
        从 CSV 文件导入学生成绩数据。
        文件格式：学号,姓名,语文,数学,英语,物理,化学（每行一个学生）
        返回导入的学生数量。
        """
        if not os.path.exists(filepath):
            print(f"[错误] 文件不存在: {filepath}")
            return 0

        count = 0
        with open(filepath, "r", encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):  # 跳过空行和注释
                    continue
                try:
                    student = Student.from_line(line)
                    self.students.append(student)
                    count += 1
                except (ValueError, IndexError) as e:
                    print(f"[警告] 第{lineno}行解析失败: {e}")

        print(f"[完成] 成功导入 {count} 名学生数据。")
        return count

    def save_to_file(self, filepath: str) -> None:
        """将当前所有学生数据导出为 CSV 文件"""
        with open(filepath, "w", encoding="utf-8") as f:
            # 写表头
            header = "学号,姓名," + ",".join(Student.SUBJECTS)
            f.write(header + "\n")
            for s in self.students:
                f.write(s.to_line() + "\n")
        print(f"[完成] 数据已导出到: {filepath}")

    def export_statistics(self, filepath: str) -> None:
        """
        导出统计结果（含总分、平均分、排名）到文件。
        按平均分降序排列。
        """
        ranked = self.rank_by_average()
        with open(filepath, "w", encoding="utf-8") as f:
            header = "排名,学号,姓名," + ",".join(Student.SUBJECTS) + ",总分,平均分"
            f.write(header + "\n")
            for rank, s in enumerate(ranked, 1):
                scores = ",".join(str(s.scores.get(sub, "")) for sub in Student.SUBJECTS)
                f.write(f"{rank},{s.student_id},{s.name},{scores},{s.total},{s.average}\n")
        print(f"[完成] 统计结果已导出到: {filepath}")

    # ===================== 查询 =====================
    def find_by_id(self, student_id: str) -> Optional[Student]:
        """按学号精确查找 —— 对应"查找"知识点（线性查找）"""
        for s in self.students:
            if s.student_id == student_id:
                return s
        return None

    def find_by_name(self, name: str, exact: bool = False) -> List[Student]:
        """按姓名查找。exact=False 时模糊匹配（包含即可）。"""
        if exact:
            return [s for s in self.students if s.name == name]
        return [s for s in self.students if name in s.name]

    def query(self, keyword: str) -> List[Student]:
        """
        综合查询：先按学号精确匹配，再按姓名模糊匹配。
        返回匹配的学生列表。
        """
        # 先试学号
        s = self.find_by_id(keyword)
        if s:
            return [s]
        # 再试姓名
        return self.find_by_name(keyword)

    # ===================== 增删改 =====================
    def add(self, student_id: str, name: str, scores: Dict[str, float]) -> bool:
        """新增学生。学号重复则拒绝。"""
        if self.find_by_id(student_id) is not None:
            print(f"[错误] 学号 {student_id} 已存在，无法新增。")
            return False
        self.students.append(Student(student_id, name, scores))
        print(f"[完成] 已添加学生: {name} ({student_id})")
        return True

    def delete(self, student_id: str) -> bool:
        """按学号删除学生。"""
        for i, s in enumerate(self.students):
            if s.student_id == student_id:
                removed = self.students.pop(i)
                print(f"[完成] 已删除学生: {removed.name} ({student_id})")
                return True
        print(f"[错误] 未找到学号为 {student_id} 的学生。")
        return False

    def update(
        self,
        student_id: str,
        name: Optional[str] = None,
        scores: Optional[Dict[str, float]] = None,
    ) -> bool:
        """
        按学号修改学生信息。
        - name: 新姓名（None 则不修改）
        - scores: 新成绩字典（None 则不修改；传入的 key 只覆盖对应科目）
        """
        s = self.find_by_id(student_id)
        if s is None:
            print(f"[错误] 未找到学号为 {student_id} 的学生。")
            return False
        if name is not None:
            s.name = name
        if scores is not None:
            s.scores.update(scores)
        print(f"[完成] 已更新学生: {s.name} ({student_id})")
        return True

    # ===================== 统计与排名 =====================
    def rank_by_average(self, descending: bool = True) -> List[Student]:
        """
        按平均分排序 —— 对应"排序"知识点。
        使用 Python 内置的 Timsort（sorted），底层是归并+插入排序。
        """
        return sorted(self.students, key=lambda s: s.average, reverse=descending)

    def print_ranking(self) -> None:
        """打印排名表"""
        ranked = self.rank_by_average()
        if not ranked:
            print("暂无学生数据。")
            return

        print("\n" + "=" * 70)
        print(f"{'排名':<5}{'学号':<12}{'姓名':<8}{'总分':>8}{'平均分':>8}")
        print("-" * 70)
        for rank, s in enumerate(ranked, 1):
            print(f"{rank:<5}{s.student_id:<12}{s.name:<8}{s.total:>8.1f}{s.average:>8.2f}")
        print("=" * 70 + "\n")

    def print_summary(self) -> None:
        """打印所有学生的概览"""
        if not self.students:
            print("暂无学生数据。")
            return
        for s in self.students:
            print(s)
            print("-" * 40)

    def print_statistics(self) -> None:
        """打印各科统计信息"""
        if not self.students:
            print("暂无学生数据。")
            return
        print("\n" + "=" * 70)
        print(f"{'科目':<8}{'最高分':>8}{'最低分':>8}{'平均分':>8}{'及格率':>8}")
        print("-" * 70)
        for sub in Student.SUBJECTS:
            vals = [s.scores.get(sub, 0) for s in self.students]
            max_v = max(vals)
            min_v = min(vals)
            avg_v = round(sum(vals) / len(vals), 2)
            pass_rate = round(sum(1 for v in vals if v >= 60) / len(vals) * 100, 1)
            print(f"{sub:<8}{max_v:>8.1f}{min_v:>8.1f}{avg_v:>8.2f}{pass_rate:>7.1f}%")
        print("=" * 70 + "\n")


# ============================================================
# 交互式命令行界面
# ============================================================
def interactive_menu():
    """CLI 交互菜单"""
    mgr = GradeManager()

    # 尝试自动加载默认数据文件（如果存在）
    default_file = "students.csv"
    if os.path.exists(default_file):
        print(f"[提示] 检测到默认数据文件 '{default_file}'，自动加载中...")
        mgr.load_from_file(default_file)

    while True:
        print("\n" + "─" * 50)
        print("   📚 学生成绩查询与统计工具")
        print("─" * 50)
        print(" 1. 从文件导入成绩数据")
        print(" 2. 按学号 / 姓名查询")
        print(" 3. 显示所有学生成绩")
        print(" 4. 按平均分排名")
        print(" 5. 显示各科统计")
        print("─" * 50)
        print(" 6. 新增学生")
        print(" 7. 删除学生")
        print(" 8. 修改学生成绩")
        print("─" * 50)
        print(" 9. 导出原始数据")
        print("10. 导出统计结果（含排名）")
        print("─" * 50)
        print("11. 生成示例数据文件")
        print(" 0. 退出程序")
        print("─" * 50)

        choice = input("请输入选项 (0-11): ").strip()

        if choice == "1":
            # ---- 导入 ----
            path = input("请输入文件路径 (直接回车使用 students.csv): ").strip()
            if not path:
                path = "students.csv"
            mgr.load_from_file(path)

        elif choice == "2":
            # ---- 查询 ----
            kw = input("请输入学号或姓名关键字: ").strip()
            if not kw:
                print("输入不能为空。")
                continue
            results = mgr.query(kw)
            if results:
                for s in results:
                    print(s)
                    print("-" * 40)
            else:
                print(f"未找到与 '{kw}' 匹配的学生。")

        elif choice == "3":
            # ---- 显示全部 ----
            mgr.print_summary()

        elif choice == "4":
            # ---- 排名 ----
            mgr.print_ranking()

        elif choice == "5":
            # ---- 各科统计 ----
            mgr.print_statistics()

        elif choice == "6":
            # ---- 新增 ----
            sid = input("学号: ").strip()
            name = input("姓名: ").strip()
            if not sid or not name:
                print("学号和姓名不能为空。")
                continue
            scores: Dict[str, float] = {}
            for sub in Student.SUBJECTS:
                val = input(f"  {sub}成绩 (回车跳过=0): ").strip()
                scores[sub] = float(val) if val else 0.0
            mgr.add(sid, name, scores)

        elif choice == "7":
            # ---- 删除 ----
            sid = input("请输入要删除的学生学号: ").strip()
            if sid:
                mgr.delete(sid)

        elif choice == "8":
            # ---- 修改 ----
            sid = input("请输入要修改的学生学号: ").strip()
            if not sid:
                continue
            s = mgr.find_by_id(sid)
            if s is None:
                print(f"[错误] 未找到学号为 {sid} 的学生。")
                continue
            print(f"当前信息: {s.name}")
            new_name = input("新姓名 (回车跳过): ").strip()
            scores_update: Dict[str, float] = {}
            for sub in Student.SUBJECTS:
                cur = s.scores.get(sub, 0)
                val = input(f"  {sub} 当前={cur}  新成绩 (回车跳过): ").strip()
                if val:
                    scores_update[sub] = float(val)
            mgr.update(sid, name=new_name if new_name else None, scores=scores_update if scores_update else None)

        elif choice == "9":
            # ---- 导出原始数据 ----
            path = input("导出路径 (回车默认 students_export.csv): ").strip()
            if not path:
                path = "students_export.csv"
            mgr.save_to_file(path)

        elif choice == "10":
            # ---- 导出统计结果 ----
            path = input("导出路径 (回车默认 statistics.csv): ").strip()
            if not path:
                path = "statistics.csv"
            mgr.export_statistics(path)

        elif choice == "11":
            # ---- 生成示例数据 ----
            generate_sample_data("students.csv")

        elif choice == "0":
            print("再见！👋")
            break

        else:
            print("无效选项，请重新输入。")


# ============================================================
# 示例数据生成
# ============================================================
def generate_sample_data(filepath: str = "students.csv") -> None:
    """生成示例学生成绩 CSV 文件"""
    sample_data = """\
2024001,张三,88,92,76,85,90
2024002,李四,65,70,55,60,58
2024003,王五,95,88,92,90,87
2024004,赵六,72,68,70,75,80
2024005,孙七,45,52,48,50,55
2024006,周八,98,96,94,92,99
2024007,吴九,83,85,79,88,82
2024008,郑十,60,62,58,55,61"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(sample_data)
    print(f"[完成] 示例数据已生成: {filepath} (共 8 名学生)")


# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    # 如果命令行传了参数，可以快速执行导出等操作
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        mgr = GradeManager()
        if cmd == "generate":
            generate_sample_data(sys.argv[2] if len(sys.argv) > 2 else "students.csv")
        elif cmd == "rank":
            mgr.load_from_file("students.csv")
            mgr.print_ranking()
        elif cmd == "export":
            mgr.load_from_file("students.csv")
            mgr.export_statistics("statistics.csv")
        else:
            print(f"未知命令: {cmd}")
            print("可用: generate | rank | export")
    else:
        interactive_menu()