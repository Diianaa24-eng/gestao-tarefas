import csv
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import cm

def exportar_csv(dados: list, ficheiro: str, colunas: list):
    """Exporta dados para CSV."""
    with open(ficheiro, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=colunas)
        writer.writeheader()
        for item in dados:
            
            row = {col: item.get(col, '') for col in colunas}
            writer.writerow(row)
    return ficheiro

def exportar_pdf(dados: list, ficheiro: str, titulo: str, colunas: list):
    """Exporta dados para PDF."""
    doc = SimpleDocTemplate(ficheiro, pagesize=A4)
    elementos = []
    styles = getSampleStyleSheet()
    
   
    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
        alignment=1  
    )
    elementos.append(Paragraph(titulo, titulo_style))
    
    
    data_relatorio = datetime.now().strftime("%d/%m/%Y %H:%M")
    elementos.append(Paragraph(f"Gerado em: {data_relatorio}", styles['Normal']))
    elementos.append(Spacer(1, 20))
    
    
    if dados:
        
        table_data = [colunas]
        
        
        for item in dados:
            row = [str(item.get(col, '')) for col in colunas]
            table_data.append(row)
        
        
        tabela = Table(table_data, repeatRows=1)
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')]),
        ]))
        elementos.append(tabela)
    else:
        elementos.append(Paragraph("Sem dados para mostrar.", styles['Normal']))
    
    doc.build(elementos)
    return ficheiro
