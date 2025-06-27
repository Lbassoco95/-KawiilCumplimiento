#!/usr/bin/env python3
"""
Ejemplo de uso del chunker de texto
"""

from extractor.text_chunker import chunk_text

def main():
    # Texto de ejemplo largo para probar el chunking
    texto_largo = """
    En un entorno donde la lucha contra el lavado de dinero y el financiamiento al terrorismo (PLD/FT) se ha vuelto prioritaria, los transmisores de dinero en México enfrentan el reto de transformar sus procesos de cumplimiento regulatorio en verdaderas estrategias de negocio. Desde septiembre de 2022, la Unidad de Inteligencia Financiera (UIF) ha impulsado una estrategia nacional que busca armonizar acciones para prevenir y combatir estos delitos financieros.

    Este documento aborda el marco regulatorio aplicable, las responsabilidades específicas de las empresas transmisoras de dinero, y las mejores prácticas para implementar sistemas efectivos de prevención que no solo cumplan con la normativa, sino que también fortalezcan la confianza de los clientes y la reputación institucional.

    A lo largo de este documento, analizaremos desde el fundamento legal y las obligaciones específicas, hasta los sistemas de monitoreo, la integración con áreas clave como tesorería, y los reportes regulatorios necesarios. También exploraremos los riesgos derivados del incumplimiento, los beneficios de una cultura proactiva de cumplimiento, y las tecnologías emergentes que están transformando el sector, ofreciendo una visión integral para que los transmisores de dinero conviertan sus obligaciones regulatorias en una verdadera ventaja competitiva.

    El artículo 115 de la Constitución Política de los Estados Unidos Mexicanos establece las bases para la operación de las instituciones financieras, incluyendo la captación de recursos, otorgamiento de créditos y operaciones activas, pasivas y fiduciarias. Este fundamento constitucional da pie a la regulación específica para los transmisores de dinero.

    Las empresas transmisoras de dinero en México, como entidades financieras no bancarias, están reguladas y supervisadas por la CNBV desde 2015. Esta regulación les impone obligaciones específicas para salvaguardar el Sistema Financiero Mexicano y reducir los riesgos de involucramiento en operaciones delictivas como el Lavado de Dinero y el Financiamiento al Terrorismo (LD/FT).
    """
    
    try:
        # Dividir el texto en chunks de 500 tokens
        chunks = chunk_text(texto_largo, max_tokens=500)
        
        # Imprimir los resultados
        print(f"=== TEXTO DIVIDIDO EN {len(chunks)} CHUNKS ===")
        print()
        
        for i, chunk in enumerate(chunks, 1):
            print(f"--- CHUNK {i} ---")
            print(chunk)
            print(f"Longitud: {len(chunk)} caracteres")
            print()
        
        print("=== FIN DE LOS CHUNKS ===")
        
    except Exception as e:
        print(f"Error al procesar el texto: {e}")

if __name__ == "__main__":
    main() 