"""
Script para inicializar la base de datos de QuickSort
"""
from app import app, db, init_database, init_tree
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Inicializa la base de datos y el árbol"""
    try:
        logger.info("Iniciando inicialización de base de datos...")
        
        with app.app_context():
            # Inicializar base de datos
            init_database()
            logger.info("✅ Base de datos inicializada correctamente")
            
            # Inicializar árbol
            init_tree()
            logger.info("✅ Árbol de organización inicializado correctamente")
        
        logger.info("🎉 Inicialización completada exitosamente!")
        logger.info("Ahora puedes ejecutar: python app.py")
        
    except Exception as e:
        logger.error(f"❌ Error durante la inicialización: {e}")
        raise

if __name__ == '__main__':
    main()
