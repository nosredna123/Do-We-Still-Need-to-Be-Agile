const express = require('express');
const cors = require('cors');
const { db, admin } = require('./firebaseAdmin');
require('dotenv').config();
const { LambdaClient, InvokeCommand } = require("@aws-sdk/client-lambda");
const multer = require('multer');
const pdfParse = require('pdf-parse');

const storage = multer.memoryStorage();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json({ limit: '30mb' }));

const ALLOWED_MIME_TYPES = [
  'application/pdf',
  'image/png',
  'image/jpeg',
  'image/webp',
];

const MIME_TO_EXT = {
  'application/pdf': 'pdf',
  'image/png': 'png',
  'image/jpeg': 'jpeg',
  'image/webp': 'webp',
};

const upload = multer({
  storage: storage,
  limits: {
    fileSize: 25 * 1024 * 1024, // Validação de tamanho máximo: 25MB em bytes
  },
  fileFilter: (req, file, cb) => {
    // Validação de formato: Permitir PDF, DOCX, PNG, JPG
    const allowedMimeTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // .docx
      'image/png',
      'image/jpeg',
      'image/jpg'
    ];

    if (allowedMimeTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('INVALID_TYPE'), false);
    }
  }
});


async function requireAuth(req, res, next) {
  const header = req.headers.authorization;
  if (!header?.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Token não fornecido' });
  }
  try {
    const token = header.split('Bearer ')[1];
    const decoded = await admin.auth().verifyIdToken(token);
    req.uid = decoded.uid;
    next();
  } catch {
    return res.status(401).json({ error: 'Token inválido' });
  }
}

function parseFlashcardsMarkdown(markdown) {
  const cards = [];
  const blocks = markdown.split('---').filter(block => block.trim());

  for (const block of blocks) {
    const perguntaMatch = block.match(/\*\*Pergunta:\*\*\s*(.+)/);
    const respostaMatch = block.match(/\*\*Resposta:\*\*\s*([\s\S]+?)(?=\n\n|$)/);

    if (perguntaMatch && respostaMatch) {
      let cleanAnswer = respostaMatch[1].trim();
      cleanAnswer = cleanAnswer.replace(/\*\*[^*]+\*\*/g, '')
        .replace(/\\n/g, ' ')
        .replace(/\n/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();

      cards.push({
        id: Math.random().toString(36).substr(2, 9),
        question: perguntaMatch[1].trim().replace(/\\n/g, ' ').replace(/\n/g, ' ').trim(),
        answer: cleanAnswer,
      });
    }
  }

  return cards;
}

app.post('/api/upload-document', (req, res) => {
  upload.single('documento')(req, res, (err) => {
    if (err) {
      if (err.message === 'INVALID_TYPE')
        return res.status(415).json({ error: 'Tipo de arquivo inválido. Aceitamos apenas arquivos PDF.' });
      if (err.code === 'LIMIT_FILE_SIZE')
        return res.status(413).json({ error: 'Arquivo muito grande. O tamanho máximo permitido é de 25MB.' });
      return res.status(500).json({ error: 'Erro no upload do documento.', details: err.message });
    }
    if (!req.file)
      return res.status(400).json({ error: 'Nenhum documento foi enviado na requisição.' });

    return res.status(200).json({
      message: 'Documento recebido com sucesso.',
      fileName: req.file.originalname,
      size: req.file.size,
    });
  });
});

async function getSavedThemes() {
  try {
    // Busca todos os flashcards
    const snapshot = await db.collection('flashcards').get();
    const themesSet = new Set();

    // Extrai apenas os nomes dos temas únicos
    snapshot.forEach(doc => {
      const data = doc.data();
      if (data.tema) {
        themesSet.add(data.tema);
      }
    });

    return Array.from(themesSet); // Retorna um array de strings, ex: ["Biologia", "Matemática"]
  } catch (error) {
    console.error("Erro ao buscar temas salvos:", error);
    return [];
  }
}

app.post('/api/generate-flashcards', async (req, res) => {
  const { content, file_base64, file_type, file_name, mode, history } = req.body;

  if (!content && !file_base64) {
    return res.status(400).json({ error: 'Envie "content" ou "file_base64".' });
  }

  if (file_base64) {
    const fileSize = Buffer.byteLength(file_base64, 'base64');
    if (fileSize > 10 * 1024 * 1024) {
      return res.status(413).json({ error: 'Arquivo muito grande. Máximo permitido: 10 MB.' });
    }
  }

  if (file_base64 && file_type === 'pdf') {
    try {
      const pdfBuffer = Buffer.from(file_base64, 'base64');
      const pdfData = await pdfParse(pdfBuffer);
      if (pdfData.numpages > 10) {
        return res.status(400).json({
          error: 'PDF muito longo. Máximo permitido: 10 páginas.'
        });
      }
    } catch (err) {
      return res.status(400).json({ error: 'Não foi possível ler o PDF enviado.' });
    }
  }
  const savedThemes = await getSavedThemes();
  const client = new LambdaClient({
    region: "us-east-2",
    credentials: {
      accessKeyId: process.env.AWS_ACCESS_KEY_ID,
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
    },
  });

  const payload = JSON.stringify({
    httpMethod: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      content,
      file_base64,
      file_type,
      file_name,
      mode,
      history,
      savedThemes // <--- Seus temas vão aqui!
    }),
    isBase64Encoded: false,
  });
  const command = new InvokeCommand({
    FunctionName: "flashcard-api",
    Payload: Buffer.from(payload),
    InvocationType: "RequestResponse",
  });

  try {
    const response = await client.send(command);
    const result = JSON.parse(Buffer.from(response.Payload).toString());

    console.log("Resposta do Lambda:", result);

    let parsedBody;
    try {
      parsedBody = JSON.parse(result.body);
    } catch {
      parsedBody = { artifact: result.body, artifact_type: 'unknown', mode: 'auto' };
    }

    if (result.statusCode && result.statusCode !== 200) {
      return res.status(result.statusCode).json(parsedBody);
    }

    if (parsedBody.artifact_type === 'flashcards') {
      const cards = parseFlashcardsMarkdown(parsedBody.artifact);
      res.status(result.statusCode || 200).json({
        artifact: cards,
        artifact_type: parsedBody.artifact_type,
        tema: parsedBody.tema,
        mode: parsedBody.mode,
        router_decision: parsedBody.router_decision
      });
    } else {
      res.status(result.statusCode || 200).json({
        artifact: parsedBody.artifact,
        artifact_type: parsedBody.artifact_type,
        tema: parsedBody.tema,
        mode: parsedBody.mode,
        router_decision: parsedBody.router_decision
      });
    }
  } catch (error) {
    console.error("Erro ao invocar Lambda:", error);
    res.status(500).json({
      error: "Falha na comunicação com o serviço de geração.",
      details: error.message,
    });
  }
});

