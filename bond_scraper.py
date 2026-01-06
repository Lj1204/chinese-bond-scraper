#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国货币网债券信息获取程序
目标: https://www.chinamoney.com.cn/english/bdInfo/
条件: Bond Type=Treasury Bond, Issue Year=2023
输出: ISIN, Bond Code, Issuer, Bond Type, Issue Date, Latest Rating
"""

import requests
import pandas as pd
import time
import json
import os
from datetime import datetime


class BondScraper:
    """债券数据爬虫类"""

    def __init__(self, bond_type='100001', year='2023', output_dir='data'):
        """
        初始化爬虫

        Args:
            bond_type (str): 债券类型代码 (100001=国债)
            year (str): 发行年份
            output_dir (str): 输出目录
        """
        self.base_url = "https://www.chinamoney.com.cn/ags/ms/cm-u-bond-md/BondMarketInfoListEN"
        self.bond_type = bond_type
        self.year = year
        self.output_dir = output_dir

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://www.chinamoney.com.cn',
            'Referer': 'https://www.chinamoney.com.cn/english/bdInfo/',
            'X-Requested-With': 'XMLHttpRequest'
        }

    def fetch_bonds(self, page_size=50, max_pages=None):
        """
        获取债券数据

        Args:
            page_size (int): 每页记录数
            max_pages (int): 最大页数限制

        Returns:
            list: 债券数据列表
        """
        all_bonds = []
        page = 1

        print("=" * 60)
        print(f"开始获取数据...")
        print(f"债券类型: Treasury Bond (代码: {self.bond_type})")
        print(f"发行年份: {self.year}")
        print("=" * 60)

        while True:
            if max_pages and page > max_pages:
                print(f"达到最大页数限制: {max_pages}")
                break

            data = {
                'pageNo': str(page),
                'pageSize': str(page_size),
                'isin': '',
                'bondCode': '',
                'issueEnty': '',
                'bondType': self.bond_type,
                'couponType': '',
                'issueYear': self.year,
                'rtngShrt': '',
                'bondSpclPrjctVrty': ''
            }

            print(f"正在获取第 {page} 页...", end='', flush=True)

            try:
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    data=data,
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()

                records = result.get('data', {}).get('resultList', [])
                total = result.get('data', {}).get('total', 0)

                if not records:
                    if page == 1:
                        print("未找到数据!")
                    break

                all_bonds.extend(records)
                print(f" 已获取 {len(all_bonds)}/{total} 条记录")

                # 检查是否还有更多
                if len(all_bonds) >= total:
                    print("所有数据获取完成!")
                    break

                page += 1
                time.sleep(0.3)  # 礼貌性延迟

            except requests.exceptions.RequestException as e:
                print(f"\n请求失败: {e}")
                break
            except json.JSONDecodeError as e:
                print(f"\nJSON解析错误: {e}")
                break

        return all_bonds

    def process_data(self, bonds):
        """
        处理债券数据

        Args:
            bonds (list): 原始债券数据

        Returns:
            pandas.DataFrame: 处理后的数据
        """
        if not bonds:
            print("没有数据可处理!")
            return None

        processed = []
        for bond in bonds:
            record = {
                'ISIN': bond.get('isin', ''),
                'Bond_Code': bond.get('bondCode', ''),
                'Issuer': bond.get('entyFullName', ''),
                'Bond_Type': bond.get('bondType', ''),
                'Issue_Date': bond.get('issueStartDate', ''),
                'Latest_Rating': bond.get('debtRtng', ''),
            }

            # 处理评级字段
            if record['Latest_Rating'] in ['---', '', None]:
                record['Latest_Rating'] = 'N/A'

            processed.append(record)

        # 创建DataFrame
        df = pd.DataFrame(processed)

        # 重命名列，使其更友好
        column_mapping = {
            'Bond_Code': 'Bond Code',
            'Bond_Type': 'Bond Type',
            'Issue_Date': 'Issue Date',
            'Latest_Rating': 'Latest Rating',
        }
        df = df.rename(columns=column_mapping)

        # 选择显示列的顺序
        display_columns = ['ISIN', 'Bond Code', 'Issuer', 'Bond Type',
                           'Issue Date', 'Latest Rating']
        df = df[display_columns + [c for c in df.columns if c not in display_columns]]

        return df

    def save_to_csv(self, df, filename=None):
        """
        保存数据到CSV文件

        Args:
            df (pandas.DataFrame): 要保存的数据
            filename (str): 文件名，如果为None则自动生成

        Returns:
            str: 保存的文件路径
        """
        if df is None or df.empty:
            print("没有数据可保存!")
            return None

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"treasury_bonds_{self.year}_{timestamp}.csv"

        filepath = os.path.join(self.output_dir, filename)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')

        print(f"\n数据已保存到: {filepath}")
        print(f"总记录数: {len(df)}")

        return filepath

    def get_summary(self, df):
        """获取数据摘要统计"""
        if df is None or df.empty:
            return {}

        summary = {
            'total_records': len(df),
            'unique_issuers': df['Issuer'].nunique(),
            'date_range': f"{df['Issue Date'].min()} 到 {df['Issue Date'].max()}",
            'rating_distribution': df['Latest Rating'].value_counts().to_dict(),
            'bond_types': df['Bond Type'].value_counts().to_dict()
        }

        return summary

    def run(self, save=True, max_pages=None):
        """
        运行完整的爬虫流程

        Args:
            save (bool): 是否保存结果
            max_pages (int): 最大页数限制

        Returns:
            tuple: (DataFrame, 文件路径)
        """
        # 获取数据
        bonds = self.fetch_bonds(max_pages=max_pages)

        # 处理数据
        df = self.process_data(bonds)

        if df is None:
            return None, None

        # 显示摘要
        summary = self.get_summary(df)
        print("\n" + "=" * 60)
        print("数据摘要:")
        print("=" * 60)
        print(f"总记录数: {summary['total_records']}")
        print(f"唯一发行人: {summary['unique_issuers']}")
        print(f"发行日期范围: {summary['date_range']}")
        print("\n评级分布:")
        for rating, count in summary['rating_distribution'].items():
            print(f"  {rating}: {count}条")

        # 显示预览
        print("\n数据预览 (前5条):")
        print(df.head(5).to_string(index=False))

        # 保存数据
        filepath = None
        if save:
            filepath = self.save_to_csv(df)

        return df, filepath


def main():
    """主函数"""
    # 创建爬虫实例
    scraper = BondScraper(
        bond_type='100001',  # 国债
        year='2023',  # 2023年
        output_dir='data'  # 输出目录
    )

    # 运行爬虫（限制最多3页用于测试）
    df, filepath = scraper.run(max_pages=3)

    return df, filepath


if __name__ == '__main__':
    df, filepath = main()