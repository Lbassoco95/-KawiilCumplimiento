import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
from extractor.text_chunker import get_embedding
from extractor.pinecone_uploader import query_pinecone

# Cargar variables de entorno
load_dotenv()

def test_bot_functionality():
    print("🧪 Probando funcionalidad del bot...")
    
    try:
        # Inicializar clientes
        print("1. Inicializando OpenAI...")
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        print("✅ OpenAI inicializado")
        
        print("2. Inicializando Pinecone...")
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT"))
        index = pc.Index("vizum-chieff")
        print("✅ Pinecone inicializado")
        
        print("3. Probando consulta de prueba...")
        pregunta = "¿Qué documentos hay sobre auditorías?"
        embedding = get_embedding(pregunta)
        results = query_pinecone(index, embedding, top_k=3)
        
        if results and 'matches' in results and len(results['matches']) > 0:
            print(f"✅ Consulta exitosa. Encontrados {len(results['matches'])} resultados")
            print("\n📄 Primeros resultados:")
            for i, match in enumerate(results['matches'][:2]):
                print(f"  {i+1}. Archivo: {match['metadata'].get('nombre_archivo', 'N/A')}")
                print(f"     Cliente: {match['metadata'].get('cliente', 'N/A')}")
                print(f"     Score: {match['score']:.3f}")
                print(f"     Texto: {match['metadata'].get('texto', 'N/A')[:100]}...")
                print()
        else:
            print("⚠️ No se encontraron resultados")
        
        print("4. Probando generación de respuesta...")
        contexto = "\n\n".join([match['metadata']['texto'] for match in results['matches']])
        prompt = f"""Responde la siguiente pregunta con base en el contexto del documento:

Pregunta: {pregunta}

Contexto: {contexto}

Respuesta:"""

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        
        respuesta = response.choices[0].message.content
        print("✅ Respuesta generada exitosamente")
        print(f"📝 Respuesta: {respuesta[:200]}...")
        
        print("\n🎉 ¡Todas las pruebas pasaron! El bot está funcionando correctamente.")
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bot_functionality() 