app.get('/api/flashcards', requireAuth, async (req, res) => {
  try {
    const snapshot = await db.collection('users').doc(req.uid).collection('flashcards').orderBy('createdAt', 'asc').get();
    const cards = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    res.status(200).json(cards);
  } catch (error) {
    console.error('Erro ao buscar flashcards:', error);
    res.status(500).json({ error: 'Falha ao buscar flashcards.', details: error.message });
  }
});

app.post('/api/upload-document', (req, res) => {
  upload.single('documento')(req, res, async (err) => {
    if (err) {
      if (err.message === 'INVALID_TYPE') {
        return res.status(415).json({
          error: "Tipo de arquivo inválido. Aceitamos apenas arquivos PDF, DOCX, PNG e JPG.",
        });
      }
      if (err.code === 'LIMIT_FILE_SIZE') {
        return res.status(413).json({
          error: "Arquivo muito grande. O tamanho máximo permitido é de 25MB.",
        });
      }
      return res.status(500).json({
        error: "Erro no upload do documento.",
        details: err.message,
      });
    }

    if (!req.file) {
      return res.status(400).json({
        error: "Nenhum documento foi enviado na requisição.",
      });
    }

    // Convertendo o arquivo para Base64
    const fileBase64 = req.file.buffer.toString('base64');

    // Configurando o cliente do Lambda
    const client = new LambdaClient({
      region: "us-east-2",
      credentials: {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID,
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
      },
    });

    // Formato do payload (pode precisar de ajustes dependendo do que seu Lambda espera)
    const payload = JSON.stringify({
      httpMethod: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        file: fileBase64,
        fileName: req.file.originalname,
        mimeType: req.file.mimetype
      }),
      isBase64Encoded: false,
    });

    // Nome da função Lambda para o processamento de PDF
    const command = new InvokeCommand({
      FunctionName: "pdf-parser-api", // Altere aqui se o nome da sua função for diferente
      Payload: Buffer.from(payload),
      InvocationType: "RequestResponse",
    });

    try {
      const response = await client.send(command);
      const result = JSON.parse(Buffer.from(response.Payload).toString());

      console.log("Resposta do Lambda de PDF:", result);

      // Tratando o corpo da resposta do Lambda
      let responseData = result.body;
      try {
        if (responseData) responseData = JSON.parse(result.body);
      } catch (e) {
        // Se não for JSON, mantém como string
      }

      return res.status(result.statusCode || 200).json({
        message: "Documento enviado e processado com sucesso pelo Lambda.",
        fileName: req.file.originalname,
        size: req.file.size,
        data: responseData || result
      });
    } catch (error) {
      console.error("Erro ao invocar Lambda de PDF:", error);
      return res.status(500).json({
        error: "Falha na comunicação com o serviço de processamento.",
        details: error.message,
      });
    }
  });
});

