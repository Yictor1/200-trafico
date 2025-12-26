#!/usr/bin/env node

/**
 * Script para ejecutar FASE 1: Crear esquema PRD en Supabase
 * Usa MCP (Model Context Protocol) similar a create_model_table.js
 * 
 * Uso: node execute_fase1_node.js
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Iniciando FASE 1: Crear esquema PRD\n');

// Leer script SQL
const sqlPath = path.join(__dirname, 'fase1_create_prd_schema.sql');
if (!fs.existsSync(sqlPath)) {
    console.error(`❌ Error: No se encuentra el script SQL: ${sqlPath}`);
    process.exit(1);
}

const sqlScript = fs.readFileSync(sqlPath, 'utf-8');

// Preparar entorno
const env = {
    ...process.env
};

// Asegurar que las variables necesarias estén presentes
if (!env.SUPABASE_ACCESS_TOKEN) {
    console.log('⚠️  SUPABASE_ACCESS_TOKEN no encontrado en entorno');
    console.log('   El script intentará usar MCP con las credenciales disponibles\n');
}

if (!env.SUPABASE_PROJECT_REF) {
    // Extraer project ref de la URL si no está explícito
    const supabaseUrl = env.SUPABASE_URL || '';
    if (supabaseUrl.includes('supabase.co')) {
        const projectRef = supabaseUrl.split('//')[1].split('.')[0];
        env.SUPABASE_PROJECT_REF = projectRef;
        console.log(`📋 Project ref detectado: ${projectRef}\n`);
    } else {
        console.error('❌ Error: No se pudo determinar SUPABASE_PROJECT_REF');
        console.error('   Configura SUPABASE_PROJECT_REF o SUPABASE_URL en el entorno');
        process.exit(1);
    }
}

// Ejecutar MCP
const mcp = spawn('npx', [
    '-y',
    '@supabase/mcp-server-supabase@latest',
    `--project-ref=${env.SUPABASE_PROJECT_REF}`
], { env });

let buffer = '';
let requestId = 0;

function sendRequest(method, params) {
    requestId++;
    const request = {
        jsonrpc: '2.0',
        id: requestId,
        method,
        params
    };
    mcp.stdin.write(JSON.stringify(request) + '\n');
    return requestId;
}

mcp.stdout.on('data', (data) => {
    buffer += data.toString();
    const lines = buffer.split('\n');

    for (let i = 0; i < lines.length - 1; i++) {
        const line = lines[i].trim();
        if (line) {
            try {
                const response = JSON.parse(line);

                if (response.id === 1) {
                    console.log('✅ Conectado a Supabase\n');
                    console.log('📋 Ejecutando script SQL de creación de esquema...\n');
                    console.log('   (Esto puede tardar unos segundos)\n');

                    sendRequest('tools/call', {
                        name: 'apply_migration',
                        arguments: {
                            name: 'fase1_create_prd_schema',
                            query: sqlScript
                        }
                    });
                }

                else if (response.id === 2) {
                    if (response.error) {
                        console.error('❌ Error:', response.error.message);
                        if (response.error.data) {
                            console.error('   Detalles:', JSON.stringify(response.error.data, null, 2));
                        }
                        mcp.kill();
                        process.exit(1);
                    }

                    console.log('✅ Script SQL ejecutado exitosamente!\n');
                    console.log('🎉 FASE 1 completada!\n');
                    console.log('📋 Tablas creadas:');
                    console.log('   - modelos');
                    console.log('   - plataformas');
                    console.log('   - cuentas_plataforma');
                    console.log('   - contenidos');
                    console.log('   - publicaciones');
                    console.log('   - eventos_sistema\n');
                    console.log('✅ El esquema PRD está listo para usar\n');

                    setTimeout(() => {
                        mcp.kill();
                        process.exit(0);
                    }, 500);
                }

            } catch (e) {
                // Ignorar líneas que no son JSON válido
            }
        }
    }

    buffer = lines[lines.length - 1];
});

mcp.stderr.on('data', (data) => {
    console.error('⚠️  stderr:', data.toString());
});

mcp.on('error', (error) => {
    console.error('❌ Error ejecutando MCP:', error.message);
    console.error('\n💡 Alternativa: Ejecuta el SQL manualmente en la consola SQL de Supabase');
    console.error(`   Archivo: ${sqlPath}\n`);
    process.exit(1);
});

// Inicializar MCP
sendRequest('initialize', {
    protocolVersion: '2024-11-05',
    capabilities: {},
    clientInfo: { name: 'fase1-migration', version: '1.0.0' }
});

// Timeout de seguridad
setTimeout(() => {
    console.log('\n⏱️  Timeout: El proceso tardó demasiado');
    console.log('💡 Verifica manualmente en la consola SQL de Supabase');
    mcp.kill();
    process.exit(1);
}, 60000); // 60 segundos



