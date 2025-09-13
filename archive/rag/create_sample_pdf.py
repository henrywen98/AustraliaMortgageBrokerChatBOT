#!/usr/bin/env python3
"""
创建测试PDF文件的脚本
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def create_sample_pdf():
    # 创建PDF文件
    doc = SimpleDocTemplate(
        "sample_mortgage_guide.pdf",
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # 获取样式
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # 创建文档内容
    story = []
    
    # 标题
    story.append(Paragraph("澳大利亚房贷指南示例", title_style))
    story.append(Spacer(1, 12))
    
    # 房贷基础知识
    story.append(Paragraph("房贷基础知识", heading_style))
    story.append(Spacer(1, 12))
    
    # 房贷类型
    story.append(Paragraph("房贷类型", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    content = """
    <b>1. 固定利率房贷</b><br/>
    - 利率在整个贷款期间保持不变<br/>
    - 适合希望稳定还款的借款人<br/>
    - 通常期限为1-5年<br/><br/>
    
    <b>2. 浮动利率房贷</b><br/>
    - 利率根据市场变化而调整<br/>
    - 可能获得更低的初始利率<br/>
    - 还款金额可能波动<br/><br/>
    
    <b>3. 分割式房贷</b><br/>
    - 部分贷款为固定利率，部分为浮动利率<br/>
    - 平衡风险和机会<br/><br/>
    """
    
    story.append(Paragraph(content, normal_style))
    story.append(Spacer(1, 12))
    
    # 申请要求
    story.append(Paragraph("申请房贷的基本要求", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    requirements = """
    - 澳大利亚公民或永久居民身份<br/>
    - 稳定的收入证明<br/>
    - 良好的信用记录<br/>
    - 足够的首付（通常为房价的20%）<br/>
    - 通过银行的借贷能力评估<br/><br/>
    """
    
    story.append(Paragraph(requirements, normal_style))
    story.append(Spacer(1, 12))
    
    # 首次购房者优惠
    story.append(Paragraph("首次购房者优惠", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    benefits = """
    - 首次购房者补助（First Home Owner Grant）<br/>
    - 印花税减免<br/>
    - 政府担保贷款计划<br/><br/>
    """
    
    story.append(Paragraph(benefits, normal_style))
    story.append(Spacer(1, 12))
    
    # 投资房贷款
    story.append(Paragraph("投资房贷款", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    investment = """
    - 通常利率较自住房贷款略高<br/>
    - 可申请负扣税优惠<br/>
    - 需要考虑租金收入<br/><br/>
    """
    
    story.append(Paragraph(investment, normal_style))
    story.append(Spacer(1, 12))
    
    # 重要提示
    story.append(Paragraph("重要提示", heading_style))
    story.append(Spacer(1, 6))
    
    notice = """
    本文档仅供参考，具体贷款条件请咨询专业的抵押贷款经纪人。我们建议您：<br/><br/>
    
    1. 在申请前充分了解不同贷款产品<br/>
    2. 比较多家银行的利率和条件<br/>
    3. 考虑您的长期财务规划<br/>
    4. 寻求专业的抵押贷款经纪人建议<br/><br/>
    
    澳大利亚的房贷市场竞争激烈，不同银行和金融机构提供各种不同的贷款产品。
    选择合适的房贷对您的财务状况和未来规划都非常重要。
    """
    
    story.append(Paragraph(notice, normal_style))
    
    # 构建PDF
    doc.build(story)
    print("✅ PDF文件创建成功: sample_mortgage_guide.pdf")

if __name__ == "__main__":
    create_sample_pdf()
