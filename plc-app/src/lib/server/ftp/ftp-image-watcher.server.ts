// src/lib/server/chokidar.service.ts
import chokidar from 'chokidar';
import fs from 'fs';
import path from 'path';
import { broadcast } from '../ws/ws.server';


interface FileMetadata {
    nombre: string;
    nombreOriginal: string;
    fecha: Date;
    tamaño: number;
    tipo: string;
    extension: string;
    contenido?: string;
    error?: string;
    rutaOriginal: string;
    rutaFinal: string;
    idUnico: string;
    lote?: string;
    pieza?: string;
}

interface ConfiguracionArchivos {
    directorioDestino: string;
    prefijoId: string;
    formatoNombre: 'timestamp' | 'secuencial' | 'lote-pieza';
    organizarPorFecha: boolean;
    organizarPorTipo: boolean;
}

// Configuración por defecto
const CONFIG_DEFAULT: ConfiguracionArchivos = {
    directorioDestino: 'C:/ftp/procesados',
    prefijoId: 'IMG',
    formatoNombre: 'timestamp',
    organizarPorFecha: true,
    organizarPorTipo: true
};

// Extensiones de archivos soportadas
const EXTENSIONES_TEXTO = ['.txt', '.json', '.xml', '.csv', '.log', '.md', '.js', '.ts', '.html', '.css'];
const EXTENSIONES_IMAGEN = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'];

// Contador para IDs secuenciales
let contadorSecuencial = 1;

function getFileType(extension: string): string {
    if (EXTENSIONES_IMAGEN.includes(extension.toLowerCase())) {
        return 'imagen';
    } else if (EXTENSIONES_TEXTO.includes(extension.toLowerCase())) {
        return 'texto';
    } else {
        return 'archivo';
    }
}

function generateUniqueId(formato: string, prefijo: string, extension: string): string {
    const timestamp = new Date().getTime();
    const fechaHora = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    
    switch (formato) {
        case 'timestamp':
            return `${prefijo}_${timestamp}${extension}`;
        case 'secuencial':
            const id = `${prefijo}_${String(contadorSecuencial).padStart(6, '0')}${extension}`;
            contadorSecuencial++;
            return id;
        case 'lote-pieza':
            // Formato: IMG_L001_P001_20240813-143022.jpg
            const loteNum = String(Math.floor(Math.random() * 999) + 1).padStart(3, '0');
            const piezaNum = String(Math.floor(Math.random() * 999) + 1).padStart(3, '0');
            return `${prefijo}_L${loteNum}_P${piezaNum}_${fechaHora}${extension}`;
        default:
            return `${prefijo}_${timestamp}${extension}`;
    }
}

function extractLoteAndPieza(nombreArchivo: string): { lote?: string; pieza?: string } {
    // Buscar patrones como L001, P001 en el nombre del archivo
    const loteMatch = nombreArchivo.match(/L(\d+)/i);
    const piezaMatch = nombreArchivo.match(/P(\d+)/i);
    
    return {
        lote: loteMatch ? loteMatch[1] : undefined,
        pieza: piezaMatch ? piezaMatch[1] : undefined
    };
}

function createDirectoryStructure(basePath: string, tipo: string, fecha: Date, organizarPorFecha: boolean, organizarPorTipo: boolean): string {
    let finalPath = basePath;
    
    // Crear directorio base si no existe
    if (!fs.existsSync(finalPath)) {
        fs.mkdirSync(finalPath, { recursive: true });
    }
    
    // Organizar por tipo
    if (organizarPorTipo) {
        finalPath = path.join(finalPath, tipo);
        if (!fs.existsSync(finalPath)) {
            fs.mkdirSync(finalPath, { recursive: true });
        }
    }
    
    // Organizar por fecha
    if (organizarPorFecha) {
        const year = fecha.getFullYear();
        const month = String(fecha.getMonth() + 1).padStart(2, '0');
        const day = String(fecha.getDate()).padStart(2, '0');
        
        finalPath = path.join(finalPath, `${year}`, `${month}`, `${day}`);
        if (!fs.existsSync(finalPath)) {
            fs.mkdirSync(finalPath, { recursive: true });
        }
    }
    
    return finalPath;
}