/**
 * SAVE /api/flashcards
 * Salva um novo flashcard no banco de dados do firebase.
 */
app.post('/api/flashcards', requireAuth, async (req, res) => {
  const { question, answer, themeName } = req.body;

  if (!question || !answer) {
    return res.status(400).json({
      error: 'Os campos "question" e "answer" são obrigatórios.'
    });
  }

  try {
    const newFlashcard = {
      question,
      answer,
      themeName: themeName || 'Geral',
      createdAt: new Date().toISOString()
    };

    const docRef = await db.collection('users').doc(req.uid).collection('flashcards').add(newFlashcard);

    return res.status(201).json({
      message: 'Flashcard salvo com sucesso.',
      id: docRef.id,
      flashcard: newFlashcard
    });
  } catch (error) {
    console.error('Erro ao salvar flashcard:', error);
    return res.status(500).json({
      error: 'Falha ao salvar o flashcard no banco de dados.',
      details: error.message
    });
  }
});

app.put('/api/flashcards/:id', requireAuth, async (req, res) => {
  const { id } = req.params;
  const { question, answer, themeName } = req.body;

  if (!question && !answer && !themeName) {
    return res.status(400).json({
      error: 'Nenhum dado fornecido. Envie "question", "answer" ou "themeName" para atualizar.'
    });
  }

  try {
    const flashcardRef = db.collection('users').doc(req.uid).collection('flashcards').doc(id);
    const doc = await flashcardRef.get();
    if (!doc.exists) {
      return res.status(404).json({ error: 'Flashcard não encontrado.' });
    }

    const updateData = {};
    if (question) updateData.question = question;
    if (answer) updateData.answer = answer;
    if (themeName) updateData.themeName = themeName;
    updateData.updatedAt = new Date().toISOString();

    await flashcardRef.update(updateData);

    res.status(200).json({
      message: 'Flashcard atualizado com sucesso.',
      id,
      ...updateData
    });
  } catch (error) {
    console.error("Erro ao atualizar flashcard:", error);
    res.status(500).json({
      error: "Falha ao atualizar o flashcard no banco de dados.",
      details: error.message,
    });
  }
});

app.delete('/api/flashcards/:id', requireAuth, async (req, res) => {
  const { id } = req.params;

  try {
    const flashcardRef = db.collection('users').doc(req.uid).collection('flashcards').doc(id);
    const doc = await flashcardRef.get();
    if (!doc.exists) {
      return res.status(404).json({ error: 'Flashcard não encontrado para exclusão.' });
    }

    await flashcardRef.delete();

    res.status(200).json({
      message: 'Flashcard excluído com sucesso.',
      id
    });
  } catch (error) {
    console.error("Erro ao excluir flashcard:", error);
    res.status(500).json({
      error: "Falha ao excluir o flashcard no banco de dados.",
      details: error.message,
    });
  }
});

// ── RESUMOS ────────────────────────────────────────────────────────────────

app.get('/api/resumos', requireAuth, async (req, res) => {
  try {
    const snapshot = await db.collection('users').doc(req.uid).collection('resumos').orderBy('createdAt', 'asc').get();
    const resumos = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    res.status(200).json(resumos);
  } catch (error) {
    console.error('Erro ao buscar resumos:', error);
    res.status(500).json({ error: 'Falha ao buscar resumos.', details: error.message });
  }
});

app.post('/api/resumos', requireAuth, async (req, res) => {
  const { topic, html } = req.body;
  if (!topic || !html) {
    return res.status(400).json({ error: 'Os campos "topic" e "html" são obrigatórios.' });
  }
  try {
    const newResumo = { topic, html, createdAt: new Date().toISOString() };
    const docRef = await db.collection('users').doc(req.uid).collection('resumos').add(newResumo);
    return res.status(201).json({ message: 'Resumo salvo com sucesso.', id: docRef.id, resumo: newResumo });
  } catch (error) {
    console.error('Erro ao salvar resumo:', error);
    return res.status(500).json({ error: 'Falha ao salvar o resumo.', details: error.message });
  }
});

app.put('/api/resumos/:id', requireAuth, async (req, res) => {
  const { id } = req.params;
  const { topic } = req.body;
  if (!topic) return res.status(400).json({ error: '"topic" é obrigatório.' });
  try {
    const ref = db.collection('users').doc(req.uid).collection('resumos').doc(id);
    const doc = await ref.get();
    if (!doc.exists) return res.status(404).json({ error: 'Resumo não encontrado.' });
    const updateData = { topic, updatedAt: new Date().toISOString() };
    await ref.update(updateData);
    res.status(200).json({ message: 'Resumo atualizado com sucesso.', id, ...updateData });
  } catch (error) {
    console.error('Erro ao atualizar resumo:', error);
    res.status(500).json({ error: 'Falha ao atualizar o resumo.', details: error.message });
  }
});

