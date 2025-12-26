const { test } = require('@playwright/test');
const path = require('path');
const fs = require('fs');

// ==========================================
// WORKER PARA XXXFOLLOW
// Flujo corregido basado en análisis completo
// ==========================================

const MODEL_NAME = process.env.MODEL_NAME;
const VIDEO_PATH = process.env.VIDEO_PATH;
const VIDEO_TITLE = process.env.VIDEO_TITLE || 'Default Title';
const VIDEO_TAGS = process.env.VIDEO_TAGS || 'latina,brunette';

if (!MODEL_NAME) {
    throw new Error('❌ ERROR: Debes especificar MODEL_NAME. Ejemplo: MODEL_NAME=demo npx playwright test ...');
}

// Ruta de autenticación
const authFile = path.join(__dirname, `../modelos/${MODEL_NAME}/.auth/xxxfollow.json`);

console.log(`🔐 Usando archivo de autenticación para ${MODEL_NAME}: ${authFile}`);

test.describe('Automatización xxxfollow', () => {

    test('Subida a xxxfollow', async ({ browser }) => {
        // Validaciones previas
        if (!fs.existsSync(authFile)) {
            throw new Error(`❌ No hay credenciales guardadas en ${authFile}. Ejecuta el login manual primero.`);
        }
        if (!VIDEO_PATH || !fs.existsSync(VIDEO_PATH)) {
            console.log('⚠️  No se especificó VIDEO_PATH o no existe. Se saltará la subida real.');
            return;
        }

        console.log('📂 Cargando sesión...');
        const context = await browser.newContext({ storageState: authFile });
        const page = await context.newPage();

        // 1. Navegar a la página de creación de post
        const targetUrl = 'https://www.xxxfollow.com/post';
        console.log(`🌐 Navegando a ${targetUrl}...`);

        await page.goto(targetUrl);
        await page.waitForLoadState('networkidle');

        // Verificar si estamos logueados
        if (page.url().includes('login') || page.url().includes('signin')) {
            throw new Error('❌ La sesión ha expirado. Por favor, loguéate de nuevo.');
        }

        // 2. Preparar inyección de archivo
        console.log('🔧 Preparando inyección de archivo...');
        await page.evaluate(() => {
            const input = document.createElement('input');
            input.type = 'file';
            input.id = 'gemini-upload-hack';
            input.style.display = 'none';
            document.body.appendChild(input);
        });

        await page.locator('#gemini-upload-hack').setInputFiles(VIDEO_PATH);

        // 3. Ejecutar la lógica de subida dentro del navegador
        console.log('🚀 Iniciando subida vía API interna...');

        const result = await page.evaluate(async ({ title, tags }) => {
            // --- CÓDIGO QUE CORRE DENTRO DEL NAVEGADOR ---

            const fileInput = document.getElementById('gemini-upload-hack');
            const file = fileInput.files[0];
            if (!file) throw new Error('No se pudo cargar el archivo en el navegador');

            console.log(`📦 Preparando subida de: ${file.name} (${file.size} bytes)`);

            // Obtener credenciales necesarias de las cookies
            function getCookie(name) {
                const value = `; ${document.cookie}`;
                const parts = value.split(`; ${name}=`);
                if (parts.length === 2) return parts.pop().split(';').shift();
                return null;
            }

            const authId = getCookie('x-auth-id');
            const csrfToken = getCookie('XSRF-TOKEN') || getCookie('x-csrf-token');

            if (!authId || !csrfToken) {
                throw new Error('❌ No se encontraron las cookies de autenticación (x-auth-id, XSRF-TOKEN)');
            }

            console.log(`🔑 Auth ID: ${authId.substring(0, 20)}...`);
            console.log(`🔑 CSRF Token: ${csrfToken.substring(0, 20)}...`);

            // Obtener user_id del localStorage
            let userId = null;
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                const value = localStorage.getItem(key);

                if (key.toLowerCase().includes('user')) {
                    try {
                        const userData = JSON.parse(value);
                        if (userData.id) {
                            userId = userData.id;
                            console.log(`👤 User ID encontrado: ${userId}`);
                            break;
                        }
                    } catch (e) {
                        // No es JSON válido
                    }
                }
            }

            if (!userId) {
                throw new Error('❌ No se pudo obtener el user_id del localStorage');
            }

            // PASO 1: Obtener upload-token
            console.log('🔑 Obteniendo upload-token...');

            const tokenResponse = await fetch('https://www.xxxfollow.com/api/v1/upload-token', {
                method: 'GET',
                headers: {
                    'referer': 'https://www.xxxfollow.com/post'
                }
            });

            if (!tokenResponse.ok) {
                throw new Error(`Error obteniendo upload-token: ${tokenResponse.status}`);
            }

            const tokenData = await tokenResponse.json();
            const uploadToken = tokenData.token;

            console.log(`✅ Upload token obtenido: ${uploadToken.substring(0, 20)}...`);

            // PASO 2: Subir el archivo
            console.log('📹 Subiendo video...');

            const formData = new FormData();
            formData.append('file', file);

            const uploadResponse = await fetch('https://upload.xxxfollow.com/api/v1/video/fans-media', {
                method: 'POST',
                headers: {
                    'upload-token': uploadToken,
                    'content-range': `bytes 0-${file.size - 1}/${file.size}`,
                    'origin': 'https://www.xxxfollow.com',
                    'referer': 'https://www.xxxfollow.com/'
                },
                body: formData
            });

            if (!uploadResponse.ok) {
                const errorText = await uploadResponse.text();
                throw new Error(`Error subiendo video: ${uploadResponse.status} - ${errorText}`);
            }

            const uploadData = await uploadResponse.json();
            console.log('✅ Video subido:', uploadData);

            const tkn = uploadData.token;
            const srvId = uploadData.server;

            if (!tkn || !srvId) {
                throw new Error('❌ No se recibieron token/server del upload');
            }

            // PASO 3: Crear post vacío (sin media)
            console.log('📝 Creando post...');

            const tagsArray = tags.split(',').map(t => t.trim());

            const postPayload = {
                access: 'free',
                gender: 'f',
                scheduled_at: null,
                tags: tagsArray,
                text: title,
                type: 'public',
                user_id: userId
            };

            const postResponse = await fetch('https://www.xxxfollow.com/api/v1/post', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-auth-id': authId,
                    'x-csrf-token': csrfToken
                },
                body: JSON.stringify(postPayload)
            });

            if (!postResponse.ok) {
                const errorText = await postResponse.text();
                throw new Error(`Error creando post: ${postResponse.status} - ${errorText}`);
            }

            const postData = await postResponse.json();
            const postId = postData.id;

            console.log(`✅ Post creado con ID: ${postId}`);

            // PASO 4: Adjuntar media al post
            console.log('📎 Adjuntando media al post...');

            const mediaFormData = new FormData();
            mediaFormData.append('tkn', tkn);
            mediaFormData.append('srv_id', srvId);
            mediaFormData.append('video_volume', '1');

            const mediaResponse = await fetch(`https://www.xxxfollow.com/api/v1/post/${postId}/media/upload`, {
                method: 'POST',
                headers: {
                    'x-auth-id': authId,
                    'x-csrf-token': csrfToken
                },
                body: mediaFormData
            });

            if (!mediaResponse.ok) {
                const errorText = await mediaResponse.text();
                throw new Error(`Error adjuntando media: ${mediaResponse.status} - ${errorText}`);
            }

            const mediaData = await mediaResponse.json();
            console.log('✅ Media adjuntado:', mediaData);

            return {
                success: true,
                postId: postId,
                mediaId: mediaData.media_id || mediaData.id,
                tkn: tkn,
                srvId: srvId
            };

        }, {
            title: VIDEO_TITLE,
            tags: VIDEO_TAGS
        });

        console.log('🏁 Resultado final:', JSON.stringify(result, null, 2));

        if (result.success) {
            console.log(`✅ VIDEO PUBLICADO EXITOSAMENTE!`);
            console.log(`   Post ID: ${result.postId}`);
            console.log(`   Media ID: ${result.mediaId}`);
        } else {
            console.error('❌ Falló la publicación');
        }

        await context.close();
    });
});
