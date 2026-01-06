#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义正则匹配函数 reg_search
支持文本内容的正则表达式匹配
"""

import re
from typing import List, Dict, Any, Union


class RegexMatcher:
    """正则匹配器类"""

    # 预定义的正则表达式模式
    PREDEFINED_PATTERNS = {
        # 证券代码
        '标的证券': r'股票代码[：:]\s*([A-Z0-9]{6}\.[A-Z]{2})',
        '股票代码': r'股票代码[：:]\s*([A-Z0-9]{6}\.[A-Z]{2})',
        '基金代码': r'基金代码[：:]\s*([A-Z0-9]{6})',
        '债券代码': r'债券代码[：:]\s*([A-Z0-9]{6,})',

        # 日期
        '换股期限': r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日',
        '发行日期': r'发行日期[：:]\s*(\d{4})年(\d{1,2})月(\d{1,2})日',
        '起息日': r'起息日[：:]\s*(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})日?',
        '到期日': r'到期日[：:]\s*(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})日?',
        '日期': r'(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})日?',

        # 金额/数值
        '金额': r'金额[：:]\s*([\d,]+\.?\d*)\s*[万元亿]?',
        '利率': r'利率[：:]\s*([\d\.]+)\s*%',
        '数量': r'数量[：:]\s*(\d+)',
        '规模': r'规模[：:]\s*([\d,]+\.?\d*)\s*[万元亿]?',

        # 通用文本
        '名称': r'{key}[：:]\s*([^\n，。]+)',
        '简称': r'{key}[：:]\s*([^\n，。]+)',
        '联系人': r'联系人[：:]\s*([^\n]+)',
        '电话': r'电话[：:]\s*([\d\-\(\)\s]+)',
        '邮箱': r'邮箱[：:]\s*([\w\.-]+@[\w\.-]+)',
        '地址': r'地址[：:]\s*([^\n]+)',
    }

    @staticmethod
    def format_date(year: str, month: str, day: str) -> str:
        """
        格式化日期为YYYY-MM-DD格式

        Args:
            year: 年
            month: 月
            day: 日

        Returns:
            格式化后的日期字符串
        """
        try:
            year_int = int(year)
            month_int = int(month)
            day_int = int(day)
            return f"{year_int:04d}-{month_int:02d}-{day_int:02d}"
        except ValueError:
            return f"{year}-{month}-{day}"

    @staticmethod
    def reg_search(text: str, regex_list: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        自定义正则匹配函数

        Args:
            text: 需要正则匹配的文本内容
            regex_list: 正则表达式列表，每个元素是一个字典

        Returns:
            匹配到的结果列表

        Example:
            >>> text = "股票代码：600900.SH，发行日期：2023年6月2日"
            >>> regex_list = [{'股票代码': '*自定义*', '发行日期': '*自定义*'}]
            >>> result = reg_search(text, regex_list)
            >>> print(result)
            [{'股票代码': '600900.SH', '发行日期': '2023-06-02'}]
        """
        results = []

        for regex_dict in regex_list:
            result_dict = {}

            for key, pattern in regex_dict.items():
                if pattern == '*自定义*':
                    # 使用预定义模式
                    if key in RegexMatcher.PREDEFINED_PATTERNS:
                        custom_pattern = RegexMatcher.PREDEFINED_PATTERNS[key]
                    elif key in ['名称', '简称']:
                        # 动态替换key
                        custom_pattern = RegexMatcher.PREDEFINED_PATTERNS['名称'].format(key=key)
                    else:
                        # 默认模式：匹配键名后的内容
                        custom_pattern = rf'{key}[：:]\s*([^\n]+)'
                else:
                    # 使用用户提供的正则表达式
                    custom_pattern = pattern

                # 执行正则匹配
                try:
                    matches = re.findall(custom_pattern, text)
                except re.error as e:
                    print(f"正则表达式错误: {e} (模式: {custom_pattern})")
                    matches = []

                # 处理匹配结果
                if matches:
                    result = RegexMatcher._process_matches(key, matches, text)
                    result_dict[key] = result
                else:
                    # 没有匹配到
                    result_dict[key] = [] if key == '换股期限' else ''

            if result_dict:
                results.append(result_dict)

        return results

    @staticmethod
    def _process_matches(key: str, matches: list, text: str = None) -> Any:
        """
        处理匹配结果

        Args:
            key: 键名
            matches: 匹配结果列表
            text: 原始文本（用于调试）

        Returns:
            处理后的结果
        """
        # 日期相关的键
        date_keys = ['换股期限', '发行日期', '起息日', '到期日', '日期']

        if key in date_keys:
            dates = []
            for match in matches:
                if isinstance(match, tuple):
                    # 元组格式 (年, 月, 日)
                    if len(match) >= 3:
                        formatted = RegexMatcher.format_date(match[0], match[1], match[2])
                        dates.append(formatted)
                    elif len(match) == 1 and re.match(r'\d{4}[\-年]\d{1,2}[\-月]\d{1,2}', match[0]):
                        # 字符串格式的日期
                        dates.append(match[0])
                else:
                    # 字符串格式
                    dates.append(match)

            if key == '换股期限':
                # 换股期限需要两个日期
                return dates[:2] if len(dates) >= 2 else dates
            else:
                # 其他日期返回第一个
                return dates[0] if dates else ''

        # 证券代码相关的键
        elif key in ['标的证券', '股票代码', '基金代码', '债券代码']:
            if len(matches) == 1:
                if isinstance(matches[0], tuple):
                    return matches[0][0] if matches[0] else ''
                else:
                    return matches[0]
            else:
                return [m[0] if isinstance(m, tuple) else m for m in matches]

        # 其他类型的键
        else:
            if len(matches) == 1:
                if isinstance(matches[0], tuple):
                    # 返回元组中第一个非空元素
                    for item in matches[0]:
                        if item:
                            return item
                    return ''
                else:
                    return matches[0]
            else:
                # 多个匹配结果
                processed = []
                for match in matches:
                    if isinstance(match, tuple):
                        processed.extend([item for item in match if item])
                    else:
                        processed.append(match)
                return processed


# 为方便使用，提供函数别名
reg_search = RegexMatcher.reg_search


def demo():
    """演示函数"""
    text = '''
标的证券：本期发行的证券为可交换为发行人所持中国长江电力股份
有限公司股票（股票代码：600900.SH，股票简称：长江电力）的可交换公司债
券。
换股期限：本期可交换公司债券换股期限自可交换公司债券发行结束
之日满 12 个月后的第一个交易日起至可交换债券到期日止，即 2023 年 6 月 2
日至 2027 年 6 月 1 日止。
'''

    regex_list = [{
        '标的证券': '*自定义*',
        '换股期限': '*自定义*'
    }]

    result = reg_search(text, regex_list)

    print("示例文本:")
    print("-" * 40)
    print(text)
    print("-" * 40)

    print("\n正则表达式列表:")
    print(regex_list)

    print("\n匹配结果:")
    print(result)

    # 验证结果
    expected = [{
        '标的证券': '600900.SH',
        '换股期限': ['2023-06-02', '2027-06-01']
    }]

    if result == expected:
        print("\n✅ 测试通过!")
    else:
        print("\n❌ 测试失败!")
        print(f"期望: {expected}")
        print(f"实际: {result}")


if __name__ == '__main__':
    demo()