app.delete('/api/resumos/:id', requireAuth, async (req, res) => {
  const { id } = req.params;
  try {
    const ref = db.collection('users').doc(req.uid).collection('resumos').doc(id);
    const doc = await ref.get();
    if (!doc.exists) return res.status(404).json({ error: 'Resumo não encontrado.' });
    await ref.delete();
    res.status(200).json({ message: 'Resumo excluído com sucesso.', id });
  } catch (error) {
    console.error('Erro ao excluir resumo:', error);
    res.status(500).json({ error: 'Falha ao excluir o resumo.', details: error.message });
  }
});

// ── DICIONÁRIOS ─────────────────────────────────────────────────────────────

app.get('/api/dicionarios', requireAuth, async (req, res) => {
  try {
    const snapshot = await db.collection('users').doc(req.uid).collection('dicionarios').orderBy('createdAt', 'asc').get();
    const dicionarios = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    res.status(200).json(dicionarios);
  } catch (error) {
    console.error('Erro ao buscar dicionários:', error);
    res.status(500).json({ error: 'Falha ao buscar dicionários.', details: error.message });
  }
});

app.post('/api/dicionarios', requireAuth, async (req, res) => {
  const { topic, html, termsCount } = req.body;
  if (!topic || !html) {
    return res.status(400).json({ error: 'Os campos "topic" e "html" são obrigatórios.' });
  }
  try {
    const newDicionario = { topic, html, termsCount: termsCount || 0, createdAt: new Date().toISOString() };
    const docRef = await db.collection('users').doc(req.uid).collection('dicionarios').add(newDicionario);
    return res.status(201).json({ message: 'Dicionário salvo com sucesso.', id: docRef.id, dicionario: newDicionario });
  } catch (error) {
    console.error('Erro ao salvar dicionário:', error);
    return res.status(500).json({ error: 'Falha ao salvar o dicionário.', details: error.message });
  }
});

app.put('/api/dicionarios/:id', requireAuth, async (req, res) => {
  const { id } = req.params;
  const { topic } = req.body;
  if (!topic) return res.status(400).json({ error: '"topic" é obrigatório.' });
  try {
    const ref = db.collection('users').doc(req.uid).collection('dicionarios').doc(id);
    const doc = await ref.get();
    if (!doc.exists) return res.status(404).json({ error: 'Dicionário não encontrado.' });
    const updateData = { topic, updatedAt: new Date().toISOString() };
    await ref.update(updateData);
    res.status(200).json({ message: 'Dicionário atualizado com sucesso.', id, ...updateData });
  } catch (error) {
    console.error('Erro ao atualizar dicionário:', error);
    res.status(500).json({ error: 'Falha ao atualizar o dicionário.', details: error.message });
  }
});

app.delete('/api/dicionarios/:id', requireAuth, async (req, res) => {
  const { id } = req.params;
  try {
    const ref = db.collection('users').doc(req.uid).collection('dicionarios').doc(id);
    const doc = await ref.get();
    if (!doc.exists) return res.status(404).json({ error: 'Dicionário não encontrado.' });
    await ref.delete();
    res.status(200).json({ message: 'Dicionário excluído com sucesso.', id });
  } catch (error) {
    console.error('Erro ao excluir dicionário:', error);
    res.status(500).json({ error: 'Falha ao excluir o dicionário.', details: error.message });
  }
});

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Servidor rodando na porta ${PORT}`);
  });
}

// ── LOGIN e LOGOUT ────────────────────────────────────────────────────────────────
app.post('/api/auth/login', async (req, res) => {

  const { idToken } = req.body;

  if (!idToken) {
    return res.status(400).json({ error: 'Token não fornecido' });
  }

  try {

    const decodedToken = await admin.auth().verifyIdToken(idToken);

    const uid = decodedToken.uid;
    const email = decodedToken.email;
    const name = decodedToken.name;

    return res.status(200).json({
      message: 'Login bem-sucedido',
      uid,
      email,
      name
    });

  } catch (error) {
    console.error('Erro ao verificar token:', error);
    return res.status(401).json({ error: 'Token inválido' });
  }


  module.exports = app;

});


app.post('/api/auth/logout', async (req, res) => {


  const uid = req.body;

  if (!uid) {
    return res.status(400).json({ error: 'UID não fornecido' });
  }

  try {
    await admin.auth().revokeRefreshTokens(uid);
    return res.status(200).json({ message: 'Logout bem-sucedido' });

  }

  catch (error) {
    console.error('Erro no logout:', error);
    return res.status(500).json({ error: 'Falha ao realizar logout' });

  }

});