function moveAndRenameFile(filePath: string, config: ConfiguracionArchivos): FileMetadata {
    const extension = path.extname(filePath);
    const nombreOriginal = path.basename(filePath);
    const fileType = getFileType(extension);
    const fecha = new Date();
    
    // Generar ID único
    const nuevoNombre = generateUniqueId(config.formatoNombre, config.prefijoId, extension);
    
    // Crear estructura de directorios
    const directorioFinal = createDirectoryStructure(
        config.directorioDestino,
        fileType,
        fecha,
        config.organizarPorFecha,
        config.organizarPorTipo
    );
    
    const rutaFinal = path.join(directorioFinal, nuevoNombre);
    
    // Extraer información de lote y pieza
    const { lote, pieza } = extractLoteAndPieza(nuevoNombre);
    
    try {
        // Mover y renombrar archivo
        fs.copyFileSync(filePath, rutaFinal);
        fs.unlinkSync(filePath); // Eliminar archivo original
        
        const stats = fs.statSync(rutaFinal);
        
        const metadata: FileMetadata = {
            nombre: nuevoNombre,
            nombreOriginal: nombreOriginal,
            fecha: fecha,
            tamaño: stats.size,
            tipo: fileType,
            extension: extension || 'sin extensión',
            rutaOriginal: filePath,
            rutaFinal: rutaFinal,
            idUnico: nuevoNombre.replace(extension, ''),
            lote: lote,
            pieza: pieza
        };
        
        // Leer contenido si es necesario
        if (fileType === 'texto') {
            try {
                const content = fs.readFileSync(rutaFinal, 'utf8');
                metadata.contenido = content.length > 1000 ? content.substring(0, 1000) + '...' : content;
            } catch (error) {
                metadata.error = `Error al leer contenido: ${error instanceof Error ? error.message : 'Error desconocido'}`;
            }
        }
        
        return metadata;
        
    } catch (error) {
        throw new Error(`Error al mover archivo: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
}

function formatConsoleOutput(metadata: FileMetadata): void {
    const emoji = metadata.tipo === 'imagen' ? '🖼️' : 
                  metadata.tipo === 'texto' ? '📄' : '📁';
    
    console.log('\n' + '='.repeat(80));
    console.log(`${emoji} ARCHIVO PROCESADO - CONTROL DE CALIDAD`);
    console.log('='.repeat(80));
    console.log(`📝 Nombre original: ${metadata.nombreOriginal}`);
    console.log(`🆔 Nuevo nombre: ${metadata.nombre}`);
    console.log(`🏷️ ID único: ${metadata.idUnico}`);
    
    if (metadata.lote) {
        console.log(`📦 Lote: ${metadata.lote}`);
    }
    if (metadata.pieza) {
        console.log(`🔧 Pieza: ${metadata.pieza}`);
    }
    
    console.log(`📅 Fecha procesado: ${metadata.fecha.toLocaleString('es-ES')}`);
    console.log(`📏 Tamaño: ${(metadata.tamaño / 1024).toFixed(2)} KB`);
    console.log(`🏷️ Tipo: ${metadata.tipo.toUpperCase()}`);
    console.log(`🔧 Extensión: ${metadata.extension}`);
    console.log(`📁 Ruta original: ${metadata.rutaOriginal}`);
    console.log(`📂 Ruta final: ${metadata.rutaFinal}`);
    
    if (metadata.contenido) {
        console.log('📖 Contenido:');
        console.log('-'.repeat(60));
        console.log(metadata.contenido);
        console.log('-'.repeat(60));
    }
    
    if (metadata.error) {
        console.log(`❌ Error: ${metadata.error}`);
    }
    
    console.log('='.repeat(80) + '\n');
}

export function startFtpWatcher(configuracion: Partial<ConfiguracionArchivos> = {}) {
    const ftpDir = 'C:/ftp';
    const config = { ...CONFIG_DEFAULT, ...configuracion };
    
    // Verificar que el directorio existe
    if (!fs.existsSync(ftpDir)) {
        console.error(`❌ Error: El directorio ${ftpDir} no existe`);
        return;
    }

    // Crear directorio de destino si no existe
    if (!fs.existsSync(config.directorioDestino)) {
        fs.mkdirSync(config.directorioDestino, { recursive: true });
        console.log(`📁 Directorio de destino creado: ${config.directorioDestino}`);
    }

    console.log(`📂 Iniciando vigilancia de la carpeta: ${ftpDir}`);
    console.log(`📁 Directorio de procesados: ${config.directorioDestino}`);
    console.log(`🏷️ Prefijo de ID: ${config.prefijoId}`);
    console.log(`📝 Formato de nombre: ${config.formatoNombre}`);
    console.log(`⏰ Hora de inicio: ${new Date().toLocaleString('es-ES')}`);
    console.log('👀 Esperando archivos nuevos para procesar...\n');

    const watcher = chokidar.watch(ftpDir, { 
        ignoreInitial: true,
        persistent: true,
        awaitWriteFinish: {
            stabilityThreshold: 3000, // Esperar 3 segundos para archivos grandes
            pollInterval: 100
        }
    });

    watcher
        .on('add', (filePath: string) => {
            try {
                console.log(`⬇️ Archivo detectado: ${path.basename(filePath)}`);
                
                const metadata = moveAndRenameFile(filePath, config);
                
                // Mostrar en consola con formato mejorado
                formatConsoleOutput(metadata);
                
                // Enviar por WebSocket (si tienes la funcionalidad)
                broadcast({ 
                    type: 'archivo_procesado', 
                    payload: {
                        ...metadata,
                        timestamp: new Date().toISOString()
                    }
                });
                
                // Log para base de datos o sistema de control
                console.log(`✅ PROCESADO: ${metadata.idUnico} | Lote: ${metadata.lote || 'N/A'} | Pieza: ${metadata.pieza || 'N/A'}`);
                
            } catch (error) {
                console.error('❌ Error procesando archivo:', error);
                console.error(`📁 Archivo problemático: ${filePath}`);
            }
        })
        .on('change', (filePath: string) => {
            console.log(`🔄 Archivo modificado (ignorado): ${path.basename(filePath)}`);
        })
        .on('unlink', (filePath: string) => {
            console.log(`🗑️ Archivo eliminado: ${path.basename(filePath)}`);
        })
        .on('error', (error) => {
            console.error('❌ Error en el watcher:', error);
        })
        .on('ready', () => {
            console.log('✅ Sistema de control de calidad listo');
            console.log('🔍 Monitoreando archivos para detección de fallas...\n');
        });

    // Manejar cierre graceful
    process.on('SIGINT', () => {
        console.log('\n🛑 Cerrando sistema de control de calidad...');
        watcher.close();
        process.exit(0);
    });

    return watcher;

    // Función auxiliar para obtener estadísticas
    function getStats() {
        return {
            totalProcesados: contadorSecuencial - 1,
            directorioOrigen: ftpDir,
            directorioDestino: config.directorioDestino,
            configuracion: config
        };
    }
}

// Funciones auxiliares exportadas
export function setContadorSecuencial(valor: number) {
    contadorSecuencial = valor;
}

export function getProximoId(): number {
    return contadorSecuencial;
}